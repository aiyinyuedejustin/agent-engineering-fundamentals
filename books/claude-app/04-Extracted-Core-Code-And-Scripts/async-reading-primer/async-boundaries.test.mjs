import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { deferred, Owner, commitAfter, waitUntil, effectAfter, TeachingQueue } from './async-boundaries.mjs';

test('await 即使等待已完成 Promise 也让调用者先改变状态', async () => {
  const owner = new Owner();
  const a = owner.begin('A');
  const job = commitAfter(owner, a, Promise.resolve('result:A'));
  owner.begin('B');
  assert.equal(await job, 'stale');
  assert.deepEqual(owner.snapshot(), { current: 'B', value: null });
});

test('反例能复现旧结果覆盖当前内容', async () => {
  const owner = new Owner(), gate = deferred();
  const a = owner.begin('A');
  const job = commitAfter(owner, a, gate.promise, { guarded: false });
  owner.begin('B'); gate.resolve('result:A');
  assert.equal(await job, 'committed');
  assert.deepEqual(owner.snapshot(), { current: 'B', value: 'result:A' });
});

test('当前归属未变时允许提交', async () => {
  const owner = new Owner(), a = owner.begin('A');
  assert.equal(await commitAfter(owner, a, Promise.resolve('result:A')), 'committed');
  assert.equal(owner.value, 'result:A');
});

test('同一标签重新开始也撤销旧票据', async () => {
  const owner = new Owner(), gate = deferred(), a = owner.begin('A');
  const job = commitAfter(owner, a, gate.promise);
  const newerA = owner.begin('A'); gate.resolve('old');
  assert.notEqual(a, newerA);
  assert.equal(await job, 'stale');
});

test('复制票据字段不会获得当前对象身份', () => {
  const owner = new Owner(), a = owner.begin('A');
  assert.equal(owner.owns({ ...a }), false);
  assert.equal(owner.owns(a), true);
});

test('销毁后迟到结果也不能提交', async () => {
  const owner = new Owner(), gate = deferred(), a = owner.begin('A');
  const job = commitAfter(owner, a, gate.promise);
  owner.dispose(); gate.resolve('old');
  assert.equal(await job, 'stale');
  assert.deepEqual(owner.snapshot(), { current: null, value: null });
});

test('等待的任务拒绝时传播异常，不伪装成 stale', async () => {
  const owner = new Owner(), a = owner.begin('A');
  await assert.rejects(commitAfter(owner, a, Promise.reject(new Error('READ_FAILED'))), /READ_FAILED/);
});

test('deadline 先到只结算等待，之后任务仍写入', async () => {
  const gate = deferred(), deadline = deferred(), effects = [];
  const work = effectAfter(gate.promise, effects);
  const waiting = waitUntil(work, deadline.promise);
  deadline.resolve();
  const report = await waiting;
  assert.deepEqual(report, { kind: 'deadline' });
  assert.equal(effects.length, 0);
  gate.resolve(); assert.equal(await work, 'written');
  assert.equal(effects.length, 1);
  assert.deepEqual(report, { kind: 'deadline' });
  assert.ok(Object.isFrozen(report));
});

test('任务先完成，随后到期不会改写已交付记录', async () => {
  const deadline = deferred();
  const report = await waitUntil(Promise.resolve(42), deadline.promise);
  deadline.resolve();
  assert.deepEqual(report, { kind: 'fulfilled', value: 42 });
});

test('任务先拒绝时，结算记录保留错误', async () => {
  const deadline = deferred(), error = new Error('FAILED');
  assert.deepEqual(await waitUntil(Promise.reject(error), deadline.promise), { kind: 'rejected', error });
});

test('deadline 后的迟到拒绝仍有处理器，不生成未处理拒绝', async () => {
  const gate = deferred(), deadline = deferred();
  const waiting = waitUntil(gate.promise, deadline.promise);
  deadline.resolve(); assert.equal((await waiting).kind, 'deadline');
  gate.reject(new Error('LATE_FAILURE'));
  // 过一个完整事件循环轮次，让 node:test 有机会发现 unhandledRejection。
  await new Promise(resolve => setImmediate(resolve));
});

test('发出 abort，但任务忽略信号，副作用仍发生', async () => {
  const gate = deferred(), effects = [], controller = new AbortController();
  const work = effectAfter(gate.promise, effects, { signal: controller.signal });
  controller.abort(); gate.resolve();
  assert.equal(await work, 'written');
  assert.equal(effects.length, 1);
});

test('任务在提交前合作检查信号，才可跳过写入', async () => {
  const gate = deferred(), effects = [], controller = new AbortController();
  const work = effectAfter(gate.promise, effects, { signal: controller.signal, cooperative: true });
  controller.abort(); gate.resolve();
  assert.equal(await work, 'aborted');
  assert.equal(effects.length, 0);
});

test('await enqueue 只拿到入队收据，任务尚未启动', async () => {
  const queue = new TeachingQueue(); let started = false;
  const receipt = await queue.enqueue(() => { started = true; });
  assert.equal(receipt.accepted, true);
  assert.equal(queue.state(receipt.id), 'queued');
  assert.equal(started, false);
  await queue.runNext(); await receipt.completion;
});

test('运行中与成功结算是不同状态', async () => {
  const queue = new TeachingQueue(), gate = deferred();
  const receipt = await queue.enqueue(() => gate.promise);
  const worker = queue.runNext();
  assert.equal(queue.state(receipt.id), 'running');
  gate.resolve('saved');
  assert.deepEqual(await receipt.completion, { state: 'fulfilled', value: 'saved' });
  assert.deepEqual(await worker, { state: 'fulfilled', value: 'saved' });
});

test('入队成功的操作也会失败，失败不阻塞下一项', async () => {
  const queue = new TeachingQueue(), error = new Error('SAVE_FAILED');
  const failed = await queue.enqueue(() => { throw error; });
  const next = await queue.enqueue(() => 'next');
  assert.equal(failed.accepted, true);
  await queue.runNext();
  assert.deepEqual(await failed.completion, { state: 'rejected', error });
  assert.equal(queue.state(failed.id), 'rejected');
  await queue.runNext();
  assert.equal((await next.completion).value, 'next');
});

test('手动单执行者拒绝并发取任务并保留 FIFO', async () => {
  const queue = new TeachingQueue(), gate = deferred(), order = [];
  const first = await queue.enqueue(async () => { await gate.promise; order.push('A'); });
  const second = await queue.enqueue(() => { order.push('B'); });
  const worker = queue.runNext();
  await assert.rejects(queue.runNext(), /WORKER_BUSY/);
  assert.equal(queue.state(second.id), 'queued');
  gate.resolve(); await worker; await first.completion;
  await queue.runNext(); await second.completion;
  assert.deepEqual(order, ['A', 'B']);
});

test('空队列没有操作可完成，无效入队被拒绝', async () => {
  const queue = new TeachingQueue();
  assert.equal(await queue.runNext(), null);
  assert.equal(queue.state(99), 'unknown');
  await assert.rejects(queue.enqueue(null), TypeError);
});

test('演示输出逐字匹配交付的预期文本', () => {
  const actual = execFileSync(process.execPath, [fileURLToPath(new URL('./demo.mjs', import.meta.url))], { encoding: 'utf8' });
  assert.equal(actual, readFileSync(new URL('./expected-output.txt', import.meta.url), 'utf8'));
});
