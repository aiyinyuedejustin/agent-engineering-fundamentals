import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ContentEpoch, withDeadline} from './existing-models.mjs';
import {LeasePool, PreviewDeadlineCase, runWorkedTimeline} from './sandbox_timeout.mjs';

function ready(options) {
  const host = new PreviewDeadlineCase(options);
  assert.equal(host.acknowledge(host.publish('A')), true);
  return host;
}
const used = host => [host.snapshot().rpc.used, host.snapshot().work.used];
const balanced = host => {
  for (const pool of [host.snapshot().rpc, host.snapshot().work]) {
    assert.equal(pool.acquired - pool.released, pool.used);
    assert.ok(pool.used >= 0);
  }
};

test('existing withDeadline settles waiting but leaves underlying work scheduled', async t => {
  // Node built-in virtual timers: no sleep or real-duration race.
  t.mock.timers.enable({apis: ['setTimeout']});
  let actualCompletions = 0;
  const work = new Promise(resolve => setTimeout(() => {
    actualCompletions++; resolve('late underlying result');
  }, 9));
  const checked = assert.rejects(withDeadline(work, 6), /deadline/);
  t.mock.timers.tick(6);
  await checked;
  assert.equal(actualCompletions, 0);
  t.mock.timers.tick(3);
  assert.equal(await work, 'late underlying result');
  assert.equal(actualCompletions, 1);
});

test('existing ContentEpoch does not lend a later acknowledgement to an early receipt', () => {
  const gate = new ContentEpoch();
  const ticket = gate.replace('text/html', 'A'), early = gate.receipt();
  gate.acknowledge(ticket, true);
  assert.equal(gate.mayUseCapability(early), false);
  assert.equal(gate.mayUseCapability(gate.receipt()), true);
});

test('deadline releases RPC capacity while retaining the real-work lease', () => {
  const host = ready(); host.begin('r1', 5); host.advanceTo(5);
  assert.equal(host.snapshot('r1').reply, 'TIMEOUT');
  assert.equal(host.snapshot('r1').worker, 'running');
  assert.equal(host.snapshot('r1').cancel, 'requested');
  assert.deepEqual(used(host), [0, 1]);
  assert.deepEqual(host.begin('r2', 5), {accepted: false, reason: 'WORK_BUSY'});
  balanced(host);
});

test('receipt-only cancellation acknowledgement does not free execution capacity', () => {
  const host = ready(); host.begin('r', 5); host.advanceTo(5);
  assert.equal(host.cancelAcknowledged('r', 'received'), true);
  assert.equal(host.snapshot('r').worker, 'running');
  assert.deepEqual(used(host), [0, 1]);
});

test('terminal stopped acknowledgement is distinct, idempotent, and cannot revive RPC', () => {
  const host = ready(); host.begin('r', 5); host.advanceTo(5);
  assert.equal(host.cancelAcknowledged('r', 'stopped'), true);
  assert.equal(host.cancelAcknowledged('r', 'stopped'), false);
  assert.equal(host.finishWork('r', 'invalid late success'), false);
  assert.equal(host.snapshot('r').reply, 'TIMEOUT');
  assert.deepEqual(used(host), [0, 0]);
  assert.deepEqual(host.snapshot().work, {used: 0, acquired: 1, released: 1});
});

test('a noncooperative worker can finish after timeout but cannot deliver a result', () => {
  const host = ready(); host.begin('r', 5); host.advanceTo(5);
  assert.equal(host.finishWork('r', 'late synthetic data'), true);
  assert.equal(host.deliver('r').accepted, false);
  assert.equal(host.deliver('r').reasons.includes('DEADLINE'), true);
  assert.deepEqual(host.delivered, []);
  assert.deepEqual(used(host), [0, 0]);
  assert.equal(host.cancelAcknowledged('r', 'stopped'), false);
  balanced(host);
});

test('content replacement revokes pending and queued delivery without faking work termination', () => {
  const host = ready(); host.begin('r', 20);
  const newer = host.publish('B'); host.acknowledge(newer);
  assert.equal(host.snapshot('r').reply, 'STALE_CONTENT');
  assert.deepEqual(used(host), [0, 1]);
  host.finishWork('r', 'A value');
  assert.ok(host.deliver('r').reasons.includes('STALE_CONTENT'));
  assert.deepEqual(host.delivered, []);
});

test('successful local completion followed by replacement is rejected at actual delivery', () => {
  const host = ready(); host.begin('r', 20); host.finishWork('r', 'A value');
  assert.deepEqual(used(host), [1, 0]);
  host.acknowledge(host.publish('B'));
  assert.ok(host.deliver('r').reasons.includes('STALE_CONTENT'));
  assert.deepEqual(used(host), [0, 0]);
});

test('old channel cannot reuse a matching numeric epoch on a new channel', () => {
  const host = ready(); host.begin('r', 20); host.finishWork('r', 'old document value');
  const oldEpoch = host.snapshot().content.epoch;
  host.closeChannel(); host.openChannel(); host.acknowledge(host.publish('A'));
  assert.equal(host.snapshot().content.epoch, oldEpoch);
  const result = host.deliver('r');
  assert.equal(result.accepted, false);
  assert.ok(result.reasons.includes('OLD_CHANNEL'));
  assert.equal(result.reasons.includes('STALE_CONTENT'), false);
  assert.deepEqual(host.delivered, []);
});

test('old content acknowledgement is rejected across channels even with equal epoch and body', () => {
  const host = new PreviewDeadlineCase(), old = host.publish('A');
  host.closeChannel(); host.openChannel(); const current = host.publish('A');
  assert.equal(old.content.epoch, current.content.epoch);
  assert.equal(host.acknowledge(old), false);
  assert.equal(host.begin('r', 3).reason, 'CONTENT_UNACKNOWLEDGED');
  assert.equal(host.acknowledge(current), true);
});

test('same acknowledged content repost reuses the imported model epoch and remains valid', () => {
  const host = ready(); host.begin('r', 20);
  const epoch = host.snapshot().content.epoch;
  host.publish('A');
  assert.equal(host.snapshot().content.epoch, epoch);
  assert.equal(host.snapshot('r').reply, 'pending');
  host.finishWork('r', 'ok'); assert.equal(host.deliver('r').accepted, true);
});

test('same unacknowledged repost creates a new epoch and rejects old ACK', () => {
  const host = new PreviewDeadlineCase();
  const first = host.publish('A'), second = host.publish('A');
  assert.equal(second.content.epoch, first.content.epoch + 1);
  assert.equal(host.acknowledge(first), false);
  assert.equal(host.acknowledge(second), true);
});

test('before deadline succeeds; at exact deadline loses regardless of completion already queued', () => {
  const early = ready(); early.begin('r', 5); early.advanceTo(4);
  early.finishWork('r', 'ok'); assert.equal(early.deliver('r').accepted, true);
  const exact = ready(); exact.begin('r', 5); exact.finishWork('r', 'queued'); exact.advanceTo(5);
  assert.equal(exact.deliver('r').accepted, false);
  assert.equal(exact.snapshot('r').reply, 'TIMEOUT');
});

test('duplicate completion, delivery, cancellation and close never release a lease twice', () => {
  const host = ready(); host.begin('r', 5); host.finishWork('r', 'ok'); host.deliver('r');
  assert.equal(host.finishWork('r', 'again'), false);
  assert.equal(host.deliver('r').accepted, false);
  assert.equal(host.cancel('r'), false);
  host.closeChannel(); assert.equal(host.closeChannel(), false); host.advanceTo(50);
  assert.deepEqual(host.snapshot().rpc, {used: 0, acquired: 1, released: 1});
  assert.deepEqual(host.snapshot().work, {used: 0, acquired: 1, released: 1});
  assert.equal(host.delivered.length, 1);
});

test('repeated user cancellation signals once but keeps work until terminal acknowledgement', () => {
  const host = ready(); host.begin('r', 5);
  assert.equal(host.cancel('r'), true); assert.equal(host.cancel('r'), false);
  assert.deepEqual(used(host), [0, 1]);
  assert.equal(host.journal.filter(event => event.event === 'cancel-requested').length, 1);
  host.cancelAcknowledged('r', 'stopped'); balanced(host);
});

test('admission limits are atomic and separate for response and work slots', () => {
  const host = ready({rpcCapacity: 1, workerCapacity: 2}); host.begin('a', 5);
  assert.equal(host.begin('b', 5).reason, 'RPC_BUSY');
  assert.deepEqual(used(host), [1, 1]);
  assert.equal(host.snapshot().work.acquired, 1);
  host.advanceTo(5); assert.equal(host.begin('b', 5).accepted, true);
  assert.deepEqual(used(host), [1, 2]);
  balanced(host);
});

test('invalid deadlines, clock regressions and missing acknowledgement consume no resource', () => {
  const host = new PreviewDeadlineCase();
  assert.equal(host.begin('r', 5).reason, 'CONTENT_UNACKNOWLEDGED');
  for (const deadline of [0, -1, Infinity, 1.5, NaN]) assert.throws(() => host.begin('r', deadline));
  host.advanceTo(5); assert.throws(() => host.advanceTo(4));
  assert.throws(() => host.begin('r', Number.MAX_SAFE_INTEGER));
  assert.deepEqual(used(host), [0, 0]);
});

test('unknown or unsolicited cancellation acknowledgement cannot free an active worker', () => {
  const host = ready(); host.begin('r', 5);
  assert.throws(() => host.cancelAcknowledged('r', 'anything'));
  assert.equal(host.cancelAcknowledged('r', 'stopped'), false);
  assert.deepEqual(used(host), [1, 1]);
});

test('malformed result is a bounded error while each resource still releases exactly once', () => {
  const host = ready(); host.begin('r', 5); host.finishWork('r', {private: 'not allowed'});
  assert.equal(host.deliver('r').accepted, true);
  assert.deepEqual(host.delivered, [{id: 'r', ok: false, error: 'BAD_RESULT'}]);
  assert.deepEqual(used(host), [0, 0]);
});

test('leases are idempotent and retain accounting equality', () => {
  const pool = new LeasePool(1), lease = pool.acquire();
  assert.equal(pool.acquire(), null);
  assert.equal(lease.release(), true); assert.equal(lease.release(), false);
  assert.deepEqual(pool.snapshot(), {used: 0, acquired: 1, released: 1});
});

test('the worked trace is deterministic and all three admitted operations balance', () => {
  const run = runWorkedTimeline();
  assert.deepEqual(run, runWorkedTimeline());
  assert.deepEqual(run, JSON.parse(readFileSync(new URL('./expected-output.json', import.meta.url), 'utf8')));
  assert.equal(run.rows.length, 16);
  assert.deepEqual(run.final.rpc, {used: 0, acquired: 3, released: 3});
  assert.deepEqual(run.final.work, {used: 0, acquired: 3, released: 3});
  assert.deepEqual(run.delivered, []);
});

test('completion before stopped acknowledgement after user cancellation releases once', () => {
  const host = ready(); host.begin('r', 5); host.cancel('r');
  assert.equal(host.finishWork('r', 'completed during cancellation'), true);
  assert.equal(host.cancelAcknowledged('r', 'stopped'), false);
  assert.equal(host.finishWork('r', 'duplicate'), false);
  assert.equal(host.snapshot('r').reply, 'CANCELLED');
  assert.equal(host.deliver('r').accepted, false);
  assert.deepEqual(host.snapshot().work, {used: 0, acquired: 1, released: 1});
});

test('time passage alone cannot release a worker with no terminal evidence', () => {
  const host = ready(); host.begin('r', 5); host.advanceTo(5);
  host.cancelAcknowledged('r', 'received'); host.advanceTo(1_000_000);
  assert.equal(host.snapshot('r').worker, 'running');
  assert.deepEqual(used(host), [0, 1]);
  assert.equal(host.begin('another', 10).reason, 'WORK_BUSY');
});

test('all 120 terminal-event orderings preserve local lease ownership and reject late delivery', () => {
  function permutations(items) {
    if (!items.length) return [[]];
    return items.flatMap((item, index) => permutations(items.filter((_, at) => at !== index))
      .map(rest => [item, ...rest]));
  }
  let count = 0;
  for (const order of permutations(['deadline', 'cancel', 'finish', 'stopAck', 'finishAgain'])) {
    const host = ready(); host.begin('r', 5);
    const events = {
      deadline: () => host.advanceTo(5), cancel: () => host.cancel('r'),
      finish: () => host.finishWork('r', 'one'),
      finishAgain: () => host.finishWork('r', 'two'),
      stopAck: () => host.cancelAcknowledged('r', 'stopped')
    };
    for (const event of order) { events[event](); balanced(host); }
    assert.deepEqual(host.snapshot().rpc, {used: 0, acquired: 1, released: 1}, order.join(','));
    assert.deepEqual(host.snapshot().work, {used: 0, acquired: 1, released: 1}, order.join(','));
    assert.equal(host.deliver('r').accepted, false);
    count++;
  }
  assert.equal(count, 120);
});
