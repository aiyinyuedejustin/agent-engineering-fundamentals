import test from 'node:test';
import assert from 'node:assert/strict';
import { SSEDecoder, LegacyTags, JsonAssembly } from './parser.mjs';
test('UTF-8, CRLF and multi-line data survive every byte split', () => {
  const bytes = new TextEncoder().encode(': comment\r\nid: 7\r\nevent: piece\r\ndata: 中文\r\ndata: 🙂\r\n\r\n');
  for (let i = 0; i <= bytes.length; i++) {
    const p = new SSEDecoder(), frames = [...p.push(bytes.slice(0, i)), ...p.push(bytes.slice(i)), ...p.finish()];
    assert.deepEqual(frames, [{ event: 'piece', data: '中文\n🙂', id: '7' }]);
  }
});
test('SSE EOF, budget and no-colon empty data have explicit behavior', () => {
  const e = s => new TextEncoder().encode(s), p = new SSEDecoder();
  assert.deepEqual(p.push(e('data: unfinished')), []); assert.deepEqual(p.finish(), []);
  assert.deepEqual(new SSEDecoder().push(e('data\n\n')), [{ event: 'message', data: '', id: '' }]);
  assert.throws(() => new SSEDecoder({ maxLine: 2 }).push(e('abc')), /budget/);
});
test('legacy tag meaning survives every split, including > inside quoted attributes', () => {
  const s = 'Before<antThinking>private</antThinking><antArtifact title="a > b">中文</antArtifact>After';
  for (let i = 0; i <= s.length; i++) {
    const p = new LegacyTags(), events = [...p.push(s.slice(0, i)), ...p.push(s.slice(i), { final: true })];
    assert.equal(events.filter(e => e.type === 'text').map(e => e.text).join(''), 'BeforeAfter');
    assert.deepEqual(events.filter(e => e.type === 'artifact'), [{ type: 'artifact', attributes: { title: 'a > b' }, content: '中文', closed: true }]);
  }
});
test('partial artifacts stay incomplete; reserved prefixes and thinking stay invisible', () => {
  assert.deepEqual(new LegacyTags().push('<antArtifact>open', { final: true }), [{ type: 'artifact', attributes: {}, content: 'open', closed: false }]);
  assert.deepEqual(new LegacyTags().push('<antThink', { final: true }), []);
  assert.deepEqual(new LegacyTags().push('<antThinking>hidden', { final: true }), []);
  assert.throws(() => new LegacyTags({ limit: 2 }).push('<ant'), /budget/);
  assert.throws(() => new LegacyTags().push('<antArtifact x="1" x="2">'), /duplicate/);
});
test('JSON is complete and object-shaped before promotion', () => {
  const p = new JsonAssembly(); p.append('{"path":'); assert.throws(() => p.finish());
  p.append('"notes.txt"}'); assert.deepEqual(p.finish(), { path: 'notes.txt' });
  const q = new JsonAssembly(); q.append('[]'); assert.throws(() => q.finish(), /object/);
});
test('legacy retained-state budget is independent of chunk size', () => {
  const artifact = '<antArtifact>x</antArtifact>', source = `ab${artifact}${artifact}cd`;
  const expected = new LegacyTags({ limit: 28 }).push(source, { final: true });
  const normalized = events => ({
    text: events.filter(e => e.type === 'text').map(e => e.text).join(''),
    artifacts: events.filter(e => e.type === 'artifact'),
  });
  for (let i = 0; i <= source.length; i++) {
    for (let j = i; j <= source.length; j++) {
      const p = new LegacyTags({ limit: 28 });
      const actual = [...p.push(source.slice(0, i)), ...p.push(source.slice(i, j)), ...p.push(source.slice(j), { final: true })];
      assert.deepEqual(normalized(actual), normalized(expected));
    }
  }
  assert.deepEqual(new LegacyTags({ limit: 2 }).push('abcd', { final: true }), [{ type: 'text', text: 'abcd' }]);
  // The body and undecided closing delimiter share the retained-state budget.
  for (let i = 0; i <= artifact.length; i++) {
    const p = new LegacyTags({ limit: 14 });
    assert.throws(() => { p.push(artifact.slice(0, i)); p.push(artifact.slice(i), { final: true }); }, /budget/);
  }
});
test('all parser size limits reject invalid configurations', () => {
  for (const limit of [-1, 0.5, NaN, Infinity, '20', null]) {
    assert.throws(() => new SSEDecoder({ maxLine: limit }), /limit/);
    assert.throws(() => new SSEDecoder({ maxEvent: limit }), /limit/);
    assert.throws(() => new LegacyTags({ limit }), /limit/);
    assert.throws(() => new JsonAssembly(limit), /limit/);
  }
});
test('budget failures terminate their parser path instead of emitting rejected data later', () => {
  const encode = text => new TextEncoder().encode(text);
  const sse = new SSEDecoder({ maxLine: 6 });
  assert.throws(() => sse.push(encode('data: a')), /budget/);
  assert.throws(() => sse.push(encode('\n\n')), /closed/); assert.deepEqual(sse.finish(), []);
  const tags = new LegacyTags({ limit: 2 });
  assert.throws(() => tags.push('<ant'), /budget/);
  assert.throws(() => tags.push('Artifact>'), /closed/);
  const json = new JsonAssembly(2); json.append('{}');
  assert.throws(() => json.append(' '), /budget/);
  assert.throws(() => json.finish(), /failed/); assert.throws(() => json.append(''), /failed/);
});
test('SSE line/event and JSON limits admit the exact boundary', () => {
  const encode = text => new TextEncoder().encode(text);
  assert.deepEqual(new SSEDecoder({ maxLine: 6, maxEvent: 6 }).push(encode('data:a\n\n')),
    [{ event: 'message', data: 'a', id: '' }]);
  assert.throws(() => new SSEDecoder({ maxEvent: 5 }).push(encode('data:a\n\n')), /budget/);
  const json = new JsonAssembly(2); json.append('{}'); assert.deepEqual(json.finish(), {});
  assert.deepEqual(new SSEDecoder({ maxLine: 0, maxEvent: 0 }).push(encode('\n')), []);
  assert.deepEqual(new LegacyTags({ limit: 0 }).push('', { final: true }), []);
});
test('long quoted headers retain incremental quote scanning across chunks', () => {
  const title = `${'x'.repeat(8_192)} > end`, p = new LegacyTags();
  assert.deepEqual(p.push(`<antArtifact title="${title.slice(0, 4_000)}`), []);
  const events = p.push(`${title.slice(4_000)}">ok</antArtifact>`, { final: true });
  assert.deepEqual(events, [{ type: 'artifact', attributes: { title }, content: 'ok', closed: true }]);
});
