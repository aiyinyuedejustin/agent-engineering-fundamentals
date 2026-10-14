# 核心实现与研究工具

这里放命名清楚、能独立阅读和运行的工程化实现，以及将结论连接到输入的工具。算法示例采用原创重写；完整安装包、商业字体和混淆产物不放进代码库。

## 可直接运行

- [精选证据校验](scripts/verify_evidence.py)：核对源文件身份与声明定位。
- [三平台 UI 对照](scripts/compare_ui_trees.py)：从三份解包目录重新生成清单与差异，不依赖缓存计数。
- [色卡与组件图生成](scripts/make_anatomy_figures.py) · [表面图生成](scripts/make_study_figures.py)：从设计数据重建原创 SVG。
- [基础交互测试](tests/demo-state/README.md) · [密度、阅读与 Quick Entry 测试](tests/phase2-components/README.md)：可复现的状态与静态检查。

## 证据与数据

[方法附录](evidence/README.md) · [来源索引](evidence/sources.md) · [设计参数](evidence/data/design-token-summary.json) · [跨平台对照](evidence/data/platform-comparison.json)

算法模块随对应章节提供。书中的“实现示例”与产品中的“实现事实”通过标题和引用分别标明，便于直接改写而不混淆归属。
