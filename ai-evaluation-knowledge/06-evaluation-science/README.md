# 评测科学：怎样判断一个分数是否可信

研究日期：2026-11-06。本文库讨论评测方法，不给当前模型排榜。第一批证据已从论文、官方报告推进到固定版本评分代码，并完成本地诊断实验。

## 先抓住五件事

1. **分数是一个测量流程的产物。** 被测对象不只是模型权重，还包括任务抽样、提示词、工具、预算、输出解析、评分器和汇总规则。没有这些条件，两个同名 benchmark 分数未必可比。
2. **可靠性和有效性不同。** 每次都给出相同判决，不代表判断正确；与人类偏好一致，也不代表能辨别事实错误或违反指令。
3. **比较需要逐题数据。** 同为 72% 对 70%，两模型错在同一批题还是不同题，会显著改变差值的不确定性。
4. **可执行测试也需要审计。** 测试通过只是满足这套测试。测试过严会拒绝正确实现，覆盖不足会放过错误实现，日志解析还可能把“没跑起来”误当“没有失败”。
5. **新题不等于零污染。** 应分别说明题目本身、来源材料、解答、数据生成模板，以及开发过程中反复调试造成的泄漏风险。

这些结论分别由有效性综述、统计框架、judge 实验和实际评分代码支撑，不靠单一论文或单次排行榜。证据和范围见 [sources.md](sources.md)。

## 阅读路线

- [01-validity-and-evaluation-design.md](01-validity-and-evaluation-design.md)：先定义测什么、为谁决策，以及如何避免把代理指标当真实能力。
- [02-grading-and-metrics.md](02-grading-and-metrics.md)：评分器选型、pass@k、严格与宽松评分、错误分母。
- [03-statistics-and-comparisons.md](03-statistics-and-comparisons.md)：逐题配对、聚类、重复采样、区间与功效、选择偏差。
- [04-judge-reliability.md](04-judge-reliability.md)：judge 的验证集、顺序偏差、长度偏差、正确率与一致率。
- [05-leakage-and-benchmark-lifecycle.md](05-leakage-and-benchmark-lifecycle.md)：污染证据等级、动态 benchmark、版本管理和退役。
- [case-studies/scorer-execution-traces.md](case-studies/scorer-execution-traces.md)：四套真实评分代码的 D3 执行链及 D4 边界实验。
- [experiments/README.md](experiments/README.md)：复现步骤、实验范围、原始 JSON。
- [evaluation-review-checklist.md](evaluation-review-checklist.md)：用于读模型报告或设计实际评测的清单。

## 深度与边界

- D0：发现来源，尚未实读。
- D1：实读论文、官方报告或文档的相关内容。
- D2：实读真实题目、配置或关键源码。
- D3：追踪具体输入如何经过源码成为分数。
- D4：实际运行并保存结果。

这里的 D4 是**真实官方评分函数在合成输入上的本地测试**，以及**统计模拟**。没有调用模型 API，没有生成模型答案，没有复现完整 SWE-bench 容器评测，也没有据此判断任何模型能力。

## 截至研究日必须保留的更新

- OpenAI 在 2026-02-23 的报告中建议从 SWE-bench Verified 转向 Pro；2026-07-08 的后续报告又因 Pro 数据质量问题**明确撤回这一建议**。不能只引用前一篇。[较新报告](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)
- HumanEval 仓库于 2026-10-16 标注 deprecated / unmaintained。因此本节把它作为历史指标与代码案例，而非推荐的新评测基线。[固定提交](https://github.com/openai/human-eval/commit/b9453e8f1865df0a0057a1383767caa400acfbcf)

维护说明：本目录是阶段性可发布研究，不代表整项长时研究已经结束。后续采集与实验应追加证据，不能把计划标成已完成。
