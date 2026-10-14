'use strict';
// Optional simulated-DOM tests. Supply the generated HTML path explicitly.
const {JSDOM, VirtualConsole} = require('jsdom');
const fs = require('node:fs');
const assert = require('node:assert/strict');
if (process.argv.length !== 3) {
  console.error('Usage: node tests/test_browser_dom.cjs /path/to/generated/index.html');
  process.exit(2);
}
const html = fs.readFileSync(process.argv[2], 'utf8');
const errors = [], writes = [], downloads = [], network = [], results = [];
const vc = new VirtualConsole();
vc.on('jsdomError', error => errors.push(String(error)));
const dom = new JSDOM(html, {url: 'https://offline.invalid/', runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vc});
const w = dom.window, d = w.document, $ = id => d.getElementById(id);
const click = selector => d.querySelector(selector).click();
const count = () => d.querySelectorAll('.card').length;
const data = JSON.parse($('color-data').textContent);
w.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
w.HTMLDialogElement.prototype.close = function () { this.open = false; };
Object.defineProperty(w, 'isSecureContext', {value: true});
Object.defineProperty(w.navigator, 'clipboard', {configurable: true, value: {writeText: async text => writes.push(text)}});
w.URL.createObjectURL = blob => { downloads.push(blob); return 'blob:offline-test'; };
w.URL.revokeObjectURL = () => {};
w.HTMLAnchorElement.prototype.click = function () { downloads.push(this.download); };
w.fetch = () => network.push('fetch');
w.XMLHttpRequest = class {open() { network.push('xhr'); }};
w.eval([...d.querySelectorAll('script')].filter(script => script.type !== 'application/json').map(script => script.textContent).join('\n'));
function test(name, fn) { fn(); results.push(name); }
function search(value) { $('search').value = value; $('search').dispatchEvent(new w.Event('input')); }
function filter(id, value) { $(id).value = value; $(id).dispatchEvent(new w.Event('change')); }
(async () => {
  test('Initial raw count and dynamic labels', () => {
    assert.equal(count(), data.profiles.raw.record_count);
    assert.equal($('rawCount').textContent, String(data.statistics.raw_palette_entries));
    assert($('sourceVersion').textContent.includes(data.product));
  });
  test('Family, search and exact detail value', () => {
    filter('categoryFilter', 'blue');
    assert.equal(count(), 35);
    search('600');
    assert.equal(count(), 1);
    click('.sample-open');
    assert.equal($('detailTitle').textContent, '--cds-blue-600');
    assert.equal($('detailHex').textContent, data.records.find(r => r.id === 'raw:--cds-blue-600').hex.toUpperCase());
  });
  test('Detail repeatedly closes and reopens', () => {
    click('#closeDialog');
    assert.equal($('detailDialog').open, false);
    for (let i = 0; i < 5; i++) { click('.sample-open'); assert($('detailDialog').open); click('#closeDialog'); }
  });
  test('Empty search and reset', () => {
    search('no-such-color'); assert.equal(count(), 0); assert(d.querySelector('.empty'));
    click('#resetButton'); assert.equal(count(), 315);
  });
  test('Every source profile count matches its payload', () => {
    for (const [key, profile] of Object.entries(data.profiles)) {
      click(`[data-profile="${key}"]`); assert.equal(count(), profile.record_count, key);
    }
  });
  test('Exact alpha and clipboard content', () => {
    click('[data-profile="cds_light"]'); search('fill-field'); click('.sample-open');
    const record = data.records.find(r => r.id === 'cds_light:--cds-fill-field');
    assert($('detailAlpha').textContent.includes(String(record.alpha)));
    click('#copyDetail'); assert.equal(writes.at(-1), `${record.hex.toUpperCase()}; alpha: ${record.alpha}`);
    click('#closeDialog'); click('#resetButton');
  });
  test('Unresolved records have neither painted color nor copy HEX action', () => {
    for (const key of ['cds_light', 'cds_dark']) {
      click(`[data-profile="${key}"]`); filter('statusFilter', 'unresolved');
      assert.equal(count(), data.records.filter(r => r.profile === key && r.status === 'unresolved').length);
      for (const sample of d.querySelectorAll('.card .sample-fill')) assert.equal(sample.style.background, '');
      if (count()) { click('.sample-open'); assert($('copyDetail').hidden); assert.equal($('detailHex').textContent, '保留表达式'); click('#closeDialog'); }
    }
  });
  test('Profile switches reset category and status filters', () => {
    click('[data-profile="cds_light"]'); assert.equal($('statusFilter').value, '');
    assert.equal(count(), data.profiles.cds_light.record_count);
  });
  test('Translucent-only filter', () => {
    filter('statusFilter', 'translucent');
    assert.equal(count(), data.records.filter(r => r.profile === 'cds_light' && r.status === 'resolved' && r.alpha < 1).length);
  });
  test('Dark canvas and opacity backgrounds remain independent', () => {
    click('#themeToggle'); assert(d.body.classList.contains('theme-dark'));
    filter('canvasBackground', 'dark'); assert(d.body.classList.contains('dark-bg'));
    filter('canvasBackground', 'light'); assert(d.body.classList.contains('light-bg')); assert(!d.body.classList.contains('dark-bg'));
    filter('canvasBackground', 'checker'); assert(!d.body.classList.contains('light-bg')); assert(d.body.classList.contains('theme-dark'));
  });
  test('CSV export has expected filename and UTF-8 payload', () => {
    click('[data-profile="legacy_v2_light"]'); click('#exportButton');
    assert.equal(downloads.at(-1), 'color-catalog-legacy_v2_light.csv');
    assert(downloads[0].size > 100);
  });
  test('Browser payload omits large provenance inventory', () => {
    assert(!data.blocks && !data.definition_inventory);
    assert(data.records.every(r => !r.resolution_chain && r.byte_start === undefined));
  });
  await new Promise(resolve => setImmediate(resolve));
  Object.defineProperty(w.navigator, 'clipboard', {configurable: true, value: {writeText: async () => { throw Error('denied'); }}});
  click('.card-copy');
  await new Promise(resolve => setImmediate(resolve));
  test('Clipboard denial is reported truthfully', () => assert($('toast').textContent.includes('未允许复制')));
  test('No network attempts or runtime errors', () => { assert.deepEqual(network, []); assert.deepEqual(errors, []); });
  console.log(JSON.stringify({status: 'passed', tests: results.length, results,
    scope: 'Simulated DOM only. Does not validate real-browser rendering, native clipboard/dialog or CSS color conversion.'}, null, 2));
  w.close();
})().catch(error => { console.error(error); w.close(); process.exit(1); });
