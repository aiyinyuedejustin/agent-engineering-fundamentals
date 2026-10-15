import test from 'node:test';
import assert from 'node:assert/strict';
import {PcmFrameAssembler} from './audio-state.mjs';
test('array-like getter cannot reopen a finished stream',()=>{
 const a=new PcmFrameAssembler(1000,3);a.push([.25]); let tail;
 const input={length:1,get 0(){tail=a.finish();return .5;}};
 assert.throws(()=>a.push(input),/finished/);
 assert.deepEqual([...tail],[.25]);assert.equal(a.pendingSamples,0);
 assert.throws(()=>a.push([]),/finished/);
});
test('iterator finish then throw keeps the terminal state',()=>{
 const a=new PcmFrameAssembler(1000,3);a.push([.25]);
 function* input(){a.finish();throw new Error('iterator error');}
 assert.throws(()=>a.push(input()),/iterator error/);
 assert.throws(()=>a.push([.5]),/finished/);
 assert.deepEqual([...a.finish()],[]);
});
test('tail data and repeated finish outputs are separately owned',()=>{
 const a=new PcmFrameAssembler(1000,3);a.push([.25]);const tail=a.finish();
 tail[0]=1;const one=a.finish(),two=a.finish();assert.notEqual(one,two);
 assert.equal(a.pendingSamples,0);assert.equal(one.length,0);
});
