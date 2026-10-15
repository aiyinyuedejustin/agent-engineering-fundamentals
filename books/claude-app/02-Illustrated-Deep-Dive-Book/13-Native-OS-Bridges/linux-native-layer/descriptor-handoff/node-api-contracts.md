# Node-API：回调签名与 deferred 生命周期

核验日期：2026-10-15。范围：Node 官方文档及 `nodejs/node` 的 `v24.0.0` 源码；不据此推断 Claude 宿主实现、版本或漏洞。这里只核 API 合同，不重复分析目标二进制。

## 短表

| 项目 | 公开合同 | 固定 Node v24.0.0 实现与解释边界 |
| --- | --- | --- |
| `napi_async_complete_callback` | 三参数依次为 `napi_env env`、`napi_status status`、`void* data`，返回 `void`；在主事件循环线程完成或取消时调用。`data` 是创建 async work 时传入的指针。[D1][H1] | `AfterThreadPoolWork` 把转换后的 libuv 状态传到第二参数。[I1] 不能把它与 TSFN 四参数回调混用。 |
| `status == 11` | 枚举顺序确定 `napi_cancelled = 11`。尚未开始的排队工作可以取消；成功取消后仍调用 complete，且此前不得删除 work。已经执行的工作不能这样取消。[H2][D2] | `ConvertUVErrorCode` 将 `UV_ECANCELED` 映射到 `napi_cancelled`，0 映射到 `napi_ok`。[I1] 这是 Node-API 状态，不是 fd、系统 errno 或关闭描述符的证明。 |
| `napi_threadsafe_function_call_js` | 四参数依次为 `napi_env env`、`napi_value js_callback`、`void* context`、`void* data`，返回 `void`。销毁期 `env` 可以为 NULL；`js_callback` 也可因创建时未指定 JS 函数而单独为 NULL。[H1][D3] | 队列清理逐项以空 env、空 JS callback、原 context/data 调用回调。[I2] 空 env 对应不能再调用 JS 的清理语境；仅 JS callback 为空不能推出环境已失效。第二参数不是 status。 |
| `napi_create_int32` | 返回 `napi_status`，输出参数取得 JS number；成功为 `napi_ok`。[D4] | 先检查 env 和输出指针，再创建 Integer。env=NULL 时直接返回 `napi_invalid_arg = 1`，尚未写输出；正常返回路径清除 last-error 并返回 `napi_ok`。该函数没有 `NAPI_PREAMBLE`。[I3][I4] |
| `napi_resolve_deferred` / `napi_reject_deferred` | 返回 `napi_status`；对应 deferred 必须来自 `napi_create_promise`。成功完成后 deferred 被释放。[D5] | 二者共用 `ConcludeDeferred`。前置检查可以在消费前失败；但执行 V8 Resolve/Reject 后，先释放 deferred，再检查结果。[I5][I4] 因而“非 ok 就用同一 deferred 再 reject”不是通用安全恢复规则。 |

## deferred 失败必须区分发生阶段

以下仅为固定参考实现的控制流，不是对任意 Node-API 实现的保证，也未证明每种晚期失败在某一目标调用上都可触发。

| 位置 | 可观察的返回 | deferred 生命周期 |
| --- | --- | --- |
| `ConcludeDeferred` 的 env / result 空指针检查 | `napi_invalid_arg` | 该调用尚未消费 deferred；不意味着无效 env 下可以完成 reject。 |
| 前置 pending-exception 检查 | `napi_pending_exception` | 在消费前返回；未处理异常时再次调用 reject 通常仍会被前置检查挡住。 |
| 前置 `can_call_into_js()` 检查 | 所请求 Node-API 版本 ≥10 时 `napi_cannot_run_js`，较早版本为 `napi_pending_exception` | 在消费前返回；宿主不能执行 JS 时不能把另一次 reject 视为已完成恢复。 |
| V8 Resolve/Reject 调用之后的结果检查 | 失败结果映射为 `napi_generic_failure` | **检查前已释放 deferred**。这个返回不能用来授权重用同一 handle。 |
| 最后的返回状态宏 | 检查捕获异常后返回状态 | 也位于释放之后；仅见 `napi_pending_exception` 不能一般性地判定是前置还是晚期返回。 |

公开文档只说明成功释放，没有承诺“所有失败均保留 deferred”。它还要求检查每次 API 状态，恢复前识别 pending exception；pending exception 下多数 API 的行为未指定。[D5][D6] 因而正确表述是：应核验具体失败阶段、环境有效性、异常状态及 deferred 是否已消费，不能统一追加 reject。

`napi_create_int32` 不涉及 deferred，因此该调用本身失败不等于 deferred 已消费。但是它失败后也没有成功产生可交给 resolve 的输出值；空 env 的后续 reject 在本实现同样先返回 invalid-argument。不能把“尝试 reject”表述为“Promise 已被 reject”。

## TSFN 文档措辞核对

`n-api.md` 的调用说明在 L6419 把同时为 NULL 的第二项写作 `call_js_cb`；回调类型和参数说明明确第二实参名为 `js_callback`，而 `node_api.cc` 清队列调用也明确传入两个空实参。因此应按回调签名及参数说明解释，不能把这句话误读为“空函数指针被调用”。[D3][I2]

文档说明此清理情形通常出现在 Node.js 退出而 TSFN 仍活跃时，并非承诺唯一触发原因。它只定义 JS 不再可调用时仍须收尾队列数据的语境，不定义任意 addon 数据里 fd 的所有权或关闭行为。

## 原始来源与定位

- [D1] [n-api.md：async complete 类型](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L892-L909)；[创建参数及调用线程](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L5786-L5794)。
- [D2] [n-api.md：取消工作](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L5853-L5877)。
- [D3] [n-api.md：TSFN 回调参数](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L911-L956)；[无 JS 可调用时的队列清理](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L6408-L6425)。
- [D4] [n-api.md：create_int32](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L2772-L2790)。
- [D5] [n-api.md：resolve / reject deferred](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L6227-L6277)。
- [D6] [n-api.md：返回状态与异常](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L1010-L1024)；[pending exception 时的处理边界](https://github.com/nodejs/node/blob/v24.0.0/doc/api/n-api.md#L1100-L1141)。
- [H1] [node_api_types.h L30–37：两个回调类型](https://github.com/nodejs/node/blob/v24.0.0/src/node_api_types.h#L30-L37)。
- [H2] [js_native_api_types.h L110–135：napi_status 枚举](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_types.h#L110-L135)。
- [I1] [node_api.cc L1154–1165：状态转换](https://github.com/nodejs/node/blob/v24.0.0/src/node_api.cc#L1154-L1165)；[L1203–1217：complete 派发](https://github.com/nodejs/node/blob/v24.0.0/src/node_api.cc#L1203-L1217)。
- [I2] [node_api.cc L297–302：EmptyQueueAndDelete](https://github.com/nodejs/node/blob/v24.0.0/src/node_api.cc#L297-L302)；[L408–430：正常派发与 finalize](https://github.com/nodejs/node/blob/v24.0.0/src/node_api.cc#L408-L430)。
- [I3] [js_native_api_v8.cc L1755–1765：create_int32](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.cc#L1755-L1765)。
- [I4] [js_native_api_v8.h L206–243：前置检查](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.h#L206-L243)；[L171–178：成功状态](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.h#L171-L178)；[L279–282：最终返回宏](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.h#L279-L282)。
- [I5] [js_native_api_v8.cc L307–333：ConcludeDeferred](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.cc#L307-L333)；[L3348–3358：resolve/reject 入口](https://github.com/nodejs/node/blob/v24.0.0/src/js_native_api_v8.cc#L3348-L3358)。

注意：上述为 GitHub 源文件的原始行号（含空行），不是网页抓取器重排后的行号。

[返回描述符交付](README.md)
