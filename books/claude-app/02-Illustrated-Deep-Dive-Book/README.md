# Claude App 工程全书

按“界面承载什么 → 动作怎样执行 → 数据怎样流动 → 产品怎样演化”阅读。每卷把结构、条件和可复用实现放在一起；源码定位集中在证据附录。

## 已有章节

- [第 1 卷：整体架构与多进程协同](01-System-Architecture/README.md)
- [第 5 卷：上下文与文件管线](05-Context-And-File-Pipeline/README.md)
- [第 6 卷：MCP 宿主与扩展边界](06-MCP-Host-Internals/README.md)
- [专题：状态、恢复与更新](11-State-Recovery-And-Updates/README.md)
- [专题：版本与跨平台](12-Versions-And-Cross-Platform/README.md)

## 主线编排

1. 整体架构：窗口、内容、进程与桥接。
2. Agent Loop：turn、run、权限与执行生命周期。
3. Computer Use：屏幕、输入、终端、主机与虚拟机。
4. Prompt 与协议：工具契约、标签与事件解析。
5. 上下文管线：文件、图像、预处理与预算。
6. MCP 宿主：配置、启动、连接、工具授权与退出。
7. Artifacts：版本、渲染、预览与能力隔离。
8. 对话与流式状态：分支、增量拼装与调度。
9. Memory / Projects / Styles：跨轮信息与个性化。
10. Feature Flags：条件组合、能力发现与版本演化。

[返回全仓导航](../README.md) · [先看前端设计](../01-Frontend-Design-And-HTML-Templates/README.md)
