"""原创宿主身份教学模型；不是完整 MCP 实现或安全沙箱。

复用本书 ApprovalDesk，唯一副作用是内存 journal。
不加载扩展清单、不读取凭据、不启动进程、不连接服务。
"""
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from itertools import count
from existing_lab import load_loop_lab

lab = load_loop_lab()

# 仅在当前进程内分配单调修订号，避免旧授权快照再次匹配。
_state_revisions = count(1)


@dataclass(frozen=True)
class Binding:
    server: str
    source: str
    revision: int
    generation: int
    tool: str


def call_digest(binding: Binding, arguments: dict) -> str:
    # 这里只演示确定性的 JSON 子集，不是通用签名规范。
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

    def __post_init__(self):
        # 运行时修订号不进入 dataclass 字段、repr、相等比较或 asdict。
        self._state_revision = next(_state_revisions)

    def __setattr__(self, name, value):
        # 保留示例的直接赋值方式。初始化赋值和同值赋值不算状态变化；
        # A → B → A 则是两次变化，不能恢复旧授权。
        if (name in {"binding", "ready", "policy"} and name in self.__dict__
                and self.__dict__[name] != value):
            object.__setattr__(self, "_state_revision", next(_state_revisions))
        object.__setattr__(self, name, value)

    def _approval_digest(self, arguments: dict) -> str:
        # call_digest 固定绑定与参数；额外加入修订号，
        # 使批准也绑定可信宿主状态的变化历史。
        snapshot = [self._state_revision, call_digest(self.binding, arguments)]
        return sha256(json.dumps(snapshot, separators=(",", ":")).encode()).hexdigest()

    def ask(self, request_id: str, arguments: dict) -> str:
        if self.policy == "unknown": return "policy-loading"
        if self.policy != "allow": return "policy-denied"
        if not self.ready: return "not-connected"
        item = lab.Approval(request_id, "demo-session", self.binding.tool,
                            self._approval_digest(arguments))
        return "pending" if self.approvals.ask(item) else "duplicate-request"

    def decide_and_record(self, request_id: str, arguments: dict, decision="once") -> str:
        # 消费批准时再次检查，不能只在画审批卡时判断。
        if self.policy != "allow" or not self.ready:
            self.approvals.decide(request_id, "deny", "")
            return "state-changed"
        result = self.approvals.decide(request_id, decision,
                                       self._approval_digest(arguments))
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
