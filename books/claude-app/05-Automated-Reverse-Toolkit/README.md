# 自动化静态逆向工具箱

一个可复用、离线、Python 标准库优先的入口：**目录/受限 ZIP/受限 ASAR → 静态快照 → CSS token 与色阶候选 → 旗标、工具契约、遥测字面量候选 → 两版本 JSON + 中文 Markdown 差分**。

这是原创研究工具，不是 Claude 官方 SDK、产品运行时，也不是完整反编译器。不下载产品、不运行安装器、不执行被分析的代码。交付只包含原创工具与合成测试，未附安装包、产品 bundle、字体或完整源码。

> 候选边界：本工具输出静态候选清单，不证明 JavaScript 语义完整。

## 一条命令先跑通

环境：Python 3.10+。不需要 pip、npm、网络或产品文件。进入本目录后执行；Windows 可将 `python3` 改为 `python`：

```sh
python3 -B reverse_toolkit.py compare --old tests/fixtures/v1 --new tests/fixtures/v2 --old-label synthetic-v1 --new-label synthetic-v2 --output private-output
```

打开 `private-output/diff.md`。同目录还会产生：

- `before.json`：旧目录快照
- `after.json`：新目录快照
- `diff.json`：完整机器可读差分，包括来源定位、覆盖警告和待核候选
- `diff.md`：中文可读差分，保留旧值、新值和来源

输出必须是**尚不存在的新目录**，父目录必须存在。重复运行请换输出名；工具不会覆盖旧证据。`private-output/`、`private-version-output/` 和 `private-directory-diff/` 已加入忽略规则，但这不是隐私保护或发布审查的替代品。

本合成例子会展示 1 个 token 新增、1 个移除、1 个值变化，1 个新旗标候选、2 个旗标值变化候选，以及契约摘要和遥测字面量变化。这里的 `demo_*` 全是原创测试名字，与产品功能无关。

## 真正一条命令：两个本地版本 → 私有解包 + 快照 + 差分

`diff-versions.py` 把准备 ZIP/ASAR 输入和生成差分合成一次调用。旧、新输入各自可以是已经解包的目录，或满足安全子集的本地 ZIP/ASAR；这些类型可以混用。ASAR 默认拒绝外置 companion；可通过 `--old-unpacked-dir` / `--new-unpacked-dir` 显式指定并严格核验精确配套目录。链接始终拒绝，先用 `inspect-asar` 查看容器声明与覆盖缺口。脚本应与 `reverse_toolkit.py`、`toolkit/` 放在同一目录。

```sh
python3 -B diff-versions.py "/path/to/old.zip" "/path/to/new.zip" --output "/path/to/private/private-version-output"
```

直接比较目录也一样：

```sh
python3 -B diff-versions.py tests/fixtures/v1 tests/fixtures/v2 --old-label synthetic-v1 --new-label synthetic-v2 --output private-directory-diff
```

打开 `private-directory-diff/report/diff.md`。ZIP 示例打开 `/path/to/private/private-version-output/report/diff.md`；实际输出路径以 `--output` 为准。ZIP 示例输出结构：

```text
private-version-output/
  inputs/
    old/            # 只有旧输入为 ZIP/ASAR 时存在；保留私有解包内容
    new/            # 只有新输入为 ZIP/ASAR 时存在；保留私有解包内容
  report/
    before.json
    after.json
    diff.json
    diff.md
  run.json          # 输入适配器、容器 SHA-256、固定上限和相对输出路径
```

- 原目录只读，不会复制进输出。ZIP 通过原工具箱的 `safeio.extract_zip` 提取，随后调用同一套 `snapshot`、`diff_snapshots` 和报告写入逻辑；没有另一套扫描器。相同目录布局、字节、标签与规则下，目录和 ZIP 入口的四个报告文件字节相同。ZIP 带有额外顶层目录时不会自动剥掉它；先保证两版本输入范围一致。
- `.asar` 常规文件选择受限 ASAR 字节适配器，其余常规文件选择受限 ZIP 适配器；扩展名不证明格式有效。ASAR 支持精确共享字节范围并逐份计入总量，拒绝部分重叠和链接；外置 companion 默认拒绝，仅支持显式精确配套合同；只读 `inspect-asar` 明确列出排除项，绝不把缺失内容当成删功能。完整约定见 [SUPPORT.md](SUPPORT.md)。**此默认入口不接收 DMG、DEB、RPM、7z、TAR 或原生安装器**；DEB 的显式 ASAR 投影使用下方专用入口，其他包装请先自行使用受信任工具得到目录。脚本不下载、不运行安装器、REA、包管理器、命令行工具或输入中的程序，不自动递归解包。
- 固定使用审计版 `Limits()` 默认值：档案 256 MiB、central directory 16 MiB、20,000 条目、单文件 64 MiB、总量 512 MiB、深度 64、压缩比 200:1、清单记录 200,000。各输入分别受这些上限约束；此入口不提供提高容量的开关。可选 `--rules /path/to/rules.json` 使用同一套有界字面量规则验证；标签通过 `--old-label`、`--new-label` 指定，仍未认证。
- `--output` 必须尚不存在，父目录必须已经存在，且输出不能在任一输入目录内，包括通过父目录符号链接指向输入的情况。不会覆盖旧输出或跟随输入根部、输出末尾的符号链接。输入内部链接沿用原扫描器的跳过与覆盖警告策略。
- 先在输出父目录内创建私有暂存目录，所有提取、快照、差分及元数据成功后，才以原子不替换操作交付完整输出。报告目录也使用相同操作；若目标中途出现，会保留那个路径并撤销本次暂存。普通异常、解析失败或可捕获的中断会清理本次暂存。`SIGKILL`、断电或清理本身失败可能留下 `.diff-versions-*` 私有暂存，需要人工检查，不要误当成功结果。
- POSIX 下外层运行目录、输入父目录、各 ZIP 解包根、报告目录为 `0700`，输出报告和提取文件为 `0600`；解包中的更深目录受私有根目录隔离。Windows 等系统的权限保障取决于文件系统/ACL，仍须选择自己的私有工作目录。原子不替换交付在 Linux 已验证；macOS/Windows 有对应代码但尚未原生执行，不支持的主机或文件系统会拒绝交付。请使用静止、隔离的输入与输出父目录；这不是抵御其他进程同时替换祖先路径的安全沙箱。独立 `unpack-zip` 仍使用原有交付实现，要求父目录静止；详见 [支持约定](SUPPORT.md)。
- **整个输出都应保持私有**：`inputs/` 含原始解包材料，`report/` 也可能包含产品路径、配置名、字面量或契约摘要。不要将此输出作为公开示例或测试 fixture，不要直接复制进发布目录；忽略规则不能替代权限保护和人工发布审查。这里提供的测试只动态生成原创合成输入。

成功退出码为 `0`，标准输出是一行 JSON，包含报告路径与覆盖警告；失败为 `2`，诊断写入标准错误。静态覆盖缺口仍可能产生成功报告，但会保留在 `warnings` 与快照 `coverage` 中。新出现旗标、工具契约或遥测候选的解释边界与原工具箱完全相同。

验证新入口及原有测试：

```sh
python3 -B run_tests.py
```


## Linux DEB：直接比较指定的应用资源

[DEB 专用入口](DEB-PROJECTION.md)将两个本地包中的指定 ASAR 与精确 companion 投影到私有目录，核验后复用同一套扫描与差分。以下路径来自已验证的 Linux 2.37337.1；新版本改变布局时会拒绝，不会猜测替代文件。

```sh
python3 -B deb_versions.py compare /private/old.deb /private/new.deb --asar-member usr/lib/claude-desktop/resources/app.asar --companion-prefix usr/lib/claude-desktop/resources/app.asar.unpacked --platform-label linux-amd64 --output /private/new-deb-comparison
```

打开 `/private/new-deb-comparison/diff.md`，详细候选见 `diff.json`。这是显式范围投影：包内非选区内容只清点，不当作应用功能差分。外层每遍完整解码预算为768 MiB，原ASAR单文件64 MiB、逻辑总量512 MiB不变；完整格式、两遍事务和磁盘预算见[专用支持说明](DEB-PROJECTION.md)。首次可用 `inspect` 检查外层结构，inspect不替代内层声明完整性核验。

## 用你有权读取的本地版本

把旧、新版本分别准备为静止的、已经解包的目录。两个目录应采用一致的范围，例如都只包含应用 `resources`，或都只包含已经展开的 `app.asar` 内容。**不能拿一个完整安装包与另一个单文件 bundle 的缺失差异解释为产品删功能。**

```sh
python3 -B reverse_toolkit.py compare \
  --old "/path/to/old-unpacked-resources" \
  --new "/path/to/new-unpacked-resources" \
  --old-label "platform-build-old" \
  --new-label "platform-build-new" \
  --output "/path/to/private/new-comparison"
```

输出必须在所有输入目录之外。版本名只是调用者标签；工具不会认证发布渠道、平台、签名或版本号。它记录文件 SHA-256、扫描策略摘要和快照摘要，方便之后复核。SHA-256 检验能发现意外改动，**不是数字签名，也不认证输入清单的作者**。读入快照还会检查用于差分的字段类型、来源文件摘要与字节范围；重新计算摘要不代表清单可信。

如果只想先保存一个版本：

```sh
python3 -B reverse_toolkit.py snapshot --input "/path/to/unpacked" --label "my-local-build" --output "/path/to/private/snapshot.json"
python3 -B reverse_toolkit.py diff --old-snapshot "/path/to/private/old.json" --new-snapshot "/path/to/private/new.json" --output "/path/to/private/new-diff"
```

没有隐式下载、嵌套解包、source map 展开、目标导入、`eval`、动态代码执行或远程页面访问。输入可以包含脚本，分析器只读取字节。

## 明确支持哪些包装

| 输入 | 内置能力 | 不应推导的能力 |
|---|---|---|
| 已解包目录 | 受限遍历、文件哈希、选定文本扩展名扫描 | 不证明来自完整/真实安装包 |
| 普通 ZIP | `unpack-zip`，仅 stored/deflated、非加密、非 ZIP64、单卷 | 不支持所有 ZIP 变体或所有安装器 |
| MSIX/AppX/APK 等 ZIP 容器 | 只有满足上述 ZIP 子集时，按普通字节容器提取 | 不验证平台签名、安装语义或应用行为 |
| ASAR | `inspect-asar` 只读检查；`unpack-asar` 提取严格子集；精确共享范围逐份复制 | 链接一律拒绝，外置 companion 需显式选择并完整核验；不认证发布方，见 [支持约定](SUPPORT.md) |
| DEB（严格 GNU TAR / XZ 子集） | [`deb_versions.py`](DEB-PROJECTION.md) 显式选定 ASAR 与完整 companion 后核验、扫描、差分 | 不做整包提取，不安装、不自动选区；新外层预算与原 ASAR 预算分别约束 |
| DMG、RPM、7z、TAR、原生可执行文件 | **没有内置解包器**；自行用受信任工具得到目录后传入 | 不把扩展名当格式检测，不宣称跨平台解包 |

受限 ZIP 命令：

```sh
python3 -B reverse_toolkit.py unpack-zip --input "/path/to/local-input.zip" --output "/path/to/private/new-unpacked-directory"
```

输出目录必须不存在。提取前检查所有成员，再写入权限受限的临时目录；CRC、实际大小或写入失败会撤销临时目录。成功后才交付新目录。检查实际 central-directory 条目数与每个本地头（包含目录条目），完整消费 stored/deflated 数据流并验证结束标记、实际长度和 CRC；不依赖 ZIP 库按声明长度截断的读取视图。文件不恢复可执行权限。

默认上限：压缩档案 256 MiB，central directory 16 MiB，20,000 个条目，单文件 64 MiB，总展开量 512 MiB，路径深度 64，单成员压缩比 200:1。拒绝绝对路径、`..`、反斜杠、盘符/alternate data stream、控制字符、特殊设备名、末尾点/空格、重复路径、大小写/Unicode 同名冲突（包括隐式父目录）、文件与目录冲突、符号链接及其他特殊文件。ZIP64、多卷、加密、BZIP2/LZMA 压缩、异常 central directory 都明确拒绝。

目录扫描采用相同的单文件、总字节和条目上限；条目数包含目录和被跳过的链接。符号链接、硬链接和特殊文件不跟随；超大文件保留跳过记录，导致覆盖不完整。总字节、深度、条目或记录上限超出则失败，不写出成功报告。扫描过程检查常见的文件更换/长度变化，但**不是抵御另一个进程恶意同时替换祖先目录的安全沙箱**。请在隔离工作区、静止副本中分析不可信输入；输出父目录也应由当前用户独占，不能由其他进程同时改动。

可显式改变前三项业务容量；新值写入扫描策略，影响可比性：

```sh
python3 -B reverse_toolkit.py snapshot --input "/path/to/unpacked" --label "bounded-run" --output "/path/to/private/snapshot.json" --max-file-mib 96 --max-total-mib 768 --max-files 30000
```

增大容量会增加内存、磁盘和时间风险。默认防护不是压缩格式解析器的完整安全审计。

## 实际扫描了什么

### CSS tokens / palettes

- 扫描 `.css`，保留 custom property 名称、**原始声明值**、选择器、父级 `@media`/`@layer` 等块上下文。
- 来源是文件相对路径、SHA-256、从 0 开始且右端不包含的 UTF-8 **字节**范围、行号。
- `css_palettes` 是 `css_tokens` 的一个候选子集：名称类似带数字的色阶，或声明值出现受识别的颜色表达式。
- 保留 `var(...)`、`oklch(...)` 等原始表达式；不自行猜测未解析值。不等价于浏览器 computed style、颜色空间转换、最终色值、有效 CSS 或完整色表。
- 本工具复用并加固已有原创 [color-tools](../04-Extracted-Core-Code-And-Scripts/core-code-lab/color-tools/README.md) 的字节扫描方法，**不复制一套颜色求值器**。需要显式主题选择、颜色求值和离线色表时继续用该模块。
- 未闭合语法、过深结构会产生覆盖缺口。CSS 转义标识符、非 ASCII 名称、现代语法边界和任意 token block 并未完整实现；错误/缺失候选仍可能发生。

### Feature flags

- JS/TS：只识别明确配置的方法名以及第一个静态字符串参数。可记录第二个简单字面量，但不称它一定是默认值。
- JSON：识别指定容器（如 `feature_flags`）的标量成员，保留声明值。
- 不解析混淆别名绑定、跨模块导入、词法遮蔽、数据流、动态字符串、插值模板、转义字符串或远端配置。
- **新出现字符串只表示本次静态样本中新观察到的候选。它不证明功能已开启、未来将上线、发布日期、账户可用性或产品承诺。**

### Tool contracts

- JS/TS：`registerTool("name")` 等调用首参数为名称候选；`inputSchema:` 等只记为**未关联 schema marker**，不会把相邻对象的 `name` 猜配给它。
- JSON：含 `name` 和 schema-shaped 对象时，保存 schema SHA-256、`type`、`required`、最多 100 个属性的名称/类型及属性总数。哈希仍覆盖完整声明对象，描述文字变化也会改变哈希。
- 不恢复 Zod、动态 spread、条件注册、请求构建器、描述中的示例、服务端验证器或实际暴露的工具集合。`static-json-structure` 也不是通过 JSON Schema 规范校验的承诺。
- 专项研究应进一步使用 AST 作用域/调用链证据；通用低依赖筛查不能替代 [第 4 卷的协议研究](../02-Illustrated-Deep-Dive-Book/04-Prompts-And-Protocols/README.md)。

### Telemetry

- 识别配置调用名（如 `track` / `logEvent`）的首字面量，以及 `event_key` / `event_name` 等字段的静态字符串。
- 字段候选不自动关联到发射器；动态字段、spread、局部别名和远端事件未知。
- 不把 SDK 错误捕获函数出现次数当作应用事件类型；也不能从字符串推断实际发送、数据收集、用户身份或隐私影响。

### 规则可配置，但不是正则脚本插件

```sh
python3 -B reverse_toolkit.py rules > "/path/to/private/rules.json"
# 人工修改完整 JSON 中的字面量名称列表，再传入：
python3 -B reverse_toolkit.py snapshot --input "/path/to/unpacked" --label "custom-rules" --rules "/path/to/private/rules.json" --output "/path/to/private/custom-snapshot.json"
```

要求保留全部六个规则列表，每项是有界 ASCII 标识符，不接受正则或可执行代码。同一别名跨文件可能绑定到不同函数；添加名称不等于证明绑定关系。规则摘要进入快照；不同规则之间的差分会明确降为待核。

### 候选、覆盖与已知词法局限

- 快照及差分明确给出 `analysis_kind: "lexical_candidate_inventory"`、`semantic_completeness_proven: false`。
- `coverage.complete_within_declared_scope` 只汇总声明范围内已报告的文件/候选管线检查。即使为 `true`，也不能推出 JavaScript 语义完整、候选全真、没有遗漏或运行时无变化。
- JavaScript 的模板与正则边界使用启发式。嵌套模板、插值内含反引号的正则、正则/除法上下文和字符串值/关键字混淆都可能导致拒绝、假候选或漏候选；未抛错并不排除这些问题。
- 原创最小反例的内层模板内容目前可能被误识别为调用候选：

  ```javascript
  const t = `${`checkGate("synthetic_false")`}`;
  ```

  该局限仍未修复；需要独立 AST/人工核验。[独立局限探针](probes/known_lexical_limitations.py)单独记录为 `expected-limitation-reproduced`，不能视为正确性通过。
- 新增的有界诊断只有稳定类别、字节位置、计数等元数据，不含原始源码或异常文本。`byte_start` / `byte_cursor` 是原输入 UTF-8 字节序列中的零基偏移；当前实现以 Latin-1 一字节一字符视图保持该合同。
- `js-quoted-state-unclosed` 描述扫描器到达输入末尾时的词法状态，不断言输入的 JavaScript 语法损坏，也不保证该位置是首次失步点。`js-token-bound-exceeded` 保留 1,000,000 token 原有硬上限。
- 本次诊断增强不改变接受范围，不恢复拒绝文件的候选，不提限。旧 v1 快照仍可读；缺少上述新增字段同样不意味着语义完整。策略版本变化会在新旧快照比较时保留告警。


## 差分如何判读

`category + key + scope` 为匹配键，CSS 的 `scope` 包含选择器与父级上下文；JS/JSON 未恢复运行时作用域。比较**值集合**，不使用 bundle 的哈希文件名作为 token 身份，不把出现次数变化当值变化。

- `added` / `removed`：在相应静态清单中新增/未再观察到，不等于产品添加/删除行为。
- `changed`：同一匹配键的原始值集合不同。注释、调用方法拼写、schema 描述等非行为改动也可能造成变化。
- `unchanged_keys`：值集合未变；出现次数、源码位置或运行时行为仍可能变化。
- `uncertain_candidates`：所有旗标、工具、遥测变化，以及扫描策略不同、覆盖缺失、多值来源等需要人工复核的变化。
- 文件差分另列；相同 SHA-256 且一对一匹配的旧/新路径只称 `possible_moves`，不证明重命名。多个相同字节文件不猜配。

若输入范围不一致、文本无法 UTF-8 解码、JSON 重复键/非法值、文件超限或扫描器拒绝输入，先看 `coverage` 和 `warnings`。不要从不完整扫描推导“已删功能”。不扫描 HTML 内联内容、source-map `sourcesContent`、嵌套档案、字体结构、原生二进制语义或远程资源。未支持的文件只做哈希清点，明确标记 `hashed-only`。

确定性范围：相同文件路径与字节、标签、规则、上限和工具版本，生成相同快照。没有运行时间或绝对输入路径。树摘要覆盖清点状态和文件身份，不是安装包字节摘要；ZIP 命令另返回原档 SHA-256。

## 可选 REA 路线

若已经安装并确认了受信任的 REA，可单独运行它的静态工件命令，再把实际得到的目录交给本工具箱。本工具箱不安装、不下载、不自动启动 REA，也不捆绑它的代码。

本研究既有流程使用 `rea-agents@6.5.0`；该版本的命令合同已在原研究中核验。以下是**手动模板**，不是本工具箱本轮运行的测试结果：

```sh
rea inspect-artifact "/absolute/path/to/local/app.asar" --json > "/path/to/private/rea-inventory.json"
rea extract-artifact "/absolute/path/to/local/app.asar" --json > "/path/to/private/rea-extraction.json"
```

先查看你实际安装版本的 `--help` 和输出结构。6.5.0 的 `extract-artifact` 使用它自己创建的临时输出目录，**不能假造一个输出目录位置参数**。从真实返回结果读取 `output_root`，核查完整性/缺失 companion/提取错误，再传给 `snapshot --input`。嵌套 ASAR 不自动等于已经展开；不要把 DMG 当作 Linux 上天然可用的直接提取格式。

可核对 [REA 6.5.0 静态工件文档](https://github.com/morluto/rea/blob/3b79af28e80785afce9f5998d8f03289402a1847/docs/javascript-artifact-reconstruction.md)。REA 许可不授予产品安装包、字体或源码的再发布权。

## 测试与发布边界

```sh
python3 -B run_tests.py
```

默认套件共329项：既有215项，加DEB投影的89项格式检查、24项事务检查与1项异地安装检查。[DEB验证记录](DEB-PROJECTION-VALIDATION.json)另列独立评审及同包smoke；早期同包零差异与[两真实版本比较](LINUX-CROSS-VERSION-VALIDATION.md)分别记录。单独运行诊断回归或未修复局限探针：

```sh
python3 -B tests/test_scanner_diagnostics.py
python3 -B probes/known_lexical_limitations.py
```

后者只读取脚本内原创合成字节，打印 JSON，不写文件、不执行 JavaScript，也不由默认测试发现。5 个 `expected-limitation-reproduced` 表示假候选仍可重现，**不是修复成功或语义正确性通过**；输出的 `fixed` 保持 `false`。若观察结果变化，探针以退出码 2 要求重新审查。

测试只使用原创合成输入：字节锚点、主题上下文、静态值变化、候选分层、策略差异、确定性、清单篡改、重命名候选、错误输入、恶意 ZIP 路径/链接/压缩比/大小/CRC 回滚、不覆盖、Markdown 安全转义、不执行目标代码，以及从任意工作目录带空格路径运行的端到端测试。

通过测试说明本工具的这些局部行为被检查；不代表对任意敌对档案做过完整安全审计，也不重新证明历史产品数量或当前产品行为。最新诊断回归及判读见 [扫描诊断附录](SCANNER-DIAGNOSTICS.md)；较早批次的验证记录见 [VALIDATION.md](VALIDATION.md)。

不要发布自行获取的原档、展开目录、产品脚本/CSS、字体、凭据、私人聊天、完整原始清单。快照与差分是**私有中间结果**：即使没有整段源码，也可能带敏感路径、配置名、字符串或 schema 摘要。发布前人工挑选最少事实，回到原字节锚点复核，再整理原创说明。

## ASAR 子集与实际包边界

先对每个输入运行 `inspect-asar`，查看 `extractable_within_subset` 和 `exclusions`。只读检查成功并不等于可以完整解包。没有排除项时可继续默认严格提取；只有外置声明而没有链接时，可显式提供精确配套目录尝试提取。它仍需核验声明的成员哈希和输入稳定性。没有跳过外置内容或完整性校验的开关，不能把遗漏的内容当作删功能。完整判读表见 [先检查 ASAR 再提取](SUPPORT.md#先检查-asar-再提取)。

```sh
python3 -B reverse_toolkit.py inspect-asar --input "/path/to/app.asar"
python3 -B reverse_toolkit.py unpack-asar --input "/path/to/app.asar" --output "/path/to/private/new-tree"
python3 -B diff-versions.py "/path/to/old.asar" "/path/to/new.asar" --output "/path/to/private/new-asar-diff"
```

三个既有Linux/Windows/macOS样本的元数据清点均有25个精确共享范围别名，分别声明3/6/10个外置文件。默认不提供companion时，严格提取会在写出前拒绝；只读元数据清点不等于成员完整性通过。显式提供精确companion后，Linux 2.37337.1已完成489个声明文件完整性核验及同包差分，见[Linux验证](LINUX-ASAR-VALIDATION.md)；不能将此同包结果扩展到另外两个平台；另有[Linux两真实版本比较](LINUX-CROSS-VERSION-VALIDATION.md)独立验证。完整支持范围、来源和测试见 [SUPPORT.md](SUPPORT.md)、[ASAR-SOURCE-NOTES.md](ASAR-SOURCE-NOTES.md)、[ASAR-VALIDATION.md](ASAR-VALIDATION.md)。


### 显式 ASAR 配套目录接口

```sh
python3 -B reverse_toolkit.py unpack-asar --input "/path/to/app.asar" --unpacked-dir "/explicit/companion" --output "/private/new-tree"
python3 -B diff-versions.py "/path/to/old.asar" "/path/to/new.asar" --old-unpacked-dir "/explicit/old" --new-unpacked-dir "/explicit/new" --output "/private/new-diff"
```

默认不读取任何 companion。显式 opt-in 后，只允许 ASAR 声明的外置文件、外置目录和必要祖先目录；缺失、额外内容（包括空目录）、链接/特殊文件、大小或声明哈希不匹配、输入变动都会整体失败，没有绕过开关。原子交付前才返回成功；失败不产出残缺差分。

此入口已在Linux通过原创合成检查和上述真实同包验证；需要POSIX no-follow与descriptor-relative原语，Windows原生sidecar入口尚不支持，macOS原生运行未验证。完整文件清单覆盖不等于完整应用或发布方认证；原生文件的语义不会因此被静态扫描器解析。详见 [显式配套目录合同](SUPPORT.md#显式配套目录精确匹配整体成功或整体失败)。

## 真实样本验证

[Linux 2.31226.1 → 2.37337.1](LINUX-CROSS-VERSION-VALIDATION.md)：真实不同DEB、同一ASAR范围、默认预算比较通过。76新增/33移除CSS候选中，33个移除均找到同键同值、不同作用域对应项；不能据数量直接判断功能删增。

[Linux 2.37337.1显式ASAR配套](LINUX-ASAR-VALIDATION.md)：489个声明文件完整性通过，同字节双输入流程完成；语义扫描仍保留18个不完整文件，报告未抹掉覆盖缺口。验证没有执行产品代码。

词法拒绝的分类、字节偏移合同与候选交叉核验建议见 [扫描诊断附录](SCANNER-DIAGNOSTICS.md)。

## 可选实验：用语法树交叉检查候选

[独立 AST 候选通道](optional-ast-channel/README.md) 用真实 JavaScript 语法节点排除五类原创词法反例。它保留独立 schema、预算和结果，不更改默认扫描器及其已报告缺口。当前89项测试使用明确标记的 Node 内部 Acorn 8.17.0；正式外置 Acorn 入口的成功路径尚待验证，不能当成默认工具箱的生产替代品。
