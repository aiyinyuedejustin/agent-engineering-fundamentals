# 最小实验：运行上游政策代码，模拟 provider 控制流程

等级：**局部 D4 / L2–L3**。不是 Harbor/OSWorld benchmark 复现，不是 VM、Docker、Kubernetes 或安全边界的实机测试。

执行时间：2026-11-06T02:37:56Z 首次 byte-identical 源码测试；最终脚本再次运行时间见 `result.txt`。Python 3.12.14，无第三方依赖安装，无模型调用、无 Internet 请求、无云开销。

## 实验做了什么

直接加载两个已审阅的上游 Python 文件。运行前验证 Git blob SHA1 与固定版本一致。Harbor error_policy 使用真实标准库执行；OSWorld provider 的 Docker、HTTP、进程列表、锁、父类和 sleep 全部替换为内存测试替身。

15 个断言覆盖：

- agent timeout、OOM、rate limit、verifier failure、未知异常的 retry/grade/reward_valid；
- 错误映射不可变，以及精确名称查找不自动继承异常分类；
- KVM 存在/不存在时 Docker run 参数；
- 固定 runtime digest、只读磁盘挂载、端口、NET_ADMIN；
- guest resource 通过环境变量传递，而不是在该调用里设置外层 Docker mem_limit/nano_cpus；
- revert 停止并删除容器；save_state 不支持；启动失败尝试清理；
- readiness 判定读取 HTTP status 200，未在这个函数中验证截图正文。

这些测试证明**该固定代码在这些模拟输入下作出这些控制决策**。不证明 Docker 接受参数、guest 能启动、参数实际生效、清理必然成功、网络隔离成立或评分公平。

## 固定源文件

1. Harbor commit `26f95e0ebd8c77011bbf4656f5c98af66ce55848`：
   https://raw.githubusercontent.com/harbor-framework/harbor/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/models/trial/error_policy.py
   - Git blob SHA1: `1e35a5801ccad8e50d9c7defcfe64bd137bb5334`
   - SHA256: `5026b5478db4ac8d13f4707a08614ba6459a55f553094c403a46683a3f1fa5d3`

2. OSWorld V2.1 commit `3d778a3c9a34a079316f70df023b166700445792`：
   https://raw.githubusercontent.com/xlang-ai/OSWorld-V2/3d778a3c9a34a079316f70df023b166700445792/desktop_env/providers/docker/provider.py
   - Git blob SHA1: `03dc71041ac79f167f077b0f03c7ea62f85e4cf1`
   - SHA256: `88a60a91ac0d29bb2ab1b6ed81e20be7e7196c170acd45c133451b04dd79cae6`

源文件通过 GitHub connector 读取并保存在本地临时目录，未打包进本知识库。复制工具最初附加了一个换行；校验发现 mismatch 后移除了唯一多出的末尾换行，并确认最终 Git blob 完全匹配上游后重新运行。`result.txt` 只保留匹配后结果，不把初次格式变更副本算作精确源码执行。

## 复现

先从上面固定 URL 保存两个文件，不要使用 main/latest。审阅代码与脚本，然后运行：

```bash
python run_contract_tests.py harbor_error_policy.py osworld_docker_provider.py
```

脚本会拒绝 Git blob 不匹配的输入。需要 Python 3.11+（上游使用 StrEnum），本次在 3.12.14 实测。

## 下一步实机验证

在得到支持的 Docker/KVM 环境后，另做 VM boot、任务 setup、错误注入、reset 独立性、外部服务 reset、实际资源约束、端口可达性和 orphan cleanup。不要把这里的 mocked tests 当成那些实验的替代品。
