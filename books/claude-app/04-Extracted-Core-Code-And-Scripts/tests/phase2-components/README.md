# Phase 2: density, reading size and Quick Entry

These additional tests exercise the original study demo, not Claude. The baseline `../demo-state/` files remain unchanged. This directory reuses its pinned jsdom 26.1.0 and simulated browser fixtures; no new dependency or package lock is introduced.

## Run

From the book root:

```sh
npm ci --prefix 04-Extracted-Core-Code-And-Scripts/tests/demo-state --ignore-scripts --no-audit --no-fund
node 04-Extracted-Core-Code-And-Scripts/tests/demo-state/run.cjs
node 04-Extracted-Core-Code-And-Scripts/tests/demo-state/static.cjs
node 04-Extracted-Core-Code-And-Scripts/tests/phase2-components/run.cjs
node 04-Extracted-Core-Code-And-Scripts/tests/phase2-components/static.cjs
```

Installing the baseline test dependency may require the npm registry or a local cache. The demo itself needs no dependency or network service. The test execution uses local source files only. The phase-2 runners resolve jsdom from the baseline harness's installation, so a second npm install is not required.

The new runners produce:

- `04-Extracted-Core-Code-And-Scripts/tests/results/phase2-components-test.json`: 32 simulated-DOM cases
- `04-Extracted-Core-Code-And-Scripts/tests/results/phase2-components-static.json`: 10 static source, DOM and CSSOM declaration checks

Generated reports are ignored by Git and do not overwrite published baseline evidence. The state runner records source hashes before/after testing and fails if files change during a run. Each failure exits nonzero. Run the unchanged 46 baseline cases and 6 baseline static checks alongside these tests.

## Scope

- Original compact/comfortable geometry is local to the specimen: control minimum 40/48 px, icon 16/20 px, padding 12/20 px, gap 8/12 px, radius 8/12 px.
- Original message size is an independent 14/16/18 px axis; tests check DOM attributes, CSS declarations, unchanged drafts and no additional persistence.
- Quick Entry has its own context, input, composition state and latest-record capture. Tests cover plain/modified Enter, IME guards, Escape, drafts, clearing, length protection, literal text sinks, synthetic height clamping and independence from the complete composer.
- Explicit Stop, inspector simulation and Retry restore focus after disabling/hiding their trigger. Passive completion/failure do not steal focus. A stop before the first content chunk replaces the waiting placeholder and has no Copy action.
- New static checks compare visible labels with declared geometry and verify label references, explicit typography boundaries, relative resources and selected-state styling.

## Limits

All baseline fixture limitations still apply: matchMedia, dialog, visibility, inert reflection, timers and clipboard are simulated. New cases do not measure CSS variable resolution, computed font sizes, rendered dimensions, actual target sizes, reflow, screenshot pixels, focus enforcement, native default editing, real IME or screen-reader output. A synthetic 320 px media fixture is not a 320 px visual test. CSSOM inspection records declarations, not a successful cascade or layout.

The focus changes respond to parent-reported observations in a real-browser preview of the baseline. Passing these new synthetic regressions is not a claim that the changed preview was revalidated in a browser. Browser results must identify the version and tested scope separately.

Quick Entry is an original in-page capture example, with no native window, global shortcut, outside-click dismissal, system context integration or persistent data. Nothing in these tests proves the researched product's live behavior. The demo makes no model/business API requests; HTTP previews naturally request their static assets.
