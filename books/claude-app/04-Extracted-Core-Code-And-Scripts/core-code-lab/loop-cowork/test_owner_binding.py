"""Original local ownership regressions; no product or real process execution."""
import unittest
from model import Phase, Session


class OwnerBindingTests(unittest.TestCase):
    def pair(self):
        left, right = Session(), Session()
        a, b = left.begin(), right.begin()
        self.assertEqual(a.epoch, b.epoch)
        return left, a, right, b

    def snapshot(self, s):
        return (s.phase, s.epoch, s.process, list(s.queued), set(s.accepted_ids))

    def test_equal_valued_sessions_are_not_same_owner(self):
        left, a, right, b = self.pair()
        self.assertEqual(left, right)  # Dataclass value equality is insufficient.
        self.assertIsNot(left, right)
        self.assertIs(a.owner, left)
        self.assertIs(b.owner, right)
        self.assertNotEqual(a, b)
        before = self.snapshot(right)
        self.assertFalse(right.attach_process(a))
        self.assertEqual(self.snapshot(right), before)
        self.assertEqual(right.events[-1], 'discard stale spawn')

    def test_bidirectional_cross_attach_rejected_then_correct_attach_works(self):
        left, a, right, b = self.pair()
        self.assertFalse(left.attach_process(b))
        self.assertFalse(right.attach_process(a))
        self.assertTrue(left.attach_process(a))
        self.assertTrue(right.attach_process(b))

    def test_registry_same_string_name_replacement_rejects_old_ticket(self):
        registry = {'same-session-id': Session()}
        old = registry['same-session-id'].begin()
        registry['same-session-id'] = Session()
        current = registry['same-session-id']; new = current.begin()
        self.assertEqual(old.epoch, new.epoch)
        self.assertFalse(current.attach_process(old))
        self.assertTrue(current.attach_process(new))
        self.assertEqual(current.result(old, success=True, keep_warm=False), 'stale')
        self.assertEqual(current.phase, Phase.RUNNING)
        self.assertTrue(current.process)

    def test_foreign_success_error_and_keep_warm_never_settle_running_owner(self):
        for success in (True, False):
            for keep_warm in (True, False):
                with self.subTest(success=success, keep_warm=keep_warm):
                    left, a, right, b = self.pair(); right.attach_process(b); right.submit('new')
                    before = self.snapshot(right); events = list(right.events)
                    self.assertEqual(right.result(a, success=success, keep_warm=keep_warm), 'stale')
                    self.assertEqual(self.snapshot(right), before)
                    self.assertEqual(right.events, events)

    def test_foreign_result_stays_stale_in_starting_and_idle(self):
        left, a, right, b = self.pair()
        self.assertEqual(right.result(a, success=False, keep_warm=False), 'stale')
        right.attach_process(b); right.result(b, success=True, keep_warm=True)
        self.assertEqual(right.result(a, success=False, keep_warm=False), 'stale')
        self.assertTrue(right.process)

    def test_stop_restart_rejects_same_owner_old_epoch_attach_and_error(self):
        s = Session(); old = s.begin(); s.stop(); new = s.begin()
        self.assertIs(old.owner, new.owner)
        self.assertEqual(new.epoch, old.epoch + 2)
        self.assertFalse(s.attach_process(old)); self.assertTrue(s.attach_process(new))
        before = self.snapshot(s)
        for success in (True, False):
            self.assertEqual(s.result(old, success=success, keep_warm=False), 'stale')
            self.assertEqual(self.snapshot(s), before)

    def test_correct_owner_warm_reuse_preserves_ticket_and_epoch(self):
        s = Session(); ticket = s.begin(); self.assertTrue(s.attach_process(ticket))
        self.assertEqual(s.result(ticket, success=True, keep_warm=True), 'idle')
        self.assertTrue(s.process); self.assertTrue(s.resume_warm(policy_current=True))
        self.assertEqual(s.epoch, ticket.epoch)
        self.assertEqual(s.result(ticket, success=True, keep_warm=True), 'idle')
        self.assertTrue(s.process)

    def test_correct_owner_error_clears_only_simulated_process(self):
        s = Session(); ticket = s.begin(); s.attach_process(ticket)
        self.assertEqual(s.result(ticket, success=False, keep_warm=True), 'idle')
        self.assertFalse(s.process)
        self.assertEqual(s.result(ticket, success=True, keep_warm=True), 'inactive')
        self.assertFalse(s.process)

    def test_late_attach_after_local_error_cannot_reactivate(self):
        s = Session(); ticket = s.begin(); s.attach_process(ticket)
        s.result(ticket, success=False, keep_warm=False)
        self.assertFalse(s.attach_process(ticket)); self.assertFalse(s.process)
        self.assertEqual(s.phase, Phase.IDLE)

    def test_correct_owner_queue_continues_and_stop_retains_dedup_contract(self):
        s = Session(); ticket = s.begin(); s.attach_process(ticket); s.submit('m')
        self.assertEqual(s.result(ticket, success=True, keep_warm=False), 'continue')
        self.assertTrue(s.process); self.assertEqual(s.phase, Phase.RUNNING)
        s.stop(); self.assertEqual(s.queued, []); self.assertIn('m', s.accepted_ids)
        self.assertEqual(s.result(ticket, success=False, keep_warm=False), 'stale')

    def test_old_owner_can_finish_itself_without_settling_replacement(self):
        left, a, right, b = self.pair(); left.attach_process(a); right.attach_process(b)
        self.assertEqual(left.result(a, success=False, keep_warm=False), 'idle')
        self.assertEqual(right.phase, Phase.RUNNING); self.assertTrue(right.process)


if __name__ == '__main__':
    unittest.main()
