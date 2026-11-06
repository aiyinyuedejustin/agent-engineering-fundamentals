# 本地复现实验：统计诊断与官方评分函数

## 实际完成了什么

本批由评测科学研究执行完成，环境为 Python 3.12.14、NumPy 2.3.5。

| 实验 | 原始结果首次成功写入时间（UTC，精确到秒） | 性质 |
|---|---|---|
| statistical_diagnostics.py | 2026-11-06 02:31:41 | 固定 seed 的合成统计演示 |
| scorer_diagnostics.py | 2026-11-06 02:33:21 | 固定官方源码的隔离函数测试，输入均为人工构造 |

时间依据该次成功运行的结果文件写入时间，原系统展示时区为 +09:00，此处已换算为 UTC。后续集成检查或复跑应另记日期，不能把集成人员的复跑算成这次原始运行。脚本复跑会覆盖同名结果 JSON；需要保留原始结果时，先复制 results 目录。

**D4 范围：没有调用模型 API，没有生成模型答案，没有跑完整数据集或 SWE-bench 容器，没有进行真实模型对比。** Judge API 调用全部用本地固定文本 stub 替代。HumanEval 只执行 pass@k 数学函数，不执行模型生成的代码。

## 目录

- `statistical_diagnostics.py`：仅依赖 Python 标准库。
- `scorer_diagnostics.py`：还需要 NumPy。
- `source_manifest.json`：官方仓库、固定提交、文件路径、Git blob SHA 与下载 URL。
- `results/statistical_diagnostics.json`：统计实验输出。
- `results/scorer_diagnostics.json`：评分实验输出，含源码 SHA-256 和函数行号。

上游原始源码不随本研究仓库重新分发，避免混淆原文与原创研究。`source_manifest.json` 的 `/tmp` 本地路径是原执行环境缓存，不是其他机器必须已有的文件。

## 在新机器复现

使用 Python 3.12 和 NumPy 2.3.5 可最接近原环境。已具有可用 NumPy 时无需安装其他评测框架，也不需要 API key。

在本目录运行：

```bash
python statistical_diagnostics.py
python scorer_diagnostics.py --download
```

`--download` 从 manifest 中的官方 GitHub 固定 commit URL 读取五个 Python 源文件，保存到临时目录，并在运行前校验 Git blob SHA。不使用浮动 main/master。若网络不可达，下载步骤会失败；不要为了凑结果绕过 hash 校验。

原研究环境已通过连接器读取这些同版本文件并核对 blob SHA，因此当时执行的是：

```bash
python scorer_diagnostics.py
```

该不带参数模式依赖 manifest 中的本地缓存路径。请在新机器优先使用 `--download`。最终结果还记录 SHA-256，方便核对文件字节。

## 执行方式与安全边界

评分脚本用 Python AST 选取明确允许的函数、常量和枚举，再对合成输入调用这些函数。它不导入整个 HumanEval/FastChat/SWE-bench 依赖树，不运行仓库安装脚本，不启动真实 judge，也不执行候选补丁。

校验 hash 是为了确认被测版本，不是万能安全保证。这里的允许函数已经人工阅读；不要把脚本修改为从任意来源执行未知函数，也不要把 HumanEval 的 reliability_guard 当成安全沙箱。

## 实验列表与正确解读

### 统计实验

- 相同 72% 对 70% 总分，在不同逐题错误重合度下具有不同配对区间。
- 每簇十个重复结局时，错误地按行 bootstrap 会低估不确定性。
- 永远判正的 judge 可以有高总体准确率，却完全不会识别负例。
- 多重比较与挑选最高观察分产生乐观偏差。
- 零失败不代表真实失败率为零。
- 任务权重不同可反转总分排序。
- 平均逐题 pass@k 与对平均成功率做非线性变换不同。
- 直接核对协方差恒等式，避免复制论文示例中的算术错误。

这些数据全部是构造或模拟，不是某个商用模型的真实表现。

### 官方评分器实验

- HumanEval：六组 n/c/k 输入，比较官方估计器、组合数恒等式与朴素 plug-in。
- SQuAD：六组归一化/语义边界例子，以及 no-answer 阈值的严格大于边界。
- FastChat：四组 pairwise、四组 single 评分文本，检验冲突标签、缺失标签、越界数字和备用解析规则。
- SWE-bench：六组状态 × 两种 eval mode，截断 ID 三种情况，日志有效性五种情况。

SWE 的 `FAIL_ONLY` 状态函数允许缺席测试视作成功，这只适用于相应“仅记录失败”的日志契约。完整路径还包含运行迹象和退出码检查。不能只截取状态函数结果，声称“完全没有运行也会通过”。

## 已遇到并解决的问题

首次 scorer 调用在 source hash 校验阶段停止：通过文本补丁写缓存时，文件末尾空白被归一化，SQuAD blob SHA 不符。未跳过校验；改用连接器返回的原始文本精确保留字节，五个文件全部匹配后再运行成功。

FastChat 历史源码的 regex 字符串在 Python 3.12 会产生 invalid escape sequence SyntaxWarning，运行仍成功。没有修改上游代码来隐藏警告。

## 延伸到真实评测还缺什么

真实模型输出、完整任务集与许可证审查、调用预算、模型与工具配置、完整执行环境、安全隔离、真实运行日志、失败分类与统计分析方案。这里只验证评分与推断机制，不替代这些步骤。
