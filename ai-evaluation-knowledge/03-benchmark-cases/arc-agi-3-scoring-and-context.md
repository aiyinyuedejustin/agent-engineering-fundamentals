# ARC-AGI-3：动作效率、上下文策略和计分模式

研究日期：2026-11-06。整体深度保守保持 **D1**：官方文档、配置及代码已读，但公开网页未返回 ls20 的实际帧与完整游戏元数据，本次也没有下载游戏包。另有 **D3 范围的 harness/评分源代码追踪**及**局部 D4 计分函数实验**；这些不等于玩过游戏或复现模型成绩。

## 版本与证据范围

- 官方 benchmarking harness：`353d38be471395b5ae47dbb44df95440677397e1`，2026-11-01。
- ARC toolkit：`f12822c4d550121c35a275008d964afbbed47d2f`，2026-06-10，README 对应 0.9.9。harness 的 `uv.lock` 也锁定 `arc-agi==0.9.9`；未另下载 wheel 核对字节一致性。
- 已读：harness 的 `main.py`、`swarm.py`、`base.py`、agent 的动作/预算/上下文/retry 主路径、两类实际模型配置、runtime-state 文档；toolkit 的计分实现、环境加载与关闭记分卡路径。
- [ls20 官方页面](https://arcprize.org/tasks/ls20)确认它属于 Public Demo，但文本抓取只得到加载占位符。两个官方 API 地址的读取也未返回元数据。因此不使用搜索得到的第三方人类基线数组冒充已核实任务数据。

[固定 harness](https://github.com/arcprize/arc-agi-3-benchmarking/tree/353d38be471395b5ae47dbb44df95440677397e1) · [固定 toolkit](https://github.com/arcprize/ARC-AGI/tree/f12822c4d550121c35a275008d964afbbed47d2f)

## 1. 不是“做对几道图形题”

RHAE 将完成关卡与相对人类的环境动作效率组合起来。官方人类基线来自首次接触游戏的参与者，按关卡采用动作数的 upper median。内部推理、模型重试或不改变环境的内部工具调用，不是计分动作。

源码 `EnvironmentScoreCalculator` 的路径是：

1. 完成关卡且动作数大于零，算 `100 × (human_actions / agent_actions)^2`，单关最多 115。
2. 未完成关卡记零。
3. 关卡以从 1 开始的序号加权，后面的关卡权重更大。
4. 游戏总分再受到已完成关卡权重占比的上限约束，不能靠极快完成前几个关卡补回没完成的后面关卡。
5. 本地 `from_scorecard` 在已有环境记录上计算游戏分数，再求环境均值。线上 competition 的范围约束另见下节，不能用本地子集均值替代。

[官方方法](https://docs.arcprize.org/methodology) · [计分源码](https://github.com/arcprize/ARC-AGI/blob/f12822c4d550121c35a275008d964afbbed47d2f/arc_agi/scorecard.py)

### 局部实验：相同 completion 不等于相同 score

实验使用五关、每关人类基线均为 10 的合成输入，AST 抽取原始算分类执行，没有加载游戏引擎。

| 合成条件 | 算得游戏分数 |
|---|---:|
| 五关全部完成，每关 10 动作 | 100 |
| 五关全部完成，每关 20 动作 | 25 |
| 前四关每关 1 动作，第五关未完成 | 66.6667 |
| 只完成第一关，使用 10 动作 | 6.6667 |

另检查了动作数为零时的防御分支，不将该输入说成可达游戏轨迹。结果说明 RHAE 分数的百分号不是普通完成率，四关完成也不能简单写成 80%。

[可复跑脚本](arc_score_probe.py) · [实际输出](arc-score-probe-output.json)

## 2. 同一个 scorecard 名称不保证同一实验规则

toolkit 的 `EnvironmentScoreList.score` 属性实际返回多个 run 的 **最大**分数，虽然附近 docstring 写着 average。合成的 20、80 两次 run 得到 80，不是 50。这是对该属性的窄范围验证，不是说所有官方排行榜允许无限重试取最好结果。

官方 Competition Mode 文档另规定：全部可用环境进入评分、每个环境只能 make 一次、只可重置关卡、只有一张记分卡、过程中不能查询分数。harness 的 `Swarm` 默认构造 `OperationMode.ONLINE`，而不是 `COMPETITION`；线上返回分数来自服务端，不能把本地算分实现与服务端协议无条件视为同一完整实现。

因此，报告至少要带上：游戏完整版本 ID、公开/私有 split、operation mode、实际参与的游戏范围、运行次数、run 选择规则。仅贴一个 scorecard 链接还不够说明它与竞赛成绩可比。

[模式文档](https://github.com/arcprize/ARC-AGI/blob/f12822c4d550121c35a275008d964afbbed47d2f/README.md#competition-mode) · [Swarm](https://github.com/arcprize/arc-agi-3-benchmarking/blob/353d38be471395b5ae47dbb44df95440677397e1/benchmarking/swarm.py) · [线上/本地关闭路径](https://github.com/arcprize/ARC-AGI/blob/f12822c4d550121c35a275008d964afbbed47d2f/arc_agi/base.py)

## 3. 视觉环境不意味着模型收到了图片

当前官方 agent 的 `build_frame_content` 把帧转换为整数网格的**文本行**，并附状态、已完成关卡和可用动作。动画超过默认 7 帧时均匀抽取；这不是把每个原始帧作为图像直接输入多模态模型。

动作输出则有三种解析入口：严格 JSON、XML、历史兼容自由文本。11 月 1 日修订加入平铺 JSON 的规范化，非法结构不回退到正则误取偶然出现的动作名；自由文本则选择最后出现的有效动作。坐标必须在 0–63 范围内，JSON 入口还拒绝以字符串、浮点或布尔值代替真正整数。

环境任务的模态和 harness 实际交给模型的模态需要分别登记。同样，解析器版本属于实验条件，不只是程序内部小细节。

[帧转换与动作解析](https://github.com/arcprize/arc-agi-3-benchmarking/blob/353d38be471395b5ae47dbb44df95440677397e1/benchmarking/agent.py)

## 4. Standard 与 Provider Adapter 并非只换 API 地址

- **Standard / manual_rolling**：保留可读文本历史，提示模型把要携带的发现写进回答；按估算 token 数裁掉较早轮次。
- **Provider Adapter / continuous_conversation**：保留 provider 原生会话/推理状态；使用原生压缩，或没有原生机制时使用 harness 摘要。只有输出被成功解析为合法动作，临时返回状态才成为下一轮的已接受状态。

实际配置例子：`openai-gpt-5-4-2026-03-05` 使用 manual_rolling；`openai-gpt-5-6-sol-max-provider-adapter` 使用 Responses、continuous_conversation 和原生 compaction。这两个例子还换了模型，所以不是可用于估计“只改状态策略效果”的受控实验。本次未调用它们。

官方 README 要求两类 harness 的结果分别标注；相同游戏、动作和评分，不足以保证上下文信息相同。

[配置](https://github.com/arcprize/arc-agi-3-benchmarking/blob/353d38be471395b5ae47dbb44df95440677397e1/benchmarking/model_configs.yaml) · [状态协议](https://github.com/arcprize/arc-agi-3-benchmarking/blob/353d38be471395b5ae47dbb44df95440677397e1/docs/runtime-state.md)

## 5. 动作预算与计算预算要拆开

上述两个配置都把每关动作预算设为 `ceil(human_baseline × 5)`；无基线时另有 fallback。基类还有 12 小时 wall-clock 默认值。解析失败、空回复与临时 API 错误走不同重试计数；模型使用量可累计到最终记录，但只有随后提交的环境动作推进环境计数。

因此，RHAE 很高不自动意味着费用低或响应快。对应用选择有用的报告应同时给出完成率、RHAE、环境动作、模型调用与重试、输入/输出/推理 token、压缩开销、费用、wall-clock 和停止原因。

**本次边界**：未获取 API key、未注册账户、未建立线上记分卡、未玩任何游戏、未执行未知游戏源代码、未复算官方人类基线或模型排行榜；组件实验不应被引用为完整 ARC-AGI-3 的 D4 复现。
