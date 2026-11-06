# RULER：有效上下文不是一个长度数字

研究日期：2026-11-06。本篇研究生成任务、长度预算、评分事件与版本迁移，不比较模型名次。没有调用模型、下载 tokenizer、准备正式 4K–1M 数据集或复现论文成绩。

## 先把三个实现分开

- NVIDIA/RULER 主仓固定在 `db43f92ff634bbce1c33d1fb15858aec4bba509a`。其中保留经典 13 子任务代码，但当前 README 已把旧运行方式标为 deprecated，推荐 `rulerv1-ns` / `rulerv2-ns`。
- 两个指南分支分别固定为 `e8bbff677ca2c239640dc90f93310dcf32408c93` 和 `4809570a2a40e803bfe341773e561524224c2e7c`。后者指向 NeMo-Skills 的历史工作分支；本次该工作分支查询返回 404，因此没有把它当作可复现版本。
- 本次实际读到的 NeMo-Skills 主干是 `bcf059af55c20a89f797724598f9908d126153e6`，同时包含 ruler、ruler2 的生成、评分与分组模块。以下新实现结论仅属于这个固定提交，不能等同于历史分支或某篇模型报告的运行环境。

来源：[RULER 主仓 README](https://github.com/NVIDIA/RULER/blob/db43f92ff634bbce1c33d1fb15858aec4bba509a/README.md)、[v2 指南](https://github.com/NVIDIA/RULER/blob/4809570a2a40e803bfe341773e561524224c2e7c/README.md)、[NeMo-Skills ruler2](https://github.com/NVIDIA-NeMo/Skills/tree/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler2)。

## 1. 任务空间：长度、难度与问法是不同变量

经典 RULER 有检索、变量跟踪、词频聚合、问答四类、13 子任务。配置既改变背景类型，也改变 key/value 类型、需要返回的值数和查询数。变量跟踪默认一条四跳链；词频题要求在大量词中恢复高频项。这些任务并不是一个 needle-in-a-haystack 换 13 个名字。

本次运行原始变量跟踪生成器的核心函数：20 段重复背景、一条四跳链、研究者指定随机种子 20261106。实际生成五条赋值、五个目标变量，赋值在文本中保持因果顺序。已读出任务 prompt 和答案，并保存生成过程与摘要。这是一个由官方生成器构造的真实任务实例，但不是正式长度校准后的官方测试样本，不含模型回答或正确率。

NeMo-Skills 的 ruler2 则把 12 子任务分成三组各四档：

- `mk_niah`：基础数字检索；复制指定 MMLU 题；先复制再求解 MMLU；直接求解 MMLU。
- `mv_niah`：同一 key 的多个数字；同一编号的多个题目；先列出匹配项再复制指定顺序的题目；直接复制指定顺序的题目。
- `qa`：由文段找文档编号；由问题找相关文档编号；先复制证据再回答 HotpotQA；直接回答 HotpotQA。

这里的 medium/hard 不只增加 token。它们改变输出事件、是否提供中间步骤以及部分题的 few-shot 数量。MMLU 求解题用 5 个示例，复制题通常为 0。ruler2 因而混合了上下文检索与已有知识/推理能力；不宜把总分差异都归于注意力能否覆盖长距离。

来源：[经典任务配置](https://github.com/NVIDIA/RULER/blob/db43f92ff634bbce1c33d1fb15858aec4bba509a/scripts/synthetic.yaml)、[变量跟踪生成器](https://github.com/NVIDIA/RULER/blob/db43f92ff634bbce1c33d1fb15858aec4bba509a/scripts/data/synthetic/variable_tracking.py)、[ruler2 任务定义](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler2/prepare.py)、[题目检索生成器](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler2/prepare_mmlu.py)。

## 2. 长度是生成过程的约束，不是同一份文本的标签

经典生成器用指定 tokenizer 测量输入长度，并留出子任务的生成预算。NeMo-Skills v1 适配器还默认扣除 50 个聊天模板 token。它按 `default` / `base` / `chat` 改变 answer prefix 的位置：前两种放在 assistant generation 起始，chat 移除前缀；前两种同时设置 text-completion 端点及任务特定输出上限。不要把三种 data_format 视为无关紧要的导出选项。

ruler2 的 NIAH/QA 生成器用 tokenizer 对完整生成的输入文本计数，搜索能容纳的背景规模，然后逐题回退长度。虽然参数帮助文字提到输入加生成，所读实际比较的是输入 token 数；本次没有看到从这个上限扣除输出 token 的步骤。v2 指南另给 16384 输出 token、temperature 0，服务示例设置 max-model-len 131072。报告应分别记录实际输入长度、模板开销、输出额度、服务总上下文上限，不把一个 `max_seq_length` 当成全部预算。

生成过程的搜索会消耗随机数。即使随机种子相同，不同 tokenizer 导致不同搜索轨迹和背景规模，也不能默认得到相同题目文本或 target 值。需要同时保存生成后 JSONL 的 hash、tokenizer revision、生成器 revision、种子、长度分布和复杂度参数。

v1 适配器默认运行未固定 revision 的 `git clone` 和数据下载；提供已有临时目录时，只检查若干文件存在便可复用。固定 NeMo-Skills 提交本身还不足以固定被调用的 RULER 与外部语料。

来源：[v1 适配器](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler/prepare.py)、[v2 NIAH 长度生成](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler2/prepare_niah.py)、[v2 QA 生成](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler2/prepare_qa.py)。

## 3. 分数不是“整题完全正确”的同义词

经典 `string_match_all` 名字中的 all 不代表所有目标同时正确才得分。它计算每题目标字符串的召回比例，再跨题平均。返回两个目标中的一个得 50%；多输出错误项不扣分；匹配不要求单词边界。QA 的 part 则接受任意一个答案别名。

NeMo-Skills v1 保留这一事件。ruler2 对每个 reference 取两者较大值：大小写无关 substring 命中，或 `1 − WER`。因此长句复制允许部分分，而完整 reference 出现在一段带额外内容的回答中仍可获满分。这里 WER 是空白分词后的词级编辑距离，不是语义判断。

ruler2 还因任务切换评分器：

- `mv_niah_medium` 的 2steps 只评最后一个双换行分段。
- QA 的 part 路径先按正则移除特定 `Document N:` 复制段落，再对答案别名评分。
- 两个 MMLU 求解任务使用独立 multichoice 路径。本次读了路由配置，但没有把该选择题 evaluator 的所有细节当成本篇已审计范围。

外层 evaluator 会保存清理控制字符后的 predicted_answer，实际调用匹配函数时却传入原始 generation。这两个字段不必得到相同分数。本次用一个带控制字符的合成输入验证了这一差别；没有证据表明它影响已发布成绩。

来源：[经典评分](https://github.com/NVIDIA/RULER/blob/db43f92ff634bbce1c33d1fb15858aec4bba509a/scripts/eval/synthetic/constants.py)、[NeMo-Skills v1/v2 evaluator](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/evaluation/evaluator/ruler.py)。

## 4. 总分、曲线和有效长度回答不同问题

NeMo-Skills 两个组分数分别对 13 或 12 子任务做等权平均。该组聚合器假设任务全部存在；本次验证缺少任务时抛出 KeyError，而不是自动平均已完成子集。保存原始子任务分数能防止总分掩盖某一任务或长度崩溃。

经典 README 的 effective length 依据 85.6% 定性阈值，这来自 Llama-2-7b 在 4K 的基线，并不是所有现实工作都认可的成功标准。超过该阈值说明在这组任务、难度、评分和预算下达标，不代表该长度内所有信息都可靠可用。不同长度的算术平均、随长度递增/递减的加权平均也对应不同使用分布。

选择模型时优先画“任务类型 × 长度”的表现面，再以真实工作负载所需的质量阈值和长度分布汇总。企业文档问答、长代码库、音视频流应另用相应任务验证；合成 RULER 可以隔离某些机制，但不能替代领域成功事件。

来源：[v1 分组评分](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler/ruler_score.py)、[v2 分组评分](https://github.com/NVIDIA-NeMo/Skills/blob/bcf059af55c20a89f797724598f9908d126153e6/nemo_skills/dataset/ruler2/ruler2_score.py)、上述固定 README。

## 5. 实验与证据边界

- D1：两仓官方说明、历史分支指南和当前推荐迁移路径已核。
- D2：实际读取经典生成配置、模板，并运行其核心构造一条变量跟踪任务；没有正式 tokenizer 校准数据集。ruler2 运行了允许但非默认的数字 key 配置；未读取由正式 word-key/MMLU/HotpotQA 流程产出的测试 JSONL。
- D3：经典任务生成到匹配、NeMo-Skills v1 适配、v2 生成/路由/聚合已追踪；MMLU 独立选择题 grader 仅核路由。
- D4（限定组件）：20 个断言通过，包括两个生成器核心、原 evaluator 的临时 JSONL 读写、评分算术和分组聚合。因为 editdistance 未安装，明确用脚本中的标准 Levenshtein 动态规划替代该依赖；未验证其安装和二进制实现。

脚本：[ruler_contract_probe.py](ruler_contract_probe.py)。结果与 6 个本地源文件 SHA256：[ruler-contract-probe-output.json](ruler-contract-probe-output.json)。复跑需要按脚本列出的文件名提供固定提交源文件；没有自动下载、安装依赖或 API 请求。

本篇可达到 L2 的协议选择与诊断理解，不能据此认定已具备完整部署/服务/长序列资源调度的 L3 经验。与 [LongBench v2](longbench-v2-protocol-audit.md) 的真实长文档任务、[跨 benchmark 测量契约](../02-benchmark-landscape/measurement-contracts-guide.md) 配合阅读。
