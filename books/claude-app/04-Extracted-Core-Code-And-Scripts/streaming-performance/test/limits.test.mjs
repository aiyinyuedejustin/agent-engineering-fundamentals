// Synthetic regressions; only original teaching models execute.
import test from 'node:test';
import assert from 'node:assert/strict';
import { FakeClock, SnapshotPresenter, StableBlocks, LatestWorkerLane, WeightedLRU, runSlices } from '../model.mjs';
const presenter = options => new SnapshotPresenter({ clock: new FakeClock(), commit() {}, ...options });
const lane = options => new LatestWorkerLane({ send() {}, publish() {}, fallback() {}, ...options });
test('character caps reject invalid configuration instead of silently disabling admission', () => {
  for (const maxChars of [NaN, Infinity, -Infinity, -1, 0.5, '10', null, Number.MAX_SAFE_INTEGER + 1]) {
    for (const create of [presenter, options => new StableBlocks(options), lane]) {
      assert.throws(() => create({ maxChars }), RangeError);
    }
  }
});
test('character caps are fixed after construction and enforce exact UTF-16 boundaries', () => {
  for (const create of [presenter, options => new StableBlocks(options), lane]) {
    const item = create({ maxChars: 2 });
    assert.throws(() => { item.maxChars = NaN; }, TypeError);
    assert.throws(() => { Object.defineProperty(item, 'maxChars', { value: Infinity }); }, TypeError);
    assert.equal(item.maxChars, 2);
  }
  const p = presenter({ maxChars: 2 }); assert.equal(p.accept('🙂'), true);
  assert.throws(() => p.accept('🙂x'), RangeError);
  const b = new StableBlocks({ maxChars: 2 }); assert.equal(b.update('🙂').tail, '🙂');
  assert.throws(() => b.update('🙂x'), RangeError);
});
test('zero character caps allow empty text and reject nonempty text', () => {
  const p = presenter({ maxChars: 0 }); assert.equal(p.accept(''), true); assert.throws(() => p.accept('a'), RangeError);
  const b = new StableBlocks({ maxChars: 0 }); assert.equal(b.update('').tail, ''); assert.throws(() => b.update('a'), RangeError);
  const sent = [], plain = [];
  const w = lane({ maxChars: 0, send: x => sent.push(x), fallback: x => plain.push(x) });
  assert.equal(w.submit(''), true); assert.equal(w.submit('a'), false);
  assert.equal(sent.length, 1); assert.deepEqual(plain, ['a']);
});
test('presenter delays reject NaN and overflow and remain fixed', () => {
  for (const key of ['visibleDelay', 'hiddenDelay']) {
    for (const value of [NaN, Infinity, -1, '24', null, 2_147_483_648]) {
      assert.throws(() => presenter({ [key]: value }), RangeError);
    }
    for (const value of [0, 0.5, 2_147_483_647]) assert.doesNotThrow(() => presenter({ [key]: value }));
    const p = presenter({ [key]: 0 }); assert.throws(() => { p[key] = NaN; }, TypeError);
  }
});
test('cache count is an integer and fixed caps preserve weighted accounting', () => {
  for (const entries of [NaN, Infinity, -1, 0.5, '1', null, Number.MAX_SAFE_INTEGER + 1]) {
    assert.throws(() => new WeightedLRU({ entries }), RangeError);
  }
  const c = new WeightedLRU({ entries: 1, weight: 0.5, itemWeight: 0.25 });
  for (const key of ['entries', 'weight', 'itemWeight']) assert.throws(() => { c[key] = NaN; }, TypeError);
  assert.equal(c.put('a', 1, 0.25), true); assert.equal(c.put('b', 2, 0.25), true);
  assert.equal(c.get('a'), undefined); assert.equal(c.used, 0.25);
});
test('cooperative work budget must be a finite positive number', async () => {
  for (const budget of [NaN, Infinity, -Infinity, 0, -1, '4', null]) {
    let visited = 0;
    await assert.rejects(runSlices([1], { visit: () => visited++, now: () => 0, yieldTask: async () => {}, budget }), RangeError);
    assert.equal(visited, 0);
  }
  assert.deepEqual(await runSlices([1], { visit() {}, now: () => 0, yieldTask: async () => {}, budget: 0.5 }), { visited: 1, yields: 0 });
});
