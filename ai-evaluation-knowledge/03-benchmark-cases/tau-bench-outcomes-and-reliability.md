# τ-bench：结果、轨迹、可靠性和语音质量是四件事

研究日期：2026-11-06。深度：**D3（局部 task → runner → evaluator → metrics 源码追踪）**。没有真实模型/语音运行；适合 L1–L3。

## 名称与版本

仓库仍叫 [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)，但当前 README 已是 τ-bench 2.0。本文固定 commit `033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f`（2026-11-04），**不能拿仓库名称认定正在评 τ²-bench 2025 原始版**。

[运行文档](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/docs/running-the-benchmark.md)区分：
- text-v1 与 voice-v2：6 语言 × 3 领域 × 每领域 50 frozen tasks，单 trial 是 900 calls；
- voice-v1：英文原 registry，278 calls；
- banking、entity 有独立 frames，不自动计入 voice-v2 overall。
同一个 CLI 不带 benchmark 参数的 text run 是 custom run，并不等于完整官方基准。

## 已读的真实任务

读取 canonical retail tasks 与[英文语言包 50 任务](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/data/tau2/multilingual/en/retail_tasks_en.json)。其中 task 6 是一个换货请求：用户最初有两个商品目标，但在确认时缩小为一个。这把交互澄清、用户状态变化和事务执行连接起来；不是从静态问题直接选一次 function。

此例含 user_scenario、initial_state、evaluation_criteria；评价中的 actions 记录一条参考调用链，reward_basis 明确为 DB 与 NL_ASSERTION，不能把 schema 的默认值当作每题实际值。此例 nl_assertions 为 null，需沿 evaluator 的空列表语义解释，不能仅看字段名声称测了复杂自然语言行为。

## 源码执行链

[batch.py](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/src/tau2/runner/batch.py) 的 run_single_task 经 build_orchestrator 建 agent、user simulator、environment 和 task，再调用 [run_simulation](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/src/tau2/runner/simulation.py)。后者执行 orchestrator.run，保存实际 policy，按半双工 message 或全双工 tick 选择 evaluator，再将 reward_info 放回 simulation。

[evaluate_simulation](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/src/tau2/evaluator/evaluator.py) 检查停止原因；非正常停止先得 0。ALL 模式可以计算诊断项，但只把 reward_basis 指定的分量乘进最终 reward。IGNORE_BASIS 会改变这个定义，因此不是同一个实验指标。

## reference actions 不一定是必须遵循的脚本

[EnvironmentEvaluator](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/src/tau2/evaluator/evaluator_env.py)：
1. 建 predicted environment 并重放实际轨迹；
2. 建 gold environment，重放 initial state 与参考 actions；
3. 比较 agent/user DB hash；
4. 执行 env assertions，并按 basis 组合。

因此两条不同的调用路径可以得到相同的正确结果。只有 ACTION 在 basis 中时，参考调用才成为硬约束。[官方 evaluation 解释](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/docs/evaluation.md)也明确提醒此点。局限是 end-state 不能自动证明中间所有行为都合规。

## communication judge 和独立语音 judges

[communication evaluator](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/src/tau2/evaluator/evaluator_communicate.py) 默认使用语义 judge，也保留 substring 模式；后者和前者在语言、改述、拼写变化上不是同一个测量规则。judge 配置与 prompt_version 在 schema 中显式记录。

运行后额外的 naturalness、speech fidelity 等 diagnostics **不改变 task reward**。自然声音、正确信息传达、正确 DB 操作、没有错误权限行为，必须分开报告。

## pass^k 不是 pass@k

[agent_metrics.py](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/src/tau2/metrics/agent_metrics.py) 实现：
`pass_hat_k = C(success_count,k) / C(num_trials,k)`。
它估计抽 k 次**全成功**的概率，不是常见的至少一次成功。全成功关注可靠性；best-of-k 强调多次尝试的能力上界。

官方分数先平均 task 内 trials，再平均 cell 内 tasks，最后等权 cells；基础设施错误排除出分母并单独报告。全部 errored 的 task 会退出 cell。研究时必须同时展示缺失、未判分和 error 数，否则可用性下降可能被条件成功率隐藏。

## 复现要固定什么

除 agent 模型外还包括 user simulator、judge、language/locale 数据包、persona、domain policy、工具语义、frame manifest/revision、重复试验、语音声道/音色、时间/步骤限制及 errors 的分母规则。当前文档对完整运行成本仍保留 TODO，因此本文不编造成本估计。

