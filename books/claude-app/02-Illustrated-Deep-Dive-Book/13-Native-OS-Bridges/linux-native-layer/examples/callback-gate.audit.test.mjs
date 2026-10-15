/** Independent synthetic-only tests. Import only the original teaching model. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { createCallbackGate } from './callback-gate.mjs';
function harness(options = {}) {
  const tasks = [], seen = [], reports = [];
  const gate = createCallbackGate({
    capacity: 4,
    deliver: value => seen.push(value),
    onError: (error, context) => reports.push({ error, context }),
    schedule: task => tasks.push(task),
    ...options,
  });
  return { tasks, seen, reports, gate,
    one() { const task = tasks.shift(); assert.equal(typeof task, 'function'); task(); },
    drain() { let left=1000; while(tasks.length) { assert.ok(left--); this.one(); } },
  };
}
test('default scheduler is deferred and accepts undefined as an ordinary payload', async () => {
  const seen=[]; const gate=createCallbackGate({deliver:v=>seen.push(v)});
  assert.equal(gate.offer(undefined),'accepted'); assert.equal(seen.length,0);
  await new Promise(resolve=>setImmediate(resolve)); assert.deepEqual(seen,[undefined]);
});
test('FIFO and capacity survive alternating saturation and draining', () => {
  const h=harness({capacity:3}), accepted=[];
  for(let i=0;i<100;i++) {
    const result=h.gate.offer(i); if(result==='accepted') accepted.push(i);
    else assert.equal(result,'full');
    assert.ok(h.gate.inspect().waiting<=3);
    if(i%2===0 && h.tasks.length) h.one();
  }
  h.drain(); assert.deepEqual(h.seen,accepted);
});
test('capacity counts waiting items, not the currently executing callback', () => {
  let h; const seen=[],results=[];
  h=harness({capacity:1,deliver(v) { seen.push(v); if(v===1) results.push(h.gate.offer(2)); }});
  h.gate.offer(1); h.drain(); assert.deepEqual(seen,[1,2]); assert.deepEqual(results,['accepted']);
});
test('reentrant offer does not overtake an older pending item', () => {
  let h; const seen=[];
  h=harness({deliver(v) { seen.push(v); if(v===1) h.gate.offer(3); }});
  h.gate.offer(1); h.gate.offer(2); h.drain(); assert.deepEqual(seen,[1,2,3]);
});
test('close before the scheduled callback rejects late offers and stale work', () => {
  const h=harness(); h.gate.offer('old'); const task=h.tasks.shift(); h.gate.close();
  assert.equal(h.gate.offer('late'),'closed'); task();
  assert.deepEqual(h.seen,[]); assert.equal(h.gate.inspect().waiting,0);
});
test('closing during deliver allows current synchronous callback to finish only', () => {
  let h; const seen=[];
  h=harness({deliver(v) { seen.push(v); h.gate.close(); seen.push('returning'); }});
  h.gate.offer(1); h.gate.offer(2); h.drain();
  assert.deepEqual(seen,[1,'returning']); assert.equal(h.gate.inspect().closed,true);
});
test('enqueue during deliver then close invalidates the extra queued task', () => {
  let h; const seen=[];
  h=harness({deliver(v) { seen.push(v); h.gate.offer(2); h.gate.close(); }});
  h.gate.offer(1); h.drain(); assert.deepEqual(seen,[1]);
});
test('repeated close remains idempotent with empty and pending gates', () => {
  for(const hasItem of [false,true]) {
    const h=harness(); if(hasItem) h.gate.offer('item');
    h.gate.close(); const state=h.gate.inspect(); h.gate.close(); h.drain();
    assert.deepEqual(h.gate.inspect(),state); assert.deepEqual(h.seen,[]);
  }
});
test('a throwing deliver reports exactly once then proceeds to later items', () => {
  const seen=[]; const h=harness({deliver(v){if(v===1) throw Error('delivery');seen.push(v);}});
  h.gate.offer(1); h.gate.offer(2); h.drain();
  assert.deepEqual(seen,[2]); assert.equal(h.reports.length,1);
  assert.equal(h.gate.inspect().failures.delivery,1);
});
test('onError can reenter offer while retaining FIFO', () => {
  let h; const seen=[];
  h=harness({deliver(v){if(v===1) throw Error('delivery');seen.push(v);},onError(){h.gate.offer(3);}});
  h.gate.offer(1); h.gate.offer(2); h.drain(); assert.deepEqual(seen,[2,3]);
});
test('onError can close and throw without allowing a later delivery', () => {
  let h; const seen=[];
  h=harness({deliver(v){seen.push(v);throw Error('delivery');},onError(){h.gate.close();throw Error('reporter');}});
  h.gate.offer(1); h.gate.offer(2); assert.doesNotThrow(()=>h.drain());
  assert.deepEqual(seen,[1]); assert.equal(h.gate.inspect().failures.reporter,1);
});
test('throwing reporter is isolated while later items still run', () => {
  const seen=[]; const h=harness({deliver(v){if(v===1) throw Error('delivery');seen.push(v);},onError(){throw Error('reporter');}});
  h.gate.offer(1); h.gate.offer(2); assert.doesNotThrow(()=>h.drain());
  assert.deepEqual(seen,[2]); assert.equal(h.gate.inspect().failures.reporter,1);
});
test('scheduler throw before enqueue returns a failure and cannot strand an open queue', () => {
  const h=harness({schedule(){throw Error('scheduler');}});
  assert.equal(h.gate.offer('first'),'scheduler-failed');
  assert.equal(h.gate.offer('second'),'closed'); assert.equal(h.gate.inspect().waiting,0);
  assert.equal(h.reports[0].context.discarded,1);
});
test('scheduler enqueue then throw invalidates its late task', () => {
  const tasks=[],seen=[];const gate=createCallbackGate({deliver:v=>seen.push(v),schedule(task){tasks.push(task);throw Error('scheduler');}});
  assert.equal(gate.offer('first'),'scheduler-failed'); tasks.shift()();
  assert.deepEqual(seen,[]); assert.equal(gate.inspect().failures.discarded,1);
});
test('scheduler reentrant offer then throw counts both discarded items', () => {
  let gate;const tasks=[],results=[],seen=[];
  gate=createCallbackGate({deliver:v=>seen.push(v),schedule(task){results.push(gate.offer('nested'));tasks.push(task);throw Error('scheduler');}});
  assert.equal(gate.offer('outer'),'scheduler-failed'); assert.deepEqual(results,['accepted']);
  tasks.shift()(); assert.deepEqual(seen,[]); assert.equal(gate.inspect().failures.discarded,2);
});
test('scheduler rearm failure closes and accounts for the remaining queue', () => {
  let calls=0;const tasks=[],seen=[];
  const gate=createCallbackGate({deliver:v=>seen.push(v),schedule(task){if(++calls===2)throw Error('rearm');tasks.push(task);}});
  for(const v of [1,2,3])gate.offer(v);tasks.shift()();
  assert.deepEqual(seen,[1]);assert.equal(gate.inspect().closed,true);
  assert.equal(gate.inspect().failures.discarded,2);assert.equal(gate.inspect().waiting,0);
});
test('scheduler failure reporter cannot reopen the gate or escape by throwing', () => {
  let gate;const offered=[];
  gate=createCallbackGate({deliver(){},schedule(){throw Error('scheduler');},onError(){offered.push(gate.offer('nested'));throw Error('reporter');}});
  assert.equal(gate.offer('outer'),'scheduler-failed');assert.deepEqual(offered,['closed']);
  assert.equal(gate.inspect().failures.reporter,1);
});
test('inspect returns snapshots rather than mutable error counters', () => {
  const h=harness(); const state=h.gate.inspect();state.closed=true;state.failures.reporter=999;
  assert.equal(h.gate.inspect().closed,false);assert.equal(h.gate.inspect().failures.reporter,0);
});
test('a synthetic resource needs explicit caller disposal when offer is rejected', () => {
  // No fd, OS resource, native binding or real resource API is involved.
  let released=0;const token={dispose(){released++;}};const h=harness({capacity:1});
  h.gate.offer('occupier');assert.equal(h.gate.offer(token),'full');assert.equal(released,0);
  token.dispose();assert.equal(released,1);h.gate.close();h.drain();
});
test('close drops JS references but does not implement a deterministic disposer', () => {
  let released=0;const token={dispose(){released++;}};const h=harness();
  h.gate.offer(token);h.gate.close();h.drain();assert.equal(released,0);
  // This is a scope-boundary test, not a failed native-lifetime guarantee.
  token.dispose();assert.equal(released,1);
});
test('the gate does not copy mutable JS buffers or make them immutable', () => {
  const h=harness();const payload=Buffer.from([1]);h.gate.offer(payload);payload[0]=9;h.drain();
  assert.equal(h.seen[0][0],9);assert.equal(h.seen[0],payload);
});
test('invalid callbacks and capacity fail at construction', () => {
  for(const capacity of [0,-1,1.5,NaN,Infinity,Number.MAX_SAFE_INTEGER+1])
    assert.throws(()=>createCallbackGate({deliver(){},capacity}),RangeError);
  for(const options of [{},{deliver:null},{deliver(){},onError:null},{deliver(){},schedule:null}])
    assert.throws(()=>createCallbackGate(options),TypeError);
});
