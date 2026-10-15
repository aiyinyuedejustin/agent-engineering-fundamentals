# 遥测事件字典：完整有界的静态目录

这是一份原创、可复核的事件名称与字段目录。对象是 Claude Desktop Linux 2.37337.1 的指定 JavaScript 目录；不是线上事件量、完整服务端 schema 或公司内部 KPI。

## 直接阅读

- [analytics_payload-01.md](analytics_payload-01.md)
- [analytics_payload-02.md](analytics_payload-02.md)
- [desktop_event-01.md](desktop_event-01.md)
- [health_action-01.md](health_action-01.md)
- [unknown-names-01.md](unknown-names-01.md)

Datadog RUM 的性能 action/timing 路径不属于本字典的有界语法集合，例如 `chat.formatter_wait` 与 `chat.code_stream_render`。formatter 等待、回退与测量边界见 [Vol.11](../../11-Performance-And-Streaming/README.md)。

## 机器可读证据

[index.json](index.json) 保存范围、计数、文件哈希、包装器映射、工具覆盖限制、外部来源和所有分片的 SHA-256。每个分片小于 145,000 字节。读取方按照 parts 中顺序拼接同名表的 rows，再按 columns 解释；不要把字典位置数当作运行次数。

- sources 是被引用文件的身份；完整扫描覆盖 3,782 个文件，全部输入清单的哈希保存在索引。
- name_forms 保存字面量、条件分支、未解析成员和模板片段。
- field_forms 保存键、条件存在性、语法值类型以及可能 undefined 的标记。
- shapes 保存字段形状、`recorded_spread_count` 和动态对象类型。该计数包括已提取字段的条件 spread 与尚未解析的 spread 形式，不等于未知字段集合数；直接字面量对象展开会被内联，不计入此列。dictionary 的 `recorded_spreads` 为相应注记的汇总，所有原始数值和字段标记保持不变。
- sites 保存 UTF-8 起止字节与上述表的关联。包装器调用和负载属性是两种视图，可能指向同一次源码调用，不可相加当事件总量。
- dictionary 保存完整名称组与每组字段并集；unknown_names/partial_names 单独保存未知和部分可解析项目。

本目录没有原始 AST、目标源码、系统提示词、运行时标识符、用户内容或遥测接口地址。Sentry 捕获记录不被命名为产品事件。字段并集不代表必填字段；包装器可能补充、清理或覆盖属性。
