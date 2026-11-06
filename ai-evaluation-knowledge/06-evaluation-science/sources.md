# 来源与证据账本

检索日期：2026-11-06。可机器读取的记录见 [sources/sources.json](sources/sources.json)，含实读范围、版本、支持的主张、限制和对应文件。记录的是已读/已执行证据，不把检索结果当实读。

| ID | 来源 | 深度 | 用途与重要限制 |
|---|---|---|---|
| ES01 | [Miller：Adding Error Bars to Evals，v1](https://arxiv.org/html/2411.00640v1) | D1 | 配对、聚类、重复采样、功效；§4.2 数值示例存在算术不一致，本库另行核对，不照抄 |
| ES02 | [Bean 等：Construct Validity，v1](https://arxiv.org/html/2511.04703v1) | D1 | 445 篇论文的构念有效性审查；特定会议/年份样本，不是普查 |
| ES03 | [Weidinger 等：Evaluation Science，v3](https://arxiv.org/html/2503.05336v3) | D1 | 真实使用情境与迭代评测；观点与框架，不是统一效果量 |
| ES04 | [HELM 原始论文官方摘要](https://arxiv.org/abs/2211.09110) | D1，范围有限 | 实读摘要与官方首页，未读完整技术报告；仅支持设计原则 |
| ES05 | [MT-Bench / Arena judge 论文，v4](https://arxiv.org/html/2306.05685v4) | D1 | 位置/冗长偏差与 agreement 口径；2023 历史模型 |
| ES06 | [AlpacaEval-LC，v2](https://arxiv.org/html/2404.04475v2) | D1 | 长度控制、gameability 与限制；不等于消除全部 judge 偏差 |
| ES07 | [LLMBar，v2](https://arxiv.org/html/2310.07641v2) | D1 | 指令遵循的 meta-evaluation；对抗集不是生产分布 |
| ES08 | [Oren 等：污染检验，v2](https://arxiv.org/html/2310.17623v2) | D1 | 可交换性、序列似然、置换检验；未检出不能证明无污染 |
| ES09 | [LiveBench，v2](https://arxiv.org/html/2406.19314v2) | D1 | 附录 A.4–A.7 评分、重评、更新与污染限制；未核验当前月度履约 |
| ES10 | [OpenAI：Verified 审计，2026-02-23](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) | D1 | 138 道失败筛选子集；59.4% 不能外推到全部 500 题 |
| ES11 | [OpenAI：Pro 审计，2026-07-08](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) | D1 | 筛选与复核流程；明确撤回 ES10 中推荐 Pro 的建议 |
| ES12 | [HumanEval 固定源码 b9453e8](https://github.com/openai/human-eval/tree/b9453e8f1865df0a0057a1383767caa400acfbcf) | D4，窄范围 | 只运行 pass@k 纯函数；仓库已弃用且不再维护 |
| ES13 | [SQuAD evaluator eee5fdb](https://github.com/rajpurkar/SQuAD-explorer/blob/eee5fdbf62f8613a7812b03419e6b29617b74fd1/evaluate-v2.0.py) | D4，窄范围 | 合成归一化与阈值输入；不是数据集缺陷率 |
| ES14 | [FastChat judge 587d5cf](https://github.com/lm-sys/FastChat/tree/587d5cfa1609a43d192cedb8441cac3c17db105d/fastchat/llm_judge) | D4，窄范围 | API stub 下运行官方解析函数；没有实际 judge 调用 |
| ES15 | [SWE-bench harness 02e7a74](https://github.com/SWE-bench/SWE-bench/tree/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness) | D4，窄范围 | 状态、test ID、日志门槛函数；非完整容器运行 |
| ES16 | [本研究统计实验](experiments/results/statistical_diagnostics.json) | D4 | 合成模拟，原始执行 2026-11-06 02:31:41 UTC；非模型实验 |

## 主张与证据对应

- “分数不自动表示真实工作能力”：ES02、ES03、ES04，综合解释。
- “同样总分差可能具有不同统计证据”：ES01 的推断公式 + ES16 的构造数据实际运行。
- “高重复一致率不等于准确”：ES05、ES07 的实证设计 + ES16 的类别不平衡反例。
- “judge 的 parser 也属于评分系统”：ES14 的代码追踪 + 实际 stub 测试。
- “自动评分不保证语义等价”：ES13 的实际边界运行。
- “没有失败日志不等于成功”：ES15 的完整日志门槛与状态分支一起解释。
- “动态题不等于保证无污染”：ES08 的检测范围 + ES09 的明确限制。
- “不能沿用已撤回推荐”：ES10 与时间更晚的 ES11，对照原始发布日期和结论。

## 未完成和不在此批范围

- 没有付费模型调用，也没有端到端模型 benchmark 复现。
- 没有用人工合成的错误示例估计现实错误频率。
- 没有对 2026 年全部 judge 文献做系统综述；新出现的研究线索不在已确认结论内。
- 未独立重建 SWE-bench 两次供应商审计的人工标注全过程。
- 没有确认 LiveBench 最新月度运行记录，也不保证其论文政策始终照常实施。
- 未读取 HELM 全文，故只使用官方摘要能支持的多指标设计事实。

## 版本与版权

本目录的解释、清单和实验脚本是原创整理；没有把论文全文或完整第三方仓库复制进交付物。官方代码下载链接固定在提交上，评分实验逐文件核对 Git blob SHA，并在结果保存 SHA-256。复现实验下载原始文件后仅执行经过阅读的允许函数。

初次访问 LiveBench / LLMBar 时猜测的 v3 URL 返回不存在；随后读取官方版本历史，改为确实存在的 v2。不存在的页面没有被用作证据。
