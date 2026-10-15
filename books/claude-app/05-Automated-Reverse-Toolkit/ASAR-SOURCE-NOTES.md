# ASAR 格式来源与设计依据

核对日期：2026-10-15 UTC。Python 适配器和合成测试均为原创；交付中没有复制 Electron、REA 或目标产品的实现代码。下列指向 `main` 的链接会随上游变化，不代表固定版本断言。

## Electron 一手格式资料

- [ASAR 格式与去重说明](https://github.com/electron/asar#format)：以 JSON 建索引的无压缩容器；偏移相对头部之后的数据区，内容相同的文件可以共享数据字节。
- [Pickle 实现](https://github.com/electron/asar/blob/main/src/pickle.ts)：小端 payload 长度、有符号字符串长度和四字节对齐。本适配器只接受该写入器生成的规范封装，不接受任意自定义 Pickle 头。
- [磁盘读写实现](https://github.com/electron/asar/blob/main/src/disk.ts)：长度与头部封装、数据绝对偏移的计算，以及 `.unpacked` 外置配套内容的处理。
- [文件系统表示](https://github.com/electron/asar/blob/main/src/filesystem.ts)：目录、文件、链接和共享偏移条目的表示。适配器据此区分精确共享范围与部分重叠。
- [完整性实现](https://github.com/electron/asar/blob/main/src/integrity.ts)：SHA256 整文件与分块元数据，包括空文件的哈希块。另只读查看了本地已安装的 `@electron/asar` 4.2.0 源码，交叉核对表示方式；本轮没有安装或执行它。

## 既有 REA 参考

只读审阅本地 REA 提交 `569ef4159db73931717825302b323fae7aa91bbf`：

- [AsarHeader.ts](https://github.com/morluto/rea/blob/569ef4159db73931717825302b323fae7aa91bbf/src/artifacts/AsarHeader.ts)：在交给上游解码前检查长度，限制头部分配量。
- [AsarListing.ts](https://github.com/morluto/rea/blob/569ef4159db73931717825302b323fae7aa91bbf/src/artifacts/AsarListing.ts)：分别约束逻辑清单规模与容器字节量。
- [AsarArtifactReader.ts](https://github.com/morluto/rea/blob/569ef4159db73931717825302b323fae7aa91bbf/src/artifacts/AsarArtifactReader.ts)：保留声明身份、外置状态和局限。REA 更丰富的配套目录流程没有移植到本标准库适配器。

## 原子不替换交付依据

- [Linux rename(2)](https://www.man7.org/linux/man-pages/man2/rename.2.html)：普通 rename 可以替换已有空目录；`RENAME_NOREPLACE` 拒绝已有目标，并要求文件系统支持。
- [Apple 导出的 rename 声明和标志](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/stdio.h)：`renamex_np` 和 `RENAME_EXCL`。
- [Python os.rename](https://docs.python.org/3/library/os.html#os.rename)：Windows 拒绝已有目标，Unix 语义不同。

当前 ASAR 提取、两版本运行目录和报告目录使用这套交付操作；独立 ZIP 提取仍使用原有实现，详见 [支持约定](SUPPORT.md)。只有 Linux 路径实际执行过，原生 macOS/Windows 行为尚未验证。

这是理解格式、限制资源并经过合成回归测试的原型，不是专业安全认证。真实包完整提取仍受外置内容等限制，进入新的使用场景前需要单独审查。
