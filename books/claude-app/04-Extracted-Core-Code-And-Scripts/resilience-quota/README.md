# 原创实验：Resilience & Quota

本实验配套卷十六，演示恢复设计中的预算、身份、完成边界、游标与草稿所有权。全部代码原创；没有导入、转译或执行 Claude bundle；没有网络请求、登录、私有 API、凭据或真实用户内容。

## 运行

Node.js 20 或更高版本，无外部运行依赖。

```bash
node --test --test-reporter=tap test/*.test.mjs
node demo.mjs
```

本次结果：64 项测试通过，0 失败。`demo-output.json` 保存确定性示例。测试中的账户、session、prompt 和事件都是虚构的。

## 读代码顺序

1. `resilience-core.mjs`：模式优先级、失败分类、类别预算、退避与完成边界。
2. `recovery-state.mjs`：存储失败兜底、cursor ack、镜像、hydration 与模拟幂等服务。
3. `demo.mjs`：先看五次网络失败轨迹，再看毒事件与 byte cap。
4. `test/resilience.test.mjs`：从反例检查契约，而不是只走 happy path。
5. `diagrams/`：Mermaid 源与原创 SVG；图描述教学模型，非目标应用截图。

## 实验可验证什么

- expanded 纯网络失败的所选控制流，在第4次改计 generic，第5次终止
- 退避指数封顶不等于请求次数封顶
- 历史预算扣减与等待档位继承是两种机制
- 本地退避与声明等待应以较长者控制，而不累加
- 完成帧之后的传输错误需要与提前中断区分
- 取消必须解除等待
- 存储不可用不能令错误处理器再次崩溃
- 同步消费者应用正常返回后才提交 cursor；同步抛错走有界毒事件处理
- 4,096 UTF-8 字节不等于4,096个汉字或 emoji
- 异步恢复不能覆盖新编辑或跨账户内容
- 模拟服务端的稳定幂等身份可避免“提交成功、回包丢失”后的重复执行

## 与目标源码的明确差异

本实验不是重建的 Claude 客户端或服务端，不能拿实验测试作为目标 runtime 通过的证据。

| 实验 | 与目标选定路径的区别 |
|---|---|
| 可读对象式错误 | 不使用目标 API error 类型、特定 transport error 类与全部 TypeError 判定 |
| 纯 RetryBudget reducer | 不发送 fetch；不实现 gzip 回退或嵌套 open retry；不重建完整 telemetry |
| retry-after parser | 只接受严格整数秒或三种 HTTP-date 语法；全部按 UTC，RFC850 使用随当前日期滚动的50年规则，并核对日历日期和星期；目标各 helper 的 Number/Date.parse 更宽松且相互不同 |
| BackoffLedger | 示范版本、计数、时间、存储降级及持久顺序字段；clear 写零计数墓碑；省略模型、声明等待 metadata 与浏览器 storage 事件；过期读返回 null，没有复刻目标清理细节 |
| CursorConsumer | 统一过滤有效序号的重复事件；非正/非安全整数序号视为无 ID，仍可调用消费者，但不提交 cursor 或清除毒事件计数；目标 poll 中显式去重，不声称目标 SSE 也完全如此 |
| mirror reader | 与 writer 一样按 UTF-8 字节限制；目标底层 reader 的 text.length 检查按代码单元 |
| DraftHydration | 用显式 edit revision/owner epoch 演示；不复刻 rich-editor merge、真实 IndexedDB、附件引用存储或多 tab 竞态 |
| IdempotentServer | 原创、内存中的假想接口契约；不证明目标服务端去重、原子性或 exactly-once |
| quotaRoute | 简化展示意图；不含全部首次触达、计划切换、overage、账户 UI 条件，不能用于真实账单或购买决策 |

CursorConsumer 的调用前置条件：`apply` 必须在返回前同步完成应用，或在失败时同步抛错；模型忽略返回值，把正常返回当作应用成功。不支持 `async` 函数或返回 Promise/thenable 的消费者：误传时会在异步工作结束前推进 cursor，之后即使拒绝，同序号重放也会被过滤。这里的“应用成功后 ack”仅指上述同步合同。

生产异步路径须串行等待当前应用完成后再提交 cursor，并另行设计失败处置、重连世代与幂等；仅添加 `async` 关键字不够。在调用之后检测 thenable 也不能撤销已启动的副作用，更不能据此自动重试。配套[不支持用法反例探针](probe-unsupported-async-callback.mjs)只重现这个限制，不是异步支持测试；探针预先处理其自建 Promise 的拒绝，不执行真实副作用。

运行反例：

```sh
node --unhandled-rejections=strict probe-unsupported-async-callback.mjs
```

输出`reproduced unsupported callback usage`并退出0，表示限制被成功重现；它不加入默认绿色测试套件，也不增加异步支持的测试计数。

## 设计练习

- 把服务端声明等待改成绝对 deadline，并测试本机时钟跳变。
- 为 poison skip 增加 snapshot-repair 信号，明确视图是否完整。
- 给模拟服务加“仍在执行”“过期身份”“相同身份不同附件”三类响应。
- 用真实可控存储适配器测试 quota exceeded、读取失败和并行 tab 写竞争。
- 为复合任务列出不在消息去重事务中的外部副作用，再设计单独的幂等键。

## 实验结果范围

纯单元/模型测试已运行；目标应用运行、联网故障注入、真实账户限额、浏览器存储端到端测试均未运行。本目录只包含原创模型与生成的测试结果，不包含目标源码和原始 REA 输出。

## 恢复边界回归：2026-10-15

新增12项原创回归，原52项保留，共64项。`test/boundaries.test.mjs` 用独立 Node 子进程分别设置 UTC、America/New_York、Asia/Tokyo；三个合法 HTTP 日期表示同一时刻，必须得到相同等待与重试决策。不存在的日期、星期不匹配及自然语言日期被拒绝。RFC850 两位年份按完整时刻的50年界限解释，不使用运行时固定世纪猜测。JavaScript 不表示闰秒，`:60` 映射到下一可表示时刻；模型不验证历史天文闰秒表。规范参考：[RFC 9110 §5.6.7](https://www.rfc-editor.org/rfc/rfc9110.html#section-5.6.7) 与 [§10.2.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-10.2.3)。

BackoffLedger 的局部合同：一个逻辑写者，可信同步存储，有限非负且不倒退的时钟。允许同一毫秒连续操作。持久 `order` 在相同时间戳内区分先后；旧v1记录缺少该字段时按0读取。clear 不物理删除两份记录，而是写带更高顺序的零计数墓碑，read 对它返回 null；旧副本不能在同毫秒恢复后复活。墓碑沿用五分钟过期合同。安全整数顺序耗尽或观测到时钟倒退时，写入返回 stored:false。

record/clear 返回的 stored:true 只表示至少一份同步写入成功；双存储都不可写时返回 false，不能承诺持久清除。累计计数与clear正确排序都依赖能读到最新记录；若最新副本也无法读取，即使stored:true也不保证完整历史或清零在稍后恢复读取时仍有效。这不解决多写者、跨tab、时钟倒退、任意存储损坏或强持久性问题。clear 的逻辑清零也不是敏感数据物理擦除。已有存储读取/写入失败不抛出错误的兜底合同保持不变。
