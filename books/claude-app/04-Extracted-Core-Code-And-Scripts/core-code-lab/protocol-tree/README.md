# Protocol and conversation-tree lab

原创教学代码，配套卷四与卷八。没有复制、import、eval 或执行 Claude 的编译模块；没有私有 API、凭据或网络依赖。

## 运行

```sh
node --test test/*.test.mjs
node demo.mjs
```

## 模块

| 文件 | 职责 |
|---|---|
| `incremental-sse.mjs` | UTF-8、SSE 行/帧状态，await 消费者与工作预算 |
| `content-reducer.mjs` | 指定事件子集、块更新、回撤、微任务合并 |
| `legacy-tags.mjs` | `antArtifact` / `antThinking` 数据型增量识别 |
| `branch-manager.mjs` | 单父树索引、可见路径、编辑、重试、兄弟切换 |

## 有意区别

- SSE 模块增加容量上限、NUL-ID 保护及严格数字 retry 检查。目标所见 retry 使用 parseInt。
- reducer 不实现全部事件、citation、审批、协作或语音协议。工具 JSON 只在完整可解析时提升为 parsed_input；目标有更宽松的 partial parser。
- legacy recognizer 是原创状态机。目标兼容路径以正则与文本 helper 为主；本代码不声称与其所有畸形输入行为等价。
- 树在批量插入前做原子校验，并严格拒绝缺失 parent。目标含更多兼容与恢复路径。
- `consumeChunks` 演示客户端读取节奏，不能证明端到端网络或模型背压。
- 不包含目标 prompts、assets、bundle、登录或服务端逻辑。

所有示例内容均为本书自造。24 项测试验证边界、切分、生命周期和结构不变量；没有把示例测试当作目标应用运行验证。
