#!/usr/bin/env python3
"""Generate original schematic figures from selected, attributed token facts."""
from pathlib import Path
import json, html
BASE=Path(__file__).resolve().parents[2]
D=json.loads((BASE/'04-Extracted-Core-Code-And-Scripts/evidence/data/design-token-summary.json').read_text())
OUT=BASE/'assets/figures';OUT.mkdir(parents=True,exist_ok=True)
def text(x,y,s,size=16,fill='#20201f',weight=400):
 return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}">{html.escape(s)}</text>'
def rect(x,y,w,h,fill,rx=12,stroke='none'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
def wrap(body,w,h,title):
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{html.escape(title)}</title><style>text{{font-family:system-ui,"Noto Sans CJK SC","Microsoft YaHei",sans-serif}}</style>'+''.join(body)+'</svg>'
body=[rect(0,0,1160,630,'#eeede8',0),text(40,48,'表面层级：同一角色，两套主题映射',26,weight=650),text(40,80,'官方 Linux 包 2.37337.1 中选定 CDS 声明的解析值；非运行时截图',15,fill='#52514e')]
for j,mode in enumerate(['cds_light','cds_dark']):
 c=D['selected_tokens']['colors'][mode];x=40+j*550
 primary=c['--cds-text-primary']['resolved_srgb'];secondary=c['--cds-text-secondary']['resolved_srgb']
 body += [rect(x,110,530,440,c['--cds-surface-0']['resolved_srgb'],20),text(x+24,148,'浅色语义配置' if j==0 else '深色语义配置',21,primary,600)]
 for i in range(4):
  name=f'--cds-surface-{i}';v=c[name]['resolved_srgb'];y=174+i*77
  body += [rect(x+24,y,482,61,v,10,'#97958c' if j==0 else '#52514e'),text(x+40,y+25,name,15,primary,500),text(x+40,y+48,v,14,secondary)]
 body += [text(x+24,522,'同色不等于同层：浮层还依赖边界、阴影与位置。',14,secondary)]
body += [text(40,589,'本图是原创示意。值的出处、选择器和字节位置见 data/design-token-summary.json。',15),text(40,613,'不要把这里的 surface-0 自动等同于旧版 bg-100，或套到全部桌面窗口。',15)]
(OUT/'surface-mappings.svg').write_text(wrap(body,1160,630,'CDS 浅色与深色表面令牌对照'))
body=[rect(0,0,1160,500,'#f9f9f7',0),text(40,48,'先分职责，再选颜色',27,weight=650),text(40,80,'从色阶到状态的设计方法；下面的组件组合是原创教学示意',15,fill='#52514e')]
labels=[('原始色阶','中性灰 / 品牌 / 状态色','事实：包内有多组色阶'),('语义角色','画布 / 文字 / 边界 / 强调','决策：这层承担什么职责'),('组件结构','输入 / 附件 / 工具 / 提交','决策：如何组合与对齐'),('交互状态','默认 / 聚焦 / 忙碌 / 错误','决策：变化后如何辨识')]
for i,(a,b,c) in enumerate(labels):
 x=40+i*275
 body += [rect(x,122,250,166,'#ffffff',16,'#d7d5cd'),text(x+18,155,str(i+1).zfill(2),15,'#8f4831',600),text(x+18,188,a,23,weight=600),text(x+18,223,b,14),text(x+18,260,c,13,fill='#52514e')]
 if i<3:body+=[text(x+253,207,'→',21,fill='#52514e')]
body += [rect(40,325,1080,128,'#eeede8',14),text(62,360,'一个橙色按钮，不能定义一套设计系统。',22,weight=600),text(62,395,'先确定按钮的任务、状态和层级，再决定填色、字号、触达范围与反馈。',17),text(62,426,'复用这些关系；把自己的适配值与观察到的产品值分开记录。',16,fill='#52514e')]
(OUT/'role-to-state.svg').write_text(wrap(body,1160,500,'色阶、语义、组件、状态四层关系'))
print('Wrote 2 original schematic SVG figures.')
