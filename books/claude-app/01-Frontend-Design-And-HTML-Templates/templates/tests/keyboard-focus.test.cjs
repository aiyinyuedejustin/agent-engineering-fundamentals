'use strict';
// Independent intended-behavior regressions. No native dialog, Tab, or layout claim.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const test = require('node:test');
const { JSDOM, VirtualConsole } = require('jsdom');
const ROOT = path.resolve(process.env.TEMPLATE_A11Y_ROOT || path.join(__dirname, '..'));
const names = { 2: '02-chat-workspace-template.html', 3: '03-split-artifact-ide-template.html',
  6: '06-floating-launcher-template.html' };
function fixture(number, t, options = {}) {
  const errors = [], vc = new VirtualConsole(); vc.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(fs.readFileSync(path.join(ROOT, names[number]), 'utf8'), {
    url: 'https://regression.invalid/' + names[number], runScripts: 'outside-only',
    pretendToBeVisual: true, virtualConsole: vc,
  });
  const w = dom.window, d = w.document;
  w.matchMedia = q => ({ matches: q.includes('max-width') && Boolean(options.mobile),
    addEventListener() {}, removeEventListener() {} });
  w.HTMLDialogElement.prototype.showModal = function () {
    this.open = true; this.querySelector('button,input,select,textarea')?.focus();
  };
  w.HTMLDialogElement.prototype.close = function () {
    this.open = false; this.dispatchEvent(new w.Event('close'));
  };
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.scrollTo = () => {}; d.execCommand = () => false;
  for (const s of d.querySelectorAll('script')) w.eval(s.textContent);
  t.after(() => { w.close(); assert.deepEqual(errors, []); });
  const $ = s => d.querySelector(s);
  return { w, d, $, click: s => $(s).click(),
    input(s, value) { $(s).value = value; $(s).dispatchEvent(new w.Event('input', { bubbles: true })); },
    key(s, key, modifiers = {}) {
      const e = new w.KeyboardEvent('keydown', { key, bubbles: true, cancelable: true, ...modifiers });
      (typeof s === 'string' ? $(s) : s).dispatchEvent(e); return e;
    },
    cancel(s) { const e = new w.Event('cancel', { cancelable: true }); if ($(s).dispatchEvent(e)) $(s).close(); },
  };
}
for (const mod of ['ctrlKey', 'metaKey']) {
  test('02 ' + mod + '+K inside note dialog preserves draft and exact opener identity', t => {
    const h = fixture(2, t); h.input('#chat-input', 'Keep this draft');
    const opener = h.$('#reading-card'); opener.focus(); h.click('#reading-card');
    const event = h.key('#note-dialog [data-close-dialog]', 'k', { [mod]: true });
    assert.equal(event.defaultPrevented, true, 'do not hand Ctrl/Meta+K to browser chrome');
    assert.equal(h.$('#note-dialog').open, true);
    assert.equal(h.$('#chat-input').value, 'Keep this draft');
    assert.equal(h.$('#reading-card'), opener);
    assert.equal(h.$('#note-dialog')._opener, opener);
    assert.equal(opener.isConnected, true);
    h.click('#note-dialog [data-close-dialog]'); assert.equal(h.d.activeElement, opener);
  });
  test('02 ordinary ' + mod + '+K still creates a new conversation', t => {
    const h = fixture(2, t); h.input('#chat-input', 'Clear intentionally');
    h.$('#chat-input').focus(); const before = h.$('#reading-card');
    const e = h.key('#chat-input', 'k', { [mod]: true });
    assert.equal(e.defaultPrevented, true); assert.equal(h.$('#chat-input').value, '');
    assert.notEqual(h.$('#reading-card'), before); assert.equal(h.d.activeElement, h.$('#chat-input'));
  });
  test('03 ' + mod + '+Enter focuses visible preview tab after hiding editor', t => {
    const h = fixture(3, t); h.click('#code-tab'); h.$('#code-editor').focus();
    assert.equal(h.key('#code-editor', 'Enter', { [mod]: true }).defaultPrevented, true);
    assert.equal(h.$('#code-panel').hidden, true); assert.equal(h.$('#preview-panel').hidden, false);
    assert.equal(h.$('#preview-tab').getAttribute('aria-selected'), 'true');
    assert.equal(h.d.activeElement, h.$('#preview-tab'));
    assert.equal(h.d.activeElement.closest('[hidden]'), null);
  });
  test('03 invalid ' + mod + '+Enter preserves code editor focus and last preview', t => {
    const h = fixture(3, t); h.click('#code-tab'); h.input('#code-editor', '');
    h.$('#code-editor').focus(); const frame = h.$('#preview-frame');
    h.key('#code-editor', 'Enter', { [mod]: true });
    assert.equal(h.$('#code-panel').hidden, false); assert.equal(h.$('#preview-panel').hidden, true);
    assert.equal(h.d.activeElement, h.$('#code-editor')); assert.equal(h.$('#preview-frame'), frame);
  });
  test('06 ' + mod + '+K captures the true opener and repeated opening retains it', t => {
    const h = fixture(6, t); h.cancel('#launcher-dialog'); h.$('#palette').focus();
    h.key('#palette', 'k', { [mod]: true }); h.input('#launcher-input', 'Keep draft');
    assert.equal(h.$('#launcher-dialog')._opener, h.$('#palette'));
    h.click('#open-launcher'); // Programmatic repeated open; does not model pointer access through inert.
    assert.equal(h.$('#launcher-dialog')._opener, h.$('#palette'));
    assert.equal(h.$('#launcher-input').value, 'Keep draft');
    h.key('#launcher-input', 'k', { [mod]: true });
    assert.equal(h.$('#launcher-dialog').open, false); assert.equal(h.d.activeElement, h.$('#palette'));
    h.key('#palette', 'k', { [mod]: true }); assert.equal(h.$('#launcher-dialog').open, true);
    assert.equal(h.$('#launcher-input').value, 'Keep draft');
  });
}
test('02 shortcut respects any open native dialog, not a single hard-coded id', t => {
  const h = fixture(2, t); h.input('#chat-input', 'Keep draft');
  const dialog = h.d.createElement('dialog'); dialog.open = true; h.d.body.append(dialog);
  assert.equal(h.key('#chat-input', 'k', { ctrlKey: true }).defaultPrevented, true);
  assert.equal(h.$('#chat-input').value, 'Keep draft');
});
test('02 new-chat shortcut from mobile drawer still closes drawer and focuses composer', t => {
  const h = fixture(2, t, { mobile: true }); h.click('#sidebar-toggle');
  h.key('#sidebar-close', 'k', { ctrlKey: true });
  assert.equal(h.$('#sidebar-toggle').getAttribute('aria-expanded'), 'false');
  assert.equal(h.$('.chat-main').inert, false); assert.equal(h.d.activeElement, h.$('#chat-input'));
});
test('03 clicking update from its focused button does not steal focus to the tab', t => {
  const h = fixture(3, t); h.click('#code-tab'); h.$('#run-code').focus(); h.click('#run-code');
  assert.equal(h.$('#code-panel').hidden, true); assert.equal(h.d.activeElement, h.$('#run-code'));
});
test('03 hiding an active preview panel also migrates focus to the visible code tab', t => {
  const h = fixture(3, t); h.$('#preview-frame').focus(); h.click('#code-tab');
  assert.equal(h.$('#preview-panel').hidden, true); assert.equal(h.d.activeElement, h.$('#code-tab'));
});
for (const method of ['cancel', 'button']) test('06 palette opener survives ' + method + ' close', t => {
  const h = fixture(6, t); h.cancel('#launcher-dialog'); h.$('#palette').focus();
  h.key('#palette', 'k', { ctrlKey: true });
  if (method === 'cancel') h.cancel('#launcher-dialog'); else h.click('#launcher-dialog [data-close-dialog]');
  assert.equal(h.$('#launcher-dialog').open, false); assert.equal(h.d.activeElement, h.$('#palette'));
});
test('06 click opener remains the clicked button even if another control held focus', t => {
  const h = fixture(6, t); h.cancel('#launcher-dialog'); h.$('#palette').focus(); h.click('#open-launcher');
  assert.equal(h.$('#launcher-dialog')._opener, h.$('#open-launcher'));
  h.cancel('#launcher-dialog'); assert.equal(h.d.activeElement, h.$('#open-launcher'));
});
test('06 intentional auto-open still returns to the stable launch button', t => {
  const h = fixture(6, t); assert.equal(h.$('#launcher-dialog').open, true);
  h.cancel('#launcher-dialog'); assert.equal(h.d.activeElement, h.$('#open-launcher'));
});
test('06 capture replacing its original record-button opener uses the stable fallback', t => {
  const h = fixture(6, t); h.input('#launcher-input', 'First capture'); h.key('#launcher-input', 'Enter');
  const opener = h.$('.capture-entry button'); opener.focus(); h.key(opener, 'k', { ctrlKey: true });
  assert.equal(h.$('#launcher-dialog')._opener, opener);
  h.input('#launcher-input', 'Second capture'); h.key('#launcher-input', 'Enter');
  assert.equal(opener.isConnected, false); assert.equal(h.$('#launcher-dialog').open, false);
  assert.equal(h.d.activeElement, h.$('#open-launcher'));
});
