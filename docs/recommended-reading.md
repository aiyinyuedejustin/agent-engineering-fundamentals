# 推荐阅读：8 份可以对照着读的成体系资料

这一页挑了 8 份成体系的资料，有书、系列教程，也有带讲解的源码解读。每份都不全，合起来能覆盖本仓库[知识地图](../README.md#知识地图)的大部分板块。复习某个板块时，先看下面的覆盖表找到对应资料，读完再回到本仓库的 docs 章节，补上资料里没讲的部分。

> 星标数、更新日期都是 2026-10-09 核对的。章节链接也在同一天逐个打开确认过。

---

## 1. 《深入理解 AI Agent：设计原理与工程实践》

- **链接**：[GitHub 仓库](https://github.com/bojieli/ai-agent-book) ｜ [在线阅读](https://bojieli.github.io/ai-agent-book/)
- **作者**：李博杰
- **形式**：开源书，正文 10 章，配 93 个可运行实验，有 PDF/EPUB
- **语言**：中文（另有英、日、韩等 13 种译本）
- **最近更新**：最近提交 2026-09-30，★52,979

**强在哪**
- 以 “Agent = LLM + 上下文 + 工具” 为主线，从 API 的消息结构讲到 chat template、KV Cache 与 Prompt Cache，再推出上下文该怎么拼才不破坏缓存。这条线讲得很透。
- 第 5 章 “故障与错误恢复” 写的都是做过才知道的事：故障分四层（API、工具、上下文、控制流）；流式连接最危险的不是断开，而是连着却不再出数据，所以要有空闲看门狗；后台辅助调用失败直接放弃，以免重试放大；跨厂商接管时，思考的文字能带走，签名凭证带不走，所以轨迹要按中立格式存。
- 编辑工具的几种格式、代码搜索的取舍（grep/glob 还是建嵌入索引）、记忆与 RAG、评测（pass^k、轨迹前缀回归、统计显著性）都有专章。

**缺什么**
- 请求层的协议细节没成体系：Chat Completions 和 Responses 的差异、SSE 事件序列、各家结构化输出都没专门讲。
- 部署链路（代理缓冲、负载均衡超时）、身份与密钥、合规、配置分层基本没讲。
- 第 6 章的语音、机器人，第 8 章的后训练，离应用工程较远，可以跳过。

**建议怎么读**
- 必读：[第 2 章 上下文工程](https://bojieli.github.io/ai-agent-book/book/chapter2/)（重点是 “KV Cache 友好的上下文设计”）、[第 5 章 Coding Agent](https://bojieli.github.io/ai-agent-book/book/chapter5/)（重点是 “故障与错误恢复” 到 “Coding Agent 的安全”）
- 按需读：[第 4 章 工具](https://bojieli.github.io/ai-agent-book/book/chapter4/)、[第 3 章 记忆与知识库](https://bojieli.github.io/ai-agent-book/book/chapter3/)、[第 7 章 评估](https://bojieli.github.io/ai-agent-book/book/chapter7/)、[第 10 章 多 Agent](https://bojieli.github.io/ai-agent-book/book/chapter10/)

---

## 2. 道雾轩《从 LLM 到 Coding Agent》+《Codex 源码解读》

- **链接**：[从 LLM 到 Coding Agent](https://daiw.net/manual/llm-to-agent)（21 篇） ｜ [Codex 源码解读](https://daiw.net/manual/codex-source)（57 篇）
- **作者**：David（个人站 道雾轩）
- **形式**：两个配套专栏。前一个从裸 API 一路搭出最小的 coding agent；后一个对照 OpenAI Codex CLI 的 Rust 源码逐个模块讲，并标出代码位置
- **语言**：中文
- **最近更新**：分别更新于 2026-09-13、2026-09-29

**强在哪**
- 离请求层最近的一份中文资料。讲到一次 API 调用到底返回什么，流式输出里工具参数逐字到达、末尾才完整，以及边流式接收边执行工具的并发编排。还讲到在流式输出、并发执行、手里还欠着 tool_result 的时候怎么干净地叫停。
- 第 17 篇讲扩展思考的三条铁律：思考块原样保留；签名和生成它的模型绑定，所以模型回退前必须先剥离；一条思考轨迹在结束前不能删。第 15 篇讲 429/529、Retry-After 优先、max_tokens 截断后先提额再续写、模型回退。
- 《Codex 源码解读》把一个生产级 agent 的外围拆得最全：Responses API 流式客户端、历史只追加不改写、AGENTS.md 的查找规则；macOS Seatbelt、Linux bubblewrap + seccomp、Windows 沙箱、网络代理、执行策略；配置分层与组织强制下发、登录与认证、app-server 的 thread/turn/item 事件协议、rollout 持久化、OpenTelemetry 遥测。

**缺什么**
- 讲的是一个本地 CLI agent，服务端多租户、任务队列、Web 前端断线续流都不涉及。
- 评测、检索基本没有。合规只零星出现。
- 源码解读跟着 Codex 版本走，细节会过时，读的时候注意文中标的源码快照。

**建议怎么读**
- 先通读《从 LLM 到 Coding Agent》前 20 篇，每篇篇幅不长。最该精读的几篇：[05 流式处理](https://daiw.net/manual/llm-to-agent/streaming)、[08 中断与转向](https://daiw.net/manual/llm-to-agent/interrupt)、[11 系统提示与上下文注入](https://daiw.net/manual/llm-to-agent/context-injection)、[12 Prompt 缓存](https://daiw.net/manual/llm-to-agent/prompt-caching)、[15 错误恢复与模型回退](https://daiw.net/manual/llm-to-agent/error-recovery)、[17 扩展思考](https://daiw.net/manual/llm-to-agent/thinking)
- 《Codex 源码解读》当查阅手册用：[07 v2 协议](https://daiw.net/manual/codex-source/app-server-protocol)、[10 会话持久化](https://daiw.net/manual/codex-source/rollout-and-storage)、[14 模型客户端](https://daiw.net/manual/codex-source/model-client)、[17 指令从哪来](https://daiw.net/manual/codex-source/instructions)、[27 权限模型](https://daiw.net/manual/codex-source/permissions-model)、[30 Linux 沙箱](https://daiw.net/manual/codex-source/linux-sandbox)、[32 网络代理](https://daiw.net/manual/codex-source/network-proxy)、[35 配置系统](https://daiw.net/manual/codex-source/config-system)、[50 登录与认证](https://daiw.net/manual/codex-source/login-and-auth)

---

## 3. Build Your Always-On AI Agent From Scratch（Prof Rod）

- **链接**：[全书目录](https://www.profrod.ai/book)
- **作者**：Rod Rivera（ITAM 实践教授，曾在阿里云、华为、三星做生产 ML 系统）
- **形式**：免费在线书，21 章，用 Python 从零搭一个长期运行的 agent，每章配 Colab 笔记本和可离线运行的检查点
- **语言**：英文
- **最近更新**：持续更新中，21 章都还标着草稿（第 3 章的实验记录于 2026-09-26）

**强在哪**
- 别的资料很少讲的分布式系统基本功，这里讲得最扎实：
  - 超时：一个截止时间要同时盖住 DNS、连接、响应头和整个响应体。只设 socket 读超时挡不住服务端一点一点慢慢发数据。
  - 请求超时被杀掉后，远端可能照样在生成、照样计费，所以失败的调用也要计入预算。
  - 回复丢了怎么办：用幂等键保证同一操作只执行一次；worker 崩溃后用租约和 fencing 接管。
  - 持久化收件箱/发件箱、排队论与定时任务、首 token 延迟里 prefill 和 decode 各占多少。
- 每个结论都拿真实模型测过。例如第 3 章实测发现，重试的收益比 “各次尝试相互独立” 的假设预测得低，因为任务里有一部分对模型来说本来就做不出。
- 评测讲到误差区间、配对比较和 “赢家诅咒”，比一般资料讲得更有统计依据。

**缺什么**
- 只对接本地 Ollama 和 Anthropic 两种接口，多厂商协议差异、流式事件没展开（刻意用了非流式）。
- 场景是一个小店助理，不讲 coding agent 的编辑工具、沙箱技术选型，也不讲多租户。
- 篇幅大、推导多，适合挑章精读，不适合通读。

**建议怎么读**
- 精读：[第 3 章 循环与可靠性](https://www.profrod.ai/book/ch03-agent-loop)、[第 12 章 重试与幂等](https://www.profrod.ai/book/ch12-ambiguous-order)、[第 13 章 租约与崩溃恢复](https://www.profrod.ai/book/ch13-worker-recovery)
- 按需：[第 4 章 持久化状态](https://www.profrod.ai/book/ch04-durable-state)、[第 8 章 持久化工作收件箱](https://www.profrod.ai/book/ch08-durable-work)、[第 10 章 排队与定时](https://www.profrod.ai/book/ch10-scheduling)、[第 16 章 评测](https://www.profrod.ai/book/ch16-evaluation)、[第 19 章 成本与部署](https://www.profrod.ai/book/ch19-operation)、[第 21 章 上下文预算](https://www.profrod.ai/book/ch21-context)

---

## 4. 《AI Agent 架构：从单体到企业级多智能体》（Kocoro-lab）

- **链接**：[GitHub 仓库](https://github.com/Kocoro-lab/ai-agent-book) ｜ [在线阅读](https://waylandz.com/ai-agent-book/)
- **作者**：Wayland Zhang。参考实现是作者团队开源的多智能体系统 [Shannon](https://github.com/Kocoro-lab/Shannon)（★2,280）
- **形式**：开源书，9 部分 33 章，每章有 “常见的坑” 和动手实验
- **语言**：中文、英文、日文
- **最近更新**：最近提交 2026-08-08，★400

**强在哪**
- 这 8 份里唯一站在服务端、多租户视角写的。它讲：
  - Go 编排、Rust 执行、Python 推理三层之间怎么传 workflow ID、怎么分层设超时；
  - 用 Temporal 做持久化执行：Workflow 和 Activity 怎么分、版本门控、信号与查询、重放调试；
  - Token 预算分三级、背压、熔断，用幂等防止重试重复计费；
  - 用 OPA 做策略治理并灰度上线；五层租户隔离（认证、会话、工作流、向量库、数据库）、API key 存储；
  - 定时运行的后台 agent，包括孤儿任务清理和预算注入；
  - 分层模型路由与集中定价。
- 每章 “常见的坑” 来自真实系统，可以直接当检查清单用。

**缺什么**
- 请求层协议、流式、提示缓存的细节几乎没有。
- 沙箱只讲 WASI 一条路线，不讲 bubblewrap、容器、microVM 怎么选。
- Part 4–6（Planning、ToT、Debate 等推理模式）偏模式介绍，和工程隐含知识关系不大。

**建议怎么读**
- 精读 Part 7–8：[第 20 章 三层架构](https://waylandz.com/ai-agent-book/%E7%AC%AC20%E7%AB%A0-%E4%B8%89%E5%B1%82%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1/)、[第 21 章 Temporal 工作流](https://waylandz.com/ai-agent-book/%E7%AC%AC21%E7%AB%A0-Temporal%E5%B7%A5%E4%BD%9C%E6%B5%81/)、[第 22 章 可观测性](https://waylandz.com/ai-agent-book/%E7%AC%AC22%E7%AB%A0-%E5%8F%AF%E8%A7%82%E6%B5%8B%E6%80%A7/)、[第 23 章 Token 预算控制](https://waylandz.com/ai-agent-book/%E7%AC%AC23%E7%AB%A0-Token%E9%A2%84%E7%AE%97%E6%8E%A7%E5%88%B6/)、[第 24 章 策略治理](https://waylandz.com/ai-agent-book/%E7%AC%AC24%E7%AB%A0-%E7%AD%96%E7%95%A5%E6%B2%BB%E7%90%86/)、[第 26 章 多租户设计](https://waylandz.com/ai-agent-book/%E7%AC%AC26%E7%AB%A0-%E5%A4%9A%E7%A7%9F%E6%88%B7%E8%AE%BE%E8%AE%A1/)
- 再读：[第 30 章 Background Agents](https://waylandz.com/ai-agent-book/%E7%AC%AC30%E7%AB%A0-Background-Agents/)、[第 31 章 分层模型策略](https://waylandz.com/ai-agent-book/%E7%AC%AC31%E7%AB%A0-%E5%88%86%E5%B1%82%E6%A8%A1%E5%9E%8B%E7%AD%96%E7%95%A5/)

---

## 5. learn-agent：20 章 Agent Harness 架构实操（ryzqi）

- **链接**：[GitHub 仓库](https://github.com/ryzqi/learn-agent)
- **作者**：ryzqi
- **形式**：20 章文章，每章配一份可运行的 TypeScript 代码和测试，一章加一种机制，最后在第 20 章总装成完整的 harness。教学方法沿用 [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)，但讲得更细、测试更严
- **语言**：中文
- **最近更新**：最近提交 2026-09-02，★353

**强在哪**
- 适合动手复习：读完一章就能跑对应的测试，看到边界条件的实际表现。
- 第 11 章 “API 韧性” 把容易做错的地方都写成了测试：
  - 按错误类型和状态码归一化，不去匹配异常文本；HTTP 200 的响应也不能直接信；
  - 输出被截断时如果带着 tool_calls，立刻失败；
  - 输入过长时，同一个逻辑请求只压缩一次；
  - Retry-After 必须能严格解析才采用，连续 529 才切到备用模型；
  - 内部重试不重跑 Hook，取消要等操作真正收束才算完。
- 任务系统一组章节讲得很实：任务 DAG、先落盘再启动后台 worker、Cron 按 UTC 持久化、用 SQLite 事务原子认领任务并带租约、Git worktree 隔离、MCP 工具池的命名隔离。

**缺什么**
- 单机、单用户。没有服务端、前端、多租户、合规。
- 没有评测，也没有可观测性。
- 很多机制是照着 Claude Code 复刻的，换别家产品时要分清哪些是通用约束、哪些只是它的取舍。

**建议怎么读**
- 精读 [第 11 章 API 恢复](https://github.com/ryzqi/learn-agent/blob/master/11.%20API%20%E9%9F%A7%E6%80%A7%E5%8D%B3%E7%94%9F%E5%91%BD%EF%BC%9A%E5%86%B3%E5%AE%9A%20AI%20Agent%20%E5%95%86%E4%B8%9A%E5%8C%96%E6%88%90%E8%B4%A5%E7%9A%84%E9%9A%90%E8%97%8F%E7%BB%86%E8%8A%82%EF%BC%88Agent%E6%9E%B6%E6%9E%84%E5%AE%9E%E6%93%8D%E5%8D%81%E4%B8%80%EF%BC%89.md)、[第 3 章 权限系统](https://github.com/ryzqi/learn-agent/blob/master/3.%20%E6%B7%B1%E5%BA%A6%E6%8B%86%E8%A7%A3%E5%A4%8D%E5%88%BB%20Claude%20Code%20%E6%9D%83%E9%99%90%E7%B3%BB%E7%BB%9F%EF%BC%9A%E5%A6%82%E4%BD%95%E5%AE%9E%E7%8E%B0%E7%94%9F%E4%BA%A7%E7%BA%A7%E7%9A%84%20Agent%20%E5%AE%89%E5%85%A8%E7%AD%96%E7%95%A5%EF%BC%9F%EF%BC%88Agent%E6%9E%B6%E6%9E%84%E5%AE%9E%E6%93%8D%E4%B8%89%EF%BC%89.md)、[第 13 章 后台任务](https://github.com/ryzqi/learn-agent/blob/master/13.%20%E4%BB%8E%E4%B8%B2%E8%A1%8C%E5%88%B0%E5%BC%82%E6%AD%A5%EF%BC%9AAI%20Agent%20%E6%9E%B6%E6%9E%84%E6%BC%94%E8%BF%9B%E4%B8%AD%E7%9A%84%E2%80%9C%E6%85%A2%E6%93%8D%E4%BD%9C%E2%80%9D%E5%A1%AB%E5%9D%91%E6%8C%87%E5%8D%97%EF%BC%88Agent%E6%9E%B6%E6%9E%84%E5%AE%9E%E6%93%8D%E5%8D%81%E4%B8%89%EF%BC%89.md)、[第 14 章 Cron 调度](https://github.com/ryzqi/learn-agent/blob/master/14.%20%E8%AE%A9%20Agent%20%E5%AD%A6%E4%BC%9A%E7%9C%8B%E8%A1%A8%EF%BC%9ACron%20%E8%B0%83%E5%BA%A6%E5%99%A8%E7%9A%84%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%AE%9E%E7%8E%B0%EF%BC%88Agent%E6%9E%B6%E6%9E%84%E5%AE%9E%E6%93%8D%E5%8D%81%E5%9B%9B%EF%BC%89.md)、[第 17 章 SQLite 认领](https://github.com/ryzqi/learn-agent/blob/master/17.%20%E4%BB%8E%E2%80%9C%E4%BA%BA%E8%82%89%E6%B4%BE%E5%8F%91%E2%80%9D%E5%88%B0%E2%80%9C%E8%87%AA%E9%A9%B1%E8%BD%AE%E8%AF%A2%E2%80%9D%EF%BC%9A%E5%A4%9A%E6%99%BA%E8%83%BD%E4%BD%93%EF%BC%88Agent%20Team%EF%BC%89%E5%8E%BB%E4%B8%AD%E5%BF%83%E5%8C%96%E5%8D%8F%E4%BD%9C%E5%AE%9E%E6%88%98%EF%BC%88Agent%E6%9E%B6%E6%9E%84%E5%AE%9E%E6%93%8D%E5%8D%81%E4%B8%83%EF%BC%89.md)
- 其余章节可以跳着看，只看 README 表格里列出的 “本章新增的关键能力”。

---

## 6. Anthropic Engineering 博客

- **链接**：[anthropic.com/engineering](https://www.anthropic.com/engineering)
- **作者**：Anthropic 工程团队（做 Claude Code、Claude API 的人）
- **形式**：工程文章合集，二十多篇，每篇都是长文
- **语言**：英文
- **最近更新**：最新一篇发表于 2026-05-25

**强在哪**
- 一手经验，而且常常附带数字和事故。几篇值得读的：
  - 怎么写给模型用的工具；
  - 上下文工程；
  - 长时间运行的 agent 需要什么样的 harness；
  - 托管 agent 为什么要把 “大脑” 和 “手” 拆开（会话不等于模型的上下文窗口）；
  - 三种隔离模式：临时容器、有人审批的沙箱、本地虚拟机；
  - 评测的整体做法，以及基础设施噪声会让 coding agent 的评测分数波动多少；
  - 三起服务端事故的复盘：路由把请求发错了上下文窗口、输出损坏、编译器 bug。
- 文章之间是同一套思路，可以当作 “做过的人怎么想” 的总纲来读。

**缺什么**
- 不是教程。没有代码层面的请求构造、重试参数、会话存储这类细节。
- 视角绑定 Claude，跨厂商、自部署都不涉及。
- 文章没有成书顺序，需要自己挑。

**建议怎么读**
- 按这个顺序挑读：[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) → [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) → [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) → [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) → [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents) → [How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude) → [Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) → [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) → [Quantifying infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise) → [A postmortem of three recent issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues)

---

## 7. AI Evals: Everything You Need to Know（Hamel Husain、Shreya Shankar）

- **链接**：[hamel.dev/blog/posts/evals-faq](https://hamel.dev/blog/posts/evals-faq/)
- **作者**：Hamel Husain、Shreya Shankar。两人开的评测课教过 5,000 多名工程师和产品经理，这份 FAQ 就是从课上的问题整理出来的
- **形式**：长篇 FAQ，按主题分组，约 60 个问题，开头有按处境挑选的阅读路径
- **语言**：英文
- **最近更新**：2026-09-21

**强在哪**
- 评测这一块最实用的一份资料。核心是先做错误分析：读真实 trace，写开放式笔记，归纳成失败分类，再决定写哪些评测。
- 写清楚了常被忽略的取舍：
  - 用二元通过/不通过，不用 1–5 打分；
  - LLM 评委要用人工标注验证，看真阳性率和真阴性率，数据要分训练、开发、测试三份；
  - 每个评委只查一种失败，只给它判断所需的那部分 trace；
  - CI 评测和线上监控的分工，guardrail 和 evaluator 的区别；
  - trace 里有敏感数据时怎么办，提示词放 Git 管版本。

**缺什么**
- 只讲评测和与之相关的 trace，不涉及 agent 本身的构造。
- 对 agent 的多步评测只有几个问题，可以配合第 6 节的 Anthropic 评测文章一起读。

**建议怎么读**
- 先按页首表格里自己的处境挑一条阅读路径，再精读 “Error Analysis”“Evaluation Design”“Production & Deployment” 三组问题。

---

## 8. 12-Factor Agents（HumanLayer）

- **链接**：[GitHub 仓库](https://github.com/humanlayer/12-factor-agents)
- **作者**：Dex Horthy / HumanLayer
- **形式**：12 条原则，每条一篇短文，配图配代码，另附工作坊代码
- **语言**：英文（另有社区中文翻译 [12-factor-agents-zh](https://github.com/yzfly/12-factor-agents-zh)）
- **最近更新**：最近提交 2025-09-21，★26,620

**强在哪**
- 一两个小时能读完。它给 “为什么不该把控制流交给框架” 一个清楚的框架：
  - 自己掌控提示词、上下文窗口和控制流；
  - 工具调用本质上就是结构化输出；
  - 执行状态和业务状态放在一起；
  - agent 能随时启动、暂停、恢复；
  - 联系人类也做成一种工具；
  - 把 agent 写成一个无状态的 reducer。
- 这些原则对应着会话存储、长任务、审批这几块的设计选择，可以当作读其他资料前的地图。

**缺什么**
- 原则层面，没有协议细节、可靠性参数和具体实现。
- 一年多没更新，例子里的模型和接口已经旧了，原则本身没有过时。

**建议怎么读**
- 全读。重点是 [Factor 3 自己掌控上下文窗口](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)、[Factor 5 统一执行状态与业务状态](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md)、[Factor 6 启动、暂停、恢复](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-06-launch-pause-resume.md)、[Factor 8 自己掌控控制流](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md)、[Factor 12 无状态 reducer](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-12-stateless-reducer.md)

---

## 覆盖表

✓ = 讲得深，有做过才知道的细节或设计取舍；△ = 提到了但没展开，或只讲了一个角度；空 = 基本没讲。

| 资料 | 模型接口协议 | 多厂商/网关/自部署 | 网络与可靠性 | 主循环 | 上下文构建 | 工具系统 | 执行环境与沙箱 | 互操作协议与多 agent | 会话与状态 | 长任务与后台 | 前端与客户端交互 | 多模态与文件 | 检索与记忆 | 身份与密钥 | 合规与数据治理 | 配置、发布与运营 | 评测与测试 | 可观测与成本 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. 深入理解 AI Agent | △ | △ | △ | ✓ | ✓ | ✓ | △ | ✓ | △ | △ |  | △ | ✓ |  | △ | △ | ✓ | △ |
| 2. 道雾轩两个专栏 | ✓ | △ | △ | ✓ | ✓ | ✓ | ✓ | △ | ✓ | △ | ✓ | △ | △ | △ |  | ✓ | △ | △ |
| 3. Prof Rod | △ | △ | ✓ | ✓ | △ | △ | △ | △ | ✓ | ✓ | △ |  | ✓ |  |  | △ | ✓ | ✓ |
| 4. Kocoro AI Agent 架构 |  | △ | △ | △ | △ | △ | △ | ✓ | △ | ✓ |  | △ | △ | △ | △ | ✓ |  | ✓ |
| 5. learn-agent | △ |  | ✓ | ✓ | △ | ✓ | △ | △ | △ | ✓ |  |  | △ |  |  | △ | △ |  |
| 6. Anthropic Engineering | △ | △ |  | ✓ | ✓ | ✓ | ✓ | △ | △ | △ |  |  | △ |  |  |  | ✓ |  |
| 7. AI Evals FAQ |  |  |  |  | △ |  |  |  |  |  |  |  | △ |  | △ | △ | ✓ | △ |
| 8. 12-Factor Agents |  |  |  | ✓ | ✓ | △ |  |  | △ | △ |  |  |  |  |  |  |  |  |
| **合起来仍然缺的** | Chat Completions 与 Responses 的选型、各家 SSE 事件和结束原因的差异 → [第 01 章](./01-llm-protocols.md) | 工具 schema 按厂商归一化、模型能力目录、自部署推理的 chat template 与 parser → [第 07 章](./07-providers-selfhost-multimodal.md) | 部署链路：nginx 缓冲、负载均衡空闲超时、Cloudflare 524、企业代理与自签证书 → [第 02 章](./02-reliability.md) |  |  |  |  | MCP 的部署形态、配置位置与授权，A2A/ACP 的边界 → [第 05 章](./05-mcp-design-choices.md)、[第 10 章](./10-retrieval-memory-a2a.md) | 会话分支、存储格式迁移 → [第 08 章](./08-sessions-jobs-frontend.md) |  | Web 端断线续流、“停止” 走独立接口、多端同步 → [第 08 章](./08-sessions-jobs-frontend.md) | 图片和文件的三种传法、大小上限、文件生命周期 → [第 07 章](./07-providers-selfhost-multimodal.md) | 嵌入模型换版本、删除同步 → [第 10 章](./10-retrieval-memory-a2a.md) | 代用户授权、token 保管、agent 自身身份 → [第 09 章](./09-identity-compliance-ops.md) | ZDR 的真实覆盖范围、数据驻留、删除权 → [第 09 章](./09-identity-compliance-ops.md) |  | 测试替身：假模型、HTTP 录制回放 → [第 04 章](./04-eval-observability-security.md) | 预算在并发下怎么不超额 → [第 09 章](./09-identity-compliance-ops.md) |

最缺的三块是**身份与密钥**、**合规与数据治理**、**多模态与文件**：这 8 份里没有一份讲得深。**模型接口协议**和**前端与客户端交互**各只有一份讲得深，而且只讲了一家厂商或一种客户端形态。这几块以本仓库的 docs 为主。

---

## 建议阅读顺序

1. **先搭框架（半天）**：读 12-Factor Agents 全文，再读 Anthropic 的 *Building effective agents*。先弄清楚哪些东西必须自己掌控。
2. **主干（1–2 周）**：读《深入理解 AI Agent》第 1、2、4、5 章，建立上下文、工具、错误恢复的整体图景。
3. **往下补请求层（1 周）**：通读《从 LLM 到 Coding Agent》，补流式、中断、缓存、思考签名、错误恢复的实现细节。读完对照本仓库 [01 模型接口协议](./01-llm-protocols.md)、[02 网络与可靠性](./02-reliability.md) 补齐协议选型和部署链路。
4. **往外补可靠性和服务端（1–2 周）**：读 Prof Rod 第 3、12、13 章（超时、幂等、租约），再读 Kocoro Part 7–8（Temporal、预算、多租户、策略治理）。
5. **动手（按需）**：跟着 learn-agent 跑第 11、13、14、17 章的测试，验证前面读到的边界条件。
6. **查阅**：做沙箱、权限、配置、会话存储、事件协议时，翻《Codex 源码解读》对应篇目，再看 Anthropic 的隔离和沙箱两篇。
7. **评测收尾**：读 AI Evals FAQ，配合 Anthropic 的 *Demystifying evals* 和 *infrastructure noise*，最后读《深入理解 AI Agent》第 7 章。
8. **补缺口**：身份、合规、多模态、自部署推理、Web 前端续流，直接读本仓库 docs 对应章节。
