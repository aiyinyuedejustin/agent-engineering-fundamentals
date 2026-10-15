'use strict';
// Structural regression only: jsdom has no layout or native scrolling implementation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createHarness, ROOT } = require('../demo-state/harness.cjs');
const files = [
  '01-Frontend-Design-And-HTML-Templates/interactive-study/index.html',
  '01-Frontend-Design-And-HTML-Templates/interactive-study/demo.css',
  '01-Frontend-Design-And-HTML-Templates/interactive-study/demo.js',
  '01-Frontend-Design-And-HTML-Templates/interactive-study/evidence.js',
  '01-Frontend-Design-And-HTML-Templates/styles/components.css',
  '01-Frontend-Design-And-HTML-Templates/styles/tokens.css'
];
const hashes = () => Object.fromEntries(files.map(file => [file,
  crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, file))).digest('hex')]));
const before = hashes(), results = [];
function check(id, title, fn, options = {}) {
  const h = createHarness(options);
  try {
    fn(h);
    assert.deepEqual(h.errors, [], 'Unexpected DOM/runtime error');
    assert.deepEqual(h.transmissions, [], 'Unexpected network API attempt');
    results.push({ id, title, status: 'pass', method: 'simulated DOM / CSSOM declarations' });
  } catch (error) {
    results.push({ id, title, status: 'fail', actual: error.message });
  } finally { h.close(); }
}
function rules(h) { return [...h.d.styleSheets].flatMap(sheet => [...sheet.cssRules]); }
function declaration(h, selector, property, list = rules(h)) {
  return list.filter(rule => rule.selectorText === selector)
    .map(rule => rule.style.getPropertyValue(property).trim()).filter(Boolean).at(-1) || '';
}
// This uses declared CSS positions; it deliberately makes no offsetParent/layout claim.
function positionedAncestor(h, el) {
  for (let parent = el.parentElement; parent; parent = parent.parentElement) {
    const position = h.w.getComputedStyle(parent).position;
    if (position && position !== 'static') return parent;
  }
  return null;
}
check('WS01', 'The preference live region has a positioning boundary inside its scrolling view', h => {
  h.click('[data-view="gallery"]');
  const status = h.$('#display-preference-status'), view = h.$('#view-gallery');
  assert.ok(view.contains(status));
  assert.equal(declaration(h, '.study-sr-only', 'position'), 'absolute');
  assert.equal(declaration(h, '.document-view', 'position'), 'relative');
  assert.equal(positionedAncestor(h, status), view,
    'An absolute live region must not escape the document-view scroll boundary');
});
check('WS02', 'Existing panel scroll declarations and viewport flex sizing remain available', h => {
  assert.equal(declaration(h, '.document-view', 'overflow'), 'auto');
  assert.equal(declaration(h, '.conversation-scroll', 'overflow'), 'auto');
  assert.equal(declaration(h, '.sidebar', 'overflow-y'), 'auto');
  assert.equal(declaration(h, '.inspector', 'overflow'), 'auto');
  assert.equal(declaration(h, '.app-shell', 'height'), '100dvh');
  assert.equal(declaration(h, '.app-shell', 'min-height'), '0');
  assert.equal(declaration(h, '.workspace', 'min-height'), '0');
  assert.equal(declaration(h, 'html, body', 'overflow'), '');
});
check('WS03', 'Short or heavily zoomed viewports retain the document-scroll fallback', h => {
  const short = rules(h).find(rule => rule.conditionText === '(max-height: 560px)');
  assert.ok(short, 'The short-viewport media branch must remain');
  const list = [...short.cssRules];
  assert.equal(declaration(h, 'body:not(.drawer-open)', 'overflow', list), 'auto');
  assert.equal(declaration(h, '.app-shell', 'height', list), 'auto');
  assert.equal(declaration(h, '.app-shell', 'min-height', list), '100dvh');
  assert.equal(declaration(h, '.view', 'height', list), 'auto');
  assert.equal(declaration(h, '.document-view', 'overflow', list), 'visible');
});
check('WS04', 'Screen-reader status remains present and updates through every preference combination', h => {
  h.click('[data-view="gallery"]');
  const status = h.$('#display-preference-status');
  assert.equal(status.getAttribute('role'), 'status');
  assert.equal(status.closest('[hidden], [aria-hidden="true"], [inert]'), null);
  assert.notEqual(h.w.getComputedStyle(status).display, 'none');
  assert.notEqual(h.w.getComputedStyle(status).visibility, 'hidden');
  for (const density of ['compact', 'comfortable']) for (const [reading, pixels] of [['sm', 14], ['md', 16], ['lg', 18]]) {
    h.click(`[data-density-choice="${density}"]`);
    assert.match(status.textContent, /消息阅读大小保持不变/);
    h.click(`[data-reading-choice="${reading}"]`);
    assert.match(status.textContent, new RegExp(`消息正文已改为 ${pixels} px`));
    assert.equal(positionedAncestor(h, status), h.$('#view-gallery'));
  }
});
check('WS05', 'Gallery keyboard events are not suppressed and Quick Entry draft/focus behavior is retained', h => {
  h.input('完整输入草稿');
  h.click('[data-view="gallery"]');
  h.click('[data-density-choice="comfortable"]'); h.click('[data-reading-choice="lg"]');
  h.$('#density-title').focus();
  for (const key of ['Tab', 'PageDown', 'PageUp']) assert.equal(h.key(h.$('#density-title'), key).defaultPrevented, false);
  h.click('#quick-entry-open');
  assert.equal(h.d.activeElement, h.$('#quick-entry-input'));
  h.$('#quick-entry-input').value = '速记草稿';
  h.$('#quick-entry-input').dispatchEvent(new h.w.Event('input', { bubbles: true }));
  h.key(h.$('#quick-entry-input'), 'Escape');
  assert.equal(h.$('#quick-entry-panel').hidden, true);
  assert.equal(h.d.activeElement, h.$('#quick-entry-open'));
  h.click('#quick-entry-open');
  assert.equal(h.$('#quick-entry-input').value, '速记草稿');
  assert.equal(h.$('#message-input').value, '完整输入草稿');
}, { width: 1188 });
check('WS06', 'The positioning boundary also survives the existing narrow-width DOM fixture', h => {
  h.click('#sidebar-toggle'); h.click('[data-view="gallery"]');
  assert.equal(h.$('#view-gallery').hidden, false);
  assert.equal(h.$('#main-content').inert, false);
  assert.equal(positionedAncestor(h, h.$('#display-preference-status')), h.$('#view-gallery'));
  h.click('#quick-entry-open');
  assert.equal(h.d.activeElement, h.$('#quick-entry-input'));
}, { width: 320 });
const after = hashes(), unchanged = JSON.stringify(before) === JSON.stringify(after);
const summary = { pass: results.filter(r => r.status === 'pass').length, fail: results.filter(r => r.status === 'fail').length, total: results.length };
const report = {
  schema_version: '1.0', tested_at: new Date().toISOString(),
  method: 'Static CSSOM declarations and simulated DOM; not real-browser layout.',
  source_unchanged: unchanged, files_sha256: before, summary, results,
  limitations: [
    'No scrollHeight, viewport geometry, screenshot, native Tab/default scrolling or mobile-browser measurement.',
    'A 320px fixture changes matchMedia state only; it does not render a narrow viewport.',
    'Live-region text/semantics are checked; actual screen-reader announcements are not tested.'
  ]
};
const output = path.join(ROOT, '04-Extracted-Core-Code-And-Scripts/tests/results/workspace-scroll.json');
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ summary, source_unchanged: unchanged, failures: results.filter(r => r.status === 'fail'), report: path.relative(ROOT, output) }, null, 2));
process.exitCode = summary.fail || !unchanged ? 1 : 0;
