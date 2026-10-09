# 08 · 会话状态、后台任务与前端交互

> 范围：会话怎么存、怎么升级、怎么分叉；长任务怎么跑、断了怎么续、定时和外部触发、等人几天；agent 到界面的事件、断线续流、多端；运行中插话和"做完了"在接口和界面上怎么做；日常测试替身。
>
> 已经在别处讲过的，这里只引用、不重复：
> - 流式中途断开、SSE 心跳、反向代理超时、后台模式按 `sequence_number` 续传、`Last-Event-ID`：见 [02](02-reliability.md) 第 5、10 节和决定 3。
> - Temporal 默认重试无限次、重试放在哪一层：见 [02](02-reliability.md) 第 1 节、决定 1。
> - 会话写入的乐观并发：见 [02](02-reliability.md) 第二节第 8 条。
> - "历史就是状态"、每步存检查点、孤儿工具调用修补、审批中断、插话和完成判定的主循环原理：见 [03](03-agent-loop-context.md) 第 4、10、12、13 节和第二节第 1 条。
> - `previous_response_id` 与服务端存 30 天：见 [01](01-llm-protocols.md)。
> - Markdown 图片外泄等渲染安全：见 [04](04-eval-observability-security.md)。
>
> 证据来源：一半是公开文档，一半是开源代码。代码固定在 2026-10-09（Asia/Shanghai）拉取的提交上，链接都指向具体提交，代码以后变了也能对上。所有带数字的事实，核对日期都是 2026-10-09。

---

## 一、知识拆解

### 1. 会话数据模型

**1.1 两种基本形态**
- **消息表**：每行一条消息（user / assistant / tool），按顺序读出来直接拼成模型请求。简单，适合"聊天记录"。pydantic-ai 的持久化文档原话是"存聊天线程，一个 jsonb 列就够了"，每轮只追加 `new_messages()`，不要每次覆盖整段。
- **事件流**：每次变化（开始一轮、工具开始、工具输出增量、审批请求、压缩、回滚……）都是一条事件，"当前状态"是把事件按顺序重放算出来的。Codex 的 rollout（每会话一个 JSONL 文件）、opencode 的 sync 模块、OpenHands 都是这一类。好处是界面重连、换设备、审计、调试都能从同一份事件里得到；代价是要写"投影"（把事件折叠成状态）和处理事件格式升级。

**1.2 "给模型看的"和"给人看的"是两份视图**
存下来的东西和每次发给模型的东西不应该一样。几个开源实现都在请求前做一次"投影"：
- opencode `message-v2.ts` 在把存储的消息转成模型消息时：
  - 出错的 assistant 消息跳过，除非是用户中止且已有真实内容；
  - 厂商私有元数据（签名、providerMetadata）只在**同一个模型**时回放，换了模型就把 reasoning 降级成普通文本；
  - 已被压缩掉的工具输出替换成 `[Old tool result content cleared]`；
  - 状态还是 pending/running 的工具调用（进程挂了、用户中止）补一个 `[Tool execution was interrupted]` 的错误结果；有部分输出的保留部分输出；
  - 厂商不支持"工具结果里带图片"时，把图片挪到一条 user 消息里。
- Goose 的消息带两个可见性开关 `user_visible` / `agent_visible`，上下文压缩时生成"只给模型看"的摘要、把原消息标成"模型不可见但用户可见"。界面还能完整显示，模型只看到摘要。
- Codex 的 `rollout/src/policy.rs` 决定哪些事件落盘：命令和 MCP 工具输出落盘时截到 64KB（`PERSISTED_COMMAND_OUTPUT_MAX_BYTES = 64 * 1024`，中间插 `... command output truncated for persistence ...`）；喂给"记忆"功能的又是另一套过滤（去掉 developer 消息和推理内容）。

**1.3 历史和元数据分开写**
Codex `thread-store` 的接口里，`append_items` 只追加历史，标题、模型、归档状态等元数据走单独的更新接口。本地实现是"JSONL 存历史 + SQLite 存可搜索的元数据"。原因很实际：列表页、搜索要快，不能每次扫 JSONL；但历史文件要保持只追加。

**1.4 单写者**
一个会话同一时刻只能有一个进程在写。
- Codex：每个会话一个写锁文件（`rollout/src/writer_lock.rs`），第二个写者直接报 `thread … already has an active writer`，崩溃留下的过期锁会被清理。
- opencode：每会话一个 Runner，忙时再提交直接抛 `BusyError`（`run-state.ts`）。取消会顺带取消子会话里的后台任务。
- 服务端常见做法：按会话 id 路由到唯一执行者（Cloudflare Durable Object 单线程、全局唯一名字；Restate 的 Virtual Object 按 key 单写），或数据库行锁 / 版本号（[02](02-reliability.md) 第二节第 8 条）。

**1.5 状态放内存还是落盘**
opencode 的会话运行状态（`idle | busy | retry{attempt, message, next}`）只在内存里，重启就没了。这对本地 CLI 没问题，对服务端就是坑：进程重启后数据库里那个会话"看起来没在跑"，但也没有任何结束标记。服务端需要把"运行中"写进库，并配合租约/心跳判断是不是真的还活着（见第 5 节）。

### 2. 存储格式的版本与迁移

**2.1 读老文件要宽容，遇到看不懂的模式要拒绝**
Codex 读 rollout（`recorder.rs` 的 `load_rollout_items`）：
- 单行解析失败就跳过并计数（最常见的是进程被杀，最后一行只写了一半）；
- 但遇到不认识的"历史模式"直接报错，不猜；
- 空文件是错误；
- 线程 id 以文件里**第一条** SessionMeta 为准，因为 fork 出来的文件会把父会话的 SessionMeta 也复制进来。

**2.2 "接口不再支持"和"磁盘上还要能读"是两件事**
Codex app-server 已经从 API 里删掉了 `thread/rollback`，但老会话文件里的 `ThreadRolledBack` 事件仍然会在重放时生效。一个功能下线，接口可以删，历史数据的解释逻辑不能删。

**2.3 协议枚举要预期会长新成员**
Codex 协议文档（`protocol_v1.md`）明确 `Op` / `EventMsg` 是 non_exhaustive，客户端必须能忽略不认识的事件。改名时两边都收：线上发 `task_started` / `task_complete`，反序列化同时接受新旧名字。

**2.4 迁移的几种做法**
- opencode 早期是 JSON 文件存储，用一个 `migration` 标记文件记录跑到第几个迁移；解码时对多出来的字段选择"保留"（`onExcessProperty: "preserve"`），老版本程序读到新字段不会丢。
- 改成 SQLite 后是普通的 SQL 迁移目录（例如 `ALTER TABLE session ADD metadata text`）。
- opencode sync 模块：事件带 `version` 和聚合 id；`session.updated` 从"整对象"改成"只发变化的字段"之后，给老客户端的总线上再转换回整对象。新旧格式并存一段时间是常态。

### 3. 分叉、回退、编辑历史

**3.1 接口长什么样（Codex app-server）**
- `thread/fork`：`last_turn_id`（包含这一轮，且这一轮不能正在运行）或 `before_turn_id`；非临时的 fork 会尽力复制附件。
- `thread/revert`：`before_turn_id`，返回分页游标。
- 都是"以轮为单位"，不是以消息为单位。

**3.2 回退不等于撤销副作用**
- opencode 的 revert 要求会话空闲；先打一个"回退点"标记，并从快照恢复文件，可以 unrevert；真正删消息是在**下一次发消息**时才做（`cleanup()`）。这样用户反悔还来得及。
- Claude Code 的 checkpoint 文档列了它**不能**回退的东西：bash 命令造成的改动、子 agent 的编辑、外部改动；运行中插进去的消息没有单独的检查点，回退只能回到整轮开头；它不替代 git。
- 结论：消息可以回退，文件可以靠快照回退，但发出去的邮件、调用过的外部 API、数据库写入回不去。分叉和回退界面上要把这个讲清楚。

**3.3 分叉对缓存的影响**
分叉后两个分支共享前缀，前缀缓存仍然能命中；但"编辑中间某条消息再重新生成"会让那条之后的缓存全部失效。Goose 有一个专门测试（`prefix_invariance.rs`）保证连续两次请求里会影响缓存的前缀不变——把"缓存前缀不被意外改动"当作回归测试来守。

### 4. 存储选型

- **本地工具**：JSONL（只追加、坏一行不影响其他行）+ SQLite（元数据和搜索），Codex 就是这么做的。
- **服务端**：Postgres 一张会话表 + 一张消息/事件表，按会话 id 查；pydantic-ai 认为大多数聊天场景 jsonb 就够。LangGraph 的排障文档提醒两件事：检查点会无限增长，需要定期清理或设保留期；`PostgresSaver` 的 `thread_id` 列有长度限制，要控制在 255 字符以内。
- **按会话单实例**：Cloudflare Durable Object 每个实例自带存储（上限 10GB，2026-10-09 核对）、单线程，天然单写；WebSocket 可以"休眠"，休眠期间不按时长计费。Cloudflare Agents SDK 在此之上提供状态同步到客户端。
- **大东西存外部**：大工具输出、附件、图片存对象存储，历史里只放引用。Temporal 场景下这是硬约束（见第 6 节）。
- **服务端存 vs 厂商存**：OpenAI Conversation 对象不受 30 天过期限制，`previous_response_id` 链式调用每次仍按全部历史输入计费。

### 5. 自己的任务执行架构

**5.1 请求-响应撑不住的时候**
agent 一轮可能跑几分钟到几小时。一旦"用户关掉页面任务还要继续"，就不能把执行绑在 HTTP 请求上，需要：任务表 + 队列 + worker。

**5.2 任务状态机**
最少要有：排队、运行、等待（审批/外部事件）、完成、失败、取消。opencode 的 `retry{attempt, message, next}` 也值得学：把"正在重试、第几次、下次什么时候"作为一个可见状态推给界面，而不是让用户看着转圈。Codex 的错误通知里有 `will_retry` 字段：为 true 时表示服务端会自己重试，这一轮不中断，界面不该显示成失败。

**5.3 worker 崩溃后的接管：可见性超时 / 租约**
队列"取走但没确认"的消息过一段时间会重新可见、被别人再取一次。这个时间设短了，长任务会被执行两次；设长了，worker 崩了要等很久才有人接。
- AWS SQS：可见性超时默认 30 秒，最长 12 小时；中途延长不会重置 12 小时上限（2026-10-09 核对）。
- Celery + Redis：可见性超时默认 1 小时；任务跑超过 1 小时，会被另一个 worker 再执行一遍，而且会一直循环下去（2026-10-09 核对）。
- Celery 默认"取到就确认"（ack early），worker 崩了任务就丢；`acks_late` 只建议用于幂等任务。
- Postgres 当队列：`SELECT … FOR UPDATE SKIP LOCKED` 让多个 worker 各取各的行。
- 要么心跳续租，要么任务本身幂等，最好两者都有。agent 的一轮里有模型调用（花钱）和工具副作用（不可逆），重复执行的代价比普通后台任务高得多。

**5.4 状态写库和发消息要原子**
"更新任务状态 + 往队列/前端发事件"如果分两步做，中间崩了就不一致。标准做法是 transactional outbox：在同一个数据库事务里写业务表和 outbox 表，再由单独进程把 outbox 发出去。opencode sync 模块是另一种：先发事件，再由投影器应用到状态，单写者 + 整数序号保证全序。

### 6. 持久化执行

**6.1 是什么**
Temporal、DBOS、Restate、Inngest、LangGraph checkpointer 做的都是一件事：把每一步的结果记下来，进程崩了从上次记到的地方接着跑，已经做过的步骤不重做（直接拿记录的结果）。pydantic-ai 的说法很到位："持久化不是存储"——它保证**一次运行**能跨崩溃活下来，不负责存聊天记录；只是想存聊天记录就上持久化引擎，是常见的误用。

**6.2 共同的约束：重放时会重新执行你的代码**
- **Temporal**：工作流代码必须确定性，模型调用、工具调用放进 Activity；改了工作流代码导致重放路径不同，会报 non-deterministic 错误。
- **Inngest**：函数按"记忆化重放"执行，每次推进都从头跑函数，`step` 里的结果直接取记录；**step 外面的代码每次都会重跑**。
- **DBOS**：把检查点写进 Postgres。pydantic-ai 的 DBOS 集成里：流式事件是攒着等这一步结束才交付的；`ctx.emit` 在重放时不会重新发；模型实例不能跨 step 边界传。
- **LangGraph**：`interrupt()` 恢复时**从节点开头重新执行**，interrupt 之前的代码会再跑一遍；一个节点里多个 interrupt 按出现顺序（索引）对应恢复值，所以不能调整顺序、不能放进 try/except；在 `while True` 里循环校验用户输入，每次恢复都会把之前所有轮重放一遍。并行的多个 interrupt 用 "id → 值" 的映射一次性恢复。
- LangGraph 的检查点写入时机有三档：`durability = "sync" | "async" | "exit"`，默认 `"async"`（`types.py`）。`exit` 只在退出时写，最快但中途崩了丢进度；`sync` 每步写完才继续，最稳但最慢。

**6.3 Temporal 跑 agent 的硬限制（2026-10-09 核对）**
- 单个 payload 2MB，单次事务和 gRPC 消息 4MB；
- 事件历史 51,200 条或 50MB 强制终止，10,240 条或 10MB 开始警告；单个工作流 Signal 上限 10,000、Update 上限 2,000，同时进行中的 Update 最多 10 个，未完成的 Activity 最多 2,000 个；
- 历史默认保留 30 天（可设 1–90 天）。
- pydantic-ai 的 Temporal 集成说得更具体：消息历史会作为参数进入**每一次**模型 Activity，聊天越长 payload 越大；二进制内容 base64 之后实际只能放约 1.5MB；工作流任务的 payload 超限会**无限重试**而不是直接失败；大于 256 KiB 的 payload 可以走外部存储。
- 长会话的标准解法：Continue-As-New（带着精简后的状态开一条新的工作流历史）。Python SDK 用 `workflow.info().is_continue_as_new_suggested()` 判断时机，不要在 signal/update 处理函数里调用。

**6.4 其他容易漏的点（来自 pydantic-ai Temporal 文档）**
- agent 名字、toolset id 要稳定，改了老的运行无法恢复；
- 传给 Activity 的数据模型就是持久化契约，改字段等于改存储格式；
- Activity 里对 usage 的修改带不回工作流；
- MCP 连接每个 Activity 重连一次；
- Temporal 的 `maximum_attempts` 默认 0 表示不限次，模型 SDK 自己的重试要关掉（`max_retries=0`），否则两层重试叠加；
- 模型 Activity 默认 30 秒心跳超时；
- 用 Workflow Streams 推流式输出：大约多 100ms 延迟，支持按 offset 续读，Activity 重试会导致事件重复，每个运行只能有一个消费者。

### 7. 定时和事件触发的 agent

**7.1 定时任务**
- **错过怎么办**：Temporal Schedule 的补跑窗口（Catchup Window）默认 **一年**（最小 10 秒）——停机一周恢复后会把这一周错过的全补跑。Kubernetes CronJob 错过超过 100 次就不再启动并报错；`startingDeadlineSeconds` 小于 10 秒可能永远调度不上（2026-10-09 核对）。
- **重叠怎么办**：Temporal 重叠策略默认 Skip，另有 BufferOne、BufferAll、CancelOther、TerminateOther、AllowAll；Kubernetes `concurrencyPolicy` 默认 **Allow**（允许并发），另有 Forbid、Replace。agent 任务一次可能跑很久，默认 Allow 很容易叠出多个实例。
- **可能执行两次或零次**：Kubernetes 文档明说某些情况下一个时间点可能建出两个 Job 或者一个都没有，所以任务必须幂等。v1.32 起 Job 上有 `batch.kubernetes.io/cronjob-scheduled-timestamp` 注解记录原定时间，可以用来做去重键。
- **时区**：Kubernetes 用 `timeZone` 字段，不接受在表达式里写 `CRON_TZ`。
- Temporal Schedule 还有"失败后暂停"和 Backfill（手动补跑一段时间）；Temporal Cloud 对 schedule 的频率有限制，并建议加抖动（定时加抖动见 [02](02-reliability.md)）。

**7.2 Webhook 触发**
共同点：对方等你回应的时间很短，超时就重发，所以**先快速确认，再异步干活，并按事件 id 去重**。
- Slack Events API：3 秒内必须响应；失败最多重试 3 次（几乎立即、1 分钟后、5 分钟后），请求头带 `x-slack-retry-num` 和 `x-slack-retry-reason`（如 `http_timeout`），用 `event_id` 去重（2026-10-09 核对）。
- GitHub：10 秒内响应，建议放队列异步处理；错过的投递不会自动重发，要自己调接口重投；用 `X-GitHub-Delivery` 去重（2026-10-09 核对）。
- Stripe：可能重复投递，按事件 id 去重；不保证顺序，也不要按 `created` 排序推断顺序；live 模式最长重试三天（2026-10-09 核对）。
- agent 场景的放大效应：如果 webhook 处理函数里直接跑 agent，超过 3 秒 Slack 就重发，于是同一条消息跑出三个 agent、回三遍。

### 8. 等人：审批可能隔几天才回来

- **挂起期间不要占资源**：Inngest `step.waitForEvent` 必须给超时，超时返回 null；用 `match` / `if` 条件匹配是哪个事件。Temporal 用 Signal/Update 等待。Cloudflare DO 的 WebSocket 休眠也是同一思路。
- **AG-UI 的中断契约**写得最全，可直接当设计清单：
  - 恢复时要覆盖**所有**未处理的中断；
  - 有未处理中断时，阻止用户发新输入；
  - 恢复操作要幂等（同一个回复提交两次不出事）；
  - 中断可以带 `expiresAt`；
  - 运行结束前先发状态快照；
  - "批准但修改参数"时，`editedArgs` 是**整体替换**原参数，不是合并；
  - 工具结果在下一次运行里按原来的 `toolCallId` 回填。
- **恢复时环境可能已经变了**：文件被别人改了、token 过期了、价格变了。恢复后要重新校验前提，而不是直接执行几天前批准的动作。LangGraph 文档的要求是：interrupt 之前的副作用必须幂等，因为恢复会重跑。
- **批准本身可以伪造**：如果"历史"和"批准结果"都是客户端提交上来的，服务端无法区分是真人批准还是伪造的（见第 10 节）。

### 9. agent → 界面的事件协议

**9.1 不只是文字增量**
一个能用的协议至少要表达：
- 一轮的开始、结束、中止、出错；
- 文字增量、推理增量；
- 工具调用：参数在流、参数完成、开始执行、输出增量、结束；
- 审批请求和审批结果；
- 计划更新、diff 更新、用量更新；
- 模型被切换、上下文被压缩；
- 某个步骤重试，前面的输出要作废。

**9.2 三个现成的参考**
- **Vercel AI SDK UI message stream**：响应头 `x-vercel-ai-ui-message-stream: v1`；事件类型有 `start`、`text-*`、`reasoning-*`、`tool-input-*`、`tool-approval-request/response`、`tool-output-*`、`data-*`（自定义数据）、`start-step`、`finish-step`、`reset-step`、`finish`、`abort`、`error`，最后以 `data: [DONE]` 结束。其中 `reset-step`：某一步重试时，作废上一个 `start-step` 以来的所有内容，再发新的。没有这个事件，重试会让界面上出现两遍半截回答。
- **Codex app-server**（JSON-RPC）：
  - 通知有 `thread/status/changed`、`turn/started`、`turn/completed`、`item/started`、`item/completed`、`item/agentMessage/delta`、`item/commandExecution/outputDelta`、`turn/plan/updated`、`turn/diff/updated`、`thread/tokenUsage/updated`、`model/rerouted`、`thread/compacted` 等；
  - item 的开始和完成事件带毫秒时间戳；增量事件带 `thread_id`、`turn_id`、`item_id`，每个片段都能对上号；
  - **审批是服务端发给客户端的请求**（`item/commandExecution/requestApproval`、`item/fileChange/requestApproval`），等客户端回复；另有 `serverRequest/resolved` 通知，告诉所有连接"这个请求已经处理了"——多个客户端同时连着时，一个人批准后其他界面要把审批框收起来。
- **AG-UI**：
  - 事件按 Start-Content-End 三段式；
  - `StateSnapshot` 是整体替换（不是合并），`StateDelta` 用 RFC 6902 JSON Patch，前端发现对不上就请求快照；
  - `MessagesSnapshot` 对 activity / reasoning 这类消息是"全有或全无"；
  - 文档要求实现方能容忍乱序到达。

**9.3 快照 + 增量是通用套路**
第一次连上或怀疑不一致时给快照，平时给增量，增量带序号。这一点在 AG-UI、OpenHands、opencode sync 里都一样。

### 10. 客户端带历史时的信任边界

很多前端框架默认"客户端把整段历史发上来"。pydantic-ai 把其中的风险写得最清楚：
- 能访问这个接口，就等于有权限以这个 agent 的身份跑，接口访问控制就是授权边界；
- 用 cookie 鉴权就有 CSRF 风险，所以只接受 `application/json`，其他类型返回 415；
- 默认剥掉客户端提交的 system prompt 和悬空的 tool call；
- `s3://`、`gs://` 这类文件 URL 默认丢弃，因为厂商会用**你服务端的 IAM 身份**去取这个对象；
- 客户端提交的审批结果、外部工具结果都可以伪造，服务端会当真并执行；
- 没有哪个框架会给 tool call 签名——签名只对"自己保留了运行记录"的服务端有意义，而这种服务端本来就不需要客户端那份历史。

结论：要么服务端存历史、客户端只发最后一条（AI SDK 文档的"只发最后一条消息"就是这个），要么接受历史可被篡改并按不可信输入处理。

### 11. 断线续流、刷新页面、多端

（协议层的续传见 [02](02-reliability.md) 第 5 节，这里讲应用层怎么搭。）

**11.1 断开连接 ≠ 取消**
- AI SDK 默认对模型流有背压：**客户端断开时，模型那边的流也会被中止**，会话可能停在坏掉的状态。要用 `consumeStream()` 去掉背压，让服务端把结果跑完存下来。
- 续流方案：会话上存 `activeStreamId`；`GET /api/chat/[id]/stream` 没有活动流时返回 204，有就续上；底层是 Redis + `resumable-stream`。
- `resumable-stream` 的设计：第一个请求是生产者，**生产者无论读者在不在都会把流跑完**；后来的读者通过 Redis pub/sub 接上；常见情况下每个流只多一次 INCR 和一次 SUBSCRIBE；流已经结束时续接返回 422；专为没有粘性负载均衡的 serverless 设计。

**11.2 停止要走独立接口**
AI SDK 的排障文档《abort 破坏续流》：开了续流后，用 abort 断开连接已经停不了生成。需要一个单独的 stop 接口，按顺序：
1. 读出当前活动流 id；
2. 把已生成的部分消息存下来；
3. 取消生产者；
4. 只有当会话上的活动流 id **仍然是这一个**时才清空（防止把用户刚发起的新一轮清掉）。

并且不要在页面卸载、组件卸载时调用 stop，否则刷新页面就把生成停了。

**11.3 先拉快照，再接增量，按 id 去重**
OpenHands 的前端：
- 先用 REST 拉历史，再开 WebSocket，并带 `resend_mode='since'` + `after_timestamp` 只要之后的事件，不支持时退回 `all`；
- 按事件 id 去重，重放来的事件**跳过有副作用的处理**（比如不要再弹一次通知、不要再触发一次跳转）；
- 后台刷新数据时不要拆掉正在用的 socket。他们踩过：后台 refetch 触发重连，结果界面卡在 "Connecting" 好几分钟。

opencode 的事件接口做法：先注册监听，再发 `server.connected`，保证这中间不丢事件；10 秒一次心跳；`Cache-Control: no-cache, no-transform` 和 `X-Accel-Buffering: no`。但它**断线重连不补发**，靠重新拉状态。本地工具这样够了，跨网络的服务端不够。

**11.4 手机和后台标签页**
OpenHands `use-page-visibility-reconnect.ts`：
- 页面隐藏 3 秒后主动干净断开（`HIDE_DEBOUNCE_MS = 3_000`），页面被冻结（freeze）时立即断开；
- 回到前台立刻重连，**跳过退避计时器**。原因是退避计时器在后台可能已经累积到几个小时，用户回来时还在等。

微软的 `fetch-event-source` 也是隐藏时关连接、回来带最后事件 id 重连。它存在的原因：浏览器原生 `EventSource` 只能 GET、不能带请求头和请求体、不能控制重试。

**11.5 多标签页**
HTTP/1.1 下浏览器对同一域名最多 6 个连接，**所有标签页共用**，MDN 标为"不修"（2026-10-09 核对）。用户开 7 个会话标签页，第 7 个就卡住。解法是 HTTP/2，或一个标签页持有连接、通过 BroadcastChannel / SharedWorker 分发给其他标签页。

### 12. 运行中用户插话：接口怎么设计

主循环里插入、排队、打断、回滚各自是什么意思，插入的话什么时候进历史，见 [03](03-agent-loop-context.md) 第 11、12 节。这里只讲接口和界面。

Codex app-server 把三种做成了独立接口，可以照着设计：
- `turn/steer` 必须带 `expected_turn_id`，和当前活动轮对不上就失败——防止用户以为在给第 3 轮补充，结果第 3 轮刚结束，话被塞进了第 4 轮。还带 `client_user_message_id` 做去重和对账。审查（review）、压缩（compact）类型的轮不接受插入，返回 `ActiveTurnNotSteerable`。
- 队列是独立模块（`ext/queue`），注释原话是"持久化、与存储无关的用户消息队列，空闲时派发"，底层 SQLite，`start()` 只在会话空闲时执行。队列可以增删改、重排。
- `turn/interrupt` 带 `thread_id` 和 `turn_id`。
- 旧版协议的行为是"新输入直接中止当前任务"，现在改成了三种分开。

界面上要注意的一点：Claude Code 文档写明，运行中插进去的消息没有自己的检查点，回退只能回到整轮开头。插话越方便，回退粒度越粗。

### 13. "做完了"在接口上怎么体现

完成工具、外部验证、独立评审这几种判定方法见 [03](03-agent-loop-context.md) 第 13 节。接口层面要补两点：
- **停止钩子要有次数上限**：Goose 允许 stop hook 拦住"这一轮要结束"（比如测试没跑过就不让停），但有上限 `GOOSE_STOP_HOOK_BLOCK_CAP`，超过后强制放行，注释写的是"避免无限循环"。
- **队列里的待处理输入要算进去**：Codex 在模型已经说完、但队列里还有插入的话时，会让这一轮继续。对外报告"完成"之前要先看队列。

### 14. 终端 agent 特有的问题

Codex TUI 的几个处理，做 CLI 时可以直接参考：
- **粘贴**：有些终端（尤其 Windows）不支持 bracketed paste，粘贴会变成一串快速按键，回车会被当成"发送"。Codex 用时间间隔识别"粘贴爆发"（`paste_burst.rs`），爆发期间回车当换行，并抑制 `?` 之类快捷键被误触发。
- **大段粘贴**：超过 1000 字符（`LARGE_PASTE_CHAR_THRESHOLD`）显示成 `[Pasted Content N chars]` 占位，不把输入框撑爆。
- **Ctrl-C 分层**：先给当前弹窗（关闭弹窗），再给历史搜索（取消搜索），再由主界面决定是中断当前轮还是作为"双击退出"的第一下；双击窗口 1 秒，第二下必须是同一个键。

### 15. 日常测试替身

- **脚本化的假模型**：pydantic-ai 的 `TestModel`（按工具 schema 生成合法参数，把所有工具调一遍）和 `FunctionModel`（自己写返回逻辑），配合 `Agent.override` 替换；全局设 `ALLOW_MODEL_REQUESTS=False`，测试里误调真模型直接报错。`TestModel` 模拟不了厂商侧的内置工具，测试时要一起关掉。AI SDK 有 `MockLanguageModelV4` 和 `simulateReadableStream`（带延迟的假流）。
- **假的 SSE 服务端**：Codex 测试里用 `sse()` 和一组 `ev_*` 构造器拼出 Responses API 的事件流；`streaming_sse.rs` 可以逐块放行，用来测"流到一半用户打断/断线"这种时序问题。
- **上下文快照**：Codex 的 `context_snapshot.rs` 把每次真正发给模型的输入存成快照，易变的文本（时间、路径）先规范化。提示词或历史拼装逻辑一改，快照 diff 一眼可见。
- **前缀不变测试**：Goose `prefix_invariance.rs`，见第 3 节。
- **HTTP 录制回放**：opencode 的 `http-recorder`：
  - 录一次、回放 JSON 磁带；`CI=true` 时缺磁带直接失败；
  - 没有"覆盖录制"模式，要刷新就删掉磁带重录，这样变化会出现在代码评审里；
  - 请求严格按顺序匹配，能覆盖重试和轮询；
  - 默认脱敏，写入前扫描整个磁带找凭证，不安全就拒绝写；
  - 局限：响应是整体缓冲的，测不了流式时序、取消和背压；磁带格式 v1 没有迁移工具。

---

## 二、文章很少讲但常碰到的事

1. **用户刷新页面，生成就停了。** 原因是把"连接断开"当成了"取消"。AI SDK 默认背压在客户端断开时会中止模型调用；在组件卸载时调 stop 也一样。要用 `consumeStream()` 让服务端跑完，停止走独立接口。
2. **停止接口把用户刚开的新一轮清掉了。** 清"活动流 id"时没检查它是不是还指向要停的那个流。
3. **重试的那一步在界面上出现两遍。** 协议里没有"作废这一步"的事件（AI SDK 的 `reset-step`）。
4. **进程被杀后会话打不开。** JSONL 最后一行只写了一半，读取时整个文件解析失败。应该跳过坏行并记数。
5. **会话恢复后模型报错：tool_use 没有对应的 tool_result。** 工具执行到一半进程挂了。投影时给 pending/running 的工具补一个"执行被中断"的结果（opencode 做法；修补原则见 [03](03-agent-loop-context.md) 第二节第 1 条）。
6. **换模型后旧会话报签名错误。** 厂商的推理签名、私有元数据只能回放给同一个模型，换模型要降级成普通文本。
7. **功能下线后老会话打不开或内容不对。** 接口删了，老数据里对应事件的解释逻辑也被删了。
8. **同一个会话被两个进程同时写坏。** 两个标签页、两台设备、一个 CLI 一个 IDE 插件同时操作。需要单写锁，或者按会话路由到唯一执行者。
9. **长任务被执行了两遍。** Celery + Redis 默认可见性超时 1 小时，任务超过 1 小时就会被另一个 worker 重跑，而且反复循环；SQS 默认只有 30 秒。
10. **Slack 机器人一条消息回三遍。** 3 秒内没确认，Slack 重发；处理函数里同步跑 agent 必然超时。先确认再异步跑，按 `event_id` 去重。
11. **停机一周恢复后定时 agent 疯狂补跑。** Temporal Schedule 的补跑窗口默认一年。Kubernetes CronJob 则相反：错过超过 100 次干脆不跑。
12. **定时 agent 叠了好几个实例。** Kubernetes CronJob 默认允许并发。
13. **LangGraph 审批恢复后重复发了邮件。** interrupt 恢复会从节点开头重跑，interrupt 之前的副作用又执行了一次。
14. **Temporal 跑长对话突然卡住不停重试。** 每次模型调用都把完整历史当参数传，超过 2MB 后工作流任务无限重试。历史条数到 51,200 也会被强制终止。
15. **前端伪造了一次"用户批准"。** 客户端提交的历史和审批结果服务端无法验证，框架也不签名。
16. **手机切回来后半天连不上。** 后台期间退避计时器涨到很长，回前台还在等。回前台时应跳过退避立即重连。
17. **开第 7 个标签页卡住。** HTTP/1.1 下同域名 6 个连接所有标签页共用。
18. **重连后通知又弹了一遍。** 补发的历史事件被当成新事件处理了副作用。按 id 去重，重放事件跳过副作用。
19. **用户补充的话进了下一轮。** 插话时没带"当前是哪一轮"的前提条件（Codex 的 `expected_turn_id`）。
20. **回退后以为一切都撤销了。** 消息和文件快照可以回退，bash 造成的改动、外部 API 调用回不去。
21. **"不让结束"的检查导致死循环。** stop hook / 验证步骤没有次数上限。
22. **服务重启后界面一直显示"运行中"。** 运行状态只在内存里，或者库里有"运行中"但没有租约过期判断。
23. **录制回放测试全绿，线上流式取消却出问题。** 录制回放把响应整体缓冲，测不了流式时序。要另外用可逐块放行的假 SSE 服务端测。

---

## 三、要拿的主意

### 决定 1：会话存成消息表还是事件流
- **问题**：每轮追加消息就够，还是要把每个变化都记成事件？
- **选项与代价**：
  - 消息表（jsonb 一列或一行一条消息）：最简单，读出来就能发给模型。界面要展示工具进度、审批、压缩这类过程信息时不够用，重连补发也没有序号可依。
  - 事件流（JSONL 或事件表 + 序号）：重连、多端、审计、调试都基于同一份数据。要写投影，还要长期维护事件格式的兼容。
  - 两者都存：事件流做真相，另存一份"给模型的消息"作为缓存，可以从事件重建。
- **怎么选**：只有聊天、没有长任务和多端，用消息表。有后台任务、审批、多个客户端同时看同一个会话，用事件流。持久化引擎（Temporal 等）只解决"一次运行不丢"，不替代这个选择。

### 决定 2：给模型的历史怎么从存储里生成
- **问题**：存什么就发什么，还是请求前做一次投影？
- **选项与代价**：直接发，代码少，但出错消息、中断的工具调用、跨模型的签名、被压缩的旧输出都会原样进请求，导致报错或浪费 token。投影一次，要多维护一层转换逻辑，并给它写快照测试。
- **怎么选**：只要支持中断、换模型、压缩中的任何一个，就要做投影。投影规则可以直接对照 opencode `message-v2.ts` 那几条。

### 决定 3：谁来保证"一个会话同一时刻只有一个写者"
- **选项与代价**：
  - 本地锁文件（Codex）：简单，只管得住一台机器，崩溃后要清理过期锁。
  - 进程内 Runner + 忙碌报错（opencode）：只适合单进程。
  - 数据库版本号 / 行锁：通用，冲突时要有重试或报错的交互。
  - 按会话 id 路由到唯一执行者（Durable Object、Restate Virtual Object、Temporal 一个会话一个工作流）：天然单写，但绑定了特定平台。
- **怎么选**：本地 CLI 用锁文件。服务端已经在用这类平台就按会话路由，否则用数据库版本号。不管哪种，第二个写者都要拿到明确的错误，不能静默覆盖。

### 决定 4：运行中用户插话，默认是插入、排队还是打断
- 各方式在主循环里的代价见 [03](03-agent-loop-context.md) 决定 8。
- **怎么选（接口层）**：三个都做成独立操作，界面上让用户选（比如回车排队、某个快捷键插入、停止按钮打断）。插入一定要带"目标轮 id"前提条件。排队的消息要落盘，进程重启后不能丢。

### 决定 5：长任务用自建队列 + worker，还是持久化执行引擎
- **选项与代价**：
  - 自建（Postgres `SKIP LOCKED` / SQS / Celery）：依赖少，团队熟悉。重复执行、租约、心跳、步骤级恢复都得自己做；可见性超时的默认值很容易让长任务跑两遍。
  - 持久化引擎（Temporal / DBOS / Restate / Inngest）：步骤级恢复和重试现成。代价是确定性约束和重放语义，以及 payload 和历史长度的硬限制（Temporal 2MB / 51,200 条）；长对话要 Continue-As-New 或把历史放外部存储；还要多运维一套系统（DBOS 只依赖 Postgres，这方面最轻）。
  - LangGraph checkpointer：已经在用 LangGraph 时成本最低。要接受"节点从头重跑"，并自己定期清理检查点。
- **怎么选**：任务几分钟、步骤少、副作用都幂等，自建就够，但要把可见性超时设得大于最长任务时间并加心跳续租。任务以小时或天计、中间要等人、步骤多且贵，就上持久化引擎，并提前设计好"历史放外部、工作流里只传引用"。

### 决定 6：恢复时会重跑的代码里，副作用怎么办
- **问题**：LangGraph 节点从头重跑、Inngest step 外代码重跑、队列重复投递，这些都会让同一个副作用执行两次。
- **选项与代价**：每个副作用放进单独的 step/activity，代码会碎一些。给外部调用带幂等键（[02](02-reliability.md) 决定 9），需要对方支持。先查后做，有竞态。
- **怎么选**：发邮件、付款、写外部系统这类不可逆的动作，一律单独一步 + 幂等键。interrupt 之前不放副作用。

### 决定 7：等人审批时，挂起状态放哪、多久算过期
- **选项与代价**：放在持久化引擎里等 signal/event：状态天然保存，但要遵守引擎的保留期，Temporal 默认保留 30 天。放进自己的库，把运行结束掉，回来时再开一次新运行：不占引擎资源，但恢复逻辑要自己写，并且要重新校验环境。
- **怎么选**：几分钟到几小时的审批，在引擎里等，并设超时（Inngest 强制要求设）。可能几天才回来的，存库 + 新运行，恢复前重新检查前提，过期就要求重新审批。两种都要带 `expiresAt`，并在有未处理审批时阻止新输入。

### 决定 8：前端怎么接收事件：SSE、WebSocket 还是轮询
- **选项与代价**：
  - SSE：简单，能穿过大多数代理。原生 `EventSource` 只能 GET、不能带头，所以通常要用 fetch 自己实现；HTTP/1.1 下有 6 连接上限。
  - WebSocket：双向，插话、审批回复可以走同一条连接。要自己做心跳、重连、补发；服务端要么保持连接，要么用 Cloudflare 这类可休眠的方案。
  - 轮询：最稳，但延迟高、浪费请求。
- **怎么选**：单向流式输出、无状态部署选 SSE + resumable stream（Redis）。多端同时操作同一个会话、需要服务端主动发审批请求，选 WebSocket（Codex app-server、OpenHands 都是）。不管选哪种，都按"REST 拉快照 → 增量带序号 → 按 id 去重"的套路搭。

### 决定 9：历史存在服务端还是由客户端带上来
- **选项与代价**：客户端带：服务端无状态，好扩展，但历史、tool call、审批都能被伪造，还要处理 CSRF 和文件 URL 借用服务端身份的问题。服务端存、客户端只发最后一条：要管存储和权限，但信任边界清楚。
- **怎么选**：只要有带副作用的工具或审批，就服务端存。确实需要客户端带历史时（比如纯前端 demo），按 pydantic-ai 的默认做：剥 system prompt、剥悬空 tool call、只允许 http(s) 文件 URL、只收 JSON。

### 决定 10：怎么判断任务完成
- 判定方法的取舍见 [03](03-agent-loop-context.md) 决定 6。
- **怎么选（接口层）**：stop hook 一律设次数上限；对外发"完成"事件前先检查队列里有没有待处理输入。

### 决定 11：定时和 webhook 触发的去重键用什么
- **选项与代价**：用厂商给的事件 id（Slack `event_id`、GitHub `X-GitHub-Delivery`、Stripe event id），最准，但只防得住对方重发。用"任务名 + 原定执行时间"（Kubernetes 的 `cronjob-scheduled-timestamp` 注解），防得住调度器重复建任务。用业务键（比如"这个 PR 的这个 commit"），防得住不同来源触发同一件事。
- **怎么选**：至少用事件 id。agent 任务花钱，建议再加业务键去重。去重记录的保留时间要长于对方的最长重试期，Stripe 是三天。

### 决定 12：分叉 / 回退做到什么粒度
- **选项与代价**：按轮，实现简单，和缓存、检查点对齐（Codex 的 fork/revert 都按轮）。按消息，更灵活，但"编辑中间消息"会让后面的缓存全部失效，副作用也更难说清楚。连文件一起回退，体验好，但要做快照，而且 bash 和外部改动依然回不去。
- **怎么选**：默认按轮。文件快照只承诺"agent 自己改的文件"。界面上明确提示外部副作用不会撤销。真删消息延后到下一次发送（opencode 做法），给用户留反悔的余地。

### 决定 13：测试替身选哪种
- **选项与代价**：假模型（TestModel / Mock）：快、确定，测不到厂商协议细节。假 SSE 服务端：能测流式时序和中途打断，要维护事件构造器。录制回放：贴近真实，测不了流式时序，磁带要脱敏、要随厂商变化重录。上下文快照：专门防"发给模型的内容被意外改了"。
- **怎么选**：业务逻辑用假模型，并全局禁止真实请求。协议适配层用录制回放，CI 里缺磁带直接失败。中断、续流、背压用可逐块放行的假 SSE。提示词和历史拼装用上下文快照，再加一条前缀不变测试守住缓存。

---

## 四、资料清单

核对日期均为 2026-10-09（Asia/Shanghai）。代码链接固定在当天拉取的提交上。

**会话存储、迁移、分叉**
- [Codex thread-store README](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/thread-store/README.md)：源码文档；1、4；历史只追加、元数据单独更新，JSONL + SQLite 的分工说得很清楚。
- [Codex rollout/policy.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/rollout/src/policy.rs)：源码；1；哪些事件落盘、工具输出落盘截到 64KB、记忆另有一套过滤，是"存储视图 ≠ 模型视图"的实例。
- [Codex rollout/writer_lock.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/rollout/src/writer_lock.rs)：源码；1.4 单写者；单会话写锁和过期锁清理。
- [Codex rollout/recorder.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/rollout/src/recorder.rs)：源码；2；读老文件"坏行跳过、未知模式拒绝"、fork 后以第一条 SessionMeta 为准。
- [Codex app-server README](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/app-server/README.md)：源码文档；2、3、9；rollback 接口删除但磁盘事件仍重放，fork 的附件复制，全套线程/轮接口说明。
- [Codex protocol_v1.md](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/docs/protocol_v1.md)：源码文档；2、12；提交队列/事件队列模型、一个会话最多一个任务、non_exhaustive 枚举和事件改名兼容。
- [Codex v2/thread.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/app-server-protocol/src/protocol/v2/thread.rs)：源码；3；fork（`last_turn_id` / `before_turn_id`）和 revert 的参数定义。
- [opencode session/message-v2.ts](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/session/message-v2.ts)：源码；1；存储到模型消息的投影规则最完整的一份（跳过出错消息、跨模型降级、中断工具补结果、图片挪位）。
- [opencode session/revert.ts](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/session/revert.ts)：源码；3；回退要求空闲、文件快照、可 unrevert、延迟删除。
- [opencode storage/storage.ts](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/storage/storage.ts)：源码；2；JSON 文件存储的迁移标记和"保留多余字段"的解码策略。
- [opencode sync/README.md](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/sync/README.md)：源码文档；1、2、5；单写者事件溯源、整数序号全序、事件版本化、给老客户端做格式转换。
- [opencode session/status.ts](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/session/status.ts)：源码；5、11；idle/busy/retry 三态，retry 带次数和下次时间，也是"状态只在内存"的反例。
- [Goose conversation/message.rs](https://github.com/aaif-goose/goose/blob/0f4768025f517f5812f6d962a90aa52d509863cf/crates/goose-provider-types/src/conversation/message.rs)：源码；1；消息级的"用户可见 / 模型可见"双开关。
- [Claude Code checkpointing](https://code.claude.com/docs/en/checkpointing)：官方文档；3、12；明确列出回退做不到的事（bash、子 agent、外部改动、插话无检查点）。
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：官方文档；4；checkpointer 和 store 的分工，检查点无限增长、thread_id 长度这两个排障点。
- [Martin Fowler: Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)：经典文章；1；重放时外部系统调用怎么处理（External Updates 一节），正好对应 agent 工具副作用。
- [Cloudflare: What are Durable Objects](https://developers.cloudflare.com/durable-objects/concepts/what-are-durable-objects/)：官方文档；1、4；单线程、全局唯一名字、自带存储，"按会话单实例"的现成形态。
- [Cloudflare Agents: Store and sync state](https://developers.cloudflare.com/agents/runtime/lifecycle/state/)：官方文档；4、11；agent 状态存在实例里并同步到客户端。

**任务架构、持久化执行**
- [AWS SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)：官方文档；5；默认 30 秒、最长 12 小时、延长不重置上限。
- [Celery: Using Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html)：官方文档；5；可见性超时默认 1 小时，超时任务会被反复重跑。
- [Celery: Tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html)：官方文档；5；默认 ack early，`acks_late` 只适合幂等任务。
- [PostgreSQL SELECT（SKIP LOCKED）](https://www.postgresql.org/docs/current/sql-select.html)：官方文档；5；用 Postgres 当任务队列的关键语法。
- [Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)：模式说明；5；状态写库和发事件的原子性。
- [pydantic-ai: Persistence](https://pydantic.dev/docs/ai/core-concepts/persistence/)：官方文档；4、6；"存聊天用 jsonb 就够，上持久化引擎是常见误用"的判断框架。
- [pydantic-ai: Durable execution overview](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/)：官方文档；6；"持久化不是存储"，以及各引擎对比的入口。
- [pydantic-ai: Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/)：官方文档；6；agent 跑在 Temporal 上的所有坑（历史进每个 Activity、payload 超限无限重试、名字要稳定、关 SDK 重试、Workflow Streams 重复事件），目前最具体的一份。
- [pydantic-ai: DBOS](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/)：官方文档；6；流式事件在持久化 step 里被缓冲、重放时不重发。
- [Temporal Cloud limits](https://docs.temporal.io/evaluate/cloud/limits)：官方文档；6；payload、历史条数和大小、Update/Activity 并发、保留期的具体数字。
- [Temporal: Events and Event History](https://docs.temporal.io/workflow-execution/event)：官方文档；6；10,240 警告 / 51,200 终止、Signal/Update 上限、Continue-As-New 的动机。
- [Temporal: Workflow Definition](https://docs.temporal.io/workflow-definition)：官方文档；6；确定性约束和 non-deterministic 错误。
- [Temporal Python: Continue-As-New](https://docs.temporal.io/develop/python/workflows/continue-as-new)：官方文档；6；`is_continue_as_new_suggested()` 和不要在 handler 里调用。
- [Inngest: How functions are executed](https://www.inngest.com/docs/durable-execution/durable-workflows)：官方文档；6；记忆化重放，step 外代码每次重跑。
- [DBOS architecture](https://docs.dbos.dev/architecture)：官方文档；6；只依赖 Postgres 的检查点方案。
- [Restate: Services](https://docs.restate.dev/foundations/services)：官方文档；6、1；Virtual Object 按 key 单写。
- [LangGraph types.py](https://github.com/langchain-ai/langgraph/blob/bfcfea554ed5c7f7be562cebf8825e911b493ab1/libs/langgraph/langgraph/types.py)：源码；6；`Durability` 三档及默认 `async`，`interrupt()` 的恢复语义注释。

**定时、webhook、等人**
- [Temporal: Schedule](https://docs.temporal.io/schedule)：官方文档；7；重叠策略、补跑窗口默认一年、失败暂停、Backfill。
- [Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)：官方文档；7；默认允许并发、可能建两次或零次、超过 100 次错过不跑、原定时间注解。
- [Slack Events API](https://docs.slack.dev/apis/events-api/)：官方文档；7；3 秒确认、3 次重试的时间点、重试请求头。
- [GitHub: Best practices for using webhooks](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)：官方文档；7；10 秒响应、错过的不会自动重投。
- [Stripe: Webhooks](https://docs.stripe.com/webhooks)：官方文档；7；重复投递、不保证顺序、重试三天。
- [Inngest: step.waitForEvent](https://www.inngest.com/docs/reference/typescript/v4/functions/step-wait-for-event)：官方文档；8；等待外部事件必须设超时，超时返回 null。
- [AG-UI: Interrupts](https://docs.ag-ui.com/concepts/interrupts)：协议文档；8、9；中断与恢复的契约清单（全部恢复、阻塞新输入、幂等、过期、editedArgs 整体替换）。
- [LangGraph: Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)：官方文档；8、6；节点从头重跑、不能 try/except、不能重排、循环校验导致重放放大。

**事件协议、续流、多端**
- [AI SDK: Stream protocol](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol)：官方文档；9；UI 事件类型全表，`reset-step` 作废重试步骤。
- [AI SDK: Chatbot resume streams](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)：官方文档；11；`activeStreamId`、204、Redis 续流的完整搭法。
- [AI SDK: Abort breaks resumable streams](https://ai-sdk.dev/docs/troubleshooting/abort-breaks-resumable-streams)：排障文档；11；独立 stop 接口的四步，以及"不要在卸载时停止"。
- [AI SDK: Chatbot message persistence](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)：官方文档；11、1；背压导致断开即中止、`consumeStream()`、服务端生成 id、只发最后一条消息。
- [vercel/resumable-stream](https://github.com/vercel/resumable-stream)：开源库；11；生产者必跑完、pub/sub 接续、serverless 无粘性路由下的续流成本。
- [AG-UI: Events](https://docs.ag-ui.com/concepts/events)：协议文档；9；三段式事件、快照整体替换 + JSON Patch 增量、容忍乱序。
- [Codex v2/turn.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/app-server-protocol/src/protocol/v2/turn.rs)：源码；12、9；`expected_turn_id` 前提条件、`client_user_message_id`、interrupt 参数。
- [Codex v2/notification.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/app-server-protocol/src/protocol/v2/notification.rs)：源码；9；`will_retry` 错误通知、`serverRequest/resolved` 多端收起审批。
- [opencode 事件接口 event.ts](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/server/routes/instance/httpapi/handlers/event.ts)：源码；11；先注册监听再发 connected、10 秒心跳、防代理缓冲的响应头。
- [OpenHands use-page-visibility-reconnect.ts](https://github.com/OpenHands/OpenHands/blob/91fcf4372d7bd5a3bf46c76b4c89ebc155bc1176/src/hooks/use-page-visibility-reconnect.ts)：源码；11；隐藏 3 秒断开、冻结立即断开、回前台跳过退避。
- [OpenHands conversation-websocket-context.tsx](https://github.com/OpenHands/OpenHands/blob/91fcf4372d7bd5a3bf46c76b4c89ebc155bc1176/src/contexts/conversation-websocket-context.tsx)：源码；11；REST 快照 + WS since 补发、按 id 去重、重放跳过副作用、后台刷新不拆 socket 的教训。
- [MDN: EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)：官方文档；11；HTTP/1.1 下同域 6 连接所有标签页共用。
- [Azure/fetch-event-source](https://github.com/Azure/fetch-event-source)：开源库；11；原生 EventSource 的限制和页面隐藏时的处理。
- [Cloudflare: Durable Objects WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/)：官方文档；11、8；WebSocket 休眠、休眠不计时长费。

**信任边界**
- [pydantic-ai: UI overview](https://pydantic.dev/docs/ai/integrations/ui/overview/)：官方文档；10 信任边界；接口访问即授权、CSRF、文件 URL 借用 IAM 身份、审批可伪造。
- [pydantic-ai: Message history](https://pydantic.dev/docs/ai/core-concepts/message-history/)：官方文档；1、11；"客户端历史的信任边界"一节，说明为什么没有框架给 tool call 签名。

**运行中插话、完成判断**
- [Codex core/session/turn.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/core/src/session/turn.rs)：源码；12；插话只在下次模型请求前进历史、两种推迟情况、有待处理输入时一轮继续。
- [Codex ext/queue](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/ext/queue/src/lib.rs)：源码；12；持久化用户消息队列、空闲时派发。
- [opencode session/run-state.ts](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/opencode/src/session/run-state.ts)：源码；12；每会话一个 Runner、忙碌报错、级联取消子会话。
- [Goose ops_steer.rs](https://github.com/aaif-goose/goose/blob/0f4768025f517f5812f6d962a90aa52d509863cf/crates/goose/src/agents/state_machine/ops_steer.rs)：源码；12；排队指导只在两轮之间应用。
- [Goose final_output_tool.rs](https://github.com/aaif-goose/goose/blob/0f4768025f517f5812f6d962a90aa52d509863cf/crates/goose/src/agents/final_output_tool.rs)：源码；13；完成工具 + JSON schema 校验 + 错误回给模型。
- [Goose ops_stop_hook.rs](https://github.com/aaif-goose/goose/blob/0f4768025f517f5812f6d962a90aa52d509863cf/crates/goose/src/agents/state_machine/ops_stop_hook.rs)：源码；13；stop hook 拦截结束及次数上限。

**测试替身**
- [opencode http-recorder README](https://github.com/anomalyco/opencode/blob/388406238bd5ca15564a762840a2362c3a45bd9c/packages/http-recorder/README.md)：源码文档；15；录制回放的取舍写得最坦白（严格顺序、CI 缺磁带失败、写前扫凭证、测不了流式）。
- [Codex tests streaming_sse.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/core/tests/common/streaming_sse.rs)：源码；15；逐块放行的假 SSE 服务端，测中途打断。
- [Codex tests context_snapshot.rs](https://github.com/openai/codex/blob/22ebb0fb178fe369190123c256ba200585765725/codex-rs/core/tests/common/context_snapshot.rs)：源码；15；模型输入快照和易变文本规范化。
- [Goose prefix_invariance.rs](https://github.com/aaif-goose/goose/blob/0f4768025f517f5812f6d962a90aa52d509863cf/crates/goose-provider-types/tests/prefix_invariance.rs)：源码；15、3；缓存前缀不变的回归测试。
- [pydantic-ai: Testing](https://pydantic.dev/docs/ai/guides/testing/)：官方文档；15；TestModel / FunctionModel / override / `ALLOW_MODEL_REQUESTS=False`。
- [AI SDK Core: Testing](https://ai-sdk.dev/docs/ai-sdk-core/testing)：官方文档；15；`MockLanguageModelV4`、`simulateReadableStream`。

**体系化参考**
- [深入理解 AI Agent：设计原理与工程实践 第 6 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter6.md)：教学；7、12；「异步与事件驱动」一节讲事件结构化建模、按紧急度选队列式/取消式/并行式处理，以及同步接口下表达异步的五条规则。

**对照**
- [OpenAI: Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)：官方文档；4；Conversation 对象不受 30 天过期限制、链式调用仍按全部历史计费。

---

## 五、阅读顺序

1. **先建立"断开 ≠ 取消"的直觉**（30 分钟）：AI SDK 的 message persistence → resume streams → abort breaks resumable streams → resumable-stream README。读完就知道一个可刷新、可停止的聊天后端最少要几块。
2. **信任边界**（15 分钟）：pydantic-ai UI overview 的信任模型 + message-history 的信任边界一节。决定 9 主要依据这两篇。
3. **会话存储的真实样子**（1 小时）：Codex thread-store README → policy.rs → recorder.rs（看 `load_rollout_items`）→ opencode message-v2.ts（看转模型消息那段）→ opencode sync/README。重点看"存储视图怎么变成模型视图"和"老数据怎么兼容"。
4. **运行中插话**（30 分钟）：Codex v2/turn.rs（steer/interrupt 参数）→ turn.rs 第 415–600 行附近 → ext/queue → Goose ops_steer.rs。
5. **事件协议**（45 分钟）：AI SDK stream protocol → AG-UI events → AG-UI interrupts → Codex app-server README 的通知部分。三者对照着看，自己的协议该有哪些事件心里就有数了。
6. **多端和手机**（20 分钟）：OpenHands 的两个前端文件 + MDN EventSource 的连接数说明。
7. **后台任务**（45 分钟）：SQS 和 Celery 的可见性超时 → Postgres SKIP LOCKED → transactional outbox。先把自建方案的坑看清楚，再看持久化引擎。
8. **持久化执行**（1.5 小时）：pydantic-ai Persistence 和 Durable overview（先搞清楚到底需不需要）→ Temporal workflow-definition → pydantic-ai Temporal（最重要）→ Temporal limits 和 event history → Continue-As-New → Inngest 执行模型 → LangGraph interrupts。
9. **定时与 webhook**（30 分钟）：Kubernetes CronJob → Temporal Schedule → Slack / GitHub / Stripe 三篇 webhook 文档，对照第 7 节的数字。
10. **完成判断和测试**（30 分钟）：Goose final_output_tool / ops_stop_hook → opencode http-recorder README → Codex streaming_sse / context_snapshot → pydantic-ai Testing。
11. 做 CLI 才需要：Codex TUI 的 `paste_burst.rs` 和 `bottom_pane/mod.rs` 开头的 Ctrl-C 说明（见第 14 节，未单列进资料清单）。
