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

## 实用约束

- 类名与变量仅部分采用 study 前缀；reset 和演示布局有全局选择器，嵌入现有应用前需要收束作用域。
- CSS 不加载字体文件。设备实际字体与换行可能不同。
- 分隔线用于装饰；表单边界使用更强的 `--study-field-border`。
- 暖色强调不是默认主操作颜色。普通动作与状态色分离。
- 40 px 为研究中多数控件的设计高度；小型工具栏有单独布局，不是通用尺寸承诺。
- 主题选择器依赖 CSS 自定义属性的继承。若在局部容器切换主题，需要在该容器上设置 `data-theme`。
- 焦点、交互、表单提交与屏幕阅读器语义不能仅靠 CSS 自动完成。
- 色彩配对与可访问性需要在实际应用场景、字体大小和状态下重新验证。
