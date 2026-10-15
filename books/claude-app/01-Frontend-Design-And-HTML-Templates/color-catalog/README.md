# 全量色表：先找色，再读主题

打开 [离线色表浏览器](index.html)，即可按色族、用途和主题筛选，查看色块并复制 HEX + alpha。文件内置全部数据，不需服务器或网络。

## 这份色表有多少颜色

- **315 个原始色阶**：gray、red、orange、yellow、green、aqua、blue、violet、magenta，每族 35 档。原始声明和值全部保留。
- **1026 条主题 / 桥接记录**：覆盖表面、文字、边界、填充、强调、状态、图表、协作、Git 和组件用色，同名项按上下文分开。
- **3234 个声明定位**：机器目录保留 843 个相关名称的全部选择器和来源；浏览页只展开所选项的来源。

| 来源配置 | 记录 | 可显示色值 | 表达式 |
|---|---:|---:|---:|
| CDS · 全量原始色阶 | 315 | 315 | 0 |
| CDS · 显式浅色 | 349 | 337 | 12 |
| CDS · 显式深色 | 349 | 338 | 11 |
| Legacy v1 · 浅色 | 50 | 50 | 0 |
| Legacy v1 · 深色 | 50 | 50 | 0 |
| Legacy v2 · 浅色 | 50 | 50 | 0 |
| Legacy v2 · 深色 | 50 | 50 | 0 |
| Legacy v2 · HSL 桥接 | 128 | 128 | 0 |

## 三层读法

1. **原始色阶**回答“有哪些颜色”：`--cds-blue-600` 是固定档位，主题切换不改变这一原始值。
2. **CDS 语义色**回答“放在哪里”：`--cds-text-primary`、`--cds-surface-0` 和 `--cds-border` 会映射到对应主题下的色阶或透明色。
3. **Legacy v1 / v2**用于读懂旧命名：v1 直接使用 HSL 分量；v2 用 `--_` 和 `--cds-hsl-*` 连接新版值。两套不能按同名直接互换。v2 表包含未被桥接覆盖的 v1 项。

“显式浅色”采用 CDS 基础声明；“显式深色”叠加 screen 条件下 data-mode=dark 覆盖。每个配置是命名的静态声明组合，不等于某张产品截图的最终 computed style。系统深色、局部 dark-scope、组件 / 工具类覆盖与特性查询保留在机器目录，不混入主表。

## 先看这九个语义色

| 名称 | CDS 浅色 | CDS 深色 |
|---|---|---|
| `--cds-surface-0` | #f9f9f7 | #0b0b0b |
| `--cds-surface-panel` | #ffffff | #1a1a19 |
| `--cds-text-primary` | #0b0b0b | #f0efec |
| `--cds-text-secondary` | #52514e | #c3c2b7 |
| `--cds-text-muted` | #898781 | #898781 |
| `--cds-clay` | #d97757 | #d97757 |
| `--cds-fill-brand` | #c6613f | #c6613f |
| `--cds-border` | #0b0b0b · α=0.1 | #ffffff · α=0.1 |
| `--cds-bg-user-message` | #0b0b0b · α=0.05 | #ffffff · α=0.05 |

## 透明度怎么用

`#ffffff80` 的 alpha 是 128/255（约 50.1961%），不是精确 50%。`#0006` 的 alpha 是 40%。色块用棋盘格展示未合成的透明色，复制按钮同时保留 HEX 与 alpha；需要落在实际表面上时再进行合成。HEX 是 8-bit 显示值；原始 HSL 分量和表达式可在详情中查看。

## 表达式区

23 条配置记录保留为表达式，包括需要元素 currentColor、CSS 级联关键字或尚未求值的相对 RGB calc。它们没有人为补出的 HEX 或透明度。搜索 token 后可直接查看原始声明和来源配置。

## 可复用入口

- `color-catalog/index.html`：单文件、离线、原创交互色表。
- `color-catalog.json`：紧凑色值导出；按 `columns` 解读每条记录，包含配置、变量名、声明、HEX、alpha 与解析状态。适合自动生成自己的设计变量。
- `build_color_catalog.py`：重新生成目录和页面；输入来自已解析的包内 CSS。

本目录基于 Claude Desktop Linux 2.37337.1 包内静态颜色事实；交互页面与组织方式为原创实现。

## 相对色与上下文值

[原创浏览器核验页](relative-color-fixture.html)用隔离的19个静态派生表达式和5个上下文例子检查相对RGB、initial回退与currentColor。它保留超范围sRGB通道，不把裁剪HEX冒充原值；只检查浏览器CSS语义，不加载产品样式文件或执行产品脚本。页面会直接显示各项计算结果与通过/失败。
