# 崩溃切点图

原创五阶段对照图，配套第17卷和crash-cut-recovery。仅Python标准库，默认在当前目录输出SVG；使用 `python3 build_figure.py --out /tmp/crash-cut-figure` 可指定目录，`--render` 可调用已有Inkscape输出PNG。图中的计数是本模型一次恢复里的操作次数，不是跨崩溃持久总账，也不表示掉电保证。
