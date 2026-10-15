# 语法版本、节点预算与候选规则：18 个文件的对照

两种扫描器得到不同结果时，先核对输入、语法版本、候选规则与资源预算。这四个条件决定结果能比较到哪一层。

## 结果

18 个文件、12,585,540 字节，解析前全部核对了原诊断与已验证提取记录的 SHA-256/大小。每文件只按原适配器固定参数解析一次：**15 `scanned`、3 `scan-incomplete`，AST 候选总数 0**。

这不是“修复了 15 个原 scanner 缺口”。15 个成功仅表示独立 AST 通道在声明范围与预算内完成语法解析/候选遍历；词法仍为原先的 18 个 `scan-incomplete`。未回写或重算原 coverage，没有把 AST 数量和词法数量合并。

零候选只描述该固定规则的观察结果。规则要求匹配配置中的调用/成员拼写及受限静态字面量，或指定对象字段；不恢复别名、动态名字、数据流、绑定或可达性。不能据此说这些文件没有相关功能，更不能把语法成功当作语义完整。

## 保留的三项拒绝

| 案例 | 字节数 | 原词法拒绝 | AST 拒绝 | 有界观察 |
|---|---:|---|---|---|
| case-07 | 61,626 | 字符串/模板状态末尾未闭合 | `ast-syntax-rejected` | 字节 30,328；8,906 token；未开始 AST 遍历 |
| case-17 | 3,572,661 | 原 1,000,000-token 上限 | `ast-node-bound-exceeded` | 第 200,001 次节点创建尝试被拒绝；270,096 AST token |
| case-18 | 7,288,531 | 原 1,000,000-token 上限 | `ast-node-bound-exceeded` | 第 200,001 次节点创建尝试被拒绝；265,885 AST token |

两个大文件先触发独立的 200,000 节点上限，属于预期的资源拒绝。没有提升节点/token/时间/内存等预算，没有保留部分候选，也没有针对真实文件重试。Acorn 与词法 token 定义不同，上表不是同一计量的提升比例。

### 单个语法条件的独立定位

case-07 的停止位置落在 `await using` 声明内。先前 Node v24.19.0 的 syntax-only 检查本身就明确使用 `module` 并接受，因此不能把这次拒绝简单归因于损坏文件或 CommonJS 包装。

对一个新写的最小例分别检查：同一 Acorn 8.17.0 在 ECMAScript 2025 下，`module` / `script` 都拒绝；只对这个原创例设置 2026 后，两者接受。证据支持首次观察边界是适配器固定 `ecmaVersion=2025` 的显式资源管理语法范围，而非 module/script 差异。

真实文件没有用更宽参数重新解析。case-07 仍保留原 `scan-incomplete`；不能推导整份真实文件在 2026 下一定接受。固定条件、字节位置与原创探针结果分别见 [SYNTAX-CONDITION.json](SYNTAX-CONDITION.json) 和 [SYNTAX-SYNTHETIC.json](SYNTAX-SYNTHETIC.json)，不含原源码、标识符或异常原文。

## 固定执行合同

- 原创适配器与已审查 SHA-256 一致，默认预算完全不变。
- 输入 64 MiB；Acorn token 1,000,000；节点 200,000；深度 64；记录 200,000；最终输出 8 MiB；子进程墙钟 15 秒/CPU 10 秒；V8 old-space 128 MiB。
- 所有真实文件固定 `source_type=module`、ECMAScript 2025，禁止回退、自动换语法或重试。
- 仅使用现有 Node 内部 Acorn 8.17.0，明确 `testing_only=true`。**没有完成正式外置 Acorn 成功路径验证。**
- 原目标字节仅送 parser，不执行、不导入、不解析目标依赖；没有访问或重试失败的 Mac/Windows 材料。
- V8 old-space 限制不是总 RSS/操作系统安全沙箱；静态候选不证明运行时语义。

## 元数据与隐私

[AGGREGATE.json](AGGREGATE.json) 按 18 个匿名案例给出输入 SHA-256、大小、原拒绝类别、AST 状态/固定诊断/计数与私有报告哈希。[PREFLIGHT.json](PREFLIGHT.json) 记录解析前身份核对、工具身份与预算。

本目录仅收录聚合元数据，原始 AST 报告和输入路径映射不随书发布。所有结果固定 `semantic_completeness_proven=false`。
