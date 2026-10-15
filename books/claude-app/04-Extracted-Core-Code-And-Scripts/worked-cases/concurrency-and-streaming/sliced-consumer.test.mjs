import test from 'node:test';
import assert from 'node:assert/strict';
import { consumeInSlices } from './sliced-consumer.mjs';
import { IncrementalSSE } from './existing-models.mjs';
const encode = text => new TextEncoder().encode(text);
async function* one(bytes) { yield bytes; }

test('a large valid burst reaches a checkpoint after at most the frame quantum', async () => {
  const count = 20_000, seen = [];
  const stats = await consumeInSlices(one(encode('data: x\n\n'.repeat(count))),
    f => seen.push(f.data), { yieldToLoop: async () => {} });
  assert.equal(seen.length, count);
  assert.ok(seen.every(x => x === 'x'));
  assert.equal(stats.maxPushBytes, 4096);
  assert.equal(stats.callbacksBeforeFirstYield, 128);
  assert.ok(stats.maxCallbacksBetweenYields <= 128);
  assert.ok(stats.maxFramesReturned <= 4096);
});

test('byte slicing and upstream chunking preserve UTF-8, CRLF, IDs and terminal frames', async () => {
  const bytes = encode('id: 1\r\nevent: delta\r\ndata: 资料😀\r\n\r\nid: 2\nevent: stop\ndata: done\n\n');
  const original = new IncrementalSSE(), expected = [...original.push(bytes), ...original.finish()];
  for (let cut = 0; cut <= bytes.length; cut++) {
    for (const size of [1, 2, 3, 7, 16]) {
      const got = [];
      async function* split() { yield bytes.subarray(0, cut); yield bytes.subarray(cut); }
      await consumeInSlices(split(), frame => got.push(frame), {
        sliceBytes: size, frameQuantum: 1, yieldToLoop: async () => {}
      });
      assert.deepEqual(got, expected);
    }
  }
});

test('parse-only input yields without waiting for a completed event', async () => {
  let yielded = 0;
  const stats = await consumeInSlices(one(encode('data: ' + 'x'.repeat(100))), () => {
    assert.fail('EOF must not manufacture a frame');
  }, { sliceBytes: 8, yieldToLoop: async () => { yielded++; } });
  assert.equal(stats.delivered, 0);
  assert.equal(yielded, 14);
  assert.equal(stats.callbacksBeforeFirstYield, 0);
});

test('abort during the first yield prevents remaining frames in the same chunk', async () => {
  const controller = new AbortController();
  let calls = 0, returned = false;
  async function* source() { try { yield encode('data: x\n\n'.repeat(50)); } finally { returned = true; } }
  await assert.rejects(consumeInSlices(source(), () => { calls++; }, {
    frameQuantum: 3, signal: controller.signal,
    yieldToLoop: async () => { controller.abort(); }
  }), { name: 'AbortError' });
  assert.equal(calls, 3);
  assert.equal(returned, true);
});

test('abort inside a synchronous frame callback blocks the following callback', async () => {
  const controller = new AbortController(); let calls = 0;
  await assert.rejects(consumeInSlices(one(encode('data: a\n\ndata: b\n\n')), () => {
    calls++; controller.abort();
  }, { signal: controller.signal, yieldToLoop: async () => {} }), { name: 'AbortError' });
  assert.equal(calls, 1);
});

test('the original per-event character limit still applies across small slices', async () => {
  await assert.rejects(consumeInSlices(one(encode('data: too-long\n\n')), () => {}, {
    sliceBytes: 1, decoderLimits: { maxLineCharacters: 8, maxEventCharacters: 8 },
    yieldToLoop: async () => {}
  }), /SSE line limit/);
});

test('invalid quanta fail before requesting input', async () => {
  let read = false;
  async function* source() { read = true; yield encode('data: x\n\n'); }
  for (const value of [0, -1, NaN, Infinity, 1.5]) {
    await assert.rejects(consumeInSlices(source(), () => {}, { sliceBytes: value }), RangeError);
    await assert.rejects(consumeInSlices(source(), () => {}, { frameQuantum: value }), RangeError);
  }
  assert.equal(read, false);
});

test('async frame callbacks complete in sequence before the next is delivered', async () => {
  const log = [];
  await consumeInSlices(one(encode('data: a\n\ndata: b\n\n')), async frame => {
    log.push('start-' + frame.data); await Promise.resolve(); log.push('end-' + frame.data);
  }, { yieldToLoop: async () => {} });
  assert.deepEqual(log, ['start-a', 'end-a', 'start-b', 'end-b']);
});

test('callback failure closes the source and never delivers a following frame', async () => {
  const error = new Error('CALLBACK_FAILED'); let calls = 0, closed = false;
  async function* source() { try { yield encode('data: a\n\ndata: b\n\n'); } finally { closed = true; } }
  await assert.rejects(consumeInSlices(source(), () => { calls++; throw error; }), value => value === error);
  assert.equal(calls, 1);
  assert.equal(closed, true);
});

test('scheduler failure stops consumption and closes the source', async () => {
  const error = new Error('SCHEDULER_FAILED'); let closed = false, calls = 0;
  async function* source() { try { yield encode('data: a\n\ndata: b\n\n'); } finally { closed = true; } }
  await assert.rejects(consumeInSlices(source(), () => { calls++; }, {
    frameQuantum: 1, yieldToLoop: async () => { throw error; }
  }), value => value === error);
  assert.equal(calls, 1);
  assert.equal(closed, true);
});

test('cleanup of incomplete UTF-8 cannot replace the original abort reason', async () => {
  const controller = new AbortController(), reason = new Error('ORIGINAL_ABORT');
  await assert.rejects(consumeInSlices(one(Uint8Array.of(0xe4)), () => {}, {
    sliceBytes: 1, decoderLimits: { maxLineCharacters: 0, maxEventCharacters: 0 },
    signal: controller.signal, yieldToLoop: async () => controller.abort(reason)
  }), value => value === reason);
});
