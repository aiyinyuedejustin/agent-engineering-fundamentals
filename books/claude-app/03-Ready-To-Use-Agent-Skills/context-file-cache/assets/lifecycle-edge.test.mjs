import test from 'node:test';
import assert from 'node:assert/strict';
import { InlineBudget, PreviewPool } from './client-context.mjs';
test('byte budget configuration is read-only for its owner lifetime', () => {
  const budget = new InlineBudget({ owner: 'synthetic', limit: 1 });
  assert.throws(() => { budget.limit = NaN; }, TypeError);
  assert.equal(budget.limit, 1); assert.equal(budget.reserve('xx'), null);
  assert.equal(budget.reserve('x').bytes, 1);
});
test('last subscriber release invalidates the old URL before revocation reentry', () => {
  const file = {}; let next = 0, nested; const revoked = [];
  const pool = new PreviewPool(() => `blob:synthetic-${++next}`, url => {
    revoked.push(url); if (revoked.length === 1) nested = pool.acquire(file);
  });
  const original = pool.acquire(file);
  assert.equal(original.release(), true);
  assert.notEqual(nested.url, original.url); assert.equal(pool.size, 1);
  const peer = pool.acquire(file); assert.equal(peer.url, nested.url);
  assert.equal(original.release(), false); nested.release(); assert.equal(revoked.length, 1);
  peer.release(); assert.equal(pool.size, 0); assert.deepEqual(revoked, [original.url, nested.url]);
});
test('revocation failure is reported without retaining or reusing the failed URL', () => {
  const file = {}; let next = 0, calls = 0;
  const failure = new Error('synthetic revoke failure');
  const pool = new PreviewPool(() => `blob:synthetic-${++next}`, () => { calls++; throw failure; });
  const original = pool.acquire(file); assert.throws(() => original.release(), error => error === failure);
  assert.equal(pool.size, 0); assert.equal(original.release(), false); assert.equal(calls, 1);
  const fresh = pool.acquire(file); assert.notEqual(fresh.url, original.url); assert.equal(pool.size, 1);
  assert.throws(() => fresh.release(), error => error === failure); assert.equal(pool.size, 0);
});
