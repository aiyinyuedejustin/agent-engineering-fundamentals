/** Independent synthetic fixtures. Imports teaching models only; no target
 * bundle, author's test fixture, network, real account or production setting. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { setImmediate as immediate } from 'node:timers/promises';
import { VersionedSettings, rebaseDisjoint } from './authority-model.mjs';
import { consumeInSlices } from './sliced-consumer.mjs';

const utf8 = value => new TextEncoder().encode(value);
const command = (operationId, expectedRevision, enabled, label) => ({
  operationId, expectedRevision, value: { enabled, label },
});
const deferred = () => {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
};
async function* source(...chunks) { yield* chunks; }
const noWait = async () => {};

test('independent: three writers with one base version permit exactly one commit', () => {
  const store = new VersionedSettings({ enabled: false, label: 'harbor' }, 40);
  const requests = [command('enable', 40, true, 'harbor'),
    command('rename', 40, false, 'estuary'), command('third', 40, true, 'pier')];
  assert.deepEqual(requests.map(q => store.submit(q).kind), ['committed', 'conflict', 'conflict']);
  assert.deepEqual(store.read(), { revision: 41, value: { enabled: true, label: 'harbor' } });
  assert.equal(store.commits, 1);
});

test('independent: canonical binding ignores record insertion order but binds both scalar values', () => {
  const store = new VersionedSettings({ enabled: false, label: 'start' }, 2);
  store.submit(command('receipt', 2, true, 'a|b\u0000c'));
  const replay = store.submit({ value: { label: 'a|b\u0000c', enabled: true },
    expectedRevision: 2, operationId: 'receipt' });
  assert.equal(replay.replayed, true);
  assert.throws(() => store.submit(command('receipt', 2, false, 'a|b\u0000c')), /OPERATION_ID_REUSED/);
  assert.throws(() => store.submit(command('receipt', 2, true, 'a|b\u0000d')), /OPERATION_ID_REUSED/);
  assert.throws(() => store.submit(command('receipt', 3, true, 'a|b\u0000c')), /OPERATION_ID_REUSED/);
  assert.equal(store.commits, 1);
});

test('independent: successful and conflict receipts remain historical after several later commits', () => {
  const store = new VersionedSettings({ enabled: true, label: 's0' }, 100);
  const success = command('saved', 100, false, 's1');
  const conflict = command('stale', 99, true, 'stale');
  store.submit(success);
  store.submit(conflict);
  for (let i = 1; i <= 4; i++) store.submit(command('later-' + i, 100 + i, true, 's' + (i + 1)));
  assert.equal(store.submit(success).snapshot.revision, 101);
  assert.equal(store.submit(conflict).snapshot.revision, 101);
  assert.equal(store.read().revision, 105);
  assert.equal(store.commits, 5);
});

test('independent: another writer after rebase causes another conflict, not overwrite', () => {
  const store = new VersionedSettings({ enabled: false, label: 'canal' }, 17);
  const base = store.read();
  store.submit(command('first', 17, true, 'canal'));
  const current = store.read();
  const proposal = rebaseDisjoint(base.value, current.value, { label: 'wharf' });
  assert.equal(proposal.kind, 'proposed');
  store.submit(command('third', 18, true, 'breakwater'));
  assert.equal(store.submit({ operationId: 'rebased', expectedRevision: current.revision,
    value: proposal.value }).kind, 'conflict');
  assert.deepEqual(store.read(), { revision: 19, value: { enabled: true, label: 'breakwater' } });
});

test('independent: revision exhaustion still permits replay of the final successful operation', () => {
  const max = Number.MAX_SAFE_INTEGER;
  const store = new VersionedSettings({ enabled: false, label: 'before' }, max - 1);
  const last = command('last', max - 1, true, 'after');
  store.submit(last);
  assert.throws(() => store.submit(command('overflow', max, false, 'invalid')), /REVISION_EXHAUSTED/);
  assert.equal(store.submit(last).replayed, true);
  assert.equal(store.read().revision, max);
  assert.equal(store.commits, 1);
});

test('independent: no-op intent on a concurrently changed field is conservatively rejected', () => {
  assert.deepEqual(rebaseDisjoint({ enabled: true, label: 'old' },
    { enabled: true, label: 'new' }, { label: 'new' }), { kind: 'conflict', fields: ['label'] });
});

test('independent: literal expected frames survive every byte split, tiny slices and multibyte data', async () => {
  const bytes = utf8('id: k\rdata: 海🪷\r\ndata: x\r\n\r\nevent: end\ndata: final\n\n');
  const expected = [
    { event: '', data: '海🪷\nx', id: 'k', retry: undefined },
    { event: 'end', data: 'final', id: undefined, retry: undefined },
  ];
  for (let split = 0; split <= bytes.length; split++) {
    for (const sliceBytes of [1, 4, 13]) {
      const got = [];
      await consumeInSlices(source(bytes.subarray(0, split), bytes.subarray(split)),
        frame => got.push(frame), { sliceBytes, frameQuantum: 2, yieldToLoop: noWait });
      assert.deepEqual(got, expected, `split=${split}, slice=${sliceBytes}`);
    }
  }
});

test('independent: repeated blank frames are bounded even without data payload', async () => {
  const seen = [];
  const stats = await consumeInSlices(source(utf8('\n'.repeat(257))), frame => seen.push(frame),
    { sliceBytes: 19, frameQuantum: 7, yieldToLoop: noWait });
  assert.equal(seen.length, 257);
  assert.equal(stats.maxFramesReturned, 19);
  assert.equal(stats.maxPushBytes, 19);
  assert.equal(stats.maxCallbacksBetweenYields, 7);
  assert.ok(seen.every(frame => frame.data === ''));
});

test('independent: unfinished event budget accumulates across lines and upstream chunks', async () => {
  let deliveries = 0;
  await assert.rejects(consumeInSlices(source(utf8('data: a\n'), utf8('data: b\n\n')),
    () => { deliveries++; }, { sliceBytes: 2, frameQuantum: 1,
      decoderLimits: { maxLineCharacters: 7, maxEventCharacters: 13 }, yieldToLoop: noWait }),
  /SSE event limit/);
  assert.equal(deliveries, 0);
});

test('independent: invalid UTF-8 uses decoder replacement, preserving framed output', async () => {
  const bytes = Uint8Array.from([...utf8('data: '), 0xe2, 0x28, 0xa1, 10, 10]);
  const got = [];
  await consumeInSlices(source(bytes), frame => got.push(frame.data),
    { sliceBytes: 1, frameQuantum: 1, yieldToLoop: noWait });
  assert.deepEqual(got, ['�(�']);
});

test('independent boundary: abort does not settle a pending source next until next settles', async () => {
  const gate = deferred(), controller = new AbortController();
  const reason = new Error('audit-next-abort');
  let nextCalls = 0, returned = 0, settled = false, callbacks = 0;
  const stream = { [Symbol.asyncIterator]() { return this; },
    next() { nextCalls++; return gate.promise; },
    async return() { returned++; return { done: true }; } };
  const outcome = consumeInSlices(stream, () => { callbacks++; }, { signal: controller.signal,
    yieldToLoop: noWait }).then(() => { settled = true; return null; }, error => { settled = true; return error; });
  assert.equal(nextCalls, 1);
  controller.abort(reason);
  await immediate();
  assert.equal(settled, false);
  gate.resolve({ done: false, value: utf8('data: late\n\n') });
  assert.equal(await outcome, reason);
  assert.equal(callbacks, 0);
  assert.equal(returned, 1);
});

test('independent boundary: abort waits for an asynchronous callback to settle', async () => {
  const gate = deferred(), entered = deferred(), controller = new AbortController();
  const reason = new Error('audit-callback-abort');
  let settled = false, callbacks = 0;
  const outcome = consumeInSlices(source(utf8('data: held\n\ndata: untouched\n\n')), () => {
    callbacks++; entered.resolve(); return gate.promise;
  }, { signal: controller.signal, yieldToLoop: noWait }).then(
    () => { settled = true; return null; }, error => { settled = true; return error; });
  await entered.promise;
  controller.abort(reason);
  await immediate();
  assert.equal(settled, false);
  gate.resolve();
  assert.equal(await outcome, reason);
  assert.equal(callbacks, 1);
});

test('independent boundary: abort waits for an outstanding scheduler Promise to settle', async () => {
  const gate = deferred(), entered = deferred(), controller = new AbortController();
  const reason = new Error('audit-scheduler-abort');
  let settled = false, callbacks = 0;
  const outcome = consumeInSlices(source(utf8('data: checkpoint\n\ndata: unread\n\n')), () => {
    callbacks++;
  }, { signal: controller.signal, frameQuantum: 1, yieldToLoop: () => {
    entered.resolve(); return gate.promise;
  } }).then(() => { settled = true; return null; }, error => { settled = true; return error; });
  await entered.promise;
  controller.abort(reason);
  await immediate();
  assert.equal(settled, false);
  gate.resolve();
  assert.equal(await outcome, reason);
  assert.equal(callbacks, 1);
});

test('independent counterexample: mutable backing bytes can alter a later event during the first callback', async () => {
  const bytes = utf8('data: one\n\ndata: two\n\n');
  const got = [];
  await consumeInSlices(source(bytes), frame => {
    got.push(frame.data);
    if (got.length === 1) bytes.set(utf8('data: six\n\n'), 11);
  }, { sliceBytes: 11, frameQuantum: 1, yieldToLoop: noWait });
  // Passing intentionally documents the counterexample, not desired immutable-input semantics.
  assert.deepEqual(got, ['one', 'six']);
});

test('independent boundary: empty chunks do not invoke the scheduling checkpoint', async () => {
  let checkpoints = 0;
  const stats = await consumeInSlices(source(...Array.from({ length: 65 }, () => new Uint8Array())),
    () => assert.fail('No frame expected'), { yieldToLoop: async () => { checkpoints++; } });
  assert.equal(stats.receivedBytes, 0);
  assert.equal(stats.pushes, 0);
  assert.equal(checkpoints, 0);
});

test('independent boundary: over-limit suffix changes delivered prefix with parser slice size', async () => {
  const bytes = utf8('data: ok\n\ndata: excessive\n\n');
  const outcomes = [];
  for (const sliceBytes of [1, 64]) {
    const got = [];
    await assert.rejects(consumeInSlices(source(bytes), frame => got.push(frame.data), {
      sliceBytes, frameQuantum: 4,
      decoderLimits: { maxLineCharacters: 8, maxEventCharacters: 16 }, yieldToLoop: noWait,
    }), /SSE line limit/);
    outcomes.push(got);
  }
  // The existing parser only returns a slice's frames if the entire push succeeds.
  assert.deepEqual(outcomes, [['ok'], []]);
});
