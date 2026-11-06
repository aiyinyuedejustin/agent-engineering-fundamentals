# Computer-use 动作传输：一次点击不只是一个函数名

研究日期：2026-11-06 UTC。OSWorld 固定版本 `8903ebeb0efdf74331bd7dc37ed91ccbbff22317`。本文件补充 [computer-use source traces](computer-use-source-traces.md)，追踪 DesktopEnv.step → PythonController → guest HTTP server。

**D3，未启动 VM、未执行 UI 操作。**收集已关闭到本节明确列出的 endpoint 和调用链，其他 runner/endpoint 不自动继承结论。

## 1. 动作完成有三层含义

[DesktopEnv.step](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/desktop_env.py#L483-L531) 根据 action_space 调用 controller，等待 pause，再抓取 observation。它不把 execute_python_command 的返回字典放进 info 或 observation。

[PythonController.execute_python_command](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/controllers/python.py#L256-L297) 把命令包装为 guest 内 `python -c`，POST `/execute`。收到 HTTP 200 后返回 response.json，并记“Command executed successfully”。

guest [execute_command](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/server/main.py#L78-L119) 用 subprocess.run 执行，正常返回时 JSON status 为 success，另带 returncode；即使命令 returncode 非零也走此 HTTP 200 分支。timeout 等 Python 异常才走 HTTP 500。

因此必须区分：

1. HTTP 请求/应答成功。
2. guest 程序 returncode 成功。
3. UI 操作产生预期效果，最终任务通过 grader。

**源码事实：**该普通 step 路径没有直接把程序错误文本反馈给 agent。模型仍可能从下一张截图推断未成功，但这不是明确的工具错误事件。日志分析不能仅搜索 “Command executed successfully” 作为 UI 动作成功率。

## 2. Retry 也会改变任务状态

同一 controller 对 execute_python_command 有专门的 [_failed_before_sending](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/controllers/python.py#L16-L36) 判别：只有 connect timeout、connection refused、DNS 或新连接失败等被归为未到达 guest 的情况才重试；read timeout、响应后断连等结果不明情况不直接重放动作。

这是因为键盘/鼠标动作通常不幂等：第一次实际打字完成但应答丢失，再试会输入两遍。该路径还禁用 HTTP redirects，以免把动作 POST 当成无害读请求。

其他入口并不完全一致：[run_python_script](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/controllers/python.py#L336-L359) 在 ReadTimeout 时停止，但其他异常走较宽 retry；[run_bash_script](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/controllers/python.py#L361-L411) 对非 200 响应等也可能重试。

**推断：**仅说“controller 有三次重试”不足以描述实验。要按 endpoint、异常类型、是否可能已产生副作用区分。本轮没有注入网络故障，未证明某次实际 run 出现了重复动作。

## 3. 输入设备状态能在进程死亡后继续影响任务

[release_stranded_input](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/controllers/python.py#L299-L334) 明确处理被中断的 keyDown/mouseDown。键盘 modifier 可以在发起进程结束后仍保持按下，使后续输入变成快捷键、点击变成 Ctrl-click。

清理通过 Linux XTEST 释放按钮和当前按下的键。源码也明确说这是 best-effort：失去响应后原命令可能仍在运行，清理之后再次按下；其他 OS 的依赖也不同。

这是一类容易漏掉的环境状态：文件、窗口、浏览器 cookie 之外，还有键盘 modifier、鼠标按钮、剪贴板、焦点、拖动状态等。截图或普通文件 snapshot 未必足以证明这些状态一致。

## 4. 时间预算在不同层分别存在

- execute_python_command 的 HTTP timeout=120 秒，guest `/execute` 的 subprocess timeout 也是 120 秒。两层近似同时超时，HTTP failure 不能单独识别 guest 已否停止。
- run_python_script 的 HTTP timeout=90 秒，但 guest `/run_python` 的 subprocess timeout=30 秒。
- run_bash_script 传给 guest 的 timeout 与 host HTTP timeout+100 分开。
- step 的 UI pause 和最终截图仍在动作之后发生，不包含在某些 endpoint 的 subprocess timeout 内。

这些数值来自固定源码，不是对 UI 延迟分布的实测。记录 elapsed time 时应标清 measurement boundary，尤其不能把每个 action 的 HTTP deadline 直接当成 agent 总 wall-clock budget。

## 5. 动作 schema 不自动构成权限边界

`computer_13` 的动作映射把动作转成 PyAutoGUI 代码，其中移动还包含随机 easing/duration；而 pyautogui/claude_computer_use/gemini_computer_use 路径可以把传入 Python 字符串交给 execute_python_command。

guest endpoint 直接执行传入 command，没有在这个函数内验证“只允许鼠标键盘 API”。因此 screenshot-only observation、PyAutoGUI 风格 prompt、严格只允许 GUI 操作，是三个不同约束。

**工程推断：**若报告声称 agent 只通过 GUI 完成任务，需要进一步审计 agent 生成动作的范围、wrapper 验证、可达 endpoint 和日志。不能只看 action_space 的名字。此结论不表示任何具体 agent 已作弊，也不是完整安全审计。

## 6. 有判别力的后续测试

1. guest 执行成功后丢弃应答，分别测试普通 input 与脚本 endpoint 是否重复动作。
2. guest 返回 HTTP 200 + 非零 returncode，核对 agent 可见 observation、日志与失败分类。
3. 在 keyDown 后中断，再验证 modifier state、清理是否成功和下一步行为。
4. 固定 random seed 与移动时长，对比相同动作计划的可重复性。
5. 对 action allowlist 做负例测试，而不是只审查 prompt。

这些仍是 D0 实验候选，不是已完成的运行证据。边界恰好说明为什么真实 task/config/source trace 比单纯 reading README 更有价值。
