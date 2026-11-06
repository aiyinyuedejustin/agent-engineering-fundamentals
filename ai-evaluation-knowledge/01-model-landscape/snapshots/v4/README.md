# 第四次稳定快照：视频评测适配器组件审计

冻结日：2026-11-06。本增量不替换v3模型来源/成绩记录；它只新增MC003、MC004两条源码/实验记录。

- 固定VLMEvalKit commit `933eda4c27844b38f57ff6733ab72aa25110bd1b`，九个文件Git blob及SHA-256验证。
- D3限定为Video-MME-v2适配器执行路径。真实任务文本/metadata已读，视频未看；数据revision未pin。
- D4限定为18个实际执行的合成组件探针。模型、judge、实验网络调用和真实视频打开均为0。
- 原创中文说明与脚本见 `experiments/vlmevalkit-video-adapter/`。无上游源码副本，无benchmark题干、选项或媒体副本。
- 已验证的条件差异包括分列options进入fallback后为空、首层字母解析、字幕时间窗、采帧端点和raw-video尺寸元数据。不能外推为官方成绩错误或模型性能排名。

模型来源仍以v3的113条来源、147条D1数值观察为准；v2的27项gpt-oss组件实验另有记录。不要将来源数、模型数、数值观察数或合成探针数混加。
