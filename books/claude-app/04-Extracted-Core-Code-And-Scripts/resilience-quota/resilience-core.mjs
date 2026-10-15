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
/** Strict HTTP-date teaching parser: all three RFC 9110 forms, in UTC.
 * A leap-second :60 maps to the next representable JS millisecond instant.
 */
export function parseRetryAfter(value, now) {
  if (typeof value !== 'string' || value.trim() === '' || !Number.isFinite(now) || !Number.isFinite(new Date(now).getTime())) return undefined;
  const text = value.trim();
  if (/^\d+$/.test(text)) {
    const result = Number(text) * 1000;
    return Number.isFinite(result) ? result : undefined;
  }
  const shortDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const longDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  let match, dayName, day, monthName, year, hour, minute, second;
  if ((match = /^(Sun|Mon|Tue|Wed|Thu|Fri|Sat), (\d{2}) ([A-Z][a-z]{2}) (\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT$/.exec(text))) {
    [, dayName, day, monthName, year, hour, minute, second] = match;
  } else if ((match = /^(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), (\d{2})-([A-Z][a-z]{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) GMT$/.exec(text))) {
    [, dayName, day, monthName, year, hour, minute, second] = match;
    dayName = shortDays[longDays.indexOf(dayName)];
    const currentYear = new Date(now).getUTCFullYear();
    year = currentYear + (Number(year) - currentYear % 100 + 100) % 100;
    // A date >50 years ahead is interpreted as the most recent matching past year.
    const cutoff = new Date(now); cutoff.setUTCFullYear(currentYear + 50);
    const candidate = new Date(0);
    candidate.setUTCFullYear(year, months.indexOf(monthName), Number(day));
    candidate.setUTCHours(Number(hour), Number(minute), Number(second), 0);
    if (candidate.getTime() > cutoff.getTime()) year -= 100;
  } else if ((match = /^(Sun|Mon|Tue|Wed|Thu|Fri|Sat) ([A-Z][a-z]{2}) ( [1-9]|0[1-9]|[12]\d|3[01]) (\d{2}):(\d{2}):(\d{2}) (\d{4})$/.exec(text))) {
    [, dayName, monthName, day, hour, minute, second, year] = match;
  } else return undefined;
  [day, year, hour, minute, second] = [day, year, hour, minute, second].map(Number);
  const month = months.indexOf(monthName);
  if (year < 1900 || month < 0 || day < 1 || hour > 23 || minute > 59 || second > 60) return undefined;
  const date = new Date(0);
  date.setUTCFullYear(year, month, day); date.setUTCHours(hour, minute, Math.min(second, 59), 0);
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month || date.getUTCDate() !== day || shortDays[date.getUTCDay()] !== dayName) return undefined;
  return Math.max(0, date.getTime() + (second === 60 ? 1000 : 0) - now);
}
export function abortableSleep(ms, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) { reject(signal.reason); return; }
    const cancel = () => { clearTimeout(timer); signal.removeEventListener('abort', cancel); reject(signal.reason); };
    const timer = setTimeout(() => { signal?.removeEventListener('abort', cancel); resolve(); }, ms);
    signal?.addEventListener('abort', cancel, { once: true });
  });
}
