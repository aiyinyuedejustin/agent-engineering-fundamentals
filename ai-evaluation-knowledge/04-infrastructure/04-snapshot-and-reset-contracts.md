# 快照恢复不是完整 reset：Firecracker 的状态契约

研究日期：2026-11-06。学习目标：L1 → L3。

证据范围：Firecracker v1.17.0 官方快照文档 D1；本文没有追踪 VMM 的 Rust 实现，没有启动 Firecracker。附属实验只实测当前 Linux 主机的私有文件映射，属于底层机制的狭义 D4，不能把 Firecracker 或任何 benchmark 整体升级为 D4。

固定版本：tag `v1.17.0` 的 annotated tag object 为 `29d66eb25954dbe3608eb91c180a6079f54d2ee8`，实际 commit 为 `95f868c8e345b1cc8faccd1a3c910b4989dc3f58`。以下事实来自该版本的 `docs/snapshotting/snapshot-support.md`，Git blob 为 `8de5ab35d4bc7e9ca43535e5336a7598b3f9e2a1`。[F1]

## 1. 为何评测平台会需要快照

评测重复运行需要“相同初始环境”，但完整启动 OS、安装依赖、打开浏览器、登录模拟网站的成本很高。快照可以复用已准备好的状态。问题在于，**复用得越完整，也越容易把应该独立的状态一起复制。**

这不是说所有容器或云 sandbox 都使用 Firecracker。OSWorld 当前 Docker provider 的 reset 是停止后重建，未实现 `save_state()`，已在前一篇中区分。这里以一个明确实现的 microVM 快照契约理解平台设计。[F1；本目录 02]

## 2. 一个快照至少涉及三组文件

Firecracker 保存 guest memory 与虚拟硬件状态。可恢复的完整集合包括：

1. guest memory file；
2. microVM state file；
3. 零个或多个 disk backing files，由集成者管理。

恢复时还要让对应 TAP 网络设备、vsock backing socket、磁盘文件按所需相对路径可用。Firecracker 不负责打包或管理整个快照生命周期。[F1: Overview、Loading snapshots]

**工程推论：** “快照文件上传完成”如果只指 VM state 文件，不能据此宣布任务环境可重现。应有原子发布的 manifest，将 memory、state、disk、guest kernel、VMM、CPU 模板和外部服务 fixture 作为一个版本集合。校验值、来源认证和访问权限应覆盖所有组成部分，而不是只覆盖一个 archive。

## 3. 文档级时序与一致性边界

官方 API 顺序如下，未在本环境执行：

```text
boot guest → guest completes boot → pause vCPUs
    → create full/diff snapshot → manage disk + memory + state files
    → configure a new Firecracker process's logging/metrics
    → prepare matching host disk/TAP/vsock resources
    → LoadSnapshot before boot → paused restored VM
    → resume → re-establish application connections and validate readiness
```

`Pause`、`Resume`、`CreateSnapshot` 只能用于已启动的 microVM；`LoadSnapshot` 在新 microVM 启动前执行。`LoadSnapshot` 可以通过 `resume_vm` 自动恢复运行。恢复失败会结束当前 Firecracker 进程，因为其状态可能已不可靠。[F1: Snapshot API]

**不能从 pause 推导出的保证：** 暂停 vCPU 并不自动暂停远端数据库、网页服务器或对象存储，也不证明应用已完成事务。若任务访问外部服务，平台需要应用级 quiesce/fixture/reset 协议，或明确接受跨组件状态不一致。这是对文档边界的工程推论，而不是本轮发现的 Firecracker bug。

## 4. COW 提供快速恢复，也增加生命周期约束

File backend 使用 `MAP_PRIVATE` 映射 memory file，按需缺页载入；写入转向匿名 copy-on-write 页。因此启动后并非所有页都已读入，也不是为每个 VM 立即复制完整内存。[F1: Overview]

必须遵守两个约束：

- memory backing file 在整个恢复 VM 生命周期都要保留；不能按“load API 已成功”立即回收。[F1]
- backing file 必须视为不可变。外部修改会改变仍依赖该文件的 guest memory，可能造成未定义行为。[F1: Loading snapshots]

**对评测的推论：** API 恢复时间很短不等于 first observation 或 first action 延迟很短。冷 page cache、远端块存储以及并发缺页可能把成本延后到 trial 内。比较恢复方案时应分别记录 API load、guest ready、task ready、首个 agent action 的时间，并标注宿主缓存是否已热。本文没有测量这些延迟。

最小实测位于 [experiments/private-mapping/README.md](experiments/private-mapping/README.md)。它使用两个真实 `mmap.ACCESS_COPY` 映射验证：一个映射的私有写入不会写回 baseline 或另一个映射；在当前 Linux 上，修改 backing file 仍可影响尚未私有化的映射页。它不模拟 CPU、网络或 VM，也不能替代 Firecracker 恢复实验。

## 5. “相同状态”与“独立 trial”可能矛盾

### 身份与随机数

从同一快照恢复两个 VM，可能复制唯一标识符、已缓存随机数和一次性令牌。VMGenID 会在恢复时变化；支持它的 Linux guest 可以重新播种内核 PRNG，但用户态已缓存的标识符或随机数仍会复制，集成者需另行处理。[F1: Snapshot security and uniqueness]

对评测应分开两种随机性：

- 可控的实验 RNG：任务输入和试验 seed，应该按实验设计固定并记录。
- 必须独立的运行身份：trial ID、临时凭据、服务注册、存储前缀，不能因快照复制而冲突。

不要为追求复现而复用安全令牌，也不要用随机化全部状态来掩盖不确定性。此处是设计建议，不是已审计任何商业平台的声明。

### 时钟

默认恢复的 guest wall clock 从制作快照时继续；应用可能看到过期或错位时间。x86_64 使用 `kvm-clock` 时，`clock_realtime: true` 可在恢复时推进时间，但要求 host Linux ≥5.16，且时间跳变可能影响应用。[F1: Loading snapshots]

评测的 timeout 应使用合适的 monotonic 控制时钟，另外记录 guest wall clock 策略。若任务依赖日期、证书有效期、缓存 TTL 或浏览器 session，应额外检查。不能假定只恢复磁盘和内存就恢复了这些外部时间关系。

### 连接与监控

network/vsock 可能丢包，已有网络连接不保证保留；vsock 的现存连接在恢复后关闭，但 guest 中监听 socket 仍可接受新连接。日志与 metrics 配置不在快照中；MMDS 配置会保存，但其 data store 不保存。[F1]

因此“进程存在”不够作为 ready 条件。恢复后应重建必要连接，重新配置观测系统，检查代理控制链路与任务服务的实际操作。日志缺失是应单独检测的基础设施失败，而不只是模型没有输出。

## 6. 性能优化会改变故障模型

- v1.17.0 的 `sync_snapshot_files` 默认为 true，写回后再返回；设 false 可减少等待，但失去 host crash 后的耐久保证。block device backing files 始终 fsync。[F1]
- diff snapshot 在此版本仍是 developer preview。一般需要按照创建顺序合并到 base，不能把某个 diff 当作独立完整镜像；文档也说明了 booted VM 首个 diff 的例外。[F1]
- dirty-page tracking 有运行开销，并与 huge pages 的收益存在交互。[F1]
- 完整内存快照会消耗磁盘，平台必须考虑失败期间容量并限制用户触发的快照数量/大小。[F1]

**推论：** “速度更快”至少应拆成 create latency、restore latency、trial latency、内存/磁盘占用和故障恢复成本。只报告 API latency 可能把延迟、资源成本或风险移到了另一个阶段。

## 7. bare metal、VM、迁移之间的具体联系

官方契约要求恢复时的软硬件配置与生成时相同。文档给出少量相同 metal 实例型号、从 host kernel 5.10 到 6.1 的已知可行组合，但明确不保证、不推荐将其当生产通用兼容性；例如 m6i.metal/Ice Lake 的快照不能据此推定可在 m5n.metal/Cascade Lake 恢复。[F1: Where can I resume my snapshots?]

这说明 bare metal 是宿主部署与硬件控制方式，不是替代任务级隔离的答案。即使使用 metal host，也仍需确定 guest kernel、CPU feature 模板、镜像、网络和每次 trial 的回收边界。反过来，“同为 x86_64”或“同为云 VM”不足以作为快照可迁移契约。

## 8. 尚未进行的最小 VM 实验

有 KVM、匹配 guest kernel 与 Firecracker 的受控机器上，可做以下实验。当前环境没有 `/dev/kvm`，本轮未执行，也未安装或申请云资源。

1. 用无凭据、无外网的最小 guest，启动后创建 full snapshot。
2. 恢复两个 trial，检查固定文件、实验 RNG、独立 trial ID、wall clock、vsock reconnect。
3. 固定 guest 内容，分别比较 cold/warm host page cache 下 load/ready/first-action latency。
4. 注入控制器崩溃，验证磁盘、TAP、memory backing 引用和 orphan VM 可被回收。
5. 对照 `sync_snapshot_files` 两种设置，先定义 crash-durability 观测方法，不把成功返回直接当作断电后可恢复。

安全边界：不要修改仍被真实恢复 VM 使用的 memory file 来做演示。附属 mmap 实验只操作自己创建的几个页面，并在结束时清理。

## 9. 学习检查

- 能否解释为何两个 clone 的私有写不互相覆盖，却仍必须保护共同 backing file？
- 能否列出 VM state 之外至少五种必须 reset 或重新初始化的状态？
- 如果 load API 延迟降低，而 agent 首步耗时上升，你会怎样定位？
- 如何同时固定实验 seed、保证 trial 身份独立，并避免重复一次性令牌？

## 来源

- [F1] Firecracker v1.17.0，已解析至 commit `95f868c8e345b1cc8faccd1a3c910b4989dc3f58`：[Snapshot support](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/docs/snapshotting/snapshot-support.md)。2026-11-06 阅读完整文档；精确访问时刻未记录。上述 Rust 实现和链接到的其他文档未作为已读源码证据。
