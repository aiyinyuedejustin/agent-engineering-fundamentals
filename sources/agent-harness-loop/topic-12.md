[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-12"></a>

## 12. 并发、调度与预算：多跑几个为何更慢

<a id="durable-orchestration-013"></a>

### durable-orchestration-013 · Worker deployment and performance

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：按负载划分队列避免饥饿；客户端和worker队列名拼错不一定报错，而是创建两条无人接任务的队列。

阅读范围：全文：Separate Task Queues / Manage Event History / Interpret metrics / Manage scale-down。限制：具体limits和默认推荐随版本变化；只引用机制，数字使用时再次核验

[公开原文](https://docs.temporal.io/best-practices/worker)

<a id="durable-orchestration-023"></a>

### durable-orchestration-023 · Building Decentralized Workflows that Scale

作者／组织：Peter Kraft, Qian Li / DBOS。类型：作者／团队实践或研究文章。版本／日期：2025-10-16。读取日：2026-10-13。

用途：重复workflow可在首个未checkpoint step并行竞争，UNIQUE(workflowID,stepID)只选择一条历史赢家，不能因此推导外部动作只发生一次。

阅读范围：完整正文 Conflicting Workflow / Cron / Efficient Queues。限制：厂商特定实现；正文图片中的SQL未作为已读代码计入，文字机制已读

[公开原文](https://www.dbos.dev/blog/scaleable-decentralized-workflows)

<a id="durable-orchestration-029"></a>

### durable-orchestration-029 · Flow control

作者／组织：Inngest。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：concurrency限制同时执行step，waiting run不占槽；throttle排队而rate limiting会丢触发，不能当同义词。

阅读范围：完整正文 Flow control types / ordering / combine。限制：产品自己的命名/组合规则，不代表通用rate limit必丢弃；当前durable endpoints不支持这些flow control

[公开原文](https://www.inngest.com/docs/durable-execution/flow-control)

<a id="durable-orchestration-039"></a>

### durable-orchestration-039 · Concur: Proactive Agent-Level Admission Control for Efficient Agentic Batch Inference

作者／组织：Qiaoling Chen et al.。类型：研究论文。版本／日期：v1 2026-01-30。读取日：2026-10-13。

用途：工具执行间隙的inactive agent仍有长期KV工作集，其他agent上下文增长可挤出它，导致回到推理时反复prefill。

选读范围：https://arxiv.org/html/2601.22705v1 sections3–4。限制：H100/SGLang等离线批量工作负载；不可直接套用托管API并发参数或吞吐收益数字

[公开原文](https://arxiv.org/abs/2601.22705)

<a id="durable-orchestration-045"></a>

### durable-orchestration-045 · Using ray.wait to limit the number of pending tasks

作者／组织：Ray contributors。类型：官方文档／规范。版本／日期：latest2.59 accessed2026-10-13。读取日：2026-10-13。

用途：限制实际运行并发不限制待调度任务的内存；无限输入流提交更快时，pending对象仍可OOM。

阅读范围：Pattern / Note / Without backpressure / With backpressure。限制：一般执行引擎原则映射到agent调度；例子阈值100不是推荐生产值

[公开原文](https://docs.ray.io/en/latest/ray-core/patterns/limit-pending-tasks.html)

<a id="durable-orchestration-049"></a>

### durable-orchestration-049 · An unfair advantage - multi-tenant queues in Postgres

作者／组织：Alexander Belanger。类型：作者／团队实践或研究文章。版本／日期：2024-04-18。读取日：2026-10-13。

用途：共享FIFO队列保护worker容量却让一个租户大量任务挡住其他用户；公平性与总并发是不同维度。

阅读范围：Fair queueing / PARTITION BY attempt / queueing woes / sequencing / concurrency limits。限制：示例SQL非经本地验证的生产代码；文称concurrency示例不能单独证明跨批所有RUNNING上限，避免直接复制；只取机制

[公开原文](https://hatchet.run/blog/multi-tenant-queues)

<a id="durable-orchestration-050"></a>

### durable-orchestration-050 · Incident report on June 22, 2026

作者／组织：Matt Aitken, Trigger.dev。类型：作者／团队实践或研究文章。版本／日期：incident2026-06-22–23; report2026-06。读取日：2026-10-13。

用途：未丢run不等于有可用执行能力；调度控制面故障造成长时间排队，已运行任务可继续。

阅读范围：TLDR / changes4-5 / Timeline / causes / knock-on problems / eu-central-1。限制：运营方事故报告，整改部分当时只是计划，不声称现已全部实施；不展开一般Kubernetes运维

[公开原文](https://trigger.dev/blog/incident-report-jun-22-2026)

<a id="durable-orchestration-060"></a>

### durable-orchestration-060 · Avoiding insurmountable queue backlogs

作者／组织：David Yanacek, AWS。类型：作者／团队实践或研究文章。版本／日期：Builder Center republished2026-06-12/modifiedJun15; original Builders Library article earlier。读取日：2026-10-13。

用途：producer入队成功仅说明接受，不说明消费者时效；测消息年龄并把首次尝试延迟与重试延迟分开。

选读范围：original https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/ redirects; Measuring availability and latency / Amazon strategies / Heartbeating long-running messages。限制：SQS数字和产品细节年代可变不采用；订单类业务可能必须继续接受，用优先级而非统一丢弃；冷邮件/审批不能未经语义判断丢旧消息

[公开原文](https://builder.aws.com/content/3EuRcgkTP1MI0c7zM8W6HL3WIqA/avoiding-insurmountable-queue-backlogs)

<a id="durable-orchestration-061"></a>

### durable-orchestration-061 · Concurrency

作者／组织：Trigger.dev。类型：官方文档／规范。版本／日期：current accessed2026-10-13。读取日：2026-10-13。

用途：perKey限制会随租户数乘大总量，共享provider应另设total且跨task共用；子任务默认不继承父限制。

阅读范围：Concurrency keys / Per-key and total / Shared resource / Concurrency and subtasks / Waits and concurrency / Pausing a limit。限制：文档描述当前实现，不倒推June事故不存在；具体60秒与新API非通用默认，版本可变；concurrency不是每秒速率限制

[公开原文](https://trigger.dev/docs/concurrency)

<a id="loop-context-059"></a>

### loop-context-059 · Pydantic AI Agents: cancellation and usage limits

作者／组织：Pydantic AI maintainers。类型：官方文档／规范。版本／日期：current read 2026-10-13。读取日：2026-10-13。

用途：request_limit与tool_calls_limit统计不同；并行调用超过tool预算时在执行前整批阻止。

选读范围：Cancelling a Run; Message History After Cancellation; sub-agents; Usage Limits through per-request budget。限制：全文截断50000字符，费用小节后半未读；cancelled usage为provider相关best effort，非准确账单。

[公开原文](https://ai.pydantic.dev/agents/)

<a id="practitioner-lessons-054"></a>

### practitioner-lessons-054 · Ten Failure Modes from a Year of Running an Agent Harness — Part 2

作者／组织：Jason Vertrees。类型：作者／团队实践或研究文章。版本／日期：unknown (opened page had no date; search metadata suggests 2026-06-11)。读取日：2026-10-13。

用途：作者复盘：局部省时的去沙箱改动放大人工审批负担；高成本重复尝试、无效effort配置和首跑无baseline的误报gate均会悄然损害loop。

阅读范围：Failure modes 6–10。限制：全文；咨询经历缺可复现制品和发生率，五位数成本仅作者个案，不作统计。

[公开原文](https://jvertrees.hashnode.dev/ten-failure-modes-from-a-year-of-running-an-agent-harness-part-2)

<a id="practitioner-lessons-055"></a>

### practitioner-lessons-055 · Orchestrating AI Agents with Temporal: Lessons from Building Pravi Agent - Studio Cavan

作者／组织：Cavan Page / Studio Cavan。类型：作者／团队实践或研究文章。版本／日期：2026-07-17。读取日：2026-10-13。

用途：事实：Pravi将便宜编排worker与有界LLM队列分开，用排队背压限制同时推理；审批信号等待释放worker。

阅读范围：Queue separation; budget inheritance; failure categories。限制：全文；并发上限不等于token速率上限；若把整个agent包成一个长Activity，其内部副作用仍需另做恢复，作者时长阈值属观点。

[公开原文](https://studiocavan.com/blog/temporal-ai-agent-orchestration/)

<a id="practitioner-lessons-057"></a>

### practitioner-lessons-057 · Loop Engineering in Production: Putting AI Agents on Call — Inside Atlan Blog

作者／组织：Arnab Saha, Alok Sharma, Nikhila Jain / Atlan。类型：作者／团队实践或研究文章。版本／日期：2026-07-17。读取日：2026-10-13。

用途：事实：前两轮方案缺少解释或过慢；并行SDK版本对所有11000条alert推理又迅速耗尽API预算。

选读范围：Three iterations; pre-filter; hybrid loop; memory。限制：读前13500字符至traced end to end；自报成本和时延非独立审计，confidence不是准确率；预过滤漏报及旧结果新鲜度仍需测。

[公开原文](https://blog.atlan.com/engineering/loop-engineering-in-production-putting-ai-agents-on-call/)

<a id="r3-runtime-008"></a>

### r3-runtime-008 · Using load shedding to avoid overload

作者／组织：David Yanacek / AWS Builders' Library。类型：作者／团队实践或研究文章。版本／日期：Migrated page published 2026-06-12, modified 2026-06-15。读取日：2026-10-14。

用途：过载时仍应让已开始的工作收尾；完成与控制路径不能被新工作挤占，排队年龄也要计入剩余期限。

选读范围：Prioritizing requests；Keeping an eye on the clock；Finishing what was started；Watching out for queues；Protecting against overload in lower layers。限制：AWS 系统实践；预留比例、独立控制池和 agent 退出顺序是按依赖设计的工程应用，不是统一默认。

[公开原文](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)

<a id="r3-runtime-011"></a>

### r3-runtime-011 · Worker shutdown behavior

作者／组织：Temporal。类型：官方文档／规范。版本／日期：Current public docs snapshot, 2026-10-14。读取日：2026-10-14。

用途：Worker 先停止接收新任务，再限时等待已接工作；后续取消能否完成取决于任务协作及 SDK。

选读范围：Opening paragraph; Graceful shutdown; Non-graceful period shutdown; General developer guidance。限制：Go 与 Core 的退出行为不同；统一 shutdown timeout 不是强杀保证，也不要求采用 Temporal。

[公开原文](https://docs.temporal.io/encyclopedia/workers/worker-shutdown)

<a id="runtime-boundaries-031"></a>

### runtime-boundaries-031 · Docker memory and CPU constraints

作者／组织：Docker。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：容器默认无resource limit；soft memory reservation不是hard cap，未限内存还禁OOM可危及host。容器内free可报告host swap，不代表自身额度；agent并发需按可实施配额计账。

选读范围：Memory risk; hard vs soft; swap。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.docker.com/engine/containers/resource_constraints/)

<a id="runtime-boundaries-059"></a>

### runtime-boundaries-059 · Charge fallback attempts once when failed continuation chain retries

作者／组织：Pydantic。类型：公开变更／提案。版本／日期：released v2.55.0; 1040a5abf8cc70ef3ebbee5ad885e11c39859c3f。读取日：2026-10-13。

用途：同一已计费失败attempt随partial/full merged response生成不同dedup token会重复扣本地预算；修复锚定最早包含它的continuation boundary。测试跨pause-turn/多segment/background job，分别有无journal。

选读范围：PR description; spend/_capability.py _anchored_token; tests/harness/spend/test_spend.py。限制：修复与版本兼容限制都由PR明确说明；非实际供应商重复收费。

[公开原文](https://github.com/pydantic/pydantic-ai/pull/10059)

[返回分类目录](README.md#topics)
