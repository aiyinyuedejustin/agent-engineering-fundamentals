# 独立评测：版本、费用与 HLE 分数的对照边界

观察日期：2026-11-06 UTC。本批全部是 D1 / L1：读取官方方法与发布文章，未运行模型，也未审计这里的统计实现。模型分数是评测机构自己的主来源报告，不是本项目的独立复现。新增 ML114–ML122、ME230–ME252；原 229 条观察不变。

## 1. “同一个 Intelligence Index”并不是同一把尺

[AA v4.1，页面日期 2026-06-15](https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-1)更换了三个组件并重设权重：Terminal-Bench Hard→2.1，tau2 Telecom→tau3 Banking，GDPval-AA→v2；移除已饱和的 IFBench。GDPval-AA v2 同时把人类表现锚定为 Elo 1000、改用轮换的 frontier judge panel、把 turn 上限从 100 增加到 250。这里数据、预算、judge、标尺一起变化，不能只把分数移动解释成模型进步。

[v4.2，2026-09-04](https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2)加入 AA-Briefcase 与 GDP.pdf，移除 GPQA Diamond，私有/保留部分的权重从 20% 增至 40%。还修改了 AA-LCR 的 grading system prompt 与答案键，调整 GDPval-AA/Briefcase 的采样和 Elo 锚点，并让 SciCode grading sandbox 不再把慢但正确的代码视为失败。版本登记必须包含这些评分层变化，不能只列新增题目名称。

GDP.pdf 的 100 份 PDF、4,592 页、1,275 个 atomic criteria 是不同计数单位。headline All-pass Rate 要求一项任务的全部准则满足。文章中 GPT-6 Astra 33.2% 不是“只答对三分之一 rubric”，也不是逐页正确率。

[v5，2026-10-27](https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v5)增加 FrontierCode 2.0 和 Terminal-Bench-Science，以 HLE-Diamond、AA-Omniscience v1.1、CritPt v2 hard subset 替换旧版本，并移除 GDPval-AA v2.1、SciCode、AA-LCR v1.1。四类各占 25%：

- Knowledge Work：Briefcase 15%、AutomationBench-AA 5%、GDP.pdf 5%。
- Coding：FrontierCode 2.0 15%、Terminal-Bench 4.0 10%。
- Science：Terminal-Bench-Science 15%、CritPt v2 hard subset 10%。
- General：Omniscience 15%（accuracy 10%、non-hallucination 5%）、HLE-Diamond 10%。

[当前方法页](https://artificialanalysis.ai/methodology/intelligence-benchmarking)标为 **v5.0.1**，其中 Briefcase v1.1 改为 Crowd-BT 拟合，Elo 数值会移动。不能将当前设置静默回填为 v5 发布时的已确认配置。网页抽取丢失部分数学符号，本笔记不补写未经核实的精确公式。

v5 文章称“open weights”领先者 Kimi K3.1 Pro 时，又明确注明 weights not yet released。知识库应保留这种来源自带的资格限定，不能据此声称权重已可下载。

## 2. 预算不只是模型旁边的价格

v5 文章报告 Claude Opus 5.5 从 low 的 35 分提升到 max 的 58 分，Cost per Task 从 $0.98 到 $10.04。数字只说明该测量系统中的能力/消耗组合；不是同样计算量下的模型差异。文章还报告 agentic 四项占指数权重 55%，却占输出 token 中位数约 90%。权重占比不等于实际运行成本占比。

[AA 通用定义页](https://artificialanalysis.ai/methodology)区分 Model、Endpoint、System 与 Provider。同一模型在不同 endpoint 的速度、缓存、价格、错误率可不同，因此数据库至少需要模型与服务端点两个层级。

当前定义中：

- **Blended price** 使用 cache-hit / input / output 的 7:2:1 假定比例，不是观察到的每个业务任务成本。
- **Cost per Task** 按指数 benchmark 权重组合输入、缓存输入、输出 token 与价格。其价格来自第一方或提供商中位数，缓存使用近期代表性 hit rate，不只依赖评测当次。页面价格会变化。
- **Time per Task** 是由评测的 answer/reasoning token 与过去五天的代表 endpoint 输出速度推算的加权时间，**并非直接计时的评测 wall-clock**。
- 当前 **Output Speed** 用请求完整时长作分母，含 first-token 等待，并计 reasoning tokens；多轮会话排除工具运行时间。因此不能与“只算 decode 段”的 tokens/s 混合。
- **Time to First Answer Token** 包含 reasoning 等待；TTFT 可能只到首个 reasoning token。两者用于不同用户体验问题。
- **Endpoint Error Rate** 将一段多轮会话视为一个请求，任一轮失败就使会话失败；但排除无效 key、余额/本账号配额、无效/超上下文请求、研究方 max_tokens 截断、安全拦截和 sandbox error。它不是所有用户任务失败率。

早期 v4.1 文章将 per-task metrics 描述为总成本/总时间/总输出 token 除以全部任务数；当前页则给出加权和近期速度的具体定义。不能凭两份文字还原精确变更时间，也不能把旧图里的数值按今天方法重新解释。复现历史成本图需要当时价格、缓存估计、endpoint、token 用量、权重和日期。

## 3. Progress Index 是模型化链接，不是证明所有榜单等价

[Progress Index v1 官方方法](https://artificialanalysis.ai/methodology/progress-index)专用于跨年代趋势。它明确说 Intelligence Index 跨版本的分数不用于长期直接比较。

方法使用 IRT 联合估计模型能力、任务难度与区分度。有充分跨模型覆盖时用 task-level 数据，否则用 benchmark aggregate；重复运行先取平均。每个模型内部各 benchmark 等权，而不是题数越多权重越大。一个 benchmark 至少覆盖四个模型，一个模型至少覆盖四个 benchmark 才进入拟合。每种 effort variant 独立拟合，展示模型最高分 variant。

其他影响解释的处理：guessing floor 归零；AA-LCR 对 context <100k 的模型填 0；尺度锚定 o3-mini(high)=220、GPT-5.5(xhigh)=320。固定分差表示 odds 的相对变化，不等于固定百分点正确率。它的历史可比性依赖 IRT 模型、题目链接和缺失值处理，不等于实际做了完全一致的题/预算。此处未阅读实现，未核验参数或拟合稳健性。

## 4. HLE 至少需要拆成三个数据版本、多个评测者

[Scale 原 HLE 页面](https://labs.scale.com/leaderboard/humanitys_last_exam)保留原 2,500 题说明，并新增 2026-09-17 的 HLE-Rolling 更新通知。原题库经过错误修正、可搜索题审查和保留池替换，从 2,700 题缩至 2,500。不要把 Rolling 的通知日期当成原 HLE 首发日期。

[Scale Diamond 页面](https://labs.scale.com/leaderboard/hle-diamond)说明：Diamond 是清理后的 1,000 题，reasoning 与 knowledge 各 500 题，来自旧题库及 held-out reserve，固定题 ID。固定题集有利于连续比较，却不自动固定模型端点、prompt、judge 或推理预算。

AA 当前方法对原 HLE 采用 2,158 道 text-only 题；对 Diamond 则评全 1,000 题，其中 272 道带图。支持图像的模型收到图，图像仅按 provider 限制缩放；不支持图像的模型只收到文本，但仍按全部题计分。这不是统一剔除视觉题的横向比较。AA 使用官方 prompt/format 加 GPT-5.6 Luna(medium) judge；Scale 原 HLE 页面写 o3-mini-2025-01-31，而 Scale Diamond 抓取文本未明确 judge ID。不能将原 HLE 的 judge 直接赋给 Diamond。

一个刻意保留的不可合并案例：

| 来源/显示设置 | Claude Opus 5.5 | GPT-6 Astra | 可确认边界 |
|---|---:|---:|---|
| AA v5 文章，max | 68% | 64% | 评测机构自报，不是本项目复现 |
| Scale Diamond Main Results | 55.0% | 60.6% | 主表 effort、tools、judge ID 未在抓取文本明确 |
| CAIS Diamond 页面，high，无工具 | 54.6% | 59.9% | 只读当前显示的 high tab |
| 同页 high，web+code | 73.9% | 82.9% | 详细工具预算/限制链接尚未读 |

这四行不能平均成“真实分数”，也不能用排序变化来单独指控某个 judge 有偏差。需要先补齐模型 snapshot、预算、工具、图像支持、judge 与运行日期。[CAIS 页面](https://lastexam.ai/blog/hle-diamond)显示 2026-09-22，但内容可变；本项目仅能确认 2026-11-06 读取到上述显示内容，不能据文章日期推断所有模型当时已经评测。

## 5. 置信区间与校准的解读边界

Scale 页给出的 Rank(UB) 算法是：1 + 其他模型中“其 95% CI 下界高于目标 CI 上界”的个数。该规则不是直接按点估计排序；也不能据区间重叠断言两模型完全等价。这里尚未读 CI 实现，所以不宣称其区间是 paired bootstrap、Wilson 或其他特定算法。

其 RMS calibration error 来自模型自己报告的 confidence 与结果的关系，不是某个特定答案正确的概率保证。高 accuracy 与低 calibration error 是两种目标。闭卷学术题的高分也不单独证明自主研究能力，Scale 两页均明确作此限定。

## 6. 数据登记与下一步

- 来源条目 ML114–ML122 是 independent_evaluation_source_or_methodology，不是九个模型。
- ME230–ME252 都是 D1、primary_reported_not_reproduced；额外标明 independent_evaluator_or_benchmark_author。独立评测者报告不等于本项目复现。
- 不录入动态榜单抽取中错位/缺少模型标签的行；只用结构化主表和完整文章段落。
- 下一步审读 HLE source 的预测→judge→accuracy/calibration/CI 路径，并用无网络、无模型的局部输入测试统计边界。结果将另设组件记录，不提升此批模型分数的深度。
