"""An original host-side identity example, NOT MCP or a security sandbox.

It reuses the book's ApprovalDesk. The only side effect is an in-memory journal.
No manifest is loaded, credentials read, process started, or service contacted.
"""
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from existing_lab import load_loop_lab

lab = load_loop_lab()


@dataclass(frozen=True)
class Binding:
    server: str
    source: str
    revision: int
    generation: int
    tool: str


def call_digest(binding: Binding, arguments: dict) -> str:
    # This is an illustrative JSON subset, not a canonical signing format.
    encoded = json.dumps([asdict(binding), arguments], sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass
class MockHost:
    binding: Binding
    ready: bool = True
    policy: str = "unknown"
    approvals: object = field(default_factory=lab.ApprovalDesk)
    journal: list[str] = field(default_factory=list)

    def ask(self, request_id: str, arguments: dict) -> str:
        if self.policy == "unknown": return "policy-loading"
        if self.policy != "allow": return "policy-denied"
        if not self.ready: return "not-connected"
        item = lab.Approval(request_id, "demo-session", self.binding.tool,
                            call_digest(self.binding, arguments))
        return "pending" if self.approvals.ask(item) else "duplicate-request"

    def decide_and_record(self, request_id: str, arguments: dict, decision="once") -> str:
        # Recheck at consumption, not only when drawing the approval card.
        if self.policy != "allow" or not self.ready:
            self.approvals.decide(request_id, "deny", "")
            return "state-changed"
        result = self.approvals.decide(request_id, decision,
                                       call_digest(self.binding, arguments))
        if result == "allow": self.journal.append(f"mock-dispatch:{self.binding.tool}")
        return result


if __name__ == "__main__":
    old = Binding("notes", "extension:sample", 1, 1, "read_note")
    host = MockHost(old, policy="allow")
    args = {"path": "notes/meeting.txt"}
    print("request:", host.ask("r1", args))
    host.binding = Binding("notes", "manual:sample", 2, 2, "read_note")
    print("same name, new provider:", host.decide_and_record("r1", args))
    print("external effects:", host.journal)
