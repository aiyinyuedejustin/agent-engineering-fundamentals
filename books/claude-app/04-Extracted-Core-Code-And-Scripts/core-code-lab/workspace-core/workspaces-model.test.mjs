import test from 'node:test';
import assert from 'node:assert/strict';
import { ArtifactType as T, isCurrentArtifactStreaming, selectVersion,
  renderPlan, ContentEpoch, inspectInbound, changeViewerMode,
  withDeadline } from './workspaces-model.mjs';
const versions = [
  { uuid: 'a', toolUseId: 't1', messageId: 'm1', closed: true },
  { uuid: 'b', toolUseId: 't2', messageId: 'm2', closed: false }
];
test('version precedence and latest fallback', () => {
  assert.equal(selectVersion(versions, { versionId:'a', toolUseId:'t2' }, false), 0);
  assert.equal(selectVersion(versions, { versionId:'missing', toolUseId:'t1' }, false), 0);
  assert.equal(selectVersion(versions, { messageId:'m1' }, false), 0);
  assert.equal(selectVersion(versions, { versionId:'a' }, true), 1);
  assert.equal(selectVersion(versions, { messageId:'new-assistant-message-uuid-7' }, false), 1);
  assert.equal(selectVersion(versions, {}, false), 1);
  assert.equal(selectVersion([], {}, false), 0);
});
test('server record or a closed latest version removes the live-source override', () => {
  assert.equal(isCurrentArtifactStreaming({chatStreaming:true,versions,latestHasServerRecord:false}),true);
  assert.equal(isCurrentArtifactStreaming({chatStreaming:true,versions,latestHasServerRecord:true}),false);
  assert.equal(isCurrentArtifactStreaming({chatStreaming:false,versions,latestHasServerRecord:false}),false);
});
test('type and streaming select source, markdown, or sandbox', () => {
  for (const t of [T.html,T.react,T.svg,T.mermaid]) {
    assert.equal(renderPlan(t,'normal',true).renderer,'source');
    assert.equal(renderPlan(t,'normal',false).renderer,'sandbox');
    assert.equal(renderPlan(t,'raw',false).renderer,'source');
  }
  assert.equal(renderPlan(T.code,'normal',false).renderer,'source');
  assert.equal(renderPlan(T.markdown,'normal',true).renderer,'markdown');
  assert.equal(renderPlan(T.text,'normal',false).toggleVisible,false);
  assert.equal(renderPlan(T.svg,'normal',false).refreshVisible,false);
  assert.equal(renderPlan(T.html,'normal',false).refreshVisible,true);
});
test('stale success cannot authorize new content', () => {
  const gate = new ContentEpoch();
  const first = gate.replace(T.html,'first');
  const second = gate.replace(T.html,'second');
  assert.equal(gate.acknowledge(first,true),false);
  assert.equal(gate.acknowledge(second,false),false);
  assert.equal(gate.acknowledge(second,true),true);
  const receipt = gate.receipt();
  assert.equal(gate.mayUseCapability(receipt),true);
  gate.replace(T.html,'third');
  assert.equal(gate.mayUseCapability(receipt),false);
});
test('a request received before acknowledgement stays untrusted', () => {
  const gate = new ContentEpoch(), ticket = gate.replace(T.svg,'svg');
  const early = gate.receipt();
  gate.acknowledge(ticket,true);
  assert.equal(gate.mayUseCapability(early),false);
  assert.equal(gate.mayUseCapability(gate.receipt()),true);
  gate.refresh();
  assert.equal(gate.acknowledge(ticket,true),false);
});
test('origin, source, method, and payload checks are independent', () => {
  const source = {}, options = { expectedOrigin:'https://renderer.example',
    expectedSource:source,knownMethods:new Set(['ready']),
    isPayloadValid:(_,p)=>p?.version===1 };
  const good = { origin:options.expectedOrigin,source,data:{channel:'request',
    requestId:'q1',method:'ready',payload:{version:1}} };
  assert.equal(inspectInbound(good,options).accepted,true);
  assert.equal(inspectInbound({...good,origin:'https://other.example'},options).accepted,false);
  assert.equal(inspectInbound({...good,source:{}},options).accepted,false);
  assert.equal(inspectInbound({...good,data:{...good.data,payload:null}},options).accepted,false);
  assert.equal(inspectInbound({...good,data:{...good.data,method:'unknown'}},options).accepted,false);
  assert.equal(inspectInbound({...good,data:{...good.data,requestId:null}},options).accepted,false);
  assert.equal(inspectInbound({...good,data:{...good.data,channel:'response'}},options).accepted,false);
});
test('minimize remembers the previous visible mode', () => {
  let state = {mode:'dialog',restoreMode:'dialog'};
  state = changeViewerMode(state,'fullscreen');
  state = changeViewerMode(state,'minimized');
  assert.equal(state.restoreMode,'fullscreen');
  assert.equal(changeViewerMode(state,'minimized'),state);
});
test('the proposed deadline helper rejects an unresolved renderer', async () => {
  await assert.rejects(withDeadline(new Promise(()=>{}),1),/deadline/);
  assert.equal(await withDeadline(Promise.resolve('ok'),100),'ok');
});


test('an acknowledged identical repost keeps the epoch and prior receipt', () => {
  const gate = new ContentEpoch();
  const first = gate.replace(T.html, 'same');
  gate.acknowledge(first, true);
  const receipt = gate.receipt();
  const repost = gate.replace(T.html, 'same');
  assert.equal(repost.epoch, first.epoch);
  assert.equal(gate.mayUseCapability(receipt), true);
  assert.equal(gate.acknowledge(repost, false), false);
  // Failure of an identical repost does not itself erase prior acknowledgement.
  assert.equal(gate.mayUseCapability(receipt), true);
});

test('an unacknowledged identical repost starts a new delivery epoch', () => {
  const gate = new ContentEpoch();
  const first = gate.replace(T.html, 'same');
  const second = gate.replace(T.html, 'same');
  assert.equal(second.epoch, first.epoch + 1);
  assert.equal(gate.acknowledge(first, true), false);
  assert.equal(gate.acknowledge(second, true), true);
});

test('a type change revokes acknowledgement even when body text is unchanged', () => {
  const gate = new ContentEpoch();
  const html = gate.replace(T.html, 'same');
  gate.acknowledge(html, true);
  const receipt = gate.receipt();
  const svg = gate.replace(T.svg, 'same');
  assert.equal(svg.epoch, html.epoch + 1);
  assert.equal(gate.mayUseCapability(receipt), false);
  assert.equal(gate.acknowledge(html, true), false);
});

test('a closed latest artifact cannot activate the three-condition live gate', () => {
  assert.equal(isCurrentArtifactStreaming({ chatStreaming: true,
    versions: [{ ...versions.at(-1), closed: true }],
    latestHasServerRecord: false }), false);
});
