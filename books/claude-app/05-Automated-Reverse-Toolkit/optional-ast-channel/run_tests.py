#!/usr/bin/env python3
"""Original offline AST tests; explicit use of the host's test-only Acorn."""
import os
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parent
raise SystemExit(subprocess.call([sys.executable,'-B','-m','unittest','discover','-s',str(root/'tests'),'-p','test_*.py','-v'],
                                 cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}))
