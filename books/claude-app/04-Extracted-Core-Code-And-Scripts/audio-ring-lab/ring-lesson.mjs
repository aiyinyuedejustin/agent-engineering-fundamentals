// 原创单 JS 确定性交错模型。不是 SharedArrayBuffer / AudioWorklet 实现。
const requireState = (condition, message) => { if (!condition) throw new Error(message); };
export class RingLesson {
  #slots; #rd = 0; #wr = 0; #g = 0; #phase = 'open';
  #pending = []; #write = null; #read = null; #flush = null; #ack = null;
  #accepted = 0; #consumed = 0; #discarded = 0; #ends = [];
  constructor(capacity = 5) {
    requireState(Number.isSafeInteger(capacity) && capacity >= 2, '容量必须是至少2的安全整数');
    this.#slots = Array(capacity);
  }
  #readable() { return (this.#wr - this.#rd + this.#slots.length) % this.#slots.length; }
  #ticket(actual, token) { requireState(actual && actual.token === token, '票据已失效或不属于本次操作'); }
  #open() { requireState(this.#phase === 'open', '当前代已封口或正在等待flush确认'); }
  snapshot() {
    const readable = this.#readable();
    return Object.freeze({capacity: this.#slots.length, usable: this.#slots.length - 1,
      rd: this.#rd, wr: this.#wr, readable, free: this.#slots.length - 1 - readable,
      generation: this.#g, phase: this.#phase, pending: this.#pending.length,
      accepted: this.#accepted, consumed: this.#consumed, discarded: this.#discarded,
      balanceOK: this.#accepted === this.#consumed + this.#discarded + readable});
  }
  // 迟到回调先检代次，再接触输入；false表示整批不接纳。
  enqueue(generation, samples) {
    if (generation !== this.#g || this.#phase !== 'open') return false;
    requireState(Array.isArray(samples), '教学输入必须是数值数组');
    const copy = Array.from(samples);
    requireState(copy.every(x => typeof x === 'number' && Number.isFinite(x)), '样本必须是有限数');
    // 防御数组getter/迭代器在复制时调用生命周期方法；不接纳旧代输出。
    if (generation !== this.#g || this.#phase !== 'open') return false;
    this.#pending = this.#pending.concat(copy);
    return true;
  }
  reserve() {
    this.#open();
    requireState(!this.#write, '只能有一个未发布写批次');
    const count = Math.min(this.#pending.length, this.#slots.length - 1 - this.#readable());
    if (!count) return null;
    requireState(Number.isSafeInteger(this.#accepted + count), 'accepted序号超出教学模型范围');
    const token = Object.freeze({});
    this.#write = {token, count, copied: false};
    return token;
  }
  copy(token) {
    this.#ticket(this.#write, token);
    requireState(!this.#write.copied, '本批已经复制');
    for (let i = 0; i < this.#write.count; i++) {
      this.#slots[(this.#wr + i) % this.#slots.length] = Object.freeze({
        value: this.#pending[i], generation: this.#g, sequence: this.#accepted + i + 1});
    }
    this.#write.copied = true;
  }
  publish(token) {
    this.#open(); this.#ticket(this.#write, token);
    requireState(this.#write.copied, '必须先copy再publish');
    const count = this.#write.count;
    this.#wr = (this.#wr + count) % this.#slots.length;
    this.#accepted += count;
    this.#pending.splice(0, count); // 未接纳尾部仍在这里，永远先于后来的批次。
    this.#write = null;
    return count;
  }
  cancel(token) { this.#ticket(this.#write, token); this.#write = null; }
  acquire(max) {
    requireState(Number.isSafeInteger(max) && max > 0, '读取上限必须为正安全整数');
    requireState(!this.#read, '只能有一个未释放读批次');
    const count = Math.min(max, this.#readable());
    if (!count) return null;
    const token = Object.freeze({});
    this.#read = {token, count, output: null};
    return token;
  }
  copyOut(token) {
    this.#ticket(this.#read, token);
    requireState(!this.#read.output, '本批已经copyOut');
    this.#read.output = Array.from({length: this.#read.count}, (_, i) =>
      this.#slots[(this.#rd + i) % this.#slots.length]);
    return Object.freeze([...this.#read.output]);
  }
  release(token) {
    this.#ticket(this.#read, token);
    requireState(this.#read.output, '必须先copyOut再release');
    const output = this.#read.output;
    this.#rd = (this.#rd + this.#read.count) % this.#slots.length;
    this.#consumed += this.#read.count;
    this.#read = null;
    const last = output.at(-1).sequence;
    const done = this.#ends.filter(end => end.sequence <= last);
    this.#ends = this.#ends.filter(end => end.sequence > last);
    return Object.freeze({output: Object.freeze([...output]), done: Object.freeze(done)});
  }
  // 调用方保证本turn所有异步输出已交齐；模型不能从空pending推断解码已结束。
  end(generation) {
    this.#open(); requireState(generation === this.#g, 'end代次不匹配');
    requireState(!this.#write && !this.#pending.length, '先结清未发布批次与保留尾部');
    const end = Object.freeze({generation, sequence: this.#accepted});
    this.#phase = 'ended';
    // 空队列边界已经消费完成，立即返回done，而不是等下一次release。
    const immediate = this.#readable() === 0;
    if (!immediate) this.#ends.push(end);
    return Object.freeze({boundary: end, done: immediate ? end : null});
  }
  nextTurn() {
    requireState(this.#phase === 'ended', '必须先自然end再开启下一turn');
    requireState(Number.isSafeInteger(this.#g + 1), 'generation超出教学模型范围');
    this.#g++; this.#phase = 'open'; return this.#g;
  }
  requestFlush() {
    requireState(this.#phase !== 'waiting', '已有flush等待确认');
    requireState(Number.isSafeInteger(this.#g + 1), 'generation超出教学模型范围');
    // 取消未发布批次：已复制槽仍不可见；旧票据无法再publish。
    this.#write = null;
    const abandonedPending = this.#pending.length;
    this.#pending = [];
    this.#phase = 'waiting';
    this.#flush = Object.freeze({generation: this.#g + 1});
    this.#ack = null;
    return Object.freeze({request: this.#flush, abandonedPending});
  }
  consumerFlush(request) {
    requireState(request === this.#flush && this.#phase === 'waiting' && !this.#ack,
      '不是当前未处理flush');
    requireState(!this.#read, '必须在完整消费步骤之间处理flush');
    const discarded = this.#readable();
    this.#discarded += discarded;
    this.#rd = this.#wr; // 只有consumer推进RD；不重置WR。
    const canceledEnds = Object.freeze([...this.#ends]);
    this.#ends = [];
    this.#ack = Object.freeze({generation: request.generation, discarded, canceledEnds});
    return this.#ack;
  }
  acknowledge(ack) {
    if (this.#phase !== 'waiting' || ack !== this.#ack || !ack) return false;
    this.#g = ack.generation; this.#phase = 'open';
    this.#flush = null; this.#ack = null;
    return true;
  }
}
