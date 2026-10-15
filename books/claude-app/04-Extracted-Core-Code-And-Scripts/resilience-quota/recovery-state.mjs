/** Original state machines illustrating ownership and recovery boundaries. */
export class MemoryStorage {
  constructor({ failReads = false, failWrites = false } = {}) { this.values = new Map(); this.failReads = failReads; this.failWrites = failWrites; }
  getItem(key) { if (this.failReads) throw new Error('storage denied'); return this.values.get(key) ?? null; }
  setItem(key, value) { if (this.failWrites) throw new Error('storage full'); this.values.set(key, value); }
  removeItem(key) { if (this.failWrites) throw new Error('storage denied'); this.values.delete(key); }
}
const key = 'teaching-backoff-v1';
const safe = (fn, fallback) => { try { return fn(); } catch { return fallback; } };
/** Single writer, nondecreasing finite clock, trusted synchronous stores.
 * order persists ordering across equal timestamps; failures=0 is a clear tombstone.
 * At least one successful write is required for a durable record/clear.
 */
export class BackoffLedger {
  constructor(local, session, now = () => Date.now()) { Object.assign(this, { local, session, now }); }
  parse(raw) {
    return safe(() => {
      const x = JSON.parse(raw), now = this.now();
      if (!x || x.v !== 1 || !Number.isInteger(x.failures) || x.failures < 0 || !Number.isFinite(now) || !Number.isFinite(x.at) || x.at < 0 || x.at > now + 60000 || now - x.at >= 300000) return null;
      const order = x.order ?? 0; // Older v1 records predate persistent ordering.
      if (!Number.isSafeInteger(order) || order < 0) return null;
      return { v: 1, failures: Math.min(15, x.failures), at: x.at, order };
    }, null);
  }
  latest() {
    const a = this.parse(safe(() => this.local.getItem(key), null));
    const b = this.parse(safe(() => this.session.getItem(key), null));
    // Timestamp remains primary for old v1 records; same-clock operations use order.
    const latest = b && (!a || b.at > a.at || (b.at === a.at && (b.order > a.order || (b.order === a.order && b.failures > a.failures)))) ? b : a;
    if (latest === b && b && safe(() => { this.local.setItem(key, JSON.stringify(b)); return true; }, false)) safe(() => this.session.removeItem(key));
    return latest;
  }
  read() { const latest = this.latest(); return latest?.failures ? latest : null; }
  write(failures, prior) {
    const at = this.now(), order = (prior?.order ?? 0) + 1;
    if (!Number.isFinite(at) || at < 0 || (prior && at < prior.at) || !Number.isSafeInteger(order)) return { stored: false };
    const record = { v: 1, failures, at, order };
    const stored = safe(() => { this.local.setItem(key, JSON.stringify(record)); return true; }, false) || safe(() => { this.session.setItem(key, JSON.stringify(record)); return true; }, false);
    return { ...record, stored };
  }
  record() {
    const prior = this.latest();
    return this.write(Math.min(15, (prior?.failures ?? 0) + 1), prior);
  }
  clear() { return this.write(0, this.latest()); }
}
/** Ack after application; three failures at a known cursor avoid an infinite poison replay. */
export class CursorConsumer {
  constructor() { this.cursor = undefined; this.poison = undefined; this.strikes = 0; this.applied = []; }
  deliver(seq, payload, apply) {
    const known = Number.isSafeInteger(seq) && seq > 0;
    if (known && this.cursor !== undefined && seq <= this.cursor) return 'duplicate';
    try { apply(payload); }
    catch {
      if (!known) return 'dropped-no-id';
      this.strikes = seq === this.poison ? this.strikes + 1 : 1;
      this.poison = seq;
      if (this.strikes < 3) return 'replay';
      this.cursor = Math.max(this.cursor ?? 0, seq); this.poison = undefined; this.strikes = 0;
      return 'skipped-poison';
    }
    this.applied.push(payload);
    if (known) { this.cursor = Math.max(this.cursor ?? 0, seq); this.poison = undefined; this.strikes = 0; }
    return 'applied';
  }
  resetCursor() { this.cursor = undefined; this.poison = undefined; this.strikes = 0; }
}
function plainText(doc) {
  if (doc?.type !== 'doc' || !Array.isArray(doc.content)) return null;
  const lines = [];
  for (const block of doc.content) {
    if (block.type !== 'paragraph') return null;
    let line = '';
    for (const item of block.content ?? []) {
      if (item.type !== 'text' || typeof item.text !== 'string' || item.marks?.length || item.text.includes('\n')) return null;
      line += item.text;
    }
    lines.push(line);
  }
  return lines.join('\n');
}
export function makeMirror(doc, { account, session, attachmentCount = 0 }, now) {
  if (!account || !session) return null;
  const text = plainText(doc);
  const result = { account, session, at: now, attachmentCount };
  if (text === null) return { ...result, omitted: 'not-plain-text' };
  if (new TextEncoder().encode(text).byteLength > 4096) return { ...result, omitted: 'exceeds-capacity' };
  return { ...result, text };
}
export function readMirror(mirror, owner) {
  if (!mirror || !owner.account || !owner.session || mirror.account !== owner.account || mirror.session !== owner.session) return null;
  if (typeof mirror.text === 'string' && new TextEncoder().encode(mirror.text).byteLength <= 4096 && mirror.omitted === undefined) return mirror;
  if (mirror.text === undefined && ['not-plain-text', 'exceeds-capacity'].includes(mirror.omitted)) return mirror;
  return null;
}
export class DraftHydration {
  constructor(owner) { this.owner = { ...owner }; this.epoch = 0; this.edits = 0; this.hydrated = false; this.text = ''; this.temporary = false; }
  begin() { return { owner: { ...this.owner }, epoch: this.epoch, edits: this.edits }; }
  edit(text) { this.text = text; this.edits++; }
  switchOwner(owner) { this.owner = { ...owner }; this.epoch++; this.edits = 0; this.text = ''; this.hydrated = false; }
  restore(token, saved) {
    if (token.epoch !== this.epoch || token.owner.account !== this.owner.account || token.owner.session !== this.owner.session) return 'owner-changed';
    if (this.temporary) return 'temporary';
    this.hydrated = true;
    if (token.edits !== this.edits) return 'kept-new-edit';
    this.text = saved; return 'restored';
  }
  canPersist() { return this.hydrated && !this.temporary; }
}
/** Deliberately simulated server contract, not a claim about Claude's server. */
export class IdempotentServer {
  constructor() { this.turns = new Map(); this.executions = 0; }
  submit(turnId, prompt) {
    if (!turnId) throw new Error('turn identity required');
    const prior = this.turns.get(turnId);
    if (prior && prior.prompt !== prompt) throw new Error('same identity, different payload');
    if (prior) return prior.reply;
    const reply = { text: `accepted:${prompt}`, sequence: ++this.executions };
    this.turns.set(turnId, { prompt, reply }); return reply;
  }
}
export function quotaRoute({ kind, representative, resetAt, modelLimit, overage, creditRequired, errorCode }) {
  if (errorCode === 'thinking_messages_rate_limit_exceeded') return { view: 'thinking-limit', automaticRetry: false };
  if (errorCode === 'opus_messages_rate_limit_exceeded') return { view: 'upstream-handler', automaticRetry: false };
  if (kind !== 'exceeded_limit') return { view: kind === 'approaching_limit' ? 'warning' : 'unknown', automaticRetry: false };
  if (representative === 'concurrents') return { view: 'finish-active-work', automaticRetry: false };
  if (modelLimit || overage || creditRequired) return { view: 'specific-account-action', automaticRetry: false };
  return { view: 'wait-for-reset', resetAt, automaticRetry: false };
}
