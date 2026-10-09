# 07 · 模型供给层：多厂商、自部署、多模态

> 范围：agent 背后"模型从哪来"这一层。具体是：一套内部消息格式怎么接好几家厂商、工具 schema 怎么适配各家、模型能力和价格数据从哪拿、小模型分工和中途换模型、自己部署开源模型（vLLM / SGLang / llama.cpp / Ollama）、图片和文件输入、厂商托管工具。
> 消息结构、SSE、结束原因、缓存前缀规则、推理内容回传的基础，以及 LiteLLM / OpenRouter / Vercel 兼容层的基本介绍，都在 [01](01-llm-protocols.md)。这里只讲 01 没讲到的部分。
> 资料核对时间：2026-10-09。源码结论来自同日的各项目 main/dev 分支。数字后面标了日期的，是那天核对过的值，各家改得很快，用之前再看一眼。
> 标「(经验)」的是工程常识，没找到一篇官方资料专门讲；标「(推断)」的是从源码读出来、但代码注释里没明说意图的。

---

## 一、知识拆解

### 1. 内部消息格式（canonical message）：你自己的那一层

**1.1 为什么要有自己的格式**
- 三家原生格式（见 01 第 1 节）互相转换都有损。能无损存下来的唯一办法，是内部格式是"并集"：每个 part 除了通用字段，还带一个"原厂原样数据"槽，比如 Vercel AI SDK 的 `providerOptions` / `providerMetadata`，opencode 在 part 上存 `metadata`。
- 必须原样存的东西：
  - 推理块的签名或密文：Anthropic `thinking.signature`、`redacted_thinking.data`；OpenAI Responses 的 `reasoning.encrypted_content`；OpenRouter 的 `reasoning_details` 数组（要求原样、按原顺序回传）。
  - 缓存断点位置（`cache_control` 挂在哪个 block 上）。
  - 图片引用的形态：base64 原文、URL 还是 file_id，以及缩放前后的尺寸。
  - 工具调用 id 的原值。各家对 id 格式有限制，转换时要改写，但存档要存原值，并且映射关系要稳定。
- 每条 assistant 消息要记下**是哪个厂商、哪个模型、哪个账号/渠道**产生的。原因见 1.3：推理块能不能回传，取决于这三样。

**1.2 发出去之前的"每家一套修补"：opencode `normalizeMessages` 是一份现成清单**
（来源：opencode `packages/opencode/src/provider/transform.ts`，2026-10-09）
- 去掉孤立的 UTF-16 代理字符（lone surrogate），否则有的厂商 JSON 解析直接报错。
- Anthropic / Bedrock：空文本 part 会被拒，要删掉；没有签名的 reasoning 要过滤掉。
- Claude 的工具调用 id 只能是 `[a-zA-Z0-9_-]`，其他字符要替换。
- Mistral：工具调用 id 必须正好 9 位字母数字；tool 消息后面不能直接跟 user 消息，要插一条内容为 "Done." 的 assistant 消息。
- DeepSeek：每条 assistant 消息都要带推理字段。
- 声明了"交错推理字段"（`reasoning_content` 或 `reasoning_details`）的模型：这个字段每条 assistant 消息都设上，空的也设。
- 模型不支持的模态（比如给纯文本模型发了图）：替换成一段文字 "ERROR: Cannot read ...，请告知用户"，不让整个请求失败。
- OpenAI Responses 且 `store=false`：去掉历史里 item 的 id，因为服务端没存，引用不到。
- 要点：这些都是"发送时"做的投影，不改存档。

**1.3 推理块的绑定关系（Anthropic 最严格）**
（来源：Anthropic thinking / extended-thinking 文档，2026-10-09）
- thinking 块只在**系统提示、工具定义、它之前的消息都没变**时有效。改了这些再把旧 thinking 发回去，会 400 或被丢掉。对 2026-08-31 及之后创建的账号，这条默认强制执行。
- 部分模型的 thinking 块绑定到产生它的账号，换账号（比如从直连换到 Bedrock）就不认。
- 跨模型能不能读，看一张"模型 × 渠道"的矩阵。读不了的块会被**静默丢弃**，不计费，也不报错。经验规律是换到更新的模型往往能保留，换到旧模型就丢。
- 手动 thinking（`budget_tokens`）只支持 `tool_choice` 为 auto/none；adaptive 模式才支持强制调用工具。
- 一轮中途开关 thinking，会被静默关掉；改 `budget_tokens` 或 thinking 模式会让缓存失效。
- 官方给了不破坏前缀的替代做法：对话中途的 system 消息、`tool_addition` / `tool_removal` 块、每条消息单独的 `output_config`。也就是说，想"中途改提示或改工具"，用这些追加的方式，别回头改前面。
- DeepSeek thinking 模式（2026-10-09）：请求带 `tools` 时，之前所有 `reasoning_content` 都必须回传，否则 400；不带 tools 时回传了也被忽略。

### 2. 工具 schema：一份定义，多家方言

**2.1 各家拒什么（2026-10-09 源码里的规则）**
- OpenAI strict 模式：要求所有字段 required、`additionalProperties:false` 等（见 01 第 5 节）。
- Gemini（opencode 的 Gemini 分支）：
  - 整数 enum 要转成字符串 enum；
  - `type: ["string","null"]` 这种类型数组，要转成 anyOf 加 `nullable`；
  - `required` 里不在 properties 中的 key 要删；
  - 数组的 `items` 为空时补 `type: string`；
  - 非 object 节点不能带 properties / required。
  - Gemini 官方结构化输出页现在已经支持 `$ref`、`anyOf`，但仍写着"只支持 JSON Schema 子集""过大或嵌套过深的 schema 可能被拒"，函数调用页建议工具数控制在 10–20 个。经过 OpenAI 兼容代理去调 Gemini 时，上面那些清洗仍然需要。
- Moonshot（Kimi）：`$ref` 节点旁边不能有别的关键字；不接受元组形式的 `items` 数组；schemars 生成的 `oneOf` 加 `const` 写法会被拒。
- pydantic-ai 给每家配一个 `json_schema_transformer`，思路和上面一样。

**2.2 四个项目的四种做法**
- Codex `codex-rs/tools/src/json_schema.rs`：先"消毒"：
  - 布尔 schema 变成字符串类型；
  - `const` 变成只有一个值的 `enum`；
  - 缺 `type` 的按其他关键字推断；
  - 删掉没人引用的 `$defs`。
- Codex `json_schema/compaction.rs`：schema 超过 `DEFAULT_COMPACT_TOOL_SCHEMA_BYTES = 5000` 字节时有损压缩，按顺序：先删 description → 再删 definitions → 再把深度超过 3 的部分折叠 → 最后裁 anyOf/oneOf。说明大型 MCP 工具的 schema 本身就会挤占上下文，而且得有个上限。
- Goose `crates/goose/src/agents/tool_schema_normalize.rs`：
  - 把"全是字符串 const 的 oneOf"折成 enum。注释里说 schemars 输出比等价 enum 大约 9 倍，而且 Moonshot 直接拒。
  - 原则：**只做能证明等价的改写**，证明不了就原样放过；还区分 draft-04/06/07 的语义差别。
- Vercel AI SDK `packages/openai/src/normalize-openai-json-schema.ts`：
  - 删掉 `propertyNames`、带前后断言（lookaround）的正则 pattern，删的时候发 warning；
  - 改写 Zod 4 生成的单元素 allOf 引用；
  - 实在没法安全转换时，直接抛 `UnsupportedFunctionalityError`。

**2.3 由此得出的规则**
- 等价改写：静默做，比如 const→enum、类型数组→anyOf。
- 有损改写（删约束）：要发 warning，并且**在本地用原 schema 校验模型给的参数**，因为厂商那边已经不检查被删的约束了。
- 无法表达：报错，不要发一个"差不多"的 schema 出去。

### 3. 能力目录和价格数据

**3.1 数据从哪来**
- models.dev（sst/models.dev）：
  - 一个开源的 TOML 仓库，提供 `api.json` 等文件。
  - 每个模型的字段：attachment、reasoning、tool_call、structured_output、temperature、knowledge、release_date、open_weights、`interleaved.field`（推理字段叫什么）、`cost.{input,output,reasoning,cache_read,cache_write,input_audio,output_audio}`、分档价格（如超过 200k 的价）、`limit.{context,input,output}`、modalities、status（deprecated）。
  - opencode 运行时就读它。
- LiteLLM `model_prices_and_context_window.json`：
  - 约 4,504 条（2026-10-09）；
  - 字段有 supports_function_calling / parallel_function_calling / prompt_caching / reasoning / vision / response_schema / system_messages、deprecation_date 等；
  - 文件自己标注 `max_tokens` 是含义模糊的旧字段，要看 `max_input_tokens` / `max_output_tokens`。
- 厂商自己的列表接口：
  - OpenRouter `/api/v1/models`：每个模型支持哪些参数、哪些推理档位。
  - vLLM `/v1/models`：返回 `max_model_len`。
  - Ollama `/api/show`：返回 `capabilities` 和 `model_info.*.context_length`。注意这是**训练时的最大值，不是运行时的 num_ctx**，见第二部分。
- Azure v1 接口：`model` 填的是**部署名**，从名字看不出是什么模型。opencode 的 `getSmallModel` 对 Azure 直接返回 undefined，就是这个原因。

**3.2 Codex 怎么管目录**（`codex-rs/models-manager`，2026-10-09）
- 远程目录本地缓存 300 秒，到期用 ETag 重新校验；缓存 key 包括 provider、凭证身份、客户端版本（不同账号看到的模型可能不同）；缓存出错不致命。
- 未知模型用 `model_info_from_slug` 生成兜底元数据：
  - 上下文 272000，可用比例 95%；
  - 工具输出按 10KB 字节截断；
  - 不开推理档位；
  - 打上 `used_fallback_model_metadata: true`，让上层知道这是猜的。

**3.3 Goose 怎么算钱**（`crates/goose/src/providers/canonical_cost.rs`）
- 价格优先级：厂商返回的实际花费 > 用户配置 > 规范价格表 > 内置定义。
- 缓存读写单独定价，不把缓存命中的 token 按原价算高。
- 每笔费用带来源标记：`ProviderReported`（厂商报的）或 `Estimated`（估的）。

**3.4 按模型配置的行为开关**（pydantic-ai `profiles/__init__.py`、`google.py`）
- `supports_forced_tool_choice`：部分新 Claude 和 Moonshot 不接受强制 tool_choice。
- `supports_forced_tool_choice_with_thinking`：DeepSeek V4 只有关掉 thinking 才能强制。
- `forced_tool_choice_disables_thinking`：Claude 强制工具时 thinking 会被关。
- `thinking_always_enabled` / `thinking_enabled_by_default`。
- `supports_inline_system_prompts`：为 false 时，对话中途的 system 内容改成 user 消息并用 `<system>` 包起来。
- Google：老模型内置工具（搜索等）和自定义函数不能同时用（Gemini 3 起可以）；有 VALIDATED 模式；`thinking_level` 和 `thinking_budget` 分代使用。
- 结论：能力目录不能只有"支持/不支持"，还要有"支持，但和什么冲突"。

### 4. 小模型分工和中途换模型

**4.1 哪些活给小模型**（opencode `provider.ts` / `transform.ts`）
- 选法：先用配置的 `small_model`；没配就用同一厂商里最新的小模型；都没有就用主模型。
- 用在：会话标题生成、摘要之类不进主推理链的活。
- 调小模型时：`store:false`，thinking 关掉或调到最低档。
- 不交给小模型的(经验)：决定调哪个工具、改代码、安全判断。小模型更容易吐出格式错误的工具调用，vLLM 文档也写了小号 Llama 常出畸形调用。

**4.2 换模型要处理什么**（Codex `core/src/session/turn.rs`、`context/model_switch_instructions.rs`）
- 换到上下文更小的模型、且当前已超过新模型上限时，**先用旧模型做一次压缩**（`CompactionReason::ModelDownshift`），新模型再接手。原因是旧模型还装得下全文。
- 模型的"压缩兼容哈希"（comp_hash）变了，也会先压缩一次。
- 压缩时还原上一轮的访问配置，因为"旧模型 + 新配置"的组合可能被服务端拒。
- 换完插一条 developer 消息 `<model_switch>`："用户之前用的是别的模型，请按以下说明继续"，附上新模型自己的指令。
- 还要处理(经验)：
  - 旧推理块：按 1.3 的规则决定丢弃，或转成纯文本摘要；
  - 工具 schema：重新按新厂商方言转换；
  - 图片：新模型不支持图片时，替换成文字占位；
  - 缓存：整段失效，第一轮按全价算。

### 5. 自部署推理引擎

**5.1 vLLM：工具调用要开对开关**（`docs/features/tool_calling.md`，2026-10-09）
- 自动工具调用要 `--enable-auto-tool-choice --tool-call-parser <名字>`，有时还要 `--chat-template`。parser 选错或没配，表现是工具调用以纯文本出现在 content 里，或者 `tool_calls` 为空。
- `tool_choice` 为 named 或 required 时，走结构化输出约束：
  - 第一次编译状态机会多花几秒；
  - 文档原话：保证"能解析的函数调用，不保证是高质量的"。
- `tool_choice=auto`：只有工具标了 `strict:true`，或者开了 `--tool-strict-level function|parameter`，参数才按 schema 约束；否则畸形的标记文本可能漏到输出里。`VLLM_ENFORCE_STRICT_TOOL_CALLING` 默认 true。
- 用 `hf` 这类基于 response_template 的 parser 时：不支持 strict、不支持 required/named、不支持 `parallel_tool_calls=false`；流式时解析不了的调用会**直接丢掉**。
- `tool_choice=none` 时工具定义默认仍会塞进 prompt（占 token，模型也可能照着写调用文本），除非加 `--exclude-tools-when-tool-choice-none`。
- 已知问题：Llama 3 不支持并行工具调用；小 Llama 经常输出畸形调用。

**5.2 vLLM：推理输出**（`docs/features/reasoning_outputs.md`）
- 响应字段从 `reasoning_content` 改名为 `reasoning`。老客户端读旧字段名，只会**静默读到空**。Vercel 的 openai-compatible 包用 `reasoning_content ?? reasoning` 两个都读。
- 工具调用只从 content 里解析，**不从 reasoning 里解析**。模型把调用写进 `<think>` 里，就丢了（见第 5 节）。
- 各模型 thinking 默认值不同：Qwen3 默认开，DeepSeek-V3.1、Gemma 4 默认关。DeepSeek-V3.1 只有非 thinking 模式能调工具。
- 开关方式：`chat_template_kwargs`（如 `enable_thinking`），或服务端 `--default-chat-template-kwargs`；传 `reasoning_effort` 会自动注入 `enable_thinking`；还有 `thinking_token_budget`。
- 推理只在 chat、`/v1/messages`、`/v1/responses` 三个接口上有。

**5.3 vLLM：其他会坑人的默认值**
- 结构化输出（`structured_outputs.md`）：
  - 后端 xgrammar / guidance，默认 auto，两者的正则方言不同；
  - 老的 `guided_*` 参数 v0.12.0 已删；
  - Qwen3 Coder 要在推理段里也约束，需开 `--structured-outputs-config.enable_in_reasoning=True`。
- 生成配置（`openai_compatible_server.md`）：
  - 默认读模型仓库里的 `generation_config.json`，覆盖你以为的采样默认值；
  - 里面的 `max_new_tokens` 会变成全服务的输出上限；
  - 要用 vLLM 自己的默认值，加 `--generation-config vllm`。
- 前缀缓存（`design/prefix_caching.md`）：
  - 按块做哈希，v0.11 起默认 sha256；用 xxhash 在多租户下有碰撞风险；
  - 请求带 `cache_salt` 可以隔离租户，也防止靠响应时间探测别人的 prompt；
  - 缓存只加速 prefill，不加速 decode。
- 显存不够（`configuration/optimization.md`）：KV cache 不够时抢占请求，用 RECOMPUTE 方式重算，延迟会抖。调 `gpu_memory_utilization`、`max_num_seqs`、`max_num_batched_tokens`；chunked prefill 默认开。

**5.4 多副本：前缀缓存要配合路由**
- vLLM 自带的数据并行负载均衡只看各引擎的运行队列和等待队列，文档说"将来可能加入 KV cache 感知"，也就是**现在不看缓存**（`serving/data_parallel_deployment.md`）。
- vLLM 文档的 llm-d 页：多副本下轮询负载会破坏缓存命中。llm-d 读取 vLLM 的 KV cache 事件，把请求发到已有该前缀的副本。官方给的数据是在他们的测试上比轮询吞吐 3 倍、首 token 快 2 倍（Llama 3.1 70B，MI300X，2026-10-09 页面）。
- SGLang 的 Model Gateway 有 `--policy cache_aware`。
- 对 agent 的意义(经验)：同一会话每轮前缀几乎不变，至少要按会话 id 做粘性路由，否则自建集群的缓存命中率会远低于单机测试。

**5.5 parser 错了或有 bug 的症状：`finish_reason=tool_calls` 但 `tool_calls` 是空的**
（vLLM issue，2026-10-09 核对）
- #53255（2026-08-21，v0.27.0）：`tool_choice=required` 返回 `finish_reason=tool_calls`，但 tool_calls 是空数组；没配 parser 时最容易出现。
- #39056（2026-04-06）：Qwen3.5 把 XML 格式的工具调用写在 `<think>` 里，被推理 parser 吞掉，tool_calls 为空。
- #50889（2026-08-03）：Gemma4 parser 在并发下偶发丢调用（`finish_reason=tool_calls`，数组为空），报告者 2 天内遇到约 5 次。
- #53363：Gemma4 上 required 不生效，只回一段文字。
- 同类还有 kimi_k2 流式解析（#54701）、DeepSeek-V3 多行参数（#60342）等。
- 同一个开源模型换个托管商效果也不同：Moonshot 的 K2 Vendor Verifier（2025-11-15 测试）里，kimi-k2-thinking 在各家的 schema_accuracy 从 100% 到 87% 左右不等，自部署 vLLM 那一行是 87.22%，SGLang 95.52%。它用的指标正好可以直接拿来当网关检查：`finish_reason 为 tool_calls 的次数` 对比 `成功解析出合法调用的次数`。

**5.6 SGLang、llama.cpp、Ollama 的差别**
- SGLang（`tool_parser.mdx`）：
  - parser 名字和 vLLM 不一样，比如 Qwen2.5 在 SGLang 叫 `qwen25`，vLLM 用 `hermes`；
  - gpt-oss parser 会过滤 analysis 通道，content 可能为空；
  - DeepSeek 要换 chat template。
  - Qwen 官方文档给 Qwen3 推荐 `--tool-call-parser hermes --reasoning-parser deepseek_r1`，vLLM 文档的表里写 `qwen3`。几家文档对不上，以实测为准。
- llama.cpp（`docs/function-calling.md`）：
  - 必须加 `--jinja`；
  - 认不出模型的模板时退回通用处理器（Generic），更费 token，日志里会出现 "Chat format: Generic"，这是排查的第一个信号；
  - 可以用 `--chat-template-file` 指定模板；
  - 并行工具调用默认关，请求里要带 `"parallel_tool_calls": true`；
  - 文档专门警告：过度量化 KV cache（如 `-ctk q4_0`）会损害工具调用；DeepSeek R1 官方模板有 bug。
- Ollama：
  - 默认上下文几处文档说法不一：FAQ 写 4096；`context-length.mdx` 写按显存给（<24GiB 给 4k，24–48GiB 给 32k，≥48GiB 给 256k），并建议 agent 类任务至少 64000；Modelfile 参数表写 num_ctx 默认 2048（都是 2026-10-09 的仓库内容）。
  - OpenAI 兼容接口不能设上下文大小，要用 Modelfile 或环境变量 `OLLAMA_CONTEXT_LENGTH`。
  - `OLLAMA_NUM_PARALLEL` 默认 1，显存按"并发数 × 上下文"涨；排队上限 `OLLAMA_MAX_QUEUE` 512；`keep_alive` 默认 5 分钟后卸载模型，下次请求冷启动。
  - Responses 的有状态用法（`previous_response_id`）不支持。
  - 超长时静默截断：`server/prompt.go` 的 `chatPrompt` 从最旧的消息开始丢，保留 system 消息和最后一条，只在 debug 日志里记一行；估算时每张图按 768 token 算。

**5.7 模型不会原生调用工具时**
- Goose `providers/toolshim.rs`：主模型照常输出文字，再用第二个"解释模型"（通过 Ollama 结构化输出）从文字里抽出工具调用。
- Qwen 文档：推理模型不要用"靠停止词切分"的 ReAct 模板，因为停止词可能出现在思考内容里，提前截断。
- HF transformers 的 chat_extras：
  - 多数模板期望 `arguments` 是字典，而 OpenAI 格式是 JSON 字符串，要转换；
  - 很多模型一次只出一个调用；
  - 工具调用 id 大多是框架编的，不是模型生成的。

### 6. "OpenAI 兼容"背后的静默差异
- DeepSeek thinking 模式（2026-10-09）：
  - temperature 和各种 penalty 被静默忽略；top_p 被限制在 0.95–1.0；
  - effort 映射：minimal→low、medium→high、xhigh→high、ultra→max；
  - `thinking` 参数要放在 `extra_body`。
- Kimi Vendor Verifier 博客：K2 Thinking 的 API 层强制 temperature=1.0、top_p=0.95，并强制校验 thinking 内容有没有正确回传。原因是社区大量"跑分异常"其实是解码参数用错。
- LiteLLM：遇到不支持的参数默认报错，`drop_params=True` 时静默删掉。
- OpenRouter 选托管商（2026-10-09）：
  - `require_parameters` 默认 false：不支持某参数的托管商也会被选中，然后忽略这个参数；tools、response_format 这类只算"偏好"。
  - 默认负载均衡按价格平方的倒数加权，避开最近 30 秒出过故障的；用了 sort 或 order 就不再做负载均衡。
  - 可以按量化等级（int4…bf16、unknown）过滤，还有 max_price、zdr、data_collection、only/ignore。
  - 发往 Anthropic 时，除非带结构化输出的 beta 头，否则 `strict` 会被去掉。

### 7. 云渠道：同一个模型，功能不一样
- Claude 走 Amazon Bedrock（Anthropic 文档的 Bedrock 页，2026-10-09）：
  - 端点 `bedrock-mantle.{region}.api.aws/anthropic/v1/messages`，模型 id 带 `anthropic.` 前缀；
  - 认证可用 SigV4、服务角色、IAM 角色（12 小时）、bearer token（12 小时）；
  - 不支持：结构化输出、URL/Files API 来源的图片和文档、服务端工具（代码执行、网页搜索/抓取）、Batches、Models 接口；
  - 区域端点贵 10%，global 不加价；默认配额每分钟输入 200 万 token。
- Claude 走 Google Vertex：
  - `model` 写在 URL 里，请求体带 `anthropic_version: vertex-2023-10-16`；
  - 支持结构化输出和网页搜索；不支持代码执行、网页抓取、Files/URL 来源、Batches；
  - 请求体上限 30MB；区域和多区域（us/eu）端点贵 10%；预留吞吐只能用区域端点。
- Azure OpenAI v1（`/openai/v1/`）：不用再带 api-version；`model` 填部署名（见第 3 节）。
- 意义：能力目录的 key 要是"模型 × 渠道"，不能只是模型。

### 8. 多模态输入

**8.1 图片怎么算 token：三家规则完全不同**
- Anthropic（vision 文档，2026-10-09）：
  - 28×28 一块，token ≈ ⌈宽/28⌉×⌈高/28⌉；
  - 标准档长边 1568px、约 1568 token 封顶；高分辨率档（Claude 4.7 及以后）长边 2576px、约 4784 token。
  - 一次请求超过 20 张图时，每张图尺寸限制变严（保持在 2000px 以内）。**这个计数包括历史消息和 tool_result 里的图**。
  - 单图 10MB（Bedrock/Google 上 5MB）；请求 32MB；每请求 100 张（200k 上下文的模型）或 600 张（其他）；最大 8000×8000。
  - 不读 EXIF 等图片元数据。
  - 坐标是相对缩放后的图说的。
- OpenAI（images-vision，2026-10-09）：
  - detail 有 low / high / original / auto；
  - 文档原话："low 不一定比 high 省 token"，比如 gpt-5.4 的 low 用的是 2048px、6,144 块的预算；
  - 按 32px 一块算，high 最多 2,500 块，超过 30,000 块直接拒；
  - 请求体 512MB、每请求最多 1,500 张；
  - 要用坐标时，建议自己先缩放，再把坐标换算回原图。
- Gemini（media-resolution，2026-10-09）：每张图的 token 数**固定**，和像素无关。Gemini 3 每张：low 280、medium 560、high 和默认 1120、ultra_high 2240。视频每帧 70 或 280；音频每秒 25；PDF 按 medium 560 每页，另加原生文本。

**8.2 图片用 base64、URL 还是 file_id**
- Anthropic 三种都支持，但 Bedrock / Vertex 上只能 base64。
- base64 每轮都要随历史重发，体积和费用都跟着历史涨。官方建议多轮里反复引用的图走 Files API。
- URL 方式：图要能被厂商服务器访问到，内网图不行；Codex 对不支持远程 URL 的情况直接换成文字占位（见第 8 节）。
- 文件类：
  - OpenAI file-inputs：PDF 会同时送抽取的文本和每页图片（token 更多）；docx/pptx 只送文本；表格走专门流程；Chat Completions 只收 PDF；单文件和总量都是 50MB。
  - Gemini：请求超过 100MB（PDF 50MB）要走 Files API。常见的"内联上限 20MB"说法已经过时。

**8.3 上传的文件谁来删**
- OpenAI Files API：单文件 512MB，每项目 2.5TB；默认一直保留到手动删除，`purpose=batch` 的默认 30 天过期；上传时可以传 `expires_after` 设自动过期。
- Anthropic Files API：
  - 单文件 500MB，每组织 1TB；
  - 上传时可设 `expires_in_seconds`（1 小时到 90 天）；
  - 文件属于整个 workspace，**同 workspace 的任何 key 都能读**，文档明确说不要接受来自不可信来源的 file_id；
  - Bedrock / Vertex 上不能用。
- Gemini Files API：48 小时自动删除；每项目 20GB、单文件 2GB；上传后不能下载回来。
- 留存：
  - Anthropic Files API 标注"不适用 ZDR"；
  - OpenAI 的 `/v1/files`、`/v1/vector_stores` 也不在 ZDR 范围（your-data 页）。
  - 所以"开了零数据保留"不等于"文件不会留在厂商那里"。

**8.4 Codex 怎么处理图片**
- `core/src/image_preparation.rs`：
  - 单张图处理失败（太大、不支持远程 URL、不支持 low detail）时，换成一段文字占位，不让整个请求失败；
  - 图被缩放过时，插一条 developer 消息："第 N/M 张图已从 W×H 缩放到 w×h"，让模型知道坐标基准。
- `utils/image/src/lib.rs`：
  - HIGH_DETAIL 长边 2048px、最多 2,500 块；ORIGINAL 长边 6000px、最多 10,000 块；
  - 按"图片摘要 + 模式"做 LRU 缓存，同一张图每次重编码出来的字节都一样。
  - (推断) 这样做是为了不让重编码改变历史字节，保住前缀缓存。

**8.5 历史里的旧截图**(经验，结合上面的规则)
- 截图是 computer-use 类 agent 历史膨胀的大头，而 Anthropic 的"超过 20 张图"规则把历史里的图也算进去。
- Anthropic vision 文档写明：用 computer use / browser use 工具集时，tool_result 里尺寸超限的图会被**拒绝而不是自动缩小**，要在自己这边先缩。其他图默认会被自动缩小，标上 `"oversized_image":"error"`（或设 `transformations`）可以改成报错，做坐标类任务时应该这么设。超过 20 张图触发的限制，报错信息里会提到 "many-image requests"；在 Bedrock / Google 上 PDF 这类文档块也算进这个数。
- 常见做法：只保留最近 K 张原图，更早的替换成一行文字描述或"[截图已省略]"。替换要成批做，换一次就让缓存失效一次，别每轮都动（和 [03](03-agent-loop-context.md) 第 16 节的压缩是同一个问题）。Anthropic computer use 文档的具体建议：保留最近 3 张，每 25 轮批量删一次；对会把思考块和截图绑定的新模型，删旧截图会让后面所有思考块失效，要改用服务端的工具结果清理（context editing）。

### 9. 厂商托管工具（网页搜索、代码执行、文件检索、远程 MCP）
- 渠道不同可用性就不同：Bedrock 上 Claude 没有服务端工具；Vertex 有网页搜索，没有代码执行和网页抓取；Gemini 老模型的内置工具不能和自定义函数一起用。
- 留存（OpenAI your-data，2026-10-09）：
  - Responses 默认存应用状态 30 天，ZDR 下强制 `store=false`；background 模式约保留 10 分钟；
  - Code Interpreter 容器的状态在容器过期前一直在；
  - 图片会过 CSAM 扫描，即使开了 ZDR 也可能被留存；
  - 实时网页搜索不在 HIPAA 范围；
  - 远程 MCP 的数据按第三方自己的政策处理；
  - prompt cache 的 KV 最长留 24 小时。
- 可迁移性：托管工具的结果是厂商专有的块类型（含引用、加密内容），换厂商时历史里这些块要么丢，要么转成纯文本，见第 1 节、4.2。

---

## 二、文章很少讲但常碰到的事

1. **自部署时"模型想调工具，但 tool_calls 是空的"很常见。**
   - 在 vLLM 上，`finish_reason=tool_calls` 加空数组，在 2026 年的 issue 里至少有三种来源：没配 parser、调用写进了 `<think>`、并发下 parser 丢调用。
   - 客户端如果只看 tool_calls，会把这一轮当成"模型说完了"，agent 安静地停掉。
   - 网关要做失败关闭（fail closed）：`finish_reason` 是 tool_calls 但数组为空，或者 content/reasoning 里出现 `<tool_call>`、`[TOOL_CALLS]`、`<|tool_call` 之类的标记，就当错误处理，不当正常结束。
2. **同一个开源模型，换个托管商或部署方式，工具调用准确率能差十几个百分点。**
   - Moonshot 测 kimi-k2-thinking，各家 schema 准确率 87%–100%（2025-11-15）。
   - 选托管商不能只比价格和延迟，要跑一遍自己的工具调用回归。
   - Kimi Vendor Verifier 给了一套验收清单：先验参数约束 → OCR 冒烟测多模态预处理 → 长输出测 KV cache 和量化问题 → 工具调用 F1 + schema 准确率。
3. **Ollama 会静默丢掉最早的消息。**
   - `/api/show` 报的 context_length 是训练最大值，不是实际运行的 num_ctx（默认值几处官方文档说法不一，从 4k 到按显存给都有，别猜，显式设置）。
   - 超了以后 `chatPrompt` 从头丢消息，只留 system 和最后一条，日志只在 debug 级别。
   - 表现是 agent "忘了"任务开头说的事，而且没有任何报错。
4. **推理字段改名，读到的是空。**
   - vLLM 把 `reasoning_content` 改成了 `reasoning`；DeepSeek 带 tools 时又要求把 `reasoning_content` 全部回传，不传就 400。
   - 一个字段名不对，表现可能是"推理没了"（不报错），也可能是 400，看是哪家。
5. **"兼容接口"静默忽略参数。**
   - DeepSeek thinking 模式忽略 temperature；OpenRouter 默认会把请求发给不支持某参数的托管商；LiteLLM 开了 drop_params 就直接删。
   - 想要的约束（比如 response_format）没生效，也不会报错。
   - 关键参数要么打开"必须支持"开关（OpenRouter `require_parameters: true`），要么在本地校验输出。
6. **schema 适配器删掉的约束，厂商就不再检查了。**
   - 删 `propertyNames`、删正则 pattern、删深层结构之后，模型给的参数可能违反原 schema。
   - 所以本地要用**原始 schema** 再校验一次，失败就把错误回给模型重试。
7. **Anthropic thinking 块绑定前缀、模型和账号。**
   - 中途改系统提示或工具、换模型、换渠道（直连换 Bedrock），旧的 thinking 块可能被静默丢掉，或者报 400。
   - 想中途改东西，用官方的追加式写法（中途 system 消息、tool_addition/removal），别回头改前面。
8. **图片的"省钱档"不一定省。**
   - OpenAI 的 low 在某些模型上比 high 预算还大；Gemini 每张图固定 token，你先缩小图也省不了；Anthropic 是按像素算的，先缩小有用。
   - 预处理策略要按厂商分开写。
9. **20 张图规则把历史也算进去了。**
   - computer-use agent 跑到第 21 张截图时，所有图的尺寸限制都变严，超限的 tool_result 图是直接拒，不是自动缩小。
   - 表现是跑了一阵突然 400。
10. **Files API 上传的文件默认不会自己消失，而且同 workspace 的 key 都能读。**
    - OpenAI 默认永久保留，Anthropic 不设过期也一直在，两家都不在 ZDR 范围。
    - 只有 Gemini 是 48 小时自动删。
    - 不清理就是持续增长的数据留存和泄漏面。
11. **云渠道的同名模型功能少一截。**
    - Bedrock 上的 Claude 没有结构化输出、Files API、服务端工具；Vertex 没有代码执行。
    - 做"主渠道挂了切到云渠道"的降级时（见 02），要先确认请求里没用到这些，否则降级本身就会失败。
12. **vLLM 默认读模型仓库的 generation_config.json。**
    - 里面的采样参数和 `max_new_tokens` 会悄悄生效，表现是"输出总在某个长度被截断"或"温度和预期不一样"。
13. **多副本自建，前缀缓存要靠路由。**
    - vLLM 自带的数据并行均衡不看缓存。轮询下 agent 的长前缀每轮都可能落到没缓存的副本上，单机压测的命中率在集群上不成立。
14. **llama.cpp 日志里出现 "Chat format: Generic" 就说明模板没认出来。**
    - 工具调用能用，但更费 token、更不稳。
    - KV cache 量化到 q4_0 会伤工具调用，省显存时容易顺手开上。
15. **vLLM 里 `tool_choice=none` 不等于"不告诉模型有工具"。**
    - 工具定义默认还在 prompt 里，模型可能照样写出调用文本。
16. **把跑了一半的轨迹换到另一家模型接着跑，难点在思考的"凭证"。**
    - 各家对思考块签名的要求从"不校验"到"拒收一切非己签发"都有，签名还可能挂在工具调用上，所以"把思考删干净"在某些厂商那里也过不了。
    - 做法：按最严格的一家设计；切换时签名一律丢弃，思考文字当普通内容带入；实在不行就把历史工具调用改写成文字叙述。轨迹从一开始就按中立格式存（见决定 1）。
    - 出处：[李博杰《深入理解 AI Agent》第 5 章「故障与错误恢复」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md)。

---

## 三、要拿的主意

### 决定 1：内部消息格式怎么设计，才能让推理签名、缓存断点、图片引用都不丢
- 选项：
  - A. 直接用某一家的格式（比如 OpenAI Chat）当内部格式；
  - B. 自定义"并集"格式，每个 part 带原厂原样数据槽，加上来源（厂商/模型/渠道/账号）；
  - C. 直接用 Vercel AI SDK 或 pydantic-ai 的消息模型。
- 代价：
  - A 最简单，但接 Anthropic/Gemini 时签名和缓存断点没地方放，换回来就丢。
  - B 要自己写每家的投影和修补（参考 opencode 的清单），工作量最大，但存档无损。
  - C 省事，但被框架的更新节奏绑住。
- 怎么选：
  - 只接一家，选 A；
  - 两家以上、并且要用推理模型或缓存，选 B 或 C；
  - 不论选哪个，存档都存"原厂响应原样 + 归一化视图"两份，发送时现算投影，不把投影结果写回存档。

### 决定 2：工具 schema 统一一份，还是每家一份
- 选项：
  - A. 只写一份，发送前按厂商自动转换；
  - B. 每家手写一份；
  - C. 只用所有家都支持的最小子集来写。
- 代价：
  - A 要维护转换器，而且会出现有损转换；
  - B 工具一多就没法维护，MCP 工具也不受你控制；
  - C 表达力差，比如没法用 anyOf。
- 怎么选：
  - 默认 A。转换器至少要处理：const、类型数组/nullable、`$ref`/`$defs`、oneOf/anyOf/allOf、整数 enum、`required` 和 properties 不一致、元组 items、`propertyNames`、带断言的 pattern、format、`additionalProperties`、深度和大小。
  - 规则：能证明等价就静默改；有损就 warning 加本地校验；无法表达就报错（Vercel 和 Goose 的做法）。
  - 自己写的工具可以顺手用 C 的风格，降低转换量。

### 决定 3：能力和价格数据从哪来，未知模型怎么办
- 选项：
  - A. 依赖 models.dev 或 LiteLLM 的公开目录；
  - B. 依赖厂商的列表接口；
  - C. 自己维护一张表；
  - 通常是组合。
- 代价：
  - 公开目录有滞后，而且只按"模型"不按"渠道"；
  - 厂商接口字段不全（Ollama 报的是训练上限，Azure 只给部署名）；
  - 自己维护最准，但要人力。
- 怎么选：
  - 按"厂商返回 > 用户配置 > 公开目录 > 内置默认"合并（Goose 的顺序），key 用"模型 × 渠道"；
  - 未知模型给保守默认，并标记"这是猜的"（Codex 的做法：大上下文但只用 95%、工具输出 10KB 截断、不开推理）；
  - 费用标 `报告值` 或 `估算值`，账单对账只信前者。
- (经验) 对自部署模型，上下文不要用目录里的值，用运行时实际配置的值（vLLM 的 `max_model_len`、Ollama 的 num_ctx）。

### 决定 4：哪些活给小模型，中途换模型要做什么
- 小模型：
  - 给标题、摘要、分类、去重这类"做错了也不伤主流程"的活；
  - 调用时关 thinking、不存状态。
  - 工具选择、改代码、安全判断留在主模型。
- 中途换模型的清单：
  1. 新模型上下文更小、当前已经超了：先用旧模型压缩；
  2. 按推理块的绑定规则决定保留还是丢（Anthropic 看"模型 × 渠道"矩阵）；
  3. 工具 schema 按新厂商重新转换；
  4. 新模型不支持的模态换成文字占位；
  5. 插一条"换过模型"的说明，附新模型自己的指令；
  6. 接受这一轮缓存全部失效。

### 决定 5：自部署选哪个引擎
- 选项：vLLM、SGLang、llama.cpp（含 LM Studio 等基于它的工具）、Ollama。
- 代价：
  - vLLM / SGLang：吞吐和并发最好，parser 和推理开关最全，但要 GPU 和运维；不同版本 parser 有回归，要钉死版本。
  - llama.cpp：能跑 CPU 和小显卡，但模板识别失败会退回通用格式，KV 量化伤工具调用。
  - Ollama：上手最快，但默认上下文小、截断静默、并发默认 1、不支持有状态 Responses。
- 怎么选：
  - 多人并发的生产用 vLLM 或 SGLang，多副本时加缓存感知路由（llm-d 或 SGLang gateway），至少按会话粘性路由；
  - 单人本地开发用 Ollama 或 llama.cpp，但必须显式把上下文设到 64k 以上，并在网关检查截断。
  - 不论选哪个，上线前跑一遍 Kimi Vendor Verifier 那种验收：参数约束、多模态冒烟、长输出、工具调用触发率和 schema 准确率。

### 决定 6：网关怎么发现"想调工具但 tool_calls 为空"，并且失败关闭
- 选项：
  - A. 只信 `tool_calls` 字段；
  - B. 加启发式检查；
  - C. 用结构化输出强制（`tool_choice=required` 或 strict）。
- 代价：
  - A 会静默停掉；
  - B 可能误报（模型在正文里讨论工具调用格式时）；
  - C 只保证能解析不保证质量，第一次有编译延迟，而且有的 parser 不支持。
- 怎么选：B 必做，C 选做。B 的检查项：
  - `finish_reason` 为 tool_calls 但数组为空；
  - content 或 reasoning 里出现该模型的调用标记；
  - 参数不能按 JSON 解析，或不符合原 schema。
- 命中后：
  - 先原样重试一次；
  - 还不行就把错误回给模型（"你的工具调用没解析出来，请重新输出"）；
  - 不要当成"任务完成"。
- 同时记指标："finish_reason=tool_calls 的次数" 和 "成功解析的次数" 的比值，掉下去就报警（借 K2VV 的指标）。

### 决定 7：图片用 base64、URL 还是 file_id，缩到多大，旧截图怎么处理，上传文件谁来删
- 方式：
  - 一次性的图用 base64；
  - 多轮反复引用、或者体积大，用 Files API（只限支持的渠道：Anthropic 直连、OpenAI、Gemini）；
  - 只有图在公网并且厂商支持时才用 URL；
  - 要切 Bedrock / Vertex 的，统一退到 base64。
- 缩放：
  - Anthropic 按像素计费，先缩到当前档位上限（标准档 1568px）；
  - OpenAI 按 detail 档预算，自己缩放并记下比例，坐标换算回原图；
  - Gemini 每张固定 token，缩小省不了钱，只省传输。
  - 缩放要确定性（同图同字节），并告诉模型缩放了多少（Codex 的做法）。
- 旧截图：
  - 保留最近几张，更早的成批换成文字；
  - 盯住"20 张"这条线；
  - 用 `oversized_image:"error"` 让超限变成能看见的错误。
- 清理：
  - 上传时就设过期（OpenAI `expires_after`、Anthropic `expires_in_seconds`）；
  - 会话结束时删除；
  - 有定时任务扫孤儿文件；
  - 不接受外部传进来的 file_id。

### 决定 8：什么时候用厂商托管工具
- 选项：
  - A. 用厂商的网页搜索、代码执行、文件检索；
  - B. 自己实现成普通函数工具或 MCP。
- 代价：
  - A 省事、延迟低，但换厂商或换渠道就没了（Bedrock 上都没有），数据按厂商规则留存（容器状态、vector store 不在 ZDR 内），结果块是专有格式。
  - B 要自己做沙箱和搜索，但完全可迁移，数据自己掌握。
- 怎么选：
  - 原型期、单厂商、没有合规要求时用 A；
  - 需要多厂商降级、ZDR、HIPAA，或者要能审计数据去向的，用 B。
  - 混用时，降级路径上要能把托管工具换成自建版本，或者明确"降级时禁用"。

---

## 四、资料清单

**源码（最有价值：能看到别人踩过的每一个坑）**
- [opencode provider/transform.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts)：源码；各厂商消息修补（空文本、tool id 格式、Mistral 插消息、DeepSeek 推理字段、模态降级）、Gemini/Moonshot schema 清洗、小模型参数；一个文件就是一份"每家有什么怪规矩"的清单。
- [opencode provider/provider.ts](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/provider.ts)：源码；小模型选择顺序、Azure 部署名导致无法推断能力；短，看选模型逻辑。
- [Codex tools/json_schema.rs](https://github.com/openai/codex/blob/main/codex-rs/tools/src/json_schema.rs)：源码；schema 消毒（const→enum、补 type、删无用 $defs）；看等价改写怎么写。
- [Codex tools/json_schema/compaction.rs](https://github.com/openai/codex/blob/main/codex-rs/tools/src/json_schema/compaction.rs)：源码；超大 schema 的有损压缩顺序和 5000 字节阈值；少见的"schema 也要控制体积"的实现。
- [Codex models-manager/model_info.rs](https://github.com/openai/codex/blob/main/codex-rs/models-manager/src/model_info.rs)：源码；未知模型的兜底元数据和"猜的"标记；直接回答"未知模型给什么默认值"。
- [Codex models-manager/cache.rs](https://github.com/openai/codex/blob/main/codex-rs/models-manager/src/cache.rs)：源码；模型目录缓存 TTL、ETag、缓存 key 含凭证身份；目录缓存怎么做的样板。
- [Codex core/session/turn.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/session/turn.rs)：源码；换到小上下文模型前先用旧模型压缩（`maybe_run_previous_model_inline_compact`）；中途换模型的真实处理。
- [Codex context/model_switch_instructions.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/context/model_switch_instructions.rs)：源码；换模型后插入的 developer 提示；很短，看措辞。
- [Codex core/image_preparation.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/image_preparation.rs)：源码；图片失败换文字占位、缩放提示；"单张图失败不拖垮整轮"的做法。
- [Codex utils/image/lib.rs](https://github.com/openai/codex/blob/main/codex-rs/utils/image/src/lib.rs)：源码；detail 档位的像素和块上限、按摘要缓存的确定性重编码；图片预处理参数的参考值。
- [Goose agents/tool_schema_normalize.rs](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/tool_schema_normalize.rs)：源码；只做可证明等价的改写、区分 JSON Schema 草案版本；注释里有 Moonshot 拒绝和体积 9 倍的实测。
- [Goose providers/canonical_cost.rs](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/providers/canonical_cost.rs)：源码；价格来源优先级、缓存定价、报告值/估算值；成本模块怎么分层。
- [Goose providers/toolshim.rs](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/providers/toolshim.rs)：源码；用第二个模型从文字里抽工具调用；不支持原生工具的模型怎么接。
- [Vercel AI SDK normalize-openai-json-schema.ts](https://github.com/vercel/ai/blob/main/packages/openai/src/normalize-openai-json-schema.ts)：源码；有损删除发 warning、无法转换就抛错；"什么时候该报错"的明确实现。
- [pydantic-ai profiles/__init__.py](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/profiles/__init__.py)：源码；按模型的行为开关（强制工具与 thinking 的冲突、中途 system 消息怎么处理）；能力目录该有哪些"冲突类"字段。
- [pydantic-ai profiles/google.py](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/profiles/google.py)：源码；Gemini 内置工具和函数能否混用、thinking 参数分代；Gemini 专属差异。
- [Ollama server/prompt.go](https://github.com/ollama/ollama/blob/main/server/prompt.go)：源码；超长时从最旧消息开始静默丢、图片按 768 token 估；静默截断的直接证据。

**引擎文档（vLLM 文档站拦了抓取，读的是仓库里的源文件）**
- [vLLM docs/features/tool_calling.md](https://github.com/vllm-project/vllm/blob/main/docs/features/tool_calling.md)：官方文档；parser 开关、required/named 走结构化输出、auto 模式的严格程度、hf parser 限制、tool_choice=none 仍带工具；自部署工具调用必读。
- [vLLM docs/features/reasoning_outputs.md](https://github.com/vllm-project/vllm/blob/main/docs/features/reasoning_outputs.md)：官方文档；字段改名、工具调用不从推理段解析、各模型 thinking 默认值、开关方式；推理模型自部署必读。
- [vLLM docs/features/structured_outputs.md](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md)：官方文档；后端差异、旧参数删除、推理段内约束；结构化输出迁移和排查。
- [vLLM docs/serving/online_serving/openai_compatible_server.md](https://github.com/vllm-project/vllm/blob/main/docs/serving/online_serving/openai_compatible_server.md)：官方文档；generation_config.json 默认生效、额外参数；解释"为什么输出总被截断"。
- [vLLM docs/design/prefix_caching.md](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md)：设计文档；块哈希、哈希算法的多租户风险、cache_salt；自建多租户必读。
- [vLLM docs/configuration/optimization.md](https://github.com/vllm-project/vllm/blob/main/docs/configuration/optimization.md)：官方文档；抢占重算、显存和批大小参数；延迟抖动排查。
- [vLLM docs/serving/data_parallel_deployment.md](https://github.com/vllm-project/vllm/blob/main/docs/serving/data_parallel_deployment.md)：官方文档；内置负载均衡不看 KV cache；说明为什么要外加路由层。
- [vLLM docs/deployment/integrations/llm-d.md](https://github.com/vllm-project/vllm/blob/main/docs/deployment/integrations/llm-d.md)：官方文档；前缀感知路由、分层 KV、PD 分离；多副本缓存路由的入口。
- [SGLang tool_parser.mdx](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/tool_parser.mdx)：官方文档；parser 名字和 vLLM 不同、gpt-oss 和 DeepSeek 的特殊处理；在两个引擎之间迁移时对照。
- [SGLang sgl_model_gateway.mdx](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/sgl_model_gateway.mdx)：官方文档；cache_aware 路由、熔断、健康检查；自建网关的现成选项。
- [llama.cpp docs/function-calling.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)：官方文档；`--jinja`、通用格式回退、并行默认关、KV 量化警告；本地跑工具调用必读。
- [Ollama docs/context-length.mdx](https://github.com/ollama/ollama/blob/main/docs/context-length.mdx)：官方文档；按显存给的默认上下文、agent 建议 64k；配合 faq.mdx 看出文档自相矛盾。
- [Ollama docs/faq.mdx](https://github.com/ollama/ollama/blob/main/docs/faq.mdx)：官方文档；num_ctx、并发、排队、keep_alive；运维参数都在这。
- [Qwen 函数调用文档](https://qwen.readthedocs.io/en/latest/framework/function_call.html)：模型方文档；推荐的 parser 组合、推理模型别用停止词 ReAct；模型方和引擎方说法不一的证据。
- [HF transformers chat_extras](https://huggingface.co/docs/transformers/main/en/chat_extras)：官方文档；模板里 arguments 是字典、id 多为合成；自己拼模板时要知道。

**问题报告和第三方验证**
- [vLLM issue #53255](https://github.com/vllm-project/vllm/issues/53255)：issue；required 时 finish_reason=tool_calls 但数组为空；决定 6 的直接证据。
- [vLLM issue #39056](https://github.com/vllm-project/vllm/issues/39056)：issue；工具调用写进 `<think>` 被吞；推理 parser 和工具 parser 的冲突。
- [vLLM issue #50889](https://github.com/vllm-project/vllm/issues/50889)：issue；并发下 parser 偶发丢调用；说明这种问题单测发现不了。
- [Moonshot K2 Vendor Verifier](https://github.com/MoonshotAI/K2-Vendor-Verifier)：评测仓库；同一模型在各托管商和 vLLM/SGLang 上的工具调用准确率；选托管商和自部署验收的数据和方法。
- [Kimi Vendor Verifier 博客](https://www.kimi.ai/blog/kimi-vendor-verifier)：模型方博客；验收流程（参数约束→多模态冒烟→长输出→工具调用）和 API 层强制参数的原因；可以直接抄成上线清单。

**厂商文档：渠道、多模态、文件、留存**
- [Anthropic 扩展思考](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)：官方文档；thinking 与 tool_choice、缓存失效；推理块规则入口。
- [Anthropic thinking](https://platform.claude.com/docs/en/build-with-claude/thinking)：官方文档；thinking 块绑定前缀和账号、跨模型可读矩阵、追加式修改；换模型和改提示前必读。
- [Anthropic vision](https://platform.claude.com/docs/en/build-with-claude/vision)：官方文档；28px 块计费、两档分辨率、20 张图规则、各渠道大小限制；图片预处理参数的依据。
- [Anthropic Files API](https://platform.claude.com/docs/en/build-with-claude/files)：官方文档；workspace 范围可读、不适用 ZDR、过期设置、渠道不可用；文件清理和安全。
- [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock)：官方文档；端点、认证、功能缺失清单、区域加价；做云渠道降级前对照。
- [Claude on Vertex AI](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)：官方文档；请求格式差异、功能缺失、30MB 上限、区域加价；同上。
- [OpenAI images-vision](https://developers.openai.com/api/docs/guides/images-vision)：官方文档；detail 档位、low 不一定省、块上限、坐标换算；OpenAI 图片预处理依据。
- [OpenAI file-inputs](https://developers.openai.com/api/docs/guides/file-inputs)：官方文档；PDF 文本加图片、各文件类型的处理方式、大小限制；文档输入的成本来源。
- [OpenAI Files API 上传接口](https://developers.openai.com/api/reference/resources/files/methods/create)：API 参考；512MB/2.5TB、默认永久保留、`expires_after`；文件清理依据。
- [OpenAI your-data](https://developers.openai.com/api/docs/guides/your-data)：官方文档；各接口和托管工具的留存、ZDR 例外、CSAM 扫描、HIPAA 范围；托管工具合规决策的唯一一手来源。
- [Gemini Files API](https://ai.google.dev/gemini-api/docs/files)：官方文档；48 小时自动删、配额、100MB 内联上限；和另外两家相反的默认值。
- [Gemini media-resolution](https://ai.google.dev/gemini-api/docs/media-resolution)：官方文档；每张图固定 token、视频音频 PDF 计费；说明"先缩图"在 Gemini 上省不了钱。
- [Gemini 函数调用](https://ai.google.dev/gemini-api/docs/function-calling)：官方文档；schema 子集、工具数建议、内置工具混用、allowed_tools；Gemini schema 适配的依据。
- [Gemini 结构化输出](https://ai.google.dev/gemini-api/docs/structured-output)：官方文档；现已支持 `$ref`/anyOf，但仍是子集、复杂 schema 可能被拒；修正"Gemini 不支持 $ref"的旧印象。

- [深入理解 AI Agent：设计原理与工程实践 第 5、6 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md)：分析；二-16、8；第 5 章讲跨厂商接管轨迹时思考签名的处理，第 6 章（[链接](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter6.md)）「Computer Use」讲动作空间设计和视觉定位。

**兼容层的静默行为**
- [OpenRouter 托管商选择](https://openrouter.ai/docs/guides/routing/provider-selection)：官方文档；require_parameters 默认 false、价格加权均衡、量化过滤、ZDR 过滤；用聚合商时必须知道的默认值。
- [OpenRouter 推理 token](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)：官方文档；reasoning_details 原样回传、各模型档位；多厂商推理字段统一的参考。
- [DeepSeek thinking 模式](https://api-docs.deepseek.com/guides/thinking_mode)：官方文档；带 tools 必须回传推理、忽略的参数、effort 映射；"兼容接口不兼容"的典型。
- [LiteLLM drop_params](https://docs.litellm.ai/docs/completion/drop_params)：官方文档；不支持参数时报错还是静默删；网关配置决策。
- [Azure OpenAI API 版本生命周期](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle)：官方文档；v1 接口不再需要 api-version、model 填部署名；接 Azure 前看。

**能力和价格目录**
- [models.dev](https://github.com/anomalyco/models.dev)：开源数据仓库；模型能力、价格分档、推理字段名、限制；字段设计可以直接参考。
- [LiteLLM model_prices_and_context_window.json](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json)：数据文件；最全的能力和价格表，含弃用日期；注意 max_tokens 是含义模糊的旧字段。

---

## 五、阅读顺序

1. 先读 opencode `transform.ts`：一个小时就能知道各家有多少怪规矩，建立"每家都要修补"的直觉。
2. 再读 Anthropic thinking 页和 DeepSeek thinking 模式：理解推理内容为什么让"统一消息格式"变难。然后定决定 1。
3. 读 Vercel `normalize-openai-json-schema.ts` 和 Goose `tool_schema_normalize.rs`，再扫一眼 Codex 的 `json_schema.rs` / `compaction.rs`。然后定决定 2。
4. 读 models.dev 的 README 和 Codex `model_info.rs`、Goose `canonical_cost.rs`、pydantic-ai profiles。然后定决定 3。
5. 读 Codex `turn.rs` 里换模型压缩的那一段。然后定决定 4。
6. 要自部署的，按顺序读：
   - vLLM tool_calling.md → reasoning_outputs.md → 三个 issue（#53255、#39056、#50889）→ K2 Vendor Verifier 和 Kimi 博客。然后定决定 5、6。
   - 用 Ollama 或 llama.cpp 的，再读 `prompt.go`、context-length.mdx 和 llama.cpp function-calling.md。
   - 多副本部署再读 data_parallel_deployment.md、llm-d.md、SGLang gateway。
7. 做多模态的，读三家图片计费页（Anthropic vision、OpenAI images-vision、Gemini media-resolution），再看 Codex 的两个图片文件。然后定决定 7。
8. 最后读 OpenAI your-data、Anthropic Files API、Bedrock/Vertex 两页、OpenRouter 托管商选择。然后定决定 8，并回头检查 02 里的降级方案有没有用到云渠道缺的功能。
