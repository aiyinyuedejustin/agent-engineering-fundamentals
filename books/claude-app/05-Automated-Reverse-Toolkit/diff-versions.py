#!/usr/bin/env python3
"""One offline transaction: two directories/ZIPs/ASARs -> private inputs and diff.

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
from toolkit.asar import extract_asar, atomic_publish


def input_kind(source: Path):
    """Select the adapter, without following a final-component input link."""
    mode = source.lstat().st_mode
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "asar" if source.suffix.lower() == ".asar" else "zip"
    raise ToolkitError("Inputs must be non-symlink directories or regular ZIP/ASAR files")


def rejection_guidance(kind, error):
    """Explain rejection without suggesting an integrity-check bypass."""
    code = getattr(error, "code", "")
    diagnostic = str(error)
    if (code == "declared-integrity-failure" or (not code and (
            "integrity mismatch" in diagnostic or (kind == "zip" and (
                "CRC" in diagnostic or "size mismatch" in diagnostic))))):
        target = "archive and exact matching companion" if kind == "asar" else "archive"
        return (f"Stop: verify the {target} against a trusted source and check the declared "
                "sizes and integrity metadata. Never bypass integrity checks, rewrite declarations, "
                "or switch extraction tools to accept mismatched bytes.")
    if kind != "asar":
        return ("Only the strict ZIP subset is supported. For unsupported packaging, "
                "extract manually with a trusted tool, then pass the directory.")
    if code == "coverage-mismatch":
        return ("Verify the selected archive and exact companion against a trusted source; "
                "check the reported missing/extra/invalid paths and declared sizes. "
                "Do not skip unmatched files or treat them as feature removals.")
    if "changed" in code or (not code and "changed" in str(error)):
        return ("The input changed. Verify a fresh, quiescent copy from a trusted source "
                "before retrying; no partial comparison was published.")
    if code == "unsupported-host-no-follow-primitives":
        return ("Use a host with the required no-follow filesystem primitives. "
                "Do not weaken the sidecar safety checks.")
    if code in ("root-io-failure", "inventory-io-failure", "read-failure"):
        return ("Check the explicit companion path and read access, then verify the selected "
                "archive and companion against a trusted source. Unknown coverage is not completeness.")
    return ("Use inspect-asar to review the archive declarations and exclusions, and verify "
            "the selected input against a trusted source. Unresolved ASAR exclusions fail "
            "the whole run; do not skip files or bypass validation.")


def compare_versions(old: Path, new: Path, output: Path,
                     old_label="old-unverified-label", new_label="new-unverified-label",
                     rules=None, *, old_unpacked_dir=None, new_unpacked_dir=None):
    """Build privately, publish the whole run only after every step succeeds.

    Inputs and the output parent must be quiescent, isolated local paths.
    This preserves the audited toolkit's contract; it is not a sandbox
    against a process concurrently replacing ancestor directories.
    """
    sources = (("old", old, old_label), ("new", new, new_label))
    kinds = {side: input_kind(source) for side, source, _ in sources}
    companions = {"old": old_unpacked_dir, "new": new_unpacked_dir}
    for side, companion in companions.items():
        if companion is not None and kinds[side] != "asar":
            raise ToolkitError(f"{side} unpacked-dir requires an ASAR input")
    out = prepare_output(output, [old, new] + [p for p in companions.values() if p is not None])
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
                    if kinds[side] == "asar":
                        extraction = extract_asar(source, root, limits, unpacked_dir=companions[side])
                    else:
                        extraction = extract_zip(source, root, limits)
                except (ToolkitError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
                    raise ToolkitError(
                        f"{side} input rejected by the bounded {kinds[side].upper()} adapter: {exc}. "
                        + rejection_guidance(kinds[side], exc)
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
        atomic_publish(stage, out)
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
        description="One offline command: directories and/or bounded ZIPs/ASARs -> fresh private staging + static diff",
        epilog=("No downloads, installers or target code execution. ASAR must be fully supported; DMG/DEB/etc. "
                "need manual trusted extraction first. Keep inputs and output parent "
                "quiescent and isolated. Output must be outside input directories."),
    )
    parser.add_argument("old", type=Path, help="Old unpacked directory or local ZIP/ASAR-subset archive")
    parser.add_argument("new", type=Path, help="New unpacked directory or local ZIP/ASAR-subset archive")
    parser.add_argument("--output", type=Path, required=True, help="New private run directory; its parent must exist")
    parser.add_argument("--old-unpacked-dir", type=Path, help="Explicit exact companion for old ASAR only")
    parser.add_argument("--new-unpacked-dir", type=Path, help="Explicit exact companion for new ASAR only")
    parser.add_argument("--old-label", default="old-unverified-label")
    parser.add_argument("--new-label", default="new-unverified-label")
    parser.add_argument("--rules", type=Path, help="Same bounded literal-rule JSON accepted by reverse_toolkit.py")
    args = parser.parse_args(argv)
    try:
        rules = load_rules(read_json(args.rules)) if args.rules else None
        result = compare_versions(args.old, args.new, args.output, args.old_label, args.new_label, rules,
                                  old_unpacked_dir=args.old_unpacked_dir, new_unpacked_dir=args.new_unpacked_dir)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ToolkitError, OSError, ValueError, RuntimeError, RecursionError,
            zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
