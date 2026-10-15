import copy
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

if __name__=='__main__':unittest.main(verbosity=2)
