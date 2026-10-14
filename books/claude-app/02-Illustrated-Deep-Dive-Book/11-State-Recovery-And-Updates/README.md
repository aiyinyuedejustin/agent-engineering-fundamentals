# 恢复专题 设置与状态恢复

让偏好能够保存，让失败能够结束，让更新真正生效

桌面应用的可靠性藏在“下一次”里：下一次启动能否读到设置，下一次重试会不会刷新错页面，下一次进程启动是否真的换成新版本。本次样本把这些问题拆给不同的状态所有者，并为网络、renderer 和图形进程使用不同的恢复路径。

最值得带走的四个发现是：用户配置与壳层 store 采用不同损坏策略；内存生效、广播完成和磁盘确认是不同结果；离线等待会延长自动重试预算；Linux 的默认更新责任属于 apt，应用负责发现版本变化与重启接管。

## 本章地图

[01 状态所有权](#01-状态所有权) · [02 设置的写入边界](#02-设置的写入边界) · [03 网络与进程恢复](#03-网络与进程恢复) · [04 Linux 更新](#04-linux-更新) · [05 日志与诊断](#05-日志与诊断) · [06 验证入口](#06-验证入口)

### 证据图例

**S 静态**表示官方 Linux amd64 2.37337.1 包中的声明与控制流；**A 原创**表示本书的状态图、解释与测试建议。研究截点为 2026-10-14，没有启动 Claude、登录、读取真实配置或日志，也没有故障注入。代码参数不等于实测时限；当前功能开关、组织策略与远程页面行为仍未知。

[设置与恢复台账](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)保存 SET、RES、UPD、LOG 共 24 条证据及位置。窗口与 IPC 归属见[第 1 卷](../01-System-Architecture/README.md)；扩展配置的专门安全边界见[第 6 卷](../06-MCP-Host-Internals/README.md)。

## 01 状态所有权

### 没有单一的设置对象

store 是主进程持有的持久化键值存储；schema 是约束字段与类型的结构规则。同一个设置界面可能同时操作多个 store 和加载器。

| 状态 | 本包所见所有者与载体 | 典型内容 | 恢复时要保住什么 |
|---|---|---|---|
| 通用壳层 store | 主进程 electron-store 派生实例，默认 `config.json` | 主题、语言、更新记账 | 可继续运行的壳层状态 |
| 用户可编辑应用配置 | schema 加载器，`claude_desktop_config.json` | preferences、MCP、图形加速开关 | 原件与手工编辑内容 |
| 窗口几何 | 独立服务，`window-state.json` | 尺寸、位置、显示器边界 | 新显示器布局中的可见位置 |
| 恢复标记 | 专用文件或 store 项 | GPU 故障、更新尝试及失败次数 | 尚未解决的跨启动证据 |
| renderer 临时状态 | 本地页面内存 | 错误层、可选小游戏状态 | 当前页面生命周期即可 |

这是 [SET-01、11、RES-06](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)涉及的状态范围，不是全产品存储清单。研究读取的是路径构造与加载代码，没有打开同名用户文件。

分开所有权后，一个具体决定就变得清楚：窗口拖动值得合并写入，用户手工配置损坏值得保留原件，而恢复标记必须等修复确认后才能清除。它们不适合共用“解析失败就置空”的策略。

### 主题有偏好值和解析后的结果

主题方法同时修改 Electron `nativeTheme.themeSource` 与 store 中的 `userThemeMode`。启动接受 `system`、`light`、`dark`；原生主题更新事件再驱动窗口背景、标题栏与菜单处理。[SET-02](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

`system` 表示跟随系统的偏好，不是一套固定颜色。自建产品可以让原生窗口订阅最终明暗状态，而不只是启动时读一次用户选项。这里描述壳层通路；远程聊天页面的全部主题 token 和跨设备同步不在证据范围。

### 语言目录数量与界面覆盖分别计量

语言初始化先建立 `en-US` 回退，再尝试保存的 locale，或匹配系统偏好语言。locale 是语言与地区标识。显式切换还检查文件名形状及目录存在性；成功后更新主进程的语言实例和持久化值，向存活 renderer 广播，窗口销毁时取消订阅。[SET-03](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

资源目录有 43 个语言 JSON，含 `zh-Hans`、`zh-Hant`、`es-419`；系统自动选择先经过较窄白名单与地区式正则，本包由此得到 10 个候选。显式切换的文件名规则更宽。这三个数字层次应分开：包携带哪些目录、自动探测能选哪些、设置菜单实际提供哪些。目录存在不证明菜单展示或译文完整。

对实现者，最有用的检查是让自动匹配、手动选择和资源清单共同引用一个权威定义，并单独标记实验目录。只测试“语言 JSON 能解析”会漏掉这些范围差异。

## 02 设置的写入边界

### 偏好 API 不是任意 JSON 写入器

AppPreferences 写入先验证 key 属于 schema，再拒绝主进程专用字段，随后校验 value。快捷键另有合法性检查；部分授权相关结构只允许普通偏好入口删除条目，不允许从这里增加授权。读取与广播也经过投影，将部分授权、目录访问集合替换为空值。[SET-04](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

因此，磁盘对象、主进程对象和页面可见对象具有不同形状。一个可借鉴的分工是：普通偏好走字段校验；授权和信任变更走专门入口；页面只接收展示所需的投影。这些字段防线仍须与第 1 卷的 IPC 调用者检查配合。

### 配置损坏按损失成本处理

用户可编辑配置加载器区分缺失、读取错误、JSON 错误和 schema 错误。它可过滤无效 MCP 条目再校验；整体不合法时仅保留少数启动恢复字段。被标记为需要保护原件的降级状态会使 writer 返回 `parked`，即暂停落盘，避免把内存回退值覆盖到原文件。[SET-05](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

这一规则不能泛化为“一有异常就停写”。文件缺失；仅空白、控制字符或替代字符的空内容；被实现视为空值的 JSON（null、布尔、数字、空字符串、空数组、空对象）；以及剔除无效 MCP 条目后整体校验通过的配置，都不会因此设置降级标记。判断依据是加载结果标记；被剔除的无效条目也不能据此承诺会永久留在原文件中。

通用壳层 `config.json` 采用另一套策略：[SET-09](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

| 情况 | 所见处理 |
|---|---|
| JSON SyntaxError | 回退空对象并标记损坏，后续显示 Settings Reset 提示 |
| `UNKNOWN`、`EBUSY`、`EIO` 开文件错误 | 以 250ms、500ms 两次延迟重试 |
| `EISDIR`、`ELOOP`、`ENOTDIR` 路径结构错误 | 尝试改名为带时间戳的 corrupt 文件，再重建 |

改名保留路径只属于特定错误分支；不能说所有损坏都会先备份。用户配置与可重建壳层状态的损失成本不同，恢复方案也随之不同。

### 保存有三个完成时刻

```text
合法偏好变更
    │
    ▼
主进程内存使用新值
    │
    ▼
尝试持久化 ── written / parked / write-failed
    │
    ▼
向订阅者发送变更
```

*图 1　A 局部更新链。内存采用新值、页面收到通知、磁盘写入确认，应分别记录。*

writer 返回 `written`、`parked` 或 `write-failed`。本次追到的普通偏好 IPC 包装器没有向调用者继续传递落盘结果；这揭示了状态分层，但未观察到 UI 误报“保存成功”。GPU 恢复等重要路径会检查 `written` 再决定后续处理。[SET-06、RES-05](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

用户配置写入优先采用按路径互斥、临时文件与 rename，默认文件权限参数为十进制 384，即 POSIX 0600；某些 rename 失败又会回退直接写。因此它具有原子替换优先路径，而非所有错误路径都具有原子性或掉电保证。[SET-07](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

### journal 也要确认它属于哪一版文件

journal 是写入过程留下的恢复记录。本包 store 的 `.journal` 同时携带内容摘要与目标 store 的版本摘要。启动恢复既检查记录完整性，也检查它是否适用于当前目标，避免残留记录覆盖后来已经变化的文件。退出调用 `quiesce` 等待正在提交的写入。[SET-08](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

这些摘要用于完整性与前序版本匹配，不是有密钥的恶意篡改认证。库内另有版本迁移和失败回滚能力，但本次主 config store 构造没有注册 migrations 表；应用配置校验前清理旧枚举也只支持“兼容性归一化”的结论。[SET-10](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

窗口几何则采用约 1 秒防抖、串行写入链与关闭时 flush，跳过最小化状态，恢复时校验尺寸并按当前显示器工作区重新安置。[SET-11](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json) 这里值得保存的是正常窗口的位置意图，而非每次临时外观；旧坐标也必须重新放回当前设备布局。

## 03 网络与进程恢复

### 错误入口留在本地外壳

主内容失败后，主进程将错误交给本地外壳；外壳表达标题、说明、Reload、可选 Restart 与重试状态。这样，恢复 UI 不必依靠失败的远程文档加载。具体容器关系见第 1 卷。[RES-01](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

### 自动重试有预算 但不是三分钟墙钟截止

| 条件 | 本包静态规则 |
|---|---|
| 普通 `load_failed` | 基准延迟 0、15、30 秒，后续沿用末档 |
| 抖动 | 基准值乘以约 ±20% 随机量 |
| `http_error` | 从较晚档起步；连续超过 3 次后停止自动重试 |
| 初始自动重试预算 | 约 180 秒；等待离线恢复会延长预算 |
| load 或网络 reset 正在执行 | 避免叠加新的请求 |
| 首次成功加载前 | 重试可关闭连接、清 DNS 缓存、重新加载代理配置 |
| focus / show / resume / unlock | 可提前触发，约 10 秒节流 |
| 自动重试耗尽后的唤醒 | 另有约 60 秒离线等待边界 |

[RES-02–03](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)显示，初始 timer 的离线等待没有统一墙钟截止；离线暂停会延长原预算。把它缩写为“最多重试三分钟”会丢掉这个重要条件。它也不是所有网络请求共用的重试策略。

回调执行前还检查当前错误层是否仍是原先那一个。用户已开始新导航时，旧错误的计时器不能刷新新页面。这是比延迟常量更有价值的结构：异步结果必须验证自己仍属于当前状态。

可选离线小游戏也属于错误页，通过主进程功能开关懒加载，资源失败可不渲染，Map 只保存在页面内存。它不能作为离线聊天能力的证据。错误页存在 `role=status`、隐藏装饰图标与减少动态效果查询，但尚未完成屏幕阅读器和键盘实测。[RES-06](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

### 不同进程故障有不同升级路径

renderer 死亡路径在约 5 分钟安静期后重置尝试计数；普通分支上限为三次，`launch-failed` 延迟为 1、5、20 秒。达到上限后转为本地重启、帮助或图形加速说明。主动结束、待执行 reload 与打印保护另有分支，不能概括为每次死亡都恰好重试三次。[RES-04](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

GPU 即图形处理器；它对应的进程连续故障需要跨启动记忆。代码保存 `gpu-crash-streak`：相邻死亡超过 5 分钟可重置普通计数，三次进入关闭硬件加速与提示重启路线，另有一分钟内二十次死亡的终止循环保护。自动关闭和极端终止各受动态功能开关约束。[RES-05](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

```text
进程内有限重试
      │ 仍持续故障
      ▼
尝试修改下次启动配置
      ├─ 写入确认且恢复条件满足 → 清理故障标记
      └─ parked 或 write-failed → 保留标记，后续继续恢复
      │
      ▼
提示用户重启，或按门控进入终止循环保护
```

*图 2　A 恢复升级图。保留标记的理由是修复尚未持久化；“已经尝试修复”不足以清除跨启动证据。*

恢复手段越往下，成本越高。可以把网络重试、renderer 重建、修改启动配置、终止循环分别记录，避免一个总“重试次数”掩盖不同的故障责任。

## 04 Linux 更新

### 包管理器安装 应用识别变化

本版本 Linux 的 `enableUpdates` 路径关闭应用内 updater，由 apt 管理安装。在相关检查未被策略禁用时，应用读取 apt Packages 比较版本，并检查 `/proc/self/exe` 的 deleted 标识及当前 exe 是否存在，以发现运行中的可执行文件已被外部替换。`autoUpdate.disabled` 为真时，周期分支可退回 idle 并跳过这些检查；focus、unlock、resume 的替换检查也受此条件限制。[UPD-01](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

外部替换会形成内部 `replaced` 状态，给页面的投影将它映射为 `Ready`。请求更新重启时，这条分支调用保留导航的 relaunch。显式“检查更新”入口也可打开官方下载页。[UPD-02](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

```text
apt 发现并安装新包
       │
       ▼
运行中应用检测可执行文件已被替换
       │ 内部 replaced → 页面 Ready
       ▼
用户请求重启 → 保留导航并 relaunch
       │
       ▼
新进程版本与更新尝试记录核对
```

*图 3　A Linux 默认责任分工。应用检测受更新策略约束；图示不表示本研究执行了 apt 安装或重启。*

包里同时包含 Electron autoUpdater 的 checking、downloading、ready、error 等公共状态，不能据此说 Linux 默认在应用内下载并安装。另一组更新记账记录 from/to version、上次尝试、失败次数和实际版本，用于跨启动确认；它也不能证明存在自动回滚。[UPD-03](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

组织更新要求是独立路径：优先选择可见且未最小化的合适窗口，没有时等焦点变化；策略禁用自动更新时，提示转向管理员处理。[UPD-04](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json) 当前组织是否启用它，仍取决于实际策略。

这套关系给实现者一个明确验收点：下载完成、文件替换、进程重启和新版本运行应分别记录。只有后一个事实成立，才足以确认应用已经接管了更新。

## 05 日志与诊断

主日志格式含时间、级别、消息和元数据；打包默认 info，开发默认 debug。默认 file transport 为每文件 10 MiB、最多 5 个文件；renderer 类别只收相关主 frame 的 warning/error，单文件上限 5 MiB，继续继承默认数量上限。[LOG-01](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json) 这些是构造默认值，不是全系统日志总量承诺。

日志初始化前先缓冲；路径异常时尝试搬移重建，再失败可禁用文件日志。某些参数元数据始终被替换，完整行 scrub 则只在受限合规模式启用，scrubber 失败使用固定 redacted 占位。浏览器类别另会截断长行并裁去查询参数与片段。[LOG-02](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

“有脱敏函数”不足以推出所有日志都已去标识化；本次没有审计全部覆盖率。日志不可写时可停止文件记录，则体现了另一条可靠性边界：记录故障的设施不应递归制造新的致命故障。

`showLogsInFileManager` 尤其值得追到实现。它会准备多类诊断材料，生成下载目录中的 ZIP，再在文件管理器显示；它并非仅打开现有日志目录。[LOG-03](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)

因此，自建支持流程应将生成支持包、检查内容和发送给接收者分成独立步骤。日志轮转限制、局部 scrub 和文件名都不能替代对最终 ZIP 的隐私检查。这里没有生成或读取任何真实用户支持包。

## 06 验证入口

### 从机制导出的最小故障矩阵

| 测试对象 | 合成故障 | 需要分别确认的结果 |
|---|---|---|
| 用户配置 | JSON 损坏、缺失、空文件、局部条目不合法 | 可运行回退、是否 parked、原件是否保留 |
| 持久化 | rename 失败、磁盘不可写、旧 journal | 内存值、通知值、落盘结果与恢复对象 |
| 网络恢复 | 离线、频繁 focus、新导航 | 预算延长、节流、旧回调失效 |
| GPU 恢复 | 配置写入失败 | 跨启动标记保留，避免失忆式重启 |
| 更新 | 文件已替换但进程仍旧 | 页面状态、重启和新版本核对分开 |
| 诊断 | 日志目录不可写、支持包生成 | 降级运行、ZIP 内容与分享边界 |

这是 A 测试建议。真正断电、磁盘满、代理异常、GPU 故障、多显示器恢复与辅助技术尚未验证；内存模拟不能替代这些实验。

### REA 与证据核验

REA 6.5.0 对更新要求模块和本地错误页完成精确选源分析，解析 2 个 JavaScript 文件、0 个解析失败。主 chunk 加错误页的另一次运行使用 1,024 MiB heap、3,000 semantic-node 上限和单文件 60 秒限额，主 chunk 超时，返回 partial observation。本章大部分机制来自原文件惰性读取与控制流人工核对，不是完整全程序调用图。

初轮台账核验了 143 个短锚点，保存文件 SHA-256、字符及 UTF-8 字节区间；审查进一步补充非停放例外和更新策略条件。位置读回匹配不等于机制已运行。最终锚点、输入身份与 REA Evidence ID 均可在[结构化证据](../../04-Extracted-Core-Code-And-Scripts/evidence/data/settings-resilience.json)复查。公开内容不包含完整 bundle、原始 REA 输出或用户状态。

下一步最有价值的证据是受控故障实验：证明新状态真的落盘，旧回调真的失效，恢复标记只在修复确认后消失，以及更新后确实运行新版本。本章先把这些问题各自的责任边界固定下来。
