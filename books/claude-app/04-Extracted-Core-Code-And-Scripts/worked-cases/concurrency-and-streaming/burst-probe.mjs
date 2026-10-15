import { IncrementalSSE, consumeChunks } from './existing-models.mjs';

export async function measureBurst(count = 20_000) {
  const bytes = new TextEncoder().encode('data: x\n\n'.repeat(count));
  const decoder = new IncrementalSSE({ maxLineCharacters: 8, maxEventCharacters: 8 });
  const frameCount = decoder.push(bytes).length;
  let delivered = 0, firstAfterChunkAfter = null;
  await consumeChunks((async function* () { yield bytes; })(), () => { delivered++; }, {
    afterChunk() { firstAfterChunkAfter ??= delivered; }
  });
  return { bytes: bytes.length, perLineLimit: 8, perEventLimit: 8,
    framesReturnedBeforeFirstCallback: frameCount, delivered, firstAfterChunkAfter };
}

if (process.argv[1] && new URL(import.meta.url).pathname === process.argv[1])
  console.log(JSON.stringify(await measureBurst(), null, 2));
