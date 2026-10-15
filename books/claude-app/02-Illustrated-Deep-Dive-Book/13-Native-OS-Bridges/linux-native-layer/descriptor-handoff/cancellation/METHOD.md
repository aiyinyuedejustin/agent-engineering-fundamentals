# 收集与复核范围

## 输入与工具

样本为Claude Desktop 2.37337.1的Linux amd64模块，SHA-256 `c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6`，10,026,272字节。日期：2026-10-15 UTC。

- 输入只读自Linux资源目录的`@ant/claude-native/claude-native-binding.node`，读取前检查普通文件和精确大小，读取后检查固定SHA-256
- 工具：已安装GNU readelf / objdump 2.44；Python标准库用于输出解析、稳定快照及原创检查
- 使用已安装REA 6.5.0的`inspect-with-objdump … file_headers --json`，底层固定`/usr/bin/objdump`，仅执行`objdump -f`
- REA Evidence ID：`ev_89d9b1ba51b34b3ecba5f51125ca0a02ad471d66849c08d41d83e5b42b1456ea`
- REA报告退出0、完整输出、前后SHA-256相同。REA自身provider version仍为unknown；2.44来自另行读取现有工具版本，二者不混写
- REA没有提供本任务所需的规范化别名分析；精确地址窗口和手工P指针追踪使用同一现有objdump/readelf完成

没有安装新软件、执行或加载目标、动态调试、故障注入、联网调用私有API、读取Mac或Windows原生件。

## 复核命令

```sh
python3 -B test-verifier.py
python3 -B verify-static.py /absolute/path/to/verified-linux.node
```

## 静态检查的合同

`verify-static.py`：末端nofollow/nonblock打开输入，拒绝非普通文件、错误大小及错误摘要。通过后才建立独占临时目录及稳定快照。现有readelf/objdump仅读取该快照；禁用debuginfod URL；输出JSON只到stdout；成功或异常退出均由TemporaryDirectory清理自身目录。

133项选定检查覆盖11个完整FDE、稀疏地址锚点、命名导入、相对重定位、execute不直接访问P槽、计数helper不含字节操作以及快照保持不变。它们不自动证明完整控制流、全局别名、所有异常路径或实际宿主调度。

15项fixture完全使用合成字节，不需要产品样本。覆盖正常读取、错误大小、错误摘要、symlink、directory、FIFO、missing file、工具失败清理、锚点失败清理，以及opcode/数值/地址左边界/寄存器后缀匹配边界、重定位类型和指令地址解析。尤其避免`0x2`错误匹配`0x20`。这些fixture不会替代真实样本检查。

## 未覆盖

- 未遍历全部间接表调用者，尚未给0x778620建立文件P别名
- 未反推完整宿主实现、Node版本或实际取消时序
- 未证明全生命周期fd归属，不判断泄漏、漏洞或全局安全
- 全模块语法搜索只用于找候选，不用于证明“没有写入者”或“不可达”
