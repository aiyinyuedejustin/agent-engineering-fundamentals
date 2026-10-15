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


if __name__ == '__main__': unittest.main()
