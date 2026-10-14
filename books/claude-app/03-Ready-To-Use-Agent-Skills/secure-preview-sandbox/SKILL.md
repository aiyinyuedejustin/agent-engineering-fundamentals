---
name: secure-preview-sandbox
description: Design or audit untrusted artifact previews, cross-origin iframe messaging, capability approval, stale-content revocation, and RPC cleanup. Use for preview security boundaries; the bundled local protocol model does not render code or prove browser isolation.
---

# 不可信作品的隔离预览

## When to use

用于 HTML、React、SVG 或图表预览的宿主边界设计，或排查旧作品仍能读文件、迟到批准泄露资料、预览断开却一直等待等问题。先保留用户指定的功能和运行位置；预览需求本身不授权执行第三方代码、联网或读取用户资料。

## Workflow

1. **先选最小执行能力。** 只需布局预览时，优先静态白名单 HTML/CSS、无脚本 sandbox、明确 CSP 与零宿主能力。确实需要脚本时，单独设计隔离来源、依赖供应、网络和资源预算，不直接放宽现有静态预览的权限。
2. **画清三条边界。** 内容进入 renderer；窗口握手建立通信；宿主按请求提供能力。阅读 [边界与适配合同](references/boundary-contract.md)，不要把 iframe、MessageChannel 或成功渲染本身当成授权。
3. **绑定实际窗口与来源。** 此模型只覆盖有独立、非 opaque 来源的 renderer：窗口握手严格核对 origin、source、协议版本、generation、随机 nonce 和 schema，使用精确 targetOrigin。端口转移后按通道归属与消息合同检查；不要要求 MessagePort 事件具备窗口的 origin 字段。opaque-origin 的静态 sandbox 是另一种合同，本模型不支持。
4. **内容替换先撤销旧能力。** 每次替换增加 sequence 并失效 acknowledgement；只有匹配请求 ID、方法、generation 和 sequence 的成功响应才能确认当前内容。收到能力请求时立即冻结 receipt；旧请求不能继承稍后产生的批准。
5. **能力默认关闭。** 按精确方法、资源和数据目的地进行授权，并在异步批准、读取与响应之间检查归属。参考 [原创局部模型](assets/sandbox-model.mjs) 的 read.text 示例。真实适配器还必须检查当前账户和资源权限；内容已确认不意味着允许访问私有数据。
6. **给每条等待路径结算规则。** 握手、请求、批准与 handler 都有 deadline；内容替换和销毁使旧工作失效，拒绝挂起 Promise、清理计时器并关闭端口。限制并发、消息速率、payload 和去重记录；记录满时关闭会话，不能驱逐 ID 后允许重放。取消本地工作不证明远端副作用回滚。
7. **分层验证后交付。** 从本技能目录运行 `node --test scripts/sandbox-model.test.mjs` 与 `node scripts/demo.mjs`，仅需 Node.js 20+。然后在真实目标浏览器补测来源隔离、CSP、存储、导航、弹窗、网络和资源耗尽。明确区分协议模型测试、浏览器实际执行和目标产品静态观察。

## Anti-Patterns

- 同源页面同时开放 allow-scripts 与 allow-same-origin，还声称其与父页面安全隔离。
- 只比较消息中的 origin 字符串，或给敏感数据使用通配 targetOrigin。
- 对已转移 MessagePort 照搬 window message 的 origin 判断，漏掉真实通道归属。
- 一个全局 acknowledged 布尔值让旧作品或旧批准获得新作品的权限。
- 把成功渲染、只读标记、工具描述或文件选择当成持续数据访问许可。
- 超时后清空 Map，却没有拒绝 Promise；重连后继续接受旧 callback。
- 原样向预览返回异常 message、stack、任意错误 code 或未经约束的 handler 结果。
- 把截图、静态字符串断言或本地 MessageChannel 测试写成 CSP 和浏览器隔离已通过。

## Local seed

```js
import { ContentGate } from './assets/sandbox-model.mjs';

const gate = new ContentGate(1);
const posted = gate.replace();
const oldRequest = gate.receipt();
gate.acknowledge(posted);
console.assert(gate.permits(oldRequest) === false);
console.assert(gate.permits(gate.receipt()) === true);
// permits 只检查当前内容收据；资源授权仍须独立进行。
```

完整协议模拟见 [scripts/demo.mjs](scripts/demo.mjs)，不加载网络、不执行 body、不读取真实文件。整个文件夹可独立复制；[证据摘录](references/evidence.json) 是指定版本的短事实与定位，不是运行依赖或当前生产实现保证。
