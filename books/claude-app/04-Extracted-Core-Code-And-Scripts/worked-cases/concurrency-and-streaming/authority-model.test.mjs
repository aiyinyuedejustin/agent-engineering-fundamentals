import test from 'node:test';
import assert from 'node:assert/strict';
import { VersionedSettings, rebaseDisjoint } from './authority-model.mjs';
import { ScopedMutationQueue } from './existing-models.mjs';

const initial = () => ({ enabled: true, label: 'original' });
const write = (operationId, expectedRevision, value) => ({ operationId, expectedRevision, value });

test('two correct local queues cannot prevent a stale whole-object overwrite', async () => {
  let resource = initial();
  const left = { ...resource }, right = { ...resource };
  const a = new ScopedMutationQueue(), b = new ScopedMutationQueue();
  await a.run('resource', () => { resource = { ...left, enabled: false }; });
  await b.run('resource', () => { resource = { ...right, label: 'renamed' }; });
  assert.deepEqual(resource, { enabled: true, label: 'renamed' });
});

test('the authority rejects the second writer based on the same old revision', () => {
  const s = new VersionedSettings(initial(), 7);
  assert.equal(s.submit(write('A', 7, { ...initial(), enabled: false })).kind, 'committed');
  const conflict = s.submit(write('B', 7, { ...initial(), label: 'renamed' }));
  assert.equal(conflict.kind, 'conflict');
  assert.deepEqual(s.read(), { revision: 8, value: { enabled: false, label: 'original' } });
  assert.equal(s.commits, 1);
});

test('changing only operation identity does not solve a revision conflict', () => {
  const s = new VersionedSettings(initial(), 7);
  s.submit(write('A', 7, { ...initial(), enabled: false }));
  assert.equal(s.submit(write('B-new-id', 7, initial())).kind, 'conflict');
  assert.equal(s.commits, 1);
});

test('conflict-free field intent rebases without restoring stale unrelated fields', () => {
  const s = new VersionedSettings(initial(), 7), base = s.read();
  s.submit(write('A', 7, { ...initial(), enabled: false }));
  const now = s.read();
  const p = rebaseDisjoint(base.value, now.value, { label: 'renamed' });
  assert.equal(p.kind, 'proposed');
  s.submit(write('B-rebased', now.revision, p.value));
  assert.deepEqual(s.read(), { revision: 9, value: { enabled: false, label: 'renamed' } });
});

test('same-field conflict is preserved for an explicit decision', () => {
  const p = rebaseDisjoint(initial(), { ...initial(), label: 'other-editor' }, { label: 'mine' });
  assert.deepEqual(p, { kind: 'conflict', fields: ['label'] });
});

test('a successful response can be lost and replayed without another commit', () => {
  const s = new VersionedSettings(initial(), 7), q = write('A', 7, { ...initial(), enabled: false });
  s.submit(q); // Simulated lost reply: caller discards this receipt.
  const r = s.submit(q);
  assert.equal(r.kind, 'committed');
  assert.equal(r.replayed, true);
  assert.equal(r.snapshot.revision, 8);
  assert.equal(s.commits, 1);
});

test('dedup lookup precedes revision validation for an already committed operation', () => {
  const s = new VersionedSettings(initial(), 7), q = write('A', 7, { ...initial(), enabled: false });
  s.submit(q);
  s.submit(write('B', 8, { enabled: false, label: 'renamed' }));
  const r = s.submit(q);
  assert.equal(r.kind, 'committed');
  assert.equal(r.snapshot.revision, 8); // Receipt, NOT latest resource state.
  assert.equal(s.read().revision, 9);
  assert.equal(s.commits, 2);
});

test('an operation identity cannot be reused with a different proposal', () => {
  const s = new VersionedSettings(initial(), 7);
  s.submit(write('A', 7, initial()));
  assert.throws(() => s.submit(write('A', 7, { ...initial(), label: 'changed' })), /OPERATION_ID_REUSED/);
  assert.equal(s.commits, 1);
});

test('rebasing changes the precondition and needs a new operation identity', () => {
  const s = new VersionedSettings(initial(), 7);
  s.submit(write('A', 7, { ...initial(), enabled: false }));
  s.submit(write('B', 7, { ...initial(), label: 'renamed' }));
  assert.throws(() => s.submit(write('B', 8, { enabled: false, label: 'renamed' })), /OPERATION_ID_REUSED/);
});

test('read snapshots, returned receipts, and input objects do not alias state', () => {
  const input = initial(), s = new VersionedSettings(input, 7);
  input.label = 'mutated';
  const q = write('A', 7, initial()), receipt = s.submit(q);
  q.value.label = 'mutated again';
  receipt.snapshot.value.label = 'mutated receipt';
  const read = s.read(); read.value.label = 'mutated read';
  assert.equal(s.read().value.label, 'original');
  assert.equal(s.submit(write('A', 7, initial())).snapshot.value.label, 'original');
});

test('malformed revision, identifier, or record is rejected without a commit', () => {
  const s = new VersionedSettings(initial(), 7);
  for (const rev of [-1, NaN, Infinity, 7.5, '7', true])
    assert.throws(() => s.submit(write('A', rev, initial())), TypeError);
  assert.throws(() => s.submit(write('', 7, initial())), TypeError);
  assert.throws(() => s.submit(write('A', 7, { enabled: 1, label: 'x' })), TypeError);
  assert.throws(() => s.submit(write('A', 7, { ...initial(), extra: true })), TypeError);
  assert.equal(s.commits, 0);
});

test('record getters are rejected without invoking them', () => {
  const s = new VersionedSettings(initial(), 7);
  let calls = 0;
  const value = { get enabled() { calls++; return true; }, label: 'x' };
  assert.throws(() => s.submit(write('A', 7, value)), TypeError);
  assert.equal(calls, 0);
});

test('revision exhaustion is explicit and leaves the old state intact', () => {
  const s = new VersionedSettings(initial(), Number.MAX_SAFE_INTEGER);
  assert.throws(() => s.submit(write('A', Number.MAX_SAFE_INTEGER, initial())), /REVISION_EXHAUSTED/);
  assert.equal(s.commits, 0);
  assert.equal(s.read().revision, Number.MAX_SAFE_INTEGER);
});

test('replaying an old conflict receipt is not a new read', () => {
  const s = new VersionedSettings(initial(), 7);
  s.submit(write('A', 7, initial()));
  const q = write('conflict', 7, initial()); s.submit(q);
  s.submit(write('B', 8, { ...initial(), label: 'newer' }));
  assert.equal(s.submit(q).snapshot.revision, 8);
  assert.equal(s.read().revision, 9);
});
