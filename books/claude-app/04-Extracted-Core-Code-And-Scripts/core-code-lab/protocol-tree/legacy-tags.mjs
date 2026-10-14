/** Original bounded legacy-tag recognizer for the two observed exact spellings.
 * It yields data objects; it never creates HTML or runs artifact content. */
export class LegacyTagStream {
  #buffer = '';
  #mode = 'text';
  #attributes = {};
  #body = '';
  #closed = false;
  #limit;
  #headerScan = 12;
  #headerQuoted = false;
  constructor({ maxBufferedCharacters = 1_048_576 } = {}) {
    if (!Number.isSafeInteger(maxBufferedCharacters) || maxBufferedCharacters < 0) throw new RangeError('Invalid size limit');
    this.#limit = maxBufferedCharacters;
  }
  get limit() { return this.#limit; }

  push(text, { final = false } = {}) {
    if (this.#closed) throw new Error('Tag parser closed');
    if (typeof text !== 'string') throw new TypeError('Expected decoded text');
    const output = [];
    try {
      // Admit retained state one UTF-16 code unit at a time. Chunk size must not
      // decide whether otherwise identical content exceeds the state budget.
      for (let i = 0; i < text.length; i++) {
        this.#buffer += text[i];
        this.#consume(output, false);
      }
      if (final) { this.#consume(output, true); this.#closed = true; }
      return output;
    } catch (error) {
      this.#closed = true; this.#buffer = ''; this.#body = ''; this.#attributes = {};
      throw error;
    }
  }

  #consume(output, final) {
    const emitText = value => {
      if (!value) return;
      if (output.at(-1)?.type === 'text') output.at(-1).text += value;
      else output.push({ type: 'text', text: value });
    };
    while (this.#buffer) {
      if (this.#buffer.length + this.#body.length > this.limit) throw new RangeError('Tag buffer limit');
      if (this.#mode !== 'text') {
        const close = this.#mode === 'thinking' ? '</antThinking>' : '</antArtifact>';
        const index = this.#buffer.indexOf(close);
        if (index < 0) {
          // Keep a suffix that might become the closing tag on the next push.
          let keep = 0;
          if (!final) for (let n = 1; n < close.length; n++) if (this.#buffer.endsWith(close.slice(0, n))) keep = n;
          this.#body += this.#buffer.slice(0, this.#buffer.length - keep);
          this.#buffer = keep ? this.#buffer.slice(-keep) : '';
          if (final) this.#finish(output, false);
          break;
        }
        this.#body += this.#buffer.slice(0, index);
        this.#buffer = this.#buffer.slice(index + close.length);
        this.#finish(output, true);
        continue;
      }
      const index = this.#buffer.indexOf('<');
      if (index < 0) { emitText(this.#buffer); this.#buffer = ''; break; }
      emitText(this.#buffer.slice(0, index));
      this.#buffer = this.#buffer.slice(index);
      const starts = ['<antThinking>', '<antArtifact'];
      if (!final && starts.some(tag => tag.startsWith(this.#buffer))) break;
      if (this.#buffer.startsWith('<antThinking>')) {
        this.#mode = 'thinking';
        this.#buffer = this.#buffer.slice('<antThinking>'.length);
        continue;
      }
      if (/^<antArtifact(?:\s|>)/.test(this.#buffer)) {
        let end = -1;
        for (let i = this.#headerScan; i < this.#buffer.length; i++) {
          const character = this.#buffer[i];
          if (character === '"') this.#headerQuoted = !this.#headerQuoted;
          else if (character === '>' && !this.#headerQuoted) { end = i; break; }
        }
        this.#headerScan = this.#buffer.length;
        if (end < 0 && !final) break;
        if (end >= 0) {
          this.#attributes = {};
          const header = this.#buffer.slice(0, end);
          for (const match of header.matchAll(/([A-Za-z_]+)="([^"]*)"/g)) this.#attributes[match[1]] = match[2];
          this.#headerScan = 12;
          this.#headerQuoted = false;
          this.#mode = 'artifact';
          this.#buffer = this.#buffer.slice(end + 1);
          continue;
        }
      }
      // Unknown tags are ordinary text in this data-only recognizer.
      emitText('<');
      this.#buffer = this.#buffer.slice(1);
    }
    if (final && this.#mode !== 'text') this.#finish(output, false);
  }

  #finish(output, closed) {
    if (this.#mode === 'artifact') output.push({ type: 'artifact', attributes: { ...this.#attributes },
      content: this.#body, closed });
    // Thinking content is deliberately omitted from visible legacy text.
    this.#body = '';
    this.#attributes = {};
    this.#mode = 'text';
  }
}
