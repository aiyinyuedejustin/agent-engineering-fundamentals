import { RetryBudget, streamOutcome } from './resilience-core.mjs';
import { CursorConsumer, IdempotentServer, makeMirror } from './recovery-state.mjs';
const retry = new RetryBudget({ mode: 'expanded' });
const trace = [];
for (let call = 1; call <= 50; call++) {
  const decision = retry.failure({ kind: 'network' });
  trace.push({ call, ...decision }); if (decision.action === 'stop') break;
}
const cursor = new CursorConsumer();
const poison = Array.from({ length: 3 }, () => cursor.deliver(7, 'malformed', () => { throw new Error('bad'); }));
const server = new IdempotentServer(); server.submit('stable-turn', 'example'); server.submit('stable-turn', 'example');
const mirror = makeMirror({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: '中'.repeat(1366) }] }] }, { account: 'demo', session: 'demo', attachmentCount: 1 }, 0);
console.log(JSON.stringify({ originalLabOnly: true, expandedNetworkFailureTrace: trace, stoppedThenDisconnected: streamOutcome({ stopped: true, networkError: true }), poison, cursor: cursor.cursor, simulatedServerExecutions: server.executions, oversizedMirror: mirror }, null, 2));
