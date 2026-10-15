import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {FakeClock, SnapshotPresenter, StableBlocks, WeightedLRU, LatestWorkerLane, runSlices} from '../model.mjs';

// These tests exercise the original teaching model only. No worker/process is launched.
test('stress: cancellation adapter throwing must not suppress latest plain fallback', () => {
  const sent=[], fallback=[];
  const lane=new LatestWorkerLane({send:j=>sent.push(j),publish:()=>{},fallback:(...x)=>fallback.push(x),cancel:()=>{throw Error('adapter failed');}});
  lane.submit('old');lane.submit('latest');
  assert.doesNotThrow(()=>lane.fail(sent[0], 'timeout'));
  assert.deepEqual(fallback,[['latest','timeout']]);
  assert.equal(lane.reply(sent[0],'late'),false);
});
test('stress: cancellation reentry cannot publish obsolete failure source after newer request', () => {
  const sent=[], fallback=[]; let lane;
  lane=new LatestWorkerLane({send:j=>sent.push(j),publish:()=>{},fallback:(...x)=>fallback.push(x),cancel:()=>lane.submit('newer during cancellation')});
  lane.submit('old');lane.submit('pending');lane.fail(sent[0]);
  assert.deepEqual(fallback,[]);
  assert.equal(sent.at(-1).text,'newer during cancellation');
});
test('stress: disposal from cancellation suppresses fallback publication', () => {
  const sent=[], fallback=[];let lane;
  lane=new LatestWorkerLane({send:j=>sent.push(j),publish:()=>{},fallback:(...x)=>fallback.push(x),cancel:()=>lane.dispose()});
  lane.submit('old');lane.fail(sent[0]);
  assert.deepEqual(fallback,[]);
});
test('stress: oversize cancellation cannot overwrite a newer reentrant final source', () => {
  const fallback=[];let lane;
  lane=new LatestWorkerLane({maxChars:3,send:()=>{},publish:()=>{},fallback:(...x)=>fallback.push(x),cancel:()=>lane.submit('new')});
  lane.submit('old');assert.equal(lane.submit('oversize'),false);
  assert.deepEqual(fallback,[]);assert.equal(lane.busy.text,'new');
});
test('stress: only one active task and one latest snapshot survive 1000 submissions', () => {
  const sent=[],published=[];
  const lane=new LatestWorkerLane({send:j=>sent.push(j),publish:(x,j)=>published.push([x,j.text]),fallback:()=>{}});
  for(let i=0;i<1000;i++)lane.submit(`source-${i}`);
  assert.equal(sent.length,1);assert.equal(lane.latest.text,'source-999');
  lane.reply(sent[0],'obsolete');assert.equal(sent.length,2);assert.deepEqual(published,[]);
  lane.reply(sent[1],'rendered');assert.deepEqual(published,[['rendered','source-999']]);
  assert.equal(lane.reply(sent[1],'replay'),false);
});
test('stress: cancellation is a request and does not make a late task result current', () => {
  const sent=[],published=[],cancelled=[];
  const lane=new LatestWorkerLane({send:j=>sent.push(j),publish:x=>published.push(x),fallback:()=>{},cancel:j=>cancelled.push(j)});
  lane.submit('old');lane.reset();lane.submit('new');
  assert.equal(cancelled.length,1);assert.equal(lane.reply(sent[0],'old result'),false);
  lane.reply(sent[1],'new result');assert.deepEqual(published,['new result']);
});
test('stress: finite huge cache weights do not overflow accounting or loop forever', () => {
  const source=readFileSync(new URL('../model.mjs',import.meta.url),'utf8');
  const helpers=source.slice(0,source.indexOf('export class FakeClock'));
  const code=helpers+source.slice(source.indexOf('export class WeightedLRU'),source.indexOf('/** One in-flight')).replace('export class','class');
  // A VM timeout bounds the original infinite-loop reproduction without real OS/process actions.
  assert.doesNotThrow(()=>vm.runInNewContext(`${code}; const c=new WeightedLRU({weight:Number.MAX_VALUE}); c.put('a',1,Number.MAX_VALUE); c.put('b',2,Number.MAX_VALUE); if(c.used!==Number.MAX_VALUE || c.get('b')!==2 || c.items.size!==1) throw Error('accounting');`,{}, {timeout:200}));
});
test('stress: fractional weight eviction leaves exact empty-cache accounting', () => {
  const c=new WeightedLRU({weight:1});c.put('a',1,.1);c.put('b',2,.2);c.delete('a');c.delete('b');
  assert.equal(c.used,0);assert.equal(c.items.size,0);
});
test('stress: zero-weight values obey entry admission and replacement preserves newest value', () => {
  const c=new WeightedLRU({entries:1,weight:0});assert.equal(c.put('a',1,0),true);assert.equal(c.put('b',2,0),true);
  assert.equal(c.get('a'),undefined);assert.equal(c.get('b'),2);assert.equal(c.used,0);
});
test('stress: terminal source is authoritative after hidden non-prefix rewrite', () => {
  const clock=new FakeClock(),seen=[]; const blocks=new StableBlocks({finalParser:text=>({source:text})});
  const p=new SnapshotPresenter({clock,commit:x=>seen.push(blocks.update(x.text,{terminal:x.terminal}))});
  p.accept('old\n\ntail');p.setHidden(true);p.accept('obsolete\n\npart');p.accept('final🙂\n\nreference', {terminal:true});clock.advance(1000);
  assert.equal(seen.at(-1).final.source,'final🙂\n\nreference');
  assert.equal(seen.at(-1).blocks.map(b=>b.text).join('')+seen.at(-1).tail,'final🙂\n\nreference');
  assert.equal(clock.tasks.size,0);
});
test('stress: 200 deterministic append/edit sequences preserve exact source and final parse', () => {
  let seed=739;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
  const atoms=['a','🙂','\r\n','\n\n','```js\n','~~~\n','α','\n'];
  for(let run=0;run<200;run++){
    const b=new StableBlocks();let source='';
    for(let step=0;step<30;step++){
      source=step%7===0?source.slice(0,rand()%(source.length+1)):source;source+=atoms[rand()%atoms.length];
      const value=b.update(source);assert.equal(value.blocks.map(x=>x.text).join('')+value.tail,source);
    }
    assert.equal(b.update(source,{terminal:true}).final.source,source);
  }
});
test('stress: abort during an unresolved visit is observed only when that visit settles', async () => {
  const controller=new AbortController();let finish;const seen=[];
  const running=runSlices([1,2],{visit:x=>{seen.push(x);return new Promise(r=>finish=r);},now:()=>0,yieldTask:async()=>{},signal:controller.signal});
  controller.abort();assert.deepEqual(seen,[1]);finish();await assert.rejects(running,{name:'AbortError'});assert.deepEqual(seen,[1]);
});
test('stress: abort during yield prevents admission of the next unit', async () => {
  const controller=new AbortController(),seen=[];let time=0;
  await assert.rejects(runSlices([1,2],{visit:x=>{seen.push(x);time+=5;},now:()=>time,yieldTask:async()=>controller.abort(),signal:controller.signal}),{name:'AbortError'});
  assert.deepEqual(seen,[1]);
});
