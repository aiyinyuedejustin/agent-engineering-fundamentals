# Kimi模型系列：表头、脚注、系统预算与成绩单位

观察日期：2026-11-06。新增20条D1数值观察ME210–ME229。没有模型执行或分数复现。

## Kimi K2原报告：同一benchmark内的三种系统

来源：[Kimi K2 v2](https://arxiv.org/html/2507.20534v2)，§4.1.1–4.1.2、表3和附录C。v2为2026-02-03修订，不能当作K2首次发布。

SWE-bench Verified分别为agentless单patch无测试51.8、agentic单次65.8、agentic多次71.6。多次模式用内部verifier做best-of-N，具体N未在已读段落确定。虽然表格都写Pass@1，第三行的一次系统输出已经包含多次内部尝试和选择，不能称为模型单rollout成功率。Agentless输出cap为16384，其余一般为8192，预算也不同。

Terminal-Bench使用Terminus得25.0，Moonshot内部harness得30.0。同模型不同harness，不能只按模型名留一个最高分。

报告的HHEM98.9和FaithJudge92.6采用 **100×(1−hallucination rate)** 以统一表格方向。实际作者报告的幻觉率分别1.1%与7.4%。若把98.9误标“幻觉率”，含义就完全反转。HHEM采用HHEM-2.1-Open，FaithJudge用o3-mini，这些任务上的无幻觉比例也不是通用世界事实正确率。

tau2总体66.1在附录明确为micro Pass@1，不是retail70.6、airline56.5、telecom65.8的简单宏平均。四个seed平均、temperature0、确定性工具适配器仍不能抹去用户模拟器等未充分固定条件。

附录对PaperBench的某个对照数与主表存在差异，本轮不复制该不一致单元格，也不自行调成一致；Kimi本身27.8还限定在表3的Code-Dev轨道。不能省略轨道后当作整个PaperBench的普适分数。

## K2 Thinking：平均多次、并行融合和访问控制

来源：[官方K2 Thinking模型卡](https://huggingface.co/moonshotai/Kimi-K2-Thinking)，§3–4及脚注。卡片于观察日读取，未固定commit，因此是D1可变网页证据。

- AIME无工具94.5为avg@32，有Python99.1为avg@16。这里平均多次不是majority vote，也不是“至少一次成功”的pass@k。
- HLE text-only普通无工具23.9、有工具44.9、heavy51.0。heavy先并行8条轨迹，再反思融合；不属于等预算的单agent直接对比。卡片未独立列出heavy的全部工具/预算细节，记录不自行补齐。
- HLE工具模式上限120步、每步48k reasoning；agentic-search是300步、每步24k。256k上下文满后隐藏旧工具输出。单个最大输出cap并不足以代表系统总计算预算。
- 作者说未封锁Hugging Face时HLE可达51.3，因此正式测试封锁HF，并报告44.9。这里保存的是作者所述访问控制对照，不是本研究确认的泄漏事件数，也不是应该选用的更高能力分。
- 模型卡说明所有所报成绩在原生INT4下；不要拿未经核验的BF16/FP8部署精度默认覆盖它。
- 官方kimi.com chat模式会减工具/步数，卡片明确提醒可能无法复现benchmark成绩。产品体验与完整评测harness是不同对象。

## K2.5：局部脚注应覆盖笼统表头

来源：[官方K2.5模型卡](https://huggingface.co/moonshotai/Kimi-K2.5)，changelog、§3和脚注。已由卡片确认[技术报告标识符2602.02276](https://arxiv.org/abs/2602.02276)，只补读其摘要/引言，没有把完整报告评测附录算作已读。无版本报告检索元数据给出2026-08-07，不能据此把它写成模型首发日期。

总表标题写Kimi K2.5 (Thinking)，但脚注明确：

- Terminal-Bench2.0的50.8使用 **non-thinking**、Terminus2与JSON parser，因为当前thinking上下文策略不兼容。
- SWE系列采用内部bash/createfile/insert/view/strreplace/submit六工具harness，最高分在 **non-thinking** 下取得。Verified76.8不应继续机械贴表头Thinking标签。
- 编码成绩平均5次，不是取最好的一次。

BrowseComp60.6、discard-all上下文管理74.9、Agent Swarm78.4是三种系统条件。swarm主agent最多15步、子agent100步，不应记作三个模型。WideSearch另设主/子均100步，不能把BrowseComp步数照搬过去。并行加速与总算力成本需分别测量。

HLE表格标Full，K2.5确实包含text与image，DeepSeek-V3.2单元格却用†标明text-only。因此同一表格里也存在子集混合。K2.5 HLE工具模式保留最近一轮工具消息，而BrowseComp采用discard-all，不要把两者都记成一个泛称“context management”。

OmniDocBench1.5的88.8在脚注明确为(1−normalized Levenshtein distance)×100，不是完全正确文档的百分比。视觉评测有64k max-tokens、avg@3；GPT-5.2-xhigh约10%请求在3次retry后仍无输出并按错计。这里的比较也包含服务可靠性，不能只解读成模型条件正确率。

2026-01-29 changelog还记录了移除默认system prompt与修正media token。实际复现至少应固定chat template和model revision，而不只固定模型显示名称。

## 实用结论

记录一个模型成绩时，优先级是具体任务脚注高于总表标题。模型、精度、prompt/template、工具harness、内部选择器、上下文策略、并行轨迹和失败处理共同定义结果。高分单元格可以引用，但缺失这些条件时不能把它当作相同成本下的裸模型排行榜。
