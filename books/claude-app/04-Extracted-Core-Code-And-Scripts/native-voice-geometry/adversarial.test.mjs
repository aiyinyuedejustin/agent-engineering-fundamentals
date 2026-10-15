import test from 'node:test';
import assert from 'node:assert/strict';
import {mapDisplayPoint,mapWindowPoint,apply,invert,rectBounds,pdfViewport,canvasTransform} from './geometry.mjs';
import {rms,pcm16le,PcmFrameAssembler,PlaybackLedger,VoiceEpoch} from './audio-state.mjs';
import {SnapshotAuthority} from './native-state.mjs';
const frame={captureId:'c',displayId:'left',frameWidth:100,frameHeight:100,displayWidth:1000,displayHeight:1000,originX:-1000,originY:-2000};
const close=(x,y)=>assert.ok(Math.abs(x-y)<1e-8,`${x} != ${y}`);

test('stress: sparse points are rejected instead of producing NaN display coordinates',()=>{
  assert.throws(()=>mapDisplayPoint(new Array(2),frame,'c'),TypeError);
});
test('stress: sparse affine matrices are rejected instead of producing NaN output',()=>{
  assert.throws(()=>apply(new Array(6),[1,2]),TypeError);
});
test('stress: sparse rectangles are rejected rather than producing NaN bounds',()=>{
  assert.throws(()=>rectBounds(new Array(4),[1,0,0,1,0,0]),TypeError);
});
test('stress: large representable display ratios do not overflow intermediate multiplication',()=>{
  const f={...frame,frameWidth:1e200,frameHeight:1e200,displayWidth:1e200,displayHeight:1e200,originX:-1e200,originY:-1e200};
  assert.deepEqual(mapDisplayPoint([5e199,5e199],f,'c'),{x:-5e199,y:-5e199,displayId:'left'});
});
test('stress: large representable window ratios do not overflow intermediate multiplication',()=>{
  const f={...frame,frameWidth:1e200,frameHeight:1e200,windowWidth:1e200,windowHeight:1e200,windowId:1};
  assert.deepEqual(mapWindowPoint([5e199,5e199],f,'c'),{x:5e199,y:5e199,windowId:1});
});
test('stress: inverse rejects a finite determinant whose inverse cannot be represented',()=>{
  assert.throws(()=>invert([1e-309,0,0,1,0,0]),RangeError);
});
test('stress: positive PDF factors that underflow to zero cannot make a valid viewport',()=>{
  assert.throws(()=>pdfViewport({viewBox:[0,0,10,20],zoom:Number.MIN_VALUE,userUnit:.5}),RangeError);
});
test('stress: negative-origin display grids preserve axes and all four boundaries',()=>{
  for(const ox of [-2500,-1,0,500])for(const oy of [-2100,-1,0,700])for(let x=0;x<=100;x+=10)for(let y=0;y<=100;y+=10){
    const p=mapDisplayPoint([x,y],{...frame,originX:ox,originY:oy},'c');
    assert.equal(p.x,ox+Math.min(x*10,999));assert.equal(p.y,oy+Math.min(y*10,999));
  }
});
test('stress: PDF rotations match an independent quarter-turn formula, including negative crops',()=>{
  const [left,bottom,right,top]=[-100,-200,300,400],w=right-left,h=top-bottom;
  for(const rotation of [-720,-450,-360,-270,-180,-90,0,90,180,270,360,450,720])for(const unit of [.25,1,2])for(const zoom of [.5,1,3]){
    const s=unit*zoom,v=pdfViewport({viewBox:[left,bottom,right,top],rotation,userUnit:unit,zoom,offsetX:-17,offsetY:29});
    const turn=((rotation%360)+360)%360;
    for(let i=0;i<=10;i++){
      const x=left+w*i/10,y=bottom+h*(10-i)/10;const local={0:[x-left,top-y],90:[y-bottom,x-left],180:[right-x,y-bottom],270:[top-y,right-x]}[turn];
      const out=apply(v.matrix,[x,y]);close(out[0],-17+s*local[0]);close(out[1],29+s*local[1]);
      const back=apply(invert(v.matrix),out);close(back[0],x);close(back[1],y);
      const backing=apply(canvasTransform(v.matrix,2),[x,y]);close(backing[0],out[0]*2);close(backing[1],out[1]*2);
    }
  }
});
test('stress: RMS of huge finite samples is finite when the mathematical result is representable',()=>{
  assert.equal(rms([1e308,-1e308]),1e308);
});
test('stress: sparse PCM samples are invalid rather than silently converted to zero',()=>{
  assert.throws(()=>pcm16le(new Array(2)),TypeError);
});
test('stress: frame format rejects an underflowed zero sample count',()=>{
  assert.throws(()=>new PcmFrameAssembler(1,Number.MIN_VALUE),RangeError);
});
test('stress: frame format rejects unsafe integer sample counts',()=>{
  assert.throws(()=>new PcmFrameAssembler(Number.MAX_SAFE_INTEGER+1,1000),RangeError);
});
test('stress: audio input is captured once before validation and assembly',()=>{
  let reads=0;const input=[];Object.defineProperty(input,0,{get(){reads++;return reads===1?.5:NaN;},enumerable:true});
  const a=new PcmFrameAssembler(1000,1);const [result]=a.push(input);
  assert.equal(reads,1);assert.deepEqual([...result.samples],[.5]);
});
test('stress: rejected late sample leaves previously buffered audio unchanged',()=>{
  const a=new PcmFrameAssembler(1000,3);a.push([.1]);assert.throws(()=>a.push([.2,NaN]));
  assert.equal(a.pendingSamples,1);const [frame]=a.push([.2,.3]);assert.equal(frame.startSample,0);assert.equal(frame.samples.length,3);
});
test('stress: enqueue rejects unsafe counts without changing sample accounting',()=>{
  const p=new PlaybackLedger();assert.throws(()=>p.enqueue(Number.MAX_SAFE_INTEGER+1),RangeError);assert.equal(p.queued,0);
});
test('stress: cumulative enqueue overflow is rejected atomically',()=>{
  const p=new PlaybackLedger();p.enqueue(Number.MAX_SAFE_INTEGER);assert.throws(()=>p.enqueue(1),RangeError);assert.equal(p.queued,Number.MAX_SAFE_INTEGER);
});
test('stress: cumulative played sample overflow is rejected atomically',()=>{
  const p=new PlaybackLedger();p.enqueue(Number.MAX_SAFE_INTEGER);p.render(Number.MAX_SAFE_INTEGER);p.enqueue(1);
  assert.throws(()=>p.render(1),RangeError);assert.equal(p.played,Number.MAX_SAFE_INTEGER);assert.equal(p.queued,1);
});
test('stress: voice sample count overflow is rejected without altering the accepted reply',()=>{
  const v=new VoiceEpoch(),epoch=v.start();v.event(epoch,'audio',Number.MAX_SAFE_INTEGER);
  assert.throws(()=>v.event(epoch,'audio',1),RangeError);assert.equal(v.replySamples,Number.MAX_SAFE_INTEGER);
});
test('stress: current epoch is independent of a stale error and audio after interrupt',()=>{
  const v=new VoiceEpoch(),old=v.start();v.event(old,'ready');const current=v.interrupt().epoch;
  assert.equal(v.event(old,'error'),false);assert.equal(v.event(old,'audio',1),false);assert.equal(v.state,'listening');
  assert.equal(v.event(current,'audio',1),true);v.stop();assert.equal(v.event(current,'audio',1),false);
});
const request={sessionId:'session',appId:'editor',windowId:9,captureId:'capture',grantVersion:3,index:0,now:10};
test('stress: missing window identity cannot alias a null window scope',()=>{
  const store=new SnapshotAuthority();assert.throws(()=>store.save({...request,windowId:undefined,expiresAt:100,elements:[{label:'synthetic'}]}),TypeError);
});
test('stress: non-finite window identity cannot collide through JSON key conversion',()=>{
  const store=new SnapshotAuthority();assert.throws(()=>store.save({...request,windowId:NaN,expiresAt:100,elements:[{label:'synthetic'}]}),TypeError);
});
test('stress: a snapshot without an explicit grant version is rejected',()=>{
  const store=new SnapshotAuthority();assert.throws(()=>store.save({...request,grantVersion:undefined,expiresAt:100,elements:[]}),TypeError);
});
test('stress: object scope IDs are rejected without invoking a custom toJSON alias',()=>{
  const store=new SnapshotAuthority();let called=0;const id={toJSON(){called++;return 'session';}};
  assert.throws(()=>store.save({...request,sessionId:id,expiresAt:100,elements:[]}),TypeError);assert.equal(called,0);
});
test('stress: snapshot content is isolated from mutation both before and after resolve',()=>{
  const store=new SnapshotAuthority(),elements=[{label:'original',nested:{value:1}}];store.save({...request,expiresAt:100,elements});
  elements[0].nested.value=2;const first=store.resolve(request);assert.equal(first.nested.value,1);first.nested.value=3;assert.equal(store.resolve(request).nested.value,1);
});
test('stress: replacing a capture revokes the prior snapshot even within the same window',()=>{
  const store=new SnapshotAuthority();store.save({...request,expiresAt:100,elements:[{label:'one'}]});store.save({...request,captureId:'new',expiresAt:100,elements:[{label:'two'}]});
  assert.throws(()=>store.resolve(request));assert.equal(store.resolve({...request,captureId:'new'}).label,'two');
});
test('stress: unequal display scales independently use x=2 and y=3',()=>{
  const f={...frame,frameWidth:500,frameHeight:300,displayWidth:1000,displayHeight:900,originX:-1000,originY:-900};
  assert.deepEqual(mapDisplayPoint([250,150],f,'c'),{x:-500,y:-450,displayId:'left'});
  assert.deepEqual(mapDisplayPoint([50,50],f,'c','percent-0-100'),{x:-500,y:-450,displayId:'left'});
});

test('numeric domain: condition-one subnormal determinant has an accurate inverse',()=>{
  for(const s of [2e-162,1e-160,1e-200,1e-300]){
    const m=[s,0,0,s,0,0];const back=apply(invert(m),apply(m,[1,-2]));close(back[0],1);close(back[1],-2);
  }
});
test('numeric domain: huge uniform scale has a representable inverse',()=>{
  const m=[1e200,0,0,1e200,0,0],back=apply(invert(m),apply(m,[1,-2]));close(back[0],1);close(back[1],-2);
});
test('numeric domain: separate row normalization preserves anisotropic diagonals',()=>{
  const m=[1e-200,0,0,1e200,0,0],back=apply(invert(m),apply(m,[2,3]));close(back[0],2);close(back[1],3);
});
test('numeric domain: tiny scaled shear and translation retain round trip',()=>{
  const s=2e-162,m=[2*s,s,-s,3*s,7*s,-11*s],back=apply(invert(m),apply(m,[3,5]));close(back[0],3);close(back[1],5);
});
test('numeric domain: singular rows and nonrepresentable inverse remain rejected',()=>{
  for(const m of [[0,0,0,1,0,0],[1,2,2,4,0,0],[1e-309,0,0,1,0,0]])assert.throws(()=>invert(m),RangeError);
});
test('numeric domain: finite Float32 extrema and subnormal samples are preserved',()=>{
  const a=new PcmFrameAssembler(1000,4),input=[3.4028234663852886e38,-3.4028234663852886e38,2**-149,-(2**-149)];
  assert.deepEqual([...a.push(input)[0].samples],input);
});
test('numeric domain: Float32 overflow rejects the complete batch atomically',()=>{
  const a=new PcmFrameAssembler(1000,2);a.push([.25]);
  assert.throws(()=>a.push([.5,1e39]),RangeError);assert.equal(a.pendingSamples,1);
  const first=a.push([.75])[0];assert.equal(first.sequence,0);assert.equal(first.startSample,0);assert.deepEqual([...first.samples],[.25,.75]);
});
test('numeric domain: either-sign Float32 overflow cannot contaminate a tail',()=>{
  for(const x of [1e39,-1e39]){
    const a=new PcmFrameAssembler(1000,3);a.push([.25]);assert.throws(()=>a.push([x]),RangeError);assert.deepEqual([...a.finish()],[.25]);
  }
});

test('numeric domain: fallback preserves extreme off-axis coefficients',()=>{
  const m=[1e308,1e308,1e-308,2e-308,0,0],inverse=invert(m);
  assert.ok(inverse.every(Number.isFinite));
  const back=apply(inverse,apply(m,[0,1]));close(back[0],0);close(back[1],1);
});
test('numeric domain: fallback preserves representable translation after cancellation',()=>{
  const inverse=invert([.5,.25,.25,.5,1e308,1e308]);
  assert.ok(inverse.every(Number.isFinite));assert.equal(inverse[4],-1.3333333333333333e308);assert.equal(inverse[5],-1.3333333333333333e308);
});
