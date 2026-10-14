/** Original event reducer and coalesced delivery, based on documented mechanisms.
 * The teaching model intentionally implements a small named event subset. */
const lateDeltas = new Set(['thinking_summary_delta', 'tool_use_block_update_delta']);
const copy = value => structuredClone(value);

export class ContentReducer {
  blocks = [];
  done = false;
  stopReason = null;
  #offset = 0;
  #serverBase = null;
  #active = null;
  #pending = false;
  #revision = 0;

  constructor(onSnapshot = () => {}, { schedule = queueMicrotask } = {}) {
    this.onSnapshot = onSnapshot;
    this.schedule = schedule;
  }

  #local(index) { return this.#offset + index - (this.#serverBase ?? 0); }
  #deliverLater() {
    if (this.#pending) return;
    this.#pending = true;
    const revision = this.#revision;
    this.schedule(() => { if (revision === this.#revision) this.flush(); });
  }
  flush() {
    if (!this.#pending) return;
    this.#pending = false;
    this.onSnapshot({ blocks: copy(this.blocks), done: this.done, stopReason: this.stopReason });
  }

  apply(event) {
    switch (event.type) {
      case 'message_start':
        this.done = false;
        this.stopReason = null;
        this.#offset = this.blocks.length;
        this.#serverBase = null;
        this.#active = null;
        break;
      case 'content_block_start': {
        if (!Number.isInteger(event.index) || event.index < 0) throw new Error('Invalid block index');
        this.#serverBase ??= event.index;
        if (this.#local(event.index) !== this.blocks.length) throw new Error('Non-contiguous block start');
        this.#active = event.index;
        const block = copy(event.content_block);
        if (block.type === 'text') block.text ??= '';
        if (block.type === 'thinking') block.thinking ??= '';
        this.blocks.push(block);
        break;
      }
      case 'content_block_delta': {
        if (event.index !== this.#active && !lateDeltas.has(event.delta.type)) {
          throw new Error('Delta does not target the active block');
        }
        const block = this.blocks[this.#local(event.index)];
        if (!block) throw new Error('Delta targets a missing block');
        const delta = event.delta;
        if (delta.type === 'flag_delta') {
          block.flags = [...new Set([...(block.flags ?? []), delta.flag])];
        } else if (block.type === 'text' && delta.type === 'text_delta') block.text += delta.text;
        else if (block.type === 'connector_text' && delta.type === 'connector_text_delta') {
          block.connector_text = (block.connector_text ?? '') + delta.connector_text;
        } else if (block.type === 'thinking' && delta.type === 'thinking_delta') block.thinking += delta.thinking;
        else if (block.type === 'thinking' && delta.type === 'thinking_summary_delta') {
          (block.summaries ??= []).push(copy(delta.summary));
        } else if (block.type === 'thinking' && delta.type === 'thinking_cut_off_delta') block.cut_off = delta.cut_off;
        else if (block.type === 'tool_use' && delta.type === 'input_json_delta') {
          block.partial_json = (block.partial_json ?? '') + delta.partial_json;
        } else if (block.type === 'tool_use' && delta.type === 'tool_use_block_update_delta') {
          for (const key of ['message', 'display_content']) {
            if (delta[key] !== undefined) block[key] = copy(delta[key]);
          }
        } else if (block.type === 'tool_result' && delta.type === 'input_json_delta') {
          try {
            const value = JSON.parse(delta.partial_json);
            block.content = Array.isArray(value) && value.length && value.every(v => v && typeof v === 'object' && 'type' in v)
              ? value : [{ type: 'text', text: delta.partial_json }];
          } catch { block.content = [{ type: 'text', text: delta.partial_json }]; }
        }
        break;
      }
      case 'content_block_stop': {
        if (event.index !== this.#active) throw new Error('Stop does not target the active block');
        const block = this.blocks[this.#local(event.index)];
        if (!block) throw new Error('Stop targets a missing block');
        if (block.type === 'text') block.stopped = true;
        if (block.type === 'thinking') {
          block.stop_timestamp = event.stop_timestamp;
          if (typeof event.summary_pending === 'boolean') block.summary_pending = event.summary_pending;
        }
        if (block.type === 'tool_use') {
          block.buffered_input = event.buffered_input ?? '{}';
          // Teaching simplification: retain incomplete JSON; never execute it and
          // only promote fully parseable JSON. The inspected client is tolerant.
          try { block.parsed_input = JSON.parse(block.partial_json ?? '{}'); } catch {}
        }
        break;
      }
      case 'content_block_retract': {
        const local = this.#local(event.from_index);
        if (local < 0 || local > this.blocks.length) throw new Error('Invalid retraction');
        this.blocks = this.blocks.slice(0, local);
        this.#offset = this.blocks.length;
        this.#serverBase = null;
        this.#active = null;
        break;
      }
      case 'message_delta': this.stopReason = event.delta.stop_reason ?? this.stopReason; break;
      case 'message_stop': this.done = true; break;
      case 'ping': return;
      default: return; // Explicit subset, not a complete server contract.
    }
    this.#deliverLater();
  }

  restart() {
    this.#revision += 1; // Old queued microtasks must not flush the new generation.
    this.blocks = [];
    this.done = false;
    this.stopReason = null;
    this.#offset = 0;
    this.#serverBase = null;
    this.#active = null;
    this.#pending = false;
  }
}
