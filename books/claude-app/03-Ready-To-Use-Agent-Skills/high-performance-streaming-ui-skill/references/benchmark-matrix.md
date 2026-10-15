# 基准与验收记录模板

## 环境

记录构建 commit、设备/CPU、浏览器版本、显示刷新率、视口、输入法、主题、冷/热缓存、网络与 CPU 节流。使用合成正文，不上传用户私聊。

## 工作负载

- 段落：短块很多、超长单块、空白、混合 Unicode 与 grapheme
- Markdown：半个 fence、列表嵌套、表格增长、晚到引用定义、修正前缀
- Rich：代码长行、语法注册失败、主题切换、数学插件失败、图表超限/卡住
- Arrival：固定小包、突发、暂停后追赶、终止/回撤/abort 同一个 chunk
- UX：同时打字、拖选、读旧内容、调整窗口、复制、搜索、打印
- Lifecycle：隐藏/恢复、卸载再挂载、离开会话、Worker late reply、资源重复清理

## 结果

每个 case 记录 receive、commit、visible、formatted 各边界；median/p95（说明样本数和统计方法）、最长 task/frame、最大 backlog、final source equality、fallback cause、retained heap 与活动资源数。

不得用一次平均值证明全部 case；不得把不存在的浏览器 API 当成测量零值。显式列出 never-run 项。

## 停止条件

正确性失败、用户输入长期饥饿、正文丢失、旧页面回写、不可释放任务、非授权内容上传，优先于性能分数。先恢复 plain fallback 与资源边界，再继续优化。
