import { consumeInSlices } from './sliced-consumer.mjs';
const bytes = new TextEncoder().encode('data: x\n\n'.repeat(20_000));
console.log(JSON.stringify(await consumeInSlices((async function* () { yield bytes; })(), () => {}), null, 2));
