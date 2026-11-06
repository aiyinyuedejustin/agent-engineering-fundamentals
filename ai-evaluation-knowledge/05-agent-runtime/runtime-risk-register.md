# Runtime 风险登记：把未知变成可检查的问题

本登记不是已发现 bug 的清单，也不声称枚举所有 unknown unknowns。它从本目录已读实现提取容易被漏掉的维度，明确哪些事实已知、哪些还需要试验。日期：2026-11-06 UTC。

## 1. 已知证据与尚未验证的后果

| 检查点 | 已有证据 | 当前未知 | 最小有判别力的下一步 |
|---|---|---|---|
| CLI 实际版本 | Harbor skip_install 后仍 configure/检测版本 | 镜像中的 CLI 和请求版本是否一致 | 保存检测版本、镜像 digest、有效 config |
| 模型桥接 | Inspect 可重定向 model，默认不转发 generation 参数 | 与原生运行行为偏差多大 | 固定 agent，录制 bridge 开/关的有效请求 |
| 隐藏网络 | host tools/provider native tools 是独立能力路径 | 任务的所有 egress 是否符合声明 | 各路径单独发无害探针，不只测容器 curl |
| 预算单位 | mini/OSWorld 的 turn 可包含多个动作 | 不同报告的 step 含义是否相同 | 同时记录 model calls、actions、wall clock、tokens |
| 预算恢复 | Inspect checkpoint 有 root usage 和 nested scope 边界 | 恢复是否改变可用预算 | crash/retry 前后比对计数和有效剩余额度 |
| 终止状态 | Submitted/DONE 与 grader 成功独立 | 上层 dashboard 是否混合状态 | 测空输出、错输出和正确输出三个正反例 |
| Cache identity | SWE-bench report key 不含 patch hash | 重跑是否使用旧报告 | 变 patch 不变 key，再用新 key 对照 |
| 轨迹完整性 | ATIF references valid 不意味着每次调用有结果 | child/media/usage 是否漏记 | 删除单个结果、child 文件或图片做负例 |
| 子 agent 成本 | 已读 Codex parent metrics 包含 descendants | 每个 producer 的 total 语义是否一致 | 明确 own/subtree 字段，再对原生 counters |
| 输出留存 | head/tail、日志摘要、media retention 有区别 | grader/研究者是否看见模型没看见的文本 | 保存 raw 与 agent-visible output 各自 hash |
| 远端取消 | adapter 的等待、SDK、进程、环境 stop 分层 | cancellation 后远端实际状态 | 同时观测 client return、remote exit、最后写入 |
| 背景工作 | Daytona session 明确保留 background children | grade 前 artifact 是否仍变化 | 连续测 artifact hash 和进程树，规定 quiescence |
| UI 按键状态 | OSWorld stranded-input cleanup 是 best effort | modifier/focus 等是否污染下一步 | 中断 keyDown，读取状态并进行受控后续动作 |
| HTTP 与程序错误 | OSWorld 普通路径不直接传递 command dict | error observability 对 agent 影响多大 | HTTP 200 + nonzero returncode 与正常操作对照 |
| 动作权限 | Python action endpoint 本身不是 GUI-only allowlist | 某 agent 是否真的仅用 GUI | 审计 wrapper 和实际 trace，加负例执行约束测试 |
| Grader 输入 | separate verifier 只搬运声明 artifacts | 是否漏依赖、是否解析不可信输入 | shared/separate 同 artifact 复评及损坏产物测试 |
| 清理确认 | stop/delete/retain 是不同分支 | 是否残留资源、访问凭证或文件 | 结束后 resource inventory，与期望状态比对 |
| 数据/镜像漂移 | 固定代码仍可能使用 dataset 未固定 revision 或 :latest | 重跑环境是否相同 | 把所有可变引用解析并记录不可变身份 |

对应来源详见 [Harbor trace](harbor-source-trace.md)、[Inspect/trajectory](inspect-bridge-and-trajectory.md)、[remote exec](remote-execution-contract.md)、[coding runtime](coding-runtime-source-trace.md)、[computer-use](computer-use-source-traces.md) 和 [action transport](computer-action-transport-addendum.md)。上表未验证后果是 D0 待测问题，不因附近有 D3 代码证据而自动成为已复现结论。

## 2. 发现 unknown unknowns 的方法

### 比较相同名字背后的不同对象

看到 step、timeout、success、session、snapshot、sandbox、total 等词时，先列出其对象和边界：模型轮次还是 primitive action，客户端还是远端，run 身份还是 trajectory 身份，文件快照还是运行进程，own usage 还是 subtree total。很多差异来自复用同一个词，而不是公式写错。

### 沿不成功路径继续读

从 happy path 的 finally、retry、exception、fallback 和 cache hit 开始扩展。确认“报错以后还会不会 grade”“cleanup 失败会不会变成 warning”“partial logs 会不会当成 empty”。本轮最有价值的差异多数在这些分支，而不是接口定义。

### 让观测本身接受测试

给输出加唯一 marker，分别放在中间、stderr、无换行长行、child agent、媒体附件和远端 artifact 中。比较 native logs、标准轨迹、agent-visible observation、viewer summary 与最终 report。丢失一个 marker 不等于任务失败，但会限制能够解释的结论。

### 用两种独立观测识别未完成动作

控制面说 timeout 不够，还要看数据面是否继续写入；日志说 success 不够，还要读目标状态；schema valid 不够，还要核对原生计数。没有第二条证据时，使用 unknown 而不是 false/zero。

## 3. 优先级与停止条件

1. 先验证可能改变 score、分母或任务难度的项：grader边界、budget、cache、工具权限、reset。
2. 再验证影响归因的项：有效请求、轨迹完整性、成本和子 agent 计数。
3. 在需要大量并发或长任务前，验证远端 cancellation、checkpoint 和 cleanup。
4. 只有研究问题确实需要时才扩展供应商性能或隔离强度比较，避免把“兼容性调试”变成没有终点的平台清单。

一个场景完成的标准不是“所有表格填满”，而是关键比较条件已固定、每个重要未知有明确处理方式、失败和缺失数据不会被静默混入结论。尚未执行的测试始终保留为计划。

## 4. 与能力层级的关系

- **L0：**能认出 agent、harness、environment、grader、trajectory 这些对象。
- **L1：**能解释本表中的边界，并指出某条证据不能支持什么。
- **L2：**能复跑 [本地机制实验](mock-conformance-lab.md)，并在真实任务上保存足够的 manifest 和负例。
- **L3：**能在真实部署中实现/验证故障恢复、可比性、证据完整性和资源回收。

D3 阅读不自动授予 L3；本轮局部 D4 mock 也不等于真实系统工程能力已验证。
