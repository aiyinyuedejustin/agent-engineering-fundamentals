// Runs only a protocol simulation. This is NOT a browser security test.
import { MessageChannel } from 'node:worker_threads';
import { SandboxHost, PROTOCOL } from '../assets/sandbox-model.mjs';
const hostOrigin = 'https://app.example', rendererOrigin = 'https://preview.example';
const nonce = 'demo_nonce_0123456789'; // Production: fresh crypto.randomUUID() per frame generation.
let host, peer;
const frameWindow = {
  postMessage(data, target, ports = []) {
    if (target !== rendererOrigin) throw Error('wrong target origin');
    if (data.kind === 'hello') queueMicrotask(() => host.receiveWindow({
      origin: rendererOrigin, source: frameWindow, ports: [], data: { ...data, kind: 'ready' }
    }));
    if (data.kind === 'channel') {
      peer = ports[0];
      peer.onmessage = ({ data: request }) => {
        if (request.kind === 'response') {
          console.log('Capability response:', request.payload ?? request.error);
          host.dispose(); peer.close(); return;
        }
        peer.postMessage({ ...request, kind: 'response', ok: true, payload: { applied: true } });
      };
      peer.start(); peer.postMessage({ ...data, kind: 'port-ready' });
    }
  }
};
host = new SandboxHost({ frameWindow, hostOrigin, rendererOrigin, generation: 1, nonce,
  createChannel: () => new MessageChannel(),
  authorize: (_method, payload) => payload.key === 'public',
  readText: () => 'Only an explicitly allowed, in-memory sample.' });
try {
  await host.connect();
  await host.postContent({ format: 'html', body: '<p>Not executed by this model.</p>' });
  console.log('Protocol model: current content acknowledged. No browser isolation was tested.');
  peer.postMessage({ protocol: PROTOCOL, kind: 'request', id: 'demo_read', generation: 1,
    sequence: host.sequence, method: 'read.text', payload: { key: 'public' } });
} catch (error) { host.dispose(); peer?.close(); throw error; }
