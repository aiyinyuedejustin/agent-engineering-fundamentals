# 外置 Acorn：便携复验

本目录预期放在 optional-ast-channel/external-entry-validation/。先自行准备可信的 Node 和 Acorn 8.17.0 CommonJS 安装，再执行：

```sh
python3 -B verify-fixtures.py --acorn-module /absolute/path/to/trusted/acorn/dist/acorn.js
```

若复验器不在上述相邻位置，显式指定已发布工具目录：

```sh
python3 -B verify-fixtures.py \
  --tool-dir /absolute/path/to/optional-ast-channel \
  --acorn-module /absolute/path/to/trusted/acorn/dist/acorn.js
```

可用 --node /absolute/path/to/trusted/node 指定运行时。脚本只读取该工具目录的 tests/fixtures.json 并调用正式 ast_candidates.py；不会自行联网、安装、查找 npm 缓存或读取私有元数据。每个原创输入与报告写到临时目录，结束后自动清理；目标 JavaScript 只作为 parser 输入，不执行或导入。可信 parser 工具代码自身会被加载。

检查每例状态、退出码、category/key 多重集、外置依赖 source、testing_only=false、版本、解析器模块 SHA-256、报告 identity 摘要、输入大小及 SHA-256、零部分输出和 coverage 标志。成功输出 52 例、45 scanned、7 预期 scan-incomplete 的 JSON 摘要；失败退出非零。

这是既有 52 例的可复现重跑，不计为新的 52 项测试，也不是原 89 项整套回归的外置重跑。完整边界和本次来源验证见 REPORT.zh.md。
