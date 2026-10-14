'use strict';
// New cases reuse the unchanged baseline's documented simulated-DOM harness.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createHarness, ROOT } = require('../demo-state/harness.cjs');
const baselineRequire = require('node:module').createRequire(require.resolve('../demo-state/harness.cjs'));
const results = [];
const files = ['01-Frontend-Design-And-HTML-Templates/interactive-study/index.html', '01-Frontend-Design-And-HTML-Templates/interactive-study/demo.js', '01-Frontend-Design-And-HTML-Templates/interactive-study/demo.css', '01-Frontend-Design-And-HTML-Templates/interactive-study/evidence.js', '01-Frontend-Design-And-HTML-Templates/styles/tokens.css', '01-Frontend-Design-And-HTML-Templates/styles/components.css'];
const hashes = () => Object.fromEntries(files.map(file => [file, crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, file))).digest('hex')]));
const before = hashes();
function test(id, title, fn, options = {}) {
  const h = createHarness(options);
  try {
    fn(h);
    assert.deepEqual(h.errors, [], 'Unexpected DOM/runtime error');
    assert.deepEqual(h.transmissions, [], 'Unexpected network API attempt');
    results.push({ id, title, status: 'pass', method: 'simulated DOM' });
  } catch (error) {
    results.push({ id, title, status: 'fail', actual: error.message, stack: error.stack });
  } finally { h.close(); }
}
function open(h) { h.click('[data-view="gallery"]'); h.click('#quick-entry-open'); }
function quickInput(h, text) { h.$('#quick-entry-input').value = text; h.$('#quick-entry-input').dispatchEvent(new h.w.Event('input', { bubbles: true })); }
function submit(h) { return h.$('#quick-entry-form').dispatchEvent(new h.w.Event('submit', { bubbles: true, cancelable: true })); }
function press(h, key, extra = {}) { return h.key(h.$('#quick-entry-input'), key, extra); }
function singleChoice(h, attribute, value) {
  assert.equal(h.$$(`[${attribute}][aria-pressed="true"]`).length, 1);
  assert.equal(h.$(`[${attribute}="${value}"]`).getAttribute('aria-pressed'), 'true');
}

test('P01', 'Initial independent dimensions and accessible selected state', h => {
  assert.equal(h.$('#density-example').dataset.density, 'compact');
  assert.equal(h.d.documentElement.dataset.messageSize, 'md');
  singleChoice(h, 'data-density-choice', 'compact'); singleChoice(h, 'data-reading-choice', 'md');
  assert.match(h.$('#density-metrics').textContent, /原创紧凑.*40 px/);
  assert.match(h.$('#reading-metrics').textContent, /16 px/);
  assert.equal(h.writes.length, 0);
});
test('P02', 'Density changes the specimen attribute without changing the reading axis', h => {
  for (const [choice, size] of [['comfortable', 48], ['compact', 40]]) {
    h.click(`[data-density-choice="${choice}"]`);
    assert.equal(h.$('#density-example').dataset.density, choice);
    assert.equal(h.d.documentElement.hasAttribute('data-density'), false);
    assert.equal(h.$('#composer').hasAttribute('data-density'), false);
    assert.equal(h.d.documentElement.dataset.messageSize, 'md');
    assert.match(h.$('#density-metrics').textContent, new RegExp(size + ' px'));
    singleChoice(h, 'data-density-choice', choice);
  }
});
test('P03', 'All six density/reading combinations keep the other axis and draft', h => {
  h.input('完整输入区的草稿');
  for (const density of ['comfortable', 'compact']) for (const [size, pixels] of [['sm', 14], ['md', 16], ['lg', 18]]) {
    h.click(`[data-density-choice="${density}"]`); h.click(`[data-reading-choice="${size}"]`);
    assert.equal(h.$('#density-example').dataset.density, density);
    assert.equal(h.d.documentElement.dataset.messageSize, size);
    singleChoice(h, 'data-density-choice', density); singleChoice(h, 'data-reading-choice', size);
    assert.match(h.$('#reading-metrics').textContent, new RegExp(pixels + ' px'));
    assert.equal(h.$('#message-input').value, '完整输入区的草稿');
    assert.equal(h.$$('.message--user').length, 1);
  }
});
test('P04', 'Theme, navigation and conversation reset retain in-page display preferences', h => {
  h.click('[data-density-choice="comfortable"]'); h.click('[data-reading-choice="lg"]');
  h.click('[data-theme-choice="dark"]'); h.click('[data-view="tokens"]'); h.click('#new-session');
  assert.equal(h.$('#density-example').dataset.density, 'comfortable');
  assert.equal(h.d.documentElement.dataset.messageSize, 'lg');
  assert.deepEqual(h.writes, [{ key: 'liubai-study-theme', value: 'dark' }]);
});
test('P05', 'Display preferences are page-only even when storage is unavailable', h => {
  h.click('[data-density-choice="comfortable"]'); h.click('[data-reading-choice="lg"]');
  assert.equal(h.d.documentElement.dataset.messageSize, 'lg');
  assert.equal(h.$('#density-example').dataset.density, 'comfortable');
  assert.deepEqual(h.writes, []);
}, { storageDenied: true });
test('P06', 'Malformed button choices cannot set unsupported attributes or text', h => {
  const density = h.$('[data-density-choice]'), reading = h.$('[data-reading-choice]');
  density.dataset.densityChoice = '__proto__'; reading.dataset.readingChoice = 'constructor';
  density.click(); reading.click();
  assert.equal(h.$('#density-example').dataset.density, 'compact');
  assert.equal(h.d.documentElement.dataset.messageSize, 'md');
});
test('P07', 'Quick Entry starts closed, empty and independent from the full composer', h => {
  assert.equal(h.$('#quick-entry-panel').hidden, true);
  assert.equal(h.$('#quick-entry-open').getAttribute('aria-expanded'), 'false');
  assert.equal(h.$('#quick-entry-submit').disabled, true);
  assert.equal(h.$('#quick-entry-result').hidden, true);
  assert.equal(h.$('#quick-entry-form').contains(h.$('#message-input')), false);
  assert.equal(h.$('#composer').contains(h.$('#quick-entry-input')), false);
  assert.equal(submit(h), false);
  assert.equal(h.state(), 'idle');
});
test('P08', 'Open focuses the text target and exposes the correct controlled region', h => {
  open(h);
  assert.equal(h.$('#quick-entry-panel').hidden, false);
  assert.equal(h.$('#quick-entry-open').getAttribute('aria-expanded'), 'true');
  assert.equal(h.d.activeElement, h.$('#quick-entry-input'));
});
test('P09', 'Plain Enter captures locally with selected context and leaves the conversation unchanged', h => {
  h.input('完整输入区草稿'); open(h); h.$('#quick-entry-context').value = 'ideas'; quickInput(h, '  一句话  ');
  assert.equal(press(h, 'Enter').defaultPrevented, true);
  assert.equal(h.$('#quick-entry-result-text').textContent, '一句话');
  assert.match(h.$('#quick-entry-result-context').textContent, /灵感/);
  assert.equal(h.$('#quick-entry-result').hidden, false);
  assert.equal(h.$('#quick-entry-input').value, '');
  assert.equal(h.$('#quick-entry-submit').disabled, true);
  assert.equal(h.$('#message-input').value, '完整输入区草稿');
  assert.equal(h.$$('.message--user').length, 1);
  assert.equal(h.state(), 'idle'); assert.equal(h.timers.size, 0); assert.equal(h.writes.length, 0);
});
test('P10', 'Native form submission is intercepted; repeat/empty submission does not overwrite', h => {
  open(h); quickInput(h, '第一条'); assert.equal(submit(h), false);
  for (const text of ['', ' \n\t　']) { quickInput(h, text); assert.equal(h.$('#quick-entry-submit').disabled, true); submit(h); press(h, 'Enter'); }
  assert.equal(h.$('#quick-entry-result-text').textContent, '第一条');
  assert.equal(h.$('#quick-entry-result').hidden, false);
});
test('P11', 'Modified Enter combinations never submit and leave native editing unhandled', h => {
  open(h); quickInput(h, '保留草稿');
  for (const extra of [{ shiftKey: true }, { altKey: true }, { ctrlKey: true }, { metaKey: true }, { shiftKey: true, ctrlKey: true }]) {
    assert.equal(press(h, 'Enter', extra).defaultPrevented, false);
    assert.equal(h.$('#quick-entry-result').hidden, true);
    assert.equal(h.$('#quick-entry-input').value, '保留草稿');
  }
});
test('P12', 'Composition state suppresses Enter, submit and Escape until compositionend', h => {
  open(h); quickInput(h, '中');
  h.$('#quick-entry-input').dispatchEvent(new h.w.CompositionEvent('compositionstart', { bubbles: true }));
  assert.equal(h.$('#quick-entry-submit').disabled, true);
  assert.equal(press(h, 'Enter').defaultPrevented, false); submit(h);
  assert.equal(press(h, 'Escape').defaultPrevented, false);
  assert.equal(h.$('#quick-entry-panel').hidden, false); assert.equal(h.$('#quick-entry-result').hidden, true);
  h.$('#quick-entry-input').dispatchEvent(new h.w.CompositionEvent('compositionend', { bubbles: true }));
  assert.equal(h.$('#quick-entry-submit').disabled, false); press(h, 'Enter');
  assert.equal(h.$('#quick-entry-result-text').textContent, '中');
});
test('P13', 'isComposing and legacy keyCode 229 each protect quick input independently', h => {
  open(h); quickInput(h, '中文');
  for (const extra of [{ isComposing: true }, { keyCode: 229 }]) for (const key of ['Enter', 'Escape']) {
    assert.equal(press(h, key, extra).defaultPrevented, false);
    assert.equal(h.$('#quick-entry-result').hidden, true); assert.equal(h.$('#quick-entry-panel').hidden, false);
  }
});
test('P14', 'Escape retains draft/context, restores opener, and reopens without data loss', h => {
  open(h); quickInput(h, '稍后继续'); h.$('#quick-entry-context').value = 'ideas';
  assert.equal(press(h, 'Escape').defaultPrevented, true);
  assert.equal(h.$('#quick-entry-panel').hidden, true);
  assert.equal(h.d.activeElement, h.$('#quick-entry-open'));
  assert.equal(h.$('#quick-entry-open').getAttribute('aria-expanded'), 'false');
  h.click('#quick-entry-open');
  assert.equal(h.$('#quick-entry-input').value, '稍后继续');
  assert.equal(h.$('#quick-entry-context').value, 'ideas');
});
test('P15', 'Dismiss button and keyboard Escape on context both preserve drafts', h => {
  open(h); quickInput(h, '草稿'); h.click('#quick-entry-dismiss');
  assert.equal(h.d.activeElement, h.$('#quick-entry-open')); h.click('#quick-entry-open');
  h.key(h.$('#quick-entry-context'), 'Escape');
  assert.equal(h.$('#quick-entry-panel').hidden, true); assert.equal(h.$('#quick-entry-input').value, '草稿');
});
test('P16', 'Quick Entry markup-looking input is a literal text sink', h => {
  open(h); const text = '<img src="https://example.invalid/x" onerror="window.bad=1"><script>window.bad=2</script> 中文';
  quickInput(h, text); submit(h);
  assert.equal(h.$('#quick-entry-result-text').textContent, text);
  assert.equal(h.$('#quick-entry-result-text').children.length, 0);
  assert.equal(h.w.bad, undefined);
});
test('P17', 'Only latest capture is retained and context snapshots do not mutate retroactively', h => {
  open(h); quickInput(h, '旧条目'); submit(h); h.$('#quick-entry-context').value = 'ideas';
  assert.match(h.$('#quick-entry-result-context').textContent, /收件盒/);
  quickInput(h, '新条目'); submit(h);
  assert.equal(h.$('#quick-entry-result-text').textContent, '新条目');
  assert.match(h.$('#quick-entry-result-context').textContent, /灵感/);
  assert.equal(h.$('#quick-entry-result').textContent.includes('旧条目'), false);
});
test('P18', 'Clear removes only the last record, retains draft and restores an available focus target', h => {
  open(h); quickInput(h, '记录'); submit(h); quickInput(h, '下一条草稿'); h.click('#quick-entry-clear');
  assert.equal(h.$('#quick-entry-result').hidden, true); assert.equal(h.$('#quick-entry-result-text').textContent, '');
  assert.equal(h.$('#quick-entry-input').value, '下一条草稿'); assert.equal(h.d.activeElement, h.$('#quick-entry-input'));
  submit(h); h.click('#quick-entry-dismiss'); h.click('#quick-entry-clear');
  assert.equal(h.d.activeElement, h.$('#quick-entry-open'));
});
test('P19', 'New observation clears capture/draft and restores the full composer focus', h => {
  open(h); quickInput(h, '记录'); submit(h); quickInput(h, '草稿'); h.click('#new-session');
  assert.equal(h.$('#quick-entry-panel').hidden, true); assert.equal(h.$('#quick-entry-result').hidden, true);
  assert.equal(h.$('#quick-entry-input').value, ''); assert.equal(h.$('#quick-entry-result-text').textContent, '');
  assert.equal(h.$('#quick-entry-context').value, 'inbox'); assert.equal(h.d.activeElement, h.$('#message-input'));
});
test('P20', 'Quick capture does not cancel or duplicate an active full-composer generation', h => {
  h.input('主输入区消息'); h.submit(); open(h); quickInput(h, '另一条速记'); submit(h);
  assert.equal(h.state(), 'generating'); assert.equal(h.$$('.message--user').length, 2);
  h.tick(20000); assert.equal(h.state(), 'complete'); assert.equal(h.$('#quick-entry-result-text').textContent, '另一条速记');
});
test('P21', 'Overlength programmatic input is rejected, retained, and recoverable', h => {
  open(h); quickInput(h, '中'.repeat(301)); submit(h);
  assert.equal(h.$('#quick-entry-submit').disabled, true); assert.equal(h.$('#quick-entry-input').getAttribute('aria-invalid'), 'true');
  assert.equal(h.$('#quick-entry-result').hidden, true); assert.equal(h.$('#quick-entry-input').value.length, 301);
  quickInput(h, '中'.repeat(300)); assert.equal(h.$('#quick-entry-input').getAttribute('aria-invalid'), 'false');
  assert.match(h.$('#quick-entry-status').textContent, /符合要求/); submit(h);
  assert.equal(h.$('#quick-entry-result-text').textContent.length, 300);
});
test('P22', 'Auto-height algorithm clamps synthetic scroll heights without resizing the composer', h => {
  open(h); const input = h.$('#quick-entry-input');
  for (const [scrollHeight, expected] of [[0, '26px'], [72, '72px'], [900, '120px']]) {
    Object.defineProperty(input, 'scrollHeight', { configurable: true, value: scrollHeight }); quickInput(h, '多行内容');
    assert.equal(input.style.height, expected);
  }
  assert.equal(h.$('#message-input').style.height, '52px');
});
test('P23', 'Hidden-panel programmatic submit cannot capture its retained draft', h => {
  open(h); quickInput(h, '保留'); h.click('#quick-entry-dismiss'); submit(h);
  assert.equal(h.$('#quick-entry-result').hidden, true); assert.equal(h.$('#quick-entry-input').value, '保留');
});
test('P24', 'New display and quick-entry interactions remain independent in a narrow media fixture', h => {
  open(h); h.click('[data-density-choice="comfortable"]'); h.click('[data-reading-choice="lg"]');
  quickInput(h, '窄屏本地记录'); submit(h);
  assert.equal(h.$('#quick-entry-result-text').textContent, '窄屏本地记录');
  assert.equal(h.$('#main-content').inert, false);
  assert.equal(h.$('#density-example').dataset.density, 'comfortable');
}, { width: 320, reduce: true, storageDenied: true });

test('P25', 'User Stop before first chunk restores composer focus and does not offer placeholder copying', h => {
  h.input('马上停止'); h.submit(); h.$('#send-button').focus(); h.click('#send-button');
  assert.equal(h.state(), 'stopped'); assert.equal(h.d.activeElement, h.$('#message-input'));
  const reply = h.$$('.message--assistant').at(-1);
  assert.equal(reply.querySelector('.streaming-text').textContent, '已停止，尚未生成内容。');
  assert.equal(reply.querySelector('.copy-reply'), null);
  h.tick(20000); assert.equal(h.state(), 'stopped');
});
test('P26', 'User Stop after a chunk retains real text and copy action', h => {
  h.input('停止部分文字'); h.submit(); h.tick(800);
  const reply = h.$$('.message--assistant').at(-1), partial = reply.querySelector('.streaming-text').textContent;
  h.$('#send-button').focus(); h.click('#send-button');
  assert.equal(h.d.activeElement, h.$('#message-input'));
  assert.equal(reply.querySelector('.streaming-text').textContent, partial);
  assert.ok(reply.querySelector('.copy-reply'));
});
test('P27', 'Passive generation completion does not take focus from another input', h => {
  h.input('后台继续'); h.submit(); open(h); quickInput(h, '速记草稿'); h.tick(20000);
  assert.equal(h.state(), 'complete'); assert.equal(h.d.activeElement, h.$('#quick-entry-input'));
  assert.equal(h.$('#quick-entry-input').value, '速记草稿');
});
test('P28', 'Stop in narrow inspector releases inert background before restoring composer focus', h => {
  h.input('待停止'); h.submit(); h.click('#inspector-toggle'); h.click('[data-tab="states"]');
  h.$('[data-simulate="stop"]').focus(); h.click('[data-simulate="stop"]');
  assert.equal(h.state(), 'stopped'); assert.equal(h.$('#main-content').inert, false);
  assert.equal(h.$('#inspector').classList.contains('is-overlay'), false);
  assert.equal(h.d.activeElement, h.$('#message-input'));
}, { width: 768 });

test('P29', 'Explicit inspector simulation starts focus the composer before their trigger disables', h => {
  for (const action of ['send', 'error']) {
    h.click('#new-session'); h.$(`[data-simulate="${action}"]`).focus(); h.click(`[data-simulate="${action}"]`);
    assert.equal(h.state(), 'generating'); assert.equal(h.d.activeElement, h.$('#message-input'));
    assert.equal(h.$(`[data-simulate="${action}"]`).disabled, true);
  }
});
test('P30', 'Explicit narrow inspector starts close overlay and release background focus', h => {
  for (const action of ['send', 'error']) {
    h.click('#new-session'); h.click('#inspector-toggle'); h.click('[data-tab="states"]'); h.click(`[data-simulate="${action}"]`);
    assert.equal(h.state(), 'generating'); assert.equal(h.$('#main-content').inert, false);
    assert.equal(h.$('#inspector').classList.contains('is-overlay'), false);
    assert.equal(h.d.activeElement, h.$('#message-input'));
  }
}, { width: 768 });

test('P31', 'Explicit retry restores composer focus after its error banner disappears', h => {
  h.input('重试消息'); h.$('#fail-next').checked = true; h.submit(); h.tick(800);
  assert.equal(h.state(), 'error'); h.$('#retry-button').focus(); h.click('#retry-button');
  assert.equal(h.state(), 'generating'); assert.equal(h.$('#error-banner').hidden, true);
  assert.equal(h.d.activeElement, h.$('#message-input')); assert.equal(h.$$('.message--user').length, 2);
});
test('P32', 'Passive failure preserves focus on a different active input', h => {
  h.input('异步错误'); h.$('#fail-next').checked = true; h.submit(); open(h); quickInput(h, '继续速记'); h.tick(800);
  assert.equal(h.state(), 'error'); assert.equal(h.d.activeElement, h.$('#quick-entry-input'));
  assert.equal(h.$('#quick-entry-input').value, '继续速记');
});

const after = hashes();
const unchanged = JSON.stringify(before) === JSON.stringify(after);
if (!unchanged) results.push({ id: 'P-SNAPSHOT', title: 'Sources stable during run', status: 'fail' });
const summary = { pass: results.filter(r => r.status === 'pass').length, fail: results.filter(r => r.status === 'fail').length, total: results.length };
const report = { schema_version: '1.0', tested_at: new Date().toISOString(), environment: { node: process.version, jsdom: baselineRequire('jsdom/package.json').version, browser: null }, scope: 'Phase-2 original density, independent message reading and in-page Quick Entry. Deterministic simulated DOM only; no product/runtime/browser claim.', files_sha256: after, sources_unchanged_during_run: unchanged, limitations: ['Reuses all baseline harness fixtures and limitations.', 'No CSS variable cascade/layout measurements, rendered size or reflow checks.', 'Synthetic input/composition/scroll heights do not validate real IME or native editing.', 'No native Quick Entry window, system shortcuts, account, backend or persistence.'], summary, results };
const output = path.join(ROOT, '04-Extracted-Core-Code-And-Scripts/tests/results/phase2-components-test.json');
fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ summary, failures: results.filter(r => r.status === 'fail'), report: path.relative(ROOT, output) }, null, 2));
process.exitCode = summary.fail ? 1 : 0;
