# 六个可以直接打开的前端模板

用暖中性色、阅读节奏与清楚的动作层级，建立自己的产品界面。

每个 HTML 都内联了全部 CSS 和 JavaScript。直接双击即可使用；不需要安装依赖、启动服务器、连接模型或加载字体。顶部提供五套原创配色与浅深主题。

## 从需要的界面开始

| 模板 | 适合做什么 | 已实现的交互 |
|---|---|---|
| [01 组件图谱](01-component-gallery.html) | 组件库与设计起步页 | 按钮加载/禁用/焦点、输入校验、原生下拉框、开关、徽章、确认对话框、折叠说明、短提示、表格双向排序、代码高亮与复制 |
| [02 对话工作区](02-chat-workspace-template.html) | 聊天、助理与知识工作台 | 收起导航、移动端抽屉、示例对话、预设思路折叠、自适应输入、Enter 发送、停止并保留草稿、上下文标签、新对话、作品卡片 |
| [03 作品与代码工作区](03-split-artifact-ide-template.html) | 左侧讨论、右侧作品的编辑体验 | HTML/CSS 编辑、代码/预览切换、拖动或键盘调整分栏、更新预览、复制、标题替换指令、错误保留上一版、重置与恢复 |
| [04 编辑式博客与文档](04-editorial-blog-and-doc-template.html) | 设计手记、产品文档与阅读页 | 本地章节目录、博客/文档切换、全文段落搜索、搜索结果定位、专注阅读、回到开头 |
| [05 设置与概览](05-settings-and-dashboard-template.html) | 产品设置、个人工作区与仪表盘 | 周/月示例数据、活动筛选、主题预览、密度与阅读字号独立调节、活动显示开关、减少动画、资料校验、保存、恢复默认 |
| [06 浮动轻入口](06-floating-launcher-template.html) | 快速记录、命令面板与搜索入口 | 模糊文本匹配、方向键导航、命令执行、保存位置选择、输入提交、关闭后保留草稿、最近八条记录、移除记录 |

模板 02 的回复与“思路”是预先编写的本地内容。模板 05 的指标明确标为示例数据。模板 06 首次打开即显示命令面板，关闭后可查看记录区。

## 单页与整包复制

只需要某个页面时，单独复制该 HTML 即可，运行时不会读取相邻文件。连同说明与复用样式一起带走时，请保留 `templates/` 与 `styles/` 两个同级目录：本说明、六个 HTML、`QA-CHECKLIST.md` 和 `tests/` 放入 `templates/`，下面四份共享文件放入 `styles/`。本说明的 `../styles/` 链接按这个交付结构书写。研究章节链接是可选出处，不参与页面运行。

## 四份共享文件

单文件已经包含同一套基础变量，不会在运行时读取这些文件。需要拆分到工程里时，按顺序引入：

1. [claude-tokens.css](../styles/claude-tokens.css)：有作用域的语义变量，五套原创浅深配色、间距、圆角、字体、控件密度与阅读字号。
2. [claude-reset-and-base.css](../styles/claude-reset-and-base.css)：只作用于 `data-ui="atelier"` 容器及子树的基础重置。
3. [tailwind.config.js](../styles/tailwind.config.js)：可选的 Tailwind CSS 3.4 配置，映射相同 CSS 变量；独立 HTML 不依赖 Tailwind。
4. [design-tokens.json](../styles/design-tokens.json)：机器可读的原创角色映射与尺寸档，便于转换到其他工具。

```html
<main data-ui="atelier"
      data-palette="sage"
      data-theme="light"
      data-density="comfortable"
      data-reading="default">
  <!-- 你的内容 -->
</main>
```

`data-palette` 支持 `paper` 纸与陶、`sage` 苔绿、`ocean` 雾蓝、`plum` 梅灰和 `graphite` 石墨。配色决定表面与强调色，`--ui-action` 仍独立承担主要动作。密度使用 `compact` / `comfortable`，阅读使用 `default` / `large`，两个尺度互不绑定。

Tailwind v4 已转向 CSS-first，JavaScript 配置不会自动发现，需要用 `@config` 显式加载；暗色变体应按 v4 配置方式设置。这里提供的是标注版本的 v3.4 起点，迁移前请对照[官方升级指南](https://tailwindcss.com/docs/upgrade-guide#using-a-javascript-config-file)。配置的 content 路径相对于配置文件，复制到自己的工程后需调整。

## 快捷键与数据

- 通用：Tab / Shift + Tab 遍历控件；原生对话框使用 Esc 关闭并恢复触发按钮焦点。
- 对话：Enter 发送，Shift + Enter 换行；Ctrl / ⌘ + K 新建本地对话。
- 作品：Ctrl / ⌘ + Enter 更新预览；分隔条聚焦后左右键调整，Home / End 到达边界。
- 轻入口：Ctrl / ⌘ + K 打开或收起；上下键选择，Enter 执行；关闭保留尚未提交的文字。
- 输入法：组合输入期间不会把候选词确认当成发送；实际操作仍需在目标输入法验收。
- 本地存储：主题、配色、聊天草稿、设置、轻入口记录使用各自的 `atelier-` 键。浏览器禁用存储时，页面继续工作并在需要时说明无法持久保存。不要用示例存储敏感数据。
- 复制：优先使用浏览器剪贴板；不可用时尝试旧式本地复制，仍失败则提示手动选择复制。

## 作品预览的边界

模板 03 只预览静态 HTML/CSS。编辑内容先在惰性模板中解析，仅保留静态元素与有限属性，再进入 `sandbox=""` iframe。预览 CSP 禁止脚本、网络、图片、字体、嵌入、表单与基址；没有同源权限，也没有通向父页面的消息桥。外链和导航元素、事件属性、脚本、表单、SVG 与 iframe 都被移除。

这适合布局练习。若要运行第三方脚本或连接真实服务，请另外设计独立源、权限与通信协议，不要直接放宽这里的 sandbox。错误时保留最后一份成功预览，修复后再次更新。

## 设计来源与原创范围

模板借鉴[视觉设计章节](../README.md)中有出处的关系：暖中性表面、工具字与阅读字分工、内容宽度、输入面层级、低噪声状态反馈。六个页面、五套配色、布局、图形、文字与交互代码均为原创适配；没有官方标志、专有字体或应用代码，也不表示某个版本的逐像素复刻。完整静态颜色记录由本书的颜色目录单独提供，不与这里的原创语义令牌混为一套。

## 检查与截图

[交互检查与截图清单](QA-CHECKLIST.md)给出每页的入口、桌面/窄屏规格，以及实际浏览器需要确认的事项。[tests/results.json](tests/results.json)记录静态与模拟 DOM 检查，不能替代真实布局、CSP 执行、中文输入法和辅助技术测试。


## 浏览器实景

以下为本书原创模板在 Chrome 中的实际渲染，视口 1188 × 761，版本 d63d0f4。通过公开 HTTPS 预览页面加载；离线 file:// 是另一项验证条件。

### 组件画廊

![组件画廊](../../assets/screenshots/01-gallery-light-d63d0f4.jpg)

### 对话工作台

![对话工作台](../../assets/screenshots/02-chat-d63d0f4.jpg)

### 分屏代码与预览

![分屏代码与预览](../../assets/screenshots/03-ide-d63d0f4.jpg)

### 技术博客

![技术博客](../../assets/screenshots/04-editorial-d63d0f4.jpg)

### 设置与看板

![设置与看板](../../assets/screenshots/05-settings-d63d0f4.jpg)

### Quick Entry

![Quick Entry](../../assets/screenshots/06-launcher-d63d0f4.jpg)
