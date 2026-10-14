#!/usr/bin/env python3
"""Extract a private CSS inventory from already-extracted, local package files.

Standard-library only. Never imports/runs application code, opens fonts, extracts
archives, downloads files or copies source stylesheets. Offsets are zero-based
UTF-8 bytes, end-exclusive. The inventory is an intermediate, not a public asset.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from inventory_inputs import source_bases, source_path

PALETTE = re.compile(r'^--cds-(gray|red|orange|yellow|green|aqua|blue|violet|magenta)-\d+$')

def family(n, v):
    if n.startswith('--tw-') or n.startswith('--lightningcss-'): return 'compiler_or_utility_state'
    if PALETTE.match(n): return 'raw_palette'
    if n.startswith('--cds-hsl-') or re.match(r'^--_(?:gray|red|yellow|green|blue|violet|brand)-',n): return 'legacy_v2_palette_bridge'
    if n.startswith('--cds-neutral-'): return 'mode_relative_neutral_palette'
    if n.startswith('--cds-role-'): return 'role_palette_alias'
    if n.startswith('--cds-chart-'): return 'data_visualization'
    if n.startswith('--cds-editor-collaborator-'): return 'collaboration_color'
    if re.search(r'(?:font|text-(?:xs|sm|base|lg|xl|\d+xl)|tracking|leading)', n): return 'typography'
    if re.search(r'(?:ease|dur(?:ation)?|animate|animation|motion|spring)', n): return 'motion'
    if re.search(r'(?:shadow|ring|focus)', n): return 'elevation_focus'
    if re.search(r'(?:radius|corner)', n): return 'shape'
    if re.search(r'(?:^--(?:bg|text|accent|brand|border|danger|oncolor|pictogram|success|warning|always)-)', n): return 'legacy_color'
    if re.search(r'(?:^--cds-(?:surface|fill|bg|text|on|border|alpha|backdrop|clay|heather|plum|cactus|mineral|black|page-bg|pictogram))', n): return 'semantic_color'
    if re.search(r'(?:opacity)', n): return 'opacity'
    if re.search(r'(?:^--(?:cds-)?z-|z-index)', n): return 'layering'
    if re.search(r'(?:gap|space|spacing|pad|inset|gutter|margin)', n): return 'spacing'
    if re.search(r'(?:height|width|size|measure|container|^--cds-(?:h-|w-|icon-|avatar|checkbox|switch|control))', n): return 'sizing'
    if re.search(r'(?:cursor)', n): return 'interaction'
    return 'component_or_other'

def decode(s): return s.encode('latin1').decode('utf-8','replace')

def scan(data):
    """Return flattened blocks and declarations while retaining exact byte ranges."""
    s=data.decode('latin1'); n=len(s); nodes=[]; stack=[]; i=0; seg=0; par=bra=0; quote=None
    def decl(a,b):
        raw=s[a:b]; leading=0
        while True:
            trim=len(raw)-len(raw.lstrip()); leading+=trim; raw=raw.lstrip()
            comment=re.match(r'^/\*.*?\*/',raw,re.S)
            if not comment: break
            leading+=comment.end(); raw=raw[comment.end():]
        raw=raw.rstrip()
        m=re.match(r'(-?[A-Za-z_][\w-]*|--[\w-]+)\s*:(.*)$',raw,re.S)
        if m and stack:
            val=m[2].strip(); nodes[stack[-1]]['decl'].append({'name':m[1],'value':decode(val),'start':a+leading,'end':b})
    while i<n:
        c=s[i]
        if quote:
            if c=='\\': i+=2; continue
            if c==quote: quote=None
            i+=1; continue
        if s.startswith('/*',i):
            end=s.find('*/',i+2); i=n if end<0 else end+2; continue
        if c in "\"'": quote=c; i+=1; continue
        if c=='\\': i+=2; continue
        if c=='(': par+=1
        elif c==')': par=max(0,par-1)
        elif c=='[': bra+=1
        elif c==']': bra=max(0,bra-1)
        elif par==0 and bra==0:
            if c=='{':
                raw=s[seg:i]; start=seg+len(raw)-len(raw.lstrip()); pre=re.sub(r'/\*.*?\*/','',raw,flags=re.S).strip()
                node={'prelude':decode(pre),'start':start,'body_start':i+1,'end':None,'parent':stack[-1] if stack else None,'decl':[]}
                nodes.append(node); stack.append(len(nodes)-1); seg=i+1
            elif c==';': decl(seg,i); seg=i+1
            elif c=='}':
                decl(seg,i)
                if stack: nodes[stack.pop()]['end']=i+1
                seg=i+1
        i+=1
    return nodes, {'unclosed_blocks':len(stack),'unclosed_quote':quote,'unclosed_parens':par,'unclosed_brackets':bra}

def contexts(nodes,i):
    out=[]; p=nodes[i]['parent']
    while p is not None:
        out.append(nodes[p]['prelude']); p=nodes[p]['parent']
    return list(reversed(out))

def classify_context(sel, ctx):
    joined=' '.join([*ctx,sel])
    if 'prefers-color-scheme:dark' in joined: return 'system_dark_condition'
    if re.search(r'data-mode[=\\"\s]*dark',joined): return 'explicit_dark_condition'
    if re.search(r'data-mode[=\\"\s]*light',joined): return 'explicit_light_or_default_condition'
    if re.search(r'data-density|data-font|data-size|data-platform',joined): return 'variant_condition'
    if sel in (':root',':root,:host',':where(:root,:host)',':host'): return 'root_default'
    if sel in ('.cds-root',':where(.cds-root)'): return 'cds_default'
    return 'selector_scoped'

def extract_inventory(resources, asar_root=None):
    bases = source_bases(resources, asar_root)
    seen = {}
    files, blocks, statistics = [], [], []
    tokens = collections.defaultdict(list)
    references = collections.Counter()
    for scope, base in bases.items():
        for candidate in sorted(base.rglob('*.css')):
            logical = scope + '/' + candidate.relative_to(base).as_posix()
            path = source_path(logical, bases)
            data = path.read_bytes()
            # Reject undecodable input rather than claim UTF-8 byte provenance.
            data.decode('utf-8')
            sha = hashlib.sha256(data).hexdigest()
            source_id = f'f{len(files):03d}'
            source = {'id': source_id, 'path': logical, 'sha256': sha, 'bytes': len(data)}
            files.append(source)
            if sha in seen:
                source['duplicate_of'] = seen[sha]
                continue
            seen[sha] = source_id
            nodes, validation = scan(data)
            if any(validation.values()):
                raise ValueError(f'Unclosed CSS syntax in {logical}: {validation}')
            statistics.append({'source': source_id, 'blocks': len(nodes),
                               'declarations': sum(len(node['decl']) for node in nodes),
                               'parser_validation': validation})
            for index, node in enumerate(nodes):
                declarations = node['decl']
                if not declarations:
                    continue
                custom = [declaration for declaration in declarations if declaration['name'].startswith('--')]
                for declaration in declarations:
                    references.update(re.findall(r'var\(\s*(--[\w-]+)', declaration['value']))
                # Keep the original block numbering for reproducibility. A font-face
                # block contributes only its selector/bounds; no font is opened.
                if not custom and node['prelude'] != '@font-face':
                    continue
                block_id = f'b{len(blocks):05d}'
                context = contexts(nodes, index)
                blocks.append({'id': block_id, 'source': source_id, 'selector': node['prelude'],
                               'context': context, 'byte_start': node['start'], 'byte_end': node['end'],
                               'activation': classify_context(node['prelude'], context)})
                for declaration in custom:
                    tokens[declaration['name']].append({'value': declaration['value'], 'block': block_id,
                                                        'byte_start': declaration['start'], 'byte_end': declaration['end']})
    if not files:
        raise ValueError('No CSS files found in the supplied source directories')
    return {
        'schema': 'claude.static-design-tokens.v1',
        'scope': 'Private, static CSS inventory from explicitly supplied directories. Duplicate hashes analyzed once. No application code executed.',
        'limitations': ['Original analytical taxonomy; not a CSS cascade simulator.',
                       'Static declarations do not establish runtime activation, visibility or computed style.',
                       'This intermediate can contain non-color declaration values. Do not publish it or raw source files.'],
        'sources': files, 'statistics': statistics, 'blocks': blocks,
        'tokens': {name: {'taxonomy': family(name, definitions[0]['value']),
                          'reference_count': references[name], 'definitions': definitions}
                   for name, definitions in sorted(tokens.items())},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, required=True, help='Resources directory containing ion-dist/')
    parser.add_argument('--asar-root', type=Path, help='Already-extracted app.asar directory; optional if absent')
    parser.add_argument('--output', type=Path, required=True, help='Private inventory JSON destination')
    args = parser.parse_args(argv)
    try:
        if args.output.suffix.lower() != '.json':
            raise ValueError('--output must name a .json inventory file')
        inventory = extract_inventory(args.resources, args.asar_root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(inventory, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    except (OSError, ValueError) as error:
        parser.exit(2, f'error: {error}\n')
    print(json.dumps({'sources': len(inventory['sources']),
                      'unique_css_sources': len(inventory['statistics']),
                      'unique_tokens': len(inventory['tokens']),
                      'custom_property_declarations': sum(len(token['definitions']) for token in inventory['tokens'].values()),
                      'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
