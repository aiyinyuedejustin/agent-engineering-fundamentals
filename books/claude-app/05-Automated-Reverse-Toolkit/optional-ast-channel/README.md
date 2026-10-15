# 可选 AST 候选通道（独立实验交付）

这是与原标准库词法工具箱分开的 opt-in 静态通道。它用 Acorn 的实际语法节点识别候选，在原创回归中排除了五类模板/正则误候选。它不改变旧工具箱、旧快照、预算、文件状态或 coverage；两个通道的候选数量不能相加。

`semantic_completeness_proven` 永远是 `false`。语法上真实的调用仍可能是局部同名函数、不可达代码、无关对象成员或仅用于测试的文本代码。这里没有名称绑定、别名/数据流恢复、可达性或运行时功能证明。

## 文件与入口

- [设计合同](DESIGN.zh.md)：输入、输出、范围与失败边界。
- `ast_candidates.py`：Python 标准库启动器与 CLI。
- `ast_worker.cjs`：原创 Acorn 静态适配器。
- `tests/fixtures.json`：[52 个原创 fixture](tests/FIXTURE-NOTES.md)。
- `tests/test_ast_channel.py`、`run_tests.py`：离线测试。
- [独立审查](INDEPENDENT-REVIEW.md)、[验证报告](REPORT.zh.md)。

## 正式依赖入口

调用方需要事先拥有并信任 Node，以及 **Acorn 8.17.0** 的 CommonJS 安装。模块必须位于该包的 `dist/acorn.js`，包根的 `package.json` 须声明 `name=acorn`、`version=8.17.0`、`main=dist/acorn.js`。该依赖来自调用方的工具环境，不能来自被分析的目标文件或未知目标目录。

```sh
python3 -B ast_candidates.py \
  --input ./original-synthetic.js \
  --source-type module \
  --node /absolute/path/to/trusted/node \
  --acorn-module /absolute/path/to/trusted/acorn/dist/acorn.js \
  > ast-candidates.private.json
```

这些路径是占位符，需要替换。`--node` 可省略，使用调用方 PATH 中的 Node。没有自动安装、自动依赖发现、插件、模块解析回退或内部 Acorn 回退。包元数据（最多 64 KiB）与模块（最多 2 MiB）同样要求常规单链接文件；带最终符号链接/硬链接的安装布局会拒绝，不自动放宽。版本与 SHA-256 只标识依赖，不能认证其安全来源。依赖代码会作为工具被加载；目标字节只传入 parser，不执行、导入、require、构建或解析目标依赖。

当前环境没有独立安装的官方 Acorn 包，因此**正式外置依赖的成功路径尚未实测**。错误版本/包布局/元数据与导出版本拒绝已测试；这些拒绝测试不冒充成功兼容证明。

## 仅测试的现有依赖

本次验证使用现有 Node v24.19.0 内部的 Acorn 8.17.0，无下载、无第三方源码副本。内部模块不是稳定公开接口，只能用明确的测试开关访问：

```sh
python3 -B ast_candidates.py --input ./original-synthetic.js \
  --source-type module --test-node-bundled-acorn
python3 -B run_tests.py
```

输出固定标记 `policy.dependency.testing_only=true`。内部模块不存在或版本不同就显式失败。它不是生产依赖替代方案；测试模式成功不代表正式依赖入口已验证。测试只解析原创字节，既不执行 fixture JavaScript，也不读取产品文件。

## 范围与输出

一次只读一个显式指定的常规单链接 UTF-8 文件，不递归、不跟随最终符号链接。必须选 `module` 或 `script`；固定 ECMAScript 2025，不自动切换 source type，不接受 JSX/TypeScript 插件。

- 规则固定为原工具箱默认调用拼写及对象字段拼写，不支持任意扩展配置。
- 名称仅取无转义字符串或无插值、无转义模板字面量，最多 256 个 Unicode code point。
- 第一参数之外仅保留短字符串、布尔值、null、有限十进制数值；负数的 UnaryExpression、十六进制、BigInt、动态表达式不提取为第二静态值。不会求值。
- 普通对象 init 属性可成为未关联的 schema marker/event 字段候选。计算属性、方法、访问器、shorthand 及类成员不伪装成这些属性。
- 模板原文/字符串/正则正文不重扫为代码。真实模板插值表达式中的调用会被遍历，属于本通道独立的声明范围。

CLI 只写一行 UTF-8 JSON，退出 0 表示 `scanned`，退出 2 表示 `scan-incomplete`。参数用法错误由 argparse 退出 2。任何解析、预算或依赖失败均清空该输入的全部候选，不保留部分结果。

独立 schema 为 `original-ast-candidate-snapshot/v1`；`analysis_kind=ast_syntax_candidate_inventory`。`coverage.complete_within_ast_declared_scope` 只表示本通道解析及受限候选遍历完成，不能据此推导完整语义。它没有被写回旧 schema。

候选 `source.byte_start` / `byte_end` 是原 UTF-8 字节的零基半开区间，包含整个名称字面量的引号/反引号。对象 identifier 字段则覆盖字段标识符。`source.line` 从 1 开始，按 ECMAScript LF、CR、CRLF、U+2028、U+2029 计行。parser UTF-16 位置经过显式转换；中文、emoji 与 BOM 有回归。诊断 `byte_offset` 也是原始字节单位，只代表停止/拒绝位置。

读取前失败的输入身份为 `identity_available=false`，大小与哈希为 null；不伪称是空文件。可用输入有 SHA-256。`identity.channel_sha256` 对移除 identity 字段后的规范紧凑 JSON 加 LF 的 UTF-8 字节计算 SHA-256；运行时/依赖/策略都纳入身份。它标识本次候选报告，不是安全或完整性证明。

输出会包含名称字面量，可能涉及私有信息。对真实材料生成的快照应留在私有工作区，不随此原创工具发布。

## 预算与拒绝

| 限制 | 默认 |
|---|---:|
| 原输入字节 | 64 MiB |
| parser token（不含 EOF） | 1,000,000 |
| 节点分配/遍历 | 200,000 |
| AST 深度（Program 为 0） | 64 |
| 候选记录 | 200,000 |
| 最终紧凑 JSON（含 identity 与 LF） | 8 MiB |
| 子进程墙钟/CPU | 15 / 10 秒 |
| V8 old space | 128 MiB |

原有数字上限没有提高，但 Acorn token 定义不同于原词法 token，不能直接混算。Python API 只允许收紧限制，CLI 不提供提限开关。Acorn 节点创建包含 startNode、startNodeAt、copyNode 三个入口；遍历有额外节点与深度检查。深度是解析后的限制，解析期递归错误也显式拒绝。

启动器要求 POSIX resource 支持，清除子进程环境，限制 stderr 捕获为 64 KiB；只终止自己创建的 Popen handle。CPU/进程被终止时可能只能给出固定的 `ast-worker-resource-or-process-failed`，不会猜测具体原因或回显 stderr。

V8 old space、输入/输出字节和 CPU/墙钟限制**不是整个进程 RSS 或操作系统安全沙箱**。没有防御恶意 parser 依赖的隔离承诺。可信工具安装应在扫描期间保持静止；元数据/哈希检查并不提供对并发恶意替换的原子认证。

## 与词法结果交叉核验

1. 保留两个原始报告及各自策略身份，先核验两者输入字节 SHA-256 相同。
2. 分别记录词法状态/候选计数与 AST 状态/候选计数，不能把 AST 成功改写为旧 coverage 成功。
3. 根据候选类别、键、各自锚点定义比对语法形态。两种锚点范围未必相同，不可只按 offset 相等连接。
4. 区分“语法形态确认”“词法假影”“未解决”。AST 失败或无匹配也不能自动证明旧候选错误；静态范围、规则和预算差异都需考虑。
5. 即使两个通道一致，也仍然只是候选。AST 新观察不称为新增功能事实。

本交付不提供合并计数或自动改写旧快照的捷径。旧词法五项已知局限仍然存在；此处的绿色测试仅说明独立 AST 合同上的原创例子满足预期。

## 固定版本的真实输入对照

[18个文件的独立对照](linux-gap-crosscheck/REPORT.zh.md)展示语法版本与节点预算如何改变拒绝原因：15个文件完成AST声明范围检查，3个保持拒绝，候选总数为0；原词法coverage未变。这里只使用明确标记的测试依赖，不替代正式外置依赖验证。
