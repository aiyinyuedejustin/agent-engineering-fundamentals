import test from 'node:test';
import assert from 'node:assert/strict';
import { createCallbackGate } from './callback-gate.mjs';
function harness(options = {}) {
  const tasks = [], values = [], errors = [];
  const gate = createCallbackGate({
    deliver: value => values.push(value),
    onError: error => errors.push(error.message),
    schedule: task => tasks.push(task), ...options,
  });
  return { gate, tasks, values, errors,
    flush() { let n = 0; while (tasks.length) { assert.ok(++n < 100); tasks.shift()(); } },
  };
}
test('FIFO delivery is deferred and synthetic Buffers retain data', () => {
  const h = harness();
  assert.equal(h.gate.offer(Buffer.from([1, 2])), 'accepted');
  assert.equal(h.gate.offer(Buffer.from([3])), 'accepted');
  assert.deepEqual(h.values, []);
  h.flush(); assert.deepEqual(h.values.map(x => [...x]), [[1, 2], [3]]);
});
test('bounded waiting queue returns full without silently dropping accepted data', () => {
  const h = harness({ capacity: 1 });
  assert.equal(h.gate.offer('first'), 'accepted');
  assert.equal(h.gate.offer('second'), 'full');
  h.flush(); assert.deepEqual(h.values, ['first']);
});
test('close invalidates an already scheduled callback', () => {
  const h = harness(); h.gate.offer('late'); h.gate.close(); h.flush();
  assert.deepEqual(h.values, []); assert.equal(h.gate.offer('later'), 'closed');
});
test('close is idempotent', () => {
  const h = harness(); h.gate.close(); h.gate.close();
  assert.equal(h.gate.inspect().closed, true);
  assert.equal(h.gate.inspect().waiting, 0);
});
test('closing within a callback prevents subsequent queued delivery', () => {
  let gate; const seen = [];
  const h = harness({ deliver: value => { seen.push(value); gate.close(); } });
  gate = h.gate; gate.offer(1); gate.offer(2); h.flush();
  assert.deepEqual(seen, [1]);
});
test('delivery errors are reported and do not strand later messages', () => {
  const seen = []; const h = harness({ deliver: value => {
    if (value === 1) throw new Error('synthetic failure'); seen.push(value);
  } });
  h.gate.offer(1); h.gate.offer(2); h.flush();
  assert.deepEqual(h.errors, ['synthetic failure']); assert.deepEqual(seen, [2]);
});
test('reentrant offer queues a later delivery', () => {
  let gate; const seen = []; const h = harness({ deliver: value => {
    seen.push(value); if (value === 1) gate.offer(2);
  } });
  gate = h.gate; gate.offer(1); h.flush(); assert.deepEqual(seen, [1, 2]);
});
test('invalid capacity is rejected', () => {
  for (const capacity of [0, -1, 1.5, Infinity]) {
    assert.throws(() => createCallbackGate({ deliver() {}, capacity }), RangeError);
  }
});

test('first scheduler failure closes instead of stranding accepted items', () => {
  const reports = [];
  const h = harness({ schedule() { throw new Error('queue unavailable'); },
    onError: (error, context) => reports.push({ message: error.message, ...context }),
  });
  assert.equal(h.gate.offer('first'), 'scheduler-failed');
  assert.equal(h.gate.offer('second'), 'closed');
  assert.equal(h.gate.inspect().waiting, 0);
  assert.deepEqual(reports, [{ message: 'queue unavailable', source: 'scheduler', discarded: 1 }]);
});
test('a scheduler that enqueues then throws cannot deliver a stale ticket', () => {
  const tasks = [], seen = [];
  const gate = createCallbackGate({ deliver: x => seen.push(x), schedule(task) {
    tasks.push(task); throw new Error('failure after enqueue');
  } });
  assert.equal(gate.offer('stale'), 'scheduler-failed');
  tasks.shift()(); assert.deepEqual(seen, []);
  assert.equal(gate.inspect().failures.scheduler, 1);
});
test('rearm failure drops waiting items with an observable count', () => {
  const tasks = [], seen = []; let attempts = 0;
  const gate = createCallbackGate({ deliver: x => seen.push(x), schedule(task) {
    if (++attempts === 2) throw new Error('later failure'); tasks.push(task);
  } });
  gate.offer(1); gate.offer(2); gate.offer(3); tasks.shift()();
  assert.deepEqual(seen, [1]); assert.equal(gate.inspect().closed, true);
  assert.equal(gate.inspect().waiting, 0); assert.equal(gate.inspect().failures.discarded, 2);
});
test('reporter exceptions are isolated and counted without blocking later delivery', () => {
  const seen = [];
  const h = harness({ deliver(value) { if (value === 1) throw new Error('delivery'); seen.push(value); },
    onError() { throw new Error('reporter'); },
  });
  h.gate.offer(1); h.gate.offer(2); assert.doesNotThrow(() => h.flush());
  assert.deepEqual(seen, [2]);
  assert.deepEqual(h.gate.inspect().failures, { delivery: 1, scheduler: 0, reporter: 1, discarded: 0 });
});
