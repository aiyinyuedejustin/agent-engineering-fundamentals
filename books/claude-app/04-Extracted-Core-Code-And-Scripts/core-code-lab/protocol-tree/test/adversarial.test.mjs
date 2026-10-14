import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
const core = new URL(process.env.PROTOCOL_STRESS_ORIGINAL === '1'
  ? '../../../../publication/04-Extracted-Core-Code-And-Scripts/core-code-lab/protocol-tree/' : '../', import.meta.url);
const { IncrementalSSE, consumeChunks, makeWorkBudget } = await import(new URL('incremental-sse.mjs', core));
const { ContentReducer } = await import(new URL('content-reducer.mjs', core));
const { ConversationBranches, ROOT } = await import(new URL('branch-manager.mjs', core));
const { LegacyTagStream } = await import(new URL('legacy-tags.mjs', core));
const bytes = text => new TextEncoder().encode(text);
const human = (uuid, parent = ROOT, index = 0) => ({ uuid, parent_message_uuid: parent, sender: 'human', index });
const answer = (uuid, parent, index = 1) => ({ uuid, parent_message_uuid: parent, sender: 'assistant', index });
const normalize = events => ({ text: events.filter(e => e.type === 'text').map(e => e.text).join(''), artifacts: events.filter(e => e.type === 'artifact') });
const snapshotTree = tree => structuredClone({ messages: [...tree.messageByUuid], parents: [...tree.parentByChildUuid], children: [...tree.childrenByParentUuid], selected: [...tree.selectedChildByUuid], leaf: tree.currentLeaf });

test('PS01: core SSE budget errors are terminal and rejected data cannot escape', () => {
  for (const [options, input] of [[{ maxLineCharacters: 6 }, 'data: a'], [{ maxEventCharacters: 6 }, 'data: a\n']]) {
    const p = new IncrementalSSE(options);
    assert.throws(() => p.push(bytes(input)), /limit/);
    assert.throws(() => p.push(bytes('\n\n')), /closed/);
    assert.deepEqual(p.finish(), []);
  }
});
test('PS01: core SSE limit configuration cannot silently disable enforcement', () => {
  for (const value of [-1, NaN, Infinity, 0.5, '6', null]) {
    assert.throws(() => new IncrementalSSE({ maxLineCharacters: value }), /limit/i);
    assert.throws(() => new IncrementalSSE({ maxEventCharacters: value }), /limit/i);
  }
});
test('PS02: core legacy budget measures retained state, independent of chunk partition', () => {
  assert.deepEqual(normalize(new LegacyTagStream({ maxBufferedCharacters: 2 }).push('abcd', { final: true })), { text: 'abcd', artifacts: [] });
  const source = 'ab<antArtifact>x</antArtifact><antArtifact>y</antArtifact>cd';
  const expected = normalize(new LegacyTagStream({ maxBufferedCharacters: 28 }).push(source, { final: true }));
  for (let i = 0; i <= source.length; i++) for (let j = i; j <= source.length; j++) {
    const p = new LegacyTagStream({ maxBufferedCharacters: 28 });
    assert.deepEqual(normalize([...p.push(source.slice(0, i)), ...p.push(source.slice(i, j)), ...p.push(source.slice(j), { final: true })]), expected);
  }
});
test('PS02: core legacy failure and finalization terminate the parser', () => {
  const p = new LegacyTagStream({ maxBufferedCharacters: 2 });
  assert.throws(() => p.push('<ant'), /limit/);
  assert.throws(() => p.push('Artifact>'), /closed/);
  const q = new LegacyTagStream(); q.push('', { final: true });
  assert.throws(() => q.push('late'), /closed/);
});
test('PS03: malformed retraction cannot silently erase reducer state', () => {
  for (const from_index of [undefined, null, NaN, Infinity, -1, 0.5, '0']) {
    const p = new ContentReducer(() => {}, { schedule: () => {} });
    p.apply({ type: 'content_block_start', index: 0, content_block: { type: 'text', text: 'keep' } });
    const before = structuredClone(p.blocks);
    assert.throws(() => p.apply({ type: 'content_block_retract', from_index }), /Invalid retraction/);
    assert.deepEqual(p.blocks, before);
  }
});
test('PS04: filtered dangling messages cannot hide cycles or missing parents', () => {
  assert.throws(() => new ConversationBranches([human('a', 'b'), human('b', 'a')]), /Cycle/);
  assert.throws(() => new ConversationBranches([human('orphan', 'missing')]), /missing/);
  assert.throws(() => new ConversationBranches([human('h'), answer('a', 'h'), human('x', 'y'), human('y', 'x')]), /Cycle/);
});
test('PS05: abort inside a frame blocks later frames in the same chunk', async () => {
  for (const asynchronous of [false, true]) {
    const controller = new AbortController(), seen = [];
    async function* chunks() { yield bytes('data:1\n\ndata:2\n\n'); }
    const apply = frame => { seen.push(frame.data); controller.abort(); };
    await assert.rejects(consumeChunks(chunks(), asynchronous ? async frame => { await Promise.resolve(); apply(frame); } : apply, { signal: controller.signal }), { name: 'AbortError' });
    assert.deepEqual(seen, ['1']);
  }
});
test('PS05: already-aborted consumption never asks the source for its first chunk', async () => {
  const controller = new AbortController(); controller.abort(); let reads = 0;
  async function* chunks() { reads++; yield bytes('data:1\n\n'); }
  await assert.rejects(consumeChunks(chunks(), () => {}, { signal: controller.signal }), { name: 'AbortError' });
  assert.equal(reads, 0);
});
test('PS06: a clone failure leaves every tree index and selection unchanged', () => {
  const tree = new ConversationBranches([human('h'), answer('a', 'h')]);
  const before = snapshotTree(tree);
  assert.throws(() => tree.append([answer('good', 'h'), { ...answer('bad', 'h'), content: () => {} }]), { name: 'DataCloneError' });
  assert.deepEqual(snapshotTree(tree), before);
});
test('PS07: sparse legacy indices do not cause a gap-sized loop', () => {
  const script = `import {ConversationBranches} from ${JSON.stringify(new URL('branch-manager.mjs', core).href)}; const p=new ConversationBranches([{uuid:'h',sender:'human',index:0},{uuid:'a',sender:'assistant',index:Number.MAX_SAFE_INTEGER}]); if(p.messageByUuid.get('a').parent_message_uuid!=='h')process.exit(3);`;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { timeout: 2_000, encoding: 'utf8' });
  assert.equal(result.error, undefined, result.error?.message);
  assert.equal(result.status, 0, result.stderr);
});
test('PS07: invalid legacy indices fail promptly', () => {
  // Child-process timeout bounds the unfixed Infinity hang.
  const script = `import assert from 'node:assert/strict'; import {ConversationBranches} from ${JSON.stringify(new URL('branch-manager.mjs', core).href)}; for(const index of [Infinity,NaN,-1,0.5,'2'])assert.throws(()=>new ConversationBranches([{uuid:'h',sender:'human',index}]),/index/i);`;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { timeout: 2_000, encoding: 'utf8' });
  assert.equal(result.error, undefined, result.error?.message);
  assert.equal(result.status, 0, result.stderr);
});

test('PS08: core quoted attribute delimiters cannot become artifact body text', () => {
  const source = '<antArtifact title="a > b">body</antArtifact>';
  for (let split = 0; split <= source.length; split++) {
    const p = new LegacyTagStream();
    assert.deepEqual([...p.push(source.slice(0, split)), ...p.push(source.slice(split), { final: true })], [{ type: 'artifact', attributes: { title: 'a > b' }, content: 'body', closed: true }]);
  }
});

test('terminal reducer snapshot flushes once and incomplete tool JSON never becomes parsed input', () => {
  const pending = [], seen = [];
  const p = new ContentReducer(s => seen.push(s), { schedule: task => pending.push(task) });
  p.apply({ type: 'content_block_start', index: 0, content_block: { type: 'tool_use', id: 't', name: 'never-executed' } });
  p.apply({ type: 'content_block_delta', index: 0, delta: { type: 'input_json_delta', partial_json: '{"code":' } });
  p.apply({ type: 'content_block_stop', index: 0 }); p.apply({ type: 'message_stop' });
  p.flush(); pending.forEach(task => task());
  assert.equal(seen.length, 1); assert.equal(seen[0].done, true); assert.equal(Object.hasOwn(seen[0].blocks[0], 'parsed_input'), false);
});
test('editing/retrying a nonselected branch preserves its relatives and selects the resulting path', () => {
  const tree = new ConversationBranches([human('h'), answer('a', 'h'), answer('b', 'h'), human('ha', 'a', 2), answer('aa', 'ha', 3), human('hb', 'b', 2), answer('bb', 'hb', 3)], { currentLeaf: 'aa' });
  tree.retryAssistant('bb', 'bb2'); assert.deepEqual(tree.visiblePath().map(m => m.uuid), ['h', 'b', 'hb', 'bb2']);
  tree.editHuman('ha', 'revised', { humanUuid: 'ha2', assistantUuid: 'aa2' }); assert.deepEqual(tree.visiblePath().map(m => m.uuid), ['h', 'a', 'ha2', 'aa2']);
  assert.equal(tree.messageByUuid.has('aa'), true); assert.equal(tree.messageByUuid.has('bb'), true);
  tree.switchSibling('ha2', -1); assert.deepEqual(tree.visiblePath().map(m => m.uuid), ['h', 'a', 'ha', 'aa']);
});
test('duplicate IDs and cyclic append failures are atomic across nonselected branches', () => {
  const tree = new ConversationBranches([human('h'), answer('a', 'h'), answer('b', 'h')]);
  const before = snapshotTree(tree);
  for (const records of [[answer('b', 'h')], [answer('x', 'y'), answer('y', 'x')], [answer('x', 'h'), answer('x', 'h')]]) {
    assert.throws(() => tree.append(records), /Duplicate|Cycle/); assert.deepEqual(snapshotTree(tree), before);
  }
});
test('work budget remains a cooperative checkpoint, not an end-to-end throughput claim', async () => {
  let now = 0, yielded = 0; const budget = makeWorkBudget({ now: () => now, milliseconds: 8, yieldToLoop: async () => { yielded++; now += 1; } });
  now = 7; await budget(); assert.equal(yielded, 0); now = 8; await budget(); assert.equal(yielded, 1); now = 16; await budget(); assert.equal(yielded, 1); now = 17; await budget(); assert.equal(yielded, 2);
});

test('random trees: selected and nonselected branch traversal matches independent ancestry', () => {
  let seed = 0x712309;
  const random = n => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed % n; };
  for (let run = 0; run < 100; run++) {
    const records = [];
    for (let i = 0; i < 40; i++) records.push(answer(`n${i}`, i === 0 || random(8) === 0 ? ROOT : `n${random(i)}`, i));
    const tree = new ConversationBranches(records);
    const parents = new Map(records.map(r => [r.uuid, r.parent_message_uuid]));
    const leaves = records.filter(r => !records.some(child => child.parent_message_uuid === r.uuid));
    for (const leaf of leaves) {
      tree.selectLeaf(leaf.uuid); const expected = [];
      for (let id = leaf.uuid; id !== ROOT; id = parents.get(id)) expected.unshift(id);
      assert.deepEqual(tree.visiblePath().map(m => m.uuid), expected);
      assert.equal(tree.currentLeaf, leaf.uuid);
    }
  }
});
