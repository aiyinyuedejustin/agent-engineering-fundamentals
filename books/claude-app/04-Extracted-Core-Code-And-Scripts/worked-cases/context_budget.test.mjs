import test from 'node:test';
import assert from 'node:assert/strict';
import {DraftOwner, InlineBudget, utf8Bytes} from './context_budget.mjs';

test('UTF-8 byte counts differ from JS string lengths', () => {
  assert.deepEqual(['ok', '资料', '😀'].map(utf8Bytes), [2, 6, 4]);
  assert.deepEqual(['ok', '资料', '😀'].map(x => x.length), [2, 2, 2]);
});
test('a reservation prevents a second asynchronous admission', () => {
  const b = new InlineBudget(12); b.reserve('seed', 'ok').commit();
  assert.ok(b.reserve('a', '资料'));
  assert.equal(b.reserve('b', '图像'), null);
  assert.deepEqual([b.used, b.reserved], [2, 6]);
});
test('cancel releases budget exactly once', () => {
  const b = new InlineBudget(6); const ticket = b.reserve('a', '资料');
  assert.equal(ticket.release(), true); assert.equal(ticket.release(), false);
  assert.deepEqual([b.used, b.reserved], [0, 0]);
});
test('commit transfers ownership, rather than counting twice', () => {
  const b = new InlineBudget(6); const t = b.reserve('a', '资料');
  assert.equal(t.commit(), true); assert.equal(t.commit(), false);
  assert.equal(t.release(), false); assert.deepEqual([b.used, b.reserved], [6, 0]);
});
test('duplicate identities cannot overwrite a reservation', () => {
  const b = new InlineBudget(20); b.reserve('a', '资料');
  assert.throws(() => b.reserve('a', 'different'), /duplicate/);
});
test('exact byte limit is admitted', () => {
  const b = new InlineBudget(6); assert.ok(b.reserve('a', '资料'));
  assert.equal(b.reserve('b', 'x'), null);
});
test('cancellation allows a later input to take the freed slot', () => {
  const d = new DraftOwner('a', 12); d.begin('seed', 'ok').complete();
  const a = d.begin('a', '资料'); assert.equal(d.begin('b', '图像').route, 'file-or-reject');
  a.cancel(); assert.equal(d.begin('b', '图像').complete(), true);
  assert.deepEqual([d.budget.used, d.budget.reserved], [8, 0]);
});
test('navigation releases pending budget and rejects a late completion', () => {
  const oldDraft = new DraftOwner('old', 12); const t = oldDraft.begin('a', '资料');
  oldDraft.invalidate(); const newDraft = new DraftOwner('new', 12);
  assert.equal(t.complete(), false);
  assert.deepEqual([oldDraft.budget.reserved, newDraft.ready.size], [0, 0]);
});
test('invalidation does not delete already committed old-draft data', () => {
  const d = new DraftOwner('old', 12); d.begin('a', '资料').complete(); d.invalidate();
  assert.equal(d.ready.get('a'), '资料'); assert.equal(d.budget.used, 6);
});
test('cancelled input cannot come back from a replayed callback', () => {
  const d = new DraftOwner('a', 12); const t = d.begin('a', '资料'); t.cancel();
  assert.equal(t.complete(), false); assert.equal(d.ready.size, 0);
});
test('removal of committed data has its own explicit transition', () => {
  const b = new InlineBudget(6); b.reserve('a', '资料').commit();
  assert.equal(b.remove('a'), true); assert.equal(b.remove('a'), false); assert.equal(b.used, 0);
});
