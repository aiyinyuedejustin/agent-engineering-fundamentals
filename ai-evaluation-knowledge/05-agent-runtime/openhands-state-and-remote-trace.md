# OpenHands SDK：会话状态、工作区和远端完成信号

研究日期：2026-11-06 UTC。代码固定到 OpenHands/software-agent-sdk `295b3baf71dfac1be028c5b187134ec3eb495346`。官方文档当日读取，版本可能与代码不同。

**D3，范围限定为 conversation state persistence、event storage、local fork/navigation、remote client synchronization/completion。**已读真实 persistence 示例及相关代码；未运行 SDK、agent server、模型或云环境，未追踪所有 server-side endpoint。它不是完成的 benchmark 案例或 D4 复现。

## 1. 一个真实示例，两个不同的“保存”对象

官方 [persistence 指南](https://docs.openhands.dev/sdk/guides/convo-persistence) 和固定版本 [10_persistence.py](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/examples/01_standalone_sdk/10_persistence.py) 创建同一个 conversation_id，配置 Terminal/FileEditor/MCP 工具，在工作目录创建再删除文件，销毁 Conversation 对象后重新创建，并询问先前做过什么。

这演示的是保存会话后恢复上下文，不是把已删除文件恢复回来。网页与固定源码的默认模型、MCP 配置也已有差别，实际复现应保存所运行的完整脚本和依赖身份，不能把文档代码块当成固定版本实验 manifest。

[ConversationState.create](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/state.py#L482-L629) 的 restore 路径：

1. 读 base_state.json，解析模型，检查 conversation ID。
2. 建立 EventLog，必要时修复缺失 HEAD，重建 active view。
3. 若提供新 agent，验证工具兼容后允许覆盖 agent；不提供时保留持久化 agent。
4. 以本次提供的 workspace 更新 state.workspace，并更新运行参数。
5. 保留累计 stats，返回可继续运行的 state。

本链路没有把 workspace 的任意文件树做快照和回滚。保存 BaseWorkspace 配置、继续使用同一个目录、复制/恢复文件字节，是三个不同操作。指南的 “Workspace Context / file system state” 不能单独作为可还原任意文件变更的证据。

## 2. Autosave 的触发方式也是契约

[state.py](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/state.py#L203-L263) 允许自定义 agent_state，但明确要求重新赋值来触发 autosave，而非只原地改一个 dict 子项。

[__setattr__ / context manager](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/state.py#L631-L683) 对公共字段变化写 base state；在 `with state` 中则延迟到最外层退出合并写入。保存失败会抛出，state-change callback 失败则记录日志。

[LocalFileStore.write](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/io/local.py#L63-L73) 对文本调用 atomic_write_text。这个事实支持“单文件写入使用原子 helper”，不自动证明 base_state、所有 event 文件和外部工具副作用组成同一事务。本轮未进一步检验所有存储介质的掉电 durability。

### Secrets 不是一概完整保存

[_save_base_state](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/state.py#L457-L479) 说明有 cipher 时按 cipher context 序列化；无 cipher 时 secrets 被 redact，restore 后会丢失，并输出 warning。

因此“secret 字段在 state 里”与“下一进程具备原来的凭证能力”不同。此处只读了实现，没有读取、复制或测试任何真实用户凭证。

## 3. 轨迹可以是树，不能总按文件顺序当成当前上下文

[append_event](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/state.py#L300-L364) 给事件补 parent_id、写入 EventLog，再推进 HEAD；state-sync 事件不作为树节点推进 HEAD。active_branch 是到当前 leaf 的路径，废弃分支仍在日志中。

[EventLog.append](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/event_store.py#L241-L303) 使用文件锁，检查重复 event ID 和不存在的显式 parent，写事件后更新索引。扫描逻辑允许缺失文件后的后续事件仍可读，并对洞和重复 ID 给 warning。

若 HEAD 对应事件丢失，[repair_missing_leaf](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/state.py#L300-L320) 退回 surviving event，并明确不能恢复丢失事件原有的 branch。

**推断：**“恢复成功、日志可读”与“轨迹完整、仍处于同一分支”不相同。评测分析应记录 parent/leaf、缺失事件告警及 active view，不应将所有事件按序拼接成模型实际见过的上下文。

## 4. Fork 与 navigate 不等于环境回滚

[LocalConversation.fork](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L861-L997) 深复制 agent，复制选定事件和 agent_state，但创建新 conversation 时传入 `workspace=self.workspace`。默认 reset_metrics=True，使 fork 的成本/token 从新统计开始。

[navigate_to](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L999-L1022) 改 HEAD 并 rebuild_view，没有文件回滚动作。

**源码事实：**这些 local conversation 操作改变事件视图和身份，不生成独立 workspace snapshot。**工程推断：**把它们用于 counterfactual branch 对照时，必须另行隔离/恢复环境，否则两条“历史分支”可能操作同一份已改变的文件。统计 whole-search cost 时，也不能只读 reset 后的分支成本。

## 5. Remote events：WebSocket 加 REST 对账

官方 [agent server overview](https://docs.openhands.dev/sdk/guides/agent-server/overview) 描述 HTTP/WebSocket client → server → workspace。已追踪 [RemoteEventsList](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/remote_conversation.py#L336-L450)：

- 初始化通过分页 REST 拉取历史。
- WebSocket 持续增量更新。
- 建立订阅后再 reconcile，以覆盖 REST 初始读取与订阅之间的间隙。
- reconnect 后 reconcile，并按 event ID 补发 callback 未见的事件、避免简单重复。
- reconciliation 请求出错时会 warning 并返回已取到的部分结果，而不是一律使流程失败。

因此“reconcile 方法返回”不自动等于“已拿到全量远端日志”。需要独立观测同步健康、分页完成与缺口。callback 尝试去重也不能直接推导外部下游副作用 exactly-once。

这条源码链包含 [reconnect 与 readiness handshake](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/remote_conversation.py#L1204-L1311)。初始历史在初始化后被视作已见，callback 不是把所有历史从头 replay 一遍。

## 6. “finished” 和 “本次 run 返回”之间还有 race

[RemoteConversation.run / _wait_for_run_completion](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/remote_conversation.py#L1395-L1582) 先清理旧 completion signal，POST run，再为此次 run 接收完成状态。

源码优先等待 post-run WebSocket full-state snapshot。REST 的 FINISHED 暂不直接视为完成，因为 stop hook 可能否决停止，把状态改回 RUNNING。连续 REST terminal 状态超过 30 秒但仍没有相应 WebSocket snapshot 时，才使用带 warning 的 fallback，并刷新 state/reconcile events。

[LocalConversation._run](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/local_conversation.py#L2104-L2164) 的确有 stop hook 把 FINISHED 改回 RUNNING 的分支。这是读取 client comment 后继续追踪另一端状态逻辑，而非把注释当成完整实测。

### 相同 API 表面不表示异常完全一致

固定源码明确写：local run 达到 iteration limit 或 stuck 时返回并保留 ERROR/STUCK 状态；remote run 会抛 ConversationRunError。评测封装只捕获异常而不读状态，可能在两种 workspace 下做出不同分类。

Remote blocking timeout 还明确提示 conversation 可能仍在 server 上运行。该 timeout 是客户端等待上限，不是服务器 kill 指令。pause/interrupt 是另外的 endpoint，workspace teardown 又是另一层。

## 7. 关闭与成本留存

[RemoteConversation.close](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/conversation/impl/remote_conversation.py#L1966-L2020) 从已有 cached stats 注册成本，明确避免把尚无 stats 的部分状态当成 0；关闭 WebSocket，并在 delete_on_close 时 best-effort DELETE conversation。shared HTTP client 由 workspace 管理，不能在 conversation close 时先关掉而阻止后续清理。

这再次表明：client closed、conversation deleted、workspace released、known cost 完整，是不同状态。本轮没有做远端资源 inventory，不能证明 cleanup 的最终结果。

## 8. 后续实验和证据缺口

1. 只改 agent_state 的嵌套 dict 与重新赋值，对比磁盘实际持久化。
2. 在 event 写入与 HEAD 更新间崩溃，检查恢复分支和告警。
3. fork 两个 conversation 后读写同一 workspace，随后引入独立 snapshot 做对照。
4. WebSocket 断连并让 REST reconciliation 第二页失败，检查日志完整性标志。
5. stop hook 连续否决 FINISHED，验证 local/remote wrapper 的终止和错误分类。
6. blocking wait timeout 后查询 remote state，再明确 pause/interrupt/teardown，区分各操作后果。

全部是未执行计划。没有模型、网络副作用、server 运行和生产可靠性数据，本文件不能支持相关成功率或性能结论。
