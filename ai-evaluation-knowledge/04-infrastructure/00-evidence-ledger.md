# Evaluation infrastructure: evidence ledger

Research date: 2026-11-06 (UTC). Nine bounded evidence subsets have been closed for the accompanying articles; extension questions remain open below. This folder is a targeted infrastructure research branch, not a shared project index. It is not a claim that the full research program or its requested time commitment is complete.

## Questions and scope

1. When do agent evaluations require containers, complete guest operating systems, bare-metal hosts, or managed cloud services?
2. Which isolation controls protect the host, and which change the capability being measured?
3. What is the complete environment lifecycle, and where do reset, timing, resource, network and cleanup failures distort scores?
4. How do real benchmark implementations expose these tradeoffs?

In scope: SWE-bench, OSWorld/OSWorld V2, Terminal-Bench/Harbor, Inspect/Kubernetes, KernelBench, WebArena, a bounded HumanEval execution attempt, and underlying virtualization/isolation specifications. Out of scope: inference-server optimization and a full survey of every sandbox vendor.

## Depth and learning labels

- D0: discovered, unverified.
- D1: official report, paper or documentation checked.
- D2: real task, configuration and key code read.
- D3: source-level execution flow traced.
- D4: actually run, reproduced or experimentally checked.
- L0: awareness; L1: understanding; L2: practical; L3: engineering.

A learning label describes the learning target of a note, not proof that a learner has mastered it. No D4 is claimed merely from reading examples.

## Collection register

| ID | Primary source family | State / bounded depth | Why it matters |
|---|---|---|---|
| I01 | OSWorld-V2 release manifest, Docker provider/manager, DesktopEnv | D3 for lifecycle; provider-only mocked D4 | Full guest OS, nested virtualization, image/release consistency, reset |
| I02 | SWE-bench harness docs, run_evaluation, ImageSpec/buildx | D3 for inspected cache/build/evaluation paths; report-cache AST branch D4 | Image identity, reuse, patch/asset staging, report provenance |
| I03 | Inspect sandbox docs and Docker config source | D1 docs; generated/custom Compose code D4 with import/appdir stubs | Control plane versus sandbox, replacement rather than merging of config |
| I04 | Inspect K8s security/concurrency docs, manager/Helm/lifecycle/chart, selected tests | D3 lifecycle only; tests read, not run | Queue/deadline/ready/cleanup, gVisor, egress, cloud identity |
| I05 | Terminal-Bench/Harbor resources, errors, separate verifier and network phases | D1 docs; error_policy/single_step/network plan/phase/web controls D3; pure error policy code D4 | Resource semantics, invalid trials, verifier lifecycle, independent tool/network planes |
| I06 | gVisor, Firecracker, Linux nested KVM, Kubernetes and Docker docs | D1; real local mmap mechanism D4 only | Threat model, snapshot reset, mutable images, cache and host requirements |
| I07 | Terminal-Bench legacy/bn-fit-modify task/config/Dockerfile/tests | D2; not run | Resource contract, pinned/unpinned dependencies, statistical verifier |
| I08 | KernelBench task/config/eval/timing/batch/cache plus NVIDIA MIG docs | D2 task, D3 selected execution/timing paths; cleanup AST function D4 | GPU allocation, clock/stream/caches, cross-sample cleanup interference |
| I09 | Anthropic infrastructure-noise empirical report | D1; no reproduction | Same model/harness can produce materially different scores under different resources |
| I10 | WebArena browser lifecycle, task JSON, backend deployment, runner/retry scripts | D2 selected real tasks and D3 reset/retry source; static JSON audit only | Browser reset is not backend reset; retries do not undo service mutations |
| I11 | HumanEval official data/execution modules, task1, README | Source/task path read; actual full-task attempt blocked before candidate execution | Local IPC can be required even for offline CPU evaluation; README/source safety-state drift |

## Version anchors

- OSWorld V2.1 tag tip: `3d778a3c9a34a079316f70df023b166700445792`; release manifest's code base_commit is a separate field.
- SWE-bench current source: `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`.
- Harbor source: `26f95e0ebd8c77011bbf4656f5c98af66ce55848`; latest release read separately as v0.25.0, not conflated with source tip.
- Terminal-Bench source used for bn-fit-modify: `fbf8a8c02fd1ef7151b5bbb460baed51c15803dd`.
- Inspect source: `7cf09c929b3ea9138762ca9e4d8d23f119554ee6`; latest release read separately as 0.3.287.
- Inspect K8s: `4fb5fcdecb81d01e1c4d7b4b971cbe54c67d00bb`; agent-env chart0.14.0.
- Firecracker v1.17.0: annotated tag resolves to `95f868c8e345b1cc8faccd1a3c910b4989dc3f58`.
- KernelBench: `423217d9fda91e0c2d67e4a43bf62f96f6d104f1`; pyproject0.2.0.dev0.
- WebArena: `dce04686a56253aefba7b18a4fa0937cf1dc987b`; canonical implementation, not the newer recommended AgentLab/BrowserGym integration.
- HumanEval: `b9453e8f1865df0a0057a1383767caa400acfbcf`; deprecated and unmaintained notice present.

Claim-near source IDs, exact URLs and reading scopes are in each article. Source access precision is date-only unless an actual execution timestamp is saved. Do not infer exact fetch times from file modification times.

## Actual local execution, with boundaries

- `experiments/mock-provider-contracts`: 15 tests, PASS. Actual Harbor error policy and OSWorld provider code with external providers mocked; no Docker/VM runtime.
- `experiments/private-mapping`: 3 tests, PASS. Actual Linux mmap and temporary file operations; no Firecracker execution.
- `experiments/kernelbench-cache-scope`: actual unchanged upstream AST function on synthetic temporary files. Broad cache-root deletion reproduced; no CUDA execution.
- `experiments/swebench-report-cache`: actual unchanged upstream AST cache branch with temporary JSON. Changed patch/image/skip_patch reuse old report under same key; live evaluation blocked. Initial local fixture omitted one constant, corrected and rerun; disclosed.
- `experiments/inspect-compose-defaults`: 5 PASS, complete upstream config module executed with import/appdir plumbing stubbed, actual preinstalled PyYAML and filesystem. No Docker or network enforcement test.
- `experiments/humaneval-single-task`: BLOCKED before candidate or official assertions. `multiprocessing.Manager` socket creation returned EPERM, parent received EOFError. No successful HumanEval task-level D4, no retry or restriction bypass.

No dependency installation, cloud resources, model API calls, credential transmissions or paid execution were performed by these experiments.

## Measured checkpoints, not an active-time estimate

| Actual UTC output | Event |
|---|---|
| 2026-11-06T02:28:01Z | Capability check: Python3.12.14, no Docker binary, no /dev/kvm |
| 2026-11-06T02:38:46Z | Final hash-verified mock-provider test run, 15 PASS |
| 2026-11-06T02:44:24Z | Working files and evidence ledger checkpoint |
| 2026-11-06T02:48:48.857332+00:00 | Actual mmap experiment, 3 PASS |
| 2026-11-06T02:53:14Z | GPU probe: no nvidia-smi, no /dev/nvidia0, no installed torch |
| 2026-11-06T02:54:16.458958+00:00 | KernelBench cleanup function experiment |
| 2026-11-06T02:57:04Z | Six stable article checkpoint |
| 2026-11-06T03:00:13.725224+00:00 | Corrected SWE report-cache experiment, PASS |
| 2026-11-06T03:03:38Z | Effective-budget visibility probe: CPU count/affinity9; root cgroup files not visible |
| 2026-11-06T03:09:58.905413+00:00 | Inspect Compose config experiment, 5 PASS |
| 2026-11-06T03:20:35Z | Read-only check after HumanEval failure: multiprocessing default IPC family AF_UNIX; no socket retry |
| 2026-11-06T03:26:42Z | WebArena article/cross-reference checkpoint |

These are observed checkpoints, not exact continuous active-work accounting. They neither establish the original start time nor prove a five-hour research duration. Parallel work must not be summed into wall-clock duration.

## Open questions and next falsification steps

- No KVM/cluster/GPU E2E experiments were possible in the current selected environment. A real provider run remains necessary to verify timing, isolation, cleanup and semantic equivalence.
- OSWorld V2.1 complete gated task dataset was not accessed. Task-level execution and provider-equivalence claims remain unverified.
- Cgroup files (`cpu.max`, `memory.max`, `pids.max`, `cpu.stat`, `memory.current`) were not visible at `/sys/fs/cgroup` in the local probe. This does not establish unlimited resources; effective host limits remain unknown. No alternative restricted filesystem was accessed.
- KernelBench's L2-flush placement in host timing is a source-derived question needing real GPU timeline measurement, not a proven timing error.
- SWE-bench report-cache behavior is proven for one function branch, not every CLI workflow. Full run fingerprinting and multi-model container-name interference require controlled end-to-end tests.
- Old/mutable cloud provider docs can conflict with current source. Verify each capability against the exact provider and installed version before designing a new experiment.
- WebArena shared-service risks are source-derived; no measured interference, state reset or performance result is claimed. Canonical shard placement must not be confused with arbitrary parallelization.
- HumanEval's attempted original execution path is blocked by local IPC restrictions. The precise lower-level restriction mechanism is not established. Do not replace IPC or move execution outside the restriction to turn this into an artificial pass.

## Important collection caveats

- Web results now expose OSWorld V2 release `osworld-v2.1`. Do not silently use 2024 OSWorld or 2025 OSWorld-Verified setup guidance as if it were the same benchmark.
- Some mutable documentation makes absolute reproducibility claims. Treat these as the project's stated purpose, not proof that all host/platform differences are eliminated.
- An initial Harbor URL was unavailable through web retrieval. This is a retrieval failure, not evidence that Harbor or its documentation is unavailable.
