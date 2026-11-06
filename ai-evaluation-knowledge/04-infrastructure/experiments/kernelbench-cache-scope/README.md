# KernelBench cache cleanup：一个源码函数的最小复现

证据级别：**一个真实源码函数 D4，不是 KernelBench 端到端 D4，也不是 CUDA 实验。** 学习目标：L2 → L3。

## 固定来源

- Repo：ScalingIntelligence/KernelBench。
- Commit：`423217d9fda91e0c2d67e4a43bf62f96f6d104f1`。
- [scripts/eval_from_generations.py](https://github.com/ScalingIntelligence/KernelBench/blob/423217d9fda91e0c2d67e4a43bf62f96f6d104f1/scripts/eval_from_generations.py)，Git blob `6fac151ba282eeccbe0014c5e7b874fe1dbbce00`，36621 bytes。
- 原文件 SHA-256：`4e13c43dfcd7f3d7e6300fe0cf9774a4e3dc33bfb09dd6bcbabf5d22c4c3136b`。
- 研究中通过 GitHub connector 读取并保存原内容；运行前验证 Git blob 完全匹配。

## 如何运行

下载上述固定 commit 的原文件，保持原始字节。然后：

```sh
python3 run_cache_scope_test.py /path/to/eval_from_generations.py
```

脚本先验证整个文件的 Git blob，不匹配则拒绝执行。接着用 Python AST 只提取 `remove_cache_dir` 函数节点，保持其实现不变，在标准库 `os`、`shutil` namespace 中编译执行。不会执行上游模块顶层代码、装饰器、Modal image 构建、模型调用或 GPU worker。

脚本只传入自己新建的临时 fixture，不接受真实 cache 路径。不要把本实验改成对真实工作目录进行删除测试。

## 观察

fixture 包含目标 sample、同一 run 的 sibling、另一 run 和 cache 之外的对照文件。调用函数请求清理目标 sample 后：

- selected sample 删除；
- sibling sample 删除；
- 另一 run 删除；
- 整个 cache root 删除；
- cache 外文件保留。

输出：[result.json](result.json)。实际运行时间 `2026-11-06T02:54:16.458958+00:00`。

结果中的 PASS 表示**重现了当前过宽删除范围**，不是说该行为正确。函数创建了 per-sample 的 `problem_cache_dir` 变量，却把 `cache_dir` 传给 `shutil.rmtree`。它在上游批处理 timeout/error 路径中被调用。

## 不支持的结论

- 未证明任何已发布分数受影响，也未量化并发编译的实际损失。
- 未验证 GPU reset、CUDA context 清理或 cloud container 回收。
- 没有运行完整上游模块或 upstream test suite；AST 片段执行须明确披露。
- 没有修改或向上游发布任何内容。
