import test from 'node:test';
import assert from 'node:assert/strict';
import { MessageChannel } from 'node:worker_threads';
import { setImmediate as nextTurn } from 'node:timers/promises';
import { ContentGate, SandboxHost, PROTOCOL, ProtocolError } from '../assets/sandbox-model.mjs';

const rendererOrigin = 'https://preview.example';
const hostOrigin = 'https://app.example';
const nonce = 'fresh_nonce_0123456789';
const errorCode = code => error => error instanceof ProtocolError && error.code === code;
const control = (kind, generation = 1) => ({ protocol: PROTOCOL, kind, generation, nonce });
const waitFor = async predicate => {
  const end = performance.now() + 1000;
  while (!predicate()) {
    assert.ok(performance.now() < end, 'condition did not become true');
    await nextTurn();
  }
};
function reply(message, override = {}) {
  return { protocol: PROTOCOL, kind: 'response', id: message.id, generation: message.generation,
    sequence: message.sequence, method: message.method, ok: true,
    payload: message.method === 'content.set' ? { applied: true } : { alive: true }, ...override };
}
function harness(t, options = {}) {
  const sentWindow = [], received = [], waiters = [];
  let peer;
  const frameWindow = {
    postMessage(data, targetOrigin, ports = []) {
      sentWindow.push({ data, targetOrigin, ports });
      if (ports.length) {
        peer = ports[0];
        peer.onmessage = event => {
          const at = waiters.findIndex(waiter => waiter.matches(event.data));
          if (at < 0) received.push(event.data);
          else waiters.splice(at, 1)[0].resolve(event.data);
        };
        peer.start();
      }
    }
  };
  const host = new SandboxHost({ frameWindow, hostOrigin, rendererOrigin, generation: 1, nonce,
    createChannel: () => new MessageChannel(), ...options });
  const receiveWindow = (data = control('ready'), patch = {}) => host.receiveWindow({
    source: frameWindow, origin: rendererOrigin, data, ports: [], ...patch
  });
  const take = async (matches = () => true) => {
    const at = received.findIndex(matches);
    if (at >= 0) return received.splice(at, 1)[0];
    let timeout;
    const result = new Promise((resolve, reject) => {
      const waiter = { matches, resolve: value => { clearTimeout(timeout); resolve(value); } };
      waiters.push(waiter);
      timeout = setTimeout(() => {
        const index = waiters.indexOf(waiter);
        if (index >= 0) waiters.splice(index, 1);
        reject(new Error('message not received'));
      }, 1000);
    });
    return result;
  };
  const open = async () => {
    const ready = host.connect();
    assert.equal(receiveWindow(), true);
    peer.postMessage(control('port-ready', options.generation ?? 1));
    await ready;
  };
  const emit = data => peer.postMessage(data);
  const setContent = async () => {
    const promise = host.postContent({ format: 'html', body: '<p>sample</p>' });
    const message = await take(data => data.method === 'content.set');
    emit(reply(message));
    await promise;
  };
  const read = (requestId = 'r_1', overrides = {}) => emit({ protocol: PROTOCOL, kind: 'request',
    id: requestId, generation: host.generation, sequence: host.sequence,
    method: 'read.text', payload: { key: 'public' }, ...overrides });
  t.after(() => { host.dispose(); peer?.close(); });
  return { host, frameWindow, sentWindow, received, receiveWindow, take, open, emit, setContent, read };
}

test('receipt captured before acknowledgement cannot inherit a later grant', () => {
  const gate = new ContentGate(1), first = gate.replace(), before = gate.receipt();
  assert.equal(gate.acknowledge(first), true);
  assert.equal(gate.permits(before), false);
  assert.equal(gate.permits(gate.receipt()), true);
});

test('generation and sequence both bind acknowledgement; replacement revokes old receipts', () => {
  const gate = new ContentGate(3), first = gate.replace();
  gate.acknowledge(first); const oldReceipt = gate.receipt(); const current = gate.replace();
  assert.equal(gate.acknowledge(first), false);
  assert.equal(gate.acknowledge({ ...current, generation: 2 }), false);
  assert.equal(gate.acknowledge(current), true);
  assert.equal(gate.permits(oldReceipt), false);
  gate.invalidate(); assert.equal(gate.permits(gate.receipt()), false);
});

test('model refuses same-origin, wildcard, opaque, and noncanonical boundaries', () => {
  for (const boundary of [hostOrigin, '*', 'null', 'https://preview.example/path']) {
    assert.throws(() => new SandboxHost({ frameWindow: { postMessage() {} }, hostOrigin,
      rendererOrigin: boundary, generation: 1, nonce }), errorCode('BAD_BOUNDARY'));
  }
});

test('window handshake checks exact source, origin, generation, nonce, schema and no unsolicited ports', async t => {
  const h = harness(t); const connecting = h.host.connect();
  assert.equal(h.receiveWindow(undefined, { source: {} }), false);
  assert.equal(h.receiveWindow(undefined, { origin: 'https://evil.example' }), false);
  assert.equal(h.receiveWindow(control('ready', 2)), false);
  assert.equal(h.receiveWindow({ ...control('ready'), nonce: 'wrong_nonce_0123456789' }), false);
  assert.equal(h.receiveWindow({ ...control('ready'), extra: true }), false);
  assert.equal(h.receiveWindow(undefined, { ports: [{}] }), false);
  assert.equal(h.sentWindow.length, 1);
  assert.equal(h.receiveWindow(), true);
  assert.equal(h.sentWindow[1].targetOrigin, rendererOrigin);
  assert.equal(h.sentWindow[1].ports.length, 1);
  assert.equal(h.receiveWindow(), false);
  h.emit(control('port-ready')); await connecting;
  assert.equal(h.host.state, 'active');
});

test('window RPC is ignored after handshake; transferred port works without event.origin', async t => {
  const h = harness(t); await h.open();
  const pending = h.host.postContent({ format: 'html', body: 'one' });
  const message = await h.take();
  assert.equal(h.receiveWindow(reply(message)), false);
  assert.equal(h.host.acknowledged, false);
  h.emit(reply(message)); await pending;
  assert.equal(h.host.acknowledged, true);
});

test('handshake has an explicit deadline and cleanup', async t => {
  let cleaned = false;
  const h = harness(t, { onDispose: () => { cleaned = true; } });
  await assert.rejects(h.host.connect({ deadlineMs: 10 }), errorCode('TIMEOUT'));
  assert.equal(h.host.state, 'disposed'); assert.equal(cleaned, true);
});

test('dispose rejects a handshake that has not finished', async t => {
  const h = harness(t); const checked = assert.rejects(h.host.connect(), errorCode('DISPOSED'));
  h.host.dispose(); await checked;
});

test('synchronous handshake transmission failure settles its promise', async t => {
  const h = harness(t); h.frameWindow.postMessage = () => { throw new Error('closed frame'); };
  await assert.rejects(h.host.connect(), errorCode('SEND_FAILED'));
  assert.equal(h.host.state, 'disposed');
});

test('ack binds ID, method, generation and sequence, not just success', async t => {
  const h = harness(t); await h.open();
  const pending = h.host.postContent({ format: 'html', body: 'one' });
  const message = await h.take();
  for (const patch of [{ id: 'other' }, { method: 'health.ping' }, { generation: 9 }, { sequence: 9 }]) {
    h.emit(reply(message, patch));
  }
  await nextTurn();
  assert.equal(h.host.acknowledged, false); assert.equal(h.host.pendingCount, 1);
  h.emit(reply(message)); await pending;
  assert.equal(h.host.acknowledged, true);
});

test('superseding content rejects old work; late success cannot acknowledge the new sequence', async t => {
  const h = harness(t); await h.open();
  const first = h.host.postContent({ format: 'html', body: 'one' });
  const firstChecked = assert.rejects(first, errorCode('STALE')); const old = await h.take();
  const second = h.host.postContent({ format: 'html', body: 'two' }); const current = await h.take();
  await firstChecked; h.emit(reply(old)); await nextTurn();
  assert.equal(h.host.acknowledged, false);
  h.emit(reply(current)); await second;
  assert.equal(h.host.sequence, 2); assert.equal(h.host.acknowledged, true);
});

test('failed or schema-invalid content responses never grant capabilities', async t => {
  const h = harness(t); await h.open();
  const first = h.host.postContent({ format: 'html', body: 'one' });
  const checked = assert.rejects(first, errorCode('REMOTE_ERROR')); const msg = await h.take();
  const negative = reply(msg); delete negative.payload; negative.ok = false; negative.error = { code: 'RENDER_FAILED' };
  h.emit(negative); await checked; assert.equal(h.host.acknowledged, false);
  const second = h.host.postContent({ format: 'html', body: 'two' });
  const checked2 = assert.rejects(second, errorCode('BAD_PAYLOAD')); const msg2 = await h.take();
  h.emit(reply(msg2, { payload: { applied: false } })); await checked2;
  assert.equal(h.host.acknowledged, false);
});

test('every outbound RPC times out and clears pending state; late reply has no effect', async t => {
  const h = harness(t); await h.open();
  const pending = h.host.postContent({ format: 'html', body: 'one' }, { deadlineMs: 10 });
  const checked = assert.rejects(pending, errorCode('TIMEOUT')); const message = await h.take();
  await checked; h.emit(reply(message)); await nextTurn();
  assert.equal(h.host.pendingCount, 0); assert.equal(h.host.acknowledged, false);
});

test('disposal rejects all outstanding RPCs, closes the session, and is idempotent', async t => {
  let calls = 0; const h = harness(t, { onDispose: () => { calls++; throw Error('cleanup failure'); } });
  await h.open();
  const checked = [h.host.ping(), h.host.ping(), h.host.ping()].map(p => assert.rejects(p, errorCode('DISPOSED')));
  assert.equal(h.host.pendingCount, 3); h.host.dispose(); h.host.dispose();
  await Promise.all(checked);
  assert.equal(h.host.pendingCount, 0); assert.equal(calls, 1);
  await assert.rejects(h.host.ping(), errorCode('NOT_CONNECTED'));
});

test('malformed port envelopes fail closed and reject outstanding RPCs', async t => {
  const h = harness(t); await h.open();
  const checked = assert.rejects(h.host.ping(), errorCode('BAD_MESSAGE'));
  h.emit({ protocol: PROTOCOL, kind: 'request', arbitrary: true }); await checked;
  assert.equal(h.host.state, 'disposed');
});

test('method and payload schemas reject unknown methods, extra fields and oversized keys before authorization', async t => {
  let calls = 0; const h = harness(t, { authorize: () => { calls++; return true; }, readText: () => 'safe' });
  await h.open(); await h.setContent();
  h.read('unknown', { method: 'delete.everything' }); assert.equal((await h.take()).error.code, 'BAD_METHOD');
  h.read('extra', { payload: { key: 'public', execute: 'bad' } }); assert.equal((await h.take()).error.code, 'BAD_PAYLOAD');
  h.read('large', { payload: { key: 'x'.repeat(65) } }); assert.equal((await h.take()).error.code, 'BAD_PAYLOAD');
  assert.equal(calls, 0);
});

test('unacknowledged requests cannot inherit a later acknowledgement', async t => {
  let calls = 0; const h = harness(t, { authorize: () => true, readText: () => { calls++; return 'safe'; } });
  await h.open();
  const pending = h.host.postContent({ format: 'html', body: 'one' }); const message = await h.take();
  h.read(); assert.equal((await h.take()).error.code, 'DENIED');
  h.emit(reply(message)); await pending;
  assert.equal(calls, 0);
});

test('capabilities are absent by default even for acknowledged content', async t => {
  const h = harness(t); await h.open(); await h.setContent(); h.read();
  assert.equal((await h.take()).error.code, 'DENIED');
});

test('permission must return exactly true; errors are sanitized', async t => {
  let mode = 'deny', calls = 0;
  const h = harness(t, { authorize: () => { if (mode === 'throw') throw Error('private token'); return 'truthy'; },
    readText: () => { calls++; return 'safe'; } });
  await h.open(); await h.setContent(); h.read('denied');
  assert.equal((await h.take()).error.code, 'DENIED'); mode = 'throw'; h.read('throws');
  assert.deepEqual((await h.take()).error, { code: 'HANDLER_FAILED' }); assert.equal(calls, 0);
});

test('authorized request returns schema-checked data; replay never reexecutes', async t => {
  let calls = 0;
  const h = harness(t, { authorize: () => true, readText: key => { calls++; return `value:${key}`; } });
  await h.open(); await h.setContent(); h.read();
  assert.deepEqual((await h.take()).payload, { text: 'value:public' });
  h.read(); assert.equal((await h.take()).error.code, 'DUPLICATE'); assert.equal(calls, 1);
});

test('stale permission completion cannot start a handler after content replacement', async t => {
  let approve, calls = 0, signal;
  const h = harness(t, { authorize: (_method, _payload, context) => { signal = context.signal; return new Promise(r => { approve = r; }); },
    readText: () => { calls++; return 'secret'; } });
  await h.open(); await h.setContent(); h.read(); await waitFor(() => approve);
  const newer = h.host.postContent({ format: 'html', body: 'two' });
  const message = await h.take(data => data.kind === 'request'); h.emit(reply(message)); await newer;
  approve(true); await nextTurn();
  assert.equal(signal.aborted, true); assert.equal(calls, 0); assert.equal(h.host.inboundCount, 0);
  assert.equal((await h.take(data => data.kind === 'response')).error.code, 'STALE');
});

test('late handler completion is discarded after replacement even if it ignores cancellation', async t => {
  let finish, signal;
  const h = harness(t, { authorize: () => true, readText: (_key, context) => { signal = context.signal; return new Promise(r => { finish = r; }); } });
  await h.open(); await h.setContent(); h.read(); await waitFor(() => finish);
  const newer = h.host.postContent({ format: 'html', body: 'two' });
  const message = await h.take(data => data.kind === 'request'); h.emit(reply(message)); await newer;
  const rejection = await h.take(data => data.kind === 'response'); assert.equal(rejection.error.code, 'STALE');
  finish('private late value'); await nextTurn(); await nextTurn();
  assert.equal(signal.aborted, true); assert.equal(h.received.some(m => m.payload?.text), false);
});

test('inbound permission and handler work share a deadline; never-resolving callbacks are canceled', async t => {
  let signal;
  const h = harness(t, { deadlineMs: 30, authorize: (_method, _payload, context) => { signal = context.signal; return new Promise(() => {}); }, readText: () => 'safe' });
  await h.open(); await h.setContent(); h.read();
  assert.equal((await h.take()).error.code, 'TIMEOUT'); assert.equal(signal.aborted, true);
  assert.equal(h.host.inboundCount, 0);
});

test('dispose aborts in-flight capability work and prevents late data responses', async t => {
  let finish, signal;
  const h = harness(t, { authorize: () => true, readText: (_key, context) => { signal = context.signal; return new Promise(r => { finish = r; }); } });
  await h.open(); await h.setContent(); h.read(); await waitFor(() => finish);
  h.host.dispose(); assert.equal(signal.aborted, true); assert.equal(h.host.inboundCount, 0);
  finish('private late value'); await nextTurn(); await nextTurn(); assert.deepEqual(h.received, []);
});

test('wrong inbound generation or sequence is stale even on the correct port', async t => {
  const h = harness(t, { authorize: () => true, readText: () => 'safe' });
  await h.open(); await h.setContent();
  h.read('old_generation', { generation: 99 }); assert.equal((await h.take()).error.code, 'STALE');
  h.read('old_sequence', { sequence: 0 }); assert.equal((await h.take()).error.code, 'STALE');
});

test('inbound result schema prevents oversized or unexpected values from leaving the host', async t => {
  const h = harness(t, { authorize: () => true, readText: () => ({ private: 'object' }) });
  await h.open(); await h.setContent(); h.read(); assert.equal((await h.take()).error.code, 'BAD_RESULT');
});

test('session ID budget closes rather than evicting replay protection', async t => {
  const h = harness(t, { maxIds: 1, authorize: () => true, readText: () => 'safe' });
  await h.open(); await h.setContent(); h.read('one'); await h.take(); h.read('two');
  await waitFor(() => h.host.state === 'disposed'); assert.equal(h.host.inboundCount, 0);
});

test('rate limit closes the channel and rejects pending work', async t => {
  const h = harness(t, { rate: { limit: 2, intervalMs: 1000 } }); await h.open();
  const checked = assert.rejects(h.host.ping(), errorCode('RATE_LIMIT')); const message = await h.take();
  h.emit(reply(message, { id: 'not_pending_1' })); h.emit(reply(message, { id: 'not_pending_2' }));
  await checked; assert.equal(h.host.pendingCount, 0);
});

test('bounded outbound and inbound concurrency rejects excess work', async t => {
  const h = harness(t, { maxPending: 1, authorize: () => new Promise(() => {}), readText: () => 'safe' });
  await h.open(); await h.setContent();
  const pending = h.host.ping(); const checked = assert.rejects(pending, errorCode('DISPOSED'));
  await assert.rejects(h.host.ping(), errorCode('BUSY')); await h.take();
  h.read('one'); await waitFor(() => h.host.inboundCount === 1); h.read('two');
  assert.equal((await h.take()).error.code, 'BUSY'); h.host.dispose(); await checked;
});

test('invalid deadlines and outgoing payloads fail before invalidating acknowledged content', async t => {
  const h = harness(t); await h.open(); await h.setContent();
  await assert.rejects(h.host.postContent({ format: 'html', body: 'ok' }, { deadlineMs: Infinity }), errorCode('BAD_DEADLINE'));
  await assert.rejects(h.host.postContent({ format: 'html', body: 'x'.repeat(65_537) }), errorCode('BAD_PAYLOAD'));
  assert.equal(h.host.acknowledged, true); assert.equal(h.host.sequence, 1);
});

test('throwing transport close cannot block all-pending rejection or disposal callback', async t => {
  let hostPort, cleaned = false;
  const h = harness(t, { createChannel: () => { const channel = new MessageChannel(); hostPort = channel.port1; return channel; },
    onDispose: () => { cleaned = true; } });
  await h.open();
  const realClose = hostPort.close.bind(hostPort);
  hostPort.close = () => { realClose(); throw Error('adapter close failure'); };
  const checked = [h.host.ping(), h.host.ping()].map(p => assert.rejects(p, errorCode('DISPOSED')));
  assert.doesNotThrow(() => h.host.dispose()); await Promise.all(checked);
  assert.equal(cleaned, true); assert.equal(h.host.pendingCount, 0);
});

test('failed port transfer and throwing peer close still reject handshake', async t => {
  const h = harness(t, { createChannel: () => {
    const channel = new MessageChannel(), close = channel.port2.close.bind(channel.port2);
    channel.port2.close = () => { close(); throw Error('adapter close failure'); };
    return channel;
  } });
  const checked = assert.rejects(h.host.connect(), errorCode('SEND_FAILED'));
  h.frameWindow.postMessage = () => { throw Error('transfer failed'); };
  assert.equal(h.receiveWindow(), false); await checked;
  assert.equal(h.host.state, 'disposed');
});


test('injected ProtocolError cannot leak arbitrary text through its code', async t => {
  const h = harness(t, { authorize: () => { throw new ProtocolError('private-token-should-not-leave'); },
    readText: () => 'not reached' });
  await h.open(); await h.setContent(); h.read();
  assert.deepEqual((await h.take()).error, { code: 'HANDLER_FAILED' });
});

test('content replacement between read settlement and reply delivery suppresses old data', async t => {
  let completeRead;
  const h = harness(t, { authorize: () => true,
    readText: () => new Promise(resolve => { completeRead = resolve; }) });
  await h.open(); await h.setContent(); h.read('settled_old_read');
  await waitFor(() => completeRead);
  completeRead('synthetic private value');
  // Await local settlement, while its queued response callback has not run yet.
  for (let n = 0; n < 100 && h.host.inboundCount; n++) await Promise.resolve();
  assert.equal(h.host.inboundCount, 0);
  const newer = h.host.postContent({ format: 'html', body: 'new content' });
  const message = await h.take(data => data.kind === 'request');
  h.emit(reply(message)); await newer;
  const response = await h.take(data => data.id === 'settled_old_read');
  assert.equal(response.ok, false);
  assert.deepEqual(response.error, { code: 'STALE' });
  assert.equal(Object.hasOwn(response, 'payload'), false);
});
