/** Original single-parent conversation tree. Not an extracted Claude module. */
export const ROOT = '00000000-0000-4000-8000-000000000000';
const clone = value => structuredClone(value);

export class ConversationBranches {
  messageByUuid = new Map();
  parentByChildUuid = new Map();
  childrenByParentUuid = new Map();
  selectedChildByUuid = new Map();
  currentLeaf = undefined;
  danglingHumanMessages = [];

  constructor(messages = [], { currentLeaf, includeDanglingHumans = false } = {}) {
    const records = messages.map(clone);
    for (const message of records) {
      if (message.index !== undefined && (!Number.isSafeInteger(message.index) || message.index < 0)) {
        throw new Error('Invalid message index');
      }
    }
    const byIndex = new Map(records.filter(m => m.index !== undefined).map(message => [message.index, message.uuid]));
    const indices = [...byIndex.keys()].sort((a, b) => a - b);
    const precedingUuid = index => {
      let low = 0, high = indices.length;
      while (low < high) {
        const mid = Math.floor((low + high) / 2);
        if (indices[mid] < index) low = mid + 1;
        else high = mid;
      }
      return low ? byIndex.get(indices[low - 1]) : undefined;
    };
    const normalized = records.map(message => ({
      ...message, parent_message_uuid: message.parent_message_uuid || precedingUuid(message.index) || ROOT,
      content: message.content ?? [{ type: 'text', text: message.text ?? '', citations: [] }],
    }));
    // Validate the entire supplied graph before display filtering can hide an
    // invalid dangling-only component. Validation performs no mutations.
    this.#prepareBatch(normalized);
    const answered = new Set(records.filter(m => m.sender === 'assistant').map(m => m.parent_message_uuid));
    const byId = new Map(normalized.map(message => [message.uuid, message]));
    if (byId.size !== records.length) throw new Error('Duplicate message UUID');
    const retained = new Set(records.filter(m => includeDanglingHumans || m.sender === 'assistant' ||
      answered.has(m.uuid) || m.parent_message_uuid === undefined).map(m => m.uuid));
    // Ancestors remain available even when a dangling human is omitted.
    for (const id of [...retained]) {
      const seen = new Set();
      let parent = byId.get(id)?.parent_message_uuid;
      while (parent && parent !== ROOT) {
        if (seen.has(parent)) throw new Error('Cycle in message ancestry');
        seen.add(parent);
        retained.add(parent);
        parent = byId.get(parent)?.parent_message_uuid;
      }
    }
    this.danglingHumanMessages = records.filter(m => !retained.has(m.uuid) && m.sender === 'human');
    this.#insertBatch(normalized.filter(m => retained.has(m.uuid)));
    if (currentLeaf && this.messageByUuid.has(currentLeaf)) this.selectLeaf(currentLeaf);
    else this.currentLeaf = this.visiblePath().at(-1)?.uuid;
  }

  #prepareBatch(messages) {
    // Clone every record before touching any index. A later DataCloneError must
    // not leave earlier records partially committed.
    messages = messages.map(clone);
    // Atomic validation is an intentional hardening in this teaching version.
    const proposed = new Map(this.messageByUuid);
    for (const message of messages) {
      if (!message.uuid || message.uuid === ROOT || proposed.has(message.uuid)) throw new Error('Duplicate or reserved UUID');
      if (!message.parent_message_uuid) throw new Error('Parent UUID required');
      proposed.set(message.uuid, message);
    }
    for (const message of messages) {
      const seen = new Set([message.uuid]);
      let parent = message.parent_message_uuid;
      while (parent !== ROOT) {
        if (seen.has(parent)) throw new Error('Cycle in message ancestry');
        seen.add(parent);
        const ancestor = proposed.get(parent);
        if (!ancestor) throw new Error('Parent UUID is missing');
        parent = ancestor.parent_message_uuid;
      }
    }
    return messages;
  }

  #insertBatch(messages) {
    const prepared = this.#prepareBatch(messages);
    for (const message of prepared) {
      const parent = message.parent_message_uuid;
      this.messageByUuid.set(message.uuid, message);
      this.parentByChildUuid.set(message.uuid, parent);
      const siblings = this.childrenByParentUuid.get(parent) ?? [];
      siblings.push(message.uuid);
      this.childrenByParentUuid.set(parent, siblings);
      this.selectedChildByUuid.set(parent, this.selectedChildByUuid.get(parent) ?? 0);
    }
    return prepared;
  }

  append(messages) {
    if (!messages.length) return;
    const prepared = this.#insertBatch(messages);
    for (const message of prepared) {
      const siblings = this.childrenByParentUuid.get(message.parent_message_uuid);
      this.selectedChildByUuid.set(message.parent_message_uuid, siblings.indexOf(message.uuid));
    }
    this.selectLeaf(prepared.at(-1).uuid);
  }

  selectLeaf(uuid) {
    if (!this.messageByUuid.has(uuid)) throw new Error('Unknown leaf');
    const seen = new Set();
    for (let child = uuid; child !== ROOT;) {
      if (seen.has(child)) throw new Error('Cycle in selected ancestry');
      seen.add(child);
      const parent = this.parentByChildUuid.get(child);
      const siblings = this.childrenByParentUuid.get(parent);
      if (!siblings?.includes(child)) throw new Error('Broken tree index');
      this.selectedChildByUuid.set(parent, siblings.indexOf(child));
      child = parent;
    }
    this.currentLeaf = uuid;
  }

  visiblePath(start = ROOT) {
    const result = [];
    const seen = new Set();
    let parent = start;
    while (this.childrenByParentUuid.has(parent)) {
      if (seen.has(parent)) throw new Error('Cycle in visible path');
      seen.add(parent);
      const siblings = this.childrenByParentUuid.get(parent);
      const selected = this.selectedChildByUuid.get(parent) ?? 0;
      const message = this.messageByUuid.get(siblings[selected]);
      if (!message) throw new Error('Invalid selected child');
      result.push({ ...clone(message), nOptions: siblings.length, selectedOption: selected,
        siblingUuids: [...siblings] });
      parent = message.uuid;
    }
    return result;
  }

  switchSibling(messageUuid, offset) {
    const parent = this.parentByChildUuid.get(messageUuid);
    if (parent === undefined) throw new Error('Unknown message');
    const siblings = this.childrenByParentUuid.get(parent);
    const current = this.selectedChildByUuid.get(parent) ?? 0;
    this.selectedChildByUuid.set(parent, Math.max(0, Math.min(siblings.length - 1, current + offset)));
    this.selectLeaf(this.visiblePath(parent).at(-1).uuid);
    return this.currentLeaf;
  }

  editHuman(uuid, text, { humanUuid, assistantUuid }) {
    const original = this.messageByUuid.get(uuid);
    if (original?.sender !== 'human') throw new Error('Editing requires a human message');
    this.append([
      { uuid: humanUuid, sender: 'human', parent_message_uuid: original.parent_message_uuid,
        content: [{ type: 'text', text }] },
      { uuid: assistantUuid, sender: 'assistant', parent_message_uuid: humanUuid, content: [] },
    ]);
  }

  retryAssistant(uuid, assistantUuid) {
    const original = this.messageByUuid.get(uuid);
    if (!original) throw new Error('Unknown retry target');
    const parent = original.sender === 'assistant' ? original.parent_message_uuid : original.uuid;
    this.append([{ uuid: assistantUuid, sender: 'assistant', parent_message_uuid: parent, content: [] }]);
  }
}
