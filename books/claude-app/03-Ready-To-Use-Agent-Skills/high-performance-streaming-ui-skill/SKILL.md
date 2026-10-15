---
name: high-performance-streaming-ui-skill
description: Design, profile, and harden streaming text interfaces with explicit parsing, batching, formatter, memory, and lifecycle contracts. Use for token-stream chat, long Markdown, code highlighting, mathematical rendering, diagrams, or long document views. Do not promise FPS from source constants.
---

# 高性能流式界面：先定合同，再选优化

## 目标与边界

让最终内容始终正确，让输入与阅读不被格式化工作长时间阻塞，让每个异步任务与缓存都有明确寿命。

这是跨框架工程 Skill，附带独立原创零依赖模型。研究来源解释为什么这些问题重要，不要求采用 Claude 的参数或依赖。不能把目标产品的源码存在性当成运行时成绩；也不能复制或执行未获授权的目标 bundle。

## 何时使用

- 长流式 Markdown 每次 token 都卡顿，或生成结束时突然大卡顿
- 代码高亮、数学、图表抢占交互，Worker 失效后界面不稳定
- 长会话/文件打开慢，滚动跳动，切换后内存持续增加
- 需要在性能改造后仍保证取消、回撤、主题变化、复制、搜索与导出

如果问题只是网络返回慢，先记录 receive 时间，避免把服务端等待误判为 render 慢。

## 第一步：画出真实执行路径

从实际调用点开始，而不是搜索库名后猜测：

```text
bytes → ordered events → authoritative reducer → replaceable snapshot
      → parser → formatter → UI commit → layout/paint
```

每条箭头都标注：同步/异步、线程、输入身份、可否合并、是否可取消、所有者。检查活动 renderer 的选择条件、挂载时 latch、功能 flag、加载失败与 fallback。Worker 必须闭合 factory → caller → worker asset/message handler；虚拟化必须看到 range、spacer、mount/unmount 或对应实现。

交付一张事实表：observed source / observed runtime / inference / original proposal。未运行时，不给产品 FPS、p95 或峰值 heap 数字。

## 第二步：先冻结正确性合同

必须明确：

1. 所有协议 delta 按顺序进入 reducer；只允许合并包含全部历史变化的完整快照。
2. first、final、error、abort、retract 的发布语义分别定义；不能等 debounce 安静后才显示 final。
3. 非前缀编辑、语言/主题/插件变更会使哪些缓存、扫描状态和任务失效？
4. 页面离开/组件卸载后，旧回复不能写回新状态。
5. 富格式化失败时保留安全的原文或普通代码；不能让用户内容消失。
6. 完成时使用完整 parser 或等价的权威校验，处理晚到引用定义等跨块语义。

不要在没有这些合同与测试时开始激进虚拟化。

## 第三步：从最小工作范围开始

按这个顺序评估，不是强制全部启用：

- 合并交付：一个 pending 完整 snapshot，首次和 terminal 明确 flush。
- 稳定块：已完成区间维持身份，活动尾块单独处理。
- 受限 fast path：只处理明确证明安全的语法子集，拒绝时立即走完整 parser。
- 最终全文处理：区分 streaming tree 与 settled tree；比较后再复用。
- 格式化隔离：分别测高亮、数学和图表；async import 不是 Worker。
- 离屏策略：先评估 content-visibility，再评估渐进挂载与真正虚拟化，记录各自功能代价。

成本模型要同时包含 parser 输入量、任务次数、string/copy 成本、DOM、layout、GC 和缓存。复杂度论证不能只统计完成行。

## 第四步：给 Worker 与富内容单独写协议

对于可替换的完整计算任务，可以使用附带 LatestWorkerLane：一个在途任务、一个最新 pending snapshot、epoch + sequence、显式 plain fallback。

```js
import { LatestWorkerLane } from './scripts/model.mjs';
const lane = new LatestWorkerLane({
  send: job => worker.postMessage(job),
  cancel: job => worker.postMessage({ cancel: true, ...job }),
  publish: (result, job) => commitIfStillCurrent(result, job),
  fallback: (text, reason) => showPlainText(text, reason),
  maxChars: 100_000
});
// 生产实现还必须验证 reply schema、监控超时与 Worker error。
worker.onmessage = event => {
  const { epoch, sequence, result } = validateReply(event.data);
  lane.reply({ epoch, sequence }, result);
};
```

代码中的 validateReply、commitIfStillCurrent、showPlainText 是接入点。脚本没有创建真实 Worker，也没有实现生产 schema。

增量高亮协议如果使用 provisional tail/recall，不能套用“只留最新 delta”策略。必须验证 recall、覆盖范围、源 revision、语言与主题，完成行和末行的处理不同。

给每个队列写单位和 cap：bytes、UTF-16 code units、事件数、jobs、AST 节点等。单批大小不等于总 pending 上限。超限选择暂停 admission、降级或终止，不能静默截断权威内容。

timeout 只是停止等待。若底层任务仍运行，标记 stuck 或隔离它；不要无限继续入队。协作式 yield 只能发生在工作单元之间，无法抢占一个长同步函数。

## 第五步：资源清单与所有权

列出并逐项验证：

| 资源 | 必须回答 |
|---|---|
| timer / rAF / idle callback | 谁创建，谁 cancel，竞争式后备是否 exactly once？ |
| observer / listener | disconnect/remove 在哪条 cleanup？ |
| per-stream Worker state | close 是否删除，旧 reply 是否被 epoch 拒绝？ |
| shared Worker | 谁负责全局 terminate，组件是否错误地频繁重建？ |
| AST / token / SVG cache | 项数、总估算、单项、寿命、配置键、eviction |
| pending promises | 取消是否只是忽略结果，底层何时真正结束？ |

缓存账本与真实 retained heap 分开汇报。检查最大单项能否绕过总阈值，以及全局缓存是否保持已卸载内容。

## 第六步：可见性与阅读完整性

至少覆盖：隐藏再恢复、后台停滞、活动输入、拖选、焦点、Anchor scroll、Copy、Find、Print/Export、辅助技术。

- content-visibility 仍保留 DOM；不能称为虚拟列表。
- 渐进挂载必须允许跳转强制 reveal-through、导出 reveal-all。
- 虚拟列表必须给选择、搜索、复制与焦点单独定义策略。
- 高度估计变化需要滚动锚点补偿；不要在用户正在拖选时低优先级预布局。

## 第七步：测试与度量

先运行附带契约测试：

```sh
node --test scripts/test/*.test.mjs
```

46 项覆盖快照合并、terminal、重入、可见性、dispose、半个 fence、非前缀编辑、Unicode、全文 finalize、缓存权重、Worker epoch、旧回复、最新原文 fallback、send failure、协作预算与取消。

教学 StableBlocks 只识别空行段落及顶层 fence，不是 CommonMark。真实应用必须替换 parser adapter，并补充：表格、列表嵌套、引用定义、数学、HTML、主题切换、超长行、协议破坏与异常恢复。

运行时基准必须用相同设备、语料、构建模式、缓存与节流条件，记录：

- first meaningful text、receive-to-commit、receive-to-visible
- 每类 formatter 的等待、耗时、回退原因与成功率
- backlog 最大值、队列/缓存计量、最终内容一致性
- React render/commit 与浏览器 layout/paint 分开
- Long Animation Frames 支持性、用户输入延迟
- 重复挂载与导航后的 retained heap、活动资源数

避免在生产日志里记录完整用户正文。优先记录长度、状态、计数、采样 timing 与非敏感合成 case ID。

## Anti-Patterns：禁止未经证据的捷径

| Anti-pattern | 修正 |
|---|---|
| 把每个 token 当成一次完整 UI 事务 | reducer 保序，snapshot 合并，final 明确 flush |
| 看到 rAF 就宣布 60 FPS | 记录真实 frame/paint 与设备刷新率 |
| 看见 Worker 构造器就说全 parser 后台化 | 追到实际 caller、消息契约和 fallback |
| 在 rAF 内做一次巨大 parse | 缩小语法范围或单元；必要时真正线程隔离 |
| 把 Promise.race 当成强制停止计算 | 处理未结束任务与后续 admission |
| 缓存只设 entry count | 加总权重、单项限制、寿命和配置失效 |
| 用文案中的 onFirstPaint 作为像素证明 | 验证实际 callback 所在 effect/commit 边界 |
| 每个 unmount terminate 共享 Worker | 单流 close；全局生命周期另管 |
| 以固定 FPS 为唯一验收 | 内容正确性、输入响应、尾部延迟、资源共同验收 |
| 直接移植产品常量 | 把它当假设，用自己的负载测量参数 |

## 输出要求

交付真实路径图、改动前后证据、契约测试、回退策略、资源清理表与剩余风险。清楚区分 passed / failed / never run。不要把本 Skill 的原创模拟统计当成 Claude 或你项目的真实性能成绩。

详见 [研究证据边界](references/evidence-boundaries.md) 与 [评测矩阵](references/benchmark-matrix.md)。

## 模型预算配置

maxChars 和缓存 entries 必须是有限非负安全整数；缓存 weight/itemWeight 允许有限非负小数。显示延迟须在 0–2,147,483,647ms 范围内；runSlices 的 budget 须为有限正数。预算与延迟构造后只读，需要变更时新建所有者并显式迁移状态。无效配置立即报错，不把 NaN 当作无限预算。字符预算按 UTF-16 code unit 计算。这些是原创教学合同，不是 Claude 限制。
