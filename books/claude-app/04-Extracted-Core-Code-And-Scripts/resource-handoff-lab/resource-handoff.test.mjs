import test from 'node:test';
import assert from 'node:assert/strict';
import { createLease, startHandoff, RELEASE_CONFIRMED } from './resource-handoff.mjs';

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
function tracked(cleanup = () => RELEASE_CONFIRMED) {
  let calls = 0;
  return {
    lease: createLease(() => { calls += 1; return cleanup(); }),
    calls: () => calls,
  };
}
async function offered(resource = tracked()) {
  const task = startHandoff({ acquire: () => resource.lease });
  const offer = await task.ready;
  return { task, offer, resource };
}
const drain = () => new Promise((resolve) => setImmediate(resolve));

test('opaque lease contains no numeric handle or methods and cannot be mutated', () => {
  const lease = createLease(() => RELEASE_CONFIRMED);
  assert.equal(Object.getPrototypeOf(lease), null);
  assert.deepEqual(Reflect.ownKeys(lease), []);
  assert.equal(Object.isFrozen(lease), true);
  assert.throws(() => { lease.fd = 7; }, TypeError);
});

test('invalid callbacks fail before any acquisition or cleanup', () => {
  assert.throws(() => createLease(null), TypeError);
  assert.throws(() => startHandoff({ acquire: 7 }), TypeError);
});

test('cancellation before acquisition starts never invokes acquire', async () => {
  let acquisitions = 0;
  const task = startHandoff({ acquire() { acquisitions += 1; return tracked().lease; } });
  assert.equal(task.cancel('no longer needed'), true);
  assert.equal(task.cancel(), false);
  assert.equal(await task.ready, null);
  assert.equal(acquisitions, 0);
  assert.equal(task.inspect().resource, null);
});

test('cancellation during acquisition stays pending, then cleans late success', async () => {
  const pending = deferred();
  const resource = tracked();
  const task = startHandoff({ acquire: () => pending.promise });
  await Promise.resolve();
  assert.equal(task.inspect().phase, 'acquiring');
  assert.equal(task.cancel(), true);
  let readySettled = false;
  task.ready.then(() => { readySettled = true; });
  await drain();
  assert.equal(readySettled, false);
  assert.equal(resource.calls(), 0);
  pending.resolve(resource.lease);
  assert.equal(await task.ready, null);
  assert.equal(resource.calls(), 1);
  assert.equal(task.inspect().resource.state, 'released');
});

test('a cancelled producer may still reject; preserve both observations', async () => {
  const pending = deferred();
  const error = new Error('acquisition failed late');
  const task = startHandoff({ acquire: () => pending.promise });
  await Promise.resolve();
  task.cancel('view closed');
  pending.reject(error);
  assert.equal(await task.ready, null);
  assert.equal(task.inspect().phase, 'cancelled');
  assert.equal(task.inspect().cancellationReason, 'view closed');
  assert.equal(task.inspect().acquisitionError, error);
});

test('acquire may synchronously request cancellation and still return a lease', async () => {
  const resource = tracked();
  const task = startHandoff({ acquire: () => { task.cancel(); return resource.lease; } });
  assert.equal(await task.ready, null);
  assert.equal(resource.calls(), 1);
});

test('ready/Promise.resolve successful delivery is not consumer ownership', async () => {
  const { task, offer, resource } = await offered();
  assert.equal(await Promise.resolve(offer), offer);
  assert.equal(task.inspect().phase, 'offered');
  assert.equal(task.inspect().resource.state, 'producer-owned');
  assert.equal(resource.calls(), 0);
  task.cancel();
  assert.equal(offer.claim(), null);
  assert.equal(resource.calls(), 1);
});

test('fulfilled ready remains fulfilled when its old offer is cancelled', async () => {
  const { task, offer } = await offered();
  task.cancel();
  assert.equal(await task.ready, offer);
  assert.equal(offer.claim(), null);
  assert.equal(task.inspect().phase, 'cancelled');
});

test('first claim transfers ownership; second claim and producer cancellation cannot revoke it', async () => {
  const { task, offer, resource } = await offered();
  const owner = offer.claim();
  assert.ok(owner);
  assert.equal(offer.claim(), null);
  assert.equal(task.cancel(), false);
  assert.equal(task.failDelivery(new Error('too late')), false);
  assert.equal(resource.calls(), 0);
  assert.equal(owner.inspect().state, 'consumer-owned');
  assert.equal(owner.close().state, 'released');
  assert.equal(task.inspect().phase, 'transferred');
});

test('claim before a queued cancellation wins; cancellation before queued claim wins', async () => {
  const first = await offered();
  const cancel = Promise.resolve().then(() => first.task.cancel());
  const owner = first.offer.claim();
  assert.equal(await cancel, false);
  owner.close();
  const second = await offered();
  const claim = Promise.resolve().then(() => second.offer.claim());
  assert.equal(second.task.cancel(), true);
  assert.equal(await claim, null);
  assert.equal(second.resource.calls(), 1);
});

test('receiver throws after claim: ownership remains consumer-side until finally closes', async () => {
  const { task, offer, resource } = await offered();
  let owner;
  assert.throws(() => {
    owner = offer.claim();
    throw new Error('consumer failed after taking ownership');
  }, /consumer failed/);
  assert.equal(task.inspect().phase, 'transferred');
  assert.equal(resource.calls(), 0);
  try { throw new Error('body failed'); }
  catch { /* consumer handles its own failure */ }
  finally { owner.close(); }
  assert.equal(resource.calls(), 1);
});

test('delivery failure before acquisition starts prevents the acquisition', async () => {
  let acquisitions = 0;
  const task = startHandoff({ acquire() { acquisitions += 1; return tracked().lease; } });
  const error = new Error('destination disappeared');
  assert.equal(task.failDelivery(error), true);
  assert.equal(await task.ready, null);
  assert.equal(task.inspect().failure, error);
  assert.equal(acquisitions, 0);
});

test('delivery failure while acquiring cleans a later resource', async () => {
  const pending = deferred();
  const resource = tracked();
  const task = startHandoff({ acquire: () => pending.promise });
  await Promise.resolve();
  task.failDelivery('destination unavailable');
  pending.resolve(resource.lease);
  assert.equal(await task.ready, null);
  assert.equal(resource.calls(), 1);
  assert.equal(task.inspect().phase, 'failed');
});

test('delivery failure after an offer prevents claim and retains the original failure', async () => {
  const { task, offer, resource } = await offered();
  const error = new Error('serialization failed');
  assert.equal(task.failDelivery(error), true);
  assert.equal(task.cancel(), false);
  assert.equal(task.failDelivery('overwrite'), false);
  assert.equal(offer.claim(), null);
  assert.equal(task.inspect().failure, error);
  assert.equal(resource.calls(), 1);
});

test('a synchronous acquisition exception is reported without fabricating a resource', async () => {
  const error = new Error('no resource');
  const task = startHandoff({ acquire() { throw error; } });
  assert.equal(await task.ready, null);
  assert.equal(task.inspect().phase, 'failed');
  assert.equal(task.inspect().acquisitionError, error);
  assert.equal(task.inspect().resource, null);
});

test('resource concealed by a failed acquire cannot be reclaimed by this model', async () => {
  const hidden = tracked();
  const task = startHandoff({ acquire() { throw new Error('allocated, then lost the lease'); } });
  assert.equal(await task.ready, null);
  assert.equal(hidden.calls(), 0); // Intentionally demonstrates a contract breach.
  assert.equal(task.inspect().resource, null);
  const recovery = await offered(hidden); // Test fixture retains it and cleans up.
  recovery.task.cancel();
});

test('a forged lease or raw integer is rejected, never interpreted as a close target', async () => {
  for (const value of [7, null, undefined, {}, Object.freeze(Object.create(null))]) {
    const task = startHandoff({ acquire: () => value });
    assert.equal(await task.ready, null);
    assert.equal(task.inspect().phase, 'failed');
    assert.equal(task.inspect().resource, null);
  }
});

test('two tasks cannot acquire the same opaque lease and cleanup the first owner', async () => {
  const resource = tracked();
  const first = await offered(resource);
  const second = startHandoff({ acquire: () => resource.lease });
  assert.equal(await second.ready, null);
  assert.equal(resource.calls(), 0);
  assert.equal(first.task.inspect().resource.state, 'producer-owned');
  first.task.cancel();
  assert.equal(resource.calls(), 1);
});

test('an already released lease cannot be recycled into a new task', async () => {
  const resource = tracked();
  const first = await offered(resource);
  first.task.cancel();
  const second = startHandoff({ acquire: () => resource.lease });
  assert.equal(await second.ready, null);
  assert.equal(resource.calls(), 1);
});

test('repeated close is stable and never calls cleanup twice', async () => {
  const { offer, resource } = await offered();
  const owner = offer.claim();
  for (let i = 0; i < 10; i += 1) {
    assert.equal(owner.close().state, 'released');
  }
  assert.equal(resource.calls(), 1);
  assert.equal(owner.inspect().cleanupAttempts, 1);
});

test('cleanup reenters consumer close: inner sees cleaning; outer releases once', async () => {
  let owner, nested, observedDuring;
  const resource = tracked(() => {
    observedDuring = owner.inspect();
    nested = owner.close();
    return RELEASE_CONFIRMED;
  });
  const { offer } = await offered(resource);
  owner = offer.claim();
  assert.equal(owner.close().state, 'released');
  assert.equal(nested.state, 'cleaning');
  assert.equal(observedDuring.state, 'cleaning');
  assert.equal(nested.state, 'cleaning'); // A snapshot does not update itself.
  assert.equal(resource.calls(), 1);
});

test('producer cleanup reenters cancel, failure and stale claim without transferring', async () => {
  let task, offer;
  const observations = [];
  const resource = tracked(() => {
    observations.push(task.cancel(), task.failDelivery('reentry'), offer.claim());
    return RELEASE_CONFIRMED;
  });
  ({ task, offer } = await offered(resource));
  task.cancel();
  assert.deepEqual(observations, [false, false, null]);
  assert.equal(resource.calls(), 1);
});

test('cleanup throws before side effect: unknown is distinct from successfully released', async () => {
  const error = new Error('before releasing');
  const resource = tracked(() => { throw error; });
  const { offer } = await offered(resource);
  const owner = offer.claim();
  assert.equal(owner.close().state, 'outcome-unknown');
  assert.equal(owner.close().cleanupError, error);
  assert.equal(resource.calls(), 1); // A leak is possible; blind retry is forbidden.
});

test('cleanup throws after side effect: unknown must not cause a second release', async () => {
  let releases = 0;
  const resource = tracked(() => { releases += 1; throw new Error('after releasing'); });
  const { offer } = await offered(resource);
  const owner = offer.claim();
  assert.equal(owner.close().state, 'outcome-unknown');
  owner.close();
  assert.equal(releases, 1);
});

test('producer cancellation plus failed cleanup retains cancellation and cleanup error', async () => {
  const error = new Error('cannot know whether released');
  const { task } = await offered(tracked(() => { throw error; }));
  assert.equal(task.cancel('navigation'), true);
  assert.equal(task.inspect().phase, 'cancelled');
  assert.equal(task.inspect().resource.state, 'outcome-unknown');
  assert.equal(task.inspect().resource.cleanupError, error);
});

test('ordinary return values do not masquerade as confirmed cleanup', async () => {
  for (const value of [undefined, true, false, 0, 'released', {}]) {
    const { offer, resource } = await offered(tracked(() => value));
    const owner = offer.claim();
    assert.equal(owner.close().state, 'outcome-unknown');
    await drain();
    assert.equal(owner.inspect().state, 'outcome-unknown');
    assert.equal(owner.inspect().returnObservation.state, 'fulfilled');
    assert.equal(resource.calls(), 1);
  }
});

test('unexpected cleanup Promise fulfillment is observed but never retroactively confirms release', async () => {
  const pending = deferred();
  const { offer } = await offered(tracked(() => pending.promise));
  const owner = offer.claim();
  assert.equal(owner.close().state, 'outcome-unknown');
  assert.equal(owner.inspect().returnObservation.state, 'pending');
  pending.resolve(RELEASE_CONFIRMED);
  await drain();
  assert.equal(owner.inspect().state, 'outcome-unknown');
  assert.equal(owner.inspect().returnObservation.state, 'fulfilled');
});

test('unexpected cleanup Promise rejection is handled and remains visible in diagnostics', async () => {
  const pending = deferred();
  const error = new Error('asynchronous cleanup failed');
  const { offer, resource } = await offered(tracked(() => pending.promise));
  const owner = offer.claim();
  owner.close();
  pending.reject(error);
  await drain();
  assert.equal(owner.inspect().returnObservation.state, 'rejected');
  assert.equal(owner.inspect().returnObservation.error, error);
  assert.equal(owner.close().state, 'outcome-unknown');
  assert.equal(resource.calls(), 1);
});

test('then getter reentry runs after unknown state and getter errors are observed', async () => {
  let owner, observed;
  const error = new Error('then getter failed');
  const unexpected = { get then() { observed = owner.close(); throw error; } };
  const { offer, resource } = await offered(tracked(() => unexpected));
  owner = offer.claim();
  owner.close();
  assert.equal(observed.state, 'outcome-unknown');
  await drain();
  assert.equal(owner.inspect().returnObservation.error, error);
  assert.equal(resource.calls(), 1);
});

test('thenable body reentry cannot retry cleanup or transfer the old offer', async () => {
  let owner, task, offer;
  const observations = [];
  const resource = tracked(() => ({ then(resolve, reject) {
    observations.push(owner.close().state, task.cancel(), offer.claim());
    reject('thenable rejected');
    resolve(RELEASE_CONFIRMED); // First settlement wins; still not a release ack.
  } }));
  ({ task, offer } = await offered(resource));
  owner = offer.claim();
  owner.close();
  await drain();
  assert.deepEqual(observations, ['outcome-unknown', false, null]);
  assert.equal(owner.inspect().returnObservation.error, 'thenable rejected');
  assert.equal(resource.calls(), 1);
});

test('inspection and returned control capabilities cannot overwrite internal state', async () => {
  const { task, offer } = await offered();
  const snap = task.inspect();
  assert.throws(() => { snap.phase = 'transferred'; }, TypeError);
  assert.throws(() => { snap.resource.state = 'released'; }, TypeError);
  assert.throws(() => { offer.claim = () => ({}); }, TypeError);
  const owner = offer.claim();
  assert.throws(() => { owner.close = () => {}; }, TypeError);
  owner.close();
});

test('numeric-handle counterexample: closing a stale bare number can close its replacement', () => {
  const registry = new Map([[7, 'resource-A']]);
  const closeByNumber = (number) => registry.delete(number);
  closeByNumber(7);
  registry.set(7, 'resource-B');
  closeByNumber(7); // Old number accidentally targets the replacement.
  assert.equal(registry.has(7), false);
});

test('lease identity: stale owner close cannot hurt a new lease with the same numeric label', async () => {
  const registry = new Map();
  let generation = 0;
  const allocate = (number) => {
    const resource = { number, generation: ++generation };
    registry.set(number, resource);
    return createLease(() => {
      assert.equal(registry.get(number), resource, 'cleanup must target the same resource identity');
      registry.delete(number);
      return RELEASE_CONFIRMED;
    });
  };
  const firstTask = startHandoff({ acquire: () => allocate(7) });
  const first = (await firstTask.ready).claim();
  first.close();
  const secondTask = startHandoff({ acquire: () => allocate(7) });
  const second = (await secondTask.ready).claim();
  const replacement = registry.get(7);
  first.close();
  assert.equal(registry.get(7), replacement);
  assert.equal(replacement.generation, 2);
  second.close();
  assert.equal(registry.size, 0);
});

test('two different leases wrapping one underlying resource are an explicit contract violation', async () => {
  let closes = 0;
  const closeSameResource = () => { closes += 1; return RELEASE_CONFIRMED; };
  const first = await offered({ lease: createLease(closeSameResource) });
  const second = await offered({ lease: createLease(closeSameResource) });
  first.task.cancel();
  second.task.cancel();
  assert.equal(closes, 2); // Opaque tokens alone cannot discover external aliases.
});

test('an ignored offer stays producer-owned until explicit stop; no hidden GC cleanup', async () => {
  const { task, resource } = await offered();
  await drain();
  assert.equal(task.inspect().resource.state, 'producer-owned');
  assert.equal(resource.calls(), 0);
  task.cancel();
  assert.equal(resource.calls(), 1);
});

test('all 256 four-operation claim/cancel/fail/close traces respect a single cleanup attempt', async () => {
  const operations = ['claim', 'cancel', 'fail', 'close'];
  for (let encoded = 0; encoded < 256; encoded += 1) {
    const { task, offer, resource } = await offered();
    let owner = null, cursor = encoded, claims = 0;
    for (let step = 0; step < 4; step += 1) {
      const operation = operations[cursor % 4];
      cursor = Math.floor(cursor / 4);
      if (operation === 'claim') {
        const result = offer.claim();
        if (result) { owner = result; claims += 1; }
      } else if (operation === 'cancel') task.cancel();
      else if (operation === 'fail') task.failDelivery('synthetic failure');
      else owner?.close();
      assert.ok(claims <= 1, `trace ${encoded}: at most one successful claim`);
      assert.ok(resource.calls() <= 1, `trace ${encoded}: at most one cleanup call`);
    }
    if (owner) owner.close();
    else task.cancel();
    assert.equal(resource.calls(), 1, `trace ${encoded}: explicit final owner cleans`);
  }
});
