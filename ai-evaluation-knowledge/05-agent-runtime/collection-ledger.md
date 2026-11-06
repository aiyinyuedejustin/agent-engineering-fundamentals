# Agent runtime 研究收集台账

研究日期：2026-11-06 UTC。收集开始约 02:19 UTC，首次精确时钟记录 02:26:09 UTC。本目录按主题分批收集、关闭、综合；不是整个五小时研究项目的完成证明。

## 问题与边界

研究 agent 如何接入评测、在哪里执行、如何记录轨迹、如何恢复，以及执行配置怎样改变比较条件。以真实 task/config 和固定版本源码为主，不重复模型排行或全量 benchmark 名录。基础设施隔离、原始 WebArena backend reset 和 benchmark 评分生态由相邻目录覆盖，本目录只在交界处引用。

## 深度标准

- D0：发现但未核验。
- D1：已读官方论文、报告或文档。
- D2：已读实际任务、配置和关键代码。
- D3：已追踪源码执行链路。
- D4：实际运行、复现或实验。局部自写实验不等于完整 benchmark 或上游产品复现。
- L0/L1/L2/L3 分别表示知晓、理解、实践、工程能力；阅读深度不会自动换算为能力等级。

## 已关闭的主题批次

| 主题 | 已核验范围 | 结果文件 | 尚未执行或证明 |
|---|---|---|---|
| Harbor 单步/独立 verifier | trial 生命周期、installed CLI、真实 separate-verifier task、reward 解析 | harbor-source-trace.md | 没运行 Harbor/模型/容器 |
| OSWorld / BrowserGym | 实际 Calc / MiniWoB task、runner、动作与观察、getter/metric | computer-use-source-traces.md | 没执行 GUI rollout；不能推出整个 benchmark 复现 |
| Inspect bridge / trajectory | 实际 Agents SDK 示例、bridge、配置处理、ATIF、usage；logs/checkpoint 文档 | inspect-bridge-and-trajectory.md | checkpoint 文档为 D1；root helper 为局部 D2；其他按文内限定 |
| Remote adapters | Docker/Modal/Daytona/SSH 的 exec、输出、超时/cleanup 分支；ASP 草案 | remote-execution-contract.md | 未执行远端 SDK，不断言底层服务最终取消语义 |
| Coding runtime | mini-SWE-agent driver/config/loop/env；SWE-bench report/cache | coding-runtime-source-trace.md | 没执行实际 task 或 grader；真实任务细节引用 benchmark 目录 |
| UI action transport | OSWorld controller/server 超时、returncode、重试与按键清理 | computer-action-transport-addendum.md | 未证明某生产 rollout 出现相关问题 |
| OpenHands state/remote | 状态恢复、事件分支、fork、WS/REST 同步、completion、close | openhands-state-and-remote-trace.md | 只读选定执行链，不是完整 server endpoint 审计 |
| Black-box ACP | OpenHands ACP session、permission、timeout、usage、synthetic completion、重连 | acp-black-box-agent-trace.md | 没运行 ACP CLI；协议与实现的差异保留版本边界 |
| Multi-step / simulated user | 实际多步 hello task、tomlkit persona/test；阶段评分、bridge、角色 usage | harbor-multi-step-and-simulated-user.md | 没运行模拟用户；未逐项审计 hidden test patch |
| 原创机制实验 | 7 个算法 mock + 3 个真实本地机制；3 轮，30 PASS | mock-conformance-lab.md | D4 只属于自写实验 |
| 原创 transport 实验 | 6 个自写 loopback server 情形 + pipe/PTY/decoder；3 轮，27 PASS | transport-fault-lab.md | 不模拟 provider durability、网络分区、租户隔离等完整系统 |

跨主题闭合综合见 [runtime-selection-and-validation.md](runtime-selection-and-validation.md)。未知维度和后续实验见 [runtime-risk-register.md](runtime-risk-register.md) 以及各文末边界。

## 固定源码版本

| 项目 | 本轮固定 SHA |
|---|---|
| Harbor | `26f95e0ebd8c77011bbf4656f5c98af66ce55848` |
| Inspect AI | `7cf09c929b3ea9138762ca9e4d8d23f119554ee6` |
| OSWorld | `8903ebeb0efdf74331bd7dc37ed91ccbbff22317` |
| BrowserGym | `27a90ce815098f43414e93491e06907af468e45b` |
| SWE-bench | `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e` |
| mini-SWE-agent | `04d809ceab9df28f9adaed044884180159172930` |
| OpenHands software-agent-sdk | `295b3baf71dfac1be028c5b187134ec3eb495346` |

通过 GitHub 官方连接器读取 main 当前 SHA，再固定代码读取。网站文档可能变化；例如 OpenHands ACP 文档与固定实现对 MCP 的叙述存在差异，已在对应文章保留，不用一句“支持/不支持”抹平。原始源码快照保留在私有研究工作区，不进入发布知识库。发布内容只包含原作分析、固定版本链接和必要的小段标识。

## 可机器核验的证据包

- runtime-evidence-bundle.json：首轮 15 sources、10 concepts、24 claims。
- runtime-evidence-openhands.json：补充 6 sources、1 concept、15 claims。
- runtime-evidence-multistep.json：补充 3 sources、1 concept、7 claims。
- runtime-evidence-transport-lab.json：补充 4 sources、5 claims。

各补充包允许引用前包的 source/concept ID。local experiment 的公开 URL 在发布前明确为 null，由发布流程核验后添加，不能先猜一个 URL。D4 claims 只指实验脚本和实际输出，不提升产品条目的深度。

## 可证明的活动时间

- 约 02:19：开始收集；02:26:09 是首次精确时钟记录。
- 02:53:38.540408–02:53:39.438283：第一组自写实验，实际记录 30 PASS。
- 03:11:37.874043：OpenHands 补充 evidence bundle 记录时间。
- 03:29:51.096131–03:29:51.637155：第二组自写实验，实际记录 27 PASS。

本段只记录能够证明的时间点。没有独立计时器把每次检索等待与思考/写作时间分离，不能把连续研究窗口冒充精确 active time，更不能把不同任务耗时相加冒充五小时墙钟。整个研究项目的时长和后续计划需要另外核对。

## 下一阶段的判别性工作

1. 在获准的真实 provider 上执行跨层取消、重复请求与 cleanup inventory 测试。
2. 用真实 native logs 对齐 ATIF/标准事件流，测 child、usage、media、compaction 的遗漏。
3. 对同一 task 比较 native 模型请求和桥接有效请求，验证配置是否改变行为。
4. 用实际中断恢复测试文件、会话、预算和外部副作用边界。
5. 用固定 target 和多个 user policy 测模拟用户的方差与信息披露公平性。

以上为尚未执行计划。继续堆叠文档数量不能替代这些真实系统验收。
