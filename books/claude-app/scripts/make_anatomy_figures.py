#!/usr/bin/env python3
"""Original research illustrations; selected facts, never reconstructed screenshots.

Uses only public-facing selected observations. Noto CJK is a system fallback;
no bundled product fonts, logos, screenshots or original product code are used.
Run from any directory. Optional raster QA: Inkscape CLI, not browser automation.
"""
from pathlib import Path
import json, html

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((BASE / 'data/design-token-summary.json').read_text())
COLORS = DATA['selected_tokens']['colors']
DENSITY = DATA['selected_tokens']['density']
INK = '#24231f'
MUTED = '#5f5d55'
PAPER = '#f2f0e9'
LINE = '#d6d2c7'
BLUE = '#245b7c'
CLAY = '#8f4831'
WHITE = '#ffffff'

def esc(s): return html.escape(str(s), quote=True)
def n(v): return f'{v:g}' if isinstance(v, (float,int)) else str(v)
def c(profile, token): return COLORS[profile]['--cds-' + token]['resolved_srgb']
def a(profile, token): return COLORS[profile]['--cds-' + token]['alpha']
def d(profile, token): return DENSITY[profile]['--cds-' + token]['px_at_rem16_scale1']

def alpha_label(profile, token):
    item = COLORS[profile]['--cds-'+token]
    if token == 'backdrop' and profile == 'cds_dark':
        return '#00000080 · α = 128/255 ≈ 50.196%'
    return f"{item['resolved_srgb']} · α = {n(item['alpha'] * 100)}%"

class Figure:
    def __init__(self, filename, width, height, title, description):
        self.filename, self.width, self.height = filename, width, height
        self.body, self.i = [], 0
        self.title, self.description = title, description
        self.rect(0,0,width,height,PAPER,0)
    def add(self, s): self.body.append(s)
    def text(self,x,y,s,size=22,fill=INK,weight=400,anchor='start',**kw):
        self.i += 1
        extra=' '.join(f'{k.replace("_","-")}="{esc(v)}"' for k,v in kw.items())
        self.add(f'<text id="t{self.i}" x="{n(x)}" y="{n(y)}" fill="{fill}" font-size="{n(size)}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')
    def lines(self,x,y,lines,size=20,leading=30,fill=INK,weight=400):
        for i,s in enumerate(lines): self.text(x,y+i*leading,s,size,fill,weight)
    def rect(self,x,y,w,h,fill=WHITE,r=16,stroke='none',sw=1,opacity=1,dash=None,**kw):
        extras=' '.join(f'{k.replace("_","-")}="{esc(v)}"' for k,v in kw.items())
        da=f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="{fill}" fill-opacity="{n(opacity)}" stroke="{stroke}" stroke-width="{n(sw)}"{da} {extras}/>')
    def line(self,x1,y1,x2,y2,color=LINE,sw=1,dash=None):
        da=f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{color}" stroke-width="{n(sw)}"{da}/>')
    def path(self,pts,color=INK,sw=2):
        self.add(f'<path d="{pts}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    def circle(self,x,y,r,fill=BLUE):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')
    def badge(self,x,y,label,fill=BLUE):
        self.circle(x,y,15,fill); self.text(x,y+6,label,17,WHITE,650,'middle')
    def tag(self,x,y,s,w,fill='#e6e2d6',textfill=MUTED):
        self.rect(x,y,w,32,fill,16); self.text(x+14,y+22,s,16,textfill,500)
    def title_block(self,kicker,title,subtitle):
        self.text(48,41,kicker,17,CLAY,650)
        self.text(48,88,title,34,INK,650)
        self.text(48,124,subtitle,19,MUTED)
    def footer(self,y,lines):
        self.line(48,y,1352,y)
        self.lines(48,y+28,lines,17,26,MUTED)
    def swatch(self,x,y,w,h,profile,token,r=10,stroke='none'):
        item = COLORS[profile]['--cds-'+token]
        self.add(f'<g data-profile="{profile}" data-token="--cds-{token}" data-resolved-srgb="{item["resolved_srgb"]}" data-alpha="{item["alpha"]}">')
        self.rect(x,y,w,h,item['resolved_srgb'],r,stroke,opacity=item['alpha'])
        self.add('</g>')
    def write(self):
        meta = {'kind':'original research diagram; not a screenshot', 'product_sample':'Claude Desktop Linux 2.37337.1', 'evidence':'packaged_static; runtime activation unverified', 'sources':['data/design-token-summary.json','data/component-trace.json','data/design-component-rules.json','data/official-image-observations.json'], 'font_policy':'system Noto Sans CJK SC fallback; no product font assets'}
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="figure-title figure-desc">
<title id="figure-title">{esc(self.title)}</title><desc id="figure-desc">{esc(self.description)}</desc>
<metadata>{esc(json.dumps(meta,ensure_ascii=False))}</metadata>
<style>text{{font-family:"Noto Sans CJK SC","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif}} text{{font-kerning:normal}}</style>
<defs><filter id="soft-shadow" x="-30%" y="-50%" width="160%" height="210%"><feGaussianBlur in="SourceAlpha" stdDeviation="8" result="blur"/><feOffset in="blur" dx="0" dy="7" result="offset"/><feFlood flood-color="#24231f" flood-opacity="0.13" result="color"/><feComposite in="color" in2="offset" operator="in" result="shadow"/><feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
{''.join(self.body)}</svg>'''
        (OUT/self.filename).write_text(svg)
        return self.filename


def palette():
    f=Figure('cds-palette.svg',1400,1720,'CDS 选定浅深色板：角色、色值与透明叠加','原创速查图。依据 Linux 2.37337.1 中选定 CDS 根声明和显式 dark 覆盖，不代表当前已登录界面。透明色实际绘制在各主题 surface-0 上，原 RGB 和 alpha 均列出。')
    f.title_block('01 / 配色速查','CDS：同一角色，在浅色与深色中成对读取','选定根声明 + 显式 dark 覆盖；不混入旧 HSL、v2 桥接或独立 df 框架。')
    for j,profile in enumerate(['cds_light','cds_dark']):
        x=48+j*664;w=640
        bg,fg,secondary=c(profile,'surface-0'),c(profile,'text-primary'),c(profile,'text-secondary')
        f.rect(x,158,w,1450,bg,20,LINE)
        f.text(x+24,197,'浅色 · cds_light' if j==0 else '深色 · cds_dark',25,fg,650)
        f.text(x+24,229,'透明色统一叠在 surface-0：'+bg,17,secondary)
        f.text(x+24,272,'A  连续表面',21,fg,650)
        for i in range(4):
            sx=x+24+i*148
            f.swatch(sx,291,136,58,profile,f'surface-{i}',9,LINE if j==0 else '#42413d')
            f.text(sx,375,f'surface-{i}',18,secondary)
            f.text(sx,403,c(profile,f'surface-{i}'),19,fg,500)
        f.text(x+24,440,'panel → surface-2；popover → surface-3',18,secondary)
        f.line(x+24,460,x+w-24,460,LINE if j==0 else '#42413d')
        f.text(x+24,496,'B  文字层级',21,fg,650)
        for i,token in enumerate(['text-primary','text-secondary','text-muted','text-accent']):
            yy=528+i*39
            f.swatch(x+24,yy-18,23,23,profile,token,5)
            f.text(x+60,yy,token,19,fg)
            f.text(x+355,yy,c(profile,token),19,secondary)
        f.line(x+24,672,x+w-24,672,LINE if j==0 else '#42413d')
        f.text(x+24,708,'C  动作、品牌与交互',21,fg,650)
        for i,(fill,on,label) in enumerate([('fill-primary','on-primary','primary'),('fill-brand','on-brand','brand'),('fill-accent','on-accent','accent')]):
            sx=x+24+i*198
            f.swatch(sx,728,186,55,profile,fill,10)
            f.text(sx+93,763,label,21,c(profile,on),650,'middle')
            f.text(sx,811,c(profile,fill),18,fg)
            f.text(sx,838,'on '+c(profile,on),16,secondary)
        f.swatch(x+24,861,28,28,profile,'clay',7)
        f.text(x+64,883,'clay '+c(profile,'clay'),18,fg)
        f.swatch(x+318,861,28,28,profile,'fill-accent-hover',7)
        f.text(x+358,883,'accent-hover '+c(profile,'fill-accent-hover'),16,fg)
        f.text(x+24,920,'fill-brand = clay-emphasized；clay 与 accent 各司其职',17,secondary)
        f.line(x+24,941,x+w-24,941,LINE if j==0 else '#42413d')
        f.text(x+24,977,'D  透明边界与薄底色',21,fg,650)
        for i,token in enumerate(['border','border-strong','fill-ghost-hover','fill-ghost-selected','bg-user-message','backdrop']):
            yy=1012+i*55
            f.swatch(x+24,yy-21,62,36,profile,token,6)
            f.text(x+103,yy-3,token,18,fg)
            f.text(x+103,yy+19,alpha_label(profile,token),16,secondary)
        f.line(x+24,1350,x+w-24,1350,LINE if j==0 else '#42413d')
        f.text(x+24,1386,'E  状态：前景 / 底色',21,fg,650)
        for i,(token,label) in enumerate([('danger','风险'),('success','成功'),('warning','警示')]):
            yy=1425+i*49
            f.swatch(x+24,yy-24,84,36,profile,'bg-'+token,8)
            f.text(x+66,yy+1,label,18,c(profile,'text-'+token),600,'middle')
            f.text(x+126,yy,token,18,fg)
            f.text(x+242,yy,c(profile,'text-'+token)+' / '+c(profile,'bg-'+token),17,secondary)
    f.footer(1635,['范围：所有色值来自选定静态配置；色样不是截图取色，也不代表每个组件会使用这一配对。',
                   '阅读方式：标注省略 --cds- 前缀。透明 swatch 显示叠加结果；标注仍保留原 RGB + alpha，不伪装成不透明 HEX。'])
    return f.write()


def anatomy():
    f=Figure('component-anatomy.svg',1400,1340,'组件解剖：完整 composer、条件插槽、独立 Quick Entry 与 Card 层','原创结构示意，不是当前应用截图。复合 composer 的槽位以目录分开列出，不宣称同时可见；Quick Entry 是另一个本地 HTML 表面。卡片层来自 C07 和 card_surface/card_press 静态规则。')
    f.title_block('02 / 组件解剖','完整输入面、轻入口和卡片，各自承担一件事','布局与尺寸比例为原创示意；组件命名来自包内静态证据，运行时启用情况未确认。')
    f.text(48,177,'A  完整 composer：编辑与工具分层',24,INK,650)
    f.tag(950,153,'C05 / C06 · 包内组件',285)
    f.rect(48,202,828,347,'none',22,BLUE,2,dash='8 7')
    f.text(70,235,'ChatComposerDock · 独立停靠包装层',19,BLUE,600)
    f.rect(75,256,774,257,WHITE,22,'#bbb7ab',1.5)
    f.text(103,299,'在这里写清楚你想完成的事……',25,MUTED)
    f.line(103,330,104,362,CLAY,2)
    f.text(103,388,'编辑区域 · 此处只示意输入，不恢复实际编辑器 DOM',17,MUTED)
    f.rect(100,430,46,46,'#f2f0e9',10)
    f.path('M 113 453 H 133 M 123 443 V 463',INK,2)
    f.rect(158,430,100,46,'#f2f0e9',10)
    f.text(208,460,'工具',20,INK,500,'middle')
    f.text(592,459,'模型 / 模式',20,MUTED)
    f.path('M 722 451 L 727 456 L 732 451',MUTED,2)
    f.rect(769,430,50,46,c('cds_light','fill-brand'),10)
    f.path('M 794 464 V 442 M 786 450 L 794 442 L 802 450',WHITE,2.5)
    f.badge(280,453,'1');f.badge(829,422,'2')
    f.text(70,580,'1  Actions · 辅助操作',20,INK,600)
    f.text(410,580,'2  PrimaryAction · 主动作',20,INK,600)
    f.text(70,610,'此例仅组装输入、工具、模型与提交；不是产品的默认状态截图。',18,MUTED)
    f.rect(908,202,444,410,'#e9e6dd',20)
    f.text(932,239,'条件插槽清单',23,INK,650)
    f.text(932,269,'不在左图中全部同时铺开',18,MUTED)
    slots=[('Header','头部插槽'),('Attachments','附件区'),('Chin','底栏插槽'),('Overlay','覆盖层插槽'),('Tray','托盘插槽')]
    for i,(name,zh) in enumerate(slots):
        yy=308+i*45
        f.rect(932,yy-23,18,18,'none',4,BLUE,1.5,dash='4 3')
        f.text(963,yy,name,20,INK,550)
        f.text(1195,yy,zh,18,MUTED)
    f.lines(932,554,['可见性和组合取决于 variant / state。','new / reply、busy、disabled、drag-over','等状态名称来自 C06；不等于全部已启用。'],16,24,MUTED)
    f.line(48,645,1352,645)
    f.text(48,686,'B  Quick Entry：独立本地窗口，初始紧凑为一行',24,INK,650)
    f.tag(1055,663,'C11 / C12 · 包内',276)
    f.rect(66,721,810,90,WHITE,22,LINE,filter='url(#soft-shadow)')
    f.text(93,777,'直接输入一个问题……',23,MUTED)
    f.text(599,777,'新对话',20,INK)
    f.path('M 682 763 L 689 770 L 696 763',MUTED,2)
    f.rect(796,742,54,48,c('cds_light','fill-brand'),10)
    f.path('M 823 777 V 755 M 815 763 L 823 755 L 831 763',WHITE,2.5)
    f.lines(66,853,['输入与上下文、提交共用一条水平轴；支持随文本增长调整高度（静态处理器）。'],18,27,MUTED)
    f.lines(929,746,['输入行 min-height：56px','容器 radius：16px','文字：16px / 150% 行高','这些尺寸只属于 Quick Entry。'],20,34,INK)
    f.line(48,900,1352,900)
    f.text(48,943,'C  Card：填充层与内容层分开，链接层补足交互',24,INK,650)
    f.tag(1070,920,'C07 + card_*',250)
    # An exploded original layer diagram. Depth offsets are explanatory, not measured.
    f.rect(74,978,540,192,'none',19,'#a8a293',1.5)
    f.rect(102,1001,540,192,c('cds_light','surface-1'),19,'#c8c3b7')
    f.rect(132,1027,540,143,WHITE,15,'#c8c3b7')
    f.text(156,1062,'内容主体 · cds-card-body',21,INK,600)
    f.lines(156,1098,['示例文件 / 结果标题','元信息与独立内容'],19,28,MUTED)
    f.rect(132,1027,540,143,'none',15,BLUE,2,dash='8 6')
    f.badge(78,975,'1');f.badge(107,1000,'2');f.badge(136,1026,'3');f.badge(673,1051,'4')
    f.lines(729,987,['1  圆角外轮廓：焦点表达位于卡片边界','2  装饰填充：常态 surface-1','3  带内边距的内容主体','4  CardLink 覆盖层（蓝色虚线为示意）'],19,35,INK)
    f.lines(729,1145,['含 CardLink 的 hover → surface-2；','按下同步调整填充缩放与内容裁切。'],18,28,MUTED)
    f.footer(1237,['读图边界：官方 A1 / A2 只支持两层 composer 与单行入口的视觉关系；包内 C05–C12 提供结构与状态锚点。',
                   'Card 是通用原语，不能据此声称已恢复全部文件 / 工具结果组件。阴影与爆炸层偏移均为本图原创表达。'])
    return f.write()


def blocks():
    f=Figure('color-block-anatomy.svg',1400,1600,'色块剖面：阅读、实体、编辑与临时浮层的四类边界','原创分析图，非界面复刻。色彩使用选定 CDS 浅色值，布局为解释角色而绘制。阅读示意不否认历史及条件助手气泡；下方卡片密度对照是原创受控实验，并非产品旧新版本。')
    f.title_block('03 / 色块剖面','色块不只是选一个底色，而是决定边界放在哪里','中性画布占大面积；实体、编辑区与临时层按职责获得不同的填充、边线或遮罩。')
    panels=[(48,160,630,388),(722,160,630,388),(48,582,630,388),(722,582,630,388)]
    for x,y,w,h in panels:f.rect(x,y,w,h,WHITE,20,LINE)
    # Reading.
    x,y,_,_=panels[0]
    f.text(x+24,y+40,'A  连续阅读画布',24,INK,650)
    f.rect(x+24,y+65,582,232,c('cds_light','surface-0'),12)
    f.text(x+47,y+102,'先让问题与回复形成连续的阅读节奏',22,INK,600)
    f.lines(x+47,y+143,['回复内容直接落在画布上，','段落、列表和留白建立关系。'],20,34,INK)
    f.lines(x+47,y+238,['另一段内容从这里继续，保留阅读方向。'],19,32,MUTED)
    f.line(x+580,y+132,x+580,y+218,CLAY,2)
    f.line(x+574,y+132,x+586,y+132,CLAY,2);f.line(x+574,y+218,x+586,y+218,CLAY,2)
    f.lines(x+24,y+329,['主要分隔：段落节奏与间距。','本例是开放回复示意；并非所有助手消息都无框。'],18,29,MUTED)
    # User/file entity.
    x,y,_,_=panels[1]
    f.text(x+24,y+40,'B  消息与文件实体',24,INK,650)
    f.rect(x+24,y+65,582,232,c('cds_light','surface-0'),12)
    f.swatch(x+185,y+88,396,63,'cds_light','bg-user-message',14)
    f.text(x+211,y+128,'请把这份资料整理成提纲。',21,INK)
    f.rect(x+49,y+179,507,90,c('cds_light','surface-1'),12,'#d9d8d3')
    f.rect(x+67,y+198,43,49,'none',7,'#a8a69e',1.5)
    f.line(x+78,y+214,x+98,y+214,'#a8a69e',1.5);f.line(x+78,y+224,x+98,y+224,'#a8a69e',1.5)
    f.text(x+128,y+215,'研究资料',20,INK,600);f.text(x+128,y+244,'文件实体 · 可操作的独立对象',17,MUTED)
    f.lines(x+24,y+329,['薄底色区分消息；卡片把文件聚成一个对象。','用户消息示例：#0b0b0b × 5%，叠于 surface-0。'],18,29,MUTED)
    # Composer.
    x,y,_,_=panels[2]
    f.text(x+24,y+40,'C  有边界的编辑面',24,INK,650)
    f.rect(x+24,y+65,582,232,c('cds_light','surface-0'),12)
    f.rect(x+48,y+88,534,186,c('cds_light','surface-2'),18,'#c7c4bb',1.5)
    f.text(x+69,y+131,'可以在这里补充内容……',22,MUTED)
    f.line(x+71,y+156,x+71,y+182,CLAY,2)
    f.path(f'M {x+72} {y+237} H {x+94} M {x+83} {y+226} V {y+248}',INK,2)
    f.text(x+378,y+243,'模式',18,MUTED)
    f.rect(x+506,y+215,48,42,c('cds_light','fill-brand'),9)
    f.path(f'M {x+530} {y+246} V {y+225} M {x+522} {y+233} L {x+530} {y+225} L {x+538} {y+233}',WHITE,2)
    f.lines(x+24,y+329,['边界围住可编辑区域，操作留在底部同一带。','填色集中于提交动作；绘图几何不是截图测量值。'],18,29,MUTED)
    # Temporary layer.
    x,y,_,_=panels[3]
    f.text(x+24,y+40,'D  临时层：提示与对话框',24,INK,650)
    f.rect(x+24,y+65,582,232,c('cds_light','surface-0'),12)
    f.text(x+44,y+105,'原工作内容',20,MUTED)
    f.line(x+44,y+132,x+312,y+132,LINE,3)
    f.line(x+44,y+151,x+490,y+151,LINE,3)
    f.swatch(x+24,y+65,582,232,'cds_light','backdrop',12)
    f.rect(x+140,y+128,347,140,c('cds_light','surface-panel'),14,LINE,filter='url(#soft-shadow)')
    f.text(x+163,y+162,'确认当前操作',21,INK,650)
    f.text(x+163,y+195,'面板与背景的层次被暂时拉开。',17,MUTED)
    f.rect(x+350,y+215,110,32,c('cds_light','fill-primary'),7)
    f.text(x+405,y+237,'继续',17,c('cds_light','on-primary'),600,'middle')
    f.rect(x+346,y+70,231,44,'#292827',9)
    f.text(x+462,y+99,'提示层：按需补充语义',17,WHITE,500,'middle')
    f.lines(x+24,y+329,['本图将两类临时层并列说明，不主张同时出现。','遮罩：#000000 × 40%；阴影为原创示意。'],18,29,MUTED)
    # Controlled experiment, intentionally with identical text and content counts.
    f.text(48,1023,'受控对照：同一份内容，是否每一段都要一张卡片？',27,INK,650)
    f.text(48,1058,'原创实验，解释边界密度；不是 Claude 的旧版 / 新版对照。',19,MUTED)
    for j in range(2):
        x=48+j*674;y=1086
        f.rect(x,y,630,331,c('cds_light','surface-0'),18,LINE)
        f.text(x+24,y+39,'每段都套容器' if j==0 else '按角色分配容器',23,INK,650)
        if j==0:
            for yy in [y+65,y+133,y+201]:f.rect(x+24,yy,582,56,WHITE,10,'#bbb7ab',1.3)
        else:
            f.swatch(x+216,y+65,390,56,'cds_light','bg-user-message',12)
            f.rect(x+24,y+201,582,56,c('cds_light','surface-1'),10,'#d9d8d3')
        f.text(x+(44 if j==0 else 236),y+102,'问题：这份研究的重点是什么？',20,INK)
        f.text(x+44,y+170,'回复：先看配色、色块与组件关系。',20,INK)
        f.text(x+44,y+238,'附件：设计观察.pdf',20,INK)
        f.text(x+24,y+299,'边界反复出现，三种角色被等量强调。' if j==0 else '填充 / 留白 / 细框，承担不同的分组任务。',18,MUTED)
    f.footer(1460,['证据对照：官方 A1（输入）、B1（tooltip）、C3（2024 对话 / Artifact）；包内 C04 / C07 / C08 与 card_surface。',
                   '历史限定：2024 官方图含助手回复框；包内也有 AssistantMessage 的 bubble 分支，开放回复不能覆盖全部情境。',
                   '图中内容、排布、图标均为原创。精确色值参考 CDS 选定色板；面积、间距和阴影不作为产品测量结论。'])
    return f.write()


def density():
    f=Figure('density-comparison.svg',1400,1530,'密度比较：默认与 comfortable，正文偏好与工具尺寸分离','依据选定 CDS 默认与 comfortable 声明生成的原创同内容样本。换算假设根字号 16px、rem-scale=1；样本绘图放大 2 倍且布局宽高原创，不是产品真实组件尺寸或屏幕截图。')
    f.title_block('04 / 密度与阅读','comfortable 是一组协调变化，不是整屏统一缩放','换算假设：根字号 16px，--cds-rem-scale = 1；以下 px 为 CSS 换算值，不是截图测量值。')
    for j,profile in enumerate(['cds_light','cds_comfortable']):
        x=48+j*674;y=158
        f.rect(x,y,630,478,WHITE,20,LINE)
        f.text(x+24,y+39,'默认 · cds_light' if j==0 else 'comfortable 覆盖',25,INK,650)
        f.text(x+24,y+72,'同内容样本 · 字号 / 控件 / 圆角均以 2 倍绘出',17,MUTED)
        py=y+98
        f.rect(x+24,py,582,286,'#f9f9f7',2*d(profile,'panel-radius'),'#d9d8d3')
        body=d(profile,'font-size-body');leading=d(profile,'leading-body')
        prose=d(profile,'font-size-prose');proselead=d(profile,'leading-prose')
        f.text(x+48,py+43,'界面：研究资料',2*body,INK,600)
        f.lines(x+48,py+93,['先整理问题，','再决定下一步。'],2*prose,2*proselead,INK)
        h=d(profile,'h-control')*2;icon=d(profile,'icon')*2;r=d(profile,'radius')*2
        cy=py+254-h
        f.rect(x+48,cy,198,h,'#e9e6dc',r)
        ix=x+68; iy=cy+(h-icon)/2
        f.rect(ix,iy,icon,icon,'none',3,INK,2)
        f.text(ix+icon+15,cy+h/2+2*body*.36,'复制',2*body,INK,500)
        f.text(x+24,y+420,f'body {n(body)} / {n(leading)}px　prose {n(prose)} / {n(proselead)}px',20,INK,600)
        f.text(x+24,y+452,f'控件 {n(h/2)}px　图标 {n(icon/2)}px　panel radius {n(d(profile,"panel-radius"))}px',19,MUTED)
    f.text(48,686,'并排核对：有些量增幅大，有些量只增加一点',26,INK,650)
    rows=[('控件高度 / 内嵌控件','h-control','h-control-nested'),('图标 / 基础圆角','icon','radius'),('composer / panel 圆角','radius-composer','panel-radius'),('body 字号 / 行高','font-size-body','leading-body'),('prose 字号 / 行高','font-size-prose','leading-prose')]
    f.rect(48,711,1304,335,WHITE,18,LINE)
    f.text(72,751,'角色',21,MUTED,600);f.text(682,751,'默认',21,MUTED,600);f.text(1025,751,'comfortable',21,MUTED,600)
    for i,(label,t1,t2) in enumerate(rows):
        yy=799+i*49
        f.line(72,yy-30,1328,yy-30,'#e6e2d8')
        f.text(72,yy,label,21,INK)
        for xx,p in [(682,'cds_light'),(1025,'cds_comfortable')]:
            f.add(f'<g data-profile="{p}" data-density-tokens="--cds-{t1},--cds-{t2}">')
            f.text(xx,yy,f'{n(d(p,t1))} / {n(d(p,t2))} px',21,INK,600)
            f.add('</g>')
    f.rect(48,1071,1304,162,'#e9e6dd',18)
    f.text(72,1111,'间距序列也分别变动（xs → xl）',23,INK,650)
    for i,(label,prefix) in enumerate([('pad','pad-'),('gap','gap-')]):
        yy=1153+i*37
        f.text(72,yy,label,20,MUTED,600)
        for xx,p in [(260,'cds_light'),(790,'cds_comfortable')]:
            values=' / '.join(n(d(p,prefix+s)) for s in ['xs','sm','md','lg','xl'])
            f.text(xx,yy,('默认  ' if p=='cds_light' else 'comfortable  ')+values+' px',20,INK)
    f.text(48,1283,'另一条独立轴：消息正文的 sm / md / lg 偏好',26,INK,650)
    f.lines(48,1324,['正文偏好会改写消息文字相关令牌；内部按钮有恢复自身字号的规则。','因此“更大的阅读文字”不必把复制、菜单等工具一起同比放大。'],21,34,INK)
    f.footer(1410,['尺寸来源：data/design-token-summary.json → selected_tokens.density；正文 / 工具独立规则见 message_text_preferences。',
                   'prose 字号与行高直接使用 rem；许多 UI 尺寸还乘 rem-scale。样本只在本图假设下比较，未模拟完整级联。',
                   '另有 step、size、文本偏好与触摸分支。本图比较所选配置，不声称它们就是每位用户看到的最终密度。'])
    return f.write()

if __name__=='__main__':
    files=[palette(),anatomy(),blocks(),density()]
    print('Wrote original SVG research illustrations:')
    for file in files:print(OUT/file)
