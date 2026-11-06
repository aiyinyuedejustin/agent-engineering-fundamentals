# SciCode：科学计算、逐步代码依赖与计分分母

研究日期：2026-11-06。**D3：固定源码、真实问题记录、提示构造、生成和验收主路径已读。**附带 D4 仅针对合成元数据的计分/缓存分支；未执行候选科学代码、未读取完整数值目标 HDF5、未运行模型或完整 benchmark。

## 研究对象

- 仓库：`scicode-bench/SciCode`，提交 `e3158ea011d4235245a547460d3688d7ccbf9900`，2025-10-07。
- 推荐入口：`eval/inspect_ai/scicode.py`；README 把旧的两阶段脚本标记为 deprecated。本案例分别标注，不把旧实现当当前推荐路径。
- 真实记录：固定仓库 `tests/test_data/first_problem.jsonl` 中 problem 77，Berendsen thermostat/barostat 分子动力学任务。记录含 12 个相互依赖步骤，已读完整结构、第一步和最后一步测试逻辑；未在此再分发题目或答案。
- 数据集划分：官方 Inspect 文档的 validation 15 个主问题、test 65 个主问题。当前运行入口从 Hugging Face 读取，未传 dataset revision；固定仓库内的任务 fixture 与 live HF 数据不是自动同一版本。

[固定仓库](https://github.com/scicode-bench/SciCode/tree/e3158ea011d4235245a547460d3688d7ccbf9900) · [实际任务 fixture](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/tests/test_data/first_problem.jsonl) · [Inspect 使用说明](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/eval/inspect_ai/README.md)

## 1. 为什么它不是另一份 HumanEval

问题 77 从周期性边界与最小镜像距离，推进到相互作用势、力、温度、压力，最后组合成带温压控制的积分流程。它要求把科学关系转成能协作的函数，而不是孤立地完成短函数。

所读测试包括两类证据：

- 基础步骤把函数结果与外置数值目标比较，使用 `np.allclose` 等判断。
- 最后步骤构造固定随机种子的模拟流程，检查温度与压力统计量是否满足规定的偏差条件。它检查科学行为，而不只是代码是否能导入。

但也不应反向夸大：有限输入、有限轨迹与指定容差不能证明整个科学实现正确。运行环境、浮点库、随机数和测试时间限制都是结果条件。

官方 FAQ 也区分数值测试与领域约束，并解释专家验证分工；其中跨领域审阅主要检查题目与背景的清晰度，不是独立完成全部科研复现。本文不把“科学家验证”简写成全体科学家重复运行并通过了所有解法。

[任务 fixture](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/tests/test_data/first_problem.jsonl) · [FAQ](https://scicode-bench.github.io/faq/)

## 2. 实际调用链

`hf_dataset → record_to_sample → scicode_solver → prepare_final_prompt_with_steps → generate → register_previous_response → scicode_scorer → ScicodeEvaluator.test_code → subprocess → 汇总`

关键条件：

1. 每个子步骤都收到此前步骤的说明和模型生成代码。此前的错误可以向后传播，这与“每步都给金标准前置函数”的条件不同。
2. `with_background=False` 不是完全不谈背景：默认模板要求模型自己写相关科学背景；True 则把专家提供的背景加入提示。两者测量的知识回忆负担不同。
3. 解析器取代码围栏并删除 import 行，保存时统一加上允许的 dependencies 和之前的代码。被执行的程序不是模型原始文本的逐字复制。
4. 生成异常被 catch 后替换成 dummy 回复，继续后续步骤。这会把一部分生成服务失败转换成待测代码结果；读取报表时仍应另记基础设施错误。
5. 每一步的测试脚本加载该 step 的 HDF5 targets，并拼接记录中的断言。缺失文件、数值目标版本或依赖环境都可能让复现不成立。

[推荐入口](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/eval/inspect_ai/scicode.py) · [代码提取](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/src/scicode/gen/models.py) · [HDF5 加载](https://github.com/scicode-bench/SciCode/blob/e3158ea011d4235245a547460d3688d7ccbf9900/src/scicode/parse/parse.py)

## 3. 两个 metric 与一个给定上下文边界

推荐 evaluator 的主问题指标要求 `total_correct == total_steps`。子问题指标把所有主问题的正确步骤数相加，再除以所有步骤数，是步骤级 micro average，不是主问题正确率，也不是每个主问题子步骤比例的等权平均。

源码为控制自由度，跳过 13.6、62.1、76.3 的生成和执行，并在后续提示中读入仓库给定代码。FAQ 解释给定上下文的目的，但网页把最后一项写成 76.2；固定实现与实际文件名是 **76.3**，本案例依代码而不悄悄合并这个差异。

**局部可复现问题：**该 Inspect evaluator 在跳过这些步骤后，仍令 `total_steps = len(sub_steps)`。给定步骤不增加 `total_correct`，却留在分母和主问题全对判定中。

为了只验证此分支，实验构造合成元数据和已缓存的 pass 日志，提取原始 `ScicodeEvaluator` 类执行。`subprocess.run` 被替换成一旦调用就报错的 trap。没有运行模型输出，也没有读取 HDF5。

| 合成条件 | 所有实际计分步骤均为 cached pass | 返回正确步骤/总步骤 | 主问题正确 |
|---|---|---:|---:|
| 普通 ID 77，列出 2 步 | 是 | 2/2 | 1 |
| ID 13，列出 7 步，跳过第 6 步 | 是 | 6/7 | 0 |
| ID 62，列出 2 步，跳过第 1 步 | 是 | 1/2 | 0 |
| ID 76，列出 4 步，跳过第 3 步 | 是 | 3/4 | 0 |

这些**合成步骤数不是对真实 13/62/76 题目长度的声明**。实验验证的是该函数的列表/跳过契约。若真实传入记录包含对应被跳过步骤，便存在分母与已执行步骤不一致的问题；这不证明某篇论文或排行榜确实使用了该提交、该记录和该运行方式。

[探针脚本](scicode_skip_probe.py) · [实际输出与源码哈希](scicode-skip-probe-output.json)

## 4. 缓存与执行边界同样重要

- 已有每步日志时，evaluator 读取第一行 pass/fail 并跳过再次执行。日志路径包含模型名、background 设置和 step ID，没有代码、数据、环境或 evaluator 哈希。更改生成代码后复用相同输出目录，不能默认获得新测试结果。
- 旧 deprecated runner 按目录中存在的文件计 `tot_prob`，不是按数据集应有步骤数；缺失步骤与上面的 Inspect 分母问题是不同风险，不能混写。
- 推荐入口虽然使用 Inspect，却在 scorer 内直接 `subprocess.run(['python', script_path], timeout=1800)`；这里的 Task 没有配置 sandbox。**接入评估框架不等于此实现已经采用其隔离环境。**

复现实验应另建独立输出目录、记录任务与 HDF5 哈希、冻结依赖和 Python、明确给定上下文步骤的分母语义，并在适合执行不可信代码的环境内运行。这里是建议，不是本次已完成这些设置。

## 5. 仍未验证的部分

未下载 HDF5 数值目标，未确认当前 HF 所有记录与仓库 fixture 一致，未运行真正科学测试，也未评估模型能力。对这些范围，D4 仍是空缺；本次局部实验只支持计分 bookkeeping 结论。整个 benchmark 不应标为“已复现”。
