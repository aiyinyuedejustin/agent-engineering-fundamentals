# HealthBench：带负权重的 rubric 与 Professional 协议边界

研究日期：2026-11-06。**Professional 整体 D2**：已读官方报告、实际公开记录和相关参考代码；生产 evaluator 未公开，不能宣称已追踪它的全部执行链。旧 HealthBench 在本次只作为已读参考实现，未另读取原版真实题目。附带 **局部 D4** 是纯合成计分实验，绝非医疗能力评估或模型复现。

## 1. 先区分四个对象

- HealthBench 原版、Hard、Consensus 是不同数据配置，不能只写“HealthBench 分数”。
- **HealthBench Professional** 于 2026-04-22 发布，关注临床咨询、写作/文档、医学研究三类专业聊天任务，公开数据共 525 条。
- **公开数据集**与**公开参考评分器**是不同产物。Professional 数据卡明确说论文成绩来自内部 evaluator，未发布官方外部实现；simple-evals 是可供研究者使用的非官方外部参考。
- 医生撰写的参考回复是 baseline，不是可以不经 rubric 判定就视为满分的唯一答案。

Professional 的构造包含困难样本富集与红队样本，不是未经选择的普通临床流量；发布说明给出的困难样本富集约为 3.5 倍，约三分之一来源于红队。这限制了把 benchmark 分数直接解释成部署错误率的方式。

[发布说明](https://openai.com/index/making-chatgpt-better-for-clinicians/) · [Professional 数据卡](https://huggingface.co/datasets/openai/healthbench-professional) · [论文](https://cdn.openai.com/dd128428-0184-4e25-b155-3a7686c7d744/HealthBench-Professional.pdf)

## 2. 实际记录与输入 schema

代码固定在 simple-evals `652c89d0ca9df547706735883097e9537d40dc47`。Professional 数据仓库查询时的 HEAD 为 `349962fd46dd02343a0d8a606491baf59154ea1a`，最后修改 2026-04-22。通过 rows API 读到一条完整实际记录，响应声明 total=525、无截断；该 viewer 请求本身未固定 revision，因此 HEAD 记录不等于独立完成数据字节一致性验证。

该记录确认的结构是：

- `conversation.messages`：消息列表，而不是直接把 conversation 当列表。
- `rubric_items`：每项含 `criterion_text` 和 `points`。
- 另外包含 `id`、use_case、type、difficulty、specialty、physician_response。

参考 `HealthBenchEval` 读取的却是原版 schema：`prompt`、`rubrics`（criterion/points/tags）、`example_tags` 和 `prompt_id`。**Professional CLI 选项不会自动把公开 Professional schema 转成这个格式。**外部运行需要显式转换并校验，不能仅把原始 JSONL 路径换进去就称为已复现。

遵循数据集的防污染请求，本文不再发布实际问题、rubric 文本、医生回复或它们的截图。字段结构与评分分析足以说明协议问题。

[实际记录来源](https://datasets-server.huggingface.co/rows?dataset=openai%2Fhealthbench-professional&config=default&split=test&offset=0&length=1) · [数据仓库元数据](https://huggingface.co/api/datasets/openai/healthbench-professional) · [固定参考 evaluator](https://github.com/openai/simple-evals/blob/652c89d0ca9df547706735883097e9537d40dc47/healthbench_eval.py)

## 3. 判分不是“答对几个医学问题”

参考实现给每个 rubric 单独构造 grader 请求。grader 返回的是该项条件是否满足，不是“回答是否好”。负权重 rubric 描述不希望出现的行为，因此满足它应扣分，而不是把标签反过来。

`calculate_score` 的分母只包含正分项；分子包含全部已满足项的正分和负分。单例可以为负。只有负分项的某个 tag 没有正分分母时返回 None，后续不汇总该 tag。**缺少该 tag 的数值不等于该风险完全不存在。**

解析器要求 `criteria_met` 真的是 JSON boolean，字符串形式不算合格。该参考 grader 的坏 JSON 重试使用无显式次数上限的循环；批量运行应另控制 judge 请求失败与费用，而不是假定每个 rubric 恰好调用一次。

总体聚合先求样本均值，再截断到 [0,1]，不是先把每个负分样本改成零。这一顺序会影响结果。

## 4. Length adjustment 的单位与输出字段

Professional 论文的主要指标使用最终回复**字符数**，不含思考 token：以 2,000 字符为中心，每多 500 字符扣原始分数 0.0147，短回复得到对称调整，然后对样本均值截断。系数来自特定 verbosity 实验，不能随意把它当所有任务、语言和回复长度的普适效用函数。

公开参考 helper 支持这个算式，但参数需要显式提供。`--healthbench-professional-mode` 主要检查自定义输入路径、GPT-5.4 low grader 和两个长度参数齐全；它既不填入论文系数，也不证明内部 harness 已被复制。

另一个容易误读的地方：参考实现的 `result.score` 仍从 **未调整** overall_score 汇总而来。长度调整结果保存在独立 metric `overall_score_length_adjusted`；CLI 通用汇总继续取 `score`。要对齐论文主指标，应明确取哪个字段，不能因为开了开关就把通用 score 当成调整后结果。

[CLI 参数与汇总](https://github.com/openai/simple-evals/blob/652c89d0ca9df547706735883097e9537d40dc47/simple_evals.py) · [论文 §4](https://cdn.openai.com/dd128428-0184-4e25-b155-3a7686c7d744/HealthBench-Professional.pdf)

## 5. 本次局部实验

AST 提取原始 RubricItem、算分、长度调整和聚合定义，仅输入合成标记与占位字符串；没有调用 grader、模型或任何临床工具。

| 实验 | 实际输出 |
|---|---|
| 正项 +2 与负项 −3 均满足 | 单例 −0.5 |
| tag 只有负项 | None |
| 单例分数 −0.5、1，按实现先均值后截断 | 0.25；逐例截断再均值会是 0.5 |
| 原始 0.8，长度 1,500 / 2,000 / 2,500，论文长度参数 | 0.8147 / 0.8 / 0.7853 |
| 一条 2,500 字符样本的聚合字段 | score=0.8；overall_score_length_adjusted=0.7853 |

[探针脚本](healthbench_score_probe.py) · [实际输出及源哈希](healthbench-score-probe-output.json)

这些结果确认参考实现的语义，**不指控论文使用了错误字段，也不说明任何模型的临床表现。**

## 6. 重复采样和不确定性也有协议版本

Professional 论文主比较采用每例 8 个样本，先在例内平均，再做配对比较和区间估计；对多重比较使用 Holm 校正。公开参考 `n_repeats` 则重复数据行，通用聚合对收到的结果列表直接 bootstrap，没有在这个函数内按 prompt_id 分组。两条流程不可默认给出相同误差条。

如果要开始真正复现，应先完成 schema 转换、逐例 ID/标签保存、数据哈希、grader snapshot、长度参数/字段、重复样本分组和失败策略校验；之后再考虑模型、harness、工具权限与临床验证。聊天 benchmark 不能替代前瞻性临床评价、专业审阅或医疗决策所需的验证。
