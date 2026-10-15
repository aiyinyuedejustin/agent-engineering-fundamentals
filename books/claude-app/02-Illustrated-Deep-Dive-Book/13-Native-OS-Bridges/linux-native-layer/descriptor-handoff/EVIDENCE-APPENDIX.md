# 证据附录：fd交付的条件、定位与未闭合链

本轮只补已发表 Linux 原生层章节留下的失败交付缺口。对象是 Claude Desktop 2.37337.1、Linux amd64 的同一份已校验原生模块；SHA-256 为 `c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6`，大小 10,026,272 字节。以下全部是静态控制流与数据传递，未加载或执行目标。

## 1. 先分清状态和结果，再看 fd

三份函数不能使用同一张“取消状态”表：

| 分析标签 | 地址 | 真正的回调形状 | 第二参数 |
|---|---|---|---|
| socket 交付 | `0x6216e0` | Thread-safe function（TSFN）`call_js_cb(env, js_callback, context, data)` | JS callback 值，不是 status |
| openRootDir 完成 | `0x61b4d0` | async-work `complete(env, status, data)` | Node-API status |
| openBeneath 完成 | `0x61b230` | async-work `complete(env, status, data)` | Node-API status |

socket 的工厂把该函数放入 `napi_create_threadsafe_function` 的 `call_js_cb` 位置，把 Promise 的 deferred 放入 context；两个文件方法把函数放入 `napi_create_async_work` 的 complete 位置。这不是根据参数数量猜测。[NDH-01]

下表使用局部记号，不冒充恢复出的 Rust 类型：

- `D`：结果结构首个64位字段。`D=-1` 选择数值成功分支。
- `V`：结果结构 `+8` 的联合载荷；在已产生成功结果时，其低32位是 fd 数字。
- `F`：已经由 execute 写入的真实成功 fd。它比“仅看到 `D=-1`”条件更强。
- `S`：文件回调的 status。固定 Node v24.0.0 ABI 中 `0=napi_ok`，`11=napi_cancelled`。参考版本只用于解释 ABI，不证明产品宿主版本。
- `C`：文件任务共享控制块 `+0x10` 的字节；本轮仅证明入口检查 `C==2` 时抑制结算，并在结束时写1，不把它命名成已验证可触发的用户取消状态。

**特别容易误读的一点：两个文件任务在 execute 尚未运行时，就已经把结果初始化为 `D=-1,V.low32=0`。** 因而取消回调看到 `D=-1`，不能证明打开过 fd，更不能把该初始0当作本次取得的描述符。execute 真正返回后才会把 worker 的结果与 fd 写入相同槽位。[NDH-02]

### 文件回调的局部条件表

共同前置动作：取出原 `D,V` 到寄存器，立即把任务内结果改为 `D=-1,V低32位=0`；取出 deferred / async-work handle，再清零其原槽。[NDH-03]

| 入口或API条件 | Promise 动作 | 清理动作 | 对已存在 `F` 的局部观察 |
|---|---|---|---|
| `S=11`，任意 `C,D` | 跳过 create_int32、resolve、reject | delete_async_work；写 `C=1`；路径/分量、错误字符串、控制块及任务容器清理 | 若原来确有 `F`，本分支没有把它传给 close 或另一个描述符接收者；是否可能带着已打开的 `F` 到达这里未证实 |
| `S!=11` 且 `C=2`，任意 `D` | 同上 | 同上 | 同上；`C=2` 的实际写入者与这些任务的关联未闭合 |
| 其余 `S!=0`，原 `D=-1` | 构造 status 错误，尝试 reject | 共同清理 | 原 fd 数字不进入新的错误对象；没有本地 fd 回收路径 |
| `S=0,C!=2,D!=-1` | 把原错误转换后尝试 reject | 错误字符串与共同清理 | 原载荷按错误解释，不能把它当 fd |
| `S=0,C!=2,D=-1`，create_int32 非0 | 构造转换错误，尝试 reject | 共同清理 | 保存 fd 的寄存器被 API status 覆盖；任务中的原 fd 已被清零；未传给描述符清理函数 |
| 同上，create_int32 为0，resolve 为0或非0 | 调用 resolve；**不检查其返回值** | 直接共同清理 | 没有针对 resolve 失败的分支或重试 reject；数字 fd 是否最终被 JS 接收不由这段代码证明 |

这里的“尝试 reject”和“调用 delete”有意不写成“Promise 已拒绝”或“清理成功”：两个文件回调都未检查 reject / delete_async_work 的返回值。[NDH-04]

### socket 回调的局部条件表

socket 收到的 `data` 是40字节堆结果容器；`context` 是 deferred。它没有 async-work 的 `S` 参数，也没有文件回调的 `C` 检查。[NDH-01、05]

| 入口或API条件 | 交付 / 错误动作 | 结果容器 | fd 的局部去向 |
|---|---|---|---|
| `D=-1`，create_int32 非0 | 构造转换错误，尝试 reject | 正常返回尾部调用 `free(data)` | fd 数字仍在原容器 `+8`；未传给局部 close / fd析构后便释放容器 |
| `D=-1`，create_int32 为0，resolve 非0 | **检查返回状态**；构造另一错误，尝试对同一个 deferred 调用 reject | 同上 | 新错误中没有 fd；释放原容器，不构成本地 fd 回收证明 |
| `D=-1`，两个API均为0 | resolve 后进入共同尾部 | 同上 | 向 JS 交付的是整数；该段不建立 fd 对象的析构器 |
| `D!=-1` | 把原错误转换后尝试 reject | 错误转换释放错误字符串，尾部释放容器 | 非成功载荷不能解释成 fd |
| `env=NULL` | **没有独立的 NULL-env 分支**；仍按 `D` 选择上述 API 路线 | 普通返回仍走上述尾部 | 这是 TSFN 拆除相关条件，不是 `S=11`；本回调自身没有独立的 fd 回收路线 |

socket 的 reject 返回值也未检查。异常落点调用的 `0x63d5a0` 不是一个带 fd 析构逻辑的隐藏 helper，而是直接跳到 libc `free`。[NDH-06]

## 2. 已闭合的是容器清理，不是 fd 的完整所有权

本轮确实把“也许 helper 里 close 了”的部分缺口缩小了：

1. 三个回调使用的 `0x98c5a8` 重定位明确是 libc `free`；它释放的是结果/任务/字符串等内存地址。
2. 文件回调的共享控制块 helper `0x709270` 只读取指针、减另一计数，必要时 `free`；没有以成功 fd 为参数的分支。
3. 文件回调的异常清理 helper `0x617860` / `0x6179f0` 释放路径或分量、非空错误字符串、共享控制块与任务容器。结果为 `D=-1` 时跳过错误载荷释放，且完成回调入口已把任务结果重置。
4. 错误转换 helper `0x52cb60` 处理错误字符串/引用和 JS Error；本轮讨论的转换失败路径传入的是新错误对象，未把 `F` 放进去。[NDH-06]

因此可以严谨地写：**在这些选定的、普通返回的交付失败路线中，没有恢复出一条从真实成功 fd 到本地描述符回收操作的边；可定位到的尾部清理主要是内存和异步资源清理。** 不能把这个局部事实升级为“确定泄漏”“可利用漏洞”或“全生命周期安全”。

“调用 free(result)”也不等于“关闭 result 内保存的 fd”。一个原始整数被复制成 JS 数字，只说明数字传递；它没有在这里自动附带 `close` 的所有权语义。

## 3. socket 的断点还早于回调

生产端选定分支 `0x4049f5..0x404a36` 分配40字节，把 `D=-1` 与 fd 写入容器，再调用 `napi_call_threadsafe_function(tsfn,data,1)`。随后没有检查该调用返回值，直接进入 `napi_release_threadsafe_function(tsfn,0)`。[NDH-05]

这新增了一个明确的研究边界：**TSFN 投递被拒绝时，不能仅凭存在 call-js 回调就断言它将接管并释放 data，更不能断言 fd 已经到达 JS。** 这段生产端没有根据入队返回状态恢复描述符归属的局部分支。异步任务层包含间接分派与运行时状态，尚未完成所有取消/丢弃/拆除路径的整体所有权证明。

## 4. 公开 Node 合同能解释什么，不能代替什么

固定 [Node v24.0.0 回调定义](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L935-L953) 允许 TSFN 在 JS 已不可调用时以 `env=NULL` 让原生侧清理待处理 data；[参考实现](https://github.com/nodejs/node/blob/v24.0.0/src/node_api.cc#L297-L303) 的队列清理会这样调用 call-js。这解释了为什么 socket 不能只研究“普通成功 env”或把参数误解为 status。

在同一参考版本，`napi_create_int32` 遇 NULL env 会在创建 value 前返回 `napi_invalid_arg`。[实现](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.cc#L1755-L1765)、[检查宏](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.h#L206-L217)。这是一种参考 ABI/实现推演，不是本样本在实际宿主运行后的观察。

另一个不能照抄的设计是“resolve 非0就用同一个 deferred 再reject”。固定版本的 [ConcludeDeferred](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.cc#L307-L333) 有前置检查失败、尚未消费 deferred 的返回，也有执行 Resolve/Reject、删除 deferred 后才返回非成功的路线。**非0状态本身不足以判定 deferred 仍可复用。** 本轮不据此给产品下运行时缺陷结论；真正宿主版本、具体失败状态与可达性仍需另证。

## 5. 所有权链具体断在哪里

| 缺口 | 本轮已经缩小到哪里 | 尚缺的证据 |
|---|---|---|
| 文件 create_int32 失败 | 原 fd 槽已清零；寄存器改存status；新错误不带fd；选定cleanup不close | 该失败如何在实际宿主发生、是否有未覆盖外部持有者或补偿机制 |
| 文件 resolve 失败 | 明确不读取返回状态；直接清理 | 实际状态及deferred是否被消费、JS能否收到数字、上层如何回收 |
| 文件取消 | `S=11` / `C=2`抑制结算；入口结果搬移和初始化已定位 | execute与取消时序；`C=2`写入链；带真实成功fd的条件组合可达性 |
| socket回调交付失败 | create/resolve检查与reject尝试、原结果free已定位；普通尾部无fd回收边 | 实际API失败状态、宿主deferred合同及外部持有者 |
| socket入队失败/环境拆除 | 入队返回值未检查；call-js无NULL-env分支 | TSFN在实际宿主的接管/拒绝/拆除路线，以及完整任务取消与drop链 |
| 异常与分配失败 | 已定位三个回调的可见cleanup helper；错误分配失败另进fatal/helper路径 | 全部unwind/landing-pad路由、fatal行为与环境销毁过程；本轮不做全面认证 |

这份局部合同的用途是让下一轮验证有明确的前置条件和描述符追踪点，而不是通过“搜不到 close”推断漏洞。没有执行攻击、竞态、目标加载、故障注入或联网私有 API。

## 复核与交付范围（正文见 README.md）

- `EVIDENCE-APPENDIX.md`（本文件）：定位表、寄存器/任务槽、边界说明。
- `verify-static.py`：只对摘要/大小匹配的稳定快照运行现有 readelf/objdump；174项选定静态检查、15个FDE通过。它不是全控制流或运行时验证器。
- `verification.json`：本轮通过结果。
- `test-verifier.py`：10项不读取产品样本的原创fixture测试，涵盖拒绝输入、稳定快照和异常清理。
- `figures/descriptor-handoff.mmd`：正文原创Mermaid图源；现有Mermaid解析器与正/负对照通过。只做语法验证，不声称浏览器布局或GitHub渲染通过。
- `EVIDENCE-LEDGER.md`：收集范围、读过的来源与明确未闭合项。
- `private-evidence/`：原始反汇编与校验后样本快照，仅供私下复核，不应随正文发布。

未修改 publication 或 git。研究日期：2026-10-15（UTC）。

## NDH-01：签名关联

### socket为TSFN call-js

- `0x58fd77`：取 `0x6216e0` 到rdx；`0x58fd83` 经 GOT `0x98d4e0` 调用。RELATIVE relocation 指向 `0x701870`。
- `0x70187a` 把该指针保存r15；`0x7018a2` 调create_promise，输出deferred到栈+0x30、Promise到+0x28。
- `0x701964` 读deferred；`0x701973` 将回调放栈+0x18（call_js_cb）；`0x701978` 将deferred放栈+0x10（context）；`0x701980` 将栈+0和+8清零（finalize data / finalize callback）。
- `0x701984..0x701994`：initial_thread_count=1，JS callback=NULL，max_queue_size=0；GOT `0x98d7b0` 为napi_create_threadsafe_function。
- `0x6216ec/ef/f2`：data=rcx→rbx，context=rdx→r14，env=rdi→r15。没有把第二参数rsi解析成status；整个FDE无env是否NULL分支。

### 文件方法为async complete

- root：`0x62f151/58` 分别指定execute=`0x619f10`、complete=`0x61b4d0`；`0x62f165`经`0x98d7e8`调用create_async_work。
- beneath：`0x61cd99/a0` 分别指定execute=`0x619e80`、complete=`0x61b230`；`0x61cdad`同样调用create_async_work。
- 文件complete的第三参数rdx是任务指针；status来自esi。beneath在`0x61b241`先把status搬eax，以便后面把rsi用作async-work handle。

## NDH-02：初始值与真正执行结果

root任务大小0x58：result位于+0x18（D）、+0x20（fd低32位）；共享控制块+0x40，deferred+0x48，async work+0x50。

beneath任务大小0x68：result位于+0x28（D）、+0x30（fd低32位）；共享控制块+0x50，deferred+0x58，async work+0x60。

- root `0x62efd2` 在构造栈槽写D=-1；`0x62efdb` 只写DWORD 0。`0x62f01d..0x62f044`复制到任务。
- beneath `0x61cba5` 写D=-1；`0x61cbae`只写DWORD 0；`0x61cc04..0x61cc28`复制到任务。
- 共享控制块均malloc(0x18)，初始byte+0x10=0（root`0x62efa1`，beneath`0x61cb5c`），两个计数字段初值2/1。未由此推断源码类型名。
- root execute在`0x619f54/58`把worker的D与fd低32位写入任务。
- beneath execute在`0x619ecf/d3`做同样操作。
- 两个execute均会按旧结果D判断是否释放旧错误字符串；它们并不把默认0当成先前已打开的fd去关闭。

## NDH-03：完成入口搬移与取消条件

### root

- `0x61b4e1/e5`：D→r14，载荷→r13；`0x61b4f7/ff` 把任务D=-1、载荷低32位=0。
- `0x61b506..0x61b511`：deferred→r8、work→r15，再将两槽清零。
- `0x61b515/19` 检查原D=-1；成功时`0x61b522 mov r13d,r13d`清除寄存器高32位，接着检查S=11。
- S=11在`0x61b51b/20`或`0x61b525/28`汇入`0x61b536`。
- 非11读取共享控制块，`0x61b532`比较C=2；相等同样汇入`0x61b536`。
- `0x61b539`调用delete_async_work；`0x61b543`写C=1；`0x61b547..0x61b553`按原D处理错误字符串。

### beneath

- `0x61b243/47`：D→r15，载荷→r12；`0x61b259/61`把任务D=-1、载荷低32位=0。
- `0x61b268..0x61b273`：deferred→r14、work→rsi，清零其槽。
- 成功D=-1时`0x61b284 mov r12d,r12d`清寄存器高32位。
- S=11检查为`0x61b27d/82`和`0x61b287/8a`；C=2检查`0x61b295/99`；两者汇入`0x61b29b` delete_async_work。
- `0x61b2a5`写C=1，随后按原D处理错误字符串。

两者取消段的 `D--; unsigned_compare(D, -3); ja skip` 恰好对原D=0或-1跳过错误字符串free；其他D按错误对象的缓冲区处理。这是联合载荷判别，不能把free的指针实参当成成功fd。

## NDH-04：文件API失败的分歧

| 操作 | root地址 | beneath地址 | 后续 |
|---|---|---|---|
| create_int32(fd) | `0x61b677/67a` | `0x61b41a/41d` | 检查eax；0走resolve |
| 非0覆盖原fd寄存器 | `0x61b684 mov r13d,eax` | `0x61b427 mov r12d,eax` | 分配49字节错误文字，构造错误而不是继续传fd |
| 错误转换 | `0x61b62c` | `0x61b37c` | 调`0x52cb60` |
| reject | `0x61b63b` | `0x61b38b` | 没有检查返回状态 |
| resolve | `0x61b6ed` | `0x61b490` | 紧接无条件jmp到共同清理；未读eax |
| resolve后的jmp | `0x61b6f3 → 0x61b641` | `0x61b496 → 0x61b391` | 和reject后清理汇合 |
| delete_async_work | `0x61b649` | `0x61b39a` | 未检查状态，随后C=1和内存清理 |

其他非0 status（排除S=11/C=2）走`0x61b5ad..0x61b5ea` / `0x61b2fe..0x61b338`：丢弃原错误缓冲区（若有）、用status构造空文字错误。原D=-1时不把fd传入新错误，且分别把载荷寄存器改为1。

## NDH-05：socket生产端与交付失败

- `0x404a00/05`：malloc(0x28)；成功后 `0x404a17`写D=-1，`0x404a1e`写已经从r14d零扩展的fd到+8。
- `0x404a22..0x404a2d`：`napi_call_threadsafe_function(tsfn,result,1)`，经GOT `0x98d0b0`。
- 返回后`0x404a33/36`直接准备TSFN并跳公共释放段；`0x404a9d/9f`以mode=0调用release，经GOT`0x98d0b8`。没有依据入队返回值的分支。
- `0x6216fc..0x621724`：D=-1才把+8送napi_create_int32；`0x62172a/2c`检查status。
- create失败沿`0x62172e..0x62178e`构造49字节错误并进公共错误转换段；原结果容器未被写成新的错误对象。
- `0x62179b`调用resolve；`0x6217a1/3`检查status。非0沿`0x6217a5..0x6217e7`构造29字节错误。
- `0x62180d`转JS错误；`0x62181b`对同一个r14 deferred尝试reject；未检查返回状态。
- `0x621821/24`最终以rbx=data为实参调用free；异常落点`0x621847/4a`将相同rbx传`0x63d5a0`。

生产端整个异步poll状态机未在本轮重新恢复成全可达图。这里针对已经进入选定成功结果投递段的条件分析；没有把所有调度/取消分支压平成普通顺序执行。

## NDH-06：helper与资源类别

| helper | 直接证据 | 可以支持的局部解释 |
|---|---|---|
| GOT`0x98c5a8` | GLOB_DAT `free@GLIBC_2.2.5` | 内存指针释放调用，不能写成fd关闭 |
| `0x63d5a0..0x63d5a6` | 唯一指令jmp GOT`0x98c5a8` | socket异常helper无隐藏fd析构 |
| `0x709270..0x709286` | 读取共享指针；检查-1；减+8计数；零则jmp free | 共享控制块释放；不读取result/成功fd |
| `0x617860..0x6178c7` | 路径缓冲区free；D非-1且非0时错误缓冲区free；减计数；任务free | root任务cleanup，成功fd字段无close操作 |
| `0x6179f0..0x617a9b` | 分量循环free；集合free；错误载荷条件free；减计数；任务free | beneath任务cleanup，不负责释放成功fd |
| `0x52cb60..0x52cc41` | 错误引用/字符串→JS错误，`0x52cc22..0x52cc2c`按容量释放错误字符串 | 新构造错误的文字回收；不是接受fd的清理函数 |

上述“没有close”限于完整解码FDE、所列helper以及本轮成功fd的数据流。自动检查只核它们不含直接`close` GOT引用；不声称用字符串搜索证明所有间接调用和整个进程都不会close。malloc失败的fatal helper、完整异常展开表和宿主销毁时序仍在范围外。


## 验证器输入与临时文件合同

脚本只接受一个输入路径；末端nofollow、非阻塞open后先核普通文件与精确大小，再读受限字节数并核SHA-256。任一身份不匹配均在调用二进制工具前拒绝。通过后在系统临时目录用TemporaryDirectory创建自身独占目录，将已校验字节写成稳定快照；readelf/objdump只读该快照。JSON仅输出stdout，没有输出路径选项，结束或工具异常时只清理自身创建的临时目录，不依赖未发布private-evidence目录。

10项fixture测试不需要真实模块；mock只用于安全输入/临时目录的测试，不用于声称样本的指令检查通过。真实样本的174项检查另由verification.json记录。
