# 02 · 网络与可靠性：重试、超时、限流、幂等

> 范围：agent 调模型 API、调外部工具时，网络出错、限流、超时、重试、幂等、并发、降级这一整块。
> 各章讲到重试的地方都以这一章为准。具体数字（默认重试次数、响应头名、超时值）都在 2026-10-09 对照原文或 SDK 源码核对过；厂商文档会改，用之前再核对一次。

---

## 一、知识拆解

### 1. 错误分类：先判断"这个错重试有没有用"

**1.1 状态码只是第一层，要看错误体里的 type/code**
- 同一个 429 可能是"发太快了"（等一会就好），也可能是"钱用完了 / 到了月度上限"（重试一万次也没用）。OpenAI 的 429 里，`error.code` 为 `credit_balance_exhausted`、`organization_spend_limit_exceeded`、`project_spend_limit_exceeded`、`organization_usage_limit_exceeded` 这几种都不能靠重试恢复，文档原话是 Don't retry quota, billing。
- Anthropic 到达档位月度消费上限时也返回 429 `rate_limit_error`，但**不带 `retry-after`**，`error.details.error_code` 是 `enforced_spend_limit_reached`；而你自己设的消费上限触发时返回的是 **400** `invalid_request_error`。只看状态码就会写错分支。
- 坑：SDK 默认会对 429 重试，所以额度用光时 SDK 仍会白白重试 2 次再报错。业务层要按 code 分流：限流类进退避队列，额度类直接告警停机。

**1.2 各状态码在 LLM 场景的实际含义（已核对的部分）**
- 400：参数/格式问题，不重试。Anthropic 还把"你自设的消费上限到了"也放在 400；还有一类很常见的 400 是会话历史不合规（比如回传的 thinking 块被改过），这类是代码 bug，重试没用。
- 401 / 403：key 错、被吊销、IP 不在白名单、地区不支持。不重试，直接告警。
- 402：Anthropic 的 `billing_error`（付款信息问题）。Gemini 文档也把 402 列为不要重试。
- 404：资源不存在（模型名写错、resource id 过期）。不重试。
- 408：请求超时。官方 Python SDK（openai / anthropic）都会重试。
- 409：Anthropic 定义为 `conflict_error`（并发修改资源）；两家 SDK 源码里注释写的是 "Retry on lock timeouts"，默认重试。
- 413：请求体太大。Anthropic Messages API 上限 32 MB、Batch API 256 MB，而且是 Cloudflare 在请求到达 API 服务器前就拒掉的——所以你看到的可能不是标准 JSON 错误体，解析代码要容错。
- 422：OpenAI Python SDK 映射为 `UnprocessableEntityError`。
- 429：限流。按 `Retry-After` 等待，没有就指数退避加抖动。
- 500：服务端内部错误，退避重试，持续出现就带上 request-id 找支持。
- 503：OpenAI 用 `service_unavailable_error` / `server_is_overloaded` 表示"模型容量不够"（和 429 slow_down 区分开了）。注意 OpenAI 文档专门写了：以前有些端点 slow_down 也返回 503，后来改成 429，所以错误处理代码要同时兼容新旧两种。
- 504：Anthropic 的 `timeout_error`，官方建议长请求改用流式。
- 529：Anthropic 专有的 `overloaded_error`，表示全局高负载，不是你一个人超了。

**1.3 SDK 把哪些错当作"可重试"**
- openai-python 和 anthropic-sdk-python 的 `_should_retry` 逻辑基本一样（都是 Stainless 生成的）：先看非标准响应头 `x-should-retry`（true/false 直接服从），再对 408、409、429、>=500 重试；连接错误、超时也重试。
- 也就是说 SDK 不读错误体。429 额度耗尽、500 里的确定性 bug，它都会照样重试。

### 2. 退避、抖动、Retry-After

**2.1 指数退避一定要加抖动**
- 只有退避没有抖动，大量客户端会在同一时刻一起重试，形成一波波尖峰。AWS 那篇文章用模拟对比了 Full Jitter、Equal Jitter、Decorrelated Jitter，结论是不加抖动的方案"明显最差"，Full Jitter 总调用量最少。
- 抖动不只用于重试：AWS Builders' Library 建议所有定时任务、周期性任务都加抖动，否则多台机器会在整分钟/零点对齐打爆下游。

**2.2 SDK 里的具体参数（源码确认）**
- 两家 Python SDK：`DEFAULT_MAX_RETRIES = 2`（即最多 3 次尝试）、`INITIAL_RETRY_DELAY = 0.5` 秒、`MAX_RETRY_DELAY = 8.0` 秒；延迟 = `min(0.5 * 2^n, 8)`，再乘以 `1 - 0.25*random()`，即只往下抖 0–25%。这种抖动幅度比 Full Jitter 小得多，并发很高时你自己的外层调度要再打散。
- Retry-After 处理：先读非标准的 `retry-after-ms`，再读 `retry-after`（秒数或 HTTP 日期）。**openai-python 只接受不超过 120 秒（`MAX_RETRY_AFTER_DELAY = 2 * 60`）的服务端延迟；超过就干脆不重试，把原始错误抛给你**；anthropic-python 则照单全收（只封顶到系统 sleep 上限）。同一类代码换个厂商，行为不一样。
- 每次重试带请求头 `x-stainless-retry-count`，排查时能在服务端看到这是第几次。
- Gemini 官方 Python SDK：文档写的是默认最多重试 4 次，初始约 1 秒，最大 60 秒。

**2.3 Retry-After 是"最少等多久"，不是"到点就一定成功"**
- RFC 9110 定义了 `Retry-After`（可以是秒数或日期）；OpenAI 文档明确说把它当最小值，再加一点随机延迟。
- 坑：Anthropic 的 `anthropic-ratelimit-*-reset` 是 RFC 3339 时间戳，OpenAI 的 `x-ratelimit-reset-*` 是 `1s`、`6m0s` 这种时长字符串，解析器要分开写。

**2.4 退避只能削短时尖峰，削不了长时间过载**
- Marc Brooker《What is Backoff For?》：退避只把工作往后推，并不减少总工作量。客户端数量没有上限时（每个请求都开一个协程/线程就等于客户端无上限），每个请求各自退避对长时间过载几乎没用；只有"数量有限、串行发请求"的客户端（比如固定数量的 worker 拉队列）退避才真正减负。
- 推论：agent 服务里"每个用户请求一个协程，各自重试各自退避"，过载时退避基本白做，必须配合全局重试预算或令牌桶重试。

**2.5 RESOURCE_EXHAUSTED 不一定能重试**
- Google AIP-194 把 `RESOURCE_EXHAUSTED` 列为"一般不要自动重试"：它可能表示配额用完，几个小时内重试都不会成功，还可能产生费用；`CANCELLED` 和 `DEADLINE_EXCEEDED` 则是"必须尊重、不能自动重试"。Gemini 的 429 用的正是 `RESOURCE_EXHAUSTED`，所以和 OpenAI/Anthropic 一样，要看具体原因再决定。

### 3. 限流：理解对方怎么数，才能自己控得住

**3.1 限流维度不止 RPM**
- OpenAI：RPM、RPD、TPM、TPD 等，哪个先满就先触发；限额在组织和项目级别，不是按用户。还有共享限额的模型族、长上下文单独限额。
- Anthropic：RPM、ITPM（输入 token）、OTPM（输出 token），按模型分别计算；对大多数模型，**缓存命中的输入 token 不计入 ITPM**，所以提高缓存命中率等于变相提额。
- 关键差异：OpenAI 按 `max(max_tokens, 估算 token 数)` 计入限额，`max_tokens` 设大了会白占额度；Anthropic 文档说 OTPM 只按实际生成计算，`max_tokens` 不影响限额。

**3.2 令牌桶，以及"每分钟 60 次"其实可能是"每秒 1 次"**
- Anthropic 明确说用的是令牌桶算法（容量持续回补，不是整分钟重置），并且 60 RPM 可能按 1 次/秒执行，短时突发会被拒。
- 所以客户端也要用令牌桶或漏桶平滑发送，而不是"每分钟开头一口气发完"。
- 还有"加速度"限制：OpenAI 的 429 `slow_down` 是流量涨得太快，哪怕没超 RPM/TPM 也会触发。经验值是到了 100 万输入 TPM 以后，每 15 分钟最多涨 50%。Anthropic 的 acceleration limits 是同一回事。上线压测、批量回刷数据时最容易撞上。

**3.3 限流响应头要用起来**
- OpenAI：`x-ratelimit-limit-requests / -tokens`、`x-ratelimit-remaining-requests / -tokens`、`x-ratelimit-reset-requests / -tokens`，有项目级 token 限额时还有 `x-ratelimit-*-project-tokens`。
- Anthropic：`anthropic-ratelimit-requests-*`、`-tokens-*`、`-input-tokens-*`、`-output-tokens-*`，每组都有 limit/remaining/reset。注意 tokens-remaining 是**四舍五入到千位**的，不能拿来做精确计数；`anthropic-ratelimit-tokens-*` 显示的是"当前最紧的那个限额"。
- 用法：在共享客户端里记录最近一次的 remaining，接近 0 时主动降速，比挨了 429 再退避要稳。

**3.4 失败的请求也算数**
- OpenAI 文档：失败的请求也计入每分钟限额，所以"一直重发"不会让你更快拿到结果，只会让限流持续更久。

### 4. 超时分层

**4.1 至少分清四种：连接、读（两次数据之间）、单次尝试总时长、整个任务截止时间**
- httpx（两家 Python SDK 的底层）分 connect、read、write、pool 四种超时，其中 **read 是"两次收到数据之间最多等多久"**，不是整个响应的总时长。
- 两家 SDK 默认 `Timeout(timeout=600, connect=5.0)`，即连接 5 秒、其他 10 分钟。流式响应只要还在吐 token，就永远不会触发这个超时；反过来，首 token 很慢的请求可能要等很久才失败。所以"首 token 超时"和"总时长截止"都要你自己在业务层实现。
- AWS Builders' Library 提醒：有些超时实现不覆盖 DNS 解析和 TLS 握手；新建 TLS 连接比复用慢，部署后冷连接会集中超时，解决办法是进程启动时预热连接。

**4.2 超时值怎么定**
- AWS 的做法：先定一个可接受的误超时比例（如 0.1%），再取下游对应的延迟分位数（p99.9）。跨公网要额外加网络余量。
- LLM 的延迟和输出长度强相关，最好按"预估输出 token × 每 token 耗时 + 首 token 时间"给每个请求单独算截止时间，而不是一个全局常量。

**4.3 非流式长请求会被 SDK 拒绝**
- anthropic-python 源码 `_calculate_nonstreaming_timeout`：预估耗时 = `3600 秒 × max_tokens / 128000`，超过 10 分钟就抛错 "Streaming is required for operations that may take longer than 10 minutes"。按这个公式，默认设置下非流式 `max_tokens` 超过约 21,333 就会被拒。官方建议：大 `max_tokens` 用流式或 Batch。

### 5. 流式响应中途断开

**5.1 HTTP 200 之后照样会出错**
- Anthropic：流里可能出现 `event: error`，比如 `overloaded_error`（非流式时就是 529）。这种错误不走 HTTP 状态码那一套。OpenAI 文档同样说明：流开始之后的错误以流事件形式到达。
- 流里还会有 `ping` 事件，以及以后可能新增的未知事件类型，解析器要能忽略不认识的事件。

**5.2 SDK 不会帮你重试流的消费过程**
- openai-python README 原话：Stream consumption is not automatically retried, because replaying a request could duplicate output already delivered to your application。OpenAI 限流文档也说：已经消费了输出，就不要自动重放请求。
- 重放的代价：输出已经展示给用户或写进了状态，再来一遍会重复；如果流里已经出现了工具调用，重放可能导致工具被执行两次。

**5.3 断了怎么续**
- Anthropic 的做法：保存已收到的部分，构造续写请求。4.5 及更早的模型把部分内容作为 assistant 消息前缀；4.6 及以后改为用一条 user 消息附上已生成的内容并要求"接着写"。**tool_use 和 thinking 块不能部分恢复**，只能从最近的文本块续。
- OpenAI Responses 的后台模式支持断点续流：创建时 `background: true` + `stream: true`，记住每个事件的 `sequence_number`，断线后用 `GET /v1/responses/{id}?stream=true&starting_after=N` 接上。

### 6. 幂等与重复副作用

**6.1 超时不等于没执行**
- Stripe 把失败分三种：连接没建立（可安全重试）、服务端处理到一半、服务端做完了但回包丢了。后两种客户端无法判断是否执行过，必须靠幂等才能安全重试。
- 对 agent 来说，调模型本身重复一般只是多花钱；**真正危险的是工具调用**：发邮件、下单、写数据库、调第三方 API。工具层必须有幂等键。

**6.2 幂等键怎么做**
- 客户端生成唯一 ID（如 UUID），放在 `Idempotency-Key` 头里，重试时复用同一个 key（Stripe 的做法）。服务端存 key + 请求参数 + 结果，同 key 再来直接返回存下的结果。
- brandur 的 Postgres 实现给了很多细节：key 和用户 ID 组合唯一；同 key 但参数不同要报错（AWS 也是这样，返回参数不匹配的校验错误）；同 key 的请求正在执行时返回 409；key 保留 24–72 小时后清理；每个"对外部系统的写操作"自成一个原子阶段，并记录恢复点。
- 坑：两家 Python SDK 的基类有生成幂等键的代码（`stainless-python-retry-<uuid>`），但我在 openai / anthropic 的 `_client.py` 里没找到设置幂等头名的地方，基类默认 `_idempotency_header = None`。所以**不要以为 SDK 重试是幂等的**，模型 API 本身也没有公开的幂等键语义。

**6.3 agent 里的落地方式**
- 给每次工具调用派生稳定的 ID（例如 `会话ID + 轮次 + tool_call_id`），作为外部 API 的幂等键，同时写进自己的执行日志；重放或恢复时先查日志，已执行过的直接复用结果。

### 7. 重试放大与重试预算

**7.1 每层都重试会指数放大**
- AWS：5 层调用每层重试 3 次，最底层数据库的负载会放大 243 倍；最佳实践是只在调用栈的一个点重试。
- Google SRE：前端、后端、JS 三层各重试 3 次（4 次尝试），一个用户动作最多打到数据库 64 次。
- agent 里的典型叠加：SDK 默认重试 2 次 × 你自己的 tenacity 重试 × 网关（LiteLLM 之类）的重试 × agent 循环里"失败了再让模型试一次"。OpenAI 文档专门提醒：自己在应用层做重试时，要关掉 SDK 重试或把它算进总次数。

**7.2 重试预算**
- SRE 的两道闸：每个请求最多 3 次尝试；每个客户端重试请求占比不超过 10%。这样最坏情况下的负载放大从约 3 倍降到约 1.1 倍。还可以给整个进程设"每分钟最多 N 次重试"的全局预算。
- 令牌桶式重试（AWS SDK 2016 年起内置，Marc Brooker 文章里叫 adaptive retries）：每次成功往桶里存一点（例如 0.1 个令牌），每次重试花 1 个，桶空了就不重试。故障率低时跟普通重试一样，故障率高时自动收敛。

### 8. 并发控制

- 有两种限法：按速率（每秒 N 个）和按并发（同时进行中最多 N 个）。Stripe 用的并发限制器针对的正是"慢接口 + 用户等不及就重试"的场景。LLM 调用时长从几秒到几分钟，**按并发数限制往往比按速率更有效**。
- 客户端排队要有上限，并且能丢弃已经过期的请求：SRE 提到队列太长时，请求在队列里等的时间比执行还久，用户早就放弃了。
- 连接池也是并发闸门：两家 SDK 默认 `max_connections=1000, max_keepalive_connections=100`；httpx 拿不到连接时抛 `PoolTimeout`，这个超时和读超时是两回事，高并发时报错类型会让人误判成"模型慢"。

### 9. 熔断、降级、模型回退

**9.1 熔断器**
- Fowler：失败达到阈值后熔断器"跳闸"，后续调用直接失败、不再打下游；过一段时间进入半开状态放一个试探请求，成功就恢复。不是所有错误都该计入熔断（例如 400 是你自己的问题）。
- AWS 的提醒：熔断会让系统多出一种难测试的模式，还可能拖慢恢复；他们更倾向用本地令牌桶限制重试。Brooker 的模拟也显示，客户端很多、每个流量很小时，熔断会太早跳闸。

**9.2 降级与模型回退**
- 回退要分原因：上下文超长、内容策略拦截、限流/过载，适合的回退目标不一样。LiteLLM 就分成 `context_window_fallbacks`、`content_policy_fallbacks`、`fallbacks` 三类，并支持冷却（例如 `allowed_fails: 3`、`cooldown_time: 30`：一分钟内失败超过阈值的部署暂时下线 30 秒）。
- 坑：回退到别的模型，输出格式、工具调用习惯、上下文长度、价格都会变；thinking 块等带签名的内容一般不能跨模型原样回传。回退路径平时不走，出事时最容易坏——SRE 原话是"你从来不用的代码路径（往往）是坏的"，要定期演练。

### 10. 长任务、后台模式、批量 API、取消

**10.1 后台模式**
- OpenAI Responses `background: true`：立即返回，状态在 `queued`/`in_progress` 时轮询，取消用 `POST /v1/responses/{id}/cancel`，**取消是幂等的**（重复取消返回最终对象）。同步请求要取消只能断开连接。注意：即使 `store=false`，后台模式也会把数据临时存约 10 分钟；后台模式的首 token 延迟比同步高。

**10.2 批量 API：便宜一半，换取不确定的完成时间**
- OpenAI Batch：价格 5 折，24 小时完成窗口，每批最多 5 万个请求、输入文件 200 MB；独立的限额池，不占同步限额；输出顺序不保证，必须用 `custom_id` 对应；过期未完成的写进错误文件，已完成的照常计费。
- Anthropic Message Batches：价格 5 折，每批最多 10 万个请求或 256 MB；大多数 1 小时内完成，最长 24 小时；结果保存 29 天；`errored`、`canceled`、`expired` 的请求不计费；参数校验是异步的，整批跑完才告诉你哪条格式错——所以先用同步 API 试跑一条。
- 适用：评测、离线数据处理、回填。不适合用户在线等待的场景。

**10.3 取消要一路传下去**
- SRE：用对冲请求或者上游已放弃时，要把取消传播到整条调用链，否则下游继续白干。agent 场景：用户点了停止，正在跑的模型流、工具子进程、外部 HTTP 调用都要取消，后台任务也要调对应的 cancel 接口。

### 11. 成本与延迟的权衡

- 重试、对冲请求、回退都在花钱换可用性：重试越多成功率越高，但每次重试都会重新计费输入 token。
- 降延迟最直接的是少生成 token（OpenAI 延迟优化指南第一条就是 Generate fewer tokens）；降成本最直接的是批量 API（5 折）和提示词缓存（Anthropic 下缓存读取还不占 ITPM）。
- 用户在等的请求：短超时 + 少量重试 + 快速失败/降级；离线任务：长超时 + 批量 API + 宽松重试。不要两类流量共用同一套参数和同一个限额池——SRE 和 Stripe 都按重要程度给请求分级，过载时先丢低优先级的。

## 二、文章很少讲但常碰到的事

**1. 反向代理默认会缓冲 SSE，导致"流式变成一次性返回"**
- nginx `proxy_buffering` 默认是 `on`，会先把上游响应攒进缓冲区；流式接口要关掉，或者让上游返回 `X-Accel-Buffering: no` 响应头单独关掉。
- nginx `proxy_read_timeout` 默认 60 秒，而且是"两次读之间"的间隔。模型思考很久不吐字时，连接会被 nginx 断掉，客户端看到的是 502/504 或流突然结束。

**2. 各层空闲超时不一致，导致莫名其妙的 502/524**
- Cloudflare：源站连接后 125 秒内没有返回 HTTP 响应就报 524（普通套餐不能调，企业版最多可调到 6000 秒）；官方建议长任务改成状态轮询。
- AWS ALB：**连接空闲超时默认 60 秒**（`idle_timeout.timeout_seconds`，可调范围 1–4000 秒），连接上 60 秒没有任何数据收发就会被关掉。官方建议在超时前至少发 1 字节，并且**应用自身的 keep-alive 超时要大于负载均衡的空闲超时**，否则 ALB 可能往已关闭的连接上发请求，返回 502。两个容易漏的细节：ALB 不支持 HTTP/2 PING 帧，PING **不会**重置空闲计时，所以心跳必须是真正的数据（比如 SSE 注释行）；另有一个"客户端 keep-alive 时长"，默认 3600 秒，到点后 ALB 会主动断开长连接（HTTP/1.1 发 `Connection: close`，HTTP/2 发 GOAWAY），超长的流也会碰上它。
- 网上不少文章写"Cloudflare 免费/Pro 套餐 100 秒超时"，这个数字已经过时；2026-10 查到的官方文档是 125 秒。这类数字一定要回官方文档核对。
- SSE 规范（WHATWG）建议每 15 秒左右发一行以 `:` 开头的注释，防止旧代理断开空闲连接。Anthropic 的 `ping` 事件起的也是这个作用。你自己的 agent 服务给前端推流时也要发心跳。
- Anthropic 文档还提到：有些网络会断开空闲连接，直连集成时可以打开 TCP keep-alive，官方 SDK 已经设了这个 socket 选项。

**3. 多 key 轮换基本不能扩容**
- OpenAI 的限额在组织和项目级别；Anthropic 的限额在组织级别（可再给 workspace 设更低的子限额）。同一组织下多建几个 key 轮换，用的还是同一个池子，不会让限额变多。真正要扩容只能提升档位或分项目/分组织隔离。
- 正确用法：按业务把 key 放到不同的 project/workspace 并设子限额，防止离线任务把在线流量的额度吃光。Anthropic 的响应头 `anthropic-workspace-id` 能告诉你这次请求算在哪个 workspace 头上。

**4. 一个进程内多个协程各自退避，等于没有限流**
- 每个协程自己看到 429 自己退避，彼此不知道对方，恢复时又一起冲上去。限流状态（remaining、reset、最近一次 Retry-After）应放在**共享的客户端/调度器**里，所有请求从同一个令牌桶取令牌。OpenAI Cookbook 的 `api_request_parallel_processor.py` 就是这个思路：碰到限流错误后让所有请求一起暂停（`seconds_to_pause_after_rate_limit_error`）。
- 多进程、多机器部署时，本地令牌桶会按机器数倍增，需要集中式计数（Stripe 用 Redis 实现令牌桶）或把额度按实例数切分。

**5. 工具调用的超时要从 agent 的总截止时间里扣**
- SRE 的截止时间传播：上游设一个绝对截止时间，每往下一层都传"剩余时间"，而不是每层各自用一个固定超时。agent 一轮可能调 5 个工具 + 2 次模型，每个都用自己的 60 秒超时，总时长就失控了。
- 往下传时预留几百毫秒给网络和后处理；剩余时间不够就别发起调用，直接失败或降级。

**6. MCP 工具也有超时和取消的规矩**
- MCP 规范：所有发出的请求都应该设超时，超时后应发 `notifications/cancelled` 并停止等待；收到进度通知时可以重置超时计时，但无论如何都要有一个最大超时。取消通知可能在对方已经处理完、甚至已经回包之后才到，双方都必须能处理这种竞态——也就是说"取消了"不等于"没执行"，有副作用的工具仍然要靠幂等。

**7. 双峰延迟会拖垮整个池子**
- SRE 例子：5% 的请求永远不返回、超时又设得比平均延迟大三个数量级，结果线程全被这 5% 占住，整体错误率涨到 80%。LLM 场景下"偶尔卡住的长请求"就是这种情况，要靠合理的单次超时 + 并发上限把慢请求隔离开（比如给每个租户只分 25% 的并发）。

**8. 会话状态的并发写冲突**
- 同一会话可能同时有两个写入者：用户连点两次发送、前端重连后重放、后台任务和前台任务同时追加消息。没有控制的话，历史会交错或丢消息。做法是乐观并发控制（读版本号、写时带条件，冲突就重读重试；AWS 退避文章的出发点就是 OCC 竞争），或者每个会话一个串行队列。
- 和模型协议也有关：Anthropic 要求回传的 thinking 块原样保留，部分新模型还要求前面的历史不变，否则返回 400。所以会话历史最好**只追加不修改**，重试/续写时不要去改已经发出去的内容。

**9. "成功"的响应也可能是不完整的**
- 流正常结束但 `stop_reason` 是 `max_tokens`，或者 Anthropic Batch 返回 `pause_turn`，都说明这一轮没做完。可靠性代码要检查结束原因，不能只看 HTTP 200。

**10. 排障要靠 request id**
- Anthropic 每个响应都有 `request-id` 头，错误体里也有 `request_id`；Python SDK 在响应对象上提供 `_request_id`。日志里要把它和你自己的 trace id、重试次数（`x-stainless-retry-count`）一起记下来，否则出问题时没法跟厂商对账。

**11. 流式连接最危险的不是断开，是静默卡住**
- 连接还在、数据不来了，不会有任何报错。SDK 的超时往往只管建连，不管传输过程。要自己加一个空闲看门狗：超过设定时间没有新数据就判定卡死，主动掐掉这条流再走重试。出处：[李博杰《深入理解 AI Agent》第 5 章「故障与错误恢复」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md)。

**12. 恢复期间先别把中间错误露出去**
- 错误处理的边界是整个恢复流程，而不是单次请求：重试、降级、续写都在进行时，扣住错误不往界面和下游事件里发；恢复成功则对方无感，全部手段用完才统一报错，并附上已经试过什么。输出被 `max_tokens` 截断时的升级顺序也一样：先静默调高上限重发，不够再追加一句让模型从断点接着写。出处同上。

---

## 三、要拿的主意

每条按「要定什么 → 选项 → 代价 → 怎么选」写。这些是做过才会碰到、而且一旦定了改起来很贵的设计决定。

### 决定 1：重试放在哪一层
- 问题：SDK 自带重试、你自己的代码、网关（LiteLLM/OpenRouter/Envoy 之类）、编排层（agent 循环或 Temporal 这类工作流引擎）都能重试，放几层？
- 选项与代价：
  - 只用 SDK 默认重试：零成本，但参数写死（2 次、最长 8 秒）、不看错误体（额度耗尽的 429 也会重试）；openai-python 遇到超过 120 秒的 Retry-After 直接放弃。
  - 自己写（tenacity 等）：可以按 `error.code` 分流、接入全局预算；但必须把 SDK 的 `max_retries` 设成 0，否则次数相乘。
  - 网关统一重试：所有服务行为一致，能跨厂商回退、集中统计；但网关自己要有重试预算（Envoy 的 retry budget 默认允许重试并发占活跃请求的 20%），而且网关和应用都重试就又叠加了。
  - 编排层重试：能跨进程崩溃继续，适合长任务；Temporal 默认重试策略是初始 1 秒、系数 2.0、最大间隔 100 倍初始值、**最大次数无限**——默认值放到 LLM 调用上会无限烧钱，必须改。
- 怎么选：**HTTP 层的瞬时错误只在一层重试**（AWS、SRE 都这么建议）。只有一个服务调模型时，放在自己代码里并关掉 SDK 重试；多服务共用模型时，放网关，应用层只处理"网关说不能再试了"的情况。编排层只重试"整个步骤"，并且要配合幂等，不要再重试单个 HTTP 请求。

### 决定 2：同步、流式、后台模式、Flex 还是批量
- 问题：同一个模型调用有多种提交方式，延迟、价格、可靠性差别很大。
- 选项与代价：
  - 同步非流式：最简单；但长输出容易撞代理/LB 的空闲超时，Anthropic SDK 会直接拒绝预计超过 10 分钟的非流式请求。
  - 同步流式：首字快、连接一直有数据不易被断；但 200 之后的错误要在流里处理，断了不能简单重放。
  - 后台模式（OpenAI `background: true`）：不怕断线，可轮询、可续流、可取消；代价是首 token 延迟更高，数据会在服务端暂存约 10 分钟（即使 `store=false`）。
  - Flex（OpenAI `service_tier: "flex"`）：按 Batch 价格计费，接口还是同步的；代价是响应更慢，会返回 `429 Resource Unavailable`（不计费），官方示例把超时调到 15 分钟。
  - 批量 API：5 折、独立限额池；代价是完成时间不确定（最长 24 小时），结果乱序，校验错误最后才知道。
- 怎么选：用户在线等 → 同步流式；单个任务要跑几分钟以上、或者链路里有 Cloudflare/ALB 这类超时 → 后台模式；不急但要逐条处理、想省钱 → Flex；大量离线任务 → 批量 API。很多团队的毛病是所有流量都走同步，结果评测和回刷数据把在线额度吃光。

### 决定 3：流式断开后，重发整个请求还是续传
- 问题：流到一半断了，用户已经看到了一部分。
- 选项与代价：
  - 整个重发：实现最简单；但输入 token 重新计费，输出可能和前半段不一样（用户看到内容"变了"），如果已经出现了工具调用还可能重复执行。OpenAI 文档明确说"已消费输出后不要自动重放"。
  - 应用层续写（Anthropic 文档的做法）：把已收到的部分作为上下文让模型接着写；但 tool_use 和 thinking 块不能部分恢复，衔接处可能不自然。
  - 后台模式按 `sequence_number` 续流：服务端那边没停，客户端接上就行，结果最干净；前提是一开始就用后台模式 + 流式创建。
  - 把部分结果标记为"未完成"交给用户决定：最诚实，产品上要有对应的界面。
- 怎么选：**首 token 之前**出错，可以透明地重试甚至换厂商（用户什么都没看到）；**首 token 之后**，不要静默重发，能续流就续流，不能就续写或明确标记为不完整。如果你的服务端会把流转发给前端，还要在自己这一层缓存已发出的事件，前端用 `Last-Event-ID` 重连时从缓存补发，而不是再调一次模型。

### 决定 4：单厂商、同厂商多模型，还是多厂商备份
- 问题：主模型挂了或限流了怎么办。
- 选项与代价：
  - 单厂商单模型：行为最一致、提示词只需调一套；厂商出事就全停。
  - 同厂商多模型/多档位：例如 Anthropic `service_tier: "auto"`（有 Priority 容量时优先用，超出部分自动回到 Standard；Priority Tier 已停止新购）；或者降到小模型。改动小，但躲不开同一厂商的整体故障。
  - 多厂商备份（自建或用 OpenRouter `provider.order` / `allow_fallbacks`、LiteLLM fallbacks）：可用性最高；代价是两套提示词和工具调用格式、两套评测、带签名的 thinking 块不能跨模型回传、数据合规要重新审（OpenRouter 有 `data_collection`、`zdr` 选项正是为此）。
- 怎么选：先把"按错误原因分类回退"做好（上下文超长 → 换长上下文模型；内容策略拦截 → 换策略不同的模型；限流/过载 → 换同级别模型）。只有当业务对可用性要求高于对输出一致性的要求时才上多厂商，并且**每个备用模型都要跑一遍评测**，否则出事那天才发现备用模型不会调你的工具。

### 决定 5：限流状态放在单进程内存，还是 Redis 一类共享存储
- 问题：客户端令牌桶、并发计数、最近一次 Retry-After 放哪。
- 选项与代价：
  - 进程内存：零依赖、零延迟；多实例部署时每个实例都以为额度是自己的，实际发送量 = 实例数 × 单实例限额；扩容就会超限。
  - 进程内存 + 按实例数平分额度：简单可行；但实例数变化要重新分配，负载不均时有的实例饿着有的实例撞墙。
  - Redis 集中令牌桶（Stripe 的做法）：全局准确；多一次网络往返，Redis 挂了要决定"放行还是拒绝"——Stripe 的原则是限流器自己出故障时要放行（fail open）。
  - 交给网关：业务代码最干净；网关成为单点，要高可用部署。
- 怎么选：单实例或实例数固定 → 内存；多实例、多服务共享一个组织的额度 → Redis 或网关。不管选哪个，都以厂商返回的 `remaining`/`Retry-After` 为准做修正，因为你的计数永远不可能和服务端一致（例如 Anthropic 的 tokens-remaining 是按千位取整的）。

### 决定 6：客户端直连模型，还是走自己的后端
- 问题：浏览器/App 直接调模型 API，还是经过你的服务。
- 选项与代价：
  - 直连：少一跳、延迟最低；但 key 暴露风险、无法统一限流和计费、无法做幂等和审计、工具调用没法在服务端执行。
  - 走自己的后端：能集中做限流、重试、回退、日志、幂等、成本控制；代价是你的后端成了长连接服务，要处理代理缓冲、空闲超时、心跳、断线续传，还要受托管平台最长运行时间的限制（例如 Vercel 函数有 `maxDuration` 上限，超长时长目前还是测试版）。
- 怎么选：agent 场景几乎总是走后端，因为工具调用、状态和密钥都在后端。关键是把"模型调用"和"给前端推流"拆成两段：模型调用在后台任务里跑、结果写进存储，前端连接只负责订阅；前端断了重连不影响模型那一侧。

### 决定 7：超时用固定值，还是截止时间往下传
- 问题：每个调用各自一个超时，还是整个请求一个总预算。
- 选项与代价：
  - 每层固定超时：好配置；但重试和回退会让总时长成倍增长，下游还在为早已放弃的上游干活。
  - 截止时间传播（SRE、gRPC 的做法）：每层只拿剩余时间；需要在调用链里传一个截止时间（gRPC 有些语言默认自动传播，如 Java、Go；C++ 要手动开），工具和子 agent 都要遵守。
- 怎么选：用户在线等的请求一律用截止时间传播，剩余时间不足就不要再发起重试或回退。离线任务可以用固定的单次超时，加上整个任务的最长时长。

### 决定 8：熔断器、重试令牌桶，还是都不要
- 问题：下游大面积出错时，怎么阻止自己把它打得更死。
- 选项与代价：
  - 不做：简单；出事时重试放大负载。
  - 熔断器：故障率高时完全停止调用，保护下游；但会多出一种难测的模式，客户端多且流量小时容易过早跳闸（Brooker 模拟结果），恢复也可能变慢。
  - 重试令牌桶（AWS SDK、Brooker 的 adaptive retries）：首次请求照发，只限制重试；没有明显的模式切换，但高故障率时仍会有少量额外负载。
- 怎么选：默认先上重试令牌桶或重试预算；只有在"下游明确挂了、继续调只是浪费钱和时间"（比如某个厂商整体故障）时，用熔断器配合模型回退，并给熔断状态加监控和手动开关。

### 决定 9：工具的副作用靠什么保证只执行一次
- 问题：agent 重试、断线恢复、进程重启时，同一个工具调用可能执行多次。
- 选项与代价：
  - 依赖外部 API 的幂等键（如 Stripe `Idempotency-Key`）：最省事；但很多外部 API 不支持。
  - 自建执行日志：每个工具调用用稳定 ID 记录"开始/完成/结果"，恢复时先查日志；需要自己处理"开始了但不知道完成没有"的情况——对不支持幂等的外部 API，brandur 的建议是这种情况只能标记失败，不能盲目重试。
  - 用持久化执行引擎（Temporal 一类）：框架记录每一步的结果，崩溃后从断点继续；代价是引入新基础设施，代码要符合它的确定性约束。
- 怎么选：先给工具分类：只读的随便重试；有副作用且对方支持幂等键的，传稳定的幂等键；不支持的，加执行日志 + 人工兜底。任务长、步骤多、跨小时的 agent，才值得上持久化执行引擎。

### 决定 10：过载时请求排队，还是直接拒绝
- 问题：上游额度满了，新来的请求怎么办。
- 选项与代价：
  - 排队等：不丢请求；但队列里的请求可能等到用户早已放弃，白白消耗额度（SRE、AWS 都强调"超时后的成功响应等于失败"）。
  - 立刻拒绝/降级：用户马上知道结果；但体验差。
  - 排队 + 丢弃过期请求 + 优先处理新请求：AWS《Avoiding insurmountable queue backlogs》提到，面对积压，客户更希望新数据先被处理，积压的数据有空再处理（偏 LIFO）。
- 怎么选：在线交互：短队列 + 截止时间，过期就丢；离线任务：长队列，可以慢慢消化。两类流量要分开排队、分开额度，过载时先丢离线的。

### 决定 11：`max_tokens` 设大还是设准
- 问题：输出上限怎么设。
- 选项与代价：
  - 设大：不容易被截断；但 OpenAI 按 `max(max_tokens, 估算值)` 计入限额，设大会白占 TPM；Anthropic 非流式时设大会被 SDK 判定"可能超过 10 分钟"而拒绝。
  - 设准：省额度；但会出现 `stop_reason: max_tokens` 的截断，需要续写逻辑。
- 怎么选：按任务类型分别设，并且所有调用都检查结束原因（各家结束原因见 [01](01-llm-protocols.md) 第 4 节）；Anthropic 的 OTPM 不受 `max_tokens` 影响，但一样要配合流式使用。

---

## 四、资料清单

- [Exponential Backoff And Jitter（AWS Architecture Blog, Marc Brooker）](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)：分析；退避与抖动；用模拟对比三种抖动算法，退避加抖动的源头文章。
- [Timeouts, retries, and backoff with jitter（Amazon Builders' Library）](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter)：教学；超时取值、重试放大 243 倍、只在一层重试、令牌桶限制重试、定时任务抖动；体系最完整的一篇，建议精读。
- [Making retries safe with idempotent APIs（Amazon Builders' Library）](https://builder.aws.com/content/3Ev0BENTyBr0XxzRk5FDZzgNYos/making-retries-safe-with-idempotent-apis)：教学；幂等键设计、语义等价响应、参数不匹配报错、迟到请求；讲清"重试为什么必须配合幂等"。
- [Handling Overload（Google SRE Book 第 21 章）](https://sre.google/sre-book/handling-overload/)：分析；客户端自适应限流、请求分级、每请求 3 次和每客户端 10% 的重试预算、"过载，不要重试"信号；重试预算的出处。
- [Addressing Cascading Failures（Google SRE Book 第 22 章）](https://sre.google/sre-book/addressing-cascading-failures/)：分析；重试风暴、截止时间传播、取消传播、双峰延迟、队列管理、降级路径要演练；分布式可靠性的必读章节。
- [OpenAI Error codes](https://developers.openai.com/api/docs/guides/error-codes)：说明；各状态码和 `error.code`（slow_down、server_is_overloaded、额度类错误）、Python SDK 异常类型；判断能否重试的一手资料。
- [OpenAI Rate limits](https://developers.openai.com/api/docs/guides/rate-limits)：说明；RPM/TPM 维度、`x-ratelimit-*` 响应头、加速度限制、按 max_tokens 计入、SDK 重试与应用层重试的叠加；限流部分最实用的官方文档。
- [Anthropic API Errors](https://platform.claude.com/docs/en/api/errors)：说明；400–529 各错误类型、413 大小上限、流中错误、长请求要用流式、request-id；529 overloaded 的出处。
- [Anthropic Rate limits](https://platform.claude.com/docs/en/api/rate-limits)：说明；令牌桶、RPM/ITPM/OTPM、缓存不计入 ITPM、消费上限的 429 和 400、`anthropic-ratelimit-*` 头；和 OpenAI 对照着读，能看出两家计算方式的差异。
- [Anthropic Streaming Messages](https://platform.claude.com/docs/en/build-with-claude/streaming)：说明；SSE 事件流程、ping、流中 error 事件、断流后续写的方法和限制；流式可靠性的一手资料。
- [OpenAI Background mode](https://developers.openai.com/api/docs/guides/background)：说明；后台任务、轮询、取消幂等、按 sequence_number 断点续流；长任务该怎么跑的官方答案。
- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)：说明；5 折价格、24 小时窗口、独立限额池、custom_id、过期处理；离线任务的成本方案。
- [Anthropic Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing)：说明；10 万条/256 MB 上限、结果类型和计费、异步校验的坑；和 OpenAI Batch 对照。
- [openai-python `_base_client.py`](https://github.com/openai/openai-python/blob/main/src/openai/_base_client.py)：源码；`_should_retry`、`_calculate_retry_timeout`、`_parse_retry_after_header`、120 秒 Retry-After 上限；看 SDK 到底替你做了什么。
- [anthropic-sdk-python `_base_client.py`](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/_base_client.py)：源码；`_should_retry`、Retry-After 不设 120 秒上限、`_calculate_nonstreaming_timeout`（非流式超过 10 分钟直接报错）；和 openai 版对照能看出同一套生成代码的行为差异。
- [openai-python README（Retries / Timeouts 部分）](https://github.com/openai/openai-python#retries)：说明；默认重试 2 次、哪些错误会重试、默认 10 分钟超时、流的消费不会自动重试；SDK 行为的官方说明。
- [Gemini API Troubleshooting](https://ai.google.dev/gemini-api/docs/troubleshooting)：说明；429 RESOURCE_EXHAUSTED、503 UNAVAILABLE、SDK 默认重试 4 次、不要重试 400/402/403；第三家厂商的对照。
- [Designing robust and predictable APIs with idempotency（Stripe）](https://stripe.com/blog/idempotency)：教学；三类网络失败、Idempotency-Key、退避加抖动；幂等键入门最清楚的一篇。
- [Implementing Stripe-like Idempotency Keys in Postgres（brandur）](https://brandur.org/idempotency-keys)：教学/实战；幂等键表结构、原子阶段、恢复点、409 处理、key 回收；工具层幂等可以直接照着做。
- [Scaling your API with rate limiters（Stripe）](https://stripe.com/blog/rate-limiters)：实战；速率限制和并发限制的区别、负载削减、令牌桶加 Redis；客户端做并发控制的参考。
- [Fixing retries with token buckets and circuit breakers（Marc Brooker）](https://brooker.co.za/blog/2022/02/28/retries.html)：分析；N 次重试、令牌桶重试、重试熔断的模拟对比，以及客户端数量的影响；重试预算的量化分析。
- [Circuit Breaker（Martin Fowler）](https://martinfowler.com/bliki/CircuitBreaker.html)：教学；熔断三状态、阈值、哪些错误该计入；概念的标准说法。
- [AWS SDK Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)：说明；standard/adaptive 两种模式、max_attempts、重试令牌桶；工业级 SDK 的重试默认值参考。
- [HTTPX Timeouts](https://www.python-httpx.org/advanced/timeouts/)：说明；connect/read/write/pool 四种超时，read 是两次读之间的间隔；理解 SDK 的 timeout 参数到底在限制什么。
- [nginx ngx_http_proxy_module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)：说明；`proxy_buffering` 默认开启、`X-Accel-Buffering`、`proxy_read_timeout` 默认 60 秒；SSE 走反向代理时必查。
- [Cloudflare Error 524](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/error-524/)：说明；125 秒代理读超时、30 秒写超时、建议改用状态轮询；部署在 CDN 后面的长请求必知。
- [AWS ALB load balancer attributes（Connection idle timeout）](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-load-balancer-attributes.html)：说明；空闲超时、超时前发 1 字节、应用 keep-alive 要长于 LB 否则 502；排查偶发 502 的关键一条。
- [WHATWG HTML: Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)：说明；SSE 格式、`Last-Event-ID`、`retry` 字段、每 15 秒发注释行防代理断开；自己实现 SSE 推流时的规范依据。
- [RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)：说明；状态码语义、`Retry-After` 格式、幂等方法定义；所有状态码讨论的基准。
- [LiteLLM Proxy Reliability（Fallbacks / Cooldowns）](https://docs.litellm.ai/docs/proxy/reliability)：说明/实战；按错误原因分类的回退、冷却参数、重试次数；模型网关做回退的现成参考。
- [What is Backoff For?（Marc Brooker）](https://brooker.co.za/blog/2022/08/11/backoff.html)：分析；退避只能应对短时尖峰、客户端数量无上限时退避无效、首次请求和重试分开看；纠正"加了退避就安全"的误解。
- [Will circuit breakers solve my problems?（Marc Brooker）](https://brooker.co.za/blog/2022/02/16/circuit-breakers.html)：分析；客户端熔断器在分片/部分故障时的副作用；决定 8 的依据。
- [Using load shedding to avoid overload（Amazon Builders' Library）](https://builder.aws.com/content/3Eun1EEyX6p2e3VYNyRLSJzLuMV/using-load-shedding-to-avoid-overload)：分析；吞吐量和有效吞吐（goodput）的区别、客户端已超时的请求不要再处理；理解"排队等"为什么会害人。
- [Avoiding insurmountable queue backlogs（Amazon Builders' Library）](https://builder.aws.com/content/3EuRcgkTP1MI0c7zM8W6HL3WIqA/avoiding-insurmountable-queue-backlogs)：分析；异步系统积压、多租户隔离、偏 LIFO 处理新数据；决定 10 的依据，离线 agent 任务队列必读。
- [Envoy CircuitBreakers / RetryBudget 配置](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/circuit_breaker.proto)：说明；`budget_percent`（默认 20%）、`min_retry_concurrency`；重试预算在网关层的现成实现。
- [gRPC Deadlines](https://grpc.io/docs/guides/deadlines/)：说明；截止时间而不是超时、自动传播（Java/Go 默认开、C++ 要手动开）、服务端检查已过期请求；第二节第 5 条和决定 7 的依据。
- [Google AIP-194: Automatic retry configuration](https://google.aip.dev/194)：说明；哪些错误码能自动重试（UNAVAILABLE）、哪些绝不能（CANCELLED、DEADLINE_EXCEEDED、INVALID_ARGUMENT）、RESOURCE_EXHAUSTED 一般不重试；按错误码定重试策略的规范写法。
- [Cloud Storage Retry strategy（Google Cloud）](https://docs.cloud.google.com/storage/docs/retry-strategy)：说明；把操作分成幂等、有条件幂等（带前置条件/ETag 才幂等）、不幂等三类；给 agent 工具分类时可以照抄这个思路。
- [OpenAI Flex processing](https://developers.openai.com/api/docs/guides/flex-processing)：说明；`service_tier: "flex"`、按 Batch 价格计费、`429 Resource Unavailable` 不计费、建议调大超时；决定 2 里介于同步和批量之间的选项。
- [Anthropic Service tiers](https://platform.claude.com/docs/en/api/service-tiers)：说明；Priority/Standard/Batch 三档、`service_tier: "auto"` 超出承诺容量自动回到 Standard、Priority Tier 已停止新购；同厂商内的容量与降级选项。
- [MCP 规范 2026-07-28：Cancellation（含 Timeouts）](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation)：说明；`notifications/cancelled`、所有请求都应设超时、取消与完成的竞态必须处理；工具层超时和取消语义的规范依据。
- [Temporal Retry Policies](https://docs.temporal.io/encyclopedia/retry-policies)：说明；默认初始 1 秒、系数 2.0、最大间隔 100 倍、最大次数无限、不可重试错误列表；编排层重试的默认值陷阱。
- [OpenRouter Provider selection](https://openrouter.ai/docs/guides/routing/provider-selection)：说明；默认在多个提供方之间负载均衡、`order`、`allow_fallbacks`、`data_collection`、`zdr`；多厂商回退在聚合网关里的现成做法和合规开关。
- [深入理解 AI Agent：设计原理与工程实践 第 5 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter5.md)：分析；二-11、二-12；「故障与错误恢复」一节把故障分成接口、工具、上下文、控制流四层，讲先分类再计数、分级恢复、每条恢复路径都要熔断，素材来自对 Claude Code 等实现的源码研究。
- [Vercel Functions: Configuring maximum duration](https://vercel.com/docs/functions/configuring-functions/duration)：说明；`maxDuration` 配置、超长时长的测试版限制；托管平台的函数时长上限会直接决定流式 agent 能跑多久。

---

## 五、阅读顺序

1. 打底原理：AWS《Timeouts, retries, and backoff with jitter》→ AWS 退避抖动文章 → SRE 第 22 章（重试和截止时间部分）→ SRE 第 21 章（重试预算部分）。
2. 幂等：Stripe 幂等博客 → AWS 幂等 API → brandur 的 Postgres 实现（做工具层时再精读）。
3. 对照厂商：OpenAI Error codes + Rate limits，Anthropic Errors + Rate limits，Gemini Troubleshooting，三家放一起看差异。
4. 看 SDK 实际行为：openai-python README 的 Retries/Timeouts → `_base_client.py` 的 `_should_retry` 和 `_calculate_retry_timeout`（再对照 anthropic 版）→ HTTPX Timeouts。
5. 流式和长任务：Anthropic Streaming → OpenAI Background mode → 两家 Batch。
6. 部署链路：nginx proxy 模块 → ALB idle timeout → Cloudflare 524 → SSE 规范。
7. 进阶：Brooker 令牌桶重试 + 《What is Backoff For?》、Fowler 熔断器、Stripe rate limiters、LiteLLM/OpenRouter 回退。
8. 做设计决定前：先读本章「三、要拿的主意」，再按需看 AWS 负载削减和队列积压两篇、gRPC Deadlines、AIP-194、MCP 取消与超时、Temporal 重试策略。
