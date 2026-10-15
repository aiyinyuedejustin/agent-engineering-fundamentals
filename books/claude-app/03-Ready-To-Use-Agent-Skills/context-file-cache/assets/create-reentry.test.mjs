import test from 'node:test';
import assert from 'node:assert/strict';
import { PreviewPool } from './client-context.mjs';

test('same object create reentry is rejected without corrupting outer acquisition', () => {
  const file = {}; let calls = 0; const revoked = [];
  const pool = new PreviewPool(() => {
    calls++;
    assert.throws(() => pool.acquire(file), /Reentrant acquisition/);
    assert.equal(pool.size, 0);
    return 'blob:synthetic';
  }, url => revoked.push(url));
  const outer = pool.acquire(file), peer = pool.acquire(file);
  assert.equal(calls, 1); assert.equal(outer.url, peer.url); assert.equal(pool.size, 1);
  assert.equal(outer.release(), true); assert.equal(outer.release(), false);
  assert.deepEqual(revoked, []); assert.equal(pool.size, 1);
  peer.release(); assert.equal(pool.size, 0); assert.deepEqual(revoked, ['blob:synthetic']);
});

test('uncaught same object reentry clears creation marker and permits a retry', () => {
  const file = {}; let recursive = true;
  const pool = new PreviewPool(() => {
    if (recursive) return pool.acquire(file).url;
    return 'blob:retry';
  }, () => {});
  assert.throws(() => pool.acquire(file), /Reentrant acquisition/);
  assert.equal(pool.size, 0); recursive = false;
  const retried = pool.acquire(file); assert.equal(pool.size, 1);
  retried.release(); assert.equal(pool.size, 0);
});

test('different object create reentry is allowed and independent', () => {
  const a = {}, b = {}; let inner; const revoked = [];
  const pool = new PreviewPool(file => {
    if (file === a) { inner = pool.acquire(b); return 'blob:a'; }
    return 'blob:b';
  }, url => revoked.push(url));
  const outer = pool.acquire(a); assert.equal(pool.size, 2);
  inner.release(); assert.equal(pool.size, 1); assert.deepEqual(revoked, ['blob:b']);
  outer.release(); assert.equal(pool.size, 0); assert.deepEqual(revoked, ['blob:b', 'blob:a']);
});

test('create exception clears marker while preserving another created object', () => {
  const a = {}, b = {}; let inner, fail = true;
  const error = new Error('synthetic create failure');
  const pool = new PreviewPool(file => {
    if (file === a && fail) { inner = pool.acquire(b); throw error; }
    return file === a ? 'blob:a' : 'blob:b';
  }, () => {});
  assert.throws(() => pool.acquire(a), value => value === error);
  assert.equal(pool.size, 1); fail = false;
  const retry = pool.acquire(a); assert.equal(pool.size, 2);
  inner.release(); retry.release(); assert.equal(pool.size, 0);
});

test('revoke reentry and repeated old release preserve replacement entry', () => {
  const file = {}; let created = 0, replacement; const revoked = [];
  const pool = new PreviewPool(() => `blob:${++created}`, url => {
    revoked.push(url);
    if (url === 'blob:1') replacement = pool.acquire(file);
  });
  const old = pool.acquire(file); old.release();
  assert.equal(pool.size, 1); assert.equal(old.release(), false);
  const peer = pool.acquire(file); assert.equal(peer.url, replacement.url);
  replacement.release(); assert.equal(pool.size, 1); peer.release();
  assert.equal(pool.size, 0); assert.deepEqual(revoked, ['blob:1', 'blob:2']);
});
