/** Original teaching models. No target application code or dependencies. */
const countLimit = value => {
  if (!Number.isSafeInteger(value) || value < 0) throw RangeError('invalid count limit');
  return value;
};
const delayLimit = value => {
  if (!Number.isFinite(value) || value < 0 || value > 2_147_483_647) throw RangeError('invalid delay limit');
  return value;
};
// Budget changes require a new owner; public assignment must not disable a cap.
const fixedLimits = (target, values) => {
  for (const [key, value] of Object.entries(values)) Object.defineProperty(target, key, { value, enumerable: true });
};
export class FakeClock {
  time = 0; next = 1; tasks = new Map();
  now = () => this.time;
  schedule = (fn, delay = 0) => {
    const id = this.next++;
    this.tasks.set(id, { fn, at: this.time + Math.max(0, delay), id });
    return id;
  };
  cancel = id => this.tasks.delete(id);
  advance(ms = 0) {
    const end = this.time + ms;
    let steps = 0;
    while (true) {
      const task = [...this.tasks.values()].sort((a, b) => a.at - b.at || a.id - b.id)[0];
      if (!task || task.at > end) break;
      if (++steps > 10000) throw Error('runaway scheduler');
      this.tasks.delete(task.id); this.time = task.at; task.fn();
    }
    this.time = end;
  }
}

/** Coalesce complete snapshots, never arbitrary deltas. Terminal flush is explicit. */
export class SnapshotPresenter {
  constructor({ clock, commit, visibleDelay = 24, hiddenDelay = 160, maxChars = 1_000_000 }) {
    fixedLimits(this, { visibleDelay: delayLimit(visibleDelay), hiddenDelay: delayLimit(hiddenDelay), maxChars: countLimit(maxChars) });
    Object.assign(this, { clock, commit });
    this.pending = null; this.timer = null; this.revision = 0;
    this.hidden = false; this.closed = false; this.first = true;
    this.metrics = { updates: 0, commits: 0, coalesced: 0 };
  }
  accept(text, { terminal = false } = {}) {
    if (this.closed) return false;
    if (typeof text !== 'string' || text.length > this.maxChars) throw RangeError('snapshot limit');
    this.metrics.updates++;
    if (this.pending) this.metrics.coalesced++;
    this.pending = Object.freeze({ text, revision: ++this.revision, terminal });
    // Commit before closing permits a consumer to dispose safely. Reentrant updates
    // are accepted during normal commits; terminal input closes ingress first.
    if (terminal) this.closed = true;
    if (terminal || this.first) { this.first = false; this.flush(); }
    else this.arm();
    return true;
  }
  arm() {
    if (!this.pending || this.timer !== null) return;
    this.timer = this.clock.schedule(() => { this.timer = null; this.flush(); },
      this.hidden ? this.hiddenDelay : this.visibleDelay);
  }
  flush() {
    if (this.timer !== null) this.clock.cancel(this.timer);
    this.timer = null;
    const snapshot = this.pending;
    this.pending = null;
    if (snapshot) { this.metrics.commits++; this.commit(snapshot); }
    this.arm();
  }
  setHidden(hidden) {
    if (this.hidden === hidden) return;
    this.hidden = hidden;
    if (this.timer !== null) this.clock.cancel(this.timer);
    this.timer = null;
    if (!hidden) this.flush(); else this.arm();
  }
  dispose() {
    if (this.timer !== null) this.clock.cancel(this.timer);
    this.timer = null; this.pending = null; this.closed = true;
  }
}

/** Educational subset: blank-line paragraphs + top-level fenced code only.
 * Lists, tables, links and math are NOT independently parsed in this model.
 * Supply a standards-compliant finalParser before rendering real Markdown.
 */
export class StableBlocks {
  constructor({ finalParser = text => ({ source: text }), maxChars = 1_000_000 } = {}) {
    fixedLimits(this, { maxChars: countLimit(maxChars) });
    this.finalParser = finalParser; this.reset();
  }
  reset() {
    this.text = ''; this.scanned = 0; this.blockStart = 0; this.fence = null;
    this.blocks = []; this.final = null; this.scannedChars = 0;
  }
  update(text, { terminal = false } = {}) {
    if (typeof text !== 'string' || text.length > this.maxChars) throw RangeError('document limit');
    if (!text.startsWith(this.text) || this.final !== null) this.reset();
    this.text = text;
    while (true) {
      const end = text.indexOf('\n', this.scanned);
      if (end < 0) break; // Never commit grammar state from an incomplete line.
      const line = text.slice(this.scanned, end).replace(/\r$/, '');
      this.scannedChars += end + 1 - this.scanned;
      const opener = /^(?: {0,3})(`{3,}|~{3,})(.*)$/.exec(line);
      if (!this.fence && opener) this.fence = { char: opener[1][0], count: opener[1].length };
      else if (this.fence) {
        const close = /^(?: {0,3})(`{3,}|~{3,})\s*$/.exec(line);
        if (close && close[1][0] === this.fence.char && close[1].length >= this.fence.count) this.fence = null;
      } else if (line.trim() === '' && end + 1 > this.blockStart) {
        this.blocks.push(Object.freeze({ start: this.blockStart, end: end + 1, text: text.slice(this.blockStart, end + 1) }));
        this.blockStart = end + 1;
      }
      this.scanned = end + 1;
    }
    if (terminal) this.final = this.finalParser(text); // Authoritative whole-document pass.
    return Object.freeze({ blocks: Object.freeze(this.blocks.slice()), tail: text.slice(this.blockStart), final: this.final });
  }
}

/** Explicit accounting, not actual heap size; rejected replacement keeps old value. */
export class WeightedLRU {
  constructor({ entries = 100, weight = 1_000_000, itemWeight = weight } = {}) {
    countLimit(entries);
    if (![weight, itemWeight].every(x => Number.isFinite(x) && x >= 0)) throw RangeError('invalid cache limits');
    fixedLimits(this, { entries, weight, itemWeight }); this.items = new Map(); this.used = 0;
  }
  get(key) {
    const item = this.items.get(key);
    if (!item) return undefined;
    this.items.delete(key); this.items.set(key, item); return item.value;
  }
  put(key, value, size) {
    if (!Number.isFinite(size) || size < 0) throw RangeError('invalid cache weight');
    if (this.entries < 1 || size > this.itemWeight || size > this.weight) return false;
    this.delete(key);
    // Evict before adding: two individually finite weights may overflow their sum.
    while (this.items.size + 1 > this.entries || !Number.isFinite(this.used + size) || this.used + size > this.weight)
      this.delete(this.items.keys().next().value);
    this.items.set(key, { value, size }); this.used += size;
    return true;
  }
  delete(key) {
    const item = this.items.get(key);
    if (item) {
      this.items.delete(key);
      // Recompute bounded accounting so fractional subtraction leaves no residue.
      this.used = [...this.items.values()].reduce((sum, entry) => sum + entry.size, 0);
    }
  }
  clear() { this.items.clear(); this.used = 0; }
}

/** One in-flight stateless formatting task + one latest snapshot.
 * Unlike the target's delta highlighter protocol this is replaceable full work.
 * The per-job sequence prevents late replies from an old worker/theme/navigation.
 */
export class LatestWorkerLane {
  constructor({ send, publish, fallback, maxChars = 100_000, cancel = () => {} }) {
    fixedLimits(this, { maxChars: countLimit(maxChars) });
    Object.assign(this, { send, publish, fallback, cancel });
    this.epoch = 1; this.sequence = 0; this.busy = null; this.latest = null; this.closed = false;
  }
  submit(text) {
    if (this.closed) return false;
    if (typeof text !== 'string') throw TypeError('text must be a string');
    if (text.length > this.maxChars) {
      const sequence = this.sequence, epoch = this.reset();
      if (!this.closed && this.epoch === epoch && this.sequence === sequence) this.fallback(text, 'oversize');
      return false;
    }
    this.latest = Object.freeze({ text, epoch: this.epoch, sequence: ++this.sequence });
    this.pump(); return true;
  }
  pump() {
    if (this.closed || this.busy || !this.latest) return;
    this.busy = this.latest; this.latest = null;
    const job = this.busy;
    try { this.send(job); }
    catch { this.fail(job, 'send-failed'); }
  }
  matches(job) { return this.busy && job.epoch === this.busy.epoch && job.sequence === this.busy.sequence; }
  reply(job, result) {
    if (this.closed || !this.matches(job)) return false;
    this.busy = null;
    // Never replace a newer requested snapshot with an older formatted result.
    if (!this.latest) this.publish(result, job);
    this.pump(); return true;
  }
  fail(job, reason = 'worker-failed') {
    if (!this.matches(job) || this.closed) return false;
    const source = this.latest?.text ?? this.busy.text;
    const sequence = this.sequence, epoch = this.reset();
    // Cancellation adapters may synchronously submit newer work or dispose.
    if (!this.closed && this.epoch === epoch && this.sequence === sequence) this.fallback(source, reason);
    return true;
  }
  reset() {
    const busy = this.busy;
    const epoch = ++this.epoch; this.busy = null; this.latest = null;
    // Revocation is local even if the adapter cannot acknowledge cancellation.
    if (busy) { try { this.cancel(busy); } catch {} }
    return epoch;
  }
  dispose() { this.closed = true; this.reset(); }
}

/** Cooperative slicing checks after each unit; one unit can exceed the budget. */
export async function runSlices(units, { visit, now, yieldTask, budget = 4, signal }) {
  if (!Number.isFinite(budget) || !(budget > 0)) throw RangeError('budget must be finite and positive');
  let start = now(), yields = 0, visited = 0;
  for (const unit of units) {
    signal?.throwIfAborted();
    await visit(unit); visited++;
    signal?.throwIfAborted();
    if (now() - start >= budget) {
      await yieldTask(); yields++; signal?.throwIfAborted(); start = now();
    }
  }
  return { visited, yields };
}

/** A safe text fallback. Escaping is independent of scheduling. */
export function escapeHTML(text) {
  return text.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
