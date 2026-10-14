import test from 'node:test';
import assert from 'node:assert/strict';
import { InlineBudget, PreviewPool } from './client-context.mjs';
test('UTF-8 reservation prevents concurrent over-admission and cleans up once', () => {
  const b = new InlineBudget({ owner: 'A', limit: 7 });
  const one = b.reserve('中文'); assert.equal(one.bytes, 6);
  assert.equal(b.reserve('ab'), null); assert.equal(b.used, 6);
  assert.equal(one.commit('one'), true); assert.equal(one.release(), false);
  const two = b.reserve('a'); assert.equal(b.used, 7);
  assert.equal(two.release(), true); assert.equal(two.release(), false);
  assert.equal(b.used, 6); b.remove('one'); assert.equal(b.used, 0);
});
test('changing owner rejects late completion even with the same new name', () => {
  const b = new InlineBudget({ owner: 'A', limit: 20 }); const old = b.reserve('stale');
  b.switchOwner('A'); assert.equal(old.commit('old'), false); assert.equal(old.release(), false);
  assert.equal(b.used, 0);
});
test('shared URL is revoked only after its final subscriber, with idempotent release', () => {
  const revoked = []; let sequence = 0;
  const pool = new PreviewPool(() => `blob:local-${++sequence}`, url => revoked.push(url));
  const file = {}, a = pool.acquire(file), b = pool.acquire(file), other = pool.acquire({});
  assert.equal(a.url, b.url); assert.notEqual(a.url, other.url);
  a.release(); a.release(); assert.deepEqual(revoked, []);
  b.release(); assert.deepEqual(revoked, [a.url]); other.release(); assert.equal(pool.size, 0);
});
test('UTF-8 byte budgets admit exact boundaries, including zero and astral characters', () => {
  for (const limit of [0, 1, 2, 3, 4, 6]) {
    for (const text of ['', 'a', '中', '🙂', '中文', 'a🙂']) {
      const b = new InlineBudget({ owner: 'A', limit });
      const bytes = new TextEncoder().encode(text).byteLength, reservation = b.reserve(text);
      assert.equal(Boolean(reservation), bytes <= limit);
      if (reservation) {
        assert.equal(b.used, bytes); assert.equal(reservation.commit('item'), true);
        assert.equal(b.used, bytes); assert.equal(reservation.commit('item'), false);
        b.remove('item'); assert.equal(b.used, 0);
      }
    }
  }
});
test('invalid budget configuration and duplicate commits preserve accounting', () => {
  for (const limit of [-1, 0.5, Infinity, NaN, '4']) {
    assert.throws(() => new InlineBudget({ owner: 'A', limit }), /limit/);
  }
  const b = new InlineBudget({ owner: 'A', limit: 2 });
  b.reserve('a').commit('same'); const second = b.reserve('b');
  assert.throws(() => second.commit('same'), /identity/); assert.equal(b.used, 2);
  assert.equal(second.release(), true); assert.equal(b.used, 1);
});
