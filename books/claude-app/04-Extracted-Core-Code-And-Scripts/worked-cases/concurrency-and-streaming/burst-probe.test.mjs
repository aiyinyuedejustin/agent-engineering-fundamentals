import test from 'node:test';
import assert from 'node:assert/strict';
import { measureBurst } from './burst-probe.mjs';
import { IncrementalSSE } from './existing-models.mjs';

test('short valid events bypass per-event limits as an aggregate frame burst', async () => {
  assert.deepEqual(await measureBurst(), { bytes: 180000, perLineLimit: 8,
    perEventLimit: 8, framesReturnedBeforeFirstCallback: 20000,
    delivered: 20000, firstAfterChunkAfter: 20000 });
});

test('small byte slices preserve framing, including split UTF-8 and CRLF', () => {
  const bytes = new TextEncoder().encode('data: 资料😀\r\n\r\ndata: next\n\n');
  const whole = new IncrementalSSE(), expected = [...whole.push(bytes), ...whole.finish()];
  for (const size of [1, 2, 3, 4, 7, 16]) {
    const split = new IncrementalSSE(), actual = [];
    for (let i = 0; i < bytes.length; i += size) actual.push(...split.push(bytes.subarray(i, i + size)));
    actual.push(...split.finish());
    assert.deepEqual(actual, expected);
  }
});
