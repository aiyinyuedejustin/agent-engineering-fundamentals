/** Original, in-memory byte ledger. No file reads, uploads, or tokenizer. */
import {pathToFileURL} from 'node:url';
export const utf8Bytes = text => new TextEncoder().encode(text).byteLength;

export class InlineBudget {
  #limit;
  #pending = new Map();
  #committed = new Map();
  constructor(limit) {
    if (!Number.isSafeInteger(limit) || limit < 0) throw new RangeError('invalid byte limit');
    this.#limit = limit;
  }
  get limit() { return this.#limit; }
  get used() { return [...this.#committed.values()].reduce((a, b) => a + b, 0); }
  get reserved() { return [...this.#pending.values()].reduce((a, b) => a + b.bytes, 0); }
  reserve(id, text) {
    const bytes = utf8Bytes(text);
    if (this.#committed.has(id) || [...this.#pending.values()].some(x => x.id === id)) {
      throw new Error('duplicate attachment identity');
    }
    if (this.used + this.reserved + bytes > this.#limit) return null;
    const token = Symbol(id);
    this.#pending.set(token, {id, bytes});
    return Object.freeze({
      // Both transitions consume the pending token. A repeated callback is harmless.
      commit: () => {
        const item = this.#pending.get(token);
        if (!item) return false;
        this.#pending.delete(token);
        this.#committed.set(item.id, item.bytes);
        return true;
      },
      release: () => this.#pending.delete(token),
    });
  }
  remove(id) { return this.#committed.delete(id); }
}

export class DraftOwner {
  #epoch = 0;
  #reservations = new Set();
  constructor(key, limit) {
    this.key = key;
    this.budget = new InlineBudget(limit);
    this.ready = new Map();
  }
  begin(id, text) {
    const reservation = this.budget.reserve(id, text);
    if (!reservation) return {route: 'file-or-reject'};
    this.#reservations.add(reservation);
    const epoch = this.#epoch;
    const finish = accepted => {
      this.#reservations.delete(reservation);
      if (!accepted || epoch !== this.#epoch) {
        reservation.release();
        return false;
      }
      if (!reservation.commit()) return false;
      this.ready.set(id, text);
      return true;
    };
    return Object.freeze({route: 'inline', complete: () => finish(true), cancel: () => finish(false)});
  }
  invalidate() {
    this.#epoch += 1;
    for (const reservation of this.#reservations) reservation.release();
    this.#reservations.clear();
    // Existing committed entries stay owned by this old draft. A new draft uses
    // a new DraftOwner; invalidating work is not a remote delete or data erasure.
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const draft = new DraftOwner('draft-A', 12);
  draft.begin('existing', 'ok').complete();
  const a = draft.begin('a', '资料');
  const b = draft.begin('b', '图像');
  console.log({used: draft.budget.used, reserved: draft.budget.reserved, a: a.route, b: b.route});
  a.cancel();
  const retry = draft.begin('b', '图像');
  draft.invalidate();
  console.log({lateCompletion: retry.complete(), used: draft.budget.used, reserved: draft.budget.reserved});
}
