import test from 'node:test';
import assert from 'node:assert/strict';
import { createLease, startHandoff, RELEASE_CONFIRMED } from './resource-handoff.mjs';

// Original adversarial audit cases. These assert the advertised isolation and
// at-most-once guarantees, rather than asserting that a known defect exists.
test('cleanup receives no internal resource record through its this receiver', async () => {
  let receiver;
  const task = startHandoff({
    acquire: () => createLease(function cleanup() {
      receiver = this;
      return RELEASE_CONFIRMED;
    }),
  });
  const owner = (await task.ready).claim();
  assert.equal(owner.close().state, 'released');
  assert.equal(receiver, undefined, 'the private mutable record must not escape as cleanup.this');
});

test('cleanup cannot use a leaked receiver to bypass the reentrant close guard', async () => {
  let calls = 0;
  let owner;
  const task = startHandoff({
    acquire: () => createLease(function cleanup() {
      calls += 1;
      if (calls === 1 && this && this.state === 'cleaning') {
        // This should never be reachable: no public API exposes the record.
        this.state = 'consumer-owned';
        owner.close();
      }
      return RELEASE_CONFIRMED;
    }),
  });
  owner = (await task.ready).claim();
  owner.close();
  owner.close();
  assert.equal(calls, 1, 'one legal lease must never invoke its cleanup twice');
  assert.equal(owner.inspect().cleanupAttempts, 1);
});

test('cleanup cannot accidentally write a property that revives a released record', async () => {
  let receiver;
  let calls = 0;
  const task = startHandoff({
    acquire: () => createLease(function cleanup() {
      receiver = this;
      calls += 1;
      return RELEASE_CONFIRMED;
    }),
  });
  const owner = (await task.ready).claim();
  owner.close();
  if (receiver) receiver.state = 'consumer-owned';
  owner.close();
  assert.equal(calls, 1);
});

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

test('cancel after resolving acquisition but before its await resumes cleans the late lease', async () => {
  const d = deferred();
  let calls = 0;
  const task = startHandoff({ acquire: () => d.promise });
  await Promise.resolve();
  assert.equal(task.inspect().phase, 'acquiring');
  d.resolve(createLease(() => { calls += 1; return RELEASE_CONFIRMED; }));
  assert.equal(task.cancel('between resolve and resume'), true);
  assert.equal(await task.ready, null);
  assert.equal(calls, 1);
  assert.equal(task.inspect().resource.state, 'released');
});

test('the first ready listener can revoke an offer before another listener claims it', async () => {
  let calls = 0;
  const task = startHandoff({
    acquire: () => createLease(() => { calls += 1; return RELEASE_CONFIRMED; }),
  });
  const first = task.ready.then(offer => {
    assert.ok(offer);
    assert.equal(task.cancel(), true);
  });
  const second = task.ready.then(offer => {
    assert.ok(offer, 'the Promise retains its fulfilled offer value');
    assert.equal(offer.claim(), null, 'settlement cannot guarantee current ownership');
  });
  await Promise.all([first, second]);
  assert.equal(calls, 1);
});

test('claim followed by a consumer exception cannot restore producer ownership', async () => {
  let owner;
  let calls = 0;
  const task = startHandoff({
    acquire: () => createLease(() => { calls += 1; return RELEASE_CONFIRMED; }),
  });
  const consumerError = new Error('consumer failed after taking ownership');
  await assert.rejects(task.ready.then(offer => {
    owner = offer.claim();
    throw consumerError;
  }), error => error === consumerError);
  assert.equal(task.cancel(), false);
  assert.equal(task.failDelivery(consumerError), false);
  assert.equal(owner.inspect().state, 'consumer-owned');
  assert.equal(calls, 0);
  owner.close();
  assert.equal(calls, 1);
});

test('a cleanup side effect followed by an exception remains unknown and is not retried', async () => {
  let calls = 0;
  let actualReleased = false;
  const failure = new Error('failed after releasing');
  const task = startHandoff({ acquire: () => createLease(() => {
    calls += 1;
    actualReleased = true;
    throw failure;
  }) });
  const owner = (await task.ready).claim();
  const result = owner.close();
  assert.equal(result.state, 'outcome-unknown');
  assert.equal(result.cleanupError, failure);
  assert.equal(actualReleased, true);
  assert.equal(owner.close().state, 'outcome-unknown');
  assert.equal(calls, 1);
});

test('producer cleanup cannot reenter claim or restart a completed stop request', async () => {
  let calls = 0;
  let offer;
  let observed;
  const task = startHandoff({ acquire: () => createLease(() => {
    calls += 1;
    observed = task.inspect();
    assert.equal(offer.claim(), null);
    assert.equal(task.cancel(), false);
    assert.equal(task.failDelivery(new Error('reentrant')), false);
    return RELEASE_CONFIRMED;
  }) });
  offer = await task.ready;
  assert.equal(task.cancel(), true);
  assert.equal(observed.phase, 'cancelled');
  assert.equal(observed.resource.state, 'cleaning');
  assert.equal(task.inspect().resource.state, 'released');
  assert.equal(calls, 1);
});

test('two acquisitions of one lease do not let the losing task close the winning owner', async () => {
  let calls = 0;
  const lease = createLease(() => { calls += 1; return RELEASE_CONFIRMED; });
  const first = startHandoff({ acquire: () => lease });
  const second = startHandoff({ acquire: () => lease });
  const [offer, rejected] = await Promise.all([first.ready, second.ready]);
  assert.ok(offer);
  assert.equal(rejected, null);
  assert.equal(second.inspect().phase, 'failed');
  assert.equal(second.inspect().resource, null);
  assert.equal(calls, 0);
  assert.equal(second.cancel(), false);
  const owner = offer.claim();
  owner.close();
  assert.equal(calls, 1);
});

test('a reentrant close snapshot stays cleaning even after the outer close confirms release', async () => {
  let owner;
  let during;
  let calls = 0;
  const task = startHandoff({ acquire: () => createLease(() => {
    calls += 1;
    during = owner.close();
    assert.equal(during.state, 'cleaning');
    return RELEASE_CONFIRMED;
  }) });
  owner = (await task.ready).claim();
  const completed = owner.close();
  assert.equal(during.state, 'cleaning');
  assert.equal(completed.state, 'released');
  assert.equal(owner.inspect().state, 'released');
  assert.equal(calls, 1);
});

test('unexpected thenable observation sees a locked unknown state before getter and executor reentry', async () => {
  let owner;
  let calls = 0;
  let getterCalls = 0;
  let thenCalls = 0;
  const diagnostic = new Error('unexpected asynchronous cleanup rejection');
  const task = startHandoff({ acquire: () => createLease(() => {
    calls += 1;
    return {
      get then() {
        getterCalls += 1;
        assert.equal(owner.inspect().state, 'outcome-unknown');
        assert.equal(owner.close().state, 'outcome-unknown');
        return (resolve, reject) => {
          thenCalls += 1;
          assert.equal(owner.close().state, 'outcome-unknown');
          reject(diagnostic);
        };
      },
    };
  }) });
  owner = (await task.ready).claim();
  assert.equal(owner.close().state, 'outcome-unknown');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(getterCalls, 1, 'then getter must not be read twice for detection and assimilation');
  assert.equal(thenCalls, 1);
  assert.equal(calls, 1);
  assert.equal(owner.inspect().state, 'outcome-unknown');
  assert.equal(owner.inspect().returnObservation.state, 'rejected');
  assert.equal(owner.inspect().returnObservation.error, diagnostic);
});

test('unexpected asynchronous confirmation cannot retroactively confirm release', async () => {
  let calls = 0;
  const task = startHandoff({ acquire: () => createLease(() => {
    calls += 1;
    return Promise.resolve(RELEASE_CONFIRMED);
  }) });
  const owner = (await task.ready).claim();
  const before = owner.close();
  assert.equal(before.state, 'outcome-unknown');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(owner.close().state, 'outcome-unknown');
  assert.equal(calls, 1);
});
