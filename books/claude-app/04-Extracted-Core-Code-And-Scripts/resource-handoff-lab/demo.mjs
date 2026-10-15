import { createLease, startHandoff, RELEASE_CONFIRMED } from './resource-handoff.mjs';

// Entirely synthetic: a Set represents live resource identities, not OS fds.
const live = new Set();
const events = [];
function allocate(label) {
  const identity = Object.freeze({ label });
  live.add(identity);
  return createLease(() => {
    live.delete(identity);
    events.push(`released: ${label}`);
    return RELEASE_CONFIRMED;
  });
}

// Scenario 1: ready alone does not transfer. Consumer closes in finally.
const normal = startHandoff({ acquire: () => allocate('consumer-owned example') });
const offer = await normal.ready;
console.log('After ready:', normal.inspect().resource.state);
const owner = offer?.claim();
if (owner) {
  try {
    console.log('After claim:', owner.inspect().state);
  } finally {
    console.log('Consumer cleanup:', owner.close().state);
  }
}

// Scenario 2: acquisition has started. Cancel cannot stop its later result.
let finishAcquisition;
const pending = new Promise((resolve) => { finishAcquisition = resolve; });
const cancelled = startHandoff({ acquire: () => pending });
await Promise.resolve();
cancelled.cancel('destination closed');
finishAcquisition(allocate('late acquisition example'));
await cancelled.ready;
console.log('Late-result cleanup:', cancelled.inspect().resource.state);
console.log('Cleanup log:', events);
console.log('Synthetic resources still live:', live.size);
if (live.size !== 0) throw new Error('demo did not release its synthetic resources');
