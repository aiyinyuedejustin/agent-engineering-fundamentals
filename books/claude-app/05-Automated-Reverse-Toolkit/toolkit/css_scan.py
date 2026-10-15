"""Original byte scanner adapted from the sibling color-tools extractor.

Reuse is intentionally limited to the scanner, avoiding a second color evaluator.
This is not a complete CSS grammar or a cascade/computed-style engine.
"""
import re

def decode(s): return s.encode('latin1').decode('utf-8')

def uncomment(s):
    """Remove comments without changing quoted selector contents."""
    out=[]; i=0; quote=None
    while i<len(s):
        if quote:
            out.append(s[i])
            if s[i]=='\\' and i+1<len(s): out.append(s[i+1]); i+=2; continue
            if s[i]==quote: quote=None
        elif s[i] in "\"'": quote=s[i]; out.append(s[i])
        elif s.startswith('/*',i):
            end=s.find('*/',i+2); i=len(s) if end<0 else end+2; continue
        else: out.append(s[i])
        i+=1
    return ''.join(out)

def scan(data):
    """Return flattened blocks and declarations while retaining exact byte ranges."""
    s=data.decode('latin1'); n=len(s); nodes=[]; stack=[]; i=0; seg=0; par=bra=0; quote=None; unclosed_comment=False; unexpected_close=0; declarations=0
    def decl(a,b):
        nonlocal declarations
        raw=s[a:b]; leading=0
        while True:
            trim=len(raw)-len(raw.lstrip()); leading+=trim; raw=raw.lstrip()
            comment=re.match(r'^/\*.*?\*/',raw,re.S)
            if not comment: break
            leading+=comment.end(); raw=raw[comment.end():]
        raw=raw.rstrip()
        m=re.match(r'(-?[A-Za-z_][\w-]*|--[\w-]+)\s*:(.*)$',raw,re.S)
        if m and stack:
            declarations+=1
            if declarations>400000: raise ValueError('CSS declaration bound exceeded')
            val=m[2].strip(); nodes[stack[-1]]['decl'].append({'name':m[1],'value':decode(val),'start':a+leading,'end':b})
    while i<n:
        c=s[i]
        if quote:
            if c=='\\': i+=2; continue
            if c==quote: quote=None
            i+=1; continue
        if s.startswith('/*',i):
            end=s.find('*/',i+2); unclosed_comment=end<0; i=n if end<0 else end+2; continue
        if c in "\"'": quote=c; i+=1; continue
        if c=='\\': i+=2; continue
        if c=='(': par+=1
        elif c==')':
            if not par: unexpected_close+=1
            par=max(0,par-1)
        elif c=='[': bra+=1
        elif c==']':
            if not bra: unexpected_close+=1
            bra=max(0,bra-1)
        elif par==0 and bra==0:
            if c=='{':
                if len(nodes)>=200000 or len(stack)>=64: raise ValueError('CSS structure bound exceeded')
                raw=s[seg:i]; start=seg+len(raw)-len(raw.lstrip()); pre=uncomment(raw).strip()
                node={'prelude':decode(pre),'start':start,'body_start':i+1,'end':None,'parent':stack[-1] if stack else None,'decl':[]}
                nodes.append(node); stack.append(len(nodes)-1); seg=i+1
            elif c==';': decl(seg,i); seg=i+1
            elif c=='}':
                decl(seg,i)
                if stack: nodes[stack.pop()]['end']=i+1
                else: unexpected_close+=1
                seg=i+1
        i+=1
    return nodes, {'unclosed_blocks':len(stack),'unclosed_quote':quote,'unclosed_parens':par,'unclosed_brackets':bra,'unclosed_comment':unclosed_comment,'unexpected_close':unexpected_close}

def contexts(nodes,i):
    out=[]; p=nodes[i]['parent']
    while p is not None:
        out.append(nodes[p]['prelude']); p=nodes[p]['parent']
    return list(reversed(out))

