# GDPval：真实工作产物、数据 v2 与评分服务的边界

研究日期：2026-11-06。**整体 D2，限真实任务记录、文件清单、rubric 与公开适配器；第三方适配器部分达到源码路径 D3。没有打开该任务的工作簿、运行模型、提交评分服务或复现人工评分。**

## 1. 先区分四个版本对象

- 原始论文：arXiv `2510.04374v1`，2025-10-05；对应 2025-09-25 发布的首版研究。
- 原始公开数据：HF `a3848a2a812d5d4d0f08003fac3c8eac40805962`（2025-09-25）。
- 当前公开数据：HF HEAD `11e7900cdcac61bc4daf59e65feb238acda98fbf`（2026-02-10），官方 commit 标题是 **Release GDPval v2 (rubrics + deliverables)**。这次查看仍是 220 条，但已含人工 deliverables 与 rubric 字段，不能继续只按首发“prompts + references”描述。
- 第三方 Inspect Evals：`d95bb308e49d810617ae65f8052dfd848e9ffedb`（2026-11-05），任务 metadata 版本 `2-A`，实际 dataset revision 仍固定到上述 2025-09-25 版本。这个 2-A 不是官方数据 v2。

GDPval-AA 的版本、代理框架、judge、Elo 锚点另有自己的变化，不与这四者互换。模型报告中的名称相近，不代表测量过程相同。

## 2. 任务单位是工作交付，不是职业本身

原始 full set 1,320 个任务，公开 gold set 220 个，44 个职业各 5 个公开任务。行业与职业选择使用美国 GDP、工资、O*NET 工作活动等背景数据；这不是按经济贡献对模型分数加权，也不意味着 220 个交付覆盖整个职业的持续职责。

输入不仅是文字：reference files 可以是表格、文档、图像、音视频、设计文件。输出同样可以是可编辑工作簿、幻灯片等。文件能打开、布局正确、内容可靠、符合需求，是相互关联但不同的评价维度。把这些任务改成纯文本问答会改变测量对象。

本次实际读到当前 rows API 第一条：
- task_id：`83d10b06-26d1-4636-a32c-23f92c57f30b`
- 职业：Accountants and Auditors。
- 任务结构：使用一个参考工作簿进行审计抽样、差异分析，交付另一个含多个 sheet 的工作簿。
- 元数据有一份 reference、一份 human deliverable、38 条 rubric，分值合计 63。
- 字段包括 prompt、reference_files/URLs/HF URIs、deliverable_files/URLs/HF URIs、rubric_pretty 和 rubric_json。
- 当前记录的文件 URLs 指向 resolve/main。读取时同时观测了 HEAD，但 rows 请求没有固定 revision；这不等于已经得到某一提交的字节级完整输入。

未下载或读取这两个工作簿，因此不声称核验了真实列名、公式、行数或人工文件质量。也不发布题目、详细 rubric 或可用作标准答案的内容。

## 3. 一条记录里的内部一致性检查

这条当前记录的 prompt 与 rubric 对操作列位置有不一致：prompt 指定 H/I 两列为季度数据、J 为差异、K 为抽样标记；多条 rubric 则采用 G/H、I、J，并且另外又出现对 K 的计数要求。

这是**已读文本之间的版本/引用一致性问题**，不需要猜测模型输出就能看到。但它尚不能证明哪一组列位置正确：没有打开 reference 工作簿，也没有查看该 rubric 的实际 grader 解释。更不能由一条记录推出整个数据集有同样问题。

工程意义在于：公开了 rubric 并不自动保证 rubric、prompt、reference 与 human deliverable 来自相互兼容的版本。使用数据 v2 前，应把四者一起做 schema 和内容审计，而不是只验题数相同。

## 4. 原始人工评分和自动评分不能并成一个数字

原始论文的主要比较是职业专家盲评模型与人工交付；对每题每模型采样 3 次，每份由 3 位专家比较，即每题每模型 9 次判断。这些判断共用题目、参考文件与人工基线，不能当成 9 个独立职业任务。

论文还披露，风格特征仍可能暴露来源，“匿名”并非模型身份绝对不可推断。首发报告的工具条件也不同：Claude 经 UI 使用文件功能，OpenAI 模型开启 web search 与 code interpreter。因此这里评的是具体系统配置，不是脱离工具与产品的权重本体。

必须明确 tie 的处理：
- win-only 是严格胜出比例；
- win+tie 是“不差于”比例；
- 将 tie 计 0.5 的期望偏好分是第三种统计量。

原始自动 judge 的 agreement 定义也不是分类 exact accuracy，而是对 `H,A ∈ {0,0.5,1}` 计算 `1 - |H-A|`。一个平局与一个胜负判断相差 0.5，而非直接按完全不同类别计 0。报告的约 65.7% 自动-人工一致、70.8% 人工-人工一致，应在此定义下理解，且排除了部分不可稳定自动评分任务与系统错误。

自动 grader 的原始限制包括互联网不可用、运行语言/依赖受限、字体渲染差异与音频处理不足。**grader 环境的能力边界，会改变可评分任务的分母。** 第三方后来的 219/220 成功评分记载也不能反推首发研究从未有 12 个被排除任务；它们可能是不同时间、服务与分析口径。

## 5. Inspect 的 exact 分数是产物收集占位，不是 GDPval 成绩

固定第三方代码路径：

`load_gdpval_dataset → get_gdpval_record → bash/python tools + generate → extract_deliverable_files → scorer → consolidate_deliverable → 外部评分服务`。

关键细节：

1. `get_gdpval_record` 给每题设 `target="NONE"`。注释明确这是为了让默认 exact scorer 能创建 Score 对象。
2. 默认 `gdpval(..., scorer=exact())` 的作用之一是保存最终 answer，让导出表把它写成 deliverable_text。**Inspect 日志中的该 exact 指标并不是官方 GDPval 质量分。**
3. 生成环境是 Docker，工具是 bash/python，每次命令 timeout 180 秒；它不等同原始论文的 code-interpreter API。任务/整个代理运行时间不能从单条命令 timeout 推出。
4. 导出器递归枚举 deliverable_files，把二进制内容编码进 sample store，再写回本地文件。文件缺失或读失败只打印提示并继续；没有导出异常不等于交付完整。
5. 默认 upload_to_hf=False；完整评分仍要求把准备好的结果交给外部服务。本文没有上传、授权第三方访问或提交评分。
6. adapter 固定的是 dataset metadata revision；reference URL 原样交给 Sample.files，没有在这一层强制重写到同一 revision。若记录里是 main URL，文件内容仍需额外固定。尚未检查旧 revision 每个 URL，故不把这个条件性风险写成已发生的结果漂移。
7. prompt suffix 额外要求渲染、检查并修复视觉文件。它会改变代理行为，应该随模型结果记录，不能省略成“零样本完成原题”。

因此有三件可分别完成的事：跑代理生成产物、成功收集提交包、获得有效质量分。一个阶段成功不能替代另两个。

## 6. 时间与经济解释：潜在节省不等于实际替代

原始论文区分直接模型耗时与“先试模型、人工审核、不满意再自己完成”的情景估算。人工完成时间来自经复核的自报，人工费用由时间与职业工资估算；审核时间也是成本，不应删除。

单次尝试的示意结构为：
`模型时间 + 审核时间 + (1 - 成功概率) × 人工重做时间`。

这是工作流情景，不是随机对照的公司部署节省。即使推理很快，审核、失败重做和少量高损失错误仍可能主导收益。论文也提示没有纳入灾难性失误成本。更不能把在已给充分上下文的交付任务上胜出，外推为负责真实职业中的需求澄清、协调、签字责任或长期关系。

## 7. 如何把此案例用到自己的评估

- 数据侧：固定 prompt、reference、human baseline、rubric 四类文件的版本与哈希；避免只固定 Parquet 行而放任附件漂移。
- 系统侧：保存工具/容器、联网能力、图像检查流程、重试和 best-of-N。多次采样后筛选不能标作单样本成功。
- 评分侧：分开 expert、服务自动 judge、自建 rubric judge；记录比较对象、tie、错误/不可评分分母与置信区间抽样单位。
- 交付侧：验证文件数量、打开成功、编辑性、计算和布局；最后一条文字回复不是整个交付。
- 商业侧：用用户真正的任务分布、审核和失败成本做小规模验证，不将基准上的职业覆盖或工资背景直接换算成业务价值。

后续可做：下载并审计该真实工作簿、对照列位置；验证完整附件固定与导出；用人工复核的小集合校准自建 grader。上述动作未完成，本文不提前升级 D4。

## 来源

- [原始论文 v1](https://arxiv.org/html/2510.04374v1)，重点 §2.5、§3.1–3.4、A.2.1、A.6。
- [官方发布](https://openai.com/index/gdpval/)。
- [官方 HF commit 历史](https://huggingface.co/api/datasets/openai/gdpval/commits/main)。
- [当前数据固定提交](https://huggingface.co/datasets/openai/gdpval/tree/11e7900cdcac61bc4daf59e65feb238acda98fbf)。
- [实际任务 rows 请求](https://datasets-server.huggingface.co/rows?dataset=openai%2Fgdpval&config=default&split=train&offset=0&length=1)，未固定 revision。
- [Inspect 任务](https://github.com/UKGovernmentBEIS/inspect_evals/blob/d95bb308e49d810617ae65f8052dfd848e9ffedb/src/inspect_evals/gdpval/gdpval.py)。
- [Inspect 数据/导出适配](https://github.com/UKGovernmentBEIS/inspect_evals/blob/d95bb308e49d810617ae65f8052dfd848e9ffedb/src/inspect_evals/gdpval/util.py)。
- [Inspect 文件收集](https://github.com/UKGovernmentBEIS/inspect_evals/blob/d95bb308e49d810617ae65f8052dfd848e9ffedb/src/inspect_evals/gdpval/extract_output.py)。
- [Inspect 复现说明与限制](https://github.com/UKGovernmentBEIS/inspect_evals/blob/d95bb308e49d810617ae65f8052dfd848e9ffedb/src/inspect_evals/gdpval/README.md)。

