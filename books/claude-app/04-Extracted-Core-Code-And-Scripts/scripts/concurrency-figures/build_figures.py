#!/usr/bin/env python3
"""Build original, self-contained teaching diagrams using only Python's stdlib.

Run: python build_figures.py [--render]
Optional PNG render uses an existing local Inkscape installation; no download.
"""
from pathlib import Path
from html import escape
import argparse
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
C = dict(bg='#f5f1e8', paper='#fffdf7', ink='#29291f', muted='#68665c',
         line='#d8d0bf', blue='#395d70', bluebg='#e7edf0',
         sage='#40634d', sagebg='#e6eee5', rust='#984a36', rustbg='#f3e4dc',
         gold='#856326', goldbg='#f3ebd5')

class SVG:
    def __init__(self, name, title, desc):
        self.name, self.bounds, self.n = name, {}, 0
        self.parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(desc)}</desc>',
            '<style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",sans-serif}</style>',
            '<defs>' + ''.join(f'<marker id="arrow-{k}" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4.5L0 9Z" fill="{C[k]}"/></marker>' for k in ('muted','sage','rust','blue')) + '</defs>'
        ]
        self.rect(0, 0, 1000, 650, C['bg'], radius=0)
    def rect(self, x, y, w, h, fill, stroke=None, radius=12):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="1.2"' if stroke else '')+'/>')
    def text(self, x, y, value, size=18, color='ink', weight=400, anchor='start', box=None):
        self.n += 1
        ident = f'text-{self.n}'
        self.parts.append(f'<text id="{ident}" x="{x}" y="{y}" font-size="{size}" fill="{C.get(color, color)}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')
        self.bounds[ident] = box or [32, 16, 968, 637]
    def path(self, d, color='muted', width=2, arrow=False, dash=None):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{C.get(color,color)}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#arrow-{color})"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def circle(self, x, y, r, fill):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')
    def save(self):
        (ROOT / f'{self.name}.svg').write_text('\n'.join(self.parts + ['</svg>']) + '\n', encoding='utf-8')
        (ROOT / f'{self.name}.text-bounds.json').write_text(json.dumps(self.bounds, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    def head(self, kicker, title, sub):
        self.text(36, 35, kicker, 14, 'rust', 600)
        self.text(36, 80, title, 30, weight=700)
        self.text(36, 111, sub, 17, 'muted')


def concurrency():
    s = SVG('conditional-write-and-receipt', '版本前提挡住旧写入，回执只证明那一次',
        '原创合成单资源模型，不代表 Claude 的真实服务端协议。A 与 B 同读 r7，值为 enabled=true、label=original。A 带 r7 条件关闭 enabled，成功产生 r8。B 仍带 r7 修改 label 时发生冲突，资源保持 r8。B 重新读取 r8，只把 label=renamed 的意图应用到当前值，用新操作身份和 r8 条件提交，得到 r9，值为 enabled=false、label=renamed。之后 A 使用相同 operationId、原 r7 前提和原 payload 重放，只返回 A 当时提交成功的 r8 回执，不再写入。当前资源仍为 r9，旧回执不能覆盖当前 r9 快照。')
    s.head('原创合成模型 · 条件写入与重放', '版本前提挡住旧写入，回执只证明那一次', 'A、B 是独立客户端；状态字段为 enabled / label。')
    s.text(59, 151, '客户端动作', 16, 'muted', 600)
    s.text(677, 151, '权威资源', 16, 'muted', 600)
    rows = [
        (166, '1', 'A、B 同读 r7', '各自保留同一份旧草稿。', 'r7', 'enabled=true  ·  label=original', 'blue', 'bluebg'),
        (233, '2', 'A：带 r7 条件，关闭 enabled', '前提仍成立 → 接受这次提交。', 'r8', 'enabled=false  ·  label=original', 'sage', 'sagebg'),
        (300, '3', 'B：仍带旧 r7，修改 label', '前提已过期 → conflict，不修改资源。', '仍为 r8', 'enabled=false  ·  label=original', 'rust', 'rustbg'),
        (367, '4', 'B：在 r8 上只应用 label 意图', '新操作身份 + r8 条件 → 接受重基提议。', 'r9', 'enabled=false  ·  label=renamed', 'sage', 'sagebg'),
    ]
    for y, num, title, detail, rev, state, color, bg in rows:
        s.rect(36, y, 928, 59, C['paper'], C['line'])
        s.circle(64, y+29.5, 15, C[bg])
        s.text(64, y+36, num, 18, color, 700, 'middle', [48,y+10,80,y+49])
        s.text(92, y+25, title, 20, weight=600, box=[86,y+4,610,y+54])
        s.text(92, y+48, detail, 15, 'muted', box=[86,y+4,610,y+54])
        s.path(f'M613 {y+29.5}H654', color, 2, True)
        if num == '3':
            s.path(f'M627 {y+20}L641 {y+39}M641 {y+20}L627 {y+39}', color, 2)
        s.rect(670, y+6, 281, 47, C[bg], radius=8)
        s.text(681, y+26, rev, 20, color, 700, box=[676,y+8,944,y+52])
        s.text(681, y+45, state, 15, color, box=[676,y+8,944,y+52])
    # The replay is deliberately separated from resource evolution.
    s.rect(36, 447, 928, 153, C['paper'], C['line'])
    s.circle(64, 473, 15, C['goldbg'])
    s.text(64, 479, '5', 18, 'gold', 700, 'middle', [48,454,80,491])
    s.text(92, 480, 'A 重放原请求：返回过去的回执，不再次写入', 21, weight=600)
    s.rect(56, 499, 395, 81, C['goldbg'], radius=9)
    s.text(74, 530, 'A 原操作重放 → 原回执 r8', 23, 'gold', 700, box=[68,505,440,574])
    s.text(74, 558, '同一操作身份、原 r7 前提、原载荷', 16, 'muted', box=[68,505,440,574])
    s.path('M466 525H546', 'rust', 2, True, '5 5')
    s.path('M495 515L511 535M511 515L495 535', 'rust', 3)
    s.text(505, 559, '不可覆盖', 15, 'rust', 600, 'middle', [456,542,554,571])
    s.rect(560, 499, 384, 81, C['sagebg'], radius=9)
    s.text(578, 530, '当前资源仍为 r9', 23, 'sage', 700, box=[572,505,938,574])
    s.text(578, 558, 'enabled=false  ·  label=renamed', 17, 'sage', box=[572,505,938,574])
    s.text(36, 631, '回执记录那一次的结果；当前值仍需读取权威资源。教学轨迹不代表真实产品协议。', 16, 'muted')
    s.save()


def slicing():
    s = SVG('chunk-slicing-and-checkpoints', '把检查点放进工作里',
        '原创有效输入实验，计数不是 FPS 或耗时，也不描述 Claude 的真实运行。相同输入包含 180000 字节、20000 个短事件。整块路径一次 push 180000 字节，先生成 20000 帧，再执行全部回调，首次 afterChunk 检查点发生在第 20000 次回调后。分片路径每次 push 最多 4096 字节，同片每交付 128 帧到达检查点并让出，片尾即使没有完整帧也让出；本输入首次让出发生在第 128 次回调后，全部 20000 帧保持原顺序。这里是逻辑计数，不保证帧率、耗时或实时响应；单次同步解析和单个回调仍不可被抢占。')
    s.head('原创合成实验 · 输入片与回调检查点', '把检查点放进工作里', '同一段有效输入，改变的是到下一次检查点之前的工作量。')
    s.rect(36, 132, 928, 53, C['paper'], C['line'])
    s.text(59, 166, '同一输入', 18, 'muted', 600)
    s.text(183, 166, '180,000 字节  /  20,000 个短事件', 24, weight=700)
    s.text(942, 166, '顺序保持', 16, 'sage', 600, 'end')
    panels = [(36, '整块 push', 'rust', 'rustbg'), (514, '分片 + 帧检查点', 'sage', 'sagebg')]
    for x,title,color,bg in panels:
        s.rect(x, 201, 450, 340, C['paper'], C['line'])
        s.rect(x+17, 218, 5, 28, C[color], radius=2)
        s.text(x+35, 242, title, 25, color, 700, box=[x+28,211,x+434,251])
        s.rect(x+21, 262, 408, 43, C[bg], radius=8)
        s.rect(x+21, 323, 408, 43, C[bg], radius=8)
        s.path(f'M{x+225} 308V320', color, 2, True)
    s.text(261, 290, '一次 push：180,000 字节', 20, 'rust', 600, 'middle', [64,267,458,301])
    s.text(261, 351, '先生成全部 20,000 帧', 20, 'rust', 600, 'middle', [64,328,458,362])
    s.path('M261 370V394', 'rust', 2, True)
    s.text(261, 417, '首次 afterChunk 检查点前', 17, 'muted', 500, 'middle')
    s.text(261, 476, '20,000', 48, 'rust', 700, 'middle', [64,425,458,488])
    s.text(261, 511, '次回调，才到首次让出机会', 18, 'rust', 500, 'middle')
    s.text(739, 290, '每次 push ≤ 4,096 字节', 20, 'sage', 600, 'middle', [542,267,936,301])
    s.text(739, 351, '每交付 128 帧 → 检查点', 20, 'sage', 600, 'middle', [542,328,936,362])
    s.text(739, 387, '继续当前片；片尾也让出', 17, 'muted', 500, 'middle')
    s.text(739, 417, '本输入首次让出前', 17, 'muted', 500, 'middle')
    s.text(739, 476, '128', 48, 'sage', 700, 'middle', [542,425,936,488])
    s.text(739, 511, '次回调，随后继续按序交付', 18, 'sage', 500, 'middle')
    s.rect(36, 558, 928, 60, C['goldbg'], radius=10)
    s.text(57, 584, '逻辑计数，不是 FPS 或耗时', 20, 'gold', 700)
    s.text(57, 607, '小片与检查点不能抢占单个同步解析或回调；全部 20,000 帧仍须按序处理。', 16, 'muted')
    s.text(36, 639, '本图仅解释原创实验的检查粒度，不代表 Claude 实测、帧率或实时响应保证。', 14, 'muted', box=[32,620,968,648])
    s.save()


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true', help='Render PNGs with installed Inkscape')
    parser.add_argument('--out', type=Path, default=Path.cwd(), help='Directory for generated diagrams')
    args = parser.parse_args()
    ROOT = args.out.resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    concurrency()
    slicing()
    if args.render:
        exe = shutil.which('inkscape')
        if not exe:
            raise SystemExit('SVGs generated. PNG rendering requires an installed Inkscape.')
        for path in [ROOT / 'conditional-write-and-receipt.svg', ROOT / 'chunk-slicing-and-checkpoints.svg']:
            subprocess.run([exe, str(path), '--export-type=png', '--export-filename='+str(path.with_suffix('.png'))], check=True, capture_output=True)
    print('Built two original 1000 × 650 SVGs' + (' and PNGs.' if args.render else '.'))

if __name__ == '__main__':
    main()
