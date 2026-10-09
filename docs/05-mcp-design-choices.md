# 05 · MCP：协议基础与会影响设计的取舍

> MCP（Model Context Protocol，让 agent 应用统一接入外部工具和数据的协议）。本章只讲会让你在设计时选 A 不选 B 的知识。
> 规范以 2026-07-28 版为准（截至 2026-10-09 是 modelcontextprotocol.io 上 `latest` 指向的版本），和旧版不同的地方单独标出。资料核对时间：2026-10-09。

---

## 一、知识拆解

### 1. 心智模型：host、client、server

- MCP 里有三个角色：**host**（你的 agent 应用，比如 Claude Code、Cursor、你自己写的服务）、**client**（host 里负责连一个服务器的连接对象，一个服务器对应一个 client）、**server**（提供工具和数据的那一方）。
- 对模型来说，MCP 是不存在的。模型看到的永远只是 function calling 的工具定义和工具结果。MCP 解决的是「工具从哪来、怎么发现、怎么调用、怎么鉴权」这层分发和接入的问题，不解决「模型会不会用工具」。

出处：[Architecture overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)、[2026-07-28 Key Changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

### 2. 消息格式：JSON-RPC 2.0

- 三种消息：请求（有 `id`，要求回复）、响应（同一个 `id`，带 `result` 或 `error` 之一）、通知（没有 `id`，不回复）。错误码有约定区间：-32700 解析错、-32600 请求无效、-32601 方法不存在、-32602 参数无效、-32603 内部错误。
- 用 `id` 配对请求和响应，并发时不能假设响应按顺序回来；通知发错了也不会有任何反馈。
- 2026-07-28 版起，每个请求在 `_meta` 里带协议版本、客户端能力、客户端身份（`io.modelcontextprotocol/protocolVersion` 等）。

出处：[JSON-RPC 2.0](https://www.jsonrpc.org/specification)

### 3. 两种传输：stdio 与 Streamable HTTP

- stdio：客户端把服务器作为子进程启动，通过标准输入输出逐行收发 JSON。服务器往 stdout 打任何非协议内容（比如调试 print）都会破坏协议，日志必须写 stderr；服务器继承客户端进程的环境变量和权限，等于在你机器上跑第三方代码。
- Streamable HTTP：客户端 POST JSON-RPC 请求，服务器可以直接返回 JSON，也可以用 SSE（服务器单向推送事件流）返回进度和结果。要校验 Origin 防 DNS 重绑定，本地服务只绑 127.0.0.1，要做鉴权；2026-07-28 版已去掉流断线续传，断了要用新 id 重发请求，所以有副作用的工具要考虑幂等（做法见 [02](02-reliability.md) 第 6 节）。

出处：[Transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)、[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)、[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)

### 4. 版本与能力协商

- 旧版本（2025-11-25 及以前）：先发 `initialize` 握手，双方交换协议版本和能力（比如是否支持工具列表变更通知），再发 `notifications/initialized`，之后才能正常调用。
- 2026-07-28 版改为无状态：去掉握手和会话 id，每个请求在 `_meta` 里带协议版本和客户端能力；服务器不支持就返回 `UnsupportedProtocolVersionError`（附支持的版本列表），客户端换版本重试；新增 `server/discover` 用来预先查询。
- 通用教训：协议版本和能力必须显式声明和检查，不要靠「对方应该支持」。同时兼容新旧两代时要专门设计降级探测（见决定 10）。

出处：[Versioning and Compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)、[旧版 Lifecycle（2025-11-25，有 initialize 握手）](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)

### 5. 工具定义里那些容易被忽略的字段

- `outputSchema` + `structuredContent`：让工具返回结构化结果，客户端可以校验。不填的话结果就是一段文本，下游只能靠模型理解。
- `isError: true`：工具执行失败（比如参数不合法、外部 API 报错）应该作为**正常结果**返回并标 `isError`，让模型看到错误信息后能自己修正；只有协议层的错误（方法不存在、参数格式坏）才走 JSON-RPC error。这个区分决定了模型能不能自我纠错。
- `annotations`（如只读、破坏性、幂等等提示）：规范明确说，除非服务器可信，客户端**必须**把这些标注当作不可信。也就是说，不能因为第三方服务器声称「只读」就跳过审批。

出处：[Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

### 6. 远程服务器的鉴权：OAuth 2.1 流程

1. 客户端不带 token 请求 → 服务器回 401，并通过 `WWW-Authenticate` 指出自己的「受保护资源元数据」地址（RFC 9728，服务器**必须**实现）。
2. 客户端从元数据里找到授权服务器，再拉授权服务器的元数据。
3. 客户端注册自己：新版推荐 **Client ID Metadata Documents**（客户端用一个 URL 当 client_id，URL 指向描述自己的 JSON）；**动态客户端注册（DCR）在 2026-07-28 已弃用**，仅为兼容保留；也可以预先注册。
4. 走授权码 + PKCE，请求里**必须**带 `resource` 参数（RFC 8707），值是 MCP 服务器的规范 URI，这样签发的 token 只对这个服务器有效。
5. 服务器**必须**校验 token 的受众（audience）确实是自己。

stdio 服务器**不应**走这套流程，而是从环境变量拿凭证（见决定 5）。用户身份、凭证归属在整个 agent 系统里怎么设计，见 [09 身份、合规与运维](09-identity-compliance-ops.md)。

### 7. 为什么不能把 token 原样转发（token passthrough）

- 做法：MCP 服务器收到客户端的 token，原样拿去调下游 API。
- 规范明确禁止。原因：服务器没法确认 token 是发给自己的，就会变成「混淆代理」——任何拿到某个下游 token 的人都能借你的服务器去调下游，绕过你的限流、审计和权限检查；日志里也分不清到底是谁在操作。
- 正确做法：客户端拿的 token 只对 MCP 服务器有效；服务器用自己的凭证或用户授权后换来的下游 token（token exchange）去调下游，并把「哪个用户做了什么」记下来。

出处：[Authorization (2026-07-28)](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)、[MCP Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)、[RFC 8707 Resource Indicators](https://datatracker.ietf.org/doc/html/rfc8707)、[RFC 9728 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728)

---

## 二、文章很少讲但常碰到的事

1. **stdio 服务器里一句调试 print 就能把协议搞坏。** stdout 只能走协议消息，日志一律写 stderr。出处：[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)。
2. **工具上的「只读」「幂等」标注不能信。** 规范要求客户端把非可信服务器的 `annotations` 当作不可信，不能据此跳过审批。出处：[Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)。
3. **resources 很多客户端支持很弱。** 指望模型自己去读 resource 常常落空，兼容面最大的仍是 tools。
4. **不固定版本的 `npx -y 包名` 等于每次启动都可能执行新代码。** 服务器先正常、后来改坏（rug pull）就是从这里进来的。出处：[Invariant Labs: Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)。
5. **仓库里的 `.mcp.json` 是攻击面。** 谁能改仓库谁就能让全组机器启动任意命令，所以各客户端都加了「首次需批准」，这道确认不能随手点过。
6. **官方服务器本身没 bug 也会出事。** GitHub MCP 的真实案例：公开 issue 里的注入指令让 agent 用用户的高权限 token 把私有仓库内容泄露到公开 PR。问题出在「私密数据 + 不可信内容 + 外发能力」的组合。出处：[Invariant Labs: GitHub MCP Exploited](https://invariantlabs.ai/blog/mcp-github-vulnerability)。
7. **官方 MCP Registry 只是目录，不是安全审核。** 出处：[Official MCP Registry](https://registry.modelcontextprotocol.io/)。
8. **很多 IdP 不支持 Client ID Metadata Documents 或动态注册，也不按 `resource` 参数设受众。** 选型前不确认，就会卡在「客户端无法自动注册」，只能退回手工预注册。
9. **新版协议里 list 类接口不再按连接变化。** 「不同用户看到不同工具」要在鉴权后的服务器逻辑里显式实现，并用 `cacheScope: private` 防止共享缓存把一个人的结果给别人。
10. **工具列表顺序一变，prompt 缓存就失效。** 服务器应按确定顺序返回工具，host 也要固定排序。
11. **环境变量里的 key 会被子进程一路继承。** 「执行脚本」类服务器再起子进程时，模型诱导执行的命令也能读到 `env`。凭证范围要小，只传给需要它的那个服务器。
12. **2025 年的大部分 MCP 文章讲的是有握手、有会话的旧模型。** 看教程先看它基于哪个协议版本，sampling、roots、动态客户端注册在 2026-07-28 都已弃用。

---

## 三、要拿的主意

每条按「要定什么 → 选项 → 代价 → 怎么选」写。

### 决定 1：能力做成 tool、resource 还是 prompt

要定什么：一个能力（比如「查订单」「项目文档」「代码审查模板」）应该做成 tool、resource 还是 prompt？要不要依赖客户端能力（sampling / elicitation / roots）？

**选项和各自代价**

| 原语 | 谁决定用它 | 适合 | 代价/坑 |
| - | - | - | - |
| tools | 模型自己决定调用 | 有动作、有参数、需要模型判断何时用的能力 | 每个工具定义都占上下文；模型可能调错；有副作用的要配审批 |
| resources | 应用（host）决定放不放进上下文 | 文件、表结构、文档这类「数据」 | 很多客户端对 resources 支持弱或只支持手动附加，指望模型自己去读 resource 常常落空 |
| prompts | 用户主动选（常见形态是斜杠命令） | 固定流程模板，比如「/review 这段代码」 | 只在有 UI 的客户端有意义，后台 agent 用不上 |

客户端能力（服务器反过来向客户端要东西）：

- **sampling**（服务器借客户端的模型来生成文本）：**2026-07-28 已标为弃用**，迁移建议是「服务器直接接模型厂商 API」。最早在 2027-07-28 之后的版本中移除。
- **roots**（客户端告诉服务器可以访问哪些目录）：**同样已弃用**，迁移建议是通过工具参数、resource URI 或服务器配置传目录。
- **logging**（服务器通过协议发日志）：**也已弃用**，stdio 下写 stderr，可观测用 OpenTelemetry。
- **elicitation**（服务器中途向用户要输入）：仍保留，新版改成「多轮请求」模式（服务器返回 `input_required`，客户端带着用户回答重发原请求）。硬性规定：密码、API key、token、支付信息这类敏感信息**不得**用表单模式收集，必须用 URL 模式跳到外部页面，让敏感内容不经过 MCP 客户端。

**什么情况选哪个**

- 默认做成 tool。大多数客户端只对 tools 支持完整，这是现实中兼容面最大的选择。
- 只读的大块数据，如果目标客户端确实支持 resources，就用 resource，省得模型花一次工具调用去拉；不确定时，同时提供一个「读取 X」的 tool 兜底。
- 新项目**不要**依赖 sampling 和 roots。旧教程里大量用到它们，照着做会在一年后被迫迁移。
- 需要用户中途确认或补充信息时用 elicitation；凡是涉及凭证的，走 URL 模式。

出处：[Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)、[Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources)、[Prompts](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts)、[Elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)、[Deprecated Features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)、[Multi Round-Trip Requests](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr)

---

### 决定 2：本地 stdio 进程还是远程 HTTP 服务

要定什么：你的 MCP 服务器作为本地子进程跑，还是作为远程 HTTP 服务跑？

**选项和各自代价**

- **stdio（本地子进程）**
  - 好处：零网络配置；可以直接访问本机文件、命令行工具、本地数据库；延迟低；不需要做 OAuth。
  - 代价：每个用户、每个客户端各起一份进程，没法集中升级和监控；服务器继承用户本机的全部权限（等于在用户电脑上跑第三方代码，`npx -y 某包` 就是在执行网上下载的代码）；凭证只能靠环境变量，散落在每台机器的配置文件里；stdout 只能输出协议消息，调试 print 会把协议搞坏。
- **Streamable HTTP（远程服务）**
  - 好处：集中部署、集中升级、集中记日志和限流；可以做多用户、按用户鉴权；客户端无需装运行时。
  - 代价：要自己做鉴权（规范要求 OAuth 2.1 那一套）、防 DNS 重绑定（校验 Origin）、限流；有网络延迟和故障；2026-07-28 起去掉了断线续传，流断了客户端要用新 id 重发，所以有副作用的工具要自己做幂等。
- 旧的 **HTTP+SSE** 传输（2024-11-05 版的两个端点方案）早在 2025-03-26 就弃用了，网上还有很多教程在用，新项目不要选。

**什么情况选哪个**

- 要操作用户本机的东西（文件、git、本地 IDE 状态）→ stdio。
- 要访问公司内部系统、SaaS、数据库，并且有多个用户 → 远程 HTTP。凭证留在服务端，比在每个人电脑上发 key 安全得多。
- 只给自己的 agent 后端用、不打算给别的客户端复用 → 很可能根本不需要 MCP，见决定 9。
- 新版协议去掉了会话，服务器默认应该是无状态的，可以直接放在负载均衡后面横向扩展。需要跨调用状态时，规范的做法是服务器生成一个句柄（handle），作为普通工具参数传来传去。旧版依赖 `Mcp-Session-Id` 做粘性会话的设计要改。

出处：[Transports 概览](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)、[stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)、[Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)、[Key Changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

---

### 决定 3：配置放哪一层，要不要提交到仓库

要定什么：你提供的服务器，用户怎么装？配置放哪一层（个人 / 项目 / 组织）？要不要把配置提交到仓库？

**现实情况（各客户端配置长得差不多，但细节不同）**

- 通用形状：一个 JSON，key 是服务器名，值里写 `command` + `args` + `env`（stdio），或 `url` + `headers`（远程）。
- **Claude Desktop**：`claude_desktop_config.json`，macOS 在 `~/Library/Application Support/Claude/`，Windows 在 `%APPDATA%\Claude\`，顶层 key 是 `mcpServers`。
- **Claude Code**：三层作用域。local（只对你在这个项目生效，存在 `~/.claude.json`）、project（项目根目录 `.mcp.json`，提交到仓库与团队共享）、user（对你所有项目生效）。`.mcp.json` 支持 `${VAR}` 和 `${VAR:-默认值}` 展开环境变量。项目里的 `.mcp.json` 服务器需要用户在信任该目录后手动批准，克隆下来的仓库不能自己批准自己的服务器。
- **Cursor**：项目级 `.cursor/mcp.json`，全局 `~/.cursor/mcp.json`；支持 `${env:NAME}` 插值和 `envFile`（只限 stdio）。
- **VS Code**：项目级 `.vscode/mcp.json`，顶层 key 是 `servers`（不是 `mcpServers`），另有 `inputs` 用来在首次启动时提示用户输入密钥；还支持给 stdio 服务器配置文件系统和网络沙箱。

**选项和代价**

- **配置提交到仓库（项目级）**：团队一致、新人开箱即用。代价：仓库成了攻击面——谁能改仓库谁就能让大家的机器启动任意命令；所以各客户端都加了「首次需批准」，你的团队要知道这道确认不能随手点过。
- **个人级配置**：安全、灵活。代价：每个人手动配，版本不一致，排错困难。
- **组织统一下发（托管配置 / 内部注册表）**：可控。代价：需要额外的分发和审核机制。

**什么情况选哪个**

- 配置文件里**只写变量引用，绝不写明文 key**，然后提交到仓库；key 由每个人的环境变量或客户端的密钥输入提供。
- 第三方服务器固定版本号（`npx -y pkg@1.2.3`，而不是不带版本）。不固定版本等于每次启动都可能拉到新代码，这是「rug pull」（服务器先正常、后来改坏）的直接入口。
- 想让服务器跨多个客户端可用，就要按每个客户端的格式各写一份配置说明，key 名和插值语法都不同，这是做 MCP 服务器的人常低估的支持成本。

出处：[Connect to local MCP servers](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers)、[Claude Code MCP](https://code.claude.com/docs/en/mcp)、[Cursor MCP](https://cursor.com/docs/mcp)、[VS Code MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)、[Invariant Labs: Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)

---

### 决定 4：自建还是用外部/官方服务器

要定什么：接 GitHub、Slack、数据库这类系统时，用厂商官方 MCP 服务器、社区服务器，还是自己写？

**选项和代价**

- **厂商官方服务器**（比如 GitHub 官方的 github-mcp-server，有远程托管版和本地版）：维护有保障、鉴权和 API 变化跟得上。代价：工具数量多（往往几十个），塞满上下文；工具粒度按厂商 API 设计，不按你的任务设计；你无法控制它什么时候改工具描述。
- **社区服务器**（官方 servers 仓库里的参考实现、注册表里的第三方）：快。代价：质量参差、可能停更；本质是在你机器上运行陌生人的代码；工具描述本身可能带注入（tool poisoning）。官方 servers 仓库里很多是「参考实现」，用于学习，不是生产级产品。
- **自建**：工具粒度按你的任务设计（比如一个「给这个客户退款」，而不是 API 的十个原子操作），权限最小、描述可控、可以加业务校验和审计。代价：要自己维护、跟进上游 API 和 MCP 版本变化。

**什么情况选哪个**

- 原型和个人使用：官方服务器优先，社区服务器要看源码、固定版本。
- 生产 agent：通常自建一层「面向任务」的窄工具，内部再去调厂商 API 或官方服务器。原因有三：工具数量可控、权限可控、行为（描述和返回格式）不会被别人悄悄改。
- 即使是官方服务器，也会碰到「致命三要素」：GitHub MCP 被利用的真实案例里，攻击者在公开仓库的 issue 里写注入指令，让 agent 用用户的高权限 token 把私有仓库内容泄露到公开 PR 里。服务器本身没有 bug，问题出在组合。所以用官方服务器时也要按会话限定能访问的仓库/范围。
- 官方 MCP Registry 只是一个「元数据目录」，用来发现服务器，不等于安全审核。

出处：[github/github-mcp-server](https://github.com/github/github-mcp-server)、[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)、[Official MCP Registry](https://registry.modelcontextprotocol.io/)、[Invariant Labs: GitHub MCP Exploited](https://invariantlabs.ai/blog/mcp-github-vulnerability)、[Simon Willison: MCP has prompt injection security problems](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/)

---

### 决定 5：本地服务器怎么拿凭证

要定什么：stdio 服务器需要 API key 时怎么传？

- 规范明确：stdio 服务器**不应**走 OAuth 那套流程，而是从环境变量拿凭证。
- 选项：配置文件 `env` 里写死（最差，会被提交、被截图、被同步）；配置里引用环境变量 / `envFile`（常见做法）；客户端的密钥输入（如 VS Code `inputs`，首次提示并存进系统密钥库）；服务器自己从系统钥匙串或密钥管理服务读取。
- 坑：环境变量会被子进程继承。如果服务器再起子进程跑命令（很多「执行脚本」类服务器会这么做），key 会一路传下去，模型诱导执行的命令也能读到 `env`。凭证范围要尽量小（只读 token、限定仓库），并且只传给需要它的那个服务器。
- 怎么选：配置里只写变量引用，绝不写明文；团队场景用客户端的密钥输入或系统钥匙串；给最小权限的 token。

---

### 决定 6：授权服务器自己做，还是接现成的 IdP

要定什么：远程 MCP 服务器要走 OAuth 2.1（流程见第一节第 6 条），发 token 的授权服务器从哪来？

- 自己实现：完全可控，但 OAuth 细节多（PKCE、发行方校验、重定向校验、混淆攻击），容易做错。
- 接现成 IdP（公司 SSO、云厂商身份服务）：省事。坑：很多 IdP 不支持 Client ID Metadata Documents 或 DCR，也不一定按 `resource` 参数设置 audience。选型前先确认 IdP 支持这些，否则会卡在「客户端无法自动注册」上，只能退回手工预注册。
- 怎么选：优先接现成 IdP，但选型时先用一个真实客户端把「注册 → 授权 → 受众校验」完整走通一遍；IdP 缺功能时宁可预注册客户端，也不要从零自写授权服务器。

---

### 决定 7：多用户场景下谁持有下游凭证

要定什么：一个远程 MCP 服务器服务很多用户时，下游系统的凭证放在哪？

- **共享服务账号**：实现最简单。代价：所有用户的操作都用同一个大权限身份执行，A 用户能通过 agent 读到 B 的数据；下游审计看不到真实用户。只适合数据本来就对所有用户公开的场景。
- **每个用户自己的下游 token（服务器代为保管）**：用户首次使用时授权，服务器按用户存 refresh token。权限天然跟用户一致。代价：要做加密存储、过期刷新、撤销；服务器成了高价值目标。
- **服务器不保管，按次换取**（token exchange / 下游也认同一个 IdP）：最干净。代价：依赖下游支持，很多 SaaS 不支持。

经验：只要数据有「谁能看」的区分，就别用共享服务账号。另外，多租户时工具列表、缓存、日志都要按用户/租户隔离；新版协议要求 list 类接口不再按连接变化，所以「不同用户看到不同工具」要在鉴权后的服务器逻辑里显式实现，并通过 `cacheScope: private` 防止共享缓存把一个人的结果给别人。

出处：[Authorization (2026-07-28)](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)、[MCP Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)、[OAuth 2.1](https://oauth.net/2.1/)、[RFC 8707 Resource Indicators](https://datatracker.ietf.org/doc/html/rfc8707)、[RFC 9728 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728)、[VS Code MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)、[Cursor MCP](https://cursor.com/docs/mcp)

---

### 决定 8：工具数量多了以后怎么办

要定什么：接了很多服务器、工具数量上百时怎么办？

**事实**

- 工具定义在对话开始前就占上下文。Anthropic 举的例子：5 个常见服务器、58 个工具约占 55K token，内部见过优化前工具定义占 134K token。
- 不只是成本问题，选错工具和填错参数是最常见的失败，尤其是名字相近的工具（如 `notification-send-user` 和 `notification-send-channel`）。
- 工具多时准确率会掉：Anthropic 的内部测试里，开启按需搜索工具后，Opus 4 在大工具库 MCP 评测上从 49% 提到 74%。RAG-MCP 论文也报告了类似现象：先检索再给模型少量工具，选择准确率明显提高。

**选项和代价**

- **全量加载**：简单，模型看到全部能力。代价：上下文和成本，选择准确率下降，prompt 缓存容易因工具列表变动而失效。
- **按任务/按会话裁剪**：host 根据场景只启用部分服务器或工具。代价：要维护映射关系，选漏了模型就做不到。
- **按需搜索（tool search / 延迟加载）**：只给模型一个「搜索工具」的工具，需要时再加载定义。代价：多一次往返；搜索质量取决于工具名和描述写得好不好；依赖模型和平台支持。
- **代码执行模式**：把 MCP 工具包装成代码 API，让模型写代码调用，中间结果留在执行环境里不进上下文。Anthropic 报告一个案例从 150,000 token 降到 2,000 token；Cloudflare 的 Code Mode 也是同一思路。代价：必须有安全的沙箱，调试更难，模型写的代码也要审。
- **合并工具**：把多个原子工具合成面向任务的工具。代价：灵活性下降。

**什么情况选哪个**

- 工具在几十个以内、名字差异明显：全量加载，把精力花在工具描述上。
- 工具上百或来自很多服务器：按需搜索或按场景裁剪。
- 任务需要处理大量中间数据（大表、长文档在工具间传递）：考虑代码执行模式。
- 不管哪种：工具列表要稳定排序（新版规范也建议服务器按确定顺序返回工具），因为顺序一变，prompt 缓存就失效。

出处：[Anthropic: Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)、[Tool search tool – Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)、[Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)、[Cloudflare: Code Mode](https://blog.cloudflare.com/code-mode/)、[RAG-MCP (arXiv 2505.03275)](https://arxiv.org/abs/2505.03275)、[Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)、[Speakeasy: Why less is more for MCP](https://www.speakeasy.com/mcp/tool-design/less-is-more)

---

### 决定 9：包成 MCP 服务器，还是直接写 function calling

要定什么：工具是包成 MCP 服务器，还是直接在 agent 代码里定义成函数？

**选项和代价**

- **直接 function calling（进程内函数）**：没有额外进程和网络；类型、错误、事务都在你代码里；调试简单；可以直接用调用方的用户上下文做权限判断。代价：只有你这个 agent 能用；换个客户端（IDE、桌面应用）要重写。
- **MCP 服务器**：一次实现，多个 host 复用；可以独立部署、独立升级、独立做鉴权；可以接入别人写好的生态。代价：多一层协议和进程/网络；版本兼容要跟进；权限和用户身份要通过协议传递，比进程内复杂；错误要区分协议错误和工具错误。
- **混合**：核心业务工具进程内，外部生态工具走 MCP。
- 第三种部署形态：一些模型厂商 API 可以直接连接远程 MCP 服务器（服务端代你调用），省掉自己写 client。代价：工具调用发生在厂商侧，你的审批、日志、重试能力会变弱，且服务器要能被厂商访问到（公网地址，或厂商提供的隧道，比如 OpenAI 的 Secure MCP Tunnel）。

**什么情况选哪个**

- 只给自己的一个 agent 用、对延迟和事务敏感 → 直接 function calling。
- 同一组能力要给多个 agent / 多个客户端（包括同事的 IDE）用 → MCP。
- 对接的是别人已经提供 MCP 服务器的系统 → 用 MCP 接入，但在你的 host 里自己控制审批和日志。
- 不要因为「MCP 是标准」就把所有内部函数都改成 MCP 服务器，这只会多出进程、网络和版本问题。

出处：[Architecture overview](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)、[MCP connector – Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)、[OpenAI: Connectors and MCP servers](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)、[Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

---

### 决定 10：要不要升级到 2026-07-28，要不要新旧兼容

要定什么：已有的 MCP 服务器/客户端要不要升级到 2026-07-28？要不要同时兼容新旧？

**2026-07-28 相对 2025-11-25 的破坏性变化（会直接影响你的代码）**

- 去掉 `initialize` 握手和 `notifications/initialized`，改为每个请求自带版本和能力；新增服务器必须实现的 `server/discover`。
- 去掉协议层会话和 `Mcp-Session-Id`；有状态的设计要改成显式句柄。
- 去掉 SSE 断线续传（`Last-Event-ID`），断了就用新 id 重发。
- 去掉 `ping`、`logging/setLevel`、`notifications/roots/list_changed`；GET 端点和 resources 订阅换成 `subscriptions/listen`。
- 服务器主动发起的请求（sampling、roots、elicitation）改为「多轮请求」模式；所有结果必须带 `resultType`。
- tasks 从核心移到扩展；错误码重新编号（如不支持版本是 -32022）；resource not found 从 -32002 改为 -32602。
- 弃用：Roots、Sampling、Logging、动态客户端注册（最早 2027-07-28 之后的版本移除）；HTTP+SSE 传输早已弃用。

**选项和代价**

- **只支持旧版**：零改动。代价：新客户端逐渐只说新版；你会错过无状态带来的扩展性。
- **只支持新版**：代码最简单。代价：还在用旧版的客户端连不上。
- **同时兼容（dual-era）**：规范专门定义了探测方式（stdio 先发 `server/discover`，失败或超时就退回旧握手）。代价：两套路径都要测。

**什么情况选哪个**

- 服务器给不特定客户端用：一段时间内做双版本兼容，用官方 SDK 来做，别自己手写协商。
- 客户端/host 自己控制、服务器也自己控制：直接上新版。
- 不管哪种：把「协议版本」当成依赖版本来管——在 CI 里对新旧版本各跑一套集成测试；关注 [feature lifecycle 政策](https://modelcontextprotocol.io/community/feature-lifecycle)（弃用后至少一年才可能移除），按这个节奏排迁移。
- 看教程和博客先看它基于哪个协议版本。2025 年的大部分 MCP 文章讲的是有握手、有会话的旧模型。

出处：[Key Changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog)、[Versioning and Compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)、[旧版 Lifecycle（2025-11-25，有 initialize 握手）](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)、[Deprecated Features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)、[Feature Lifecycle and Deprecation Policy](https://modelcontextprotocol.io/community/feature-lifecycle)

---

## 四、资料清单

- [Architecture overview（MCP）](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)：教学；一-1、决定 9；host、client、server 三个角色和分层，入门第一篇。
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)：规范；一-2；很短，请求/响应/通知/错误码一次读完，MCP 和很多工具协议都建在它上面。
- [MCP 2026-07-28 Key Changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog)：规范；一-4、决定 2、决定 10；新版所有破坏性改动的权威清单（去握手、去会话、去断线续传、trace 上下文进 `_meta`），读旧教程前先读它。
- [MCP Transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)：规范；一-3、决定 2；stdio 和 Streamable HTTP 的收发规则与安全要求。
- [MCP Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)：规范；一-3、决定 2；远程传输的请求头、Origin 校验、流式响应规则。
- [MCP Versioning and Compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)：规范；一-4、决定 10；无握手的版本协商和新旧兼容探测。
- [MCP Deprecated Features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)：规范；决定 1、决定 10；一张表说明 Roots、Sampling、Logging、动态客户端注册已弃用、迁移路径和最早移除时间。
- [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)：规范；一-5；outputSchema、isError、annotations 不可信等关键规则。
- [MCP Elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation)：规范；决定 1；表单模式和 URL 模式的区别，敏感信息必须走 URL 模式。
- [MCP Authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)：规范；一-6、一-7；OAuth 2.1、受保护资源元数据、resource 参数、受众校验，以及 stdio 不走 OAuth。
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)：规范/说明；一-7、决定 7；混淆代理、token 透传、SSRF、本地服务器风险等协议层攻击与对策。
- [Connect to local MCP servers](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers)：教学；决定 3；Claude Desktop 配置文件位置和格式。
- [Claude Code: Connect to tools via MCP](https://code.claude.com/docs/en/mcp)：说明；决定 3、决定 5；三层作用域、`.mcp.json`、环境变量展开、项目服务器需批准。
- [Cursor: MCP](https://cursor.com/docs/mcp)：说明；决定 3、决定 5；`.cursor/mcp.json`、`${env:}` 插值、envFile。
- [VS Code: MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)：说明；决定 3、决定 5；`servers`/`inputs` 格式和 stdio 服务器沙箱。
- [Anthropic: Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)：分析；决定 8；工具定义占用上下文和选择准确率的具体数字。
- [Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)：分析；决定 8；把工具当代码 API 的思路和代价。
- [Cloudflare: Code Mode](https://blog.cloudflare.com/code-mode/)：分析；决定 8；同一思路的另一实现，解释为什么模型写代码调 API 比直接调工具更好。
- [RAG-MCP (arXiv)](https://arxiv.org/abs/2505.03275)：分析（论文）；决定 8；工具检索缓解 prompt 膨胀和选择困难的实验。
- [Invariant Labs: Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)：分析；二-4、决定 3；工具描述注入和 rug pull 的原始披露。
- [Invariant Labs: GitHub MCP Exploited](https://invariantlabs.ai/blog/mcp-github-vulnerability)：分析；二-6、决定 4；官方服务器在致命三要素下被利用的真实案例。
- [Simon Willison: MCP has prompt injection security problems](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/)：分析；决定 4；从使用者角度总结 MCP 的注入风险。

- [深入理解 AI Agent：设计原理与工程实践 第 4 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter4.md)：教学；决定 8、决定 9；「工具生态：MCP 与 Skill Hub」「工具太多怎么办」两节讲层次化组织、按需加载和主动工具发现。

工具描述怎么写、返回值怎么控制大小，见 [03](03-agent-loop-context.md) 第 5 节和 Anthropic《Writing effective tools for agents》。

---

## 五、阅读顺序

1. 打底：Architecture overview → JSON-RPC 2.0 → Key Changes（先知道新旧两代的差别）。
2. 协议细节：Transports → Versioning → Tools。
3. 鉴权与安全：Authorization → Security Best Practices → Invariant Labs 两篇。
4. 规模化：advanced tool use → Code execution with MCP。
5. 最后读你要用的那个客户端的配置文档。
