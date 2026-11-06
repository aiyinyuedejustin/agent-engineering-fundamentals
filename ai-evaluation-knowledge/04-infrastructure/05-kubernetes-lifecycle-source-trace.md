# Kubernetes 评测环境：从排队到清理的源码路径

研究日期：2026-11-06。学习目标：L2 → L3。

范围：Inspect 的 Kubernetes sandbox 扩展，不是一个独立 benchmark。生命周期子系统达到 **D3**：读取配置、Helm 模板和创建/ready/cleanup 调用路径，并对照上游测试。没有连接 Kubernetes 集群，没有渲染或安装 chart，没有运行上游测试，**不声明 D4**。

固定代码：`UKGovernmentBEIS/inspect_k8s_sandbox` commit `4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb`；读取时 main tip 的提交日期为 2026-10-30。内置 `agent-env` chart version `0.14.0`。这不是对所有 Inspect 发布版的保证。[K1–K5]

## 1. 架构：控制面不是 agent 的执行边界

```text
Inspect process (controller + model calls + task lifecycle)
  ├─ task-scoped HelmReleaseManager
  ├─ Helm submission queue → Kubernetes API → admission/scheduler
  ├─ readiness API reads → confirmed live sandbox Pods
  └─ Pod operation executor → exec / files in chosen sandbox

One sample's Helm release
  ├─ service A StatefulSet → sandbox container + CoreDNS (+ extras)
  ├─ service B StatefulSet → sandbox container + CoreDNS (+ extras)
  └─ networking / volumes / account / other declared resources
```

Inspect 可在本地运行而将 sandbox 放到集群。模型 API、controller 凭据与 task 代码不因此自动搬进 sandbox。Pod 数量也不一定等于 sample 数量，一个 sample 的多服务环境可能占多个 Pod。[K1、K2、K4；D1 文档 K6]

Kubernetes 管理资源和生命周期；真正的执行隔离还取决于 runtime、kernel、网络、mount、身份和 admission policy。内置模板默认 `gvisor`，但 `CLUSTER_DEFAULT` 会不设置 `runtimeClassName`，继而采用集群默认配置。[K4]

## 2. 初始化：先登记，再安装，最后交付

固定源码路径：

1. `K8sSandboxEnvironment.task_init()` 验证 prerequisites，创建 `PodOpExecutor`，并在 task 的 async context 初始化 `HelmReleaseManager`。sample contexts 继承该 manager，最终 task cleanup 才能看见所有 release。[K1:L160–181]
2. `sample_init()` 解析配置，取得 sample UUID，将 metadata 合并到 chart values，构造 `Release`。[K1:L191–227]
3. `manager.install()` **先把 release 加入追踪列表，再 await 安装**，这样部分安装失败仍有回收记录。[K2:L41–50]
4. `Release.install()` 在 install semaphore 内提交 Helm，但离开 semaphore 后才等待 Pod ready。[K3:L261–303]
5. Helm 使用 `--output=json` 返回 rendered manifest，代码从中抽取 expected services。operator 的 cluster values 最后加入，从而覆盖 task values。[K3:L334–385]
6. ready 后使用同一组已确认 Pod 生成 sandbox 对象，记录 Pod UID 和 restart count，并将 `default` sandbox 排第一，交给 Inspect。[K1:L197–214；K3:L308–332]

**工程结论：** 复现记录只存 task YAML 不够。集群管理员 override、最终 rendered manifest、runtime class、镜像 digest、namespace policy 和节点池也会改变实际环境。应记录“最终生效配置”，不是把声明配置当作执行事实。

## 3. 并发不是一个数，而是一张资源等待图

本实现有不同的限制层：sample 并发、Helm install、Helm uninstall、Pod operations，以及集群的 CPU/RAM/GPU/存储调度容量。官方 concurrency 文档也区分这些队列。[K6]

### 为何 install 与 uninstall 不能共用同一队列

若所有 permit 都被“等待空闲容量”的 install 占用，释放容量所需的 uninstall 又拿不到 permit，系统可能形成循环等待。源码用两个 semaphore，默认各 8，而不是一个全局 Helm semaphore。[K3:L674–687]

### 为何 install permit 只覆盖提交

如果 A 的 Pod 因稀缺 GPU 或指定节点池而 pending，A 不应一直占着提交 permit，阻止资源已可用的 B 被提交。本版本把 readiness wait 放在 semaphore 外。这是避免队头阻塞的具体措施，不是无限增加集群容量。[K3:L270–293]

上游 `test_install_permit_is_released_before_the_readiness_wait` 构造一个 permit、阻塞第一个 ready wait，然后确认第二个 install 仍能提交。这里读取了测试，未执行。[K7:L1245–1289]

### 哪些等待计入预算

源码在取得 install permit 后，计算 `deadline = monotonic() + timeout`。提交和 readiness 共享这一个 deadline，resource quota 冲突重试也不会重置预算。[K3:L274–293、L354–355]

注意：从这段代码看，等待取得 install permit 的时间发生在 deadline 创建之前。**不能把这个 timeout 描述为从调用开始到环境可用的完整端到端墙钟上限。** 总延迟还需包含外层排队、镜像准备、controller 调度等阶段。

上游测试用 100 秒总预算、30 秒已耗提交时间，断言 Helm 剩余 `--timeout=70s`。[K7:L1162–1190] uninstall 另有独立 timeout，避免安装预算被设为数小时后，失败清理也占住资源数小时。[K3:L668–671；K7:L1296–1310]

## 4. readiness 是可验证的集合条件

“Helm 命令退出 0”与“sample 可运行”不是同一件事。本实现要满足：

- rendered manifest 声明的 sandbox service 都有 ready Pod；
- 所读 live Pods 均满足 ready 条件；
- init containers、volume binding 等前置条件已经由 Pod readiness 反映；
- watch/cache 观察到 ready 后，再用一致性读取确认，并将这组 Pod 交付调用者。[K3:L444–489]

这样避免缓存滞后造成过早判断。代码也不把持续的 API/RBAC 读取失败一律报成容量不足，而保留 diagnostic。[K3:L479–488]

**仍然有限：** Pod Ready 只落实所配置的 probe。若服务没有适当的 application readiness probe，仍不能证明数据库 fixture、网页内容或评估器依赖已正确初始化。ready 是一系列契约，不是万能布尔值。

## 5. 清理失败既影响成本，也可能污染统计

三个不同阶段的路径不能混成一个 `finally`：

### sample 初始化失败

Inspect 在 `sample_init()` 抛错时不会再调用 `sample_cleanup()`。本实现立即尝试 uninstall，否则每次重试都可能留下新的 Pod。清理失败不得掩盖原安装 diagnostic；release 保留在 manager，等待 task cleanup 再试。[K1:L229–242；K8:L281–327]

### sample 已完成但 cleanup 失败

抛出 cleanup 异常会使原本成功的 sample 被 Inspect 记为 error。此处实现记录 warning、保留 release 供 task cleanup 重试，不抹掉已完成的有效样本。[K1:L245–272；K8:L210–235]

### task 最终 cleanup 失败

`uninstall_all()` 复制清理列表后先清空追踪，再并行 gather。此阶段失败不会自动再试，而会输出具体 release、namespace、context 和手动清理方式。[K2:L63–98]

这意味着“已从内存列表移除”不等于“集群资源已销毁”。生产评测还需要持久的资源审计与 orphan 检测。官方 cleanup 文档也指出 controller crash 可留下资源。[K6]

操作注意：无具体 release ID 的批量 cleanup 可涉及当前 namespace 中其他 Inspect 资源。本文未运行任何 cleanup 命令，也不建议未确认所有权就清空共享 namespace。

## 6. 安全默认值与容易被忽略的例外

### 资源预算必须按整个 Pod/环境计

内置主 service 默认 request=limit：CPU `500m`、memory `2Gi`。但每个 Pod 还有 CoreDNS，可能还有额外 sidecar/init container；不能把一个主容器 limit 直接当作整个 sample 资源总量。[K4:L146–156、L180 起]

模板使用 StatefulSet，每个 service 一副本。容器或节点故障后可能被重建，restart 不是“同一个 trial 无事发生”。扩展支持追踪重启并按策略处理；官方 limitations 文档解释重启可能丢失状态。[K3:L323–330；K6]

### 不挂 Kubernetes token 不等于没有云身份

内置值关闭 `automountServiceAccountToken`。同一文件明确提示，IRSA 等 cloud workload identity 可通过另一种 provider-specific token 注入。这两个控制面不同。[K5:L206–218]

因此还需要核查云 IAM、metadata service、挂载 secrets、controller-to-sandbox 传参；不能仅凭 `automount=false` 就断言 agent 没有云权限。创建 Pod 的 RBAC 也不能代替 privileged/hostPath/host namespace 的 admission 控制。[K6: workloads]

### 额外容器不会自动继承 service 的安全设置

`extraContainers` 原样加入 Pod，每个需要自己的 `securityContext`。模板的 service hardening 不自动扩展到额外 sidecar。[K5:L38–41]

### 网络变化也是任务条件变化

默认 `allowDomains=[]`；启用 Cilium policies 时无互联网访问。域名 allowlist 默认面向 HTTP 80/TLS 443 请求身份，额外端口另配，wildcard 支持有 Cilium 版本要求。关闭 `networkPolicy.enabled` 后，本 chart 不再提供其网络隔离保证。[K5:L7–37]

任务安装依赖、读取网页、访问模型托管 web tool 可能走不同路径。应按 startup、agent、verifier 阶段列出所需出口，并分别验证。不要为了让一个 pip 命令成功而默认给整个 trial 任意外网访问。

## 7. 最小集群验证计划，尚未执行

建议在专用 namespace、无真实凭据和受控镜像的测试集群中执行：

1. 单 sample、双 service，分别记录 submit、scheduled、image pulled、Pod Ready、application Ready 和 cleanup 完成时间。
2. 用不可满足的 resource request 制造一个 pending release，同时提交可调度 release，验证无队头阻塞。
3. 注入 initialization error，检查 release 立即清理；再注入 cleanup error，确认样本结果保留而资源残留单独报告。
4. 强制重启一个测试容器，确认不会悄悄接续为同一干净环境。
5. 检查有效 network policy、DNS 与 service account/cloud identity，不只阅读 values 文件。
6. controller 受控退出后，使用精确 ownership labels 检查 orphan；记录清理成本与最长滞留时间。

这些是待运行实验，不是通过清单。当前环境没有为本研究连接的集群；未创建云资源或产生费用。

## 8. 学习检查

- 为什么“先追踪再安装”与“成功卸载后再移除追踪”是一对设计？
- 如何区分 pending、RBAC read failure、应用未 ready 和任务失败？
- 为什么同一个 sample 的 cleanup 失败不应不加区分地改写模型得分？
- 能否给出一个 deployment 看起来相同，但最终安全边界不同的具体 override？

## 来源与追踪范围

以下源码均固定同一个 commit，2026-11-06 阅读，精确读取时刻未记录。

- [K1] [`_sandbox_environment.py`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/src/k8s_sandbox/_sandbox_environment.py)，重点 task/sample lifecycle L160–272。
- [K2] [`_manager.py`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/src/k8s_sandbox/_manager.py)，重点 L19–98。
- [K3] [`_helm.py`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/src/k8s_sandbox/_helm.py)，重点 L261–385、L444–489、L664–700。
- [K4] [`templates/services.yaml`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/src/k8s_sandbox/resources/helm/agent-env/templates/services.yaml)，StatefulSet/runtime/account/resources/sidecar 模板。
- [K5] [`values.yaml`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/src/k8s_sandbox/resources/helm/agent-env/values.yaml)；[`Chart.yaml`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/src/k8s_sandbox/resources/helm/agent-env/Chart.yaml)。
- [K6] 官方可变文档：[总览](https://k8s-sandbox.aisi.org.uk/)、[concurrency](https://k8s-sandbox.aisi.org.uk/tips/concurrency/)、[cleanup](https://k8s-sandbox.aisi.org.uk/tips/cleanup/)、[limitations](https://k8s-sandbox.aisi.org.uk/design/limitations/)、[workloads](https://k8s-sandbox.aisi.org.uk/security/kubernetes-workloads/)、[network](https://k8s-sandbox.aisi.org.uk/security/network-access/)。D1。
- [K7] [`test_helm.py`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/test/k8s_sandbox/test_helm.py)，读取 L1162–1330 的 timeout、readiness、permit 测试。未运行。
- [K8] [`test_manager.py`](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox/blob/4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb/test/k8s_sandbox/test_manager.py)，读取 L195–332 的 cleanup/initialization failure 测试。未运行。
