# DEB → 指定 ASAR 的一行静态差分

一条命令从两个本地 Linux DEB 中投影指定 app.asar 和精确 companion，核验声明完整性，再生成静态候选差分。不会安装软件或运行包内代码。原 diff-versions.py 接口不变；此专用入口复用同一 ASAR、Sidecar、scanner、diff 和原子交付逻辑。

## 一行使用

将 deb_projection.py 和 deb_versions.py 放在工具箱根目录，与 reverse_toolkit.py、toolkit/ 并列。下面使用已验证 Linux 2.37337.1 包内的实际路径；路径布局变化会明确失败，不自动猜测：

```sh
python3 -B deb_versions.py inspect /private/input.deb --asar-member usr/lib/claude-desktop/resources/app.asar --companion-prefix usr/lib/claude-desktop/resources/app.asar.unpacked
python3 -B deb_versions.py compare /private/old.deb /private/new.deb --asar-member usr/lib/claude-desktop/resources/app.asar --companion-prefix usr/lib/claude-desktop/resources/app.asar.unpacked --platform-label linux-amd64 --output /private/new-output
```

selector 必须精确、规范相对路径。两边共用同一 selector、platform、规则和预算；不自动搜 app.asar、不补 companion、不处理安装脚本。标签由用户提供，未经版本或平台认证。inspect 完整验证外层流，但不提取、不证明 ASAR 声明完整性。compare 才核验内层并整体交付。--rules 可传原工具箱规则 JSON（额外读取上限16MiB）；没有跳过完整性、忽略额外文件或提限参数。

输出父目录须事先存在、可信且静止，输出路径不得已存在。报错退出2，正常退出0。任何被捕获失败均撤销本次暂存，已有/竞态出现输出保持不变。

## 精确支持合同

- AR 恰三成员、固定顺序：debian-binary（精确2.0换行）、control.tar.xz、data.tar.xz；成员名允许最多单个尾斜线；严格尺寸/字段/换行补齐/容器EOF。
- 单个 FORMAT_XZ、CRC64、有界解码，拒绝多流、Stream Padding、任何尾字节或缺损 footer/index/check。TAR 双零后继续消费零尾块及 XZ 真正EOF。
- 仅 GNU basic magic/version，extended area全部为零；ASCII八进制，不接受base-256；regular为type0，directory为5。NUL regular、USTAR、PAX、GNU K/S、设备、硬链接、contiguous全部拒绝，即使在选区外。
- GNU L仅规范 ././@LongLink、最多4097B、单个最终NUL、严格UTF-8；下一头必须type0，只使用一次；物理头和逻辑条目分别计数。
- control进一步收窄为唯一根目录（可省）和顶层普通文件，必须有唯一control；控制脚本仅哈希、不写盘、不执行。
- data选区外type2仅零载荷、有界目标文本元数据，不解析、不跟随、不物化；链接路径与全局命名空间一样校验，且不能在选区/祖先。其他未知类型仍全局拒绝。
- 路径仅去单个前导./，目录去单个尾/；根目录有专门例外。拒绝穿越、重复/空分量、绝对/非可移植名称。NFC(casefold)包括全部隐式祖先，顺序无关检测文件/目录/链接冲突。显示使用JSON escaping；不声称解决所有视觉混淆。
- companion要求显式真实目录项，完整前缀子树包括空目录全部投影，绝不按ASAR声明预过滤extra。由原Sidecar执行missing/extra/invalid精确核验。

## 预算与磁盘口径

| 新外层资源 | 固定上限 |
|---|---:|
| DEB | 256MiB |
| control+data完整解码流 / 每遍 | 768MiB |
| control流 | 16MiB |
| 非选区opaque普通单项 | 256MiB |
| decoder memlimit | 128MiB |
| 输入/解码输出/载荷读写块 | 64KiB |
| 每压缩成员展开/完整压缩尺寸 | 200:1 |
| 两TAR物理头 / 逻辑条目 | 各20,000 |
| 路径/隐式祖先/清单/GNU L合计表示 | 16MiB |
| 路径UTF-8/深度/分量 | 4096B / 64 / 255B |
| 选区单项 / 原料总量 | 64MiB / 512MiB |
| 每侧原料+逻辑展开同时在盘 | 512MiB |
| 两侧载荷同时在盘 | 1GiB |
| 报告单项 / 总计 | 64MiB / 128MiB |
| inspect stdout编码输出 | 16MiB，完整验收后才输出，超限无半截JSON |
| 单侧外层清单JSON | 16MiB（同时计入报告总计） |

最后四项是该profile独立更严格预算，不是提高原Limits。ASAR原64MiB单文件、512MiB逻辑量、别名副本计费和exact-sidecar规则不变。提取前用原ASAR admission清点声明逻辑量，联合原料尺寸做每侧512MiB预检。落盘选区字节按已核验声明和实际精确读数计费。报告iterencode逐段计UTF-8字节、在写入前拒绝超量。已有scanner/diff会构造内存结构；writer预算不是RSS硬上限，JSON一个token可能先在内存形成。

两遍每侧768MiB，双输入最多3GiB解码工作量，另外每遍有界完整DEB哈希读取；不能宣称一次只读取768MiB。最大新增常规文件内容1GiB+128MiB，不含输入原包、目录/文件系统开销、已有其他任务、进程内存。无CPU/RSS沙箱或fsync持久性承诺。

## 事务与范围绑定

1. 固定两个输入fd，分别完整第一遍AR/TAR/XZ校验，尚不写选区。
2. 在目标父目录创建0700临时目录，同fd第二遍完整扫描；逐项元数据与载荷哈希、完整AR/压缩哈希/DEB哈希再次相等，只复制选区。
3. 复用原ASAR extraction/Sidecar；源和配套复查；原scanner和diff保留覆盖缺口。
4. selector/profile/platform直接进入snapshot policy，重算policy与snapshot摘要；两边policy不同时拒绝。标签保留在snapshot身份摘要。diff JSON和Markdown均明确所选路径/平台/范围，并声明非完整应用。
5. 所有报告成功且原始源fd/path身份最后复核后，复用atomic_publish整体no-replace交付；失败清理本次暂存，绝不删除晚出现目标。

文件0600、目录0700，不恢复owner、mode、执行位、setuid或时间戳。没有subprocess、安装、下载、目标import/source/eval。SIGKILL/断电/清理失败可能留私有暂存。需可信静止祖先和隔离工作区，不防御同UID恶意并发。Linux执行验证不代表Mac/Win原生验证。

## 结果与公开边界

run.json有三层校验与scanner原coverage。outer_envelope_inventory_complete、outer_compressed_streams_verified与selected_asar_declared_scope_complete互不混用。complete_package、complete_application、publisher_authenticity_verified始终false。失败CLI报outer inventory不完整且exclusions未知null，不伪造空清单。

原始包、raw/、inputs/、snapshot和完整清单都是私有中间材料，不应公开。随工具发布的只有原创实现、原创合成测试、文档和脱敏验证摘要。

Linux 2.37337.1 的同包双输入 smoke 已通过：489个声明文件核验，选区79,057,846B，逻辑展开81,280,912B；保留44个 hashed-only、18个 scan-incomplete。零差异仅为同包重复性 smoke，不是两个真实版本的检出验收。未认证发布方，也未扩展Mac/Win原生证据。

## 测试

```sh
python3 -B -m unittest discover -s tests -p 'test_deb_*.py' -v
```

所有fixture由标准库动态合成，不含产品字节；tarfile仅用于测试生成，不用于生产解析或提取。脱敏实际运行摘要见 DEB-PROJECTION-VALIDATION.json。独立评审计划的87类是类别清单，不能把测试条数或部分覆盖称为全部87类验收完成。实现仍需外部安全审计，当前结果不证明任意恶意包安全。
