# Harbor：黑箱 CLI、trial 和 verifier 的源码链路

研究日期：2026-11-06。固定提交：`26f95e0ebd8c77011bbf4656f5c98af66ce55848`。范围内收集已关闭：单步 trial、installed agent 生命周期、Codex CLI 接入、artifact→separate verifier、reward 读取。网络后端和多步 trial 另行研究。

**达到 D3，未达到 D4。** 已读官方文档、实际任务配置及代码执行链；没有运行 Harbor、调用模型或启动云沙箱。以下“源码事实”不表示所有 provider 已经实测。

## 1. 需要分开的四个对象

- **Agent** 是执行任务的程序；模型只是 agent 的一个组成部分。
- **Environment** 提供进程、文件、网络等机制，不应与 agent loop 混为一体。
- **Trial** 是某 agent 对某 task 的一次尝试，负责生命周期与证据收集。
- **Verifier** 根据 task 的判定逻辑生成 reward。

官方 [core concepts](https://docs.harborframework.com/core-concepts) 区分这些对象。[custom agents](https://docs.harborframework.com/agents/custom-agents) 进一步区分 installed agent（CLI 在任务环境内运行）与 external agent（loop 在 Harbor 侧，通过 BaseEnvironment 操作任务环境）。这不是“开源/闭源”分类，而是运行位置分类。

## 2. 实际执行顺序

源码入口为 [Trial.run](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/trial.py#L608-L685)：

1. 初始化结果、发出开始事件。
2. prepare：验证能力、启动环境、healthcheck、注入 task skills、安装/配置 agent。
3. 进入具体 trial 的 run。
4. 异常路径记录异常并尝试恢复输出。
5. finally 路径关闭 bridge、停止环境、保存 result、清理敏感数据与日志句柄。

具体 [SingleStepTrial._run](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/single_step.py#L38-L113)：

agent run → 同步 agent logs → 收集 artifacts → separate 模式先停止 agent 环境 → verifier → shared 模式停止环境。

agent timeout 与 nonzero exit 会在 agent 子阶段被记录，后续仍可尝试验收已有产物。因此“agent 进程错误”“reward 是 0”“trial reward 是否有效”是三个问题。官方 [error classification](https://docs.harborframework.com/jobs/error-classification.md) 为 retry、grade、reward validity 分别定义决策；预算耗尽与基础设施失败不应使用同一失败标签。不要根据“verifier 曾运行”推断该样本一定计入最终分母。

## 3. 黑箱 CLI 接入并非只做 subprocess 包装

[BaseInstalledAgent.setup](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/agents/installed/base.py#L1171-L1213) 依次执行 install、configure。skip_install 仅跳过安装，configure 仍运行，并尽可能检测镜像实际提供的版本，而不是沿用未经核验的 requested version。

[Codex.run](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/agents/installed/codex.py#L2070-L2250) 的接入工作还包括：

- 解析实际模型标识、推理参数与 CLI flags。
- 解析认证来源，生成运行时有效 config。
- 创建 agent 自有目录，传递任务 skills/MCP 设置。
- 决定新会话还是 resume，准备旧 session。
- 启动 headless CLI、保存 JSON 输出、最终复制原生日志。
- 运行后尝试清理临时认证/config 目录。

这一 adapter 在任务环境内关闭 CLI 自身的 approvals/sandbox，由外层执行环境承担隔离。**工程推断：**不能直接把该启动命令移到个人主机上；“benchmark 内允许的执行方式”不等于“本机安全默认”。

观测对象必须包括 CLI 版本、有效 config、模型参数、内置工具、原生日志 parser 版本、sandbox 能力。只记录 model name 无法完整描述被评测系统。

## 4. 真实任务证据：separate-verifier-environment

已读以下同一任务的四个文件：

- [task.toml](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/separate-verifier-environment/task.toml)
- [instruction.md](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/separate-verifier-environment/instruction.md)
- [environment/Dockerfile](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/separate-verifier-environment/environment/Dockerfile)
- [tests/test.sh](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/examples/tasks/separate-verifier-environment/tests/test.sh)

此例要求 agent 生成两个文件，一个在约定 publish 目录，一个在显式 artifacts 配置中。verifier 验证二者内容，还检查未声明的 scratch 文件没有出现。agent 与 verifier 都配置 no-network、60 秒执行预算，资源亦显式写入。镜像使用 ubuntu tag，并非不可变 digest。

这不是“复制整个 agent 文件系统到 grader”：[separate verifier 源码](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/trial.py#L1020-L1141) 创建新环境、清空 reward 目录、上传声明产物、构建 verifier 后执行。任务没有声明的必要输出可能导致假失败。task filesystem、native session 和 trajectory 是不同恢复对象。

官方 [separate verifier 文档](https://docs.harborframework.com/tasks/separate-verifier.md) 说明新建任务默认配置 separate，但旧任务两个相关字段都省略时仍是 shared。因此仅凭新 CLI 的默认模板不能断言旧 benchmark 全部采用隔离 grader。

## 5. reward 的权威来源

[Verifier.verify](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/verifier/verifier.py#L193-L310) 的核心路径是：

清理 stale reward → 上传/使用内置 tests → 执行 test script → 下载 verifier 输出 → 优先解析 reward.json，否则 reward.txt → 返回 VerifierResult。

[reward parser](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/verifier/verifier.py#L69-L126) 检查空文件、格式与非有限数值。**源码事实：**test.sh 的退出码不是这个方法直接采用的最终分数；它期待 reward 文件。**工程推断：**自建任务必须测试 script 崩溃、空 reward、陈旧 reward、NaN/Infinity、多个 reward 文件、输出下载失败，而不只是 oracle happy path。

## 6. 尚不能从本轮推断的内容

- 没有证明 Docker、Modal、Daytona 等后端在超时、取消、输出截断、网络切换上等价。
- 没有证明所有 Codex 原生事件都能无损转成 ATIF。
- 没有检查全部 agent parser；某一个 adapter 的行为不能泛化到其他 CLI。
- 没有证明 isolated verifier 可以阻止所有 reward hacking；被读取的产物依然是 agent 可控输入。
- 尚未执行 oracle、nop、故障注入或 end-to-end 对照，不能宣称达到 D4。

## 7. 后续有判别力的实验

以下是实验计划，不是已验证结论：

1. 同任务运行 oracle、nop、写错文件、只在未声明目录写文件，验证 grader 正反例。
2. 相同 artifact 在 shared/separate 两种模式重评分，核查 grader 环境依赖。
3. timeout 后检查完整进程树、后台工作与 artifact 稳定时间，区分取消协程与停止工作。
4. 故意截断 CLI JSONL、删去子 agent 日志、破坏图片引用，检查“无轨迹”是否会被误当零成本。
5. pinned CLI 对比未固定版本，保存生效配置与工具清单，而非只保存用户输入参数。

