#!/usr/bin/env python3
"""Sample-bound static anchors for the file-task control-byte investigation.

Runs readelf/objdump on a private stable snapshot, never loads the input. The
assertions are selected evidence anchors, not a general alias/reachability proof.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

EXPECTED = 'c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6'
SIZE = 10026272
WINDOWS = {
 0x617860:0x6178c7, 0x6179f0:0x617a9b,
 0x619e80:0x619f10, 0x619f10:0x619f96,
 0x61b230:0x61b4d0, 0x61b4d0:0x61b72d,
 0x61c8f0:0x61d12d, 0x62d560:0x62d806,
 0x62ecd0:0x62f4d8, 0x709270:0x709286,
 0x778620:0x778638,
}
# Original, sparse semantic anchors. Full target disassembly is not embedded.
FACTS = {
 # root: P allocation, initialization, copy into T, callback/queue binding
 0x62ef85:('mov','edi,0x18'), 0x62ef8a:('call','98c598'),
 0x62ef99:('mov','[rax+0x8],0x1'), 0x62efa1:('mov','BYTE PTR [rax+0x10],0x0'),
 0x62efa5:('mov','[rsp+0x10],rax'), 0x62efb2:('mov','[rax],0x2'),
 0x62efec:('mov','[rsp+0x58],rax'), 0x62eff1:('mov','edi,0x58'),
 0x62f012:('movups','[rsp+0x58]'), 0x62f017:('movups','[r12+0x40],xmm0'),
 0x62f151:('lea','619f10'), 0x62f158:('lea','61b4d0'),
 0x62f162:('mov','r9,r12'), 0x62f165:('call','98d7e8'),
 0x62f1b0:('call','98d7f0'), 0x62f1b6:('test','eax,eax'), 0x62f1b8:('je','62f24d'),
 # root: Promise return, local reference release (not cancellation)
 0x62f251:('mov','rax,QWORD PTR [rsp+0xe0]'), 0x62f261:('mov','r12,QWORD PTR [rsp+0x10]'),
 0x62f284:('mov','[rsp+0x18],r12'), 0x62f28e:('mov','rbp,rax'),
 0x62f2a0:('dec','QWORD PTR [r12]'), 0x62f2a4:('mov','r12,0xffffffffffffffff'),
 0x62f2b5:('call','98d7c8'), 0x62f2bb:('jmp','62eef1'),
 0x62ef19:('mov','rax,rbp'), 0x62ef76:('cmp','r12,0xffffffffffffffff'),
 0x62ef80:('jmp','62ed8f'), 0x62eda0:('ret',),
 # beneath: same P, placed at T+0x50
 0x61cb40:('mov','edi,0x18'), 0x61cb45:('call','98c598'),
 0x61cb54:('mov','[rax+0x8],0x1'), 0x61cb5c:('mov','BYTE PTR [rax+0x10],0x0'),
 0x61cb60:('mov','[rsp+0x28],rax'), 0x61cb96:('mov','[rax],0x2'),
 0x61cbc2:('mov','[rsp+0x80],rax'), 0x61cbca:('mov','edi,0x68'),
 0x61cbed:('movaps','[rsp+0x80]'), 0x61cbf5:('movups','[r13+0x50],xmm0'),
 0x61cd99:('lea','619e80'), 0x61cda0:('lea','61b230'),
 0x61cdaa:('mov','r9,r13'), 0x61cdad:('call','98d7e8'),
 0x61ce01:('call','98d7f0'), 0x61ce07:('test','eax,eax'), 0x61ce09:('je','61ce79'),
 # beneath: only Promise returned through success result, then wrapper returns it
 0x61ce7d:('mov','r13,QWORD PTR [rsp+0xe0]'), 0x61ce8d:('mov','rbp,QWORD PTR [rsp+0x28]'),
 0x61ced1:('mov','[r14+0x8],r13'), 0x61ced5:('mov','[r14],0xffffffffffffffff'),
 0x61cedc:('dec','QWORD PTR [rbp+0x0]'), 0x61ceee:('call','98d7c8'),
 0x62d7d3:('call','61c8f0'), 0x62d7d8:('cmp','[rsp],0xffffffffffffffff'),
 0x62d7dd:('jne','62d75b'), 0x62d7e3:('mov','rax,QWORD PTR [rsp+0x8]'),
 0x62d7e8:('jmp','62d793'), 0x62d7a4:('ret',),
 # execute: worker calls precede result writes; no control field fetch
 0x619e85:('mov','rbx,rsi'), 0x619ea0:('call','4f3bc0'),
 0x619ecf:('mov','[rbx+0x28],rax'), 0x619ed3:('mov','[rbx+0x30],ecx'),
 0x619f15:('mov','rbx,rsi'), 0x619f25:('call','4f4670'),
 0x619f54:('mov','[rbx+0x18],rax'), 0x619f58:('mov','[rbx+0x20],ecx'),
 # complete: the same pointer is loaded, C=2 is checked, C=1 is written
 0x61b28c:('mov','r8,QWORD PTR [rbx+0x50]'),
 0x61b290:('movzx','r8d,BYTE PTR [r8+0x10]'), 0x61b295:('cmp','r8b,0x2'),
 0x61b299:('jne','61b2fe'), 0x61b29b:('call','98d7f8'),
 0x61b2a1:('mov','rax,QWORD PTR [rbx+0x50]'), 0x61b2a5:('mov','BYTE PTR [rax+0x10],0x1'),
 0x61b3a0:('mov','rax,QWORD PTR [rbx+0x50]'), 0x61b3a4:('mov','BYTE PTR [rax+0x10],0x1'),
 0x61b52a:('mov','rax,QWORD PTR [rbx+0x40]'),
 0x61b52e:('movzx','eax,BYTE PTR [rax+0x10]'), 0x61b532:('cmp','al,0x2'),
 0x61b534:('jne','61b5ad'), 0x61b539:('call','98d7f8'),
 0x61b53f:('mov','rax,QWORD PTR [rbx+0x40]'), 0x61b543:('mov','BYTE PTR [rax+0x10],0x1'),
 0x61b64f:('mov','rax,QWORD PTR [rbx+0x40]'), 0x61b653:('mov','BYTE PTR [rax+0x10],0x1'),
 # reference helper consumes the pointer but never fetches/writes C
 0x709270:('mov','rdi,QWORD PTR [rdi]'), 0x709279:('dec','[rdi+0x8]'),
 0x709280:('jmp','98c5a8'),
 # a real computed writer of 2 exists, but linking its rdi to P remains open
 0x778620:('cmp','sil,0x2'), 0x778624:('sete','al'), 0x778627:('inc','al'),
 0x77862b:('test','sil,sil'), 0x778631:('cmove','eax,ecx'),
 0x778634:('xchg','BYTE PTR [rdi+0x10],al'),
}
RELOCS = {0x98c598:'malloc@GLIBC_2.2.5', 0x98c5a8:'free@GLIBC_2.2.5',
 0x98d7e0:'napi_create_promise', 0x98d7e8:'napi_create_async_work',
 0x98d7f0:'napi_queue_async_work', 0x98d7f8:'napi_delete_async_work'}
INDIRECT_WRITER_REFS=[0x984f78,0x985660,0x9860f8,0x986ff8,0x988b50,0x98a218,0x98aa98]

def read_permitted(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 with os.fdopen(fd,'rb') as f:
  info=os.fstat(f.fileno())
  if not stat.S_ISREG(info.st_mode) or info.st_size!=SIZE:
   raise ValueError('Input is not the permitted regular Linux sample size')
  data=f.read(SIZE+1)
 if len(data)!=SIZE or hashlib.sha256(data).hexdigest()!=EXPECTED:
  raise ValueError('Input hash/size mismatch; no binary tooling invoked')
 return data

def parse_instructions(text):
 return {int(m[1],16): m[2] for line in text.splitlines()
         if (m:=re.match(r'\s*([0-9a-f]+):\s+(\S.*)',line))}

def matches(instruction, parts):
 return bool(instruction) and instruction.split()[0]==parts[0] and all(
  re.search(r'(?<![A-Za-z0-9_])'+re.escape(part)+r'(?![A-Za-z0-9_])',instruction) for part in parts[1:])

def relative_matches(line, address, target):
 fields=line.split()
 return len(fields)==4 and fields[0]==f'{address:016x}' and fields[2]=='R_X86_64_RELATIVE' and fields[3]==f'{target:x}'

def verify(path):
 data=read_permitted(path)
 checks=[]
 def check(name,condition):
  checks.append({'check':name,'passed':bool(condition)})
  if not condition:raise AssertionError(name)
 def run(args):
  return subprocess.check_output(args,text=True,timeout=60,
   env={**os.environ,'DEBUGINFOD_URLS':''})
 with tempfile.TemporaryDirectory(prefix='file-control-byte-') as temp:
  snapshot=Path(temp)/'linux.node';snapshot.write_bytes(data)
  frames=run(['/usr/bin/readelf','-W','--debug-dump=frames',str(snapshot)])
  relocs=run(['/usr/bin/readelf','-Wr',str(snapshot)])
  instructions={};windows={}
  for s,e in WINDOWS.items():
   check(f'FDE {s:x}..{e:x}',f'pc={s:016x}..{e:016x}' in frames)
   out=run(['/usr/bin/objdump','-d','-M','intel','--no-show-raw-insn',
            f'--start-address={s}',f'--stop-address={e}',str(snapshot)])
   check(f'clean decode {s:x}',not re.search(r'\(bad\)|\.byte',out))
   windows[s]=parse_instructions(out);instructions.update(windows[s])
  for a,parts in FACTS.items():
   check(f'anchor {a:x}',matches(instructions.get(a,''),parts))
  for a,name in RELOCS.items():
   check(f'import {name}',any(l.startswith(f'{a:016x} ') and name in l for l in relocs.splitlines()))
  for a,target in [(0x98d7c8,0x709270)]+[(a,0x778620) for a in INDIRECT_WRITER_REFS]:
   check(f'relative {a:x}->{target:x}',any(relative_matches(l,a,target) for l in relocs.splitlines()))
  # Bounded operand checks, not universal alias analysis. The worker receives
  # path/fd/flags fields, not the task's control pointer.
  for s,offset in [(0x619e80,'0x50'),(0x619f10,'0x40')]:
   check(f'execute {s:x} no operand at task control slot',
     all(f'[rbx+{offset}]' not in i and f'[rsi+{offset}]' not in i for i in windows[s].values()))
  check('reference helper no byte operand',all('BYTE PTR' not in i for i in windows[0x709270].values()))
  check('snapshot unchanged',hashlib.sha256(snapshot.read_bytes()).hexdigest()==EXPECTED)
  # This is an observation only: dynamic resolution and host behavior remain open.
  observed_cancel_import=any('napi_cancel_async_work' in l for l in relocs.splitlines())
 return {'sample_sha256':EXPECTED,'sample_size':SIZE,'target_loaded':False,'target_executed':False,
  'fde_count':len(WINDOWS),'check_count':len(checks),'checks':checks,
  'observations':{'named_napi_cancel_async_work_dynamic_relocation':observed_cancel_import},
  'scope':'Selected static anchors and local operand checks only; no global writer absence, cancellation reachability, runtime ordering, descriptor-leak or vulnerability proof.'}

if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python3 -B verify-static.py /path/to/verified-linux.node')
 print(json.dumps(verify(sys.argv[1]),ensure_ascii=False,indent=2))
