/**
 * Original teaching model. No extracted code; no browser or network access.
 * `selectVersion` and `renderPlan` restate observed client policies.
 * ContentEpoch and inspectInbound are deliberately smaller educational
 * designs. They are not a compatible implementation of Claude's protocol.
 */
export const ArtifactType = Object.freeze({
  text: 'text/plain', markdown: 'text/markdown', html: 'text/html',
  code: 'application/vnd.ant.code', svg: 'image/svg+xml',
  mermaid: 'application/vnd.ant.mermaid', react: 'application/vnd.ant.react'
});

export function isCurrentArtifactStreaming({ chatStreaming, versions,
  latestHasServerRecord }) {
  return Boolean(chatStreaming && !versions.at(-1)?.closed &&
    !latestHasServerRecord);
}

export function selectVersion(versions, selection, currentStreaming) {
  if (versions.length === 0) return 0;
  const last = versions.length - 1;
  if (currentStreaming ||
      selection.messageId?.startsWith('new-assistant-message-uuid')) return last;
  for (const [field, requested] of [
    ['uuid', selection.versionId],
    ['toolUseId', selection.toolUseId],
    ['messageId', selection.messageId]
  ]) {
    if (!requested) continue;
    const index = versions.findIndex(version => version[field] === requested);
    if (index >= 0) return index;
  }
  return last;
}

export function renderPlan(type, viewing, currentStreaming) {
  const { text, markdown, code, html, react, svg, mermaid } = ArtifactType;
  const rich = new Set([html, react, svg, mermaid]);
  const canPreview = type !== text && !(currentStreaming && rich.has(type));
  const sourceVisible = !canPreview || viewing === 'raw';
  const toggleVisible = canPreview && ![text, markdown, code].includes(type);
  return {
    renderer: sourceVisible || type === code ? 'source'
      : type === markdown ? 'markdown' : 'sandbox',
    sourceVisible, toggleVisible,
    refreshVisible: !sourceVisible && [html, react].includes(type),
    keepSandboxMounted: ![code, markdown].includes(type)
  };
}

export class ContentEpoch {
  #epoch = 0;
  #current;
  #accepted = false;
  replace(type, content) {
    // Reposting the identical, already acknowledged body need not revoke it.
    // Reposting an unacknowledged body still creates a new delivery epoch.
    const alreadyAcknowledged = this.#accepted &&
      this.#current?.type === type && this.#current?.content === content;
    if (!alreadyAcknowledged) {
      this.#epoch += 1;
      this.#accepted = false;
    }
    this.#current = { type, content };
    return { epoch: this.#epoch, ...this.#current };
  }
  acknowledge(ticket, success) {
    if (!success || ticket.epoch !== this.#epoch) return false;
    if (ticket.type !== this.#current?.type ||
        ticket.content !== this.#current?.content) return false;
    this.#accepted = true;
    return true;
  }
  receipt() {
    return { epoch: this.#epoch, accepted: this.#accepted };
  }
  mayUseCapability(receipt) {
    return this.#accepted && receipt.accepted && receipt.epoch === this.#epoch;
  }
  refresh() {
    this.#epoch += 1;
    this.#accepted = false;
  }
}

/** Window-message teaching path only. This is not a MessagePort validator.
 * The real protocol also has per-method schemas, rate limits and permissions.
 */
export function inspectInbound(event, { expectedOrigin, expectedSource,
  knownMethods, isPayloadValid }) {
  if (event.origin !== expectedOrigin || event.source !== expectedSource)
    return { accepted: false, reason: 'wrong-window-or-origin' };
  const value = event.data;
  if (!value || typeof value !== 'object' || value.channel !== 'request' ||
      typeof value.requestId !== 'string' || !knownMethods.has(value.method))
    return { accepted: false, reason: 'bad-envelope' };
  if (!isPayloadValid(value.method, value.payload))
    return { accepted: false, reason: 'bad-payload' };
  return { accepted: true, request: value };
}

export function changeViewerMode(state, nextMode) {
  if (!['dialog', 'fullscreen', 'minimized'].includes(nextMode))
    throw new TypeError('Unknown viewer mode');
  if (nextMode === state.mode) return state;
  return {
    mode: nextMode,
    restoreMode: nextMode === 'minimized' && state.mode !== 'minimized'
      ? state.mode : state.restoreMode
  };
}

/** Defensive recommendation, not a claim about recovered client behavior.
 * This limits waiting; it does not cancel the underlying operation.
 */
export async function withDeadline(work, timeoutMs) {
  let timer;
  try {
    return await Promise.race([
      work,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('Renderer deadline exceeded')),
          timeoutMs);
      })
    ]);
  } finally { clearTimeout(timer); }
}
