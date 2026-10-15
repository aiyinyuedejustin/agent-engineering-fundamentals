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

InlineBudget 的 limit 是构造时验证的只读配置；变更额度须新建账本并按宿主合同迁移现有条目，不能直接修改属性。PreviewPool 在调用注入的 revokeURL 之前移除旧条目，因此该回调重入 acquire 时会重新调用 createURL 创建新条目。revokeURL 若抛错会向调用者传播，旧 handle 已释放且不会复用；这不证明 URL 已实际撤销。宿主需记录并处理清理失败，不能以池为空声称底层资源已回收，也不能重放该 handle 的 release 假装重试成功。

落地需要补测：同名不同内容、相同 bytes 不同权限、磁盘额度耗尽、浏览器清除存储、离线恢复、取消后服务端已经完成、多个标签页同时修改、销毁后迟到回调。文件内容一律是不可信数据，缓存命中不使其成为指令。

## 注入的预览适配器合同

PreviewPool 保持同步 API：createURL(file) 必须同步返回该资源的 URL，失败可以抛错；这是调用前提，代码不验证或支持 Promise 返回值。每次成功创建应提供可独立撤销的资源身份，不能让不同活跃 entry 共用同一个可被撤销的 URL；原生 createObjectURL 符合这一使用方式。同一 File/Blob 对象正在创建时递归 acquire 会明确抛错，避免覆盖活动记录；适配器可捕获该错误继续创建，或让它传播，此时池会清除创建标记以允许重试。不同对象的创建期重入允许。此限制针对自定义适配器回调，原生 URL.createObjectURL 不会自行回调本池；不是浏览器漏洞声明。若适配器在抛错前分配了资源，该资源的清理由适配器负责，因为池没有收到其 URL。

release 只移除它仍持有的 entry，重复 release 不再次撤销。最后一个订阅者释放时仍先移除 entry 再调用 revokeURL，以保留撤销期同对象重入的既有合同。池没有 dispose/clear API；宿主必须释放各 handle，不能把本模型理解为全池销毁接口。
