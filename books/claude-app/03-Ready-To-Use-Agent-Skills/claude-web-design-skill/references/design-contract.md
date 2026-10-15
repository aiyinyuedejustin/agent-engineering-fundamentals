# 参数合同：观察事实与原创实现

研究范围：Claude Desktop Linux 2.37337.1，2026-10-14。以下来自官方分发包的静态声明，不证明相应分支已在某个账户启用，也不是官方公开的通用设计规范。CDS 颜色/密度/时长的选定声明、SHA-256、短定位与字体元数据随本文件放在 observed-tokens.json。另附 [color-catalog.json](color-catalog.json)：本书已发布选定 profile 的完整 1341 条颜色记录及 resolution_extension，逐字节随包复制；旧 HSL v1/v2 颜色可在对应 profile 查找。它不是所有运行时 CSS，不包含原始 CSS 或字体文件。精选事实、完整选定色表与原创 tokens 的区别及取值流程见 [色表取值指南](color-catalog-guide.md)。桌面框架尺寸仍是原研究的上下文摘要，不能声称已由包内色表逐项复核；需要完整声明定位时另查原研究证据。原创 HTML/CSS 的运行不依赖书外文件。

## 观察到的颜色

| 范围 / 角色 | 浅色 | 深色 |
|---|---|---|
| 旧 HSL v1 bg-100 | #faf9f5 | #262624 |
| 条件映射 v2 bg-100 | #f9f9f7 | #151515 |
| CDS surface-0 | #f9f9f7 | #0b0b0b |
| CDS surface-1 | #fcfcfb | #151515 |
| CDS surface-2 | #ffffff | #1a1a19 |
| CDS surface-3 | #ffffff | #20201f |
| CDS text-primary | #0b0b0b | #f0efec |
| CDS text-secondary | #52514e | #c3c2b7 |
| CDS text-muted | #898781 | #898781 |
| CDS text-accent | #184f95 | #6da7ec |
| CDS clay / emphasized clay | #d97757 / #c6613f | 同左 |
| CDS ghost-hover | #0b0b0b，5% | #ffffff，7.5% |
| CDS ghost-selected | #0b0b0b，10% | #ffffff，15% |

透明值必须与实际底色合成。白字与 #c6613f 约 4.05:1；#898781 与 #f9f9f7 约 3.41:1。这些是假设配对，不是对真实 UI 元素的违规判定。小字选择应验证实际 4.5:1 阈值，不能四舍五入把失败算成通过。

## 观察到的尺寸

在根字号 16px、rem-scale=1、无后续覆盖时：

| CDS 角色 | 基础密度 | comfortable |
|---|---:|---:|
| control 高 / nested 高 | 24 / 18px | 32 / 22px |
| icon | 16px | 20px |
| radius / composer / panel | 6 / 12 / 10px | 8 / 14 / 12px |
| pad xs / sm / md / lg / xl | 4 / 6 / 8 / 12 / 20px | 6 / 8 / 12 / 16 / 24px |
| gap xs / sm / md / lg / xl | 6 / 8 / 12 / 20 / 32px | 8 / 12 / 16 / 28 / 40px |
| body 字号 / 行高 | 13 / 19px | 14 / 20px |
| prose 字号 / 行高 | 14 / 20px | 16 / 24px |
| title 字号 / 行高 | 20 / 25px | 22 / 28px |

桌面框架另有默认 sidebar 288px、header 48px、row 26px、row font 13px、icon 16px、card radius 8px。平台、density、variant 和内联值可覆盖。用户气泡分支最大 measure 85%，不代表所有助手回复都应被画成气泡。

CDS 时长 fast/snap/base/sheet/slow 为 60/120/200/300/450ms。观察这些值不等于需要把所有组件都加动画。原包针对 touch、focus 与 reduced motion 有分支；本骨架只保留轻量状态反馈。

## 字体覆盖与替代

包内可见 anthropic-sans、anthropic-serif、anthropic-mono，选定正常字体声明的 weight 范围为 300–800。历史 Styrene/Tiempos、生成品牌材料指南中的 Poppins/Lora 与当前应用字体不是同一个证据范围。

所检 Sans/Serif/Mono 字体样本不覆盖中日韩统一表意文字，不能推导整个应用不支持中文。Latin 使用衬线体时，中文可能仍回退为无衬线；CSS 字体栈也不单独证明最终使用了哪张字体。

原创骨架：

- 操作：system-ui → PingFang SC → Microsoft YaHei → Noto Sans CJK SC → sans-serif。
- 中文正文：同操作栈，16px / 1.75；优先可靠回退。若项目需要中文衬线，另选合法可用的 CJK serif 并重新验小字号。
- 英文长文：Georgia → Cambria → Times New Roman → serif，仅对 lang=en 生效。
- 代码：ui-monospace → SFMono-Regular → Consolas → Liberation Mono → monospace。

不随技能分发或下载任何专有字体，也不声明操作系统一定预装某个具体字体。

## 原创 token 决定

assets/tokens.css 的命名、排列与代码为原创。它借用部分已观察到的中性表面值，但主动选择深色 primary action、较强边界与辅助文字，并采用 44px 最小按钮触达、320px 起的窄屏重排、最大 48rem 阅读区、16px 中文正文、12px composer radius、8/12/16/24/32px 间距。这些是该教学起点的设计选择，不是 Anthropic 参数。

以语义变量改造已有产品：canvas 对页面；surface 对输入容器；raised 对预览；text 对主文；muted 对仍须可读的辅助信息；line 对装饰分隔；control-border 对必须辨认的边界；focus 对键盘焦点。一个角色不要同时承担选择、错误与品牌。

需要紧凑设置或模态窗口时，按 [原创交互契约](interaction-contracts.md) 区分正文、控件和命中区域；其中的密度与交互配方不改变上面的静态证据口径。

## 复核入口

- [设计工作室的 Anthropic 品牌案例](https://geist.co/work/anthropic)
- [官方生成材料品牌指南](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md)，不作为应用字体证据
- [W3C 文字对比度解释](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- 本地 observed-tokens.json：版本冻结的静态证据；不要自动当成未来版本的当前值
