/** 原创离线演示：只操作合成对象，不读取真实记忆或网络。 */
import assert from 'node:assert/strict';
import {
  ScopedMutationQueue, applyQueuedOptimistic, decideAccess,
  evaluateCapabilityGraph, LatestRequestGuard, resolveFreshAccess,
} from './memory-flags-model.mjs';

const queue = new ScopedMutationQueue();
const cache = new Map([['example-workspace', { enabled: false }]]);

// 同作用域的失败先回滚，再让后续修改读取缓存。
const failed = applyQueuedOptimistic(queue, 'example-workspace', cache, { enabled: true }, async () => {
  throw new Error('合成的保存失败');
});
const recovered = applyQueuedOptimistic(queue, 'example-workspace', cache, { mode: 'topics' }, async () => {
  assert.equal(cache.get('example-workspace').enabled, false);
  return { enabled: false, mode: 'topics', saved: true };
});
await assert.rejects(failed, /合成的保存失败/);
await recovered;

// 返回顺序不等于生效顺序；旧请求不能覆盖新的编辑。
const guard = new LatestRequestGuard();
const older = guard.begin();
const newer = guard.begin();
assert.equal(older.isCurrent(), false);
assert.equal(newer.isCurrent(), true);

const access = decideAccess({ clientGate: true, serverStatus: 'available', userEnabled: false });
const refreshed = await resolveFreshAccess({ allowed: true, checkedAt: 0 }, 100, 20, async () => {
  throw new Error('合成的刷新失败');
});
assert.equal(refreshed, false);

console.log(JSON.stringify({
  demonstration: '原创合成数据，不代表真实产品状态',
  cache: cache.get('example-workspace'),
  olderRequestIsCurrent: older.isCurrent(),
  userPausedAccess: access,
  staleAccessAfterFailedRefresh: refreshed,
  prerequisiteOrder: evaluateCapabilityGraph({ compose: { dependsOn: ['chat'] }, chat: { dependsOn: [] } }),
}, null, 2));
