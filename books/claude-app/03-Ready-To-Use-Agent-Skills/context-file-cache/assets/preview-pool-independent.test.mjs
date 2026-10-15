import test from 'node:test';
import assert from 'node:assert/strict';
import { PreviewPool } from './client-context.mjs';

test('API remains synchronous, frozen handles share a single lifetime', () => {
  const events = [], file = {};
  const pool = new PreviewPool(f => { assert.equal(f, file); events.push('create'); return 'blob:1'; }, u => events.push(`revoke:${u}`));
  const a = pool.acquire(file), b = pool.acquire(file);
  assert.equal(Object.isFrozen(a), true); assert.equal(a.then, undefined);
  assert.deepEqual(events, ['create']); assert.equal(pool.size, 1);
  assert.equal(a.release(), true); assert.equal(a.release(), false);
  assert.equal(b.release(), true); assert.equal(b.release(), false);
  assert.deepEqual(events, ['create', 'revoke:blob:1']); assert.equal(pool.size, 0);
});

test('caught same-file creation reentry neither invokes create again nor poisons future lifetimes', () => {
  const file = {}, revoked = []; let creates = 0;
  const pool = new PreviewPool(() => {
    assert.equal(pool.size, 0); ++creates;
    assert.throws(() => pool.acquire(file), /Reentrant acquisition/);
    return `blob:${creates}`;
  }, u => revoked.push(u));
  for (let i = 1; i <= 3; i++) {
    const h = pool.acquire(file); assert.equal(h.url, `blob:${i}`);
    assert.equal(h.release(), true); assert.equal(pool.size, 0);
  }
  assert.equal(creates, 3); assert.deepEqual(revoked, ['blob:1', 'blob:2', 'blob:3']);
});

test('cross-file A to B to A cycle throws but clears both markers and preserves unrelated entry', () => {
  const a = {}, b = {}, c = {}; let cycle = true; const revoked = [];
  const pool = new PreviewPool(f => {
    if (cycle && f === a) return pool.acquire(b).url;
    if (cycle && f === b) return pool.acquire(a).url;
    return f === a ? 'blob:a' : f === b ? 'blob:b' : 'blob:c';
  }, u => revoked.push(u));
  const hc = pool.acquire(c);
  assert.throws(() => pool.acquire(a), /Reentrant acquisition/);
  assert.equal(pool.size, 1); const peerC = pool.acquire(c); assert.equal(peerC.url, hc.url);
  cycle = false; const ha = pool.acquire(a), hb = pool.acquire(b); assert.equal(pool.size, 3);
  hc.release(); peerC.release(); ha.release(); hb.release(); assert.equal(pool.size, 0);
  assert.deepEqual(revoked, ['blob:c', 'blob:a', 'blob:b']);
});

test('create throw keeps nested independent handle and retries both call and getter failures', () => {
  const a = {}, b = {}; const fail = new Error('create failure'); let inner, throwCreate = true;
  const pool = new PreviewPool(f => {
    if (f === a && throwCreate) { inner = pool.acquire(b); throw fail; }
    return f === a ? 'blob:a' : 'blob:b';
  }, () => {});
  assert.throws(() => pool.acquire(a), e => e === fail); assert.equal(pool.size, 1);
  const originalCreate = pool.createURL;
  Object.defineProperty(pool, 'createURL', { configurable: true, get() { throw fail; } });
  assert.throws(() => pool.acquire(a), e => e === fail); assert.equal(pool.size, 1);
  Object.defineProperty(pool, 'createURL', { configurable: true, writable: true, value: originalCreate });
  throwCreate = false; const outer = pool.acquire(a); assert.equal(pool.size, 2);
  inner.release(); outer.release(); assert.equal(pool.size, 0);
});

test('revoke can release old handles, acquire same-file replacement, then throw without corrupting replacement', () => {
  const file = {}, fail = new Error('revoke failure'); let seq = 0, old, peer, next;
  const revoked = [];
  const pool = new PreviewPool(() => `blob:${++seq}`, u => {
    revoked.push(u);
    if (u === 'blob:1') {
      assert.equal(pool.size, 0); assert.equal(old.release(), false); assert.equal(peer.release(), false);
      next = pool.acquire(file); assert.equal(pool.size, 1); throw fail;
    }
  });
  old = pool.acquire(file); peer = pool.acquire(file);
  assert.equal(old.release(), true); assert.throws(() => peer.release(), e => e === fail);
  assert.equal(peer.release(), false); assert.equal(pool.size, 1);
  const nextPeer = pool.acquire(file); assert.equal(nextPeer.url, next.url); assert.equal(seq, 2);
  next.release(); assert.equal(pool.size, 1); nextPeer.release(); assert.equal(pool.size, 0);
  assert.deepEqual(revoked, ['blob:1', 'blob:2']);
});

test('revoke can create and release nested replacement in-stack', () => {
  const file = {}; let seq = 0; const revoked = [];
  const pool = new PreviewPool(() => `blob:${++seq}`, u => {
    revoked.push(u);
    if (u === 'blob:1') { const inner = pool.acquire(file); inner.release(); assert.equal(inner.release(), false); }
  });
  const h = pool.acquire(file); assert.equal(h.release(), true); assert.equal(pool.size, 0);
  assert.deepEqual(revoked, ['blob:1', 'blob:2']);
});

test('throwing revoke is attempted once and preserves exact exception', () => {
  const failure = Object.freeze({ kind: 'synthetic-revoke-error' }); let calls = 0;
  const pool = new PreviewPool(() => 'blob:x', () => { ++calls; throw failure; });
  const h = pool.acquire({}); assert.throws(() => h.release(), e => e === failure);
  assert.equal(pool.size, 0); assert.equal(h.release(), false); assert.equal(calls, 1);
});

test('Promise create result is not validated: synchronous URL contract is an adapter precondition', () => {
  const promise = Promise.resolve('blob:async'); let revoked;
  const pool = new PreviewPool(() => promise, u => { revoked = u; });
  const h = pool.acquire({}); assert.equal(h.url, promise); h.release(); assert.equal(revoked, promise);
});
