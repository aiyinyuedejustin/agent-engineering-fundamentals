"""Shared path and shape checks for local, read-only CSS inputs."""
from pathlib import Path, PurePosixPath
import re


def source_bases(resources, asar_root=None):
    bases = {'ion': (Path(resources) / 'ion-dist').resolve()}
    if asar_root is not None:
        bases['asar'] = Path(asar_root).resolve()
    for scope, path in bases.items():
        if not path.is_dir():
            raise ValueError(f'Missing {scope} source directory: {path}')
    return bases


def source_path(logical_path, bases):
    """Reject absolute paths, traversal, unexpected namespaces and symlink escapes."""
    path = PurePosixPath(logical_path)
    if path.is_absolute() or len(path.parts) < 2 or '..' in path.parts or '\\' in logical_path:
        raise ValueError(f'Unsafe inventory source path: {logical_path}')
    scope, *parts = path.parts
    if scope not in ('ion', 'asar'):
        raise ValueError(f'Unknown inventory source namespace: {scope}')
    if scope not in bases:
        raise ValueError('Inventory uses asar sources; supply --asar-root')
    base = bases[scope].resolve()
    target = base.joinpath(*parts).resolve()
    if not target.is_relative_to(base):
        raise ValueError(f'Source path leaves its declared directory: {logical_path}')
    if target.suffix.lower() != '.css' or not target.is_file():
        raise ValueError(f'Source is not a readable CSS file: {logical_path}')
    return target


def validate_inventory(data):
    """Validate the minimal interchange contract, also accepting the original inventory."""
    if not isinstance(data, dict):
        raise ValueError('Inventory must be a JSON object')
    sources = data.get('sources')
    blocks = data.get('blocks')
    tokens = data.get('tokens')
    if not isinstance(sources, list) or not isinstance(blocks, list) or not isinstance(tokens, dict):
        raise ValueError('Inventory requires sources[], blocks[], and tokens{}')
    source_ids = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError('Each source must be an object')
        if not isinstance(source.get('id'), str) or not source['id'] or source['id'] in source_ids:
            raise ValueError('Source IDs must be unique strings')
        source_ids.add(source['id'])
        if not isinstance(source.get('path'), str) or not re.fullmatch('[0-9a-f]{64}', source.get('sha256', '')):
            raise ValueError('Each source needs a path and SHA-256')
    block_ids = set()
    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError('Each block must be an object')
        if not isinstance(block.get('id'), str) or not block['id'] or block['id'] in block_ids:
            raise ValueError('Block IDs must be unique strings')
        block_ids.add(block['id'])
        if block.get('source') not in source_ids:
            raise ValueError('Block references an unknown source')
        if not isinstance(block.get('selector'), str) or not isinstance(block.get('context'), list) or not all(isinstance(x, str) for x in block['context']):
            raise ValueError('Block requires a selector and string context list')
        check_offsets(block)
    for name, token in tokens.items():
        if not isinstance(token, dict):
            raise ValueError('Each token must be an object')
        if not isinstance(name, str) or not name.startswith('--') or not isinstance(token.get('taxonomy'), str):
            raise ValueError('Invalid token name or taxonomy')
        if type(token.get('reference_count')) is not int or token['reference_count'] < 0:
            raise ValueError('Token reference_count must be a nonnegative integer')
        if not isinstance(token.get('definitions'), list) or not token['definitions']:
            raise ValueError('Token requires at least one definition')
        for definition in token['definitions']:
            if not isinstance(definition, dict):
                raise ValueError('Each definition must be an object')
            if definition.get('block') not in block_ids or not isinstance(definition.get('value'), str):
                raise ValueError('Definition requires a known block and string value')
            check_offsets(definition)


def check_offsets(item):
    start, end = item.get('byte_start'), item.get('byte_end')
    if type(start) is not int or type(end) is not int or not 0 <= start < end:
        raise ValueError('Byte offsets must be nonnegative integer, end-exclusive ranges')
