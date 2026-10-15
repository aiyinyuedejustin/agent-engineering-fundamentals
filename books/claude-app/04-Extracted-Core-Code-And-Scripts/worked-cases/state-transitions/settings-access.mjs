/** Original case adapter. Identity is caller-supplied; this is not authorization. */
import { LatestRequestGuard, decideAccess, resolveFreshAccess } from './original-models.mjs';
export { ScopedMutationQueue, applyQueuedOptimistic } from './original-models.mjs';

export class ScopedAccessView {
  #guard = new LatestRequestGuard();
  constructor(org, snapshot) { this.org = org; this.snapshot = snapshot; }
  switchOrg(org) {
    this.#guard.invalidate();
    this.org = org;
    this.snapshot = undefined; // Do not present another organization's allow.
  }
  beginRead() { return { org: this.org, ...this.#guard.begin() }; }
  receive(ticket, reply, checkedAt) {
    if (!ticket.isCurrent()) return { accepted: false, reason: 'stale-generation' };
    if (ticket.org !== this.org || reply.org !== ticket.org)
      return { accepted: false, reason: 'scope-mismatch' };
    this.snapshot = { org: ticket.org, checkedAt, ...decideAccess(reply) };
    return { accepted: true, ...this.snapshot };
  }
  async mayStartAction(now, maxAge, refresh) {
    const ticket = this.beginRead();
    const snapshot = this.snapshot?.org === ticket.org ? this.snapshot : undefined;
    const allowed = await resolveFreshAccess(snapshot, now, maxAge, async () => {
      const reply = await refresh(ticket.org);
      const result = this.receive(ticket, reply, now);
      return result.accepted ? this.snapshot : { allowed: false };
    });
    // Recheck after await even if the helper reused a fresh cached result.
    return ticket.isCurrent() && ticket.org === this.org && allowed;
  }
}

export function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
export const turn = () => new Promise(resolve => setImmediate(resolve));
