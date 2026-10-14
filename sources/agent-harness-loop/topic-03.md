[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-03"></a>

## 3. 流式输出：先组装结果，再决定执行

<a id="protocol-006"></a>

### protocol-006 · Streaming API responses

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：Responses 流是语义类型事件，Chat Completions 是 delta；不能跨API复用同一文本拼接器作为完整解释器。

选读范围：Read the responses; Moderation risk。限制：动态文档，具体字段/默认值须按模型快照验证；未把厂商性能宣传作为独立测量结论。

[公开原文](https://developers.openai.com/api/docs/guides/streaming-responses)

<a id="protocol-007"></a>

### protocol-007 · Streaming messages

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：Messages 流是 message_start → 分索引的 block start/delta/stop → message_delta → message_stop，ping 与未知事件可能穿插；initial stop_reason 为 null。

选读范围：Event types; Content block delta types; Error recovery。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/streaming)

<a id="protocol-011"></a>

### protocol-011 · Fine-grained tool streaming

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：eager_input_streaming跳过服务端参数缓冲/JSON验证，降低首片延迟但拼完也可能非法。

选读范围：Accumulating tool input deltas; Handling invalid JSON。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

[公开原文](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming)

<a id="protocol-023"></a>

### protocol-023 · Responses API streaming response.function_call_arguments.done event missing function name

作者／组织：CarsonStevensAI; repository maintainers/comments。类型：公开问题讨论。版本／日期：2025-10-31T20:20:03Z; updated 2026-09-09T20:01:07Z。读取日：2026-10-13。

用途：2025年openai2.6.1用户发现function_call_arguments.done.name为空；维护者说明应按item_id找function-call item。

阅读范围：完整issue与维护者关闭说明。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/openai/openai-python/issues/2723)

<a id="protocol-024"></a>

### protocol-024 · Responses streaming: response.function_call_arguments.done events lack the required 'name' field, failing strict event-union validation

作者／组织：mecampbellsoup; repository maintainers/comments。类型：公开问题讨论。版本／日期：2026-07-05T21:10:38Z; updated 2026-09-08T18:45:24Z。读取日：2026-10-13。

用途：同一事件契约漂移会被宽松SDK掩盖：严格Pydantic union验证报大量错误，lenient fallback继续但类型标注误导用户。

阅读范围：issue reproduction; maintainer release comment。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/openai/openai-python/issues/3472)

<a id="protocol-025"></a>

### protocol-025 · Server tool input reconstruction missing in streaming

作者／组织：bexgboost; repository maintainers/comments。类型：公开问题讨论。版本／日期：2025-05-24T17:19:21Z; updated 2025-05-30T00:52:20Z。读取日：2026-10-13。

用途：非stream正常、stream最终server_tool_use.input却为空：SDK只累积client tool输入，API原始delta实际存在。

阅读范围：issue Investigation & Root Cause; maintainer fix link。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/954)

<a id="protocol-026"></a>

### protocol-026 · ServerToolResult not delivered when client tools interrupt the stream (code_execution + client tool concurrency)

作者／组织：agorski-comp; repository maintainers/comments。类型：公开问题讨论。版本／日期：2026-04-02T07:42:30Z; updated 2026-08-06T15:24:30Z。读取日：2026-10-13。

用途：真实混合server/client工具案例出现孤立server_tool_use，导致UI永久spinner和监控误报；用户曾伪造成功placeholder。

阅读范围：production traces; closing maintainer comment。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/1325)

<a id="protocol-033"></a>
<a id="protocol-audit-013"></a>

### protocol-033 · feat(api): correct function argument completion event fields (openapi-545)

作者／组织：markstuart-oai。类型：公开变更／提案。版本／日期：2a98f6a1dee448c6410531c89c2de0af4383c6a7。读取日：2026-10-13。 引用别名：protocol-audit-013（本组合计 1 项，关联文档与版本复核不另计）。

用途：稳定与beta模型均删除done事件name字段；真实修复调整类型契约，不制造API未给的字段。

选读范围：事件类型 diff：删除 function_call_arguments.done 中错误的 name 字段。限制：仅阅读与协议bug相关diff；release其他改动不作来源。

已读关联文档／版本（同一计数组）：
- protocol-033：2a98f6a1dee448c6410531c89c2de0af4383c6a7；范围：事件类型 diff：删除 function_call_arguments.done 中错误的 name 字段。[该记录原文](https://github.com/openai/openai-python/pull/3801)
- protocol-audit-013：merged commit 2a98f6a1dee448c6410531c89c2de0af4383c6a7；范围：PR 正文与实际 diff；补充复核，不新增计数。[该记录原文](https://github.com/openai/openai-python/pull/3801)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/openai/openai-python/pull/3801)

<a id="protocol-034"></a>

### protocol-034 · release: 0.52.2

作者／组织：stainless-app\[bot\]。类型：公开变更／提案。版本／日期：a1f61dd577cc78b2a4c26bc4eb80a875eca4aee6。读取日：2026-10-13。

用途：0.52.2引入TRACKS_TOOL_INPUT tuple同时覆盖client/server/MCP输入块，并增加枚举类型覆盖测试来防新block漏处理。

选读范围：0.52.2 的相关 diff：TRACKS_TOOL_INPUT 与 client / server / MCP 输入块累计测试。限制：仅阅读与协议bug相关diff；release其他改动不作来源。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/pull/960)

<a id="protocol-039"></a>

### protocol-039 · Streaming responses with tool calling

作者／组织：Ollama。类型：作者／团队实践或研究文章。版本／日期：2025-05-28。读取日：2026-10-13。

用途：Ollama旧实现缓冲完整生成再解析JSON；新实现识别模型模板前缀、暂存不完整前缀并增量输出。

选读范围：How tool parsing works in Ollama through Reference。限制：只读解析机制相关正文；32k等经验参数不提升为通用配置规则。

[公开原文](https://ollama.com/blog/streaming-tool)

<a id="protocol-045"></a>

### protocol-045 · ResponseStreamState implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：main accessed 2026-10-13; blob SHA 708de7b3d65f7eec8d9c088a4c3c1e011fc73681 (not a commit)。读取日：2026-10-13。

用途：响应累积按output_index索引保存item，再按content_index组装内容；不是把全部delta拼成一个字符串。

选读范围：src/openai/lib/streaming/responses/_responses.py lines 237–400。限制：仅读ResponseStreamState相关段落；blob哈希不是commit，不保证其对应某已发布SDK。

[公开原文](https://github.com/openai/openai-python/blob/main/src/openai/lib/streaming/responses/_responses.py)

<a id="protocol-046"></a>
<a id="protocol-audit-012"></a>

### protocol-046 · Chat stream helper implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob f9dec645b67383da62a688ce1c73eebf7607c553。读取日：2026-10-13。 引用别名：protocol-audit-012（本组合计 1 项，关联文档与版本复核不另计）。

用途：Chat辅助done事件从已累积tool_call.function.name构造；是SDK丰富后的事件，不是原始SSE格式。

选读范围：FunctionToolCallArgumentsDoneEvent 的构造分支。限制：[protocol-046](topic-03.md#protocol-046)同文件发行版复核。

已读关联文档／版本（同一计数组）：
- protocol-046：main accessed 2026-10-13; blob SHA 3476314f7f47a6924cad78d3176391e769233280 (not a commit)；范围：src/openai/lib/streaming/chat/_completions.py lines 343–497。[该记录原文](https://github.com/openai/openai-python/blob/main/src/openai/lib/streaming/chat/_completions.py)
- protocol-audit-012：v3.9.0; blob f9dec645b67383da62a688ce1c73eebf7607c553；范围：FunctionToolCallArgumentsDoneEvent 的构造分支；补充复核，不新增计数。[该记录原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/streaming/chat/_completions.py)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/streaming/chat/_completions.py)

<a id="protocol-048"></a>
<a id="runtime-boundaries-005"></a>

### protocol-048 · Anthropic Python v1.13.0 accumulated message helper

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.13.0 / b4b7916deaf4e5570cd627b1ae7ee4394a4de39f。读取日：2026-10-13。 引用别名：runtime-boundaries-005（本组合计 1 项，关联文档与版本复核不另计）。

用途：get_final_message消费到底后只assert已存在snapshot；snapshot在message_start即建立，未显式核查message_stop。因此应用不能把helper名中的final当作流完整性契约。

选读范围：get_final_message; accumulate_event message_start/message_delta。限制：限定 v1.13.0 的累计消息 helper；未独立运行完整 SDK 集成测试。

已读关联文档／版本（同一计数组）：
- protocol-048：main accessed 2026-10-13; blob SHA d036a04d1f96e0063fa9b7c7046b60750c874f11 (not a commit)；范围：src/anthropic/lib/streaming/_messages.py lines 341–537。[该记录原文](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/lib/streaming/_messages.py)
- runtime-boundaries-005：v1.13.0 / b4b7916deaf4e5570cd627b1ae7ee4394a4de39f；范围：get_final_message; accumulate_event message_start/message_delta；补充复核，不新增计数。[该记录原文](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/lib/streaming/_messages.py)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/lib/streaming/_messages.py)

<a id="protocol-053"></a>

### protocol-053 · IndexError in accumulate_event during Responses API streaming

作者／组织：openai/openai-python issue author。类型：公开问题讨论。版本／日期：2026-02-09; reported SDK 2.16.0。读取日：2026-10-13。

用途：用户在带web search、结构化输出和starting_after的Responses流中遇到output_index导致的IndexError，显示恢复流不一定符合简单连续list假设。

阅读范围：Issue body and reproduction。限制：开放issue，未找到与当前实现变更的明确修复关联；不宣称已修复或可稳定复现。

[公开原文](https://github.com/openai/openai-python/issues/2852)

<a id="protocol-056"></a>

### protocol-056 · AsyncChat.send_message_stream does not pass thought_signature with function calls

作者／组织：googleapis/python-genai reporter and maintainers。类型：公开问题讨论。版本／日期：2026-01-11; SDK 1.57.0 Gemini 3 Pro Preview Vertex。读取日：2026-10-13。

用途：用户给出两个callable的异步流工具循环复现，下一轮收到缺失thought_signature的400。

阅读范围：Issue reproduction with two callable functions and comments。限制：开放issue且无最终根因；不能把[protocol-064](topic-02.md#protocol-064)另一个用户的分组错误直接认定为本例原因。

[公开原文](https://github.com/googleapis/python-genai/issues/1938)

<a id="protocol-057"></a>

### protocol-057 · Streaming finish_reason stop for tool calls versus non-streaming tool_calls

作者／组织：googleapis/python-genai reporter and maintainers。类型：公开问题讨论。版本／日期：2026-08-17; Gemini OpenAI compatibility layer。读取日：2026-10-13。

用途：同请求只切换stream后，非流返回tool_calls，流式已发完整工具调用却以stop结束；原始curl排除了该报告中SDK转换的影响。

阅读范围：Raw curl request/non-streaming result and SSE transcript; maintainer escalation。限制：未解决报告，不据此断言所有Gemini版本都如此；不能用任意工具存在就覆盖安全终止原因。

[公开原文](https://github.com/googleapis/python-genai/issues/2868)

<a id="protocol-058"></a>

### protocol-058 · xAI tool calls return finishReason stop instead of tool-calls

作者／组织：Vercel AI SDK reporters and maintainers。类型：公开问题讨论。版本／日期：2026-02-03; reported ai 6.0.27 gateway 3.0.32; closed unable to reproduce。读取日：2026-10-13。

用途：最初问题部分涉及未提供execute导致SDK不自动续轮，工具执行策略与finishReason映射不是同一问题。

阅读范围：Initial report; execute-handler discussion; July maintainer retest。限制：不得引用为当前xAI确定故障；多报告版本、模型和中间层不同。

[公开原文](https://github.com/vercel/ai/issues/12218)

<a id="protocol-059"></a>

### protocol-059 · Tool execution does not respect unsafe finishReason values

作者／组织：Vercel AI SDK reporter and reproduction。类型：公开问题讨论。版本／日期：2026-08-19; ai 7.0.68 @ai-sdk/openai 4.0.43。读取日：2026-10-13。

用途：输入参数完整且有效时，length/error/content-filter/other等不安全终止仍可能触发自动工具执行，问题在终态门控而非JSON校验。

阅读范围：Issue reproduction; mock provider cases; maintainer/bot diagnosis。限制：为历史SDK bug，后续PR [protocol-061](topic-03.md#protocol-061)已合并；不要不分版本宣称当前SDK仍执行。

[公开原文](https://github.com/vercel/ai/issues/19063)

<a id="protocol-060"></a>

### protocol-060 · apply_patch_call never sets hasFunctionCall in OpenAI Responses adapter

作者／组织：Vercel AI SDK reporters and maintainers。类型：公开问题讨论。版本／日期：2026-09-07; reported @ai-sdk/openai 4.0.47/4.0.60。读取日：2026-10-13。

用途：新原生apply_patch_call已转换出工具项但未设hasFunctionCall，造成finishReason错报stop；消息分段与循环判定可因此不一致。

阅读范围：Issue body, initial closure, later fix/release comments。限制：未单独阅读后续修复PR；只将issue所列发布版本作为追查线索。

[公开原文](https://github.com/vercel/ai/issues/20427)

<a id="protocol-061"></a>
<a id="protocol-audit-014"></a>

### protocol-061 · Prevent automatic tool execution after unsafe model finish reasons

作者／组织：Vercel AI SDK。类型：公开变更／提案。版本／日期：merged a8285273ef8b4b2c36cf3cb692706da7f40077d4。读取日：2026-10-13。 引用别名：protocol-audit-014（本组合计 1 项，关联文档与版本复核不另计）。

用途：补丁集中引入isToolExecutionAllowedFinishReason，只允许stop或tool-calls驱动自动工具执行，并用于流式和非流式路径。

阅读范围：PR 19066 diff: shared helper, generateText, executeToolsFromStream and regression tests。限制：这是AI SDK的标准化终态执行策略，不是所有厂商原生枚举定义；安全授权仍是另一层。

已读关联文档／版本（同一计数组）：
- protocol-061：merged a8285273ef8b4b2c36cf3cb692706da7f40077d4；范围：PR 19066 diff: shared helper, generateText, executeToolsFromStream and regression tests。[该记录原文](https://github.com/vercel/ai/pull/19066)
- protocol-audit-014：merged; published ai@7.0.70；范围：PR 正文、实际 diff 与发行说明评论；补充复核，不新增计数。[该记录原文](https://github.com/vercel/ai/pull/19066)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/vercel/ai/pull/19066)

<a id="protocol-audit-015"></a>

### protocol-audit-015 · Published AI SDK streaming tool dispatch

作者／组织：Vercel AI SDK maintainers。类型：源码／仓库文档。版本／日期：ai@7.0.70; blob a02b49e8aeaade10d22fc23c625982e7addd6e7e。读取日：2026-10-13。

用途：批准后的client calls先入队，在model-call-end按终态允许后执行；providerExecuted调用不进入该execute分支。

选读范围：流式工具分派与 finishReason 门控分支。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。

[公开原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.ts)

[返回分类目录](README.md#topics)
