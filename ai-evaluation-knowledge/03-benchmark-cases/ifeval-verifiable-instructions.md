# IFEval：可验证约束、计分单位与 loose 的准确含义

更新日期：2026-11-06。代码与任务追踪为 **D3**；另做了一次隔离的评分组件微实验，属于 **组件 D4**，不是模型评测或完整 benchmark 复现。

## 研究对象与证据

固定 `google-research/google-research` 提交 `e6890f85757dd84e27ca6df2dd30651dafad28e0`，该目录最后一次相关提交日期为 2026-07-22。已读 `evaluation_main.py`、`evaluation_lib.py`、`instructions_registry.py`、相关 checker 类，以及完整输入 JSONL 的结构。该文件包含 541 条输入。

[固定目录](https://github.com/google-research/google-research/tree/e6890f85757dd84e27ca6df2dd30651dafad28e0/instruction_following_eval) · [真实输入数据](https://github.com/google-research/google-research/blob/e6890f85757dd84e27ca6df2dd30651dafad28e0/instruction_following_eval/data/input_data.jsonl)

## 1. 原始用户请求与真正被评分的内容并不相同

真实输入 `key=1001` 要求一种文体的日本旅行行程，同时禁用逗号。它的 `instruction_id_list` 只有 `punctuation:no_comma`。因此这一条的自动判定并不验证旅行建议质量、事实准确性或文体是否合适。

`key=1000` 则组合了禁逗号、突出显示的小节数量、最低字数等多个可检查约束。任务文本中提到某个网页，不意味着该 evaluator 会联网读取网页、核对摘要或评估浏览能力。

这不是说题目毫无价值，而是划定 construct：IFEval 的自动分数反映所注册、可机械验证的指令约束，不能直接解释为“完整用户需求满足率”。本文不复制完整测试题或回答。

## 2. 输入、运行与结果契约

1. 输入 JSONL 提供 `key`、`prompt`、指令 ID 列表和逐指令参数。
2. 模型生成阶段在该评分入口之外。评测脚本读取另一个已有的 prompt/response JSONL。
3. response 按 prompt 字符串映射，而不是按 key 关联。缺失的 prompt 会导致查找失败；重复 prompt 会覆盖此前条目。使用改写或截断后的 prompt 作为 join key 也可能错位。
4. 对每个 instruction ID，从 registry 创建相应 checker，用 kwargs 构建规则，检查 response。
5. 保存每条 instruction 的布尔结果及它们的逻辑 AND，并同时报告 prompt-level 和 instruction-level 成绩。

例如一条有三个约束，两个通过，则 instruction-level 对应部分为 2/3，而该 prompt 仍失败。样本拥有的约束数量不同，这两个统计量的权重也不同，不能只标注一个含糊的“IFEval accuracy”。

[评分入口](https://github.com/google-research/google-research/blob/e6890f85757dd84e27ca6df2dd30651dafad28e0/instruction_following_eval/evaluation_main.py) · [评分与聚合](https://github.com/google-research/google-research/blob/e6890f85757dd84e27ca6df2dd30651dafad28e0/instruction_following_eval/evaluation_lib.py) · [规则注册表](https://github.com/google-research/google-research/blob/e6890f85757dd84e27ca6df2dd30651dafad28e0/instruction_following_eval/instructions_registry.py)

## 3. strict 与 loose 不只是同一个分数的四舍五入

strict 检查原始非空回答。loose 生成多个候选：原文、移除星号、移除首行、尾行或两端，以及这些操作的组合。**每条 instruction 可以分别选择一个能通过的候选，然后再对所有 instruction 的结果做 AND。**

所以 loose 的逻辑是“每条约束各自存在一个可通过的候选”，不是“存在同一个候选满足全部约束”。前者比后者宽松。源码把 loose 描述为上界式检查；该区别本身不等于实现错误，但如果把它解读为某一份共同规范化后的回答完全合规，就会过度解释。

## 4. 原创最小实验

使用合成请求：包含关键词 HEADER，同时不含逗号。合成回答的首行含 HEADER 和逗号，中间为无逗号短文本，末行也含逗号。

- strict：关键词通过，禁逗号失败，整体失败。
- loose：关键词从原文通过，禁逗号从去除首尾后的候选通过，整体通过。
- 枚举所有候选：没有一个候选同时通过两条约束。

实验直接从两个固定上游文件的 AST 提取相关类和函数，没有改写 checker 算法；未联网、未调用模型、未使用官方测试集作调优。本地运行输出及 SHA-256 随附。它只确认该逻辑在所构造输入上的行为，不估计该现象在真实模型响应上的频率或排名影响。

- [实验程序](ifeval_loose_probe.py)
- [实验输出](ifeval-loose-probe-output.json)

复现时将固定版本的 `instructions.py` 与 `evaluation_lib.py` 保存到本地，再运行程序的 `--instructions` 和 `--evaluation-lib` 两个参数。完整上游源码未复制进本知识库。

## 5. 使用建议与下一步

- 四个基础口径应分别标注：strict/loose × prompt/instruction。
- 对产品任务另加内容正确性与实际效用，不把格式合规当作完整质量。
- 数据准备时检查 prompt 唯一性、样本覆盖和映射字段。
- 检查具体规则如何实现。例如当前 KeywordChecker 使用正则匹配；逗号规则只检查特定字符。自然语言词义与程序判定之间需要保持清晰界限。
- 若要评估该 loose 差异的实际影响，需要在固定模型输出集上额外比较“逐约束候选”和“共同候选”两种判定，并报告置信区间。此项尚未执行。
