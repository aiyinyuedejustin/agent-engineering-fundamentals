# AndroidWorld：模拟器启动、应用快照与任务状态并不是同一层

状态：本篇证据子集已闭合。阅读日期2026-11-06。学习目标L2→L3。

版本：google-research/android_world固定commit `55ddaf5edc6f6c25673aed343907d5b9dca66f84`。README说明Docker支持仍为experimental；不是所有部署方式经过等价性验证。

深度：实际Calendar任务及Docker配置D2；启动、任务初始化、应用快照、时间、异常清理相关代码D3；5个本地原样AST/mock实验D4。没有安装Android、执行ADB、启动模拟器/容器、调整权限或运行模型。局部D4不等于Android任务复现或隔离证明。

## 1. 五层状态必须分别命名

| 层 | 本案例中的对象 | 不能替代的其他层 |
|---|---|---|
| 主机/容器 | Linux或macOS、KVM/CPU架构、实验性Docker封装 | 不能保证任务数据库基线 |
| 模拟设备 | Pixel 6、API33、AVD用户数据、emulator进程 | 冷启动不等于出厂重置 |
| 应用 | APK、/data/data内数据、权限、安全上下文 | 应用数据copy不等于整机快照 |
| 任务 | 特定数据库表、噪声记录、参数seed、当前日期 | 不等于所有应用与共享存储归零 |
| 控制与观测 | ADB、gRPC无障碍树、连接恢复 | 观测操作不一定只读 |

README推荐Pixel6/API33；launcher源码也明确这是测试和开发配置，其他配置未验证。固定代码版本不自动固定Android系统镜像修订、APK字节或宿主加速模式。[A1][A2]

## 2. 实际启动链：连接已存在设备，而不是每个episode新建VM

标准路径先由操作者启动模拟器，再由`load_and_setup_env`连接。`get_controller`建立AndroidEnv配置：console端口、相邻ADB端口、gRPC端口；若底层配置支持`connect_to_existing`则设置为True，再安装/启动无障碍forwarder wrapper。[A2][A3]

```text
模拟器进程 / 既有AVD
  → AndroidEnv controller连接
  → 无障碍forwarder wrapper初始化
  → 可选首次安装/配置应用并保存应用数据快照
  → 配置日期/时区
  → 创建带参数的任务集合
  → 每个任务 initialize → agent → scorer → tear_down
```

`run.py`最终正常路径关闭env，但这是一次suite的生命周期，不是每个任务销毁整个模拟器。[A4]

### Docker不自动成为安全沙箱

固定README示例用`--privileged`启动容器；Dockerfile安装模拟器、创建Pixel6/API33 AVD，entrypoint启动headless emulator、执行`adb root`、再运行服务。[A1][A5] 这是便于控制的测试设备方案，不应据此宣称宿主面对不可信代码或应用具有强隔离。

headless脚本还会列出ADB可见的emulator并逐个发送kill，再启动一个新设备；后续多条ADB命令没有显式serial。放入共享ADB server的多设备环境之前，必须检查影响域，不能直接把“单实例脚本”当作安全并发launcher。本研究没有执行这些命令。[A5]

加速检测读取CPU的vmx/svm标志，无法单靠这一点证明容器有可用KVM设备、嵌套虚拟化权限和正确架构。README明确指出Apple Silicon上AMD64容器的双层模拟会很慢。2048MB是模拟器参数，不是整个宿主进程/容器的峰值内存保证。[A1][A5]

## 3. -no-snapshot并不清空用户数据

推荐启动命令和headless脚本带`-no-snapshot`。Android官方文档把它定义为禁用Quick Boot快照的载入/保存；另一个`-wipe-data`选项才重建用户数据分区。官方文档还说明SD card镜像不随wipe-data删除。[D1]

因此至少要分别记录：

- 是否冷启动；
- AVD的userdata镜像是否复用；
- SD card/共享存储是否复用；
- 应用数据快照是否恢复；
- 特定任务数据是否清空并重新生成。

“我们用了-no-snapshot”不足以回答后四项。它也不否定项目可以通过应用/任务层完成需要的重置。

## 4. 应用snapshot其实是设备内目录复制

`app_snapshot.py`把应用私有目录复制到设备内`/data/data/android_world/snapshots/<package>`，同一应用只有一个快照，后保存的覆盖前者。它不保存运行内存、整机设置、其他应用、整个共享存储或外部服务。[A6][A7]

restore流程是：

1. 关闭应用；
2. 检查快照目录存在，否则RuntimeError；
3. 尝试清空应用目录，清理RuntimeError只warning；
4. `copy_dir`复制快照到应用目录；
5. 发出restorecon与递归chmod777命令，作为权限/安全上下文丢失的修复措施。[A6]

`file_utils.copy_dir`最终构造设备端`cp -a source/. dest/`。这不是文件系统事务或完整VM回滚协议。[A8] 本地mock验证清空目录失败后，代码仍走复制和权限命令；这些命令只被记录为字符串，没有实际执行。[X1]

更上层`TaskEval._initialize_apps`捕获restore的RuntimeError后跳过继续。首次`setup_app`也会在app.setup的ValueError后继续保存快照。因此“有快照目录”和“快照是经过验证的完整基线”是不同断言。[A6][A9][A10]

不要把这些分支直接转化为“所有任务都不可靠”。具体任务可能有更严格的清表、重建和初始状态验证，下一节正是这样的例子。

## 5. 真实案例：Calendar任务有任务级数据库合同

`SimpleCalendarAddOneEventTomorrow`要求在Simple Calendar Pro为“明天”新建事件，继承`SimpleCalendarAddOneEvent`及SQLite任务基类。目标包含小时、标题、描述、时长；参数生成使用基准日期次日，添加0–20条噪声事件。[A11]

固定代码的基础日期是2023-10-15 15:34:00 UTC，所以本任务中的“明天”来自这个实验日期，不是运行者真实当天。应用显示的日期、目标参数和验证时间解释必须一致。[A7][A11]

初始化链中，SQLiteApp先清空目标表以修复上次崩溃残留，再调用TaskEval初始化，再清表一次并加入噪声；AddMultipleRows随后保存before行集合。验证读取after并检查目标添加完整性，正常teardown也清表。[A12]

这说明重置合同是组合的：即使基础应用快照层选择容错继续，特定数据库任务还会执行自己的清理。审查单个snapshot warning不能替代读取真实任务继承链。本次没有执行这些数据库操作，也没有生成或评分一个真实Calendar episode。

### “冻结时间”的准确含义

launcher参数叫`freeze_datetime`，其setup方法关闭自动时间/自动时区，设置24小时制与UTC；TaskEval每次任务初始化再设置具体date。[A2][A10][A13] 所读实现不是停止系统时钟的虚拟时钟机制。任务开始后时间仍会推进，不能把它描述为整个episode时间完全静止。

实验时应记录设备起始时间和真实elapsed time两套时钟；尤其涉及“今天”“明天”、提醒、计时器、超时，不能把设备日期回拨与宿主性能计时混用。

## 6. 观测也可能改变设备

`get_a11y_tree`发现airplane mode开启时，为恢复gRPC无障碍树，会调用`attempt_enable_networking()`并等待，然后读取树。[A3]

本地原样函数mock实验确认调用发生，再返回给定forest。这只证明**观测路径含有修改请求**，未验证真实设备上网络变化、连接内容或任务影响。[X1]

由此得到一个应逐任务核查的问题：若任务目标涉及网络设置，观测恢复动作是否会改变待评价状态？即使没有这样的任务，也应把自动恢复动作记入轨迹，避免把所有状态变化都归因于agent。该问题不能靠“工具名叫get”来排除。

## 7. 异常清理与幂等性不能只看正常流程

`suite_utils._run_task`把initialize、run_episode与is_successful放在try里；异常被记录并转为失败结果后立即return。正常路径末尾才调用`tear_down`，不是finally。[A14] 本地mock episode抛错后，原样函数返回失败结果且不调用teardown。[X1]

这不自动证明后续episode被污染，因为新任务初始化可能主动重置；但平台需要区分“正常清理完成”“异常后依赖下一次初始化修复”“实例应退休重建”三种状态。

另一个小而具体的幂等性细节：`TaskEval.initialize_task`先清interaction cache、初始化时间和应用，再检查`self.initialized`。第二次调用会抛“already called”，但检查前的重置请求已经发生。mock断言确认顺序。调用者不能假定重复初始化异常意味着没有副作用。[A10][X1]

suite的本地计分tally还会跳过带EXCEPTION_INFO的episode；这只是所读路径，不等于完整论文/排行榜分母。本篇不审计全部聚合逻辑，应分别报告模型失败、环境/评估异常和清理状态。[A14]

## 8. 最小实验与下一步验收

[实验目录](experiments/androidworld-lifecycle/README.md)保存可复查脚本、固定完整源文件哈希和实际输出。2026-11-06T03:45:27.036232+00:00，5项PASS：

- 无障碍树读取遇到airplane mode时请求启用网络；
- 缺应用snapshot的RuntimeError不阻止基础initialized标记；
- 重复初始化在guard前已请求时间/应用重置；
- restore清目录异常后继续复制及记录权限修复命令；
- episode异常路径跳过teardown。

全部Android/文件/ADB操作都是mock。测试输出中的异常和warning是故障注入的预期输出，不是失败的测试或真实设备操作。

真实平台的后续验收应使用独占测试AVD，不连接个人手机：

1. 固定SDK、system image、APK、AVD配置和快照内容指纹，不能只记API level。
2. 给每个worker独立AVD数据目录、console/ADB/gRPC端口和明确device serial。
3. 为正常结束、agent异常、验证异常、进程终止分别检查应用数据、共享目录、时间和网络设置。
4. 校验重置后语义状态，而不只检查boot_completed或快照目录存在。
5. 对所有观测恢复操作留审计事件，标明它们何时改变设备。
6. 在权限开放的模拟器与真实宿主之间维持独立安全边界；不要把为评分便利而root的设备当作生产安全配置。

这些是待执行的工程验收计划，不是已经完成的运行。

## 来源与范围

- [A1 README](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/README.md)：完整阅读，测试设备、实验性Docker、模型成本与部署说明。
- [A2 env_launcher.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/env_launcher.py)：完整阅读，连接与setup。
- [A3 controller](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/android_world_controller.py)：完整阅读；仅get_a11y_tree局部mock执行。
- [A4 run.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/run.py)：主流程197–243等相关区段已读。
- [A5 Docker配置](https://github.com/google-research/android_world/tree/55ddaf5edc6f6c25673aed343907d5b9dca66f84/docker_setup)：start_emu.sh、start_emu_headless.sh、entrypoint.sh及根目录Dockerfile完整阅读，未执行。
- [A6 app_snapshot.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/utils/app_snapshot.py)：完整阅读；restore函数mock执行。
- [A7 device_constants.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/device_constants.py)：完整阅读。
- [A8 file_utils.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/utils/file_utils.py)：clear_directory、mkdir、copy_dir，102–225相关段落；不是全文件审计。
- [A9 setup.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/setup_device/setup.py)：完整阅读，首次配置与快照。
- [A10 TaskEval](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/task_evals/task_eval.py)：完整阅读；初始化两个方法mock执行。
- [A11 Calendar真实任务](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/task_evals/single/calendar/calendar.py)：25–228相关任务/参数/继承代码，未运行。
- [A12 SQLite validators](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/task_evals/common_validators/sqlite_validators.py)：21–401相关验证与生命周期代码，未运行。
- [A13 datetime_utils.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/utils/datetime_utils.py)：完整阅读，没有修改真实设备时钟。
- [A14 suite_utils.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/suite_utils.py)：实例生成、_run_task、_run_task_suite相关段落；仅_run_task异常分支mock执行，非完整聚合审计。
- [D1 Android命令行文档](https://developer.android.com/studio/run/emulator-commandline)：官方D1，读取Quick Boot选项与AVD用户数据/SD card说明；动态文档无固定版本。
- [X1 局部实验结果](experiments/androidworld-lifecycle/result.txt)：5项PASS，无设备运行。
