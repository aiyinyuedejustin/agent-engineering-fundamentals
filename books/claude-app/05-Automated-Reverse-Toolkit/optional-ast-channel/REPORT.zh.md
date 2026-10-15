# 可选 AST 通道：候选验证报告

## 结论

独立原型已实现，89/89 项原创测试通过，独立审查额外 36 项断言通过。只使用已存在的 Node v24.19.0 内部 Acorn 8.17.0，并显式标为测试依赖；未下载依赖、未打包第三方源码、未执行目标 JavaScript。

正式 CLI 要求调用方显式提供可信已安装 Acorn 8.17.0 的 `dist/acorn.js`。本环境没有该独立安装，因此正式依赖成功路径仍是**尚未验证的发布前门槛**。本交付是单独 staging 原型，没有修改 publication 或 Git。

## 候选结果

52 个原创 fixture 中，45 个完成 AST 候选扫描，7 个坏语法/JSX/TypeScript 输入明确 `scan-incomplete`、零部分候选。五类已知误候选均在原词法通道各重现 1 个，在独立 AST 通道各为 0：

1. 嵌套模板原始文字。
2. 字符串 `return` 干扰除法/正则边界。
3. 箭头后正则正文。
4. 逻辑与后正则正文。
5. 控制语句头部后正则正文。

每类都另有后续真实调用的正控制；真实模板插值表达式内调用也保留。计数分开保存于 [SYNTHETIC-CROSSCHECK.json](SYNTHETIC-CROSSCHECK.json)，不相加，不改写词法 coverage。**旧词法局限仍未修复**；这里的成功仅属于独立 AST 通道的声明合同。

没有把 AST 成功解释为语义完整。局部同名函数、不可达调用、无关对象同名成员仍能形成候选；无绑定/可达性分析，schema marker 也没有自动关联为真实契约。

## 边界验证

- 真实 1,000,000-token 输入接受，第 1,000,001 个 token 明确拒绝；没有提高默认上限。
- 节点创建及 shorthand copy、遍历深度、记录、最终 JSON 输出均有有界拒绝。
- 20,000 个原创调用的实际 CLI 输出为 6,527,258 字节，小于 8 MiB；输出预算包含 identity 与末尾 LF。
- 非 UTF-8、BOM、中文/emoji、六类换行组合、非法文件名和源名、依赖异常/版本、协议损坏均测试。
- 文件写入哨兵不出现；静态和动态 import 语法不解析目标依赖。
- 子进程 CPU、墙钟、stdout、stderr 有界拒绝，仅回收自己创建的 handle。

独立审查发现的节点计数、最终编码预算、异常归一化与行号问题已修复并按最终哈希复核。完整结论与仍存在的边界见 [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md)。V8 old-space 限制不是总 RSS/操作系统隔离；可信依赖代码本身需要执行，安装来源与静止性由调用方负责。

## 复核命令

在本目录执行：

```sh
python3 -B run_tests.py
sha256sum -c MANIFEST.sha256
```

从任意工作目录也可把 `run_tests.py` 换成其绝对路径。正式 CLI / 测试模式示例及输入、输出、字节单位合同见 [README.md](README.md)。测试默认不需要词法工具箱或产品材料。

[SYNTHETIC-CROSSCHECK.json](SYNTHETIC-CROSSCHECK.json) 是额外的五项对照记录：从 `tests/fixtures.json` 选择 `trap-` 前缀案例，分别调用原工具箱 `literal_candidates(data, load_rules())` 与本通道 `analyze_bytes(data, test_node_bundled=True)`；在相同字节 SHA-256 下分别记录候选计数。对照只读原创工具与原创字节。

机器摘要见 [VALIDATION.json](VALIDATION.json)。本轮没有读取新产品输入，因而不为真实 Linux 文件重算 AST 覆盖，也不声称原先 18 个拒绝已经解决。
