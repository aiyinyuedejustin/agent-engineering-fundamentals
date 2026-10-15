# 流式呈现调度实验室

独立原创、零依赖的可运行模型。它借鉴经证据核实的问题分解，不导入、执行或复制 Claude 目标模块，也不连接服务端。

## 运行

需要支持 Node 内置 test runner 的 Node.js（建议 Node 22 或更新）：

```sh
node --test test/*.test.mjs
node simulate.mjs
```

从本目录执行。测试验证契约，模拟统计逻辑解析输入量，不宣称浏览器帧率或真实产品加速比。

## 五个可迁移组件

| 组件 | 契约 | 主动简化/差异 |
|---|---|---|
| SnapshotPresenter | 完整快照合并、首次/终止立即交付、可见性切换、dispose | 24/160ms 是实验参数；不是 Claude 常量；不是实际浏览器 paint |
| StableBlocks | 已完成块身份稳定，未完成行不提交扫描状态，非前缀编辑重建，最终全文解析 | 仅空行段落及顶层 fence 子集；不是 CommonMark 解析器 |
| LatestWorkerLane | 一个在途完整任务、一个最新快照、epoch/sequence、plain fallback | 无真实线程；与目标的增量 delta+recall 高亮协议不同 |
| WeightedLRU | 同时限制项数、总权重及单项权重 | 权重由调用方提供，不是实际 heap bytes |
| runSlices | 单元完成后检查预算/取消，再让出任务 | 无法抢占一个尚未返回的昂贵单元 |

`FakeClock` 让 race、重入、隐藏、终止和销毁可确定地复现；生产适配时替换为真实调度器，并记录真实浏览器 trace。

## 使用示例

```js
import { SnapshotPresenter, StableBlocks, LatestWorkerLane } from './model.mjs';
const splitter = new StableBlocks({ finalParser: wholeText => yourMarkdownParser(wholeText) });
const presenter = new SnapshotPresenter({
  clock: { schedule: (fn, ms) => setTimeout(fn, ms), cancel: clearTimeout },
  commit: snapshot => {
    const state = splitter.update(snapshot.text, { terminal: snapshot.terminal });
    renderYourView(state); // 接入业务组件；安全处理生成内容
  }
});
// 此处必须传入 reducer 已按顺序处理完全部 delta 的完整快照。
presenter.accept('第一段\n\n活动尾部');
presenter.accept('第一段\n\n活动尾部完成', { terminal: true });
```

示例中的 parser 和 view 是接入点，不是实验室已经实现的功能。不要把测试通过解释为它们已接受安全或性能验证。

## 关键限制

- chunk scanner 不支持所有列表、表格、HTML、引用定义、数学和嵌套块语义。真实应用必须用完整 parser，确认安全的增量边界，并保留最终全文一致性检查。
- 输入长度、缓存权重和队列限制需要按业务设定。实验没有实现网络字节缓冲或服务端背压。
- WorkerLane 合并的是可替换的完整格式化任务，不能丢弃协议 delta。真实 Worker 必须验证消息形状，支持崩溃、重启和有限重试。
- 原始文本/代码始终可显示；格式化失败不应让内容消失。HTML 转义示例只适用于文本插入，不能替代完整 HTML sanitizer 或 URL allowlist。
- 46 项测试验证最终内容、资源释放和竞争条件；没有启动目标 Claude 或测量真实 DOM、GPU、堆内存、帧率。

## 模型预算配置

maxChars 和缓存 entries 必须是有限非负安全整数；缓存 weight/itemWeight 允许有限非负小数。显示延迟须在 0–2,147,483,647ms 范围内；runSlices 的 budget 须为有限正数。预算与延迟构造后只读，需要变更时新建所有者并显式迁移状态。无效配置立即报错，不把 NaN 当作无限预算。字符预算按 UTF-16 code unit 计算。这些是原创教学合同，不是 Claude 限制。
