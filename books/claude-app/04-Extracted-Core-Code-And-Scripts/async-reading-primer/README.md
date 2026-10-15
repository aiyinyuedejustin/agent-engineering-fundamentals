# 异步阅读准备实验

原创、依赖为零的 Node.js 教学实验。它把三种容易混淆的边界变成可控的事件顺序：await 前后归属变化、等待期限与任务寿命、入队与操作结算。没有 Claude 包、Electron、浏览器、网络访问或真实文件保存。`guarded=false` 与默认不配合取消的任务是有意保留的反例。

## 运行

Node.js 20+。先进入本 README 所在目录，再运行：

```sh
node demo.mjs
node --test async-boundaries.test.mjs
```

从本书根目录 `books/claude-app/` 进入此处的命令是：

```sh
cd 04-Extracted-Core-Code-And-Scripts/async-reading-primer
```

无需 package.json、npm install 或测试框架。逐字演示输出如下；测试还会自动核对此文本对应的 `expected-output.txt`，避免文档与代码各说各话。

```text
await unsafe: current=B, value=result:A, outcome=committed
await guarded: current=B, value=null, outcome=stale
deadline: report=deadline, writes=0
deadline later: report=deadline, signal=true, work=written, writes=1
queue admitted: accepted=true, state=queued, writes=0
queue started: state=running, writes=0
queue completed: state=fulfilled, value=saved, writes=1
```

测试应报告 19 项通过，0 失败、0 跳过；运行时长和测试报告排版取决于 Node 版本。当前交付在 Node.js v24.19.0 实测。也可分别运行 `node demo.mjs await`、`node demo.mjs deadline`、`node demo.mjs queue`。

## 直接复制运行

在本目录执行下面完整命令。`--input-type=module` 使标准输入按 ESM 解析；模型文件本身用 `.mjs`，不依赖 package.json 的 type 字段。

```sh
node --input-type=module <<'JS'
import { deferred, Owner, commitAfter } from './async-boundaries.mjs';
const owner = new Owner();
const a = owner.begin('A');
const gate = deferred();
const job = commitAfter(owner, a, gate.promise);
owner.begin('B');
gate.resolve('result:A');
console.log(await job);
console.log(JSON.stringify(owner.snapshot()));
JS
```

输出：

```text
stale
{"current":"B","value":null}
```

上面的 heredoc 是 POSIX shell 写法；Windows 可把 `JS` 之间的代码保存为本目录下的 `exercise.mjs`，然后执行 `node exercise.mjs`。

所有模型入口的准确 import 是：

```js
import {
  deferred, Owner, commitAfter, waitUntil, effectAfter, TeachingQueue
} from './async-boundaries.mjs';
```

测试文件的标准库依赖也是 Node 自带模块：`node:test`、`node:assert/strict`、`node:child_process`、`node:fs`、`node:url`。子进程只执行本目录的原创 demo，不执行产品代码。

## gate 为何比 sleep 更适合这组练习

`deferred()` 返回 `{ promise, resolve, reject }`。等待者停在 promise 上，实验驱动者用 resolve/reject 指定下一个事件。它控制的是“先发生什么”，没有假装模拟真实耗时。演示中的 deadline 也由一个 gate 触发；它不测量计时器精度，不提供真实超时工具。

`waitUntil` 对成功、失败和期限分别返回 `{kind:'fulfilled', value}`、`{kind:'rejected', error}`、`{kind:'deadline'}`。deadline 参数必须在到期时 fulfill。这个等待器不取消任务。真实计时器适配器还要清除不用的计时器；别把教学辅助函数直接当生产超时实现。

`TeachingQueue` 只有一个手动启动的执行者。`enqueue` 返回收据，`runNext()` 取出一项，`receipt.completion` 等待该项结算。completion 总是 fulfill 一个记录，操作失败由 `{state:'rejected', error}` 表示；这不等于操作成功。真实 SDK 可能选择让完成 Promise reject，必须读自己的契约。若只 await completion 而从不调用 runNext，任务永远不会被本模型启动。

## 预测题

先写预测，再修改 demo 的工作副本。不要靠改变测试断言把错误改成“通过”。

1. 把 A→B 改成 A→A，guarded 版本是否接收旧结果？
2. 把 gate.promise 换成 Promise.resolve('result:A')，其余顺序不动。旧结果会抢在 begin('B') 前提交吗？
3. 给 deadline 演示的 effectAfter 加上 `cooperative: true`。第二行输出中的 work 与 writes 变成什么？
4. 把 abort 移到 `await work` 之后。配合取消的任务还能撤回写入吗？
5. 将 queue 的任务改为 `async () => { throw new Error('SAVE_FAILED'); }`。入队是否仍成功？completion 是 reject 还是 fulfill 什么记录？
6. 在“权限检查完成”与“提交”之间新增一次 await。原先的归属检查还充分吗？应在何处补查？

## 对照答案与测试定位

1. 不接收。每次 begin 都换 ticket，即使 label 相同。对应“同一标签重新开始也撤销旧票据”。
2. 不会。已 fulfilled 的 Promise 仍使 await 后续稍后恢复。对应第一项测试。
3. `work=aborted, writes=0`；`report=deadline` 和 `signal=true` 不变。信号在任务恢复后才被观察到。对应“任务在提交前合作检查信号”。
4. 不能，writes 仍为 1。当前实验没有撤回操作；真实外部副作用更不能由 abort 自动回滚。可按下段完整代码验证。
5. accepted 仍为 true。completion fulfill 的记录为 `{state:'rejected', error}`，不是操作成功。对应“入队成功的操作也会失败”。
6. 不充分。应在新的 await 之后、提交之前重新核对；若交付前再出现异步边界，也需重新判断。资源权限或外部原子性仍是另一层契约。

取消发生太晚的完整验证：

```sh
node --input-type=module <<'JS'
import { deferred, effectAfter } from './async-boundaries.mjs';
const gate = deferred(), effects = [], controller = new AbortController();
const work = effectAfter(gate.promise, effects, {
  signal: controller.signal, cooperative: true
});
gate.resolve();
await work;
controller.abort();
console.log(`aborted=${controller.signal.aborted}, writes=${effects.length}`);
JS
```

输出为 `aborted=true, writes=1`。

## 可证明与不可证明的事

19 项测试覆盖当前/过期/同名新代/伪造/销毁的归属、已完成 Promise 的让出、拒绝传播、期限前后成功与失败、迟到拒绝、取消信号合作与否、入队/运行/结算状态、失败后的继续处理、FIFO 与单执行者，以及演示输出。

本例没有持久队列、重试、幂等性、并发 worker、容量限制、操作历史淘汰、外部权限或真实资源回收。内存状态 Map 会保留本次实验所有条目。ticket 身份只适用于本进程，不能作为跨进程身份认证。通过测试证明的是这些原创局部模型的行为，不能推导 Claude 或任意生产系统已实现相同保证。
