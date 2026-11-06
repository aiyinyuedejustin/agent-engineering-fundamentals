# gpt-oss 评测组件微实验

## 范围与结论边界

这不是 gpt-oss 模型推理，也不是 GPQA、AIME 或 HealthBench 分数复现。我们固定官方仓库 commit，读完实际任务、配置与关键代码，并沿入口、数据读取、sampler、答案抽取、打分和汇总追踪执行路径。随后只对组件运行 27 个离线探针。模型和 judge 调用均为 0；实验过程中没有网络调用。

- 代码路径理解：D3 / L2。
- 实际运行的解析器、构造函数、空集合与统计组件探针：局部 D4。
- 模型报告分数仍是 D1，不能因这个实验升级为 D4。
- 不据此推断发布分数受到多大影响。探针是合成边界案例，不代表真实模型输出频率。

固定版本：[`openai/gpt-oss@277020131d524f06bed5f66b694a92ed7f6e5224`](https://github.com/openai/gpt-oss/commit/277020131d524f06bed5f66b694a92ed7f6e5224)，commit 时间 2026-10-29，读取日 2026-11-06。这是晚于 2025-08 模型卡的代码版本，不声称与发布时配置相同。

## 可重复方法

1. 阅读 `source-manifest.json` 的固定 commit、9 个文件 URL、Git blob SHA 和 SHA-256。
2. 可运行 `python fetch_inputs.py /tmp/gpt-oss-probe-inputs` 获取原始输入。该辅助脚本只下载和校验，不执行下载的模块。它是供复验的准备脚本，本次研究使用 GitHub 连接器取回相同文件并校验 Git blob SHA，没有运行这个下载脚本。
3. 安装或使用已有 Python 3.10+ 与 NumPy。记录的实测环境为 Python 3.12.14、NumPy 2.3.5。
4. 运行 `python probe.py --source-dir /tmp/gpt-oss-probe-inputs --output results.json`。

`probe.py` 通过 AST 选取原始函数、类和正则表达式，函数体不改动。数据加载器被三条合成记录替代，避免下载 benchmark、调用 API 或产生费用；类型注解推迟求值，以免引入不相关依赖。没有执行完整 CLI、模型 sampler、真实数据评分或部署环境。所有输入文件在执行前必须匹配 Git blob SHA。

## 27 个探针的主要观察

完整逐项输入与输出见 `results.json`。下面是实际观察，不是尚待验证的代码猜测。

1. **GPQA 抽取不是“取最后最终答案”。** 输入先写 `Answer: A`、后改为 `Answer: B`，返回 A。先写 `Answer: A`、后写 boxed B，也返回 A。规则优先级以及每条规则的首次匹配决定结果。
2. **GPQA 的兜底并不总返回 A–D 或 None。** `Because I cannot decide.` 返回 B，`Dunno` 返回 D，`no answer` 返回小写 n，空串返回空串。只有抽取字符恰好等于正确选项才会得分，但模糊输出可能被当作有效选项。不能只依据函数 docstring 判断行为。
3. **AIME 解析是浅层正则与整数转换。** 没有 boxed 答案的 `No answer. Tried 3 cases.` 被抽成 3；nested boxed text 42 抽取后无法转成整数。逗号分组 boxed 1,234 变成 234。AIME 正常答案范围只有 0–999，因此最后一例是解析边界探针，不是声称数据集存在四位答案。
4. **零样本并非空评测。** 三条合成样本、8 次重复时，`num_examples=None` 与 `num_examples=0` 都生成 24 个实例。`num_examples=1,n_repeats=8` 会断言失败；重复数为 1 时才生成一个样本。这同时发生于 AIME 和非 debug 的 GPQA 构造函数。
5. **GPQA debug 特判覆盖样本数意图。** 固定版本会筛选包含特定 ESPRESSO 字符串的题目；合成数据中无论 num_examples 设为 0、1、10，都保留唯一匹配行。它不是通用的随机小样本开关。
6. **空任务集合可能先在并发层失败。** 原始 `map_with_progress` 对空列表创建 0 线程的 ThreadPool，抛出 ValueError。
7. **标准差不等于标准误。** report 的 std 对 0、1、0、1 返回 0.5，是 NumPy 默认总体标准差，不是均值标准误或置信区间。
8. **HealthBench 的截断时点改变结果。** 合成 rubric 得到单例原始分数 −2 和 1，官方函数先平均、后截到 [0,1]，结果 0；逐例先截断再平均则为 0.5。两者不是同一指标。实验使用虚构 rubric，不涉及真实患者。

## D3 执行路径与运行前检查

### 入口与真实任务

[`__main__.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/__main__.py) 默认遍历 2 个模型、3 个 reasoning effort、5 个 eval，合计 30 个模型配置与任务组合。GPQA 和 AIME 的 CLI 配置各重复 8 次；类构造函数自身的默认值不能替代入口实际传入值。默认 n_threads 为 1584，max_tokens 为 131072。

入口把 HealthBench judge 固定为 `gpt-4.1-2025-04-14`，地址为 OpenAI API；因此“被测模型跑在 localhost”不意味着整条评测无外部 API 或免费。入口在选择任务前创建 judge client，初始化是否需要凭据依赖 SDK 环境，本实验没有测试。

### GPQA

[`gpqa_eval.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/gpqa_eval.py) 从公开 CSV 读取 diamond 数据，固定 RNG 0，重复实例后为每个实例重新排列选项。提示要求 A/B/C/D。调用 sampler 后，`abcd_grader.extract_abcd` 决定抽取值，与正确字母作精确比较；每条结果是 0 或 1。`report.aggregate_results` 平均所有实例，不做多数投票。

### AIME

[`aime_eval.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/aime_eval.py) 从 Hugging Face `raw/main` 读取 AIME2025 I、II 两个 JSONL。固定代码 commit 并不固定数据 revision。提示要求 boxed 答案，优先取最后一个可匹配 boxed/framebox，找不到时取最后一个数字片段；转换为整数后精确比较，再平均重复实例。

### Sampler

[`responses_sampler.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/responses_sampler.py) 和 [`chat_completions_sampler.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/chat_completions_sampler.py) 请求超时为 24 小时。BadRequest 转为可继续评分的空/占位响应，其他异常指数退避重试，没有有限的尝试上限。Chat Completions 对空 content 重试。Responses 直接使用 output_text。未验证服务端是否按预期应用 reasoning budget、Harmony 格式或 token 上限。

### HealthBench

[`healthbench_eval.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/healthbench_eval.py) 按 full/hard/consensus 读取带日期文件名的数据。每个 rubric item 单独请求 judge，JSON 必须含布尔 criteria_met，否则持续重试。分子包括满足的负分项，分母仅正分项；先计算每例分数，再在数据集/标签聚合层截断均值。bootstrap_std 使用 1000 次重采样。我们只实测 rubric 算术和截断顺序，未运行 judge。

### 输出与可追踪性

[`report.py`](https://github.com/openai/gpt-oss/blob/277020131d524f06bed5f66b694a92ed7f6e5224/gpt_oss/evals/report.py) 默认输出 mean/std；并发使用 unordered 映射，记录顺序不保证与输入相同。CLI 写 HTML、指标 JSON 和 allresults JSON，但未自动写本研究要求的完整 commit、数据 hash、依赖锁、硬件、预算和错误分类。正式复现应补 manifest，而不是只保存最终分数。

## 尚未完成

没有加载模型权重、下载正式 benchmark 数据、跑 GPU 推理、调用外部 judge、估计上述边界在真实输出中的发生率，或对模型卡成绩做数值重现。没有向上游提交 issue 或修改其仓库。已有 issue #294 的搜索结果涉及零样本行为，但本文件的结论基于固定源码与本地探针，不依赖该 issue 为真。
