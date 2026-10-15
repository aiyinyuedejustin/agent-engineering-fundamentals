const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {JSDOM} = require('jsdom');
function harness() {
  const dom = new JSDOM('<html data-theme="host"><body><button id="outside">host</button><section></section><section></section></body></html>',{runScripts:'outside-only',url:'https://example.invalid'});
  const w = dom.window, d = w.document; let next = 0;
  const pending = new Map(), callbacks = [], mediaListeners = new Set();
  w.setTimeout = fn => { callbacks.push(fn); pending.set(++next,fn); return next; };
  w.clearTimeout = id => pending.delete(id);
  w.matchMedia = () => ({matches:false,addEventListener:(_,fn)=>mediaListeners.add(fn),removeEventListener:(_,fn)=>mediaListeners.delete(fn)});
  w.eval(fs.readFileSync(path.join(__dirname,'scoped-chat.js'),'utf8'));
  const roots = [...d.querySelectorAll('section')];
  const mount = (i,options={}) => w.AtelierScopedChat.mount(roots[i],{namespace:'test:'+i,...options});
  const event = (el,type,options={}) => el.dispatchEvent(new w.Event(type,{bubbles:true,cancelable:true,...options}));
  const key = (el,k,options={}) => { const e = new w.KeyboardEvent('keydown',{key:k,bubbles:true,cancelable:true,...options}); el.dispatchEvent(e); return e; };
  const input = (i,value) => { const el=roots[i].querySelector('textarea'); el.value=value; event(el,'input'); return el; };
  const send = i => event(roots[i].querySelector('form'),'submit');
  const tick = () => { for (const [id,fn] of [...pending]) { pending.delete(id); fn(); } };
  return {w,d,roots,mount,event,key,input,send,tick,pending,callbacks,mediaListeners,close:()=>dom.window.close()};
}
function check(name,fn) { test(name,() => {const h=harness();try { fn(h); } finally {h.close();}}); }
check('两个实例的 ID、label 与 aria-controls 都只指向自己的元素',h=>{
 h.mount(0);h.mount(1);const ids=[...h.d.querySelectorAll('[id]')].map(x=>x.id);assert.equal(ids.length,new Set(ids).size);
 for(const root of h.roots){for(const el of root.querySelectorAll('[for],[aria-controls]'))assert.ok(root.contains(h.d.getElementById(el.getAttribute('for')||el.getAttribute('aria-controls'))));}
});
check('theme/palette 只改各自 root，宿主保持原值',h=>{
 h.mount(0);h.mount(1);h.roots[0].querySelector('[data-action="theme"]').click();assert.equal(h.roots[0].dataset.theme,'dark');assert.equal(h.roots[1].dataset.theme,'light');assert.equal(h.d.documentElement.dataset.theme,'host');
 const p=h.roots[0].querySelector('select');p.value='sage';h.event(p,'change');assert.equal(h.roots[1].dataset.palette,'paper');
});
check('Ctrl/Meta+K 仅属于当前焦点实例；宿主与 defaultPrevented 不接管',h=>{
 h.mount(0);h.mount(1);h.input(0,'left');const right=h.input(1,'right');right.focus();assert.equal(h.key(right,'k',{ctrlKey:true}).defaultPrevented,true);assert.equal(h.roots[0].querySelector('textarea').value,'left');assert.equal(right.value,'');
 const outside=h.d.getElementById('outside');outside.focus();assert.equal(h.key(outside,'k',{metaKey:true}).defaultPrevented,false);
 const left=h.roots[0].querySelector('textarea');left.focus();left.addEventListener('keydown',e=>e.preventDefault(),{once:true});h.key(left,'k',{metaKey:true});assert.equal(left.value,'left');
});
check('独立 namespace 恢复各自草稿，故意共用时后挂载读取同一键',h=>{
 const a=h.mount(0),b=h.mount(1);h.input(0,'左');h.input(1,'右');a.unmount();h.mount(0);assert.equal(h.roots[0].querySelector('textarea').value,'左');b.unmount();h.mount(1,{namespace:'test:0'});assert.equal(h.roots[1].querySelector('textarea').value,'左');
});
check('组合输入、isComposing、229 与修饰 Enter 不提交',h=>{
 h.mount(0);const x=h.input(0,'中文');x.focus();h.event(x,'compositionstart');h.key(x,'Enter');h.send(0);h.key(x,'k',{ctrlKey:true});assert.equal(x.value,'中文');h.event(x,'compositionend');
 for(const options of [{isComposing:true},{keyCode:229},{shiftKey:true},{ctrlKey:true},{metaKey:true},{altKey:true}])h.key(x,'Enter',options);
 assert.equal(h.pending.size,0);h.key(x,'Enter');assert.equal(h.pending.size,1);
});
check('停止恢复原草稿；已写下一条时优先保留下一条',h=>{
 h.mount(0);h.input(0,'第一条');h.send(0);h.send(0);assert.equal(h.roots[0].querySelector('textarea').value,'第一条');h.tick();assert.equal(h.roots[0].querySelectorAll('[data-role="assistant"]').length,0);
 h.send(0);h.input(0,'下一条');h.send(0);assert.equal(h.roots[0].querySelector('textarea').value,'下一条');
});
check('新对话取消旧生成，即使旧回调已经排队也不写入',h=>{
 h.mount(0);h.input(0,'old');h.send(0);const stale=h.callbacks.at(-1);h.roots[0].querySelector('[data-action="new"]').click();stale();assert.equal(h.roots[0].querySelector('[data-role="messages"]').childNodes.length,0);
});
check('卸载移除 timer、媒体回调、旧监听；同 root 新实例不受旧回调影响',h=>{
 const a=h.mount(0);const oldInput=h.input(0,'old');const oldButton=h.roots[0].querySelector('[data-action="theme"]');h.send(0);const stale=h.callbacks.at(-1);a.unmount();a.unmount();assert.equal(h.pending.size,0);assert.equal(h.mediaListeners.size,0);assert.equal(h.roots[0].childNodes.length,0);assert.equal(h.roots[0].hasAttribute('data-ui'),false);
 h.mount(0);const before=h.roots[0].innerHTML;stale();oldButton.click();h.key(oldInput,'Enter');assert.equal(h.roots[0].innerHTML,before);assert.equal(h.roots[0].dataset.theme,'light');
});
check('系统主题只影响未手动选择实例，卸载撤回订阅',h=>{
 const a=h.mount(0);h.mount(1);h.roots[1].querySelector('[data-action="theme"]').click();for(const fn of h.mediaListeners)fn({matches:false});assert.equal(h.roots[1].dataset.theme,'dark');for(const fn of h.mediaListeners)fn({matches:true});assert.equal(h.roots[0].dataset.theme,'dark');a.unmount();assert.equal(h.mediaListeners.size,1);
});
check('存储 getter 拒绝或 JSON 类型损坏时仍可输入和完成',h=>{
 Object.defineProperty(h.w,'localStorage',{get(){throw Error('denied');}});h.mount(0);h.input(0,'<img src=x>');h.send(0);h.tick();assert.equal(h.roots[0].querySelectorAll('img').length,0);assert.equal(h.roots[0].querySelectorAll('[data-role="assistant"]').length,1);
 h.mount(1,{storage:{getItem:()=>'{"bad":true}',setItem(){throw Error('quota');}}});assert.equal(h.roots[1].dataset.theme,'light');assert.equal(h.roots[1].querySelector('textarea').value,'');
});
check('拒绝重复挂载；卸载还原宿主原有根属性',h=>{
 h.roots[0].dataset.theme='dark';const a=h.mount(0);assert.throws(()=>h.mount(0));a.unmount();assert.equal(h.roots[0].dataset.theme,'dark');assert.throws(()=>h.w.AtelierScopedChat.mount(h.roots[0]));
});
