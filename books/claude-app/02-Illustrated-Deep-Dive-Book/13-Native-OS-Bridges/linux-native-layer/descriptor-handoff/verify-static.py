#!/usr/bin/env python3
"""Verify selected static facts against the one permitted Linux ELF; never load it."""
from pathlib import Path
import hashlib,json,os,re,stat,subprocess,sys,tempfile
EXPECTED='c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6'
SIZE=10026272
D=Path(__file__).resolve().parent
WINDOWS={0x4047b0:0x404c32,0x52cb60:0x52cc41,0x58fd60:0x5902d1,
0x617860:0x6178c7,0x6179f0:0x617a9b,0x619e80:0x619f10,0x619f10:0x619f96,
0x61b230:0x61b4d0,0x61b4d0:0x61b72d,0x61c8f0:0x61d12d,
0x6216e0:0x621855,0x62ecd0:0x62f4d8,0x63d5a0:0x63d5a6,
0x701870:0x701a9f,0x709270:0x709286}
# Each address is decoded from its containing FDE, not from an arbitrary byte offset.
CHECKS={
0x58fd77:['lea','6216e0'],0x58fd83:['call','98d4e0'],
0x70187a:['mov','r15,rdx'],0x7018a2:['call','98d7e0'],
0x701973:['mov','[rsp+0x18],r15'],0x701978:['mov','[rsp+0x10],rax'],
0x701980:['movups','[rsp],xmm0'],0x70198d:['xor','esi,esi'],0x701994:['call','98d7b0'],
0x404a05:['call','98c598'],0x404a17:['mov','[rax],0xffffffffffffffff'],
0x404a1e:['mov','[rax+0x8],rcx'],0x404a25:['mov','rsi,rax'],
0x404a2d:['call','98d0b0'],0x404a33:['mov','rdi,r15'],0x404a36:['jmp','404a9d'],
0x404a9f:['call','98d0b8'],
0x6216ec:['mov','rbx,rcx'],0x6216ef:['mov','r14,rdx'],0x6216f2:['mov','r15,rdi'],
0x6216f8:['mov','rsi,QWORD PTR [rcx+0x8]'],0x6216fc:['cmp','rdi,0xffffffffffffffff'],
0x621700:['je','621713'],0x621724:['call','98d488'],0x62172a:['test','eax,eax'],
0x62172c:['je','621790'],0x62178e:['jmp','6217ec'],0x62179b:['call','98d808'],
0x6217a1:['test','eax,eax'],0x6217a3:['je','621821'],0x62180d:['call','52cb60'],
0x62181b:['call','98d800'],0x621821:['mov','rdi,rbx'],0x621824:['call','98c5a8'],
0x62184a:['call','63d5a0'],0x63d5a0:['jmp','98c5a8'],
0x61b4e1:['mov','r14,QWORD PTR [rdx+0x18]'],0x61b4e5:['mov','r13,QWORD PTR [rdx+0x20]'],
0x61b4f7:['mov','[rbx+0x18],0xffffffffffffffff'],0x61b4ff:['mov','[rbx+0x20],0x0'],
0x61b511:['movups','[rbx+0x48],xmm0'],0x61b525:['cmp','esi,0xb'],
0x61b528:['je','61b536'],0x61b532:['cmp','al,0x2'],0x61b534:['jne','61b5ad'],
0x61b539:['call','98d7f8'],0x61b543:['mov','[rax+0x10],0x1'],
0x61b54a:['cmp','r14,0xfffffffffffffffd'],0x61b54e:['ja','61b559'],
0x61b553:['call','98c5a8'],0x61b5ad:['test','esi,esi'],0x61b5b8:['je','61b5ec'],
0x61b5e4:['mov','r13d,0x1'],0x61b5f0:['je','61b666'],0x61b62c:['call','52cb60'],
0x61b63b:['call','98d800'],0x61b641:['mov','rdi,r15'],0x61b649:['call','98d7f8'],
0x61b677:['mov','esi,r13d'],0x61b67a:['call','98d488'],0x61b680:['test','eax,eax'],
0x61b682:['je','61b6e1'],0x61b684:['mov','r13d,eax'],0x61b6dc:['jmp','61b608'],
0x61b6ed:['call','98d808'],0x61b6f3:['jmp','61b641'],0x61b598:['call','98c5a8'],
0x61b70d:['call','617860'],
0x61b243:['mov','r15,QWORD PTR [rdx+0x28]'],0x61b247:['mov','r12,QWORD PTR [rdx+0x30]'],
0x61b259:['mov','[rbx+0x28],0xffffffffffffffff'],0x61b261:['mov','[rbx+0x30],0x0'],
0x61b273:['movups','[rbx+0x58],xmm0'],0x61b287:['cmp','eax,0xb'],
0x61b28a:['je','61b29b'],0x61b295:['cmp','r8b,0x2'],0x61b299:['jne','61b2fe'],
0x61b29b:['call','98d7f8'],0x61b2a5:['mov','[rax+0x10],0x1'],
0x61b2ac:['cmp','r15,0xfffffffffffffffd'],0x61b2b0:['ja','61b2bb'],0x61b2b5:['call','98c5a8'],
0x61b2fe:['test','eax,eax'],0x61b309:['je','61b33a'],0x61b332:['mov','r12d,0x1'],
0x61b33e:['je','61b40c'],0x61b37c:['call','52cb60'],0x61b38b:['call','98d800'],
0x61b391:['mov','rdi,QWORD PTR [rsp]'],0x61b39a:['call','98d7f8'],
0x61b41a:['mov','esi,r12d'],0x61b41d:['call','98d488'],0x61b423:['test','eax,eax'],
0x61b425:['je','61b484'],0x61b427:['mov','r12d,eax'],0x61b47f:['jmp','61b357'],
0x61b490:['call','98d808'],0x61b496:['jmp','61b391'],0x61b3f7:['call','98c5a8'],
0x61b4b0:['call','6179f0'],
0x619f54:['mov','[rbx+0x18],rax'],0x619f58:['mov','[rbx+0x20],ecx'],
0x619ecf:['mov','[rbx+0x28],rax'],0x619ed3:['mov','[rbx+0x30],ecx'],
0x62efd2:['mov','[rsp+0x30],0xffffffffffffffff'],0x62efdb:['mov','[rsp+0x38],0x0'],
0x61cba5:['mov','[rsp+0x58],0xffffffffffffffff'],0x61cbae:['mov','[rsp+0x60],0x0'],
0x62efa1:['mov','[rax+0x10],0x0'],0x61cb5c:['mov','[rax+0x10],0x0'],
0x62f158:['lea','61b4d0'],0x62f165:['call','98d7e8'],0x61cda0:['lea','61b230'],0x61cdad:['call','98d7e8'],
0x709270:['mov','rdi,QWORD PTR [rdi]'],0x709279:['dec','[rdi+0x8]'],0x709280:['jmp','98c5a8'],
0x52cc2c:['call','98c5a8'],0x61788a:['call','98c5a8'],0x61789d:['call','98d7c8'],
0x617a5c:['call','98c5a8'],0x617a6f:['call','98d7c8']}
RELOCS={0x98c598:'malloc@GLIBC_2.2.5',0x98c5a8:'free@GLIBC_2.2.5',0x98c928:'close@GLIBC_2.2.5',
0x98d0b0:'napi_call_threadsafe_function',0x98d0b8:'napi_release_threadsafe_function',
0x98d488:'napi_create_int32',0x98d7b0:'napi_create_threadsafe_function',0x98d7e0:'napi_create_promise',
0x98d7e8:'napi_create_async_work',0x98d7f8:'napi_delete_async_work',0x98d800:'napi_reject_deferred',0x98d808:'napi_resolve_deferred'}
def main():
 if len(sys.argv)!=2: raise SystemExit('Usage: python3 verify-static.py /path/to/verified-linux.node')
 fd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 with os.fdopen(fd,'rb') as f:
  st=os.fstat(f.fileno())
  if not stat.S_ISREG(st.st_mode) or st.st_size!=SIZE: raise ValueError('Not the permitted regular Linux sample size')
  data=f.read(SIZE+1)
 digest=hashlib.sha256(data).hexdigest()
 if len(data)!=SIZE or digest!=EXPECTED: raise ValueError('Sample hash/size mismatch; no binary tooling invoked')
 checks=[]
 def check(name,ok):
  checks.append({'check':name,'passed':bool(ok)})
  if not ok: raise AssertionError(name)
 with tempfile.TemporaryDirectory(prefix='native-descriptor-handoff-') as tmp:
  p=Path(tmp)/'linux.node';p.write_bytes(data)
  frames=subprocess.check_output(['readelf','-W','--debug-dump=frames',str(p)],text=True)
  reloc=subprocess.check_output(['readelf','-Wr',str(p)],text=True)
  ds={};instructions={}
  for s,e in WINDOWS.items():
   check(f'FDE {s:x}..{e:x}',f'pc={s:016x}..{e:016x}' in frames)
   out=subprocess.check_output(['objdump','-d','-M','intel',f'--start-address={s}',f'--stop-address={e}',str(p)],text=True)
   ds[s]=out
   check(f'decode {s:x}',not re.search(r'\(bad\)|\.byte',out))
   for line in out.splitlines():
    m=re.match(r'\s*([0-9a-f]+):\s',line)
    if m: instructions[int(m.group(1),16)]=line
  for a,parts in CHECKS.items():
   line=instructions.get(a,'')
   check(f'instruction {a:x}',all(x in line for x in parts))
  for a,name in RELOCS.items():
   check(f'relocation {a:x} {name}',any(l.startswith(f'{a:016x} ') and name in l for l in reloc.splitlines()))
  for a,target in [(0x98d4e0,0x701870),(0x98d7c8,0x709270)]:
   check(f'relative {a:x}->{target:x}',any(l.startswith(f'{a:016x} ') and l.rstrip().endswith(f'{target:x}') for l in reloc.splitlines()))
  # This assertion is intentionally lexical and local; it is not global non-leak proof.
  for s in [0x6216e0,0x61b230,0x61b4d0,0x617860,0x6179f0,0x63d5a0,0x709270]:
   check(f'no direct close GOT reference in FDE {s:x}',not re.search(r'# 98c928\b',ds[s]))
  check('stable snapshot',hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED)
 print(json.dumps({'sample_sha256':digest,'sample_size':SIZE,'executed_target':False,'loaded_target':False,
 'fde_count':len(WINDOWS),'check_count':len(checks),'checks':checks,
 'scope':'Selected instruction/relocation checks only. Control-flow/data-flow interpretation is manual; this is not a runtime or global ownership proof.'},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
