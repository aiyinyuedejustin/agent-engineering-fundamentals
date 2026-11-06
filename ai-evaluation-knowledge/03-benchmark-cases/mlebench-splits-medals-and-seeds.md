# MLE-bench：重新划分的数据、奖牌阈值与 seed 分母

研究日期：2026-11-06。固定版本：openai/mle-bench @ `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`（2026-04-24）。

**D3：真实 competition 任务说明、配置、准备/评分/聚合路径已读。D4 仅限 19 项合成组件断言。没有下载 Kaggle 数据、训练模型、调用代理或重跑正式比赛。** 图像像素、训练行和历史报告的 LFS 大文件未核验。

## 1. 测量单位与资源条件

MLE-bench 让代理完成机器学习工程工作：理解数据、写训练/推理代码、实验、选择模型，最终提交预测文件。测量单位通常是一个完整 competition，不是一个训练样本，也不是 LLM 单次问答。

固定 README 的建议设置是 24 小时、36 vCPU、440GB 内存和一张 24GB A10，至少 3 个 seed，报告 Any Medal (%) 的 mean ± SEM。这些是推荐条件，README 明说可偏离但应披露；因此不能只看到 benchmark 名称就假定所有结果预算相同。

官方 2026-04-24 公告暂停新榜单提交，原因是改进公平、可比的提交流程。README 也将使用 test-set feedback 的部分提交分到额外表。这说明反馈访问权限是结果身份的一部分，不是只有模型与 GPU 需要记录。

## 2. 真实任务：Aerial Cactus Identification

本次读取 split75 中真实包含的 `aerial-cactus-identification`，它也在 22 题 low/lite 子集。输入是图像与训练标签，输出为每个图像 ID 的 has_cactus 概率，指标 ROC AUC。完整任务说明、config、prepare.py、grade.py 均已读，但未看图像像素或标签文件。

准备器不是使用 Kaggle 原始隐藏测试集：
- 从公开 old_train 以 `test_size=0.19, random_state=0` 新分 train/test；
- 新 test 的完整标签写入 private/test.csv；
- 对应图像复制到 public/test.zip；
- sample_submission 中的概率统一设为 0.5；
- 检查 ID 唯一、不重叠，以及样本数与列一致。

这意味着 benchmark 测试划分与原 Kaggle 榜单所用样本不同。历史排行榜阈值是参照物，不是证明代理真的在原始隐藏测试集获得同一名次。原任务说明保留过往比赛背景，实际执行协议还必须看 MLE-bench 准备器。

config 写了 `awards_medals: false`，但 benchmark 的通用 ranker 仍可计算参照阈值与 any_medal。Competition dataclass 没有 awards_medals 字段。故这里的“奖牌”是 benchmark 根据分数构造的能力门槛，不是声称 Kaggle 真的授予了奖章。

## 3. registry 中存在，不等于正式 split 中包含

也读了 registry 内的 Spaceship Titanic 任务和准备器：它从公开 train 再划分 10% 为新测试，输出布尔分类并按 accuracy 计分。但它**不在该提交的 split75.txt**。

这个例子说明扫描 competition 文件夹得到的任务数，不能直接当作正式 benchmark 样本数。full split、lite split、registry 所有可用任务应分开记录。

## 4. 从 CSV 到 competition report

路径：
`Registry.get_competition → grade_csv → competition.grader → competition-specific grade_fn → rank_score → CompetitionReport`。

Aerial Cactus 的 `prepare_for_auroc_metric` 先检查 ID/目标列、长度、概率范围，按 ID 排序，确认 ID 完全一致，再把真实标签与概率交给 ROC AUC。另一共享 accuracy helper 同样按 ID 对齐，因此提交文件原始行顺序不是评分依据。

通用 `Grader.__call__`：
- 无效提交或 grader 异常转换为 None，并记录日志；
- 成功返回的分数先 round 到 5 位小数；
- `grade_csv` 把 score 非 None 作为 valid_submission。

这最后一个条件不是“分数有限且合法”的同义词。合成函数若返回 NaN，wrapper 仍返回非 None 的 NaN，而阈值比较不给奖牌。本次只验证这个边界，不声称任何真实比赛的 grader 或数据产生过 NaN。每项指标应另做有效数值验证。

submission_exists、valid_submission、above_median、any_medal 是四种不同事件。文件存在但格式无效，与有效提交却未达到奖牌阈值，不能混为同一失败类型。

## 5. 阈值、方向和相等分数

`rank_score` 根据排行榜首尾的 score 推断“越低越好”还是“越高越好”，因此输入榜单顺序是契约的一部分。金/银/铜阈值由队伍数所在区间和榜单位置计算，median 使用 score 中位数。

- 达到奖牌阈值使用 ≤ 或 ≥，相等计入。
- above_median 使用严格 < 或 >，相等不计入。
- 金、银、铜互斥，金牌不会同时再计一枚银或铜。
- score=None 时所有这些成功标记为假。
- 5 位小数的 rounding 在阈值比较之前，近边界结果可能因此改变奖牌事件。

合成 100 队榜单用整数分数构造：60.999999 原本未到铜牌线 61，wrapper 四舍五入后达到 61。这是评分顺序的行为示例，不是声称真实榜单阈值是 61，更不是未经上下文认定 rounding 错误。

未取得实际 leaderboard.csv 的 LFS 对象，所以本文没有报告该真实 competition 的数值奖牌门槛。已看到的指针哈希不等于已读实际榜单内容。

## 6. 聚合时的两个分母

基础 `aggregate_reports` 仅对给定 report 列表数成功次数；它的 docstring 仍提 pass_at_n，但函数没有该参数，也没有 best-of-N 操作。不能只读注释就把输出解释成 pass@N。

正式 README 指向 `experiments/aggregate_grading_reports.py`：

1. 根据选定 split 读取应评 competition IDs。
2. 按每个 competition 的报告读取顺序构造第 1、第 2……个 seed。
3. 每个 seed 用同一组 competition 做等权 any-medal 百分比。
4. 对 seed 的百分比取均值，并计算跨 seed 的 SEM。

缺报告有两种不同政策：
- 默认要求每个预期 competition 至少有报告，并以各题可用报告数的最小值决定完整 seed 数；多出的尾部报告不会进入这次完整-seed聚合。
- `--pad-missing` 按最大可用数构造 seed，缺项补失败报告。README 有脚注标出部分榜项使用此法。

合成例：A、B 第一次都成功，只有 A 有第二次且失败。默认保留一个完整 seed，均值 100%；补失败后两个 seed 的均值为 50%。这不是原始数据的变化，而是缺失处理改变估计对象。

此代码以“每题第 n 份报告”配对，没有在这个结构中保存明确的全局 seed ID。源注释也强调不要按有效性重排。上游若漏掉中间某次运行，仍应核查真实 run-group 对齐，不能只凭列表长度保证同一实验配对。

## 7. 误差条是什么意思

该版本要求报告 mean ± **SEM**，不是默认 95% CI。脚本同时算 `mean ± 1.96×SEM` 的区间，是正态近似而非本次对 competition 抽样的 bootstrap。

当只有一个 seed，代码将 SEM 设为 0；这不是“已经知道该系统无随机波动”，只是无法从单个 seed 估计跨运行方差的实现选择。重复 seed 的波动也不涵盖比赛选择、数据划分或部署分布变化带来的不确定性。

## 8. 实验及失败尝试

[脚本](mlebench_grade_probe.py) 和 [结果](mlebench-grade-probe-output.json)：
- 19 项断言均通过；
- 用真实固定源码中的 Grader、seed 聚合和 CSV 对齐函数；
- 数据、排行榜和报告均为人工合成；
- pandas 2.2.3、numpy 2.3.5；
- 没有执行训练、下载比赛或把合成分数当成 agent 成绩。

最初探针抽取时遗漏了源文件的延迟类型注解语义，加载出现 NameError；修正为保留 future annotations 后才运行断言。最终输出对应修正后的脚本。

曾尝试读取仓库内一个历史 grading report，GitHub 返回 LFS pointer；对应 media URL 不被 GitHub connector 支持，通用网页提取又不支持该内容类型。没有成功获得历史报告正文，故**没有历史成绩复算**，不把尝试过的路径标成 D4 复现。

源文件 SHA256：
- grade_helpers.py：`3e2683df1c3a9e0594a068d55ad9d6f053c6381927a211b1d352f7e122e9902f`
- aggregate_grading_reports.py：`f17b1381a771e3ce3fdbc5a5b504e5e6a2edc5dd5b1b8924e5a4c33ea2df543b`
- competitions/utils.py：`670622dc0417a05e57715287459601cfd854e552d796f6d6311b525b135a876d`

## 9. 复现清单

至少保存：competition split、原始数据许可与哈希、prepare 脚本/库版本、数据划分、参考榜单 LFS 对象、grader、代理/模型/工具、硬件与时限、是否访问测试反馈、每次运行 ID、无效/缺失提交政策、seed 对齐与误差条定义。把这些写清，比只列“MLE-bench 分数”更能支持系统选型。

## 固定官方来源

- [README 与暂停新提交公告](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/README.md)
- [正式 split75](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/experiments/splits/split75.txt)
- [实际 Aerial Cactus 任务目录](https://github.com/openai/mle-bench/tree/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/mlebench/competitions/aerial-cactus-identification)
- [Registry](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/mlebench/registry.py)
- [评分入口](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/mlebench/grade.py)
- [通用奖牌评分](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/mlebench/grade_helpers.py)
- [指标输入对齐](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/mlebench/competitions/utils.py)
- [跨 seed 聚合](https://github.com/openai/mle-bench/blob/507f92e1138bb6e40dac5c6ee7a6758e6424bf97/experiments/aggregate_grading_reports.py)

