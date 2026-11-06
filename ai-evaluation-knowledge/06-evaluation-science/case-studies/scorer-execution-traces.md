# 四个评分器的源码执行链与实际诊断

固定版本与 SHA 见 [source_manifest.json](../experiments/source_manifest.json)，实际函数范围、输入与输出见 [scorer_diagnostics.json](../experiments/results/scorer_diagnostics.json)。以下 D4 均是**合成输入的评分函数实验**，不是模型跑分。

## 1. HumanEval：从样本通过记录到 pass@k

固定提交：`b9453e8f1865df0a0057a1383767caa400acfbcf`。

### D3 执行链

1. `evaluate_functional_correctness` 读取题目和逐样本 completion。
2. 每个 completion 经 `check_correctness` 返回 task_id、completion_id、passed 和 result。
3. 按任务收集、按 completion_id 排序，分别统计 n 与 c。
4. 对满足所有任务 n≥k 的 k，调用 `estimate_pass_at_k`。
5. 逐题估计值求均值，并保存逐样本结果。

真正执行候选代码的路径会把 prompt、completion、test 与 `check(entry_point)` 拼接，放入子进程执行并控制超时。本次没有进入该路径，且该仓库的防护函数不等于安全沙箱。[evaluation.py](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/human_eval/evaluation.py)、[execution.py](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/human_eval/execution.py)

### D4：官方 L13–36 的估计函数

| n | c | k | 官方 pass@k | 朴素 `1−(1−c/n)^k` |
|---:|---:|---:|---:|---:|
| 10 | 1 | 5 | 0.50000 | 0.40951 |
| 10 | 2 | 5 | 0.77778 | 0.67232 |
| 4 | 1 | 4 | 1.00000 | 0.68359 |

组合数恒等式与官方实现对全部六个测试输入一致。最后一行是在已观察四个样本中选全部四个，已知其中一个通过；它不能解释为无限未来重采样必然成功。

**使用教训：**不要把不同 k、不同采样温度、不同尝试预算或不同选择器的成绩当同一个指标。

## 2. SQuAD：归一化规则决定“相同”

固定提交：`eee5fdbf62f8613a7812b03419e6b29617b74fd1`。

### D3 执行链

`get_raw_scores` → 过滤空归一化参考答案 → 每条参考答案的 exact/F1 → 取最大值 → no-answer threshold → 按分母汇总。

`normalize_answer` 按顺序小写、删除 ASCII 标点、删除英文冠词、规范空白。F1 使用 Counter 交集，允许重复 token，空答案特殊处理。多参考答案是取最高分，不是均值。[源码 L45–126](https://github.com/rajpurkar/SQuAD-explorer/blob/eee5fdbf62f8613a7812b03419e6b29617b74fd1/evaluate-v2.0.py#L45-L126)

### D4 边界

- `0.5` 和 `05` 都变成 `05`，exact=1。
- `not guilty` 和 `guilty`，exact=0、F1=2/3。
- 空字符串和 `the` 都变成空，exact=1。
- `twenty one` 和 `21`，exact=0。
- no-answer probability=0.5 时，threshold=0.49 会触发无答案；threshold=0.5 不触发，因为代码使用严格大于。

**不夸大问题：**这些是诊断函数边界的构造例子，不是从真实 SQuAD 项中统计的错误率。原任务的抽取式问答设计解释了部分归一化选择。把它用于数值/法律/中文任务前需重新验证。

**缺失预测的范围：**`get_raw_scores` 会输出提醒并跳过缺失 ID；但完整 main 后续按 HasAns/NoAns ID 列表索引时可能触发 KeyError。因此不能只看子函数就声称整份官方脚本会默默缩小分母并成功输出。

## 3. FastChat：自然语言判决、解析和汇总是三层

固定提交：`587d5cfa1609a43d192cedb8441cac3c17db105d`。

### D3 执行链

- `run_judge_pair` 填充问题与答案，取得判决文本，按 output_format 解析 winner。
- `play_a_match_pair` 交换答案再调用一次，把 A/B 映射回 model_1/model_2。
- `show_result.py` 排除 error 行；不一致的双向结果计 tie；adjusted win rate 给 tie 0.5 分。
- single-answer 路径解析数值，未解析时使用 -1，展示时将 -1 行排除。

这意味着 prompt、模型返回文本、parser、错误行策略和 tie 规则都影响最终分数。[common.py](https://github.com/lm-sys/FastChat/blob/587d5cfa1609a43d192cedb8441cac3c17db105d/fastchat/llm_judge/common.py)、[show_result.py](https://github.com/lm-sys/FastChat/blob/587d5cfa1609a43d192cedb8441cac3c17db105d/fastchat/llm_judge/show_result.py)

### D4：将 API 调用替换为固定文本

| 人工提供的 judge 文本 | 实际 parser 结果 | 原因 |
|---|---|---|
| `The winner is [[B]].` | B | 命中 B |
| `I considered [[A]] but my final verdict is [[B]].` | A | 先检查 A 是否出现在文本任意位置 |
| `No decision.` | error | 没有合法标签 |
| `[[C]]` | tie | C 表示平局 |
| `[[11]]` | 11 | 数值解析函数本身没有 1–10 区间约束 |
| `Analysis [3], final rating [8]` | 3 | 备用正则取第一个匹配 |

**结论范围：**没有测真实 judge 多常产生这些文本。结果仅证明固定解析器在这些输入下的实际行为。更稳健的方案是单一结构化 verdict、唯一性检查、范围检查，以及将解析失败作为显式结果报告。

## 4. SWE-bench：先证明运行有效，再解释测试状态

固定提交：`02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`。

### D3 执行链

`get_eval_report` → `get_logs_eval` → `get_eval_tests_report` → `get_resolution_status` → resolved 布尔值。

- 日志层检查 patch/reset/error/timeout 标记、测试输出边界、解析结果、测试确实运行的迹象和命令退出码。
- 状态层把 FAIL_TO_PASS 与 PASS_TO_PASS 分开处理，并按 eval_type 使用不同日志契约。
- FULL 需要所有要求的修复和回归维护条件成立。

[固定 grading.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py)、[固定常量](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/constants/__init__.py)

### D4-A：PASS_AND_FAIL 状态

| 情况 | verdict |
|---|---|
| 修复测试与回归测试均 PASSED | FULL |
| 修复测试 SKIPPED，回归 PASSED | NO |
| 修复 PASSED，回归 SKIPPED | FULL |
| 修复 XFAIL，回归 PASSED | FULL |
| 缺失修复测试记录 | NO |

这里的 XFAIL 与 skipped 规则是**这个固定版本的实现契约**，不应推广成所有 benchmark 的“通过”定义。要解释它是否合理，还需要看相应测试框架、预期失败和数据集生成方式。

### D4-B：FAIL_ONLY 不能脱离上游日志检查

该模式只记录失败，所以状态函数把没有记录为 FAILED 的预期项视为成功。我们直接调用该子函数时，空状态表可返回 FULL；但完整执行链有运行有效性门槛，不能由此推断“测试没跑也会成功”。

使用同一个官方 `get_logs_eval`，只替换具体项目 parser：

| 合成日志 | 有效？ |
|---|---|
| 无测试输出记录 | 否 |
| `Executed 0 of 0` | 否 |
| `1 passing`，退出码 0 | 是 |
| parser 给出 PASSED，但命令退出码 1 | 否 |
| parser 给出 PASSED，命令退出码 0 | 是 |

这个测试验证了日志门槛分支，不等于验证所有真实项目 parser 或所有日志伪造方式。

### D4-C：截断参数化 test ID

官方 `_resolve_case` 先精确匹配；仅当预期 ID 的 `[` 数量多于 `]` 时才尝试前缀回退，而且候选必须在 pass/fail 分类上相同。

- 两候选 PASSED/XFAIL：可匹配为通过。
- 一候选 PASSED、一候选 FAILED：拒绝回退。
- 完整普通 ID：不做任意前缀匹配。

**使用教训：**判决依赖测试标识的清洗和映射。升级 harness 或修正数据 ID，可能改变分数，即使模型输出完全不变。

## 5. 这批实验能支持什么

可以支持：特定 commit 的评分行为、具体分支的可执行解释、为什么需要 parser/日志/分母审计。

不能支持：真实模型的排行榜、真实数据中缺陷的频率、整个评测框架已安全、或相关 benchmark 应完全弃用。要到后者，需要更完整的数据抽样、端到端复现和部署目的判断。
