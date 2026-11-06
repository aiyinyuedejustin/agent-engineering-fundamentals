# AndroidWorld生命周期的5个局部mock实验

**D4范围仅限原样上游函数/方法的本地控制流。** 学习目标L2。没有Android模拟器、ADB、网络、socket、子进程、模型调用、权限修改或设备数据操作。测试记录的restorecon/chmod命令只是Python列表。

固定上游commit：`55ddaf5edc6f6c25673aed343907d5b9dca66f84`。

## 输入与运行

先保存已审阅的下列固定文件原始字节；脚本验证完整Git blob，不自动下载、安装或导入Android依赖。

| 源文件 | 本地名 | Git blob |
|---|---|---|
| [android_world_controller.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/env/android_world_controller.py) | controller.py | 3ce79c02e62208c7e3271826c1621bd52f9b43a8 |
| [task_eval.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/task_evals/task_eval.py) | task_eval.py | bce5a4e19f90be5754d2ee401cf3223054d6e81b |
| [app_snapshot.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/utils/app_snapshot.py) | app_snapshot.py | e2d23cab729c5352c28b5080013b63e855b72e25 |
| [suite_utils.py](https://github.com/google-research/android_world/blob/55ddaf5edc6f6c25673aed343907d5b9dca66f84/android_world/suite_utils.py) | suite_utils.py | 2c72a418f773779d60799ef4eebae0eff192c635 |

```sh
python3 run_contract_tests.py /path/to/reviewed-source-directory
```

使用Python标准库。实际环境Python3.12；本次无任何依赖安装。结果包含各源文件字节数和SHA-256。

## 方法

AST提取未修改的get_a11y_tree、TaskEval._initialize_apps/initialize_task、restore_snapshot、_run_task函数体，不执行上游模块imports。类方法提取后绑定最小假self；添加future annotations以避开外部类型注解求值。

设备、ADB、文件操作、clock、日志辅助和失败结果构造都用本地mock/stub替代。没有尝试突破此前HumanEval运行环境的IPC限制，也没有再次运行HumanEval。

## 实测

[result.txt](result.txt)记录2026-11-06T03:45:27.036232+00:00的5项PASS：

1. 假设备开启airplane mode时，观测函数请求启用网络，然后返回forest。
2. 基础TaskEval应用snapshot失败被捕获，初始化仍完成。
3. 重复initialize调用在报already called之前已触发时间/应用重置。
4. restore清目录失败后仍调用复制并构造权限恢复命令。
5. episode抛异常后返回失败结果，teardown未调用。

输出中的ValueError traceback、缺snapshot warning和DeprecationWarning都是预期故障注入/日志，不代表有真实设备失败或测试失败。

这些实验不能证明设备网络实际被打开、快照是否物理完整、真实应用权限变化或后续任务污染。真实Calendar任务还有特定清表逻辑，本实验没有模拟或执行整条Calendar任务继承/数据库链。
