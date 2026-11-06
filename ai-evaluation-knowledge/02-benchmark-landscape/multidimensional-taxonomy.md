# Benchmark 不是一张排行榜：多维分类与选择方法

更新日期：2026-11-06。本文是对已经关闭的第一批采集包的综合，不声称覆盖全部基准；个别项目仍只有 D1 文档证据。具体深度、版本和限制见 [机器可读目录](benchmark-catalog.json) 与 [源码案例](../03-benchmark-cases/)。

## 1. 先辨认自己看到的是哪一种对象

同样被称为 benchmark 的东西，可能处于不同层次：

1. **数据集**：题目、答案、参考材料及划分。例如 GPQA 的不同子集。
2. **任务集合**：每题还包含初始化、工具、时间预算和成功条件。例如 OSWorld、Terminal-Bench。
3. **执行与判分实现**：怎样调模型、操作环境、提取答案、调用 judge、聚合结果。例如 simple-evals 的参考实现。
4. **测量方法**：把多次实验转成有含义的指标。例如 METR 用任务的人类完成时长拟合成功率曲线。
5. **持续评测服务**：维护提交、抽样、环境与数据更新，并发布结果。例如动态 benchmark 或竞技场。
6. **复合指数**：把不同来源、不同量纲或归一化分数按权重合成。Artificial Analysis Intelligence Index 就有明确版本、子项及权重。

同一个项目可以横跨几层，但层次不能互相替代：有公开数据不代表可复现整个系统；有开源 harness 不代表测试集开放；一个总指数也不是新的原子能力。

[METR 测量说明](https://evals.alignment.org/time-horizons/) · [Artificial Analysis 指数方法](https://artificialanalysis.ai/methodology/intelligence-benchmarking) · [simple-evals](https://github.com/openai/simple-evals)

## 2. 十四个互相独立的分类轴

| 轴 | 需要记录的问题 | 为什么影响解释 |
|---|---|---|
| 测量目标 | 知识、推理、检索、实现、交互、偏好、安全或可靠性？ | “困难”并不是统一能力。 |
| 被测单位 | 基础模型、模型+固定工具、完整 agent、产品系统、某个组件？ | 工具与 scaffold 的进步不能全归因于模型权重。 |
| 输入与输出模态 | 文本、图像、视频、音频、结构化数据、文件、动作？ | 输入有图片不代表输出也被视觉评估。 |
| 任务形式 | 选择题、短答案、长文、代码、状态变更、可交付文件？ | 输出形式决定可用的验证方法。 |
| 交互结构 | 一次回答、固定多轮、模拟用户、真实反馈、环境循环？ | 对话历史作为输入，不等于模型参与了多轮交互。 |
| 环境闭合程度 | 静态文本、可重置模拟服务、容器、VM、真实网站？ | 真实性、漂移、成本和可复现性互相牵制。 |
| 时间结构 | 长输入、长生成、多步任务、跨会话记忆、真实持续工作？ | “长”可能描述完全不同的维度。 |
| 参考与判分 | 精确匹配、执行测试、数据库状态、规则、rubric judge、人评？ | 各有漏判、误判和成本，不能用一个准确率标签掩盖。 |
| 成功逻辑 | 任一通过、全部通过、加权部分得分、阈值通过、守卫条件？ | 80% rubric 覆盖与80%任务成功是不同随机变量。 |
| 资源预算 | tokens、工具次数、wall clock、GPU、网络权限、美元？ | 分数随预算变化，资源是实验条件。 |
| 数据与环境时效 | 固定、定期刷新、滚动时间窗、在线生成？ | 控制污染与保持可比性不是同一目标。 |
| 开放性 | 任务、答案、资产、镜像、judge prompt、完整日志分别开放吗？ | “open”应拆成字段，不能只填一个布尔值。 |
| 统计设计 | 单次、重复、配对、分层、置信区间、错误处理？ | 小样本、重试和缺失处理能改变排名。 |
| 适用范围 | 领域、语言、用户分布、真实损失、排除条件？ | 外部效度需要证据，不能由榜单领先推导。 |

这些轴是分析框架，不是官方共识标准。它们的作用是迫使比较者把隐含条件写出来，而不是发明又一个万能分数。

## 3. 用任务结构而不是营销名称组织生态

### 3.1 静态知识与推理

MMLU-Pro、GPQA、HLE、BBEH、FrontierMath 提供不同领域、题型与难度的切面。应至少区分选择题与开放答案、文本与多模态、公开与私有、主集与精选子集。HLE 与 HLE-Diamond，FrontierMath 不同 tier 或新项目，不能按名字相似就当成同一测量。

这类测试通常容易并行、容易保存输入输出，但无法单独回答一个 agent 能否长期可靠操作工具。

[MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro) · [GPQA](https://github.com/idavidrein/gpqa) · [HLE](https://github.com/centerforaisafety/hle) · [FrontierMath](https://epoch.ai/frontiermath)

### 3.2 检索与研究

BrowseComp 的核心是难以找到但相对容易核对的短答案。DeepResearch Bench 及其后续版本更关注研究报告内容、分析和引用。两者可以互补，但短答案正确不能代替报告覆盖、证据质量与论证评价。引用存在也不等于引用支持了相应主张。

[BrowseComp 源码案例](../03-benchmark-cases/browsecomp-reference-evaluator.md) · [DeepResearch Bench](https://deepresearch-bench.github.io/) · [DeepResearch Bench II](https://agentresearchlab.com/benchmarks/deepresearch-bench-ii/)

### 3.3 长上下文与记忆

LongBench v2 和 RULER 能帮助研究长输入条件下的信息处理，但长上下文长度不是跨会话记忆的同义词。原始材料长度、实际输入 tokens、截断或检索策略、问题位置、信息密度，都应分别记录。

同样，多周故事背景并不自动成为连续多周 agent 实验。Artificial Analysis 当前 AA-Briefcase 方法明确把任务作为独立运行，后续任务接收统一参考材料而非沿用该模型自己此前的交付物。这是场景真实性与持续状态实验的关键区别。

[LongBench](https://github.com/THUDM/LongBench) · [RULER](https://github.com/NVIDIA/RULER) · [AA-Briefcase 方法](https://artificialanalysis.ai/methodology/intelligence-benchmarking)

### 3.4 编码与工程

函数补全、竞赛题解、仓库 issue 修复、终端系统任务、机器学习实验是不同工作。HumanEval、LiveCodeBench、SWE-bench、Terminal-Bench、MLE-bench、PaperBench 不构成一条简单难度梯子。

例如 SWE-bench 关注提交补丁是否修复并避免指定回归；Terminal-Bench 可要求构建一个完整评估工具；PaperBench 涉及论文实现与复现阶段。应分别检查测试覆盖、环境安装、隐藏验收、运行时限和 artifact 边界。

[SWE-bench 案例](../03-benchmark-cases/swe-bench-task-and-grading.md) · [Terminal-Bench 案例](../03-benchmark-cases/terminal-bench-evaluating-an-evaluator.md) · [PaperBench 项目](https://github.com/openai/frontier-evals/tree/main/project/paperbench)

### 3.5 工具与交互 agent

工具名与参数生成、真实多步调用、模拟用户对话、可变数据库状态、桌面 GUI 是不同层次。BFCL、MCP Atlas、τ-bench、WebArena、OSWorld、AndroidWorld 分别暴露这些维度的一部分。

特别是“正确调用”与“任务完成”要分开。τ-bench 的状态验收可接受与参考动作序列不同但结果正确的路径；OSWorld 的某些任务读取应用配置或文件状态，而不是依据最终截图看起来是否正确。不同任务的成功判定仍需逐题阅读。

[τ-bench 案例](../03-benchmark-cases/tau-bench-outcomes-and-reliability.md) · [OSWorld 案例](../03-benchmark-cases/osworld-state-evaluator.md) · [MCP Atlas](https://labs.scale.com/papers/mcpatlas) · [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html)

### 3.6 专业交付物、偏好与安全

GDPval、HealthBench 与专业科学任务评测引入领域判断，但真实职业的法律责任、协作和长期后果并没有全部进入测试。偏好竞技场主要回答人们更喜欢哪一个输出；安全基准则可能衡量拒绝、攻击成功率、正常任务效用或二者组合。三种问题不能互相替代。

HealthBench 虽以对话历史为输入，官方主评测是生成待评分的最后一轮回复，不应自动归入完整多轮医疗 agent 测试。传统文本 Arena 与新 Agent Arena 也应分开：后者方法采用工作流组件随机分配及任务过程信号，不是简单把文本双盲投票换一个名字。

[GDPval](https://openai.com/index/gdpval/) · [HealthBench](https://openai.com/index/healthbench/) · [Agent Arena 方法](https://arena.ai/blog/agent-arena-methodology/) · [HarmBench](https://github.com/centerforaisafety/HarmBench) · [AgentDojo](https://github.com/ethz-spylab/agentdojo)

## 4. 一个结果应拥有“测量身份”，而不只是分数

建议每条结果最少关联以下信息：

```text
result_identity = {
  model_revision, reasoning_mode, system_prompt,
  agent_scaffold_revision, tool_set, tool_permissions,
  dataset_revision, task_subset, environment_revision,
  inference_budget, retry_policy, trial_count,
  grader_revision, judge_model_revision, aggregation,
  error_policy, run_date
}
```

这是建议的数据结构，不是某个官方 API。若关键字段未知，应明确写 unknown；不能用后来读到的最新代码补填旧成绩的运行条件。代码提交日期、数据集日期、实验日期和网页访问日期也应分开。

## 5. 六个经常误导比较的词

- **pass@1**：可能是单次样本成功率，也可能是多个重复的均值。重复次数本身不等于允许多次尝试后挑最好。
- **pass@k 与 pass^k**：前者通常是 k 次至少一次成功，后者常用于 k 次全部成功的可靠性。τ-bench 的组合估计与 HumanEval 的成功发现概率不能混用。
- **agentic**：需要说明实际行动、环境状态和反馈，不只是模型输出较长推理。
- **human-level**：需要说明人类基线任务、时间、工具、经验、样本及估计方法。
- **open**：分别问任务、答案、资产、环境、scaffold、judge 和日志是否开放。
- **long-horizon**：需区分 agent 实际运行时间、步骤数、输入长度与人类任务时长。METR horizon 不是模型在现实世界可以自主连续工作的保证时长。

[τ-bench 可靠性说明](../03-benchmark-cases/tau-bench-outcomes-and-reliability.md) · [METR time horizons](https://evals.alignment.org/time-horizons/)

## 6. 从使用目标倒推一组小而互补的评测

| 目标 | 先选择的测量类型 | 不能省略的补充 |
|---|---|---|
| 选择客服工具 agent | 对话+业务状态成功、policy 约束、重复可靠性 | 自己的业务数据、真实错误成本与人工接管。 |
| 选择代码助手 | 单元能力+仓库修复+实际开发流程 | 安全、回归、依赖安装、成本和 reviewer 时间。 |
| 选择研究助手 | 短答案检索+长报告证据与引用 | 自家领域时效、引用支持度、遗漏及信息来源权限。 |
| 选择桌面助手 | 可重置 GUI 任务+最终状态验收 | 应用版本、恢复策略、误操作风险和完成成本。 |
| 评估通用模型更新 | 固定回归集+新鲜外部任务+成对失败分析 | 同预算对比、置信区间、污染风险和部署分布。 |
| 研究 evaluator | 小型已知答案集+边界样例+源代码追踪 | judge 校准、错误归因、未评分与基础设施失败。 |

这些是设计建议而非具体模型推荐。公开基准最适合提供外部参照与诊断线索；生产决策仍需要代表实际使用分布的独立任务与验收标准。

## 7. 当前证据边界

本批次覆盖41个代表性目录记录，只有若干案例达到真实任务与源码路径层级。音频、视频、跨语言、机器人与真实长期记忆仍覆盖不足；私有评测的任务质量与运行细节无法仅凭方法页独立验证。任何“全面生态”或“最全面排行榜”的说法都超出了现有证据。
