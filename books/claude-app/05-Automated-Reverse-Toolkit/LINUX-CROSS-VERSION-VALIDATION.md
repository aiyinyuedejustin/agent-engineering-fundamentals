# 用两个真实版本检验差分：数量变化不等于功能变化

Linux amd64 **2.31226.1 → 2.37337.1**，在2026-10-15使用已发布的 `deb_versions.py` 与全部默认预算，完成同一ASAR及精确companion范围的真实跨版本比较，退出0。最有用的结果不是“多了76、少了33”，而是：**33个移除候选都能在新作用域里找到同键同值的对应项。**

## 1. 先确认两边比较的是同一种东西

两个输入都来自官方stable APT索引，包大小与SHA256分别匹配。外部来源核查将Packages摘要对到InRelease签名，再将签名指纹与[官方Linux文档](https://code.claude.com/docs/en/desktop-linux)对照。包身份、指纹、工具源码摘要与独立复核计数集中在[机器记录](LINUX-CROSS-VERSION-VALIDATION.json)。

工具从两个DEB中选择相同的 `usr/lib/claude-desktop/resources/app.asar` 与 `.unpacked` 前缀。两侧均通过规定的AR/XZ/GNU TAR完整流、ASAR声明和精确companion检查；未改预算或更换提取规则。

| 范围内指标 | 2.31226.1 | 2.37337.1 |
|---|---:|---:|
| ASAR声明文件完整性通过 | 470 | 489 |
| companion文件 | 3 | 3 |
| 选区原料字节 | 74,502,975 | 79,057,846 |
| 逻辑展开字节 | 76,731,057 | 81,280,912 |
| scanned | 410 | 427 |
| hashed-only | 44 | 44 |
| scan-incomplete | 16 | 18 |

容器完整性通过与扫描覆盖是两个结果。两版都有未完成扫描的文件，快照的complete_within_declared_scope都为false；警告和失败分类原样保留。

## 2. 先读候选，再解释增删

| 候选类别 | 新增 | 移除 | 值变化 | 相同键/范围 |
|---|---:|---:|---:|---:|
| CSS token | 76 | 33 | 0 | 2,341 |
| CSS色阶 | 0 | 0 | 0 | 714 |
| 旗标 | 0 | 0 | 0 | 0 |
| 工具契约 | 0 | 0 | 0 | 4 |
| 遥测 | 0 | 0 | 0 | 1 |

这些数量按类别、键名与作用域计数，不是唯一品牌变量数或产品功能数。尤其是旗标两侧均无匹配候选，不能将0差分解释成没有旗标或旗标没有变化。全部109个增删候选仍保留uncertain状态。

文件路径/字节摘要另得到369新增、350移除、27变更；唯一精确字节的possible-move为0。含内容指纹的文件名会随内容变化，不能把这些文件数直接换算成增删功能。

## 3. 33个“移除”为什么没有直接变成删除结论

逐组对照发现：

- **28组排版候选**保留键名与值集合，但选择器范围纳入排队消息区域。
- **4组气泡布局候选**保留原值并扩大作用域；新样本另有堆叠气泡的间距、相接圆角和正文缩进声明。
- **1组环形边框工具类候选**来自选择器合并。

33组都具有唯一的同键/同值、不同scope对应项。扫描器按精确作用域区分身份，因此产生removed与added；这不足以证明变量被删除，也不证明CSS级联语义完全等价。

剩余新增候选还包括按钮/卡片按压缩放、编辑器评论边框相关静态声明。它们提供下一轮界面核查的方向；本次没有执行目标应用，不把声明存在写成已启用的功能或路线图。

## 4. 复算同一范围

先按[DEB投影说明](DEB-PROJECTION.md)准备两个有权读取的本地包，在工具箱目录运行：

```sh
python3 -B deb_versions.py compare OLD.deb NEW.deb --asar-member usr/lib/claude-desktop/resources/app.asar --companion-prefix usr/lib/claude-desktop/resources/app.asar.unpacked --old-label 2.31226.1 --new-label 2.37337.1 --platform-label linux-amd64 --output NEW_PRIVATE_DIRECTORY
```

本次compare机器执行耗时81.738秒；不包含下载和分析，也不是性能承诺。独立复核验证53项报告合同，并逐一核对13个运行工具文件与[固定发布提交](https://github.com/aiyinyuedejustin/agent-engineering-fundamentals/tree/fbc57b9431b3ac6f59174b55fbc3b2594561a440/books/claude-app/05-Automated-Reverse-Toolkit)一致，没有重跑或执行产品字节。

输出中的原包提取树、完整快照和字面量报告应保留为私有材料。这里只交付原创摘要与计数。外部签名索引校验与工具自身解析职责分开，工具的publisher_authenticity_verified仍为false；本案例仅覆盖指定Linux两版本与ASAR范围，不扩展到整包、完整JavaScript语义或其他平台。

[返回工具箱](README.md) · [扫描诊断](SCANNER-DIAGNOSTICS.md)
