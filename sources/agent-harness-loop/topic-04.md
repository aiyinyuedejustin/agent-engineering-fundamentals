[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

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

选读范围：article body。限制：文中内部评测和节省token数据不能外推到别的模型或工具集；与 [tools-security-002](topic-04.md#tools-security-002)是不同工具机制的补充。

[公开原文](https://www.anthropic.com/engineering/advanced-tool-use)

<a id="tools-security-059"></a>

### tools-security-059 · Equipping agents for the real world with Agent Skills

作者／组织：Anthropic / Barry Zhang, Keith Lazuka, Mahesh Murag。类型：作者／团队实践或研究文章。版本／日期：2025-10-16; updated 2025-12-18。读取日：2026-10-13。

用途：技能元数据、主体、引用资源分层加载；脚本可运行而无需先进入模型上下文，节省上下文不等于代码已经审核。

阅读范围：Anatomy; code execution; security considerations。限制：原文是机制介绍和作者建议，不提供供应链防御的形式保证。

[公开原文](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

[返回分类目录](README.md#topics)
