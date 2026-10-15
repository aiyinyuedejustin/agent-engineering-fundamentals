# 可独立复制的选定颜色参考

本技能整个文件夹可单独复制。运行示例、查色和便携测试都不需要本书其他目录，不需要 npm 安装、网络或原始产品文件。

## 三类文件不要混淆

- [observed-tokens.json](observed-tokens.json)：精选静态事实，含常用 CDS 颜色、密度、时长和字体元数据；不是全色表。
- [color-catalog.json](color-catalog.json)：本书已发布选定 profile 的完整元数据副本，包含 1341 条基线记录和 resolution_extension。来自 Claude Desktop Linux 2.37337.1 的静态声明选择与附加推导；并非全量运行时 CSS、完整层叠计算、登录后外观或未来版本保证。sources 中路径只是原样保留的来源标识，不是技能运行依赖；不随包复制原始 CSS、专有字体。
- [assets/tokens.css](../assets/tokens.css)：原创语义映射与可访问性适配的实现起点，不是产品 CSS，不是上述记录的一对一导出。

## 按 profile 与 name 取值

先选范围：raw、cds_light、cds_dark、legacy_v1_light、legacy_v1_dark、legacy_v2_light、legacy_v2_dark、bridge。相同名称可存在于不同 profile；禁止跨 profile 任意拼接或只按 name 取首条。profile 是选定声明分支，不证明该分支在真实 DOM 已启用。

在 skill 根目录用 Node.js 22+ 运行以下示例，不需要安装依赖：

```sh
node --input-type=module -e '
import {readFileSync} from "node:fs";
const c = JSON.parse(readFileSync("references/color-catalog.json", "utf8"));
const profile = "cds_light", name = "--cds-bg-tint-aqua";
const rows = c.records.map(row => Object.fromEntries(c.columns.map((key, i) => [key, row[i]])));
const baseline = rows.find(row => row.profile === profile && row.name === name);
if (!baseline) throw new Error("Not published in this selected profile");
const extension = c.resolution_extension.records[`${profile}:${name}`] ?? null;
console.log(JSON.stringify({baseline, extension}, null, 2));
'
```

columns 明确为 profile、name、declared、hex、alpha、status。保留 declared 与基线 status，不用推导结果覆盖原始记录。基线 resolved 的 hex 是四舍五入的 8-bit sRGB 表示，alpha 独立保存，不能丢弃。HSL 三元组只有放入 hsl(...) 的消费上下文才表示颜色。

基线 unresolved 时查 resolution_extension.records[`${profile}:${name}`]：

1. statically_resolved 且 srgb_in_gamut=true：可使用扩展 hex 和 alpha，明确标为静态推导。
2. statically_resolved 且 srgb_in_gamut=false：共 5 条 extended sRGB。使用 srgb_channels / css_color_srgb 与 alpha 保留越界通道，hex 必须为 null。不得把 clipped_preview.hex 冒充真实 HEX；该字段仅是逐通道裁剪预览，不是浏览器 gamut mapping、computed style 或产品测量。
3. context_dependent：共 4 条。hex 与 alpha 均为 null，先读取 dependency_kind、reason 和消费上下文。initial 的 var() fallback 与 currentColor 的实际颜色/透明度不能凭空补齐，也不得编造 HEX。

## 数量与验证

基线：1341 条 = 1318 resolved + 23 unresolved。扩展对这 23 条补充解释：19 条静态数值 = 14 条可表示 HEX + 5 条 extended sRGB；另 4 条依赖消费上下文。合计 1337 条有静态数值、1332 条有 HEX。这不是把基线统计改写为“全部 resolved”。

在 skill 根目录执行 `node --test assets/*.test.mjs`。新增 color-catalog.test.mjs 核验结构、唯一键、逐 profile 统计、扩展分类、未伪造 HEX、包内 Markdown 相对链接。测试只使用包内文件，可以从任意工作目录通过绝对测试路径运行；不读取书外目录。测试不是实际产品视觉或全量 CSS 验证。

维护完整研究书时，另在书根运行 `node --test 04-Extracted-Core-Code-And-Scripts/tests/portable-color-catalog-sync.test.mjs`：逐字节比较权威发布色表与技能副本。色表重建后必须一起更新副本、审查统计及本指南，并重跑两组测试；同步测试故意不放进便携技能，不能因书外源文件缺失而跳过校验。书内同步测试不会修改文件，也不要求独立复制的使用者取得本书。
