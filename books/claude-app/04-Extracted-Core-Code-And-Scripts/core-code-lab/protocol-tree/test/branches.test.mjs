import test from 'node:test';
import assert from 'node:assert/strict';
import { ConversationBranches, ROOT } from '../branch-manager.mjs';
const human = (uuid, parent = ROOT, index = 0) => ({ uuid, parent_message_uuid: parent, sender: 'human', index, text: uuid });
const answer = (uuid, parent, index = 1) => ({ uuid, parent_message_uuid: parent, sender: 'assistant', index, text: uuid });
const ids = tree => tree.visiblePath().map(message => message.uuid);

test('selected leaf chooses a root-to-leaf path among siblings', () => {
  const tree = new ConversationBranches([human('h1'), answer('a1', 'h1'), answer('a2', 'h1'), human('h2', 'a2'), answer('a3', 'h2')], { currentLeaf: 'a3' });
  assert.deepEqual(ids(tree), ['h1', 'a2', 'h2', 'a3']);
  assert.equal(tree.visiblePath()[1].nOptions, 2);
  tree.switchSibling('a2', -1); assert.deepEqual(ids(tree), ['h1', 'a1']);
  tree.switchSibling('a1', 1); assert.deepEqual(ids(tree), ['h1', 'a2', 'h2', 'a3']);
});
test('editing forks a new human branch and leaves original descendants intact', () => {
  const tree = new ConversationBranches([human('h1'), answer('a1', 'h1'), human('h2', 'a1', 2), answer('a2', 'h2', 3)]);
  tree.editHuman('h2', 'Revised', { humanUuid: 'h2b', assistantUuid: 'a2b' });
  assert.deepEqual(ids(tree), ['h1', 'a1', 'h2b', 'a2b']);
  assert.equal(tree.messageByUuid.has('a2'), true);
  tree.switchSibling('h2b', -1); assert.deepEqual(ids(tree), ['h1', 'a1', 'h2', 'a2']);
});
test('retry appends an assistant sibling, not a second parent', () => {
  const tree = new ConversationBranches([human('h1'), answer('a1', 'h1')]);
  tree.retryAssistant('a1', 'a1b');
  assert.deepEqual(tree.childrenByParentUuid.get('h1'), ['a1', 'a1b']);
  assert.equal(tree.parentByChildUuid.get('a1b'), 'h1');
  assert.deepEqual(ids(tree), ['h1', 'a1b']);
});
test('dangling human messages can be separated from the completed display path', () => {
  const messages = [human('h1'), answer('a1', 'h1'), human('waiting', 'a1', 2)];
  const tree = new ConversationBranches(messages);
  assert.deepEqual(ids(tree), ['h1', 'a1']);
  assert.equal(tree.danglingHumanMessages[0].uuid, 'waiting');
  const all = new ConversationBranches(messages, { includeDanglingHumans: true });
  assert.deepEqual(ids(all), ['h1', 'a1', 'waiting']);
});
test('legacy missing parents are inferred from the previous available index', () => {
  const tree = new ConversationBranches([{ uuid: 'old1', sender: 'human', index: 1, text: 'A' }, { uuid: 'old2', sender: 'assistant', index: 3, text: 'B' }]);
  assert.deepEqual(ids(tree), ['old1', 'old2']);
  assert.equal(tree.messageByUuid.get('old1').content[0].text, 'A');
});
test('invalid batch insertion is atomic', () => {
  const tree = new ConversationBranches([human('h1'), answer('a1', 'h1')]);
  assert.throws(() => tree.append([answer('good', 'h1'), answer('bad', 'missing')]), /missing/);
  assert.equal(tree.messageByUuid.has('good'), false);
  assert.deepEqual(ids(tree), ['h1', 'a1']);
});
test('cycles, duplicate IDs and unknown leaves are rejected', () => {
  assert.throws(() => new ConversationBranches([answer('a', 'b'), answer('b', 'a')]), /Cycle/);
  assert.throws(() => new ConversationBranches([human('h'), human('h')]), /Duplicate/);
  assert.throws(() => new ConversationBranches([]).selectLeaf('absent'), /Unknown/);
});
