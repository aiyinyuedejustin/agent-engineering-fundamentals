# 预览协议模型的边界与适配合同

## 观察、工程选择与执行证明

references/evidence.json 保留 2026-10-14 对 Claude Desktop Linux 2.37337.1 选定客户端代码的静态观察，未执行目标应用或 renderer：

- W05–W06：选定富内容路径使用配置的 renderer URL；窗口握手核对来源与具体 iframe，再转移 MessageChannel。端口消息不提供相同的 origin 字段。
- W07、W10、W12：可见 schema、速率、重复请求与 capability 检查；内容序号和 acknowledgement 参与防止旧收据继承新状态。协议方法存在不代表每个调用方都实现或允许它。
- W09：所检通用 sendRequest 路径没有显式计时器，清理也未明显结算所有挂起请求。这里的统一 deadline 和销毁结算是原创改进，不声称原产品已实现。
- W17：截图路径还检查 capture-only、credentialless、私有资料接触状态及图像结果。截图不能证明完整隔离，也不替代执行权限判断。

证据中的文件名、哈希、短锚点是出处描述，不需要拥有原安装包才能使用模型。所有模型代码为原创教学实现。格式枚举包含 html/react/svg/mermaid 只是协议数据；模型没有相应渲染器。

## 隔离层先于通信层

模型拒绝 host 和 renderer 同源、通配、opaque 的 "null" 来源以及带路径的非规范 origin；它支持 HTTP 是为了本地开发，生产应按实际部署采用 HTTPS。构造器参数由可信宿主提供，不能从待预览内容读取。nonce 必须每代新建，示例固定值只能用于合成测试。

独立 origin 不自动提供无凭据运行：需检查 cookie 域、授权头、Service Worker、缓存、父页面引用、下载/弹窗/导航和网络权限。实际 sandbox/CSP 配置需要按所选浏览器与 renderer 功能验收。静态无脚本 sandbox 通常产生 opaque origin，不能直接改成通配消息授权来套用本模型。

窗口消息的认证依据是浏览器提供的 source 与 origin，不能信任 payload 自报身份。MessagePort 的能力来自受检查握手中转移的那个具体端口；转移后只接受当前端口，继续验证有界 schema、request ID、generation、sequence 与 method。模型不处理 frame 导航：真实宿主必须在 load、意外导航、替换、账户切换和退出时销毁旧通道并创建新 generation。

## 授权适配器与撤销

本例只有 read.text，且授权回调默认为拒绝。readText 与 authorize 是受信任宿主适配器，不提供给不可信内容。成功的内容 acknowledgement 只证明协议中收到匹配响应；恶意 renderer 可能撒谎，不能把它当成安全审查或真实像素已完成的证明。

入站 receipt 在任何 await 之前取得且被冻结。guard 检查会话仍 active、请求未超时/取消、内容 generation/sequence 未变。它不会替代外部资源 ACL、租户身份或组织策略。实际 readText 应在读取与交付前核对当前资源授权，并在策略撤销时销毁会话或使用自身的策略版本栅栏。不要仅在 authorize 开始时检查一次后长期缓存其结果。

handler 必须尊重 signal，且对可能产生副作用的步骤在提交前调用 context.guard() 并重新检查真实授权。即使 handler 忽略 signal，包装层也不会交付迟到结果；但模型无法停止该 handler、撤销其网络请求或回滚已经产生的副作用。示例只读内存资料，不演示外部写操作重试。

错误响应只允许模型定义的有限公共代码。任意异常文本及外部构造的未知 ProtocolError.code 都被归一为 HANDLER_FAILED。成功数据也需要专用结果 schema 与授权；本例只允许最多 65,536 个 UTF-16 code unit 的文本，不是字节预算或模型 token 限制。

## 有界状态与清理

每次内容替换使旧挂起 RPC 和能力工作失败；只有新内容的匹配成功响应才恢复 acknowledgement。每条请求都有 timer。协议 ID 在本代保留，达到 maxIds 后关闭；没有跨进程 exactly-once 保证。rate 限制收到的端口消息，maxPending 分别限制出站和入站并发，不等于浏览器总内存或 CPU 有界。

dispose 先让状态和收据失效，再结算握手与请求、取消能力工作和清理端口。关闭适配器抛错不会阻止 Promise 结算；但吞掉 close 异常不证明操作系统资源已经回收。真实宿主仍应确认 frame、worker、process 等资源实际销毁，必要时报告清理失败。

## 可复现检查

在此技能目录运行：

```sh
node --test scripts/sandbox-model.test.mjs
node scripts/demo.mjs
```

测试使用 Node 自带 MessageChannel 与合成窗口，覆盖严格握手、错误代次、旧批准、替换、迟到 handler、超时、销毁、去重、容量及错误脱敏。它没有 DOM、真实 iframe、CSP 执行、导航或资源隔离，因此不能得出浏览器安全验收已通过的结论。
