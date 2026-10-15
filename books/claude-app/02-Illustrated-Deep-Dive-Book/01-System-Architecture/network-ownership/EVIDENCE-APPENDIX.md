# 网络分层：样本与定位

[evidence.json](evidence.json) 保存 39 个短锚点、文件 SHA-256 和 UTF-8 字节位置；7 个成员逐字节比对已校验 ASAR。短锚点用于定位，不附带长段 bundle 或完整内置 prompt。

REA 6.5.0 本轮以 fail integrity policy 分析 3 个选择成员，未报告完整性矛盾，但主 chunk 在 512 MiB heap 预算下未完成语义分析。[REA 摘要](rea-summary.json) 明确保留此限制。上面调用链来自人工有界静态阅读与字节锚点验证，不能称为 REA 已证明的完整调用图。没有扩大预算或执行目标来掩盖覆盖缺口。

当前 Electron 文档用于解释 API 概念；样本的实际部署、开关取值、代理/证书配置与 OS socket 进程归属需由对应运行环境确认。目标代码仅作静态文本读取，没有执行。

[返回网络分层正文](README.md)
