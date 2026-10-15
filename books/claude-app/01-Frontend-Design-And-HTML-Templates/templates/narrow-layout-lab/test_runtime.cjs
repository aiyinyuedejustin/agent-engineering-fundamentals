'use strict';
// Original minimal-DOM tests of harness control flow, not layout or CSP enforcement.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto, createHash } = require('node:crypto');
const html = fs.readFileSync(path.join(__dirname, 'fixture.html'), 'utf8');
const dataText = html.match(/<script id="fixture-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const originalPayload = JSON.parse(dataText);

function element() {
  return {
    textContent: '', value: '', dataset: {}, style: {}, attributes: {}, children: [], events: {},
    clientHeight: 900, loads: 0, _source: '', connected: false,
    append(child) { this.children.push(child); },
    cloneNode() {
      const next = element();
      next.style = {...this.style}; next.dataset = {...this.dataset};
      next.attributes = {...this.attributes}; next.title = this.title;
      next._source = this._source; next.loads = this.loads;
      return next;
    },
    replaceWith(next) {
      next.onReplace = this.onReplace;
      this.connected = false; next.connected = true;
      this.onReplace?.(next);
    },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; if (name === 'srcdoc') this._source = ''; },
    addEventListener(name, listener) { (this.events[name] ||= []).push(listener); },
    async dispatch(name) { await Promise.all((this.events[name] || []).map(listener => listener({target: this}))); },
    getBoundingClientRect() { return {width: this.overrideWidth ?? (parseFloat(this.style.width) || 375)}; },
    get srcdoc() { return this._source; },
    set srcdoc(source) { this.loads++; this._source = source; }
  };
}

function harness({payload = originalPayload, crypto = webcrypto} = {}) {
  const ids = Object.fromEntries(['fixture-data', 'template-select', 'template-frame', 'geometry', 'source-name', 'source-sha', 'load-status', 'reload-template'].map(id => [id, element()]));
  ids['fixture-data'].textContent = JSON.stringify(payload);
  ids['template-frame'].connected = true;
  ids['template-frame'].onReplace = next => {ids['template-frame'] = next;};
  const observed = new Set();
  const widths = [375, 768, 1024].map(width => Object.assign(element(), {dataset: {width: String(width)}}));
  const window = element();
  const context = vm.createContext({
    document: {getElementById: id => ids[id], querySelectorAll: () => widths, createElement: element},
    window, crypto, TextDecoder, Uint8Array, atob,
    requestAnimationFrame: callback => callback(),
    ResizeObserver: class {constructor(callback) {this.callback = callback;} observe(target) {observed.add(target); this.callback();} unobserve(target) {observed.delete(target);}}
  });
  vm.runInContext(script, context, {timeout: 1000});
  return {ids, widths, window, context, observed};
}

async function until(predicate) {
  const deadline = Date.now() + 3000;
  while (!predicate()) {
    if (Date.now() > deadline) throw new Error('Harness did not settle');
    await new Promise(resolve => setImmediate(resolve));
  }
}
function sha(value) {return createHash('sha256').update(value).digest('hex');}


test('initial fixed source is byte-identical and measured at the 375 mock CSS-px width', async () => {
  const {ids} = harness();
  await until(() => ids['template-frame'].srcdoc);
  assert.equal(sha(ids['template-frame'].srcdoc), originalPayload.templates[0].sha256);
  assert.equal(ids['source-sha'].textContent, originalPayload.templates[0].sha256);
  assert.match(ids.geometry.textContent, /选中 375 CSS px.*实测 375 × 900 CSS px/);
  assert.equal(ids['template-frame'].dataset.digest, 'verified');
});

test('six menu entries only; all switch to the corresponding exact fixed source', async () => {
  const {ids} = harness();
  await until(() => ids['template-frame'].srcdoc);
  assert.equal(ids['template-select'].children.length, 6);
  for (let index = 0; index < 6; index++) {
    ids['template-select'].value = String(index);
    await ids['template-select'].dispatch('change');
    assert.equal(sha(ids['template-frame'].srcdoc), originalPayload.templates[index].sha256);
    assert.equal(ids['source-name'].textContent, originalPayload.templates[index].filename);
  }
});

test('repeated width changes update dimensions without reloading or rewriting the source', async () => {
  const {ids, widths} = harness();
  await until(() => ids['template-frame'].srcdoc);
  const source = ids['template-frame'].srcdoc;
  const loads = ids['template-frame'].loads;
  for (const index of [1, 2, 0, 0, 2]) {
    await widths[index].dispatch('click');
    assert.equal(ids['template-frame'].style.width, `${widths[index].dataset.width}px`);
    assert.equal(ids['template-frame'].srcdoc, source);
    assert.equal(ids['template-frame'].loads, loads);
    assert.equal(widths[index].attributes['aria-pressed'], 'true');
    assert.equal(widths.filter(button => button.attributes['aria-pressed'] === 'true').length, 1);
  }
});

test('reload preserves selected width and reuses exact initial source', async () => {
  const {ids, widths} = harness();
  await until(() => ids['template-frame'].srcdoc);
  await widths[1].dispatch('click');
  const loads = ids['template-frame'].loads;
  await ids['reload-template'].dispatch('click');
  assert.equal(ids['template-frame'].style.width, '768px');
  assert.equal(ids['template-frame'].loads, loads + 1);
  assert.equal(sha(ids['template-frame'].srcdoc), originalPayload.templates[0].sha256);
});

test('invalid menu and width values cannot select arbitrary content or arbitrary widths', async () => {
  const {ids, widths} = harness();
  await until(() => ids['template-frame'].srcdoc);
  const source = ids['template-frame'].srcdoc;
  for (const value of ['6', '-1', 'https://example.invalid', '1.5']) {
    ids['template-select'].value = value;
    await ids['template-select'].dispatch('change');
    assert.equal(ids['template-frame'].srcdoc, source);
    assert.match(ids['load-status'].textContent, /拒绝非固定模板选项/);
  }
  widths[0].dataset.width = '999';
  await widths[0].dispatch('click');
  assert.equal(ids['template-frame'].style.width, '375px');
});

test('source digest mismatch refuses the payload', async () => {
  const payload = structuredClone(originalPayload);
  const bytes = Buffer.from(payload.templates[0].base64, 'base64');
  bytes[0] ^= 1;
  payload.templates[0].base64 = bytes.toString('base64');
  const {ids} = harness({payload});
  await until(() => ids['load-status'].textContent.startsWith('未装载'));
  assert.equal(ids['template-frame'].srcdoc, '');
  assert.match(ids['load-status'].textContent, /SHA-256 不符/);
});

test('byte-length mismatch refuses the payload before loading', async () => {
  const payload = structuredClone(originalPayload);
  payload.templates[0].bytes++;
  const {ids} = harness({payload});
  await until(() => ids['load-status'].textContent.startsWith('未装载'));
  assert.equal(ids['template-frame'].srcdoc, '');
  assert.match(ids['load-status'].textContent, /字节长度不符/);
});

test('WebCrypto-unavailable fallback accurately discloses build-only verification', async () => {
  const fallback = harness({crypto: null}).ids;
  await until(() => fallback['template-frame'].srcdoc);
  assert.equal(fallback['template-frame'].dataset.digest, 'build-only');
  assert.match(fallback['load-status'].textContent, /仅构建时校验/);
  await fallback['template-frame'].dispatch('load');
  assert.match(fallback['load-status'].textContent, /无 WebCrypto/);
});

test('racing template changes never let the earlier digest overwrite the newer source', async () => {
  const pending = [];
  const crypto = {subtle: {digest: (algorithm, bytes) => new Promise(resolve => pending.push({resolve, bytes}))}};
  const {ids} = harness({crypto});
  ids['template-select'].value = '5';
  const change = ids['template-select'].dispatch('change');
  assert.equal(pending.length, 2);
  pending[1].resolve(await webcrypto.subtle.digest('SHA-256', pending[1].bytes));
  await change;
  assert.equal(sha(ids['template-frame'].srcdoc), originalPayload.templates[5].sha256);
  pending[0].resolve(await webcrypto.subtle.digest('SHA-256', pending[0].bytes));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(sha(ids['template-frame'].srcdoc), originalPayload.templates[5].sha256);
  assert.equal(ids['template-frame'].loads, 1);
});

test('measurement mismatch is visible rather than reported as the requested value', async () => {
  const {ids, window} = harness();
  await until(() => ids['template-frame'].srcdoc);
  ids['template-frame'].overrideWidth = 360;
  await window.dispatch('resize');
  assert.match(ids.geometry.textContent, /选中 375 CSS px.*实测 360 × 900 CSS px/);
  assert.equal(ids.geometry.dataset.matches, 'false');
});

test('iframe load event is explicitly not claimed as visual, interaction or CSP success', async () => {
  const {ids} = harness();
  await until(() => ids['template-frame'].srcdoc);
  await ids['template-frame'].dispatch('load');
  assert.match(ids['load-status'].textContent, /load 不等于页面或 CSP 验收通过/);
});


test('pending initial digest does not label the empty frame as a verified source', async () => {
  const pending = [];
  const crypto = {subtle: {digest: (_algorithm, bytes) => new Promise(resolve => pending.push({resolve, bytes}))}};
  const {ids} = harness({crypto});
  assert.equal(ids['template-frame'].srcdoc, '');
  assert.equal(ids['source-name'].textContent, '');
  assert.equal(ids['source-sha'].textContent, '');
  pending[0].resolve(await webcrypto.subtle.digest('SHA-256', pending[0].bytes));
  await until(() => ids['template-frame'].srcdoc);
  assert.equal(ids['source-sha'].textContent, sha(ids['template-frame'].srcdoc));
});

test('delayed selection retains source attribution and rejects old load before and after atomic frame replacement', async () => {
  const pending = [];
  const crypto = {subtle: {digest: (_algorithm, bytes) => new Promise(resolve => pending.push({resolve, bytes}))}};
  const {ids, widths} = harness({crypto});
  pending[0].resolve(await webcrypto.subtle.digest('SHA-256', pending[0].bytes));
  await until(() => ids['template-frame'].srcdoc);
  const oldFrame = ids['template-frame'];
  await oldFrame.dispatch('load');
  const oldTitle = oldFrame.title;
  ids['template-select'].value = '1';
  const change = ids['template-select'].dispatch('change');
  const pendingStatus = ids['load-status'].textContent;
  assert.match(pendingStatus, /正在核对所选模板/);
  assert.equal(ids['template-frame'], oldFrame);
  assert.equal(ids['source-name'].textContent, originalPayload.templates[0].filename);
  assert.equal(ids['source-sha'].textContent, sha(oldFrame.srcdoc));
  await oldFrame.dispatch('load');
  assert.equal(ids['load-status'].textContent, pendingStatus);
  await widths[1].dispatch('click');
  assert.match(oldFrame.title, /01 组件图谱/);
  assert.match(oldFrame.title, /768 CSS px/);
  assert.notEqual(oldFrame.title, oldTitle);
  pending[1].resolve(await webcrypto.subtle.digest('SHA-256', pending[1].bytes));
  await change;
  const newFrame = ids['template-frame'];
  assert.notEqual(newFrame, oldFrame);
  assert.equal(oldFrame.connected, false);
  assert.equal(newFrame.connected, true);
  assert.equal(ids['source-name'].textContent, originalPayload.templates[1].filename);
  assert.equal(ids['source-sha'].textContent, sha(newFrame.srcdoc));
  assert.equal(newFrame.style.width, '768px');
  const mountedStatus = ids['load-status'].textContent;
  await oldFrame.dispatch('load');
  assert.equal(ids['load-status'].textContent, mountedStatus);
  await newFrame.dispatch('load');
  assert.match(ids['load-status'].textContent, /iframe 已触发 load/);
});

test('a failed newer digest retains the last source and blocks its late load from overwriting the error', async () => {
  const pending = [];
  const crypto = {subtle: {digest: (_algorithm, bytes) => new Promise(resolve => pending.push({resolve, bytes}))}};
  const {ids} = harness({crypto});
  pending[0].resolve(await webcrypto.subtle.digest('SHA-256', pending[0].bytes));
  await until(() => ids['template-frame'].srcdoc);
  const oldFrame = ids['template-frame'];
  ids['template-select'].value = '2';
  const change = ids['template-select'].dispatch('change');
  pending[1].resolve(new Uint8Array(32).buffer);
  await change;
  const status = ids['load-status'].textContent;
  assert.match(status, /未装载.*SHA-256 不符/);
  assert.equal(ids['template-frame'], oldFrame);
  assert.equal(ids['source-sha'].textContent, sha(oldFrame.srcdoc));
  await oldFrame.dispatch('load');
  assert.equal(ids['load-status'].textContent, status);
});

test('replacement moves observation to the new frame and retains the sandbox attributes', async () => {
  const {ids, observed} = harness();
  // Markup attributes are supplied explicitly because this mock does not parse HTML.
  ids['template-frame'].attributes.sandbox = 'allow-scripts';
  ids['template-frame'].attributes.referrerpolicy = 'no-referrer';
  await until(() => ids['template-frame'].srcdoc);
  const oldFrame = ids['template-frame'];
  ids['template-select'].value = '5';
  await ids['template-select'].dispatch('change');
  assert.notEqual(ids['template-frame'], oldFrame);
  assert.equal(observed.size, 1);
  assert.equal(observed.has(oldFrame), false);
  assert.equal(observed.has(ids['template-frame']), true);
  assert.equal(ids['template-frame'].attributes.sandbox, 'allow-scripts');
  assert.equal(ids['template-frame'].attributes.referrerpolicy, 'no-referrer');
});
