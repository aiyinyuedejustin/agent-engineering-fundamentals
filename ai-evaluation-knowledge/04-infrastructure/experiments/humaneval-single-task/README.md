# HumanEval 单题执行尝试：在 IPC 阶段被环境拒绝

**结果是 BLOCKED，不是 PASS，也不是模型答错。** 原任务测试与候选代码都没有执行。不能将本次尝试写成 HumanEval task-level D4 成功复现。

## 原定范围

固定 `openai/human-eval` commit `b9453e8f1865df0a0057a1383767caa400acfbcf`，研究日期 2026-11-06。该 repository README 当前明确标为 deprecated and unmaintained。

选用官方 `HumanEval/1`，功能为分离括号组。完整 prompt、4个 assert 与原执行模块均已阅读。计划只运行4个本地手写控制：正确、错误、语法错误、可被短 timeout 中断的纯循环。不调用模型，不执行不受检查的任意生成代码，不安装依赖。

## 固定输入与来源

| 文件 | Git blob | 字节数 | SHA-256 |
|---|---|---:|---|
| human_eval/execution.py | bcfd7c5d452e2dcbb1ea89317c47b9e0f1c2c4ca | 6582 | 79901c6f5b59701c465b164aed290fa53abc35abc80a5378fc10f4dac1f9a84c |
| human_eval/data.py | ed497942668840b4d6d010bfab2d1798bc81eff6 | 1529 | e1351f0ded89b072490180ce94ce33b88bac4e38b26f08eb26ab0714586585ab |
| data/HumanEval.jsonl.gz | 998d25196e17af24daf9b6cb3a975fe752528e46 | 44877 | b796127e635a67f93fb35c04f4cb03cf06f38c8072ee7cee8833d7bee06979ef |

固定链接：[execution.py](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/human_eval/execution.py)、[data.py](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/human_eval/data.py)、[dataset](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/data/HumanEval.jsonl.gz)、[README](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/README.md)、[MIT license](https://github.com/openai/human-eval/blob/b9453e8f1865df0a0057a1383767caa400acfbcf/LICENSE)。本目录不复制完整数据集或上游模块。

文本代码通过 GitHub source 接口读取。二进制 gzip 不受该文本接口支持，后从上述固定 commit 的官方 raw 文件下载并校验 Git blob。获取数据成功不代表运行成功。

## 真实发生的调用链

```text
hash verification succeeds
  → load full unchanged data.py and execution.py
  → read_problems loads official dataset and selects HumanEval/1
  → check_correctness starts first control
  → multiprocessing.Manager starts IPC server
  → SocketListener calls socket.socket
  → PermissionError: [Errno 1] Operation not permitted
  → parent receives EOFError while waiting for Manager server address
```

当前 Python multiprocessing 默认 socket family 为 AF_UNIX，随后通过只读属性检查确认；没有再次尝试创建 socket。没有确定产生 EPERM 的具体底层安全机制，不臆测为某个特定 seccomp 规则。

`check_correctness()` 在创建候选执行进程之前先创建 Manager，因此失败发生在 `unsafe_execute()` 和官方 assertions 之前。结果见 [result.json](result.json)。失败命令的精确 UTC 开始时刻没有输出，不补造时间。

## 已采取的限制与未提供的保证

runner 使用自己的临时目录、最小子进程 environment、Python `-I`、12秒外层 watchdog，以及子进程 CPU/address-space/file-size/file-descriptor/core-dump 限额。只允许匹配固定 hash 的上游代码和硬编码的手写控制。

这些措施**不是可执行任意恶意代码的安全 sandbox**。上游 reliability_guard 自己也明确如此警告。本次不为绕过限制而修改 harness 的 IPC、不申请放宽运行环境、不在其他环境重试；保留 blocked 结果。

## 代码保留的用途

`run_single_task.py` 保存原计划以供将来在已获准、具备对应能力的专用环境中审查后重现。输入布局：

```text
source_root/
  execution.py
  data.py
  data/HumanEval.jsonl.gz
```

预期命令为 `python3 run_single_task.py source_root`。此命令在本研究环境不能成功，不能将它写成已通过的快速开始步骤。

## 两个值得保留的发现

1. “离线 CPU 任务”仍可能依赖本地 socket IPC。环境能力检查必须涵盖 harness，而不只检查 candidate 能否使用 Python。
2. README 仍说执行行被注释，但这个固定 `execution.py` 中的 `exec(check_program, exec_globals)` 实际已启用。运行前必须检查真实源码，不能仅相信历史安全提示的状态描述。

这两点是限制与版本审计结果，不是对全套 HumanEval 分数或安全性的验证。
