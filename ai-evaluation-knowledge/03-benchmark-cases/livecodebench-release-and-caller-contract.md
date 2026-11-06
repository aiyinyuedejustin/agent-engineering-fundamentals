# LiveCodeBench：动态数据不免除版本与调用契约

更新日期：2026-11-06。整体深度保守为 **D1**：官方文档及固定源码已读，已追踪路由、评测与聚合路径，但未完成真实数据条目的独立读取。另有一个 **评分调用方组件 D4** 实验，不是完整 benchmark 复现。

固定仓库 `LiveCodeBench/LiveCodeBench`，提交 `28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24`，2025-07-16。本次没有加载数据脚本、反序列化压缩测试、执行候选代码或调用模型。

[固定版本](https://github.com/LiveCodeBench/LiveCodeBench/tree/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24)

## 1. 动态发布解决的是一类污染风险，不是污染绝对为零的证明

项目通过收集不同时间发布的竞赛题，允许按时间窗口评估。固定 README 已列出多个 release，CLI 又默认 `release_latest`。所以“LiveCodeBench 分数”至少还需要 release、起止日期、实际问题 ID 集合、数据 revision，以及模型版本和被声称的训练截止时间。

即使题目发布晚于某个训练截止时间，也仍需检查模型更新、题目复用、评测期数据泄露和其他接触路径。这里是测量设计上的限制分析，不是对某个模型污染的指控。“contamination-free”作为项目标题不应被扩写为已审计每个模型的训练数据。

[README 与 release 说明](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/README.md) · [CLI 默认参数](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/runner/parser.py)

## 2. scenario 与 fast/full 路径改变了被测工作

code generation、自修复、代码执行预测和测试输出预测是不同 scenario。某个 scenario 得分不能泛指整个项目的综合能力。

在所读提交中，普通 code generation 默认加载裁剪过测试集的 lite 数据，并可在加载时筛选日期。`--not_fast` 转向另一个数据源。需要注意，full loader 虽接受 release 参数，但函数体没有把它传给数据加载调用；路由也没有向它传递同样的日期过滤条件。因此不能只相信两个命令行参数长得相似，就认定 fast/full 的题目集合完全相同。

这是静态源码观察，尚未在当前远端数据加载器上实测。实际运行应在两条路径开始前导出问题 ID、测试数量和版本信息，再判断是否属于仅测试量不同的可比实验。

[scenario 路由](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/runner/scenario_router.py) · [数据对象与加载器](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/benchmarks/code_generation.py)

## 3. 代码成功如何变成 pass@k

每个问题有多个生成结果；每个生成结果又有若干测试结果。聚合实现先检查一份生成的所有测试值是否大于零，再将该问题成功生成数 c 和总生成数 n 输入 pass@k 估计器。

主 `compute_metrics_from_results` 路径只在所有问题都满足 n≥k 时输出该 k。这个输入域条件很重要：仅有十次样本，并不足以通过该无偏估计方法报告 pass@25。

[运行测试与候选聚合](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation/compute_code_generation_metrics.py) · [pass@k 实现](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation/pass_k_utils.py)

## 4. 辅助汇总脚本缺少同一输入域保护：已做局部实验

固定 `compute_scores.py` 在打印日期窗口成绩时遍历多个 k，但没有复制主路径的 n≥k 检查。原创实验构造三个任务，每个有十个全部失败的历史 grade，直接执行从固定源码提取的 `compute_scores` 函数。

观察结果：pass@1、5、10 打印为0，pass@25及更大 k 打印为1。相同合成 grade 走主 `compute_metrics_from_results` 则只输出1、5、10三个有效 k，均为0。

这不是模型在较大预算突然达到100%，而是把估计器用于不支持的输入域后出现的数值。实验确认辅助调用路径的风险；没有核查任何已发布 leaderboard 是否使用该脚本或引用了无效的 k，因此不能借此否定其公开成绩。

[辅助汇总源码](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation/compute_scores.py) · [原创实验程序](livecodebench_k_guard_probe.py) · [运行输出及源文件 SHA-256](livecodebench-k-guard-probe-output.json)

## 5. 工程边界

执行器区分函数调用与 stdin/stdout 风格，并有逐例时限和进程外层时限。输出比较、超时、运行错误及框架异常会影响结果，需要保存细分元数据。项目也明确提醒 `reliability_guard` 不是安全沙箱；不能因为名字含 guard 就在有敏感文件或权限的工作环境直接执行模型代码。

固定代码中 guard 支持可选 memory limit，但该调用点未传入值。注释中写有内存限制并不等于该路径实际设置了限制。对环境保证应检查配置与系统状态，不能只读取附近注释。

[具体测试实现](https://github.com/LiveCodeBench/LiveCodeBench/blob/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation/testing_util.py)

## 6. 后续可执行但本次未做的工作

在独立、安全环境内读取固定 release 的真实题目和测试；导出 fast/full 的 task manifest；验证日期过滤；对合法样本范围运行评分回归；然后才开展模型推理或完整复现。数据页当前 viewer 因自定义加载脚本不可用，本研究没有因此启用未审查的远程代码。
