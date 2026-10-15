# Security Guardrails · 原创无副作用实验

对应全书第 14 卷。68 个断言覆盖受限命令语法、参数合同、虚拟路径授权、一次性审批、URL 出口、展示合同与条件式敏感保存。

## 运行

无需安装依赖，使用 Node 20 或更高版本：

```sh
node --test guardrails.test.mjs
node demo.mjs
```

本次执行：68 passed，0 failed，0 skipped。测试和 demo 不导入 Claude、不执行 shell、不调用网络，也不读取或修改真实文件。所有文档、路径、URL 和秘密值都是合成数据。

## 文件

- `guardrails.mjs`：原创纯逻辑与内存模型
- `guardrails.test.mjs`：含反例与竞态状态的单元测试
- `demo.mjs`：可读的端到端虚拟演示

## 模型边界

| 模块 | 做什么 | 明确不做什么 |
|---|---|---|
| `tokenizeSimple` | 接受一个小型词法子集，不支持就拒绝 | 不模拟 Bash，不接任何真实 runner |
| `parseTeachingCommand` | 解释虚构 docstat/doccopy 的选项与操作数 | 不判断任意程序安全 |
| `VirtualFS` | 内存中的链接、路径分段、只读与保护根 | 不模拟真实 inode、硬链接、mount、Windows 或 OS 原子打开 |
| `buildPlan` | 分开源读取与目标写入，记录资源票据 | 不复制文件 |
| `createApprovalBoundary` | 精确计划、期限、一次性消费与上下文失效 | 不认证真实用户、不实现跨进程令牌 |
| `decideUrl` | 标准 URL 解析后进行教学导航决策 | 不请求 URL，不做 DNS、redirect、SSRF 或恶意站点判断 |
| `previewContract` | 区分文本、图片与交互展示合同 | 不解析/清洗/执行 HTML 或 SVG |
| `prepareSensitiveSave` | 可信 provider 不可用时阻止保存计划 | 不提供密码学，不落盘，不验证 provider 的真实实现 |

## 重要假设

1. grants、保护根、会话/策略版本及安全存储 adapter 由可信宿主持有。模型生成的同名字段不具有相同权力。
2. `trustedUiConfirm` 的函数引用只给经过认证的 UI 控制器，不能暴露给模型、文档或工具结果。`observeExternal` 返回的是资料，无法变成审批票据。
3. SHA-256 指纹用于绑定内容，不能认证批准者。这里的 token 是 Map 中的进程内对象身份，不能复制为 JSON 后当作线上凭证。
4. 虚拟文件系统的全局 revision 故意保守：任意链接修改都使旧票据过期。真实系统需要更细的资源身份及原子操作。
5. 审批先消费，再检查资源，任何失败都需要一个新的明确决定。消费票据不表示副作用发生，更不提供回滚。
6. 单元测试不能证明提示注入鲁棒性。它只证明外部文字不能绕过此模型的授权通道。
7. 原创保存策略选择 fail-closed，刻意不同于研究样本的部分未加密回退。`test-only` provider 只产生标记字符串，不是真正加密。

## 可继续做的练习

- 添加取消与执行并发的 fake runner，区分 not-started / committed / outcome-unknown。
- 设计精确批准某个 HTTPS 目的地的一次性计划，验证目的地和数据类别变化会失效。
- 用独立、自有临时环境实现平台 adapter，再验证实际资源操作；不要把本模型中的字符串检查直接接到高权限执行器。

这些练习是后续设计方向，不属于本次已实现和已验证的能力。
