import test from 'node:test';
import assert from 'node:assert/strict';
import { ScopedMutationQueue, decideAccess, readBoundedNumber, evaluateCapabilityGraph, LatestRequestGuard, applyQueuedOptimistic, resolveFreshAccess } from './memory-flags-model.mjs';
const tick = () => new Promise(resolve => setImmediate(resolve));

test('one scope preserves submission order', async () => {
  const queue = new ScopedMutationQueue(), seen = [];
  let release; const held = new Promise(resolve => { release = resolve; });
  const one = queue.run('org-a', async () => { seen.push('start-a'); await held; seen.push('end-a'); });
  const two = queue.run('org-a', () => { seen.push('start-b'); });
  await tick(); assert.deepEqual(seen, ['start-a']);
  release(); await Promise.all([one, two]);
  assert.deepEqual(seen, ['start-a', 'end-a', 'start-b']);
});
test('another scope progresses while the first is pending', async () => {
  const queue = new ScopedMutationQueue();
  let release; const held = new Promise(resolve => { release = resolve; });
  const one = queue.run('org-a', () => held);
  assert.equal(await queue.run('org-b', () => 42), 42);
  release(); await one;
});
test('rejection is observable and does not poison later work', async () => {
  const queue = new ScopedMutationQueue();
  const failed = queue.run('org-a', () => { throw new Error('save failed'); });
  const next = queue.run('org-a', () => 'saved');
  await assert.rejects(failed, /save failed/); assert.equal(await next, 'saved');
  await tick(); assert.equal(queue.pendingScopes, 0);
});
test('policy refusal cannot be replaced by user preference', () => {
  assert.deepEqual(decideAccess({ clientGate: true, serverStatus: 'blocked_by_org_admin', userEnabled: true }), { state: 'blocked_by_org_admin', allowed: false });
});
test('unknown is distinct from off', () => {
  assert.equal(decideAccess({ clientGate: undefined }).state, 'loading');
  assert.equal(decideAccess({ clientGate: false }).state, 'platform');
  assert.equal(decideAccess({ clientGate: true }).state, 'loading');
});
test('user pause is reversible without changing availability policy', () => {
  const base = { clientGate: true, serverStatus: 'available' };
  assert.equal(decideAccess({ ...base, userEnabled: false }).allowed, false);
  assert.equal(decideAccess({ ...base, userEnabled: true }).allowed, true);
});
test('invalid remote numeric data uses a typed fallback', () => {
  for (const value of [NaN, Infinity, '120', null, {}]) assert.deepEqual(readBoundedNumber(value, 10, 1, 60), { value: 10, source: 'invalid' });
  assert.equal(readBoundedNumber(undefined, 10, 1, 60).source, 'absent');
  assert.equal(readBoundedNumber(1000, 10, 1, 60).value, 60);
  assert.equal(readBoundedNumber(-1, 10, 1, 60).value, 1);
});
test('dependency graph orders prerequisites before consumers', () => {
  assert.deepEqual(evaluateCapabilityGraph({ create: { dependsOn: ['skills'] }, skills: { dependsOn: ['chat'] }, chat: { dependsOn: [] } }), ['chat', 'skills', 'create']);
});
test('cycles and absent dependencies fail clearly', () => {
  assert.throws(() => evaluateCapabilityGraph({ a: { dependsOn: ['b'] }, b: { dependsOn: ['a'] } }), /cycle/);
  assert.throws(() => evaluateCapabilityGraph({ a: { dependsOn: ['missing'] } }), /Unknown/);
});

test('an older response cannot become current after a new edit starts', () => {
  const guard = new LatestRequestGuard();
  const first = guard.begin(), second = guard.begin();
  assert.equal(first.isCurrent(), false);
  assert.equal(second.isCurrent(), true);
  guard.invalidate(); assert.equal(second.isCurrent(), false);
});
test('an optimistic failure rolls back before the queued edit begins', async () => {
  const queue = new ScopedMutationQueue(), cache = new Map([['org-a', { enabled: false }]]);
  let reject; const pending = new Promise((_, fail) => { reject = fail; });
  const first = applyQueuedOptimistic(queue, 'org-a', cache, { enabled: true }, () => pending);
  const observed = assert.rejects(first, /offline/);
  const second = applyQueuedOptimistic(queue, 'org-a', cache, { mode: 'topics' }, async () => {
    assert.deepEqual(cache.get('org-a'), { enabled: false, mode: 'topics' });
    return { enabled: false, mode: 'topics', confirmed: true };
  });
  await tick(); assert.equal(cache.get('org-a').enabled, true);
  reject(new Error('offline')); await observed; await second;
  assert.deepEqual(cache.get('org-a'), { enabled: false, mode: 'topics', confirmed: true });
});
test('failed optimistic creation restores absence, not an undefined row', async () => {
  const cache = new Map();
  await assert.rejects(applyQueuedOptimistic(new ScopedMutationQueue(), 'org-a', cache, {}, async () => { throw new Error('denied'); }));
  assert.equal(cache.has('org-a'), false);
});
test('a recent access snapshot does not trigger another read', async () => {
  assert.equal(await resolveFreshAccess({ allowed: true, checkedAt: 90 }, 100, 20, async () => { throw new Error('should not run'); }), true);
});
test('a stale allowed snapshot cannot survive a failed permission refresh', async () => {
  assert.equal(await resolveFreshAccess({ allowed: true, checkedAt: 0 }, 100, 20, async () => { throw new Error('offline'); }), false);
});
test('a stale or future-dated snapshot is replaced by the fresh verdict', async () => {
  for (const checkedAt of [0, 200]) {
    assert.equal(await resolveFreshAccess({ allowed: true, checkedAt }, 100, 20, async () => ({ allowed: false })), false);
  }
});
