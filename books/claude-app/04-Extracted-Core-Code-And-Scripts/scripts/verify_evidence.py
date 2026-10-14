#!/usr/bin/env python3
"""Verify selected local evidence identities and anchors. Never execute target files.
A pass does not establish semantic attribution, CSS activation or runtime behavior.
"""
import argparse, hashlib, json
from pathlib import Path


def bounded(base, relative):
    base = base.resolve()
    target = (base / relative).resolve()
    if not target.is_relative_to(base):
        raise ValueError('Source escapes input root: ' + relative)
    return target


def verify(data_dir, resources, asar):
    counts = {'file_reads': 0, 'selected_declarations': 0, 'component_rules': 0, 'javascript_anchors': 0}
    failures = []
    def read(relative, digest, size=None):
        if relative.startswith('ion/'):
            path = bounded(resources / 'ion-dist', relative[4:])
        elif relative.startswith('asar/'):
            path = bounded(asar, relative[5:])
        elif relative.startswith('app.asar/'):
            path = bounded(asar, relative[9:])
        else:
            path = bounded(resources, relative)
        raw = path.read_bytes(); counts['file_reads'] += 1
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('SHA-256 mismatch: ' + relative)
        if size is not None and len(raw) != size:
            raise ValueError('Size mismatch: ' + relative)
        return raw
    def check(label, operation):
        try: operation()
        except (OSError, ValueError, KeyError, AssertionError) as exc:
            failures.append({'check':label,'error':str(exc) or type(exc).__name__})
    def css():
        x=json.loads((data_dir/'design-token-summary.json').read_text())
        raw={f['id']:read(f['path'],f['sha256'],f['bytes']) for f in x['sources']}
        blocks={b['id']:b for b in x['blocks']}
        def walk(value, key=''):
            if isinstance(value,dict):
                if 'ref' in value:
                    bid,start,end=value['ref']; b=blocks[bid]
                    assert b['byte_start'] <= start < end <= b['byte_end'], 'Reference outside block'
                    content=raw[b['source']][start:end].decode('utf-8')
                    if key.startswith('--'):
                        assert content == key+':'+value['declared'], 'Declaration differs: '+key
                    counts['selected_declarations'] += 1
                for k,v in value.items():walk(v,k)
            elif isinstance(value,list):
                for v in value:walk(v,key)
        walk(x)
    def rules():
        x=json.loads((data_dir/'design-component-rules.json').read_text())
        raw={f['id']:read(f['path'],f['sha256'],f['bytes']) for f in x['sources']}
        for o in x['observations']:
            for a in o['anchors']:
                content=raw[a['source']][a['byte_start']:a['byte_end']].decode('utf-8')
                assert content.startswith(a['selector']+'{'), o['id']+': selector mismatch'
                counts['component_rules'] += 1
    def components():
        x=json.loads((data_dir/'component-trace.json').read_text())
        raw={p:read(p,f['sha256'],f['size_bytes']) for p,f in x['files'].items()}
        for c in x['claims']:
            for a in c['evidence']:
                blob=raw[a['file']]; start=a['utf8_byte_offset']; anchor=a['anchor'].encode()
                assert blob[start:start+len(anchor)] == anchor, c['id']+': literal mismatch'
                if 'occurrence_zero_based' in a:
                    assert blob[:start].count(anchor)==a['occurrence_zero_based'], c['id']+': occurrence differs'
                counts['javascript_anchors'] += 1
    for label,fn in [('selected CSS declarations',css),('component CSS selectors',rules),('JavaScript anchors',components)]:check(label,fn)
    return {'passed':not failures,'checks':counts,'failures':failures,'scope':'Identity and literal references only; no target execution, semantic attribution, CSS cascade, runtime or rendering verification.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--resources',required=True,type=Path,help='Extracted resources directory containing ion-dist')
    ap.add_argument('--asar-root',required=True,type=Path,help='Already extracted app.asar directory')
    ap.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[2]/'04-Extracted-Core-Code-And-Scripts/evidence/data')
    ap.add_argument('--report',type=Path)
    args=ap.parse_args(); result=verify(args.data,args.resources,args.asar_root)
    output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.report:args.report.write_text(output)
    print(output,end='');raise SystemExit(0 if result['passed'] else 1)
