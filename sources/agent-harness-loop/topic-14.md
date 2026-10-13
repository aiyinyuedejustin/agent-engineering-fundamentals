[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-14"></a>

## 14. 日志与轨迹：留得下来，也查得回去

<a id="boundary-closure-014"></a>

### boundary-closure-014 · OpenTelemetry Tracing API: parent, events, SpanKind and links

作者／组织：OpenTelemetry。类型：官方文档／规范。版本／日期：current specification, accessed 2026-10-13。读取日：2026-10-13。

用途：parent 由创建时 Context 产生；links 可以关联同 trace 或不同 trace 的 SpanContext，适合脱离简单父子树的关联。

选读范围：Parent；Specifying links；Add Events；SpanKind；Link。限制：只读 Parent、Specifying links、Add Events、SpanKind、Link；span 链接是插桩记录的关系，不自证实际因果、业务提交先后或根因；不是运行状态库。

[公开原文](https://opentelemetry.io/docs/specs/otel/trace/api/)

<a id="boundary-closure-015"></a>

### boundary-closure-015 · OpenTelemetry Logs Data Model: source and observed timestamps

作者／组织：OpenTelemetry。类型：官方文档／规范。版本／日期：current specification, accessed 2026-10-13。读取日：2026-10-13。

用途：Timestamp 是源端时钟记录的发生时间，ObservedTimestamp 是收集系统观察时间；两个字段可能使用不同机器时钟。

选读范围：Log record definition；Timestamp；ObservedTimestamp；Trace context。限制：只读 Log record definition、Timestamp、ObservedTimestamp、Trace context；关于因果顺序的限制由字段语义与 Lamport 共同推导，不是此规范承诺提供因果重建。

[公开原文](https://opentelemetry.io/docs/specs/otel/logs/data-model/)

<a id="boundary-closure-016"></a>

### boundary-closure-016 · Time, Clocks, and the Ordering of Events in a Distributed System

作者／组织：Leslie Lamport。类型：研究论文。版本／日期：Communications of the ACM, July 1978, 21(7)。读取日：2026-10-13。

用途：happened-before 由进程内顺序、同一消息发送到接收、传递性定义，是偏序；有些事件互不可比。

选读范围：Ordering of events；Logical Clocks（PDF 第 1–3 页）。限制：只读 Ordering of events 与 Logical Clocks，PDF pp.1–3；数学否定符在文本抽取中有损，采用旁边无歧义文字说明；不延伸到完整算法、物理时钟证明。

[公开原文](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)

<a id="practitioner-lessons-046"></a>

### practitioner-lessons-046 · How Kelet AI built a durable agent that debugs durable agents. | Temporal

作者／组织：Almog Baku / Kelet。类型：作者／团队实践或研究文章。版本／日期：2026-06-18。读取日：2026-10-13。

用途：事实：表面下游评分失败实际来自上游丢失事件时间顺序；按session聚合多条轨迹才找出系统性原因。

阅读范围：Insurance failure; session workflow; self-filtering。限制：全文；产品个案，不能把durable runtime解释为自动副作用幂等。

[公开原文](https://temporal.io/blog/we-built-a-durable-agent-debugs-durable-agents)

<a id="traces-eval-001"></a>

### traces-eval-001 · Semantic conventions for generative client AI spans

作者／组织：OpenTelemetry。类型：官方文档／规范。版本／日期：main; commit 4f85037ef86e92c510d2ef881a58f1076f6fc0e4 (2026-10-06)。读取日：2026-10-13。

用途：Span 描述调用方看到的逻辑操作，覆盖自动重试直到完整接收、失败或取消，而不是每次 HTTP 尝试混为独立业务操作。

选读范围：Spans; Execute tool span; Capturing instructions, inputs, and outputs。限制：规范仍为 Development；Streaming chunks 章节 TODO；只读 Spans/Execute tool/Capturing instructions 范围

[公开原文](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

<a id="traces-eval-002"></a>

### traces-eval-002 · Semantic Conventions for GenAI agent and framework spans

作者／组织：OpenTelemetry。类型：官方文档／规范。版本／日期：main accessed 2026-10-13。读取日：2026-10-13。

用途：同进程 agent 调用为 INTERNAL，远程托管 agent 调用为 CLIENT，workflow 应表示应用可见的编排操作而非每个隐藏 runner。

选读范围：Invoke agent client/internal span; Invoke workflow span; Plan span。限制：Development 规范；只读 client/internal invoke、workflow、plan 与工具属性相关范围

[公开原文](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)

<a id="traces-eval-005"></a>

### traces-eval-005 · OpenInference Semantic Conventions

作者／组织：Arize-ai / OpenInference。类型：官方文档／规范。版本／日期：main 2026-10-13。读取日：2026-10-13。

用途：OpenInference 用显式 LLM/TOOL/AGENT/RETRIEVER/GUARDRAIL/EVALUATOR/PROMPT span kind 区分行为；评估也作为可追踪操作而非仅最终分数。

选读范围：Span Kinds; Reserved Attributes。限制：只读 span kinds 与 reserved attributes 前 18k；字段随 main 变化，opaque 数据不应解释为可读思维

[公开原文](https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md)

<a id="traces-eval-006"></a>

### traces-eval-006 · Tracing - OpenAI Agents SDK

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：内置 tracing 默认启用，敏感数据采集也默认 true；generation/function span 可包含输入输出，需主动设置敏感开关。

阅读范围：Tracing; Sensitive data; Redaction before export。限制：文档会变；只证明 SDK 支持和默认，不代表第三方 exporter 自动符合安全策略

[公开原文](https://openai.github.io/openai-agents-python/tracing/)

<a id="traces-eval-007"></a>

### traces-eval-007 · Masking sensitive LLM data

作者／组织：Langfuse。类型：官方文档／规范。版本／日期：updated 2026-08-13。读取日：2026-10-13。

用途：新版 Python mask_otel_spans 在 export 阶段覆盖第三方 instrumentation；legacy mask 只覆盖 Langfuse SDK 属性创建，不能假设可处理所有 OTel 字段。

阅读范围：Configure masking; mask_otel_spans behavior; Masking with OpenTelemetry。限制：特定 SDK 版本契约；示例正则非通用 PII 检测

[公开原文](https://langfuse.com/docs/observability/features/masking)

<a id="traces-eval-008"></a>

### traces-eval-008 · Data Retention

作者／组织：Langfuse。类型：官方文档／规范。版本／日期：updated 2026-09-23。读取日：2026-10-13。

用途：保留 dataset item 不保留其来源 trace：独立存的输入、expected output、metadata 可还在，而原事件、时序与观测链已删。实验 run 记录也不保留关联 trace 与 scores。

阅读范围：Details; What does project retention delete?; Self-hosted。限制：这是 Langfuse 当前实现示例，不泛化所有平台；数据 access window 不等于实际删除

[公开原文](https://langfuse.com/docs/administration/data-retention)

<a id="traces-eval-009"></a>

### traces-eval-009 · Log Files - Inspect AI

作者／组织：UK AI Security Institute / Inspect。类型：官方文档／规范。版本／日期：0.3.206+ storage optimizations; current 2026-10-13。读取日：2026-10-13。

用途：长 horizon 完整前缀在每个 model event 重复会产生 O(N²) 日志；Inspect 用消息去重与 zstd，读取时应走版本化 API 而非直接依赖 JSON 结构。

选读范围：Log Format; Model API Logging; Log File API。限制：已读 Overview 至 Attachments 前，后续存储部署段未读

[公开原文](https://inspect.aisi.org.uk/eval-logs.html)

<a id="traces-eval-013"></a>

### traces-eval-013 · Traces appear but spans show No spans found despite successful export #2477

作者／组织：jaijuneja; seratch / OpenAI Agents SDK。类型：公开问题讨论。版本／日期：opened 2026-02-13; SDK 0.8.4 Python 3.12。读取日：2026-10-13。

用途：使用者报告 API 返回 204 且显示导出 4 项，但 UI 只有 trace 无 spans；force_flush、同批导出与换 key 均未解决。

阅读范围：Description; What we tried; maintainer replies。限制：单一报障，不可推断通用根因或声称已修复；页面最终 closed+wontfix 并非代码修复证据

[公开原文](https://github.com/openai/openai-agents-python/issues/2477)

<a id="traces-eval-014"></a>

### traces-eval-014 · Masking Function Causes Major Latency #10550

作者／组织：hananmannhelloheart; Langfuse maintainers。类型：公开问题讨论。版本／日期：2025-11-18 to 2025-12-01; langfuse 3.10.0。读取日：2026-10-13。

用途：用户在 LangGraph 链加入 Presidio masking 后报告响应翻倍；改为远程 API 仍因同步等待没有解决。

选读范围：Question; PresidioPIIMasker.mask; final maintainer answer。限制：延迟倍数仅为用户报告未独立测量；读取问题、核心 masking 实现与最终答复，略部分配置代码

[公开原文](https://github.com/orgs/langfuse/discussions/10550)

<a id="traces-eval-015"></a>

### traces-eval-015 · LangSmith Tracing and OpenTelemetry Span Hierarchy #1682

作者／组织：yoavigra; Angus Jelinek / LangSmith。类型：公开问题讨论。版本／日期：2025-04-23; fixed SDK 0.3.37。读取日：2026-10-13。

用途：跨异步 worker thread 的 OTel context 未传播，导致链 trace 与原 request span 断开；维护者先给包装 context 建议，重现后确认 SDK 缺陷，0.3.37修复。

阅读范围：Issue; maintainer reproduction/fix version; linked PR 1693。限制：后续用户 current span 指向顶层的问答未得到结论；不将整个上下文兼容问题视为彻底解决

[公开原文](https://github.com/langchain-ai/langsmith-sdk/issues/1682)

<a id="traces-eval-016"></a>

### traces-eval-016 · Traces Not Appearing in Single Trace Tree when using AsyncPipeline of Haystack #1678

作者／组织：Dipkumar Patel; William FH。类型：公开问题讨论。版本／日期：2025-04-21; haystack-ai 2.12.0 langsmith 0.3.27。读取日：2026-10-13。

用途：同一示例同步 Pipeline 嵌套正常，AsyncPipeline 组件变成多个根 trace；维护者指出线程切换没有 copy context，需框架传播或显式 copy_context。

阅读范围：Description; reproduction; hinthornw reply。限制：上游解决实现未在该页展示，仅记录已关闭；建议本质是上下文传播

[公开原文](https://github.com/langchain-ai/langsmith-sdk/issues/1678)

<a id="traces-eval-020"></a>

### traces-eval-020 · Agent Traces: getting to the fix, fast

作者／组织：Sierra。类型：作者／团队实践或研究文章。版本／日期：unknown; current 2026-10-13。读取日：2026-10-13。

用途：Sierra 描述在生产、手工测试、simulation 都产生同样 trace，覆盖编排组件与自定义 API，允许按步骤拆解 latency。

阅读范围：Metrics aren't enough; Always on; Latency; Actionable debugging。限制：厂商产品经验文；full reasoning path/answer why 是营销式措辞，只能解释记录的显式行为而非证明内部原因

[公开原文](https://sierra.ai/blog/agent-traces)

<a id="traces-eval-022"></a>

### traces-eval-022 · Reasoning models don't always say what they think

作者／组织：Anthropic Alignment Science。类型：作者／团队实践或研究文章。版本／日期：2025-04-03 blog for arXiv2505.05410。读取日：2026-10-13。

用途：作者通过插入影响答案的 hints 检验公开 CoT 是否承认依赖，发现被影响与承认之间存在明显差距；可读 reasoning 不能被当作完整因果审计证据。

阅读范围：研究博客：Testing for faithfulness；Conclusions。限制：实际阅读作者研究博客，未通读对应论文；特定模型、选择题和提示实验不能外推全部 agent。博客与同一研究论文合计一项。

[公开原文](https://www.anthropic.com/research/reasoning-models-dont-say-think)

<a id="traces-eval-024"></a>

### traces-eval-024 · A pipeline for transcript analysis using Inspect Scout

作者／组织：UK AI Security Institute。类型：作者／团队实践或研究文章。版本／日期：2026-02-25。读取日：2026-10-13。

用途：先定义问题、整理日志、人工看样本，再把具体可观察信号变scanner并验证，而非先大规模跑通用judge。

阅读范围：Stages1–7。限制：scanners 的标签仍非内部意图证明；博客为流程概述

[公开原文](https://www.aisi.gov.uk/blog/a-pipeline-for-transcript-analysis-using-inspect-scout)

<a id="traces-eval-027"></a>

### traces-eval-027 · Output files - SWE-agent

作者／组织：SWE-agent maintainers。类型：官方文档／规范。版本／日期：latest; 1.1.0 schema change discussed。读取日：2026-10-13。

用途：每步保留模型原response、解析thought/action、执行observation、执行后state及精确模型query，能分开parser错、执行错和模型错。

选读范围：Trajectories; Query and message field。限制：只读schema说明与开头例子；页面长示例标为v0.7.0，不能按现代格式机械解析

[公开原文](https://swe-agent.com/latest/usage/trajectories/)

<a id="traces-eval-028"></a>

### traces-eval-028 · Output files - mini-SWE-agent

作者／组织：mini-SWE-agent maintainers。类型：官方文档／规范。版本／日期：v2.0; trajectory_format mini-swe-agent-1.1。读取日：2026-10-13。

用途：轨迹不只是messages，还需agent/model/environment配置及类型、mini版本、exit_status、submission与format标识，才能解释相同prompt的行为变化。

阅读范围：Full page。限制：版本2格式；默认保存内容仍需自行秘密清理

[公开原文](https://mini-swe-agent.com/latest/usage/output_files/)

<a id="traces-eval-033"></a>

### traces-eval-033 · Sampling

作者／组织：OpenTelemetry。类型：官方文档／规范。版本／日期：modified 2025-10-16。读取日：2026-10-13。

用途：head sampling早做决定，无法保证保留晚发生错误的所有trace；tail sampling可看失败/长延迟但必须缓冲状态，有资源/运维负担。

阅读范围：Head Sampling; Tail Sampling; When not to sample。限制：文档为通用tracing原理；对agent质量率的应用为推论，不能照搬1%比例

[公开原文](https://opentelemetry.io/docs/concepts/sampling/)

<a id="traces-eval-034"></a>

### traces-eval-034 · How Canvas powers the AI agent development feedback loop

作者／组织：Honeycomb。类型：作者／团队实践或研究文章。版本／日期：unknown; current 2026-10-13。读取日：2026-10-13。

用途：Honeycomb报告用自家调查agent的生产telemetry排故、按严重度频率排序，再比较版本前后结果；观测改动应有验证闭环。

选读范围：Stages1–5。限制：厂商自述和产品营销；前后比较本身不排除流量分布混淆，不是随机实验

[公开原文](https://www.honeycomb.io/blog/how-canvas-powers-ai-agent-development-feedback-loop)

<a id="traces-eval-037"></a>

### traces-eval-037 · Observability - Microsoft Agent Framework

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：同时instrument chat client和agent会重复记录相同prompt/response；成本/存储聚合要区分聚合span与实际模型span，避免重复计数。

选读范围：OpenTelemetry Integration; Important duplication; MCP trace propagation。限制：读取公开正文C#/Python说明至配置；未查看语言代码示例；页面包含通用authorization banner但正文可读

[公开原文](https://learn.microsoft.com/en-us/agent-framework/agents/observability)

<a id="traces-eval-038"></a>

### traces-eval-038 · Logging - AutoGen

作者／组织：Microsoft AutoGen。类型：官方文档／规范。版本／日期：stable 2026-10-13。读取日：2026-10-13。

用途：AutoGen区分供人读的TRACE_LOGGER与可被系统依赖的EVENT_LOGGER结构事件；debug文本格式不应成为下游parser契约。

阅读范围：Logging; Structured logging; Emitting logs。限制：代码示例未逐行读取，主契约完整阅读

[公开原文](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/logging.html)

<a id="traces-eval-039"></a>

### traces-eval-039 · Traces - Strands Agents

作者／组织：AWS / Strands Agents。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：agent→cycle→LLM/tool分层，cycle_id可定位一次loop而非整个session；工具call id与执行status用于关联模型意图和实际结果。

选读范围：Trace Structure; Captured Attributes; Common Issues。限制：已读说明和属性表，略部署代码；字段同时处于新旧alias迁移

[公开原文](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/)

<a id="traces-eval-041"></a>

### traces-eval-041 · Agents SDK tracing processors implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：main; GitHub latest1335f4e 2026-09-27。读取日：2026-10-13。

用途：BatchTraceProcessor有界内存queue默认8192、批128、5秒节奏；put_nowait满时直接丢trace/span，不是持久审计队列。

选读范围：BatchTraceProcessor; on_trace_start; on_span_end; _export_batches。限制：完整阅读 BatchTraceProcessor；未覆盖整个 serialization 与 HTTP exporter。

[公开原文](https://github.com/openai/openai-agents-python/blob/main/src/agents/tracing/processors.py)

<a id="traces-eval-043"></a>

### traces-eval-043 · Prevent logging sensitive data in traces

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：隐藏inputs/outputs与隐藏metadata是独立覆盖面；租户要求完全不trace时应conditional tracing而非仅mask。

选读范围：Hide metadata; Rule-based masking; process functions。限制：读intro、hide、rule-based和function processing及第三方注意事项；略示例代码

[公开原文](https://docs.langchain.com/langsmith/mask-inputs-outputs)

<a id="traces-eval-045"></a>

### traces-eval-045 · ATIF: Agent Trajectory Interchange Format (RFC 0001)

作者／组织：Harbor maintainers / Boxuan Li。类型：官方文档／规范。版本／日期：ATIF 1.8; main 74cc631, 2026-08-26。读取日：2026-10-13。

用途：session_id属于运行范围，trajectory_id标识单份轨迹；v1.7子agent引用要求trajectory_id或path，不能仅用共享session_id解析。

选读范围：Version history; Root metadata; Step Object; VII Context Management。限制：读版本史、root/Step/ToolCall/Metrics、Context Management；未逐个读全部JSON例子。此为Harbor规范而非普世标准。

[公开原文](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md)

<a id="traces-eval-059"></a>

### traces-eval-059 · Handling sensitive data

作者／组织：OpenTelemetry。类型：官方文档／规范。版本／日期：modified 2026-01-14。读取日：2026-10-13。

用途：instrumentation库也会收敏感信息，需逐出口审查；最可靠的保护是最小化采集，Collector后处理并不消除先前传输。

阅读范围：Full page。限制：官方安全工程建议，非法律意见；先前传输边界为机制推论。

[公开原文](https://opentelemetry.io/docs/security/handling-sensitive-data/)

<a id="traces-eval-060"></a>

### traces-eval-060 · Trace Context

作者／组织：W3C。类型：官方文档／规范。版本／日期：Recommendation 2021-11-23。读取日：2026-10-13。

用途：traceparent/tracestate仅用于关联，不得塞入PII；随机trace_id种子也不能包含可识别人信息，跨信任边界传播可关联用户请求。

选读范围：Sections 6–8。限制：读6隐私、7安全、8ID生成；未逐字阅读全部header语法。trace_id非认证为规范风险的工程推论。

[公开原文](https://www.w3.org/TR/trace-context/)

[返回分类目录](README.md#topics)
