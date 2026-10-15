# 核心实现与研究工具

这里放命名清楚、能独立阅读和运行的工程化实现，以及将结论连接到输入的工具。算法示例采用原创重写；完整安装包、商业字体和混淆产物不放进代码库。

按章节找实现，先读[19 卷代码与测试导航](book-code-navigation.md)：逐卷连接学习说明、原创代码和测试，并区分离线模型、需要样本的复算与尚待执行的原生验证。

## 随仓即可运行

- [原创机制实验室](core-code-lab/README.md)：流式协议、对话树、执行循环、预览状态、记忆与配置；本实验室 155 项离线测试，不含下列新增专题。
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

- [导航与退出实验](shell-lifecycle/README.md)：导航代际、晚到回调、具名清理与落盘结算；12 项离线测试。

- [工具合同实验](tool-contracts/README.md)：形状校验、适配损失、权限与执行器分层；24 项无依赖测试。

- [流式性能实验](streaming-performance/README.md)：调度、增量状态、完成边界与资源寿命；46 项零依赖合同测试。

- [安全边界实验](security-guardrails/README.md)：审批绑定、资源变化、外链与敏感保存策略；68 项原创离线测试。

## 一条命令运行已收录的原创模型

在本目录运行：

```sh
python3 -B run_book_tests.py --skills
```

运行完整集合需要 Python 3.10+ 与 Node.js 22+（本轮验证使用 Node.js 24.19.0），不安装依赖，不请求网络，也不需要产品安装包。默认依次检查核心实验室、预览超时双账本、状态转移案例、异步阅读准备、导航退出、工具合同、流式性能、安全边界、原生/语音/坐标、恢复/配额、工程案例和遥测指标；`--skills` 再检查 skills 里的独立副本。重复副本用于保证单独复制后可运行，不算新增算法覆盖。`--list` 可先查看测试组。

前端检查另有独立口径：交互工作台为 46+32 项模拟 DOM、6+10 项静态检查及 6 项滚动容器回归，共 100 项检查；六套 HTML 模板为 80 项基础、25 项边界、8 项预览生命周期、8 项文档导航、31 项当前章节、19项键盘焦点与32项预览输入检查，共 203 项静态/模拟 DOM 检查。它们使用可选开发依赖，均未混入本命令，也不代表浏览器绘制、真实中文输入法或辅助技术验收。浏览器记录须同时注明对应提交、视口和实际覆盖场景。

- [原生、语音与坐标实验](native-voice-geometry/README.md)：音频分帧、播放账本、目标身份、显示器/PDF 变换；81 项测试含 360 组矩阵往返。
- [音频ring发布与跨代握手](audio-ring-lab/README.md)：分开复制、发布、释放，演练保尾FIFO、flush确认和自然end边界；21项测试。

跨版本的受限解包、快照与差分另见 [自动逆向工具箱](../05-Automated-Reverse-Toolkit/README.md)。

- [恢复与配额实验](resilience-quota/README.md)：分类退避、终止边界、订阅游标与草稿归属；64 项原创模型测试。

- [三个可手算的工程案例](worked-cases/README.md)：Stop/restart、UTF-8 预留与 MCP 审批绑定；17 项 Python 与 12 项 Node 测试。
- [两个状态转移案例](worked-cases/state-transitions/README.md)：对话树身份重命名、顺序保存与组织切换；20 项测试与 2 份确定性演示输出。

- [原创模型的七条边界合同](model-boundaries.md)：取消重入、数值溢出、审批序列化与原子输入验证。

- [三个异步边界实验](async-reading-primer/README.md)：19 项确定性测试与逐步预测题。
- [遥测指标实验](../02-Illustrated-Deep-Dive-Book/12-Telemetry-And-Product-Metrics/metrics-lab/README.md)：74 项测试，从合成事件重算指标、隔离时间矛盾并保留筛选前分母。

- [出版物完整性检查器](scripts/publication-checks/README.md)：只读检查必需目录、阅读链接与四份已登记清单；53 项合成测试，输出结构化报告。

- [条件写入与流式工作粒度](worked-cases/concurrency-and-streaming/README.md)：27项实现测试与16项独立合同复核，覆盖旧快照覆盖、重基、历史回执，以及大输入块的分片检查点。

- [逻辑崩溃与恢复实验](crash-cut-recovery/README.md)：35个测试方法，在自有临时目录与子进程中检查write、rename、commit之间的恢复合同；不等同掉电耐久性。

- [原生回调生命周期](../02-Illustrated-Deep-Dive-Book/13-Native-OS-Bridges/linux-native-layer/README.md)：34项原创模型测试覆盖有限队列、迟到回调、调度失败与错误报告器异常；已纳入统一测试入口。

- [资源交付与回收实验](resource-handoff-lab/README.md)：显式claim转移、迟到资源、清理重入与结果未知；85项原创合成测试，已纳入统一入口，不操作真实文件描述符。
