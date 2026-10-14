import test from 'node:test';
import assert from 'node:assert/strict';
import { BoundaryError, IntegrationHost, ResourceService, persistSecret } from './boundary-model.mjs';

const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};
const config = { endpoint: 'https://synthetic.invalid', workspace: 'docs', secretRef: 'vault:test' };
const request = (operationId = 'op-1', tool = 'read_document', args = { resource: 'doc-a' }) =>
  ({ serverId: 'index', tool, args, operationId });
const configure = (host) => host.configure('index', config, { scopeApproved: true });
function makeHost() {
  const host = new IntegrationHost();
  host.register({ id: 'index', artifact: 'sha256:synthetic', peerIdentity: 'service-a' });
  return host;
}
function transport(call = async () => 'text') {
  return { verifiedPeerIdentity: 'service-a', call, closed: 0,
    async close() { this.closed++; } };
}
async function ready({ decision = 'allow', call } = {}) {
  const host = makeHost(), wire = transport(call);
  host.setInstallationAllowed('index', true);
  configure(host);
  host.setToolPolicy('index', 'read_document', decision);
  await host.connect('index', { resolveSecret: async () => 'synthetic-token', open: async () => wire });
  return { host, wire };
}
const hasCode = (code) => (error) => error instanceof BoundaryError && error.code === code;

test('installation does not authorize startup or calls', async () => {
  const host = makeHost(); configure(host);
  let opens = 0;
  await assert.rejects(host.connect('index', { resolveSecret: async () => 'token',
    open: async () => { opens++; return transport(); } }), hasCode('INSTALLATION_BLOCKED'));
  assert.equal(opens, 0);
  assert.equal((await host.call(request())).status, 'not-dispatched');
});

test('configuration scope and missing values are independent gates', () => {
  const host = makeHost();
  assert.throws(() => host.configure('index', config), hasCode('CONFIG_SCOPE_NOT_APPROVED'));
  assert.throws(() => host.configure('index', { ...config, workspace: '' }, { scopeApproved: true }), hasCode('CONFIG_REQUIRED'));
  assert.equal(host.snapshot('index').configured, false);
});

test('secure store unavailable: no sealing and no plaintext sink write', async () => {
  let seals = 0, writes = 0;
  await assert.rejects(persistSecret({ reference: 'ref', value: 'sensitive-synthetic',
    vault: { available: async () => false, seal: async () => { seals++; } },
    sink: { write: async () => { writes++; } } }), hasCode('SECRET_STORE_UNAVAILABLE'));
  assert.equal(seals, 0); assert.equal(writes, 0);
});

test('encryption exceptions are sanitized and do not fall back to plaintext', async () => {
  let writes = 0;
  await assert.rejects(persistSecret({ reference: 'ref', value: 'synthetic-secret',
    vault: { available: async () => true, seal: async () => { throw Error('synthetic-secret'); } },
    sink: { write: async () => { writes++; } } }), hasCode('SECRET_PERSIST_FAILED'));
  assert.equal(writes, 0);
});

test('unsupported sensitive types and plaintext-shaped vault outputs fail closed', async () => {
  let writes = 0;
  const options = { reference: 'ref', vault: { available: async () => true, seal: async (v) => v },
    sink: { write: async () => { writes++; } } };
  await assert.rejects(persistSecret({ ...options, value: { token: 'secret' } }), hasCode('INVALID_SECRET'));
  await assert.rejects(persistSecret({ ...options, value: 'secret' }), hasCode('INVALID_SEALED_VALUE'));
  assert.equal(writes, 0);
});

test('successful persistence sends only opaque bytes and returns a reference', async () => {
  let stored;
  const result = await persistSecret({ reference: 'ref', value: 'synthetic-secret',
    vault: { available: async () => true, seal: async () => new Uint8Array([17, 4]) },
    sink: { write: async (key, value) => { stored = { key, value }; } } });
  assert.deepEqual(result, { reference: 'ref' });
  assert.deepEqual(stored, { key: 'ref', value: new Uint8Array([17, 4]) });
});

test('missing secret prevents connector from opening', async () => {
  const host = makeHost(); host.setInstallationAllowed('index', true); configure(host);
  let opens = 0;
  await assert.rejects(host.connect('index', { resolveSecret: async () => null,
    open: async () => { opens++; return transport(); } }), hasCode('SECRET_UNAVAILABLE'));
  assert.equal(opens, 0);
});

test('installation revocation during secret lookup prevents startup', async () => {
  const host = makeHost(); host.setInstallationAllowed('index', true); configure(host);
  const secret = deferred(), entered = deferred(); let opens = 0;
  const pending = host.connect('index', { resolveSecret: () => { entered.resolve(); return secret.promise; },
    open: async () => { opens++; return transport(); } });
  await entered.promise;
  host.setInstallationAllowed('index', false); secret.resolve('token');
  await assert.rejects(pending, hasCode('STALE_GENERATION'));
  assert.equal(opens, 0);
});

test('late old connection is closed and cannot overwrite a newer generation', async () => {
  const host = makeHost(); host.setInstallationAllowed('index', true); configure(host);
  const opening = deferred(), entered = deferred(), old = transport(), fresh = transport();
  const first = host.connect('index', { resolveSecret: async () => 'token',
    open: () => { entered.resolve(); return opening.promise; } });
  await entered.promise;
  const newest = await host.connect('index', { resolveSecret: async () => 'token', open: async () => fresh });
  opening.resolve(old);
  await assert.rejects(first, hasCode('STALE_GENERATION'));
  assert.equal(old.closed, 1); assert.equal(fresh.closed, 0);
  assert.equal(host.snapshot('index').generation, newest.generation);
  assert.equal(host.snapshot('index').status, 'ready');
});

test('authenticated peer mismatch closes candidate and fails startup', async () => {
  const host = makeHost(); host.setInstallationAllowed('index', true); configure(host);
  const wrong = transport(); wrong.verifiedPeerIdentity = 'other-service';
  await assert.rejects(host.connect('index', { resolveSecret: async () => 'token', open: async () => wrong }), hasCode('PEER_MISMATCH'));
  assert.equal(wrong.closed, 1); assert.equal(host.snapshot('index').status, 'failed');
});

test('connection success is not tool authorization; annotations grant nothing', async () => {
  let calls = 0;
  const { host } = await ready({ call: async () => { calls++; return 'result'; } });
  const result = await host.call(request('unapproved-tool', 'delete_everything', { readOnlyHint: true }));
  assert.equal(result.reason, 'POLICY_NOT_LOADED'); assert.equal(calls, 0);
});

test('declined confirmation never dispatches', async () => {
  let calls = 0;
  const { host } = await ready({ decision: 'ask', call: async () => { calls++; return ''; } });
  const result = await host.call(request(), { confirm: async () => false });
  assert.equal(result.reason, 'USER_DECLINED'); assert.equal(calls, 0);
});

test('revocation while confirmation is open wins over a later yes', async () => {
  const approval = deferred(), entered = deferred(); let calls = 0;
  const { host } = await ready({ decision: 'ask', call: async () => { calls++; return ''; } });
  const pending = host.call(request(), { confirm: () => { entered.resolve(); return approval.promise; } });
  await entered.promise;
  host.setToolPolicy('index', 'read_document', 'blocked'); approval.resolve(true);
  const result = await pending;
  assert.equal(result.status, 'not-dispatched'); assert.equal(result.reason, 'TOOL_BLOCKED'); assert.equal(calls, 0);
});

test('allow to ask during asynchronous preparation requires new approval', async () => {
  const gate = deferred(), entered = deferred(); let calls = 0;
  const { host } = await ready({ call: async () => { calls++; return ''; } });
  const pending = host.call(request(), { prepare: () => { entered.resolve(); return gate.promise; } });
  await entered.promise;
  host.setToolPolicy('index', 'read_document', 'ask'); gate.resolve();
  assert.equal((await pending).reason, 'POLICY_CHANGED'); assert.equal(calls, 0);
});

test('arguments are snapshotted before approval and cannot change destination', async () => {
  const gate = deferred(), entered = deferred(); let sent;
  const { host } = await ready({ decision: 'ask', call: async (r) => { sent = r; return 'ok'; } });
  const args = { resource: 'doc-a' };
  const pending = host.call(request('immutable', 'read_document', args), { confirm: (review) => {
    assert.equal(Object.isFrozen(review.request.args), true);
    entered.resolve(); return gate.promise;
  } });
  await entered.promise; args.resource = 'other'; gate.resolve(true);
  assert.equal((await pending).status, 'completed'); assert.equal(sent.args.resource, 'doc-a');
});

test('post-dispatch revocation discards response and cannot imply rollback', async () => {
  const response = deferred(), entered = deferred();
  const { host } = await ready({ call: () => { entered.resolve(); return response.promise; } });
  const pending = host.call(request()); await entered.promise;
  host.setToolPolicy('index', 'read_document', 'blocked'); response.resolve('private result');
  const result = await pending;
  assert.equal(result.status, 'unknown'); assert.equal(result.retry, 'reconcile-only');
  assert.equal(Object.hasOwn(result, 'value'), false);
});

test('old generation response cannot populate current session', async () => {
  const response = deferred(), entered = deferred();
  const { host } = await ready({ call: () => { entered.resolve(); return response.promise; } });
  const pending = host.call(request()); await entered.promise;
  await host.disconnect('index'); response.resolve('old result');
  const result = await pending;
  assert.equal(result.status, 'unknown'); assert.equal(result.reason, 'STALE_GENERATION');
});

test('lost response after a side effect stays unknown; duplicate ID never replays', async () => {
  let effects = 0;
  const { host } = await ready({ call: async () => { effects++; throw Error('socket lost; synthetic-secret'); } });
  const first = await host.call(request());
  assert.equal(first.status, 'unknown'); assert.equal(first.reason, 'TRANSPORT_RESULT_UNKNOWN');
  assert.equal(first.retry, 'reconcile-only');
  await assert.rejects(host.call(request()), hasCode('OPERATION_ALREADY_USED'));
  assert.equal(effects, 1); assert.equal(host.operation('op-1').status, 'unknown');
});

test('concurrent requests with one operation ID dispatch at most once', async () => {
  const gate = deferred(), entered = deferred(); let calls = 0;
  const { host } = await ready({ call: () => { calls++; entered.resolve(); return gate.promise; } });
  const first = host.call(request()); await entered.promise;
  await assert.rejects(host.call(request()), hasCode('OPERATION_ALREADY_USED'));
  gate.resolve('ok'); assert.equal((await first).status, 'completed'); assert.equal(calls, 1);
});

test('cleanup failure blocks relaunch rather than claiming the old process stopped', async () => {
  const { host, wire } = await ready();
  wire.close = async () => { throw Error('still alive'); };
  let opens = 0;
  await assert.rejects(host.connect('index', { resolveSecret: async () => 'token',
    open: async () => { opens++; return transport(); } }), hasCode('CLEANUP_FAILED'));
  assert.equal(opens, 0); assert.equal(host.snapshot('index').cleanupFailed, true);
});

test('configuration changes invalidate old permission and connection', async () => {
  const { host } = await ready(); configure(host);
  await host.connect('index', { resolveSecret: async () => 'token', open: async () => transport() });
  assert.equal((await host.call(request())).reason, 'POLICY_NOT_LOADED');
});

test('host allow never overrides independent resource denial or forged principal', async () => {
  const service = new ResourceService({ 'doc-a': 'original' });
  service.setAccess('admin', 'doc-a', ['read', 'write']);
  const { host } = await ready({ call: (r) => service.execute(r, 'guest') });
  const result = await host.call(request('forgery', 'read_document', { resource: 'doc-a', principal: 'admin' }));
  assert.equal(result.status, 'unknown'); assert.equal(result.reason, 'RESOURCE_DENIED');
  assert.equal(await service.execute({ tool: 'read_document', args: { resource: 'doc-a' } }, 'admin'), 'original');
});

test('resource authorization is checked again after awaited preparation', async () => {
  const service = new ResourceService({ 'doc-a': 'original' });
  service.setAccess('user', 'doc-a', ['write']);
  const gate = deferred(), entered = deferred();
  const pending = service.execute({ tool: 'append_note', args: { resource: 'doc-a', text: '+changed' } }, 'user', {
    beforeCommit: () => { entered.resolve(); return gate.promise; },
  });
  await entered.promise; service.setAccess('user', 'doc-a', ['read']); gate.resolve();
  await assert.rejects(pending, hasCode('RESOURCE_DENIED'));
  assert.equal(await service.execute({ tool: 'read_document', args: { resource: 'doc-a' } }, 'user'), 'original');
});

test('resource classification ignores untrusted read-only annotations', async () => {
  const service = new ResourceService({ 'doc-a': 'original' }); service.setAccess('user', 'doc-a', ['read']);
  await assert.rejects(service.execute({ tool: 'append_note', args: { resource: 'doc-a', text: 'bad' },
    annotations: { readOnlyHint: true } }, 'user'), hasCode('RESOURCE_DENIED'));
});

test('independently authorized host and service can execute a synthetic write', async () => {
  const service = new ResourceService({ 'doc-a': 'original' }); service.setAccess('user', 'doc-a', ['read', 'write']);
  const { host } = await ready({ call: (r) => service.execute(r, 'user') });
  host.setToolPolicy('index', 'append_note', 'ask');
  const result = await host.call(request('write-1', 'append_note', { resource: 'doc-a', text: '+note' }), {
    confirm: async (review) => review.request.args.text === '+note' && review.artifact === 'sha256:synthetic',
  });
  assert.equal(result.status, 'completed'); assert.equal(result.value, 'original+note');
});

test('write failure does not return a secret reference or expose sink error text', async () => {
  let writes = 0;
  await assert.rejects(persistSecret({ reference: 'ref', value: 'synthetic-secret',
    vault: { available: async () => true, seal: async () => new Uint8Array([1]) },
    sink: { write: async () => { writes++; throw Error('synthetic-secret'); } } }), hasCode('SECRET_PERSIST_FAILED'));
  assert.equal(writes, 1);
});

test('external BoundaryError cannot smuggle arbitrary text through sanitization', async () => {
  const { host } = await ready({ call: async () => { throw new BoundaryError('synthetic-secret'); } });
  const result = await host.call(request());
  assert.equal(result.status, 'unknown'); assert.equal(result.reason, 'TRANSPORT_RESULT_UNKNOWN');
  assert.equal(JSON.stringify(result).includes('synthetic-secret'), false);
});

test('configuration revocation during startup stops the late candidate', async () => {
  const host = makeHost(); host.setInstallationAllowed('index', true); configure(host);
  const gate = deferred(), entered = deferred(), wire = transport();
  const pending = host.connect('index', { resolveSecret: async () => 'token',
    open: () => { entered.resolve(); return gate.promise; } });
  await entered.promise; host.revokeConfiguration('index'); gate.resolve(wire);
  await assert.rejects(pending, hasCode('STALE_GENERATION'));
  assert.equal(wire.closed, 1); assert.equal(host.snapshot('index').configured, false);
});

test('revoking and restoring ask permission cannot reuse a pending old approval', async () => {
  const gate = deferred(), entered = deferred(); let calls = 0;
  const { host } = await ready({ decision: 'ask', call: async () => { calls++; return ''; } });
  const pending = host.call(request(), { confirm: () => { entered.resolve(); return gate.promise; } });
  await entered.promise;
  host.setToolPolicy('index', 'read_document', 'blocked');
  host.setToolPolicy('index', 'read_document', 'ask'); gate.resolve(true);
  assert.equal((await pending).reason, 'POLICY_CHANGED'); assert.equal(calls, 0);
});

test('synchronous transport throw after entry is conservatively unknown', async () => {
  let effects = 0;
  const { host } = await ready({ call: () => { effects++; throw Error('failed after effect'); } });
  const result = await host.call(request());
  assert.equal(result.status, 'unknown'); assert.equal(effects, 1);
  await assert.rejects(host.call(request()), hasCode('OPERATION_ALREADY_USED'));
});

test('argument accessors are rejected without invoking them', async () => {
  let reads = 0, calls = 0;
  const { host } = await ready({ call: async () => { calls++; return ''; } });
  const args = { get resource() { reads++; return 'doc-a'; } };
  await assert.rejects(host.call(request('getter', 'read_document', args)), hasCode('INVALID_ARGUMENTS'));
  assert.equal(reads, 0); assert.equal(calls, 0);
});
