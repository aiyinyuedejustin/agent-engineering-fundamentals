/** Original teaching model. No Claude code is imported or executed. */
export const MODES = Object.freeze({
  off: {},
  legacy: { overload: { limit: 10, base: 5000, factor: 1.5, jitter: .1, inheritedBudget: true } },
  expanded: {
    network: { limit: 30, base: 500, factor: 2, jitter: .1, cap: 4 },
    server: { limit: 2, base: 8000, factor: 1.5, jitter: .15 },
    overload: { limit: 5, base: 8000, factor: 1.5, jitter: .15 }
  },
  emergency: { overload: { limit: 3, base: 45000, factor: 2, jitter: .2, cap: 2 } }
});
export function chooseMode({ disabled = false, emergency = false, idempotency = false } = {}) {
  return disabled ? 'off' : emergency ? 'emergency' : idempotency ? 'expanded' : 'legacy';
}
export function classify(error) {
  if (error.abort) return null;
  if (error.kind === 'network' || error.kind === 'incomplete-stream') return 'network';
  if (error.status === 409 || error.code === 'container-in-use' || error.status === 429) return null;
  if (error.status >= 400 && error.status < 500) return null;
  if (error.kind === 'overload') return 'overload';
  return error.status >= 500 ? 'server' : null;
}
export function backoff({ base, factor, jitter, cap = 10 }, exponent, random = .5) {
  if (!Number.isFinite(exponent) || exponent < 0 || !Number.isFinite(random) || random < 0 || random > 1) throw new RangeError('invalid backoff input');
  const nominal = base * factor ** Math.min(exponent, cap);
  return Math.floor(Math.max(0, nominal * (1 + jitter * (2 * random - 1))));
}
/** Pure reducer: decisions, not network requests. Failure limits include the initial failed call. */
export class RetryBudget {
  constructor({ mode = 'legacy', inherited = 0, inheritedClass, perTurn = false, honorStated = false } = {}) {
    if (!(mode in MODES)) throw new TypeError('unknown mode');
    if (!Number.isInteger(inherited) || inherited < 0) throw new RangeError('invalid inherited failures');
    Object.assign(this, { mode, inherited, inheritedClass, perTurn, honorStated });
    this.counts = { network: 0, server: 0, overload: 0 };
    this.calls = 0; this.done = false;
  }
  failure(error, random = .5) {
    if (this.done) throw new Error('terminal budget');
    if (++this.calls >= 50) return this.stop('runaway');
    const originalClass = error.abort ? null : ['legacy', 'emergency'].includes(this.mode)
      ? (error.kind === 'overload' ? 'overload' : null) : classify(error);
    let errorClass = originalClass;
    if (this.mode !== 'expanded' && errorClass !== 'overload') errorClass = null;
    if (errorClass === 'network' && this.counts.network >= 3 && MODES[this.mode].server) errorClass = 'server';
    const rule = MODES[this.mode][errorClass];
    if (!rule) return this.stop(error.abort ? 'cancelled' : 'not-retryable');
    const count = ++this.counts[errorClass];
    const limit = rule.inheritedBudget && this.perTurn && this.inheritedClass === errorClass
      ? Math.max(1, rule.limit - this.inherited) : rule.limit;
    const stated = this.honorStated && errorClass === 'overload' && Number.isFinite(error.retryAfterMs) && error.retryAfterMs > 0
      ? Math.min(120000, error.retryAfterMs) : undefined;
    const stoppedForWait = this.perTurn && stated !== undefined && stated > 60000;
    if (count >= limit || stoppedForWait) return this.stop(stoppedForWait ? 'stated-wait' : 'exhausted', { errorClass, originalClass, count, limit, stated });
    const delay = backoff(rule, count - 1 + Math.min(this.inherited, 4), random);
    const wait = stated === undefined ? undefined : stated * (1 + .1 * random);
    return { action: 'retry', originalClass, errorClass, count, limit, delayMs: Math.max(delay, wait ?? 0), nominalDelayMs: delay, statedWaitMs: wait };
  }
  stop(reason, extra = {}) { this.done = true; return { action: 'stop', reason, ...extra }; }
}
export function streamOutcome({ stopped, successorPending, networkError, cleanClose, started, stopReason, expanded, detached, turnId, resendGate, aborted }) {
  if (aborted) return 'cancelled';
  if (networkError && stopped && !successorPending) return 'succeeded-unclean';
  if (cleanClose && expanded && !detached && turnId && resendGate && started && (successorPending || (!stopped && !stopReason))) return 'resend-eligible';
  if (networkError) return 'transport-error';
  return stopped || stopReason ? 'settled' : 'incomplete';
}
/** Original stricter retry-after parser, not the target helper. */
export function parseRetryAfter(value, now) {
  if (typeof value !== 'string' || value.trim() === '') return undefined;
  const text = value.trim();
  if (/^\d+$/.test(text)) {
    const result = Number(text) * 1000;
    return Number.isFinite(result) ? result : undefined;
  }
  // Reject signed/fractional numeric tokens instead of letting Date.parse reinterpret them.
  if (/^[+\-\d.]/.test(text)) return undefined;
  const date = Date.parse(text);
  return Number.isFinite(date) ? Math.max(0, date - now) : undefined;
}
export function abortableSleep(ms, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) { reject(signal.reason); return; }
    const cancel = () => { clearTimeout(timer); signal.removeEventListener('abort', cancel); reject(signal.reason); };
    const timer = setTimeout(() => { signal?.removeEventListener('abort', cancel); resolve(); }, ms);
    signal?.addEventListener('abort', cancel, { once: true });
  });
}
