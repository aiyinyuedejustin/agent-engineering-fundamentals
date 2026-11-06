# MCP-Atlas：真实工具环境，答案覆盖率与任务分母

研究日期：2026-11-06。固定代码：scaleapi/mcp-atlas @ `e3dfef3ce93287c3d7b9e765c3a021f252eefbff`（2026-10-29）。HF HEAD 观测为 `8c563b55d7c967755f474299848049834d624617`（2026-08-03）。

**D3：真实公开任务、参考轨迹、当前 TypeScript agent loop 与 Python scorer 路径已读。D4 仅为 15 项合成评分实验，judge 全部替身。没有调用 MCP 服务、真实模型或在线 judge，也未复现官方榜单。**

## 1. 不能把首发论文、四月榜单更新、十月代码混成一个版本

- 首发论文描述 1,000 题，其中公开 500、私有 500；每题只暴露一个受控工具子集，混入相关干扰工具。
- 当前官方榜单说明：2026 年 4 月更新 judge 和瞬态工具错误处理，将原先 20 turn 限制替换为最多 100 次 tool calls，并重新评分。
- 固定十月代码的 agent harness 已由 Python 改写成 TypeScript v2.0.0。默认同时有 256 turn 和 100 tool-call 上限，当前 scorer 默认 `gemini/gemini-3.1-pro-preview`。
- 当前 README 列完整服务集合 36 servers / 307 tools，数据卡仍写 36 / 220；需要区分当前环境可用工具清单与数据集最初覆盖的工具集合，不能悄悄挑一个数字当作永恒事实。
- 公开 500 题本地分数不应直接标作完整 1,000 题正式成绩；当前代码输出的 all 也只表示传入 dataframe 全部行。

历史诊断曾未公开；当前 v2 changelog 说明已新增公开 diagnostics 管线。因此“诊断不公开”同样需要带时间范围。

## 2. 已读真实 task，不把参考轨迹当作唯一合法路径

实际读取 rows API 第一条，task ID `689f4d693e212e8ef3390731`，返回没有 truncated_cells：
- 自然语言请求比较一个开源游戏仓库创建年与官网域名注册年的差；
- 15 个 enabled tools，包含 GitHub 搜索/读取、fetch、whois 和代码执行；
- 3 条 GTFA claims；
- 参考轨迹有 5 次工具调用，从找仓库、取时间信息到计算差值。

这里只保留任务结构，不复制完整题目、答案或参考轨迹。参考轨迹是数据证据和诊断线索；当前 correctness scorer 并不要求模型逐步照做。没有重新查询这些外部服务，记录中的历史响应不应误写成今天核验的网页状态。

rows 请求与默认 `load_dataset(...)` 均没有固定 revision。虽然记录了访问时 HF HEAD，仍需在实际运行时固定数据字节、服务器版本、外部响应与初始状态。

## 3. 当前 loop 实际限制的是尝试次数

`run_eval.py → /v2/mcp_eval/run_agent → agent-eval.ts → MCPClient`：

- 先取得并过滤本题 enabled tool menu。sandbox client 在调用时也检查工具是否被允许，不只是把多余工具从 prompt 隐藏。
- 同一 assistant turn 中的多个调用按循环逐个执行。
- totalToolCalls 在解析参数并调用服务前增加；参数错误、服务异常也会消耗预算。100 不是“100 次成功调用”。
- 工具错误被反馈为 tool message，使模型有机会恢复。语言模型请求的若干可重试错误有另一个 retry 层；不要把两类重试或 turn/call 预算互换。
- 模型返回无 tool calls 时自然结束；到达预算/轮数时产生独立 error event。
- batch runner 挑最后一条有文字的 assistant message 作为 response，不要求它是自然结束后的无工具最终答案。因此预算结束时，可能把此前带调用的文字作为可评分回答。event 类型的错误不自动变成 CSV 的 ERROR 前缀。

最后一点不等于整题必然误判：当前指标允许对已有答案给部分分。但“有 response”不能用来证明任务正常结束，最好单独保存 finish reason 和工具失败计数。

## 4. context 与环境 reset 也会改变比较

当前 `compact` 的实际实现是保留最近两轮工具结果全文，将更老且较长的工具结果截到前 1,500 字符，**不是用模型生成摘要**。另一 tool-output-cap 会在结果进入后续上下文前按字符截断。不同设置可能删除完成任务所需证据，应随分数记录。

当前 loop 明确注释并关闭 reset-state 调用，因为 image 没实现该 endpoint。README 支持多个任务共用一个 sandbox，也允许外部 orchestrator 为每题提供临时 sandbox；内部 Modal proxy 没在此仓库发布。

这只是源码与部署选项观察，本文没有测试交叉任务污染。但 stateful 文件、记忆、git 或数据库服务的评估，必须证明每题初始状态、并发隔离与复位策略，不能由 Docker 或“可复现”字样自动推出隔离已成立。

## 5. primary score 主要验证最终答案覆盖，不验证全部实际动作

`score_claims.py` 将每条 claim 与模型 response 分别送入 LLM judge。该 prompt 不把完整工具轨迹提供给这个 coverage 判定。judge 输出：
- fulfilled → 1
- partially_fulfilled → 0.5
- not_fulfilled → 0

题目 coverage 是 claim 分数的简单平均，保留 3 位小数；脚本报告 ≥0.50 和 ≥0.75 两个阈值的 pass rate。主榜关注 0.75。通过阈值并不要求所有 claim 完全成立。

judge 的 confidence 被记录、平均，但不用于 coverage 加权。数值指导允许约 5% 相对差和百分比 ±1 个百分点，并提醒按语境处理；这是 LLM 软判规则，不是逐数执行的精确程序约束。

所以该分数擅长回答“最终回应涵盖多少预设信息”，不单独证明：
- 信息通过本次工具而非记忆获得；
- 全部外部写入/动作真的完成；
- every intermediate step 正确；
- 所有未列入 rubric 的额外陈述都真实。

轨迹诊断可以补充这些解释，但不能把辅助分析直接当作已进入 primary reward 的约束。

## 6. 四种失败走不同分母路径

代码中有重要区别：

1. **已有任务行、response 为空或 ERROR 前缀**：直接记 coverage=0，不调用 judge，留在有效 score 分母。
2. **单条 claim 的 judge 请求耗尽重试**：该 claim 转为 not_fulfilled，仍在该题 claim 分母里。日志称 skipped，但实现不是移除 claim。
3. **非空回答但没有可提取 claims，或行处理异常**：返回 coverage=None；统计阶段 dropna，排除出有效 score 分母。
4. **模型 CSV 根本没有某个 task ID**：ground truth 与输出用 inner join，该题在评分前就消失，不会自动补零。重复 task ID 则可能产生重复行，没有在这一层强制唯一。

因此 “pass rate” 需要同时报告计划题数、合并题数、unique task 数、非空 score 数与失败原因。合成实验用 3 行，其中一个通过、一个 ERROR 为零、一个无 claims 为 None：统计 pass rate 是 50%，不是按全部 3 题算出的 33.3%。

`_compute_split_stats` 的 clean_runs 还直接从总行数减掉 None 数与有 errors 字段的行数，二者重叠时可重复扣减；单行同时满足两项的合成输入得到 -1。此项是附属计数边界，不改变上述 coverage numerator，不能夸大为“所有分数错误”。

## 7. 断点续跑与 provenance

runner 的 existing_task_ids 读取所有已有 ID，不检查 response 是否成功；已写入 ERROR 的 ID 也会被视为已完成而跳过。改变模型、工具预算或数据版本后复用同一输出文件，也不能仅靠 task ID 去重得到一个干净新实验。

README 提倡每次运行独立目录，runner 写 run_config.json，scorer 会带上找到的配置。实际复现仍要验证配置对应每一行，而非只依赖最终目录里最新的一个文件。

## 8. 组件实验

[脚本](mcp_atlas_scoring_probe.py) 与 [结果](mcp-atlas-scoring-probe-output.json) 共 15 项断言通过：
- 真实 scorer 控制流 + 替身 judge，验证 1/0.5 平均、confidence 不加权、judge 故障分母；
- 空输出为零、空 claims 为 None，以及统计 dropna；
- inner join 缺失任务、重复 ID 行；
- clean_runs 重复扣减边界；
- claim extraction 接受 Python list 字符串，并过滤过短 claim。

源 `score_claims.py` SHA256：`33d5159cd1b1df9ff63f0918998d6fced812c5e3362cba1b993efafc571d0f85`；pandas 2.2.3。

所有标签、CSV 和故障均为合成。没有估计这些情况在真实 500/1,000 题运行中的发生率，也没有据此改写任何模型成绩。在线 judge 准确性、真实服务状态、代理恢复能力仍未实验核验。

## 9. 选型与复现建议

- 工具接口协议：固定 enabled menu、工具 schema、服务版本、密钥/数据可用性与失败重试。
- 系统预算：分别记录 LLM turns、尝试的 tool calls、成功 calls、字符截断、timeout 和模型 reasoning 配置。
- 成功事件：把答案覆盖、实际状态/动作、引用真实性、finish reason 分开。
- 统计：缺失题补零或排除必须明确，并禁止无意重复 ID。
- 持续比较：固定外部快照或记录响应变化；公开/私有 split、judge 和 harness 更新分别登记。

## 固定源码与官方证据

- [官方榜单及 2026 年 4 月更新说明](https://labs.scale.com/leaderboard/mcp_atlas)
- [固定 README](https://github.com/scaleapi/mcp-atlas/blob/e3dfef3ce93287c3d7b9e765c3a021f252eefbff/README.md)
- [v2 changelog](https://github.com/scaleapi/mcp-atlas/blob/e3dfef3ce93287c3d7b9e765c3a021f252eefbff/CHANGELOG.md)
- [数据固定 HEAD](https://huggingface.co/datasets/ScaleAI/MCP-Atlas/tree/8c563b55d7c967755f474299848049834d624617)
- [实际 rows 请求](https://datasets-server.huggingface.co/rows?dataset=ScaleAI%2FMCP-Atlas&config=default&split=train&offset=0&length=1)，未固定 revision。
- [Agent loop](https://github.com/scaleapi/mcp-atlas/blob/e3dfef3ce93287c3d7b9e765c3a021f252eefbff/services/agent-harness/src/mcp-agent/agent-evals/agent-eval.ts)
- [Sandbox client](https://github.com/scaleapi/mcp-atlas/blob/e3dfef3ce93287c3d7b9e765c3a021f252eefbff/services/agent-harness/src/mcp-agent/helpers/mcp-client/sandbox-client.ts)
- [Batch runner](https://github.com/scaleapi/mcp-atlas/blob/e3dfef3ce93287c3d7b9e765c3a021f252eefbff/run_eval.py)
- [Claims scorer](https://github.com/scaleapi/mcp-atlas/blob/e3dfef3ce93287c3d7b9e765c3a021f252eefbff/services/scoring/score_claims.py)

