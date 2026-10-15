# 三个可手算的工程案例

原创、离线、确定性的补充实验。需要 Node.js 20+ 和 Python 3.10+；不需要安装依赖，不联网、不读取真实文件内容、不启动产品进程、不运行 MCP 服务。

## 三个入口

| 文件 | 解释的场景 | 复用的现有实验 |
|---|---|---|
| `loop_timeline.py` | Stop、重启、晚到初始化/结果、过期审批 | `core-code-lab/loop-cowork/model.py` 的 Session 与 ApprovalDesk |
| `context_budget.mjs` | UTF-8 字节预留、对称释放、草稿代次 | 概念连接到 ContentEpoch 与前端 generation；实现独立 |
| `mcp_binding.py` | 同名服务换配置或重连后，审批绑定是否仍成立 | 同一个 ApprovalDesk；没有重新实现审批表 |

Python 入口寻找出版物根目录并直接加载其中的原创实验代码。可以从出版物任意子目录调用，也可显式设置 `BOOK_PUBLICATION` 为包含 `04-Extracted-Core-Code-And-Scripts` 的目录。只读取书中自己的 `.py`，不寻找产品安装目录。

## 从本目录运行

```sh
python3 -B loop_timeline.py
node context_budget.mjs
python3 -B mcp_binding.py
python3 -B -m unittest -v test_worked_cases.py
node --test context_budget*.test.mjs
```

两个测试入口分别为 17 个 Python 测试（6 个回合组合案例、11 个 MCP 绑定案例）和 12 个 Node 测试。测试数仅属于这三个新增案例，不应与产品验证、前端工作台或六套 HTML 模板的测试合并表述。

## 模型边界

- Python 复用的审批摘要规则对参数变化一律保守拒绝；不是所有产品工具的真实策略。
- MCP 示例的 Binding 由可信宿主提供，只演示应该绑定什么；它不是服务认证、协议实现、签名方案或操作系统沙箱。
- `decide_and_record` 只写内存日志，检查与记录同步完成；没有解决真实跨进程执行的原子性。
- 字节预算只处理已经得到的确定文本、单 JavaScript realm、单份草稿；没有编码估计、Blob 存储、上传、tokenizer 或共享跨标签页额度。
- 草稿 owner 失效释放 pending 预留，但保留旧草稿已完成数据。真实发送队列的持有与页面卸载需要更细的所有权模型。
- `InlineBudget.remove()` 只演示记账移除；完整 UI 还需在同一事务中移除附件记录与其卡片。它不删除服务器文件。
- 重放晚到事件是确定性单元测试，不是目标产品的竞态实测。

第一、三例的运行输出可以和图中逐行核对。第二例刻意使用 12 字节预算，方便手算，不表示任何产品额度。

## 身份与状态转移

[乐观节点换身份、设置队列与过期 allow](state-transitions/README.md)：20 项测试、两条确定性轨迹与完整前后状态。

- [预览超时与双资源账本](sandbox-timeout/README.md)：24 项测试，分别观察响应等待和实际工作；此组测试需要 Node.js 22+ 的内置虚拟定时器接口。
