import test from 'node:test';
import assert from 'node:assert/strict';
import {PcmFrameAssembler} from './audio-state.mjs';

test('尾段只交付一次，finish 终止这条采样流',()=>{
  const p=new PcmFrameAssembler(1000,3);
  const [frame]=p.push([1,2,3,4]);
  assert.equal(frame.startSample,0);
  assert.deepEqual([...p.finish()],[4]);
  assert.equal(p.pendingSamples,0);
  assert.deepEqual([...p.finish()],[]);
  assert.throws(()=>p.push([5,6,7]),/finished/);
  assert.equal(p.pendingSamples,0);
});
test('空流结束后拒绝空写入',()=>{
  const p=new PcmFrameAssembler(1000,3);
  assert.deepEqual([...p.finish()],[]);
  assert.throws(()=>p.push([]),/finished/);
});
test('完整帧边界结束后也不能续写',()=>{
  const p=new PcmFrameAssembler(1000,3);
  assert.equal(p.push([1,2,3]).length,1);
  assert.deepEqual([...p.finish()],[]);
  assert.throws(()=>p.push([4]),/finished/);
});
test('终态写入在读取迭代器之前拒绝',()=>{
  const p=new PcmFrameAssembler(1000,3);p.finish();let reads=0;
  const value={get [Symbol.iterator](){reads++;throw new Error('must not read');}};
  assert.throws(()=>p.push(value),/finished/);assert.equal(reads,0);
});
test('输入迭代器结束流后，当前批次不能复活流',()=>{
  const p=new PcmFrameAssembler(1000,3);p.push([1]);let tail;
  function* samples(){yield 2;tail=p.finish();yield 3;}
  assert.throws(()=>p.push(samples()),/finished/);
  assert.deepEqual([...tail],[1]);assert.equal(p.pendingSamples,0);
  assert.deepEqual([...p.finish()],[]);
});
test('无效批次不隐式结束开放流',()=>{
  const p=new PcmFrameAssembler(1000,3);p.push([1]);
  assert.throws(()=>p.push([NaN]),TypeError);
  const [frame]=p.push([2,3]);assert.deepEqual([...frame.samples],[1,2,3]);
  assert.deepEqual([...p.finish()],[]);
});
test('新采样流需要新实例，时间原点独立',()=>{
  const first=new PcmFrameAssembler(1000,3);first.push([1]);first.finish();
  const second=new PcmFrameAssembler(1000,3);const [frame]=second.push([2,3,4]);
  assert.equal(frame.sequence,0);assert.equal(frame.startSample,0);assert.equal(frame.startMs,0);
});
