# 10 · 检索、记忆与 agent 间协议

> 只写「做过才知道、会让你选 A 不选 B」的东西。
> MCP 本身见 [05](05-mcp-design-choices.md)；多 agent 值不值得拆、15 倍 token 见 [03](03-agent-loop-context.md) 第 9 节和决定 3；租户过滤必须在代码里强制见 [04](04-eval-observability-security.md) 第二节第 5 条。本章只在这些基础上往下讲，不重复。
> 源码类证据来自 openai/codex main、anomalyco/opencode dev、google-gemini/gemini-cli main。带具体数字的地方，核对日期都是 2026-10-09，厂商随时可能改。

---

## 一、知识拆解

### 1. 向量这一层：模型、维度、归一化、前缀

**1.1 一个模型就是一个向量空间**

- 不同模型生成的向量不能混在一个索引里比。换模型基本等于全部重新生成向量。Gemini 文档明确写了 `gemini-embedding-001` 和 `gemini-embedding-2` 的向量空间不兼容，换了就得全量重算。
- 例外要看厂商有没有明说。Voyage 说 voyage-4 系列各型号生成的向量彼此兼容，可以文档用大模型、查询用小模型。没写「兼容」就当不兼容。
- 所以每条向量旁边都要存「哪个模型、哪个版本、多少维」。不存的话，迁移进行到一半时，你分不清哪些是旧的。

**1.2 维度和归一化**

- OpenAI：text-embedding-3-small 是 1536 维，-3-large 是 3072 维，单条输入最多 8192 token。可以用 `dimensions` 参数直接要短一点的向量。如果你自己截断，截完必须重新做 L2 归一化。OpenAI 的向量已经归一化，所以点积和余弦相似度结果一样，余弦和欧氏距离排出来的顺序也一样。
- Gemini：默认 3072 维，推荐 768/1536/3072。`gemini-embedding-001` 在非 3072 维时要你自己归一化，`gemini-embedding-2` 会自动归一化。（Gemini 文档页面标注的最后更新时间是 2026-09-17。）
- Voyage：`output_dimension` 可选 256/512/1024/2048，输出类型支持 int8 和 binary。Cohere 的 `embedding_types` 也支持 int8、binary 这些。
- 维度不只影响效果，也影响存储和能不能建索引。pgvector 每条 `vector` 占 4×维度+8 字节。它的 HNSW/IVFFlat 索引对 `vector` 最多支持 2000 维，`halfvec` 4000 维，`bit` 64000 维。也就是说，3072 维的 text-embedding-3-large 不能直接在普通 `vector` 列上建 HNSW 索引，要么降到 2000 维以内，要么改用 halfvec。

**1.3 查询和文档用的不是同一种「口气」**

很多模型要你告诉它这段文本是查询还是文档，不同厂商的做法不一样：

| 厂商 | 怎么区分查询和文档 | 不区分会怎样 |
| - | - | - |
| Cohere v2 embed | `input_type` 必填（v3 以后）：`search_document` / `search_query` / `classification` / `clustering` / `image` | 不填直接报错 |
| Voyage | `input_type` 设成 query 或 document，服务端会在文本前加一段固定提示；带和不带 input_type 生成的向量彼此兼容 | 能用，效果打折 |
| Gemini embedding-2 | 没有 `task_type` 参数，要你自己在文本里写前缀：查询写 `task: search result \| query: {内容}`，文档写 `title: {标题或 none} \| text: {内容}` | 拿 001 的写法（传 task_type）套到 2 上，前缀就丢了 |
| OpenAI text-embedding-3 | 不区分 | — |

这类前缀是「写入时」和「查询时」两边约定好的。改了前缀格式，效果上等于换了半个模型，旧数据要重算。

**1.4 批量和截断：最常见的「静默出错」**

- 截断默认是静默的：Voyage `truncation` 默认 True；Cohere `truncate` 默认 END（设成 NONE 才会报错）；Gemini 超出 8192 token 也是静默截断（001 的上限是 2048）。长文档只有前半段被向量化，你不会收到任何报错。
- Gemini 的坑：在一次调用的 `contents` 里放多段文本，得到的是**一个**合并后的向量，不是每段一个。要么每段包成单独的 Content，要么走 batch 接口。Batch API 价格是一半。
- 批量上限各家不同：Cohere 一次最多 96 条；Voyage 一次最多 1000 条，另外按模型限制总 token（1M / 320K / 120K 三档）。批处理代码要按条数和 token 两个维度切。

出处：[OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)、[Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)、[Voyage Embeddings](https://docs.voyageai.com/docs/embeddings)、[Cohere Embed API](https://docs.cohere.com/reference/embed)、[pgvector README](https://github.com/pgvector/pgvector)

### 2. 切块、混合检索和重排

**2.1 先问要不要检索**

Anthropic 的 Contextual Retrieval 文章开头就说：知识库小于 20 万 token（约 500 页）时，直接整个放进 prompt，配合 prompt 缓存，不用做 RAG。检索系统是有维护成本的，先用这条线过滤一遍。

**2.2 切块丢上下文的问题和补法**

- 一块文本被切出来后，常常不知道自己在讲哪家公司、哪个季度。Anthropic 的做法是：先让模型为每块生成一小段说明它在整篇里位置的文字，拼在块前面，再去做向量和 BM25。用了 prompt 缓存后，处理成本是每百万文档 token 1.02 美元。
- 他们给出的效果（top-20 检索失败率）：只用上下文向量，失败率降 35%（5.7%→3.7%）；再加 BM25，降 49%（→2.9%）；再加重排，降 67%（→1.9%）。另外，召回 20 块比 10 块、5 块效果好。

**2.3 混合检索：BM25 + 向量，用排名融合**

- BM25 的分数和余弦相似度不在一个尺度上，直接加权相加很难调。常用的是 RRF（倒数排名融合）：每个文档的分数是它在各路结果中排名的 `1/(k+排名)` 之和。
- Elasticsearch 的实现里，`rank_constant`（即 k）默认 60；`rank_window_size` 决定每一路取多少条参与融合，默认等于 `size`。`from + size` 超过 `rank_window_size` 时直接返回空，翻页时要注意。改了 `rank_window_size`，同样的查询排序也可能变。

**2.4 重排**

Anthropic 的设置是先召回 150 块，用重排模型挑出 20 块。重排是加在检索之后的一步，会增加延迟和费用，换来的是上面那 67% 里最后一段提升。

出处：[Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)、[Elasticsearch: Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)

### 3. 索引的生命周期：过滤、多租户、增量、删除、迁移

**3.1 带过滤条件的向量查询会「少返回」**

- pgvector 的近似索引（HNSW/IVFFlat）是先在索引里找近邻，再套 WHERE 条件。README 给的例子：条件只命中 10% 的行，HNSW 用默认 `hnsw.ef_search = 40`，平均只能返回 4 行。
- 解决办法：0.8.0 起有 `hnsw.iterative_scan`（`strict_order` 或 `relaxed_order`），不够数会自动多扫一些，上限由 `hnsw.max_scan_tuples`（默认 20000）控制；过滤值很少时用部分索引（`WHERE category_id = 123`）；过滤值很多时用分区。
- 加了近似索引后，查询结果和精确搜索会不一样。上线后要定期拿精确搜索的结果对比，看召回率。

**3.2 多租户**

- pgvector：多个租户共用一个近似索引时，一个租户的数据会影响另一个租户的召回和速度。要隔离，就按租户做 list 分区或者分表。
- Qdrant：不推荐每个租户一个 collection（每个都有资源开销，Qdrant Cloud 每个集群默认最多 1000 个 collection）。三种做法：
  - 按 payload 字段过滤：建 `is_tenant: true` 的 keyword 索引，适合大量小租户；还可以设 `m: 0, payload_m: 16`，关掉全局索引、只为每个租户单独建图，提高写入索引速度。
  - 每个租户一个 shard：隔离强，适合少量大租户。
  - 分层（v1.16.0 起）：小租户共用一个 shard，大租户升级成独立 shard。
- 不管哪种，租户条件都要由代码加上，见 [04](04-eval-observability-security.md) 第二节第 5 条。

**3.3 删除和更新**

- 一份文档会切成很多块，每块一条向量。删文档、改文档时，要能按文档 ID 找到它所有的块一起删，否则旧块会继续被检索出来。所以每条向量至少要带：文档 ID、块序号或块 ID、内容哈希（判断要不要重算）、模型版本、租户 ID。（这是根据上面几家的约束整理的做法，不是某个厂商的规定。）
- pgvector 的 HNSW 索引 VACUUM 会很慢，README 建议先 `REINDEX INDEX CONCURRENTLY` 再 `VACUUM`。删得多的表要把这个排进运维。

**3.4 换模型的迁移（Qdrant 教程讲得最完整）**

两种路线：

| 路线 | 步骤 | 回滚 | 坑 |
| - | - | - | - |
| 蓝绿（两个 collection） | 建新 collection → 开双写 → 后台 scroll 旧数据、用新模型重算、写进新 collection（不覆盖双写已写入的点）→ 拿自己的查询比较新旧效果 → 原子切换 alias → 观察一段时间 → 关双写、删旧 collection | 关双写之前随时能切回；关了以后再回滚会丢掉这期间的写入 | 迁移期间的**删除**会出错：新 collection 里还没有这个点，删除失败；之后迁移进程又把它从旧 collection 搬过来，被删的数据「复活」了。delete、delete_vectors、overwrite_payload、delete_payload 都要暂停或额外处理 |
| 命名向量（同一 collection，Qdrant 1.18+） | 加一个新的命名向量（只改 schema）→ 双写两个向量 → 后台只更新新向量 → 切查询里的 `using` → 观察 → 删旧向量 | 删旧向量前改回 `using` 就行 | 回填期间要暂停对已有点的更新和删除：并发更新会让回填用旧文本算出新向量。删旧向量是不能回头的一步 |

教程还强调：新模型在你的数据上不一定更好，切流量前用自己的查询算 Recall@10 之类的指标对比；更大的向量要更多内存，延迟也可能变。

出处：[pgvector README](https://github.com/pgvector/pgvector)、[Qdrant: Multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/)、[Qdrant: Migrate to a New Embedding Model](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/)

### 4. 检索方式：提前塞进上下文，还是让 agent 自己搜

- **提前检索（预注入）**：用户一问，系统先检索，把结果拼进 prompt。可控、一次调用，但检索错了模型没办法补救。
- **agent 自己搜**：把 grep、读文件、语义搜索做成工具，让模型多轮自己查。灵活，但轮次多、token 多。
- 代码场景的风向变化（时间线很重要）：
  - 2025-11-06，Cursor 发文说语义搜索让回答准确率平均高 12.5%（不同模型 6.5%–23.5%）；A/B 测试中代码保留率高 0.3%，1000 个文件以上的大仓库高 2.6%；结论是 grep 加语义搜索一起用最好。他们还用 agent 的搜索轨迹训练了自己的 embedding 模型。
  - 2026 年 8 月，Cursor 员工在官方论坛回复：模型用 grep 已经很好，单独的语义搜索已经没有明显帮助，现在 agent 用本地的 Instant Grep 加普通读文件，不再给代码算向量、也不在服务器上存。Cursor 文档同时写了 Explore 子 agent：在单独上下文里用更快的模型并行搜索，只把结论带回主对话。
  - Claude Code 早期用过 Voyage 嵌入做 RAG，也试过本地向量库，最后换成"模型自己用 glob/grep 多轮搜"，理由是效果更好、没有索引过期、不用处理索引的权限和安全（[Pragmatic Engineer 对 Boris Cherny 的访谈](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)）。
  - Cline 很早就不做代码索引，理由是：切块会切断代码之间的逻辑联系；索引要单独的流水线保持新鲜，旧索引会让模型引用已经不存在的函数；向量本身是额外的数据安全面。HN 讨论里也有人反驳说「agent 自己搜也是 RAG，只是检索器换成了模型」。
- 通用结论：检索方案依赖当前模型的能力，模型换代后要重新评估，不要当成一次性决定。对文本知识库，第 2 节的 20 万 token 线和 2.2 节的混合检索仍然是起点。

出处：[Cursor: Improving agent with semantic search](https://cursor.com/blog/semsearch)、[Cursor 论坛：Codebase Indexing not working in v3.12 onwards](https://forum.cursor.com/t/codebase-indexing-not-working-in-v-3-12-onwards/167527)、[Cursor Docs: Search](https://cursor.com/docs/agent/tools/search)、[Cline: Why Cline Doesn't Index Your Codebase](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)、[HN 讨论](https://news.ycombinator.com/item?id=44106944)

### 5. 记忆：谁写、谁读、存哪、怎么过期和纠错

**5.1 记忆分几类**

LangChain 的概念文档按心理学分三类：语义记忆（事实，比如用户偏好）、情景记忆（经历，常用作 few-shot 例子）、程序记忆（规则，常见形式是 agent 改自己的提示词）。语义记忆又有两种存法：

- 一个持续更新的「档案」（一份 JSON）：每次要把旧档案传进去生成新档案，档案大了容易出错。
- 一堆小条目的「集合」：新增简单、召回高，但模型要学会删改旧条目，有的模型爱重复插入，有的爱乱改；条目之间的关系也容易丢。

**5.2 什么时候写**

- 在主流程里写（hot path）：写完马上能用，用户能看到「已记住」；代价是增加延迟，模型要分心判断该记什么。ChatGPT 用的是一个 `save_memories` 工具。
- 在后台写：不影响响应速度，但要决定多久跑一次、什么时候触发（定时、对话空闲后、手动）。
- Codex 是后台写的完整例子（源码 `codex-rs/memories/`）：
  - 第 1 阶段，每个对话单独抽取：输出结构化的原始记忆、对话摘要、slug；抽取时做密钥脱敏（替换成 `[REDACTED_SECRET]`）；靠数据库租约和重试退避防止重复处理，有并发上限。
  - 第 2 阶段，全局合并：加一把全局锁，在一个带 git 基线的目录里改记忆文件、生成 diff；做合并的子 agent 不需要审批、不能联网、只能写本地，并且关掉了再派子 agent 的能力，防止递归。
  - 默认值（`config/src/types.rs`）：每次启动最多处理 2 个对话；只看 10 天内的对话；对话闲置 6 小时后才处理（注释建议 12 小时以上）；剩余额度低于 25% 不跑；合并时最多 256 条原始记忆；30 天没用到的记忆会被清理。
  - 临时会话和子 agent 会话不生成记忆。

**5.3 存在哪、谁能读**

- Anthropic 的 memory tool 是客户端执行的：模型只发出 view/create/str_replace/insert/delete/rename 这些文件操作，真正读写哪里由你的代码决定。`/memories` 只是一个前缀，你可以映射到每个用户的目录或数据库里的 key。这意味着权限、租户隔离、加密都是你的事。
- 文档点名要防路径穿越：`/memories/../../secrets.env` 这种路径必须拒绝，包括 URL 编码的 `%2e%2e%2f`；要规范化路径后再判断是否还在目录内；不能删除或重命名 `/memories` 根目录。
- 读的那一侧要控量：Anthropic 建议限制单个记忆文件大小和 view 返回字符数（模型那边超过 16000 字符会截断显示）；Claude Code 给子 agent 的记忆只自动加载 `MEMORY.md` 的前 200 行或 25KB。

**5.4 过期和纠错**

- 过期：Anthropic 建议定期删除长期没被访问的记忆文件；Codex 按 `usage_count` 和最后使用时间排序，30 天不用就清掉。
- 纠错：记忆是文件或条目，纠错就是改它。memory tool 的 `str_replace` 要求旧文本唯一，否则拒绝替换。用户说「你记错了」时，要能找到那一条改掉，而不是再追加一条矛盾的。

**5.5 记忆是注入攻击的持久化通道**

- 2024 年 Johann Rehberger 演示了 SpAIware：网页里的提示注入让 ChatGPT 调用记忆工具，写入「把之后所有对话发到某个地址」的指令，之后每个新对话都会带着这条记忆。OpenAI 修了外发数据的通道，但作者明确说，不可信内容仍然可以写入任意记忆。2025 年同样的攻击在 Windsurf 上复现，原因是 `create_memory` 自动调用、不需要人确认。
- Codex 的应对是「污染标记」：配置 `disable_on_external_context`（旧名 `no_memories_if_mcp_or_web_search`）打开后，用过 MCP 或网页搜索的对话会被标成 `memory_mode = 'polluted'`，不再参与记忆生成，并排队触发第 2 阶段的遗忘（`state/src/runtime/memories.rs`）。
- 原则：读过外部内容的对话，写记忆要么禁止，要么要人确认；记忆写入前脱敏；用户必须能看到并删除每一条记忆。

出处：[LangChain: Memory overview](https://docs.langchain.com/oss/python/concepts/memory)、[Anthropic: Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)、[Codex memories README](https://github.com/openai/codex/blob/main/codex-rs/memories/README.md)、[Codex config types.rs](https://github.com/openai/codex/blob/main/codex-rs/config/src/types.rs)、[Codex state memories.rs](https://github.com/openai/codex/blob/main/codex-rs/state/src/runtime/memories.rs)、[Embrace The Red: SpAIware](https://embracethered.com/blog/posts/2024/chatgpt-macos-app-persistent-data-exfiltration/)、[Embrace The Red: Windsurf SpAIware](https://embracethered.com/blog/posts/2025/windsurf-spaiware-exploit-persistent-prompt-injection/)

### 6. agent 之间、agent 和外部之间的协议

**6.1 先分清三种连接**

| 连接 | 协议 | 一句话 |
| - | - | - |
| agent ↔ 工具/数据 | MCP（见 05） | 调用的是一个能力，输入输出结构清楚，通常没有长状态 |
| agent ↔ 另一个 agent（常常跨团队、跨公司） | A2A | 对方是个黑盒，会自己规划、会反问、任务可能跑很久 |
| 编辑器/IDE ↔ 编码 agent | ACP（Agent Client Protocol） | 照着 LSP 设计，编辑器把 agent 当子进程启动 |
| 你的前端/其他系统 ↔ 你的 agent 服务 | 自己定义（参考 Codex app-server） | 线程、轮次、条目、审批回调、取消 |

A2A 自己的说法是：MCP 是「纵向」的，让一个 agent 能力更深；A2A 是「横向」的，跨越组织边界去找别的 agent。它也承认，一个 A2A agent 中定义清楚、无状态的技能可以直接暴露成 MCP 工具。

**6.2 A2A v1.0 的数据模型和操作**

- 规范的权威来源是 `spec/a2a.proto`，分三层：数据模型 → 操作 → 绑定（JSON-RPC、gRPC、HTTP+JSON 三种，规范保证等价）。
- 核心对象：
  - **Agent Card**：放在 `/.well-known/agent-card.json`。字段包括 `supportedInterfaces`（url、protocolBinding、tenant、protocolVersion）、`capabilities`（streaming、pushNotifications、extensions、extendedAgentCard）、`securitySchemes`（apiKey、http、oauth2 含设备码流程、oidc、mtls）、`skills`，可以带 JWS 签名。登录后可用 GetExtendedAgentCard 拿到更详细的版本。
  - **Message**：用来沟通。**Artifact**：用来放结果。Message 不保证送达，重连流时可能漏掉状态消息，所以结果一定放 Artifact。
  - **Part**：text、raw（base64）、url、data 四选一。
  - **Task**：`taskId` 永远由服务端生成，客户端不能自己定；`contextId` 把多个任务归成一组；两者不匹配必须拒绝。
- 操作：SendMessage（返回 Task 或直接返回 Message）、SendStreamingMessage、GetTask（可用 historyLength 控制带多少历史）、ListTasks（游标分页，pageSize 最大 100、默认 50，按更新时间倒序，只能列出当前调用方有权看的）、CancelTask（幂等，可能返回不可取消错误）、SubscribeToTask、推送配置的增删查、GetExtendedAgentCard。
- `returnImmediately` 默认 false：SendMessage 会一直等到任务进入终态，或进入 INPUT_REQUIRED/AUTH_REQUIRED 才返回。做长任务时要显式设 true，然后轮询或订阅。
- SendMessage 按 messageId 去重是「可以做」，不是「必须做」。客户端重试可能造成重复任务，别依赖对方去重。

**6.3 任务状态和「终态不可重启」**

- 状态：SUBMITTED、WORKING；终态 COMPLETED、FAILED、CANCELED、REJECTED；中断态 INPUT_REQUIRED、AUTH_REQUIRED。JSON 里写作 `TASK_STATE_COMPLETED` 这种形式。
- 任务进入终态后不能再继续，往终态任务发消息会报 UnsupportedOperationError。想在结果上改，要在同一个 `contextId` 下新建任务，用 `referenceTaskIds` 指向原任务。好处是每个产物都能追溯到一个确定的任务。
- 产物的版本历史由**客户端**维护，协议不管。服务端改出新版本时应保持同一个 artifact 名字、换新的 artifactId。
- agent 可以只回 Message、只回 Task，或者先用 Message 商量范围、再建 Task 执行。一旦建了 Task，之后对这个任务的回复都只能是 Task。

**6.4 流、订阅、推送**

- 一个任务可以同时有多个流。任务的生命周期不依附于某个流，关掉一个流不影响任务。
- SubscribeToTask 返回的第一个事件必须是任务当前状态，这样「先 Get 再 Subscribe」中间不会漏事件。
- 推送通知（webhook）是「至少一次」送达，接收方要按幂等处理重复；载荷和流事件同一格式。规范建议 webhook 超时 10–30 秒，失败时指数退避重试，连续失败多次可以停止。
- 推送的安全要求（第 13.2 节）：发送方要校验 webhook URL 防 SSRF（拒绝 127/8、10/8、172.16/12、192.168/16、localhost、链路本地地址，必要时用白名单）；接收方必须验证请求身份、核对任务 ID 是自己创建的、返回 2xx、做限流；每个推送配置用单独的一次性用途 token。

**6.5 版本和 v0.3 → v1.0 的破坏性改动**

- 请求头 `A2A-Version` 为空时按 0.3 处理；不支持的版本返回 VersionNotSupportedError（-32009）；SDK 不应悄悄降级到旧版本。v1.0 起每个 interface 单独声明 `protocolVersion`，一个 agent 可以同时暴露新旧两个版本的入口。
- v1.0 改动里影响最大的：Part 从 TextPart/FilePart/DataPart 加 `kind` 字段，改成一个 Part 用字段名区分；流事件从 `kind` 改成包一层 `statusUpdate`/`artifactUpdate`；Agent Card 的 url/preferredTransport 移进 `supportedInterfaces`；枚举从 `completed` 改成 `TASK_STATE_COMPLETED`、角色从 `user` 改成 `ROLE_USER`；分页从页码改成游标；错误改用 google.rpc.Status，HTTP+JSON 的 Content-Type 从 `application/problem+json` 改成 `application/json`。
- 网上 2025 年的 A2A 教程大多是 0.2/0.3 写法，照抄会和 v1.0 的服务端对不上。

**6.6 A2A 的授权规则**

- 每个操作都要做授权检查，**在查数据库之前**做，避免泄露「这个资源存在」。即使请求没带 contextId 之类的过滤条件，也只能返回调用方有权看的。
- 「找不到」和「没权限」对外必须看起来一样（统一返回 TaskNotFound）。
- 扩展版 Agent Card 必须登录后才能拿，不要放内部服务地址、明文凭证。

**6.7 ACP（编辑器和编码 agent 之间）**

- 本地 agent 作为子进程启动，走 stdio 上的 JSON-RPC；远程支持还在开发中。
- 生命周期：initialize（交换能力）→ authenticate → session/new（`cwd` 必须是绝对路径，同时传入这个会话可用的 MCP 服务器列表）或 session/load（把完整历史以 session/update 通知重放一遍）或 session/resume（不重放）→ session/prompt。
- agent 往编辑器推的 session/update 有：用户/agent 消息片段、思考片段、tool_call 和 tool_call_update、plan、可用命令变化、模式变化、配置变化、会话信息、用量（已用/上限/费用）。
- 审批：agent 调 `session/request_permission`，给出选项，选项的 kind 是 allow_once / allow_always / reject_once / reject_always。「记住选择」是协议里的一等概念。
- 取消：`session/cancel` 是通知（没有响应）。编辑器要把还挂着的审批请求都回成 `cancelled`；agent 要捕获中断异常，以 stopReason `cancelled` 正常结束这轮，而不是返回错误；取消之后、prompt 响应之前，仍可能收到更新。stopReason 共 5 种：end_turn、max_tokens、max_turn_requests、refusal、cancelled。
- 文件读写可以走编辑器：`fs/read_text_file` 读的是编辑器里**包括未保存修改**的内容，和磁盘上的不一定一样。agent 用自己的文件工具读磁盘，会和用户屏幕上看到的不一致。
- 约定：所有路径必须是绝对路径，行号从 1 开始；自定义方法以 `_` 开头；扩展数据放 `_meta`。MCP 服务器配置里的 env 可能带密钥，日志里要脱敏。

**6.8 你自己的 agent 作为服务时，API 长什么样（以 Codex app-server 为参照）**

事件流怎么推给界面、断线续流、多端同步见 [08](08-sessions-jobs-frontend.md) 第 9、11 节；这里只看对外接口的形状。

- 三个层级：Thread（会话）→ Turn（一轮）→ Item（一条消息、一次工具调用等）。传输有 stdio JSONL、websocket（实验）、unix socket。每个连接先 initialize/initialized 握手；实验性接口要客户端主动声明 `experimentalApi`；客户端可以用 `optOutNotificationMethods` 屏蔽不想要的通知。
- 线程操作：start、resume、fork（可指定从哪一轮分叉，在一轮进行中分叉会记录一个中断标记）、read、list、archive、delete（连带删除派生出的子线程）、unsubscribe（没有订阅者 30 分钟后卸载）。
- 轮次操作：turn/start（这轮的覆盖参数会成为之后的默认值，但 `outputSchema` 只对这一轮有效）、turn/steer（必须带 `expectedTurnId`，防止插话插到别的轮次）、turn/interrupt（这一轮以 `interrupted` 结束）。
- 事件：item/started → 若干 delta → item/completed（以它为准）；turn/completed 带状态 completed/interrupted/failed，失败时带错误类型（比如上下文超限、额度用完）。
- 审批是**服务端发给客户端的请求**，决定有 accept / acceptForSession / decline / cancel，处理完再发一个 `serverRequest/resolved` 通知。网络访问的审批按主机+协议+端口合并。向用户提问的请求可以设自动处理超时。
- 过载时返回 -32001「Server overloaded; retry later」，客户端要带抖动退避。
- 换模型恢复旧线程时，会给出警告，并插入一次性的「模型已切换」说明。
- 可以按版本导出 TypeScript 类型和 JSON Schema，客户端和服务端版本对齐靠这个。

**6.9 实现和规范之间的差距（以 gemini-cli 的 A2A 服务端为例，标注为实验性）**

- 每轮 agent 回答结束后，任务被置为 input-required，而不是 completed。所有工具都在等审批时，也是 input-required。
- 客户端断开连接时，执行器会中止任务并置为 input-required（附说明「Execution aborted by client」）；显式取消才是 canceled。规范说任务生命周期和连接无关，这个实现里断线就等于停工。
- 对已经是终态（canceled/failed/completed）的任务再发消息，会把它重新置回 submitted，和规范的「终态不可重启」不一致。
- 持久化用 GCS 存任务元数据和整个工作目录的 tar.gz；taskId 用 `^[a-zA-Z0-9_-]+$` 校验，防止路径穿越。
- 结论：接别人的 A2A agent 时，不要假设它严格按规范处理断线和终态，要用 GetTask 确认真实状态。

出处：[A2A Specification](https://a2a-protocol.org/latest/specification/)、[A2A: Life of a Task](https://a2a-protocol.org/latest/topics/life-of-a-task/)、[A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)、[A2A: What's New in v1.0](https://a2a-protocol.org/latest/whats-new-v1/)、[ACP Overview](https://agentclientprotocol.com/protocol/v1/overview)、[ACP Session Setup](https://agentclientprotocol.com/protocol/v1/session-setup)、[ACP Prompt Turn](https://agentclientprotocol.com/protocol/v1/prompt-turn)、[ACP Tool Calls](https://agentclientprotocol.com/protocol/v1/tool-calls)、[ACP File System](https://agentclientprotocol.com/protocol/v1/file-system)、[Codex App Server](https://learn.chatgpt.com/docs/app-server)、[gemini-cli a2a-server executor.ts](https://github.com/google-gemini/gemini-cli/blob/main/packages/a2a-server/src/agent/executor.ts)、[gemini-cli a2a-server gcs.ts](https://github.com/google-gemini/gemini-cli/blob/main/packages/a2a-server/src/persistence/gcs.ts)

### 7. 子 agent：传什么、给多大权限、限多少、出错谁管

**7.1 传什么上下文**

三种做法：

- **只传任务描述（全新上下文）**：Claude Code 默认子 agent 看不到主对话历史，只拿到主 agent 写的委派说明，外加它自己的系统提示、CLAUDE.md、git 状态快照。Anthropic 研究系统的经验是委派说明要写四样：目标、输出格式、该用哪些工具和来源、任务边界；写得太短，子 agent 会重复劳动或漏掉内容。
- **复制完整历史（fork）**：Claude Code 的 fork 继承全部对话、系统提示、工具和模型，因此能复用主对话的 prompt 缓存，成本更低；代价是失去隔离，fork 不能再派 fork。Codex 也有 `full_history_fork` 选项。
- **过滤后的历史**：OpenAI Agents SDK 的 handoff 默认把完整历史交给下一个 agent，可以用 `input_filter` 过滤（比如 `remove_all_tools` 去掉工具调用条目）。两个容易踩的坑：
  - `remove_all_tools` 只去掉结构化的工具条目，已经写进普通消息或摘要里的工具参数和结果不会被去掉。嵌套历史（`nest_handoff_history`，beta、默认关闭）是把历史压成摘要，**不是脱敏**。
  - 用服务端托管的对话（`conversation_id`、`previous_response_id`）时不支持 input_filter；不想让下一个 agent 继承历史，就得另起一次运行，并且不要复用原来的对话 ID。
- 结果怎么回来：Anthropic 建议子 agent 把大块产出写到文件系统或外部存储，只把引用传回主 agent，避免主 agent 转述时丢信息（他们叫「传话游戏」）。

**7.2 权限是继承还是收窄**

- opencode（`subagent-permissions.ts`）：子 agent 只继承**会话级**的 deny 规则和外部目录规则，不继承 allow 规则；子 agent 自己没明确允许的话，默认禁止再派子 agent（`task`）和写待办（`todowrite`）。思路是「限制往下传，授权不往下传」。
- Claude Code：子 agent 不设 `permissionMode` 时继承主对话的模式；主对话处于 bypassPermissions、acceptEdits 或 auto 时，子 agent 设什么都被忽略、跟主对话一样。工具默认继承主对话可用的工具，再用 `tools` 白名单或 `disallowedTools` 黑名单收窄。插件里带的子 agent 不允许设 hooks、mcpServers、permissionMode。
- Claude Code 还有两条规则值得照抄：任何 agent 发来的消息都不算用户批准，也不能改子 agent 的权限设置；子 agent 的最终报告在交给主 agent 前会被扫描，像系统标签、`Human:` 这类模仿格式的文本会被转义，提到权限绕过的会加标记行。
- Codex（`child_config.rs`）：子 agent 从父 agent 当前生效的配置出发，再叠加这一步的模型、推理强度、审批策略、沙箱、工作目录，最后叠加角色配置。源码注释特意提醒：不要复制过期的配置，否则子 agent 会用错误的模型服务商或策略启动。

**7.3 深度、并发、预算**

| 系统 | 深度 | 并发/数量 | 其他 |
| - | - | - | - |
| Codex | 默认最大深度 1（子 agent 不能再派） | 默认最多 6 个线程；multi-agent v2 每会话最多 4 个并发 | 等待子 agent 的超时最短 10 秒、默认 30 秒、最长 1 小时；一次派发最多覆盖 5 个模型参数 |
| Claude Code | 默认往下 3 层（v2.1.219 起；之前出现过 5 层、1 层的默认值），`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 可改 | 同时运行 20 个时拒绝再派，报错并告诉模型不要重试；整个会话的总数不设上限 | `maxTurns` 到了以后返回结果并标记为部分完成，可以续跑 |

- 到达深度上限时，Claude Code 直接不给子 agent 派发工具（fork 例外，工具还在但调用会报错）。「不给工具」比「给了再报错」更省 token。
- Anthropic 的研究系统把工作量规则写进提示词：简单查事实 1 个 agent、3–10 次工具调用；对比类 2–4 个子 agent、每个 10–15 次；复杂研究 10 个以上子 agent。模型自己判断工作量容易过度投入。

**7.4 出错谁负责**

- Claude Code：前台子 agent 被限流或服务端错误打断时，如果已经有文字输出，就把部分输出连同「没做完」的说明交回主 agent；什么都没产出则报错。后台子 agent 被标为失败，最后的输出随失败通知一起交回。配了备用模型链时会自动切模型继续。
- Codex app-server：turn/completed 的状态是 failed 时带错误类型，由调用方决定重试还是换策略。
- A2A：子任务失败就是 FAILED 终态，不能原地重试，要新建任务。
- 原则：子 agent 只负责「如实报告做到哪、为什么停」；重试、换方案、告诉用户由主 agent 决定。主 agent 要能区分「完成」「部分完成」「失败」三种结果。

出处：[Claude Code: Create custom subagents](https://code.claude.com/docs/en/sub-agents)、[OpenAI Agents SDK: Handoffs](https://openai.github.io/openai-agents-python/handoffs/)、[Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)、[opencode subagent-permissions.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/agent/subagent-permissions.ts)、[Codex child_config.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/agent/child_config.rs)、[Codex config/mod.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/config/mod.rs)

---

## 二、文章很少讲但常碰到的事

1. **截断默认不报错。** Voyage、Cohere、Gemini 的 embedding 接口默认都会悄悄截掉超长部分。长文档只有开头被检索到，排查时很难想到这里。要么切块时按 token 数严格控制，要么把截断参数改成报错。
2. **Gemini 一次传多段文本只返回一个向量。** 批量写入时以为拿到 N 个向量，其实是 1 个合并的。
3. **换模型 ≠ 换个参数。** 不同模型的向量空间不兼容，前缀格式（Gemini embedding-2 写在文本里、Cohere/Voyage 用 input_type）也算模型约定的一部分。每条向量要记录模型、版本、维度、前缀格式。
4. **3072 维在 pgvector 里建不了普通 HNSW 索引。** 上限是 2000 维，要降维或用 halfvec。选模型时就要想到存储。
5. **带过滤的向量查询会少返回。** pgvector 默认参数下，命中 10% 的条件平均只返回 4 行。做多租户、按权限过滤时这个问题必然出现。
6. **租户共用索引会互相影响召回。** 不只是安全问题，也是效果和速度问题。
7. **迁移期间的删除会让数据复活。** 蓝绿迁移时，删除在新库里找不到点就失败了，之后迁移进程又把旧数据搬过去。要么迁移时暂停删除，要么记录墓碑（删除记录）在迁移结束后补删。
8. **代码检索的结论一年内反转。** Cursor 2025 年 11 月说语义搜索提升 12.5%，2026 年 8 月就去掉了语义索引改用本地 grep。检索方案要跟着模型能力定期重新评估。
9. **记忆是注入攻击的持久化通道。** 一次网页注入写进记忆，以后每个对话都受影响。读过外部内容的对话要么不写记忆，要么写之前要人确认（Codex 的 polluted 标记是可以照抄的实现）。
10. **memory tool 的存储在你这边，权限也在你这边。** 路径穿越、按用户隔离、大小上限、过期清理，Anthropic 文档全列成了「你的责任」。
11. **A2A 的 SendMessage 默认是阻塞的。** `returnImmediately` 默认 false，长任务会把 HTTP 连接挂到超时。
12. **A2A 推送至少送达一次，webhook 地址是 SSRF 入口。** 接收方要幂等，发送方要拦内网地址。
13. **「找不到」和「没权限」要返回一样的错误，并且授权在查库之前做。** 否则可以靠错误码探测别人的任务 ID。
14. **2025 年的 A2A 教程大多过时。** v1.0 改了 Part 结构、流事件格式、枚举值、分页、错误格式。
15. **ACP 读文件读的是编辑器缓冲区。** 用户没保存的修改也在里面，和磁盘不一致。
16. **取消不是错误。** ACP 要求以 `cancelled` 正常结束这一轮，并把挂起的审批都回成 cancelled；取消后仍可能收到更新，界面要容忍。
17. **断线是否等于取消，各家实现不同。** 规范说任务和连接无关，gemini-cli 的实现里断线就中止。接入方要用查询接口确认状态，不要只看连接。
18. **子 agent 的权限只该往下收窄。** opencode 只继承 deny、默认禁止递归派发；Claude Code 规定其他 agent 的消息不算批准。
19. **「过滤历史」不等于「脱敏」。** OpenAI Agents SDK 的工具过滤和嵌套摘要都可能留下工具参数和结果；服务端托管对话时干脆不能过滤。
20. **深度和并发上限各家默认值差很多。** Codex 默认深度 1、Claude Code 默认 3 层、并发 20；Claude Code 的深度默认值在几个小版本里改过两次（5 层 → 1 层 → 3 层）。自己做的话要显式配置，并让超限的提示告诉模型「不要重试」。
21. **多 agent 的故障是"拜占庭式"的。** agent 很少直接停掉，而是继续给出看似可信的错误结论，而且错误会在转述中被下游放大。打断这条链要靠独立视角的交叉验证：审查者不看前面 agent 的思考过程，只对照原始证据和结论。失控的 agent 还可能派生出上千个子 agent，自主性强的 agent 要用独立的 API key 限住花费。出处：[李博杰《深入理解 AI Agent》第 10 章「多 Agent 协作的失败模式」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter10.md)、[Why Do Multi-Agent LLM Systems Fail?（论文）](https://arxiv.org/abs/2503.13657)。

---

## 三、要拿的主意

### 决定 1：换 embedding 模型

**问题**：新模型更好或更便宜，要不要换、怎么换不停服？

| 选项 | 代价 | 什么情况选 |
| - | - | - |
| 不换 | 继续用旧模型，厂商下线时被动迁移 | 新模型在你自己的查询集上没有明显提升 |
| 蓝绿：新建库 + 双写 + 回填 + 切别名 | 两份存储；迁移期间删除和部分更新要暂停或特殊处理；关双写后不能无损回滚 | 任何存储都适用；数据量大、需要随时回滚 |
| 同库加一列/一个命名向量 | 回填期间更新和删除要暂停；删旧向量后不能回头 | 存储支持多向量列（Qdrant 1.18+ 命名向量、pgvector 加一列），想少一份 collection |
| 同家族兼容模型直接切查询端 | 只在厂商明确写了兼容时可行 | 比如 Voyage-4 系列内部换型号 |

**检查清单**：维度会不会超过索引上限（pgvector 2000）；要不要重新归一化；查询和文档的前缀/input_type 有没有变；截断参数是否显式设置；用自己的查询集比较 Recall@10 再切；迁移过程中的删除怎么处理。

### 决定 2：向量存储：托管向量库还是 pgvector，多租户怎么隔离

| 选项 | 代价 | 什么情况选 |
| - | - | - |
| pgvector（和业务数据同库） | 删除、权限、事务和业务表一起做，最省同步工作；但近似索引带过滤会少返回，要调 iterative_scan 或分区；维度上限 2000；HNSW 的 VACUUM 慢 | 数据量中等，最重要的是删除和权限与业务数据保持一致 |
| 专门的向量库（Qdrant 等） | 多一个系统，业务库删了数据要同步过去；但租户隔离有现成方案（payload 租户索引、按租户分 shard、分层） | 数据量大、租户数多且大小差别大、需要独立扩容 |
| 每个租户一个库/collection | 资源开销大，Qdrant Cloud 默认最多 1000 个 collection | 租户少、要求强隔离（合规） |

**判断**：先问「删除和权限要多强的一致性」。要求「用户删了文档，立刻搜不到」时，和业务数据同库最省事；选独立向量库就要设计删除同步（按文档 ID 删全部块、失败重试、定期对账）。

### 决定 3：提前检索还是让 agent 自己搜

| 选项 | 代价 | 什么情况选 |
| - | - | - |
| 全部塞进上下文 + 缓存 | 每次请求都带全部内容，贵在 token，便宜在工程 | 知识库小于约 20 万 token |
| 提前检索（混合检索 + 重排）后注入 | 要维护索引流水线、处理新鲜度和删除；检索错了模型补救不了 | 文本知识库、问答类、要求一次调用低延迟 |
| 给 agent 搜索工具（grep/读文件/语义搜索）多轮自查 | 轮次多、token 多；需要好的工具描述 | 代码库、结构化目录、内容变化快；模型够强 |
| agent 自查 + 用子 agent 隔离搜索过程 | 多一层调用，主 agent 只看到摘要 | 搜索产生大量中间结果、会撑爆主上下文 |

**判断**：代码场景现在倾向 grep + 读文件 + 子 agent 搜索（Cursor、Cline 都这么做）；非代码文本知识库仍以混合检索 + 重排为起点。无论选哪个，都在模型换代时重新跑一遍对比。

### 决定 4：记忆：谁写、谁读、怎么过期、用户能不能看和删

| 问题 | 选项 | 代价 | 建议 |
| - | - | - | - |
| 谁写 | 主流程中模型调工具写 / 后台异步抽取 | 前者增加延迟、容易被注入；后者有延迟、要调度 | 用户明确说「记住」走前者并展示给用户；习惯和偏好类走后台抽取 |
| 写什么 | 档案（一份 JSON）/ 条目集合 | 档案越大越难更新；集合要处理重复和删改 | 少量稳定字段用档案；开放式信息用集合 |
| 外部内容 | 照常写 / 禁写 / 写前确认 | 照常写有持久化注入风险 | 读过网页、MCP、第三方文档的对话禁写或确认（参考 Codex polluted） |
| 谁能读 | 只有本人 / 团队共享 / 子 agent 也读 | 共享越多，泄露和污染面越大 | 按用户隔离；子 agent 默认不读主对话的记忆（Claude Code 就是这样），需要时单独给 |
| 过期 | 不过期 / 按未使用天数 / 按条数上限 | 不过期会越积越多、旧事实误导 | 按「最后使用时间」清理（Codex 默认 30 天）+ 总量上限 |
| 纠错 | 追加新条 / 原地修改 | 追加会留下互相矛盾的记忆 | 原地修改，要求匹配唯一 |
| 用户可见 | 隐藏 / 可查看 / 可查看可删除 | 隐藏的记忆出了问题用户无法自救 | 每条可查看、可删除、可导出；写入前脱敏 |

### 决定 5：什么时候需要 A2A / ACP，只用 MCP 够不够；自己的 agent 服务暴露什么接口

| 场景 | 选 | 理由 |
| - | - | - |
| 对方是确定的函数（查订单、跑 SQL） | MCP 工具（见 05） | 无状态、输入输出清楚 |
| 对方是别的团队/公司的 agent，会反问、跑很久、要鉴权 | A2A | 有任务状态、input-required、推送、Agent Card 发现和多种鉴权 |
| 你在做编码 agent，想接进多个编辑器 | ACP | 编辑器负责 UI、审批、文件缓冲区，agent 只写一次 |
| 你自己的前端或业务系统调用你的 agent | 自定义 API（参照 Codex app-server） | 没必要为一个调用方套用通用协议 |
| 内部两个 agent 在同一进程 | 都不用，直接函数调用/子 agent | 协议只增加序列化和版本问题 |

**自定义 agent 服务至少要有的接口**（综合 A2A 和 Codex app-server）：

- 提交：建会话/线程、提交一轮输入，服务端生成任务 ID；提交可以选择立即返回。
- 订阅：流式事件（开始、增量、完成，以完成事件为准），首个事件是当前完整状态；断线后能按 ID 重新订阅；关键结果另存成产物，不只靠流消息。
- 审批回调：服务端主动向客户端发请求，选项包括「这次允许 / 本会话允许 / 拒绝 / 取消」，处理完广播一个「已处理」事件，好让多个界面同步。
- 中途插话：带上「期望的当前轮次 ID」，不匹配就拒绝。
- 取消：幂等；取消后这一轮以「已中断」正常结束，不当错误；挂起的审批一起回成取消。
- 查询和列表：列表只返回调用方有权看的，游标分页；「找不到」和「没权限」统一错误。
- 回调推送（如果有）：至少一次、幂等、URL 防 SSRF。
- 过载：明确的「请稍后重试」错误码，客户端带抖动退避。
- 版本：请求带协议版本，不支持就明确报错，不悄悄降级；导出 schema 给客户端生成类型。

### 决定 6：子 agent：传什么、给什么权限、限多少、失败谁管

| 问题 | 选项 | 代价 | 什么情况选 |
| - | - | - | - |
| 上下文 | 只传任务说明 | 说明写不好就误解任务 | 子任务独立、以读为主（并行搜索、跑测试看结果） |
| | 复制完整历史（fork） | 失去隔离；但能复用 prompt 缓存 | 子任务需要大量背景，且信任边界相同 |
| | 过滤后的历史 | 过滤不等于脱敏；服务端托管对话可能不支持 | 交接给另一个专职 agent 继续对话（客服转退款） |
| 权限 | 完全继承 | 子 agent 会拿到父 agent 的所有授权 | 很少合适 |
| | 只继承禁止项 + 自己的白名单 | 要为每类子 agent 写权限 | 默认选它（opencode 做法） |
| | 父 agent 处于「免审批」模式时子 agent 跟随 | 风险随父 agent 放大 | 只在父 agent 本身就在沙箱里时接受 |
| 递归 | 允许子 agent 再派 | 树形扩张，成本难控 | 明确的「审查者再派验证者」这种两层结构 |
| | 默认禁止 | 少一些并行 | 默认选它，到上限时直接不给派发工具 |
| 预算 | 深度、并发、每个子 agent 的轮数 | 设太小会出现「部分完成」 | 三者都显式配置；超限错误告诉模型不要重试 |
| 失败 | 子 agent 自己重试到成功 | 隐藏问题、浪费预算 | 不推荐 |
| | 子 agent 如实返回「完成/部分完成/失败 + 原因 + 已有产出」，主 agent 决定 | 主 agent 逻辑多一些 | 默认选它 |

另外两条：子 agent 的输出对主 agent 来说是不可信内容（可能读过网页），回传前要能识别其中模仿系统格式的指令；其他 agent 发来的消息不能当作用户批准。

---

## 四、资料清单

**向量与检索**

- [OpenAI: Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)：官方说明；1.2；`dimensions` 缩短、自行截断要重新归一化、点积等于余弦、输入上限，是理解「维度和归一化」最短的一篇。
- [Gemini API: Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)：官方说明；1.1–1.4；001 和 2 不兼容、embedding-2 没有 task_type 要自己写前缀、多段输入合并成一个向量、归一化差异。坑最多的一份文档。
- [Voyage AI: Embeddings](https://docs.voyageai.com/docs/embeddings)：官方说明；1.1、1.3、1.4；voyage-4 系列互相兼容（换模型的少见例外）、input_type 的实际含义、截断默认开、批量的条数和 token 上限。
- [Cohere: Embed API v2](https://docs.cohere.com/reference/embed)：API 参考；1.3、1.4；input_type 必填、一次 96 条、truncate 默认 END。
- [pgvector README](https://github.com/pgvector/pgvector)：源码仓库文档；1.2、3.1–3.3；维度上限、带过滤少返回的具体数字和 iterative_scan、多租户互相影响、VACUUM 建议。用 Postgres 存向量必读。
- [Qdrant: Multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/)：官方说明；3.2；三种租户隔离方式和各自适用的租户规模，以及关掉全局索引按租户建图的做法。
- [Qdrant: Migrate to a New Embedding Model](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/)：教程；3.4；蓝绿和命名向量两条迁移路线的完整步骤，点明迁移期间删除导致数据复活、回填期间并发更新的问题和不可回头的那一步。不限于 Qdrant，思路通用。
- [Elasticsearch: Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)：官方说明；2.3；RRF 公式、k 默认 60、rank_window_size 和翻页的关系，带完整算例。
- [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)：分析（含实验数字）；2.1–2.4；20 万 token 以下直接塞、上下文前缀、BM25、重排各自带来的失败率下降。
- [Cursor: Improving agent with semantic search](https://cursor.com/blog/semsearch)：分析（含 A/B 数字）；4；语义搜索对代码 agent 的提升幅度和用 agent 轨迹训练 embedding 的方法。要和下一条一起读。
- [Cursor 论坛：Codebase Indexing not working in v3.12 onwards](https://forum.cursor.com/t/codebase-indexing-not-working-in-v-3-12-onwards/167527)：官方员工回复；4；2026 年 8 月放弃语义索引、改用本地 Instant Grep 的原因。
- [Cursor Docs: Search](https://cursor.com/docs/agent/tools/search)：官方说明；4；Instant Grep 本地建索引、Explore 子 agent 隔离搜索上下文。
- [Cline: Why Cline Doesn't Index Your Codebase](https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing)：分析；4；不给代码建向量索引的三条理由（切块、新鲜度、安全）。
- [Building Claude Code with Boris Cherny（Pragmatic Engineer）](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)：访谈；4；Claude Code 从 RAG 换到 glob/grep 的经过和理由（索引过期、权限复杂），和 Cursor、Cline 两篇对照读。
- [HN: Why Cline doesn't index your codebase 讨论](https://news.ycombinator.com/item?id=44106944)：讨论；4；反方观点「agent 自查也是 RAG」，用来平衡上一条。

**记忆**

- [LangChain: Memory overview](https://docs.langchain.com/oss/python/concepts/memory)：概念说明；5.1、5.2；三类记忆、档案和集合两种存法的取舍、主流程写和后台写的取舍。框架无关，是决策框架。
- [Anthropic: Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)：官方说明；5.3、5.4；客户端执行的记忆工具、六个命令的精确行为、路径穿越防护、大小上限和过期建议。
- [Codex memories README](https://github.com/openai/codex/blob/main/codex-rs/memories/README.md)：源码文档；5.2；两阶段后台记忆流水线、脱敏、全局锁、合并子 agent 的权限限制。
- [Codex config/src/types.rs](https://github.com/openai/codex/blob/main/codex-rs/config/src/types.rs)：源码；5.2、5.5；记忆的所有默认值和外部内容禁写开关。
- [Codex state/src/runtime/memories.rs](https://github.com/openai/codex/blob/main/codex-rs/state/src/runtime/memories.rs)：源码；5.5；把对话标为 polluted 并触发遗忘的实现。
- [Embrace The Red: SpAIware（ChatGPT 记忆注入）](https://embracethered.com/blog/posts/2024/chatgpt-macos-app-persistent-data-exfiltration/)：安全分析；5.5；记忆如何把一次注入变成持续的数据外泄，以及修复后仍可写入任意记忆。
- [Embrace The Red: Windsurf SpAIware](https://embracethered.com/blog/posts/2025/windsurf-spaiware-exploit-persistent-prompt-injection/)：安全分析；5.5；同样的攻击在编码 agent 上复现，根因是记忆工具自动调用不需确认。

**agent 间协议与服务接口**

- [A2A Specification (v1.0)](https://a2a-protocol.org/latest/specification/)：规范；6.2–6.6；操作、状态、流和推送的语义、错误码、版本头、第 13 节安全要求。
- [A2A: Life of a Task](https://a2a-protocol.org/latest/topics/life-of-a-task/)：说明；6.3；Message 和 Task 怎么选、终态不可重启、产物版本由客户端管理。
- [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)：说明；6.1；官方给出的两者分工（纵向/横向），和 05 对照读。
- [A2A: What's New in v1.0](https://a2a-protocol.org/latest/whats-new-v1/)：迁移说明；6.5；v0.3 到 v1.0 的全部破坏性改动和迁移优先级。读任何旧教程前先看。
- [ACP: Overview](https://agentclientprotocol.com/protocol/v1/overview)：规范；6.7；ACP 的定位、传输和整体流程。
- [ACP: Session Setup](https://agentclientprotocol.com/protocol/v1/session-setup)：规范；6.7；session/new、load、resume 的区别，MCP 服务器列表按会话传入。
- [ACP: Prompt Turn](https://agentclientprotocol.com/protocol/v1/prompt-turn)：规范；6.7；一轮的完整流程、stopReason、取消的精确语义。
- [ACP: Tool Calls](https://agentclientprotocol.com/protocol/v1/tool-calls)：规范；6.7；工具调用状态和四种审批选项。
- [ACP: File System](https://agentclientprotocol.com/protocol/v1/file-system)：规范；6.7；通过编辑器读写文件、读到未保存内容。
- [OpenAI Codex: App Server](https://learn.chatgpt.com/docs/app-server)：官方说明；6.8；一个生产级「agent 即服务」的完整接口：线程/轮次/条目、插话、中断、审批请求、过载错误。设计自己的 agent API 时最好的参照。
- [gemini-cli a2a-server（executor.ts、persistence/gcs.ts）](https://github.com/google-gemini/gemini-cli/blob/main/packages/a2a-server/src/agent/executor.ts)：源码；6.9；一个真实 A2A 服务端在断线、审批、终态上的处理，以及和规范的差异；持久化见同目录 [gcs.ts](https://github.com/google-gemini/gemini-cli/blob/main/packages/a2a-server/src/persistence/gcs.ts)。

**子 agent**

- [Claude Code: Create custom subagents](https://code.claude.com/docs/en/sub-agents)：官方说明；7.1–7.4；子 agent 加载什么、fork 和全新上下文的区别、权限模式继承规则、深度和并发上限、出错时返回什么、输出扫描。信息密度最高的一份。
- [OpenAI Agents SDK: Handoffs](https://openai.github.io/openai-agents-python/handoffs/)：官方说明；7.1；input_filter、嵌套历史、服务端托管对话不能过滤，以及「过滤不等于脱敏」的明确警告。
- [opencode subagent-permissions.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/agent/subagent-permissions.ts)：源码；7.2；30 行代码说明「只继承禁止项、默认禁止递归」。
- [Codex child_config.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/agent/child_config.rs) 与 [config/mod.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/config/mod.rs)：源码；7.2、7.3；子 agent 配置怎么从父 agent 派生、默认深度/线程/超时上限。
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)：分析；7.1、7.3；委派说明的四要素、按复杂度分配子 agent 数量、产出写文件只传引用。
- [深入理解 AI Agent：设计原理与工程实践 第 3、10 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter3.md)：教学；1–5、7、二-21；第 3 章讲用户记忆、混合检索、知识怎么更新；第 10 章（[链接](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter10.md)）讲多 agent 的上下文共享与隔离、六种失败模式、A2A。
- [Why Do Multi-Agent LLM Systems Fail?（论文）](https://arxiv.org/abs/2503.13657)：论文；7、二-21；在 7 个多 agent 框架约 150 条轨迹上做的失败分类（设计缺陷、agent 间对齐失败、缺少完成验证）。

---

## 五、阅读顺序

1. **先定要不要检索**：Anthropic Contextual Retrieval（20 万 token 线、混合检索和重排的收益）→ Elasticsearch RRF。
2. **向量层的坑**：Gemini Embeddings → Voyage Embeddings → Cohere Embed → OpenAI Embeddings。重点看前缀、截断、批量、兼容性。
3. **存储和运维**：pgvector README（过滤、多租户、维度上限）→ Qdrant Multitenancy → Qdrant 迁移教程。
4. **代码检索的转向**：Cursor 语义搜索博客 → Cursor 论坛回复 → Cursor Search 文档 → Cline 博客 → HN 讨论。
5. **记忆**：LangChain Memory overview（框架）→ Anthropic Memory tool（接口和安全）→ SpAIware 两篇（为什么要防）→ Codex memories README 和 types.rs（一个完整实现）。
6. **协议**：A2A and MCP（分工，和 05 对照）→ A2A Life of a Task → A2A 规范第 3、4、13 节 → What's New in v1.0 → gemini-cli a2a-server（实现差距）。
7. **编辑器和服务接口**：ACP Overview → Session Setup → Prompt Turn → Tool Calls → File System → Codex App Server。
8. **子 agent**：Claude Code subagents → OpenAI Handoffs → opencode subagent-permissions.ts → Codex child_config.rs → Anthropic 多 agent 研究系统（配合 03 第 9 节）。
