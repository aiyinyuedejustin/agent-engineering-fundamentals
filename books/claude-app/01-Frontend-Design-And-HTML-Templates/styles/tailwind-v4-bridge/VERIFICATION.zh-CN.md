# 验证记录

核验日期：2026-10-15。范围限定为 Tailwind 3.4.19 与 4.3.3，没有扩展版本矩阵。

## 最终保留的桥接

- 官方 npm registry 查询后固定 v4 CSS/CLI 4.3.3、v3 3.4.19，使用 `--ignore-scripts --no-audit --no-fund` 隔离安装，没有改 publication 依赖。
- 最终主流程只编译 **v4 默认语义夹具与 v3 原配置快照夹具**，均退出 0。
- **36 项编译/静态断言通过**：语义色、字体、圆角、高度、阴影的局部变量引用；v4 语义间距；默认桥接不引入 dark/scope；撤回增强不可导入；v3 selector dark；无全局 Preflight reset；CSS/JSON palette 一致；快照未改；MIT banner 与无外部资源夹具。
- v3 的 `preflight: false` 经包含 `@tailwind base` 的真实入口验证。v4 则从入口省略 Preflight 导入，不依赖 v3 JS 配置。生成的 `--tw-*` 初始化不是全局 reset。
- 独立 cloud Chrome 检查了默认页的 **14 个节点**：嵌套主题颜色、局部字体与圆角、控件高度、间距及容器外原生 margin/list/box 值符合预期。此结论限定本次页面和浏览器。

最终机器结果：`verification/results.json`。真实浏览器原始报告完整复制在 `verification/browser-results.json`，对应固定提交 `886d74eb6668a19456734aabdb7844496abbeead`。默认适配器和 base 夹具没有因撤回实验而变化。

写入安全复验另见 `verification/write-safety.json`：已有输出目录被拒绝，失败重跑不改现存报告，独占临时目录清理；当时审查原件与六模板哈希一致。四个只读审查快照在 `tests/reference/`；`publication-readonly-baseline.json` 供比对。

## 已失败并撤回的 scoped-dark 实验

浏览器的 13 项背景检查中 **4 失败、9 通过**，不能称为全部通过。四个预期 `rgb(241, 173, 165)` 的节点实际仍是画布色：

- `dark-root`、`dark-child`：`rgb(27, 27, 24)`
- `nested-dark-root`、`nested-dark-child`：`rgb(23, 33, 39)`

CSSOM 实际读到 scope-start 的 `&` 前缀，确认它相对外层工具类解析；直接 scoped declarations 又不是预想的工具类后代规则。已撤去可导入增强、入口推荐与主测试的假阳性结构断言。源码、原生成 CSS/HTML 和旧 40 项静态结果保留在 `regressions/scoped-dark-negative/`，明确作为失败证据。旧静态通过不覆盖真实浏览器失败。

CSSOM 已解析 scope，不能依据工具环境的 `typeof CSSScopeRule` 返回值推断浏览器不支持。详见 `verification/scoped-dark-withdrawal.json` 与负例说明中的规范和上游记录。

## 范围限制

主测试不启动浏览器。默认页的 `tests/browser-checks.js` 可供浏览器控制台只读复验，不嵌入页面。本次未覆盖 Firefox/Safari、旧浏览器、系统偏好自动切换、框架集成、Portal/Shadow DOM、全部变体组合、alpha 修饰、完整应用视觉回归或原六模板全场景回归。不承诺 v3/v4 无损兼容。

## 复跑

准备两个独立目录，按 `verification/v4.package.json`、`v3.package.json` 与相应锁文件安装。锁文件均来自官方 registry；建议在各自目录运行 `npm ci --ignore-scripts --no-audit --no-fund`。随后：

```sh
TAILWIND_V4_DIR=/absolute/path/to/v4-toolchain \
TAILWIND_V3_DIR=/absolute/path/to/v3-toolchain \
node tests/verify.mjs --output /absolute/path/to/new-report-directory
```

两个环境变量都必须显式设置。两个工具目录分别把相应 `v4.package.json` / `v3.package.json` 及锁文件命名为 `package.json`、`package-lock.json` 后安装。`--output` 指定的结果目录必须尚不存在，父目录须已存在；若省略该参数，脚本在交付目录独占创建 `verification-run-*`。现有报告或无关文件不会被覆盖。测试会在 v4 工具目录内用 `mkdtemp` 独占创建临时目录以解析依赖，并在 `finally` 只清理本次创建的临时目录；不复用或删除固定 `work/`，不修改原配置或模板。本交付的 `verification/` 是整理后的本次报告，不是默认覆盖目标。它编译 `tests/reference/tailwind.config.js` 的原字节快照，仅以 CLI `--content` 指定回归夹具。默认的源扫描范围另由原配置负责，不能据此说整套应用内容扫描已通过。
