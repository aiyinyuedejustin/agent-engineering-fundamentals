# v9 模型标签身份审计

稳定文件：model-identities-v9.json，覆盖v9的252条观察所用全部63个原样model label。只做D1语义规范化，不证明权重hash或API snapshot相同。不要将模型报告publisher直接复制成其所有竞品的creator。

可以作为同一underlying model的配置关联：DeepSeek-V3.2 Thinking/non-thinking；KimiK2.6 AgentSwarm；Step3.5Flash PaCoRe；MiMo-Audio-Instruct+Think。前两类reasoning与swarm不同：配置保留，系统能力不能全部归入裸模型。

HY-MT1.0-7B是明确改名alias：HY-MT1.5论文§3.1直接写它指previous model Hunyuan-MT-7B。FP8/Int4是HY-MT1.5-1.8B的量化artifact，不能丢精度/校准方式，但不另计底座训练身份。

必须分开的训练版本：MiniMax-M1-40k/80k是不同训练阶段，不只是inference token cap；Magistral Small SFT、RL-only、SFT+RL；Qwen3Omni Instruct/Thinking与Flash；Base与post-trained版本；KimiK2Instruct/K2Thinking/K2.5；HunyuanVideo CFG-distilled；MT-Chimera候选融合模型。不同规模也保留。

两个暂不自动并表的label：

- Qwen3-Omni-30B-A3B：speech表省略suffix，不能凭名字自动选Instruct或Thinking。
- HunyuanVideo1.5 720p：这里原观察包含T2V/I2V与不同速度配置。按每条settings细分，不认定一个唯一checkpoint。

组织只写已核验的发布者/研究团队，如Qwen team、InternVL team、Ovis team、KAT-Coder team。此处不从商业传闻补上母公司。GPT/Claude等品牌的组织来源另列，避免把AA/Scale误当模型creator。

v11后续新增标签不在此63项范围。其中“GPT-4o product as labeled by report”尤其需要保留未核验身份，论文URL为chat.chatbot.app，不可自动映射官方GPT-4oAPI。StepAudio3Gen各pretraining ablation是实验checkpoint而非部署产品；StepAudio2.5 ASR/TTS是不同专门分支；Qwen3.5OmniFlash/Plus资源/架构variant分别保留。
