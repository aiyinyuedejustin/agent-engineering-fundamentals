# 解析层次与证据边界

2026-10-14，Claude Desktop Linux 2.37337.1 选定 classic chat 客户端静态研究。evidence.json 保留短事实及文件定位；并非所有 Claude API/Code/语音路线的统一规范。

## 观察事实

- PT-02–03：行解码器保留未完成字节，识别 CR/LF 并抑制 CR 后的 LF；空行完成帧，多行 data 以换行连接。
- PT-15、17：classic reducer 检查 active block index；tool_use 的 partial JSON 先作为字符串累加。
- PT-19–20：局部工具输入显示解析器能容忍未闭合容器等不完整状态，并做弱缓存；这不是工具执行授权。
- PT-21–22、26：legacy 使用精确 antArtifact 与 antThinking，保留/抑制不完整开头；作品检测可跨相邻文本块。
- PT-23：作品还可来自名为 artifacts 的结构化 tool_use，存在取消结果过滤。legacy 文本不是唯一来源。

## 原创示例合同

parser.mjs 是独立小模型，不复制目标实现：

- SSEDecoder 仅处理 UTF-8 与 SSE framing；只在有 data 字段的空行边界产出帧，注释被忽略，无冒号 data 等价空值，retry 只接受安全整数。严格无效 UTF-8 会报错。这些是本模型明确选择，并不声称与所检 wrapper 的所有容错行为相同。
- EOF 丢弃未闭合的事件；连接是否重试交给上层，不能把 EOF 自动当 message_stop。
- LegacyTags 识别两个精确标签，artifact header 仅支持双引号属性。重复/不支持属性语法报错；引号中的 > 不结束 header。正文是原始字符串，不递归执行嵌套标签。
- 未闭合 artifact 以 closed=false 产出，未闭合 thinking 不出现在可见文字里。调用方决定如何显示中止状态；它不是生产思考策略的完整实现。
- JsonAssembly 只在 finish 时严格解析 JSON object；不提供猜测补全。仍需工具 schema 校验、超时与明确授权。

所有 size limit 都由示例自行选择，不是 Claude 上限；字符预算与 bytes 预算不同。本模型的字符计数为 UTF-16 code unit；配置必须为非负安全整数，建立后不可修改。SSE 的 maxLine 计算单行内容，maxEvent 累计本帧非空行的长度（不含换行分隔符）；JsonAssembly 的 limit 计算累计 JSON 原文。LegacyTags 的 limit 限制单个识别步骤保留的正文与未决片段之和，包括未完成的开/闭标签，非整个 push chunk 或整个输出流；普通已输出文字不累积占额。正文为 limit 长度不保证还能容纳关闭分隔符，应为未决分隔符预留空间。多个小作品同块到达与分块到达保持相同准入结果。预算失败使相应 parser 路径不可继续，不能在捕获错误后补个换行重新产出已拒绝的内容；JSON 的不完整语法错误仍可等待更多片段，预算失败则不可恢复。正常 UI 应以 content block ID 为归属保存缓冲，以 generation 失效旧 flush。停止、retract 或错误之后，清空/保留哪些部分由协议明确规定。

## 必测不变量

对任何合法 fixture，在任意 chunk 分割下，拼合后的输出语义都一致。别要求 text event 的切片数量一样。一次连接的 ID 不可让新会话误接旧事件；schema 不合格的数据不进入执行层；preview 内容保持数据身份。达到 budget 时应停止该解析路径并展示可诊断错误，不应进入无限重试。
