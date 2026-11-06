# Coverage and verification status

Reviewed integration snapshot: **2026-11-06T02:45:11.467919Z**.

## Actual central coverage

| Measure | Verified snapshot | Interpretation |
|---|---:|---|
| Explicit normalized model identities | 9 | Only names in inspected result observations; modes/swarm not extra models |
| Benchmark/protocol records | 52 | 41 catalog entries plus distinct report protocol/version records; not 52 completed deep studies |
| Model–benchmark observations | 42 | D1 source-reported values; no local model inference |
| Concepts | 8 | Evidence-linked working definitions |
| Source records | 222 | Includes discovered candidates and repeated index pointers |
| Unique source URLs | 181 | URL uniqueness does not mean full-document review |
| Evidence records | 106 | Claim-level records with scope and limitations |
| Fully checklist-reviewed deep studies | 0 | Four benchmark source-path case studies published; full checklist review remains open |
| Full benchmark reproductions | 0 | No real model/full task-set run |

Model-report snapshot: **94 report/index/version candidate records, 19 D1 and 75 D0**. This is not a 94-model inventory. Benchmark catalog: **41 entries, 36 D1, 4 scoped D3 and 1 D0** after conservatively downgrading SimpleQA pending a real dataset-row inspection.

Source inspection statuses: **146 partially read records; 76 discovered records**. Exact per-source access times were not measured for most retrievals: their exact timestamp remains null and the verified read/discovery date is retained. Do not fabricate midnight UTC timestamps.

## Claim-level depth distribution

| Depth | Evidence records | Scope |
|---|---:|---|
| D0 | 1 | Video-MME candidate only |
| D1 | 90 | Catalog facts, report observations and labeled conceptual synthesis |
| D2 | 1 | Terminal-Bench legacy bn-fit-modify task/resource contract |
| D3 | 7 | Specific execution paths, not all framework/provider branches |
| D4 | 7 | Claims from four executed local diagnostic programs, not seven full benchmarks |

The four executed programs are BrowseComp parser probe, Harbor/OSWorld provider-policy mock tests, isolated official scoring functions, and synthetic statistics. No Docker/VM, cloud sandbox, browser benchmark or paid model API run is claimed.

## Published section scope

- **01 Models:** immutable v1 source/report registry and 42 observation tuples. Five-hour and 200-model targets remain unfinished.
- **02 Landscape:** representative 41-entry catalog; not exhaustive. Video-MME is D0. Protocol versions must remain distinct.
- **03 Cases:** BrowseComp, SWE-bench, original OSWorld, current τ-bench source traces, plus one parser-only mock probe.
- **04 Infrastructure:** deployment/isolation distinction; OSWorld V2.1 provider lifecycle; resource-budget case; 15 mocked/provider-policy assertions.
- **05 Runtime:** Harbor single-step/installed-agent/verifier trace; OSWorld/BrowserGym and selected MiniWoB paths.
- **06 Science:** validity/design; grading/metrics; scoped official-scorer and synthetic-statistics experiments.
- **07–09:** scaffolds only. No complete blind-spot map, curriculum, or accepted architecture is claimed.

## Integration checks performed

- Parsed all central CSV/JSONL files, checked unique IDs, foreign keys, evidence entity IDs, artifact paths and depth rules using `data/validate_indexes.py`.
- Re-ran statistical_diagnostics.py and scorer_diagnostics.py in a separate temporary copy; both outputs match the retained original JSON exactly. This validation does not create an additional model result or benchmark reproduction.
- Parsed every staged Python script; retained original upstream-source blob/hash provenance.
- Source snapshots/raw copied upstream code and active research ledgers are excluded from this publication.
- Credential-pattern scanning and changed-path review are performed before publishing. The scan is a precaution, not a universal guarantee.

## Known gaps and next priorities

1. Extend the actual model entity inventory, distinguishing families, aliases, checkpoint IDs and deployed API identities.
2. Review source-path cases against the full deep-study checklist, explicitly documenting uninspected licensing, splits, controls, reproducibility and statistical issues.
3. Preserve OSWorld original versus V2.1 and τ-bench current versus historical protocol distinctions; do not transfer scores across them.
4. Inspect actual SimpleQA rows; extend video/audio and undercovered task domains.
5. Integrate later stable research snapshots separately; do not overwrite immutable v1 or infer coverage from unfinished files.
6. Continue active research toward the requested duration; no five-hour completion claim at this checkpoint.

All model results remain `comparability_status=unassessed`; no global ranking is supported by this snapshot.
