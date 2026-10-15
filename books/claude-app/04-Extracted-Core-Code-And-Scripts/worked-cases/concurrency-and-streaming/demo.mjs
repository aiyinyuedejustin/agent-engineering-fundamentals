import { ScopedMutationQueue } from './existing-models.mjs';
import { VersionedSettings, rebaseDisjoint } from './authority-model.mjs';

// Both clients read before either saves. Even completely sequential saves lose
// an update if the later client submits its stale complete object unconditionally.
let naive = { enabled: true, label: 'original' };
const a = { ...naive }, b = { ...naive };
await new ScopedMutationQueue().run('same-resource', () => {
  naive = { ...a, enabled: false };
});
await new ScopedMutationQueue().run('same-resource', () => {
  naive = { ...b, label: 'renamed' };
});
console.log(`local queues: enabled=${naive.enabled}, label=${naive.label}`);

const store = new VersionedSettings({ enabled: true, label: 'original' }, 7);
const base = store.read();
const first = { operationId: 'disable-1', expectedRevision: 7,
  value: { ...base.value, enabled: false } };
const disable = store.submit(first);
console.log(`conditional A: ${disable.kind}, revision=${disable.snapshot.revision}`);
const rename = store.submit({ operationId: 'rename-1', expectedRevision: 7,
  value: { ...base.value, label: 'renamed' } });
console.log(`conditional B: ${rename.kind}, enabled=${store.read().value.enabled}`);

const current = store.read();
const rebased = rebaseDisjoint(base.value, current.value, { label: 'renamed' });
if (rebased.kind !== 'proposed') throw new Error('Unexpected example conflict');
const retry = store.submit({ operationId: 'rename-2', expectedRevision: current.revision,
  value: rebased.value });
console.log(`rebase B: ${retry.kind}, revision=${retry.snapshot.revision}, enabled=${store.read().value.enabled}`);

const receipt = store.submit(first);
console.log(`replay A: receiptRevision=${receipt.snapshot.revision}, currentRevision=${store.read().revision}, commits=${store.commits}`);
