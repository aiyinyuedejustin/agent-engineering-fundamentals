# 拆开 Claude App

### 从一块温暖的背景色，到一套能执行任务的桌面系统

这本书把 Claude App 拆成两条阅读路线：**看得见的设计，拿来做网页；看不见的机制，拿来做系统。** 色板、组件、状态机和代码放在一起，读完一节就能进入对应的实现。

![Claude App：界面、状态、能力与执行的全景关系](assets/figures/book-panorama.svg)

## 先挑一个入口

| 想做什么 | 直接打开 | 一句话精华 |
|---|---|---|
| 做一个有阅读感的网页 | [前端审美与设计系统](01-Frontend-Design-And-HTML-Templates/README.md) · [设计速查](01-Frontend-Design-And-HTML-Templates/quick-reference.md) | 温暖来自大面与文字的关系，不来自把每个按钮染成橙色 |
| 看组件怎样响应操作 | [原创交互工作台](01-Frontend-Design-And-HTML-Templates/interactive-study/index.html) · [运行说明](01-Frontend-Design-And-HTML-Templates/interactive-study/README.md) | 密度、阅读字号、输入状态和 Quick Entry 可以独立研究 |
| 理解桌面产品的内部组织 | [技术全书目录](02-Illustrated-Deep-Dive-Book/README.md) | 窗口、内容、能力与执行拥有不同的生命周期 |
| 让另一个 agent 接着做 | [Skills 导航](03-Ready-To-Use-Agent-Skills/README.md) | 把选型依据、反例和代码入口一起交给 agent |
| 复算参数或研究新版本 | [代码与脚本](04-Extracted-Core-Code-And-Scripts/README.md) | 重要结论能追到输入，也能从输入重新算出来 |

## 前端：先看图，再看代码

[![浅深色板](assets/figures/cds-palette.svg)](01-Frontend-Design-And-HTML-Templates/README.md#01-色板与主题)

[![输入面与卡片解剖](assets/figures/component-anatomy.svg)](01-Frontend-Design-And-HTML-Templates/README.md#04-组件解剖)

- [色块与边界](assets/figures/color-block-anatomy.svg)：阅读画布、消息、输入区与临时浮层，各自承担什么。
- [密度与文字](assets/figures/density-comparison.svg)：控件密度与长文阅读不必绑在一起。
- [基础样式](01-Frontend-Design-And-HTML-Templates/styles/README.md)：变量、组件与页面布局的三层分工。

[完整交互色表](01-Frontend-Design-And-HTML-Templates/color-catalog/index.html)已可使用：315 个原始色阶，连同主题与桥接记录共 1,341 项。六套零依赖 HTML 模板可直接下载打开；模板内嵌 CSS 和 JavaScript，交互只使用本地演示数据。

- [组件交互画廊](01-Frontend-Design-And-HTML-Templates/templates/01-component-gallery.html)
- [对话工作台](01-Frontend-Design-And-HTML-Templates/templates/02-chat-workspace-template.html)
- [分屏代码与预览](01-Frontend-Design-And-HTML-Templates/templates/03-split-artifact-ide-template.html)
- [技术博客与文档](01-Frontend-Design-And-HTML-Templates/templates/04-editorial-blog-and-doc-template.html)
- [设置与数据看板](01-Frontend-Design-And-HTML-Templates/templates/05-settings-and-dashboard-template.html)
- [Quick Entry 指令面板](01-Frontend-Design-And-HTML-Templates/templates/06-floating-launcher-template.html)

## 技术全书：十卷主线，专题补充

| 卷 | 主题 | 要解决的问题 |
|---|---|---|
| 01 | [整体架构与多进程协同](02-Illustrated-Deep-Dive-Book/01-System-Architecture/README.md) | 一个窗口后面，哪些东西一起活、哪些东西分别活？ |
| 02 | Agent Loop 与执行状态机 | 一次回复结束，为什么执行进程未必结束？ |
| 03 | Computer Use 与 Cowork | 主机、虚拟机、终端和屏幕操作怎样分工？ |
| 04 | Prompt、工具契约与解析 | 从连续字节到可执行动作，中间有哪些结构边界？ |
| 05 | [上下文与文件管线](02-Illustrated-Deep-Dive-Book/05-Context-And-File-Pipeline/README.md) | 拖入一个文件后，哪些工作在本地，哪些交给服务？ |
| 06 | [MCP 宿主与扩展](02-Illustrated-Deep-Dive-Book/06-MCP-Host-Internals/README.md) | 安装一个工具，为什么还不等于可以调用它？ |
| 07 | Artifacts 与预览沙盒 | 怎样让生成代码可见、可交互，又不拿到宿主能力？ |
| 08 | 对话分支与流式渲染 | 编辑、重试和连续输出如何保持一致？ |
| 09 | Memory、Projects 与 Styles | 跨对话信息和当前轮输入怎样分层组织？ |
| 10 | Feature Flags 与配置演化 | 开关、能力与产品入口如何组合，代码能说明什么？ |
| 专题 | [状态、恢复与更新](02-Illustrated-Deep-Dive-Book/11-State-Recovery-And-Updates/README.md) | 网络失败、配置损坏、崩溃与升级分别怎样处理？ |
| 专题 | [版本与跨平台](02-Illustrated-Deep-Dive-Book/12-Versions-And-Cross-Platform/README.md) | 三个平台共享哪些字节，又保留哪些系统差异？ |

## 使用这份材料

下载 `books/claude-app/` 即可保留书、图和示例。原创代码用于解释机制和独立开发；产品源码定位、版本范围与核验记录集中在[证据附录](04-Extracted-Core-Code-And-Scripts/evidence/README.md)，不打断正文。

主样本：Claude Desktop 2.37337.1，覆盖 Linux、Windows、macOS 包；公开移动端与网页资料按各自来源日期记录。[来源索引](04-Extracted-Core-Code-And-Scripts/evidence/sources.md)
