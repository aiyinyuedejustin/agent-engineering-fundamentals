[返回分类目录](README.md#topics) · [返回单页正文](../../docs/agent-harness-loop-guide.md)

<a id="supplementary"></a>

## 补充证据，不增加来源总数

以下条目只用于辅助确认已有结论或定位版本，不增加总数。判断依据是实际阅读的实质内容与去重关系，不仅是文件类型；同一实现的短类型片段、局部测试与调用点不拆成新增来源。同页或同文件的新版本复核已并入对应条目。

<a id="human-control-038"></a>
<a id="runtime-boundaries-029"></a>

### human-control-038 · Sharing objects with presigned URLs (independent recheck)

作者／组织：AWS。类型：官方文档／规范。版本／日期：S3 User Guide accessed 2026-10-13。读取日：2026-10-13。 引用别名：runtime-boundaries-029（同一组补充材料，不计数）。 补充证据，不增加总数。

用途：presigned URL受签名主体权限、credential寿命和额外策略共同限制，名义URL到期时间不是唯一期限。

选读范围：Who can create / expiration / limiting capabilities / expiry while downloading。限制：签名 URL 的有效期还受签名凭证和策略约束；链接存在不等于任何接收人都能访问。

已读关联文档／版本（同一计数组）：
- human-control-038：S3 User Guide accessed 2026-10-13；范围：Who can create / expiration / limiting capabilities / expiry while downloading；补充复核，不新增计数。[该记录原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- runtime-boundaries-029：live documentation 2026-10-13；范围：Who can create; expiration; FAQs；补充复核，不新增计数。[该记录原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

关联讨论、合并记录与发行版本不等价，不同版本的行为不可互换；复核不证明用户实际安装或服务端部署已升级。

[公开原文](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)

<a id="protocol-audit-008"></a>

### protocol-audit-008 · Google SDK FunctionCall/FunctionResponse types

作者／组织：Google。类型：源码／仓库文档。版本／日期：v2.13.0; blob feffb5756f8ca0836e113036274ee274c57654e7。读取日：2026-10-13。 补充证据，不增加总数。

用途：FunctionCall.id与FunctionResponse.id为Optional；存在时应匹配，不得假设所有模式始终给ID。

选读范围：FunctionCall / FunctionResponse 类型定义。限制：仅类型与注释复核，不证明服务端每一种组合均接受。 辅助核验类型片段，不作为额外独立来源计数。

[公开原文](https://github.com/googleapis/python-genai/blob/v2.13.0/google/genai/types.py)

<a id="protocol-audit-022"></a>

### protocol-audit-022 · Anthropic released MessageParam role

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0 (2026-08-20); blob 466c03eca17656b06337de7eb71f164d89196c2c。读取日：2026-10-13。 补充证据，不增加总数。

用途：发行版MessageParam role已有system；支持新版专页而非API参考页旧式绝对否定说明。

选读范围：MessageParam.role 与同 tag 的版本说明。限制：一个类型枚举复核，不另计新增来源；类型允许不表示每模型接受。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/types/message_param.py)

<a id="protocol-audit-027"></a>

### protocol-audit-027 · LiteLLM affinity regression cases

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：测试覆盖同边界、混合origin、unknown origin、跨组和order-based failover，证明同组与异组路径须分开。

选读范围：加密 reasoning 亲和性与 fallback 回归用例（静态阅读）。限制：只静态读列出测试及assert，未跑litellm或真实provider。 同机制实现的辅助回归测试核验，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/tests/unit/router_utils/pre_call_checks/test_encrypted_content_affinity_check.py)

<a id="protocol-audit-028"></a>

### protocol-audit-028 · LiteLLM Responses reasoning strip implementation

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：只检查list中type=reasoning且有encrypted_content的item；有可读摘要则去id/密文，无可读内容则删item；原地修改输入列表。

选读范围：Responses reasoning 清理分支。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。 同机制实现的配套helper核验，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/responses/utils.py)

<a id="protocol-audit-029"></a>

### protocol-audit-029 · LiteLLM Anthropic-shaped bridge reasoning

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：清除Anthropic-shaped messages时is_encrypted_reasoning_block仅识别LiteLLM Responses桥接前缀。

选读范围：Anthropic 消息桥接与 reasoning 转换分支。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。 同机制实现的配套helper核验，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/litellm_core_utils/prompt_templates/common_utils.py)

<a id="protocol-audit-030"></a>

### protocol-audit-030 · LiteLLM fallback hop integration

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：fallback hop在部署参数准备阶段调用strip helper，unmarked_origin指向刚失败部署；这不是通用history repair。

选读范围：Router 的 fallback 调用点。限制：辅助调用点与network-router源码交叉复核，不另计巨文件小段。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router.py)

<a id="protocol-audit-031"></a>

### protocol-audit-031 · LiteLLM previous-response deployment continuity

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：previous_response_id routing是另一开关路径；可识别且原部署healthy时pin，target_order存在则提前跳过。

选读范围：previous_response_id 的 deployment 连续性检查。限制：只裁决指定路径；未调用真实模型API，也未运行整个SDK测试套件。 同适配审计中的局部previous_response_id辅助helper，不作为额外独立来源计数。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/litellm/router_utils/pre_call_checks/deployment_affinity_check.py)

<a id="protocol-audit-032"></a>

### protocol-audit-032 · LiteLLM Responses deployment tests

作者／组织：LiteLLM maintainers。类型：源码／仓库文档。版本／日期：fixed repository commit 0976c0889a66bbdd51c77edc1876315c8e754493; pyproject 1.106.0, release mapping unverified。读取日：2026-10-13。 补充证据，不增加总数。

用途：测试区分有previous_response_id、无ID、不存在ID、多ID的路由情况；仅模拟调用目标，非跨provider state恢复证明。

选读范围：Responses deployment 连续性测试（静态阅读）。限制：辅助固定实现核对；测试未执行。

[公开原文](https://github.com/BerriAI/litellm/blob/0976c0889a66bbdd51c77edc1876315c8e754493/tests/unit/router_utils/pre_call_checks/test_responses_api_deployment_check.py)

<a id="tools-security-061"></a>

### tools-security-061 · MCP Versioning

作者／组织：Model Context Protocol。类型：官方文档／规范。版本／日期：Current 2026-07-28 verified 2026-10-13。读取日：2026-10-13。 补充证据，不增加总数。

用途：官方明确当前版2026-07-28，日期版本只在不向后兼容变化时递增。

阅读范围：Revisions; Negotiation。限制：仅作为版本定位证据，不额外计数。

[公开原文](https://modelcontextprotocol.io/specification/versioning)

<a id="protocol-audit-010"></a>

### protocol-audit-010 · Responses done native event type

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob 793edac97bfb2b8ed23d0c899f5b279a997e3d5b。读取日：2026-10-13。 补充证据，不增加总数。

用途：原生done仅声明arguments/item_id/output_index/sequence_number/type，无name或item。

选读范围：ResponseFunctionCallArgumentsDoneEvent 类型定义。限制：辅助确认同一PR契约，不把一个小类型文件另充新增来源。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/types/responses/response_function_call_arguments_done_event.py)

<a id="protocol-audit-011"></a>

### protocol-audit-011 · Chat stream helper event types

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob d4c1f28300b4f63da95a87613e78c6f4a4e897b7。读取日：2026-10-13。 补充证据，不增加总数。

用途：Chat辅助事件tool_calls.function.arguments.done明确带name/index/arguments/parsed_arguments；名称与原生Responses事件不同。

选读范围：FunctionToolCallArgumentsDoneEvent 类型定义。限制：仅事件类型辅助复核，未把多个类型文件拆成来源计数。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/streaming/chat/_events.py)

<a id="protocol-audit-016"></a>

### protocol-audit-016 · Published unsafe-finish regression tests

作者／组织：Vercel AI SDK maintainers。类型：源码／仓库文档。版本／日期：ai@7.0.70; blob ae0aa433eee8205a61a8f4b0e490f401c174ee9f。读取日：2026-10-13。 补充证据，不增加总数。

用途：发行版测试覆盖length/error/content-filter/other时即使参数对象有效execute仍不调用。

选读范围：unsafe finish reason 的工具执行回归测试（静态阅读）。限制：辅助核验同一个补丁的回归，不另计小段测试。

[公开原文](https://github.com/vercel/ai/blob/ai%407.0.70/packages/ai/src/generate-text/execute-tools-from-stream.test.ts)

<a id="runtime-boundaries-017"></a>

### runtime-boundaries-017 · AI SDK release boundaries 7.0.130-138

作者／组织：Vercel。类型：源码／仓库文档。版本／日期：ai@7.0.138 / 543d42cdda96e2ecb59c0a28f197067b96b5ac8d。读取日：2026-10-13。 补充证据，不增加总数。

用途：7.0.130修复abort时pending promise与reader；7.0.136才修复模型内容timer不覆盖本地工具且每retry刷新；7.0.138处理resume重复parts与匹配tool输出对象。补丁版本也能改变harness可观察语义。

选读范围：7.0.136, 7.0.130, 7.0.138 release entries。限制：固定 7.0.138 tag 对应 commit 的 CHANGELOG L1–210 已复读，具体 timer 另与7.0.136固定实现交叉核验。 辅助核验实现的版本发布边界，不作为额外独立来源计数。

[公开原文](https://github.com/vercel/ai/blob/543d42cdda96e2ecb59c0a28f197067b96b5ac8d/packages/ai/CHANGELOG.md)

<a id="protocol-audit-020"></a>

### protocol-audit-020 · Anthropic schema transformation tests

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0; blob 7a2799dced9310db6547c680a1e0dcda46939e84。读取日：2026-10-13。 补充证据，不增加总数。

用途：原维护者测试展示minimum/default进入description、object额外字段关闭等实际变换。

选读范围：schema transformation 相关测试。限制：辅助同模块固定版本验证，不另计测试片段。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/tests/lib/_parse/test_transform.py)

<a id="protocol-audit-021"></a>

### protocol-audit-021 · Anthropic typed parse response validation

作者／组织：Anthropic。类型：源码／仓库文档。版本／日期：v1.0.0; blob ee8326e5f7a7072ed2ffdfed79fea347a1f3eb36。读取日：2026-10-13。 补充证据，不增加总数。

用途：parse_text使用TypeAdapter(output_format).validate_json，表明使用该typed helper时原类型校验会再次发生。

选读范围：parse_text / parse_response。限制：短实现用于界定helper路径，不声称所有create/raw schema路径自动校验。

[公开原文](https://github.com/anthropics/anthropic-sdk-python/blob/v1.0.0/src/anthropic/lib/_parse/_response.py)

<a id="protocol-audit-035"></a>

### protocol-audit-035 · OpenAI Chat auto-parser guards

作者／组织：OpenAI。类型：源码／仓库文档。版本／日期：v3.9.0; blob 7a1bded1de9f8066ee4035dc71156e7db30dd2a3。读取日：2026-10-13。 补充证据，不增加总数。

用途：validate_input_tools拒绝非strict工具；length/content_filter在parse阶段抛专门异常。

选读范围：Chat 自动解析的前置检查与 chat resource 调用点。限制：本地SDK方法约束而非服务端400；不等同create接口约束。 局部类型/helper/parse守卫的辅助核验，不作为额外独立来源计数。

[公开原文](https://github.com/openai/openai-python/blob/v3.9.0/src/openai/lib/_parsing/_completions.py)

<a id="r3-audit-005"></a>

### r3-audit-005 · time.monotonic clock contract

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3.15 文档；读取于 2026-10-14。读取日：2026-10-14。 补充证据，不增加总数。

用途：Python 文档说明该单调钟在进程间共享；应核对钟域与启动纪元，不能一概断言单调读数跨进程无意义。

选读范围：time.monotonic 条目及跨进程同钟、参考原点、实现与版本变化说明。限制：短 API 契约作时钟边界佐证，不提供跨主机或重启后的可移植业务到期保证；不增加总数。

[公开原文](https://docs.python.org/3/library/time.html#time.monotonic)

<a id="r3-literal-002"></a>

### r3-literal-002 · tempfile.mkstemp permissions

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3.15 文档；读取于 2026-10-14。读取日：2026-10-14。 补充证据，不增加总数。

用途：mkstemp 在支持权限位的平台创建不可执行的临时文件；替换可执行产物前须明确所需权限。

选读范围：tempfile.mkstemp：创建权限、可执行位、句柄关闭与删除责任。限制：短 API 契约佐证，不重复计数；不要求盲复制 owner、ACL、setuid 等全部安全属性。

[公开原文](https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp)

<a id="r3-literal-003"></a>

### r3-literal-003 · os.replace atomic replacement contract

作者／组织：Python Software Foundation。类型：官方文档／规范。版本／日期：Python 3.15 文档；读取于 2026-10-14。读取日：2026-10-14。 补充证据，不增加总数。

用途：os.replace 以源对象替换目标路径；成功时的原子性不构成旧目标权限自动继承的承诺。

选读范围：os.replace：源到目标替换、已有目标文件、跨文件系统失败与成功时原子性。限制：短 API 契约作元数据边界佐证；权限故障由 API 契约与另行报告的本地演示合并解释，未在此重跑。

[公开原文](https://docs.python.org/3/library/os.html#os.replace)

<a id="network-errors-063"></a>

### network-errors-063 · Stream — buffering, writable.write and backpressure

作者／组织：Node.js。类型：官方文档／规范。版本／日期：Node.js v26.11.1 live documentation, read 2026-10-13。读取日：2026-10-13。 补充证据，不增加总数。

用途：writable.write返回false后生产者应等待drain再继续写；若忽略信号继续写，缓冲可增长至内存耗尽，因此设置阈值本身不等于实现背压。

选读范围：Buffering; Event:drain; writable.write (lines951–979); Three states/readableFlowing (line1032); pipeline (lines3562–3595)。限制：只读Buffering、drain、writable.write、Readable状态与pipeline相关段落，未运行Node。作为既有流式执行机制的补充核验，不增加主计数。不能外推暂停本地流会停止远端模型生成。

[公开原文](https://nodejs.org/api/stream.html)

<a id="r3-literal-004"></a>

### r3-literal-004 · rate: concurrent admission and reservations

作者／组织：Go Authors。类型：官方文档／规范。版本／日期：在线包文档；读取于 2026-10-14。读取日：2026-10-14。 补充证据，不增加总数。

用途：共享 Limiter 在允许后续事件时计入已有预留；未执行动作可取消预留，体现先准入、再执行的资源约束。

选读范围：Limiter 并发安全与 token 消费；ReserveN；Reservation；CancelAt；SetLimitAt 的既有预留边界。限制：补充 API 例子，不额外计数；补充 token 的速率限制不是一次性总费用封顶，动态改限额也有既有预留边界。

[公开原文](https://pkg.go.dev/golang.org/x/time/rate)

<a id="durable-orchestration-042"></a>

### durable-orchestration-042 · Agent-scaling analysis changelog

作者／组织：Yubin Kim and agent-scaling contributors。类型：源码／仓库文档。版本／日期：v2.2.0–v2.2.2 accessed2026-10-13。读取日：2026-10-13。 补充证据，不增加总数。

用途：v2.2.0修正分析误纳10个out-of-sample行，260而非270行；旧脚本未复现论文回归值，修正后可复现。

阅读范围：https://raw.githubusercontent.com/ybkim95/agent-scaling/main/CHANGELOG.md v2.2.0–v2.2.2。限制：分析脚本修正不等于实验结果被否定；experimental code保持2.1.3，不将此描述成造假 既有论文的分析CHANGELOG辅助核验，不作为额外独立来源计数。

[公开原文](https://github.com/ybkim95/agent-scaling/blob/main/CHANGELOG.md)

[返回分类目录](README.md#topics)
