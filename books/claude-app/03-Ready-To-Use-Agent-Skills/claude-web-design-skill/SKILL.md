---
name: claude-web-design-skill
description: Build or refine calm, reading-first chat and knowledge interfaces inspired by observed Claude design patterns, with semantic tokens, original accessible styling, CJK typography, and responsive HTML/CSS. Use for frontend implementation or design review, not for claiming an exact current Claude clone.
---

# 阅读优先的对话界面

## When to use

用于用户要求 Claude 气质的聊天、知识工作台、长文阅读与作品分屏界面，或需要消除模板化「AI 味」的同类产品。先保留用户已有品牌、技术栈和信息架构；不要把普通营销页强制改成聊天应用。

## Workflow

1. 明确当前主要活动：阅读、输入、导航、检查作品。先以灰度建立四者的层级，再上色。确认目标语言、窄屏行为、主题与实际内容长度。
2. 阅读 [参数与来源边界](references/design-contract.md)。表内参数属于指定版本和选择器；不要把旧 HSL、v2、CDS 和桌面框架混成一个「官方统一值」。常用精选事实见 [静态令牌记录](references/observed-tokens.json)；本书已发布选定 profile 的完整 1341 条色表及推导扩展随包保存在 [color-catalog.json](references/color-catalog.json)，按 [色表取值指南](references/color-catalog-guide.md) 使用。完整仅指该选定范围，不是所有运行时 CSS。
3. 用 [原创 tokens.css](assets/tokens.css) 与 [skeleton.html](assets/skeleton.html) 起步；二者可一同复制到项目。本地字体、无外部依赖，不需要本书其他文件。这是整页骨架：tokens.css 在 :root 定义变量，并含 body、button、:focus-visible 等全局规则，不提供局部组件隔离。若接入现有页面或组件库，先映射语义令牌并收束选择器作用域，不要整份覆盖全局 CSS。
4. 先落实阅读宽度、正文/操作字体、composer 状态与 focus-visible，再做装饰。中文正文单独决定黑体或宋体；不要以 Latin serif 名称推断中文字形。需要模态窗口或紧凑设置时，再读 [交互与密度契约](references/interaction-contracts.md) 和 [原创可运行小例](assets/interaction-recipes.html)。
5. 实现空态、长内容、附件处理中、失败可重试、生成中、取消后等真实状态。只实现当前产品确实存在的状态，不为清单虚构模型、附件或网络流程。骨架只示范布局与本地交互，接模型前清楚区分本地提交和实际完成。
6. 在 375、768、1280px、200% 缩放、两种主题下检查长中文标题、长路径、代码块、键盘和触屏。对比度检查实际前景/背景组合，不仅检查色板。运行 `node --test assets/*.test.mjs`；它们只检查包内颜色、结构与模拟 DOM 逻辑，不能代替浏览器视觉与辅助技术测试。修改或内嵌到新页面后，对最终产物重做同类检查。
7. 交付可运行页面、令牌选择说明和真实测试结果。指出哪些数值是观察事实，哪些是为该产品作出的原创决定。

## Ten Anti-Slop Rules

1. 不用渐变光晕、磨砂玻璃和发光描边替代层级。默认平面暖中性色，只有真实浮层获得阴影。
2. 不把每段回复包成同权重卡片。连续回答保留阅读流，文件、工具结果与用户消息按职责形成容器。
3. 不把陶土色涂满所有主动作。品牌点缀、焦点、选择与错误各有语义；提交按钮可用高对比中性色。
4. 不用三个大标题和口号填满空态。给出一句任务提示、可用输入和具体下一步。
5. 不把每个间距任意设为 16 或 24。相关控件用 8–12px，段落用 16–24px，区域之间用 32px 起；按内容而非整齐卡片数量调整。
6. 不拿英文截图决定中文字体。用混排句、长汉字标题和数字测试真实回退；不复制专有字体文件。
7. 不靠 11px 浅灰字制造精致感。正文和重要辅助信息需可读；弱装饰边框不能承担唯一交互提示。
8. 不让关键操作只在 hover 出现。键盘 focus-within 和无 hover 设备能发现同一动作；关闭后回到原触发点。
9. 不把 loading 画成永动旋转而没有归属。说明在处理哪个附件、等待哪种条件，提供适当取消与重试。
10. 不用假按钮、伪造成功和随机动画完成截图。每个可点击控件都有行为；状态变化与用户动作对应，减少动态效果时仍完整可用。

## Anti-Patterns

- 声称骨架就是 Claude 当前生产界面，或把静态包值称为已登录页面实测。
- 所有文本都使用一个 serif 栈；所有 24px 视觉控件都当成足够大的触控目标。
- 用 `open` 属性或 `show()` 假装模态；把原生 dialog 当作未经实测的严格首尾焦点循环。
- 紧凑模式直接缩小正文、根字号或触达区域，混淆观察到的 CDS 控件尺寸与原创布局选择。
- 深色模式仅反色；全局 `overflow:hidden` 隐藏溢出；全局强制断词破坏代码。
- 为复刻观感移除焦点环，或未经验证直接用白色小字覆盖陶土填充。

## Implementation seed

```html
<main class="conversation" aria-label="对话">
  <section class="transcript" aria-label="消息记录"></section>
  <form class="composer">
    <label for="prompt">你的问题</label>
    <textarea id="prompt" name="prompt" rows="3"></textarea>
    <button class="primary" type="submit">发送</button>
  </form>
</main>
```

不要给整个快速增长的 transcript 加 assertive live region。用独立、简短的状态区播报开始、结束与错误；为新增消息保留结构与可访问名称。
