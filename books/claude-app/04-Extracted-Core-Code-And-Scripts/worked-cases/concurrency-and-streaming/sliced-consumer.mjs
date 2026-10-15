/** Original teaching ADAPTER around the book's original IncrementalSSE.
 * This bounds parser calls and callback runs, not total retained memory or time.
 * No network, target code, or production parser replacement. For complete input
 * within decoder limits, frames are preserved in order until cancellation/error.
 * Caller-owned ordinary ArrayBuffer bytes are BORROWED: no holder may mutate,
 * reuse, or detach the current chunk until next() is requested or consumption
 * ends. Concurrently mutated SharedArrayBuffer storage is outside this contract.
 * Abort is checked only after pending next/onFrame/yield promises settle.
 * On parse failure, the delivered prefix can differ with push slice boundaries;
 * prior callback effects are not rolled back. This is not batch atomicity.
 */
import { IncrementalSSE } from './existing-models.mjs';

function positiveInteger(value, name) {
  if (!Number.isSafeInteger(value) || value <= 0) throw new RangeError(`Invalid ${name}`);
  return value;
}

export async function consumeInSlices(chunks, onFrame, {
  sliceBytes = 4096, frameQuantum = 128, signal, decoderLimits,
  yieldToLoop = () => new Promise(resolve => setTimeout(resolve, 0)),
} = {}) {
  positiveInteger(sliceBytes, 'sliceBytes');
  positiveInteger(frameQuantum, 'frameQuantum');
  if (typeof onFrame !== 'function' || typeof yieldToLoop !== 'function')
    throw new TypeError('Callbacks must be functions');
  const decoder = new IncrementalSSE(decoderLimits);
  const stats = { receivedBytes: 0, delivered: 0, pushes: 0, maxPushBytes: 0,
    maxFramesReturned: 0, yields: 0, maxCallbacksBetweenYields: 0,
    callbacksBeforeFirstYield: null };
  let callbacks = 0;
  const check = () => signal?.throwIfAborted();
  async function yieldNow() {
    stats.maxCallbacksBetweenYields = Math.max(stats.maxCallbacksBetweenYields, callbacks);
    stats.callbacksBeforeFirstYield ??= stats.delivered;
    callbacks = 0;
    stats.yields++;
    check();
    await yieldToLoop();
    check();
  }
  async function deliver(frames) {
    stats.maxFramesReturned = Math.max(stats.maxFramesReturned, frames.length);
    for (const frame of frames) {
      check();
      const result = onFrame(frame);
      if (result != null && typeof result.then === 'function') await result;
      stats.delivered++;
      callbacks++;
      check();
      if (callbacks >= frameQuantum) await yieldNow();
    }
  }

  try {
    check();
    for await (const chunk of chunks) {
      check();
      if (!(chunk instanceof Uint8Array)) throw new TypeError('Expected Uint8Array chunk');
      stats.receivedBytes += chunk.byteLength;
      for (let offset = 0; offset < chunk.byteLength; offset += sliceBytes) {
        check();
        // A subarray keeps the original backing storage alive. This is NOT a
        // claim that upstream memory has been freed or capped by sliceBytes.
        const slice = chunk.subarray(offset, offset + sliceBytes);
        stats.pushes++;
        stats.maxPushBytes = Math.max(stats.maxPushBytes, slice.byteLength);
        await deliver(decoder.push(slice));
        // Parse-only input (a long unfinished field, comments, etc.) must also
        // have a checkpoint, even when this slice produced no complete frame.
        await yieldNow();
      }
    }
    check();
    await deliver(decoder.finish());
    stats.maxCallbacksBetweenYields = Math.max(stats.maxCallbacksBetweenYields, callbacks);
    return stats;
  } finally {
    // The adapter owns its decoder. Discard incomplete state on error/abort;
    // finish() is idempotent in the existing book model. Never deliver here.
    // Flushing an incomplete UTF-8 code point can itself violate a configured
    // line limit. Cleanup must not replace the real abort/callback error.
    try { decoder.finish(); } catch { /* discard only: never resume delivery */ }
  }
}
