'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const baselineRequire = require('node:module').createRequire(require.resolve('../demo-state/harness.cjs'));
const { JSDOM } = baselineRequire('jsdom');
const ROOT = path.resolve(__dirname, '../../..');
const read = file => fs.readFileSync(path.join(ROOT, file), 'utf8');
const html = read('01-Frontend-Design-And-HTML-Templates/interactive-study/index.html'), js = read('01-Frontend-Design-And-HTML-Templates/interactive-study/demo.js');
const cssFiles = ['01-Frontend-Design-And-HTML-Templates/styles/tokens.css', '01-Frontend-Design-And-HTML-Templates/styles/components.css', '01-Frontend-Design-And-HTML-Templates/interactive-study/demo.css'];
const dom = new JSDOM(html), d = dom.window.document;
const rules = [];
for (const file of cssFiles) {
  const style = d.createElement('style'); style.textContent = read(file); d.head.append(style);
  for (const rule of style.sheet.cssRules) if (rule.selectorText) rules.push(rule);
}
const rule = selector => rules.filter(r => r.selectorText === selector).at(-1)?.style;
const prop = (selector, name) => rules.filter(r => r.selectorText === selector).map(r => r.style.getPropertyValue(name).trim()).filter(Boolean).at(-1) || '';
const results = [];
function check(id, title, fn) {
  try { fn(); results.push({ id, title, status: 'pass', method: 'static source/DOM/CSSOM declarations' }); }
  catch (error) { results.push({ id, title, status: 'fail', actual: error.message }); }
}
check('PS01', 'New control IDs are unique and all ARIA/label references resolve', () => {
  const ids = [...d.querySelectorAll('[id]')].map(el => el.id); assert.equal(ids.length, new Set(ids).size);
  for (const el of d.querySelectorAll('#display-lab [aria-describedby], #display-lab [for], #quick-entry-example [aria-describedby], #quick-entry-example [aria-controls], #quick-entry-example [for]')) {
    for (const attr of ['aria-describedby', 'aria-controls', 'for']) for (const id of (el.getAttribute(attr) || '').split(/\s+/).filter(Boolean)) assert.ok(d.getElementById(id), id);
  }
});
check('PS02', 'Original density declarations and visible metrics agree on two distinct geometries', () => {
  for (const [selector, expected, label] of [
    ['.study-density-example', [40, 16, 12, 8, 8], '原创紧凑'],
    ['.study-density-example[data-density="comfortable"]', [48, 20, 20, 12, 12], '原创舒适']
  ]) {
    const properties = ['--study-control-height', '--study-density-icon', '--study-density-padding', '--study-density-gap', '--study-radius-control'];
    properties.forEach((property, i) => assert.equal(prop(selector, property), expected[i] + 'px'));
    const line = js.split('\n').find(line => line.includes(label + '：'));
    assert.ok(line); for (const value of expected) assert.ok(line.includes(value + ' px'));
  }
});
check('PS03', 'Reading declarations change only a message-size variable and density does not set it', () => {
  for (const [size, value] of [['sm', 14], ['md', 16], ['lg', 18]]) {
    const style = rule(`[data-message-size="${size}"]`);
    assert.equal(style.length, 1); assert.equal(style[0], '--study-message-size');
    assert.equal(style.getPropertyValue('--study-message-size'), value + 'px');
  }
  for (const selector of ['.study-density-example', '.study-density-example[data-density="comfortable"]']) assert.equal(prop(selector, '--study-message-size'), '');
  assert.equal(d.querySelectorAll('[data-density]').length, 1);
  assert.equal(d.querySelector('[data-density]').id, 'density-example');
});
check('PS04', 'Messages consume the reading axis while tools have explicit UI typography', () => {
  assert.match(prop('.message-content', 'font'), /var\(--study-message-size\)/);
  assert.equal(prop('.message--user', 'font-size'), 'var(--study-message-size)');
  assert.equal(prop('.message-content .streaming-text', 'font-size'), 'var(--study-message-size)');
  assert.equal(prop('.study-button', 'font-size'), 'var(--study-size-label)');
  assert.match(prop('.message-content .artifact-card', 'font'), /var\(--study-font-ui\)/);
  assert.equal(prop('.message-actions .study-button', 'font-size'), '11px');
});
check('PS05', 'Density consumers declare grouped control, icon, spacing and radius variables', () => {
  assert.equal(prop('.study-density-example .study-icon', 'width'), 'var(--study-density-icon)');
  assert.equal(prop('.study-density-example .study-field', 'min-height'), 'var(--study-control-height)');
  assert.equal(prop('.study-density-example .study-button', 'gap'), 'var(--study-density-gap)');
  assert.equal(prop('.study-density-example', 'padding'), 'var(--study-density-padding)');
  assert.equal(prop('.study-density-example', 'border-radius'), 'var(--study-radius-control)');
});
check('PS06', 'Quick Entry has a distinct horizontal form and documented original geometry', () => {
  const form = d.querySelector('#quick-entry-form');
  assert.equal(form.closest('#composer'), null); assert.equal(form.querySelector('.composer-toolbar'), null);
  assert.ok(form.querySelector('select')); assert.ok(form.querySelector('textarea')); assert.ok(form.querySelector('button[type="submit"]'));
  assert.equal(prop('.study-quick-entry', 'display'), 'flex');
  assert.equal(prop('.study-quick-entry', 'min-height'), '48px');
  assert.equal(prop('.study-quick-entry', 'border-radius'), '12px');
  assert.match(prop('.study-quick-entry textarea', 'font'), /16px\/1.5/);
});
check('PS07', 'New form controls have real labels, explicit submit types and a length ceiling', () => {
  for (const el of d.querySelectorAll('#quick-entry-example input, #quick-entry-example textarea, #quick-entry-example select, #display-lab input')) assert.ok(d.querySelector(`label[for="${el.id}"]`));
  assert.equal(d.querySelector('#quick-entry-input').maxLength, 300);
  assert.equal(d.querySelector('#quick-entry-status').getAttribute('role'), 'status');
  assert.equal(d.querySelector('#quick-entry-form').hasAttribute('action'), false);
  assert.match(js, /quickInput\.value\.length > 300/);
  assert.match(js, /\$\('#quick-entry-result-text'\)\.textContent = text/);
});
check('PS08', 'Reading/density controls have labelled groups and forced-color selection treatment', () => {
  for (const group of d.querySelectorAll('#display-lab [role="group"]')) {
    assert.ok(group.getAttribute('aria-label')); assert.equal(group.querySelectorAll('[aria-pressed="true"]').length, 1);
    for (const button of group.querySelectorAll('button')) assert.equal(button.type, 'button');
  }
  assert.match(read('01-Frontend-Design-And-HTML-Templates/styles/components.css'), /@media \(forced-colors: active\).*\.study-choice-field button\[aria-pressed="true"\]/);
});
check('PS09', 'New examples introduce no remote assets, network APIs, imports or stored input', () => {
  for (const el of d.querySelectorAll('script[src],link[href]')) {
    const resource = el.getAttribute('src') || el.getAttribute('href');
    assert.ok(!/^(https?:|\/\/|data:)/.test(resource)); assert.ok(fs.existsSync(path.resolve(ROOT, '01-Frontend-Design-And-HTML-Templates/interactive-study', resource)));
  }
  for (const file of cssFiles) assert.ok(!/@import\b|url\s*\(/.test(read(file)));
  assert.ok(!/\bfetch\s*\(|new\s+(?:XMLHttpRequest|WebSocket|EventSource)|\bsendBeacon\s*\(/.test(js));
  assert.equal((js.match(/localStorage\.setItem\(/g) || []).length, 1);
  assert.match(js, /localStorage\.setItem\('liubai-study-theme', theme\)/);
});
check('PS10', 'Documentation distinguishes original specimen values and unverified browser behavior', () => {
  const readme = read('01-Frontend-Design-And-HTML-Templates/interactive-study/README.md');
  assert.match(readme, /40.*48/); assert.match(readme, /14.*16.*18/);
  assert.match(readme, /24.*32/); assert.match(readme, /真实浏览器/);
  assert.match(readme, /Quick Entry/);
  assert.ok(!html.includes('网络请求为零')); assert.ok(!html.includes('无网络请求'));
});
const files = ['01-Frontend-Design-And-HTML-Templates/interactive-study/index.html', '01-Frontend-Design-And-HTML-Templates/interactive-study/demo.js', ...cssFiles];
const summary = { pass: results.filter(r => r.status === 'pass').length, fail: results.filter(r => r.status === 'fail').length, total: results.length };
const report = { schema_version: '1.0', tested_at: new Date().toISOString(), method: 'Static source/DOM/CSSOM declarations, not computed browser style.', files_sha256: Object.fromEntries(files.map(file => [file, crypto.createHash('sha256').update(read(file)).digest('hex')])), limitations: ['CSSOM parsing records declarations, not their computed cascade, layout or actual contrast.', 'No screenshot, accessibility tree, real keyboard/IME, actual pointer target or offline-browser test.'], summary, results };
const output = path.join(ROOT, '04-Extracted-Core-Code-And-Scripts/tests/results/phase2-components-static.json');
fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
dom.window.close(); console.log(JSON.stringify({ summary, failures: results.filter(r => r.status === 'fail'), report: path.relative(ROOT, output) }, null, 2)); process.exitCode = summary.fail ? 1 : 0;
