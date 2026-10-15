"""Deterministic directory adapter; all outputs are private intermediates."""
from __future__ import annotations
import bisect
from collections import Counter
import json
import os
from pathlib import Path
import re
import stat

from .css_scan import contexts, scan
from .literals import json_candidates, literal_candidates, load_rules
from .safeio import Limits, ToolkitError, bounded_read, digest

SCHEMA = "original-static-snapshot/v1"
TEXT_EXTENSIONS = {".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json"}
LIMITATIONS = [
    "Static file/declaration/literal observations only; no target code is imported or executed.",
    "Flag additions are not product commitments, rollout status, entitlement or future release evidence.",
    "JS/TS matching is lexical, not AST binding/data-flow analysis: aliases, shadowing, minification, regex ambiguities, templates and escapes can cause misses/false matches.",
    "Tool/schema-shaped objects are static candidates, not the live tool registry, validated runtime schema or server behavior.",
    "Telemetry literals do not prove an event is emitted, transmitted, collected or associated with a person.",
    "CSS parser is a bounded block/declaration scanner, not a full CSS grammar; no cascade, computed styles, theme activation or color evaluation.",
    "Only listed text extensions are scanned. HTML inline styles, source-map sourcesContent, nested archives, native binaries and remote resources are not recursively analyzed.",
    "Outputs may contain private paths/names/literals; keep them private and review before publication. Raw packages, fonts and full source are not copied into reports.",
    "Use a quiescent, isolated input directory. This is not a sandbox against a process concurrently swapping ancestor directories.",
]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def css_candidates(data):
    nodes, validation = scan(data)
    records, issues = [], []
    if any(validation.values()):
        issues.append("css-unbalanced-syntax")
    if len(nodes) > 200000:
        raise ToolkitError("CSS block bound exceeded")
    for i, node in enumerate(nodes):
        ctx = contexts(nodes, i)
        if len(ctx) > 64 or sum(map(len, ctx)) + len(node["prelude"]) > 4096:
            issues.append("css-context-bound")
            continue
        scope = ctx + [node["prelude"]]
        for decl in node["decl"]:
            if not decl["name"].startswith("--"):
                continue
            if len(decl["name"]) > 256 or len(decl["value"]) > 4096:
                issues.append("css-declaration-bound")
                continue
            record = {"category": "css_tokens", "key": decl["name"], "scope": scope, "value": decl["value"], "kind": "custom-property-declaration", "confidence": "static-declaration", "start": decl["start"], "end": decl["end"]}
            records.append(record)
            if re.search(r"(?i)(?:#[0-9a-f]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\s*\()", decl["value"]) or re.search(r"(?:gray|red|orange|yellow|green|aqua|blue|violet|magenta|neutral)-\d+$", decl["name"]):
                records.append({**record, "category": "css_palettes", "kind": "palette-or-color-expression-candidate"})
    return records, sorted(set(issues))


def snapshot(root: Path, label: str, limits=Limits(), rules=None):
    if root.is_symlink() or not root.is_dir():
        raise ToolkitError("Input must be an existing, non-symlink directory")
    root = root.resolve()
    rules = load_rules(rules)
    files, records, issues = [], [], []
    total_bytes, entries = 0, 0
    stack = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        if depth > limits.max_depth:
            raise ToolkitError("Directory depth bound exceeded")
        # Bound enumeration before sorting, including non-files/directories.
        children = []
        with os.scandir(directory) as scan_dir:
            for child in scan_dir:
                entries += 1
                if entries > limits.max_files:
                    raise ToolkitError("Directory entry bound exceeded")
                children.append(child)
        for entry in sorted(children, key=lambda x: x.name):
            path = Path(entry.path)
            logical = path.relative_to(root).as_posix()
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                stack.append((path, depth+1))
                continue
            if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
                files.append({"path": logical, "bytes": info.st_size, "sha256": None, "status": "skipped-link-or-special"})
                issues.append({"path": logical, "reason": "skipped-link-or-special"})
                continue
            total_bytes += info.st_size
            if total_bytes > limits.max_total_bytes:
                raise ToolkitError("Directory total byte bound exceeded")
            file = {"path": logical, "bytes": info.st_size, "sha256": None, "status": "hashed-only"}
            files.append(file)
            if info.st_size > limits.max_file_bytes:
                file["status"] = "skipped-file-size-bound"
                issues.append({"path": logical, "reason": file["status"]})
                continue
            data = bounded_read(path, limits.max_file_bytes)
            file["sha256"] = digest(data)
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                data.decode("utf-8")  # Reject bad provenance, never replace bytes.
                if path.suffix.lower() == ".css":
                    candidates, warnings = css_candidates(data)
                    issues.extend({"path": logical, "reason": warning} for warning in warnings)
                elif path.suffix.lower() == ".json":
                    candidates = json_candidates(data, rules)
                else:
                    candidates = literal_candidates(data, rules)
                file["status"] = "scanned"
            except (UnicodeError, ValueError, RecursionError) as exc:
                file["status"] = "scan-incomplete"
                # Keep error class only: parser messages can contain private source.
                issues.append({"path": logical, "reason": "scanner-rejected-input", "error_type": type(exc).__name__})
                continue
            newlines = [i for i, byte in enumerate(data) if byte == 10]
            for candidate in candidates:
                source = {"path": logical, "sha256": file["sha256"]}
                if "start" in candidate:
                    start, end = candidate.pop("start"), candidate.pop("end")
                    source.update({"byte_start": start, "byte_end": end, "line": bisect.bisect_left(newlines, start)+1})
                if "json_pointer" in candidate:
                    source["json_pointer"] = candidate.pop("json_pointer")
                candidate["source"] = source
                records.append(candidate)
                if len(records) > limits.max_records:
                    raise ToolkitError("Inventory record bound exceeded")
    files.sort(key=lambda f: f["path"])
    records.sort(key=canonical)
    issues.sort(key=canonical)
    policy = {"adapter": "unpacked-directory-v1", "scanner_version": "1.0.1", "extensions": sorted(TEXT_EXTENSIONS), "rules": rules, "limits": limits.dictionary()}
    result = {"schema": SCHEMA, "label": label, "identity": {"tree_sha256": digest(canonical(files).encode()), "policy_sha256": digest(canonical(policy).encode()), "version_label_verified": False}, "policy": policy, "coverage": {"complete_within_declared_scope": not issues, "issues": issues, "entry_count": entries, "regular_file_bytes": total_bytes, "file_status_counts": dict(sorted(Counter(f["status"] for f in files).items()))}, "files": files, "records": records, "limitations": LIMITATIONS}
    result["identity"]["snapshot_sha256"] = digest(canonical(result).encode())
    return result


def verify_snapshot(doc):
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ToolkitError("Unsupported snapshot schema")
    try:
        identity = dict(doc["identity"])
        declared = identity.pop("snapshot_sha256")
        if declared != digest(canonical({**doc, "identity": identity}).encode()):
            raise ToolkitError("Snapshot digest mismatch")
        if identity["tree_sha256"] != digest(canonical(doc["files"]).encode()) or identity["policy_sha256"] != digest(canonical(doc["policy"]).encode()):
            raise ToolkitError("Snapshot tree/policy digest mismatch")
        if not isinstance(doc["files"], list) or not isinstance(doc["records"], list):
            raise ToolkitError("Malformed snapshot lists")
        if not isinstance(doc["label"], str) or not isinstance(doc["limitations"], list) or any(not isinstance(item, str) for item in doc["limitations"]):
            raise ToolkitError("Malformed snapshot description")
        if not isinstance(doc["coverage"], dict) or not isinstance(doc["coverage"]["complete_within_declared_scope"], bool):
            raise ToolkitError("Malformed snapshot coverage")
        for file in doc["files"]:
            if not isinstance(file["path"], str) or type(file["bytes"]) is not int or file["bytes"] < 0:
                raise ToolkitError("Malformed snapshot file identity")
            if file["sha256"] is not None and (not isinstance(file["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", file["sha256"])):
                raise ToolkitError("Malformed snapshot file digest")
        paths = [f["path"] for f in doc["files"]]
        if len(paths) != len(set(paths)):
            raise ToolkitError("Duplicate snapshot file paths")
        files = {file["path"]: file for file in doc["files"]}
        for record in doc["records"]:
            if record["category"] not in ("css_tokens", "css_palettes", "flags", "tool_contracts", "telemetry") or not isinstance(record["key"], str) or not isinstance(record["scope"], list) or any(not isinstance(part, str) for part in record["scope"]):
                raise ToolkitError("Malformed snapshot record")
            if not isinstance(record["kind"], str) or not isinstance(record["confidence"], str) or "value" not in record:
                raise ToolkitError("Malformed snapshot record metadata")
            source = record["source"]
            file = files[source["path"]]
            if not file["sha256"] or source["sha256"] != file["sha256"]:
                raise ToolkitError("Snapshot record source digest mismatch")
            if "json_pointer" in source:
                if not isinstance(source["json_pointer"], str) or (source["json_pointer"] and not source["json_pointer"].startswith("/")):
                    raise ToolkitError("Malformed snapshot JSON pointer")
            elif any(type(source[key]) is not int for key in ("byte_start", "byte_end", "line")) or not (0 <= source["byte_start"] <= source["byte_end"] <= file["bytes"]) or source["line"] < 1:
                raise ToolkitError("Malformed snapshot byte range")
        return doc
    except (KeyError, TypeError) as exc:
        raise ToolkitError("Malformed snapshot") from exc
