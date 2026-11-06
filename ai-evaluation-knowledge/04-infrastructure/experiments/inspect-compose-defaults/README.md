# Inspect Compose 默认配置：5 个局部实验

**D4 只针对配置选择/生成，不是 Docker 网络隔离实测。** 学习目标 L2。

固定 Inspect commit：`7cf09c929b3ea9138762ca9e4d8d23f119554ee6`。

## 输入文件

1. [`docker/config.py`](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/util/_sandbox/docker/config.py)：6722 bytes；Git blob `cfdd5335f41e927ca7d141870a349ed5246a5a40`；SHA-256 `283fdcee2cc2b8dac5e75ed479cd9d28e5187a530dde6f7d2a7051e8dab336cb`。
2. [`compose.py`](https://github.com/UKGovernmentBEIS/inspect_ai/blob/7cf09c929b3ea9138762ca9e4d8d23f119554ee6/src/inspect_ai/util/_sandbox/compose.py)：17446 bytes；Git blob `f3464f95ae8258bb851ffeb9b1c74bc427faa36e`；SHA-256 `c549e9a06e4343d3522b0391c1a3c5994941bdf615c930eefc9ef50d2d9dfada`。

## 运行

保存原始字节后：

```sh
python3 run_compose_tests.py /path/to/config.py /path/to/compose.py
```

本环境已预装 PyYAML6.0.3；未安装任何依赖。脚本要求 PyYAML 已存在，不会自动下载。无 Docker、无模型调用、无网络或付费资源。

两个源文件均先验证完整 Git blob。完整 config module 原样执行；compose.py 只通过 AST literal-eval 提取4个文件名/目录常量，不执行其他代码。appdirs 重定向到测试创建的临时目录，package import plumbing 用 stub 替代。YAML 解析与文件读写为真实操作。

## 结果与范围

[result.txt](result.txt) 保存实际 `2026-11-06T03:09:58.905413+00:00` 的5个 PASS：

- generic synthesized Compose 包含 network_mode none；
- Dockerfile synthesized Compose 同样包含 none；
- custom Compose 原样使用，未合并默认网络/init 字段；
- custom Compose 优先于 legacy auto file；
- central generated Compose 使用绝对 build context，并保留 none。

测试没有启动任何容器，不支持“网络包已被拒绝”“custom Compose 一定能连公网”或“整个 Inspect 安全”的结论。它证明 config resolution 路径的输出；运行态边界需额外验证。
