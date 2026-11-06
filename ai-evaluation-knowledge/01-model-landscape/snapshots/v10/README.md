# 第十次稳定快照：HLE评分组件

冻结日：2026-11-06。

- 这是代码增量，不替换v9模型数据视图：122来源、52D1、252个D1数值观察。
- MC007限定D3源码路径，MC008为25项实际运行的无模型/无judge/无网络合成组件D4。
- 八个源码文件commit/双hash固定；25项探针重放结果字节相等；NumPy与上游pin不一致已披露。
- 当前分支四组组件共89个不同合成探针：27gpt-oss+18VLMEvalKit+19Ovis+25HLE。不能算89次模型评测或89个benchmarks。
- HLE校准最后bin、temperature转发、缓存、Wald边界只针对simple runner，不声称当前发布榜单受影响。
- Diamond任务rows返回401，停止读取；仅公开metadata，实际题目/图片未读，不冒充真实任务D2。
- 此目录不包含上游原始源码或benchmark数据，只有原创审读、测试编排、hash清单和合成结果。
