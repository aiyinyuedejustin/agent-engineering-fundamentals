# Ling 2.0、KAT-Coder与Ovis2.5：保留协议空白比补出一个排名更重要

观察日期：2026-11-06。本轮三篇官方报告限定章节达到D1/L1；新观察ME191–ME209。没有运行模型、读取这些成绩所用的真实任务或完成可复现配置追踪。

## 1. Ling 2.0：多次采样不自动变成pass@k

来源：[Ling 2.0 v2](https://arxiv.org/html/2510.22115v2)。已读§4.5–4.6、§5.5与表8/脚注。返回文本在约150k字符处截断，不能说读完全文；本次引用的章节均在完整返回区域。v2修订日期未另行确定。

评测默认0-shot，GPQA每题重复16次，ARC-AGI-1、ZebraLogic、HLE每题重复4次，但报告明确给的是 **pass@1**。这些重复用于估计单次表现，不是多次取最好、pass@4/16或多数票。记录中保留repeat数，而不擅改指标名。

报告对BBEH与Omni-MATH使用LLM judge。尤其Omni-MATH明确没有沿用其所说的原规则评价方式，因此74.46不能与任意“Omni-MATH准确率”视为同协议。具体judge模型、版本和提示尚未核实；HLE的文本/多模态子集也没有在已读段落确定。

表8的几个脚注改变了分数含义：

- CodeForces1901基于14场Div.2比赛与专家测试用例，该基准最高可达2209。它不是实时Codeforces账号rating，也不是人群百分位。
- MultiPL-E77.91只覆盖Python、C++、Java、JavaScript、TypeScript、PHP六种语言，不是原基准所有语言的总体结果。
- Arena-Hard v2的style-controlled76.26和win-rate75.83是两列不同量，不能只按任务名合并。
- OlympiadBench-Stem选择无图的物理子集，不应扩张成完整多模态OlympiadBench。

ApexEval用于选择最有潜力继续RL的checkpoint，目标是多次尝试的潜在上界，不是最终产品的单次可靠性。作者使用“最高pass@k”之类表述，但已读方法没有提供足以重建整个估计器的完整细节。论文还把MathVerify/XVerify举在智能judge类别下，本文不因此推断实际执行依赖一定是某个LLM服务；需要读具体实现才能确定。

§5.5报告在OpenCompass上加入多节点Ray/SGLang、重复前缀缓存与异步执行。这是评测基础设施性能的作者陈述，不等于本轮复跑。checkpoint评测耗时缩短、prompt缓存吞吐提高和模型准确率是不同结果，不能互相替代。

## 2. KAT-Coder：论文明确的只有一部分比较条件

来源：[KAT-Coder v3](https://arxiv.org/html/2510.18779v3)，§5与表1。

SWE-bench Verified73.4明确使用Claude Code，但该段没有提供Claude Code revision、任务镜像、token/turn限制、超时、重复次数或方差。本轮可以保存“作者在Claude Code下报告73.4”，不能宣称已复现，也不能无条件与另一Claude Code版本的分数排序。

tau2的62.3是 **Retail单域**，不是三域平均。LiveCodeBench48.2指定V6，但已读段落没有精确日期切片与生成设置。其他领域分数也不能补造pass@k、采样温度或judge。

论文用整体比较来论证四阶段训练有效；比较表本身不足以识别每个阶段的因果贡献。需要stage ablation、等计算量对照等额外证据才能把“每阶段都贡献多少”写成结论。本轮不把训练说明当作已完成的机制验证。

## 3. Ovis2.5：总分、原版/新版OCR和视频条件都要拆开

来源：[Ovis2.5 v1](https://arxiv.org/html/2508.11737v1)，§2、§4.1–4.5及表2–8，2025-08-15版。

OpenCompass总体分为八项benchmark得分的平均，2B/9B分别73.9/78.3。它是跨不同构念与评分规则的宏平均，不是把所有题目合成一个样本池的准确率。任一任务的增加、删减或重新缩放都可能改变总分的解释。

报告优先引用官方成绩，没有时才自行重测并标星号。混合表不能默认对手都经过同一实现、judge、图像设置和采样预算。Ovis自身的thinking模式是可选的，但已读评测章节没有足够细节把所有表格唯一映射到token预算、thinking开关和temperature，须保留空缺。

OCRBench原版与v2不同：Ovis2.5-9B在总体套件的原版OCRBench为87.9，而v2英文/中文为63.4/58.0。不能用后两者画成同任务退化，也不能把英文和中文不说明权重地合并。DocVQA/TextVQA在该表是validation拆分，MMMU也是val。

Video-MME字幕/无字幕为72.8/68.6，属于原版Video-MME，不是后来Video-MME-v2。帧采样、resize、字幕注入、模型适配器与judge并未在已读段落固定。本知识库的VLMEvalKit v2组件实验不能用来解释或纠正这些2025报告成绩。

原生分辨率架构描述表示采用NaViT并保留可变分辨率输入的结构；不能仅凭“native resolution”几个字推断processor无限制保留任意输入像素。报告把4K感知与长视频列为未来方向，实际像素上限和video token预算仍需源码/配置检查。

## 本轮可复用的阅读纪律

- 报告给多少配置就记多少，未给出的不要凭模型家族常用设置补齐。
- 采样次数、pass@1、pass@k、majority vote和checkpoint选择上界分别保存。
- benchmark名称后保留版本、语言、日期范围、拆分和评分器。
- 从“表格分数”到“可复现工程结论”至少还缺配置、真实任务、执行路径与实际运行证据。
- 不能把某个实现的后续缺陷反推为更早或另一个实现发布成绩的错误。
