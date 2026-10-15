# 两个可运行的状态转移案例

原创教学适配器，直接 import 本书已有原模型。没有目标应用代码、网络请求、真实组织或真实记忆数据。案例补充卷八，以及卷九/十之间的状态边界。

## 环境与精确工作目录

Node.js 20+，仅使用内置模块。验证环境为 Node.js v24.19.0。默认从本书根目录 `books/claude-app/` 运行：

```sh
node 04-Extracted-Core-Code-And-Scripts/worked-cases/state-transitions/tree-case.mjs
node 04-Extracted-Core-Code-And-Scripts/worked-cases/state-transitions/settings-case.mjs
node --test 04-Extracted-Core-Code-And-Scripts/worked-cases/state-transitions/state-cases.test.mjs
node 04-Extracted-Core-Code-And-Scripts/worked-cases/state-transitions/verify-demos.mjs
```

两个 demo 的逐行预期输出见 `tree.expected.txt` 与 `settings.expected.txt`；最后一条会逐字比较输出，成功打印 `PASS: 2 deterministic demo outputs match expected snapshots`。测试输出应包含 tests 20、pass 20、fail 0；各项耗时随机器变化，不应当作性能指标。

附加 `--json` 可输出完整可读轨迹：树包括每条消息、四张 Map、currentLeaf、dangling 与 visiblePath；设置包括每次缓存写入和组织切换后的结果。

## 实际 import 链

```text
tree-case.mjs
  → tree-rekey.mjs
    → original-models.mjs
      → ../../core-code-lab/protocol-tree/branch-manager.mjs

settings-case.mjs
  → settings-access.mjs
    → original-models.mjs
      → ../../core-code-lab/memory-flags/memory-flags-model.mjs
```

`original-models.mjs` 的相对 URL 基于它自身位置，而非 shell 的当前目录。它采用以下精确导入：

```js
export const { ConversationBranches, ROOT } =
  await import(new URL('protocol-tree/branch-manager.mjs', coreRoot));
export const { ScopedMutationQueue, applyQueuedOptimistic,
  LatestRequestGuard, decideAccess, resolveFreshAccess } =
  await import(new URL('memory-flags/memory-flags-model.mjs', coreRoot));
```

正常发布布局中，`coreRoot = new URL('../../core-code-lab/', import.meta.url)`。设置 `STATE_CASE_CORE_ROOT` 时，以该环境变量指定的目录作为根；此开关只为暂存验证或已知的原模型目录使用，并不下载或执行目标产品模块。

## 各文件职责

| 文件 | 实现什么 | 刻意不做什么 |
|---|---|---|
| original-models.mjs | 定位并导入已发布的两个原创模块 | 不复制实现、不加载目标 bundle |
| tree-rekey.mjs | 输入索引核对、候选克隆、更名、候选验证 | 不重新实现树遍历/插入、不合并冲突身份 |
| tree-case.mjs | 可复现的前后快照与单引用发布 | 不访问服务端、不管理 React row key |
| settings-access.mjs | 组合组织身份、原版本守卫与新鲜度函数 | 不做真实认证、请求取消或远端授权 |
| settings-case.mjs | 两次受控保存与一次过期读取的确定性时序 | 不用真实时钟、网络或 sleep 猜测调度 |
| state-cases.test.mjs | 20 项反例与正向对照 | 不重跑目标产品或进行性能、安全压力测试 |
| verify-demos.mjs | 对比两个 demo 与文字快照 | 不将运行耗时视为通过标准 |

## 模型的新增边界

- 原 `ConversationBranches` 没有 rekey API。本例返回完整候选树，由调用方一次替换引用；所有旧引用继续指向原快照。窄 fast path 拒绝 assistant 已有主索引或 dangling 后代、正式身份冲突、输入索引不一致等情况。
- 树默认保持主索引与 dangling 的原分区；隐藏分支的选择位置也会恢复。直接对公开 Map 的任意修改不属于原模型的已验证 API，本例只检查并拒绝可发现的不一致。
- 原队列的失败回滚先完成，后续同 scope 操作才开始。第二个 patch 不是提交时就立即乐观生效。
- 原 `resolveFreshAccess` 不识别组织；本例外层检查组织与请求代次。新鲜度、结果归属与用户偏好分别判断。
- `ScopedAccessView` 用一个 guard 表达“本视图只接纳最新请求”，不是通用并发动作调度器。
- 所有允许结果都只是模拟布尔值，未执行任何真实受保护动作。真实应用仍需可信端点的权限验证、明确的事务/幂等性和完整的生命周期处理。
