/** Original teaching model. No proprietary source or private API calls. */
export class ScopedMutationQueue {
  #tails = new Map();

  run(scope, operation) {
    const previous = this.#tails.get(scope) ?? Promise.resolve();
    const result = previous.then(operation);
    // A rejected operation must not poison the rest of this scope's queue.
    const settled = result.then(() => undefined, () => undefined);
    this.#tails.set(scope, settled);
    settled.then(() => {
      if (this.#tails.get(scope) === settled) this.#tails.delete(scope);
    });
    return result;
  }

  get pendingScopes() { return this.#tails.size; }
}

export function decideAccess({ clientGate, serverStatus, userEnabled }) {
  if (clientGate === undefined) return { state: 'loading', allowed: false };
  if (!clientGate) return { state: 'platform', allowed: false };
  if (serverStatus === undefined) return { state: 'loading', allowed: false };
  if (serverStatus !== 'available') return { state: serverStatus, allowed: false };
  if (userEnabled === false) return { state: 'user-paused', allowed: false };
  return { state: 'available', allowed: true };
}

export function readBoundedNumber(raw, fallback, min, max) {
  if (typeof raw !== 'number' || !Number.isFinite(raw)) {
    return { value: fallback, source: raw === undefined ? 'absent' : 'invalid' };
  }
  return { value: Math.max(min, Math.min(max, raw)), source: 'remote' };
}

export function evaluateCapabilityGraph(table) {
  const active = new Set(), done = new Set(), order = [];
  function visit(name) {
    if (!Object.hasOwn(table, name)) throw new Error(`Unknown dependency: ${name}`);
    if (active.has(name)) throw new Error(`Dependency cycle: ${name}`);
    if (done.has(name)) return;
    active.add(name);
    for (const dependency of table[name].dependsOn) visit(dependency);
    active.delete(name); done.add(name); order.push(name);
  }
  for (const name of Object.keys(table)) visit(name);
  return order;
}

/** A request may still resolve after transport cancellation. */
export class LatestRequestGuard {
  #version = 0;
  begin() {
    const version = ++this.#version;
    return { version, isCurrent: () => this.#version === version };
  }
  invalidate() { this.#version += 1; }
}

/** Original transactional UI example; the server result is authoritative. */
export function applyQueuedOptimistic(queue, scope, cache, patch, save) {
  return queue.run(scope, async () => {
    const previous = cache.get(scope);
    cache.set(scope, { ...previous, ...patch });
    try {
      const confirmed = await save(patch);
      cache.set(scope, confirmed);
      return confirmed;
    } catch (error) {
      if (previous === undefined) cache.delete(scope);
      else cache.set(scope, previous);
      throw error;
    }
  });
}

/** Example policy: unknown or failed refresh cannot grant a new action. */
export async function resolveFreshAccess(snapshot, now, maxAge, refresh) {
  const age = snapshot ? now - snapshot.checkedAt : Infinity;
  if (age >= 0 && age <= maxAge) return snapshot.allowed === true;
  try { return (await refresh()).allowed === true; }
  catch { return false; }
}
