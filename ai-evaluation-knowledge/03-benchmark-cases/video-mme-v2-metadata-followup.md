# Video-MME-v2 后续：真实任务元数据与分组标签

更新日期：2026-11-06。本页补充前一份 [分组评分案例](video-mme-v2-grouped-scoring.md) 尚缺的真实任务证据。当前可标 **D2，范围限定为真实任务文本、元数据、配置及关键源码**；没有下载或观看视频，因此不声称检查了视频与答案的对应质量，也没有运行模型。

## 实际读取了什么

通过官方 Hugging Face 数据服务读取 test split 的前四条完整 metadata。返回确认总计3,200条；四条属于 video `001`，question IDs 为 `001-1` 至 `001-4`，group type 为 logic，structure 为 `[1,2,3,4]`。`question`、`options`、`answer` 是独立列，另有视频 URL 与三级分类信息。返回没有截断单元格。

本研究只在此记录接口事实，不复制题目、选项、答案或视频内容。数据 revision 仍未固定，准确记录为2026-11-06访问的官方服务响应，不能误认为已经与代码提交锁定为同一数据快照。

[官方四行数据接口](https://datasets-server.huggingface.co/rows?dataset=MME-Benchmarks%2FVideo-MME-v2&config=default&split=test&offset=0&length=4)

## 一个有实际数据支撑的聚合区别

同一四题逻辑组的 `level` 不是固定值；所读组按题目顺序分别为1、2、3、3。独立脚本的 `get_final_acc` 按每条问题自己的 level 等字段聚合；`get_final_rating` 则把整组分数归给该组最后一题的 level、second_head 和 third_head。

因此该实现里的“level 1 accuracy”与“level 1 grouped rating”不只是对同一批题用两种公式。分组单位与类别归属也可能不同。解释分类结果时必须先说清楚单位：问题，还是以最后题标签归类的四题组。

这是由真实 metadata 加固定源码共同支持的结论，不是只用合成分类假设推出来的。是否符合论文设计意图，以及其他适配器是否一致，本次尚未核查。

[固定聚合实现](https://github.com/MME-Benchmarks/Video-MME-v2/blob/b2834bd4091d6234ccaf0fa1f149a7ef4eac5875/evaluation/test_video_mme_v2.py)

## 输入适配器应该核对什么

已读独立脚本显式把 `question` 与 `options` 拼到模型提示中。任何另一个工具包适配器都需要单独检查这个 mapping，不能因 dataset 名称相同就推断题干、选项、字幕和采样配置一致。对模型能力做比较前，先比较最终发出的输入往往更有价值。

当前没有新模型成绩。此前合成 scorer 微实验仍只是组件 D4；这次读取真实元数据不把它升级成完整数据集实验。
