# 跨基准测量契约：同一分数究竟在说什么

研究日期：2026-11-06。本文是对本轮已完成案例的有界综合，不新增外部事实，也不增加任何 benchmark 的验证深度。案例中的 D3 仅代表指定源码路径，组件 D4 不代表模型、产品或整个基准已经复现。

## 1. 一个可比较结果的最小单位

结果不是“模型名 + benchmark 名 + 数字”，而是：

**模型/端点版本 × 任务与数据版本 × 可用信息和工具 × 执行预算 × 采样/选择策略 × 成功事件 × 聚合与失败处理。**

只要其中一项改变，便应先视为新的实验条件。需要比较，不一定需要完全相同，但必须能指出差异及其可能改变的解释。

把 claim 拆成三个层次：
1. 观察：这次产物/轨迹在这个 grader 下得到什么。
2. 能力解释：它支持对哪种能力做多大范围的推断。
3. 部署推断：能否在用户的环境、风险和任务分布下使用。

第三层不能直接从第一层跳到。真实工具不保证真实工作流程覆盖，真实工作任务也不保证实际业务收益。

## 2. 从成功事件出发选基准

| 成功事件 | 已读代表案例 | 能支持的窄结论 | 仍需额外验证 |
|---|---|---|---|
| 选项/答案被 parser 判对 | [MMLU-Pro](../03-benchmark-cases/mmlu-pro-prompts-parsers-and-retries.md)、[LongBench v2](../03-benchmark-cases/longbench-v2-protocol-audit.md) | 给定 prompt/context 与答案抽取规则的题目正确率 | 生成步骤是否可靠、parser 是否把否定/修正看错 |
| 明示格式约束被机械检查满足 | [IFEval](../03-benchmark-cases/ifeval-verifiable-instructions.md) | 可验证指令维度上的遵从 | 其他语义需求、内容质量、同一变换下能否共同满足 |
| 代码在指定测试下通过 | [SWE-bench](../03-benchmark-cases/swe-bench-task-and-grading.md)、[SciCode](../03-benchmark-cases/scicode-scientific-tests-and-bookkeeping.md) | 覆盖到的功能/数值行为 | 测试覆盖外的正确性、安全、可维护性 |
| 预测质量达到历史参照线 | [MLE-bench](../03-benchmark-cases/mlebench-splits-medals-and-seeds.md) | 新测试划分上训练/推理产物达到参照指标 | 原 Kaggle 排名、真实商业泛化与算力效率 |
| 函数调用表示符合候选集合 | [BFCL v4](../03-benchmark-cases/bfcl-v4-distinct-success-events.md) | 函数/参数选择与可解析输出 | 实际执行、副作用、最终用户目标 |
| 环境状态与期望状态相同 | [OSWorld](../03-benchmark-cases/osworld-state-evaluator.md)、[τ-bench](../03-benchmark-cases/tau-bench-outcomes-and-reliability.md) | 被检查的持久状态/约束达成 | 未检查状态、沟通、过程和权限 |
| 最终答案覆盖预设 claim | [MCP-Atlas](../03-benchmark-cases/mcp-atlas-claims-tools-and-denominators.md)、[BrowseComp](../03-benchmark-cases/browsecomp-reference-evaluator.md) | 输出被判包含所需信息 | 信息来源、未列入 rubric 的错误、动作真实完成 |
| 专业 rubric 的加权质量 | [HealthBench Professional](../03-benchmark-cases/healthbench-rubrics-and-professional-protocol.md) | 被选任务与 rubric 下的回复质量 | 临床实际成效、未评风险、产品和内部实现差异 |
| 交付相对人工基线被偏好 | [GDPval](../03-benchmark-cases/gdpval-artifacts-versions-and-judging.md) | 指定专家/judge、工具配置与文件产物的相对偏好 | 整个职业替代、工作流成本、签字责任 |
| 随机分配后的用户反馈变化 | [Arena / Agent Arena](arena-preference-and-agent-signals.md) | 该流量分布与反馈定义下的相对效应 | 其他用户群、沉默任务的成功、绝对正确率 |
| 交互完成与行动效率 | [ARC-AGI-3](../03-benchmark-cases/arc-agi-3-scoring-and-context.md) | 游戏协议与参考行动数下的完成/效率分 | 真实通用工作能力；本轮还没有实际游戏输入核验 |
| 分组视频问题正确结构 | [Video-MME-v2](../03-benchmark-cases/video-mme-v2-grouped-scoring.md) | 给定分组与帧/字幕协议下的问答表现 | 完整视频理解、不同适配器下的可比性 |

这不是互斥分类。一个 benchmark 可以有多个分支，BFCL 正是 AST、模拟状态与答案匹配共存的例子。应在“结果记录”层写事件，而不是给整个 benchmark 永久贴一个标签。

## 3. 六个最容易被藏起来的接口

### A. 用户任务 → 实际模型输入

问题不一定完整送入模型。要找：
- 题目/附件是否转换、降采样或裁掉；
- few-shot、CoT、system prompt、语言与选项拼接；
- 工具 schema 是否整批暴露，是否混入干扰工具；
- 历史消息是否保留原生 reasoning 状态、手工摘要或文本截断。

例：LongBench v2 的长文可能按 token 预算裁头尾；视频适配器的帧选择决定模型真正看见什么；MCP-Atlas 的 compact 实际做前缀截断。

### B. 模型输出 → 可评价产物

解析失败不是自动等同能力失败，也不是可以悄悄丢掉的样本。
- MMLU-Pro 本地脚本对无法抽取的答案会随机猜，另一些路径又不同。
- GDPval 的最后回复只是文件产物的一部分。
- MCP-Atlas 遇预算退出时仍可能抽出之前的 assistant 文字。

需要保存 raw output、parsed output、finish reason 与解析日志，才能区分模型未完成、格式不符和 grader 接口错误。

### C. 产物 → 评分器看到的对象

代码测试可能运行修改后的仓库；状态 checker 只看某些字段；LLM judge 可能只看最后文本，不看轨迹或附件。不能由存在 trajectory 文件推断它进入了评分。

审计时画出最短事实链：**哪一段数据传给哪个函数，返回哪个布尔/数值，被哪一层再聚合**。看文档里的“验证”“执行”“多模态”不足以替代这条链。

### D. 单项结果 → 每题分数

- rubric 可以有负分或长度校正，不能叫“百分之多少题答对”。
- 同一题的多个约束可以 AND；多个 claim 可以取平均。
- 组内顺序、前缀正确性或平方惩罚，会让相同正确题数得到不同分。
- 未运行的提供步骤、跳过步骤、无 gold 分支，应检查是否还在分母中。

同样的二值子项列表，经过不同函数后可以代表完全不同的成功事件。

### E. 每题分数 → benchmark 汇总

最低限度列出：
- 计划题数；
- 实际开始、完成、有效、评分成功的题数；
- 唯一任务数，避免重复行；
- 缺失、异常、不可评分的处理；
- 题目/领域/职业/组别的权重；
- 采样次数与 best-of-N、pass@k、pass^k、重试的区别。

不能把每题多次采样的最佳值当成单次性能，也不能把所有重试均成功的可靠性与至少一次成功混称“成功率”。

### F. benchmark 汇总 → 人的决策

部署需要的并非总榜第一，而是：
- 当前任务分布下的效用；
- 最坏后果和可恢复性；
- 人工核查负担；
- 延迟、成本和资源上限；
- 版本变化后能否重新评估。

高分可以用于筛选候选，不应越过任务相关验证和风险审查。

## 4. 为什么 D4 也要写范围

本轮有三种性质不同的实验：
1. 原始评分函数 + 合成输入，验证算术、parser 或控制流。
2. 已发布实际输出/判断的再分析。
3. 真正跑模型、工具或环境，完成实际 task。

前两种可以是局部 D4，但不会自动成为第三种。报告需要同时写“执行了什么”和“没有执行什么”，例如：
- 正确：在固定源码的 claim aggregator 上用替身 judge 验证缺失分母。
- 不正确：已经验证 MCP agent 的真实能力。
- 正确：读到真实视频题目元数据与 scoring code，没有看媒体。
- 不正确：已经完整验证视频任务或视频模型。

深度不是排名游戏。对保密 benchmark 能诚实做到 D1，比把未读数据或未运行环境写成 D3/D4 更有用。

## 5. 可复用的结果契约字段

下面是字段模板，不是真实运行结果：

```json
{
  "benchmark": {
    "name": "example",
    "edition": "explicit edition",
    "dataset_revision": "immutable revision",
    "task_ids": ["explicit manifest"],
    "artifact_hashes": {},
    "split_and_selection": "full / selected subset / filtering rule"
  },
  "system": {
    "model_snapshot": "provider version",
    "endpoint": "provider and serving route",
    "harness_revision": "immutable revision",
    "prompts_and_adapters": "versioned files",
    "tool_and_environment_config": "versioned files",
    "initial_state_and_reset": "explicit procedure",
    "context_policy": "input/output truncation, sampling, history"
  },
  "execution": {
    "attempts_per_task": 1,
    "selection_policy": "none",
    "budgets": {},
    "retry_and_finish_policy": "explicit",
    "run_ids": ["unique identifiers"]
  },
  "measurement": {
    "success_event": "exact event definition",
    "scorer_revision": "immutable revision",
    "judge_snapshot_and_prompt": "if applicable",
    "failure_policy": "missing / parse / infrastructure / judge",
    "aggregation": "weights, thresholds, tie rules",
    "uncertainty_unit": "task / seed / user / group"
  },
  "evidence": {
    "overall_depth": "D0-D4",
    "component_depths": [],
    "executed_scope": "what actually ran",
    "unverified_scope": "what remains unknown"
  }
}
```

不是所有字段都要铺在摘要里，但结果文件应能恢复它们。特别避免只保存一个目录名或一个会被覆盖的 run_config。

## 6. 如何做最小而有用的对照实验

先写清要回答的问题，例如“额外联网是否改善这批当前检索任务”，而不是“哪个模型最聪明”。

1. 选一个与需求相关、成本可承受的任务分层。
2. 固定 task IDs、输入与 scorer。
3. 一次只改变一个关键条件；若同时换模型和 native context 保留机制，应报告为系统比较，不能归因于单个因素。
4. 保存每题配对结果和失败类型，不只汇总平均。
5. 检查差值是否被 parser、缓存、重复行或缺失处理造成。
6. 资源允许时做重复运行，区分题目差异与随机采样方差。
7. 用少量人工审核检查自动分数与目标是否一致。
8. 只把有证据支持的结论迁移到部署。

无需为了凑 D4 而运行昂贵完整 benchmark。一个能排除关键错误解释的局部实验，常常比没有版本记录的大规模跑分更有效。

## 7. 按学习目标使用这份知识库

- **L0 认识**：知道各类测量对象与分数名称，不把 static QA、agent、偏好和经济交付混为一谈。
- **L1 理解**：能口述一条真实 task 从输入到评分的链，解释一个失败与分母边界。
- **L2 实践**：能复跑一个已附的离线组件实验，改变合成输入并预测结果；不需要调用模型 API。
- **L3 工程**：能固定完整实验契约，处理状态、并发、缓存、异常、产物验证和版本回归。

L 层级不是 D 层级。会解释 D3 源码不等于已有可用生产工程；亲自运行一个 D4 小探针也不等于掌握整个评测领域。

## 阅读顺序

先读 [多维 taxonomy](multidimensional-taxonomy.md) 和 [任务选择指南](benchmark-selection-guide.md)，再从上表选两个测量机制不同的案例。用同一份契约模板对比它们，最后阅读各自原始源码与实验脚本。此顺序比逐个记榜单数字更能建立可迁移的方法。

