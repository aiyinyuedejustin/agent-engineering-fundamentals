# Harbor：固定多步骤任务与模拟用户不是同一种多轮评测

研究日期：2026-11-06 UTC。固定源码 `26f95e0ebd8c77011bbf4656f5c98af66ce55848`。范围内收集关闭。**D3，未运行 Harbor、ACP CLI、模拟用户或模型。**已读实际多步骤任务的配置、各步 instruction/test，以及模拟用户任务的配置、persona、instruction 和外层 test.sh；没有逐项审计其完整 hidden test patch。

## 1. 先分开四种“多轮”

1. 同一 agent 内部的 model/tool loop。
2. 一个 task 中预先定义的多个有名字的 steps。
3. 模拟用户根据 target agent 的行为继续提问、澄清和验收。
4. 多 agent 子任务分工。

它们的预算、信息流和评分都不同。此版本 [MultiStepTrial 构造器](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/multi_step.py#L25-L71) 明确拒绝同时配置 user_agent，不能把两种模式直接叠加。

## 2. 固定 multi-step 的生命周期

[MultiStepTrial._run / _run_step](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/multi_step.py#L73-L173) 逐个创建 StepResult：

准备该步 → agent 运行 → 同步 logs → 收集 artifacts → 该步 verifier → 归档该步输出 → 决定是否继续。

agent environment 在步骤之间保持，不是每步从初始镜像重置。最后一步 separate verifier 才可以先停掉 agent 环境；前面步骤还要继续使用它。

### 文件状态持续与会话持续是两个开关

`resume_trajectory` 为 True 且不是第一步时，调用 agent.resume；否则使用新的 run。只有第一步使用 load_trajectory。构造期检查 agent 是否支持 resume，防止开始消耗环境资源后才发现不兼容。

[日志和 workdir 管理](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/multi_step.py#L272-L324) 会在 resume 时保留 session logs，并把该步 workdir 内容上传到当前 cwd；这是叠加上传，不是恢复完整干净环境。即便模型会话不延续，文件状态仍然可能延续。

### Grader 本身可能改变环境

shared verifier 后，下步之前清理 tests/verifier 输出目录，避免 agent 直接看到前步 grader 文件；这不等于回滚整个 workspace。

真实 [hello-multi-step-advanced](https://github.com/harbor-framework/harbor/tree/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/hello-multi-step-advanced) 的 implement test 会先把 config.txt 改为预期姓名，再改为 World 检查非硬编码。它是会写入状态的 verifier，不是纯读取观察者。shared/separate 模式下这些副作用的位置不同，迁移模式应重新验证每步前置条件。

## 3. 实际任务是怎样定义难度和分数的

已读 [task.toml](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/hello-multi-step-advanced/task.toml)：

- scaffold：创建可执行 greet.sh，输出 hello；agent timeout 60 秒；min_reward=1。
- implement：读取上传的 config.txt，按名字问候；agent timeout 90 秒；min_reward=0.5，并有 healthcheck 确认前步脚本可执行。
- document：写 README，同时不得破坏前步行为；agent timeout 60 秒。
- 每步 verifier timeout 30 秒；task-level greet.sh artifact 每步收集，README 只在最后一步收集。

[三步 tests](https://github.com/harbor-framework/harbor/tree/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/hello-multi-step-advanced/steps) 共用 [helpers.sh](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/hello-multi-step-advanced/tests/helpers.sh)，写 reward.txt 为 0 或 1。task 注释说 implement 可以接受 partial credit，但当前 test 实际是二元分数；阈值 0.5 本身不会创造部分分。

document test 只检查 README 中几个必要文本片段，并做功能 regression。这是该示例的验收范围，不应声称验证了文档全部语义或质量。

## 4. Early stop 和最终 reward 的细节

[_should_stop_after_step](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/multi_step.py#L198-L245)：

- 有 exception 且没有 verifier result 时停止。
- 没有 min_reward 时不按阈值停。
- 全局 disable verifier 时跳过阈值检查。
- min_reward 可以是单个 reward 阈值或按 key 的阈值；缺少所需 key 视为负无穷，不能通过阈值。

[Trial._select_multi_step_reward / _aggregate_step_rewards](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/trial.py#L915-L948)：

- FINAL 取最后一个**已执行** StepResult 的 verifier_result，不是保证执行过声明列表的最后一步。
- mean 路径只把具有 verifier_result 的步骤放入分母。
- 在这些已纳入步骤之间，缺失的 reward key 记为 0。

**解释用反例，不是运行结果：**若第一步 reward=1，第二步异常且没有 verifier result，mean 可能仍为 1；这并不说明两步都完成。FINAL 则可能是空 verifier result。最终 job 的 error/reward-validity policy 仍需另查，不能仅从此函数推断实际 leaderboard 分母。

建议 report 同时包含：planned/executed/graded steps、每步异常、early-stop reason、reward strategy、各 key 分母和最终 trial validity。

## 5. 模拟用户改变了信息提供方式

官方 [simulate a user](https://docs.harborframework.com/jobs/simulate-a-user) 描述：user agent 取得完整 task instruction，target 初始没有该 instruction，通过对话获得需求，最后运行 verifier。

[simulated_user.py](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/simulated_user.py) 默认把 persona、bridge instructions、task instruction 拼接。自定义模板必须包括 bridge_instructions 和 instruction，persona 可选。

[Trial._run_agent_phase](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/trial.py#L708-L793) 在这种模式下实际运行 user_agent，而 target 通过 bridge 被其消息驱动。两个角色共用任务环境；源码因此拒绝同一种 agent 的不同版本 pin，因为共享安装位置会使后安装版本覆盖前者。

**推断：**这不是单纯把相同 task 重复问几次。模拟用户的模型、persona、披露策略、可检查的 workspace 和停止标准，都会改变 target 得到的信息与反馈。角色间“私有指令”是实验信息流设定，不能自动当作操作系统级不可访问保证。

## 6. 实际模拟用户任务：tomlkit 转换器

已读 [任务目录](https://github.com/harbor-framework/harbor/tree/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/deepswe_tomlkit-toml-table-converters) 的 task.toml、instruction.md、persona.md 与 tests/test.sh。

- task 指定 tomlkit base commit `dd05eebc8ed9e30fc6c223088a5a450cb54c1cab`，要求多种 TOML table 表示的双向转换，并保留数据/注释/round-trip 行为。
- agent timeout 5400 秒，verifier 1800 秒，2 CPU/8192 MB，使用 task-specific 镜像 tag，允许联网。
- persona 要求先给模糊请求，看到实现后逐项披露要求，可只读查看 repository，但不能直接替 target 完成修改。
- verifier 先保存 model.patch，再重置 test patch 涉及的文件、应用测试 patch，执行 base 与 new 两组测试；两组都通过才写 reward=1。

这支持“自适应需求披露 + 最终代码测试”的案例描述。没有执行 persona rollout，也没有逐项审核完整 test.patch，所以不能断言模拟用户足够真实、所有自然语言要求都被测到或该 benchmark 已被完整复现。

## 7. ACP bridge 与两角色的成本不要混记

[Harbor ACP bridge](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/bridges/acp.py) 在此版本固定 acpx 0.11.2，配置 target command、默认 approve-all、单次 ACP prompt timeout 等。它教 user_agent 通过 acpx prompt 与 target 说话，默认 prompt 明确禁止 user_agent 自己编辑任务文件。

[_sync_agent_output](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/trial.py#L1167-L1186) 首先使用运行中的 user_agent 填 AgentContext/trajectory usage，再调用 bridge.enrich_context。

[extract_target_usage / enrich_context](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/bridges/acp.py#L76-L104) 与 [metadata 写入](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/bridges/acp.py#L270-L281) 从 ACP export 深度遍历，保留最后一个含 token-usage 形状 key 的 mapping，放在 acp_target_usage metadata。

这不是把 target 和 user 的账单合成已验证总成本的算法，也没有在该 helper 中证明选中的 mapping 是整个 target session 的累计总量。成本研究应分别保留两角色原始 usage、模型身份、parser/bridge 版本和缺失状态，随后再决定是否可相加。

## 8. 后续实验

1. 相同 workspace，用新 agent session 与 resume session 对照，分离文件记忆和对话记忆。
2. 在中间步骤没有 verifier result 时，对照 FINAL/mean 和 job-level validity，检查报告完整性。
3. shared/separate verifier 对同一任务执行正反例，检查 grader 副作用。
4. 固定 target，更换 user persona/model/披露策略，分层报告结果而非只给一个总分。
5. 给模拟用户放置不允许修改的受控文件，核验只读角色约束是否真正执行。
6. 将 user/target native counters 与 ACP export 对齐，确认成本与 token 统计。

以上是未执行计划。多轮评测首先需要定义“谁知道什么、谁可以做什么、每个阶段何时结束”，再讨论最终 score。
