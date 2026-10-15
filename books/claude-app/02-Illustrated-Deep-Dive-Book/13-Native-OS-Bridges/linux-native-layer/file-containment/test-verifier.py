"""Original fixtures for verifier input/output discipline; no target needed."""
from pathlib import Path
import contextlib, hashlib, importlib.util, io, json, os, tempfile, unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('static_verifier',Path(__file__).with_name('verify-static.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class VerifierFixtures(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='verifier-fixtures-')
  self.root=Path(self.tmp.name);self.data=b'original verifier fixture; never executable\n'
  self.input=self.root/'sample.bin';self.input.write_bytes(self.data)
  self.size=patch.object(v,'SIZE',len(self.data));self.size.start()
  self.sha=patch.object(v,'EXPECTED',hashlib.sha256(self.data).hexdigest());self.sha.start()
 def tearDown(self):self.sha.stop();self.size.stop();self.tmp.cleanup()
 def rejected(self,path):
  with patch.object(v.subprocess,'check_output') as commands,patch.object(v.subprocess,'run') as cc,contextlib.redirect_stderr(io.StringIO()):
   self.assertEqual(v.main([str(path)]),2);commands.assert_not_called();cc.assert_not_called()
 def test_symlink_input_rejected_without_tools(self):
  link=self.root/'input-link';link.symlink_to(self.input);self.rejected(link)
 def test_directory_input_rejected_without_tools(self):self.rejected(self.root)
 def test_fifo_rejected_without_block_or_tools(self):
  fifo=self.root/'input-fifo';os.mkfifo(fifo);self.rejected(fifo)
 def test_wrong_hash_rejected_without_tools(self):
  self.input.write_bytes(b'x'*len(self.data));self.rejected(self.input)
 def test_wrong_size_rejected_without_tools(self):
  self.input.write_bytes(b'x');self.rejected(self.input)
 def test_unknown_output_option_cannot_overwrite_existing_file(self):
  existing=self.root/'existing.json';existing.write_bytes(b'keep this file')
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as e:
   v.main([str(self.input),'--json',str(existing)])
  self.assertEqual(e.exception.code,2);self.assertEqual(existing.read_bytes(),b'keep this file')
 def test_old_private_output_option_is_not_accepted(self):
  existing=self.root/'evidence';existing.mkdir();f=existing/'fde.txt';f.write_bytes(b'keep evidence')
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as e:
   v.main([str(self.input),'--private-evidence',str(existing)])
  self.assertEqual(e.exception.code,2);self.assertEqual(f.read_bytes(),b'keep evidence')
 def test_success_uses_stable_private_snapshot_and_stdout_then_cleans_it(self):
  seen=[];existing=self.root/'existing.json';existing.write_bytes(b'keep this file')
  def inspect(snapshot):
   seen.append(snapshot)
   self.assertNotEqual(snapshot,self.input)
   self.assertEqual(snapshot.read_bytes(),self.data)
   self.assertEqual(snapshot.stat().st_mode & 0o111,0)
   self.input.write_bytes(b'x'*len(self.data))
   self.assertEqual(snapshot.read_bytes(),self.data)
   return {'fixture':'pass','target_executed':False}
  output=io.StringIO()
  with patch.object(v,'verify_snapshot',side_effect=inspect),contextlib.redirect_stdout(output):
   self.assertEqual(v.main([str(self.input)]),0)
  self.assertEqual(json.loads(output.getvalue())['fixture'],'pass')
  self.assertFalse(seen[0].exists());self.assertFalse(seen[0].parent.exists())
  self.assertEqual(existing.read_bytes(),b'keep this file')
 def test_snapshot_is_cleaned_on_verification_exception(self):
  seen=[]
  def fail(snapshot):seen.append(snapshot);raise ValueError('fixture rejection')
  with patch.object(v,'verify_snapshot',side_effect=fail),contextlib.redirect_stderr(io.StringIO()):
   self.assertEqual(v.main([str(self.input)]),2)
  self.assertFalse(seen[0].parent.exists())
 def test_regular_input_bytes_and_mode_unchanged_on_success(self):
  before=self.input.stat().st_mode
  with patch.object(v,'verify_snapshot',return_value={'fixture':'pass'}),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(v.main([str(self.input)]),0)
  self.assertEqual(self.input.read_bytes(),self.data);self.assertEqual(self.input.stat().st_mode,before)

if __name__=='__main__':unittest.main()
