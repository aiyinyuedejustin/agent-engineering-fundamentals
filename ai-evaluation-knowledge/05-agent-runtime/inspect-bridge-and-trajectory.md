# Inspect bridge、轨迹和恢复：接入成功不等于语义不变

研究日期：2026-11-06 UTC。本文件范围内收集已关闭。Inspect 源码固定到 `7cf09c929b3ea9138762ca9e4d8d23f119554ee6`，Harbor 固定到 `26f95e0ebd8c77011bbf4656f5c98af66ce55848`。网页文档为当日读取，可能继续变化。

**深度：**Inspect 示例任务与 sandbox bridge 执行链、Harbor 轨迹校验与 Codex 转换达到 D3；Inspect checkpoint 和日志格式为 D1。没有运行这些系统，未声称 D4。这里把运行时桥接、观测格式、恢复能力分别讨论。

## 1. 先明确被评测的对象

一种实验是保留原生 agent 的模型参数、工具和控制流，观察整个产品的能力；另一种实验是保留 agent loop，但统一替换模型与生成参数，比较模型。两者都合理，问题是不能混为一个实验。

官方 [agent bridge](https://inspect.aisi.org.uk/agent-bridge.html) 通过兼容模型 API 接入外部框架。桥接后得到预算、日志和评分集成，并不自动证明原生请求的所有语义都原样保留。

实际 [Agents SDK 示例任务](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/examples/bridge/agentsdk/task.py) 使用 JSON dataset、`web_research_agent()` 和 `model_graded_fact()`。[对应 agent](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/examples/bridge/agentsdk/agent.py) 在 `agent_bridge(state)` 中运行带 WebSearchTool 的 SDK Agent，把模型名写作 `inspect`，最后返回 bridge.state。[dataset](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/examples/bridge/agentsdk/dataset.json) 包含三条有目标答案的研究问答。

这是已读的真实示例，不是论文级 benchmark 复现。它使用进程内 agent_bridge；下面的 sandbox_agent_bridge 是另一种部署路径，不能把两者的默认权限直接互相套用。

## 2. Sandbox bridge 的实际控制链

[sandbox/bridge.py](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/agent/_bridge/sandbox/bridge.py#L55-L335) 的路径是：

1. 取得 sandbox，解析搜索、代码执行、远程 MCP 的授权配置。
2. 创建 SandboxAgentBridge，注册 host-side tools，检查重复名称。
3. 在 host task group 启动 model service，等待启动信号。
4. 在 sandbox 内用 exec_remote 启动 model_proxy，通过兼容 API 接收 agent 请求。
5. 同时监控 proxy 进程与服务侧失败，再交给 agent 主体执行。
6. 退出时在 shielded cancellation scope 内杀掉 proxy，取消 task group；把服务侧失败传到样本运行器。

这里的 proxy 终止是源码可见行为，不是“任意 agent 子进程和第三方系统都已停止”的证明。

### 2.1 模型名不是最终模型身份

源码说明 aliases 优先，resolver 次之，然后才使用 model pin/当前 eval model。未识别的客户端模型名默认路由到 eval model。alias 是 agent 可调用模型的入口，源码明确提醒不要随意暴露 grader role。

**工程建议：**每次生成至少保存 requested model、resolved model、provider、有效 generation config。仅从 CLI 发出的 model 字符串归因，会把桥接重定向当成原生模型调用。

### 2.2 默认并非 faithful proxy

`forward_generation_config=False` 是此版本 sandbox bridge 的默认值。客户端的 max_tokens、temperature、reasoning effort 等会被丢弃，采用 Inspect 解析后的模型配置/供应商默认值；system prompt、tools、response format 等结构参数仍转发。设为 True 才把客户端生成参数视为权威。

此外，service_tier、store、truncation 与 provider tool options 由 eval 配置控制；previous_response_id 请求会被拒绝；HTTP headers 采用 allowlist。以上来自固定源码的 API 文档及参数传递路径，尚未逐项做请求级实测。

**推断：**若论文声称“同一 agent，仅换环境”，这些选项应纳入实验清单，否则实际还改变了采样和会话行为。

### 2.3 网络边界不止一个

sandbox 不能联网，不代表模型供应商的 native web search 或远程 MCP 不能联网。此版本 sandbox bridge 默认不授予这些能力，正是为了避免绕过 sandbox egress。host-side tools 也是另一条执行路径。

[host_tool.py](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/agent/_bridge/sandbox/host_tool.py#L110-L165) 默认要求工具调用匹配模型在桥接生成中提出的 proposal，且 grant 只能消费一次。没有 proposal 或重复调用会记录 permission rejection。`require_proposal=False` 可为 model-written code 调用工具等模式放宽这条检查；这是能力变化，需要明确记录，而不是无关紧要的兼容性开关。

### 2.4 一个已确认的文档/实现差异

当日官方 agent-bridge 文档以及 bridge.py 的参数说明提到返回 MCPServerConfigStdio；但同一固定源码中 [_register_bridged_tools](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/agent/_bridge/sandbox/bridge.py#L389-L409) 实际返回 MCPServerConfigHTTP，URL 是本地 proxy 的 `/mcp/<name>`。

这是可定位的版本一致性风险，不是对所有版本的结论。接入者应以所安装版本的返回类型和端到端测试为准，不能只复制网页示例。该差异未在真实运行中复现。

## 3. 日志层次不同，回答的问题也不同

官方 [eval logs](https://inspect.aisi.org.uk/eval-logs.html) 与 [event reference](https://inspect.aisi.org.uk/reference/inspect_ai.event.html) 支持以下区分：

| 证据 | 能回答 | 不能单独证明 |
|---|---|---|
| 最终 score | grader 接受了什么结果 | agent 如何达到结果、成本是否完整 |
| ModelEvent | 请求/解析模型、生成配置、工具定义、输出、重试等 | sandbox 文件系统全状态 |
| ToolEvent | 参数、结果、错误、完成/取消和 span 关系 | 外部副作用被撤回或 exactly-once |
| SandboxEvent | exec/read/write 的记录 | 完整输出；文档有截断限制 |
| CompactionEvent | summary/edit/trim 与 token 变化 | 压缩前状态仍可用于逐步重放 |
| 原生 agent 日志 | adapter 没有保留的实现细节 | 稳定通用 schema 或完整评测判定 |

`.eval` 应用官方日志 API 读取，不应视为一个任意 JSON 文件。摘要读取会省略细节；raw model API logging 默认不是所有请求的完整留存，需要显式配置。图片日志开关影响留存，不等于改变送给模型的观测。执行 status=success 与任务分数成功是不同字段。

另一个细节来自 [bridge/context.py](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/agent/_bridge/context.py#L1-L109)：`is_root_agent()` 对 unknown、utility 或没有上下文也可能返回 True，这是控制策略的回退值。分析多 agent 轨迹时需要 `kind == "root"` 的正面归因，不能把该 helper 的 True 当成来源已确认。

## 4. ATIF：可交换格式不是完整性证明

Harbor 官方 [ATIF](https://docs.harborframework.com/agents/atif.md) 当日版本为 v1.8；固定 [Trajectory 模型](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/models/trajectories/trajectory.py) 接受 v1.0 至 v1.8。

已追踪的约束包括：

- session_id 是 run 级身份，多个 child trajectory 可以共享；trajectory_id 是 trajectory 文档身份，嵌入的子轨迹要求非空且在该数组中唯一。
- 每份 trajectory 的 step_id 从 1 连续编号，不是整个多 agent 系统的全局时钟。
- 已给出的 observation.source_call_id 必须指向同一 step 的 tool_call；但校验函数遇到 observation=None 会跳过，并不要求每个 tool call 都有一个结果。
- schema 校验与媒体文件存在、原生日志完整、所有分支被采集是不同检查。

**推断：**“通过 ATIF schema”只能作为结构合法性的证据，不能直接作为无损日志、无漏记成本、可重放的证据。还需要检查调用/结果配对、媒体可解析、child refs 可解析、起止事件与 native counters 是否一致。

### 4.1 多 agent 成本不能对所有节点直接求和

Codex adapter 的 [_include_subagent_metrics](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/agents/installed/codex.py#L1503-L1542) 把 child totals 合入 parent；child totals 已经包含其后代。任何一个必要值缺失时，相应总数保留为 unknown，而不是填 0。

因此对 root 和所有嵌入 child 的 final_metrics 再求一次总和会重复计算。指标数据库必须标注“本节点 own usage”还是“含后代 subtree total”。这条结论特指已读的 Codex adapter，未证明所有 ATIF producer 采用相同聚合方式。

### 4.2 转换失败可能与 reward 分离

[populate_context_post_run](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/agents/installed/codex.py#L1899-L1934) 捕获轨迹转换异常后记录日志并返回；没有 trajectory 时也返回；只有 final_metrics 存在时才填入 context 的 token/cost。写出轨迹文件失败亦被记录。

这证明必须单独统计 telemetry completeness；它没有证明任何已公布结果实际漏记。缺少 cost 不是免费，缺少 trajectory 不是没有发生调用。

## 5. Checkpoint 保存什么、不保存什么

以下只达到 D1，依据当日官方 [checkpointing](https://inspect.aisi.org.uk/checkpointing.html)：

- 保存已注册 agent state、指定 sandbox paths、sample store/events。
- 不保存任意进程 RAM、正在运行的工具、打开的连接或外部副作用。
- 在 turn boundary 才触发；长工具调用可能使时间触发器延后。
- 恢复前先在新 sandbox 运行 setup，再恢复指定路径；不是继续同一 VM 进程。
- `ckpt-NNNNN.json` 写入后才算 committed，未提交的孤立快照不参与恢复。
- sandbox_paths 是整份 map 的覆盖，显式路径需要自行包含 home；`.cache` 目录始终被排除。
- 默认成功完成后删除 checkpoint；archive strategy 是未加密 archive，restic 使用每样本密码加密 repository。选择影响留存与敏感数据处理。
- root usage 会恢复，但 nested limit scopes 不会；scoring-only resume 不重新启用已耗尽的执行时间限制。
- 默认 checkpoint 失败不使样本失败，需要 max_consecutive_failures 配置才能把 durability 作为硬要求。

**推断：**日志可浏览、文件可恢复、agent 可继续、外部动作不重复，是四种不同能力。恢复后如果重做一次发送/提交/远程写入，需要独立的幂等键或去重机制，不能靠 checkpoint 名称推断 exactly-once。

## 6. OpenTelemetry 的补充角色

当日读取的官方 [GenAI agent spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) 标注 Development，并区分 create_agent、invoke_agent、workflow、tool 等跨度。它适合跨服务关联、延迟与错误观测；内容采集可能是 opt-in，provider 名也可能代表代理层。

它与 ATIF/`.eval` 并非可直接互换的“同一种轨迹”。本轮只核验文档，未检查某个真实 exporter 是否记录全部事件，未锁定该独立规范仓库 SHA。不能把规范存在当成生态实现已兼容。

## 7. 尚未解决的问题与实验清单

1. 用固定 CLI 和请求录制对照 bridge 开/关，核对 generation config、缓存、错误/拒绝重试、streaming 与 response continuation。
2. 测量 native tool、host tool、sandbox tool 三条路径的网络约束与成本归因。
3. 故意删除一个 child log、一个 tool result、一张图片，区分 schema 合法、可浏览和完整性状态。
4. 在外部写入完成但 checkpoint 尚未提交时崩溃，验证恢复是否重复副作用。
5. 把时钟、token、cost、turn、primitive action 分开记录，观察恢复前后是否连续。

这些是未执行计划，不是 D4 结果。下一步本地自写机制实验只验证逻辑反例，仍不能替代真实 adapter/cloud 运行。
