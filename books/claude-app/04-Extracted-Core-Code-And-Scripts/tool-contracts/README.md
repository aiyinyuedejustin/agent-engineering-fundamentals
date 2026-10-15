# 工具合同实验与有界静态提取

这是原创教学代码，不是 Claude 的工具实现副本。所有目标软件材料都当作静态文本解析；不导入目标模块，不启动应用，不调用原生程序，不访问私有端点。

## 可以直接运行的原创实验

```sh
node --test test/contract-lab.test.mjs
```

`node example.mjs` 展示一笔成功调用、一笔在 dispatch 前被拒绝的调用，以及适配损失提示；只记录内存中的示例事件。

需要支持 `node:test` 与 `structuredClone` 的 Node.js。实验文件没有第三方运行依赖，共 24 个测试。`contract-lab.mjs` 提供：

- 一个小型严格 schema 子集校验器，覆盖 required、类型、数组长度、数值范围/enum、type-array union、未知字段规则。
- 一个有限的适配损失提示器；它根据此次观察的转换器画像报告值得复核的关键词，不执行目标转换器，不是漏洞判定器。
- 一个原创路由器，把形状校验、语义检查、当前许可和 dispatch 分开。示例 handler 仅用于测试，不执行电脑操作。

重要差异：模型不做隐式类型转换，integer 限于安全整数，批处理在首个动作前预检全部形状，并在每个动作前刷新许可。这些是原创设计选择，不能据此描述目标软件。模型也不承诺批处理原子回滚，不是生产级完整 JSON Schema 实现。


## 对照阅读

[59 项客户端静态定义与合同层次](../../02-Illustrated-Deep-Dive-Book/04-Prompts-And-Protocols/client-tool-contracts.md)解释这些设计选择的来源；[证据表](../evidence/data/client-tool-contracts.json)给出有界字段与短定位。
