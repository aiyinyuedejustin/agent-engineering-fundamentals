# MMLU-Pro：同一题库，不同提示、解析与重试政策

研究日期：2026-11-06。**D3，限定已读 local/API/APIX 路径**：读取真实 test 与 validation 记录、配置和关键源码，追踪生成与计分链。附带 **局部 D4** 只运行 parser/保存函数的合成实验，没有下载模型、调用 API 或重跑题库。

## 版本与实际任务证据

- 仓库提交：`f418b116db00b065c2aea046518d8fcf74d39872`，2026-03-18。
- HF 数据仓库查询时 HEAD：`b189ec765aa7ed75c8acfea42df31fdae71f97be`，2026-05-02。代码调用 `load_dataset` 未固定 revision；本次 rows viewer 请求也未固定 revision，不将不同日期的数据默认为同一快照。
- 完整读取 test 的 question_id 70 和 validation 的 question_id 0。前者有 **9 个**实际选项；后者有 10 个选项与 CoT 示例。公开接口报告 test 12,032 条、validation 70 条。
- 这说明“十选项基准”是总体设计描述，不代表每一行恰好十个有效选项。两条记录都含问题、选项、答案字母、答案索引、类别和来源字段；本文不再发布题干/答案。

[固定仓库](https://github.com/TIGER-AI-Lab/MMLU-Pro/tree/f418b116db00b065c2aea046518d8fcf74d39872) · [真实 test 记录](https://datasets-server.huggingface.co/rows?dataset=TIGER-Lab%2FMMLU-Pro&config=default&split=test&offset=0&length=1) · [真实 validation 记录](https://datasets-server.huggingface.co/rows?dataset=TIGER-Lab%2FMMLU-Pro&config=default&split=validation&offset=0&length=1) · [数据元信息](https://huggingface.co/api/datasets/TIGER-Lab/MMLU-Pro)

## 1. 从题库到模型输入的路径

local 路径为：`load_mmlu_pro → preprocess → 按类别选取 validation → generate_cot_prompt → batch_inference → extract_answer → save_res → 跨类别正确数/总数`。

- `preprocess` 去掉字面值为 N/A 的选项，提示按剩余选项重新编号。
- 默认 ntrain=5，但 local runner 会在提示超出预算时逐步减少示例。因此实际 few-shot 数未必相同，应该逐题记录，而不是只记命令行的 5。
- 固定 local 配置是最大模型上下文 4096、最多生成 2048 token、temperature=0、遇到 `Question:` 停止。API 路径根据供应商另设参数，不能仅凭同一题库声称预算一致。
- API 路径使用该类别所有 validation 示例；提示要求 CoT 后给出规定形式的字母答案。
- 最终总 accuracy 是汇总正确/错误数量，而不是 14 个类别的等权均值。

HF 仓库另有 `eval.yaml` 声明 Inspect 的 multiple_choice solver 与 choice scorer。该配置本身没有证明与上述 CoT/正则路径相同；本次未运行这个 adapter。

[local runner](https://github.com/TIGER-AI-Lab/MMLU-Pro/blob/f418b116db00b065c2aea046518d8fcf74d39872/evaluate_from_local.py) · [API runner](https://github.com/TIGER-AI-Lab/MMLU-Pro/blob/f418b116db00b065c2aea046518d8fcf74d39872/evaluate_from_api.py) · [固定 HF eval.yaml](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/blob/b189ec765aa7ed75c8acfea42df31fdae71f97be/eval.yaml)

## 2. 答案解析不是只看最后一句

local 与旧 API parser 优先搜索 `answer is` 后面的 A–J；该分支使用第一次匹配。如果没有，再尝试 Answer:，最后退回独立大写字母的最后一次出现。自然语言中出现字母也可能被识别成选项。

本次执行原始 parser 的合成结果：

| 合成输出 | 解析结果 |
|---|---|
| The answer is (B). | B |
| Initially the answer is (A), but after checking the answer is (D). | A |
| D | D |
| I cannot determine it. | I |
| not sure | None |

这只是边界行为演示，未测量实际模型中发生频率。不能把“最后在语义上选择了某答案”直接等同于该 parser 会返回它，也不能把此行为泛化为所有 MMLU-Pro harness。

## 3. 未解析答案如何进入分数

local `save_res` 先把记录写出，然后对 `pred=None` 的记录在该题实际选项数中随机猜一个索引。猜出的结果不写回 pred。文件内容相同，后续再次计分仍会消耗新的随机数。

源码 `eval_cot` 还会连续两次调用 `save_res`，一次用于日志，一次返回统计。固定 seed 只初始化随机状态一次，不会让两次抽样自动相同。

局部实验输入一个九选项、无法解析的合成记录，连续调用同一原始保存函数 12 次，出现了 0 和 1 两种分数，而保存的 pred 始终为 null。这不是模型表现改变，而是未解析答案的计分政策带来的变化。

独立的 `compute_accuracy.py` 则在未解析时从固定 A–J 中随机选字母，不同于按实际选项长度随机选索引。若题目少于十个有效选项，两种随机回退政策也不同。

[探针脚本](mmlupro_parser_probe.py) · [实际输出及源哈希](mmlupro-parser-probe-output.json) · [独立后处理脚本](https://github.com/TIGER-AI-Lab/MMLU-Pro/blob/f418b116db00b065c2aea046518d8fcf74d39872/compute_accuracy.py)

## 4. retry_wrong 是 oracle 条件，不是普通 API 重试

`evaluate_from_apiX.py` 区分 token/服务失败重试与 `retry_wrong`。后者把解析出的字母与数据集金标准比较：答对即停止，答错而次数仍有余额则重新生成，最终保存被选中的一次。它没有把金标准答案写入下一次提示，但**停止/选择规则用到了金标准**。

该参数默认是 0；固定 README 的一个通用 API 示例显式使用 2。复制这个示例会允许最多三次按正确性筛选的生成，不是普通单次准确率，也不是多数票，更不是模型在不知道真值时进行的自我验证。它可用于调试，但用于比较时必须单独命名和报告。

本次只追踪了这一分支，没有实际调用模型，也没有证据说任何已发布排行榜使用过非零 retry_wrong。

[APIX 源码](https://github.com/TIGER-AI-Lab/MMLU-Pro/blob/f418b116db00b065c2aea046518d8fcf74d39872/evaluate_from_apiX.py) · [README 示例](https://github.com/TIGER-AI-Lab/MMLU-Pro/blob/f418b116db00b065c2aea046518d8fcf74d39872/README.md)

## 5. 复现前还需检查

- 数据 revision、选项清理、类别和真实示例数。
- 模型 API 精确版本、生成预算、stop 条件和上下文裁剪。
- 第一匹配/最后匹配、解析失败、随机猜测和未知答案的处理。
- API 错误是否留在完整题目分母、已有输出何时被复用、重试是否依赖真值。
- 已有结果目录是否混入不同提示、版本或 sampling 条件。

固定仓库新增的 Gemini 3.1 shell 示例指向 `evaluate_gemini_3-1_pro.py` 等文件，但本次固定 tree 中没有这些 Python 文件。因此不能根据 shell 命令反推出其完整评测实现或声称可原样复现该新增结果。

结论不是“选择题 benchmark 没用”，而是：任务内容、候选生成、答案提取和真值使用方式共同定义实验。现成脚本也需要协议审查。
