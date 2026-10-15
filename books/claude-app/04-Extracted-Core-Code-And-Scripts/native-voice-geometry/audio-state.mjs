/** Original simulations using synthetic samples only. No microphone, browser or network. */
export function rms(samples) {
  if (!samples.length) return 0;
  // Scaled sum of squares avoids overflow for representable finite RMS values.
  let scale=0, energy=0;
  for (const x of samples) {
    if (!Number.isFinite(x)) throw new TypeError('Invalid sample');
    const magnitude=Math.abs(x);
    if(magnitude>scale){energy=1+energy*(scale/magnitude)**2;scale=magnitude;}
    else if(magnitude>0)energy+=(magnitude/scale)**2;
  }
  return scale*Math.sqrt(energy/samples.length);
}
export function pcm16le(samples) {
  const bytes=new Uint8Array(samples.length*2), view=new DataView(bytes.buffer);
  for (let i=0;i<samples.length;i++){
    const v=samples[i];
    if (!Number.isFinite(v)) throw new TypeError('Invalid sample');
    const x=Math.min(1,Math.max(-1,v));
    view.setInt16(i*2,Math.round(x*(x<0?32768:32767)),true);
  }
  return bytes;
}
export class PcmFrameAssembler {
  #pending=[]; #sequence=0; #finished=false;
  constructor(sampleRate, durationMs) {
    if (!Number.isSafeInteger(sampleRate) || sampleRate<=0 || !Number.isFinite(durationMs) || durationMs<=0)
      throw new RangeError('Invalid audio format');
    this.samplesPerFrame=sampleRate*durationMs/1000;
    if (!Number.isSafeInteger(this.samplesPerFrame) || this.samplesPerFrame<1) throw new RangeError('Frame duration does not have an integer sample count');
    this.sampleRate=sampleRate;
  }
  push(samples) {
    // finish 关闭这一条采样流；在读取输入前拒绝后续写入。
    if (this.#finished) throw new Error('PCM stream is finished');
    // Snapshot once, then validate all input before mutating assembly state.
    const batch=Array.from(samples);
    // 用户迭代器可能在展开输入时调用 finish，再次确认流仍开放。
    if (this.#finished) throw new Error('PCM stream is finished');
    for (let i=0;i<batch.length;i++) {
      const sample=batch[i];
      if (!Number.isFinite(sample)) throw new TypeError('Invalid sample');
      const converted=Math.fround(sample);
      if (!Number.isFinite(converted)) throw new RangeError('Sample is not representable as finite Float32');
      batch[i]=converted;
    }
    const frames=[];
    for (const sample of batch) {
      this.#pending.push(sample);
      if (this.#pending.length === this.samplesPerFrame) {
        const sequence=this.#sequence++;
        frames.push({sequence,startSample:sequence*this.samplesPerFrame,
          startMs:sequence*this.samplesPerFrame/this.sampleRate*1000,
          samples:Float32Array.from(this.#pending)});
        this.#pending=[];
      }
    }
    return frames;
  }
  get pendingSamples(){return this.#pending.length;}
  finish(){
    if (this.#finished) return new Float32Array(0);
    const tail=Float32Array.from(this.#pending);
    this.#pending=[];
    this.#finished=true;
    return tail;
  }
}
export class EnvelopeHistory {
  #history=[]; #level=0;
  constructor({capacity=32,tauMs=80,noiseFloor=.02}={}) {
    if(!Number.isInteger(capacity)||capacity<1||!Number.isFinite(tauMs)||tauMs<=0||!Number.isFinite(noiseFloor)||noiseFloor<0||noiseFloor>=1) throw new RangeError('Invalid envelope parameters');
    Object.assign(this,{capacity,tauMs,noiseFloor});
  }
  sample(samples,elapsedMs) {
    if(!Number.isFinite(elapsedMs)||elapsedMs<0)throw new RangeError('Invalid elapsed time');
    const target=Math.min(1,Math.sqrt(Math.max(0,rms(samples)-this.noiseFloor)/(1-this.noiseFloor)));
    this.#level += (target-this.#level)*(1-Math.exp(-elapsedMs/this.tauMs));
    this.#history.push(this.#level);
    if(this.#history.length>this.capacity)this.#history.shift();
    return this.#level;
  }
  get values(){return [...this.#history];}
}
/** Abstract sample accounting, deliberately not a copy of the shipped worklet. */
export class PlaybackLedger {
  constructor(sampleRate=16000) {
    if(!Number.isSafeInteger(sampleRate)||sampleRate<=0)throw new RangeError('Invalid sample rate');
    Object.assign(this,{sampleRate,queued:0,played:0,underruns:0,started:false,pendingGap:false});
  }
  enqueue(count){if(!Number.isSafeInteger(count)||count<0||!Number.isSafeInteger(this.queued+count))throw new RangeError('Invalid or unrepresentable count');this.queued+=count;}
  render(requested) {
    if(!Number.isSafeInteger(requested)||requested<1)throw new RangeError('Invalid quantum');
    const consumed=Math.min(requested,this.queued);
    if(!Number.isSafeInteger(this.played+consumed))throw new RangeError('Played sample count overflow');
    if(consumed>0){if(this.pendingGap)this.underruns++;this.pendingGap=false;this.started=true;}
    this.queued-=consumed;this.played+=consumed;
    if(consumed<requested&&this.started)this.pendingGap=true;
    return {consumed,zeroFilled:requested-consumed};
  }
  finishTurn(){this.pendingGap=false;this.started=false;}
  interrupt(){this.queued=0;this.finishTurn();}
  get playedMs(){return this.played/this.sampleRate*1000;}
}
/** Epoch guard illustrates stale async work, not the target's entire state machine. */
export class VoiceEpoch {
  constructor(){this.epoch=0;this.state='idle';this.replySamples=0;}
  start(){this.epoch++;this.state='connecting';this.replySamples=0;return this.epoch;}
  event(epoch,type,payload=0){
    if(epoch!==this.epoch||this.state==='idle'||this.state==='error')return false;
    if(type==='ready')this.state='listening';
    else if(type==='input-end')this.state='processing';
    else if(type==='audio'){if(!Number.isSafeInteger(payload)||payload<0||!Number.isSafeInteger(this.replySamples+payload))throw new RangeError('Invalid samples');this.replySamples+=payload;this.state='speaking';}
    else if(type==='error')this.state='error';
    else throw new RangeError('Unknown event');
    return true;
  }
  interrupt(){this.epoch++;this.replySamples=0;this.state='listening';return {epoch:this.epoch,effect:'request-server-interrupt'};}
  stop(){this.epoch++;this.replySamples=0;this.state='idle';}
}
