# BFCL v4：函数调用、状态成功与答案命中不是同一种事件

研究日期：2026-11-06。固定仓库：ShishirPatil/gorilla @ `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`（提交时间 2026-03-23）。以下路径均相对其 `berkeley-function-call-leaderboard/`。

**深度：D3，限已读真实任务与公开执行/评分路径；另有 D4 组件实验。没有运行模型、真实 API、完整模拟环境或复现排行榜。** 本文不是对历史所有 BFCL 版本的说明，也不把仓库 README 的“executable”概括等同每个当前类别都会执行函数。

## 1. 真实任务和版本边界

已读 `bfcl_eval/data/BFCL_v4_simple_python.json` 的完整 `simple_python_0` 及对应 possible_answer：几何计算工具，两个必需整数参数和一个可选字符串参数。这里的目标是生成指定函数及可接受参数，不是自行计算最终数值。可选参数在标准答案里以候选值列表表达，空字符串兼作“允许省略”的标记。

也读了 `BFCL_v4_multi_turn_miss_func.json` 的 `multi_turn_miss_func_0`：多个用户轮次、模拟文件系统与另一个工具类的初始状态、指定时点缺失/补充的函数，以及空用户轮次。本文仅保留结构，不复制完整问题、标准答案或样例初始配置。

`category_mapping.py` 的版本前缀是 BFCL_v4。当前分类包括 single-turn、live、multi-turn、web search、三种 memory backend 和 format sensitivity。旧 exec、REST、SQL 类别在分类列表注释掉，相关数据放在 unused_datasets；runner 也跳过 executable/SQL/chatable。**这是固定版本的选择，不代表所有版本从未执行过这些任务。**

## 2. 单轮主路径：可接受调用表示，不是运行结果

路径为：

`evaluate_task → load_dataset_entry / load_ground_truth_entry → ast_file_runner → handler.decode_ast → is_function_calling_format_output → ast_checker → save_eval_results`。

- 原生 function-calling 的 OpenAI completion handler 对参数 JSON 解码。
- prompting 路径清理包围符、补方括号，通过 Python AST 或相应语言 parser 得到函数名与参数字典。
- simple 要求一个调用；multiple 从可选工具中找标准函数；parallel 允许顺序变化，但要求调用数量相同。
- 函数名可能按模型配置把点转换为下划线，因此名称正规化也属于适配器协议。
- 必需参数不能缺失，意外参数会失败。可选参数是否可省略仍取决于答案候选是否含空字符串。
- Python 类型检查使用精确 type；bool 不等同 int。显式允许 int 转 float，tuple 会转 list。字符串比较去掉若干标点与空格并忽略大小写，存在由规范化主动合并的不同字符串。
- 类型检查的支持范围有限；源码说明不是任意深度的通用递归类型验证器。

因此 AST pass 表示“解码后的调用符合该答案集合与正规化规则”。它不能独自证明函数真的可运行、服务状态正确、用户目标完成，或副作用安全。

## 3. parallel 的“无序”不等于全局最优匹配

`parallel_function_checker_no_order` 对每个标准调用依次找第一个未使用且合格的模型调用，命中就占用该位置，没有回溯或二分图匹配。

合成实验给两个同名调用设置允许参数集合 [1,2] 与 [1]。模型输出顺序 [1,2] 失败，改成 [2,1] 成功；两组都存在完整合法配对，但贪心选择对第一组提前用掉唯一的 1。

这只证明**允许集合重叠时的组件边界**。尚未对全部真实 gold 做重叠条件扫描，不能据此断言已发布分数受到影响。

## 4. multi-turn：每轮公共状态 + 累积返回值，不是逐步轨迹一致

`_evaluate_single_multi_turn_entry` 要求轮数与 gold 相同；逐消息 decode_execute，忽略解码失败/空调用，再交给 `multi_turn_checker`。

后者在模型与 gold 的独立实例上重放调用。状态对象用 model、entry、class 等构造缓存键，连续轮次复用。执行器导入模拟后端，补实例名称后执行调用；这不是本文实际执行过的环境，也不据此认定已形成安全隔离。

对于非空 gold 轮次，评分同时检查：

1. gold 对象上的公共属性是否相同。私有属性跳过；仅在模型侧新增的属性不会被该比较遍历。
2. gold 当前轮的返回值是否包含于模型截至当前轮的所有返回值中。顺序不要求一致，但重复次数要够。
3. 方法调用顺序 checker 存在，但调用处被注释。

这是允许不同有效路径的一种设计，也意味着“同状态且覆盖返回值”与“相同过程”不是同一指标。较早轮次得到的返回值可以满足后面轮次需要。

**空 gold 轮次还需要单独审计。** 主 checker 会执行模型调用后直接 continue，跳过该轮状态与返回值比较。源码注释说 irrelevance 由独立 helper 检查；然而该固定 `eval_runner.py` 只导入 `multi_turn_irrelevance_checker`，没有调用它。组件实验用假执行器构造一个空 gold 末轮：主 checker 返回真，独立 irrelevance helper 返回假。这个实验没有执行真实后端，也没有估计真实任务或模型的触发比例。它提示工程检查应追踪 helper 是否进入正式路径，而不是看到函数存在就认为约束已生效。

## 5. agentic：最后非工具消息的字符串命中

web search / memory 的评分分支收集解码不了或为空的消息，选最后一条作为非工具回答；中间工具调用不直接计入这个最终 correctness checker。

`agentic_checker` 把答案与回答做有限标点/大小写规范化，然后用带单词边界的正则寻找任一可接受答案。实际实现没有删除空白，虽然注释写到 whitespace。

合成实验：
- “It is not amber.” 对答案 amber 仍通过：字符串出现并不理解否定。
- NewYork 对 New York 不通过：空格未被删除。
- ambergris 对 amber 不通过：边界规则生效。

这些是匹配器语义，不是对模型检索能力的测量。不能把 agentic accuracy 解释成所有工具动作、来源真实性、引用或完整对话均已验证。

## 6. 总分与缺失结果

`eval_runner_helper.py` 给出的该版本总分权重为：
- non-live 10%
- live 10%
- irrelevance 10%
- multi-turn 30%
- agentic 40%

各层内部也不一致：non-live 分层等权；live 的 AST 四类按题数加权；multi-turn 四类等权；agentic 先平均 web 的两类和 memory 的三后端，再让两组各占一半。format sensitivity 和 live relevance 会输出，但不进入上述五项总分公式。不能用所有原始题目的简单微平均重建它。

默认会检查完整结果数量；显式 `--partial-eval` 可仅评已有结果。类别 accuracy 分母是结果条数，partial 结果不能和全量正式榜直接比较。总表还会读取已有本地 score 文件补齐其他类别，复用旧产物时必须记录每类版本与来源；缺失类别在总体计算中可作为 0 而非仅改变分母。

## 7. 实验与复现边界

[实验脚本](bfcl_checker_probe.py) 与 [完整结果](bfcl-checker-probe-output.json) 共 15 项断言，均通过。脚本只提取已读评分函数，未导入模型 SDK、下载数据、执行候选代码或调用外部工具。最后两项明确使用假执行器，验证控制流，不是假装跑了 BFCL 环境。

源文件 SHA256：
- ast_checker.py：`ad21dc1b57b2835029bbf0556d9737399dad58fdef6af248ef45fcd7327ecd3a`
- agentic_checker.py：`9ece48a8bfb702039793ba14d1f3fde27242a5e9361fdcdc7f7243d446583199`
- multi_turn_checker.py：`da48a1d490a9d9a9ff7661e3633b674ecde4da11266057462fc2ede547edfc2f`

未完成：全量 overlap 扫描、真实 multi-turn 后端执行、web/memory 的外部服务/缓存再现、各模型 adapter 的逐项核验、官方已发布结果重评分。D4 不能传播为“BFCL 已完整复现”。

## 8. 使用建议

- 选工具接口模型：分别报告 AST 类别、irrelevance、multi-turn 和 agentic，保留总分权重。
- 选生产 agent：另加真实服务状态、权限边界、失败恢复、消息/财务副作用检查。单一 BFCL 分数不足。
- 重建实验：固定仓库、数据、handler、FC/prompting 模式、返回格式、类别、partial 开关、搜索配置、memory backend、旧 score 文件策略。
- 验证 grader：加入规范化碰撞、候选集重叠、空 gold 轮次、否定句、重复返回值等单元测试，且区分设计选择与未覆盖契约。

## 官方证据

均为固定提交的公开源代码，不链接本地工作副本：
- [README](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/README.md)
- [类别与版本](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/constants/category_mapping.py)
- [任务目录](https://github.com/ShishirPatil/gorilla/tree/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/data)
- [runner](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/eval_runner.py)
- [AST checker](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py)
- [multi-turn checker](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py)
- [模拟执行器](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_utils.py)
- [agentic checker](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/agentic_eval/agentic_checker.py)
- [聚合权重与分母](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/eval_runner_helper.py)
- [模型适配器](https://github.com/ShishirPatil/gorilla/blob/6ea57973c7a6097fd7c5915698c54c17c5b1b6c8/berkeley-function-call-leaderboard/bfcl_eval/model_handler/api_inference/openai_completion.py)

