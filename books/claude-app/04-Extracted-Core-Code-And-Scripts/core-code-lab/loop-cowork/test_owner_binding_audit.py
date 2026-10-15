"""原创独立归属检查，以及明确保留的进程票据边界。"""
import gc
import unittest
import weakref
from model import Session, SpawnTicket, Phase

class IndependentTests(unittest.TestCase):
    def test_structurally_equal_running_sessions_reject_foreign_results(self):
        for success in (True, False):
            a, b = Session(), Session()
            ta, tb = a.begin(), b.begin()
            a.attach_process(ta); b.attach_process(tb)
            self.assertEqual(a, b)
            before = repr(b)
            self.assertEqual(b.result(ta, success=success, keep_warm=False), 'stale')
            self.assertEqual(repr(b), before)

    def test_constructed_same_owner_same_epoch_is_accepted_not_original_identity_guard(self):
        s = Session(); original = s.begin()
        reconstructed = SpawnTicket(original.epoch, s)
        self.assertIsNot(original, reconstructed)
        self.assertNotEqual(original, reconstructed)
        self.assertTrue(s.attach_process(reconstructed))
        self.assertEqual(s.result(SpawnTicket(original.epoch, s), success=True, keep_warm=True), 'idle')

    def test_strong_owner_reference_keeps_session_alive_until_ticket_released(self):
        s = Session(); ref = weakref.ref(s); ticket = s.begin()
        del s; gc.collect()
        self.assertIs(ref(), ticket.owner)
        del ticket; gc.collect()
        self.assertIsNone(ref())

    def test_ticket_repr_does_not_expand_session_and_hash_uses_identity(self):
        s = Session(); t = s.begin(); other = SpawnTicket(t.epoch, s)
        self.assertEqual(repr(t), 'SpawnTicket(epoch=1)')
        self.assertEqual(len({t, other}), 2)

    def test_restart_warm_reuse_rejects_old_epoch_success_and_error(self):
        for success in (True, False):
            s = Session(); old = s.begin(); s.attach_process(old); s.stop()
            new = s.begin(); s.attach_process(new)
            s.result(new, success=True, keep_warm=True)
            self.assertTrue(s.resume_warm(policy_current=True))
            before = repr(s)
            self.assertEqual(s.result(old, success=success, keep_warm=True), 'stale')
            self.assertEqual(repr(s), before)

    def test_same_process_epoch_delayed_result_can_settle_resumed_turn_boundary(self):
        s = Session(); t = s.begin(); s.attach_process(t)
        s.result(t, success=True, keep_warm=True); s.resume_warm(policy_current=True)
        # Deliberate existing process-epoch model: no distinct per-turn ticket.
        self.assertEqual(s.result(t, success=False, keep_warm=True), 'idle')
        self.assertFalse(s.process)

    def test_stop_rejects_all_old_result_flags_without_state_changes(self):
        s = Session(); t = s.begin(); s.attach_process(t); s.stop()
        before = repr(s)
        for success in (True, False):
            for keep_warm in (True, False):
                self.assertEqual(s.result(t, success=success, keep_warm=keep_warm), 'stale')
                self.assertEqual(repr(s), before)

if __name__ == '__main__': unittest.main(verbosity=2)
