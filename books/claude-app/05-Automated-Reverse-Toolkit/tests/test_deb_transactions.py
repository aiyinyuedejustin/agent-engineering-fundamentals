"""Original ASAR and Debian synthetic integration fixtures; no product bytes."""
import hashlib
import io
import json
import lzma
import os
from pathlib import Path
import stat
import struct
import tarfile
import tempfile
import unittest
from unittest import mock

import deb_versions as v
from deb_projection import Selection, ToolkitError, inspect_deb
from toolkit.asar import extract_asar
from toolkit.inventory import snapshot
from toolkit.diffing import diff_snapshots

SCOPE = Selection('opt/demo/app.asar','opt/demo/app.asar.unpacked')

def integrity(data):
    value = hashlib.sha256(data).hexdigest()
    return dict(algorithm='SHA256',hash=value,blockSize=65536,blocks=[value])

def asar(color=b'red', corrupt=False):
    packed = b':root { --original-fixture: ' + color + b'; }'
    external = b'original opaque bytes'
    nodes = {'demo.css':dict(size=len(packed),offset='0',integrity=integrity(packed)),
             'native':dict(files={'opaque.bin':dict(size=len(external),unpacked=True,integrity=integrity(external))})}
    if corrupt: nodes['demo.css']['integrity']['hash'] = '0'*64
    text = json.dumps(dict(files=nodes),separators=(',',':')).encode()
    padded = text+b'\0'*((-len(text))%4)
    header_size = 8+len(padded)
    return struct.pack('<4I',4,header_size,header_size-4,len(text))+padded+packed,external

def tar(entries):
    out = io.BytesIO()
    with tarfile.open(fileobj=out,mode='w',format=tarfile.GNU_FORMAT) as target:
        for name,data,kind in entries:
            item = tarfile.TarInfo(name)
            item.type = kind
            item.mode = 0o4755
            item.size = len(data)
            if kind == tarfile.SYMTYPE: item.linkname = '../../never-follow'
            target.addfile(item,io.BytesIO(data))
    return out.getvalue()

def deb(color=b'red',extra=None,missing=False,corrupt=False):
    archive,external = asar(color,corrupt)
    data = [(SCOPE.asar,archive,tarfile.REGTYPE),
            (SCOPE.companion,b'',tarfile.DIRTYPE),
            (SCOPE.companion+'/native',b'',tarfile.DIRTYPE)]
    if not missing: data.append((SCOPE.companion+'/native/opaque.bin',external,tarfile.REGTYPE))
    if extra == 'file': data.append((SCOPE.companion+'/extra.bin',b'extra',tarfile.REGTYPE))
    if extra == 'directory': data.append((SCOPE.companion+'/extra',b'',tarfile.DIRTYPE))
    data.append(('bin/excluded-link',b'',tarfile.SYMTYPE))
    control = tar([('control',b'Package: original-fixture\n',tarfile.REGTYPE),('postinst',b'exit 99 # inert',tarfile.REGTYPE)])
    parts = [('debian-binary',b'2.0\n'),('control.tar.xz',lzma.compress(control)),('data.tar.xz',lzma.compress(tar(data)))]
    out = bytearray(b'!<arch>\n')
    for name,body in parts:
        out += (name.ljust(16)+'0'.ljust(12)+'0'.ljust(6)+'0'.ljust(6)+'100644'.ljust(8)+str(len(body)).ljust(10)+'`\n').encode()
        out += body + (b'\n' if len(body)%2 else b'')
    return bytes(out)

class Transactions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.root = Path(self.temp.name)
        self.old = self.root/'old.deb'; self.new = self.root/'new.deb'
        self.old.write_bytes(deb()); self.new.write_bytes(deb(b'blue'))
        self.output = self.root/'output'
    def tearDown(self): self.temp.cleanup()
    def compare(self): return v.compare_debs(self.old,self.new,self.output,SCOPE)
    def clean(self):
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob('.deb-projection-*')))
    def test_known_static_change_and_scope_binding(self):
        self.compare()
        report = json.loads((self.output/'diff.json').read_text())
        self.assertEqual(len(report['inventories']['css_tokens']['changed']),1)
        self.assertFalse(report['projection']['complete_package'])
        self.assertIn('仅比较所选', (self.output/'diff.md').read_text())
    def test_direct_asar_matches_projected_content(self):
        self.compare()
        roots=[]
        for side,color in [('old',b'red'),('new',b'blue')]:
            archive,external=asar(color)
            inp=self.root/(side+'.asar'); inp.write_bytes(archive)
            companion=self.root/(side+'-companion'); (companion/'native').mkdir(parents=True)
            (companion/'native/opaque.bin').write_bytes(external)
            root=self.root/(side+'-direct'); extract_asar(inp,root,unpacked_dir=companion)
            direct=snapshot(root,side+'-unverified-label')
            projected=json.loads((self.output/(side+'-snapshot.json')).read_text())
            self.assertEqual(direct['files'],projected['files'])
            self.assertEqual(direct['records'],projected['records'])
            roots.append(direct)
        core=diff_snapshots(*roots); projected=json.loads((self.output/'diff.json').read_text())
        self.assertEqual(core['inventories'],projected['inventories'])
        self.assertEqual(core['files'],projected['files'])
    def test_permissions_and_no_links(self):
        self.compare()
        for path in self.output.rglob('*'):
            self.assertFalse(path.is_symlink())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o700 if path.is_dir() else 0o600)
            if path.is_file(): self.assertEqual(path.stat().st_nlink,1)
    def test_inspect_does_not_claim_inner_validation(self):
        result=inspect_deb(self.old,SCOPE)
        self.assertFalse(result['selected_asar_declared_scope_complete'])
        self.assertTrue(result['outer_compressed_streams_verified'])
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),['new.deb','old.deb'])
    def test_extra_file_is_not_prefiltered(self):
        self.new.write_bytes(deb(extra='file'))
        with self.assertRaisesRegex(ToolkitError,'extra'): self.compare()
        self.clean()
    def test_extra_empty_directory_is_not_prefiltered(self):
        self.new.write_bytes(deb(extra='directory'))
        with self.assertRaisesRegex(ToolkitError,'extra'): self.compare()
        self.clean()
    def test_missing_companion_rolls_back(self):
        self.new.write_bytes(deb(missing=True))
        with self.assertRaises(ToolkitError): self.compare()
        self.clean()
    def test_inner_hash_failure_rolls_back_both(self):
        self.new.write_bytes(deb(corrupt=True))
        with self.assertRaisesRegex(ToolkitError,'integrity'): self.compare()
        self.clean()
    def test_existing_file_untouched(self):
        self.output.write_bytes(b'sentinel')
        with self.assertRaises(ToolkitError): self.compare()
        self.assertEqual(self.output.read_bytes(),b'sentinel')
    def test_existing_directory_untouched(self):
        self.output.mkdir(); (self.output/'sentinel').write_bytes(b'keep')
        with self.assertRaises(ToolkitError): self.compare()
        self.assertEqual((self.output/'sentinel').read_bytes(),b'keep')
    def test_dangling_output_symlink_untouched(self):
        self.output.symlink_to('missing')
        with self.assertRaises(ToolkitError): self.compare()
        self.assertTrue(self.output.is_symlink())
    def test_late_output_race_no_replace(self):
        original=v.atomic_publish
        def race(stage,destination):
            destination.mkdir(); (destination/'sentinel').write_bytes(b'keep')
            original(stage,destination)
        with mock.patch.object(v,'atomic_publish',race), self.assertRaises(ToolkitError): self.compare()
        self.assertEqual((self.output/'sentinel').read_bytes(),b'keep')
        self.assertFalse(list(self.root.glob('.deb-projection-*')))
    def test_source_same_size_mutation_between_passes(self):
        original=v.scan; calls=0
        def changed(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==3:
                body=bytearray(self.old.read_bytes()); body[-1]^=1; self.old.write_bytes(body)
            return original(*args,**kwargs)
        with mock.patch.object(v,'scan',changed), self.assertRaises(ToolkitError): self.compare()
        self.clean()
    def test_source_identity_changed_before_publish(self):
        original=v.Reports.json
        def changed(reports,path,value,*args):
            result=original(reports,path,value,*args)
            if path.name=='run.json': os.utime(self.old,ns=(1,1))
            return result
        with mock.patch.object(v.Reports,'json',changed), self.assertRaises(ToolkitError): self.compare()
        self.clean()
    def test_keyboard_interrupt_rollback(self):
        with mock.patch.object(v,'snapshot',side_effect=KeyboardInterrupt),self.assertRaises(KeyboardInterrupt): self.compare()
        self.clean()
    def test_disk_write_error_rollback(self):
        with mock.patch.object(v.Reports,'json',side_effect=OSError('synthetic disk full')),self.assertRaises(OSError): self.compare()
        self.clean()
    def test_report_total_budget_rollback(self):
        with mock.patch.object(v,'REPORT_TOTAL',100),self.assertRaisesRegex(ToolkitError,'Report byte'): self.compare()
        self.clean()
    def test_additional_disk_budget_before_extraction(self):
        with mock.patch.object(v,'SIDE_DISK',100),mock.patch.object(v,'extract_asar') as extract,self.assertRaisesRegex(ToolkitError,'disk budget'): self.compare()
        extract.assert_not_called(); self.clean()
    def test_input_symlink_rejected(self):
        self.old.unlink(); self.old.symlink_to(self.new)
        with self.assertRaises(ToolkitError): self.compare()
        self.clean()
    def test_input_hardlink_rejected(self):
        os.link(self.old,self.root/'hardlink')
        with self.assertRaises(ToolkitError): self.compare()
        self.clean()
    def test_inspect_cli_budget_no_partial_stdout(self):
        output=io.StringIO(); errors=io.StringIO()
        from contextlib import redirect_stdout, redirect_stderr
        with mock.patch.object(v,'ENVELOPE_REPORT',100),redirect_stdout(output),redirect_stderr(errors):
            status=v.main(['inspect',str(self.old),'--asar-member',SCOPE.asar,'--companion-prefix',SCOPE.companion])
        self.assertEqual(status,2); self.assertEqual(output.getvalue(),'')
        self.assertIn('CLI JSON byte budget',errors.getvalue())
    def test_writer_exact_limit(self):
        report=v.Reports(); path=self.root/'report'
        self.assertEqual(report.write(path,['é'],2),2)
        self.assertEqual(path.read_bytes(),'é'.encode())
    def test_writer_over_limit_never_writes_excess(self):
        report=v.Reports(); path=self.root/'report'
        with self.assertRaises(ToolkitError): report.write(path,['a','é'],2)
        self.assertEqual(path.read_bytes(),b'a')
    def test_policy_scope_changes_hash(self):
        self.compare()
        before=json.loads((self.output/'old-snapshot.json').read_text())
        after=json.loads((self.output/'old-snapshot.json').read_text())
        v.scope_snapshot(after,Selection('elsewhere.asar'),'linux-unverified-label')
        self.assertNotEqual(before['identity']['policy_sha256'],after['identity']['policy_sha256'])

if __name__=='__main__': unittest.main(verbosity=2)
