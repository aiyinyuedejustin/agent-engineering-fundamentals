# KernelBench：硬件、计时与清理会直接改变测量对象

研究日期：2026-11-06。学习目标：L2 → L3。

范围与深度：真实矩阵乘法任务、批处理配置、GPU 调度、correctness → timing → cleanup 路径已读，相关子系统达到 D3。一个 cache cleanup 源码函数在临时目录中实测，只有该函数为狭义 D4。**没有运行 CUDA kernel、没有复现模型分数、没有使用 Modal 或付费 GPU。**

固定版本：`ScalingIntelligence/KernelBench` commit `423217d9fda91e0c2d67e4a43bf62f96f6d104f1`，2026-11-06 通过 GitHub API 读取的 main snapshot，commit 日期为 2026-03-05。README 称 main 为最新稳定分支，但同一快照 `pyproject.toml` 标注 `0.2.0.dev0`，不能只记一个含糊的“最新版”。[G1、G2]

## 1. 真实任务而不是抽象“跑 GPU”

读取任务 `KernelBench/level1/1_Square_matrix_multiplication_.py`：

- reference 为 `torch.matmul(A, B)`；
- `N = 2048 * 2`，输入为两个随机 `4096 × 4096` tensor；
- 无特殊模型初始化参数；
- 默认 fp32 时每个输入仅数据部分约 64 MiB，两个输入加一个输出约 192 MiB。这只是尺寸推算，不是峰值显存实测，未含 clone、allocator、模型、编译与 timing buffer。[G3]

任务要求生成与 reference 一致且更快的实现。`fast_p` 同时要求正确性与相对速度。因而硬件、reference 版本、精度、计时方法和输入分布都是题目的一部分，不能看成“可随意替换的后端”。[G1]

## 2. 核心架构与调用时序

```text
生成代码（可以先离线完成）
  → 选择 problem / sample / device
  → optional CPU compilation cache
  → worker loads reference and candidate Python code
  → compile / initialize / move to selected GPU
  → randomized correctness trials
  → if correct, performance trials using selected timing method
  → optional excessive-speedup heuristic
  → record metadata and aggregate results
  → cleanup caches / retire failed process or container as applicable
```

`scripts/eval_from_generations.py` 默认 local、一个 GPU、timeout 180 秒、5 次 correctness、100 次 performance、fp32、`cuda_event`。library 函数自身的默认值不同，例如 correctness=1、performance=10、measure_performance=false。**报告脚本配置与调用参数，不能仅抄函数默认值。**[G4、G5]

local 批处理每批最多 `num_gpu_devices` 个样本，按 `cuda:i` 分配；共享一个 batch timeout，按剩余墙钟时间取结果。超时与多进程错误产生失败结果，并触发 cache cleanup。源码不因此证明整台宿主 GPU 独占：library 中检查 device busy 仍是 TODO。[G4:L570–706；G5:L429]

Modal 批处理会按 `config.gpu` 调整 evaluator class 的 GPU 选项，等待 GPU attach；特定 GPU error 会调用 experimental `stop_fetching_inputs()` 退休 container，避免继续接单。此处是所读 wrapper 的行为，不代表我们验证了云端恢复保证，也不应把 `empty_cache()` 当成完整 GPU reset。[G4:L163–253、L480–507]

## 3. correctness 与 performance 的“多次”不是同一含义

correctness 路径按初始 seed 派生多个 trial seed，每次重新产生输入，检查 shape 与 `torch.allclose`；容差由精度决定。[G5:L727–848]

performance 路径只在 timing 调用前生成一次 inputs，然后 timing loop 反复调用同一个函数和这组 inputs。**100 次 timing 不等于测试 100 组新输入。** cache、对象身份或有状态 candidate 因而需要独立审计。这里描述实现，不把这种 microbenchmark 设计本身判定为错误。[G5:L607–637；G6]

candidate Python 通过 `exec` 或临时 module import 执行。library 本身不是一个防恶意代码的 sandbox。正确性与性能测量代码也处在可被 Python candidate 影响的环境中；官方 EVAL 指南承认 reward-hacking 防护仍在发展，要求独立验证异常速度结果。[G5:L124–207；G7]

**工程建议：** 运行不可信生成代码时，应在外层提供资源、文件、网络、凭据和设备隔离；reference/结果的可信边界另行设计。不要把“独立 Python process”直接等同于安全执行环境。

## 4. 计时方法实际测到了什么

### CUDA events

源码先 warmup，清 PyTorch allocator cache；每轮 synchronize，创建 events，用大 tensor 写入扰动 L2，再在当前 stream 记录 start/end，调用 candidate，最后 synchronize 所有 streams 并读取两个 events 的 elapsed time。[G6:L201–281]

重要区别：**等待所有 streams 完成，不会自动使两个当前 stream events 覆盖其他 stream 上的全部工作。** 源码注释明确承认当前方法尚未防御额外 CUDA stream 情况。本文没有运行 adversarial kernel。[G6:L261–269]

### Host wall time

host-time 路径用 `perf_counter` 夹住 candidate 与末尾 device synchronize，测量包含 Python、launch、同步以及所有 stream 完成等待的端到端延迟。它与 CUDA event 时间不是同一种指标。[G6:L433–500]

还有一个待验证的细节：该路径在 L2 扰动操作后、CPU timer 前没有额外 synchronize。因为 GPU 操作可能异步，扰动工作的剩余成本可能落入计时区间。这是**基于调用顺序的待验证推论**，不是本轮已测得的误差或性能 bug。需要真实 GPU timeline/对照实验确认。

### Triton 与 profiler

`do_bench` interface 将外部 `num_warmup/num_trials` 视为未使用参数，内部采用时间预算；`do_bench_impl` 则按指定次数运行。`nsight_python_time` 是另一条实验路径，不应把所有 backend 返回的 trial 数当作相同设计。[G6:L284–430、L502 起]

因此结果至少记录 timing method、warmup、discard-first、实际 trials、cache 策略、precision 和设备信息。此快照 `get_timing_stats` 把 mean/std/min/max 格式化到三位有效数字，做接近 1× 阈值的比较时还要考虑精度与测量波动。[G6:L602–625]

## 5. “同型号 GPU”也不构成同一 baseline

仓库 baseline README 记录已有 baseline 使用 PyTorch `2.5.0+cu124`、CUDA 12.4，而同一代码快照 pyproject 要求 torch≥2.9.0、Python==3.10.*。README 明确建议在自己的 cluster 重测 baseline，因为 GPU、电源设置和软件版本会改变 timing。[G2、G8]

baseline JSON 用于部分离线分析；`eval_kernel_against_ref` 本身不会读取这些 JSON。某些 single-run workflow 现场测 reference；另一些分析消费历史 baseline。不能混用旧 numerator 与新 denominator 后仍称同条件 speedup。[G8]

baseline 表甚至列出同类 L40S 在不同 provider 的 300W/350W 配置，以及 H100 PCIe 与其他 H100 配置。本文不比较这些 provider 的优劣，也没有实测差值。它说明只记录 GPU marketing name 会遗漏条件。[G8]

## 6. GPU sharing 是另一个隔离维度

NVIDIA 官方 MIG 文档区分 GPU Instance (GI) 与 Compute Instance (CI)：GI 划分内存资源并提供 memory QoS；同一 GI 内的多个 CI 仍共享内存与部分 engines，仅计算 slices 被细分。MPS 也不是同样的物理内存带宽分区机制。[G9]

MIG 可以部署在 bare-metal/container、GPU passthrough VM 或支持的 vGPU 配置中。这再次说明：**裸金属/VM 是宿主部署轴，MIG/MPS/整卡是设备分配轴，容器/VM runtime 是执行隔离轴。** 三者不能互相代替。[G10]

对 kernel performance 评测需额外记录：

- 完整 device model、驱动、CUDA/ROCm、framework/compiler 和 power/clock 条件；
- 是整卡、MIG GI/CI profile、MPS，还是其他分时共享；
- device memory、L2、SM 与带宽的实际分配；
- 是否同时存在其他进程，以及编译与测量是否竞争 CPU/IO；
- profiler、P2P、IPC、collective 功能是否受该配置限制。

这些是建议记录的实验条件，不代表本轮检查了每一家 cloud provider 的分配实现。MIG 功能/枚举/互通限制随 GPU 和驱动版本变化；不要把某份硬件表推广成永久规则。变更 MIG 模式还可能重置 GPU 或需要管理权限，**本研究未执行这些变更**。[G9、G10]

## 7. 实测发现：局部失败清理可能影响其他样本

固定 `eval_from_generations.py` 中的 `remove_cache_dir(cache_dir, run_name, problem_id, sample_id)`：

1. 计算 `cache_dir/run_name/problem_id/sample_id`；
2. 但判断与 `shutil.rmtree` 使用的是 `cache_dir`，不是计算出的 per-sample path。[G4:L420–436]

本研究执行了这一**未修改的 AST 函数片段**，只传入新建临时目录中的合成 fixture：请求清理 run-A/problem-1 时，run-A/problem-2、run-B 和 cache 根都消失；cache 之外的对照文件保留。[G11]

这是实际 filesystem 行为的狭义 D4。没有 import 整个模块，没有载入 PyTorch/Modal，没有执行模型生成代码，也没有删任何真实 cache。

**意义及边界：** 证据证明这个固定函数的删除范围。批处理 timeout/error 路径会调用它，因而共享该 cache root 时可能影响其他任务的编译缓存与后续测量条件；但本轮没有并发 GPU 重现，不能声称已量化某次 benchmark 分数影响。没有向上游提交 issue 或修改上游代码。

## 8. 最小 GPU 实验计划，尚未执行

当前能力检查于 `2026-11-06T02:53:14Z` 实际执行：无 `nvidia-smi` 命令、无 `/dev/nvidia0`、Python 未安装 torch。因此不安装依赖、不申请 GPU，以 source trace 与安全的 cache 片段实验继续。

下一阶段在已授权 GPU 上：

1. 固定该矩阵任务与安全 reference candidate，保存精度/编译/硬件 manifest；reference-vs-reference 应近似 1×，但不能要求每次精确 1。
2. 同机、同轮交错测 reference/candidate，避免只用历史 baseline；报告分布而非只有均值。
3. 分别用 CUDA events 与 host-time，验证指标差别；另设受控多-stream 正确程序检查覆盖范围。
4. 比较固定输入与每轮新输入、cold/warm cache、独占与已知共享模式，不把条件变化混成同一排行榜。
5. 注入安全的 compilation failure 与 timeout，验证其他 sample cache 未受影响；区分基础设施失败、编译失败和正确性失败。

## 9. 学习检查

- 为什么 CUDA synchronize 与 CUDA events 不能互相替代？
- fast_1 的 numerator 和 denominator 必须对齐哪些条件？
- 为什么 cache cleanup bug 既是可靠性问题，也是评测有效性问题？
- 一个 1g MIG 设备和完整 GPU 跑同一 shape，哪些结果可比较，哪些不能直接合并？

## 来源

代码均固定 `423217d9fda91e0c2d67e4a43bf62f96f6d104f1`，2026-11-06 阅读；精确单次读取时刻未记录。

- [G1] [README](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/README.md)，任务与 metric 定义、baseline 建议。
- [G2] [pyproject.toml](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/pyproject.toml)，版本、Python、依赖。
- [G3] [Square matrix multiplication task](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/KernelBench/level1/1_Square_matrix_multiplication_.py)，全文。
- [G4] [eval_from_generations.py](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/scripts/eval_from_generations.py)，读取 config、Modal class、local worker、batch timeout、cache cleanup；没有把 pass@k 分析尾段纳入已追踪范围。
- [G5] [eval.py](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/src/kernelbench/eval.py)，读取 load、cleanup、eval_kernel_against_ref、run_and_check_correctness 路径；未审计所有 backend 编译器。
- [G6] [timing.py](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/src/kernelbench/timing.py)，相关 timing methods、cache helper、stats。
- [G7] [EVAL.md](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/EVAL.md)，全文；WIP 防护与异常速度独立验证建议。
- [G8] [Baseline timing README](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/results/timing/README.md)，全文。
- [G9] NVIDIA [MIG Concepts](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/concepts.html)，D1，可变 latest 文档，2026-11-06 阅读。
- [G10] NVIDIA [MIG Deployment Considerations](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/deployment-considerations.html)，D1，可变 latest 文档，2026-11-06 阅读。
- [G11] 本地 [cache-scope 实验](experiments/kernelbench-cache-scope/README.md)，精确源码 blob、步骤、输出和 D4 边界。
