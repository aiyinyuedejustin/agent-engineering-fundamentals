[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

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

[返回分类目录](README.md#topics)
