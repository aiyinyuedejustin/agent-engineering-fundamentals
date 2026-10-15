# Linux ASAR 显式配套验证

验证日期：2026-10-15 UTC。结论：**显式提取通过；同版本流程 smoke 通过，但语义扫描存在已报告缺口。**

## 样本与来源边界

- 固定本地样本：Claude Desktop 2.37337.1，Linux amd64。仅把 app.asar 和明确指定的 app.asar.unpacked 当作字节数据。
- ASAR：49,024,278 字节；SHA-256：`3d4aea62ccf045ea88d3e92ce728e23aa01c965f25eda450f6369e7557848395`。
- 已先核查历史 Linux REA 成功记录：integrity_policy=fail，完整性矛盾为空。现有已知 companion 失败记录仅为 Windows/macOS；本轮没有读取或重试这些材料。
- 既有 APT 报告记录 Good signature、Packages 与已签名 InRelease 一致、DEB SHA-256 匹配。签名指纹为 `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`；原 GPG 日志同时提示 owner trust 未建立。
- 这里只复核既有来源报告与当前 ASAR 身份，没有重新认证下载、签名或外层包到当前提取目录的来源链。ASAR 成员哈希本身不认证发布方。

## 工具与动作

- 使用当前 05 工具箱；清单覆盖的 30 项在操作前后哈希一致。适配器为 bounded-asar-v1，配套合同为 explicit-exact-asar-sidecar/v1。
- inspect-asar 只检查容器元数据，本身没有 --unpacked-dir 参数。其 exit 0，正确列出 3 个外置排除项，并保留 declared_member_integrity_verified=false。
- unpack-asar 明确传入固定 app.asar.unpacked；不猜目录、不跳过声明。所有步骤保持默认限制：256 MiB 容器、16 MiB 头部、64 MiB 单文件、512 MiB 总逻辑提取量、20,000 条目。没有提高限制。

## 声明与实际覆盖

| 项目 | 结果 |
|---|---:|
| ASAR 条目 | 530 |
| packed 常规文件 | 486 |
| 显式 unpacked 常规文件 | 3 |
| 实际输出文件 / 目录 | 489 / 41 |
| 有完整性声明且全部整文件及分块 SHA-256 通过 | 489 |
| packed 逻辑字节 | 51,247,344 |
| unpacked 字节 | 30,033,568 |
| 合计逻辑输出字节 | 81,280,912 |
| 精确共享范围别名 | 25 |

- sidecar 清点完成，missing / extra / invalid 均为空。默认容器排除项保留于 container_exclusions，成功提取的 exclusions 为空。
- 489 个当前输出文件的大小与 SHA-256 还全部匹配既有 Linux 成功提取清单。输入身份元数据在全部动作前后保持一致。
- 全部文件保存为 0600；提取根、暂存根和 smoke 目录为 0700；未保留任何可执行权限。输出通过工具原子交付。

## 三个配套成员的实读 SHA-256

- `node_modules/@ant/claude-native/claude-native-binding.node`
  - 10,026,272 字节；整文件及声明分块校验通过
  - `c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6`
- `node_modules/node-pty/prebuilds/linux-x64/pty.node`
  - 75,976 字节；整文件及声明分块校验通过
  - `123792d8f22f36d519b21dfb6f4b716f9b18b9e579085ea2840d0773d88d35fd`
- `resources/github-mcp/github-mcp-server`
  - 19,931,320 字节；整文件及声明分块校验通过
  - `a649c80070fe9cb4e002b7bc37f54df8f9bdd46a8e90ae7ee5684ce901779f6f`

## 同版本、同字节一条命令 smoke

- 同一个 Linux ASAR 和同一个显式 companion 分别作为 old/new；使用相同标签和默认规则。入口 diff-versions.py 正常结束，exit 0。两个提取阶段各自 489 个声明成员完整性通过。
- before/after 快照字节相同。文件增加、删除、变更、候选移动及 unresolved 均为 0；所观察的静态候选也没有变化。
- 每侧 3,761 条候选记录：427 个文件 scanned，44 个 hashed-only，18 个 scan-incomplete。三个原生成员均仅 hashed-only。
- 两侧 coverage.complete_within_declared_scope 均为 false；两条覆盖警告保留。18 个拒绝条目的公开诊断只有 scanner-rejected-input / ToolkitError，本轮没有据此猜测具体词法错误或预算需求，也没有放宽扫描器。
- **这仅说明该真实 Linux 样本能完成显式配套与两侧同字节流程。零差异不能表述为完整语义无变化，也不证明跨版本变化检出能力。**

## 成功与停止边界

- 本轮没有哈希或声明失败；没有更换提取器、修改声明、绕过校验或提高容量。
- 完整只指所选 ASAR 声明的 packed + unpacked 范围；不覆盖整个应用、ion-dist、安装行为、运行时能力或发布方认证。
- 未执行安装器、JS、原生二进制或加载产品模块。没有新增下载、安装、登录、系统设置更改。
- 没有对 Windows/macOS 失败材料作新动作，不说明其错误已解决。
- 原包、提取源码、字体、完整快照和原始清单全部留在私有暂存。此报告只含原创说明与必要元数据。


[机器可读验证记录](LINUX-ASAR-VALIDATION.json)保留本次样本、默认限制、完整性与扫描覆盖计数。
