# LongBench v2：长文档、实际输入与统计分母不是同一件事

更新日期：2026-11-06。**整体证据保守记为 D1**：官方论文、方法和固定源代码已读，已追踪预测到汇总的程序路径；但未成功读取完整真实数据条目，因此不满足本研究 D2 的完整前置条件。没有调用模型，也未复现榜单。

## 版本与可访问性

- 代码：`THUDM/LongBench`，提交 `2e00731f8d0bff23dc4325161044d0ed8af94c1e`，2025-01-15。
- 论文：arXiv `2412.15204v2`，2025-01-03。
- 本次读到：`pred.py`、`result.py`、模型长度配置、direct 与 CoT 答案模板、README、官方方法页。
- Hugging Face 的旧组织地址重定向到 `zai-org/LongBench-v2`；数据页注明 viewer 的 row group 超出可读取大小。直接读取大型 JSON 又超时。本次没有下载完整约465 MB数据文件，也没有固定数据 revision。

[固定源代码](https://github.com/THUDM/LongBench/tree/2e00731f8d0bff23dc4325161044d0ed8af94c1e) · [论文](https://arxiv.org/html/2412.15204v2) · [数据页](https://huggingface.co/datasets/THUDM/LongBench-v2)

## 1. 两代数据与两种长度单位

固定仓库根目录对应 v2；旧 v1 内容放在 `LongBench/` 子目录。v2 的任务定义为503道选择题，文档长度用 **words** 描述。模型调用代码则依据 tokenizer 计算的 **tokens** 截断。这两个长度不是可直接等同的数值。

因此“在2M长度任务上得分”并不保证模型实际读过全部2M words，也不能据此确认模型拥有相同大小的有效上下文窗口。需要另记原始文档长度、模板后的 token 数、截断后 token 数与所使用的 tokenizer。

[项目说明](https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/README.md) · [长度配置](https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/config/model2maxlen.json)

## 2. 源码路径与四种运行模式

`main` 从 Hugging Face 加载数据，按已有输出中的 `_id` 跳过已完成项，再启动并行预测。`get_pred` 选择 direct、CoT、no-context 或 RAG 模板。`query_llm` 对整份 prompt 做 tokenizer 编码；超限时保留开头和结尾各约一半，丢弃中间部分，随后通过 OpenAI 兼容接口发送单条 user message。

直接模式一次调用输出答案。CoT 模式先生成分析，再进行第二次答案调用；第二次模板明确省略长文，保留问题、选项及上一轮分析。RAG 模式使用提供的 retrieved chunks，按原文位置重排后组装。它不在该函数内实现检索器；不能仅凭 `--rag` 参数认定完整检索流程已经包含在同一脚本。

[预测代码](https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/pred.py) · [CoT 最终答案模板](https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/prompts/0shot_cot_ans.txt)

## 3. 答案解析本身也是实验条件

该实现先删除星号，再用特定英文句式提取 A–D。单独回复一个正确字母、使用其他措辞或其他大小写，并不一定被解析为正确。判分随后只是提取结果与答案标签相等。

这是一条具体的 parser contract，不代表所有后续 LongBench 评测都必须使用同一规则，更不能自动推断模型榜单差异来自解析失败。若改用更宽松 parser，应把版本及受影响样本另行报告。

## 4. API 失败、缺失与分母

固定 `query_llm` 最多尝试五次，仍失败时返回空字符串；`get_pred` 遇到空字符串会跳过该项而不写输出。`result.py` 则以实际读到的预测条目数作为整体分母，而没有在脚本内核对预期503条是否齐全。

所以一次不完整运行可以产生只基于成功返回项的数值。正确实践应同时报告 expected、attempted、scored、API-error、parse-error 数量，并显式决定缺失如何计分。此处是源码行为，不是对作者已公布实验遗漏样本的指控。

汇总脚本还包含默认关闭的 `compensated` 分支：若打开，无法解析的答案可以得到随机猜测基线式的部分分数。该开关会改变指标定义，应作为协议字段记录，而不是不加说明地与默认成绩混用。

[聚合代码](https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/result.py)

## 5. 结果缓存与可追溯性

预测文件按模型名称及模式命名，现有 `_id` 会被视为已完成。若修改了模型 revision、模板、token budget 或 tokenizer 却继续使用同一输出文件，可能混合多个协议的结果。本研究未观察到实际混合运行，只指出该缓存键不包含全部测量身份。

另一个细节是写日志时只保留 context 的前一小段。它能减少结果文件体积，但不能单靠该字段恢复真正发送给模型的完整截断 prompt。复现实验应额外保存输入 hash、数据 revision、截断策略和最终调用配置。

## 6. 可迁移检查表

- 长度：文档 words、输入 tokens、实际可见区域分别是什么？
- 模式：一次调用还是两次，第二次看到什么材料？
- 提取：语义答案正确但格式不同，会怎样计分？
- 缺失：API失败、空回答、解析失败是否进入同一分母？
- 缓存：哪些字段改变后必须重跑？
- 审计：是否能恢复实际 prompt，而不只是原始数据的一小段？

这些问题对任何长上下文基准都适用，但答案必须从各自的固定实现读取，不能把本案例的行为外推到所有项目。
