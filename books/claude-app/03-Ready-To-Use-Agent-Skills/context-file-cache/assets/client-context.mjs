/** Original, local teaching models. No network, disk or server-cache behavior. */
export class InlineBudget {
  #owner; #epoch = 0; #entries = new Map(); #pending = new Map();
  constructor({ owner, limit }) {
    if (!Number.isSafeInteger(limit) || limit < 0) throw new RangeError('Invalid byte limit');
    this.#owner = owner; this.limit = limit;
  }
  get used() { return [...this.#entries.values(), ...this.#pending.values()].reduce((a, b) => a + b, 0); }
  reserve(text) {
    if (typeof text !== 'string') throw new TypeError('Expected immutable text');
    const bytes = new TextEncoder().encode(text).byteLength;
    if (this.used + bytes > this.limit) return null;
    const key = Symbol('reservation'), epoch = this.#epoch, owner = this.#owner;
    this.#pending.set(key, bytes);
    const live = () => epoch === this.#epoch && owner === this.#owner && this.#pending.has(key);
    return Object.freeze({ bytes,
      release: () => live() ? this.#pending.delete(key) : false,
      commit: id => {
        if (!live()) return false;
        if (typeof id !== 'string' || !id || this.#entries.has(id)) throw new Error('Duplicate or invalid attachment identity');
        this.#entries.set(id, bytes); this.#pending.delete(key); return true;
      },
    });
  }
  remove(id) { return this.#entries.delete(id); }
  switchOwner(owner) {
    this.#epoch++; this.#owner = owner; this.#entries.clear(); this.#pending.clear();
  }
}

export class PreviewPool {
  #entries = new Map();
  constructor(createURL, revokeURL) { this.createURL = createURL; this.revokeURL = revokeURL; }
  acquire(file) {
    if (!file || typeof file !== 'object') throw new TypeError('Expected File/Blob object identity');
    let entry = this.#entries.get(file);
    if (!entry) { entry = { url: this.createURL(file), count: 0 }; this.#entries.set(file, entry); }
    entry.count++; let released = false;
    return Object.freeze({ url: entry.url, release: () => {
      if (released) return false;
      released = true; entry.count--;
      if (entry.count === 0) { this.revokeURL(entry.url); this.#entries.delete(file); }
      return true;
    } });
  }
  get size() { return this.#entries.size; }
}
