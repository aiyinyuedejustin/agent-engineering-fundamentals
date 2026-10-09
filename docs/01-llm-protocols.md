# 01 · 模型接口协议与请求层

> 范围：调模型的那一层：消息怎么拼、请求怎么发、流怎么收、结束原因怎么看、钱和 token 怎么算。重试、超时、限流放在 [02 网络与可靠性](02-reliability.md)。
> 资料核对时间：2026-10-09。各家文档改得很勤（OpenAI 文档已从 platform.openai.com 搬到 developers.openai.com，Anthropic 从 docs.anthropic.com 搬到 platform.claude.com，Gemini 主推的接口已换成 Interactions API），具体数字以链接里的为准。
> 标了「(经验)」的条目是常见工程经验，没有找到一篇官方文档专门讲。

---

## 一、知识拆解

### 1. 消息模型：三家接口长得不一样

**1.1 OpenAI Chat Completions：消息数组 + 无状态**
- 请求就是 `messages` 数组，每条有 `role`（`system`/`developer`/`user`/`assistant`/`tool`）和 `content`。`content` 可以是字符串，也可以是 parts 数组（`{"type":"text"}`、`{"type":"image_url"}` 等）。
- 服务端不记任何东西，每轮你都得把完整历史发过去。
- 模型要调工具时，assistant 消息里带 `tool_calls`（每个有 `id`、`function.name`、`function.arguments`），这时 `content` 常常是 `null`。`arguments` 是 **JSON 字符串**，不是对象，要自己 `json.loads`。
- 工具结果用 `role:"tool"` + `tool_call_id` 回填。一条 assistant 消息里的每个 `tool_call` 都必须有对应的 tool 消息，少一个就 400。

**1.2 OpenAI Responses：Items + 可选的服务端状态**
- 输入叫 `input`，输出是 `output` 数组，里面是各种 Item：`message`、`function_call`、`function_call_output`、`reasoning` 等，每个 Item 有自己的 `id`。
- 工具调用是独立的 `function_call` Item，带 `call_id`；回填用 `{"type":"function_call_output","call_id":...,"output":...}`，不是 `role:"tool"`。
- 两种多轮方式：一是传 `previous_response_id` 让服务端接上历史（依赖 `store`，响应默认存 30 天）；二是自己把上一轮 `output` 里的 Item 原样拼回 `input`（无状态）。
- 坑：`previous_response_id` 指向的响应拿不到时，文档要求你把它设成 `null`，再发完整上下文；所以就算用服务端状态，也要在本地留一份完整历史。
- 结构化输出参数名不同：Chat 是 `response_format`，Responses 是 `text.format`。

**1.3 Anthropic Messages：content blocks**
- `system` 是**顶层参数**，不放在 messages 里（Anthropic 的 OpenAI 兼容层会把 system/developer 消息提到最前面拼起来，见第二节第 1 条）。
- `content` 是 block 数组：`text`、`image`、`tool_use`（有 `id`、`name`、`input`，`input` 已经是对象）、`tool_result`（有 `tool_use_id`、`content`、可选 `is_error`）、`thinking` 等。
- 硬规则：`tool_result` 必须放在**紧挨着的下一条 user 消息**里，并且在 content 数组里**排在最前面**，文字只能放在所有 tool_result 后面。违反时报错 "tool_use ids were found without tool_result blocks immediately after"。
- 必须带 `anthropic-version` 请求头（SDK 会自动加）。

**1.4 Gemini：contents/parts，接口正在换代**
- 老接口 `generateContent`：`contents[]` 里每条是 `{role: "user"|"model", parts: [...]}`，系统提示是单独的 `systemInstruction`；流式走 `:streamGenerateContent`。
- part 上有 `thought`、`thoughtSignature`（不透明的 base64 签名，下一轮要原样带回）。
- 新的 Interactions API 用 `input` + `steps`，流式事件是 `step.start / step.delta / step.stop`，签名以 `thought_signature` 增量的形式在 `step.stop` 前发出。
- 显式上下文缓存只在 generateContent 上有，Interactions API 只有隐式缓存。选接口时这点会影响成本设计。

**1.5 消息最后都会变成一串 token**
- 不管哪种 JSON 格式，服务端最终都用聊天模板（chat template）把消息渲染成带特殊标记的文本，再分词。比如 `add_generation_prompt` 会在末尾加上「assistant 开始说话」的标记。
- 所以 token 计数里每条消息都有固定开销（OpenAI cookbook 里是每条 +3，回复前再 +3），而自部署模型的模板写错，工具调用就会坏。

### 2. 流式（SSE）

**2.1 SSE 本身**
- 格式是一行行 `event:` / `data:` / `id:` / `retry:`，事件之间用空行分隔；一个事件可以有多行 `data:`，要拼起来。别按 TCP 包切，要按行缓冲。
- 浏览器的 `EventSource` 只支持 GET，LLM 接口是 POST，所以都是自己用 fetch 读流再解析。

**2.2 各家事件序列**
- Chat Completions：每块是 `chat.completion.chunk`，增量在 `choices[0].delta`。设了 `stream_options: {"include_usage": true}` 后，最后会多出一块：`choices` 是空数组 `[]`，`usage` 有值；前面所有块的 `usage` 都是 `null`。只写 `chunk.choices[0]` 的代码会在这一块崩掉。
- Responses：带类型的事件，`response.created` → `response.output_item.added` → `response.output_text.delta` / `response.function_call_arguments.delta` → `...done` → `response.completed`（或 incomplete/failed）。每个事件有 `sequence_number`，可以用来检查有没有丢事件、顺序对不对。
- Anthropic：`message_start` → 每个块各自一组 `content_block_start` / `content_block_delta` / `content_block_stop` → `message_delta`（带 `stop_reason` 和**累计**的 usage）→ `message_stop`。中间可能插 `ping`，也可能来一个 `event: error`（比如 `overloaded_error`，非流式时对应 HTTP 529）。所以 HTTP 200 不代表这次请求成功。

**2.3 流式工具参数拼接（最常出 bug 的地方）**
- Chat Completions：`delta.tool_calls[i]` 按 `index` 归属，`id` 和 `name` 通常只在第一块出现，后面只有 `arguments` 片段，按 index 拼字符串，流结束后再 parse。并行调用时多个 index 会交错出现。
- 有的「OpenAI 兼容」服务第一块不带 `function.name`。Vercel AI SDK 专门为这种情况按 index 先把参数缓冲起来，等拿到 name 再往下传（源码见资料清单）。
- Anthropic：`input_json_delta.partial_json` 片段按 content block 的 `index` 拼，`content_block_stop` 后再 parse。第一个片段可能是空字符串。
- 开了 Anthropic fine-grained tool streaming 后，服务端不做缓冲和校验，可能收到不完整或非法 JSON。被 `max_tokens` 截断时参数也会断在中间。parse 一定要包 try。

### 3. 工具调用协议细节

- **id 必须配对**：OpenAI 的 `tool_call_id`/`call_id`、Anthropic 的 `tool_use_id`，都必须对应得上，不能漏、不能重复。截断历史时不能把调用和结果拆开（只删 assistant 的 tool_calls、留下 tool 结果会 400，反过来也一样）。
- **并行调用**：OpenAI 用 `parallel_tool_calls: false` 可以限制成最多一个；Anthropic 一轮多个 `tool_use` 时，结果要放在同一条 user 消息里一起回。
- **工具出错也要回填**：Anthropic 用 `is_error: true`，OpenAI 就把错误信息写进 output。不回填，下一次请求就因为 id 配不上直接失败。
- **严格模式**：OpenAI 的 `strict: true` 要求 schema 里所有字段都写进 `required`，并且 `additionalProperties: false`。Anthropic 有 Strict tool use（语法约束采样）。注意：Anthropic 的 OpenAI 兼容层会**忽略** `strict`。

### 4. 结束原因：每次都要看

- OpenAI Chat：`finish_reason` 有 `stop` / `length` / `tool_calls` / `content_filter`。Responses：`status: "incomplete"`，`incomplete_details.reason: "max_output_tokens"`。
- Anthropic `stop_reason`：`end_turn` / `max_tokens` / `stop_sequence` / `tool_use` / `pause_turn`（服务端工具循环到上限了，把 assistant 内容原样发回去就能接着跑）/ `refusal` / `model_context_window_exceeded`。
- 被 `max_tokens` 截断、最后一块又是 `tool_use` 时，文档建议**调大 max_tokens 重新请求**，不要拿半截参数去执行。
- Anthropic 有时在工具结果之后返回空回复（只有 2–3 个 token，`end_turn`）。文档专门讲了原因和处理办法，不能当成任务完成了。
- 推理模型可能把 `max_output_tokens` 全花在推理上，结果是零可见输出、照样收费。OpenRouter 文档把这种情况写成 `finish_reason:"length"` + 空 content，而且明确说重试没用，要调高上限或者限制推理量。

### 5. 结构化输出

- 三档可靠性：在提示词里说「请输出 JSON」 < JSON mode（保证是合法 JSON，不保证结构） < 带 schema 的 Structured Outputs（受约束解码，保证符合 schema）。
- OpenAI Structured Outputs 对 schema 有限制（必须全部 required、`additionalProperties:false`），可选字段要用 `["string","null"]` 这种写法表达。
- 模型拒答时不按 schema 输出，而是给一个 `refusal` 字段，代码要单独处理这个分支。
- Anthropic 有 JSON outputs 和 strict tool use 两样，前者管回复格式，后者管工具入参，可以同时开。

### 6. Token、分词、计数

- 主流是字节级 BPE。中文、代码、emoji 每个字符占的 token 比英文多。Gemini 文档的经验值是 1 token ≈ 4 个英文字符，对中文不成立。
- 换模型可能就换了分词器：Anthropic 文档写明 Claude Opus 4.7 及以后用新分词器，同样文本大约多 30% token，旧的计数和成本估算不能直接沿用。
- 本地 tiktoken 只能估算消息体，算不进系统隐藏 token 和工具定义渲染后的开销。Anthropic 的 `count_tokens` 接口自己也说结果是估算值。要卡上下文上限，就得留余量，或者以响应里的 `usage` 为准。
- 上下文窗口 = 输入 + 输出（推理模型还要算上推理 token）。`max_tokens` 只是输出上限，不是窗口大小。

### 7. 计费与 usage 字段

- 输入、输出、缓存读、缓存写、推理 token 的单价都不一样。usage 字段各家叫法不同：OpenAI 是 `input_tokens_details.cached_tokens` 和 `output_tokens_details.reasoning_tokens`；Anthropic 是 `cache_read_input_tokens` / `cache_creation_input_tokens`。
- 推理 token 算在输出 token 里，按输出价收费，但你看不到内容。
- 流式时 usage 只在最后才给（OpenAI 要开 `include_usage`；Anthropic 的 `message_delta` 里是累计值，不是增量，不要累加）。

### 8. Prompt caching：前缀规则决定你怎么拼上下文

- 三家都是**前缀匹配**：从请求开头起逐字节相同的部分才能命中。Anthropic 的缓存层级是 tools → system → messages，改了哪一层，这一层和后面所有层都会失效。
- 由此得出的设计规则：不变的放前面（工具定义、系统提示），会变的放后面；不要在系统提示里放时间戳；工具列表的顺序要固定；序列化 JSON 时 key 的顺序要稳定。
- OpenAI：可见输入至少 1,024 token 才能缓存（新模型；老模型按配置而定），可以用 `prompt_cache_key` 提高路由命中率，`cached_tokens` 按 128 向下取整。
- Anthropic：用 `cache_control` 显式打断点，最多 4 个；每个断点往前最多回看 20 个 block，所以一轮里加超过 20 个 block 会命中不了上一轮的缓存。有最小长度要求（按模型不同），空文本块不能缓存。
- Gemini：隐式缓存自动生效，有最小 token 数（当前 Flash 系列是 4,096）；显式缓存要单独创建缓存对象。

### 9. 采样参数

- `temperature`、`top_p`、`top_k`、`stop`、`seed`。原理看 HF 的 how-to-generate。
- 推理模型通常换用 `reasoning.effort` / `reasoning_effort`，传了某些采样参数会被拒绝或者被忽略。各家对 OpenAI `reasoning_effort` 的映射也不同（Gemini 兼容层把它映射到 `thinking_level` / `thinking_budget`，并且不能和这两个同时传）。
- OpenAI 迁移文档写明：从 GPT-5.4 起，Chat Completions 上只要用工具调用，`reasoning_effort` 就只能是 `none`。这直接影响接口选型。

### 10. 推理模型：推理内容要原样回传

- OpenAI Responses：无状态模式（`store:false` 或 ZDR）下，`reasoning` Item 自带 `encrypted_content`，下一轮要原样放回 `input`，模型才能接着之前的推理往下做，工具循环里尤其要紧。
- Anthropic：`thinking` block 带 `signature`。回填工具结果时，上一条 assistant 消息里的 thinking block 必须**完整、不改动**地一起发回去（包括 `redacted_thinking`）；一次工具循环算同一个 assistant 回合，回合中间不能改 thinking 配置。有的模型默认不显示推理内容，`thinking` 字段是空字符串、只有 signature，照样要原样带回。
- Gemini：`thoughtSignature` / `thought_signature` 同样要原样带回。
- 通用结论：**存历史时要按原始响应存**，不要只存自己抽出来的文字。网关层面要能透传这些不透明字段（OpenRouter 用 `reasoning_details` 统一了这类字段）。

### 11. 错误与重试

哪些状态码能重试、退避怎么算、SDK 默认替你做了什么、限流响应头怎么用，统一在 [02 网络与可靠性](02-reliability.md) 第 1–3 节展开。这里只记一条和协议直接相关的：同一个状态码可能对应完全不同的情况（429 既可能是发太快，也可能是额度用光），要按错误体里的 type/code 分流。

---

## 二、文章很少讲但常碰到的事

1. **多厂商消息格式互转会丢信息**：OpenAI 的 `role:"tool"` 消息要转成 Anthropic user 消息里的 `tool_result` block；多条连续 tool 消息要合并成一条 user 消息；两条连续的 user 或 assistant 要合并（LiteLLM 源码里专门有这段逻辑）。system 只能放顶层一个，Anthropic 兼容层把所有 system/developer 消息提到开头拼起来，你放在对话中间的 system 位置就变了。
2. **空 content / null**：OpenAI 带 tool_calls 时 `content` 是 `null`；转到别家时空文本块可能被拒。LiteLLM 会把空的或只有空白的文本替换成占位文字来「满足协议」，这说明这个坑真实存在。工具 `arguments` 是空字符串时，LiteLLM 转 Gemini 会补一个空对象，否则调用失败。
3. **finish_reason = length / stop_reason = max_tokens**：文本可以续写，工具调用不能拿半截去执行；推理模型可能零输出，重试也没用。见上面第 4 节。
4. **工具参数 JSON 解析失败**：没开 strict、或者开了细粒度流式、或者被截断，都可能拿到坏 JSON。常见做法是把解析错误当成工具错误回填（`is_error`），让模型自己改，不要直接抛异常让整个 agent 崩掉。（经验 + Anthropic fine-grained 文档）
5. **「OpenAI 兼容」只兼容一部分**：Anthropic 兼容层忽略 `strict`、不支持 prompt caching、丢掉音频输入，并且大部分不支持的字段会**被静默忽略、不报错**；Gemini 兼容层要用 `extra_body` 传特有参数。所以兼容层适合快速试用，不适合用在生产的关键路径上。
6. **流里出错**：HTTP 200 之后流中间可能来 error 事件（Anthropic `overloaded_error`；OpenRouter 用 `finish_reason:"error"` 的 chunk 表示）。重试逻辑要能处理「已经输出了一半」的情况：要么丢掉重来，要么续写（Anthropic 文档对部分老模型给了续写方案）。
7. **流式最后的 usage 块 `choices` 为空**：见第 2 节。
8. **模型别名和版本固定**：别名（例如 `claude-sonnet-5-5` 这种不带日期的 ID）会被悄悄指向新快照，行为、分词器、价格都可能变。生产环境固定快照版本，升级当成一次发布来测。另外分词器变了，所有按 token 定的阈值都要重新测。（Anthropic models overview / token counting 文档）
9. **字符串编码与 token 计数偏差**：按字符数估 token 在中文上偏差很大；`len()` 数的是 Unicode 码点，tiktoken 按字节 BPE 切分，emoji 和组合字符尤其不准；在 UTF-8 字节边界上截断字符串会产生非法字符。流式的增量可能把一个多字节字符拆到两块里，用字节解码器的时候要做增量解码。（经验）
10. **历史截断要按「回合」切**：截断或压缩上下文时，不能把 tool_use 和 tool_result、reasoning 和后面的 function_call 拆开；也尽量别动前缀，否则缓存全部失效。
11. **成本陷阱**：失败的请求也计入限流；推理 token 看不见但要付钱；缓存写入比普通输入更贵（Anthropic），缓存命中率低的时候反而更亏。
12. **请求 ID 要记日志**：Anthropic 响应头里的 `request-id`、OpenAI 的 `x-request-id`，排查问题和找厂商支持都要用。（Anthropic errors 文档）

---

## 三、要拿的主意

每条按「要定什么 → 选项 → 代价 → 怎么选」写。

### 决定 1：Chat Completions 还是 Responses（OpenAI）
- 选项：Chat Completions（无状态，生态最广）；Responses + `previous_response_id`（服务端存状态）；Responses + `store:false` 自己拼 Item（无状态）。
- 代价：Chat 在新推理模型上能用的东西受限（GPT-5.4 起工具调用只能配 `reasoning_effort:none`），推理内容也回传不了。服务端状态省带宽、省拼接代码，但数据要在 OpenAI 那边存 30 天，响应 ID 失效时还得退回发完整上下文，换厂商也很难迁移。无状态 Responses 要自己存好 `encrypted_content`。
- 怎么选：用推理模型做 agent，就选 Responses。有合规、ZDR、多厂商要求，或者想完全掌控上下文，用 `store:false` 自己拼。只做简单补全、或者要对接一堆兼容服务时，Chat Completions 仍然是最大公约数。

### 决定 2：自己写多厂商适配层，还是用 LiteLLM / OpenRouter 这类网关
- 选项：只用一家的原生 SDK；自己定义一套内部消息格式，每家写一个 adapter；用 LiteLLM（库或代理）；用 OpenRouter（托管网关）。
- 代价：网关接入快，但统一出来的是最小公约数，新特性（缓存断点、thinking 签名、细粒度流式）要么慢一步才支持，要么被「静默丢参数」（LiteLLM 默认对不支持的参数报错，开 `drop_params` 后就静默丢掉）。自己写 adapter 能完整掌控，但要跟着三家的文档改动一直维护。托管网关还多一跳延迟，多一个数据经手方。
- 怎么选：核心路径只用 1–2 家，就自己写一个薄 adapter，内部格式按「Item 列表 + 原始响应透传」来设计。厂商很多、要做路由和兜底的，用网关，但要实测缓存和推理字段有没有透传到。

### 决定 3：官方 SDK 还是裸 HTTP
- 代价：SDK 已经处理好重试、退避、超时、SSE 解析、流式参数拼接（读它的源码就是最好的教材），代价是多一层依赖、版本升级的成本，以及一些默认行为（比如自动重试）跟你自己的逻辑叠在一起。裸 HTTP 什么都要自己写，但完全透明、好审计。
- 怎么选：默认用 SDK，但要显式配置 `max_retries` 和超时，并且只在一层做重试（放哪一层见 [02](02-reliability.md) 决定 1）。网关、代理这类需要逐字节透传的服务，用裸 HTTP。

### 决定 4：流式还是非流式
- 代价：流式首字延迟低，长请求也不容易被网关超时切断（Anthropic 建议长请求走流式），但要处理流中报错、半截输出、usage 最后才到、工具参数拼接。非流式简单，但长输出容易超时。
- 怎么选：面向用户的界面和长输出用流式。后台批处理、短的工具决策可以用非流式。也可以服务端用流式，再自己聚合成完整结果，这样两种好处都拿到。

### 决定 5：Structured Outputs 还是自己解析
- 代价：受约束解码保证格式，但 schema 有限制，换厂商不一定支持，第一次用一个新 schema 可能有额外延迟（经验）。自己解析（提示词 + 校验 + 重试）到哪都能用，但会多花重试的钱和时间。
- 怎么选：机器要消费的字段（工具入参、路由决策）开 strict / structured outputs；跨厂商或者 schema 复杂的，用「宽松 schema + 本地校验 + 把错误回填给模型」。无论选哪个，都要处理 `refusal` 和截断。

### 决定 6：历史存什么
- 选项：只存提取出来的文字；存原始响应的 Item / blocks。
- 怎么选：存原始的。thinking 签名、encrypted reasoning、call_id 都靠它；前缀缓存也要求重放的内容和上次完全一致。

---

## 四、资料清单

- [Migrate to the Responses API (OpenAI)](https://developers.openai.com/api/docs/guides/migrate-to-responses)：说明/分析；1.1、1.2、决定 1；Messages 和 Items 的官方逐项对照，含存储默认值、`text.format`、GPT-5.4 起 Chat 的限制。
- [Conversation state (OpenAI)](https://developers.openai.com/api/docs/guides/conversation-state)：说明；1.2、决定 1；`previous_response_id`、30 天留存、ID 失效时的退路。
- [Function calling (OpenAI)](https://developers.openai.com/api/docs/guides/function-calling)：教学；1.1、3；工具调用完整循环，含 `tool_call_id`、`parallel_tool_calls`、strict schema 的写法。
- [Responses streaming events (OpenAI API Reference)](https://developers.openai.com/api/reference/resources/responses/streaming-events)：说明；2.2、2.3；全部事件类型和字段（`sequence_number`、`function_call_arguments.delta` 等），写解析器时当字典查。
- [Reasoning models (OpenAI)](https://developers.openai.com/api/docs/guides/reasoning)：说明；10、4、7；`encrypted_content`、`reasoning_tokens`、`incomplete` + `max_output_tokens`。
- [Better performance from reasoning models using the Responses API (Cookbook)](https://developers.openai.com/cookbook/examples/responses_api/reasoning_items)：教学；10；手把手演示 reasoning item 怎么回传、加密内容怎么带回。
- [Structured model outputs (OpenAI)](https://developers.openai.com/api/docs/guides/structured-outputs)：说明；5、决定 5；schema 限制、`refusal`、JSON mode 和 Structured Outputs 的区别。
- [Prompt caching (OpenAI)](https://developers.openai.com/api/docs/guides/prompt-caching)：说明；8；前缀怎么匹配、1,024 门槛、`prompt_cache_key`、`cached_tokens` 怎么算。
- [How to stream completions (Cookbook)](https://developers.openai.com/cookbook/examples/how_to_stream_completions)：教学；2.2、7；`include_usage` 最后一块 `choices` 为空。
- [How to count tokens with tiktoken (Cookbook)](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken)：教学；6、1.5；每条消息的固定开销是怎么来的。
- [Streaming messages (Anthropic)](https://platform.claude.com/docs/en/build-with-claude/streaming)：说明；2.2、2.3；事件顺序、`input_json_delta`、ping、流内 error、usage 是累计值。
- [Handle tool calls (Anthropic)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)：说明；1.3、3；tool_result 的位置和顺序硬规则、`is_error`、常见报错原文。
- [Stop reasons and fallback (Anthropic)](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)：说明；4；每种 stop_reason 怎么处理、截断的 tool_use、空回复、`pause_turn`。
- [Thinking in tool and multi-turn workflows (Anthropic)](https://platform.claude.com/docs/en/build-with-claude/thinking-tool-workflows)：说明；10；thinking block 要原样回传、一个回合内不能改配置。
- [Prompt caching (Anthropic)](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)：说明/分析；8；讲前缀缓存机制最细的一篇：缓存层级、4 个断点、20 block 回看窗口、什么会让缓存失效。
- [Token counting (Anthropic)](https://platform.claude.com/docs/en/build-with-claude/token-counting)：说明；6；计数是估算、新分词器多约 30% token。
- [OpenAI SDK compatibility (Anthropic)](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)：分析；兼容层；逐字段列出哪些被忽略（strict、缓存、音频）、system 被提到最前，是讲兼容层坑最直白的官方文档。
- [Fine-grained tool streaming (Anthropic)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming)：说明；2.3、二-4；明说可能收到非法 JSON，要防御性解析。
- [Generating content API reference (Gemini)](https://ai.google.dev/api/generate-content)：说明；1.4；`contents/parts`、`systemInstruction`、`thoughtSignature`、`streamGenerateContent`。
- [OpenAI compatibility (Gemini)](https://ai.google.dev/gemini-api/docs/openai)：说明；兼容层、9；`reasoning_effort` 怎么映射、`extra_body` 怎么传。
- [Server-sent events (WHATWG HTML 标准)](https://html.spec.whatwg.org/multipage/server-sent-events.html)：说明；2.1；SSE 解析规则的原始出处（多行 data、空行分隔、retry、Last-Event-ID）。
- [openai-python `lib/streaming/chat/_completions.py`](https://github.com/openai/openai-python/blob/main/src/openai/lib/streaming/chat/_completions.py)：源码；2.3；官方怎么把流式 chunk 累积成快照、怎么解析工具参数。
- [anthropic-sdk-python `lib/streaming/_messages.py`](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/lib/streaming/_messages.py)：源码；2.3；`partial_json` 怎么累积成工具输入快照。
- [Vercel AI SDK `openai-compatible-chat-language-model.ts`](https://github.com/vercel/ai/blob/main/packages/openai-compatible/src/chat/openai-compatible-chat-language-model.ts)：源码；2.3、兼容层；处理「首块不带 name」这类兼容服务的不规范行为，正好能看出真实世界有多乱。
- [LiteLLM `prompt_templates/factory.py`](https://github.com/BerriAI/litellm/blob/main/litellm/litellm_core_utils/prompt_templates/factory.py)：源码；二-1、二-2、决定 2；格式互转的踩坑大全：同角色消息合并、空内容处理、空参数补全。
- [OpenRouter API Error Handling and Debugging](https://openrouter.ai/docs/api_reference/errors-and-debugging)：分析；4、二-6；流前和流中错误的区别、推理把预算用光导致的空输出，网关视角的总结。
- [Chat templates (Hugging Face Transformers)](https://huggingface.co/docs/transformers/main/en/chat_templating)：教学；1.5；消息 JSON 是怎么变成 token 序列的，`add_generation_prompt` 是干什么的。
- [How to generate text (Hugging Face 博客)](https://huggingface.co/blog/how-to-generate)：教学；9；greedy、beam、top-k、top-p、temperature 的直观解释。
- [深入理解 AI Agent：设计原理与工程实践 第 2 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter2.md)：教学；1、8、10；「Agent 如何调用大模型」「KV Cache 友好的上下文设计」两节从接口消息一直讲到 chat template 和缓存，包括「改前缀不只是多花钱，还可能丢掉推理」（思考块绑定前缀）的说明。

---

## 五、阅读顺序

1. 先建立消息模型：OpenAI Migrate to Responses → Anthropic Handle tool calls → Gemini generateContent 参考（扫读）。
2. 再看底层：HF Chat templates → tiktoken cookbook → Anthropic Token counting。
3. 流式：WHATWG SSE → Anthropic Streaming → OpenAI Responses streaming events → 对照读两家 SDK 的流式源码。
4. 收尾：Anthropic Stop reasons（错误和重试接着读 [02](02-reliability.md)）。
5. 成本与推理：Anthropic Prompt caching → OpenAI Prompt caching → OpenAI Reasoning + reasoning items cookbook → Anthropic thinking tool workflows。
6. 多厂商：Anthropic 的 OpenAI 兼容说明 → Gemini OpenAI 兼容 → LiteLLM factory.py → Vercel 源码 → OpenRouter 错误处理文档。
