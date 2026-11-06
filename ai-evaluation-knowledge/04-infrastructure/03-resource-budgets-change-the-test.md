# 资源预算不是评测的背景噪声：Terminal-Bench 的真实案例

研究日期：2026-11-06。学习目标：L1 → L3。

证据深度：Anthropic 的实验报告为 D1；Terminal-Bench 的 `bn-fit-modify` 实际任务、Dockerfile、配置、测试脚本和测试代码为 D2；Harbor 的错误政策与单步执行分支达到局部 D3。没有复现该论文/报告的资源实验，不标 D4。

## 1. 一条具体的实验结果

Anthropic 于 2026-02-05 发布的第一方工程报告比较了 Terminal-Bench 2.0 的六组资源配置：从任务声明值同时作为 reservation 与 ceiling，到完全不设上限。在其固定 Claude 模型、harness 和任务集的实验中：[R1]

| 对比 | 报告中的观察 |
|---|---|
| 严格 1× → 不设上限 | 基础设施错误率 5.8% → 0.5% |
| 严格 1× → 3× ceiling | 错误率 5.8% → 2.1%，p < 0.001 |
| 1× → 3× 的成功分变化 | 未达到显著，报告 p = 0.40 |
| 3× → 不设上限 | 错误再少 1.6 个百分点，但成功率增加近 4 个百分点 |
| 1× → 不设上限 | 成功率总差约 6 个百分点，p < 0.01 |
| SWE-bench 扩展实验 | 227 道题，每题 10 samples；RAM 从 1× 到 5×，成功率提高 1.54 个百分点 |

**能够支持的结论**：在该实验条件下，资源和执行策略会改变结果；它们应被当成实验变量公开。

**不能直接支持的结论**：所有 benchmark 都应该使用 3×；所有模型都受同样影响；3× 与 1× 严格等价；任何小于 3 分的领先必定无意义。

尤其要注意：p = 0.40 是“没有在该检验中发现显著差异”，不是等价性证明。报告对非 Claude 模型只给出未经严格检验的趋势观察，对时间段/API 延迟也明确是 anecdotal。不要把这些部分写成普遍已证事实。

## 2. 从 `bn-fit-modify` 任务看资源为何改变策略

本轮读的是 Terminal-Bench 仓库当前固定 commit `fbf8a8c02fd1ef7151b5bbb460baed51c15803dd` 下的 `legacy/bn-fit-modify/`。这与 2026-02 报告中的原始运行快照不是同一已证实版本，以下用于解释机制，不是假定字节一致的复现。

任务要求 agent 从给定 CSV 恢复一个 Bayesian network 的 DAG、做因果干预，并输出结构和采样数据。配置声明：1 CPU、2048 MB RAM、10240 MB storage，agent/verifier 各 3600 秒，允许 Internet。[R2]

Dockerfile 预装 R、Python、编译工具和数学库，但没有把全部 Python data-science stack 预装好；数据来自一个 `main` URL。测试脚本还会在 verifier 阶段安装 uv 和指定版本的 pandas/scipy/pytest。[R3–R5]

Anthropic 报告记录的机制是：某些模型先安装 pandas、networkx、scikit-learn 等较重依赖，在严格内存环境中可能于真正写答案前 OOM；另一种标准库路线开销更低。[R1]

这里至少有四个不同测量对象：

1. 在指定资源限制内完成任务的能力。
2. 借助常见生态工具完成任务的能力。
3. 包安装、网络和平台的可靠性。
4. 验证脚本自身的依赖和计算成本。

如果没有明确目标，资源扩容既可能修复第 3 项噪声，也可能合法地放宽第 1 项题目难度。

## 3. 声明值、请求值和上限不是同一个数

Kubernetes 的主文档说明：[R6]

- CPU request 主要影响调度和资源竞争权重。
- CPU limit 通过限制 CPU 时间、节流来执行，通常不是杀进程。
- Memory request 主要用于调度。
- Memory limit 可能触发 OOM，具体受 cgroup/内核行为影响。
- 内存型 `emptyDir` 的文件也消耗内存预算，而不只是磁盘预算。

因此不能照搬一些工程文章中“超过任何资源上限就 killed”的简写。对 CPU 和 RAM 必须分开描述。

Harbor 当前文档也显式区分：[R7]

| Policy | 语义 |
|---|---|
| `request` | 预留请求，不设硬 ceiling |
| `limit` | 只设硬 ceiling |
| `guarantee` | 请求和硬 ceiling 都有 |
| `auto` | provider 默认行为 |
| `ignore` | 不把该值传给 provider |

同一 task.toml 经 `auto` 跑在两个 provider 上，可以得到不同的有效实验条件。应保存“解析后配置”和运行时实际资源，而不只保存用户输入配置。

## 4. 时间也有多个预算

至少应分别记录：排队、镜像 build/pull、环境启动、setup、agent 执行、模型等待、tool 执行、verifier、artifact 下载、cleanup。

这是由多个项目生命周期归纳出的记录建议，不是某个项目已经统一实现的标准。比如 Harbor 的任务配置独立声明 build/agent/verifier timeout；OSWorld Docker provider 还有独立的 300 秒 ready 等待。[R2, R8]

如果 agent 的 wall-clock budget 包含模型 API 等待，则 API 抖动能改变可完成轮数；如果只算执行时间，则可能遮蔽用户实际等待成本。应提前决定测的是能力、吞吐、交互时延还是完整系统，并据此同时报告必要的时钟。

## 5. 错误分类也会改变分母

Harbor 固定 commit `26f95e0e...` 的 `error_policy.py` 把异常映射成 cause、retry、是否继续 grading 和 reward validity：[R9]

| 情形 | 当前 Harbor 政策 |
|---|---|
| Agent 超时、context/output budget 用完 | 不 retry，仍可 grading，reward 有效 |
| Agent refusal | 不 retry，仍可 grading，reward 有效 |
| Sandbox build/start/OOM 等失败 | 可 retry，不 grading，reward 无效 |
| 可重试的 model API 故障 | 可 retry，可继续 grading，reward 无效 |
| Verifier timeout/reward 解析问题 | 不 retry，reward 无效 |

`SingleStepTrial` 源码表明 agent timeout 可以被记录后仍收集输出并进入 verifier；共享模式与独立 verifier 模式又有不同的停止顺序。[R10]

**需要批判地使用这个政策**：它是框架政策，不是自然定律。如果研究目标本来就包括资源节制，agent 自己造成的 OOM 不一定应当完全从有效样本分母删除。反过来，把不相关的镜像拉取失败算成模型失败也不正确。

报告至少披露 attempted / valid / infra-failed / retried / omitted 的数量，按 task、model、provider 分层，并保留第一次失败记录。只看最终 pass rate 可能掩盖非随机缺失。

## 6. 可以直接执行的实验设计草案

以下是待执行方案，不是已完成实验。

### 设计 A：资源敏感性曲线

- 固定 task revision、image digest、agent/harness/model、prompt、sampling 参数。
- 分别变更 reservation 与 ceiling，不把二者绑成一个 multiplier。
- 选择轻任务、编译任务、统计任务，记录 per-task 曲线，不只报告总平均。
- 在相同任务/种子上配对比较；随机打乱配置运行顺序，降低时间段偏差。
- 记录 OOM、CPU throttling、峰值 RSS、包下载字节、模型等待和工具执行时间。
- 预先定义：何种失败可以重试，重试次数，如何计算分母。
- 若想证明一定范围内等价，事先设定实际等价界值并采用相应检验，不能只凭不显著。

### 设计 B：并发敏感性

- 固定单任务资源，将并发从 1、2、4、8...增加到可承受范围。
- 同时观测宿主 memory pressure、磁盘 I/O、network egress、API 429、启动 P95/P99、agent timeout。
- 计算每个有效完成 trial 的费用，而不是每小时创建的容器数量。
- 若错误显著增加，先确定瓶颈层级，不能笼统说“模型不稳定”。

### 设计 C：verifier 独立性

- 比较 agent 和 verifier 共享环境与独立环境。
- 独立模式只传输出 artifact，预构建 verifier 依赖。
- 验证正确输出在两者中同分，错误输出不能通过。
- 记录新引入的 artifact/schema/版本问题，不把隔离自动视为零代价改进。

## 7. 复现清单

需要保存：任务/数据 revision、镜像 digest、guest/host 架构、runtime 版本、provider/region/instance type、CPU request/limit、RAM request/limit、磁盘类型/容量、GPU 型号、网络策略、timeout 分项、并发、retry policy、失败分母、缓存冷热状态、模型版本和采样设置。

如果只保存 `model=...; dataset=terminal-bench@2.0; score=...`，无法回答资源是否改变了试题。

## 来源

- [R1] Anthropic，2026-02-05：https://www.anthropic.com/research/infrastructure-noise
- [R2] 实际任务配置：https://github.com/harbor-framework/terminal-bench/blob/fbf8a8c02fd1ef7151b5bbb460baed51c15803dd/legacy/bn-fit-modify/task.toml
- [R3] 环境：https://github.com/harbor-framework/terminal-bench/blob/fbf8a8c02fd1ef7151b5bbb460baed51c15803dd/legacy/bn-fit-modify/environment/Dockerfile
- [R4] 测试入口：https://github.com/harbor-framework/terminal-bench/blob/fbf8a8c02fd1ef7151b5bbb460baed51c15803dd/legacy/bn-fit-modify/tests/test.sh
- [R5] 测试逻辑：https://github.com/harbor-framework/terminal-bench/blob/fbf8a8c02fd1ef7151b5bbb460baed51c15803dd/legacy/bn-fit-modify/tests/test_outputs.py
- [R6] Kubernetes resource semantics：https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- [R7] Harbor resources：https://docs.harborframework.com/tasks/resources.md
- [R8] OSWorld provider：https://github.com/xlang-ai/OSWorld-V2/blob/3d778a3c9a34a079316f70df023b166700445792/desktop_env/providers/docker/provider.py
- [R9] Harbor error policy：https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/models/trial/error_policy.py
- [R10] Harbor single-step flow：https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/single_step.py
