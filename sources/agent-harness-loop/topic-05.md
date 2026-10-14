[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

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

选读范围：批准签名的工具调用身份与参数绑定，以及续跑参数校验／变换的说明。限制：签名不证明用户身份、租户权限、有效期或目标资源仍相同；实际代码另核 [human-control-029](topic-05.md#human-control-029)

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

<a id="r3-tools-005"></a>

### r3-tools-005 · How we contain Claude across products

作者／组织：Max McGuinness, Mikaela Grace, Jiri De Jonghe, Jake Eaton, Abel Ribbink / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-05-25。读取日：2026-10-14。

用途：项目配置在信任确认前被激活，以及同域 API 使用攻击者账户上传，都是作者报告的边界失效。

选读范围：Article body, containment patterns and reported failures ; focus 62–65, 88–99, 106–120。限制：第一方报告非独立复现；不沿用单次红队成功率推广所有模型，也不宣称代理已消灭外发风险。

[公开原文](https://www.anthropic.com/engineering/how-we-contain-claude)

<a id="r3-tools-006"></a>

### r3-tools-006 · Workspace Trust

作者／组织：Microsoft / VS Code。类型：官方文档／规范。版本／日期：Page footer 2026-10-07。读取日：2026-10-14。

用途：打开终端、枚举任务、加载执行路径配置都可能间接执行项目内容。

选读范围：Safe code browsing; Restricted Mode; terminal/tasks/settings/extensions; trust scopes。限制：VS Code 行为是产品例子，不要求所有 harness 禁用所有 agent；恶意扩展可忽略受限模式。

[公开原文](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust)

<a id="r3-tools-010"></a>

### r3-tools-010 · Safeguarding VS Code against prompt injections

作者／组织：Michael Stepankin / GitHub Security Lab。类型：作者／团队实践或研究文章。版本／日期：2025-08-25; updated 2026-07-06。读取日：2026-10-14。

用途：读取与浏览器打开就可串成外发，不能只审写工具。

选读范围：Agent loop/context and tool review; fetch URL parsing; Simple Browser; immediate-effect edits。限制：仅使用已公开历史漏洞的失效机制；未执行 payload；不把旧漏洞状态说成当前仍可利用。

[公开原文](https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/)

<a id="r3-tools-013"></a>

### r3-tools-013 · How GitHub's agentic security principles make our AI agents as secure as possible

作者／组织：Rahul Zhade / GitHub。类型：作者／团队实践或研究文章。版本／日期：Live page accessed 2026-10-14; publication date not extracted。读取日：2026-10-14。

用途：issue 内容作者、指派 agent 的发起者和真正执行的 agent 是不同角色。

选读范围：Security concerns and six agentic product rules。限制：历史产品文章有特定 firewall/MCP 行为；不当作今日全部产品的统一实现。

[公开原文](https://github.blog/ai-and-ml/github-copilot/how-githubs-agentic-security-principles-make-our-ai-agents-as-secure-as-possible/)

<a id="r3-tools-016"></a>

### r3-tools-016 · Policy engine

作者／组织：Google / Gemini CLI maintainers。类型：官方文档／规范。版本／日期：Live docs accessed 2026-10-14。读取日：2026-10-14。

用途：管理策略文件有独立所有权/可写性边界。

选读范围：Admin policy provenance/security ; rule schema ; shell and MCP rules。限制：此处不声称文档暴露了通用 bypass；仅用公开契约说明规则边界和版本成本。

[公开原文](https://geminicli.com/docs/reference/policy-engine/)

<a id="runtime-boundaries-039"></a>

### runtime-boundaries-039 · Avoid executing PATH helpers before workspace trust

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-02; 637c3227b3c5327d64a73fe0b3764ade139efd1f。读取日：2026-10-13。

用途：doctor/startup 在用户信任工作区前运行 PATH 内 git/npm --version 也会执行仓库植入程序；修复区分静态定位与执行，可信系统路径和 sanitized Git 环境在初始化也必须应用。

选读范围：PR description; doctor/runtime.rs; tests/doctor_path_safety.rs。限制：已合并；未核发布tag。

[公开原文](https://github.com/openai/codex/pull/42324)

<a id="runtime-boundaries-062"></a>
<a id="boundary-closure-002"></a>

### runtime-boundaries-062 · Request preconditions

作者／组织：Google Cloud。类型：官方文档／规范。版本／日期：current2026-10-13。读取日：2026-10-13。 引用别名：boundary-closure-002（本组合计 1 项，关联文档与版本复核不另计）。

用途：延迟重试可能删掉同名新产物；generation匹配把操作绑定到对象版本，412应当冲突处理而非无条件重试。读metadata和数据分两次也需版本条件，防manifest hash对应旧版本、下载新版本。

选读范围：Introduction; composition/copy preconditions; multiple request retries example; best practices。限制：相关章节静态阅读，未运行测试。

已读关联文档／版本（同一计数组）：
- boundary-closure-002：current docs, accessed 2026-10-13；范围：Introduction；Precondition criteria；Best practices；Multiple request retries；补充复核，不新增计数。[该记录原文](https://docs.cloud.google.com/storage/docs/request-preconditions)
- runtime-boundaries-062：current2026-10-13；范围：Introduction; composition/copy preconditions; multiple request retries example; best practices。[该记录原文](https://docs.cloud.google.com/storage/docs/request-preconditions)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

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
<a id="r3-tools-001"></a>
<a id="tools-security-063"></a>

### tools-security-012 · Security Best Practices — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：r3-tools-001、tools-security-063（本组合计 1 项，关联文档与版本复核不另计）。

用途：现版将Session Hijacking改为State Handle Hijacking：所有请求验证身份，handle服务端绑定经验证主体，不能把拥有handle当认证。

阅读范围：State Handle Hijacking; Mix-Up; Localhost Redirect; Scope Minimization。限制：2026-07-28 版安全章节；与旧版合为同一来源。状态句柄变化不代表所有已部署客户端都已升级。

已读关联文档／版本（同一计数组）：
- r3-tools-001：2025-11-25 documentation route; live content read 2026-10-14；范围：Confused Deputy; Token Passthrough; SSRF; Session Hijacking; Local MCP Server Compromise; OAuth URL validation; stdio proxy security; Scope Minimization；补充复核，不新增计数。[该记录原文](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)
- tools-security-012：2025-11-25；范围：Security Best Practices: attacks and mitigations。[该记录原文](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices)
- tools-security-063：2026-07-28；范围：State Handle Hijacking; Mix-Up; Localhost Redirect; Scope Minimization；补充复核，不新增计数。[该记录原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

<a id="tools-security-014"></a>
<a id="tools-security-064"></a>

### tools-security-014 · Authorization — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：tools-security-064（本组合计 1 项，关联文档与版本复核不另计）。

用途：必须在给任何token endpoint发送授权码前对比已记录issuer；当metadata宣告支持iss但响应缺失时拒绝。

选读范围：Authorization Response Validation; Access Token Usage; Scope Challenge Handling。限制：同一规范章节新版本复核，合并014不重复计数；没有穷尽OAuth外链。

已读关联文档／版本（同一计数组）：
- tools-security-014：2025-11-25；范围：2025-11-25 版：Purpose 至 Token Audience Binding（正文前 22000 字符）。[该记录原文](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)
- tools-security-064：2026-07-28；范围：Authorization Response Validation; Access Token Usage; Scope Challenge Handling；补充复核，不新增计数。[该记录原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

<a id="tools-security-015"></a>
<a id="tools-security-066"></a>

### tools-security-015 · Elicitation — Model Context Protocol (2026-07-28)

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：2026-07-28。读取日：2026-10-13。 引用别名：tools-security-066（本组合计 1 项，关联文档与版本复核不另计）。

用途：accept仍只表示同意外部交互，现版用重试原请求结合requestState或服务器状态检查完成，不再依赖旧completion通知。

阅读范围：URL Mode; Statefulness; Safe URL Handling; Phishing。限制：同一规范章节新版本复核，合并015不重复计数。

已读关联文档／版本（同一计数组）：
- tools-security-015：2025-11-25；范围：Elicitation form/URL modes, user interaction and completion。[该记录原文](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)
- tools-security-066：2026-07-28；范围：URL Mode; Statefulness; Safe URL Handling; Phishing；补充复核，不新增计数。[该记录原文](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

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

[返回分类目录](README.md#topics)
