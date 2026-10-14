import test from 'node:test';
import assert from 'node:assert/strict';
import { NavigationOwner, settleShutdown } from './lifecycle.mjs';
test('旧导航成功不会覆盖新导航失败', () => {
  const owner = new NavigationOwner(), old = owner.begin('old'), now = owner.begin('new');
  assert.equal(owner.settle(now, { ok: false, error: 'offline' }), true);
  assert.equal(owner.settle(old, { ok: true }), false);
  assert.equal(owner.snapshot().error, 'offline');
});
test('伪造同值ticket不能取得归属', () => {
  const owner = new NavigationOwner(), ticket = owner.begin('page');
  assert.equal(owner.settle({ ...ticket }, { ok: true }), false);
  assert.equal(owner.settle(ticket, { ok: true }), true);
  assert.equal(owner.settle(ticket, { ok: false }), false);
});
test('销毁后晚到回调无效', () => {
  const owner = new NavigationOwner(), ticket = owner.begin('page'); owner.dispose();
  assert.equal(owner.owns(ticket), false); assert.equal(owner.settle(ticket, { ok: true }), false);
  assert.equal(owner.snapshot(), null);
});
test('失败清理项不阻止其他项与持久化', async () => {
  let flushed = false;
  const r = await settleShutdown({ ok: () => {}, bad: () => { throw Error('internal'); } },
    { flush: () => { flushed = true; } });
  assert.equal(r.reason, 'settled'); assert.equal(flushed, true);
  assert.deepEqual(r.cleanup.map(x => x.state), ['fulfilled', 'rejected']);
  assert.equal(JSON.stringify(r).includes('internal'), false);
});
test('期限结束不代表任务取消，报告保持快照', async () => {
  let finish;
  const r = await settleShutdown({ slow: () => new Promise(resolve => { finish = resolve; }) }, { deadlineMs: 0 });
  assert.equal(r.reason, 'deadline'); assert.equal(r.cleanup[0].state, 'pending');
  finish(); await new Promise(resolve => setImmediate(resolve));
  assert.equal(r.cleanup[0].state, 'pending');
});
test('落盘失败单独报告', async () => {
  const r = await settleShutdown({}, { flush: () => { throw Error('disk'); } });
  assert.equal(r.reason, 'settled'); assert.equal(r.persistence, 'rejected');
});
test('无界期限与非函数任务提前拒绝', async () => {
  await assert.rejects(settleShutdown({}, { deadlineMs: Infinity }), RangeError);
  await assert.rejects(settleShutdown({ bad: 3 }), TypeError);
});
