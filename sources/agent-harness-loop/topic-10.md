[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-10"></a>

## 10. 持久化与恢复：进程回来后，任务怎样继续

<a id="boundary-closure-007"></a>

### boundary-closure-007 · Restate TypeScript durable steps

作者／组织：Restate。类型：官方文档／规范。版本／日期：current TypeScript documentation, accessed 2026-10-13。读取日：2026-10-13。

用途：ctx.run 保存操作返回值到 execution log，重放使用记录；失败按策略重试，除非配置停止或 TerminalError。

选读范围：Run；Serialization；Error handling；deterministic UUID。限制：读 Run、Serialization、Error handling、deterministic UUID；把多操作拆为独立边界是由接口推出的设计建议，不证明单步外部成功与结果落盘之间无窗口。

[公开原文](https://docs.restate.dev/develop/ts/durable-steps)

<a id="boundary-closure-008"></a>

### boundary-closure-008 · Inngest step.run(): execute a step

作者／组织：Inngest。类型：官方文档／规范。版本／日期：TypeScript SDK v4 reference。读取日：2026-10-13。

用途：每次 step.run 有独立重试计数；step ID 用来记忆步骤状态，返回值以 JSON 序列化。

选读范围：参数；并行例子；Retries；Return values。限制：读参数、并行例子、Retries、Return values；独立重试不等于外部 exactly-once，工具内部未落盘子动作仍可能重做。

[公开原文](https://www.inngest.com/docs/reference/typescript/v4/functions/step-run)

<a id="boundary-closure-009"></a>

### boundary-closure-009 · Transactional outbox pattern, including sample code

作者／组织：AWS。类型：官方文档／规范。版本／日期：current guidance, accessed 2026-10-13。读取日：2026-10-13。

用途：业务记录与待发事件在同一数据库事务提交，另一个派发器发送；派发失败无需重做业务记录，重复通知仍须处理。

选读范围：Intent–Issues；outbox implementation；sample code。限制：读 Intent–Issues、outbox implementation、sample code；仅指出页面代码片段的契约缺口，不指控完整仓库或生产系统已丢消息；FIFO 说法不泛化为端到端 exactly-once。

[公开原文](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

<a id="boundary-closure-010"></a>

### boundary-closure-010 · NServiceBus Outbox processing and dispatch recovery

作者／组织：Particular Software。类型：官方文档／规范。版本／日期：NServiceBus core 9 documentation。读取日：2026-10-13。

用途：Phase 1 在事务中执行业务并保存待发消息；重投查到既有记录便跳过 handler，进入 Phase 2 派发。

选读范围：How it works；transaction scope；dispatch errors。限制：读 How it works、transaction scope、dispatch errors；不参加事务的邮件/文件系统操作不在保证内；失败进入 error queue 后仍需恢复触发，不是无限自动成功。

[公开原文](https://docs.particular.net/nservicebus/outbox/?version=core_9)

<a id="durable-orchestration-001"></a>

### durable-orchestration-001 · Scaling Managed Agents: Decoupling the brain from the hands

作者／组织：Lance Martin, Gabe Cemaj, Michael Cohen / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-04-08。读取日：2026-10-13。

用途：会话 append-only 日志、harness 和执行 sandbox 解耦后可独立恢复，容器死亡可作为工具错误处理，harness 通过 session 日志重启。

阅读范围：文章中会话日志、harness 与执行沙箱解耦，以及按需启动和首 token 延迟的段落。限制：供应商生产经验；未给 exactly-once 提交协议，不可据此承诺副作用精确一次

[公开原文](https://www.anthropic.com/engineering/managed-agents)

<a id="durable-orchestration-005"></a>

### durable-orchestration-005 · Persistence

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed 2026-10-13。读取日：2026-10-13。

用途：checkpointer 保存 thread-scoped graph state，store 保存跨 thread 应用数据，二者不能互换。

阅读范围：Checkpointer、thread-scoped state 与跨 thread store；内存保存器和保留策略的说明。限制：当前文档可变；durable-execution旧URL重定向至此，只计一次

[公开原文](https://docs.langchain.com/oss/python/langgraph/persistence)

<a id="durable-orchestration-006"></a>

### durable-orchestration-006 · Checkpointers

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed 2026-10-13; DeltaChannel &gt;=1.2 beta。读取日：2026-10-13。

用途：完整 checkpoint 在 super-step 边界提交，pending writes 保存同一步内已成功节点输出，恢复失败兄弟时无需重跑成功者。

选读范围：核心 checkpoint 概念、pending writes、恢复、耐久模式与 time travel；未逐行审读自定义 saver。限制：读取核心概念/恢复/耐久模式，未逐行审读自定义 saver 代码

[公开原文](https://docs.langchain.com/oss/python/langgraph/checkpointers)

<a id="durable-orchestration-008"></a>

### durable-orchestration-008 · Resuming one of two parallel interrupts inside a subgraph re-runs a sibling node that already completed #9106

作者／组织：Connor Imes and LangGraph contributors。类型：公开问题讨论。版本／日期：2026-09-29; reproductions 1.2.10/1.2.12 and main 2d942085。读取日：2026-10-13。

用途：嵌套图中逐个恢复两个审批，可能已完成的A副作用执行两遍，但最终graph state仍显示A/B各一次；仅断言最终状态会漏掉外部重复动作。

选读范围：问题正文、嵌套子图复现、重复副作用计数与 replay 判定的相关讨论。限制：公开issue及复现，未在独立复跑；当前仍open，候选PR未合并，评论有AI辅助内容，不能写成维护者已保证修复

[公开原文](https://github.com/langchain-ai/langgraph/issues/9106)

<a id="durable-orchestration-009"></a>

### durable-orchestration-009 · Scalar resume is accepted for multiple interrupts in one subgraph task #8579

作者／组织：DongBo / LangGraph contributors。类型：公开问题讨论。版本／日期：2026-08-09; langgraph1.2.10 main d56666f; closed2026-10-02。读取日：2026-10-13。

用途：同一个父任务pending write内含多个子interrupt时，旧逻辑只数首个ID，接受含糊scalar响应并按内部执行顺序投递到某一分支。

阅读范围：问题正文、多个 interrupt 的 scalar resume 复现及关闭前后的相关讨论。限制：issue已于Oct2关闭，最终教程应描述版本案例而非宣称所有当前版本仍有bug；尚未核验发布版本

[公开原文](https://github.com/langchain-ai/langgraph/issues/8579)

<a id="durable-orchestration-010"></a>

### durable-orchestration-010 · Resuming after interrupt doesn't reuse prior task outputs when interrupt is in subgraph #6792

作者／组织：venkatesh-sivaraman and LangGraph users。类型：公开问题讨论。版本／日期：2026-02-12; langgraph1.0.8。读取日：2026-10-13。

用途：同样entrypoint加一层父图包装后，interrupt前任务输出不复用，表现为步骤重跑及中断重复。

选读范围：问题正文与早期复现评论：entrypoint 外包父图后任务输出不复用。限制：已阅读正文和早期复现评论，未把未经证实评论中的根因推断当事实；与9106有关联但提供不同版本及API拓扑

[公开原文](https://github.com/langchain-ai/langgraph/issues/6792)

<a id="durable-orchestration-011"></a>

### durable-orchestration-011 · Temporal Workflow

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：恢复通过从头运行Workflow代码并读取历史事件重建状态，不是恢复内存快照；外部I/O和LLM放入Activity以记录返回值。

阅读范围：Workflow 恢复、事件历史、确定性与 Activity 返回值的说明。限制：Activity结果被记录后的replay复用不代表Activity尝试精确一次

[公开原文](https://docs.temporal.io/workflows)

<a id="durable-orchestration-012"></a>

### durable-orchestration-012 · Of course you can build dynamic AI agents with Temporal

作者／组织：Mason Egger, Steve Androulakis / Temporal。类型：作者／团队实践或研究文章。版本／日期：2025-11-12。读取日：2026-10-13。

用途：LLM生成下一步/计划由Activity记录，Workflow可依结果动态选择工具或子工作流；确定性不等于预定DAG。

阅读范围：文章中动态计划、Activity 记录模型决策及崩溃后恢复的讨论。限制：供应商宣传文，“没有Temporal只能从头开始”忽略其他持久化方案；工具副作用仍需幂等

[公开原文](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)

<a id="durable-orchestration-014"></a>

### durable-orchestration-014 · Continue-As-New

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Continue-As-New把必要状态作为参数传入新执行，同Workflow ID但新Run ID与新history。

阅读范围：全文 What is / When to Continue-As-New。限制：run身份变化需要与外部关联ID区分，不能当无状态重启

[公开原文](https://docs.temporal.io/workflow-execution/continue-as-new)

<a id="durable-orchestration-015"></a>

### durable-orchestration-015 · Activities

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Activity是可非确定性外部操作，但失败会从初始状态重试，须幂等；heartbeat detail可供下次尝试自行接续。

阅读范围：正文 Activities定义、retry/heartbeat段。限制：仅Activity概念层；外部effect提交协议需应用提供

[公开原文](https://docs.temporal.io/activities)

<a id="durable-orchestration-021"></a>

### durable-orchestration-021 · What we’ve learned building cloud agents

作者／组织：Josh Ma / Cursor。类型：作者／团队实践或研究文章。版本／日期：2026; accessed2026-10-13。读取日：2026-10-13。

用途：由work-stealing进程loop迁到Temporal后逐步重划activity边界，并把永恒agent workflow改成每任务结束的较短workflow以便升级。

阅读范围：正文 Long-running agents / Decoupling / Development environment。限制：可靠性及规模数值为作者自报，无外部SLA测量；架构机制比数字更适合正文

[公开原文](https://cursor.com/blog/cloud-agent-lessons)

<a id="durable-orchestration-025"></a>

### durable-orchestration-025 · AI Agents should be serverless and durable

作者／组织：Giselle van Dongen, Igal Shilman / Restate。类型：作者／团队实践或研究文章。版本／日期：2025-10-09。读取日：2026-10-13。

用途：等待人工的durable promise允许进程挂起，恢复通过journal取得已完成LLM与tool结果；等待期限和唤醒条件也是持久状态。

阅读范围：完整主体 Cost efficiency / Safe evolution / SDK integration。限制：供应商比较夸张，其他orchestrator也可serverless；几行集成不会自动覆盖未标记的外部副作用

[公开原文](https://restate.dev/blog/resilient-serverless-agents)

<a id="durable-orchestration-026"></a>

### durable-orchestration-026 · Durable Orchestration for AI Agents with Restate and OpenAI SDK

作者／组织：Restate Team。类型：作者／团队实践或研究文章。版本／日期：2026-01-15。读取日：2026-10-13。

用途：agent SDK可作为loop定义层，durable runtime负责session、并发、审批timer和跨agent调用，二者边界可以独立。

选读范围：Building Blocks / Beyond Basics prose。限制：阅读技术解释正文，未审阅缺失的动态示例代码；几行集成不自动覆盖未标记的外部副作用。

[公开原文](https://restate.dev/blog/durable-orchestration-for-ai-agents-with-restate-and-openai-sdk)

<a id="durable-orchestration-027"></a>

### durable-orchestration-027 · Agent checkpointing is far from production-grade resiliency

作者／组织：Giselle van Dongen / Restate。类型：作者／团队实践或研究文章。版本／日期：2026-06-15。读取日：2026-10-13。

用途：checkpoint只是恢复资料，仍需独立故障发现者/重派发者、持久retry日程、唤醒、版本路由与zombie fencing。

阅读范围：完整主体 iceberg sections。限制：文中对所有agent SDK和单写者必须的绝对断言是竞争厂商主张，需收窄为同一可变状态对象的默认设计；不采纳80%量化及保证任何代码必完成

[公开原文](https://restate.dev/blog/why-checkpointing-is-not-production-grade-durable-execution)

<a id="durable-orchestration-028"></a>

### durable-orchestration-028 · Persistent Agent Sessions

作者／组织：Restate。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：同key Virtual Object独占写handler串行，多个session可并行，shared只读handler可与message同时执行。

选读范围：How it works / TS chat / Built-in concurrency / Concurrent retrieval / Steerable agents。限制：已读概念、TS例子和并发/steering尾部；未逐个读7种SDK重复示例

[公开原文](https://docs.restate.dev/ai/patterns/sessions)

<a id="durable-orchestration-030"></a>

### durable-orchestration-030 · A reference agent architecture

作者／组织：Restate。类型：源码／仓库文档。版本／日期：main accessed2026-10-13; reference implementation。读取日：2026-10-13。

用途：controller Agent负责活动turn/输入队列/审批，AgentSession负责transcript和执行loop；二者按同agentId区分所有权。

阅读范围：README 架构正文：Agent / AgentSession、steer / interrupt、sequence 与 revision。限制：新参考实现，不是独立验证生产案例；源码README含实质架构而非仅目录说明

[公开原文](https://github.com/restatedev/agent)

<a id="durable-orchestration-035"></a>

### durable-orchestration-035 · AutoGen teams API: pause/resume and state

作者／组织：Microsoft AutoGen。类型：官方文档／规范。版本／日期：stable; pause/state changes v0.4.9。读取日：2026-10-13。

用途：pause仅调用各agent的on_pause，默认可为空操作且run不会返回；它不是进程冻结或完成。

选读范围：BaseGroupChat.pause, resume, save_state, load_state。限制：仅读相关API片段，未声称整个团队实现审计

[公开原文](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html)

<a id="durable-orchestration-036"></a>

### durable-orchestration-036 · Agent state serialization and save/load

作者／组织：Eric Zhu and AutoGen maintainers。类型：公开问题讨论。版本／日期：2024-11-08; closed2024-12-04 via4436。读取日：2026-10-13。

用途：序列化运行状态不等于完整序列化agent对象；加载仍需先构造正确类型和配置。

阅读范围：Issue body and maintainers discussion。限制：设计讨论时期版本，不据此声称当前缺功能

[公开原文](https://github.com/microsoft/autogen/issues/4100)

<a id="durable-orchestration-041"></a>

### durable-orchestration-041 · Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers

作者／组织：Sajjad Khan。类型：研究论文。版本／日期：v1 2026-08-04。读取日：2026-10-13。

用途：恢复至少要区分继续原分支、显式新fork、审批值消费和外部effect提交；单一resumeAPI无法从checkpointID推断所有意图。

选读范围：https://arxiv.org/html/2608.03836v1 sectionsIII,VI-G,IX。限制：独立研究预印本且未本地复现；有限TLA+状态与抽象模型、SQLiteledger不等于所有外部服务；其称6792已修复与live issue状态不一致，产品结论需以当前代码核查

[公开原文](https://arxiv.org/abs/2608.03836)

<a id="durable-orchestration-044"></a>

### durable-orchestration-044 · Durable Execution with Temporal

作者／组织：Pydantic AI。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：外层run循环在workflow，LLM/tool/MCP在Activity；跨进程对象必须序列化，不能把内存MCP连接复用给另一个worker。

选读范围：Temporal Integration Considerations / Agent Run Context and Dependencies / Large Payloads / Streaming / Activity Configuration。限制：在线文档可变且部分标题与搜索缓存不同；具体默认期限非通用值，未读全部demo

[公开原文](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/)

<a id="durable-orchestration-046"></a>

### durable-orchestration-046 · Actor Fault Tolerance

作者／组织：Ray contributors。类型：官方文档／规范。版本／日期：latest2.59 accessed2026-10-13。读取日：2026-10-13。

用途：max_restarts重跑构造器而非恢复应用状态，checkpoint要主动保存且跨节点可读。

阅读范围：Actor process failure / Actor checkpointing / Actor creator failure / Unavailable actors。限制：Ray默认行为需按版本核对；文中简单文件checkpoint示例没有原子写/外部effect保证

[公开原文](https://docs.ray.io/en/latest/ray-core/fault_tolerance/actors.html)

<a id="durable-orchestration-047"></a>

### durable-orchestration-047 · How to think about durable execution

作者／组织：Alexander Belanger。类型：作者／团队实践或研究文章。版本／日期：2025-12-11。读取日：2026-10-13。

用途：作者从Porter基础设施编排说明单个易幂等任务可能只需持久队列，多步跨系统中间状态才使durable workflow收益明显。

阅读范围：Simple tasks / Complex tasks / Durable execution / It is not a silver bullet。限制：厂商作者经验；stateless或调用外部API并不自动幂等，文章简例需附前提；非所有任务都需框架

[公开原文](https://hatchet.run/blog/durable-execution)

<a id="durable-orchestration-051"></a>

### durable-orchestration-051 · Trigger.dev v3: Durable Serverless functions. No timeouts.

作者／组织：Trigger.dev engineering。类型：作者／团队实践或研究文章。版本／日期：2024 v3 announcement。读取日：2026-10-13。

用途：durability并非只有event replay：CRIU可在支持的等待边界冻结容器进程并稍后恢复，保存模型不同于graph state checkpoint。

阅读范围：How does this work / Checkpoints and Restoring / Versioning / Open-source and self-hosting。限制：历史v3设计，不把旧API/No timeouts标题当当前产品无任何上限；付款示例无幂等key，不能作为安全交易模板

[公开原文](https://trigger.dev/blog/v3-announcement)

<a id="durable-orchestration-052"></a>

### durable-orchestration-052 · Lifecycle of a Durable Object

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：updated2026-09-30。读取日：2026-10-13。

用途：持久对象身份不保证内存对象常驻；hibernation保持特定WebSocket但构造器再执行，普通JS定时器与未完成IO会妨碍休眠。

阅读范围：Lifecycle state transitions / Shutdown behavior / Working without shutdown hooks。限制：示例data.forEach(async...)存在不等待回调和乱序进度风险，不能抄为顺序恢复模板；持久化进度仍不覆盖effect-commit原子性

[公开原文](https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/)

<a id="durable-orchestration-053"></a>

### durable-orchestration-053 · Worker Versioning

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：pin运行到同一build避免新代码解释旧历史；代价是必须保留旧worker，长任务可在Continue-As-New边界升级。

阅读范围：Pinned 与 Auto-Upgrade、replay 兼容、版本保留、升级边界及队列阻塞的说明。限制：特定Temporal功能默认和版本要求可变；只说明机制不将所有系统都要求pin

[公开原文](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning)

<a id="durable-orchestration-057"></a>

### durable-orchestration-057 · durability=sync: put_writes/put persistence order is unenforced

作者／组织：Sajjad Khan and LangGraph contributors。类型：公开问题讨论。版本／日期：opened2026-06-10; 1.2.0/1.2.4 and Sep12 1.2.11 reproduction; open2026-10-13。读取日：2026-10-13。

用途：sync循环等待checkpoint future不自动给所有pending write future建立先后关系；故障恢复选择重放或重执行可受线程调度影响。

选读范围：问题正文、复现与早期讨论，以及 9 月 12 日 PostgreSQL probe 说明；未读全部隐藏评论。限制：未本地运行；部分复现评论AI-assisted且PR8055曾因assignment gate关闭，不把修复提案当已合并；与 [durable-orchestration-041](topic-10.md#durable-orchestration-041)论文同作者并非独立实验交叉背书

[公开原文](https://github.com/langchain-ai/langgraph/issues/8039)

<a id="durable-orchestration-058"></a>

### durable-orchestration-058 · How to do distributed locking

作者／组织：Martin Kleppmann。类型：作者／团队实践或研究文章。版本／日期：2016-02-08。读取日：2026-10-13。

用途：lease到期不代表旧worker已停止；GC暂停、网络迟到让旧attempt在新owner开始后仍写入。

选读范围：效率／正确性区别，以及租约、资源保护和 fencing 的章节；未采用后半 Redlock 专项争论。限制：一般分布式机制只映射到长任务控制面，不展开Redis产品争论；外部系统不支持fencing时需其他幂等/事务/对账边界

[公开原文](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

<a id="human-control-007"></a>

### human-control-007 · Chatbot Message Persistence

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 current docs。读取日：2026-10-13。

用途：默认backpressure使客户端断开可能终止LLM流；consumeStream在后端持续消费可使onEnd及保存继续执行。

选读范围：opening caveat、Handling client disconnects。限制：只读开篇及Handling client disconnects；服务端进程/平台寿命依然是外部前提

[公开原文](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)

<a id="human-control-020"></a>

### human-control-020 · File checkpointing

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current docs；link安全跳过要求Claude Code v2.1.216+。读取日：2026-10-13。

用途：rewindFiles只恢复文件不恢复对话；只跟踪Write/Edit/NotebookEdit，不含Bash及多数子agent写。

选读范围：opening/How checkpointing works/Implement。限制：文件恢复不涵盖已发消息/数据库/远端commit；只实读开篇/How/Implement及restore要求

[公开原文](https://code.claude.com/docs/en/agent-sdk/file-checkpointing)

<a id="human-control-033"></a>

### human-control-033 · Channel inbound lifecycle and delivery settlement

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current plugin SDK docs accessed 2026-10-13。读取日：2026-10-13。

用途：外部builder不能自行铸造参与者provenance；ingress resolver绑定生命周期epoch、agent/session/message/event/admission，异步准备后必须assertActive。

选读范围：首15k正文，ingress identity / lifecycle / acknowledgment / delivery finalization。限制：官方接口契约，非独立执行验证；SDK细节与平台adapter实现关联

[公开原文](https://docs.openclaw.ai/plugins/sdk-channel-inbound)

<a id="human-control-040"></a>

### human-control-040 · Durable chat admission and control-race tests

作者／组织：OpenClaw。类型：源码／仓库文档。版本／日期：main accessed 2026-10-13; primary blob 106defff4fce9851fc98eccfcc617867a7d4a12f。读取日：2026-10-13。

用途：真实存储fixture在清空瞬态dedupe cache后重试已collect source，断言ACK cached且不再次dispatch、不追加transcript；同key换payload/recipient拒绝。

选读范围：pending-inputs、chat-send-ordering 与 approval-run-cancellation 测试：重试、取消和会话替换。限制：已读源码未运行；单进程SQLite fixture/cache清除不等于实测进程崩溃；派发mock不证明真实provider副作用幂等；同测试族合并一个计数

[公开原文](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)

<a id="practitioner-lessons-004"></a>

### practitioner-lessons-004 · 007: What we have learned when we built our own Agent Harness

作者／组织：Anil Can Baykal; Ali Onur Geven / Integral。类型：作者／团队实践或研究文章。版本／日期：2026-07-02。读取日：2026-10-13。

用途：事实：利用既有事件基础设施；runner无状态，repo、issue、PR等外部制品承担跨轮交接；prompt独立版本发布。

阅读范围：The orchestration we feared; Conventions; The snake eats its own tail。限制：无状态runner不等于系统无状态，也未证明副作用exactly-once；judge故障fail-open需按风险决定，不宜推广至资金动作。

[公开原文](https://engineering.integral.de/posts/007-agent-harness/)

<a id="practitioner-lessons-011"></a>

### practitioner-lessons-011 · Inside Replit’s Snapshot Engine: The Tech Making AI Agents Safe

作者／组织：Connor Brewster; Luis Héctor Chávez / Replit。类型：作者／团队实践或研究文章。版本／日期：2025-12-18。读取日：2026-10-13。

用途：事实：不可变16MiB块+manifest以copy-on-write实现快照；git提交、数据库状态、agent状态需作为不同状态面考虑。

阅读范围：Bottomless Storage; Versioning Agent Code Changes; Forkable Databases。限制：文中Future的并行模拟与原子采纳属展望；快照覆盖本地受管状态，不自然覆盖邮件、付款等外部副作用。

[公开原文](https://replit.com/blog/inside-replits-snapshot-engine)

<a id="practitioner-lessons-022"></a>

### practitioner-lessons-022 · Building an AI Agent Platform

作者／组织：Chase Dovey。类型：作者／团队实践或研究文章。版本／日期：2026-03-15。读取日：2026-10-13。

用途：事实：TinyClaw统一入口处理消息去重、短消息合并和策略；用channel+message ID的60秒内存表防重复webhook。

选读范围：Message Pipeline; Agent Runner; Session Management。限制：读前14000字符；内存TTL去重不耐重启，过期锁强拆无fencing，丢弃坏行可能丢状态，regex不能保证注入/SSRF安全；不采纳自动允许或绕限建议。

[公开原文](https://cdovey.dev/blog/building-an-ai-agent-platform-from-scratch/)

<a id="practitioner-lessons-026"></a>

### practitioner-lessons-026 · Absurd Workflows: Durable Execution With Just Postgres

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2025-11-03。读取日：2026-10-13。

用途：事实：Postgres队列和checkpoint状态存储，agent每轮步骤存增量消息；失败重试task，已完成step从缓存加载。

阅读范围：With Agents; Events and Sleeps。限制：作者简述无重复工作不能理解为外部副作用exactly-once；整个singleStep包模型和tool时，checkpoint前崩溃可重复执行。

[公开原文](https://lucumr.pocoo.org/2025/11/3/absurd-workflows/)

<a id="practitioner-lessons-027"></a>

### practitioner-lessons-027 · Absurd In Production

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2026-04-04。读取日：2026-10-13。

用途：事实：五个月生产后补了claim/lease/watchdog/deadlock/event race边界；beginStep/completeStep适配before/after hooks。

阅读范围：What Changed; What Held Up; What’s Still Missing。限制：不将“步骤外可随机”泛化为可随意改变恢复控制流；按step缓存仍需稳定标识和代码兼容。

[公开原文](https://lucumr.pocoo.org/2026/4/4/absurd-in-production/)

<a id="practitioner-lessons-031"></a>

### practitioner-lessons-031 · Building Spectre: Internal Collaborative Cloud Agent Platform

作者／组织：Joey Wang; Gabe Pereyra / Harvey。类型：作者／团队实践或研究文章。版本／日期：2026-04-07。读取日：2026-10-13。

用途：事实：durable run保存owner、sharing、附件、轨迹、制品和provider session引用；follow-up启动新worker并恢复session，非保活旧容器。

选读范围：Durable runs ephemeral workers; Sandboxes; Scheduled Runs。限制：阅读前13500字符至What Spectre Taught Us；控制面持久状态仍需事务/去重；共享可见性不自动等于访问授权。

[公开原文](https://www.harvey.ai/blog/building-spectre-internal-collaborative-cloud-agent-platform)

<a id="runtime-boundaries-010"></a>

### runtime-boundaries-010 · fsync durability and delayed disk-full errors

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19 / 2026-02-08。读取日：2026-10-13。

用途：文件fsync不保证目录项已落盘，需目录fd单独fsync；ENOSPC/EDQUOT可在同步时才报告。checkpoint完成信号若早于数据与目录提交，崩溃后可能无法恢复。

选读范围：DESCRIPTION L39-67; ERRORS L72-98。限制：文件系统/硬件契约仍有差异

[公开原文](https://man7.org/linux/man-pages/man2/fsync.2.html)

<a id="runtime-boundaries-015"></a>

### runtime-boundaries-015 · LangGraph graph migrations

作者／组织：LangChain。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。

用途：被interrupt线程不能删除/重命名即将进入的节点；重命名state key会丢旧值，改变类型可能不兼容。技术上可恢复也不保证业务行为兼容，应在state记录行为版本。

选读范围：Graph migrations L898-908; runtime context。限制：partial；仅迁移和runtime context

[公开原文](https://docs.langchain.com/oss/python/langgraph/graph-api)

<a id="runtime-boundaries-019"></a>

### runtime-boundaries-019 · Transcript JSONL corruption; records spliced by unsynchronized writers

作者／组织：NubeBuster。类型：公开问题讨论。版本／日期：created 2026-07-28T03:49:43Z; updated 2026-10-11T06:18:57Z; open。读取日：2026-10-13。

用途：维护者确认多个session writer缺共享锁是real bug；报告者后续实际短写probe发现compaction写忽略bytesWritten，sync+rename仍会原子替换成不完整文件。最新报告2.1.292仍发生；未核验闭源bundle，短写具体根因属报告者分析。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/anthropics/claude-code/issues/81843)

<a id="runtime-boundaries-021"></a>

### runtime-boundaries-021 · Toggling defer on a fan-in node breaks resumed threads: silent barrier corruption one way, ValueError the other

作者／组织：serhiy-bzhezytskyy。类型：公开问题讨论。版本／日期：created 2026-08-14T05:30:15Z; updated 2026-09-24T15:35:16Z; open。读取日：2026-10-13。

用途：切defer改变barrier checkpoint形状，恢复可静默永不触发。作者承认最初unit tests只构造内存tuple没走serde，漏掉tuple变list及finished flag；实际checkpoint端到端测试推翻先前修复。issue仍open。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/langchain-ai/langgraph/issues/8618)

<a id="runtime-boundaries-022"></a>

### runtime-boundaries-022 · \[CLI\] All tools become unavailable after resuming a pre-upgrade session; `/model` restores them

作者／组织：leo9344。类型：公开问题讨论。版本／日期：created 2026-08-28T04:42:35Z; updated 2026-10-11T15:45:17Z; open。读取日：2026-10-13。

用途：升级后resume旧session工具不可见，new session正常，model切换有时修复。初报者一度称0.152.1解决，后在0.153.4再次遇到；不能把单个成功反馈写成已彻底修复。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/openai/codex/issues/41265)

<a id="runtime-boundaries-023"></a>

### runtime-boundaries-023 · LangGraph backward compatibility

作者／组织：LangChain。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：每次resume使用最新graph，技术兼容与业务兼容不同；推荐起始state锁behavior version。Functional API/task/interrupt以位置匹配cache，新增重排会误用旧结果；纯node无此位置约束但副作用仍要幂等。

选读范围：technical/business/non-determinism。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.langchain.com/oss/python/langgraph/backward-compatibility)

<a id="runtime-boundaries-024"></a>

### runtime-boundaries-024 · SQLite atomic commit

作者／组织：SQLite。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：rollback journal先于数据库修改持久化，随后DB同步与commit点共同保证崩溃恢复；OS缓存中的write不是持久化。保证依赖VFS/同步/文件系统硬件假设，不能将设置为OFF后仍称durable。

选读范围：Hardware assumptions; single file commit 3.5-3.11。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://www.sqlite.org/atomiccommit.html)

<a id="runtime-boundaries-025"></a>

### runtime-boundaries-025 · SQLite corruption failure boundaries

作者／组织：SQLite。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：运行中直接copy数据库可混合新旧页；恢复需要hot journal/WAL，删掉辅助文件破坏恢复；fork后继承连接、不同锁协议、在用数据库改名都是例外。沙箱快照/备份必须用一致性方式。

选读范围：backup/journals; locking; unlink; fork; sync。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://www.sqlite.org/howtocorrupt.html)

<a id="runtime-boundaries-032"></a>

### runtime-boundaries-032 · Temporal Python workflow versioning

作者／组织：Temporal。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：workflow逻辑变化可能破坏replay，worker versioning与patched marker是不同方案；移除patch需经历deprecated与旧history保留窗口，new worker通过测试不等于旧run安全。

选读范围：patch/deprecate/remove; replay testing。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.temporal.io/develop/python/workflows/versioning)

<a id="runtime-boundaries-033"></a>

### runtime-boundaries-033 · DBOS workflow code upgrades

作者／组织：DBOS。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：默认workflow源代码hash版本只恢复匹配任务；蓝绿要保留旧进程排空。patch实际由历史当前位置是否已有输出决定，旧workflow尚未到达变更点也可选新分支，不能只按创建时间简化。

选读范围：Patching internals; versioning; blue-green。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.dbos.dev/python/tutorials/upgrading-workflows)

<a id="runtime-boundaries-034"></a>

### runtime-boundaries-034 · Restate immutable deployment versioning

作者／组织：Restate。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：请求重试pin原endpoint，新版本只帮助新请求；修旧run要pause后显式新deployment恢复且journal兼容。Virtual Object state跨版本持久，pin代码不取消state schema兼容责任。

选读范围：immutable deployments; state; migrate in-flight invocations。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.restate.dev/services/versioning)

<a id="runtime-boundaries-035"></a>

### runtime-boundaries-035 · Inngest step identity across deployment

作者／组织：Inngest。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：resume用当前代码按stable step ID复用结果；循环还包含occurrence counter。改ID会重新执行副作用，major变更需新function并让触发条件互斥，验证paused旧run与fresh新run两条路。

选读范围：How versioning works; table; test paused run。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://www.inngest.com/docs/durable-execution/guides-and-advanced/versioning)

<a id="runtime-boundaries-037"></a>

### runtime-boundaries-037 · OpenAI Agents v0.23.1 RunState schema

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v0.23.1 / c4a1d047b22488234b2ba81056e1b9b8db2127a5。读取日：2026-10-13。

用途：当前 RunState schema1.18，新SDK接受其支持的已发布旧schema，旧SDK可能拒绝更新schema；tool origin/agent/server/审批身份陆续纳入。resumed工具已做但Session append失败保存pending batch，恢复在exclusive session中对账而非重跑工具。

选读范围：schema policy L205-262; RunState docstring L790-810; _validate_run_state_schema_version L4045-4063。限制：静态核验，未运行完整SDK测试；已核 tag→commit

[公开原文](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_state.py)

<a id="runtime-boundaries-041"></a>

### runtime-boundaries-041 · Record interrupted turns in managed daemon recovery snapshots

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-15; 4d2807023aae3ee317d39a9868fb187618699df2。读取日：2026-10-13。

用途：daemon 恢复仅存 thread ID 不足：输入已接受但尚未形成模型回复时，还要保存活动 turn、output schema、service tier。把恢复数据原子写入同一候选数组，避免 sidecar 与任务列表不一致；shutdown 不能等待已阻塞 rollout writer。

选读范围：PR body and daemon_recovery.rs patch。限制：已合并；未核发布tag。

[公开原文](https://github.com/openai/codex/pull/45807)

<a id="runtime-boundaries-044"></a>

### runtime-boundaries-044 · write(2) Linux manual

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19。读取日：2026-10-13。

用途：write 成功也可能只写部分字节（磁盘满、文件限制、信号中断）；必须推进 offset 并补余量。成功返回不保证持久存储，延迟错误可到 fsync/close 才出现，JSONL 一次write不能当完整记录保证。

选读范围：DESCRIPTION partial writes; NOTES durability。限制：POSIX/Linux 系统调用契约，不能直接等同高级 appendFile 的重试行为。

[公开原文](https://man7.org/linux/man-pages/man2/write.2.html)

<a id="runtime-boundaries-045"></a>

### runtime-boundaries-045 · rename(2) Linux manual

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19。读取日：2026-10-13。

用途：rename 的原子性保证目标名称替换时无缺失窗口，不保证新文件内容完整或断电耐久；跨挂载点 EXDEV，不能假设临时目录文件可原子移入任意目标。

选读范围：DESCRIPTION atomic replacement; ERRORS EXDEV。限制：与 fsync(2)、write(2) 合读才得 durable-save 结论。

[公开原文](https://man7.org/linux/man-pages/man2/rename.2.html)

<a id="runtime-boundaries-051"></a>

### runtime-boundaries-051 · Managing State

作者／组织：Microsoft AutoGen。类型：官方文档／规范。版本／日期：stable tutorial; state examples version1.0.0。读取日：2026-10-13。

用途：AssistantAgent 默认状态只含 model_context，自定义agent默认 save/load 空状态；团队状态保存各agent/manager的消息与轮次，不自动捕获外部工具进程。示例 json.dump 只是序列化持久化教学，不能推出原子替换/崩溃恢复。

选读范围：Saving and Loading Agents note; team state payload; Persisting State example。限制：文档样例不等稳定跨版本schema契约。

[公开原文](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/state.html)

<a id="runtime-boundaries-060"></a>

### runtime-boundaries-060 · Save a sandbox automatically

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：2026-09-30 / SDK1.0。读取日：2026-10-13。

用途：save与stop不能视为单步：snapshot期间可来新请求，保存后重新检查busy/lastActivity才决定destroy；alarm失败/部署中断重试，只能恢复最后checkpoint。

选读范围：Save before stop steps2–3; activeDuringSave; limitations。限制：官方示例机制，不证明一般数据库应用一致性快照。

[公开原文](https://developers.cloudflare.com/sandbox/files/save-a-sandbox-automatically/)

<a id="runtime-boundaries-063"></a>

### runtime-boundaries-063 · Work with sessions

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current2026-10-13; CLI lookup boundary2.1.223。读取日：2026-10-13。

用途：session只持久conversation，不持久filesystem；跨host需session-store或搬transcript并匹配cwd/lookup语义，session ID本身不是远端持久存储。CLI2.1.223前搜索范围限制在当前project/worktrees，SDK bundled CLI不同会改变恢复结果。

选读范围：Opening distinction; Resume across hosts。限制：platform.claude.com旧URL重定向；不声称会话恢复能还原外部工具状态。

[公开原文](https://code.claude.com/docs/en/agent-sdk/sessions)

<a id="runtime-boundaries-064"></a>

### runtime-boundaries-064 · Hot-reload user config when batch writing config

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged / a684a36091d70e1d8720fb99aafecd2a41ea7207。读取日：2026-10-13。

用途：config落盘与运行任务使用新配置是不同阶段：显式reloadUserConfig后遍历loaded threads提交ReloadUserConfig；提交失败只warn且batch_write仍返回写成功。该实现并不等于所有in-flight turn在同一时刻切换配置。

选读范围：config_api.rs UserConfigReloader/ConfigApi::batch_write; RecordingUserConfigReloader test。限制：已合并但未核发布tag；测试断言reloader被调用，未证明各线程已应用。

[公开原文](https://github.com/openai/codex/pull/13839)

<a id="traces-eval-064"></a>

### traces-eval-064 · Workflow Definition

作者／组织：Temporal。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：durable workflow replay验证相同Command序列与Event History，而非让LLM重新生成完全相同文本；外部API/LLM/DB应隔离成Activities。

选读范围：Deterministic constraints; Code changes; Intrinsic nondeterminism; Versioning。限制：读完整机制正文略七语言实现例；Activity执行仍有重试/副作用语义，不能推出外部effect全局恰好一次。

[公开原文](https://docs.temporal.io/workflow-definition)

[返回分类目录](README.md#topics)
