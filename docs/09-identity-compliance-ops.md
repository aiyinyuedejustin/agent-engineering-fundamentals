# 09 · 身份、密钥、多租户、合规与运营治理

> 这一章讲 agent 系统上线以后、进了公司以后才会碰到的事：凭证放哪、谁的身份在干活、数据在哪被留了多久、组织怎么统一管、钩子挂了算不算放行、钱在哪一层数、公司网络下 SDK 连不上怎么办。
> MCP 自己的鉴权（OAuth 2.1、PRM、`resource` 参数、token 透传禁令、多用户凭证三种持有方式）在 [05](05-mcp-design-choices.md) 第一节第 6、7 条和决定 5–7，这里只引用不重复。日志脱敏的基本手段见 [04](04-eval-observability-security.md) 第二节第 1 条，按用户限额见 04 第二节第 5 条，错误码和多 key 不能扩容见 [02](02-reliability.md) 第 1 节和第二节第 3 条。
> 源码证据来自 openai/codex（提交 22ebb0fb，2026-10-09 08:04 北京时间）和 aaif-goose/goose（提交 0f476802，2026-10-09 07:24 北京时间）。所有链接、所有具体数字都在 2026-10-09 打开核对过。厂商的数字和功能变动快，用之前再看一眼原文。

---

## 一、知识拆解

### 1. 凭证：有哪几种，各自活多久

一个 agent 系统里同时存在好几类凭证，混在一起管是大部分事故的起点。

| 凭证 | 代表谁 | 典型寿命 | 丢了以后怎么止损 |
| --- | --- | --- | --- |
| 模型厂商 API key | 一个人、一个服务账号，或一个 workspace/project | 不设就长期有效 | 去控制台吊销；GitHub 公开仓库里的部分厂商 key 会被自动吊销（见第 2 节） |
| 用户 OAuth access token | 某个用户，带 scope | 分钟到小时 | 等它过期，或在授权服务器吊销 |
| 用户 OAuth refresh token | 同上 | 天到月，有的会轮换 | 吊销；轮换体系下被重放会触发整条链失效 |
| 工作负载身份换来的短 token | 一个服务账号（由云平台/K8s/CI 身份映射） | 分钟到小时 | 删掉映射规则；不用管 key 轮换 |
| 第三方工具 token（GitHub、Google、Slack…） | 某个用户在第三方的身份 | 各家不同 | 第三方吊销；见 05 决定 7 |
| agent 自己的身份断言 | 某个 agent 实例、某次任务 | 一次任务 | 让签名 key 或任务注册失效 |

**1.1 本地存储（CLI、桌面 agent）**

- Codex 的 `cli_auth_credentials_store` 有四个值（`codex-rs/config/src/types.rs`）：`file`（默认，写 `CODEX_HOME/auth.json`）、`keyring`（系统钥匙串，拿不到就报错）、`auto`（有钥匙串就用，否则退回文件）、`ephemeral`（只在内存，进程退出就没了）。组织可以在 requirements 里锁死这个值（见第 5 节）。
- Codex 的另一套做法（`codex-rs/secrets/src/local.rs`）：密钥本体写成 age/scrypt 加密的文件（`local.age`、`codex_auth.age`、`mcp_oauth.age` 等），只把解密口令放进系统钥匙串，账号名是 `secrets|<codex_home 路径哈希前 16 位>`。好处是钥匙串里只有一个短条目，密钥数量和大小不受钥匙串限制；不同 `CODEX_HOME` 互不串。网关 OAuth 单独用一把口令，注释写明是为了避免并发首次写入时的竞争。
- 密钥分作用域：全局，或者按「环境」（git 仓库根目录名，不在仓库里就用 `cwd-<路径哈希>`）。同一个名字在不同项目可以是不同的值。名字只允许 `A-Z0-9_`，因为最后要变成环境变量。
- goose 默认用系统钥匙串，设了 `GOOSE_DISABLE_KEYRING` 就退回 `~/.config/goose/secrets.yaml` 明文（`crates/goose/src/config/base.rs`）。无头 Linux、容器、CI 里往往没有钥匙串服务，这条退路几乎一定会被走到。
- 环境变量会被子进程继承，所以 shell 工具、MCP stdio 服务器都能看到 agent 的 key（05 决定 5）。key 不进模型上下文的原则见 04 第 3.5 条。

**1.2 交互式登录的两种形态**

- **本机回调（loopback redirect）**：本地起一个 HTTP 服务接授权码。RFC 8252 §7.3 要求授权服务器允许回环地址上的任意端口。但实际上很多授权服务器有固定的重定向白名单：Codex 用固定端口 1455，被占用时先尝试通知旧的登录服务退出，重试 10 次后改用备用端口 1457，源码注释写着「和 Hydra 重定向白名单保持同步」（`codex-rs/login/src/server.rs`）。
- **设备码（device flow，RFC 8628）**：适合 SSH、容器、没有浏览器的机器。客户端按 `interval` 轮询（没给就默认 5 秒），收到 `slow_down` 要在当前间隔上加 5 秒，收到 `authorization_pending` 继续等。goose 的实现在 `crates/goose/src/providers/oauth_device_flow.rs`。

**1.3 刷新：轮换、重放检测、多进程竞争**

- RFC 9700 §4.14：公共客户端的 refresh token 必须做发送方绑定，或者每次刷新都换一个新的（轮换）。轮换体系下，一个已经用过的旧 refresh token 再被提交，授权服务器会把当前有效的那个也作废，合法客户端只能重新登录。
- 这条安全设计在工程上的直接后果：**同一台机器上两个进程（两个终端、IDE 插件加 CLI）同时发现 token 快过期、同时刷新，后到的那个提交的就是「旧」token，于是两边都被踢下线。**
- Codex 的处理（`codex-rs/login/src/auth/manager.rs`）：
  - 收到 401 后，第一步不是刷新，而是**从磁盘重新读一次凭证**，而且只有账号 id 对得上才用（别的进程可能已经刷新过了）；读到的还是旧的，才去刷新；刷新也失败才把错误抛上去。API key 模式什么也不做。
  - 刷新失败区分 `refresh_token_expired`、`refresh_token_reused`、`refresh_token_invalidated`，各给用户一条不同的提示。
  - 永久性失败会被缓存，后面的请求直接失败，不再反复去撞授权服务器。
  - 主动刷新：JWT 快到 `exp`，或者距上次刷新超过 8 天（`TOKEN_REFRESH_INTERVAL = 8`）。
- Google 的 refresh token 会因为这些原因失效（[Google OAuth 2.0 文档](https://developers.google.com/identity/protocols/oauth2)）：用户撤销授权；6 个月没用；带 Gmail scope 时用户改了密码；同一 Google 账号同一 client id 下最多 100 个 refresh token，**超了会静默作废最旧的**；同意屏幕是外部用户且处于 Testing 状态时，refresh token 7 天过期（只要了 openid/email/profile 的除外）；管理员把某个服务设为受限（`admin_policy_enforced`）；GCP 会话控制到期，返回 `invalid_grant` 加 `error_subtype: invalid_rapt`，会话时长可以短到 1 小时。

**1.4 工作负载身份（不存长期 key）**

- 思路：工作负载已经有一个平台签发的身份（K8s 投射的 service account token、云平台元数据服务的身份 token、GitHub Actions OIDC token、SPIFFE JWT-SVID），拿它去换模型厂商的短期 token。OpenAI 的说明：管理员先配三样东西——信任哪个签发方、哪些 token 属性可以映射到哪个服务账号、接收权限的服务账号；交换**不会自动创建**服务账号或 project（[OpenAI Workload identity federation](https://developers.openai.com/api/docs/guides/workload-identity-federation)）。
- Codex 客户端的实现细节（`codex-rs/workload-identity/src/`）：断言文件必须是绝对路径、不超过 16 KiB；grant_type 是 `urn:ietf:params:oauth:grant-type:jwt-bearer`；token 地址必须是 HTTPS 或回环地址；**提前刷新的余量是 min(120 秒, token 寿命的一半)**，短寿命 token 不会因为固定余量太大而一直在刷新；遇到 408/429/5xx 或断言文件暂时不存在这类临时错误，继续用缓存的 token 直到它真过期。

**1.5 谁在干活：委托、冒充和 agent 自己的身份**

- RFC 8693（token exchange）区分两种：**冒充**（拿到的 token 看起来就是用户本人，下游分不出是 agent 干的）和**委托**（token 里用 `act` 声明写明「这个 agent 代表这个用户」，可以一层层嵌套成链；`may_act` 声明谁被允许代表我）。审计和权限收窄都依赖委托。
- MCP 的 Enterprise-Managed Authorization（EMA）把这件事落成了流程：先在企业 IdP 用 RFC 8693 换一个 ID-JAG（`requested_token_type` 是 id-jag，JWT 的 `typ` 是 `oauth-id-jag+jwt`，`aud` 只能有一个，带 `jti` 防重放），再拿它去 MCP 授权服务器用 RFC 7523 jwt-bearer 换 access token；MCP 场景要求带 `resource`。用户不用逐个点同意，企业在 IdP 统一管哪些 agent 能连哪些服务。EMA 在 2026 年 6 月进入 Stable；底下的 ID-JAG 截至 2026-10-09 还是 IETF 草案（-04，2026-05-21），不是 RFC。账号关联先按 `sub`，再按 email。
- Token Vault 模式（Auth0 的叫法）：用户连接第三方时，平台拿到并保存第三方的 access/refresh token，agent 只持有平台自己的 token，**每次要调第三方时再做一次交换**拿当次可用的第三方 token。这样长任务中途 token 过期由平台负责刷新，agent 进程里不留长期第三方凭证。
- agent 自己的身份：Codex 的 `agent-identity` 给每个 agent 运行时一把 ed25519 key，每个任务单独注册并带时间戳签名，下游用 JWKS 按 `kid` 验签，`aud` 固定；还附带一份「物料清单」（agent 版本、harness id、运行位置）。任务 id 只在一次运行内有效。
- OWASP Agentic Top 10（2026）的 ASI03「身份与权限滥用」列的就是这些问题：agent 不加收窄地继承人的权限、凭证被记进记忆里留到下次、多 agent 之间的混淆代理、伪造 agent 身份。给的对策是每个 agent 有独立身份、短期且按任务收窄的 token、每个动作单独授权。

### 2. 组织结构：key 归谁、限额挂在哪

**2.1 Anthropic workspace**（[Workspaces 文档](https://platform.claude.com/docs/en/manage-claude/workspaces)）

- 每个请求只落在一个 workspace，只能访问该 workspace 里的资源（Files、Batches、Skills）。
- key 有三类，人离职时行为不同，这一点最容易出事：
  - **workspace key**（旧式、没有所有者）：建它的人被移除后照样能用。
  - **个人 key**：所有者被移出 workspace 后很快失效；**被移出组织时 key 被归档，重新邀请也不会恢复**。
  - **服务账号 key**：建它的人被移除后照样能用。
  - 所以生产流量绝不能挂在某个员工的个人 key 上，否则这个人离职那天线上就断。
- 多 workspace 的 key 用请求头 `anthropic-workspace-id` 选 workspace。响应头里也会回 `anthropic-workspace-id`、`anthropic-organization-id`、`request-id`，排查「这次请求记到了谁的账上、吃的是谁的限额」靠这个。
- Default Workspace 在 key、用量报表、成本报表里的 `workspace_id` 是 `null`，「所有 workspace 通用」的 key 也是 `null`，要看 key 的 `scope` 字段才分得清。List Workspaces 默认不返回它，要加 `include_default=true`。
- workspace 的花费和速率限额只能比组织低；不设就等于组织的；组织限额永远生效，各 workspace 加起来超过组织限额也没用；Default Workspace 不能设限额。
- **prompt cache 在 Claude API 上按 workspace 隔离，在 Bedrock 和 Google Cloud 上按组织隔离。** 拆 workspace 会降低缓存命中，换云平台会改变隔离边界。
- Claude Code 有一个自动创建的专用 workspace：登录时给每个人铸一把 key，人被移出就失效；它是唯一支持按人每月花费上限的 workspace；把它归档，整个组织就不能用 Console 计费登录 Claude Code 了。
- 管理接口（Admin API）不接受只绑一个 workspace 的 key。

**2.2 OpenAI project**（[Production best practices](https://developers.openai.com/api/docs/guides/production-best-practices)）

- 建议给 project key 设过期时间并定期轮换；管理员可以在组织或 project 级设 key 最长寿命，project 不能超过组织。
- API Key Governance 可以限定只允许建服务账号 key、只允许建用户的 project key，或禁止新建。**这些限制只管新建，已有的 key 不受影响**，收紧策略后要另外清点存量 key。
- 生产和预发拆成不同 project，各设速率和花费限额（与 02 第二节第 3 条一致）。

**2.3 泄露以后**

- GitHub secret scanning 的合作方计划：公开仓库里出现合作方格式的 key，GitHub 会通知厂商，厂商可以自动吊销。截至 2026-10-09 的支持表（[Supported secret scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns)）：OpenAI、Anthropic（API/admin/service/user key）、xAI、OpenRouter、Groq、Azure OpenAI 在合作方列表里；**Google Gemini API key、DeepSeek、Mistral、Cohere、Perplexity、Tavily、Pinecone、LangSmith 不在**。Anthropic 加入时的公告写明只覆盖公开仓库，自动吊销并发邮件。
- 不在列表里的 key、私有仓库、日志、trace、聊天记录里的泄露，都得自己发现自己吊销。
- 落盘前的兜底过滤：Codex 的 `redact_secrets`（`codex-rs/secrets/src/sanitizer.rs`）只用了四条正则——`sk-` 加 20 位以上、`AKIA` 加 16 位、`Bearer` 后 16 位以上、`api_key|token|secret|password` 后接 `:` 或 `=` 再加 8 位以上。它是尽力而为，测试里专门验证了不误伤普通文本。这说明正则过滤只能挡最常见的格式，不能当作唯一防线。

### 3. 数据保留和数据驻留

**3.1 一次请求的数据可能留在哪些地方**

| 位置 | 例子 | 能不能关 |
| --- | --- | --- |
| 厂商滥用监控日志 | OpenAI 默认 30 天 | 需申请 ZDR/MAM |
| 厂商应用状态 | OpenAI Responses 默认留 30 天；Conversations、Assistants、Files、Batch | 看端点，有的不在 ZDR 范围内 |
| 缓存 | prompt cache、结构化输出 schema 缓存、Vertex 内存缓存 24 小时 | 部分可关 |
| 厂商侧工具 | 搜索 grounding、代码执行容器、远程 MCP 连接器 | 多数不在 ZDR 范围内 |
| 你和厂商之间的网关 | OpenRouter、LiteLLM、自建网关的日志 | 自己配 |
| 你自己的系统 | 会话库、trace、日志、向量库、评测集、备份 | 自己负责 |

**3.2 ZDR 不是一个开关，是一张「哪个端点、哪个功能算」的表**

- OpenAI（[Data controls](https://developers.openai.com/api/docs/guides/your-data)）：ZDR/MAM 要审批；开了 ZDR 会强制 `store=false`；Conversations、Assistants、Vector Stores、Files、Batch、Evals 不在 ZDR 范围内；后台模式要存约 10 分钟；**图片和文件输入会做 CSAM 扫描，命中的即使在 ZDR 下也会保留**；prompt cache 的 KV 只在 GPU 本地、最长 24 小时；远程 MCP 的数据走第三方自己的政策；Assistants 对象删除后 30 天清除，不删就一直在。
- Anthropic（[Zero data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)）：ZDR 按组织开，新建的组织要单独开；不覆盖 Console、Managed Agents、消费者应用、Batch（留 29 天）、Files、代码执行（容器留 30 天）、MCP 连接器、agent skills。**ZDR 组织调用不在范围内的功能，请求不会被拦，数据就悄悄留下了**；HIPAA 组织则直接返回 400。strict 工具和结构化输出的 schema 会缓存最长 24 小时，所以 schema 里不能放 PHI。ZDR 组织不支持 CORS（浏览器直连会失败）。被标记的内容最长可留 2 年。走 Bedrock/Vertex 时数据处理方是云厂商。HIPAA 一旦开启不能关，HIPAA 和非 HIPAA 业务要分两个组织。
- Google Vertex（[Vertex AI zero data retention](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention)）：关滥用日志要申请例外；Google 搜索 grounding 留 3 天且不能关（要 ZDR 就换企业版 Web Grounding）；Maps grounding 留 30 天；Interactions API 的 `store` 默认是 true，要手动设 false；内存缓存 24 小时，要在 project 级用 `cacheConfig` 的 `disableCache` 关（对所有区域生效）；Live API 会话恢复留 24 小时。
- Gemini API（[Gemini API 附加条款](https://ai.google.dev/gemini-api/terms)）：免费层的数据会用于训练并有人工审阅；**只有 Cloud project 开了计费才算付费层**；欧洲经济区、瑞士、英国的用户必须用付费层。测试时随手用免费 key 跑真实数据，就是把数据交出去训练。

**3.3 驻留：「在哪处理」和「在哪存」是两件事**

- OpenAI（同上 Data controls）：可以按 project 设，也可以用全局 project 的 key 通过 `us.`/`eu.` 域名前缀按请求设；2026-03-05 及以后发布的模型加价 10%；非美国区域要求 MAM 或 ZDR；**系统数据（包括结构化输出的 schema）不受驻留约束**；澳大利亚、加拿大、日本、印度、新加坡、韩国、英国只做存储驻留，不做本地处理；非美国区域的 Chat Completions 不能设 `store=true`；扩展 prompt 缓存可能在区域外处理；不支持 Assistants 用客户自管密钥（EKM）。
- Anthropic（[Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency)）：请求参数 `inference_geo`（`global`/`us`），响应 `usage.inference_geo` 回显实际在哪推理；只支持 Claude 4.6 及以后的模型，老模型返回 400；**OpenAI SDK 兼容端点不支持**，Bedrock/Vertex 上由端点区域决定；workspace 可以设 `allowed_inference_geos` 和默认值；仅美国推理价格是 1.1 倍；各 geo 共享速率限额。
- Azure OpenAI（[Data, privacy, and security](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy)）：Global 部署可能在任何地理区域处理，DataZone 在区域组内处理；静态数据留在客户的地理区域；Batch 属于 Global 类型；改过滥用监控后可以用 `az cognitiveservices account show` 看 `ContentLogging=false` 确认。
- Bedrock 跨区域推理（[Cross-region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)）：分地理范围 profile 和全球 profile（全球便宜约 10%，全球路由）；SCP 要放行所有目标区域，全球 profile 要放行 `aws:RequestedRegion: "unspecified"`；会路由到账号里没启用的区域；实际区域记在 CloudTrail 的 `additionalEventData.inferenceRegion`。另外 [Bedrock 数据保护](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)说明模型厂商无权访问部署账号，并提醒不要把 PII 写进资源标签和名字（会进计费和诊断日志）。

**3.4 网关也是一个数据处理方**

- 在你和模型厂商中间加一层网关，网关公司就成了额外的处理方，合规清单（子处理方列表、DPA）要加上它。
- OpenRouter（[ZDR](https://openrouter.ai/docs/guides/features/zdr)、[Provider logging](https://openrouter.ai/docs/guides/privacy/provider-logging)）给了一个可以参考的语义：
  - 请求级的 `provider.zdr` 和账号级、guardrail 级设置是「或」关系，**请求参数只能收紧，不能放松**。
  - 某个上游的政策查不清时，按「会保留、会训练」处理。
  - **它把 prompt 内存缓存定义为「不算保留」**，所以 ZDR 路由下仍可能命中有隐式缓存的端点。别家可能定义不同，签合同时要问清楚。
  - ZDR 只管推理路由，不管 web search 等插件和工具。
  - 自带 key 的私有部署默认按「会保留」处理，要你声明；声明只是你的保证，平台不核实。
  - 区域路由用 `eu.`/`us.` 子域名。

**3.5 删除请求**

- 英国 ICO 的被遗忘权指南（[Right to erasure](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/)）有三条对工程影响最大：一个月内响应；**备份里的数据也要处理**，暂时覆盖不掉的要「置于不可用状态」并告诉用户何时真正清除；数据给过别人的，要逐个通知接收方删除。
- 放到 agent 系统里，一次删除要覆盖：会话和消息库；厂商侧有状态的对象（OpenAI Conversations/Responses `store=true`/Files/Vector Stores，Anthropic Files、Batch 结果）；agent 记忆和向量库（嵌入向量也是从个人数据算出来的）；trace 和日志平台；评测集和标注数据；网关日志；备份。厂商侧的对象只有你手里有 id 才删得掉，**所以从第一天就要把「用户 → 厂商侧对象 id」的映射存下来**。

### 4. PII 脱敏放在哪一层

| 层 | 做法 | 代价 |
| --- | --- | --- |
| 发给模型之前（客户端或你的后端） | 识别并替换成占位符 | 模型看不到原值，起草邮件、填表这类要用名字的任务会做坏；识别漏掉的照样发出去 |
| 网关 | 统一过滤所有出站请求 | 不知道业务语义，误杀和漏网都更多；网关自己要看到明文 |
| trace/日志导出（SDK 或 Collector） | 落盘前删字段、哈希、打码（04 第二节第 1 条） | 不影响模型质量，但厂商那边照样收到原文 |
| 存储 | 加密、限权限、设保留期 | 只降低泄露面，不减少流向 |

- Presidio 的文档首页直接写：基于自动检测，**不保证找全所有敏感信息**，要配合其他保护（[Presidio docs](https://github.com/data-privacy-stack/presidio/blob/main/docs/index.md)）。
- 可逆脱敏：Presidio 的匿名化支持 replace、mask、redact、encrypt，并提供 Deanonymize 把加密的值还原（[Presidio anonymizer](https://github.com/data-privacy-stack/presidio/blob/main/docs/anonymizer/index.md)）。agent 场景常用的做法是：发出前把「张三」换成稳定的占位符（同一会话里同一个人始终是同一个占位符），模型的输出和工具调用参数在执行前再换回原值。占位符要稳定，否则模型会把一个人当成两个人。
- 工具调用参数也要还原：模型让你给 `<PERSON_1>` 发邮件，执行层要知道它是谁；反过来工具结果里新出现的 PII，进上下文之前又要脱一次。

### 5. 配置分层与组织下发

- Codex 的层级和优先级（`codex-rs/config/src/config_layer_source.rs`，数字越大越优先）：内置默认 -10、MDM 0、系统 10、企业托管 15、用户 20（profile 21）、项目 25、会话参数 30、旧版托管文件 40、旧版 MDM 50。
- Codex 把组织下发分成两种（[Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration)）：
  - **requirements（约束）**：用户改不了。字段有 `allowed_login_methods`、`allowed_chatgpt_workspaces`、`cli_auth_credentials_store`、`allowed_approval_policies`、`allowed_sandbox_modes`、`allowed_permission_profiles`、`allow_managed_hooks_only`、`mcp_servers`、`rules`、`enforce_residency` 等。冲突时退回兼容的值并提示。`mcp_servers` 按名字加身份（命令或 URL）放行；字符串形式的命令不检查参数和环境变量；空列表等于全禁。`allowed_permission_profiles` 没列的都禁，包括以后新加的内置 profile。requirements 里的规则只能是 prompt 或 forbidden，不能是 allow（源码 `requirements_exec_policy.rs`）。
  - **defaults（默认值）**：`managed_config.toml`，每次启动重新套用，用户会话中可以改。
  - 位置：`/etc/codex/requirements.toml`，或 MDM 的 `requirements_toml_base64`、`config_toml_base64`。文档提醒不要把密钥放进 MDM 载荷。
  - 云端下发的 requirements 拉取失败且没有有效缓存时**报错拒绝启动（fail closed）**；缓存带签名、绑定身份；后台刷新不会改正在运行的进程。登录相关的约束只能放本地，因为它们在登录之前就要生效。
  - 0.137 及以前的旧客户端会忽略新字段，要等全员升级后新约束才算真正生效。
  - 驻留约束最终落在请求头 `x-openai-internal-codex-residency: us` 上（`model-provider-info`）。
  - 网络白名单不管 web search、MCP、连接器，这些有各自的开关；按主机名匹配「不等于设备认证」。
- Claude Code（[Settings](https://code.claude.com/docs/en/settings)）：优先级 managed > 命令行 `--settings` > 项目 local > 项目共享 > 用户。数组类设置跨层合并，有顺序的列表（如 `fallbackModel`）整个取一层。**managed 里设的 model 只是默认值，不是锁**，要锁用 `availableModels`。更严格的值从任何层来都生效（文档有例外表）。项目文件不能把 `defaultMode` 设成 `bypassPermissions`/`auto`，项目文件里的遥测导出环境变量会被忽略。仓库里的 allow 规则要等用户信任该目录后才生效，deny/ask 立即生效。设置会热加载，但部分键只在启动时读。换模型会丢掉 prompt cache。

### 6. 策略钩子（hooks）

- 事件点：Codex 和 Claude Code 基本一致——PreToolUse、PermissionRequest、PostToolUse、压缩前后、SessionStart、UserPromptSubmit、子 agent 开始/结束、Stop 等。Codex 的 hooks 输出结构沿用 Claude Code 的格式，输出结构开了 `deny_unknown_fields`，PermissionRequest 里预留的字段（`updated_input`、`updated_permissions`、`interrupt`）出现就按失败处理（fail closed）。结果分三类：Success、FailedContinue、FailedAbort（`codex-rs/hooks/src/`）。
- Claude Code 的语义（[Hooks reference](https://code.claude.com/docs/en/hooks)）：
  - **只有退出码 2 会拦截，退出码 1 是「非阻塞错误」，照样放行。**
  - 脚本路径写错，等于这道闸没了，而且不报错。
  - command/http/mcp_tool 类 PreToolUse 钩子超时不拦截（SDK 回调超时会拦截）。默认超时：command/http/mcp_tool 600 秒，prompt 30 秒，agent 60 秒，UserPromptSubmit 30 秒；SessionEnd 只有 1.5 秒。
  - 匹配到的多个钩子并行执行并去重，没有顺序保证。
  - `updatedInput` 是整体替换，不是合并；替换后权限规则会对新输入重新判一次。
  - 钩子返回 allow 也绕不过 deny/ask 规则。
  - JSON 不符合 schema 算非阻塞错误。
- Codex 文档同样写明 PreToolUse 回调出错、超时、输出格式不对时可能不拦截。
- 结论：**钩子默认是 fail open 的**。真要「拦住」的东西，要么写成 deny 规则或 requirements，要么在钩子里把所有异常路径都收敛到「明确返回拒绝」，并用 `allow_managed_hooks_only` 一类开关防止用户自带钩子。

### 7. 预算和计数

- 限额有三层：厂商的组织/project/workspace 限额（[02](02-reliability.md) 第一节「限流」和第二节第 3 条），网关的按 key/团队/用户预算，你自己应用里的按用户限额（04 第二节第 5 条）。它们各管一段，不能互相替代：厂商限额只认 key，不认你的终端用户。
- LiteLLM 的预算（[Users & budgets](https://docs.litellm.ai/docs/proxy/users)）把几个坑写得很清楚：
  - 预算要有 Postgres；**没数据库时设了 `max_budget` 也不生效，只在启动时打一行警告**。
  - 用团队 key 时只检查团队和成员预算。
  - **预留（reservation，默认开）**：调用前按 `max_tokens` 或模型上限估最大花费并先扣，调用后用实际花费替换。
  - Batch 无法事先定价。
  - 热路径计数在 Redis；重启后读到旧快照会让花费超出预算，除非打开 `fail_closed_budget_enforcement`。
  - 可以同时设日和月等多个窗口。
  - 把成员预算调到低于已花金额，会立刻拦住。
- 并发：在途请求数要在同一层计数和释放；流式请求要在流结束或断开时释放，否则泄漏的计数会把用户永久卡住（分布式计数的做法见 02 决定 5）。

### 8. 企业网络：代理和证书

- 现象：在公司网络里，SDK 报 `self signed certificate in certificate chain` 或 `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`，原因是 TLS 检查代理用公司自己的根证书重新签了证书，而运行时只信自带的根证书包。
- Node（[Node.js CLI](https://nodejs.org/api/cli.html)）：
  - `NODE_EXTRA_CA_CERTS` 只在启动时读，代码里显式传了 `ca` 选项它就被忽略，setuid 进程也忽略。
  - `--use-system-ca` 从 v23.8.0 加入（非 Windows/macOS 是 v23.9）；环境变量 `NODE_USE_SYSTEM_CA=1` 从 v24.6.0/v22.19.0 起支持。
  - **Node 默认不读 `HTTP_PROXY`**，要设 `NODE_USE_ENV_PROXY=1`（v24.0.0/v22.21.0 起）或在代码里配代理 agent。
- Python：
  - httpx 默认 `trust_env`，`SSL_CERT_FILE` 会替换默认证书位置（[httpx 环境变量](https://www.python-httpx.org/environment_variables/)）。
  - requests 用 `REQUESTS_CA_BUNDLE`；用 prepared request 发送时不读环境变量，除非调用 `merge_environment_settings`（[requests advanced](https://requests.readthedocs.io/en/latest/user/advanced/)）。
  - truststore 让 Python 用系统信任库而不是 certifi，需要 3.10+；`inject_into_ssl` 只该在应用里调用，库不该调用（[truststore](https://truststore.readthedocs.io/en/latest/)）。
- Claude Code（[Network configuration](https://code.claude.com/docs/en/network-config)）：
  - 支持 `HTTPS_PROXY`/`NO_PROXY`，不支持 SOCKS；NTLM/Kerberos 代理要改走 LLM 网关。
  - 信任内置的 Mozilla 根证书加系统证书库（npm 安装要 Node 22.15+），也认 `NODE_EXTRA_CA_CERTS`。
  - mTLS 证书轮换后，在连接出错时重新读取。
  - **后台常驻进程继承的是第一个启动它的 shell 的环境变量**，所以代理和证书变量要写进 settings，不要只靠 shell。
  - 云端会话忽略 settings 里的证书变量。
- goose（`crates/goose/src/config/tls.rs`）：`GOOSE_CLIENT_CERT_PATH` 和 `GOOSE_CLIENT_KEY_PATH` 必须成对设置，只设一个直接报错退出；自定义 CA 用 `GOOSE_CA_CERT_PATH`。

### 9. 审计与归因

- 一条可追责的记录至少要回答：哪个终端用户、哪个 agent/任务、用的哪个凭证（key id、workspace/project）、放行决定来自配置还是人。
- Codex 的 OTel 事件 `codex.tool_decision` 记录批准或拒绝，**以及这个决定来自配置还是用户**；`codex.user_prompt` 默认只记长度，内容要显式打开 `log_user_prompt` 才记（[Codex advanced config](https://learn.chatgpt.com/docs/config-file/config-advanced)）。
- 把厂商回给你的 id 存下来：Anthropic 的 `request-id`、`anthropic-workspace-id`；Bedrock 在 CloudTrail 里记实际推理区域。
- 委托 token 里的 `act` 链（第 1 节）是跨系统归因的唯一标准做法；冒充式 token 下，下游日志里全是「用户本人」。

---

## 二、文章很少讲但常碰到的事

1. **生产流量挂在员工个人 key 上，人一离职线上就断。** Anthropic 的个人 key 在人被移出组织时归档，重新邀请也不恢复；服务账号 key 和旧式 workspace key 不受影响（第 2 节）。
2. **两个进程同时刷新 token，两边一起被踢下线。** 轮换加重放检测的安全设计（RFC 9700）碰上同机多进程就会这样。做法：401 后先从磁盘重读、账号对得上就用，没变才刷新；刷新时加文件锁（第 1 节）。
3. **Google 的 refresh token 会无声失效。** Testing 状态 7 天、每账号每 client 100 个上限超了静默作废最旧的、`invalid_rapt` 会话控制最短 1 小时。开发期一切正常，换了一批测试账号或上线前没改发布状态就出问题（第 1 节）。
4. **ZDR 下调用不在范围内的功能，Anthropic 不报错，数据就留下了。** HIPAA 组织才会 400。OpenAI 也有一整列不在 ZDR 范围内的端点，CSAM 扫描命中的图片即使在 ZDR 下也留（第 3 节）。所以合规要靠你自己的出站白名单，不能靠厂商报错。
5. **驻留会被悄悄打破。** Azure/Bedrock 的 Global 类部署全球路由；Anthropic 的 `inference_geo` 在 OpenAI 兼容端点上不生效；OpenAI 的结构化输出 schema 属于系统数据，不受驻留约束（第 3 节）。要检查实际落点：Anthropic 看 `usage.inference_geo`，Bedrock 看 CloudTrail。
6. **schema 里不能放敏感数据。** Anthropic 会把 strict 工具和结构化输出 schema 缓存最长 24 小时；OpenAI 把 schema 当作系统数据、不在驻留范围内。把枚举值写成客户名单、把示例写成真实病例，都是在把 PII 放进不受保护的地方（第 3 节）。
7. **钩子默认放行。** Claude Code 只有退出码 2 拦截，脚本抛异常（退出码 1）、超时、路径写错都会放行（第 6 节）。很多人写的「安全钩子」实际只在一切正常时才拦得住。
8. **组织策略要 fail closed，个人钩子是 fail open，两者不能混用。** Codex 拉不到云端 requirements 又没有缓存就拒绝启动；而钩子出错就放行。要「一定拦住」的东西放进前者（第 5、6 节）。
9. **收紧 key 策略只管新 key。** OpenAI 的 Key Governance 不影响存量 key；GitHub 自动吊销只覆盖部分厂商、只覆盖公开仓库（第 2 节）。收紧后必须清点存量。
10. **网关预算没配数据库就不生效。** LiteLLM 没有 Postgres 时 `max_budget` 只打一行警告；Redis 计数在重启后可能是旧值，会超支（第 7 节）。上线前要做一次「真的会被拦住吗」的测试。
11. **预算要先预留再结算。** 调用前按 `max_tokens` 估最大花费先扣，结束后按实际花费退差。只在调用后记账，并发一高就会集体超支。这也是 `max_tokens` 不能随手设成模型上限的另一个原因（02 决定 11）。
12. **Node 默认不走 `HTTP_PROXY`。** Python 的 httpx/requests 默认会读，Node 要 `NODE_USE_ENV_PROXY=1` 或代码里配。同一套环境变量，Python 写的工具能连上，Node 写的 MCP 服务器连不上（第 8 节）。
13. **后台进程用的是「第一次启动它时」的环境。** Claude Code 的后台常驻进程继承第一个启动它的 shell 的环境变量，之后在别的终端改代理变量不生效（第 8 节）。所有常驻的 agent 守护进程都有这个问题。
14. **托管配置里的 model 不是锁。** Claude Code managed settings 里的 model 只是默认值，用户能换；要锁得用 `availableModels`。Codex 也分 requirements 和 defaults（第 5 节）。
15. **旧客户端看不懂新约束，就当没有。** Codex 0.137 及以前会忽略新的 requirements 字段（第 5 节）。下发新约束前先确认全员版本。
16. **免费 key 的数据会拿去训练。** Gemini API 只有绑定了计费的 project 才算付费层（第 3 节）。测试环境用免费 key 跑真实客户数据，是一个常见的合规事故。
17. **prompt cache 的隔离边界随部署方式变。** Anthropic 在自家 API 上按 workspace 隔离，在 Bedrock/Vertex 上按组织隔离（第 2 节）。拆 workspace 会降低命中率；多租户共享一个组织时，要知道缓存边界在哪。
18. **删除请求的难点是厂商侧对象的 id。** 不保存「用户 → 厂商侧 file/conversation/batch id」的映射，删除请求来了也删不掉；备份要「置于不可用」，接收方要逐个通知（第 3 节）。
19. **本地登录回调端口被占。** RFC 说回环地址可以用任意端口，但很多授权服务器只放行固定端口。上一次登录没退出的残留进程会占着端口，要先通知它退出，再退到备用端口（第 1 节）。
20. **无头环境没有钥匙串。** 容器、CI、SSH 机器上，「默认用钥匙串」的工具会退回明文文件或直接报错。要事先决定这些环境用哪种凭证：工作负载身份、环境变量注入，还是内存态（第 1 节、1.4）。

---

## 三、要拿的主意

### 决定 1：凭证存在哪

- **问题**：本地 agent（CLI、桌面）的 key 和 OAuth token 放在哪。
- **选项**：系统钥匙串；加密文件（口令放钥匙串）；明文文件（权限 600）；仅内存；环境变量。
- **代价**：钥匙串在无头 Linux/容器里常常没有，条目大小和数量也有限；加密文件多一层复杂度，但能放多个、能按项目分；明文文件最省事，泄露面最大；仅内存每次都要重新登录；环境变量会被所有子进程继承（05 决定 5）。
- **怎么选**：桌面默认钥匙串，拿不到就退回加密文件（Codex 的做法），并在日志里说明退到了哪一级；无头环境优先工作负载身份，其次是平台注入的短期环境变量；共享机器、演示环境用仅内存。不要静默退回明文。

### 决定 2：服务账号还是用户委托

- **问题**：agent 调下游系统时用谁的身份。
- **选项**：共享服务账号；用户 OAuth 委托（存每个用户的 refresh token）；token exchange 委托（带 `act`）；企业 IdP 统一管的 ID-JAG/EMA。
- **代价**：服务账号最简单，但下游看不出是哪个用户，权限通常过大，用户之间会互相看到数据（混淆代理，见 05 第一节第 7 条和决定 7）；用户 OAuth 要管刷新和失效（第 1 节），每个第三方都要单独做一次；token exchange 需要 IdP 支持；EMA 截至 2026-10 还依赖草案，IdP 支持有限。
- **怎么选**：读写的是用户自己的数据，就用用户委托；后台批处理、跟具体用户无关的数据，用服务账号，并通过工作负载身份拿短期 token；企业客户要求统一管控，就上 EMA。不管哪种，都要让下游日志能看出「哪个 agent 代表哪个用户」。

### 决定 3：任务跑到一半 token 过期怎么办

- **问题**：长任务（几十分钟到几小时）比 access token 寿命长。
- **选项**：任务开始时拿一次 token 一直用；每次调用前检查并按需刷新；用 Token Vault 类服务每次调用现换；失败后才刷新。
- **代价**：开始时拿一次一定会在中途过期；每次检查要处理多进程竞争；Token Vault 多一个依赖和一次网络往返；只靠失败后刷新，非幂等操作可能已经执行了一半。
- **怎么选**：调用前主动刷新（余量取 min(固定值, 寿命/2)），401 后按「重读磁盘 → 刷新 → 抛错」走一次（第 1 节），永久失败要缓存并通知用户重新授权，而不是让任务无限重试。多进程或多实例共用同一份凭证时，把刷新集中到一个地方（凭证代理或 vault）。refresh token 彻底失效时，任务要能暂停并等待用户重新授权，而不是直接失败丢掉进度。

### 决定 4：哪些功能和 ZDR/驻留冲突，网关算不算处理方

- **问题**：客户要求零保留或限定区域，系统里哪些东西要关、换或者加合同。
- **选项**：只用厂商的 ZDR 范围内端点；关掉不在范围内的功能（Batch、Files、托管代码执行、远程 MCP 连接器、搜索 grounding、有状态会话）；换到云厂商托管（Bedrock/Vertex/Azure）；经网关做 ZDR 路由。
- **代价**：关功能就少能力；换云厂商托管会改变处理方、价格、限额和缓存边界；加网关多一个处理方要签 DPA，而且它对「保留」的定义（是否包含缓存）可能和客户理解的不同。
- **怎么选**：先列出系统用到的每个厂商功能，逐个对照厂商的 ZDR 表和驻留表（第 3 节），在出站层加白名单拦掉不在范围内的调用（因为 Anthropic 不会替你报错）；网关一律算处理方，写进子处理方列表；Global 类部署在有驻留要求时禁用（Bedrock 用 SCP，Azure 选 DataZone/区域部署）。

### 决定 5：删除请求要删什么

- **问题**：用户要求删除数据。
- **选项**：只删自己数据库；连同厂商侧对象一起删；连同备份、trace、评测集一起处理。
- **代价**：只删自己库不满足法规要求；删厂商侧对象需要事先存 id；备份通常没法单条删。
- **怎么选**：按 3.5 的清单删除，并在设计时就做好三件事：存「用户 → 厂商侧对象 id」映射；trace/日志按用户 id 可查可删，或者干脆不存内容；备份有固定的轮换周期，并对用户说明「备份在 N 天内覆盖」。尽量用 `store=false` 和短保留期，从源头减少要删的地方。

### 决定 6：PII 脱敏放哪一层

- **问题**：敏感数据要不要发给模型，在哪里拦。
- **选项**：发送前不可逆替换；发送前可逆占位、执行时还原；只在日志/trace 导出时脱敏；不脱敏，靠合同（ZDR、BAA）。
- **代价**：不可逆替换会让需要真实值的任务做不了；可逆占位要维护映射表，工具参数和结果都要转换；只在导出时脱敏，厂商仍然拿到原文；只靠合同，要接受厂商侧的保留例外（CSAM 扫描、被标记内容）。
- **怎么选**：日志/trace 导出时脱敏是必做的底线（04 第二节第 1 条）；模型不需要真实值的字段（证件号、卡号）在发送前不可逆替换；需要真实值又不能外发的（人名、地址），用稳定的可逆占位符；所有自动识别都不保证找全（Presidio 原话），高风险场景要配合数据分级和出站白名单。

### 决定 7：组织策略怎么下发

- **问题**：公司要统一管员工的 agent 设置。
- **选项**：只发默认值；发不可改的约束；在网关和网络层强制；三者叠加。
- **代价**：默认值用户能改；约束要客户端支持，旧版本会忽略；网关和网络层只能管出站流量，管不到本地工具和文件读写。
- **怎么选**：安全相关的（登录方式、允许的审批/沙箱模式、MCP 白名单、驻留、只用托管钩子）发约束；偏好类（默认模型、默认提示）发默认值；约束拉取失败要 fail closed；配合 MDM 强制客户端最低版本；凭证不放进 MDM 载荷。

### 决定 8：钩子的超时和错误语义怎么定

- **问题**：自己写的策略钩子在出错、超时、输出格式不对时，放行还是拦截。
- **选项**：fail open（出错放行）；fail closed（出错拦截）；按钩子分级。
- **代价**：fail open 意味着钩子的服务挂了，安全检查就没了；fail closed 意味着钩子的服务挂了，所有人都干不了活。
- **怎么选**：安全检查类（禁止删库、禁止外发）要 fail closed：在脚本里用 try/catch 把所有异常收敛成「明确拒绝」（Claude Code 里就是退出码 2），给出比工具更短的超时，并且要监控钩子的错误率；记录、通知、格式化类钩子 fail open。能写成静态 deny 规则的就不要写成钩子。

### 决定 9：预算和并发在哪一层数

- **问题**：防止单个用户或单个租户把钱烧光。
- **选项**：只靠厂商的 project/workspace 限额；网关按 key/团队预算；应用层按终端用户预算；多层叠加。
- **代价**：厂商限额只认 key，一个用户刷爆了所有人一起停；网关多一个组件，计数依赖数据库和 Redis；应用层要自己做预留和结算。
- **怎么选**：厂商层按环境/业务拆 workspace/project 设上限，作为最后的保险；终端用户的预算在应用层或网关层做，**先预留后结算**，计数存储不可用时 fail closed；Batch 这类无法预先定价的单独设额度；多窗口（日/月）同时设。

### 决定 10：企业网络下 SDK 怎么连出去

- **问题**：客户环境有 TLS 检查代理和自签根证书。
- **选项**：每个运行时分别配 CA 文件；让运行时读系统证书库；所有出站走公司的 LLM 网关。
- **代价**：分别配 CA，每种语言、每个进程的变量都不一样，容易漏（Node 默认连代理变量都不读）；读系统证书库要较新的运行时版本；走网关要多部署一个组件，但代理认证（NTLM/Kerberos）和证书问题只在网关处理一次。
- **怎么选**：能用系统证书库就用（Node `NODE_USE_SYSTEM_CA=1`、Python truststore），代理变量写进应用配置而不是只依赖 shell；NTLM/Kerberos 代理、或者 agent 要拉起多种语言的子进程（MCP 服务器）时，统一走网关。上线前在客户网络里专门测一遍「子进程是否继承了代理和 CA 设置」。

---

## 四、资料清单

（全部在 2026-10-09 打开核对。）

**规范和标准**
- [RFC 9700 OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)：规范；1.3；§4.14 规定了 refresh token 轮换和重放检测，是多进程刷新竞争的根源。
- [RFC 8252 OAuth 2.0 for Native Apps](https://www.rfc-editor.org/rfc/rfc8252)：规范；1.2；§7.3 回环重定向要允许任意端口，可以对照现实中固定端口的做法。
- [RFC 8628 Device Authorization Grant](https://www.rfc-editor.org/rfc/rfc8628)：规范；1.2；无浏览器登录的轮询间隔、`slow_down` 和 `authorization_pending` 的语义。
- [RFC 8693 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693)：规范；1.5、9；委托和冒充的区分，以及 `act`/`may_act` 的写法，是 agent 归因的基础。
- [MCP Enterprise-Managed Authorization](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization)：规范；1.5；企业 IdP 统一授权 agent 连 MCP 服务器的完整流程。
- [Identity Assertion JWT Authorization Grant（IETF 草案）](https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/)：草案；1.5；ID-JAG 的格式和校验规则，用来确认它目前仍是草案。
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)：风险清单；1.5；ASI03 把 agent 的身份和权限问题分类列出，并给出对策，适合做评审检查表。
- [ICO: Right to erasure](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/)：监管指南；3.5；讲清一个月期限、备份「置于不可用」和通知接收方三件事。

**厂商文档：身份和组织**
- [Anthropic Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)：说明；2.1；三类 key 在人员移除时的不同行为、Default Workspace 的 `null` id、缓存隔离边界、限额层级。
- [OpenAI Production best practices](https://developers.openai.com/api/docs/guides/production-best-practices)：说明；2.2；key 最长寿命、Key Governance 只管新 key、按环境拆 project。
- [OpenAI Workload identity federation](https://developers.openai.com/api/docs/guides/workload-identity-federation)：说明；1.4；不存长期 key 的信任模型，交换不会自动创建主体。
- [Google OAuth 2.0 文档](https://developers.google.com/identity/protocols/oauth2)：说明；1.3；refresh token 失效原因的完整列表（7 天、100 个上限、`invalid_rapt`）。
- [Auth0 Token Vault](https://auth0.com/docs/secure/call-apis-on-users-behalf/token-vault)：产品说明；1.5、决定 3；「平台保存第三方 token、agent 每次现换」的模式。
- [WorkOS：MCP Enterprise-Managed Authorization 与 ID-JAG](https://workos.com/blog/mcp-enterprise-managed-authorization-id-jag)：分析；1.5；把 EMA 两步交换讲得比规范好懂，并说明了 IdP 支持现状。

**厂商文档：数据保留和驻留**
- [OpenAI Data controls](https://developers.openai.com/api/docs/guides/your-data)：说明；3.2、3.3；按端点列出的保留和 ZDR 资格表、驻留的区域和例外（schema 属于系统数据）。
- [Anthropic Zero data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)：说明；3.2；哪些功能不在 ZDR 范围、ZDR 不拦截而 HIPAA 拦截、schema 缓存 24 小时。
- [Anthropic Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency)：说明；3.3；`inference_geo` 的用法、限制和价格。
- [Vertex AI zero data retention](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/zero-data-retention)：说明；3.2；grounding、缓存、Interactions `store` 默认值这些容易漏的保留点。
- [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms)：条款；3.2；免费层和付费层的数据使用差别，以及「开了计费才算付费」。
- [Azure OpenAI Data, privacy, and security](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy)：说明；3.3；Global/DataZone 部署的处理位置和滥用监控的核对方法。
- [Amazon Bedrock Cross-region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)：说明；3.3；跨区域 profile 的路由范围、SCP 写法和 CloudTrail 字段。
- [Amazon Bedrock Data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)：说明；3.3；模型厂商无法访问部署账号，以及标签和名字里不要放 PII。
- [OpenRouter Zero Data Retention](https://openrouter.ai/docs/guides/features/zdr)：说明；3.4；网关层 ZDR 的语义（只能收紧、缓存不算保留、工具不覆盖、未知按保留）。
- [OpenRouter Provider Logging](https://openrouter.ai/docs/guides/privacy/provider-logging)：说明；3.4；各上游的保留和训练政策总表，以及区域路由。

**治理、钩子、预算**
- [Codex Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration)：说明；5、6；约束和默认值的区别、fail closed 拉取、旧客户端忽略新字段、网络白名单的边界。
- [Claude Code Settings](https://code.claude.com/docs/en/settings)：说明；5；各层的优先级和合并规则，「managed 的 model 不是锁」这类例外。
- [Claude Code Hooks reference](https://code.claude.com/docs/en/hooks)：说明；6；退出码、超时、并行、`updatedInput` 替换语义，钩子 fail open 的依据。
- [Codex Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)：说明；9；OTel 事件里记录决定来源和默认不记提示内容的做法。
- [LiteLLM Users & budgets](https://docs.litellm.ai/docs/proxy/users)：说明；7；预留后结算、没数据库不生效、Redis 旧快照超支等预算实现细节。

**泄露和脱敏**
- [GitHub Supported secret scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns)：参考表；2.3；哪些 LLM 厂商的 key 会被自动报告和吊销，哪些不会。
- [GitHub Changelog：Anthropic 成为 secret scanning 合作方](https://github.blog/changelog/2024-08-20-anthropic-is-now-a-github-secret-scanning-partner/)：公告；2.3；说明范围只有公开仓库，处理方式是自动吊销加邮件。
- [Claude API key best practices](https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure)：说明；2.3；厂商对 key 存放和泄露处理的官方建议。
- [Presidio 文档首页](https://github.com/data-privacy-stack/presidio/blob/main/docs/index.md)：说明；4；明确写着「不保证找全」。
- [Presidio Anonymizer](https://github.com/data-privacy-stack/presidio/blob/main/docs/anonymizer/index.md)：说明；4；replace/mask/redact/encrypt 和可逆还原的接口。

**企业网络**
- [Claude Code Network configuration](https://code.claude.com/docs/en/network-config)：说明；8；代理、CA、mTLS 轮换、后台进程继承环境变量。
- [Node.js CLI options](https://nodejs.org/api/cli.html)：参考；8；`NODE_EXTRA_CA_CERTS`、`NODE_USE_SYSTEM_CA`、`NODE_USE_ENV_PROXY` 的版本和生效条件。
- [truststore](https://truststore.readthedocs.io/en/latest/)：说明；8；Python 用系统证书库，以及只能在应用里注入。
- [httpx Environment Variables](https://www.python-httpx.org/environment_variables/)：参考；8；`trust_env` 和 `SSL_CERT_FILE` 的行为。
- [Requests Advanced Usage](https://requests.readthedocs.io/en/latest/user/advanced/)：参考；8；`REQUESTS_CA_BUNDLE`，以及 prepared request 不读环境变量。

**源码（提交见文首）**
- [openai/codex `codex-rs/login`](https://github.com/openai/codex/tree/main/codex-rs/login)：源码；1.2、1.3；固定回调端口和备用端口、401 后先重读磁盘再刷新、刷新失败分类和缓存。
- [openai/codex `codex-rs/secrets`](https://github.com/openai/codex/tree/main/codex-rs/secrets)：源码；1.1、2.3；加密文件加钥匙串口令的存储方式、按环境分作用域、`redact_secrets` 的正则。
- [openai/codex `codex-rs/workload-identity`](https://github.com/openai/codex/tree/main/codex-rs/workload-identity)：源码；1.4；断言文件限制、提前刷新余量、临时错误时继续用缓存。
- [openai/codex `codex-rs/agent-identity`](https://github.com/openai/codex/tree/main/codex-rs/agent-identity)：源码；1.5；按任务签名的 agent 身份和物料清单。
- [openai/codex `codex-rs/config`](https://github.com/openai/codex/tree/main/codex-rs/config)：源码；1.1、5；凭证存储模式、配置层优先级、requirements 字段和「规则不能是 allow」。
- [openai/codex `codex-rs/hooks`](https://github.com/openai/codex/tree/main/codex-rs/hooks)：源码；6；钩子结果分类、严格的输出解析和预留字段 fail closed。
- [block/goose `crates/goose/src/config`](https://github.com/aaif-goose/goose/tree/main/crates/goose/src/config)：源码；1.1、8；钥匙串退回明文文件、mTLS 证书和 key 必须成对。
- [block/goose `oauth_device_flow.rs`](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/providers/oauth_device_flow.rs)：源码；1.2；设备码轮询的完整实现。

---

## 五、阅读顺序

1. 先读 [05](05-mcp-design-choices.md) 第一节第 6、7 条（MCP 鉴权），本章默认你已经知道 OAuth 2.1 和 token 透传禁令。
2. 读 OWASP Agentic Top 10 的 ASI03，建立「agent 身份和权限会出哪些问题」的整体印象。
3. 读 RFC 8693 的 delegation/impersonation 部分和 MCP EMA 页面（配合 WorkOS 那篇），弄清委托链怎么表达。
4. 读 RFC 9700 §4.14，然后看 Codex `login/src/auth/manager.rs` 的 401 恢复逻辑，理解刷新竞争和对应的解法；再看 Google OAuth 文档的 refresh token 失效列表。
5. 读 Anthropic Workspaces 和 OpenAI Production best practices，定下组织结构、key 类型和限额怎么挂。
6. 读三家的数据文档：OpenAI Data controls、Anthropic ZDR 和 Data residency、Vertex ZDR。边读边列出自己系统用到的功能，逐个对照。再读 Azure 和 Bedrock 跨区域文档、OpenRouter ZDR，补上「部署方式」和「网关」两个变量。
7. 读 ICO 被遗忘权指南，对照 3.5 的清单检查自己的存储。
8. 读 Codex Managed configuration 和 Claude Code Settings、Hooks，重点看约束/默认值的区别和钩子 fail open 的条件。
9. 读 LiteLLM 预算文档，哪怕不用 LiteLLM，也可以照着检查自己的预算实现。
10. 最后按需查企业网络部分：Claude Code Network configuration、Node CLI、truststore、httpx、requests。
