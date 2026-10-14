import test from 'node:test';
import assert from 'node:assert/strict';
import { SessionModel, ApprovalInbox } from './session-model.mjs';
const fake = () => ({ closes: 0, close() { this.closes++; } });
test('stop during startup prevents stale success from attaching', () => {
  const s = new SessionModel(), old = s.begin(); s.stop(); const newer = s.begin();
  const stale = fake(); assert.equal(s.attach(old, stale), false); assert.equal(stale.closes, 1);
  assert.equal(s.state, 'starting'); assert.equal(s.attach(newer, fake()), true);
  assert.equal(s.result(old, { status: 'success' }), false);
});
test('turn success and process EOF are different outcomes', () => {
  const s = new SessionModel(), ticket = s.begin(), transport = fake(); s.attach(ticket, transport);
  assert.equal(s.result(ticket, { status: 'success' }), true);
  assert.equal(s.connected, true); assert.equal(transport.closes, 0);
  s.eof(ticket); assert.equal(s.outcome, 'success'); assert.equal(s.connected, false);
  const other = s.begin(); s.attach(other, fake()); s.eof(other); assert.equal(s.outcome, 'incomplete');
});
test('duplicate in-flight approval shares one result and teardown settles waits', async () => {
  const inbox = new ApprovalInbox(), p = inbox.request('A'); assert.equal(inbox.request('A'), p);
  inbox.decide('A', 'unexpected'); assert.equal(await p, 'deny');
  assert.equal(inbox.decide('A', 'allow'), false);
  const q = inbox.request('B'); inbox.close(); assert.equal(await q, 'deny');
  assert.throws(() => inbox.request('C'), /closed/);
});
test('settled approval identities stay settled for the inbox lifetime', async () => {
  const inbox = new ApprovalInbox();
  for (const decision of ['allow', 'deny']) {
    const original = inbox.request(decision);
    assert.equal(inbox.decide(decision, decision), true);
    assert.equal(await original, decision);
    assert.equal(inbox.request(decision), original);
    assert.equal(await inbox.request(decision), decision);
    assert.equal(inbox.decide(decision, 'allow'), false);
    assert.equal(inbox.abort(decision), false);
  }
  const aborted = inbox.request('aborted'); inbox.abort('aborted');
  assert.equal(inbox.request('aborted'), aborted); assert.equal(await aborted, 'deny');
  inbox.close(); assert.throws(() => inbox.request('allow'), /closed/);
});
test('duplicate attach never closes the transport already owned by this session', () => {
  const s = new SessionModel(), ticket = s.begin(), transport = fake();
  s.attach(ticket, transport);
  assert.equal(s.attach(ticket, transport), false);
  assert.equal(transport.closes, 0); assert.equal(s.connected, true);
  assert.equal(s.attach({}, transport), false); assert.equal(transport.closes, 0);
});
test('close can synchronously notify EOF without recursive teardown', () => {
  for (const action of ['error', 'eof', 'stop', 'begin']) {
    const s = new SessionModel(), ticket = s.begin(); let closes = 0;
    s.attach(ticket, { close() { closes++; assert.ok(closes <= 1); s.eof(ticket); } });
    if (action === 'error') s.result(ticket, { status: 'error' });
    else if (action === 'eof') s.eof(ticket);
    else if (action === 'stop') s.stop();
    else {
      s.result(ticket, { status: 'success' }); const newer = s.begin();
      assert.equal(s.current(newer), true); assert.equal(s.state, 'starting');
      assert.equal(s.outcome, null);
    }
    assert.equal(closes, 1);
  }
});
test('old EOF and result cannot affect a new running session', () => {
  const s = new SessionModel(), old = s.begin(); s.stop();
  const current = s.begin(), transport = fake(); s.attach(current, transport);
  assert.equal(s.eof(old), false); assert.equal(s.result(old, { status: 'error' }), false);
  assert.equal(s.state, 'running'); assert.equal(s.connected, true); assert.equal(transport.closes, 0);
});
