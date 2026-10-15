"""Original deterministic scenarios; no process, tool, or network is started."""
from existing_lab import load_loop_lab

lab = load_loop_lab()


def stop_then_restart():
    s = lab.Session()
    rows = []
    def record(event, outcome=""):
        rows.append({"event": event, "epoch": s.epoch, "phase": s.phase.value,
                     "process": s.process, "queued": list(s.queued), "outcome": outcome})
    old = s.begin(); s.submit("message-A"); record("A begins")
    s.stop(); record("Stop invalidates A")
    new = s.begin(); s.submit("message-B"); record("B begins")
    record("A initialization arrives", s.attach_process(old))
    record("B initialization arrives", s.attach_process(new))
    assert s.consume() == "message-B"
    record("A result arrives", s.result(old, success=True, keep_warm=True))
    record("B result arrives", s.result(new, success=True, keep_warm=True))
    return rows


def cancelled_approval():
    desk = lab.ApprovalDesk()
    desk.ask(lab.Approval("card-A", "session-A", "write-note", "digest-A"))
    desk.ask(lab.Approval("card-B", "session-B", "write-note", "digest-B"))
    cancelled = desk.cancel_session("session-A")
    late = desk.decide("card-A", "once", "digest-A")
    current = desk.decide("card-B", "once", "digest-B")
    repeated = desk.decide("card-B", "once", "digest-B")
    return cancelled, late, current, repeated


if __name__ == "__main__":
    import json
    print(json.dumps(stop_then_restart(), indent=2))
    print("cancel count, late A, current B, repeated B:", cancelled_approval())
