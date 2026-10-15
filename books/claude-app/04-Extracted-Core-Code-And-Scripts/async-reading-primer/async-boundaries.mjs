/** 原创教学模型；只操作进程内存，不连接 Claude、浏览器或外部服务。 */
export function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

/** 每次 begin 都产生不同的归属凭据，即使 label 相同。 */
export class Owner {
  #generation = 0;
  #ticket = null;
  value = null;
  begin(label) {
    this.#ticket = Object.freeze({ generation: ++this.#generation, label });
    this.value = null;
    return this.#ticket;
  }
  owns(ticket) { return ticket !== null && ticket === this.#ticket; }
  dispose() { this.#ticket = null; this.value = null; }
  snapshot() {
    return Object.freeze({ current: this.#ticket?.label ?? null, value: this.value });
  }
}

/** guarded=false 是刻意保留的反例，不能用作生产实现。 */
export async function commitAfter(owner, ticket, ready, { guarded = true } = {}) {
  const result = await ready;
  if (guarded && !owner.owns(ticket)) return 'stale';
  // 此检查与本地赋值之间没有 await。外部资源提交仍需自身的原子性/授权策略。
  owner.value = result;
  return 'committed';
}

/**
 * deadline 必须是到期时 fulfill 的 Promise；本函数不创建计时器。
 * 两条分支都转换为明确记录。它不 abort 任务，不回滚副作用。
 * 提前挂上 work 的拒绝处理器，也观察 deadline 之后才发生的 work 拒绝。
 */
export function waitUntil(work, deadline) {
  return Promise.race([
    Promise.resolve(work).then(
      value => Object.freeze({ kind: 'fulfilled', value }),
      error => Object.freeze({ kind: 'rejected', error })
    ),
    Promise.resolve(deadline).then(() => Object.freeze({ kind: 'deadline' }))
  ]);
}

/**
 * 模拟任务在 gate 放行后做一次内存写入。
 * cooperative 版本在提交前观察信号；并未实现“abort 时立即唤醒等待”。
 */
export async function effectAfter(gate, effects, { signal, cooperative = false } = {}) {
  await gate;
  if (cooperative && signal?.aborted) return 'aborted';
  effects.push('write');
  return 'written';
}

/**
 * 手动驱动的单执行者 FIFO。enqueue 只入队；runNext 才取出一个任务。
 * completion 总是 fulfill 一个结算记录，失败由 state:'rejected' 表示。
 * 这是本例的显式契约，不代表任何真实队列 SDK 的返回值含义。
 */
export class TeachingQueue {
  #items = [];
  #states = new Map();
  #nextId = 0;
  #busy = false;
  async enqueue(operation) {
    if (typeof operation !== 'function') throw new TypeError('operation must be a function');
    const id = ++this.#nextId;
    const done = deferred();
    this.#items.push({ id, operation, done });
    this.#states.set(id, 'queued');
    return Object.freeze({ id, accepted: true, completion: done.promise });
  }
  state(id) { return this.#states.get(id) ?? 'unknown'; }
  async runNext() {
    if (this.#busy) throw new Error('WORKER_BUSY');
    const item = this.#items.shift();
    if (!item) return null;
    this.#busy = true;
    this.#states.set(item.id, 'running');
    let outcome;
    try {
      const value = await item.operation();
      outcome = Object.freeze({ state: 'fulfilled', value });
    } catch (error) {
      outcome = Object.freeze({ state: 'rejected', error });
    } finally {
      this.#busy = false;
    }
    this.#states.set(item.id, outcome.state);
    item.done.resolve(outcome);
    return outcome;
  }
}
