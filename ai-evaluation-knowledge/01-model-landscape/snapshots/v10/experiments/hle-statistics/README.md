# HLE simple runner：评分、置信区间与缓存的局部实验

## 证据范围

源码固定为 [centerforaisafety/hle@22ed3074b1e7b134bcbc09028d0ba320839b0655](https://github.com/centerforaisafety/hle/tree/22ed3074b1e7b134bcbc09028d0ba320839b0655)，commit 时间 2026-09-23T15:38:47Z，读取/实验日期 2026-11-06。8 个源码/配置文件都校验 Git blob SHA-1 与 SHA-256，清单见 source-manifest.json。

完成限定路径 D3 和 **25 项合成组件 D4**。执行 Python 3.12.14、NumPy 2.3.5；上游 requirements 固定 NumPy 1.26.4，所以不是完整依赖锁定复现。没有模型、judge、数据集或网络调用。二次重放 results.json 字节一致；重放不新增实验计数。

重要边界：这是 repository 的 simple runner，不证明它等于 Scale、CAIS Diamond 或 AA 当前线上流水线。不能据此修改已发布成绩或声称那些榜单存在同样影响。

## 实际追踪路径

- `run_model_predictions.py`：CLI → load_dataset(test，未传 revision) → max_samples → filename/ID 缓存过滤 → asyncio semaphore → format_message → API → predictions JSON。
- `run_judge_results.py`：数据集总题数 → 已有 predictions/缓存筛选 → add_judge_response → LLM结构化回答 → judged JSON → dump_metrics → calibration/accuracy/Wald CI。
- README、requirements，以及 Diamond 工具评测文档/依赖/blocklist 仅作配置审读。blocklist 的执行 wrapper 未提供给本次审读，不能把一份 JSON 当成已验证过滤器。

源码函数通过 AST 原样抽取执行，不复制到公开实验目录。API、数据集、并发收集器等替身在 probe.py 明确标出；独立 all-bin comparator 只用于诊断，不作为官方修复或替代榜单分数。

## 发现一：最高置信度 bin 没有计入校准误差

[run_judge_results.py L96–127](https://github.com/centerforaisafety/hle/blob/22ed3074b1e7b134bcbc09028d0ba320839b0655/hle_eval/run_judge_results.py#L96-L127)先按 confidence 排序，按 beta=100 创建 bins，把尾部余数并入最后 bin；但累计循环只遍历到 len(bins)-2。因此最后一组最高 confidence 样本未加入分子，分母仍为全部样本。

实际合成结果（此表为 0–1 RMS 原始值，不是印刷的百分比）：

| 样本 | 数据 | 源函数 RMS | 同样分箱、包含全部 bin 的诊断值 |
|---|---|---:|---:|
| 0 / 99 | 任意 | IndexError | 不定义 |
| 100 / 199 | 全错，confidence=1 | 0 | 1 |
| 200 | 全错，confidence=1 | 0.70710678 | 1 |
| 250 | 全错，confidence=1 | 0.63245553 | 1 |
| 1000 | 全错，confidence=1 | 0.94868330 | 1 |
| 2500 | 全错，confidence=1 | 0.97979590 | 1 |
| 1000 | 前900条confidence=0且全错；后100条confidence=1且全错 | 0 | 0.31622777 |

小规模 smoke test 尤其容易触发异常或虚假的零值。真实模型的差异大小、方向与排名影响取决于其逐题 confidence/正确性数据，不能由这些合成数字推算。

## 发现二：accuracy 和 calibration 使用不同样本基数

[dump_metrics L129–155](https://github.com/centerforaisafety/hle/blob/22ed3074b1e7b134bcbc09028d0ba320839b0655/hle_eval/run_judge_results.py#L129-L155)只收集有 judge_response 的记录；accuracy 的分母却是传入的数据集总数 n。缺失预测或缺失 judge 相当于没有正确答案，不缩小 accuracy 的分母；calibration 只使用已经 judge 的样本。

合成的 1,000 题中只有 200 个已判正确回答，输出是 accuracy 20.0% ±2.48%，而不是可用回答中的 100%。它也打印 Available predictions 与 Total questions，提醒样本不足。这可以是保守失败记账策略，但在不同重试/失败处理方式之间不能直接比较。

空的 judged_predictions 在 calibration 步骤触发 IndexError，最终 summary 无法打印。对于真实大批评测，应同时保存完成率、模型失败、judge失败与指标分母，而非只收集一个分数。

## 发现三：simple runner 的 CI 是 Wald，边界会退化

实现明确标注 Wald estimator：用已经四舍五入至两位的 accuracy、全题 n，算 1.96×sqrt(p×(100−p)/n)。这里是独立 Bernoulli 的渐近近似，不是 paired bootstrap、Wilson 或重复采样层次模型。

合成 200/200 正确产生 100.0% ±0.0%。零半宽不意味着已证明总体正确率为100%。不能把这个源码结论直接赋给官网所有置信区间，网站生产实现未核实。

Calibration 的打印顺序是先把 0–1 RMS round 到两位，再乘100，输出实质为整百分点精度。采样方差、judge变异、数据选择误差与部署稳定性不在此 Wald 区间中。

## 发现四：声明的 temperature 没有传到 API

README 和 CLI 声称默认 temperature=0，但 [prediction 调用 L31–40](https://github.com/centerforaisafety/hle/blob/22ed3074b1e7b134bcbc09028d0ba320839b0655/hle_eval/run_model_predictions.py#L31-L40)中相应参数被注释。传入 temperature=0.23 的合成测试捕获实际调用 kwargs，没有 temperature 字段。

这说明此脚本依赖服务端默认，而不是证明真实服务端用了某个数值。不可反向宣称网页上所有 temperature=0 的成绩都错误。

此外，prompt role 使用 model 名称是否包含 `o1` 来切换 user/system；image 字段直接进入 image_url，没有在这段脚本内解码、缩放或测试图像可达性。脚本仅转发并不证明后端视觉处理一致。

## 发现五：缓存身份不足以表达完整评测配置

prediction 文件只用 model basename 命名；dataset、revision、prompt、temperature、token budget 都不进入名字。按 question ID 跳过已有结果。合成的同名模型从 dataset A 切到 B，有相同 ID 的题继续复用旧响应。

judge 文件只用 prediction 文件 basename 命名；已含 judge_response 时直接复用，不校验修改后的 gold、回答或 judge版本。合成修改 gold 后旧 judgement 保留。文件同时没有强制把陈旧 ID 清理到当前题集；向 dump_metrics 传入300个旧正确记录、当前n=200，会进入sqrt负数并报错。这是缓存错配的组件风险，不是观察到的线上错误。

复现建议：外部 experiment manifest 明确 dataset revision、题ID集合hash、model endpoint/snapshot、生成参数、judge版本/prompt、代码commit。变更任何条件时使用新的输出目录，不覆盖旧证据。

## 发现六：并发与小样本开关的字面行为

prediction 和 judge 两段都在创建 tasks 外层先持有一次同一个 semaphore，再由每个任务获取。实际 prediction 合成测试 num_workers=2 峰值1、=3峰值2。main 断言必须大于1，避免单个permit被外层占满时无法继续。此处只测本地协程并发，未做真实API速率/吞吐测试。

max_samples=0 因 truthiness 判断表示不限量，不是0题；2表示前两题。二者都实际运行了原 main，但数据由三行合成 Dataset 替身提供。

## Diamond 工具协议：这是更完整的系统条件

[固定版本工具文档](https://github.com/centerforaisafety/hle/blob/22ed3074b1e7b134bcbc09028d0ba320839b0655/docs/evaluation-with-tools.md)明确：

- code sandbox 不能联网/下载/安装；外部资料仅经 web_search/web_fetch。
- Python3.11.16 与固定依赖，不增设专门 solver、棋引擎、OCR 等任务库。
- search 每次最多20结果，随后过滤；fetch只返回Markdown，60,000字符上限，不回媒体。
- blocklist需要wrapper真正执行；查询、结果URL/title/snippet、抓取内容、缓存、代理/归档内嵌URL都要检查并记录命中规则。
- 模型通过各自 provider harness：Opus5.5 使用 Claude Code2.1.280，Fable5.1/Opus5为2.1.278，Astra/Sol等使用CodexCLI0.155.1；不是统一裸API工具循环。未在此文档看到总step/token/wallclock上限。

这补全了 v9 中“工具推荐设置链接未读”的后续阅读，但不修改已经冻结的v9。网页成绩能否准确映射这个commit仍未核验。

## 数据访问边界与复跑

HF公开 metadata 返回 Diamond revision `04eeb7efa7e3e4f83a00cbd5ce436a38fd5dda23`、1,000条、gated=auto；rows请求返回401。本项目停止获取实际题目，没有绕过，没有下载/复制题目、答案或图像。因而不声称读取真实Diamond任务的D2。组件D3/D4仅覆盖上面的源码与合成实验。

在具备 NumPy 的隔离环境，先取得manifest内固定源文件，再运行：

```bash
python probe.py --source-dir /path/to/verified-hle-source --output /tmp/hle-results.json
```

可选 fetch_inputs.py 只下载并校验公开源码，不执行它，不取任何benchmark数据。本次通过连接器取得源码，未运行这个下载脚本。
