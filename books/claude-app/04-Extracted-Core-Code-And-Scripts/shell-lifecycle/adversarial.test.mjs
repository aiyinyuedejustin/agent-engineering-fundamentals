import test from 'node:test';
import assert from 'node:assert/strict';
import {NavigationOwner,settleShutdown} from './lifecycle.mjs';

test('stress: deadlines beyond the platform timer range are rejected before starting cleanup',async()=>{
  let started=false;await assert.rejects(settleShutdown({one:()=>{started=true;}},{deadlineMs:2**31}),RangeError);assert.equal(started,false);
});
test('stress: all tasks are admitted before awaiting any task',async()=>{
  const started=[];let finish;
  const running=settleShutdown({first:()=>{started.push('first');return new Promise(r=>finish=r);},second:()=>{started.push('second');},third:()=>{started.push('third');throw Error('synthetic');}},{deadlineMs:100});
  await Promise.resolve();assert.deepEqual(started,['first','second','third']);finish();
  const report=await running;assert.equal(report.reason,'settled');assert.deepEqual(report.cleanup.map(x=>x.state),['fulfilled','fulfilled','rejected']);
});
test('stress: late completion during flush does not mutate deadline cleanup snapshot',async()=>{
  let finish,releaseFlush,enteredFlush;
  const flushing=new Promise(r=>enteredFlush=r);
  const running=settleShutdown({slow:()=>new Promise(r=>finish=r)},{deadlineMs:0,flush:()=>{enteredFlush();return new Promise(r=>releaseFlush=r);}});
  await flushing;finish();await Promise.resolve();await Promise.resolve();releaseFlush();
  const report=await running;assert.equal(report.reason,'deadline');assert.equal(report.cleanup[0].state,'pending');assert.equal(report.persistence,'fulfilled');
});
test('stress: cleanup timeout is not an implicit timeout or cancellation of persistence',async()=>{
  let release;let settled=false;
  const running=settleShutdown({}, {deadlineMs:0,flush:()=>new Promise(r=>release=r)}).then(x=>{settled=true;return x;});
  await new Promise(r=>setImmediate(r));assert.equal(settled,false);release();assert.equal((await running).persistence,'fulfilled');
});
test('stress: 100 navigation generations reject stale and replayed settlement',()=>{
  const owner=new NavigationOwner(),tickets=[];for(let i=0;i<100;i++)tickets.push(owner.begin(`synthetic:${i}`));
  for(const ticket of tickets.slice(0,-1))assert.equal(owner.settle(ticket,{ok:true}),false);
  const current=tickets.at(-1);assert.equal(owner.settle(current,{ok:false,error:'latest'}),true);assert.equal(owner.settle(current,{ok:true}),false);
  assert.equal(owner.snapshot().error,'latest');owner.dispose();assert.equal(owner.settle(current,{ok:true}),false);
});
