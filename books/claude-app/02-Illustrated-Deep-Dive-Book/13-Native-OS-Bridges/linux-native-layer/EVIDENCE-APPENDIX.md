# 原生层证据附录

本附录仅含研究范围、必要定位与原创解释，不包含目标二进制、完整符号表、原始大段源码、反汇编或字符串。审计日期：2026-10-15 UTC。

## A. 输入身份与授权边界

唯一原生分析目标是先前已通过 Linux ASAR 显式配套声明校验的 `node_modules/@ant/claude-native/claude-native-binding.node`。当前实读大小为 10,026,272 字节，SHA-256 为：

`c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6`

配套 ASAR 版本为 Claude Desktop 2.37337.1 Linux amd64；既有显式提取报告确认该成员的整文件与声明分块 SHA-256 均通过。本轮再核对上述身份，不修改声明、不重新解压、不放宽完整性要求。成员哈希证明内部一致性，不等同于独立认证发布方；外层包到提取目录的来源链未在本轮重新认证。

少量调用层闭合只读取同一份已验证 Linux 输出中的：

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| `node_modules/@ant/claude-native/index.js` | 311 | `6c33aacb3683311b773761656fdbf51dc25d74d323dc28c75dd7f3e20cb7cbae` |
| `node_modules/@ant/claude-native/package.json` | 993 | `78a5eca095e19aea49b2f502714166129e78549aac601fca62c3fe2a3e64ad90` |
| `.vite/build/index.chunk-ny8j26BQ.js` | 6,956,732 | `d241a58d6a392b2074afb85713b9a7210cac511d068c30cb182552775e4ee512` |

同版 worker JS 仅用于确认另有同类 loader，本节不从中新增功能结论。共享 JS 中出现其他平台的分支，不代表本轮读取了其他平台样本；Windows/macOS 已知失败材料未读、未重试。

## B. REA 优先使用与补充工具

已安装 `rea-agents` 版本为 6.5.0。先读安装包 README、已安装 CLI 合同及 `ObjdumpCommand.js`，再参考同版本源码目录的 `docs/reverse-engineering-tools.md`、`docs/rust-binaries.md`、`docs/binary-diagnostics.md`；实际能力由安装包命令与结果确认。

| 选择 | 实际操作与结果 | 为什么没有进一步扩展 |
|---|---|---|
| REA GNU objdump 集成 | `inspect-with-objdump` 的 file_headers、section_headers、symbols；3 次 exit 0、未截断、调用前后目标哈希相同 | 当前 symbols 操作固定为 `objdump -t`，不能替代动态符号表检查 |
| REA Rust reader | `inspect-rust-binary` 成功识别 ELF、amd64、64 位小端 | 未找到 `.dep-v0`；不恢复 crate 清单，不据此说没有依赖 |
| REA offline layout | 检查已装依赖条件 | 当前 Python 找不到 pwntools、pyelftools、Unicorn；没有安装或尝试动态调试 |
| readelf / objdump 补充 | readelf 的 ELF、动态符号、动态依赖、版本、notes 与重定位；有界 objdump 代码窗口 | 纯静态、不解析运行时依赖路径、不请求 dlopen/ldd |

REA 结果原样保留其限制：provider 版本未由 REA 探测，前后摘要一致不保证调用期间不存在瞬时改写。本轮另行运行系统工具的版本查询，观察 GNU binutils 2.44；Node 仅用于运行既有 REA 分析器与原创测试，版本 v24.19.0。

REA Rust reader 在只读数据发现编译器路径形态并给出 `inferred` 标记；它不是编译器认证，本节不发布该路径内容或据此声明精确 Rust 编译器版本。`.symtab` 缺失，`.dynsym` 存在；REA 的 “no symbols” 只对应其此次普通符号表操作，绝不解释为没有动态符号。

未执行 `ldd`、`require(target)`、目标 JS、原生程序、构造函数、安装器、GDB inferior 或仿真。没有新的工具安装、下载或系统配置更改。

## C. 分级证据矩阵

- **结构观察**：格式、声明、符号、重定位或清晰的 JS 静态调用。
- **局部指令观察**：已解码的局部分支或调用位置，不代表从公开入口完整可达。
- **线索**：有界字符串或同现关系，不独立支持功能判断。
- **原创建议**：研究者自己的模型，不是产品代码恢复结果。

| ID | 直接观察 | 定位 / 复核方法 | 结论边界 |
|---|---|---|---|
| LNB-01 | ELF64，小端，EM_X86_64，ET_DYN，entry=0 | ELF header；31 个 section header、11 个 program header | entry=0 不代表装载无副作用；存在 INIT/INIT_ARRAY |
| LNB-02 | 5 个 DT_NEEDED；GLIBC 版本需求最高至 2.34 | `.dynamic`；`.gnu.version_r`；强引用如 pthread_create、dlopen、dlsym 对应 GLIBC_2.34 | 不是产品全平台最低 OS 说明；未解析实际库路径 |
| LNB-03 | 256 个 dynsym 项；254 个命名未定义项；59 个 napi_、19 个 pw_；唯一已定义导出为注册函数 | `.dynsym` 索引 255，链接 VA `0x704e90`，size `0x132c`；readelf 与样本绑定解析器交叉核对 | 导出入口不是 JS 方法清单；未定义项不全是强引用 |
| LNB-04 | 注册函数符号范围内有 TSFN 创建和 cleanup hook 调用 | `0x705970` → GOT `0x98d7b0` → dynsym 98；`0x70579f`、`0x705bb8` → GOT `0x98de98` → dynsym 140 | 有调用位置，不宣称任意启动路径必然执行或正确清理 |
| LNB-05 | external Buffer 返回值为 22 时进入 copy Buffer 调用 | 下节列出完整局部证据链 | 不证明运行发生、端到端零拷贝、完整内存安全或作者归属 |
| LNB-06 | PipeWire 依赖 + 19 个动态导入 + 局部指令调用 | connect_fd：`0x66293f` → `0x98d908`；stream_connect：`0x6644cf` → `0x98d940`；dequeue：`0x5dbb5d` → `0x98d760`；queue：`0x5dbd69` / `0x5dbece` → `0x98d768` | 不推导已录音、截屏、控制桌面或通过权限 |
| LNB-07 | `.rodata` 中命中 portal ScreenCast / RemoteDesktop 名称 | 文件偏移 `0x53dae` / `0x53d4c`；只扫描预选 14 词、每词最多 8 命中 | 只作为后续引用追踪线索；不拼接为已证明的功能链 |
| LNB-08 | loader 明确加载同目录 .node；helper wrapper 等 native 返回 fd，再构造 Node Socket；packaged 缺方法则拒绝 | index.js；main chunk 的 `function mi(e)` 与 `async function qCn(e)`，主 chunk Unicode 字符位置分别约 282332 / 2937955 | 只证明调用层要求与分支；不证明 native 内部 peer 身份验证 |
| LNB-09 | 必需 loader 失败即抛错；safe-fs wrapper 调用 openRootDir/openBeneath 等并处理部分失败清理 | 主 chunk Unicode 字符约 282531、507192–508750 | 不证明原生路径包含性算法或所有竞态安全 |

动态依赖的精确名称：`libpipewire-0.3.so.0`、`libgcc_s.so.1`、`libm.so.6`、`libc.so.6`、`ld-linux-x86-64.so.2`。没有从依赖名称推断库的小版本，也没有把 DT_NEEDED 当成完成运行时解析。

254 个命名未定义项中有 14 个 WEAK 项；其余 240 项为 GLOBAL。弱引用如部分 pidfd / statx 名称不能当成一律强制存在的同一兼容门槛。未观察到某个库的 DT_NEEDED，也不能排除 dlopen、静态链接或更间接路径；样本确有 dlopen/dlsym 导入。

## D. Buffer 分支：从符号到局部控制流

下面是原创语义摘要，未复制原始反汇编：

| 证据步骤 | 精确事实 |
|---|---|
| 动态符号 | 索引 144 为 `napi_create_external_buffer`，145 为 `napi_create_buffer_copy` |
| 重定位 | GOT `0x98ded8` / `0x98dee0` 分别由上述符号的 R_X86_64_GLOB_DAT 重定位绑定 |
| 对齐依据 | `.eh_frame_hdr` 表给出该局部函数候选 initial location `0x70afa0`，下一项 `0x70b3d0`；从前者开始用 objdump 顺序解码 |
| 调用 | 链接 VA `0x70b0dc` 的间接调用引用 `0x98ded8` |
| 分支 | `0x70b0e4` 比较返回 EAX 与 `0x16`；`0x70b0e7` 在不等时转到 `0x70b12d` |
| 相等路线 | `0x70b0fb` 的间接调用引用 `0x98dee0` |
| 公共语义 | 官方 napi_status 枚举按零起始计数，napi_no_external_buffers_allowed 的值为 22（第 23 个成员）；同时核对 external Buffer API 的不支持说明 |

链接 VA 不是运行时地址。去符号化后 objdump 常用最近的公开符号加巨大偏移来显示邻近地址，不能据此把所有代码归属为 `napi_register_module_v1`。这里的注册函数调用点只采用该导出符号声明的有限范围；Buffer 分支在另一段代码。

样本绑定的候选扫描只在 `.text` 的 7,738,104 字节内寻找指向选定 GOT 槽的 RIP-relative 间接 call/jump 字节形态。这些初筛结果仍叫候选，未全部解码、未声称完整调用图。用于正文的 Buffer 与 PipeWire 局部窗口再以 unwind header 的已声明起点对齐，并用 GNU objdump 复核。普通字符串扫描限于 `.rodata` 402,100 字节，命中不等于引用关系，未命中不等于全文件没有该词。

## E. 主动不下结论的内容

1. 未恢复完整 Rust 源码、crate 依赖树、完整 native 导出注册表或整条媒体调用链。
2. 没有证明本机或任意账户启用了相关功能，更没有访问麦克风、桌面、窗口、剪贴板或用户文件。
3. 文件/进程/socket 导入可来自通用运行库；chroot、setuid、fork 等名称不能证明产品某一 sandbox 策略已经实现。
4. GNU_RELRO、BIND_NOW、不可执行栈声明等只可作为静态加固线索，不是整包安全认证。本节不据此做漏洞或“安全无误”判断。
5. Node-API 公共规范用于解释接口，不被用来代替目标版本事实；注册入口中的 v1 不是完整 Node-API 使用版本号。
6. 原创 gate 测试只覆盖合成 JS 生命周期，不覆盖真实线程、真实 Node-API、fd 传递、PipeWire、portal 或 native 内存。

## F. 公开一手解释来源

- [ELF 动态链接规范](https://refspecs.linuxfoundation.org/elf/gabi4+/ch5.dynamic.html)：命名依赖与装载结构的解释。
- [Node.js v24.11.0 Node-API](https://nodejs.org/download/release/v24.11.0/docs/api/n-api.html#napi_status)：固定版本的状态枚举与 ABI 语义。其 external Buffer、thread-safe function 与环境清理章节只用于解释所见 API。
- [PipeWire Stream](https://docs.pipewire.org/group__pw__stream.html)：stream 与 buffer 接口的公开语义。
- [PipeWire Core](https://docs.pipewire.org/group__pw__core.html)：connect_fd 的连接与 fd 语义。
- [XDG ScreenCast portal](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html)：说明协议自身仍有多阶段会话过程，不作为目标执行证据。

文档查询日为 2026-10-15；在线 PipeWire 与 portal 文档会演进。本报告只采用所见 API 的基础含义，不把其当前新增特性归到旧样本。
