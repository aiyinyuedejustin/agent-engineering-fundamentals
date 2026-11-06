# SWE-bench：通过测试不等于一个不变的测量规则

研究日期：2026-11-06。深度：**D3（任务字段、run_instance 与 grader 源码链）**。没有运行模型、Docker 或完整数据集。适合 L1–L3。

## 版本边界

固定 harness commit：`02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`，2026-09-02。
数据实例来自 2026-11-06 读取的 [SWE-bench Verified 数据页](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)，数据集 revision 未锁定，因此不能声称这个笔记是完整可复现 manifest。

[官方总览](https://www.swebench.com/) 将原版 2,294、Lite 300、Verified 500、Multilingual 300、Multimodal 480 分开；Bash Only 是固定 mini-SWE-agent 环境下的 Verified 展示。不同数据集与 harness 不能只用“SWE-bench”一个字符串表示。

## 真实任务结构

读取了 `astropy__astropy-12907`：任务涉及嵌套组合模型的 separability 计算。实例给出 repo、base_commit、problem_statement、reference patch、test_patch、FAIL_TO_PASS、PASS_TO_PASS、image、log_parser、eval_script 等字段。模型应看到问题与待修复代码；reference patch 与验收测试不应错误暴露到 agent workspace。

此例说明任务不是“一段文字 + 一个答案”。它还依赖代码版本、测试补丁、环境镜像及日志解析器。这里不复制完整题目或解法。

## 源码路径

- [run_evaluation.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/run_evaluation.py)
- [grading.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py)
- [evaluation guide](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/docs/guides/evaluation.md)

`run_instances` 将数据变成 TestSpec 并并行分派；`run_instance` 创建容器、应用模型 patch、放入 eval 脚本、限时运行测试、写日志、调用 `get_eval_report`。复用相同 run_id/model/instance 且已存在 report 时会直接读缓存，不能拿旧结果冒充新 patch 的评测。

`get_logs_eval` 先判定日志有效性，调用对应 repo parser，再由 `get_eval_tests_report` 区分需要从失败变成功的 F2P 与需要维持成功的 P2P；二者均完整通过才是 full resolution。数据的 `eval_type` 会改变缺失测试的语义。

## 代码比“跑 unit tests”多出的东西

本版本明确处理了：
- 测试根本没执行时，不能把空结果当成功。
- F2P 被 skip 不能算修复；P2P 的 skip 在本版本可算没有回归。
- 参数化测试 ID 被截断时，只有候选结果一致才使用前缀回退。
- 测试输出 marker 外的真实结果需要回退读取。
- 打印 PASSED 字符串不能覆盖测试进程实际非零退出状态。

这些并非已复现的所有上游缺陷发生率，而是已读源码中的行为。相关[反伪造测试](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/tests/test_grading_spoofed_output.py)和[marker 测试](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/tests/test_grading_marker_fallback.py)给出了回归场景。

## 外部有效性与最新争议

OpenAI 2026-07-08 的[一手审计](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)报告 SWE-Bench Pro 的任务问题并撤回此前推荐 Pro 的建议。其 human campaign 在先筛选的可疑任务上判定问题，再以全部 731 public tasks 为分母；27.4% 和 34.1% 来自不同审查路径，不能混写为两个独立随机抽样估计。它是一个模型开发方的审计结论，仍须结合 benchmark 维护方回应、任务 revision 和后续修复判断。

**建议：**把 SWE-bench 用作可解释的软件修复测量组成部分，而不是雇佣能力、代码质量、安全性或全部软件工程能力的代名词。报告数据版本、scaffold、预算、测试覆盖、基础设施失败与有效分母。
