import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareCanonicalPair, makeTreeFixture, canonicalPair, snapshotTree, ROOT, ConversationBranches } from './tree-rekey.mjs';
import { ScopedMutationQueue, applyQueuedOptimistic, ScopedAccessView, deferred, turn } from './settings-access.mjs';

const noChange = (tree, action, pattern) => {
  const before = snapshotTree(tree), refs = [tree.messageByUuid, tree.parentByChildUuid, tree.childrenByParentUuid, tree.selectedChildByUuid];
  assert.throws(action, pattern);
  assert.deepEqual(snapshotTree(tree), before);
  [tree.messageByUuid, tree.parentByChildUuid, tree.childrenByParentUuid, tree.selectedChildByUuid].forEach((ref, i) => assert.strictEqual(ref, refs[i]));
};

test('A01 all four indices, leaf and visible projection use canonical IDs; old object is unchanged', () => {
  const tree = makeTreeFixture(), before = snapshotTree(tree);
  const next = prepareCanonicalPair(tree, canonicalPair);
  assert.deepEqual(snapshotTree(tree), before);
  assert.deepEqual([...next.messageByUuid.keys()], ['h0', 'a0', 'h-old', 'a-old', 'h1', 'a1']);
  assert.equal(next.messageByUuid.get('a1').parent_message_uuid, 'h1');
  assert.equal(next.parentByChildUuid.get('a1'), 'h1');
  assert.deepEqual(next.childrenByParentUuid.get('a0'), ['h-old', 'h1']);
  assert.deepEqual(next.childrenByParentUuid.get('h1'), ['a1']);
  assert.equal(next.selectedChildByUuid.get('a0'), 1);
  assert.equal(next.selectedChildByUuid.get('h1'), 0);
  assert.equal(next.currentLeaf, 'a1');
  assert.equal(JSON.stringify(snapshotTree(next)).includes('opt:'), false);
  assert.deepEqual(next.danglingHumanMessages, tree.danglingHumanMessages);
  assert.deepEqual(next.visiblePath().map(m => m.uuid), ['h0', 'a0', 'h1', 'a1']);
});
test('A02 replacement on a hidden branch preserves selected path and remembered branch positions', () => {
  const next = prepareCanonicalPair(makeTreeFixture({ selected: 'a-old' }), canonicalPair);
  assert.deepEqual(next.visiblePath().map(m => m.uuid), ['h0', 'a0', 'h-old', 'a-old']);
  next.switchSibling('h-old', 1);
  assert.deepEqual(next.visiblePath().map(m => m.uuid), ['h0', 'a0', 'h1', 'a1']);
});
test('A03 collision with an indexed or filtered dangling identity is rejected before publication', () => {
  for (const canonicalAssistant of ['a-old', 'h-wait']) {
    const tree = makeTreeFixture();
    noChange(tree, () => prepareCanonicalPair(tree, { ...canonicalPair, canonicalAssistant }), /occupied/);
  }
});
test('A04 reserved, equal, temporary and empty canonical IDs are atomically rejected', () => {
  for (const patch of [{ canonicalHuman: ROOT }, { canonicalHuman: 'a1' }, { canonicalAssistant: '' }, { canonicalHuman: 'opt:new' }]) {
    const tree = makeTreeFixture();
    noChange(tree, () => prepareCanonicalPair(tree, { ...canonicalPair, ...patch }), /Canonical/);
  }
});
test('A05 wrong human, missing optimistic node and sender mismatch do not produce a partial rename', () => {
  for (const patch of [{ optimisticHuman: 'h-old' }, { optimisticAssistant: 'absent' }, { optimisticAssistant: 'opt:h1' }]) {
    const tree = makeTreeFixture();
    noChange(tree, () => prepareCanonicalPair(tree, { ...canonicalPair, ...patch }), /Optimistic|optimistic|parent/);
  }
  const tree = makeTreeFixture();
  tree.append([{ uuid: 'opt:other', sender: 'human', parent_message_uuid: 'a0', content: [] }]);
  noChange(tree, () => prepareCanonicalPair(tree, { ...canonicalPair, optimisticHuman: 'opt:other' }), /parent mismatch/);
});
test('A06 an indexed descendant prevents the narrow fast path', () => {
  const tree = makeTreeFixture();
  tree.append([{ uuid: 'child', sender: 'human', parent_message_uuid: 'opt:a1', content: [] }]);
  noChange(tree, () => prepareCanonicalPair(tree, canonicalPair), /descendants/);
});
test('A07 a filtered dangling descendant also prevents the fast path', () => {
  const base = makeTreeFixture();
  const tree = new ConversationBranches([...base.messageByUuid.values(), { uuid: 'wait-child', sender: 'human', parent_message_uuid: 'opt:a1' }], { currentLeaf: 'opt:a1' });
  assert.equal(tree.childrenByParentUuid.has('opt:a1'), false);
  noChange(tree, () => prepareCanonicalPair(tree, canonicalPair), /descendants/);
});
test('A08 uncloneable payload rejects preparation and leaves all original Map references intact', () => {
  const tree = makeTreeFixture(), before = snapshotTree(tree), originalRefs = [tree.messageByUuid, tree.parentByChildUuid, tree.childrenByParentUuid, tree.selectedChildByUuid];
  const uncloneable = () => {};
  tree.messageByUuid.get('opt:a1').bad = uncloneable;
  assert.throws(() => prepareCanonicalPair(tree, canonicalPair), { name: 'DataCloneError' });
  [tree.messageByUuid, tree.parentByChildUuid, tree.childrenByParentUuid, tree.selectedChildByUuid].forEach((ref, i) => assert.strictEqual(ref, originalRefs[i]));
  assert.equal(tree.messageByUuid.has('h1'), false); assert.equal(tree.currentLeaf, 'opt:a1');
  assert.strictEqual(tree.messageByUuid.get('opt:a1').bad, uncloneable);
  delete tree.messageByUuid.get('opt:a1').bad; // Remove only the test's injected function to compare every state field.
  assert.deepEqual(snapshotTree(tree), before);
});
test('A09 inconsistent public indices are rejected, not silently repaired', () => {
  const tree = makeTreeFixture(); tree.parentByChildUuid.set('opt:a1', 'h-old');
  assert.throws(() => prepareCanonicalPair(tree, canonicalPair), /disagreement/);
  assert.equal(tree.parentByChildUuid.get('opt:a1'), 'h-old'); assert.equal(tree.messageByUuid.has('h1'), false);
});
test('A10 replaying the same replacement is rejected; no implicit merge/idempotency claim', () => {
  const next = prepareCanonicalPair(makeTreeFixture(), canonicalPair);
  noChange(next, () => prepareCanonicalPair(next, canonicalPair), /pair missing/);
});
test('B01 two queued edits: first rollback is the second baseline; success is authoritative', async () => {
  const q = new ScopedMutationQueue(), cache = new Map([['a', { enabled: false, mode: 'summary', revision: 7 }]]), hold = deferred();
  const first = applyQueuedOptimistic(q, 'a', cache, { enabled: true }, () => hold.promise);
  const observed = assert.rejects(first, /offline/);
  let secondStarted = false;
  const second = applyQueuedOptimistic(q, 'a', cache, { mode: 'topics' }, async () => {
    secondStarted = true;
    assert.deepEqual(cache.get('a'), { enabled: false, mode: 'topics', revision: 7 });
    return { enabled: false, mode: 'topics', revision: 8 };
  });
  await turn(); assert.equal(secondStarted, false); assert.equal(cache.get('a').enabled, true);
  hold.reject(new Error('offline')); await observed; await second; await turn();
  assert.deepEqual(cache.get('a'), { enabled: false, mode: 'topics', revision: 8 }); assert.equal(q.pendingScopes, 0);
});
test('B02 two failures each restore their own start baseline, then queue remains usable', async () => {
  const q = new ScopedMutationQueue(), original = { enabled: false, mode: 'summary' }, cache = new Map([['a', original]]);
  const jobs = [{ enabled: true }, { mode: 'topics' }].map(p => applyQueuedOptimistic(q, 'a', cache, p, async () => { throw new Error('fail'); }));
  assert.deepEqual((await Promise.allSettled(jobs)).map(x => x.status), ['rejected', 'rejected']);
  assert.deepEqual(cache.get('a'), original); assert.equal(await q.run('a', () => 'alive'), 'alive');
});
test('B03 another scope proceeds while A waits and cannot be rolled back by A', async () => {
  const q = new ScopedMutationQueue(), cache = new Map(), hold = deferred();
  const a = applyQueuedOptimistic(q, 'a', cache, { enabled: true }, () => hold.promise);
  const observed = assert.rejects(a, /fail/);
  await applyQueuedOptimistic(q, 'b', cache, { enabled: false }, async () => ({ enabled: false, revision: 1 }));
  hold.reject(new Error('fail')); await observed;
  assert.equal(cache.has('a'), false); assert.deepEqual(cache.get('b'), { enabled: false, revision: 1 });
});
test('B04 A stale allow arriving after B deny cannot update view or start the original action', async () => {
  const view = new ScopedAccessView('a', { org: 'a', checkedAt: 0, allowed: true }), late = deferred();
  const action = view.mayStartAction(1000, 100, () => late.promise);
  view.switchOrg('b'); const b = view.beginRead();
  view.receive(b, { org: 'b', clientGate: true, serverStatus: 'blocked_by_org_admin', userEnabled: true }, 1001);
  const before = structuredClone(view.snapshot);
  late.resolve({ org: 'a', clientGate: true, serverStatus: 'available', userEnabled: true });
  assert.equal(await action, false); assert.deepEqual(view.snapshot, before);
});
test('B05 A-to-B-to-A still rejects original A response: scope equality alone is insufficient', () => {
  const view = new ScopedAccessView('a'), old = view.beginRead();
  view.switchOrg('b'); view.switchOrg('a');
  assert.deepEqual(view.receive(old, { org: 'a', clientGate: true, serverStatus: 'available' }, 1), { accepted: false, reason: 'stale-generation' });
  assert.equal(view.snapshot, undefined);
});
test('B06 latest same-scope request wins, and a current reply with wrong org is independently rejected', () => {
  const view = new ScopedAccessView('a'), old = view.beginRead(), current = view.beginRead();
  assert.equal(view.receive(old, { org: 'a' }, 1).reason, 'stale-generation');
  assert.equal(view.receive(current, { org: 'b' }, 1).reason, 'scope-mismatch');
  assert.equal(view.snapshot, undefined);
});
test('B07 stale or future allow plus failed refresh denies a new action', async () => {
  for (const checkedAt of [0, 2000]) {
    const view = new ScopedAccessView('a', { org: 'a', allowed: true, checkedAt });
    assert.equal(await view.mayStartAction(1000, 100, async () => { throw new Error('offline'); }), false);
  }
});
test('B08 a fresh wrong-organization allow is not reusable', async () => {
  const view = new ScopedAccessView('b', { org: 'a', allowed: true, checkedAt: 999 });
  let reads = 0;
  assert.equal(await view.mayStartAction(1000, 100, async org => { reads++; assert.equal(org, 'b'); throw new Error('offline'); }), false);
  assert.equal(reads, 1);
});
test('B09 switch during await invalidates even a fresh cached allow', async () => {
  const view = new ScopedAccessView('a', { org: 'a', allowed: true, checkedAt: 999 });
  const action = view.mayStartAction(1000, 100, async () => { throw new Error('must not refresh'); });
  view.switchOrg('b'); assert.equal(await action, false);
});
test('B10 recent correct-scope allow can be reused; server refusal outranks user preference', async () => {
  const view = new ScopedAccessView('a', { org: 'a', allowed: true, checkedAt: 999 });
  assert.equal(await view.mayStartAction(1000, 100, () => assert.fail('no refresh')), true);
  assert.equal(await view.mayStartAction(2000, 100, async () => ({ org: 'a', clientGate: true, serverStatus: 'blocked_by_org_admin', userEnabled: true })), false);
  assert.equal(view.snapshot.state, 'blocked_by_org_admin');
});
