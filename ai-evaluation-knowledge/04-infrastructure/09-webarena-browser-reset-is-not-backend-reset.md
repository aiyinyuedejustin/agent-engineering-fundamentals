# WebArena：browser reset、backend reset 与并行隔离不是同一件事

研究日期：2026-11-06。学习目标：L2 → L3。

证据深度：官方任务 JSON 与环境配置 D2，browser setup/reset、runner、并行脚本和重试清理路径 D3。进行了静态 JSON 字段统计，**没有启动浏览器或网站，没有访问示例账号，没有 reset 或修改任何服务，不声明环境运行 D4**。

固定版本：`web-arena-x/webarena` commit `dce04686a56253aefba7b18a4fa0937cf1dc987b`，提交日期 2025-11-26，2026-11-06 读取。官方 README 说明它是复现论文的 canonical implementation，同时自2024-12-05起推荐 AgentLab/BrowserGym 进行新实验。本文分析原实现，不把结论自动推广到新框架。[W1]

BrowserGym 本身的 reset/step 与 task validation 调用路径另见 [computer-use source traces](../05-agent-runtime/computer-use-source-traces.md)；backend reset 不应仅由该统一接口名称推断。

## 1. 真实环境有不止一个状态拥有者

WebArena 包括购物、购物管理、论坛、GitLab、百科与地图等服务。浏览器只是其中一个客户端，登录 cookie、服务数据库、Git repository、商品库存/收藏和服务配置分别有自己的生命周期。[W1、W2]

```text
Agent state / trajectory
  → browser process + context + pages + storage_state
      → shared service endpoint
          → backend process + database / repository / uploaded content

Judge
  → final browser state and/or authoritative backend page/content
```

一个新浏览器可以登录到已经被前一任务修改的同一个账户。新 cookie 不意味着新账户，新 context 也不意味着新数据库。

## 2. env.reset 的确切源码路径

`ScriptBrowserEnv.reset()`：[W3:L185–221]

1. 调用 Gym 的 reset；
2. 如果之前已 reset，退出旧 Playwright context manager；
3. 读取 config_file，调用 setup；
4. 标记 reset_finished；
5. 可等待配置的间隔，然后返回 observation 与 metadata。

`setup()` 创建新的 Playwright/Chromium browser，然后创建 browser context，载入任务的 `storage_state`、viewport、geolocation，打开 start_url；可启用 tracing 和 accessibility tree。[W3:L125–169]

**所读路径没有 backend/database reset 操作。** 它也没有把 `require_reset` 任务字段转化为服务重置。这里是固定源码局部路径的结论，不是说任何 WebArena 外部部署都不做 reset。

## 3. backend reset 是独立的部署操作

官方 Docker/AMI 文档明确在评估812个 examples 后重置环境：停止并移除 shopping、shopping_admin、forum、gitlab 容器，从初始镜像重新启动，再执行相关配置步骤。[W2:L108–119]

README 还要求正式评估使用自建网站，公开 demo 仅供浏览理解。[W1: End-to-end Evaluation]

注意文档中的 “remove the images” 注释下面实际调用的是 `docker remove`，删除的是 container，不是 `docker image rm`。把“从初始镜像重建容器”误写成“删除初始镜像”，会误解 reset 的成本和语义。[W2]

**推论：** 如果自行加了持久 volume、改了数据库位置或把服务拆到别处，停止/重建原来的 container 不保证恢复相同数据。应对实际存储拓扑验证 reset，不只复制命令。

## 4. 一个字段不等于一个保证

对固定 `config_files/test.raw.json` 的812条记录做统计，全部 `require_reset=false`。已读 `run.py` 与 `browser_env/envs.py` 都没有使用这个字段。[W4；静态审计附件]

但“false”不能解读为任务都是只读。例如任务441–445：

- 都访问同一个 GitLab project；
- 都要求修改网站 title；
- evaluator 都读取同一个 `main/index.html` raw resource；
- 各自期待不同 title；
- 该字段仍全部为 false。[W4]

这不证明原 benchmark 设计错误。它证明 metadata 名称不能替代对状态、执行代码与 protocol 的检查。backend reset 粒度可能是整套 evaluation，而不是单个 task。

静态结果保存在 [webarena-reset-static-audit.json](evidence/webarena-reset-static-audit.json)，只保留计数、任务ID与资源定位，不复制完整812题答案集。

## 5. 并行的 unit 是浏览器，还是完整环境？

canonical `parallel_run.sh` 将 task index 范围分给多个 tmux pane，但使用同一个 SERVER 形成共享网站 endpoints。同一 worker 顺序执行其配置列表；脚本并未为每个 worker 创建独立 backend 数据副本。[W5]

重要限定：441–445在给定脚本的同一个380–480 shard，**不能据此说官方默认脚本会让这五题并发冲突**。如果改为按题随机分片、同时跑多个模型或并行做同题多样本，则共享资源的访问关系需要重新分析。

共享后端的潜在问题包括：

- 一个 sample 改写另一个 sample 的待评估对象；
- 同一账号的收藏、issue、commit、会话或通知积累；
- evaluator 读到的状态已不是被评 sample 刚完成的状态；
- reset 一个服务时中断其他活跃 sample。

这些是由架构与任务资源重合推导的风险，不是本轮测得的错误率或既有排行榜缺陷。

## 6. 重试恢复了输出文件，不一定恢复了任务世界

`run.py` 每题可先执行 auto_login 更新 cookie，再 `agent.reset()` 与 `env.reset()`。它在结果目录保存 render HTML；`get_unfinished()` 根据这些 HTML 文件判断哪些题还需运行。[W6:L243–282、L393–403]

并行脚本会调用 `check_error_runs.py --delete_errors`，删除未完整记录、发生未处理异常或检测到意外登出的 render 文件，然后重跑对应范围。该路径清理的是完成标记/输出文件，没有伴随 backend reset。[W5:L43–67；W7]

**工程推论：** 如果第一次尝试已经部分修改服务，第二次尝试可能从不同初始状态出发。删除失败日志或完成标记不能撤销网站上的副作用。应保留 attempt identity、第一轮状态与重试原因，不要把 retry 简化成“同一次实验再试一下”。

另一个统计边界：`run.py` 只有 evaluator 正常返回才 append score；API/其他异常只记日志，结尾的本地平均值使用已 append 的 scores。这个日志平均值不自动代表所有计划任务的总分。外层重试与最终统计可能进一步处理它，所以本文不推断已发布论文分数受影响。[W6:L330–365]

## 7. cloud 部署建议仍需自己的威胁模型

原部署文档提供 public AMI 与网站端口配置，其中示例允许从广泛来源访问多个服务端口。[W2:L17–35]

这适合解释其可连接假设，但不应无审查地复制到含真实数据、私密凭据或共享生产网络的环境。研究环境应使用合成账号/数据，限制入口到已授权 clients，明确出入口、管理接口和云身份边界。本文没有创建实例、改 security group 或登录任何服务。

AMI、Docker images 与地图 backend 也有独立版本/区域/地址要求。仅固定 browser_env 的 Git commit，无法保证完整网站状态一致。

## 8. 最小实机验证计划，尚未执行

应在专用、可销毁的测试服务上进行：

1. 保存 backend 初始 fixture 的版本与可验证摘要，确认浏览器初始 storage_state 对应正确用户。
2. 用无害 marker 写入模拟服务，调用 browser reset，检查 marker 是否仍存在；然后执行实际 backend reset 再比较。
3. 用两个隔离客户端操作同一个合成记录，记录 action 与 judge 读取的时序；再用独立 backend 副本作对照。
4. 在写入后、正常结束前注入可控失败，按原 retry 路径重跑，检查是否从相同 baseline 开始。
5. 将 per-task、per-shard、per-model、whole-suite 四种 reset 粒度分别标注，不未经说明混入同一分数。

若为提高隔离而改为每题重置，必须披露这与 canonical protocol 的差异。更强隔离不自动保证与历史结果可比。

## 9. 学习检查

- 在一项网站操作任务中，哪些状态由 browser 持有，哪些由 backend 持有？
- 为什么重新登录不是 reset，为什么删除失败 HTML 也不是 rollback？
- 如果原顺序执行改为随机并行，你需要重新验证哪些资源冲突？
- “require_reset=false”能证明什么，不能证明什么？

## 来源

以下均固定 `dce04686a56253aefba7b18a4fa0937cf1dc987b`，2026-11-06 阅读。无精确 fetch 时刻记录。

- [W1] [README](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/README.md)，canonical/new-framework 建议、正式网站要求与总体流程。
- [W2] [environment_docker/README.md](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/environment_docker/README.md)，读取 AMI/网络/启动与reset相关段落；未实际执行所含命令。
- [W3] [browser_env/envs.py](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/browser_env/envs.py)，setup/reset/close L125–229。
- [W4] [config_files/test.raw.json](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/config_files/test.raw.json)，blob `6649a867e5d7c7da7e6f69c86d2ffdb505fb12d3`；解析812条 metadata，并完整阅读所选441–445与552配置，不声明人工逐题审计全部任务。
- [W5] [parallel_run.sh](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/parallel_run.sh)，全文。
- [W6] [run.py](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/run.py)，test循环、retry完成标记与main相关路径。
- [W7] [scripts/check_error_runs.py](https://github.com/web-arena-x/webarena/blob/dce04686a56253aefba7b18a4fa0937cf1dc987b/scripts/check_error_runs.py)，全文，只读未运行。
