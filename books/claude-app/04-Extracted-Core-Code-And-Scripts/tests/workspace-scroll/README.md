# 工作区滚动边界回归

这些检查只针对原创 `interactive-study`，不测试 Claude 产品。

## 运行

在本书根目录先安装现有测试依赖，再运行：

```sh
npm ci --prefix 04-Extracted-Core-Code-And-Scripts/tests/demo-state --ignore-scripts --no-audit --no-fund
node 04-Extracted-Core-Code-And-Scripts/tests/workspace-scroll/run.cjs
```

复用 `demo-state` 的固定版本 jsdom 26.1.0 与既有模拟环境，不新增依赖。报告写入 `04-Extracted-Core-Code-And-Scripts/tests/results/workspace-scroll.json`；失败或运行期间源文件变化均返回非零状态。

## 问题与最小修复

真实浏览器在 1188 × 761 px 视口观察到：初始对话的文档 `scrollHeight` 为 761；进入「组件图谱」后为 774，选择「舒适」后约 824，再选择「大 18」后约 831。后续聚焦速记控件时，页面外层曾向下滚动 34 px，工具栏和左侧标记的顶部被裁去。

可见卡片已经位于 `.document-view { overflow: auto }` 内。但 `#display-preference-status` 是绝对定位的屏幕阅读器状态节点，原先没有位于该滚动边界内的定位祖先，其静态位置延伸到视口以下。仅有 `overflow: auto` 不足以约束包含块位于外侧的绝对定位后代。

修复只给 `.document-view` 增加 `position: relative`，让状态节点的包含块进入视图自己的滚动边界。不删除状态节点，不改变其 `role="status"`、文字更新或通用隐藏方式；不新增根节点溢出裁切，也不使用 JavaScript 重置页面滚动或阻止键盘默认行为。

普通高度的 `100dvh` 外框、`.workspace` 的 `min-height: 0` 与各面板滚动保留。高度不超过 560 px 时，仍切换到文档滚动，使短屏或高倍缩放下的控件可达。导航抽屉、注释面板、Quick Entry 草稿与焦点流程不变。

## 六项自动检查

1. 状态节点在其视图内部拥有明确的定位祖先
2. 对话、文档、导航、注释面板的滚动声明与外框尺寸保留
3. 短视口文档滚动的媒体查询分支保留
4. 六种密度与字号组合仍更新可访问的状态节点
5. 不吞掉画廊控件的 Tab / PageUp / PageDown 事件，速记收起与重开仍保留草稿和焦点流程
6. 320 px 媒体查询模拟中，定位边界及现有抽屉/速记逻辑仍成立

jsdom 不执行真实布局。检查 1、2、3、6 是 DOM/CSS 声明防回退措施；检查 5 的事件结果不证明浏览器默认滚动或真实 Tab 导航成功。320 px 模拟也不是移动端视觉测试。屏幕阅读器状态语义与内容更新通过，不代表实际辅助技术播报已测。

## 真实浏览器复验路径

在高于 560 px 的视口进行，优先重复 1188 × 761 px；记录实际浏览器版本与代码提交：

1. 刷新，测量 `innerHeight`、`document.scrollingElement.scrollHeight`、`scrollY` 及工具栏顶边。
2. 进入「组件图谱」，依次选择「舒适」「大 18」；每步再次测量。外层高度应等于视口高度、`scrollY` 保持 0。
3. 用原生 Tab 经过试样按钮、输入、返回对话按钮和速记入口。打开速记，输入草稿，Esc 收起后重新打开；内部面板仍应滚动到焦点，工具栏保持可见，草稿保留。
4. 用原生 PageDown / PageUp 或滚轮滚动画廊，确认内部内容可以到达末尾；切换对话和语义变量，再检查面板与外框。
5. 另测 320 / 390 / 768 px 宽度，以及高度不超过 560 px 的短视口和缩放场景。短视口允许且需要外层文档滚动，不应使用「外层始终为零」作为断言。

真实浏览器复验结果需单独记录，不得把本脚本通过称为布局、移动端、原生键盘或完整无障碍验证通过。
