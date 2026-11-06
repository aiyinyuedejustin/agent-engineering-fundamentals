# 选择 agent runtime：先定比较对象，再定接入方式

本页是截至 2026-11-06 UTC 已收集证据的闭合综合，不增加未核验的产品能力。来源深度以各链接文章为准：上游主要是限定范围 D3；两组自写本地实验是限定范围 D4。没有完整 benchmark、云 provider 或付费模型复现。

## 1. 不要只问“支持哪个 agent”

可比的实验至少要固定七个合同：

1. **任务合同：**输入、初始状态、可见信息、期望输出、grader 输入。
2. **控制合同：**谁决定 model/tool loop，谁决定停止，谁允许工具调用。
3. **预算合同：**限制对象是 turn、primitive action、token、费用、墙钟还是 inactivity。
4. **执行合同：**cwd、user、env、shell、TTY、输出通道、超时、取消与后台任务。
5. **观测合同：**模型实际看到什么，与 raw logs、标准轨迹、viewer 摘要有什么区别。
6. **恢复合同：**恢复对话、文件、进程、浏览器/backend、外部副作用中的哪些对象。
7. **评分合同：**agent 自报完成、程序退出、grader 得分、trial validity 和聚合分母分别如何表示。

合同在这里指明确的技术约定，不是法律协议。固定同一个模型名称和 benchmark 名称，仍可能只固定了上述七项中的很少一部分。

## 2. 接入方式是多个轴，不是互斥产品类别

| 需要保留的能力/控制 | 已读的具体方式 | 最容易忽略的代价 |
|---|---|---|
| 研究者控制 agent loop 与环境调用 | [mini-SWE-agent](coding-runtime-source-trace.md) 的模型调用、动作解析、顺序执行 | 你比较的是这个 scaffold；step/cost 边界仍须审计 |
| 保留原生 headless CLI 的规划与工具 | [Harbor installed agent](harbor-source-trace.md) 安装/配置、执行、解析原生日志 | CLI 实际版本、原生权限、子 agent 与 usage parser 进入实验条件 |
| 让外部 agent 的模型请求进入统一评测服务 | [Inspect bridge](inspect-bridge-and-trajectory.md) 路由、配置和日志接管 | 原生 model alias、生成参数、host tools 的处理可能改变行为 |
| 用统一会话协议驱动黑箱 coding agent | [OpenHands ACP](acp-black-box-agent-trace.md) initialize/session/prompt/events | 不控制内部循环；权限选择、inactivity、synthetic terminal events 需显式记录 |
| 把控制端与工作环境分开 | [remote adapters](remote-execution-contract.md)、[OpenHands remote](openhands-state-and-remote-trace.md) | transport failure 不是远端动作未执行；client wait 不是 remote kill |
| 通过页面结构或桌面观察行动 | [BrowserGym / OSWorld](computer-use-source-traces.md) | 截图、AXTree、DOM、Python 执行并非同一观测/行动能力 |
| 测澄清需求与交互式协作 | [Harbor simulated user](harbor-multi-step-and-simulated-user.md) | 用户模型、披露策略、角色权限与双角色费用一起改变评测 |

这些方式可以组合。例如，一个原生 CLI 可以在远端容器中运行，同时让模型请求经过 bridge；因此“我们用了某 runtime”不足以重建实验条件。

## 3. 三种比较问题应使用不同设计

### 比较模型

尽量固定 scaffold、工具、初始状态、预算单位、grader 和重试策略。保存**有效**请求，而非只保存用户配置：Inspect bridge 是否转发某个参数、CLI 是否自行选模型，都会影响有效条件。

若两个模型需要不同提示、工具或预算才能正常工作，应报告为两个具体系统条件，不能把全部差异归因于模型权重。是否允许适配取决于研究问题；关键是把适配内容公开。

### 比较 agent 产品或 scaffold

允许保留其原生循环与工具，但需要描述环境和权限边界，分别报告运行完整性、结果分数与资源消耗。黑箱代理缺失 usage 或内层 tool result 时，应报告不可观测，而不是补成零或以标准轨迹存在作为完整性的证明。

原生 permission bypass 与外部 sandbox 并不是等价概念。一个受控 benchmark 中允许的 CLI 配置，不应直接复制到用户电脑或有真实外部账户的环境。

### 比较 runtime / provider

固定 agent 和任务，只改变执行位置还不够。还要对齐 shell、TTY、cwd、资源限制、网络、文件传输、timeout 和 cleanup。对照 [基础设施研究](../04-infrastructure/) 中的隔离和部署维度；本目录没有完成各 provider 的性能或隔离强度横评。

最小验收不应只有“hello world 返回 0”。它还应包含：超时后是否继续写文件、后台子进程、stderr、无换行长输出、UTF-8 分块、带空格 cwd、重复请求、取消、文件下载失败和结束后的资源检查。

## 4. 一个可落地的最小实验包

以下是本文的原创建议，不是上游共有 schema：

- **Manifest：**task 与数据 revision、代码 commit、镜像 digest、agent 请求/实际版本、model provider 与标识、有效生成配置、工具权限、seed（若存在）、预算及单位、网络与资源限制、重试策略。
- **Run identity：**experiment/run/trial/attempt/step/agent-role 的不同 ID；同一逻辑操作重试保留 operation ID，同时新增 attempt ID。
- **Observations：**agent-visible output 与 raw output 分开保存；明确 truncation、media retention、stderr/TTY 与缺失项。
- **State evidence：**关键 artifacts 的 hash、远端执行 receipt、程序退出和资源停止状态；不要用同一个 boolean 代替。
- **Grade evidence：**grader 版本、实际输入 artifacts、每 key reward、异常、validity、planned/executed/graded steps 和各聚合分母。
- **Cost evidence：**每角色/每模型的原生 usage、计量单位、own/subtree/inclusive 语义、已知缺失和 parser 版本。
- **Recovery evidence：**恢复了什么、没恢复什么；是否创建 fresh session；外部副作用是否已对账。

不要把任何密码、token 或完整 secret dump 放进公开 manifest。有效配置需要可复现，但凭据应使用不可逆标识或保密引用。

## 5. 从正例走向负例

建议按以下顺序推进，先让便宜的故障暴露：

1. **静态核验：**读一个真实 task/config/grader，沿 run→action→observation→grade→cleanup 走完，不只读 README。
2. **局部原理实验：**运行 [第一组机制实验](mock-conformance-lab.md) 与 [第二组传输实验](transport-fault-lab.md)。它们不替代产品验收，但能确认你理解要测什么。
3. **单次原生验收：**在获准的实际环境中，分别运行成功、失败、超时和缺失 artifact 的受控任务。
4. **恢复与重试：**在关键边界注入故障，确认没有重复副作用、预算重置或静默漏记。
5. **规模化前：**测多任务并发、共享 backend 干扰、资源上限和 cleanup 库存。单任务正常不证明并发正常。
6. **正式比较：**固定统计方案与失败处理，不在看到结果后随意更换分母或重试失败任务。

后四步尚未在本轮上游执行。它们是清晰的下一阶段任务，而不是本轮已具备的 D4 证据。

## 6. 目前仍不能回答什么

- 各 provider 的真实尾延迟、故障率、并发公平性、取消可靠性和资源残留率。
- 所有黑箱 CLI 的日志是否完整，包括隐藏子 agent、MCP、原生联网、自动 compaction 和计费。
- 每个恢复实现是否在其真实部署中恢复了全部必要状态。
- 模拟用户对不同 target 的信息披露是否公平，其方差是否足以改变排序。
- 协议标准化是否足以让两个系统在相同任务上行为等价。

这些不是文档中出现“支持”就能解决的问题。进入 L2/L3 的下一步是执行有判别力的真实负例，保持原始证据和边界，不是继续把 D3 阅读数量当作运行能力。
