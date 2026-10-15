#!/usr/bin/env python3
"""One offline transaction: two directories/ZIPs -> private inputs and diff.

Python 3.10+. Install beside reverse_toolkit.py and toolkit/. Input packages
are never imported, executed, downloaded, or passed to another executable.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import zipfile

from reverse_toolkit import emit, prepare_output, read_json, write_report
from toolkit.diffing import diff_snapshots
from toolkit.inventory import snapshot
from toolkit.literals import load_rules
from toolkit.safeio import Limits, ToolkitError, extract_zip


def input_kind(source: Path):
    """Select the adapter, without following a final-component input link."""
    mode = source.lstat().st_mode
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "zip"
    raise ToolkitError("Inputs must be non-symlink directories or regular ZIP files")


def compare_versions(old: Path, new: Path, output: Path,
                     old_label="old-unverified-label", new_label="new-unverified-label",
                     rules=None):
    """Build privately, publish the whole run only after every step succeeds.

    Inputs and the output parent must be quiescent, isolated local paths.
    This preserves the audited toolkit's contract; it is not a sandbox
    against a process concurrently replacing ancestor directories.
    """
    sources = (("old", old, old_label), ("new", new, new_label))
    kinds = {side: input_kind(source) for side, source, _ in sources}
    out = prepare_output(output, [old, new])
    limits = Limits()  # Exactly the audited defaults; no capacity bypass flags.
    rules = load_rules(rules)
    stage = Path(tempfile.mkdtemp(prefix=".diff-versions-", dir=out.parent))
    try:
        # mkdtemp creates the run's outer boundary with mode 0700 on POSIX.
        # A separate private parent keeps extracted source away from reports.
        inputs = stage / "inputs"
        inputs.mkdir(mode=0o700)
        inventories, adapters = {}, {}
        for side, source, label in sources:
            if kinds[side] == "directory":
                root = source
                adapters[side] = {"adapter": "unpacked-directory-v1", "copied": False}
            else:
                root = inputs / side
                try:
                    extraction = extract_zip(source, root, limits)
                except (ToolkitError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
                    raise ToolkitError(
                        f"{side} input rejected by the bounded ZIP adapter: {exc}. "
                        "Only the audited stored/deflated ZIP subset is supported. "
                        "For ASAR, DMG, DEB, RPM, 7z, TAR or other packaging, "
                        "extract manually with a trusted tool, then pass the directory."
                    ) from exc
                adapters[side] = {**extraction, "private_root": f"inputs/{side}"}
            inventories[side] = snapshot(root, label, limits, rules)

        report = diff_snapshots(inventories["old"], inventories["new"])
        # Reuse the audited exclusive writer and report renderer unchanged.
        write_report(stage / "report", report, inventories["old"], inventories["new"])
        os.chmod(stage / "report" / "diff.md", 0o600)
        emit(stage / "run.json", {
            "schema": "original-version-diff-run/v1",
            "inputs": adapters,
            "limits": limits.dictionary(),
            "report": "report/diff.md",
            "private": True,
            "notice": "Entire output is private. Extracted packages, snapshots and reports require review before sharing.",
        })
        if out.exists() or out.is_symlink():
            raise ToolkitError("Output appeared during operation; nothing was replaced")
        stage.rename(out)
    except BaseException:
        # Remove only our private staging directory, never an output that
        # appeared meanwhile. shutil.rmtree refuses a symlink at its root.
        shutil.rmtree(stage)
        raise

    return {
        "output_directory": str(out),
        "report_directory": str(out / "report"),
        "markdown_report": str(out / "report" / "diff.md"),
        "json_report": str(out / "report" / "diff.json"),
        "private_inputs_directory": str(out / "inputs"),
        "uncertain_candidates": len(report["uncertain_candidates"]),
        "coverage_warnings": report["warnings"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="One offline command: directories and/or bounded ZIPs -> fresh private staging + static diff",
        epilog=("No downloads, installers or target code execution. ASAR/DMG/DEB/etc. "
                "need manual trusted extraction first. Keep inputs and output parent "
                "quiescent and isolated. Output must be outside input directories."),
    )
    parser.add_argument("old", type=Path, help="Old unpacked directory or local ZIP-subset archive")
    parser.add_argument("new", type=Path, help="New unpacked directory or local ZIP-subset archive")
    parser.add_argument("--output", type=Path, required=True, help="New private run directory; its parent must exist")
    parser.add_argument("--old-label", default="old-unverified-label")
    parser.add_argument("--new-label", default="new-unverified-label")
    parser.add_argument("--rules", type=Path, help="Same bounded literal-rule JSON accepted by reverse_toolkit.py")
    args = parser.parse_args(argv)
    try:
        rules = load_rules(read_json(args.rules)) if args.rules else None
        result = compare_versions(args.old, args.new, args.output, args.old_label, args.new_label, rules)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ToolkitError, OSError, ValueError, RuntimeError, RecursionError,
            zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
