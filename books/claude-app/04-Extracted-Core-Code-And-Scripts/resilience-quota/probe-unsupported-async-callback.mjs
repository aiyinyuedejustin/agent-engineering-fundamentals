// 原创合成反例，只导入同目录教学模型。
// 不联网、不运行真实任务或定时器；自建Promise的拒绝提前注册处理。
import assert from 'node:assert/strict';
import { CursorConsumer } from './recovery-state.mjs';
const consumer = new CursorConsumer();
let rejectApplication;
let applied = false;
const application = new Promise((resolve, reject) => { rejectApplication = reject; });
const observedApplication = application.catch(error => error.message);
const disposition = consumer.deliver(107, 'synthetic-event', () => application);
const beforeSettlement = { disposition, cursor: consumer.cursor, applied };
rejectApplication(new Error('synthetic reducer failure'));
const failure = await observedApplication;
const replay = consumer.deliver(107, 'synthetic-event', () => { applied = true; });
const result = { status: 'reproduced unsupported callback usage', beforeSettlement, failure, replay, cursor: consumer.cursor, applied };
// 断言固定当前不支持用法的反例，不代表异步合同已经实现。
assert.deepEqual(beforeSettlement, { disposition: 'applied', cursor: 107, applied: false });
assert.equal(replay, 'duplicate');
assert.equal(applied, false);
console.log(JSON.stringify(result, null, 2));
