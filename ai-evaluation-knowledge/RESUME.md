# Resume entry

## Read first

1. `README.md` for scope and workspace layout.
2. `methodology.md` for D0–D4 evidence criteria and deep-study review.
3. `data/README.md` for index schemas and count rules.
4. `research-status/coverage.md` for the latest reviewed coverage state.
5. Current section reports and editing ownership, before editing any section files.

## Last completed step

On **2026-11-06 UTC**, the shared scaffold, methodology, central empty indexes, and sections 07–09 were initialized. The scaffold task did not inspect or modify other research sections. It did not populate research records, validate their findings, or run any experiments.

## Current checkpoint

- Workspace: the `ai-evaluation-knowledge/` folder in the research repository.
- Central CSV indexes: headers only.
- Central source/evidence JSONL indexes: zero records.
- Coverage: initialization baseline; artifacts in other sections still require review and ingestion.
- Targets: 200+ provenance-backed model seeds and 50 substantive benchmark deep studies; neither is claimed complete.
- Autonomous scheduling: none established by this checkpoint.

## Concrete next action

Inventory the current section artifacts, identify completed batches and active ownership, then review one completed batch for primary sources, stable model/benchmark identity, and justified D0–D4 depth. Ingest only supported records. Validate references and update coverage counts from actual records.

## Continuation order

1. Reconcile duplicate model aliases and benchmark variants before importing.
2. Create source records for actual sources, preserving publication/access dates and code revisions.
3. Add claim-level evidence with precise locators and limitations.
4. Add entity and result rows linked to those source/evidence IDs.
5. Review case-study completeness; do not count placeholders or documentation-only cases as implementation-backed deep studies.
6. Record uncovered risks and unresolved questions in `07-unknown-unknowns/`.
7. Add source traces and experiments only to their earned depth; preserve logs and manifests for actual runs.
8. Refresh coverage and this checkpoint with completed actions, next priorities, blockers, and explicit ownership.

## Handoff template

For each resumed batch, append a concise entry containing: UTC date/time; scope; files inspected; files changed; verified counts added; evidence depths reached; completed versus incomplete steps; precise blockers; and the next action. Do not paste secrets or unsupported totals.

## Publication and active-work continuation

The verified destination is `aiyinyuedejustin/agent-engineering-fundamentals`, branch `main`, new folder `ai-evaluation-knowledge/`. The first publication increment contains only this scaffold. For each later increment, refresh the remote head, preserve unrelated paths, publish reviewed files with non-force expected-head protection, and verify the resulting remote commit.

Continue the requested research for at least five hours of real active work across parallel research streams. Do not claim that waiting or elapsed clock time alone satisfies this. Record each substantive work batch and its outputs; duration completion remains outstanding at this checkpoint.
