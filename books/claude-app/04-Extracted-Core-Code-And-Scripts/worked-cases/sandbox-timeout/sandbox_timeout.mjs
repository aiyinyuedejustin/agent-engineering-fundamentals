/**
 * Original deterministic adapter around the book's ContentEpoch.
 * Trusted synthetic events only: no renderer, RPC transport, browser, or I/O work.
 * A manual integer clock makes the response deadline a half-open interval.
 */
import {ContentEpoch} from './existing-models.mjs';

export class LeasePool {
  #active = new Set();
  #acquired = 0;
  #released = 0;
  constructor(limit) {
    if (!Number.isSafeInteger(limit) || limit < 1) throw new RangeError('invalid capacity');
    this.limit = limit;
  }
  get available() { return this.#active.size < this.limit; }
  acquire() {
    if (!this.available) return null;
    const token = Symbol();
    this.#active.add(token); this.#acquired++;
    return Object.freeze({release: () => {
      if (!this.#active.delete(token)) return false;
      this.#released++;
      return true;
    }});
  }
  snapshot() {
    return {used: this.#active.size, acquired: this.#acquired, released: this.#released};
  }
}

export class PreviewDeadlineCase {
  #gate = new ContentEpoch();
  #channel = null;
  #generation = 0;
  #operations = new Map();
  #now = 0;
  constructor({rpcCapacity = 2, workerCapacity = 1} = {}) {
    this.rpcSlots = new LeasePool(rpcCapacity);
    this.workSlots = new LeasePool(workerCapacity);
    this.journal = [];
    this.delivered = [];
    this.openChannel();
  }
  get now() { return this.#now; }
  #note(event, id = null, detail = {}) {
    this.journal.push(Object.freeze({at: this.now, event, id, ...detail}));
  }
  #operation(id) {
    const op = this.#operations.get(id);
    if (!op) throw new Error(`unknown operation: ${id}`);
    return op;
  }
  #settle(op, status) {
    if (op.reply !== 'pending') return false;
    op.reply = status;
    op.rpcLease.release();
    this.#note('reply-settled', op.id, {status});
    return true;
  }
  #requestStop(op) {
    if (op.worker !== 'running' || op.cancel !== 'none') return false;
    op.cancel = 'requested'; // Signal sent, NOT proof of stopped execution.
    this.#note('cancel-requested', op.id);
    return true;
  }
  openChannel() {
    if (this.#channel) throw new Error('close the old channel first');
    this.#channel = Object.freeze({generation: ++this.#generation});
    this.#gate = new ContentEpoch(); // A new document must be acknowledged anew.
    this.#note('channel-opened', null, {generation: this.#generation});
  }
  closeChannel() {
    if (!this.#channel) return false;
    this.#channel = null; // Revoke delivery before touching pending callbacks.
    for (const op of this.#operations.values()) {
      this.#settle(op, 'CHANNEL_CLOSED');
      this.#requestStop(op);
    }
    this.#note('channel-closed');
    return true;
  }
  publish(body, type = 'text/html') {
    if (!this.#channel) throw new Error('no channel');
    if (typeof body !== 'string' || !body || typeof type !== 'string' || !type) {
      throw new TypeError('nonempty synthetic content required');
    }
    const ticket = Object.freeze({channel: this.#channel,
      content: Object.freeze(this.#gate.replace(type, body))});
    for (const op of this.#operations.values()) {
      if (!this.#gate.mayUseCapability(op.receipt)) {
        this.#settle(op, 'STALE_CONTENT'); this.#requestStop(op);
      }
    }
    this.#note('content-posted', null, {epoch: ticket.content.epoch});
    return ticket;
  }
  acknowledge(ticket) {
    const accepted = ticket.channel === this.#channel &&
      this.#gate.acknowledge(ticket.content, true);
    this.#note('content-ack', null, {accepted});
    return accepted;
  }
  begin(id, deadlineMs) {
    if (typeof id !== 'string' || !id || this.#operations.has(id)) throw new Error('invalid or reused operation ID');
    if (!Number.isSafeInteger(deadlineMs) || deadlineMs < 1 ||
        !Number.isSafeInteger(this.now + deadlineMs)) throw new RangeError('invalid deadline');
    const receipt = Object.freeze(this.#gate.receipt());
    let reason = null;
    if (!this.#channel) reason = 'CHANNEL_CLOSED';
    else if (!this.#gate.mayUseCapability(receipt)) reason = 'CONTENT_UNACKNOWLEDGED';
    else if (!this.rpcSlots.available) reason = 'RPC_BUSY';
    else if (!this.workSlots.available) reason = 'WORK_BUSY';
    if (reason) { this.#note('admission-denied', id, {reason}); return {accepted: false, reason}; }
    // Both capacities checked in one synchronous step before acquiring either.
    const op = {id, receipt, channel: this.#channel, deadlineAt: this.now + deadlineMs,
      reply: 'pending', worker: 'running', cancel: 'none', candidate: null,
      rpcLease: this.rpcSlots.acquire(), workLease: this.workSlots.acquire()};
    this.#operations.set(id, op);
    this.#note('admitted', id, {deadlineAt: op.deadlineAt});
    return {accepted: true, id};
  }
  advanceTo(time) {
    if (!Number.isSafeInteger(time) || time < this.now) throw new RangeError('clock must be monotonic');
    // Process each deadline at its own virtual instant, even across a large jump.
    const due = [...this.#operations.values()].filter(op => op.reply === 'pending' && op.deadlineAt <= time)
      .sort((a, b) => a.deadlineAt - b.deadlineAt);
    for (const op of due) {
      this.#now = op.deadlineAt;
      this.#settle(op, 'TIMEOUT');
      this.#requestStop(op);
    }
    this.#now = time;
  }
  cancel(id) {
    const op = this.#operation(id);
    const settled = this.#settle(op, 'CANCELLED');
    const signaled = this.#requestStop(op);
    return settled || signaled;
  }
  cancelAcknowledged(id, kind) {
    if (!['received', 'stopped'].includes(kind)) throw new TypeError('unknown cancellation acknowledgement');
    const op = this.#operation(id);
    if (!['requested', 'received'].includes(op.cancel) || op.worker !== 'running') return false;
    if (kind === 'received') {
      if (op.cancel === 'received') return false;
      op.cancel = 'received'; // The worker saw the request but may still be running.
    } else {
      // A trusted synthetic worker reports terminal shutdown, not merely receipt.
      op.cancel = 'stopped'; op.worker = 'stopped'; op.workLease.release();
    }
    this.#note('cancel-ack', id, {kind});
    return true;
  }
  finishWork(id, value) {
    const op = this.#operation(id);
    if (op.worker !== 'running') return false;
    op.worker = 'completed';
    op.workLease.release(); // Physical-work lifetime ends here, even after timeout.
    op.candidate = typeof value === 'string' && value.length <= 65_536
      ? Object.freeze({ok: true, value}) : Object.freeze({ok: false, error: 'BAD_RESULT'});
    this.#note('work-finished', id); // Payload is deliberately absent from journal.
    return true;
  }
  deliver(id) {
    const op = this.#operation(id);
    if (!op.candidate) return {accepted: false, reasons: ['NO_RESULT']};
    const reasons = [];
    if (op.reply !== 'pending') reasons.push('REPLY_CLOSED');
    if (!this.#channel || op.channel !== this.#channel) reasons.push('OLD_CHANNEL');
    if (!this.#gate.mayUseCapability(op.receipt)) reasons.push('STALE_CONTENT');
    if (this.now >= op.deadlineAt) reasons.push('DEADLINE');
    if (reasons.length) {
      this.#note('result-dropped', id, {reasons});
      return {accepted: false, reasons};
    }
    this.#settle(op, op.candidate.ok ? 'SUCCESS' : op.candidate.error);
    this.delivered.push(Object.freeze({id, ...op.candidate}));
    this.#note('result-delivered', id);
    return {accepted: true};
  }
  snapshot(id) {
    const op = id ? this.#operation(id) : null;
    return {
      at: this.now, channel: this.#channel?.generation ?? null, content: this.#gate.receipt(),
      rpc: this.rpcSlots.snapshot(), work: this.workSlots.snapshot(),
      ...(op ? {id, reply: op.reply, worker: op.worker, cancel: op.cancel} : {})
    };
  }
}

export function runWorkedTimeline() {
  const host = new PreviewDeadlineCase();
  const rows = [];
  const row = (event, id, result = null) => rows.push({event, ...host.snapshot(id), result});
  host.acknowledge(host.publish('A')); row('确认 A');
  host.advanceTo(1); host.begin('r1', 5); row('r1 开始，deadline=6', 'r1');
  host.advanceTo(6); row('r1 deadline 到期', 'r1');
  host.advanceTo(7); host.cancelAcknowledged('r1', 'received'); row('只确认收到取消请求', 'r1');
  host.advanceTo(8); host.acknowledge(host.publish('B'));
  row('确认 B；新读取仍因工作槽满而拒绝', 'r1', host.begin('r2', 8));
  host.advanceTo(9); host.finishWork('r1', 'late A result'); row('r1 底层完成', 'r1');
  host.advanceTo(10); row('投递 r1 的迟到结果', 'r1', host.deliver('r1'));
  host.advanceTo(11); host.begin('r2', 10); row('r2 现在能开始', 'r2');
  host.advanceTo(12); host.cancel('r2'); row('用户取消 r2', 'r2');
  host.advanceTo(13); host.cancelAcknowledged('r2', 'received'); row('r2 只确认收到取消', 'r2');
  host.advanceTo(14); host.cancelAcknowledged('r2', 'stopped'); row('r2 确认工作已停', 'r2');
  host.advanceTo(15); row('重复终止与完成回调无效', 'r2', {
    duplicateAck: host.cancelAcknowledged('r2', 'stopped'), lateFinish: host.finishWork('r2', 'impossible')});
  host.advanceTo(16); host.begin('r3', 14); row('r3 开始', 'r3');
  host.advanceTo(17); host.finishWork('r3', 'B result'); row('r3 完成，响应尚未投递', 'r3');
  host.advanceTo(18); host.closeChannel(); host.openChannel(); host.acknowledge(host.publish('B'));
  row('新通道重新确认 B', 'r3');
  host.advanceTo(19); row('旧通道的 r3 回调到达', 'r3', host.deliver('r3'));
  return {rows, journal: host.journal, delivered: host.delivered, final: host.snapshot()};
}
