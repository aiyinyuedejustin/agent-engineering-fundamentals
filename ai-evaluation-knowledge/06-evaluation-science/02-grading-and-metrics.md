# 评分器与指标：先定义正确，再计算分数

## 1. 评分器的选择顺序

| 任务 | 优先考虑 | 主要风险 |
|---|---|---|
| 标准答案、分类、选项 | 明确答案抽取 + 精确比较 | 字符串不同但语义相同，或过度归一化 |
| 数学表达式 | 受限语法解析 + 数值/符号等价检查 | 定义域、单位、近似误差、解析失败 |
| 代码生成 | 隔离环境中的测试、性质测试 | 测试覆盖不足、实现过拟合、环境噪声 |
| 工具/流程任务 | 最终状态 + 必要过程约束 | 状态对但过程违规，或参考轨迹过严 |
| 开放文本 | 分维度 rubric + 校准后的人工/模型判分 | judge 偏差、尺度不稳、遗漏关键事实 |

“能程序化”不等于“无需验证”。LiveBench 的论文明确讨论 regex 评分引入格式要求的风险，且说明更改解析规则后会重评所有模型。[附录 A.4–A.6](https://arxiv.org/html/2406.19314v2#A1.SS4)

## 2. Exact match、token F1 和语义正确不是一回事

SQuAD 2.0 官方脚本先小写、去 ASCII 标点、去英文冠词、折叠空白，再做 exact match。F1 基于 token 多重集合的交集，多个参考答案取最高分。[固定源码 L45–100](https://github.com/rajpurkar/SQuAD-explorer/blob/eee5fdbf62f8613a7812b03419e6b29617b74fd1/evaluate-v2.0.py#L45-L100)

本地实际运行发现：

- `The Eiffel Tower.` 与 `eiffel tower` 得 1，符合该任务的容错设计。
- `not guilty` 与 `guilty` 的 F1 是 2/3，但含义相反。
- `0.5` 与 `05` 被归一化成相同字符串，exact match 为 1。
- 空答案与 `the` 也被归一化成相同字符串。
- `twenty one` 与 `21` 的 exact match 为 0。

这些是人工构造的边界输入，用于说明不可把该评分器不加审计地搬到法律、数值或多语言任务；不是对 SQuAD 数据中错误发生率的估计。[实验原始结果](experiments/results/scorer_diagnostics.json)

## 3. pass@k 的正确含义

对每题生成 n 个样本，其中 c 个通过，HumanEval 使用：

`estimated pass@k = 1 − C(n−c, k) / C(n, k)`，要求 n ≥ k。

它估计的是从这一采样机制产生的 k 次尝试中至少一次成功的概率。原始实现逐题计算后求平均，并仅对所有题样本数都足够的 k 输出结果。[固定源码](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/human_eval/evaluation.py#L13-L36)

不能直接用 `1 − (1 − c/n)^k` 替代这个有限样本估计器。本地运行 n=10、c=2、k=5，官方值为 0.77778，朴素代入为 0.67232。二者估计方式不同；官方值也不是说这个模型今后任意五次必然有 77.778% 的成功率而没有估计不确定性。

还要区分：

- pass@1：一次随机尝试成功。
- pass@k：k 次里至少一次成功，需要有办法识别成功候选；测试集 oracle 选择不等于用户能选择。
- 所有 k 次都成功的可靠性：独立、同题成功率为 p 时为 p^k，与 `1−(1−p)^k` 方向相反。
- best-of-k：还包含选择器的能力和开销，不能自动等同 oracle pass@k。

逐题成功率不同，先取均值再做幂运算也不对。例如两题成功率 0.2 和 0.8，平均 pass@2 为 0.66，而把平均成功率 0.5 代进去会得到 0.75。[统计演示](experiments/results/statistical_diagnostics.json)

## 4. 汇总规则本身就是实验条件

- micro：按样本或事件加权，容易由大类主导。
- macro：按类别等权，容易让极小类别贡献过大。
- workload-weighted：按目标使用分布加权，权重来源必须公开。
- worst-group / tail：关注最差分组或高分位延迟，应和总分并列。
- conjunction：所有要求均满足才成功，适合某些流程任务，但应保留逐项失败信息。

相同每类分数，权重不同就可能改变胜负。[统计演示](experiments/statistical_diagnostics.py) 用两个系统在每类均相差 5 个百分点的例子，展示不同任务配比可以把较好的系统总分反转成 63% 对 82%。这是比较协议问题，不是模型能力变化。

## 5. 分母、无效样本和重试必须预先规定

至少区分：模型答错、拒答、超时、输出解析失败、工具失败、环境失败、任务本身失效。不要默默删掉失败项再算准确率。

三种不同口径应分别命名：

1. end-to-end success：所有分配任务都在分母中。
2. conditional success：只在环境有效/结果可解析的样本上计分。
3. coverage：被条件口径保留下来的比例。

FastChat 的展示脚本会排除单答评分 -1 和 pairwise 的 error 行。若模型之间错误率不同，保留下来的均值就不再是相同条件下的总体表现。因此报告均值同时必须报告解析成功率和被删行数。[固定 show_result.py](https://github.com/lm-sys/FastChat/blob/587d5cfa1609a43d192cedb8441cac3c17db105d/fastchat/llm_judge/show_result.py)

## 6. 测试评分的底线

必须区分“没有记录失败”和“确认测试运行且通过”。SWE-bench 的现行固定版本通过运行迹象、测试命令退出码、状态映射及 F2P/P2P 规则共同形成 verdict。[固定 grading.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py)

代码测试还需要真正的隔离环境。HumanEval 的 `reliability_guard` 明确不是安全沙箱，本次实验仅运行评分数学函数，不执行模型生成代码。[execution.py](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/human_eval/execution.py)
