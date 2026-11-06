"""Optional source-only fetcher; no dataset access or source execution."""
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen
m=json.loads((Path(__file__).parent/'source-manifest.json').read_text())
root=Path(sys.argv[1])
for item in m['files']:
 url=f"https://raw.githubusercontent.com/{m['repository']}/{m['commit']}/{item['path']}"
 with urlopen(url,timeout=30) as response: data=response.read()
 assert hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob_sha'],item['path']
 path=root/item['path'];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
print(f"Verified {len(m['files'])} pinned source inputs")
