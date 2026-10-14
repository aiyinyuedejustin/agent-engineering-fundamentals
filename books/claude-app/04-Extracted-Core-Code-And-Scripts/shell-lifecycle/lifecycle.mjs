/** 原创教学模型：导航代际与退出结算。不会创建 Electron 窗口。 */
export class NavigationOwner {
  #generation = 0;
  #current = null;
  begin(url) {
    if (typeof url !== 'string' || !url) throw new TypeError('需要导航地址');
    const ticket = Object.freeze({ generation: ++this.#generation, url });
    this.#current = { ticket, state: 'loading', error: null };
    return ticket;
  }
  settle(ticket, { ok, error = null }) {
    // 旧导航不能清除新导航的错误层，也不能把新页面标记为 ready。
    if (ticket !== this.#current?.ticket) return false;
    if (this.#current.state !== 'loading') return false;
    this.#current = { ticket, state: ok ? 'ready' : 'failed', error: ok ? null : error };
    return true;
  }
  owns(ticket) { return this.#current?.ticket === ticket; }
  snapshot() {
    return this.#current ? { url: this.#current.ticket.url, generation: this.#generation,
      state: this.#current.state, error: this.#current.error } : null;
  }
  dispose() { this.#current = null; ++this.#generation; }
}

/** 有限等待只结束协调者的等待；它不会强制终止已启动的任务。 */
export async function settleShutdown(tasks, { deadlineMs = 1000, flush = async () => {} } = {}) {
  if (!Number.isFinite(deadlineMs) || deadlineMs < 0) throw new RangeError('期限必须有限且非负');
  const names = Object.keys(tasks);
  if (names.some(name => typeof tasks[name] !== 'function')) throw new TypeError('清理项必须为函数');
  const outcomes = new Map(names.map(name => [name, { name, state: 'pending' }]));
  const running = names.map(name => Promise.resolve().then(tasks[name]).then(
    () => outcomes.set(name, { name, state: 'fulfilled' }),
    () => outcomes.set(name, { name, state: 'rejected' })
  ));
  let timer;
  const limit = new Promise(resolve => { timer = setTimeout(() => resolve('deadline'), deadlineMs); });
  const reason = await Promise.race([Promise.all(running).then(() => 'settled'), limit]);
  clearTimeout(timer);
  // 返回前复制快照；后续任务完成不会偷偷改写已经交付的报告。
  const cleanup = [...outcomes.values()].map(entry => ({ ...entry }));
  let persistence;
  try { await flush(); persistence = 'fulfilled'; } catch { persistence = 'rejected'; }
  return { reason, cleanup, persistence };
}
