"""Original teaching models for turn lifecycle, authority and coordinates.

This code is newly written for the book. It contains no recovered Claude source.
It never starts a process, connects to a service, reads a real screenshot, or sends
computer input. Dataclasses and fake executors make invariants testable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import floor, isfinite
from typing import Callable, Iterable


class Phase(str, Enum):
    IDLE = "idle"
    STARTING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    ARCHIVED = "archived"


EDGES = {
    Phase.IDLE: {Phase.STARTING, Phase.RUNNING, Phase.STOPPING, Phase.ARCHIVED},
    Phase.STARTING: {Phase.RUNNING, Phase.IDLE, Phase.STOPPING},
    Phase.RUNNING: {Phase.IDLE, Phase.STOPPING},
    Phase.STOPPING: {Phase.IDLE},
    Phase.ARCHIVED: {Phase.STARTING},
}


@dataclass(frozen=True)
class SpawnTicket:
    epoch: int


@dataclass
class Session:
    """Session and process lifetime are deliberately separate variables."""
    phase: Phase = Phase.IDLE
    epoch: int = 0
    process: bool = False
    queued: list[str] = field(default_factory=list)
    accepted_ids: set[str] = field(default_factory=set)
    events: list[str] = field(default_factory=list)

    def move(self, target: Phase) -> None:
        if target == self.phase:
            return
        if target not in EDGES[self.phase]:
            raise ValueError(f"invalid lifecycle edge: {self.phase} -> {target}")
        self.events.append(f"{self.phase.value}->{target.value}")
        self.phase = target

    def begin(self) -> SpawnTicket:
        self.move(Phase.STARTING)
        self.epoch += 1
        return SpawnTicket(self.epoch)

    def attach_process(self, ticket: SpawnTicket) -> bool:
        if ticket.epoch != self.epoch or self.phase != Phase.STARTING:
            self.events.append("discard stale spawn")
            return False
        self.process = True
        self.move(Phase.RUNNING)
        return True

    def submit(self, message_id: str) -> bool:
        if message_id in self.accepted_ids:
            return False
        if self.phase not in {Phase.STARTING, Phase.RUNNING}:
            raise ValueError("start or resume a session before submitting")
        self.accepted_ids.add(message_id)
        self.queued.append(message_id)
        return True

    def consume(self) -> str:
        return self.queued.pop(0)

    def result(self, ticket: SpawnTicket, *, success: bool, keep_warm: bool) -> str:
        if ticket.epoch != self.epoch:
            return "stale"
        if self.phase != Phase.RUNNING:
            return "inactive"
        if success and self.queued:
            return "continue"
        self.move(Phase.IDLE)
        self.process = success and keep_warm
        return "idle"

    def resume_warm(self, *, policy_current: bool) -> bool:
        if self.phase != Phase.IDLE or not self.process:
            return False
        if not policy_current:
            self.process = False
            return False
        self.move(Phase.RUNNING)
        return True

    def stop(self) -> None:
        self.epoch += 1
        self.move(Phase.STOPPING)
        self.queued.clear()
        self.process = False
        self.move(Phase.IDLE)


@dataclass(frozen=True)
class Approval:
    request_id: str
    session: str
    tool: str
    argument_digest: str


@dataclass
class ApprovalDesk:
    """Teaching choice: approval pins a digest; no actual inputs are executed."""
    pending: dict[str, Approval] = field(default_factory=dict)
    outcomes: dict[str, str] = field(default_factory=dict)

    def ask(self, item: Approval) -> bool:
        if item.request_id in self.pending or item.request_id in self.outcomes:
            return False
        self.pending[item.request_id] = item
        return True

    def decide(self, request_id: str, choice: str, argument_digest: str) -> str:
        item = self.pending.pop(request_id, None)
        if item is None:
            return "missing"
        allowed = choice in {"once", "always"} and item.argument_digest == argument_digest
        result = "allow" if allowed else "deny"
        self.outcomes[request_id] = result
        return result

    def cancel_session(self, session: str) -> int:
        doomed = [key for key, value in self.pending.items() if value.session == session]
        for key in doomed:
            self.pending.pop(key)
            self.outcomes[key] = "deny"
        return len(doomed)


class Tier(int, Enum):
    READ = 0
    CLICK = 1
    FULL = 2


@dataclass(frozen=True)
class Action:
    kind: str
    target_app: str


def required_tier(action: Action) -> Tier:
    if action.kind == "screenshot":
        return Tier.READ
    if action.kind in {"left_click", "move"}:
        return Tier.CLICK
    return Tier.FULL


@dataclass
class FakeComputer:
    grants: dict[str, Tier]
    operations: list[str] = field(default_factory=list)
    interrupted: bool = False

    def batch(self, actions: Iterable[Action], after_action: Callable[[int], None] = lambda _: None) -> dict:
        completed = 0
        for index, action in enumerate(actions):
            if self.interrupted:
                return {"completed": completed, "error": "interrupted"}
            tier = self.grants.get(action.target_app)
            if tier is None or tier < required_tier(action):
                return {"completed": completed, "error": "denied"}
            # A journal entry only. It cannot click or type into any application.
            self.operations.append(f"{action.kind}:{action.target_app}")
            completed += 1
            after_action(index)
        return {"completed": completed, "error": None}


@dataclass(frozen=True)
class Frame:
    frame_width: int
    frame_height: int
    display_width: int
    display_height: int
    origin_x: int = 0
    origin_y: int = 0

    def map_point(self, x: float, y: float, *, percentages: bool = False) -> tuple[int, int]:
        # Deliberate stricter teaching design: no no-screenshot fallback exists.
        dimensions = (self.frame_width, self.frame_height, self.display_width, self.display_height)
        if any(not isinstance(n, int) or n <= 0 for n in dimensions):
            raise ValueError("positive frame and display dimensions required")
        if not all(isfinite(n) for n in (x, y)):
            raise ValueError("finite coordinates required")
        width, height = (100, 100) if percentages else (self.frame_width, self.frame_height)
        if not (0 <= x <= width and 0 <= y <= height):
            raise ValueError("point outside coordinate frame")
        # Round-half-up for nonnegative display-relative positions.
        dx = min(floor(x * self.display_width / width + 0.5), self.display_width - 1)
        dy = min(floor(y * self.display_height / height + 0.5), self.display_height - 1)
        return self.origin_x + dx, self.origin_y + dy


@dataclass(frozen=True)
class Route:
    owner: str
    coordinate_space: str | None = None


def execution_route(tool: str, mode: str) -> Route:
    """An educational ownership table, not a product API or launcher."""
    if mode not in {"host-loop", "vm-loop"}:
        raise ValueError("unknown mode")
    if tool == "computer_click":
        return Route("host platform executor", "last full screenshot")
    if tool == "workspace_bash":
        return Route("isolated workspace VM")
    if tool in {"read_file", "write_file"}:
        return Route("host CLI" if mode == "host-loop" else "VM CLI")
    if tool == "model_completion":
        return Route("inference service beyond client evidence")
    raise ValueError("tool has no declared execution owner")


if __name__ == "__main__":
    s = Session()
    ticket = s.begin()
    s.submit("synthetic-message-1")
    assert s.attach_process(ticket)
    s.consume()
    print(s.result(ticket, success=True, keep_warm=True), "process retained:", s.process)
    print("warm resume:", s.resume_warm(policy_current=True))
    print("host-loop Bash owner:", execution_route("workspace_bash", "host-loop").owner)
    print("image point -> display point:", Frame(1000, 600, 2000, 1200, -2000).map_point(500, 300))
