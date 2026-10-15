#!/usr/bin/env python3
"""Read-only, dependency-free publication checks; see README.md for the contract."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

VERSION = "1.1.0"
SCHEMA = "publication-integrity-report/v1"
EXCLUDED = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv"}
MAX_DOCUMENT_BYTES = 8 * 1024 * 1024
PUNCT = r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
ESCAPE = re.compile(r"\\([" + re.escape(PUNCT) + r"])")


class CheckError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def normalize(path, base=""):
    """Normalize POSIX paths without ever allowing traversal above the book root."""
    if not isinstance(path, str) or "\x00" in path or "\\" in path:
        raise CheckError("invalid_path", "Path must be a NUL-free POSIX path without backslashes")
    if path.startswith("/"):
        raise CheckError("outside_root", "Absolute filesystem paths are not allowed")
    parts = []
    for part in (base + "/" + path if base else path).split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                raise CheckError("outside_root", "Path traverses outside the publication root")
            parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


class SafeTree:
    """POSIX directory-descriptor access: never follow a symlink in any component."""
    def __init__(self, root):
        if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
            raise CheckError("platform_unsupported", "POSIX dir_fd and O_NOFOLLOW are required")
        self.root = os.path.abspath(root)
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
        try:
            for part in self.root.split("/"):
                if not part:
                    continue
                new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = new
        except OSError:
            os.close(fd)
            raise CheckError("root_unreadable", "Root or an ancestor is missing, unreadable, or a symlink")
        self.fd = fd

    def close(self):
        os.close(self.fd)

    def open(self, path):
        path = normalize(path)
        if any(part in EXCLUDED for part in path.split("/")):
            raise CheckError("excluded_path", "Metadata/dependency directories are outside the read scope")
        fd = os.dup(self.fd)
        try:
            for index, part in enumerate(path.split("/") if path else []):
                info = os.stat(part, dir_fd=fd, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    raise CheckError("symlink_rejected", "Symlink traversal is not allowed")
                if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                    raise CheckError("special_file_rejected", "Only regular files and directories are allowed")
                flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
                if index < len(path.split("/")) - 1:
                    flags |= os.O_DIRECTORY
                new = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = new
            return fd
        except FileNotFoundError:
            os.close(fd)
            raise CheckError("missing_path", "Path does not exist")
        except (OSError, CheckError) as exc:
            os.close(fd)
            if isinstance(exc, CheckError):
                raise
            raise CheckError("path_unreadable", "Path is unreadable, changed, or is not a directory")

    def kind(self, path):
        fd = self.open(path)
        try:
            mode = os.fstat(fd).st_mode
            return "directory" if stat.S_ISDIR(mode) else "file" if stat.S_ISREG(mode) else "special"
        finally:
            os.close(fd)

    def read(self, path, limit=MAX_DOCUMENT_BYTES):
        fd = self.open(path)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise CheckError("not_regular_file", "Expected a regular file")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read(limit + 1)
            if len(data) > limit:
                raise CheckError("document_too_large", "Document exceeds the 8 MiB parsing limit")
            return data
        finally:
            os.close(fd)

    def digest(self, path):
        fd = self.open(path)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise CheckError("not_regular_file", "Expected a regular file")
            digest, size = hashlib.sha256(), 0
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
            after = os.fstat(fd)
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise CheckError("changed_during_read", "File changed while it was being hashed")
            return digest.hexdigest(), size
        finally:
            os.close(fd)

    def walk(self, path=""):
        fd = self.open(path)
        try:
            for name in sorted(os.listdir(fd)):
                rel = normalize(name, path)
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if name in EXCLUDED and stat.S_ISDIR(info.st_mode):
                    yield "excluded", rel
                elif stat.S_ISLNK(info.st_mode):
                    yield "symlink", rel
                elif stat.S_ISDIR(info.st_mode):
                    yield from self.walk(rel)
                elif stat.S_ISREG(info.st_mode):
                    yield "file", rel
                else:
                    yield "special", rel
        finally:
            os.close(fd)


def without_inline_code(line):
    """Same-line, equal-length backtick delimiters only; preserve offsets."""
    return re.sub(r"(`+)(?!`)(.*?)\1(?!`)", lambda m: " " * len(m.group()), line)


def visible_lines(text, warnings=None):
    """Skip frontmatter, comments, ordinary fences and indented code."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n".join(" " * len(s) for s in m.group().split("\n")), text, flags=re.S)
    fence = None
    front = text.startswith("---\n") or text.startswith("---\r\n")
    for number, line in enumerate(text.splitlines(), 1):
        if front:
            if number > 1 and line in ("---", "..."):
                front = False
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            continue
        if match:
            fence = match[1]
            continue
        if line.startswith(("    ", "\t")):
            if warnings is not None and re.search(r"</?[A-Za-z][^>]*>|</?[A-Za-z][A-Za-z0-9-]*(?:\s|>|$)|<[!?]", line):
                warnings.append((number, "unsupported_indented_html", "Unfenced indented HTML may continue a paragraph; conservatively unverified"))
            continue
        yield number, line


def github_slug(text):
    """Documented basic GitHub rule, for the explicitly supported heading subset."""
    escaped = []
    def protect(match):
        escaped.append(match[1])
        return chr(0xE000 + len(escaped) - 1)
    text = ESCAPE.sub(protect, text)
    def protect_code(match):
        escaped.append(match[2])
        return chr(0xE000 + len(escaped) - 1)
    text = re.sub(r"(`+)(.*?)\1", protect_code, text)
    text = re.sub(r"(?<!\w)(_+)(.+?)\1(?!\w)", r"\2", text)
    text = re.sub(r"(\*+|~~)(.+?)\1", r"\2", text)
    for index, value in enumerate(escaped):
        text = text.replace(chr(0xE000 + index), value)
    text = text.strip().lower()
    return "".join("-" if c == " " else c for c in text
                   if c in " -_" or unicodedata.category(c)[0] in "LMN")


def bounded_id(value):
    return isinstance(value, str) and 1 <= len(value) <= 128 and all(
        c in "_-" or unicodedata.category(c)[0] in "LN" for c in value)


def destination(line, start):
    """Parse one inline destination, balanced parentheses, escapes, optional title."""
    i = start
    while i < len(line) and line[i] in " \t":
        i += 1
    if i < len(line) and line[i] == "<":
        end = i + 1
        while end < len(line) and (line[end] != ">" or line[end - 1] == "\\"):
            end += 1
        if end == len(line):
            return None
        raw, i = line[i + 1:end], end + 1
    else:
        begin, depth = i, 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line):
                i += 2
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth == 0:
                    break
                depth -= 1
            elif ch.isspace() and depth == 0:
                break
            i += 1
        if depth:
            return None
        raw = line[begin:i]
    while i < len(line) and line[i] in " \t":
        i += 1
    if i < len(line) and line[i] in "\"'":
        quote, i = line[i], i + 1
        while i < len(line) and line[i] != quote:
            i += 2 if line[i] == "\\" else 1
        i += 1
        while i < len(line) and line[i] in " \t":
            i += 1
    if i >= len(line) or line[i] != ")":
        return None
    return raw, i + 1


def label_end(line, start):
    """Find a balanced label without interpreting its inline formatting."""
    depth, i = 1, start + 1
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "[":
            depth += 1
        elif line[i] == "]":
            depth -= 1
            if not depth:
                return i
        i += 1
    return len(line)


def reference_key(label):
    return re.sub(r"\s+", " ", ESCAPE.sub(r"\1", label).strip()).casefold()


def markdown(text):
    """Return supported links, heading anchors and explicit coverage warnings."""
    links, warnings, anchors, used = [], [], set(), set()
    explicit = Counter()
    source_lines = text.splitlines()
    headings_complete = True
    if re.search(r"[\v\f\x1c-\x1e\x85\u2028\u2029]", text):
        warnings.append((1, "unsupported_line_separator", "Non-CR/LF separators are outside the Markdown line subset"))
        headings_complete = False
    lines = list(visible_lines(text, warnings))
    if any(code == "unsupported_indented_html" for _, code, _ in warnings):
        headings_complete = False
    references, definition_lines = {}, set()
    for number, line in lines:
        match = re.match(r"^ {0,3}\[([^\]]+)\]:[ \t]*(.*)$", line)
        if match:
            definition_lines.add(number)
            result = destination(match[2] + ")", 0) if match[2] else None
            if result is None or result[1] != len(match[2]) + 1:
                warnings.append((number, "unsupported_reference", "Multiline or unsupported reference definition"))
            else:
                references.setdefault(reference_key(match[1]), result[0])
    if text.startswith(("---\n", "---\r\n")) and not any(line in ("---", "...") for line in text.splitlines()[1:]):
        warnings.append((1, "unsupported_frontmatter", "Unterminated YAML frontmatter; content was not scanned"))
        headings_complete = False
    for idx, (number, line) in enumerate(lines):
        if number in definition_lines:
            continue
        heading = re.match(r"^ {0,3}#{1,6}(?:[ \t]+(.*?)|[ \t]*)$", line)
        title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[1] or "") if heading else None
        if title is None and idx + 1 < len(lines):
            next_number, next_line = lines[idx + 1]
            if next_number == number + 1 and line.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", next_line):
                title = line.strip()
        if title is not None:
            if re.search(r"[\[\]<>]|&(?:#[xX]?[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);|\{#|\$|:[A-Za-z0-9_+-]+:", title):
                warnings.append((number, "unsupported_heading", "Heading contains links, HTML/entities, explicit IDs, math, or emoji shortcodes"))
                headings_complete = False
            else:
                base, suffix = github_slug(title), 0
                slug = base
                while slug in used:
                    suffix += 1
                    slug = base + "-" + str(suffix)
                used.add(slug)
                anchors.add(slug)
        visible = without_inline_code(line)
        if re.search(r"(?<!\\)`", visible):
            warnings.append((number, "unsupported_code_span", "Unmatched or multiline inline-code delimiter; line link parsing skipped"))
            headings_complete = False
            continue
        empty_anchor = re.fullmatch(r' {0,3}<a id="([^"<>]+)"></a>[ \t]*', source_lines[number - 1])
        isolated = ((number == 1 or not source_lines[number - 2].strip(" \t"))
                    and (number == len(source_lines) or not source_lines[number].strip(" \t")))
        if empty_anchor and bounded_id(empty_anchor[1]) and isolated and line == source_lines[number - 1]:
            explicit[empty_anchor[1]] += 1
            continue
        html_visible = re.sub(r"\]\(\s*<[^>\n]*>\s*", "](", visible)
        html_visible = re.sub(r"<(?:https?://|mailto:)[^>]*>", "", html_visible)
        html_visible = re.sub(r"<br\s*/?>", "", html_visible, flags=re.I)
        if re.search(r"</?[A-Za-z][^>]*>|</?[A-Za-z][A-Za-z0-9-]*(?:\s|>|$)|<[!?]", html_visible):
            warnings.append((number, "unsupported_html", "Raw HTML/MDX links, anchors, and block semantics are not parsed"))
            headings_complete = False
        if re.match(r"^ {0,3}(?:>\s*|[-+*]\s+|\d+[.)]\s+)(?:#{1,6}\s|`{3,}|~{3,})", visible):
            warnings.append((number, "unsupported_container", "Headings/fences inside lists or blockquotes are not parsed"))
            headings_complete = False
        i = 0
        while i < len(visible):
            if visible[i] == "\\":
                i += 2
                continue
            if visible[i] != "[":
                i += 1
                continue
            end = label_end(visible, i)
            label = line[i + 1:end]
            nested = "[" in ESCAPE.sub("", label)
            inner_image = None
            # Common linked-image form: [![alt](image.svg)](destination.md).
            if nested and label.startswith("!["):
                inner_end = label_end(label, 1)
                if inner_end + 1 < len(label) and label[inner_end + 1] == "(":
                    inner_image = destination(label, inner_end + 2)
                    if inner_image and inner_image[1] == len(label) and "[" not in label[2:inner_end]:
                        nested = False
            if end + 1 < len(visible) and visible[end + 1] == "(":
                result = destination(line, end + 2)
                if nested or result is None:
                    warnings.append((number, "unsupported_link", "Malformed, nested-label, multiline, or unsupported title syntax"))
                    i = end + 2
                else:
                    raw, i = result
                    if inner_image:
                        links.append((number, inner_image[0]))
                    links.append((number, raw))
            elif end + 1 < len(visible) and visible[end + 1] == "[":
                close = label_end(visible, end + 1)
                key = reference_key(line[end + 2:close] or label)
                if key in references:
                    if nested:
                        warnings.append((number, "unsupported_link", "Nested reference-link label is outside the subset"))
                    else:
                        links.append((number, references[key]))
                i = close + 1
            else:
                key = reference_key(label)
                if end < len(visible) and key in references:
                    links.append((number, references[key]))
                i = max(end + 1, i + 1)
    if "<!--" in re.sub(r"<!--.*?-->", "", text, flags=re.S):
        warnings.append((1, "unsupported_comment", "Unterminated HTML comment"))
        headings_complete = False
    for anchor, count in explicit.items():
        if count != 1 or anchor in anchors:
            warnings.append((1, "unsupported_anchor_collision", "Explicit anchor duplicates an ID or heading slug"))
            headings_complete = False
        anchors.add(anchor)
    return links, anchors, headings_complete, warnings


class Checker:
    def __init__(self, tree, contract):
        self.tree, self.contract = tree, contract
        self.issues, self.counts, self.cache = [], Counter(), {}
        self.excluded, self.manifests = [], []

    def issue(self, severity, code, path, message, line=None, **details):
        record = dict(severity=severity, code=code, path=path, message=message)
        if line is not None:
            record["line"] = line
        if details:
            record["details"] = details
        self.issues.append(record)

    def document(self, path):
        if path not in self.cache:
            try:
                data = self.tree.read(path)
                parsed = markdown(data.decode("utf-8-sig"))
                self.cache[path] = parsed
                self.counts["markdown_files_read"] += 1
                for line, code, message in parsed[3]:
                    self.issue("unsupported", code, path, message, line)
            except (CheckError, UnicodeDecodeError) as exc:
                self.issue("error", getattr(exc, "code", "invalid_utf8"), path, str(exc))
                self.cache[path] = ([], set(), False, [])
        return self.cache[path]

    def structure(self):
        for group in self.contract["required"]:
            for path in group["paths"]:
                self.counts["required_paths_checked"] += 1
                try:
                    kind = self.tree.kind(path)
                    if kind != group["kind"]:
                        self.issue("error", "wrong_path_type", path, "Required " + group["kind"] + " is a " + kind)
                except CheckError as exc:
                    self.issue("error", exc.code, path, str(exc), group=group["name"])

    def link(self, source, line, raw):
        self.counts["markdown_links_found"] += 1
        raw = html.unescape(ESCAPE.sub(r"\1", raw))
        try:
            parsed = urlsplit(raw)
        except ValueError:
            self.issue("unsupported", "invalid_url", source, "URL cannot be parsed", line, target=raw)
            return
        if parsed.scheme.lower() in ("http", "https", "mailto", "tel") or raw.startswith("//"):
            self.counts["external_links_not_checked"] += 1
            return
        if parsed.scheme:
            self.issue("unsupported", "unsupported_scheme", source, "URL scheme is outside the local-file contract", line, target=raw)
            return
        try:
            if re.search(r"%(?![0-9a-fA-F]{2})", parsed.path + parsed.fragment):
                raise CheckError("invalid_percent_encoding", "Malformed percent encoding")
            path = unquote(parsed.path, encoding="utf-8", errors="strict")
            fragment = unquote(parsed.fragment, encoding="utf-8", errors="strict")
            if path.startswith("/"):
                prefix = "/" + self.contract["repository_prefix"].strip("/")
                if path == prefix:
                    path = ""
                elif path.startswith(prefix + "/"):
                    path = path[len(prefix) + 1:]
                else:
                    raise CheckError("outside_root", "Repository-root link is outside the book prefix")
                target = normalize(path)
            else:
                target = normalize(path, str(PurePosixPath(source).parent)) if path else source
            kind = self.tree.kind(target)
            self.counts["local_paths_checked"] += 1
            if parsed.query:
                self.counts["local_queries_ignored"] += 1
            if fragment:
                if kind == "directory":
                    self.issue("unsupported", "directory_fragment", source, "Directory rendering/README selection is not inferred", line, target=raw)
                elif PurePosixPath(target).suffix.lower() not in (".md", ".markdown"):
                    self.issue("unsupported", "non_markdown_fragment", source, "HTML/PDF/source-line fragments are not checked", line, target=raw)
                else:
                    _, anchors, complete, _ = self.document(target)
                    if not complete:
                        self.issue("unsupported", "fragment_incomplete", source, "Target has unsupported heading or HTML semantics", line, target=raw)
                    elif fragment not in anchors:
                        self.issue("error", "missing_heading", source, "No matching supported heading or explicit-anchor fragment", line, target=raw, resolved_path=target)
                    else:
                        self.counts["heading_fragments_checked"] += 1
        except (CheckError, UnicodeDecodeError) as exc:
            self.issue("error", getattr(exc, "code", "invalid_utf8_url"), source, str(exc), line, target=raw)

    def manifest(self, path):
        record = dict(path=path, entries=0, matched=0)
        self.manifests.append(record)
        issue_start = len(self.issues)
        try:
            value = json.loads(self.tree.read(path).decode("utf-8"), object_pairs_hook=unique_json_object)
            files = value.get("files") if isinstance(value, dict) else None
            if isinstance(files, dict):
                entries = [{"path": p, "sha256": h} for p, h in files.items()]
            elif isinstance(files, list):
                entries = files
            else:
                raise CheckError("manifest_schema", "Expected files array or path-to-sha256 object")
            if not entries:
                raise CheckError("manifest_schema", "Manifest must contain at least one entry")
            record["entries"] = len(entries)
            seen = set()
            for entry in entries:
                self.counts["manifest_entries_checked"] += 1
                if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-fA-F]{64}", entry["sha256"]):
                    self.issue("error", "manifest_schema", path, "Entry requires path and 64-digit SHA-256")
                    continue
                try:
                    target = normalize(entry["path"], str(PurePosixPath(path).parent))
                except CheckError as exc:
                    self.issue("error", exc.code, path, str(exc), target=entry["path"])
                    continue
                if target in seen:
                    self.issue("error", "manifest_duplicate", path, "Duplicate normalized manifest entry", target=target)
                    continue
                seen.add(target)
                try:
                    digest, size = self.tree.digest(target)
                    if digest != entry["sha256"].lower():
                        self.issue("error", "manifest_hash_drift", path, "Listed file hash no longer matches", target=target, expected=entry["sha256"], actual=digest)
                    elif "bytes" in entry and (type(entry["bytes"]) is not int or entry["bytes"] != size):
                        self.issue("error", "manifest_size_drift", path, "Listed byte count no longer matches", target=target, expected=entry["bytes"], actual=size)
                    else:
                        record["matched"] += 1
                except CheckError as exc:
                    self.issue("error", exc.code, path, str(exc), target=target)
        except (CheckError, ValueError, UnicodeDecodeError) as exc:
            self.issue("error", getattr(exc, "code", "manifest_invalid_json"), path, str(exc))
        record["status"] = "failed" if len(self.issues) > issue_start else "passed"

    def run(self):
        started = datetime.now(timezone.utc).isoformat()
        def stage_status(issues):
            return "failed" if any(x["severity"] == "error" for x in issues) else "incomplete" if issues else "passed"
        self.structure()
        structure_end = len(self.issues)
        checks = {"required_structure": {"status": stage_status(self.issues)}}
        try:
            for kind, path in self.tree.walk():
                if kind == "excluded":
                    self.excluded.append(path)
                elif kind in ("symlink", "special"):
                    self.issue("error", kind + "_rejected", path, "Entry was not followed or read")
                elif PurePosixPath(path).suffix.lower() in (".md", ".markdown"):
                    for line, raw in self.document(path)[0]:
                        self.link(path, line, raw)
        except (CheckError, OSError) as exc:
            self.issue("error", getattr(exc, "code", "walk_failed"), "", "Tree traversal failed: " + str(exc))
        markdown_end = len(self.issues)
        checks["markdown_links"] = {"status": stage_status(self.issues[structure_end:markdown_end])}
        for path in self.contract["manifests"]:
            self.manifest(path)
        checks["listed_manifest_hashes"] = {"status": stage_status(self.issues[markdown_end:])}
        levels = Counter(item["severity"] for item in self.issues)
        status = "failed" if levels["error"] else "incomplete" if levels["unsupported"] else "passed"
        return dict(schema=SCHEMA, checker_version=VERSION, status=status,
                    started_at=started, finished_at=datetime.now(timezone.utc).isoformat(),
                    root=self.tree.root, repository_prefix=self.contract["repository_prefix"],
                    snapshot="Read-only non-atomic filesystem observation; rerun after publication edits settle.",
                    scope={"required_structure": True, "markdown": "documented inline/reference-link, basic-heading and standalone empty-anchor subset only",
                           "manifests": "explicitly listed SHA-256 entries only; not provenance or complete inventory",
                           "source_code_executed": False, "network_used": False, "secret_scan": False,
                           "security_audit": False, "excluded_directory_names": sorted(EXCLUDED),
                           "excluded_directories_observed": self.excluded,
                           "document_parse_limit_bytes": MAX_DOCUMENT_BYTES},
                    summary=dict(self.counts, errors=levels["error"], unsupported=levels["unsupported"]),
                    checks=checks, manifests=self.manifests, issues=self.issues)


def validate_contract(value):
    if not isinstance(value, dict) or value.get("schema") != "publication-integrity-contract/v1":
        raise ValueError("Unsupported contract schema")
    if not isinstance(value.get("repository_prefix"), str):
        raise ValueError("repository_prefix must be a POSIX relative path")
    normalize(value["repository_prefix"])
    if not isinstance(value.get("required"), list) or not isinstance(value.get("manifests"), list):
        raise ValueError("required and manifests must be arrays")
    for group in value["required"]:
        if not isinstance(group, dict) or group.get("kind") not in ("directory", "file") or not isinstance(group.get("name"), str) or not isinstance(group.get("paths"), list):
            raise ValueError("Invalid required group")
        for path in group["paths"]:
            normalize(path)
    for path in value["manifests"]:
        normalize(path)
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Publication root, not repository root")
    parser.add_argument("--contract", default=os.path.join(os.path.dirname(__file__), "contract.json"))
    args = parser.parse_args(argv)
    tree = None
    try:
        # The caller explicitly selects this local JSON configuration, never executable code.
        with open(args.contract, encoding="utf-8") as stream:
            contract = validate_contract(json.load(stream, object_pairs_hook=unique_json_object))
        tree = SafeTree(args.root)
        report = Checker(tree, contract).run()
        code = 1 if report["status"] == "failed" else 2 if report["status"] == "incomplete" else 0
    except (OSError, ValueError, CheckError) as exc:
        report = dict(schema=SCHEMA, checker_version=VERSION, status="invalid_run",
                      issues=[dict(severity="error", code=getattr(exc, "code", "invalid_configuration"), message=str(exc))])
        code = 2
    finally:
        if tree:
            tree.close()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    summary = report.get("summary", {})
    print("publication-check: {} (errors={}, unsupported={}); exit {}".format(
        report["status"], summary.get("errors", "?"), summary.get("unsupported", "?"), code), file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
