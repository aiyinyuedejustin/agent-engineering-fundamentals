import {RingLesson} from './ring-lesson.mjs';
import {earlyPublish, earlyRelease} from './unsafe-fixtures.mjs';
const r = new RingLesson();
function publish() { const t = r.reserve(); if (!t) return 0; r.copy(t); return r.publish(t); }
function consume(n) {
  const t = r.acquire(n); if (!t) return;
  r.copyOut(t); const {output, done} = r.release(t);
  console.log('消费', output.map(x => `${x.value}(g${x.generation},#${x.sequence})`), '自然完成', done);
}
r.enqueue(0, [1, 2, 3, 4, 5]); publish();
console.log('部分发布后', r.snapshot());
consume(2); r.enqueue(0, [6, 7]); publish();
consume(4); publish(); // 5在6之前；7仍保留，后面才发布。
console.log('封存自然边界', r.end(0)); r.nextTurn();
r.enqueue(1, [8, 9]); publish(); consume(4); // 一个读取批次跨g0/g1自然边界。
r.enqueue(1, [10, 11]); publish();
const {request} = r.requestFlush();
console.log('ack前新代输入', r.enqueue(2, [12]));
const ack = r.consumerFlush(request);
console.log('consumer丢弃，仍等待ack', ack, r.snapshot().phase);
r.acknowledge(ack); r.enqueue(2, [12]); publish(); consume(4);
console.log('余额', r.snapshot());
console.log('错误演练：提前publish', earlyPublish());
console.log('错误演练：提前release', earlyRelease());
