'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const vm = require('node:vm');
const {TextEncoder} = require('node:util');
const {JSDOM, VirtualConsole} = require('jsdom');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
function setup() {
  const errors=[], calls=[];
  const console = new VirtualConsole();
  console.on('jsdomError', error=>errors.push(error.message));
  const dom = new JSDOM(html, {runScripts:'dangerously',url:pathToFileURL(path.join(__dirname,'index.html')).href,pretendToBeVisual:true,virtualConsole:console,beforeParse(window){
    window.TextEncoder=TextEncoder;
    for (const api of ['fetch','XMLHttpRequest','WebSocket','EventSource']) window[api]=function(...args){calls.push({api,args});throw new Error('Network forbidden');};
    window.navigator.sendBeacon=(...args)=>{calls.push({api:'sendBeacon',args});return false;};
  }});
  const w=dom.window, d=w.document;
  return {dom,w,d,errors,calls,model:()=>w.attachmentLesson.createModel(),state:()=>w.attachmentLesson.snapshot(),click:selector=>{const el=d.querySelector(selector);assert(el,selector);el.click();},close:()=>{assert.deepEqual(errors,[]);assert.deepEqual(calls,[]);w.close();}};
}
function invariants(m) {
  assert(m.confirmed>=0);assert(m.reserved>=0);assert(m.occupied<=m.limit);
  assert.equal(m.occupied,m.confirmed+m.reserved);
  for (const r of m.records) {
    if(r.state==='ready'){assert.equal(r.reserved,0);}
    else assert.equal(r.confirmed,0);
    if(r.state!=='deriving')assert.equal(r.reserved,0);
  }
}
test('HTML parses; fixtures count actual UTF-8, not JavaScript length',()=>{
  const a=setup();assert.equal(a.w.attachmentLesson.fixtureBytes.note,18);assert.equal(a.w.attachmentLesson.fixtureBytes.short,7);assert.equal(a.w.attachmentLesson.fixtureBytes.long,36);assert.equal('Hi 🌱'.length,5);assert.equal(a.d.querySelectorAll('input[type="file"]').length,0);a.close();
});
test('out-of-order completion preserves slot order and total occupancy',()=>{
  const a=setup();assert.equal(a.state().reserved,25);a.click('#advance');let s=a.state();assert.deepEqual(Array.from(s.records,r=>r.state),['deriving','ready']);assert.deepEqual(Array.from(s.records,r=>r.slot),[1,2]);assert.equal(s.reserved,18);assert.equal(s.confirmed,7);a.click('#advance');a.click('#advance');s=a.state();assert.equal(s.confirmed,25);assert.equal(s.reserved,0);assert(s.eligibility.ok);a.click('#send');assert.deepEqual(Array.from(a.state().receipt.attachments,r=>r.name),['中文便签.txt','短句.txt']);a.close();
});
test('pending reservation rejects a concurrent request and can be retried after release',()=>{
  const a=setup();a.click('[data-scenario="budget"]');assert.equal(a.state().records[1].state,'rejected');assert.equal(a.state().reserved,18);assert(!a.state().eligibility.ok);a.click('#cancel-'+a.state().records[0].id);assert.equal(a.state().reserved,0);a.click('#retry-'+a.state().records[1].id);assert.equal(a.state().reserved,36);a.click('#advance');a.click('#advance');assert(a.state().eligibility.ok);a.click('#send');assert.equal(a.state().receipt.attachments[0].slot,2);a.close();
});
test('exact boundary is accepted; one more fixture is refused without taking bytes',()=>{
  const a=setup(),m=a.model();m.add('long');m.add('short'); // 43 B
  const first=m.records[0];m.cancel(first.id);m.add('note');m.add('note'); // 43 B again; 4 slots
  assert.equal(m.occupied,43);const before=m.records.length;m.add('short');assert.equal(m.records.length,before);invariants(m);
  const b=a.model();b.limit=36;b.add('long');assert.equal(b.occupied,36);b.add('short');assert.equal(b.records[1].state,'rejected');assert.equal(b.occupied,36);invariants(b);a.close();
});
test('same name has stable, distinct identities',()=>{
  const a=setup(),m=a.model();m.add('note');m.add('note');assert.equal(m.records[0].name,m.records[1].name);assert.notEqual(m.records[0].id,m.records[1].id);m.advance();m.advance();m.advance();m.send();assert.equal(m.receipt.attachments.length,2);a.close();
});
test('cancel releases once and late completion cannot resurrect a record',()=>{
  const a=setup(),m=a.model();m.add('note');const id=m.records[0].id,ticket=m.records[0].ticket;m.cancel(id);m.cancel(id);assert.equal(m.occupied,0);m.complete(ticket);assert.equal(m.records[0].state,'cancelled');assert.equal(m.occupied,0);assert.match(m.events[0].message,/丢弃/);invariants(m);a.close();
});
test('account switch discards old callbacks even after switching back',()=>{
  const a=setup(),m=a.model();m.add('note');const ticket=m.records[0].ticket;m.changeContext('account-b','draft-a');m.add('short');m.changeContext('account-a','draft-a');m.add('note');const before=JSON.stringify(m.records);m.complete(ticket);assert.equal(JSON.stringify(m.records),before);assert.equal(m.occupied,18);a.close();
});
test('draft switch and same-draft reopening invalidate the generation',()=>{
  const a=setup();for (const target of ['draft-b','draft-a']) {const m=a.model();m.add('note');const t=m.records[0].ticket;m.changeContext('account-a',target);m.add('short');m.complete(t);assert.equal(m.records.length,1);assert.equal(m.records[0].fixture,'short');assert.equal(m.occupied,7);assert.notEqual(m.epoch,t.epoch);invariants(m);}a.close();
});
test('UI switching archives pending callbacks and zeroes current ledger',()=>{
  const a=setup();const d=a.d.querySelector('#draft');d.value='draft-b';d.dispatchEvent(new a.w.Event('change',{bubbles:true}));assert.equal(a.state().records.length,0);assert.equal(a.state().stale.length,2);a.click('#late');assert.equal(a.state().records.length,0);assert.equal(a.state().occupied,0);assert.match(a.d.querySelector('#announcer').textContent,/丢弃/);a.close();
});
test('held route does not advance; known transient error only retries manually',()=>{
  const a=setup();a.click('[data-scenario="retry"]');a.click('#advance');a.click('#advance');assert.equal(a.state().records[0].state,'held');assert.equal(a.state().records[1].state,'retryable');assert.equal(a.state().occupied,0);a.click('#advance');assert.equal(a.state().records[1].state,'retryable');const ids=Array.from(a.state().records,r=>r.id);a.click('#retry-'+ids[0]);a.click('#retry-'+ids[1]);a.click('#advance');a.click('#advance');assert(a.state().eligibility.ok);a.click('#send');assert.equal(a.state().receipt.attachments.length,2);assert(a.state().receipt.attachments.every(r=>r.syntheticReference.startsWith('fake:')));assert.equal(a.state().occupied,0);a.close();
});
test('retry ticket rejects stale success from previous attempt',()=>{
  const a=setup(),m=a.model();m.add('image');const old=m.records[0].ticket;m.advance();m.advance();m.retry(m.records[0].id);m.complete(old);assert.equal(m.records[0].state,'deriving');assert.equal(m.records[0].attempt,2);m.advance();m.advance();assert.equal(m.records[0].state,'ready');a.close();
});
test('duplicate current completion cannot double-charge the ledger',()=>{
  const a=setup(),m=a.model();m.add('note');const ticket=m.records[0].ticket;m.complete(ticket);m.complete(ticket);assert.equal(m.confirmed,18);assert.equal(m.reserved,0);assert.equal(m.records.length,1);invariants(m);a.close();
});
test('Send is guarded in code as well as aria-disabled; text does not bypass blockers',()=>{
  const a=setup();assert.equal(a.d.querySelector('#send').getAttribute('aria-disabled'),'true');a.click('#sample-text');a.click('#send');assert.equal(a.state().receipt,null);assert.equal(a.d.querySelector('#receipt').hidden,true);a.click('#reopen');a.click('#send');assert.equal(a.state().receipt,null);a.click('#sample-text');assert(a.state().eligibility.ok);a.click('#send');assert.equal(a.state().receipt.attachments.length,0);assert.equal(a.state().receipt.text,'请比较这些合成素材。');a.close();
});
test('cancelled slots do not block Send; removing ready data releases confirmation',()=>{
  const a=setup(),m=a.model();m.add('note');m.add('short');m.cancel(m.records[0].id);m.advance();assert(m.eligibility().ok);assert.equal(m.confirmed,7);m.cancel(m.records[1].id);assert.equal(m.confirmed,0);assert(!m.eligibility().ok);invariants(m);a.close();
});
test('receipt is a snapshot, not a mutable reflection of later changes',()=>{
  const a=setup(),m=a.model();m.add('short');m.advance();m.send();const receipt=JSON.stringify(m.receipt);m.cancel(m.records[0].id);m.add('note');assert.equal(JSON.stringify(m.receipt),receipt);const external=m.snapshot();external.receipt.attachments[0].name='changed';assert.equal(JSON.stringify(m.receipt),receipt);a.close();
});
test('focus returns to the same fixed slot when its cancel control disappears',()=>{
  const a=setup();const id=a.state().records[0].id,b=a.d.querySelector('#cancel-'+id);b.focus();assert.equal(a.d.activeElement,b);b.click();assert.equal(a.d.activeElement.id,'slot-1');assert.equal(a.d.activeElement.tabIndex,-1);a.close();
});
test('focus survives a full card repaint; retry disappearance returns to its slot',()=>{
  const a=setup();a.click('[data-scenario="retry"]');const id=a.state().records[0].id;const cancel=a.d.querySelector('#cancel-'+id);cancel.focus();a.click('#advance');assert.equal(a.d.activeElement.id,'cancel-'+id);const retry=a.d.querySelector('#retry-'+id);retry.focus();retry.click();assert.equal(a.d.activeElement.id,'slot-1');a.close();
});
test('polite atomic announcements include reason and both budget values',()=>{
  const a=setup();a.click('#advance');const el=a.d.querySelector('#announcer');assert.equal(el.getAttribute('role'),'status');assert.equal(el.getAttribute('aria-live'),'polite');assert.equal(el.getAttribute('aria-atomic'),'true');assert.match(el.textContent,/已确认 7 字节，已预留 18 字节/);assert.match(el.textContent,/暂不可发送/);a.close();
});
test('static accessibility contracts: IDs, reference targets, labels, focus, motion',()=>{
  const a=setup(),ids=new Set();for(const el of a.d.querySelectorAll('[id]')){assert(!ids.has(el.id),'duplicate id '+el.id);ids.add(el.id);}
  for(const el of a.d.querySelectorAll('[aria-describedby],[aria-labelledby]'))for(const attr of ['aria-describedby','aria-labelledby'])for(const id of (el.getAttribute(attr)||'').split(/\s+/).filter(Boolean))assert(ids.has(id),'missing '+id);
  for(const el of a.d.querySelectorAll('input,select'))assert(a.d.querySelector(`label[for="${el.id}"]`));
  for(const b of a.d.querySelectorAll('button'))assert(b.textContent.trim()||b.getAttribute('aria-label'));
  assert(html.includes(':focus-visible'));assert(html.includes('prefers-reduced-motion'));assert(!html.includes('tabindex="1"'));a.close();
});
test('runtime has no external assets, storage, clocks, uploads or service requests',()=>{
  const a=setup();assert.equal(a.d.querySelectorAll('script[src],link[rel="stylesheet"],iframe,img,audio,video,input[type="file"]').length,0);
  assert(!/\b(fetch|XMLHttpRequest|WebSocket|EventSource|setTimeout|setInterval|localStorage|indexedDB|sendBeacon)\s*[.(]/.test(script));
  for(const scenario of ['order','budget','retry','stale']){a.click(`[data-scenario="${scenario}"]`);for(let i=0;i<5;i++)a.click('#advance');a.click('#send');a.click('#reopen');a.click('#late');}a.close();
});
test('deterministic stress trace preserves accounting and ownership invariants',()=>{
  const a=setup(),m=a.model();let seed=2171;const rnd=n=>{seed=(seed*1664525+1013904223)>>>0;return seed%n;};const fixtures=['note','short','long','pdf','image'];
  for(let i=0;i<500;i++){const r=m.records[rnd(Math.max(1,m.records.length))];switch(rnd(8)){case 0:m.add(fixtures[rnd(5)]);break;case 1:m.advance();break;case 2:if(r)m.cancel(r.id);break;case 3:if(r)m.retry(r.id);break;case 4:m.deliverLate();break;case 5:m.changeContext('account-'+rnd(2),'draft-'+rnd(2));break;case 6:m.send();break;case 7:if(r&&r.ticket)m.complete(r.ticket);break;}invariants(m);}a.close();
});

test('budget rejection records its check time rather than claiming current capacity',()=>{
  const a=setup();a.click('[data-scenario="budget"]');
  assert.match(a.state().records[1].reason,/上次检查时剩余 30 B/);
  a.click('#cancel-'+a.state().records[0].id);
  assert.equal(a.state().reserved,0);assert.equal(a.state().confirmed,0);
  assert.match(a.state().records[1].reason,/上次检查时剩余 30 B/);
  assert(!a.state().records[1].reason.includes('当前只剩'));a.close();
});
