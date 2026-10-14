/** Original bounded teaching parsers. Data output only; no DOM or execution. */
function sizeLimit(value) {
  if (!Number.isSafeInteger(value) || value < 0) throw new RangeError('Invalid size limit');
  return value;
}
export class SSEDecoder {
  #decoder = new TextDecoder('utf-8', { fatal: true }); #line = ''; #cr = false;
  #data = []; #event = ''; #size = 0; #closed = false;
  #maxLine; #maxEvent;
  lastEventId = ''; retry = undefined;
  constructor({ maxLine = 65_536, maxEvent = 262_144 } = {}) {
    this.#maxLine = sizeLimit(maxLine); this.#maxEvent = sizeLimit(maxEvent);
  }
  get maxLine() { return this.#maxLine; }
  get maxEvent() { return this.#maxEvent; }
  push(bytes) {
    if (this.#closed) throw new Error('Decoder closed');
    try { return this.#consume(this.#decoder.decode(bytes, { stream: true })); }
    catch (error) { this.#close(); throw error; }
  }
  #consume(text) {
    const out = [];
    for (const c of text) {
      if (this.#cr) { this.#cr = false; if (c === '\n') continue; }
      if (c === '\r' || c === '\n') { this.#finishLine(out); this.#cr = c === '\r'; }
      else { this.#line += c; if (this.#line.length > this.maxLine) throw new RangeError('Line budget exceeded'); }
    }
    return out;
  }
  #finishLine(out) {
    const line = this.#line; this.#line = '';
    if (line === '') {
      if (this.#data.length) out.push({ event: this.#event || 'message', data: this.#data.join('\n'), id: this.lastEventId });
      this.#data = []; this.#event = ''; this.#size = 0; return;
    }
    this.#size += line.length;
    if (this.#size > this.maxEvent) throw new RangeError('Event budget exceeded');
    if (line.startsWith(':')) return;
    const colon = line.indexOf(':'), field = colon < 0 ? line : line.slice(0, colon);
    let value = colon < 0 ? '' : line.slice(colon + 1); if (value.startsWith(' ')) value = value.slice(1);
    if (field === 'data') this.#data.push(value);
    else if (field === 'event') this.#event = value;
    else if (field === 'id' && !value.includes('\0')) this.lastEventId = value;
    else if (field === 'retry' && /^\d+$/.test(value) && Number.isSafeInteger(Number(value))) this.retry = Number(value);
  }
  finish() {
    if (this.#closed) return [];
    try { return this.#consume(this.#decoder.decode()); }
    finally { this.#close(); }
  }
  #close() {
    this.#closed = true; this.#line = ''; this.#data = []; this.#event = ''; this.#size = 0;
  }
}

export class LegacyTags {
  #buffer = ''; #mode = 'text'; #body = ''; #attrs = {}; #closed = false;
  #headerScan = 12; #headerQuoted = false;
  #limit;
  constructor({ limit = 262_144 } = {}) { this.#limit = sizeLimit(limit); }
  get limit() { return this.#limit; }
  push(chunk, { final = false } = {}) {
    if (this.#closed) throw new Error('Tag parser closed');
    if (typeof chunk !== 'string') throw new TypeError('Expected decoded text');
    const out = [];
    try {
      // Process UTF-16 code units uniformly, regardless of caller chunk boundaries.
      // Only unconsumed state counts against the limit, never a whole network chunk.
      for (let i = 0; i < chunk.length; i++) {
        this.#buffer += chunk[i]; this.#consume(out, false);
      }
      if (final) this.#consume(out, true);
      return out;
    } catch (error) {
      this.#closed = true; this.#buffer = ''; this.#body = ''; this.#attrs = {};
      throw error;
    }
  }
  #consume(out, final) {
    const emit = text => {
      if (!text) return;
      if (out.at(-1)?.type === 'text') out.at(-1).text += text;
      else out.push({ type: 'text', text });
    };
    while (this.#buffer) {
      if (this.#buffer.length + this.#body.length > this.limit) throw new RangeError('Tag budget exceeded');
      if (this.#mode !== 'text') {
        const end = this.#mode === 'thinking' ? '</antThinking>' : '</antArtifact>';
        const pos = this.#buffer.indexOf(end);
        if (pos < 0) {
          let keep = 0;
          if (!final) for (let n = 1; n < end.length; n++) if (this.#buffer.endsWith(end.slice(0, n))) keep = n;
          this.#body += this.#buffer.slice(0, this.#buffer.length - keep);
          this.#buffer = keep ? this.#buffer.slice(-keep) : '';
          break;
        }
        this.#body += this.#buffer.slice(0, pos); this.#buffer = this.#buffer.slice(pos + end.length);
        this.#finish(out, true); continue;
      }
      const lt = this.#buffer.indexOf('<');
      if (lt < 0) { emit(this.#buffer); this.#buffer = ''; break; }
      emit(this.#buffer.slice(0, lt)); this.#buffer = this.#buffer.slice(lt);
      const starts = ['<antThinking>', '<antArtifact'];
      if (starts.some(s => s.startsWith(this.#buffer))) {
        if (!final) break;
        this.#buffer = ''; break; // suppress incomplete reserved openers at EOF
      }
      if (this.#buffer.startsWith('<antThinking>')) {
        this.#mode = 'thinking'; this.#buffer = this.#buffer.slice(13); continue;
      }
      if (/^<antArtifact(?:\s|>)/.test(this.#buffer)) {
        let end = -1;
        for (let i = this.#headerScan; i < this.#buffer.length; i++) {
          const c = this.#buffer[i]; if (c === '"') this.#headerQuoted = !this.#headerQuoted;
          else if (c === '>' && !this.#headerQuoted) { end = i; break; }
        }
        this.#headerScan = this.#buffer.length;
        if (end < 0) { if (final) this.#buffer = ''; break; }
        let rest = this.#buffer.slice(12, end); const attrs = Object.create(null);
        while (rest.trim()) {
          const m = /^\s+([A-Za-z_][\w-]*)="([^"]*)"/.exec(rest);
          if (!m || Object.hasOwn(attrs, m[1])) throw new Error('Unsupported or duplicate attribute');
          attrs[m[1]] = m[2]; rest = rest.slice(m[0].length);
        }
        this.#attrs = attrs; this.#mode = 'artifact'; this.#buffer = this.#buffer.slice(end + 1);
        this.#headerScan = 12; this.#headerQuoted = false; continue;
      }
      emit('<'); this.#buffer = this.#buffer.slice(1);
    }
    if (final) { if (this.#mode !== 'text') this.#finish(out, false); this.#closed = true; }
  }
  #finish(out, closed) {
    if (this.#mode === 'artifact') out.push({ type: 'artifact', attributes: { ...this.#attrs }, content: this.#body, closed });
    this.#mode = 'text'; this.#body = ''; this.#attrs = {};
  }
}

export class JsonAssembly {
  #text = ''; #limit; #failed = false;
  constructor(limit = 65_536) { this.#limit = sizeLimit(limit); }
  get limit() { return this.#limit; }
  append(fragment) {
    if (this.#failed) throw new Error('JSON assembly failed');
    if (typeof fragment !== 'string') throw new TypeError('JSON fragment must be text');
    if (this.#text.length + fragment.length > this.limit) {
      this.#failed = true; this.#text = ''; throw new RangeError('JSON budget exceeded');
    }
    this.#text += fragment;
  }
  finish() {
    if (this.#failed) throw new Error('JSON assembly failed');
    const value = JSON.parse(this.#text);
    if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error('Expected object');
    return value;
  }
}
