# 可选 AST 候选通道：最小合同

## 输入与依赖

独立 CLI 一次读取一个调用方明确指定的 UTF-8 JavaScript 常规文件；不递归、不跟随最终符号链接、不运行或导入输入。原 Python 标准库工具箱保持不变。

发行依赖入口要求 `--acorn-module` 明确指向调用方信任、已安装的 Acorn 8.17.0 CommonJS `dist/acorn.js`，并核对包元数据和实际导出版本。版本/哈希只能标识依赖，不能代替可信安装来源。不会从目标目录自动寻找依赖，不下载或打包 Acorn 源码。

本机已有 Node 内置 Acorn 8.17.0，仅通过显式测试模式使用。该模式不是稳定公开依赖接口，输出标记 `testing_only=true`；不能冒充发行路径已被验证。固定 ECMAScript 2025，source type 必须明确为 `module` 或 `script`，不自动尝试更宽松语法、JSX/TS 插件或旧词法回退。

## 输出与兼容

独立 `original-ast-candidate-snapshot/v1`，固定 `analysis_kind=ast_syntax_candidate_inventory`、`semantic_completeness_proven=false`。保留输入 SHA-256、parser/运行时/适配器身份、限制、状态、诊断及候选原始字节位置。只输出候选，不输出 AST 或源码。

不写入或转换旧 `original-static-snapshot/v1`，不替换既有 `coverage` 或文件状态；词法与 AST 数量始终分别报告，禁止相加或重复称为新事实。AST `scanned` 仅表示在该通道预算内完成解析与声明的候选遍历，不证明运行时语义完整。

## 静态字面量范围

- 真实 `CallExpression`，callee 为直接标识符或非计算成员名，且原始拼写匹配既有默认规则；第一参数须为无转义引号字符串或无插值、无转义模板字面量。
- 默认名称长度 256；第二静态值仅保留既有允许的短字符串、布尔值、null、有限 JSON 风格数值。
- 动态名字、字符串拼接、转义名字、计算成员名、别名解析、绑定/可达性推断均不支持。
- 对象字面量普通 init 属性可形成无关联 schema marker 或 event-name 候选；方法、getter/setter、计算属性及类成员不当成普通对象字段。
- 遍历真实模板插值表达式中的 AST 节点；模板原文、普通字符串及正则正文永远不重新当代码解析。实际插值内调用可成为候选，但这属于 AST 独立通道的明确范围。

## 失败和预算

原有输入 64 MiB、token 1,000,000、候选 200,000 的数字上限不提高。AST token 与词法 token 的定义不同，不能把两者计数当同一测量。额外限制 AST 节点、树深度、输出字节、解析子进程的 V8 堆、CPU及墙钟时间；超限只允许收紧。

token 和节点限制在 parser 消费/创建过程中检查；遍历深度另做有界检查。所有失败整文件零候选、明确 `scan-incomplete`，无部分输出或降级成功。诊断只含白名单代码、计数和有界字节位置，不透传 parser 异常文本或 stderr。

输入只通过 stdin 送给原创 worker；不会作为 node 脚本参数或 eval/import/require 目标。Python 只终止自己创建的 Popen handle，清除 Node 启动注入环境变量，限制输出捕获和运行时长。V8 堆上限不是整个进程 RSS 沙箱，文档必须明确这个边界；不得宣称是对恶意依赖或操作系统的隔离。

## 验证和停止点

仅原创 fixture：五类已知词法误候选在 AST 通道均应消失，配套真实调用必须保留；覆盖 Unicode 字节位置、无执行哨兵、无效语法、预算、依赖缺失/版本错误、旧 schema 隔离。默认词法通道保持原行为，不声称已经修复它。

本轮不读取新的产品材料、不联网安装、不改 publication/git。若正式依赖路径无法在当前环境实测，明确列为未验证，不用内部 Acorn 替代成公开支持承诺。
