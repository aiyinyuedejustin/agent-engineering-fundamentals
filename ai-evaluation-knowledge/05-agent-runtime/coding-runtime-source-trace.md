# mini-SWE-agent：从任务配置到 patch，和评分器的分界

研究日期：2026-11-06 UTC。范围内收集已关闭。mini-SWE-agent 固定到 `04d809ceab9df28f9adaed044884180159172930`，SWE-bench 固定到 `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`。

**D3，未运行 agent 或 benchmark。**已追踪 batch driver、真实 benchmark 配置、DefaultAgent、Local/Docker environment，以及提交文件和 SWE-bench report 缓存之间的边界。具体 SWE-bench 任务与 grader 另见 [任务案例](../03-benchmark-cases/swe-bench-task-and-grading.md)，本文件不重复该案例。

## 1. 三个程序不是一个程序

1. Agent driver 选择任务、配置 model/environment，驱动 agent 并保存 submission。
2. Agent loop 把模型输出变成工具动作和后续 observation。
3. Evaluation harness 把 submission 应用到独立任务环境，再按测试判定。

SWE-bench 分数不能从 agent exit_status=Submitted 推出；生成 patch 的容器也不应自动视为 grader 容器。

## 2. 实际 batch 入口

[run/benchmarks/swebench.py](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/run/benchmarks/swebench.py) 的链路如下：

- CLI 选择 subset/split，调用 load_dataset，然后按 instance_id filter/slice，可先固定 seed=42 shuffle。
- 默认跳过 preds.json 中已经有 key 的实例，是否成功不是此处筛选条件；`redo_existing` 才重做。
- 合并配置并创建 ThreadPoolExecutor；每个 instance 创建新的 model、environment、ProgressTrackingAgent。
- problem_statement 作为任务，agent.run 返回 exit_status/submission。
- finally 保存 trajectory，并把 submission 写入 preds.json 的 model_patch 字段。异常也有输出路径，不能把“preds.json 有此实例”当成成功修复。

[ProgressTrackingAgent](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/run/benchmarks/utils/common.py) 继承 DefaultAgent，只在 step 前更新进度显示，然后调用 super().step()。

### 默认选择也属于实验配置

源码默认 subset=lite、split=dev、workers=1，不是所有读者可能想当然的 Verified/test。load_dataset 调用未传 revision；构造的默认 task image 使用 `:latest`，除非实例本身提供 image_name/docker_image。

**推断：**仓库 SHA 固定，不代表 dataset revision、image digest、模型服务和外部依赖也固定。复现清单必须分别记录这些身份，不能只写“使用最新 mini-SWE-agent”。

## 3. 已读的真实 SWE-bench 配置

[config/benchmarks/swebench.yaml](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/config/benchmarks/swebench.yaml) 明确配置：

- step_limit=250，cost_limit=3.0。
- Docker environment，cwd=/testbed，单次 execute timeout=60，shell 为 bash -c。
- BASH_ENV 指向 /root/.bashrc，使非 login shell 也读取镜像的环境初始化。这一点会影响测试是否在正确环境中执行。
- 默认模型是配置中的带日期 Anthropic 标识，model_kwargs 包括 parallel_tool_calls=true。
- observation 超过 10,000 字符时展示前 5,000 和后 5,000，并告知中间省略。模型看到的 observation 不等于工具原始 stdout。
- 提交约定要求单独创建/查看 patch，再用完成 marker 和 patch 内容结束。

这些是该配置版本的事实，不是所有 CLI 模式的默认值。自定义 `-c` 会替换默认配置列表，源码帮助明确要求需要默认配置时自行加回。误以为“只覆盖一个参数”可能实际上去掉整份 benchmark 模板。

## 4. Agent loop 的预算和控制流

[DefaultAgent](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/agents/default.py) 可分为：

1. run 渲染 system/task 模板，初始化 messages。
2. query 在模型调用前检查调用数、已花费金额和 wall clock。
3. 增加 n_calls，调用 model.query，累计返回 cost，保存 assistant message。
4. execute_actions 通过 list comprehension 依次执行该消息内的 actions，统一格式化 observations。
5. 捕获格式错误或退出信号；每轮 finally 保存轨迹；最后一条 role=exit 时停止。

**预算单位：**step_limit 实际限制 model query 次数，不是 shell command 数。一个响应可以包含多个 action；此 DefaultAgent 顺序执行它们，尽管请求模型配置允许 parallel_tool_calls。允许模型输出多个 tool call，不代表 executor 并行。

**预算时点：**cost_limit 检查的是调用前已知累计成本，最后一次生成可以使总金额超过阈值，源码注释也写了 after exceeding。wall_time_limit 同样在 query 边界检查，不会单独打断已开始的模型或工具调用；工具 timeout 是另一层。

**对象复用：**cost、n_calls 和 start_time 在构造器初始化，run 重置 messages 但没有重置所有这些计数。自定义集成若重用一个 agent 对象，需要理解这点；本轮 batch driver 每实例新建 agent，所以不能据此声称默认 batch 有跨样本预算污染。

## 5. Local 和 Docker environment 不是可互换的安全假设

[LocalEnvironment](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/local.py) 直接在本机执行 shell，并继承 host os.environ 与显式 env。每次 action 新建 shell，cd/export 不跨调用持续，但文件修改持续。

其 `_run` 在 POSIX 设置 start_new_session，timeout 后 killpg 并 drain 输出；非 POSIX 只调用 process.kill。这个具体实现比“subprocess 超时就结束所有工作”的口号更精确，也不是任意脱离 process group 后代都可清理的证明。

[DockerEnvironment](https://github.com/SWE-agent/mini-swe-agent/blob/04d809ceab9df28f9adaed044884180159172930/src/minisweagent/environments/docker.py) 在构造时 docker run 一个 sleep 保活容器，再逐 action docker exec。它合并 stdout/stderr；超时被转为 returncode=-1 与 exception_info observation。cleanup 启动异步 stop/rm shell，析构时调用，不是阻塞等待并验证所有资源已删除。

**工程推断：**本机模式不应被描述为 sandbox；Docker 模式需要独立验证容器配置、网络、mount 和清理结果。不能仅用相同 Environment protocol 证明隔离相同。

两个环境的完成检测都要求首行完成 marker 且命令 returncode=0，再抛 Submitted，后续内容作为 submission。这个协议用于结束 agent，不负责判断 patch 是否正确。

## 6. 两层缓存会影响“重新跑一次”的含义

Agent driver 的跳过条件是 preds.json 中有 instance_id；SWE-bench [run_instance](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/run_evaluation.py#L229-L275) 的 report 路径则由 run_id、清洗后的 model_name_or_path、instance_id 组成。

如果 report 已存在，源码直接读取返回，没有在该分支比对 patch hash、task revision 或 grader revision。`rewrite_reports` 是从已有 test output 重新生成 report，不是重新运行测试。

**推断：**修改 patch 后复用这些身份，可能得到旧报告。实验管理应选择新的 run_id 或明确清理可恢复缓存，同时记录 patch hash、task/image/grader 身份。这里是由缓存条件得到的风险分析，未声称任何已公布结果受到影响。

SWE-bench [get_eval_report](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py#L329-L394) 对无法解析测试输出可标 infra_failure，但 resolved 仍保持 False，该标志是诊断性信息。它不会自动证明样本已从任何上游聚合分母排除。最终分母需要另查 aggregation policy。

## 7. 最小可审计记录与后续实验

建议每个样本保留：dataset revision、instance_id、task base commit、image digest、完整合并配置、agent/模型/环境版本、effective limits、native trajectory、patch hash、agent exit_status、grader execution status、test results、cache hit 与 cleanup status。

未执行的高价值实验：

- 同一 model query 返回 1 与多个命令，对照 model-turn 与 action 数量。
- 最后一次模型调用越过 cost_limit，核对最终 usage，而非只看 limit 参数。
- 同 run_id/instance/model 改 patch，再对比新 run_id，验证缓存行为。
- 提交空 patch、无效 patch、正确 patch，区分 Submitted、applied 和 resolved。
- 中途杀进程，检查非原子 write_text 的轨迹/预测文件是否可恢复，以及后台容器是否仍在。

上述最后一项是故障注入计划，不是已观察到的文件损坏。局部自写实验可展示机制，但不替代原系统运行。
