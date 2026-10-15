import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { MemoryStorage, BackoffLedger } from '../recovery-state.mjs';
import { parseRetryAfter } from '../resilience-core.mjs';
const make = () => { const local = new MemoryStorage(), session = new MemoryStorage(); return { local, session, ledger: new BackoffLedger(local, session, () => 1000000) }; };
test('single writer preserves same-clock fallback counts and recovery', () => {
  const { local, session, ledger } = make();
  assert.equal(ledger.record().failures, 1); local.failWrites = true;
  assert.equal(ledger.record().failures, 2); assert.equal(ledger.read().failures, 2);
  assert.equal(ledger.record().failures, 3); local.failWrites = false;
  assert.equal(ledger.read().failures, 3); assert.equal(session.values.size, 0);
  assert.equal(ledger.record().failures, 4);
});
test('same-clock clear tombstone wins over stale local and survives reconstruction', () => {
  const { local, session, ledger } = make(); ledger.record(); local.failWrites = true; ledger.record();
  assert.equal(ledger.clear().stored, true); assert.equal(ledger.read(), null);
  const restored = new BackoffLedger(local, session, () => 1000000);
  assert.equal(restored.read(), null); local.failWrites = false;
  assert.equal(restored.read(), null); assert.equal(session.values.size, 0);
  assert.equal(restored.record().failures, 1);
});
test('old session cannot resurrect after clear successfully writes local', () => {
  const { local, session, ledger } = make(); local.failWrites = true; ledger.record();
  local.failWrites = false; session.failWrites = true; // promotion cannot remove old session
  assert.equal(ledger.clear().stored, true); assert.equal(ledger.read(), null);
  assert.equal(ledger.record().failures, 1); assert.equal(ledger.read().failures, 1);
});
test('unwritable stores report clear failure rather than promise durable deletion', () => {
  const { local, session, ledger } = make(); ledger.record(); local.failWrites = session.failWrites = true;
  assert.equal(ledger.clear().stored, false); assert.equal(ledger.read().failures, 1);
});
test('old v1 records migrate without weakening same-time ordering', () => {
  const { local, ledger } = make(); local.setItem('teaching-backoff-v1', JSON.stringify({ v: 1, failures: 5, at: 1000000 }));
  assert.equal(ledger.read().order, 0); assert.equal(ledger.record().failures, 6); assert.equal(ledger.read().order, 1);
});
test('expired clear tombstones do not preserve old failure counts', () => {
  let now = 1000000; const local = new MemoryStorage(), session = new MemoryStorage(), ledger = new BackoffLedger(local,session,()=>now);
  ledger.record(); local.failWrites = true; ledger.clear(); now += 300000;
  assert.equal(ledger.read(),null); assert.equal(ledger.record().failures,1);
});
const now = Date.UTC(2026,0,1);
for (const zone of ['UTC', 'America/New_York', 'Asia/Tokyo']) test(`all HTTP-date forms are UTC in ${zone}`, () => {
  const module = new URL('../resilience-core.mjs', import.meta.url).href;
  const code = `import { parseRetryAfter, RetryBudget } from ${JSON.stringify(module)};
    const dates=['Thu, 01 Jan 2026 00:00:20 GMT','Thursday, 01-Jan-26 00:00:20 GMT','Thu Jan  1 00:00:20 2026','Thu Jan 01 00:00:20 2026'];
    const waits=dates.map(x=>parseRetryAfter(x,${now}));
    console.log(JSON.stringify({waits,actions:waits.map(retryAfterMs=>new RetryBudget({mode:'legacy',perTurn:true,honorStated:true}).failure({kind:'overload',retryAfterMs}).action)}));`;
  const child = spawnSync(process.execPath,['--input-type=module','-e',code],{env:{...process.env,TZ:zone},encoding:'utf8',timeout:5000});
  assert.equal(child.status,0,child.stderr); assert.deepEqual(JSON.parse(child.stdout),{waits:[20000,20000,20000,20000],actions:['retry','retry','retry','retry']});
});
test('strict dates reject non-HTTP, normalization and weekday mismatch', () => {
  for(const x of ['Sun, 01 Jan 1899 00:00:00 GMT','Sat, 01 Jan 0000 00:00:00 GMT','January 1, 2026 00:00:20 GMT','Sun, 31 Feb 2026 00:00:00 GMT','Fri, 01 Jan 2026 00:00:20 GMT','Thu, 01 Jan 2026 24:00:00 GMT','Thu, 01 Jan 2026 00:60:00 GMT','Thu, 01 Jan 2026 00:00:61 GMT','Thu, 01 Foo 2026 00:00:00 GMT']) assert.equal(parseRetryAfter(x,now),undefined,x);
});
test('RFC850 rolling 50-year cutoff is date-sensitive and crosses centuries', () => {
  const format = date => ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][date.getUTCDay()]+`, 01-Jan-${String(date.getUTCFullYear()%100).padStart(2,'0')} 00:00:00 GMT`;
  const future = new Date(Date.UTC(2076,0,1));
  assert.equal(parseRetryAfter(format(future),now),future.getTime()-now);
  const past = new Date(Date.UTC(1976,0,1));
  assert.equal(parseRetryAfter(format(past),now-1),0); // >50y ahead must be 1976
  const nextCentury = new Date(Date.UTC(2110,0,1)), nearEnd = Date.UTC(2090,0,1);
  assert.equal(parseRetryAfter(format(nextCentury),nearEnd),nextCentury.getTime()-nearEnd);
});
test('leap second maps to next JS instant and invalid now fails closed', () => {
  assert.equal(parseRetryAfter('Sat, 31 Dec 2016 23:59:60 GMT', Date.UTC(2016,11,31,23,59,59)),1000);
  assert.equal(parseRetryAfter('10',NaN),undefined);
});
