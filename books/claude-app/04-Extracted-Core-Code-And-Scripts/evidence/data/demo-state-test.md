# Original demo state and component review

Portable-suite verification run: 2026-10-14T17:06:39.934Z  
Original reviewed run: 2026-10-14T16:55:39.395Z  
Environment: Node v24.19.0, jsdom 26.1.0, Linux. No browser was launched.

## Result

- **46 / 46 simulated DOM checks passed.**
- **6 / 6 static source/semantic checks passed.**
- **60 opaque token pairs calculated.** All tested non-decorative pairs meet their stated arithmetic thresholds after a correction. Decorative Clay is 2.9615:1 on the light canvas and must not be treated as normal text; the demo's author mark is aria-hidden.
- Three source-backed findings were repaired by the author and retested. No unresolved failure remains in the executed checks.
- Source hashes were unchanged throughout the final state-test run. Static and state reports identify the same six author files.

**These results do not establish a real-browser, visual, accessibility or WCAG pass.** Local browser execution was unavailable in the assigned environment. The test harness uses simulated browser surfaces, described below.

## Findings and repairs

### DS-01 · P2 · Resolved: navigation breakpoint focus

At narrow width, opening navigation focuses its mobile-only Close button. Widening to desktop removed modal state while leaving focus on the now-hidden Close. The author added focus recovery in `syncSidebar()`. Cases D35 and D38 now verify widening and narrowing logic. These are source-backed simulated results, not measured browser focus behavior.

### DS-02 · P2 · Resolved: inspector breakpoint focus

The compact inspector had the corresponding Close-button issue. The author added focus recovery in `syncInspector()`, including a previously collapsed desktop preference. D36, D39 and D40 now pass.

### DS-03 · P2 · Resolved: selected navigation number contrast

The light `.nav-item > span` used muted `#68665f` on selected `#e5e3db`, calculating to **4.471900:1**, below 4.5:1. The author darkened the original muted token to `#65635c`, which calculates to **4.679050:1**. This is an opaque source-pair calculation; actual rendered adjacency/cascade remains unmeasured.

The earlier findings are retained in `demo-state-findings.json`; they are not silently discarded by the passing final run.

## Executed coverage

### State and interruption logic

- Initialization; blank and whitespace submission; one send/completion cycle; Enter guard; Shift+Enter left to native editing.
- Compositionstart/end, `isComposing` and legacy keyCode 229 guards. **Synthetic events only; no real IME pass.**
- Repeated Enter and simulation clicks; rapid send becomes Stop; no duplicate pending job.
- Stop before completion; reset before and during streaming; new-session during pending error.
- Forced replay of canceled callbacks, including a stale callback after a new generation starts.
- Navigation during pending work preserves the user's selected section while the same conversation finishes.
- Failure keeps the submitted input; repeated retry adds no duplicate user message; a newer draft survives failure/retry.
- Hostile HTML, script, URI and long mixed text stay literal, with no child markup or instrumented network call.
- Draft survives theme and section changes. System theme is sampled at startup; valid persisted theme takes precedence. No user-selectable live system theme mode is promised.
- Denied storage access, quota denial, malformed values and unrelated storage preservation.
- Reduced-motion JavaScript branch produces one completed response after the initial wait.

### DOM semantics and focus-management logic

- Tab selection, roving tabindex, ArrowLeft/ArrowRight/Home/End and associated panel visibility.
- Repeated modal open/close, duplicate open guard, synthetic outside click, opener recovery and removed-opener fallback.
- A native-dialog close event simulated inside a drawer returns to its opener before the drawer closes.
- Narrow drawer and inspector roles, aria-modal, background inert flags, endpoint Tab handlers, Escape and scrim close.
- Repeated drawer cycles clear inert/scrim/scroll-lock state; media changes restore focus when panels or Close controls become hidden.
- Clipboard fulfillment feedback; rejected and missing clipboard APIs select text and explain manual recovery.
- Validation retains bad input, focuses the field and clears the error after repair; boundary toggles and specimen buttons update their intended states.

### Static source/component review

- Unique IDs and valid label, ARIA and SVG fragment references.
- Local linked assets exist and use relative paths; no CSS import/font/URL resource or executable network API was found in the reviewed original sources.
- Chinese document language, form labels, dialog labels, theme group, real tabs, native disabled buttons, status and alert attributes.
- Literal prompt sink, no destructive storage reset, reduced-motion CSS branch and short-height scrolling branch.
- Source-pair arithmetic for text roles across six surfaces, action/error/success/chip pairs, input boundaries and focus tokens in both themes. These checks are deliberately separate from decorative separators.

## Simulation boundaries and unrun review scenarios

The harness injects matchMedia, deterministic timers, storage/clipboard fixtures, dialog open/close, visibility rectangles, missing inert reflection and an innerText fallback. Visibility is modeled from selected author rules. The harness cannot enforce native inert, render a modal top layer, implement normal Tab order, draw pixels, use real fonts or run a screen reader.

Still unverified:

- Native dialog Escape, modal top layer, actual focus containment and inert background enforcement; actual accessible names/tree and announcements (A01–A03, A05–A07, A16–A17).
- Actual CJK IME and native newline editing (F03–F04).
- 320/390/768/1440 CSS-pixel layout, short heights, 200% zoom/text, text-spacing overrides, pointer hit areas, overflow and long-content rendering (Y01–Y04, A08–A11, O09).
- Real theme cascade, nested theme behavior, all composited/text pairs, focus/error/disabled state appearance and system-font fallback (T01, T04–T09, Y01–Y04).
- Forced colors and custom-switch rendering, actual reduced-motion appearance (A13–A14).
- Browser `file://` loading/security, cold-cache offline loading, real clipboard/storage permissions and browser network logs (O01–O03, O06, O08).
- Screenshots, visual similarity or any authenticated Claude behavior. This test subject is original example code only.

F12 apply/cancel and F13 search/no-results are not implemented promises and were not failed for absence. The reviewer matrix should retain its unrun or bounded status; these unit-style results must not be copied over as full scenario passes.

## Reproduce and artifacts

See [`04-Extracted-Core-Code-And-Scripts/tests/demo-state/README.md`](../../tests/demo-state/README.md). Commands from the downloaded book root:

```sh
npm install --prefix 04-Extracted-Core-Code-And-Scripts/tests/demo-state --ignore-scripts --no-audit --no-fund
node 04-Extracted-Core-Code-And-Scripts/tests/demo-state/run.cjs
node 04-Extracted-Core-Code-And-Scripts/tests/demo-state/static.cjs
```

- `data/demo-state-test.json`: portable-suite per-check results, environment, patches and source hashes.
- `data/demo-state-static.json`: portable-suite source checks and all 60 exact contrast calculations.
- `data/demo-state-findings.json`: repaired issue history and final hashes.
- `04-Extracted-Core-Code-And-Scripts/tests/demo-state/harness.cjs`: transparent browser-surface fixtures.
- `04-Extracted-Core-Code-And-Scripts/tests/demo-state/run.cjs`: repeatable state assertions.
- `04-Extracted-Core-Code-And-Scripts/tests/demo-state/static.cjs`: repeatable semantic/resource and contrast checks.

New runs write to `04-Extracted-Core-Code-And-Scripts/tests/results/demo-state-test.json` and `04-Extracted-Core-Code-And-Scripts/tests/results/demo-state-static.json`, leaving these published reference results unchanged. The JSON references were generated by running the portable suite in an isolated copy of the downloaded-book layout. Paths in this published report have been rebased to the book root; the original review date is retained above, and the checks, findings and source hashes are unchanged.

A jsdom 27.4.0 exploratory selector-order anomaly and two test expectation/timing errors were fixed in the harness, not reported as application defects. The final harness is pinned to jsdom 26.1.0.


## 当前快照

目录迁移后的当前源码再次通过 46 项基础状态检查、6 项基础静态检查；新增密度、阅读字号、Quick Entry 与焦点修复通过 32 项状态检查和 10 项静态检查。精确哈希与执行时间见同目录 JSON。

真实浏览器的首轮记录见 [browser baseline](demo-browser-baseline.json)，覆盖旧提交并发现焦点问题；不能以它替代当前改动的浏览器回归。
