/**
 * 原创的单 JS 线程所有权模型；不调用原生 API，不操作真实句柄。
 *
 * 使用合同：
 * - 每个 lease（不透明资源凭据）对应一个独占资源，禁止重复包装同一资源。
 * - acquire() 成功交出全新 lease 之前，未完成的工作仍由取得方负责。
 *   如果取得失败，取得方必须自行清理尚未交出的资源。
 * - ready 只交出 offer（认领机会）；只有 offer.claim() 成功才转移所有权。
 *   claim 不调用用户回调，也不暴露裸句柄。
 * - cleanup 必须同步执行；只有确认释放完成，才返回 RELEASE_CONFIRMED。
 *   抛错或返回其他值，都表示 outcome-unknown（无法确认释放结果）。
 * - 结果未知时不自动重试，也不依靠垃圾回收器清理资源。
 */
export const RELEASE_CONFIRMED = Symbol('release-confirmed');
const records = new WeakMap();

export function createLease(cleanup) {
  if (typeof cleanup !== 'function') throw new TypeError('cleanup must be a function');
  const lease = Object.freeze(Object.create(null));
  records.set(lease, {
    state: 'fresh', cleanup, cleanupAttempts: 0, cleanupError: null,
    returnObservation: null,
  });
  return lease;
}

function inspectResource(record) {
  return Object.freeze({
    state: record.state,
    cleanupAttempts: record.cleanupAttempts,
    cleanupError: record.cleanupError,
    returnObservation: record.returnObservation,
  });
}

function release(record) {
  // 先锁住状态，再调用外部传入的清理代码。
  // 清理中重入 close/cancel 只能看到 cleaning，不能再次调用 cleanup。
  if (record.state !== 'producer-owned' && record.state !== 'consumer-owned') {
    return inspectResource(record);
  }
  record.state = 'cleaning';
  record.cleanupAttempts += 1;
  try {
    // 取出函数后单独调用，避免通过 this 泄露可变的内部 record。
    const cleanup = record.cleanup;
    record.cleanup = null; // 已进入唯一一次清理尝试，不再由记录保留此闭包。
    const confirmation = cleanup();
    if (confirmation === RELEASE_CONFIRMED) {
      record.state = 'released';
    } else {
      record.state = 'outcome-unknown';
      record.cleanupError = new TypeError(
        'cleanup must synchronously return RELEASE_CONFIRMED; no retry is safe by default',
      );
      // 意外返回的异步工作只用于诊断，不算成功释放。
      // Promise 接纳返回值时，then 的 getter 或回调可能重入，所以先置为 unknown。
      // 即使稍后兑现了确认值，也不能反过来证明同步清理已经成功。
      record.returnObservation = Object.freeze({ state: 'pending' });
      try {
        const observed = Promise.resolve(confirmation);
        // 绕过实例上被覆盖的 .then；constructor/species 自定义逻辑仍可能失败。
        // 因此，对任意返回值的观察只是尽力而为，失败也要保留诊断。
        Promise.prototype.then.call(
          observed,
          () => { record.returnObservation = Object.freeze({ state: 'fulfilled' }); },
          (error) => {
            record.returnObservation = Object.freeze({ state: 'rejected', error });
          },
        );
      } catch (error) {
        record.returnObservation = Object.freeze({ state: 'observation-failed', error });
      }
    }
  } catch (error) {
    // 回调可能先释放资源、再抛错；不能仅凭异常认定资源尚未释放。
    record.state = 'outcome-unknown';
    record.cleanupError = error;
  }
  return inspectResource(record);
}

export function startHandoff({ acquire }) {
  if (typeof acquire !== 'function') throw new TypeError('acquire must be a function');
  let phase = 'queued';
  let record = null;
  let failure = null;
  let cancellationReason = null;
  let acquisitionError = null;

  function inspect() {
    return Object.freeze({
      phase, failure, cancellationReason, acquisitionError,
      resource: record === null ? null : inspectResource(record),
    });
  }

  function stop(nextPhase, reason) {
    if (!['queued', 'acquiring', 'offered'].includes(phase)) return false;
    phase = nextPhase; // 先记录取消或失败，防止清理重入时仍能认领资源。
    if (nextPhase === 'cancelled') cancellationReason = reason;
    else failure = reason;
    if (record !== null) release(record);
    return true; // 仅表示接受请求，不证明取得工作已停止，也不证明资源已释放。
  }

  function claim() {
    if (phase !== 'offered') return null;
    // 从修改状态到返回 owner 之间不调用外部代码，避免转移中途被回调重入。
    const owner = Object.freeze({
      close: () => release(record),
      inspect: () => inspectResource(record),
    });
    record.state = 'consumer-owned';
    phase = 'transferred';
    return owner;
  }

  // 先让调用方拿到任务控制对象，再在微任务里开始 acquire。
  // 这样，“启动前取消”有独立且可测试的含义：取得函数根本不会执行。
  const ready = Promise.resolve().then(async () => {
    if (phase !== 'queued') return null;
    phase = 'acquiring';
    let lease;
    try {
      lease = await acquire();
      const candidate = records.get(lease);
      if (candidate === undefined || candidate.state !== 'fresh') {
        throw new TypeError('acquire must return a fresh, unshared lease');
      }
      record = candidate;
      record.state = 'producer-owned';
    } catch (error) {
      acquisitionError = error;
      if (phase === 'acquiring') {
        phase = 'failed';
        failure = error;
      }
      return null;
    }

    if (phase !== 'acquiring') {
      // 取消或交付失败不代表生产者已停止；资源仍可能迟到。
      // 本任务接下这份 lease 后，仍须承担一次清理尝试。
      release(record);
      return null;
    }
    phase = 'offered';
    return Object.freeze({ claim });
  });

  return Object.freeze({
    ready,
    cancel: (reason = 'cancelled') => stop('cancelled', reason),
    failDelivery: (error = new Error('delivery failed')) => stop('failed', error),
    inspect,
  });
}
