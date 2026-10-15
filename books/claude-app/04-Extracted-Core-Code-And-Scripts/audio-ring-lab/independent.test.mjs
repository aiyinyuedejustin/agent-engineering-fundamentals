import test from 'node:test';
import assert from 'node:assert/strict';
import {RingLesson} from './ring-lesson.mjs';
const put=r=>{const t=r.reserve();if(t){r.copy(t);r.publish(t);}return t};
const take=(r,n)=>{const t=r.acquire(n);if(!t)return null;r.copyOut(t);return r.release(t)};
test('invalid numeric domains and input snapshot',()=>{
 for(const n of [0,1,-1,2.2,NaN,Infinity,-Infinity,Number.MAX_SAFE_INTEGER+1,'5',null])assert.throws(()=>new RingLesson(n));
 const r=new RingLesson(2);for(const n of [0,-1,1.5,NaN,Infinity,'1',null])assert.throws(()=>r.acquire(n));
 for(const a of [[undefined],[NaN],[Infinity],['1'],new Array(1),null,new Float32Array(1)])assert.throws(()=>r.enqueue(0,a));
 const input=[-0,Number.MAX_VALUE];r.enqueue(0,input);input[0]=42;put(r);assert.ok(Object.is(take(r,1).output[0].value,-0));put(r);assert.equal(take(r,1).output[0].value,Number.MAX_VALUE);
});
test('reentrant lifecycle invalidates input; nested enqueue linearizes at append',()=>{
 const r=new RingLesson(); const a=[1];Object.defineProperty(a,0,{get(){const q=r.requestFlush().request;r.acknowledge(r.consumerFlush(q));return 1}});
 assert.equal(r.enqueue(0,a),false);assert.equal(r.snapshot().pending,0);
 const b=[2];Object.defineProperty(b,0,{get(){r.enqueue(1,[1]);return 2}});assert.equal(r.enqueue(1,b),true);put(r);assert.deepEqual(take(r,4).output.map(x=>x.value),[1,2]);
 const c=[3];Object.defineProperty(c,0,{get(){r.end(1);r.nextTurn();return 3}});assert.equal(r.enqueue(1,c),false);
});
test('multiple empty natural generations and exact boundary reporting',()=>{
 const r=new RingLesson();r.enqueue(0,[1]);put(r);const ends=[r.end(0).boundary];r.nextTurn();ends.push(r.end(1).boundary);r.nextTurn();r.enqueue(2,[2]);put(r);ends.push(r.end(2).boundary);
 const t=r.acquire(2);const out=r.copyOut(t);assert.deepEqual(out.map(x=>x.generation),[0,2]);assert.deepEqual(r.release(t).done,ends);assert.equal(r.acquire(2),null);
});
test('current ack cannot replay and foreign instance tickets cannot mutate',()=>{
 const a=new RingLesson(),b=new RingLesson();a.enqueue(0,[1]);b.enqueue(0,[2]);const w=a.reserve();for(const f of ['copy','publish','cancel'])assert.throws(()=>b[f](w));a.copy(w);assert.throws(()=>a.copy(w));a.publish(w);
 const t=a.acquire(1);assert.throws(()=>b.copyOut(t));a.copyOut(t);assert.throws(()=>a.copyOut(t));a.release(t);
 const q=a.requestFlush().request;const ack=a.consumerFlush(q);assert.throws(()=>a.consumerFlush(q));assert.equal(a.acknowledge(ack),true);assert.equal(a.acknowledge(ack),false);
});
test('seeded step-level reference ledger across publish/release/flush/end',()=>{
 for(const capacity of [2,3,5,8])for(let seed=1;seed<=20;seed++){
  let rng=seed;const random=n=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng%n};
  const r=new RingLesson(capacity);let pending=[],queue=[],ends=[],w=null,rd=null,req=null,ack=null,g=0,phase='open',accepted=0,consumed=0,discarded=0,value=0;
  for(let step=0;step<2000;step++){
   const op=random(13);
   if(op===0&&phase==='open'){const a=Array.from({length:random(7)},()=>++value);assert.equal(r.enqueue(g,a),true);pending.push(...a);}
   if(op===1&&phase==='open'&&!w){const token=r.reserve();const n=Math.min(pending.length,capacity-1-queue.length);assert.equal(!!token,n>0);if(token)w={token,n,copied:false};}
   if(op===2&&w&&!w.copied){r.copy(w.token);w.copied=true;}
   if(op===3&&w&&w.copied){assert.equal(r.publish(w.token),w.n);queue.push(...pending.splice(0,w.n).map(value=>({value,generation:g,sequence:++accepted})));w=null;}
   if(op===4&&w){r.cancel(w.token);w=null;}
   if(op===5&&!rd){const n=1+random(8),token=r.acquire(n);assert.equal(!!token,queue.length>0);if(token)rd={token,n:Math.min(n,queue.length),copied:false};}
   if(op===6&&rd&&!rd.copied){assert.deepEqual(r.copyOut(rd.token),queue.slice(0,rd.n));rd.copied=true;}
   if(op===7&&rd&&rd.copied){const output=queue.splice(0,rd.n),last=output.at(-1).sequence,done=ends.filter(e=>e.sequence<=last);ends=ends.filter(e=>e.sequence>last);consumed+=rd.n;assert.deepEqual(r.release(rd.token),{output,done});rd=null;}
   if(op===8&&phase!=='waiting'){const result=r.requestFlush();assert.equal(result.abandonedPending,pending.length);req=result.request;pending=[];w=null;phase='waiting';}
   if(op===9&&phase==='waiting'&&!rd&&!ack){ack=r.consumerFlush(req);assert.equal(ack.discarded,queue.length);assert.deepEqual(ack.canceledEnds,ends);discarded+=queue.length;queue=[];ends=[];}
   if(op===10&&ack){assert.equal(r.acknowledge(ack),true);g++;phase='open';ack=null;req=null;}
   if(op===11&&phase==='open'&&!pending.length&&!w){const boundary={generation:g,sequence:accepted};assert.deepEqual(r.end(g),{boundary,done:queue.length?null:boundary});if(queue.length)ends.push(boundary);phase='ended';}
   if(op===12&&phase==='ended'){assert.equal(r.nextTurn(),++g);phase='open';}
   const s=r.snapshot();assert.equal(s.balanceOK,true);assert.deepEqual([s.pending,s.readable,s.free,s.generation,s.phase,s.accepted,s.consumed,s.discarded],[pending.length,queue.length,capacity-1-queue.length,g,phase,accepted,consumed,discarded]);
  }
 }
});
