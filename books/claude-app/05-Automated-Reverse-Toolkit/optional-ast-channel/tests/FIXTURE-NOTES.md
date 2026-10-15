# Synthetic AST candidate fixtures

This fixture set is newly authored synthetic JavaScript and intentionally unsupported syntax. No product input, extracted product name, imported target, or executed target is included. Only public-facing rule spellings from the original local scanner were used as matcher vocabulary.

`fixtures.json` is a top-level array. Each record has `id`, `source`, `expected_status`, `expected_candidates` (category/key objects), and `notes`. Compare candidate pairs as a multiset; do not depend on traversal order. A `scan-incomplete` result must not masquerade as a successful empty scan or return partial candidates. Every result remains a static candidate report with `semantic_completeness_proven: false` in a separate AST channel/schema.

Coverage includes each of five lexical false-positive traps in isolation and with a subsequent real-call control, actual calls inside template interpolation expressions, all default call spellings, direct/member calls, static template names, comments/strings/regex, dynamic/concatenated/escaped names, computed callees/keys, method/accessor exclusions, ObjectExpression properties, unsupported TypeScript/JSX, malformed JavaScript, length boundaries, and Unicode/emoji anchors. The Unicode fixture additionally supplies zero-based half-open UTF-8 byte ranges for complete quoted literals, including quotes.

Object schema markers are unassociated: nearby names and tool calls cannot convert them into proven contracts. Event fields use the same unescaped static-name rule as call arguments, including no-substitution templates. Computed properties and non-init methods/accessors are excluded. Static traversal may identify real calls inside method bodies or interpolation expressions without executing them or proving runtime identity/reachability.

Validation may parse source strings but must never evaluate, import, require, or execute fixture source. Node `--check` is a syntax-only smoke test, not Acorn-specific verification or evidence of semantic completeness. The consuming adapter's Acorn test run remains the authoritative contract check.

Author validation: all 52 records matched their expected syntax status under Node syntax-only checking (45 valid JavaScript, 7 intentional parse failures); both Unicode byte anchors were independently verified by slicing UTF-8 bytes. No fixture source was executed. The consuming test runner subsequently verified all 52 fixtures using the explicitly marked Node-internal Acorn 8.17.0 test dependency; this is not a successful production external-package integration test.
