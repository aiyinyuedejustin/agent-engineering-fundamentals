[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="topic-06"></a>

## 6. 执行环境：命令在哪儿跑，资源归谁收尾

<a id="durable-orchestration-043"></a>

### durable-orchestration-043 · feat(tools): run sync tools in a thread

作者／组织：Deepankar Mahapatro and OpenAI Agents SDK maintainers。类型：公开变更／提案。版本／日期：opened2025-06-07; closed stale2025-08。读取日：2026-10-13。

用途：async外层调度不让同步requests工具自动非阻塞；一个阻塞函数可让同event-loop的其他agent停顿。

选读范围：PR discussion default to_thread versus opt-in wrapper。限制：未合并历史PR，不声称当前SDK默认；评论示例有def/await笔误不可复制

[公开原文](https://github.com/openai/openai-agents-python/pull/820)

<a id="durable-orchestration-055"></a>

### durable-orchestration-055 · We ditched worktrees for Claude Code. Here's what we use instead

作者／组织：Eric Allam。类型：作者／团队实践或研究文章。版本／日期：2026-04-16。读取日：2026-10-13。

用途：worktree只隔离源码，不隔离Postgres迁移、Redis、测试数据、端口与构建环境；并行成本来自完整环境。

阅读范围：文章中 worktree 与共享服务隔离的讨论，以及结尾的重叠文件和副作用测试边界。限制：单团队经验，GitButler不是通用替代方案；第三方磁盘数字未独立核验不采用

[公开原文](https://trigger.dev/blog/parallel-agents-gitbutler)

<a id="durable-orchestration-059"></a>

### durable-orchestration-059 · Crab: A Semantics-Aware Checkpoint/Restore Runtime for Agent Sandboxes

作者／组织：Tianyuan Wu, Chaokun Chang, Lunxi Cao, Wei Gao, Wei Wang。类型：研究论文。版本／日期：v1 2026-04-30。读取日：2026-10-13。

用途：会话+文件仍可能遗漏后台进程；恢复状态范围应由后续工具依赖决定，不能一律说history足够或全VM必需。

选读范围：论文摘要、Sections 2–4、5.1、5.2 开头、6、7.1–7.2；未读完整组件评测。限制：100个先筛选无故障可解任务、记录轨迹确定性回放和单次注入崩溃；100%仅该实验，不是外部副作用或任意工作负载保证；论文未说明remote effect回滚，不能推广

[公开原文](https://arxiv.org/abs/2604.28138)

<a id="network-errors-027"></a>

### network-errors-027 · Python asyncio subprocesses

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：Process.wait遇子进程写满stdout/stderr PIPE可deadlock；communicate避免此情况但把输出缓存在内存。

选读范围：Process wait/communicate/terminate/kill/pid。限制：只读Interacting with Subprocesses等相关节；终止整个进程组的方案需另有OS依据。

[公开原文](https://docs.python.org/3/library/asyncio-subprocess.html)

<a id="network-errors-029"></a>

### network-errors-029 · AnyIO working with threads

作者／组织：AnyIO maintainers。类型：官方文档／规范。版本／日期：unknown。读取日：2026-10-13。

用途：abandon_on_cancel=True只停止等待并忽略结果，线程继续跑；线程取消须业务代码主动check_cancelled。

选读范围：full page Running function / limiter / Reacting to cancellation。限制：线程数是当前库默认，不应作为所有harness建议值。

[公开原文](https://anyio.readthedocs.io/en/stable/threads.html)

<a id="network-errors-030"></a>
<a id="tools-security-024"></a>

### network-errors-030 · subprocess — Subprocess management — Python 3.15.0 documentation

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3 docs retrieved 2026-10-13。读取日：2026-10-13。 引用别名：tools-security-024（本组合计 1 项，关联文档与版本复核不另计）。

用途：wait 配合未消费 stdout/stderr PIPE 可死锁；communicate 防 pipe 死锁但将输出缓存在内存，无限日志仍会耗尽资源。

选读范围：subprocess Security Considerations, Popen wait/communicate/kill, process groups。限制：与具体 Python 版本、OS 有关；只读取相关段落。

已读关联文档／版本（同一计数组）：
- network-errors-030：unknown；范围：Popen.communicate/terminate/kill/pid sections。[该记录原文](https://docs.python.org/3/library/subprocess.html)
- tools-security-024：Python 3 docs retrieved 2026-10-13；范围：subprocess Security Considerations, Popen wait/communicate/kill, process groups。[该记录原文](https://docs.python.org/3/library/subprocess.html)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.python.org/3/library/subprocess.html)

<a id="network-errors-033"></a>

### network-errors-033 · Claude Code #84647: Bash timeout leaves runaway child

作者／组织：trof3039; bobleer。类型：公开问题讨论。版本／日期：unknown。读取日：2026-10-13。

用途：报告超时和子agent完成后ugrep仍跑15分钟占约20GB；curl限时和head收尾并未限制中间grep。

阅读范围：full issue and timeline2026-08-06 through stale-close2026-10-05。限制：用户事故报告未独立重跑；issue因stale关闭并非修复，平台差异需说明。

[公开原文](https://github.com/anthropics/claude-code/issues/84647)

<a id="practitioner-lessons-003"></a>

### practitioner-lessons-003 · Why We Built Our Own Background Agent

作者／组织：Ramp Builders。类型：作者／团队实践或研究文章。版本／日期：unknown。读取日：2026-10-13。

用途：事实：每30分钟构建完整开发环境快照；会话恢复用完成时快照；同步最新代码时允许先读，但阻塞写编辑直到同步完成。

选读范围：Sandbox; API; Slack（正文前16000字符）。限制：阅读正文前16000字符至Chrome extension；提前读可能观察旧版，需写入屏障及失效检查；作者对模型自控子agent数量的建议不构成预算保证。

[公开原文](https://builders.ramp.com/post/why-we-built-our-background-agent)

<a id="practitioner-lessons-010"></a>

### practitioner-lessons-010 · Enabling Agent 3 to Self-Test at Scale with REPL-Based Verification

作者／组织：Peter Zhong; Jacky Zhao; Ryan Carelli / Replit。类型：作者／团队实践或研究文章。版本／日期：2025-12-15。读取日：2026-10-13。

用途：事实：遇到外观可用但事件处理/数据未接线的界面后，构建持久JS REPL+Playwright，交替探索DOM与执行测试。

选读范围：Verification Spectrum; Code use; Putting the REPL back。限制：读前12500字符至More state information；持久变量不是持久化恢复承诺；把多个副作用合入代码仍须考虑中断后的部分完成。

[公开原文](https://replit.com/blog/automated-self-testing)

<a id="practitioner-lessons-014"></a>

### practitioner-lessons-014 · Warp scores 71% on SWE-bench Verified

作者／组织：Ben Navetta / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-06-23。读取日：2026-10-13。

用途：事实：同一agent执行长命令时切换到输入/读取输出的受限工具集，保持上下文，解决git pager卡住。

阅读范围：Long-running commands; Editing; Model Choice。限制：模糊匹配有误改风险；原文结论为当时模型组合且MCP/web在eval中关闭。

[公开原文](https://www.warp.dev/blog/swe-bench-verified)

<a id="practitioner-lessons-016"></a>

### practitioner-lessons-016 · How we scored #1 on Terminal-Bench (52%)

作者／组织：Jack Nichols / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-06-25。读取日：2026-10-13。

用途：事实：旧工具在vim等交互命令中只能等人退出，自动评测超时；新工具周期读取PTY并允许写字节，运行期间禁止冲突的新命令和编辑。

阅读范围：Model experimentation; Long-running command support; Planning。限制：仅Terminal-Bench v0.1.1及指定模型；不能推导规划总有效或Opus普遍较差。

[公开原文](https://www.warp.dev/blog/terminal-bench)

<a id="practitioner-lessons-017"></a>

### practitioner-lessons-017 · Architecting Fast, Secure Cloud Sandboxes for AI Development with Namespace

作者／组织：Ben Navetta / Warp。类型：作者／团队实践或研究文章。版本／日期：2025-12-15。读取日：2026-10-13。

用途：事实：agent工具以sidecar volume挂入用户镜像，避免每个基础镜像安装整个runtime；由harness团队独立更新。

阅读范围：Cloud-hosted agents; Securing cloud sandboxes。限制：厂商架构自述；sidecar自动最新版影响复现，不能读成版本固定或已完成egress限制。

[公开原文](https://www.warp.dev/blog/secure-cloud-sandboxes-for-ai-dev-with-namespace)

<a id="practitioner-lessons-023"></a>

### practitioner-lessons-023 · The Bitter Lesson of Agent Frameworks

作者／组织：Gregor Zunic / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2026-01-16。读取日：2026-10-13。

用途：事实：抛弃复杂message manager后，开放CDP+extension控制；浏览器状态只保留最近N份，接受部分cache损失。

阅读范围：Why we threw everything away; Ephemeral messages; for-loop doesn’t work。限制：作者“99%在模型”“无需guardrail”是观点，正文仍承认安全、重试、压缩和显式停止；不是安全保证。

[公开原文](https://browser-use.com/posts/bitter-lesson-agent-frameworks)

<a id="practitioner-lessons-025"></a>

### practitioner-lessons-025 · We built our own custom harness, was it worth it?

作者／组织：Lukasz Piliszczuk / Motion。类型：作者／团队实践或研究文章。版本／日期：2026-07-30。读取日：2026-10-13。

用途：事实：营销agent Runneth由Claude SDK迁Pi再自建Rust；按团队测量每会话内存约100MB降至10MB，动机是VM并发成本与可控快捷路径。

阅读范围：Our harness journey; What owning the harness unlocked; tradeoffs。限制：成本是特定版本/负载自述；共享VM有其他隔离风险；作者明确并不建议人人重写。

[公开原文](https://motionengineering.substack.com/p/we-built-our-own-custom-harness-was)

<a id="practitioner-lessons-030"></a>

### practitioner-lessons-030 · Lessons from my self-improving coding agent

作者／组织：Joel Hans。类型：作者／团队实践或研究文章。版本／日期：2026-02-25。读取日：2026-10-13。

用途：作者实验：约100session与八次维护产生工具/skills，但需持续判断的学习捕获技能60多次只用两次；明确session结束触发的反思更稳定。

选读范围：Knowing isn’t doing; deferral instinct; Specific reliability。限制：读前13500字符至最后一节中段；成功率样本量未详，模型自述原因只算解释假设；不能推广为自主学习无效。

[公开原文](https://ngrok.com/blog/bmo-self-improving-coding-agent)

<a id="practitioner-lessons-041"></a>

### practitioner-lessons-041 · The Bitter Lesson of Agent Harnesses

作者／组织：Gregor Zunic / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2026-04-19。读取日：2026-10-13。

用途：事实：团队把click等包装与watchdog删减为原始CDP、可编辑helpers及持久daemon，允许agent自己补上传等缺失操作。

阅读范围：Four-file harness; editable helpers; target recovery。限制：全文；个案不证明所有watchdog或安全边界可删；浏览器容错机制与授权边界须分开。

[公开原文](https://browser-use.com/posts/bitter-lesson-agent-harnesses)

<a id="practitioner-lessons-051"></a>

### practitioner-lessons-051 · Closer to the Metal: Leaving Playwright for CDP

作者／组织：Nick Sweeting / Browser Use。类型：作者／团队实践或研究文章。版本／日期：2025-08-20。读取日：2026-10-13。

用途：事实：团队观察Python到Node再到浏览器的多进程状态漂移、崩溃/对话框/焦点与远端上传失败；改直接CDP后自行承担浏览器异常处理。

阅读范围：Multi-hop architecture; event bus; element handles。限制：全文分段读；Playwright评价是当时负载下的团队经验，不是其所有版本的普遍限制；与2026-04团队进一步删watchdog需并读。

[公开原文](https://browser-use.com/posts/playwright-to-cdp)

<a id="runtime-boundaries-007"></a>

### runtime-boundaries-007 · Windows Job Objects

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：2025-07-14。读取日：2026-10-13。

用途：Windows Job可一组管理后代、KILL_ON_JOB_CLOSE在最后handle关闭时终止成员；breakaway/WMI子进程等是边界。通知除特定限额外不保证送达，不能仅无通知推定未发生。

选读范围：Job membership, limits, notifications, kill-on-close。限制：只论Windows官方契约，不能证明任意程序全部包含

[公开原文](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)

<a id="runtime-boundaries-008"></a>

### runtime-boundaries-008 · Node child process lifecycle

作者／组织：Node.js。类型：官方文档／规范。版本／日期：v26.11.1。读取日：2026-10-13。

用途：kill成功只表示信号发送，killed不是退出确认；Linux杀父不杀孙。PIPE容量有限，env的PATH查找及Windows Path/PATH去重影响同一命令真实执行对象。

选读范围：pipes/env/Windows bat; kill/killed L1131-1220。限制：partial；阅读相关生命周期与环境章节

[公开原文](https://nodejs.org/api/child_process.html)

<a id="runtime-boundaries-009"></a>

### runtime-boundaries-009 · kill(2) process and group semantics

作者／组织：Linux man-pages。类型：官方文档／规范。版本／日期：man-pages 6.19。读取日：2026-10-13。

用途：负PID可向进程组发信号，但组内至少一个对象成功即可整体成功；signal 0只做存在/权限检查，僵尸也可能仍有PID。loop需分别确认进程组收尾，不能以kill返回值当全部停止。

选读范围：DESCRIPTION, RETURN VALUE, ERRORS。限制：POSIX/Linux契约，不是跨平台实现

[公开原文](https://man7.org/linux/man-pages/man2/kill.2.html)

<a id="runtime-boundaries-011"></a>

### runtime-boundaries-011 · Modal sandbox snapshots and retention

作者／组织：Modal。类型：官方文档／规范。版本／日期：live 2026-10-13; Python v1.5 TTL change。读取日：2026-10-13。

用途：filesystem snapshot不含mounted Volume；v1.5默认30天TTL替代永久保存，过期Image.from_id仍可构造但首exec失败。memory snapshot有7天链继承期限、TCP重连、exec后台进程不正确恢复等约束。

选读范围：Snapshot Retention; Memory Snapshot Limitations; Persisting State。限制：产品特定；memory snapshot为Alpha

[公开原文](https://modal.com/docs/guide/sandbox-snapshots)

<a id="runtime-boundaries-012"></a>

### runtime-boundaries-012 · Modal sandbox file delivery

作者／组织：Modal。类型：官方文档／规范。版本／日期：live 2026-10-13。读取日：2026-10-13。

用途：临时沙箱文件可经stream copy交出，挂载Volume还要commit，其他沙箱需reload_volumes才见更新。官方例子先等待写进程、检查同步退出码再终止，交付应区分本地存在、持久存储及外部可见。

选读范围：Filesystem API; streaming copies; Using Volumes; sync。限制：不声称copy API自动提供内容校验或用户权限

[公开原文](https://modal.com/docs/guide/sandbox-files)

<a id="runtime-boundaries-013"></a>

### runtime-boundaries-013 · Modal volume consistency and migration

作者／组织：Modal。类型：官方文档／规范。版本／日期：live 2026-10-13 / v1-v2。读取日：2026-10-13。

用途：同文件并发last-write-wins，reload时本容器卷暂空且打开文件会busy。v1有inode限额，df返回占位数据；同名新卷有新ID，替换后旧运行任务仍指旧ID，必须重新部署/启动。

选读范围：Volume commits/reloads; consistency; busy; inode limit; migration。限制：部分章节；不外推所有分布式文件系统

[公开原文](https://modal.com/docs/guide/volumes)

<a id="runtime-boundaries-014"></a>

### runtime-boundaries-014 · E2B pause/resume lifecycle

作者／组织：E2B。类型：官方文档／规范。版本／日期：live 2026-10-13; SDK2.48.0 refusal rollout。读取日：2026-10-13。

用途：paused当前无限期保存；connect只延长不缩短寿命。pause拒绝503时沙箱仍运行；auto-pause持续拒绝可降级filesystem-only，丢内存并重启。持久化请求成功与保留哪种状态须明确。

选读范围：state transitions; refusal; timeout; auto-pause; network。限制：区域分批上线；不能将内存保留视为无条件保证

[公开原文](https://docs.e2b.dev/sandbox/persistence)

<a id="runtime-boundaries-018"></a>

### runtime-boundaries-018 · \[Windows Desktop\] Terminating a shell command does not kill its descendant process tree

作者／组织：Hadeanyolo。类型：公开问题讨论。版本／日期：created 2026-07-13T09:33:31Z; updated 2026-09-04T21:41:02Z; open。读取日：2026-10-13。

用途：Windows Desktop报告Script terminated后多代Git/SSH继续运行，并有正常成功命令后的残留复现。命令结果与后代清理应分别报告；issue仍open，未确认通用根因。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/openai/codex/issues/32742)

<a id="runtime-boundaries-020"></a>

### runtime-boundaries-020 · \[BUG\] On a genuinely full disk, the Bash ENOSPC notice names the session tmpdir instead of the filesystem, and no command can then run to diagnose it

作者／组织：oconnorjoseph。类型：公开问题讨论。版本／日期：created 2026-08-26T18:21:49Z; updated 2026-10-10T22:11:01Z; open。读取日：2026-10-13。

用途：真实满盘时stdout写临时文件也失败，连df/du诊断都无法通过Bash工具运行；需要独立于耗尽资源的有界诊断路径，不能让模型盲删。作者生产观察，未确认产品修复。

阅读范围：issue body; and comments。限制：用户报告不等于产品普遍失效；保留维护者结论与报告者假说边界

[公开原文](https://github.com/anthropics/claude-code/issues/89879)

<a id="runtime-boundaries-027"></a>

### runtime-boundaries-027 · E2B streams versus sandbox lifetime

作者／组织：E2B。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：单连接断开可发生在sandbox仍运行时；SDK有keepalive与commands.connect(pid)/pty.connect(pid)重附着。重试run命令与重连输出不是同一动作，loop应先识别运行对象。

选读范围：stream lifetime; timeout behavior。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.e2b.dev/faq/sandbox-lifetime)

<a id="runtime-boundaries-028"></a>

### runtime-boundaries-028 · E2B filesystem-only snapshots

作者／组织：E2B。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：filesystem-only恢复是重启而非内存恢复，服务需重启且外部客户端重新连接；2.55.0新增mode且不能与deprecated keepMemory同时传，filesystem-only与autoResume互斥。

选读范围：SDK2.55.0 mode; comparison; validation。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.e2b.dev/sandbox/filesystem-only-snapshots)

<a id="runtime-boundaries-030"></a>

### runtime-boundaries-030 · Docker stop semantics

作者／组织：Docker。类型：官方文档／规范。版本／日期：live documentation 2026-10-13。读取日：2026-10-13。

用途：stop先对容器主进程送可配置stop signal，grace后SIGKILL；timeout=-1无限等待，Linux/Windows默认grace不同。harness取消预算需含优雅停止和强制清理。

选读范围：description; signal; timeout。限制：产品特定当前契约；未进行云服务实测

[公开原文](https://docs.docker.com/reference/cli/docker/container/stop/)

<a id="runtime-boundaries-038"></a>

### runtime-boundaries-038 · Support managed app-server lifecycle on Windows

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-02; 715294448f56ce3ca6b2f62c84e9c9ef5e9aee20。读取日：2026-10-13。

用途：保留 Windows 进程身份 handle；需要终止时重开有 terminate 权限的 handle 并核对创建时间，防止 PID 复用杀错进程。查询 handle 不要求终止权限，测试验证。

选读范围：PR body; backend/windows.rs Process::terminate; windows_tests.rs identity_queries_do_not_require_termination_access。限制：已合并；未核到发布版本，不写已发布。

[公开原文](https://github.com/openai/codex/pull/42381)

<a id="runtime-boundaries-042"></a>

### runtime-boundaries-042 · Suppress Windows console windows for background subprocesses

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged 2026-09-29; fbc169827e9789f9e7ba2ed97c15e2021c3312bb。读取日：2026-10-13。

用途：Windows 创建 flag 会覆盖：后台启动同时保留 CREATE_NO_WINDOW 与 CREATE_SUSPENDED，先绑定 Job 后恢复；绑定失败 fallback 必须清除 SUSPENDED 否则永不执行。fallback 返回 None Job，因此可运行不等于树已受管。

选读范围：utils/process/src/lib.rs + background_command_tests.rs; utils/pty/src/win/job.rs。限制：已合并；未核发布tag。

[公开原文](https://github.com/openai/codex/pull/49164)

<a id="runtime-boundaries-046"></a>

### runtime-boundaries-046 · Creating a Pseudoconsole Session

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：2022-09-20。读取日：2026-10-13。

用途：ClosePseudoConsole 会终止附着客户端，但关闭本身可能发最后一帧输出；单线程同步收尾若不继续读输出会死锁，需分线程服务输入输出直到关闭完成。

选读范围：Preparing communication channels; Ending the pseudoconsole session。限制：ConPTY，不推广为普通 PIPE 行为。

[公开原文](https://learn.microsoft.com/en-us/windows/console/creating-a-pseudoconsole-session)

<a id="runtime-boundaries-047"></a>
<a id="r3-runtime-009"></a>

### runtime-boundaries-047 · Pod Lifecycle

作者／组织：Kubernetes。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。 引用别名：r3-runtime-009（本组合计 1 项，关联文档与版本复核不另计）。

用途：同一个 Pod UID 不会被重新调度，替代 Pod 即便同名也是新实体；emptyDir 随原 Pod 消失。Running 是容器状态聚合，不代表 agent 成功，restartPolicy 可在旧副作用已发生后重跑进程。

选读范围：Pod lifetime; Pod phase; container restart policy。限制：阅读 Pod 生命周期、phase 与容器重启策略；未覆盖全部 termination 细节。

已读关联文档／版本（同一计数组）：
- r3-runtime-009：Current docs snapshot, 2026-10-14；范围：Termination of Pods; Pod Termination Flow; Pod shutdown and sidecar containers；补充复核，不新增计数。[该记录原文](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- runtime-boundaries-047：current docs 2026-10-13；范围：Pod lifetime; Pod phase; container restart policy。[该记录原文](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

<a id="runtime-boundaries-048"></a>

### runtime-boundaries-048 · Environment Variables

作者／组织：Microsoft。类型：官方文档／规范。版本／日期：2025-07-14。读取日：2026-10-13。

用途：子进程默认继承启动时父进程环境块；修改外部系统环境不更新运行中父进程。hot reload 配置与后续工具 env 必须明确重新构造，不能假设 UI/系统改过就被旧 daemon 继承。

选读范围：Environment block and CreateProcess/SetEnvironmentVariable。限制：仅继承契约，不作为环境清洗的完整方案。

[公开原文](https://learn.microsoft.com/en-us/windows/win32/procthread/environment-variables)

<a id="runtime-boundaries-049"></a>

### runtime-boundaries-049 · Replace the Sandbox class

作者／组织：Cloudflare。类型：官方文档／规范。版本／日期：SDK 0.12.10→1.0.1; updated 2026-10-13。读取日：2026-10-13。

用途：1.0 inactivity timeout 不跨 Durable Object restart，必须构造器恢复；start 返回不等 ready，setup Promise 避免并发请求绕过初始化，部署可能中断 setup 所以各步须可重入。

选读范围：Replace class steps 2,6,7,8。限制：时间敏感迁移文档；仅此SDK版本，禁止跨版本套用旧示例。

[公开原文](https://developers.cloudflare.com/sandbox/sdk/migrate/replace-the-sandbox-class/)

<a id="runtime-boundaries-050"></a>

### runtime-boundaries-050 · Persistence

作者／组织：Daytona。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：sandbox stop 的含义随类型变：container 磁盘保留RAM丢失，VM stop磁盘offload并释放quota，pause保存RAM，GPU stop直接删除。产物策略须绑定 sandbox class，不只绑定供应商。

选读范围：Filesystem persistence table; Memory persistence table。限制：当前产品文档，不宣称内存快照能保持所有外部连接有效。

[公开原文](https://www.daytona.io/docs/en/persistence/)

<a id="runtime-boundaries-052"></a>

### runtime-boundaries-052 · Run Each Conversation in Its Own Docker Container

作者／组织：OpenHands。类型：官方文档／规范。版本／日期：current docs 2026-10-13。读取日：2026-10-13。

用途：每会话容器仍 bind mount 宿主 workspace/history/persistence；共用host workspace仍共用可写文件，不因容器隔离而免冲突。idle20分钟stop、下次重建，启动时清理旧容器，历史靠外部mount留存。

选读范围：How Isolation Works; Workspace and Persistence; Configuration Reference。限制：官方配置示例使用latest镜像；生产需记录兼容版本，本文未运行。

[公开原文](https://docs.openhands.dev/openhands/usage/agent-canvas/backend-setup/docker-execution)

<a id="runtime-boundaries-055"></a>

### runtime-boundaries-055 · Tini process lifecycle

作者／组织：Thomas Orozco / Tini。类型：官方文档／规范。版本／日期：v0.19.0。读取日：2026-10-13。

用途：reaping 防僵尸占满PID；默认只转发信号到直接child，-g 才发进程组。PID1/subreaper 与 kill-tree 是两条职责，不能有 --init 就声称所有后代必被取消。

选读范围：Why Tini; Subreaping; Process group killing; Understanding Tini。限制：相关章节静态阅读，未运行测试。

[公开原文](https://github.com/krallin/tini/blob/v0.19.0/README.md)

<a id="runtime-boundaries-056"></a>

### runtime-boundaries-056 · systemd.kill process killing procedure

作者／组织：systemd。类型：官方文档／规范。版本／日期：v259。读取日：2026-10-13。

用途：KillMode=control-group 默认管全cgroup，mixed先main SIGTERM后全组SIGKILL，process仅main会让后台工具逃出生命周期/资源核算。关闭SendSIGKILL可能因残存成员阻止重启；停机状态不等于无资源。

选读范围：KillMode, KillSignal, SendSIGKILL sections。限制：阅读官方 tag 中 KillMode、信号和升级终止机制的文档；未运行跨平台测试。

[公开原文](https://github.com/systemd/systemd/blob/v259/man/systemd.kill.xml)

<a id="runtime-boundaries-057"></a>

### runtime-boundaries-057 · Allow Windows daemon launches with residual job membership

作者／组织：OpenAI。类型：公开变更／提案。版本／日期：merged / 8b78f4796605bda8e31329537f5fef036e405e66。读取日：2026-10-13。

用途：Windows breakaway可脱内层job却仍留外层，IsProcessInJob非零不足以断言daemon必被杀。修复去掉笼统拒绝，先做suspended breakaway probe再停旧daemon，probe必须terminate+reap。

选读范围：PR body; windows_tests.rs detached_launch_preflight_allows_residual_job。限制：已合并，未核发布tag；回归测试显式证明内外job成员不同。

[公开原文](https://github.com/openai/codex/pull/48157)

<a id="tools-security-022"></a>

### tools-security-022 · anthropics/sandbox-runtime

作者／组织：Anthropic experimental sandbox-runtime maintainers。类型：源码／仓库文档。版本／日期：rolling README retrieved 2026-10-13。读取日：2026-10-13。

用途：运行时读写规则默认不同：读通常开放，写需允许；无设置与设置存在但无效不应混为一谈，后者应退出而非回退。

选读范围：README architecture, filesystem/network settings, control-fd, violation attribution, resolved-address check。限制：rolling main 文档，非固定提交；只读 README 的安全相关前段，未审计实现正确性。

[公开原文](https://github.com/anthropic-experimental/sandbox-runtime)

<a id="tools-security-023"></a>

### tools-security-023 · containers/bubblewrap

作者／组织：bubblewrap maintainers。类型：源码／仓库文档。版本／日期：rolling README retrieved 2026-10-13。读取日：2026-10-13。

用途：bubblewrap 只是构造沙箱的工具，不自带完整安全策略；实际边界由调用者提供的参数、挂载和命名空间决定。

选读范围：README System security, Sandbox security, Sandboxing, Limitations。限制：README 的平台假设需与部署内核能力匹配；非新漏洞发现。

[公开原文](https://github.com/containers/bubblewrap)

<a id="tools-security-026"></a>

### tools-security-026 · Configure the sandboxed Bash tool - Claude Code Docs

作者／组织：Anthropic / Claude Code documentation。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：Bash 沙箱只包围 shell/Monitor 子进程，Read/Edit/WebFetch、MCP server、hooks 等走不同路径；denyRead 不能自动阻断 Read 工具。

选读范围：Sandbox scope/defaults; modes; escape hatch; filesystem rules。限制：文档含当日版本特性；实现与 README 支持平台可能不同，不能把独立 sandbox-runtime 能力等同 Claude Code 产品已支持。

[公开原文](https://code.claude.com/docs/en/sandboxing)

<a id="tools-security-027"></a>

### tools-security-027 · Implementing a secure sandbox for local agents · Cursor

作者／组织：Ani Betts, Yash Gaitonde, Alex Haugland / Cursor。类型：作者／团队实践或研究文章。版本／日期：2026-02-18。读取日：2026-10-13。

用途：沙箱隔离由 OS 原语实现，macOS/Linux/WSL2 的路径不同，统一 API 不代表统一实现约束。

阅读范围：article body。限制：40% 中断下降为厂商生产观察，非可泛化安全测量。

[公开原文](https://cursor.com/blog/agent-sandboxing)

<a id="tools-security-028"></a>

### tools-security-028 · Git commands do not seem to work on modal

作者／组织：Gguinet and klieret / SWE-agent。类型：公开问题讨论。版本／日期：2025-06-12。读取日：2026-10-13。

用途：git show/log 在无正常终端的 Modal 环境触发 pager 等待 RETURN，被 loop 当成执行超时。

选读范围：问题正文与维护者首个回复（所读正文约 1 万字符）。限制：只读正文和首个维护者回复，未单独读取关联 PR。

[公开原文](https://github.com/SWE-agent/SWE-agent/issues/1204)

<a id="tools-security-029"></a>

### tools-security-029 · Linux sandbox panics when project `.codex` is a symlink into writable workspace.

作者／组织：emcd and Codex maintainers。类型：公开问题讨论。版本／日期：2026-05-02; Codex 0.128.0。读取日：2026-10-13。

用途：受保护 .codex 经过工作区可写 symlink 时，sandbox 构造拒绝却以 panic 反馈；命令还没开始就失败，不应当成目标程序错误。

阅读范围：article body。限制：issue 关闭针对 panic 处理，不能据此声称所有 symlink 布局已支持。

[公开原文](https://github.com/openai/codex/issues/20716)

<a id="tools-security-030"></a>

### tools-security-030 · Linux sandbox 0.162: deny_read entries that name the same file through a symlink fail with "Unable to mount source on destination: No such file or directory"

作者／组织：offbrand-games and argszero / openai/codex issue。类型：公开问题讨论。版本／日期：2026-10-09; Codex 0.162.0。读取日：2026-10-13。

用途：同一受限文件经 symlink 两个名字重复挂载 mask 可导致 bwrap 启动失败，按字符串去重不等于按实际文件身份去重。

阅读范围：article body。限制：开放 issue；后续回复的补丁作者明确未在 Linux 真运行测试，修复建议不能作为已验证解决。

[公开原文](https://github.com/openai/codex/issues/52658)

<a id="tools-security-033"></a>

### tools-security-033 · Computer use

作者／组织：OpenAI。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：计算机工具的执行器要维持 session、执行限额和权限；不能只实现一个 exec 函数就认为接入完成。

选读范围：code-execution integration; safety guidance。限制：只读执行集成及安全段落。

[公开原文](https://developers.openai.com/api/docs/guides/tools-computer-use)

<a id="tools-security-034"></a>

### tools-security-034 · Auto-waiting | Playwright

作者／组织：Microsoft / Playwright。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：点击前 actionability 要求唯一元素、可见、稳定、能收到事件且启用；force 会跳过部分检查。

阅读范围：article body。限制：Playwright 的具体检查语义；harness 推论是仍需确认目标语义和执行后状态。

[公开原文](https://playwright.dev/docs/actionability)

<a id="tools-security-044"></a>

### tools-security-044 · Kill shell tool process groups on timeout

作者／组织：luca-ctx and Codex maintainers。类型：公开变更／提案。版本／日期：merged 2025-11-08; a2fdfce02a870773b3b037954b0fad6222020389。读取日：2026-10-13。

用途：只终止 shell 直接子进程会留下孙进程持有 PTY，timeout 已到但 tool 无法返回，agent 永久卡住。

阅读范围：article body。限制：已合并修复历史；文中的1000ms默认值不应转成现在通用建议。

[公开原文](https://github.com/openai/codex/pull/5258)

<a id="tools-security-047"></a>

### tools-security-047 · asyncio timeouts for RemoteRuntime

作者／组织：18jeffreyma / SWE-ReX。类型：公开问题讨论。版本／日期：2025-08-21。读取日：2026-10-13。

用途：重测试负载下控制 webserver 与工具进程争 CPU，远程命令出现 asyncio timeout；用户还发现 HTTP层300秒上限先于长命令超时。

阅读范围：article body。限制：CPU竞争是报告者推测；300秒问题有相关 PR 交叉支撑，不把假设写成已验证根因。

[公开原文](https://github.com/SWE-agent/SWE-ReX/issues/245)

<a id="tools-security-048"></a>

### tools-security-048 · Timeout Increase

作者／组织：jlebensold and dcloud347 / SWE-ReX。类型：公开变更／提案。版本／日期：opened 2025-08-26; still open at retrieval。读取日：2026-10-13。

用途：提案将 HTTP 客户端 timeout 与调用者命令 timeout 关联，避免通信层先断开导致命令结果不可知。

阅读范围：article body。限制：PR open，不宣称方案已合并或验证；与source047是独立issue/PR但同一故障链。

[公开原文](https://github.com/SWE-agent/SWE-ReX/pull/248)

<a id="tools-security-050"></a>

### tools-security-050 · Security Model - gVisor

作者／组织：gVisor maintainers。类型：官方文档／规范。版本／日期：rolling docs retrieved 2026-10-13。读取日：2026-10-13。

用途：gVisor 限制宿主内核攻击面，但仍允许映射文件和网络操作；沙箱不是安全架构替代品。

阅读范围：article body。限制：通用基础设施只用于解释 agent 任意代码执行的边界，不扩写内核百科。

[公开原文](https://gvisor.dev/docs/architecture_guide/security/)

<a id="tools-security-051"></a>

### tools-security-051 · docs/prod-host-setup.md

作者／组织：Firecracker maintainers / AWS。类型：源码／仓库文档。版本／日期：rolling production guide retrieved 2026-10-13。读取日：2026-10-13。

用途：microVM 也需 jailer 或等价限制、每租户隔离和宿主资源控制；默认不对 guest egress 做过滤。

选读范围：Production host recommendations: serial/log resource limits, jailer, guest egress, tenant separation。限制：主分支生产建议，无固定提交；仅引用与执行loop后果相关控制。

[公开原文](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md)

<a id="tools-security-060"></a>

### tools-security-060 · SWE-ReX local runtime implementation

作者／组织：SWE-agent maintainers。类型：源码／仓库文档。版本／日期：main, accessed 2026-10-13。读取日：2026-10-13。

用途：持久PTY需要独立提示符和退出码协议；交互命令可返回合成exit_code=0，静默提取失败可返回None，消费者不能混同为真实业务成功。

选读范围：src/swerex/runtime/local.py: BashSession._run_normal; LocalRuntime.execute。限制：主分支快照未本地执行；这里只解释可见代码，不宣称发现漏洞或证明所有平台行为。

[公开原文](https://github.com/SWE-agent/SWE-ReX/blob/main/src/swerex/runtime/local.py)

[返回分类目录](README.md#topics)
