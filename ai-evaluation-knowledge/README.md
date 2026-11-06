# AI 评测基础设施研究知识库

这是持续建设的证据型研究工作区，研究模型、benchmark、agent runtime、隔离环境与测量方法之间的关系。当前内容是第一批可审阅成果，不是完成版综述，也不是模型总榜。

**继续研究从这里开始：** [RESUME.md](RESUME.md)、[方法与证据等级](methodology.md)、[覆盖情况](research-status/coverage.md)、[数据索引规范](data/README.md)。

## 当前实际完成的内容

截至 2026-11-06 首批集成快照：

- **41 个代表性 benchmark 目录条目**，不是 41 个深度复现。加上报告中需要单独区分的版本/协议，中央索引共有 **52 个 benchmark/协议记录**。
- **9 个明确模型名称**，来自已读报告中的结果。推理模式与 Kimi Agent Swarm 没有被当成额外模型。
- **42 个 D1 原文报告数值观测**，保留 harness、任务子集、工具、预算和聚合差异。没有独立复现这些分数。
- **4 篇 benchmark 源码路径案例**：BrowseComp、SWE-bench、原 OSWorld、当前 τ-bench。每篇明确所读版本与未完成部分。
- **5 篇基础设施/runtime 分析**，覆盖隔离、VM 生命周期、资源预算、Harbor trial/verifier、OSWorld/BrowserGym 执行边界。
- **2 篇评测科学正文**及 **4 个局部实验程序**：BrowseComp parser、provider/policy mock、官方 scorer 隔离函数、合成统计诊断。
- 中央索引有 **222 个来源记录、181 个不同来源 URL、106 条证据、8 个概念**。来源记录包含只发现未读的候选与共用官方索引入口，不能把这些数字理解为读完了 222 份独立报告。

**没有完成完整 benchmark/model 运行。** D4 仅指已实际执行的局部函数、模拟控制流程或合成统计实验。完整深度研究检查表尚未签核，因此不把现有案例冒充 50 个已完成深度研究。

## 优先阅读

1. [有效性与评测设计](06-evaluation-science/01-validity-and-evaluation-design.md)：先定义决策、任务与可观察成功条件。
2. [评分器与指标](06-evaluation-science/02-grading-and-metrics.md)：分清答案正确、解析成功、有效分母和 pass@k。
3. [BrowseComp reference evaluator](03-benchmark-cases/browsecomp-reference-evaluator.md)：一个小 parser contract 可以改变整条计分链。
4. [Harbor 执行链](05-agent-runtime/harbor-source-trace.md)：agent、environment、trial、verifier 是不同对象。
5. [隔离与部署](04-infrastructure/01-isolation-is-not-deployment.md)及[资源预算](04-infrastructure/03-resource-budgets-change-the-test.md)：相同配置文字未必等于相同执行条件。
6. [模型报告快照 v1](01-model-landscape/snapshots/v1/README.md)：94 个来源/报告候选中只有 19 个达到所标范围的 D1，其余 75 个仍为 D0。

## 目录

| 路径 | 内容 |
|---|---|
| `01-model-landscape/` | 模型报告、来源登记和报告数值观察 |
| `02-benchmark-landscape/` | 代表性 benchmark 目录与版本边界 |
| `03-benchmark-cases/` | 真实任务、配置、评分器和源码路径案例 |
| `04-infrastructure/` | 隔离、部署、资源、生命周期与局部测试 |
| `05-agent-runtime/` | agent loop、trial、环境接口与日志/产物契约 |
| `06-evaluation-science/` | 有效性、评分、统计与实际局部实验 |
| `07-unknown-unknowns/` | 尚未系统填充的盲点与开放问题 |
| `08-learning-path/` | 待从已核验证据形成的学习路线 |
| `09-architecture-decisions/` | 待审阅的架构方案与权衡，尚无已接受架构 |
| `data/` | 模型、benchmark、结果、概念、来源与证据索引 |
| `research-status/` | 实际覆盖、验证范围与下一步 |

## 证据等级

- D0：发现候选，未核验实质内容。
- D1：已读官方报告、论文或文档的明确范围。
- D2：已读真实任务、配置或关键实现。
- D3：已跟踪具体源码执行路径。
- D4：已实际执行实验，并保留设置、结果与限制。

等级用于**具体证据范围**。D3 不表示已运行；局部 D4 不表示完整 benchmark 复现；模型报告分数不是本项目跑分。中央实体的 depth 仅为已关联证据的最高等级，不是该实体所有属性的统一可信度。

## 长期目标与限制

目标仍是 200+ 可追溯模型种子与 50 个实质性 benchmark 深度研究，不按别名、配置或占位文件凑数。五小时以上持续研究要求仍未宣称完成；以实际研究活动和产物为准，不用等待时间替代工作。

成果持续发布在 `aiyinyuedejustin/agent-engineering-fundamentals` 的独立 `ai-evaluation-knowledge/` 目录。只发布审阅后的原创分析、事实记录、测试代码和结果，不重新打包完整上游源码、私有数据或未审阅草稿；保留仓库其他内容。
