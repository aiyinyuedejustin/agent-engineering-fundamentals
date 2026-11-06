# ScreenSpot-Pro：定位一个点，不等于完成一次操作

研究日期：2026-11-06。代码固定为 `likaixin2000/ScreenSpot-Pro-GUI-Grounding@dbe00114bc53a32c61c1a267786da85967710da8`，数据固定为 `likaixin/ScreenSpot-Pro@210e78d3844251110bff86c95835ebd37a6930fa`。

本篇实际读取并复算全部 26 个标注 JSON，追踪串行/并行 evaluator、一个模型适配器和裁剪坐标转换。没有看到实际截图像素，没有运行视觉模型或操作桌面。D4 只表示标注统计与合成评分/流程实验，绝不表示复现 grounding 正确率。

## 1. 先核对真正计分的数据

固定数据树实际包含 1,581 行，task ID 和截图路径各 1,581 个，均无重复。当前同一版本 `eval.yaml` 的简介却写 1,585；本篇以实际 26 个 JSON 的枚举结果为准，而不是选择一个顺眼的简介数字。

- UI 类型：977 个 text、604 个 icon。
- 平台：Windows 927、macOS 604、Linux 50。
- 六个组：Creative 341、Dev 299、CAD 261、Scientific 254、Office 230、OS 196。
- 有 23 个专业应用条目，加上三个操作系统通用条目，共 26 个标注文件。不能把“26 个条目”与“26 个专业应用”直接互换。

实际读过的 `vscode_macos_0` 是刷新文件浏览器的图标定位任务，带中英文 instruction、像素 bbox、截图文件名、2560×1664 尺寸和 icon 标签。这里只描述任务形式，不复制完整题目/答案清单。后续统计覆盖全部标注，而非仅这个例子。

来源：[固定数据树](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/tree/210e78d3844251110bff86c95835ebd37a6930fa)、[VS Code 标注](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/blob/210e78d3844251110bff86c95835ebd37a6930fa/annotations/vscode_macos.json)、[eval.yaml](https://huggingface.co/datasets/likaixin/ScreenSpot-Pro/blob/210e78d3844251110bff86c95835ebd37a6930fa/eval.yaml)。

## 2. 从真实标注看高分辨率困难在哪里

把每个框面积除以对应截图面积，本次得到：

| 范围 | 平均面积占比 | 中位面积占比 |
|---|---:|---:|
| 全部 1,581 题 | 0.06508% | 0.03549% |
| icon 604 题 | 0.03078% | 0.01367% |
| text 977 题 | 0.08629% | 0.06522% |

1,321 个目标框小于整张截图面积的 0.1%。这能说明本集合中定位区域相对很小，但不能单靠框面积断言文字可读性、视觉对比度或模型究竟看不见什么，因为本次没有检查像素。面积统计按标注浮点几何计算，未做裁剪或 +1 像素修正。

一条标注 `inventor_windows_60` 的 y1 为 -1，稍越过图像上边界；本次保留原值计入统计，没有静默修改数据。它是一条边界质量记录，不是对整套标注质量或已发布分数的否定。全部来源文件和解析后规范化 JSON hash 随实验结果提供；hash 不宣称等于原 HTTP 字节 hash。

## 3. 计分事件是 point-in-box

核心正例 scorer 将 gold 的像素坐标除以原图宽高，得到归一化 bbox，再检查模型返回的归一化点是否落入矩形，四条边均包含。返回 None 判 wrong_format，其他未命中点判 wrong。它不评 bbox IoU，不要求预测框形状正确，也不执行点击或检查应用状态。

因此，能定位“运行”“删除”“发布”按钮，不代表真的运行成功、删除了正确对象或发布到了正确位置。自然语言 instruction 有时看起来像完整任务，但此处成功事件仍只是某一截图上的坐标命中。与 [OSWorld](osworld-state-evaluator.md) 的实际状态检查不能共享一个“GUI 成功率”定义。

总体 `action_acc` 是所有已返回结果的 micro average，wrong_format 也留在分母。text/icon accuracy 是各自子集分数，不应把两者简单平均冒充总体。空子集返回 0，需要同时读 num_total，避免把无数据解释为能力为零。所读 runner 没有逐题模型异常兜底；异常可能中断运行而非自动记错，必须核对最终结果条数与计划 manifest。

来源：[串行 evaluator](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/blob/dbe00114bc53a32c61c1a267786da85967710da8/eval_screenspot_pro.py)、[并行 evaluator](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/blob/dbe00114bc53a32c61c1a267786da85967710da8/eval_screenspot_pro_parallel.py)。

## 4. 模型适配器也是被测系统的一部分

读到的 Qwen2.5-VL 适配器先调用 smart_resize，按 patch_size×merge_size 处理尺寸，手动 max_pixels 设为 99,999,999；随后把 resized_image 传给 processor。这个手动值并不证明模型最终看到了同样的像素数，因为 processor 还有自己的处理路径，本次未加载 processor 或追踪其库内实现。

输出被引导为工具调用 JSON。若返回两个数，直接当点；若四个数，则取框中心。最后除以 resized_width/resized_height，转换到 evaluator 需要的归一化空间。图像原尺寸、手动缩放尺寸、processor 最终像素/token、输出坐标单位、最后归一化分母应分别记录，不能只写“原图输入”。

同文件的 vLLM 适配路径另设 mm_processor_kwargs，使用 temperature 0、max_tokens 100；普通 Hugging Face 路径与 model_factory 的 generation config 又不同。即便权重相同，这些也是不同可复现设置，不能只按模型名称合并结果。

裁剪/zoom 方法还需要第二次坐标映射。原始 view_bbox_to_real_bbox 先以 viewport 的宽高缩放，再加左上偏移。裁剪中心不一定是原图中心，遗漏偏移就会把局部坐标错投到全屏。所读 iterative_narrowing 默认最多三次 grounder 调用，每轮围绕预测中心缩小视野；与一次全屏推理不是同样的预算。它是静态图像搜索策略，不是多步应用控制。

来源：[Qwen2.5 适配器](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/blob/dbe00114bc53a32c61c1a267786da85967710da8/models/qwen2_5vl.py)、[model_factory](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/blob/dbe00114bc53a32c61c1a267786da85967710da8/model_factory.py)、[iterative narrowing](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/blob/dbe00114bc53a32c61c1a267786da85967710da8/models/methods/iterative_narrowing.py)。

## 5. 配置组合不能仅看 CLI 名字

在这个固定提交，官方 shell 示例使用英文、positive、instruction；本段额外组合实验不代表官方榜单运行了这些组合。

- 英文 `inst_style=all` 会扩展三个标签，但三个都取同一个 instruction 字段。本次原始 main 函数配合假模型验证：3 次调用、只有 1 个不同 prompt。不能把这说成三种措辞鲁棒性测试。
- 串行 main 的模型方法分派读取准备循环留下的最后一个 task_instance，而不是当前 sample。合成 `gt_type=all` 情况中，两个不同类型都走 negative 方法；并行 worker 则按每个 sample 自己的类型正确分派。默认全 positive 不触发这一差别。
- 输出字段叫 lang，通用筛选函数读取 language。自行按 language 筛选已有结果时要核 schema；默认 overall 统计不受该筛选字段影响。

这些结论来自组件级重现，未测出现频率，未核查任何已发布模型结果的受影响程度。将默认榜单问题与额外 CLI 组合问题区分开，比泛称“benchmark 有 bug”更有用。

来源：[官方运行脚本](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/blob/dbe00114bc53a32c61c1a267786da85967710da8/run_ss_pro.sh)、上述固定 evaluator。

## 6. 证据与复现边界

- D2（标注层）：固定版本的全部任务 metadata 已实际读取，示例指令、bbox、图像尺寸、类别、路径已核。截图链接访问失败；页面截图工具仅返回 URL 和 image 能力告警，没有可见像素。因此不声称完整视觉任务检查。
- D3（实现层）：数据展开→调用→坐标归一化→命中判分→micro 聚合已追踪；裁剪坐标映射已读。Qwen processor 内部行为未执行或完整追踪。
- D4（限定）：1,581 条真实标注统计与 20 个断言通过，后者包括原始串行 main 的临时 JSON 输入/输出、并行 worker、点框评分和裁剪转换；模型响应全部合成。没有模型分数、图像质量或真实点击实验。

脚本：[screenspot_contract_probe.py](screenspot_contract_probe.py)。结果：[screenspot-contract-probe-output.json](screenspot-contract-probe-output.json)。原始任务文本、答案框和图片不随研究产物再发布；通过固定源链接和规范化 hash 追溯。复跑读取本地 annotation bundle，不自动下载或调用 API。

实际选型建议：把这套基准用于定位模块的高分辨率小目标诊断，同时报告原图/最终像素、坐标尺度、crop 次数、text/icon、平台和应用切片；多步工作流另选状态型任务。已有榜单的 greedy decoding 和 micro-average 说明见[官方 leaderboard](https://gui-agent.github.io/grounding-leaderboard/)，仍应逐条核对其 wrapper 与预算。
