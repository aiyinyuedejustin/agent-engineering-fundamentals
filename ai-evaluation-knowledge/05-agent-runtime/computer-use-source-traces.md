# OSWorld 与 BrowserGym：computer-use 的执行与计分边界

研究日期：2026-11-06。固定 SHA：OSWorld `8903ebeb0efdf74331bd7dc37ed91ccbbff22317`；BrowserGym `27a90ce815098f43414e93491e06907af468e45b`。

**本页 D3，未运行桌面 VM、浏览器 benchmark 或模型。** 两条链路均读过具体任务/配置及核心代码。不是性能排名；更不能从这里推导模型的相对优劣。

## 1. OSWorld：环境 reset→agent predict→action→最终状态验收

已追踪的普通 runner 是 [lib_run_single.run_single_example](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/lib_run_single.py#L15-L76)，不是文件中所有 provider 专用 runner：

1. 先 reset 环境，再把可能改变的 VM IP 交给 agent reset。
2. 等待环境就绪，获取初始观测、开始录屏。
3. 调用 agent.predict(instruction, obs)，得到 response 和 actions。
4. 逐个执行 actions，每次保存执行后的截图和 JSONL 记录。
5. 按 done 或 max_steps 停止，等待状态稳定，再调用 env.evaluate()。
6. 写 result.txt、任务完成记录、录屏。

**容易遗漏的预算语义：**普通 runner 的 step_idx 每次 predict 后增加一次，而一轮 predict 内可以执行多个 action。因此 max_steps 在这条实现中限制的是预测轮数，不是底层鼠标/键盘动作总数。其他专用 runner 必须逐个核对，不能仅凭参数同名推断等价。

### reset 的实际职责

[DesktopEnv.reset](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/desktop_env.py#L344-L410) 清空计数与 action history，根据环境是否已被使用决定是否还原 snapshot；setup 在成功以前也可能改变 VM，所以代码在 setup 前标记 environment used，失败重试能够触发还原。snapshot restore 可能返回新的 VM 身份，因此更新 manager 与 VM path。

**工程推断：**隔离质量需要验证失败 setup 之后的下一任务，不应只测试顺利完成后 reset。固定随机种子本身不能恢复后台进程、网络服务或桌面登录状态。

### observation 与 action

[DesktopEnv._get_obs/step](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/desktop_env.py#L412-L531) 提供 screenshot，并按配置提供 accessibility tree 与 terminal。动作存在不同 action_space；部分路径执行 Python 命令。WAIT、FAIL、DONE 为特殊动作。

step 内 reward 初始化为 0；最终成功率应读 evaluate，不可把逐步日志里的 reward=0 当作所有任务失败。DONE 只表达 agent 宣布停止，并不直接证明任务完成。FAIL 在 infeasible 类任务与可行任务的判定不同。

## 2. 一道实际表格任务的验收链

任务：[01b269ae…](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/evaluation_examples/examples/libreoffice_calc/01b269ae-2111-4a07-81fd-3fcd711993b0.json)。

任务要求填充指定表格范围内的空单元格，使用上方单元格的值，并保持无关区域不变。setup 下载工作簿并在 LibreOffice Calc 打开。

最终验收并非让 LLM 看一张截图打分：

1. evaluator.postconfig 激活目标窗口、触发保存并短暂等待。
2. result getter 从 VM 获取工作簿，expected getter 获取参考工作簿。
3. metric compare_table 按 sheet_data 规则比较第一个工作表的数据。
4. DesktopEnv.evaluate 返回指标结果，runner 保存为最终 score。

对应 [evaluate](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/desktop_env.py#L533-L602)、[file getters](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/evaluators/getters/file.py#L52-L231)、[compare_table](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/evaluators/metrics/table.py#L374-L502)。

### 验收范围不能等同自然语言要求

源码中的 sheet_data 规则通过 DataFrame 比较工作表数据，并使用默认四位小数精度。此具体配置没有同时启用所有格式、其他 sheet 或 formula-preservation 规则。

**工程推断：**“没有改动无关区域”可能包含数据、样式、公式、图表、隐藏 sheet 等不同含义；判分器只覆盖显式检查的部分。必须逐任务检查 criterion，不应从完整自然语言描述推定 grader 覆盖了全部要求。

### 文件获取与缓存细节

get_cloud_file 支持可选 sha256；提供时会核验缓存和下载内容。不提供时可复用已有缓存。该具体任务引用 main 上的远程文件且未声明 sha256。

get_vm_file 在部分失败时返回 None，compare_table 对缺失或无法打开的结果返回 0。**工程推断：**文件传输错误与 agent 没有产出可能落入同样分值，需要保留 getter 错误证据，不能只看 score。

## 3. BrowserGym：同一环境接口下可以有不同观测和动作政策

核心 [BrowserEnv.reset](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/core/src/browsergym/core/env.py#L223-L409)：

创建 task → 确定 task/override 的浏览器配置 → 启动 Chromium 和 context → task.setup → 初始化目标/聊天状态 → 等待 DOM 与活动页面检查 → 返回 observation。

[step/post_step](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/core/src/browsergym/core/env.py#L432-L548)：

action_mapping → 执行生成的 Python → 捕获 action error → 等待页面事件/DOM → task.validate → 提取新观测 → 返回 Gymnasium 五元组。

因此 action error 不一定终止 episode；错误可以成为下一轮 observation 的一部分。task.validate 的奖励与 done 逻辑由具体 task 实现，不是 BrowserGym 全局统一答案匹配。

### 观测不是天然“只看截图”

[_get_obs](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/core/src/browsergym/core/env.py#L612-L696) 可包含截图、DOM snapshot、accessibility tree、focus、URL、打开页面、上一动作错误等；另有 raw-page 模式。最终给模型什么还取决于 agent 的 obs_preprocessor。

官方 [demo 配置](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/demo_agent/run_demo.py) 默认 use_axtree=true、use_screenshot=false、use_html=false。由此不能把未核查配置的 BrowserGym 结果称为“纯视觉 computer-use”。

### 动作集合也是实验变量

[HighLevelActionSet.to_python_code](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/core/src/browsergym/core/action/highlevel.py#L515-L557) 区分 strict parser 与可搜索提取 parser，并区分单动作与 multiaction。允许多动作时，多条动作顺序执行，中间没有页面反馈。

底层 [execute_python_code](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/core/src/browsergym/core/action/base.py#L46-L73) 使用 Python exec，源码明确提醒它不是安全边界。**工程推断：**不要把 restricted action schema 与操作系统隔离混为一谈；任意 Python action 模式需要外层运行环境保护。

## 4. 实际 MiniWoB click-test 任务路径

[ClickTestTask](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/miniwob/src/browsergym/miniwob/all.py#L231-L234) 使用 subdomain click-test，实际 setup/validate 继承 [AbstractMiniwobTask](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/miniwob/src/browsergym/miniwob/base.py)。

setup 打开任务 HTML、按配置移除面向人的奖励显示、从 seed 派生网页随机种子并启动任务。该实现设定特殊 viewport，设置 screenshot scale factor。validate 验证页面/URL，然后读取网页任务状态，把正的 raw reward 变成二值 reward。

**可比性含义：**相同 MiniWoB 名称不保证同样 viewport、缩放、时间预算或 reward reduction。benchmark adapter 也可能改变评测接口，不只是搬运题目。

## 5. 实验层如何结束与保存

[EnvArgs.make_env](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/loop.py#L39-L96) 把 max_steps 传给 Gymnasium max_episode_steps。

[ExpArgs.run](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/loop.py#L386-L484) 创建 agent/env、reset、循环 get_action/step，并区分 terminated 与 truncated；agent 返回 None 被记录为 truncation。finally 尝试保存最后 step、summary 并关闭环境。

[summary](https://github.com/ServiceNow/BrowserGym/blob/27a90ce815098f43414e93491e06907af468e45b/browsergym/experiments/src/browsergym/experiments/loop.py#L519-L553) 包括累计 reward、error、terminated/truncated 和统计信息。结果读取器还涉及 pickle 文件，因此外来 result 包应视为不可信文件，不能随意反序列化。

## 6. 本轮确认的 unknown-unknown 检查项

| 容易忽略的问题 | 本轮直接证据 | 实验时需记录 |
|---|---|---|
| step 的单位 | OSWorld 普通 runner 每 predict 增一次，BrowserGym 外层限制 env step | model turns、tool batches、primitive actions 分开 |
| DONE 不是成功 | OSWorld 另行 evaluate | stop reason 与 grader outcome |
| screenshot 不是唯一输入 | 两套环境都允许额外观测，BrowserGym demo 默认 axtree | 实际模型可见 observation |
| setup 失败也会污染状态 | OSWorld reset 的 used 标志 | reset 前后状态、setup error |
| “原样保持”可能只检查部分维度 | 实际 Calc task 的 sheet_data 规则 | criterion coverage |
| provider/VM 状态会变化 | reset 之后更新 VM IP | 环境身份、snapshot 与恢复日志 |
| UI settle 时间影响 wall time | OSWorld 普通 runner 固定等待与逐 action pause | active/wait/setup/grading 分项时间 |
| 高层 action 不等于安全沙箱 | BrowserGym 的 Python executor | OS/container/VM 隔离措施 |

这些是源码证据支持的检查方向，不是已量化的性能影响或已复现的安全漏洞。

