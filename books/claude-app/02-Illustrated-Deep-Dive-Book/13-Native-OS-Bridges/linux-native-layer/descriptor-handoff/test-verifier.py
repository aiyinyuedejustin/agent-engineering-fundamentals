#!/usr/bin/env python3
"""Own fixtures only. Does not read or execute any product binary."""
import contextlib,hashlib,importlib.util,io,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('verifier',Path(__file__).with_name('verify-static.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
REAL_TEMP=tempfile.TemporaryDirectory
class VerifierTests(unittest.TestCase):
 def setUp(self):
  self.tmp=REAL_TEMP(prefix='descriptor-handoff-fixtures-');self.root=Path(self.tmp.name)
  self.fixture=self.root/'fixture.bin';self.fixture.write_bytes(b'own-fixture')
 def tearDown(self):self.tmp.cleanup()
 def invoke(self,args):
  with patch.object(v.sys,'argv',['verify-static.py']+args),contextlib.redirect_stdout(io.StringIO()) as out:
   v.main()
  return out.getvalue()
 def rejects_before_tools(self,args,exc=Exception):
  with patch.object(v.subprocess,'check_output') as tool:
   with self.assertRaises(exc):self.invoke(args)
   tool.assert_not_called()
 def test_missing_argument(self):self.rejects_before_tools([],SystemExit)
 def test_extra_output_argument(self):self.rejects_before_tools([str(self.fixture),'--output=x'],SystemExit)
 def test_missing_file(self):self.rejects_before_tools([str(self.root/'absent')],FileNotFoundError)
 def test_directory(self):self.rejects_before_tools([str(self.root)],(ValueError,IsADirectoryError))
 def test_fifo_no_blocking(self):
  p=self.root/'fifo';os.mkfifo(p);self.rejects_before_tools([str(p)],ValueError)
 def test_terminal_symlink(self):
  p=self.root/'link';p.symlink_to(self.fixture);self.rejects_before_tools([str(p)],OSError)
 def test_wrong_size(self):self.rejects_before_tools([str(self.fixture)],ValueError)
 def test_wrong_hash(self):
  with patch.object(v,'SIZE',len(b'own-fixture')):
   self.rejects_before_tools([str(self.fixture)],ValueError)
 def fake_tools(self,args,**kwargs):
  p=Path(args[-1]);self.assertTrue(p.is_file());self.assertEqual(p.read_bytes(),b'own-fixture')
  self.assertEqual(p.parent.parent,self.root);self.assertNotEqual(p,self.fixture)
  self.snapshots.add(p)
  if args[0]=='readelf' and '--debug-dump=frames' in args:
   return '\n'.join(f'pc={s:016x}..{e:016x}' for s,e in v.WINDOWS.items())
  if args[0]=='readelf':
   return '\n'.join([f'{a:016x} GLOB_DAT {n}' for a,n in v.RELOCS.items()]+[
    '000000000098d4e0 RELATIVE 701870','000000000098d7c8 RELATIVE 709270'])
  s=int(next(x.split('=')[1] for x in args if x.startswith('--start-address=')))
  e=v.WINDOWS[s]
  return '\n'.join(f' {a:x}: '+ ' '.join(parts) for a,parts in v.CHECKS.items() if s<=a<e)
 def temp_factory(self,*args,**kwargs):return REAL_TEMP(*args,**kwargs,dir=self.root)
 def fixture_context(self):
  stack=contextlib.ExitStack()
  stack.enter_context(patch.object(v,'SIZE',len(b'own-fixture')))
  stack.enter_context(patch.object(v,'EXPECTED',hashlib.sha256(b'own-fixture').hexdigest()))
  stack.enter_context(patch.object(v.tempfile,'TemporaryDirectory',side_effect=self.temp_factory))
  return stack
 def test_stable_snapshot_and_success_cleanup(self):
  self.snapshots=set()
  with self.fixture_context(),patch.object(v.subprocess,'check_output',side_effect=self.fake_tools):
   r=json.loads(self.invoke([str(self.fixture)]))
  self.assertEqual(r['fde_count'],15);self.assertTrue(all(x['passed'] for x in r['checks']))
  self.assertEqual(self.fixture.read_bytes(),b'own-fixture');self.assertTrue(self.snapshots)
  self.assertTrue(all(not p.exists() for p in self.snapshots));self.assertEqual(list(self.root.iterdir()),[self.fixture])
 def test_tool_failure_cleans_only_owned_snapshot(self):
  unrelated=self.root/'keep.txt';unrelated.write_text('keep')
  with self.fixture_context(),patch.object(v.subprocess,'check_output',side_effect=RuntimeError('own fixture failure')):
   with self.assertRaises(RuntimeError):self.invoke([str(self.fixture)])
  self.assertEqual(self.fixture.read_bytes(),b'own-fixture');self.assertEqual(unrelated.read_text(),'keep')
  self.assertEqual(set(self.root.iterdir()),{self.fixture,unrelated})
if __name__=='__main__':unittest.main(verbosity=2)
