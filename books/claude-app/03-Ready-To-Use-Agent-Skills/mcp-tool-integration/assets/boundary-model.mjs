// Original, dependency-free teaching model. No MCP wire protocol or real secrets.
export class BoundaryError extends Error {
  constructor(code) { super(code); this.name = 'BoundaryError'; this.code = code; }
}
const fail = (code) => { throw new BoundaryError(code); };
const safeCodes = new Set([
  'INVALID_SECRET', 'SECRET_STORE_UNAVAILABLE', 'INVALID_SEALED_VALUE', 'SECRET_PERSIST_FAILED',
  'INVALID_INSTALLATION', 'UNKNOWN_SERVER', 'INVALID_POLICY', 'CONFIG_SCOPE_NOT_APPROVED',
  'CONFIG_REQUIRED', 'STALE_GENERATION', 'INSTALLATION_BLOCKED', 'CLEANUP_FAILED',
  'SECRET_UNAVAILABLE', 'PEER_MISMATCH', 'CONNECTION_FAILED', 'NOT_CONNECTED',
  'POLICY_NOT_LOADED', 'TOOL_BLOCKED', 'POLICY_CHANGED', 'INVALID_CALL', 'OPERATION_ALREADY_USED',
  'INVALID_ARGUMENTS', 'USER_DECLINED', 'TRANSPORT_RESULT_UNKNOWN', 'PREPARATION_FAILED',
  'INVALID_RESOURCE_POLICY', 'RESOURCE_DENIED', 'RESOURCE_POLICY_CHANGED', 'RESOURCE_MISSING',
  'INVALID_RESOURCE_CALL',
]);
const nonempty = (v) => typeof v === 'string' && v.trim().length > 0;
const freeze = (v) => {
  if (v && typeof v === 'object') {
    for (const x of Object.values(v)) freeze(x);
    Object.freeze(v);
  }
  return v;
};
// Only finite, plain JSON data may cross this example's request boundary.
function copyJSON(value) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (Array.isArray(value)) return value.map(copyJSON);
  if (value && [Object.prototype, null].includes(Object.getPrototypeOf(value))) {
    const out = Object.create(null);
    for (const [k, descriptor] of Object.entries(Object.getOwnPropertyDescriptors(value))) {
      if (['__proto__', 'constructor', 'prototype'].includes(k)) fail('INVALID_ARGUMENTS');
      if (!Object.hasOwn(descriptor, 'value')) fail('INVALID_ARGUMENTS');
      out[k] = copyJSON(descriptor.value);
    }
    return out;
  }
  fail('INVALID_ARGUMENTS');
}
function codeOf(error, fallback) {
  return error instanceof BoundaryError && safeCodes.has(error.code) ? error.code : fallback;
}

// Trusted vault and sink adapters are prerequisites. This is not encryption.
export async function persistSecret({ vault, sink, reference, value }) {
  if (!nonempty(reference) || !nonempty(value)) fail('INVALID_SECRET');
  try {
    if (await vault.available() !== true) fail('SECRET_STORE_UNAVAILABLE');
    const sealed = await vault.seal(value);
    if (!(sealed instanceof Uint8Array) || sealed.length === 0) fail('INVALID_SEALED_VALUE');
    await sink.write(reference, new Uint8Array(sealed));
    return Object.freeze({ reference });
  } catch (error) {
    // Do not expose vendor errors, secret text, or a plaintext fallback.
    fail(codeOf(error, 'SECRET_PERSIST_FAILED'));
  }
}

export class IntegrationHost {
  #servers = new Map();
  #policies = new Map();
  #operations = new Map();
  #revision = 0;

  register({ id, artifact, peerIdentity }) {
    if (![id, artifact, peerIdentity].every(nonempty) || this.#servers.has(id)) fail('INVALID_INSTALLATION');
    this.#servers.set(id, {
      id, artifact, peerIdentity, installationAllowed: false, config: null,
      generation: 0, status: 'installed', transport: null,
      cleanup: Promise.resolve(), cleanupFailed: false,
    });
  }
  #server(id) { return this.#servers.get(id) ?? fail('UNKNOWN_SERVER'); }
  #key(id, tool) { return JSON.stringify([id, tool]); }
  #invalidate(s) {
    s.generation += 1;
    s.status = 'disconnected';
    const old = s.transport;
    s.transport = null;
    if (old) s.cleanup = s.cleanup.then(async () => {
      try { await old.close(); } catch { s.cleanupFailed = true; }
    });
  }
  // Only trusted host policy/configuration code may invoke these methods.
  setInstallationAllowed(id, allowed) {
    if (typeof allowed !== 'boolean') fail('INVALID_POLICY');
    const s = this.#server(id);
    if (s.installationAllowed !== allowed) this.#invalidate(s);
    s.installationAllowed = allowed;
  }
  configure(id, { endpoint, workspace, secretRef }, { scopeApproved = false } = {}) {
    const s = this.#server(id);
    if (scopeApproved !== true) fail('CONFIG_SCOPE_NOT_APPROVED');
    if (![endpoint, workspace, secretRef].every(nonempty)) fail('CONFIG_REQUIRED');
    this.#invalidate(s);
    s.config = Object.freeze({ endpoint, workspace, secretRef });
    for (const [key, p] of this.#policies) if (p.serverId === id) this.#policies.delete(key);
  }
  revokeConfiguration(id) {
    const s = this.#server(id);
    this.#invalidate(s);
    s.config = null;
    for (const [key, p] of this.#policies) if (p.serverId === id) this.#policies.delete(key);
  }
  setToolPolicy(id, tool, decision) {
    this.#server(id);
    if (!nonempty(tool) || !['allow', 'ask', 'blocked'].includes(decision)) fail('INVALID_POLICY');
    this.#policies.set(this.#key(id, tool), Object.freeze({
      serverId: id, decision, revision: ++this.#revision,
    }));
  }
  snapshot(id) {
    const s = this.#server(id);
    return Object.freeze({ id, artifact: s.artifact, generation: s.generation,
      status: s.status, installationAllowed: s.installationAllowed,
      configured: !!s.config, cleanupFailed: s.cleanupFailed });
  }
  #connectionGuard(s, generation) {
    if (s.generation !== generation) fail('STALE_GENERATION');
    if (!s.installationAllowed) fail('INSTALLATION_BLOCKED');
    if (!s.config) fail('CONFIG_REQUIRED');
    if (s.cleanupFailed) fail('CLEANUP_FAILED');
  }
  async #closeCandidate(s, candidate) {
    if (!candidate) return;
    try { await candidate.close(); } catch { s.cleanupFailed = true; }
  }
  async connect(id, { resolveSecret, open }) {
    const s = this.#server(id);
    this.#invalidate(s);
    const generation = s.generation;
    let candidate;
    try {
      this.#connectionGuard(s, generation);
      s.status = 'connecting';
      await s.cleanup;
      this.#connectionGuard(s, generation);
      const token = await resolveSecret(s.config.secretRef);
      this.#connectionGuard(s, generation);
      if (!nonempty(token)) fail('SECRET_UNAVAILABLE');
      candidate = await open(Object.freeze({ serverId: id, artifact: s.artifact,
        expectedPeerIdentity: s.peerIdentity, generation, config: s.config, token }));
      this.#connectionGuard(s, generation);
      // verifiedPeerIdentity must come from a trusted connector's authentication.
      if (candidate?.verifiedPeerIdentity !== s.peerIdentity ||
          typeof candidate.call !== 'function' || typeof candidate.close !== 'function') fail('PEER_MISMATCH');
      s.transport = candidate;
      s.status = 'ready';
      return this.snapshot(id);
    } catch (error) {
      await this.#closeCandidate(s, candidate);
      if (s.generation === generation) s.status = 'failed';
      fail(codeOf(error, 'CONNECTION_FAILED'));
    }
  }
  async disconnect(id) {
    const s = this.#server(id);
    this.#invalidate(s);
    await s.cleanup;
    if (s.cleanupFailed) fail('CLEANUP_FAILED');
  }
  #callGuard(s, generation, tool, policyRevision) {
    this.#connectionGuard(s, generation);
    if (s.status !== 'ready' || !s.transport) fail('NOT_CONNECTED');
    const policy = this.#policies.get(this.#key(s.id, tool));
    if (!policy) fail('POLICY_NOT_LOADED');
    if (policy.decision === 'blocked') fail('TOOL_BLOCKED');
    if (policyRevision !== undefined && policy.revision !== policyRevision) fail('POLICY_CHANGED');
    return policy;
  }
  operation(operationId) { return this.#operations.get(operationId) ?? null; }
  async call({ serverId, tool, args, operationId }, {
    confirm = async () => false, prepare = async () => {},
  } = {}) {
    if (![serverId, tool, operationId].every(nonempty)) fail('INVALID_CALL');
    if (this.#operations.has(operationId)) fail('OPERATION_ALREADY_USED');
    // Capture immutable arguments before any asynchronous prompt or preparation.
    let request;
    try { request = freeze(copyJSON({ serverId, tool, args, operationId })); }
    catch { fail('INVALID_ARGUMENTS'); }
    const record = (status, extra = {}) => {
      const outcome = Object.freeze({ operationId, status, ...extra });
      this.#operations.set(operationId, outcome);
      return outcome;
    };
    record('preparing'); // Reserve the ID before awaiting; concurrent duplicates fail.
    let submitted = false;
    try {
      const s = this.#server(serverId);
      const generation = s.generation;
      const policy = this.#callGuard(s, generation, tool);
      const review = Object.freeze({ request, artifact: s.artifact, generation,
        endpoint: s.config.endpoint, workspace: s.config.workspace });
      if (policy.decision === 'ask') {
        if (await confirm(review) !== true) fail('USER_DECLINED');
        this.#callGuard(s, generation, tool, policy.revision);
      }
      await prepare(review);
      this.#callGuard(s, generation, tool, policy.revision);
      // No await between final check and submission. Sync throws are ambiguous too.
      submitted = true;
      record('dispatched');
      const value = await s.transport.call(request);
      this.#callGuard(s, generation, tool, policy.revision);
      return record('completed', { value: freeze(copyJSON(value)) });
    } catch (error) {
      return record(submitted ? 'unknown' : 'not-dispatched', {
        reason: codeOf(error, submitted ? 'TRANSPORT_RESULT_UNKNOWN' : 'PREPARATION_FAILED'),
        retry: submitted ? 'reconcile-only' : 'new-authorized-attempt',
      });
    }
  }
}

// A separate resource-side authority, operating on synthetic exact resource IDs.
// A real service must obtain principal from its authenticated session, never args.
export class ResourceService {
  #acl = new Map();
  #revision = 0;
  #documents;
  constructor(documents = {}) { this.#documents = new Map(Object.entries(documents)); }
  setAccess(principal, resource, actions) {
    if (![principal, resource].every(nonempty) || !Array.isArray(actions) ||
        actions.some((a) => !['read', 'write'].includes(a))) fail('INVALID_RESOURCE_POLICY');
    this.#acl.set(JSON.stringify([principal, resource]), new Set(actions));
    this.#revision += 1;
  }
  #check(principal, resource, action, revision) {
    if (!this.#acl.get(JSON.stringify([principal, resource]))?.has(action)) fail('RESOURCE_DENIED');
    if (revision !== undefined && revision !== this.#revision) fail('RESOURCE_POLICY_CHANGED');
    if (!this.#documents.has(resource)) fail('RESOURCE_MISSING');
  }
  async execute(input, authenticatedPrincipal, { beforeCommit = async () => {} } = {}) {
    const { tool, args } = freeze(copyJSON(input));
    const action = new Map([['read_document', 'read'], ['append_note', 'write']]).get(tool);
    if (!action || !args || !nonempty(args.resource) ||
        (action === 'write' && typeof args.text !== 'string')) fail('INVALID_RESOURCE_CALL');
    // Classification is owned by this service, not by annotations in input.
    const revision = this.#revision;
    this.#check(authenticatedPrincipal, args.resource, action);
    await beforeCommit();
    this.#check(authenticatedPrincipal, args.resource, action, revision);
    if (action === 'write') this.#documents.set(args.resource, this.#documents.get(args.resource) + args.text);
    return this.#documents.get(args.resource);
  }
}
