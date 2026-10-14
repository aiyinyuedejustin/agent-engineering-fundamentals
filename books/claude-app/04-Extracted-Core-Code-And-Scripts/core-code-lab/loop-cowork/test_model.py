import unittest
from model import Action, Approval, ApprovalDesk, FakeComputer, Frame, Phase, Session, Tier, execution_route


class LifecycleTests(unittest.TestCase):
    def ready(self):
        s = Session(); ticket = s.begin(); self.assertTrue(s.attach_process(ticket)); return s, ticket

    def test_reject_invalid_edge(self):
        archived = Session(phase=Phase.ARCHIVED)
        with self.assertRaises(ValueError):
            archived.move(Phase.RUNNING)

    def test_stop_invalidates_start(self):
        s = Session(); old = s.begin(); s.stop(); self.assertFalse(s.attach_process(old))

    def test_restarted_generation_wins(self):
        s = Session(); old = s.begin(); s.stop(); new = s.begin()
        self.assertFalse(s.attach_process(old)); self.assertTrue(s.attach_process(new))

    def test_result_does_not_imply_exit(self):
        s, token = self.ready(); self.assertEqual(s.result(token, success=True, keep_warm=True), "idle")
        self.assertTrue(s.process); self.assertEqual(s.phase, Phase.IDLE)

    def test_error_never_keeps_warm(self):
        s, token = self.ready(); s.result(token, success=False, keep_warm=True); self.assertFalse(s.process)

    def test_stale_result_ignored(self):
        s, token = self.ready(); s.stop(); self.assertEqual(s.result(token, success=True, keep_warm=True), "stale")

    def test_pending_message_keeps_running(self):
        s, token = self.ready(); s.submit("m"); self.assertEqual(s.result(token, success=True, keep_warm=False), "continue")
        self.assertEqual(s.phase, Phase.RUNNING)

    def test_duplicate_message_not_added(self):
        s = Session(); s.begin(); self.assertTrue(s.submit("m")); self.assertFalse(s.submit("m")); self.assertEqual(s.queued, ["m"])

    def test_stop_discards_queue(self):
        s = Session(); s.begin(); s.submit("m"); s.stop(); self.assertEqual(s.queued, [])

    def test_warm_reuse_requires_current_policy(self):
        s, token = self.ready(); s.result(token, success=True, keep_warm=True)
        self.assertFalse(s.resume_warm(policy_current=False)); self.assertFalse(s.process)

    def test_warm_reuse_succeeds(self):
        s, token = self.ready(); s.result(token, success=True, keep_warm=True)
        self.assertTrue(s.resume_warm(policy_current=True)); self.assertEqual(s.phase, Phase.RUNNING)


class PermissionTests(unittest.TestCase):
    def setUp(self): self.desk = ApprovalDesk(); self.item = Approval("r1", "s1", "tool", "same")
    def test_duplicate_pending_id(self): self.assertTrue(self.desk.ask(self.item)); self.assertFalse(self.desk.ask(self.item))
    def test_allow_exact_input(self): self.desk.ask(self.item); self.assertEqual(self.desk.decide("r1", "once", "same"), "allow")
    def test_changed_input_denied(self): self.desk.ask(self.item); self.assertEqual(self.desk.decide("r1", "once", "changed"), "deny")
    def test_unknown_choice_denied(self): self.desk.ask(self.item); self.assertEqual(self.desk.decide("r1", "surprise", "same"), "deny")
    def test_reply_only_consumed_once(self):
        self.desk.ask(self.item); self.desk.decide("r1", "once", "same")
        self.assertEqual(self.desk.decide("r1", "always", "same"), "missing")
    def test_cancel_only_one_session(self):
        self.desk.ask(self.item); self.desk.ask(Approval("r2", "s2", "tool", "same"))
        self.assertEqual(self.desk.cancel_session("s1"), 1); self.assertIn("r2", self.desk.pending)


class ComputerTests(unittest.TestCase):
    def test_batch_is_not_atomic(self):
        c = FakeComputer({"editor": Tier.FULL}); result = c.batch([Action("left_click", "editor"), Action("type", "secret")])
        self.assertEqual(result, {"completed": 1, "error": "denied"}); self.assertEqual(len(c.operations), 1)
    def test_read_grant_blocks_click(self): self.assertEqual(FakeComputer({"editor": Tier.READ}).batch([Action("left_click", "editor")])["error"], "denied")
    def test_click_grant_blocks_typing(self): self.assertEqual(FakeComputer({"editor": Tier.CLICK}).batch([Action("type", "editor")])["error"], "denied")
    def test_grants_rechecked_each_action(self):
        c = FakeComputer({"editor": Tier.FULL})
        out = c.batch([Action("left_click", "editor"), Action("type", "editor")], lambda _: c.grants.clear())
        self.assertEqual(out["completed"], 1)
    def test_interrupt_between_actions(self):
        c = FakeComputer({"editor": Tier.FULL})
        def interrupt(_): c.interrupted = True
        out = c.batch([Action("left_click", "editor"), Action("type", "editor")], interrupt)
        self.assertEqual(out, {"completed": 1, "error": "interrupted"})
    def test_frame_to_display(self): self.assertEqual(Frame(1000, 600, 2000, 1200, -2000).map_point(500, 300), (-1000, 600))
    def test_edge_clamps_last_pixel(self): self.assertEqual(Frame(1000, 600, 2000, 1200).map_point(1000, 600), (1999, 1199))
    def test_normalized_coordinates(self): self.assertEqual(Frame(1000, 600, 2000, 1200).map_point(50, 50, percentages=True), (1000, 600))
    def test_bad_coordinates(self):
        f = Frame(10, 10, 10, 10)
        for point in [(-1, 0), (11, 0), (float('nan'), 0), (float('inf'), 0)]:
            with self.subTest(point=point), self.assertRaises(ValueError): f.map_point(*point)
    def test_route_distinguishes_bash_and_host_files(self):
        self.assertNotEqual(execution_route("workspace_bash", "host-loop").owner, execution_route("read_file", "host-loop").owner)
    def test_unknown_route_rejected(self):
        with self.assertRaises(ValueError): execution_route("unknown", "host-loop")


if __name__ == '__main__': unittest.main()
