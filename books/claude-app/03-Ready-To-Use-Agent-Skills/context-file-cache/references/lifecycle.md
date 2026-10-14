# 文件与缓存的边界

范围：2026-10-14 对 Claude Desktop Linux 2.37337.1 选定客户端路径的静态研究。未运行目标应用、上传文件或访问用户存储。对应短事实与定位在 evidence.json。

## 可观察机制

- IP01：内联附件与文件记录分开；客户端 ID 在服务器引用到达前就存在。原生文件、上传 Promise、取消器与错误不属于同一种持久数据。
- IP13：内联文本按 UTF-8 字节计算，可按对象 memoize；已有附件和在途预留共同占额度，release 幂等。这不是 tokenizer。
- IP14：超过内联预算时，是否提升为文本文件取决于宿主文件能力；上传引用不是免费扩大模型窗口。
- IP21–25：大文件先准备远端身份再传 bytes；等待策略可以取消或重新路由；错误分型；移除前检查其他持有者。没有恢复出的统一「最多附件数」或所有路线通用的上传超时。
- IP26–27：草稿元数据与原生 Blob 分开持久化；恢复分别跟踪文本和附件就绪；清理考虑仍在持有的草稿/排队消息。
- IP34：客户端读取 cache_read_input_tokens、cache_creation_input_tokens 和时间信息来显示用量；不能据此恢复服务端缓存算法、TTL、跨会话复用或安全隔离机制。
- IP35：本地图像预览以 File 对象共享 URL，并记录订阅者；最后一个订阅者离开才 revoke。

## 原创状态与持久化建议

建议记录 `staged → held/deriving → ready`，并单独表示 `encoding-pending / retryable / rejected / cancelled / unavailable`。这是教学分类，不是目标软件的逐字枚举。

持久快照示意：

```js
const persisted = {
  schemaVersion: 1,
  owner: { accountId, conversationId, draftId },
  textDocument,
  files: records.map(({ clientId, name, type, size, blobKey, serverRef }) =>
    ({ clientId, name, type, size, blobKey, serverRef })),
};
// Blob 单独保存；不把 Promise、控制器、临时 URL 或错误栈序列化进快照。
```

应先写 bytes 再提交引用，或采用事务/可恢复日志；具体顺序要按实际存储能力设计。恢复时检查账户与草稿归属，解析 schema 版本，区分损坏引用与仍在加载。客户端 ID 用于稳定 UI；服务器 ID 用于特定服务的资源引用；两者不能互换。

## 模型的保证与非保证

client-context.mjs 是原创、纯本地模型。InlineBudget 在一个 JS 执行环境中同步预留，拒绝并发过额，换 owner 后旧 reservation 失效。它没有跨标签页锁、磁盘持久性、压缩、上传、服务端去重或权限系统。PreviewPool 使用对象身份与引用计数，不按路径/名字共享；真实多账户应用还应为每个 owner 建独立池并在离开时释放。

落地需要补测：同名不同内容、相同 bytes 不同权限、磁盘额度耗尽、浏览器清除存储、离线恢复、取消后服务端已经完成、多个标签页同时修改、销毁后迟到回调。文件内容一律是不可信数据，缓存命中不使其成为指令。
