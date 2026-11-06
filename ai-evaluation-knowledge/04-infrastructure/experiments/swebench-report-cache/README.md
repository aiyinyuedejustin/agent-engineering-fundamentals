# SWE-bench report cache：源代码分支的最小实验

**D4 仅针对缓存分支，非完整 SWE-bench/Docker 复现。** 学习目标 L2。

## 固定输入

- SWE-bench commit `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`。
- 原文件 [swebench/harness/run_evaluation.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/run_evaluation.py)。
- Git blob `bf9680f8d910f274ffbba35d57ec5d0e47a96243`，31442 bytes。
- SHA-256 `04b5dab584fbe62ae9d1ff025edf52d714e584102d587c7e647805d1efb37d84`。

## 重现

保留上述原文件字节后运行：

```sh
python3 run_report_cache_test.py /path/to/run_evaluation.py
```

脚本验证完整文件 Git blob，只提取未修改的 `run_instance` AST function，并保留 upstream future-annotations 语义。使用 Python 标准库、合成 spec/prediction 和真实临时 JSON 文件。cache miss 在创建 logger 之前被保护钩子停止，不能进入 Docker 或 test execution。

## 实际结果

见 [result.json](result.json)，实际执行于 `2026-11-06T03:00:13.725224+00:00`。

相同 run ID、model name、instance ID 命中同一 report。修改 patch、image 或 skip_patch 均未改变这个缓存结果。新 run ID 触发 cache miss，被保护钩子停止。

这只验证缓存键与顺序，不声明原 report 真实有效，也不说明 CLI 的所有过滤/重新评分路径都已运行。缓存用于相同输入的 resume 很合理；实验展示的是输入改变后错误复用 run identity 的风险。

## 实验修正记录

首次测试的 cache-hit 检查成功，但 cache-miss 对照在 logger 前引用 `LOG_INSTANCE` 时因实验 namespace 漏填该常量而发生 NameError。补入合成日志文件名后完整重跑通过。这是本地实验 fixture 的修正，不是上游缺陷。两次均未创建容器或执行测试。
