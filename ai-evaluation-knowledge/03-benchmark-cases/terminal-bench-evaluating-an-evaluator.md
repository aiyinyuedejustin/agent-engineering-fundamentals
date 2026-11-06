# Terminal-Bench 4.0：当被测 agent 的产物本身是 evaluator

更新日期：2026-11-06。深度：**D3，仅任务内部的执行与验收路径**。未运行 Harbor、容器、GPU 推理或完整任务，不能称为 D4，也不能据此推断任何模型的 Terminal-Bench 分数。

## 固定研究对象

- 仓库：`harbor-framework/terminal-bench`。
- 发布标签：`v4.0.0`。
- 提交：`452bf305c6daa62fc59061d22133a7cbc7c1572e`，提交时间 2026-08-26。
- 任务目录：`tasks/math-eval-grader`。
- 已读：任务说明、`task.toml`、README、agent Dockerfile、`tests/test.sh`、`tests/test_outputs.py`。
- 本文为原创分析，不复制完整任务、答案、隐藏测试或参考解法。

[固定版本任务目录](https://github.com/harbor-framework/terminal-bench/tree/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader)

## 1. 这里有两层 evaluation，不能混称为模型数学能力测试

外层：Terminal-Bench 测试一个 agent 能否在给定计算环境里完成软件工作。内层：该 agent 必须实现数学答案 grader，并用它评估一个固定的小型数学模型。外层分数衡量的是评测工程任务的完成情况，内层 accuracy 是被要求交付的结果字段，二者不相同。

输入包括题目文件、答案 PDF 和有标签的开发样例。交付物是抽取出的答案数据、可调用的 grader 与包含原始模型输出的结果文件。模型 revision、生成参数和环境依赖均有约束；这不是允许 agent 自由挑选模型、提示词、数据子集的开放分析。

[任务说明](https://github.com/harbor-framework/terminal-bench/blob/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader/instruction.md)

## 2. 任务 contract 比 README 概览更接近实际运行条件

`task.toml` 将三个产物列为 artifacts；agent 时限为 28,800 秒，verifier 为 900 秒，后者使用单独环境。agent 环境请求 8 CPU、16 GiB 级内存、30 GiB 级存储和一张 H100。这里的资源是任务声明，不代表本次研究实际启动过这些资源。

README 顶部的旧摘要仍写 4 小时，但同一文件变更记录、instruction 和 TOML 都反映 8 小时。这是版本研究中很常见的局部文档陈旧：应记录冲突，再以执行配置解释该固定提交，而不是任选一个数字。

[任务配置](https://github.com/harbor-framework/terminal-bench/blob/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader/task.toml) · [README](https://github.com/harbor-framework/terminal-bench/blob/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader/README.md)

## 3. 从产物到 reward 的任务内执行路径

1. 构建 agent 镜像时安装固定版本的推理、PDF 和符号计算依赖，并缓存固定模型 revision；复制题目、开发样例和 PDF。
2. agent 在工作目录中写出三个 artifact。
3. 独立 verifier 的 shell 入口运行 pytest，随后根据 pytest 退出码写入二值 reward。
4. pytest 分别检查 PDF 答案抽取、grader 对未公开给 agent 的标签样例的泛化、结果文件完整性及内部一致性。
5. verifier 重新运行提交的 grader，核对所报告的正确性标记和 accuracy；另以固定模型输出抽查作为推理结果真实性的检查。

这条路径揭示三个不同的验收维度：答案抽取是否正确、grader 是否正确、agent 是否按指定协议实际生成了结果。只检查结果 JSON 的 schema，或者只相信 agent 自报 accuracy，都不足以完成该任务的验收。

[agent 环境](https://github.com/harbor-framework/terminal-bench/blob/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader/environment/Dockerfile) · [shell 验收入口](https://github.com/harbor-framework/terminal-bench/blob/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader/tests/test.sh) · [验收实现](https://github.com/harbor-framework/terminal-bench/blob/452bf305c6daa62fc59061d22133a7cbc7c1572e/tasks/math-eval-grader/tests/test_outputs.py)

## 4. 验收环境也要把 agent 产物当成不可信代码

该任务会导入并执行 agent 写出的 Python。因此，“测试在独立容器中运行”并不能自动保证测试数据和 reward 不受产物影响。固定提交采用多层措施：预先把标签加载到 verifier 进程、在标准运行路径移走磁盘上的测试信息、通过输入流仅传递待判定的数据对，并让产物在低权限子进程中运行；reward 目录由更高权限的入口保护。

这是从源码观察到的防护意图和实现，不是对隔离安全性的完整证明。本研究没有执行对抗测试，没有检查 Harbor 如何复制 artifacts，也没有验证内核、容器和宿主机边界。尤其不能把源码注释中“不能作弊”的表述当作经过安全审计的结论。

## 5. 对 benchmark 设计的可迁移启发

- **核对实际产物，而非只核对最终对话。** 文件、状态和可调用程序具有不同验收接口。
- **验收可执行产物需要信任边界。** 产物即使名为 grader，也仍是不可信程序。
- **一致性与真实性不同。** 自报 accuracy 与重算一致，只能证明内部一致；固定输出抽查增加证据，但不是对每一步推理的密码学证明。
- **运行条件属于测量定义。** 模型 revision、浮点格式、生成策略、依赖、时限和 GPU 类型变化，可能改变可复现性。
- **二值 reward 隐藏诊断信息。** 一个总失败可能来自抽取、泛化、推理、格式或环境；分析时应保存各测试的结果，而不只保存最终 0/1。

## 6. 剩余研究边界

下一步可在授权资源内检查 Harbor 的 artifact 传递、独立 verifier 生命周期和 reward 聚合。再下一步才是环境构建与代表性任务运行。本文不会把读取 test code 记作执行验证，也不将这一任务推广为 Terminal-Bench 全部任务都具有同等隔离或同一评分方法。
