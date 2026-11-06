# VLMEvalKit 的 Video-MME-v2：输入适配比一个 benchmark 名称包含更多条件

观察日期：2026-11-06（UTC）。本文件是原创代码审读与实验分析，不是厂商成绩复现。

## 证据范围

- **D2，限定范围**：读取真实公开任务 `001-1` 的文本及元数据、数据集字段、配置与关键代码。没有观看其视频，没有核对任务内容或答案的正确性，也没有下载媒体。
- **D3，限定范围**：固定 `open-compass/VLMEvalKit@933eda4c27844b38f57ff6733ab72aa25110bd1b`，追踪配置 → 数据转换 → runner 的 prompt 分支 → 采帧/字幕 → 首层答案解析 → fallback 选择题匹配 → 分组汇总。未深入每个模型的 `generate` 或自定义 prompt 实现。
- **D4，限定范围**：实际运行18个合成组件探针，执行所固定源码中 AST 选取的原始函数体。模型调用0、judge调用0、实验网络调用0、真实视频打开0。不能据此给任何模型成绩、完整 benchmark 或 GPU 推理标 D4。
- 学习层级：组件层面的 L2；不声称完成部署或生产可靠性验证。

## 固定来源与真实任务检查

九个来源文件的 Git blob SHA 与 SHA-256 均在执行前核验，见 [source-manifest.json](source-manifest.json)。核心入口：

- [video_dataset_config.py，108–154行](https://github.com/open-compass/VLMEvalKit/blob/933eda4c27844b38f57ff6733ab72aa25110bd1b/vlmeval/dataset/video_dataset_config.py#L108-L154)
- [VideoMMEv2 类及评分辅助函数](https://github.com/open-compass/VLMEvalKit/blob/933eda4c27844b38f57ff6733ab72aa25110bd1b/vlmeval/dataset/videommev2.py)
- [runner：inference_video.py](https://github.com/open-compass/VLMEvalKit/blob/933eda4c27844b38f57ff6733ab72aa25110bd1b/vlmeval/inference_video.py)
- [Video-MME 选项提取工具](https://github.com/open-compass/VLMEvalKit/blob/933eda4c27844b38f57ff6733ab72aa25110bd1b/vlmeval/dataset/utils/videomme.py#L121-L179)
- [通用选择题 fallback](https://github.com/open-compass/VLMEvalKit/blob/933eda4c27844b38f57ff6733ab72aa25110bd1b/vlmeval/dataset/utils/multiple_choice.py#L346-L405)
- [字符/选项文本匹配](https://github.com/open-compass/VLMEvalKit/blob/933eda4c27844b38f57ff6733ab72aa25110bd1b/vlmeval/utils/matching_util.py)
- [官方数据页](https://huggingface.co/datasets/MME-Benchmarks/Video-MME-v2)及[单条公开元数据 API](https://datasets-server.huggingface.co/rows?dataset=MME-Benchmarks%2FVideo-MME-v2&config=default&split=test&offset=0&length=1)。API 观察到3200行、11个原始字段，`question` 与 `options` 分列，首条 `question_id=001-1`、`video_id=001`、logic组结构 `[1,2,3,4]`。该数据观察未固定 HF revision，不等于可重现的数据快照。本文不再发布任务题干、选项或媒体。

## 从配置到评分的路径

1. 配置中注册14种 v2 别名，区分64帧/1fps、字幕、字幕交错、reasoning和resize。`reasoning` 改的是输出提示格式，不是某个API供应商的推理预算。
2. `prepare_dataset` 从 HF 或 ModelScope取数据，未提供revision。由 `test.parquet` 生成TSV，保留 `question` 与 `options` 两列。缓存完整性检查采用固定TSV MD5和视频路径存在性，不验证视频/字幕内容哈希。
3. runner根据模型与backend选择raw-video或image-list。Gemini genai的固定帧配置会改为多图；vertex路径也改为多图。部分本地模型可以使用 `model.build_prompt`，绕过下述数据集prompt；因此本文不能外推到所有模型。
4. 数据集默认 `nframe=64, fps=-1, with_subtitle=False, subtitle_interleave=False, reasoning=False, resize_target_area=False`。固定帧取 `int(i*N/(K+1)), i=1..K`；fps模式取 `int(duration*requested_fps)` 帧，从索引0开始。两种方式的端点、帧数和字幕覆盖不同。
5. image-list模式按帧时间组织字幕；raw-video模式只给视频路径与尺寸/采样元数据，再把全部字幕拼成一个文本块。框架把参数写进消息，不等于每个模型backend都照此执行。
6. `evaluate` 首先使用A–H正则提取；只有结果为空才进入fallback。默认judge名为 `gpt-4o-mini`，缺key或不可用时会退为无judge的匹配路径。已有score文件会直接进入汇总，跳过重新解析，所以重新配置judge并不必然重算旧分。
7. `get_final_rating` 每连续4行组成一组，并从组末行取得level/category；不按question_id重新排序或分组。输入顺序属于计分契约，不能打乱后直接评分。relevance和logic为组级指标，不能称为逐题accuracy。

## 已运行的18个组件探针

输出完整记录见 [results.json](results.json)，驱动程序见 [probe.py](probe.py)。所有输入均为自造fixture。

### A. 同名字幕配置不保证相同信息量

合成视频元数据为10帧、1fps，固定取3帧得到 `[2,5,7]`，不是 `[0,5,9]`。字幕 `early` 位于0–0.5秒，image-list交错模式从第一个采样帧2秒开始，因此未包含 `early`；同样字幕在非交错模式及raw-video模式均保留。

字幕helper注释写重叠区间 `[start,end)`，实现判断 `word.end >= start` 且 `word.start < end`。合成词 `edge` 位于1.5–2.0秒，同时出现在 `[0,2)` 与 `[2,5)` 两块中。该边界词重复是实测组件行为，不代表官方真实字幕一定有这些边界值。

补充边界探针：10秒视频、0.05fps时，取整得到0帧，函数返回空列表。是否应拒绝这种配置需要任务策略决定，不能推导为所有默认配置的问题。

### B. `resize=False` 在两条prompt路径不等价

raw-video分支不读取 `resize_target_area`，总是按约448×448面积、16倍数计算尺寸。合成1080×1920元数据得到宽592、高336，尽管flag为False。image-list分支则在该flag为真时才执行数据集侧resize。

实验证明的是发送的prompt元数据；没有调用真正的视频decoder、API或模型processor，不能声称最终模型看到的像素尺寸就是592×336。

### C. 首层A–H正则并非“读取最终答案”

- `Final Answer: D` → D。
- `Based on the video, Final Answer: D` → B。
- `I first considered A, but Final Answer: D` → A。
- `circle` → 空字符串，进入fallback。

正则会移除若干固定前缀，再取剩余文本中的第一个大写A–H。reasoning提示允许详细推理，因此“前面推理的字符”与“最终选项”冲突是需要测试的具体条件。但本文没有统计真实模型输出中该条件的发生率，不声称任何现有榜单偏差大小。

### D. 分列选项与fallback的输入契约不一致

数据转换和已读真实元数据都保留独立 `options` 列，prompt构造也正确拼接 `question + '\n' + options` 给模型。可是fallback `extract_option` 只从 `input_item['question'].split('\n')[1:]` 创建A/B等选项键，没有读取 `options`。

执行原始 `extract_option → extract_answer_from_item → build_choices → can_infer` 链、设置 `model=None`：

- `question='Which shape is shown?'`、独立 `options='A. square\nB. circle'`、回答 `circle`：choices为空，结果Z。
- 相同选项直接写入question的后续行、回答仍为 `circle`：choices为A/B，结果B。

这验证了无judge路径中的特定fallback差异。语言检测仅对本合成英文fixture固定为False；选项构造、prompt构造与匹配函数体未经改写。没有调用LLM judge，不对有judge时的所有结果作断言。

## 如何复跑

需要Python、NumPy、pandas、Pillow。实验记录为Python3.12.14、NumPy2.3.5、pandas2.2.3。无需安装VLMEvalKit完整依赖、decord或模型权重。

1. 可使用 `python fetch_inputs.py /tmp/vlmevalkit-probe-inputs` 获取固定commit的九个来源文件并校验Git blob。这个下载辅助脚本没有在本研究中实际执行；本次来源文件通过GitHub读取接口取得并核验。
2. 运行 `python probe.py --source-root /tmp/vlmevalkit-probe-inputs --output /tmp/vlmevalkit-probe-results.json`。
3. 对照 `results.json` 的18项 `actual/expected`。不要将零API组件测试写作模型或视频任务复现。

程序会动态读取固定来源、用AST选择原始类/函数体；不在公开成果中嵌入上游源文件。decord被仅返回形状、长度和fps的fake替代，缓存帧是空临时文件，避免任何图像解码。只覆盖上述行为，不模拟整个benchmark运行。

## 对模型报告阅读的结论

一条“Video-MME-v2成绩”至少还要附带：实现仓库及commit、数据revision、采帧方式/数量、raw-video或image-list、模型自定义prompt是否启用、字幕方式、resize执行位置、reasoning提示、解析器和judge、是否复用了score缓存，以及逐题还是组级指标。缺项时可以引用报告数值，但不宜拿它作严格横向排名。

这些源码和实验没有证明任何官方成绩错误，也没有给出更正后的模型分数。下一步若要测实际影响，需要合法取得媒体、固定真实预测日志、记录模型与backend版本，比较同一批预测在不同解析/预处理契约下的变化，并保留费用和可重复性证据。
