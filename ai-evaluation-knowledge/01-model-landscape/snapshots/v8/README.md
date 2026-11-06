# 第八次稳定快照：Ovis媒体预处理与预算组件

冻结日：2026-11-06。本目录只新增MC005、MC006，不替换v7模型来源/数值JSON。

- GitHub固定commit e1916bf3cb0ca123e71ab173ff4463df5c3a71b5，八文件blob及SHA-256校验。
- D3限定为媒体和chat控制流。HF分发remote-code另有revision与不同入口，未执行；真实图像任务未观看。
- D4限定为19项实际合成组件实验。NumPy显式替代Torch张量控制操作，图像processor为零数组，generation为固定token输出。无权重、模型、judge或实验网络调用。
- 非默认temporal参数与极端宽高比单独标注，不作为已发布检查点故障证据。
- 代码/分析/结果为原创成果；没有上游源码副本或实际任务图片。

当前模型表仍取v7：113来源、43D1/70D0、229条D1报告数值。此前v2有27项gpt-oss组件探针，v4有18项VLMEvalKit组件探针；这里19项是新组件实验，不是新增模型成绩。
