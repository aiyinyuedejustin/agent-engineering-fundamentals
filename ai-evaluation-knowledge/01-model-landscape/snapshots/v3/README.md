# 模型报告第三次稳定快照

冻结日：2026-11-06。继续采集中，尚非最终综合。

- 113条来源记录：34条D1、79条D0。新增19条来源线索，避免把同系列多个尺寸机械计成独立报告。
- 147条模型—评测数值观察：全部D1，报告作者所报、没有独立复现；ME001–099沿用v2，新增ME100–147。
- 新增原创中文分析：`report-reading-notes-v3.md`，覆盖GLM5、LongCat、MiMo、ERNIE、Qwen3-Omni、InternVL3.5、HunyuanVideo1.5，以及新来源的时间边界。
- v2的gpt-oss D3/局部D4组件实验继续有效，但本目录不重复复制。模型成绩不因该实验升级深度。

## 新的汇总陷阱

1. WER越低越好；F1不能等同AP/AUROC。
2. HunyuanVideo的“Win Rate”是两方偏好率之差，应使用百分点，非概率。
3. 单GPU最低显存与8GPU最快速度来自不同设置，不能合成一个不存在的部署配置。
4. GUI grounding、online agent、空间问答与真实机器人控制分别解释。
5. LongCat的模型判分不是原始exact match；GLM的verified修改任务不是原Terminal-Bench。
6. 来源日期只保留已知精度。搜到openPangu Git LFS指针不等于拿到报告；出版页日期不必等于模型首发日。

JSON唯一ID、source_id引用与未复现标志已检查。本目录不含报告全文、私有信息或复制的上游源码。完整字段与局限见各条记录，汇总不可丢失配置与限制。D0不是已核验模型，D1也不意味着读完全文。
