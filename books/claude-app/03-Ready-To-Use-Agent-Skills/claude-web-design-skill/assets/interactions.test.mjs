// Static and simulated-DOM checks only: no browser rendering, inertness, native
// autofocus, Escape dispatch, Tab order, target geometry, or AT is tested here.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const html = readFileSync(new URL('./interaction-recipes.html', import.meta.url), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const style = html.match(/<style>([\s\S]*?)<\/style>/)[1];
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);

function setup() {
  const queue = [];
  let document;
  class Element {
    constructor(id) {
      this.id = id; this.attrs = {}; this.dataset = {}; this.events = {};
      this.children = []; this.textContent = ''; this.value = ''; this.returnValue = '';
      this.open = false; this.isConnected = true; this.disabled = false;
      this.blockedAncestor = false; this.visible = true; this.showCalls = 0;
    }
    addEventListener(type, fn) { (this.events[type] ||= []).push(fn); }
    fire(type, extra = {}) {
      const event = { currentTarget: this, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; }, ...extra };
      for (const fn of this.events[type] || []) fn(event);
      return event;
    }
    setAttribute(name, value) { this.attrs[name] = value; }
    removeAttribute(name) { delete this.attrs[name]; }
    focus() { document.activeElement = this; }
    closest() { return this.blockedAncestor ? {} : null; }
    getClientRects() { return this.visible ? [{}] : []; }
    append(child) { this.children.push(child); }
    showModal() { this.showCalls++; this.open = true; } // Deliberately does not emulate autofocus/inert.
    close(value) {
      if (!this.open) return;
      if (value !== undefined) this.returnValue = value;
      this.open = false;
      queue.push(() => this.fire('close')); // No browser focus algorithm is emulated.
    }
    set innerHTML(_) { throw new Error('HTML insertion is not allowed in this example'); }
  }
  const elements = Object.fromEntries(ids.map(id => [id, new Element(id)]));
  const root = new Element('html'); root.dataset.density = 'comfortable';
  document = { documentElement: root, activeElement: null, getElementById: id => elements[id], createElement: tag => new Element(tag) };
  vm.runInNewContext(script, { document });
  return { elements, root, document, flush: () => { while (queue.length) queue.shift()(); } };
}

function open(s) { s.elements['open-note'].focus(); s.elements['open-note'].fire('click'); }

test('original interaction example parses and declares named modal/field plus local-only resources', () => {
  new vm.Script(script);
  assert.equal(ids.length, new Set(ids).size);
  for (const attr of ['aria-labelledby', 'aria-describedby']) {
    for (const match of html.matchAll(new RegExp(`${attr}="([^"]+)"`, 'g'))) {
      for (const id of match[1].split(/\s+/)) assert.ok(ids.includes(id), `missing ${id}`);
    }
  }
  assert.match(html, /<dialog\b[^>]*id="note-dialog"[^>]*aria-labelledby="note-title"/);
  assert.match(html, /<textarea\b[^>]*id="note-text"[^>]*autofocus/);
  assert.ok(!/<dialog\b[^>]*(?:\sopen(?:\s|>)|tabindex)/.test(html));
  assert.ok(!/\binnerHTML\b|https?:\/\/|\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(/.test(html));
  assert.ok(!/addEventListener\(['"]keydown/.test(script), 'No home-grown Tab/Escape trap');
});

test('compact overrides only layout tokens; reading and target tokens remain independent', () => {
  const declarations = body => Object.fromEntries([...body.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map(m => [m[1], m[2].trim()]));
  const root = declarations(style.match(/:root\s*\{([^}]+)\}/)[1]);
  assert.equal(root['--reading-size'], '1rem');
  assert.equal(root['--reading-leading'], '1.75');
  assert.equal(root['--control-min'], '44px');
  const compact = [...style.matchAll(/:root\[data-density="compact"\]\s*\{([^}]+)\}/g)];
  assert.ok(compact.length > 0);
  const allowed = ['--chrome-gap', '--chrome-pad', '--section-pad'];
  for (const rule of compact) {
    assert.ok(Object.keys(declarations(rule[1])).every(key => allowed.includes(key)));
    assert.ok(!/(?:font(?:-size)?|line-height|min-(?:width|height))\s*:/.test(rule[1]));
  }
  assert.notEqual(declarations(compact[0][1])['--chrome-pad'], root['--chrome-pad']);
  assert.match(style, /@media\s*\(any-pointer:\s*coarse\)[\s\S]*--control-min:\s*48px/);
  assert.match(style, /button\s*\{[^}]*min-width:\s*var\(--control-min\)[^}]*min-height:\s*var\(--control-min\)/);
  assert.match(style, /\.reading\s*\{[^}]*padding:\s*var\(--section-pad\) 1rem/);
  assert.match(style, /\.reading\s*\{[^}]*max-width:\s*48rem[^}]*font-size:\s*var\(--reading-size\)[^}]*line-height:\s*var\(--reading-leading\)/);
});

test('simulated settings round-trip aria-pressed without changing draft or focus', () => {
  const s = setup(); const e = s.elements;
  e['note-text'].value = '保留这段草稿'; e['density-toggle'].focus();
  for (const id of ['density-toggle', 'theme-toggle']) {
    e[id].fire('click'); assert.equal(e[id].attrs['aria-pressed'], 'true');
    e[id].fire('click'); assert.equal(e[id].attrs['aria-pressed'], 'false');
  }
  assert.equal(s.root.dataset.density, 'comfortable'); assert.equal(s.root.dataset.theme, 'light');
  assert.equal(e['note-text'].value, '保留这段草稿'); assert.equal(s.document.activeElement.id, 'density-toggle');
});

test('simulated open guards repeated calls and resets stale return value', () => {
  const s = setup(); const dialog = s.elements['note-dialog']; dialog.returnValue = 'saved';
  open(s); s.elements['open-note'].fire('click');
  assert.equal(dialog.open, true); assert.equal(dialog.showCalls, 1); assert.equal(dialog.returnValue, '');
});

test('unsupported dialog API reports the limit without pretending to open', () => {
  const s = setup(); s.elements['note-dialog'].showModal = undefined; open(s);
  assert.equal(s.elements['note-dialog'].open, false);
  assert.match(s.elements.status.textContent, /不支持/);
});

test('simulated close returns to invoker and preserves draft through reopen', () => {
  const s = setup(); const e = s.elements; open(s);
  e['note-text'].value = '未提交'; e['note-text'].focus(); e['cancel-note'].fire('click'); s.flush();
  assert.equal(e['note-dialog'].open, false); assert.equal(e['note-dialog'].returnValue, 'cancel');
  assert.equal(s.document.activeElement, e['open-note']); assert.equal(e['note-text'].value, '未提交');
  open(s); assert.equal(e['note-text'].value, '未提交'); assert.equal(e['note-dialog'].returnValue, '');
});

test('cancel handler leaves native default unprevented; simulated later close restores focus', () => {
  const s = setup(); const e = s.elements; open(s); e['note-text'].focus();
  const event = e['note-dialog'].fire('cancel');
  assert.equal(event.defaultPrevented, false); assert.equal(e['note-dialog'].open, true);
  assert.equal(s.document.activeElement, e['note-text']);
  // Explicit test harness completion, NOT evidence of a real Escape/default action.
  e['note-dialog'].close(); s.flush();
  assert.equal(e['note-dialog'].returnValue, 'cancel'); assert.equal(s.document.activeElement, e['open-note']);
});

test('simulated missing, disabled, hidden or inert invoker uses page-title fallback', () => {
  for (const mutation of [e => { e.isConnected = false; }, e => { e.disabled = true; }, e => { e.visible = false; }, e => { e.blockedAncestor = true; }]) {
    const s = setup(); open(s); mutation(s.elements['open-note']);
    s.elements['cancel-note'].fire('click'); s.flush();
    assert.equal(s.document.activeElement, s.elements['page-title']);
  }
});

test('queued close handler does not steal focus from a rapidly reopened dialog', () => {
  const s = setup(); const e = s.elements; open(s); e['cancel-note'].fire('click');
  e['open-note'].fire('click'); e['note-text'].focus(); s.flush();
  assert.equal(e['note-dialog'].open, true); assert.equal(s.document.activeElement, e['note-text']);
  e['cancel-note'].fire('click'); s.flush(); assert.equal(s.document.activeElement, e['open-note']);
});

test('back-to-back simulated close/reopen/close does not overwrite restored focus', () => {
  const s = setup(); const e = s.elements; open(s); e['cancel-note'].fire('click');
  e['open-note'].fire('click'); e['cancel-note'].fire('click'); s.flush();
  assert.equal(s.document.activeElement, e['open-note']);
});

test('simulated empty validation keeps dialog open and focuses described error field', () => {
  const s = setup(); const e = s.elements; open(s); e['note-text'].value = '  ';
  const event = e['note-form'].fire('submit');
  assert.equal(event.defaultPrevented, true); assert.equal(e['note-dialog'].open, true);
  assert.equal(e['note-text'].attrs['aria-invalid'], 'true'); assert.ok(e['note-error'].textContent);
  assert.equal(s.document.activeElement, e['note-text']); assert.equal(e.notes.children.length, 0);
  e['note-text'].fire('input'); assert.equal(e['note-text'].attrs['aria-invalid'], undefined); assert.equal(e['note-error'].textContent, '');
});

test('simulated success inserts literal text, clears only submitted draft and restores invoker', () => {
  const s = setup(); const e = s.elements; open(s);
  e['note-text'].value = '  <img src=x onerror=alert(1)>  '; e['note-form'].fire('submit'); s.flush();
  assert.equal(e.notes.children.length, 1); assert.equal(e.notes.children[0].textContent, '<img src=x onerror=alert(1)>');
  assert.equal(e['note-text'].value, ''); assert.equal(e['note-dialog'].returnValue, 'saved');
  assert.equal(e['note-dialog'].open, false); assert.equal(s.document.activeElement, e['open-note']);
  assert.match(e.status.textContent, /刷新即清除/);
});

test('all local Markdown links and HTML resource references stay inside the portable package', () => {
  const base = fileURLToPath(new URL('../', import.meta.url));
  const walk = folder => readdirSync(folder, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? walk(path.join(folder, entry.name)) : [path.join(folder, entry.name)]);
  for (const file of walk(base).filter(file => /\.(?:md|html)$/.test(file))) {
    const text = readFileSync(file, 'utf8');
    const refs = file.endsWith('.md') ? [...text.matchAll(/\]\(([^)]+)\)/g)].map(m => m[1]) : [...text.matchAll(/\b(?:src|href)="([^"]+)"/g)].map(m => m[1]);
    for (const ref of refs) {
      if (/^(?:https?:|#)/.test(ref)) continue;
      const target = path.resolve(path.dirname(file), ref.split('#')[0]);
      assert.ok(target.startsWith(base), `nonportable link: ${ref}`);
      assert.ok(existsSync(target), `missing local link: ${ref}`);
    }
  }
});
