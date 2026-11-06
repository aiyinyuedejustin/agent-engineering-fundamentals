# BrowserGym / AgentLab：重置、就绪和依赖调度是三个合同

状态：本篇证据子集已闭合。阅读日期2026-11-06。学习目标L2→L3。

证据深度：BrowserGym及AgentLab相关调用链D3；真实WebArena元数据D2；7个本地、无网络的原样AST分支实验D4。未运行浏览器、Ray、Docker或任何后端重置，未测量分数变化。D4不覆盖真实服务健康、数据库回滚或并发隔离。

固定版本：

- BrowserGym：`27a90ce815098f43414e93491e06907af468e45b`。
- AgentLab：`8488c564eea0525aaff5dea189bb03a9b529546e`。
- BrowserGym README链接的**非官方**部署脚本gasse/webarena-setup：`8d0e0a20d50e4a8c02d1520195182e19fc3c080f`。不能把它称为原版WebArena的强制部署方案。

前一篇[原版WebArena](09-webarena-browser-reset-is-not-backend-reset.md)讨论浏览器重建与服务状态不同。本篇追查新版集成增加了什么保证，以及哪些保证仍需操作者落实。浏览器动作/校验细节另见[运行时源码追踪](../05-agent-runtime/computer-use-source-traces.md)。

## 1. 三个问题不可互相替代

| 合同 | 应回答的问题 | 代码中的实现点 |
|---|---|---|
| 重置 | 哪些状态回到哪个版本的初始值？ | `WebArenaInstance.full_reset`、远程reset服务、容器与卷 |
| 就绪 | 服务可连、HTTP成功、可登录、任务语义正确，检查到哪一级？ | reset `/status`、`_check_is_reachable`、`massage_tasks` |
| 调度 | 哪些任务可以共享后端并行？重复种子、模型、失败重试如何隔开？ | CSV依赖图、Benchmark图转换、AgentLab消费者/Ray |

这些合同可以分别失败。例如控制端返回ready，而业务端返回500；调度图正确，而整个批次从未经确认的旧数据库开始；容器成功重建，而命名卷仍保持上一次状态。

## 2. 实际调用链：每次study尝试准备后端，不等于每个任务重置

在固定AgentLab版本，`Study.run()`默认最多3次尝试，每次调用`Study._run()`。后者先`benchmark.prepare_backends()`，再`run_experiments()`；不只在第一次尝试准备后端。[B1]

BrowserGym的`Benchmark.prepare_backends()`逐项调用`prepare_backend`。WebArena分支创建实例，调用`full_reset()`，按布尔值记录DONE/SKIPPED，然后执行预热任务；外层随后可记录backend ready。[B2][B3]

```text
Study.run 的一次尝试
  → Benchmark.prepare_backends
    → WebArenaInstance.full_reset
      → 可选的 GET /reset
      → 轮询 GET /status
      → 检查每个网站是否可达
    → 预热任务：reset、noop、noop、close
  → run_experiments
    → 根据选择的执行后端处理任务列表
  → 保存结果、找未完成项，必要时进入下一次尝试
```

WebArena具体任务的`setup`负责选择配置、生成临时配置、登录、地理位置与起始页面，`teardown`为空；它不是上图的整站重置。[B4] 因此不能把“每个episode调用env.reset”写成“每个episode获得独立新数据库”。

**重试推论，尚未端到端验证**：该调用链允许下一次尝试再次重置整个后端，而结果层只重跑未完成/错误的部分。是否适合某个有状态任务集合，需要审查依赖是否只是避免干扰的排序，还是确实需要前一任务的状态。不能从函数名自动判断，也不能据此断言所有重试分数错误。[B1]

## 3. full_reset默认是可跳过的

`full_reset(skip_if_not_set=True)`读取`WA_FULL_RESET`。未设置或为空时：记录错误和warning，设置`was_reset=False`，随后仍执行网站可达性检查。只有显式传`skip_if_not_set=False`才立即抛错。`prepare_backend`没有传严格模式。[B3][B5]

这是一种兼容人工重置的设计，不是证明后端脏了。严格可复现实验需区分：

- 自动重置执行并确认；
- 人工重置，有操作者、时间与初始状态证据；
- 自动重置跳过，初始状态未知。

不要把三者都记成一个`prepared=true`。

当reset URL存在，控制端200表示启动，418表示已有reset正在进行，两种情况都会继续等待。轮询status要求200且正文精确等于`Ready for duty!`，否则继续等或报错。[B5]

**超时边界**：reset/status的`requests.get`都没有显式`timeout`；10分钟计时在reset请求返回后启动，并且只有status请求返回以后才检查。因此它是轮询逻辑的超时，不是包含每次阻塞网络调用的硬总截止时间。实验用假时钟证明了检查位置，没有真的挂住网络请求。[B5][X1]

## 4. “可达”与“业务健康”不是同一件事

`_check_is_reachable`循环网站，调用带timeout的`requests.get`，只把连接异常和超时转换为错误。它没有`raise_for_status`或其他HTTP状态断言。[B5]

本地mock让控制端返回ready、业务站返回500，原样方法仍返回`True`。这证明的是**代码的状态码判断范围**，不是某个线上站点确实500，也不是已经完成真实数据库reset。[X1]

后续`massage_tasks`提供更深预热：子进程内调用任务reset和两次noop，后者触发task validation。每个任务默认可重试一次，最终失败只warning并跳过，准备过程不因此整体fail closed。[B3] 不能把它称为完整验收测试。

预热也并非必然“零成本探活”：它运行真实task setup/validation；WebArena集成README提示某些评估会调用GPT-4。这里**未执行**任何预热、浏览器或模型调用。规划时应检查具体预热任务的验证路径与外部账单，不把它当作只读TCP检测。[B3][B6]

## 5. 追到重置服务：容器被重建，命名卷不一定被重置

BrowserGym README推荐的可选非官方脚本使用一个HTTP控制服务：原子创建`reset.lock`防止重复启动，在线程里执行reset.sh，成功/失败写状态文件，随后释放锁。它会用脚本退出码决定status，不验证业务数据库的内容摘要。[S1]

reset.sh依次调用删除容器、创建容器、启动容器、打补丁四个脚本。启动脚本包含固定60秒等待；补丁脚本重新配置应用、刷新部分缓存、运行数据库migration等。[S2]

尤其要注意地图服务：

- 删除脚本是`docker stop`和`docker remove`，没有移除命名卷；
- 地图Compose显式挂载`db-data`、`web-storage`、`web-tmp`；注释说明这些数据跨运行保留；
- 创建脚本重新使用同一个Compose项目，补丁脚本执行migration，并非恢复数据库快照。[S2][S3]

Docker官方文档确认卷生命周期独立于容器，容器删除不会自动删除卷。[D1] 因而在这个固定脚本组合下，不能仅凭“所有容器删掉再建”宣称地图数据库已恢复基线。**这不是实测地图任务受污染的结论**：某些任务可能只读；实际受影响状态和评分需专门实验。

此外地图配置默认指向外部tile、geocoding和routing服务。自托管WebArena并不自动意味着所有依赖都离线、冻结或完全受本机reset控制。[S2]

安全与控制面备注：所读reset服务绑定所有地址，处理GET reset/status的代码中没有应用层认证；外部防火墙/代理可能提供保护，本次没有查看任何实际部署。应把reset服务作为有破坏性的控制面隔离，不能因任务网站允许访问就默认也允许代理访问它。[S1] 未探测任何远程端口、未触发reset。

## 6. 元数据已经表达冲突，但执行器必须真正消费它

BrowserGym WebArena CSV为真实任务提供`depends_on`。前文讨论的同一GitLab文件修改任务441→442→443→444→445，在这里有明确顺序链；不能拿原版runner的局限去断言当前集成没有调度保护。[B7]

`extract_sparse_task_dependency_graph_from_subset`删除不在子集的节点时，会连接其父子节点。只选择441和445，仍得到445依赖441，而不是因为中间任务被过滤就丢失约束。本地原样函数对完整官方CSV验证了这一点。[B8][X1]

BrowserGym的`build_env_args_dependency_graphs`在`supports_parallel_seeds=False`时，把同一任务的不同种子分到不同图；docstring要求图间顺序执行，通常插入整站reset。**返回图本身不执行reset，也不分配独占后端**。[B8]

固定AgentLab消费的是另一条接口：`Study.agents_on_benchmark`调用`add_dependencies(..., benchmark.dependency_graph_over_tasks())`，不是自动消费上面的分种子图。其`add_dependencies`在存在任务依赖时拒绝重复任务名，所以“BrowserGym支持分图”不等于“这个AgentLab路径自动支持多种子重复”。本地实际调用复现了这个ValueError。[B1][A1][X1]

执行后端也不同：

- Ray代码递归创建依赖任务，把上游ObjectRef传入下游remote任务，形成执行依赖；
- joblib分支直接并行提交剩余任务，没有读取`depends_on`；
- sequential分支按输入列表顺序执行，没有在该函数里做拓扑排序；正常列表顺序与任意重排不能混为一谈。

该文件自身文档也警告WebArena图依赖应使用Ray或sequential。开头另有旧的dask说明，而dask实现已注释；以具体分支源码为准。[A2][A3] 本次没有运行Ray或joblib调度器，因此不宣称验证其分布式行为。

## 7. 最小实验与工程验收

[实验目录](experiments/browsergym-reset-contract/README.md)提供脚本、四个输入的完整Git blob校验及实际结果。2026-11-06T03:37:31.246231+00:00运行，7项PASS：

1. 缺reset URL时返回False，但仍做可达性检查；
2. 严格模式在调用provider前抛错；
3. ready控制协议加业务500，方法仍返回True；
4.轮询截止检查在status返回以后，两个控制请求没有timeout参数；
5. 真实CSV子集保留441→445传递顺序；
6. 非并行种子产生独立图，没有生成reset动作；
7. AgentLab实际依赖转换函数拒绝重复任务名。

要把这套流程提升到真实平台验收，至少补齐：

- 独占实例租约：agent、任务批次、重试与reset的所有者；避免别人运行时整体reset。
- 状态清单：容器可写层、命名卷、绑定目录、数据库、远程服务、浏览器会话分别如何重置。
- 语义探针：登录、已知记录、可写回滚测试、基线摘要；不能只靠HTTP连通。
- 全路径截止：排队、reset HTTP、轮询、warm-up、任务、清理分别计时，并有真正的总上限。
- 调度证据：实际依赖图、执行后端、重复种子分组、开始结束时间和reset generation。
- 阻塞策略：reset被跳过、预热失败、后端健康不符时，明确标成环境无效，而非静默纳入模型失败率。

以上是工程建议，不是项目已经实现的功能。涉及真实reset或数据删除时只操作明确归属的测试实例，不在共享服务上试运行。

## 来源与读取范围

- [B1 AgentLab study.py](https://github.com/ServiceNow/AgentLab/blob/8488c564eea0525aaff5dea189bb03a9b529546e/src/agentlab/experiments/study.py)：读取make_study、run/_run、实验生成、SequentialStudies/worker初始化相关区段。
- [B2 Benchmark](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/benchmark/base.py)：完整阅读，prepare_backends及依赖图接口。
- [B3 prepare_backend / massage](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/benchmark/utils.py)：完整阅读。
- [B4 WebArena task](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/webarena/src/browsergym/webarena/task.py)：setup/teardown/validate已读，未执行。
- [B5 WebArena instance](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/webarena/src/browsergym/webarena/instance.py)：完整阅读，reset/可达性方法mock执行。
- [B6 集成README](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/webarena/README.md)：完整阅读，明确unofficial、可选reset、评估成本。
- [B7 WebArena元数据](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/benchmark/metadata/webarena.csv)：完整文件哈希校验和CSV解析，检查选定链，非所有任务语义审计。
- [B8 元数据图工具](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/benchmark/metadata/utils.py)：完整阅读，所述纯函数实际执行。
- [A1 AgentLab exp_utils](https://github.com/ServiceNow/AgentLab/blob/8488c564eea0525aaff5dea189bb03a9b529546e/src/agentlab/experiments/exp_utils.py)：完整阅读，仅add_dependencies AST执行。
- [A2 launch_exp](https://github.com/ServiceNow/AgentLab/blob/8488c564eea0525aaff5dea189bb03a9b529546e/src/agentlab/experiments/launch_exp.py)：读取run_experiments及重试接口相关代码。
- [A3 Ray图执行器](https://github.com/ServiceNow/AgentLab/blob/8488c564eea0525aaff5dea189bb03a9b529546e/src/agentlab/experiments/graph_execution_ray.py)：完整阅读，未运行。
- [S1 reset server](https://github.com/gasse/webarena-setup/blob/8d0e0a20d50e4a8c02d1520195182e19fc3c080f/webarena/reset_server/server.py)：完整阅读，未启动。
- [S2 reset脚本链](https://github.com/gasse/webarena-setup/tree/8d0e0a20d50e4a8c02d1520195182e19fc3c080f/webarena)：完整阅读reset_server/reset.sh及02、03、04、05、07脚本；没有执行、没有读取实际用户实例。
- [S3 地图Compose](https://github.com/gasse/webarena-setup/blob/8d0e0a20d50e4a8c02d1520195182e19fc3c080f/webarena/openstreetmap-templates/docker-compose.yml)：完整阅读，命名卷与绑定目录。
- [D1 Docker卷生命周期](https://docs.docker.com/engine/storage/volumes/#a-volumes-lifecycle)：官方文档D1，2026-11-06读取，动态页没有固定版本。
- [X1 实际实验结果](experiments/browsergym-reset-contract/result.txt)：原样局部逻辑、全部外部交互mock，无网络/服务重置。
