#!/usr/bin/env python3
"""Explicit offline DEB projection and one-transaction static version diff."""
from __future__ import annotations
import argparse
from contextlib import ExitStack
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from deb_projection import (Selection, PROFILE, MIB, scan, inspect_deb,
                            require, mkdir_private, _source, _identity)
from toolkit.safeio import Limits, ToolkitError, bounded_read
from toolkit.asar import extract_asar, atomic_publish, _admit
from toolkit.inventory import snapshot, canonical
from toolkit.diffing import diff_snapshots
from toolkit.literals import load_rules
from reverse_toolkit import prepare_output

SIDE_DISK = 512*MIB
REPORT_FILE = 64*MIB
REPORT_TOTAL = 128*MIB
ENVELOPE_REPORT = 16*MIB

class Reports:
    """Count encoded bytes before each exclusive write; no unlimited json.dump."""
    def __init__(self): self.total = 0
    def write(self, path, chunks, limit=REPORT_FILE):
        count = 0
        fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as out:
            for text in chunks:
                # iterencode may return one long string token. Split writes and
                # count encoded bytes; scanner memory is a separate core bound.
                for pos in range(0, len(text), 16384):
                    data = text[pos:pos+16384].encode('utf-8')
                    count += len(data)
                    self.total += len(data)
                    require(count <= limit and self.total <= REPORT_TOTAL, 'Report byte budget')
                    out.write(data)
        return count
    def json(self, path, value, limit=REPORT_FILE):
        encoder = json.JSONEncoder(ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False)
        return self.write(path, encoder.iterencode(value), limit)


def scope_snapshot(doc, selection, platform):
    # Additive policy binding, followed by the core's canonical digest rules.
    doc['policy']['projection'] = dict(profile=PROFILE, selection=asdict(selection), platform=platform,
                                      complete_package=False, complete_application=False)
    doc['identity']['policy_sha256'] = hashlib.sha256(canonical(doc['policy']).encode()).hexdigest()
    del doc['identity']['snapshot_sha256']
    doc['identity']['snapshot_sha256'] = hashlib.sha256(canonical(doc).encode()).hexdigest()
    return doc


def markdown(report, selection):
    def safe(value):
        text = json.dumps(value, ensure_ascii=True).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        for char in '\\`*_[]()#|': text = text.replace(char, '\\'+char)
        return text
    # A deliberately compact wrapper. Detailed values/anchors remain in the
    # unchanged core diff structure in diff.json; do not reproduce giant values.
    yield '# DEB 指定 ASAR 范围静态候选差分\n\n'
    yield '仅比较所选 ASAR 声明范围；整包、安装行为和运行时未比较。\n\n'
    yield 'complete_package=false；complete_application=false；semantic_completeness_proven=false。\n\n'
    yield '- Profile: ' + safe(PROFILE) + '\n'
    yield '- ASAR member: ' + safe(selection.asar) + '\n'
    yield '- Companion prefix: ' + safe(selection.companion) + '\n'
    yield '- Platform label (unverified): ' + safe(report['projection']['platform']) + '\n'
    yield '- Old/new labels (unverified): ' + safe([report['old']['label'],report['new']['label']]) + '\n\n'
    yield '范围摘要见 run.json；完整候选及字节锚点见 diff.json。版本标签未经验证。\n\n'
    yield '非选区成员全部列于 old-envelope.json / new-envelope.json，绝不作为功能删除证据。\n\n'
    yield '## 覆盖警告\n'
    for warning in report['warnings']:
        yield '- ' + json.dumps(warning, ensure_ascii=True) + '\n'
    yield '\n## 候选变化计数\n'
    for category, changes in report['inventories'].items():
        yield f"- {category}: added={len(changes['added'])}, removed={len(changes['removed'])}, changed={len(changes['changed'])}, unchanged={changes['unchanged_keys']}\n"
    yield '\n静态候选不是已确认功能、未来承诺或运行时 schema。缺失不证明移除。原扫描覆盖缺口保留于快照与 JSON 报告。\n'


def compare_debs(old, new, output, selection, *, old_label='old-unverified-label',
                 new_label='new-unverified-label', platform='linux-unverified-label', rules=None):
    require(hasattr(os, 'O_NOFOLLOW'), 'Host lacks no-follow primitive')
    for label in (old_label,new_label,platform):
        require(isinstance(label,str) and 0 < len(label.encode()) <= 4096, 'Label byte budget')
    output = prepare_output(Path(output), [Path(old),Path(new)])
    rules = load_rules(rules)
    stage = None
    try:
        with ExitStack() as stack:
            opened = {}
            envelopes = {}
            for side,path in (('old',old),('new',new)):
                source,size = stack.enter_context(_source(Path(path), Limits()))
                opened[side] = (source,size)
                envelopes[side] = scan(source,size,selection)
            # No selected bytes have been materialized until both complete
            # first passes (including checksum/footer/tail checks) succeed.
            stage = Path(tempfile.mkdtemp(prefix='.deb-projection-', dir=output.parent))
            reports = Reports()
            snapshots, inner = {}, {}
            for side,label in (('old',old_label),('new',new_label)):
                raw = stage/'raw'/side
                mkdir_private(raw)
                source,size = opened[side]
                scan(source,size,selection,raw,envelopes[side])
                archive = raw/'app.asar'
                companion = raw/'companion' if selection.companion else None
                # Admit original ASAR declarations before copying logical alias
                # bytes, preserving default Limits while imposing a stricter
                # independent simultaneous-disk budget.
                with _source(archive, Limits()) as (asar,asar_size):
                    entries, metadata = _admit(asar,asar_size,Limits())
                expanded = sum(e['size'] for e in entries if e['kind'] == 'file')
                require(envelopes[side]['selected_bytes']+expanded <= SIDE_DISK,
                        'Selected raw plus logical extraction disk budget')
                root = stage/'inputs'/side
                mkdir_private(root.parent)
                inner[side] = extract_asar(archive, root, Limits(), unpacked_dir=companion)
                require(inner[side]['expanded_bytes'] == expanded, 'ASAR logical accounting mismatch')
                envelopes[side]['selected_asar_declared_scope_complete'] = True
                snapshots[side] = scope_snapshot(snapshot(root,label,Limits(),rules),selection,platform)
                reports.json(stage/(side+'-envelope.json'),envelopes[side],ENVELOPE_REPORT)
                reports.json(stage/(side+'-snapshot.json'),snapshots[side])
            require(snapshots['old']['identity']['policy_sha256'] == snapshots['new']['identity']['policy_sha256'],
                    'Projection policies differ')
            report = diff_snapshots(snapshots['old'],snapshots['new'])
            report['projection'] = snapshots['old']['policy']['projection']
            report['scope'] = 'Only the explicit ASAR declared scope; not a complete package/application comparison.'
            reports.json(stage/'diff.json',report)
            reports.write(stage/'diff.md',markdown(report,selection))
            run = dict(schema='deb-asar-projection-run/v1',profile=PROFILE,selection=asdict(selection),
                       platform_label=platform, labels=dict(old=old_label,new=new_label),
                       core_limits=Limits().dictionary(), outer_limits=envelopes['old']['limits'],
                       simultaneous_payload_bytes=sum(e['selected_bytes']+inner[s]['expanded_bytes'] for s,e in envelopes.items()),
                       disk_limits=dict(per_side=SIDE_DISK,two_sides=2*SIDE_DISK,report_file=REPORT_FILE,reports=REPORT_TOTAL),
                       inner=inner, scanner_coverage={s:v['coverage'] for s,v in snapshots.items()},
                       scope_policy_sha256=snapshots['old']['identity']['policy_sha256'],
                       complete_package=False,complete_application=False,publisher_authenticity_verified=False,
                       private=True, product_code_executed=False)
            reports.json(stage/'run.json',run)
        # Both original source descriptors/path identities are checked by their
        # context exits before atomic publication, including failures late in scan.
        atomic_publish(stage,output)
        stage = None
        return dict(output_directory=str(output), markdown_report=str(output/'diff.md'),
                    selected_asar_declared_scope_complete=True,complete_package=False,
                    coverage_warnings=report['warnings'])
    finally:
        if stage is not None:
            shutil.rmtree(stage)


def bounded_json_text(value, limit):
    """Admit the entire encoded response before emitting any stdout bytes."""
    result = bytearray()
    for chunk in json.JSONEncoder(ensure_ascii=True,sort_keys=True).iterencode(value):
        encoded = chunk.encode('utf-8')
        require(len(result)+len(encoded)+1 <= limit, 'CLI JSON byte budget')
        result.extend(encoded)
    return result.decode('utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Explicit XZ-only DEB to ASAR scope; never installs or executes input')
    sub = parser.add_subparsers(dest='command',required=True)
    inspect = sub.add_parser('inspect')
    inspect.add_argument('source',type=Path)
    compare = sub.add_parser('compare')
    compare.add_argument('old',type=Path); compare.add_argument('new',type=Path)
    compare.add_argument('--output',required=True,type=Path)
    compare.add_argument('--old-label',default='old-unverified-label')
    compare.add_argument('--new-label',default='new-unverified-label')
    compare.add_argument('--platform-label',default='linux-unverified-label')
    compare.add_argument('--rules',type=Path)
    for p in (inspect,compare):
        p.add_argument('--asar-member',required=True)
        p.add_argument('--companion-prefix')
    args = parser.parse_args(argv)
    try:
        selection = Selection(args.asar_member,args.companion_prefix)
        if args.command == 'inspect':
            result = inspect_deb(args.source,selection)
        else:
            rules = json.loads(bounded_read(args.rules,16*MIB)) if args.rules else None
            result = compare_debs(args.old,args.new,args.output,selection,old_label=args.old_label,
                                  new_label=args.new_label,platform=args.platform_label,rules=rules)
        print(bounded_json_text(result, ENVELOPE_REPORT))
        return 0
    except (ToolkitError,OSError,ValueError,RuntimeError,RecursionError) as exc:
        # Do not echo arbitrary input bytes or unbounded path-bearing OSErrors.
        print(json.dumps(dict(error=type(exc).__name__,message=('Filesystem operation failed' if isinstance(exc,OSError) else str(exc)[:8192]),
                              complete_package=False,outer_envelope_inventory_complete=False,
                              exclusions=None),ensure_ascii=True),file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
