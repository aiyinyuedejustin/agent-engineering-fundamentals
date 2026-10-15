# Tailwind v4：可选 CSS-first 语义桥接

这是既有原创 `--ui-*` 令牌的适配器，不是 Claude 官方主题，也不是 v3 配置的无损升级。默认六个 HTML 模板继续只用原 CSS，不需要 Tailwind；它们不依赖本适配器。

## 1. 选择正确入口

- Tailwind 3.4 项目继续用既有 `tailwind.config.js`。本次以 **3.4.19** 实际编译回归。
- Tailwind 4 项目采用 `styles/claude-tailwind-v4.css`，以 **4.3.3** 实际编译。不要把 `@config` 当成完整迁移：v4 不再自动发现 JS 配置，且不支持其中的 `corePlugins`，所以原来的 `preflight: false` 不能保护 v4 入口。[官方升级指南](https://tailwindcss.com/docs/upgrade-guide#using-a-javascript-config-file)

## 2. 安装与装配

2026-10-15 查询官方 npm registry，读到 `tailwindcss` 与 `@tailwindcss/cli` 的 `latest` 均为 4.3.3，再固定版本；3.4.19 来自同次查询的 `v3-lts`。这是复现版本，不是持续更新的“最新版本”承诺。

```sh
npm install --save-dev --save-exact --ignore-scripts tailwindcss@4.3.3 @tailwindcss/cli@4.3.3
```

把桥接文件与原 `claude-tokens.css`、`claude-reset-and-base.css` 放在项目同一 `styles/` 目录。以 `styles/example.entry.css` 为入口，把 `@source "../src"` 改为真实源码目录，然后：

```sh
npx @tailwindcss/cli -i ./styles/example.entry.css -o ./dist/app.css
```

入口只导入 `theme.css` 与 `utilities.css`，**不导入 `preflight.css`，也不使用总入口 `@import "tailwindcss"`**。原 reset 放进 `base` 层，使后面的工具类能覆盖它；不要另加一份未分层的 reset。[官方关闭 Preflight 方法](https://tailwindcss.com/docs/preflight#disabling-preflight)

## 3. 使用语义类

```html
<main data-ui="atelier" data-palette="sage" data-theme="dark"
      class="bg-canvas text-ink font-sans p-gutter">
  <button class="bg-action text-on-action rounded-control min-h-control">
    继续
  </button>
</main>
```

主题属性须同放在每个容器上。每层独立主题都用新的 `data-ui="atelier"` 根，并显式指定合法 palette 与 `light`/`dark`。裸 `data-theme` 不会生成本套令牌；不要把仅有 `data-theme="dark"`、缺 palette 的组合当成完整深色配置。

`@theme inline` 让 `.bg-canvas` 直接生成 `background-color: var(--ui-canvas)`，字体、圆角、阴影也在使用处读局部变量，嵌套容器才能各用自己的值。`bg-canvas text-ink` 通常已足够切换主题，无需再写一份 `dark:`。[官方变量引用说明](https://tailwindcss.com/docs/theme#referencing-other-variables)

桥接保留原配置的语义色、三类字体、三种圆角、浮层阴影、最小控件高度及三档间距；并补上已有令牌里的强边界、状态浅底与遮罩颜色。JSON 是令牌记录，不会被此 CSS 自动读取。不要据此推断 v3/v4 的透明度修饰、默认工具类或所有组合都等价。

## 4. 深色变体由项目另行配置

默认桥接**不改写 `dark:`**。Tailwind 默认的系统深色媒体查询与这里的 `data-theme` 不是同一个开关。官方数据属性示例按任意深色祖先匹配，内层 `light` 不会自动取消外层命中；原 v3 配置回归也呈现这种行为。[官方 dark-mode 说明](https://tailwindcss.com/docs/dark-mode#using-a-data-attribute)

因此，本适配器推荐普通语义类 `bg-canvas text-ink`，依靠最近的 atelier 根上的变量处理嵌套主题。若确需 `dark:` 切换布局或语义角色，由项目自行选择并验收策略。

本次曾试验 `@custom-variant dark` 内嵌 `@scope`，但真实 Chrome 中四个应命中的 dark 元素全部未命中。该增强已撤回，不能作为可用入口；失败源码与旧生成物仅归档在 `regressions/scoped-dark-negative/`，结果见 `verification/browser-results.json`。CLI 编译成功不等于浏览器匹配正确。

## 5. 验证与许可

`tests/verify.mjs` 在两个独立工具目录重建产物并检查 36 项断言；不安装依赖、不访问网络、只向新报告目录写入。重跑方法见验证说明。`verification/base.compiled.html` 为无脚本、无外部资源的默认桥接验收页；`v3.compiled.html` 用于原配置对照。

“无 Preflight”不等于“没有任何全局 CSS”：Tailwind 仍可能输出 `@property` 注册、`--tw-*` 初始化与常规全局工具类。需要混用其他工具类体系时，仍须评估命名冲突与项目隔离策略。

适配器与验收夹具为原创代码；生成样式含对应版本 Tailwind 的 MIT 授权代码。编译器 banner 已保留，原包 LICENSE 文本位于 `THIRD-PARTY-LICENSES/`。不分发 node_modules。
