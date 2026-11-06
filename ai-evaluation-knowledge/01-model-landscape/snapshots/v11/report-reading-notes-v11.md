# 新一代音频/图像报告：用户体验、指标与服务端配置

日期：2026-11-06。新增五份既有候选的正文审读：Qwen3.5-Omni v1、LongCat-Flash-Omni v2、HunyuanImage3.0 v3、StepAudio2.5 v1、StepAudio3Gen v1。全部 D1 / L1，没有试听音频、观看评测图像、调用模型或复现分数。ME253–ME303 为作者报告数值，前252条保持不变。

## 1. StepAudio 2.5：ASR、TTS 与实时产品是三条评测路径

[报告 v1](https://arxiv.org/html/2605.23463v1) §4.3 的 ASR 测试将本地模型放在单张 H800、并发1，唯独 Doubao-ASR-2603 使用官方API。因此“同样 serving setup”不能理解成所有竞争模型都使用了相同硬件/调度。

中文平均CER 2.97%、英文平均WER 3.68%、long-form平均error 3.70%是不同集合与分母。Long-form集合混有中文WenetSpeech与英文LibriSpeech/Earnings22，不应把其均值当作跨语言合并编辑距离后的统一WER。对没有原生长音频能力的基线还使用VAD切成最多30秒片段，这同时改变上下文和边界条件。

表1存在值得保留的正文/表格差异：正文说 MTP-5 前后平均波动在0.06点内，但表内英文3.83→3.68相差0.15，长音频3.63→3.70相差0.07，中文3.00→2.97相差0.03。本项目不猜哪个数字是排版错误，也不把这改写成统计显著退化/提升。

表2 RTF=0.0053来自100段、每段30秒的音频，不是语音对话的首包延迟、端点检测延迟或整段回答的完成时间。

TTS §5.3 使用774个prompt，与MiniMax-2.8-HD、Elevenlabs-v3、Gemini-3.1-Flash-TTS做人类成对偏好比较，报告总体胜率67.6%。评审筛选听觉敏感度、固定评审人群和评测时段、随机音频顺序、要求理由，并进行分歧复核。竞争模型采用官方推荐voice preset，因此比较对象仍是模型+voice配置。已读文字未明确ties计分、所有匹配场次与CI，不把67.6%称为“语音正确率”。

Realtime §6.3 又分移动app主观对话、API general/car客观对话、87段speaker声学属性理解、11类Step-SPQA。报告给出优势差值，但图中绝对分值未核验，所以本批不为这些图登记猜测数字。问答能力、听感和移动端交互必须分别记录。

## 2. StepAudio 3 Gen：Elo、style judge 与音频扩展演示

[报告 v1](https://arxiv.org/html/2609.12945v1) §5.1–5.2 的 RVQ/adaptor 与 interference-aware 结果是**预训练后消融checkpoint**，不是最终产品的开关实验。三阶段baseline还没有RVQ Adaptor；不能把它与新流程的全部差值归因于某个唯一训练步骤。

TTS §5.3 用中文真人说话文本、每个竞争模型选一个voice，六系统总计1,500次成对比较，允许平局。StepAudio3Gen的Elo1755.33属于这一个pool；其对五个opponent各100场的直接比较总体胜率82%。1,500是match数量，既不是1,500个独立prompt，也不是全部都以StepAudio3Gen为一方。没有原始票、匹配图或评审聚类信息，不能自行计算可靠CI。

Voice design §5.4 包含另一组五模型、总490场中英比较，Elo1668.5和胜率75.5%。1668.5低于上一组1755.33不表示模型更不擅长voice design，因为对手、任务、拟合尺度都不同。

InstructTTSEval用1000中文+1000英文文本，各有APS/DSD/RP三条件，每系统共6000个utterance。Gemini3.1Pro-preview听音频、按原指令输出binary style consistency；每条件分母是**valid judgments**，AVG为三条件无权平均。中文85.2%、英文77.7%不是人工MOS，也不自动惩罚每个无效judge结果。要做可靠对照还需要失败/无效样本率。

§6的vocal、music、sound、vibe-speech是扩展能力描述/示例，没有看到与TTS同等级的总体评分协议。因此“能演示一分钟音乐”不能作为音乐质量/长时一致性的总体通过率。

## 3. Qwen3.5-Omni：不是更大模型在同一服务器上更快

[报告 v1](https://arxiv.org/html/2604.15804v1) §2.5 表2明确写 **theoretical first-packet latency**。内部vLLM启用torch.compile与CUDA Graph，Flash与Plus使用不同资源配置和并行策略，作者明确说不适合严格横比。

Flash单并发音频235ms、视频426ms；并发8为352/1625ms。Plus相应435/651ms和955/1980ms。这是首个可播放音频包的critical path，ARIA使text/speech交错执行，不能简单加表中Thinker TTFT、Talker TTFC、TPOP算overall。也不能跟AA的Time per Task或StepASR RTF混用。

### 听懂、说清与说得自然要分开

- ASR FLEURS是top60语言；S2TT是top59，因为该翻译集合不含Afrikaans。旧Qwen3-Omni的较小语言集合不能直接比较均值。
- VoiceBench93.1反映该套dialogue任务表现，不是实时语音自然度/打断延迟。
- 表7 Video-MME明确use_audio_in_video=True，而表6是vision-to-text/no-subtitle设置。83.7与81.9不能自动视为已对齐frame/prompt的音频消融。两者都不是2026年的Video-MME-v2。
- OmniGAIA57.2明确without thinking prompt、without formatting，使用DeepSeek-V3.2-Thinking judge；不能默认它与benchmark原配置完全一致。
- SEED-TTS英文WER1.26衡量生成内容被识别回来的准确性，不足以单独证明语音自然、富表现力或对话互动更好。

### 表格与文字的可复查差异

表9列20个公开TTS多语言测试，比较Qwen与MiniMax、ElevenLabs；表10另列9个内部语言，只比较Qwen与Ground Truth音频经同一ASR后的WER。正文“29语言中22项最低”不应改写成“在29项中22项击败两商业竞品”，因为内部9项没有商业竞品数字。逐行比较表9的三模型数字，Qwen独立最低的是13/20；再加内部9项低于Ground Truth，恰为22/29，但后九项是不同参照物。

例如内部Urdu生成音频WER14.819，Ground Truth音频17.822。评测ASR是gpt-4o-transcribe-2025-03-20。更低的ASR错误率可能反映更清晰、规范、对识别器友好的发音，不能由这个指标证明合成语音整体胜过真人声音。

CV3-Eval表11明确英语target用WER、其他target用CER。正文说12方向中10项最佳，但表中逐行数字看，只有Japanese→Chinese不是Qwen最低，得到11/12。保留差异，不静默把正文改成11，也不把它升格为新的实测结论。

Custom-voice表12又是独立任务：商业API采样时间为2026年3月，指定了ElevenLabs、Gemini、GPT-Audio和MiniMax的模型版本与voice。模型版本、声音、采样月份都应进入复现记录，而不是只存供应商品牌。

## 4. LongCat-Flash-Omni：100ms在VAD之后，app分数不等于API模型分数

[报告 v2](https://arxiv.org/html/2511.00279v2)修订日期2025-11-28，首次提交2025-10-31。§6.2的系统每包接收1秒audio+2帧，推测性提前decode；若用户继续说话则rollback。论文说600–700ms的VAD端点检测与prefill重叠，**在端点检测后**100ms内收到模型response。不能引用成“用户停止说话到回答仅100ms”。

§7.4.1为Gemini2.5Pro限thinking budget128，并采用内部修正的OmniBench，61.38不能当作未经修改的标准OmniBench成绩。UNO-Bench有1880题、44任务类型、包含多选和多步开放题，内部采集/人工注释是来源说明，不足以独立证明完全没有contamination。

§7.4.2特别值得保留：10名训练过的对话者、每产品200段约3分钟通话、四类各50段；250名用户对完整交互视频每段作三重评分。自然流畅程度是0–3等级均分，LongCat1.37、报告标为GPT-4o的产品1.79，不是成功率。六维度good-case比例又是另一套专家定性指标，例如LongCat实时性49.5%、paralinguistic91.5%、accuracy36.0%，不能合成一个自动正确率。

各产品采集日期不同，跨2025年8月至9月。更关键的是“GPT-4o”脚注实际链接到chat.chatbot.app/?model=gpt-4o，并非本次已验证的OpenAI第一方端点。论文称官方app/web，但本项目没有验证该产品的provider、模型snapshot或路由。因此保留原作者标签与URL，**不要把这条自动合并进官方GPT-4o API模型实体**。

§7.2.2 ASR文字泛称consistent superiority，表9却显示多个子集更弱，例如LongCat LibriSpeech-other4.01而Qwen3-Omni2.48；WenetSpeech-meeting6.69而Step-Audio2-mini4.87。应读取具体行，不能把宣传性段落概括直接转为全项优势。

## 5. HunyuanImage3.0：按图平均和按语义点平均不是同一指标

[报告 v3](https://arxiv.org/html/2509.23951v3) §5.1的SSAE先从500prompt抽取3500个语义点，归12种field；另一LLM检查点与prompt一致性，之后人工修正，后续图片评分固定这些点。MLLM对每点0/1评分。

其 Mean Image Accuracy 是先对每图取平均再平均；Global Accuracy 对所有点平均。若复杂prompt拥有更多点，后者会给复杂prompt更大权重。两者都不同于“每图所有点全对”的all-pass；记录一个SSAE总分前必须先问用哪个聚合、哪个judge。

§5.2 GSB用1000prompt、每prompt只生成一次、超过100名专业评审，其他模型默认设置。正文报告对HunyuanImage2.1相对胜率14.10%，对Seedream4.0/NanoBanana/GPT-Image为1.17/2.64/5.00%。已读文字没有明确relative win rate计算公式，图柱未作视觉核验。本批按原名记录，**不擅自解释成胜率概率或胜减负的百分点**，也不借用HunyuanVideo另一报告的公式。

结论仍明确这次release只含text-to-image，image-to-image训练还在进行。因此原生多模态架构的训练能力描述不能自动改写成所有模态已经发布。

## 后续可执行工作

1. 对公开音频benchmark确认prompt、采样率、分段策略、ASR清洗、valid-judge失败策略与聚合脚本，避免按品牌做混合排行榜。
2. 对偏好评测获取独立prompt/音频/评审数量、重复投票结构、对手池与tie规则；在拿到原票之前不重算Elo或CI。
3. 对产品测量记录app版本、时间窗、网络、VAD/音频I/O、provider与model身份；独立于模型API能力。
4. 对只有图示、缺judge版本、内部修正但不公开patch的结果保留未知，不补造默认值。
