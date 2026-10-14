// Original educational protocol model. No product code, renderer, or isolation implementation.
export const PROTOCOL = 'preview-demo/1';
export class ProtocolError extends Error {
  constructor(code) { super(code); this.name = 'ProtocolError'; this.code = code; }
}
const fail = code => new ProtocolError(code);
// Only this model's bounded public codes may cross the capability boundary.
const PUBLIC_ERROR_CODES = new Set(['BAD_BOUNDARY', 'BAD_DEADLINE', 'BAD_GENERATION', 'BAD_LIMIT', 'BAD_MESSAGE', 'BAD_METHOD', 'BAD_PAYLOAD', 'BAD_RESULT', 'BAD_STATE', 'BUSY', 'DENIED', 'DISPOSED', 'DUPLICATE', 'EXHAUSTED_SEQUENCE', 'HANDLER_FAILED', 'MESSAGE_ERROR', 'NOT_CONNECTED', 'RATE_LIMIT', 'REMOTE_ERROR', 'SEND_FAILED', 'SESSION_BUDGET', 'STALE', 'TIMEOUT']);
const publicErrorCode = error => error instanceof ProtocolError && PUBLIC_ERROR_CODES.has(error.code)
  ? error.code : 'HANDLER_FAILED';
const object = value => value !== null && typeof value === 'object' &&
  (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
const exact = (value, keys) => object(value) && Object.keys(value).length === keys.length &&
  keys.every(key => Object.hasOwn(value, key));
const integer = value => Number.isSafeInteger(value) && value >= 0;
const id = value => typeof value === 'string' && /^[A-Za-z0-9_-]{1,64}$/.test(value);
const token = value => typeof value === 'string' && /^[A-Za-z0-9_-]{16,128}$/.test(value);
const origin = value => {
  try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) && url.origin === value; }
  catch { return false; }
};
function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
function duration(value) {
  if (!Number.isFinite(value) || value < 1 || value > 60_000) throw fail('BAD_DEADLINE');
  return value;
}
const control = (data, kind, generation, nonce) => exact(data, ['protocol', 'kind', 'generation', 'nonce']) &&
  data.protocol === PROTOCOL && data.kind === kind && data.generation === generation && data.nonce === nonce;
const baseKeys = ['protocol', 'kind', 'id', 'generation', 'sequence', 'method'];
const base = data => object(data) && data.protocol === PROTOCOL && id(data.id) &&
  integer(data.generation) && data.generation > 0 && integer(data.sequence) &&
  typeof data.method === 'string' && data.method.length <= 40;
const request = data => base(data) && data.kind === 'request' && exact(data, [...baseKeys, 'payload']);
const response = data => base(data) && data.kind === 'response' && typeof data.ok === 'boolean' &&
  (data.ok ? exact(data, [...baseKeys, 'ok', 'payload']) :
    exact(data, [...baseKeys, 'ok', 'error']) && exact(data.error, ['code']) && id(data.error.code));
const contentPayload = value => exact(value, ['format', 'body']) &&
  ['html', 'react', 'svg', 'mermaid'].includes(value.format) &&
  typeof value.body === 'string' && value.body.length <= 65_536;
const readPayload = value => exact(value, ['key']) && typeof value.key === 'string' &&
  /^[A-Za-z0-9_-]{1,64}$/.test(value.key);
const contentResult = value => exact(value, ['applied']) && value.applied === true;
const pingResult = value => exact(value, ['alive']) && value.alive === true;

export class ContentGate {
  #generation; #sequence = 0; #acknowledged = false;
  constructor(generation) {
    if (!integer(generation) || generation === 0) throw fail('BAD_GENERATION');
    this.#generation = generation;
  }
  get generation() { return this.#generation; }
  get sequence() { return this.#sequence; }
  replace() {
    if (this.#sequence === Number.MAX_SAFE_INTEGER) throw fail('EXHAUSTED_SEQUENCE');
    this.#acknowledged = false;
    this.#sequence++;
    return this.receipt();
  }
  receipt() {
    return Object.freeze({ generation: this.#generation, sequence: this.#sequence, acknowledged: this.#acknowledged });
  }
  matches(receipt) {
    return receipt.generation === this.#generation && receipt.sequence === this.#sequence;
  }
  acknowledge(receipt) {
    if (!this.matches(receipt) || receipt.sequence === 0) return false;
    this.#acknowledged = true;
    return true;
  }
  permits(receipt) {
    return this.matches(receipt) && receipt.acknowledged && this.#acknowledged;
  }
  invalidate() { this.#acknowledged = false; }
}

export class SandboxHost {
  #frame; #origin; #nonce; #channelFactory; #authorize; #readText; #onDispose;
  #gate; #port = null; #state = 'new'; #ready = null; #handshakeTimer;
  #pending = new Map(); #inbound = new Map(); #seen = new Set(); #counter = 0;
  #defaultDeadline; #maxPending; #maxIds; #rate; #clock; #windowStart; #count = 0;
  constructor({ frameWindow, hostOrigin, rendererOrigin, generation, nonce,
    createChannel = () => new MessageChannel(), authorize = () => false,
    readText, onDispose = () => {}, deadlineMs = 1000,
    maxPending = 32, maxIds = 1024, rate = { limit: 100, intervalMs: 1000 },
    now = () => performance.now() }) {
    if (!frameWindow || typeof frameWindow.postMessage !== 'function' ||
        !origin(hostOrigin) || !origin(rendererOrigin) || rendererOrigin === hostOrigin || !token(nonce)) {
      throw fail('BAD_BOUNDARY');
    }
    if (![maxPending, maxIds, rate.limit, rate.intervalMs].every(n => Number.isSafeInteger(n) && n > 0)) {
      throw fail('BAD_LIMIT');
    }
    this.#frame = frameWindow; this.#origin = rendererOrigin; this.#nonce = nonce;
    this.#gate = new ContentGate(generation); this.#channelFactory = createChannel;
    this.#authorize = authorize; this.#readText = readText; this.#onDispose = onDispose;
    this.#defaultDeadline = duration(deadlineMs); this.#maxPending = maxPending; this.#maxIds = maxIds;
    this.#rate = { ...rate }; this.#clock = now; this.#windowStart = now();
  }
  get state() { return this.#state; }
  get generation() { return this.#gate.generation; }
  get sequence() { return this.#gate.sequence; }
  get pendingCount() { return this.#pending.size; }
  get inboundCount() { return this.#inbound.size; }
  get acknowledged() { return this.#gate.receipt().acknowledged; }
  #control(kind) { return { protocol: PROTOCOL, kind, generation: this.generation, nonce: this.#nonce }; }
  connect({ deadlineMs = this.#defaultDeadline } = {}) {
    if (this.#state !== 'new') return Promise.reject(fail('BAD_STATE'));
    duration(deadlineMs);
    this.#state = 'handshaking'; this.#ready = deferred();
    const result = this.#ready.promise;
    this.#handshakeTimer = setTimeout(() => this.dispose(fail('TIMEOUT')), deadlineMs);
    try { this.#frame.postMessage(this.#control('hello'), this.#origin); }
    catch { this.dispose(fail('SEND_FAILED')); }
    return result;
  }
  receiveWindow(event) {
    if (this.#state !== 'handshaking' || this.#port || event.source !== this.#frame ||
        event.origin !== this.#origin || (event.ports?.length ?? 0) !== 0 ||
        !control(event.data, 'ready', this.generation, this.#nonce)) return false;
    let channel;
    try {
      channel = this.#channelFactory();
      const port = channel.port1;
      this.#port = port;
      port.onmessage = event => this.#receivePort(event.data, port);
      port.onmessageerror = () => this.dispose(fail('MESSAGE_ERROR'));
      port.start();
      this.#frame.postMessage(this.#control('channel'), this.#origin, [channel.port2]);
      return true;
    } catch {
      try { channel?.port2.close(); } catch { /* Transfer failure still settles the session. */ }
      this.dispose(fail('SEND_FAILED'));
      return false;
    }
  }
  #receivePort(data, port) {
    if (this.#state === 'disposed' || port !== this.#port) return;
    const time = this.#clock();
    if (time - this.#windowStart >= this.#rate.intervalMs) { this.#windowStart = time; this.#count = 0; }
    if (++this.#count > this.#rate.limit) { this.dispose(fail('RATE_LIMIT')); return; }
    if (this.#state === 'handshaking') {
      if (!control(data, 'port-ready', this.generation, this.#nonce)) { this.dispose(fail('BAD_MESSAGE')); return; }
      this.#state = 'active'; clearTimeout(this.#handshakeTimer);
      this.#ready.resolve(); this.#ready = null;
      return;
    }
    if (response(data)) { this.#receiveResponse(data); return; }
    if (request(data)) { this.#receiveRequest(data); return; }
    this.dispose(fail('BAD_MESSAGE'));
  }
  #send(data) {
    try { this.#port.postMessage(data); return true; }
    catch { this.dispose(fail('SEND_FAILED')); return false; }
  }
  #outbound(method, payload, checkResult, receipt, deadlineMs) {
    if (this.#state !== 'active') return Promise.reject(fail('NOT_CONNECTED'));
    duration(deadlineMs);
    if (this.#pending.size >= this.#maxPending) return Promise.reject(fail('BUSY'));
    const requestId = `h_${++this.#counter}`;
    const entry = { ...deferred(), method, receipt, checkResult };
    entry.timer = setTimeout(() => this.#finishOutbound(requestId, fail('TIMEOUT')), deadlineMs);
    this.#pending.set(requestId, entry);
    this.#send({ protocol: PROTOCOL, kind: 'request', id: requestId,
      generation: receipt.generation, sequence: receipt.sequence, method, payload });
    return entry.promise;
  }
  #finishOutbound(requestId, error, value) {
    const entry = this.#pending.get(requestId);
    if (!entry) return;
    this.#pending.delete(requestId); clearTimeout(entry.timer);
    if (error) entry.reject(error); else entry.resolve(value);
  }
  #receiveResponse(data) {
    const entry = this.#pending.get(data.id);
    if (!entry || data.method !== entry.method || data.generation !== entry.receipt.generation ||
        data.sequence !== entry.receipt.sequence) return;
    if (!data.ok) { this.#finishOutbound(data.id, fail('REMOTE_ERROR')); return; }
    if (!entry.checkResult(data.payload)) { this.#finishOutbound(data.id, fail('BAD_PAYLOAD')); return; }
    this.#finishOutbound(data.id, null, data.payload);
  }
  async postContent(payload, { deadlineMs = this.#defaultDeadline } = {}) {
    if (this.#state !== 'active') throw fail('NOT_CONNECTED');
    if (!contentPayload(payload)) throw fail('BAD_PAYLOAD');
    duration(deadlineMs);
    const receipt = this.#gate.replace();
    this.#cancelWork(fail('STALE'));
    await this.#outbound('content.set', { ...payload }, contentResult, receipt, deadlineMs);
    if (this.#state !== 'active' || !this.#gate.acknowledge(receipt)) throw fail('STALE');
    return receipt.sequence;
  }
  ping({ deadlineMs = this.#defaultDeadline } = {}) {
    return this.#outbound('health.ping', {}, pingResult, this.#gate.receipt(), deadlineMs);
  }
  #reply(data, error, value) {
    if (this.#state !== 'active') return;
    const reply = { protocol: PROTOCOL, kind: 'response', id: data.id,
      generation: data.generation, sequence: data.sequence, method: data.method, ok: !error };
    if (error) reply.error = { code: publicErrorCode(error) };
    else reply.payload = value;
    this.#send(reply);
  }
  #receiveRequest(data) {
    const receipt = this.#gate.receipt(); // Capture BEFORE any await or permission decision.
    const reject = code => this.#reply(data, fail(code));
    if (data.generation !== receipt.generation || data.sequence !== receipt.sequence) return reject('STALE');
    if (data.method !== 'read.text') return reject('BAD_METHOD');
    if (!readPayload(data.payload)) return reject('BAD_PAYLOAD');
    if (this.#seen.has(data.id)) return reject('DUPLICATE');
    if (this.#seen.size >= this.#maxIds) { this.dispose(fail('SESSION_BUDGET')); return; }
    this.#seen.add(data.id); // Never evict IDs within this generation.
    if (!this.#gate.permits(receipt) || typeof this.#readText !== 'function') return reject('DENIED');
    if (this.#inbound.size >= this.#maxPending) return reject('BUSY');
    const payload = Object.freeze({ key: data.payload.key });
    const task = { ...deferred(), controller: new AbortController(), done: false };
    const finish = (error, result) => {
      if (task.done) return;
      task.done = true; clearTimeout(task.timer); this.#inbound.delete(data.id);
      if (error) { task.controller.abort(error); task.reject(error); }
      else task.resolve(result);
    };
    task.cancel = error => finish(error);
    task.timer = setTimeout(() => finish(fail('TIMEOUT')), this.#defaultDeadline);
    this.#inbound.set(data.id, task);
    const guard = () => {
      if (task.done || task.controller.signal.aborted || this.#state !== 'active' || !this.#gate.permits(receipt)) {
        throw fail('STALE');
      }
    };
    const context = Object.freeze({ receipt, signal: task.controller.signal, guard });
    task.promise.then(result => {
      // Settlement queues this callback. Content can change before actual delivery,
      // after the task has already left #inbound and is no longer cancelable there.
      this.#reply(data, this.#gate.permits(receipt) ? null : fail('STALE'), result);
    }, error => this.#reply(data, error));
    // The wrapper is cancelable even when a supplied callback ignores AbortSignal.
    Promise.resolve().then(async () => {
      guard();
      const allowed = await this.#authorize('read.text', payload, context);
      guard();
      if (allowed !== true) throw fail('DENIED');
      const text = await this.#readText(payload.key, context);
      guard();
      if (typeof text !== 'string' || text.length > 65_536) throw fail('BAD_RESULT');
      return { text };
    }).then(value => finish(null, value), error => finish(error));
  }
  #cancelWork(error) {
    for (const requestId of this.#pending.keys()) this.#finishOutbound(requestId, error);
    for (const task of [...this.#inbound.values()]) task.cancel(error);
  }
  dispose(error = fail('DISPOSED')) {
    if (this.#state === 'disposed') return;
    this.#state = 'disposed'; this.#gate.invalidate();
    clearTimeout(this.#handshakeTimer);
    if (this.#ready) { this.#ready.reject(error); this.#ready = null; }
    const port = this.#port; this.#port = null;
    this.#cancelWork(error); this.#seen.clear();
    // A broken transport adapter must not prevent promise settlement or other cleanup.
    if (port) {
      try { port.onmessage = null; } catch {}
      try { port.onmessageerror = null; } catch {}
      try { port.close(); } catch {}
    }
    try { this.#onDispose(); } catch { /* Cleanup callback cannot prevent pending settlement. */ }
  }
}
