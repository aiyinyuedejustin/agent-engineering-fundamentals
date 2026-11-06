#!/usr/bin/env python3
"""Original stdlib-only transport fault lab; no upstream framework execution.

Uses a self-written, loopback-only JSON-line server, controlled local subprocesses,
an OS pipe and a configured PTY. No model calls, credentials, internet, packages,
Docker, provider SDKs or cloud resources. All owned tasks/processes are joined.
"""
from __future__ import annotations

import argparse
import asyncio
import codecs
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import pty
import select
import subprocess
import sys
import termios
import time


def check(name: str, observed: dict, condition: bool, kind: str) -> dict:
    if not condition:
        raise AssertionError(f"{name}: {observed}")
    return {"id": name, "kind": kind, "passed": True, "observed": observed}


class ReceiptServer:
    """Small controlled server, intentionally not a production implementation.

    A lock serializes its in-memory commit/cache pair. Neither durable storage nor
    crash recovery is modeled. With bind_body=False, key reuse is intentionally
    unsafe for different operation bodies, to demonstrate the extra obligation.
    """
    def __init__(self, dedupe: bool = False, bind_body: bool = False):
        self.dedupe = dedupe
        self.bind_body = bind_body
        self.ledger: list[dict] = []
        self.receipts: dict[str, tuple[int, dict]] = {}
        self.lock = asyncio.Lock()
        self.tasks: set[asyncio.Task] = set()
        self.committed = asyncio.Event()

    async def __aenter__(self):
        self.server = await asyncio.start_server(self.handle, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]
        return self

    async def __aexit__(self, *_):
        self.server.close()
        await self.server.wait_closed()
        if self.tasks:
            await asyncio.wait_for(asyncio.gather(*list(self.tasks)), 5)

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        self.tasks.add(task)
        try:
            req = json.loads(await asyncio.wait_for(reader.readline(), 5))
            key, amount = req["id"], req["amount"]
            async with self.lock:
                cached = self.receipts.get(key) if self.dedupe else None
                if cached and self.bind_body and cached[0] != amount:
                    result = {"error": "idempotency_key_body_mismatch"}
                elif cached:
                    result = cached[1]
                else:
                    await asyncio.sleep(req.get("delay_sec", 0))
                    result = {"receipt": len(self.ledger) + 1,
                              "amount": amount, "id": key}
                    self.ledger.append(dict(result))
                    if self.dedupe:
                        self.receipts[key] = (amount, result)
                    self.committed.set()
            if not req.get("drop_reply", False):
                writer.write((json.dumps(result) + "\n").encode())
                await writer.drain()
        except (BrokenPipeError, ConnectionResetError):
            # A disconnected client is not interpreted as operation cancellation.
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except (BrokenPipeError, ConnectionResetError):
                pass
            self.tasks.discard(task)

    async def request(self, key="operation", amount=1, timeout=2, **options):
        reader, writer = await asyncio.open_connection("127.0.0.1", self.port)
        try:
            writer.write((json.dumps({"id": key, "amount": amount, **options}) + "\n").encode())
            await writer.drain()
            raw = await asyncio.wait_for(reader.readline(), timeout)
            if not raw:
                return {"transport": "eof_without_receipt"}
            return json.loads(raw)
        except TimeoutError:
            return {"transport": "client_wait_timeout"}
        finally:
            writer.close()
            await writer.wait_closed()


async def server_cases() -> list[dict]:
    kind = "original_loopback_server_experiment"
    out = []
    async with ReceiptServer() as server:
        first = await server.request(key="attempt-1", drop_reply=True)
        second = await server.request(key="attempt-2")
        out.append(check("lost_response_blind_retry_duplicates", {
            "first": first, "retry": second, "commits": len(server.ledger),
        }, first["transport"] == "eof_without_receipt" and len(server.ledger) == 2, kind))
    async with ReceiptServer() as server:
        await server.request(key="same-id", drop_reply=True)
        await server.request(key="same-id")
        out.append(check("request_id_alone_is_not_idempotency", {
            "commits": len(server.ledger), "ids": [r["id"] for r in server.ledger],
        }, len(server.ledger) == 2, kind))
    async with ReceiptServer(dedupe=True) as server:
        await server.request(drop_reply=True)
        retry = await server.request()
        out.append(check("deduplicated_retry_returns_original_receipt", {
            "commits": len(server.ledger), "retry": retry,
        }, len(server.ledger) == 1 and retry["receipt"] == 1, kind))
    async with ReceiptServer(dedupe=True) as server:
        response = await server.request(delay_sec=0.08, timeout=0.01)
        at_timeout = len(server.ledger)
        await asyncio.wait_for(server.committed.wait(), 2)
        retry = await server.request()
        out.append(check("client_timeout_does_not_cancel_server_commit", {
            "client": response, "commits_at_timeout": at_timeout,
            "commits_after_wait": len(server.ledger), "retry": retry,
        }, response["transport"] == "client_wait_timeout"
            and at_timeout == 0 and len(server.ledger) == 1, kind))
    async with ReceiptServer(dedupe=True) as server:
        responses = await asyncio.gather(
            server.request(delay_sec=0.02), server.request(delay_sec=0.02))
        out.append(check("concurrent_key_claim_is_atomic_in_this_server", {
            "commits": len(server.ledger), "receipts": [r["receipt"] for r in responses],
        }, len(server.ledger) == 1 and responses[0] == responses[1], kind))
    async with ReceiptServer(dedupe=True, bind_body=False) as weak:
        await weak.request(amount=1)
        wrong = await weak.request(amount=99)
    async with ReceiptServer(dedupe=True, bind_body=True) as bound:
        await bound.request(amount=1)
        rejected = await bound.request(amount=99)
        out.append(check("idempotency_key_needs_operation_binding", {
            "unbound_second_response": wrong, "bound_second_response": rejected,
            "requested_second_amount": 99,
        }, wrong["amount"] == 1
            and rejected["error"] == "idempotency_key_body_mismatch", kind))
    return out


def pipe_eof_case() -> dict:
    """No timing race: an owned holder releases its FD only on our stdin signal."""
    read_fd, write_fd = os.pipe()
    holder = None
    try:
        holder = subprocess.Popen([
            sys.executable, "-c",
            "import sys; print('ready', flush=True); sys.stdin.buffer.read(1)",
        ], pass_fds=(write_fd,), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
           stderr=subprocess.PIPE)
        assert holder.stdout.readline() == b"ready\n"
        first = subprocess.run([
            sys.executable, "-c", "import os,sys; os.write(int(sys.argv[1]), b'ONE')",
            str(write_fd),
        ], pass_fds=(write_fd,), capture_output=True, timeout=3)
        os.close(write_fd)
        write_fd = -1
        initial = os.read(read_fd, 3)
        readable_before_release = bool(select.select([read_fd], [], [], 0.02)[0])
        holder.communicate(input=b"x", timeout=3)
        tail = os.read(read_fd, 1)
        return check("pipe_eof_requires_all_writer_fds_closed", {
            "first_process_exit": first.returncode,
            "first_bytes": initial.decode(),
            "eof_ready_while_other_writer_alive": readable_before_release,
            "eof_after_holder_exit": tail == b"",
        }, first.returncode == 0 and initial == b"ONE"
            and not readable_before_release and tail == b"", "actual_local_os_pipe")
    finally:
        if holder is not None and holder.poll() is None:
            holder.kill()
            holder.communicate()
        if write_fd >= 0:
            os.close(write_fd)
        os.close(read_fd)


def pty_case() -> dict:
    code = "import os; os.write(1,b'OUT\\n'); os.write(2,b'ERR\\n')"
    pipe = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=3)
    master, slave = pty.openpty()
    process = None
    try:
        settings = termios.tcgetattr(slave)
        settings[1] |= termios.OPOST | termios.ONLCR
        termios.tcsetattr(slave, termios.TCSANOW, settings)
        process = subprocess.Popen([sys.executable, "-c", code], stdout=slave, stderr=slave)
        os.close(slave)
        slave = -1
        chunks = []
        while True:
            if not select.select([master], [], [], 3)[0]:
                raise TimeoutError("owned PTY child did not close")
            try:
                chunk = os.read(master, 4096)
            except OSError as exc:
                if exc.errno != errno.EIO:
                    raise
                break
            if not chunk:
                break
            chunks.append(chunk)
        process.wait(timeout=3)
        combined = b"".join(chunks)
        return check("configured_pty_changes_channels_and_newlines", {
            "pipe_stdout": pipe.stdout.decode(), "pipe_stderr": pipe.stderr.decode(),
            "pty_combined": combined.decode(), "pty_opost_onlcr": True,
        }, pipe.stdout == b"OUT\n" and pipe.stderr == b"ERR\n"
            and combined == b"OUT\r\nERR\r\n", "actual_local_configured_pty")
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        if slave >= 0:
            os.close(slave)
        os.close(master)


def decoder_case() -> dict:
    original = "结果✓"
    chunks = [bytes([value]) for value in original.encode("utf-8")]
    lossy = "".join(chunk.decode("utf-8", errors="replace") for chunk in chunks)
    decoder = codecs.getincrementaldecoder("utf-8")()
    restored = "".join(decoder.decode(chunk) for chunk in chunks) + decoder.decode(b"", final=True)
    return check("stream_chunks_are_not_text_character_boundaries", {
        "original": original, "per_chunk_replace": lossy, "incremental": restored,
        "byte_chunks": len(chunks),
    }, lossy != original and restored == original, "actual_local_stdlib_decoder")


async def main(output: Path, repetitions: int):
    started = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    rounds = []
    for repetition in range(repetitions):
        cases = await server_cases()
        cases.extend([pipe_eof_case(), pty_case(), decoder_case()])
        rounds.append({"repetition": repetition + 1, "cases": cases})
    report = {
        "experiment": "original transport fault lab",
        "scope": "Self-written loopback server and actual local Python/OS behavior; not upstream SDK, cloud-provider or benchmark reproduction.",
        "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start, 6),
        "python": platform.python_version(), "platform": platform.platform(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "repetitions": repetitions, "case_count": len(rounds[0]["cases"]),
        "passed_assertions": sum(len(r["cases"]) for r in rounds),
        "rounds": rounds,
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["case_count", "repetitions", "passed_assertions", "elapsed_seconds", "script_sha256"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.repetitions <= 20:
        parser.error("repetitions must be between 1 and 20")
    asyncio.run(main(args.output, args.repetitions))
