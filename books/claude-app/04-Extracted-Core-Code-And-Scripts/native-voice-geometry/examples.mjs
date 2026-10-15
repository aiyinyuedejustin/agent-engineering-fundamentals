import {mapDisplayPoint,mapWindowPoint,pdfViewport,rectBounds,apply,canvasTransform} from './geometry.mjs';
import {PcmFrameAssembler,pcm16le,PlaybackLedger} from './audio-state.mjs';
const frame={captureId:'synthetic-42',imageWidth:500,imageHeight:300,frameWidth:1000,frameHeight:600,
  displayWidth:2000,displayHeight:1200,originX:-2000,originY:-100,displayId:'left'};
const pdf=pdfViewport({viewBox:[0,0,600,800],zoom:1.5});
const rotated=pdfViewport({viewBox:[10,20,210,120],zoom:2,userUnit:1.5,rotation:90,offsetX:7,offsetY:11});
const assembler=new PcmFrameAssembler(16000,20), audio=assembler.push(new Float32Array(1007));
const ledger=new PlaybackLedger(16000);ledger.enqueue(400);ledger.render(160);ledger.interrupt();
console.log(JSON.stringify({
  kind:'original-synthetic-worked-examples',
  display:{center:mapDisplayPoint([500,300],frame,'synthetic-42'),edge:mapDisplayPoint([1000,600],frame,'synthetic-42'),percentCenter:mapDisplayPoint([50,50],frame,'synthetic-42','percent-0-100')},
  window:mapWindowPoint([500,300],{...frame,windowWidth:800,windowHeight:480,windowId:'window-A'},'synthetic-42'),
  pdf:{viewport:pdf,rectangle:rectBounds([100,600,200,700],pdf.matrix),rotated,rotatedFullBounds:rectBounds([10,20,210,120],rotated.matrix),cssPoint:apply(pdf.matrix,[100,700]),bitmapPointAtDpr2:apply(canvasTransform(pdf.matrix,2),[100,700])},
  audio:{sampleRate:16000,durationMs:20,samplesPerFrame:assembler.samplesPerFrame,pcm16BytesPerFrame:pcm16le(audio[0].samples).byteLength,frames:audio.length,tailSamples:assembler.finish().length,playedMsAfterInterrupt:ledger.playedMs,remainingSamplesAfterInterrupt:ledger.queued}
},null,2));
