# Agent harness 与 loop 工程指南

资料核对截至 2026-10-13（UTC）。[分类来源索引：556 项来源与 19 项补充核验](../sources/agent-harness-loop/README.md)，含原文、阅读范围与版本限制。

一个能调用模型的程序，离一个能可靠完成任务的 agent 还有几段路：模型提出的动作要由谁执行，结果怎样送回模型，什么时候该等待或停止，进程重启后又凭什么继续。本文面向准备实现第一套 harness 的开发者，以“修改脚本、验证、经批准创建评审并交付”为例，按十五类责任说明机制、选择与代价。这些责任可以先放在一个小程序里，再随实际需求拆开。

## 1. 从一条工单看清 harness 与 loop

用户交来一条故障工单，希望 agent 修改工作区脚本、运行指定验证，得到确认后创建远端代码评审，最后交付补丁和链接。模型负责理解问题、提出下一步；组织模型、工具与运行状态的宿主程序，通常称为 harness。loop 是其中反复构造输入、接收提议、执行获准动作并利用结果继续的循环。文件由执行工具修改，测试由进程运行，评审由目标服务保存，宿主据这些真实结果判断任务进度。[(1)](https://developers.openai.com/api/docs/guides/function-calling)[(2)](https://www.anthropic.com/engineering/building-effective-agents)

先走完一次最小往返。以下“C1”只是说明关系的代号，不是具体接口字段名：

1. 宿主把任务、当前已知文件信息，以及“读取文件”工具的用途和参数说明交给模型。工具说明告诉模型可以请求什么，不会自行执行读取。
2. 模型返回调用 C1，提议读取某个路径。宿主检查调用是否完整、参数是否合法、路径是否在授权范围内，然后执行读取。
3. 工具返回文件内容、读取范围和必要的版本信息。宿主保存这次执行及观察，按模型 API 的格式把结果关联到 C1。
4. 宿主构造下一次输入，包含合法续接所需的前次输出与 C1 的结果，或按接口契约引用服务端保存的状态。模型这次看到了文件，才据此提出编辑或进一步查询。

因此，工具结果不是随意追加的一句聊天。它要与先前提议配对，并真正进入下一次模型请求。这里讲的是由宿主执行的本地或外接工具；提供商内部托管工具可能在响应期间就已执行，宿主不能用自己的执行门追溯阻止它。已知必须做的步骤也不必每轮让模型选择，例如修改后运行指定验证，可以直接成为宿主的必经路径。[(1)](https://developers.openai.com/api/docs/guides/function-calling)[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)[(4)](https://github.com/vercel/ai/blob/79b4ab869b38c5c702bc3a3bf055254b74648759/packages/ai/src/generate-text/stream-text.ts)[(5)](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)

接着看“创建这次评审”。宿主先记录待执行动作与实际参数，等待批准，再派发一次请求，最后保存远端评审号。这里有几种不同身份：协议调用 ID 用来配对模型提议和工具结果；业务动作 ID 追踪用户要完成的这件事；执行尝试（attempt）记录某一次派发；远端收据证明目标服务接受或完成了什么。同一动作因网络恢复产生第二次尝试，业务动作身份仍保持；用户要求再建一份评审，才是新动作。新的模型调用也可能只是核对原动作，不能因此自动另建业务动作。[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

这些身份连接的是几种用途不同的状态。协议历史负责合法续接模型；控制记录负责决定继续、等待批准还是结束；动作记录和外部收据负责核对实际效果；工作区保存文件与执行环境。它们可以同处一个数据库或进程，却不宜混成一串聊天文字。界面进度和下一次模型输入都是按用途取出的视图：界面显示“验证中”，并不意味着模型看到了完整测试日志；磁盘已有补丁，也不等于远端已经发布。[(8)](https://www.anthropic.com/engineering/managed-agents)[(9)](https://chabot.dev/blog/three-attempts-at-an-agent/)

一件任务可以由一段或多段有边界的运行完成，本文称 run。一次模型请求又可能提出多个工具调用。框架里的 turn、step、session 未必采用同一计数法，所以设置“最多十步”前，要确定数的是模型请求、工具批次还是外层循环。第一版就应有总期限、步数或费用上限，以及无进展时的停止办法；反复改写计划而没有新证据，不应无限延长运行。[(10)](https://docs.temporal.io/workflow-execution/continue-as-new)[(11)](https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/src/minisweagent/agents/default.py)[(12)](https://ai.pydantic.dev/agents/)

任务成功还需要单独的验收条件：改动满足工单，指定验证满足约定通过条件，批准覆盖实际发布动作，远端结果有可查询凭据，交付物版本正确并有可用访问方式。测试失败或权限不足时可以诚实交付已有证据，但运行应标为失败、阻塞或等待，不能称为成功。模型停止调用工具只是一次控制信号，宿主仍要检查这些条件。[(13)](https://ampcode.com/how-to-build-an-agent)[(14)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)[(15)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

## 2. Protocol 选择：模型接口与工具接入各管什么

先画清要连接的两个部件。模型原生应用编程接口（API）规定输入历史、输出内容、调用关联和终态；harness 内部接口把它们转成控制程序可以处理的对象；工具接入接口再把动作交给函数、命令行或远端服务。MCP，即 Model Context Protocol，主要标准化工具等能力的发现和接入，不代替模型 API。JSON 是数据形式，JSON Schema 约束字段和类型，而协议还规定这些数据在什么顺序、身份和状态下才有意义。[(1)](https://developers.openai.com/api/docs/guides/function-calling)[(16)](https://json-schema.org/draft/2020-12/json-schema-validation)[(17)](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

常见模型入口有 OpenAI Chat Completions、OpenAI Responses、Anthropic Messages 和 Gemini generateContent。它们在历史单元、工具结果配对、流事件和服务端状态上不同，不能只比较请求函数长什么样。可从三个选择起步：只用一个固定提供商时，原生客户端程序库（SDK）及其类型通常最容易保全语义；已有应用仅替换后端时，兼容入口能减少改动，但要实测自己的工具链；确实需要多家路由时，再做内部适配层，并让不支持的能力和降级显式可见。统一接口减少业务分支，同时增加映射与兼容测试的维护成本。[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)[(18)](https://platform.claude.com/docs/en/build-with-claude/streaming)[(19)](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)[(20)](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)

状态放在哪里，是另一个独立选择。客户端自管输入，便于按自己的留存、审计与迁移需求重建请求，但要保存所有必要协议内容；依赖服务端会话或前次响应标识，可以减少传输和组装工作，却受其保留期、访问范围与恢复条件约束。两种方式可在同一个 API 中并存，不是互斥的产品标签。若必须独立恢复，不能只存服务端响应 ID；若愿意依赖提供商状态，则应明确服务不可用时能继续到哪里。[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)[(21)](https://developers.openai.com/api/docs/guides/conversation-state)

有些接口还返回供后续请求使用的不透明协议状态，例如带签名或加密的内容块。应用不一定能解释它们，它们也不等于用户可读的说明或认证密钥。宿主的责任是按接口规定保留、关联和回传，而非自行改写；能否跨模型、账户或历史前缀复用，要由相应接口决定。这些状态仍应受会话数据的访问与留存规则保护，不因不可读就适合公开记录。只留下最终文本，又可能失去合法续接所需的工具调用和状态。[(22)](https://developers.openai.com/api/docs/guides/reasoning)[(23)](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)[(24)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

适配层因此宜保留原生内容、调用身份、响应批次、次序、终态和必要状态，再生成统一展示视图。一个 Gemini 并行调用问题就来自把同一响应里的多个调用拆成多条模型消息，后面的调用被解释成新步骤：字段都还在，分组关系却变了。工具能否并行执行，与结果如何排回协议历史是两回事。最小适配测试应覆盖多调用、交错增量、失败终态和下一轮续接；“兼容某 API”或一次请求成功，都不能替代这些检查。[(25)](https://github.com/googleapis/js-genai/issues/1275)[(19)](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)[(26)](https://github.com/vercel/ai/blob/ai%407.0.70/packages/openai/src/responses/convert-to-openai-responses-input.ts)[(27)](https://github.com/vercel/ai/pull/19066)

工具侧按部署与复用需求选。少量私有本地函数可以直调；已有成熟命令行程序（CLI）时，往往能减少接入工作；需要多客户端复用、独立部署和统一发现时，再考虑 MCP，并承担服务启动、认证、版本与故障处理成本。选了 MCP 仍要决定服务和宿主是否同机、由谁管理寿命。双方实际实现的协议版本都应进入集成测试，不能把新规范发布当成旧客户端已经迁移。[(28)](https://nx.dev/blog/why-we-deleted-most-of-our-mcp-tools)[(29)](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

## 3. 流式输出：先组装结果，再决定执行

流式输出让用户早看到内容，也使宿主需要处理半成品。网络读取的一块字节未必是一条完整事件；SSE 按约定把服务器事件分帧，一个事件又可能只携带某个内容块的一段增量。工具参数可能经过多段才组成完整 JSON，字符、换行和转义都可能跨块。实现上先还原传输事件，再解释模型协议，最后才生成工具提议，别把网络读取直接接到工具执行。[(30)](https://html.spec.whatwg.org/multipage/server-sent-events.html)[(1)](https://developers.openai.com/api/docs/guides/function-calling)

每个调用应有自己的组装缓冲，按原生项目、内容块或调用身份归并增量。工具名相同也可能是两次不同调用，不能用名称代替身份。最终对象还可能包含状态、注释或拒绝信息，单纯拼接文字会丢掉它们。保留必要的原始事件与组装结果，有助于区分提供商真的没返回，还是 SDK 或适配层漏了内容。[(31)](https://github.com/openai/openai-python/blob/main/src/openai/lib/streaming/responses/_responses.py)[(32)](https://github.com/anthropics/anthropic-sdk-python/issues/954)[(33)](https://github.com/anthropics/anthropic-sdk-python/pull/960)

第一版可以采用一个保守的本地执行门：等一次模型响应完成组装后，再检查以下条件。

- 调用身份和参数齐全，并通过结构校验。
- 原生响应没有被标为截断或失败，协议允许提交这次工具提议。
- 参数满足业务约束，当前授权允许实际对象、内容和目的地。
- 将执行哪个调用、属于哪次尝试已经确定；不完整提议只记录，不派发。

这是可选的宿主策略，不是所有 API 共用的终止事件表。它牺牲部分抢先执行的速度，换来较清楚的提交边界。AI SDK 曾修复参数合法、响应却截断时仍自动执行本地工具的问题；反过来，兼容层也可能把正常工具响应映射为普通 stop。适配层要结合原生终态与内容解释，不能只用“JSON 能解析”或单个结束字符串开门。[(34)](https://github.com/vercel/ai/issues/19063)[(27)](https://github.com/vercel/ai/pull/19066)[(35)](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.test.ts)[(36)](https://github.com/googleapis/python-genai/issues/2868)

展示和执行则可以采用不同时间点：界面预览正在生成的内容，控制状态只接纳经过验收的结果。失败后，尚未派发的本地提议可以丢弃或重新生成；已经显示的半句话和提供商内部已执行的工具效果不能这样撤销。没有收到所需终态，就保存“不完整”，不要把字节流结束（EOF）或名字带 final 的 SDK 辅助函数当成完整性保证。后续重试只覆盖宿主实际控制的边界。[(37)](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/_streaming.py)[(38)](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/lib/streaming/_messages.py)[(4)](https://github.com/vercel/ai/blob/79b4ab869b38c5c702bc3a3bf055254b74648759/packages/ai/src/generate-text/stream-text.ts)

## 4. 工具契约：让下一步不必靠猜

一个好工具要让模型知道何时用、怎样传参，以及结果可以支持什么下一步。处理工单时，“找到了几个脚本”不足以继续；路径、匹配原因、内容范围和定点再读入口才有用。稳定 ID 负责精确操作，名称帮助理解对象。工具描述还应说明副作用和返回范围，让读取文件、修改文件与公开发布成为明确不同的能力。设计从任务需要倒推，通常比逐一包装底层 API 更清楚。[(39)](https://www.anthropic.com/engineering/writing-tools-for-agents)

选择粒度时，要同时考虑模型往返与执行端复杂度。窄工具容易限制权限、解释失败，但可能需要多次调用才能完成筛选；代码工具适合在执行环境里循环、聚合和分析，能把大量数据变成小结果，却要求更强的资源控制和子操作记录。一个工具内部做了十次写入，仍有十次需要核对的效果。已有成熟 shell 不必重复包装所有命令，固定且高后果的业务动作则常值得提供专门接口。在相同任务、环境和评分条件下比较完整轨迹，而非追求工具越少或越多。[(40)](https://blog.cloudflare.com/code-mode/)[(41)](https://blog.cloudflare.com/code-mode-mcp/)[(42)](https://learn.microsoft.com/en-us/graph/json-batching)[(43)](https://vercel.com/blog/testing-if-bash-is-all-you-need)

执行前依次验证不同层次：JSON 是否可解析，是否符合 schema，是否符合原始业务约束，目标是否存在且可操作。模型看到的 schema 可能经过 SDK 转换，部分约束会被弱化或移入文字说明，因此执行端仍应保留自己的校验。身份、路径和权限值尤其不能靠模糊纠错静默换成另一个目标。可修正的参数错误应把原因返回给模型；权限问题则进入授权流程，不能靠重新描述参数绕过。[(16)](https://json-schema.org/draft/2020-12/json-schema-validation)[(44)](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/lib/_parse/_transform.py)[(45)](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

返回值需要同样明确。大结果应支持分页、过滤与范围读取，标出总量或已知范围、截断位置及后续入口；文件句柄应说明保存位置和有效寿命。错误应区分校验失败、执行失败和结果未知，并报告已经完成的部分。这样模型可以缩小查询、补齐参数或请求核对，而不必猜“调用失败”究竟意味着什么。工具很多时可渐进发现，让本轮只看到相关能力；发现过程仍应服从当前身份和权限。[(39)](https://www.anthropic.com/engineering/writing-tools-for-agents)[(46)](https://arxiv.org/html/2405.15793v3)[(41)](https://blog.cloudflare.com/code-mode-mcp/)

若运行中增删或替换工具，宜让每次模型请求绑定确定的工具来源与契约版本；返回后不能仅按名称路由到新定义。变更应在协议允许的边界生效，失效而未执行的提议退回重选，当前权限仍须复查。固定工具集可先随运行固定，无须引入热更新。[(47)](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)[(48)](https://blog.trailofbits.com/2025/07/28/we-built-the-security-layer-mcp-always-needed/)

缓存的取舍是减少重复访问，还是容忍过时结果。目录、业务数据、凭证和模型前缀不是一种缓存，应分别定义键、寿命与失效条件。影响结果的调用者、租户、授权范围、参数和版本需要进入相应缓存判断，命中后仍要满足当前权限与新鲜度。共享工具实例曾因复用首位调用者的目录而向后来者返回错误资源；同一用户撤权后，身份字符串又并未改变。因此敏感目录宜采用可撤销的权限版本或重新核验，不能只靠滑动过期。[(49)](https://github.com/mastra-ai/mastra/issues/17609)[(50)](https://github.com/n8n-io/n8n/pull/37401)[(51)](https://pbf.codes/posts/three-bugs-behind-one-symptom-oauth-postmortem/)

## 5. 权限与安全：在执行前检查真实动作

工单、网页和工具结果都可能包含第三方文字。它们是供任务使用的材料，不自动获得用户命令的权力。宿主需要保留来源，把“模型认为应该做”与“经验证的用户授权做”分开。危险常出现在能力组合处：可信读取工具拿到私有内容，模型受公开材料影响，再通过可信写入工具向外发布。只验证工具服务器可信，不能约束这条信息流；执行门还要检查实际对象、内容范围和接收方。[(52)](https://invariantlabs.ai/blog/mcp-github-vulnerability)[(53)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)

认证回答调用者是谁，授权回答他能对什么对象做什么。批准界面、执行环境和目标服务各管一段边界。可把凭证留在能力较窄的执行端，由它核验用户、租户、真实工具来源和目标范围；生成代码只调用必要能力，不直接接触密钥。这减少凭证暴露，却不能阻止代码滥用已允许的接口，因此还应约束数据去向。低风险只读操作可少打断，高后果写入应采用更窄的参数和审批范围。[(40)](https://blog.cloudflare.com/code-mode/)[(54)](https://arxiv.org/html/2503.18813v3)[(55)](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

批准应引用后端真实保存的待执行动作。不要接受客户端重传一段历史和 approved=true，就认定动作已经获准。一个可检查的批准记录宜绑定调用者、工具来源、操作、对象或接收方、数据范围与实际参数，并定义期限、撤销和使用次数。签名用于检测其覆盖字段被改动，不证明当前用户或租户有权限，也不自动证明真人看过界面。执行前用可信记录重验这些条件，恢复时沿用同一边界。[(56)](https://ai.pydantic.dev/deferred-tools/)[(57)](https://github.com/vercel/ai/blob/main/packages/ai/src/generate-text/validate-tool-approvals.ts)[(58)](https://docs.openclaw.ai/tools/exec-approvals)

批准还可能依赖目标版本。用户确认的是某版脚本，等待期间别人改了同一路径，参数相同也可能已经不是同一含义。需要保护版本的动作，应保存批准依据，并在目标服务支持时采用条件写入。Cloud Storage 的代次匹配能让针对旧对象的迟到删除无法删掉同名新对象。先读版本再无条件写仍有竞争窗口；条件不匹配应重新评估，而不是自动改用最新版本直到成功。审批完整性、当前权限和目标版本应分别判断。[(59)](https://www.rfc-editor.org/rfc/rfc9110.html)[(60)](https://docs.cloud.google.com/storage/docs/request-preconditions)

拒绝和异常分支也属于安全实现。历史上一个 filesystem MCP 漏洞已做真实路径检查，却把越权异常当成“文件可能不存在”，转入更宽松的父目录检查，最终放行。权限拒绝应作为独立结果保留，让 loop 缩小请求或等待必要授权。重试、换工具或换环境不能因此扩大权限。安全回归应特意走拒绝、缓存命中、恢复和批准过期路径，而不只测试正常执行。[(61)](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/)[(58)](https://docs.openclaw.ai/tools/exec-approvals)

这些机制各有代价：窄能力减少灵活性，审批增加等待，内容检查会漏判或误判；可以按风险组合使用，但强制约束要放在实际执行必经路径。提示词和长期记忆能帮助模型选对动作，不能取代授权；输入检测减少恶意材料成功影响计划的机会，确定性检查限制最终可做的事，信息流规则约束结果能去哪里。测试应检查整条链是否守住这些边界。[(62)](https://arxiv.org/html/2506.08837v2)[(63)](https://github.github.com/gh-aw/reference/safe-outputs/)[(64)](https://code.claude.com/docs/en/memory)

生命周期钩子（hook）是在模型调用、工具执行等固定位置自动运行的代码，不靠模型主动选择。应规定顺序、超时及失败后的阻断或降级策略：安全检查失败不能静默放行，普通遥测失败也不必重做业务。afterRun 一类回调还可能对应失败或取消，应读取真实终态再决定通知内容。[(65)](https://cline.bot/blog/extend-cline-with-plugins-and-hooks)[(66)](https://langfuse.com/docs/observability/features/masking)

## 6. 执行环境：命令在哪儿跑，资源归谁收尾

执行脚本前，先确定工具实际连接的环境：工作目录、依赖与版本、环境变量、凭证、网络出口，以及是否允许交互。持久 shell 会留下上次的目录、变量和后台进程，独立子进程则通常更容易把每次调用的起点写清楚。前者省去重建状态的成本，后者减少隐含依赖，选择取决于任务需要。把环境身份和寿命纳入工具契约，明确重启后哪些文件仍在、哪些服务须重建；会话 ID 本身不能证明工作区已持久保存。[(67)](https://github.com/SWE-agent/SWE-ReX/blob/main/src/swerex/runtime/local.py)[(68)](https://code.claude.com/docs/en/agent-sdk/sessions)

无人值守执行宜显式选择非交互模式，配置标准输入、分页器和编辑器。PTY 是模拟终端的通道，程序发现连接终端时可能分页或等待确认；PIPE 主要传递字节，行为未必相同。Git 停在分页器里等按键，就不是“算得太慢”，继续加超时也没有帮助。确实需要交互时，工具应暴露可关联的进程身份、当前输出和输入入口，让下一轮有依据地继续，而非重新启动一个副本。[(69)](https://github.com/SWE-agent/SWE-agent/issues/1204)[(67)](https://github.com/SWE-agent/SWE-ReX/blob/main/src/swerex/runtime/local.py)

标准输出和错误输出应持续消费。管道容量有限，不读取会反过来阻塞子进程；全读入内存又可能拖垮宿主。一个实用起点是有界保存、明确截断、将必要完整输出写入可复取文件，再向模型返回摘要与定位。退出码和业务验证分别记录：零退出码表示程序报告成功退出，是否真的修复了工单仍看测试或产物。成本由此从模型上下文转到文件保存与检索，但不会凭空消失。[(70)](https://docs.python.org/3/library/subprocess.html)[(71)](https://github.com/openai/codex/pull/5258)

启动进程也意味着承担收尾责任。超时或取消后，要停止受控工作、回收进程，并处理仍由后代持有的输出通道。直接子进程退出，孙进程仍占着 PTY，工具就可能迟迟不返回。进程组、Windows Job、线程和协程的停止边界不同，宜用各运行时支持的管理方式并做实际停止测试，记录取消请求与已确认退出。单个 kill 调用成功只能证明它所承诺的动作，不能代替整棵执行链收尾。[(72)](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)[(73)](https://nodejs.org/api/child_process.html)[(74)](https://man7.org/linux/man-pages/man2/kill.2.html)

隔离也应按执行面检查。某个 Bash 沙箱不一定覆盖 Read/Edit、MCP、hooks 或浏览器；容器默认配置也不等于已经设了 CPU、内存和磁盘上限。逐项列出可读写目录、环境变量、套接字挂载与网络去向，并检查失败后会否退回限制更少的路径。临时环境便于清理，但任务仍需的补丁和验证结果应先转到约定的持久位置，环境回收后留下一个本机路径没有交付价值。[(75)](https://code.claude.com/docs/en/sandboxing)[(76)](https://learn.chatgpt.com/docs/agent-approvals-security)[(77)](https://gvisor.dev/docs/architecture_guide/security/)[(78)](https://docs.docker.com/engine/containers/resource_constraints/)

浏览器是另一种有状态环境。截图到点击之间页面会变化，坐标可能已指向不同对象；自动等待检查元素是否可见、稳定或可点击，不判断业务含义。具后果操作要在执行时核对页面来源与目标，执行后再读取真实结果。把点击成功、页面跳转和评审创建分别记录，才能在页面异常时知道该重试哪个动作，避免重做已经完成的写入。[(79)](https://playwright.dev/docs/actionability)[(80)](https://embracethered.com/blog/posts/2026/toctou-agent-what-you-click-is-not-what-you-get/)

## 7. 网络：请求究竟卡在哪一层

一次模型请求先可能在本地等待额度或空闲连接，再经过地址解析、建连、TLS 身份验证与加密、代理转发、请求发送、首段内容、后续流和连接清理。DNS 找到地址，代理转发请求，连接池复用连接。每层都可能让界面表现为“还在思考”，但处理方式不同：连接池等待先查本地并发与泄漏，证书错误查信任配置，发出请求后的读取超时则还涉及远端结果未知。记录错误阶段，才知道下一步该检查谁。[(81)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(82)](https://www.python-httpx.org/advanced/timeouts/)[(83)](https://www.python-httpx.org/advanced/ssl/)

timeout 只是某段等待的上限，要同时标明作用域。连接超时、两块数据之间的读取间隔、一次请求尝试和整个任务期限，不能互相代替。OpenAI Python 一条报告设置单次 30 秒、最多两次重试，最终等待约 92 秒，原因正是三次尝试加退避。这个例子并非超时失效，而是用户期待的范围与设置不一致。整个运行的 deadline 应由外层持有，把请求、流消费、退避、工具和必要收尾算在一起，向下传剩余时间。[(84)](https://github.com/openai/openai-python/issues/3828)[(85)](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_internal/model_retry.py)

实现时可给总期限之内的不同阶段设较短上限，让明显失联的请求早点返回。每次重试仍受原期限约束，不能重新拿到一整段任务时间；长工具若有自己的计时，也应清楚是否计入模型等待。这样做需要贯穿调用链传递期限，但能避免每一层都遵守局部限制、整件任务仍无限拖长。超时选择要结合正常延迟分布与可接受失败率，过短会制造重试负载，过长会占住资源。[(81)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(82)](https://www.python-httpx.org/advanced/timeouts/)[(86)](https://github.com/vercel/ai/blob/543d42cdda96e2ecb59c0a28f197067b96b5ac8d/packages/ai/CHANGELOG.md)

活动与进展也应分别测量。SSE 注释心跳说明连接有数据，不证明模型产生了有用内容；代理缓冲可能把上游连续输出攒住，使客户端长时间沉默。至少区分首内容等待、内容间隔和总耗时，并核对 SDK 的计时究竟止于模型输出结束，还是覆盖本地工具执行。升级 SDK、换代理或传输库后都要重测，不能只保留一个含义漂移的 latency 数字。[(30)](https://html.spec.whatwg.org/multipage/server-sent-events.html)[(87)](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)[(86)](https://github.com/vercel/ai/blob/543d42cdda96e2ecb59c0a28f197067b96b5ac8d/packages/ai/CHANGELOG.md)

逻辑结果确认之后，再有界地清理传输资源。收到明确失败终态却一直等 EOF，可能让后来的空闲超时掩盖原错误；在应用终态立即退出，也可能影响特定传输库的连接复用。宿主应先保存已确认结果，再按库的契约关闭或排空尾部，并给清理留上限。清理失败单独记账，不改写此前的业务结论。是否需要排空、排多少，没有跨所有 SDK 的统一答案。[(88)](https://github.com/openai/codex/issues/43140)[(89)](https://github.com/openai/openai-python/issues/3440)[(90)](https://github.com/openai/openai-python/pull/3510)

排错应在真正运行 agent 的环境里进行。终端 curl 能通，不说明应用采用相同 DNS、代理变量和证书。记录 SDK 与传输版本、端点、提供商请求标识、各阶段时间和连接池占用，再与代理及上游记录对照。客户端连接宜由明确的所有者创建、复用与关闭：每轮新建增加建连开销，忘关流又会耗尽池。慢首内容、长流、断流与取消都值得成为集成测试。[(91)](https://www.python-httpx.org/async/)[(92)](https://www.python-httpx.org/environment_variables/)[(93)](https://www.python-httpx.org/advanced/transports/)[(94)](https://github.com/anthropics/claude-code/issues/78529)

## 8. 错误处理与重试：先查上一次做到了哪里

创建评审的请求已经送达，服务创建成功，回包却丢了。客户端看到超时，此时应把业务结果记为未知；直接按“失败”重发，可能得到两份评审。副作用就是外部世界发生的变化，包括写文件、发消息和创建记录。错误处理首先要回答：故障是否暂时，上次可能执行到哪里，再做是否安全，还有多少预算。对只读查询，重复通常主要增加费用与负载；对写入，答案可能改变用户实际得到的结果。[(95)](https://stripe.com/blog/idempotency)[(81)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

一个可实现的分支起点是：

- 参数、目标或权限条件不满足：报告具体原因，先修正条件或等待批准；保留明确拒绝。
- 宿主或工具实现的代码缺陷：保存原始异常与脱敏后的复现输入，进入修复路径；原样重试不算修复。若已派发写入，仍须核对实际效果。
- 已确认没有效果，或重复效果受可靠契约保护的暂时故障：进入有界重试，受总期限和尝试预算限制。
- 请求可能已产生效果：先按动作身份查询或对账；若目标系统提供合适的幂等机制，再按其规则继续。
- 无法安全判定的高影响动作：停在“未知”，保存证据并交给有权限的人决定。

这里“未知”是需要处理的业务状态，不是异常类型的别名。取消应走取消路径，预算耗尽也应结束或延后；二者都不该因为被 catch 捕获就变成网络重试。[(81)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(15)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

幂等表示重复同一逻辑操作不会重复产生该操作的效果。第 1 节的业务动作 ID 可以贯穿各次尝试，但只有目标系统支持对应契约时才有保护作用。核对操作键的去重窗口、同键换参数、首次失败和查询结果规则；参数哈希只说明输入相同，无法区分用户两次相同意图。若业务变更和执行收据能在同一数据库事务里提交，可以利用该资源内的原子性；跨到外部服务又是另一条边界。自行加一个不被目标识别的 header，并不会获得幂等保证。[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

支持幂等也不等于“重试到成功”。Stripe v1 会保存执行开始后的首次状态和响应，包括某些 500；沿用同键可能只拿回原错误，键被清理后再用又可能成为新操作。模型请求若含提供商托管工具，断流前还可能已经执行了一部分，所以要分别处理已完成效果、未派发提议和未知动作。客户端把失败尝试的增量丢掉，只能隔离尚未交给本地工具的内容。[(96)](https://docs.stripe.com/api/idempotent_requests)[(97)](https://github.com/anthropics/anthropic-sdk-python/issues/1470)[(4)](https://github.com/vercel/ai/blob/79b4ab869b38c5c702bc3a3bf055254b74648759/packages/ai/src/generate-text/stream-text.ts)

复合工具需要细到子操作。创建评审、上传附件、发通知是三个效果，最后一步失败不撤销前两步。Graph 批量请求外层 200 仍可能包含逐项失败；DynamoDB 的批量写入非原子，收到有效结果后按契约重试列出的未处理项。保存每个子操作的身份、收据、未处理项与未知项，才能只补该补的部分。若整个响应丢失，就不能猜哪些子项未处理，应重新进入核对。[(42)](https://learn.microsoft.com/en-us/graph/json-batching)[(98)](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html)[(99)](https://docs.restate.dev/develop/ts/durable-steps)

确定可重试后，再做退避、随机抖动与预算管理。SDK、网关、runner 和工具客户端若嵌套重试，最坏请求量会按各层尝试次数相乘；应明确重试责任，并统计底层总尝试、耗时和费用。服务器要求的等待超过剩余期限时，延后或停止，别截短后提前冲回去。同是 429，短时限流与消费额度用尽需要不同处理，状态码之外还要读错误体。[(81)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(100)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)[(101)](https://platform.claude.com/docs/en/api/rate-limits)[(102)](https://github.com/pydantic/pydantic-ai/blob/7db7a4d8c4b7b7b85b8636cf0b6e3305bafb5167/pydantic_ai_slim/pydantic_ai/retries.py)

重新生成模型响应、切换提供商和补偿业务动作也应显式区分。切换前检查工具能力、历史形状、必要状态及获准的数据接收范围；只有响应 ID 而没有可重建历史，换路由并不能迁移状态。补偿则是新的业务动作，需要自己的授权与结果，可能失败，也可能无法完整还原。第 10 节将处理另一种问题：当宿主本身退出后，如何重建这里所需的判断。[(103)](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router_utils/pre_call_checks/deployment_affinity_check.py)[(104)](https://openrouter.ai/docs/guides/routing/provider-selection)[(105)](https://github.com/BerriAI/litellm/issues/27967)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

## 9. 上下文与记忆：下一次模型真正看到什么

模型每次使用的是宿主实际构造的输入：稳定指令、当前任务、选中的历史、工具定义和必要观察。工作区有补丁、数据库有目标，不代表它们都进入了这次请求。原始记录保留事实，当前输入帮助作下一步，两者可以有不同内容与寿命。排查“失忆”时分三步：事实是否仍存，是否进入实际请求，模型又怎样使用了它。不要仅根据最终回答猜是哪一层坏了。[(106)](https://pi.dev/docs/latest/compaction)[(107)](https://swe-agent.com/latest/usage/trajectories/)[(108)](https://github.com/openai/codex/issues/49022)

每轮还要组装生效指令与配置，明确全局、项目和目录规则何时加载、怎样合并、冲突怎样处理，保留来源与实际结果。文件存在不等于已加载，后拼接也不保证覆盖。历史续接与配置继承是不同契约：Responses 通过 previous_response_id 续接时，上一请求顶层 instructions 不自动继承。[(64)](https://code.claude.com/docs/en/memory)[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)

输入选择可以按下一步的依赖决定，而不是先找一个通用压缩比例：

- 只依赖近期对话的短任务，保留近期上下文最直接，但别切坏未完成的协议单元。
- 连续推进同一长任务，用摘要保留目标、已验证状态和未完成项；代价是生成摘要与核验遗漏。
- 需要某个旧事实或文件细节时，按来源检索相关片段，付出检索延迟来减少无关输入。
- 探索能独立完成、主任务只需结论和证据时，可隔离为子任务，承担交接与集成成本。

这些策略可以组合。用实际续做检验选择：是否还能找到正确文件、记住待批准动作、避免把未验证改动写成完成，比摘要看起来流畅更重要。[(109)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)[(110)](https://factory.ai/news/evaluating-compression)[(2)](https://www.anthropic.com/engineering/building-effective-agents)

预算要按真实请求计算。token 是模型处理和计费的单位，没有固定的中文字符换算；工具定义、长结果、图片、音频和输出余量都可能占空间。若估算只看文字，多模态输入就可能压缩后仍然超限。宜先减少无关观察，通过分页、范围读取和外部文件保留大数据，再安排压缩时机。较小单次请求不一定带来较小总成本：漏掉关键事实后重新搜索，也会把省下的 token 花回来。[(111)](https://github.com/openai/codex/issues/33493)[(112)](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/core/src/compact_remote_v2.rs)[(22)](https://developers.openai.com/api/docs/guides/reasoning)[(110)](https://factory.ai/news/evaluating-compression)

对工单任务，一份能续做的摘要应包含当前目标，已验证与未验证的改动，失败尝试及原因，文件和产物位置，待批准动作，以及重要判断的证据入口。“计划运行测试”必须保持计划状态，不能在摘要里升级成已通过。关键完成状态由执行层维护，原始证据另有可追溯记录。连续压缩要合并上次摘要与新进展，否则越早的约束越容易消失；工具调用与结果等协议单元也不能从中间随意切开。[(110)](https://factory.ai/news/evaluating-compression)[(113)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)[(114)](https://www.liuvv.com/p/412550b7.html)

有不透明协议状态时，先选合法续接方式。服务端支持的专用压缩可能保留部分状态，应用自行写摘要、另开上下文则是有损重建；随意换历史前缀，不能期待旧状态在任意模型和账户下继续有效。反过来，也不能断言任何压缩都会破坏状态，接口可能提供带签名摘要等专用路径。模型前缀缓存只减少重复计算开销，输入仍在那里，它不负责筛选事实或建立长期记忆。[(23)](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)[(115)](https://platform.claude.com/docs/en/build-with-claude/compaction-thinking-blocks)[(116)](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)

长期记忆服务于未来任务，应挑选稳定且有用的事实，并附来源、范围、时间与失效规则，区分用户明确要求、环境事实和模型推断。项目路径变化、权限撤销或用户改变决定，都需要更新或作废旧条目。写入、检索、进入输入、被正确采用是四个环节，测试应覆盖更新、时间关系和无答案时的处理。共享记忆还需约定写入者、版本与冲突处理；记忆可以指导行为，授权仍由执行路径决定。[(117)](https://arxiv.org/html/2410.10813)[(118)](https://aclanthology.org/2026.findings-acl.1337.pdf)[(119)](https://www.notion.com/blog/building-shared-memory-for-ai-agents-in-notion)[(64)](https://code.claude.com/docs/en/memory)

计划和反思也应引入证据。测试指出哪个行为仍错，工具指出哪个目标不存在，才会约束下一轮行动；没有新观察的“再自我检查一次”可能只是重写旧假设。没有适用于所有模型的窗口百分比阈值，压缩、工具策略和额外思考都应在模型升级后复测，保留仍能改善任务结果的部分。[(120)](https://arxiv.org/html/2310.01798)[(121)](https://arxiv.org/html/2303.11366)[(122)](https://www.anthropic.com/engineering/claude-think-tool)

## 10. 持久化与恢复：进程回来以后从哪里继续

第 8 节假设宿主还记得发生了什么；持久化解决宿主退出后怎样重建同样的判断。checkpoint 是在某个边界保存的状态，必须说明覆盖哪些对象、何时提交和恢复从哪一步开始。重试增加一次执行尝试，恢复重新取得控制位置，回放则按选定方式读取或重演历史。三者可以组合，但不能都实现成一个不加区分的“再跑一次”。[(123)](https://docs.temporal.io/workflows)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

不用工作流引擎也能先做一个小版本。以创建评审为例，以下是建议的提交顺序，不是任何 SDK 自动提供的字段或保证：

1. 可靠保存业务动作身份、参数、批准依据与待执行状态；需要等待时，把等待位置一起提交。
2. 执行前重验条件，先保存本次尝试开始的记录，再向工具派发请求。这样崩溃后能识别“可能已经发出”的窗口。
3. 收到结果后追加成功收据、明确失败或未知事实，再推进相应控制位置；相关本地记录可在同一数据库事务内提交。
4. 重启后，有可信收据就继续后续步骤；尝试已开始却无结果就按第 8 节核对；确知尚未派发的动作才在重验授权后执行。

单一写入者加支持事务的本地数据库，是容易检查的起点。它增加保存与同步成本，却让恢复有据可查。开始记录可能写完而请求还没发出，远端也可能成功而本地收据尚未保存；因此这一顺序识别不确定窗口，不消除它。只有业务变更和收据同属一个原子事务的资源，才可利用该事务一起确认。恢复测试要查看独立效果记录或目标系统，不能只看最终对话状态。[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)[(124)](https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal)[(125)](https://github.com/langchain-ai/langgraph/issues/9106)

保存范围还要包括协议历史、控制位置、动作记录、工作区引用和解释它们的代码版本。会话日志在，沙箱文件仍可能过期；容器重启，内存、连接和后台进程也可能已消失。把会话与动作状态放在环境之外，可以把执行器损坏当作一次可处理的工具故障。整个 agent 保存成一个大步骤较简单，失败时重做范围也大；在外部写入和长等待处切分，恢复更细，同时增加记录、版本和恢复分支的维护工作。[(8)](https://www.anthropic.com/engineering/managed-agents)[(126)](https://modal.com/docs/guide/sandbox-snapshots)[(127)](https://docs.temporal.io/activities)

持久执行引擎提供更明确的重建方式。有的重跑编排代码，用已保存结果替代旧模型和工具调用；这里要求旧历史产生兼容的编排决定，不要求模型再次生成同一句话。另一些保存进程快照，恢复内存与位置，但受环境、连接和存储契约限制。长等待、跨进程或多步外部操作出现后，再评估引擎是否值得。无论哪种方案，还需要活着的监督者发现未完成任务并重新调度，存了状态不意味着任务会自行醒来。[(123)](https://docs.temporal.io/workflows)[(128)](https://trigger.dev/blog/v3-announcement)[(129)](https://restate.dev/blog/why-checkpointing-is-not-production-grade-durable-execution)

“文件已保存”也要分清完整、原子可见和耐久。以支持相应语义的本地文件系统为例，可先在目标目录写临时文件，检查写完整并校验格式或内容，按耐久要求同步文件，再用同一挂载文件系统内的原子重命名替换目标，必要时同步目录。完整写入避免半文件，原子替换避免读者看见中间版本，耐久同步处理崩溃后的保留；三者不是一个保证。Linux 的 write 可能短写，rename 不跨挂载点，文件 fsync 也不自动保证目录项落盘，错误都要检查。真实保证仍取决于文件系统与硬件契约。[(130)](https://man7.org/linux/man-pages/man2/write.2.html)[(131)](https://man7.org/linux/man-pages/man2/rename.2.html)[(132)](https://man7.org/linux/man-pages/man2/fsync.2.html)

数据库、快照和对象存储各遵自己的提交方式。运行中数据库宜用一致性备份接口，别只复制主文件而漏掉依赖日志；文件快照也可能截到仍在写的内容。对象存储分片上传完还可能需要完成发布并核对最终结果，不能套用本地 rename 的保证。JSONL 可作记录格式，但多写者、短写、损坏恢复仍需设计，关键动作记录不能因解析失败而悄悄跳过。[(133)](https://www.sqlite.org/atomiccommit.html)[(134)](https://www.sqlite.org/howtocorrupt.html)[(135)](https://developers.cloudflare.com/sandbox/files/save-a-sandbox-automatically/)[(136)](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html)

任务结果与交付另存状态：临时文件生成、持久发布、目标用户可访问、消息渠道接受通知，是不同事实。若结果引用和待发通知同属一个数据库，可同事务保存，再由派发器发送，这就是 outbox；重启后只补交付，不重做已成功的评审。发送后、本地标记前仍有未知窗口，要按消息凭据或目标幂等契约核对。平台接受不证明用户已读，限时链接也受凭证寿命影响；交付前应检查正确版本、权限和有效期。[(137)](https://docs.slack.dev/reference/methods/files.completeUploadExternal/)[(138)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)[(139)](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)[(140)](https://docs.particular.net/nservicebus/outbox/?version=core_9)[(141)](https://docs.slack.dev/reference/methods/chat.postMessage/)

最后确定旧任务由哪个版本接管。能读旧 JSON，不代表新代码仍按原含义解释节点、工具 schema 或批准规则。可以为有边界的运行固定版本，在任务边界升级；确需新版本接手，就对真实旧记录做兼容测试或迁移。用户有意重新运行或分叉，也应与恢复原动作区分。恢复能力由保存、兼容解释、重新调度和提交所有权共同组成，第 12 节再处理多个执行者接管时的冲突。[(142)](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning)[(143)](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_state.py)[(144)](https://docs.langchain.com/oss/python/langgraph/checkpointers)[(145)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

## 11. 插话、暂停与取消：让旧任务正确让路

评审正在创建，用户说“先别发，改一下描述”。这条消息若只排在旧任务后面，就无法阻止已启动的写入。产品要明确新输入的含义：成为下一任务、拒绝当前输入、在安全点调整后续计划，或取消旧运行。安全点是宿主检查控制消息、决定还能否启动下一动作的位置。控制入口应保持响应，不能被一个长工具占住；代价是要显式处理控制与执行之间的状态转换，而非只写一条顺序调用链。[(146)](https://docs.langchain.com/langsmith/rollback-concurrent)[(147)](https://docs.openclaw.ai/concepts/queue)[(148)](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)

入口确认宜分成“已收到”“已持久保存”“当前运行已采用”。产品承诺哪一层，就在对应边界返回确认，并用稳定消息身份支持查询。重复消息、同 ID 不同内容、乱序到达和保留期也要有规则；内存里的去重覆盖不到重启。用户看到发送成功，仍可能尚未影响本轮计划，界面应能说明这个差别，而不是把三种确认都写成同一个“已处理”。[(149)](https://github.com/openai/codex/blob/rust-v0.149.1/codex-rs/core/src/session/turn_input.rs)[(15)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)[(150)](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)

断线后先判断要恢复哪件事。重订阅界面事件只恢复观察；重新发起模型生成会产生新请求；从 checkpoint 恢复则重新取得宿主控制位置。三者不能由一个“重连”按钮混用。若应用提供序号或游标和补发，应按运行内具体请求、响应或流的身份及已确认位置续接、去重，检查缺口与过期；一个运行可有多条流，序号不能脱离所属流使用。没有可靠补发时，重新取当前状态并标明缺失，不盲拼旧流或重复业务。这是应用层策略，协议是否提供这些能力需另查。[(151)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(152)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)[(153)](https://agentclientprotocol.com/protocol/v1/session-setup)

全量重播与增量续流需要不同合并方式。AI SDK 的可恢复流示例默认重播完整流，客户端重建中断响应；只发送剩余内容时则需保留已有部分，刷新页面后的内存状态又未必仍在。契约支持的同一响应续传，与重新生成替代响应也不同：新生成不能直接拼到旧半句话后当成完整成功结果。先约定返回快照、全量事件还是增量，并核对响应身份与完成状态，再实现客户端合并；别假定所有现行协议共有恢复能力。[(151)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(153)](https://agentclientprotocol.com/protocol/v1/session-setup)

取消应沿执行链逐段确认：界面停止等待，后端收到取消，宿主停止调度，模型请求中止，工具协程、线程或进程退出，远端操作停止。AI SDK 的可恢复模式里，客户端 stop 可以只是断开消费，停止后台工作需另一条后端路径；普通流在断开时又可能因消费方式不同而停止。界面只报告已确认阶段，远端未确认效果仍保留未知。暂停通常是暂不启动后续工作，已提交动作能否撤销要看目标服务。[(151)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(152)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)[(154)](https://anyio.readthedocs.io/en/stable/threads.html)[(155)](https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination)

控制命令和结果要绑定具体运行或执行代次。过期 stop 不能停止新运行，旧工具晚到不能把新任务覆盖成完成，但真实的远端收据仍应保存供核对。长审批等待恢复时，也要重验运行仍活跃、批准仍有效。取消不应只覆盖眼前的一次异步等待：后续排队输入、摘要和自动续跑都可能再次启动工作，必须一起检查控制状态。[(151)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(58)](https://docs.openclaw.ai/tools/exec-approvals)[(150)](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)[(156)](https://github.com/earendil-works/pi/issues/9783)

需要继续在后台做的工作，应交给寿命更长的拥有者，带上状态、期限和结果回收方式。父任务结束前，要么等待其子工作收尾，要么完成明确交接。长审批可以保存等待位置，由新输入唤醒；不必让内存调用栈永远活着。这样后台执行是一项受管理的责任，而非“启动后不再管”的捷径。[(157)](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)[(158)](https://docs.langchain.com/oss/python/langgraph/interrupts)

## 12. 并发、调度与预算：多跑几个为何更慢

并发首先增加的是资源竞争。限制正在运行的数量，挡不住无限待办占满内存；有界队列限制积压，准入决定是否接受新工作，速率限制约束单位时间请求，公平调度决定谁先获得资源。宜分别测等待年龄、首次启动时延和真实执行时长。低 CPU 加长队列可能卡在槽位、连接或调度，继续增加模型并发未必有用。可合并的状态刷新与用户明确下达的写动作，还需要不同的积压处理规则。[(159)](https://docs.ray.io/en/latest/ray-core/patterns/limit-pending-tasks.html)[(160)](https://hatchet.run/blog/multi-tenant-queues)[(161)](https://builder.aws.com/content/3EuRcgkTP1MI0c7zM8W6HL3WIqA/avoiding-insurmountable-queue-backlogs)

阈值还需配套背压：消费跟不上时，向支持等待的生产者传递暂停；不能暂停的部分则选择有界存储、取消或只丢可舍弃进度，关键动作收据不能这样丢弃。本地暂停读取不证明远端生成已停，仍要核对生产端语义。[(162)](https://nodejs.org/api/stream.html)[(163)](https://github.com/openai/openai-agents-python/blob/main/src/agents/tracing/processors.py)

预算按真实资源归总。一个模型步骤可能提出多个工具，一个代码工具又发出多次 API 请求，子 agent 也消耗自己的环境和模型额度。父任务要传递可用预算并回收用量，运行、用户、租户和共享提供商也可能各有限额。token、费用、请求数、墙钟、CPU、内存和磁盘不能互换；部分额度能在启动前硬挡，部分费用只能响应后获知。解析失败仍可能已花钱，取消后缺失的用量应标未知，不能记成零。[(11)](https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/src/minisweagent/agents/default.py)[(12)](https://ai.pydantic.dev/agents/)[(164)](https://trigger.dev/docs/concurrency)

对可变对话与控制状态，由一个执行者负责提交，是简单的起点；它仍可并行等待只读工具、接收控制消息或运行独立子任务。多个执行者需要共享写入时，再选择事务、版本冲突检查或分支合并。并行计算与提交顺序是两项决定，不能让模型口头约定谁“拿到锁”。单进程应用不必先装上分布式锁，围绕真实共享对象升级即可。[(165)](https://docs.restate.dev/ai/patterns/sessions)[(148)](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)[(166)](https://cursor.com/blog/scaling-agents)

跨进程接管时，租约过期只说明旧执行者可能失联，它仍可能从长暂停中恢复。可为接管分配递增执行代次，即 fencing token，由接收提交的一方拒绝旧代次。必须是接收端检查，而非旧进程先在本地看锁是否仍有效。它保护的是所覆盖的状态提交；若外部服务不支持相同条件，就不能阻止旧执行者早已发出的写入，仍需第 8 节的幂等与核对策略。[(145)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)[(124)](https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal)

等待也会占槽位。父任务占满全部槽后等待子任务，子任务又没有槽可用，就会死锁。可以在持久等待时释放父槽、使用独立资源池或预留容量，代价是恢复时还须重新准入，并处理竞争。调度测试既要看正常吞吐，也要看失败时容量能否回收、积压恢复是否压垮控制服务；“任务没有丢”不等于它们能及时重新运行。[(164)](https://trigger.dev/docs/concurrency)[(167)](https://trigger.dev/blog/incident-report-jun-22-2026)

## 13. 多 agent：按任务独立性拆分

工单任务可以让一个子 agent 查相关代码，另一个独立审阅补丁；两者同时改同一脚本，就会争抢隐含决定。多 agent 适合独立搜索、候选方案和输入输出清楚的审阅。顺序依赖强的工作，则可能把并行收益花在重复上下文和协调上。保守起点是一个写入者加独立审阅者：审阅者用较干净的上下文减少继承原假设，咨询型子任务则可得到理解问题所需的背景。[(168)](https://cognition.com/blog/multi-agents-working)[(169)](https://www.anthropic.com/engineering/multi-agent-research-system)

独立性要看能带回什么新证据。Anthropic 的并行编译器实验给多个 agent 独立仓库副本，遇到共同构建问题时仍重复处理同一瓶颈；改进任务切分和测试才使并行更有用。共享同一个错误 API 假设的执行者，即使彼此同意也没有增加证据。先分清哪些探索能分别产出结果，哪些决定必须先统一，再计算多执行者是否值得。[(170)](https://www.anthropic.com/engineering/building-c-compiler)[(171)](https://jvertrees.hashnode.dev/ten-failure-modes-from-a-year-of-running-an-agent-harness-part-1)

交接宜包含目标、范围、已有证据、权限、预算、预期产物、未完成项和需要父方决定的问题。子任务说“测试成功”，父方应能找到命令、环境、实际结果与对应版本。收到报告后，还要把重要发现纳入主任务计划，并在必要时更新兄弟任务；收到与采用不是同一件事。最终应有明确集成人负责冲突处理、整体验证和用户交付，不能用子任务各自结束代替整体完成。[(172)](https://arxiv.org/abs/2503.13657)[(168)](https://cognition.com/blog/multi-agents-working)

交接还应记录谁在等谁，拒绝循环依赖或将阻塞决定交还父方；子任务等待仍受父方分配的期限和预算约束。这样工作拆开后，主任务仍能判断下一步由谁推进。[(164)](https://trigger.dev/docs/concurrency)[(157)](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)

隔离范围也不止源码。Git worktree 分开工作文件，却可能共用数据库、端口、缓存、凭证或后台服务。并行写入需检查这些共享对象，建立环境隔离和合并规则，并将成本计入父任务预算。取消或替换后，旧子任务沿第 11 节的身份规则归档结果与收据，不覆盖新计划。具备可检查的交接与集成条件，才值得扩大并行。[(173)](https://trigger.dev/blog/parallel-agents-gitbutler)[(148)](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)

## 14. 日志与轨迹：留得下来，也查得回去

这里把一次运行中模型输入输出、工具提议、授权、真实执行和结果核对的关联记录称为轨迹。恢复记录决定能否继续，诊断日志解释局部现场，trace 关联跨组件操作，界面展示用户关心的进度。它们可共用事件来源，但保存责任不同：动作身份、批准依据、执行状态与关键收据应可靠保存；完整模型正文按权限与留存政策受控采集，未保存的细节就明确不能精确复现。不要先要求无条件全量记录，再靠末端脱敏补救。[(24)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)[(107)](https://swe-agent.com/latest/usage/trajectories/)[(15)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

一个可用的最小事件记录宜关联运行、业务动作或模型调用、执行尝试（若有）、事件类型、时间和正文或产物引用；字段名可自定，关联必须能查回。再记录模型、提示、工具 schema 与代码版本。大正文外置时，引用也要有访问控制、保留期与完整性检查。存储设计的验收可以很具体：拿到一个远端评审号，能否反查所属动作、各次尝试、批准和相关模型调用，而不依赖界面里的一段摘要。[(24)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)[(107)](https://swe-agent.com/latest/usage/trajectories/)[(174)](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md)

回到第 1 节的创建动作：先留下某次尝试超时的事实，随后查到远端评审，就追加成功收据并推进交付；不要把原超时覆盖掉，也别另造一个动作掩盖重试。对当前状态而言可以继续，对诊断而言仍要解释为何进入过恢复。事实追加和当前状态投影各有用途，后者便于运行，前者使变化可追溯。[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(95)](https://stripe.com/blog/idempotency)[(15)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

排查“用户拿到的链接打不开”，可从结果往前查：先核文件版本、发布状态和收件人权限；再列出该动作的所有尝试，检查实际参数与批准；随后对照已留存的模型输入、原生输出和解析结果；最后沿请求标识查网络及执行环境。这样能把错误落在产生分歧的边界，而非先猜提示词。最早可见分歧只是调查入口，仍需检查它是否根因，以及后续恢复是否又引入问题。[(107)](https://swe-agent.com/latest/usage/trajectories/)[(175)](https://arize.com/blog/ai-agent-debugging-four-lessons-from-shipping-alyx-to-production/)

span 表示一段被观测操作，trace 把相关 span 串起来。一段逻辑模型调用可能含多次网络尝试，工具提议也要与真正执行区分。跨进程记录源端时间、采集时间、事件身份和传播关系：时钟可能偏移，同一父操作下的子任务可能并行。界面按时间排序方便浏览，推断先后还要看消息发送与接收，推断因果则需要进一步证据。[(24)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)[(176)](https://opentelemetry.io/docs/specs/otel/trace/api/)[(177)](https://opentelemetry.io/docs/specs/otel/logs/data-model/)[(178)](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)

遥测可以采样或丢失。有界内存队列、导出失败、进程退出、后端索引和界面展示都可能留下缺口，长 span 还可能等结束才入队。没有看到 trace 不能证明动作没执行，所以关键收据不宜仅靠遥测保存。监测丢弃、截断、损坏与导出失败，明确证据完整程度；诊断保存越丰富，存储成本和敏感数据暴露面也越大。[(163)](https://github.com/openai/openai-agents-python/blob/main/src/agents/tracing/processors.py)[(179)](https://langfuse.com/docs/administration/data-retention)

先最小化采集，再在离开信任边界前脱敏。输入、输出、元数据、事件名、附件和所有导出器都要检查；一个并列的脱敏观察者不会自动阻止其他出口看到原文。输出设字节上限、转义控制字符并记录截断位置，避免每轮重复保存完整前缀。OpenAI 的 reasoning summary 并非原始推理 token；这类内容宜作为可观察输出保存，不据此补出未观测的内部步骤。[(180)](https://openai.github.io/openai-agents-python/tracing/)[(66)](https://langfuse.com/docs/observability/features/masking)[(181)](https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/)[(22)](https://developers.openai.com/api/docs/guides/reasoning)

## 15. 回放与评测：让事故变成可验证的修复

先约定“回放”做什么。浏览历史只读记录；固定模型与工具响应重跑宿主，主要检查控制代码；从 checkpoint 继续可能调用真实服务；改动某一步再运行则是新实验。默认隔离回放副作用，未录制请求应明确失败，别悄悄穿透生产接口再创建一份评审。固定响应能稳定重放已录制交互，不能恢复未记录的调度、计时或文件系统现场；真实环境测试再检查当前工具与权限，两者互补。[(182)](https://docs.langchain.com/oss/python/langgraph/use-time-travel)[(183)](https://github.com/clay-good/agent-replay)[(184)](https://vcrpy.readthedocs.io/en/latest/usage.html)

测试可按成本分层。解析、状态转移、预算和授权门先用无模型的确定性测试；录制输入输出用于适配、恢复和版本兼容；少量真实端到端任务验证模型、工具与环境的组合。每个用例写清初始状态、输入、版本和可检查结果，验证文件、远端对象及不变量。除非顺序本身是安全要求，不必强制唯一工具路线；未经批准发布、重复创建或把失败测试报成通过，则不能被其他分数抵消。[(185)](https://ai.pydantic.dev/testing/)[(14)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)[(186)](https://hamel.dev/blog/posts/llm-judge/)

评分器也要用反例测试。一个 span 评估示例用 any 判断“存在一个不是 delete_database 的 span”，同一轨迹只要还有一次正常读取，就可能通过。它证明的是存在安全动作，所需条件却是全程没有危险动作。应构造安全与危险并存、只有危险、只有安全和记录缺失等用例。即便遍历整棵 span 树，采样或遗漏仍让“从未越权”缺乏充分证据，此时应标缺证据，而非绿色通过。[(187)](https://pydantic.dev/docs/ai/evals/evaluators/span-based/)[(188)](https://pydantic.dev/docs/ai/api/pydantic_evals/evaluators/)[(189)](https://github.com/vercel-labs/agent-eval)

模型实验要保持条件可比。记录模型、harness、工具、环境、数据集与评分规则版本；judge 是评分程序或模型，本身也可能误判。一次 trial 应是一遍真实执行，复制旧轨迹或重新评分不增加独立样本。固定温度也不保证工具路线一致，重要比较通常需要多次运行。清理会泄露前次答案的 Git 历史、缓存和外部资源，分别报告质量、成本、延迟及基础设施失败，不只保留成功样本。故障样本适合排错；观察总体表现，应从目标任务分布中抽取有代表性的样本。[(14)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)[(190)](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)[(189)](https://github.com/vercel-labs/agent-eval)[(191)](https://inspect.aisi.org.uk/scoring-workflow.html)

最小回归组可以按边界组织，而不必按框架堆测试：

- 模型交互：交错工具增量、缺少终态、压缩后续做；断言调用仍正确配对，未完成内容不会触发执行。
- 业务效果：回包丢失、批量部分成功、批准后参数或版本变化；断言真实效果次数、结果核对和授权范围。
- 控制恢复：外部成功而收据未保存时崩溃、取消后旧结果晚到、通知派发前崩溃；断言恢复位置与后续动作。
- 资源与交付：队列满、遥测丢失、临时文件不完整或用户无访问权；断言系统报告实际缺口，不虚构成功。

并发竞态可用可控暂停点安排交错，比随机 sleep 更容易稳定重现。新的恢复代码也要进入回归，而不是只验证最初故障消失。[(35)](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.test.ts)[(150)](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)[(125)](https://github.com/langchain-ai/langgraph/issues/9106)[(98)](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html)[(140)](https://docs.particular.net/nservicebus/outbox/?version=core_9)

落地不必一次装齐十五类复杂机制。第一版先让单个运行、一个写入者和少量工具走通第 1 节的闭环，带上完成条件、授权门、总期限与可查动作记录；若要自动重试远端写入，一开始就处理未知结果。出现长等待或重启需求，再补持久恢复；出现共享写入和接管，再补冲突与执行代次；确有独立且值得并行的工作，再增加多 agent。每次升级都检查解决了什么失败、增加多少等待和维护成本，模型更新后重测可删的能力补丁。机制的价值在于让任务结果更可靠，而非让架构显得更大。[(2)](https://www.anthropic.com/engineering/building-effective-agents)[(192)](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)[(193)](https://replit.com/blog/free-the-models)[(14)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
