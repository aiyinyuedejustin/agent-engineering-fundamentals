#!/usr/bin/env python3
"""Independent generated-HTML audit, using only Python's standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import sys

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.errors = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script','iframe','object','embed','form','input','button','svg','math','base','audio','video'}:
            self.errors.append('forbidden element: '+tag)
        for key, value in attrs.items():
            if key.lower().startswith('on') or key in {'srcdoc','style'}:
                self.errors.append('forbidden attribute: '+key)
            if key in {'href','src'}:
                split = urlsplit(value)
                if split.scheme and split.scheme not in {'https','http','mailto'}:
                    self.errors.append('forbidden URL scheme: '+value)
                if key == 'src' and split.scheme:
                    self.errors.append('nonlocal resource: '+value)
                if not split.scheme:
                    self.links.append(value)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('duplicate ID: '+attrs['id'])
            self.ids.add(attrs['id'])

root = Path(sys.argv[1]).resolve()
pages = {}
errors = []
for file in sorted(root.rglob('*.html')):
    parser = Audit()
    parser.feed(file.read_text())
    pages[file] = parser
    errors.extend(f'{file.relative_to(root)}: {e}' for e in parser.errors)
for file, parser in pages.items():
    for link in parser.links:
        split = urlsplit(link)
        target = (file.parent / unquote(split.path)).resolve() if split.path else file
        if not target.is_relative_to(root):
            errors.append(f'{file.relative_to(root)}: escaped root: {link}')
        elif not target.exists():
            errors.append(f'{file.relative_to(root)}: missing target: {link}')
        elif split.fragment and target in pages and unquote(split.fragment) not in pages[target].ids:
            errors.append(f'{file.relative_to(root)}: missing anchor: {link}')
print(json.dumps({'html_pages':len(pages),'errors':errors}, ensure_ascii=False, indent=2))
sys.exit(bool(errors))
