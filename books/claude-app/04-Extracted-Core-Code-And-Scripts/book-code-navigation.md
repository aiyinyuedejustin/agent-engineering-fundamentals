# 19 卷代码与测试导航

从正文中的一个问题进入实现，再看测试怎样构造正常、失败、取消与过期输入。下表列的是每卷的起步路径，不是全部代码清单；多个卷共用模型时不算作新增实现。所有实现均为本书原创教学模型或分析工具，不是产品源码，也不是官方 SDK。

## 先确定运行范围

- 只运行[基础五模块](core-code-lab/README.md)：Node.js 20+、Python 3.10+，按该目录 README 运行。
- 运行[全书统一入口](README.md#一条命令运行已收录的原创模型)：Node.js 22+、Python 3.10+。预览超时实验使用内置虚拟定时器接口；不要把五模块的最低版本直接当成全书前提。
- 单独运行某个实验：先进入该行“学习入口”的目录，再按它的 README 执行。测试列是可阅读的首个合同，不是让读者在任意工作目录运行一个文件就代替完整测试组。

在本文件所在目录 `04-Extracted-Core-Code-And-Scripts/` 中：

```sh
python3 -B run_book_tests.py --list
python3 -B run_book_tests.py
python3 -B run_book_tests.py --skills
```

`--list` 只列测试组，但仍检查 Node.js 版本；默认命令运行已登记的离线模型。`--skills` 额外核验独立复制的 Skill 模型，不增加算法覆盖。统一入口不安装依赖、不联网、不执行目标产品；前端 DOM/浏览器检查和逆向工具箱另有入口。

## 从卷到代码

下表第 1–17 卷的起步模型都使用原创合成输入，不需要 Claude 账号、安装包或真实设备。第 17 卷会在自有临时目录和子进程中做文件实验，不是掉电耐久性测试。

| 卷与正文 | 学习入口：先理解什么 | 原创实现 | 先读的测试 |
|---|---|---|---|
| [01 整体架构与多进程协同](../02-Illustrated-Deep-Dive-Book/01-System-Architecture/README.md) | [导航代际与退出结算](shell-lifecycle/README.md) | [lifecycle.mjs](shell-lifecycle/lifecycle.mjs) | [lifecycle.test.mjs](shell-lifecycle/lifecycle.test.mjs) |
| [02 Agent Loop 执行引擎](../02-Illustrated-Deep-Dive-Book/02-Agent-Loop-Engine/README.md) | [会话代际与审批消费](core-code-lab/loop-cowork/README.md) | [model.py](core-code-lab/loop-cowork/model.py) | [test_model.py](core-code-lab/loop-cowork/test_model.py) |
| [03 Computer Use 与 Cowork](../02-Illustrated-Deep-Dive-Book/03-Computer-Use-And-Cowork/README.md) | [逐动作授权与坐标边界](core-code-lab/loop-cowork/README.md) | [model.py](core-code-lab/loop-cowork/model.py) | [test_model.py](core-code-lab/loop-cowork/test_model.py) |
| [04 Prompt 与协议解析](../02-Illustrated-Deep-Dive-Book/04-Prompts-And-Protocols/README.md) | [增量 UTF-8 / SSE](core-code-lab/protocol-tree/README.md) | [incremental-sse.mjs](core-code-lab/protocol-tree/incremental-sse.mjs) | [protocol.test.mjs](core-code-lab/protocol-tree/test/protocol.test.mjs) |
| [05 上下文与文件管线](../02-Illustrated-Deep-Dive-Book/05-Context-And-File-Pipeline/README.md) | [UTF-8 预算与附件身份](worked-cases/README.md) | [context_budget.mjs](worked-cases/context_budget.mjs) | [context_budget.test.mjs](worked-cases/context_budget.test.mjs) |
| [06 MCP 宿主与扩展边界](../02-Illustrated-Deep-Dive-Book/06-MCP-Host-Internals/README.md) | [审批绑定与过期拒绝](worked-cases/README.md) | [mcp_binding.py](worked-cases/mcp_binding.py) | [test_worked_cases.py](worked-cases/test_worked_cases.py) |
| [07 Artifacts 与沙箱](../02-Illustrated-Deep-Dive-Book/07-Artifacts-And-Sandbox/README.md) | [版本选择与内容 epoch](core-code-lab/workspace-core/README.md) | [workspaces-model.mjs](core-code-lab/workspace-core/workspaces-model.mjs) | [workspaces-model.test.mjs](core-code-lab/workspace-core/workspaces-model.test.mjs) |
| [08 对话树与流式状态](../02-Illustrated-Deep-Dive-Book/08-Conversation-Tree-And-Streaming/README.md) | [分支与可见路径](core-code-lab/protocol-tree/README.md) | [branch-manager.mjs](core-code-lab/protocol-tree/branch-manager.mjs) | [branches.test.mjs](core-code-lab/protocol-tree/test/branches.test.mjs) |
| [09 Memory、Projects 与 Styles](../02-Illustrated-Deep-Dive-Book/09-Memory-Projects-And-Styles/README.md) | [顺序写入与过期响应](core-code-lab/memory-flags/README.md) | [memory-flags-model.mjs](core-code-lab/memory-flags/memory-flags-model.mjs) | [memory-flags-model.test.mjs](core-code-lab/memory-flags/memory-flags-model.test.mjs) |
| [10 Feature Flags 与版本演化](../02-Illustrated-Deep-Dive-Book/10-Feature-Flags-And-Evolution/README.md) | [能力依赖与访问快照](core-code-lab/memory-flags/README.md) | [memory-flags-model.mjs](core-code-lab/memory-flags/memory-flags-model.mjs) | [memory-flags-model.test.mjs](core-code-lab/memory-flags/memory-flags-model.test.mjs) |
| [11 流式性能与分层调度](../02-Illustrated-Deep-Dive-Book/11-Performance-And-Streaming/README.md) | [增量调度与资源寿命](streaming-performance/README.md) | [model.mjs](streaming-performance/model.mjs) | [model.test.mjs](streaming-performance/test/model.test.mjs) |
| [12 遥测事件与指标设计](../02-Illustrated-Deep-Dive-Book/12-Telemetry-And-Product-Metrics/README.md) | [合成事件与指标分母](../02-Illustrated-Deep-Dive-Book/12-Telemetry-And-Product-Metrics/metrics-lab/README.md) | [metrics_lab.py](../02-Illustrated-Deep-Dive-Book/12-Telemetry-And-Product-Metrics/metrics-lab/metrics_lab.py) | [test_metrics_lab.py](../02-Illustrated-Deep-Dive-Book/12-Telemetry-And-Product-Metrics/metrics-lab/test_metrics_lab.py) |
| [13 原生系统桥接](../02-Illustrated-Deep-Dive-Book/13-Native-OS-Bridges/README.md) | [目标身份重验证](native-voice-geometry/README.md) | [native-state.mjs](native-voice-geometry/native-state.mjs) | [models.test.mjs](native-voice-geometry/models.test.mjs) |
| [14 安全防线与执行边界](../02-Illustrated-Deep-Dive-Book/14-Security-And-Guardrails/README.md) | [审批、资源与外链边界](security-guardrails/README.md) | [guardrails.mjs](security-guardrails/guardrails.mjs) | [guardrails.test.mjs](security-guardrails/guardrails.test.mjs) |
| [15 语音与视觉数学](../02-Illustrated-Deep-Dive-Book/15-Voice-And-Vision-Math/README.md) | [音频账本与坐标变换](native-voice-geometry/README.md) | [audio-state.mjs](native-voice-geometry/audio-state.mjs) | [models.test.mjs](native-voice-geometry/models.test.mjs) |
| [16 恢复、限流与配额](../02-Illustrated-Deep-Dive-Book/16-Resilience-And-Quota/README.md) | [重试分类与恢复身份](resilience-quota/README.md) | [resilience-core.mjs](resilience-quota/resilience-core.mjs) | [resilience.test.mjs](resilience-quota/test/resilience.test.mjs) |
| [17 状态、恢复与更新](../02-Illustrated-Deep-Dive-Book/17-State-Recovery-And-Updates/README.md) | [write / rename / commit 切点](crash-cut-recovery/README.md) | [protocol.py](crash-cut-recovery/protocol.py) | [test_crash_cuts.py](crash-cut-recovery/test_crash_cuts.py) |
| [18 版本与跨平台](../02-Illustrated-Deep-Dive-Book/18-Versions-And-Cross-Platform/README.md) | 路径集合、原始摘要、CRLF 与实例去重的四类结果 | [lesson.py](../02-Illustrated-Deep-Dive-Book/18-Versions-And-Cross-Platform/lab/lesson.py)，直接调用 [compare_ui_trees.py](scripts/compare_ui_trees.py) | [10 项合成测试](../02-Illustrated-Deep-Dive-Book/18-Versions-And-Cross-Platform/lab/test_lesson.py)已纳入统一入口；真实样本独立复算仍需三份已解包 resources，执行成功不代表相等或整包认证 |
| [19 移动界面与交互边界](../02-Illustrated-Deep-Dive-Book/19-Mobile-Surfaces/README.md) | 正文“可复用的下一轮原生验证清单” | 本卷未交付原生实现 | 计划尚待授权、设备与测试账户后执行；公开文档和宣传图不替代真机测试 |

## 主线读完后的对应深入

这些入口已有正文或模型，按正在追踪的失败情形选读，不必全跑一遍才能理解主线。

- 第 2/5/6 卷：[三个手算案例](worked-cases/README.md)，把 Stop/restart、UTF-8 预留和 MCP 审批拆成时间线；附件另有[交互课](../01-Frontend-Design-And-HTML-Templates/interactive-lessons/attachment-pipeline/README.md)。
- 第 4 卷：[工具合同](tool-contracts/README.md)，对照[模型](tool-contracts/contract-lab.mjs)与[测试](tool-contracts/test/contract-lab.test.mjs)，区分形状校验、适配、权限与执行。
- 第 7 卷：[预览超时双账本](worked-cases/sandbox-timeout/README.md)，区分调用方结算与后台工作结束。
- 第 8/9 卷：[两个状态转移案例](worked-cases/state-transitions/README.md)，逐步看消息身份重命名和组织切换。
- 第 9/11 卷：[条件写入与流式工作粒度](worked-cases/concurrency-and-streaming/README.md)，检查旧快照覆盖及大输入块中的取消检查点。
- 第 13 卷：[Linux 原生层研究与原创回调模型](../02-Illustrated-Deep-Dive-Book/13-Native-OS-Bridges/linux-native-layer/README.md)；读[callback-gate.mjs](../02-Illustrated-Deep-Dive-Book/13-Native-OS-Bridges/linux-native-layer/examples/callback-gate.mjs)、[模型测试](../02-Illustrated-Deep-Dive-Book/13-Native-OS-Bridges/linux-native-layer/examples/callback-gate.test.mjs)及[独立反例](../02-Illustrated-Deep-Dive-Book/13-Native-OS-Bridges/linux-native-layer/examples/callback-gate.audit.test.mjs)。两份测试已纳入统一入口的 `native-callback-lifetime` 组；资源只是合成 JS 对象，不验证真实线程、fd、PipeWire 或 native 权限。
- 第 15 卷：从[geometry.mjs](native-voice-geometry/geometry.mjs)继续追坐标换算，再看同目录完整测试与[手算输出](native-voice-geometry/worked-examples.json)。
- 第 16 卷：从[recovery-state.mjs](resilience-quota/recovery-state.mjs)补上订阅游标和草稿恢复；不要将重连当作任务重发。

## 版本研究、静态候选与独立验证

第 10/18 卷涉及的[自动逆向工具箱](../05-Automated-Reverse-Toolkit/README.md)不属于 `run_book_tests.py` 的模型集合。先读[扫描诊断与解释边界](../05-Automated-Reverse-Toolkit/SCANNER-DIAGNOSTICS.md)，再决定是在运行合成回归，还是对有权读取的产品样本生成候选清单。

从 `05-Automated-Reverse-Toolkit/` 目录分别运行：

```sh
python3 -B run_tests.py
python3 -B tests/test_scanner_diagnostics.py
python3 -B probes/known_lexical_limitations.py
```

第二行单独定位诊断合同，其测试已包含在默认套件中；不要重复计功。第三行是独立的已知局限探针，不在默认绿色套件中。输出 `expected-limitation-reproduced`、`fixed=false` 和退出 0 表示成功重现尚未修复的假候选，不表示扫描正确。`scanned` 与声明范围内覆盖完成也不证明语义完整、运行可达或产品行为已发生。

## 六套前端模板的测试另行运行

[六模板入口](../01-Frontend-Design-And-HTML-Templates/templates/README.md) → [静态与模拟 DOM 测试说明](../01-Frontend-Design-And-HTML-Templates/templates/tests/README.md) → [浏览器验收清单](../01-Frontend-Design-And-HTML-Templates/templates/QA-CHECKLIST.md)。页面本身无需依赖；测试使用单独的开发依赖，不能混入零依赖模型的结论。浏览器截图、键盘焦点、CSP、file URL、真实输入法与辅助技术应按各记录的具体环境和覆盖项判断。

## 结果究竟证明什么

模型测试通过，只说明这些原创输入下的局部合同成立；样本复算只证明其声明范围内的字节比较；已知局限探针成功说明问题可重现。三者均不能证明目标产品的真实安全性、性能、当前账户行为或完整协议兼容。每卷的证据边界和未验证项仍然适用。

[返回全书目录](../02-Illustrated-Deep-Dive-Book/README.md) · [返回核心实现与研究工具](README.md)

- 第13卷的资源所有权补充：[资源交付与回收实验](resource-handoff-lab/README.md)以offer/claim区分Promise到达与资源接管，包含取得前后取消、数字复用和清理失败反例。
