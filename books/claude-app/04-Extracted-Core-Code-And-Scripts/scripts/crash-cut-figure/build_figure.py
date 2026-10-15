#!/usr/bin/env python3
"""Build the original crash-cut teaching figure using Python's standard library.

Optional --render uses the existing Inkscape installation, without downloads.
"""
from pathlib import Path
from html import escape
import argparse
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
NAME = 'crash-cuts-and-recovery'
C = dict(bg='#f5f1e8', paper='#fffdf7', ink='#29291f', muted='#68665c',
         line='#d8d0bf', blue='#395d70', bluebg='#e7edf0',
         sage='#40634d', sagebg='#e6eee5', rust='#984a36', rustbg='#f3e4dc',
         gold='#856326', goldbg='#f3ebd5')


class SVG:
    def __init__(self):
        self.parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650" role="img" aria-labelledby="title desc">',
            '<title id="title">写完、替换、提交：五个暂停点的恢复承诺</title>',
            '<desc id="desc">原创单 writer 逻辑崩溃恢复教学模型，不是 Claude 的实现或断电持久性保证。'
            'C2 writeComplete：候选写完并读回核对，target 为 r7、candidate 为 r8，无 intent；恢复保留 r7，不安装孤儿候选。'
            'C4 完整 intent 写完：target 为 r7、candidate 为 r8，意图完整；只有合法 intent 与预期操作一致，targetHash 等于 baseHash，候选摘要、JSON 结构、revision 都匹配，才安装候选，再写 receipt 并退休 intent。'
            'C5 renameComplete：target 已为 r8，candidate 已无，intent 完整，receipt 尚无；恢复优先识别已安装，补匹配回执并退休 intent，不再替换 target。'
            'C6 匹配 receipt 已写完：target 为 r8，intent 尚在；恢复验证匹配回执，只退休 intent，不重复替换或重写回执。'
            'C7 commitComplete：target 为 r8，匹配 receipt 存在，intent 已退休；确认 already-committed，不再写入，但调用方可能还没有收到成功回复。'
            '各行的替换与回执写入计数仅指首次恢复子进程，依次为 0/0、1/1、0/1、0/0、0/0，不是跨崩溃的持久总账。'
            '错误回执或冲突状态不能按成功路径继续。本模型无 fsync、无硬件断电测试，不证明持久顺序或外部副作用恰好一次。</desc>',
            '<style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei","PingFang SC",sans-serif}</style>',
            '<defs>' + ''.join(f'<marker id="arrow-{k}" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4.5L0 9Z" fill="{C[k]}"/></marker>' for k in ('blue', 'gold', 'sage')) + '</defs>'
        ]
        self.bounds = {}
        self.n = 0

    def rect(self, x, y, w, h, fill, stroke=None, radius=12):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{C.get(fill,fill)}"' + (f' stroke="{C.get(stroke,stroke)}" stroke-width="1.2"' if stroke else '') + '/>')

    def text(self, x, y, value, size=18, color='ink', weight=400, anchor='start', box=None):
        self.n += 1
        ident = f'text-{self.n}'
        self.parts.append(f'<text id="{ident}" x="{x}" y="{y}" font-size="{size}" fill="{C.get(color,color)}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')
        self.bounds[ident] = box or [32, 16, 968, 646]

    def arrow(self, x1, x2, y, color):
        self.parts.append(f'<path d="M{x1} {y}H{x2}" fill="none" stroke="{C[color]}" stroke-width="2" stroke-linecap="round" marker-end="url(#arrow-{color})"/>')

    def save(self):
        (ROOT / (NAME+'.svg')).write_text('\n'.join(self.parts + ['</svg>'])+'\n', encoding='utf-8')
        (ROOT / (NAME+'.text-bounds.json')).write_text(json.dumps(self.bounds, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def build():
    s = SVG()
    s.rect(0, 0, 1000, 650, 'bg', radius=0)
    s.text(36, 35, '原创合成实验 · 确定阶段之间停止，再启动', 14, 'rust', 600)
    s.text(36, 79, '写完 ≠ 替换完成 ≠ 提交完成', 31, weight=700)
    s.text(36, 109, '完整候选不能自动提交；恢复看留下的事实，不猜上次走到了哪里。', 17, 'muted')

    s.text(54, 147, '已完成阶段', 16, 'muted', 600)
    s.text(320, 147, '停止后留下的事实', 16, 'muted', 600)
    s.text(652, 147, '首次恢复动作', 16, 'muted', 600)

    rows = [
        ('C2', 'writeComplete', '候选写完并读回核对',
         'target r7 · candidate r8', '无 intent · 无 receipt',
         '保留 r7，不安装候选', '无提交意图', '0 / 0', 'blue', 'bluebg'),
        ('C4', '完整 intent', '允许恢复继续的决策点',
         'target r7 · candidate r8', '完整 intent · 无 receipt',
         '验证前提与候选 → 安装 r8', '写回执，退休 intent', '1 / 1', 'gold', 'goldbg'),
        ('C5', 'renameComplete', '正式路径已是新内容',
         'target r8 · candidate 已无', '完整 intent · 无 receipt',
         '已安装，不重复替换', '补回执，退休 intent', '0 / 1', 'sage', 'sagebg'),
        ('C6', '匹配 receipt', '此操作的回执已写完',
         'target r8 · receipt 匹配', 'intent 尚在 · candidate 已无',
         '验证回执，只退休 intent', '不替换，也不重写回执', '0 / 0', 'sage', 'sagebg'),
        ('C7', 'commitComplete', '目标、回执、清理均满足',
         'target r8 · receipt 匹配', 'intent 已退休 · candidate 已无',
         '确认已提交，不再写入', 'already-committed', '0 / 0', 'sage', 'sagebg'),
    ]
    for i, (cut, title, sub, state, files, action, detail, counts, color, bg) in enumerate(rows):
        y = 160 + i*70
        s.rect(36, y, 928, 63, 'paper', 'line')
        s.rect(48, y+14, 41, 32, bg, radius=9)
        s.text(68.5, y+36, cut, 17, color, 700, 'middle', [50,y+15,87,y+45])
        s.text(102, y+26, title, 20, color, 700, box=[98,y+6,306,y+32])
        s.text(102, y+49, sub, 15, 'muted', box=[98,y+32,306,y+57])
        s.text(320, y+26, state, 18, weight=600, box=[316,y+6,600,y+32])
        s.text(320, y+49, files, 15, 'muted', box=[316,y+32,600,y+57])
        s.arrow(608, 635, y+31, color)
        s.text(652, y+26, action, 19, color, 700, box=[648,y+6,950,y+32])
        s.text(652, y+49, detail, 15, 'muted', box=[648,y+32,858,y+57])
        s.rect(875, y+34, 72, 21, bg, radius=5)
        s.text(911, y+50, counts, 14, color, 600, 'middle', [879,y+35,943,y+54])

    s.text(36, 527, '右侧计数 = 本次恢复的「替换 / 回执写入」；不含停止前已完成的动作。', 14, 'muted', box=[32,510,968,531])

    s.rect(36, 539, 928, 49, 'goldbg', radius=10)
    s.text(56, 571, 'C7：提交已完成 ≠ 回复已送达', 23, 'gold', 700, box=[50,545,565,583])
    s.text(571, 570, '本地 receipt 不能证明调用方已收到成功回复。', 16, 'muted', box=[565,545,950,583])

    s.text(36, 611, '成功路径须匹配预期操作；C4 还需核对 baseHash、候选摘要、JSON 结构与 revision。', 14, 'muted', box=[32,593,968,616])
    s.text(36, 637, '原创单 writer 教学模型，非 Claude 实现；无 fsync、无掉电测试，不证明断电持久性。', 14, 'muted', box=[32,619,968,644])
    s.save()


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    parser.add_argument("--out", type=Path, default=Path.cwd(), help="Directory for generated figure")
    args = parser.parse_args()
    ROOT = args.out.resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    build()
    if args.render:
        exe = shutil.which('inkscape')
        if not exe:
            raise SystemExit('SVG generated. Rendering needs an existing Inkscape installation.')
        svg = ROOT / (NAME+'.svg')
        subprocess.run([exe, str(svg), '--export-type=png', '--export-filename='+str(svg.with_suffix('.png'))], check=True, capture_output=True)
    print('Built original 1000 × 650 crash-cut figure' + (' and PNG.' if args.render else '.'))


if __name__ == '__main__':
    main()
