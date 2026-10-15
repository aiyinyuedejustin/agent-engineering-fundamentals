#!/usr/bin/env python3
"""Input/snapshot/anchor tests using only synthetic bytes and synthetic output."""
import contextlib
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('verify_static',Path(__file__).with_name('verify-static.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class SafetyFixtures(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='file-control-fixture-')
  self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);self.input=self.root/'input';self.data=b'fixture'
  self.input.write_bytes(self.data)
  self.patches=contextlib.ExitStack();self.addCleanup(self.patches.close)
  self.patches.enter_context(patch.object(v,'SIZE',len(self.data)))
  self.patches.enter_context(patch.object(v,'EXPECTED',hashlib.sha256(self.data).hexdigest()))
 def rejected_without_tool(self,path):
  with patch.object(v.subprocess,'check_output') as tool:
   with self.assertRaises((ValueError,OSError)):v.verify(path)
   tool.assert_not_called()
 def test_valid_input_bytes(self):self.assertEqual(v.read_permitted(self.input),self.data)
 def test_wrong_size_before_tool(self):
  self.input.write_bytes(b'x');self.rejected_without_tool(self.input)
 def test_same_size_wrong_hash_before_tool(self):
  self.input.write_bytes(b'x'*len(self.data));self.rejected_without_tool(self.input)
 def test_symlink_before_tool(self):
  link=self.root/'link';link.symlink_to(self.input);self.rejected_without_tool(link)
 def test_directory_before_tool(self):self.rejected_without_tool(self.root)
 def test_fifo_before_tool(self):
  fifo=self.root/'pipe';os.mkfifo(fifo);self.rejected_without_tool(fifo)
 def test_missing_before_tool(self):self.rejected_without_tool(self.root/'missing')
 def test_cleanup_after_tool_error(self):
  snapshots=[]
  def fail(args,**kw):
   q=Path(args[-1]);snapshots.append(q)
   self.assertEqual(q.read_bytes(),self.data)
   self.assertNotEqual(q,self.input)
   self.assertEqual(kw['env']['DEBUGINFOD_URLS'],'')
   self.assertNotIn('shell',kw)
   raise subprocess.CalledProcessError(1,args)
  with patch.object(v.subprocess,'check_output',side_effect=fail):
   with self.assertRaises(subprocess.CalledProcessError):v.verify(self.input)
  self.assertTrue(snapshots);self.assertTrue(all(not q.exists() for q in snapshots))
 def test_cleanup_after_anchor_failure(self):
  snapshots=[]
  def synthetic(args,**kw):
   snapshots.append(Path(args[-1]))
   if '--debug-dump=frames' in args:return '\n'.join(f'pc={s:016x}..{e:016x}' for s,e in v.WINDOWS.items())
   return ''
  with patch.object(v.subprocess,'check_output',side_effect=synthetic):
   with self.assertRaisesRegex(AssertionError,'anchor'):v.verify(self.input)
  self.assertTrue(all(not q.exists() for q in snapshots))
 def test_exact_opcode(self):
  self.assertTrue(v.matches('mov BYTE PTR [rax+0x10],0x2',('mov','BYTE PTR [rax+0x10],0x2')))
  self.assertFalse(v.matches('cmov BYTE PTR [rax+0x10],0x2',('mov','BYTE PTR [rax+0x10],0x2')))
 def test_exact_numeric_operand(self):
  self.assertFalse(v.matches('cmp al,0x20',('cmp','al,0x2')))
  self.assertTrue(v.matches('cmp al,0x2',('cmp','al,0x2')))
 def test_exact_address_left_boundary(self):
  self.assertFalse(v.matches('call a98d7c8',('call','98d7c8')))
  self.assertTrue(v.matches('call 98d7c8',('call','98d7c8')))
 def test_relative_requires_type(self):
  self.assertTrue(v.relative_matches('000000000098d7c8 0000000000000008 R_X86_64_RELATIVE 709270',0x98d7c8,0x709270))
  self.assertFalse(v.relative_matches('000000000098d7c8 0000000000000008 R_X86_64_GLOB_DAT 709270',0x98d7c8,0x709270))
 def test_exact_register_suffix(self):
  self.assertFalse(v.matches('mov [r14+0x8],r13d',('mov','[r14+0x8],r13')))
 def test_parser_address(self):
  self.assertEqual(v.parse_instructions('  10: cmp al,0x2\nignored line\n  12: jne 99'),{16:'cmp al,0x2',18:'jne 99'})

if __name__=='__main__':unittest.main(verbosity=2)
