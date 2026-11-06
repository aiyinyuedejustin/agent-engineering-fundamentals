# 镜像、缓存与 run identity：复现不只是固定 Git commit

研究日期：2026-11-06。学习目标：L2 → L3。

证据范围：Docker/Kubernetes 官方文档 D1；SWE-bench 当前 image builder 与 report-cache 调用路径 D3；`run_instance` 的缓存命中分支在合成文件上狭义 D4。没有构建镜像，没有启动 Docker，没有运行 SWE-bench 数据集或评分测试。

固定 SWE-bench commit：`02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`，本轮读取日期 2026-11-06。所有源码结论只针对这个版本。[P1–P4]

## 1. 先区分四种完全不同的 cache

| 缓存 | 主要目的 | 容易误以为的保证 | 真实应验证的键或状态 |
|---|---|---|---|
| Docker build layer cache | 加速环境构建 | 重新 build 就取到最新依赖 | Dockerfile、context、base image、外部依赖解析与 cache policy |
| node/daemon image cache | 减少 pull | 同一 tag 在所有主机相同 | 已解析 image/index digest、平台与 pull policy |
| benchmark report cache | 恢复中断任务 | 相同 task ID 就可复用旧分数 | prediction、任务/测试/评分器、环境、预算与协议 fingerprint |
| trial runtime/compile cache | 加速执行 | 清理某个失败任务只影响它 | namespace、ownership、删除范围、并发与初始冷热状态 |

这是本文的工程分类，不是某框架统一提供的保证。前几篇的 KernelBench cache-root 删除和 Firecracker backing-file 生命周期说明，缓存还会耦合不同 trial。

## 2. Dockerfile 相同，不必然得到同一镜像

Docker 官方说明：build cache 的 `RUN` 命中通常比较指令，不会自动检查包仓库是否更新。`COPY`/`ADD` 会检查相关元数据，但仅改变 mtime 不会使 cache 失效；build secret 内容变化也不自动使 cache 失效。[P5]

两个常见误解：

- `--no-cache` 使构建步骤重跑，但不等于拉取新的 base image；更新 base image 是 `--pull` 的另一项职责。[P6]
- 固定 `FROM ubuntu:24.04` 是固定 tag，不是固定内容。tag 可指向不同 image digest。即便固定 base digest，后续未锁版本的 apt/pip/git/download 步骤仍可能变化。[P6；后一句为由构建输入推导的结论]

所以“缓存导致旧依赖”与“无缓存导致新依赖漂移”都可能发生。解决方式不是永远禁用缓存，而是明确构建输入、保存最终 digest，并把环境更新当作有版本的实验条件变化。

**安全与复现的张力：** 固定 digest 不会自动获得安全更新。应维护可审计的环境升级与重新验证流程，既不能悄悄漂移，也不能为了复现无限期使用有已知风险的环境。[P6]

## 3. SWE-bench 当前源码揭示的 build / reuse 语义

官方 harness 概览介绍 base/env/instance 分层设计；但这次固定的当前源码把 `ImageSpec` 的输入定义为已生成 Dockerfile，`TestSpec` 假定实例镜像已准备好。理解现代调用路径要看真正构建的 Dockerfile/上下文，不能只根据旧模块路径推断层次。[P1–P4、P8]

### build 路径

`ImageSpec` 默认 tag 为 `latest`，支持 amd64/arm64 命名与 platform 映射。`build_instance_image()` 先查本地 image name；存在就跳过构建，不在该分支比较 Dockerfile 内容。[P2、P3]

`build_image()` 调用 `docker buildx build`，传入 platform、tag、Dockerfile、context、`--load`。`nocache` 为真才添加 `--no-cache`；该命令构造未添加 `--pull`。[P3]

`build_instance_images(force_rebuild=True)` 先移除对应 image，但其 worker payload 的 `nocache` 为 false。因此从这条函数路径看，**force rebuild 实例镜像不等于禁用 builder layer cache，也不等于更新 base image。** 这是源码语义，不是本轮 Docker 实测。[P3]

### evaluation 路径

`create_container()` 先 `images.get(test_spec.image)`，只在找不到时 pull。使用 mutable tag 的话，不同主机可能各自保留不同旧内容；如果实际传入的是 digest，则该类 tag 漂移问题不同。[P1:L89–101]

create call 设置 root user、`tail -f /dev/null`、`cap_add=["SYS_ADMIN"]`。源码注释说该 capability 为浏览器 sandbox 兼容而添加。这个局部调用没有声明 CPU/memory limit；不能因此断言外围 Docker daemon、宿主或服务没有限制。[P1:L116–142；P4]

**结论：** image digest 只锁 image，不锁 runtime capabilities、网络、挂载、宿主 kernel、资源配额或安全边界。环境 manifest 应同时记录这些项目。

## 4. Kubernetes 上相同 tag 还可能混出多个版本

官方文档明确：`IfNotPresent` 使用节点已有镜像；`Always` 每次请求 runtime pull/resolve，但已缓存层可复用，并不是每次下载全部字节。mutable tag 变化时，不同 Pods 可能运行旧/新内容的混合。[P7]

默认 pull policy 在创建对象时确定，不会因以后把 image 改成 `latest` 就自动更新为 `Always`。显式 digest 解决镜像内容身份问题，但多架构 index 还会指向不同平台 manifest，应记录实际平台与最终选中的内容。[P7]

镜像拉取本身也是调度延迟：镜像大小、node cache、registry 可达性和串/并行 pull 策略会影响 ready 时间。不能把所有 startup timeout 都归因于 agent 或任务难度。本文没有修改 kubelet 参数或运行 pull 压测。

## 5. 真实 report-cache 路径：相同 run ID 不代表相同实验

固定 `run_instance()` 建立目录：

```text
logs / run_id / normalized_model_name / instance_id / report.json
```

若 report 存在，函数直接读取返回，然后才可能创建 logger、container、应用 patch 或运行 tests。该命中分支没有检查当前 patch、image、timeout、test spec 的 hash。[P1:L251–273]

本研究把未修改函数的 AST 节点提取出来，只执行这个分支，对真实临时 JSON 文件测试：

- 改 `model_patch`，仍返回原 report；
- 改 `test_spec.image`，仍返回原 report；
- 改为 `skip_patch=True`，仍返回原 report；
- 改 run ID，缓存未命中，并被实验的保护钩子在 live evaluation 之前停止。[P9]

这证明 cache key 行为，不代表缓存设计本身一定有错。resume 通常期待同一个 run ID 的输入不变。**风险在于操作者重复使用 run ID，却误以为新输入已被重新验证。** 本轮没有在完整 CLI 上复现分数变化。

`get_dataset_from_preds()` 还会按 report existence 排除已完成实例。`rewrite_reports=True` 重新解析已有 test output，不执行新 patch 的测试。重新评分与重新运行是两种操作。[P1:L542–640、L258–271]

### 容器 identity 也是另一层键

container name 使用 `instance_id + run_id`，没有 model name；遇到已有同名容器会尝试 force remove，冲突时再添加时间后缀。[P1:L105–142]

工程推论：在共享 daemon 上，若两个不同模型的独立作业复用同一 run ID/instance，存在彼此干扰的可能。本文未运行这一并发场景，也没有删除任何真实容器。run identity 应在共享控制域中唯一，而不只是人类可读的标签。

## 6. 镜像之外的任务资产也要固定

当前 SWE harness 支持 binary `image_assets`，优先从指定 task repo 读取，否则从声明 URL 下载，失败记录 warning 并跳过。文件会在 eval 脚本应用测试补丁之后、test-output marker 之前恢复，以支持 expected.png 等二进制基准。[P1:L154–226、L351–369]

这意味着只保存 Docker image 不一定保存完整任务。资产 URL、镜像 repo revision、hash、测试脚本、log parser 都应进入 provenance。所读局部下载函数未执行内容 hash 校验；这不等于所有上游打包或发布环节都没有验证。

源码 `write_run_metadata()` 保存 dataset、split、task_repo 和创建时间，帮助以后正确重评分。这很有价值，但它并不单独构成完整的内容寻址实验 manifest。[P1:L479–512]

## 7. 最低可用 provenance 清单

以下为建议，不声称上述框架都已经实现：

1. benchmark release、代码 commit、任务集 revision、实际 task IDs 与顺序；
2. instruction、prediction patch/artifact、测试与 grader 的内容 hash；
3. image index digest、所选平台 manifest digest、Dockerfile/context 与依赖锁；
4. runtime/kernel、capabilities、挂载、网络、身份、资源 request/limit 与实际硬件；
5. trial seed、所有 timeout 起点、重试/有效样本政策、cache warm/cold 模式；
6. 外部服务 fixture、数据资产 hashes、不可变引用与必要时间条件；
7. 唯一 run/trial ID、旧 report 的 reuse 原因、原始日志、错误分类、cleanup 成功与 orphan 状态。

不应把 token、secret、完整凭据加入 manifest。需要能重建安全配置，不是复制权限材料。

## 8. 尚未运行的容器最小实验

在专用可用 Docker 环境中，用自建无敏感数据的小镜像：

- 固定 tag，替换其目标内容，比较“本地已有”“显式 pull”“固定 digest”的实际 image ID；
- 用受控本地依赖源分别测 build cache、no-cache、pull，区分三种概念；
- 更换 patch 与 test spec，确认不同 experiment fingerprint 不误命中旧 report；
- 两个独立 run 并发，检查 container/image/cache namespace 不互相覆盖；
- 正常与异常退出后审计残余容器、网络、volume、cache。

当前没有 Docker binary，以上实验未执行。已有 report-cache 实验仅使用 Python 标准库和临时 JSON 文件。

## 来源

- [P1] [SWE-bench run_evaluation.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/run_evaluation.py)，读取 create_container、asset staging、run_instance、run metadata、dataset/cache filtering 等路径。
- [P2] [image_spec.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/image_builder/image_spec.py)，全文。
- [P3] [docker_build.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/image_builder/docker_build.py)，全文。
- [P4] [types.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/types.py)；[image builder constants](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/image_builder/constants/__init__.py)。
- [P5] Docker [Build cache invalidation](https://docs.docker.com/build/cache/invalidation/)，D1，2026-11-06 阅读全文，可变文档。
- [P6] Docker [Building best practices](https://docs.docker.com/build/building/best-practices/)，D1，读取 cache、pull/no-cache、digest pinning 等相关段落，可变文档。
- [P7] Kubernetes [Images](https://kubernetes.io/docs/concepts/containers/images/)，D1，读取 tags/digests、pull policy、pull concurrency、multi-architecture 段落，可变文档，不以 latest 页代替具体集群版本。
- [P8] SWE-bench [Harness reference](https://www.swebench.com/SWE-bench/reference/harness/)，D1，可变概览文档。
- [P9] [report-cache 最小实验](experiments/swebench-report-cache/README.md)，函数片段 D4，记录原文件 hash、运行结果与保护边界。

所有 source read date 为 2026-11-06；精确单次访问时刻未记录。实验时刻以各自输出为准。
