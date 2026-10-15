# Deadline、取消确认与双资源账本

原创、离线、确定性实验。直接复用本书 `workspace-core/workspaces-model.mjs` 中的 `ContentEpoch` 和 `withDeadline`，不复制其实现；没有第三方依赖。

## 运行

先进入本 README 所在目录。要求 Node.js 22+，本次使用 24.19.0。

```sh
node demo.mjs
node --test sandbox_timeout.test.mjs
```

从出版物其他目录调用这些文件也可以。定位器从代码位置向上寻找出版物；单独搬移实验时，设置 `BOOK_PUBLICATION` 为原出版物根目录。错误路径会明确报错，不会静默加载别的实现。

## 文件

- `sandbox_timeout.mjs`：216 行事件适配器、幂等 lease 与 16 个时刻的 worked timeline
- `existing-models.mjs`：只加载本书现有原创模型，不查找产品安装目录
- `sandbox_timeout.test.mjs`：24 项测试，含 120 种终态事件排列
- `demo.mjs`：输出固定事件序列
- `expected-output.json`：与正文时间线对应的固定输出，测试做完整深比较

正文见第 7 卷的 `worked-case.md`；其中解释了两个账本、取消确认合同、晚到结果及模型边界。

## 最重要的预期

1. deadline 结算 RPC，RPC 等待槽释放；底层工作可能继续占工作槽。
2. `received` 只确认取消请求已收到；只有可信的 `stopped` 或实际完成才释放工作 lease。
3. 候选结果在实际交付时还要检查响应终态、通道、内容收据与 deadline。
4. 重复完成、重复取消和重复清理，不能使任何 lease 释放两次。
5. 新通道不能因为 epoch 数字或正文恰好相同而继承旧通道的确认。

本例不执行 HTML/React，不建立 RPC 或 MessagePort，不读取真实文件，不联网，不验证 Claude 运行行为或浏览器隔离。手动注入的工作终态只是测试夹具提供的事实，不能替代真实执行器的资源回收确认。`TIMEOUT`、`received`、`stopped` 和双资源槽均为教学设计，不是声称已恢复的产品协议。

操作历史和候选结果为方便教学保留在内存中；执行槽有界不等于总内存有界。生产集成还需要独立的历史、缓冲区、流量、身份、资源授权与强制终止策略。
