# 已撤回的 scoped-dark 实验

这里保留失败证据，不是可复用适配器。不要导入、恢复或把旧静态结果称为浏览器通过。

真实 cloud Chrome 在 886d74e 版本的夹具上有四项未命中：dark-root、dark-child、nested-dark-root、nested-dark-child 的危险底色均未应用。具体预期、实测与来源见`../../verification/browser-results.json`。普通语义变量的默认夹具核心 computed style 正确。

云 Chrome 的 CSSOM 还读到 `@scope (& [data-ui=atelier][data-theme=dark])`，确认根相对外层工具类解析。CSSOM 已解析作用域，不能凭工具返回的 `typeof CSSScopeRule` 判断浏览器不支持。

原 CSS 被编译为 `.dark\:bg-danger { @scope (...) to (...) { background-color: var(--ui-danger); } }`。CSS Cascade 6 的作用域嵌套与 scoped declarations 语义并不保留预想的工具类匹配：起始选择器受嵌套上下文影响；直接声明匹配作用域根、特异性为零；scope 内的 `&` 指向 `:where(:scope)`。因此简单补 `&` 也不是已验证修复。

原始源码、编译物和历史静态结果均保留为文本。历史 40 项通过仅代表当时 CLI/结构断言通过，不能覆盖这四项浏览器失败。最终交付撤掉可导入增强，仅保留默认桥接和 v3 回归。

规范：
- https://drafts.csswg.org/css-cascade-6/#scope-nesting
- https://drafts.csswg.org/css-cascade-6/#scoped-declarations

上游也记录了相同类型的生成结构问题：[issue #18961](https://github.com/tailwindlabs/tailwindcss/issues/18961)、[PR #20369](https://github.com/tailwindlabs/tailwindcss/pull/20369)。PR 描述了把 scope 放到工具类外层的修复方向，但本交付固定的 4.3.3 实际输出仍为已归档结构；不能因上游 PR 已合并就推断这个已安装包已经修好。没有引入私有 hoist 指令或尝试无限版本矩阵。
