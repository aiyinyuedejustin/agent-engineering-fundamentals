---
name: mcp-tool-integration
description: 设计、审查或调试 MCP 工具集成的安装信任、配置范围、传输身份、逐次调用权限与资源端授权；用于密钥失败、异步撤权、旧连接回调和未知执行结果等边界问题。不用于宣称完整协议实现或推断产品私有服务端行为。
---

# MCP 工具集成：把可连接与可授权分开

目标是产出可验证的集成边界、状态转换与失败处理。MCP 消息协议、MCPB 包交付、宿主审批和资源服务的授权是不同合同。保留用户指定的宿主、运行位置和部署方式，不因采用 MCP 就扩大安装、文件或联网权限。

## Workflow

1. **先确定执行与信任边界。** 标明宿主、包/配置来源、实际执行机器、传输端点、已认证主体和资源所有者。名称相同不能证明是同一服务；登记版本与制品标识。描述里出现“本地”时，写清属于谁的机器。
2. **分别定义五个门。** 安装门验证来源、制品与运行权限；配置门验证必填项、有效范围及敏感引用；连接门验证传输和对端身份；调用门绑定服务、工具、不可变参数及本次审批；资源门在服务执行侧核对实际主体、资源与动作。任一门成功都不替代其余门。策略尚未加载按未授权处理。
3. **按实际能力编写配置适配器。** 明确平台覆盖、配置来源优先级、执行目录、环境变量和密钥提供者；更改配置后使旧代次与旧审批失效。不要默认沿用示例版本、任意 shell 展开或全量继承环境变量。密钥不可读、加密不可用、类型不支持或写入失败时阻止相关操作，不把明文当作回退值。
4. **用代次隔离生命周期。** 启动、重配、撤销、断开都应使旧连接票据失效；每次异步返回后再次核对代次和当前权限。关闭迟到连接，不让旧结果更新新会话。无法确认旧运行时停止时保留阻塞状态，不报告“已停止”。[参考合同](references/contract.md) 区分代次隔离与真实进程清理。
5. **把确认绑定到实际请求。** 在等待用户、准备附件、解析配置、连接或发送前后复核相关权限。参数先复制并冻结；发现工具时绑定来源身份和可信工具合同。`readOnlyHint`、工具描述和服务返回文字都不是授权。对资源的读取与随后向另一站点发送数据分别判断授权。
6. **区分未发出、已完成与结果未知。** 一旦交给传输，异常、超时、取消和断线都可能发生在副作用之后；不得自动重发，也不得换一个操作 ID 绕过不确定状态。优先查询服务端持久回执；只有明确的去重合同与相同幂等键才能支持受控重试。审批不能保证远端回滚。
7. **用行为测试交付。** 从 [原创模型](assets/boundary-model.mjs) 提取适用部分；运行 `node --test assets/boundary-model.test.mjs`。至少验证延迟批准后的撤权、配置变化、旧连接迟到、密钥失败、资源端拒绝及“写入成功但响应丢失”。最后按真实 SDK/服务合同补集成测试，清楚列出未验证部分。

## 最小调用示例

此例在本目录执行，只操作内存中的合成资料，不安装扩展、不打开网络、不读取真实密钥：

```js
import { IntegrationHost, ResourceService } from './assets/boundary-model.mjs';

const resource = new ResourceService({ 'doc-a': '合成资料' });
resource.setAccess('test-user', 'doc-a', ['read']);
const host = new IntegrationHost();
host.register({ id: 'index', artifact: 'synthetic-v1', peerIdentity: 'test-service' });
// 以下管理调用只能来自可信宿主控制面；不是模型自行批准的接口。
host.setInstallationAllowed('index', true);
host.configure('index', {
  endpoint: 'memory:test', workspace: 'test-docs', secretRef: 'test-only',
}, { scopeApproved: true });
host.setToolPolicy('index', 'read_document', 'ask');
await host.connect('index', {
  resolveSecret: async () => 'synthetic-token',
  open: async () => ({
    verifiedPeerIdentity: 'test-service', // 测试替身；生产环境须真实认证。
    call: (request) => resource.execute(request, 'test-user'),
    close: async () => {},
  }),
});
const result = await host.call({ serverId: 'index', tool: 'read_document',
  args: { resource: 'doc-a' }, operationId: 'example-read-1',
}, { confirm: async () => true }); // 仅合成测试；真实适配器须取得有效批准。
console.log(result.status); // completed
await host.disconnect('index');
```

## Anti-Patterns

- 用一个 `enabled` 同时代表已安装、配置有效、连接正常和调用获准。
- 认为允许安装、选择目录或完成登录就允许全部工具、文件操作及数据外传。
- 把“敏感字段”标记、密钥字符串的存在或某个加密 API 成功当作全部安全属性的证明。
- 仅在请求开始时查权限，随后跨越确认窗口、异步准备和重连仍使用旧决定。
- 凭工具名称复用审批，忽略服务身份、配置、参数或代次已经改变。
- 把 `allowed_directories` 或“只读”注解当作 OS 沙箱或资源端强制授权。
- 把中断、连接关闭、超时或报错当作副作用未发生，直接重放写操作。
- 用静态客户端字节证明当前账户权限、真实运行时行为或整个服务端实现。

## 参考与证据合同

- [references/contract.md](references/contract.md)：实现或改造模型前阅读，定义可信适配器、状态语义、重试边界及生产环境缺口。
- [assets/boundary-model.mjs](assets/boundary-model.mjs)：原创、无依赖的局部状态模型；不包含目标产品实现，不是 MCP SDK、认证实现、加密实现或 OS 沙箱。
- [assets/boundary-model.test.mjs](assets/boundary-model.test.mjs)：Node 内置测试；只用合成输入和内存替身。
- [references/evidence.json](references/evidence.json)：历史证据摘录与官方来源字典。研究截点为 2026-10-14，静态对象为 Claude Desktop Linux 2.37337.1。X03/X10 启发配置与生命周期分离；X07 是有条件的安全存储失败路径观察；X11/X15/X16 支持权限边界的讨论。本文的失败关闭、代次栅栏和操作账本是原创工程选择，不宣称目标产品采用同一实现。

公开文档和静态观察只能支持其各自范围。`official_sources` 的日期是原研究检索日期；可变链接不是最新版本保证。接入真实 SDK 时重新核对所用规范版本与实现，不需要原始安装包或研究仓库即可使用本技能。
