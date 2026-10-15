# 正式外置 Acorn 入口验证

## 结论

PASS，限于固定 Acorn 8.17.0、Node v24.19.0、Python 3.12.14、Linux/POSIX 的本次原创输入验证。正式 CLI 的外置依赖成功路径现已实测，输出 dependency.source=explicit-installed-acorn、testing_only=false。原始适配器、固定 ECMAScript 2025、预算与拒绝检查均未改动；不再需要用 Node 内部模块推代这项成功路径。

52 个既有原创 fixture 全部通过正式 CLI：45 scanned，7 按预期 scan-incomplete 且零候选。另 8 个 CLI 场景及 7 个收紧预算的 Python API 探针通过；总计 60 个正式 CLI、7 个 API 检查（不含单独 smoke）。这些不是原有 89 项测试套件的外置模式重跑，不能写作“89/89 外置验证”。

## 来源与锁定

先查询官方 https://registry.npmjs.org/acorn/8.17.0 ，核对 name、version、main、tarball、SHA-512 integrity 和无生产依赖；再在隔离工作目录执行 npm install --ignore-scripts --save-exact --no-audit --no-fund --registry=https://registry.npmjs.org/ --cache=./npm-cache。npm 报告 added 1 package，退出 0。未全局安装，不执行 lifecycle scripts，不安装目标依赖。

package.json 精确锁定 acorn=8.17.0；package-lock.json v3 仅含项目根与 acorn，无传递依赖。缓存 tarball 的 SHA-512 独立重算，与官方元数据及锁文件一致；已安装 package.json 和 dist/acorn.js 与这个验证过的 tarball 对应成员逐字节相同。该来源核验不等于恶意代码审计、签名验证或操作系统隔离。

正式加载的 dist/acorn.js SHA-256：b373ccd10e9deb63654289f73216eeefcaf0405d9ee24289aabf596b91b4c318。

## 已核验行为

- 原创 fixture 的状态与候选多重集逐项匹配；五类词法陷阱没有 AST 误候选，对应真实调用保留。
- 每份报告都核验输入摘要、外置依赖身份、testing_only=false、semantic_completeness_proven=false、legacy_coverage_modified=false，以及规范 JSON 报告身份摘要。
- 正式 CLI 从不同于工具目录的工作目录启动，检查退出码和空 stderr，JSON 编码与原入口编码一致。
- 静态与动态 import 指向不存在的原创模块仍扫描成功；含文件写入、process.exit、throw 的目标文本只作解析，哨兵文件未产生。
- module 和 script 的显式成功/拒绝路径、ECMAScript 2025 对 await using 的拒绝、BOM/中文/emoji/CRLF 字节锚点均核验。
- 20,000 个原创调用完整输出；精确 1,000,000-token 输入通过，第 1,000,001 token 整文件拒绝。
- 收紧 token、shorthand 节点计数、深度、记录、输出预算的 API 探针通过。没有提高预算。

## 边界

本次只解析原创合成文本，未再次解析 Linux 产品文件，没有新增读取 Mac/Windows/其他大包。历史 Linux 18 文件对照仍是内部测试依赖结果；不能因本次外置成功而改写那次报告的 testing_only 标记、状态或 coverage。原词法已知局限、两通道计数不可相加、语义完整性未证明等限制全部保留。

仅确认这个精确版本、CommonJS dist/acorn.js 常规单链接安装布局；不宣称 Acorn 其他版本、ESM 布局、符号链接/硬链接布局、其他 Node/Python 版本或其他平台已测。可信 parser 工具代码会被执行，目标 JavaScript 不执行、不导入、不构建、不解析其依赖。V8 old-space 限制不等于总 RSS 或系统沙箱。

## 交付与复现

本目录只含原创验证摘要、便携复验脚本与说明、原创 package.json 配置和生成的锁文件，不包含 node_modules、第三方源码、npm 缓存或产品文本。第三方包必须由复核者从上述官方 registry 独立获取；在新的独立工具目录使用所附配置与锁文件执行 npm ci --ignore-scripts --no-audit --no-fund --registry=https://registry.npmjs.org/，再把该目录下 node_modules/acorn/dist/acorn.js 的绝对路径显式传给正式 CLI。

该说明只提供复现步骤；本次实际安装命令是上文 npm install，不声称已另跑 npm ci。实现哈希与逐例结果见 [验证记录](VALIDATION.json)，交叉核验见 [独立复核](INDEPENDENT-REVIEW.zh.md)。所附配置及锁文件用于独立工具环境复现；不要将目标项目依赖作为解析器工具依赖。

便携复验入口见 [运行说明](README.md) 和 [verify-fixtures.py](verify-fixtures.py)。该脚本已用现有官方外置包成功重跑同一52例（45 scanned、7预期拒绝）；不增加不同测试总数。
