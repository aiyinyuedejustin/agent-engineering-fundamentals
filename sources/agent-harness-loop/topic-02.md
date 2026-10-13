[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-02"></a>

## 2. Protocol 选择：模型接口与工具接入各管什么

<a id="human-control-008"></a>

### human-control-008 · Session Setup

作者／组织：Agent Client Protocol。类型：官方文档／规范。版本／日期：ACP v1 current 2026-10-13。读取日：2026-10-13。

用途：session/load须重播历史并在全部发送后响应，session/resume禁止历史重播，只恢复上下文和连接；能力需协商。

选读范围：Loading/Resuming/Closing Active Sessions/Additional Workspace Roots。限制：协议的工作根SHOULD不能当OS隔离；不表示所有ACP实现支持这些能力

[公开原文](https://agentclientprotocol.com/protocol/v1/session-setup)

<a id="practitioner-lessons-028"></a>

### practitioner-lessons-028 · MCP vs CLI: Benchmarking Tools for Coding Agents

作者／组织：Mario Zechner。类型：作者／团队实践或研究文章。版本／日期：2025-08-15。读取日：2026-10-13。

用途：事实：作者自制terminalcp的MCP/CLI等价接口，三任务×四工具×十重复；两种接口均成功，命令安全检查差异影响耗时/token。

选读范围：Building a CLI and MCP server; Designing evaluation; The Results; So MCP or CLI。限制：阅读前12000字符（工具设计/评测方法）及The Results至结尾；中段任务配置未逐项读；作者自认非科学评测，小样本且安全策略不同。

[公开原文](https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/)

<a id="practitioner-lessons-032"></a>

### practitioner-lessons-032 · Why we Built our own Cloud Agent Infrastructure

作者／组织：Gabe Pereyra / Harvey。类型：作者／团队实践或研究文章。版本／日期：2026-06-01。读取日：2026-10-13。

用途：事实（团队需求）：法律客户model路由还受保密/利益冲突允许列表约束；多provider兼容需同时正规化tool格式、stop、stream、sandbox与行为。

阅读范围：Law Firms; Zero Data Retention; Cost。限制：供应商当前能力断言截至2026-06；“持久化与ZDR互斥”仅指相应第三方边界，不等于客户自有合规存储不可持久。

[公开原文](https://www.harvey.ai/blog/why-we-built-our-own-cloud-agent-infrastructure)

<a id="practitioner-lessons-042"></a>

### practitioner-lessons-042 · Introducing Cline SDK: the upgraded agent runtime, and we rebuilt Cline upon it

作者／组织：Renee Huang / Cline。类型：作者／团队实践或研究文章。版本／日期：2026-05-13。读取日：2026-10-13。

用途：事实：从IDE内长大的runtime中拆出无状态核心loop、持久运行服务与provider层，让多个界面连接同一任务。

阅读范围：Stateless core; durable runtime; migration status。限制：全文；不能把开头重建宣传理解为所有客户端已迁移；厂商基准不作为普遍性能证明。

[公开原文](https://cline.bot/blog/introducing-cline-sdk-the-upgraded-agent-runtime)

<a id="practitioner-lessons-044"></a>

### practitioner-lessons-044 · Cline CLI & My Undying Love of Cline Core | Cline Blog

作者／组织：Andrei Eternal / Cline。类型：作者／团队实践或研究文章。版本／日期：2025-10-16。读取日：2026-10-13。

用途：事实：Node核心服务经gRPC连接多种UI，host-provider单独提供IDE诊断等能力，状态更新通过订阅传播。

阅读范围：Cline Core architecture; host providers; CLI subagents。限制：全文；版本限定，不能把路线图当当前跨端兼容事实。

[公开原文](https://cline.bot/blog/cline-cli-my-undying-love-of-cline-core)

<a id="protocol-001"></a>
<a id="protocol-audit-017"></a>

### protocol-001 · Function calling

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。 引用别名：protocol-audit-017（本条合计 1 项，各版本复核不另计）。

用途：工具调用只是模型提出的请求；执行与结果回传由应用完成，必须保留调用与结果之间的 call_id。

选读范围：Handling function calls; Strict mode; Streaming。限制：动态文档，具体字段/默认值须按模型快照验证；未把厂商性能宣传作为独立测量结论。

已读版本／别名（同一来源）：
- protocol-001：live documentation as accessed 2026-10-13；范围：Handling function calls; Strict mode; Streaming。[该版本原文](https://developers.openai.com/api/docs/guides/function-calling)
- protocol-audit-017：live 2026-10-13；范围：Strict mode 默认值与 Streaming 事件；补充复核，不新增计数。[该版本原文](https://developers.openai.com/api/docs/guides/function-calling)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://developers.openai.com/api/docs/guides/function-calling)

<a id="protocol-002"></a>

### protocol-002 · Migrate to the Responses API

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：迁移不只是更换 URL：Messages 变 Items，工具结果按 call_id 对应，结构化输出移到 text.format，流式消费改为按事件类型。

选读范围：Messages vs. Items; steps 2–7; common migration errors。限制：动态文档，具体字段/默认值须按模型快照验证；未把厂商性能宣传作为独立测量结论。

[公开原文](https://developers.openai.com/api/docs/guides/migrate-to-responses)

<a id="protocol-003"></a>

### protocol-003 · Reasoning models

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：max_output_tokens 包含推理、可见输出和非可见格式 token；达到上限可在任何可见文本之前返回 incomplete。

选读范围：Allocating space for reasoning; Preserve reasoning across calls; Keeping reasoning items in context; phase parameter； Reasoning summaries。限制：动态文档，具体字段/默认值须按模型快照验证；未把厂商性能宣传作为独立测量结论。

[公开原文](https://developers.openai.com/api/docs/guides/reasoning)

<a id="protocol-004"></a>

### protocol-004 · Conversation state

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：Responses 支持手工 item 回放、previous_response_id 链、durable conversation 对象三种状态持有方式。

选读范围：Manually manage conversation state; Passing context from previous response; Data retention。限制：动态文档，具体字段/默认值须按模型快照验证；未把厂商性能宣传作为独立测量结论。

[公开原文](https://developers.openai.com/api/docs/guides/conversation-state)

<a id="protocol-009"></a>

### protocol-009 · Extended thinking

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：manual thinking budget是目标值，max_tokens才是总输出硬上限；interleaved模式存在budget与max_tokens关系例外。

选读范围：Budget rules; Interleaved thinking; Turn structure in manual mode。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

<a id="protocol-013"></a>

### protocol-013 · Handle tool calls

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live docs as accessed 2026-10-13。读取日：2026-10-13。

用途：客户端tool_use用user角色tool_result回传，tool_use_id关联；结果可含text/image/document，不只是字符串。

选读范围：Handling results from client tools; Handling errors。限制：不同API与模型版本限制不可外推。

[公开原文](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)

<a id="protocol-014"></a>

### protocol-014 · Thinking in tool and multi-turn workflows

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live docs as accessed 2026-10-13。读取日：2026-10-13。

用途：单次tool-use loop算同一assistant turn，thinking配置应在turn间改变。

选读范围：The rules this walkthrough applies。限制：不同API与模型版本限制不可外推。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/thinking-tool-workflows)

<a id="protocol-015"></a>

### protocol-015 · OpenAI SDK compatibility

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live docs as accessed 2026-10-13。读取日：2026-10-13。

用途：兼容层忽略strict、response_format、reasoning_effort等参数，不报错不等于生效。

选读范围：Important compatibility limitations; Detailed API support; Error message compatibility。限制：不同API与模型版本限制不可外推。

[公开原文](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)

<a id="protocol-016"></a>

### protocol-016 · API versioning

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live docs as accessed 2026-10-13。读取日：2026-10-13。

用途：固定API版本仍允许新输出值/枚举变体/stream event，严格穷尽枚举且遇未知崩溃不是向前兼容。

选读范围：Versioning guarantees; Version history。限制：不同API与模型版本限制不可外推。

[公开原文](https://platform.claude.com/docs/en/api/versioning)

<a id="protocol-017"></a>
<a id="protocol-audit-006"></a>

### protocol-017 · Thought signatures (generateContent)

作者／组织：Google。类型：官方文档／规范。版本／日期：2026-09-04。读取日：2026-10-13。 引用别名：protocol-audit-006（本条合计 1 项，各版本复核不另计）。

用途：Gemini3严格验证当前turn每step的首个functionCall签名，平行调用只有第一个携带；旧turn不作同样验证。

选读范围：Signatures in function calling parts; FAQs; Thought signatures for different models。限制：不同API与模型版本限制不可外推。

已读版本／别名（同一来源）：
- protocol-017：2026-09-04；范围：Signatures in function calling parts; FAQs; Thought signatures for different models。[该版本原文](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures)
- protocol-audit-006：page updated 2026-09-04；范围：Thought signatures：签名保留与 Content 分组规则；补充复核，不新增计数。[该版本原文](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures)

<a id="protocol-018"></a>
<a id="protocol-audit-005"></a>

### protocol-018 · Function calling (generateContent)

作者／组织：Google。类型：官方文档／规范。版本／日期：2026-10-09。读取日：2026-10-13。 引用别名：protocol-audit-005（本条合计 1 项，各版本复核不另计）。

用途：当前接口支持按function_call id映射结果，完整Part及签名不能随意合并；扫描全部parts找调用，不能假设最后一个必为functionCall。

选读范围：Managing conversation history manually; Parallel function calling; Automatic function calling; Notes and limitations。限制：同页工具结果顺序表述冲突，待实现核对；不能据此声称任意消息顺序皆可。

已读版本／别名（同一来源）：
- protocol-018：2026-10-09；范围：Managing conversation history manually; Parallel function calling; Automatic function calling; Notes and limitations。[该版本原文](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)
- protocol-audit-005：live 2026-10-13；范围：Function calling：调用与结果匹配、并行调用；补充复核，不新增计数。[该版本原文](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)

<a id="protocol-020"></a>

### protocol-020 · OpenAI compatibility

作者／组织：Google。类型：官方文档／规范。版本／日期：2026-09-02。读取日：2026-10-13。

用途：reasoning_effort映射到Gemini thinking_level/budget并非同一语义刻度；某些模型无法none关闭。

选读范围：Thinking; Enable Gemini features with extra_body; Current limitations。限制：不同API与模型版本限制不可外推。

[公开原文](https://ai.google.dev/gemini-api/docs/openai)

<a id="protocol-021"></a>

### protocol-021 · Interactions API overview

作者／组织：Google。类型：官方文档／规范。版本／日期：2026-10-09。读取日：2026-10-13。

用途：Interaction是含thought/tool/result/model_output的step序列；get还含user_input而create仅模型生成step，二者不是完全同形历史。

选读范围：How Interactions API works; Server-side state; Limitations。限制：不同API与模型版本限制不可外推。

[公开原文](https://ai.google.dev/gemini-api/docs/interactions-overview)

<a id="protocol-022"></a>

### protocol-022 · Gemini thinking (Interactions)

作者／组织：Google。类型：官方文档／规范。版本／日期：2026-10-09。读取日：2026-10-13。

用途：thought block可只有signature没有summary，不能按summary非空决定保存；signature流在step.stop前最后delta。

选读范围：Thought summaries; Streaming with thinking; Token limits; Thought signatures。限制：不同API与模型版本限制不可外推。

[公开原文](https://ai.google.dev/gemini-api/docs/thinking)

<a id="protocol-027"></a>

### protocol-027 · Google Vertex: Reasoning `thoughtSignature` is not included when AI SDK throws `AI_InvalidToolInputError`

作者／组织：eddieconk; repository maintainers/comments。类型：公开问题讨论。版本／日期：2025-11-24T19:38:47Z; updated 2026-07-22T12:46:03Z。读取日：2026-10-13。

用途：AI SDK验证工具参数失败的异常分支丢了providerMetadata，虽然先前tool-input事件有签名，最终invalid tool-call没保留，续回合400。

阅读范围：issue reproduction; reporter event trace; maintainer reproduction。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/vercel/ai/issues/10560)

<a id="protocol-028"></a>

### protocol-028 · @ai-sdk/google-vertex drops thoughtSignature in multi-step tool calls due to namespace desync

作者／组织：buibaoanh; repository maintainers/comments。类型：公开问题讨论。版本／日期：2026-02-08T19:23:54Z; updated 2026-07-22T11:40:48Z。读取日：2026-10-13。

用途：Google Vertex providerOptions fallback读取google配置但继续从vertex命名空间找签名，跨命名空间转换导致第二步失败。

阅读范围：root cause and versions; issue closed。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/vercel/ai/issues/12351)

<a id="protocol-031"></a>

### protocol-031 · Gemini function/tool calls not executing automatically

作者／组织：KaiquanMah; repository maintainers/comments。类型：公开问题讨论。版本／日期：2025-05-26T09:33:35Z; updated 2025-06-24T03:38:38Z。读取日：2026-10-13。

用途：把FunctionDeclaration传给SDK只是给模型描述；传callable才允许Python automatic function calling执行。

阅读范围：report and Google maintainers replies。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/googleapis/python-genai/issues/859)

<a id="protocol-032"></a>

### protocol-032 · Interactions API: cannot combine built-in tools with function calling on gemini-3.6-flash / gemini-3.5-flash-lite — server requires tool_config.include_server_side_tool_invocations, but interactions.create() provides no way to set it

作者／组织：rizwankce; repository maintainers/comments。类型：公开问题讨论。版本／日期：2026-07-22T09:36:19Z; updated 2026-07-23T05:55:14Z。读取日：2026-10-13。

用途：google-genai2.11–2.13报告Interactions混合内建/自定义工具触发服务端要求一个Interactions根本不接受的flag。

阅读范围：report; independent reproduction 2026-07-22; maintainer bug acknowledgement。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/googleapis/python-genai/issues/2761)

<a id="protocol-035"></a>

### protocol-035 · Armin is wrong and here's why

作者／组织：Mario Zechner。类型：作者／团队实践或研究文章。版本／日期：2025-11-22。读取日：2026-10-13。

用途：作者将opaque状态视为客户端需echo的服务端数据，认为跨provider必有损而非可由CRDT消除。

阅读范围：Where's your state sync problem at?; Switching providers; Armin is right actually。限制：一手经验/观点，不能用其2025年API可用性描述替代2026年规范；两位作者对同步问题抽象持不同看法。

[公开原文](https://mariozechner.at/posts/2025-11-22-armin-is-wrong/)

<a id="protocol-037"></a>

### protocol-037 · LLM APIs are a Synchronization Problem

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2025-11-22。读取日：2026-10-13。

用途：作者亲历Responses状态难恢复，提出应明确canonical state、derived cache与transport，而不是只统一消息表面形状。

阅读范围：Completion API; Responses API; State Sync API。限制：一手经验/观点，不能用其2025年API可用性描述替代2026年规范；两位作者对同步问题抽象持不同看法。

[公开原文](https://lucumr.pocoo.org/2025/11/22/llm-apis/)

<a id="protocol-038"></a>

### protocol-038 · Why we built the Responses API

作者／组织：OpenAI。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：Responses以有序、不同类型的Item表达文本、推理与工具动作，避免Chat中把内容和工具调用并入同一message后丢失顺序。

选读范围：v1/responses is an agentic loop; Moving up the stack; Preserving reasoning safely。限制：读完相关设计正文，未细读代码；文章内自有benchmark不视为跨系统普遍性能结论。

[公开原文](https://developers.openai.com/blog/responses-api)

<a id="protocol-040"></a>

### protocol-040 · Tool Calling - vLLM

作者／组织：vLLM。类型：官方文档／规范。版本／日期：latest documentation accessed 2026-10-13。读取日：2026-10-13。

用途：tool_choice调用义务、工具封装语法约束和参数schema约束是不同能力，受解析器、模板、strict与服务器配置共同影响。

选读范围：Tool Calling through Llama: named/required/none, constrained decoding, strict, hf/Mistral parsers。限制：未读全页全部模型解析器；latest浮动，未固定发布版本，不能推广具体模型限制。

[公开原文](https://docs.vllm.ai/en/latest/features/tool_calling/)

<a id="protocol-041"></a>

### protocol-041 · Chat templates

作者／组织：Hugging Face。类型：官方文档／规范。版本／日期：Transformers current documentation; v5.19.0 linked。读取日：2026-10-13。

用途：消息会变成模型特定控制token，同一基础模型的不同微调版也可能需要不同模板。

选读范围：Using apply_chat_template; add_generation_prompt; continue_final_message。限制：读全页解释正文，未逐行阅读所有示例；只描述文档所述Transformers行为。

[公开原文](https://huggingface.co/docs/transformers/en/chat_templating)

<a id="protocol-042"></a>

### protocol-042 · Using the Messages API

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current documentation accessed 2026-10-13。读取日：2026-10-13。

用途：Messages无状态调用要显式提供会话历史，可用合成assistant消息构造上下文。

选读范围：Basic request/response; multiple conversational turns; system and prefill guidance。限制：已读主要解释正文，示例代码未逐行读；新功能支持模型名单需独立更新。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)

<a id="protocol-043"></a>

### protocol-043 · Generating content: GenerateContentResponse and Content types

作者／组织：Google。类型：官方文档／规范。版本／日期：v1beta API reference accessed 2026-10-13。读取日：2026-10-13。

用途：被拦截的prompt可能没有candidate，promptFeedback与candidate终止原因应分别解释；finishReason缺失表示尚未终止。

选读范围：GenerateContentResponse; Candidate; FinishReason; Content; Part; FunctionCall; FunctionResponse。限制：大型参考页仅读列出的类型，不将Live/Interactions与generateContent混用；模型和模式支持范围需另核。

[公开原文](https://ai.google.dev/api/generate-content)

<a id="protocol-044"></a>

### protocol-044 · openai-python helpers.md

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：main accessed 2026-10-13。读取日：2026-10-13。

用途：SDK parse方法要求strict工具，并可在length或content_filter结束时抛异常，不能与create返回行为混同。

选读范围：Structured Outputs Parsing through Chat Completions Streaming events。限制：未读Assistants和Beta Agents部分；main辅助文档与具体安装版本可能不同。

[公开原文](https://github.com/openai/openai-python/blob/main/helpers.md)

<a id="protocol-047"></a>

### protocol-047 · Google Gen AI chat histories and streaming automatic function calling

作者／组织：Google。类型：源码／仓库文档。版本／日期：main accessed 2026-10-13; blob SHA 9b4088ad238d64e905efd47b2d283fe9ad0924ea (not a commit)。读取日：2026-10-13。

用途：SDK同时维护comprehensive和curated history，默认展示历史可能含无效/空模型轮，而实际下一请求只使用有效历史。

选读范围：google/genai/chats.py lines 39–185 and 437–583。限制：只读同步streaming与基础历史逻辑；不把当前实现等同所有SDK或异步路径。

[公开原文](https://github.com/googleapis/python-genai/blob/main/google/genai/chats.py)

<a id="protocol-050"></a>
<a id="protocol-audit-023"></a>

### protocol-050 · Mistral parallel template role validation

作者／组织：vLLM maintainers。类型：源码／仓库文档。版本／日期：v0.10.0; blob 2ef4bedf862114ddba1074b0cef234e5b2a0cb91。读取日：2026-10-13。 引用别名：protocol-audit-023（本条合计 1 项，各版本复核不另计）。

用途：交替校验先去首system并过滤tool/tool_results和有tool_calls字段的消息；不是API通用交替公理。

选读范围：角色检查与 tool ID 渲染分支。限制：[protocol-050](topic-02.md#protocol-050)同文件版本复核；未安装Jinja执行模板。

已读版本／别名（同一来源）：
- protocol-050：main accessed 2026-10-13; blob SHA 2ef4bedf862114ddba1074b0cef234e5b2a0cb91 (not a commit)；范围：examples/tool_chat_template_mistral_parallel.jinja all 94 lines。[该版本原文](https://github.com/vllm-project/vllm/blob/main/examples/tool_chat_template_mistral_parallel.jinja)
- protocol-audit-023：v0.10.0; blob 2ef4bedf862114ddba1074b0cef234e5b2a0cb91；范围：角色检查与 tool ID 渲染分支；补充复核，不新增计数。[该版本原文](https://github.com/vllm-project/vllm/blob/v0.10.0/examples/tool_chat_template_mistral_parallel.jinja)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/vllm-project/vllm/blob/v0.10.0/examples/tool_chat_template_mistral_parallel.jinja)

<a id="protocol-051"></a>

### protocol-051 · Create a Message - Claude API Reference

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current API reference accessed 2026-10-13。读取日：2026-10-13。

用途：连续user或assistant消息会被合并成单个turn，直接反驳所有厂商都严格交替的规则。

选读范围：messages input contract; role enumeration; thinking/redacted block types; system。限制：只读输入、角色和thinking类型相关段落；system冲突不能靠本页单独定论。

[公开原文](https://platform.claude.com/docs/en/api/messages/create)

<a id="protocol-054"></a>
<a id="protocol-audit-024"></a>

### protocol-054 · AI SDK Responses history conversion

作者／组织：Vercel AI SDK maintainers。类型：源码／仓库文档。版本／日期：ai@7.0.70; blob dc6307e8fab0c0175048a41cd959b725906748a2。读取日：2026-10-13。 引用别名：protocol-audit-024（本条合计 1 项，各版本复核不另计）。

用途：会话/previous-response已知项去重、function_call与call_id、reasoning引用有不同规则。

选读范围：工具调用、结果与 reasoning 的历史转换分支。限制：[protocol-054](topic-02.md#protocol-054)同文件发行版复核；不把当前main新增保护反投射到旧tag。

已读版本／别名（同一来源）：
- protocol-054：main accessed 2026-10-13; blob SHA b7585d55c45e635ede03d29223c15de81d6b0448 (not a commit)；范围：lines 710–766, 927–990, 1254–1362, 1807–1833。[该版本原文](https://github.com/vercel/ai/blob/main/packages/openai/src/responses/convert-to-openai-responses-input.ts)
- protocol-audit-024：ai@7.0.70; blob dc6307e8fab0c0175048a41cd959b725906748a2；范围：工具调用、结果与 reasoning 的历史转换分支；补充复核，不新增计数。[该版本原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/openai/src/responses/convert-to-openai-responses-input.ts)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/openai/src/responses/convert-to-openai-responses-input.ts)

<a id="protocol-055"></a>

### protocol-055 · Invalid signature in thinking block when replaying history

作者／组织：anthropics/anthropic-sdk-python reporter and maintainer。类型：公开问题讨论。版本／日期：2026-05-23; reported Claude 4.x gateway history。读取日：2026-10-13。

用途：维护者明确签名不会因时间自然过期，排查应看文本/签名被改写、块重排或合并以及模型切换，而非默认TTL过期。

阅读范围：Issue body; maintainer dtmeadows-ant comment 5192744619。限制：报告仍开放；不同模型的当前兼容/丢弃规则见[protocol-063](topic-02.md#protocol-063)，旧建议不覆盖所有新模型。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/1598)

<a id="protocol-063"></a>
<a id="protocol-audit-004"></a>

### protocol-063 · Thinking

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current docs accessed 2026-10-13; binding beta 2026-08-01。读取日：2026-10-13。 引用别名：protocol-audit-004（本条合计 1 项，各版本复核不另计）。

用途：工具使用回合内必须保存thinking，跨回合推荐保留，而工具使用之外可以省略过去thinking；不能概括为所有块永远原样回传。

选读范围：Thinking with tool use; preserving blocks; interleaved/preserved thinking; model preservation; encryption; redaction。限制：动态规则受模型与账户生效条件约束；保留、绑定及默认丢弃行为不可跨版本推断。专门规则另见 [protocol-audit-001](topic-02.md#protocol-audit-001)；未实测全部 API 组合。

已读版本／别名（同一来源）：
- protocol-063：current docs accessed 2026-10-13; binding beta 2026-08-01；范围：Thinking with tool use; preserving blocks; interleaved/preserved thinking; model preservation; encryption; redaction。[该版本原文](https://platform.claude.com/docs/en/build-with-claude/thinking)
- protocol-audit-004：live 2026-10-13；范围：Thinking：模型、账户和功能兼容条件；补充复核，不新增计数。[该版本原文](https://platform.claude.com/docs/en/build-with-claude/thinking)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/thinking)

<a id="protocol-064"></a>
<a id="protocol-audit-009"></a>

### protocol-064 · Parallel function thought_signature report with author self-correction

作者／组织：googleapis/js-genai reporter peterbherman and maintainers。类型：公开问题讨论。版本／日期：2026-01-23; @google/genai 1.38 Vertex Gemini 3 Flash Preview; author correction April。读取日：2026-10-13。 引用别名：protocol-audit-009（本条合计 1 项，各版本复核不另计）。

用途：作者最初归因服务端并行调用缺签名，后更正为自己把同响应的多个functionCall parts拆成独立model Content，令每一段都变成需要首签名的新步骤。

阅读范围：Issue body and author correction comment 4316663989。限制：这是一个明确归因的客户侧实例，不证明所有缺签名400都是同类错误，也不能代替不同API的结果顺序规则。

已读版本／别名（同一来源）：
- protocol-064：2026-01-23; @google/genai 1.38 Vertex Gemini 3 Flash Preview; author correction April；范围：Issue body and author correction comment 4316663989。[该版本原文](https://github.com/googleapis/js-genai/issues/1275)
- protocol-audit-009：author correction comment 4316663989；范围：原始问题与作者更正评论 4316663989；补充复核，不新增计数。[该版本原文](https://github.com/googleapis/js-genai/issues/1275)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/googleapis/js-genai/issues/1275)

<a id="protocol-audit-001"></a>

### protocol-audit-001 · Preserved thinking

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。

用途：前缀、模型可读性、账户绑定是三类检查；其错误/丢弃行为不同，不能合称签名过期。

选读范围：Preserved thinking：前缀、模型可读性、账户绑定与裁剪规则。限制：动态模型/平台兼容表，仅截至读取日；不同账户和模型的实测未做。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)

<a id="protocol-audit-007"></a>

### protocol-audit-007 · Interactions function calling

作者／组织：Google。类型：官方文档／规范。版本／日期：page updated 2026-09-23。读取日：2026-10-13。

用途：Interactions stateless history以user_input/thought/function_call/function_result steps回放；并不是generateContent Content/Part结构。

选读范围：function_result 与 parallel function calling 示例。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。

[公开原文](https://ai.google.dev/gemini-api/docs/function-calling)

<a id="protocol-audit-026"></a>

### protocol-audit-026 · LiteLLM encrypted-content affinity implementation

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。

用途：先从编码id/密文或bridge块提取origin，完全无marker时直接返回候选pool。

选读范围：加密 reasoning 的亲和性键与匹配实现。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router_utils/pre_call_checks/encrypted_content_affinity_check.py)

<a id="tools-security-045"></a>

### tools-security-045 · SyntaxError in stdio deserializeMessage when handling MCP server tool calls

作者／组织：karmiy and bhosmer-ant / MCP TypeScript SDK。类型：公开问题讨论。版本／日期：2025-03-31; maintainer response 2025-10-06。读取日：2026-10-13。

用途：console.log 的调试字符串污染 stdio JSON-RPC 通道，引发 parse error；报告者最初误以为反序列化器应兼容普通文本。

阅读范围：article body。限制：不是 SDK 已确认的解析 bug；是用法错误及维护者纠正。

[公开原文](https://github.com/modelcontextprotocol/typescript-sdk/issues/244)

<a id="tools-security-062"></a>

### tools-security-062 · MCP 2026-07-28 Key Changes

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。

用途：移除initialize握手和协议session，以每请求元数据、server/discover、显式业务handle替代；跨请求身份不能靠连接状态。

阅读范围：Major changes; Minor changes; Deprecated。限制：此来源是规范差异，不证明SDK或产品已实现；旧2025来源保留历史版本标记。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

[返回分类目录](README.md#topics)
