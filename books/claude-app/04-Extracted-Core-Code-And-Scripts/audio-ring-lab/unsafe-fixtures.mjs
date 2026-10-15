// 故意损坏合同的专用反例。与RingLesson没有继承关系，不可切换为生产模式。
export function earlyPublish() {
  const slots = Array(5);
  let wr = 0;
  wr = 1; // 错：还没复制，就宣称槽0可读。
  const observed = wr > 0 ? slots[0] : null;
  slots[0] = 101;
  return {observed, eventualValue: slots[0]};
}
export function earlyRelease() {
  const slots = [101, 102, 103, 104, undefined];
  let rd = 0;
  let wr = 4; // 满：可用4。
  const acquiredIndex = rd;
  rd = 2; // 错：宣称两个槽已消费，但尚未copyOut。
  slots[wr] = 105; wr = (wr + 1) % 5;
  slots[wr] = 106; wr = (wr + 1) % 5;
  return {expected: 101, observed: slots[acquiredIndex], rd, wr};
}
