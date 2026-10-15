# 研究来源与边界

本 Skill 从 Claude Desktop 2.37337.1 的已验证公开安装包客户端静态研究提炼问题结构，代码为独立原创模型。不是目标应用源码、drop-in renderer 或全部语义的复现。

可核实机制：

- chat 请求的 streaming Markdown 分支还受挂载时 loader 状态影响
- completed chunks / active tail、受限 fast paths、settled 全文 parse 与再分配
- highlighter 实际 module Worker、grammar-state completed lines、provisional recall、epoch/close
- KaTeX 动态加载与 Mermaid 串行绘制，不能泛称同一种 Worker 架构
- 文件/文档渐进挂载、Markdown content-visibility、代码/diff virtualization 是不同 surface 策略
- AST/tokens/SVG cache 有不同项数与计量限制；容量估算不等于真实 heap

本文没有测得目标应用 FPS、p95、heap 或 cache hit rate，也没有登录执行或调用其私有 API。产品静态 ledger PF-01–47 与配套书章一起提供；Skill 单独复制时不依赖目标 bundle。

主文档：

- https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/content-visibility
- https://react.dev/reference/react/Profiler
- https://developer.mozilla.org/en-US/docs/Web/API/PerformanceLongAnimationFrameTiming

附带模型的明确差异：

1. SnapshotPresenter 使用可注入时钟，24/160ms 是教学配置。
2. StableBlocks 只识别空行段落和顶层 code fences；复杂 Markdown 不安全地独立解析会出错。
3. LatestWorkerLane 传完整、可替换任务，目标 highlighter 传增量并使用 recall；不可混用丢弃规则。
4. WeightedLRU 的 weight 是显式输入，不是引擎内存估值。
5. runSlices 的单元完成后才检查预算；一个昂贵同步单元不能被抢占。
