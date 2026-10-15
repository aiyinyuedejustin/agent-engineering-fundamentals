#!/usr/bin/env python3
"""Original hash-gated, read-only-input static verifier. JSON goes to stdout.
The target is never loaded or executed. Only a digest-matching regular input
file is copied into a private TemporaryDirectory for GNU readelf/objdump.
No caller-selected output files/directories are accepted. Selected instruction
anchors are not a full control-flow, behavioral, or security proof.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, stat, subprocess, sys, tempfile

EXPECTED='c3934f38ec5de0a2b6ef31641c28d8bec2fb125ff6a3a39b6dba84d9885cbca6'
SIZE=10026272
STARTS=[0x6313d0,0x6316a0,0x62d560,0x62ecd0,0x61c8f0,0x619e80,0x619f10,
        0x4f4670,0x4f3bc0,0x4f34b0,0x62d330,0x61b230,0x61b4d0,0x632350]

def read_verified_input(path):
 # NONBLOCK avoids waiting on a FIFO before fstat can reject it. NOFOLLOW
 # rejects a symlink in the final path component. No input write is opened.
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  meta=os.fstat(fd)
  if not stat.S_ISREG(meta.st_mode):raise ValueError('input must be a regular file')
  if meta.st_size!=SIZE:raise ValueError('unexpected sample size')
  chunks=[];remaining=SIZE+1
  while remaining:
   chunk=os.read(fd,min(remaining,1024*1024))
   if not chunk:break
   chunks.append(chunk);remaining-=len(chunk)
  data=b''.join(chunks)
 finally:os.close(fd)
 if len(data)!=SIZE or hashlib.sha256(data).hexdigest()!=EXPECTED:
  raise ValueError('unexpected sample digest/size')
 return data

def verify_snapshot(binary):
 before=EXPECTED
 def digest():return hashlib.sha256(binary.read_bytes()).hexdigest()
 results=[]
 def check(name,ok):
  results.append({'test':name,'passed':bool(ok)})
  if not ok:raise AssertionError(name)
 check('fixed Linux amd64 snapshot digest and size',digest()==EXPECTED and binary.stat().st_size==SIZE)
 def run(argv):return subprocess.check_output(argv+[str(binary)],text=True)
 frames=run(['readelf','-wf'])
 relocs=run(['readelf','-Wr'])
 bounds={int(a,16):int(b,16) for a,b in re.findall(r'pc=([0-9a-f]+)\.\.([0-9a-f]+)',frames)}
 dec={}
 windows=[]
 for a in STARTS:
  check(f'FDE begins at {a:x}',a in bounds)
  b=bounds[a]
  text=run(['objdump','-d','-M','intel',f'--start-address={a}',f'--stop-address={b}'])
  check(f'aligned decode has no bad/byte marker {a:x}',not re.search(r'\(bad\)|\.byte',text))
  dec[a]=text
  windows.append({'start':hex(a),'end_exclusive':hex(b)})
 def anchor(f,pc,pattern):
  check(f'instruction {pc:x}: {pattern}',bool(re.search(rf'^\s*{pc:x}:.*{pattern}',dec[f],re.M)))
 def edge(f,pc,dst):anchor(f,pc,rf'call\s+{dst:x}\b')
 def got(f,pc,slot):anchor(f,pc,rf'call.*# {slot:x}\b')
 def relocation(slot,symbol):check(f'GOT {slot:x} resolves {symbol}',bool(re.search(rf'^0*{slot:x}\s+.*GLOB_DAT.*\b{symbol}(?:@|\s)',relocs,re.M)))
 for slot,sym in [(0x98d640,'napi_create_function'),(0x98d7e8,'napi_create_async_work'),(0x98d7f0,'napi_queue_async_work'),(0x98c830,'syscall'),(0x98c7a0,'__errno_location'),(0x98d2e8,'openat'),(0x98d300,'open'),(0x98c928,'close'),(0x98d488,'napi_create_int32'),(0x98d800,'napi_reject_deferred'),(0x98d808,'napi_resolve_deferred')]:relocation(slot,sym)
 b=binary.read_bytes()
 for pos,name in [(0x3f04d,b'openBeneath'),(0x3d84d,b'openRootDir')]:check(f'exact method name at {pos:x}',b[pos:pos+len(name)]==name)
 # Register constructors bind names and callbacks to napi_create_function.
 for f,npc,np,cbpc,cb,call in [(0x6313d0,0x6313e1,0x3f04d,0x6313e8,0x62d560,0x6313fd),(0x6316a0,0x6316b1,0x3d84d,0x6316b8,0x62ecd0,0x6316cd)]:
  anchor(f,npc,rf'lea\s+rsi,.*# {np:x}\b');anchor(f,cbpc,rf'lea\s+rcx,.*# {cb:x}\b');got(f,call,0x98d640)
 edge(0x62d560,0x62d7d3,0x61c8f0)
 # Explicit execute callback argument and subsequent queue call.
 for f,pc,ex,call,queue in [(0x61c8f0,0x61cd99,0x619e80,0x61cdad,0x61ce01),(0x62ecd0,0x62f151,0x619f10,0x62f165,0x62f1b0)]:
  anchor(f,pc,rf'lea\s+rcx,.*# {ex:x}\b');got(f,call,0x98d7e8);got(f,queue,0x98d7f0)
 edge(0x619e80,0x619ea0,0x4f3bc0);edge(0x619f10,0x619f25,0x4f4670)
 anchor(0x619e80,0x619e88,r'mov\s+esi,DWORD PTR \[rsi\+0x18\]')
 anchor(0x4f4670,0x4f4700,r'mov\s+esi,0x2b0000');got(0x4f4670,0x4f4707,0x98d300)
 anchor(0x4f4670,0x4f470f,r'js\s+4f473c');anchor(0x4f4670,0x4f4711,r'mov\s+DWORD PTR \[r14\+0x8\],eax')
 # Per-component validation and slash separator.
 edge(0x4f3bc0,0x4f3c0d,0x62d330)
 check('join separator is slash',b[0x57005:0x57006]==b'/')
 anchor(0x4f3bc0,0x4f3c2a,r'lea\s+rcx,.*# 57005\b')
 for pc,pat in [(0x62d357,r'je\s+62d433'),(0x62d37e,r'cmp\s+BYTE PTR \[rsi\],0x2e'),(0x62d383,r'jmp\s+62d433'),(0x62d388,r'cmp\s+WORD PTR \[rsi\],0x2e2e'),(0x62d38d,r'je\s+62d433'),(0x62d52a,r'je\s+62d433'),(0x62d530,r'cmp\s+eax,0x2f'),(0x62d533,r'je\s+62d433'),(0x62d541,r'mov.*0xffffffffffffffff')]:anchor(0x62d330,pc,pat)
 # open_how: flags at +0x90; mode +0x98; resolve +0xa0.
 for pc,pat in [(0x4f3be1,r'mov\s+DWORD PTR \[rsp\+0xc\],esi'),(0x4f3c5a,r'or\s+eax,0xa0800'),(0x4f3c61,r'shl\s+ecx,0x19'),(0x4f3c64,r'sar\s+ecx,0x1f'),(0x4f3c6b,r'mov\s+QWORD PTR \[rsp\+0x90\],rax'),(0x4f3c73,r'mov\s+QWORD PTR \[rsp\+0x98\],rcx'),(0x4f3c7b,r'mov\s+QWORD PTR \[rsp\+0xa0\],0xe'),(0x4f3d4b,r'lea\s+rcx,\[rsp\+0x90\]'),(0x4f3d53,r'mov\s+edi,0x1b5'),(0x4f3d58,r'mov\s+r8d,0x18'),(0x4f3d5e,r'mov\s+esi,DWORD PTR \[rsp\+0xc\]'),(0x4f3d62,r'mov\s+rdx,r15'),(0x4f3d70,r'js\s+4f3d97')]:anchor(0x4f3bc0,pc,pat)
 got(0x4f3bc0,0x4f3d67,0x98c830);got(0x4f3bc0,0x4f3d9c,0x98c7a0)
 for pc,pat in [(0x4f3dde,r'xor\s+ebp,ebp'),(0x4f3de0,r'cmp\s+eax,0xb'),(0x4f3de3,r'je\s+4f3e29'),(0x4f3de5,r'cmp\s+eax,0x26'),(0x4f3de8,r'je\s+4f3e29'),(0x4f3e5e,r'je\s+4f3e7c')]:anchor(0x4f3bc0,pc,pat)
 edge(0x4f3bc0,0x4f3e03,0x632350);edge(0x4f3bc0,0x4f3ea6,0x4f34b0)
 # Error formatter normal return stores a nonnegative length, never success -1.
 for pc,pat in [(0x6323f8,r'test\s+r15,r15'),(0x6323fb,r'jns\s+63240a'),(0x632408,r'ud2'),(0x63243b,r'mov\s+QWORD PTR \[rbx\],r15')]:anchor(0x632350,pc,pat)
 # Fallback opens each nonleaf with the same fixed directory flags, then leaf.
 for pc,pat in [(0x4f372e,r'or\s+edx,0xa0800'),(0x4f379a,r'mov\s+edx,0x2b0000'),(0x4f39b8,r'mov\s+edx,0x2b0000'),(0x4f39ad,r'mov\s+r13d,DWORD PTR \[rsp\+0xc\]'),(0x4f39b2,r'mov\s+edi,r13d'),(0x4f39c5,r'mov\s+DWORD PTR \[rsp\+0x4\],eax')]:anchor(0x4f34b0,pc,pat)
 for pc in [0x4f3741,0x4f37a1,0x4f39bf]:got(0x4f34b0,pc,0x98d2e8)
 for pc in [0x4f3510,0x4f35ab,0x4f3970]:edge(0x4f34b0,pc,0x62d330)
 for pc in [0x4f375b,0x4f39d4]:got(0x4f34b0,pc,0x98c928)
 for f,integer,resolve,reject in [(0x61b230,0x61b41d,0x61b490,0x61b38b),(0x61b4d0,0x61b67a,0x61b6ed,0x61b63b)]:
  got(f,integer,0x98d488);got(f,resolve,0x98d808);got(f,reject,0x98d800)
 abi=subprocess.run(['cc','-m64','-fsyntax-only',str(Path(__file__).with_name('abi-layout.c'))],capture_output=True,text=True)
 check('analysis-host x86-64 ABI assertions (compile-only)',abi.returncode==0)
 check('sample digest unchanged after checks',digest()==before)
 report={'kind':'sample-bound selected static anchors; not behavior or full control-flow proof','input_sha256':before,'snapshot_sha256_after':digest(),'target_bytes':SIZE,'target_executed':False,'target_loaded':False,'fdes':windows,'checks':results,'passed':len(results)}
 return report

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('binary',type=Path)
 args=p.parse_args(argv)
 try:
  data=read_verified_input(args.binary)
  with tempfile.TemporaryDirectory(prefix='native-static-') as owned:
   snapshot=Path(owned)/'verified-sample.node'
   # The newly created private directory is ours; create an exclusive,
   # non-executable file and never reopen the caller's path for analysis.
   fd=os.open(snapshot,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as f:f.write(data)
   report=verify_snapshot(snapshot)
  print(json.dumps(report,ensure_ascii=False,indent=2))
  return 0
 except (OSError,ValueError) as e:
  print(f'REJECTED: {e}; target not loaded or executed.',file=sys.stderr)
  return 2

if __name__=='__main__':sys.exit(main())
