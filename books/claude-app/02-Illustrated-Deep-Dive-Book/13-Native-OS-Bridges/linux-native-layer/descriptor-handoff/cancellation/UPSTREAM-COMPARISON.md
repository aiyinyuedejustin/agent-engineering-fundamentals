# 固定版本对照：库有取消分支，不等于调用接入取消信号

Linux样本的只读数据中有9处`napi-2.16.17`路径线索，例如`0x4046d`的`threadsafe_function.rs`和`0x4440d`的`tokio_runtime.rs`。这让官方`napi@2.16.17`成为有根据的对照对象，但不是二进制与源码逐行绑定的证明。

| 固定版本的公开实现 | 阅读文件任务时应保留的区别 |
|---|---|
| 未提供外部状态时，run新建初值0的共享状态，再克隆给work | 与样本新分配控制块的形状相符；不能据此恢复P的源码类型 |
| execute调用compute；complete以取消status或共享值2抑制Promise结算，最终写1 | 读取取消值的模板可以存在，写入者仍须单独证明 |
| AsyncTask::new保存None；with_signal保存Some | 库提供接入方式，不证明某个导出方法选择了它 |
| 转成JS值时，两支都只返回Promise；Some支另把work与deferred保存在signal内 | 相同的结果接口，可以对应不同的取消能力保留方式 |

前两项见固定版本的[async_work.rs](https://github.com/napi-rs/napi-rs/blob/f2178312d0e3e07beecc19836b91716a229107d3/crates/napi/src/async_work.rs)；后两项见[task.rs](https://github.com/napi-rs/napi-rs/blob/f2178312d0e3e07beecc19836b91716a229107d3/crates/napi/src/bindgen_runtime/js_values/task.rs#L26-L46)及其[JS值转换](https://github.com/napi-rs/napi-rs/blob/f2178312d0e3e07beecc19836b91716a229107d3/crates/napi/src/bindgen_runtime/js_values/task.rs#L139-L155)。公开类型是`Rc<AtomicU8>`，这里不把这个名字直接赋给样本P。

两个公开取消入口的次序也不同：[AsyncWorkPromise::cancel](https://github.com/napi-rs/napi-rs/blob/f2178312d0e3e07beecc19836b91716a229107d3/crates/napi/src/async_work.rs#L38-L42)先写2，再请求Node取消；[AbortSignal的on_abort](https://github.com/napi-rs/napi-rs/blob/f2178312d0e3e07beecc19836b91716a229107d3/crates/napi/src/bindgen_runtime/js_values/task.rs#L116-L135)先排除已完成状态，再请求取消、写2并尝试reject。不能把它们合并成一条未经核实的产品调用链。

**可复用的判断方法是检查能力在哪里保留。** 本样本已证明返回Promise和本地P引用清理；尚未证明文件调用把同一P、work与deferred交给了哪个可达的取消入口。路径版本与结构相符只能支持对照，不能补上该别名边，也不能证明“无取消”或“带成功fd的取消必然可达”。
