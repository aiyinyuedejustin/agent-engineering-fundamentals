"""Relocated installation and foreign working-directory CLI smoke; synthetic only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_deb_transactions import deb, SCOPE
import reverse_toolkit
import deb_versions

class PortableInstall(unittest.TestCase):
    def test_relocated_without_pythonpath_and_foreign_cwd(self):
        candidate=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as scratch:
            root=Path(scratch)
            installed=root/'relocated toolkit with spaces'
            shutil.copytree(Path(reverse_toolkit.__file__).parent,installed,
                            ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            for name in ('deb_projection.py','deb_versions.py'):
                shutil.copyfile(Path(deb_versions.__file__).resolve().parent/name,installed/name)
            foreign=root/'foreign cwd'; foreign.mkdir()
            old=root/'old original.deb'; new=root/'new original.deb'
            old.write_bytes(deb()); new.write_bytes(deb(b'green'))
            env=dict(os.environ); env.pop('PYTHONPATH',None); env['PYTHONDONTWRITEBYTECODE']='1'
            common=['--asar-member',SCOPE.asar,'--companion-prefix',SCOPE.companion]
            inspect=subprocess.run([sys.executable,'-B',str(installed/'deb_versions.py'),'inspect',str(old),*common],cwd=foreign,env=env,capture_output=True,text=True,check=True)
            info=json.loads(inspect.stdout)
            self.assertTrue(info['outer_envelope_inventory_complete'])
            self.assertFalse(info['selected_asar_declared_scope_complete'])
            output=root/'new output'
            compare=subprocess.run([sys.executable,'-B',str(installed/'deb_versions.py'),'compare',str(old),str(new),*common,'--output',str(output)],cwd=foreign,env=env,capture_output=True,text=True,check=True)
            self.assertTrue(json.loads(compare.stdout)['selected_asar_declared_scope_complete'])
            result=json.loads((output/'diff.json').read_text())
            self.assertEqual(len(result['inventories']['css_tokens']['changed']),1)
            self.assertFalse(list(installed.rglob('*.pyc')))

if __name__=='__main__': unittest.main(verbosity=2)
