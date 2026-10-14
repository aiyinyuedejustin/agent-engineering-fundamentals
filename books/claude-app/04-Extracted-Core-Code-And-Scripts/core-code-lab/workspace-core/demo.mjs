import { ArtifactType as T, ContentEpoch, renderPlan, selectVersion } from './workspaces-model.mjs';

const versions = [
  { uuid: 'revision-a', toolUseId: 'tool-a', messageId: 'message-a', closed: true },
  { uuid: 'revision-b', toolUseId: 'tool-b', messageId: 'message-b', closed: false }
];
console.log('选择旧版本：', selectVersion(versions, { versionId: 'revision-a' }, false));
console.log('正在生成时：', renderPlan(T.react, 'normal', true).renderer);
console.log('生成结束后：', renderPlan(T.react, 'normal', false).renderer);

const gate = new ContentEpoch();
const ticketA = gate.replace(T.html, '<h1>A</h1>');
const early = gate.receipt();
gate.acknowledge(ticketA, true);
console.log('提前到达的请求不能借用后来的确认：', gate.mayUseCapability(early));
const accepted = gate.receipt();
const same = gate.replace(T.html, '<h1>A</h1>');
console.log('相同且已确认内容重发可沿用 epoch：', same.epoch === ticketA.epoch);
console.log('原确认仍适用：', gate.mayUseCapability(accepted));
const ticketB = gate.replace(T.html, '<h1>B</h1>');
console.log('旧投递回执不能确认新内容：', gate.acknowledge(ticketA, true));
gate.acknowledge(ticketB, true);
console.log('旧内容的请求仍不能执行：', gate.mayUseCapability(accepted));
