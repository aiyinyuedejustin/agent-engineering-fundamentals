# 可移植颜色目录工具

从**你本地已经解包的 CSS**提取声明清单，再生成带来源定位的颜色 JSON 和单文件离线浏览页。工具只用 Python 标准库；无需原研究工作区、固定绝对路径、应用运行环境或网络。

工具保留原研究的静态配置选择方法。已使用 Claude Desktop Linux 2.37337.1 的原清单和重新提取的清单分别回归：两条路径生成的 **1,341 条颜色记录完全一致**，包括 **23 条未求值表达式**。这说明该版本的事实得到保留，不代表任意新版本都会产生相同数量，也不代表浏览器最终 computed style。

## 交付内容与边界

- `extract_design_tokens.py`：扫描明确指定的本地 CSS 目录，生成私有声明清单。
- `build_color_catalog.py`：验证清单、来源 SHA-256、声明字节锚点和解析依赖，生成目录及离线页面。
- `inventory_inputs.py`：清单结构和输入路径校验。
- `color_catalog_template.html`：原创页面模板，数据在构建时内嵌。
- `tests/test_color_tools.py`：仅使用程序生成的原创测试数据，无产品文件依赖。
- `tests/verify_baseline.py`：使用你自行提供的私有输入执行完整基线回归。
- `tests/test_browser_dom.cjs`、`package.json`：可选的模拟 DOM 测试。

交付包不包含安装包、下载资产、原始 CSS、应用 JavaScript、字体、原始提取清单或 `node_modules`。工具不下载、不解压、不导入或执行目标应用代码，也不打开字体文件。不要把安装包、私有输入目录或原清单加入交付包。

## 环境

- Python **3.10 或更新版本**，无需 `pip install`。
- 可选 DOM 测试：Node.js 18+、`jsdom` 26.1.0。生成和使用色表本身均不需要 Node.js。
- Linux、macOS、Windows 均可使用 Python CLI；下面的命令用 POSIX shell 写法示例，Windows 可将变量替换成带引号的实际路径。

## 必需输入

所有路径都由命令行提供，可以包含空格，可以放在任意有权限读取的位置。

| 参数 | 含义 | 何时需要 |
|---|---|---|
| `--resources` | 已解包应用的 `resources` 目录；其下必须有 `ion-dist/` | 提取和构建均必需 |
| `--asar-root` | 已经展开的 `app.asar` 根目录，例如其下直接存在 `.vite/` | 完整基线必需；只有 ion 来源时可省略 |
| `--inventory` | JSON 声明清单，来自本工具提取器或兼容的原研究清单 | 构建必需 |
| `--output` | 提取时是 `.json` 文件；构建时是输出目录 | 两步均必需 |

`--asar-root` 接受的是目录，不是 `.asar` 文件。此包不负责取得、下载或解包应用；请使用你有权访问的本地输入。完整基线需要与清单一致的 ion 和 asar 文件，不能用另一版本的 CSS 替代。

来源路径采用逻辑命名空间：清单中的 `ion/assets/example.css` 对应 `--resources/ion-dist/assets/example.css`；`asar/.vite/example.css` 对应 `--asar-root/.vite/example.css`。不会从原研究的 JSON 元数据或默认工作区猜测输入位置。绝对来源路径、`..` 穿越、未知命名空间和越出声明目录的文件符号链接均被拒绝。

## 路径 A：从本地 CSS 重新提取并构建

以下变量全部替换为自己的实际路径。把输出放在独立目录，避免与输入、工具文件混放。

```sh
TOOLS="/path/to/color-tools"
RESOURCES="/path/to/unpacked-app/resources"
ASAR_ROOT="/path/to/extracted-app-asar"
INVENTORY="/path/to/private/color-inventory.json"
OUTPUT="/path/to/generated-color-catalog"

python3 "$TOOLS/extract_design_tokens.py" \
  --resources "$RESOURCES" \
  --asar-root "$ASAR_ROOT" \
  --output "$INVENTORY"

python3 "$TOOLS/build_color_catalog.py" \
  --inventory "$INVENTORY" \
  --resources "$RESOURCES" \
  --asar-root "$ASAR_ROOT" \
  --output "$OUTPUT" \
  --product "Claude Desktop Linux" \
  --version "2.37337.1" \
  --expect-records 1341
```

上述产品和版本标签仅是你提供的描述，不会被工具验证。对其他版本，应填写实际标签，并在人工复核范围后调整或省略 `--expect-records`。这个参数只检查记录总数；完整事实一致性应使用后面的基线测试。

提取清单是**私有中间文件**。它保留所有扫描到的自定义属性，可能含非颜色声明，不能当作公开的颜色目录分享。相同 SHA-256 的 CSS 仅分析一次，保留重复来源标记；来源 ID 和块 ID 按目录与文件顺序确定。

## 路径 B：使用已有清单构建

已有兼容的 `design-token-taxonomy.json` 时，可以跳过提取步骤，把 `--inventory` 指向它，再执行上面的构建命令。仍然必须提供清单对应的本地 CSS：构建器会重新读文件、检查 SHA-256，并核对每个输出颜色声明及其解析依赖的 UTF-8 字节范围。单独一份 JSON 不足以通过来源验证。

兼容清单的最小结构：

- `sources[]`：唯一字符串 `id`、命名空间相对路径 `path`、小写 64 位 `sha256`。
- `blocks[]`：唯一字符串 `id`、`source`、`selector`、字符串数组 `context`、`byte_start`、`byte_end`。
- `tokens{}`：名称映射到 `taxonomy`、非负整数 `reference_count`、非空 `definitions[]`。
- 每个 definition 包含 `value`、`block`、`byte_start`、`byte_end`。
- 所有偏移均为原文件的 **UTF-8 字节、从 0 开始、右端不包含**，不是字符索引或行号。

清单的分类和选择器上下文仍属于输入事实；字节核验不是对任意外部清单的全面语义审计。应使用可信清单，或用本包提取器从原始文件重建。

默认从 `ion/` 来源中选择唯一一个拥有完整 315 项根色阶的文件，**不硬编码带哈希的 CSS 文件名**。若出现多个候选，使用清单中确切的来源 ID 或路径：

```sh
python3 "$TOOLS/build_color_catalog.py" \
  --inventory "$INVENTORY" --resources "$RESOURCES" \
  --asar-root "$ASAR_ROOT" --output "$OUTPUT" \
  --primary-source "ion/assets/your-selected-source.css"
```

显式指定来源仍需包含完整色阶。它不会自动拼接多个文件的语义配置。可用 `--template /path/to/template.html` 指定自己的模板；模板必须恰好包含一个 `__COLOR_DATA__` 占位符。模板属于可执行页面代码，只应使用可信模板。

## 输出与使用

成功构建只向 `--output` 目录写入两份文件：

1. `color-catalog.json`：完整事实、配置、声明清单、来源哈希、字节位置、解析链与统计。
2. `index.html`：内嵌精简数据的离线色表，无外链脚本、字体、图片或网络请求。

直接用浏览器打开 `index.html` 即可筛选色族、主题、类别、透明色和表达式，搜索 token、查看来源并导出当前筛选结果。复制功能受浏览器的剪贴板权限限制；拒绝时会显示失败提示，不会声称复制成功。页面的深浅画布只改变展示背景，不会改变所选来源配置。

同一输出目录重复运行会替换同名的这两份产物；构建器拒绝用它们覆盖输入清单或模板。生成内容先在内存完成验证，校验错误不会开始写输出；文件系统中途写入失败不提供事务回滚。

## 基线记录和解析边界

Claude Desktop Linux 2.37337.1 的验证结果：

| 配置 | 总记录 | 可解析 | 保留表达式 |
|---|---:|---:|---:|
| 原始色阶 | 315 | 315 | 0 |
| CDS 显式浅色 | 349 | 337 | 12 |
| CDS 显式深色 | 349 | 338 | 11 |
| Legacy v1 浅色 | 50 | 50 | 0 |
| Legacy v1 深色 | 50 | 50 | 0 |
| Legacy v2 浅色 | 50 | 50 | 0 |
| Legacy v2 深色 | 50 | 50 | 0 |
| HSL 桥接 | 128 | 128 | 0 |
| 合计 | **1,341** | **1,318** | **23** |

即 315 个原始色阶 + 349 × 2 个 CDS 配置记录 + 200 个 Legacy 配置记录 + 128 个桥接记录。机器目录覆盖 843 个相关名称、3,234 个颜色声明锚点、4 个实际颜色来源文件。全量提取扫描范围更大，不能把这 4 个文件理解为所有输入文件。

- 配置是明确的静态声明选择：根声明、组件层、未分层默认值，以及显式 `data-mode=dark` 的 screen 覆盖。
- 不模拟完整 CSS cascade；不声称页面已经激活某个 DOM、system 模式、局部 dark-scope、特性查询或跨文件样式。
- 支持 3/4/6/8 位 HEX、`transparent`、HSL 分量三元组、保持通道不变且仅调整 alpha 的相对 HSL、与 transparent 混合的指定 sRGB `color-mix`、支持格式的数字 `rgb/rgba`。
- 仅展开精确简单形式的 `var(--name)`。fallback、缺失引用、循环引用、其他函数格式、`currentColor`、CSS 级联关键字和相对 RGB calc 等均保留表达式与原因，不猜测 HEX 或 alpha。
- HSL 三元组在按 `hsl(...)` 消费时表示颜色。HEX 是四舍五入后的 8-bit sRGB 展示值；原始表达式、浮点通道和未合成 alpha 保留在 JSON。
- `#ffffff80` 的 alpha 是 128/255，不是精确 0.5；透明颜色不预先合成到页面背景。
- 名称分类、选择器格式和 9 × 35 色阶集合服务于已记录的来源结构。工具可迁移，不意味着任意 CSS、压缩形式或新版本结构都自动兼容；遇到差异应先审查输入和配置方法。

## 测试

### 1. 无产品文件的单元测试

```sh
python3 -m unittest discover -s "$TOOLS/tests" -p 'test_*.py' -v
```

覆盖原创最小输入、315 项色阶、明暗配置与层顺序、Legacy 桥接、透明度、未求值表达式、输入校验、哈希及字节锚点篡改、路径穿越/符号链接、模板转义、CLI 移动到其他目录后执行、带空格路径以及 `python -O` 下仍然有效的验证。

### 2. 原清单 / 重新提取的完整事实回归

你需要另行持有原清单和原 `color-catalog.json`，两者均不随工具包附送。

```sh
python3 "$TOOLS/tests/verify_baseline.py" \
  --inventory "/path/to/private/original-design-token-taxonomy.json" \
  --baseline "/path/to/private/original-color-catalog.json" \
  --resources "$RESOURCES" \
  --asar-root "$ASAR_ROOT" \
  --output "$OUTPUT"
```

测试先确认重新提取的 `sources`、`blocks`、`tokens`、`statistics` 与原清单完全相同，再检查两条构建路径的全部 `records`、`statistics`、`definition_inventory`、`sources`、`blocks` 与基线逐项相同，并确认来源哈希、3,234 个声明锚点及 23 条未求值记录未被填入颜色。`--output` 可省略，此时不会保留构建产物。

整份 JSON 不要求字节相同：私有输入清单的序列化及内容范围不同会改变 `taxonomy_sha256`；可移植版还更新了说明文字和产品标签机制。对颜色事实的比较是完整记录比较，不只是数量比较。

### 3. 可选的离线页面模拟 DOM 测试

只有此测试需要安装 npm 开发依赖；离线构建无需这一步。请在你允许安装依赖的工具副本中运行：

```sh
cd "$TOOLS"
npm install --ignore-scripts
node tests/test_browser_dom.cjs "$OUTPUT/index.html"
```

覆盖所有配置的记录数、筛选/搜索/重置、详情重复打开关闭、精确 alpha 和复制内容、剪贴板拒绝、未求值项不显示伪造色块、背景切换、CSV 下载、无网络调用和无脚本异常。它是模拟 DOM 检查，不替代真实浏览器的视觉、原生 dialog、实际剪贴板权限和 CSS 渲染测试。

## 常见失败

- `Missing ion source directory`：`--resources` 应指向包含 `ion-dist` 的上一层目录。
- `Inventory uses asar sources; supply --asar-root`：补充已解包的 asar 目录，不要传归档文件。
- `Source hash mismatch`：文件与清单不一致；检查版本或重新提取，不要修改哈希来绕过检查。
- `Declaration byte anchor mismatch` / `Invalid declaration byte bounds`：清单或文件已变化；从正确的原文件重建。
- `Cannot choose a unique complete ion palette`：候选缺失或不唯一；检查输入，必要时明确指定 `--primary-source`。
- `Expected 1341 records`：输入版本或配置结构发生变化；先复核差异，再决定期望值。

CLI 校验失败以非零状态退出并给出错误。执行 `python3 "$TOOLS/build_color_catalog.py" --help` 或提取器的 `--help` 可查看全部参数。
