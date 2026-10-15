# 静态候选扫描：诊断与解释边界

本工具生成静态候选清单。`scanned` 表示文件走完声明的候选扫描管线，不证明候选全真、没有遗漏、运行时可达或产品行为发生变化。

## 覆盖不等于语义完整

快照与差分固定给出：

```json
{
  "analysis_kind": "lexical_candidate_inventory",
  "semantic_completeness_proven": false
}
```

`coverage.complete_within_declared_scope` 保留旧接口，只汇总声明范围内已报告的文件/候选管线检查。即使值为 `true`，也不能推导 JavaScript 语义完整。旧 v1 快照没有新增字段仍可读取，其缺省同样不意味着完整。

新增、移除、值变化均指候选观察。文件相同、候选零差异或未额外列出不确定项，也不证明完整语义无变化。字符串、模板、正则的启发式边界可能导致假候选或漏候选，且不一定抛错。

## 结构化拒绝诊断

扫描器仍把原有失败文件标为 `scan-incomplete`，保留 `scanner-rejected-input` 与 `ToolkitError`，不保留该文件的候选。额外 `diagnostic` 只包含固定枚举及有界数字，不含原始源码、token 值或任意异常文本：

| code | 含义 | 不能推导 |
|---|---|---|
| `js-comment-state-unclosed` | 扫描器的注释状态到达输入末尾 | 原始 JavaScript 必定损坏 |
| `js-quoted-state-unclosed` | 扫描器的字符串或模板状态到达输入末尾 | 报错引号就是首次根因位置 |
| `js-token-bound-exceeded` | 观察到第 1,000,001 个 token，超过原上限 | 自动提高限额或忽略尾部即可安全完成 |

`schema` 为 `original-scanner-diagnostic/v1`，`phase` 为 `javascript-tokenization`。`category` 区分 `lexical-state` 与 `resource-bound`；`input_validity` 保持 `not-determined`。预算错误还包含 `token_limit=1000000`。

### 位置单位

- `byte_start`：失败时当前词法项的零基起始**字节**位置，不保证是首次因果失步点。
- `byte_cursor`：扫描器停止位置，以原输入字节数为上界；不会返回 EOF 之外的位置。
- 二者针对原 UTF-8 字节序列，不是 Unicode 字符数或 UTF-16 位置。当前 Python 实现用 Latin-1 一字节一字符的可逆视图保持这一合同。测试包含中文、emoji 前缀和末尾反斜杠。
- 文件哈希与字节锚点应一起核验。不要把异常位置当成未经核实的产品源码事实。

## 已确认的 Linux 样本边界

[Linux ASAR 验证](LINUX-ASAR-VALIDATION.md)中的同一已校验样本仍为 489 文件：427 `scanned`、44 `hashed-only`、18 `scan-incomplete`，3,761 条候选。诊断增强后文件行、候选以及原有拒绝没有改变。

18 项中，16 项为扫描器的字符串/模板末尾拒绝，2 项为原 token 预算拒绝。独立纯语法检查接受这 18 份字节；检查只解析输入，没有执行或导入产品代码。因而不能把这 16 项直接归因为坏文件。

对 16 项的首次可核验边界偏离，14 项为嵌套模板被提前截断，1 项为插值内正则字符类的反引号，1 项为箭头后的正则未识别。这是按文件的首个观察分类，并非互斥的整文件根因穷举；部分文件还有其他正则上下文问题。两个预算拒绝继续保留，未提高上限。

## 五个未修复的假候选局限

运行独立探针：

```sh
python3 -B probes/known_lexical_limitations.py
```

该脚本不属于默认测试，只分析脚本内原创合成字节，不执行 JavaScript、不读取产品文件、不联网、不写文件。五种情形为：

1. 嵌套模板的原始文字被当成调用。
2. 普通字符串值等于 `return`，错误影响后续除法/正则判断。
3. 箭头后的正则正文被当成调用。
4. 逻辑与后的正则正文被当成调用。
5. 控制语句头部后的正则正文被当成调用。

例如：

```javascript
const t = `${`checkGate("synthetic_false")`}`;
```

内层文字目前会产生一个错误的 flag 候选。探针输出 `expected-limitation-reproduced`、`fixed=false`；这明确表示错误仍存在，**不是正确性通过**。退出 0 只表示重现了已记录局限；若观察行为改变，退出 2 要求审查，不会擅自称为修复。

不应通过吞异常、全文正则回退、部分文件挽救或扩大 regex 前驱列表来制造覆盖提升。完整模板/正则边界修复属于另外的解析能力变更，必须独立说明接受范围、预算及回归。

## 测试与策略兼容

```sh
python3 -B run_tests.py
python3 -B tests/test_scanner_diagnostics.py
```

默认测试为 202 项既有回归加 13 项诊断回归，共 215 项。新增回归验证拒绝保持、1,000,000-token 原上限、字节偏移、源码不泄漏、固定候选声明以及旧快照兼容；五个未修复的假候选探针不在默认绿色套件内，也没有用 skip/xfail 隐藏。

诊断策略版本显式为 `1.0.1+diagnostic-preview.1`。旧 v1 快照仍可读取；新旧策略差异继续触发比较警告，不能假装是同一策略。此版本不改变接受范围或候选提取算法，不证明全部词法问题已经被检测或修复。

## 可选 AST 交叉核验

真实 JavaScript parser 可核对模板/正则边界，以及候选是否位于 `CallExpression` 等实际语法节点，明显有助于剔除词法假影。但 AST 也不证明名称绑定、shadowing、运行时可达性、事件发送或产品承诺。

本工具没有引入生产 AST 依赖。若另行提供适配器，应是显式 opt-in、固定 parser 版本和来源、单独策略身份；保留原字节及 token 上限，限制时间、内存、节点与深度。超限、语法不支持或解析失败仍须显式拒绝，不能为了覆盖率换口径。解析过程不得执行、导入、构建目标代码或访问远端资源；UTF-16 parser 位置须经过测试转换为 UTF-8 字节位置。

建议交叉核验结果分为“语法形态确认”“词法假影”“未解决”，不直接改名为运行时事实；与原候选清单分开计数和比较。
