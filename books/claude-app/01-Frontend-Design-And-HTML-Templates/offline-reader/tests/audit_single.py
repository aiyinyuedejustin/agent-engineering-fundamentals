#!/usr/bin/env python3
"""Audit self-contained preview resources, CSP hash, SVG and all local anchors."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import base64
import hashlib
import json
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from svg_check import validate

class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[];self.ids=set();self.links=[];self.styles=[];self.style=False;self.csp=[];self.images=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in {'script','iframe','frame','object','embed','base','link','svg','math','form','input','button','audio','video','source'}:self.errors.append('forbidden element: '+tag)
        if tag=='style':self.styles.append('');self.style=True
        if tag=='meta' and attrs.get('http-equiv','').lower()=='content-security-policy':self.csp.append(attrs.get('content',''))
        elif tag=='meta' and 'http-equiv' in attrs:self.errors.append('unexpected http-equiv')
        if 'id' in attrs:
            if attrs['id'] in self.ids:self.errors.append('duplicate ID: '+attrs['id'])
            self.ids.add(attrs['id'])
        for key,value in attrs.items():
            if key.startswith('on') or key in {'style','srcdoc','srcset','formaction','ping'}:self.errors.append('active attribute: '+key)
            if key=='src':
                if tag!='img' or not value.startswith('data:image/svg+xml;base64,'):self.errors.append('nonembedded image/resource')
                else:
                    try:validate(base64.b64decode(value.split(',',1)[1],validate=True));self.images+=1
                    except Exception as error:self.errors.append('unsafe embedded SVG: '+str(error))
            if key=='href':
                split=urlsplit(value)
                if tag!='a':self.errors.append('resource href')
                elif value.startswith('#'):self.links.append(unquote(value[1:]))
                elif split.scheme not in {'https','http','mailto'} or split.username or split.password:self.errors.append('nonfragment local navigation or unsafe URL')
    def handle_endtag(self,tag):
        if tag=='style':self.style=False
    def handle_data(self,data):
        if self.style:self.styles[-1]+=data
    def result(self):
        for target in self.links:
            if target not in self.ids:self.errors.append('missing same-page anchor: '+target)
        if len(self.styles)!=1 or len(self.csp)!=1:self.errors.append('one exact style and CSP required')
        else:
            digest=base64.b64encode(hashlib.sha256(self.styles[0].encode()).digest()).decode()
            expected={key:"'none'" for key in ['default-src','script-src','font-src','connect-src','object-src','frame-src','base-uri','form-action']}
            expected.update({'style-src':"'sha256-"+digest+"'",'img-src':'data:'})
            directives={p.strip().split(' ',1)[0]:p.strip().split(' ',1)[1] for p in self.csp[0].split(';') if p.strip()}
            if directives!=expected:self.errors.append('CSP is broader than exact CSS hash and data images')
            if re.search(r'@import|url\s*\(',self.styles[0],re.I):self.errors.append('CSS resource request')
        if self.images!=1:self.errors.append('exactly one embedded SVG required')
        return {'styles':len(self.styles),'embedded_images':self.images,'same_page_links':len(self.links),'errors':self.errors}

if __name__=='__main__':
    audit=Audit();audit.feed(Path(sys.argv[1]).read_text());result=audit.result()
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
