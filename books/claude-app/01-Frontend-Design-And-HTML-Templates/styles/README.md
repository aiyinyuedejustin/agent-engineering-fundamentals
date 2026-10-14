# 原创语义组件

这组文件服务于 `../demo/` 中的独立界面研究。它们不是官方 Claude 组件，不依赖任何提取的产品源码。

## 加载顺序

```html
<link rel="stylesheet" href="components/tokens.css">
<link rel="stylesheet" href="components/components.css">
```

在根元素上设置 `data-theme="light"` 或 `data-theme="dark"`。主题切换只改变语义变量；组件不需要知道具体颜色。

## 三层契约

1. `tokens.css` 决定颜色、字体、尺寸、形状与动效等变量。
2. `components.css` 实现按钮、字段、提示、卡片、分段控件、开关与模态窗口的基础外观。
3. 业务页面负责布局、内容、状态转换、焦点管理与错误恢复。

变量名称是本研究原创。部分色彩字面值来自静态声明观察；它们的具体语义分配以及新增值都属于研究实现，而不是官方默认样式。来源与限制见 `../demo/README.md`。

## 示例

### 按钮

```html
<button class="study-button study-button--primary">主要操作</button>
<button class="study-button">次要操作</button>
<button class="study-button study-button--quiet">轻量操作</button>
<button class="study-button" disabled>暂不可用</button>
```

只在动作确实不可执行时使用 `disabled`。按钮文字说明动作；只有图标时提供可理解的 `aria-label`。

### 输入与错误

```html
<label class="study-label" for="title">笔记名称</label>
<input class="study-field" id="title" aria-describedby="title-help">
<p class="study-helper" id="title-help">输入至少两个字符。</p>
```

错误时设置 `aria-invalid="true"`，将帮助文字替换为具体恢复指引，并使用 `study-helper--error`。不要只改变颜色，也不要自动清空输入。

### 开关

```html
<label class="study-switch-row" for="show-guides">
  <span>显示辅助线</span>
  <input class="study-switch" id="show-guides" type="checkbox">
</label>
```

这是原生复选框，保留键盘与表单语义。实际功能由调用方实现。

### 模态窗口

```html
<dialog class="study-dialog" aria-labelledby="dialog-title">
  <h2 id="dialog-title">确认标题</h2>
  <p>解释当前操作及其后果。</p>
  <div class="study-dialog-footer">
    <button class="study-button">取消</button>
    <button class="study-button study-button--primary">继续</button>
  </div>
</dialog>
```

使用原生 `showModal()`，不要只加 CSS 显示。调用方应实现按钮操作、焦点恢复与必要的状态处理；可参考 demo 的 `openDialog` 与 `close` 监听。

## 第二阶段：局部密度、消息字号与 Quick Entry

### 局部密度

在试样容器使用 `.study-density-example`，再设置 `data-density="compact"` 或 `data-density="comfortable"`。前者是默认值，后者局部重映射 control-height、label-size、radius、icon、padding 和 gap。实际消费由相应 `.study-density-*` 子类以及容器内的 `.study-button` / `.study-field` 完成。

```html
<div class="study-density-example" data-density="comfortable">
  <div class="study-density-toolbar">
    <span class="study-density-caption">操作文字</span>
    <button class="study-button" type="button">检查层级</button>
  </div>
  <p class="study-message-text">这段阅读文字有独立大小。</p>
</div>
```

原创紧凑 / 舒适参数依次为：控件 40 / 48 px、图标 16 / 20 px、内边距 12 / 20 px、间距 8 / 12 px、圆角 8 / 12 px、操作文字 13 / 14 px。密度变化只作用于这个容器，不承诺整个组件库全部响应。

### 消息阅读轴

根元素或局部祖先设置 `data-message-size="sm"`、`"md"`、`"lg"`，只定义 `--study-message-size` 的 14 / 16 / 18 px。`.study-message-text` 消费它和独立的行高变量；demo 中的消息规则也消费它。不要把该变量赋给整个 body 或工具按钮。可复用容器若含内部按钮，应像 demo 的消息操作、内容预览卡那样明确恢复工具字体。

`.study-choice-field` 只负责这组选择控件的外观；调用方必须实现可见标签、唯一 aria-pressed 选项、状态更新和有效值约束。它不是原生 radio，也不添加未实现的箭头键约定。

### 水平短输入

`.study-quick-entry` 是单独的横向容器，包含 `.study-quick-context` select、textarea 与 `.study-button`；不要套在主 Composer 上，也不要把该例的 48 px / 12 px 几何当作产品的 56 px / 16 px 证据值。示例的输入目标是页面内存，调用方需明确其去向和生命周期。

完整 HTML 在 `demo/index.html` 的 `#quick-entry-example`，行为在 `demo/demo.js` 的 `captureQuickEntry`、`setQuickEntryOpen` 与 `resetQuickEntry`。CSS 不提供提交、验证、IME 保护或焦点恢复，复用时需一并实现这些职责。原始输入只能进入 textContent 等文字接口，不拼进 HTML。

这三项都是研究中的独立适配；模拟测试只证明声明与事件路径，真实浏览器布局、原生输入法和辅助技术仍需验证。详见 `../tests/phase2-components/README.md`。

## 实用约束

- 类名与变量仅部分采用 study 前缀；reset 和演示布局有全局选择器，嵌入现有应用前需要收束作用域。
- CSS 不加载字体文件。设备实际字体与换行可能不同。
- 分隔线用于装饰；表单边界使用更强的 `--study-field-border`。
- 暖色强调不是默认主操作颜色。普通动作与状态色分离。
- 40 px 为研究中多数控件的最小高度；新密度试样的舒适分支局部使用 48 px。小型工具栏有单独布局，不是通用尺寸承诺。
- 主题选择器依赖 CSS 自定义属性的继承。若在局部容器切换主题，需要在该容器上设置 `data-theme`。
- 焦点、交互、表单提交与屏幕阅读器语义不能仅靠 CSS 自动完成。
- 色彩配对与可访问性需要在实际应用场景、字体大小和状态下重新验证。
