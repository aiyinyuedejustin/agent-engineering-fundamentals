# OSWorld：屏幕动作与真实状态判分分离

研究日期：2026-11-06。深度：**D3（原 OSWorld 仓库单任务执行/评分链）**。未运行 VM 或模型。适合 L1–L3。

## 精确范围

固定 `xlang-ai/OSWorld` commit：`8903ebeb0efdf74331bd7dc37ed91ccbbff22317`（2026-11-02）。这是原 OSWorld/Verified 系列代码实例，**不是 OSWorld 2.1 任务复现**。

[原项目页](https://os-world.github.io/)注明其 369 任务，部分网络依赖可能使评估成为 361 任务。新的 [OSWorld-V2](https://github.com/xlang-ai/OSWorld-V2) 在本次读取时推荐 `osworld-v2.1`（2026-09-16），要求 code、task files、assets、mock websites 和 VM images 同版。不能把旧 369 题结论自动搬到新版长流程任务。

## 读取的真实实例

[Chrome task 030eeff7-b492-4218-b312-701ec99ee0cc](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/evaluation_examples/examples/chrome/030eeff7-b492-4218-b312-701ec99ee0cc.json) 的目标是打开 Chrome 的 Do Not Track 设置。这里只描述目标，不在用户真实浏览器执行任何改动。

配置有：
- `snapshot` 和启动 Chrome 的 `config`；
- 用户可读的 `instruction`；
- `evaluator.postconfig`：失焦、等待、重启浏览器等动作，以让状态落盘；
- `func=exact_match`；
- `result.type=enable_do_not_track`；
- `expected.type=rule`，期望值为字符串 true。

## 源码链

[desktop_env.py](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/desktop_env.py) 中，`_set_evaluator_info` 用配置名称绑定 metric 与 getter；`step` 执行动作并返回新观察；`evaluate` 先跑 postconfig，再取得 result/expected 并调用 metric。

[get_enable_do_not_track](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/evaluators/getters/chrome.py) 读取浏览器 Preferences JSON，按 OS/CPU 架构选择路径，并把设置转换成 true/false 字符串。[exact_match](https://github.com/xlang-ai/OSWorld/blob/8903ebeb0efdf74331bd7dc37ed91ccbbff22317/desktop_env/evaluators/metrics/general.py) 进行精确比较。

因此评分不是让视觉模型判断截图“看起来设置成功”，也不要求复制一条固定点击轨迹，而是读取真实应用状态。UI 任务可以拥有确定性 state-based oracle。

## 隐含假设与潜在误差

- getter 假设正确的浏览器 profile 路径；多 profile、安装变化、ARM 与 x86 差异会改变路径。
- 设置未持久化前评分可能是假阴性，故 postconfig 是测量的一部分。
- getter 捕获异常后返回 false，会把某些读取故障和真实未完成合并。工程平台应额外保留 getter 错误日志。
- state success 不能证明动作安全、没有不必要操作或隐私目标真的实现。Do Not Track 配置正确也不保证网站尊重它。
- agent 可用动作空间会影响测量对象；GUI-only 与可直接执行 Python 的设置不能无说明比较。

## 可复现清单

除模型名外，还需固定 dataset/release、VM image digest、分辨率、动作空间、步数/时间预算、浏览器版本、网络/proxy、profile、setup/postconfig、getter 和 metric 代码。新版还需同版 task assets 与 mocked websites。
