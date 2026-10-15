'use strict';
// Original deterministic DOM regression tests. Geometry and native anchor scrolling are simulated.
// No browser rendering, downloads, product code, or external network calls are involved.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {JSDOM,VirtualConsole}=require('jsdom');
const input=path.resolve(process.argv[2]||path.join(__dirname,'../04-editorial-blog-and-doc-template.html'));
const journal=['intention','space','type','details'],docs=['docs-start','docs-theme','docs-reuse','docs-access'];
const results=[];
function fixture(options={}){
 let html=fs.readFileSync(input,'utf8');
 if(options.base)html=html.replace('<head>','<head><base href="https://source.invalid/files/">');
 const errors=[],observers=[],frames=[],scrolls=[],nativeAnchors=[];
 const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(html,{url:options.local?'file:///tmp/editorial.html':'https://preview.invalid/?document=book',runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
 const w=dom.window,d=w.document,$=s=>d.querySelector(s);
 let y=0,maxY=Infinity;
 const positions=Object.fromEntries([...journal,...docs].map((id,i)=>[id,{top:500+(i%4)*300,height:260}]));
 Object.defineProperty(w,'scrollY',{get:()=>y});
 w.matchMedia=()=>({matches:false});
 w.requestAnimationFrame=fn=>{frames.push(fn);return frames.length;};
 w.cancelAnimationFrame=()=>{};
 if(!options.noObserver)w.IntersectionObserver=class{
  constructor(callback,settings){this.callback=callback;this.settings=settings;this.targets=[];observers.push(this);}
  observe(el){this.targets.push(el);}disconnect(){this.targets=[];}unobserve(el){this.targets=this.targets.filter(x=>x!==el);}
 };
 w.HTMLElement.prototype.getBoundingClientRect=function(){
  const p=positions[this.id];
  if(!p||this.closest('[hidden]')||(this.matches('.article-section')&&d.documentElement.classList.contains('searching')))return {x:0,y:0,top:0,bottom:0,left:0,right:0,width:0,height:0};
  return {x:0,y:p.top,top:p.top,bottom:p.top+p.height,left:0,right:600,width:600,height:p.height};
 };
 function moveTo(next){const delta=next-y;y=next;for(const p of Object.values(positions))p.top-=delta;}
 w.HTMLElement.prototype.scrollIntoView=function(settings){scrolls.push({id:this.id,settings});moveTo(Math.min(maxY,Math.max(0,y+this.getBoundingClientRect().top-110)));};
 w.scrollTo=({top})=>moveTo(top);
 if(options.historyDenied)w.history.replaceState=()=>{throw new w.DOMException('blocked','SecurityError');};
 for(const script of d.querySelectorAll('script'))w.eval(script.textContent);
 // Reproduce the browser's default anchor step after the template's bubbling listener.
 d.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const canceled=e.defaultPrevented;e.preventDefault();if(canceled||e.button!==0||e.metaKey||e.ctrlKey||e.altKey||e.shiftKey)return;const id=a.dataset.section;if(!id)return;nativeAnchors.push(id);d.getElementById(id).scrollIntoView({behavior:'auto',block:'start'});try{w.history.pushState(null,'',a.href);}catch{}});
 return {w,d,$,errors,observers,positions,scrolls,nativeAnchors,
  place(ids,tops,heights=[]){ids.forEach((id,i)=>positions[id]={top:tops[i],height:heights[i]??260});},
  emit(entries){for(const o of observers)o.callback(entries.map(([id,isIntersecting=true])=>({target:d.getElementById(id),isIntersecting,boundingClientRect:d.getElementById(id).getBoundingClientRect()})),o);},
  flush(){let count=0;while(frames.length){assert.ok(++count<30,'animation-frame runaway');const batch=frames.splice(0);for(const fn of batch)fn(16*count);}},
  scrollTo(next){moveTo(next);w.dispatchEvent(new w.Event('scroll'));},
  notifyScroll(){w.dispatchEvent(new w.Event('scroll'));},
  resize(){w.dispatchEvent(new w.Event('resize'));},
  setMaxY(next){maxY=next;},
  current(){const all=[...d.querySelectorAll('.toc a[aria-current]')];assert.ok(all.length<=1,'at most one current link');if(all[0])assert.equal(all[0].getAttribute('aria-current'),'location');return all[0]?.dataset.section??null;},
  click(id,modifiers={}){$(id).dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true,button:0,...modifiers}));},
  search(value){$('#doc-search').value=value;$('#doc-search').dispatchEvent(new w.Event('input',{bubbles:true}));},
  close(){assert.deepEqual(errors,[],'no script/runtime errors');w.close();}
 };
}
function test(name,fn,options={}){let h;try{h=fixture(options);fn(h);h.close();h=null;results.push({name,result:'pass'});console.log('PASS '+name);}catch(e){results.push({name,result:'fail',error:e.message});console.log('FAIL '+name+': '+e.message);}finally{h?.w.close();}}
function docsAt(h,tops){h.place(docs,tops);h.click('#docs-tab');}

test('initial directory identifies the first journal section',h=>assert.equal(h.current(),'intention'));
test('forward IO order chooses the top reading section, not the final entry',h=>{docsAt(h,[-100,110,300,600]);h.emit([['docs-theme'],['docs-reuse']]);assert.equal(h.current(),'docs-theme');});
test('reversed IO order produces the same current section',h=>{docsAt(h,[-100,110,300,600]);h.emit([['docs-reuse'],['docs-theme']]);assert.equal(h.current(),'docs-theme');});
test('single-entry IO batch considers all current sections',h=>{docsAt(h,[-100,110,300,600]);h.emit([['docs-reuse']]);assert.equal(h.current(),'docs-theme');});
test('leave-only entry recomputes selection',h=>{docsAt(h,[-400,-170,110,400]);h.emit([['docs-reuse']]);assert.equal(h.current(),'docs-reuse');h.place(docs,[-100,110,350,650]);h.emit([['docs-reuse',false]]);assert.equal(h.current(),'docs-theme');});
test('expired entry snapshot cannot overwrite live geometry',h=>{docsAt(h,[-500,-250,110,400]);h.emit([['docs-theme']]);assert.equal(h.current(),'docs-reuse');});
test('hidden journal entries cannot clear the docs current section',h=>{docsAt(h,[-100,110,350,650]);h.emit([['docs-theme']]);h.emit([['type'],['details',false]]);assert.equal(h.current(),'docs-theme');});
test('switching modes sets a current section without awaiting IO',h=>{docsAt(h,[-100,110,350,650]);assert.equal(h.current(),'docs-theme');h.place(journal,[-800,-350,110,600]);h.click('#journal-tab');assert.equal(h.current(),'type');h.emit([['docs-access']]);assert.equal(h.current(),'type');});
test('scrolling across the reading line updates within an unchanged IO intersection',h=>{docsAt(h,[-300,100,340,640]);h.emit([['docs-theme']]);h.scrollTo(260);assert.equal(h.current(),'docs-reuse');h.scrollTo(0);assert.equal(h.current(),'docs-theme');});
test('gap between sections keeps the preceding heading until the next reaches the reading line',h=>{docsAt(h,[-400,-150,112,500]);h.notifyScroll();assert.equal(h.current(),'docs-theme');h.scrollTo(2);assert.equal(h.current(),'docs-reuse');});
test('reading-line tie is stable in document order',h=>{docsAt(h,[-200,110,110,500]);h.emit([['docs-reuse'],['docs-theme']]);assert.equal(h.current(),'docs-reuse');});
test('above-content and below-content boundaries choose first and last sections',h=>{docsAt(h,[400,700,1000,1300]);h.notifyScroll();assert.equal(h.current(),'docs-start');h.place(docs,[-1100,-800,-500,-200]);h.notifyScroll();assert.equal(h.current(),'docs-access');});
test('search hides current marker and ignores visibility callbacks',h=>{docsAt(h,[-100,110,350,650]);h.search('主题');assert.equal(h.current(),null);h.emit([['docs-start'],['docs-theme',false]]);assert.equal(h.current(),null);h.search('');assert.equal(h.current(),'docs-theme');});
test('Escape clears search and restores the visible reading section',h=>{docsAt(h,[-100,110,350,650]);h.search('主题');h.$('#doc-search').dispatchEvent(new h.w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));assert.equal(h.$('#search-results').hidden,true);assert.equal(h.current(),'docs-theme');});
for(const [base,local] of [[false,false],[true,false],[false,true]])test(`search result keeps focus, URL, mode and current together base=${base} file=${local}`,h=>{h.place(docs,[500,800,1100,1400]);h.search('主题');h.click('.search-result');assert.equal(h.d.activeElement.id,'docs-theme');if(!local)assert.equal(h.w.location.hash,'#docs-theme');assert.equal(h.$('#docs-content').hidden,false);assert.equal(h.$('#search-results').hidden,true);assert.equal(h.current(),'docs-theme');h.emit([['docs-theme'],['docs-reuse']]);h.flush();h.emit([['docs-reuse'],['intention',false]]);assert.equal(h.current(),'docs-theme');h.notifyScroll();assert.equal(h.current(),'docs-theme');},{base,local});
test('history denial still locates, focuses and marks search result',h=>{h.search('主题');h.click('.search-result');h.flush();h.emit([['docs-reuse']]);assert.equal(h.d.activeElement.id,'docs-theme');assert.equal(h.current(),'docs-theme');},{historyDenied:true});
test('native TOC click wins over queued IO before and after anchor scroll',h=>{docsAt(h,[500,800,1100,1400]);h.click('.toc a[data-section="docs-theme"]');assert.equal(h.current(),'docs-theme');h.emit([['docs-start'],['docs-reuse']]);assert.equal(h.current(),'docs-theme');h.flush();h.emit([['docs-reuse']]);assert.equal(h.current(),'docs-theme');assert.deepEqual(h.nativeAnchors,['docs-theme']);assert.equal(h.w.location.hash,'#docs-theme');});
test('page-bottom click remains current when target cannot align to the reading line',h=>{docsAt(h,[0,220,440,660]);h.setMaxY(100);h.click('.toc a[data-section="docs-access"]');h.flush();h.emit([['docs-theme'],['docs-reuse']]);assert.equal(h.positions['docs-access'].top,560);assert.equal(h.current(),'docs-access');h.notifyScroll();assert.equal(h.current(),'docs-access');h.scrollTo(80);assert.equal(h.current(),'docs-start');});
test('manual scrolling releases search navigation preference',h=>{h.search('主题');h.click('.search-result');h.flush();h.scrollTo(h.w.scrollY+310);assert.equal(h.current(),'docs-reuse');});
test('repeated clicks retain only the newest navigation frame',h=>{docsAt(h,[0,220,440,660]);h.click('.toc a[data-section="docs-theme"]');h.click('.toc a[data-section="docs-access"]');h.flush();h.emit([['docs-theme']]);assert.equal(h.current(),'docs-access');});
test('mode switch invalidates a pending navigation frame',h=>{docsAt(h,[0,220,440,660]);h.click('.toc a[data-section="docs-theme"]');h.place(journal,[500,800,1100,1400]);h.click('#journal-tab');h.flush();h.emit([['docs-theme']]);assert.equal(h.current(),'intention');});
test('search invalidates a pending navigation frame',h=>{docsAt(h,[0,220,440,660]);h.click('.toc a[data-section="docs-theme"]');h.search('主题');h.flush();h.emit([['docs-theme']]);assert.equal(h.current(),null);});
test('modified TOC clicks do not change current section in this page',h=>{docsAt(h,[-100,110,350,650]);h.emit([['docs-theme']]);for(const modifiers of [{ctrlKey:true},{metaKey:true},{shiftKey:true},{altKey:true},{button:1}]){h.click('.toc a[data-section="docs-access"]',modifiers);assert.equal(h.current(),'docs-theme');}assert.deepEqual(h.nativeAnchors,[]);});
test('cancelled TOC click does not change current section',h=>{docsAt(h,[-100,110,350,650]);h.emit([['docs-theme']]);h.$('.toc a[data-section="docs-access"]').addEventListener('click',e=>e.preventDefault());h.click('.toc a[data-section="docs-access"]');assert.equal(h.current(),'docs-theme');});
test('resize clears navigation preference and recomputes current geometry',h=>{docsAt(h,[0,220,440,660]);h.click('.toc a[data-section="docs-access"]');h.flush();h.place(docs,[-100,110,350,650]);h.resize();assert.equal(h.current(),'docs-theme');});
test('reading-mode layout change clears navigation preference',h=>{docsAt(h,[0,220,440,660]);h.click('.toc a[data-section="docs-access"]');h.flush();h.place(docs,[-100,110,350,650]);h.click('#read-mode');assert.equal(h.current(),'docs-theme');assert.equal(h.$('#read-mode').getAttribute('aria-pressed'),'true');});
test('scroll tracking works when IntersectionObserver is unavailable',h=>{docsAt(h,[-100,110,350,650]);assert.equal(h.current(),'docs-theme');h.scrollTo(250);assert.equal(h.current(),'docs-reuse');},{noObserver:true});
test('back to top releases current navigation target on scroll',h=>{h.click('.toc a[data-section="details"]');h.flush();assert.equal(h.current(),'details');h.click('#back-top');h.notifyScroll();assert.equal(h.current(),'intention');assert.equal(h.d.activeElement.id,'main');});
test('back to top clears navigation preference even when scroll position does not change',h=>{h.place(journal,[50,250,450,650]);h.setMaxY(0);h.click('.toc a[data-section="details"]');h.flush();assert.equal(h.current(),'details');h.click('#back-top');assert.equal(h.current(),'intention');});
const report={source:input,sha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),method:'Original deterministic jsdom tests with simulated section geometry, IntersectionObserver callbacks, requestAnimationFrame, and native anchor scrolling. No real rendering or browser claim.',summary:{total:results.length,passed:results.filter(r=>r.result==='pass').length,failed:results.filter(r=>r.result==='fail').length},results};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.summary));process.exitCode=report.summary.failed?1:0;
