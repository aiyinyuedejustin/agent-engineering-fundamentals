[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-11"></a>

## 11. 插话、暂停与取消：让旧任务正确让路

<a id="durable-orchestration-007"></a>

### durable-orchestration-007 · Interrupts

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed 2026-10-13; response_schema &gt;=1.2.12。读取日：2026-10-13。

用途：interrupt 恢复从节点开始重跑，父节点调用子图时父节点前段也重跑；原进程栈未被冻结。

选读范围：暂停与恢复、并发 interrupt ID、中断顺序、子图恢复及中断前副作用的说明。限制：文中称1,2,3次重放为指数级不准确；示例只执行一次不能覆盖崩溃后重试，须另外解释提交边界

[公开原文](https://docs.langchain.com/oss/python/langgraph/interrupts)

<a id="durable-orchestration-016"></a>

### durable-orchestration-016 · Cancellation and Termination

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Cancel是协作请求，能执行清理；Terminate立即关工作流，没有清理和补偿，已发生外部动作不会自动撤销。

阅读范围：Cancellation 与 Termination 的区别、清理、Activity heartbeat 及父子结束策略。限制：工作流终止不证明外部进程或远端动作已停止

[公开原文](https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination)

<a id="durable-orchestration-018"></a>

### durable-orchestration-018 · Workflow message passing: Signals, Queries, Updates

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Signal是异步写入且不返回处理结果，Update是可等待结果/错误的跟踪写请求，Query只读且不能阻塞。

阅读范围：Signal、Query 与 Update 的写入、等待结果和只读语义。限制：各产品消息API保证不同，应借用分类而非照搬实现

[公开原文](https://docs.temporal.io/encyclopedia/workflow-message-passing)

<a id="durable-orchestration-031"></a>

### durable-orchestration-031 · Double texting

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：新消息到达已有run时可enqueue/reject/interrupt/rollback，串行队列是默认，不是唯一交互语义。

阅读范围：full body Enqueue/Reject/Interrupt/Rollback。限制：功能属于LangSmith Deployment，不是LangGraph OSS自动保证；外部effect回滚边界为工程推论

[公开原文](https://docs.langchain.com/langsmith/double-texting)

<a id="durable-orchestration-032"></a>

### durable-orchestration-032 · Restate agent turn routing implementation

作者／组织：restatedev/agent contributors。类型：源码／仓库文档。版本／日期：main accessed2026-10-13。读取日：2026-10-13。

用途：ask忙时入队，steer不取消工具，onTurnEnd拒绝陈旧/重复结果并清理子任务和审批后启动后继。

阅读范围：raw.githubusercontent.com/restatedev/agent/main/packages/libs/core/src/agent/turns.ts; handlers.onTurnEnd, route, startSuccessor。限制：代码设计示例未本地执行，main可变；同仓其他薄包装文件未额外计数

[公开原文](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)

<a id="durable-orchestration-048"></a>

### durable-orchestration-048 · Notes on structured concurrency, or: Go statement considered harmful

作者／组织：Nathaniel J. Smith。类型：作者／团队实践或研究文章。版本／日期：2018。读取日：2026-10-13。

用途：父任务return不等于后台子任务结束；未join任务会在文件/连接已关闭后继续使用资源，错误也可能无人收集。

选读范围：go statement considered harmful; Nurseries subsections escape/cancellation/resource/error propagation。限制：2018 Trio设计经验；现代语言产品比较不沿用，内存nursery不提供进程崩溃后的durability

[公开原文](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)

<a id="human-control-001"></a>

### human-control-001 · Codex App Server

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：current docs, accessed 2026-10-13。读取日：2026-10-13。

用途：turn/steer必须匹配expectedTurnId，不创建新turn且不能修改turn级model/cwd/sandbox覆盖。

选读范围：Steer an active turn、Approvals、Errors、Item lifecycle。限制：公开协议文档不等于所有版本实现；MCP elicitation形态仍是此产品所实现版本，不能替代新版MCP规范

[公开原文](https://learn.chatgpt.com/docs/app-server)

<a id="human-control-002"></a>

### human-control-002 · Prompt Turn

作者／组织：Agent Client Protocol。类型：官方文档／规范。版本／日期：ACP v1 current 2026-10-13。读取日：2026-10-13。

用途：cancel后客户端必须取消待审批；代理应尽快停模型/工具，收尾及pending updates之后以cancelled结束原prompt。

选读范围：Stop Reasons/Cancellation。限制：SHOULD与MUST强度不同；不能推出远端副作用已撤销

[公开原文](https://agentclientprotocol.com/protocol/v1/prompt-turn)

<a id="human-control-006"></a>

### human-control-006 · Chatbot Resume Streams

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 current docs。读取日：2026-10-13。

用途：resumable stream中关闭页面或useChat.stop只是断开HTTP消费；明确停止需要独立后端endpoint取消active work并清理activeStreamId。

选读范围：How stream resumption works/Stop an Active Resumable Stream。限制：示例不是完整授权/事务实现；流恢复只恢复事件消费不自动恢复死进程

[公开原文](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)

<a id="human-control-009"></a>

### human-control-009 · turn/steer can succeed without persisting input while sampling is in flight

作者／组织：angelsbrood; fuller-stack-dev。类型：公开问题讨论。版本／日期：2026-08-26；rust-v0.148.0/0.149.1；后续v0.151.0报告；open。读取日：2026-10-13。

用途：报告者用受控sampling堵塞复现RPC已成功但steer只在pending queue，六分钟无对应user-item durable lifecycle。

选读范围：正文Bounded reproduction/Root cause/Verified minimal fix。限制：已读正文与相关评论，未自行复现；接收函数仅排队返回，不足以证明完整 mailbox 根因或所有采样期行为。

[公开原文](https://github.com/openai/codex/issues/40805)

<a id="human-control-012"></a>

### human-control-012 · Preserve late steer after turn finalization

作者／组织：friel-openai。类型：公开变更／提案。版本／日期：2026-06-27；head 875de1ec111beed474f590f0d329f7b9cf1835e3；open/unmerged verified。读取日：2026-10-13。

用途：补丁把final pending-input检查与取走active task放在同锁下，若有输入继续旧task而不是暴露idle。

选读范围：PR diff：on_task_finished / TaskFinishAction；task_finish_continues_late_input。限制：未合并，不能称正式已修复；已直接读diff，不以bot approval当验证

[公开原文](https://github.com/openai/codex/pull/30341)

<a id="human-control-013"></a>

### human-control-013 · Opening an active conversation in another VS Code window can silently transfer ownership and allow concurrent turns

作者／组织：alexchexes。类型：公开问题讨论。版本／日期：2026-08-14；extension 26.5727.51351；CLI 0.146.0-alpha.9.2；open。读取日：2026-10-13。

用途：报告第二窗口hydration跨await后覆盖follower角色成为owner，两app-server继续写同一rollout。

选读范围：正文timeline及Additional information。限制：日志和shipping code归因来自报告者，未本地复现；非普遍所有版本结论

[公开原文](https://github.com/openai/codex/issues/38629)

<a id="human-control-015"></a>

### human-control-015 · Rollback concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：rollback中断旧run并从数据库删除它，不能再restart；示例最终state只含新run。

选读范围：Introduction/Create runs/View run results。限制：示例只有天气搜索，未承诺撤销已执行外部副作用；不能将run删除当现实回滚

[公开原文](https://docs.langchain.com/langsmith/rollback-concurrent)

<a id="human-control-016"></a>

### human-control-016 · Interrupt concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：interrupt保留旧run及partial状态并标interrupted，第二run接续；区别于删除旧run的rollback。

选读范围：Introduction/Create runs/View run results。限制：只描述Agent Server；不把平台策略等同所有LangGraph运行；示例未覆盖remote取消

[公开原文](https://docs.langchain.com/langsmith/interrupt-concurrent)

<a id="human-control-017"></a>

### human-control-017 · Enqueue concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：enqueue让新消息成为后续run，当前文档说是Agent Server默认；最后state保留两次run成果。

选读范围：introduction/Create runs/results。限制：仅队列策略而非去重/持久ACK保证；JS例子语法不宜照抄

[公开原文](https://docs.langchain.com/langsmith/enqueue-concurrent)

<a id="human-control-018"></a>

### human-control-018 · Reject concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：reject拒绝第二run以409冲突并让原run继续；拒绝并不等同停止原工作。

选读范围：introduction/Create runs 409/results。限制：这是并发准入拒绝，不是工具审批拒绝，正文需明确两类reject

[公开原文](https://docs.langchain.com/langsmith/reject-concurrent)

<a id="human-control-021"></a>

### human-control-021 · Command queue

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：chat.send对既有session的输入先持久化DB再ACK；collect合并turn与源输入consumed同事务。

选读范围：Queue modes/Input durability/Queued-turn cancellation/Answering a pending question。限制：官方实现契约，未直接核完整SQLite实现；默认数值不是通用建议

[公开原文](https://docs.openclaw.ai/concepts/queue)

<a id="human-control-022"></a>

### human-control-022 · Messages and delivery

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：通用inbound dedupe是按agent/channel route/message ID的内存缓存，20分钟或5000条边界；不能推导跨重启保障。

选读范围：Inbound dedupe/Channel run ownership/Agent reactions/Silent replies。限制：OpenClaw特有行为；不应把所有群聊强制回复泛化；docs queue中durable ingress另有持久层

[公开原文](https://docs.openclaw.ai/concepts/messages)

<a id="human-control-025"></a>

### human-control-025 · Codex turn_input.rs steer_input implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：rust-v0.149.1；blob 424faf3c3a0e298dc5c8e1f562c919388adb9c0e。读取日：2026-10-13。

用途：在active_turn锁下检查expected turn及任务种类，nonempty input入pending queue后返回turn ID；本函数未等待模型采纳或rollout写盘。

选读范围：turn_input.rs 的 steer_input 实现（第 470–568 行）。限制：只读470–568行及函数；不据局部函数证明整个系统无其他去重

[公开原文](https://github.com/openai/codex/blob/rust-v0.149.1/codex-rs/core/src/session/turn_input.rs)

<a id="human-control-039"></a>

### human-control-039 · Interrupts: run boundaries and human resume

作者／组织：AG-UI。类型：官方文档／规范。版本／日期：current interrupt contract accessed 2026-10-13; no implementation version established。读取日：2026-10-13。

用途：RUN_FINISHED可带interrupt outcome，本次run结束仍需人类恢复；新run关联同thread和interrupt ID，pending时不得开始新普通input。

选读范围：正文 Core concepts / pending interrupts / resume payload / tool approval / idempotency and expiration。限制：协议契约而非实现审计；与OpenAI Agents允许部分pending审批续跑不同，不能混用

[公开原文](https://docs.ag-ui.com/concepts/interrupts)

<a id="human-control-041"></a>

### human-control-041 · Mid-turn steering over Responses WebSocket

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：current docs 2026-10-13; GPT-6 family, GPT-5.6 and earlier unsupported。读取日：2026-10-13。

用途：steer.accepted只表示入队；自动continuation等当前output和已启动hosted工具结束，不撤销原动作；每response的限额不等于整条任务限额。

选读范围：steer.accepted、pending / failed、工具等待、continuation 以及断线重连的说明。限制：仅当前指定模型/WebSocket产品契约；不要类推Codex app-server所有行为；未运行SDK示例

[公开原文](https://developers.openai.com/api/docs/guides/steering)

<a id="loop-context-018"></a>

### loop-context-018 · pi agent-loop.ts

作者／组织：Pi maintainers。类型：源码／仓库文档。版本／日期：main read 2026-10-13。读取日：2026-10-13。

用途：两层循环分别处理工具/steering与模型本欲停止后到来的follow-up；消息排队时机是loop语义的一部分。

阅读范围：runLoop; streamAssistantResponse; shouldTerminateToolBatch。限制：动态main未锁定commit；与2025博客的无max-step描述时代不同。

[公开原文](https://github.com/earendil-works/pi/blob/main/packages/agent/src/agent-loop.ts)

<a id="loop-context-025"></a>

### loop-context-025 · Cancellation gaps: between-turn compaction and pending input

作者／组织：tryingET / Pi issue。类型：公开问题讨论。版本／日期：2026-09, main 4d38031fb。读取日：2026-10-13。

用途：取消摘要尝试不一定取消整轮agent；在prepareNextTurn和input hook挂起时，stop/clearQueue后旧输入可能继续入历史或触发模型。

阅读范围：Original reproduction; clarified Escape behavior; timeline。限制：AI辅助报告有明确披露；未自行运行测试，维护者重新打开不等于全部根因已确认。

[公开原文](https://github.com/earendil-works/pi/issues/9783)

<a id="network-errors-026"></a>

### network-errors-026 · Python asyncio tasks and timeouts

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3.15 documentation as read 2026-10-13。读取日：2026-10-13。

用途：asyncio.timeout通过取消当前task转换TimeoutError；wait_for等待取消真正完成，实际墙钟可能超过配置时间。

选读范围：sections Task cancellation/Shielding/Timeouts/Waiting primitives。限制：读取的current页为Python3.15；timeout自3.11可用，具体TaskGroup新API不要倒推旧版本。

[公开原文](https://docs.python.org/3/library/asyncio-task.html)

<a id="network-errors-028"></a>

### network-errors-028 · AnyIO cancellation and timeouts

作者／组织：AnyIO maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：AnyIO level cancellation在已取消scope每个yield点重复触发，与asyncio edge语义不同；外层deadline可能更早。

选读范围：Differences/Timeouts/Finalization/Shielding。限制：未完整读所有scope corruption示例；结论限定取消、超时、finalization部分。

[公开原文](https://anyio.readthedocs.io/en/stable/cancellation.html)

<a id="network-errors-035"></a>

### network-errors-035 · AI SDK #15430: mid-body abort leaves result promises pending

作者／组织：daga-segwise; Vercel maintainers。类型：公开问题讨论。版本／日期：ai 6.0.180 with Bun in report。读取日：2026-10-13。

用途：header200后body被cancel，stream无finish事件，text/steps一直pending；外层AbortSignal也未使聚合promise落终态。

阅读范围：full body and maintainer reproduction/fix notes2026-07-07。限制：报告ai6.0.180/Bun，PR创建不等于已确认发布修复；与现行文档分开。

[公开原文](https://github.com/vercel/ai/issues/15430)

<a id="network-errors-039"></a>

### network-errors-039 · AI SDK stopping streams

作者／组织：Vercel。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：浏览器stop仅abort客户端HTTP；server runtime必须传播disconnect并把req.signal传到模型请求；Vercel Node须supportsCancellation。

阅读范围：full page。限制：平台能力随版本变化；是该SDK的resume契约，不是所有恢复系统互斥。

[公开原文](https://ai-sdk.dev/docs/advanced/stopping-streams)

<a id="runtime-boundaries-043"></a>

### runtime-boundaries-043 · Keep completed tool returns when sibling raises or run cancelled

作者／组织：Pydantic。类型：公开变更／提案。版本／日期：merged 2026-10-09 ad14dc9ae0cc5cb0b9261daa4507acfd63fea817; released v2.55.0。读取日：2026-10-13。

用途：parallel_ordered_events 先发出的慢工具失败时，后发工具可能已经执行完成但尚未记录；恢复历史会为遗失结果补入 interrupted 占位，模型可能因此再次调用已经完成的工具；不是runner保证自动重执行。修复 cancel_and_drain 后记录已成功但未记录的 task，保持异常/事件顺序。

选读范围：PR body; _tool_execution.py patch; tests/test_run_cancellation.py 3 new tests。限制：静态阅读发布修复与测试；未本地执行。 修复覆盖异常/取消路径成功task结果的留存，不证明硬进程崩溃与外部提交之间无丢失窗口。

[公开原文](https://github.com/pydantic/pydantic-ai/pull/10049)

[返回分类目录](README.md#topics)
