import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest
from metrics_lab import aggregate, valid_event, ContractError

def event(name, t=0, task='task1', eid=None, **props):
    defaults = {'task_submitted': {'eligible': True, 'surface': 'agent'},
                'attempt_started': {'attempt_id': 'a1'},
                'first_output_visible': {'attempt_id': 'a1'},
                'attempt_finished': {'attempt_id': 'a1', 'outcome': 'success'},
                'task_closed': {'outcome': 'success'},
                'value_confirmed': {'method': 'explicit_user'}}
    return dict(schema_version=1, event_id=eid or name+str(t)+task,
                name=name, time_ms=t, user_id='synthetic1', task_id=task,
                consent=True, sample_probability=1,
                properties={**defaults[name], **props})

def run(rows, cutoff=2000, horizon=1000):
    return aggregate(rows, as_of_ms=cutoff, horizon_ms=horizon)

class MetricsTests(unittest.TestCase):
    def test_success_value(self):
        r=run([event('task_submitted'), event('first_output_visible',100),
               event('task_closed',500), event('value_confirmed',600)])
        self.assertEqual(r['marginal_rates'], dict(visible=1, success=1, value=1))
        self.assertEqual(r['ttfo_p95_ms'],100)
    def test_delivery_retry_deduplicated(self):
        e=event('task_submitted'); r=run([e,copy.deepcopy(e)])
        self.assertEqual(r['denominator'],1)
        self.assertEqual(r['quality']['duplicate_deliveries'],1)
    def test_conflicting_id_rejected(self):
        a=event('task_submitted'); b=copy.deepcopy(a);b['time_ms']=1
        with self.assertRaises(ContractError):run([a,b])
    def test_phase_duplicates_do_not_inflate_task(self):
        r=run([event('task_submitted'),event('first_output_visible',10),event('first_output_visible',20)])
        self.assertEqual(r['marginal_counts']['visible'],1)
        self.assertEqual(r['ttfo_p50_ms'],10)
    def test_retry_denominator_is_task(self):
        r=run([event('task_submitted'),event('attempt_started',1),
               event('attempt_finished',2,outcome='failure'),
               event('attempt_started',3,attempt_id='a2'),event('task_closed',4)])
        self.assertEqual(r['denominator'],1);self.assertEqual(r['retry_task_count'],1)
    def test_censoring(self):
        r=run([event('task_submitted',1500)])
        self.assertEqual(r['denominator'],0)
        self.assertIsNone(r['marginal_rates']['success'])
        self.assertEqual(r['quality']['right_censored_tasks'],1)
    def test_unknown_is_not_failure(self):
        r=run([event('task_submitted')])
        self.assertEqual(r['outcomes']['unknown'],1);self.assertEqual(r['outcomes']['failure'],0)
    def test_cancelled_distinct(self):
        r=run([event('task_submitted'),event('task_closed',10,outcome='cancelled')])
        self.assertEqual(r['outcomes']['cancelled'],1)
    def test_after_horizon_excluded(self):
        r=run([event('task_submitted'),event('task_closed',1001)])
        self.assertEqual(r['marginal_counts']['success'],0)
    def test_boundary_included(self):
        r=run([event('task_submitted'),event('task_closed',1000)])
        self.assertEqual(r['marginal_counts']['success'],1)
    def test_out_of_order(self):
        a=[event('task_submitted'),event('first_output_visible',10),event('task_closed',30)]
        self.assertEqual(run(a),run(list(reversed(a))))
    def test_future_excluded(self):
        r=run([event('task_submitted'),event('task_closed',2100)])
        self.assertEqual(r['quality']['future_events'],1)
    def test_consent_filter(self):
        a=event('task_submitted');a['consent']=False
        self.assertEqual(run([a])['denominator'],0)
    def test_unknown_field_blocks_prompt(self):
        a=event('task_submitted');a['properties']['prompt']='DO NOT COLLECT'
        with self.assertRaises(ContractError):valid_event(a)
    def test_sampling_rejected(self):
        a=event('task_submitted');a['sample_probability']=.5
        with self.assertRaises(ContractError):valid_event(a)
    def test_nan_rejected(self):
        a=event('task_submitted');a['sample_probability']=float('nan')
        with self.assertRaises(ContractError):valid_event(a)
    def test_boolean_timestamp_rejected(self):
        a=event('task_submitted');a['time_ms']=True
        with self.assertRaises(ContractError):valid_event(a)
    def test_conflicting_terminals_quarantined(self):
        r=run([event('task_submitted'),event('task_closed',5),event('task_closed',6,outcome='failure')])
        self.assertEqual(r['denominator'],0);self.assertEqual(r['quality']['quarantined_tasks'],1)
    def test_duplicate_submissions_quarantined(self):
        r=run([event('task_submitted'),event('task_submitted',1)])
        self.assertEqual(r['quality']['quarantined_tasks'],1)
    def test_orphan(self):
        self.assertEqual(run([event('task_closed',10)])['quality']['orphan_tasks'],1)
    def test_value_requires_success_and_order(self):
        r=run([event('task_submitted'),event('value_confirmed',2),event('task_closed',3)])
        self.assertEqual(r['marginal_counts']['value'],0)
    def test_success_not_forced_into_visible_funnel(self):
        r=run([event('task_submitted'),event('task_closed',5)])
        self.assertEqual(r['marginal_counts']['success'],1)
        self.assertEqual(r['sequential_funnel']['visible_and_success'],0)
    def test_user_namespace_separates_task(self):
        a=event('task_submitted');b=copy.deepcopy(a);b['user_id']='synthetic2'
        self.assertEqual(run([a,b])['denominator'],2)
    def test_ineligible_predeclared(self):
        self.assertEqual(run([event('task_submitted',eligible=False)])['denominator'],0)
    def test_invalid_cutoff(self):
        with self.assertRaises(ContractError):run([],cutoff=True)
    def test_empty_quantiles(self):
        self.assertIsNone(run([])['ttfo_p95_ms'])

class AdversarialTests(unittest.TestCase):
    def assertQuarantined(self, rows, reason):
        r = run(rows)
        self.assertEqual(r['denominator'], 0)
        self.assertEqual(r['retry_task_count'], 0)
        self.assertEqual(r['quality']['quarantined_tasks'], 1)
        self.assertEqual(r['quarantine_reasons'][reason], 1)
        self.assertEqual(r['cohort_accounting']['quarantined_mature_eligible_tasks'], 1)
        return r

    def test_each_execution_phase_after_close_quarantines(self):
        for name in ('attempt_started', 'attempt_finished', 'first_output_visible'):
            for outcome in ('success', 'failure', 'cancelled'):
                with self.subTest(name=name, outcome=outcome):
                    self.assertQuarantined([event('task_submitted'),
                        event('attempt_started', 1), event('task_closed', 10, outcome=outcome),
                        event(name, 11, attempt_id='a2')], 'activity_after_task_close')

    def test_delayed_delivery_preserves_business_time(self):
        rows = [event('task_submitted'), event('attempt_started', 1),
                event('task_closed', 20), event('attempt_started', 10, attempt_id='a2')]
        self.assertEqual(run(rows)['retry_task_count'], 1)
        self.assertEqual(run(rows), run(list(reversed(rows))))

    def test_same_millisecond_activity_is_not_invented_order(self):
        rows = [event('task_submitted'), event('attempt_started', 10),
                event('first_output_visible', 10), event('attempt_finished', 10),
                event('task_closed', 10), event('value_confirmed', 10)]
        r = run(rows)
        self.assertEqual(r['marginal_counts'], dict(visible=1, success=1, value=1))
        self.assertEqual(r['quarantine_reasons'], {})

    def test_equal_semantic_closes_deduplicate(self):
        r = run([event('task_submitted'), event('task_closed', 10),
                 event('task_closed', 10, eid='new_delivery_id')])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['completion_p95_ms'], 10)
        self.assertEqual(r['quality']['logical_close_duplicates'], 1)

    def test_shifted_close_timestamp_is_not_silently_minimized(self):
        self.assertQuarantined([event('task_submitted'), event('task_closed', 10),
            event('task_closed', 11)], 'conflicting_task_closes')

    def test_conflicting_closes_at_same_timestamp(self):
        self.assertQuarantined([event('task_submitted'), event('task_closed', 10),
            event('task_closed', 10, eid='different_close', outcome='failure')],
            'conflicting_task_closes')

    def test_repeated_attempt_start_same_business_time(self):
        r = run([event('task_submitted'), event('attempt_started', 1),
                 event('attempt_started', 1, eid='another_start_envelope')])
        self.assertEqual(r['retry_task_count'], 0)
        self.assertEqual(r['attempt_coverage']['observed_attempt_ids'], 1)
        self.assertEqual(r['quality']['logical_attempt_start_duplicates'], 1)

    def test_attempt_id_cannot_restart_at_changed_time(self):
        self.assertQuarantined([event('task_submitted'), event('attempt_started', 1),
            event('attempt_started', 2)], 'conflicting_attempt_starts')

    def test_repeated_attempt_finish_same_business_time(self):
        r = run([event('task_submitted'), event('attempt_finished', 10),
                 event('attempt_finished', 10, eid='another_finish_envelope')])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['quality']['logical_attempt_finish_duplicates'], 1)

    def test_changed_attempt_finish_timestamp_or_outcome_quarantines(self):
        for second in (event('attempt_finished', 11),
                       event('attempt_finished', 10, eid='failed_finish', outcome='failure')):
            with self.subTest(second=second):
                self.assertQuarantined([event('task_submitted'), event('attempt_finished', 10),
                    second], 'conflicting_attempt_finishes')

    def test_observed_phase_before_its_attempt_start(self):
        for name in ('first_output_visible', 'attempt_finished'):
            with self.subTest(name=name):
                self.assertQuarantined([event('task_submitted'), event('attempt_started', 20),
                    event(name, 10)], 'attempt_activity_before_start')

    def test_render_after_attempt_execution_finish_allowed_before_task_close(self):
        r = run([event('task_submitted'), event('attempt_started', 1),
                 event('attempt_finished', 2), event('first_output_visible', 3),
                 event('task_closed', 4)])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['ttfo_p95_ms'], 3)

    def test_missing_attempt_start_diagnosed_not_invented(self):
        r = run([event('task_submitted'), event('first_output_visible', 10),
                 event('attempt_finished', 20), event('task_closed', 30)])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['retry_task_count'], 0)
        self.assertEqual(r['attempt_coverage']['attempt_ids_missing_start'], 1)
        self.assertEqual(r['attempt_coverage']['attempt_ids_missing_finish'], 0)

    def test_missing_attempt_finish_does_not_infer_failure(self):
        r = run([event('task_submitted'), event('attempt_started', 1), event('task_closed', 10)])
        self.assertEqual(r['outcomes']['success'], 1)
        self.assertEqual(r['attempt_coverage']['attempt_ids_missing_finish'], 1)

    def test_output_only_attempt_missing_both_boundaries(self):
        r = run([event('task_submitted'), event('first_output_visible', 10)])
        self.assertEqual(r['attempt_coverage']['attempt_ids_missing_start'], 1)
        self.assertEqual(r['attempt_coverage']['attempt_ids_missing_finish'], 1)
        self.assertEqual(r['outcomes']['unknown'], 1)

    def test_absent_attempt_stream_does_not_erase_task_outcome(self):
        r = run([event('task_submitted'), event('task_closed', 10)])
        self.assertEqual(r['marginal_counts']['success'], 1)
        self.assertEqual(r['attempt_coverage']['tasks_without_attempt_evidence'], 1)

    def test_unattributable_value_is_diagnosed_not_success(self):
        for close in ([], [event('task_closed', 10, outcome='failure')],
                      [event('task_closed', 10)]):
            with self.subTest(close=close):
                r = run([event('task_submitted'), event('value_confirmed', 5)] + close)
                self.assertEqual(r['denominator'], 1)
                self.assertEqual(r['marginal_counts']['value'], 0)
                self.assertEqual(r['quality']['uncredited_value_confirmations'], 1)

    def test_pre_submission_evidence_quarantines_candidate(self):
        r = self.assertQuarantined([event('task_submitted', 10),
            event('first_output_visible', 1)], 'event_before_task_submission')
        self.assertEqual(r['quality']['events_before_start'], 1)

    def test_mixed_consent_is_whole_task_exclusion(self):
        denied = event('task_closed', 10); denied['consent'] = False
        r = run([event('task_submitted'), denied])
        self.assertEqual(r['denominator'], 0)
        self.assertEqual(r['cohort_accounting']['excluded_consent_tasks'], 1)
        self.assertEqual(r['cohort_accounting']['mature_eligible_consented_tasks'], 0)
        self.assertEqual(r['quality']['mixed_consent_tasks'], 1)
        self.assertEqual(r['outcomes']['unknown'], 0)

    def test_false_submission_true_close_is_not_an_orphan(self):
        denied = event('task_submitted'); denied['consent'] = False
        r = run([denied, event('task_closed', 10)])
        self.assertEqual(r['cohort_accounting']['orphan_tasks'], 0)
        self.assertEqual(r['cohort_accounting']['excluded_consent_tasks'], 1)

    def test_all_nonconsenting_task_distinct_from_mixed(self):
        rows = [event('task_submitted'), event('task_closed', 10)]
        for e in rows: e['consent'] = False
        r = run(rows)
        self.assertEqual(r['quality']['nonconsenting_tasks'], 1)
        self.assertNotIn('mixed_consent_tasks', r['quality'])
        self.assertEqual(r['quality']['nonconsenting_events'], 2)

    def test_denied_duplicate_is_counted_once(self):
        e = event('task_submitted'); e['consent'] = False
        r = run([e, copy.deepcopy(e)])
        self.assertEqual(r['quality']['duplicate_deliveries'], 1)
        self.assertEqual(r['quality']['nonconsenting_events'], 1)

    def test_future_consent_signal_does_not_leak_into_snapshot(self):
        denied = event('attempt_started', 2100); denied['consent'] = False
        r = run([event('task_submitted'), denied])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['quality']['future_events'], 1)
        self.assertEqual(run([event('task_submitted'), denied], cutoff=2200)['denominator'], 0)

    def test_consent_exclusion_applies_even_after_metric_horizon(self):
        denied = event('attempt_started', 1500); denied['consent'] = False
        r = run([event('task_submitted'), event('task_closed', 10), denied])
        self.assertEqual(r['denominator'], 0)
        self.assertEqual(r['cohort_accounting']['excluded_consent_tasks'], 1)

    def test_post_horizon_activity_neither_counts_retry_nor_rewrites_window(self):
        r = run([event('task_submitted'), event('attempt_started', 1),
                 event('task_closed', 10), event('attempt_started', 1001, attempt_id='a2')])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['retry_task_count'], 0)
        self.assertEqual(r['quality']['events_after_horizon'], 1)

    def test_horizon_boundary_after_close_is_a_contradiction(self):
        self.assertQuarantined([event('task_submitted'), event('task_closed', 10),
            event('attempt_started', 1000)], 'activity_after_task_close')

    def test_ambiguous_submission_does_not_fabricate_candidate_anchor(self):
        r = run([event('task_submitted'), event('task_submitted', 1)])
        self.assertEqual(r['cohort_accounting']['ambiguous_submission_tasks'], 1)
        self.assertEqual(r['success_fraction_sensitivity']['denominator'], 0)
        self.assertIsNone(r['success_fraction_sensitivity']['upper'])

    def test_same_time_submission_new_id_remains_ambiguous(self):
        r = run([event('task_submitted'), event('task_submitted', eid='second_submit')])
        self.assertEqual(r['cohort_accounting']['ambiguous_submission_tasks'], 1)

    def test_quarantine_cannot_hide_denominator_inflation(self):
        r = run([event('task_submitted', task='clean'), event('task_closed', 10, task='clean'),
                 event('task_submitted', task='bad'), event('task_closed', 10, task='bad', outcome='failure'),
                 event('attempt_started', 11, task='bad')])
        self.assertEqual(r['marginal_rates']['success'], 1)
        self.assertEqual(r['cohort_accounting']['mature_eligible_consented_tasks'], 2)
        self.assertEqual(r['cohort_accounting']['quarantine_fraction_of_candidates'], .5)
        self.assertEqual(r['success_fraction_sensitivity'],
            dict(denominator=2, confirmed_successes=1, uncertain_outcomes=1, lower=.5, upper=1))

    def test_unknown_expands_sensitivity_not_observed_success(self):
        r = run([event('task_submitted')])
        self.assertEqual(r['marginal_counts']['success'], 0)
        self.assertEqual(r['success_fraction_sensitivity']['lower'], 0)
        self.assertEqual(r['success_fraction_sensitivity']['upper'], 1)

    def test_all_quarantined_returns_null_clean_rates_and_nonempty_bounds(self):
        r = self.assertQuarantined([event('task_submitted'), event('task_closed', 1),
            event('attempt_started', 2)], 'activity_after_task_close')
        self.assertIsNone(r['marginal_rates']['success'])
        self.assertEqual(r['success_fraction_sensitivity']['denominator'], 1)
        self.assertEqual(r['success_fraction_sensitivity']['upper'], 1)

    def test_multiple_reasons_count_task_once(self):
        r = self.assertQuarantined([event('task_submitted'), event('task_closed', 1),
            event('task_closed', 2, outcome='failure'), event('attempt_started', 3)],
            'activity_after_task_close')
        self.assertEqual(r['quarantine_reasons']['conflicting_task_closes'], 1)
        self.assertEqual(r['cohort_accounting']['quarantined_mature_eligible_tasks'], 1)

    def test_attempt_ids_scoped_to_task_and_user(self):
        a = [event('task_submitted', task='one'), event('attempt_started', 1, task='one')]
        b = [event('task_submitted', task='two'), event('attempt_started', 2, task='two')]
        r = run(a+b)
        self.assertEqual(r['denominator'], 2)
        self.assertEqual(r['retry_task_count'], 0)
        self.assertEqual(r['attempt_coverage']['observed_attempt_ids'], 2)

    def test_all_small_log_permutations_are_equal(self):
        rows = [event('task_submitted'), event('attempt_started', 1),
                event('attempt_started', 2, attempt_id='a2'), event('task_closed', 3),
                event('value_confirmed', 4)]
        expected = run(rows)
        for permutation in itertools.permutations(rows):
            self.assertEqual(run(permutation), expected)

    def test_adversarial_fixture_shuffle_and_cohort_reconciliation(self):
        rows = [json.loads(line) for line in Path(__file__).with_name('adversarial-events.jsonl').read_text().splitlines()]
        expected = run(rows)
        for seed in range(25):
            shuffled = copy.deepcopy(rows); random.Random(seed).shuffle(shuffled)
            self.assertEqual(run(shuffled), expected)
        c = expected['cohort_accounting']
        self.assertEqual(c['observed_task_keys'], sum(c[k] for k in
            ('excluded_consent_tasks', 'orphan_tasks', 'ambiguous_submission_tasks',
             'ineligible_tasks', 'right_censored_tasks', 'mature_eligible_consented_tasks')))
        self.assertEqual(c['mature_eligible_consented_tasks'],
                         c['included_tasks'] + c['quarantined_mature_eligible_tasks'])
        self.assertEqual(expected, json.loads(Path(__file__).with_name('adversarial-result.json').read_text()))

    def test_cli_default_horizon_matches_sample_bytes(self):
        directory = Path(__file__).parent
        output = subprocess.check_output([sys.executable, str(directory / 'metrics_lab.py'),
                                          str(directory / 'sample-events.jsonl'), '2000000'])
        self.assertEqual(output, (directory / 'sample-result.json').read_bytes())

    def test_cli_explicit_horizon_matches_adversarial_bytes(self):
        directory = Path(__file__).parent
        output = subprocess.check_output([sys.executable, str(directory / 'metrics_lab.py'),
                                          str(directory / 'adversarial-events.jsonl'), '2000', '1000'])
        self.assertEqual(output, (directory / 'adversarial-result.json').read_bytes())

    def test_baseline_sample_snapshot(self):
        rows = [json.loads(line) for line in Path(__file__).with_name('sample-events.jsonl').read_text().splitlines()]
        r = aggregate(rows, as_of_ms=2_000_000)
        self.assertEqual(r, json.loads(Path(__file__).with_name('sample-result.json').read_text()))
        self.assertEqual(r['denominator'], 3)
        self.assertEqual(r['marginal_counts'], dict(visible=2, success=1, value=1))
        self.assertEqual(r['retry_task_count'], 1)
        self.assertEqual(r['ttfo_p95_ms'], 400)

    def test_same_task_and_event_ids_across_users_are_separate(self):
        first = [event('task_submitted'), event('attempt_started', 1), event('task_closed', 10)]
        second = copy.deepcopy(first)
        for e in second: e['user_id'] = 'synthetic2'
        second[-1]['properties']['outcome'] = 'failure'
        r = run(first + second)
        self.assertEqual(r['denominator'], 2)
        self.assertEqual(r['outcomes']['success'], 1)
        self.assertEqual(r['outcomes']['failure'], 1)
        self.assertEqual(r['quarantine_reasons'], {})

    def test_consent_does_not_cross_user_namespace(self):
        allowed = event('task_submitted')
        denied = copy.deepcopy(allowed); denied['user_id'] = 'synthetic2'; denied['consent'] = False
        r = run([allowed, denied])
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['cohort_accounting']['excluded_consent_tasks'], 1)

    def test_event_id_is_user_scoped_not_task_scoped(self):
        a = event('task_submitted', task='one', eid='same_event')
        b = event('task_submitted', task='two', eid='same_event')
        with self.assertRaises(ContractError): run([a, b])

    def test_schema_does_not_pretend_to_support_organization_partition(self):
        e = event('task_submitted'); e['organization_id'] = 'org1'
        with self.assertRaises(ContractError): run([e])

    def test_timestamp_must_be_nonnegative_integer_not_bool_or_float(self):
        for timestamp in (-1, True, False, 1.0, float('nan'), float('inf'), '1'):
            with self.subTest(timestamp=timestamp):
                e = event('task_submitted'); e['time_ms'] = timestamp
                with self.assertRaises(ContractError): run([e])

    def test_analysis_clock_and_horizon_types_and_bounds(self):
        for cutoff in (-1, True, 1.0, float('nan')):
            with self.subTest(cutoff=cutoff):
                with self.assertRaises(ContractError): run([], cutoff=cutoff)
        for horizon in (0, -1, True, 1.0, float('nan')):
            with self.subTest(horizon=horizon):
                with self.assertRaises(ContractError): run([], horizon=horizon)

    def test_early_terminal_does_not_shortcut_maturity(self):
        rows = [event('task_submitted', 1500), event('task_closed', 1600)]
        r = run(rows, cutoff=2000)
        self.assertEqual(r['denominator'], 0)
        self.assertEqual(r['cohort_accounting']['right_censored_tasks'], 1)
        self.assertEqual(run(rows, cutoff=2500)['denominator'], 1)

    def test_cutoff_boundary_and_unbounded_python_integer_clock(self):
        r = run([event('task_submitted'), event('task_closed', 1000)], cutoff=1000)
        self.assertEqual(r['denominator'], 1)
        self.assertEqual(r['marginal_counts']['success'], 1)
        big = 10**100
        r = run([event('task_submitted', big, eid='big_submit'), event('task_closed', big+1, eid='big_close')], cutoff=big+1000)
        self.assertEqual(r['completion_p95_ms'], 1)

    def test_nonfinite_and_huge_sampling_values_are_contract_errors(self):
        for probability in (float('inf'), float('-inf'), 10**1000, True):
            with self.subTest(probability=repr(probability)[:40]):
                e = event('task_submitted'); e['sample_probability'] = probability
                with self.assertRaises(ContractError): run([e])

    def test_future_invalid_envelope_still_fails_batch_validation(self):
        e = event('attempt_started', 2100); e['properties']['payload'] = 'not allowed'
        with self.assertRaises(ContractError): run([event('task_submitted'), e])

if __name__=='__main__':unittest.main(verbosity=2)
