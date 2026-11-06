"""Fetch immutable public source inputs, never execute them.

Optional preparation for probe.py; uses the pinned commit and Git blob hash.
Usage: python fetch_inputs.py /tmp/ovis-probe-inputs
The checked-in artifact intentionally excludes copied upstream source files.
"""
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen

manifest = json.loads((Path(__file__).parent / 'source-manifest.json').read_text())
root = Path(sys.argv[1])
for item in manifest['files']:
    url = f"https://raw.githubusercontent.com/{manifest['repository']}/{manifest['commit']}/{item['path']}"
    with urlopen(url, timeout=30) as response:
        data = response.read()
    actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if actual != item['blob_sha']:
        raise ValueError(f"Source hash mismatch: {item['path']}")
    path = root / item['path']
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
print(f"Verified {len(manifest['files'])} source files at {manifest['commit']}")
