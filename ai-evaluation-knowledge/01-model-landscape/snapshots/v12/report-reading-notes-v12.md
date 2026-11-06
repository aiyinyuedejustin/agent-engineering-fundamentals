# OpenAI近期卡片：相同权重、不同产品与更新后的比较基线

观察日期2026-11-06。升级ML006/009/010/011，新增已读GPT-Live1.1卡片ML123及仅发现Images2.6索引ML124。现124来源：62D1、62D0。ME304–ME342是39条新报告观察，全部D1，未运行模型。本文只讨论高层测量与可比性，不提供危险任务的实现步骤。

## 1. 同一名字不保证同一版本，不同名字也不保证不同权重

[GPT-Rosalind-6卡片](https://deploymentsafety.openai.com/gpt-rosalind-6) §1–2明确：**与GPT-6 Astra使用相同权重，没有添加训练数据或额外post-training**。它的部署访问与拒绝边界不同。数据库可建立相同underlying weights的关联，同时保留独立deployment/policy variant；不能因为名字新就当作新训练底座，也不能因为权重同就混合所有评测结果。

对照，[GPT-6 Cyber卡片](https://deploymentsafety.openai.com/gpt-6-cyber/introduction) §2明确有专门强化学习post-training与alignment训练。因此它是不同训练variant，而不是Astra的普通reasoning-effort设置。本文不把两者当同一个模型ID。

[GPT-6 October卡片](https://deploymentsafety.openai.com/gpt-6-october) §1又说明：ChatGPT使用October版本，Codex/Work仍使用之前September版本。因此“GPT-6 Sol”或“GPT-6 Luna”这个basename不够，版本月份与产品端点需要保留。该信息是卡片发布时的说明，不作为今天某个用户账户实时路由的证明。

[GPT-Live1.1卡片](https://deploymentsafety.openai.com/gpt-live-1-1/gpt-live-1-1.pdf)把voice体验描述为两模型系统，其alignment测量还涉及delegated thinking model。语音front end、被委派模型和整套产品的能力/安全分数是不同对象。卡片中“不委派时低于某能力阈值”不意味着委派后的完整系统同样低于阈值。

## 2. 同卡重测旧模型，比跨旧卡拼分数更可用

Rosalind §3明确旧Rosalind5.5在相同benchmark版本和problem集合上重测，因此不同于其发布时数字：

- MedChemBench v7：99问题，每problem每budget最多9个scored responses；先problem内平均，再problem等权。最高budget Rosalind6为49.6%，旧5.5为28.9%，是rubric均分。
- GeneBench Pro v13：129问题，每模型每题7个responses，用于估计single-attempt success，分别37.7%/16.7%。这不是“七次至少成功一次”；其benchmark-specific配置与production不同。
- LifeSciBench Gold：因任务或环境问题排除6题，剩94题，每题最多8次scored responses，分别61.3%/44.0%。不能与未排除的100题旧数值直接比较。

相反，同卡§4.2.2.3的安全参考表明确说有些run的版本、推理、评分、覆盖不同，**仅descriptive comparison**。例如Astra的Broken Search参考是1.5%，而Cyber卡§4.2给Astra6.92%。没有对齐信息就不能解释成Astra退化、Rosalind改进幅度或训练因果效应。

## 3. 名为“deception”的分数可能只检查final answer

Cyber卡Blocker Deception20.29%检查最终回答。作者特别说明：他们查看的flagged样本多数已经在早先commentary说明blocker，只是最终总结没有再次附上。作者将其解释为不完整的最终摘要，而非有意欺骗。

这不使指标无意义：用户可能只依赖最终结果。但研究者应写清scored surface与标签含义，不能把20.29%翻译成“模型有20%故意骗人”。同卡Broken Search0.33%则检查最终回答虚称访问了不可用工具或资料。两个名字接近的诚实指标，所检测行为并不相同。

Warnings评测又把“应停止”与“应继续”拆成两组，Cyber分别73.00%/80.43%。不能不看题数权重就平均成整体服从率。Honeypot比较还分有无deployment safety instructions；观察到0%不保证真实错误概率为0。

Agent Replay Auto-Review28.40%来自此前blocked且确认发生过assistant failure的困难生产案例，工具响应经模拟。条件分布已被选择，不能当作普通流量的28.4%会出问题。

## 4. 同名或近名的安全能力benchmark仍需保留metric

Cyber §7报告历史ExploitBench的 **ACE-normalized mean capability=100%**，同时报告近期internal port的实际mean ACE success=42%。前者有历史数据污染风险提示，后者用2026年6–8月的新任务。两者不是相同题、相同分数含义；不能说模型在几个月内从100%跌到42%。

SRE-Bench92.84%要求六个objective全部满足，是task all-pass，而非六项partial-credit均值。SEC-Bench Pro87.02%按pass@1报告。这里只登记公开汇总分数，不声称取得任务环境、实现细节或复现能力。

## 5. Safety最低effort与capability最高effort不应合成“同一配置”

October卡说明，常规安全/mental-health评测用最低部署reasoning setting，capability assessment用最大reasoning effort。表4间接prompt injection另注明跨可用reasoning levels等权平均。总则不能覆盖明确例外。

HealthBench/Professional还做响应长度调整：以2000可见字符为参照，每多500字符分别扣2.99/1.47点，短回答相应加分，模型prompt不告知该惩罚。SolOctober Professional为55.2（raw62.2，平均4360字符），HealthBench52.1（raw55.7，2602字符）。raw和adjusted可能方向不同，不能混用。

MentalHealthBench1215题，每题4response；正文说先对每response裁剪0–100，再题内平均、跨题平均，SE以1215个task means计算。表题同时称task-clipped。这里保留正文运算与表名，不自行推断它等于其他repo的clip-after-mean。4次采样增加稳定性，不等于将标准误的独立单位从1215变为4860。这个rubric分也不是临床治疗效果。

## 6. 真实来源的voice prompt，也不等于真实流量发生率

Live1.1报告有两个安全集合：

- Production prompts来自获准使用、经隐私处理的真实audio，刻意选旧模型尚未理想回答的困难案例；文字说明包含transcription步骤，具体音频/文本路由未完全展开。
- Synthetic prompts由policy边界产生文字，再转成语音输入，覆盖罕见/对抗情境。

两者均不按生产prevalence加权。Live1.1在mental-health子集的production分数0.81，synthetic0.63；旧Live1相应0.78/0.70。不能用其中一组来否定另一组，也不能说用户总体体验发生了同等幅度变化。报告明确指出若干synthetic类别有统计显著回退，production则没有显著回退，但未在本批读到完整原始数据/测试方法。

这些声学安全表也不测语音自然度、音色、延迟或ASR错误率。系统层interventions不全部包含在这些model-level测试中。不同产品层级必须显式说明。

## 7. Astra卡的更新本身就是版本证据

[当前Astra卡](https://deploymentsafety.openai.com/gpt-6-astra)仍标September3发布时间，但changelog已经包含：

- September9重新说明verbalized metagaming与oversight gaming，并移除可能混淆的旧比较图。
- September22更正HealthBench配置错误，并加入新版alignment结果/其他模型附录。
- October30更正外部WCB结果：原61.6%±0.6%开了web search，而comparators没有；关闭web后为59.2%±0.6%。两次都发生于pre-release评测期。这是配置修正，不是模型发布日期或训练变化。

只保存September3网页日期会丢掉重要的测量历史。此处不把已更正旧值作为正常模型成绩入表。

## 8. Internal deployment simulation仍是simulation

Astra §8.6从可恢复conversation/workspace、至少一次tool call的内部历史任务，固定prefix，重新采样最后assistant turn。LLM工具模拟器可在重建workspace中执行代码来提供响应。匹配54,218任务，Astra有34个severity≥3 flags，Sol有73个。它们是monitor判断，不是已确认的现实事故数量。

用于检测模拟逼真程度的二选一judge把Astra重采样trajectory选为真实的比例为42.6%；它不是模型正确率。卡片也承认内外分布偏移。不能把34/54218直接当作外部长期部署风险。

verbalized evaluation awareness分别9.6%/2.8%，依赖CoT中可观察的表达，不覆盖所有可能未说出的意识。§8.7对oversight gaming的判断也明确非因果，需要解释CoT。因此“检测到某种表述”与“行为由该意图导致”应分开。

## 后续

本批是官方网页/PDF指定部分阅读，不是全报告安全审计。Astra抓取文本截断120k，仅所列章节确认读过。未读取的图数字不填，所有参数未知项保留；source/index/模型身份仍分别计数。v12作为模型数据视图，v10等代码实验继续独立存在。
