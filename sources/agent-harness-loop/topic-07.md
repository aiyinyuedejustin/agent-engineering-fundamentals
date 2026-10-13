[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-07"></a>

## 7. 网络：请求究竟卡在哪一层

<a id="network-errors-003"></a>

### network-errors-003 · Timeouts - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：HTTPX默认5秒是网络无活动超时；read timeout约束等待下一chunk，不是总响应耗时。

阅读范围：默认网络无活动超时，以及 connect / read / write / pool 四类配置的说明。限制：这里描述HTTPX原生默认；OpenAI等SDK会覆盖默认值。

[公开原文](https://www.python-httpx.org/advanced/timeouts/)

<a id="network-errors-004"></a>

### network-errors-004 · Resource Limits - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：连接总数、可保留空闲连接数与空闲到期时间分别配置；当前文档默认100、20、5秒。

阅读范围：连接总量、空闲连接数与 keep-alive 到期配置的正文。限制：默认值具版本性；HTTP/2的多路复用还需另核验。

[公开原文](https://www.python-httpx.org/advanced/resource-limits/)

<a id="network-errors-007"></a>

### network-errors-007 · Async Support - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：不要在hot loop里反复新建AsyncClient，否则失去连接池收益。

阅读范围：full page, Opening and closing clients / Streaming responses。限制：共享范围必须兼容实际事件循环与客户端生命周期，不能随意跨loop复用。

[公开原文](https://www.python-httpx.org/async/)

<a id="network-errors-008"></a>

### network-errors-008 · Proxies - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：live documentation/main as read 2026-10-13; publication date unknown。读取日：2026-10-13。

用途：HTTPS目标的代理URL通常仍为http://，因为先连HTTP代理再CONNECT隧道并TLS握手。

阅读范围：full page, HTTP Proxies / FORWARD vs TUNNEL。限制：特定代理可能支持HTTPS-to-proxy，须按部署验证。

[公开原文](https://www.python-httpx.org/advanced/proxies/)

<a id="network-errors-009"></a>

### network-errors-009 · Environment Variables - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：live documentation/main as read 2026-10-13; publication date unknown。读取日：2026-10-13。

用途：默认读取HTTP_PROXY/HTTPS_PROXY/ALL_PROXY/NO_PROXY以及SSL_CERT_FILE/SSL_CERT_DIR；trust_env=False改变整组环境配置。

阅读范围：full page。限制：不能把禁用trust_env当成绕过企业网络策略的方法。

[公开原文](https://www.python-httpx.org/environment_variables/)

<a id="network-errors-010"></a>

### network-errors-010 · Transports - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：live documentation/main as read 2026-10-13; publication date unknown。读取日：2026-10-13。

用途：HTTPTransport(retries=N)仅重试ConnectError/ConnectTimeout，不涵盖读写错误或503。

阅读范围：full page, HTTP Transport / ASGI startup and shutdown / Mock transports。限制：本文混有不同代际custom transport示例；仅依赖明确描述的语义。

[公开原文](https://www.python-httpx.org/advanced/transports/)

<a id="network-errors-011"></a>

### network-errors-011 · SSL - HTTPX

作者／组织：HTTPX maintainers。类型：官方文档／规范。版本／日期：live documentation/main as read 2026-10-13; publication date unknown。读取日：2026-10-13。

用途：证书验证失败会成为ConnectError；默认certifi信任包可替换为显式SSLContext或系统信任库。

阅读范围：full page。限制：诊断结论是loop工程推论；不可把所有SSL错误都认作证书配置问题。

[公开原文](https://www.python-httpx.org/advanced/ssl/)

<a id="network-errors-012"></a>

### network-errors-012 · OpenAI Python SDK README

作者／组织：OpenAI / Stainless。类型：官方文档／规范。版本／日期：live documentation/main as read 2026-10-13; publication date unknown。读取日：2026-10-13。

用途：当前README已默认HTTPX2；默认重试2次，包含连接错误、408、409、429及5xx，timeout默认10分钟。

选读范围：README Handling errors / Request IDs / Retries / Timeouts / with_streaming_response / HTTPX2 migration。限制：仅阅读相关README节，SDK默认不能推断其他语言或旧版本。

[公开原文](https://github.com/openai/openai-python)

<a id="network-errors-013"></a>

### network-errors-013 · Claude Python SDK configuration

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation/main as read 2026-10-13; publication date unknown。读取日：2026-10-13。

用途：当前文档默认httpx，2次重试及10分钟timeout；stream helper累积最终消息，而create(stream=True)仅提供事件迭代。

选读范围：extracted page sections Handling errors through Long requests。限制：已读至Long requests等相关章节，不将静态网页视为特定安装版本保证。

[公开原文](https://platform.claude.com/docs/en/api/sdks/python)

<a id="network-errors-016"></a>

### network-errors-016 · OpenAI #3828: read timeout multiplied by retries

作者／组织：sakshamyadav090; marcuswood-oai。类型：公开问题讨论。版本／日期：openai-python 2.54.0; httpx 0.28.1。读取日：2026-10-13。

用途：故障注入中timeout=30,max_retries=2总等待91.6秒；维护者确认这是每attempt timeout加退避的预期行为。

阅读范围：full issue and maintainer reply 2026-09-09。限制：报告环境openai 2.54.0/httpx0.28.1；量值是作者可复现报告，未独立重跑。

[公开原文](https://github.com/openai/openai-python/issues/3828)

<a id="network-errors-017"></a>

### network-errors-017 · OpenAI #3969: unmapped TLS transport exception regression

作者／组织：FarzamMohammadi; marcuswood-oai。类型：公开问题讨论。版本／日期：openai-python 3.14.1 regression; reporter confirmed fix in 3.20.0。读取日：2026-10-13。

用途：3.14.1缩窄异常捕获以保留应用异常后，未被httpcore2映射的ssl.SSLError逃过网络重试；agent并发评测出现失败。

阅读范围：full issue, reproduction and maintainer/reporter confirmation 2026-09-28/30。限制：事故为特定版本；不能把已修复故障描述为当前普遍问题。

[公开原文](https://github.com/openai/openai-python/issues/3969)

<a id="network-errors-021"></a>
<a id="runtime-boundaries-004"></a>

### network-errors-021 · Anthropic Python v1.13.0 raw streams

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.13.0 / b4b7916deaf4e5570cd627b1ae7ee4394a4de39f。读取日：2026-10-13。 引用别名：runtime-boundaries-004（本条合计 1 项，各版本复核不另计）。

用途：发布版message_stop只是可yield事件，不立即break；底层等待transport EOF。SSE error通过_make_status_error构造，但迭代transport异常没有类似OpenAI显式包装。finally关闭，解释器finalizing时sync路径仅标记closed。

选读范围：_iter_events; __stream__; message_stop allowed events; SSE error branch。限制：限定 v1.13.0 底层 stream 的所读分支；不能把底层迭代器与高层累计消息 helper 的返回时机混为一谈。

已读版本／别名（同一来源）：
- network-errors-021：main as read 2026-10-13; immutable Git blob 45db64b21dbd5d338450792e23e71e233519ce97；范围：src/anthropic/_streaming.py（第 1–230 行）。[该版本原文](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/_streaming.py)
- runtime-boundaries-004：v1.13.0 / b4b7916deaf4e5570cd627b1ae7ee4394a4de39f；范围：_iter_events; __stream__; message_stop allowed events; SSE error branch；补充复核，不新增计数。[该版本原文](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/_streaming.py)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/_streaming.py)

<a id="network-errors-022"></a>

### network-errors-022 · OpenAI #2722: meta-only SSE JSONDecodeError

作者／组织：c4milo; fanaticalfishing。类型：公开问题讨论。版本／日期：reports on openai-python 2.6.1 and 2.37.0。读取日：2026-10-13。

用途：代理插入不带data的retry/id等SSE字段导致JSON解析失败；生产复现显示慢模型活到keepalive到达才触发，所以看似模型相关。

阅读范围：full issue incl production report2026-05-19。限制：报告涵盖2.6.1/2.37.0；不要把提议patch或issue open状态当成当前main未修证明。

[公开原文](https://github.com/openai/openai-python/issues/2722)

<a id="network-errors-023"></a>

### network-errors-023 · WHATWG HTML Server-sent events

作者／组织：WHATWG。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：UTF-8及CR/LF/CRLF逐行解析，空行分事件；EOF前不完整事件应丢弃，空data buffer不发浏览器message。

选读范围：original9.2.1–9.2.7; living standard2026-10-12。限制：浏览器EventSource处理模型不等于所有SDK POST流行为；实读9.2.1–9.2.7。

[公开原文](https://html.spec.whatwg.org/multipage/server-sent-events.html)

<a id="network-errors-024"></a>

### network-errors-024 · NGINX HTTP proxy module

作者／组织：NGINX。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：response buffering默认on，可由X-Accel-Buffering控制但也可被忽略；buffering off立即转发数据。

选读范围：2 lines169–180,624–654,819–826,891–904,931–938。限制：只读buffering/read/send timeout/next upstream相关节；部署版本及全路径配置必须现场验证。

[公开原文](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

<a id="network-errors-025"></a>

### network-errors-025 · Cloudflare Error524

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：documentation updated 2026-07-23。读取日：2026-10-13。

用途：524说明已成功连origin但读取或写入阶段超时；当前页读125秒、写30秒，长工作建议状态轮询等架构处理。

选读范围：full support article。限制：当前文档2026-07-23，数值会变化且存在不同套餐/服务例外；非所有524都是相同阶段。

[公开原文](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/error-524/)

<a id="network-errors-031"></a>

### network-errors-031 · HTTPX #3782: double cancellation leaks active connections

作者／组织：BenjaminChoou; FriendlyPasser; amasen02。类型：公开问题讨论。版本／日期：httpx 0.28.1; httpcore 1.0.9 in report。读取日：2026-10-13。

用途：两次Task.cancel之间yield导致连接清理中断，反复后池active数增长直到PoolTimeout；独立本地服务器复现。

选读范围：body and comments2026-09-16/23。限制：实读body/repro/关键timeline，完整重复日志未全读；0.28.1/httpcore1.0.9等特定组合，修复PR另待核验。

[公开原文](https://github.com/encode/httpx/issues/3782)

<a id="network-errors-032"></a>

### network-errors-032 · OpenAI #1059: reused async client hangs

作者／组织：robert-foley; dumbPy; RobertCraigie。类型：公开问题讨论。版本／日期：2024 report; resolution comment identifies httpcore 1.0.3。读取日：2026-10-13。

用途：复用AsyncOpenAI跑多批gather出现连接/持续timeout；维护者最终指向httpcore1.0.3包含clean-state-cancellations修复。

选读范围：issue body/repro plus final comment1944343209。限制：2024旧版本事故已修；原始repro含多次asyncio.run，不能由此得出应每请求重建client。

[公开原文](https://github.com/openai/openai-python/issues/1059)

<a id="network-errors-034"></a>

### network-errors-034 · AI SDK #17310: chunk timeout counts tool execution

作者／组织：yonatan-shorani; Vercel maintainers。类型：公开问题讨论。版本／日期：ai 7.0.28 in report。读取日：2026-10-13。

用途：ai7.0.28立即输出tool-call后300ms工具被150ms chunk timer误杀；文档所称流空闲与实际pipeline范围不一致。

阅读范围：full issue and timeline; current docs crosscheck network-errors-037。限制：当前settings已区分范围，stepMs仍刻意覆盖tools；旧bug报告提案不能替代现行契约。

[公开原文](https://github.com/vercel/ai/issues/17310)

<a id="network-errors-037"></a>

### network-errors-037 · AI SDK settings timeout contract

作者／组织：Vercel。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：totalMs覆盖all steps，stepMs累积generation/retries/local tools；firstChunkMs/chunkMs只认content-bearing输出，不被metadata/empty/raw activity重置。

选读范围：maxRetries/abortSignal/timeout full sections。限制：现行站点文档而非所有旧ai版本；仅相关timeout/retry章节。

[公开原文](https://ai-sdk.dev/docs/ai-sdk-core/settings)

<a id="network-errors-048"></a>

### network-errors-048 · LiteLLM #19184: stream_timeout scope regression

作者／组织：LiteLLM issue reporter and maintainers。类型：公开问题讨论。版本／日期：comparison of LiteLLM 1.79.3 and 1.80.13。读取日：2026-10-13。

用途：同名stream_timeout从等待首chunk的预期变为截断整个流，健康但耗时5秒的流在2秒时失败。

阅读范围：Issue body/reproducer and author confirmation; linked fix PR。限制：全文与关键确认已读；issue关闭并关联PR #19191，未独立验证修复发布版本。

[公开原文](https://github.com/BerriAI/litellm/issues/19184)

<a id="network-errors-049"></a>

### network-errors-049 · LiteLLM timeout contracts and streaming keep-alive

作者／组织：LiteLLM maintainers。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：router全局timeout、部署stream_timeout和pass-through请求timeout分别可能约束全调用、首chunk、后续chunk，不能根据名字推断。

阅读范围：Global/per-model timeouts; pass-through streaming timeout; SSE keep-alive before upstream response。限制：全页相关段已读；first chunk不严格等于模型第一个有意义token，且需与#19184版本分开。

[公开原文](https://docs.litellm.ai/docs/proxy/timeout)

<a id="network-errors-051"></a>

### network-errors-051 · Codex #43140: response.failed error delayed until SSE EOF

作者／组织：Codex issue reporter。类型：公开问题讨论。版本／日期：Codex 0.153.4; commit 3d2ee51ca2d5db578f328aa75e20aa22c0197c9a。读取日：2026-10-13。

用途：已收到response.failed后仍等待EOF，若连接继续保持，idle timeout会覆盖真正的终态错误和重试提示。

选读范围：正文前 2 万字符：process_sse 终态错误处理、复现与回归表。限制：阅读主体、复现表与修复说明，未完整审阅补丁；作者明确没有证明线上Azure停顿都由此导致。

[公开原文](https://github.com/openai/codex/issues/43140)

<a id="network-errors-052"></a>

### network-errors-052 · Claude Code #78529: runtime DNS differs from working curl

作者／组织：Claude Code issue reporters。类型：公开问题讨论。版本／日期：Claude Code 2.1.212 and 2.1.220 reports。读取日：2026-10-13。

用途：同机curl/dig可用而内嵌运行时解析失败：报告涉及resolv.conf注释处理，以及依赖NSS resolved但无nameserver条目的系统。

阅读范围：Issue body plus independent reproducer comment covering Bun resolver, NSS and zero-nameserver behavior。限制：正文和独立长复现评论已读；底层根因是报告者分析，未核实上游修复，不建议读者绕过网络/安全设置。

[公开原文](https://github.com/anthropics/claude-code/issues/78529)

<a id="network-errors-053"></a>

### network-errors-053 · OpenAI #3440: SSE DONE closes reusable HTTP connections

作者／组织：OpenAI Python issue reporter。类型：公开问题讨论。版本／日期：openai-python 2.44.0; references earlier cleanup change 6132922c。读取日：2026-10-13。

用途：应用层\[DONE\]早于HTTP chunked传输结束；立即退出并关闭可导致已成功请求的连接不能回池。

选读范围：Issue body, DONE versus HTTP chunk terminator discussion, reproducer。限制：阅读正文、根因与复现；没有确认当前main是否已修复。与#43140不是相互否定，而是两层终止的张力。

[公开原文](https://github.com/openai/openai-python/issues/3440)

<a id="network-errors-054"></a>
<a id="runtime-boundaries-001"></a>

### network-errors-054 · PR 3510: post-DONE drain rejected

作者／组织：openai/openai-python。类型：公开变更／提案。版本／日期：closed unmerged 2026-09-23。读取日：2026-10-13。 引用别名：runtime-boundaries-001（本条合计 1 项，各版本复核不另计）。

用途：PR已关闭未合并；维护者承认排空有助连接复用，但等待开放连接及取消处理中断清理增添风险，倾向传输层优化；HTTPX2 2.13.0修复的是async generator cleanup异常，不是连接复用。

选读范围：PR state + maintainer closing comment 5787052387。限制：该 PR 已关闭且未合并；维护者讨论排空与清理的取舍，不据此认定 SDK 已采用该补丁。

已读版本／别名（同一来源）：
- network-errors-054：open PR/revision discussion as read; revision c8e39cbc4abf4aaeda3c55f187569d03731a1bda；范围：PR 正文与 c8e39cbc4abf4aaeda3c55f187569d03731a1bda 修订的 review。[该版本原文](https://github.com/openai/openai-python/pull/3510)
- runtime-boundaries-001：closed unmerged 2026-09-23；范围：PR state + maintainer closing comment 5787052387；补充复核，不新增计数。[该版本原文](https://github.com/openai/openai-python/pull/3510)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/openai/openai-python/pull/3510)

<a id="network-errors-059"></a>

### network-errors-059 · aiohttp connector, DNS cache and graceful shutdown

作者／组织：aiohttp maintainers。类型：官方文档／规范。版本／日期：stable documentation as read 2026-10-13。读取日：2026-10-13。

用途：连接池总量与每host上限不同，connector所有权与DNS缓存TTL也独立；自定义resolver可能走不同解析路径。

选读范围：Connectors and ownership; limiting pool/per-host connections; DNS cache/resolver; Graceful Shutdown。限制：只读Connectors、DNS cache、SSL和Graceful Shutdown章节；未推断所有运行时共享相同问题。

[公开原文](https://docs.aiohttp.org/en/stable/client_advanced.html)

<a id="runtime-boundaries-003"></a>

### runtime-boundaries-003 · OpenAI Python v3.29.0 streaming core

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.29.0 / 7e1643a67322956ac81fc7d0c3f0f9161e2e5482。读取日：2026-10-13。

用途：该已发布版将stream迭代transport timeout/request异常映射到SDK错误；\[DONE\]后break并finally close，不执行PR3510提议排空。底层Stream本身没有要求响应终态出现，故正常EOF不等于语义成功。

选读范围：Stream._iter_events/__stream__; AsyncStream equivalents; SSEDecoder。限制：静态源码核验；未运行完整SDK集成测试

[公开原文](https://github.com/openai/openai-python/blob/7e1643a67322956ac81fc7d0c3f0f9161e2e5482/src/openai/_streaming.py)

<a id="runtime-boundaries-006"></a>

### runtime-boundaries-006 · AI SDK 7.0.91 stream retry and timeout implementation

作者／组织：Vercel。类型：源码／仓库文档。版本／日期：ai@7.0.91 / 79b4ab869b38c5c702bc3a3bf055254b74648759。读取日：2026-10-13。

用途：streamRetries 省略关闭流内重试。shouldBufferToolParts 仅 streamRetries&gt;0 或显式设置 streamRetries 且有 onError 时为真；重试时丢弃该attempt工具/审批缓冲，先前完成steps保留。

选读范围：stream-text.ts 第 625–654、2198–2278、2440–2705 行；相关 stream-text.test.ts 第 3179–3370 行（静态阅读）。限制：静态源码核验；未运行完整SDK集成测试

[公开原文](https://github.com/vercel/ai/blob/79b4ab869b38c5c702bc3a3bf055254b74648759/packages/ai/src/generate-text/stream-text.ts)

[返回分类目录](README.md#topics)
