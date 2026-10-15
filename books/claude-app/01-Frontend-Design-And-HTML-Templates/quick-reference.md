# Claude 视觉设计速查

六个具体发现与一个起步配方

[返回视觉设计章节](README.md) · [打开原创 demo](interactive-study/index.html) · [查选定数据](../04-Extracted-Core-Code-And-Scripts/evidence/data/design-token-summary.json)

![CDS 浅深表面层级原创色样](../assets/figures/surface-mappings.svg)

*选定 CDS 静态值，原创建图；下列参数和 demo 的自主选择分开记录。*

## 1 浅深主题的成对起点

| 角色 | 浅色 | 深色 |
|---|---|---|
| surface 0 / 1 | `#f9f9f7` / `#fcfcfb` | `#0b0b0b` / `#151515` |
| surface 2 / 3 | `#ffffff` / `#ffffff` | `#1a1a19` / `#20201f` |
| primary / secondary 文字 | `#0b0b0b` / `#52514e` | `#f0efec` / `#c3c2b7` |
| ghost hover / selected | 深色 `#0b0b0b`，alpha 5% / 10% | 白色，alpha 7.5% / 15% |

浅色的高层表面可以同色，靠轮廓、阴影和位置继续区分；深色表面逐层变亮。透明值随承托背景改变，复用时保留 alpha。[完整色板](README.md#01-色板与主题)

## 2 Clay、Accent 与 Primary 分开

- Clay `#d97757`；强调品牌填充 `#c6613f`
- Accent 填充 `#2a78d6`；accent 文字浅色 `#184f95`，深色 `#6da7ec`
- Primary 填充 / 文字：浅色近黑 / 白，深色白 / 近黑

官方样本里，聊天发送是暖橙，设置 Save 是黑底白字，活跃语音 Stop 是浅蓝底蓝字。保留各动作的用途，再决定自己的色彩映射。白字搭配 `#c6613f` 的假设对比度约 4.05:1，不能默认适合所有小字。[色彩分工](README.md#primaryclay-与-accent-的分工)

## 3 输入面分两层，Quick Entry 共一轴

完整 composer：编辑区域在上，附加动作与模型 / 提交分列下方。包内部件包括 Header、Attachments、Actions、PrimaryAction、Chin、Overlay、Tray，外部另有 Dock；可选部件不必同时可见。

Quick Entry：输入、会话上下文、提交同轴；所检独立窗口声明为最小输入行 56px、圆角 16px、文字 16px / 150%。这些数值不属于主 composer。[结构解剖](README.md#composer-的七个部件与一个-dock)

## 4 阅读大小与操作密度独立

| CDS 参数 | 默认 | comfortable |
|---|---:|---:|
| body 字号 / 行高 | 13 / 19px | 14 / 20px |
| prose 字号 / 行高 | 14 / 20px | 16 / 24px |
| 控件 / 图标 | 24 / 16px | 32 / 20px |
| 普通 / composer 圆角 | 6 / 12px | 8 / 14px |

换算前提：根字号 16px、rem-scale=1。prose 为普通 rem，许多工具值还乘 scale。消息 sm / md / lg 可以改正文，而内部按钮恢复自身字号。demo 提供原创 40 / 48px 密度与独立 14 / 16 / 18px 阅读字号；它没有复刻包内 24 / 32px 参数。[字体与密度](README.md#03-字体与密度)

中文也有独立判断：所检 Sans / Serif / Mono 文件没有 CJK 统一表意字形；中文依赖回退。demo 的系统衬线阅读是原创适配，不能当作 Claude 中文默认字体。

## 5 消息、阅读与作品入口采用不同容器

用户消息及指定助手气泡分支的最大 measure 为 85%；所有助手回复不必共享气泡。Card 则分外框、fill、body、media 与 link，承担可识别的对象入口；Artifact 工作区还有自己的标题与切换。

迁移时分别决定：哪里需要一块底色，哪里靠间距保持阅读，哪里必须让人看出可以打开。demo 的作品入口仅打开模态预览，没有完整 Artifact 分屏。[色块剖面](README.md#02-色块与边界)

## 6 精细反馈藏在条件规则里

- Card：常态 surface-1，含链接的 hover 为 surface-2；按压联动填充缩放与内容裁切，按下 fast、释放 slow / 弹簧
- MessageActions：粗指针或无 hover 时常显，取消显隐过渡
- Hairline：2x / 3x / 4x 分辨率对应 0.5px / 1⁄3px / 1⁄4px
- Composer Chin：触摸分支补偿视觉行外的触达；实际命中面积仍需实测

这些机制已进入研究图谱，多数尚未进入 demo。复用入口与缺口见[覆盖矩阵](README.md#机制与-demo-覆盖矩阵)。

## 一个最小起步配方

1. 打开 [demo](interactive-study/index.html)，进入“语义变量”，切换浅深；看画布、内容面、文字与表单边界怎样一起变。
2. 修改 [tokens.css](styles/tokens.css) 的 surface / ink、action / on-action、error / error-soft 三组，使用自己的品牌与字体。
3. 进入“组件图谱”，触发输入错误并打开 dialog；再在“状态”里发送、停止、模拟失败、重试，观察草稿与按钮名称。
4. 嵌入自己的页面前收束 CSS 作用域。[components.css](styles/components.css) 仍含 body、button、p、focus 等全局规则，前缀不提供完整隔离。

研究基准：2026-10-14；主要样本 Claude Desktop Linux 2.37337.1。数据是静态观察，图与 demo 是原创；未登录运行 Claude。这里的交互工作台有 46 项基础、32 项新增模拟 DOM 检查，以及 6 项基础、10 项新增静态检查；不包含六套独立 HTML 模板的测试。[初版浏览器记录](../04-Extracted-Core-Code-And-Scripts/evidence/data/demo-browser-baseline.json)仅覆盖提交 520db1b 的指定场景；2026-10-15 已在 Chrome、1188 × 761 CSS 像素视口检查新增密度、阅读与 Quick Entry；提交 3166d2d 的六种组合、内部键盘滚动和相关草稿／焦点路径已复验通过。窄屏、短视口、缩放、真实中文 IME、跨平台字体与辅助技术等仍未验收。[证据图例](README.md#证据图例) · [基础测试报告](../04-Extracted-Core-Code-And-Scripts/evidence/data/demo-state-test.md) · [新增测试范围](../04-Extracted-Core-Code-And-Scripts/tests/phase2-components/README.md)
