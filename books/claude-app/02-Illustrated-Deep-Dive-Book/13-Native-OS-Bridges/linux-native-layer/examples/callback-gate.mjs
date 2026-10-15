/**
 * Original teaching model. JS-owner-thread gate, not a native thread queue.
 * Payloads must already be copied/owned by JS. No target import or real fd.
 * schedule must enqueue asynchronously. deliver and onError are synchronous.
 * Capacity bounds waiting items, not bytes or a native producer's queue.
 * Scheduler failure closes the gate; reporter failure is counted, not thrown.
 */
export function createCallbackGate({
  deliver, onError = () => {}, capacity = 4, schedule = queueMicrotask,
}) {
  if (!Number.isSafeInteger(capacity) || capacity < 1) {
    throw new RangeError('capacity must be a positive safe integer');
  }
  if (typeof deliver !== 'function' || typeof onError !== 'function' ||
      typeof schedule !== 'function') throw new TypeError('callbacks required');
  let closed = false, scheduled = false, generation = 0;
  const pending = [];
  const failures = { delivery: 0, scheduler: 0, reporter: 0, discarded: 0 };
  function close() {
    if (closed) return;
    closed = true;
    generation += 1;
    pending.length = 0;
    scheduled = false;
  }
  function report(error, context) {
    try { onError(error, context); }
    catch { failures.reporter += 1; }
  }
  function arm() {
    if (closed || scheduled || pending.length === 0) return true;
    scheduled = true;
    const ticket = generation;
    try {
      schedule(() => {
        if (closed || ticket !== generation) return;
        scheduled = false;
        const value = pending.shift();
        try { deliver(value); }
        catch (error) {
          failures.delivery += 1;
          report(error, { source: 'delivery' });
        } finally { arm(); }
      });
      return true;
    } catch (error) {
      failures.scheduler += 1;
      const discarded = pending.length;
      failures.discarded += discarded;
      close(); // Also invalidates a task enqueued just before schedule threw.
      report(error, { source: 'scheduler', discarded });
      return false;
    }
  }
  return Object.freeze({
    offer(value) {
      if (closed) return 'closed';
      if (pending.length >= capacity) return 'full';
      pending.push(value);
      return arm() ? 'accepted' : 'scheduler-failed';
    },
    close,
    inspect() { return { closed, waiting: pending.length, failures: { ...failures } }; },
  });
}
