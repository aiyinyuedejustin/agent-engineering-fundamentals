# ACP 接入黑箱 CLI：协议事件并不等于全部模型调用

研究日期：2026-11-06 UTC。OpenHands SDK 源码固定为 `295b3baf71dfac1be028c5b187134ec3eb495346`。ACP 协议网页为当日读取的可变文档，未固定其规范仓库版本。

**D3 范围：**OpenHands ACPAgent 的启动、prompt、usage、工具状态补全、取消与恢复分支；已读 local/remote 示例。**D1 范围：**ACP session/prompt-turn 协议。没有安装 npx 包、启动外部 CLI、进行认证、调用模型或运行云服务。

## 1. 三种“把 agent 接进来”不是同一层

| 路径 | 接入层 | 典型可观测信息 | 不能自动推断 |
|---|---|---|---|
| Harbor installed CLI adapter | 在 task environment 内启动 agent | 原生日志、产物、adapter 转换的 ATIF、grader reward | 所有 CLI 内部请求都完整可见 |
| Inspect model API bridge | 接管兼容模型 API 请求 | 实际模型调用、有效 generation config、桥接工具与预算 | 原生 agent 配置完全未变、未走旁路 |
| OpenHands ACPAgent | 与外部 agent 的高层 session/prompt 协议 | 文本/工具更新、session、provider 报出的 usage | 一个 ACP turn 只含一个模型调用，或所有内部工具/模型事件无损留存 |

这三种可以组合，不是互相替代的产品排名。分别见 [Harbor](harbor-source-trace.md) 与 [Inspect](inspect-bridge-and-trajectory.md)。

## 2. 真实示例与启动链

已读固定源码的 [local ACP 示例](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/examples/01_standalone_sdk/40_acp_agent_example.py)：从 provider registry 取得启动命令，要求列出/read 项目文件，再发送图片，并用 ask_agent 问旁支问题；finally 调用 agent.close。

[remote 示例](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/examples/02_remote_agent_server/09_acp_agent_with_remote_runtime.py) 通过 APIRemoteWorkspace 在 agent-server 内运行预装 ACP CLI，收集 callback 事件。它是接入示例，不是带 grader 的 benchmark。镜像 tag 与 CLI 身份仍需固定。

[ACPAgent._start_acp_server](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3051-L3450) 的关键链路：

1. 建立 bridge、masker，构造 subprocess 环境和 provider 设置。
2. 使用 stdin/stdout pipes 启动 CLI，并过滤混入 stdout 的非 JSON-RPC 行，stderr 单独处理。
3. initialize 发现 agent name/version/capabilities，再做可用的认证/session 设置。
4. 有旧 session ID 时尝试 load；否则 new_session。
5. 解析 provider 报告的模型和模型切换机制，设置实际请求模型与 session mode。

**重要范围：**这是 agent 进程控制和协议连接。外部 agent 自己决定模型、工具、context compaction 和执行逻辑；一个高层 prompt 可以包含很多内部生成和工具调用。

## 3. Permission 与 isolation 需要单独审查

当前 [_OpenHandsACPBridge.request_permission](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L1703-L1720) 的意图是自动批准，实际实现选择 options 的第一个 option_id；没有 options 时使用 allow_once。它没有在此函数中根据 option.kind 选择。评测配置应保存返回选项的实际含义，不能只依赖注释的“通常 allow once”。

[ACPAgent 参数](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L1815-L1895) 对部分已知 provider 默认选择 bypass/full-access mode。client fs/terminal 方法在该 bridge 中未实现，因为外部 server 自行处理文件和终端操作。

源码还明确把 conversation 的 secret registry 提前注入 CLI 环境，因为无法逐工具扫描一个黑箱 CLI 的需要。**工程推断：**应该为评测提供最小范围、可撤销的测试凭证，并依赖经过验证的外层隔离，而不是把普通个人环境直接当执行环境。本轮没有读取或传递任何实际凭证。

## 4. 一次 ACP prompt 的执行边界

[_step](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L4154-L4286) 找到用户消息，构建 prompt blocks，重置 turn accumulator，然后调用协议 prompt。可重试的连接错误和特定 server error 有 retry 分支；超时另行取消。

[_do_acp_prompt](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3806-L3834) 等待 prompt response，若尚未收到 UsageUpdate，再等待一个短时间窗口；缺失时 warning，不把整轮必然判为失败。

### Idle timeout 与 hard deadline

acp_prompt_timeout 默认 1800 秒，但它是 **inactivity timeout**。每条 token、thought、tool progress 或 usage 更新都会重置时钟。[等待实现](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3842-L3901) 使用 asyncio.wait 检查空闲时长，不是从 turn 开始倒计时的绝对截止。

acp_startup_timeout 默认 90 秒则是 hard deadline。remote conversation blocking timeout 又是第三层。把这三个字段统一写作 “timeout=30 min” 会丢掉重要实验条件。

### Stop reason 与 grader

官方 [prompt-turn 协议](https://agentclientprotocol.com/protocol/prompt-turn) 区分 end_turn、max_tokens、max_turn_requests、refusal、cancelled。结束一轮不是任务通过。

所读 [_finalize_successful_turn](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3906-L3993) 记录 usage、补齐工具状态，生成 FinishAction/FinishObservation，并把 conversation 设为 FINISHED。分析应保留原始 stopReason 和 wrapper 状态，不能仅把 FINISHED 算为 benchmark success。本轮未验证所有 stopReason 的端到端映射。

## 5. 工具状态可能由 adapter 补全

[_flush_inflight_tool_calls_as_completed](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3604-L3624) 在 prompt 成功返回后，把 server 开始但未发送 terminal update 的 tool card 补为 completed，以保持 action→observation 配对和 UI 终止。

取消/重试时 [_cancel_inflight_tool_calls](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3559-L3602) 也会生成 synthetic failed 事件，防止 UI 永远显示 running。

**推断：**标准化轨迹中的 completed/failed 可能是原生报告，也可能是 adapter 根据 turn 边界补出的状态。若研究工具错误率、取消成功率或实际完成时刻，应标明 provenance，不能把这两类事件不加区分地统计。

## 6. Usage 是报告数据，完整性和单位仍需核对

[_extract_token_usage / _record_usage](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L943-L986) 与 [计费记录路径](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L2151-L2225) 使用：

- PromptResponse.usage 的每轮 token，或 provider 特定 `_meta` fallback。
- UsageUpdate 中累计 session cost 的正向 delta。
- 若没有记录到 cost，但有 token 和明确 model，则尝试 LiteLLM pricing 估算。
- 全部缺失时只记录 debug 信息，tracking unavailable；缺失不能解释为免费。

官方协议允许 UsageUpdate.cost.currency 是 USD 等货币，也可以是 credits。所读 `_record_usage` 直接使用 amount 做差并 add_cost，没有在这条路径按 currency 分支。这是需要用非 USD synthetic response 验证的单位兼容性问题；本轮没有证明任何已用 provider 实际报告非 USD，也没有做价格账单核对。

此外，定价表估算不是 provider 实际账单，尤其不能假定所有 cache、reasoning、subscription 或折扣规则都被同样覆盖。

## 7. Session ID 不等于可恢复的完整执行环境

官方 [session setup](https://agentclientprotocol.com/protocol/session-setup) 要求先初始化能力，再按 agent 支持的 session 功能使用 load/resume。session 是 agent 自己管理的上下文身份。

OpenHands 保存 prior ACP session ID 和对应 cwd。[_start_acp_server 的恢复段](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3128-L3176) 在 cwd 不匹配时不直接用旧 ID；[load 段](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3340-L3407) 对协议层 ACPRequestError fallback 到 new_session，而 transport failure 则继续抛错。

**推断：**外层 Conversation 恢复后，内层 CLI 可能已经是一个新 session。应记录 requested prior ID、实际 session ID、恢复还是 fallback，以及有效模型配置。否则“resume 成功”的日志可能掩盖内部上下文重建。

## 8. 取消是协议动作、drain 与进程清理的组合

ACP 规范要求收到 session/cancel 后尽快停止操作，并在结束前返回 cancelled；客户端仍应接收取消后的迟到 update。这个协议要求不是某个 provider 已完全符合的证明。

当前 async 路径有 [send cancel + drain](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L3626-L3733)：等待短 grace window，未 quiesce 时安排重启 ACP runtime；重启保留 prior session ID，因为本地 drain timeout 不证明 server 丢失持久会话。

[close/_shutdown_runtime](https://github.com/OpenHands/software-agent-sdk/blob/295b3baf71dfac1be028c5b187134ec3eb495346/openhands-sdk/openhands/sdk/agent/acp_agent.py#L4733-L4827) 关闭连接、terminate/wait，必要时 kill，再清理读流和凭证生命周期。它清理控制的 CLI 进程；是否结束所有脱离进程树的工作和远端服务仍需实测。

## 9. 文档与固定实现差异

当日 OpenHands ACP guide 写 mcp_config 不支持；固定源码 supports_openhands_mcp=False 的说明却明确区分“不在进程内创建工具”与“把配置转发给 ACP server”，启动代码也实际构造 MCP 列表传给 new/load session。

这说明 capability helper 名字、网页和当前代码不能机械互译。这里只确认所读版本差异，未运行兼容性测试；也不据此宣称所有 ACP server 支持相同 transport。

## 10. 下一组值得做的实验

1. 一个 ACP turn 内两次模型调用，对比 native counters、协议 usage 与外层 step 数。
2. tool start 后省略 terminal update，区分原生结束与 adapter synthetic completion。
3. 发送 cumulative cost、零 delta、重置累计计数、credits 货币单位和缺失 usage，核对指标语义。
4. 请求执行后断连再 retry，检查副作用是否重复。
5. stale session、cwd 改动、load 被拒绝，检查是否明确标出 fresh fallback。
6. 持续 progress 但不完成的 server，区分 idle timeout 与真正总预算。

这些计划未执行。接入一个标准协议并不会自动解决 benchmark 的预算公平、轨迹完整性、权限隔离和可恢复性。
