# 出版物完整性检查器

这是一个原创、只读、无第三方依赖的 Python 小工具。它帮助维护本书的目录、阅读链接和已登记文件的 SHA-256，不运行书中代码，不安装依赖，不联网，不修复或改写出版物，也不调用 Git。

本工具位于 `04-Extracted-Core-Code-And-Scripts/scripts/publication-checks/`。也可以保留为独立目录；入口始终显式接收“书根目录”，不依赖脚本安装位置。

## 运行

要求 Python 3.10+，以及支持目录文件描述符、`O_NOFOLLOW` 的 POSIX 系统，例如 Linux 或 macOS。Windows 原生环境会明确拒绝运行；可在 Linux/WSL 环境中使用，不能降级成会跟随符号链接的读取方式。

从本工具目录执行：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 check_publication.py /path/to/publication > /tmp/publication-check.json
```

在完整远程仓库的检出目录中，书根目录应传入 `/path/to/repository/books/claude-app`。本地研究副本的书根目录名可以是 `publication`；两者具有相同书内相对路径。不要把完整仓库根目录误当成书根目录。

JSON 写到标准输出；一句摘要写到标准错误。工具不主动创建报告文件；上例的重定向由调用者选择。建议将报告放在书根目录外，避免把本机路径和过时快照提交到出版物。

退出状态：

- `0`：`passed`，声明范围内无错误，未检测到需要报告的不支持语法。
- `1`：`failed`，至少一个可确定的结构、文件、链接、路径或清单错误；仍会列出不支持的语法。
- `2`：`incomplete`，已支持检查没有错误，但存在未完成的语法/片段检查；或者 `invalid_run`，配置、平台或书根目录不可用。

`passed` 只针对下文的有限合同，不表示“全部 Markdown 已解析”“浏览器渲染正确”或“通过安全审计”。调用者应同时读取 `status`、`summary.errors`、`summary.unsupported` 与 `issues`，不要只看退出码。

## 固定检查合同

`contract.json` 是可审阅的数据，不是可执行插件。默认合同要求：

- 五个主要资料目录和 `assets`；书首页及五个主目录的 README。
- 六个指定 HTML 模板。
- 第 01–16 卷的 README，以及第 17–19 卷三个补充卷的 README。
- 七套机制实现 skill 的 `SKILL.md`。全书阅读入口 `claude-app-study` 不计为第八套机制实验。
- 三份指定公开清单：工具箱 `manifest.json`、第 12 卷 `validation.json`、附件实验台 `validation.json`。

名称逐项固定在配置中，删除文件不会让“实际扫描到的数量”自动降低为新的验收标准。新增卷、移动目录或新增需要追踪的清单时，应先审阅并修改合同。其他书可以通过 `--contract /path/to/contract.json` 复用检查器；保留 schema、相对路径数组、类型和清单字段即可。

## Markdown 支持范围

扫描书根目录中的 UTF-8 `.md` 与 `.markdown` 文件。支持以下有限且明确的形式：

- 单行内联链接和图片：`[文字](relative.md)`、`![图](image.svg)`；支持成对括号路径、Markdown 标点反斜线转义、尖括号目标和单/双引号标题。
- 单行 reference 定义，以及完整、折叠、快捷 reference 链接；标签按空白归一化和大小写折叠匹配，重复定义采用第一个。未使用的定义不视作可点击链接。
- 常见的可点击图片：`[![说明](image.svg)](chapter.md)`，分别检查图片和外层目标。
- 相对文件或目录路径；标准 URL 拆分后只解码一次百分号编码。查询串不用于文件定位，计入 `local_queries_ignored`。片段单独解码且区分大小写。非法百分号编码和非法 UTF-8 会报错。
- 仓库根相对链接 `/books/claude-app/...` 映射到传入的书根目录；其他仓库路径会报越界。HTTP(S)、mailto、tel 和协议相对地址不发起请求，不声称其可达。
- 普通 ATX 标题与单行 Setext 标题的 GitHub 风格片段：小写、空格变连字符、去除标点/符号、保留字母/数字/组合标记/下划线/连字符；去掉简单强调和行内代码标记；重复片段依次加 `-1`、`-2`，并处理与已有后缀冲突。
- 普通 fenced code、四空格/制表符缩进代码、同行行内代码、闭合 HTML 注释和开头的 YAML frontmatter 不做链接检查。纯 `<br>` 不产生链接警告。

标题规则参考 [GitHub 官方格式说明](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links)。该工具没有引入 CommonMark/GFM 解析器，也没有复制 GitHub 完整 Unicode slugger 数据表；复杂 Unicode、渲染器扩展和未来规则变化仍需人工核对。

会明确报告的不支持项包括：多行或复杂 reference 定义、复杂嵌套标签、多行/未闭合行内代码、列表或引用容器中的标题/围栏、HTML/MDX、标题中的链接/HTML 实体/自定义 ID/数学与 emoji 短码、HTML/PDF/源码行号片段，以及目录片段的 README 自动选择。遇到可能影响标题列表的结构，不会把该文档的片段检查冒充为完成。

这是保守的有限扫描器，不保证识别每一种未支持语法。缩进列表、跨行段落、嵌套 HTML 和复杂行内格式的精确渲染不在合同内；无警告也不能代替完整 Markdown 渲染测试。书中示例代码和未使用 reference 定义中的路径不作为读者链接验收。

## 清单与读取边界

三种已知清单统一读取 `files` 字段：可以是含 `path`、`sha256`、可选 `bytes` 的数组，或路径到 SHA-256 的映射。路径相对清单所在目录，最终必须位于书根目录内。检查只比较清单实际列出的文件，不替清单扩大范围，不断言所有公开文件已入清单，也不核验清单中的历史测试结论、来源、真实性或版权，不检查文件的 Git 跟踪状态、远程提交或发布状态。

SHA-256 一致仅说明当前字节与清单记录一致。它不证明内容可信、不含秘密或恶意行为。工具没有 secret scanner，不读取私有研究目录，不运行被检查的 Python/JavaScript/HTML，也不进行软件安全、法律、可访问性或产品行为认证。

所有出版物文件访问都锚定在已打开的根目录文件描述符；逐层使用 `O_NOFOLLOW`。书根目录自身、祖先或链接目标的符号链接均拒绝，特殊文件不读取；链接中的 `..` 不得越过书根。`.git`、`.hg`、`.svn`、`node_modules`、`__pycache__`、`.venv`、`venv` 不遍历，显式指向这些目录的读取也会拒绝。普通 `.gitignore` 仍可按清单验证。

Markdown 和 JSON 的单文件解析上限为 8 MiB；清单目标按块计算哈希，不作为程序加载。配置文件是调用者显式选择的本地可信输入，不属于出版物扫描边界。

## 快照与维护

报告记录开始/结束时间，整个检查不是原子文件系统快照。出版物同时更新时，临时缺文件或 hash drift 可能只是编辑中的状态。先停止相关编辑，再重新运行；不要自动更新哈希来消除失败。哈希文件在读取期间可检测到的大小/修改时间变化会单独报错，但这不替代文件系统快照。

建议维护流程：编辑完成 → 运行合成测试 → 运行只读检查 → 逐项处理错误 → 对不支持项做针对性的人工或渲染器验证 → 需要时由维护者重新生成正确清单 → 再运行。检查器自身不修复链接、不刷新清单、不提交、不推送。

测试只创建临时合成目录，覆盖重复标题后缀、转义路径、URL/片段、百分号编码、缺文件、越界链接、符号链接、清单漂移、引用链接、可点击图片和 CLI 状态。不会把“测试通过”描述成整本书或第三方产品通过运行时验证。

## 给自动化读取者

稳定输出标识为 `publication-integrity-report/v1`。每项问题至少含 `severity`、`code`、`path`、`message`；存在行号时给出 `line`，目标、期望/实际哈希等放在 `details`。

请按错误码分类消费，不解析英文提示句；保留 `unsupported` 问题和 `scope`。`checks` 分别记录目录、Markdown、清单阶段的状态，因此目录/哈希可通过而总状态仍为 `incomplete`。只有该清单的 `status` 为 `passed`，且 `matched` 数与 `entries` 数一致时，才能说“这份清单列出的当前文件全部匹配”。不能由此推断清单外文件、远程仓库、渲染结果或历史测试也被验证。
