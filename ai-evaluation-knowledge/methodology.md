# Research methodology

## Research objective

Build an extensible account of how AI evaluation is specified, executed, measured, and interpreted. Breadth helps discover important systems; depth establishes what those systems actually do. The 200+ model seed and 50 benchmark deep-study targets are planning goals, not quotas that justify weak evidence.

## Unit of work

Keep these units separate:

- **Model:** a named and versioned checkpoint or service. A family, alias, endpoint, and checkpoint may need separate relationships, but must not be silently counted as distinct trained models.
- **Benchmark:** a versioned dataset, task suite, or evaluation protocol. Variants with materially different splits, metrics, tools, budgets, or grading are not interchangeable.
- **Framework:** infrastructure implementing task loading, model interfaces, execution, scoring, aggregation, or reporting.
- **Evidence:** a specific claim linked to a source and a precise locator or experiment artifact.
- **Model–benchmark result:** one evaluation result under a specified protocol, with provenance and known comparability limits.

## Evidence-depth ladder

| Depth | What must have happened | What must be recorded | What it does not establish |
| --- | --- | --- | --- |
| D0 | A candidate/source was discovered. | Name, discovery URL or source, reason for inclusion, next verification step. | Correctness of any substantive claim. |
| D1 | Relevant primary report, paper, or official documentation was read. | Exact source, inspected section/page, supported claim, version/date, limitations. | That the implementation matches the document, or that a result was reproduced. |
| D2 | Actual task/configuration/key source code was inspected. | Repository and revision where available, file and symbol/line locators, concrete behavior, remaining gaps. | Complete source-level execution flow or runtime behavior. |
| D3 | The execution path was followed across the relevant source components. | Entry point, configuration resolution, data path, model invocation, output processing, scoring, aggregation, and unresolved branches. | That the code was run, or that external components behaved as assumed. |
| D4 | An actual experiment was executed. | Command/config, environment and revision, inputs/split, model identity, seeds and budgets, logs, outputs, measurements, and limitations. | Broad generalization beyond the tested setup or independent reproduction of all published results. |

Use the highest depth justified for **each evidence record**, not a blanket depth for an entire model or project. Index summary depth means the highest supported evidence depth linked to that entity; it must not imply that every property is verified to that depth. If a D4 experiment is exploratory and the implementation has not been traced, record that gap instead of inventing D2/D3 coverage. Published authors' experiments remain external D1 evidence until independently executed here.

## Source and claim discipline

1. Prefer original papers, official technical reports, official documentation, datasets, code repositories, release notes, and model cards.
2. Use secondary sources for discovery or contextual interpretation, with their role labeled.
3. Store source metadata in `data/sources.jsonl`. Record actual access time; distinguish publication date from access date.
4. Store supported claims in `data/evidence.jsonl`, with source IDs and precise locators. A source's existence is not evidence that it supports every nearby claim.
5. Mark observations as `reported`, `source_inspected`, `experiment_observed`, or `interpretation`. Label uncertainty directly.
6. Preserve conflicting findings. Differences can reflect versions, prompts, budgets, sampling, or scoring rather than errors.
7. A missing field means unknown or unverified. Do not fill it using typical defaults or extrapolation.

## Model seed review

For each candidate, identify organization, canonical name, family, version/release, modalities, availability, primary source, and aliases where supported. Keep a candidate at D0 if only discovered. Deduplicate exact aliases and checkpoint mirrors before counting. Keep model families and individual variants distinguishable. Do not infer licenses, parameter counts, context limits, or availability from neighboring models.

A 200+ seed inventory is meaningful only with identifiable entities and provenance. It does not mean 200+ models were tested or deeply analyzed.

## Benchmark deep-study checklist

Each substantive case study should address these dimensions, explicitly marking unknown or uninspected items:

- Intended construct, task domain, and what successful performance is supposed to mean.
- Dataset origin, versions, splits, size, access, license, and known overlap/leakage issues.
- Input/output schema, concrete example shape, prompt/template, few-shot policy, and preprocessing.
- Task definition/configuration, implementation entry points, and relevant dependencies.
- Model interface, inference settings, tool permissions, runtime/sandbox assumptions, retries, and timeouts.
- Response parsing, exact scorer or grader, metric units/direction, aggregation, and invalid/missing output handling.
- Evaluation budgets, sample counts, variance/uncertainty, cost, and sensitivity to protocol choices.
- Published results with exact protocol qualifiers and independent evidence boundaries.
- Limitations, failure modes, contamination controls, and unresolved questions.
- Reproduction recipe or a precise explanation of what prevents reproduction.

A placeholder, search result, or summary paragraph does not count as a deep study. A completed deep-study count requires a substantive case artifact, evidence links, at least inspected task/configuration or key implementation evidence (D2), and a review of this checklist. Publish depth distributions alongside totals. D3 source traces and D4 experiments are separate achievements; do not imply all deep studies reached them. If implementation is inaccessible, keep the case useful but label it documentation-only and exclude it from an implementation-backed deep-study total.

## Infrastructure analysis

Follow the sequence: task selection → configuration resolution → data loading → sample construction → model/API request → execution and retry policy → output normalization → scorer/grader → aggregation → report/artifact. Record file/symbol/line references and the exact code revision. Identify behavior crossing into external services or dependencies that were not inspected. A D3 trace may use source inspection alone and must say so.

## Result comparability

Never merge raw model scores solely because the benchmark name matches. Compare benchmark version, split, prompt, shots, model version, inference parameters, sample count, pass@k or other sampling budget, tool access, grader version, aggregation, and date. Record original value and units. Any normalized value needs an explicit transformation and evidence. Distinguish authors' claims, independent published evaluations, and experiments run in this workspace.

Missing protocol fields are comparability gaps, not permission to assume equivalence. No new ranking should be produced from incomparable results without a clear qualification.

## Executed experiments

Before execution, state the question, hypothesis if any, setup, controls, budget, and success/stop criteria. Do not use private data or incur paid API charges without the required authorization. Preserve failed and partial runs. Record whether the model was remote or local, exact available version information, data subset, commands, package versions, seeds, resource limits, and any nondeterminism. Save raw logs and machine-readable outputs when feasible. Report measured results separately from interpretation.

## Review and handoff

For each completed batch:

1. Validate source links, evidence locators, and stable IDs.
2. Deduplicate entities and preserve aliases without inflating counts.
3. Validate CSV/JSONL syntax and foreign-key references.
4. Check whether each claimed depth meets its criteria.
5. Refresh coverage from the indexes, while noting section artifacts not yet ingested.
6. Update `RESUME.md` with the last completed step, concrete next action, and blockers.

Do not mark a task complete because a folder exists. Do not claim scheduled continuation or a running experiment without verifying it.
