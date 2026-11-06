# “禁止联网”究竟约束谁：phase、sandbox 与模型托管工具

研究日期：2026-11-06。学习目标：L2 → L3。

证据范围：Harbor network plan、trial phase、native web-tool 控制源码路径 D3；provider 真正执行防火墙的实现未全面追踪，也未实测。Inspect Compose 配置解析代码达到狭义 D4，5 个测试通过；**没有 Docker 网络或云端防火墙实验**。

固定版本：Harbor `26f95e0ebd8c77011bbf4656f5c98af66ce55848`；Inspect `7cf09c929b3ea9138762ca9e4d8d23f119554ee6`。官方 online network capability 表是可变文档，不能代替实际安装版。[N1–N6]

## 1. 至少需要区分三个网络平面

```text
Controller / harness
  ├─ model API / hosted web search / remote MCP
  ├─ provider / Kubernetes / registry control APIs
  └─ sandbox execution transport

Sandbox
  ├─ agent shell / browser / package manager / test process egress
  ├─ local or multi-service task networking
  └─ installed agent's model API requests, if inference originates here

External task services
  └─ websites, DB fixtures, storage, other services with independent state
```

容器不能访问公网，不代表 controller 没有公网，也不代表模型服务商代为执行的 web search 被关掉。反过来，关掉模型 web search，也不会自动配置 container firewall。任意 MCP tool 又可能通过自己的服务端联网。[N1: Built-in web tools]

这影响两个独立问题：

- **安全/隐私**：数据会通过哪些路径离开环境？
- **评测有效性**：agent 是否获得了题目禁止的搜索、答案、外部计算或共享状态？

仅验证 `curl` 失败只能支持其中一个 shell 路径的观察。

相关调用边界见 [Inspect bridge 与 trajectory](../05-agent-runtime/inspect-bridge-and-trajectory.md) 第2.3节，以及 [ACP black-box agent trace](../05-agent-runtime/acp-black-box-agent-trace.md)。本文专注网络 policy，不重复协议/轨迹内部实现。

## 2. Harbor：网络策略在不同 phase 解析

官方任务格式区分：

- `[environment]`：环境启动与 agent setup 的 baseline；
- `[agent]`：`agent.run()` 阶段，不包含 `agent.setup()`；
- `[verifier]`：verify 阶段；
- `[verifier.environment]`：独立 verifier 环境自己的 baseline。[N1]

`resolve_trial_network_plan()` 从任务与 step override、run-specific extra hosts 合成 agent baseline/phase、verifier baseline/phase。shared verifier 以 agent environment baseline 为基础；separate verifier 可以有独立环境配置。未写 phase override 时继承相应 baseline，不应把某个单独 TOML 字段当成完整最终策略。[N2]

实际 agent phase 的顺序为：[N3:L707–792]

1. 解析 effective network plan；
2. 在 sandbox 上切换 phase policy；
3. 应用执行环境与 native web-tool 配置；
4. 调用 agent run/resume/load，并施加 agent timeout；
5. 退出 context 时尝试恢复 baseline policy。

`_phase_network_policy()` 使用 `finally` 恢复 baseline，但这是调用恢复操作，不是对 provider 一定成功的证明。远端故障或取消情况下应观察实际状态，而不只观察 Python context 是否退出。[N3:L451–467]

## 3. “no-network”仍可能被解析为带推理例外的 allowlist

这条具体行为容易被漏掉：`Trial._network_plan()` 会为 **installed agent** 找出其推理 endpoint 的精确 hostname，并为 restricted policy 增加推理目的地址。host-side inference 不需要 sandbox egress，因此不走同一添加路径。[N3:L313–361]

`add_inference_hosts()` 通过 `merge_extra_allowlists()` 合并；非 public 策略加上额外 hosts 后，结果是 allowlist。只提取 HTTP(S) endpoint 的精确 host，不猜 wildcard。显式 run-specific agent allowlist 会替代自动 inference additions 的选择逻辑。[N2；N3:L306–311]

**含义：** 任务声明的 `no-network` 不是永远等价于 effective sandbox policy 中零外部目标。应保存最终解析的策略与添加原因，并决定推理 API 例外是否符合实验协议。此处说明框架设计，不将必要的模型调用例外称为绕过。

hostname allowlist 也不等于“只允许这个模型 API 路径”。源码按 host 而非 URL path 解析；应把同一域名下其他能力作为 threat model 的一部分，而不夸大 allowlist 的精细度。[N2: inference_endpoint_host]

## 4. Native web tools 是另一套 capability 与覆盖规则

`_configure_web_tools()` 对非 public policy 默认要求禁用 agent 的 native web tools；模拟用户与目标 agent 两个角色都应用。[N3:L699–705]

`BaseAgent.set_web_tools_disabled()` 尊重显式 `disable_web_search` 选项。显式 false 可以保留 native web tool，即使 sandbox policy restricted。未声明可控制 native tools 的 agent 在收到相关请求时会记录 error 并继续，sandbox policy 仍独立生效。[N4:L197–246]

这不证明那些 agent 一定有未受控工具，也不证明日志中的 error 可忽略。它说明 **environment capability 的 fail-closed 验证不等于整个 tool surface 的统一 fail-closed 契约**。任意 MCP 不在这个 native-web 开关的覆盖范围。[N1、N4]

上游 `test_web_tool_policy.py` 覆盖 public → no-network → allowlist → public、显式 true/false、run/resume/load，以及模拟用户两个角色。已阅读相关测试，未运行，不把测试文件存在等同于通过。[N5]

## 5. Provider 名字相同的 mode 不一定等价

官方 capability 表明确区分 exact/wildcard hostname、IPv4/IPv6、CIDR、dynamic policy，以及 single-container/Compose/不同 runtime 的支持。未声明所需能力时，框架应在验证阶段拒绝，而不是自动降低环境策略。[N1；N3:L390–449]

几个有意义的语义例子，均是 2026-11-06 文档事实，非本轮实测：

- 部分 provider 的动态策略只作用于新连接，旧连接仍开放；所以“切换 phase”不必然切断之前建立的 session。
- 有的 allowlist 按 hostname 解析到 IP，有的按 HTTP Host/TLS SNI；wildcard、apex domain、HTTP/HTTPS 和端口行为不同。
- Docker/Podman allowlist 要求 Linux containers 与相应 nftables kernel 能力；仅能创建容器不证明可执行此策略。
- Modal Compose 的外层 egress policy 同时覆盖服务启动的 image pulls/build downloads；文档说明不会临时扩大 restricted startup policy。准备依赖与 agent 运行可用不同 phase。[N1]

因此换 provider 要做契约测试，不能只验证配置字符串能被接受。尤其不能把 DNS 成功当作 HTTPS 成功、把新连接拒绝当作旧连接撤销、把 sandbox 限制当作所有工具限制。

## 6. Inspect：添加一个 Compose 文件会替换默认配置

固定 Inspect `docker/config.py` 的路径很直接：

1. 如果找到 `compose.yaml` 等现存自定义文件，直接返回其路径；
2. 否则可用已有 `.compose.yaml`；
3. 有 Dockerfile 时合成 Compose；
4. 都没有时合成 Python 容器 Compose。

两种合成模板都含 `network_mode: none`、`init: true` 等默认值。**自定义 Compose 不与这些模板合并。** 配置里没有写网络限制，不会因为之前使用过默认 sandbox 就自动继承限制。[N6、N7]

本轮实际执行完整 upstream config module，只有 appdirs 和 import plumbing 被替换为临时测试目录/已验证的原版常量；使用预装 PyYAML 与真实 filesystem。5 个测试验证：[N8]

- generic 与 Dockerfile 合成路径都输出 `network_mode: none`；
- custom Compose 原样保留，不自动加入 network_mode 或 init；
- custom Compose 优先于 legacy auto file；
- central auto-compose 的 build context 转为绝对路径，仍保留 no-network 字段。

这只证明生成/选择了什么配置，**不是验证网络包是否被阻断**。运行态仍依赖 Docker、其他网络路径及 host 配置。官方 Inspect sandbox 文档说明 custom Compose 替代默认配置，普通 Compose 默认网络行为可能允许互联网。[N7]

## 7. 网络策略的最小验证矩阵

以下是下一阶段待运行设计，未执行外部连接或修改防火墙：

| 维度 | 至少验证的对照 |
|---|---|
| phase | startup、agent setup、run/resume/load、verifier、cleanup |
| 路径 | shell、browser、installed agent inference、hosted web tool、remote MCP |
| 目标 | 允许域、拒绝域、apex/subdomain、IPv4/IPv6、非默认端口 |
| 连接 | 新 TCP/TLS、策略变化前建立的长连接、DNS cache |
| 配置 | default、custom Compose、run override、separate verifier、runtime 切换 |
| 故障 | provider policy call 失败、取消、controller crash、恢复 baseline 失败 |

使用受控测试服务和无敏感的 marker 数据，记录 effective policy、连接结果和 provider/runtime 版本。hosted tool 与 MCP 的验证应依据实际工具 surface，而不是假装 container firewall 覆盖所有平面。

## 8. 学习检查

- 为什么 setup 能装软件但 agent 不能联网，是合理的阶段策略而不一定是漏洞？
- 如何证明无外网任务没有通过 hosted search 获取答案？
- 改成 custom Compose 后，如何确认没有丢掉默认网络限制？
- 如果旧连接在 phase 切换后仍可用，你会把哪些 trial 判为有效、无效或待重跑？

## 来源

- [N1] Harbor [Network policies](https://docs.harborframework.com/tasks/network-policies.md)，官方可变文档，2026-11-06 阅读全文。capability 表不是各 provider 的实测保证。
- [N2] [`trial/network_policy.py`](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/network_policy.py)，全文，blob `91bc3495639118a3c47630fee831053cb5fae26f`。
- [N3] [`trial/trial.py`](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/trial/trial.py)，读取 L261–361、L390–467、L699–792；不是对完整2108行的审计。
- [N4] [`agents/base.py`](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/agents/base.py)，set_web_tools_disabled L197–246；[`agents/capabilities.py`](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/src/harbor/agents/capabilities.py)，全文。
- [N5] [`test_web_tool_policy.py`](https://github.com/harbor-framework/harbor/blob/26f95e0ebd8c77011bbf4656f5c98af66ce55848/tests/unit/trial/test_web_tool_policy.py)，读取主要 phase/explicit override/双角色测试；未运行。
- [N6] Inspect [`docker/config.py`](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/util/_sandbox/docker/config.py)，全文；[`compose.py`](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/util/_sandbox/compose.py)，读取导入及文件名常量段，不声明全文已审计。
- [N7] Inspect [Sandboxing](https://inspect.aisi.org.uk/sandboxing.html)，官方可变文档，默认与 custom Compose 网络说明。
- [N8] [Compose 配置实验](experiments/inspect-compose-defaults/README.md)，5 PASS，局部 D4，无网络运行验证。

除实际实验输出外，source access precision 为 2026-11-06 日期级。
