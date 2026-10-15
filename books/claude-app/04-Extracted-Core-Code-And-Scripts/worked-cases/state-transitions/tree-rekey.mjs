/** Case-specific, copy-on-write adapter around the book's original tree model.
 * No target implementation, network, event reducer, row-key or storage model.
 */
import { ConversationBranches, ROOT } from './original-models.mjs';
export { ConversationBranches, ROOT };
const copy = value => structuredClone(value);
const fail = reason => { throw new Error(reason); };

export function snapshotTree(tree) {
  return copy({
    messageByUuid: [...tree.messageByUuid], parentByChildUuid: [...tree.parentByChildUuid],
    childrenByParentUuid: [...tree.childrenByParentUuid], selectedChildByUuid: [...tree.selectedChildByUuid],
    currentLeaf: tree.currentLeaf, danglingHumanMessages: tree.danglingHumanMessages,
    visiblePath: tree.visiblePath().map(m => ({ uuid: m.uuid, parent: m.parent_message_uuid,
      nOptions: m.nOptions, selectedOption: m.selectedOption, siblingUuids: m.siblingUuids })),
  });
}

/** Validate the indexed input rather than silently repair public-Map corruption. */
export function checkIndexedTree(tree) {
  const messages = [...tree.messageByUuid.values()];
  new ConversationBranches([...messages, ...tree.danglingHumanMessages], { includeDanglingHumans: true });
  const expectedChildren = new Map();
  for (const [id, message] of tree.messageByUuid) {
    if (id !== message.uuid || tree.parentByChildUuid.get(id) !== message.parent_message_uuid)
      fail('Index/message disagreement');
    const children = expectedChildren.get(message.parent_message_uuid) ?? [];
    children.push(id); expectedChildren.set(message.parent_message_uuid, children);
  }
  if (tree.parentByChildUuid.size !== messages.length || tree.childrenByParentUuid.size !== expectedChildren.size ||
      tree.selectedChildByUuid.size !== expectedChildren.size) fail('Index cardinality disagreement');
  for (const [parent, children] of expectedChildren) {
    if (JSON.stringify(tree.childrenByParentUuid.get(parent)) !== JSON.stringify(children)) fail('Child order disagreement');
    const selected = tree.selectedChildByUuid.get(parent);
    if (!Number.isInteger(selected) || selected < 0 || selected >= children.length) fail('Invalid selected position');
  }
  if (tree.currentLeaf !== undefined && !tree.messageByUuid.has(tree.currentLeaf)) fail('Unknown current leaf');
  tree.visiblePath();
}

/** Narrow fast path: replace an optimistic human+assistant pair, never merge IDs.
 * Returns a fully checked new tree. Caller publishes once with store.current = next.
 * The old tree and its public Maps are never mutated, even when validation throws.
 */
export function prepareCanonicalPair(tree, { optimisticHuman, optimisticAssistant, canonicalHuman, canonicalAssistant }) {
  checkIndexedTree(tree);
  const human = tree.messageByUuid.get(optimisticHuman), assistant = tree.messageByUuid.get(optimisticAssistant);
  if (human?.sender !== 'human' || assistant?.sender !== 'assistant') fail('Optimistic pair missing or wrong sender');
  if (!optimisticHuman.startsWith('opt:') || !optimisticAssistant.startsWith('opt:')) fail('Expected optimistic identities');
  if (assistant.parent_message_uuid !== optimisticHuman) fail('Assistant parent mismatch');
  const occupied = new Set([...tree.messageByUuid.keys(), ...tree.danglingHumanMessages.map(m => m.uuid)]);
  for (const id of [canonicalHuman, canonicalAssistant]) {
    if (typeof id !== 'string' || !id || id === ROOT || id.startsWith('opt:') || occupied.has(id))
      fail('Canonical identity invalid or occupied');
  }
  if (canonicalHuman === canonicalAssistant) fail('Canonical identities must differ');
  // A filtered dangling human is still a dependent, even without an indexed edge.
  if (tree.childrenByParentUuid.has(optimisticAssistant) ||
      tree.danglingHumanMessages.some(m => m.parent_message_uuid === optimisticAssistant))
    fail('Optimistic assistant already has descendants');

  const rename = id => id === optimisticHuman ? canonicalHuman : id === optimisticAssistant ? canonicalAssistant : id;
  const rewrite = message => ({ ...copy(message), uuid: rename(message.uuid),
    parent_message_uuid: rename(message.parent_message_uuid) });
  const retained = [...tree.messageByUuid.values()].map(rewrite);
  const dangling = tree.danglingHumanMessages.map(rewrite);
  // Use the imported constructor for graph validation, cloning and index building.
  // includeDanglingHumans keeps the current indexed partition; it does not guess UI filtering anew.
  const candidate = new ConversationBranches(retained, { includeDanglingHumans: true });
  candidate.selectedChildByUuid = new Map([...tree.selectedChildByUuid].map(([parent, position]) => [rename(parent), position]));
  candidate.currentLeaf = rename(tree.currentLeaf);
  candidate.danglingHumanMessages = dangling;
  checkIndexedTree(candidate);
  return candidate;
}

export function makeTreeFixture({ selected = 'opt:a1' } = {}) {
  const msg = (uuid, parent, sender, text) => ({ uuid, parent_message_uuid: parent, sender,
    content: [{ type: 'text', text }] });
  return new ConversationBranches([
    msg('h0', ROOT, 'human', '比较两种方案'), msg('a0', 'h0', 'assistant', '先明确约束'),
    msg('h-old', 'a0', 'human', '旧版本问题'), msg('a-old', 'h-old', 'assistant', '旧版本回答'),
    msg('opt:h1', 'a0', 'human', '修订后的问题'), msg('opt:a1', 'opt:h1', 'assistant', '新回答已收齐'),
    msg('h-wait', 'a0', 'human', '另一条尚未回答的输入'),
  ], { currentLeaf: selected });
}
export const canonicalPair = Object.freeze({ optimisticHuman: 'opt:h1', optimisticAssistant: 'opt:a1', canonicalHuman: 'h1', canonicalAssistant: 'a1' });
