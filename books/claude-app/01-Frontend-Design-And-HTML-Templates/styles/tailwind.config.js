/** 原创语义配置；Tailwind CSS 3.4 的 CommonJS 配置格式。
 * 文件名按用户的复用约定保留 claude；不表示官方实现或五套官方配色。
 * 此配置无插件依赖，先在应用根容器加载 claude-tokens.css。
 * 使用例：<main data-ui="atelier" data-palette="sage" data-theme="dark">。
 * 五套配色由 CSS 自定义属性驱动；切换 data-palette 不必重新生成工具类。
 * content 路径相对于本配置；移植到项目根目录时，请按实际源码位置修改。
 * 语义色为完整 CSS 颜色变量；不要假定 bg-accent/50 等透明度修饰直接兼容。
 * 2026-10-14 核验官方升级指南：v4 采用 CSS-first；JS 配置不再自动发现，
 * 必须用 @config "./tailwind.config.js" 显式加载；v4 dark 变体请单独配置。
 * 参考 https://tailwindcss.com/docs/upgrade-guide#using-a-javascript-config-file
 * 若工程 package.json 使用 type:module，请改名 .cjs 或改为 export default。
 * HTML 模板不依赖此配置、不加载 Tailwind CDN，也不需要构建。
 */
module.exports = {
  content: { relative: true, files: ["../templates/*.html", "../src/**/*.{html,js,ts,jsx,tsx}"] },
  darkMode: ["selector", '[data-theme="dark"]'],
  corePlugins: { preflight: false }, // 使用有作用域的独立 reset，避免全局污染。
  theme: { extend: {
    colors: {
      canvas: "var(--ui-canvas)", surface: "var(--ui-surface)", sidebar: "var(--ui-sidebar)",
      ink: "var(--ui-ink)", muted: "var(--ui-muted)", line: "var(--ui-line)",
      accent: "var(--ui-accent)", "accent-soft": "var(--ui-accent-soft)",
      action: "var(--ui-action)", "on-action": "var(--ui-on-action)",
      danger: "var(--ui-danger)", success: "var(--ui-success)"
    },
    fontFamily: { sans: ["var(--ui-font)"], serif: ["var(--ui-reading)"], mono: ["var(--ui-mono)"] },
    borderRadius: { control: "var(--ui-radius)", card: "var(--ui-card-radius)", composer: "var(--ui-composer-radius)" },
    boxShadow: { float: "var(--ui-shadow)" },
    minHeight: { control: "var(--ui-control)" },
    spacing: { gutter: "24px", section: "48px", editorial: "72px" }
  } },
  plugins: []
};
