# Independent review: optional AST candidate channel

Review date: 2026-10-15. Scope: the original staging prototype, its design contract, and original synthetic fixtures/tests. No product inputs were read; no target JavaScript was executed or imported; no network access or installation was performed. The reviewer changed only this review file, not implementation, publication, or git state.

## Conclusion

The final reviewed revision passes the 89-test synthetic suite and 36 additional independent final assertions. The concrete budget, error-normalization, and line-location defects found during review were fixed by the implementer and independently rechecked. No unresolved defect was found in those reviewed supported paths.

This is **not verification of the genuine external Acorn package success path**. `acorn/dist/acorn.js` is not resolvable in this environment. Successful parsing was tested only with the explicit Node-internal Acorn 8.17.0 test mode, which is correctly marked `testing_only=true`. Synthetic external dependency stubs test rejection paths only. A release support claim still requires testing a trusted genuine installed Acorn 8.17.0 package through `--acorn-module`.

This remains a bounded static syntax-candidate prototype. It is neither a semantic inventory nor an operating-system/RSS sandbox.

## Exact final revision reviewed

SHA-256 values were checked before and after final verification:

- `ast_candidates.py`: `42de4412758e4c9f101e446482f9f4dab9d3179d00a780d83f7a2bd0b8a807cd`
- `ast_worker.cjs`: `6def4a9a4df09ed6e3a1ed101748b3987e34a4e12569b51d275eab8487db56e5`
- `DESIGN.zh.md`: `7037109a195ffce40bf182f7f47dca1f2bc6f03734b45915d84fabc72a35445c`
- `tests/test_ast_channel.py`: `8c521a02bd90a5b05070a38866aaaa2988b92dbd36362655294a93dd04626c69`

Runtime: Node v24.19.0, its explicitly exposed internal Acorn 8.17.0, and Python 3.12.14 on POSIX.

## Findings discovered and disposition

### 1. Node allocation budget bypass through shorthand copies — fixed

The original subclass counted `startNode` and `startNodeAt`, but Acorn 8.17.0 also creates nodes directly in `copyNode`. Shorthand object/pattern properties use that path. The synthetic input `const a={x};` originally succeeded with `max_nodes=7` while traversal visited eight nodes.

The final worker overrides `copyNode` as well and adds a traversal node-count check. Independent inspection of the locally available parser prototype found the three direct `new Node` entry points to be `startNode`, `startNodeAt`, and `copyNode`. Final probes confirm that the example rejects at seven and succeeds at eight with eight recorded allocations. This was a real accounting/budget defect, not an execution vulnerability or evidence of unbounded memory.

### 2. Final CLI encoding exceeded the advertised output bound — fixed

The original worker checked compact JSON, but the launcher added identity metadata and emitted pretty JSON afterward. At the default 8 MiB bound, 20,000 synthetic `checkGate("x");` statements produced a successful report whose CLI-style output was 9,527,894 bytes. A lowered 16,384-byte cap also reproduced the issue with 30 calls.

The final launcher uses one compact UTF-8 wire serializer and checks the completed report, including identity metadata and the trailing newline. The independently executed CLI now emits **6,527,258 bytes** for the 20,000-call fixture, below 8,388,608 bytes. Additional lowered-cap probes and identity recomputation pass. Over-budget output becomes a zero-record `scan-incomplete` report.

### 3. Rejected source names could crash or enlarge failure output — fixed

Originally, a surrogate-escaped POSIX filename reached identity hashing and caused `UnicodeEncodeError`, yielding exit 1 and a Python traceback instead of JSON. Invalid bytes-valued names could cause `TypeError`; a rejected 20,000-character API name was echoed into a 21,115-byte failure report.

The final validator rejects surrogate code points, control characters, non-string names, and overlong names. Failure reports use the fixed `input.js` label for rejected names. Independent CLI verification with an actual synthetic filename containing byte `0xff` now returns exit 2, valid zero-record JSON, and no stderr. All invalid-name probes remain below a lowered 4,096-byte output bound.

### 4. Malformed dependency metadata and limit configuration escaped normalization — fixed

Non-object JSON package metadata originally raised `AttributeError`; a 20,001-byte, 10,000-level JSON array could raise `RecursionError`. Non-mapping `limit_overrides` also raised `AttributeError`.

The final code validates metadata root and override types and normalizes metadata recursion failure. Independent checks of list, null, string, deeply nested metadata, and list/integer/string overrides now return fixed-code `scan-incomplete` reports. No placeholder dependency module is loaded in these preflight rejection probes.

### 5. Line anchors counted only LF — fixed

Originally, candidates after CR, U+2028, or U+2029 had correct UTF-8 byte spans but incorrect line numbers. The final mapper recognizes ECMAScript line terminators and counts CRLF once. Independent checks cover LF, CR, CRLF, U+2028, U+2029, and consecutive CR/CRLF, with Unicode/astral characters inside the anchored literal. All pass.

## Verification performed

1. Ran all 52 original fixture records independently before fixes. All expected statuses, candidate multisets, and the supplied Unicode byte anchors matched. This includes all five known lexical false-positive traps and their real-call positive controls.
2. Ran the initial 79-test suite, then reran the final suite using `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`: **89 tests passed** in the final run. This includes the exact one-million-token boundary and its immediate over-limit rejection.
3. Executed 36 additional final assertions independently of that suite: shorthand allocation boundaries; six line-ending cases; invalid source names; malformed overrides and metadata; actual non-UTF8 POSIX filename handling; unknown input identity; actual CLI output size; lowered output caps; report identity recomputation; malformed/deep worker protocol responses.
4. Independently exercised the process controller with original trusted test snippets: a one-second wall timeout, a one-second CPU budget, oversized stdout, and oversized stderr. Each produced a fixed failure code; the wall timeout completed in about 1.01 seconds and the CPU probe in about 1.16 seconds. The suite separately verifies termination of the owned Popen handle and clean worker environment.
5. Verified exact/over-limit regular-file reads, immediate FIFO rejection, overlong/malformed UTF-8 encodings, UTF-8 BOM preservation, and literal byte slicing after BMP and astral characters.
6. Parsed synthetic side-effect-looking target text containing a file-write sentinel without creating the sentinel. Static and dynamic import syntax referencing nonexistent modules parsed without resolving those modules. These probes never execute fixture text.
7. Confirmed that a private synthetic marker in malformed target source does not appear in parser diagnostics. Worker stderr is bounded and discarded, not forwarded. The final unknown/unread input report uses `identity_available=false` with null size/hash rather than claiming an empty-file input identity.

## Boundaries that are implemented correctly

- **Input selection:** one explicitly selected regular, single-link file; bounded read; final symlink and non-regular-file rejection; descriptor identity and size/mtime checks. No recursive target discovery.
- **Input transport:** target bytes travel through stdin to the original worker. They are not a Node script, evaluated expression, imported module, or inferred dependency path. The CLI rejects a target/dependency path collision.
- **Dependency gate:** release path requires explicit `dist/acorn.js`, package name/version/main checks before loading, and an exported version/parser check after loading. Test mode is explicit, separate, and visible in output.
- **Parser controls:** token and node checks run during parsing; depth is checked during iterative traversal; output and record collection are bounded. Any observed parse, budget, protocol, or child-process failure returns no candidates and does not fall back to the old lexer.
- **Process controls:** empty child environment prevents inherited `NODE_OPTIONS`/`NODE_PATH` injection; fixed V8 old-space, semi-space, and stack settings; POSIX CPU/core limits; parent wall-clock control; bounded pipe capture. Cleanup targets only the newly created Popen handle, not a process group or discovered processes.
- **Private diagnostics:** fixed issue codes and bounded offsets replace parser exception text. No AST or source dump is emitted. Candidate literal names and the input basename are intentionally part of successful output and therefore still require private handling.
- **Anchors:** zero-based, half-open UTF-8 byte spans refer to the original bytes, including delimiters for literal candidates; BOM, BMP, and astral prefixes were checked. Source SHA-256 matches the bytes actually analyzed.
- **Channel isolation:** separate `original-ast-candidate-snapshot/v1`, fixed syntax-candidate analysis kind, `semantic_completeness_proven=false`, and `legacy_coverage_modified=false`. No reviewed code imports, rewrites, or merges legacy snapshots or changes default scanner behavior.

## Truthful limitations and remaining verification gate

These are scope boundaries, not defects concealed by a passing test count:

- **Genuine external dependency success remains unverified.** The final revision must be exercised against a trusted installed official Acorn 8.17.0 package before describing that distribution path as tested. Node's internal module is not a stable public dependency API.
- **Trusted dependency/runtime code executes.** `require` loads the explicitly chosen parser. Metadata and hashes identify bytes but do not authenticate the package, isolate malicious dependency code, or guarantee a concurrently mutable installation has not changed. Use a trusted, stable installation and trusted Node runtime.
- **V8 old-space is not total process RSS.** Buffers, source decoding, young-generation/native allocations, and Python-side objects are outside that one setting. No whole-process memory sandbox or hostile-dependency containment was established.
- **AST depth is a traversal limit, not a parser recursion limit.** Parsing happens first. Deep grammar may hit Acorn/stack/resource rejection before traversal reaches the configured depth check. Parent resource controls and fail-closed reporting remain important. An `ast-syntax-rejected` code with `input_validity=not-determined` must not be promoted into proof that input is semantically invalid.
- **Counts are not interchangeable.** Acorn token counts exclude EOF and differ from the legacy lexical measurement. Node allocations, visited nodes, records, and legacy facts are distinct counts; candidate totals must not be added across channels as unique discoveries.
- **Syntax candidates still include semantic false positives.** Independent probes correctly retained calls to a locally shadowed configured name, unreachable calls, and matching method names on unrelated receivers. No binding, reachability, alias/data-flow, receiver identity, or runtime registry proof is supplied.
- **Schema/event fields remain unassociated.** An object property or nearby tool call does not establish a tool contract or runtime telemetry definition.
- **Declared exclusions remain real.** Computed/dynamic names, concatenations, escaped names, aliases, JSX/TypeScript, and unsupported literal forms are not recovered. The `optional` field reflects the call node's own optional flag, not a proof about all enclosing optional-chain operations or execution.

No claim is made that these synthetic tests cover all Acorn grammar/resource behavior, all operating-system failure modes, real product inputs, or semantic inventory completeness.
