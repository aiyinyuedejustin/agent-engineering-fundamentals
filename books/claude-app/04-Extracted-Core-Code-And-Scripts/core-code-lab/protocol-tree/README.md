# Protocol and conversation-tree lab

原创教学代码，配套卷四与卷八。没有复制、import、eval 或执行 Claude 的编译模块；没有私有 API、凭据或网络依赖。

## 运行

```sh
node --test test/*.test.mjs
node demo.mjs
```

41 项模块测试包含原有 24 项与新增 17 项对抗回归。测试只验证本模型，不是目标产品运行验证。

## 模块

| 文件 | 职责 |
|---|---|
| `incremental-sse.mjs` | UTF-8、SSE 行/帧状态，await 消费者与工作预算 |
| `content-reducer.mjs` | 指定事件子集、块更新、回撤、微任务合并 |
| `legacy-tags.mjs` | `antArtifact` / `antThinking` 数据型增量识别 |
| `branch-manager.mjs` | 单父树索引、可见路径、编辑、重试、兄弟切换 |

## 容量与结束合同

- SSE 的 `maxLineCharacters`、`maxEventCharacters` 与标签的 `maxBufferedCharacters` 必须为非负安全整数，构造后只读。计数单位为 UTF-16 code unit，不是 UTF-8 字节。
- SSE 单行预算不含换行；事件预算累计本帧行内容，包括当前未闭合行，不含换行。超额或解码路径出错即终止此 parser，清空未决内容；不能捕获错误后追加换行把被拒绝的数据重新发出。`finish()` 可重复调用并返回空列表，之后不能再 `push()`。
- SSE 的 UTF-8 策略仍是 TextDecoder 默认替换无效字节；配套 streaming-tag-parser skill 的 SSEDecoder 则选择严格报错。两者不是同一容错合同。
- 标签预算约束单次识别步骤保留的正文与未决片段，不约束整个网络 chunk 或已经输出的普通文字。相同内容分块与合块具有相同准入结果。关闭分隔符也占未决容量，因此正文不能独占全部预算。
- 标签预算失败或 `final: true` 后，此实例不可继续输入。未闭合 artifact 以 `closed: false` 产出；thinking 正文不进入可见文本。header 中双引号内的 `>` 不会被当作 header 结尾。
- 内容回撤要求 `from_index` 为非负整数，且映射到现有内容的合法范围；不完整或非数字事件在修改状态前拒绝。该 reducer 仍是有限事件子集，不代替完整 schema 校验。
- `consumeChunks` 在首次读取前、每个 frame 回调前后及 chunk 检查点检查取消。已经运行的回调不回滚；它不能强制中止上游正在进行的 I/O，也不能限制所有网络缓冲。
- `makeWorkBudget` 只在调用方指定的检查点让出事件循环。它不是单个巨大 chunk 的硬实时限额，也不是服务端流控。

## 树的输入与原子性

树在显示过滤之前校验所有输入记录，包含暂不显示的 dangling human；缺失 parent、重复/保留 UUID 和循环都不能藏在未选分支里。旧记录的 `index` 如存在，必须是非负安全整数；缺失 parent 时从已有索引中找最近前项，不逐个扫描数字空洞。

批量插入先克隆全部记录，再校验完整拟议结构，最后更新索引。任何记录无法 structuredClone 或结构校验失败时，已有记录、parent/children 索引和选择状态保持不变。该保证针对公共方法；直接改写公开 Map 不属于受验证的操作。

## 有意区别

- SSE 模块增加容量上限、NUL-ID 保护及严格数字 retry 检查。目标所见 retry 使用 parseInt。
- reducer 不实现全部事件、citation、审批、协作或语音协议。工具 JSON 只在完整可解析时提升为 parsed_input；目标有更宽松的 partial parser。解析结果仍是数据，没有执行器或工具授权。
- legacy recognizer 是原创状态机。header 不是通用 XML parser：核心模型提取双引号属性，不做完整属性语法验证；skill 的 LegacyTags 另外拒绝重复/不支持的属性。目标兼容路径以正则与文本 helper 为主，本代码不声称与其所有畸形输入行为等价。
- 树的完整输入校验、批量克隆原子性和容量失败后终止都是教学模型选择，不能反推目标产品具备这些保护。
- `consumeChunks` 演示客户端读取节奏，不能证明端到端网络或模型背压。
- 不包含目标 prompts、assets、bundle、登录或服务端逻辑。

新增回归覆盖超额后恢复尝试、分块预算不变性、错误回撤、被过滤的循环/孤儿、同 chunk 中取消、克隆失败回滚、稀疏 index、带引号的 delimiter、未选分支编辑/重试、100 棵合成树的路径选择，以及终止 snapshot 和不完整工具 JSON。


[八个异常输入契约与最小反例](ADVERSARIAL.md)
