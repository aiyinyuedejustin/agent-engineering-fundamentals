# AI 评测基础设施研究知识库

这是持续建设的证据型研究工作区，研究模型、benchmark、agent runtime、隔离环境与测量方法之间的关系。当前是第六批可审阅成果，不是完成版综述，也不是模型总榜。

**继续研究从这里开始：** [RESUME.md](RESUME.md)、[方法与证据等级](methodology.md)、[实际覆盖](research-status/coverage.md)、[索引规范](data/README.md)。

## 当前实际完成的内容

- **65 个经语义去重的模型/训练变体种子**，只表示报告支持的身份区分，不表示核验了 65 个不同权重文件。中央模型表共 **77 条记录**，另保留 3 个具名语音/委派系统与 9 个身份未决的报告条件，不把它们算入 65。
- **342 个 D1 原文数值观测**，来自最新模型数据快照 v12；其中 23 条来源明确是独立评测方或 benchmark 作者。全部仍未由本项目复现，且可比性未判定。
- **47 个代表性 benchmark 目录条目**。加上报告中需要单列的版本、内部评测和历史协议，中央索引有 **159 个 benchmark/协议记录**，不能把它们当作 159 个深度研究。
- **21 篇 benchmark 案例**、12 篇基础设施文章、完整的 22 文件 runtime 专题、5 篇评测科学正文及评分执行链/审查清单。
- **28 个已实际执行的局部诊断程序**。模型代码部分包含 gpt-oss、VLMEvalKit、Ovis 和 HLE 的合成组件探针；它们没有运行模型或重现公开分数。
- 中央索引共有 **485 个来源记录、432 个不同外部来源 URL、533 条证据、24 个概念**。来源记录包含 62 个 D0 候选和 2 个原创本地实验，不能理解为读完了 485 份独立报告。

**完整模型/benchmark 复现数量仍为 0。** 完整深度研究检查表尚未签核，不把局部源码分析冒充 50 个已完成深度研究。200+ 模型种子与五小时以上持续研究要求也没有宣称完成；等待上传不是研究活动。

## 本批基础设施阅读入口

- [KernelBench 的硬件与计时](04-infrastructure/06-kernelbench-hardware-and-timing.md)及[镜像、缓存和运行身份](04-infrastructure/07-images-caches-and-run-identity.md)：硬件、输入重复和缓存键会改变实际测量。
- [网络策略的多个平面](04-infrastructure/08-network-policy-has-multiple-planes.md)：容器网络策略不等于控制器、模型托管工具、MCP 与 verifier 的共同边界。
- [WebArena 状态重置](04-infrastructure/09-webarena-browser-reset-is-not-backend-reset.md)、[BrowserGym/AgentLab 重置与调度](04-infrastructure/10-browsergym-reset-scheduling-contract.md)、[AndroidWorld 设备状态](04-infrastructure/11-androidworld-device-state-contract.md)。
- [Firecracker jailer 与编排器边界](04-infrastructure/12-firecracker-jailer-and-orchestrator-boundaries.md)：固定两个项目的源码版本，不代表已验证它们兼容或实际隔离有效。

本批五个局部实验在集成时独立重放成功，原始结果未改。[HumanEval 单任务尝试](04-infrastructure/experiments/humaneval-single-task/README.md)与[Go jailer 测试尝试](04-infrastructure/experiments/firecracker-jailer-selection/README.md)均为 **BLOCKED**，分别在候选执行前与编译前停止，不计入成功诊断或完整复现。

## benchmark 阅读入口

- [评测选择指南](02-benchmark-landscape/benchmark-selection-guide.md)与[成功事件和测量约定](02-benchmark-landscape/measurement-contracts-guide.md)。目录的 47 项为 30 D1、3 D2、14 D3；没有把组件 D4 提升成整个 benchmark 的 D4。
- [AgentDojo](03-benchmark-cases/agentdojo-utility-and-attack-outcomes.md)、[BFCL](03-benchmark-cases/bfcl-v4-distinct-success-events.md)、[MCP-Atlas](03-benchmark-cases/mcp-atlas-claims-tools-and-denominators.md)：任务效用、工具调用与攻击成功不是同一个事件。
- [HealthBench Professional](03-benchmark-cases/healthbench-rubrics-and-professional-protocol.md)、[GDPval](03-benchmark-cases/gdpval-artifacts-versions-and-judging.md)、[MLE-bench](03-benchmark-cases/mlebench-splits-medals-and-seeds.md)：公开参考实现、内部生产计分与历史报告要分开。
- [MMLU-Pro](03-benchmark-cases/mmlu-pro-prompts-parsers-and-retries.md)、[RULER](03-benchmark-cases/ruler-versions-generation-and-effective-context.md)、[ScreenSpot-Pro](03-benchmark-cases/screenspot-pro-geometry-and-measurement.md)：提示、重试、版本、坐标和聚合改变测量对象。

新收录的 10 个探针均独立重放并与原始输出 JSON 完全一致。ScreenSpot 包括真实公开标注的统计复算，但没有看截图、调用模型或点击 UI；其他探针也保留各自的合成输入、模拟依赖与未覆盖路径。

## 模型阅读入口

- [最新快照 v12](01-model-landscape/snapshots/v12/README.md)：124 个来源/报告候选，62 D1、62 D0；342 个 D1 数值观测。
- [模型身份审查](01-model-landscape/audits/model-identities-v9.md)及[后续 22 个标签](01-model-landscape/audits/model-identities-v12-additions.json)：85 个原始标签不等于 85 个模型。
- [报告笔记 v3](01-model-landscape/snapshots/v3/report-reading-notes-v3.md)、[音频/翻译 v5](01-model-landscape/snapshots/v5/report-reading-notes-v5.md)、[Kimi v7](01-model-landscape/snapshots/v7/report-reading-notes-v7.md)、[独立评测 v9](01-model-landscape/snapshots/v9/report-reading-notes-v9.md)、[多模态 v11](01-model-landscape/snapshots/v11/report-reading-notes-v11.md)、[同权重与版本更新 v12](01-model-landscape/snapshots/v12/report-reading-notes-v12.md)。
- [VLMEvalKit 视频适配器](01-model-landscape/snapshots/v4/experiments/vlmevalkit-video-adapter/README.md)、[Ovis 预处理](01-model-landscape/snapshots/v8/experiments/ovis-preprocessing/README.md)、[HLE simple runner](01-model-landscape/snapshots/v10/experiments/hle-statistics/README.md)：分别 18、19、25 个合成组件探针，集成时独立重放结果完全一致。

推理模式、Agent Swarm、PaCoRe、量化与同权重 deployment 条件保留在具体观测中。Rosalind 6 与 Astra 的同权重关系不表示评测设置或结果等价；Cyber 的额外训练、Sol/Luna 的月份版本不能被抹掉。第三方产品使用“GPT-4o”标签，也不自动证明它是 OpenAI 的对应模型。

## 建议阅读顺序

1. [有效性与评测设计](06-evaluation-science/01-validity-and-evaluation-design.md)：定义问题、任务与成功条件。
2. [评分器与指标](06-evaluation-science/02-grading-and-metrics.md)：答案、解析、分母和 pass@k。
3. [BrowseComp evaluator](03-benchmark-cases/browsecomp-reference-evaluator.md)：沿完整计分接口找证据边界。
4. [Runtime 选型与验收](05-agent-runtime/runtime-selection-and-validation.md)：比较模型、scaffold 与 provider 是不同问题。
5. [隔离与部署](04-infrastructure/01-isolation-is-not-deployment.md)、[快照/reset](04-infrastructure/04-snapshot-and-reset-contracts.md)：恢复对象与外部副作用必须明确。
6. [统计比较](06-evaluation-science/03-statistics-and-comparisons.md)、[judge 可靠性](06-evaluation-science/04-judge-reliability.md)、[污染与生命周期](06-evaluation-science/05-leakage-and-benchmark-lifecycle.md)。

## 目录与证据

`01-model-landscape/` 保存报告、身份审查、数值观察和组件实验；`02-benchmark-landscape/` 是代表性目录；`03-benchmark-cases/` 是任务/源码案例；`04-infrastructure/` 研究环境与执行；`05-agent-runtime/` 研究控制、轨迹、恢复与传输；`06-evaluation-science/` 研究测量有效性。当前公开的 `07–09` 仍是待集成的盲点、学习和架构入口。

D0 是候选发现；D1 是明确范围的报告/文档阅读；D2 是真实任务、配置或关键实现；D3 是具体源码执行链；D4 是保留实际结果的实验。等级只适用于该条证据。D3 不表示已运行，局部 D4 不表示完整复现，模型报告分数不是本项目跑分。

成果仅发布在本仓库独立的 `ai-evaluation-knowledge/` 目录。保留全部历史模型快照，不把历史数据重复加总。只发布审阅后的原创分析、事实记录、测试代码和结果，不重新打包完整上游源码、私有数据或草稿。
