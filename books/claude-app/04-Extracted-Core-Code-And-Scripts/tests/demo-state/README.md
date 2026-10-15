# Original demo: simulated state regression tests

This harness tests the **original local study demo**, not Claude or an authenticated product. It does not launch a browser, use a login or contact an external service. No author files are modified.

## Reproduce

From the downloaded publication root (the directory containing `README.md`, `01-Frontend-Design-And-HTML-Templates` and `04-Extracted-Core-Code-And-Scripts`), with Node.js 18 or newer and npm installed:

```sh
npm install --prefix 04-Extracted-Core-Code-And-Scripts/tests/demo-state --ignore-scripts --no-audit --no-fund
node 04-Extracted-Core-Code-And-Scripts/tests/demo-state/run.cjs
node 04-Extracted-Core-Code-And-Scripts/tests/demo-state/static.cjs
```

The dependency is pinned to **jsdom 26.1.0**, and `package-lock.json` pins the transitive dependency tree. For stricter lockfile-only installation, substitute `npm ci --prefix 04-Extracted-Core-Code-And-Scripts/tests/demo-state --ignore-scripts --no-audit --no-fund` for the install command. Do not delete or regenerate the lockfile to reproduce this reviewed dependency tree.

Dependency installation uses the official npm registry (or an existing local npm cache), and may need internet access. Test execution reads the local book files and does not need a server, browser, login or external service. The demo itself has no npm dependency; jsdom is only a test dependency. Tested with Node v24.19.0, npm 11.9.0 and jsdom 26.1.0 on Linux.

Each runner creates `04-Extracted-Core-Code-And-Scripts/tests/results/` if needed and writes only its generated JSON report there:

- `04-Extracted-Core-Code-And-Scripts/tests/results/demo-state-test.json`: 46 state/interaction cases in a simulated DOM
- `04-Extracted-Core-Code-And-Scripts/tests/results/demo-state-static.json`: 6 static checks and 60 source-color calculations

The directory is gitignored. A failed check exits nonzero. The state runner compares the six demo/component source hashes before and after execution; a source change invalidates the run. The static report records the same six files. Source paths in both reports are relative to the downloaded book root. No code file is changed by these tests.

Published reference results are in [`data/demo-state-test.json`](../../evidence/data/demo-state-test.json) and [`data/demo-state-static.json`](../../evidence/data/demo-state-static.json), with the [review explanation](../../evidence/data/demo-state-test.md) and [repaired findings history](../../evidence/data/demo-state-findings.json). Re-running the suite never overwrites those references. Timestamps and environment fields vary by run; the checks and source hashes can be compared directly. The broader [scenario specification](../../evidence/data/design-test-scenarios.json) includes many browser-only checks that remain unrun; do not treat this suite's passing cases as passes for every mapped scenario.

## What the harness does

- Evaluates the actual `evidence.js` and `demo.js` in an isolated DOM with actual HTML and locally inlined CSS.
- Drives submit, click, keyboard, composition and media-change events.
- Uses deterministic timers, including replaying a canceled callback to test generation-ticket guards.
- Injects denied/malformed storage and clipboard fixtures.
- Records attempted fetch/XHR/WebSocket/EventSource/beacon calls and fails tests if they occur.
- Checks narrow drawer state, ARIA attributes, inert flags, endpoint Tab handlers and focus-return calls.
- Statically checks IDs, labels/references, relative assets, network dependencies and key CSS branches.
- Calculates opaque-token contrast pairs from source values using WCAG relative luminance, without rounding a below-threshold value up to a pass.

## What it cannot establish

This is **simulated DOM testing**, not browser testing. The harness supplies matchMedia, timers, dialog open/close, visibility rectangles, missing inert property reflection and an innerText fallback. It does not implement actual layout, native modal top-layer behavior, focus containment, inert enforcement, the accessibility tree, default Tab movement, real CJK input method composition, native Shift+Enter editing, actual clipboard permissions, file:// security or browser resource loading.

Visibility rectangles model only selected source-declared visibility conditions. They test the app's focus-management logic, not the screen. `dialog.close()` in this harness dispatches a close event, but native Escape, backdrop painting and focus containment require a real browser. A synthetic composition pass is not proof of real IME behavior.

A jsdom 27.4.0 exploratory harness exhibited incorrect scoped comma-selector ordering for `Element.querySelectorAll`; that version was replaced by pinned 26.1.0. Other exploratory false positives were corrected in the test harness: nonempty Shift+Enter must leave Send enabled, and cross-realm clipboard promises need a host event-loop turn. Neither was an application defect.

The test runner's passed checks must not be relabeled as browser, screenshot, layout, accessibility, WCAG, offline-loading or product-behavior passes. The full reviewer scenarios remain partly unrun.
