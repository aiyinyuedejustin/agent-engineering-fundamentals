/** Original local lifecycle model, intentionally not a product SDK. */
export class SessionModel {
  #generation = 0; #current = null; #transport = null;
  state = 'idle'; outcome = null;
  begin() {
    if (this.state !== 'idle') throw new Error('Session is not idle');
    const previous = this.#transport; this.#transport = null;
    this.state = 'starting'; this.outcome = null;
    const ticket = this.#current = Object.freeze({ generation: ++this.#generation });
    // Invalidate ownership before close(), which may synchronously emit EOF.
    previous?.close();
    return ticket;
  }
  current(ticket) { return ticket === this.#current && ticket?.generation === this.#generation; }
  attach(ticket, transport) {
    if (!this.current(ticket) || this.state !== 'starting') {
      // A duplicate callback must not close the already-owned connection.
      if (transport !== this.#transport) transport.close();
      return false;
    }
    this.#transport = transport; this.state = 'running'; return true;
  }
  result(ticket, { status }) {
    if (!this.current(ticket) || this.state !== 'running') return false;
    if (!['success', 'error'].includes(status)) throw new Error('No valid terminal result');
    this.outcome = status; this.state = 'idle';
    if (status === 'error') {
      const transport = this.#transport; this.#transport = null; transport?.close();
    }
    return true;
  }
  eof(ticket) {
    if (!this.current(ticket)) return false;
    if (this.state === 'running' || this.state === 'starting') this.outcome = 'incomplete';
    const transport = this.#transport; this.#transport = null; this.state = 'idle';
    transport?.close(); return true;
  }
  stop() {
    ++this.#generation; this.#current = null; this.state = 'stopping';
    const transport = this.#transport; this.#transport = null;
    this.outcome = 'cancelled'; this.state = 'idle'; transport?.close();
  }
  get connected() { return this.#transport !== null; }
}

export class ApprovalInbox {
  #pending = new Map(); #settled = new Map(); #closed = false;
  request(id) {
    if (this.#closed) throw new Error('Approval inbox closed');
    if (typeof id !== 'string' || !id) throw new Error('Invalid request identity');
    if (this.#pending.has(id)) return this.#pending.get(id).promise;
    if (this.#settled.has(id)) return this.#settled.get(id);
    let resolve; const promise = new Promise(done => { resolve = done; });
    this.#pending.set(id, { promise, resolve }); return promise;
  }
  decide(id, decision) {
    const item = this.#pending.get(id); if (!item) return false;
    this.#pending.delete(id); this.#settled.set(id, item.promise);
    item.resolve(decision === 'allow' ? 'allow' : 'deny'); return true;
  }
  abort(id) { return this.decide(id, 'deny'); }
  close() {
    this.#closed = true;
    for (const id of this.#pending.keys()) this.abort(id);
    this.#settled.clear(); // No further requests are accepted after close.
  }
}
