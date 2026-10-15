import test from 'node:test';
import assert from 'node:assert/strict';
import {mapDisplayPoint,mapWindowPoint,apply,compose,invert,rectBounds,pdfViewport,canvasTransform} from './geometry.mjs';
import {rms,pcm16le,PcmFrameAssembler,EnvelopeHistory,PlaybackLedger,VoiceEpoch} from './audio-state.mjs';
import {sameEditTarget,SnapshotAuthority,ShortcutLease,connectorOwner} from './native-state.mjs';
const frame={captureId:'capture-A',displayId:'left',imageWidth:500,imageHeight:300,
  frameWidth:1000,frameHeight:600,displayWidth:2000,displayHeight:1200,originX:-2000,originY:-100};
const nearly=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
test('display transform uses full frame, negative origin and independent axes',()=>{
  assert.deepEqual(mapDisplayPoint([500,300],frame,'capture-A'),{x:-1000,y:500,displayId:'left'});
});
test('right/bottom edge are clamped to last display coordinate',()=>{
  assert.deepEqual(mapDisplayPoint([1000,600],frame,'capture-A'),{x:-1,y:1099,displayId:'left'});
});
test('0..100 is an explicit mode; never an inferred 0..1 space',()=>{
  assert.deepEqual(mapDisplayPoint([50,50],frame,'capture-A','percent-0-100'),{x:-1000,y:500,displayId:'left'});
  assert.equal(mapDisplayPoint([1,1],frame,'capture-A','percent-0-100').x,-1980);
  assert.throws(()=>mapDisplayPoint([50,50],frame,'capture-A','normalized'));
});
test('reject stale screenshots and invalid frame geometry',()=>{
  assert.throws(()=>mapDisplayPoint([1,1],frame,'capture-old'));
  assert.throws(()=>mapDisplayPoint([1,1],{...frame,frameWidth:0},'capture-A'));
  assert.throws(()=>mapDisplayPoint([NaN,1],frame,'capture-A'));
  assert.throws(()=>mapDisplayPoint([-1,1],frame,'capture-A'));
  assert.throws(()=>mapDisplayPoint([1001,1],frame,'capture-A'));
});
test('image size is a fallback only when full frame is absent',()=>{
  assert.equal(mapDisplayPoint([250,150],{...frame,frameWidth:undefined,frameHeight:undefined},'capture-A').x,-1000);
});
test('window mapping yields local coordinates and never adds desktop origin',()=>{
  assert.deepEqual(mapWindowPoint([500,300],{...frame,windowId:42,windowWidth:800,windowHeight:480},'capture-A'),{x:400,y:240,windowId:42});
});
test('window teaching policy rejects out-of-bounds points',()=>{
  assert.throws(()=>mapWindowPoint([1001,0],{...frame,windowId:42,windowWidth:800,windowHeight:480},'capture-A'));
});
test('affine composition order is inner then outer',()=>{
  const scale=[2,0,0,3,0,0],pan=[1,0,0,1,10,20];
  assert.deepEqual(apply(compose(pan,scale),[4,5]),[18,35]);
  assert.deepEqual(apply(compose(scale,pan),[4,5]),[28,75]);
});
test('PDF bottom-left space maps to CSS top-left at rotation zero',()=>{
  const v=pdfViewport({viewBox:[0,0,612,792],zoom:2});
  assert.deepEqual(apply(v.matrix,[0,792]),[0,0]);
  assert.deepEqual(apply(v.matrix,[612,0]),[1224,1584]);
});
test('PDF rotated nonzero crop box and userUnit are respected',()=>{
  const v=pdfViewport({viewBox:[10,20,210,120],rotation:90,zoom:2,userUnit:1.5,offsetX:7,offsetY:11});
  assert.deepEqual([v.width,v.height],[300,600]);
  assert.deepEqual(rectBounds([10,20,210,120],v.matrix),[7,11,307,611]);
});
test('PDF rectangle fixture preserves both flip and scale',()=>{
  const v=pdfViewport({viewBox:[0,0,600,800],zoom:1.5});
  assert.deepEqual(rectBounds([100,600,200,700],v.matrix),[150,150,300,300]);
});
test('DPR transforms backing-store pixels without changing CSS pointer space',()=>{
  const v=pdfViewport({viewBox:[0,0,600,800]});
  const css=apply(v.matrix,[100,700]),canvas=apply(canvasTransform(v.matrix,2),[100,700]);
  assert.deepEqual(css,[100,100]);assert.deepEqual(canvas,[200,200]);
  assert.deepEqual(apply(invert(v.matrix),css),[100,700]);
});
test('PDF transform round-trips 360 generated cases including negative crop origins',()=>{
  for(const rotation of [0,90,180,270,-90,450])for(let i=1;i<=60;i++){
    const v=pdfViewport({viewBox:[-30,10,170,310],zoom:i/17,userUnit:1.25,rotation,offsetX:-7,offsetY:9});
    const p=[-30+i*2,10+i*3],q=apply(invert(v.matrix),apply(v.matrix,p));
    nearly(q[0],p[0]);nearly(q[1],p[1]);
  }
});
test('tiny uniform scaling is invertible despite a small determinant',()=>{
  const m=[1e-7,0,0,1e-7,0,0];
  const q=apply(invert(m),apply(m,[12,34]));nearly(q[0],12);nearly(q[1],34);
});
test('all four corners determine rectangle bounds for a shear',()=>{
  assert.deepEqual(rectBounds([0,0,2,3],[1,1,-1,1,0,0]),[-3,0,2,5]);
});
test('reject singular and malformed PDF transforms',()=>{
  assert.throws(()=>invert([1,1,1,1,0,0]));
  assert.throws(()=>pdfViewport({viewBox:[0,0,0,100]}));
  assert.throws(()=>pdfViewport({viewBox:[0,0,10,10],rotation:45}));
  assert.throws(()=>canvasTransform([1,0,0,1,0,0],0));
});
test('RMS is amplitude energy, not speech classification',()=>{
  assert.equal(rms([1,-1,1,-1]),1);assert.equal(rms([0,0]),0);assert.equal(rms([]),0);
  assert.throws(()=>rms([Infinity]));
});
test('PCM16 explicitly clips and writes little endian',()=>{
  assert.deepEqual([...pcm16le([-2,-1,0,1,2])],[0,128,0,128,0,0,255,127,255,127]);
});
test('16kHz times 20ms is exactly 320 samples',()=>{
  const a=new PcmFrameAssembler(16000,20);assert.equal(a.samplesPerFrame,320);
  const frames=a.push(new Float32Array(640));assert.equal(frames.length,2);assert.equal(frames[1].startMs,20);
});
test('framing is invariant under arbitrary incoming chunk boundaries',()=>{
  const data=Float32Array.from({length:1007},(_,i)=>i/1007);
  const a=new PcmFrameAssembler(16000,20),b=new PcmFrameAssembler(16000,20);
  const whole=a.push(data),parts=[];
  for(let i=0;i<data.length;i+=137)parts.push(...b.push(data.slice(i,i+137)));
  assert.deepEqual(parts,whole);assert.deepEqual(b.finish(),a.finish());assert.equal(b.pendingSamples,0);
});
test('invalid samples do not partially mutate frame assembly',()=>{
  const a=new PcmFrameAssembler(8000,10);assert.throws(()=>a.push([1,NaN]));assert.equal(a.pendingSamples,0);
  assert.throws(()=>new PcmFrameAssembler(44100,1));
});
test('envelope keeps a bounded history and uses elapsed time for smoothing',()=>{
  const a=new EnvelopeHistory({capacity:2}),b=new EnvelopeHistory({capacity:2});
  const x=a.sample([1,1],100);b.sample([1,1],50);const y=b.sample([1,1],50);nearly(x,y);
  b.sample([0,0],50);assert.equal(b.values.length,2);assert.ok(b.values[1]<b.values[0]);
});
test('initial silence and normal completion are not counted as underruns',()=>{
  const p=new PlaybackLedger();p.render(128);assert.equal(p.underruns,0);
  p.enqueue(128);p.render(128);p.render(128);p.finishTurn();p.enqueue(128);p.render(128);assert.equal(p.underruns,0);
});
test('mid-turn starvation counts once only when audio resumes',()=>{
  const p=new PlaybackLedger();p.enqueue(128);p.render(128);p.render(128);p.render(128);
  p.enqueue(128);p.render(128);assert.equal(p.underruns,1);assert.equal(p.played,256);
});
test('played duration excludes zero fill and queued-but-unheard samples',()=>{
  const p=new PlaybackLedger(16000);p.enqueue(400);p.render(160);assert.equal(p.playedMs,10);
  p.interrupt();assert.equal(p.queued,0);assert.equal(p.playedMs,10);p.render(160);assert.equal(p.playedMs,10);
});
test('late async work cannot revive stopped voice state',()=>{
  const v=new VoiceEpoch(),epoch=v.start();v.event(epoch,'ready');v.stop();
  assert.equal(v.event(epoch,'audio',320),false);assert.equal(v.state,'idle');
});
test('interrupt cuts old reply epoch but only requests remote interruption',()=>{
  const v=new VoiceEpoch(),epoch=v.start();v.event(epoch,'audio',320);
  const effect=v.interrupt();assert.equal(effect.effect,'request-server-interrupt');
  assert.equal(v.event(epoch,'audio',320),false);assert.equal(v.replySamples,0);
});
const before={windowId:9,processId:88,elementId:'field-A',selection:'hello'};
test('edit target identity requires the same window, process, element and selection',()=>{
  const after={...before,verdict:'ready',editable:true};assert.equal(sameEditTarget(before,after),true);
  for(const patch of [{windowId:10},{processId:89},{elementId:'field-B'},{selection:'changed'},{editable:false},{verdict:'secure'}])
    assert.equal(sameEditTarget(before,{...after,...patch}),false);
});
test('empty element identities are never treated as stable targets',()=>{
  assert.equal(sameEditTarget({...before,elementId:''},{...before,elementId:'',verdict:'ready',editable:true}),false);
});
test('snapshot indices are scoped to session/window/capture/grant generation',()=>{
  const store=new SnapshotAuthority();const request={sessionId:'A',appId:'editor',windowId:9,captureId:'c1',grantVersion:3,index:0,now:10};
  store.save({...request,expiresAt:100,elements:[{role:'button',label:'Untrusted text'}]});
  assert.equal(store.resolve(request).role,'button');
  for(const patch of [{sessionId:'B'},{windowId:10},{captureId:'c2'},{grantVersion:4},{now:100},{index:1}])
    assert.throws(()=>store.resolve({...request,...patch}));
});
function fakeRegistry(){const held=new Set(),blocked=new Set();return {held,blocked,register(key){if(blocked.has(key)||held.has(key))return false;held.add(key);return true;},unregister(key){held.delete(key);}};}
test('shortcut replacement restores a working prior key after conflict',()=>{
  const r=fakeRegistry(),s=new ShortcutLease(r,()=>{});s.replace('Ctrl+K');r.blocked.add('Ctrl+J');
  assert.deepEqual(s.replace('Ctrl+J'),{ok:false,active:'Ctrl+K',rollback:'restored'});
});
test('shortcut rollback failure is a first-class outcome',()=>{
  const r=fakeRegistry(),s=new ShortcutLease(r,()=>{});s.replace('Ctrl+K');r.blocked.add('Ctrl+K');r.blocked.add('Ctrl+J');
  assert.deepEqual(s.replace('Ctrl+J'),{ok:false,active:null,rollback:'failed'});
});
test('shortcut cleanup does not unregister another owner',()=>{
  const r=fakeRegistry(),s=new ShortcutLease(r,()=>{});r.register('Other');s.replace('Own');s.close();assert.deepEqual([...r.held],['Other']);
});
test('connector owner is explicit and cannot be inferred from plugin or client name',()=>{
  assert.equal(connectorOwner({kind:'account-remote'}).connectionOrigin,'provider-cloud');
  assert.equal(connectorOwner({kind:'desktop-local'}).connectionOrigin,'desktop-host');
  assert.throws(()=>connectorOwner({client:'desktop',plugin:'calendar'}));
});
