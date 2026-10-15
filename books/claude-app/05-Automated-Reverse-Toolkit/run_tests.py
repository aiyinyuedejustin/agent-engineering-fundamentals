#!/usr/bin/env python3
"""Run original offline fixtures from any current directory."""
from pathlib import Path
import os
import subprocess
import sys

root = Path(__file__).resolve().parent
result = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py", "-v"], cwd=root, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
raise SystemExit(result.returncode)
