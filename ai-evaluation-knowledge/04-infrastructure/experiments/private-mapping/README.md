# 最小实验：真实 Linux private mapping 与 baseline 生命周期

证据级别：**底层机制 D4，非 Firecracker D4，非 benchmark 复现。** 学习目标：L2。

研究问题：私有 copy-on-write 映射能否隔离 clone 的写入？为什么 baseline backing file 仍不能随意修改或回收？

## 运行

只需 Python 标准库，不安装依赖，不需要 Docker、KVM、GPU、网络或提权。

```sh
python3 run_mapping_tests.py
```

脚本只写自己创建的临时目录。当前实测输出保存在 [result.txt](result.txt)。测试代码为本研究编写，不是上游 Firecracker 测试。

## 三个观察

1. 两个真实 `mmap.ACCESS_COPY` 映射共享一个 baseline 文件。改写 clone A，clone B 与磁盘文件仍保留原值。
2. 当前 Linux 主机上，clone 已私有化的第一页不随 backing file 改写；尚未私有化的第二页却能看到 backing file 的新内容。这揭示了“不写回原文件”不等于“不再依赖原文件”。
3. 已建立的映射可在文件被 unlink 后继续读取，但新的基于路径的打开失败。仅靠某个运行中进程仍能读到数据，不能证明未来恢复和故障重试仍可用。

第三点不能用来推翻 Firecracker 的文件保留契约：该实验只验证 Linux 进程映射，未覆盖 VMM 的其他访问、控制层、重启或恢复路径。第二点对文件变更的可见性也不是跨 OS 的通用保证。

## 对应一手来源与边界

- Firecracker v1.17.0 / commit `95f868c8e345b1cc8faccd1a3c910b4989dc3f58` 的 [snapshot support](https://github.com/firecracker-microvm/firecracker/blob/95f868c8e345b1cc8faccd1a3c910b4989dc3f58/docs/snapshotting/snapshot-support.md) 明确要求恢复 VM 的 memory backing file 保留且不可变。该文档是实验动机，本文未执行其 VM API。
- 实验没有测量启动速度、物理共享内存页数、VM 之间隔离强度或恶意 guest 逃逸。测试 PASS 不能据此证明 sandbox 安全。
- 模拟数据为固定字母，无凭据、用户数据或外部任务内容。
