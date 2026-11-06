# 评测基础设施：不要把部署地点、运行时和隔离边界混成一件事

研究日期：2026-11-06。第一轮文档证据已闭合；本页的机制解释为 D1，学习目标为 L1 → L2。没有完成实机安全验证。

## 1. 一个必须先拆开的错误分类

“裸机、虚拟机、Docker、Kubernetes、云沙箱”不是互斥的五种选项。实际运行可能是：云上的物理主机 → 云虚拟机 → Kubernetes Pod → Docker 容器 → QEMU 客体操作系统。也可能是 Kubernetes 用 gVisor 执行容器，完全没有传统完整客体操作系统。

应当分别回答五个问题：

| 轴 | 要回答的问题 | 对评测的直接影响 |
|---|---|---|
| 主机部署 | 自有裸机、桌面、云 VM、专用宿主机？ | 硬件、虚拟化能力、租户干扰、计费、配额 |
| 工作负载封装 | 普通进程、OCI 镜像、完整 OS 镜像？ | 依赖可移植性、桌面/内核语义、恢复方式 |
| 隔离边界 | 同一用户进程、共享内核容器、用户态内核、虚拟机？ | 不可信代码能触达什么系统接口 |
| 编排控制 | 单机脚本、Compose、Kubernetes、托管 API？ | 排队、并发、健康检查、失败恢复、清理 |
| 测量契约 | CPU/内存/网络/时间限制如何真正执行？ | 分数是否可比较、超时与失败如何归因 |

这套五轴划分是本研究的归纳，不是某一个项目的官方术语。它的价值在于避免“用了 Docker 所以没有虚拟化”“用了 K8s 所以隔离更强”等错误推断。

## 2. 从真实项目反推选择

### SWE-bench：封装仓库状态和测试依赖

官方 harness 文档描述 base → environment → instance 三层镜像，以复用语言工具链、仓库依赖和实例状态。[I02] 但当前源码已把镜像构建放进独立 image_builder，并在评测执行端消费预构建的实例镜像。本例说明：**构建系统、agent 运行环境、最终评分容器可以是不同系统**。不要只看仓库 README 就假设一套容器包办全部流程。

### OSWorld V2：Docker 中托管的是 VM

V2.1 Docker provider 把 QCOW2 系统盘挂到运行时容器中，发现 `/dev/kvm` 时启用硬件加速，未发现时写入 `KVM=N`。它不是把一个普通 Linux GUI 进程直接放进应用容器。VM 的快照/重建、客体文件系统和控制接口都是评测协议的一部分。[I01a–c]

### Inspect：创建 sandbox 不会自动把 Python harness 隔离进去

Inspect 的工具函数、solver、scorer 仍运行于评测主进程；只有通过 `sandbox()` 接口发出的操作才在 sandbox 里执行。[I03] 因此“Task 声明 sandbox”不等于任意自定义工具都安全。自定义工具如果直接调用本机 shell，仍可能操作控制主机。

### Inspect Kubernetes：扩容和安全控制是可组合能力

K8s 插件让 agent 交互的容器进入集群，Inspect 进程仍可在本地。官方默认 Helm chart 使用 gVisor，并通过 Cilium 控制网络。[I04a] Kubernetes 本身不是某种单一沙箱实现；实际安全边界取决于 runtime、准入策略、网络插件、挂载和身份。

### Harbor：统一接口不保证统一资源语义

Harbor 的 CPU/内存策略区分 `limit`、`request`、`guarantee`、`auto`、`ignore`。不同 provider 支持的策略不同，storage/GPU/TPU 还依赖 provider 能力。[I05a] 相同 `cpus=2` 不能单独证明两个 provider 给出的实验条件相同。

## 3. 隔离并不是一个“强弱”总分

| 机制 | 主要提供什么 | 不应自动推断什么 |
|---|---|---|
| 普通进程/本地执行 | 低开销、容易调试 | 没有因名字叫 environment 就产生隔离 |
| 普通容器 | 命名空间、文件系统视图、资源控制等 | 通常共享主机内核；镜像可复现不等于能抵御不可信代码 |
| gVisor | 在 Sentry 中重实现系统 API，减少直接触达宿主内核的接口 | 不是全部 Linux 功能；不能单独替代网络策略或主机资源限额 |
| 完整 VM / microVM | 客体内核与虚拟硬件边界 | 不保证无侧信道、不保证网络隔离、不保证控制接口安全 |
| 专用裸机 | 可以减少与其他租户共享硬件 | 若直接执行不可信代码，依然需要权限、网络与恢复边界 |

gVisor 官方明确把安全、性能和兼容性当作不同权衡，并不主张只因用了虚拟化硬件就能判断谁更安全。它还依赖宿主 cgroups 对抗资源耗尽，依赖外部网络策略约束连接。[I06a]

对于 agent 评测，应额外问：**边界保护的是宿主、其他样本、评分器、答案、凭据，还是外部世界？** 一个设计可能保护宿主却让 agent 改写评分文件，也可能隔离文件系统但允许从网络找到参考答案。

## 4. 更安全的环境可能改变试题

Inspect K8s 文档记录 gVisor 会限制部分低层 syscall/网络操作，并可能让某些 cybersecurity 任务更难或不可解。[I04b] 这是测量有效性问题，而不仅是“兼容性 bug”。

可接受的处理方式不是默认关闭安全控制。先确认任务真正需要什么，建立精确的测试环境，限定网络和目标，再决定哪些能力必须提供。对比结果时披露运行时及必要例外。

同理，CPU 节流、OOM、DNS 限制、不能访问软件包仓库，都可能改变 agent 的可行策略集合。若目标是测“受限机器上的能力”，限制是题目的一部分；若目标是跨模型比较，则必须使限制可比。

## 5. Kubernetes 的几个隐藏控制面

- **ServiceAccount**：Pod 中默认 token 自动挂载可能把执行环境变成 Kubernetes API 客户端。Inspect 的内置 chart 默认关闭自动挂载；需要 API 时应使用最小权限专用身份。[I04c]
- **RBAC 不是 Pod 安全性**：能创建 Pod 的身份可能请求 privileged、hostPath 或 host namespace；还需要 admission policy。[I04c]
- **DNS 也是出口**：仅阻断 HTTP 不等于阻断数据外泄。Inspect 的 Cilium/CoreDNS 设计同时约束可查询域名。[I04d]
- **禁用策略意味着什么**：`networkPolicy.enabled=false` 时 chart 自己不再约束网络，必须由集群/runtime 负责。不能保留“默认隔离”的心理模型。[I04d]
- **编排吞吐不等于执行吞吐**：Helm install、Helm uninstall、Pod exec/file I/O、模型 API 并发都是不同队列。[I04e]

## 6. 最低可用的选型流程

1. 写出任务真实依赖：完整桌面、浏览器、特定内核、GPU、多容器、外网、持久连接。
2. 写出威胁模型：只防误操作，还是把 agent 产出的代码和任务文件都视为不可信。
3. 优先使用 benchmark 官方支持、版本明确的 provider，先做少量健康检查和正/负对照。
4. 明确 resources 的 reservation、ceiling、超时和网络策略，不只记录抽象配置数值。
5. 证实 reset 清除了 agent 状态，同时没有破坏任务需要的外部状态。
6. 再增加并发，观察错误率、尾延迟、OOM、CPU throttling、清理滞留和单位有效样本成本。

这是工程建议，不是已运行结果。下一步 D4 必须包括真实环境中的健康检查、权限测试、清理验证和评分对照。

## 主要来源

- [I01a] OSWorld V2.1 Docker provider，固定代码：https://github.com/xlang-ai/OSWorld-V2/blob/3d778a3c9a34a079316f70df023b166700445792/desktop_env/providers/docker/provider.py
- [I01b] OSWorld V2.1 manifest：https://github.com/xlang-ai/OSWorld-V2/blob/osworld-v2.1/benchmark_releases/osworld-v2.1.json
- [I01c] Linux nested KVM：https://docs.kernel.org/virt/kvm/x86/running-nested-guests.html
- [I02] SWE-bench harness 文档：https://www.swebench.com/SWE-bench/reference/harness/
- [I03] Inspect sandbox 文档：https://inspect.aisi.org.uk/sandboxing.html
- [I04a] Inspect K8s 总览：https://k8s-sandbox.aisi.org.uk/
- [I04b] Runtime：https://k8s-sandbox.aisi.org.uk/security/container-runtime/
- [I04c] Workloads：https://k8s-sandbox.aisi.org.uk/security/kubernetes-workloads/
- [I04d] Network：https://k8s-sandbox.aisi.org.uk/security/network-access/
- [I04e] Concurrency：https://k8s-sandbox.aisi.org.uk/tips/concurrency/
- [I05a] Harbor resource policies：https://docs.harborframework.com/tasks/resources.md
- [I06a] gVisor security model：https://gvisor.dev/docs/architecture_guide/security/

除标明固定代码的链接外，其余多为可变文档；本页反映 2026-11-06 读取内容，不能代替锁定依赖和实际配置。
