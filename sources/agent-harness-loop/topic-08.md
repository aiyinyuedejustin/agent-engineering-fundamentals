[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-08"></a>

## 8. 错误处理与恢复：什么时候能重试，什么时候先查结果

<a id="boundary-closure-005"></a>

### boundary-closure-005 · DynamoDB BatchWriteItem API contract

作者／组织：AWS。类型：官方文档／规范。版本／日期：current API reference, accessed 2026-10-13。读取日：2026-10-13。

用途：每项 Put/Delete 原子，整个 batch 不原子；已收到有效响应时只把 UnprocessedItems 作为下一批，并按退避处理。

选读范围：操作说明；UnprocessedItems；部分成功示例。限制：读操作说明、UnprocessedItems、部分成功示例；没有回包时不能凭此断定哪些项未处理，仍属结果未知。未调用真实服务。

[公开原文](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html)

<a id="boundary-closure-006"></a>

### boundary-closure-006 · Microsoft Graph JSON batching

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：page updated 2025-02-21。读取日：2026-10-13。

用途：外层 200 只代表 batch 可解析，逐项 status 才反映各请求结果；响应可乱序，须用 id 匹配。

选读范围：Creating a batch；Processing response；Sequencing；Batch size limitations。限制：读 Creating a batch、Processing response、Sequencing、Batch size limitations；batch 内 id 是相关标识，文档未承诺跨 batch 幂等；未调用服务。

[公开原文](https://learn.microsoft.com/en-us/graph/json-batching)

<a id="durable-orchestration-022"></a>

### durable-orchestration-022 · Transactional Execution - Beyond Durable Execution

作者／组织：Chuck Bear / DBOS。类型：作者／团队实践或研究文章。版本／日期：2024-04-11; historical @Transaction/@Communicator API。读取日：2026-10-13。

用途：只有当业务数据库变更和已执行记录在同一事务原子提交时，才可保证该数据库effect的单次提交；checkpoint和effect分离留下崩溃窗口。

阅读范围：Durable vs Transactional / distributed systems / numbered implementation;重复页面正文只计一次。限制：旧API命名；其邮件Message-ID普遍可去重说法过强，不应采纳为发送保证；事务仅覆盖同事务资源

[公开原文](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

<a id="human-control-011"></a>

### human-control-011 · Make turn/steer retries idempotent by clientUserMessageId

作者／组织：jalehman。类型：公开问题讨论。版本／日期：2026-07-10；open。读取日：2026-10-13。

用途：clientUserMessageId当时只是相关ID，提案要求同thread/ID/参数重试返回原结果、冲突参数报错并跨重启去重。

选读范围：issue全文及7月20评论。限制：feature request不是已发布契约；下游回声故障报告明确区分为OpenClaw归因，不能归给Codex生成

[公开原文](https://github.com/openai/codex/issues/32254)

<a id="human-control-034"></a>

### human-control-034 · Channel outbound: durable ingress, receipts and unknown sends

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current plugin SDK docs accessed 2026-10-13。读取日：2026-10-13。

用途：持久ingress按eventID和lane去重，admission顺序串行化避免异步append颠倒；持久提交失败应拒绝transport callback而非调度未落盘消息。

选读范围：durable ingress admission / delivery evidence / durable send / automatic reconciliation and stale completion sections。限制：文档不是所有adapter保证；pruned行后相同event可重新insert，isNew只是存储行新建；best_effort可能live-only

[公开原文](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

<a id="network-errors-001"></a>

### network-errors-001 · Timeouts, retries, and backoff with jitter

作者／组织：Marc Brooker / AWS。类型：作者／团队实践或研究文章。版本／日期：Builder Center republished 2026-06-12; original Builders Library article。读取日：2026-10-13。

用途：五层各做三次尝试会把底层故障负载放大至243倍；重试预算须在SDK、harness、代理和工具客户端之间统筹。

阅读范围：文章中的超时选择、多层重试放大、退避抖动、token bucket 及结果未知的讨论。限制：区域内部p99.9定时方法不可直接用于全球互联网；circuit breaker评价是AWS经验而非禁用规则。

[公开原文](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

<a id="network-errors-002"></a>

### network-errors-002 · Making retries safe with idempotent APIs

作者／组织：Malcolm Featonby / AWS。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：参数相同不等于业务意图相同；应由调用者提供稳定操作ID，而不是只hash参数去重。

选读范围：Client request ID、原子性、参数不匹配、迟到请求、保留期与语义等价响应的说明。限制：EC2保留期做法与服务资源生命周期绑定，不应复制为通用TTL。

[公开原文](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

<a id="network-errors-005"></a>

### network-errors-005 · Exponential Backoff And Jitter

作者／组织：Marc Brooker / AWS。类型：作者／团队实践或研究文章。版本／日期：2015-03-04; update 2023-05。读取日：2026-10-13。

用途：仅指数退避仍会形成同相重试波；Full/Equal/Decorrelated jitter在模拟中改善竞争负载，但工作量与完成时间有取舍。

阅读范围：full article, Introducing OCC / Adding Backoff / Adding Jitter。限制：数字来自OCC模拟，不能当作LLM API生产收益或三算法普遍排名。

[公开原文](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

<a id="network-errors-006"></a>

### network-errors-006 · Designing robust and predictable APIs with idempotency

作者／组织：Brandur Leach / Stripe。类型：作者／团队实践或研究文章。版本／日期：2017-02-22。读取日：2026-10-13。

用途：连不上、执行中断、已执行但响应丢失是不同失败窗口，后二者客户端通常无法判定业务是否成功。

阅读范围：full article, Planning for failure / Guaranteeing exactly once semantics。限制：文章exactly-once措辞依赖服务端幂等实现，不证明跨外部系统全局恰好一次。

[公开原文](https://stripe.com/blog/idempotency)

<a id="network-errors-014"></a>

### network-errors-014 · Anthropic #688: Overloaded error during LangChain streaming

作者／组织：Kevin-McIsaac; maintainer localden。类型：公开问题讨论。版本／日期：unknown。读取日：2026-10-13。

用途：维护者说明max_retries用于初始HTTP请求，不用于已输出token后的mid-stream error；异常必须包住迭代本身。

阅读范围：issue body and full timeline; maintainer comment 2026-04-28。限制：报告2024-10，维护者澄清2026-04；不等于所有provider均不支持resume。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/688)

<a id="network-errors-015"></a>
<a id="runtime-boundaries-002"></a>

### network-errors-015 · OpenAI Python v3.29.0 retry implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.29.0 / 7e1643a67322956ac81fc7d0c3f0f9161e2e5482。读取日：2026-10-13。 引用别名：runtime-boundaries-002（本组合计 1 项，关联文档与版本复核不另计）。

用途：有限Retry-After超过120秒在_should_retry中拒绝重试，优先于x-should-retry；不能只读退避计算函数声称它会提前重试。数值溢出用超过上限的有限sentinel保留拒绝。

选读范围：_parse_retry_after_header L812-848; _calculate_retry_timeout L861-883; _should_retry L885-927; constants MAX_RETRY_AFTER_DELAY=120。限制：限定 v3.29.0 所列重试分支；静态实现不等于所有请求路径或用户安装版本的运行证明。

已读关联文档／版本（同一计数组）：
- network-errors-015：main as read 2026-10-13; immutable Git blob 883bed6e19b9fd05126affe1e6ced56a309db164；范围：_parse_retry_after_header；_calculate_retry_timeout；_should_retry；SyncAPIClient.request。[该记录原文](https://github.com/openai/openai-python/blob/main/src/openai/_base_client.py)
- runtime-boundaries-002：v3.29.0 / 7e1643a67322956ac81fc7d0c3f0f9161e2e5482；范围：_parse_retry_after_header L812-848; _calculate_retry_timeout L861-883; _should_retry L885-927; constants MAX_RETRY_AFTER_DELAY=120；补充复核，不新增计数。[该记录原文](https://github.com/openai/openai-python/blob/7e1643a67322956ac81fc7d0c3f0f9161e2e5482/src/openai/_base_client.py)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/openai/openai-python/blob/7e1643a67322956ac81fc7d0c3f0f9161e2e5482/src/openai/_base_client.py)

<a id="network-errors-018"></a>

### network-errors-018 · Anthropic #1918: status 200 mid-stream errors

作者／组织：HardMax71。类型：公开问题讨论。版本／日期：unknown。读取日：2026-10-13。

用途：作者更正：原先fix已加入APIStatusError.type，保留HTTP200是设计；仍存在按exception class分类无法识别流内overload的差异。

阅读范围：issue body including correction and repro on0.122/1.4。限制：未合并提案不代表当前行为；作者撤回的最初指控不能照搬。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/1918)

<a id="network-errors-019"></a>

### network-errors-019 · Anthropic #1919: raw transport errors escape mid-stream

作者／组织：HardMax71。类型：公开问题讨论。版本／日期：unknown。读取日：2026-10-13。

用途：已建立stream后ReadTimeout/RemoteProtocolError曾绕过APIError类和发送层重试；报告区分异常包装与能否安全重试。

阅读范围：full body and timeline,2026-09-07/25。限制：当前main相关代码另核验于[network-errors-021](topic-07.md#network-errors-021)；跨项目修复状态不可相互推断。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/1919)

<a id="network-errors-020"></a>

### network-errors-020 · Anthropic #1470: truncation after server-side tool execution

作者／组织：ypang-anytimeai; dtmeadows-ant。类型：公开问题讨论。版本／日期：unknown。读取日：2026-10-13。

用途：报告38个content blocks后在工具input JSON片段中连接FIN；此前服务端脚本已成功运行，不能假定断流前工具全未执行。

阅读范围：full issue and maintainer reply2026-08-06。限制：是具体0.79.0beta运行的报告；不得泛化为稳定可重现服务缺陷或idle timeout。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/1470)

<a id="network-errors-036"></a>

### network-errors-036 · AI SDK #18668: attempt-isolated stream recovery

作者／组织：Vercel AI SDK maintainers / ai-sdk-factory。类型：公开问题讨论。版本／日期：ai 7.0.91 release announcement in issue, 2026-09-02。读取日：2026-10-13。

用途：重试失败model step而保留之前完成steps；开发迭代专门隔离失败attempt工具调用/审批/执行，避免重放副作用。

阅读范围：full issue and release timeline through2026-09-02。限制：这是项目设计/实现轨迹而非用户生产事故；现行官方error-handling文档再次核验。

[公开原文](https://github.com/vercel/ai/issues/18668)

<a id="network-errors-038"></a>

### network-errors-038 · AI SDK error handling and streaming recovery

作者／组织：Vercel。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：maxRetries与streamRetries分开；失败attempt工具缓冲到成功model-call finish才暴露/执行，早先完成steps不重做。

阅读范围：entire error-handling page。限制：安全性只覆盖SDK客户端工具隔离，不保证provider工具幂等或远程执行取消。

[公开原文](https://ai-sdk.dev/docs/ai-sdk-core/error-handling)

<a id="network-errors-040"></a>

### network-errors-040 · Claude API rate limits and spend-limit distinctions

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：RPM、输入TPM、输出TPM与短窗口突发、加速限制不同；只按一分钟平均流量节流仍可能429。

选读范围：正文前 2 万字符：Rate limits、acceleration limits、spend-limit errors 与 response headers。限制：只读限流机制、错误区别和headers，未逐项核对所有模型价格/额度表；模型额度和计费字段会变化。

[公开原文](https://platform.claude.com/docs/en/api/rate-limits)

<a id="network-errors-041"></a>

### network-errors-041 · Claude API errors

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：SSE可以在HTTP 200之后报错；日志仅以HTTP状态判断成功会丢失生成失败。

选读范围：HTTP errors; Error shapes; Request ID; Long requests; first 12k relevant characters reread。限制：阅读HTTP错误、错误体、request ID、长请求段；SDK typed exception建议须结合#1919的中途流异常版本边界。

[公开原文](https://platform.claude.com/docs/en/api/errors)

<a id="network-errors-042"></a>

### network-errors-042 · OpenAI rate limits guide

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：组织、项目和共享模型组都可能构成限流边界；换模型不一定换到独立额度池。

选读范围：正文前 2 万字符：limit scopes、shared limits、acceleration / overload 与 retry guidance。限制：读取限流层级、错误类别与重试建议；代码示例未逐个执行验证，历史示例不应直接复制。

[公开原文](https://developers.openai.com/api/docs/guides/rate-limits)

<a id="network-errors-043"></a>
<a id="protocol-audit-025"></a>

### network-errors-043 · LiteLLM reliability, retries and fallbacks

作者／组织：LiteLLM maintainers。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。 引用别名：protocol-audit-025（本组合计 1 项，关联文档与版本复核不另计）。

用途：Router可以先在模型组内重试再逐级fallback；外层loop若另有重试，会乘上这一预算。

选读范围：Retries/Timeout/Fallbacks; encrypted reasoning and encrypted_content_affinity; cooldown and fallback model IDs。限制：阅读前18k的重试/超时/cooldown/fallback状态段；加密状态处理是高风险实现断言，仍需固定版本代码和provider文档交叉核查。

已读关联文档／版本（同一计数组）：
- network-errors-043：live documentation as read 2026-10-13；范围：Retries/Timeout/Fallbacks; encrypted reasoning and encrypted_content_affinity; cooldown and fallback model IDs。[该记录原文](https://docs.litellm.ai/docs/proxy/reliability)
- protocol-audit-025：live 2026-10-13；范围：Fallback reasoning 兼容说明；补充复核，不新增计数。[该记录原文](https://docs.litellm.ai/docs/proxy/reliability)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.litellm.ai/docs/proxy/reliability)

<a id="network-errors-044"></a>
<a id="protocol-audit-034"></a>

### network-errors-044 · Provider selection controls

作者／组织：OpenRouter。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。 引用别名：protocol-audit-034（本组合计 1 项，关联文档与版本复核不另计）。

用途：require_parameters默认false不保证参数强制生效；data_collection、zdr和only/ignore控制不同边界。

选读范围：Provider selection：require_parameters、data_collection、ZDR 与 only/ignore。限制：Provider routing 旧地址重定向到此页；ZDR 对推理端点的筛选不自动覆盖工具后端，未审计第三方保留政策。

已读关联文档／版本（同一计数组）：
- network-errors-044：live documentation as read 2026-10-13；范围：Provider routing parameters; allow_fallbacks; require_parameters; data_collection; zdr; latency/throughput preferences; max_price。[该记录原文](https://openrouter.ai/docs/features/provider-routing)
- protocol-audit-034：live 2026-10-13；范围：Provider selection：require_parameters、data_collection、ZDR 与 only/ignore；补充复核，不新增计数。[该记录原文](https://openrouter.ai/docs/guides/routing/provider-selection)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://openrouter.ai/docs/guides/routing/provider-selection)

<a id="network-errors-045"></a>

### network-errors-045 · OpenRouter model fallbacks

作者／组织：OpenRouter。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：模型fallback与同模型provider路由是两层机制；响应实际model与计费对象可能改变。

阅读范围：Full original page, including models array, actual model field, Anthropic-compatible fallback constraints。限制：全页已读；与可靠性博客在“any error”措辞上存在范围差异，不据此推荐绕过内容过滤。

[公开原文](https://openrouter.ai/docs/guides/routing/model-fallbacks)

<a id="network-errors-047"></a>

### network-errors-047 · LiteLLM #27967: mid-stream fallback fails on unsupported assistant prefill

作者／组织：LiteLLM issue reporter and maintainers。类型：公开问题讨论。版本／日期：report on LiteLLM 1.83。读取日：2026-10-13。

用途：流中途失败后，把已有文本作为assistant prefill交给备选模型，可能因新模型不支持prefill而400；恢复机制会制造并掩盖第二个错误。

阅读范围：Issue body, proposed root cause, maintainer/reporter comments, linked PR reference。限制：全文含作者根因分析与评论已读；关联PR #36267不等于已核实发布修复，不采用作者关于安全机制的无证推断。

[公开原文](https://github.com/BerriAI/litellm/issues/27967)

<a id="network-errors-050"></a>

### network-errors-050 · LiteLLM #31067: fallback returns prose instead of tool calls

作者／组织：LiteLLM issue reporter。类型：公开问题讨论。版本／日期：LiteLLM 1.82.3 in report。读取日：2026-10-13。

用途：流中途fallback继续assistant文本，可能得到HTTP成功的普通解释而不是预期工具调用；协议成功不证明业务恢复成功。

阅读范围：Full issue body, version and described continuation construction。限制：全文读过但无独立复现实验；允许auto tool choice时无工具调用本身不必然错误，需明确测试意图与基线。

[公开原文](https://github.com/BerriAI/litellm/issues/31067)

<a id="network-errors-055"></a>
<a id="durable-orchestration-056"></a>

### network-errors-055 · OpenAI Agents #3852: retry rewind loses persisted user input

作者／组织：OpenAI Agents issue reporters and maintainers。类型：公开问题讨论。版本／日期：openai-agents-python 0.18.1 in report。读取日：2026-10-13。 引用别名：durable-orchestration-056（本组合计 1 项，关联文档与版本复核不另计）。

用途：本地SQLiteSession在重试回滚时删除已保存输入，而save-once标志没有复位，最终只留下assistant回复。

阅读范围：Issue body, independent reproducer, save_input-once and rewind analysis, linked PR。限制：全文与独立复现评论已读；关联修复PR #3857，不把本地session问题外推到所有后端。

已读关联文档／版本（同一计数组）：
- durable-orchestration-056：0.18.1; opened/closed2026-07-16 via3857；范围：issue mechanism0.18.1/repro roles; completed via3857；补充复核，不新增计数。[该记录原文](https://github.com/openai/openai-agents-python/issues/3852)
- network-errors-055：openai-agents-python 0.18.1 in report；范围：Issue body, independent reproducer, save_input-once and rewind analysis, linked PR。[该记录原文](https://github.com/openai/openai-agents-python/issues/3852)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/openai/openai-agents-python/issues/3852)

<a id="network-errors-056"></a>

### network-errors-056 · PydanticAI model clients, concurrency and FallbackModel

作者／组织：PydanticAI maintainers。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：provider拥有的HTTP client可由agent上下文管理；自传client由应用负责关闭，资源所有权要明确。

选读范围：HTTP client lifecycle; request concurrency; FallbackModel defaults, SDK retry interaction, response handlers and streaming limitation。限制：只读HTTP client lifecycle、concurrency limiter和FallbackModel相关子节；未读完整模型目录。

[公开原文](https://ai.pydantic.dev/models/overview/)

<a id="network-errors-057"></a>

### network-errors-057 · PydanticAI HTTP request retries

作者／组织：PydanticAI maintainers。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：HTTP transport重试位于模型不可见的底层；网络异常重试与基于HTTP状态的重试需要分别配置，后者依赖validator。

选读范围：Introduction; usage; wait strategy; retry transports; best practices; provider-specific behavior。限制：读介绍、主要用法、wait策略、transport和provider-specific限制；未逐行验证Tenacity wait代码，max_wait语义列入交叉审查。

[公开原文](https://ai.pydantic.dev/retries/)

<a id="network-errors-058"></a>

### network-errors-058 · OpenAI Agents model call timeouts and runner-managed retries

作者／组织：OpenAI Agents SDK maintainers。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：Runner retry opt-in不代表底层SDK不再重试；超时和预算需要把两层都计入。

选读范围：Model call timeouts; Runner-managed retries; Retry decisions and Safety boundaries; mixed provider behavior。限制：阅读Model call timeouts、Runner-managed retries及其Safety boundaries，未逐行独立核对实现；新契约需固定release复核。

[公开原文](https://openai.github.io/openai-agents-python/models/)

<a id="network-errors-060"></a>

### network-errors-060 · Stripe idempotent request contract, including v1/v2 distinction

作者／组织：Stripe。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：v1在执行开始后缓存状态码与响应体，包含500；同key重发不意味着会重新尝试执行直到成功。

阅读范围：Idempotent requests main section, cached failures, key pruning, validation/concurrency exceptions, API v2 behavior。限制：已完整读取幂等请求相关主节，未使用相邻include/metadata内容；Stripe具体行为不能直接外推其他工具服务。

[公开原文](https://docs.stripe.com/api/idempotent_requests)

<a id="network-errors-061"></a>

### network-errors-061 · AWS SDK retry behavior and adaptive limiter scope

作者／组织：AWS。类型：官方文档／规范。版本／日期：documented new behavior gated by AWS_NEW_RETRIES_2026=true。读取日：2026-10-13。

用途：文档新策略需要明确opt-in，不能写成所有已部署AWS SDK的默认行为；max_attempts包含首次请求，与max_retries不同。

选读范围：Feature opt-in banner; standard/adaptive modes; token buckets; maximum attempts; retryable errors; long-polling behavior。限制：读取前24k中模式、quota、计数、错误分类和long polling，末尾配额计算细节未完整审阅。

[公开原文](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)

<a id="network-errors-062"></a>

### network-errors-062 · OpenRouter streaming error and cancellation contracts

作者／组织：OpenRouter。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。

用途：SSE comment用于keepalive，不能当JSON；流前错误与首token之后的200流内错误需要不同处理。

选读范围：SSE comments; pre-token/mid-stream errors; cancellation support; generation IDs; API behavior。限制：阅读SSE、error handling、cancellation和API behavior相关段；provider支持列表会变，示例代码未运行，不直接照搬。

[公开原文](https://openrouter.ai/docs/api/reference/streaming)

<a id="practitioner-lessons-045"></a>

### practitioner-lessons-045 · The immortal life of Pi: Running the Pi coding agent on Temporal. | Temporal

作者／组织：Moe Abadi / Temporal。类型：作者／团队实践或研究文章。版本／日期：2026-10-08。读取日：2026-10-13。

用途：事实：Workflow将模型调用、工具调用和sealStep分成Activities；工具执行前落盘claim，有claim无结果视为结果未知而不自动重复。

阅读范围：Claims and tool outcome; sealStep; leases; what survives。限制：全文；实验性Pi/Temporal适配与杀worker演示不是生产SLA；交互UI本身崩溃仍需重开，持久性不等于任意副作用恰好一次。

[公开原文](https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal)

<a id="protocol-010"></a>
<a id="r3-loop-006"></a>

### protocol-010 · Stop reasons and fallback

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。 引用别名：r3-loop-006（本组合计 1 项，关联文档与版本复核不另计）。

用途：HTTP200仍可能是refusal、max_tokens、model_context_window_exceeded或pause_turn；stop_reason与网络异常须分层。

选读范围：Quick reference; empty end_turn; tool_use; pause_turn; Streaming considerations。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

已读关联文档／版本（同一计数组）：
- protocol-010：live documentation as accessed 2026-10-13；范围：Quick reference; empty end_turn; tool_use; pause_turn; Streaming considerations。[该记录原文](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)
- r3-loop-006：Live docs accessed 2026-10-14；范围：Quick reference；Empty responses with end_turn；max_tokens 与不完整工具块；stop_sequence；tool_use 开头；补充复核，不新增计数。[该记录原文](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)

<a id="protocol-audit-033"></a>

### protocol-audit-033 · Proposed disable_mid_stream_continuation option

作者／组织：LiteLLM maintainers。类型：公开变更／提案。版本／日期：closed, merged=false as read 2026-10-13。读取日：2026-10-13。

用途：这是给prefill不支持模型的规避选项提案；当前关闭但未合并，不能称修复已经发布。

选读范围：PR 正文及 diff；提案状态。限制：不要采用未合并参数作为现行可用接口。

[公开原文](https://github.com/BerriAI/litellm/pull/36267)

<a id="runtime-boundaries-016"></a>

### runtime-boundaries-016 · Pydantic AI v2.55.0 retry-after wait

作者／组织：Pydantic。类型：源码／仓库文档。版本／日期：v2.55.0 / 7db7a4d8c4b7b7b85b8636cf0b6e3305bafb5167。读取日：2026-10-13。

用途：与OpenAI的拒绝策略不同，wait_retry_after对秒数/日期明确min(server delay,max_wait)，会截短服务端时间；该helper不是全局deadline，也不等于最早时间保证。非可重放request body流重试会StreamConsumed。

选读范围：wait_retry_after L514-593; transport validator。限制：静态源码核验；需自定义stop/policy避免提前发

[公开原文](https://github.com/pydantic/pydantic-ai/blob/7db7a4d8c4b7b7b85b8636cf0b6e3305bafb5167/pydantic_ai_slim/pydantic_ai/retries.py)

<a id="runtime-boundaries-036"></a>

### runtime-boundaries-036 · OpenAI Agents v0.23.1 retry deadline implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v0.23.1 / c4a1d047b22488234b2ba81056e1b9b8db2127a5。读取日：2026-10-13。

用途：explicit decision.delay 先于 normalized retry_after，再是 default backoff（max_delay 仅限制此项）。stream deadline 在 while 每个 attempt 重置，sleep 在其外；故 model timeout 不是整个 run 总 deadline。

选读范围：_evaluate_retry L460-495; get_response_with_retry L585-683; stream_response_with_retry L713-891; companion src/agents/retry.py。限制：静态核验，未运行完整SDK测试；已核 tag→commit

[公开原文](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_internal/model_retry.py)

<a id="runtime-boundaries-058"></a>

### runtime-boundaries-058 · Fix retried Anthropic requests sending empty binary bytes

作者／组织：Pydantic。类型：公开变更／提案。版本／日期：released v2.55.0; d380fd30893475e425a9a53f80033e43b49ff46f。读取日：2026-10-13。

用途：同一请求对象可含已经读取到底的 BytesIO，retry序列化变成空image/PDF；修复预编码不可变base64字符串。真实SDK序列化+mock HTTP测试逐attempt比对相同非空wire bytes，说明仅assert调用次数不能验证重试正确。

选读范围：PR body; tests/models/anthropic/test_binary_content_retries.py; v2.55.0 release entry。限制：流式路径共用修复点，但作者明确无专门streaming regression test。

[公开原文](https://github.com/pydantic/pydantic-ai/pull/10014)

[返回分类目录](README.md#topics)
