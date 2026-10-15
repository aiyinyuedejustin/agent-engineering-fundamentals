import assert from 'node:assert/strict';
import { prepareCanonicalPair, makeTreeFixture, canonicalPair, snapshotTree } from './tree-rekey.mjs';
const store = { current: makeTreeFixture() };
const original = store.current, before = snapshotTree(original);
const candidate = prepareCanonicalPair(original, canonicalPair);
assert.deepEqual(snapshotTree(original), before); // Preparation did not publish anything.
store.current = candidate; // The sole publication point in this single-threaded example.
const after = snapshotTree(store.current);
assert.equal(store.current.currentLeaf, 'a1');
if (process.argv.includes('--json')) console.log(JSON.stringify({ before, after }, null, 2));
else {
  console.log('before: h0 > a0 > opt:h1 > opt:a1');
  console.log('after:  ' + after.visiblePath.map(m => m.uuid).join(' > '));
  console.log('a0 children: ' + store.current.childrenByParentUuid.get('a0').join(', '));
  console.log('selected a0: ' + store.current.selectedChildByUuid.get('a0'));
  console.log('dangling: ' + store.current.danglingHumanMessages.map(m => m.uuid).join(', '));
  console.log('old snapshot unchanged: true');
}
