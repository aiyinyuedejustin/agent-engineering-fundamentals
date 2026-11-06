# Infrastructure second checkpoint

Recorded date: 2026-11-06 UTC. This is an incremental evidence checkpoint, not proof of five hours of work or a statement that the overall research is complete.

New stable articles beyond the first ledger:

- 10-browsergym-reset-scheduling-contract.md: subsystem D3; 7 local AST/mock checks passed.
- 11-androidworld-device-state-contract.md: actual task/config D2, selected lifecycle D3; 5 local AST/mock checks passed.
- 12-firecracker-jailer-and-orchestrator-boundaries.md: selected native/OCI jailer, launch, cleanup and snapshot paths D3; Go selector experiment blocked before compilation, 0 tests.

Observed execution/checkpoint timestamps:

| UTC | Event |
|---|---|
| 2026-11-06T03:37:31.246231+00:00 | BrowserGym reset/dependency probe, 7 PASS |
| 2026-11-06T03:41:27Z | Read-only check found prior /tmp source caches missing; shared deliverables intact, cause undetermined |
| 2026-11-06T03:45:27.036232+00:00 | AndroidWorld lifecycle probe, 5 PASS |
| 2026-11-06T03:49:32Z | Firecracker deeper source pass checkpoint |
| 2026-11-06T03:51:46Z | Tool availability check: PATH go found; rustc/cargo not found on PATH |
| 2026-11-06T03:53:21.790969+00:00 | Go-selector experiment stopped at failed go-version prerequisite, no compilation |
| 2026-11-06T03:53:53Z | Read-only toolchain path/file checkpoint; no dependency installation |

These are real measured checkpoints, not exact start/end times for continuous active research. Parallel workers' time must not be summed as wall-clock duration. The initial stable ledger remains unchanged so previous publication snapshots retain their meaning.

No new cloud resources, KVM/Android/Docker/runc instances, model API calls or credentials were used. The blocked HumanEval operation was not retried. Subsequent experiments were unrelated no-network mock work.
