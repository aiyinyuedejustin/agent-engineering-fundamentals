# Remote execution：统一接口背后的语义差异

研究日期：2026-11-06 UTC。本文件完成范围内收集，源码固定到 Harbor `26f95e0ebd8c77011bbf4656f5c98af66ce55848`。**D3 源码链路，未在 Docker、Modal、Daytona 或 SSH 远端执行。**本文件只比较 adapter 的具体执行与清理路径，平台隔离、资源和供应商部署选择见相邻 infrastructure 研究。

## 1. 一个 exec 签名不能保证行为等价

[BaseEnvironment.exec](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/base.py#L1436-L1463) 接收 command、cwd、env、timeout_sec、user，返回 [ExecResult](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/base.py#L110-L113) 的 stdout、stderr、return_code。

这些字段本身没有表达：输出是否截断、超时后远端是否仍运行、是否保留后台进程、是否使用 PTY、是否合并 stderr、哪个阶段发生错误、是否重试过有副作用的命令。适配器能提供共同调用方式，不意味着消除了这些差异。

[capabilities.py](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/capabilities.py) 进一步把 no-network、hostname/IP/CIDR allowlist、动态网络、Compose、Windows、mount、CPU/memory request/limit 分开。这是比单一“支持 sandbox”更有用的工程描述，但 capability 声明仍需要 provider 实测。

## 2. 三条已追踪的执行路径

| 维度 | Docker Compose adapter | Modal direct SDK 路径 | Daytona POSIX direct 路径 |
|---|---|---|---|
| 本轮追踪 | exec → _compose_exec → compose subprocess → collect | exec → strategy → _sdk_exec → sandbox.exec.aio | exec → strategy → _sandbox_exec → session command → poll |
| shell | main 为 bash -c；sidecar 为 sh -c | 默认 bash -c，login 显式选择 | 默认 bash -c，外围可加 env、timeout、cd、su |
| 输出 | compose 的 stderr 合并到 stdout | 独立 stdout/stderr，二者同时 drain | POSIX 从 session logs 取 stdout/stderr |
| timeout 可见实现 | host wait_for，超时终止本地 compose 进程并抛 RuntimeError | 把 timeout 传给 SDK；等待输出与 exit | 命令包裹 GNU 风格 timeout，同时把 timeout 传给 session submission |
| 清理边界 | _terminate_process 针对本地 compose 进程；环境 stop 另行进行 | 异常时取消 reader/wait tasks；sandbox terminate 是另一层 | 本次 exec 故意不删除 session，以保留后台 child；sandbox stop/delete 是另一层 |

此表描述已读调用层，不替 SDK/引擎实现做未经验证的保证。Direct 与 Docker-in-Docker 是不同 strategy，不能用 direct 结论覆盖 DinD。

### 2.1 Docker：杀掉客户端与停止容器是两件事

[docker.py 的 compose subprocess/collector](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/docker/docker.py#L748-L951) 使用 asyncio.create_subprocess_exec，stderr=STDOUT。buffered 与 streamed 路径都对读取/等待设置预算，timeout 时 terminate 本地进程，5 秒后仍未结束则 kill。streamed 路径也在其他 BaseException 时清理本地 subprocess。

源码特意自己按 chunk 切换行，避免 StreamReader 默认长行限制；streamed 路径把等待 process exit 也放入 timed scope，避免“stdout 已关闭但进程仍挂住”。这说明输出收集器本身也是正确性组件，不只是日志美化。

[service_exec/_compose_exec](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/docker/docker.py#L1398-L1494) 对 sidecar 不继承 main 的 cwd、user、persistent env，且使用 sh。这些默认值差异可能改变相同 shell 片段的行为。

[stop](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/docker/docker.py#L1230-L1268) 是独立步骤：keep_containers 优先于 delete，走 compose stop；否则 down 或 down --volumes 等。失败有 warning 分支，因此必须记录清理结果。仅观察 exec 抛 timeout，不能推断容器内所有后代已经消失。

### 2.2 Modal：SDK timeout 与本地 cancellation 不同

[_sdk_exec](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/modal.py#L1432-L1507) 把 timeout_sec 交给 sandbox.exec.aio，分别启动 stdout.read、stderr.read、wait 三个 task，再 gather。异常路径取消并 drain 这些 task。

**已知：**此层没有在该异常分支显式调用远端 process.kill。**未知：**SDK 取消语义是否已经终止远端进程、是否存在 disconnect 后继续运行、timeout 与取消对后代有何不同。本轮没有读完 SDK 底层或做云端实验，不能声称 Modal 会泄漏进程。

该 adapter 还区分主动 terminate 与意外 exit 137，以免把显式清理误报为 OOM；这是错误分类与执行生命周期相互影响的实例。

### 2.3 Daytona：后台进程是明确保留的语义

[_sandbox_exec](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/daytona/environment.py#L1808-L1894) 在 POSIX 下创建 session，run_async 提交，随后 [_poll_response](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/daytona/environment.py#L1693-L1754) 每秒查询直到 exit_code 非空，然后取日志。创建 session 与查询/取日志有 retry wrapper；不要把这些 wrapper 误读为整条任意 agent 命令都会安全重试。

finally 中明确不删除 session，注释原因是删除会结束包括后台启动的 child processes。因此需要持久 server 的任务可以受益，但每条 exec 返回不代表整个任务环境静止。poll loop 本身没有本地总 deadline，不能仅根据 timeout 参数断言 host polling 必然在该时刻结束。

Windows 分支使用 process.exec，输出是合并流，放入 stdout、stderr 为空；还拒绝 custom user。POSIX 结果不能直接推广到 Windows。

源码的 POSIX cwd 片段为字符串插值 `cd {cwd} && ...`，此处没有 shell quoting。这是值得用含空格目录做 conformance test 的具体检查点，不是已验证的 Daytona 远端故障。本轮没有请求上线修复或向第三方提交问题。

[_stop_sandbox](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/daytona/environment.py#L1673-L1691) 先尝试 delete；若服务拒绝删除，退回 stop 并 warning sandbox 仍在账户中。停止计费、删除资源、释放访问权限也不能混为同一个布尔状态。

## 3. SSH 是 transport，不是隔离等级

官方 [Agent Sandbox Protocol RFC](https://docs.harborframework.com/sandboxes/asp.md) 自称 v0 draft，主要描述 `.asp.json` 中 SSH 连接/workspace 等信息，provisioning 在范围外。不能当成已经普遍实现的成熟标准。

已读 [SSHAccess](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/environments/ssh.py#L47-L177)：

- 有 pinned host key 时 StrictHostKeyChecking=yes；没有时为 accept-new 并使用独立 known_hosts。
- 不读取用户 ssh config，命令在声明 workspace 下运行。
- 每个 process context 负责本地 SSH 子进程；退出时 terminate，drain pipes，3 秒后可 kill。
- provider 负责 access lease；此 helper 不负责创建或隔离远端机器。

**推断：**SSH 传输与容器/VM/微虚机隔离是正交维度；同一个 SSH interface 可能连接到完全不同的权限与生命周期边界。杀掉本地 SSH 客户端是否终止 remote descendants 需要单独验证。

## 4. 更合适的 conformance test 清单

建议固定同一组无害命令，在每个 backend 和具体 strategy 上产生机器可读结果。以下为实验设计，尚未远端执行。

1. **流与字节：**stdout/stderr 分别写 marker、交错输出、无换行的长输出、无效 UTF-8；记录原始字节数、解码策略、截断位置。
2. **时间：**命令正常超时、关闭 stdout 后继续运行、后台 child 持有 pipe、控制连接中断；分别记录 client return、remote exit、最后一次 artifact write。
3. **进程：**普通 child、同 process group child、新 session child；说明取消哪一级，不把一次 killpg 当成全系统清理保证。
4. **上下文：**含空格 cwd、跨调用 cd/export、env 覆盖、numeric UID、不存在 user、shell 不存在、sidecar 差异。
5. **重试：**读取可重试与状态写入可重试分开；让第一次响应丢失但写入已经完成，检查是否重复副作用。
6. **资源：**requested 与 effective limits、OOM 信号、磁盘满、输出超量，明确错误分类与分母规则。
7. **文件与清理：**软链接、目录复制、所有者、artifact flush、stop 后 resource inventory，保存 cleanup failure 独立状态。

一个合适的执行记录至少增加：phase、backend+strategy+version、attempt、submitted/started/exited/client_return 时间、timeout_kind、output_complete、remote_exit_known、cleanup_status。它可以在上层封装中实现，不必假设已有 SDK 统一提供。

## 5. 本轮不能证明的内容

- 没有比较云供应商性能、价格或可靠性；没有启动任何付费资源。
- 没有证明任何 adapter 已发生进程泄漏、结果污染或安全事故。
- 没有把一个分支的源码解释当成该产品所有模式的行为。
- 超时/取消/网络断连后的远端最终状态仍是重要待测项。

本轮强结论是：后端名称不够描述运行条件，exec API 兼容性也不够证明评测可比性。
