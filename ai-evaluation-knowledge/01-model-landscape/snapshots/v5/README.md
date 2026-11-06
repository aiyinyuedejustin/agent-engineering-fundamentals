# 第五次稳定快照：音频与翻译报告扩展

冻结日：2026-11-06。继续收集中，尚非最终综合。

- 当前模型来源视图113条：38条D1、75条D0。本轮将Step-Audio2、MiMo-Audio、Hunyuan-MT、HY-MT1.5的限定原文章节升级D1，没有增加候选计数。
- 当前数值观察视图190条，全部D1作者报告、未独立复现。ME001–147与v3逐条一致；新增ME148–190共43条。
- 新增原创专题笔记 `report-reading-notes-v5.md`。旧v3专题笔记应继续保留，不被本文件替代。
- v2的gpt-oss与v4的VLMEvalKit代码/组件实验仍是独立补充，不随此模型数值视图升级深度。
- 原始全文、任务题干、音视频与源码快照均未放入本目录。

主要可比性限制：MMAU修订与mini模型身份、ASR→judge的构念边界、SpeechMMLU/MultiChallenge Audio过滤与历史模态、翻译reward与评价指标共用、XCOMET/CometKiwi排序反转、WMT24pp与WMT25不同切片、顺序短文本response time不是首包/并发/端侧延迟。
