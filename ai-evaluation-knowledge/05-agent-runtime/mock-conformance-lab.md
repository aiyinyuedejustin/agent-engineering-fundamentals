# 本地机制实验：D4 的范围必须写在结果旁边

## 运行事实

- 代码：[mock_conformance_lab.py](mock_conformance_lab.py)，完全自写、仅 Python 标准库。
- 机器可读结果：[mock-conformance-results.json](mock-conformance-results.json)。
- 已执行时间：2026-11-06 02:53:38.540408 至 02:53:39.438283 UTC。
- 环境：Python 3.12.14，Linux x86_64；10 个实验各重复 3 次，共 30 项断言通过，耗时约 0.898 秒。
- 本次代码 SHA-256：`56a56799244c618a39459fc1a153a4307e4da8e9d11617e61784e1df38dcf3f8`。
- 未调用网络、模型 API、Docker daemon、云服务；未安装或运行任何 upstream agent/harness 包。临时文件在结束时清理，受控 subprocess 全部等待回收。

**深度界线：**这是 D4 自写机制实验，其中 7 个是明确的算法 mock，3 个使用真实本地 subprocess/bash。它不把 Harbor、Inspect、SWE-bench、mini-SWE-agent、OSWorld、BrowserGym 或任何 cloud provider 从 D3 升为 D4，也不产生 benchmark score。

## 结果

| 实验 | 类型 | 三次均观察到 | 可以支持的结论 |
|---|---|---|---|
| Turn budget | 算法 mock | 3 model calls 执行 6 actions | 两种预算单位不能直接对比 |
| Cost budget | 算法 mock | 阈值 1.0，累计 1.2 后停止 | 调用前检查不是绝不超支的硬上限 |
| Trace references | 算法 mock | 引用检查通过，但调用没有结果 | 引用合法不是记录完整 |
| Subtree metrics | 算法 mock | root total=100；全节点求和=150 | inclusive totals 不能跨层简单累加 |
| Cache identity | 算法 mock | 改 patch 但不改 key，返回旧 hash | 内容不在 cache identity 内就需要额外失效策略 |
| Checkpoint side effect | 算法 mock | 同一个外部动作记录了两次 | 恢复状态不保证外部 exactly-once |
| Observation truncation | 算法 mock | 12,023 字符缩成头尾 10,000 后，中部 marker 消失 | 模型可见文本不等于原始完整输出 |
| Wait cancellation | 真实本地 Python subprocess | 取消已启动的 process.wait waiter 后，worker 继续写 artifact；显式 terminate 后没有 artifact | 取消等待与终止计算是不同操作 |
| Shell persistence | 真实本地 bash | 文件保留；cd/export 不传到下一 shell | 持久文件系统与持久 shell 状态不同 |
| Cwd quoting | 真实本地 bash | 未引用含空格路径失败；shlex.quote 后成功 | shell 拼接需要正确引用路径 |

这些实验是有意构造的反例，不是“测试覆盖了整个框架”的证明。上游源码联系和版本边界见 [coding runtime](coding-runtime-source-trace.md)、[bridge/trajectory](inspect-bridge-and-trajectory.md) 与 [remote execution](remote-execution-contract.md)。

例如，本地 quoting 实验证明的是 bash 语义；Harbor 的 Daytona POSIX wrapper 恰好有该待测构造，但没有启动 Daytona，因此不能写成“已在 Daytona 复现”。同理，本地 waiter cancellation 不确定 Modal SDK 的远端取消行为。

## 如何复跑

在有 Python 3.10+、bash 的 Linux/macOS 环境，从本目录运行：

```sh
python mock_conformance_lab.py --output /tmp/agent-runtime-lab.json --repetitions 3
```

复跑应使用新的输出路径，保留已发布的原始结果。Windows 不在本实验已支持或已验证范围内。脚本包含超时和清理逻辑，仍建议先阅读源文件再运行。

## 下一步如何升级证据

1. **从逻辑到实现：**把相同输入放进固定版本的真实 adapter，保留 mock 结果为独立对照，而不是替换标签。
2. **从单组件到链路：**用一个真实任务跑 agent → artifact → grader → aggregate，核对每个阶段状态。
3. **从 happy path 到故障：**在远端写入完成但响应丢失、日志不完整、超时、cleanup failure 等位置注入故障。
4. **从一次到可重复：**固定 task/dataset/image/agent/adapter/model config，重复记录错误率、耗时、成本和分母，报告差异而不是只报告断言通过。

能力训练上，这份实验可作为 L1 到 L2 的练习材料；完成它不自动证明能工程化运行真实评测，也不等于 L3。
