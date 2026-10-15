#!/usr/bin/env python3
"""Validate UTF-8 static illustrations and serialize only allowlisted XML."""
import base64
import json
import re
import sys
import xml.etree.ElementTree as ET

TAGS = set('svg title desc metadata style rect text tspan path g line polygon polyline circle ellipse defs marker filter feGaussianBlur feOffset feFlood feComposite feMerge feMergeNode linearGradient radialGradient stop clipPath'.split())
ATTRS = set('id class x y x1 y1 x2 y2 cx cy r rx ry width height viewBox fill fill-opacity stroke stroke-width stroke-linecap stroke-linejoin stroke-dasharray opacity d points font-size font-weight font-family text-anchor dominant-baseline transform marker-end marker-start marker-mid refX refY markerWidth markerHeight markerUnits orient in in2 result stdDeviation dx dy flood-color flood-opacity operator filter role aria-labelledby aria-label style offset stop-color stop-opacity gradientUnits gradientTransform clip-path'.split())
CSS_PROPS = set('font-family font-size font-weight font-kerning fill stroke stroke-width text-anchor'.split())

def check_css(value, stylesheet=False):
    # Deliberately narrow: no escapes, comments, at-rules, URLs, functions or nested rules.
    if re.search(r'[\\@<>&()]|/\*|[\x00-\x08\x0b\x0c\x0e-\x1f]', value):
        raise ValueError('unsafe or unsupported SVG CSS')
    if stylesheet:
        # Forward-only parsing: an unanchored regex search can backtrack quadratically
        # on a long invalid selector with no opening brace.
        cursor = 0
        while cursor < len(value):
            while cursor < len(value) and value[cursor].isspace():
                cursor += 1
            if cursor == len(value):
                break
            start = value.find('{', cursor)
            end = value.find('}', start + 1) if start >= 0 else -1
            if start < 0 or end < 0 or not re.fullmatch(r'[a-zA-Z0-9_. ,#\s-]+', value[cursor:start]):
                raise ValueError('unsupported SVG selector or stylesheet')
            check_css(value[start+1:end])
            cursor = end + 1
    else:
        for declaration in value.split(';'):
            if not declaration.strip():
                continue
            prop, sep, val = declaration.partition(':')
            if not sep or prop.strip() not in CSS_PROPS or not re.fullmatch(r'[\w\s#.,%"\'\-]+', val):
                raise ValueError('unsupported SVG declaration')

def validate(data):
    # Inspect normalized text before XML parsing; byte-pattern checks miss UTF-16/32 DTDs.
    data = data.decode('utf-8-sig')
    if '\x00' in data:
        raise ValueError('SVG must be UTF-8 without null bytes')
    declaration = re.match(r'^\s*<\?xml\s+([^?]*)\?>', data)
    if declaration:
        encoding = re.search(r'encoding\s*=\s*["\']([^"\']+)["\']', declaration[1])
        if encoding and encoding[1].lower() not in {'utf-8', 'utf8'}:
            raise ValueError('SVG encoding must be UTF-8')
    # Graphviz's fixed public SVG declaration is metadata, not a reason to fetch a DTD.
    # Remove exactly this known declaration before parsing; reject every other DTD.
    data = re.sub(r'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1\.1//EN"\s+"http://www\.w3\.org/Graphics/SVG/1\.1/DTD/svg11\.dtd">', '', data)
    if re.search(r'<!DOCTYPE|<!ENTITY|<\?(?!xml\s)', data, re.I):
        raise ValueError('SVG declarations or processing instructions are prohibited')
    root = ET.fromstring(data)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('SVG root and namespace required')
    for element in root.iter():
        if not element.tag.startswith('{http://www.w3.org/2000/svg}'):
            raise ValueError('foreign namespace')
        tag = element.tag.split('}')[-1]
        if tag not in TAGS:
            raise ValueError('unsupported SVG element: ' + tag)
        for key, val in element.attrib.items():
            if key not in ATTRS and not re.fullmatch(r'data-[a-z0-9-]+', key):
                raise ValueError('unsupported SVG attribute: ' + key)
            if key == 'style':
                check_css(val)
            elif re.search(r'url\s*\(', val, re.I):
                if not re.fullmatch(r'url\(#[A-Za-z0-9_-]+\)', val):
                    raise ValueError('only local fragment SVG references supported')
            elif re.search(r'[\\<>]|(?:javascript|data|https?|file):', val, re.I):
                raise ValueError('prohibited SVG attribute value')
        if tag == 'style':
            if len(element):
                raise ValueError('nested SVG style element')
            check_css(element.text or '', stylesheet=True)
    # Serialize parsed/validated XML only: no DOCTYPE, processing instruction, or comment survives.
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    return ET.tostring(root, encoding='unicode')

if __name__ == '__main__':
    result = {}
    for item in json.load(sys.stdin):
        filename = item['path']
        try:
            result[filename] = {'svg': validate(base64.b64decode(item['data'], validate=True))}
        except (ValueError, ET.ParseError, OSError) as error:
            result[filename] = {'error': str(error)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
