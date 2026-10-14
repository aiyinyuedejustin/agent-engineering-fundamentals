[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

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

<a id="r3-feedback-003"></a>

### r3-feedback-003 · An update on recent Claude Code quality reports

作者／组织：Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-04-23; fixes through v2.1.116。读取日：2026-10-14。

用途：空闲后的旧 thinking 清理标志曾持续影响后续轮次，内部实验又妨碍复现；有效配置与时间路径都影响现场。

选读范围：Three causes and caching optimization。限制：thinking 缺陷在 v2.1.101 修复，三项问题至 v2.1.116 解决；不是每轮清空全部聊天，也不评价当前模型质量。

[公开原文](https://www.anthropic.com/engineering/april-23-postmortem)

<a id="r3-feedback-004"></a>

### r3-feedback-004 · Local development & testing

作者／组织：LangChain。类型：官方文档／规范。版本／日期：Live docs accessed 2026-10-14。读取日：2026-10-14。

用途：秒级热重载开发与接近生产的完整链路验证互补；本地成功不证明部署后的依赖、网络与认证正确。

选读范围：Recommended workflow; langgraph dev/up; pre-deployment checklist; dependencies。限制：命令属于特定平台；接近生产不等于与托管生产完全相同，不要求每次运行全远端矩阵。

[公开原文](https://docs.langchain.com/langsmith/local-dev-testing)

<a id="r3-feedback-009"></a>

### r3-feedback-009 · Harness engineering: leveraging Codex in an agent-first world

作者／组织：Ryan Lopopolo / OpenAI。类型：作者／团队实践或研究文章。版本／日期：2026-02-11。读取日：2026-10-14。

用途：每个 worktree 可启动的应用和可查询的局部观察，使 agent 能独立复现和验证；环境能力缺失会拖慢开发。

选读范围：Increasing application legibility; Agent legibility is the goal。限制：一个第一方产品案例；单命令小闭环是指南综合建议，未声称通用加速比。

[公开原文](https://openai.com/index/harness-engineering/)

<a id="r3-feedback-011"></a>

### r3-feedback-011 · FunctionTool ignores strict_json_schema parameter #992

作者／组织：habema; OpenAI Agents SDK issue。类型：公开问题讨论。版本／日期：2025-07-02; SDK 0.1.0; closed。读取日：2026-10-14。

用途：历史 SDK 0.1.0 手工 FunctionTool 的本地构造可成功，但生成 schema 被真实 Responses API 拒绝。

选读范围：Describe the bug; Debug information; Repro steps。限制：社区已关闭报告，未独立复现，不声明当前仍失败或已核验修复发行版。

[公开原文](https://github.com/openai/openai-agents-python/issues/992)

<a id="r3-feedback-012"></a>

### r3-feedback-012 · MCP Inspector CLI Client

作者／组织：Model Context Protocol maintainers。类型：源码／仓库文档。版本／日期：main as accessed 2026-10-14; moving branch。读取日：2026-10-14。

用途：JSON Schema 合法不保证各客户端可用；可脚本化 connect/list/call 与可区分错误有助于短集成反馈。

选读范围：Schema portability; Exit codes and error envelopes; Why use CLI。限制：阅读时 main 分支，可能与固定 Inspector 发行版不同；不推断最低兼容版本。

[公开原文](https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md)

<a id="r3-feedback-013"></a>
<a id="r3-audit-003"></a>
<a id="r3-audit-004"></a>
<a id="r3-feedback-016"></a>

### r3-feedback-013 · 异步检查点 conformance 覆盖：LangGraph PR #8537

作者／组织：LangGraph maintainers。类型：公开变更／提案。版本／日期：2026-08-07 合并；checkpoint-postgres 3.1.2 收录。读取日：2026-10-14。 引用别名：r3-audit-003、r3-audit-004、r3-feedback-016（本组合计 1 项，关联文档与版本复核不另计）。

用途：维护者补齐 SQLite 依赖和 Postgres runner，揭示此前关键 conformance 静默跳过或未运行；新增范围仍主要是 async savers。

选读范围：PR description；缺失 SQLite conformance 依赖及 Postgres runner 的说明；async-only 范围；review 与 merge timeline。限制：是同一迁移/契约事故的佐证，不扩写成同步后端全覆盖或全项目无测试；不额外计数。

已读关联文档／版本（同一计数组）：
- r3-audit-003：2026-08-07 合并；checkpoint-postgres 3.1.2 收录；范围：PR description；缺失 SQLite conformance 依赖及 Postgres runner 的说明；async-only 范围；review 与 merge timeline；补充复核，不新增计数。[该记录原文](https://github.com/langchain-ai/langgraph/pull/8537)
- r3-audit-004：checkpoint-postgres 3.1.2；发布条目核验于 2026-10-14；范围：release What’s Changed 中 #8535 与 #8537 条目；补充复核，不新增计数。[该记录原文](https://github.com/langchain-ai/langgraph/releases/tag/checkpointpostgres==3.1.2)
- r3-feedback-013：2026-08-05; closed by #8535；范围：Cause; Repro; Impact; Why it went unnoticed。[该记录原文](https://github.com/langchain-ai/langgraph/issues/8534)
- r3-feedback-016：2026-08-07 合并；checkpoint-postgres 3.1.2 收录；范围：PR review and #8537 commit excerpts；补充复核，不新增计数。[该记录原文](https://github.com/langchain-ai/langgraph/pull/8535)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://github.com/langchain-ai/langgraph/pull/8537)

<a id="traces-eval-004"></a>

### traces-eval-004 · Demystifying evals for AI agents

作者／组织：Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe / Anthropic。类型：作者／团队实践或研究文章。版本／日期：2026-01-09。读取日：2026-10-13。

用途：必须区分 transcript 里声称完成与环境 outcome 真正完成，例如预订记录是否存在于数据库。评估对象是模型与 harness 的组合。

阅读范围：Structure; non-determinism; roadmap steps 1–8。限制：案例来自作者内外部实践，建议非严格普遍定律；不是 benchmark 排名证据

[公开原文](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

<a id="traces-eval-010"></a>
<a id="r3-feedback-006"></a>

### traces-eval-010 · Unit testing - Pydantic AI

作者／组织：Pydantic。类型：官方文档／规范。版本／日期：current 2026-10-13。读取日：2026-10-13。 引用别名：r3-feedback-006（本组合计 1 项，关联文档与版本复核不另计）。

用途：harness 单元测试可替换模型并硬性关闭真实模型请求，避免延迟、费用及随机性进入逻辑回归。

阅读范围：Unit testing with TestModel; FunctionModel; fixtures。限制：Mock 通过仅说明脚本路径，不能证明模型会选择正确动作

已读关联文档／版本（同一计数组）：
- r3-feedback-006：Live docs accessed 2026-10-14；范围：TestModel is not magic; FunctionModel weather counterexample；补充复核，不新增计数。[该记录原文](https://pydantic.dev/docs/ai/guides/testing/)
- traces-eval-010：current 2026-10-13；范围：Unit testing with TestModel; FunctionModel; fixtures。[该记录原文](https://ai.pydantic.dev/testing/)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

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

作者／组织：Ankur Goyal / Braintrust, Vercel guest post。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。 引用别名：practitioner-lessons-019（本组合计 1 项，关联文档与版本复核不另计）。

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

[返回分类目录](README.md#topics)
