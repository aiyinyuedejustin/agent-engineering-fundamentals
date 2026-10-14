# Agent harness 与 loop 工程指南

资料核对截至 2026-10-14（UTC）。[分类来源索引：581 项来源与 23 项补充核验](../sources/agent-harness-loop/README.md)，含原文、阅读范围与版本限制。

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

一件任务可由一段或多段有边界的运行完成，本文称 run。一次模型请求也可能提出多个工具调用；设置“最多十步”前，要确认框架数的是请求、工具批次还是外层循环。第一版应有总期限、步数或费用上限，以及无进展退出。还要让正常结束在控制策略上可达：若需模型给出自然答案，首轮强制调用后就不能一直保留 required 或指定工具约束；也可由宿主验收工具结果后直接结束。步数上限只能截断错误循环，不能修好结束路径。[(10)](https://docs.temporal.io/workflow-execution/continue-as-new)[(11)](https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/src/minisweagent/agents/default.py)[(12)](https://ai.pydantic.dev/agents/)[(13)](https://openai.github.io/openai-agents-python/agents/)

任务成功还需要单独的验收条件：改动满足工单，指定验证满足约定通过条件，批准覆盖实际发布动作，远端结果有可查询凭据，交付物版本正确并有可用访问方式。测试失败或权限不足时可以诚实交付已有证据，但运行应标为失败、阻塞或等待，不能称为成功。模型停止调用工具只是一次控制信号，宿主仍要检查这些条件。[(14)](https://ampcode.com/how-to-build-an-agent)[(15)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)[(16)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

## 2. Protocol 选择：模型接口与工具接入各管什么

先画清要连接的两个部件。模型原生应用编程接口（API）规定输入历史、输出内容、调用关联和终态；harness 内部接口把它们转成控制程序可以处理的对象；工具接入接口再把动作交给函数、命令行或远端服务。MCP，即 Model Context Protocol，主要标准化工具等能力的发现和接入，不代替模型 API。JSON 是数据形式，JSON Schema 约束字段和类型，而协议还规定这些数据在什么顺序、身份和状态下才有意义。[(1)](https://developers.openai.com/api/docs/guides/function-calling)[(17)](https://json-schema.org/draft/2020-12/json-schema-validation)[(18)](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

常见模型入口有 OpenAI Chat Completions、OpenAI Responses、Anthropic Messages 和 Gemini generateContent。它们在历史单元、工具结果配对、流事件和服务端状态上不同，不能只比较请求函数长什么样。可从三个选择起步：只用一个固定提供商时，原生客户端程序库（SDK）及其类型通常最容易保全语义；已有应用仅替换后端时，兼容入口能减少改动，但要实测自己的工具链；确实需要多家路由时，再做内部适配层，并让不支持的能力和降级显式可见。统一接口减少业务分支，同时增加映射与兼容测试的维护成本。[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)[(19)](https://platform.claude.com/docs/en/build-with-claude/streaming)[(20)](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)[(21)](https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk)

状态放在哪里，是另一个独立选择。客户端自管输入，便于留存、审计和迁移，但要保存必要协议内容；服务端会话或前次响应标识减少传输与组装，却受保留期、访问范围和恢复条件约束。同一会话要选清 SDK、宿主或服务端谁组装历史、谁持久化，避免引用已有服务端前缀时又注入全量历史；兼用两层状态需显式对齐。若必须独立恢复，不能只存响应 ID；依赖提供商状态则要明确服务不可用时能继续到哪里。本地过滤器可能只看见本轮增量，删去其中内容不代表服务端旧前缀也被清理。[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)[(22)](https://developers.openai.com/api/docs/guides/conversation-state)[(23)](https://openai.github.io/openai-agents-python/running_agents/)

有些接口还返回供后续请求使用的不透明协议状态，例如带签名或加密的内容块。应用不一定能解释它们，它们也不等于用户可读的说明或认证密钥。宿主的责任是按接口规定保留、关联和回传，而非自行改写；能否跨模型、账户或历史前缀复用，要由相应接口决定。这些状态仍应受会话数据的访问与留存规则保护，不因不可读就适合公开记录。只留下最终文本，又可能失去合法续接所需的工具调用和状态。[(24)](https://developers.openai.com/api/docs/guides/reasoning)[(25)](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)[(26)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

适配层宜保留原生内容、调用身份、响应批次、次序、终态和必要状态，再生成展示视图。一个 Gemini 问题来自把同一响应的并行调用拆成多条模型消息，后面的调用被解释成新步骤。工具执行可以并行，协议分组仍要保全。最小适配测试覆盖多调用、交错增量、失败终态和续接，“兼容某 API”不能替代验证。[(27)](https://github.com/googleapis/js-genai/issues/1275)[(20)](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)[(28)](https://github.com/vercel/ai/blob/ai%407.0.70/packages/openai/src/responses/convert-to-openai-responses-input.ts)[(29)](https://github.com/vercel/ai/pull/19066)

消息位置也属于控制语义。工具观察、宿主指令与真实用户插话应分别组装；自动回传结果时别顺手伪造用户“继续”，或把宿主规则塞进工具结果。Anthropic 文档记录过由此引起的空响应或续接异常，但也允许特定显式续接方式。应按接口选择控制路径，遇到空响应先查实际消息形状。[(30)](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)[(31)](https://platform.claude.com/docs/en/agents-and-tools/tool-use/troubleshooting-tool-use)

工具侧按部署与复用需求选。少量私有本地函数可以直调；已有成熟命令行程序（CLI）时，往往能减少接入工作；需要多客户端复用、独立部署和统一发现时，再考虑 MCP，并承担服务启动、认证、版本与故障处理成本。选了 MCP 仍要决定服务和宿主是否同机、由谁管理寿命。双方实际实现的协议版本都应进入集成测试，不能把新规范发布当成旧客户端已经迁移。[(32)](https://nx.dev/blog/why-we-deleted-most-of-our-mcp-tools)[(33)](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

## 3. 流式输出：先组装结果，再决定执行

流式输出让用户早看到内容，也使宿主需要处理半成品。网络读取的一块字节未必是一条完整事件；SSE 按约定把服务器事件分帧，一个事件又可能只携带某个内容块的一段增量。工具参数可能经过多段才组成完整 JSON，字符、换行和转义都可能跨块。实现上先还原传输事件，再解释模型协议，最后才生成工具提议，别把网络读取直接接到工具执行。[(34)](https://html.spec.whatwg.org/multipage/server-sent-events.html)[(1)](https://developers.openai.com/api/docs/guides/function-calling)

每个调用应有自己的组装缓冲，按原生项目、内容块或调用身份归并增量。工具名相同也可能是两次不同调用，不能用名称代替身份。最终对象还可能包含状态、注释或拒绝信息，单纯拼接文字会丢掉它们。保留必要的原始事件与组装结果，有助于区分提供商真的没返回，还是 SDK 或适配层漏了内容。[(35)](https://github.com/openai/openai-python/blob/main/src/openai/lib/streaming/responses/_responses.py)[(36)](https://github.com/anthropics/anthropic-sdk-python/issues/954)[(37)](https://github.com/anthropics/anthropic-sdk-python/pull/960)

第一版可以采用一个保守的本地执行门：等一次模型响应完成组装后，再检查以下条件。

- 调用身份和参数齐全，并通过结构校验。
- 原生响应没有被标为截断或失败，协议允许提交这次工具提议。
- 参数满足业务约束，当前授权允许实际对象、内容和目的地。
- 将执行哪个调用、属于哪次尝试已经确定；不完整提议只记录，不派发。

这是可选的宿主策略，不是所有 API 共用的终止事件表。它牺牲部分抢先执行的速度，换来较清楚的提交边界。AI SDK 曾修复参数合法、响应却截断时仍自动执行本地工具的问题；反过来，兼容层也可能把正常工具响应映射为普通 stop。适配层要结合原生终态与内容解释，不能只用“JSON 能解析”或单个结束字符串开门。[(38)](https://github.com/vercel/ai/issues/19063)[(29)](https://github.com/vercel/ai/pull/19066)[(39)](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.test.ts)[(40)](https://github.com/googleapis/python-genai/issues/2868)

展示和执行则可以采用不同时间点：界面预览正在生成的内容，控制状态只接纳经过验收的结果。失败后，尚未派发的本地提议可以丢弃或重新生成；已经显示的半句话和提供商内部已执行的工具效果不能这样撤销。没有收到所需终态，就保存“不完整”，不要把字节流结束（EOF）或名字带 final 的 SDK 辅助函数当成完整性保证。后续重试只覆盖宿主实际控制的边界。[(41)](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/_streaming.py)[(42)](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/lib/streaming/_messages.py)[(4)](https://github.com/vercel/ai/blob/79b4ab869b38c5c702bc3a3bf055254b74648759/packages/ai/src/generate-text/stream-text.ts)

## 4. 工具契约：让下一步不必靠猜

一个好工具要让模型知道何时用、怎样传参，以及结果可以支持什么下一步。处理工单时，“找到了几个脚本”不足以继续；路径、匹配原因、内容范围和定点再读入口才有用。稳定 ID 负责精确操作，名称帮助理解对象。工具描述还应说明副作用和返回范围，让读取文件、修改文件与公开发布成为明确不同的能力。设计从任务需要倒推，通常比逐一包装底层 API 更清楚。[(43)](https://www.anthropic.com/engineering/writing-tools-for-agents)

工具粒度同时影响模型往返与执行复杂度。窄工具易限权和解释失败，却可能需要多次调用；代码工具适合循环、聚合和分析，能把大量数据变成小结果，但要求更强的资源控制和子操作记录。内部做了十次写入，仍有十次效果要核对。已有成熟 shell 不必逐命令重包装，固定且高后果的业务动作则常值得专门接口。[(44)](https://blog.cloudflare.com/code-mode/)[(45)](https://blog.cloudflare.com/code-mode-mcp/)[(46)](https://learn.microsoft.com/en-us/graph/json-batching)

执行前分层验证：JSON 可解析、符合 schema、符合业务约束，目标存在且可操作。SDK 可能转换模型所见 schema，弱化约束或移入说明，执行端仍应独立校验。身份、路径和权限值不能靠模糊纠错静默换目标。参数错误可返回模型修正，权限问题则进入授权流程。[(17)](https://json-schema.org/draft/2020-12/json-schema-validation)[(47)](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/lib/_parse/_transform.py)[(48)](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

包装 CLI 时，把数据作为独立参数传入，不拼 shell 字符串。argv 只去掉 shell 的一层解释，程序自身的选项、配置或插件仍能改变行为。窄工具宜固定程序与选项，校验参数含义、路径和目的地；支持时用 -- 结束选项。通用 shell 按代码执行授权并隔离，不能凭 git/npm 前缀判为低风险。[(49)](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)[(50)](https://geminicli.com/docs/reference/policy-engine/)

返回值应支持下一步核对。大结果提供分页、过滤与范围读取，标出总量或已知范围、截断位置及后续入口；文件句柄说明位置和寿命。有关联的读取还应返回可用的数据版本或观察时点，便于判断能否合并。错误区分校验失败、执行失败和结果未知，并报告已完成部分。工具多时可渐进发现，但目录仍须服从当前身份和权限。[(43)](https://www.anthropic.com/engineering/writing-tools-for-agents)[(51)](https://arxiv.org/html/2405.15793v3)[(45)](https://blog.cloudflare.com/code-mode-mcp/)

若运行中增删或替换工具，宜让每次模型请求绑定确定的工具来源与契约版本；返回后不能仅按名称路由到新定义。变更应在协议允许的边界生效，失效而未执行的提议退回重选，当前权限仍须复查。固定工具集可先随运行固定，无须引入热更新。[(52)](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)[(53)](https://blog.trailofbits.com/2025/07/28/we-built-the-security-layer-mcp-always-needed/)

缓存的取舍是减少重复访问，还是容忍过时结果。目录、业务数据、凭证和模型前缀不是一种缓存，应分别定义键、寿命与失效条件。影响结果的调用者、租户、授权范围、参数和版本需要进入相应缓存判断，命中后仍要满足当前权限与新鲜度。共享工具实例曾因复用首位调用者的目录而向后来者返回错误资源；同一用户撤权后，身份字符串又并未改变。因此敏感目录宜采用可撤销的权限版本或重新核验，不能只靠滑动过期。[(54)](https://github.com/mastra-ai/mastra/issues/17609)[(55)](https://github.com/n8n-io/n8n/pull/37401)[(56)](https://pbf.codes/posts/three-bugs-behind-one-symptom-oauth-postmortem/)

## 5. 权限与安全：在执行前检查真实动作

工单、网页和工具结果里的第三方文字是任务材料，不自动获得用户授权；可信工具也会载入不可信内容。危险常在能力组合处：私有内容可被诱导经另一可信工具外发。写入与外发应分开判断，fetch 参数、搜索词或浏览器 URL 即使不改远端记录，也已发送出去。允许域名不等于允许其中任意账号、操作与数据；同一云 API 也可能接收发往他人账号的上传。敏感出口宜用窄能力绑定实际接收方、操作和受控凭证；无法细分时，不默认组合敏感输入与通用外发。[(57)](https://invariantlabs.ai/blog/mcp-github-vulnerability)[(58)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)[(59)](https://www.anthropic.com/engineering/how-we-contain-claude)[(60)](https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/)

认证回答谁在调用，授权回答能对什么对象做什么。有效执行主体及其租户、角色与批准状态应来自已认证的宿主上下文，不能相信模型填写的同名参数；模型可指定目标用户、租户等业务对象 ID，执行端再按可信主体查其权限。MCP 这类会话关联 ID 不代替认证。凭证宜留在窄执行端，日志分清发起用户与实际执行身份。隐藏密钥减少暴露，却不能阻止滥用已允许的能力，数据去向仍须受控。[(44)](https://blog.cloudflare.com/code-mode/)[(61)](https://arxiv.org/html/2503.18813v3)[(62)](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)[(63)](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)[(64)](https://github.blog/ai-and-ml/github-copilot/how-githubs-agentic-security-principles-make-our-ai-agents-as-secure-as-possible/)

批准应引用后端真实保存的待执行动作。不要接受客户端重传一段历史和 approved=true，就认定动作已经获准。一个可检查的批准记录宜绑定调用者、工具来源、操作、对象或接收方、数据范围与实际参数，并定义期限、撤销和使用次数。签名用于检测其覆盖字段被改动，不证明当前用户或租户有权限，也不自动证明真人看过界面。执行前用可信记录重验这些条件，恢复时沿用同一边界。[(65)](https://ai.pydantic.dev/deferred-tools/)[(66)](https://github.com/vercel/ai/blob/main/packages/ai/src/generate-text/validate-tool-approvals.ts)[(67)](https://docs.openclaw.ai/tools/exec-approvals)

批准还可能依赖目标版本。用户确认的是某版脚本，等待期间别人改了同一路径，参数相同也可能已经不是同一含义。需要保护版本的动作，应保存批准依据，并在目标服务支持时采用条件写入。Cloud Storage 的代次匹配能让针对旧对象的迟到删除无法删掉同名新对象。先读版本再无条件写仍有竞争窗口；条件不匹配应重新评估，而不是自动改用最新版本直到成功。审批完整性、当前权限和目标版本应分别判断。[(68)](https://www.rfc-editor.org/rfc/rfc9110.html)[(69)](https://docs.cloud.google.com/storage/docs/request-preconditions)

拒绝和异常分支也属于安全实现。历史上一个 filesystem MCP 漏洞已做真实路径检查，却把越权异常当成“文件可能不存在”，转入更宽松的父目录检查，最终放行。权限拒绝应作为独立结果保留，让 loop 缩小请求或等待必要授权。重试、换工具或换环境不能因此扩大权限。安全回归应特意走拒绝、缓存命中、恢复和批准过期路径，而不只测试正常执行。[(70)](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/)[(67)](https://docs.openclaw.ai/tools/exec-approvals)

窄能力减少灵活性，审批增加等待，内容检查也会漏判或误判，应按风险组合。提示词和记忆帮助模型选动作；强制授权、执行限制和数据去向检查要放在实际必经路径，并测试整条链。[(71)](https://arxiv.org/html/2506.08837v2)[(72)](https://github.github.com/gh-aw/reference/safe-outputs/)[(73)](https://code.claude.com/docs/en/memory)

生命周期钩子（hook）是宿主自动执行的代码，启动配置、热加载和插件同样可能先于模型工具调用执行。信任门须在激活前：陌生项目配置先只作惰性数据查看，不让解析激活代码；会触发执行的编辑先暂存，批准后才发布到自动加载路径，先落盘再“保留/撤销”挡不住 watcher。已获准的固定配置可按明确范围复用信任，变更后重验；强制策略不能由 agent 自改。这不要求所有普通编辑都审批。hook 还须规定顺序、超时与失败策略：安全检查失败不放行，遥测失败不重做业务；afterRun 也可能对应失败或取消，通知前读真实终态。[(59)](https://www.anthropic.com/engineering/how-we-contain-claude)[(74)](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust)[(60)](https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/)[(50)](https://geminicli.com/docs/reference/policy-engine/)[(75)](https://cline.bot/blog/extend-cline-with-plugins-and-hooks)[(76)](https://langfuse.com/docs/observability/features/masking)

## 6. 执行环境：命令在哪儿跑，资源归谁收尾

执行脚本前，先确定工具实际连接的环境：工作目录、依赖与版本、环境变量、凭证、网络出口，以及是否允许交互。持久 shell 会留下上次的目录、变量和后台进程，独立子进程则通常更容易把每次调用的起点写清楚。前者省去重建状态的成本，后者减少隐含依赖，选择取决于任务需要。把环境身份和寿命纳入工具契约，明确重启后哪些文件仍在、哪些服务须重建；会话 ID 本身不能证明工作区已持久保存。[(77)](https://github.com/SWE-agent/SWE-ReX/blob/main/src/swerex/runtime/local.py)[(78)](https://code.claude.com/docs/en/agent-sdk/sessions)

无人值守执行宜显式选择非交互模式，配置标准输入、分页器和编辑器。PTY 是模拟终端的通道，程序发现连接终端时可能分页或等待确认；PIPE 主要传递字节，行为未必相同。Git 停在分页器里等按键，就不是“算得太慢”，继续加超时也没有帮助。确实需要交互时，工具应暴露可关联的进程身份、当前输出和输入入口，让下一轮有依据地继续，而非重新启动一个副本。[(79)](https://github.com/SWE-agent/SWE-agent/issues/1204)[(77)](https://github.com/SWE-agent/SWE-ReX/blob/main/src/swerex/runtime/local.py)

标准输出和错误输出应持续消费。管道容量有限，不读取会反过来阻塞子进程；全读入内存又可能拖垮宿主。一个实用起点是有界保存、明确截断、将必要完整输出写入可复取文件，再向模型返回摘要与定位。退出码和业务验证分别记录：零退出码表示程序报告成功退出，是否真的修复了工单仍看测试或产物。成本由此从模型上下文转到文件保存与检索，但不会凭空消失。[(80)](https://docs.python.org/3/library/subprocess.html)[(81)](https://github.com/openai/codex/pull/5258)

启动进程也意味着承担收尾责任。超时或取消后，要停止受控工作、回收进程，并处理仍由后代持有的输出通道。直接子进程退出，孙进程仍占着 PTY，工具就可能迟迟不返回。进程组、Windows Job、线程和协程的停止边界不同，宜用各运行时支持的管理方式并做实际停止测试，记录取消请求与已确认退出。单个 kill 调用成功只能证明它所承诺的动作，不能代替整棵执行链收尾。[(82)](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)[(83)](https://nodejs.org/api/child_process.html)[(84)](https://man7.org/linux/man-pages/man2/kill.2.html)

隔离也应按执行面检查。某个 Bash 沙箱不一定覆盖 Read/Edit、MCP、hooks 或浏览器；容器默认配置也不等于已经设了 CPU、内存和磁盘上限。逐项列出可读写目录、环境变量、套接字挂载与网络去向，并检查失败后会否退回限制更少的路径。临时环境便于清理，但任务仍需的补丁和验证结果应先转到约定的持久位置，环境回收后留下一个本机路径没有交付价值。[(85)](https://code.claude.com/docs/en/sandboxing)[(86)](https://learn.chatgpt.com/docs/agent-approvals-security)[(87)](https://gvisor.dev/docs/architecture_guide/security/)[(88)](https://docs.docker.com/engine/containers/resource_constraints/)

浏览器是另一种有状态环境。截图到点击之间页面会变化，坐标可能已指向不同对象；自动等待检查元素是否可见、稳定或可点击，不判断业务含义。具后果操作要在执行时核对页面来源与目标，执行后再读取真实结果。把点击成功、页面跳转和评审创建分别记录，才能在页面异常时知道该重试哪个动作，避免重做已经完成的写入。[(89)](https://playwright.dev/docs/actionability)[(90)](https://embracethered.com/blog/posts/2026/toctou-agent-what-you-click-is-not-what-you-get/)

## 7. 网络：请求究竟卡在哪一层

一次模型请求先可能在本地等待额度或空闲连接，再经过地址解析、建连、TLS 身份验证与加密、代理转发、请求发送、首段内容、后续流和连接清理。DNS 找到地址，代理转发请求，连接池复用连接。每层都可能让界面表现为“还在思考”，但处理方式不同：连接池等待先查本地并发与泄漏，证书错误查信任配置，发出请求后的读取超时则还涉及远端结果未知。记录错误阶段，才知道下一步该检查谁。[(91)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(92)](https://www.python-httpx.org/advanced/timeouts/)[(93)](https://www.python-httpx.org/advanced/ssl/)

timeout 只是某段等待的上限，要同时标明作用域。连接超时、两块数据之间的读取间隔、一次请求尝试和整个任务期限，不能互相代替。OpenAI Python 一条报告设置单次 30 秒、最多两次重试，最终等待约 92 秒，原因正是三次尝试加退避。这个例子并非超时失效，而是用户期待的范围与设置不一致。整个运行的 deadline 应由外层持有，把请求、流消费、退避、工具和必要收尾算在一起，向下传剩余时间。[(94)](https://github.com/openai/openai-python/issues/3828)[(95)](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_internal/model_retry.py)

期限还要选对时钟。本地耗时用单调钟；跨重启的业务到期宜保存明确 UTC 截止时间，约定权威时间或误差策略，恢复与派发前重验。未经契约，不把原始单调读数直接跨环境或重启用作业务期限；还须确认机器睡眠是否计入。跨服务传扣除已耗时的剩余预算，排队、退避和重试都不能重领完整时长。各阶段可设更短上限，但要结合正常延迟分布：过短制造重试负载，过长占住资源。[(96)](https://pkg.go.dev/time)[(97)](https://grpc.io/docs/guides/deadlines/)[(98)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)[(91)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

活动与进展也应分别测量。SSE 注释心跳说明连接有数据，不证明模型产生了有用内容；代理缓冲可能把上游连续输出攒住，使客户端长时间沉默。至少区分首内容等待、内容间隔和总耗时，并核对 SDK 的计时究竟止于模型输出结束，还是覆盖本地工具执行。升级 SDK、换代理或传输库后都要重测，不能只保留一个含义漂移的 latency 数字。[(34)](https://html.spec.whatwg.org/multipage/server-sent-events.html)[(99)](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)[(100)](https://github.com/vercel/ai/blob/543d42cdda96e2ecb59c0a28f197067b96b5ac8d/packages/ai/CHANGELOG.md)

逻辑结果确认之后，再有界地清理传输资源。收到明确失败终态却一直等 EOF，可能让后来的空闲超时掩盖原错误；在应用终态立即退出，也可能影响特定传输库的连接复用。宿主应先保存已确认结果，再按库的契约关闭或排空尾部，并给清理留上限。清理失败单独记账，不改写此前的业务结论。是否需要排空、排多少，没有跨所有 SDK 的统一答案。[(101)](https://github.com/openai/codex/issues/43140)[(102)](https://github.com/openai/openai-python/issues/3440)[(103)](https://github.com/openai/openai-python/pull/3510)

排错应在真正运行 agent 的环境里进行。终端 curl 能通，不说明应用采用相同 DNS、代理变量和证书。记录 SDK 与传输版本、端点、提供商请求标识、各阶段时间和连接池占用，再与代理及上游记录对照。客户端连接宜由明确的所有者创建、复用与关闭：每轮新建增加建连开销，忘关流又会耗尽池。慢首内容、长流、断流与取消都值得成为集成测试。[(104)](https://www.python-httpx.org/async/)[(105)](https://www.python-httpx.org/environment_variables/)[(106)](https://www.python-httpx.org/advanced/transports/)[(107)](https://github.com/anthropics/claude-code/issues/78529)

## 8. 错误处理与重试：先查上一次做到了哪里

创建评审的请求已经送达，服务创建成功，回包却丢了。客户端看到超时，此时应把业务结果记为未知；直接按“失败”重发，可能得到两份评审。副作用就是外部世界发生的变化，包括写文件、发消息和创建记录。错误处理首先要回答：故障是否暂时，上次可能执行到哪里，再做是否安全，还有多少预算。对只读查询，重复通常主要增加费用与负载；对写入，答案可能改变用户实际得到的结果。[(108)](https://stripe.com/blog/idempotency)[(91)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)

一个可实现的分支起点是：

- 参数、目标或权限条件不满足：报告具体原因，先修正条件或等待批准；保留明确拒绝。
- 宿主或工具实现的代码缺陷：保存原始异常与脱敏后的复现输入，进入修复路径；原样重试不算修复。若已派发写入，仍须核对实际效果。
- 已确认没有效果，或重复效果受可靠契约保护的暂时故障：进入有界重试，受总期限和尝试预算限制。
- 请求可能已产生效果：先按动作身份查询或对账；若目标系统提供合适的幂等机制，再按其规则继续。
- 无法安全判定的高影响动作：停在“未知”，保存证据并交给有权限的人决定。

这里“未知”是需要处理的业务状态，不是异常类型的别名。取消应走取消路径，预算耗尽也应结束或延后；二者都不该因为被 catch 捕获就变成网络重试。[(91)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(16)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

幂等表示重复同一逻辑操作不会重复产生该操作的效果。第 1 节的业务动作 ID 可以贯穿各次尝试，但只有目标系统支持对应契约时才有保护作用。核对操作键的去重窗口、同键换参数、首次失败和查询结果规则；参数哈希只说明输入相同，无法区分用户两次相同意图。若业务变更和执行收据能在同一数据库事务里提交，可以利用该资源内的原子性；跨到外部服务又是另一条边界。自行加一个不被目标识别的 header，并不会获得幂等保证。[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

支持幂等也不等于“重试到成功”。Stripe v1 会保存执行开始后的首次状态和响应，包括某些 500；沿用同键可能只拿回原错误，键被清理后再用又可能成为新操作。模型请求若含提供商托管工具，断流前还可能已经执行了一部分，所以要分别处理已完成效果、未派发提议和未知动作。客户端把失败尝试的增量丢掉，只能隔离尚未交给本地工具的内容。[(109)](https://docs.stripe.com/api/idempotent_requests)[(110)](https://github.com/anthropics/anthropic-sdk-python/issues/1470)[(4)](https://github.com/vercel/ai/blob/79b4ab869b38c5c702bc3a3bf055254b74648759/packages/ai/src/generate-text/stream-text.ts)

复合工具需要细到子操作。创建评审、上传附件、发通知是三个效果，最后一步失败不撤销前两步。Graph 批量请求外层 200 仍可能包含逐项失败；DynamoDB 的批量写入非原子，收到有效结果后按契约重试列出的未处理项。保存每个子操作的身份、收据、未处理项与未知项，才能只补该补的部分。若整个响应丢失，就不能猜哪些子项未处理，应重新进入核对。[(46)](https://learn.microsoft.com/en-us/graph/json-batching)[(111)](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html)[(112)](https://docs.restate.dev/develop/ts/durable-steps)

确定可重试后，再做退避、随机抖动与预算管理。SDK、网关、runner 和工具客户端若嵌套重试，最坏请求量会按各层尝试次数相乘；应明确重试责任，并统计底层总尝试、耗时和费用。服务器要求的等待超过剩余期限时，延后或停止，别截短后提前冲回去。同是 429，短时限流与消费额度用尽需要不同处理，状态码之外还要读错误体。[(91)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)[(113)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)[(114)](https://platform.claude.com/docs/en/api/rate-limits)[(115)](https://github.com/pydantic/pydantic-ai/blob/7db7a4d8c4b7b7b85b8636cf0b6e3305bafb5167/pydantic_ai_slim/pydantic_ai/retries.py)

重新生成模型响应、切换提供商和补偿业务动作也应显式区分。切换前检查工具能力、历史形状、必要状态及获准的数据接收范围；只有响应 ID 而没有可重建历史，换路由并不能迁移状态。补偿则是新的业务动作，需要自己的授权与结果，可能失败，也可能无法完整还原。第 10 节将处理另一种问题：当宿主本身退出后，如何重建这里所需的判断。[(116)](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router_utils/pre_call_checks/deployment_affinity_check.py)[(117)](https://openrouter.ai/docs/guides/routing/provider-selection)[(118)](https://github.com/BerriAI/litellm/issues/27967)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

## 9. 上下文与记忆：下一次模型真正看到什么

模型使用的是宿主实际构造的输入：指令、任务、选中历史、工具定义和观察。构造输入是读取与转换视图，不应把重排的旧记录、目标复述或检索片段再追加成新用户事件。历史写入按事件身份与来源接纳新增内容，不能按文本去重，用户可能真的再说一次相同的话；合成摘要若需持久保存，也要有明确类型与写入责任。排查“失忆”依次问：事实是否仍存、是否进入实际请求、模型怎样使用，而非只猜最终回答。[(119)](https://pi.dev/docs/latest/compaction)[(120)](https://swe-agent.com/latest/usage/trajectories/)[(121)](https://github.com/openai/openai-agents-python/issues/4069)[(122)](https://github.com/openai/openai-agents-python/pull/4181)

每轮还要组装生效指令与配置，明确全局、项目和目录规则何时加载、怎样合并、冲突怎样处理，保留来源与实际结果。文件存在不等于已加载，后拼接也不保证覆盖。历史续接与配置继承是不同契约：Responses 通过 previous_response_id 续接时，上一请求顶层 instructions 不自动继承。[(73)](https://code.claude.com/docs/en/memory)[(3)](https://developers.openai.com/api/docs/guides/migrate-to-responses)

输入选择可以按下一步的依赖决定，而不是先找一个通用压缩比例：

- 只依赖近期对话的短任务，保留近期上下文最直接，但别切坏未完成的协议单元。
- 连续推进同一长任务，用摘要保留目标、已验证状态和未完成项；代价是生成摘要与核验遗漏。
- 需要某个旧事实或文件细节时，按来源检索相关片段，付出检索延迟来减少无关输入。
- 探索能独立完成、主任务只需结论和证据时，可隔离为子任务，承担交接与集成成本。

这些策略可组合，以实际续做检验：能否找对文件、记住待批准动作、分清验证状态，而不只看摘要是否流畅。[(123)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)[(124)](https://factory.ai/news/evaluating-compression)[(2)](https://www.anthropic.com/engineering/building-effective-agents)

预算要按真实请求计算。token 是模型处理和计费的单位，没有固定的中文字符换算；工具定义、长结果、图片、音频和输出余量都可能占空间。若估算只看文字，多模态输入就可能压缩后仍然超限。宜先减少无关观察，通过分页、范围读取和外部文件保留大数据，再安排压缩时机。较小单次请求不一定带来较小总成本：漏掉关键事实后重新搜索，也会把省下的 token 花回来。[(125)](https://github.com/openai/codex/issues/33493)[(126)](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/core/src/compact_remote_v2.rs)[(24)](https://developers.openai.com/api/docs/guides/reasoning)[(124)](https://factory.ai/news/evaluating-compression)

工单摘要应保留目标、已验证与未验证改动、失败尝试及原因、文件和产物位置、待批准动作及证据入口。“计划测试”不能写成“已通过”，完成状态由执行层维护。连续压缩需合并旧摘要与新进展，调用和结果等协议单元不能从中间切开。[(124)](https://factory.ai/news/evaluating-compression)[(127)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)[(128)](https://www.liuvv.com/p/412550b7.html)

压缩还须证明覆盖范围：只读最近 N 条，不能据此清空整份历史。保守起点是只换模型输入视图，原始证据按权限和留存政策保存；也不能为补全而把过滤策略故意排除的数据重新发给模型。若确需替换存储，将所读范围、版本与服务端响应标识绑定为同一次压缩的基底，在同一串行或条件提交边界核对版本并只替换已覆盖部分；冲突就重建，覆盖不明就暂缓。异步返回后取“最新”标识，或先检查再无条件清空，都可能用旧摘要删掉新事件。[(129)](https://github.com/openai/openai-agents-python/pull/3827)[(130)](https://github.com/openai/openai-agents-python/pull/4293)

有不透明协议状态时，先选合法续接方式。服务端专用压缩可能保留必要状态，自写摘要另开上下文则是有损重建；换历史前缀后，旧状态能否复用仍由接口决定。不能因此断言压缩总会破坏状态，接口可能提供带签名摘要。模型前缀缓存减少重复计算，不筛选事实，也不负责长期记忆。[(25)](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)[(131)](https://platform.claude.com/docs/en/build-with-claude/compaction-thinking-blocks)[(132)](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)

长期记忆服务于未来任务，应挑选稳定且有用的事实，并附来源、范围、时间与失效规则，区分用户明确要求、环境事实和模型推断。项目路径变化、权限撤销或用户改变决定，都需要更新或作废旧条目。写入、检索、进入输入、被正确采用是四个环节，测试应覆盖更新、时间关系和无答案时的处理。共享记忆还需约定写入者、版本与冲突处理；记忆可以指导行为，授权仍由执行路径决定。[(133)](https://arxiv.org/html/2410.10813)[(134)](https://aclanthology.org/2026.findings-acl.1337.pdf)[(135)](https://www.notion.com/blog/building-shared-memory-for-ai-agents-in-notion)[(73)](https://code.claude.com/docs/en/memory)

计划与反思要引入新证据：测试或工具给出的具体结果能约束下一步，无新观察的“再检查”可能只重写旧假设。压缩阈值、工具策略和额外思考应在模型升级后复测，保留仍改善结果的部分。[(136)](https://arxiv.org/html/2310.01798)[(137)](https://arxiv.org/html/2303.11366)[(138)](https://www.anthropic.com/engineering/claude-think-tool)

## 10. 持久化与恢复：进程回来以后从哪里继续

第 8 节假设宿主还记得发生了什么；持久化解决宿主退出后怎样重建同样的判断。checkpoint 是在某个边界保存的状态，必须说明覆盖哪些对象、何时提交和恢复从哪一步开始。重试增加一次执行尝试，恢复重新取得控制位置，回放则按选定方式读取或重演历史。三者可以组合，但不能都实现成一个不加区分的“再跑一次”。[(139)](https://docs.temporal.io/workflows)[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)

不用工作流引擎也能先做一个小版本。以创建评审为例，以下是建议的提交顺序，不是任何 SDK 自动提供的字段或保证：

1. 可靠保存业务动作身份、参数、批准依据与待执行状态；需要等待时，把等待位置一起提交。
2. 执行前重验条件，先保存本次尝试开始的记录，再向工具派发请求。这样崩溃后能识别“可能已经发出”的窗口。
3. 收到结果后追加成功收据、明确失败或未知事实，再推进相应控制位置；相关本地记录可在同一数据库事务内提交。
4. 重启后，有可信收据就继续后续步骤；尝试已开始却无结果就按第 8 节核对；确知尚未派发的动作才在重验授权后执行。

单一写入者加支持事务的本地数据库，是容易检查的起点。它增加保存与同步成本，却让恢复有据可查。开始记录可能写完而请求还没发出，远端也可能成功而本地收据尚未保存；因此这一顺序识别不确定窗口，不消除它。只有业务变更和收据同属一个原子事务的资源，才可利用该事务一起确认。恢复测试要查看独立效果记录或目标系统，不能只看最终对话状态。[(7)](https://www.dbos.dev/blog/durable-code-execution-vs-transactional-execution)[(140)](https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal)[(141)](https://github.com/langchain-ai/langgraph/issues/9106)

保存范围还要包括协议历史、控制位置、动作记录、工作区引用和解释它们的代码版本。会话日志在，沙箱文件仍可能过期；容器重启，内存、连接和后台进程也可能已消失。把会话与动作状态放在环境之外，可以把执行器损坏当作一次可处理的工具故障。整个 agent 保存成一个大步骤较简单，失败时重做范围也大；在外部写入和长等待处切分，恢复更细，同时增加记录、版本和恢复分支的维护工作。[(8)](https://www.anthropic.com/engineering/managed-agents)[(142)](https://modal.com/docs/guide/sandbox-snapshots)[(143)](https://docs.temporal.io/activities)

持久执行引擎各有恢复契约。重跑式引擎可复用已完成且已保存的任务结果，但恢复仍可能从入口或节点开头执行，未完成任务也可重跑，并非暂停后的下一行。重跑范围内的副作用和非确定性选择，应放进记录结果的任务或独立提交的步骤，外部效果仍须防重复并核对未知结果；审批绑定已保存的选择，恢复不能重抽目标。框架暂停/控制信号须按契约传播，别被 catch 当普通失败重试，真实暂时故障仍按第 8 节有界恢复。旧历史须产生兼容编排决定，不要求模型重生成同一句话。快照式引擎可恢复内存与位置，仍受环境、连接和存储约束。长等待、跨进程或多步外写时再评估；无论哪种，都需监督者发现未完成任务并重新调度。[(139)](https://docs.temporal.io/workflows)[(144)](https://trigger.dev/blog/v3-announcement)[(145)](https://restate.dev/blog/why-checkpointing-is-not-production-grade-durable-execution)[(146)](https://docs.langchain.com/oss/python/langgraph/functional-api)[(147)](https://docs.langchain.com/oss/python/langgraph/interrupts)

“文件已保存”要分清完整、原子可见和耐久。在支持相应语义的本地文件系统上，可在目标目录写临时文件，处理短写并校验内容，按任务设置必要权限等元数据，按耐久要求同步文件，再同文件系统原子替换目标，必要时同步目录；每步错误都须检查。原子替换不会继承旧文件的可执行位，不能因用解释器测试通过，就认定真实直接启动也成功；也别机械复制高权限位。完整写入避免半文件，原子替换避免中间版本，耐久同步处理崩溃保留，实际保证仍取决于文件系统与硬件契约。[(148)](https://man7.org/linux/man-pages/man2/write.2.html)[(149)](https://man7.org/linux/man-pages/man2/rename.2.html)[(150)](https://man7.org/linux/man-pages/man2/fsync.2.html)[(151)](https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp)[(152)](https://docs.python.org/3/library/os.html#os.replace)

数据库、快照和对象存储各遵自己的提交方式。运行中数据库宜用一致性备份接口，别只复制主文件而漏掉依赖日志；文件快照也可能截到仍在写的内容。对象存储分片上传完还可能需要完成发布并核对最终结果，不能套用本地 rename 的保证。JSONL 可作记录格式，但多写者、短写、损坏恢复仍需设计，关键动作记录不能因解析失败而悄悄跳过。[(153)](https://www.sqlite.org/atomiccommit.html)[(154)](https://www.sqlite.org/howtocorrupt.html)[(155)](https://developers.cloudflare.com/sandbox/files/save-a-sandbox-automatically/)[(156)](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html)

任务结果与交付另存状态：临时文件生成、持久发布、目标用户可访问、消息渠道接受通知，是不同事实。若结果引用和待发通知同属一个数据库，可同事务保存，再由派发器发送，这就是 outbox；重启后只补交付，不重做已成功的评审。发送后、本地标记前仍有未知窗口，要按消息凭据或目标幂等契约核对。平台接受不证明用户已读，限时链接也受凭证寿命影响；交付前应检查正确版本、权限和有效期。[(157)](https://docs.slack.dev/reference/methods/files.completeUploadExternal/)[(158)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)[(159)](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)[(160)](https://docs.particular.net/nservicebus/outbox/?version=core_9)[(161)](https://docs.slack.dev/reference/methods/chat.postMessage/)

最后确定旧任务由哪个版本接管。能读旧 JSON，不代表新代码仍按原含义解释节点、工具 schema 或批准规则。可以为有边界的运行固定版本，在任务边界升级；确需新版本接手，就对真实旧记录做兼容测试或迁移。用户有意重新运行或分叉，也应与恢复原动作区分。恢复能力由保存、兼容解释、重新调度和提交所有权共同组成，第 12 节再处理多个执行者接管时的冲突。[(162)](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning)[(163)](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_state.py)[(164)](https://docs.langchain.com/oss/python/langgraph/checkpointers)[(165)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

## 11. 插话、暂停与取消：让旧任务正确让路

评审正在创建，用户说“先别发，改一下描述”。这条消息若只排在旧任务后面，就无法阻止已启动的写入。产品要明确新输入的含义：成为下一任务、拒绝当前输入、在安全点调整后续计划，或取消旧运行。安全点是宿主检查控制消息、决定还能否启动下一动作的位置。控制入口应保持响应，不能被一个长工具占住；代价是要显式处理控制与执行之间的状态转换，而非只写一条顺序调用链。[(166)](https://docs.langchain.com/langsmith/rollback-concurrent)[(167)](https://docs.openclaw.ai/concepts/queue)[(168)](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)

入口确认分“已收到”“已持久保存”“当前运行已采用”，按承诺边界确认并用稳定身份查询。外部事件推送（Webhook）的签名有效也不保证事件唯一、有序：按容量准入，持久接纳后及时应答，再异步处理；用事件/投递身份去重，同 ID 异内容与保留期也须定义，业务效果仍按动作身份保护。到达顺序或粗时间戳不能胜过权威版本与状态，必要时查询对账，别让迟到旧事件回滚新状态。内存去重挡不住重启，界面发送成功也不代表本轮已采用。[(169)](https://github.com/openai/codex/blob/rust-v0.149.1/codex-rs/core/src/session/turn_input.rs)[(16)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)[(170)](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)[(171)](https://docs.stripe.com/webhooks)

断线后先分清恢复对象：重订阅界面只恢复观察，重新生成会发出新模型请求，从 checkpoint 恢复则取回宿主控制位置。若应用支持游标与补发，要按具体请求、响应或流的身份和已确认位置续接、去重，检查缺口与过期；一个运行的多条流不能共用无归属的序号。无可靠补发时，重新取当前状态并标明缺失，不盲拼旧流或重复业务。[(172)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(173)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)[(174)](https://agentclientprotocol.com/protocol/v1/session-setup)

再约定返回快照、全量事件还是增量。AI SDK 的可恢复流示例默认重播完整流，客户端重建中断响应；只发剩余内容则须保留已有部分，刷新页面后这些内存状态又可能丢失。同一响应续传与新生成也不同，新内容不能直接拼到旧半句话后当作完整结果。合并前核对响应身份、范围与完成状态，不假定所有协议都有恢复能力。[(172)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(174)](https://agentclientprotocol.com/protocol/v1/session-setup)

取消应沿执行链逐段确认：界面停止等待，后端收到取消，宿主停止调度，模型请求中止，工具协程、线程或进程退出，远端操作停止。AI SDK 的可恢复模式里，客户端 stop 可以只是断开消费，停止后台工作需另一条后端路径；普通流在断开时又可能因消费方式不同而停止。界面只报告已确认阶段，远端未确认效果仍保留未知。暂停通常是暂不启动后续工作，已提交动作能否撤销要看目标服务。[(172)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(173)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)[(175)](https://anyio.readthedocs.io/en/stable/threads.html)[(176)](https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination)

控制命令和结果要绑定具体运行或执行代次。过期 stop 不能停止新运行，旧工具晚到不能把新任务覆盖成完成，但真实的远端收据仍应保存供核对。长审批等待恢复时，也要重验运行仍活跃、批准仍有效。取消不应只覆盖眼前的一次异步等待：后续排队输入、摘要和自动续跑都可能再次启动工作，必须一起检查控制状态。[(172)](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)[(67)](https://docs.openclaw.ai/tools/exec-approvals)[(170)](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)[(177)](https://github.com/earendil-works/pi/issues/9783)

后台工作要有寿命足够的拥有者、期限和结果回收方式；父任务结束前等待子工作收尾或明确交接，长审批则保存等待位置。异步实现须明确异常怎样传播，不能假定一个并行调用报错就会停止其余调用。取消还可能打断 finally 中的异步清理：按运行时契约，仅给必要清理有界保护和短预算，结束后继续传播取消，别无限保护业务。有同任务、逆序退出要求的取消上下文，须按该契约关闭，不能把所有 close 一律并行化。[(178)](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)[(147)](https://docs.langchain.com/oss/python/langgraph/interrupts)[(179)](https://anyio.readthedocs.io/en/stable/cancellation.html)[(180)](https://docs.python.org/3/library/asyncio-task.html)[(181)](https://github.com/modelcontextprotocol/python-sdk/pull/353)

## 12. 并发、调度与预算：多跑几个为何更慢

并发首先增加的是资源竞争。限制正在运行的数量，挡不住无限待办占满内存；有界队列限制积压，准入决定是否接受新工作，速率限制约束单位时间请求，公平调度决定谁先获得资源。宜分别测等待年龄、首次启动时延和真实执行时长。低 CPU 加长队列可能卡在槽位、连接或调度，继续增加模型并发未必有用。可合并的状态刷新与用户明确下达的写动作，还需要不同的积压处理规则。[(182)](https://docs.ray.io/en/latest/ray-core/patterns/limit-pending-tasks.html)[(183)](https://hatchet.run/blog/multi-tenant-queues)[(184)](https://builder.aws.com/content/3EuRcgkTP1MI0c7zM8W6HL3WIqA/avoiding-insurmountable-queue-backlogs)

阈值还需配套背压：消费跟不上时，向支持等待的生产者传递暂停；不能暂停的部分则选择有界存储、取消或只丢可舍弃进度，关键动作收据不能这样丢弃。本地暂停读取不证明远端生成已停，仍要核对生产端语义。[(185)](https://nodejs.org/api/stream.html)[(186)](https://github.com/openai/openai-agents-python/blob/main/src/agents/tracing/processors.py)

预算要在派发前分配，完成后结算。一个模型步骤可含多个工具，一个代码工具可发多次请求，子 agent 也消耗环境与模型额度。可硬计量的额度应由父方在消费前原子预留，或分成不重叠份额，完成后结算并回收未用额度；给两个子任务各复制同一份余额，事后正确归总也会超支。运行、用户、租户与共享提供商可能各有限额。token、费用、请求数、墙钟、CPU、内存和磁盘不能互换；响应后才知的费用不能仅靠事后记账承诺精确硬封顶。解析失败仍可能花钱，缺失用量应标未知，不能记零。[(11)](https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/src/minisweagent/agents/default.py)[(12)](https://ai.pydantic.dev/agents/)[(187)](https://trigger.dev/docs/concurrency)[(188)](https://pkg.go.dev/golang.org/x/time/rate)

可变对话与控制状态先由一个执行者提交，仍可并行等待工具或接收控制消息。但只读不等于独立或共同快照：工单从待办移到完成，两次各读“最新数量”再相加可能重复计数。若结论依赖同一状态，采用后端支持的共同快照、可比较版本或冻结输入并核对；无法获得一致视图就说明时点差异，串行调用也不自动解决。多个执行者确需共享写入，再选择事务、版本冲突检查或分支合并；并行计算与提交顺序分别决定，不靠模型口头拿锁，也不必先装分布式锁。[(189)](https://docs.restate.dev/ai/patterns/sessions)[(168)](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)[(190)](https://cursor.com/blog/scaling-agents)[(191)](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-READ-COMMITTED)

跨进程接管时，租约过期只说明旧执行者可能失联，它仍可能从长暂停中恢复。可为接管分配递增执行代次，即 fencing token，由接收提交的一方拒绝旧代次。必须是接收端检查，而非旧进程先在本地看锁是否仍有效。它保护的是所覆盖的状态提交；若外部服务不支持相同条件，就不能阻止旧执行者早已发出的写入，仍需第 8 节的幂等与核对策略。[(165)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)[(140)](https://temporal.io/blog/the-immortal-life-of-pi-running-the-pi-coding-agent-on-temporal)

等待也会占槽位。父任务占满槽后等待子任务，子任务无槽可用，就会死锁。可在持久等待时释放父槽、分开资源池或预留容量；恢复须重新准入，并测试故障后容量回收与积压恢复。[(187)](https://trigger.dev/docs/concurrency)[(192)](https://trigger.dev/blog/incident-report-jun-22-2026)

服务化部署还须设计排水：停止新业务准入，按策略让已接工作限时完成或取消，仍允许必要收尾与收据写入，最后关闭共享客户端和数据库。控制、续租与保存结果要留有必要调度和连接容量，避免被普通工作挤满。内部收尾期限应短于平台强制终止期限；强杀不保证 finally 执行，恢复仍靠此前持久记录。部署测试应在工具执行和保存收据途中触发退出；简单 CLI 无须为此建设完整调度平台。[(98)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)[(193)](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)[(194)](https://docs.temporal.io/encyclopedia/workers/worker-shutdown)

## 13. 多 agent：按任务独立性拆分

工单任务可以让一个子 agent 查相关代码，另一个独立审阅补丁；两者同时改同一脚本，就会争抢隐含决定。多 agent 适合独立搜索、候选方案和输入输出清楚的审阅。顺序依赖强的工作，则可能把并行收益花在重复上下文和协调上。若已决定采用多 agent，保守起点是一个写入者加独立审阅者：审阅者用较干净的上下文减少继承原假设，咨询型子任务则可得到理解问题所需的背景。[(195)](https://cognition.com/blog/multi-agents-working)[(196)](https://www.anthropic.com/engineering/multi-agent-research-system)

独立性要看能带回什么新证据。Anthropic 的并行编译器实验给多个 agent 独立仓库副本，遇到共同构建问题时仍重复处理同一瓶颈；改进任务切分和测试才使并行更有用。共享同一个错误 API 假设的执行者，即使彼此同意也没有增加证据。先分清哪些探索能分别产出结果，哪些决定必须先统一，再计算多执行者是否值得。[(197)](https://www.anthropic.com/engineering/building-c-compiler)[(198)](https://jvertrees.hashnode.dev/ten-failure-modes-from-a-year-of-running-an-agent-harness-part-1)

交接宜包含目标、范围、已有证据、权限、预算、预期产物、未完成项和需要父方决定的问题。子任务说“测试成功”，父方应能找到命令、环境、实际结果与对应版本。收到报告后，还要把重要发现纳入主任务计划，并在必要时更新兄弟任务；收到与采用不是同一件事。最终应有明确集成人负责冲突处理、整体验证和用户交付，不能用子任务各自结束代替整体完成。[(199)](https://arxiv.org/abs/2503.13657)[(195)](https://cognition.com/blog/multi-agents-working)

交接还应记录谁在等谁，拒绝循环依赖或将阻塞决定交还父方；子任务等待仍受父方分配的期限和预算约束。这样工作拆开后，主任务仍能判断下一步由谁推进。[(187)](https://trigger.dev/docs/concurrency)[(178)](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)

隔离范围也不止源码。Git worktree 分开工作文件，却可能共用数据库、端口、缓存、凭证或后台服务。并行写入需检查这些共享对象，建立环境隔离和合并规则，并将成本计入父任务预算。取消或替换后，旧子任务沿第 11 节的身份规则归档结果与收据，不覆盖新计划。具备可检查的交接与集成条件，才值得扩大并行。[(200)](https://trigger.dev/blog/parallel-agents-gitbutler)[(168)](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)

## 14. 日志与轨迹：留得下来，也查得回去

这里把一次运行中模型输入输出、工具提议、授权、真实执行和结果核对的关联记录称为轨迹。恢复记录决定能否继续，诊断日志解释局部现场，trace 关联跨组件操作，界面展示用户关心的进度。它们可共用事件来源，但保存责任不同：动作身份、批准依据、执行状态与关键收据应可靠保存；完整模型正文按权限与留存政策受控采集，未保存的细节就明确不能精确复现。不要先要求无条件全量记录，再靠末端脱敏补救。[(26)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)[(120)](https://swe-agent.com/latest/usage/trajectories/)[(16)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

最小事件记录宜关联运行、业务动作或模型调用、执行尝试、事件类型、时间与正文或产物引用，字段名可自定，关联必须查得回。复现还需有效配置：代码与依赖、实际模型参数、提示和工具版本、功能开关、上下文策略及后端，不能只记 commit 和模型名。按权限保存脱敏配置快照或可反查的版本指纹，复现用实际发布构建与配置，不记录凭证；外置正文引用须有访问控制、保留期与完整性检查。验收时拿一个远端评审号，反查动作、尝试、批准、模型调用及配置，而不依赖界面摘要。[(26)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)[(120)](https://swe-agent.com/latest/usage/trajectories/)[(201)](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md)[(202)](https://www.anthropic.com/engineering/april-23-postmortem)

回到第 1 节的创建动作：先留下某次尝试超时的事实，随后查到远端评审，就追加成功收据并推进交付；不要把原超时覆盖掉，也别另造一个动作掩盖重试。对当前状态而言可以继续，对诊断而言仍要解释为何进入过恢复。事实追加和当前状态投影各有用途，后者便于运行，前者使变化可追溯。[(6)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)[(108)](https://stripe.com/blog/idempotency)[(16)](https://docs.openclaw.ai/plugins/sdk-channel-outbound)

排查“用户拿到的链接打不开”，可从结果往前查：先核文件版本、发布状态和收件人权限；再列出该动作的所有尝试，检查实际参数与批准；随后对照已留存的模型输入、原生输出和解析结果；最后沿请求标识查网络及执行环境。这样能把错误落在产生分歧的边界，而非先猜提示词。最早可见分歧只是调查入口，仍需检查它是否根因，以及后续恢复是否又引入问题。[(120)](https://swe-agent.com/latest/usage/trajectories/)[(203)](https://arize.com/blog/ai-agent-debugging-four-lessons-from-shipping-alyx-to-production/)

span 表示一段被观测操作，trace 把相关 span 串起来。一段逻辑模型调用可能含多次网络尝试，工具提议也要与真正执行区分。跨进程记录源端时间、采集时间、事件身份和传播关系：时钟可能偏移，同一父操作下的子任务可能并行。界面按时间排序方便浏览，推断先后还要看消息发送与接收，推断因果则需要进一步证据。[(26)](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)[(204)](https://opentelemetry.io/docs/specs/otel/trace/api/)[(205)](https://opentelemetry.io/docs/specs/otel/logs/data-model/)[(206)](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)

遥测可以采样或丢失。有界内存队列、导出失败、进程退出、后端索引和界面展示都可能留下缺口，长 span 还可能等结束才入队。没有看到 trace 不能证明动作没执行，所以关键收据不宜仅靠遥测保存。监测丢弃、截断、损坏与导出失败，明确证据完整程度；诊断保存越丰富，存储成本和敏感数据暴露面也越大。[(186)](https://github.com/openai/openai-agents-python/blob/main/src/agents/tracing/processors.py)[(207)](https://langfuse.com/docs/administration/data-retention)

先最小化采集，再在离开信任边界前脱敏。输入、输出、元数据、事件名、附件和所有导出器都要检查；一个并列的脱敏观察者不会自动阻止其他出口看到原文。输出设字节上限、转义控制字符并记录截断位置，避免每轮重复保存完整前缀。OpenAI 的 reasoning summary 并非原始推理 token；这类内容宜作为可观察输出保存，不据此补出未观测的内部步骤。[(208)](https://openai.github.io/openai-agents-python/tracing/)[(76)](https://langfuse.com/docs/observability/features/masking)[(209)](https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/)[(24)](https://developers.openai.com/api/docs/guides/reasoning)

## 15. 回放与评测：让事故变成可验证的修复

先约定“回放”做什么。浏览历史只读记录；固定模型与工具响应重跑宿主，主要检查控制代码；从 checkpoint 继续可能调用真实服务；改动某一步再运行则是新实验。默认隔离回放副作用，未录制请求应明确失败，别悄悄穿透生产接口再创建一份评审。固定响应能稳定重放已录制交互，不能恢复未记录的调度、计时或文件系统现场；真实环境测试再检查当前工具与权限，两者互补。[(210)](https://docs.langchain.com/oss/python/langgraph/use-time-travel)[(211)](https://github.com/clay-good/agent-replay)[(212)](https://vcrpy.readthedocs.io/en/latest/usage.html)

测试按成本分层：解析、状态转换、预算和授权门用无模型确定性测试；录制输入输出检查适配、恢复和兼容；少量真实端到端任务检查组合效果。但替身类型通过，不证明真实传输与序列化通过，内存后端通过也不代表生产数据库通过。给实际使用的适配器、传输和后端跑同一小组契约用例，报告已执行、跳过与不支持；关键依赖缺失导致 skip，不能算发布通过。日常仍用廉价替身，发布保留少量隔离副作用的真实冒烟，并确认事故用例修复前失败、修复后通过。[(213)](https://pydantic.dev/docs/ai/guides/testing/)[(214)](https://github.com/openai/openai-agents-python/issues/992)[(215)](https://github.com/langchain-ai/langgraph/issues/8534)[(216)](https://github.com/langchain-ai/langgraph/pull/8537)

每个用例写清初始状态、输入和可检查结果，验证文件、远端对象及不变量。除非顺序是安全要求，不必强制唯一工具路线；未经批准发布、重复创建或把失败测试报成通过，不能被其他分数抵消。[(217)](https://ai.pydantic.dev/testing/)[(15)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)[(218)](https://hamel.dev/blog/posts/llm-judge/)

评分器也要用反例测试。一个 span 评估示例用 any 判断“存在一个不是 delete_database 的 span”，同一轨迹只要还有一次正常读取，就可能通过。它证明的是存在安全动作，所需条件却是全程没有危险动作。应构造安全与危险并存、只有危险、只有安全和记录缺失等用例。即便遍历整棵 span 树，采样或遗漏仍让“从未越权”缺乏充分证据，此时应标缺证据，而非绿色通过。[(219)](https://pydantic.dev/docs/ai/evals/evaluators/span-based/)[(220)](https://pydantic.dev/docs/ai/api/pydantic_evals/evaluators/)[(221)](https://github.com/vercel-labs/agent-eval)

模型实验须保持第 14 节的实际配置可比，另固定数据集与评分规则版本；judge 是评分程序或模型，也可能误判。一次 trial 应是真实执行，复制轨迹或重新评分不增加独立样本。固定温度不保证路线一致，重要比较通常需多次运行。清理可能泄露前次答案的 Git 历史、缓存和外部资源，分别报告质量、成本、延迟与基础设施失败，不只留成功样本。故障样本用于排错，总体表现则从目标任务分布抽代表样本。[(15)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)[(222)](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)[(221)](https://github.com/vercel-labs/agent-eval)[(223)](https://inspect.aisi.org.uk/scoring-workflow.html)

最小回归组可以按边界组织，而不必按框架堆测试：

- 模型交互：交错工具增量、缺少终态、压缩后续做；断言正确配对、覆盖范围及未完成内容不执行。改等待、缓存或上下文逻辑时，按实际配置覆盖“运行—空闲—继续—插话／恢复”及后续多轮，不能只测新会话。
- 业务效果：回包丢失、批量部分成功、批准后参数或版本变化；断言真实效果次数、结果核对和授权范围。
- 控制恢复：外部成功而收据未保存时崩溃、取消后旧结果晚到、通知派发前崩溃；断言恢复位置与后续动作。
- 资源与交付：队列满、遥测丢失、临时文件不完整或用户无访问权；断言系统报告实际缺口，不虚构成功。

并发竞态可用可控暂停点安排交错，比随机 sleep 更容易稳定重现。新的恢复代码也要进入回归，而不是只验证最初故障消失。[(39)](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.test.ts)[(170)](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)[(141)](https://github.com/langchain-ai/langgraph/issues/9106)[(111)](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html)[(160)](https://docs.particular.net/nservicebus/outbox/?version=core_9)

第一天可先留一个可重置的小任务，用一条命令走通模型提议、工具执行、结果续接与验收，能对照实际输入、原生输出、解析结果和执行记录，快速完成“改—跑—看”。日常用替身或录制路径，协议、依赖、执行环境变化及发布前再跑接近生产形态的冒烟；采用 SDK 或托管框架，也先用该样例验证失败可定位、状态可重置、结果可导出，不必先造调试平台。[(224)](https://docs.langchain.com/langsmith/local-dev-testing)[(225)](https://openai.com/index/harness-engineering/)[(226)](https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md)

第一版保留单运行、单写入者和少量工具，带完成条件、授权门、总期限与可查动作记录；自动重试远端写入前就处理未知结果。长等待或重启需要持久恢复，共享写入与接管需要冲突和执行代次，确有独立且值得并行的工作才增加多 agent。每次升级都衡量所解决的失败、等待与维护成本，模型更新后重测可删的能力补丁。[(2)](https://www.anthropic.com/engineering/building-effective-agents)[(227)](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)[(228)](https://replit.com/blog/free-the-models)[(15)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
