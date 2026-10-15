# 音频队列的发布边界：样本写好了，才把门打开

容量算式回答“还有几个槽位”，发布协议回答“这些样本什么时候可以读”。本节沿 Linux 2.37337.1 的所选 producer 与 consumer，依次看索引、溢出、flush 和 turn end。源码短锚点与文件身份集中在[证据表](evidence.json)，REA静态索引来源见[紧凑记录](rea-provenance.json)。

## 1. 两条边界，分别由谁推进

所读 producer 先加载 WR/RD，计算本次能接纳的前缀长度；复制样本，必要时分成尾部和头部两段；最后才用 Atomics.store 发布 WR。consumer 先加载 RD/WR，复制不超过可读边界的样本到输出，再用 Atomics.store 发布 RD。[ARP-01–05、15]

这使 WR 表示“已经完成复制、可以读取的边界”，RD 表示“已经取走、可以重用的边界”。不能先推进 WR 再慢慢补样本，也不能先推进 RD 再读取原位置，否则另一端可能读到未完成数据或覆盖尚未取走的数据。

这里的索引使用原子访问，Float32 样本区是普通访问。ECMAScript 的 synchronizes-with / happens-before 关系解释了为什么发布顺序重要：相同内存范围上的 seq-cst 读若读取对应 seq-cst 写，可建立同步关系，结合各自 agent 顺序连接前后的操作。它不是“用了 Atomics，所有东西就天然安全”。数据区仍需保持不冲突的所有权；是否满足整套协议必须另行论证。[ECMAScript memory model §29.6、29.10–11](https://tc39.es/ecma262/multipage/memory-model.html#sec-synchronizes-with)

在本次读到的活动路径，producer 写 WR，worklet 的 pop 或 drainAll 写 RD。ring 类还提供同时归零两索引的 clear，注释限制为双方都不活跃时使用；所读播放器没有调用它。不能把这个静止态工具当作运行中 interrupt 的捷径。

## 2. 满了之后，尾部不会自动留下来

目标的 ring.push 返回实际写入数，播放器只把这个数加入 totalPushedSamples。若不足输入长度，writeToSink 明确记录 dropped 数量；所读路径没有保留该 Float32 尾部并重试。[ARP-16–18]

所以目标这里采取的是“接纳前缀，丢弃余下样本”，而不是无损背压。上层 pendingChunks 的存在也不能证明已从 pending 取出的这批 PCM 尾部会回队。网络收到、解码完成、成功入 ring、consumer 消费，必须分别记账。

三种数字尤其不能混用：dropped 是本次未接纳数量的告警字段，不是在这里看到的累计播放指标；totalPushedSamples 仅累计成功入队数；played 由 worklet 在实际取出并写入输出后增加，零填充不增加它。所读播放器以 played/sampleRate 换算时长，仍不是扬声器端的声学测量。[ARP-27–28、30]

手算例子：容量5，可用4。初始 RD=WR=0，尝试写入 a,b,c,d,e，只接纳前四个，WR=4。consumer 取走 a,b 后 RD=2。此时再写 f,g，可跨尾部回绕，WR=1，队列顺序为 c,d,f,g。

若原创模型选择无损策略，e 必须由 producer 保留，并在 f,g 之前重试；它与目标这里的丢弃策略不同。两种政策都需要明确，不能把无损重试写成静态样本事实。

## 3. Flush 是消费者丢弃，不是双端一起清零

播放器 stop 设置 interrupted，发送仅含 type 的 flush，并在主线程重置 played 计数。worklet 收到 flush 时读取当时 WR，把 RD 快进到该值，再清理开始播放、缺口和 residual 状态。它不把 WR 归零。[ARP-06–08、20–22]

这个动作丢弃的是“处理 flush 时，已发布到所见 WR 的区间”。它没有给尚未发布的复制、未来网络音频或下一轮建立自动归属。本次读到的 flush 消息没有 generation，worklet 没有发送 flush acknowledgement，drained 也不携带代次；主线程只用 drained 触发完成条件复查。drained 受 drainPosted 门控；主线程仍需检查 ring、待处理数据和解码等条件，不能按通知次数对账 turn。[ARP-14、24]

正常 pop 和 flush 由同一 worklet consumer 端改变 RD，这与让主线程越权改 RD 是不同设计。Web Audio 规范描述渲染线程先处理关联任务队列，再处理 render quantum；这解释消息回调和渲染处理所在的执行模型，但不意味着主线程发出消息时对方已经处理，更不等于端到端代次确认。[Web Audio API §2.6](https://www.w3.org/TR/webaudio-1.1/#rendering-loop)

所读 decoder 回调有 interrupted/decoder实例检查，queueAudio 又可解除 interrupted。它们是局部过滤条件，不能据此声称“任何迟到旧音频都无法进入下一轮”。特别是 flush 尚未被消费、主线程就发布新数据时，新数据是否会被同一次 drain 丢掉，仍需上层调用顺序或更强协议限定。[ARP-25–26]

## 4. Turn end 的 residual 是数量边界，不是代次标签

turn_end 到达 worklet 时，记录当时可读样本数为 residualSamples，清除当前缺口状态。residual 阶段中，每次实际读出样本后扣除该数量，不要求 ring 必须先变空。[ARP-09–13]

例如边界处还剩3个旧样本，接着又入队4个新样本。一次取4个后 residual 变成−1：这个 quantum 横跨了旧尾部与后续样本。实现会结束 residual 阶段、尝试一次 drained 通知，并在整个 quantum 都有数据时重新开启缺口判断。若恰好读完3个，residual=0，同样结束 residual 阶段；residual 恰为零时不会设置 hasStarted 或重新开启 gapReady；后续普通消费路径才重新建立这两个状态。它不把之后的所有音频长期归为旧尾部。

这是按 FIFO 位置记账的边界技巧，不是每个样本携带 turn ID。快照取的是“收到控制消息时的已发布数量”，不是服务端宣告结束那一刻的精确总数。signalTurnEnd 释放 prebuffer 后发送控制消息；本次未由这两个文件证明所有异步解码输出已经先于边界发布，也未证明下一轮绝不会先发布。因而不能把 residual 称为完整的代次隔离协议。


## 5. 实现时需要写进接口的四条合同

| 边界 | 要明确的接口含义 | 一个容易写错的替代物 |
|---|---|---|
| 发布与回收 | 复制完成才发布WR；读取完成才释放RD | 先更新索引，再处理样本 |
| 容量不足 | 返回accepted，并明示尾部丢弃还是保留 | 把received直接累加成played |
| 丢弃当前轮 | 定义谁消费flush、何时允许新轮发布 | 双方随时把两个索引归零 |
| 自然完成 | 定义尾部与异步解码完成边界、回执归属 | 把任何一次drained当作当前turn成功 |

其中，携带代次的flush/ack与单调accepted边界是自建系统可选择的更强合同；本节两文件的静态观察并未建立这类端到端保证。一次原子整数更新只保证那一次访问的性质，多步状态转换仍需自己的协议。

配套[原创确定性交错实验](../../../04-Extracted-Core-Code-And-Scripts/audio-ring-lab/README.md)把copy/publish、copyOut/release、flush/ack与自然end分成显式步骤，可逐步运行，也可运行专门的错误排序反例。实验采用保留尾部政策，与上文所读目标路径的丢弃政策不同。

[返回第15卷](../README.md#72-一个槽为什么不能用)
