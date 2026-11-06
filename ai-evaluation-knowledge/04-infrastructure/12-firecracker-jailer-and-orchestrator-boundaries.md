# Firecracker：威胁模型必须落到实际启动器与恢复链

状态：本篇证据子集已闭合。阅读日期2026-11-06。学习目标L2→L3。

固定版本：

- Firecracker v1.17.0，commit `95f868c8e345b1cc8faccd1a3c910b4989dc3f58`。
- firecracker-containerd，commit `be68640a5d2237f5b427c37c1f5809ec154126c5`。
- 两个项目分别固定审查，**没有验证这两个版本组合可运行或受支持**。containerd项目的go.mod固定Go1.25.0、containerd1.7.33、runc1.2.8和Firecracker Go SDK伪版本`v1.0.1-0.20250818195323-ed6ff32aa924`。[C1]

证据深度：威胁模型/运维建议D1；具体配置D2；native jailer、snapshot load/build、containerd jailer选择/启动/清理相关子系统D3。**本篇没有Firecracker、jailer或runc运行D4。** Go selector局部实验在编译前失败，详见第8节。此前[Linux mmap实验](experiments/private-mapping/README.md)只验证本地内存映射机制，不升级为microVM执行证明。

## 1. 先把要防什么说清楚

官方设计把guest vCPU侧视为不可信，依赖KVM/硬件虚拟化与VMM提供第一层边界，再用宿主进程约束降低VMM出问题后的影响：seccomp、namespace/cgroup、降权。jailer调用者、输入路径和放入jail内的资源属于可信控制面，不能随意让agent指定它们。[F1][F2]

必须区分三个不同目标：

1. **安全隔离**：不可信任务能否越过guest、访问宿主或其他任务？
2. **资源隔离**：一个任务能否耗尽CPU、内存、I/O、日志或后台内核工作？
3. **评估一致性**：重新开始后是否获得相同镜像、数据、时钟、网络、CPU特征和预算？

有KVM不等于自动满足后两者。官方生产建议明确CPU/内存限制要按工作负载配置，Firecracker不会替操作者选择普适的严格默认值；网络流量也不由Firecracker做过滤，TAP之后的宿主策略必须单独配置。[F1][F3]

## 2. native jailer：从进程继承状态到降权exec

固定源码的调用序列是：[F4][F5]

```text
main_exec
  → sanitize_process：关闭继承FD、清环境变量
  → 解析参数 / Env::new
  → 创建jail根目录
  → Env::run
    → 复制Firecracker二进制
    → 可选加入给定network namespace
    → 安装rlimit / 可选cgroup配置
    → 建立chroot隔离
    → 创建设备节点等必要资源
    → 可选daemonize / 可选新PID namespace
    → 用指定uid/gid exec Firecracker
```

### 不要把可选功能写成默认保证

- network namespace只在传`--netns`时加入已有namespace；“创建隔离网络并安装出站规则”不在这一步自动完成。
- 新PID namespace由`--new-pid-ns`选择。
- cgroup v2且没有具体`--cgroup`参数时，源码检查parent cgroup存在才写入`cgroup.procs`；不存在则继续，没有在该分支报错。
- 默认resource limits只有NOFILE=2048，文件大小限制为None；CPU/内存需其他配置。[F5][F6]

因此审核应检查实际cgroup归属及生效参数，而不只检查命令是否包含`--cgroup-version=2`。这些是源级行为，不是本机namespace/cgroup实验。

### 文档与源码小漂移也影响复现

同一固定版本的jailer文档描述按/proc列举关闭FD，而源码用`close_range(3, UINT_MAX, CLOSE_RANGE_UNSHARE)`，失败向上传播。生产文档一处把NOFILE默认写4096，而resource_limits.rs为2048，jailer专门文档也写2048。[F2][F3][F4][F6] 应记录源码和实际运行值，不在不同文档间任意挑一个数字。

### 文件复制有明确威胁模型理由

native jailer复制Firecracker二进制而非硬链接，注释给出的原因包括避免不同VMM进程共享该二进制的内存页。目标打开带O_NOFOLLOW，并拒绝多硬链接目标。[F5] 这不是“任何copy都安全”的一般证明；父目录/资源所有权仍在可信操作者责任内。

## 3. 具体编排案例：containerd里的jailer不是native jailer

firecracker-containerd架构把宿主containerd→shim→Firecracker控制面与guest内agent→runc容器生命周期连接起来；一个microVM可以装多个容器。[C2] 所以“容器数”和“安全域数”不是天然一比一。

### 选择器的确切分支

`runtime/jailer.go:newJailer`：

- CreateVMRequest为空，或request.JailerConfig为空：返回`noopJailer`。
- JailerConfig存在，但UID或GID为0：拒绝。
- 非零UID/GID的显式配置：创建bundle目录，把CPU/Mems/cgroup/file-exposure等参数交给`newRuncJailer`。[C3]

自动创建单任务VM的调用点构造CreateVMRequest，只给VMID、退出策略和容器数，没给JailerConfig。[C4] 宿主全局Config的JailerConfig只存runc可执行文件/模板路径，并不在所读selector里替代缺失的request.JailerConfig。[C5]

**准确结论**：这个默认路径不添加该组件的runc host jail。不能扩大为“没有KVM隔离”“关闭了Firecracker seccomp”或“所有部署都以root运行”。宿主进程已有约束、其他启动方式和完整部署配置仍需另查。

### 显式runc路径怎么工作

它读OCI配置模板，构造bundle，复制Firecracker二进制/guest kernel，暴露驱动文件，重写API/vsock路径，最后执行`runc run <vmID>`。它不是调用Firecracker release中的native jailer二进制。[C6]

示例OCI模板包含空capability列表、noNewPrivileges、多个namespace、设备allowlist和NOFILE1024；UID/GID的0是待替换占位符，`overwriteConfig`随后写入请求提供的非零身份。[C6][C7] 这是**仓库示例模板**，不是本次核验过的任何线上实际配置。

比较这两种启动器时，应比最终进程的namespace、uid/gid、cgroup、seccomp和文件可见性，而不是只比较都叫jailer。

## 4. 文件暴露策略决定了基线是否共享

containerd的默认root drive配置使用read-only；请求可显式提供可写root drive。[C4] runc jailer提供copy与bind两条文件暴露路径：

- copy建立独立文件并调整所有权，read-only drive的复制模式为0400；
- bind路径加入OCI mount，所读代码的options只有`bind`，没有在这里加入`ro`，也没有消费copy分支的文件mode参数。[C6]

不能把guest看到的只读块设备、宿主以只读FD打开、宿主bind mount只读和源文件POSIX权限混为一谈。它们是不同的强制层。BIND是否在实际部署可写，还取决于源挂载、源文件权限、运行uid及Firecracker打开模式；本篇不声称发现了可利用的逃逸或已测得污染。

仓库的host-file-isolation设计文档也明确：硬链接、符号链接、bind mount、同一FD等复用底层存储方式本身不防修改，必须叠加其他机制。那份文档含设计建议，不应替代当前代码路径。[C8]

对评估平台而言，镜像复用必须写成“哪些字节共享、谁能修改、何时复制/写时复制”，不能只写“每任务一个目录”。参见[镜像、缓存与run identity](07-images-caches-and-run-identity.md)。

## 5. 启动成功、任务就绪和清理成功分开记录

containerd CreateVM使用`sync.Once`确保一个shim只执行一次创建，后续返回AlreadyExists。创建失败会取消shim上下文，不是在同一shim上无条件重试。[C4]

createVM顺序：选择jailer→构造配置→注入jailer handlers→NewMachine→Start→vsock连接guest agent→挂载请求驱动。以上成功后才close(vmReady)，让其他方法继续；“VMM进程已启动”不是全部就绪条件。[C4]

外层CreateVM建立超时context，但`machine.Start`收到的是长生命周期shim context；后续vsock与mount使用request context。因此不能只看外层60秒就宣称**每一段启动操作都受该总截止覆盖**。这是所读调用参数的界限，SDK内部其他超时未完整审计。[C4]

清理也有两个容易混淆的名字：

- 导出的`Cleanup` RPC在所读代码里只返回删除响应，带TODO，没有在该函数销毁VM；
- 内部`cleanup()`由VM退出监视器等调用，执行jailer.Close、发布停止事件、取消shim，受cleanupOnce保护；
- runcJailer.Close使用独立5秒context强制删除runc容器，并无论结果如何尝试删bundle，组合返回两类错误。[C4][C6]

监视器还针对runc1.2+中Firecracker死亡不一定立即结束runc的情况加了状态轮询。[C4] 评估平台应保存“guest任务结束、VMM退出、jail删除、文件清理”各自结果，不能用某个RPC返回成功代替全部清理证明。

网络配置的另一个待验证点：buildVMConfiguration用nil列表触发默认网卡，注释区分nil与显式空列表。但RPC编码是否能保留这种区别需要wire层测试；本次没有做，不能仅凭函数注释就宣称发送空列表一定能禁网。[C4]

## 6. Snapshot恢复：格式检查不是可信内容认证

固定Firecracker源码的状态格式版本为**12.0.0**，它不是产品版本1.17.0。[F7]

恢复链可概括为：[F7][F8][F9]

```text
snapshot_state_from_file
  → Snapshot::load
    → 有界读取状态文件 / bitcode解码 / magic与版本检查 / CRC64检查
  → 应用TAP与vsock路径覆盖
  → 恢复machine配置 / 内存结构sanity checks
  → 文件映射或userfaultfd内存后端
  → KVM、vCPU和设备状态恢复
  → vCPU线程以Paused开始
```

几个容易被“snapshot validated”掩盖的细节：

1. 10,000,000字节限制作用于序列化**状态文件**，不是guest全部内存或磁盘预算。[F8]
2. magic和版本规则有明确边界；同major、minor不高于当前值的格式可以过该检查，patch不限。但结构解码、设备/CPU/内核兼容性仍可能失败。[F8]
3. `load`调用bitcode解码与头校验后再验证CRC；CRC用于意外损坏检测，不是来源签名或授权。绝不能把外部未知来源snapshot当成“CRC过了就安全”。[F8]
4. 名为validate_cpu_vendor/manufacturer的函数在所读版本对不匹配只warning，不返回错误；sanity check中真正硬失败的是特定内存区域结构条件。这不是跨CPU可移植保证。[F7]
5. 恢复VMGenID设备必须在KVM状态恢复之后，否则注入guest的generation-change中断会被覆盖。builder源码明确这一顺序，并把vCPU以Paused状态启动。[F9]

快照创建也不是一个文件的原子提交：create_snapshot先写/可选sync状态文件，再保存内存文件；状态文件以truncate方式打开。若后续失败，编排器必须识别不完整快照集合，不能仅因状态文件存在就发布可复用基线。[F7] 本次没有注入真实KVM保存故障，也没有证明某个编排器已经犯此错误。

已有[快照与reset合同](04-snapshot-and-reset-contracts.md)讨论外部磁盘、身份、时钟、网络及immutable backing。这里新增的是源级加载/恢复顺序，不能把前一篇mmap实验冒充整个恢复链运行。

## 7. 资源账户还可能漏掉“VM之外的工作”

官方生产建议提到：x86 guest定时器可驱动宿主kvm-pit内核线程，该线程默认处于root cgroup，需要宿主管理才能纳入预期账户；Firecracker已降权，不能自己完成这个事后移动。[F3] 这提示“VMM pid在正确cgroup”不等于所有诱发工作都已经计入同一资源组。

同一文档还说明guest可影响serial/log输出量，日志消费者和存储上限属于宿主责任；一次aarch64配置例子中host console logging令snapshot restore由3ms增至8.5ms。数字是**上游报告例子D1**，不是本研究复现，也不是所有机器的统一开销。[F3]

这与AI评估的连接很直接：模型可生成大量输出、创建大量进程/文件或高频I/O；“给了2个vCPU”并没有完整描述实际可用预算与平台侧负担。

## 8. 最小实验：明确记录未成功

[selector实验目录](experiments/firecracker-jailer-selection/README.md)准备了完整原样`runtime/jailer.go`加本地stub依赖的Go测试，计划检验三类纯选择/参数传递行为，不调用runc、KVM或namespace。

实际在2026-11-06T03:53:21.790969+00:00，PATH里的`/usr/bin/go`对`go version`返回非零并输出`Go: Unknown option: version`。因此没有验证出可用Go编译器，**编译/测试均未开始，0个测试执行**。没有安装工具链、没有联网拉依赖，也没有改用真实VMM绕过前提。

保存的Python runner后来补了清楚的工具链前置检查，但没有重跑。Go测试fixture未经过编译，不能当作已验证quickstart。源码结论维持D3。

实践验收顺序建议：

1. 先在隔离测试host固定VMM、启动器、模板、kernel、rootfs与SDK版本。
2. 从实际CreateVM请求追到最终process，不只审查配置文件里是否出现jailer字样。
3. 实测uid/gid、namespace、seccomp、cgroup及驱动FD权限；包含缺配置、错误路径和拒绝分支。
4. 快照发布采用完整manifest、字节摘要、权限与原子完成标记，校验多文件一致性。
5. 验证故障时的实例退休、cleanup结果、剩余进程/挂载/卷与日志配额。

以上真实平台操作尚未执行；涉及namespace、权限、cgroup或破坏性清理时必须在获准的独占测试环境实施。

## 来源与读取范围

- [F1 design.md](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/docs/design.md)：威胁包含、sandboxing、网络等相关章节。
- [F2 jailer.md](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/docs/jailer.md)：完整阅读，trusted inputs/可选配置/cleanup责任。
- [F3 prod-host-setup.md](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/docs/prod-host-setup.md)：1–200及相关网络/硬件章节；未执行文档命令。
- [F4 jailer/main.rs](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/src/jailer/src/main.rs)：221–389相关初始化代码；测试仅阅读。
- [F5 jailer/env.rs](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/src/jailer/src/env.rs)：159–297、490–585、646–788；不是全文件安全审计。
- [F6 resource_limits.rs](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/src/jailer/src/resource_limits.rs)：完整阅读，未运行其中setrlimit测试。
- [F7 vmm/persist.rs](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/src/vmm/src/persist.rs)：149–554相关保存、sanity与恢复链。
- [F8 snapshot/mod.rs](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/src/vmm/src/snapshot/mod.rs)：完整阅读，单元测试未运行。
- [F9 builder.rs](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/src/vmm/src/builder.rs)：427–570恢复相关段落。
- [C1 containerd go.mod](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/go.mod)：读取固定依赖/语言版本，未构建依赖图。
- [C2 architecture](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/docs/architecture.md)：完整阅读；README多租户风险声明也已读。
- [C3 jailer.go](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/runtime/jailer.go)：完整阅读；原始blob `19af4ad2dce6eb62f9cf64be06a475de09be5502`，未成功执行。
- [C4 service.go](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/runtime/service.go)：348–393、456–640、927–1068、1740–1825相关段落。
- [C5 config.go](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/config/config.go)：完整阅读。
- [C6 runc_jailer.go](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/runtime/runc_jailer.go)：92–307、371–475、502–614；noop_jailer.go完整阅读。
- [C7 示例OCI模板](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/runtime/firecracker-runc-config.json.example)：完整阅读，非实际部署配置。
- [C8 host-file-isolation](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/docs/host-file-isolation.md)：完整阅读，区分设计建议与运行实现。
