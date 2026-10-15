import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createLease, startHandoff, RELEASE_CONFIRMED,
} from './resource-handoff.mjs';

const turn = () => new Promise(resolve => setImmediate(resolve));
const pending = () => Promise.withResolvers();
const confirmed = () => RELEASE_CONFIRMED;
async function owned(cleanup = confirmed) {
  const task = startHandoff({ acquire: () => createLease(cleanup) });
  const offer = await task.ready;
  const owner = offer.claim();
  assert.ok(owner);
  return { task, offer, owner };
}

// These are original tests of ordinary JS objects. No OS descriptors are opened
// or closed; all numeric identifiers below belong to synthetic registries.

test('queued cancellation suppresses acquire and has no resource', async () => {
  let acquired = 0;
  const task = startHandoff({ acquire() { acquired++; return createLease(confirmed); } });
  assert.equal(task.cancel('before-start'), true);
  assert.equal(await task.ready, null);
  assert.equal(acquired, 0);
  assert.equal(task.inspect().resource, null);
  assert.equal(task.inspect().phase, 'cancelled');
});

test('synchronous cancellation inside acquire does not orphan its returned lease', async () => {
  let closes = 0;
  let task;
  task = startHandoff({ acquire() {
    assert.equal(task.cancel('inside-acquire'), true);
    return createLease(() => { closes++; return RELEASE_CONFIRMED; });
  } });
  assert.equal(await task.ready, null);
  assert.equal(closes, 1);
  assert.equal(task.inspect().resource.state, 'released');
});

test('pending cancellation waits for and cleans a late lease', async () => {
  const gate = pending();
  let closes = 0;
  const task = startHandoff({ acquire: () => gate.promise });
  await Promise.resolve();
  assert.equal(task.inspect().phase, 'acquiring');
  task.cancel();
  let settled = false;
  task.ready.then(() => { settled = true; });
  await turn();
  assert.equal(settled, false);
  gate.resolve(createLease(() => { closes++; return RELEASE_CONFIRMED; }));
  assert.equal(await task.ready, null);
  assert.equal(closes, 1);
});

test('offer Promise settlement is not transfer even when cancel observer runs first', async () => {
  let closes = 0;
  const task = startHandoff({ acquire: () => createLease(() => { closes++; return RELEASE_CONFIRMED; }) });
  const cancellation = task.ready.then(offer => {
    assert.ok(offer);
    assert.equal(task.inspect().phase, 'offered');
    assert.equal(task.inspect().resource.state, 'producer-owned');
    assert.equal(task.cancel(), true);
    return offer;
  });
  const laterObserver = task.ready.then(offer => offer.claim());
  assert.ok(await cancellation);
  assert.equal(await laterObserver, null);
  assert.equal(closes, 1);
});

test('two ready observers cannot both claim', async () => {
  let closes = 0;
  const task = startHandoff({ acquire: () => createLease(() => { closes++; return RELEASE_CONFIRMED; }) });
  const left = task.ready.then(o => o.claim());
  const right = task.ready.then(o => o.claim());
  const [a, b] = await Promise.all([left, right]);
  assert.ok(a);
  assert.equal(b, null);
  assert.equal(task.cancel(), false);
  assert.equal(task.failDelivery(new Error('stale failure')), false);
  assert.equal(closes, 0);
  assert.equal(a.close().state, 'released');
  assert.equal(closes, 1);
});

test('acquisition thenable can cancel synchronously after resolving without losing cleanup', async () => {
  let closes = 0;
  let task;
  task = startHandoff({ acquire: () => ({ then(resolve) {
    resolve(createLease(() => { closes++; return RELEASE_CONFIRMED; }));
    task.cancel('thenable-after-resolve');
  } }) });
  assert.equal(await task.ready, null);
  assert.equal(closes, 1);
});

test('delivery failure before a late acquisition retains failure and cleans the result', async () => {
  const gate = pending();
  const failure = new Error('receiver disappeared');
  let closes = 0;
  const task = startHandoff({ acquire: () => gate.promise });
  await Promise.resolve();
  assert.equal(task.failDelivery(failure), true);
  gate.resolve(createLease(() => { closes++; return RELEASE_CONFIRMED; }));
  assert.equal(await task.ready, null);
  assert.equal(task.inspect().failure, failure);
  assert.equal(task.inspect().phase, 'failed');
  assert.equal(closes, 1);
});

test('pending cancellation followed by rejection preserves both cancellation and acquisition error', async () => {
  const gate = pending();
  const rejected = new Error('acquire rejected');
  const task = startHandoff({ acquire: () => gate.promise });
  await Promise.resolve();
  task.cancel('cancel reason');
  gate.reject(rejected);
  assert.equal(await task.ready, null);
  assert.equal(task.inspect().phase, 'cancelled');
  assert.equal(task.inspect().cancellationReason, 'cancel reason');
  assert.equal(task.inspect().acquisitionError, rejected);
});

test('post-claim consumer throw leaves cleanup solely with consumer', async () => {
  let closes = 0;
  const { task, owner } = await owned(() => { closes++; return RELEASE_CONFIRMED; });
  try { throw new Error('consumer work failed'); }
  catch { assert.equal(task.failDelivery(new Error('too late')), false); }
  assert.equal(task.cancel(), false);
  assert.equal(owner.inspect().state, 'consumer-owned');
  assert.equal(closes, 0);
  owner.close();
  assert.equal(closes, 1);
});

test('cleanup does not receive mutable internal record as this', async () => {
  let receiver = 'not called';
  const { owner } = await owned(function () { receiver = this; return RELEASE_CONFIRMED; });
  owner.close();
  assert.equal(receiver, undefined);
});

test('synchronous cleanup reentry observes guard and never retries', async () => {
  let calls = 0;
  let during;
  let task, offer, owner;
  ({ task, offer, owner } = await owned(() => {
    calls++;
    during = owner.close();
    assert.equal(owner.inspect().state, 'cleaning');
    assert.equal(offer.claim(), null);
    assert.equal(task.cancel(), false);
    assert.equal(task.failDelivery(), false);
    return RELEASE_CONFIRMED;
  }));
  const done = owner.close();
  assert.equal(during.state, 'cleaning');
  assert.equal(done.state, 'released');
  assert.equal(during.state, 'cleaning', 'snapshot does not become live final state');
  owner.close();
  assert.equal(calls, 1);
});

test('producer cleanup cannot reclaim itself through saved offer', async () => {
  let offer;
  let calls = 0;
  const task = startHandoff({ acquire: () => createLease(() => {
    calls++;
    assert.equal(task.cancel(), false);
    assert.equal(task.failDelivery(), false);
    assert.equal(offer.claim(), null);
    assert.equal(task.inspect().resource.state, 'cleaning');
    return RELEASE_CONFIRMED;
  }) });
  offer = await task.ready;
  assert.equal(task.cancel(), true);
  assert.equal(calls, 1);
});

test('cleanup effect followed by throw is unknown and cannot be retried', async () => {
  const error = new Error('throw after external effect');
  let calls = 0;
  let effects = 0;
  const { owner } = await owned(() => { calls++; effects++; throw error; });
  const first = owner.close();
  assert.equal(first.state, 'outcome-unknown');
  assert.equal(first.cleanupError, error);
  for (let i = 0; i < 50; i++) owner.close();
  assert.equal(calls, 1);
  assert.equal(effects, 1);
});

test('throw before effect is equally unknown; model cannot infer release failure', async () => {
  let effects = 0;
  const { owner } = await owned(() => { throw new Error('before effect'); effects++; });
  assert.equal(owner.close().state, 'outcome-unknown');
  owner.close();
  assert.equal(effects, 0);
  assert.equal(owner.inspect().cleanupAttempts, 1);
});

for (const value of [undefined, null, false, true, 0, 'released', {}, Symbol('release-confirmed')]) {
  test(`non-confirming cleanup value (${String(value)}) remains unknown`, async () => {
    let calls = 0;
    const { owner } = await owned(() => { calls++; return value; });
    assert.equal(owner.close().state, 'outcome-unknown');
    owner.close();
    assert.equal(calls, 1);
  });
}

test('fulfilling Promise with confirmation cannot convert async misuse into released', async () => {
  let calls = 0;
  const { owner } = await owned(() => { calls++; return Promise.resolve(RELEASE_CONFIRMED); });
  assert.equal(owner.close().state, 'outcome-unknown');
  await turn();
  assert.equal(owner.inspect().state, 'outcome-unknown');
  owner.close();
  assert.equal(calls, 1);
});

test('rejected cleanup Promise is observed but remains unknown', async () => {
  let calls = 0;
  const { owner } = await owned(() => { calls++; return Promise.reject(new Error('async cleanup rejected')); });
  assert.equal(owner.close().state, 'outcome-unknown');
  await turn();
  assert.equal(owner.inspect().state, 'outcome-unknown');
  owner.close();
  assert.equal(calls, 1);
});

test('throwing then getter cannot escape close or enable cleanup retry', async () => {
  let calls = 0;
  let reads = 0;
  const { owner } = await owned(() => {
    calls++;
    return { get then() { reads++; throw new Error('then getter failed'); } };
  });
  assert.equal(owner.close().state, 'outcome-unknown');
  await turn();
  owner.close();
  assert.equal(calls, 1);
  assert.ok(reads <= 1, 'diagnostics must not repeatedly probe a hostile getter');
});

test('thenable diagnostic reentry cannot claim, cancel, close twice, or report release', async () => {
  let cleanupCalls = 0;
  let thenCalls = 0;
  let task, offer, owner;
  ({ task, offer, owner } = await owned(() => {
    cleanupCalls++;
    return { then(resolve, reject) {
      thenCalls++;
      assert.equal(owner.close().cleanupAttempts, 1);
      assert.equal(task.cancel(), false);
      assert.equal(offer.claim(), null);
      resolve(RELEASE_CONFIRMED);
      reject(new Error('ignored second outcome'));
      throw new Error('throw after resolution');
    } };
  }));
  assert.equal(owner.close().state, 'outcome-unknown');
  await turn();
  assert.equal(owner.inspect().state, 'outcome-unknown');
  assert.equal(cleanupCalls, 1);
  assert.equal(thenCalls, 1);
});

test('late rejected Promise after cleanup reentry cannot cause another attempt', async () => {
  const gate = pending();
  let calls = 0;
  let owner;
  ({ owner } = await owned(() => { calls++; assert.equal(owner.close().state, 'cleaning'); return gate.promise; }));
  owner.close();
  owner.close();
  gate.reject(new Error('late rejection'));
  await turn();
  assert.equal(calls, 1);
  assert.equal(owner.inspect().state, 'outcome-unknown');
});

test('same numeric slot can be reallocated during old cleanup without stale capability touching it', async () => {
  let nextGeneration = 0;
  let live = null;
  let closes = [];
  function allocate() {
    assert.equal(live, null);
    const identity = Object.freeze({ slot: 7, generation: ++nextGeneration });
    live = identity;
    return identity;
  }
  const a = allocate();
  let b, second;
  const first = await owned(() => {
    assert.equal(live, a);
    closes.push(a.generation);
    live = null;
    b = allocate();
    second = startHandoff({ acquire: () => createLease(() => {
      assert.equal(live, b);
      closes.push(b.generation);
      live = null;
      return RELEASE_CONFIRMED;
    }) });
    return RELEASE_CONFIRMED;
  });
  first.owner.close();
  const secondOwner = (await second.ready).claim();
  for (let i = 0; i < 20; i++) {
    first.owner.close();
    first.task.cancel();
    first.task.failDelivery();
    first.offer.claim();
  }
  assert.equal(live, b);
  assert.equal(a.slot, b.slot);
  assert.notEqual(a.generation, b.generation);
  assert.deepEqual(closes, [a.generation]);
  secondOwner.close();
  assert.equal(live, null);
  assert.deepEqual(closes, [a.generation, b.generation]);
});

test('concurrent attempts to deliver one lease cannot steal its accepted owner', async () => {
  let closes = 0;
  const lease = createLease(() => { closes++; return RELEASE_CONFIRMED; });
  const first = startHandoff({ acquire: () => lease });
  const second = startHandoff({ acquire: () => lease });
  const [offer, rejected] = await Promise.all([first.ready, second.ready]);
  assert.ok(offer);
  assert.equal(rejected, null);
  assert.equal(second.inspect().phase, 'failed');
  assert.equal(closes, 0);
  second.cancel();
  const owner = offer.claim();
  assert.ok(owner);
  owner.close();
  assert.equal(closes, 1);
});

test('duplicate wrappers of one underlying resource remain caller violation, not false guarantee', async () => {
  // Deliberately invalid input: two distinct leases alias a single synthetic
  // resource. The model promises per-lease attempts, not alias discovery.
  let rawAttempts = 0;
  const cleanup = () => { rawAttempts++; return RELEASE_CONFIRMED; };
  const a = await owned(cleanup);
  const b = await owned(cleanup);
  a.owner.close();
  b.owner.close();
  assert.equal(rawAttempts, 2);
});

test('resource concealed by rejected acquisition remains outside model visibility', async () => {
  let concealedEffects = 0;
  const task = startHandoff({ acquire() {
    createLease(() => { concealedEffects++; return RELEASE_CONFIRMED; });
    throw new Error('resource never returned');
  } });
  assert.equal(await task.ready, null);
  assert.equal(task.inspect().resource, null);
  assert.equal(concealedEffects, 0);
});

test('lease, offer, owner, task and snapshots are immutable capabilities', async () => {
  const lease = createLease(confirmed);
  assert.equal(Object.getPrototypeOf(lease), null);
  assert.deepEqual(Object.keys(lease), []);
  const task = startHandoff({ acquire: () => lease });
  const offer = await task.ready;
  const owner = offer.claim();
  for (const value of [lease, task, offer, owner, task.inspect(), owner.inspect()]) {
    assert.equal(Object.isFrozen(value), true);
  }
  const close = owner.close;
  assert.equal(close().state, 'released', 'owner method does not require a receiver');
});

test('bounded operation sequences agree with an independent ownership automaton', async () => {
  const alphabet = ['cancel', 'fail', 'claim', 'close'];
  for (const outcome of ['released', 'outcome-unknown']) {
    // Exhaustively enumerate all 4^5 action words after offer publication.
    // This is bounded model checking, not a proof for arbitrary programs.
    for (let word = 0; word < 4 ** 5; word++) {
      let calls = 0;
      const task = startHandoff({ acquire: () => createLease(() => {
        calls++;
        if (outcome === 'outcome-unknown') throw new Error('synthetic uncertain effect');
        return RELEASE_CONFIRMED;
      }) });
      const offer = await task.ready;
      let owner = null;
      let expectedPhase = 'offered';
      let expectedResource = 'producer-owned';
      let expectedCalls = 0;
      let digits = word;
      const sequence = [];
      for (let step = 0; step < 5; step++) {
        const action = alphabet[digits % 4];
        digits = Math.floor(digits / 4);
        sequence.push(action);
        const context = `${outcome}: ${sequence.join(' -> ')}`;
        if (action === 'cancel' || action === 'fail') {
          const accepted = expectedPhase === 'offered';
          const observed = action === 'cancel' ? task.cancel() : task.failDelivery();
          assert.equal(observed, accepted, context);
          if (accepted) {
            expectedPhase = action === 'cancel' ? 'cancelled' : 'failed';
            expectedResource = outcome;
            expectedCalls++;
          }
        } else if (action === 'claim') {
          const claim = offer.claim();
          if (expectedPhase === 'offered') {
            assert.ok(claim, context);
            owner = claim;
            expectedPhase = 'transferred';
            expectedResource = 'consumer-owned';
          } else assert.equal(claim, null, context);
        } else if (owner) {
          owner.close();
          if (expectedResource === 'consumer-owned') {
            expectedResource = outcome;
            expectedCalls++;
          }
        }
        assert.equal(task.inspect().phase, expectedPhase, context);
        assert.equal(task.inspect().resource.state, expectedResource, context);
        assert.equal(calls, expectedCalls, context);
      }
      if (owner) owner.close();
      else task.cancel();
      assert.equal(calls, 1);
    }
  }
});

test('producer-side cancellation observes rejected cleanup thenable without changing cancelled', async () => {
  let calls = 0;
  let observed = 0;
  const task = startHandoff({ acquire: () => createLease(() => {
    calls++;
    return { then(_resolve, reject) { observed++; reject(new Error('thenable rejected')); } };
  }) });
  const offer = await task.ready;
  assert.equal(task.cancel(), true);
  assert.equal(offer.claim(), null);
  await turn();
  assert.equal(task.inspect().phase, 'cancelled');
  assert.equal(task.inspect().resource.state, 'outcome-unknown');
  assert.equal(observed, 1);
  task.cancel();
  assert.equal(calls, 1);
});

test('unknown old cleanup after a side effect never retries against a reused numeric slot', async () => {
  let live = { slot: 7, generation: 'A' };
  const a = live;
  let attempts = 0;
  const old = await owned(() => {
    attempts++;
    assert.equal(live, a);
    live = { slot: 7, generation: 'B' }; // Synthetic release + reuse already happened.
    throw new Error('status lost after release');
  });
  assert.equal(old.owner.close().state, 'outcome-unknown');
  const b = live;
  for (let i = 0; i < 20; i++) {
    old.owner.close();
    old.task.cancel();
    old.task.failDelivery();
  }
  assert.equal(attempts, 1);
  assert.equal(live, b);
  assert.equal(live.generation, 'B');
});

test('native rejected Promise with poisoned instance then is observed using the intrinsic method', async () => {
  let reads = 0;
  const reason = new Error('native rejection');
  const returned = Promise.reject(reason);
  Object.defineProperty(returned, 'then', { get() { reads++; throw new Error('poisoned instance then'); } });
  const { owner } = await owned(() => returned);
  assert.equal(owner.close().state, 'outcome-unknown');
  await turn();
  assert.equal(reads, 0);
  assert.equal(owner.inspect().returnObservation.state, 'rejected');
  assert.equal(owner.inspect().returnObservation.error, reason);
});

test('constructor getter observation failure is contained after the unknown guard', async () => {
  const gate = pending();
  // A separate harness observer prevents this intentionally unsupported object
  // from causing an unhandled rejection. It does not repair model observation.
  const harnessObserved = gate.promise.catch(() => {});
  let owner;
  let reads = 0;
  const observationError = new Error('constructor getter failed');
  Object.defineProperty(gate.promise, 'constructor', { get() {
    reads++;
    assert.equal(owner.close().state, 'outcome-unknown');
    throw observationError;
  } });
  ({ owner } = await owned(() => gate.promise));
  const snapshot = owner.close();
  assert.equal(snapshot.state, 'outcome-unknown');
  assert.equal(snapshot.returnObservation.state, 'observation-failed');
  assert.equal(snapshot.returnObservation.error, observationError);
  gate.reject(new Error('unobservable by model'));
  await harnessObserved;
  await turn();
  assert.equal(reads, 1);
  assert.equal(owner.inspect().cleanupAttempts, 1);
  assert.equal(owner.inspect().returnObservation.state, 'observation-failed');
});
