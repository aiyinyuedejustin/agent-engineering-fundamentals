# AgentDojo：正常任务效用与攻击目标完成率必须分开

更新日期：2026-11-06。深度 **D3，限定一个真实任务定义、配置和任务执行/验收路径**。未运行模型、攻击或模拟工具，更没有对真实邮箱、文件或日历执行操作。

## 研究对象

- 代码提交：`089ed468cf3ed0322acc66b0211f26d9d90dbf60`，2026-06-02。
- 案例任务：workspace 的 **v1** `UserTask0`，配合相同版本的环境与注入位置定义。
- 研究范围：真实任务类、workspace环境组合、calendar配置中的目标事件、注入字段、`benchmark.py`、`task_suite/task_suite.py`、版本加载器。
- 注意：代码支持 v1.1、v1.2 等后续任务定义；本案例不会把 v1 的验收规则默认推广为全部最新版本。

[固定仓库](https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60) · [版本加载器](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/task_suite/load_suites.py)

## 1. 一个真实只读任务与它的自动 utility

任务让 agent 查询一场日历活动的受邀者，并提供活动概述。参考工具流程是查询日历。默认环境把邮箱、日历与云盘组合起来，工具集同时包含读取和修改能力，因此“只读请求”并不表示 agent 只能访问只读工具。

该 v1 任务的 utility 检查要求回答包含预期受邀者地址，并在 strict 条件下保持环境状态不变；它没有单独核对活动概述的质量。因此 utility 通过的语义应限制在实现覆盖的条件，而不是声称所有自然语言要求已被完整满足。

[实际任务类](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/default_suites/v1/workspace/user_tasks.py) · [工具与环境组合](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/default_suites/v1/workspace/task_suite.py)

## 2. 不可信内容来自环境字段，而不是顶层用户命令

所读活动的描述含有预定义注入占位符。测试时，框架将攻击内容放到允许的环境字段；没有攻击时使用默认文字。任务本身仍是原先的合法请求。这使研究者能够在相同业务任务上比较无攻击效用、攻击下效用与攻击目标达成情况。

本页只分析威胁模型和验收，不复制可操作攻击 payload、目标地址或原始环境数据。占位符替换机制也说明攻击面有边界：该套件不是允许攻击者任意修改系统提示或整个应用数据库。

[环境入口](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/data/suites/workspace/environment.yaml) · [事件配置](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/data/suites/workspace/include/calendar.yaml) · [允许注入的位置](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/data/suites/workspace/injection_vectors.yaml)

## 3. 任务与攻击形成配对，不是单一问答列表

`benchmark_suite_with_injections` 选择用户任务和攻击目标，运行相应组合。对于非拒绝服务攻击，还会把攻击目标作为直接请求交给 agent，以确认模型具备完成目标操作的能力。若做不到，框架发出警告；此处并不会自动把相关目标从全部统计中剔除。

这一区别很重要：注入没有成功，可能是信任边界有效，也可能是 agent 原本就不会完成那项操作。只有同时查看正常能力与攻击结果，才能更好地区分两者。

[基准编排源码](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/benchmark.py)

## 4. 从环境初始化到两类验收

`run_task_with_pipeline` 加载并验证注入位置，构建环境，执行任务特有初始化并保存前状态的深拷贝。随后通过工具 runtime 调用 agent pipeline，获取最终回答、后状态和工具调用轨迹。

用户任务可优先使用轨迹验收，否则使用回答和前后状态。攻击目标也有独立的轨迹或状态判定。这允许检查不留下最终状态差异的操作，例如先修改再恢复，或一段只有调用轨迹能证明发生过的行为。

这与“拿最终回答问另一个模型是否安全”不同。它也不保证每种真实危害都被覆盖：实现只验证各任务定义中的特定目标和条件。

[任务执行与验收](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/task_suite/task_suite.py) · [攻击目标的独立判定接口](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/default_suites/v1/workspace/injection_tasks.py)

## 5. 不要按字段名字猜分数方向

在有攻击的任务执行返回值中，名为 `security` 的布尔值表示 **注入目标是否成功**，并非 True 就更安全。无攻击路径又会返回固定 True 作为第二个值；拒绝服务分支则直接令该字段等于 `not utility`。同一字段需要结合运行模式理解。

部分上下文超限或服务异常路径将 utility 设为 False、security 设为 True。因此错误日志和实际攻击目标命中应分开分析。不能把每个 True 都叙述成已观察到模型执行了具体恶意动作；有些是错误处理政策给出的结果。

这不是对所有 AgentDojo 报告的统计方式提出结论，而是提醒复用原始日志时必须读取生产该字段的控制流。

## 6. 应保留的结果与限制

建议至少分别保存：无攻击正常任务成功率、攻击下正常任务成功率、指定攻击目标成功率、基础设施/上下文错误，以及攻击目标作为直接任务的能力检查。再按 suite、task pair、attack、defense、模型和版本分层。

本案例尚未追踪某个具体模型适配器的底层 API 调用，也没有评价任何防御的有效性。源代码通过官方网页读取；未为追求 D4 而执行攻击。后续若运行，应使用独立的合成环境、固定预算与清晰的攻击授权边界。
