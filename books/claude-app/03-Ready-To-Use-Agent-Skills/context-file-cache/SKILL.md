---
name: context-file-cache
description: Design or debug client attachment pipelines, draft/blob persistence, UTF-8 budgets, cancellation, and preview-resource caches for chat applications. Use for context and file lifecycle work; do not infer server prompt-cache internals or model tokenization from client counters.
---

# 上下文文件与客户端缓存

## When to use

输入附件跨聊天串线、并发超预算、刷新后丢失、object URL 泄漏、失败重试混乱，或需要设计文件到上下文的完整客户端流水线时使用。若问题是服务端 prompt caching 的价格、TTL、缓存命中策略，应查询该服务的当前官方 API 文档；本技能的客户端证据不能回答那些问题。

## Workflow

1. 先标出表示和归属：内联文本、原生 File/Blob、服务器文件引用、同步资料引用分别建模。记录 account、conversation/draft、client ID 和处理代次，别用文件名充当身份。
2. 阅读 [生命周期合同](references/lifecycle.md)，确认本次任务属于准入、处理、持久化、恢复还是资源释放。需要复核产品观察时读 [版本冻结证据](references/evidence.json)。
3. 把文件选择、拖入、粘贴接入共同入口。按能力与处理器优先级路由；先校验再处理。不要把 picker 的 accept 当作安全校验。
4. 内联预算使用 UTF-8 字节；异步转换前先预留额度。使用 [原创客户端模型](assets/client-context.mjs) 的 reservation 思路，并把所有数量上限作为产品配置传入。模型 token、字符串长度、字节数分别命名。
5. 每次异步写回前检查归属和代次。切换会话、删除或路线变化时取消旧任务；旧任务即使随后成功，也不能重新挂回当前输入。
6. 持久化 JSON 元数据与 Blob 内容分开处理。恢复要区分文字已就绪、Blob 仍加载、引用不可恢复。只有引用而没有 bytes 时明确提示，不能把附件标为可发送。
7. 错误分为准入拒绝、编码待选择、可重试传输错误、用户取消、未知外部结果。自动重试限定在已知可重试且幂等的操作；已发出的远端删除/上传不能凭取消本地 Promise 判定撤销成功。
8. 运行 `node --test assets/*.test.mjs`。再用真实宿主测试刷新恢复、跨账户隔离和网络中断；本地模型不证明浏览器存储或服务器合同。

## Anti-Patterns

- 把 `cache_read_input_tokens` 显示字段描述为客户端能控制服务端缓存放置。
- `text.length` 当字节数，字节数除以四当真实 tokenizer；根据文件名全局共享缓存。
- 两个并发转换都先读同一个剩余额度，完成后才入账。
- 用一个 loading 布尔值表示等待策略、转换、上传、编码选择和失败。
- JSON.stringify 整个运行态，试图保存 Promise、AbortController 或 File 的实际 bytes。
- 移除一张附件卡片就删除共享远端文件；释放一个订阅者就 revoke 其他预览仍在使用的 URL。

## Code seed

```js
import { InlineBudget, PreviewPool } from './assets/client-context.mjs';
const budget = new InlineBudget({ owner: 'draft-A', limit: 12_000 });
const reservation = budget.reserve('中文与 English');
if (reservation) reservation.commit('attachment-1');
// 12_000 是本例配置；不是 Claude 上限或模型 token 窗口。
const previews = new PreviewPool(URL.createObjectURL, URL.revokeObjectURL);
```

只要复制整个技能文件夹，示例与参考就能独立使用；没有对本书其他目录的运行依赖。
