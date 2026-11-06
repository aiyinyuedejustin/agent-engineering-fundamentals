# Central indexes and schemas

All CSV files use UTF-8, comma separation, one header row, and standard CSV quoting. Empty cells mean unknown/unverified, not zero or false. Multi-value ID and modality fields use semicolons. JSONL files contain one JSON object per line and no enclosing array. Empty JSONL files are intentionally valid empty indexes.

**Current records:** the fifth reviewed research batch is populated. See `../research-status/coverage.md` for counts and limits. Validate with `python data/validate_indexes.py`. Never add dummy rows or treat report candidates as model entities.

## Stable identifiers

Use readable lowercase IDs such as `model:<slug>`, `benchmark:<slug>`, `concept:<slug>`, `source:<slug>`, and `evidence:<slug>`. Include versions when needed to disambiguate. Examples here are naming conventions, not actual records. Keep an ID stable after publication; record aliases or replacements in notes rather than silently reusing it.

## `models.csv`

One row per explicitly identified model entity. Required for ingestion: `model_id`, `canonical_name`, `entity_type`, `source_ids`, `depth`, and `status`.

- `entity_type`: `family`, `checkpoint`, `api_model`, `alias`, or `other`; this prevents family/variant/alias count inflation.
- `parent_model_id` and `alias_of_model_id`: relationships to an indexed canonical entity when verified.
- `organization`, `family`, `version`, `release_date`, `modalities`, `availability`, `license`: source-backed values only.
- `official_url`, `repository_url`, `checkpoint_url`: URLs actually discovered, not constructed guesses.
- `source_ids` and `evidence_ids`: semicolon-separated foreign keys. D0 discovery may have source IDs without substantive evidence IDs.
- `depth`: highest linked evidence depth, or D0 for discovered candidates; not the depth of every property.
- `status`: `candidate`, `documented`, `implementation_inspected`, `source_traced`, `experimented`, or `needs_review`.
- `last_verified_utc`: actual most recent verification timestamp, ISO 8601 UTC; leave blank if not verified.

Count model seeds only after semantic deduplication. `identity_status` is `source_supported_label`, `named_voice_model_system`, or `unresolved_reported_condition`. `count_as_model_seed` is a literal true/false; current counts exclude named voice/delegation systems and unresolved conditions from the conservative model-seed total. `reported_labels` preserves the source labels grouped into each entity. These are not verified weight hashes or released-checkpoint counts. Do not silently discard unresolved observations: they remain linked to explicit excluded records.

The immutable v9/v12-additions identity audits explain every grouping. Reasoning modes, quantization, swarm and same-weight deployment differences remain in each observation. The HunyuanVideo resolution bucket is split by task metadata but excluded from the seed count until checkpoint identity is resolved.

## `benchmarks.csv`

One row per identified benchmark/protocol version. Required: `benchmark_id`, `canonical_name`, `entity_type`, `source_ids`, `depth`, and `status`.

- `entity_type`: `dataset`, `task`, `suite`, `protocol`, or `other`.
- `parent_benchmark_id`: verified suite/variant relationship.
- `version`, `domain`, `task_type`, `modalities`, `split`, `metric`, `metric_direction`: verified protocol descriptors.
- `official_url`, `paper_url`, `repository_url`, `dataset_url`: discovered source URLs.
- `case_study_path`: relative path to the substantive local case artifact, when present.
- `catalog_depth`: the catalog author’s scoped overall inspection depth for representative entries, kept separate from the highest linked claim `depth`. A component D4 does not promote catalog depth or establish whole-benchmark reproduction. Empty for report-only protocols outside the catalog.
- `deep_study_review`: `not_started`, `in_progress`, `reviewed_complete`, or `needs_review`. This is not inferred merely from depth or file existence.
- `status`: `candidate`, `documented`, `implementation_inspected`, `source_traced`, `experimented`, or `needs_review`.

A completed implementation-backed deep study requires `reviewed_complete`, an existing substantive case artifact, and linked D2-or-deeper evidence, following the methodology. Count D3 and D4 separately.

## `model_benchmark_evidence.csv`

One row per sourced result observation, not a synthesized leaderboard. Required: `result_id`, `model_id`, `benchmark_id`, `result_origin`, `source_ids`, `evidence_ids`, and `comparability_status`.

- `result_origin`: `source_reported`, `developer_reported`, `independent_reported`, or `local_experiment`. Use `independent_reported` only where the source record explicitly identifies an independent evaluator or benchmark author; otherwise retain `source_reported` rather than guessing whether the publisher measured, quoted or reran each cell.
- `model_version`, `benchmark_version`, `split`, `prompt_id`, `shots`, `sample_count`, `sampling_budget`, `inference_settings`, `tool_access`, `grader`, and `aggregation`: preserve protocol qualifiers or leave unknown.
- `score_raw`, `score_unit`, `metric`, `metric_direction`: original reported metric. Do not normalize silently.
- `uncertainty`: source-reported interval/error estimate or a clearly specified locally computed estimate.
- `evaluation_date`: date the evaluation occurred, if known; not automatically the paper date.
- `comparability_status`: `unassessed`, `protocol_matched`, `partially_matched`, or `not_comparable`, with a reason in `notes`.
- `artifact_path`: experiment manifest or raw-result artifact path for local experiments.

A numeric score alone is insufficient to establish equivalence to another score. Unknown values must not be replaced with zero.

## `concepts.csv`

One row per defined concept. Required: `concept_id`, `name`, `definition`, `source_ids`, and `status`. Definitions should distinguish measurement constructs from implementation mechanisms. `related_concept_ids` references this same file. `status` is `candidate`, `documented`, or `needs_review`.

## `sources.jsonl`

Each source object has:

- Required: `source_id`, `title`, `url`, `source_type`, `primary`, `accessed_at_utc`, `inspection_status`.
- Optional: `authors` (array), `organization`, `published_date`, `version`, `repository_commit`, `local_path`, `content_hash`, `license`, `notes`.
- `source_type`: `paper`, `technical_report`, `documentation`, `repository`, `code_file`, `dataset`, `model_card`, `release_note`, `article`, `task`, `original_experiment`, or `other`.
- `primary`: boolean describing whether the source is primary for the recorded claim context; explain mixed cases in notes. For a discovered candidate this describes the official destination, not verification of the target report.
- `inspection_status`: `discovered`, `read`, `partially_read`, `executed`, or `unavailable`.

For an original local experiment, `url` may remain null until publication is verified. In that case `source_type` must be `original_experiment`, with an existing `local_path` and matching `sha256`; do not invent a public URL. Source-record counts include these records, but unique external URL counts exclude null.

Only record access times for actual retrievals. If exact time was not measured, `accessed_at_utc` is null, `accessed_date` retains the actual date, and `access_time_precision` is `date`. A URL-only discovery does not mean the target content was read. Report candidates may share an official index URL; source-record count and unique-URL count are different. `read_scope` and `notes` preserve the actual inspected extent.

## `evidence.jsonl`

Each evidence object has:

- Required: `evidence_id`, `entity_ids` (array), `claim`, `claim_type`, `depth`, `source_refs` (array), `recorded_at_utc`, `verification_status`.
- Each `source_refs` item: `source_id`, `locator` (page, section, file/symbol/lines, or experiment artifact), and optionally `excerpt` or `notes`.
- `claim_type`: `reported`, `source_inspected`, `experiment_observed`, or `interpretation`.
- `depth`: `D0`, `D1`, `D2`, `D3`, or `D4`; satisfy methodology criteria.
- `verification_status`: `supported`, `partial`, `conflicted`, `unverified`, or `superseded`.
- Optional: `repository_commit`, `artifact_paths` (array), `execution_performed` (boolean), `limitations` (array), `contradicts_evidence_ids` (array), `supersedes_evidence_ids` (array), `review_notes`.

Model-result evidence uses `result_ref` to link the full settings in `model_benchmark_evidence.csv`, rather than duplicating every setting in JSONL. Immutable source observation JSON retains the original fields.

D4 synthetic experiments can have an empty external `source_refs` array when the actual script/results supply the evidence. Always include artifact paths and explicitly state synthetic/component scope.

For D3, document the source trace and explicitly mark `execution_performed: false` unless execution also happened. For D4, reference a completed experiment manifest and actual outputs; distinguish successful, failed, and partial execution. An interpretation must identify its supporting evidence and assumptions rather than claiming to be a direct quote.

## Validation before publishing counts

- Parse every CSV and JSONL file successfully.
- Check IDs are unique within each index and foreign keys exist.
- Check referenced paths exist and URLs/locators came from actual sources.
- Deduplicate aliases and mirrors before reporting totals.
- Count evidence depths from records, not filenames, intentions, or target numbers.
- Distinguish no record, not assessed, inspected but inconclusive, and verified absence.
