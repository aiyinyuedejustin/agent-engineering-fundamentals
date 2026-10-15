import assert from 'node:assert/strict';
import { ScopedMutationQueue, applyQueuedOptimistic, ScopedAccessView, deferred, turn } from './settings-access.mjs';
const trace = [];
const record = (event, state) => trace.push({ step: trace.length, event, state: structuredClone(state) });
class RecordingMap extends Map {
  set(key, value) { super.set(key, value); if (this.recording) record('cache-write', { org: key, ...value }); return this; }
}
const cache = new RecordingMap([['org-a', { enabled: false, mode: 'summary', revision: 7 }]]);
cache.recording = true;
const queue = new ScopedMutationQueue(), firstReply = deferred(), secondReply = deferred();
record('initial', cache.get('org-a'));
const first = applyQueuedOptimistic(queue, 'org-a', cache, { enabled: true }, () => firstReply.promise);
// Attach rejection handling before driving the synthetic failure.
const firstObserved = first.then(() => 'unexpected-success', error => error.message);
const second = applyQueuedOptimistic(queue, 'org-a', cache, { mode: 'topics' }, () => {
  assert.deepEqual(cache.get('org-a'), { enabled: false, mode: 'topics', revision: 7 });
  record('second-save-starts-after-rollback', cache.get('org-a'));
  return secondReply.promise;
});
record('both-submitted', cache.get('org-a'));
await turn();
firstReply.reject(new Error('offline'));
await turn();
assert.equal(await firstObserved, 'offline');
secondReply.resolve({ enabled: false, mode: 'topics', revision: 8, serverNormalized: true });
await second; await turn();
assert.equal(queue.pendingScopes, 0);
record('queue-drained', { pendingScopes: queue.pendingScopes });

const view = new ScopedAccessView('org-a', { org: 'org-a', checkedAt: 0, state: 'available', allowed: true });
const lateA = deferred();
// now=1000, maxAge=100: the old allow cannot be used without a refresh.
const startA = view.mayStartAction(1000, 100, org => {
  assert.equal(org, 'org-a'); record('refresh-a-start', { org, oldAllowExpired: true }); return lateA.promise;
});
view.switchOrg('org-b');
record('switch-to-b', { org: view.org, snapshot: view.snapshot ?? null });
const readB = view.beginRead();
view.receive(readB, { org: 'org-b', clientGate: true, serverStatus: 'blocked_by_org_admin', userEnabled: true }, 1001);
record('current-b-deny', view.snapshot);
lateA.resolve({ org: 'org-a', clientGate: true, serverStatus: 'available', userEnabled: true });
const allowedA = await startA;
assert.equal(allowedA, false);
assert.equal(view.snapshot.org, 'org-b');
assert.equal(view.snapshot.allowed, false);
record('late-a-allow-ignored', { startA: allowedA, current: view.snapshot });
if (process.argv.includes('--json')) console.log(JSON.stringify(trace, null, 2));
else {
  for (const entry of trace) console.log(`${String(entry.step).padStart(2, '0')} ${entry.event} ${JSON.stringify(entry.state)}`);
}
