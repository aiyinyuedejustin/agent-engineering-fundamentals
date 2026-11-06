# BrowserGym重置与调度：7个无网络局部实验

范围：D4仅覆盖已校验上游代码的局部函数/方法行为。学习目标L2。不是BrowserGym、WebArena、AgentLab、Ray或Docker端到端复现。

实际结果：[result.txt](result.txt)，2026-11-06T03:37:31.246231+00:00，7项PASS。无依赖安装、无网络请求、无socket、无子进程、无浏览器、无模型调用、无真实reset。

## 固定输入

把以下原始文件保存为右侧名字，保持原始字节和末尾换行。脚本先验证完整Git blob，不匹配就退出，不会自动下载。

| 固定源 | 本地名 | Git blob |
|---|---|---|
| [BrowserGym instance.py](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/webarena/src/browsergym/webarena/instance.py) | bg_instance.py | 1e6a9f98ce91aaaa435ee8a7ed6e31836dfe93cf |
| [BrowserGym metadata/utils.py](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/benchmark/metadata/utils.py) | bg_metadata_utils.py | f1fccd6f9c504b979f24ee66f1133ab0c3d0d7ae |
| [BrowserGym webarena.csv](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/benchmark/metadata/webarena.csv) | bg_webarena.csv | b263a22d41d9dfd917be4eed4ee1a127753129e5 |
| [AgentLab exp_utils.py](https://github.com/ServiceNow/AgentLab/blob/8488c564eea0525aaff5dea189bb03a9b529546e/src/agentlab/experiments/exp_utils.py) | agentlab_exp_utils.py | 27b909b2eefb9c8f5809384681c81da1c1d99b71 |

结果同时记录字节数、SHA-256和实际时间。源获取是此前只读研究步骤；实验本身不联网。

```sh
python3 run_contract_tests.py /path/to/reviewed-source-directory
```

## 执行了什么

- AST提取完整`WebArenaInstance`类定义，不执行模块imports或构造器。调用原样`full_reset`及`_check_is_reachable`方法；os.environ是私有字典，requests和time完全用本地对象替代。
- AST提取原样`extract_graph_children`、`extract_sparse_task_dependency_graph_from_subset`、`build_env_args_dependency_graphs`；真实CSV用Python标准库解析。
- AST提取AgentLab原样`add_dependencies`，参数是最小本地假对象。
- 只添加future annotations，避免依赖包类型注解求值；函数体不修改。没有导入BrowserGym、AgentLab、requests、Playwright、pandas或Ray。
- 上游reset测试文件已阅读作为交叉检查，本脚本是独立unittest用例，并未运行上游pytest套件。

## 七项断言

1. 未设置reset URL：返回False，但仍调用可达性检查。
2. 显式严格模式：在provider调用前抛RuntimeError。
3. 假控制端ready、假业务站HTTP500：仍返回True，说明可达性函数不检查状态码。
4. 假时间经过601秒：轮询在status返回后报超时；两个控制请求均未传timeout。
5. 实际官方CSV只选441和445：删去中间节点仍保留445依赖441。
6. 不支持并行种子的图构建函数：产生两个分离图，但不产生reset节点。
7. AgentLab依赖转换：存在依赖时拒绝重复任务名。

限制：fake HTTP不会证明网络超时的真实持续时间，返回500的模拟不会证明任何线上实例不健康。纯图结果不证明Ray调度顺序。未运行部署reset脚本，未改变任何容器、数据库、卷或外部服务。
