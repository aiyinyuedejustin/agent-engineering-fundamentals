# 生命周期事实与原创合同

范围：Claude Desktop Linux 2.37337.1，2026-10-14，静态客户端/SDK/transport 研究；没有执行 CLI 或目标应用。短事实与定位见 evidence.json。

## 已观察到什么

- AL-01：可见层包括 LocalAgentModeSessions IPC、会话管理器、SDK query consumer 和 CLI transport；不能等同于服务器模型循环。
- AL-03–04：会话生命周期包含 idle、initializing、running、stopping、archived，存在显式合法转移表；初始化代次与对象身份防止迟到 query 重新挂接。仅凭状态名不能猜全转移表。
- AL-11、15：can_use_tool 请求触发授权回调；控制流区分 request/response/cancel；在途重复 ID 与关闭后的请求受到处理。工具真正在哪执行还要看 CLI 或 MCP 分支。
- AL-17、19：success 与 is_error 共同影响 turn 判定；有排队消息可能继续。没有结果就结束不能当成功。result、idle 和进程退出不是同一事件。
- AL-20：UI stopSession 与 SDK interrupt 是不同路径。stop 使初始化代次失效，并清理队列/输入；不能笼统叫「暂停输出」。
- AL-24：所检 Node ProcessTransport 有结束 stdin、宽限、信号升级的关闭步骤；这不是 Windows、VM adapter 和所有 backend 的统一退出合同。

## 推荐分离的状态轴

| 轴 | 示例 | 应由谁确认 |
|---|---|---|
| Session 生命周期 | idle / starting / active / stopping | 会话所有者 |
| Turn | pending / streaming / success / error / cancelled | 明确的终态协议 |
| Transport | connecting / open / closed / failed | 连接/进程层 |
| Approval | waiting / allowed / denied / aborted | 授权层 |
| UI | visible / minimized / closed | 页面呈现层 |

这张表是原创设计建议；各轴无需使用相同枚举。每个事件应带归属，日志保留 ID、版本和错误类别，避免写入凭据或完整敏感输入。

## 教学模型如何简化

session-model.mjs 只有 idle/starting/running/stopping，使用 host 自选的 generation ticket，接受明确 success/error 的本地 result；clean success 保留模拟 transport。它没有 archived、建议等待、后台任务、SDK message schema、CLI signal tree 或真实恢复。其状态表是原创且刻意较小，不声称 wire compatibility。

ApprovalInbox 演示在途及已结算 ID 去重、明确 allow/deny、取消和 teardown 拒绝。已结算 ID 在本 inbox 生命周期内保留原 Promise，重复决定返回 false；不得通过驱逐记录后重新接受旧 ID。每个新 session 必须创建新 inbox，结束时 close 释放记录。生产实现必须把授权绑定到具体工具及不可变参数，并由可信宿主验证用户决定；工具执行层仍需自己按请求 ID 保证幂等，重复读取同一 allow 不授权重复执行。收到了 allow 字符串本身不构成用户许可。

SessionModel 在调用 transport.close 前先移除旧 transport 的所有权；重新 begin 时先失效旧 ticket，避免 close 同步发出 EOF 导致递归关闭或旧事件污染新启动。重复 attach 同一个当前连接返回 false，但不会关闭它。示例假设 close 可同步发出事件且本身不抛异常；真实适配器的关闭失败、异步退出与重试仍需单独处理。

生产退出还应处理所有 in-flight RPC 的 settle、释放锁、持久化最终状态和进程树。连接关闭后外部写操作可能已成功，标为 outcome unknown 并查询可用回执，不要盲目重发。
