import test from 'node:test';
import assert from 'node:assert/strict';
import { IncrementalSSE, consumeChunks, makeWorkBudget } from '../incremental-sse.mjs';
import { ContentReducer } from '../content-reducer.mjs';
import { LegacyTagStream } from '../legacy-tags.mjs';
const bytes = text => new TextEncoder().encode(text);

for (const separator of ['\n', '\r', '\r\n']) test(`SSE survives every two-chunk cut with ${JSON.stringify(separator)}`, () => {
  const wire = bytes(['event: content_block_delta', 'id: turn-7', 'data: {"text":"中文🙂"}', '', ''].join(separator));
  for (let split = 0; split <= wire.length; split++) {
    const parser = new IncrementalSSE();
    const frames = [...parser.push(wire.slice(0, split)), ...parser.push(wire.slice(split)), ...parser.finish()];
    assert.equal(frames.length, 1);
    assert.equal(frames[0].event, 'content_block_delta');
    assert.deepEqual(JSON.parse(frames[0].data), { text: '中文🙂' });
    assert.equal(parser.lastEventId, 'turn-7');
  }
});

test('SSE handles bytewise chunks, multiline data, comments, and retry', () => {
  const parser = new IncrementalSSE();
  const frames = [];
  for (const byte of bytes(': note\nretry: 25\nevent: custom\ndata: one\ndata: two\n\n')) frames.push(...parser.push(Uint8Array.of(byte)));
  assert.deepEqual(frames[0], { event: 'custom', data: 'one\ntwo', id: undefined, retry: 25 });
  assert.equal(parser.retryMilliseconds, 25);
});
test('SSE does not manufacture a final unterminated frame', () => {
  const parser = new IncrementalSSE();
  assert.deepEqual(parser.push(bytes('data: incomplete\n')), []);
  assert.deepEqual(parser.finish(), []);
  assert.throws(() => parser.push(bytes('x')), /closed/);
});
test('SSE memory guards reject oversized lines and events', () => {
  assert.throws(() => new IncrementalSSE({ maxLineCharacters: 3 }).push(bytes('data: x')), /line limit/);
  assert.throws(() => new IncrementalSSE({ maxEventCharacters: 5 }).push(bytes('data: a\n')), /event limit/);
});
test('consumer awaits work before requesting the next chunk', async () => {
  const order = [];
  async function* chunks() { order.push('read1'); yield bytes('data: 1\n\n'); order.push('read2'); yield bytes('data: 2\n\n'); }
  await consumeChunks(chunks(), frame => order.push(`frame${frame.data}`), { afterChunk: async () => { order.push('yield'); await Promise.resolve(); } });
  assert.deepEqual(order, ['read1', 'frame1', 'yield', 'read2', 'frame2', 'yield']);
});
test('work budget yields after elapsed time', async () => {
  let time = 0, yielded = 0;
  const budget = makeWorkBudget({ now: () => time, yieldToLoop: async () => yielded++, milliseconds: 8 });
  await budget(); assert.equal(yielded, 0);
  time = 9; await budget(); assert.equal(yielded, 1);
  time = 10; await budget(); assert.equal(yielded, 1);
});
test('reducer coalesces a chunk and preserves immutable snapshots', () => {
  const scheduled = [], delivered = [];
  const state = new ContentReducer(value => delivered.push(value), { schedule: task => scheduled.push(task) });
  state.apply({ type: 'message_start' });
  state.apply({ type: 'content_block_start', index: 0, content_block: { type: 'text', text: '' } });
  state.apply({ type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: 'A' } });
  state.apply({ type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: 'B' } });
  assert.equal(scheduled.length, 1); scheduled.shift()();
  assert.equal(delivered[0].blocks[0].text, 'AB');
  state.apply({ type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: 'C' } });
  assert.equal(delivered[0].blocks[0].text, 'AB');
  state.flush(); assert.equal(delivered[1].blocks[0].text, 'ABC');
});
test('reducer permits specified late summaries but rejects other stale deltas', () => {
  const state = new ContentReducer();
  state.apply({ type: 'content_block_start', index: 0, content_block: { type: 'thinking', thinking: '' } });
  state.apply({ type: 'content_block_start', index: 1, content_block: { type: 'text', text: '' } });
  state.apply({ type: 'content_block_delta', index: 0, delta: { type: 'thinking_summary_delta', summary: { summary: 'Brief' } } });
  assert.equal(state.blocks[0].summaries[0].summary, 'Brief');
  assert.throws(() => state.apply({ type: 'content_block_delta', index: 0, delta: { type: 'thinking_delta', thinking: 'late' } }), /active/);
});
test('tool-use JSON is accumulated; tool-result payload is replaced', () => {
  const state = new ContentReducer();
  state.apply({ type: 'content_block_start', index: 0, content_block: { type: 'tool_use', name: 'example', id: 'tool-1', input: {} } });
  for (const partial_json of ['{"q":', '"hello"}']) state.apply({ type: 'content_block_delta', index: 0, delta: { type: 'input_json_delta', partial_json } });
  state.apply({ type: 'content_block_stop', index: 0 });
  assert.deepEqual(state.blocks[0].parsed_input, { q: 'hello' });
  state.apply({ type: 'content_block_start', index: 1, content_block: { type: 'tool_result', content: [] } });
  for (const partial_json of ['first', 'second']) state.apply({ type: 'content_block_delta', index: 1, delta: { type: 'input_json_delta', partial_json } });
  assert.deepEqual(state.blocks[1].content, [{ type: 'text', text: 'second' }]);
});
test('retraction resets index base; later message-start appends another segment', () => {
  const state = new ContentReducer();
  for (const index of [0, 1]) state.apply({ type: 'content_block_start', index, content_block: { type: 'text', text: String(index) } });
  state.apply({ type: 'content_block_retract', from_index: 1 });
  state.apply({ type: 'content_block_start', index: 7, content_block: { type: 'text', text: 'replacement' } });
  state.apply({ type: 'message_stop' }); assert.equal(state.done, true);
  state.apply({ type: 'message_start' });
  state.apply({ type: 'content_block_start', index: 0, content_block: { type: 'text', text: 'next segment' } });
  assert.deepEqual(state.blocks.map(b => b.text), ['0', 'replacement', 'next segment']);
});
test('restart invalidates an old queued delivery', () => {
  const queue = [], seen = [];
  const state = new ContentReducer(x => seen.push(x), { schedule: x => queue.push(x) });
  state.apply({ type: 'message_start' }); state.restart();
  state.apply({ type: 'content_block_start', index: 0, content_block: { type: 'text', text: 'new' } });
  queue[0](); assert.equal(seen.length, 0);
  queue[1](); assert.equal(seen[0].blocks[0].text, 'new');
});
test('legacy tags survive every chunk boundary without showing thinking text', () => {
  const input = 'Before<antThinking>hidden</antThinking><antArtifact identifier="demo" type="text/plain">Body</antArtifact>After';
  for (let split = 0; split <= input.length; split++) {
    const parser = new LegacyTagStream();
    const values = [...parser.push(input.slice(0, split)), ...parser.push(input.slice(split), { final: true })];
    assert.equal(values.filter(v => v.type === 'text').map(v => v.text).join(''), 'BeforeAfter');
    assert.equal(values.find(v => v.type === 'artifact').content, 'Body');
    assert.equal(values.find(v => v.type === 'artifact').closed, true);
  }
});
test('an unfinished legacy artifact is data marked open', () => {
  const parser = new LegacyTagStream();
  assert.deepEqual(parser.push('<antArtifact identifier="x">hello', { final: true }), [
    { type: 'artifact', attributes: { identifier: 'x' }, content: 'hello', closed: false },
  ]);
});

test('a full chunk flows synchronously into one coalesced snapshot', async () => {
  const seen = [];
  const reducer = new ContentReducer(snapshot => seen.push(snapshot));
  const events = [
    { type: 'content_block_start', index: 0, content_block: { type: 'text', text: '' } },
    { type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: 'A' } },
    { type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: 'B' } },
  ];
  async function* chunks() { yield bytes(events.map(event => `data: ${JSON.stringify(event)}\n\n`).join('')); }
  await consumeChunks(chunks(), frame => reducer.apply(JSON.parse(frame.data)), { afterChunk: () => reducer.flush() });
  assert.equal(seen.length, 1);
  assert.equal(seen[0].blocks[0].text, 'AB');
});
test('aborted consumers do not apply a subsequent chunk', async () => {
  const controller = new AbortController();
  const seen = [];
  async function* chunks() { yield bytes('data: 1\n\n'); controller.abort(); yield bytes('data: 2\n\n'); }
  await assert.rejects(consumeChunks(chunks(), frame => seen.push(frame.data), { signal: controller.signal }));
  assert.deepEqual(seen, ['1']);
});
