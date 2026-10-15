#!/usr/bin/env python3
"""Verify short anchors and hashes without executing the target app."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('artifact_root',type=Path);p.add_argument('--ledger',type=Path,default=Path(__file__).resolve().parents[1]/'evidence/data/streaming-performance.json');a=p.parse_args();d=json.loads(a.ledger.read_text());cache={}
for rel,meta in d['files'].items():
 raw=(a.artifact_root/rel).read_bytes();assert hashlib.sha256(raw).hexdigest()==meta['sha256'],rel;cache[rel]=raw.decode()
for c in d['claims']:
 s=cache[c['file']];r=c['character_range'];assert s[r['start']:r['end']]==c['anchor'],c['id'];raw=s.encode();b=c['byte_range'];assert raw[b['start']:b['end']].decode()==c['anchor'],c['id']
print(f"Verified {len(d['claims'])} claims and {len(d['files'])} file hashes; target code was not executed.")
