import test from 'node:test';
import assert from 'node:assert/strict';
import { FakeClock, SnapshotPresenter, StableBlocks, WeightedLRU, LatestWorkerLane, runSlices, escapeHTML } from '../model.mjs';
const presenter = (options = {}) => {
  const clock = new FakeClock(), seen = [];
  const view = new SnapshotPresenter({ clock, commit: x => seen.push(x), ...options });
  return { clock, seen, view };
};
test('first snapshot is immediate; burst coalesces only complete snapshots', () => {
  const { clock, seen, view } = presenter();
  view.accept('a'); view.accept('ab'); view.accept('abc');
  assert.equal(seen.length, 1); clock.advance(24);
  assert.equal(seen.at(-1).text, 'abc'); assert.equal(view.metrics.coalesced, 1);
});
test('terminal update flushes immediately and closes ingress', () => {
  const { clock, seen, view } = presenter();
  view.accept('a'); view.accept('ab'); view.accept('abc', { terminal: true });
  clock.advance(999); assert.deepEqual(seen.map(x => x.text), ['a', 'abc']);
  assert.equal(view.accept('late'), false); assert.equal(clock.tasks.size, 0);
});
test('hidden cadence changes and return to foreground catches up', () => {
  const { clock, seen, view } = presenter();
  view.accept('a'); view.accept('b'); view.setHidden(true); clock.advance(24);
  assert.equal(seen.length, 1); view.setHidden(false); assert.equal(seen.at(-1).text, 'b');
});
test('dispose clears pending work and suppresses later updates', () => {
  const { clock, seen, view } = presenter(); view.accept('a'); view.accept('b'); view.dispose();
  clock.advance(1000); assert.equal(seen.length, 1); assert.equal(clock.tasks.size, 0);
});
test('commit may reenter presenter without dropping newer work', () => {
  const clock = new FakeClock(), seen = []; let view;
  view = new SnapshotPresenter({ clock, commit: x => { seen.push(x.text); if (x.text === 'a') view.accept('b'); } });
  view.accept('a'); clock.advance(24); assert.deepEqual(seen, ['a', 'b']);
});
test('oversize snapshot does not overwrite accepted state', () => {
  const { view, seen } = presenter({ maxChars: 2 }); view.accept('ok');
  assert.throws(() => view.accept('bad'), RangeError); assert.equal(seen.at(-1).text, 'ok');
});
test('stable block identities survive append', () => {
  const b = new StableBlocks(); const a = b.update('one\n\ntwo');
  const c = b.update('one\n\ntwo more'); assert.equal(a.blocks[0], c.blocks[0]);
  assert.equal(c.tail, 'two more');
});
test('open fence retains blank lines in active tail', () => {
  const b = new StableBlocks(); const a = b.update('```js\nconst a=1;\n\n');
  assert.equal(a.blocks.length, 0);
  const c = b.update('```js\nconst a=1;\n\n```\n\nnext');
  assert.equal(c.blocks.length, 1); assert.equal(c.tail, 'next');
});
test('incomplete fence marker is not committed prematurely', () => {
  const b = new StableBlocks(); b.update('``'); b.update('```js');
  assert.equal(b.fence, null); b.update('```js\n'); assert.equal(b.fence.count, 3);
});
test('short close and opposite fence cannot close an open fence', () => {
  const b = new StableBlocks(); b.update('````\na\n```\n~~~\n\n');
  assert.equal(b.blocks.length, 0); assert.equal(b.fence.count, 4);
});
test('non-prefix edit invalidates blocks and parser checkpoint', () => {
  const b = new StableBlocks(); const a = b.update('old\n\ntail');
  const c = b.update('new\n\ntail'); assert.notEqual(a.blocks[0], c.blocks[0]);
  assert.equal(c.blocks[0].text, 'new\n\n');
});
test('final parser receives entire document including reference definitions', () => {
  let input; const b = new StableBlocks({ finalParser: text => { input = text; return { linked: text.includes('[x]: /a') }; } });
  b.update('See [x]\n\n'); const text = 'See [x]\n\n[x]: /a';
  const final = b.update(text, { terminal: true }); assert.equal(input, text); assert.equal(final.final.linked, true);
});
test('character-by-character chunks reconstruct arbitrary Unicode exactly', () => {
  const b = new StableBlocks(); const text = '你好🙂\n\n```\nα\n```\n\nend'; let value;
  for (let i = 1; i <= text.length; i++) value = b.update(text.slice(0, i));
  assert.equal(value.blocks.map(x => x.text).join('') + value.tail, text);
  assert.equal(b.scannedChars, text.lastIndexOf('\n') + 1);
});
test('document limit is checked before mutation', () => {
  const b = new StableBlocks({ maxChars: 3 }); b.update('ok'); assert.throws(() => b.update('oops'));
  assert.equal(b.text, 'ok');
});
test('LRU promotes hits and enforces total weight', () => {
  const c = new WeightedLRU({ entries: 2, weight: 10 });
  c.put('a', 1, 4); c.put('b', 2, 4); c.get('a'); c.put('c', 3, 4);
  assert.equal(c.get('b'), undefined); assert.equal(c.used, 8);
});
test('oversize replacement preserves old cache item', () => {
  const c = new WeightedLRU({ weight: 8, itemWeight: 5 }); c.put('a', 1, 4);
  assert.equal(c.put('a', 2, 6), false); assert.equal(c.get('a'), 1);
});
test('cache validates invalid weight and clears accounting', () => {
  const c = new WeightedLRU(); assert.throws(() => c.put('bad', 1, NaN));
  c.put('a', 1, 3); c.clear(); assert.equal(c.used, 0); assert.equal(c.items.size, 0);
});
function lane(options = {}) {
  const sent = [], results = [], fallbacks = [], cancelled = [];
  const worker = new LatestWorkerLane({ send: x => sent.push(x), publish: x => results.push(x), fallback: (...x) => fallbacks.push(x), cancel: x => cancelled.push(x), ...options });
  return { worker, sent, results, fallbacks, cancelled };
}
test('worker lane retains one in-flight and latest request only', () => {
  const { worker, sent, results } = lane(); worker.submit('a'); worker.submit('ab'); worker.submit('abc');
  assert.equal(sent.length, 1); worker.reply(sent[0], 'stale formatting'); assert.equal(results.length, 0);
  assert.equal(sent[1].text, 'abc'); worker.reply(sent[1], 'final formatting'); assert.deepEqual(results, ['final formatting']);
});
test('epoch discards old replies after reset', () => {
  const { worker, sent, results } = lane(); worker.submit('a'); worker.reset(); worker.submit('new');
  assert.equal(worker.reply(sent[0], 'old'), false); worker.reply(sent[1], 'new'); assert.deepEqual(results, ['new']);
});
test('worker failure exposes newest source as plain fallback', () => {
  const { worker, sent, fallbacks } = lane(); worker.submit('a'); worker.submit('newest'); worker.fail(sent[0], 'timeout');
  assert.deepEqual(fallbacks, [['newest', 'timeout']]); assert.equal(worker.busy, null);
});
test('oversize job cancels old computation and remains displayable', () => {
  const { worker, sent, fallbacks, cancelled } = lane({ maxChars: 2 }); worker.submit('a');
  assert.equal(worker.submit('long'), false); assert.equal(cancelled.length, 1);
  assert.deepEqual(fallbacks[0], ['long', 'oversize']); assert.equal(worker.reply(sent[0], 'old'), false);
});
test('dispose prevents queued callbacks and releases owned job', () => {
  const { worker, sent, results } = lane(); worker.submit('a'); worker.dispose();
  assert.equal(worker.reply(sent[0], 'late'), false); assert.equal(worker.submit('b'), false); assert.equal(results.length, 0);
});
test('synchronous worker-send failure falls back without recursive retry', () => {
  const { worker, fallbacks } = lane({ send: () => { throw Error('closed port'); } }); worker.submit('a');
  assert.deepEqual(fallbacks, [['a', 'send-failed']]); assert.equal(worker.busy, null);
});
test('work slicing yields at cooperative checkpoints', async () => {
  let now = 0, turns = 0;
  const result = await runSlices([1, 2, 3, 4], { visit: () => { now += 2; }, now: () => now, yieldTask: async () => { turns++; }, budget: 4 });
  assert.deepEqual(result, { visited: 4, yields: 2 }); assert.equal(turns, 2);
});
test('cancellation inside visit stops before next unit', async () => {
  const abort = new AbortController(), seen = [];
  await assert.rejects(runSlices([1, 2], { visit: x => { seen.push(x); abort.abort(); }, now: () => 0, yieldTask: async () => {}, signal: abort.signal }), { name: 'AbortError' });
  assert.deepEqual(seen, [1]);
});
test('one expensive unit can exceed cooperative budget', async () => {
  let now = 0, atYield;
  await runSlices([1], { visit: () => { now = 80; }, now: () => now, yieldTask: async () => { atYield = now; }, budget: 4 });
  assert.equal(atYield, 80);
});
test('fallback escapes active markup', () => {
  assert.equal(escapeHTML('<img onerror="x"> &'), '&lt;img onerror=&quot;x&quot;&gt; &amp;');
});
