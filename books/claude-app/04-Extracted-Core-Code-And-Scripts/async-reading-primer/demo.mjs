import { deferred, Owner, commitAfter, waitUntil, effectAfter, TeachingQueue } from './async-boundaries.mjs';

async function awaitDemo() {
  for (const guarded of [false, true]) {
    const owner = new Owner();
    const ticket = owner.begin('A');
    const ready = deferred();
    const job = commitAfter(owner, ticket, ready.promise, { guarded });
    owner.begin('B');
    ready.resolve('result:A');
    const outcome = await job;
    const snapshot = owner.snapshot();
    console.log(`await ${guarded ? 'guarded' : 'unsafe'}: current=${snapshot.current}, value=${snapshot.value}, outcome=${outcome}`);
  }
}

async function deadlineDemo() {
  const gate = deferred();
  const deadline = deferred();
  const effects = [];
  const controller = new AbortController();
  const work = effectAfter(gate.promise, effects, { signal: controller.signal });
  const waiting = waitUntil(work, deadline.promise);
  deadline.resolve();
  const report = await waiting;
  console.log(`deadline: report=${report.kind}, writes=${effects.length}`);
  controller.abort();
  gate.resolve();
  const outcome = await work;
  console.log(`deadline later: report=${report.kind}, signal=${controller.signal.aborted}, work=${outcome}, writes=${effects.length}`);
}

async function queueDemo() {
  const queue = new TeachingQueue();
  const gate = deferred();
  let writes = 0;
  const receipt = await queue.enqueue(async () => { await gate.promise; writes++; return 'saved'; });
  console.log(`queue admitted: accepted=${receipt.accepted}, state=${queue.state(receipt.id)}, writes=${writes}`);
  const worker = queue.runNext();
  console.log(`queue started: state=${queue.state(receipt.id)}, writes=${writes}`);
  gate.resolve();
  const result = await receipt.completion;
  await worker;
  console.log(`queue completed: state=${result.state}, value=${result.value}, writes=${writes}`);
}

const demos = { await: awaitDemo, deadline: deadlineDemo, queue: queueDemo };
const selected = process.argv[2] ?? 'all';
if (selected === 'all') {
  for (const demo of Object.values(demos)) await demo();
} else if (Object.hasOwn(demos, selected)) {
  await demos[selected]();
} else {
  console.error('Usage: node demo.mjs [all|await|deadline|queue]');
  process.exitCode = 1;
}
