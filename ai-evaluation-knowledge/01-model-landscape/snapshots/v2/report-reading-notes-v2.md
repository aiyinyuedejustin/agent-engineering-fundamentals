# 第二批模型报告核验记录

状态：采集与局部核验持续进行。本文是原文章节阅读记录与可比较性判断，不是全领域排名或最终综合结论。日期为 2026-11-06。所有厂商结果仍为 D1，没有独立重现。代码组件实验另见 [gpt-oss 微实验](experiments/gpt-oss-eval-microprobe/README.md)。

## 本轮新增的可核验信息

模型来源登记册仍为 94 条来源记录，其中 D1 从 19 增至 26；其余 68 条仍 D0。99 个模型–评测数值观察包括上一版 42 条与新增 57 条，不能当作 99 个独立 benchmark 或模型。每条都有 source_id、表格/章节、配置、单位、范围与限制。

### Magistral：先明确估计的量，再看大小

[论文 v1](https://arxiv.org/html/2506.10910v1) §5、表 2–4区分单次采样平均成功率与 64 次多数投票。Magistral Medium 的 AIME2024 是 pass@1 73.6、maj@64 90.0。Small 的 SFT、RL-only、SFT+RL 三种训练阶段在 pass@1 上分别为 65.4、65.8、70.7，但 maj@64 为 90.0、86.7、83.3。它们说明两个指标能给出不同顺序，不支持“RL 对所有选择策略都单调提升”的结论。

AIME 采样 64 次，LiveCodeBench 采样 16 次；推理、代码任务 top-p 不同。多语言 AIME 将原题翻译并约束推理与输出都使用输入语言，中文 63.7 对英语 73.6。只有 30 道题，语言约束、翻译质量与推理能力不能从这一差值中分离。

### MiniMax-M1：预算标签不等于只改一个参数

[论文](https://arxiv.org/html/2506.13585) 说明 40k 模型是 80k 训练过程的中间版本。因此表 2 的 40k/80k 差别不应登记为纯推理预算因果实验。两者在 SWE-bench Verified 为 55.6/56.0，使用修改版 Agentless、两阶段 localization，不使用 embedding retrieval。论文没有证明它们与其他厂商 agent harness 等价。

tau-bench 用户模拟器为 GPT-4.1，最多 40 步。airline 60.0→62.0，但 retail 67.8→63.5；MRCR128k 为 76.1→73.4，1M 为 58.6→56.2。扩展上下文长度是输入规格，不是每种长上下文任务表现的保证。HLE 表中有 text-only 星号，不能沿表横向忽略这个差异。

### Olmo 3：把评测成本和重复数写进实验设计

[论文 v1](https://arxiv.org/html/2512.13961v1) §4.1.1 说明，在其 7B 开发阶段，评测占计算预算 10%–20%。这是这组开发流程的观察，不能外推为所有团队的固定比例。

论文用 14 个模型各运行 3 次，先计算每个模型的标准差，再取 benchmark 维度的均值。报告 GPQA 为 1.4798、AlpacaEval 3 为 1.2406、IFEval 为 0.8835；AIME24 使用 avg@32 后为 0.5437，LCB 使用 avg@10 后为 0.2852。这不是未经重复数控制的 benchmark 固有方差排名。

表 16 明确 temperature 0.6、top-p 0.95、最多 32768 tokens、零样本提示，评分前移除思考段。AIME 每题 32 次，代码每题 10 次，不同任务的答案抽取规则也不同。K2-V2 的 AlpacaEval 因 judge token parsing 出错得到 null，不应该填成 0。这里尚未追踪 Olmo evaluator 代码，不标 D2/D3。

### Step 3.5 Flash：同一报告也需要对齐正文与附录

[论文 v1](https://arxiv.org/html/2602.10604v1) §6.2 和附录 E.2 是本轮最详细的 agent 配置来源之一。正文称 IMO-AnswerBench 8 次、其他未单列任务 4 次；附录却称 IMO-AnswerBench 64 次，并对 deep search 指定 avg@3（GPT-5.2 xHigh 为 avg@1）。记录这些不一致，不自行替作者选一个作为绝对真值。

PaCoRe 使用 [4,4,4,4] 多轮并行轨迹。AIME2025 从 97.3 到 99.9，HLE text 从 23.1 到 27.9，而 IFBench 从 67.4 到 56.8。应登记为系统配置变化，不把 PaCoRe 的结果称为普通单次模型调用结果。

Terminal-Bench2.0 使用修改的 Terminus2：命令超时后中断、跳过同轮后续命令，内部软件包镜像、16GB 内存、XML 交互、上下文保留问题与最近 50%、最多 200 轮和 6 小时。检查器也做了修正。表 16 同一系列 avg@8 从 baseline 50.98 到输出16k的48.03，再到无 pruning 的45.22。不能把表里的 avg@8 与报告提到的 pass@8 混为一谈。

BrowseComp 全集 discard-all 的 69.0，和表 17 的 200 例子集 discard-all 66.0不是冲突。子集里 multi-agent 为 68.5、721 real steps，而普通方式为49.5、86 steps。更高分伴随更多步骤与不同编排，这不是等预算比较。

tau2-bench 使用 GPT-4.1、温度0作为用户，并使用特定 airline ground truth 修正、retail/telecom 用户提示补充。88.2 的 8 次平均不能直接与 DeepSeek 使用模型自身为用户的80.3对应。

MRCR-8needle 在这里为线性 token 轴上梯形积分的 AUC@128k，不是“128k位置准确率”。FRAMES-Oracle 预先给出全部正确 Wikipedia 文章，不能用于证明检索链的效果。CF-Div2 自建53题与生成测试、无时间罚分的 Elo 假设也需要单独记录，不能当真人竞赛排名。

### Nemotron 3 Ultra：发布模型、量化实验与 test-time system 分开

[官方报告](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf) §3.7.2 强调 PinchBench、ProfBench 是最终只评一次的 held-out 测试，没有用于 checkpoint selection。这是报告对开发流程的陈述，尚未通过训练日志核验。

证明数学结果使用每题128条尝试、512k context、generate/verify/refine，不是 pass@1。量化章节的一些表来自中间 checkpoint、NeMo Evaluator SDK 与 vLLM0.20.0；不同 BPE 配方改变了哪些层量化，不能只把 BPE 当连续单变量。最终模型、量化 recipe、软件后端、推测解码、吞吐测量条件必须独立登记。

### Grok4.20：安全系统卡不自动等于能力报告

[官方系统卡](https://data.x.ai/2026-04-07-grok-4-20-model-card.pdf) 明确有 single-agent 与 multi-agent 模式，未注明时默认 single-agent、内部工具、最终部署 checkpoint。安全表格中有0–1率值，不能再误乘或误认为已是百分比。没有从安全成功率推断总体商业或研究能力。

### gpt-oss：论文证据与后期公开代码不合并成同一个版本

[论文 v1](https://arxiv.org/html/2508.10925v1) §2.6/表3为低、中、高三档 reasoning 和有/无工具提供分数。例如120b的 AIME2025 无工具为50.4/80.0/92.5，有工具72.9/91.6/97.9。20b tau-bench airline 为32.0/42.6/38.0，单凭点估计不能声称所有任务都随 effort 单调提升。

论文对 MMMLU 描述了移除 Markdown/LaTeX 和多语言答案标记的抽取处理，说明 parser 是评测协议的一部分。本轮进一步读取并固定晚于论文的官方 eval 源码，完成27个组件探针。源码结论见单独实验文件，不将晚期代码默认配置追溯为模型卡实际使用配置。

## 后续核验队列

- 仍有68条来源只发现、未读正文，优先补 GLM、ERNIE、LongCat、MiMo 等原始报告，而不是扩大“已验证”数字。
- 深挖 Qwen、DeepSeek、Kimi 的数据 revision、judge、harness commit 和成本口径；厂商分数只能作为具体配置的观察。
- 对日期异常、正文/附录冲突、指标单位缺失保留未知值，寻找作者解释或可执行配置，不自行补齐。
- 对实际模型复现另建资源/费用计划，不能用组件实验充当大型模型成绩复现。
