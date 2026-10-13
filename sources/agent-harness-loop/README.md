# Agent harness 与 loop：分类来源索引

截至 2026-10-13，本索引列出 556 个实质阅读后保守去重的来源，另列 19 项不增加总数的补充证据。正文是一篇单页指南；这里用于核验原始依据与版本边界。

[返回单页正文](../../docs/agent-harness-loop-guide.md) · [机器可读来源元数据](sources.json)。快速入口：[基础循环](#loop-context-006) · [工具契约](#tools-security-001) · [超时与重试](#network-errors-001) · [Agent 评测](#traces-eval-004)。

## 使用与口径

同篇文章的镜像、同论文的 HTML／PDF、同一规范章节的新旧版，以及同一仓库文件的 main／tag／commit 合并计数。相近标题但内容独立的文章不自动合并。每条保留稳定编号、引用别名和实际阅读的版本；别名不是额外来源。

“阅读范围”指实际支持该条用途的正文、章节、讨论或代码段落，并不表示每篇全文逐字通读。两轮独立审校实质复读了 143 个去重来源单位（含不计入主总数的辅助材料）；这是按风险选样的复核，不代表全部来源经过第二次通读。搜索摘要、抓取成功、目录页和未读正文的链接本身不构成依据。

官方规范说明约定，源码说明所读版本的静态实现，issue／PR 可能只是报告或未发布提案，实践文章与论文受其任务和实验条件限制。它们不能互相替代。动态文档以读取日为界；main 分支、已合并 PR 与用户已安装版本是三种不同事实。

下列要点是研究用途的简短转述，保留必要限制；原文内容和完整抓取文本不随索引发布。来源链接均指向公开原文。

<a id="topics"></a>

## 按正文主题查找

- [1. 先看清一次动作：harness、loop 与完成条件](#topic-01)（42 个来源）
- [2. Protocol 选择：模型接口与工具接入各管什么](#topic-02)（43 个来源）
- [3. 流式输出：先组装结果，再决定执行](#topic-03)（21 个来源）
- [4. 工具契约：让下一步有据可依](#topic-04)（31 个来源）
- [5. 权限与安全：模型提议不能自己变成授权](#topic-05)（59 个来源）
- [6. 执行环境：命令在哪儿跑，资源归谁收尾](#topic-06)（55 个来源）
- [7. 网络：请求究竟卡在哪一层](#topic-07)（29 个来源）
- [8. 错误处理与恢复：什么时候能重试，什么时候先查结果](#topic-08)（37 个来源）
- [9. 上下文与记忆：下次模型真正看到什么](#topic-09)（53 个来源）
- [10. 持久化与恢复：进程回来后，任务怎样继续](#topic-10)（62 个来源）
- [11. 插话、暂停与取消：让旧任务正确让路](#topic-11)（28 个来源）
- [12. 并发、调度与预算：多跑几个为何更慢](#topic-12)（15 个来源）
- [13. 多 agent：按独立性拆任务，不按人数求能力](#topic-13)（12 个来源）
- [14. 日志与轨迹：留得下来，也查得回去](#topic-14)（30 个来源）
- [15. 回放与评测：证明修复，而不是制造绿色分数](#topic-15)（39 个来源）
- [补充证据，不增加来源总数](#supplementary)

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

选读范围：Abstract; Section 2; analysis on sampling and weak models; limitations。限制：与 [loop-context-036](#loop-context-036)的任务、prompt及oracle条件差异必须说明，不以单篇解决争论。

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

[返回分类目录](#topics)

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

选读范围：角色检查与 tool ID 渲染分支。限制：[protocol-050](#protocol-050)同文件版本复核；未安装Jinja执行模板。

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

选读范围：工具调用、结果与 reasoning 的历史转换分支。限制：[protocol-054](#protocol-054)同文件发行版复核；不把当前main新增保护反投射到旧tag。

已读版本／别名（同一来源）：
- protocol-054：main accessed 2026-10-13; blob SHA b7585d55c45e635ede03d29223c15de81d6b0448 (not a commit)；范围：lines 710–766, 927–990, 1254–1362, 1807–1833。[该版本原文](https://github.com/vercel/ai/blob/main/packages/openai/src/responses/convert-to-openai-responses-input.ts)
- protocol-audit-024：ai@7.0.70; blob dc6307e8fab0c0175048a41cd959b725906748a2；范围：工具调用、结果与 reasoning 的历史转换分支；补充复核，不新增计数。[该版本原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/openai/src/responses/convert-to-openai-responses-input.ts)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/openai/src/responses/convert-to-openai-responses-input.ts)

<a id="protocol-055"></a>

### protocol-055 · Invalid signature in thinking block when replaying history

作者／组织：anthropics/anthropic-sdk-python reporter and maintainer。类型：公开问题讨论。版本／日期：2026-05-23; reported Claude 4.x gateway history。读取日：2026-10-13。

用途：维护者明确签名不会因时间自然过期，排查应看文本/签名被改写、块重排或合并以及模型切换，而非默认TTL过期。

阅读范围：Issue body; maintainer dtmeadows-ant comment 5192744619。限制：报告仍开放；不同模型的当前兼容/丢弃规则见[protocol-063](#protocol-063)，旧建议不覆盖所有新模型。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/issues/1598)

<a id="protocol-063"></a>
<a id="protocol-audit-004"></a>

### protocol-063 · Thinking

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current docs accessed 2026-10-13; binding beta 2026-08-01。读取日：2026-10-13。 引用别名：protocol-audit-004（本条合计 1 项，各版本复核不另计）。

用途：工具使用回合内必须保存thinking，跨回合推荐保留，而工具使用之外可以省略过去thinking；不能概括为所有块永远原样回传。

选读范围：Thinking with tool use; preserving blocks; interleaved/preserved thinking; model preservation; encryption; redaction。限制：动态规则受模型与账户生效条件约束；保留、绑定及默认丢弃行为不可跨版本推断。专门规则另见 [protocol-audit-001](#protocol-audit-001)；未实测全部 API 组合。

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

[返回分类目录](#topics)

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

作者／组织：markstuart-oai。类型：公开变更／提案。版本／日期：2a98f6a1dee448c6410531c89c2de0af4383c6a7。读取日：2026-10-13。 引用别名：protocol-audit-013（本条合计 1 项，各版本复核不另计）。

用途：稳定与beta模型均删除done事件name字段；真实修复调整类型契约，不制造API未给的字段。

选读范围：事件类型 diff：删除 function_call_arguments.done 中错误的 name 字段。限制：仅阅读与协议bug相关diff；release其他改动不作来源。

已读版本／别名（同一来源）：
- protocol-033：2a98f6a1dee448c6410531c89c2de0af4383c6a7；范围：事件类型 diff：删除 function_call_arguments.done 中错误的 name 字段。[该版本原文](https://github.com/openai/openai-python/pull/3801)
- protocol-audit-013：merged commit 2a98f6a1dee448c6410531c89c2de0af4383c6a7；范围：PR 正文与实际 diff；补充复核，不新增计数。[该版本原文](https://github.com/openai/openai-python/pull/3801)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

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

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob f9dec645b67383da62a688ce1c73eebf7607c553。读取日：2026-10-13。 引用别名：protocol-audit-012（本条合计 1 项，各版本复核不另计）。

用途：Chat辅助done事件从已累积tool_call.function.name构造；是SDK丰富后的事件，不是原始SSE格式。

选读范围：FunctionToolCallArgumentsDoneEvent 的构造分支。限制：[protocol-046](#protocol-046)同文件发行版复核。

已读版本／别名（同一来源）：
- protocol-046：main accessed 2026-10-13; blob SHA 3476314f7f47a6924cad78d3176391e769233280 (not a commit)；范围：src/openai/lib/streaming/chat/_completions.py lines 343–497。[该版本原文](https://github.com/openai/openai-python/blob/main/src/openai/lib/streaming/chat/_completions.py)
- protocol-audit-012：v3.9.0; blob f9dec645b67383da62a688ce1c73eebf7607c553；范围：FunctionToolCallArgumentsDoneEvent 的构造分支；补充复核，不新增计数。[该版本原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/streaming/chat/_completions.py)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/streaming/chat/_completions.py)

<a id="protocol-048"></a>
<a id="runtime-boundaries-005"></a>

### protocol-048 · Anthropic Python v1.13.0 accumulated message helper

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.13.0 / b4b7916deaf4e5570cd627b1ae7ee4394a4de39f。读取日：2026-10-13。 引用别名：runtime-boundaries-005（本条合计 1 项，各版本复核不另计）。

用途：get_final_message消费到底后只assert已存在snapshot；snapshot在message_start即建立，未显式核查message_stop。因此应用不能把helper名中的final当作流完整性契约。

选读范围：get_final_message; accumulate_event message_start/message_delta。限制：限定 v1.13.0 的累计消息 helper；未独立运行完整 SDK 集成测试。

已读版本／别名（同一来源）：
- protocol-048：main accessed 2026-10-13; blob SHA d036a04d1f96e0063fa9b7c7046b60750c874f11 (not a commit)；范围：src/anthropic/lib/streaming/_messages.py lines 341–537。[该版本原文](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/lib/streaming/_messages.py)
- runtime-boundaries-005：v1.13.0 / b4b7916deaf4e5570cd627b1ae7ee4394a4de39f；范围：get_final_message; accumulate_event message_start/message_delta；补充复核，不新增计数。[该版本原文](https://github.com/anthropics/anthropic-sdk-python/blob/b4b7916deaf4e5570cd627b1ae7ee4394a4de39f/src/anthropic/lib/streaming/_messages.py)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

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

阅读范围：Issue reproduction with two callable functions and comments。限制：开放issue且无最终根因；不能把[protocol-064](#protocol-064)另一个用户的分组错误直接认定为本例原因。

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

阅读范围：Issue reproduction; mock provider cases; maintainer/bot diagnosis。限制：为历史SDK bug，后续PR [protocol-061](#protocol-061)已合并；不要不分版本宣称当前SDK仍执行。

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

作者／组织：Vercel AI SDK。类型：公开变更／提案。版本／日期：merged a8285273ef8b4b2c36cf3cb692706da7f40077d4。读取日：2026-10-13。 引用别名：protocol-audit-014（本条合计 1 项，各版本复核不另计）。

用途：补丁集中引入isToolExecutionAllowedFinishReason，只允许stop或tool-calls驱动自动工具执行，并用于流式和非流式路径。

阅读范围：PR 19066 diff: shared helper, generateText, executeToolsFromStream and regression tests。限制：这是AI SDK的标准化终态执行策略，不是所有厂商原生枚举定义；安全授权仍是另一层。

已读版本／别名（同一来源）：
- protocol-061：merged a8285273ef8b4b2c36cf3cb692706da7f40077d4；范围：PR 19066 diff: shared helper, generateText, executeToolsFromStream and regression tests。[该版本原文](https://github.com/vercel/ai/pull/19066)
- protocol-audit-014：merged; published ai@7.0.70；范围：PR 正文、实际 diff 与发行说明评论；补充复核，不新增计数。[该版本原文](https://github.com/vercel/ai/pull/19066)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/vercel/ai/pull/19066)

<a id="protocol-audit-015"></a>

### protocol-audit-015 · Published AI SDK streaming tool dispatch

作者／组织：Vercel AI SDK maintainers。类型：源码／仓库文档。版本／日期：ai@7.0.70; blob a02b49e8aeaade10d22fc23c625982e7addd6e7e。读取日：2026-10-13。

用途：批准后的client calls先入队，在model-call-end按终态允许后执行；providerExecuted调用不进入该execute分支。

选读范围：流式工具分派与 finishReason 门控分支。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。

[公开原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.ts)

[返回分类目录](#topics)

<a id="topic-04"></a>

## 4. 工具契约：让下一步有据可依

<a id="human-control-004"></a>

### human-control-004 · Chatbot Tool Usage

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 current docs。读取日：2026-10-13。

用途：addToolApprovalResponse只更改审批响应，需sendMessage或sendAutomaticallyWhen继续；按钮已批准不等于下一轮已执行。

选读范围：审批响应后的继续执行，以及客户端消息与工具错误显示的相关说明。限制：本页为使用契约；签名细节另见Tool Approvals；未执行示例

[公开原文](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-tool-usage)

<a id="human-control-005"></a>

### human-control-005 · Tool Calling

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 docs；needsApproval已deprecated于普通core工具。读取日：2026-10-13。

用途：手动审批使当前generateText/streamText结束并返回approval request，不是冻结进程；第二次调用才执行或把execution-denied回填模型。

选读范围：markdown Tool Execution Approval/How It Works/Handling Approval Requests。限制：仅实读Tool Execution Approval及错误处理章节；支付示例不构成通用授权设计

[公开原文](https://ai-sdk.dev/docs/ai-sdk-core/tools-and-tool-calling)

<a id="loop-context-042"></a>

### loop-context-042 · Building an Agent That Leverages Throwaway Code

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2025-10-17。读取日：2026-10-13。

用途：文件系统让代码工具与模型分析工具共享同一产物，避免某工具生成结果只能交给特定下游的死路。

选读范围：Pyodide; File Systems Are King; Durable Execution; What Other Than Code; start of example。限制：示范没有给出完整的安全与持久性保证；按 step 缓存不等于任意外部副作用恰好一次。

[公开原文](https://lucumr.pocoo.org/2025/10/17/code/)

<a id="loop-context-044"></a>

### loop-context-044 · Context-Efficient Backpressure for Coding Agents

作者／组织：Dex / HumanLayer。类型：作者／团队实践或研究文章。版本／日期：2025-12-09。读取日：2026-10-13。

用途：测试先完整落日志，成功只报简短状态，失败给具体输出；比直接head截断后重跑更能保留可用反馈。

阅读范围：Full body。限制：文章75k smart zone非普遍模型定律；fail-fast仅适合逐个修复而非全面故障清点。

[公开原文](https://www.humanlayer.dev/blog/context-efficient-backpressure)

<a id="loop-context-050"></a>

### loop-context-050 · The think tool: Enabling Claude to stop and think

作者／组织：Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-03-20, Dec15 update。读取日：2026-10-13。

用途：think工具只是记录思考不获取新信息；当时在复杂顺序工具/政策约束任务有收益，简单独立调用无收益。

阅读范围：Whole relevant body incl performance, When to use/not use, update。限制：正文数值描述与表存在差异，避免精确引用改善百分点；旧模型3.7评测。

[公开原文](https://www.anthropic.com/engineering/claude-think-tool)

<a id="practitioner-lessons-018"></a>

### practitioner-lessons-018 · We removed 80% of our agent’s tools

作者／组织：Andrew Qu / Vercel。类型：作者／团队实践或研究文章。版本／日期：2025-12-22。读取日：2026-10-13。

用途：事实：d0把17类业务工具删成ExecuteCommand+ExecuteSQL，直接让模型读取良好维护的Cube语义层文件。

阅读范围：v2; benchmark table; Lessons learned。限制：并非真的只剩一个工具，示例仍有SQL；五题不能证明泛化成功率或安全性。

[公开原文](https://vercel.com/blog/we-removed-80-percent-of-our-agents-tools)

<a id="practitioner-lessons-020"></a>

### practitioner-lessons-020 · I Built an Agent Harness to See What’s Inside

作者／组织：Konstantinas Mamonas。类型：作者／团队实践或研究文章。版本／日期：2026-09-01。读取日：2026-10-13。

用途：事实：Buntline在工具输出入历史前截断并spill文件，保留head/tail及分页读取；重复检测同时看调用与结果以免误杀有进展的轮询。

阅读范围：Nothing Gets to Rewrite History; Tool Output; Absorbing Failures; Buntline Building。限制：小模型prompt位置实验仅四提示；自动修复被截断JSON和映射工具名不能无条件用于有副作用调用。

[公开原文](https://mamonas.dev/posts/agent-harness-to-see-whats-inside/)

<a id="practitioner-lessons-037"></a>

### practitioner-lessons-037 · Operator: A look under the hood

作者／组织：Jack Ryan / Intercom。类型：作者／团队实践或研究文章。版本／日期：2026-05-15。读取日：2026-10-13。

用途：事实：生产多workspace差异使薄API wrapper不够，purpose-built reporting工具编码有效指标和字段稀疏度；技能编排完整诊断任务。

选读范围：The tooling layer; Attribute awareness; The action layer。限制：读前10500字符至尾部总结；工具多不等于同轮全部注入；文章偏产品说明，未提供安全实现或准确率。

[公开原文](https://www.intercom.com/blog/operator-a-look-under-the-hood)

<a id="practitioner-lessons-040"></a>

### practitioner-lessons-040 · What Happens When You Give your Agent Maximum Freedom

作者／组织：Gregor Zunic / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2026-03-13。读取日：2026-10-13。

用途：作者观察：模型按熟悉的方式假定Python状态持久、写串行请求或绕开专用工具；重复prompt要求不足以改变这些行为。

阅读范围：Observed agent behavior; AST checks; missing capabilities。限制：全文；AST启发式不等于完整安全检测；“训练总会胜出”为作者概括，不能推广为定律；并行仅适用于无依赖操作。

[公开原文](https://browser-use.com/posts/agent-freedom)

<a id="practitioner-lessons-043"></a>

### practitioner-lessons-043 · Extending the Cline loop with plugins and hooks | Cline Blog

作者／组织：Etisha Garg / Cline。类型：作者／团队实践或研究文章。版本／日期：2026-06-15。读取日：2026-10-13。

用途：事实：生命周期hook由runtime确定触发，区别于模型自行决定是否调用MCP工具；beforeTool可拦截，afterRun还会处理失败和取消。

选读范围：Hooks versus MCP; beforeTool; afterRun。限制：读前12000字符到onEvent列表；示例正则拦命令不构成完整shell安全策略；文章beforeRun/beforeTool有表述混淆。

[公开原文](https://cline.bot/blog/extend-cline-with-plugins-and-hooks)

<a id="practitioner-lessons-048"></a>

### practitioner-lessons-048 · Harness engineering in practice - Afraz Ahmed

作者／组织：Afraz Ahmed。类型：作者／团队实践或研究文章。版本／日期：2026-07-15。读取日：2026-10-13。

用途：事实：托管支持copilot用确定性首轮快照和profiler收集器替代多次探索；CommandResult区分被拒、下线和空成功。

阅读范围：Collectors; CommandResult; evidence gate; weekly review。限制：完整11节分两次阅读；二进制allowlist不是完整沙箱证明，建议后附警告也不是硬执行阻断；无受控效果数字。

[公开原文](https://afraz.dev/blog/harness-engineering-in-practice/)

<a id="practitioner-lessons-050"></a>

### practitioner-lessons-050 · Building a harness that makes a small LLM reliable

作者／组织：Nikhil Verma。类型：作者／团队实践或研究文章。版本／日期：2026-05-20。读取日：2026-10-13。

用途：事实：Haiku生成格式正确但不存在的UUID；作者用session持久化的双向typed reference registry，重写工具schema与结果，执行前拒绝未知引用并回传可修复错误。

阅读范围：Reference registry; tool rewriting; completion guard。限制：全文分段读；示例将JSON Schema pattern泛称annotation的解释不采用；200步与强制补执行不是通用安全默认，尤其涉及写操作。

[公开原文](https://nikhil-verma.com/blog/reliable-small-llm-agent-harness/)

<a id="practitioner-lessons-068"></a>

### practitioner-lessons-068 · Why We Deleted (Most of) Our MCP Tools

作者／组织：Max Kless / Nx。类型：作者／团队实践或研究文章。版本／日期：2026-02-17。读取日：2026-10-13。

用途：事实：能用CLI自行筛选数据后，团队删去多数单纯转述project graph/schema的MCP工具，改skills指导何时生成、如何验证；保留认证API和运行中进程连接。

阅读范围：Numbers; where MCP still shines。限制：全文，图中具体数字未读取；团队基准判分包含LLM judge；动态MCP加载已缩小工具与skills开销差异。

[公开原文](https://nx.dev/blog/why-we-deleted-most-of-our-mcp-tools)

<a id="protocol-005"></a>

### protocol-005 · Structured model outputs

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：JSON mode 只保证可解析 JSON，Structured Outputs 才约束支持的 schema 子集，仍不保证语义正确。

选读范围：Refusals; Avoid JSON schema divergence; Supported schemas; JSON mode。限制：动态文档，具体字段/默认值须按模型快照验证；未把厂商性能宣传作为独立测量结论。

[公开原文](https://developers.openai.com/api/docs/guides/structured-outputs)

<a id="protocol-008"></a>

### protocol-008 · Define tools

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：tool_choice 参数可被API接受但不保证跨模型/思考模式可用；强制tool可能跳过thinking，而auto允许自然前言。

选读范围：Specifying client tools; Requirements and limitations; Forcing tool use。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

[公开原文](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)

<a id="protocol-012"></a>
<a id="protocol-audit-018"></a>

### protocol-012 · Structured outputs

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。 引用别名：protocol-audit-018（本条合计 1 项，各版本复核不另计）。

用途：SDK可将不支持的minimum/maxLength等约束移入description，服务端schema与原始业务schema并不相同；最终本地验证仍必要。

选读范围：How SDK transformation works; JSON Schema limitations; Invalid outputs; Schema complexity limits。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

已读版本／别名（同一来源）：
- protocol-012：live documentation as accessed 2026-10-13；范围：How SDK transformation works; JSON Schema limitations; Invalid outputs; Schema complexity limits。[该版本原文](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- protocol-audit-018：live 2026-10-13；范围：Schema 限制、属性名大小写与解析条件；补充复核，不新增计数。[该版本原文](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)

<a id="protocol-019"></a>

### protocol-019 · Structured outputs (generateContent)

作者／组织：Google。类型：官方文档／规范。版本／日期：2026-10-09。读取日：2026-10-13。

用途：支持JSON Schema子集且未支持关键字可被忽略；应用必须做语义与业务验证。

选读范围：JSON schema support; Best practices; Limitations。限制：不同API与模型版本限制不可外推。

[公开原文](https://ai.google.dev/gemini-api/docs/generate-content/structured-output)

<a id="protocol-029"></a>

### protocol-029 · Structured outputs `response_format` requires `strict` function calling JSON Schema?

作者／组织：moonbox3; repository maintainers/comments。类型：公开问题讨论。版本／日期：2024-09-20T19:48:26Z; updated 2026-09-09T22:13:26Z。读取日：2026-10-13。

用途：用户把SDK .parse()发请求前的ValueError误称服务端400；维护者指出严格tool要求属于auto-parser而非API要求。

阅读范围：RobertCraigie and marcuswood-oai clarifications。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/openai/openai-python/issues/1733)

<a id="protocol-030"></a>

### protocol-030 · Improper handling of pydantic `extra="allow"`

作者／组织：lucaswiman; repository maintainers/comments。类型：公开问题讨论。版本／日期：2025-11-08T00:05:22Z; updated 2025-11-09T09:13:56Z。读取日：2026-10-13。

用途：Pydantic extra='allow'生成additionalProperties:true；openai2.7.1严格化函数仅在key缺省时加false，导致服务端400。

阅读范围：minimal reproduction; source commit 6574bcd; proposed fix。限制：历史版本复现；issue不单独证明所有当前版本仍有bug。评论推测未当技术事实。

[公开原文](https://github.com/openai/openai-python/issues/2740)

<a id="protocol-062"></a>

### protocol-062 · JSON Schema Validation: A Vocabulary for Structural Validation of JSON

作者／组织：Austin Wright; Henry Andrews; Ben Hutton。类型：官方文档／规范。版本／日期：draft 2020-12 / draft-bhutton-json-schema-validation-01。读取日：2026-10-13。

用途：required规定字段存在，null是类型/值问题，必填且可null不等于字段可省略；enum按JSON值相等判断。

选读范围：JSON Schema Validation：Sections 4.2、6.1.1–6.1.3、6.5.3、7.2.1–7.2.2、9.2、10。限制：只读所列相关章节；不把格式和默认注解当服务端实际保证。

[公开原文](https://json-schema.org/draft/2020-12/json-schema-validation)

<a id="protocol-audit-019"></a>

### protocol-audit-019 · Anthropic published schema transformation

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0; blob ce0c83ac96430010d315f4cd576cae9a08c4ed39。读取日：2026-10-13。

用途：未支持关键字移到description；oneOf还被降成anyOf，有重叠分支时语义会变化。

选读范围：已发布版本的 schema transformation 模块。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/lib/_parse/_transform.py)

<a id="runtime-boundaries-040"></a>

### runtime-boundaries-040 · Extract apps cache logic into ConnectorRuntimeManager

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：OPEN unmerged; head 4f6fb1bbf118525ec4092df7b679416715961837。读取日：2026-10-13。

用途：提案把工具目录缓存按账号、用户、workspace、Codex home 区分，发布不可变 tools+refresh 快照，schema 不符丢弃，读取上限在 metadata 与 read 后双重检查防文件增长。

选读范围：PR body; connectors/src/connector_runtime/mod.rs and persistence.rs; legacy-cache cold-load test。限制：未合并提案，不能写当前产品保证；已读具体写入实现。

[公开原文](https://github.com/openai/codex/pull/31471)

<a id="tools-security-001"></a>

### tools-security-001 · Writing effective tools for agents — with agents

作者／组织：Ken Aizawa / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-09-11。读取日：2026-10-13。

用途：工具不是现有 API 的逐一包装；应根据完整任务的观察轨迹减少重叠能力，并让工具在服务端完成检索、聚合等确定性工作。

阅读范围：article body。限制：作者内部 Claude 经验；命名、格式效果需在目标模型任务上验证。

[公开原文](https://www.anthropic.com/engineering/writing-tools-for-agents)

<a id="tools-security-002"></a>

### tools-security-002 · Code execution with MCP: Building more efficient agents

作者／组织：Adam Jones and Conor Kelly / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-11-04。读取日：2026-10-13。

用途：工具发现和中间结果处理可放进代码执行层，仅让模型读取任务需要的 schema 和筛选后的结果。

阅读范围：article body。限制：示例的 token 节省不是通用基准；权限检查应保留在哪些边界，仍须结合实际执行路径验证。

[公开原文](https://www.anthropic.com/engineering/code-execution-with-mcp)

<a id="tools-security-013"></a>
<a id="tools-security-065"></a>

### tools-security-013 · Tools — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：tools-security-065（本条合计 1 项，各版本复核不另计）。

用途：同名工具跨server可冲突，serverInfo.name也不保证唯一，不能单靠显示名称作权限键。

阅读范围：Capabilities; Tool Names; x-mcp-header; Stateful Tools; Error Handling。限制：同一工具规范章节新版本复核，合并013不重复计数。

已读版本／别名（同一来源）：
- tools-security-013：2025-11-25；范围：article body。[该版本原文](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- tools-security-065：2026-07-28；范围：Capabilities; Tool Names; x-mcp-header; Stateful Tools; Error Handling；补充复核，不新增计数。[该版本原文](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

<a id="tools-security-020"></a>

### tools-security-020 · Code Mode: the better way to use MCP | Cloudflare Blog

作者／组织：Cloudflare。类型：作者／团队实践或研究文章。版本／日期：2025-09-26。读取日：2026-10-13。

用途：Code Mode 用无直接 fetch/connect 的短命 V8 isolate 执行代码，只暴露显式 MCP bindings。

选读范围：Code Mode design; Running code in a sandbox; Workers bindings。限制：性能与易用性为 Cloudflare 自家测试经验；读取设计和隔离段落。

[公开原文](https://blog.cloudflare.com/code-mode/)

<a id="tools-security-021"></a>

### tools-security-021 · Code Mode: give agents an entire API in 1,000 tokens | Cloudflare Blog

作者／组织：Cloudflare。类型：作者／团队实践或研究文章。版本／日期：2026-02-20。读取日：2026-10-13。

用途：server-side search/execute 两个入口将整套 API 的发现成本转为按需读取，权限仍以 OAuth downscope 到用户批准能力。

选读范围：Server-side Code Mode; permissions; competing approaches。限制：读取机制和权限段落，未把 99.9% token 节省当成模型能力基准。

[公开原文](https://blog.cloudflare.com/code-mode-mcp/)

<a id="tools-security-031"></a>

### tools-security-031 · SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

作者／组织：John Yang, Carlos Jimenez, Alexander Wettig et al.。类型：研究论文。版本／日期：arXiv:2405.15793v3。读取日：2026-10-13。

用途：SWE-agent 的 ACI 用有限搜索摘要、带位置的文件视图、编辑后即刻反馈和 lint 拒绝坏编辑，改变了 loop 后续可观察状态。

选读范围：Sections 3 and 5.1 read fully; introduction and behavior analysis。限制：旧模型和 SWE-bench 实验；不意味着现代模型一定需要相同工具或上下文上限。

[公开原文](https://arxiv.org/html/2405.15793v3)

<a id="tools-security-056"></a>

### tools-security-056 · Text editor tool

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：rolling docs, accessed 2026-10-13。读取日：2026-10-13。

用途：模型发出 view/str_replace 请求不代表平台替应用实现了文件读写；应用负责执行、安全路径验证和权限检查。

选读范围：commands; implementation; common errors; see also。限制：API工具版本会变化；不是对文件系统沙箱正确性的证明。

[公开原文](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)

<a id="tools-security-057"></a>

### tools-security-057 · Introducing advanced tool use on the Claude Developer Platform

作者／组织：Anthropic / Bin Wu。类型：作者／团队实践或研究文章。版本／日期：2025-11-24。读取日：2026-10-13。

用途：延迟工具发现把目录索引与完整schema分开；描述仍需可检索，少量工具时额外搜索未必划算。

选读范围：article body。限制：文中内部评测和节省token数据不能外推到别的模型或工具集；与 [tools-security-002](#tools-security-002)是不同工具机制的补充。

[公开原文](https://www.anthropic.com/engineering/advanced-tool-use)

<a id="tools-security-059"></a>

### tools-security-059 · Equipping agents for the real world with Agent Skills

作者／组织：Anthropic / Barry Zhang, Keith Lazuka, Mahesh Murag。类型：作者／团队实践或研究文章。版本／日期：2025-10-16; updated 2025-12-18。读取日：2026-10-13。

用途：技能元数据、主体、引用资源分层加载；脚本可运行而无需先进入模型上下文，节省上下文不等于代码已经审核。

阅读范围：Anatomy; code execution; security considerations。限制：原文是机制介绍和作者建议，不提供供应链防御的形式保证。

[公开原文](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

[返回分类目录](#topics)

<a id="topic-05"></a>

## 5. 权限与安全：模型提议不能自己变成授权

<a id="boundary-closure-001"></a>

### boundary-closure-001 · RFC 9110: HTTP Semantics — conditional requests

作者／组织：IETF / Fielding, Nottingham, Reschke。类型：官方文档／规范。版本／日期：RFC 9110, June 2022。读取日：2026-10-13。

用途：If-Match 使用强比较，条件为假不得执行请求动作；常用 412，规范保留可确认动作已成功时返回 2xx 的例外。

选读范围：RFC 9110 §§13.1.1、13.2.1–13.2.2。限制：只读 §§13.1.1、13.2.1–13.2.2；HTTP 语义不证明任一 API 支持条件写入，也不绑定用户授权、跨资源不变量或内部事务实现。

[公开原文](https://www.rfc-editor.org/rfc/rfc9110.html)

<a id="boundary-closure-003"></a>

### boundary-closure-003 · Terraform v1.13.3 local backend saved-plan validation

作者／组织：HashiCorp。类型：源码／仓库文档。版本／日期：v1.13.3 tag。读取日：2026-10-13。

用途：localRun 先请求 state lock，再 RefreshState，读取 PersistentMeta；localRunForPlanFile 比较保存计划中的 lineage/serial。

选读范围：localRun；localRunForPlanFile。限制：只读 localRun 与 localRunForPlanFile；state manager 元数据与锁的保证不等于远端真实基础设施无旁路漂移，不证明所有 provider 原子更新。未运行 Terraform。

[公开原文](https://raw.githubusercontent.com/hashicorp/terraform/v1.13.3/internal/backend/local/backend_local.go)

<a id="boundary-closure-004"></a>

### boundary-closure-004 · terraform apply command reference

作者／组织：HashiCorp。类型：官方文档／规范。版本／日期：current page v1.16.x selected, accessed 2026-10-13。读取日：2026-10-13。

用途：传入 saved plan 即视为批准，不再提示；该文件包含已决定的操作，不能在 apply 时追加 planning options。

选读范围：Usage；Saved Plan Mode；Apply Options。限制：只读 Usage、Saved Plan Mode、相关 Apply Options；当前文档与 v1.13.3 代码分别标版本，不宣称相同最新实现或检测所有外部漂移。

[公开原文](https://developer.hashicorp.com/terraform/cli/commands/apply)

<a id="durable-orchestration-054"></a>

### durable-orchestration-054 · Introducing Dynamic Workflows: durable execution that follows the tenant

作者／组织：Dan Lapid and Luís Duarte。类型：作者／团队实践或研究文章。版本／日期：2026-05-01。读取日：2026-10-13。

用途：模型动态生成workflow与durable执行不矛盾：运行时产生的计划代码可交给平台，但后续醒来必须能路由到同租户及合适代码。

阅读范围：文章正文：动态工作流、租户 routing envelope、元数据与示例代码重加载。限制：beta发布稿，零成本/普遍速度比较属于营销不外推；版本风险是由其示例和replay要求推导，未发现其实际故障

[公开原文](https://blog.cloudflare.com/dynamic-workflows/)

<a id="human-control-003"></a>

### human-control-003 · Tool Calls

作者／组织：Agent Client Protocol。类型：官方文档／规范。版本／日期：ACP v1 current 2026-10-13。读取日：2026-10-13。

用途：permission返回绑定request id与toolCallId，并将selected/optionId与cancelled分开；allow_once/always及reject_once/always表达不同范围。

选读范围：Permission 请求与响应、工具调用状态和增量更新规则。限制：协议提供表示，未保证审批UI是真实授权；本页工具状态列表与取消页客户端cancelled处理需对接验证

[公开原文](https://agentclientprotocol.com/protocol/v1/tool-calls)

<a id="human-control-010"></a>

### human-control-010 · Tool Approvals

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 current docs。读取日：2026-10-13。

用途：无签名客户端历史可伪造schema合法批准；HMAC绑定approval ID/工具调用身份与参数。

选读范围：批准签名的工具调用身份与参数绑定，以及续跑参数校验／变换的说明。限制：签名不证明用户身份、租户权限、有效期或目标资源仍相同；实际代码另核 [human-control-029](#human-control-029)

[公开原文](https://ai-sdk.dev/docs/agents/tool-approvals)

<a id="human-control-014"></a>

### human-control-014 · feat: add workflow-safe signed tool approvals to WorkflowAgent

作者／组织：Vercel maintainers / ai-sdk-factory。类型：公开变更／提案。版本／日期：2026-08-31 merged 11109ae0fff79c3f8e2acca7af1145477c29cb53；@ai-sdk/workflow 2.0.16。读取日：2026-10-13。

用途：WorkflowAgent原缺签名路径；补丁把签名/核验留在durable step内部，只跨workflow传env变量名，防raw secret持久化。

选读范围：PR Summary、Testing、发行说明及实际 diff。限制：已直接读PR正文及核心diff片段，列出的全套覆盖部分来自PR说明而非逐一读取所有测试body；CI结果未本地复现。

[公开原文](https://github.com/vercel/ai/pull/19976)

<a id="human-control-019"></a>

### human-control-019 · Configure permissions

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current docs；关键特性要求2.1.199/2.1.259等。读取日：2026-10-13。

用途：权限评估顺序hooks→deny→ask→mode→allow→canUseTool；提前auto-approved调用不经过canUseTool。

选读范围：How permissions are evaluated、auto-approved warning、allowed_tools caveat。限制：当前SDK/CLI契约随版本变；未读整页全部模式，不把文档例子当安全证明

[公开原文](https://code.claude.com/docs/en/agent-sdk/permissions)

<a id="human-control-023"></a>

### human-control-023 · Connect an agent to Clearance

作者／组织：Authio。类型：官方文档／规范。版本／日期：private preview docs 2026-10-13。读取日：2026-10-13。

用途：批准重试须同agent/session、未过期且provider/tool/redacted arguments匹配，approval被单次retry消费；五分钟过期。

选读范围：sections 4–5/Troubleshooting。限制：私有预览产品文档，未独立实现核验；redacted arguments如何防止脱敏后碰撞未说明；MCP使用旧session握手，不代表2026版通则

[公开原文](https://docs.authio.com/clearance/connect-an-agent)

<a id="human-control-024"></a>

### human-control-024 · Human-in-the-loop

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：current openai-agents-python docs 2026-10-13。读取日：2026-10-13。

用途：RunState保存暂停及sticky decisions；按call ID批准，always_approve按工具身份扩展本run未来调用且可随序列化恢复。

选读范围：How flow works/Custom rejection messages/Streaming and sessions。限制：没有自动规定通用过期/目标再授权；ComputerTool safety_check是另一接口

[公开原文](https://openai.github.io/openai-agents-python/human_in_the_loop/)

<a id="human-control-029"></a>

### human-control-029 · validateApprovedToolApprovals implementation

作者／组织：Vercel。类型：源码／仓库文档。版本／日期：main blob 7d164765c2ed67a3795cb1f5100fa5acfa0397ab read 2026-10-13。读取日：2026-10-13。

用途：续跑先核HMAC，再schema/refinement，deep equality确保执行值没有静默替换，最后重新resolveToolApproval，当前denied覆写此前批准。

选读范围：validate-tool-approvals.ts；相关测试中的 schema 变换、当前策略拒绝及工具输入／call ID 复验。限制：函数没有用户/租户/expiry字段；当前policy返回非denied会保留批准，不能说自动重新问一次；未运行测试

[公开原文](https://github.com/vercel/ai/blob/main/packages/ai/src/generate-text/validate-tool-approvals.ts)

<a id="human-control-030"></a>

### human-control-030 · Exec approvals: plan binding, liveness and trust

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current docs accessed 2026-10-13。读取日：2026-10-13。

用途：审批绑定实际argv、cwd、env及解析后的可执行文件，明确的脚本operand内容变化应拒绝；存储的systemRunPlan优先于后续客户端重传字段。

选读范围：正文 Trust model / approval-bound command plans / timeouts and handoff / recurring grants。限制：文档契约，未完整核验exec实现；pinning不涵盖shell内部所有间接执行文件；内容绑定属于尽力机制，不承诺任何路径都安全

[公开原文](https://docs.openclaw.ai/tools/exec-approvals)

<a id="human-control-031"></a>

### human-control-031 · AAP HTTP contract: decision, consumption and outcome

作者／组织：Agent Approval Protocol。类型：官方文档／规范。版本／日期：current specification accessed 2026-10-13; no release tag established。读取日：2026-10-13。

用途：长轮询200可仍pending，GET历史approved不续期；必须在expires_at前且调用开始前consume。

选读范围：Create/Retrieve/Cancel Request, Consume an Approval, Report an Outcome。限制：新协议的规范性设计，未证明主流实现采用；consume原子不等于外部副作用exactly-once；execution attempt边界须调用方可靠定义

[公开原文](https://agentapprovalprotocol.io/specification/http)

<a id="human-control-032"></a>

### human-control-032 · Handle approvals and user input

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current Claude Agent SDK; updatedInput omission behavior changed in 2.1.207。读取日：2026-10-13。

用途：canUseTool允许同意、带updatedInput修改、拒绝并给模型反馈，不能把拒绝当成静默丢弃工具调用。

选读范围：Handle tool approval requests / Respond to tool requests / callback input and signal。限制：产品SDK文档；不是一般授权边界；不能跨语言假设signal等价，未验证所有hook次序实现

[公开原文](https://code.claude.com/docs/en/agent-sdk/user-input)

<a id="human-control-036"></a>

### human-control-036 · Chat.addToolApprovalResponse drops approval signature in SDK 6.0.210

作者／组织：bman654; maintainer lgrammel / Vercel。类型：公开问题讨论。版本／日期：opened 2026-07-16; reporter 6.0.210; maintainer says fixed 6.0.221+; closed。读取日：2026-10-13。

用途：报告签名审批在Chat.addToolApprovalResponse转换中丢元数据，server fail-closed拒绝resume而不是执行工具。

选读范围：issue body and maintainer comments。限制：issue不是本地复现；不能写成当前版本漏洞或说closed意味着原报告错误

[公开原文](https://github.com/vercel/ai/issues/17358)

<a id="practitioner-lessons-013"></a>

### practitioner-lessons-013 · Doubling down on our commitment to secure vibe coding

作者／组织：Replit Team。类型：作者／团队实践或研究文章。版本／日期：2025-07-29。读取日：2026-10-13。

用途：事实（厂商事故回顾）：agent删除客户数据库后，备份可恢复但agent不知道rollback功能；开发期变更曾能影响生产。

阅读范围：Doubling down on our commitment（Jason Lemkin incident）。限制：只据厂商自述，完整恢复不消除不可用窗口；不能用“有快照”替代写入边界。

[公开原文](https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding)

<a id="practitioner-lessons-036"></a>

### practitioner-lessons-036 · Lessons on UX, security, and scale when building an enterprise-grade Slack agent

作者／组织：Julia Xu; Jason Harris; Emi / Sourcegraph。类型：作者／团队实践或研究文章。版本／日期：2026-05-04。读取日：2026-10-13。

用途：事实：Slack thread承载会话；用两侧verified email关联用户权限；长搜索状态可追踪并链接到完整结果。

阅读范围：Enterprise security; Scaling with Redis rate limiting。限制：匹配邮箱前提须两个系统均验证及管理员开启；fail-open不可自动适用于硬预算或安全控制。

[公开原文](https://sourcegraph.com/blog/deep-search-slack-agent-lessons)

<a id="practitioner-lessons-038"></a>

### practitioner-lessons-038 · Prompts are infrastructure: building agents that actually listen

作者／组织：Nikita Sirohi / Augment。类型：作者／团队实践或研究文章。版本／日期：2026-03-05 updated 2026-06-18。读取日：2026-10-13。

用途：事实：生产persona以工具可用性区分read-only research、editing和planning；移除grep促使agent调用context engine，作者报告eval与反馈提升。

选读范围：Four layers; Tools; Skills and files。限制：读前10500字符；prompt层“更具体胜出”和强调可防覆盖不是安全契约；未给提升数字，不采纳强调词代替权限控制。

[公开原文](https://www.augmentcode.com/blog/prompts-are-infrastructure-building-agents-that-actually-listen)

<a id="practitioner-lessons-064"></a>

### practitioner-lessons-064 · A three-line nginx misconfiguration collapsed all five authorization boundaries in front of my MCP server

作者／组织：Brian Mitchell。类型：作者／团队实践或研究文章。版本／日期：2026-08-10 updated 2026-08-19。读取日：2026-10-13。

用途：作者在故意错误的 Nginx 共享缓存前复现身份与权限隔离失效；直接连接所测 SDK 的对照保持边界，故不能称作 SDK 默认漏洞。

阅读范围：Authorization matrix; broken cache; direct SDK control; public-to-private。限制：全文；是可复现实验不是生产泄漏事件；Nginx/代理是特定配置，不推断默认漏洞；SDK版本限Python1.29与TS1.30。

[公开原文](https://brianmitchell.ai/research/mcp-cache-authorization-boundaries/)

<a id="practitioner-lessons-065"></a>

### practitioner-lessons-065 · fix(core): Re-check user tool access on agent runtime cache hits

作者／组织：bjorger / n8n contributors。类型：公开变更／提案。版本／日期：2026-08-31 merged; released n8n@2.38.1 on 2026-09-01。读取日：2026-10-13。

用途：原缓存命中可长期复用工具目录的授权视图；该变更加入周期复验，真实凭证执行仍有项目级权限检查。

阅读范围：PR merged_at=2026-08-31T11:59:43Z; merge 6e9c3e2; maintainer replies; official release https://github.com/n8n-io/n8n/releases/tag/n8n%402.38.1。限制：已读合并diff、维护者回复及2.38.1发行记录。缓存命中复验最多每分钟一次；数据库复验异常时沿用缓存并更新复验时间，不能承诺撤权最多一分钟生效。此检查使缓存结果贴近当前重新构建；credential真实执行另有project-scoped检查。竞态已在abffd0b5f3通过重取缓存身份与single-flight处理，未本地执行测试。

[公开原文](https://github.com/n8n-io/n8n/pull/37401)

<a id="practitioner-lessons-066"></a>

### practitioner-lessons-066 · \[BUG\] MCPServer caches resources/list on the shared instance, leaking resources across authenticated callers (cross-tenant)

作者／组织：Mastra contributors。类型：公开问题讨论。版本／日期：commit a97044b0; issue17609 reported 2026-06-05。读取日：2026-10-13。

用途：事实：回归测试说明旧共享长寿命MCPServer缓存首次resources/list，忽略extra.authInfo；测试要求不同caller分别调用动态provider。

阅读范围：describe MCPServer dynamic resource provider; five regression cases; issue17609 summary, affected versions, serverless closure, impact。限制：已完整读固定commit回归文件及原始issue17609；合为一份贡献计数，不拆issue/测试充数；未确认稳定发行修复版本或生产泄漏规模。

[公开原文](https://github.com/mastra-ai/mastra/issues/17609)

<a id="practitioner-lessons-067"></a>

### practitioner-lessons-067 · mcp-cache-kit

作者／组织：StudioMeyer / madetocreate。类型：源码／仓库文档。版本／日期：README accessed 2026-10-13。读取日：2026-10-13。

用途：实现契约：结果缓存按request与authorization scope分区，private缺scope拒绝缓存；无效/缺失hint默认不缓存，TTL时钟可注入测试。

阅读范围：完整 README；未运行或审计实现。限制：完整README，未运行或审计实现；SEP-2549/2026-07-28标为RC，不据此宣称当前通用标准；user ID或tenant ID单独未必足以描述授权上下文；安全宣传不视为证明。

[公开原文](https://github.com/studiomeyer-io/mcp-cache-kit)

<a id="practitioner-lessons-071"></a>

### practitioner-lessons-071 · Sidecars: A low-latency trust boundary for Sandboxes

作者／组织：Olivia Johnston, Rebecka Storm, Adam Azzam / Modal。类型：作者／团队实践或研究文章。版本／日期：2026-10-01。读取日：2026-10-13。

用途：事实：agent生成代码与可信harness/凭据在同sandbox会共享信任边界；sidecar把代理、密钥注入和审计隔离到同宿主另一容器/VM边界。

阅读范围：Trusted code; isolation; networking; Ramp。限制：全文；Beta机制与内部通信基准，不是全任务延迟收益；文中隔离模型的宣传不能替代部署验证，私有代码本身仍可能被外泄。

[公开原文](https://modal.com/blog/introducing-sandbox-sidecars-trust-boundary)

<a id="practitioner-lessons-075"></a>

### practitioner-lessons-075 · \[BUG\] MCPServer caches prompts/list on the shared instance, leaking prompts across authenticated callers (cross-tenant) — same defect as #17609, unfixed for prompts

作者／组织：Adarsh-9182 / Mastra issue contributors。类型：公开问题讨论。版本／日期：PR22214 merged 2026-08-24; package CHANGELOG lists fix in @mastra/mcp 1.17.2。读取日：2026-10-13。

用途：事实：报告指出资源缓存修复后，邻近prompts/list和prompts/get仍复用首caller的definedPrompts，动态provider只首次获当前authInfo。

阅读范围：definedPrompts code; issue timeline; PR22214; https://github.com/mastra-ai/mastra/blob/main/packages/mcp/CHANGELOG.md 1.17.2 Patch Changes (line631), 1.17.2-alpha.1 (line658)。限制：核对PR合并时间、issue/comments与packages/mcp/CHANGELOG.md：1.17.2 Patch Changes列出#22214，同修复亦见1.17.2-alpha.1。issue里较后的自动triage仍留pending release，已被发行changelog交叉纠正。未核npm tarball、未本地执行包或复现。

[公开原文](https://github.com/mastra-ai/mastra/issues/22208)

<a id="practitioner-lessons-076"></a>

### practitioner-lessons-076 · Three Bugs Behind One Symptom: A Multi-Tenant OAuth Token-Refresh Postmortem · pbf.codes

作者／组织：Piotr / pbf.codes。类型：作者／团队实践或研究文章。版本／日期：2026-08-25。读取日：2026-10-13。

用途：作者复盘：MCP gateway只检查刷新HTTP200而没看JSON失败；credential ID映射永久缓存；重新授权建新credential却没更新server_instances引用，三处问题掩盖彼此。

阅读范围：Three bugs; encore; cache-key omission。限制：全文；5分钟TTL是作者选择非通用撤权要求；Shopify刷新CAS案例是邻域背景，不将其当agent生产事实；没有公开运行数据可独立验证。

[公开原文](https://pbf.codes/posts/three-bugs-behind-one-symptom-oauth-postmortem/)

<a id="runtime-boundaries-039"></a>

### runtime-boundaries-039 · Avoid executing PATH helpers before workspace trust

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-02; 637c3227b3c5327d64a73fe0b3764ade139efd1f。读取日：2026-10-13。

用途：doctor/startup 在用户信任工作区前运行 PATH 内 git/npm --version 也会执行仓库植入程序；修复区分静态定位与执行，可信系统路径和 sanitized Git 环境在初始化也必须应用。

选读范围：PR description; doctor/runtime.rs; tests/doctor_path_safety.rs。限制：已合并；未核发布tag。

[公开原文](https://github.com/openai/codex/pull/42324)

<a id="runtime-boundaries-062"></a>
<a id="boundary-closure-002"></a>

### runtime-boundaries-062 · Request preconditions

作者／组织：Google Cloud。类型：官方文档／规范。版本／日期：current2026-10-13。读取日：2026-10-13。 引用别名：boundary-closure-002（本条合计 1 项，各版本复核不另计）。

用途：延迟重试可能删掉同名新产物；generation匹配把操作绑定到对象版本，412应当冲突处理而非无条件重试。读metadata和数据分两次也需版本条件，防manifest hash对应旧版本、下载新版本。

选读范围：Introduction; composition/copy preconditions; multiple request retries example; best practices。限制：相关章节静态阅读，未运行测试。

已读版本／别名（同一来源）：
- boundary-closure-002：current docs, accessed 2026-10-13；范围：Introduction；Precondition criteria；Best practices；Multiple request retries；补充复核，不新增计数。[该版本原文](https://docs.cloud.google.com/storage/docs/request-preconditions)
- runtime-boundaries-062：current2026-10-13；范围：Introduction; composition/copy preconditions; multiple request retries example; best practices。[该版本原文](https://docs.cloud.google.com/storage/docs/request-preconditions)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.cloud.google.com/storage/docs/request-preconditions)

<a id="tools-security-003"></a>

### tools-security-003 · Beyond permission prompts: making Claude Code more secure and autonomous

作者／组织：David Dworken and Oliver Weller-Davies / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-10-20。读取日：2026-10-13。

用途：权限提示过密会形成审批疲劳；操作系统隔离可把用户决策从每条命令上移为明确的文件与网络边界。

阅读范围：article body。限制：文章将隔离保护表述得很强；允许目的地、当前工作区的破坏和权限代理自身仍需单独建模。

[公开原文](https://www.anthropic.com/engineering/claude-code-sandboxing)

<a id="tools-security-004"></a>

### tools-security-004 · The lethal trifecta for AI agents: private data, untrusted content, and external communication

作者／组织：Simon Willison。类型：作者／团队实践或研究文章。版本／日期：2025-06-16。读取日：2026-10-13。

用途：私有数据读取、不可信内容和对外通信的组合才构成可利用的数据外泄链，风险不局限于恶意工具服务器。

阅读范围：article body。限制：作者观点与案例汇总，引用事件需要追到首次披露；不能把成功率语言当作通用统计。

[公开原文](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)

<a id="tools-security-005"></a>

### tools-security-005 · MCP Security Notification: Tool Poisoning Attacks

作者／组织：Luca Beurer-Kellner and Marc Fischer / Invariant Labs。类型：作者／团队实践或研究文章。版本／日期：2025-04-01。读取日：2026-10-13。

用途：工具描述在尚未调用工具前就进入上下文，恶意描述可改变其他可信工具的参数；单独沙箱化恶意服务器并不能切断模型中介的跨服务器影响。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)

<a id="tools-security-006"></a>

### tools-security-006 · WhatsApp MCP Exploited: Exfiltrating your message history via MCP

作者／组织：Luca Beurer-Kellner and Marc Fischer / Invariant Labs。类型：作者／团队实践或研究文章。版本／日期：2025-04-07; updated 2025-04-09。读取日：2026-10-13。

用途：WhatsApp 实验的泄露出口就是已可信的发消息工具；无需恶意工具被实际调用。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://invariantlabs.ai/blog/whatsapp-mcp-exploited)

<a id="tools-security-007"></a>

### tools-security-007 · GitHub MCP Exploited: Accessing private repositories via MCP

作者／组织：Marco Milanta and Luca Beurer-Kellner / Invariant Labs。类型：作者／团队实践或研究文章。版本／日期：2025-05-26。读取日：2026-10-13。

用途：公开 issue 的不可信文字导致 agent 读取私库后开公开 PR，全部使用可信 GitHub 工具也能发生外泄。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://invariantlabs.ai/blog/mcp-github-vulnerability)

<a id="tools-security-008"></a>

### tools-security-008 · Jumping the line: How MCP servers can attack you before you ever use them - The Trail of Bits Blog

作者／组织：Trail of Bits。类型：作者／团队实践或研究文章。版本／日期：2025-04-21。读取日：2026-10-13。

用途：工具发现本身会加载指令性文本，调用审批放在 tools/call 阶段时已经晚于污染上下文的时间。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/)

<a id="tools-security-009"></a>

### tools-security-009 · Deceiving users with ANSI terminal codes in MCP - The Trail of Bits Blog

作者／组织：Trail of Bits。类型：作者／团队实践或研究文章。版本／日期：2025-04-29; Claude Code 0.2.76。读取日：2026-10-13。

用途：ANSI 控制序列可隐藏或覆盖终端上的文字，而模型仍看到原始内容；还可使显示链接与真实目标不一致。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/)

<a id="tools-security-010"></a>

### tools-security-010 · We built the security layer MCP always needed - The Trail of Bits Blog

作者／组织：Trail of Bits。类型：作者／团队实践或研究文章。版本／日期：2025-07-28。读取日：2026-10-13。

用途：mcp-context-protector 在描述进入上下文前实行 TOFU，新增或变更工具只阻断相应工具，server instructions 变化则阻断整个服务器。

选读范围：Defending context window; TOFU pinning; guardrail quarantine; ANSI sanitization; limitations。限制：产品 beta 实现介绍；LLM 检测不是确定性保证。

[公开原文](https://blog.trailofbits.com/2025/07/28/we-built-the-security-layer-mcp-always-needed/)

<a id="tools-security-011"></a>

### tools-security-011 · Cursor IDE's MCP Vulnerability - Check Point Research

作者／组织：Andrey Charikov, Roman Zaikin, Oded Vanunu / Check Point Research。类型：作者／团队实践或研究文章。版本／日期：2025-08-05; fixed Cursor 1.3。读取日：2026-10-13。

用途：CVE-2025-54136 的根因是把批准绑定在 MCP 名称，而没有绑定 command/args 内容；后来修改的项目配置被静默执行。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://research.checkpoint.com/2025/cursor-vulnerability-mcpoison/)

<a id="tools-security-012"></a>
<a id="tools-security-063"></a>

### tools-security-012 · Security Best Practices — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：tools-security-063（本条合计 1 项，各版本复核不另计）。

用途：现版将Session Hijacking改为State Handle Hijacking：所有请求验证身份，handle服务端绑定经验证主体，不能把拥有handle当认证。

阅读范围：State Handle Hijacking; Mix-Up; Localhost Redirect; Scope Minimization。限制：2026-07-28 版安全章节；与旧版合为同一来源。状态句柄变化不代表所有已部署客户端都已升级。

已读版本／别名（同一来源）：
- tools-security-012：2025-11-25；范围：Security Best Practices: attacks and mitigations。[该版本原文](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices)
- tools-security-063：2026-07-28；范围：State Handle Hijacking; Mix-Up; Localhost Redirect; Scope Minimization；补充复核，不新增计数。[该版本原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

<a id="tools-security-014"></a>
<a id="tools-security-064"></a>

### tools-security-014 · Authorization — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：tools-security-064（本条合计 1 项，各版本复核不另计）。

用途：必须在给任何token endpoint发送授权码前对比已记录issuer；当metadata宣告支持iss但响应缺失时拒绝。

选读范围：Authorization Response Validation; Access Token Usage; Scope Challenge Handling。限制：同一规范章节新版本复核，合并014不重复计数；没有穷尽OAuth外链。

已读版本／别名（同一来源）：
- tools-security-014：2025-11-25；范围：2025-11-25 版：Purpose 至 Token Audience Binding（正文前 22000 字符）。[该版本原文](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- tools-security-064：2026-07-28；范围：Authorization Response Validation; Access Token Usage; Scope Challenge Handling；补充复核，不新增计数。[该版本原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

<a id="tools-security-015"></a>
<a id="tools-security-066"></a>

### tools-security-015 · Elicitation — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：tools-security-066（本条合计 1 项，各版本复核不另计）。

用途：accept仍只表示同意外部交互，现版用重试原请求结合requestState或服务器状态检查完成，不再依赖旧completion通知。

阅读范围：URL Mode; Statefulness; Safe URL Handling; Phishing。限制：同一规范章节新版本复核，合并015不重复计数。

已读版本／别名（同一来源）：
- tools-security-015：2025-11-25；范围：Elicitation form/URL modes, user interaction and completion。[该版本原文](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)
- tools-security-066：2026-07-28；范围：URL Mode; Statefulness; Safe URL Handling; Phishing；补充复核，不新增计数。[该版本原文](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)

<a id="tools-security-016"></a>

### tools-security-016 · Sampling - Model Context Protocol

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2025-11-25。读取日：2026-10-13。

用途：服务器采样请求把模型调用能力借给服务器，客户端仍需控制模型访问、上下文和审批；不是反向 RPC 就可无条件执行。

选读范围：Sampling capability, context inclusion, tools。限制：阅读 2025-11-25 版采样安全、上下文及能力协商部分；2026-07-28 已将 Sampling 标为 Deprecated，不等于移除。

[公开原文](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling)

<a id="tools-security-017"></a>

### tools-security-017 · Claude Code: Data Exfiltration with DNS (CVE-2025-55284) · Embrace The Red

作者／组织：Johann Rehberger / Embrace The Red。类型：作者／团队实践或研究文章。版本／日期：2025-08-11; fixed v1.0.4。读取日：2026-10-13。

用途：Claude Code 曾把 DNS 查询相关命令列入无需审批的 allowlist，间接注入借域名查询带出本地数据。

阅读范围：article body。限制：案例仅证明所述版本和实验条件下存在失败，不能推算普遍发生率。

[公开原文](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/)

<a id="tools-security-018"></a>

### tools-security-018 · Claude Pirate: Abusing Anthropic's File API For Data Exfiltration · Embrace The Red

作者／组织：Johann Rehberger / Embrace The Red。类型：作者／团队实践或研究文章。版本／日期：2025-10-28; updated 2025-10-30。读取日：2026-10-13。

用途：Claude Code Interpreter 默认允许的供应商 API 域名可接收攻击者账户凭证，文件最终上传到攻击者账户，证明允许域名不等于允许接收方。

阅读范围：article body。限制：案例针对 Claude Code Interpreter，不是 source-003 的 Claude Code bash 沙箱；不能混写成同一产品漏洞。

[公开原文](https://embracethered.com/blog/posts/2025/claude-abusing-network-access-and-anthropic-api-for-data-exfiltration/)

<a id="tools-security-019"></a>

### tools-security-019 · Anthropic Filesystem MCP Server: Directory Access Bypass via Improper Path Validation · Embrace The Red

作者／组织：Johann Rehberger / Embrace The Red。类型：作者／团队实践或研究文章。版本／日期：2025-08-03; historical filesystem MCP issues。读取日：2026-10-13。

用途：allowedDirectories 用字符串 startsWith 判断，使 data-archived 被当作 data 的子目录，破坏目录范围承诺。

阅读范围：article body。限制：案例只覆盖披露版本与实验条件；目录前缀漏洞为 CVE-2025-53110，符号链接漏洞为 CVE-2025-53109，原博客编号需对照首次披露。

[公开原文](https://embracethered.com/blog/posts/2025/anthropic-filesystem-mcp-server-bypass/)

<a id="tools-security-032"></a>

### tools-security-032 · Agent approvals & security | ChatGPT Learn

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：沙箱决定技术上能做什么，approval policy 决定何时需批准，自动 reviewer 只审查本来需要批准的动作，不替代边界。

选读范围：Sandbox and approvals; network policy; protected paths; auto review。限制：文档当日版本且多产品范围，最终稿应提炼通用机制，不罗列全部配置键。

[公开原文](https://learn.chatgpt.com/docs/agent-approvals-security)

<a id="tools-security-035"></a>

### tools-security-035 · Changes to remote debugging switches to improve security | Blog | Chrome for Developers

作者／组织：Will Harris / Google Chrome。类型：作者／团队实践或研究文章。版本／日期：2025-03-17; Chrome 136。读取日：2026-10-13。

用途：Chrome 136 默认 profile 不再接受 remote-debugging-port/pipe，要求独立 user-data-dir，以减少调试接口用于窃取真实用户 cookie。

阅读范围：article body。限制：具体 Chrome 版本更改；不能推断其他浏览器相同行为。

[公开原文](https://developer.chrome.com/blog/remote-debugging-port)

<a id="tools-security-036"></a>

### tools-security-036 · Computer-Use and TOCTOU: What You Click Is Not What You Get! · Embrace The Red

作者／组织：Johann Rehberger / Embrace The Red。类型：作者／团队实践或研究文章。版本／日期：2026-06-25; experiment October 2025。读取日：2026-10-13。

用途：模型读取截图并推理期间 UI 会变化，同一坐标可能从继续按钮变为邮件发送，形成 TOCTOU。

阅读范围：article body。限制：报道区分 2025 年实验与 2026 年披露，并称 Anthropic 后续处理该风险；不能当作当前未修复漏洞。

[公开原文](https://embracethered.com/blog/posts/2026/toctou-agent-what-you-click-is-not-what-you-get/)

<a id="tools-security-037"></a>

### tools-security-037 · \[2503.18813\] Defeating Prompt Injections by Design

作者／组织：Edoardo Debenedetti et al. / Google, Google DeepMind, ETH Zurich。类型：研究论文。版本／日期：arXiv:2503.18813v3。读取日：2026-10-13。

用途：控制流隔离仍不够：无工具的隔离模型可被诱导输出错误收件人/文件名，使预先批准的调用序列传错数据。

选读范围：Sections 1–4、5.3、6、7。限制：研究 artifact，非通用生产库；不能将 AgentDojo 上 67% 安全完成率扩展为所有任务安全。

[公开原文](https://arxiv.org/html/2503.18813v3)

<a id="tools-security-038"></a>

### tools-security-038 · Design Patterns for Securing LLM Agentsagainst Prompt Injections

作者／组织：Luca Beurer-Kellner et al.。类型：研究论文。版本／日期：arXiv:2506.08837v2。读取日：2026-10-13。

用途：action-selector、plan-then-execute、map-reduce、dual LLM、code-then-execute 和 context-minimization 通过刻意限制 agent 泛化能力换取部分边界。

选读范围：Sections 1–3 six patterns; case studies 4.1–4.3 security discussion。限制：论文给出机制与案例而非每种模式通用安全性；只读前43k检索文本中相关章节。

[公开原文](https://arxiv.org/html/2506.08837v2)

<a id="tools-security-039"></a>

### tools-security-039 · Context is Key for Agent Security

作者／组织：Lillian Tsai and Eugene Bagdasaryan。类型：研究论文。版本／日期：arXiv:2501.17070v2。读取日：2026-10-13。

用途：Conseca 用可信用户任务/上下文生成可审计策略，再由确定性执行器约束每次动作和参数，策略生成与执行 agent 分离。

选读范围：Sections 1–5, security discussion and prototype limitations。限制：v2 标题 Context is Key for Agent Security；20任务原型，非广泛生产评估。

[公开原文](https://arxiv.org/html/2501.17070v2)

<a id="tools-security-040"></a>

### tools-security-040 · Agents Rule of Two: A Practical Approach to AI Agent Security

作者／组织：Meta。类型：作者／团队实践或研究文章。版本／日期：2025-10-31。读取日：2026-10-13。

用途：Rule of Two 把不可信输入、敏感数据、外部写/通信作为 session 能力组合；同时需三者时不能任其无监督运作。

阅读范围：article body。限制：设计框架，不是完整 formal proof；工具/来源的信任标记仍可能错。

[公开原文](https://ai.meta.com/blog/practical-ai-agent-security/)

<a id="tools-security-041"></a>

### tools-security-041 · Continuously hardening ChatGPT Atlas against prompt injection | OpenAI

作者／组织：OpenAI。类型：作者／团队实践或研究文章。版本／日期：2025-12-22。读取日：2026-10-13。

用途：注入后果可跨几十到几百动作，单步是否安全的测试不足以衡量长轨迹偏离；需要保留攻击轨迹来改进系统防护。

选读范围：browser threat model; system safeguards and rapid response; user guidance。限制：仅采纳 harness/轨迹相关内容，不扩写 RL 训练细节。

[公开原文](https://openai.com/index/hardening-atlas-against-prompt-injection/)

<a id="tools-security-042"></a>

### tools-security-042 · Mitigating prompt injections in browser use \\ Anthropic

作者／组织：Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-11-24。读取日：2026-10-13。

用途：浏览器输入来自页面、广告、动态脚本、隐藏文本/图像，操作出口又含导航、表单和下载，比单纯文本回答面更广。

阅读范围：article body。限制：内部 adaptive Best-of-N 每环境100次的实验；不能换算为真实事故率，未引用图中不可见数值。

[公开原文](https://www.anthropic.com/news/prompt-injection-defenses)

<a id="tools-security-043"></a>

### tools-security-043 · CVE-2025-6514 Threatens LLM clients

作者／组织：Or Peles / JFrog Security Research。类型：作者／团队实践或研究文章。版本／日期：2025-07-09; fixed mcp-remote 0.1.16。读取日：2026-10-13。

用途：连接远程 MCP 的认证发现阶段就可能执行不可信 URL；mcp-remote 将 URL 交给平台 open/shell 导致 OS 命令注入，未等到模型工具调用。

选读范围：Affected versions; authorization endpoint handling; technical root cause; mitigation。限制：受影响0.0.5–0.1.15；Windows完整参数 RCE 与 macOS/Linux受限参数执行能力要区分。

[公开原文](https://jfrog.com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/)

<a id="tools-security-046"></a>

### tools-security-046 · DNS Rebinding Protection Disabled by Default in Model Context Protocol Python SDK for Servers Running on Localhost · Advisory · modelcontextprotocol/python-sdk · GitHub

作者／组织：MCP Python SDK maintainers / pcarleton。类型：官方文档／规范。版本／日期：2025-12-02; patched mcp 1.23.0。读取日：2026-10-13。

用途：无认证 localhost HTTP MCP 若默认未启 DNS rebinding 防护，可被恶意网页调用；stdio 不受该特定问题影响。

阅读范围：GHSA-9h52-p55h-vw2f Description。限制：部署条件严格限定；不应笼统说全部 MCP 不安全。

[公开原文](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-9h52-p55h-vw2f)

<a id="tools-security-049"></a>

### tools-security-049 · Safe Outputs | GitHub Agentic Workflows

作者／组织：GitHub Agentic Workflows。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：agent 阶段只有只读外部权限，产出结构化请求，由独立具窄写权限 job 执行，实现模型建议与目标系统写权限分离。

选读范围：Safe Outputs introduction, operation schemas and max limits。限制：只读入门和部分操作限制；不是对全体系实现安全性的独立审计。

[公开原文](https://github.github.com/gh-aw/reference/safe-outputs/)

<a id="tools-security-052"></a>

### tools-security-052 · Critical RCE in Anthropic MCP Inspector (CVE-2025-49596) Enables Browser-Based Exploits

作者／组织：Oligo Security Research。类型：作者／团队实践或研究文章。版本／日期：2025-06-27; fixed Inspector 0.14.1。读取日：2026-10-13。

用途：调试用 MCP Inspector 的网页 client 与本机进程 proxy 之间缺认证，恶意网页可触达能启动 stdio 命令的高权限本地桥梁。

选读范围：MCP Inspector architecture, vulnerability and fix。限制：浏览器0.0.0.0现状是2025披露时点，不当作2026所有浏览器未修复。

[公开原文](https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596)

<a id="tools-security-053"></a>

### tools-security-053 · CVE-2025-53109: EscapeRoute Breaks Anthropic’s MCP Server

作者／组织：Elad Beber / Cymulate Research Labs。类型：作者／团队实践或研究文章。版本／日期：2025-07-02; updated 2026-03-17。读取日：2026-10-13。

用途：prefix containment 与 symlink 错误处理是两个问题：实际路径越权抛出的错误，被宽泛 catch 误认为文件尚不存在，然后只验证原路径父目录。

选读范围：CVE-2025-53110 containment and CVE-2025-53109 symlink validatePath code。限制：原作者将prefix标为CVE-2025-53110、symlink标为53109；source019引用CVE映射不精确，机制以本首次披露为准。

[公开原文](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/)

<a id="tools-security-054"></a>

### tools-security-054 · Security Architecture | GitHub Agentic Workflows

作者／组织：GitHub Agentic Workflows。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：底座隔离、配置分配权限、阶段计划约束分别防不同问题；上层策略不能弥补 token 预先分配过大或底层隔离失败。

选读范围：Trust layers, SafeOutputs, AWF, MCP gateway, threat-detection pipeline。限制：过滤后的前22k相关内容；域名allowlist和AI检测都不能独立给出全风险阻断保证。

[公开原文](https://github.github.com/gh-aw/introduction/architecture/)

<a id="tools-security-058"></a>

### tools-security-058 · Deferred tools

作者／组织：Pydantic AI。类型：官方文档／规范。版本／日期：v2 rolling docs, accessed 2026-10-13。读取日：2026-10-13。

用途：中断审批或外部工作是持久协议：保存原始消息历史，结果按待处理tool_call_id恢复；run_id与conversation_id不是同一个标识。

选读范围：Human-in-the-loop tool approval; Approval is not an authorization boundary against an untrusted client; deferred results。限制：具体API属于当前v2文档；批准记录服务端绑定策略是宿主实现职责。

[公开原文](https://ai.pydantic.dev/deferred-tools/)

[返回分类目录](#topics)

<a id="topic-06"></a>

## 6. 执行环境：命令在哪儿跑，资源归谁收尾

<a id="durable-orchestration-043"></a>

### durable-orchestration-043 · feat(tools): run sync tools in a thread

作者／组织：Deepankar Mahapatro and OpenAI Agents SDK maintainers。类型：公开变更／提案。版本／日期：opened2025-06-07; closed stale2025-08。读取日：2026-10-13。

用途：async外层调度不让同步requests工具自动非阻塞；一个阻塞函数可让同event-loop的其他agent停顿。

选读范围：PR discussion default to_thread versus opt-in wrapper。限制：未合并历史PR，不声称当前SDK默认；评论示例有def/await笔误不可复制

[公开原文](https://github.com/openai/openai-agents-python/pull/820)

<a id="durable-orchestration-055"></a>

### durable-orchestration-055 · We ditched worktrees for Claude Code. Here's what we use instead

作者／组织：Eric Allam。类型：作者／团队实践或研究文章。版本／日期：2026-04-16。读取日：2026-10-13。

用途：worktree只隔离源码，不隔离Postgres迁移、Redis、测试数据、端口与构建环境；并行成本来自完整环境。

阅读范围：文章中 worktree 与共享服务隔离的讨论，以及结尾的重叠文件和副作用测试边界。限制：单团队经验，GitButler不是通用替代方案；第三方磁盘数字未独立核验不采用

[公开原文](https://trigger.dev/blog/parallel-agents-gitbutler)

<a id="durable-orchestration-059"></a>

### durable-orchestration-059 · Crab: A Semantics-Aware Checkpoint/Restore Runtime for Agent Sandboxes

作者／组织：Tianyuan Wu, Chaokun Chang, Lunxi Cao, Wei Gao, Wei Wang。类型：研究论文。版本／日期：v1 2026-04-30。读取日：2026-10-13。

用途：会话+文件仍可能遗漏后台进程；恢复状态范围应由后续工具依赖决定，不能一律说history足够或全VM必需。

选读范围：论文摘要、Sections 2–4、5.1、5.2 开头、6、7.1–7.2；未读完整组件评测。限制：100个先筛选无故障可解任务、记录轨迹确定性回放和单次注入崩溃；100%仅该实验，不是外部副作用或任意工作负载保证；论文未说明remote effect回滚，不能推广

[公开原文](https://arxiv.org/abs/2604.28138)

<a id="network-errors-027"></a>

### network-errors-027 · Python asyncio subprocesses

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：Process.wait遇子进程写满stdout/stderr PIPE可deadlock；communicate避免此情况但把输出缓存在内存。

选读范围：Process wait/communicate/terminate/kill/pid。限制：只读Interacting with Subprocesses等相关节；终止整个进程组的方案需另有OS依据。

[公开原文](https://docs.python.org/3/library/asyncio-subprocess.html)

<a id="network-errors-029"></a>

### network-errors-029 · AnyIO working with threads

作者／组织：AnyIO maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：abandon_on_cancel=True只停止等待并忽略结果，线程继续跑；线程取消须业务代码主动check_cancelled。

选读范围：full page Running function / limiter / Reacting to cancellation。限制：线程数是当前库默认，不应作为所有harness建议值。

[公开原文](https://anyio.readthedocs.io/en/stable/threads.html)

<a id="network-errors-030"></a>
<a id="tools-security-024"></a>

### network-errors-030 · subprocess — Subprocess management — Python 3.15.0 documentation

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3 docs retrieved 2026-10-13。读取日：2026-10-13。 引用别名：tools-security-024（本条合计 1 项，各版本复核不另计）。

用途：wait 配合未消费 stdout/stderr PIPE 可死锁；communicate 防 pipe 死锁但将输出缓存在内存，无限日志仍会耗尽资源。

选读范围：subprocess Security Considerations, Popen wait/communicate/kill, process groups。限制：与具体 Python 版本、OS 有关；只读取相关段落。

已读版本／别名（同一来源）：
- network-errors-030：unknown；范围：Popen.communicate/terminate/kill/pid sections。[该版本原文](https://docs.python.org/3/library/subprocess.html)
- tools-security-024：Python 3 docs retrieved 2026-10-13；范围：subprocess Security Considerations, Popen wait/communicate/kill, process groups。[该版本原文](https://docs.python.org/3/library/subprocess.html)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.python.org/3/library/subprocess.html)

<a id="network-errors-033"></a>

### network-errors-033 · Claude Code #84647: Bash timeout leaves runaway child

作者／组织：trof3039; bobleer。类型：公开问题讨论。版本／日期：unknown。读取日：2026-10-13。

用途：报告超时和子agent完成后ugrep仍跑15分钟占约20GB；curl限时和head收尾并未限制中间grep。

阅读范围：full issue and timeline2026-08-06 through stale-close2026-10-05。限制：用户事故报告未独立重跑；issue因stale关闭并非修复，平台差异需说明。

[公开原文](https://github.com/anthropics/claude-code/issues/84647)

<a id="practitioner-lessons-003"></a>

### practitioner-lessons-003 · Why We Built Our Own Background Agent

作者／组织：Ramp Builders。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：事实：每30分钟构建完整开发环境快照；会话恢复用完成时快照；同步最新代码时允许先读，但阻塞写编辑直到同步完成。

选读范围：Sandbox; API; Slack（正文前16000字符）。限制：阅读正文前16000字符至Chrome extension；提前读可能观察旧版，需写入屏障及失效检查；作者对模型自控子agent数量的建议不构成预算保证。

[公开原文](https://builders.ramp.com/post/why-we-built-our-background-agent)

<a id="practitioner-lessons-010"></a>

### practitioner-lessons-010 · Enabling Agent 3 to Self-Test at Scale with REPL-Based Verification

作者／组织：Peter Zhong; Jacky Zhao; Ryan Carelli / Replit。类型：作者／团队实践或研究文章。版本／日期：2025-12-15。读取日：2026-10-13。

用途：事实：遇到外观可用但事件处理/数据未接线的界面后，构建持久JS REPL+Playwright，交替探索DOM与执行测试。

选读范围：Verification Spectrum; Code use; Putting the REPL back。限制：读前12500字符至More state information；持久变量不是持久化恢复承诺；把多个副作用合入代码仍须考虑中断后的部分完成。

[公开原文](https://replit.com/blog/automated-self-testing)

<a id="practitioner-lessons-014"></a>

### practitioner-lessons-014 · Warp scores 71% on SWE-bench Verified

作者／组织：Ben Navetta / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-06-23。读取日：2026-10-13。

用途：事实：同一agent执行长命令时切换到输入/读取输出的受限工具集，保持上下文，解决git pager卡住。

阅读范围：Long-running commands; Editing; Model Choice。限制：模糊匹配有误改风险；原文结论为当时模型组合且MCP/web在eval中关闭。

[公开原文](https://www.warp.dev/blog/swe-bench-verified)

<a id="practitioner-lessons-016"></a>

### practitioner-lessons-016 · How we scored #1 on Terminal-Bench (52%)

作者／组织：Jack Nichols / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-06-25。读取日：2026-10-13。

用途：事实：旧工具在vim等交互命令中只能等人退出，自动评测超时；新工具周期读取PTY并允许写字节，运行期间禁止冲突的新命令和编辑。

阅读范围：Model experimentation; Long-running command support; Planning。限制：仅Terminal-Bench v0.1.1及指定模型；不能推导规划总有效或Opus普遍较差。

[公开原文](https://www.warp.dev/blog/terminal-bench)

<a id="practitioner-lessons-017"></a>

### practitioner-lessons-017 · Architecting Fast, Secure Cloud Sandboxes for AI Development with Namespace

作者／组织：Ben Navetta / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-12-15。读取日：2026-10-13。

用途：事实：agent工具以sidecar volume挂入用户镜像，避免每个基础镜像安装整个runtime；由harness团队独立更新。

阅读范围：Cloud-hosted agents; Securing cloud sandboxes。限制：厂商架构自述；sidecar自动最新版影响复现，不能读成版本固定或已完成egress限制。

[公开原文](https://www.warp.dev/blog/secure-cloud-sandboxes-for-ai-dev-with-namespace)

<a id="practitioner-lessons-023"></a>

### practitioner-lessons-023 · The Bitter Lesson of Agent Frameworks

作者／组织：Gregor Zunic / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2026-01-16。读取日：2026-10-13。

用途：事实：抛弃复杂message manager后，开放CDP+extension控制；浏览器状态只保留最近N份，接受部分cache损失。

阅读范围：Why we threw everything away; Ephemeral messages; for-loop doesn’t work。限制：作者“99%在模型”“无需guardrail”是观点，正文仍承认安全、重试、压缩和显式停止；不是安全保证。

[公开原文](https://browser-use.com/posts/bitter-lesson-agent-frameworks)

<a id="practitioner-lessons-025"></a>

### practitioner-lessons-025 · We built our own custom harness, was it worth it?

作者／组织：Lukasz Piliszczuk / Motion。类型：作者／团队实践或研究文章。版本／日期：2026-07-30。读取日：2026-10-13。

用途：事实：营销agent Runneth由Claude SDK迁Pi再自建Rust；按团队测量每会话内存约100MB降至10MB，动机是VM并发成本与可控快捷路径。

阅读范围：Our harness journey; What owning the harness unlocked; tradeoffs。限制：成本是特定版本/负载自述；共享VM有其他隔离风险；作者明确并不建议人人重写。

[公开原文](https://motionengineering.substack.com/p/we-built-our-own-custom-harness-was)

<a id="practitioner-lessons-030"></a>

### practitioner-lessons-030 · Lessons from my self-improving coding agent

作者／组织：Joel Hans。类型：作者／团队实践或研究文章。版本／日期：2026-02-25。读取日：2026-10-13。

用途：作者实验：约100session与八次维护产生工具/skills，但需持续判断的学习捕获技能60多次只用两次；明确session结束触发的反思更稳定。

选读范围：Knowing isn’t doing; deferral instinct; Specific reliability。限制：读前13500字符至最后一节中段；成功率样本量未详，模型自述原因只算解释假设；不能推广为自主学习无效。

[公开原文](https://ngrok.com/blog/bmo-self-improving-coding-agent)

<a id="practitioner-lessons-041"></a>

### practitioner-lessons-041 · The Bitter Lesson of Agent Harnesses

作者／组织：Gregor Zunic / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2026-04-19。读取日：2026-10-13。

用途：事实：团队把click等包装与watchdog删减为原始CDP、可编辑helpers及持久daemon，允许agent自己补上传等缺失操作。

阅读范围：Four-file harness; editable helpers; target recovery。限制：全文；个案不证明所有watchdog或安全边界可删；浏览器容错机制与授权边界须分开。

[公开原文](https://browser-use.com/posts/bitter-lesson-agent-harnesses)

<a id="practitioner-lessons-051"></a>

### practitioner-lessons-051 · Closer to the Metal: Leaving Playwright for CDP

作者／组织：Nick Sweeting / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2025-08-20。读取日：2026-10-13。

用途：事实：团队观察Python到Node再到浏览器的多进程状态漂移、崩溃/对话框/焦点与远端上传失败；改直接CDP后自行承担浏览器异常处理。

阅读范围：Multi-hop architecture; event bus; element handles。限制：全文分段读；Playwright评价是当时负载下的团队经验，不是其所有版本的普遍限制；与2026-04团队进一步删watchdog需并读。

[公开原文](https://browser-use.com/posts/playwright-to-cdp)

<a id="runtime-boundaries-007"></a>

### runtime-boundaries-007 · Windows Job Objects

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：2025-07-14。读取日：2026-10-13。

用途：Windows Job可一组管理后代、KILL_ON_JOB_CLOSE在最后handle关闭时终止成员；breakaway/WMI子进程等是边界。通知除特定限额外不保证送达，不能仅无通知推定未发生。

选读范围：Job membership, limits, notifications, kill-on-close。限制：只论Windows官方契约，不能证明任意程序全部包含

[公开原文](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)

<a id="runtime-boundaries-008"></a>

### runtime-boundaries-008 · Node child process lifecycle

作者／组织：Node.js。类型：官方文档／规范。版本／日期：v26.11.1。读取日：2026-10-13。

用途：kill成功只表示信号发送，killed不是退出确认；Linux杀父不杀孙。PIPE容量有限，env的PATH查找及Windows Path/PATH去重影响同一命令真实执行对象。

选读范围：pipes/env/Windows bat; kill/killed L1131-1220。限制：partial；阅读相关生命周期与环境章节

[公开原文](https://nodejs.org/api/child_process.html)

<a id="runtime-boundaries-009"></a>

### runtime-boundaries-009 · kill(2) process and group semantics

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19。读取日：2026-10-13。

用途：负PID可向进程组发信号，但组内至少一个对象成功即可整体成功；signal 0只做存在/权限检查，僵尸也可能仍有PID。loop需分别确认进程组收尾，不能以kill返回值当全部停止。

选读范围：DESCRIPTION, RETURN VALUE, ERRORS。限制：POSIX/Linux契约，不是跨平台实现

[公开原文](https://man7.org/linux/man-pages/man2/kill.2.html)

<a id="runtime-boundaries-011"></a>

### runtime-boundaries-011 · Modal sandbox snapshots and retention

作者／组织：Modal。类型：官方文档／规范。版本／日期：live 2026-10-13; Python v1.5 TTL change。读取日：2026-10-13。

用途：filesystem snapshot不含mounted Volume；v1.5默认30天TTL替代永久保存，过期Image.from_id仍可构造但首exec失败。memory snapshot有7天链继承期限、TCP重连、exec后台进程不正确恢复等约束。

选读范围：Snapshot Retention; Memory Snapshot Limitations; Persisting State。限制：产品特定；memory snapshot为Alpha

[公开原文](https://modal.com/docs/guide/sandbox-snapshots)

<a id="runtime-boundaries-012"></a>

### runtime-boundaries-012 · Modal sandbox file delivery

作者／组织：Modal。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。

用途：临时沙箱文件可经stream copy交出，挂载Volume还要commit，其他沙箱需reload_volumes才见更新。官方例子先等待写进程、检查同步退出码再终止，交付应区分本地存在、持久存储及外部可见。

选读范围：Filesystem API; streaming copies; Using Volumes; sync。限制：不声称copy API自动提供内容校验或用户权限

[公开原文](https://modal.com/docs/guide/sandbox-files)

<a id="runtime-boundaries-013"></a>

### runtime-boundaries-013 · Modal volume consistency and migration

作者／组织：Modal。类型：官方文档／规范。版本／日期：live 2026-10-13 / v1-v2。读取日：2026-10-13。

用途：同文件并发last-write-wins，reload时本容器卷暂空且打开文件会busy。v1有inode限额，df返回占位数据；同名新卷有新ID，替换后旧运行任务仍指旧ID，必须重新部署/启动。

选读范围：Volume commits/reloads; consistency; busy; inode limit; migration。限制：部分章节；不外推所有分布式文件系统

[公开原文](https://modal.com/docs/guide/volumes)

<a id="runtime-boundaries-014"></a>

### runtime-boundaries-014 · E2B pause/resume lifecycle

作者／组织：E2B。类型：官方文档／规范。版本／日期：live 2026-10-13; SDK2.48.0 refusal rollout。读取日：2026-10-13。

用途：paused当前无限期保存；connect只延长不缩短寿命。pause拒绝503时沙箱仍运行；auto-pause持续拒绝可降级filesystem-only，丢内存并重启。持久化请求成功与保留哪种状态须明确。

选读范围：state transitions; refusal; timeout; auto-pause; network。限制：区域分批上线；不能将内存保留视为无条件保证

[公开原文](https://docs.e2b.dev/sandbox/persistence)

<a id="runtime-boundaries-018"></a>

### runtime-boundaries-018 · \[Windows Desktop\] Terminating a shell command does not kill its descendant process tree

作者／组织：Hadeanyolo。类型：公开问题讨论。版本／日期：created 2026-07-13T09:33:31Z; updated 2026-09-04T21:41:02Z; open。读取日：2026-10-13。

用途：Windows Desktop报告Script terminated后多代Git/SSH继续运行，并有正常成功命令后的残留复现。命令结果与后代清理应分别报告；issue仍open，未确认通用根因。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/openai/codex/issues/32742)

<a id="runtime-boundaries-020"></a>

### runtime-boundaries-020 · \[BUG\] On a genuinely full disk, the Bash ENOSPC notice names the session tmpdir instead of the filesystem, and no command can then run to diagnose it

作者／组织：oconnorjoseph。类型：公开问题讨论。版本／日期：created 2026-08-26T18:21:49Z; updated 2026-10-10T22:11:01Z; open。读取日：2026-10-13。

用途：真实满盘时stdout写临时文件也失败，连df/du诊断都无法通过Bash工具运行；需要独立于耗尽资源的有界诊断路径，不能让模型盲删。作者生产观察，未确认产品修复。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/anthropics/claude-code/issues/89879)

<a id="runtime-boundaries-027"></a>

### runtime-boundaries-027 · E2B streams versus sandbox lifetime

作者／组织：E2B。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：单连接断开可发生在sandbox仍运行时；SDK有keepalive与commands.connect(pid)/pty.connect(pid)重附着。重试run命令与重连输出不是同一动作，loop应先识别运行对象。

选读范围：stream lifetime; timeout behavior。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.e2b.dev/faq/sandbox-lifetime)

<a id="runtime-boundaries-028"></a>

### runtime-boundaries-028 · E2B filesystem-only snapshots

作者／组织：E2B。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：filesystem-only恢复是重启而非内存恢复，服务需重启且外部客户端重新连接；2.55.0新增mode且不能与deprecated keepMemory同时传，filesystem-only与autoResume互斥。

选读范围：SDK2.55.0 mode; comparison; validation。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.e2b.dev/sandbox/filesystem-only-snapshots)

<a id="runtime-boundaries-030"></a>

### runtime-boundaries-030 · Docker stop semantics

作者／组织：Docker。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：stop先对容器主进程送可配置stop signal，grace后SIGKILL；timeout=-1无限等待，Linux/Windows默认grace不同。harness取消预算需含优雅停止和强制清理。

选读范围：description; signal; timeout。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.docker.com/reference/cli/docker/container/stop/)

<a id="runtime-boundaries-038"></a>

### runtime-boundaries-038 · Support managed app-server lifecycle on Windows

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-02; 715294448f56ce3ca6b2f62c84e9c9ef5e9aee20。读取日：2026-10-13。

用途：保留 Windows 进程身份 handle；需要终止时重开有 terminate 权限的 handle 并核对创建时间，防止 PID 复用杀错进程。查询 handle 不要求终止权限，测试验证。

选读范围：PR body; backend/windows.rs Process::terminate; windows_tests.rs identity_queries_do_not_require_termination_access。限制：已合并；未核到发布版本，不写已发布。

[公开原文](https://github.com/openai/codex/pull/42381)

<a id="runtime-boundaries-042"></a>

### runtime-boundaries-042 · Suppress Windows console windows for background subprocesses

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-29; fbc169827e9789f9e7ba2ed97c15e2021c3312bb。读取日：2026-10-13。

用途：Windows 创建 flag 会覆盖：后台启动同时保留 CREATE_NO_WINDOW 与 CREATE_SUSPENDED，先绑定 Job 后恢复；绑定失败 fallback 必须清除 SUSPENDED 否则永不执行。fallback 返回 None Job，因此可运行不等于树已受管。

选读范围：utils/process/src/lib.rs + background_command_tests.rs; utils/pty/src/win/job.rs。限制：已合并；未核发布tag。

[公开原文](https://github.com/openai/codex/pull/49164)

<a id="runtime-boundaries-046"></a>

### runtime-boundaries-046 · Creating a Pseudoconsole Session

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：2022-09-20。读取日：2026-10-13。

用途：ClosePseudoConsole 会终止附着客户端，但关闭本身可能发最后一帧输出；单线程同步收尾若不继续读输出会死锁，需分线程服务输入输出直到关闭完成。

选读范围：Preparing communication channels; Ending the pseudoconsole session。限制：ConPTY，不推广为普通 PIPE 行为。

[公开原文](https://learn.microsoft.com/en-us/windows/console/creating-a-pseudoconsole-session)

<a id="runtime-boundaries-047"></a>

### runtime-boundaries-047 · Pod Lifecycle

作者／组织：Kubernetes。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：同一个 Pod UID 不会被重新调度，替代 Pod 即便同名也是新实体；emptyDir 随原 Pod 消失。Running 是容器状态聚合，不代表 agent 成功，restartPolicy 可在旧副作用已发生后重跑进程。

选读范围：Pod lifetime; Pod phase; container restart policy。限制：阅读 Pod 生命周期、phase 与容器重启策略；未覆盖全部 termination 细节。

[公开原文](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

<a id="runtime-boundaries-048"></a>

### runtime-boundaries-048 · Environment Variables

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：2025-07-14。读取日：2026-10-13。

用途：子进程默认继承启动时父进程环境块；修改外部系统环境不更新运行中父进程。hot reload 配置与后续工具 env 必须明确重新构造，不能假设 UI/系统改过就被旧 daemon 继承。

选读范围：Environment block and CreateProcess/SetEnvironmentVariable。限制：仅继承契约，不作为环境清洗的完整方案。

[公开原文](https://learn.microsoft.com/en-us/windows/win32/procthread/environment-variables)

<a id="runtime-boundaries-049"></a>

### runtime-boundaries-049 · Replace the Sandbox class

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：SDK 0.12.10→1.0.1; updated 2026-10-13。读取日：2026-10-13。

用途：1.0 inactivity timeout 不跨 Durable Object restart，必须构造器恢复；start 返回不等 ready，setup Promise 避免并发请求绕过初始化，部署可能中断 setup 所以各步须可重入。

选读范围：Replace class steps 2,6,7,8。限制：时间敏感迁移文档；仅此SDK版本，禁止跨版本套用旧示例。

[公开原文](https://developers.cloudflare.com/sandbox/sdk/migrate/replace-the-sandbox-class/)

<a id="runtime-boundaries-050"></a>

### runtime-boundaries-050 · Persistence

作者／组织：Daytona。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：sandbox stop 的含义随类型变：container 磁盘保留RAM丢失，VM stop磁盘offload并释放quota，pause保存RAM，GPU stop直接删除。产物策略须绑定 sandbox class，不只绑定供应商。

选读范围：Filesystem persistence table; Memory persistence table。限制：当前产品文档，不宣称内存快照能保持所有外部连接有效。

[公开原文](https://www.daytona.io/docs/en/persistence/)

<a id="runtime-boundaries-052"></a>

### runtime-boundaries-052 · Run Each Conversation in Its Own Docker Container

作者／组织：OpenHands。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：每会话容器仍 bind mount 宿主 workspace/history/persistence；共用host workspace仍共用可写文件，不因容器隔离而免冲突。idle20分钟stop、下次重建，启动时清理旧容器，历史靠外部mount留存。

选读范围：How Isolation Works; Workspace and Persistence; Configuration Reference。限制：官方配置示例使用latest镜像；生产需记录兼容版本，本文未运行。

[公开原文](https://docs.openhands.dev/openhands/usage/agent-canvas/backend-setup/docker-execution)

<a id="runtime-boundaries-055"></a>

### runtime-boundaries-055 · Tini process lifecycle

作者／组织：Thomas Orozco / Tini。类型：官方文档／规范。版本／日期：v0.19.0。读取日：2026-10-13。

用途：reaping 防僵尸占满PID；默认只转发信号到直接child，-g 才发进程组。PID1/subreaper 与 kill-tree 是两条职责，不能有 --init 就声称所有后代必被取消。

选读范围：Why Tini; Subreaping; Process group killing; Understanding Tini。限制：相关章节静态阅读，未运行测试。

[公开原文](https://github.com/krallin/tini/blob/v0.19.0/README.md)

<a id="runtime-boundaries-056"></a>

### runtime-boundaries-056 · systemd.kill process killing procedure

作者／组织：systemd。类型：官方文档／规范。版本／日期：v259。读取日：2026-10-13。

用途：KillMode=control-group 默认管全cgroup，mixed先main SIGTERM后全组SIGKILL，process仅main会让后台工具逃出生命周期/资源核算。关闭SendSIGKILL可能因残存成员阻止重启；停机状态不等于无资源。

选读范围：KillMode, KillSignal, SendSIGKILL sections。限制：阅读官方 tag 中 KillMode、信号和升级终止机制的文档；未运行跨平台测试。

[公开原文](https://github.com/systemd/systemd/blob/v259/man/systemd.kill.xml)

<a id="runtime-boundaries-057"></a>

### runtime-boundaries-057 · Allow Windows daemon launches with residual job membership

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged / 8b78f4796605bda8e31329537f5fef036e405e66。读取日：2026-10-13。

用途：Windows breakaway可脱内层job却仍留外层，IsProcessInJob非零不足以断言daemon必被杀。修复去掉笼统拒绝，先做suspended breakaway probe再停旧daemon，probe必须terminate+reap。

选读范围：PR body; windows_tests.rs detached_launch_preflight_allows_residual_job。限制：已合并，未核发布tag；回归测试显式证明内外job成员不同。

[公开原文](https://github.com/openai/codex/pull/48157)

<a id="tools-security-022"></a>

### tools-security-022 · anthropics/sandbox-runtime

作者／组织：Anthropic experimental sandbox-runtime maintainers。类型：源码／仓库文档。版本／日期：rolling README retrieved 2026-10-13。读取日：2026-10-13。

用途：运行时读写规则默认不同：读通常开放，写需允许；无设置与设置存在但无效不应混为一谈，后者应退出而非回退。

选读范围：README architecture, filesystem/network settings, control-fd, violation attribution, resolved-address check。限制：rolling main 文档，非固定提交；只读 README 的安全相关前段，未审计实现正确性。

[公开原文](https://github.com/anthropic-experimental/sandbox-runtime)

<a id="tools-security-023"></a>

### tools-security-023 · containers/bubblewrap

作者／组织：bubblewrap maintainers。类型：源码／仓库文档。版本／日期：rolling README retrieved 2026-10-13。读取日：2026-10-13。

用途：bubblewrap 只是构造沙箱的工具，不自带完整安全策略；实际边界由调用者提供的参数、挂载和命名空间决定。

选读范围：README System security, Sandbox security, Sandboxing, Limitations。限制：README 的平台假设需与部署内核能力匹配；非新漏洞发现。

[公开原文](https://github.com/containers/bubblewrap)

<a id="tools-security-026"></a>

### tools-security-026 · Configure the sandboxed Bash tool - Claude Code Docs

作者／组织：Anthropic / Claude Code documentation。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：Bash 沙箱只包围 shell/Monitor 子进程，Read/Edit/WebFetch、MCP server、hooks 等走不同路径；denyRead 不能自动阻断 Read 工具。

选读范围：Sandbox scope/defaults; modes; escape hatch; filesystem rules。限制：文档含当日版本特性；实现与 README 支持平台可能不同，不能把独立 sandbox-runtime 能力等同 Claude Code 产品已支持。

[公开原文](https://code.claude.com/docs/en/sandboxing)

<a id="tools-security-027"></a>

### tools-security-027 · Implementing a secure sandbox for local agents · Cursor

作者／组织：Ani Betts, Yash Gaitonde, Alex Haugland / Cursor。类型：作者／团队实践或研究文章。版本／日期：2026-02-18。读取日：2026-10-13。

用途：沙箱隔离由 OS 原语实现，macOS/Linux/WSL2 的路径不同，统一 API 不代表统一实现约束。

阅读范围：article body。限制：40% 中断下降为厂商生产观察，非可泛化安全测量。

[公开原文](https://cursor.com/blog/agent-sandboxing)

<a id="tools-security-028"></a>

### tools-security-028 · Git commands do not seem to work on modal

作者／组织：Gguinet and klieret / SWE-agent。类型：公开问题讨论。版本／日期：2025-06-12。读取日：2026-10-13。

用途：git show/log 在无正常终端的 Modal 环境触发 pager 等待 RETURN，被 loop 当成执行超时。

选读范围：问题正文与维护者首个回复（所读正文约 1 万字符）。限制：只读正文和首个维护者回复，未单独读取关联 PR。

[公开原文](https://github.com/SWE-agent/SWE-agent/issues/1204)

<a id="tools-security-029"></a>

### tools-security-029 · Linux sandbox panics when project `.codex` is a symlink into writable workspace.

作者／组织：emcd and Codex maintainers。类型：公开问题讨论。版本／日期：2026-05-02; Codex 0.128.0。读取日：2026-10-13。

用途：受保护 .codex 经过工作区可写 symlink 时，sandbox 构造拒绝却以 panic 反馈；命令还没开始就失败，不应当成目标程序错误。

阅读范围：article body。限制：issue 关闭针对 panic 处理，不能据此声称所有 symlink 布局已支持。

[公开原文](https://github.com/openai/codex/issues/20716)

<a id="tools-security-030"></a>

### tools-security-030 · Linux sandbox 0.162: deny_read entries that name the same file through a symlink fail with "Unable to mount source on destination: No such file or directory"

作者／组织：offbrand-games and argszero / openai/codex issue。类型：公开问题讨论。版本／日期：2026-10-09; Codex 0.162.0。读取日：2026-10-13。

用途：同一受限文件经 symlink 两个名字重复挂载 mask 可导致 bwrap 启动失败，按字符串去重不等于按实际文件身份去重。

阅读范围：article body。限制：开放 issue；后续回复的补丁作者明确未在 Linux 真运行测试，修复建议不能作为已验证解决。

[公开原文](https://github.com/openai/codex/issues/52658)

<a id="tools-security-033"></a>

### tools-security-033 · Computer use

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：计算机工具的执行器要维持 session、执行限额和权限；不能只实现一个 exec 函数就认为接入完成。

选读范围：code-execution integration; safety guidance。限制：只读执行集成及安全段落。

[公开原文](https://developers.openai.com/api/docs/guides/tools-computer-use)

<a id="tools-security-034"></a>

### tools-security-034 · Auto-waiting | Playwright

作者／组织：Microsoft / Playwright。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：点击前 actionability 要求唯一元素、可见、稳定、能收到事件且启用；force 会跳过部分检查。

阅读范围：article body。限制：Playwright 的具体检查语义；harness 推论是仍需确认目标语义和执行后状态。

[公开原文](https://playwright.dev/docs/actionability)

<a id="tools-security-044"></a>

### tools-security-044 · Kill shell tool process groups on timeout

作者／组织：luca-ctx and Codex maintainers。类型：公开变更／提案。版本／日期：merged 2025-11-08; a2fdfce02a870773b3b037954b0fad6222020389。读取日：2026-10-13。

用途：只终止 shell 直接子进程会留下孙进程持有 PTY，timeout 已到但 tool 无法返回，agent 永久卡住。

阅读范围：article body。限制：已合并修复历史；文中的1000ms默认值不应转成现在通用建议。

[公开原文](https://github.com/openai/codex/pull/5258)

<a id="tools-security-047"></a>

### tools-security-047 · asyncio timeouts for RemoteRuntime

作者／组织：18jeffreyma / SWE-ReX。类型：公开问题讨论。版本／日期：2025-08-21。读取日：2026-10-13。

用途：重测试负载下控制 webserver 与工具进程争 CPU，远程命令出现 asyncio timeout；用户还发现 HTTP层300秒上限先于长命令超时。

阅读范围：article body。限制：CPU竞争是报告者推测；300秒问题有相关 PR 交叉支撑，不把假设写成已验证根因。

[公开原文](https://github.com/SWE-agent/SWE-ReX/issues/245)

<a id="tools-security-048"></a>

### tools-security-048 · Timeout Increase

作者／组织：jlebensold and dcloud347 / SWE-ReX。类型：公开变更／提案。版本／日期：opened 2025-08-26; still open at retrieval。读取日：2026-10-13。

用途：提案将 HTTP 客户端 timeout 与调用者命令 timeout 关联，避免通信层先断开导致命令结果不可知。

阅读范围：article body。限制：PR open，不宣称方案已合并或验证；与source047是独立issue/PR但同一故障链。

[公开原文](https://github.com/SWE-agent/SWE-ReX/pull/248)

<a id="tools-security-050"></a>

### tools-security-050 · Security Model - gVisor

作者／组织：gVisor maintainers。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：gVisor 限制宿主内核攻击面，但仍允许映射文件和网络操作；沙箱不是安全架构替代品。

阅读范围：article body。限制：通用基础设施只用于解释 agent 任意代码执行的边界，不扩写内核百科。

[公开原文](https://gvisor.dev/docs/architecture_guide/security/)

<a id="tools-security-051"></a>

### tools-security-051 · docs/prod-host-setup.md

作者／组织：Firecracker maintainers / AWS。类型：源码／仓库文档。版本／日期：rolling production guide retrieved 2026-10-13。读取日：2026-10-13。

用途：microVM 也需 jailer 或等价限制、每租户隔离和宿主资源控制；默认不对 guest egress 做过滤。

选读范围：Production host recommendations: serial/log resource limits, jailer, guest egress, tenant separation。限制：主分支生产建议，无固定提交；仅引用与执行loop后果相关控制。

[公开原文](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md)

<a id="tools-security-060"></a>

### tools-security-060 · SWE-ReX local runtime implementation

作者／组织：SWE-agent maintainers。类型：源码／仓库文档。版本／日期：main, accessed 2026-10-13。读取日：2026-10-13。

用途：持久PTY需要独立提示符和退出码协议；交互命令可返回合成exit_code=0，静默提取失败可返回None，消费者不能混同为真实业务成功。

选读范围：src/swerex/runtime/local.py: BashSession._run_normal; LocalRuntime.execute。限制：主分支快照未本地执行；这里只解释可见代码，不宣称发现漏洞或证明所有平台行为。

[公开原文](https://github.com/SWE-agent/SWE-ReX/blob/main/src/swerex/runtime/local.py)

[返回分类目录](#topics)

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

[返回分类目录](#topics)

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

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.29.0 / 7e1643a67322956ac81fc7d0c3f0f9161e2e5482。读取日：2026-10-13。 引用别名：runtime-boundaries-002（本条合计 1 项，各版本复核不另计）。

用途：有限Retry-After超过120秒在_should_retry中拒绝重试，优先于x-should-retry；不能只读退避计算函数声称它会提前重试。数值溢出用超过上限的有限sentinel保留拒绝。

选读范围：_parse_retry_after_header L812-848; _calculate_retry_timeout L861-883; _should_retry L885-927; constants MAX_RETRY_AFTER_DELAY=120。限制：限定 v3.29.0 所列重试分支；静态实现不等于所有请求路径或用户安装版本的运行证明。

已读版本／别名（同一来源）：
- network-errors-015：main as read 2026-10-13; immutable Git blob 883bed6e19b9fd05126affe1e6ced56a309db164；范围：_parse_retry_after_header；_calculate_retry_timeout；_should_retry；SyncAPIClient.request。[该版本原文](https://github.com/openai/openai-python/blob/main/src/openai/_base_client.py)
- runtime-boundaries-002：v3.29.0 / 7e1643a67322956ac81fc7d0c3f0f9161e2e5482；范围：_parse_retry_after_header L812-848; _calculate_retry_timeout L861-883; _should_retry L885-927; constants MAX_RETRY_AFTER_DELAY=120；补充复核，不新增计数。[该版本原文](https://github.com/openai/openai-python/blob/7e1643a67322956ac81fc7d0c3f0f9161e2e5482/src/openai/_base_client.py)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

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

阅读范围：full body and timeline,2026-09-07/25。限制：当前main相关代码另核验于[network-errors-021](#network-errors-021)；跨项目修复状态不可相互推断。

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

作者／组织：LiteLLM maintainers。类型：官方文档／规范。版本／日期：live documentation as read 2026-10-13。读取日：2026-10-13。 引用别名：protocol-audit-025（本条合计 1 项，各版本复核不另计）。

用途：Router可以先在模型组内重试再逐级fallback；外层loop若另有重试，会乘上这一预算。

选读范围：Retries/Timeout/Fallbacks; encrypted reasoning and encrypted_content_affinity; cooldown and fallback model IDs。限制：阅读前18k的重试/超时/cooldown/fallback状态段；加密状态处理是高风险实现断言，仍需固定版本代码和provider文档交叉核查。

已读版本／别名（同一来源）：
- network-errors-043：live documentation as read 2026-10-13；范围：Retries/Timeout/Fallbacks; encrypted reasoning and encrypted_content_affinity; cooldown and fallback model IDs。[该版本原文](https://docs.litellm.ai/docs/proxy/reliability)
- protocol-audit-025：live 2026-10-13；范围：Fallback reasoning 兼容说明；补充复核，不新增计数。[该版本原文](https://docs.litellm.ai/docs/proxy/reliability)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.litellm.ai/docs/proxy/reliability)

<a id="network-errors-044"></a>
<a id="protocol-audit-034"></a>

### network-errors-044 · Provider selection controls

作者／组织：OpenRouter。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。 引用别名：protocol-audit-034（本条合计 1 项，各版本复核不另计）。

用途：require_parameters默认false不保证参数强制生效；data_collection、zdr和only/ignore控制不同边界。

选读范围：Provider selection：require_parameters、data_collection、ZDR 与 only/ignore。限制：Provider routing 旧地址重定向到此页；ZDR 对推理端点的筛选不自动覆盖工具后端，未审计第三方保留政策。

已读版本／别名（同一来源）：
- network-errors-044：live documentation as read 2026-10-13；范围：Provider routing parameters; allow_fallbacks; require_parameters; data_collection; zdr; latency/throughput preferences; max_price。[该版本原文](https://openrouter.ai/docs/features/provider-routing)
- protocol-audit-034：live 2026-10-13；范围：Provider selection：require_parameters、data_collection、ZDR 与 only/ignore；补充复核，不新增计数。[该版本原文](https://openrouter.ai/docs/guides/routing/provider-selection)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

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

作者／组织：OpenAI Agents issue reporters and maintainers。类型：公开问题讨论。版本／日期：openai-agents-python 0.18.1 in report。读取日：2026-10-13。 引用别名：durable-orchestration-056（本条合计 1 项，各版本复核不另计）。

用途：本地SQLiteSession在重试回滚时删除已保存输入，而save-once标志没有复位，最终只留下assistant回复。

阅读范围：Issue body, independent reproducer, save_input-once and rewind analysis, linked PR。限制：全文与独立复现评论已读；关联修复PR #3857，不把本地session问题外推到所有后端。

已读版本／别名（同一来源）：
- durable-orchestration-056：0.18.1; opened/closed2026-07-16 via3857；范围：issue mechanism0.18.1/repro roles; completed via3857；补充复核，不新增计数。[该版本原文](https://github.com/openai/openai-agents-python/issues/3852)
- network-errors-055：openai-agents-python 0.18.1 in report；范围：Issue body, independent reproducer, save_input-once and rewind analysis, linked PR。[该版本原文](https://github.com/openai/openai-agents-python/issues/3852)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

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

### protocol-010 · Stop reasons and fallback

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：live documentation as accessed 2026-10-13。读取日：2026-10-13。

用途：HTTP200仍可能是refusal、max_tokens、model_context_window_exceeded或pause_turn；stop_reason与网络异常须分层。

选读范围：Quick reference; empty end_turn; tool_use; pause_turn; Streaming considerations。限制：实时文档，版本/平台相关；未验证服务端实际行为，不将厂商建议当跨模型定律。

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

[返回分类目录](#topics)

<a id="topic-09"></a>

## 9. 上下文与记忆：下次模型真正看到什么

<a id="loop-context-001"></a>

### loop-context-001 · Effective context engineering for AI agents

作者／组织：Anthropic Applied AI。类型：作者／团队实践或研究文章。版本／日期：2025-09-29。读取日：2026-10-13。

用途：上下文在每次推理前重新策展，累积工具观察并不等于可用工作记忆；长窗能力不是准确性的保证。

阅读范围：Context retrieval and agentic search; Context engineering for long-horizon tasks。限制：作者第一手工程经验；具体模型版本、产品实现和数据不应推广成普遍定律。

[公开原文](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

<a id="loop-context-003"></a>

### loop-context-003 · Context Engineering for AI Agents: Lessons from Building Manus

作者／组织：Yichao 'Peak' Ji / Manus。类型：作者／团队实践或研究文章。版本／日期：2025-07-18。读取日：2026-10-13。

用途：稳定前缀、追加式历史、确定性序列化直接影响缓存；动工具定义可破坏缓存且令旧调用失去定义。

阅读范围：Design Around the KV-Cache; Mask, Don't Remove; Use the File System as Context; Keep the Wrong Stuff In。限制：作者第一手工程经验；具体模型版本、产品实现和数据不应推广成普遍定律。

[公开原文](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)

<a id="loop-context-007"></a>

### loop-context-007 · Handoff (No More Compaction)

作者／组织：Amp。类型：作者／团队实践或研究文章。版本／日期：2025-10-23。读取日：2026-10-13。

用途：因摘要叠摘要有损且鼓励漫长跑题线程，Amp当时去掉压缩；handoff依据下一任务目标抽取上下文，并让用户在新线程检查草稿。

阅读范围：entire article。限制：历史设计；Amp 在 2026 年 5 月的重建中重新采用压缩，见本索引 Amp, Rebuilt。

[公开原文](https://ampcode.com/news/handoff)

<a id="loop-context-009"></a>

### loop-context-009 · Context Management in Amp

作者／组织：Amp。类型：官方文档／规范。版本／日期：2025-11 guide, later warning added。读取日：2026-10-13。

用途：handoff为下一任务抽取信息而非覆盖全部历史；引用线程通过第二模型按问题提取相关信息。

阅读范围：Context in Amp; Edit & Restore; Handoff; Referencing Threads。限制：页首明确此为较早模型时代指南；多模态和推理处理的简化说法不作规范依据。

[公开原文](https://ampcode.com/guides/context-management)

<a id="loop-context-012"></a>

### loop-context-012 · Compaction Reference

作者／组织：Pi maintainers。类型：官方文档／规范。版本／日期：latest fetched 2026-10-13。读取日：2026-10-13。

用途：压缩点必须保留工具调用及结果对应关系，不可在tool result处切；一个用户跨度超预算时分开总结早期前缀。

阅读范围：When It Triggers; Overflow and Length Recovery Ordering; Cut Point Rules; Cumulative File Tracking; Message Serialization。限制：动态文档未锁commit；具体阈值不是跨模型最优参数。

[公开原文](https://pi.dev/docs/latest/compaction)

<a id="loop-context-013"></a>

### loop-context-013 · Amp, Rebuilt

作者／组织：Amp。类型：作者／团队实践或研究文章。版本／日期：2026-05-06, updated through September。读取日：2026-10-13。

用途：Amp重建架构回归自动压缩，90%窗口触发，移除handoff；其理由是新模型更能处理压缩，早期策略需随能力重评。

阅读范围：No More Manual Context Management; Queuing & Steering; What's Gone。限制：厂商产品与经验声明，不推广其取消默认审批的安全判断。

[公开原文](https://ampcode.com/news/neo)

<a id="loop-context-014"></a>

### loop-context-014 · Evaluating Context Compression for AI Agents

作者／组织：Factory Research。类型：作者／团队实践或研究文章。版本／日期：2025-12-16。读取日：2026-10-13。

用途：压缩质量可用事实回忆、产物追踪、续做计划、决策依据四种probe测，而非只测摘要文字相似或压缩率。

阅读范围：Measuring context quality; Three approaches; Results; Methodology details。限制：厂商自测、LLM judge且原始私有数据难独立复现；文中对竞品机制/低熵的解释不作为已证明因果。

[公开原文](https://factory.ai/news/evaluating-compression)

<a id="loop-context-015"></a>

### loop-context-015 · Compressing Context

作者／组织：Theo Luan / Factory。类型：作者／团队实践或研究文章。版本／日期：2025-07-21。读取日：2026-10-13。

用途：触发压缩的高水位与压缩后保留的低水位分开；间隙窄导致频繁摘要与缓存失效，间隙宽更易丢重要细节。

选读范围：Naive Approach; Our Approach; Tuning Our Thresholds; Prompting: What Must Survive。限制：正文机制已读，公式被网页KaTeX错误遮蔽，未据此引用公式。

[公开原文](https://factory.ai/news/compressing-context)

<a id="loop-context-016"></a>

### loop-context-016 · Deferred Context Engine

作者／组织：Factory Research / Shashank Sharma。类型：作者／团队实践或研究文章。版本／日期：2026-05-20。读取日：2026-10-13。

用途：先放简短能力索引，相关能力再加载并在本任务复用；缓存只降低重复计算价格，不移除无关工具对选择的干扰。

阅读范围：Discover / Promote / Reuse; Production results; Fewer input tokens reduce selection noise。限制：生产遥测的估算输入节省，不是随机对照成功率改善；补充Manus早期不动态移除工具的边界。

[公开原文](https://factory.ai/news/deferred-context-engine)

<a id="loop-context-017"></a>

### loop-context-017 · The Context Window Problem: Scaling Agents Beyond Token Limits

作者／组织：Varin Nair / Factory。类型：作者／团队实践或研究文章。版本／日期：2025-08-25。读取日：2026-10-13。

用途：代码检索不仅相似片段，还需调用/依赖关系多跳探索；仓库概览→候选检索→定点文件读取是分层输入策略。

阅读范围：Critical context; Naive vector retrieval; Factory's Context Stack。限制：厂商产品架构描述，收益多为定性且当时窗口大小已历史化。

[公开原文](https://factory.ai/news/context-window-problem)

<a id="loop-context-019"></a>

### loop-context-019 · OpenCode V2 Compaction

作者／组织：OpenCode。类型：官方文档／规范。版本／日期：V2 read 2026-10-13。读取日：2026-10-13。

用途：压缩接受请求不等于完成，要观察compaction事件；请求在安全点运行，多次pending请求合并。

阅读范围：Manual; Providers; Limits。限制：只适用V2，参数与V1不同。

[公开原文](https://opencode.ai/v2/docs/compaction/)

<a id="loop-context-022"></a>

### loop-context-022 · Lost in the Middle: How Language Models Use Long Contexts

作者／组织：Nelson F. Liu et al.。类型：研究论文。版本／日期：2023 / TACL 2024。读取日：2026-10-13。

用途：控制相关证据位置和干扰文档数，早期多模型出现中间位置性能较差；宣称支持长窗不能替代位置鲁棒性评估。

选读范围：Abstract; Sections 1–4.2 (read through query-aware comparison)。限制：历史模型GPT-3.5/Claude1.3等，不能把U形曲线当所有2026模型必有规律。

[公开原文](https://arxiv.org/html/2307.03172)

<a id="loop-context-023"></a>

### loop-context-023 · Context Rot: How Increasing Input Tokens Impacts LLM Performance

作者／组织：Kelly Hong, Anton Troynikov, Jeff Huber / Chroma。类型：研究论文。版本／日期：2025-07-14。读取日：2026-10-13。

用途：区分无关内容与主题相似的干扰项，保持题目难度固定只增加长度；语义模糊和干扰会放大长窗退化。

选读范围：Introduction; Contributions; NIAH extensions; Needle-Question Similarity; Impact of Distractors; Limitations; Appendix judge alignment。限制：已读上述实质章节；未逐个阅读交互图表所有点，实验不覆盖真实复杂agent任务。

[公开原文](https://research.trychroma.com/context-rot)

<a id="loop-context-024"></a>

### loop-context-024 · Local compaction v2 retains unbounded input_image payloads, causing repeated auto-compaction

作者／组织：snrui and issue participants。类型：公开问题讨论。版本／日期：2026-07, Codex 0.144.2/0.145.0。读取日：2026-10-13。

用途：报告指向text-only保留预算将image/audio计零，压缩后仍近阈值，短消息再次触发压缩；存储重复base64还放大磁盘。

选读范围：Original report; July 19 and July 23 reproductions, pinned code pointers。限制：读到原始报告和前三条详细证据评论；后续截断。报告仍open，不认定当前版本仍存在同根因。

[公开原文](https://github.com/openai/codex/issues/33493)

<a id="loop-context-026"></a>

### loop-context-026 · Active Goal is lost after automatic context compaction

作者／组织：yeatdev and issue participants。类型：公开问题讨论。版本／日期：2026-09–10, versions specified in report。读取日：2026-10-13。

用途：压缩后已完成旧问题可能重新取得优先级；有评论记录get_goal返回正确active目标，但最终回答仍偏向旧问题。

阅读范围：Original report; October 10/12 sanitized trace comments。限制：加密payload不可检查，报告不证明根因是目标缺失；历史核验案例而非最小确定复现。

[公开原文](https://github.com/openai/codex/issues/49022)

<a id="loop-context-027"></a>

### loop-context-027 · durable: calibrate compaction retention to reported context usage

作者／组织：neavo / Pi issue。类型：公开问题讨论。版本／日期：2026-10-07。读取日：2026-10-13。

用途：CJK文本token/字符比例差异导致provider计费量已超阈值、字符估算却认为没内容可截；两套预算不一致让压缩跳过直到截断。

阅读范围：Why; How; synthetic reproduction。限制：合成CJK/faux provider，尚未独立复现或证明修复合并。

[公开原文](https://github.com/earendil-works/pi/issues/10583)

<a id="loop-context-028"></a>

### loop-context-028 · Codex App entered an infinite auto-compaction loop

作者／组织：ewzxyh and issue participants。类型：公开问题讨论。版本／日期：2026-07-07, App 26.623.141536。读取日：2026-10-13。

用途：用户报告数小时重复计划→压缩→相似计划且无实质进展，展示没有no-progress停止条件的成本风险。

阅读范围：Original report; timeline。限制：仅用户报告，不把约30%配额或其根因猜测当普遍统计；与 [loop-context-024](#loop-context-024)不假设同一根因。

[公开原文](https://github.com/openai/codex/issues/31351)

<a id="loop-context-029"></a>

### loop-context-029 · LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory

作者／组织：Di Wu et al.。类型：研究论文。版本／日期：ICLR 2025。读取日：2026-10-13。

用途：长期记忆应测提取、跨会话综合、时间推理、知识更新、拒答五能力；只测能否召回旧事实不足。

选读范围：Sections 1,3,5.1–5.5。限制：读到主要方法和实验；未逐一阅读附录/所有模型表，数据为模拟并人审，不能替代真实隐私记忆评测。

[公开原文](https://arxiv.org/html/2410.10813)

<a id="loop-context-030"></a>

### loop-context-030 · Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo)

作者／组织：Adyasha Maharana et al.。类型：研究论文。版本／日期：2024。读取日：2026-10-13。

用途：记忆评估覆盖多跳、时间、不可回答问题与事件摘要；生成长对话需人工修正长期不一致。

选读范围：Abstract; Sections 3–5 incl benchmark and baseline tables。限制：主方法与实验设置/表已读，未读全部结果解析和附录；人设对话不是所有agent工作流。

[公开原文](https://arxiv.org/html/2402.17753)

<a id="loop-context-031"></a>

### loop-context-031 · MemGPT: Towards LLMs as Operating Systems

作者／组织：Charles Packer et al.。类型：研究论文。版本／日期：2023/2024。读取日：2026-10-13。

用途：主上下文与外部存储显式区分；外部数据必须用工具调回才会参与推理，不是模型天然知道整个数据库。

选读范围：Sections 1–2.4。限制：主要架构/控制流已读；未将早期实验分数外推至现代模型。

[公开原文](https://arxiv.org/html/2310.08560)

<a id="loop-context-032"></a>

### loop-context-032 · Sleep-time Compute

作者／组织：Letta。类型：作者／团队实践或研究文章。版本／日期：2025-04-21。读取日：2026-10-13。

用途：把主交互与记忆重组分给不同agent可将延迟移到空闲期；主agent不再直接改核心记忆。

阅读范围：Full body。限制：机制与产品原型描述，不把异步计算称免费，也不外推数学评测到所有任务。

[公开原文](https://www.letta.com/blog/sleep-time-compute/)

<a id="loop-context-033"></a>

### loop-context-033 · Memory Blocks: The Key to Agentic Context Management

作者／组织：Letta。类型：作者／团队实践或研究文章。版本／日期：2025-05-14。读取日：2026-10-13。

用途：memory block含label/value/size limit/description，可单独持久化并在请求时编译成prompt；支持只读块。

阅读范围：Full body。限制：文章未定义完整冲突解决协议；只把block作为上下文单元解释。

[公开原文](https://www.letta.com/blog/memory-blocks/)

<a id="loop-context-034"></a>

### loop-context-034 · Stateful Agents: The Missing Link in LLM Intelligence

作者／组织：Letta。类型：作者／团队实践或研究文章。版本／日期：2025-02-06。读取日：2026-10-13。

用途：区分持久状态的累积与每次有限窗口的编译；系统指令、可编辑记忆、外存metadata、近期消息和历史摘要可分别管理。

阅读范围：Full body。限制：营销性未来判断不采纳；不能称唯一或首个框架。

[公开原文](https://www.letta.com/blog/stateful-agents/)

<a id="loop-context-035"></a>

### loop-context-035 · Introducing Context Repositories: Git-based Memory for Coding Agents

作者／组织：Letta。类型：作者／团队实践或研究文章。版本／日期：2026-02-12。读取日：2026-10-13。

用途：记忆目录树/description常驻、system目录全文常驻，其余按需读；文件布局是选择性上下文索引。

阅读范围：Full body。限制：产品设计声明；合并成功不证明记忆事实一致，这一边界是工程推论。

[公开原文](https://www.letta.com/blog/context-repositories/)

<a id="loop-context-040"></a>

### loop-context-040 · Agentic Coding Things That Didn’t Work

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2025-07-30。读取日：2026-10-13。

用途：过多slash命令和静态自动化不比直接上下文好；作者只保留重复使用且实测有益的流程。

阅读范围：Full body。限制：自述失败，不代表所有hooks或子agent无用；旧Claude Code行为已变化。

[公开原文](https://lucumr.pocoo.org/2025/7/30/things-that-didnt-work/)

<a id="loop-context-041"></a>

### loop-context-041 · Agent Design Is Still Hard

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2025-11-21。读取日：2026-10-13。

用途：在工具返回边界补充目标与环境变化，能保持稳定系统前缀且让模型知道状态已变。

选读范围：SDK selection; Caching; Reinforcement; Isolate Failures; Sub Agents; Output Tool; Testing。限制：作者未确诊Vercel历史损坏根因；缓存策略和模型偏好属当时经验。

[公开原文](https://lucumr.pocoo.org/2025/11/21/agents-are-hard/)

<a id="loop-context-043"></a>

### loop-context-043 · Advanced Context Engineering for Coding Agents

作者／组织：Dex / HumanLayer。类型：作者／团队实践或研究文章。版本／日期：2025-08-29。读取日：2026-10-13。

用途：研究→计划→实现用持久产物交接，重点是纠正/完整/大小/轨迹，不是追求最短prompt。

选读范围：Intro; context engineering; research/plan/implement; This is not Magic; Eggs on Faces。限制：40–60%为团队启发式，没有普遍阈值证据；产量/时间是自述。

[公开原文](https://www.humanlayer.dev/blog/advanced-context-engineering)

<a id="loop-context-045"></a>

### loop-context-045 · Long-Context Isn't the Answer

作者／组织：Kyle / HumanLayer。类型：作者／团队实践或研究文章。版本／日期：2026-03-23。读取日：2026-10-13。

用途：团队自述1M窗口在其复杂代码工作中未改善指令遵守，仍采用隔离与精简；体现可接收长度和有效任务性能不同。

阅读范围：Full body。限制：对参数规模/YaRN/指令预算的解释多为推测，不作为已验证Anthropic内部机制；与Amp经验适用情境不同。

[公开原文](https://www.humanlayer.dev/blog/long-context-isnt-the-answer)

<a id="loop-context-046"></a>

### loop-context-046 · Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory

作者／组织：Prateek Chhikara et al.。类型：研究论文。版本／日期：2025。读取日：2026-10-13。

用途：新交互抽候选事实，再检索相似记忆选择ADD/UPDATE/DELETE/NOOP；记忆写入本身也是有错误可能的模型决策。

选读范围：Abstract; Sections 2.1–2.2,5。限制：厂商评测不用于排名；删除记忆未证明删除原始事件、摘要、缓存等所有副本。

[公开原文](https://arxiv.org/html/2504.19413)

<a id="loop-context-047"></a>

### loop-context-047 · Zep: A Temporal Knowledge Graph Architecture for Agent Memory

作者／组织：Preston Rasmussen et al.。类型：研究论文。版本／日期：2025。读取日：2026-10-13。

用途：原始episode和衍生实体/事实分层，保留溯源；语义推断与原始内容不是同等权威。

选读范围：Sections 2,2.2,2.3。限制：LLM仍决定实体去重/矛盾，时态结构不能自动确保事实正确；作者新信息优先策略有来源权威边界。

[公开原文](https://arxiv.org/html/2501.13956)

<a id="loop-context-048"></a>

### loop-context-048 · A-Mem: Agentic Memory for LLM Agents

作者／组织：Wujiang Xu et al.。类型：研究论文。版本／日期：2025。读取日：2026-10-13。

用途：原始交互、时间、关键词、标签、上下文描述和链接组成note；新记忆可触发旧note元数据重写。

选读范围：Sections 3.1–3.4,6。限制：传播错误是机制风险推论，论文并未量化所有污染场景；仅文本任务。

[公开原文](https://arxiv.org/html/2502.12110)

<a id="loop-context-049"></a>

### loop-context-049 · Recursive Language Models

作者／组织：Alex L. Zhang, Tim Kraska, Omar Khattab。类型：研究论文。版本／日期：2025/2026 current revision。读取日：2026-10-13。

用途：长prompt放外部REPL变量，root仅看metadata；代码可对片段递归调用并把中间结果存在变量，避免每个结果全部进入root窗口。

选读范围：Section 2; Section7; Appendix B。限制：此为推理scaffold研究，非无限可靠agent；主评测与开放长期项目不同。

[公开原文](https://arxiv.org/html/2512.24601)

<a id="loop-context-051"></a>

### loop-context-051 · Building agents with the Claude Agent SDK

作者／组织：Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-09-29。读取日：2026-10-13。

用途：gather context→act→verify循环要求可测反馈；规则/lint与视觉渲染各查不同错误。

选读范围：Building your loop; Gather; Take action; Verify; Testing。限制：已读全文核心，未计页尾其他文章；canonical迁移至claude.com/blog同名页。

[公开原文](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

<a id="loop-context-053"></a>

### loop-context-053 · Codex compact_remote_v2.rs at 0fb559f

作者／组织：OpenAI Codex maintainers。类型：源码／仓库文档。版本／日期：0fb559f0f6e231a88ac02ea002d3ecd248e2b515。读取日：2026-10-13。

用途：已直接核验message_text_token_count对InputImage/InputAudio计零、truncate_message_text_to_token_budget保留二者，支持024所述预算口径缺陷。

选读范围：RETAINED_MESSAGE_TOKEN_BUDGET; truncate_retained_messages_for_remote_compaction; message_text_token_count; truncate_message_text_to_token_budget。限制：固定历史commit证据，不声称现版仍未修；未运行复现。

[公开原文](https://github.com/openai/codex/blob/0fb559f0f6e231a88ac02ea002d3ecd248e2b515/codex-rs/core/src/compact_remote_v2.rs)

<a id="loop-context-055"></a>

### loop-context-055 · From Recall to Forgetting: Benchmarking Long-Term Memory for Personalized Agents

作者／组织：Md Nayem Uddin et al.。类型：研究论文。版本／日期：ACL Findings 2026。读取日：2026-10-13。

用途：Memora用显式ADD/UPDATE/DELETE轨迹建ground truth，并同时测有效信息出现与失效信息不得出现。

选读范围：Abstract; Sections3,4,6,7。限制：模拟压力测试、模型judge；遗忘为回答不使用失效事实，不等同后台物理擦除。

[公开原文](https://aclanthology.org/2026.findings-acl.1337.pdf)

<a id="loop-context-056"></a>

### loop-context-056 · Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects

作者／组织：Chris Latimer et al.。类型：研究论文。版本／日期：2025-12, current revision。读取日：2026-10-13。

用途：将世界事实、agent经历、意见、综合观察分四类，避免把自行推断作为原始证据。

选读范围：Abstract; Section3.1–3.4。限制：本文架构用人类认知隐喻，不意味模型有主观体验；未凭abstract分数下排名结论。

[公开原文](https://arxiv.org/html/2512.12818)

<a id="loop-context-058"></a>

### loop-context-058 · autoregressive queens of failure

作者／组织：Geoffrey Huntley。类型：作者／团队实践或研究文章。版本／日期：2025-04-22。读取日：2026-10-13。

用途：混合无关任务的历史会影响后续生成，作者建议聚焦线程并在明显漂移时重新开始。

阅读范围：Full body。限制：文中不能free上下文和一旦错就无救是夸张/历史工具约束；现代context editing构成反例，不作字面事实。

[公开原文](https://ghuntley.com/gutter/)

<a id="loop-context-060"></a>

### loop-context-060 · How Claude remembers your project

作者／组织：Anthropic Claude Code。类型：官方文档／规范。版本／日期：current, mentions v2.1.280。读取日：2026-10-13。

用途：CLAUDE.md/auto memory是模型context而非强制配置；必须执行的禁止不能只靠记忆文件。

选读范围：Opening comparison; When to add; Auto memory; Storage; How it works; Audit。限制：动态产品细节按版本复核；不把文件modified时间等同事实发生或验证时间。

[公开原文](https://code.claude.com/docs/en/memory)

<a id="loop-context-061"></a>

### loop-context-061 · Short-term memory

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current read 2026-10-13。读取日：2026-10-13。

用途：thread级状态持久化与向模型裁剪输入不同；RemoveMessage依赖add_messages reducer语义。

选读范围：Overview; Trim; Delete; Summarize; Access memory。限制：删除graph当前state不自动证明所有checkpoint/日志副本已物理抹除。

[公开原文](https://docs.langchain.com/oss/python/langchain/short-term-memory)

<a id="loop-context-062"></a>

### loop-context-062 · Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?

作者／组织：Thibaud Gloaguen et al.。类型：研究论文。版本／日期：2026 current revision。读取日：2026-10-13。

用途：在SWE-bench Lite与CTXbench对比无文件、自动生成、人工维护context，整体未见显著任务成功率提升而调用步骤/成本增加。

选读范围：Abstract; Section4.1–4.3 incl significance tests。限制：每agent单采样、Python任务/特定模型；不能将平均无显著改善写成必然降低成功率，也不覆盖非标准私有流程价值。

[公开原文](https://arxiv.org/html/2602.11988)

<a id="loop-context-063"></a>

### loop-context-063 · LLMs Get Lost In Multi-Turn Conversation

作者／组织：Philippe Laban et al.。类型：研究论文。版本／日期：2025-05 current revision。读取日：2026-10-13。

用途：把同一任务逐步揭示时，模型早期自行假设并过早给完整解，随后受旧答案锚定；多轮问题不只是容量耗尽。

选读范围：Abstract; Section6.2–6.3;7.1;9。限制：合成sharded英文文本分析任务，作者明确非自然对话；摘要与图表数字不一致，避免未核验精确泛化百分比。

[公开原文](https://arxiv.org/html/2505.06120)

<a id="practitioner-lessons-007"></a>

### practitioner-lessons-007 · Background Coding Agents: Context Engineering (Honk, Part 2)

作者／组织：Max Charas; Marc Bruggmann / Spotify。类型：作者／团队实践或研究文章。版本／日期：2025-11-24。读取日：2026-10-13。

用途：事实：自制loop要求预先列文件、每session十turn且最多三次retry；复杂跨文件任务耗尽turn和上下文，转向Claude Code。

阅读范围：Rolling our own agentic loop; The right tools for the job。限制：其静态上下文选择适合可预定义迁移；后续Part4明确报告它限制复杂迁移，不能当所有agent的最优解。

[公开原文](https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2)

<a id="practitioner-lessons-009"></a>

### practitioner-lessons-009 · Background Coding Agents: Downstream Consumer Dataset Migrations (Honk, Part 4)

作者／组织：Devon Edwards Joseph / Spotify。类型：作者／团队实践或研究文章。版本／日期：2026-04-22。读取日：2026-10-13。

用途：事实：无外部工具/skills的受限agent必须用完整字段映射；Scio变化过多导致团队放弃该部分自动化。

阅读范围：With Honk, context is key; What did we learn。限制：具体迁移经验，不代表所有Scala或SQL任务；不能把无测试的成功PR数量当功能正确证据。

[公开原文](https://engineering.atspotify.com/2026/4/background-coding-agents-dataset-migrations-honk-part-4)

<a id="practitioner-lessons-015"></a>

### practitioner-lessons-015 · Warp scores 75.8% on SWE-bench Verified

作者／组织：Suraj Gupta; Daniel Peng / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-09-01。读取日：2026-10-13。

用途：事实：编辑结果从整文件改为修改区±k行；摘要由同一模型生成并确定性保留TODO/规则，最近一轮维持连续性。

阅读范围：Maintaining task list; Improving longer conversations; file editing。限制：作者宣称同产品能力不等于同产品默认采样预算；摘要更改当时仍待上线。

[公开原文](https://www.warp.dev/blog/swe-bench-verified-update)

<a id="practitioner-lessons-033"></a>

### practitioner-lessons-033 · Building Shared Memory for AI Agents in Notion

作者／组织：Hesham Salman / Notion。类型：作者／团队实践或研究文章。版本／日期：2026-08-18。读取日：2026-10-13。

用途：事实：Lore共享记忆有默认事实过期，supersedes/scoped/conflicts_with关系与孤儿/重复诊断，区分经验与可从代码重得信息。

阅读范围：Memory has to stay clean; What we measured。限制：不能把seeded实验收益直接套到自然累积memory；memory本身仍可能伤害，权限与来源需独立设计。

[公开原文](https://www.notion.com/blog/building-shared-memory-for-ai-agents-in-notion)

<a id="practitioner-lessons-034"></a>

### practitioner-lessons-034 · Building Deep Dive: Infrastructure for AI Agents That Actually Go Deep

作者／组织：Dust Team。类型：作者／团队实践或研究文章。版本／日期：2025-10-29。读取日：2026-10-13。

用途：事实：日志中agent虚构文件路径促成合成filesystem，导航与search并用；toolset动态发现，主agent协调最多六worker且用Temporal承载。

阅读范围：1 filesystem; 4 coordination; 5 reasoning; 6 context; 7 handoff。限制：正文native reasoning收益是团队经验，必须遵守每provider实际reasoning回传契约；共享继承指令需防权限提升。

[公开原文](https://dust.tt/blog/building-deep-dive-infrastructure-for-ai-agents-that-actually-go-deep)

<a id="practitioner-lessons-035"></a>

### practitioner-lessons-035 · Agent Memory: Building persistence into AI collaboration

作者／组织：Dust Team。类型：作者／团队实践或研究文章。版本／日期：2025-08-14。读取日：2026-10-13。

用途：设计事实：记忆实现为opt-in工具、按用户隔离并可检查，而非所有agent默认开启。

阅读范围：Introducing Agent Memory; Why we built memory as a tool。限制：偏发布说明，保留其具体设计分叉，不采纳“永远记住”或“完美连续性”等宣传；未公开质量数据。

[公开原文](https://dust.tt/blog/agent-memory-building-persistence-into-ai-collaboration)

<a id="practitioner-lessons-039"></a>

### practitioner-lessons-039 · Speed Matters: How Browser Use Achieves the Fastest Agent Execution

作者／组织：Gregor Zunic / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2025-10-09。读取日：2026-10-13。

用途：事实：浏览器状态会在agent动作之外变化；该实现把新DOM状态放在稳定对话前缀之后，按需截图，并让单独提取调用把长页压成目标信息。

阅读范围：Browser state; screenshots; evaluation。限制：全文；自报速度和分数依赖browser-use 0.8.0、模型及修改后的judge，不可直接与未改judge的数字横比。

[公开原文](https://browser-use.com/posts/speed-matters)

<a id="practitioner-lessons-053"></a>

### practitioner-lessons-053 · Agent 上下文工程：从开源实现到 JSONL Context Agent | Levon's Blog

作者／组织：Levon / unix2dos。类型：作者／团队实践或研究文章。版本／日期：2026-08-27 updated 2026-09-03。读取日：2026-10-13。

用途：事实：作者自己的JSONL实现区分原始artifact、transcript、compaction entry和实际PromptView，压缩后重建视图避免旧内存历史继续发送。

阅读范围：706-line implementation; PromptView; compaction chain。限制：全文；只采作者自实现机制，对OpenClaw/Pi/Hermes版本比较为二手内容不作权威断言。

[公开原文](https://www.liuvv.com/p/412550b7.html)

<a id="practitioner-lessons-069"></a>

### practitioner-lessons-069 · Building Ask DoorDash (Part 2): Intelligence - DoorDash

作者／组织：Zhucheng Zhan, Raghav Saboo, Heather Song, Fan Xia, Xiaochang Miao / DoorDash。类型：作者／团队实践或研究文章。版本／日期：2026-06-18。读取日：2026-10-13。

用途：事实：长期行为推断、即时session线索和用户明确陈述分层；按任务/namespace/新鲜度选择记忆，先scan目录再按需读取内容。

阅读范围：Partitioning; scan before read; extraction; forgetting。限制：全文分两次读；namespace划分本身不是完整授权证明；prompt提取规则不保证永不误存；7天生产对比不明确随机实验，不能据此宣称因果收益；embedding无需重建的泛化说法不采用。

[公开原文](https://careersatdoordash.com/blog/building-ask-doordash-part-two-intelligence/)

<a id="practitioner-lessons-074"></a>

### practitioner-lessons-074 · Building an agent harness in the open: six months of lessons — Forgeplan Blog

作者／组织：Eli Rum / ForgePlan。类型：作者／团队实践或研究文章。版本／日期：2026-04-15; body includes 2026-05-08 update。读取日：2026-10-13。

用途：事实：并行agent一个读LanceDB一个读markdown导致双真相；作者改markdown权威、数据库派生，清除绕过文件层的32处调用并以可见性及回归测试约束。

阅读范围：ADR-003; PROB-060; PROB-034; hint contract。限制：完整正文分段读；个人项目，机制未运行验证；可靠性分数不等于真实正确率；不采其零token记忆、生成文档绝不漂移、自评必然失败等过强说法。

[公开原文](https://forgeplan.dev/blog/building-an-agent-harness/)

<a id="protocol-052"></a>
<a id="protocol-audit-003"></a>

### protocol-052 · Mid-conversation system messages and tool changes

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current docs; inline tool definitions beta 2026-09-15。读取日：2026-10-13。 引用别名：protocol-audit-003（本条合计 1 项，各版本复核不另计）。

用途：中途system有明确可插入位置，不能放在tool_use与其tool_result之间，连续system按一组检查位置。

选读范围：Definitions; initial tool-change beta discussion; When to use; Limitations; Turn-scoped sections。限制：未逐行读全页中间示例；功能/模型/部署支持范围需钉版本，不作跨厂商推荐。

已读版本／别名（同一来源）：
- protocol-052：current docs; inline tool definitions beta 2026-09-15；范围：Definitions; initial tool-change beta discussion; When to use; Limitations; Turn-scoped sections。[该版本原文](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)
- protocol-audit-003：live 2026-10-13；范围：Mid-conversation system messages：中途系统消息、工具定义与前缀规则；补充复核，不新增计数。[该版本原文](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)

<a id="protocol-audit-002"></a>

### protocol-audit-002 · Compaction and preserved thinking

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：compact-2026-09-04 beta。读取日：2026-10-13。

用途：on-demand签名摘要可使保留尾部thinking继续有效，但每次压缩的模型、相邻消息role边界、system和非deferred tools必须满足条件。

选读范围：Compaction and preserved thinking：压缩块及受保护推理的关系。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。

[公开原文](https://platform.claude.com/docs/en/build-with-claude/compaction-thinking-blocks)

[返回分类目录](#topics)

<a id="topic-10"></a>

## 10. 持久化与恢复：进程回来后，任务怎样继续

<a id="boundary-closure-007"></a>

### boundary-closure-007 · Restate TypeScript durable steps

作者／组织：Restate。类型：官方文档／规范。版本／日期：current TypeScript documentation, accessed 2026-10-13。读取日：2026-10-13。

用途：ctx.run 保存操作返回值到 execution log，重放使用记录；失败按策略重试，除非配置停止或 TerminalError。

选读范围：Run；Serialization；Error handling；deterministic UUID。限制：读 Run、Serialization、Error handling、deterministic UUID；把多操作拆为独立边界是由接口推出的设计建议，不证明单步外部成功与结果落盘之间无窗口。

[公开原文](https://docs.restate.dev/develop/ts/durable-steps)

<a id="boundary-closure-008"></a>

### boundary-closure-008 · Inngest step.run(): execute a step

作者／组织：Inngest。类型：官方文档／规范。版本／日期：TypeScript SDK v4 reference。读取日：2026-10-13。

用途：每次 step.run 有独立重试计数；step ID 用来记忆步骤状态，返回值以 JSON 序列化。

选读范围：参数；并行例子；Retries；Return values。限制：读参数、并行例子、Retries、Return values；独立重试不等于外部 exactly-once，工具内部未落盘子动作仍可能重做。

[公开原文](https://www.inngest.com/docs/reference/typescript/v4/functions/step-run)

<a id="boundary-closure-009"></a>

### boundary-closure-009 · Transactional outbox pattern, including sample code

作者／组织：AWS。类型：官方文档／规范。版本／日期：current guidance, accessed 2026-10-13。读取日：2026-10-13。

用途：业务记录与待发事件在同一数据库事务提交，另一个派发器发送；派发失败无需重做业务记录，重复通知仍须处理。

选读范围：Intent–Issues；outbox implementation；sample code。限制：读 Intent–Issues、outbox implementation、sample code；仅指出页面代码片段的契约缺口，不指控完整仓库或生产系统已丢消息；FIFO 说法不泛化为端到端 exactly-once。

[公开原文](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

<a id="boundary-closure-010"></a>

### boundary-closure-010 · NServiceBus Outbox processing and dispatch recovery

作者／组织：Particular Software。类型：官方文档／规范。版本／日期：NServiceBus core 9 documentation。读取日：2026-10-13。

用途：Phase 1 在事务中执行业务并保存待发消息；重投查到既有记录便跳过 handler，进入 Phase 2 派发。

选读范围：How it works；transaction scope；dispatch errors。限制：读 How it works、transaction scope、dispatch errors；不参加事务的邮件/文件系统操作不在保证内；失败进入 error queue 后仍需恢复触发，不是无限自动成功。

[公开原文](https://docs.particular.net/nservicebus/outbox/?version=core_9)

<a id="durable-orchestration-001"></a>

### durable-orchestration-001 · Scaling Managed Agents: Decoupling the brain from the hands

作者／组织：Lance Martin, Gabe Cemaj, Michael Cohen / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-04-08。读取日：2026-10-13。

用途：会话 append-only 日志、harness 和执行 sandbox 解耦后可独立恢复，容器死亡可作为工具错误处理，harness 通过 session 日志重启。

阅读范围：文章中会话日志、harness 与执行沙箱解耦，以及按需启动和首 token 延迟的段落。限制：供应商生产经验；未给 exactly-once 提交协议，不可据此承诺副作用精确一次

[公开原文](https://www.anthropic.com/engineering/managed-agents)

<a id="durable-orchestration-005"></a>

### durable-orchestration-005 · Persistence

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed 2026-10-13。读取日：2026-10-13。

用途：checkpointer 保存 thread-scoped graph state，store 保存跨 thread 应用数据，二者不能互换。

阅读范围：Checkpointer、thread-scoped state 与跨 thread store；内存保存器和保留策略的说明。限制：当前文档可变；durable-execution旧URL重定向至此，只计一次

[公开原文](https://docs.langchain.com/oss/python/langgraph/persistence)

<a id="durable-orchestration-006"></a>

### durable-orchestration-006 · Checkpointers

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed 2026-10-13; DeltaChannel &gt;=1.2 beta。读取日：2026-10-13。

用途：完整 checkpoint 在 super-step 边界提交，pending writes 保存同一步内已成功节点输出，恢复失败兄弟时无需重跑成功者。

选读范围：核心 checkpoint 概念、pending writes、恢复、耐久模式与 time travel；未逐行审读自定义 saver。限制：读取核心概念/恢复/耐久模式，未逐行审读自定义 saver 代码

[公开原文](https://docs.langchain.com/oss/python/langgraph/checkpointers)

<a id="durable-orchestration-008"></a>

### durable-orchestration-008 · Resuming one of two parallel interrupts inside a subgraph re-runs a sibling node that already completed #9106

作者／组织：Connor Imes and LangGraph contributors。类型：公开问题讨论。版本／日期：2026-09-29; reproductions 1.2.10/1.2.12 and main 2d942085。读取日：2026-10-13。

用途：嵌套图中逐个恢复两个审批，可能已完成的A副作用执行两遍，但最终graph state仍显示A/B各一次；仅断言最终状态会漏掉外部重复动作。

选读范围：问题正文、嵌套子图复现、重复副作用计数与 replay 判定的相关讨论。限制：公开issue及复现，未在独立复跑；当前仍open，候选PR未合并，评论有AI辅助内容，不能写成维护者已保证修复

[公开原文](https://github.com/langchain-ai/langgraph/issues/9106)

<a id="durable-orchestration-009"></a>

### durable-orchestration-009 · Scalar resume is accepted for multiple interrupts in one subgraph task #8579

作者／组织：DongBo / LangGraph contributors。类型：公开问题讨论。版本／日期：2026-08-09; langgraph1.2.10 main d56666f; closed2026-10-02。读取日：2026-10-13。

用途：同一个父任务pending write内含多个子interrupt时，旧逻辑只数首个ID，接受含糊scalar响应并按内部执行顺序投递到某一分支。

阅读范围：问题正文、多个 interrupt 的 scalar resume 复现及关闭前后的相关讨论。限制：issue已于Oct2关闭，最终教程应描述版本案例而非宣称所有当前版本仍有bug；尚未核验发布版本

[公开原文](https://github.com/langchain-ai/langgraph/issues/8579)

<a id="durable-orchestration-010"></a>

### durable-orchestration-010 · Resuming after interrupt doesn't reuse prior task outputs when interrupt is in subgraph #6792

作者／组织：venkatesh-sivaraman and LangGraph users。类型：公开问题讨论。版本／日期：2026-02-12; langgraph1.0.8。读取日：2026-10-13。

用途：同样entrypoint加一层父图包装后，interrupt前任务输出不复用，表现为步骤重跑及中断重复。

选读范围：问题正文与早期复现评论：entrypoint 外包父图后任务输出不复用。限制：已阅读正文和早期复现评论，未把未经证实评论中的根因推断当事实；与9106有关联但提供不同版本及API拓扑

[公开原文](https://github.com/langchain-ai/langgraph/issues/6792)

<a id="durable-orchestration-011"></a>

### durable-orchestration-011 · Temporal Workflow

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：恢复通过从头运行Workflow代码并读取历史事件重建状态，不是恢复内存快照；外部I/O和LLM放入Activity以记录返回值。

阅读范围：Workflow 恢复、事件历史、确定性与 Activity 返回值的说明。限制：Activity结果被记录后的replay复用不代表Activity尝试精确一次

[公开原文](https://docs.temporal.io/workflows)

<a id="durable-orchestration-012"></a>

### durable-orchestration-012 · Of course you can build dynamic AI agents with Temporal

作者／组织：Mason Egger, Steve Androulakis / Temporal。类型：作者／团队实践或研究文章。版本／日期：2025-11-12。读取日：2026-10-13。

用途：LLM生成下一步/计划由Activity记录，Workflow可依结果动态选择工具或子工作流；确定性不等于预定DAG。

阅读范围：文章中动态计划、Activity 记录模型决策及崩溃后恢复的讨论。限制：供应商宣传文，“没有Temporal只能从头开始”忽略其他持久化方案；工具副作用仍需幂等

[公开原文](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal)

<a id="durable-orchestration-014"></a>

### durable-orchestration-014 · Continue-As-New

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Continue-As-New把必要状态作为参数传入新执行，同Workflow ID但新Run ID与新history。

阅读范围：全文 What is / When to Continue-As-New。限制：run身份变化需要与外部关联ID区分，不能当无状态重启

[公开原文](https://docs.temporal.io/workflow-execution/continue-as-new)

<a id="durable-orchestration-015"></a>

### durable-orchestration-015 · Activities

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Activity是可非确定性外部操作，但失败会从初始状态重试，须幂等；heartbeat detail可供下次尝试自行接续。

阅读范围：正文 Activities定义、retry/heartbeat段。限制：仅Activity概念层；外部effect提交协议需应用提供

[公开原文](https://docs.temporal.io/activities)

<a id="durable-orchestration-021"></a>

### durable-orchestration-021 · What we’ve learned building cloud agents

作者／组织：Josh Ma / Cursor。类型：作者／团队实践或研究文章。版本／日期：2026; accessed2026-10-13。读取日：2026-10-13。

用途：由work-stealing进程loop迁到Temporal后逐步重划activity边界，并把永恒agent workflow改成每任务结束的较短workflow以便升级。

阅读范围：正文 Long-running agents / Decoupling / Development environment。限制：可靠性及规模数值为作者自报，无外部SLA测量；架构机制比数字更适合正文

[公开原文](https://cursor.com/blog/cloud-agent-lessons)

<a id="durable-orchestration-025"></a>

### durable-orchestration-025 · AI Agents should be serverless and durable

作者／组织：Giselle van Dongen, Igal Shilman / Restate。类型：作者／团队实践或研究文章。版本／日期：2025-10-09。读取日：2026-10-13。

用途：等待人工的durable promise允许进程挂起，恢复通过journal取得已完成LLM与tool结果；等待期限和唤醒条件也是持久状态。

阅读范围：完整主体 Cost efficiency / Safe evolution / SDK integration。限制：供应商比较夸张，其他orchestrator也可serverless；几行集成不会自动覆盖未标记的外部副作用

[公开原文](https://restate.dev/blog/resilient-serverless-agents)

<a id="durable-orchestration-026"></a>

### durable-orchestration-026 · Durable Orchestration for AI Agents with Restate and OpenAI SDK

作者／组织：Restate Team。类型：作者／团队实践或研究文章。版本／日期：2026-01-15。读取日：2026-10-13。

用途：agent SDK可作为loop定义层，durable runtime负责session、并发、审批timer和跨agent调用，二者边界可以独立。

选读范围：Building Blocks / Beyond Basics prose。限制：阅读技术解释正文，未审阅缺失的动态示例代码；几行集成不自动覆盖未标记的外部副作用。

[公开原文](https://restate.dev/blog/durable-orchestration-for-ai-agents-with-restate-and-openai-sdk)

<a id="durable-orchestration-027"></a>

### durable-orchestration-027 · Agent checkpointing is far from production-grade resiliency

作者／组织：Giselle van Dongen / Restate。类型：作者／团队实践或研究文章。版本／日期：2026-06-15。读取日：2026-10-13。

用途：checkpoint只是恢复资料，仍需独立故障发现者/重派发者、持久retry日程、唤醒、版本路由与zombie fencing。

阅读范围：完整主体 iceberg sections。限制：文中对所有agent SDK和单写者必须的绝对断言是竞争厂商主张，需收窄为同一可变状态对象的默认设计；不采纳80%量化及保证任何代码必完成

[公开原文](https://restate.dev/blog/why-checkpointing-is-not-production-grade-durable-execution)

<a id="durable-orchestration-028"></a>

### durable-orchestration-028 · Persistent Agent Sessions

作者／组织：Restate。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：同key Virtual Object独占写handler串行，多个session可并行，shared只读handler可与message同时执行。

选读范围：How it works / TS chat / Built-in concurrency / Concurrent retrieval / Steerable agents。限制：已读概念、TS例子和并发/steering尾部；未逐个读7种SDK重复示例

[公开原文](https://docs.restate.dev/ai/patterns/sessions)

<a id="durable-orchestration-030"></a>

### durable-orchestration-030 · A reference agent architecture

作者／组织：Restate。类型：源码／仓库文档。版本／日期：main accessed2026-10-13; reference implementation。读取日：2026-10-13。

用途：controller Agent负责活动turn/输入队列/审批，AgentSession负责transcript和执行loop；二者按同agentId区分所有权。

阅读范围：README 架构正文：Agent / AgentSession、steer / interrupt、sequence 与 revision。限制：新参考实现，不是独立验证生产案例；源码README含实质架构而非仅目录说明

[公开原文](https://github.com/restatedev/agent)

<a id="durable-orchestration-035"></a>

### durable-orchestration-035 · AutoGen teams API: pause/resume and state

作者／组织：Microsoft AutoGen。类型：官方文档／规范。版本／日期：stable; pause/state changes v0.4.9。读取日：2026-10-13。

用途：pause仅调用各agent的on_pause，默认可为空操作且run不会返回；它不是进程冻结或完成。

选读范围：BaseGroupChat.pause, resume, save_state, load_state。限制：仅读相关API片段，未声称整个团队实现审计

[公开原文](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html)

<a id="durable-orchestration-036"></a>

### durable-orchestration-036 · Agent state serialization and save/load

作者／组织：Eric Zhu and AutoGen maintainers。类型：公开问题讨论。版本／日期：2024-11-08; closed2024-12-04 via4436。读取日：2026-10-13。

用途：序列化运行状态不等于完整序列化agent对象；加载仍需先构造正确类型和配置。

阅读范围：Issue body and maintainers discussion。限制：设计讨论时期版本，不据此声称当前缺功能

[公开原文](https://github.com/microsoft/autogen/issues/4100)

<a id="durable-orchestration-041"></a>

### durable-orchestration-041 · Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers

作者／组织：Sajjad Khan。类型：研究论文。版本／日期：v1 2026-08-04。读取日：2026-10-13。

用途：恢复至少要区分继续原分支、显式新fork、审批值消费和外部effect提交；单一resumeAPI无法从checkpointID推断所有意图。

选读范围：https://arxiv.org/html/2608.03836v1 sectionsIII,VI-G,IX。限制：独立研究预印本且未本地复现；有限TLA+状态与抽象模型、SQLiteledger不等于所有外部服务；其称6792已修复与live issue状态不一致，产品结论需以当前代码核查

[公开原文](https://arxiv.org/abs/2608.03836)

<a id="durable-orchestration-044"></a>

### durable-orchestration-044 · Durable Execution with Temporal

作者／组织：Pydantic AI。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：外层run循环在workflow，LLM/tool/MCP在Activity；跨进程对象必须序列化，不能把内存MCP连接复用给另一个worker。

选读范围：Temporal Integration Considerations / Agent Run Context and Dependencies / Large Payloads / Streaming / Activity Configuration。限制：在线文档可变且部分标题与搜索缓存不同；具体默认期限非通用值，未读全部demo

[公开原文](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/)

<a id="durable-orchestration-046"></a>

### durable-orchestration-046 · Actor Fault Tolerance

作者／组织：Ray contributors。类型：官方文档／规范。版本／日期：latest2.59 accessed2026-10-13。读取日：2026-10-13。

用途：max_restarts重跑构造器而非恢复应用状态，checkpoint要主动保存且跨节点可读。

阅读范围：Actor process failure / Actor checkpointing / Actor creator failure / Unavailable actors。限制：Ray默认行为需按版本核对；文中简单文件checkpoint示例没有原子写/外部effect保证

[公开原文](https://docs.ray.io/en/latest/ray-core/fault_tolerance/actors.html)

<a id="durable-orchestration-047"></a>

### durable-orchestration-047 · How to think about durable execution

作者／组织：Alexander Belanger。类型：作者／团队实践或研究文章。版本／日期：2025-12-11。读取日：2026-10-13。

用途：作者从Porter基础设施编排说明单个易幂等任务可能只需持久队列，多步跨系统中间状态才使durable workflow收益明显。

阅读范围：Simple tasks / Complex tasks / Durable execution / It is not a silver bullet。限制：厂商作者经验；stateless或调用外部API并不自动幂等，文章简例需附前提；非所有任务都需框架

[公开原文](https://hatchet.run/blog/durable-execution)

<a id="durable-orchestration-051"></a>

### durable-orchestration-051 · Trigger.dev v3: Durable Serverless functions. No timeouts.

作者／组织：Trigger.dev engineering。类型：作者／团队实践或研究文章。版本／日期：2024 v3 announcement。读取日：2026-10-13。

用途：durability并非只有event replay：CRIU可在支持的等待边界冻结容器进程并稍后恢复，保存模型不同于graph state checkpoint。

阅读范围：How does this work / Checkpoints and Restoring / Versioning / Open-source and self-hosting。限制：历史v3设计，不把旧API/No timeouts标题当当前产品无任何上限；付款示例无幂等key，不能作为安全交易模板

[公开原文](https://trigger.dev/blog/v3-announcement)

<a id="durable-orchestration-052"></a>

### durable-orchestration-052 · Lifecycle of a Durable Object

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：updated2026-09-30。读取日：2026-10-13。

用途：持久对象身份不保证内存对象常驻；hibernation保持特定WebSocket但构造器再执行，普通JS定时器与未完成IO会妨碍休眠。

阅读范围：Lifecycle state transitions / Shutdown behavior / Working without shutdown hooks。限制：示例data.forEach(async...)存在不等待回调和乱序进度风险，不能抄为顺序恢复模板；持久化进度仍不覆盖effect-commit原子性

[公开原文](https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/)

<a id="durable-orchestration-053"></a>

### durable-orchestration-053 · Worker Versioning

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：pin运行到同一build避免新代码解释旧历史；代价是必须保留旧worker，长任务可在Continue-As-New边界升级。

阅读范围：Pinned 与 Auto-Upgrade、replay 兼容、版本保留、升级边界及队列阻塞的说明。限制：特定Temporal功能默认和版本要求可变；只说明机制不将所有系统都要求pin

[公开原文](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning)

<a id="durable-orchestration-057"></a>

### durable-orchestration-057 · durability=sync: put_writes/put persistence order is unenforced

作者／组织：Sajjad Khan and LangGraph contributors。类型：公开问题讨论。版本／日期：opened2026-06-10; 1.2.0/1.2.4 and Sep12 1.2.11 reproduction; open2026-10-13。读取日：2026-10-13。

用途：sync循环等待checkpoint future不自动给所有pending write future建立先后关系；故障恢复选择重放或重执行可受线程调度影响。

选读范围：问题正文、复现与早期讨论，以及 9 月 12 日 PostgreSQL probe 说明；未读全部隐藏评论。限制：未本地运行；部分复现评论AI-assisted且PR8055曾因assignment gate关闭，不把修复提案当已合并；与 [durable-orchestration-041](#durable-orchestration-041)论文同作者并非独立实验交叉背书

[公开原文](https://github.com/langchain-ai/langgraph/issues/8039)

<a id="durable-orchestration-058"></a>

### durable-orchestration-058 · How to do distributed locking

作者／组织：Martin Kleppmann。类型：作者／团队实践或研究文章。版本／日期：2016-02-08。读取日：2026-10-13。

用途：lease到期不代表旧worker已停止；GC暂停、网络迟到让旧attempt在新owner开始后仍写入。

选读范围：效率／正确性区别，以及租约、资源保护和 fencing 的章节；未采用后半 Redlock 专项争论。限制：一般分布式机制只映射到长任务控制面，不展开Redis产品争论；外部系统不支持fencing时需其他幂等/事务/对账边界

[公开原文](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

<a id="human-control-007"></a>

### human-control-007 · Chatbot Message Persistence

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 current docs。读取日：2026-10-13。

用途：默认backpressure使客户端断开可能终止LLM流；consumeStream在后端持续消费可使onEnd及保存继续执行。

选读范围：opening caveat、Handling client disconnects。限制：只读开篇及Handling client disconnects；服务端进程/平台寿命依然是外部前提

[公开原文](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)

<a id="human-control-020"></a>

### human-control-020 · File checkpointing

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current docs；link安全跳过要求Claude Code v2.1.216+。读取日：2026-10-13。

用途：rewindFiles只恢复文件不恢复对话；只跟踪Write/Edit/NotebookEdit，不含Bash及多数子agent写。

选读范围：opening/How checkpointing works/Implement。限制：文件恢复不涵盖已发消息/数据库/远端commit；只实读开篇/How/Implement及restore要求

[公开原文](https://code.claude.com/docs/en/agent-sdk/file-checkpointing)

<a id="human-control-033"></a>

### human-control-033 · Channel inbound lifecycle and delivery settlement

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current plugin SDK docs accessed 2026-10-13。读取日：2026-10-13。

用途：外部builder不能自行铸造参与者provenance；ingress resolver绑定生命周期epoch、agent/session/message/event/admission，异步准备后必须assertActive。

选读范围：首15k正文，ingress identity / lifecycle / acknowledgment / delivery finalization。限制：官方接口契约，非独立执行验证；SDK细节与平台adapter实现关联

[公开原文](https://docs.openclaw.ai/plugins/sdk-channel-inbound)

<a id="human-control-040"></a>

### human-control-040 · Durable chat admission and control-race tests

作者／组织：OpenClaw。类型：源码／仓库文档。版本／日期：main accessed 2026-10-13; primary blob 106defff4fce9851fc98eccfcc617867a7d4a12f。读取日：2026-10-13。

用途：真实存储fixture在清空瞬态dedupe cache后重试已collect source，断言ACK cached且不再次dispatch、不追加transcript；同key换payload/recipient拒绝。

选读范围：pending-inputs、chat-send-ordering 与 approval-run-cancellation 测试：重试、取消和会话替换。限制：已读源码未运行；单进程SQLite fixture/cache清除不等于实测进程崩溃；派发mock不证明真实provider副作用幂等；同测试族合并一个计数

[公开原文](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/chat-send-pending-inputs.test.ts)

<a id="practitioner-lessons-004"></a>

### practitioner-lessons-004 · 007: What we have learned when we built our own Agent Harness

作者／组织：Anil Can Baykal; Ali Onur Geven / Integral。类型：作者／团队实践或研究文章。版本／日期：2026-07-02。读取日：2026-10-13。

用途：事实：利用既有事件基础设施；runner无状态，repo、issue、PR等外部制品承担跨轮交接；prompt独立版本发布。

阅读范围：The orchestration we feared; Conventions; The snake eats its own tail。限制：无状态runner不等于系统无状态，也未证明副作用exactly-once；judge故障fail-open需按风险决定，不宜推广至资金动作。

[公开原文](https://engineering.integral.de/posts/007-agent-harness/)

<a id="practitioner-lessons-011"></a>

### practitioner-lessons-011 · Inside Replit’s Snapshot Engine: The Tech Making AI Agents Safe

作者／组织：Connor Brewster; Luis Héctor Chávez / Replit。类型：作者／团队实践或研究文章。版本／日期：2025-12-18。读取日：2026-10-13。

用途：事实：不可变16MiB块+manifest以copy-on-write实现快照；git提交、数据库状态、agent状态需作为不同状态面考虑。

阅读范围：Bottomless Storage; Versioning Agent Code Changes; Forkable Databases。限制：文中Future的并行模拟与原子采纳属展望；快照覆盖本地受管状态，不自然覆盖邮件、付款等外部副作用。

[公开原文](https://replit.com/blog/inside-replits-snapshot-engine)

<a id="practitioner-lessons-022"></a>

### practitioner-lessons-022 · Building an AI Agent Platform

作者／组织：Chase Dovey。类型：作者／团队实践或研究文章。版本／日期：2026-03-15。读取日：2026-10-13。

用途：事实：TinyClaw统一入口处理消息去重、短消息合并和策略；用channel+message ID的60秒内存表防重复webhook。

选读范围：Message Pipeline; Agent Runner; Session Management。限制：读前14000字符；内存TTL去重不耐重启，过期锁强拆无fencing，丢弃坏行可能丢状态，regex不能保证注入/SSRF安全；不采纳自动允许或绕限建议。

[公开原文](https://cdovey.dev/blog/building-an-ai-agent-platform-from-scratch/)

<a id="practitioner-lessons-026"></a>

### practitioner-lessons-026 · Absurd Workflows: Durable Execution With Just Postgres

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2025-11-03。读取日：2026-10-13。

用途：事实：Postgres队列和checkpoint状态存储，agent每轮步骤存增量消息；失败重试task，已完成step从缓存加载。

阅读范围：With Agents; Events and Sleeps。限制：作者简述无重复工作不能理解为外部副作用exactly-once；整个singleStep包模型和tool时，checkpoint前崩溃可重复执行。

[公开原文](https://lucumr.pocoo.org/2025/11/3/absurd-workflows/)

<a id="practitioner-lessons-027"></a>

### practitioner-lessons-027 · Absurd In Production

作者／组织：Armin Ronacher。类型：作者／团队实践或研究文章。版本／日期：2026-04-04。读取日：2026-10-13。

用途：事实：五个月生产后补了claim/lease/watchdog/deadlock/event race边界；beginStep/completeStep适配before/after hooks。

阅读范围：What Changed; What Held Up; What’s Still Missing。限制：不将“步骤外可随机”泛化为可随意改变恢复控制流；按step缓存仍需稳定标识和代码兼容。

[公开原文](https://lucumr.pocoo.org/2026/4/4/absurd-in-production/)

<a id="practitioner-lessons-031"></a>

### practitioner-lessons-031 · Building Spectre: Internal Collaborative Cloud Agent Platform

作者／组织：Joey Wang; Gabe Pereyra / Harvey。类型：作者／团队实践或研究文章。版本／日期：2026-04-07。读取日：2026-10-13。

用途：事实：durable run保存owner、sharing、附件、轨迹、制品和provider session引用；follow-up启动新worker并恢复session，非保活旧容器。

选读范围：Durable runs ephemeral workers; Sandboxes; Scheduled Runs。限制：阅读前13500字符至What Spectre Taught Us；控制面持久状态仍需事务/去重；共享可见性不自动等于访问授权。

[公开原文](https://www.harvey.ai/blog/building-spectre-internal-collaborative-cloud-agent-platform)

<a id="runtime-boundaries-010"></a>

### runtime-boundaries-010 · fsync durability and delayed disk-full errors

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19 / 2026-02-08。读取日：2026-10-13。

用途：文件fsync不保证目录项已落盘，需目录fd单独fsync；ENOSPC/EDQUOT可在同步时才报告。checkpoint完成信号若早于数据与目录提交，崩溃后可能无法恢复。

选读范围：DESCRIPTION L39-67; ERRORS L72-98。限制：文件系统/硬件契约仍有差异

[公开原文](https://man7.org/linux/man-pages/man2/fsync.2.html)

<a id="runtime-boundaries-015"></a>

### runtime-boundaries-015 · LangGraph graph migrations

作者／组织：LangChain。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。

用途：被interrupt线程不能删除/重命名即将进入的节点；重命名state key会丢旧值，改变类型可能不兼容。技术上可恢复也不保证业务行为兼容，应在state记录行为版本。

选读范围：Graph migrations L898-908; runtime context。限制：partial；仅迁移和runtime context

[公开原文](https://docs.langchain.com/oss/python/langgraph/graph-api)

<a id="runtime-boundaries-019"></a>

### runtime-boundaries-019 · Transcript JSONL corruption; records spliced by unsynchronized writers

作者／组织：NubeBuster。类型：公开问题讨论。版本／日期：created 2026-07-28T03:49:43Z; updated 2026-10-11T06:18:57Z; open。读取日：2026-10-13。

用途：维护者确认多个session writer缺共享锁是real bug；报告者后续实际短写probe发现compaction写忽略bytesWritten，sync+rename仍会原子替换成不完整文件。最新报告2.1.292仍发生；未核验闭源bundle，短写具体根因属报告者分析。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/anthropics/claude-code/issues/81843)

<a id="runtime-boundaries-021"></a>

### runtime-boundaries-021 · Toggling defer on a fan-in node breaks resumed threads: silent barrier corruption one way, ValueError the other

作者／组织：serhiy-bzhezytskyy。类型：公开问题讨论。版本／日期：created 2026-08-14T05:30:15Z; updated 2026-09-24T15:35:16Z; open。读取日：2026-10-13。

用途：切defer改变barrier checkpoint形状，恢复可静默永不触发。作者承认最初unit tests只构造内存tuple没走serde，漏掉tuple变list及finished flag；实际checkpoint端到端测试推翻先前修复。issue仍open。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/langchain-ai/langgraph/issues/8618)

<a id="runtime-boundaries-022"></a>

### runtime-boundaries-022 · \[CLI\] All tools become unavailable after resuming a pre-upgrade session; `/model` restores them

作者／组织：leo9344。类型：公开问题讨论。版本／日期：created 2026-08-28T04:42:35Z; updated 2026-10-11T15:45:17Z; open。读取日：2026-10-13。

用途：升级后resume旧session工具不可见，new session正常，model切换有时修复。初报者一度称0.152.1解决，后在0.153.4再次遇到；不能把单个成功反馈写成已彻底修复。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/openai/codex/issues/41265)

<a id="runtime-boundaries-023"></a>

### runtime-boundaries-023 · LangGraph backward compatibility

作者／组织：LangChain。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：每次resume使用最新graph，技术兼容与业务兼容不同；推荐起始state锁behavior version。Functional API/task/interrupt以位置匹配cache，新增重排会误用旧结果；纯node无此位置约束但副作用仍要幂等。

选读范围：technical/business/non-determinism。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.langchain.com/oss/python/langgraph/backward-compatibility)

<a id="runtime-boundaries-024"></a>

### runtime-boundaries-024 · SQLite atomic commit

作者／组织：SQLite。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：rollback journal先于数据库修改持久化，随后DB同步与commit点共同保证崩溃恢复；OS缓存中的write不是持久化。保证依赖VFS/同步/文件系统硬件假设，不能将设置为OFF后仍称durable。

选读范围：Hardware assumptions; single file commit 3.5-3.11。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://www.sqlite.org/atomiccommit.html)

<a id="runtime-boundaries-025"></a>

### runtime-boundaries-025 · SQLite corruption failure boundaries

作者／组织：SQLite。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：运行中直接copy数据库可混合新旧页；恢复需要hot journal/WAL，删掉辅助文件破坏恢复；fork后继承连接、不同锁协议、在用数据库改名都是例外。沙箱快照/备份必须用一致性方式。

选读范围：backup/journals; locking; unlink; fork; sync。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://www.sqlite.org/howtocorrupt.html)

<a id="runtime-boundaries-032"></a>

### runtime-boundaries-032 · Temporal Python workflow versioning

作者／组织：Temporal。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：workflow逻辑变化可能破坏replay，worker versioning与patched marker是不同方案；移除patch需经历deprecated与旧history保留窗口，new worker通过测试不等于旧run安全。

选读范围：patch/deprecate/remove; replay testing。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.temporal.io/develop/python/workflows/versioning)

<a id="runtime-boundaries-033"></a>

### runtime-boundaries-033 · DBOS workflow code upgrades

作者／组织：DBOS。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：默认workflow源代码hash版本只恢复匹配任务；蓝绿要保留旧进程排空。patch实际由历史当前位置是否已有输出决定，旧workflow尚未到达变更点也可选新分支，不能只按创建时间简化。

选读范围：Patching internals; versioning; blue-green。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.dbos.dev/python/tutorials/upgrading-workflows)

<a id="runtime-boundaries-034"></a>

### runtime-boundaries-034 · Restate immutable deployment versioning

作者／组织：Restate。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：请求重试pin原endpoint，新版本只帮助新请求；修旧run要pause后显式新deployment恢复且journal兼容。Virtual Object state跨版本持久，pin代码不取消state schema兼容责任。

选读范围：immutable deployments; state; migrate in-flight invocations。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.restate.dev/services/versioning)

<a id="runtime-boundaries-035"></a>

### runtime-boundaries-035 · Inngest step identity across deployment

作者／组织：Inngest。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：resume用当前代码按stable step ID复用结果；循环还包含occurrence counter。改ID会重新执行副作用，major变更需新function并让触发条件互斥，验证paused旧run与fresh新run两条路。

选读范围：How versioning works; table; test paused run。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://www.inngest.com/docs/durable-execution/guides-and-advanced/versioning)

<a id="runtime-boundaries-037"></a>

### runtime-boundaries-037 · OpenAI Agents v0.23.1 RunState schema

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v0.23.1 / c4a1d047b22488234b2ba81056e1b9b8db2127a5。读取日：2026-10-13。

用途：当前 RunState schema1.18，新SDK接受其支持的已发布旧schema，旧SDK可能拒绝更新schema；tool origin/agent/server/审批身份陆续纳入。resumed工具已做但Session append失败保存pending batch，恢复在exclusive session中对账而非重跑工具。

选读范围：schema policy L205-262; RunState docstring L790-810; _validate_run_state_schema_version L4045-4063。限制：静态核验，未运行完整SDK测试；已核 tag→commit

[公开原文](https://github.com/openai/openai-agents-python/blob/v0.23.1/src/agents/run_state.py)

<a id="runtime-boundaries-041"></a>

### runtime-boundaries-041 · Record interrupted turns in managed daemon recovery snapshots

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-15; 4d2807023aae3ee317d39a9868fb187618699df2。读取日：2026-10-13。

用途：daemon 恢复仅存 thread ID 不足：输入已接受但尚未形成模型回复时，还要保存活动 turn、output schema、service tier。把恢复数据原子写入同一候选数组，避免 sidecar 与任务列表不一致；shutdown 不能等待已阻塞 rollout writer。

选读范围：PR body and daemon_recovery.rs patch。限制：已合并；未核发布tag。

[公开原文](https://github.com/openai/codex/pull/45807)

<a id="runtime-boundaries-044"></a>

### runtime-boundaries-044 · write(2) Linux manual

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19。读取日：2026-10-13。

用途：write 成功也可能只写部分字节（磁盘满、文件限制、信号中断）；必须推进 offset 并补余量。成功返回不保证持久存储，延迟错误可到 fsync/close 才出现，JSONL 一次write不能当完整记录保证。

选读范围：DESCRIPTION partial writes; NOTES durability。限制：POSIX/Linux 系统调用契约，不能直接等同高级 appendFile 的重试行为。

[公开原文](https://man7.org/linux/man-pages/man2/write.2.html)

<a id="runtime-boundaries-045"></a>

### runtime-boundaries-045 · rename(2) Linux manual

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19。读取日：2026-10-13。

用途：rename 的原子性保证目标名称替换时无缺失窗口，不保证新文件内容完整或断电耐久；跨挂载点 EXDEV，不能假设临时目录文件可原子移入任意目标。

选读范围：DESCRIPTION atomic replacement; ERRORS EXDEV。限制：与 fsync(2)、write(2) 合读才得 durable-save 结论。

[公开原文](https://man7.org/linux/man-pages/man2/rename.2.html)

<a id="runtime-boundaries-051"></a>

### runtime-boundaries-051 · Managing State

作者／组织：Microsoft AutoGen。类型：官方文档／规范。版本／日期：stable tutorial; state examples version1.0.0。读取日：2026-10-13。

用途：AssistantAgent 默认状态只含 model_context，自定义agent默认 save/load 空状态；团队状态保存各agent/manager的消息与轮次，不自动捕获外部工具进程。示例 json.dump 只是序列化持久化教学，不能推出原子替换/崩溃恢复。

选读范围：Saving and Loading Agents note; team state payload; Persisting State example。限制：文档样例不等稳定跨版本schema契约。

[公开原文](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/state.html)

<a id="runtime-boundaries-060"></a>

### runtime-boundaries-060 · Save a sandbox automatically

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：2026-09-30 / SDK1.0。读取日：2026-10-13。

用途：save与stop不能视为单步：snapshot期间可来新请求，保存后重新检查busy/lastActivity才决定destroy；alarm失败/部署中断重试，只能恢复最后checkpoint。

选读范围：Save before stop steps2–3; activeDuringSave; limitations。限制：官方示例机制，不证明一般数据库应用一致性快照。

[公开原文](https://developers.cloudflare.com/sandbox/files/save-a-sandbox-automatically/)

<a id="runtime-boundaries-063"></a>

### runtime-boundaries-063 · Work with sessions

作者／组织：Anthropic。类型：官方文档／规范。版本／日期：current2026-10-13; CLI lookup boundary2.1.223。读取日：2026-10-13。

用途：session只持久conversation，不持久filesystem；跨host需session-store或搬transcript并匹配cwd/lookup语义，session ID本身不是远端持久存储。CLI2.1.223前搜索范围限制在当前project/worktrees，SDK bundled CLI不同会改变恢复结果。

选读范围：Opening distinction; Resume across hosts。限制：platform.claude.com旧URL重定向；不声称会话恢复能还原外部工具状态。

[公开原文](https://code.claude.com/docs/en/agent-sdk/sessions)

<a id="runtime-boundaries-064"></a>

### runtime-boundaries-064 · Hot-reload user config when batch writing config

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged / a684a36091d70e1d8720fb99aafecd2a41ea7207。读取日：2026-10-13。

用途：config落盘与运行任务使用新配置是不同阶段：显式reloadUserConfig后遍历loaded threads提交ReloadUserConfig；提交失败只warn且batch_write仍返回写成功。该实现并不等于所有in-flight turn在同一时刻切换配置。

选读范围：config_api.rs UserConfigReloader/ConfigApi::batch_write; RecordingUserConfigReloader test。限制：已合并但未核发布tag；测试断言reloader被调用，未证明各线程已应用。

[公开原文](https://github.com/openai/codex/pull/13839)

<a id="traces-eval-064"></a>

### traces-eval-064 · Workflow Definition

作者／组织：Temporal。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：durable workflow replay验证相同Command序列与Event History，而非让LLM重新生成完全相同文本；外部API/LLM/DB应隔离成Activities。

选读范围：Deterministic constraints; Code changes; Intrinsic nondeterminism; Versioning。限制：读完整机制正文略七语言实现例；Activity执行仍有重试/副作用语义，不能推出外部effect全局恰好一次。

[公开原文](https://docs.temporal.io/workflow-definition)

[返回分类目录](#topics)

<a id="topic-11"></a>

## 11. 插话、暂停与取消：让旧任务正确让路

<a id="durable-orchestration-007"></a>

### durable-orchestration-007 · Interrupts

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed 2026-10-13; response_schema &gt;=1.2.12。读取日：2026-10-13。

用途：interrupt 恢复从节点开始重跑，父节点调用子图时父节点前段也重跑；原进程栈未被冻结。

选读范围：暂停与恢复、并发 interrupt ID、中断顺序、子图恢复及中断前副作用的说明。限制：文中称1,2,3次重放为指数级不准确；示例只执行一次不能覆盖崩溃后重试，须另外解释提交边界

[公开原文](https://docs.langchain.com/oss/python/langgraph/interrupts)

<a id="durable-orchestration-016"></a>

### durable-orchestration-016 · Cancellation and Termination

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Cancel是协作请求，能执行清理；Terminate立即关工作流，没有清理和补偿，已发生外部动作不会自动撤销。

阅读范围：Cancellation 与 Termination 的区别、清理、Activity heartbeat 及父子结束策略。限制：工作流终止不证明外部进程或远端动作已停止

[公开原文](https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination)

<a id="durable-orchestration-018"></a>

### durable-orchestration-018 · Workflow message passing: Signals, Queries, Updates

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：Signal是异步写入且不返回处理结果，Update是可等待结果/错误的跟踪写请求，Query只读且不能阻塞。

阅读范围：Signal、Query 与 Update 的写入、等待结果和只读语义。限制：各产品消息API保证不同，应借用分类而非照搬实现

[公开原文](https://docs.temporal.io/encyclopedia/workflow-message-passing)

<a id="durable-orchestration-031"></a>

### durable-orchestration-031 · Double texting

作者／组织：LangChain。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：新消息到达已有run时可enqueue/reject/interrupt/rollback，串行队列是默认，不是唯一交互语义。

阅读范围：full body Enqueue/Reject/Interrupt/Rollback。限制：功能属于LangSmith Deployment，不是LangGraph OSS自动保证；外部effect回滚边界为工程推论

[公开原文](https://docs.langchain.com/langsmith/double-texting)

<a id="durable-orchestration-032"></a>

### durable-orchestration-032 · Restate agent turn routing implementation

作者／组织：restatedev/agent contributors。类型：源码／仓库文档。版本／日期：main accessed2026-10-13。读取日：2026-10-13。

用途：ask忙时入队，steer不取消工具，onTurnEnd拒绝陈旧/重复结果并清理子任务和审批后启动后继。

阅读范围：raw.githubusercontent.com/restatedev/agent/main/packages/libs/core/src/agent/turns.ts; handlers.onTurnEnd, route, startSuccessor。限制：代码设计示例未本地执行，main可变；同仓其他薄包装文件未额外计数

[公开原文](https://github.com/restatedev/agent/blob/main/packages/libs/core/src/agent/turns.ts)

<a id="durable-orchestration-048"></a>

### durable-orchestration-048 · Notes on structured concurrency, or: Go statement considered harmful

作者／组织：Nathaniel J. Smith。类型：作者／团队实践或研究文章。版本／日期：2018。读取日：2026-10-13。

用途：父任务return不等于后台子任务结束；未join任务会在文件/连接已关闭后继续使用资源，错误也可能无人收集。

选读范围：go statement considered harmful; Nurseries subsections escape/cancellation/resource/error propagation。限制：2018 Trio设计经验；现代语言产品比较不沿用，内存nursery不提供进程崩溃后的durability

[公开原文](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)

<a id="human-control-001"></a>

### human-control-001 · Codex App Server

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：current docs, accessed 2026-10-13。读取日：2026-10-13。

用途：turn/steer必须匹配expectedTurnId，不创建新turn且不能修改turn级model/cwd/sandbox覆盖。

选读范围：Steer an active turn、Approvals、Errors、Item lifecycle。限制：公开协议文档不等于所有版本实现；MCP elicitation形态仍是此产品所实现版本，不能替代新版MCP规范

[公开原文](https://learn.chatgpt.com/docs/app-server)

<a id="human-control-002"></a>

### human-control-002 · Prompt Turn

作者／组织：Agent Client Protocol。类型：官方文档／规范。版本／日期：ACP v1 current 2026-10-13。读取日：2026-10-13。

用途：cancel后客户端必须取消待审批；代理应尽快停模型/工具，收尾及pending updates之后以cancelled结束原prompt。

选读范围：Stop Reasons/Cancellation。限制：SHOULD与MUST强度不同；不能推出远端副作用已撤销

[公开原文](https://agentclientprotocol.com/protocol/v1/prompt-turn)

<a id="human-control-006"></a>

### human-control-006 · Chatbot Resume Streams

作者／组织：Vercel。类型：官方文档／规范。版本／日期：AI SDK v7 current docs。读取日：2026-10-13。

用途：resumable stream中关闭页面或useChat.stop只是断开HTTP消费；明确停止需要独立后端endpoint取消active work并清理activeStreamId。

选读范围：How stream resumption works/Stop an Active Resumable Stream。限制：示例不是完整授权/事务实现；流恢复只恢复事件消费不自动恢复死进程

[公开原文](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-resume-streams)

<a id="human-control-009"></a>

### human-control-009 · turn/steer can succeed without persisting input while sampling is in flight

作者／组织：angelsbrood; fuller-stack-dev。类型：公开问题讨论。版本／日期：2026-08-26；rust-v0.148.0/0.149.1；后续v0.151.0报告；open。读取日：2026-10-13。

用途：报告者用受控sampling堵塞复现RPC已成功但steer只在pending queue，六分钟无对应user-item durable lifecycle。

选读范围：正文Bounded reproduction/Root cause/Verified minimal fix。限制：已读正文与相关评论，未自行复现；接收函数仅排队返回，不足以证明完整 mailbox 根因或所有采样期行为。

[公开原文](https://github.com/openai/codex/issues/40805)

<a id="human-control-012"></a>

### human-control-012 · Preserve late steer after turn finalization

作者／组织：friel-openai。类型：公开变更／提案。版本／日期：2026-06-27；head 875de1ec111beed474f590f0d329f7b9cf1835e3；open/unmerged verified。读取日：2026-10-13。

用途：补丁把final pending-input检查与取走active task放在同锁下，若有输入继续旧task而不是暴露idle。

选读范围：PR diff：on_task_finished / TaskFinishAction；task_finish_continues_late_input。限制：未合并，不能称正式已修复；已直接读diff，不以bot approval当验证

[公开原文](https://github.com/openai/codex/pull/30341)

<a id="human-control-013"></a>

### human-control-013 · Opening an active conversation in another VS Code window can silently transfer ownership and allow concurrent turns

作者／组织：alexchexes。类型：公开问题讨论。版本／日期：2026-08-14；extension 26.5727.51351；CLI 0.146.0-alpha.9.2；open。读取日：2026-10-13。

用途：报告第二窗口hydration跨await后覆盖follower角色成为owner，两app-server继续写同一rollout。

选读范围：正文timeline及Additional information。限制：日志和shipping code归因来自报告者，未本地复现；非普遍所有版本结论

[公开原文](https://github.com/openai/codex/issues/38629)

<a id="human-control-015"></a>

### human-control-015 · Rollback concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：rollback中断旧run并从数据库删除它，不能再restart；示例最终state只含新run。

选读范围：Introduction/Create runs/View run results。限制：示例只有天气搜索，未承诺撤销已执行外部副作用；不能将run删除当现实回滚

[公开原文](https://docs.langchain.com/langsmith/rollback-concurrent)

<a id="human-control-016"></a>

### human-control-016 · Interrupt concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：interrupt保留旧run及partial状态并标interrupted，第二run接续；区别于删除旧run的rollback。

选读范围：Introduction/Create runs/View run results。限制：只描述Agent Server；不把平台策略等同所有LangGraph运行；示例未覆盖remote取消

[公开原文](https://docs.langchain.com/langsmith/interrupt-concurrent)

<a id="human-control-017"></a>

### human-control-017 · Enqueue concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：enqueue让新消息成为后续run，当前文档说是Agent Server默认；最后state保留两次run成果。

选读范围：introduction/Create runs/results。限制：仅队列策略而非去重/持久ACK保证；JS例子语法不宜照抄

[公开原文](https://docs.langchain.com/langsmith/enqueue-concurrent)

<a id="human-control-018"></a>

### human-control-018 · Reject concurrent runs

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：reject拒绝第二run以409冲突并让原run继续；拒绝并不等同停止原工作。

选读范围：introduction/Create runs 409/results。限制：这是并发准入拒绝，不是工具审批拒绝，正文需明确两类reject

[公开原文](https://docs.langchain.com/langsmith/reject-concurrent)

<a id="human-control-021"></a>

### human-control-021 · Command queue

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：chat.send对既有session的输入先持久化DB再ACK；collect合并turn与源输入consumed同事务。

选读范围：Queue modes/Input durability/Queued-turn cancellation/Answering a pending question。限制：官方实现契约，未直接核完整SQLite实现；默认数值不是通用建议

[公开原文](https://docs.openclaw.ai/concepts/queue)

<a id="human-control-022"></a>

### human-control-022 · Messages and delivery

作者／组织：OpenClaw。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：通用inbound dedupe是按agent/channel route/message ID的内存缓存，20分钟或5000条边界；不能推导跨重启保障。

选读范围：Inbound dedupe/Channel run ownership/Agent reactions/Silent replies。限制：OpenClaw特有行为；不应把所有群聊强制回复泛化；docs queue中durable ingress另有持久层

[公开原文](https://docs.openclaw.ai/concepts/messages)

<a id="human-control-025"></a>

### human-control-025 · Codex turn_input.rs steer_input implementation

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：rust-v0.149.1；blob 424faf3c3a0e298dc5c8e1f562c919388adb9c0e。读取日：2026-10-13。

用途：在active_turn锁下检查expected turn及任务种类，nonempty input入pending queue后返回turn ID；本函数未等待模型采纳或rollout写盘。

选读范围：turn_input.rs 的 steer_input 实现（第 470–568 行）。限制：只读470–568行及函数；不据局部函数证明整个系统无其他去重

[公开原文](https://github.com/openai/codex/blob/rust-v0.149.1/codex-rs/core/src/session/turn_input.rs)

<a id="human-control-039"></a>

### human-control-039 · Interrupts: run boundaries and human resume

作者／组织：AG-UI。类型：官方文档／规范。版本／日期：current interrupt contract accessed 2026-10-13; no implementation version established。读取日：2026-10-13。

用途：RUN_FINISHED可带interrupt outcome，本次run结束仍需人类恢复；新run关联同thread和interrupt ID，pending时不得开始新普通input。

选读范围：正文 Core concepts / pending interrupts / resume payload / tool approval / idempotency and expiration。限制：协议契约而非实现审计；与OpenAI Agents允许部分pending审批续跑不同，不能混用

[公开原文](https://docs.ag-ui.com/concepts/interrupts)

<a id="human-control-041"></a>

### human-control-041 · Mid-turn steering over Responses WebSocket

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：current docs 2026-10-13; GPT-6 family, GPT-5.6 and earlier unsupported。读取日：2026-10-13。

用途：steer.accepted只表示入队；自动continuation等当前output和已启动hosted工具结束，不撤销原动作；每response的限额不等于整条任务限额。

选读范围：steer.accepted、pending / failed、工具等待、continuation 以及断线重连的说明。限制：仅当前指定模型/WebSocket产品契约；不要类推Codex app-server所有行为；未运行SDK示例

[公开原文](https://developers.openai.com/api/docs/guides/steering)

<a id="loop-context-018"></a>

### loop-context-018 · pi agent-loop.ts

作者／组织：Pi maintainers。类型：源码／仓库文档。版本／日期：main read 2026-10-13。读取日：2026-10-13。

用途：两层循环分别处理工具/steering与模型本欲停止后到来的follow-up；消息排队时机是loop语义的一部分。

阅读范围：runLoop; streamAssistantResponse; shouldTerminateToolBatch。限制：动态main未锁定commit；与2025博客的无max-step描述时代不同。

[公开原文](https://github.com/earendil-works/pi/blob/main/packages/agent/src/agent-loop.ts)

<a id="loop-context-025"></a>

### loop-context-025 · Cancellation gaps: between-turn compaction and pending input

作者／组织：tryingET / Pi issue。类型：公开问题讨论。版本／日期：2026-09, main 4d38031fb。读取日：2026-10-13。

用途：取消摘要尝试不一定取消整轮agent；在prepareNextTurn和input hook挂起时，stop/clearQueue后旧输入可能继续入历史或触发模型。

阅读范围：Original reproduction; clarified Escape behavior; timeline。限制：AI辅助报告有明确披露；未自行运行测试，维护者重新打开不等于全部根因已确认。

[公开原文](https://github.com/earendil-works/pi/issues/9783)

<a id="network-errors-026"></a>

### network-errors-026 · Python asyncio tasks and timeouts

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3.15 documentation as read 2026-10-13。读取日：2026-10-13。

用途：asyncio.timeout通过取消当前task转换TimeoutError；wait_for等待取消真正完成，实际墙钟可能超过配置时间。

选读范围：sections Task cancellation/Shielding/Timeouts/Waiting primitives。限制：读取的current页为Python3.15；timeout自3.11可用，具体TaskGroup新API不要倒推旧版本。

[公开原文](https://docs.python.org/3/library/asyncio-task.html)

<a id="network-errors-028"></a>

### network-errors-028 · AnyIO cancellation and timeouts

作者／组织：AnyIO maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：AnyIO level cancellation在已取消scope每个yield点重复触发，与asyncio edge语义不同；外层deadline可能更早。

选读范围：Differences/Timeouts/Finalization/Shielding。限制：未完整读所有scope corruption示例；结论限定取消、超时、finalization部分。

[公开原文](https://anyio.readthedocs.io/en/stable/cancellation.html)

<a id="network-errors-035"></a>

### network-errors-035 · AI SDK #15430: mid-body abort leaves result promises pending

作者／组织：daga-segwise; Vercel maintainers。类型：公开问题讨论。版本／日期：ai 6.0.180 with Bun in report。读取日：2026-10-13。

用途：header200后body被cancel，stream无finish事件，text/steps一直pending；外层AbortSignal也未使聚合promise落终态。

阅读范围：full body and maintainer reproduction/fix notes2026-07-07。限制：报告ai6.0.180/Bun，PR创建不等于已确认发布修复；与现行文档分开。

[公开原文](https://github.com/vercel/ai/issues/15430)

<a id="network-errors-039"></a>

### network-errors-039 · AI SDK stopping streams

作者／组织：Vercel。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：浏览器stop仅abort客户端HTTP；server runtime必须传播disconnect并把req.signal传到模型请求；Vercel Node须supportsCancellation。

阅读范围：full page。限制：平台能力随版本变化；是该SDK的resume契约，不是所有恢复系统互斥。

[公开原文](https://ai-sdk.dev/docs/advanced/stopping-streams)

<a id="runtime-boundaries-043"></a>

### runtime-boundaries-043 · Keep completed tool returns when sibling raises or run cancelled

作者／组织：Pydantic。类型：公开变更／提案。版本／日期：merged 2026-10-09 ad14dc9ae0cc5cb0b9261daa4507acfd63fea817; released v2.55.0。读取日：2026-10-13。

用途：parallel_ordered_events 先发出的慢工具失败时，后发工具可能已经执行完成但尚未记录；恢复历史会为遗失结果补入 interrupted 占位，模型可能因此再次调用已经完成的工具；不是runner保证自动重执行。修复 cancel_and_drain 后记录已成功但未记录的 task，保持异常/事件顺序。

选读范围：PR body; _tool_execution.py patch; tests/test_run_cancellation.py 3 new tests。限制：静态阅读发布修复与测试；未本地执行。 修复覆盖异常/取消路径成功task结果的留存，不证明硬进程崩溃与外部提交之间无丢失窗口。

[公开原文](https://github.com/pydantic/pydantic-ai/pull/10049)

[返回分类目录](#topics)

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

[返回分类目录](#topics)

<a id="topic-13"></a>

## 13. 多 agent：按独立性拆任务，不按人数求能力

<a id="durable-orchestration-002"></a>

### durable-orchestration-002 · How we built our multi-agent research system

作者／组织：Jeremy Hadfield et al. / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2025-06-13。读取日：2026-10-13。

用途：只读广度搜索适合独立子任务，但模糊分工会重复研究，须明确目标、输出、工具、范围与预算。

选读范围：L64,L78-L88; 已读相关主体，非附录。限制：内部研究评测及指定 Claude 版本；性能数值不可泛化为所有多 agent 场景

[公开原文](https://www.anthropic.com/engineering/multi-agent-research-system)

<a id="durable-orchestration-003"></a>

### durable-orchestration-003 · Don’t Build Multi-Agents

作者／组织：Walden Yan / Cognition。类型：作者／团队实践或研究文章。版本／日期：2025-06-12。读取日：2026-10-13。

用途：并行执行者会各自作出未写入任务描述的隐式设计决定，合并文件并不能合并这些冲突的假设。

阅读范围：文章中隐式决策、完整历史与并行执行者协调问题的讨论。限制：明确是2025年模型和生产经验，需与作者2026后续文配读

[公开原文](https://cognition.com/blog/dont-build-multi-agents)

<a id="durable-orchestration-004"></a>

### durable-orchestration-004 · Multi-Agents: What's Actually Working

作者／组织：Walden Yan / Cognition。类型：作者／团队实践或研究文章。版本／日期：2026-04-22。读取日：2026-10-13。

用途：作者生产系统采用单写者加 clean-context reviewer、consultant、manager，而非任意并行写 swarm。

阅读范围：文章中单写者、reviewer / consultant / manager，以及子代理通信与状态假设的讨论。限制：厂商经验数据未给完整评测方法；对注意力与偏差的理论说明不是独立验证的事实

[公开原文](https://cognition.com/blog/multi-agents-working)

<a id="durable-orchestration-017"></a>

### durable-orchestration-017 · Child Workflows

作者／组织：Temporal。类型：官方文档／规范。版本／日期：accessed2026-10-13。读取日：2026-10-13。

用途：子工作流提供独立history与worker隔离，但父子无共享本地状态，父Continue-As-New不保留旧子任务关系。

阅读范围：Child Workflow 的独立历史、隔离、协调成本、Continue-As-New 与容量建议。限制：1000子任务建议是该平台容量经验，不能当所有harness固定值

[公开原文](https://docs.temporal.io/child-workflows)

<a id="durable-orchestration-019"></a>

### durable-orchestration-019 · Scaling long-running autonomous coding

作者／组织：Wilson Lin / Cursor。类型：作者／团队实践或研究文章。版本／日期：2026-01-14。读取日：2026-10-13。

用途：平等agent共享协调文件和手工锁失败：持锁过久/忘释放/违规写会让20个agent只剩约2至3个吞吐。

阅读范围：全文 Learning to coordinate / Planners and workers / What we learned。限制：研究原型而非一般生产SLA；million LoC不是正确性证据；后续更详细文章给出取舍

[公开原文](https://cursor.com/blog/scaling-agents)

<a id="durable-orchestration-020"></a>

### durable-orchestration-020 · Towards self-driving codebases

作者／组织：Wilson Lin / Cursor。类型：作者／团队实践或研究文章。版本／日期：2026-02-05。读取日：2026-10-13。

用途：把计划、检查、写代码、合并、判断完成全部堆给一个连续executor会出现睡眠、少委派、忘合并和过早完成。

阅读范围：全文；第二次从Pathological behaviors至Specifying intent补读被截断中段。限制：作者明确研究浏览器不供外部使用，不能把容忍坏commit迁移到生产发布主干；无独立复现

[公开原文](https://cursor.com/blog/self-driving-codebases)

<a id="durable-orchestration-024"></a>

### durable-orchestration-024 · Building a C compiler with a team of parallel Claudes

作者／组织：Nicholas Carlini / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-02-05。读取日：2026-10-13。

用途：16个agent各自容器repo副本，通过任务文件claim与git集成，巨型Linux编译任务却让它们同时撞上同一bug并覆盖彼此；需改变测试分解方式才实现有效并行。

阅读范围：Enabling long-running / Running parallel / Make parallelism easy / Evaluation。限制：作者称能力极限研究原型；成本与编译器成功有明确限制，不代表无人验证可生产部署

[公开原文](https://www.anthropic.com/engineering/building-c-compiler)

<a id="durable-orchestration-038"></a>
<a id="traces-eval-058"></a>

### durable-orchestration-038 · Why Do Multi-Agent LLM Systems Fail?

作者／组织：Mert Cemri et al.。类型：研究论文。版本／日期：v3 2025-10-26。读取日：2026-10-13。 引用别名：traces-eval-058（本条合计 1 项，各版本复核不另计）。

用途：信息未被采用可能是未发送、未收到、被忽略、上下文截断等不同故障，不能笼统归为agent不聪明。

选读范围：https://arxiv.org/html/2503.13657v3 sections4, appendixA, examplesN1/N3/N8/N11。限制：特定框架和任务集的1600+轨迹，不将频率作为一般故障概率；旧摘要数字已更新

已读版本／别名（同一来源）：
- durable-orchestration-038：v3 2025-10-26；范围：https://arxiv.org/html/2503.13657v3 sections4, appendixA, examplesN1/N3/N8/N11。[该版本原文](https://arxiv.org/abs/2503.13657)
- traces-eval-058：v1, 2025-03-17；范围：3 Methodology; 4.1; 4.3; 7。[该版本原文](https://arxiv.org/html/2503.13657v1)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://arxiv.org/abs/2503.13657)

<a id="durable-orchestration-040"></a>

### durable-orchestration-040 · Towards a Science of Scaling Agent Systems

作者／组织：Yubin Kim et al.。类型：研究论文。版本／日期：v3 2026-04-08。读取日：2026-10-13。

用途：可拆分金融分析与顺序规划对多agent有相反收益；在固定预算下，协调消耗会挤掉真正解决任务的计算。

选读范围：https://arxiv.org/html/2512.08296v3 sections4.2,5。限制：不能将45%阈值或错误放大倍数写成定律；分析脚本修正需同时查看作者changelog

[公开原文](https://arxiv.org/abs/2512.08296)

<a id="practitioner-lessons-005"></a>

### practitioner-lessons-005 · Free the models: Harness design at the frontier

作者／组织：Daniel Furman; Jacky Zhao; Vaibhav Kumar; Ed Sioufi; Michele Catasta / Replit。类型：作者／团队实践或研究文章。版本／日期：2026-09-29。读取日：2026-10-13。

用途：事实（作者实验）：harness提供领域子agent、tier/effort、可复用worker与动态effort选择；不同模型自主委派和重用比例不同。

阅读范围：Why we scaffold less; Composable primitives; Results; Footnotes。限制：仅作者特定模型与两个基准四次重复；不能推论所有模型都会合理控成本，或所有安全/确定性控制都应删去。

[公开原文](https://replit.com/blog/free-the-models)

<a id="practitioner-lessons-060"></a>

### practitioner-lessons-060 · Building Ask DoorDash (Part 4): A Platform for Building and Evolving Agents - DoorDash

作者／组织：Fabio Flores, Lucas Arango / DoorDash。类型：作者／团队实践或研究文章。版本／日期：2026-07-24。读取日：2026-10-13。

用途：事实：gateway负责认证/上下文与传输，域orchestrator把后续回合固定到域内以省路由，再识别越界请求交回router。

阅读范围：Domain orchestration; skills; platform boundaries。限制：全文；文中50–60%缩减只指指令，不包含tool schemas/results/history，不能转写为总token节省。

[公开原文](https://careersatdoordash.com/blog/building-ask-doordash-part-four-a-platform-for-building_and_evolving_agents/)

<a id="practitioner-lessons-070"></a>

### practitioner-lessons-070 · How DoorDash built an AI code reviewer engineers actually listen to - DoorDash

作者／组织：Adam Yarger, Adam Rogal / DoorDash。类型：作者／团队实践或研究文章。版本／日期：2026-05-11。读取日：2026-10-13。

用途：作者复盘：专科fan-out漏整体架构，两个通才又注意力过散，第三版先scout找线索，再交两名reviewer验证，分离怀疑与求证。

选读范围：v1/v2/v3; precision; focused context。限制：读前13000字符至Closing the loop开头；60.2%接受率只计已发布且settled高严重度评论，不表示总体查全率；与其7月评测复盘并读。

[公开原文](https://careersatdoordash.com/blog/doordash-built-an-ai-code-reviewer-engineers-actually-listen-to/)

[返回分类目录](#topics)

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

[返回分类目录](#topics)

<a id="topic-15"></a>

## 15. 回放与评测：证明修复，而不是制造绿色分数

<a id="practitioner-lessons-012"></a>

### practitioner-lessons-012 · Closing the loop: Evaluating and improving Replit Agent at scale

作者／组织：Daniel Furman; Peter Zhong; Zhen Li; Michele Catasta / Replit。类型：作者／团队实践或研究文章。版本／日期：2026-06-23。读取日：2026-10-13。

用途：事实：离线行为测试、生产A/B、trace失败聚类互补；运行更久或成本更低单独无法判断品质方向。

选读范围：Evaluation has to do more; A/B; Telescope; A concrete example。限制：读前12500字符至Where human taste still matters；厂商结果未独立复现；自我改进并非自动获准上线。

[公开原文](https://replit.com/blog/evaluating-and-improving-agent-at-scale)

<a id="practitioner-lessons-029"></a>

### practitioner-lessons-029 · Ten Failure Modes from a Year of Running an Agent Harness — Part 1

作者／组织：Jason Vertrees / Heavy Chain。类型：作者／团队实践或研究文章。版本／日期：2026-06-08。读取日：2026-10-13。

用途：作者亲历：738个mock驱动测试通过但应用未写真实DB或发网络请求；多个独立agent切片无人负责组装后的行为验收。

阅读范围：1 Green Board; 4 Fabricated Fidelity; 5 Trust Chain。限制：叙事未公开事故制品与量化样本；作者未公开部分修复细节，不把故事当频率证明。

[公开原文](https://jvertrees.hashnode.dev/ten-failure-modes-from-a-year-of-running-an-agent-harness-part-1)

<a id="practitioner-lessons-047"></a>

### practitioner-lessons-047 · Improving Deep Agents with harness engineering

作者／组织：Vivek Trivedy / LangChain。类型：作者／团队实践或研究文章。版本／日期：2026-02-17。读取日：2026-10-13。

用途：事实：固定模型后通过轨迹检查添加完成前测试清单、初始环境注入、近deadline提醒和重复编辑提醒，报告TB2从52.8到66.5。

阅读范围：Trace analysis; middleware; reasoning effort。限制：全文；多个改动一起比较，不足以归因单个hook收益；数字限当时模型、任务和预算。

[公开原文](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)

<a id="practitioner-lessons-059"></a>

### practitioner-lessons-059 · Building Ask DoorDash (Part 3): Evaluation - DoorDash

作者／组织：Steven Xu, Fabio Flores, Twisha Jain / DoorDash。类型：作者／团队实践或研究文章。版本／日期：2026-06-30。读取日：2026-10-13。

用途：事实：评测先判断某criterion是否适用，再投影该criterion需要的trace；完整交互包含用户没看到的工具调用和展示widget。

选读范围：Trace projection; simulated shopper; judge calibration。限制：读前14500字符至EvalService；模拟用户无法保证真实迁移，性能数字为团队自报。

[公开原文](https://careersatdoordash.com/blog/building-ask-doordash-part-three-evaluation/)

<a id="practitioner-lessons-062"></a>

### practitioner-lessons-062 · How we learned to trust our AI code reviewer at DoorDash - DoorDash

作者／组织：Saketh Dhulipalla, Vasily Vlasov, Marcus Yearwood, Adam Yarger / DoorDash。类型：作者／团队实践或研究文章。版本／日期：2026-07-06。读取日：2026-10-13。

用途：事实：被接受评论无法覆盖漏报和沉默，因此团队从正常PR、revert和hotfix构建正负例，人工复核production反馈与judge分歧。

选读范围：Acceptance limits; DashBench; controlled comparisons。限制：读前13000字符；数据集105例来自约1000候选，非整个工程总体；多阶段与单阶段差异依赖任务和预算。

[公开原文](https://careersatdoordash.com/blog/how-we-learned-to-trust-our-ai-code-reviewer-at-doordash/)

<a id="practitioner-lessons-063"></a>

### practitioner-lessons-063 · Eval-driven development: Lessons from evaluating GenAI at scale | Airbnb Engineering & Data Science

作者／组织：Rohit Girme, Dan Miller, Mia Zhao, Lifan Yang, Clint Kelly / Airbnb。类型：作者／团队实践或研究文章。版本／日期：unknown (opened page had no date; search metadata suggests 2026-07-28)。读取日：2026-10-13。

用途：事实：agent最终答案可能掩盖错误工具参数或路径，团队重建trace树并用对应职责的子agent judge检查过程。

阅读范围：Section 3 agent evaluation; phased testing。限制：全文；仅使用agent评测和实验机制，非agent的训练/模型部署建议不纳入；图像细节未读。

[公开原文](https://airbnb.tech/ai-ml/eval-driven-development-lessons-from-evaluating-genai-at-scale/)

<a id="practitioner-lessons-073"></a>

### practitioner-lessons-073 · The agent optimization loop and how we built it in Foundry - Command Line

作者／组织：Vivek Bhaduria, Luis Quintanilla, Saket Sathe / Microsoft。类型：作者／团队实践或研究文章。版本／日期：2026-06-02。读取日：2026-10-13。

用途：事实：系统从失败trace生成配置候选，以相同多维评测比较，再由开发者审核、版本化部署；生产信号先由人更新评测，再启动优化。

选读范围：Optimization loop; unseen regressions; when to skip; future rollout。限制：读前14000字符至未来扩展检索参数；reflector优于其他优化的说法缺实验细节，仅作者经验；示例审批故事为说明性场景非公开生产事故。

[公开原文](https://commandline.microsoft.com/the-agent-optimization-loop-and-how-we-built-it-in-foundry/)

<a id="traces-eval-004"></a>

### traces-eval-004 · Demystifying evals for AI agents

作者／组织：Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-01-09。读取日：2026-10-13。

用途：必须区分 transcript 里声称完成与环境 outcome 真正完成，例如预订记录是否存在于数据库。评估对象是模型与 harness 的组合。

阅读范围：Structure; non-determinism; roadmap steps 1–8。限制：案例来自作者内外部实践，建议非严格普遍定律；不是 benchmark 排名证据

[公开原文](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

<a id="traces-eval-010"></a>

### traces-eval-010 · Unit testing - Pydantic AI

作者／组织：Pydantic。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：harness 单元测试可替换模型并硬性关闭真实模型请求，避免延迟、费用及随机性进入逻辑回归。

阅读范围：Unit testing with TestModel; FunctionModel; fixtures。限制：Mock 通过仅说明脚本路径，不能证明模型会选择正确动作

[公开原文](https://ai.pydantic.dev/testing/)

<a id="traces-eval-011"></a>

### traces-eval-011 · How to evaluate your agent with trajectory evaluations

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：trajectory matching 提供 strict/unordered/subset/superset 四种不同约束，按实际安全/业务不变量选取，而非把单一 golden path 当唯一正确行为。

选读范围：Introduction; Trajectory match evaluator。限制：已读 matching 主体；不是证明某种匹配比真实结果评价更好

[公开原文](https://docs.langchain.com/langsmith/trajectory-evals)

<a id="traces-eval-012"></a>

### traces-eval-012 · Use time-travel

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：LangGraph replay 从 checkpoint 后重新执行节点，LLM、API、interrupt 都会再次发生且结果可变；这不是播放缓存记录。

阅读范围：Overview; Replay; Fork; Interrupts; Subgraphs。限制：并非确定性复现，重新执行有外部副作用风险；外部系统不会因改 checkpoint 自动回滚

[公开原文](https://docs.langchain.com/oss/python/langgraph/use-time-travel)

<a id="traces-eval-017"></a>

### traces-eval-017 · A Field Guide to Rapidly Improving AI Products

作者／组织：Hamel Husain。类型：作者／团队实践或研究文章。版本／日期：unknown; current 2026-10-13。读取日：2026-10-13。

用途：作者咨询案例中先读真实对话、开放标注再归类，发现日期/交接等少数高频缺陷，通用 helpfulness 仪表盘掩盖了具体业务失败。

选读范围：Sections1–5。限制：只读1–5节；10x迭代等为经验性主张不当作科学估计；大部分案例非开放可复现数据

[公开原文](https://hamel.dev/blog/posts/field-guide/)

<a id="traces-eval-018"></a>

### traces-eval-018 · Creating a LLM-as-a-Judge That Drives Business Results

作者／组织：Hamel Husain。类型：作者／团队实践或研究文章。版本／日期：unknown; current 2026-10-13。读取日：2026-10-13。

用途：从领域专家 pass/fail 与详细 critique 起步，先修明显系统 bug，再针对无法廉价编程判定的部分训练或校准 judge。

选读范围：Step1; Step3–6; agreement warning。限制：强烈倡导单主评与binary属于作者方法论；其示例某些安全缺陷仍pass不可照搬，安全约束需独立硬门槛；读主体 Step1–6主要相关段

[公开原文](https://hamel.dev/blog/posts/llm-judge/)

<a id="traces-eval-019"></a>

### traces-eval-019 · How do I debug multi-turn conversation traces?

作者／组织：Hamel Husain。类型：作者／团队实践或研究文章。版本／日期：unknown; current 2026-10-13。读取日：2026-10-13。

用途：先读用户可见对话判断是否达目标，再追踪最早上游失败；下游连锁错误不应按多项根因重复计数。

阅读范围：Full article。限制：作者经验，不保证首失败必定是最终根因；多独立故障仍须额外标注

[公开原文](https://hamel.dev/blog/posts/evals-faq/how-do-i-debug-multi-turn-conversation-traces.html)

<a id="traces-eval-023"></a>

### traces-eval-023 · How to make completions consistent with seed

作者／组织：Shyamal Anadkat / OpenAI。类型：官方文档／规范。版本／日期：2023-11-06; archived。读取日：2026-10-13。

用途：历史 seed/system_fingerprint API 明确仅 best-effort，固定 seed、参数和fingerprint仍可能不同；模型层控制不等于整个有工具的 loop 可确定复现。

阅读范围：Implementing consistent outputs; seed/system_fingerprint。限制：已归档；只作确定性承诺的历史反例，不当作2026模型参数支持矩阵

[公开原文](https://developers.openai.com/cookbook/examples/reproducible_outputs_with_the_seed_parameter)

<a id="traces-eval-025"></a>

### traces-eval-025 · Causal Agent Replay: Counterfactual Attribution for LLM-Agent Failures

作者／组织：Jaineet Shah。类型：研究论文。版本／日期：arXiv2606.08275v1 2026-06-06。读取日：2026-10-13。

用途：反事实不是让judge猜哪一步坏，而是重建该点精确状态，替换action/observation/context/policy后向前运行多次，以结果分布变化和置信区间表达效果。

阅读范围：Sections2–7。限制：新预印本与合成SCM验证，尚非成熟生产标准；文中通用因果结论需谨慎，引用为方法边界

[公开原文](https://arxiv.org/html/2606.08275v1)

<a id="traces-eval-026"></a>

### traces-eval-026 · agent-replay README

作者／组织：clay-good。类型：源码／仓库文档。版本／日期：main ccda6229a9451692fb6f1d6d323dd825c2be9dbb 2026-09-07。读取日：2026-10-13。

用途：该项目replay实际是终端播放历史，fork仅复制prefix与lineage并不执行agent；同名功能在不同产品里含义不同，不能根据time-travel名称推断运行语义。

选读范围：README Replay; Compare; Fork; Regression check。限制：小型开源项目README而非独立生产验证；读README Record/Replay/Compare/Fork/Regression相关段，未审完整实现

[公开原文](https://github.com/clay-good/agent-replay)

<a id="traces-eval-029"></a>

### traces-eval-029 · Span-Based Evaluation

作者／组织：Pydantic。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：span评估能检查输出没暴露的工具使用、代理委托和预算退化；必须与输出/环境评价结合。

阅读范围：HasMatchingSpan; Verify Tool Usage; Error Detection; Best Practices。限制：HasMatchingSpan 使用 any(query)；单个非危险 span 不证明整棵树不存在危险调用。该结论来自实现推导，不代表上游已确认文档缺陷。

[公开原文](https://pydantic.dev/docs/ai/evals/evaluators/span-based/)

<a id="traces-eval-031"></a>

### traces-eval-031 · Support creating a SpanTree from historical Logfire data #3946

作者／组织：jtattermusch / Pydantic AI。类型：公开问题讨论。版本／日期：2026-01-07; open at fetched snapshot。读取日：2026-10-13。

用途：历史span不可重建会迫使调试一个evaluator时反复重新运行昂贵模型case；应将执行和评分解耦，让固定trace能反复被新grader处理。

阅读范围：Issue description。限制：这是功能请求及用户工具经验，未证明当下主分支仍无内置能力

[公开原文](https://github.com/pydantic/pydantic-ai/issues/3946)

<a id="traces-eval-032"></a>

### traces-eval-032 · Defeating Nondeterminism in LLM Inference

作者／组织：Horace He / Thinking Machines。类型：作者／团队实践或研究文章。版本／日期：2025-09-10。读取日：2026-10-13。

用途：temperature=0只约束采样；服务负载改变batch size，非batch-invariant kernel可使同一请求的数值/greedy路径变化，不应把所有差异都归为prompt。

选读范围：Batch invariance and determinism; Experiments。限制：读Introduction、batch invariance、experiments；不深入训练部分，不泛化特定性能数字到所有服务

[公开原文](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)

<a id="traces-eval-035"></a>

### traces-eval-035 · Why evaluate agents

作者／组织：Google ADK。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：测试数据要同时保存初始session state、每turn输入、预期中间工具/代理输出与最终结果；简单session用于快测，长evalset用于集成。

选读范围：Test files; Evalsets; conformance; criteria。限制：已读正文主说明与conformance/criteria，未跑命令；文档偏向exact轨迹，需与灵活任务案例并列

[公开原文](https://adk.dev/evaluate/)

<a id="traces-eval-036"></a>

### traces-eval-036 · Evals: don't compare args using tool trajectory #2757

作者／组织：mattmcc-attest; Google ADK contributors。类型：公开问题讨论。版本／日期：2025-08-27 to 2026-01-26。读取日：2026-10-13。

用途：用户只需验证工具种类，但AgentTool生成参数不可逐字固定，导致不得不移除trajectory criterion；这是golden参数过严的实际反馈。

阅读范围：Issue; comments Nov4–6; Jan26。限制：未审外链gist，不能声称自定义metric已内置或current仍无ignore args

[公开原文](https://github.com/google/adk-python/issues/2757)

<a id="traces-eval-040"></a>

### traces-eval-040 · pydantic_evals.evaluators API

作者／组织：Pydantic。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：ArgumentCorrectness需明确first/last/nth occurrence及是否包含失败attempt；重试存在时不指定会检验错那一次。

选读范围：HasMatchingSpan; ArgumentCorrectness; MaxToolCalls; TrajectoryOrder。限制：阅读 HasMatchingSpan、ArgumentCorrectness、预算与 TrajectoryOrder 的 API；源码补查辅助理解，不另拆计数。

[公开原文](https://pydantic.dev/docs/ai/api/pydantic_evals/evaluators/)

<a id="traces-eval-042"></a>

### traces-eval-042 · Usage / Record Modes - VCR.py

作者／组织：VCR.py maintainers。类型：官方文档／规范。版本／日期：8.0.0 latest。读取日：2026-10-13。

用途：录制HTTP请求响应后回放可令相同glue离线可测；none拒绝所有未录请求，new_episodes会意外执行新请求，agent测试尤其要避免自动穿透到真实有副作用API。

阅读范围：Usage; Record Modes。限制：第二条为工程推论；HTTP fixture不保证所有计时/并发/系统I/O确定

[公开原文](https://vcrpy.readthedocs.io/en/latest/usage.html)

<a id="traces-eval-044"></a>

### traces-eval-044 · Datasets

作者／组织：Braintrust。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：数据集应版本化，实验固定版本才能区分harness变更与样本集改变；input/expected/metadata/tags分别负责复现、标准与切片。

阅读范围：Full page。限制：平台文档不证明保留保障；引用生命周期注意是结合008推论

[公开原文](https://www.braintrust.dev/docs/annotate/datasets)

<a id="traces-eval-046"></a>

### traces-eval-046 · Migrating CompileBench to Harbor: standardizing AI agent evals

作者／组织：Quesma。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：作者将多语言自定义harness迁到Harbor，维护成本来自任务与评分基础设施而不只是模型；自包含任务、reward契约使失败可定位。

阅读范围：Full article。限制：团队一手经验，无对照性能测量；不推广Harbor必然优于其他框架。

[公开原文](https://quesma.com/blog/compilebench-in-harbor/)

<a id="traces-eval-047"></a>

### traces-eval-047 · How we compare model quality in Cursor

作者／组织：Cursor。类型：作者／团队实践或研究文章。版本／日期：CursorBench 3.1; 2026-05 update。读取日：2026-10-13。

用途：以真实内部agent会话及后续commit构造任务，随使用分布刷新；同一版本内比较模型，不能把不同eval版本得分当连续趋势。

阅读范围：Real tasks; Hybrid online/offline; Versions。限制：公司自述；实际长期外部服务任务可复现性仍有限，不把公共benchmark批評当已独立验证结论。

[公开原文](https://cursor.com/blog/cursorbench)

<a id="traces-eval-048"></a>
<a id="practitioner-lessons-019"></a>

### traces-eval-048 · Testing if bash is all you need

作者／组织：Ankur Goyal / Braintrust, Vercel guest post。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。 引用别名：practitioner-lessons-019（本条合计 1 项，各版本复核不另计）。

用途：SQL/bash/filesystem同问题实验中的初始大分差，部分来自harness和golden答案错误：stat六万八千文件超时、缺schema、data-loading off-by-one、五个错误或歧义标准答案。

阅读范围：Experiment iterations; trace-driven fixes; conclusion。限制：案例特定小数据工作负载；不把初始100%对53%推广为SQL普遍优越。

[公开原文](https://vercel.com/blog/testing-if-bash-is-all-you-need)

<a id="traces-eval-049"></a>

### traces-eval-049 · Introducing Invariant Explorer

作者／组织：Lavinia Petrache and Luca Beurer-Kellner / Invariant Labs。类型：作者／团队实践或研究文章。版本／日期：2024-12-17。读取日：2026-10-13。

用途：将人工注释与pytest断言失败定位到trace中具体消息或工具结果，便于从线上失败提炼可重复边缘情境。

阅读范围：Full article。限制：产品发布介绍，无生产因果成效数据；观测定位不等于证明内部推理因果。

[公开原文](https://invariantlabs.ai/blog/explorer)

<a id="traces-eval-050"></a>

### traces-eval-050 · agent-eval README and test contract

作者／组织：Vercel Labs。类型：源码／仓库文档。版本／日期：main 28e71cf, 2026-10-08。读取日：2026-10-13。

用途：否定transcript断言在缺失或空轨迹时仍必须抛错；LLM criterion失败关闭不应被.not反转成失败开放。

选读范围：Observability; Judge assertions; Reuse/fingerprints; Retry classification; Token usage。限制：读README观测、judge、reuse/fingerprint、token与retry/reporter章节；未全实现审计。其默认行为为事实，非推荐全部照做。

[公开原文](https://github.com/vercel-labs/agent-eval)

<a id="traces-eval-051"></a>

### traces-eval-051 · Compare experiments

作者／组织：Braintrust。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：默认按input配对会被timestamp/session_id等动态字段打断，需稳定comparison key；baseline还受branch和dataset_id约束。

选读范围：Comparison keys; Trial grouping; Diffs; CI。限制：读完整正文略代码；平台特定默认应按版本核对。

[公开原文](https://www.braintrust.dev/docs/evaluate/compare-experiments)

<a id="traces-eval-052"></a>

### traces-eval-052 · Set up human feedback workflows using annotation queues

作者／组织：LangChain。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：run标注和整段thread标注解决不同问题，多轮必须正确session/thread关联；两条run的pairwise不等于两段完整对话。

选读范围：Run/thread queues; Multiple reviewers; Retention。限制：完整正文略API示例；功能与套餐限制可能变，不作为统一接口。

[公开原文](https://docs.langchain.com/langsmith/annotation-queues)

<a id="traces-eval-053"></a>

### traces-eval-053 · Scorers

作者／组织：UK AI Security Institute / Inspect。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：回答错误、格式无效、无回答和无可用target而无法评分必须区分；grader失败不能混作agent能力错误。

选读范围：Built-in scorers; error policies; metrics links。限制：读正文及API说明，略长代码；具体scorer参数需固定版本。

[公开原文](https://inspect.aisi.org.uk/scorers.html)

<a id="traces-eval-054"></a>

### traces-eval-054 · Validating scanners

作者／组织：Meridian Labs / Inspect Scout。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：trace scanner应以人工标签验证，用precision/recall/F1/balanced accuracy对齐漏报误报代价；开发集与测试集拆分避免调prompt过拟合。

选读范围：Validation; Predicates; Persistence。限制：读validation设计、指标、predicate持久化约8.5k字符；非全文所有代码。

[公开原文](https://meridianlabs-ai.github.io/inspect_scout/validation.html)

<a id="traces-eval-055"></a>

### traces-eval-055 · Invariant Testing: test agent trajectories

作者／组织：Invariant Labs。类型：源码／仓库文档。版本／日期：current main 2026-10-13。读取日：2026-10-13。

用途：测试在trace.as_context下把assertion连接到精确文本位置；实例既断言提取地点数量为1也断言Paris，可直接高亮错误London。

阅读范围：README testing example and localized assertion explanation。限制：读README与示例测试；非整个代码库安全审计。

[公开原文](https://github.com/invariantlabs-ai/testing)

<a id="traces-eval-056"></a>

### traces-eval-056 · Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Applications with Human Preferences

作者／组织：Shreya Shankar et al.。类型：研究论文。版本／日期：v1, 2024-04-18。读取日：2026-10-13。

用途：开发者在见到输出后既新增标准也重释旧标准；同一句无hashtags有人理解去掉#有人理解移除整实体，评分实现可悄悄偏离自然语言rubric。

选读范围：Abstract; introduction; 7.3; 8.3; conclusion。限制：读摘要引言、7.3、8.3与结论；9名开发者、两类pipeline、短期非生产研究，推广有限。第二条为工程推论。

[公开原文](https://arxiv.org/html/2404.12272v1)

<a id="traces-eval-057"></a>

### traces-eval-057 · Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems

作者／组织：Shaokun Zhang et al.。类型：研究论文。版本／日期：v1, 2025-04-30。读取日：2026-10-13。

用途：完整上下文判责任agent与逐步定位错误各有不同表现，失败归因不能假设一个LLM读完整日志就能准确指出根因。

选读范围：Sections 2–4.3; Appendix F。限制：读摘要、1–4.3、附录F；184标注任务、127系统多为自动生成，turn-based单行动假设，不支持并行系统普遍结论。

[公开原文](https://arxiv.org/html/2505.00212v1)

<a id="traces-eval-061"></a>

### traces-eval-061 · Pytest integration

作者／组织：LangChain。类型：官方文档／规范。版本／日期：langsmith &gt;=0.3.4; metadata &gt;=0.7.13。读取日：2026-10-13。

用途：单个test case映射dataset example与experiment run，适于不同用例有不同输入和断言；每次run更新dataset，应记录真实数据集版本。

选读范围：Define tests; Feedback; Metadata; Caching; Rich outputs。限制：读完整正文略代码；HTTP缓存不证明实时模型回归，结合042；未运行示例。

[公开原文](https://docs.langchain.com/langsmith/pytest)

<a id="traces-eval-062"></a>

### traces-eval-062 · Scoring Workflow

作者／组织：UK AI Security Institute / Inspect。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。

用途：先生成并保存未评分log，再独立score可迭代grader而不重跑昂贵agent；这是对同一证据重新评判，不是agent性能改善。

阅读范围：Unscored Evals; Score Command; overwrite modes。限制：读完整正文略API代码；若原log未采到所需状态，换grader也不能恢复。

[公开原文](https://inspect.aisi.org.uk/scoring-workflow.html)

[返回分类目录](#topics)

<a id="supplementary"></a>

## 补充证据，不增加来源总数

以下条目只用于辅助确认已有结论或定位版本，不增加总数。判断依据是实际阅读的实质内容与去重关系，不仅是文件类型；同一实现的短类型片段、局部测试与调用点不拆成新增来源。同页或同文件的新版本复核已并入对应条目。

<a id="human-control-038"></a>
<a id="runtime-boundaries-029"></a>

### human-control-038 · Sharing objects with presigned URLs (independent recheck)

作者／组织：AWS。类型：官方文档／规范。版本／日期：S3 User Guide accessed 2026-10-13。读取日：2026-10-13。 引用别名：runtime-boundaries-029（同一组补充材料，不计数）。 补充证据，不增加总数。

用途：presigned URL受签名主体权限、credential寿命和额外策略共同限制，名义URL到期时间不是唯一期限。

选读范围：Who can create / expiration / limiting capabilities / expiry while downloading。限制：签名 URL 的有效期还受签名凭证和策略约束；链接存在不等于任何接收人都能访问。

已读版本／别名（同一来源）：
- human-control-038：S3 User Guide accessed 2026-10-13；范围：Who can create / expiration / limiting capabilities / expiry while downloading；补充复核，不新增计数。[该版本原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- runtime-boundaries-029：live documentation 2026-10-13；范围：Who can create; expiration; FAQs；补充复核，不新增计数。[该版本原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

不同版本的行为不可互换；版本复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

<a id="protocol-audit-008"></a>

### protocol-audit-008 · Google SDK FunctionCall/FunctionResponse types

作者／组织：Google。类型：源码／仓库文档。版本／日期：v2.13.0; blob feffb5756f8ca0836e113036274ee274c57654e7。读取日：2026-10-13。 补充证据，不增加总数。

用途：FunctionCall.id与FunctionResponse.id为Optional；存在时应匹配，不得假设所有模式始终给ID。

选读范围：FunctionCall / FunctionResponse 类型定义。限制：仅类型与注释复核，不证明服务端每一种组合均接受。 辅助核验类型片段，不作为额外独立来源计数。

[公开原文](https://github.com/googleapis/python-genai/blob/v2.13.0/google/genai/types.py)

<a id="protocol-audit-022"></a>

### protocol-audit-022 · Anthropic released MessageParam role

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0 (2026-08-20); blob 466c03eca17656b06337de7eb71f164d89196c2c。读取日：2026-10-13。 补充证据，不增加总数。

用途：发行版MessageParam role已有system；支持新版专页而非API参考页旧式绝对否定说明。

选读范围：MessageParam.role 与同 tag 的版本说明。限制：一个类型枚举复核，不另计新增来源；类型允许不表示每模型接受。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/types/message_param.py)

<a id="protocol-audit-027"></a>

### protocol-audit-027 · LiteLLM affinity regression cases

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：测试覆盖同边界、混合origin、unknown origin、跨组和order-based failover，证明同组与异组路径须分开。

选读范围：加密 reasoning 亲和性与 fallback 回归用例（静态阅读）。限制：只静态读列出测试及assert，未跑litellm或真实provider。 同机制实现的辅助回归测试核验，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/tests/unit/router_utils/pre_call_checks/test_encrypted_content_affinity_check.py)

<a id="protocol-audit-028"></a>

### protocol-audit-028 · LiteLLM Responses reasoning strip implementation

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：只检查list中type=reasoning且有encrypted_content的item；有可读摘要则去id/密文，无可读内容则删item；原地修改输入列表。

选读范围：Responses reasoning 清理分支。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。 同机制实现的配套helper核验，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/responses/utils.py)

<a id="protocol-audit-029"></a>

### protocol-audit-029 · LiteLLM Anthropic-shaped bridge reasoning

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：清除Anthropic-shaped messages时is_encrypted_reasoning_block仅识别LiteLLM Responses桥接前缀。

选读范围：Anthropic 消息桥接与 reasoning 转换分支。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。 同机制实现的配套helper核验，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/litellm_core_utils/prompt_templates/common_utils.py)

<a id="protocol-audit-030"></a>

### protocol-audit-030 · LiteLLM fallback hop integration

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：fallback hop在部署参数准备阶段调用strip helper，unmarked_origin指向刚失败部署；这不是通用history repair。

选读范围：Router 的 fallback 调用点。限制：辅助调用点与network-router源码交叉复核，不另计巨文件小段。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router.py)

<a id="protocol-audit-031"></a>

### protocol-audit-031 · LiteLLM previous-response deployment continuity

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：previous_response_id routing是另一开关路径；可识别且原部署healthy时pin，target_order存在则提前跳过。

选读范围：previous_response_id 的 deployment 连续性检查。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。 同适配审计中的局部previous_response_id辅助helper，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router_utils/pre_call_checks/deployment_affinity_check.py)

<a id="protocol-audit-032"></a>

### protocol-audit-032 · LiteLLM Responses deployment tests

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：测试区分有previous_response_id、无ID、不存在ID、多ID的路由情况；仅模拟调用目标，非跨provider state恢复证明。

选读范围：Responses deployment 连续性测试（静态阅读）。限制：辅助固定实现核对；测试未执行。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/tests/unit/router_utils/pre_call_checks/test_responses_api_deployment_check.py)

<a id="tools-security-061"></a>

### tools-security-061 · MCP Versioning

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：Current 2026-07-28 verified 2026-10-13。读取日：2026-10-13。 补充证据，不增加总数。

用途：官方明确当前版2026-07-28，日期版本只在不向后兼容变化时递增。

阅读范围：Revisions; Negotiation。限制：仅作为版本定位证据，不额外计数。

[公开原文](https://modelcontextprotocol.io/specification/versioning)

<a id="protocol-audit-010"></a>

### protocol-audit-010 · Responses done native event type

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob 793edac97bfb2b8ed23d0c899f5b279a997e3d5b。读取日：2026-10-13。 补充证据，不增加总数。

用途：原生done仅声明arguments/item_id/output_index/sequence_number/type，无name或item。

选读范围：ResponseFunctionCallArgumentsDoneEvent 类型定义。限制：辅助确认同一PR契约，不把一个小类型文件另充新增来源。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/types/responses/response_function_call_arguments_done_event.py)

<a id="protocol-audit-011"></a>

### protocol-audit-011 · Chat stream helper event types

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob d4c1f28300b4f63da95a87613e78c6f4a4e897b7。读取日：2026-10-13。 补充证据，不增加总数。

用途：Chat辅助事件tool_calls.function.arguments.done明确带name/index/arguments/parsed_arguments；名称与原生Responses事件不同。

选读范围：FunctionToolCallArgumentsDoneEvent 类型定义。限制：仅事件类型辅助复核，未把多个类型文件拆成来源计数。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/streaming/chat/_events.py)

<a id="protocol-audit-016"></a>

### protocol-audit-016 · Published unsafe-finish regression tests

作者／组织：Vercel AI SDK maintainers。类型：源码／仓库文档。版本／日期：ai@7.0.70; blob ae0aa433eee8205a61a8f4b0e490f401c174ee9f。读取日：2026-10-13。 补充证据，不增加总数。

用途：发行版测试覆盖length/error/content-filter/other时即使参数对象有效execute仍不调用。

选读范围：unsafe finish reason 的工具执行回归测试（静态阅读）。限制：辅助核验同一个补丁的回归，不另计小段测试。

[公开原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.test.ts)

<a id="runtime-boundaries-017"></a>

### runtime-boundaries-017 · AI SDK release boundaries 7.0.130-138

作者／组织：Vercel。类型：源码／仓库文档。版本／日期：ai@7.0.138 / 543d42cdda96e2ecb59c0a28f197067b96b5ac8d。读取日：2026-10-13。 补充证据，不增加总数。

用途：7.0.130修复abort时pending promise与reader；7.0.136才修复模型内容timer不覆盖本地工具且每retry刷新；7.0.138处理resume重复parts与匹配tool输出对象。补丁版本也能改变harness可观察语义。

选读范围：7.0.136, 7.0.130, 7.0.138 release entries。限制：固定 7.0.138 tag 对应 commit 的 CHANGELOG L1–210 已复读，具体 timer 另与7.0.136固定实现交叉核验。 辅助核验实现的版本发布边界，不作为额外独立来源计数。

[公开原文](https://github.com/vercel/ai/blob/543d42cdda96e2ecb59c0a28f197067b96b5ac8d/packages/ai/CHANGELOG.md)

<a id="protocol-audit-020"></a>

### protocol-audit-020 · Anthropic schema transformation tests

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0; blob 7a2799dced9310db6547c680a1e0dcda46939e84。读取日：2026-10-13。 补充证据，不增加总数。

用途：原维护者测试展示minimum/default进入description、object额外字段关闭等实际变换。

选读范围：schema transformation 相关测试。限制：辅助同模块固定版本验证，不另计测试片段。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/tests/lib/_parse/test_transform.py)

<a id="protocol-audit-021"></a>

### protocol-audit-021 · Anthropic typed parse response validation

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0; blob ee8326e5f7a7072ed2ffdfed79fea347a1f3eb36。读取日：2026-10-13。 补充证据，不增加总数。

用途：parse_text使用TypeAdapter(output_format).validate_json，表明使用该typed helper时原类型校验会再次发生。

选读范围：parse_text / parse_response。限制：短实现用于界定helper路径，不声称所有create/raw schema路径自动校验。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/lib/_parse/_response.py)

<a id="protocol-audit-035"></a>

### protocol-audit-035 · OpenAI Chat auto-parser guards

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob 7a1bded1de9f8066ee4035dc71156e7db30dd2a3。读取日：2026-10-13。 补充证据，不增加总数。

用途：validate_input_tools拒绝非strict工具；length/content_filter在parse阶段抛专门异常。

选读范围：Chat 自动解析的前置检查与 chat resource 调用点。限制：本地SDK方法约束而非服务端400；不等同create接口约束。 局部类型/helper/parse守卫的辅助核验，不作为额外独立来源计数。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/_parsing/_completions.py)

<a id="network-errors-063"></a>

### network-errors-063 · Stream — buffering, writable.write and backpressure

作者／组织：Node.js。类型：官方文档／规范。版本／日期：Node.js v26.11.1 live documentation, read 2026-10-13。读取日：2026-10-13。 补充证据，不增加总数。

用途：writable.write返回false后生产者应等待drain再继续写；若忽略信号继续写，缓冲可增长至内存耗尽，因此设置阈值本身不等于实现背压。

选读范围：Buffering; Event:drain; writable.write (lines951–979); Three states/readableFlowing (line1032); pipeline (lines3562–3595)。限制：只读Buffering、drain、writable.write、Readable状态与pipeline相关段落，未运行Node。作为既有流式执行机制的补充核验，不增加主计数。不能外推暂停本地流会停止远端模型生成。

[公开原文](https://nodejs.org/api/stream.html)

<a id="durable-orchestration-042"></a>

### durable-orchestration-042 · Agent-scaling analysis changelog

作者／组织：Yubin Kim and agent-scaling contributors。类型：源码／仓库文档。版本／日期：v2.2.0–v2.2.2 accessed2026-10-13。读取日：2026-10-13。 补充证据，不增加总数。

用途：v2.2.0修正分析误纳10个out-of-sample行，260而非270行；旧脚本未复现论文回归值，修正后可复现。

阅读范围：https://raw.githubusercontent.com/ybkim95/agent-scaling/main/CHANGELOG.md v2.2.0–v2.2.2。限制：分析脚本修正不等于实验结果被否定；experimental code保持2.1.3，不将此描述成造假 既有论文的分析CHANGELOG辅助核验，不作为额外独立来源计数。

[公开原文](https://github.com/ybkim95/agent-scaling/blob/main/CHANGELOG.md)

[返回分类目录](#topics)
