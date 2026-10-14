#!/usr/bin/env python3
"""Original learning diagrams. Python standard library only; no external assets.
Run: python build_learning_figures.py
The geometry and test data are pedagogical examples, not runtime captures.
"""
from pathlib import Path
from html import escape
import json
import math
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parents[2] / "assets" / "figures"
P = dict(bg='#f5f3ec', paper='#fcfcfa', ink='#25231e', muted='#67645c', line='#d9d5cb',
         rust='#a65539', rustlight='#f2e2d7', sage='#466957', sagelight='#e7ece7',
         lilac='#e9e7ed', quiet='#eeeae1', inactive='#aaa69b')

class SVG:
    def __init__(self, name, title, desc, height):
        self.name, self.height = name, height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}" role="img" aria-labelledby="title desc">',
                      f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
                      '<style>text{font-family:"Noto Sans CJK SC",system-ui,sans-serif} .mono{font-family:"DejaVu Sans Mono","Noto Sans CJK SC",monospace}</style>',
                      '<defs>' + ''.join(f'<marker id="arrow-{k}" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0L8 4L0 8Z" fill="{P[k]}"/></marker>' for k in ['muted','rust','sage']) + '</defs>']
        self.rect(0,0,1440,height,P['bg'],rx=0)
    def rect(self,x,y,w,h,fill=None,stroke=None,rx=16,sw=1.5):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or P["paper"]}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>')
    def text(self,x,y,text,size=22,fill=None,weight=400,anchor='start',mono=False):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or P["ink"]}" font-weight="{weight}" text-anchor="{anchor}"'+(' class="mono"' if mono else '')+f'>{escape(str(text))}</text>')
    def lines(self,x,y,lines,size=21,fill=None,leading=33,weight=400):
        for i,t in enumerate(lines): self.text(x,y+i*leading,t,size,fill,weight)
    def line(self,x1,y1,x2,y2,color=None,width=2,arrow=None):
        self.parts.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color or P["line"]}" stroke-width="{width}" stroke-linecap="round"'+(f' marker-end="url(#arrow-{arrow})"' if arrow else '')+'/>')
    def path(self,d,color=None,width=2,arrow=None):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color or P["line"]}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"'+(f' marker-end="url(#arrow-{arrow})"' if arrow else '')+'/>')
    def circle(self,x,y,r,fill,stroke=None):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')+'/>')
    def header(self,tag,title,subtitle):
        self.text(60,56,tag,18,P['rust'],600)
        self.text(60,110,title,37,weight=700)
        self.text(60,148,subtitle,21,P['muted'])
    def badge(self,x,y,w,text,color='sage',size=18):
        self.rect(x,y,w,34,P[color+'light'],rx=17)
        self.text(x+w/2,y+24,text,size,P[color],600,'middle')
    def save(self):
        body='\n'.join(self.parts+['</svg>'])
        ET.fromstring(body)
        (OUT/self.name).write_text(body,encoding='utf-8')


def coordinates():
    s=SVG('coordinate-frames-and-batch.svg','双屏坐标：截图、显示器局部与桌面全局',
          '原创双屏例子。左屏原点 (-2000, 0)，尺寸 2000×1200。截图 1000×600 的点 (500,300)，先换算成局部 (1000,600)，再加原点得到全局 (-1000,600)。缩放观察和批内新截图不改变本批开始前的完整截图参照。',1190)
    s.header('卷 03 · COMPUTER USE / 原创学习图','坐标要经过缩放，再加上屏幕原点','同一个目标，在截图坐标、显示器局部坐标和桌面全局坐标中有不同的数值。')
    s.rect(60,180,1320,530,stroke=P['line'])
    s.text(90,222,'桌面全局坐标：两块屏幕并排',24,weight=650)
    s.badge(1035,198,310,'尺寸为教学例子，非设备实测',size=17)
    # Both screens use the same geometric scale; x=0 is their boundary.
    for x,label in [(90,'左屏 · 2000 × 1200'),(430,'右屏 · 2000 × 1200')]:
        s.rect(x,258,330,198,P['sagelight'] if x==90 else P['quiet'],P['line'],rx=8)
        s.text(x+165,291,label,19,P['muted'],500,'middle')
        s.line(x+165,456,x+165,474,P['muted'],3)
        s.line(x+125,474,x+205,474,P['muted'],3)
    s.line(420,245,420,485,P['rust'],2)
    s.text(90,248,'(-2000, 0)',18,P['muted'],mono=True)
    s.text(435,248,'(0, 0)',18,P['rust'],mono=True)
    s.text(770,491,'x 向右；y 向下',18,P['muted'],anchor='end')
    s.line(90,258,255,357,P['sage'],2)
    s.circle(255,357,8,P['sage'])
    s.rect(115,382,280,44,P['paper'],rx=10)
    s.text(255,412,'全局点 (-1000, 600)',21,P['sage'],600,'middle')
    # Original screenshot has half the display dimensions.
    s.text(880,249,'左屏返回的完整截图 F0',22,weight=600)
    s.rect(880,270,400,240,P['rustlight'],P['line'],rx=8)
    s.line(1080,270,1080,510,P['line'],1)
    s.line(880,390,1280,390,P['line'],1)
    s.circle(1080,390,8,P['rust'])
    s.text(1080,347,'1000 × 600',22,P['muted'],500,'middle')
    s.text(1080,441,'截图点 (500, 300)',22,P['rust'],600,'middle')
    s.path('M880 390 C820 390 820 357 784 357',P['muted'],2,'muted')
    s.text(816,325,'换算',18,P['muted'],anchor='middle')
    # Three explicit coordinate spaces, with exact arithmetic.
    boxes=[(90,'① 截图坐标','(500, 300)','frame：1000 × 600','rust'),
           (530,'② 显示器局部坐标','(1000, 600)','x × 2000/1000；y × 1200/600','sage'),
           (970,'③ 桌面全局坐标','(-1000, 600)','(1000, 600) + (-2000, 0)','sage')]
    for x,title,value,note,col in boxes:
        s.rect(x,542,380,130,P[col+'light'],rx=12)
        s.text(x+20,574,title,20,P['muted'],500)
        s.text(x+20,613,value,29,P[col],650)
        s.text(x+20,649,note,17,P['muted'])
    s.line(479,607,515,607,P['muted'],2,'muted')
    s.line(919,607,955,607,P['muted'],2,'muted')
    s.text(90,698,'实现顺序：按 frame 比例换算 → 四舍五入 → 加 origin → 夹到显示器最后一个像素。',18,P['muted'])
    # Fixed reference in a batch.
    s.rect(60,740,1320,350,stroke=P['line'])
    s.text(90,785,'缩放只改变观察；本批动作共用开始前的 F0',25,weight=650)
    s.rect(90,836,230,138,P['rustlight'],P['line'],rx=8)
    s.text(205,866,'批开始前的完整 F0',18,P['rust'],600,'middle')
    s.rect(158,884,66,49,P['paper'],P['rust'],rx=2)
    s.circle(191,908,5,P['rust'])
    s.text(205,962,'1000 × 600',18,P['muted'],anchor='middle')
    s.line(320,908,366,908,P['muted'],2,'muted')
    s.rect(380,836,200,138,P['quiet'],P['line'],rx=8)
    s.circle(480,894,13,P['rust'])
    s.text(480,930,'Zoom 局部放大',19,P['ink'],500,'middle')
    s.text(480,960,'只用来观察',18,P['muted'],anchor='middle')
    s.text(90,1013,'放大图不成为后续 click 的局部坐标系。',20,P['muted'])
    s.path('M205 824 V810 H1270 V833',P['sage'],3)
    s.text(878,802,'本批的坐标 / region 一直参照 F0',19,P['sage'],600,'middle')
    for x,title,sub,color in [(645,'1 · click','参照 F0','sage'),(890,'2 · screenshot','得到 F1','rust'),(1135,'3 · click','仍参照 F0','sage')]:
        s.rect(x,846,190,96,P[color+'light'],rx=12)
        s.text(x+95,884,title,21,P[color],600,'middle')
        s.text(x+95,920,sub,20,P['muted'],400,'middle')
    s.line(843,894,880,894,P['muted'],2,'muted')
    s.line(1088,894,1125,894,P['muted'],2,'muted')
    s.lines(645,988,['F1 可作为批结果返回，','但不替换这一批共用的 F0 参照。'],20,P['muted'],31)
    s.text(90,1067,'注意：固定坐标参照不代表目标不会移动；batch 仍顺序执行，已发生的动作不自动回滚。',19,P['muted'])
    s.text(60,1143,'读图范围：正常的有截图 frame 分支；normalized 与无前图回落另见正文。原点与尺寸属于截图 sidecar。',18,P['muted'])
    s.save()

PAYLOAD={'type':'content_block_delta','index':0,'delta':{'type':'text_delta','text':'你好'}}
DATA=json.dumps(PAYLOAD,ensure_ascii=False,separators=(',',':'))
WIRE=('event: content_block_delta\r\ndata: '+DATA+'\r\n\r\n').encode('utf-8')
CUT1=WIRE.index('你'.encode())+2
CUT2=len(WIRE)-3
CHUNKS=[WIRE[:CUT1],WIRE[CUT1:CUT2],WIRE[CUT2:]]


def stream():
    s=SVG('utf8-sse-to-render.svg','从 UTF-8 字节到 SSE 事件、内容块与界面绘制',
          '原创文本你好用 UTF-8 编码。第一块在你的 E4 BD 与 A0 之间切开，第二块在数据行 CR 与 LF 之间切开。行解析保留状态，空行闭帧。JSON 中 index 为零，text_delta 追加你好到已打开的文本块，再经合并交付与绘制显示。',1390)
    s.header('卷 04 → 卷 08 · STREAMING / 原创学习图','从被切开的汉字，到一条可见回复','网络 chunk、SSE 事件、内容块状态和界面绘制，各有自己的边界。')
    s.rect(60,180,1320,413,stroke=P['line'])
    s.text(90,222,'① 原始输入：一帧 SSE，文本是「你好」',25,weight=650)
    s.text(90,255,'本图自造测试数据；CR = 0D，LF = 0A；方括号显示换行字节，不是正文字符。',19,P['muted'])
    s.rect(90,278,1260,100,P['quiet'],rx=10)
    s.text(110,312,'event: content_block_delta [CR][LF]',20,mono=True)
    s.text(110,344,'data: '+DATA+' [CR][LF]',19,mono=True)
    s.text(110,369,'[CR][LF]  ← 空行结束这一帧',18,P['rust'],mono=True)
    # Widths intentionally differ; chunks are neither equal characters nor tokens.
    cards=[(90,410,420,'chunk 1',f'{len(CHUNKS[0])} 字节','… 22 E4 BD','行前缀省略；“你”只到前 2 字节'),
           (530,410,540,'chunk 2',f'{len(CHUNKS[1])} 字节','A0 E5 A5 BD 22 7D 7D 0D','补齐“你”与“好”，停在数据行 CR'),
           (1090,410,260,'chunk 3',f'{len(CHUNKS[2])} 字节','0A 0D 0A','LF + 空行 CRLF')]
    for x,y,w,label,count,raw,note in cards:
        s.rect(x,y,w,130,P['rustlight'] if x!=1090 else P['sagelight'],rx=12)
        s.text(x+18,y+30,label,21,weight=650)
        s.text(x+w-18,y+30,count,17,P['muted'],anchor='end')
        s.text(x+18,y+71,raw,22,P['rust'] if x!=1090 else P['sage'],600,mono=True)
        s.text(x+18,y+108,note,17,P['muted'])
    s.text(90,574,'“你” = E4 BD A0；“好” = E5 A5 BD。chunk 1 / 2 切开一个汉字，chunk 2 / 3 切开 CRLF。',20,P['muted'])
    s.line(720,602,720,625,P['muted'],2,'muted')
    s.rect(60,636,1320,236,stroke=P['line'])
    s.text(90,679,'② 先还原行与帧，再解析 JSON',25,weight=650)
    s.lines(90,722,['保留不完整行与 CRLF 状态。','完整 data 行才解码并处理字段。','数据行结尾只结束行；随后空行交付帧。'],20,P['muted'],32)
    s.line(594,760,635,760,P['muted'],2,'muted')
    s.rect(655,707,320,132,P['sagelight'],rx=10)
    s.text(675,739,'完整 SSE frame',21,P['sage'],650)
    s.text(675,775,'event: content_block_delta',16,mono=True)
    s.text(675,811,'data: 完整 JSON 字符串',19,P['muted'])
    s.line(983,760,1022,760,P['muted'],2,'muted')
    s.rect(1042,707,308,132,P['quiet'],rx=10)
    s.text(1062,739,'JSON.parse(data)',20,weight=650,mono=True)
    s.text(1062,775,'index: 0',20,P['muted'],mono=True)
    s.text(1062,811,'text_delta: “你好”',20,P['rust'])
    s.line(720,881,720,904,P['muted'],2,'muted')
    s.rect(60,915,1320,171,stroke=P['line'])
    s.text(90,958,'③ reducer：按 index 更新已打开的内容块',25,weight=650)
    s.text(90,998,'此前已收到 index = 0 的 content_block_start；本例只演示 text_delta 的追加语义。',19,P['muted'])
    s.badge(90,1021,390,'blocks[0] = { text: "" }',size=20)
    s.text(526,1046,'+ “你好”',25,P['rust'],600)
    s.line(674,1038,730,1038,P['muted'],2,'muted')
    s.badge(765,1021,555,'blocks[0] = { type: "text", text: "你好" }',size=19)
    s.line(720,1095,720,1118,P['muted'],2,'muted')
    s.rect(60,1129,1320,166,stroke=P['line'])
    s.text(90,1172,'④ 交付最新快照，然后由界面绘制',25,weight=650)
    for x,w,title,sub in [(90,340,'内容块最新状态','同一批可已消费多帧'),(500,390,'合并交付 / 边界 flush','classic：微任务合并，smooth=false')]:
        s.rect(x,1193,w,77,P['sagelight'],rx=10)
        s.text(x+18,1225,title,22,P['sage'],600)
        s.text(x+18,1254,sub,17,P['muted'])
    s.line(442,1231,484,1231,P['muted'],2,'muted')
    s.line(903,1231,945,1231,P['muted'],2,'muted')
    s.rect(965,1193,385,77,P['rustlight'],rx=10)
    s.text(989,1243,'你好',30,P['rust'],650)
    s.text(1105,1235,'提交与 paint 在后',20,P['muted'])
    s.text(60,1343,'没有一一对应：一次 chunk ≠ 一帧 event ≠ 一个 token ≠ 一次 paint。此图不推断服务端 token 生成时刻。',19,P['muted'])
    s.save()

EDGES=[('Root','H1'),('H1','A1'),('H1','A1b'),('A1','H2'),('A1','H2b'),('H2','A2'),('H2b','A2b'),('A1b','H3')]
PATH_A=['Root','H1','A1','H2b','A2b']
PATH_B=['Root','H1','A1b','H3']


def tree():
    s=SVG('message-tree-visible-paths.svg','同一棵消息树上的编辑分支与重试分支',
          '左右绘制相同消息树。左边选中 Root H1 A1 H2b A2b，右边选中 Root H1 A1b H3。下方分别显示对应 transcript。编辑 human 在原父节点下新建 human 兄弟及 assistant，重试 assistant 在同一 human 下新建 assistant 兄弟，旧分支均保留。',1250)
    s.header('卷 08 · CONVERSATION TREE / 原创学习图','一棵消息树，两条可见历史','编辑与重试会增加兄弟节点；显示哪条历史，由各层选中的子节点共同决定。')
    pos={'Root':(315,98),'H1':(315,180),'A1':(210,274),'A1b':(495,274),
         'H2':(115,376),'H2b':(315,376),'H3':(495,376),'A2':(115,478),'A2b':(315,478)}
    for ox,title,sub,selected,col,trans in [
        (60,'A · 选择编辑分支的叶子 A2b','H2b 与 H2 是 A1 下的 human 兄弟',PATH_A,'rust','H1 → A1 → H2b → A2b'),
        (740,'B · 选择重试分支中的 H3','A1b 与 A1 是 H1 下的 assistant 兄弟',PATH_B,'sage','H1 → A1b → H3')]:
        oy=181
        s.rect(ox,oy,640,655,stroke=P['line'])
        s.text(ox+25,oy+40,title,23,P[col],650)
        s.text(ox+25,oy+73,sub,18,P['muted'])
        chosen=set(zip(selected,selected[1:]))
        # Tree origin sits below the explanatory line.
        offset=38
        for a,b in sorted(EDGES, key=lambda edge: edge in chosen):
            ax,ay=pos[a];bx,by=pos[b]
            active=(a,b) in chosen
            s.path(f'M{ox+ax} {oy+ay+offset+23} V{oy+(ay+by)/2+offset} H{ox+bx} V{oy+by+offset-23}',P[col] if active else P['line'],5 if active else 2)
        for node,(x,y) in pos.items():
            active=node in selected
            w=122 if node=='Root' else 106
            s.rect(ox+x-w/2,oy+y+offset-23,w,46,P[col] if active else P['quiet'],rx=10)
            s.text(ox+x,oy+y+offset+8,'Root' if node=='Root' else node,23,P['paper'] if active else P['muted'],650 if active else 400,'middle')
        s.rect(ox+25,oy+566,590,64,P[col+'light'],rx=10)
        s.text(ox+43,oy+590,'可见 transcript（不含 Root）',17,P['muted'])
        s.text(ox+43,oy+619,trans,24,P[col],600)
    s.line(85,869,130,869,P['rust'],5)
    s.text(144,877,'粗线 + 实心节点：选中路径',19,P['muted'])
    s.line(535,869,580,869,P['line'],2)
    s.text(594,877,'浅线 + 浅底节点：保留的其他分支',19,P['muted'])
    s.text(1375,877,'H = human；A = assistant',18,P['muted'],anchor='end')
    # Small structural operations; fixed parent and new siblings are explicit.
    for x,title in [(60,'编辑 human：复用原 parent，新增 H + A'),(740,'重试 assistant：同一 H 下新增 A')]:
        s.rect(x,912,640,244,stroke=P['line'])
        s.text(x+25,951,title,22,weight=650)
    def node(x,y,label,col=None,w=100):
        s.rect(x,y,w,44,P[col+'light'] if col else P['quiet'],rx=9)
        s.text(x+w/2,y+29,label,21,P[col] if col else P['muted'],600,'middle')
    # edit
    node(90,1020,'A1',w=100)
    for yy,target,col in [(986,'H2',None),(1061,'H2b','rust')]:
        s.path(f'M190 1042 H224 V{yy+22} H255',P['rust'] if col else P['line'],3 if col else 2)
        node(255,yy,target,col,105)
        s.line(360,yy+22,405,yy+22,P['rust'] if col else P['line'],3 if col else 2)
        node(405,yy,'A2b' if col else 'A2',col,105)
        s.text(530,yy+29,'新增' if col else '保留',18,P['rust'] if col else P['muted'])
    s.text(90,1134,'H2b.parent = H2.parent = A1',18,P['muted'],mono=True)
    # retry
    node(770,1020,'H1',w=100)
    for yy,target,col in [(986,'A1',None),(1061,'A1b','sage')]:
        s.path(f'M870 1042 H915 V{yy+22} H960',P['sage'] if col else P['line'],3 if col else 2)
        node(960,yy,target,col,110)
        s.text(1100,yy+29,'新增回复版本' if col else '保留原回复及后代',18,P['sage'] if col else P['muted'])
    s.text(770,1134,'A1b.parent = A1.parent = H1',18,P['muted'],mono=True)
    s.text(60,1202,'连线表示 parent → child；同一节点只有一个 parent。切换分支只改变选中路径，不必新增或删除节点。',19,P['muted'])
    s.save()


def parse_sse_chunks(chunks):
    """Original byte-buffer model: CR, LF, and split CRLF all end lines correctly."""
    line=bytearray(); frame={}; events=[]; skip_lf=False
    def emit_line():
        nonlocal frame
        t=line.decode('utf-8'); line.clear()
        if not t:
            if frame: events.append(frame)
            frame={}
            return
        key,_,val=t.partition(':')
        if val.startswith(' '): val=val[1:]
        if key=='data': frame[key]=frame.get(key,'')+('\n' if key in frame else '')+val
        elif key=='event': frame[key]=val
    for chunk in chunks:
        for byte in chunk:
            if skip_lf:
                skip_lf=False
                if byte==10: continue
            if byte in (10,13):
                emit_line()
                skip_lf=byte==13
            else: line.append(byte)
    return events


def verify():
    assert '你'.encode()==bytes.fromhex('E4 BD A0')
    assert '好'.encode()==bytes.fromhex('E5 A5 BD')
    assert CHUNKS[0].endswith(bytes.fromhex('E4 BD'))
    assert CHUNKS[1]==bytes.fromhex('A0 E5 A5 BD 22 7D 7D 0D')
    assert CHUNKS[2]==bytes.fromhex('0A 0D 0A')
    assert b''.join(CHUNKS)==WIRE
    frame=parse_sse_chunks(CHUNKS)
    assert parse_sse_chunks(CHUNKS[:1])==[]
    assert parse_sse_chunks(CHUNKS[:2])==[]
    blocks=[{'type':'text','text':''}]
    blocks[PAYLOAD['index']]['text'] += PAYLOAD['delta']['text']
    assert blocks==[{'type':'text','text':'你好'}]
    assert len(frame)==1 and json.loads(frame[0]['data'])==PAYLOAD
    # Every possible single cut, plus one-byte chunks, gives the same SSE frame.
    for i in range(len(WIRE)+1): assert parse_sse_chunks([WIRE[:i],WIRE[i:]])==frame
    assert parse_sse_chunks([bytes([b]) for b in WIRE])==frame
    local=(math.floor(500*2000/1000+.5),math.floor(300*1200/600+.5))
    global_point=(max(-2000,min(-1,local[0]-2000)),max(0,min(1199,local[1])))
    assert local==(1000,600) and global_point==(-1000,600)
    parents=dict((b,a) for a,b in EDGES)
    assert len(parents)==len(EDGES)
    children={}
    for a,b in EDGES: children.setdefault(a,[]).append(b)
    for path in [PATH_A,PATH_B]:
        assert all(parents[b]==a for a,b in zip(path,path[1:]))
        selected={}
        leaf=path[-1]
        while leaf in parents:
            parent=parents[leaf]
            selected[parent]=children[parent].index(leaf)
            leaf=parent
        visible=['Root']
        while visible[-1] in selected:
            current=visible[-1]
            visible.append(children[current][selected[current]])
        assert visible==path
    results={'coordinate':{'frame':[1000,600],'display':[2000,1200],'origin':[-2000,0],'input':[500,300],'local':local,'global':global_point},
        'sse':{'wire_utf8':WIRE.decode(),'byte_length':len(WIRE),'chunk_lengths':list(map(len,CHUNKS)),
               'cut_offsets':[CUT1,CUT2],'chunk2_hex':CHUNKS[1].hex(' ').upper(),'chunk3_hex':CHUNKS[2].hex(' ').upper(),
               'all_single_cut_cases':len(WIRE)+1,'one_byte_chunks':'pass','reconstructed_frame':frame[0]},
        'tree':{'edges':EDGES,'path_A':PATH_A,'path_B':PATH_B,'single_parent':'pass'},
        'svg_validation':'all files parse as XML; no external assets, fonts or logos bundled'}
    (OUT/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':
    coordinates(); stream(); tree(); verify()
