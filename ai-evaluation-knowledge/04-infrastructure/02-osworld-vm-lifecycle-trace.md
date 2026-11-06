# OSWorld V2.1：Docker 背后的 VM 生命周期

研究日期：2026-11-06。学习目标：L2 → L3。

证据深度必须分范围说：release manifest、provider 和 DesktopEnv 生命周期达到源码路径追踪 D3；V2.1 官方完整任务集没有下载、没有执行。完整 benchmark 复现不达到 D4。任务类位于 gated Hugging Face 数据集，本轮未请求其权限。

## 1. 锁定版本，而不是只记住“OSWorld”

固定版本：`osworld-v2.1`，Git tag 实际指向 `3d778a3c9a34a079316f70df023b166700445792`，于 2026-11-06 通过 GitHub ref API 读取。

读取的主要文件：

- `desktop_env/desktop_env.py`
- `desktop_env/providers/docker/provider.py`
- `desktop_env/providers/docker/manager.py`
- `benchmark_releases/osworld-v2.1.json`

manifest 中的 `osworld_code.base_commit` 是 `325ab352...`，不应把这个字段误写成已解析的 tag tip。它们是不同字段。

V2.1 把代码、Python 任务类、完整 gated assets、匿名可读 public assets、mocked websites 和 provider images 分开固定。**只锁 Git commit 仍不足以重建实验。** README 的历史发布段落仍保留旧推荐，而顶部更新与版本表推荐 V2.1；本研究按明确最新发布段落与 manifest 对齐，不把历史文本当成冲突的两个现行推荐。

## 2. 从初始化走到可观察的桌面

下面是所读固定源码的调用顺序，不是运行日志：

1. `DesktopEnv.__init__` 调用 `create_vm_manager_and_provider(...)`，按 provider 建立 manager/provider。
2. Docker/AWS 等新建型 provider 初始标记为 clean；VMware/VirtualBox 标记为 used，随后需要恢复。
3. 若未指定 VM 路径，则 manager 选择系统盘。Docker manager 使用固定 Hugging Face revision 的 QCOW2 ZIP URL；本地目标盘已存在就直接复用。
4. `_prepare_volume()` 记录用户要求的磁盘大小；`_start_emulator()` 调用 provider。
5. Docker provider 持有一个端口分配文件锁，分配 VNC、控制 API、Chrome 和 VLC 端口。
6. provider 检查 `/dev/kvm`。有则传入 device；无则设置 `KVM=N` 并记录慢速运行警告。
7. 容器从固定 digest 的 `happysixd/osworld-docker` 启动，挂载只读 `/System.qcow2`，添加 `NET_ADMIN`，映射四类端口。
8. `_wait_for_vm_ready()` 最长 300 秒轮询截图 endpoint，HTTP 200 即被视为 VM ready。
9. `DesktopEnv` 从 provider 返回值解析地址/端口，创建 `PythonController` 和 `SetupController`，需要时扩展 guest volume。
10. `_get_obs()` 返回 screenshot，可选 accessibility tree、terminal output，以及 instruction。

### 从源码得到的三个边界

- Docker 能启动并不等于 guest OS 已 ready；当前 provider 使用截图 API 作 readiness 门槛。
- 截图成功不证明应用、任务服务、网络和评估器都 ready，任务 setup 还要继续执行。
- 文件名含有 `snapshot` 不说明底层真的保存/恢复内存快照。本 provider 的 `save_state()` 是 `NotImplementedError`，`revert_to_snapshot()` 实际停止容器；后续启动重新创建 VM。

## 3. reset 是状态机，不是删除一个目录

`reset()` 的主要路径：

1. 重置 trajectory/step/action history。
2. 最多尝试 5 次任务 setup。
3. 若 `is_environment_used` 为真，调用 `_revert_to_snapshot()`，再 `_start_emulator()`。
4. 有 task 时，在任何 task-specific setup 前先标 dirty。
5. 检查 proxy/控制服务可用性，设置 task 信息和缓存目录，应用 runtime overrides。
6. 执行 task 自定义 setup 或配置 setup；失败等待并重试。
7. 最终失败抛 `EnvironmentSetupError`；成功后返回第一帧 observation。

**提前标 dirty 是一个很具体的正确性机制。** 如果 setup 写了一半文件后失败，而框架仍认为环境 clean，下一次 retry 就不再是同一初始状态。

`step()` 也将环境标 dirty，记录 action，执行 controller 动作，再等待和采集 observation。`evaluate()` 可以调用 task 自定义 evaluate；不是所有 V2 任务都走旧的 evaluator 字典分支。

## 4. 与云、裸机、嵌套虚拟化的关系

Linux KVM 文档区分 L0 宿主、L1 guest hypervisor、L2 nested guest。[S4] 此处 L0/L1/L2 是 Linux 的虚拟化层级，不是本知识库的学习等级。

在云 VM 内运行 Docker，再由 Docker 内 QEMU 启动 OSWorld guest，可能需要云 VM 暴露硬件虚拟化功能。把 `/dev/kvm` 映射进容器只解决设备暴露，不自动解决上层云的嵌套虚拟化支持。

源码存在无 KVM 的慢速分支，**不意味着这种分支已被 benchmark 验证为时间预算等价**。Linux 官方文档也提醒，要分清 QEMU 纯软件仿真 TCG 和 KVM-on-KVM。

实际选型应先列：宿主 CPU 架构、KVM 是否可访问、L0/L1 内核和 QEMU、provider image、guest 分辨率、RAM/vCPU、网络条件，再谈并发数量。

## 5. manifest 公开承认的验证边界

这些是上游 release manifest 的记录，不是本研究自行复现实验：

- Docker archive 的字节数、SHA256 和 runtime digest 已验证，但 VM 未 boot，原因是缺少 KVM。
- AWS/Docker guest 等价性未建立。
- 未完成全量 108-task agent evaluation。
- mocked website 的源代码及 submodule 已检查，但没有部署验证。
- 未修改的 Task029 仍存在 120 秒 HTTP-server setup timeout；另行测试的修复不在该 release 内。

这比“官方发布所以完全复现”更准确，也说明一次 release-validation 应分别记录 bytes、boot、service-ready、task-setup、oracle、full-run 等等级。

## 6. 本轮发现、但未用实验确认的问题

### 6.1 有 checksum manifest 不等于下载路径执行 checksum 校验

在所读 Docker manager 中，下载/复用路径以目标文件是否存在为重要条件，代码未见读取 release manifest 并核对 SHA256 的步骤。结论仅限这个文件路径，不代表项目所有下载工具都没有校验。

工程建议：实验入口显式验证实际 QCOW2 和 runtime digest。缓存目录存在但内容来自旧 release，会造成“代码正确、磁盘错误”。

### 6.2 端口分配检查存在作用域

provider 在同一主机的文件锁下检查系统和运行中 Docker 容器端口，再启动容器。这降低同一实现的冲突，但不是全局分布式端口分配器；其他不遵守锁的进程仍可能同时占用端口。未复现竞争，不声称存在已证实 bug。

### 6.3 控制接口必须加入威胁模型

provider 明确映射桌面控制和浏览器调试端口。源码未为端口指定 host bind 地址。应检查最终绑定、宿主防火墙和云安全组，不能因 guest 镜像是只读就认为控制面不可外部触达。本研究没有扫描任何真实部署。

### 6.4 reset 不一定重置外部网站

guest 重建只证明 guest 侧回到初始盘状态，不能单独证明远端 mocked web、GitLab 数据库、用户账号、缓存和 DNS 回到初态。需要检查任务 setup 对外部状态的处理。此项因 gated 任务未读，明确留作后续验证。

## 7. 最小复现前检查表

| 检查 | 证据应是什么 | 本轮状态 |
|---|---|---|
| 代码和数据版本 | tag → commit；tasks/assets/website manifest | 已读 manifest |
| 镜像完整性 | 实际文件 hash + runtime digest | 未下载镜像 |
| 主机能力 | KVM 可访问、嵌套支持、架构 | 本工作环境未发现 Docker 命令或 `/dev/kvm` |
| Guest boot | 启动日志、guest OS/分辨率、截图 | 未运行 |
| Task setup | 初始状态断言和 setup log | 未运行 |
| 正负对照 | oracle 能过、空/错误行为不能过 | 未运行 |
| Reset | 跨 trial 状态泄露测试 | 未运行 |
| Cleanup | VM/容器/volume/端口全部回收 | 未运行 |
| Comparable run | 固定模型、harness、limits、任务与错误政策 | 未运行 |

2026-11-06 02:28:01 UTC 的只读能力检查：`command -v docker` 无输出；`/dev/kvm` 不存在；宿主报告 x86_64 Linux。这只是本工作容器的能力探测，不是 OSWorld D4。没有安装软件、改安全配置或产生云费用。

## 来源

- [S1] DesktopEnv：https://github.com/xlang-ai/OSWorld-V2/blob/3d778a3c9a34a079316f70df023b166700445792/desktop_env/desktop_env.py
- [S2] Docker provider：https://github.com/xlang-ai/OSWorld-V2/blob/3d778a3c9a34a079316f70df023b166700445792/desktop_env/providers/docker/provider.py
- [S3] Docker manager：https://github.com/xlang-ai/OSWorld-V2/blob/3d778a3c9a34a079316f70df023b166700445792/desktop_env/providers/docker/manager.py
- [S4] Linux nested KVM：https://docs.kernel.org/virt/kvm/x86/running-nested-guests.html
- [S5] Release manifest：https://github.com/xlang-ai/OSWorld-V2/blob/3d778a3c9a34a079316f70df023b166700445792/benchmark_releases/osworld-v2.1.json
- [S6] README，读取时的现行与历史说明：https://github.com/xlang-ai/OSWorld-V2/blob/main/README.md
