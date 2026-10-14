'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { JSDOM, VirtualConsole } = require('jsdom');
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const OUTPUT = path.resolve(process.argv[3] || path.join(__dirname, 'edge-results.json'));
const results = [];
const names = fs.readdirSync(ROOT).filter(name => /^0[1-6].*\.html$/.test(name)).sort();
function harness(file, options = {}) {
  const errors = [], network = [], writes = [];
  const store = new Map(Object.entries(options.stored || {}));
  const vc = new VirtualConsole(); vc.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(fs.readFileSync(path.join(ROOT, file), 'utf8'), {
    url: 'https://offline.invalid/' + file, runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vc,
  });
  const w = dom.window, d = w.document;
  let now = 0, next = 1, denyWrites = Boolean(options.writeDenied);
  const timers = new Map(), media = new Map();
  w.setTimeout = (fn, delay = 0) => { const id = next++; timers.set(id, { fn, at: now + Number(delay) }); return id; };
  w.clearTimeout = id => timers.delete(id);
  function tick(ms) {
    const end = now + ms; let count = 0;
    for (;;) {
      const task = [...timers].filter(([, item]) => item.at <= end).sort((a, b) => a[1].at - b[1].at)[0];
      if (!task) break;
      if (++count > 1000) throw Error('timer runaway');
      now = task[1].at; timers.delete(task[0]); task[1].fn();
    }
    now = end;
  }
  w.matchMedia = query => {
    if (!media.has(query)) {
      const listeners = new Set();
      media.set(query, { matches: query.includes('max-width') && Boolean(options.mobile), media: query,
        addEventListener: (kind, fn) => { if (kind === 'change') listeners.add(fn); },
        removeEventListener: (kind, fn) => listeners.delete(fn),
        change(value) { if (this.matches === value) return; this.matches = value; for (const fn of listeners) fn({ matches: value, media: query }); },
      });
    }
    return media.get(query);
  };
  w.HTMLDialogElement.prototype.showModal = function () { this.open = true; this.querySelector('input,button,select,textarea')?.focus(); };
  w.HTMLDialogElement.prototype.close = function () { this.open = false; this.dispatchEvent(new w.Event('close')); };
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.HTMLElement.prototype.setPointerCapture = function () {};
  w.scrollTo = () => {};
  d.execCommand = () => false;
  Object.defineProperty(w, 'localStorage', { get() { return {
    getItem: key => store.get(key) ?? null,
    setItem(key, value) { if (denyWrites) throw new w.DOMException('Quota', 'QuotaExceededError'); store.set(key, value); writes.push({ key, value }); },
  }; } });
  for (const api of ['fetch', 'WebSocket', 'EventSource']) w[api] = function (...args) { network.push({ api, args }); throw Error('network forbidden'); };
  w.XMLHttpRequest = class { open(...args) { network.push({ api: 'xhr', args }); } };
  w.navigator.sendBeacon = (...args) => network.push({ api: 'beacon', args });
  for (const script of d.querySelectorAll('script')) w.eval(script.textContent);
  const $ = selector => d.querySelector(selector), $$ = selector => [...d.querySelectorAll(selector)];
  const input = (selector, value) => { $(selector).value = value; $(selector).dispatchEvent(new w.Event('input', { bubbles: true })); };
  const change = (selector, value) => { if (typeof value === 'boolean') $(selector).checked = value; else $(selector).value = value; $(selector).dispatchEvent(new w.Event('change', { bubbles: true })); };
  const key = (selector, value, extra = {}) => { const event = new w.KeyboardEvent('keydown', { key: value, bubbles: true, cancelable: true, ...extra }); (typeof selector === 'string' ? $(selector) : selector).dispatchEvent(event); return event; };
  const compose = (selector, type) => $(selector).dispatchEvent(new w.CompositionEvent(type, { bubbles: true }));
  const submit = selector => $(selector).dispatchEvent(new w.Event('submit', { bubbles: true, cancelable: true }));
  const cancel = selector => { const event = new w.Event('cancel', { cancelable: true }); const dialog = $(selector); if (dialog.dispatchEvent(event)) dialog.close(); return event; };
  return { w, d, $, $$, store, errors, network, writes, input, change, key, compose, submit, cancel, tick,
    click: selector => $(selector).click(), resize: mobile => w.matchMedia('(max-width:760px)').change(mobile),
    denyWrites: value => { denyWrites = value; }, close: () => w.close(),
  };
}
function test(index, id, title, fn, options = {}) {
  let h;
  try { h = harness(names[index], options); fn(h); assert.deepEqual(h.errors, []); assert.deepEqual(h.network, []); results.push({ id, file: names[index], title, result: 'pass' }); }
  catch (error) { results.push({ id, file: names[index], title, result: 'fail', error: error.message }); }
  finally { h?.close(); }
}
// Regressions: assert intended state so the unmodified input demonstrates each defect.
test(1, 'EDGE-01a', 'Desktop-to-mobile resize returns focus before the sidebar becomes inert', h => {
  h.$('#new-chat').focus(); h.resize(true);
  assert.equal(h.$('#sidebar').inert, true);
  assert.equal(h.$('.chat-main').inert, false);
  assert.equal(h.d.activeElement.id, 'sidebar-toggle');
});
test(1, 'EDGE-01b', 'Mobile-to-desktop resize moves focus off the now-hidden mobile close control', h => {
  h.click('#sidebar-toggle'); assert.equal(h.d.activeElement.id, 'sidebar-close'); h.resize(false);
  assert.equal(h.$('#sidebar').inert, false);
  assert.notEqual(h.d.activeElement.id, 'sidebar-close');
  assert.equal(h.d.activeElement.id, 'sidebar-toggle');
}, { mobile: true });
test(1, 'EDGE-01c', 'Mobile drawer restores collapsed desktop preference without trapping focus', h => {
  h.click('#sidebar-toggle'); h.resize(true); h.click('#sidebar-toggle'); h.$('#new-chat').focus(); h.resize(false);
  assert.equal(h.$('#sidebar').inert, true);
  assert.equal(h.$('.chat-main').inert, false);
  assert.equal(h.d.activeElement.id, 'sidebar-toggle');
});
test(4, 'EDGE-02a', 'Failed save remains unsaved after changing a control and restoring its value', h => {
  h.input('#display-name', 'Session only'); h.submit('#settings-form');
  assert.match(h.$('#save-status').textContent, /未能持久保存/);
  h.change('#control-density', 'compact'); h.change('#control-density', 'comfortable');
  assert.doesNotMatch(h.$('#save-status').textContent, /^所有更改已保存$/);
  assert.equal(h.store.has('atelier-settings'), false);
}, { writeDenied: true });
test(4, 'EDGE-02b', 'Failed reset remains unsaved after changing a control and restoring its value', h => {
  h.input('#display-name', 'Previously saved'); h.submit('#settings-form'); h.denyWrites(true);
  h.click('#reset-settings'); h.click('#confirm-reset');
  assert.match(h.$('#save-status').textContent, /未能持久保存/);
  h.change('#control-density', 'compact'); h.change('#control-density', 'comfortable');
  assert.doesNotMatch(h.$('#save-status').textContent, /^所有更改已保存$/);
  assert.equal(JSON.parse(h.store.get('atelier-settings')).name, 'Previously saved');
});
test(4, 'EDGE-03', 'Reset clears prior display-name validation error', h => {
  h.input('#display-name', ' '); h.submit('#settings-form');
  assert.equal(h.$('#display-name').getAttribute('aria-invalid'), 'true');
  h.click('#reset-settings'); h.click('#confirm-reset');
  assert.equal(h.$('#display-name').value, '留白的朋友');
  assert.notEqual(h.$('#display-name').getAttribute('aria-invalid'), 'true');
  assert.doesNotMatch(h.$('#profile-help').textContent, /^请填写/);
});
test(2, 'EDGE-04a', 'Title instruction targets real H1 rather than an HTML comment', h => {
  h.input('#code-editor', '<!-- <h1>Comment example</h1> --><h1>Actual title</h1>');
  h.input('#ide-input', '标题改为 New title'); h.submit('#ide-form');
  const preview = new JSDOM(h.$('#preview-frame').srcdoc);
  assert.equal(preview.window.document.querySelector('h1').textContent, 'New title'); preview.window.close();
});
test(2, 'EDGE-04b', 'Title instruction targets real H1 rather than a STYLE raw-text comment', h => {
  h.input('#code-editor', '<style>/* <h1>CSS example</h1> */</style><h1>Actual title</h1>');
  h.input('#ide-input', '标题改为 New title'); h.submit('#ide-form');
  const preview = new JSDOM(h.$('#preview-frame').srcdoc);
  assert.equal(preview.window.document.querySelector('h1').textContent, 'New title'); preview.window.close();
});
test(2, 'EDGE-04c', 'An H1 found only in a comment reports a missing title', h => {
  h.input('#code-editor', '<!-- <h1>Example only</h1> --><p>Visible paragraph</p>');
  h.input('#ide-input', '标题改为 New title'); h.submit('#ide-form');
  assert.match(h.$('#ide-messages').lastElementChild.textContent, /没有找到 H1/);
});
test(2, 'EDGE-05', 'Title-only edit preserves H1 class, id, and style while keeping replacement literal', h => {
  h.input('#code-editor', '<h1 class="hero" id="heading" style="color:red">Old</h1>');
  h.input('#ide-input', '标题改为 $& <img src=x> & done'); h.submit('#ide-form');
  const preview = new JSDOM(h.$('#preview-frame').srcdoc), heading = preview.window.document.querySelector('h1');
  assert.equal(heading.className, 'hero'); assert.equal(heading.id, 'heading'); assert.equal(heading.style.color, 'red');
  assert.equal(heading.textContent, '$& <img src=x> & done'); assert.equal(heading.querySelector('img'), null); preview.window.close();
});
test(2, 'EDGE-06', 'Static text-only HTML previews instead of being rejected as empty', h => {
  h.input('#code-editor', 'Plain text &amp; escaped &lt;script&gt; is static HTML'); h.click('#run-code');
  assert.equal(h.$('#preview-error').hidden, true);
  const preview = new JSDOM(h.$('#preview-frame').srcdoc);
  assert.equal(preview.window.document.body.textContent, 'Plain text & escaped <script> is static HTML'); preview.window.close();
});
// Controls: interrupted and repeated flows which must continue to work.
test(1, 'CONTROL-01', 'Stop at 899ms cancels completion and preserves newer draft', h => {
  h.input('#chat-input', 'First'); h.submit('#chat-form'); h.tick(899); h.input('#chat-input', 'Next'); h.click('#send-chat'); h.tick(5000);
  assert.equal(h.$('#chat-input').value, 'Next'); assert.equal(h.$$('.message.assistant').length, 1); assert.equal(h.$('#pending-response'), null);
  assert.equal(JSON.parse(h.store.get('atelier-chat-draft')), 'Next');
});
test(1, 'CONTROL-02', 'Completion at 900ms preserves newer draft and later send intentionally submits it', h => {
  h.input('#chat-input', 'First'); h.submit('#chat-form'); h.input('#chat-input', 'Next'); h.tick(900);
  assert.equal(h.$('#chat-input').value, 'Next'); assert.equal(h.$('#send-chat').getAttribute('aria-label'), '发送消息');
  h.click('#send-chat'); assert.equal(h.$$('.message.user').at(-1).textContent, 'Next'); h.tick(900);
  assert.equal(h.$$('.message.assistant').length, 3);
});
test(1, 'CONTROL-03', 'Stop, resubmit, new conversation and another submission do not leak old completions', h => {
  h.input('#chat-input', 'First'); h.submit('#chat-form'); h.click('#send-chat'); h.submit('#chat-form'); h.tick(300);
  h.click('#new-chat'); h.input('#chat-input', 'Newest'); h.submit('#chat-form'); h.tick(2000);
  assert.equal(h.$$('.message.user').length, 2); assert.equal(h.$$('.message.assistant').length, 2);
  assert.equal(h.$$('.message.user').at(-1).textContent, 'Newest');
});
test(1, 'CONTROL-04', 'Repeated viewport switches restore inert/ARIA state and desktop preference', h => {
  for (let n = 0; n < 4; n++) { h.resize(true); assert.equal(h.$('#sidebar').inert, true); h.click('#sidebar-toggle'); assert.equal(h.$('.chat-main').inert, true); h.resize(false); assert.equal(h.$('#sidebar').inert, false); assert.equal(h.$('.chat-main').inert, false); assert.equal(h.$('#sidebar').hasAttribute('aria-modal'), false); }
});
test(0, 'CONTROL-05', 'Gallery dialog native-cancel simulation returns opener through repeated cycles', h => {
  for (let n = 0; n < 3; n++) { h.$('#open-dialog').focus(); h.click('#open-dialog'); h.cancel('#publish-dialog'); assert.equal(h.$('#publish-dialog').open, false); assert.equal(h.d.activeElement.id, 'open-dialog'); }
});
test(1, 'CONTROL-06', 'Chat dialog close does not discard a draft and returns focus to reading card', h => {
  h.input('#chat-input', 'Keep draft'); h.$('#reading-card').focus(); h.click('#reading-card'); h.click('#note-dialog [data-close-dialog]');
  assert.equal(h.$('#chat-input').value, 'Keep draft'); assert.equal(h.d.activeElement.id, 'reading-card');
});
test(4, 'CONTROL-07', 'Cancelled settings reset preserves unsaved values and original stored settings', h => {
  h.input('#display-name', 'Persisted'); h.submit('#settings-form'); h.input('#display-name', 'Unsaved');
  h.$('#reset-settings').focus(); h.click('#reset-settings'); h.cancel('#reset-dialog');
  assert.equal(h.$('#display-name').value, 'Unsaved'); assert.equal(JSON.parse(h.store.get('atelier-settings')).name, 'Persisted'); assert.equal(h.d.activeElement.id, 'reset-settings');
});
test(4, 'CONTROL-08', 'Successful retry after failed settings save really persists latest values', h => {
  h.input('#display-name', 'Retry'); h.submit('#settings-form'); h.denyWrites(false); h.submit('#settings-form');
  assert.equal(JSON.parse(h.store.get('atelier-settings')).name, 'Retry'); h.change('#control-density', 'compact'); h.change('#control-density', 'comfortable');
  assert.match(h.$('#save-status').textContent, /所有更改已保存/);
}, { writeDenied: true });
test(2, 'CONTROL-09', 'Preview removes navigable/active constructs, preserves CSP and last success on error', h => {
  h.input('#code-editor', '<base href="https://example.invalid/"><form><input autofocus><button>Submit</button></form><svg onload="bad()"></svg><h1 onclick="bad()">Safe</h1><a href="javascript:bad()">Link</a><img src=x><iframe srcdoc="bad"></iframe>'); h.click('#run-code');
  const source = h.$('#preview-frame').srcdoc; assert.match(source, /<h1>Safe<\/h1>/); assert.doesNotMatch(source, /<base|<form|<svg|onclick|javascript:|<img|<iframe/);
  assert.match(source, /script-src 'none'/); assert.match(source, /connect-src 'none'/); assert.equal(h.$('#preview-frame').getAttribute('sandbox'), '');
  h.input('#code-editor', '<script>bad()</script>'); h.click('#run-code'); assert.equal(h.$('#preview-frame').srcdoc, source); assert.equal(h.$('#preview-error').hidden, false);
});
test(2, 'CONTROL-10', 'Title update changes only first real H1 and does not execute markup', h => {
  h.input('#code-editor', '<h1>First</h1><h1>Second</h1>'); h.input('#ide-input', '标题改为 <script>bad()</script>'); h.submit('#ide-form');
  const preview = new JSDOM(h.$('#preview-frame').srcdoc); assert.equal(preview.window.document.querySelectorAll('h1')[1].textContent, 'Second'); assert.equal(preview.window.document.querySelector('script'), null); preview.window.close();
});
test(5, 'CONTROL-11', 'Composition protects selected command, capture, shortcut and native cancel', h => {
  h.input('#launcher-input', '主题'); h.key('#launcher-input', 'ArrowDown'); const theme = h.d.documentElement.dataset.theme;
  h.compose('#launcher-input', 'compositionstart'); h.key('#launcher-input', 'Enter'); h.submit('#launcher-form'); h.key('#launcher-input', 'k', { ctrlKey: true });
  const cancel = h.cancel('#launcher-dialog'); assert.equal(cancel.defaultPrevented, true); assert.equal(h.$('#launcher-dialog').open, true); assert.equal(h.d.documentElement.dataset.theme, theme); assert.equal(h.$$('.capture-entry').length, 0);
  h.compose('#launcher-input', 'compositionend'); h.key('#launcher-input', 'ArrowDown'); h.key('#launcher-input', 'Enter'); assert.notEqual(h.d.documentElement.dataset.theme, theme);
});
test(5, 'CONTROL-12', 'Escape preserves draft and context over repeated reopen cycles', h => {
  h.input('#launcher-input', 'Keep local draft'); h.change('#capture-context', 'ideas');
  for (let n = 0; n < 3; n++) { h.cancel('#launcher-dialog'); assert.equal(h.d.activeElement.id, 'open-launcher'); h.click('#open-launcher'); assert.equal(h.$('#launcher-input').value, 'Keep local draft'); assert.equal(h.$('#capture-context').value, 'ideas'); assert.equal(h.d.activeElement.id, 'launcher-input'); }
});
test(5, 'CONTROL-13', 'Selected command resets safely when query narrows and capture remains literal', h => {
  h.key('#launcher-input', 'End'); h.input('#launcher-input', 'Unmatched <b>literal</b>'); assert.equal(h.$('#launcher-input').getAttribute('aria-activedescendant'), 'command-0'); h.key('#launcher-input', 'Enter');
  assert.equal(h.$$('.capture-entry').length, 1); assert.equal(h.$('#captures b'), null);
});
test(3, 'CONTROL-14', 'Editorial Escape then mode switch keeps search and focus targets coherent', h => {
  h.input('#doc-search', '字体'); h.key('#doc-search', 'Escape'); assert.equal(h.$('#search-results').hidden, true); h.click('#docs-tab'); h.input('#doc-search', '主题'); h.key('#doc-search', 'Escape'); assert.equal(h.$('#search-results').hidden, true);
});
const report = { generatedAt: new Date().toISOString(), root: ROOT, method: 'jsdom with deterministic timers, media-query changes, storage exceptions and native-dialog-method stubs. No browser/layout/CSP-enforcement claim.',
  runner: { node: process.version, jsdom: require('jsdom/package.json').version },
  sha256: Object.fromEntries(names.map(file => [file, crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, file))).digest('hex')])),
  summary: { total: results.length, passed: results.filter(r => r.result === 'pass').length, failed: results.filter(r => r.result === 'fail').length }, results };
fs.writeFileSync(OUTPUT, JSON.stringify(report, null, 2) + '\n'); console.log(JSON.stringify(report.summary)); for (const result of results.filter(r => r.result === 'fail')) console.log(result.id + ' ' + result.title + '\n' + result.error);
process.exitCode = report.summary.failed ? 1 : 0;
