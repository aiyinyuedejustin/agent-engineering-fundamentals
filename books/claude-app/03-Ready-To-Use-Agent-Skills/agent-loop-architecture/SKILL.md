---
name: agent-loop-architecture
description: Design or debug desktop agent session lifecycles, asynchronous query ownership, approval control messages, turn completion, cancellation, and teardown. Use for client orchestration architecture; do not treat it as a reconstruction of private model reasoning or server execution loops.
---

# Agent 会话与控制循环

## When to use

用于启动/停止竞态、迟到消息污染新会话、权限卡悬挂、turn 结束却误杀连接、进程断开却显示成功，或设计带工具权限的客户端 Agent 会话管理器。普通对话内容格式问题应在内容 reducer 处理，不要扩大成整个 loop 重写。

## Workflow

1. 先画所有权：UI/session manager、query consumer、transport/process、tool executor、approval service 分别负责什么。`can_use_tool` 是授权回调，不能画成主进程任意执行工具的入口。
2. 阅读 [状态与边界](references/lifecycle.md)。把产品已观察行为与自己的实现合同分别写下。AgentLoopEngine 是工程书的概括名称，不是恢复出的目标类名。
3. 为 session、启动 generation、query 身份、turn ID、control request ID 建独立标识。每个异步写回都核对代次与对象归属。可参考 [原创局部模型](assets/session-model.mjs)。
4. 分离应用消息与控制消息。授权请求绑定 session、tool、参数、request ID 和 abort；未知决定默认拒绝；重复/过期请求不得重新产生副作用。已结算 ID 也保留去重记录，每个 session 使用新 inbox；不要驱逐后重开旧请求。
5. 明确定义一次 turn 的成功、错误、取消、无终态 EOF。result 可以结束 turn，而健康连接仍保留；进程退出也可能没有成功 result。
6. 明确用户 Stop、turn interrupt、session archive、UI close 的含义。先失效旧代次，再取消输入、等待/拒绝挂起控制请求并关闭资源。不要把网络断开视为远端操作已回滚。
7. 用注入 transport 和合成消息测试启动中 stop、旧成功回调、重复授权、终态前 EOF、结果后暖连接。运行 `node assets/session-model.test.mjs`。再按真实 backend 的取消/重试/退出合同做集成测试，不用静态证据代替。

## Anti-Patterns

- 一个 `isRunning` 同时代表进程存在、turn 正在生成、授权待决和 UI 可输入。
- 旧 query 的 result 没核对 generation 就把新会话改成 idle。
- 收到 result 就断言进程已结束；迭代器正常 return 就断言任务成功。
- 将 300 秒 stalled telemetry 或健康检测阈值当成所有工具的执行超时。
- 权限卡被关闭但 Promise 永久悬挂，或对未知决定默认 allow。
- 失败后无条件重发工具调用，忽略第一次调用可能已经产生外部副作用。

## Code seed

```js
const ticket = session.begin();
const transport = await createTransport();
if (!session.attach(ticket, transport)) {
  // attach 已关闭这个迟到连接；它不能重新成为当前会话。
  return;
}
// 此后每次 onEvent 都携带 ticket；不得只凭 session 名称写回。
```

这里只是客户端编排示意。模型调用、权限决策界面、工具执行、持久恢复与进程管理要由目标产品自己的明确合同提供。
