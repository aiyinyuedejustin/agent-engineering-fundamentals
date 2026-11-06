# 本地传输故障实验：响应丢失、重复动作、EOF 与 PTY

研究日期：2026-11-06 UTC。**D4 仅限本页自写实验，不是任何上游 agent、SDK、云平台或 benchmark 的复现。**

这组实验补充 [remote execution contract](remote-execution-contract.md) 与 [OpenHands remote trace](openhands-state-and-remote-trace.md)：接口返回失败、服务端是否执行、日志是否完整，是三个不同问题。阅读代码可以识别边界，本地故障注入让这些区别变成可观察的结果。

## 1. 实验对象与安全边界

- [transport_fault_lab.py](transport_fault_lab.py)：完全自写，仅 Python 标准库。
- [transport-fault-results.json](transport-fault-results.json)：实际运行输出，逐轮保留输入情形和观测。
- 六个测试使用自写 JSON-line TCP 服务，只监听 127.0.0.1 的临时端口。它不是 HTTP、ACP、ASP 或任何 provider API 的实现。
- 三个测试使用实际本地 pipe、明确配置的 PTY、UTF-8 增量解码器。
- 无外网请求、模型调用、凭据、安装、Docker 或云资源。所有自建连接、tasks、子进程与 FD 在结束前关闭或等待。
- 服务端去重表在内存中；没有持久化、崩溃恢复、跨机器复制或租户身份认证。不能以此声称实现了生产级 exactly-once。

运行记录：2026-11-06 03:29:51.096131–03:29:51.637155 UTC；Python 3.12.14，Linux x86_64。9 个情形重复 3 轮，27 个断言全部通过。总耗时 0.541012 秒，仅作运行记录，不是性能基准。

脚本 SHA-256：`271c5ff4cfabc098675c15acb6ec914d904f43b778c7309e46a6daf8a02897bb`。

复跑到新的输出文件，避免覆盖本轮证据：

```bash
python 05-agent-runtime/transport_fault_lab.py --output /tmp/transport-fault-rerun.json --repetitions 3
```

## 2. 六个服务端实验

| 情形 | 实际观测 | 只支持什么结论 |
|---|---|---|
| 操作已提交，但服务端丢弃响应；客户端换新 ID 重试 | 客户端首次只看见 EOF；ledger 中有 2 次提交 | 没有响应不证明没有执行 |
| 重试使用同一 request ID，但服务端没有去重逻辑 | 相同 ID 出现 2 次提交 | 追踪 ID 本身不是幂等性机制 |
| 服务端用同一 key 返回原 receipt | ledger 只有 1 次提交，重试得到 receipt=1 | 这个自写服务的受控去重路径有效 |
| 客户端等待 10ms 超时，服务端提交延迟 80ms | 超时时提交数 0，随后提交数 1 | 取消本地等待不自动取消这个服务端 handler |
| 两个并发请求使用同一 key | lock 保护下只提交 1 次，两方 receipt 相同 | 本实现的内存 commit/cache 临界区覆盖并发竞争 |
| 同一 key 对应不同 amount | 不绑定 body 时错误返回旧 amount=1；绑定后拒绝 amount=99 的第二请求 | 去重 key 还需要明确请求语义和参数一致性 |

这些案例是原理实验，不是已发现某云 SDK 重复执行的证据。将它们用于真实 adapter 测试时，必须换成该 adapter 的实际协议，并独立读取远端状态。不能只看客户端 exception。

### 与一手资料的关系

[RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2) 将 idempotency 定义为多次相同请求的预期服务端效果与一次相同；它不要求每次返回字节完全相同，也不禁止独立 access log。该节限制对非幂等请求的自动重试，除非已知操作语义可安全重试，或能判断原请求没有应用。已读该节，未声称读完 RFC 全文。

[Amazon Builders' Library：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) 进一步讨论：caller-provided key、记录 token 与业务操作的原子性、语义等价响应、迟到请求和 key 有效期、同 key 不同参数应返回不匹配错误。已读相关章节。我们的内存 lock 只覆盖其中很小一部分，没有实验 durable atomicity 或 key expiry。

因此，评测运行器的 retry manifest 至少需要：操作类型、稳定 operation ID、attempt ID、参数 hash、服务端幂等性承诺、有效期、查询/对账方法。它们是本文提出的工程检查项，不是这些框架共有的现成功能。

## 3. 三个真实本地 I/O 实验

### 首个进程退出，不等于 pipe 到达 EOF

一个受控子进程写入 ONE 后以 0 退出；另一个受控子进程仍继承同一 pipe 的写 FD。实验在第一个进程退出后读到 ONE，但没有 EOF。只有显式通知第二个进程关闭后，读端才得到 EOF。

这个测试通过额外控制管道释放 FD，而不是依赖“睡多久大概能重现”的时序假设。两个子进程都由实验直接持有并 wait，不留下后台进程。

这说明 process exit、output completion 和 command completion 需要各自定义。它不是 Kubernetes、SSH 或 Docker 远程 exec 的运行验证，相关 adapter 仍须另外测。

### PTY 可能改变通道和换行

同一程序分别向 stdout 写 OUT\n、stderr 写 ERR\n。普通 pipes 分别保留两个流；将两个流接到同一 PTY、明确开启 OPOST/ONLCR 后，观测为合并的 OUT\r\nERR\r\n。

实验不声称所有平台或所有 PTY 默认设置相同。[Python pty 官方文档](https://docs.python.org/3.12/library/pty.html) 明确指出该功能具有平台依赖性。使用 TTY 解决交互兼容性时，不能仍假定 stderr 可单独评分或输出字节与无 TTY 完全一致。

### 字节 chunk 不一定是字符边界

把“结果✓”的 UTF-8 字节分成 9 个单字节 chunk。每个 chunk 单独以 errors=replace 解码会产生替换字符；同一标准库 incremental decoder 维护跨 chunk 状态后，恢复原文本。

这不是某条已审计 adapter 存在乱码 bug 的证据。它给出一个非常便宜的负例输入：测试输出截断、分块、日志标准化和流式 viewer 时，应包含跨 chunk 的非 ASCII 字符。

## 4. 如何迁移成真实 harness 验收

1. 先建立只会修改受控计数器或临时文件的动作，避免用真实邮件、支付或不可恢复写入做实验。
2. 同时记录客户端 observation、远端 receipt、实际副作用、原始输出和标准轨迹。
3. 在“收到请求前、提交前、提交后响应前、收到响应后保存轨迹前”分别注入故障。
4. 分开测试相同 operation ID 重试、不同 ID 重试，以及同 ID 不同参数。
5. 验证 client timeout、cancel request、remote process exit、stdout EOF、environment stop 各自的状态。
6. 测同一行为在 pipes/PTY、stdout/stderr、ASCII/UTF-8、短行/无换行长输出下是否仍可解释。
7. 记录未能证实的状态为 unknown；不要从缺失日志推断没有副作用。

上述迁移计划尚未在上游执行。本地 27 个 PASS 证明这份自写实验的断言通过，不证明某产品通过了同样的验收。
