from dataclasses import replace
import unittest
from loop_timeline import stop_then_restart, cancelled_approval, lab
from mcp_binding import Binding, MockHost, call_digest


class LoopTimelineTests(unittest.TestCase):
    def test_generations_explain_every_callback(self):
        rows = stop_then_restart()
        self.assertEqual([r['epoch'] for r in rows], [1, 2, 3, 3, 3, 3, 3])
        self.assertEqual([r['outcome'] for r in rows[3:]], [False, True, 'stale', 'idle'])

    def test_old_start_cannot_consume_new_queue(self):
        rows = stop_then_restart()
        self.assertEqual(rows[3]['queued'], ['message-B'])
        self.assertFalse(rows[3]['process'])

    def test_turn_end_can_keep_warm_process(self):
        end = stop_then_restart()[-1]
        self.assertEqual(end['phase'], 'idle')
        self.assertTrue(end['process'])

    def test_cancel_and_duplicate_answers_are_distinct(self):
        self.assertEqual(cancelled_approval(), (1, 'missing', 'allow', 'missing'))

    def test_old_id_is_not_a_new_user_intention(self):
        s = lab.Session(); s.begin(); s.submit('m'); s.stop(); s.begin()
        self.assertFalse(s.submit('m'))
        self.assertTrue(s.submit('new-m'))

    def test_deny_does_not_stop_independent_session(self):
        s = lab.Session(); ticket = s.begin(); s.attach_process(ticket)
        d = lab.ApprovalDesk(); d.ask(lab.Approval('r', 's', 'mock', 'd'))
        self.assertEqual(d.decide('r', 'deny', 'd'), 'deny')
        self.assertEqual(s.phase, lab.Phase.RUNNING)


class McpBindingTests(unittest.TestCase):
    def setUp(self):
        self.binding = Binding('notes', 'extension:sample', 1, 1, 'read_note')
        self.host = MockHost(self.binding, policy='allow')
        self.args = {'path': 'notes/meeting.txt'}

    def test_exact_call_is_recorded_once(self):
        self.assertEqual(self.host.ask('r', self.args), 'pending')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'allow')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'missing')
        self.assertEqual(len(self.host.journal), 1)

    def test_same_name_different_source_is_denied(self):
        self.host.ask('r', self.args)
        self.host.binding = replace(self.binding, source='manual:sample')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'deny')
        self.assertEqual(self.host.journal, [])

    def test_restart_requires_new_approval_in_this_teaching_policy(self):
        self.host.ask('r', self.args)
        self.host.binding = replace(self.binding, generation=2)
        self.assertEqual(self.host.decide_and_record('r', self.args), 'deny')

    def test_configuration_revision_is_bound(self):
        self.host.ask('r', self.args)
        self.host.binding = replace(self.binding, revision=2)
        self.assertEqual(self.host.decide_and_record('r', self.args), 'deny')

    def test_changed_target_is_denied(self):
        self.host.ask('r', self.args)
        self.assertEqual(self.host.decide_and_record('r', {'path': 'other/file.txt'}), 'deny')

    def test_different_tool_is_denied(self):
        self.host.ask('r', self.args)
        self.host.binding = replace(self.binding, tool='send_summary')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'deny')

    def test_policy_loading_is_not_connection_failure(self):
        self.host.policy = 'unknown'
        self.assertEqual(self.host.ask('r', self.args), 'policy-loading')
        self.assertFalse(self.host.approvals.pending)

    def test_revocation_while_approval_is_visible(self):
        self.host.ask('r', self.args); self.host.policy = 'deny'
        self.assertEqual(self.host.decide_and_record('r', self.args), 'state-changed')
        self.host.policy = 'allow'
        self.assertEqual(self.host.decide_and_record('r', self.args), 'missing')

    def test_disconnection_is_not_undo(self):
        self.host.ask('r', self.args); self.host.decide_and_record('r', self.args)
        self.host.ready = False
        self.assertEqual(self.host.ask('next', self.args), 'not-connected')
        self.assertEqual(len(self.host.journal), 1)

    def test_duplicate_request_does_not_replace_parameters(self):
        self.host.ask('r', self.args)
        self.assertEqual(self.host.ask('r', {'path': 'other'}), 'duplicate-request')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'allow')

    def test_json_key_order_is_irrelevant(self):
        self.assertEqual(call_digest(self.binding, {'a': 1, 'b': 2}),
                         call_digest(self.binding, {'b': 2, 'a': 1}))


class McpLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.binding = Binding('notes', 'extension:sample', 1, 1, 'read_note')
        self.host = MockHost(self.binding, policy='allow')
        self.args = {'path': 'notes/meeting.txt'}

    def assert_stale_after(self, field, interim):
        original = getattr(self.host, field)
        self.assertEqual(self.host.ask('r', self.args), 'pending')
        setattr(self.host, field, interim)
        setattr(self.host, field, original)
        self.assertEqual(self.host.decide_and_record('r', self.args), 'deny')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'missing')
        self.assertEqual(self.host.ask('r', self.args), 'duplicate-request')
        self.assertEqual(self.host.journal, [])
        self.assertEqual(self.host.ask('new', self.args), 'pending')
        self.assertEqual(self.host.decide_and_record('new', self.args), 'allow')

    def test_policy_deny_allow_before_first_click(self):
        self.assert_stale_after('policy', 'deny')

    def test_policy_unknown_allow_before_first_click(self):
        self.assert_stale_after('policy', 'unknown')

    def test_disconnect_reconnect_before_first_click(self):
        self.assert_stale_after('ready', False)

    def test_binding_change_restore_before_first_click(self):
        self.assert_stale_after('binding', replace(self.binding, source='manual:sample'))

    def test_duplicate_after_restore_cannot_refresh_old_snapshot(self):
        self.host.ask('r', self.args)
        self.host.policy = 'deny'; self.host.policy = 'allow'
        self.assertEqual(self.host.ask('r', self.args), 'duplicate-request')
        self.assertEqual(self.host.decide_and_record('r', self.args), 'deny')
        self.assertEqual(self.host.journal, [])

    def test_equal_assignments_keep_pending_approval(self):
        self.host.ask('r', self.args)
        self.host.policy = 'allow'; self.host.ready = True
        self.host.binding = replace(self.binding)
        self.assertEqual(self.host.decide_and_record('r', self.args), 'allow')

    def test_disconnected_click_consumes_before_restore(self):
        self.host.ask('r', self.args); self.host.ready = False
        self.assertEqual(self.host.decide_and_record('r', self.args), 'state-changed')
        self.host.ready = True
        self.assertEqual(self.host.decide_and_record('r', self.args), 'missing')
        self.assertEqual(self.host.journal, [])

    def test_nested_argument_mutation_is_denied_and_consumed(self):
        args = {'paths': ['notes/meeting.txt']}
        self.host.ask('r', args); args['paths'][0] = 'other'
        self.assertEqual(self.host.decide_and_record('r', args), 'deny')
        self.assertEqual(self.host.decide_and_record('r', args), 'missing')
        self.assertEqual(self.host.journal, [])

    def test_one_transition_revokes_every_older_card_only(self):
        self.host.ask('a', self.args); self.host.ask('b', self.args)
        self.host.ready = False; self.host.ready = True
        self.host.ask('c', self.args)
        self.assertEqual(self.host.decide_and_record('c', self.args), 'allow')
        self.assertEqual(self.host.decide_and_record('a', self.args), 'deny')
        self.assertEqual(self.host.decide_and_record('b', self.args), 'deny')
        self.assertEqual(len(self.host.journal), 1)

    def test_other_host_transition_does_not_revoke_this_host(self):
        other = MockHost(self.binding, policy='allow', approvals=self.host.approvals)
        self.host.ask('a', self.args); other.ask('b', self.args)
        other.policy = 'deny'; other.policy = 'allow'
        self.assertEqual(self.host.decide_and_record('a', self.args), 'allow')
        self.assertEqual(other.decide_and_record('b', self.args), 'deny')

    def test_dataclass_public_shape_and_value_semantics_preserved(self):
        from dataclasses import asdict, fields
        desk = lab.ApprovalDesk(); journal = []
        left = MockHost(self.binding, True, 'allow', desk, journal)
        right = MockHost(self.binding, True, 'allow', desk, journal)
        self.assertEqual([f.name for f in fields(left)],
                         ['binding', 'ready', 'policy', 'approvals', 'journal'])
        self.assertEqual(left, right)
        self.assertEqual(repr(left), repr(right))
        self.assertEqual(asdict(left), asdict(right))
        left.policy = 'deny'; left.policy = 'allow'
        self.assertEqual(left, right)
        self.assertEqual(replace(left), left)
        with self.assertRaises(TypeError): hash(left)

    def test_replacement_is_new_host_not_old_authorization(self):
        self.host.ask('r', self.args)
        cloned = replace(self.host)
        self.assertEqual(cloned.decide_and_record('r', self.args), 'deny')
        self.assertEqual(self.host.journal, [])


if __name__ == '__main__': unittest.main()
