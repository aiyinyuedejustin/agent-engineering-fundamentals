# 原创定位附录：文件包含性路线

## 样本与方法

- 样本：Claude Desktop 2.37337.1，Linux amd64 的原生模块。
- 大小：10,026,272 字节。
- SHA-256：`c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6`。
- 解析前、复核后摘要一致；没有加载、执行目标或读取 macOS/Windows 失败样本。
- 地址均为 ELF linked VA，不是 ASLR 后地址。字符串所在只读 LOAD 的文件偏移与 VA 相同；代码则不可直接把 VA 当文件偏移。
- GNU readelf 读取重定位与 `.eh_frame` FDE；GNU objdump 从 FDE 起点解码。正文选定 14 个窗口均无 `(bad)` 或 `.byte` 截断标记。这不是对全部字节的反汇编正确性认证。
- 既有 REA 6.5.0 file_headers 结果可作为同摘要格式背景；本轮定位使用 GNU 工具，不声称新增第二套独立解码结果。

`verify-static.py` 先以 nofollow 普通文件读取获得已核对摘要的字节，再把它们复制到自行创建的私有临时目录，工具只对这个稳定快照取得选定窗口与 relocation，执行 123 项断言。JSON 仅输出到 stdout，没有任意文件输出参数。它不以已有反汇编文本作为唯一验证输入，也不自动证明完整控制流；分支串联与范围限制由人工审读。

## NFC-01：名字、callback、异步工作参数

### openBeneath

- 名字：0x3f04d，长度 11。
- 构造器 FDE 0x6313d0..0x6314b1：0x6313e1 取名字；0x6313e8 指定 callback=0x62d560；0x6313fd 经 GOT 0x98d640 调用 `napi_create_function`。
- callback FDE 0x62d560..0x62d806：0x62d7d3 直接调用异步工厂 0x61c8f0。
- 工厂 FDE 0x61c8f0..0x61d12d：0x61cd99 将 execute=0x619e80 传入 rcx；0x61cda0 将 complete=0x61b230 传入 r8；0x61cdad 调用 `napi_create_async_work`（GOT 0x98d7e8）；创建成功分支 0x61ce01 调用 queue（GOT 0x98d7f0）。
- execute FDE 0x619e80..0x619f10：0x619e88 读任务+0x18 为 esi；+0x8/+0x10 成为分量集合指针/数量，+0x1c/+0x20 成为 r8d/r9d；0x619ea0 直接调用 0x4f3bc0。

### openRootDir

- 名字：0x3d84d，长度 11。
- 构造器 FDE 0x6316a0..0x631781：0x6316b1 取名字；0x6316b8 指定 callback=0x62ecd0；0x6316cd 调用 `napi_create_function`。
- callback FDE 0x62ecd0..0x62f4d8：0x62f151/0x62f158 分别指定 execute=0x619f10、complete=0x61b4d0；0x62f165 调用 create_async_work；成功分支 0x62f1b0 调用 queue。
- execute FDE 0x619f10..0x619f96：0x619f25 直接调用 0x4f4670。

这里证明了注册构造器和任务实参关联，不把“传入 execute 指针”画成已发生的运行时直接调用，不声称恢复了整个模块注册与调度实现。

## NFC-02：根目录打开

FDE 0x4f4670..0x4f47ea：

- 0x4f4700：flags=0x2b0000。
- 0x4f4707：调用 GOT 0x98d300，GLOB_DAT 指向 `open`。
- 0x4f470d/0x4f470f：测试返回值，负数跳 0x4f473c 的 errno 处理。
- 0x4f4711/0x4f4715：成功 fd 写结果+8；结果首字段写 -1。

不把 -1 结果标记与 syscall 失败返回 -1 混淆：二者处于不同层级、不同字段。根路径不是在这个函数里逐分量执行 openat。

## NFC-03：分量拒绝

验证器 FDE 0x62d330..0x62d557：

- 0x62d354..0x62d357：长度零进入拒绝段 0x62d433。
- 长度一：0x62d37e 比较字节 0x2e；相等经 0x62d383 进入拒绝段。
- 长度二：0x62d388 比较 0x2e2e；0x62d38d 相等进入拒绝段。
- 0x62d525..0x62d52a：逐字节读取，零字节进入拒绝段。
- 0x62d530..0x62d533：斜杠 0x2f 进入同一拒绝段。
- 0x62d541：通过路线写 -1 标记。
- 0x62d50b..0x62d511 还有计数与 255 的比较；不把该计数未经证明写成字节长度。

首选函数 0x4f3bc0 中 0x4f3c0d 调用验证器；循环步长 24。0x4f3c2a 取 `/` 分隔符 0x57005，0x4f3c42 调用组合处理。逐段 fallback 的首、中、末检查点分别为 0x4f3510、0x4f3970、0x4f35ab。

## NFC-04：openat2 参数与选择性 fallback

FDE 0x4f3bc0..0x4f3f2b：

- 0x4f3be1 保存输入 esi（dirfd）到栈+0xc。
- 0x4f3c54..0x4f3c73：输入 flags OR 0xa0800，扩展后写栈+0x90；通过位移和掩码按 flags 的 bit 6 选择 mode，写栈+0x98。
- 0x4f3c7b：栈+0xa0 写 0xe。连续三项对应 `open_how` 的 flags/mode/resolve。
- 0x4f3d4b..0x4f3d67：`syscall(0x1b5, dirfd, path, &how, 0x18)`；此处是 libc `syscall` 的 C ABI：edi=437、esi=dirfd、rdx=path、rcx=&how、r8d=24，不是直接内核 syscall 指令的寄存器布局；GOT 0x98c830 的 GLOB_DAT 为 `syscall`。
- 0x4f3d70：负返回值跳 0x4f3d97。非负路线最终在 0x4f3e64/0x4f3e67 写 fd 和成功标记。
- 0x4f3d9c：调用 `__errno_location`（GOT 0x98c7a0），随后取 32 位 errno。
- 0x4f3dde 将 ebp 清零；0x4f3de0/0x4f3de5 比较 11/38；相等分别经 0x4f3de3/0x4f3de8 跳 0x4f3e29。清理后 0x4f3e5e 跳 0x4f3e7c，并在 0x4f3ea6 调用 fallback=0x4f34b0。
- 其他 errno 在 0x4f3e03 调用错误构造器 0x632350；传入必要锚点 `openat2`（0x56fcc，7 字节）。它构造带非 -1 首字段的错误结果，退出而不进入上述 fallback。

EAGAIN/ENOSYS 是按此 x86-64 Linux ABI 解码。未把 EAGAIN 解释成只与旧内核有关；本轮也未验证目标所在机器的内核版本。

## NFC-05：逐分量 openat 与目录 fd 轮换

FDE 0x4f34b0..0x4f3bb4：

- 0x4f34c1..0x4f34c4：分量数为零跳错误段 0x4f3540。
- 首个中间分量：0x4f3793 取原 dirfd；0x4f379a flags=0x2b0000；0x4f37a1 调 `openat`（GOT 0x98d2e8）。
- 后续中间分量：0x4f39ad..0x4f39bf 将当前 fd 作为 edi、单分量指针作为 rsi、flags=0x2b0000，调用 openat。
- 0x4f39c5 保存新 fd；0x4f39c9..0x4f39cb 检查负返回值；非负路线 0x4f39d1..0x4f39d4 对旧临时 fd 调 `close`（GOT 0x98c928）。循环在 0x4f3935..0x4f3952 继续或转末段。
- 末分量：0x4f372e 对调用方 flags OR 0xa0800；0x4f3734 当前 dirfd，0x4f3738 单分量指针，0x4f373b mode；0x4f3741 调 openat。
- 末段成功：0x4f374f 按分量数检查是否有临时目录；有则 0x4f375b close。0x4f3763/0x4f3766 写 fd 和结果标记。
- 所选拒绝路线可以汇入 0x4f3676..0x4f3687 的 close。未穷尽异常展开、取消或 JS 交付失败的所有资源路线。

首个与后续中间分量的固定 flags 相同；不能只核对末端 `O_NOFOLLOW` 后宣布整条逐段机制已证实。即使逐段机制成立，它也没有单靠这些指令证明被重命名的目录在后续时刻仍属于原根的目录树。

## NFC-06：完成 callback

- openBeneath 完成 FDE 0x61b230..0x61b4d0：选定成功路线 0x61b41d 调 napi_create_int32、0x61b490 调 resolve；错误路线 0x61b38b 调 reject。
- openRootDir 完成 FDE 0x61b4d0..0x61b72d：0x61b67a 调 napi_create_int32，0x61b6ed 调 resolve，0x61b63b 调 reject。
- 对应 GOT：0x98d488、0x98d808、0x98d800。

这组调用点支持“fd 数值交付到 JS Promise”的局部形态；不把它外推为所有交付失败均已正确 close。

## ABI 与解释来源

- [Linux v6.12 openat2 公开 ABI](https://github.com/torvalds/linux/blob/v6.12/include/uapi/linux/openat2.h)：24 字节结构的三字段及 resolve 位。
- [Linux v6.12 x86-64 syscall 表](https://github.com/torvalds/linux/blob/v6.12/arch/x86/entry/syscalls/syscall_64.tbl)：437 对应 openat2。
- [openat2 手册](https://man7.org/linux/man-pages/man2/openat2.2.html)：解析约束、EAGAIN 的竞争相关语义。
- [open 手册](https://man7.org/linux/man-pages/man2/open.2.html)：openat/dirfd、O_PATH、O_NOFOLLOW 等语义。
- 原创 `abi-layout.c` 对分析机现有头文件执行编译期断言：结构大小/偏移、flags、resolve 位、errno、syscall 编号。此检查不说明产品构建采用了同版本头文件。

## 如何复核

将合法取得且摘要一致的 Linux 模块交给：

```sh
python3 verify-static.py /absolute/path/to/claude-native-binding.node
```

脚本只接受一个输入文件，拒绝末端符号链接、目录与其他非普通文件。读取的字节通过大小与 SHA-256 校验后，写入脚本自行创建的私有临时快照；已有的 GNU readelf/objdump 只读取这个稳定快照，结果 JSON 输出到 stdout。脚本不接受输出文件/目录参数，不改写输入或任意已有文件，结束时只清理自己创建的临时目录。它不执行目标、不安装依赖、不联网。编译器仅对原创的 `abi-layout.c` 执行 `-fsyntax-only`，检查分析机的 x86-64 Linux ABI 常量与结构布局，不链接、不运行。

本轮 **123/123 项选定静态检查通过，覆盖 14 个 FDE 解码窗口**。研究时产生的长反汇编单独保留，不随正文发布。另有 10 项原创 fixture 单测，覆盖错误摘要/大小、symlink、目录、FIFO、拒绝输出参数、稳定快照与清理；这些测试不需要真实模块，可运行 `python3 test-verifier.py`。通过的是样本绑定的定位检查，不是全控制流验证、安全认证或真实行为测试。

[返回原理正文](README.md)
