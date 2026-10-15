"""Compare observed value sets without assuming runtime or release intent."""
from collections import defaultdict
import json

from .inventory import canonical, verify_snapshot

CATEGORIES = ("css_tokens", "css_palettes", "flags", "tool_contracts", "telemetry")


def group(records):
    result = {}
    for record in records:
        identity = canonical([record["category"], record["key"], record["scope"]])
        entry = result.setdefault(identity, {"category": record["category"], "key": record["key"], "scope": record["scope"], "values": {}, "occurrences": 0})
        value_key = canonical(record["value"])
        value = entry["values"].setdefault(value_key, {"value": record["value"], "sources": [], "confidence": [], "kinds": []})
        value["sources"].append(record["source"])
        value["confidence"].append(record["confidence"])
        value["kinds"].append(record["kind"])
        entry["occurrences"] += 1
    for entry in result.values():
        for value in entry["values"].values():
            value["sources"] = sorted({canonical(s): s for s in value["sources"]}.values(), key=canonical)
            value["confidence"] = sorted(set(value["confidence"]))
            value["kinds"] = sorted(set(value["kinds"]))
    return result


def side(entry):
    if entry is None: return None
    return {"values": [entry["values"][key] for key in sorted(entry["values"])], "occurrences": entry["occurrences"]}


def diff_snapshots(old, new):
    verify_snapshot(old)
    verify_snapshot(new)
    warnings = []
    if old["identity"]["policy_sha256"] != new["identity"]["policy_sha256"]:
        warnings.append("Scan policies differ: rule/limit/extension changes can create apparent additions/removals.")
    for label, snapshot in (("old", old), ("new", new)):
        if not snapshot["coverage"]["complete_within_declared_scope"]:
            warnings.append(f"{label} scan has coverage gaps; absence is not proof of removal.")
    left, right = group(old["records"]), group(new["records"])
    changes = {category: {"added": [], "removed": [], "changed": [], "unchanged_keys": 0} for category in CATEGORIES}
    uncertain = []
    for identity in sorted(set(left) | set(right)):
        before, after = left.get(identity), right.get(identity)
        current = after or before
        if before and after and set(before["values"]) == set(after["values"]):
            changes[current["category"]]["unchanged_keys"] += 1
            continue
        status = "added" if before is None else "removed" if after is None else "changed"
        item = {"key": current["key"], "scope": current["scope"], "before": side(before), "after": side(after)}
        reasons = list(warnings)
        if current["category"] in ("flags", "tool_contracts", "telemetry"):
            reasons.append("Static candidate only; runtime binding, availability and behavior are unverified.")
        if any(len(x["values"]) > 1 for x in (before, after) if x):
            reasons.append("Multiple observed values: no cross-file precedence or runtime selection was resolved.")
        item["interpretation"] = "uncertain-candidate" if reasons else "observed-static-value-set-change"
        changes[current["category"]][status].append(item)
        if reasons:
            uncertain.append({"category": current["category"], "key": current["key"], "scope": current["scope"], "observed_change": status, "reasons": reasons})
    old_files, new_files = ({f["path"]: f for f in s["files"]} for s in (old, new))
    files = {"added": [], "removed": [], "changed": [], "unresolved": [], "possible_moves": []}
    for path in sorted(set(old_files) | set(new_files)):
        a, b = old_files.get(path), new_files.get(path)
        if not a: files["added"].append(b)
        elif not b: files["removed"].append(a)
        elif not a["sha256"] or not b["sha256"]:
            files["unresolved"].append({"path": path, "before": a, "after": b})
        elif a["sha256"] != b["sha256"]:
            files["changed"].append({"path": path, "before": a, "after": b})
    # Only unique exact byte matches; never infer a rename from hashed filenames.
    removed, added = defaultdict(list), defaultdict(list)
    for file in files["removed"]:
        if file["sha256"]: removed[file["sha256"]].append(file["path"])
    for file in files["added"]:
        if file["sha256"]: added[file["sha256"]].append(file["path"])
    for sha in sorted(set(removed) & set(added)):
        if len(removed[sha]) == len(added[sha]) == 1:
            files["possible_moves"].append({"old_path": removed[sha][0], "new_path": added[sha][0], "sha256": sha, "interpretation": "identical-bytes-possible-move-not-proven-rename"})
    return {"schema": "original-static-diff/v1", "old": {"label": old["label"], **old["identity"]}, "new": {"label": new["label"], **new["identity"]}, "scope": "Differences between observed static inventories; not a release roadmap or a runtime schema diff.", "warnings": warnings, "files": files, "inventories": changes, "uncertain_candidates": uncertain, "limitations": old["limitations"]}


def readable(report):
    def safe(value):
        text = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for char in "\\`*_[]()#|": text = text.replace(char, "\\"+char)
        return text.replace("\n", " ").replace("\r", " ")
    def values(entry):
        if entry is None: return "（未观察到）"
        return safe(json.dumps([x["value"] for x in entry["values"]], ensure_ascii=False, sort_keys=True))
    lines = ["# 静态版本差分", "", f"{safe(report['old']['label'])} → {safe(report['new']['label'])}", "", "新增旗标不代表未来产品承诺。工具声明候选不等于运行时 schema；遥测字符串不证明实际发送。", "", "同一 category + key + CSS 上下文按值集合比较，忽略文件改名和出现次数；不恢复加载顺序。版本标签由调用者提供，未验证。", ""]
    for warning in report["warnings"]: lines.append("- 覆盖警告：" + safe(warning))
    for category in CATEGORIES:
        changes = report["inventories"][category]
        lines += ["", "## " + category, "", f"新增 {len(changes['added'])}，移除 {len(changes['removed'])}，值变化 {len(changes['changed'])}，值集合未变 {changes['unchanged_keys']}。"]
        for status, title in (("added", "新增"), ("removed", "移除"), ("changed", "值变化")):
            for item in changes[status]:
                lines += ["", f"### {title}：{safe(item['key'])}", "", "- 上下文："+safe(" / ".join(item["scope"]) or "未解析运行时作用域"), "- 旧值："+values(item["before"]), "- 新值："+values(item["after"]), "- 判读："+item["interpretation"]]
                for label in ("before", "after"):
                    if item[label]:
                        for value in item[label]["values"]:
                            for source in value["sources"]:
                                anchor = "JSON pointer " + source["json_pointer"] if "json_pointer" in source else f"bytes {source['byte_start']}:{source['byte_end']}"
                                lines.append(f"- {label} 定位：{safe(source['path'])}，{safe(anchor)}，SHA-256 {safe(source['sha256'])}")
    lines += ["", "## 文件变化", ""]
    for key in ("added", "removed", "changed", "unresolved", "possible_moves"):
        lines.append(f"- {key}: {len(report['files'][key])}")
    for entry in report["files"]["possible_moves"]:
        lines.append(f"- 相同字节候选移动：{safe(entry['old_path'])} → {safe(entry['new_path'])}；不能证明是重命名。")
    lines += ["", "## 待人工复核的候选", ""]
    for item in report["uncertain_candidates"]:
        lines.append(f"- {item['category']} / {safe(item['key'])} / {item['observed_change']}: " + safe(" ".join(item["reasons"])))
    if not report["uncertain_candidates"]: lines.append("本次差分没有额外标记的候选；仍只代表声明范围内的静态事实。")
    lines += ["", "## 范围与限制", ""] + ["- "+safe(x) for x in report["limitations"]]
    return "\n".join(lines) + "\n"
