# 验证记录

核验日期：2026-10-15。范围限定为 Tailwind 3.4.19 与 4.3.3，没有扩展版本矩阵。

## 已通过

- 官方 npm registry 查询：v4 CSS 与独立 CLI 的 latest 标签均为 4.3.3；v3-lts 为 3.4.19，并再次查询该精确版本存在。
- 安装固定版本，使用 `--ignore-scripts --no-audit --no-fund`，分别放在独立工具目录，不改变六套模板的零依赖入口。
- v4 默认语义夹具、v4 可选 dark 夹具、v3 原配置快照夹具均实际 CLI 编译，退出码 0。
- 40 项自动断言通过：语义色、三类字体、三种圆角、最小高度和阴影直接引用局部变量；v4 语义间距；默认桥接未引入作用域变体；可选作用域的精确选择器；v3 selector dark；无全局 Preflight reset；CSS/JSON 五套浅深 palette 一致；快照未改；v4 banner 保留；验收页无脚本与外部资产。
- v3 的 `corePlugins.preflight = false` 经含 `@tailwind base` 的真实入口验证。生成的全局规则只含工具类运行所需的 `--tw-*` 初始化，不能把它们误判成全局 reset。
- v4 的关闭方式在入口层移除了 Preflight 导入，不依赖 v3 JS 配置。

另有写入安全复验：拒绝已存在的输出目录、被拒绝的重跑不改任何报告字节、独占临时目录已清理，审查原件与六模板哈希仍一致。见 `verification/write-safety.json`。

机器结果：`verification/results.json`。生成的 CSS、工具清单与锁文件都在 `verification/`。`tests/reference/` 是本次只读审查的四个文件快照；`publication-readonly-baseline.json` 记录审查资产与六个模板的 SHA-256，用于比对审查输入。

## 浏览器状态与边界

编译验收与浏览器验收分别记录；当前文件仅确认编译与静态断言。浏览器计算样式结果完成后单列保存。

默认页 `base.compiled.html` 覆盖浅→深→浅→深嵌套，内层局部字体、圆角、画布覆盖，以及外部标题、按钮、列表、盒模型不被 reset 的检查。

可选页 `dark.compiled.html` 覆盖 dark 根本身、后代、内层 light、再次 dark、新的默认 atelier 根、错误大小写和无关组件。`tests/browser-checks.js` 是供控制台执行的一次性只读检查表达式，不嵌入页面。

当前不覆盖：Firefox/Safari、旧浏览器、自动跟随系统偏好、框架集成、Portal/Shadow DOM、所有变体组合、alpha 修饰、完整应用视觉回归或原六模板全场景回归。作用域增强不构成默认兼容性承诺。

## 复跑

准备两个独立目录，按 `verification/v4.package.json`、`v3.package.json` 与相应锁文件安装。锁文件均来自官方 registry；建议在各自目录运行 `npm ci --ignore-scripts --no-audit --no-fund`。随后：

```sh
TAILWIND_V4_DIR=/absolute/path/to/v4-toolchain \
TAILWIND_V3_DIR=/absolute/path/to/v3-toolchain \
node tests/verify.mjs --output /absolute/path/to/new-report-directory
```

两个环境变量都必须显式设置。v4 工具目录须以 `v4.package.json` 和 `v4.package-lock.json` 分别命名为 `package.json`、`package-lock.json`；v3 目录同理。`--output` 指定的结果目录必须尚不存在，父目录须已存在；若省略该参数，脚本在交付目录独占创建 `verification-run-*`。现有报告或无关文件不会被覆盖。测试会在 v4 工具目录内用 `mkdtemp` 独占创建临时目录以解析依赖，并在 `finally` 只清理本次创建的临时目录；不复用或删除固定 `work/`，不修改原配置或模板。本交付的 `verification/` 是整理后的本次报告，不是默认覆盖目标。它编译 `tests/reference/tailwind.config.js` 的原字节快照，仅以 CLI `--content` 指定回归夹具。默认的源扫描范围另由原配置负责，不能据此说整套应用内容扫描已通过。
