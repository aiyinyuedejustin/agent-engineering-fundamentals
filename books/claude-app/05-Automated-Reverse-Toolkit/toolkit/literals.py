"""Conservative literal candidates, NOT a JavaScript AST or runtime schema."""
from __future__ import annotations
import bisect
import json
import math
import re

from .safeio import ToolkitError, digest

DEFAULT_RULES = {
    "flag_calls": ["checkGate", "check_gate", "getFeatureFlag", "get_feature_flag", "isFeatureEnabled", "isEnabled", "useFeatureFlag", "useGate"],
    "tool_calls": ["registerTool", "defineTool", "register_tool", "define_tool"],
    "telemetry_calls": ["track", "trackEvent", "capture", "logEvent", "emitEvent"],
    "schema_keys": ["input_schema", "output_schema", "inputSchema", "outputSchema", "parameters"],
    "flag_containers": ["feature_flags", "featureFlags", "flags", "gates", "experiments"],
    "event_keys": ["event_key", "event_name", "eventName", "telemetry_event"],
}


def load_rules(value=None):
    rules = DEFAULT_RULES if value is None else value
    if not isinstance(rules, dict) or set(rules) != set(DEFAULT_RULES):
        raise ToolkitError("Rules must contain exactly the documented rule lists")
    for values in rules.values():
        if not isinstance(values, list) or len(values) > 100 or any(not isinstance(v, str) or not re.fullmatch(r"[A-Za-z_$][\w$]{0,127}", v, re.ASCII) for v in values):
            raise ToolkitError("Rules must be bounded literal identifiers, not regular expressions")
    return {k: sorted(set(v)) for k, v in sorted(rules.items())}



def _lexical_error(code, start, cursor, token_count, quote=None):
    """Controlled diagnostics only; never serialize source/token values."""
    known = {
        "js-comment-state-unclosed": ("Unclosed JavaScript comment", "lexical-state"),
        "js-quoted-state-unclosed": ("Unclosed JavaScript string/template", "lexical-state"),
        "js-token-bound-exceeded": ("JavaScript lexical token bound exceeded", "resource-bound"),
    }
    message, category = known[code]
    error = ToolkitError(message)  # Keep the original exception type/behavior.
    error.scan_diagnostic = {
        "schema": "original-scanner-diagnostic/v1",
        "phase": "javascript-tokenization",
        "code": code,
        "category": category,
        "byte_start": start,
        "byte_cursor": cursor,
        "tokens_observed": token_count,
        "input_validity": "not-determined",
    }
    if code == "js-token-bound-exceeded":
        error.scan_diagnostic["token_limit"] = 1000000
    if quote is not None:
        error.scan_diagnostic["quote_kind"] = {"'": "single", '"': "double", "`": "template"}[quote]
    return error


def tokens(data):
    # Latin-1 gives a reversible one-character-per-byte view. Do not eval/import.
    s, out, i = data.decode("latin1"), [], 0
    while i < len(s):
        c, start = s[i], i
        if c.isspace():
            i += 1
            continue
        if s.startswith("//", i):
            end = s.find("\n", i + 2)
            i = len(s) if end < 0 else end + 1
            continue
        if s.startswith("/*", i):
            end = s.find("*/", i + 2)
            if end < 0:
                raise _lexical_error("js-comment-state-unclosed", start, len(s), len(out))
            i = end + 2
            continue
        if c in "\"'`":
            q = c
            i += 1
            while i < len(s) and s[i] != q:
                i += 2 if s[i] == "\\" else 1
            if i >= len(s):
                raise _lexical_error("js-quoted-state-unclosed", start, min(i, len(s)), len(out), q)
            i += 1
            raw = s[start+1:i-1].encode("latin1").decode("utf-8")
            # Escapes and interpolated templates are intentionally not decoded
            # into names: doing so partially would create false identities.
            typ = "string" if "\\" not in raw and not (q == "`" and "${" in raw) else "opaque-string"
            out.append((typ, raw, start, i))
        elif c == "/" and (not out or out[-1][1] in ("=", "(", ",", ":", "return", "[", "!", "?", ";", "{")):
            # A lexical regex-literal guard, not a complete JS grammar.
            i += 1
            bracket = False
            while i < len(s):
                if s[i] == "\\":
                    i += 2
                    continue
                if s[i] == "[": bracket = True
                elif s[i] == "]": bracket = False
                elif s[i] == "/" and not bracket:
                    i += 1
                    break
                elif s[i] in "\r\n": break
                i += 1
            out.append(("opaque-regex", "", start, i))
        elif c.isascii() and (c.isalpha() or c in "_$"):
            i += 1
            while i < len(s) and s[i].isascii() and (s[i].isalnum() or s[i] in "_$"):
                i += 1
            out.append(("identifier", s[start:i], start, i))
        elif c.isdigit():
            i += 1
            while i < len(s) and s[i] in "0123456789.eE+-": i += 1
            out.append(("number", s[start:i], start, i))
        else:
            i += 1
            out.append(("punct", c, start, i))
        if len(out) > 1000000:
            raise _lexical_error("js-token-bound-exceeded", start, min(i, len(s)), len(out))
    return out


def literal_candidates(data, rules):
    ts = tokens(data)
    records = []
    call_types = {name: category for key, category in (("flag_calls", "flags"), ("tool_calls", "tool_contracts"), ("telemetry_calls", "telemetry")) for name in rules[key]}
    for i, token in enumerate(ts):
        typ, name, start, end = token
        if typ == "identifier" and name in call_types and i + 3 < len(ts) and ts[i+1][1] == "(" and ts[i+2][0] == "string" and ts[i+3][1] in (",", ")"):
            arg = ts[i+2]
            if len(arg[1]) > 256:
                continue
            value = {"call_spelling": name}
            if ts[i+3][1] == "," and i + 5 < len(ts) and ts[i+5][1] in (",", ")"):
                default = ts[i+4]
                if default[0] == "string" and len(default[1]) <= 512:
                    value["second_literal"] = default[1]
                elif default[1] in ("true", "false", "null"):
                    value["second_literal"] = json.loads(default[1])
                elif default[0] == "number":
                    try: value["second_literal"] = json.loads(default[1])
                    except ValueError: pass
                    if isinstance(value.get("second_literal"), float) and not math.isfinite(value["second_literal"]):
                        raise ToolkitError("Non-finite JavaScript numeric literal")
            records.append({"category": call_types[name], "key": arg[1], "scope": [], "value": value, "kind": "call-first-literal", "confidence": "lexical-candidate", "start": arg[2], "end": arg[3]})
        if typ in ("identifier", "string") and name in rules["schema_keys"] and i+1 < len(ts) and ts[i+1][1] == ":":
            # Nearby names are NOT associated with a tool: object/scope recovery
            # is deliberately left to AST/REA/manual verification.
            records.append({"category": "tool_contracts", "key": "schema-marker:" + name, "scope": [], "value": {"schema_key": name}, "kind": "unassociated-schema-marker", "confidence": "lexical-candidate", "start": start, "end": end})
        if typ in ("identifier", "string") and name in rules["event_keys"] and i+3 < len(ts) and ts[i+1][1] == ":" and ts[i+2][0] == "string" and ts[i+3][1] in (",", "}"):
            value = ts[i+2]
            if len(value[1]) <= 256:
                records.append({"category": "telemetry", "key": value[1], "scope": [], "value": {"field": name}, "kind": "unassociated-event-field", "confidence": "lexical-candidate", "start": value[2], "end": value[3]})
    return records


def json_candidates(data, rules):
    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ToolkitError("Non-finite JSON number")
        return result
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ToolkitError("Duplicate JSON object key")
            result[key] = value
        return result
    doc = json.loads(data, object_pairs_hook=pairs, parse_float=finite_float, parse_constant=lambda _: (_ for _ in ()).throw(ToolkitError("Non-finite JSON number")))
    records, visited = [], 0
    def add(category, key, value, pointer, kind):
        if len(str(key)) <= 256:
            records.append({"category": category, "key": str(key), "scope": [], "value": value, "kind": kind, "confidence": "static-json-structure", "json_pointer": pointer})
    def walk(node, pointer="", depth=0):
        nonlocal visited
        visited += 1
        if visited > 200000 or depth > 64:
            raise ToolkitError("JSON structural bound exceeded")
        if isinstance(node, dict):
            for key, value in node.items():
                here = pointer + "/" + key.replace("~", "~0").replace("/", "~1")
                if key in rules["flag_containers"] and isinstance(value, dict):
                    for flag, default in value.items():
                        if default is None or isinstance(default, (bool, int, float, str)):
                            if len(json.dumps(default)) <= 1024:
                                add("flags", flag, {"declared_value": default, "container": key}, here + "/" + flag.replace("~", "~0").replace("/", "~1"), "flag-map-member")
                if key in rules["schema_keys"] and isinstance(value, dict):
                    name = node.get("name")
                    contract = {"schema_key": key, "schema_sha256": digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()), "type": value.get("type"), "required": value.get("required", [])}
                    props = value.get("properties", {})
                    if isinstance(props, dict):
                        contract["properties"] = [{"name": n, "type": v.get("type") if isinstance(v, dict) else None} for n, v in sorted(props.items())][:100]
                        contract["property_count"] = len(props)
                    if len(json.dumps(contract)) <= 8192:
                        add("tool_contracts", name if isinstance(name, str) else "schema-marker:"+key, contract, here, "json-schema-shaped-object")
                if key in rules["event_keys"] and isinstance(value, str):
                    add("telemetry", value, {"field": key}, here, "event-name-field")
                walk(value, here, depth+1)
        elif isinstance(node, list):
            for i, value in enumerate(node): walk(value, pointer+"/"+str(i), depth+1)
    walk(doc)
    return records
