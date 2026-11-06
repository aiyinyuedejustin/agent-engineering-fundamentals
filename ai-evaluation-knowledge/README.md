# AI evaluation knowledge base

This is a persistent, evidence-first research workspace for understanding AI models, benchmarks, evaluation infrastructure, and evaluation science. It is a work in progress, not a completed survey or leaderboard.

**Start or resume:** read [RESUME.md](RESUME.md), [methodology.md](methodology.md), and [research-status/coverage.md](research-status/coverage.md).

## Scope and quality targets

- Discover a broad seed inventory of **200+ models**, including distinct model families, versions, and deployment forms where useful.
- Develop **50 benchmark deep studies** with substantive evaluation-protocol and implementation analysis.
- Explain the infrastructure that connects model inference, task data, prompts, execution, scoring, aggregation, and reporting.
- Investigate limitations such as contamination, leakage, variance, grader reliability, comparability, cost, and reproducibility.

These are research targets, not completed counts or permission to pad an inventory. A model alias is not a distinct model. A list entry is not a deep study. Missing evidence remains missing.

## Workspace map

| Path | Purpose |
| --- | --- |
| `01-model-landscape/` | Model discovery, taxonomy, and model-level research. |
| `02-benchmark-landscape/` | Benchmark discovery, taxonomy, and landscape research. |
| `03-benchmark-cases/` | Benchmark case studies and implementation analysis. |
| `04-infrastructure/` | Evaluation frameworks, serving, orchestration, and execution paths. |
| `05-agent-runtime/` | Agent execution, task environments, and runtime contracts. |
| `06-evaluation-science/` | Measurement issues, methodological case studies, and experiments. |
| `07-unknown-unknowns/` | Uncovered risks, blind spots, and open questions supported by observations. |
| `08-learning-path/` | Progressive learning modules grounded in reviewed research. |
| `09-architecture-decisions/` | Evidence-backed design alternatives, decisions, and consequences. |
| `data/` | Central machine-readable indexes and their schema. |
| `research-status/` | Coverage, verification gaps, and handoff state. |

The numbered folders reflect the current research layout. Research in other sections can precede ingestion into the central indexes.

## Evidence depth

- **D0 — discovered:** a candidate or source has been found.
- **D1 — primary documentation:** an official report, paper, or documentation has actually been inspected.
- **D2 — implementation inspected:** real task definitions, configuration, or key implementation code has been inspected.
- **D3 — source-level execution trace:** the execution path has been followed through source, with concrete entry points, transformations, and scoring behavior documented.
- **D4 — experiment executed:** an actual experiment was run, with a recorded setup, outputs, and limitations.

Depth belongs to the evidence supporting a claim. A repository link alone is not D2. A source trace is not an executed experiment. A published result is not our reproduction. See the methodology for promotion criteria.

## Current state

The central indexes were initialized as empty, schema-only files on **2026-11-06 UTC**. Their empty state does not assert that all other sections are empty. Coverage must be recalculated after evidence is reviewed and ingested. Do not present targets as achievements or treat draft notes as verified findings.

## Working rules

1. Preserve original sources, dates, exact model/benchmark versions, and relevant code revisions.
2. Separate reported results, inspected implementation behavior, and locally observed results.
3. Record uncertainty, contradictory evidence, unsupported assumptions, and uninspected steps explicitly.
4. Update indexes and status only after checking the supporting artifact.
5. Keep credentials, account tokens, private datasets, and unnecessary personal data out of this workspace.

## Publication and work accounting

The requested destination is an independent folder in a suitable existing repository selected through the user's GitHub connector. The verified destination is `aiyinyuedejustin/agent-engineering-fundamentals`, branch `main`, under the new `ai-evaluation-knowledge/` folder. This first increment contains only the scaffold and empty indexes. Research increments are published after review, preserving unrelated repository files.

The request includes at least five hours of research across parallel research streams. This is an outstanding work requirement, not elapsed-time evidence of completion. Record actual research activity and artifacts; waiting alone does not count as active research.
