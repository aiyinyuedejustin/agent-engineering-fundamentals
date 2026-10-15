import test from 'node:test';
import assert from 'node:assert/strict';
import {RingLesson} from './ring-lesson.mjs';
import {earlyPublish, earlyRelease} from './unsafe-fixtures.mjs';
const put = r => { const t = r.reserve(); if (!t) return 0; r.copy(t); return r.publish(t); };
const take = (r, n) => { const t = r.acquire(n); if (!t) return {output: [], done: []}; r.copyOut(t); return r.release(t); };
const values = result => result.output.map(x => x.value);
const balanced = r => assert.equal(r.snapshot().balanceOK, true);

test('容量5可用4：满、空、wrap，RD/WR不需要归零', () => {
  const r = new RingLesson();
  assert.equal(r.snapshot().usable, 4);
  r.enqueue(0, [1, 2, 3, 4]); assert.equal(put(r), 4);
  assert.equal(r.snapshot().free, 0); assert.equal(r.reserve(), null);
  assert.deepEqual(values(take(r, 2)), [1, 2]);
  r.enqueue(0, [5, 6]); put(r);
  assert.equal(r.snapshot().wr, 1);
  assert.deepEqual(values(take(r, 4)), [3, 4, 5, 6]);
  assert.equal(r.acquire(4), null); balanced(r);
});
test('partial保留尾部：网络/待接纳/accepted/consumed分账，e先于f,g', () => {
  const r = new RingLesson();
  r.enqueue(0, [1, 2, 3, 4, 5]); put(r);
  assert.equal(r.snapshot().accepted, 4); assert.equal(r.snapshot().pending, 1);
  assert.equal(r.snapshot().consumed, 0);
  assert.deepEqual(values(take(r, 2)), [1, 2]);
  r.enqueue(0, [6, 7]); assert.equal(put(r), 2);
  assert.equal(r.snapshot().pending, 1);
  assert.deepEqual(values(take(r, 4)), [3, 4, 5, 6]); put(r);
  assert.deepEqual(values(take(r, 4)), [7]);
  assert.equal(r.snapshot().accepted, 7); balanced(r);
});
test('copy不可见；publish/release先后合同及唯一未结票据', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2]);
  const w = r.reserve(); assert.throws(() => r.reserve());
  assert.throws(() => r.publish(w), /先copy/); r.copy(w);
  assert.equal(r.acquire(4), null); assert.equal(r.snapshot().accepted, 0);
  r.publish(w); assert.throws(() => r.publish(w));
  const t = r.acquire(2); assert.throws(() => r.acquire(1));
  assert.throws(() => r.release(t), /先copyOut/);
  assert.equal(r.snapshot().free, 2);
  const output = r.copyOut(t); assert.equal(Object.isFrozen(output), true);
  assert.equal(Object.isFrozen(output[0]), true);
  assert.equal(r.snapshot().consumed, 0); r.release(t);
  assert.equal(r.snapshot().free, 4); assert.throws(() => r.release(t)); balanced(r);
});
test('未release的读槽不能覆盖；复制期间producer只写安全空位', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2, 3, 4, 5]); put(r);
  const t = r.acquire(2); assert.equal(r.reserve(), null);
  assert.deepEqual(r.copyOut(t).map(x => x.value), [1, 2]);
  assert.equal(r.reserve(), null); r.release(t); put(r);
  assert.deepEqual(values(take(r, 4)), [3, 4, 5]); balanced(r);
});
test('取消未发布批次保留pending，旧票据失效且新批次重写', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2]);
  const w = r.reserve(); r.copy(w); r.cancel(w);
  assert.equal(r.snapshot().pending, 2); assert.throws(() => r.publish(w));
  put(r); assert.deepEqual(values(take(r, 4)), [1, 2]); balanced(r);
});
test('flush取消copied未published批次；等待ack不接新代或旧回调', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2, 3]); put(r);
  r.enqueue(0, [4, 5]); const w = r.reserve(); r.copy(w);
  const {request, abandonedPending} = r.requestFlush();
  assert.equal(abandonedPending, 2); assert.throws(() => r.publish(w));
  assert.equal(r.enqueue(0, [8]), false); assert.equal(r.enqueue(1, [9]), false);
  assert.throws(() => r.reserve()); assert.equal(r.acknowledge({generation: 1}), false);
  const ack = r.consumerFlush(request);
  assert.equal(ack.discarded, 3); assert.equal(r.snapshot().wr, 3);
  assert.equal(r.snapshot().rd, 3); assert.throws(() => r.reserve());
  assert.equal(r.snapshot().phase, 'waiting'); // 没有自动超时放行。
  assert.equal(r.acknowledge(ack), true);
  assert.equal(r.enqueue(0, [88]), false); r.enqueue(1, [9]); put(r);
  const result = take(r, 4); assert.deepEqual(values(result), [9]);
  assert.equal(result.output[0].generation, 1); assert.equal(result.output[0].sequence, 4);
  balanced(r);
});
test('旧ack与旧flush重复到达不会打开第二次flush的门', () => {
  const r = new RingLesson();
  const first = r.requestFlush().request; const old = r.consumerFlush(first); r.acknowledge(old);
  const second = r.requestFlush().request;
  assert.equal(r.acknowledge(old), false); assert.throws(() => r.consumerFlush(first));
  assert.throws(() => r.reserve());
  const current = r.consumerFlush(second);
  assert.equal(r.acknowledge(old), false); assert.equal(r.acknowledge(current), true);
  assert.equal(r.snapshot().generation, 2);
});
test('flush只在消费批次之间；已acquire必须copyOut/release结清', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2, 3]); put(r);
  const t = r.acquire(1); const {request} = r.requestFlush();
  assert.throws(() => r.consumerFlush(request), /消费步骤之间/);
  r.copyOut(t); r.release(t);
  assert.equal(r.consumerFlush(request).discarded, 2); balanced(r);
});
test('自然end必须清尾部，封口拒旧回调；一个quantum跨代边界才done', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2, 3, 4, 5]); put(r);
  assert.throws(() => r.end(0), /保留尾部/);
  take(r, 2); put(r); // 旧代还剩3,4,5。
  const end = r.end(0); assert.equal(end.boundary.sequence, 5); assert.equal(end.done, null);
  assert.equal(r.enqueue(0, [999]), false); assert.throws(() => r.end(0));
  assert.equal(r.nextTurn(), 1); assert.equal(r.enqueue(0, [999]), false);
  r.enqueue(1, [6]); put(r);
  const t = r.acquire(4); const out = r.copyOut(t);
  assert.deepEqual(out.map(x => x.generation), [0, 0, 0, 1]);
  assert.equal(r.snapshot().consumed, 2); // copyOut还没有完成消费合同。
  const result = r.release(t);
  assert.deepEqual(values(result), [3, 4, 5, 6]); assert.deepEqual(result.done, [end.boundary]);
  assert.deepEqual(r.end(1).done, {generation: 1, sequence: 6}); balanced(r);
});
test('自然边界前释放不done，刚好达到边界done且只发一次', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2, 3]); put(r); const end = r.end(0);
  assert.deepEqual(take(r, 2).done, []); assert.deepEqual(take(r, 1).done, [end.boundary]);
  assert.deepEqual(take(r, 1).done, []); balanced(r);
});
test('flush取消自然end，不把discard冒充自然done；accepted序号不归零', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2]); put(r); const end = r.end(0);
  const {request} = r.requestFlush(); const ack = r.consumerFlush(request);
  assert.deepEqual(ack.canceledEnds, [end.boundary]); r.acknowledge(ack);
  r.enqueue(1, [3]); put(r); const result = take(r, 1);
  assert.equal(result.output[0].sequence, 3); assert.deepEqual(result.done, []); balanced(r);
});
test('空turn立即done；非法生命周期与输入拒绝', () => {
  const r = new RingLesson(); assert.throws(() => r.nextTurn());
  assert.throws(() => r.acquire(0)); assert.throws(() => new RingLesson(1));
  assert.throws(() => r.enqueue(0, [NaN])); assert.throws(() => r.end(4));
  assert.deepEqual(r.end(0).done, {generation: 0, sequence: 0});
  assert.equal(r.enqueue(0, []), false); assert.throws(() => r.reserve()); r.nextTurn();
});
test('不安全fixture：提前publish读到未初始化值；提前release覆盖未读槽', () => {
  assert.deepEqual(earlyPublish(), {observed: undefined, eventualValue: 101});
  const bad = earlyRelease(); assert.equal(bad.observed, 106); assert.notEqual(bad.observed, bad.expected);
});
test('reserve后consumer释放更多空间，不扩张既有预留批次', () => {
  const r = new RingLesson(); r.enqueue(0, [1, 2, 3]); put(r);
  r.enqueue(0, [4, 5, 6]); const w = r.reserve(); // 只预留1个。
  assert.deepEqual(values(take(r, 3)), [1, 2, 3]);
  r.copy(w); assert.equal(r.publish(w), 1);
  assert.equal(r.snapshot().pending, 2); put(r);
  assert.deepEqual(values(take(r, 4)), [4, 5, 6]); balanced(r);
});
test('end拒绝未发布写票据；旧回调拒绝发生在读取payload之前', () => {
  const r = new RingLesson(); r.enqueue(0, [1]); const w = r.reserve(); r.copy(w);
  assert.throws(() => r.end(0), /未发布/); r.publish(w); r.end(0); r.nextTurn();
  const poison = [];
  Object.defineProperty(poison, Symbol.iterator, {get() { throw new Error('不应读取旧payload'); }});
  assert.equal(r.enqueue(0, poison), false);
});
test('固定调度枚举：不同生产批次与消费长度均保持FIFO及余额', () => {
  for (let batch = 1; batch <= 7; batch++) for (let quantum = 1; quantum <= 6; quantum++) {
    const r = new RingLesson(); const expected = []; const actual = [];
    for (let turn = 0; turn < 12; turn++) {
      const input = Array.from({length: batch}, (_, i) => turn * batch + i);
      expected.push(...input); r.enqueue(0, input); put(r); balanced(r);
      actual.push(...values(take(r, quantum))); balanced(r);
    }
    while (r.snapshot().pending || r.snapshot().readable) {
      put(r); actual.push(...values(take(r, quantum))); balanced(r);
    }
    assert.deepEqual(actual, expected);
    assert.equal(r.snapshot().accepted, expected.length);
  }
});
