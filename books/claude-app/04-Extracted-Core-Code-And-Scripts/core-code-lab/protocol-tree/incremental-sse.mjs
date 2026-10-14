/** Original teaching implementation. No network endpoints or target imports. */
function sizeLimit(value) {
  if (!Number.isSafeInteger(value) || value < 0) throw new RangeError('Invalid size limit');
  return value;
}

export class IncrementalSSE {
  #decoder = new TextDecoder();
  #line = '';
  #afterCR = false;
  #event = this.#blank();
  #eventCharacters = 0;
  #closed = false;
  #maxLineCharacters;
  #maxEventCharacters;

  constructor({ maxLineCharacters = 1_048_576, maxEventCharacters = 4_194_304 } = {}) {
    this.#maxLineCharacters = sizeLimit(maxLineCharacters);
    this.#maxEventCharacters = sizeLimit(maxEventCharacters);
    this.lastEventId = '';
    this.retryMilliseconds = undefined;
  }

  get maxLineCharacters() { return this.#maxLineCharacters; }
  get maxEventCharacters() { return this.#maxEventCharacters; }

  #blank() { return { event: '', data: [], id: undefined, retry: undefined }; }

  push(bytes) {
    if (this.#closed) throw new Error('The decoder is closed');
    try { return this.#consume(this.#decoder.decode(bytes, { stream: true })); }
    catch (error) { this.#close(); throw error; }
  }

  #consume(text) {
    const frames = [];
    for (const character of text) {
      if (this.#afterCR) {
        this.#afterCR = false;
        if (character === '\n') continue;
      }
      if (character === '\r' || character === '\n') {
        this.#finishLine(frames);
        this.#afterCR = character === '\r';
      } else {
        this.#line += character;
        if (this.#line.length > this.maxLineCharacters) throw new RangeError('SSE line limit');
        if (this.#eventCharacters + this.#line.length > this.maxEventCharacters) throw new RangeError('SSE event limit');
      }
    }
    return frames;
  }

  #finishLine(frames) {
    const line = this.#line;
    this.#line = '';
    if (line === '') {
      // Match the inspected framing behavior: a blank line completes a frame,
      // even if it carries no data. Consumers may ignore empty frames.
      frames.push({ ...this.#event, data: this.#event.data.join('\n') });
      this.#event = this.#blank();
      this.#eventCharacters = 0;
      return;
    }
    this.#eventCharacters += line.length;
    if (this.#eventCharacters > this.maxEventCharacters) throw new RangeError('SSE event limit');
    const colon = line.indexOf(':');
    if (colon <= 0) return; // Comment lines and unrecognized no-colon lines.
    const field = line.slice(0, colon);
    const value = line.slice(colon + (line[colon + 1] === ' ' ? 2 : 1));
    if (field === 'data') this.#event.data.push(value);
    if (field === 'event') this.#event.event = value;
    if (field === 'id' && !value.includes('\0')) {
      this.lastEventId = value;
      this.#event.id = value;
    }
    // Deliberately stricter than the inspected parseInt-based retry field.
    if (field === 'retry' && /^\d+$/.test(value)) {
      this.retryMilliseconds = Number(value);
      this.#event.retry = this.retryMilliseconds;
    }
  }

  finish() {
    if (this.#closed) return [];
    try { return this.#consume(this.#decoder.decode()); }
    finally { this.#close(); }
  }

  #close() {
    this.#closed = true;
    // EOF and failures discard incomplete state rather than reviving it later.
    this.#line = '';
    this.#event = this.#blank();
    this.#eventCharacters = 0;
    this.#afterCR = false;
  }
}

/** Await the consumer before requesting another chunk. This is local read pacing,
 * not a promise that upstream TCP buffers or the model itself stop producing. */
export async function consumeChunks(chunks, onFrame, {
  decoder = new IncrementalSSE(), afterChunk = () => {}, signal,
} = {}) {
  signal?.throwIfAborted();
  for await (const chunk of chunks) {
    signal?.throwIfAborted();
    for (const frame of decoder.push(chunk)) {
      signal?.throwIfAborted();
      const result = onFrame(frame);
      // Do not create a microtask gap for a synchronous frame callback: all
      // events in this chunk can coalesce before the afterChunk boundary.
      if (result != null && typeof result.then === 'function') await result;
      signal?.throwIfAborted();
    }
    await afterChunk();
    signal?.throwIfAborted();
  }
  signal?.throwIfAborted();
  for (const frame of decoder.finish()) {
    signal?.throwIfAborted();
    const result = onFrame(frame);
    if (result != null && typeof result.then === 'function') await result;
    signal?.throwIfAborted();
  }
}

export function makeWorkBudget({ milliseconds = 8, now = () => performance.now(),
  yieldToLoop = () => new Promise(resolve => setTimeout(resolve, 0)) } = {}) {
  let start = now();
  return async () => {
    if (now() - start < milliseconds) return;
    await yieldToLoop();
    start = now();
  };
}
