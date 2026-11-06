# BrowseComp：短答案正确性与浏览能力之间的距离

研究日期：2026-11-06。证据深度：**D3（reference evaluator 调用链）**；另完成 **D4 范围限定的 parser 单元实验**，不是整个 benchmark 的复现。适合 L1–L3。

## 版本与资料

- 官方说明：[BrowseComp, 2025-04-10](https://openai.com/index/browsecomp/)。
- 固定代码：openai/simple-evals，commit `652c89d0ca9df547706735883097e9537d40dc47`（2026-04-22）。
- [browsecomp_eval.py](https://github.com/openai/simple-evals/blob/652c89d0ca9df547706735883097e9537d40dc47/browsecomp_eval.py)、[common.py](https://github.com/openai/simple-evals/blob/652c89d0ca9df547706735883097e9537d40dc47/common.py)、[simple_evals.py](https://github.com/openai/simple-evals/blob/652c89d0ca9df547706735883097e9537d40dc47/simple_evals.py)。

## 它实际测什么

官方题集有 1,266 道题，构造方向是从可核验事实反推难检索问题。目标是找到短而明确的答案，不是评估长篇研究报告的论证、引用覆盖率、重要性判断或用户问题澄清。它把“难做、易验”的不对称性变成可运行任务。

**结论边界：**正确答案可以来自浏览、内部知识或其他策略；仅凭最终正确率不能识别搜索过程是否可靠。因此浏览工具、检索预算、网页环境、尝试数及答案选择策略是实验条件，而不是数据集天然固定的属性。

## 源码执行链

1. `BrowseCompEval.__init__` 读公开 CSV；可用固定 seed 0 抽取子集。题目和答案使用 canary 派生的 XOR key 解码，作用是降低意外泄漏，不应理解成保密机制。
2. `__call__` 将解码题目放入输出格式模板，要求 explanation、exact answer、confidence，然后调用传入的 `sampler`。
3. `grade_sample` 把问题、参考答案及模型回复交给另一个 grader sampler。评分模板要求抽取最终答案并判断语义等价，不要求 grader 自己求解。
4. 单题被包装成 `SingleEvalResult`；公共聚合函数汇总均值等统计并保存对话/HTML。reference evaluator 本身没有实现浏览器，它依赖 sampler 提供能力。

## 一个实际复现的接口缺陷

本 commit 中，`grade_sample` 用正则 `correct: (yes|no)`，返回的是 `match.group(0)`，而调用方用 `grade_result == "yes"` 判断正确。两者接口不一致。

| 模拟 grader 返回 | 实际 grade_sample 返回 | 调用方 is_correct | is_incorrect |
|---|---|---:|---:|
| correct: yes | correct: yes | false | false |
| correct: no | correct: no | false | false |
| invalid output | no | false | true |

实验只从固定源码 AST 中提取 `grade_sample`，用本地 mock grader 替代 API；没有取数据集、没有访问模型、没有进行搜索、没有完整 benchmark 分数。因此它证明的是**该固定版本 reference parser 的行为**，不能证明论文或榜单成绩使用同一实现，更不能据此宣布公开成绩无效。修正建议是返回 group(1)，并增加 structured output 与格式失败独立计数；未修改上游。

实验脚本：`browsecomp_parser_probe.py`。输入必须是上述固定版本的源码文件。实验输出：`browsecomp-parser-probe-output.json`。

## 学习与工程检查点

- 把 grader 输出 schema 当 API contract 测试，不要只测试 prompt 文案。
- 至少包含正确、错误、无答案、格式错误四类 fixture。
- 留存原始 judge 输出、解析结果、解析版本和逐题分数。
- 将网页取得的证据质量另设维度；不能从短答案 accuracy 推导引用真实性。
- 因题集带明确的防污染要求，本笔记不复制解码后的题目和答案。

## 未做

没有审计其他 fork、发布成绩的内部 evaluator、全部 grader prompt 稳健性或 judge 校准；没有 D4 端到端 run。
