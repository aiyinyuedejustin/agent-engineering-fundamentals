"""Original, offline-only task-event validator and cohort aggregator.
No network, telemetry SDK, target code, or production endpoint is used.
Identifiers in this lab must be synthetic or purpose-scoped pseudonyms.
"""
from __future__ import annotations
from collections import defaultdict
from math import ceil, isfinite
import json
import re
import sys

NAMES = {'task_submitted', 'attempt_started', 'first_output_visible',
         'attempt_finished', 'task_closed', 'value_confirmed'}
BASE = {'schema_version', 'event_id', 'name', 'time_ms', 'user_id', 'task_id',
        'consent', 'sample_probability', 'properties'}
PROPS = {
    'task_submitted': {'eligible', 'surface'},
    'attempt_started': {'attempt_id'},
    'first_output_visible': {'attempt_id'},
    'attempt_finished': {'attempt_id', 'outcome'},
    'task_closed': {'outcome'},
    'value_confirmed': {'method'},
}
TOKEN = re.compile(r'[A-Za-z0-9_-]{1,64}\Z')

class ContractError(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise ContractError(reason)

def valid_event(event):
    """Reject unknown fields rather than accidentally accepting prompt text."""
    require(isinstance(event, dict), 'event must be object')
    require(set(event) == BASE, 'missing or unknown top-level field')
    require(type(event['schema_version']) is int and event['schema_version'] == 1,
            'unsupported schema version')
    require(isinstance(event['name'], str) and event['name'] in NAMES, 'unknown event name')
    for key in ('event_id', 'user_id', 'task_id'):
        require(isinstance(event[key], str) and TOKEN.fullmatch(event[key]),
                'invalid identifier')
    require(type(event['time_ms']) is int and event['time_ms'] >= 0,
            'time must be nonnegative integer milliseconds')
    require(type(event['consent']) is bool, 'consent must be boolean')
    probability = event['sample_probability']
    require(type(probability) in (int, float) and isfinite(probability)
            and probability == 1, 'lab requires complete unsampled task cohort')
    props = event['properties']
    require(isinstance(props, dict) and set(props) == PROPS[event['name']],
            'missing or unknown property')
    if 'attempt_id' in props:
        require(isinstance(props['attempt_id'], str)
                and TOKEN.fullmatch(props['attempt_id']), 'invalid attempt id')
    if 'eligible' in props:
        require(type(props['eligible']) is bool, 'eligible must be boolean')
        require(props['surface'] in ('chat', 'agent'), 'unknown surface')
    if 'outcome' in props:
        require(isinstance(props['outcome'], str) and props['outcome'] in ('success', 'failure', 'cancelled'),
                'unknown outcome')
    if 'method' in props:
        require(props['method'] in ('explicit_user', 'verified_delivery'),
                'unknown value confirmation method')
    return event

def percentile_nearest_rank(values, p):
    """Descriptive quantile, not a confidence interval; empty is None."""
    if not values:
        return None
    values = sorted(values)
    return values[max(0, ceil(len(values) * p) - 1)]

def aggregate(events, *, as_of_ms, horizon_ms=600_000):
    require(type(as_of_ms) is int and as_of_ms >= 0, 'invalid analysis clock')
    require(type(horizon_ms) is int and horizon_ms > 0, 'invalid horizon')
    unique, counters = {}, defaultdict(int)
    for raw in events:
        e = valid_event(raw)
        # A producer must keep event_id stable across a delivery retry.
        identity = (e['user_id'], e['event_id'])
        if identity in unique:
            require(unique[identity] == e, 'conflicting event_id reuse')
            counters['duplicate_deliveries'] += 1
            continue
        unique[identity] = e
    tasks = defaultdict(list)
    for e in unique.values():
        if e['time_ms'] > as_of_ms:
            counters['future_events'] += 1
            continue
        if not e['consent']:
            counters['nonconsenting_events'] += 1
            continue
        tasks[e['user_id'], e['task_id']].append(e)
    ttfo, completion, units = [], [], []
    for key, rows in sorted(tasks.items()):
        starts = [e for e in rows if e['name'] == 'task_submitted']
        if not starts:
            counters['orphan_tasks'] += 1
            continue
        # Two distinct submissions for the same logical task are ambiguous.
        if len(starts) != 1:
            counters['quarantined_tasks'] += 1
            continue
        start = starts[0]
        if not start['properties']['eligible']:
            counters['ineligible_tasks'] += 1
            continue
        stop = start['time_ms'] + horizon_ms
        if stop > as_of_ms:
            counters['right_censored_tasks'] += 1
            continue
        window = [e for e in rows if start['time_ms'] <= e['time_ms'] <= stop]
        counters['events_before_start'] += sum(e['time_ms'] < start['time_ms'] for e in rows)
        counters['events_after_horizon'] += sum(e['time_ms'] > stop for e in rows)
        closed = [e for e in window if e['name'] == 'task_closed']
        outcomes = {e['properties']['outcome'] for e in closed}
        if len(outcomes) > 1:
            counters['quarantined_tasks'] += 1
            continue
        # A single logical close may be repeated under different event IDs.
        terminal = min(closed, key=lambda e: e['time_ms']) if closed else None
        outcome = terminal['properties']['outcome'] if terminal else 'unknown'
        visible = [e for e in window if e['name'] == 'first_output_visible'
                   and (terminal is None or e['time_ms'] <= terminal['time_ms'])]
        confirmations = [e for e in window if e['name'] == 'value_confirmed'
                         and terminal and e['time_ms'] >= terminal['time_ms']]
        success = outcome == 'success'
        value = success and bool(confirmations)
        if visible:
            ttfo.append(min(e['time_ms'] for e in visible) - start['time_ms'])
        if success:
            completion.append(terminal['time_ms'] - start['time_ms'])
        attempts = {e['properties']['attempt_id'] for e in window
                    if e['name'] == 'attempt_started'}
        units.append({'key': key, 'visible': bool(visible), 'success': success,
                      'value': value, 'outcome': outcome, 'attempts': len(attempts)})
    n = len(units)
    counts = {k: sum(u[k] for u in units) for k in ('visible', 'success', 'value')}
    sequential = {
        'submitted': n,
        'visible': counts['visible'],
        'visible_and_success': sum(u['visible'] and u['success'] for u in units),
        'visible_success_and_value': sum(u['visible'] and u['success'] and u['value'] for u in units),
    }
    return {
        'denominator': n,
        'marginal_counts': counts,
        'marginal_rates': {k: (v / n if n else None) for k, v in counts.items()},
        'sequential_funnel': sequential,
        'outcomes': {k: sum(u['outcome'] == k for u in units)
                     for k in ('success', 'failure', 'cancelled', 'unknown')},
        'retry_task_count': sum(u['attempts'] > 1 for u in units),
        'ttfo_observed_count': len(ttfo),
        'ttfo_p50_ms': percentile_nearest_rank(ttfo, .5),
        'ttfo_p95_ms': percentile_nearest_rank(ttfo, .95),
        'completion_observed_count': len(completion),
        'completion_p95_ms': percentile_nearest_rank(completion, .95),
        'quality': dict(sorted(counters.items())),
        'limitations': ['No population extrapolation from consented traffic',
                       'Unknown outcome is not an observed failure',
                       'Quantiles describe observed output/completion only',
                       'No causal lift or confidence intervals are computed'],
    }

if __name__ == '__main__':
    # Explicit cutoff makes repeated analyses reproducible.
    require(len(sys.argv) == 3, 'usage: metrics_lab.py events.jsonl AS_OF_MS')
    with open(sys.argv[1], encoding='utf8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    print(json.dumps(aggregate(rows, as_of_ms=int(sys.argv[2])), indent=2))
