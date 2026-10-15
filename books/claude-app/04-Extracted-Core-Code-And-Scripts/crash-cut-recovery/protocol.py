"""Original, single-writer logical recovery model. Not a product implementation.

The public runner creates a TemporaryDirectory. This private worker only uses
that runner's capability and fixed filenames; there is no user-path CLI option.
No fsync, network, user configuration, or hardware-failure simulation is used.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys


FILES = ("settings.json", "candidate.json", "intent.json", "receipt.json")
WRITE_CUTS = tuple(f"C{i}" for i in range(8))
RECOVERY_CUTS = ("R_RENAME", "R_RECEIPT", "R_COMMIT")
OLD = {"revision": 7, "label": "old"}
NEW = {"revision": 8, "label": "new"}
OPERATION_ID = "op-r7-r8"


def encode(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def intent_for_demo() -> dict:
    return {"schema": 1, "resource": "synthetic-settings", "operationId": OPERATION_ID,
            "baseHash": digest(encode(OLD)), "nextHash": digest(encode(NEW)),
            "nextRevision": 8}


def decode(data: bytes) -> object:
    # Duplicate keys are rejected instead of silently using the last value.
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def settings(data: bytes) -> dict:
    value = decode(data)
    if (not isinstance(value, dict) or set(value) != {"revision", "label"}
            or type(value["revision"]) is not int or value["revision"] < 0
            or not isinstance(value["label"], str)):
        raise ValueError("invalid settings")
    return value


def valid_intent(data: bytes) -> dict:
    value = decode(data)
    keys = {"schema", "resource", "operationId", "baseHash", "nextHash", "nextRevision"}
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("invalid journal fields")
    if type(value["schema"]) is not int or value["schema"] != 1:
        raise ValueError("unsupported schema")
    if value["resource"] != "synthetic-settings":
        raise ValueError("unsupported resource")
    if (not isinstance(value["operationId"], str)
            or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", value["operationId"])):
        raise ValueError("invalid operation id")
    for key in ("baseHash", "nextHash"):
        if not isinstance(value[key], str) or not re.fullmatch(r"[0-9a-f]{64}", value[key]):
            raise ValueError("invalid hash")
    if (value["baseHash"] == value["nextHash"]
            or type(value["nextRevision"]) is not int or value["nextRevision"] < 0):
        raise ValueError("invalid transition")
    return value


def expected_receipt(intent: dict) -> dict:
    return {"schema": 1, "resource": intent["resource"],
            "operationId": intent["operationId"], "nextHash": intent["nextHash"],
            "revision": intent["nextRevision"]}


def valid_receipt(data: bytes) -> dict:
    value = decode(data)
    keys = {"schema", "resource", "operationId", "nextHash", "revision"}
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("invalid receipt fields")
    if (type(value["schema"]) is not int or value["schema"] != 1
            or value["resource"] != "synthetic-settings"
            or type(value["revision"]) is not int or value["revision"] < 0
            or not isinstance(value["operationId"], str)
            or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", value["operationId"])
            or not isinstance(value["nextHash"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", value["nextHash"])):
        raise ValueError("invalid receipt")
    return value


def checkpoint(phase: str, selected: str | None) -> None:
    if phase == selected:
        print(json.dumps({"event": "paused", "checkpoint": phase}), flush=True)
        # The parent observes this exact handshake before terminating its child.
        # EOF is an error, not permission to silently continue the transaction.
        sys.stdin.buffer.read(1)
        raise RuntimeError("paused worker was resumed instead of terminated")


def put(root: Path, name: str, data: bytes) -> None:
    assert name in FILES
    with (root / name).open("wb") as stream:
        stream.write(data)
    # close/write completion is not a hardware-durability claim.


def rejected(action: str) -> dict:
    return {"status": "rejected", "action": action,
            "target_replacements": 0, "receipt_writes": 0}


def finish(root: Path, intent: dict, selected: str | None,
           recovering: bool, replacements: int, route: str) -> dict:
    target = (root / "settings.json").read_bytes()
    if digest(target) != intent["nextHash"] or settings(target)["revision"] != intent["nextRevision"]:
        raise RuntimeError("installed target failed postcondition")
    receipt = expected_receipt(intent)
    path = root / "receipt.json"
    writes = 0
    if not path.exists():
        put(root, "receipt.json", encode(receipt))
        writes = 1
    elif valid_receipt(path.read_bytes()) != receipt:
        raise RuntimeError("receipt changed inside single-writer transaction")
    checkpoint("R_RECEIPT" if recovering else "C6", selected)
    (root / "intent.json").unlink()
    checkpoint("R_COMMIT" if recovering else "C7", selected)
    return {"status": "committed", "action": route,
            "target_replacements": replacements, "receipt_writes": writes}


def write(root: Path, selected: str | None, deny_rename: bool = False) -> dict:
    intent = intent_for_demo()
    if digest((root / "settings.json").read_bytes()) != intent["baseHash"]:
        return rejected("base-conflict")
    if (root / "intent.json").exists() or (root / "receipt.json").exists():
        return rejected("existing-operation")
    checkpoint("C0", selected)
    candidate = encode(NEW)
    # Synthetic torn files: a deterministic prefix, not an observed OS tear.
    put(root, "candidate.json", candidate[:len(candidate) // 2])
    checkpoint("C1", selected)
    put(root, "candidate.json", candidate)
    if digest((root / "candidate.json").read_bytes()) != intent["nextHash"]:
        raise RuntimeError("candidate write verification failed")
    checkpoint("C2", selected)  # writeComplete
    journal = encode(intent)
    put(root, "intent.json", journal[:len(journal) // 2])
    checkpoint("C3", selected)
    put(root, "intent.json", journal)
    checkpoint("C4", selected)
    try:
        if deny_rename:
            raise PermissionError("synthetic rename refusal")
        os.replace(root / "candidate.json", root / "settings.json")
    except OSError:
        return rejected("rename-refused")
    checkpoint("C5", selected)  # renameComplete
    return finish(root, intent, selected, False, 1, "writer-committed")


def recover(root: Path, selected: str | None, expected: dict) -> dict:
    journal = root / "intent.json"
    receipt_path = root / "receipt.json"
    if not journal.exists():
        if not receipt_path.exists():
            return {"status": "idle", "action": "no-intent",
                    "target_replacements": 0, "receipt_writes": 0}
        try:
            receipt = valid_receipt(receipt_path.read_bytes())
            if receipt != expected_receipt(expected):
                return rejected("operation-conflict")
            target = (root / "settings.json").read_bytes()
            if digest(target) != receipt["nextHash"] or settings(target)["revision"] != receipt["revision"]:
                raise ValueError("receipt does not describe current target")
        except (ValueError, KeyError, TypeError, OSError):
            return rejected("invalid-receipt")
        return {"status": "committed", "action": "already-committed",
                "target_replacements": 0, "receipt_writes": 0}
    try:
        intent = valid_intent(journal.read_bytes())
    except (ValueError, KeyError, TypeError, OSError):
        return rejected("invalid-journal")
    if intent != expected:
        return rejected("operation-conflict")
    # A receipt for some other operation cannot authorize this transaction.
    if receipt_path.exists():
        try:
            if valid_receipt(receipt_path.read_bytes()) != expected_receipt(intent):
                return rejected("receipt-conflict")
        except (ValueError, OSError):
            return rejected("invalid-receipt")
    try:
        target = (root / "settings.json").read_bytes()
        current_hash = digest(target)
    except OSError:
        return rejected("invalid-target")
    if current_hash == intent["nextHash"]:  # Already installed takes precedence.
        try:
            if settings(target)["revision"] != intent["nextRevision"]:
                return rejected("invalid-target")
        except (ValueError, TypeError):
            return rejected("invalid-target")
        return finish(root, intent, selected, True, 0, "finalized-installed")
    if current_hash != intent["baseHash"]:
        return rejected("base-conflict")
    try:
        candidate = (root / "candidate.json").read_bytes()
        if (digest(candidate) != intent["nextHash"]
                or settings(candidate)["revision"] != intent["nextRevision"]):
            return rejected("invalid-material")
    except (ValueError, TypeError, OSError):
        return rejected("invalid-material")
    try:
        os.replace(root / "candidate.json", root / "settings.json")
    except OSError:
        return rejected("rename-refused")
    checkpoint("R_RENAME", selected)
    return finish(root, intent, selected, True, 1, "installed-candidate")


def worker_main() -> None:
    mode, cut, denial = sys.argv[1:]
    selected = None if cut == "none" else cut
    allowed = WRITE_CUTS if mode == "write" else RECOVERY_CUTS if mode == "recover" else ()
    if mode not in ("write", "recover") or selected not in (None, *allowed):
        raise ValueError("unsupported worker mode or checkpoint")
    root = Path(os.environ["CRASH_CUT_ROOT"])
    token = os.environ["CRASH_CUT_TOKEN"]
    if (not root.is_dir() or root.is_symlink()
            or (root / ".lab-owner").read_text() != token):
        raise RuntimeError("missing runner-owned sandbox capability")
    # Reject links before any experiment operation. This is a fixture guard,
    # not a security boundary against concurrent hostile filesystem mutation.
    if any((root / name).is_symlink() for name in FILES):
        raise RuntimeError("symlinks are outside this experiment")
    result = (write(root, selected, denial == "deny") if mode == "write"
              else recover(root, selected, expected=intent_for_demo()))
    print(json.dumps({"event": "result", "result": result}), flush=True)


if __name__ == "__main__":
    worker_main()
