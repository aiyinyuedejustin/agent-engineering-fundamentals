/** Original, in-memory teaching model. No target code, network, or real settings.
 * Each instance owns exactly one synthetic settings resource. Revisions are
 * authoritative resource versions, not UI request generations or timestamps.
 */
const fields = ['enabled', 'label'];

function ordinaryRecord(value, allowed) {
  if (value === null || typeof value !== 'object' ||
      ![Object.prototype, null].includes(Object.getPrototypeOf(value)))
    throw new TypeError('Expected an ordinary data record');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  const keys = Reflect.ownKeys(descriptors);
  if (keys.some(key => !allowed.includes(key) || !Object.hasOwn(descriptors[key], 'value')))
    throw new TypeError('Unknown key or accessor');
  return Object.fromEntries(keys.map(key => [key, descriptors[key].value]));
}

function settings(value, partial = false) {
  const copy = ordinaryRecord(value, fields);
  if (!partial && fields.some(key => !Object.hasOwn(copy, key)))
    throw new TypeError('Missing settings field');
  if (Object.hasOwn(copy, 'enabled') && typeof copy.enabled !== 'boolean')
    throw new TypeError('enabled must be boolean');
  if (Object.hasOwn(copy, 'label') && typeof copy.label !== 'string')
    throw new TypeError('label must be string');
  return copy;
}

function revision(value) {
  if (!Number.isSafeInteger(value) || value < 0) throw new TypeError('Invalid revision');
  return value;
}

function request(value) {
  const copy = ordinaryRecord(value, ['operationId', 'expectedRevision', 'value']);
  if (typeof copy.operationId !== 'string' || !copy.operationId.length)
    throw new TypeError('operationId required');
  return { operationId: copy.operationId,
    expectedRevision: revision(copy.expectedRevision), value: settings(copy.value) };
}

export class VersionedSettings {
  #value;
  #revision;
  #receipts = new Map();
  #commits = 0;

  constructor(value, initialRevision = 0) {
    this.#value = settings(value);
    this.#revision = revision(initialRevision);
  }

  read() { return { revision: this.#revision, value: { ...this.#value } }; }
  get commits() { return this.#commits; }

  submit(input) {
    const q = request(input);
    // Canonical for this deliberately tiny scalar schema. This is not a
    // general JSON canonicalizer and is not a cryptographic authentication tag.
    const binding = JSON.stringify([q.expectedRevision, q.value.enabled, q.value.label]);
    const previous = this.#receipts.get(q.operationId);
    if (previous) {
      if (previous.binding !== binding) throw new Error('OPERATION_ID_REUSED');
      // A receipt describes the previous operation, not today's resource state.
      return structuredClone({ ...previous.result, replayed: true });
    }

    let result;
    if (q.expectedRevision !== this.#revision) {
      result = { kind: 'conflict', operationId: q.operationId, snapshot: this.read() };
    } else {
      if (this.#revision === Number.MAX_SAFE_INTEGER) throw new RangeError('REVISION_EXHAUSTED');
      // One synchronous state transition in this MODEL, with no await/callback.
      // A real authority needs a database conditional update/transaction here.
      this.#value = q.value;
      this.#revision++;
      this.#commits++;
      result = { kind: 'committed', operationId: q.operationId, snapshot: this.read() };
    }
    // This model remembers conflicts as well as commits. Changing the expected
    // revision or proposal is a new operation and requires a fresh identity.
    this.#receipts.set(q.operationId, { binding, result: structuredClone(result) });
    return structuredClone({ ...result, replayed: false });
  }
}

/** Conservative three-way rebase for independent scalar assignments ONLY.
 * It never decides which of two conflicting same-field user intents should win.
 */
export function rebaseDisjoint(base, current, intent) {
  base = settings(base); current = settings(current); intent = settings(intent, true);
  const conflicts = Object.keys(intent).filter(key => current[key] !== base[key]);
  return conflicts.length ? { kind: 'conflict', fields: conflicts }
    : { kind: 'proposed', value: { ...current, ...intent } };
}
