[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-01"></a>

## 1. 先看清一次动作：harness、loop 与完成条件

<a id="boundary-closure-011"></a>

### boundary-closure-011 · SQS SendMessageBatch request and per-item response

作者／组织：AWS。类型：官方文档／规范。版本／日期：current API reference, accessed 2026-10-13。读取日：2026-10-13。

用途：同一 HTTP 200 可同时包含 Successful 与 Failed；成功项包含关联 Id 和服务端 MessageId，失败项包含 Code/Id/SenderFault。

选读范围：概述；Response Syntax / Elements。限制：读概述及 Response Syntax/Elements；成功表示入队接受，不能推出用户收到或业务被消费；未调用队列。

[公开原文](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessageBatch.html)

<a id="boundary-closure-012"></a>

### boundary-closure-012 · Slack chat.postMessage response and failure semantics

作者／组织：Slack。类型：官方文档／规范。版本／日期：current API documentation, accessed 2026-10-13。读取日：2026-10-13。

用途：成功响应返回 channel、ts 及服务端解析后的 message，可记录消息身份；调用方须检查 ok。

选读范围：Response；错误条目。限制：读 Response 和错误条目；未证明 client_msg_id 有跨重试幂等保证，不能依据错误表存在该字段就承诺安全重发；未发送消息。

[公开原文](https://docs.slack.dev/reference/methods/chat.postMessage/)

<a id="boundary-closure-013"></a>

### boundary-closure-013 · Twilio Message resource status contract

作者／组织：Twilio。类型：官方文档／规范。版本／日期：2010-04-01 API, current documentation。读取日：2026-10-13。

用途：queued 表示 API 接受并排队，sent 是上游运营商接受，delivered 是运营商及可用时终端的投递确认；这些并非同一完成事实。

选读范围：SID；Message Status values；status callback 字段。限制：只读 SID、Message Status values 与 status callback 字段；文档属性摘要与状态表对 read 渠道范围有差异，正文仅说特定支持渠道，不列完整名单；未发消息。

[公开原文](https://www.twilio.com/docs/messaging/api/message-resource)

<a id="durable-orchestration-033"></a>

### durable-orchestration-033 · Turn runtime semantics

作者／组织：restatedev/agent contributors。类型：官方文档／规范。版本／日期：main accessed2026-10-13。读取日：2026-10-13。

用途：pending tool的完成/取消竞争应保留真实赢家；有pending工作时文本只算候选答复，不能作为已完成交付。

阅读范围：正文 Ownership / Steering / Pending tools / Budgets / Interruption。限制：该参考实现的具体数值不是通用默认；不把其model guardrail当安全证明

[公开原文](https://github.com/restatedev/agent/blob/main/docs/turn-runtime.md)

<a id="durable-orchestration-034"></a>

### durable-orchestration-034 · Termination

作者／组织：Microsoft AutoGen。类型：官方文档／规范。版本／日期：stable accessed2026-10-13。读取日：2026-10-13。

用途：TerminationCondition有状态，按每次agent响应后的delta消息检查并在run后重置；不是每个内部工具调用都自动检查。

选读范围：TerminationCondition overview and built-in conditions。限制：框架条件的触发粒度不是通用loop语义；不引用未读demo输出

[公开原文](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/termination.html)

<a id="durable-orchestration-037"></a>

### durable-orchestration-037 · Termination and infinite loops in group chat

作者／组织：Xiaoyun Zhang, Adam Fourney and AutoGen contributors。类型：公开问题讨论。版本／日期：2023-10-06; closed2024-08-26。读取日：2026-10-13。

用途：字符串TERMINATE可能被引用、遗漏或错误触发；结构化终止事件改善识别，但谁有权终止整个团队仍需控制器定义。

阅读范围：Full issue conversation。限制：旧版本历史案例，不能宣称当前产品仍有同样缺陷

[公开原文](https://github.com/microsoft/autogen/issues/133)

<a id="human-control-026"></a>

### human-control-026 · files.completeUploadExternal

作者／组织：Slack。类型：官方文档／规范。版本／日期：current API docs 2026-10-13。读取日：2026-10-13。

用途：上传字节后必须finalize，否则文件和metadata丢弃；不指定channel_id则文件private。

选读范围：Arguments/Usage info/Response/Errors。限制：只用文件交付路径，不扩展Slack一般开发；ok不证明目标用户已读

[公开原文](https://docs.slack.dev/reference/methods/files.completeUploadExternal/)

<a id="human-control-027"></a>

### human-control-027 · Share a file with a link

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：Microsoft Graph v1.0 current docs。读取日：2026-10-13。

用途：link scope区分anonymous/organization/users；organization链接对外部接收人不自动有效。

选读范围：HTTP 请求与响应契约、Scope types 及 retainInheritedPermissions 的说明。限制：只实读HTTP契约/Scope types；未实际创建分享，不推断某接收人权限

[公开原文](https://learn.microsoft.com/en-us/graph/api/driveitem-createlink?view=graph-rest-1.0)

<a id="human-control-028"></a>

### human-control-028 · Files and artifacts

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：Agents API beta current docs 2026-10-13。读取日：2026-10-13。

用途：托管环境在 turn 完成时发布指定输出目录中的不可变产物；按 turn ID 与路径选择版本，不能只取同路径的最新文件。

选读范围：托管／自托管文件发布、turn 与路径版本标识，以及环境和 session 生命周期的说明。限制：只覆盖此托管API；不证明收到artifact ID的最终用户已有访问权

[公开原文](https://developers.openai.com/api/docs/guides/agents-api/environments/files)

<a id="human-control-035"></a>

### human-control-035 · Life of a Task

作者／组织：A2A Protocol。类型：官方文档／规范。版本／日期：latest docs accessed 2026-10-13; unpinned version。读取日：2026-10-13。

用途：contextId关联会话背景而taskId标识工作单元；input-required/auth-required暂停但非终态。

选读范围：正文 Task lifecycle / task continuation / artifacts and multi-turn examples。限制：协议教程，不证明具体服务严格实现；artifact存在不说明受众能下载或验收通过

[公开原文](https://a2a-protocol.org/latest/topics/life-of-a-task/)

<a id="human-control-037"></a>

### human-control-037 · Download and export files

作者／组织：Google。类型：官方文档／规范。版本／日期：Drive API v3 guide accessed 2026-10-13。读取日：2026-10-13。

用途：blob download、Workspace export和浏览器链接是不同结果形态；先检查capabilities.canDownload。

选读范围：introductory download matrix / canDownload / Download blob file content in a browser / LRO sections。限制：仅用于交付边界，不扩展Drive通用教程；当前API调用者可下载不能推出另一收件人可下载；未以真实收件人身份测试

[公开原文](https://developers.google.com/workspace/drive/api/guides/manage-downloads)

<a id="loop-context-002"></a>

### loop-context-002 · Effective harnesses for long-running agents

作者／组织：Justin Young / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-11-26。读取日：2026-10-13。

用途：仅有压缩不足以连续推进：模型会一次做太多，留下半成品；也会见到已有进展就过早宣布完成。

阅读范围：The long-running agent problem; Feature list; Testing; Getting up to speed。限制：作者第一手工程经验；具体模型版本、产品实现和数据不应推广成普遍定律。

[公开原文](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

<a id="loop-context-004"></a>

### loop-context-004 · Building effective agents

作者／组织：Erik Schluntz and Barry Zhang / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2024-12-19, page updated after original。读取日：2026-10-13。

用途：固定路径的workflow和模型决定下一步的agent应分清；灵活性换取成本、延迟与累积错误。

阅读范围：When (and when not) to use agents; Evaluator-optimizer; Agents。限制：作者第一手工程经验；具体模型版本、产品实现和数据不应推广成普遍定律。

[公开原文](https://www.anthropic.com/engineering/building-effective-agents)

<a id="loop-context-005"></a>
<a id="protocol-036"></a>

### loop-context-005 · What I learned building an opinionated and minimal coding agent

作者／组织：Mario Zechner。类型：作者／团队实践或研究文章。版本／日期：2025-11-30。读取日：2026-10-13。 引用别名：protocol-036（本条合计 1 项，各版本复核不另计）。

用途：作者的最小循环以无工具调用为退出条件，不内置max steps；这是个人工具取舍，非可无人值守部署的安全保证。

阅读范围：Minimal agent scaffold; No built-in to-dos; No plan mode; No sub-agents。限制：作者个人工作流偏好，与无人值守系统要求不同；文章早于pi压缩实现。

已读版本／别名（同一来源）：
- loop-context-005：2025-11-30；范围：Minimal agent scaffold; No built-in to-dos; No plan mode; No sub-agents。[该版本原文](https://www.mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- protocol-036：2025-11-30；范围：pi-ai and pi-agent-core。[该版本原文](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://www.mariozechner.at/posts/2025-11-30-pi-coding-agent/)

<a id="loop-context-006"></a>

### loop-context-006 · How to Build an Agent

作者／组织：Thorsten Ball / Amp。类型：作者／团队实践或研究文章。版本／日期：unknown (Claude 3.7-era implementation)。读取日：2026-10-13。

用途：客户端显式维护conversation；模型输出包含tool_use时执行并把带ID的结果追加，再继续推理；无工具结果则重新等待用户输入。

选读范围：Run, runInference, executeTool code; beginning through first executable tool loop。限制：阅读核心循环与工具执行实现，未把教学示例当作完备的生产实现。

[公开原文](https://ampcode.com/how-to-build-an-agent)

<a id="loop-context-010"></a>

### loop-context-010 · Designing agentic loops

作者／组织：Simon Willison。类型：作者／团队实践或研究文章。版本／日期：2025-09-30。读取日：2026-10-13。

用途：试错搜索类任务需要明确目标、可迭代工具和可测成功条件；测试能把循环从主观自信转为外部反馈。

阅读范围：Picking the right tools for the loop; Issuing tightly scoped credentials; When to design an agentic loop。限制：个人经验；其 YOLO 使用偏好不构成默认安全建议。

[公开原文](https://simonwillison.net/2025/Sep/30/designing-agentic-loops/)

<a id="loop-context-011"></a>

### loop-context-011 · How coding agents work

作者／组织：Simon Willison。类型：作者／团队实践或研究文章。版本／日期：2026, references March 2026 prompt。读取日：2026-10-13。

用途：模型调用本身无会话记忆，harness重建输入；缓存重复前缀减少处理开销但不创造语义上的长期记忆。

阅读范围：Chat templated prompts; Token caching; Calling tools; Reasoning。限制：面向入门的简化模型，不以其示例regex解析描述现行所有协议。

[公开原文](https://simonwillison.net/guides/agentic-engineering-patterns/how-coding-agents-work/)

<a id="loop-context-020"></a>

### loop-context-020 · mini-swe-agent DefaultAgent

作者／组织：SWE-agent maintainers。类型：源码／仓库文档。版本／日期：main read 2026-10-13。读取日：2026-10-13。

用途：停止有step/cost/wall-clock和连续格式错误上限；query前检查而cost在响应后累计，因此阈值可被单次调用越过。

阅读范围：AgentConfig; run; query; serialize。限制：成本上限不是严格预付预算，源码注释明确exceeding；工具动作副作用不由序列化回滚。

[公开原文](https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/main/src/minisweagent/agents/default.py)

<a id="loop-context-021"></a>

### loop-context-021 · How do multi-step agents work?

作者／组织：Hugging Face smolagents。类型：官方文档／规范。版本／日期：current read 2026-10-13。读取日：2026-10-13。

用途：agent logs是有类型的SystemPromptStep/TaskStep/ActionStep/PlanningStep，向模型发送前转换消息；日志不是直接等于上下文。

阅读范围：Initialization; ReAct loop; planning。限制：概念页不证明规划提升，也不涵盖所有终止实现。

[公开原文](https://huggingface.co/docs/smolagents/conceptual_guides/react)

<a id="loop-context-036"></a>

### loop-context-036 · Large Language Models Cannot Self-Correct Reasoning Yet

作者／组织：Jie Huang et al.。类型：研究论文。版本／日期：ICLR 2024。读取日：2026-10-13。

用途：无外部反馈的自我修正在实验中常把正确答案改错；用oracle决定何时停止会夸大现实自纠能力。

选读范围：Abstract, Sections 3.1–3.3, 6–7。限制：历史GPT-3.5/GPT-4/Llama2实验，不能断言现代理论上不能自纠；不否定风格修改或外部反馈。

[公开原文](https://arxiv.org/html/2310.01798)

<a id="loop-context-037"></a>

### loop-context-037 · Reflexion: Language Agents with Verbal Reinforcement Learning

作者／组织：Noah Shinn et al.。类型：研究论文。版本／日期：NeurIPS 2023。读取日：2026-10-13。

用途：actor、evaluator、self-reflection分角色；将失败信号转为下一试验可用经验，并非无反馈重复要求模型想一想。

选读范围：Abstract; Sections 1,3,5。限制：未照搬算法图里疑似or停止条件排版；源码与任务具体终止逻辑需另查。

[公开原文](https://arxiv.org/html/2303.11366)

<a id="loop-context-038"></a>

### loop-context-038 · Self-Refine: Iterative Refinement with Self-Feedback

作者／组织：Aman Madaan et al.。类型：研究论文。版本／日期：NeurIPS 2023。读取日：2026-10-13。

用途：生成→具体可执行反馈→改写，停止可由次数或反馈分数决定；应有显式stop而不是永远优化。

选读范围：Abstract; Section 2; analysis on sampling and weak models; limitations。限制：与 [loop-context-036](topic-01.md#loop-context-036)的任务、prompt及oracle条件差异必须说明，不以单篇解决争论。

[公开原文](https://arxiv.org/html/2303.17651)

<a id="loop-context-039"></a>

### loop-context-039 · ReAct: Synergizing Reasoning and Acting in Language Models

作者／组织：Shunyu Yao et al.。类型：研究论文。版本／日期：ICLR 2023。读取日：2026-10-13。

用途：思考更新内部上下文但不产生环境观察；动作获得外部证据，二者是不同状态变更。

选读范围：Abstract; Sections 2,3.3。限制：PaLM时代受控任务，结果不能直接映射2026harness。

[公开原文](https://arxiv.org/html/2210.03629)

<a id="loop-context-054"></a>

### loop-context-054 · GRAPH_RECURSION_LIMIT

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current read 2026-10-13。读取日：2026-10-13。

用途：达到最大steps可能是逻辑环也可能是合法复杂流程；提高recursion_limit前先判定是否有终止条件。

阅读范围：Entire page。限制：框架中的recursion limit是执行步预算，不是Python调用栈深度，需结合具体graph语义。

[公开原文](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT)

<a id="loop-context-057"></a>

### loop-context-057 · Ralph Wiggum as a software engineer

作者／组织：Geoffrey Huntley。类型：作者／团队实践或研究文章。版本／日期：2025-07-14, evolving post。读取日：2026-10-13。

用途：循环每轮重新加载spec/plan并只做一项，靠文件与测试承接状态；fresh context是显式恢复策略。

选读范围：Intro; one item per loop; extend context; don't assume; backpressure; todo list; broken codebase。限制：强烈个人风格与无上限建议不照搬；只采机制与作者自述失败，不采商业替代结论。

[公开原文](https://ghuntley.com/ralph/)

<a id="loop-context-064"></a>

### loop-context-064 · Agentless: Demystifying LLM-based Software Engineering Agents

作者／组织：Chunqiu Steven Xia et al.。类型：研究论文。版本／日期：2024 / FSE 2025。读取日：2026-10-13。

用途：对结构明确的修bug任务，固定定位→修复→验证是应比较的低复杂基线，不必一开始让模型决定所有流程。

选读范围：Abstract; Sections3.1–3.3。限制：不证明开放长期任务无需agent；基准修bug与真实维护任务范围不同，生成测试也可能错误。

[公开原文](https://arxiv.org/html/2407.01489)

<a id="practitioner-lessons-001"></a>

### practitioner-lessons-001 · Minions: Stripe’s one-shot, end-to-end coding agents

作者／组织：Stripe Engineering。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：事实（团队自述）：单次任务在预热且与生产隔离的devbox执行；同一流程混合自主循环与确定性lint、git、CI步骤。

阅读范围：How do minions work?。限制：两轮CI是Stripe成本权衡，不是普遍上限；人审仍是合并条件。

[公开原文](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents)

<a id="practitioner-lessons-002"></a>

### practitioner-lessons-002 · Minions: Stripe’s one-shot, end-to-end coding agents—Part 2

作者／组织：Stripe Engineering。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：事实：blueprint状态机把Implement task/Fix CI failures等agent节点与Run linters/Push changes等确定性节点组合；目录规则按范围注入而非全局堆叠。

阅读范围：Blueprints; Context gathering; … and iterate。限制：隔离前提缺失时不可照搬跳过审批；能力目录大小不等于每轮上下文大小。

[公开原文](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)

<a id="practitioner-lessons-006"></a>

### practitioner-lessons-006 · Spotify’s Journey with Our Background Coding Agent (Honk, Part 1)

作者／组织：Max Charas; Marc Bruggmann / Spotify。类型：作者／团队实践或研究文章。版本／日期：2025-11-06。读取日：2026-10-13。

用途：事实：只将Fleet Management中的代码变换替换成agent，仓库选取、PR、人审、合并继续由原有系统处理。

阅读范围：Enter AI coding agents; New challenges。限制：合并PR与节省时间是团队自述，不能当agent正确率；文中主动承认安全、成本与可预测性未解决。

[公开原文](https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1)

<a id="practitioner-lessons-008"></a>

### practitioner-lessons-008 · Background Coding Agents: Predictable Results Through Strong Feedback Loops (Honk, Part 3)

作者／组织：Max Charas; Marc Bruggmann / Spotify。类型：作者／团队实践或研究文章。版本／日期：2025-12-09。读取日：2026-10-13。

用途：事实：verify按仓库特征自动选verifier，解析错误只返回相关片段；agent主动调用与stop hook强制调用并用，失败不创建PR。

阅读范围：How things fail; Verification loops; Using LLMs。限制：veto率不等于正确拦截率；judge缺乏校准，CI通过也可能功能错误。

[公开原文](https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3)

<a id="practitioner-lessons-021"></a>

### practitioner-lessons-021 · I built the agent runtime three times

作者／组织：Chris Chabot。类型：作者／团队实践或研究文章。版本／日期：2026-06。读取日：2026-10-13。

用途：事实：自动续写在完成后多跑两轮；五轮cap只止损，不定义完成，后来增加需求审计和集成后验证。

阅读范围：The first agent; One transcript was doing six jobs。限制：个人复盘无量化对照；事件记录仍需定义提交原子性，不能自动解决副作用。

[公开原文](https://chabot.dev/blog/three-attempts-at-an-agent/)

<a id="practitioner-lessons-024"></a>

### practitioner-lessons-024 · AI Agent Debugging: Four Lessons from Shipping Alyx to Production

作者／组织：Laurie Voss / Arize。类型：作者／团队实践或研究文章。版本／日期：2026-02-25。读取日：2026-10-13。

用途：事实：Alyx曾27次调用只重整TODO；计划独立保存，finish在未完成时拒绝，blocked可结束等待用户。

选读范围：Lessons 1–4（PlanMessage中段代码未完整读取）。限制：阅读 Lessons 1–4，未完整阅读 PlanMessage 中段门控代码；“只有 LLM 能语义评测”是作者过强观点，不采用；生产黄金样本仍需独立验证。

[公开原文](https://arize.com/blog/ai-agent-debugging-four-lessons-from-shipping-alyx-to-production/)

<a id="practitioner-lessons-049"></a>

### practitioner-lessons-049 · What I Learned Building My Own AI Harness | joacod

作者／组织：Joaquin Diaz。类型：作者／团队实践或研究文章。版本／日期：2026-05-22。读取日：2026-10-13。

用途：事实：作者把一次有界run定义为模型调用、动作、策略、审批、事件与持久化的中心实体，并分离UI/core/infra/contracts。

阅读范围：Run-first design; architecture; unfinished work。限制：全文；个人学习项目，真实MCP transport等仍未完成，不作为生产成熟度证据。

[公开原文](https://joacod.com/blog/what-i-learned-building-nano-harness/)

<a id="practitioner-lessons-052"></a>

### practitioner-lessons-052 · 12 Factor Agents | HumanLayer Blog

作者／组织：Dex Horthy / HumanLayer。类型：作者／团队实践或研究文章。版本／日期：2025-04-03。读取日：2026-10-13。

用途：作者经验：工具提议到实际执行之间保留自己控制的流程，可插审批、持久化和外部回调恢复；人机输入应是结构化事件。

选读范围：Factors 5–9; tool calling; compact errors。限制：读前14000字符及Factors5–9、12标题附近；未完整读全12因子；GitHub镜像不另计。

[公开原文](https://www.humanlayer.dev/blog/12-factor-agents)

<a id="practitioner-lessons-056"></a>

### practitioner-lessons-056 · Teaching an agent to auto-fix bugs - Linear

作者／组织：Igor Sechyn / Linear。类型：作者／团队实践或研究文章。版本／日期：2026-06-12。读取日：2026-10-13。

用途：作者复盘：直接要求agent修任意triage bug效果差；先在弃用feature flag等窄任务建立可靠路径，再拓展。

阅读范围：Initial attempt; narrower scope; investigation gate。限制：全文；不同任务成功率差异不能当模型能力统一指标，结果是团队观察。

[公开原文](https://linear.app/now/linear-agent-bug-fix)

<a id="practitioner-lessons-058"></a>

### practitioner-lessons-058 · Introducing Roast: Structured AI workflows made easy (2025) - Shopify

作者／组织：Obie Fernandez / Shopify。类型：作者／团队实践或研究文章。版本／日期：2025-06-18。读取日：2026-10-13。

用途：事实：Roast将确定性步骤和agent步骤放同一工作流；Boba迁移先用sed/Sorbet自动修复，再让agent处理剩余问题和测试。

阅读范围：Boba workflow; session replay; deterministic steps。限制：正文完整，提取器未显示部分代码块；重放不是外部副作用回滚；共享上下文也可能膨胀。

[公开原文](https://shopify.engineering/introducing-roast)

<a id="practitioner-lessons-061"></a>

### practitioner-lessons-061 · Delegating Engineering Work To Cloud-Based Agents - DoorDash

作者／组织：Santosh Banda, Jeffrey Hwang, Siddarth Kodwani / DoorDash。类型：作者／团队实践或研究文章。版本／日期：2026-08-11。读取日：2026-10-13。

用途：事实：Flux playbook声明输入、上下文、工具权限、验证和输出，确定性步骤与agent步骤混合运行在隔离sandbox。

阅读范围：Playbooks; sandbox; gateway; shared threads。限制：全文；5秒sandbox setup是p95目标，不应当成所有运行的已测承诺。

[公开原文](https://careersatdoordash.com/blog/delegating-engineering-work-to-cloud-based-agents/)

<a id="practitioner-lessons-072"></a>

### practitioner-lessons-072 · Why We Removed LangGraph From Our AI Platform - DEV Community

作者／组织：Nicola Richli / yeos.ai。类型：作者／团队实践或研究文章。版本／日期：2026-07-27。读取日：2026-10-13。

用途：作者复盘：其企业平台实际请求大多顺序，graph状态、reducers和checkpoint抽象增加调试负担；改成显式planner/context/tool runner/validator组件与逐阶段timeline。

阅读范围：Problems; composable components; graph fit。限制：全文；没有源码或性能数值，改善仅作者生产经验；线性组件仍可能内部隐藏复杂loop，不能自动获得恢复语义。

[公开原文](https://dev.to/nicolaric/why-we-removed-langgraph-from-our-ai-platform-i9o)

<a id="runtime-boundaries-026"></a>

### runtime-boundaries-026 · S3 upload integrity

作者／组织：AWS。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：multipart ETag不是整个文件MD5；full-object与composite checksum不同。服务端可校验并BadDigest拒绝，但某些算法若未在CreateMultipartUpload声明，Complete头可被接受而不验证，不能只看有checksum字段。

选读范围：Full object and composite; multipart full checksums。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html)

<a id="runtime-boundaries-053"></a>

### runtime-boundaries-053 · CompleteMultipartUpload

作者／组织：Amazon Web Services。类型：官方文档／规范。版本／日期：current API 2026-10-13。读取日：2026-10-13。

用途：CompleteMultipartUpload 先发200再处理并发空白保活，200 body仍可能是错误；agent上传工具必须解析最终结果，不能HTTP header一到就记交付完成。所有parts已上传也不是对象已commit；只能按完整part列表完成。

选读范围：API introductory contract and special errors。限制：AWS SDK处理内嵌错误，手写HTTP客户端不得假设同样行为。

[公开原文](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html)

<a id="runtime-boundaries-054"></a>

### runtime-boundaries-054 · Data validation and change detection with checksums

作者／组织：Google Cloud。类型：官方文档／规范。版本／日期：updated 2026-10-13。读取日：2026-10-13。

用途：gcloud 客户端校验在对象finalize之后，错误对象可能可见1–3秒，客户端此时崩溃会留错对象；上传请求带checksum做服务端校验更早拒绝。

选读范围：Google Cloud CLI copies and rewrites; Change detection for rsync; Performing data integrity checks。限制：区分客户端/传输/版本，不能把一种SDK最新默认推广所有旧版本。

[公开原文](https://docs.cloud.google.com/storage/docs/data-validation)

<a id="runtime-boundaries-061"></a>

### runtime-boundaries-061 · Store and share data with workflow artifacts

作者／组织：GitHub。类型：官方文档／规范。版本／日期：upload-artifact v4/download-artifact v5 tutorial。读取日：2026-10-13。

用途：v4产物不可变，修改后应新对象；retention受仓/组织上限约束，不是永久存储。下载自动比对SHA256，但不符只是UI/log warning，harness若需硬保证必须升级成失败。

选读范围：Passing data between jobs; Validating artifacts; retention。限制：从旧 how-tos URL 重定向到本 canonical；不把warning当验证成功或自动失败。

[公开原文](https://docs.github.com/en/actions/tutorials/store-and-share-data)

[返回分类目录](README.md#topics)
