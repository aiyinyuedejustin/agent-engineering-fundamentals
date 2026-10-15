# 色表补充：可求值不等于有等价HEX

原色表的23条表达式记录对应12个变量名。本次静态复核得到：**19条有确定数值，4条需要消费元素或级联上下文**。19条中14条可附常规HEX显示值，另5条必须保留超范围sRGB通道。

这是Claude Desktop Linux 2.37337.1包内声明在指定浅/深色配置下的派生结果，不是已登录页面实测，也不证明相关分支已启用。

## 计数怎么读

| 处理方式 | 记录数 | 内容 |
|---|---:|---|
| 相对RGB计算 | 16 | 八色tint × 浅/深主题 |
| 变量别名解析 | 2 | personal用户消息 → blue tint |
| CSS命名色 | 1 | 浅色Git draft hover：gray = #808080 |
| 保留上下文依赖 | 4 | 两条initial、两条currentColor混色 |

因此1,341条记录中，**1,337条有静态数值，1,332条有常规HEX显示值，5条为扩展sRGB，4条依赖上下文**。HEX仍是8-bit取整显示值，alpha单独保留。

## 五条超范围结果

RGB使用0–255数轴。它们不能用逐通道裁剪的HEX无损替代：

| 配置 / 变量后缀 | 未裁剪RGB | alpha |
|---|---|---:|
| light / bg-tint-violet | (169.142857,157.714286,256.714286) | .35 |
| dark / bg-tint-aqua | (-4.333333,45,35.666667) | .75 |
| dark / bg-tint-blue | (-3,35.666667,81) | .75 |
| dark / bg-tint-yellow | (58.333333,27.666667,-7) | .75 |
| dark / bg-user-message-personal | (-3,35.666667,81) | .75 |

[CSS Color 5](https://www.w3.org/TR/2026/WD-css-color-5-20260913/#relative-colors)保留相对色的超范围颜色分量，并单独处理alpha。正确导出应保留原表达式及color(srgb …)；若提供裁剪HEX/HSL，只能标为预览，不能冒充浏览器computed style、最终绘制像素或产品实测值。

计算用精确分数。例如浅色aqua红通道为 **(191 − 819/5) / (7/20) = 544/7**。分数分母有括号，避免误读为连续除法。18条相对色及别名均通过不先裁剪的alpha逆合成校验；参考底色是由公式常数推导的数学关系，不代表实际组件底色。

## 数值对应什么界面用途

- **Badge：** 非bold分支使用八色tint；bold分支使用另一组不透明色阶。
- **UserMessage：** personal背景走blue tint别名，但限于self、非editing、非fullWidth、非queued等条件。
- **Shortcut / kbd：** 边框跟随消费元素currentColor。默认文字色、onFill、实心按钮祖先会改变结果，不能统一补成灰色。文字本身若半透明，混色alpha还要相乘。
- **border-line：** initial不是黑色或透明色。对未注册自定义属性，它触发特定消费者中的var() fallback；当前浅/深配置分别回退到#0b0b0b/.1与#ffffff/.1。[自定义属性规范](https://www.w3.org/TR/css-variables-1/#guaranteed-invalid)
- **按钮与输入：** primary/secondary/ghost等按钮状态、TextInput和部分TextArea的field/hover/invalid/focus链已有可解析token。深色secondary普通ring透明，不代表pressed-ring或输入field-ring也透明。
- **Git draft hover：** 已确认token对象映射；尚无具体可见组件的结论。[gray命名色](https://www.w3.org/TR/css-color-4/#named-colors)

来源文件哈希、32个组件定位及中文结论见[组件定位元数据](component-consumers.public.json)，不附原压缩代码片段。

## 核验与使用边界

13项原创单元测试通过；云Chrome 154对原创最小页的19个数值及5个上下文例子 **24/24通过**，其中五条超范围computed值均被保留。这只验证浏览器颜色语义，不验证Claude页面的DOM、分支、完整级联或像素结果。核验摘要见[验证记录](verification.public.json)。

扩展目录应分别标记“静态数值”“扩展sRGB”“上下文依赖”，同时保留原声明与来源。不要使用裁剪HEX覆盖原式，也不要把默认消费示例写回全局token；局部作用域仍可能把tint换成opaque变量。
