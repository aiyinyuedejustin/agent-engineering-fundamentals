'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require('jsdom');
const ROOT = path.resolve(__dirname, '../..');
const DEMO = path.join(ROOT, 'demo');
function createHarness(options = {}) {
  const errors = [], transmissions = [], writes = [], storage = new Map(Object.entries(options.storage || {}));
  const vconsole = new VirtualConsole();
  vconsole.on('jsdomError', error => errors.push(String(error)));
  let width = options.width || 1440, dark = options.dark || false, reduce = options.reduce || false;
  const queries = new Map();
  const dom = new JSDOM(fs.readFileSync(path.join(DEMO, 'index.html'), 'utf8'), { url: options.url || 'https://demo.invalid/demo/', runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vconsole });
  const w = dom.window, d = w.document;
  // These patches deliberately model browser-only surfaces; they are not a browser or layout implementation.
  const evaluateQuery = q => q.includes('max-width: 760px') ? width <= 760 : q.includes('max-width: 1000px') ? width <= 1000 : q.includes('prefers-color-scheme') ? dark : q.includes('prefers-reduced-motion') ? reduce : false;
  w.matchMedia = query => { if (!queries.has(query)) { const listeners = new Set(); queries.set(query, { media: query, get matches() { return evaluateQuery(query); }, addEventListener(type, fn) { if(type === 'change') listeners.add(fn); }, removeEventListener(type, fn) { listeners.delete(fn); }, listeners }); } return queries.get(query); };
  function changeMedia(next) { const old = new Map([...queries].map(([q,m]) => [q,m.matches])); if ('width' in next) width = next.width; if ('dark' in next) dark = next.dark; if ('reduce' in next) reduce = next.reduce; for (const [q,m] of queries) if (old.get(q) !== m.matches) for(const fn of m.listeners) fn({ matches:m.matches, media:q }); }
  Object.defineProperty(w, 'localStorage', { configurable: true, get() { if (options.storageDenied) throw new w.DOMException('blocked fixture','SecurityError'); return { getItem: k => storage.get(k) ?? null, setItem(k,v) { if(options.writeDenied) throw new w.DOMException('blocked fixture','QuotaExceededError'); writes.push({key:k,value:v}); storage.set(k,String(v)); }, removeItem: k => storage.delete(k), clear() { storage.clear(); writes.push({clear:true}); } }; } });
  function visible(el) { if (!el.isConnected || el.closest('[hidden]')) return false; if (el.closest('dialog') && !el.closest('dialog').open) return false; if (el.closest('#sidebar') && (width <= 760 ? !d.querySelector('#app-shell').classList.contains('sidebar-open') : d.querySelector('#app-shell').classList.contains('sidebar-collapsed'))) return false; if(el.closest('#inspector') && width <= 1000 && !d.querySelector('#inspector').classList.contains('is-overlay')) return false; if (el.classList.contains('sidebar-mobile-close') && width > 760) return false; if (el.classList.contains('inspector-mobile-close') && width > 1000) return false; return true; }
  w.HTMLElement.prototype.getClientRects = function() { return visible(this) ? [{x:10,y:10,width:100,height:40,left:10,right:110,top:10,bottom:50}] : []; };
  w.HTMLElement.prototype.getBoundingClientRect = function() { return {x:10,y:10,width:100,height:40,left:10,right:110,top:10,bottom:50}; };
  if (!('inert' in w.HTMLElement.prototype)) Object.defineProperty(w.HTMLElement.prototype, 'inert', { get(){return this.hasAttribute('inert');}, set(v){this.toggleAttribute('inert',Boolean(v));} });
  w.HTMLDialogElement.prototype.showModal = function() { if (this.open) throw new Error('already open'); this.open = true; };
  w.HTMLDialogElement.prototype.close = function() { if (!this.open) return; this.open = false; this.dispatchEvent(new w.Event('close')); };
  if(!('innerText' in w.HTMLElement.prototype)) Object.defineProperty(w.HTMLElement.prototype,'innerText',{get(){return this.textContent;},set(v){this.textContent=v;}});
  let now = 0, nextTimer = 1;
  const timers = new Map(), archivedTimers = new Map();
  w.setTimeout = (fn,delay=0) => { const id=nextTimer++; const task={id,fn,time:now+Number(delay)}; timers.set(id,task); archivedTimers.set(id,task); return id; };
  w.clearTimeout = id => timers.delete(id);
  function tick(ms) { const end=now+ms; let guard=0; while(true) { const task=[...timers.values()].filter(t=>t.time<=end).sort((a,b)=>a.time-b.time||a.id-b.id)[0]; if(!task)break; if(++guard>10000)throw new Error('Timer runaway'); now=task.time; timers.delete(task.id); task.fn(); } now=end; }
  function blockNetwork(type) { return (...args) => { transmissions.push({type,args:args.map(String)}); throw new Error(`Network fixture blocked ${type}`); }; }
  w.fetch=blockNetwork('fetch'); w.XMLHttpRequest=class{ open(...args){ blockNetwork('xhr')(...args); } }; w.WebSocket=blockNetwork('websocket'); w.EventSource=blockNetwork('eventsource'); w.navigator.sendBeacon=blockNetwork('beacon');
  if(options.clipboard === 'success') Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async text=>writes.push({clipboard:text})}});
  if(options.clipboard === 'reject') Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async()=>{throw new Error('fixture denial');}}});
  for(const file of ['../components/tokens.css','../components/components.css','demo.css']) { const style=d.createElement('style'); style.textContent=fs.readFileSync(path.resolve(DEMO,file),'utf8'); d.head.append(style); }
  w.eval(fs.readFileSync(path.join(DEMO,'evidence.js'),'utf8'));
  w.eval(fs.readFileSync(path.join(DEMO,'demo.js'),'utf8'));
  const $=s=>d.querySelector(s), $$=s=>[...d.querySelectorAll(s)];
  function input(value){ $('#message-input').value=value; $('#message-input').dispatchEvent(new w.Event('input',{bubbles:true})); }
  function key(target,key,extras={}){ const e=new w.KeyboardEvent('keydown',{key,bubbles:true,cancelable:true,...extras}); target.dispatchEvent(e); return e; }
  return {w,d,$,$$,errors,transmissions,writes,storage,timers,archivedTimers,tick,input,key,changeMedia,visible,state:()=>$('#composer').dataset.state,submit:()=>$('#composer').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true})),click:s=>$(s).click(),close:()=>w.close()};
}
module.exports={createHarness,ROOT};
