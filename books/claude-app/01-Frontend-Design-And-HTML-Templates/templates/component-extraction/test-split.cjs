// 原页与拆分副本加载同样的确定性业务状态。不会访问网络或运行浏览器。
const assert = require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), os=require('node:os');
const {JSDOM}=require('jsdom'); const {split}=require('./split-page.cjs');
const source=path.resolve(process.argv[2]||path.join(__dirname,'..'));
const work=fs.mkdtempSync(path.join(os.tmpdir(),'atelier-extraction-')), output=path.join(work,'split');
try {
 split(source,output);
 const original=fs.readFileSync(path.join(source,'02-chat-workspace-template.html'),'utf8');
 const external=fs.readFileSync(path.join(output,'index.html'),'utf8');
 const script=original.match(/<script>([\s\S]*?)<\/script>/)[1];assert.equal(script,fs.readFileSync(path.join(output,'page.js'),'utf8'));
 const inlineCSS=original.match(/<style>([\s\S]*?)<\/style>/)[1].trim();
 const css=['styles/claude-tokens.css','styles/claude-reset-and-base.css','page.css'].map(f=>fs.readFileSync(path.join(output,f),'utf8').trim()).join('\n');
 assert.equal(inlineCSS.replace(/\s+/g,' '),css.replace(/\s+/g,' '));
 function run(html,splitPage,fileURL) {
  const dom=new JSDOM(html,{url:fileURL?'file:///demo/index.html':'https://example.invalid/index.html',runScripts:'outside-only'}),w=dom.window,d=w.document;
  const store=new Map(),timers=new Map();let seq=0;w.setTimeout=fn=>{timers.set(++seq,fn);return seq;};w.clearTimeout=id=>timers.delete(id);
  w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});w.HTMLElement.prototype.scrollIntoView=function(){};
  w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'));};
  Object.defineProperty(w,'localStorage',{get(){if(fileURL)throw Error('denied');return{getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v)};}});
  const scripts=[...d.querySelectorAll('script')];assert.equal(scripts.length,1);
  if(splitPage){assert.equal(scripts[0].defer,true);assert.equal(scripts[0].getAttribute('src'),'page.js');assert.deepEqual([...d.querySelectorAll('link[rel="stylesheet"]')].map(e=>e.getAttribute('href')),['styles/claude-tokens.css','styles/claude-reset-and-base.css','page.css']);}
  w.eval(splitPage?fs.readFileSync(path.join(output,scripts[0].getAttribute('src')),'utf8'):scripts[0].textContent);
  const $=s=>d.querySelector(s),event=(el,type)=>el.dispatchEvent(new w.Event(type,{bubbles:true,cancelable:true}));
  $('#theme-toggle').click();$('#palette').value='sage';event($('#palette'),'change');
  const beforeIME=d.querySelectorAll('.message.user').length;const x=$('#chat-input');x.value='保留输入';event(x,'input');event(x,'compositionstart');event($('#chat-form'),'submit');assert.equal(d.querySelectorAll('.message.user').length,beforeIME);event(x,'compositionend');event($('#chat-form'),'submit');$('#send-chat').click();assert.equal(x.value,'保留输入');
  event($('#chat-form'),'submit');for(const [id,fn] of [...timers]){timers.delete(id);fn();}
  assert.match($('#chat-status').textContent,/示例已完成/);
  const result={theme:d.documentElement.dataset.theme,palette:d.documentElement.dataset.palette,messages:$('#messages').textContent,status:$('#chat-status').textContent,draft:x.value,storage:[...store]};dom.window.close();return result;
 }
 for(const fileURL of [false,true])assert.deepEqual(run(original,false,fileURL),run(external,true,fileURL));
 console.log(JSON.stringify({passed:true,checks:['script unchanged','CSS content/order preserved','HTTPS simulated state parity','file URL with denied storage simulated state parity'],realBrowser:false}));
} finally { fs.rmSync(work,{recursive:true,force:true}); }
