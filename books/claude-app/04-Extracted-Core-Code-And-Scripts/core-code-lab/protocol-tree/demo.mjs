import { IncrementalSSE, consumeChunks, makeWorkBudget } from './incremental-sse.mjs';
import { ContentReducer } from './content-reducer.mjs';
import { ConversationBranches, ROOT } from './branch-manager.mjs';

const tree = new ConversationBranches([
  { uuid: 'human-1', parent_message_uuid: ROOT, sender: 'human', index: 0, text: 'Explain the idea.' },
  { uuid: 'answer-1', parent_message_uuid: 'human-1', sender: 'assistant', index: 1, text: 'First version.' },
]);
tree.retryAssistant('answer-1', 'answer-2');
console.log('After retry:', tree.visiblePath().map(m => m.uuid));
tree.switchSibling('answer-2', -1);
console.log('After switching back:', tree.visiblePath().map(m => m.uuid));

const events = [
  { type: 'message_start' },
  { type: 'content_block_start', index: 0, content_block: { type: 'text', text: '' } },
  { type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: 'Hello, ' } },
  { type: 'content_block_delta', index: 0, delta: { type: 'text_delta', text: '世界🙂' } },
  { type: 'content_block_stop', index: 0 },
  { type: 'message_delta', delta: { stop_reason: 'end_turn' } },
  { type: 'message_stop' },
];
const wire = new TextEncoder().encode(events.map(event => `event: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`).join(''));
async function* chunks() { for (let i = 0; i < wire.length; i += 13) yield wire.slice(i, i + 13); }
const reducer = new ContentReducer(snapshot => console.log('Snapshot:', JSON.stringify(snapshot)));
const budget = makeWorkBudget();
await consumeChunks(chunks(), frame => { if (frame.data) reducer.apply(JSON.parse(frame.data)); }, {
  decoder: new IncrementalSSE(),
  afterChunk: async () => { reducer.flush(); await budget(); },
});
