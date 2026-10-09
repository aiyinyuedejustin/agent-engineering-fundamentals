# 03 · Agent 主循环、上下文拼接与整体架构

> 范围：一个 agent 从"调一次模型"到"能放进生产"之间，工程上必须自己处理的部分。重点放在通用组件和原理上，花哨的功能点不收。
> 资料核对时间：2026-10-09。本章管主循环里的原理：插话、完成判定、指令文件、中途提醒、窗口满了都在这里讲；对应的接口和界面怎么做见 [08 会话、后台任务与前端](08-sessions-jobs-frontend.md)。

---

## 一、知识拆解

### 1. Agent 主循环（loop）

**1.1 最小结构**
本质就是一个 while 循环：把消息历史发给模型 → 看返回里有没有工具调用 → 有就执行、把结果追加进历史、再调一次 → 没有就把文字回复交给用户，结束本轮。Amp 的教程用不到 400 行 Go 写完了，mini-swe-agent 用约 100 行 Python 写完。先手写一遍再用框架，否则框架出问题你看不懂。

**1.2 终止条件不能只靠模型**
"模型不再调工具"是正常出口，但必须另外有硬上限：最大步数、最大 token/费用、总耗时。到上限时要给用户一个明确状态（"做到第 N 步停了，原因是…"），而不是直接抛异常丢掉上下文。OpenAI Agents SDK 的 `max_turns` 超限会抛 `MaxTurnsExceeded`，mini-swe-agent 有 `step_limit` 和 `cost_limit`，都是这个思路。

**1.3 按 stop_reason 分支，而不是按"有没有文字"**
返回的结束原因要逐个处理：正常结束、要调工具、撞到 `max_tokens`（输出被截断，可能连工具参数 JSON 都只写了一半）、服务端工具循环到了上限要你接着发（Anthropic 的 `pause_turn`）、拒答。把 `max_tokens` 截断当正常结束是常见 bug：用户看到半句话，或者工具参数解析失败。

**1.4 一"轮"（turn）和一"步"（step）要分清**
用户发一句话到 agent 回复用户叫一轮，中间可能有几十次"模型调用 + 工具执行"。日志、计费、步数上限、取消、重试都要明确是按轮还是按步算，否则统计和限流都会错。

### 2. 消息历史怎么拼

**2.1 角色和顺序是协议，不是建议**
system（或 developer）放最前；之后 user / assistant 交替；带工具调用的 assistant 消息后面必须紧跟对应的工具结果。Anthropic 要求工具结果放在下一条 user 消息里，而且 `tool_result` 块必须排在 content 数组最前面，任何文字只能放在后面；OpenAI Chat Completions 要求每个 `tool_call_id` 都有一条 `role: tool` 的回复。顺序错了直接 400。

**2.2 tool_call_id 一一配对**
每个工具调用有 id，结果必须带同一个 id 回填。少一个、多一个、重复一个、id 对不上，都会被拒。并行调用时最容易出错：模型一次发 3 个调用，你只回了 2 个（第 3 个超时被你吞了），下次请求就 400。

**2.3 并行工具调用**
模型可以在一条消息里发多个调用。工程上要决定：能不能并发执行（有没有读写冲突）、一个失败了其他怎么办（失败的也要回一个错误结果，不能缺）、结果按什么顺序回填（按调用顺序最稳）。Anthropic 文档还特别提醒：所有并行结果要放在同一条 user 消息里回，分成多条会让模型以后越来越少用并行。

**2.4 原样回传 assistant 消息（含推理块）**
带推理的模型在工具循环中，你回传 assistant 消息时要原样带上它的思考块 / reasoning item（包括加密内容），不能删改，否则会报错或者模型丢失前面推理的连贯性。Anthropic 明说思考块必须完整不改地随工具结果回传；OpenAI Responses 里 reasoning item 也要放回 input。自己"整理"历史、只保留文字，是常见翻车点。

**2.5 两种状态管理方式：自己存全量 vs 服务端存**
Chat Completions 是无状态的，每次都要把全部历史发过去；Responses API 可以用 `previous_response_id` 让服务端串起来。Codex 选择每次发全量、不用服务端状态，原因是要支持零数据保留，并且请求完全无状态更好排查。自己存全量更可控，代价是请求体随对话线性增长。

### 3. 上下文窗口预算

**3.1 窗口包含输入和输出**
上下文上限 = 输入 token + 输出 token（包括推理 token）。所以发请求前要按"历史 + 工具定义 + 预留输出"算预算，不能只算历史。工具定义本身也占 token，几十个工具的 schema 可能就是几千 token。

**3.2 截断要按"消息组"截，不能按条截**
最基本的做法是丢最早的对话，但一个"assistant 工具调用 + 它的所有工具结果"必须当成一组，一起留或一起丢，否则就是 2.2 的配对错误。system 和最初的任务描述一般要钉住不丢。

**3.3 越长越笨（context rot）**
即使没超窗口，内容越长模型越容易漏掉中间的关键信息、被无关内容带偏。Chroma 的实验测了 18 个模型都有这个现象。所以"窗口还够"不等于"可以全塞进去"，预算应该比硬上限紧得多。

**3.4 前缀缓存决定成本和延迟**
主流 API 都只对"完全相同的前缀"命中缓存（Anthropic 的层级是 tools → system → messages，改了哪一层，这层和后面的缓存都失效）。agent 的输入输出比可能到 100:1（Manus 的数据），缓存命中率直接决定钱和首 token 延迟。推论：历史只追加、不改写；工具列表顺序固定；会变的东西放后面。

### 4. 状态与会话持久化

**4.1 历史就是状态**
最简单可靠的做法：把消息列表（加上少量业务状态）原样持久化，恢复时读回来接着跑。12-factor agents 的第 5、6 条讲的就是"执行状态和业务状态统一存、能暂停能恢复"。不要把关键状态只放在内存里的框架对象中。

**4.2 checkpoint 粒度**
按"步"存 checkpoint：每次模型返回、每次工具执行完都落盘。这样进程崩了、机器重启了，能从最后一步恢复，而不是整轮重跑（重跑会重复执行有副作用的工具）。LangGraph 用 `thread_id` + checkpointer 实现的就是这个。

**4.3 跨会话的长任务**
任务长到一个窗口装不下时，靠的不是记忆功能，而是让 agent 在外部留下进度文件、git 提交、任务清单，下个会话先读这些再干活。Anthropic 的长时间 agent 文章给了完整做法。

### 5. 工具定义与描述

**5.1 描述是写给模型看的文档**
名字、描述、参数说明要像给新同事写的 API 文档：做什么、什么时候用、什么时候不用、参数格式举例、返回什么。Anthropic 说详细描述是影响工具使用效果最大的因素。

**5.2 工具粒度按任务设计，不按 API 设计**
不要把后端每个接口一比一包成工具。一个工具对应一件"人会做的事"（比如"查某客户最近订单"而不是"list_all_orders"），能减少调用步数和上下文占用。相近的工具要用前缀分组（命名空间），避免模型选错。

**5.3 返回值要省 token、带下一步线索**
返回人能读懂的字段，不要返回 UUID 堆和整页原始 JSON；支持分页、过滤、截断，并在截断时告诉模型"还有多少、怎么取下一页"。Claude Code 默认把工具返回限制在 25,000 token。

**5.4 工具调用本质是结构化输出**
模型并不"执行"任何东西，它只是输出一段 JSON，执行权在你手里（12-factor 第 4 条）。所以校验参数、鉴权、限流、沙箱都是你的代码的事。也可以不用原生 function calling，像 mini-swe-agent 一样让模型只输出 bash 命令，照样能跑。

### 6. 错误回填

**6.1 工具错误要回给模型，不要直接崩**
工具执行失败时，把简短、可操作的错误信息作为工具结果回填（Anthropic 用 `is_error: true`），让模型自己换参数或换方法。错误信息要说清楚哪里错了、该怎么改，而不是甩一整段堆栈。

**6.2 连续错误要有上限**
同一个错误反复出现时要计数，超过阈值（比如 3 次）就停下来交给人或换策略，否则模型会在错误里死循环烧钱（12-factor 第 9 条）。

**6.3 区分三类错误**
模型 API 错误（限流、超时、5xx，由你的重试层处理，不进上下文）、工具执行错误（回填给模型）、协议错误（400，说明你拼的历史坏了，重试没用，要修数据）。三类混在一起处理是常见问题。

### 7. 基本模式

**7.1 ReAct**
"想一步 → 做一步 → 看结果"交替进行，是今天几乎所有工具调用 agent 的原型。现在的原生 function calling 就是把 ReAct 的格式标准化了。

**7.2 规划（plan-and-execute）**
先让模型出一个完整计划，再逐步执行，必要时重新规划。好处是步骤可见、可审、可以用便宜模型执行；坏处是计划容易过时。很多 agent 把计划做成一个"更新计划"工具，让模型自己维护待办列表（Codex 的 `update_plan`）。

**7.3 反思 / 评审**
让模型（最好是另一个上下文干净的实例）检查结果再改。关键工程点：评审者不要和执行者共享上下文、只给它读权限、给它明确的通过标准，否则它会给自己打高分。

### 8. Workflow 与 agent 的区别

workflow 是代码写死流程、模型只在节点里干活；agent 是模型自己决定下一步做什么。Anthropic 的建议是能用 workflow 就别用 agent：先试单次调用 → 再试固定流程（链式、路由、并行、编排-执行、评估-优化）→ 最后才上自主 agent。agent 带来灵活性，代价是延迟、成本、不可预测。

### 9. 多 agent 编排

**9.1 常见的两种形态**
一种是"经理 + 工人"：主 agent 把子任务当工具调用派给子 agent，收结果汇总；另一种是"交接"（handoff）：把整个对话控制权交给另一个 agent。OpenAI Swarm 的 cookbook 把 handoff 实现为"一个返回新 agent 的工具调用"，很好理解。

**9.2 多 agent 最大的问题是上下文不共享**
子 agent 只拿到一句任务描述，会误解任务、和其他子 agent 做出互相矛盾的决定。Cognition 的结论是：要么共享完整轨迹，要么别拆。Anthropic 的研究系统反过来证明，在"读多写少、能并行搜索"的任务上拆开有效，但 token 消耗大约是普通聊天的 15 倍（单 agent 约 4 倍）。判断标准：子任务是否真的独立、是否以读为主。

### 10. 人工审批中断点

高风险工具（写库、发消息、付款、删除）执行前要暂停，等人批准、拒绝或修改参数后再继续。实现上要求：状态能落盘（第 4 节）、能从中断处恢复、拒绝时也要给那个工具调用回填一个"用户拒绝"的结果（否则又是配对错误）。12-factor 第 7 条主张把"联系人类"本身做成一个工具。

---

### 11. 一个会话同一时刻只能有一个"活动回合"
历史是一条只能追加的链，两个回合同时往里写，必然出现交错的工具调用和结果，下次请求就是 400 或语义错乱。所以每个会话要有一把锁：有回合在跑时，新的请求不能再启动一个新回合。opencode 的 `run-state.ts` 就是按会话 ID 维护一个 runner，忙的时候 `assertNotBusy` 直接报 BusyError。这把锁是后面"用户插话"所有策略的前提。

### 12. 用户在 agent 运行中又发消息
LangGraph 把它叫 double texting，归纳了四种：排队（默认，跑完当前回合再处理）、拒绝、打断（停掉当前回合、保留已做的进度，把新消息接上）、回滚（停掉并丢弃当前回合，像没发生过一样重来）。第五种是"注入"（steer）：不打断，而是在当前回合下一次调模型之前把新消息塞进去。Codex 的主循环就是这么做的：用户运行中发的消息先进 `pending_input` 队列，循环每走一步、在下一次调模型前把队列取出来追加进历史；但"压缩"和"代码审查"这类回合不允许插话（`NonSteerableTurnKind`），因为插进去会破坏它们的输入。OpenAI Responses API 也有了服务端版本（`response.steer`），文档明确说：插话不会撤销已经执行的动作，也不会取消已经开始的工具。

主循环上要注意的点：
- 注入只能放在"步与步之间"，不能插在 assistant 的工具调用和工具结果中间（否则就是 2.1 的顺序错误）。
- 打断要走第二节第 2 条的清理流程，并在历史里留一条"上一回合被用户有意打断，命令可能执行了一半"的说明。Codex 用独立的 `<turn_aborted>` 片段做这件事，下次模型就知道要先检查现场。
- 带"期望回合 ID"做插话请求（Codex 的 `TurnSteerParams.expectedTurnId`），避免用户的插话落到一个已经结束、换成新回合的会话上。
- 一次追加多条排队事件时，模型常常只回应最后一条。给每条加上"[未处理事件 2/4]"这类编号，末尾再写一句"共 4 条，请全部处理"。出处：[李博杰《深入理解 AI Agent》第 6 章「不支持原生异步时的兼容方案」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter6.md)。
- 打断时给还没返回的工具补的占位结果，措辞要写成"还在后台执行，结果未到"，并在真实结果到达后作为新事件追加；否则模型会把"已启动"当成"已完成"，编出还没到的数据。需要异步的工具干脆在名字上体现，比如 `initiate_phone_call` 立刻返回任务 ID，完成时另发事件。出处同上。

### 13. 怎么判断任务真的做完了
"模型不再调工具"只说明模型认为做完了。常见三种更硬的做法：
- **完成工具**：给模型一个 `final_output` / `submit` 工具，只有调了它才算结束，参数就是结构化的最终结果。模型如果直接用文字收尾，循环就追加一句提醒逼它调用。Goose 的 `final_output_tool.rs` 就有这句"You MUST call the final_output tool NOW"。OpenAI Agents SDK 的 `tool_use_behavior`、pydantic-ai 的 Tool Output 模式、Vercel AI SDK 的 `stopWhen: hasToolCall(...)` 都是同一个思路。
- **外部验证**：结束前由代码跑一个检查（测试、lint、接口返回值、文件是否存在），不通过就把失败结果回填，继续循环。Anthropic 把它总结成"收集上下文 → 行动 → 验证 → 重复"。
- **独立评审**：另起一个上下文干净、只读的 agent 判定通过与否（见第 7 节）。Anthropic 的长任务文章发现模型会在没有端到端验证的情况下宣布功能完成，需要显式要求它像真实用户一样测试。
不管哪种，验证失败的次数要有上限，否则就是另一种死循环。

### 14. 指令文件（AGENTS.md / CLAUDE.md 这一类）的分层规则
几乎所有 coding agent 都实现了，但规则各不相同，自己做时要明确定下这几件事：
- **从哪里找**：Codex 先确定项目根（往上找到 `.git` 这类标记为止），然后收集"从项目根到当前目录"沿途每一层的 AGENTS.md，按从根到深的顺序拼接，不越过项目根；每层最多取一个文件，`AGENTS.override.md` 优先于 `AGENTS.md`；全局的放在 `~/.codex`。opencode 只认第一个存在的文件名（AGENTS.md 优先于 CLAUDE.md），但会把这个名字从当前目录到工作区根的每一层都收集起来。
- **深层目录的文件什么时候加载**：启动时只加载从根到当前目录这一条链；子目录里的指令文件等 agent 真的读到那个目录的文件时再按需附加（opencode 的 `instruction.ts` 在读文件时从该文件往上找，同一条消息内只附加一次；Claude Code 文档也写明子目录文件按需加载）。按需加载意味着这段内容是在对话中途追加的，不应该回头改 system。
- **冲突时谁说了算**：通用约定是越近越优先，后拼接的覆盖先拼接的，用户在对话里明确说的最优先（agents.md 规范原文）。实现上就是靠"拼接顺序 + 模型偏向后面的内容"，并不是硬规则。
- **大小上限**：Codex 有总字节预算（默认 32 KiB，超出就截断并打警告）；Claude Code 的自动记忆只加载前 200 行或 25KB。没有上限的话，一个巨大的指令文件能吃掉大半窗口，而且每个会话都付这份钱。
- **它是上下文，不是强制规则**：Claude Code 文档明说指令文件是给模型看的上下文，要硬性阻止某个动作得用 hook。安全策略不能只写在 AGENTS.md 里。
- **放在哪个角色**：Codex 把这些用户指令放成一条 `role=user` 的消息（带标记包起来），而不是并进 system，这样 system 可以保持跨项目不变、缓存友好。

各家的实际规则对照（2026-10-09 核对）：

| | 查找范围 | 合并方式 | 大小控制 |
|---|---|---|---|
| Codex | 全局 `~/.codex` 下取一个；项目内从项目根（默认以 `.git` 为标记）到当前目录，每级先找 `AGENTS.override.md` 再找 `AGENTS.md` 再找自定义备用名，每级最多一个 | 从根到当前目录拼接，越近越靠后 | 合计 `project_doc_max_bytes`，默认 32KiB，超了截断 |
| Claude Code | 当前目录及所有上级目录的 `CLAUDE.md`、`CLAUDE.local.md`；子目录的在模型读写那个子目录里的文件时才加载 | 全部拼接，不互相覆盖；同级里 local 排在后面 | 建议每个文件 200 行以内 |
| opencode | 全局一个；项目内对第一个找到的文件名（AGENTS.md 优先于 CLAUDE.md）向上收集所有层级；子目录的在 read 工具读到该目录文件时附在工具结果里 | 拼接，每段前标"Instructions from: 路径" | 无硬上限 |
| agents.md 规范 | — | "离得最近的那个优先" | — |

同一个仓库在不同 agent 里看到的指令可能不一样，团队要选定一种约定（比如只在根目录放一个，子目录只放局部规则且互不矛盾）。另外两点：
- **仓库里的指令文件是不可信输入**：Claude Code 对指向工作目录外的 `@import` 和符号链接要先弹窗批准；Codex 对自定义备用文件名做了检查，含路径分隔符的名字直接忽略（代码注释说明：在 Windows 上解析网络路径时，哪怕只是查元数据也可能把本机凭证发出去）。
- **压缩之后要重新注入**：Claude Code 在压缩后从磁盘重读根目录的 CLAUDE.md，子目录的等下次访问再加载。

### 15. 中途插入"状态提醒"：放哪、用什么角色、怎么不破坏缓存
agent 跑着跑着，需要告诉模型一些新情况：当前时间、计划/待办状态、文件被外部改了、权限或模式变了（如从规划模式切到执行模式）、预算还剩多少、上一回合被打断。原则：
- **永远追加，不回头改**。改 system 或改旧消息会让从改动点往后的缓存全部失效（见第 3 节）。Anthropic 专门出了"对话中途的 system 消息"功能：在需要的位置追加一条 `role: system`，前面缓存的前缀不受影响，而且这条指令按 system 级别对待，而不是普通用户文字。
- **角色选择**：没有中途 system 消息能力的 API，一般用 developer 角色（OpenAI）或带固定标签包起来的 user 消息。Codex 把每类提醒做成独立"片段"，各有固定的标签（如 `<current_time_reminder>`、`<turn_aborted>`、`<environment_context>`），时间提醒用 developer 角色，打断提示用 user 角色。固定标签的好处是程序能识别、去重、压缩时能保留或丢弃，而模型也能分清"这是系统给的状态"还是"用户说的话"。
- **挂在哪条消息上**：opencode 的做法是把提醒作为"合成文本块"挂到最后一条 user 消息上（`synthetic: true`），既不改旧内容，又不额外多出一条消息破坏 user/assistant 交替。
- **频率**：每一步都插一条时间戳会让历史变长、而且每条都不一样；按需插（状态真的变了才插）或按间隔插。
- **压缩后要重新放回**：压缩会把这些提醒一起摘要掉，压缩后的新历史里要重新插入当前环境、指令文件这类"初始上下文"。Codex 的 `compact.rs` 有专门的规则决定插在哪里（优先放在最后一条真实用户消息之前）。
- **必须能区分"合成的"和"用户真说的"**：界面展示、会话标题生成、压缩摘要、审计、"用户最后说了什么"这些逻辑都要跳过合成消息。Codex 用标签匹配器识别合成的 user 消息，opencode 用 `synthetic` 字段。不区分的话，常见 bug 是会话标题变成了一段系统提醒，或者压缩时把提醒当用户需求保留。
- **状态变化要写进工具结果**：例如 Claude Code 的"Shell cwd was reset"、"命令已转后台，后续命令的 cwd 不变"。模型只能看到你写进上下文的东西。
- **要用的结论提前算好再给，别让模型自己数**：模型从上下文里"查找"很强，"统计"很弱。规定"每个商家最多打 3 次电话"，模型打完 3 次后常常数不清，又打第 4 次；在工具结果里直接写"这是第 3 次呼叫该商家（3/3）"，违规就基本消失，小模型也能稳定遵守。书中把这种在末尾注入的计数、待办、环境摘要叫"状态栏"。两条纪律：状态由代码维护，不要让模型批量统计——实验发现模型几乎无条件相信状态栏写的数字，写错了它也照做；状态栏是对原始记录的有损提炼，只覆盖你预想到的问题，原始记录不能轻易删。出处：[李博杰《深入理解 AI Agent》第 2 章「Agent 状态栏」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter2.md)。
- **状态更新是"每轮替换"还是"一直追加"**：每轮替换（删掉上一条状态再追加新的）只保留一份最新状态，但删除点之后的缓存要重算，通常是一轮的后缀；一直追加（Claude Code 的 `<system-reminder>` 就是只追加、不删改）对缓存完全友好，但旧状态会堆积，模型要自己认"最新一条"。状态小、两次更新之间新增内容多、会话不长时选追加；状态大、更新频繁、会话很长时选替换。出处同上。

### 16. 窗口满了怎么办：原理和代价
窗口满了必须有一个策略，否则长任务一定在某一步直接报错。几个通用原理：
- **触发阈值要预留输出空间**：判断"满了"要用"已用 token + 预留输出"对比上限，而不是等报错。opencode 的 `overflow.ts` 预留 min(20000, 模型最大输出)；OpenAI 的服务端压缩用 `compact_threshold` 设定阈值。token 计数本身只是估计（Anthropic 计数接口文档明说），阈值要留余量。
- **几种做法的本质区别**：丢最老的消息组（便宜，丢信息）；把旧的工具结果清空只留占位（Anthropic 的 context editing，信息丢得最少，因为工具结果通常可以重新获取）；让模型写摘要替换旧历史（Codex、Anthropic compaction、OpenAI compaction）；结束本会话、靠外部进度文件开新会话（见第 4 节）。
- **摘要会丢什么**：摘要是不可逆的有损压缩，最容易丢的是具体的报错原文、文件路径、用户的原话要求。Codex 的做法是摘要之外，再原样保留最近的用户消息（上限约 2 万 token），因为用户原话是最不能被改写的东西。Manus 的思路是"能重新取回的才压缩"：网页内容可以丢，但要留 URL。
- **压缩本身会失败**：压缩也是一次模型调用，会超时、会撞上同样的窗口上限（要压缩的内容本身就太长）、会被用户打断。Codex 专门有 `compact_model_fallback.rs`：换过模型的会话用旧模型压缩失败，就换当前模型重试一次，并打点统计。要想清楚压缩失败时是退回到截断、还是直接把错误交给用户。还要给压缩加"连续失败就停"的熔断：据 [李博杰《深入理解 AI Agent》第 5 章「故障与错误恢复」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md) 对 Claude Code 的分析，生产数据里有大量会话困在反复压缩失败的循环里烧钱，阈值（连续 3 次）是按真实会话统计定的。
- **压缩后缓存全部失效**：历史被整体替换，前缀变了，下一次请求是全价、首 token 慢。所以压缩不能太频繁，阈值不能贴着当前长度设。
- **替换文本一旦生成就冻结**：大工具输出被换成预览后，把替换后的字符串存下来，会话重启后用完全相同的字符串，否则恢复出来的历史和缓存对不上。出处：[李博杰《深入理解 AI Agent》第 2 章「缓存作为架构约束」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter2.md)。
- **能隔离就别等压缩**：会产生大量中间内容的活（大范围搜代码、读一堆网页）交给子 agent，在它自己的上下文里做完，只回传几百 token 的结论。压缩是事后有损补救，隔离让噪声根本不进主上下文；代价是子 agent 的任务描述必须自包含。出处：[李博杰《深入理解 AI Agent》第 2 章「隔离优于压缩」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter2.md)。
- **对外是一个事件**：压缩应该在历史里留一个明确的边界（Claude Agent SDK 会发 `compact_boundary` 事件），这样持久化、回放、调试的时候知道这里发生过替换。

---

## 二、文章很少讲但常碰到的事

**1. 中断后历史里有"孤儿工具调用"，下一次请求直接 400**
进程被杀、用户按了取消、工具超时被你丢弃、审批被拒，都会在持久化的历史里留下"assistant 发了 tool_calls，但后面没有对应结果"。恢复会话时，OpenAI 兼容接口会报 `An assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'`。做法：每次发请求前跑一遍历史修复，给缺结果的调用补一条"执行被中断，结果不可用"的占位结果（并行调用只补缺的那几个）；同时删掉前面没有对应调用的孤立工具结果。出处：[Kimi CLI 修复 PR #2383](https://github.com/MoonshotAI/kimi-cli/pull/2383)、[deepagentsjs issue #150](https://github.com/langchain-ai/deepagentsjs/issues/150)（并行调用里拒绝审批后的同类 bug）、[LangChain 的 INVALID_TOOL_RESULTS 说明](https://docs.langchain.com/oss/python/langchain/errors/INVALID_TOOL_RESULTS)。

**2. 用户中途打断与取消**
取消要分层：取消正在流式输出的模型请求、杀掉正在跑的工具子进程、然后按第二节第 1 条把历史补齐成合法状态，再接用户的新消息。已经产生副作用的工具（写了一半文件）要在结果里如实写"已中断，可能部分执行"，让模型下次先检查现场。只断开 HTTP、不清理历史，下一轮必报错。

**3. 工具输出过大**
一次 `cat` 大文件、一次返回几万行日志，就能吃掉大半窗口，还会拖垮后面所有请求的缓存和延迟。工具层要有统一的输出上限（按 token 或字节），截断时保留头尾、在中间写明"省略了 N 行，可用某参数分页查看"。出处：Anthropic 工具写作文章（Claude Code 默认 25,000 token 上限，并建议截断时引导模型用更精确的查询）。

**4. 流式工具参数是一块块拼起来的**
流式模式下工具参数以 JSON 片段到达，要自己累积；遇到 `max_tokens` 截断时参数可能是半个 JSON。解析一定要包 try，失败时回填错误让模型重发，而不是让整个 agent 崩掉。出处：[Anthropic fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming)。

**5. 死循环检测**
模型会反复用同样参数调同一个工具，或者反复输出同一段话。光靠最大步数太晚（已经烧了钱），要主动检测：对"工具名 + 参数"做哈希，连续重复超过阈值就打断；对输出文本分块检测重复。Gemini CLI 的实现：连续 5 次相同工具调用、或同一内容块重复 10 次判为循环，低置信时再请一个模型二次判断。出处：[Gemini CLI loopDetectionService.ts](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/services/loopDetectionService.ts)。

**6. 时间和环境信息要注入，而且注入位置会影响缓存**
模型不知道今天几号、在哪个目录、什么系统、什么时区，你不告诉它，它就按训练数据瞎猜（比如搜"最新文档"带去年的年份）。Codex 在对话开头放一条 `<environment_context>` 消息写明工作目录和 shell，环境变化时追加一条新消息而不是改旧的。如果把"当前时间精确到秒"写进 system prompt，每次请求前缀都变，缓存全部失效。出处：OpenAI《Unrolling the Codex agent loop》、Manus 文章（明确提醒不要在 system prompt 开头放时间戳）。

**7. 改 system prompt / 工具列表 = 缓存全废**
缓存只认完全相同的前缀。会话中途改 system、增删工具、甚至只是工具列表顺序不稳定（比如从 MCP 拿到的工具顺序每次不一样），都会导致整段缓存失效，成本和延迟成倍上升。Codex 就踩过 MCP 工具顺序不固定导致缓存未命中的 bug。做法：工具列表排序固定；要动态限制可用工具时，用"屏蔽"而不是"删除"（Manus 的做法是在解码层屏蔽，而不是从定义里删）；配置变化用追加消息表达。出处：Codex 文章、Anthropic 缓存文档的失效表、Manus 文章。

**8. 不要把错误痕迹从历史里删掉**
直觉上会想"把失败的尝试清掉让上下文干净"，但这样模型看不到自己犯过的错，会重复犯。Manus 的经验是保留错误和失败的工具结果，让模型据此调整。和 3.2 的截断不矛盾：截断是在预算压力下丢最老的，而不是专门删失败的。

**9. 重试和副作用**
模型调用重试是安全的，工具执行的重试不一定（发邮件、扣款重试两次就是两份）。恢复会话时（第 4 节）要先确认上次执行到哪了。幂等键、执行日志怎么做见 [02](02-reliability.md) 第 6 节和决定 9。

**10. 不可信内容进入上下文**
网页、邮件、文件内容通过工具结果进入上下文后，模型可能把里面的文字当成指令执行。agent 同时具备"私密数据 + 不可信内容 + 对外发送能力"三样时就有外泄风险，要么砍掉一样，要么在高风险动作前加人工审批（第 10 节）。原理和防法见 [04](04-eval-observability-security.md) 的安全部分。

**11. 指令文件是用户消息，不是 system prompt，也不是安全控制**
写在 AGENTS.md 里的"禁止 push"只是建议。Claude Code 文档明说 CLAUDE.md 作为 system prompt 之后的一条用户消息送入，"不保证严格遵守"；Codex 也把 AGENTS.md 作为 user 角色的片段。要硬拦得靠权限和沙箱（[06](06-tools-sandbox.md) 第 7、9 节）。

**12. 合成的提醒消息必须打标记**
否则会话标题、压缩摘要、审计、"用户最后说了什么"都会被污染。出处：Codex `contextual_user_message.rs`、opencode `session/reminders.ts`（`synthetic: true`）。

**13. 错误处理路径自己也会调模型，可能形成连环故障**
真实发生过的链条：上下文溢出导致 agent 停止 → 触发"结束时自动提交"的钩子 → 钩子调模型写提交说明 → 再次溢出 → 再次触发钩子。错误路径上要禁用一切会再调模型的副作用；辅助性的后台调用（生成标题、输入建议）失败就放弃，不要重试去挤占主链路的额度。出处：[李博杰《深入理解 AI Agent》第 5 章「故障与错误恢复」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md)。

**14. system prompt 里每多一个运行时条件，缓存变体就翻倍**
操作系统、当前模式、用户偏好这类开关如果写在缓存边界之前，N 个二值条件就会产生 2^N 种前缀，缓存命中率被稀释。做法：把 system prompt 切成"全局不变"和"会话相关"两段，所有动态内容放在后段或追加消息里。派生子 agent 时如果想复用父 agent 的缓存，子 agent 的提示词、工具、模型配置、消息前缀要和父 agent 逐字节一致。出处：[李博杰《深入理解 AI Agent》第 2 章「缓存作为架构约束」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter2.md)。

---

## 三、要拿的主意

每条按「要定什么 → 选项 → 代价 → 怎么选」写。

### 决定 1：用框架还是自己写循环
- 选项：自己写（几百行）；用轻量 SDK（OpenAI Agents SDK、pydantic-ai、Vercel AI SDK、Claude Agent SDK）；用编排框架（LangGraph）。
- 代价：自己写要自己做持久化、中断恢复、流式、重试、可观测性，但每一个 token 进了哪里都清楚，换模型厂商也自由。SDK 省掉样板代码，但上下文怎么拼、截断怎么做、错误怎么回填被它决定了，出问题时你要读它的源码；SDK 版本升级也会改变行为。LangGraph 一类的价值主要在持久化、checkpoint、人工中断、多分支编排，单纯的工具循环用它是杀鸡用牛刀。
- 怎么选：先手写一遍最小循环（哪怕最后不用）。如果核心竞争力就是 agent 本身（比如 coding agent），自己写主循环，像 Codex、opencode 都是自研；如果 agent 只是产品里的一个功能、需要快速上线，用 SDK，但要确认它允许你接管上下文拼接（12-factor 第 3、8 条的意思）；需要长时间运行、等人审批、可恢复的流程，再考虑 LangGraph 这类带持久化的框架。不管用什么，确保能拿到每次实际发给模型的完整请求。

### 决定 2：会话状态放服务端还是客户端
- 选项：每次自己发全量历史（Chat Completions、Responses `store:false`）；用厂商的服务端状态（`previous_response_id`、Conversations）；用框架的 session 存储（Agents SDK sessions、LangGraph checkpointer）。
- 代价：自己发全量，请求体随对话增长，但完全无状态、可以随便换模型、改历史、做零数据保留，排查时请求即全部真相。服务端状态省带宽、写起来简单，但被绑在一个厂商上，历史不能随意修剪（OpenAI 文档提示用了链式 ID 就不要自己手动剪），数据保留也要另外审。
- 怎么选：生产系统默认"自己存全量、自己发"，Codex 就是这么选的，理由是无状态和零数据保留。只有在原型阶段或确定不会换厂商、不需要改写历史时才用服务端状态。真正贵的是模型推理而不是网络传输，靠前缀缓存把成本降下来，而不是靠少发数据。

### 决定 3：单 agent 加工具，还是多 agent
- 选项：一个 agent + 多工具；主 agent 把子 agent 当工具调用（经理-工人）；agent 之间交接控制权（handoff）。
- 代价：多 agent 的 token 成本高得多（Anthropic 数据：单 agent 约为聊天的 4 倍，多 agent 约 15 倍），子 agent 之间看不到彼此的上下文，容易做出互相矛盾的决定；好处是能并行、每个子 agent 的上下文干净。
- 怎么选：默认单 agent。只有当子任务真的互相独立、以读为主（并行搜索、并行调研）、或者单个上下文装不下时才拆。判断多一个 agent 值不值，看它有没有带来新信息：同一模型重读自己的输出、几个 agent 辩论同一段文字，基本不比单 agent 强；审查者拿着测试结果、渲染截图、外部工具查证去审，才明显有用（[李博杰《深入理解 AI Agent》第 10 章「多 Agent 何时真正优于单 Agent」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter10.md)）。同一模型生成的多个审查意见也不能当成独立意见：Anthropic 的实验里 30 个同时上线的 agent 有 18 个建了同名 git 分支。要写东西的任务（改代码、写报告）尽量由一个 agent 串行完成。拆的时候子 agent 用经理-工人模式（结果回到主 agent），比交接控制权更好控。

### 决定 4：工具结果全量放进上下文，还是存外部只放引用
- 选项：全量放入；截断后放入（头尾 + 省略提示）；存到文件/存储里，上下文只放路径、ID、摘要，需要时再读。
- 代价：全量放最简单、模型信息最全，但一次大输出就能吃掉窗口，拖慢后面每一步。只放引用最省上下文，但模型要多一次读取调用，而且需要一个能读回来的工具和存储。
- 怎么选：设一个统一上限（比如几千到两万 token），小于上限全量放，超过就截断并告诉模型怎么取剩余部分。大文件、网页、日志这种"可以重新取回"的内容优先存外部放引用（Manus 的"文件系统就是上下文"、Anthropic 的"just in time"取用）。不可重现的结果（一次性的 API 返回、付费查询）要么全量存外部，要么至少保证能找回来。

### 决定 5：并行工具调用开还是关
- 选项：开（各家默认）；关（OpenAI `parallel_tool_calls: false`；Anthropic 在 `tool_choice` 里设 `disable_parallel_tool_use: true`）；开但执行端串行。
- 代价：开着能减少来回次数、降延迟，但要处理部分失败、结果配对、读写冲突，取消和中断时出错面更大。关掉逻辑最简单，但慢，而且模型一步只做一件事。
- 怎么选：只读工具多（搜索、读文件、查询）的 agent 开着，执行层只读工具并发、写操作串行。工具大多有副作用、需要逐个审批、或者你的回填逻辑还不稳时先关。注意"模型发了并行调用"和"你并行执行"是两回事，可以接受并行调用但按顺序执行。每个工具在定义里声明自己能否并发（默认不能），一个调用失败时只取消同批里依赖它的调用，不波及独立的调用。

### 决定 6：终止条件怎么定
- 选项：模型不再调工具就停；硬上限（步数、token、费用、时间）；完成工具（必须调 `final_output`）；外部验证通过才算完成。
- 代价：只靠模型自己停，会出现提前收工和停不下来两种问题。硬上限必须有，但它是保险丝，触发时任务通常是失败的。完成工具让结束变得明确、结果结构化，但模型偶尔会不调，需要追加提醒。外部验证最可靠，但要为每类任务写检查逻辑。
- 怎么选：所有 agent 都要有硬上限（步数 + 费用至少两项，Claude Agent SDK 就提供 `max_turns` 和 `max_budget_usd`，子 agent 的花费也计入）。对话类 agent 用"不再调工具"作为正常出口；批处理、无人值守的任务用完成工具 + 外部验证。连续出错、死循环检测也算终止条件（见第 6 节、第二节第 5 条）。上限触发时要给出明确的失败状态，不要伪装成正常回复。

### 决定 7：原生 function calling，还是让模型输出文本/代码当动作
- 选项：原生工具调用（JSON 参数）；只给一个 bash（mini-swe-agent）；让模型写代码当动作（smolagents 的 code agent）。
- 代价：原生调用结构最清晰，易校验、易做权限，但每个能力都要定义成工具，工具多了占上下文。只给 bash 或写代码非常灵活、对任何模型都能用，但权限控制只能靠沙箱，解析失败要自己处理。
- 怎么选：面向外部用户、需要细粒度权限和审批的，用原生工具调用；在隔离沙箱里跑的研究型、编码型 agent，可以考虑 bash 或代码动作。

### 决定 8：用户运行中插话怎么处理
- 选项：排队、拒绝、打断、回滚、注入（见第 12 节）。
- 代价：排队最简单但用户要等，而且 agent 可能继续执行用户已经不想要的操作；打断响应快，但要清理现场、补齐孤儿调用；注入体验最好，但要保证只在步与步之间插入，并且有些回合（压缩、审查）不能插。
- 怎么选：最低限度要有"排队 + 打断"两个选项给用户。有长时间运行任务、用户经常补充要求的产品（coding agent）再做注入。后台批处理接口一般用拒绝或排队。

### 决定 9：窗口满了用哪种策略
- 选项：丢最老的消息组；清理旧工具结果；摘要压缩（自写或用厂商的服务端压缩）；开新会话 + 外部进度文件。
- 代价：见第 16 节。丢消息和清工具结果便宜但会丢信息；摘要保留语义但有损、会失败、会让缓存失效；开新会话最干净，但要求任务能拆成多个阶段并有外部记录。
- 怎么选：先尽量不让窗口满（工具输出上限、引用代替全文）。然后优先清理旧工具结果，其次摘要压缩（压缩时保留用户原话和最近几步），超长任务从一开始就按"多会话 + 进度文件"设计。用厂商的服务端压缩省代码，但输出的压缩项是不透明的（OpenAI 的是加密内容），换厂商就用不了。

### 决定 10：最终结果的形式：自由文本还是结构化
- 选项：自由文本；结构化输出（JSON schema / 原生结构化输出）；完成工具携带结构化参数。
- 代价：自由文本给人看最好，但下游程序很难用。原生结构化输出部分模型不支持，或者与工具调用同时用时有限制（Goose 对不支持的厂商会给出专门提示）。完成工具兼容性最好，但需要处理模型不调用的情况。
- 怎么选：给人看的对话 agent 用自由文本；被程序调用的 agent（作为子 agent、批处理）用完成工具或结构化输出，并对结果做 schema 校验，校验失败作为错误回填让模型重来。

### 决定 11：循环跑在哪里
- 选项：用户本机（CLI / IDE 插件）；自己的服务端；厂商托管的 agent 服务。
- 代价：本机能直接碰用户的文件和环境，延迟低、不用管多租户，但关掉终端任务就停，长任务和多端同步做不了。服务端能长时间跑、能断线重连、能多端看进度，但要处理会话锁（第 11 节）、事件流、恢复、多租户隔离，工具执行还要远程沙箱。托管服务最省事，但控制权最少。
- 怎么选：交互式开发工具放本机；长时间、无人值守、需要从多个端查看的任务放服务端。无论哪种，把"循环"和"界面"之间做成事件接口（提交、事件流、审批回调、取消），以后挪地方不用重写循环。

### 决定 12：指令文件和中途提醒怎么组织
- 选项：指令文件：只读根目录一个；从根到当前目录全部拼接；启动时加载上级目录、子目录的在访问时按需加载。中途提醒：改 system prompt；追加独立消息；附在最近的用户消息上。
- 代价：只读一个，大仓库里局部规则无处放；全部拼接，不相关的规则占预算、层级之间可能互相矛盾；按需加载实现复杂，压缩后要重新注入。改 system prompt 会让缓存全部失效。
- 怎么选：按需加载，并设合计大小上限（超了截断时告诉用户）；兼容 AGENTS.md 作为通用文件名；指向仓库外的导入和符号链接要先批准。中途提醒一律追加，用固定的标签和角色，打上"合成"标记，同类提醒只在状态变化时发一次。

---

## 四、资料清单

- [Building Effective AI Agents（Anthropic）](https://www.anthropic.com/engineering/building-effective-agents)：说明/分析；覆盖 1、7、8、9；业界最常被引用的入门框架，workflow 和 agent 的分界讲得最清楚，几种基本编排模式都有图。
- [12-factor-agents（HumanLayer）](https://github.com/humanlayer/12-factor-agents)：分析；覆盖 2、3、4、5、6、10；从生产经验总结的 12 条原则，"自己掌控上下文、控制流、暂停恢复、错误压缩"都是硬核工程点；第 3 条（Own your context window）附了具体的上下文拼接示例。
- [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction)：教学；覆盖 1、5、7；免费系统课程，Unit 1 的"思考-行动-观察"循环和工具章节适合打基础。
- [LLM Powered Autonomous Agents（Lilian Weng）](https://lilianweng.github.io/posts/2023-06-23-agent/)：分析/综述；覆盖 7；规划、记忆、工具使用三大块的经典综述，适合建立概念地图。
- [Agents（Chip Huyen）](https://huyenchip.com/2025/01/07/agents.html)：分析；覆盖 5、7；规划、反思、工具选择讲得系统，最后一节专门讲 agent 的失败模式和评估。
- [A practical guide to building agents（OpenAI，PDF）](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)：说明；覆盖 1、8、9、10；官方给工程团队的指南，单 agent 与多 agent 编排、护栏、人工介入的取舍。
- [Unrolling the Codex agent loop（OpenAI）](https://openai.com/index/unrolling-the-codex-agent-loop/)：分析；覆盖 1、2、3.4、二-6、二-7；一个生产级 agent 的主循环逐字段拆解，prompt 怎么拼、为什么不用服务端状态、什么操作会让缓存失效，隐含知识密度最高的一篇。
- [Tool use with Claude（Anthropic 文档）](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)：说明；覆盖 1、2、5；Claude 工具调用的整体流程和客户端/服务端工具区别。
- [Define tools（Anthropic 文档）](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)：说明；覆盖 5.1；怎么写工具描述，好坏描述对照示例。
- [Parallel tool use（Anthropic 文档）](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use)：说明；覆盖 2.3；并行调用的回填格式和常见错误（结果拆成多条消息的后果）。
- [Writing effective tools for AI agents（Anthropic）](https://www.anthropic.com/engineering/writing-tools-for-agents)：分析；覆盖 5、二-3；工具粒度、命名空间、返回值省 token、截断与错误提示，含 25k token 上限的实际数字。
- [Effective context engineering for AI agents（Anthropic）](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)：分析；覆盖 3；从"注意力是有限预算"出发讲 system prompt、工具、示例、历史该放什么。
- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)：分析；覆盖 3.4、二-6、二-7、二-8；KV 缓存命中率为什么是第一指标、工具"屏蔽不删除"、保留错误痕迹，都是一线经验。
- [Context Rot（Chroma）](https://www.trychroma.com/research/context-rot)：分析/实验；覆盖 3.3；用实验证明输入越长效果越差，给"预算要比窗口紧"提供依据。
- [How to Build an Agent（Thorsten Ball / Amp）](https://ampcode.com/notes/how-to-build-an-agent)：教学；覆盖 1、2、5；不到 400 行 Go 从零写出能改代码的 agent，看完就明白"agent 就是循环 + 工具"。
- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)：源码；覆盖 1.2、5.4；约 100 行的主循环，只用 bash、历史线性追加、步数和费用上限，最适合精读的最小实现。
- [mini-swe-agent 主循环 default.py](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/agents/default.py)：源码；覆盖 1、6；直接看循环、终止条件和异常怎么转成给模型的消息。
- [Orchestrating Agents: Routines and Handoffs（OpenAI Cookbook）](https://developers.openai.com/cookbook/examples/orchestrating_agents)：教学；覆盖 9.1；用很少的代码讲清楚 handoff 就是"返回另一个 agent 的工具调用"（Swarm 的设计来源；页面已标记归档，但原理不过时）。
- [Running agents（OpenAI Agents SDK）](https://openai.github.io/openai-agents-python/running_agents/)：说明；覆盖 1.2、1.4、4；SDK 的 agent loop 定义、`max_turns`、会话管理，适合对照自己的实现。
- [openai-agents-python run.py](https://github.com/openai/openai-agents-python/blob/main/src/agents/run.py)：源码；覆盖 1、9；生产级 runner 的完整实现，看工具执行、handoff、护栏如何插入循环。
- [Workflows and agents（LangGraph 文档）](https://docs.langchain.com/oss/python/langgraph/workflows-agents)：教学；覆盖 7、8；把 Anthropic 的几种 workflow 模式逐个写成可运行代码。
- [Interrupts（LangGraph 文档）](https://docs.langchain.com/oss/python/langgraph/interrupts)：说明；覆盖 10；人工审批中断点的实现方式：checkpoint + thread_id + resume。
- [Persistence（LangGraph 文档）](https://docs.langchain.com/oss/python/langgraph/persistence)：说明；覆盖 4.2；checkpoint 的粒度、恢复、常见问题（checkpoint 无限增长等）。
- [Effective harnesses for long-running agents（Anthropic）](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)：分析；覆盖 4.3、7.3；跨多个上下文窗口的长任务怎么靠进度文件和 git 接力。
- [How we built our multi-agent research system（Anthropic）](https://www.anthropic.com/engineering/multi-agent-research-system)：分析；覆盖 9；多 agent 什么时候值得、token 消耗约为普通聊天的 15 倍、子 agent 任务描述怎么写、状态和错误如何处理。
- [Don't Build Multi-Agents（Cognition）](https://cognition.com/blog/dont-build-multi-agents)：分析；覆盖 9.2；多 agent 的反面论证，"共享完整轨迹"原则，和上一条对照读。
- [ReAct（论文）](https://arxiv.org/abs/2210.03629)：分析/论文；覆盖 7.1；今天工具调用循环的原型，读摘要和示例轨迹即可。
- [Gemini CLI loopDetectionService.ts](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/services/loopDetectionService.ts)：源码；覆盖 二-5；生产级死循环检测：工具调用重复、内容重复、低置信时让模型二次判断，阈值都在代码里。

- [How the agent loop works（Claude Agent SDK 文档）](https://code.claude.com/docs/en/agent-sdk/agent-loop)：说明；覆盖 1、3、16、决定 6；一个生产级循环的官方说明：轮次、并行工具执行、`max_turns`/`max_budget_usd`（子 agent 花费计入）、自动压缩和 `compact_boundary` 事件。
- [Building agents with the Claude Agent SDK（Anthropic）](https://claude.com/resources/articles/building-agents-with-the-claude-agent-sdk)：分析；覆盖 13；"收集上下文 → 行动 → 验证 → 重复"的循环设计，验证这一步怎么做（规则、视觉、LLM 评审）。
- [Harness design for long-running application development（Anthropic）](https://www.anthropic.com/engineering/harness-design-long-running-apps)：分析；覆盖 7.3、13；生成者与评审者分离的长任务设计，讲为什么执行者不该给自己打分。
- [Designing agentic loops（Simon Willison）](https://simonwillison.net/2025/Sep/30/designing-agentic-loops/)：分析；覆盖 1、决定 11；从"给 agent 定一个清晰目标和可验证的终点、在哪里放开权限"的角度讲循环设计，包括沙箱和放权的取舍。
- [Mid-turn steering（OpenAI 文档）](https://developers.openai.com/api/docs/guides/steering)：说明；覆盖 12、决定 8；服务端"运行中插话"的语义：只是排队、不撤销已执行动作、不取消已开始的工具、被插话的响应以 `steered` 结束。
- [Double texting（LangSmith Agent Server 文档）](https://docs.langchain.com/langsmith/double-texting)：说明；覆盖 12、决定 8；用户运行中再发消息的四种策略（排队、拒绝、打断、回滚）定义清楚，可直接当设计清单。
- [Mid-conversation system messages and tool changes（Anthropic 文档）](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)：说明；覆盖 15、二-7；为什么改顶层 system 会废掉缓存，以及在对话中途追加 system 消息、改工具而不破坏前缀缓存。
- [Compaction（OpenAI 文档）](https://developers.openai.com/api/docs/guides/compaction)：说明；覆盖 16、决定 9；服务端压缩的触发阈值 `compact_threshold`、压缩项不透明、和链式 ID 一起用时不要手动修剪。
- [Compaction overview（Anthropic 文档）](https://platform.claude.com/docs/en/build-with-claude/compaction)：说明；覆盖 16、决定 9；按需压缩、按阈值压缩、自写摘要器三种方式的对比。
- [Context editing（Anthropic 文档）](https://platform.claude.com/docs/en/build-with-claude/context-editing)：说明；覆盖 16、决定 4；按规则清掉旧工具结果和旧思考块，是"不摘要也能腾空间"的做法。
- [Manage tool context（Anthropic 文档）](https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context)：说明；覆盖 5、决定 4；工具多、工具结果大时的四种手段（工具搜索、程序化调用、缓存、上下文编辑）各解决什么问题。
- [Custom instructions with AGENTS.md（Codex 文档）](https://learn.chatgpt.com/docs/agent-configuration/agents-md)：说明；覆盖 14；指令文件查找顺序、每层只取一个、override 优先、从根往下拼接、大小上限，规则写得最完整的一份。
- [AGENTS.md 规范](https://agents.md/)：说明；覆盖 14；跨工具的指令文件约定：嵌套文件、最近的优先、用户对话里说的覆盖一切。
- [How Claude remembers your project（Claude Code 文档）](https://code.claude.com/docs/en/memory)：说明；覆盖 14；CLAUDE.md 的分层加载（上层启动加载、子目录按需加载）、大小上限，以及"这是上下文不是强制配置，硬限制要用 hook"。
- [Agents（OpenAI Agents SDK 文档）](https://openai.github.io/openai-agents-python/agents/)：说明；覆盖 13、决定 6、决定 10；`output_type`、`tool_use_behavior`（工具结果是回给模型还是直接结束）、`reset_tool_choice` 防工具循环。
- [Sessions（OpenAI Agents SDK 文档）](https://openai.github.io/openai-agents-python/sessions/)：说明；覆盖 4、决定 2；框架层的会话存储：中断后用同一会话恢复、历史与新输入怎么合并、限制取回的历史条数。
- [Output（pydantic-ai 文档）](https://pydantic.dev/docs/ai/core-concepts/output/)：说明；覆盖 13、决定 10；结构化结果的三种实现方式（工具输出、原生结构化输出、提示词约束）和各自限制，输出校验失败怎么让模型重试。
- [Agents（pydantic-ai 文档）](https://pydantic.dev/docs/ai/core-concepts/agent/)：说明；覆盖 决定 6；`UsageLimits` 对 token、请求数、工具调用数、费用设上限的具体接口。
- [Loop Control（Vercel AI SDK 文档）](https://ai-sdk.dev/docs/agents/loop-control)：说明；覆盖 决定 6；`stopWhen` 组合停止条件（步数、某个工具被调用），`prepareStep` 在每步之间改模型、工具、消息。
- [How to think about agent frameworks（LangChain）](https://www.langchain.com/blog/how-to-think-about-agent-frameworks)：分析；覆盖 8、决定 1；"编排框架"和"agent 抽象"的区别，框架真正该提供什么（持久化、中断、可观测性）。
- [Context Engineering for Agents（LangChain）](https://www.langchain.com/blog/context-engineering-for-agents)：分析；覆盖 3、决定 4；写入、选取、压缩、隔离四类上下文策略的分类法，对照多个真实 agent。
- [Plan-and-Execute Agents（LangChain）](https://www.langchain.com/blog/planning-agents)：教学；覆盖 7.2；先规划再执行的几种实现（Plan-and-Execute、ReWOO、LLMCompiler）及各自省了什么。
- [Lost in the Middle（论文）](https://arxiv.org/abs/2307.03172)：分析/论文；覆盖 3.3、14；长上下文中间的信息最容易被忽略，是"关键指令放开头或结尾、靠近使用位置"的依据。
- [smolagents](https://github.com/huggingface/smolagents)：源码；覆盖 决定 7；"让模型写代码当动作"的代表实现，和原生 JSON 工具调用对照看。
- [Codex core/src/session/turn.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/session/turn.rs)：源码；覆盖 1、12；生产级主循环：每步前取出用户插话队列、什么时候需要再调一次模型、压缩后如何继续。
- [Codex core/src/agents_md.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs)：源码；覆盖 14；项目根判定、从根到当前目录收集指令文件、字节预算截断的实现，文件头注释就是规则说明。
- [Codex core/src/compact.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/compact.rs)：源码；覆盖 16；压缩后新历史怎么组成：摘要 + 最近用户原话（约 2 万 token 上限）+ 重新插入的初始上下文及插入位置规则。
- [Codex core/src/compact_model_fallback.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/compact_model_fallback.rs)：源码；覆盖 16；压缩失败后什么情况下换模型重试、什么情况下不重试（被打断、超预算）。
- [Codex core/src/context/turn_aborted.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/context/turn_aborted.rs)：源码；覆盖 二-2、12；打断后回填给模型的那段说明原文，和它用的角色与标签。
- [Codex core/src/context/current_time_reminder.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/context/current_time_reminder.rs)：源码；覆盖 二-6、15；时间提醒作为独立 developer 片段追加，而不是写进 system。
- [opencode session/run-state.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/run-state.ts)：源码；覆盖 11；每个会话一个 runner、忙时拒绝、取消的实现。
- [opencode session/instruction.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/instruction.ts)：源码；覆盖 14；全局与项目指令文件查找、读文件时就近按需附加子目录指令且每条消息只附加一次。
- [opencode session/reminders.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/reminders.ts)：源码；覆盖 15；模式切换提醒作为合成文本块挂到最后一条用户消息上。
- [opencode session/overflow.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/overflow.ts)：源码；覆盖 16；30 多行的"窗口是否快满"判断：可用输入 = 上限 − 预留输出，含缓存读写 token。
- [Goose agents/final_output_tool.rs](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/final_output_tool.rs)：源码；覆盖 13、决定 10；完成工具的实现，模型不调用时追加的催促语，以及并行调用中还有未回答兄弟调用时的处理。
- [Kimi CLI PR #2383：修复孤儿工具调用](https://github.com/MoonshotAI/kimi-cli/pull/2383)：源码；覆盖 二-1；会话被杀后恢复时补占位工具结果的真实修复，含测试用例清单，可以照抄思路。
- [LLM Agents MOOC（UC Berkeley）](https://llmagents-learning.org/f24)：教学；覆盖 7；ReAct 作者等一线研究者的系列课程，适合补理论背景。
- [深入理解 AI Agent：设计原理与工程实践（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter2.md)：教学/分析；覆盖 3、15、16、二-14；开源中文书，第 2 章「KV Cache 友好的上下文设计」「Agent 状态栏」「上下文压缩策略」讲缓存约束、状态注入和分层压缩，带对照实验；第 5 章「故障与错误恢复」（[链接](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md)）讲四层故障和熔断；第 6 章「异步与事件驱动」（[链接](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter6.md)）讲运行中插话的兼容做法；第 10 章（[链接](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter10.md)）讲多 agent 何时值得。体系完整，部分模型和产品细节以原文为准。
- [Patterns and problems in multiagent systems（Anthropic）](https://www.anthropic.com/research/multiagent-systems)：分析/实验；覆盖 9、决定 3；多 agent 同质趋同（30 个 agent 里 18 个建同名分支）、互相拆台、协调后效果大增但成本也大增的一手数据。
- [AI Agents for Beginners（Microsoft）](https://github.com/microsoft/ai-agents-for-beginners)：教学；覆盖 7、9、10；18 课的开源课程，含设计模式、规划、多 agent、人工介入，配代码。

---

## 五、阅读顺序

1. 先建立整体概念：Anthropic《Building Effective AI Agents》→ Lilian Weng 综述（快速翻）。
2. 动手写一遍：Amp《How to Build an Agent》→ 精读 mini-swe-agent 的 default.py。
3. 补协议硬规则：[01](01-llm-protocols.md) 里的工具调用、结束原因、推理块回传几节 → Anthropic Parallel tool use。
4. 看生产级怎么做：OpenAI《Unrolling the Codex agent loop》→ Manus 上下文工程 → 12-factor agents 全文。
5. 工具与上下文：Anthropic《Writing effective tools》→《Effective context engineering》→ Context Rot。
6. 持久化与审批：LangGraph Persistence → Interrupts。
7. 多 agent：Anthropic 研究系统 和 Cognition《Don't Build Multi-Agents》对照读 → OpenAI handoff cookbook。
8. 主循环细节：Claude Agent SDK《How the agent loop works》→ Codex 的 turn.rs / compact.rs / agents_md.rs 对照本章第 11–16 节读 → opencode 的 run-state.ts、instruction.ts、overflow.ts。
9. 做设计决定前：读本章「三、要拿的主意」，再对照 OpenAI Mid-turn steering、LangSmith Double texting、各家 Compaction 文档。
10. 最后拿本章「二、文章很少讲但常碰到的事」对照自己的代码逐条检查。
