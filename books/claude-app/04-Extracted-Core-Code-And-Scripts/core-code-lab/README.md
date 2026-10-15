# 原创核心机制代码实验室

这里把研究中重新编写的教学模型与分析工具放在同一入口。目录名中的 “Extracted” 指研究主题的提炼；本目录代码是原创实现，不是提取或反编译的产品源码，不是官方 SDK，也不保证与产品协议兼容。原模块的中文说明与注释保留，模块之间没有隐式依赖。

## 先运行，不需要产品文件

环境：Node.js 20+、Python 3.10+。下面的命令均从本目录运行；核心测试无需安装 npm 或 pip 依赖，不联网。Windows 可用 `python` 替换 `python3`。

```sh
python3 -B verify_manifest.py
python3 -B run_tests.py
python3 -B run_tests.py --demos
```

第一个命令核验交付文件和 SHA-256。第二个运行五个模块的全部无产品依赖测试。第三个先测试，再运行四个合成数据演示。测试失败会返回非零退出状态；不会把可选、未运行的检查算作通过。可以从任意工作目录调用这两个脚本的绝对路径。

## 两类内容，输入要求不同

| 模块 | 类型 | 观察重点 | 是否另需样本 |
|---|---|---|---|
| [protocol-tree](protocol-tree/README.md) | 离线教学示例 | 增量 UTF-8 / SSE、内容归约、兼容标签、对话分支 | 否，演示数据原创 |
| [loop-cowork](loop-cowork/README.md) | 离线教学示例 | 会话 generation、审批一次消费、逐动作授权、坐标与执行边界 | 否，只模拟内存状态 |
| [workspace-core](workspace-core/README.md) | 离线教学示例 | artifact 版本选择、内容 epoch、窗口消息入口、工作区显示状态 | 否，不执行 HTML |
| [memory-flags](memory-flags/README.md) | 离线教学示例 | 同作用域串行修改、乐观回滚、过期请求、能力依赖与访问快照 | 否，无真实存储和服务 |
| [color-tools](color-tools/README.md) | 可移植分析工具 | CSS 声明提取、SHA-256 与字节锚点、显式配置颜色解析 | 实际提取需要；单元测试不需要 |

### 分别运行

```sh
# 以下命令仍在实验室根目录执行。
node --test protocol-tree/test/*.test.mjs
node protocol-tree/demo.mjs
python3 -B -m unittest discover -s loop-cowork -p 'test_*.py' -v
python3 -B loop-cowork/model.py
node --test workspace-core/workspaces-model.test.mjs
node workspace-core/demo.mjs
node --test memory-flags/memory-flags-model.test.mjs
node memory-flags/demo.mjs
python3 -B -m unittest discover -s color-tools/tests -p 'test_*.py' -v
```

`run_tests.py` 自行展开测试文件名，无需 shell 的通配符支持。它设置 `PYTHONDONTWRITEBYTECODE=1`，避免把 Python 缓存写入交付目录。

## 需要自行提供样本的工作

`color-tools/extract_design_tokens.py` 与 `build_color_catalog.py` 要求你有权读取的本地、已解包 CSS 和对应目录结构。它们不下载或解包产品，不执行产品 JavaScript；原始清单可能包含非颜色声明，应作为私有中间文件处理。实际 CLI 参数、输入命名空间、输出覆盖行为及已知解析边界，见 [color-tools/README.md](color-tools/README.md)。

可选检查没有纳入默认测试：

- `color-tools/tests/verify_baseline.py`：另需本地产品样本、原清单与原颜色目录，验证指定历史版本的完整事实一致性。
- `color-tools/tests/test_browser_dom.cjs`：另需生成的离线 HTML 与 `jsdom`；在允许安装依赖的工作副本运行。模拟 DOM 不能替代真实浏览器视觉测试。

色表 README 中 1,341 条记录、23 条未求值表达式等，是此前特定样本的基线记录；默认测试只检验原创合成输入，不重现或重新证明这些产品数量。

## 如何阅读与扩展

先运行 demo，再读同模块的模型和测试。测试中的正常、重复、取消、失败和过期路径比正常演示更接近设计要点。模型中的保守拒绝、容量限制、超时和简化状态机，有些是作者的教学选择或防御建议；不能反向当作产品实现证据。

这些示例不是生产安全边界。它们不覆盖真实身份认证、跨进程授权、网络重试、持久化、全部协议事件或跨设备竞态。测试通过说明本实验室的局部不变量成立，不证明目标产品的真实运行、安全性或当前托管版本行为。

## 交付与完整性

`manifest.json` 列出每个交付文件的相对路径、字节数、SHA-256 和来源类别。原样复制文件可与源哈希直接核对；模块 README 的命令路径经过可移植性调整，新增入口、脚本和演示标记为原创整合。清单本身不递归列入哈希。

本目录不附安装包、bundle、原始 CSS、产品字体、私有证据、原始提取清单、生成结果、测试日志、`node_modules` 或 Python 缓存。不要把自行取得的样本或生成产物放回交付目录。完整性核验会报告新增或缺失文件；依赖安装和本地改写应在工作副本中完成。Python 命令使用 -B 避免导入产生 __pycache__；已有缓存不会被 -B 删除。发布前应在仅含拟发布文件的干净检出或导出快照中核验，不将本地缓存加入清单，也不忽略其他未知文件。
