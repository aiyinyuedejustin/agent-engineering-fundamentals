import test from 'node:test';
import assert from 'node:assert/strict';
import { MODES, chooseMode, classify, backoff, RetryBudget, streamOutcome, parseRetryAfter, abortableSleep } from '../resilience-core.mjs';
import { MemoryStorage, BackoffLedger, CursorConsumer, makeMirror, readMirror, DraftHydration, IdempotentServer, quotaRoute } from '../recovery-state.mjs';
const network = { kind: 'network' }, overloaded = { kind: 'overload', status: 529 };
const doc = text => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text }] }] });
const owner = { account: 'test-account', session: 'test-session' };
const fail = () => { throw new Error('cannot apply'); };
function runFailures(options, error) {
  const b = new RetryBudget(options), trace = [];
  for (let i = 0; i < 60; i++) { const d = b.failure(error); trace.push(d); if (d.action === 'stop') return trace; }
  throw new Error('test runaway');
}
test('mode precedence: off beats all; emergency beats expanded', () => {
  assert.equal(chooseMode({ disabled: true, emergency: true, idempotency: true }), 'off');
  assert.equal(chooseMode({ emergency: true, idempotency: true }), 'emergency');
  assert.equal(chooseMode({ idempotency: true }), 'expanded'); assert.equal(chooseMode(), 'legacy');
});
for (const status of [400, 401, 403, 404, 409, 429]) test(`HTTP ${status} is not generic completion retry`, () => assert.equal(classify({ status }), null));
test('500 generic and 529 overloaded remain distinct', () => { assert.equal(classify({ status: 500 }), 'server'); assert.equal(classify(overloaded), 'overload'); });
test('in-use conflict can be signaled outside 409', () => assert.equal(classify({ status: 500, code: 'container-in-use' }), null));
test('expanded continuous network reaches five calls, not thirty', () => {
  const trace = runFailures({ mode: 'expanded' }, network);
  assert.equal(trace.length, 5);
  assert.deepEqual(trace.map(x => x.errorClass), ['network', 'network', 'network', 'server', 'server']);
  assert.deepEqual(trace.slice(0, -1).map(x => x.delayMs), [500, 1000, 2000, 8000]);
  assert.equal(trace.at(-1).reason, 'exhausted');
});
test('limits include initial failure, not additional retries', () => {
  for (const [mode, total] of [['legacy', 10], ['expanded', 5], ['emergency', 3]]) assert.equal(runFailures({ mode }, overloaded).length, total);
  assert.equal(runFailures({ mode: 'expanded' }, { status: 500 }).length, 2);
});
test('mode-specific classifiers: legacy overload-only and off empty', () => {
  assert.equal(runFailures({ mode: 'legacy' }, network).length, 1);
  assert.equal(runFailures({ mode: 'off' }, overloaded).length, 1);
  // A synthetic type/status combination tests classifier precedence, not a real server response.
  assert.equal(runFailures({ mode: 'legacy' }, { ...overloaded, status: 429 }).length, 10);
  assert.equal(runFailures({ mode: 'emergency' }, { ...overloaded, status: 429 }).length, 3);
  assert.equal(runFailures({ mode: 'expanded' }, { ...overloaded, status: 429 }).length, 1);
});
test('inherited legacy matching class consumes budget', () => assert.equal(runFailures({ mode: 'legacy', inherited: 8, inheritedClass: 'overload', perTurn: true }, overloaded).length, 2));
test('different inherited class changes delay, not legacy failure limit', () => {
  const trace = runFailures({ mode: 'legacy', inherited: 8, inheritedClass: 'server', perTurn: true }, overloaded);
  assert.equal(trace.length, 10); assert.equal(trace[0].delayMs, 25312);
});
test('expanded does not subtract inherited count from class limit', () => assert.equal(runFailures({ mode: 'expanded', inherited: 15, inheritedClass: 'overload', perTurn: true }, overloaded).length, 5));
test('exponent cap is different from a retry-count cap', () => {
  assert.equal(backoff(MODES.expanded.network, 4), 8000); assert.equal(backoff(MODES.expanded.network, 40), 8000);
});
test('jitter stays in its declared interval across 1001 random samples', () => {
  for (let i = 0; i <= 1000; i++) { const x = backoff(MODES.expanded.server, 2, i / 1000); assert.ok(x >= 15300 && x <= 20700); }
});
test('invalid exponent and random input rejected', () => {
  for (const x of [-1, NaN, Infinity]) assert.throws(() => backoff(MODES.legacy.overload, x));
  for (const random of [-1, 2, NaN, Infinity]) assert.throws(() => backoff(MODES.legacy.overload, 0, random));
});
test('stated and exponential waits overlap using max, not sum', () => {
  const b = new RetryBudget({ mode: 'expanded', honorStated: true });
  const x = b.failure({ ...overloaded, retryAfterMs: 20000 }, 0);
  assert.equal(x.delayMs, 20000); assert.equal(x.nominalDelayMs, 6800);
});
test('long stated wait hands control back only with per-turn option', () => {
  const opts = { mode: 'legacy', honorStated: true, perTurn: true };
  assert.equal(new RetryBudget(opts).failure({ ...overloaded, retryAfterMs: 60001 }).reason, 'stated-wait');
  assert.equal(new RetryBudget(opts).failure({ ...overloaded, retryAfterMs: 60000 }).action, 'retry');
  assert.equal(new RetryBudget({ ...opts, perTurn: false }).failure({ ...overloaded, retryAfterMs: 60001 }).action, 'retry');
});
test('server stated wait clamps at two minutes', () => assert.equal(new RetryBudget({ mode: 'legacy', honorStated: true, perTurn: true }).failure({ ...overloaded, retryAfterMs: 1e9 }).stated, 120000));
test('aborted error never spends a retry', () => assert.equal(new RetryBudget({ mode: 'expanded' }).failure({ abort: true }).reason, 'cancelled'));
test('sleep is cancellable while waiting', async () => {
  const c = new AbortController(), e = new Error('cancelled'); const pending = abortableSleep(60000, c.signal); c.abort(e); await assert.rejects(pending, x => x === e);
});
test('sleep honors already cancelled signal', async () => {
  const c = new AbortController(); c.abort(new Error('pre-cancelled')); await assert.rejects(abortableSleep(60000, c.signal), /pre-cancelled/);
});
test('terminal budget cannot silently restart', () => {
  const b = new RetryBudget({ mode: 'off' }); b.failure(overloaded); assert.throws(() => b.failure(overloaded), /terminal/);
});
test('network failure after message stop can be successful unclean close', () => assert.equal(streamOutcome({ stopped: true, networkError: true }), 'succeeded-unclean'));
test('pending successor after stop defeats trailing-error suppression', () => assert.equal(streamOutcome({ stopped: true, successorPending: true, networkError: true }), 'transport-error'));
test('resend gate needs every identity and lifecycle condition', () => {
  const all = { cleanClose: true, expanded: true, turnId: 'turn', resendGate: true, started: true };
  assert.equal(streamOutcome(all), 'resend-eligible');
  for (const key of ['cleanClose', 'expanded', 'turnId', 'resendGate', 'started']) assert.notEqual(streamOutcome({ ...all, [key]: false }), 'resend-eligible');
  assert.notEqual(streamOutcome({ ...all, detached: true }), 'resend-eligible');
  assert.equal(streamOutcome({ ...all, aborted: true }), 'cancelled');
});
test('retry-after accepts seconds and HTTP date', () => {
  const now = Date.UTC(2026, 0, 1);
  assert.equal(parseRetryAfter('15', now), 15000);
  assert.equal(parseRetryAfter('Thu, 01 Jan 2026 00:00:20 GMT', now), 20000);
  assert.equal(parseRetryAfter('Wed, 31 Dec 2025 23:59:59 GMT', now), 0);
});
test('strict teaching parser rejects malformed numeric retry-after', () => { for (const x of ['', '-1', '1.5', 'NaN', 'wat']) assert.equal(parseRetryAfter(x, 0), undefined); });
test('backoff history lasts less than five minutes and caps at fifteen', () => {
  let now = 1e6; const ledger = new BackoffLedger(new MemoryStorage(), new MemoryStorage(), () => now);
  for (let i = 0; i < 50; i++) ledger.record(); assert.equal(ledger.read().failures, 15);
  now += 299999; assert.equal(ledger.read().failures, 15); now++; assert.equal(ledger.read(), null);
});
test('session fallback promotes to local when storage recovers', () => {
  const local = new MemoryStorage({ failWrites: true }), session = new MemoryStorage();
  const ledger = new BackoffLedger(local, session, () => 1e6);
  assert.equal(ledger.record().stored, true); assert.equal(local.values.size, 0); assert.equal(session.values.size, 1);
  local.failWrites = false; assert.equal(ledger.read().failures, 1); assert.equal(local.values.size, 1); assert.equal(session.values.size, 0);
});
test('unavailable storage does not crash the recovery UI', () => {
  const broken = new MemoryStorage({ failReads: true, failWrites: true }); const ledger = new BackoffLedger(broken, broken);
  assert.equal(ledger.read(), null); assert.equal(ledger.record().stored, false); assert.doesNotThrow(() => ledger.clear());
});
test('ledger rejects corruption, unsupported versions and far future stamps', () => {
  const ledger = new BackoffLedger(new MemoryStorage(), new MemoryStorage(), () => 1e6);
  for (const raw of ['{', 'null', '{"v":2}', JSON.stringify({ v: 1, failures: -1, at: 1e6 }), JSON.stringify({ v: 1, failures: 1, at: 1060001 })]) assert.equal(ledger.parse(raw), null);
});
test('success clears local and session failure history', () => {
  const l = new MemoryStorage(), s = new MemoryStorage(), ledger = new BackoffLedger(l, s); ledger.record(); ledger.clear(); assert.equal(ledger.read(), null);
});
test('cursor commits only after application succeeds', () => {
  const c = new CursorConsumer(); assert.equal(c.deliver(7, 'x', fail), 'replay'); assert.equal(c.cursor, undefined);
  assert.equal(c.deliver(7, 'x', () => {}), 'applied'); assert.equal(c.cursor, 7);
});
test('poison frame skips on third delivery and subsequent events progress', () => {
  const c = new CursorConsumer(); assert.deepEqual([1,2,3].map(() => {
    const outcome = c.deliver(7, 'poison', fail);
    c.deliver(undefined, 'id-less control payload', () => {});
    return outcome;
  }), ['replay', 'replay', 'skipped-poison']);
  assert.equal(c.cursor, 7); assert.equal(c.deliver(8, 'next', () => {}), 'applied'); assert.equal(c.cursor, 8);
});
test('ID-less and invalid-sequence payloads are applied without cursor commit', () => {
  const c = new CursorConsumer(); assert.equal(c.deliver(undefined, 'x', fail), 'dropped-no-id'); assert.equal(c.cursor, undefined);
  for (const seq of [undefined, 0, -1, NaN, 1.5, Number.MAX_SAFE_INTEGER + 1]) assert.equal(c.deliver(seq, 'control', () => {}), 'applied');
  assert.equal(c.cursor, undefined);
});
test('teaching cursor duplicate filtering avoids double apply', () => {
  const c = new CursorConsumer(); let calls = 0; c.deliver(7, 'x', () => calls++); assert.equal(c.deliver(7, 'x', () => calls++), 'duplicate'); assert.equal(calls, 1);
});
test('410-style cursor reset permits fresh snapshot delivery', () => { const c = new CursorConsumer(); c.deliver(10, 'x', () => {}); c.resetCursor(); assert.equal(c.deliver(1, 'new', () => {}), 'applied'); });
test('mirror measures UTF-8 bytes, not JS character count', () => {
  assert.equal(makeMirror(doc('a'.repeat(4096)), owner, 0).text.length, 4096);
  assert.equal(makeMirror(doc('a'.repeat(4097)), owner, 0).omitted, 'exceeds-capacity');
  assert.equal(makeMirror(doc('中'.repeat(1365)), owner, 0).text.length, 1365);
  assert.equal(makeMirror(doc('中'.repeat(1366)), owner, 0).omitted, 'exceeds-capacity');
  assert.equal(makeMirror(doc('😀'.repeat(1024)), owner, 0).text.length, 2048);
  assert.equal(makeMirror(doc('😀'.repeat(1025)), owner, 0).omitted, 'exceeds-capacity');
});
test('rich text mirror stores omission metadata, never flattens marks silently', () => {
  const d = doc('bold'); d.content[0].content[0].marks = [{ type: 'bold' }]; const m = makeMirror(d, { ...owner, attachmentCount: 2 }, 0);
  assert.equal(m.omitted, 'not-plain-text'); assert.equal(m.text, undefined); assert.equal(m.attachmentCount, 2);
});
test('mirrors require account and session match', () => {
  const m = makeMirror(doc('private'), owner, 0); assert.equal(readMirror(m, owner).text, 'private');
  assert.equal(readMirror(m, { ...owner, account: 'other' }), null); assert.equal(readMirror(m, { ...owner, session: 'other' }), null);
});
test('teaching reader rejects forged oversized UTF-8 mirror', () => assert.equal(readMirror({ ...owner, text: '中'.repeat(4096) }, owner), null));
test('unhydrated draft suppresses writes', () => { const d = new DraftHydration(owner); assert.equal(d.canPersist(), false); assert.equal(d.restore(d.begin(), 'saved'), 'restored'); assert.equal(d.canPersist(), true); });
test('typing during hydration wins over old disk value', () => { const d = new DraftHydration(owner), token = d.begin(); d.edit('new'); assert.equal(d.restore(token, 'old'), 'kept-new-edit'); assert.equal(d.text, 'new'); });
test('account switch invalidates an in-flight restoration', () => { const d = new DraftHydration(owner), token = d.begin(); d.switchOwner({ account: 'other', session: 'other' }); assert.equal(d.restore(token, 'secret'), 'owner-changed'); assert.equal(d.text, ''); });
test('temporary session never persists the teaching draft', () => { const d = new DraftHydration(owner); d.temporary = true; assert.equal(d.restore(d.begin(), 'saved'), 'temporary'); assert.equal(d.canPersist(), false); });
test('simulated idempotency survives commit then lost acknowledgement', () => {
  const server = new IdempotentServer(); server.submit('turn-1', 'task'); const reply = server.submit('turn-1', 'task'); assert.equal(reply.sequence, 1); assert.equal(server.executions, 1);
});
test('same key with different payload is a conflict, not a duplicate', () => { const server = new IdempotentServer(); server.submit('turn', 'one'); assert.throws(() => server.submit('turn', 'two'), /different payload/); });
test('new key on resend duplicates work in the simulated server', () => { const server = new IdempotentServer(); server.submit('old', 'task'); server.submit('new', 'task'); assert.equal(server.executions, 2); });
test('quota routes distinguish concurrency, reset window, model and credits', () => {
  assert.equal(quotaRoute({ kind: 'exceeded_limit', representative: 'concurrents' }).view, 'finish-active-work');
  assert.equal(quotaRoute({ kind: 'exceeded_limit', representative: 'five_hour', resetAt: 123 }).resetAt, 123);
  assert.equal(quotaRoute({ kind: 'exceeded_limit', creditRequired: true }).view, 'specific-account-action');
  assert.equal(quotaRoute({ kind: 'exceeded_limit', modelLimit: true }).automaticRetry, false);
});
