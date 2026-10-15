"""Original vector figures for the three worked cases; writes original SVGs to the requested output directory."""
from html import escape
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[2] / 'assets' / 'figures')
OUT = parser.parse_args().out
OUT.mkdir(parents=True, exist_ok=True)
INK = '#252a30'; MUTED = '#58616a'; BG = '#f7f5ef'
BLUE = '#dbeaf8'; GREEN = '#dcece0'; RED = '#f7e0d8'; LINE = '#c7cbc9'


def text(x, y, value, size=18, fill=INK, weight='400'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{escape(value)}</text>'


def rect(x, y, w, h, fill='#fff', stroke=LINE, r=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'


def save(name, title, subtitle, body, height):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="{height}" viewBox="0 0 1120 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>
<style>text {{ font-family: 'Noto Sans CJK SC', 'PingFang SC', 'Microsoft YaHei', sans-serif; }}</style>
<rect width="1120" height="{height}" fill="{BG}"/>
{text(36, 48, title, 28, weight='700')}
{text(36, 80, subtitle, 16, MUTED)}
{''.join(body)}
{text(36, height-22, '原创教学模型 · 合成事件与数值 · 不表示产品的真实运行测量', 14, MUTED)}
</svg>'''
    (OUT / name).write_text(svg)


body = [rect(36, 104, 1048, 44, '#e9e6dd')]
for x, label in [(50, '事件次序'), (405, '当前代次'), (530, '会话状态'), (745, '进程'), (855, '结果归属')]:
    body.append(text(x, 134, label, 17, weight='700'))
rows = [
 ('1  A 开始，排队 message-A', '1', 'initializing', '无', 'A 的票据：1', BLUE),
 ('2  用户按 Stop', '2', 'idle', '无', '旧票据失效', RED),
 ('3  B 开始，排队 message-B', '3', 'initializing', '无', 'B 的票据：3', BLUE),
 ('4  A 初始化成功，晚到', '3', 'initializing', '无', '拒绝接管', RED),
 ('5  B 初始化成功', '3', 'running', '有', '接管当前会话', GREEN),
 ('6  注入 A 的旧 result', '3', 'running', '有', 'stale，不结算 B', RED),
 ('7  B 的 result 成功', '3', 'idle', '有', '回合结束，可保暖', GREEN),
]
for i, row in enumerate(rows):
    y = 153 + i*54
    body.append(rect(36, y, 1048, 49, row[5], r=6))
    for x, value in zip([50, 430, 530, 752, 855], row[:5]):
        body.append(text(x, y+32, value, 17))
body += [rect(36, 548, 1048, 72, '#fff'), text(54, 578, '为什么只看状态会失败？', 18, weight='700'),
         text(54, 605, '第 4 行仍是 initializing，但它属于 B。状态相同，不能证明异步结果身份相同。', 17)]
save('loop-stop-restart-timeline.svg', 'Stop 之后，晚到的成功也必须失效', '七个确定性事件：代次保护的是结果归属，idle 与进程存活分开记录。', body, 670)

body = [text(36, 125, '总预算 12 字节；已有文本 ok = 2，附件 A / B 各为 6 个 UTF-8 字节。', 18)]
body += [rect(36, 146, 1048, 42, '#e9e6dd'), text(50, 175, '步骤', 17, weight='700'),
         text(390, 175, '账本占用（每格 1 字节）', 17, weight='700'), text(840, 175, 'U / R', 17, weight='700')]
rows = [('初始：已有 ok',2,0,'2 / 0'), ('A 预留 6 字节',2,6,'2 / 6'),
        ('B 也要 6：拒绝内联',2,6,'2 / 6'), ('A 取消：释放预留',2,0,'2 / 0'),
        ('B 重试：重新预留',2,6,'2 / 6'), ('B 提交：额度转移',8,0,'8 / 0')]
for i,(label, used, reserved, total) in enumerate(rows):
    y=198+i*58
    body.append(text(50,y+31,label,18))
    for j in range(12):
        fill = '#364b5b' if j<used else '#76a9d1' if j<used+reserved else '#fff'
        body.append(rect(390+j*32, y+4, 28, 31, fill, r=3))
    body.append(text(840,y+31,total,18))
body += [rect(36,566,1048,88,'#fff'), text(54,595,'两条独立不变量',18,weight='700'),
         text(54,621,'预算：已提交 U + 在途预留 R ≤ 12。归属：只接受当前草稿代次的完成回调。',17),
         text(54,646,'取消先释放预留；晚到回调再次检查代次。两者缺一，都会留下错误状态。',17)]
save('context-budget-ledger.svg','预算必须计算尚未完成的承诺','深色 = 已提交 U；蓝色 = 在途预留 R；空格 = 剩余额度。',body,704)

body=[]
for x, title, fill in [(36,'用户审查的调用',BLUE),(588,'重连后的候选调用',RED)]:
    body += [rect(x,112,496,334,fill), text(x+22,148,title,22,weight='700')]
fields=[('server','notes','notes'),('source','extension:sample','manual:sample'),('revision','1','2'),
        ('generation','1','2'),('tool','read_note','read_note'),('arguments','notes/meeting.txt','notes/meeting.txt')]
for i,(label,left,right) in enumerate(fields):
    y=192+i*39
    for x,value in [(36,left),(588,right)]:
        body += [text(x+22,y,label,17,MUTED),text(x+185,y,value,18,weight='600' if left!=right else '400')]
body += [rect(36,466,1048,56,'#fff'),text(54,501,'同一个显示名 ≠ 同一个服务绑定。模型重算绑定 + 参数摘要，不匹配则拒绝旧批准。',18),
         rect(36,544,504,96,GREEN),rect(564,544,520,96,'#fff'),
         text(56,578,'一次批准的消费条件',19,weight='700'),text(56,609,'当前策略允许 + 连接就绪 + 绑定与参数匹配',16),
         text(584,578,'这仍然没有证明什么？',19,weight='700'),text(584,609,'服务身份真实、OS 沙箱、远端资源授权。',16)]
save('mcp-tool-binding.svg','工具名称不能充当授权的全部身份','保守原创策略：配置来源、修订、连接代次或参数变化，都使本次旧批准失效。',body,690)
print('Wrote 3 original SVG figures.')
