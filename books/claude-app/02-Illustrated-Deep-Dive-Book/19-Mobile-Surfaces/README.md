# 第 19 卷：Claude iOS / Android 的界面与交互边界

本章讨论标准版 Claude iOS / Android 应用，重点是输入、语音、文件交接与系统入口如何适应移动环境。材料来自截至 2026-10-14（UTC）观察的官方文档和图片，用于补充 Desktop 2.37337.1 的静态研究；移动端结论依据独立证据，原生运行行为仍待验证。

## 先说结论

移动端可以继承桌面研究中的会话层级、输入工具分组、附件与交付物的区分，但必须单独研究操作系统入口、键盘、安全区和跨应用交接。目前最可靠的移动端差异来自官方操作说明；商店图片主要说明产品表达，不能支持精确原生界面还原。

视觉资料包括 13 张商店图片及 2 张官方移动语音界面裁切。13 张商店图均为宣传材料，其中五组内容在两个商店高度相近；Google Play 还包含具有 iPhone 风格锁屏线索的设备照片。因此，商店归属只能标记发布渠道，原生 UI 的平台归属须另行核对。

[完整证据账本](../../04-Extracted-Core-Code-And-Scripts/evidence/data/mobile-surfaces.json)记录图片地址、SHA-256、尺寸和观察边界。原始图片仅作私下核验，出版物不附带原图。以下编号对应证据账本，图片尺寸均指下载文件像素，不是逻辑点、dp 或 CSS px。

## 1. 对象身份与时间不能混在一起

- 标准 iOS 应用：[Claude by Anthropic，App Store ID 6473753684](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684)。观察日的页面显示版本 1.261012.20；商店图片对应的版本未标明。
- Android 应用：[Claude by Anthropic，包标识 com.anthropic.claude](https://play.google.com/store/apps/details?id=com.anthropic.claude&hl=en_US)。观察日的英文页面显示更新时间 2026-10-13；Android version code 尚未核验。
- 当前帮助文档要求 iOS/iPadOS 18+、Android 8.0+。iOS 另有组织管理用 Claude for Intune，不能混作同一分发对象。见 [iOS 安装说明](https://support.claude.com/en/articles/9266462-install-claude-for-ios) 与 [Android 安装说明](https://support.claude.com/en/articles/9612887-install-claude-for-android)。本章没有查看 iPad、Intune 或折叠屏运行界面。

必须分开记录四个时间/版本字段：页面观察日、文章发布日期、商店当前版本、截图拍摄日期。这里所有图片的拍摄日期与应用 build 均未知。CDN 路径、文件修改时间、下载时间或当前版本号都不能补上这个空白。

官方 2024 年 [iOS 发布文章](https://claude.com/resources/articles/team-plan-and-ios) 和 [Android 发布文章](https://claude.com/resources/articles/android-app) 可以支持“跨设备会话、拍照和文件输入在早期就存在”的历史结论。它们不能证明 2026 年的控件位置。返回 HTTP 403 的历史图片未纳入视觉证据。

## 2. 图片呈现的界面与交互

### 2.1 商店图是经过编排的产品场景

App Store 的五张图片为 600 × 1300；Google Play 的八张所下载图片为 333 × 592。它们并非可直接相互叠加比较的等比例截屏。

| 主题 | iOS 证据 | Android 商店证据 | 可以观察的内容 | 不能据此断定 |
|---|---|---|---|---|
| 地图回答 | MS-IOS-01 | MS-AND-02 | 浅色聊天切片、用户消息块、地图与场所卡 | 地图提供商在每次原生运行中的选择、真实卡片尺寸 |
| 语音 | MS-IOS-02 | MS-AND-03 | 人物照片与独立波形符号 | 语音会话屏幕、正在监听/说话状态 |
| 连接工具 | MS-IOS-03 | MS-AND-04 | 服务标识和宣传排布 | 连接器设置页、授权流程、原生网格 |
| 交互作品 | MS-IOS-04 | MS-AND-05 | 聊天与作品分层表达、作品切片的关闭/更多入口 | 截图内闪卡的深色与紫色属于 Claude 全局主题 |
| 附件及文件 | MS-IOS-05 | MS-AND-06 | 图片/文档缩略项、带类型的交付物卡、输入控件分组 | 完整屏幕、键盘避让、底部安全距离 |
| 任务通知 | 所查 iPhone 图集中未出现 | MS-AND-07 | 设备照片中的多条通知 | Android 通知外观；图片具有 iPhone 风格线索 |
| 任务审批 | 所查 iPhone 图集中未出现 | MS-AND-08 | 状态筛选、任务卡与 Approve 按钮 | Android 独占功能、真实审批状态机 |

来源：[App Store](https://apps.apple.com/us/app/claude-by-anthropic/id6473753684)、[Google Play](https://play.google.com/store/apps/details?id=com.anthropic.claude&hl=en_US)。表中缺项仅指所查图片集，产品能力须依据文档或运行证据判断。

多张图中的卡片越出后方聊天框，并叠在真实场景照片上，属于宣传拼贴。放大的卡片呈现产品功能而非浮层尺寸；共享构图也只支持视觉表达相近，组件库、渲染技术和代码是否共用仍待独立证据。

### 2.2 导航：保留紧凑入口，展开结构尚未验证

商店的聊天切片显示左上菜单图标，以及右上的新建样式图标和省略号，证据覆盖导航入口层。导航抽屉展开、组织切换、项目列表与完整底部导航未出现在图集中，完整原生 IA 仍待验证。来源：MS-IOS-01/04/05、MS-AND-02/05/06。

另有文本证据：移动端文件能力设置从左侧栏中的姓名/首字母进入 Settings。它证明存在这条文档化路径，并不提供侧栏宽度或展开动画。见 [Create and edit files with Claude](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)。

MS-AND-08 的 All / Blocked / In progress / Done 胶囊与任务卡，说明官方以“按状态查看工作”表达移动任务列表。它既不是实时操作记录，也没有证据证明只属于 Android。

### 2.3 Composer：语义能迁移，控件规格不能迁移

浅色宣传切片（MS-IOS-05 / MS-AND-06）把文字行放在上面，下面是工具行：左侧加号和模型胶囊，右侧麦克风与暖色圆形发送箭头。可以把它理解成“组织输入 / 发出输入”两个功能组；这是本研究的设计解释，不是源码测量。

更直接的视觉证据是官方帮助文章里的暗色移动输入框裁切（MS-VOICE-01，原证据 OV08-IMG3）：加号和调节图标在左，麦克风和高对比圆形波形按钮在右。这里麦克风与波形同时存在。官方文字把两者区分为听写和双向语音，不能合并成一个“麦克风功能”。见 [Use voice mode](https://support.claude.com/en/articles/11101966-use-voice-mode)。

浅色宣传图出现模型胶囊，暗色帮助裁切出现调节图标。两张图没有同一版本或同一账户条件，不能把差异归因于 iOS 对 Android，也不能拼成一套“当前标准工具栏”。

### 2.4 Voice：移动端有自己的控制层

帮助文档描述连续免手持与按住说话两种方式，同一会话可在文字和语音间切换。移动端在语音状态左下角进入设置，选择 voice 和 pace。官方设置裁切（MS-VOICE-02，原证据 OV08-IMG4）能直接看到顶部拖动条、分组圆角选项、亮边框选中项和底部指示条。见 [Use voice mode](https://support.claude.com/en/articles/11101966-use-voice-mode)。

可复用的交互原则是：输入模式、语音选择与节奏分别控制，且设置靠近活动会话。拖动关闭手势、横向滚动、触觉反馈、录音动效、打断延迟和后台音频能力仍需运行验证。文章仅将裁切标为 mobile，平台归属未细分到 iOS/Android。

### 2.5 键盘与安全区的待验证边界

所查图集未呈现当前系统键盘、中文输入法组合状态、焦点光标、键盘收起或 Android 返回键。语音设置图的底部指示条说明截图包含底部系统区域线索，却不能提供设备型号、屏幕比例、底部 inset 或触控命中区。

以下实现细节仍需真机验证：

- composer 是否随键盘上移、是否覆盖消息尾部；
- Enter 发送还是换行，中文候选词确认是否误发；
- 列表是否保持滚动锚点，旋转是否保留草稿；
- 原生 safe-area 数值、键盘动画曲线、手势冲突；
- 当前 iOS 与 Android 的字号、基线、系统字体名或按钮 dp。

这些是后续真机验证项目，不应从桌面响应式 CSS、移动网页或宣传图片推断。移动浏览器里的 claude.ai 也不是原生应用测试的替代品。

## 3. 附件、交付物与系统交接

输入附件与输出文件是两个不同层级。宣传图将照片缩略图、DOC/PDF 文件项放在用户消息附近；回答中的 PPTX 则有标题和文件类型。输入提供上下文，输出是可打开的工作成果。这里只迁移语义，不迁移卡片宽度、阴影或内边距。

移动端的关键差别在交接之后：官方文档明确说，点 Download 会打开系统预览或另一应用，而不是保证留在 Claude 内。Design 的移动端文档则说明可在 Artifacts 中全屏查看并编辑设计，修改共享设置需到 web/desktop。两者需要分别建模为“系统文件交接”与“应用内作品查看”。见 [文件创建](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)、[Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)。

示例作品里的深色卡片、紫色反馈按钮或地图颜色可能属于生成内容或第三方地图。品牌 token 的归属应区分宿主应用、生成作品与第三方内容。

## 4. iOS / Android 差异主要出现在系统边界

| 能力边界 | iOS 文档 | Android 文档 | 研究含义 |
|---|---|---|---|
| 短信与邮件 | 预览后打开目标应用，由用户检查发送 | 通过系统分享/intent 打开目标应用，由用户检查发送 | 会话卡片不是最终发送界面 |
| 提醒/时间工具 | 支持已有列表中的提醒事项 | 文档列出闹钟、计时器；不支持 iOS 提醒事项功能 | 不应强制两端同一工具目录 |
| 外部启动 | Ask Claude intent、Siri、Spotlight、Share、Shortcuts，以及系统相机入口 | 主屏 widget 的聊天、拍照、听写入口 | 移动入口不只存在于应用内部 |
| Widget | 新聊天、听写、拍照 | 新聊天、听写、拍照，可调整 widget 大小 | 听写入口不等于双向语音会话 |
| 权限 | 系统分享及按需系统权限 | 系统分享/intent 及按需系统权限 | 拒绝权限、回到 Claude 的路径要单独测试 |

来源：[iOS 系统应用](https://support.claude.com/en/articles/11869619-use-claude-with-ios-apps)、[Android 系统应用](https://support.claude.com/en/articles/11869629-use-claude-with-android-apps)、[iOS intents / widgets](https://support.claude.com/en/articles/10263469-use-claude-app-intents-shortcuts-and-widgets-on-ios)、[Android widget](https://support.claude.com/en/articles/10534883-use-the-claude-widget-on-android)。

两端文档还分别说明健康数据集成；它们有套餐、地区和系统条件，不能因为商店描述出现健康场景就认为每个账户可用。两端系统应用文档均说明不直接访问通讯录，Team/Enterprise 的 location tool 也有当前限制。此处仅用于界面能力边界，不是对数据访问或健康功能的实测。

## 5. “移动工作区”需要拆开谈

项目、组织账户、Code 仓库与设备本地目录分别具有不同的上下文和访问边界，需按对象区分 workspace 的含义。

1. 会话与任务：2026-09-16 发布说明记录了合并 Chat/Cowork 的分批推出。当前帮助文档强调同一套餐的账户也可能处于不同阶段；手机可查看、继续或发起云端任务。涉及用户电脑文件、浏览器或 computer use 的任务仍依赖运行中的 Desktop。见 [发布说明](https://support.claude.com/en/articles/12138966-release-notes)、[统一体验](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)。
2. 项目：统一体验文档将其描述为文件、指令和相关工作上下文的集合。移动项目创建、移动/归档及组织切换的运行界面仍待独立核验。
3. Code 会话：官方移动深链接支持会话列表、已有会话和新会话预填，要求账户有 Code 权限。问题、仓库、分支与模式是文档化参数；桌面的 folder/file 参数会被忽略。因此手机入口不能等同于获得手机或桌面本地目录访问权。见 [移动深链接](https://support.claude.com/en/articles/14898120-open-the-claude-mobile-app-with-a-link)。
4. 组织能力：角色限制在服务端执行。官方特别指出，移动端被禁用的 connector tool 可能仍显示为可用，但调用会被拒绝。这是“看起来打开”不等于“确实能执行”的具体例子。见 [Enterprise 自定义角色](https://support.claude.com/en/articles/13930452-manage-custom-roles-on-enterprise-plans)。

这些文档描述功能与边界；实际账户的 rollout 状态，以及 Desktop 2.37337.1 静态 bundle 中各路径是否生效，仍须分别核对。

## 6. 已有明确文档的移动限制

- Enterprise search 的专用搜索项目不能在 iOS/Android 使用。这不等于所有连接器搜索都不能用。见 [Enterprise search](https://support.claude.com/en/articles/12489464-use-enterprise-search)。
- 给指定人员发起聊天共享仍限 web；移动端可打开收到的共享会话。不要将“能查看分享”写成“能配置分享”。见 [指定人员共享](https://support.claude.com/en/articles/16762496-share-a-chat-with-specific-people)。
- 手机可使用 web connectors，移动端新装连接器为 beta；自定义连接器以 web/desktop 为主要设置路径。Desktop extensions 是另一层，不应等同于移动端连接器。见 [连接器](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)。
- Design 的移动端查看/编辑与共享设置权限不同，后者需 web/desktop。见 [Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)。

这些限制以 2026-10-14 打开的文档为准，今后可能变化。商店评论不是本章能力判定依据；不能用单条评论替代官方说明或受控实测。

## 7. 从桌面研究迁移什么

| 可迁移的研究模型 | 必须重新验证的移动实现 |
|---|---|
| 用户输入、模型回答、工具结果、交付物之间的层级 | 原生字体、缩放、内边距、圆角及精确颜色 |
| 输入上下文与发送/语音动作的分组 | 键盘、输入法、safe-area、硬件返回键与手势 |
| 附件身份、文件类型、打开/下载的语义 | 系统照片/文件选择器及预览/分享返回路径 |
| 同一会话延续不同输入模式 | 音频中断、蓝牙切换、后台/锁屏恢复 |
| 任务状态、需要人决定的动作显著化 | 通知深链接、权限拒绝、离线及重连恢复 |
| 账户/项目/会话的概念区分 | 手机上的具体导航层级及不同 rollout 状态 |

共享产品概念可以迁移；移动端由系统拥有的界面、生命周期与权限状态需要独立实现和验证。

## 8. 可复用的下一轮原生验证清单

本章的取样范围为公开文档与图片，未安装或运行目标移动应用，未登录账户、读取私有会话或提取 IPA/APK。

以下为待执行的原创验证计划。取得合适授权和可用设备后，应使用合成消息、测试文件和测试账户，并记录 app build、OS、设备、语言、套餐与 rollout 状态。

| 场景 | 应记录的状态 | 要回答的问题 |
|---|---|---|
| 中英文长输入 | 空白、聚焦、输入法组合、换行、发送后 | 是否误发、遮挡、丢草稿或丢滚动位置？ |
| 键盘收起/旋转 | 键盘打开、关闭、横屏、返回竖屏 | 输入与消息尾部是否可达？ |
| 附件 | 拒绝照片权限、选择多项、取消选择、上传中、失败 | 用户是否知道哪些附件真的进入消息？ |
| 语音 | 未授权、免手持、按住说话、切换文字、音频中断 | 输入模式与录音状态是否清晰？ |
| 输出文件 | 文件卡、系统预览、外部打开、返回 Claude | 是否保留会话位置与文件身份？ |
| 项目/组织/Code | 切换前后、无权限、失效会话、预填仓库 | 能否明确当前上下文和执行位置？ |
| 任务审批 | 等待决定、同意、拒绝、过期、网络断开 | 是否存在重复动作或过时批准？ |
| 访问性 | 大字、读屏、深浅主题、外接键盘 | 控件名称、焦点顺序和触摸区域是否可用？ |

现有证据支持带来源和待验项的移动交互模型；原生控件尺寸与精确视觉规范须在真机验证后补全。

本卷没有原生实现或已执行的移动端测试。要查其他卷的模型与输入要求，可用[19 卷代码与测试导航](../../04-Extracted-Core-Code-And-Scripts/book-code-navigation.md)；下面的实验室链接是桌面机制的参考入口，不是本卷的真机验收结果。

[返回全书目录](../README.md) · [阅读前提与术语](../README.md#一页阅读准备) · [原创代码实验室](../../04-Extracted-Core-Code-And-Scripts/core-code-lab/README.md)
