'use strict';
// Uses synthetic clipboard write outcomes only. Never reads the system clipboard.
const {JSDOM, VirtualConsole}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
if(process.argv.length!==3)throw Error('Usage: node tests/test_copy_fallback_dom.cjs generated-index.html');
const html=fs.readFileSync(process.argv[2],'utf8'),errors=[],writes=[],legacy=[],network=[],results=[];
const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(String(e)));
const dom=new JSDOM(html,{url:'https://offline.invalid/',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
const w=dom.window,d=w.document,$=id=>d.getElementById(id),payload=$('color-data').textContent,data=JSON.parse(payload);
const dataBefore=JSON.stringify(data),tick=()=>new Promise(r=>setImmediate(r));
let execMode='success',readCalls=0,writeMode='success';
w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};
Object.defineProperty(w,'isSecureContext',{configurable:true,value:true});
const syntheticClipboard={writeText:async text=>{writes.push(text);if(writeMode==='throw')throw Error('synthetic write failure')},readText:()=>{readCalls++;throw Error('Clipboard reads forbidden in this test')}};
Object.defineProperty(w.navigator,'clipboard',{configurable:true,value:syntheticClipboard});
d.execCommand=command=>{
  assert.equal(command,'copy');const helper=d.querySelector('.clipboard-helper');assert(helper,'Missing transient textarea');
  const modal=$('detailDialog').open;assert.equal(helper.parentElement,modal?$('detailDialog'):d.body,'Modal copy target must not be in an inert body sibling');
  assert.equal(d.activeElement,helper);assert.equal(helper.selectionStart,0);assert.equal(helper.selectionEnd,helper.value.length);
  assert(helper.readOnly);legacy.push({text:helper.value,host:modal?'dialog':'body'});
  if(execMode==='throw')throw Error('synthetic execCommand failure');return execMode!=='false';
};
w.fetch=()=>network.push('fetch');w.XMLHttpRequest=class{open(){network.push('xhr')}};
w.eval([...d.querySelectorAll('script')].filter(s=>s.type!=='application/json').map(s=>s.textContent).join('\n'));
function test(name,fn){fn();results.push(name)}
function click(selector){const e=d.querySelector(selector);assert(e,'Missing '+selector);e.click()}
function open(profile,name){click('#resetButton');click(`[data-profile="${profile}"]`);$('search').value=name;$('search').dispatchEvent(new w.Event('input'));click(`[data-id="${profile}:${name}"] .sample-open`)}
function secure(value){Object.defineProperty(w,'isSecureContext',{configurable:true,value})}
function resetFocus(){const button=$('copyOriginal');button.focus();return button}
(async()=>{
  const raw=data.records.find(r=>r.id==='raw:--cds-blue-600');open(raw.profile,raw.name);
  test('Manual field is visible, read-only and defaults to the exact current value',()=>{assert($('manualCopyText').readOnly);assert(!$('manualCopyText').hidden);assert.equal($('manualCopyText').value,`${raw.hex.toUpperCase()}; alpha: ${raw.alpha}`)});
  test('Manual select action selects all text without any clipboard operation',()=>{const n=writes.length,m=legacy.length;click('#selectManualCopy');assert.equal(d.activeElement,$('manualCopyText'));assert.equal($('manualCopyText').selectionStart,0);assert.equal($('manualCopyText').selectionEnd,$('manualCopyText').value.length);assert.equal(writes.length,n);assert.equal(legacy.length,m);assert($('toast').textContent.includes('Ctrl+C'))});
  test('Every detail copy target synchronizes the manual field',()=>{click('#copyToken');assert.equal($('manualCopyText').value,raw.name);click('#copyOriginal');assert.equal($('manualCopyText').value,raw.declared);click('#copyDetail');assert.equal($('manualCopyText').value,`${raw.hex.toUpperCase()}; alpha: ${raw.alpha}`)});
  await tick();
  test('Modern write path awaits fulfillment and makes no system-paste claim',()=>{assert.equal(legacy.length,0);assert.equal(writes.at(-1),`${raw.hex.toUpperCase()}; alpha: ${raw.alpha}`);assert($('toast').textContent.includes('浏览器已完成复制请求'));assert.equal(d.querySelectorAll('.clipboard-helper').length,0)});
  const pending=[];
  Object.defineProperty(w.navigator,'clipboard',{configurable:true,value:{readText:syntheticClipboard.readText,writeText:text=>new Promise((resolve,reject)=>{writes.push(text);pending.push({resolve,reject})})}});
  $('toast').textContent='pending-marker';click('#copyOriginal');click('#copyToken');
  test('Pending modern writes do not prematurely report request completion',()=>assert.equal($('toast').textContent,'pending-marker'));
  pending[1].resolve();await tick();const newerSuccess=$('toast').textContent;pending[0].reject(Error('older failed'));await tick();
  test('Older failure cannot replace newer success or the latest manual value',()=>{assert(newerSuccess.includes('浏览器已完成'));assert.equal($('toast').textContent,newerSuccess);assert.equal($('manualCopyText').value,raw.name)});
  click('#copyOriginal');click('#copyToken');pending[3].reject(Error('newer failed'));await tick();const newerFailure=$('toast').textContent;pending[2].resolve();await tick();
  test('Older success cannot replace newer failure',()=>{assert(newerFailure.includes('自动复制未完成'));assert.equal($('toast').textContent,newerFailure)});
  click('#copyOriginal');click('#closeDialog');$('toast').textContent='closed-marker';pending[4].resolve();await tick();
  test('Closing the dialog invalidates pending copy feedback',()=>assert.equal($('toast').textContent,'closed-marker'));
  open(raw.profile,raw.name);click('#copyOriginal');const other=data.records.find(r=>r.id==='raw:--cds-blue-650');open(other.profile,other.name);$('toast').textContent='new-detail-marker';pending[5].reject(Error('old detail failed'));await tick();
  test('Changing details invalidates pending feedback without overwriting new text',()=>{assert.equal($('toast').textContent,'new-detail-marker');assert.equal($('manualCopyText').value,`${other.hex.toUpperCase()}; alpha: ${other.alpha}`)});
  click('#copyOriginal');click('#selectManualCopy');const selectedMessage=$('toast').textContent;pending[6].resolve();await tick();
  test('Explicit manual selection keeps its guidance when an older request completes',()=>assert.equal($('toast').textContent,selectedMessage));
  open(raw.profile,raw.name);click('#copyOriginal');$('detailDialog').dispatchEvent(new w.Event('cancel'));$('toast').textContent='cancel-marker';pending[7].resolve();await tick();
  test('Native cancel invalidates pending copy feedback',()=>assert.equal($('toast').textContent,'cancel-marker'));
  Object.defineProperty(w.navigator,'clipboard',{configurable:true,value:syntheticClipboard});
  writeMode='throw';resetFocus();click('#copyOriginal');await tick();
  test('Modern rejection preserves manual text without trying a legacy permission bypass',()=>{assert.equal($('manualCopyText').value,raw.declared);assert.equal(legacy.length,0);assert($('toast').textContent.includes('自动复制未完成'));assert.equal(d.activeElement,$('copyOriginal'))});
  writeMode='success';secure(false);let prior=resetFocus();click('#copyOriginal');await tick();
  test('Legacy dialog helper uses the active dialog, cleans up and restores focus',()=>{assert.equal(legacy.at(-1).host,'dialog');assert.equal(legacy.at(-1).text,raw.declared);assert.equal(d.querySelectorAll('.clipboard-helper').length,0);assert.equal(d.activeElement,prior);assert($('toast').textContent.includes('已尝试复制'));assert(!$('toast').textContent.includes('已复制：'))});
  execMode='throw';prior=resetFocus();click('#copyOriginal');await tick();
  test('Thrown execCommand always cleans up and restores focus',()=>{assert.equal(d.querySelectorAll('.clipboard-helper').length,0);assert.equal(d.activeElement,prior);assert.equal($('manualCopyText').value,raw.declared);assert($('toast').textContent.includes('自动复制未完成'))});
  execMode='false';prior=resetFocus();click('#copyOriginal');await tick();
  test('False execCommand result cleans up and reports incomplete copy',()=>{assert.equal(d.querySelectorAll('.clipboard-helper').length,0);assert.equal(d.activeElement,prior);assert($('toast').textContent.includes('自动复制未完成'))});
  execMode='success';const originalFocus=w.HTMLTextAreaElement.prototype.focus;w.HTMLTextAreaElement.prototype.focus=function(...args){if(this.classList.contains('clipboard-helper'))return;return originalFocus.apply(this,args)};const beforeRejected=legacy.length;prior=resetFocus();click('#copyOriginal');await tick();w.HTMLTextAreaElement.prototype.focus=originalFocus;
  test('Selection cannot be accepted if the transient field did not receive focus',()=>{assert.equal(legacy.length,beforeRejected);assert.equal(d.querySelectorAll('.clipboard-helper').length,0);assert.equal(d.activeElement,prior);assert($('toast').textContent.includes('自动复制未完成'))});
  test('Repeated fallback copy operations leave no helper elements or focus drift',()=>{for(let i=0;i<8;i++){const button=resetFocus();click('#copyOriginal');assert.equal(d.querySelectorAll('.clipboard-helper').length,0);assert.equal(d.activeElement,button)}});
  click('#closeDialog');const card=d.querySelector('.card-copy');card.focus();card.click();await tick();
  test('Non-modal copy helper uses body and restores the invoking card focus',()=>{assert.equal(legacy.at(-1).host,'body');assert.equal(d.querySelectorAll('.clipboard-helper').length,0);assert.equal(d.activeElement,card)});
  secure(true);Object.defineProperty(w.navigator,'clipboard',{configurable:true,value:{readText:syntheticClipboard.readText}});open(raw.profile,raw.name);prior=resetFocus();click('#copyOriginal');await tick();
  test('Missing writeText method takes the guarded fallback path',()=>{assert.equal(legacy.at(-1).text,raw.declared);assert.equal(legacy.at(-1).host,'dialog');assert.equal(d.activeElement,prior)});
  Object.defineProperty(w.navigator,'clipboard',{configurable:true,value:syntheticClipboard});
  for(const record of data.records.filter(r=>data.resolution_extension?.records[r.id])){open(record.profile,record.name);const x=data.resolution_extension.records[record.id];test(record.id+' manual value preserves the original or unclipped derived string',()=>{assert.equal($('manualCopyText').value,x.audit_status==='statically_resolved'?x.css_color_srgb:record.declared);click('#copyOriginal');assert.equal($('manualCopyText').value,record.declared);if(!$('copyExpanded').hidden){click('#copyExpanded');assert.equal($('manualCopyText').value,record.resolved_expression)}if(!$('copyHex').hidden){click('#copyHex');assert.equal($('manualCopyText').value,`${x.hex.toUpperCase()}; alpha: ${x.alpha}`)}click('#selectManualCopy');assert.equal($('manualCopyText').selectionEnd,$('manualCopyText').value.length)});click('#closeDialog')}
  await tick();
  test('No clipboard read permission, source mutation, network calls or script errors',()=>{assert.equal(readCalls,0);assert.equal($('color-data').textContent,payload);assert.equal(JSON.stringify(JSON.parse($('color-data').textContent)),dataBefore);assert(!html.includes('clipboard-read'));assert(!html.includes('navigator.clipboard.read'));assert.deepEqual(network,[]);assert.deepEqual(errors,[])});
  console.log(JSON.stringify({status:'passed',tests:results.length,results,html_sha256:crypto.createHash('sha256').update(html).digest('hex'),scope:'Synthetic DOM behavior only; no real clipboard access, permission request, system paste verification or browser bridge assertion.'},null,2));w.close();
})().catch(e=>{console.error(e);w.close();process.exit(1)});
