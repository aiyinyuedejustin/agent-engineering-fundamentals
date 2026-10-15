import { FakeClock, SnapshotPresenter, StableBlocks } from './model.mjs';
const paragraphs = Array.from({ length: 160 }, (_, i) => `段落 ${i + 1}：让接收、解析、格式化与提交各自拥有明确边界。\n\n`);
const corpus = paragraphs.join('') + '```js\nconst answer = 42;\n```\n\n结束。';
const clock = new FakeClock();
let naiveParseChars = 0, chunkParseChars = 0, last = '', previousBlocks = new Set(), commits = 0;
const blocks = new StableBlocks({ finalParser: text => { chunkParseChars += text.length; return { source: text }; } });
const presenter = new SnapshotPresenter({ clock, commit(snapshot) {
  commits++; last = snapshot.text;
  const state = blocks.update(snapshot.text, { terminal: snapshot.terminal });
  if (!snapshot.terminal) {
    for (const block of state.blocks) if (!previousBlocks.has(block)) chunkParseChars += block.text.length;
    chunkParseChars += state.tail.length;
  }
  previousBlocks = new Set(state.blocks);
} });
let updates = 0;
for (let i = 9; i < corpus.length; i += 9) {
  const text = corpus.slice(0, i); naiveParseChars += text.length; updates++;
  presenter.accept(text); clock.advance(3);
}
naiveParseChars += corpus.length; updates++;
presenter.accept(corpus, { terminal: true }); clock.advance(1000);
if (last !== corpus) throw Error('final content lost');
console.log(JSON.stringify({ label: 'deterministic model, not Claude benchmark', unit: 'UTF-16 code units', sourceLength: corpus.length, updates, commits, naiveParseInput: naiveParseChars, stableAndTailParseInput: chunkParseChars, parseInputReduction: +(1 - chunkParseChars / naiveParseChars).toFixed(4), completedLineBookkeeping: blocks.scannedChars, finalContentExact: last === corpus, pendingTimers: clock.tasks.size, caveat: 'Counts logical parser input only; no real parser, DOM, Worker startup, string-copy, GC or paint cost is timed.' }, null, 2));
