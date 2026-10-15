"""Safe runner and JSON evidence collector; Python standard library only."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import queue
import secrets
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone

import protocol


class Sandbox:
    """Own exactly one TemporaryDirectory and only the Popen handles we create."""
    def __enter__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="logical-crash-cut-")
        self.root = Path(self.temporary.name)
        self.token = secrets.token_hex(24)
        (self.root / ".lab-owner").write_text(self.token)
        self.put("settings.json", protocol.encode(protocol.OLD))
        return self

    def __exit__(self, *args):
        self.temporary.cleanup()

    def put(self, name: str, data: bytes):
        if name not in protocol.FILES:
            raise ValueError("only fixed fixture filenames are allowed")
        (self.root / name).write_bytes(data)

    def read(self, name: str) -> bytes:
        if name not in protocol.FILES:
            raise ValueError("only fixed fixture filenames are allowed")
        return (self.root / name).read_bytes()

    def snapshot(self) -> dict:
        files = {}
        for name in protocol.FILES:
            path = self.root / name
            if path.exists():
                data = path.read_bytes()
                stat = path.stat()
                item = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                        "inode": stat.st_ino, "mtime_ns": stat.st_mtime_ns}
                try:
                    item["json"] = json.loads(data)
                except (ValueError, UnicodeError):
                    item["json"] = "unknown: invalid JSON"
                files[name] = item
        target = files.get("settings.json", {}).get("json")
        return {"files": files, "target": target if isinstance(target, dict) else "unknown"}

    def run(self, mode: str, cut: str | None = None, deny_rename: bool = False) -> dict:
        valid = protocol.WRITE_CUTS if mode == "write" else protocol.RECOVERY_CUTS if mode == "recover" else ()
        if mode not in ("write", "recover") or cut not in (None, *valid):
            raise ValueError("unsupported mode or checkpoint")
        env = {**os.environ, "CRASH_CUT_ROOT": str(self.root), "CRASH_CUT_TOKEN": self.token}
        command = [sys.executable, "-B", str(Path(__file__).with_name("protocol.py")),
                   mode, cut or "none", "deny" if deny_rename else "allow"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, env=env)
        messages = queue.Queue()
        reader = threading.Thread(target=lambda: messages.put(process.stdout.readline()), daemon=True)
        reader.start()
        try:
            try:
                line = messages.get(timeout=15)
            except queue.Empty as error:
                raise RuntimeError("worker produced no handshake/result") from error
            if not line:
                _, stderr = process.communicate(timeout=5)
                raise RuntimeError(f"worker exited without a result: {stderr}")
            event = json.loads(line)
            if cut is not None:
                if event != {"event": "paused", "checkpoint": cut}:
                    raise RuntimeError(f"wrong checkpoint handshake: {event}")
                process.terminate()  # Only this Popen child; no PID or process-group lookup.
                stdout, stderr = process.communicate(timeout=5)
                if process.returncode == 0:
                    raise RuntimeError("checkpoint child unexpectedly exited normally")
                stop_method = "Popen.terminate-after-checkpoint-handshake"
            else:
                stdout, stderr = process.communicate(timeout=5)
                if process.returncode != 0 or event.get("event") != "result":
                    raise RuntimeError(f"worker failed: {event}; {stderr}")
                stop_method = "normal-exit"
            if stdout or stderr:
                raise RuntimeError(f"unexpected worker output: {stdout!r}; {stderr!r}")
            return {"mode": mode, "checkpoint": cut, "exit_code": process.returncode,
                    "stop_method": stop_method, **event, "state": self.snapshot()}
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()  # Last-resort cleanup, still only our exact handle.
                    process.wait(timeout=5)
            reader.join(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                stream.close()


def scenario(name: str, cut: str = "C4", mutation: str | None = None,
             recovery_cuts: tuple[str, ...] = (), deny_rename: bool = False) -> dict:
    with Sandbox() as box:
        initial = box.run("write", None if deny_rename else cut, deny_rename)
        if mutation == "newer-target":
            box.put("settings.json", protocol.encode({"revision": 9, "label": "third-party"}))
        elif mutation == "corrupt-candidate":
            box.put("candidate.json", b'{"revision":8,"label":"damaged"}\n')
        elif mutation == "wrong-receipt":
            receipt = protocol.expected_receipt(protocol.intent_for_demo())
            receipt["operationId"] = "different-operation"
            box.put("receipt.json", protocol.encode(receipt))
        before_recovery = box.snapshot()
        recovery = [box.run("recover", phase) for phase in recovery_cuts]
        recovery.extend([box.run("recover"), box.run("recover")])
        return {"case": name, "writer": initial, "mutation": mutation,
                "before_recovery": before_recovery, "recoveries": recovery}


def collect() -> dict:
    cases = [scenario(cut, cut) for cut in protocol.WRITE_CUTS]
    cases += [scenario("stale-journal-vs-r9", mutation="newer-target"),
              scenario("corrupt-candidate", mutation="corrupt-candidate"),
              scenario("wrong-operation-receipt", "C5", mutation="wrong-receipt"),
              scenario("rename-refused", deny_rename=True),
              scenario("recovery-stops-after-rename", recovery_cuts=("R_RENAME",)),
              scenario("recovery-stops-after-receipt", recovery_cuts=("R_RECEIPT",)),
              scenario("recovery-stops-after-commit", recovery_cuts=("R_COMMIT",)),
              scenario("recovery-stops-twice", recovery_cuts=("R_RENAME", "R_RECEIPT"))]
    source_hashes = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                     for name in ("protocol.py", "lab.py", "test_crash_cuts.py")}
    return {"scope": "original single-writer logical process-stop/restart model",
            "excluded": ["hardware power loss", "fsync durability", "Claude execution proof",
                         "concurrent writers", "in-place write fallback"],
            "synthetic_torn_files": ["C1: fixed candidate prefix", "C3: fixed journal prefix"],
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_sha256": source_hashes,
            "python": platform.python_version(), "platform": platform.platform(),
            "case_count": len(cases), "cases": cases}


if __name__ == "__main__":
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
