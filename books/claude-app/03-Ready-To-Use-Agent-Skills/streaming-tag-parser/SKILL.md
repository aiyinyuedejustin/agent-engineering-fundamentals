---
name: streaming-tag-parser
description: Implement or review incremental SSE framing, streamed JSON assembly, and legacy artifact-tag recognition with chunk-boundary tests. Use for chat content parsers; keep parsing separate from rendering, tool execution, and authorization.
---

# 流式分帧与标签解析

## When to use

用于标签被分成两段而闪现、UTF-8 字符损坏、半个 JSON 被当成完整工具参数、思考区域泄露到可见正文，或需要把 SSE/内容块/作品对象分层实现的任务。若上游已有结构化内容块，优先消费它，不要重新把整个对话串接后用 HTML regex 猜含义。

## Workflow

1. 写清协议层次：bytes → UTF-8 → SSE 行/帧 → JSON 事件 → typed content reducer → 可见内容/作品。网络 chunk 不等于事件、token 或一次屏幕更新。
2. 阅读 [解析合同](references/parser-contract.md)。确认目标 surface 和协议版本；同名 input_json_delta 在不同产品路径里未必具有相同累加语义。
3. 只在传输层处理 CR、LF、CRLF、空行与多行 data；保留 TextDecoder 的跨块状态。不要对每个网络 chunk 单独 `JSON.parse`。
4. 对结构化工具输入只累加原始片段。显示可以有容错预览，但执行必须等待明确闭合、完整 JSON、工具专用 schema 和独立授权。不要修补一个猜测参数后立即调用工具。
5. 如果必须兼容 legacy，使用精确大小写 antArtifact / antThinking；保留可能构成开标签的尾部；把不完整状态显式标记。参考 [原创解析器](assets/parser.mjs)，它输出数据，不产生 DOM。
6. 给单行、事件、头部、正文与累计 JSON 配置有界预算，校验有限非负安全整数。以保留状态计数，不把网络 chunk 大小当作内容预算；预算失败后终止该解析路径。取消与换 generation 后丢弃旧缓冲；未知事件保留诊断或按明确策略忽略，不能变成可执行内容。
7. 运行 `node assets/parser.test.mjs`，包含每个 UTF-8 byte split、每个 tag character split、CRLF、引号内的 >、缺尾标签、过额与不完整 JSON。测试实际 reducer 时增加 index 不匹配、retraction 和旧 microtask 回写。

## Anti-Patterns

- `chunk.split('\n\n')` 作为唯一 SSE parser；对每个 chunk 使用新的 TextDecoder。
- 对整个增量串反复做一个贪婪 regex；忘记 opener 也能跨消息块。
- 用 innerHTML 呈现解析结果，或把标签名里的 system/thinking 当成真实消息角色与权限。
- 把无结尾的 artifact 标成 complete；把容错 JSON parse 当成执行许可。
- 静默丢失所有 parser 错误，或者对未知 payload 继续按成功处理。
- 将局部 awaited consumer/backpressure 写成端到端网络内存有界的保证。

## Code seed

下面是集成骨架，导入路径相对于本技能目录；chunks、validateEvent 与 applyEvent 由调用方提供。

```js
import { SSEDecoder } from './assets/parser.mjs';

const sse = new SSEDecoder();
for await (const bytes of chunks) {
  for (const frame of sse.push(bytes)) {
    const event = JSON.parse(frame.data);
    validateEvent(event);       // 应用自己的事件 schema
    await applyEvent(event);    // 渲染节奏与传输解码分离
  }
}
sse.finish(); // 不把未结束帧补成成功事件
```

模型不实现重连、完整产品事件集、XML、HTML sanitization 或安全执行沙箱；这些仍是独立合同。
