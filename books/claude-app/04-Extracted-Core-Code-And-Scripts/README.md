# 核心实现与研究工具

这里放命名清楚、能独立阅读和运行的工程化实现，以及将结论连接到输入的工具。算法示例采用原创重写；完整安装包、商业字体和混淆产物不放进代码库。

## 随仓即可运行

- [原创机制实验室](core-code-lab/README.md)：流式协议、对话树、执行循环、预览状态、记忆与配置；123 项离线测试。
- [三张学习图生成器](scripts/build_learning_figures.py)：Python 标准库生成坐标、UTF-8/SSE 与分支阅读图。

## 需要本地产品样本的工具

- [精选证据校验](scripts/verify_evidence.py)：核对源文件身份与声明定位。
- [三平台 UI 对照](scripts/compare_ui_trees.py)：从三份解包目录重新生成清单与差异，不依赖缓存计数。

## 设计图与交互测试

- [色卡与组件图生成](scripts/make_anatomy_figures.py) · [表面图生成](scripts/make_study_figures.py)：从设计数据重建原创 SVG。
- [基础交互测试](tests/demo-state/README.md) · [密度、阅读与 Quick Entry 测试](tests/phase2-components/README.md)：可复现的状态与静态检查。

## 证据与数据

[方法附录](evidence/README.md) · [来源索引](evidence/sources.md) · [设计参数](evidence/data/design-token-summary.json) · [跨平台对照](evidence/data/platform-comparison.json)

算法模块随对应章节提供。书中的“实现示例”与产品中的“实现事实”通过标题和引用分别标明，便于直接改写而不混淆归属。

- [导航与退出实验](shell-lifecycle/README.md)：导航代际、晚到回调、具名清理与落盘结算；7 项离线测试。

- [工具合同实验](tool-contracts/README.md)：形状校验、适配损失、权限与执行器分层；24 项无依赖测试。

- [流式性能实验](streaming-performance/README.md)：调度、增量状态、完成边界与资源寿命；27 项零依赖合同测试。

- [安全边界实验](security-guardrails/README.md)：审批绑定、资源变化、外链与敏感保存策略；57 项原创离线测试。

## 一条命令运行已收录的原创模型

在本目录运行：

```sh
python3 -B run_book_tests.py --skills
```

需要 Python 3.10+ 与 Node.js 20+，不安装依赖，不请求网络，也不需要产品安装包。默认依次检查核心实验室、导航退出、工具合同、流式性能和安全边界；`--skills` 再检查 skills 里的独立副本。重复副本用于保证单独复制后可运行，不算新增算法覆盖。`--list` 可先查看测试组。

模板的 jsdom 测试另有可选开发依赖，真实浏览器绘制另行验收；这两类结果没有混入本命令。

- [原生、语音与坐标实验](native-voice-geometry/README.md)：音频分帧、播放账本、目标身份、显示器/PDF 变换；34 项测试含 360 组矩阵往返。

跨版本的受限解包、快照与差分另见 [自动逆向工具箱](../05-Automated-Reverse-Toolkit/README.md)。

- [恢复与配额实验](resilience-quota/README.md)：分类退避、终止边界、订阅游标与草稿归属；52 项原创模型测试。
