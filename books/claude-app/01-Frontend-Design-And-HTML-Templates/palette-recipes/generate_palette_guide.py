#!/usr/bin/env python3
"""Build an original, source-synchronized Chinese palette reference (stdlib only)."""
from __future__ import annotations
import argparse
import colorsys
import hashlib
import html
import json
import os
from fractions import Fraction
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
ROLES = {
    'canvas': ('页面背景', '整页画布'), 'sidebar': ('导航背景', '侧栏与次级底面'),
    'surface': ('卡片表面', '卡片、菜单、浮层'), 'ink': ('正文文字', '标题与主要内容'),
    'muted': ('辅助文字', '说明、时间、元信息'), 'line': ('轻分隔线', '装饰性分隔'),
    'line-strong': ('控件边界', '需要辨认的输入框与控件边界'),
    'accent': ('强调色', '链接、选中标记、焦点环'), 'accent-soft': ('强调底色', '轻提示与选择底面'),
}
COMMON = {
    'action': '主要动作底色', 'on-action': '主要动作文字', 'danger': '错误文字／图标',
    'danger-soft': '错误底色', 'success': '成功文字／图标', 'success-soft': '成功底色', 'scrim': '遮罩',
}
DESCRIPTIONS = {
    'paper': '温暖纸面与陶土点缀，适合写作、笔记和知识工作台。',
    'sage': '低饱和绿与柔和纸白，适合阅读、生活工具和慢节奏仪表盘。',
    'ocean': '清冷灰蓝与清晰层级，适合研究、数据工具和专业文档。',
    'plum': '带紫调的灰与温和粉白，适合作品集、编辑工具和创意空间。',
    'graphite': '克制灰阶与蓝灰点缀，适合代码、设置页和通用工作台。',
}


def decimal(value, places=6):
    return f'{float(value):.{places}f}'.rstrip('0').rstrip('.') or '0'


def fraction(value):
    f = Fraction(value)
    return str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}'


def color(value):
    if not re.fullmatch(r'#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', value):
        raise ValueError(f'Unsupported source color: {value}')
    r, g, b = (int(value[i:i+2], 16) for i in (1, 3, 5))
    a8 = int(value[7:9], 16) if len(value) == 9 else 255
    channels = [Fraction(v, 255) for v in (r, g, b)]
    low, high = min(channels), max(channels)
    delta = high - low
    lightness = (high + low) / 2
    if delta == 0:
        hue = saturation = Fraction(0)
    else:
        saturation = delta / (1 - abs(2 * lightness - 1))
        if high == channels[0]:
            hue = ((channels[1] - channels[2]) / delta) % 6
        elif high == channels[1]:
            hue = (channels[2] - channels[0]) / delta + 2
        else:
            hue = (channels[0] - channels[1]) / delta + 4
        hue *= 60
    alpha = Fraction(a8, 255)
    hsl = [hue, saturation * 100, lightness * 100]
    alpha_css = '' if a8 == 255 else f' / calc({a8} / 255)'
    hsl_exact = [fraction(v) for v in hsl]
    def calc(v, unit=''):
        return f'{v.numerator}{unit}' if v.denominator == 1 else f'calc({v.numerator}{unit} / {v.denominator})'
    return {
        'hex': value.lower(), 'rgb': [r, g, b], 'alphaByte': a8,
        'alphaExact': fraction(alpha), 'alphaDecimal': decimal(alpha),
        'rgbCss': f'rgb({r} {g} {b}{alpha_css})',
        'hslCss': f'hsl({decimal(hue)} {decimal(saturation*100)}% {decimal(lightness*100)}%{alpha_css})',
        'hslExact': {'h': hsl_exact[0], 'sPercent': hsl_exact[1], 'lPercent': hsl_exact[2]},
        'hslExactCss': f'hsl({calc(hue)} {calc(saturation*100, "%")} {calc(lightness*100, "%")}{alpha_css})',
    }


def luminance(rgb):
    ch = [v / 255 for v in rgb]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in ch]
    return sum(v*w for v, w in zip(linear, (.2126, .7152, .0722)))


def contrast(fg, bg):
    foreground, background = color(fg), color(bg)
    if background['alphaByte'] != 255:
        raise ValueError('Contrast requires an opaque background')
    a = foreground['alphaByte'] / 255
    composite = [v*a + w*(1-a) for v,w in zip(foreground['rgb'], background['rgb'])]
    x,y = sorted((luminance(composite), luminance(background['rgb'])))
    return (y + .05) / (x + .05)


def parse_css(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return [(selector.strip(), dict(re.findall(r'--ui-([a-z0-9-]+)\s*:\s*([^;{}]+);', body)))
            for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text)]


def load_sources(source):
    paths = {k: source / f for k,f in {'css': 'claude-tokens.css', 'json': 'design-tokens.json', 'base': 'claude-reset-and-base.css'}.items()}
    text = paths['css'].read_text()
    data = json.loads(paths['json'].read_text())
    blocks = parse_css(text)
    assert set(data['palettes']) == set(DESCRIPTIONS), 'Unexpected palette set'
    palette_css = {}
    for selector, vals in blocks:
        match = re.search(r'data-palette="([a-z]+)"\]\[data-theme="(light|dark)"', selector)
        if match:
            palette_css[match.groups()] = vals
    assert len(palette_css) == 10
    common = {}
    for pid,p in data['palettes'].items():
        for mode in ('light','dark'):
            source_values = palette_css[(pid, mode)]
            assert set(p[mode]) == set(ROLES)
            for role,value in p[mode].items():
                assert value == source_values[role], f'JSON/CSS drift: {pid}.{mode}.{role}'
                color(value)
            values = {role: source_values[role] for role in COMMON}
            if mode in common:
                assert values == common[mode], f'Unexpected per-palette action override: {pid}/{mode}'
            common[mode] = values
    shared = next(vals for _,vals in blocks if 'font' in vals)
    shadows = {'light': shared['shadow'], 'dark': next(vals['shadow'] for selector,vals in blocks if 'shadow' in vals and 'data-theme="dark"' in selector)}
    profiles = {name: next(vals for selector,vals in blocks if f'data-density="{name}"' in selector) for name in ('compact','comfortable')}
    large = next(vals['reading-size'] for selector,vals in blocks if 'data-reading="large"' in selector)
    for i,v in enumerate(data['spacing'],1):
        assert shared[f'space-{i}'] == f'{v}px'
    for k,csskey in {'control':'radius','card':'card-radius','composer':'composer-radius'}.items():
        assert shared[csskey] == f'{data["radius"][k]}px'
    for mode,v in profiles.items():
        assert v['control'] == data['profiles'][mode]['controlMinHeight']
        assert v['text'] == data['profiles'][mode]['uiFontSize']
    assert large == data['profiles']['reading']['large']
    assert shared['reading-size'] == data['profiles']['reading']['default']
    assert float(shared['leading']) == data['profiles']['reading']['lineHeight']
    base = paths['base'].read_text()
    focus = re.search(r':where\(:focus-visible\)\s*\{([^}]+)\}',base).group(1).strip()
    assert focus == 'outline: 2px solid var(--ui-accent); outline-offset: 4px;'
    base_leading = re.search(r'font: var\(--ui-text\)/(\S+) var\(--ui-font\)',base).group(1)
    return {'paths': paths, 'data': data, 'shared': shared, 'profiles': profiles, 'large': large, 'common': common, 'shadows': shadows, 'focus': focus, 'baseLeading': base_leading}


def build_contrasts(source):
    result = []
    for pid,p in source['data']['palettes'].items():
        for mode in ('light','dark'):
            v = p[mode] | source['common'][mode]
            tests = [(a,b,4.5) for a in ('ink','muted','accent') for b in ('canvas','sidebar','surface')]
            tests += [('line-strong',b,3) for b in ('canvas','sidebar','surface')]
            tests += [('accent',b,3) for b in ('canvas','sidebar','surface')]
            tests += [('accent','accent-soft',4.5), ('on-action','action',4.5), ('danger','danger-soft',4.5), ('success','success-soft',4.5)]
            checks = [{'foreground':a, 'background':b,'threshold':threshold,'ratio':contrast(v[a],v[b]),'passed':contrast(v[a],v[b]) >= threshold} for a,b,threshold in tests]
            decorative = {b:contrast(v['line'],v[b]) for b in ('canvas','sidebar','surface')}
            result.append({'palette':pid,'mode':mode,'checks':checks,'decorativeLineRatios':decorative})
    return result


def esc(x): return html.escape(str(x), quote=True)


def text(x,y,value,size=16,fill='#26251f',weight=400,family=None):
    font = f' style="font-family:{esc(family)}"' if family else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}"{font}>{esc(value)}</text>'


def rect(x,y,w,h,fill,rx=0,stroke=None,sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'


def svg_start(w,h,title,description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(title)}</title><desc id="desc">{esc(description)}</desc>',
            '<style>text{font-family:"Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif} .mono{font-family:Consolas,monospace}</style>']


def palette_svg(pid, p, source):
    out = svg_start(1380,1320,f'{p["name"]} 浅深配色色卡',f'原创配色 {pid}，包含浅色和深色的九个实际语义令牌与 HEX、RGB、HSL、Alpha。')
    out += [rect(0,0,1380,1320,'#f0eee7'),text(40,50,p['name'],30,weight=700),text(40,82,f'{pid} · 原创复用配方 · '+DESCRIPTIONS[pid],16),text(40,111,'HEX/RGB 为源值；HSL 显示到小数后 6 位；本图九个角色的 Alpha 均为 1。',14,fill='#656258')]
    for i,mode in enumerate(('light','dark')):
        v = p[mode] | source['common'][mode]
        x = 40 + i*670
        out += [rect(x,138,630,1140,v['canvas'],20,stroke=v['line']),text(x+24,178,'浅色 Light' if mode=='light' else '深色 Dark',22,v['ink'],700),rect(x+24,200,582,202,v['surface'],14,stroke=v['line'])]
        out += [text(x+44,238,'界面应让内容先被看见',22,v['ink'],600),text(x+44,268,'正文、说明、边界和强调色各有自己的职责。',15,v['muted'])]
        out += [rect(x+44,291,332,40,v['surface'],8,stroke=v['line-strong']),text(x+56,317,'可辨认的输入框边界',14,v['muted'])]
        out += [rect(x+39,348,144,44,'none',12,stroke=v['accent'],sw=2),rect(x+44,353,134,34,v['action'],8),text(x+70,376,'继续阅读',14,v['on-action'],600)]
        out += [rect(x+205,353,160,34,v['accent-soft'],8),text(x+225,376,'强调色与柔和底色',13,v['accent'],500)]
        for j,(role,(label,_)) in enumerate(ROLES.items()):
            y = 428 + j*91
            c = color(v[role])
            out += [rect(x+24,y,76,64,v[role],10,stroke=v['line-strong']),text(x+116,y+14,f'{label}  --ui-{role}',15,v['ink'],600),text(x+116,y+36,f'{c["hex"].upper()}  |  {c["rgbCss"]}  |  A=1',13,v['muted']),text(x+116,y+57,c['hslCss'],13,v['muted'])]
    out += [text(40,1302,'颜色来源：同目录生成器读取共享 CSS，并逐值核对 design-tokens.json。五套配方均为原创，不标作 CDS 官方值。',12,fill='#656258'),'</svg>']
    return '\n'.join(out)+'\n'


def overview_svg(source):
    out = svg_start(1380,1230,'五套原创配方总览','每套含浅色和深色，以及页面背景、卡片、文字、边界、强调色五个可见色块。')
    out += [rect(0,0,1380,1230,'#f0eee7'),text(36,52,'五套原创配方，一套语义接口',30,weight=700),text(36,85,'背景 → 卡片 → 文字 → 边界 → 强调色。更换 data-palette，保留布局和组件。',17,fill='#656258')]
    for j,(pid,p) in enumerate(source['data']['palettes'].items()):
        y = 114+j*218
        for i,mode in enumerate(('light','dark')):
            x = 36 + 670*i
            v=p[mode]
            out += [rect(x,y,638,196,v['canvas'],18,stroke=v['line']),text(x+20,y+32,f'{p["name"]} · {pid} · '+('浅色' if mode=='light' else '深色'),19,v['ink'],600)]
            for k,role in enumerate(('canvas','surface','ink','line','accent')):
                xx=x+20+k*121
                out += [rect(xx,y+52,108,72,v[role],8,stroke=v['line-strong']),text(xx,y+147,ROLES[role][0],13,v['ink']),text(xx,y+170,v[role].upper(),13,v['muted'])]
    out += [text(36,1220,'原创模板值；浅深主题均已在共享 CSS 中实现。',12,fill='#656258'),'</svg>']
    return '\n'.join(out)+'\n'


def foundations_svg(source):
    d, s = source['data'],source['shared']
    out=svg_start(1380,950,'字、间距、圆角与焦点环','展示实际字体回退、字号、间距阶梯、圆角和焦点环。')
    out += [rect(0,0,1380,950,'#f8f7f3'),text(40,56,'字、间距、圆角与焦点环',30,weight=700),text(40,90,'以下尺寸来自模板共享变量与基础样式。',17,fill='#656258')]
    for i,(title,key,sample) in enumerate((('界面工具字','font','Clear controls · 清楚的控件'),('长文阅读字','reading','Ideas deserve room · 给文字留出呼吸'),('代码与数字','mono','const scale = [4, 8, 12, 16];'))):
        y=124+i*120
        out += [rect(40,y,1300,103,'#ffffff',14,stroke='#d9d6cc'),text(60,y+31,title,15,fill='#656258'),text(60,y+72,sample,28,family=s[key]),text(700,y+65,{'font':f'{s["text"]} / {source["baseLeading"]} · 紧凑 {source["profiles"]["compact"]["text"]}','reading':f'{s["reading-size"]} / {s["leading"]} · 大字 {source["large"]}','mono':' → '.join(v.strip().strip(chr(34)) for v in s["mono"].split(",")[:-1])}[key],18)]
    out += [text(40,535,'间距阶梯',22,weight=600)]
    for i,v in enumerate(d['spacing']):
        x=40+i*160
        out += [rect(x,562,128,90,'#ffffff',8,stroke='#d9d6cc'),rect(x+10,574,v,54,'#a24b33',3),text(x+10,643,f'{v}px  ·  space-{i+1}',13)]
    out += [text(40,706,'三个圆角',22,weight=600)]
    for i,(key,radius) in enumerate(d['radius'].items()):
        x=40+i*220
        out += [rect(x,738,184,100,'#ffffff',radius,stroke='#878273'),text(x+16,785,key,18,weight=600),text(x+16,815,f'{radius}px',16,fill='#656258')]
    out += [text(750,706,'可见的键盘焦点',22,weight=600),rect(750,743,194,54,'none',13,stroke='#a24b33',sw=2),rect(755,748,184,44,'#ffffff',8,stroke='#878273'),text(775,777,'Tab 聚焦',17),text(970,768,'2px accent 外轮廓',17),text(970,798,'与边界保持 4px 间隔',17)]
    out += [text(40,900,'字体只使用本机回退；未打包专有字体。图示字形受查看设备字体影响。',15,fill='#656258'),'</svg>']
    return '\n'.join(out)+'\n'


def color_table(values, labels):
    lines=['| 角色与变量 | HEX | RGB | HSL | Alpha |','|---|---|---|---|---|']
    for role,value in values.items():
        c=color(value)
        label=labels[role][0] if isinstance(labels[role],tuple) else labels[role]
        alpha=c['alphaExact'] if c['alphaByte']==255 else f'{c["alphaExact"]} ≈ {c["alphaDecimal"]}'
        lines.append(f'| {label}<br>`--ui-{role}` | `{c["hex"]}` | `{c["rgbCss"]}` | `{c["hslCss"]}` | {alpha} |')
    return '\n'.join(lines)


def write_readme(source, outdir, ratios):
    d,s=source['data'],source['shared']
    links={k:Path(os.path.relpath(p,outdir)).as_posix() for k,p in source['paths'].items()}
    lines=['# 五套原创网站配色与排版配方','',
    '直接复用已经在六个前端模板中实现的纸与陶、苔绿、雾蓝、梅灰、石墨。每套都包含浅色与深色：页面背景、卡片、文字、边界、强调色各自独立，切换主题不需要重写组件。','',
    '**本页是原创复用配方。** 色值与尺寸来自模板实际 CSS；CDS 静态观测属于另一组有版本与选择器边界的证据，不把二者混成“官方精确主题”。','',
    '![五套原创配方的浅深色块总览](swatches/overview.svg)','',
    '## 先复制这一段','',
    f'复制 [{links["css"].split("/")[-1]}]({links["css"]}) 与 [claude-reset-and-base.css]({links["base"]}) 到网站同一目录。按以下顺序引入；三个属性放在同一个容器上。','',
    '```html','<link rel="stylesheet" href="./claude-tokens.css">','<link rel="stylesheet" href="./claude-reset-and-base.css">','',
    '<main data-ui="atelier" data-palette="paper" data-theme="light">','  <article class="recipe-card">','    <h1>给内容留出空间</h1>','    <p class="recipe-note">清楚的正文、安静的底面、必要时才出现的强调色。</p>','    <a class="recipe-link" href="#next">继续阅读</a>','    <button class="recipe-button" type="button">保存</button>','    <p id="next">从这张卡片开始，再接入自己的内容和保存逻辑。</p>','  </article>','</main>','',
    '<style>','[data-ui="atelier"] .recipe-card {','  padding: var(--ui-space-5);','  color: var(--ui-ink);','  background: var(--ui-surface);','  border: 1px solid var(--ui-line);','  border-radius: var(--ui-card-radius);','  box-shadow: var(--ui-shadow);','}',
    '[data-ui="atelier"] .recipe-note { color: var(--ui-muted); }',
    '[data-ui="atelier"] .recipe-link { color: var(--ui-accent); }',
    '[data-ui="atelier"] .recipe-button {','  min-height: var(--ui-control);','  padding: var(--ui-space-2) var(--ui-space-4);','  border: 1px solid var(--ui-action);','  border-radius: var(--ui-radius);','  background: var(--ui-action);','  color: var(--ui-on-action);','}',
    '[data-ui="atelier"] input {','  border: 1px solid var(--ui-line-strong);','  background: var(--ui-surface);','}','</style>','```','',
    '将 `data-palette` 改为 `paper` / `sage` / `ocean` / `plum` / `graphite`；将 `data-theme` 改为 `dark` 即可使用对应深色。主按钮使用 `--ui-action`，不会随 `--ui-accent` 自动变成彩色。','',
    '## 颜色读法','',
    '- `canvas` 是页面背景，`sidebar` 是导航底面，`surface` 是卡片与浮层。','- `ink` / `muted` 分别承担正文与辅助文字；`accent` / `accent-soft` 成对使用。','- `line` 是安静的装饰性分隔；必须辨认的输入框、控件轮廓使用 `line-strong`。','- HEX 与 RGB 是源文件的精确 8 位 sRGB 值。HSL 显示到小数后 6 位，已验证转回相同 8 位 RGB；需要无舍入值时，使用 [tokens-expanded.json](tokens-expanded.json) 中的分数及 `hslExactCss`。','- 8 位 HEX 的末两位是 Alpha。例如 `#26251f40` 的 Alpha 为 `64/255`，不是精确的 `0.25`；`#00000080` 为 `128/255`，不是精确的 `0.5`。','']
    for pid,p in d['palettes'].items():
        lines += [f'## {p["name"]} `{pid}`','',DESCRIPTIONS[pid],'',f'![{p["name"]}浅深配色与颜色数值](swatches/{pid}.svg)','']
        for mode,label in [('light','浅色'),('dark','深色')]:
            lines += [f'### {label} `{mode}`','',color_table(p[mode],ROLES),'']
    lines += ['## 主动作与状态色','', '以下变量由 CSS 定义，并由五套配色共同使用；它们没有列在当前精简版 design-tokens.json 的 palettes 中。错误与成功除了用颜色，还应提供文字或图标。','']
    for mode,label in [('light','浅色'),('dark','深色')]:
        lines += [f'### {label}共用颜色','',color_table(source['common'][mode],COMMON),'']
    lines += ['### 阴影的透明度','', '| 模式 | `--ui-shadow` | 精确 Alpha |','|---|---|---|']
    for mode,label in [('light','浅色'),('dark','深色')]:
        shadow=source['shadows'][mode]
        alphas=[color(h)['alphaExact'] for h in re.findall(r'#[0-9a-fA-F]{8}',shadow)]
        lines.append(f'| {label} | `{shadow}` | '+ '；'.join(alphas)+' |')
    lines += ['', '阴影与遮罩颜色必须先与实际底色合成，再测量文字或边界对比度。不要拿带透明度的 HEX 直接当作不透明颜色。','',
    '## 字体与中文回退','', '![字体间距圆角与焦点环示意](swatches/foundations.svg)','',
    '以下是 CSS 实际字体栈。按字符覆盖和本机已安装字体回退，不下载字体。拉丁字与汉字可能由不同字体完成。','',
    '```css',f'--ui-font: {s["font"]};',f'--ui-reading: {s["reading"]};',f'--ui-mono: {s["mono"]};','```','',
    '| 用途 | 拉丁字回退 | 中文回退 |','|---|---|---|',
    '| 界面与控件 | -apple-system → BlinkMacSystemFont → Segoe UI | PingFang SC → Microsoft YaHei → sans-serif |',
    '| 长文阅读 | Georgia → Times New Roman | Songti SC → STSong → serif |',
    '| 代码与数字 | SFMono-Regular → Consolas → Liberation Mono → monospace | 原栈未指定中文等宽字体，由系统补字；中英字符宽度不保证统一 |','',
    '中文代码注释需要固定字宽时，可在自己的工程中把已安装的 `"Noto Sans Mono CJK SC"` 放到通用 `monospace` 之前；这是可选扩展，不是模板已启用的字体。不要把系统回退栈写成官方字体名称。','',
    '### 字号与密度','', '| 模式 | 界面字号 | 控件最小高度 | 阅读字号／行高 |','|---|---|---|',
    f'| 未设置 density | {s["text"]} | {s["control"]} | {s["reading-size"]} / {s["leading"]} |',
    f'| `data-density="compact"` | {source["profiles"]["compact"]["text"]} | {source["profiles"]["compact"]["control"]} | 不改变阅读字号 |',
    f'| `data-density="comfortable"` | {source["profiles"]["comfortable"]["text"]} | {source["profiles"]["comfortable"]["control"]} | 不改变阅读字号 |',
    f'| `data-reading="large"` | 不改变界面字号 | 不改变控件高度 | {source["large"]} / {s["leading"]} |','',
    f'基础界面行高是 `{source["baseLeading"]}`；阅读正文需要显式使用阅读变量。改变控件密度与放大阅读正文是两个独立开关。','',
    '```css','[data-ui="atelier"] .reading-body {','  font-family: var(--ui-reading);','  font-size: var(--ui-reading-size);','  line-height: var(--ui-leading);','}','[data-ui="atelier"] :is(code, pre) { font-family: var(--ui-mono); }','```','',
    '## 间距与圆角','', '| 变量 | 实际值 |','|---|---|']
    for i,v in enumerate(d['spacing'],1): lines.append(f'| `--ui-space-{i}` | {v}px |')
    lines += ['', '```css',f'--ui-radius: {s["radius"]};          /* 控件 */',f'--ui-card-radius: {s["card-radius"]};    /* 卡片 */',f'--ui-composer-radius: {s["composer-radius"]}; /* 输入面 */','```','',
    '可从 `space-2` 做控件内部的小间隔、`space-4` 做区块内间距、`space-5` 做卡片内边距、`space-6` 或 `space-7` 做章节间距。这是使用建议；变量本身不强制布局。','',
    '## 边界 焦点环与动态','',
    '基础样式已提供键盘焦点：2px 的强调色外轮廓，向外偏移 4px。不要用 `outline: none` 覆盖。容器的 `overflow` 也不能把焦点环裁掉。','',
    '```css',':where([data-ui="atelier"]) :where(:focus-visible) {','  outline: 2px solid var(--ui-accent);','  outline-offset: 4px;','}','```','',
    f'动画节奏是 `--ui-fast: {s["fast"]}` 与 `--ui-ease: {s["ease"]}`。系统设置减少动态效果时，时长归零，基础样式关闭动画、过渡与平滑滚动。','',
    '## 已计算的对比度','',
    '以下取 `canvas`、`sidebar`、`surface` 三个底面上的最低值。正常字号文字按 4.5:1 检查，必要的非文字边界按 3:1 检查；判定使用未四舍五入的值。规则见 [W3C 文字对比度](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) 与 [W3C 非文字对比度](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)。','',
    '| 配方／模式 | 正文 ink | 辅助 muted | 强调 accent | 强边界 line-strong |','|---|---:|---:|---:|---:|']
    for r in ratios:
        p=d['palettes'][r['palette']];v=p[r['mode']]
        nums=[min(contrast(v[k],v[b]) for b in ('canvas','sidebar','surface')) for k in ('ink','muted','accent','line-strong')]
        lines.append(f'| {p["name"]}／'+('浅' if r['mode']=='light' else '深')+' | '+' | '.join(f'{n:.2f}:1' for n in nums)+' |')
    total=sum(len(r['checks']) for r in ratios)
    passed=sum(c['passed'] for r in ratios for c in r['checks'])
    lines += ['',f'共 {total} 组阈值检查，{passed} 组通过，还包括主按钮文字、强调色配强调底色、错误与成功状态文字。详细未舍入数值见 [contrast-report.json](contrast-report.json)。',
    '', '**轻分隔线 `line` 没有达到控件辨认所需的 3:1。** 它用于装饰性分隔；必要边界用 `line-strong`。以上是令牌配对测试，页面仍须验收实际相邻颜色、文字大小、焦点可见性与裁剪。','',
    '## 从实际令牌重新生成','',
    f'源文件：[{links["css"].split("/")[-1]}]({links["css"]})、[design-tokens.json]({links["json"]})、[claude-reset-and-base.css]({links["base"]})。生成器逐个核对 CSS 与 JSON 中的 90 个配色值，并从 CSS 补充状态色、字体、透明度与焦点规则。','',
    '```bash','python generate_palette_guide.py','python -m unittest discover -p "test_*.py" -v','',
    '# 调整交付目录后，可明确指定共享文件目录：','python generate_palette_guide.py --source-dir ../styles','',
    '# 只确认生成物与源文件仍一致，不改文件：','python generate_palette_guide.py --check','```','',
    '目录包含五张浅深色卡、总览与基础尺寸图（均为可缩放 SVG）、扩展颜色 JSON、对比度报告，以及无第三方依赖的生成器和测试。HEX、RGB、Alpha 与分数 HSL 都由实际源值计算，没有手工维护另一套颜色表。','']
    return '\n'.join(lines)


def outputs(source,outdir):
    ratios=build_contrasts(source)
    expanded={'schemaVersion':1,'provenance':'original adaptation; actual frontend template tokens',
      'precision':'HEX/RGB/alpha and hslExact are exact. hslCss is rounded to six decimal places.',
      'palettes':{pid:{'name':p['name'],**{mode:{k:color(v) for k,v in p[mode].items()} for mode in ('light','dark')}} for pid,p in source['data']['palettes'].items()},
      'common':{mode:{k:color(v) for k,v in vals.items()} for mode,vals in source['common'].items()},
      'shadows':{mode:{'css':v,'colors':[color(h) for h in re.findall(r'#[0-9a-fA-F]{8}',v)]} for mode,v in source['shadows'].items()},
      'sourceSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source['paths'].values()}}
    report={'method':'WCAG relative luminance on sRGB; alpha composited against opaque background before luminance. Thresholds evaluated before rounding.', 'allPassed':all(c['passed'] for r in ratios for c in r['checks']),'palettes':ratios}
    assert report['allPassed'], 'Contrast regression: inspect contrast-report.json'
    result={'README.md':write_readme(source,outdir,ratios),'tokens-expanded.json':json.dumps(expanded,ensure_ascii=False,indent=2)+'\n','contrast-report.json':json.dumps(report,ensure_ascii=False,indent=2)+'\n','swatches/overview.svg':overview_svg(source),'swatches/foundations.svg':foundations_svg(source)}
    for pid,p in source['data']['palettes'].items(): result[f'swatches/{pid}.svg']=palette_svg(pid,p,source)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path)
    parser.add_argument('--output-dir',type=Path,default=ROOT)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    source_dir=args.source_dir
    if source_dir is None:
        source_dir=next((p for p in (ROOT.parent/'frontend-templates'/'shared',ROOT.parent/'styles') if (p/'claude-tokens.css').exists()),None)
    if source_dir is None: parser.error('Supply --source-dir with the shared token files')
    source=load_sources(source_dir.resolve())
    files=outputs(source,args.output_dir.resolve())
    for name,body in files.items():
        path=args.output_dir/name
        if args.check:
            assert path.exists() and path.read_text()==body,f'Generated file stale: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(body)
    print(f'{"Verified" if args.check else "Generated"} {len(files)} artifacts; 90 palette values matched CSS/JSON; 190 contrast checks passed.')


if __name__=='__main__': main()
