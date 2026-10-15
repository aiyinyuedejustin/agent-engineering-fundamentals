# Claude App 工程全书

按“界面承载什么 → 动作怎样执行 → 数据怎样流动 → 产品怎样演化”阅读。核心主线与扩展专题把结构、条件和可复用实现放在一起；源码定位集中在证据附录。主要静态样本为 Claude Desktop 2.37337.1，公开产品与移动资料的观察日期另列在各卷。

## 十卷主线

1. [整体架构与多进程协同](01-System-Architecture/README.md)：窗口、内容、进程与桥接。
2. [Agent Loop 执行引擎](02-Agent-Loop-Engine/README.md)：turn、run、权限、恢复与执行生命周期。
3. [Computer Use 与 Cowork](03-Computer-Use-And-Cowork/README.md)：屏幕、输入、终端、主机与虚拟机。
4. [Prompt 与协议解析](04-Prompts-And-Protocols/README.md)：请求契约、标签、SSE 与增量解析。
5. [上下文与文件管线](05-Context-And-File-Pipeline/README.md)：文件、图像、预处理、生命周期与预算。
6. [MCP 宿主与扩展边界](06-MCP-Host-Internals/README.md)：配置、启动、连接、工具授权与退出。
7. [Artifacts 与沙箱](07-Artifacts-And-Sandbox/README.md)：版本、渲染、预览与能力隔离。
8. [对话树与流式状态](08-Conversation-Tree-And-Streaming/README.md)：分支、增量拼装、调度与中止。
9. [Memory、Projects 与 Styles](09-Memory-Projects-And-Styles/README.md)：跨轮信息、项目知识与个性化。
10. [Feature Flags 与版本演化](10-Feature-Flags-And-Evolution/README.md)：条件组合、能力发现与兼容结构。

## 深入专题

- [第 11 卷：流式性能与分层调度](11-Performance-And-Streaming/README.md)：稳定块与尾块、高亮 Worker、图表队列、虚拟化与资源生命周期。

- [第 13 卷：原生系统桥接](13-Native-OS-Bridges/README.md)：快捷键、系统入口、选择文本与编辑目标重验证。
- [第 14 卷：安全防线与执行边界](14-Security-And-Guardrails/README.md)：内容信任、命令语义、资源身份、外链与敏感字段存储。

- [第 15 卷：语音与视觉数学](15-Voice-And-Vision-Math/README.md)：采样、播放、打断、显示器坐标与 PDF 仿射变换。

## 平台与恢复专题

- [第 17 卷：状态、恢复与更新](17-State-Recovery-And-Updates/README.md)
- [第 18 卷：版本与跨平台](18-Versions-And-Cross-Platform/README.md)
- [第 19 卷：iOS / Android 的界面与交互边界](19-Mobile-Surfaces/README.md)

## 一页阅读准备

### 需要哪些基础

能阅读 JavaScript 对象、数组、函数和 async/await 即可开始。遇到异步迭代、事件监听、AbortController、React 状态或缓存时，先按“输入是什么、状态由谁持有、什么时候失效”读图，再回看代码。第 2、3 卷的练习使用 Python；运行全部原创实验需要 Node.js 20+ 和 Python 3.10+，不需要 Claude 账号或产品文件。颜色分析工具的实际提取另需合法取得的样本，默认合成测试不需要。

### 先区分六组概念

- 进程与窗口：进程负责执行与隔离，窗口承载界面；窗口关闭不自动证明所有后台工作结束。
- IPC 与网络协议：IPC 连接应用进程；HTTP、SSE 和 JSON-RPC 分别承担不同的通信工作。SSE 分片不必恰好对应一个事件。
- session、turn 与 run：会话、一次交互和一次执行的生命周期可能不同；各卷会注明具体代码中的含义。
- 数据与权限：知道文件路径、收到工具请求、显示为可用，都不等于获得执行许可。要继续找到负责判断和执行的边界。
- 客户端状态与服务端事实：乐观更新、估算预算和缓存命中可以解释界面行为，不能补出服务端持久化、tokenizer 或完整上下文算法。
- 产品证据与教学模型：正文中的条件分支来自固定样本；实验代码是原创、简化、可测试的模型，其中的更严格拒绝策略不能倒推为产品保证。

### 怎么选阅读路线

- 从架构入门：1 → 2 → 3 → 6，跟踪“用户输入到工具执行”的责任交接。
- 研究聊天数据流：4 → 5 → 8，跟踪输入、请求、事件、消息树与显示。
- 研究工作区与个性化：7 → 9 → 10，再用 17、18 理解恢复和版本条件。
- 研究移动体验：先读 19，再用 18 核对哪些桌面结论可以迁移；商店宣传图不能替代原生运行测量。

每卷先读开头和总图，再挑一个失败、取消或过期场景沿调用链追踪。最后进入[原创代码实验室](../04-Extracted-Core-Code-And-Scripts/core-code-lab/README.md)，运行对应模型和测试。图是解释工具，证据编号连接到短锚点、文件摘要与限制；结论的成立条件比单个函数名字更重要。

## 复核入口

[证据方法与复现范围](../04-Extracted-Core-Code-And-Scripts/evidence/README.md)说明如何区分静态事实、公开说明与实际观察。[本轮纠错摘要](../04-Extracted-Core-Code-And-Scripts/evidence/data/book-corrections.json)记录纳入本书的 20 项已复核修正；各卷的证据链接保留具体条件与短定位。出版物不附安装包、完整模块、完整专有提示词、原始提取图或账户数据。

[返回全仓导航](../README.md) · [先看前端设计](../01-Frontend-Design-And-HTML-Templates/README.md)
