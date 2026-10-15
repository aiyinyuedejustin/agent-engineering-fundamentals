"""Original, offline-only task-event validator and cohort aggregator.
No network, telemetry SDK, target code, or production endpoint is used.
Identifiers in this lab must be synthetic or purpose-scoped pseudonyms.
"""
from __future__ import annotations
from collections import defaultdict
from math import ceil
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
    require(type(probability) in (int, float) and probability == 1, 'lab requires complete unsampled task cohort')
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

def inspect_chronology(window, counters):
    """Check observed contradictions, without inventing missing attempt events.

    A task close ends execution and visible-output activity. Its business timestamp
    and outcome are immutable, including when re-emitted with a new event ID.
    Equality is allowed because millisecond timestamps do not establish tie order.
    Attempt finishes describe execution, so output can become visible afterwards,
    provided that it is no later than the task close.
    """
    reasons = set()
    closes = [e for e in window if e['name'] == 'task_closed']
    close_signatures = {(e['time_ms'], e['properties']['outcome']) for e in closes}
    if len(close_signatures) > 1:
        reasons.add('conflicting_task_closes')
    counters['logical_close_duplicates'] += len(closes) - len(close_signatures)
    terminal = min(closes, key=lambda e: (e['time_ms'], e['properties']['outcome'])) if closes else None
    attempts = defaultdict(lambda: {'starts': [], 'finishes': [], 'visible': []})
    phase = {'attempt_started': 'starts', 'attempt_finished': 'finishes',
             'first_output_visible': 'visible'}
    for e in window:
        if e['name'] not in phase:
            continue
        attempts[e['properties']['attempt_id']][phase[e['name']]].append(e)
        if terminal and e['time_ms'] > terminal['time_ms']:
            reasons.add('activity_after_task_close')
    for evidence in attempts.values():
        starts = {e['time_ms'] for e in evidence['starts']}
        finishes = {(e['time_ms'], e['properties']['outcome']) for e in evidence['finishes']}
        counters['logical_attempt_start_duplicates'] += len(evidence['starts']) - len(starts)
        counters['logical_attempt_finish_duplicates'] += len(evidence['finishes']) - len(finishes)
        if len(starts) > 1:
            reasons.add('conflicting_attempt_starts')
        if len(finishes) > 1:
            reasons.add('conflicting_attempt_finishes')
        if starts and any(e['time_ms'] < min(starts)
                          for e in evidence['finishes'] + evidence['visible']):
            reasons.add('attempt_activity_before_start')
    return reasons, terminal, attempts


def aggregate(events, *, as_of_ms, horizon_ms=600_000):
    require(type(as_of_ms) is int and as_of_ms >= 0, 'invalid analysis clock')
    require(type(horizon_ms) is int and horizon_ms > 0, 'invalid horizon')
    unique, counters, quarantine_reasons = {}, defaultdict(int), defaultdict(int)
    for raw in events:
        e = valid_event(raw)
        # A producer must keep event_id and its entire envelope stable on retry.
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
        tasks[e['user_id'], e['task_id']].append(e)
        if not e['consent']:
            counters['nonconsenting_events'] += 1

    # These mutually exclusive buckets reconcile all observed task keys. Only
    # uniquely anchored, mature, eligible, fully consented tasks enter candidates.
    cohort = {k: 0 for k in ('observed_task_keys', 'excluded_consent_tasks',
              'orphan_tasks', 'ambiguous_submission_tasks', 'ineligible_tasks',
              'right_censored_tasks', 'mature_eligible_consented_tasks',
              'included_tasks', 'quarantined_mature_eligible_tasks')}
    cohort['observed_task_keys'] = len(tasks)
    coverage = {k: 0 for k in ('observed_attempt_ids', 'attempt_ids_with_start',
                'attempt_ids_with_finish', 'attempt_ids_missing_start',
                'attempt_ids_missing_finish', 'tasks_without_attempt_evidence')}
    ttfo, completion, units = [], [], []
    for key, rows in sorted(tasks.items()):
        consent_states = {e['consent'] for e in rows}
        if False in consent_states:
            # Do not reconstruct a partial cohort from the consent=True subset.
            # Inspect no eligibility or outcome from this excluded task.
            counters['mixed_consent_tasks' if True in consent_states else 'nonconsenting_tasks'] += 1
            cohort['excluded_consent_tasks'] += 1
            continue
        starts = [e for e in rows if e['name'] == 'task_submitted']
        if not starts:
            counters['orphan_tasks'] += 1
            cohort['orphan_tasks'] += 1
            continue
        # Two distinct submissions cannot establish an unambiguous cohort anchor.
        if len(starts) != 1:
            counters['quarantined_tasks'] += 1
            quarantine_reasons['ambiguous_submission'] += 1
            cohort['ambiguous_submission_tasks'] += 1
            continue
        start = starts[0]
        if not start['properties']['eligible']:
            counters['ineligible_tasks'] += 1
            cohort['ineligible_tasks'] += 1
            continue
        stop = start['time_ms'] + horizon_ms
        if stop > as_of_ms:
            counters['right_censored_tasks'] += 1
            cohort['right_censored_tasks'] += 1
            continue
        cohort['mature_eligible_consented_tasks'] += 1
        before_start = sum(e['time_ms'] < start['time_ms'] for e in rows)
        counters['events_before_start'] += before_start
        counters['events_after_horizon'] += sum(e['time_ms'] > stop for e in rows)
        window = [e for e in rows if start['time_ms'] <= e['time_ms'] <= stop]
        reasons, terminal, attempt_evidence = inspect_chronology(window, counters)
        if before_start:
            reasons.add('event_before_task_submission')
        if reasons:
            counters['quarantined_tasks'] += 1
            cohort['quarantined_mature_eligible_tasks'] += 1
            for reason in reasons:
                quarantine_reasons[reason] += 1
            continue

        outcome = terminal['properties']['outcome'] if terminal else 'unknown'
        visible = [e for e in window if e['name'] == 'first_output_visible']
        # A confirmation is a signal, not authority to synthesize success/close.
        # Early/unattributable signals remain explicit diagnostics, not credits.
        signals = [e for e in window if e['name'] == 'value_confirmed']
        confirmations = [e for e in signals if terminal and outcome == 'success'
                         and e['time_ms'] >= terminal['time_ms']]
        counters['uncredited_value_confirmations'] += len(signals) - len(confirmations)
        success = outcome == 'success'
        value = success and bool(confirmations)
        if visible:
            ttfo.append(min(e['time_ms'] for e in visible) - start['time_ms'])
        if success:
            completion.append(terminal['time_ms'] - start['time_ms'])
        started_attempts = sum(bool(evidence['starts']) for evidence in attempt_evidence.values())
        finished_attempts = sum(bool(evidence['finishes']) for evidence in attempt_evidence.values())
        coverage['observed_attempt_ids'] += len(attempt_evidence)
        coverage['attempt_ids_with_start'] += started_attempts
        coverage['attempt_ids_with_finish'] += finished_attempts
        coverage['attempt_ids_missing_start'] += len(attempt_evidence) - started_attempts
        coverage['attempt_ids_missing_finish'] += len(attempt_evidence) - finished_attempts
        coverage['tasks_without_attempt_evidence'] += not bool(attempt_evidence)
        units.append({'key': key, 'visible': bool(visible), 'success': success,
                      'value': value, 'outcome': outcome, 'attempts': started_attempts})
    n = len(units)
    cohort['included_tasks'] = n
    candidates = cohort['mature_eligible_consented_tasks']
    quarantined = cohort['quarantined_mature_eligible_tasks']
    counts = {k: sum(u[k] for u in units) for k in ('visible', 'success', 'value')}
    outcomes = {k: sum(u['outcome'] == k for u in units)
                for k in ('success', 'failure', 'cancelled', 'unknown')}
    # Worst-case outcome assignments for this fixed candidate cohort, not a
    # statistical interval or a correction for missing/consent-excluded tasks.
    uncertain = quarantined + outcomes['unknown']
    cohort['quarantine_fraction_of_candidates'] = quarantined / candidates if candidates else None
    sensitivity = {
        'denominator': candidates,
        'confirmed_successes': counts['success'],
        'uncertain_outcomes': uncertain,
        'lower': counts['success'] / candidates if candidates else None,
        'upper': (counts['success'] + uncertain) / candidates if candidates else None,
    }
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
        'outcomes': outcomes,
        'retry_task_count': sum(u['attempts'] > 1 for u in units),
        'ttfo_observed_count': len(ttfo),
        'ttfo_p50_ms': percentile_nearest_rank(ttfo, .5),
        'ttfo_p95_ms': percentile_nearest_rank(ttfo, .95),
        'completion_observed_count': len(completion),
        'completion_p95_ms': percentile_nearest_rank(completion, .95),
        'cohort_accounting': cohort,
        'success_fraction_sensitivity': sensitivity,
        'attempt_coverage': coverage,
        'quality': dict(sorted(counters.items())),
        'quarantine_reasons': dict(sorted(quarantine_reasons.items())),
        'limitations': ['No population extrapolation from consented traffic',
                       'Unknown outcome is not an observed failure',
                       'Quantiles describe observed output/completion only',
                       'Retry count means multiple observed attempt starts, not verified sequential retries',
                       'Missing attempt events are diagnosed, not reconstructed',
                       'Sensitivity bounds cover candidates only, not consent exclusions or missing submissions',
                       'No causal lift or confidence intervals are computed'],
    }

if __name__ == '__main__':
    # Explicit cutoff makes repeated analyses reproducible.
    require(len(sys.argv) in (3, 4), 'usage: metrics_lab.py events.jsonl AS_OF_MS [HORIZON_MS]')
    with open(sys.argv[1], encoding='utf8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    horizon = int(sys.argv[3]) if len(sys.argv) == 4 else 600_000
    print(json.dumps(aggregate(rows, as_of_ms=int(sys.argv[2]), horizon_ms=horizon), indent=2))
