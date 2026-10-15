#!/usr/bin/env python3
"""Offline, standard-library-first CLI. Python 3.10+."""
from __future__ import annotations
import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from toolkit.diffing import diff_snapshots, readable
from toolkit.inventory import snapshot
from toolkit.literals import load_rules
from toolkit.safeio import Limits, ToolkitError, bounded_read, extract_zip
from toolkit.asar import extract_asar, inspect_asar, atomic_publish


def emit(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def read_json(path):
    return json.loads(bounded_read(path, 256 * 1024 * 1024))


def prepare_output(output, inputs):
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise ToolkitError("Output must not exist; choose a new private directory/file")
    if not output.parent.is_dir():
        raise ToolkitError("Output parent must already exist")
    resolved = output.parent.resolve() / output.name
    for source in inputs:
        source = source.resolve()
        if source == resolved or (source.is_dir() and source in resolved.parents):
            raise ToolkitError("Output must be outside all input directories")
    return resolved


def write_report(output, report, old=None, new=None):
    temp = Path(tempfile.mkdtemp(prefix=".reverse-toolkit-report-", dir=output.parent))
    try:
        if old is not None: emit(temp / "before.json", old)
        if new is not None: emit(temp / "after.json", new)
        emit(temp / "diff.json", report)
        (temp / "diff.md").write_text(readable(report), encoding="utf-8")
        if output.exists() or output.is_symlink():
            raise ToolkitError("Output appeared during operation")
        atomic_publish(temp, output)
    except BaseException:
        shutil.rmtree(temp)
        raise


def positive(value):
    value = int(value)
    if value <= 0: raise argparse.ArgumentTypeError("must be positive")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline static inventories; no download, no target execution")
    sub = parser.add_subparsers(dest="command", required=True)
    def scan_options(p, rules=True):
        if rules: p.add_argument("--rules", type=Path, help="Explicit literal rule lists; see rules command")
        p.add_argument("--max-file-mib", type=positive, default=64)
        p.add_argument("--max-total-mib", type=positive, default=512)
        p.add_argument("--max-files", type=positive, default=20000)
    snap = sub.add_parser("snapshot", help="Inventory an already unpacked directory")
    snap.add_argument("--input", type=Path, required=True)
    snap.add_argument("--label", required=True)
    snap.add_argument("--output", type=Path, required=True)
    scan_options(snap)
    compare = sub.add_parser("compare", help="One command: two directories → snapshots + JSON/Markdown diff")
    compare.add_argument("--old", type=Path, required=True)
    compare.add_argument("--new", type=Path, required=True)
    compare.add_argument("--old-label", default="old-unverified-label")
    compare.add_argument("--new-label", default="new-unverified-label")
    compare.add_argument("--output", type=Path, required=True)
    scan_options(compare)
    diff = sub.add_parser("diff", help="Compare verified snapshot files")
    diff.add_argument("--old-snapshot", type=Path, required=True)
    diff.add_argument("--new-snapshot", type=Path, required=True)
    diff.add_argument("--output", type=Path, required=True)
    unpack = sub.add_parser("unpack-zip", help="Extract bounded stored/deflated non-ZIP64 ZIP to a new directory")
    unpack.add_argument("--input", type=Path, required=True)
    unpack.add_argument("--output", type=Path, required=True)
    scan_options(unpack, rules=False)
    asar = sub.add_parser("unpack-asar", help="Extract the strict bounded ASAR subset; no links or sidecars")
    asar.add_argument("--input", type=Path, required=True)
    asar.add_argument("--output", type=Path, required=True)
    scan_options(asar, rules=False)
    inspect = sub.add_parser("inspect-asar", help="Read-only ASAR compatibility report with explicit exclusions")
    inspect.add_argument("--input", type=Path, required=True)
    scan_options(inspect, rules=False)
    sub.add_parser("rules", help="Print default rule JSON, without reading inputs")
    args = parser.parse_args(argv)
    try:
        if args.command == "rules":
            print(json.dumps(load_rules(), ensure_ascii=False, indent=2))
            return 0
        limits = Limits()
        if hasattr(args, "max_files"):
            limits = replace(limits, max_files=args.max_files, max_file_bytes=args.max_file_mib*1024*1024, max_total_bytes=args.max_total_mib*1024*1024)
        rules = load_rules(read_json(args.rules)) if getattr(args, "rules", None) else None
        if args.command == "inspect-asar":
            print(json.dumps(inspect_asar(args.input, limits), sort_keys=True))
        elif args.command == "snapshot":
            out = prepare_output(args.output, [args.input])
            result = snapshot(args.input, args.label, limits, rules)
            emit(out, result)
            print(json.dumps({"snapshot": str(out), "records": len(result["records"]), "coverage_complete": result["coverage"]["complete_within_declared_scope"]}))
        elif args.command == "compare":
            out = prepare_output(args.output, [args.old, args.new])
            old, new = snapshot(args.old, args.old_label, limits, rules), snapshot(args.new, args.new_label, limits, rules)
            report = diff_snapshots(old, new)
            write_report(out, report, old, new)
            print(json.dumps({"report_directory": str(out), "uncertain_candidates": len(report["uncertain_candidates"]), "coverage_warnings": report["warnings"]}))
        elif args.command == "diff":
            out = prepare_output(args.output, [args.old_snapshot, args.new_snapshot])
            report = diff_snapshots(read_json(args.old_snapshot), read_json(args.new_snapshot))
            write_report(out, report)
            print(json.dumps({"report_directory": str(out), "uncertain_candidates": len(report["uncertain_candidates"])}))
        else:
            out = prepare_output(args.output, [args.input])
            adapter = extract_asar if args.command == "unpack-asar" else extract_zip
            print(json.dumps(adapter(args.input, out, limits), sort_keys=True))
        return 0
    except (ToolkitError, OSError, ValueError, RuntimeError, RecursionError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
