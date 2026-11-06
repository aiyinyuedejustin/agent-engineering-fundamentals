# Ovis2.5：原生分辨率、媒体打包与思考预算的实现契约

观察日：2026-11-06。原创源码分析与合成组件实验。19个探针实际通过，模型/判分器/实验网络调用均为0。没有运行权重或真实图像题目，也没有复现Ovis报告分数。

## 范围与版本

- **D1**：读官方Ovis2.5论文、模型卡、配置，以及公开示例任务的文字。尝试打开示例图像时工具未返回可见像素，所以不声称看过实际图像或完成真实视觉任务。
- **D3，组件限定**：跟踪GitHub demo/chat → formatter → preprocess → patch/grid → visual placeholder → merge/generate的源码路径。真实视觉编码、attention计算和模型答案没有执行。
- **D4，组件限定**：动态加载经过blob哈希核验的原始方法AST，在synthetic输入上测试resize、patch packing、placeholder计数和双阶段chat控制流。Torch未安装，显式使用NumPy张量替身；这不是Torch后端的数值一致性测试。
- L2仅适用于组件实验，不宣称生产部署能力。

官方旧组织链接AIDC-AI现指向ATH-MaaS。旧路径的GitHub文件读取失败后，通过官方网页解析得到新仓库，并使用新仓库接口读取；不是访问受限仓库的绕行。

本次发现两种不同交付实现，必须分别固定：

1. [GitHub ATH-MaaS/Ovis](https://github.com/ATH-MaaS/Ovis/tree/e1916bf3cb0ca123e71ab173ff4463df5c3a71b5)，commit `e1916bf3cb0ca123e71ab173ff4463df5c3a71b5`。八个文件的Git blob SHA及SHA-256见 [source-manifest.json](source-manifest.json)。**本次可执行实验只对这条实现负责**。
2. [HF Ovis2.5-9B](https://huggingface.co/ATH-MaaS/Ovis2.5-9B)，官方[模型API](https://huggingface.co/api/models/ATH-MaaS/Ovis2.5-9B)返回revision `d73b2283ae2a930b7762f8d7b8b8a3f0f3b5c3bd`。已读该revision的[modeling_ovis2_5.py](https://huggingface.co/ATH-MaaS/Ovis2.5-9B/raw/d73b2283ae2a930b7762f8d7b8b8a3f0f3b5c3bd/modeling_ovis2_5.py)；检索器会移除部分特殊token和缩进，因此未将返回文本当作字节完整源码执行，也未声称核验其文件blob。

GitHub类为 `Ovis`，配置类型 `ovis`，入口使用 `text_or_conversations` 与单独的images/videos，双阶段预算在 `chat`。HF的auto_map指向 `Ovis2_5`、`ovis2_5`，入口使用messages，双阶段预算在 `generate`，另有 `enable_thinking_budget` 开关。示例代码看似都叫Ovis2.5，不等于接口与默认值完全一致。

## 1. “原生分辨率”不是“永不resize”

[GitHub VisualTokenizer](https://github.com/ATH-MaaS/Ovis/blob/e1916bf3cb0ca123e71ab173ff4463df5c3a71b5/ovis/model/modeling_ovis.py#L36-L157)以 `patch_size × hidden_stride` 作为尺寸倍数。官方配置是16×2=32，而helper形参上的通用默认factor28不是实际调用值。

直接 `preprocess_inputs` 默认像素区间为448²至1344×1792；GitHub `chat` 与HF `preprocess_inputs` 默认最大面积则为1792²。GitHub单图demo采用1792²，多图采用896²。像素限制必须连同入口和参数保存，不能只抄一个default。

执行原始resize方法、采用直接preprocess默认上限后：

- 2160×3840 → 1152×2048。4K输入被缩小。
- 100×100 → 448×448。低分辨率输入被放大。
- 1080×1920 → 1088×1920。尺寸按32倍数舍入，宽高比只能近似保持。

这些是尺寸算术结果，不是视觉质量实验。NaViT避免固定切块的结构优势与输入仍受像素预算约束可以同时成立。

## 2. 每帧面积、patch数量与视觉token不是一回事

`preprocess`读取第一帧的尺寸，然后用该尺寸为同一video列表中的所有帧计算目标大小。合成200×100与100×200两帧均被请求处理为宽64、高32，说明混合宽高比帧会沿用首帧形状。正常同尺寸视频不触发这种差异；本实验不声称官方视频有变尺寸帧。

每帧调用一次图像processor，因此max_pixels是逐帧预算，不是所有帧共享的总面积预算。两个合成帧产生grid `[2,2,4]` 和16个patch行；hidden_stride=2后对应4个visual atoms。提示中的媒体占位符还会添加起止标记，不能只用“帧数×分辨率”代替全部上下文token预算。

本实验processor返回零数组，只验证打包维度与传参，不测试PIL插值、归一化、视觉编码器数值或图像识别能力。

## 3. 边界探针要与已发布配置分开

合成边界发现：

- 高宽比极大且短边≥32时，先把比例截为200；32×100000变32×6400，不是保留原比例。
- 短边小于32走另一分支，1×10000经后续floor可得到0×155168。这里只计算尺寸，没有调用真实processor；可以作为输入校验测试，不代表常规照片路径失败。
- min_pixels=max_pixels=448²时，100×200经ceil对齐产生320×640=204800，大于目标200704。等上下限与离散patch格点存在冲突，调用方不能把该参数理解为严格精确像素数。

官方检查点 `temporal_patch_size=1`。另测的2/3属于**非发布默认配置**：size2时placeholder数量多除一次temporal尺度，size3且输入2帧时padding后reshape报ValueError。它们是参数扩展的边界证据，绝不能写成“已发布Ovis2.5模型发生视频bug”或用于推翻其榜单分数。

## 4. 思考预算包含控制流与额外提示

[GitHub chat实现](https://github.com/ATH-MaaS/Ovis/blob/e1916bf3cb0ca123e71ab173ff4463df5c3a71b5/ovis/model/modeling_ovis.py#L468-L609)在启用thinking且设置正budget时先生成第一段。如果尚未出现结束消息且缺思考结束标记，会插入一段强制结束提示，再用剩余总budget生成第二段。

使用固定token输出替身，而非语言模型：

- 第一段3token、桥接提示3token、总budget10 → 第二段只剩4token。
- 第一段已包含思考结束标记时不插桥接，实际消耗2token → 第二段可用8token。
- 第一段已含消息结束标记 → 跳过第二段。
- 未设置thinking_budget → 仅调用一次、使用整个max_new_tokens。
- 总budget4却第一段3token、再插3token桥接时，最终可超过总预算并无最终回答。这个刻意不足的边界配置不符合HF示例推荐的余量条件，不能外推为常规配置的输出超限。

GitHub更新history只保留最终response，不保留返回的thinking字符串；本实验只用无语义整数token验证流程，没有生成或记录任何模型推理内容。

HF remote-code把两阶段逻辑放在另一入口，其官方卡特别要求 `max_new_tokens > thinking_budget + 25`，还说明默认TextIteratorStreamer不兼容，需要手动结束的streamer helper。上述GitHub探针不能替代HF实现的运行验证。HF解析文本不完整时，尤其不能从缺失的特殊token猜测其真实字符串。

## 复跑与文件

- [probe.py](probe.py)：原创驱动，运行时从外部源码路径选取原始方法AST。
- [results.json](results.json)：19项actual/expected与环境、替身和局限。
- [fetch_inputs.py](fetch_inputs.py)：可选固定commit下载脚本，本研究没有实际运行它；本次源码通过GitHub接口取得并核验。

准备固定源码后执行：

`python probe.py --source-root /tmp/ovis-probe-inputs --output /tmp/ovis-results.json`

仅需Python、NumPy、Pillow，无需Torch、模型权重、CUDA或网络推理。公开成果不包含上游源码副本、真实任务图片或报告全文。

## 对评测设计的启示

保存模型名称之外，至少固定分发源、checkpoint revision、remote-code/仓库版本、入口函数、单图/多图/视频像素预算、采帧方法、patch合并、模板、thinking预算及streaming接口。源码路径与组件行为可以达到局部D3/D4，但它们不能替代真实任务的输入检查、模型执行或成绩复现。
