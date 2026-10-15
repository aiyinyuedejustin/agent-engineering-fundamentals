#!/usr/bin/env python3
"""Build original, source-anchored color facts and a standalone color browser.
No source stylesheet, application script or font is copied into the deliverable.
Profiles are explicit declaration selections, not a browser cascade simulator.
"""
from __future__ import annotations
import argparse, colorsys, hashlib, json, math, re
from pathlib import Path
from inventory_inputs import source_bases, source_path, validate_inventory
from resolution_overlay import write_new_outputs

FAMILIES = ['gray','red','orange','yellow','green','aqua','blue','violet','magenta']
SHADES = [0,10,20,30,40,50,60,70,80,90,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,810,820,830,840,850,860,870,880,890,900]
COLOR_CATEGORIES = {'raw_palette','semantic_color','legacy_color','legacy_v2_palette_bridge','mode_relative_neutral_palette','role_palette_alias','data_visualization','collaboration_color'}
EXTRA_COLORS = ['--cds-button-on-content','--cds-button-on-content-hover','--cds-button-on-content-ring','--cds-editor-code-ink','--cds-radio-group-card-selected','--cds-segmented-control-thumb','--cds-segmented-control-track','--cds-shimmer-text-peak','--cds-shortcut-cap-fill','--cds-shortcut-cap-ink','--cds-shortcut-cap-line','--cds-skeleton-base','--cds-skeleton-sheen','--cds-slider-fill','--cds-slider-handle','--cds-slider-stop-dot','--cds-slider-track','--cds-tooltip-bg','--cds-tooltip-fg','--cds-fill-field-ring','--cds-fill-secondary-pressed-ring','--cds-fill-secondary-ring','--cds-ring-color','--cds-shadow-color','--cds-slider-handle-shadow-depth','--cds-slider-handle-shadow-outer']
ROOTS = {':root',':root,:host',':where(:root,:host)'}
DARK = '[data-mode=dark] .cds-root:not([data-mode=light]):not([data-mode=system]),.cds-root[data-mode=dark]'
GIT_BASE = ':where(:root,:host,.cds-root[data-mode],[data-mode] .cds-root:not([data-mode]))'
GIT_DARK = ':where([data-mode=dark] .cds-root:not([data-mode=light]):not([data-mode=system]),.cds-root[data-mode=dark],.cds-dark-scope[data-mode=dark])'
NUMBER = r'(?:\d+(?:\.\d*)?|\.\d+)'

class Unresolved(ValueError): pass

def expanded(name, env, trail=()):
    if name in trail: raise Unresolved('cyclic_reference: ' + ' → '.join((*trail,name)))
    if name not in env: raise Unresolved('missing_in_profile: ' + name)
    value=env[name]['value']
    # Only exact simple var() calls are substituted. Fallbacks are preserved.
    def sub(m): return expanded(m[1],env,(*trail,name))
    value=re.sub(r'var\((--[\w-]+)\)',sub,value)
    if 'var(' in value: raise Unresolved('unsupported_variable_expression: '+value)
    return value

def parse_color(value):
    """Conservative exact-pattern parser. Unsupported functions never get a HEX."""
    v=value.strip()
    if v=='transparent': return (0.,0.,0.,0.),'transparent_keyword'
    if re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F])?|#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?',v):
        z=v[1:]
        if len(z) in (3,4):z=''.join(c*2 for c in z)
        if len(z)==6:z+='ff'
        return tuple(int(z[i:i+2],16)/255 for i in (0,2,4,6)),'hex_literal'
    m=re.fullmatch(fr'({NUMBER}) ({NUMBER})% ({NUMBER})%',v)
    if m:
        h,s,l=map(float,m.groups())
        if not (0<=s<=100 and 0<=l<=100):raise Unresolved('out_of_range_hsl')
        return (*colorsys.hls_to_rgb((h%360)/360,l/100,s/100),1.),'hsl_components_to_srgb'
    m=re.fullmatch(fr'hsl\(from (.+) h s l / ({NUMBER})(%)?\)',v)
    if m:
        base,_=parse_color(m[1]);a=float(m[2])/(100 if m[3] else 1)
        if not 0<=a<=1:raise Unresolved('out_of_range_alpha')
        return (*base[:3],a),'relative_hsl_unchanged_channels_alpha_override'
    m=re.fullmatch(fr'color-mix\(in srgb, (.+) ({NUMBER})%, transparent\)',v)
    if m:
        base,_=parse_color(m[1]);weight=float(m[2])/100
        if not 0<=weight<=1:raise Unresolved('out_of_range_mix_weight')
        return (*base[:3],base[3]*weight),'srgb_mix_with_transparent_premultiplied_alpha'
    m=re.fullmatch(fr'rgba?\(({NUMBER})[ ,]+({NUMBER})[ ,]+({NUMBER})(?:\s*[/,]\s*({NUMBER})(%)?)?\)',v)
    if m:
        rgb=[float(m[i])/255 for i in (1,2,3)];a=float(m[4])/(100 if m[5] else 1) if m[4] else 1.
        if not all(0<=n<=1 for n in [*rgb,a]):raise Unresolved('out_of_range_rgb')
        return (*rgb,a),'rgb_literal'
    if 'currentColor' in v:raise Unresolved('requires_element_currentColor')
    if v in ('initial','inherit','unset','revert','revert-layer'):raise Unresolved('requires_css_cascade_keyword')
    if v.startswith('rgb(from '):raise Unresolved('relative_rgb_calc_not_evaluated')
    raise Unresolved('unsupported_color_expression')

def color_fields(value):
    rgba,method=parse_color(value)
    channels=[math.floor(max(0,min(1,c))*255+.5) for c in rgba[:3]]
    return {'status':'resolved','hex':'#'+''.join(f'{c:02x}' for c in channels),'alpha':rgba[3],'srgb_channels':list(rgba[:3]),'conversion':method}

def choose_primary_source(d, requested=None):
    """Choose an explicit ID/path, or the sole ion source with the complete palette."""
    if requested:
        matches = [f for f in d['sources'] if requested in (f['id'], f['path'])]
        if len(matches) != 1:
            raise ValueError('--primary-source must match exactly one inventory source ID or path')
        return matches[0]
    blocks = {b['id']: b for b in d['blocks']}
    required = {f'--cds-{family}-{shade}' for family in FAMILIES for shade in SHADES}
    found = {}
    for name in required & d['tokens'].keys():
        for definition in d['tokens'][name]['definitions']:
            block = blocks[definition['block']]
            if block['selector'] in ROOTS and block['context'] in ([], ['@layer base'], ['@layer theme']):
                found.setdefault(block['source'], set()).add(name)
    candidates = [f for f in d['sources'] if f['path'].startswith('ion/') and found.get(f['id']) == required]
    if len(candidates) != 1:
        raise ValueError('Cannot choose a unique complete ion palette; supply --primary-source with an inventory source ID or path')
    return candidates[0]


def build_catalog(inventory, resources, asar_root, *, primary_source=None,
                  product='Claude Desktop', version='unspecified'):
    """Read and verify local inputs; return derived color facts without writing files."""
    path = Path(inventory)
    d = json.loads(path.read_text(encoding='utf-8'))
    validate_inventory(d)
    bs = {b['id']: b for b in d['blocks']}
    fs = {f['id']: f for f in d['sources']}
    source = choose_primary_source(d, primary_source)
    sid = source['id']
    bases = source_bases(resources, asar_root)
    selected_names = {n for n,t in d['tokens'].items() if t['taxonomy'] in COLOR_CATEGORIES and n != '--text-body'} | (set(EXTRA_COLORS) & d['tokens'].keys())
    data_by_source = {}
    hash_checks = []
    used_sources = {bs[x['block']]['source'] for n in selected_names for x in d['tokens'][n]['definitions']}

    def read_source(fid):
        if fid not in data_by_source:
            f = fs[fid]
            raw = source_path(f['path'], bases).read_bytes()
            sha = hashlib.sha256(raw).hexdigest()
            if sha != f['sha256']:
                raise ValueError(f'Source hash mismatch: {fid} ({f["path"]})')
            data_by_source[fid] = raw
            hash_checks.append({'source': fid, 'sha256': sha, 'verified': True})
        return data_by_source[fid]

    for fid in sorted(used_sources):
        read_source(fid)

    def check_declaration(name, definition):
        block = bs[definition['block']]
        raw = read_source(block['source'])
        start, end = definition['byte_start'], definition['byte_end']
        if not 0 <= block['byte_start'] <= start < end <= block['byte_end'] <= len(raw):
            raise ValueError(f'Invalid declaration byte bounds: {name}')
        actual = re.sub(r'\s*:\s*', ':', raw[start:end].decode('utf-8').strip(), count=1)
        if actual != f"{name}:{definition['value']}":
            raise ValueError(f'Declaration byte anchor mismatch: {name}')

    definition_inventory = {}
    anchor_count = 0
    for n in sorted(selected_names):
        token = d['tokens'][n]
        entries = []
        for definition in token['definitions']:
            check_declaration(n, definition)
            block = bs[definition['block']]
            entries.append({'value': definition['value'], 'source': block['source'], 'block': definition['block'], 'byte_start': definition['byte_start'], 'byte_end': definition['byte_end']})
            anchor_count += 1
        definition_inventory[n] = {'category': token['taxonomy'] if n not in EXTRA_COLORS else 'component_color', 'reference_count': token['reference_count'], 'definitions': entries}
    # Explicit selections are staged; their sequence is documented below.
    def select(predicate):
        env={}
        for n,t in d['tokens'].items():
            hits=[x for x in t['definitions'] if bs[x['block']]['source']==sid and predicate(bs[x['block']])]
            if hits:env[n]=max(hits,key=lambda x:x['byte_start'])
        return env
    roots=select(lambda b:b['selector'] in ROOTS and b['context'] in ([],['@layer base'],['@layer theme']))
    cds_component=select(lambda b:b['selector']=='.cds-root' and b['context']==['@layer components'])
    cds_default=select(lambda b:b['selector'] in ('.cds-root',GIT_BASE) and not b['context'])
    cds_dark=select(lambda b:b['selector'] in (DARK,GIT_DARK,'[data-mode=dark]') and b['context']==['@media screen'])
    cds_dark_component=select(lambda b:b['selector']==DARK+',.cds-dark-scope[data-mode=dark]' and b['context']==['@layer components','@media screen'])
    profiles={
      'cds_light':{'label':'CDS · 显式浅色','kind':'semantic','mode':'light','description':'CDS 基础色 + .cds-root 默认语义值；按显式浅色阅读。','selection':['root declarations (unconditional or base/theme layer)','component layer .cds-root','unlayered .cds-root and mode-aware Git base'],'env':roots|cds_component|cds_default},
      'cds_dark':{'label':'CDS · 显式深色','kind':'semantic','mode':'dark','description':'CDS 基础值叠加 screen 下 data-mode=dark 的显式覆盖。','selection':['cds_light stages','component layer explicit-dark override','screen explicit-dark CDS/Git/root override'],'env':roots|cds_component|cds_default|cds_dark_component|cds_dark}}
    for legacy_version in ('v1','v2'):
        for mode in ('light','dark'):
            base_sel='[data-theme=claude],[data-theme=claude][data-mode=light]' if mode=='light' else '[data-theme=claude][data-mode=dark]'
            legacy_base=select(lambda b:b['selector']==base_sel and b['context']==['@layer base'])
            env=roots|legacy_base
            stages=['root declarations','legacy v1 '+mode+' @layer base']
            if legacy_version=='v2':
                sel='[data-color-version=v2][data-theme=claude],[data-color-version=v2][data-theme=claude][data-mode=light]' if mode=='light' else '[data-color-version=v2][data-theme=claude][data-mode=dark]'
                env|=select(lambda b:b['selector']==sel and not b['context']);stages.append('unlayered legacy v2 '+mode+' bridge override')
            key=f'legacy_{legacy_version}_{mode}'
            profiles[key]={'label':f'Legacy {legacy_version} · '+('浅色' if mode=='light' else '深色'),'kind':'legacy','mode':mode,'description':('旧版 HSL 分量主题。' if legacy_version=='v1' else '旧命名经 --_ / --cds-hsl 桥接到新版色值；保留未覆盖的 v1 项。'),'selection':stages,'env':env}
    profiles['bridge']={'label':'Legacy v2 · HSL 桥接','kind':'bridge','mode':'none','description':'--cds-hsl-* 分量和 --_* 别名。','selection':['unconditional root declarations'],'env':roots}
    records=[]
    def record(n,env,profile,kind):
        x=env[n];b=bs[x['block']];cat=definition_inventory[n]['category'];out={'id':profile+':'+n,'name':n,'profile':profile,'kind':kind,'category':cat,'declared':x['value'],'source':b['source'],'block':x['block'],'byte_start':x['byte_start'],'byte_end':x['byte_end']}
        try:
            v=expanded(n,env);out['resolved_expression']=v;out.update(color_fields(v))
        except Unresolved as e:out.update(status='unresolved',reason=str(e))
        deps=[];seen=set()
        def visit(name):
            if name in seen or name not in env:return
            seen.add(name);z=env[name];check_declaration(name,z);deps.append({'name':name,'value':z['value'],'block':z['block'],'byte_start':z['byte_start'],'byte_end':z['byte_end']})
            for dep in re.findall(r'var\((--[\w-]+)',z['value']):visit(dep)
        visit(n);out['resolution_chain']=deps
        return out
    for family in FAMILIES:
        for shade in SHADES:
            n=f'--cds-{family}-{shade}'
            if n not in roots:
                raise ValueError(f'Primary source is missing required root palette token: {n}')
            vals={x['value'] for x in d['tokens'][n]['definitions']}
            if len(vals)!=1:
                raise ValueError(f'Raw palette values disagree across sources: {n}')
            r=record(n,roots,'raw','raw');r.update(family=family,shade=shade);records.append(r)
    for key,p in profiles.items():
        env=p['env']
        if p['kind']=='semantic':names=[n for n in selected_names if n in env and definition_inventory[n]['category'] not in ('raw_palette','legacy_color','legacy_v2_palette_bridge')]
        elif p['kind']=='legacy':names=[n for n in selected_names if n in env and definition_inventory[n]['category']=='legacy_color']
        else:names=[n for n in selected_names if n in env and definition_inventory[n]['category']=='legacy_v2_palette_bridge']
        for n in sorted(names):records.append(record(n,env,key,p['kind']))
        p['record_count']=len(names);p['resolved_count']=sum(r['status']=='resolved' for r in records if r['profile']==key);del p['env']
    profiles={'raw':{'label':'CDS · 全量原始色阶','kind':'raw','mode':'none','description':'9 个色族，每族 35 个档位；数字是色阶编号，不是语义优先级。','record_count':315,'resolved_count':sum(r['status']=='resolved' for r in records if r['profile']=='raw'),'selection':['selected root declarations; raw values agree across all inventoried definitions']},**profiles}
    used_blocks={x['block'] for t in definition_inventory.values() for x in t['definitions']}
    out={'schema':'claude.complete-color-catalog.v1','product':product,'version':version,'evidence_status':'packaged_static','primary_source':sid,'scope':{'raw_palette':'all 315 CDS raw palette names: 9 families × 35 shades','semantic_profiles':'CDS explicit light/dark; legacy v1 and v2 light/dark; HSL bridge','declaration_inventory':'All definitions for color-taxonomy names, except --text-body (font-size), plus explicitly identified component color names present in the input. Other utility tokens, shadows, dimensions, third-party themes and inline colors are not claimed exhaustive.','profile_meaning':'Named declaration selections from one packaged source. No cross-file merge, DOM activation, full cascade simulation, system-mode selection or feature-query activation is asserted.','alpha':'Uncomposited channel alpha. HEX is rounded 8-bit sRGB display; exact original declaration and floating sRGB channels are retained. HSL component triples represent colors only when consumed as hsl(...).'},'families':FAMILIES,'shades':SHADES,'profiles':profiles,'records':records,'definition_inventory':definition_inventory,'sources':[fs[fid] for fid in sorted(used_sources)],'blocks':[bs[bid] for bid in sorted(used_blocks)],'verification':{'taxonomy_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_hash_checks':hash_checks,'byte_anchors_checked':anchor_count,'raw_values_agree_across_sources':True,'excluded_non_color_names':['--text-body'],'parser_support':['3/4/6/8-digit HEX','transparent','HSL component triples','relative hsl with unchanged channels and numeric alpha','srgb color-mix of one supported color with transparent','numeric rgb/rgba literals'],'unsupported_handling':'No HEX, alpha or swatch is assigned. Preserve declared and expanded expressions plus reason.'}}
    out['statistics']={'raw_palette_entries':315,'families':9,'shades_per_family':35,'profile_records':len(records),'resolved_records':sum(r['status']=='resolved' for r in records),'unresolved_records':sum(r['status']=='unresolved' for r in records),'color_names_in_inventory':len(definition_inventory),'declarations_in_inventory':anchor_count,'profiles':{k:{'total':p['record_count'],'resolved':p['resolved_count'],'unresolved':p['record_count']-p['resolved_count']} for k,p in profiles.items()}}
    return out


def browser_payload(catalog):
    """Keep only the facts needed by the original offline viewer."""
    blocks = {b['id']: b for b in catalog['blocks']}
    sources = {f['id']: f for f in catalog['sources']}
    omitted = {'resolution_chain', 'srgb_channels', 'byte_start', 'byte_end', 'source', 'block'}
    records = [{k: v for k, v in r.items() if k not in omitted} | {
        'selector': blocks[r['block']]['selector'],
        'conditions': blocks[r['block']]['context'],
        'source_label': sources[r['source']]['path'],
    } for r in catalog['records']]
    payload = {key: catalog[key] for key in ('product', 'version', 'families', 'profiles', 'statistics')} | {'records': records}
    if 'resolution_extension' in catalog:
        payload['resolution_extension'] = catalog['resolution_extension']
    return payload


def render_html(catalog, template):
    if template.count('__COLOR_DATA__') != 1:
        raise ValueError('Template must contain exactly one __COLOR_DATA__ placeholder')
    payload = json.dumps(browser_payload(catalog), ensure_ascii=False, separators=(',', ':'))
    # Prevent user-supplied metadata/declarations from closing the JSON script element.
    payload = payload.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    return template.replace('__COLOR_DATA__', payload)


def write_outputs(catalog, output, template):
    html = render_html(catalog, Path(template).read_text(encoding='utf-8'))
    write_new_outputs(output, {
        'color-catalog.json': json.dumps(catalog, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
        'index.html': html,
    })


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory', type=Path, required=True, help='JSON inventory produced by extract_design_tokens.py')
    ap.add_argument('--resources', type=Path, required=True, help='Resources directory containing ion-dist/')
    ap.add_argument('--asar-root', type=Path, help='Already-extracted app.asar directory; required when the inventory uses asar sources')
    ap.add_argument('--output', type=Path, required=True, help='New, non-existing destination directory for color-catalog.json and index.html')
    ap.add_argument('--template', type=Path, default=Path(__file__).with_name('color_catalog_template.html'))
    ap.add_argument('--resolution-overlay', type=Path, help='Reviewed additive resolution overlay for this exact baseline')
    ap.add_argument('--primary-source', help='Exact inventory source ID or path; default: the sole complete ion palette')
    ap.add_argument('--product', default='Claude Desktop', help='Metadata label only; not inferred or verified')
    ap.add_argument('--version', default='unspecified', help='Package version label only; not inferred or verified')
    ap.add_argument('--expect-records', type=int, help='Fail before writing if record count differs (1341 for the documented baseline)')
    args = ap.parse_args(argv)
    try:
        catalog = build_catalog(args.inventory, args.resources, args.asar_root,
                                primary_source=args.primary_source, product=args.product, version=args.version)
        if args.expect_records is not None and len(catalog['records']) != args.expect_records:
            raise ValueError(f"Expected {args.expect_records} records, got {len(catalog['records'])}; review the source/profile recipe")
        outputs = [args.output / name for name in ('color-catalog.json', 'index.html')]
        protected = [args.inventory, args.template] + ([args.resolution_overlay] if args.resolution_overlay else [])
        if any(target.resolve() == original.resolve() for target in outputs for original in protected):
            raise ValueError('Output files must not overwrite the inventory or template')
        if args.resolution_overlay:
            from resolution_overlay import apply_resolution_overlay, load_resolution_overlay
            catalog = apply_resolution_overlay(catalog, load_resolution_overlay(args.resolution_overlay))
        write_outputs(catalog, args.output, args.template)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        ap.exit(2, f'error: {error}\n')
    print(json.dumps(catalog['statistics'], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
