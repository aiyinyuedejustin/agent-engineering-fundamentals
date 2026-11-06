# Firecracker-containerd jailer selector：未执行成功的局部实验计划

**状态：BLOCKED，编译前工具链检查失败。0个Go测试运行。没有本实验的D4成功结论。** 学习目标L2；源级结论在主文标D3。

固定输入：[runtime/jailer.go](https://github.com/firecracker-microvm/firecracker-containerd/blob/be68640a5d2237f5b427c37c1f5809ec154126c5/runtime/jailer.go)，commit `be68640a5d2237f5b427c37c1f5809ec154126c5`，4000 bytes，Git blob `19af4ad2dce6eb62f9cf64be06a475de09be5502`，SHA-256 `aa2440b79328203728fd1f72d438e841581e3c5a581edf1701e6092661b1b0da`。

## 计划测试的范围

run_tests.py要求预先保存审阅过的上游原始文件，验证完整Git blob后，将其**原样**放入临时Go module。所有外部依赖、noop/runc工厂均为本地最小stub，拟测试：

1. nil request或nil JailerConfig选择noop，且不建bundle；
2. 显式配置中UID/GID为0，在文件设置前被拒绝；
3. 显式非零身份选择runc工厂，并转交资源/暴露策略参数。

即使未来通过，也只证明selector逻辑和参数传递，不证明runc隔离、Firecracker执行、cgroup限制或安全性。os.MkdirAll只会操作测试自己创建的临时目录。生成的mock module声明Go1.19是局部fixture要求，不代表完整上游项目的编译要求；上游go.mod要求Go1.25.0。

## 实际发生的事

2026-11-06T03:53:21.790969+00:00，已验证源文件哈希，并准备了临时mock fixture。PATH解析到`/usr/bin/go`，但`go version`返回非零：

```text
Go: Unknown option: version
```

因此没有验证出可用Go工具链，编译和测试均未开始。未安装工具链、未下载依赖、未调用runc/KVM/Firecracker、未进行namespace或权限操作。这是工具链前提失败，不是权限拒绝，也不是上游selector测试失败。

- [result.txt](result.txt)：原始失败输出，保留当时的Python traceback。
- [result.json](result.json)：明确的机器可读状态和0测试计数。
- [run_tests.py](run_tests.py)：后来增加了清楚的Go版本前置检查，未重跑；Go fixture本身未经编译，不能当作已验证quickstart。

未来在已有Go工具链、获准的本地环境中可审阅后执行：

```sh
python3 run_tests.py /path/to/reviewed/jailer.go
```

runner设置GOPROXY=off、GOSUMDB=off、GOTOOLCHAIN=local、CGO_ENABLED=0；依赖只指向随脚本生成的本地stub。它不会自动解决工具链问题。真实VMM实验需单独规划，不能通过删除限制或改用真实host操作来“补出”本次成功。
