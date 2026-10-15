# Native / Voice / Vision 原创实验

这是一组无依赖、可重复执行的教学模型。所有输入都是合成样本；不会启动 Claude、访问账户、注册快捷键、读取剪贴板、采集麦克风或执行原生模块。

## 运行

需要支持 ES modules 与 `node:test` 的 Node.js：

```sh
node --test --test-reporter=tap models.test.mjs
node examples.mjs
```

本次验证：61 个测试通过，0 个失败。PDF 变换属性测试包含 360 组正向/逆向 round trip。`worked-examples.json` 保存数值示例。

## 文件

- `geometry.mjs`：display frame、负显示器原点、window-local、仿射矩阵、PDF viewBox、rotation、userUnit、DPR。
- `audio-state.mjs`：RMS、PCM16 little-endian、固定采样率分帧、按时间平滑的包络、播放样本账本、epoch guard。
- `native-state.mjs`：编辑对象身份、snapshot 作用域/有效期、快捷键失败补偿、显式 connector owner。
- `examples.mjs`：完整帧中点、边界夹取、PDF 旋转矩形、320 样本/640 字节 PCM 帧与 10 ms 已播放音频。
- `models.test.mjs`：正常、边界、竞态、失败恢复与生成式几何用例。
- `diagrams/`：六份原创 Mermaid 源图，可在支持 Mermaid 的 Markdown 环境中渲染。

## 模型与目标实现的区别

1. geometry 实验强制匹配 capture identity；目标的 display 转换还存在无 prior screenshot 的警告回落，实验没有复制它。
2. window 点在实验中严格拒绝越界；目标所读 Qt helper 采用夹取。
3. PDF lab 是通用原创矩阵实现。只在 Office MCP 依赖里找到 viewport 数学，未证明它驱动聊天 PDF 高亮。
4. PCM assembler 不做重采样、不实现 codec；包络参数也是原创选择。
5. PlaybackLedger 不实现完整 worklet residual-sample 协议，不是实时音频引擎。
6. VoiceEpoch 只演示过期异步事件隔离，不模拟服务器 VAD 或完整网络恢复。
7. SnapshotAuthority 的显式 grantVersion/expiry 是原创强化，不宣称是目标结构。
8. ShortcutLease 使用 fake registry，不读取或改变系统按键。

出版边界：可以分发这里的原创文件与精简事实证据；不得加入下载的安装包、提取的私有 bundle、native binaries、完整 REA 图或任何真实音频/用户信息。
