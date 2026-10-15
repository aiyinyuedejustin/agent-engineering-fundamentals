# 条件写入与流式工作粒度

两组原创实验，各自补全一种容易被本地正确性掩盖的边界。

- [两边都保存成功，为什么仍会丢失修改？](../../../02-Illustrated-Deep-Dive-Book/09-Memory-Projects-And-Styles/authoritative-writes.md)：权威版本条件、重基意图与历史幂等回执，14项测试。
- [小事件不等于小工作](../../../02-Illustrated-Deep-Dive-Book/11-Performance-And-Streaming/chunk-work-quantum.md)：复用已有SSE decoder的字节片/帧数检查点，2项原实现probe及11项适配器测试。

从本目录执行，Node.js 20+，无安装步骤：

```sh
node --test *.test.mjs
node demo.mjs
node burst-probe.mjs
node sliced-demo.mjs
```

依赖书内 `../../core-code-lab/` 的原创队列与parser，复制时需保留书内结构。模型不连接产品、网络或数据库。流式适配器借用当前chunk字节，调用者在处理完成前不得改写；取消只在外部等待结束后的检查点观察；错误后的已交付前缀不具备整批原子性。详细合同见对应小节。

另含16项独立合成合同复核，总计43项。边界反例按真实行为断言：借用字节被改写会改变后续输入；pending外部Promise不会被signal抢占；超限时已交付前缀可随分片不同。通过这些反例不代表模型提供了更强的快照、强制取消或批次原子保证。
