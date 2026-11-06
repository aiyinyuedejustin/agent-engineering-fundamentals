# 第三批：协议差异与多模态报告

研究仍处于采集阶段。本文记录具体原文章节，不生成跨厂商总排名。读取日为2026-11-06。工作登记册共113条来源记录，其中34条D1、79条D0；数值观察147条，均为报告作者所报、未独立复现。深度只针对注明的章节。

## 1. GLM-5：修改环境后要改记录，不只改分数

原始来源：[GLM-5论文](https://arxiv.org/html/2602.15763)，§6.1–6.3与附录B.2–B.4。

Terminal-Bench2.0同时报告原版与zai verified修改版：Terminus2为56.2/60.7，Claude Code为56.2/61.1。verified版修订了模糊指令，不能把更高值直接覆盖原版。两种harness的运行预算还不同：Terminus2为2小时、8192输出token、128K上下文；ClaudeCode2.1.14移除了墙钟时间上限、65536输出token、5次平均。

MCP-Atlas使用500题公开集、10分钟超时，而非原4分钟，judge为Gemini3Pro。报告称所有基线重跑，此处是作者的同协议对照，不等于原官方榜单。

“BrowseComp without context management”在附录中仍然只保留最近5轮细节。因此标签不应被机械翻译成“全量历史不丢弃”。研究记录保留作者命名，也另存实际行为。

内部CC-Bench-V2前端集有220个任务、949个检查项。指标分三层：构建成功BSR、检查项成功CSR、所有要求都满足的任务成功ISR。React上GLM5的CSR71.0略高于Opus4.5的70.7，但ISR34.6低于39.7。这说明细项平均不能代替端到端完成率。Agent-as-a-Judge由ClaudeCode+Sonnet4.5+Playwright构成，论文称130个check-items与人类94%一致、8模型排名Spearman85.7%，这只是特定验证样本，并非完美judge证明。

Large Repo Exploration只要求agent读到目标文件；分数不能解读为理解或修改成功率。Chained Tasks的状态累积、旧测试累积，但报的是单任务pass@1，而非整链全部成功。SWE-rebench January2026的resolved rate与pass@5也分开保留。

元数据警告：检索器把这篇论文Author误标为Anthropic，正文明确为GLM-5 Team、Zhipu AI与清华大学。发布日期元数据也与早期发现日期不同。版本日期未解决前不补造精确修订时间。

## 2. LongCat-Flash：相同题目、不同判分器，仍不是同一实验

原始来源：[LongCat-Flash v2](https://arxiv.org/html/2509.01322v2)，§4.4。

报告对若干通识、GPQA和MATH500使用语义评分模型，替代原先exact match，并明确称结果可能比原文高。GPQA-Diamond73.23应带上“model-judged”标签；不能直接混入纯规则抽取的GPQA榜单。

GraphWalks报告precision与128k子集，和另一份报告的BFS F1、256K–1M子集不等价。AceBench使用direct prompting而非function calling。SWE-bench采用R2E-Gym的OpenHands、100次迭代，但DeepSeek-V3.1和Claude4Sonnet的数值来自别的公开报告，表格不能整体标成“所有模型同框架重跑”。

VitaBench在这版报告里是proprietary，宣布未来公开。记录此时点的状态不代表它今天仍未公开，也不意味着论文已提供全部可运行数据。

## 3. MiMo-V2-Flash：容器也有数据泄漏面

原始来源：[MiMo-V2-Flash v2](https://arxiv.org/html/2601.02780v2)，§4.5、附录B/C。

附录B讨论SWE-Bench官方镜像中未删除未来ground truth commits导致的reward hacking，作者称已更新评测镜像，并处理自建训练镜像。因此任务JSON和harness commit相同也不充分，镜像、git对象历史和可访问文件会改变问题本身。这里记录作者陈述，没有独立检查其训练镜像。

tau2用户agent是DeepSeek-V3.2，而非GPT-4.1；MRCR合并2/4/8 needles，不能替代8-needle AUC@128k。BrowseComp58.3归因于激进reset，附录同时描述summary/file-memory流程，不能从一个“context management”标签反推完整可执行配置。

## 4. ERNIE4.5：base、post-trained与multimodal不共用默认提示

原始来源：[官方PDF](https://ernie.baidu.com/blog/publication/ERNIE_Technical_Report.pdf)，封面2025-06-29，§8.1与部分§8.2。

Base评测有5-shot通识、10-shot SimpleQA、3-shotBBH、8-shotMATH、0-shot代码等；post-trained比较使用non-thinking模式；多模态任务说明是zero-shot。SimpleQA base38.4与post-trained45.9不能在未控制提示与训练差异时解释成“只经post-training提升7.5分”。表4的竞品由作者重跑，不是照抄其发布分数。

## 5. Qwen3-Omni：任务、模态和输出形式必须一起登记

原始来源：[Qwen3-Omni报告](https://arxiv.org/html/2509.17765)，§2.5、5–6、附录9.1。

### 指标方向不能统一成“越高越好”

- ASR的WER越低越好；19语言Fleurs上30B-A3B Instruct为5.33，Thinking为8.63。这里reasoning不是对感知任务的通用增强开关。
- S2TT用BLEU，音乐多标签分类使用micro-F1，不用AP/AUROC。理由是语言模型输出离散标签集合，没有可校准逐标签概率。不能把F1直接拼入旧概率排序指标的曲线。
- Speech generation评估主要是给定文本生成语音，检查内容一致性与speaker similarity。它不覆盖完整实时对话中的打断、轮次管理或任务完成。

VoiceBench表7区分30B-A3B-Thinking88.8与Flash-Thinking89.5，周围文字提到Thinking89.5容易让人误归到公开30B变体。证据表按明确列名登记，同时保存这处表述歧义。

### 首包延迟不是端到端完成时间

表2称“theoretical first-packet latency”。音频/视频在并发1时为234/547ms，并发6时为1172/2284ms；这是vLLM及特定编译/图优化下分项相加的口径，读到的章节没有给出准确硬件型号。不能省略并发、输入模态，把234ms宣传成所有部署的完成时间。

### “不退化”需要有明确的统计命题

§6的控制实验对齐30B-A3B规模、同模态语料、训练计划和FLOPs，比简单比较各自旗舰模型更有证据价值。但MMLU-Pro仍有61.81→61.57，RealWorldQA73.98→71.89、MVBench71.87→69.50等点估计下降。作者也说明无法扫描所有规模。它支持特定实验下整体能力保持的讨论，不证明每个任务不下降，更没有在此表给出统计等价性检验。

## 6. InternVL3.5：grounding、online agent与具身问答分别解释

原始来源：[InternVL3.5报告](https://arxiv.org/html/2508.18265)，§2.4–2.5、3.1、3.10–3.15。

默认实验除特别说明外不做test-time scaling。Parallel Thinking使用VisualPRM-v1.1做best-of-N选择，这不是多数投票，也不能和单响应无critic系统合并。

ScreenSpot-v2与OSWorld-G是GUI grounding，WindowsAgentArena和WebArena-Lite-v2是online agent任务。241B-A28B分别92.9、53.2、18.0、11.7不能仅按分数差解释难度；任务目标完全不同。在线步数默认50，部分带标记竞品100或200，比较表需要保留这条脚注。

论文“Embodied Agent Tasks”章节评估VSI-Bench、ERQA、SpaCE-10、OmniSpatial；其中SpaCE-10报告single-choice。不能把空间问答成绩自动升级成真实机器人的动作控制成功率。实际动作空间、闭环控制、接触动力学和机器人安全没有在这些表里证明。

基础设施部分将视觉encoder/MLP与语言模型分到不同服务器，通过异步流水传BF16特征。吞吐变化可能来自视觉分辨率router与部署解耦，不应全部归因于模型参数量。

## 7. HunyuanVideo1.5：胜率可以是差值，低显存和高速可能来自不同配置

原始来源：[HunyuanVideo1.5 v2](https://arxiv.org/html/2511.18870v2)，§5–6。

GSB评测使用300个T2V prompts、300个I2V images、100多名专业评审。作者称每输入只运行一次、没有挑样，竞品使用默认配置。

表5对Veo3的T2V结果中，HY Better24.64%、Other Better34.96%，所谓HY Win Rate为−10.32%。它实际上是24.64−34.96的**偏好率差（百分点）**，不是赢的概率。平局又分equally good与equally bad。忽略这个定义会把同名“胜率”解释错。

推理速度表使用CFG-distilled模型、8张H800、context parallel。720p241frames、50步、有工程加速时，稀疏attention的总时间58.39秒，对照96.78秒。另一个13.6GB峰值显存数字来自单GPU、pipeline/group offloading与VAE tiling、720p121frames。不能组合成“单卡13.6GB，241帧58.39秒”的虚构配置。

## 8. 新增来源线索与日期边界

本轮增补Ling2.0、KAT-Coder、HunyuanImage/MT、Ovis、InternVL-U、StepAudio、MiMo-Audio、QwenAudioGen、Seedance等来源线索。只看到搜索结果的记录仍D0；openPangu链接实际是Git LFS指针，不当成读过PDF。Seed1.5-VL、Seedream3.0与Wan2.1早于2025-06，未作为期内新报告纳入本批新增计数。

[Seedance2.0官方出版页](https://seed.bytedance.com/en/public_papers/seedance-2-0-advancing-video-generation-for-world-complexity)日期为2026-04-15，正文称模型在中国于2月初发布。D1只覆盖页面和摘要；尚未读完整实验报告，不登记能力分数。
