[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

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

阅读范围：Original report; timeline。限制：仅用户报告，不把约30%配额或其根因猜测当普遍统计；与 [loop-context-024](topic-09.md#loop-context-024)不假设同一根因。

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

[返回分类目录](README.md#topics)
