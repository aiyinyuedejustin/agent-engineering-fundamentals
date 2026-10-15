/** Original, side-effect-free teaching models. NOT a production shell or sandbox.
 * No target application code is imported; no process/network/real-file operations.
 */
import {createHash} from 'node:crypto';

export class Rejected extends Error {}
const reject = message => { throw new Rejected(message); };
const plain = value => value !== null && typeof value === 'object'
  && [Object.prototype, null].includes(Object.getPrototypeOf(value));

/** Canonical form for plain JSON only; digest binds content, NOT caller authority. */
export function canonical(value) {
  const seen = new Set();
  function encode(item, depth) {
    if (depth > 32) reject('JSON depth budget');
    if (item === null || typeof item === 'boolean' || typeof item === 'string') return JSON.stringify(item);
    if (typeof item === 'number' && Number.isFinite(item)) return JSON.stringify(item);
    if (!Array.isArray(item) && !plain(item)) reject('plain JSON required');
    if (seen.has(item)) reject('cyclic input');
    seen.add(item);
    try {
      const entries = Object.getOwnPropertyDescriptors(item);
      if (Object.values(entries).some(x => !('value' in x))) reject('accessors are not data');
      if (Object.getOwnPropertySymbols(item).length) reject('symbol keys are not JSON');
      if (Array.isArray(item)) {
        if (Object.getPrototypeOf(item) !== Array.prototype || item.length > 4096
          || Object.keys(entries).length !== item.length + 1 || Object.keys(item).length !== item.length
          || Array.from({length: item.length}, (_, i) => Object.hasOwn(item, i)).some(x => !x)) reject('dense bounded JSON array required');
        // Read the inspected data descriptors; never call methods supplied by input.
        const values = [];
        for (let i = 0; i < item.length; i++) values.push(encode(entries[i].value, depth + 1));
        return `[${values.join(',')}]`;
      }
      if (Object.keys(entries).length > 256) reject('JSON object key budget');
      return `{${Object.keys(entries).sort().map(k => `${JSON.stringify(k)}:${encode(entries[k].value, depth + 1)}`).join(',')}}`;
    } finally { seen.delete(item); }
  }
  return encode(value, 0);
}
export const fingerprint = value => createHash('sha256').update(canonical(value)).digest('hex');

/** Tiny grammar: words, ASCII spaces/tabs, and paired quotes. No expansions,
 * escapes, operators, comments, newlines or shell execution. Rejects even some
 * harmless shell strings on purpose. A real Bash parser is a different task.
 */
export function tokenizeSimple(source) {
  if (typeof source !== 'string' || source.length === 0 || source.length > 4096) reject('command length');
  if (/[\r\n\x00-\x08\x0b\x0c\x0e-\x1f\x7f\\]/u.test(source)) reject('unsupported characters');
  let quote = null, word = '', active = false;
  const words = [];
  const emit = () => { if (active) words.push(word); word = ''; active = false; };
  for (const ch of source) {
    if (quote !== null) {
      if (ch === quote) { quote = null; continue; }
      if (quote === '"' && /[$`]/u.test(ch)) reject('expansion syntax');
      word += ch; continue;
    }
    if (ch === "'" || ch === '"') { quote = ch; active = true; continue; }
    if (ch === ' ' || ch === '\t') { emit(); continue; }
    if (/[;&|<>()$`*?\[\]{}~#!]/u.test(ch)) reject('outside tiny grammar');
    word += ch; active = true;
  }
  if (quote !== null) reject('unclosed quote');
  emit();
  if (!words.length || words.length > 16) reject('argument count');
  return words;
}

/** POSIX-like namespace used ONLY inside VirtualFS. No real OS assumptions. */
export function pathParts(path) {
  if (typeof path !== 'string' || !path.startsWith('/') || path.startsWith('//')
      || /[\\\x00-\x1f\x7f]/u.test(path)) reject('absolute virtual POSIX path required');
  const parts = path.slice(1).split('/');
  if (parts.some(x => x === '.' || x === '..') || (path !== '/' && parts.some(x => x === ''))) reject('ambiguous path');
  return path === '/' ? [] : parts;
}
export function contains(root, candidate) {
  const a = pathParts(root), b = pathParts(candidate);
  return a.length <= b.length && a.every((part, index) => b[index] === part);
}

/** Fictional commands; their names deliberately cannot be sent to an OS runner.
 * Syntax: docstat [--format text|json] -- PATH
 *         doccopy [--overwrite] -- SOURCE DESTINATION
 */
export function parseTeachingCommand(source) {
  const [executable, ...argv] = tokenizeSimple(source);
  const divider = argv.indexOf('--');
  if (divider === -1) reject('explicit option terminator required');
  const flags = argv.slice(0, divider), paths = argv.slice(divider + 1);
  paths.forEach(pathParts);
  if (executable === 'docstat') {
    if (paths.length !== 1) reject('exactly one operand required');
    if (!(flags.length === 0 || (flags.length === 2 && flags[0] === '--format' && ['text', 'json'].includes(flags[1])))) reject('unknown or duplicate option');
    return Object.freeze({tool: 'docstat', version: 1, argv: Object.freeze(argv), effect: 'read', paths: Object.freeze(paths)});
  }
  if (executable === 'doccopy') {
    if (paths.length !== 2 || !(flags.length === 0 || (flags.length === 1 && flags[0] === '--overwrite'))) reject('copy grammar');
    return Object.freeze({tool: 'doccopy', version: 1, argv: Object.freeze(argv), effect: 'write', paths: Object.freeze(paths)});
  }
  reject('unknown executable');
}

/** Virtual resources only. Global revision intentionally over-invalidates:
 * it makes races observable without claiming to implement OS atomic open.
 */
export class VirtualFS {
  #links = new Map(); #revision = 0;
  get revision() { return this.#revision; }
  link(alias, target) {
    pathParts(alias); pathParts(target);
    if (alias === '/') reject('root link unsupported');
    this.#links.set(alias, target); this.#revision++;
  }
  resolve(path) {
    pathParts(path);
    const seen = new Set();
    for (let hops = 0; hops < 32; hops++) {
      if (seen.has(path)) reject('virtual link cycle');
      seen.add(path);
      const entry = [...this.#links].filter(([alias]) => contains(alias, path))
        .sort(([a], [b]) => b.length - a.length)[0];
      if (!entry) return path;
      const [alias, target] = entry;
      path = (target === '/' ? '' : target) + path.slice(alias.length) || '/';
    }
    reject('virtual link hop budget');
  }
  grant(root, mode = 'read') {
    if (!['read', 'write'].includes(mode)) reject('mode');
    return Object.freeze({requestedRoot: root, canonicalRoot: this.resolve(root), mode});
  }
  authorize(path, effect, grants, protectedRoots = []) {
    if (!['read', 'write'].includes(effect)) reject('effect');
    const target = this.resolve(path);
    if (protectedRoots.some(p => contains(this.resolve(p), target) || contains(p, path))) reject('protected resource');
    const grant = grants.find(g => this.resolve(g.requestedRoot) === g.canonicalRoot
      && contains(g.canonicalRoot, target) && (effect === 'read' || g.mode === 'write'));
    if (!grant) reject('no current resource grant');
    return Object.freeze({requestedPath: path, canonicalPath: target, effect, revision: this.#revision});
  }
  validateTicket(ticket) {
    if (ticket.revision !== this.#revision || this.resolve(ticket.requestedPath) !== ticket.canonicalPath) reject('resource changed');
    return true;
  }
}

/** A host boundary must keep trustedUiConfirm away from model/tool code.
 * Possession of text {source:'user'} never obtains that reference.
 * Tokens are process-local opaque objects, not transferable authentication.
 */
export function createApprovalBoundary({now = () => Date.now()} = {}) {
  let context = Object.freeze({session: 'demo', generation: 1, policyRevision: 1});
  const pending = new Map();
  function scoped(plan) { return {context, plan}; }
  return {
    setContext(next) {
      if (!plain(next) || typeof next.session !== 'string'
        || !Number.isSafeInteger(next.generation) || next.generation < 1
        || !Number.isSafeInteger(next.policyRevision) || next.policyRevision < 1) reject('context shape');
      context = Object.freeze({...next}); pending.clear();
    },
    trustedUiConfirm(plan, {ttlMs = 1000, decision = 'allow'} = {}) {
      if (decision !== 'allow') reject('no affirmative decision');
      if (!Number.isSafeInteger(ttlMs) || ttlMs < 1 || ttlMs > 60000) reject('expiry');
      const time = now(), expires = time + ttlMs;
      if (!Number.isFinite(time) || !Number.isFinite(expires) || expires <= time) reject('invalid approval clock');
      const token = Object.freeze({});
      pending.set(token, {digest: fingerprint(scoped(plan)), expires});
      return token;
    },
    consume(token, plan) {
      const saved = pending.get(token);
      pending.delete(token); // every attempt consumes this one-use ticket
      if (!saved) reject('unknown, revoked or already consumed');
      const time = now();
      if (!Number.isFinite(time) || time >= saved.expires) reject('approval expired or clock invalid');
      if (fingerprint(scoped(plan)) !== saved.digest) reject('approved inputs changed');
      return Object.freeze({kind: 'authorized-plan', digest: saved.digest});
    },
    observeExternal(text, provenance) {
      if (typeof text !== 'string' || typeof provenance !== 'string') reject('observation shape');
      return Object.freeze({kind: 'untrusted-observation', text, provenance});
    },
    cancel(token) { return pending.delete(token); },
  };
}

/** Navigation policy for the lab: HTTPS only, no userinfo, no hidden controls,
 * explicit base origin, exact origin membership, no automatic remote images.
 * Does not fetch, follow redirects, resolve DNS, or implement SSRF defense.
 */
export function decideUrl(raw, {base = 'https://app.example.test/', trustedOrigins = [], purpose = 'navigate'} = {}) {
  if (!['navigate', 'image'].includes(purpose) || typeof raw !== 'string' || !raw
    || raw !== raw.trim() || /[\x00-\x20\x7f\\\p{Cf}]/u.test(raw)) return {decision: 'deny', reason: 'ambiguous input'};
  let url, baseUrl;
  try { baseUrl = new URL(base); url = new URL(raw, baseUrl); }
  catch { return {decision: 'deny', reason: 'invalid URL'}; }
  if (baseUrl.protocol !== 'https:' || baseUrl.username || baseUrl.password) return {decision: 'deny', reason: 'invalid trusted base'};
  if (url.protocol !== 'https:' || url.username || url.password) return {decision: 'deny', reason: 'scheme or userinfo'};
  const result = {url: url.href, origin: url.origin, hostname: url.hostname};
  if (url.hostname.split('.').some(label => label.startsWith('xn--'))) return {...result, decision: 'ask', reason: 'internationalized host'};
  if (purpose === 'image' && url.origin !== baseUrl.origin) return {...result, decision: 'ask', reason: 'remote resource load'};
  const trusted = url.origin === baseUrl.origin || trustedOrigins.includes(url.origin);
  return {...result, decision: trusted ? 'allow' : 'ask', reason: trusted ? 'exact origin' : 'external origin'};
}

/** These are mutually different preview contracts, not an HTML sanitizer. */
export function previewContract(kind) {
  if (kind === 'text') return Object.freeze({render: 'textContent', scripts: false, network: false});
  if (kind === 'svg-image') return Object.freeze({render: 'img', scripts: false, network: 'outer-image-request', requirement: 'validated image source and browser image mode'});
  if (kind === 'interactive') return Object.freeze({render: 'separate-origin iframe', scripts: true, network: 'explicit CSP/egress policy', broker: 'schema + origin/source + content epoch + per-capability authorization'});
  reject('unknown preview contract');
}

/** A fail-closed ORIGINAL policy; intentionally stricter than observed fallback.
 * The injected provider must be a trusted adapter. No crypto is implemented here.
 */
export function prepareSensitiveSave(value, provider) {
  if (typeof value !== 'string') return {status: 'blocked', reason: 'unsupported sensitive type'};
  if (!provider || provider.backend === 'basic_text' || !provider.available) return {status: 'blocked', reason: 'secure backend unavailable'};
  try {
    const ciphertext = provider.encrypt(value);
    if (typeof ciphertext !== 'string' || !ciphertext || ciphertext === value) return {status: 'blocked', reason: 'invalid encryption result'};
    return {status: 'ready', backend: provider.backend, ciphertext};
  } catch { return {status: 'blocked', reason: 'encryption failed'}; }
}

/** Compile a command into an immutable resource plan before showing approval.
 * Grants/protectedRoots are host-owned inputs, never model-supplied authority.
 */
export function buildPlan(fs, source, grants, protectedRoots = []) {
  const command = parseTeachingCommand(source);
  const resources = command.paths.map((path, index) => fs.authorize(path,
    command.tool === 'doccopy' && index === 1 ? 'write' : 'read', grants, protectedRoots));
  return Object.freeze({namespace: 'virtual-posix-v1', command, resources: Object.freeze(resources)});
}
