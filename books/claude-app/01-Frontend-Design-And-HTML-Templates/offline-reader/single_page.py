#!/usr/bin/env python3
"""Compose only generated safe preview HTML. Never parse original Markdown as HTML."""
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from svg_check import validate

ALLOWED_TAGS = set('html head meta title body header nav a span main p h1 h2 h3 h4 h5 h6 aside details summary div code pre table thead tbody tr th td strong em del br hr ul ol li img footer link blockquote'.split())
VOID = {'meta','link','img','br','hr'}
def esc(value): return html.escape(str(value), quote=True)

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=set();self.headings=[];self.heading=None;self.code_depth=0;self.code=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids: raise ValueError('duplicate generated ID')
            self.ids.add(attrs['id'])
        if tag in {'h2','h3'} and 'id' in attrs:
            self.heading={'id':attrs['id'],'text':''}
        if tag=='pre' and attrs.get('aria-label')=='原始文件源码':self.code_depth=1
        elif self.code_depth:self.code_depth+=1
    def handle_endtag(self,tag):
        if tag in {'h2','h3'} and self.heading:
            self.headings.append(self.heading);self.heading=None
        if self.code_depth:self.code_depth-=1
    def handle_data(self,data):
        if self.heading:self.heading['text']+=data
        if self.code_depth:self.code.append(data)

class Compose(HTMLParser):
    def __init__(self,css,csp,data_image,links,appendix):
        super().__init__(convert_charrefs=True)
        self.css=css;self.csp=csp;self.data_image=data_image;self.links=links;self.appendix=appendix
        self.output=[];self.styles=0;self.images=0;self.policies=0;self.mains=0
    def handle_decl(self,decl):
        if decl.lower()!='doctype html':raise ValueError('unexpected declaration')
        self.output.append('<!doctype html>')
    def handle_starttag(self,tag,attrs):
        if tag not in ALLOWED_TAGS:raise ValueError('unexpected generated element: '+tag)
        attrs=dict(attrs)
        for key in attrs:
            if key.startswith('on') or key in {'style','srcdoc','srcset','formaction','ping'}:raise ValueError('unexpected active attribute')
        if tag=='meta' and attrs.get('http-equiv','').lower()=='content-security-policy':
            attrs['content']=self.csp;self.policies+=1
        elif tag=='meta' and 'http-equiv' in attrs:raise ValueError('unexpected http-equiv')
        if tag=='link':
            if attrs!={'rel':'stylesheet','href':'reader.css'}:raise ValueError('unexpected stylesheet')
            self.output.append('<style>'+self.css+'</style>');self.styles+=1;return
        if 'src' in attrs:
            if tag!='img' or attrs['src']!=self.links['image']:raise ValueError('unexpected generated resource')
            attrs['src']=self.data_image;self.images+=1
        if 'href' in attrs:
            if tag!='a':raise ValueError('unexpected resource link')
            dest=attrs['href'];split=urlsplit(dest)
            if split.scheme:
                if split.scheme not in {'http','https','mailto'} or split.username or split.password:raise ValueError('unexpected external link')
            elif split.netloc:raise ValueError('protocol-relative link')
            elif not split.path or split.path=='index.html':attrs['href']='#'+(split.fragment or 'main')
            elif dest in self.links:attrs['href']='#'+self.links[dest]
            else:raise ValueError('unmapped local navigation: '+dest)
        self.output.append('<'+tag+''.join(' '+key+('="'+esc(value)+'"' if value is not None else '') for key,value in attrs.items())+'>')
    def handle_endtag(self,tag):
        if tag not in ALLOWED_TAGS:raise ValueError('unexpected closing element')
        if tag=='main':self.output.append(self.appendix);self.mains+=1
        if tag not in VOID:self.output.append('</'+tag+'>')
    def handle_data(self,data):self.output.append(esc(data))
    def handle_comment(self,data):pass
    def handle_pi(self,data):raise ValueError('processing instruction')

def compose(site,options):
    entry=options['entry'];image=options['image']
    # This is intentionally not an arbitrary Markdown/image renderer.
    if entry!='02-Illustrated-Deep-Dive-Book/05-Context-And-File-Pipeline/worked-case.md' or image!='assets/figures/context-budget-ledger.svg':
        raise ValueError('only the fixed two-input sample is supported')
    manifest=json.loads((site/'build-manifest.json').read_text())
    if sorted(i['path'] for i in manifest['inputs'])!=sorted([entry,image]) or manifest['images']!=1:
        raise ValueError('unexpected preview inputs')
    index=(site/'index.html').read_text(encoding='utf-8')
    # HTML parsing normalizes CRLF/CR to LF before CSP hashes are checked.
    # Hash and emit the same normalized stylesheet, including on Windows checkouts.
    css=(site/'reader.css').read_bytes().decode('utf-8').replace('\r\n','\n').replace('\r','\n')
    if re.search(r'</style|@import|url\s*\(',css,re.I):raise ValueError('stylesheet is not self-contained')
    css_hash=base64.b64encode(hashlib.sha256(css.encode('utf-8')).digest()).decode('ascii')
    csp="default-src 'none'; script-src 'none'; style-src 'sha256-"+css_hash+"'; img-src data:; font-src 'none'; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'"
    serialized=validate((site/'media'/image).read_bytes()).encode('utf-8')
    data_image='data:image/svg+xml;base64,'+base64.b64encode(serialized).decode('ascii')
    scan=Inspect();scan.feed(index)
    def allocate(base):
        candidate=base;number=0
        while candidate in scan.ids:number+=1;candidate=base+'-'+str(number)
        scan.ids.add(candidate);return candidate
    contents_id=allocate('reader-single-contents');notes_id=allocate('reader-single-notes')
    source_id=allocate('reader-single-source');figure_id=allocate('reader-single-figure')
    source=Inspect();source.feed((site/'source'/(entry+'.html')).read_text(encoding='utf-8'))
    svgsource=Inspect();svgsource.feed((site/'source'/(image+'.html')).read_text(encoding='utf-8'))
    provenance={'mode':'self-contained-fixed-preview','source':manifest,'singleCompilerInputs':options['compilerInputs'],'styleSha256Base64':css_hash,'embeddedSvgSha256':hashlib.sha256(serialized).hexdigest()}
    appendix=(f'<section id="{contents_id}"><h2>样章目录</h2><nav aria-label="同页样章目录">'
      +''.join(f'<p><a href="#{esc(h["id"])}">{esc(h["text"])}</a></p>' for h in scan.headings)
      +f'</nav></section><section id="{notes_id}"><h2>单文件阅读说明</h2>'
      +'<p>这是固定附件预算案例的排版样章。CSS 与已验证 SVG 都包含在本文件内，页面不加载脚本、字体或网络资源。原文中保留的外部来源，仅在主动点击时打开。</p>'
      +'<p>目录、阅读说明和原文均使用同页锚点。展开下面的原文区可核对内容；浏览器查找、缩放、打印和代码横向滚动仍可使用。完整书请运行主构建器。</p>'
      +f'</section><section id="{source_id}"><h2>原始 Markdown</h2><details><summary>展开只读原文</summary>'
      +'<div class="code-block"><pre tabindex="0" aria-label="样章原始 Markdown"><code>'+esc(''.join(source.code))+'</code></pre></div></details></section>'
      +f'<section id="{figure_id}"><h2>原始图源</h2><details><summary>展开只读 SVG 源码</summary>'
      +'<div class="code-block"><pre tabindex="0" aria-label="样章原始 SVG"><code>'+esc(''.join(svgsource.code))+'</code></pre></div></details></section>'
      +'<details><summary>查看生成记录</summary><div class="code-block"><pre tabindex="0" aria-label="单文件生成记录"><code>'
      +esc(json.dumps(provenance,ensure_ascii=False,sort_keys=True,indent=2))+'</code></pre></div></details>')
    links={'contents.html':contents_id,'about.html':notes_id,'source/'+entry+'.html':source_id,'source/'+image+'.html':figure_id,'image':'media/'+image}
    renderer=Compose(css,csp,data_image,links,appendix);renderer.feed(index);renderer.close()
    if (renderer.styles,renderer.images,renderer.policies,renderer.mains)!=(1,1,1,1):raise ValueError('unexpected page resource/section counts')
    return ''.join(renderer.output)

if __name__=='__main__':
    print(compose(Path(sys.argv[1]),json.load(sys.stdin)),end='')
