# 原创逻辑崩溃／重启恢复实验

本目录配套[第17卷：停在write、rename、commit之间](../../02-Illustrated-Deep-Dive-Book/17-State-Recovery-And-Updates/README.md#小实验writerenamecommit-之间停下重启后该读到什么)。

**范围：**只验证本模型在确定文件操作阶段之间停止、再启动后的决策。不是硬件掉电测试、fsync 耐久性认证、任意 I/O 内部崩溃证明或 Claude 实机运行证明。SET-07 的 private-file writer 与 SET-08 的 store/journal 保持为两条产品路线；本模型不是将它们拼接后的产品实现。

## 直接运行

要求 Python 3.10+，仅标准库；本次实测环境见 run-records.json，未验证其他操作系统。

从完整仓库根目录运行：

```sh
cd books/claude-app/04-Extracted-Core-Code-And-Scripts/crash-cut-recovery
python3 -B -m unittest discover -s . -p 'test_*.py' -v
python3 -B lab.py > /tmp/crash-cut-records.json
```

- `protocol.py`：原创协议、精确暂停点、严格 JSON/摘要校验、恢复逻辑。
- `lab.py`：父进程创建和清理自己的 TemporaryDirectory；创建子进程、等待阶段握手后通过其 handle 终止；收集机器记录。
- `test_crash_cuts.py`：独立黑盒测试；预期字节、摘要、操作与版本不调用协议内部的写入、恢复、校验或序列化函数。
- `run-records.json`：本次实际运行的 16 个场景；每个包含停止码、每份合成文件的大小/SHA-256/可解析内容、第一次及后续恢复。也记录最终源码摘要。
- `test_independent_audit.py`：17个独立反例方法；与18个实现测试合计35方法。独立复核覆盖完整操作身份、重复恢复以及进程/目录清理范围。

入口不接收用户目录，不读取真实配置，不访问网络。实验字段只映射到四个固定文件名，journal 不能指定路径。子进程需验证父进程生成的随机目录标记，拒绝 fixture 符号链接；这仅防止误用，不是对恶意并发文件系统操作的安全证明。不要绕过 runner 调用私有 worker。

## 本模型的文件与合同

合成旧目标是 `{"revision":7,"label":"old"}`，新目标是 r8/new。所有内容使用确定性 JSON 编码。

| 文件 | 责任 |
|---|---|
| settings.json | 当前正式路径下的目标 |
| candidate.json | 准备中的新字节 |
| intent.json | 固定 schema、resource、operationId、baseHash、nextHash、nextRevision |
| receipt.json | 此操作匹配的 operationId、nextHash、revision，以及 schema/resource |

只有完整合法 intent 才授权恢复继续。提交完成要求：target 对应 nextHash 和 revision，receipt 对应同一操作，intent 已退休。receipt 是合成的本地应用记账；它不证明外部副作用“恰好一次”，也不证明可抗断电。

恢复入口从调用上下文取得本实验固定的预期操作：op-r7-r8，及 r7→r8 对应的完整意图字段。journal 必须与预期一致；receipt 必须与该预期生成的完整回执一致，即使同 operationId 也不能改绑其他 payload。无 intent 时，孤儿 candidate 保留但不安装。无 intent、有合法、对应预期操作且与 target 匹配的 receipt 时报告 already-committed。实际多操作系统须另行提供可信的操作上下文，本实验不实现日志检索或调度。畸形 journal/receipt 保留并拒绝，实验没有设计自动人工处置替代品或任意损坏的自愈机制。

## 八个精确切点

| 切点 | 子进程停止位置 | target | 首次恢复动作 | 首次恢复的替换／回执写入次数 |
|---|---|---|---|---|
| C0 | 写 candidate 前 | r7 | no-intent | 0 / 0 |
| C1 | candidate 固定前半段写入并关闭 | r7 | no-intent | 0 / 0 |
| C2 | candidate 写完、关闭并读回核对 | r7 | no-intent | 0 / 0 |
| C3 | intent 固定前半段写入并关闭 | r7 | invalid-journal | 0 / 0 |
| C4 | 完整 intent 写完，尚未 replace | r7 | installed-candidate | 1 / 1 |
| C5 | replace 已完成，尚无 receipt | r8 | finalized-installed | 0 / 1 |
| C6 | receipt 写完，尚未退休 intent | r8 | finalized-installed | 0 / 0 |
| C7 | commitComplete，尚未将结果返回父进程 | r8 | already-committed | 0 / 0 |

C7 特别说明：应用状态已经完成，调用方却可能没有收到返回值。恢复器根据磁盘上的本模型事实确认结果；不能把“未收到响应”直接等同于“没有执行”。

C1/C3 是**主动制造的合成 torn file**，不是本次观察到文件系统自行发生半写。阶段握手后子进程阻塞；父进程不靠定时 sleep 猜切点。在本次 Linux 运行中，终止子进程返回码是 -15；代码不把该数值写成跨平台标准。超时清理也只针对自己持有的 Popen handle，从不按名称/PID 搜索其他进程。

## 对抗与重复恢复验收

1. 在 C4 后由 harness 把自己目录中的 target 改为 r9。恢复返回 base-conflict，r9 字节和文件状态不变；再次恢复仍拒绝。
2. 保留合法 journal，破坏候选字节。恢复返回 invalid-material，不触碰 r7。附加测试把 journal 的摘要改为吻合其他 payload，确认它仍与调用方预期操作不符，返回 operation-conflict。
3. 完整候选但缺失／坏 schema／重复键的 journal 不能继续；未知字段和路径字段也拒绝。
4. 已安装后只有同 operationId、nextHash、revision 的回执才能继续清理。错误回执、截断回执、bool 伪装的整数类型均拒绝。
5. 在恢复 replace 后、receipt 后、intent 退休后分别停止，再启动。不会重复替换 target；正常完成后的再恢复不改 target 或 receipt。另有一个场景连续经历 R_RENAME 与 R_RECEIPT 两次中断。
6. 合成 rename 拒绝时保留旧 target、candidate、intent，不报告提交完成，不作直接原地写回退；解除注入后的新进程可以恢复。

测试除核对结果字段，还比较真实合成文件的字节、摘要、inode 与 mtime，验证拒绝和幂等路径未重写它们。计数只统计相应子进程内显式操作，不是跨崩溃的持久总账；原进程停止前的动作另由切点与文件快照记录。

## 没有验证的内容

- 没有 OS 崩溃、硬件断电、缓存丢失、文件系统／挂载／设备故障注入。
- 没有 fsync，也没有文件数据、目录项、journal、receipt 的持久顺序证明。
- 没有多 writer 竞争、跨文件系统 rename、网络文件系统或全平台认证。
- 没有任意指令切点的穷尽模型检查；特别是 receipt 写入内部没有做进程切断实验。手工损坏 receipt 的测试仅验证保守拒绝。
- 没有 direct-write fallback；不能据此评价 SET-07 该分支的运行结果。
- 没有运行、挂钩或修改 Claude；没有复用目标算法、私有格式或真实数据。

Linux 的 [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html) 描述替换的可见性；[fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html) 指出文件同步不自动完成包含目录项的同步。二者是解释边界的外部资料，不是本实验的执行证据。加入一次 fsync 也不能把本实验升级为通用断电安全证明。
