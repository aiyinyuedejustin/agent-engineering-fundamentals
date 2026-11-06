"""Offline component probes against hash-verified, AST-selected upstream bodies.

No upstream source or benchmark task content is embedded. Fake media metadata
and synthetic subtitle/options fixtures are intentionally not benchmark runs.
"""
import argparse
import ast
import copy as cp
import hashlib
import json
import logging
import math
import os
import os.path as osp
from pathlib import Path
import platform
import random as rd
import re
import string
import sys
import tempfile
import types

import numpy as np
import pandas as pd
from PIL import Image


def load_nodes(root, path, names, ns):
    tree = ast.parse((root / path).read_text(), filename=path)
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in names for t in node.targets
        ):
            selected.append(node)
    if len(selected) != len(names):
        raise ValueError(f'Missing requested AST nodes: {path}')
    exec(compile(ast.Module(body=selected, type_ignores=[]), path, 'exec'), ns)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).parent / 'source-manifest.json').read_text())
    for item in manifest['files']:
        data = (args.source_root / item['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == item['blob_sha'], item['path']
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']

    ns = dict(ast=ast, json=json, math=math, os=os, osp=osp, np=np, pd=pd,
              Image=Image, re=re, string=string, cp=cp, rd=rd,
              logger=logging.getLogger('probe'), VideoBaseDataset=object)
    load_nodes(args.source_root, 'vlmeval/dataset/videommev2.py', {
        'load_subtitle_jsonl', 'subtitle_concat_all', 'subtitle_between_timestamps', 'VideoMMEv2'
    }, ns)
    load_nodes(args.source_root, 'vlmeval/dataset/utils/videomme.py', {
        'extract_option', 'extract_characters_regex_v2'
    }, ns)
    load_nodes(args.source_root, 'vlmeval/dataset/utils/multiple_choice.py', {
        'build_choices', 'build_prompt', 'extract_answer_from_item'
    }, ns)
    load_nodes(args.source_root, 'vlmeval/utils/matching_util.py', {
        '_VERBOSE_ANSWER_RE', 'can_infer_option', 'can_infer_text', 'can_infer'
    }, ns)
    load_nodes(args.source_root, 'vlmeval/smp/vlm.py', {'build_option_str'}, ns)
    # The fixtures contain English only. Language detection is not under test.
    ns['cn_string'] = lambda _: False
    cases = []

    def check(name, actual, expected, scope):
        if isinstance(actual, tuple):
            actual = list(actual)
        assert actual == expected, (name, actual, expected)
        cases.append(dict(id=f'VMA{len(cases)+1:03}', name=name, actual=actual,
                          expected=expected, passed=True, scope=scope))

    class FakeFrame:
        shape = (1080, 1920, 3)

    class FakeVideo:
        # Ten frames at 1fps. No video file is opened and no pixel is decoded.
        def __init__(self, _): pass
        def __len__(self): return 10
        def get_avg_fps(self): return 1.0
        def __getitem__(self, index): return FakeFrame()

    old_decord = sys.modules.get('decord')
    sys.modules['decord'] = types.SimpleNamespace(VideoReader=FakeVideo)
    try:
        with tempfile.TemporaryDirectory(prefix='vlm-adapter-') as tmp:
            root = Path(tmp)
            (root / 'subtitle').mkdir()
            entries = [
                dict(text='early', start_time=0.0, end_time=0.5),
                dict(text='edge', start_time=1.5, end_time=2.0),
                dict(text='middle', start_time=2.2, end_time=2.5),
                dict(text='late', start_time=6.0, end_time=6.5),
            ]
            (root / 'subtitle/001.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in entries))
            paths = [str(root / f'frame{i}.jpg') for i in range(3)]
            for p in paths:
                Path(p).touch()  # Exercise cached-frame branch, not image decoding.
            ds = object.__new__(ns['VideoMMEv2'])
            ds.data_root = str(root)
            ds.nframe, ds.fps = 3, -1
            ds.resize_target_area = False
            ds.with_subtitle, ds.subtitle_interleave = True, True
            ds.response_prompt = ds.INSTRUCT_PROMPT
            ds.frame_paths = lambda _: paths
            ds.frame_paths_fps = lambda _, count: paths[:count]
            frames, indices, info = ds.save_video_frames('001')
            check('fixed-frame sampler excludes endpoints', indices, [2, 5, 7], 'sampler arithmetic with fake metadata')
            ds.nframe, ds.fps = -1, 0.05
            frames0, indices0, _ = ds.save_video_frames('001')
            check('sub-one-frame fps budget returns no frames', [frames0, indices0], [[], []], 'sampler arithmetic with fake metadata')
            ds.nframe, ds.fps = 3, -1
            check('subtitle ending exactly at boundary appears before boundary',
                  ns['subtitle_between_timestamps'](entries, 0, 2), 'early edge', 'original subtitle overlap helper')
            check('same boundary word also appears after boundary',
                  ns['subtitle_between_timestamps'](entries, 2, 5), 'edge middle', 'original subtitle overlap helper')
            line = dict(video='001', question='Which shape is shown?', options='A. square\nB. circle')
            msg = ds.build_prompt(line, video_llm=False)
            text = '\n'.join(m['value'] for m in msg if m['type'] == 'text')
            check('interleaved subtitles omit pre-first-frame early word', 'early' in text, False, 'frame prompt with synthetic subtitles and fake metadata')
            check('interleaved subtitles retain boundary and later words', all(x in text for x in ['edge', 'middle', 'late']), True, 'frame prompt with synthetic subtitles and fake metadata')
            ds.subtitle_interleave = False
            msg = ds.build_prompt(line, video_llm=False)
            text = '\n'.join(m['value'] for m in msg if m['type'] == 'text')
            check('non-interleaved subtitles retain early word', 'early' in text, True, 'frame prompt with synthetic subtitles and fake metadata')
            ds.subtitle_interleave = True
            msg = ds.build_prompt(line, video_llm=True)
            check('raw-video prompt emits resize dimensions despite resize flag false',
                  [msg[0]['resized_width'], msg[0]['resized_height']], [592, 336], 'raw-video prompt metadata, not model behavior')
            check('raw-video prompt passes requested frame count', msg[0]['nframes'], 3, 'raw-video prompt metadata')
            text = '\n'.join(m['value'] for m in msg if m['type'] == 'text')
            check('raw-video prompt concatenates early subtitle despite interleave flag true', 'early' in text, True, 'raw-video prompt with synthetic subtitles')
    finally:
        if old_decord is None:
            del sys.modules['decord']
        else:
            sys.modules['decord'] = old_decord

    extract = ns['extract_characters_regex_v2']
    for response, expected in [
        ('Final Answer: D', 'D'),
        ('Based on the video, Final Answer: D', 'B'),
        ('I first considered A, but Final Answer: D', 'A'),
        ('circle', ''),
    ]:
        check('v2 regex: ' + response, extract(response), expected, 'original letter parser on synthetic response')

    separate = dict(question='Which shape is shown?', options='A. square\nB. circle', prediction='circle')
    joined = dict(question='Which shape is shown?\nA. square\nB. circle', prediction='circle')
    sep_result = ns['extract_option'](None, separate, 'Video-MME')
    joined_result = ns['extract_option'](None, joined, 'Video-MME')
    check('fallback separate options column creates no choices', ns['build_choices'](separate), {}, 'original extract_option plus build_choices')
    check('fallback with no judge returns Z for separate options', sep_result, 'Z', 'original fallback chain with model=None; language detector stubbed')
    check('fallback joined question yields A/B choices', ns['build_choices'](joined), {'A': 'square', 'B': 'circle'}, 'original extract_option plus build_choices')
    check('fallback joined question recognizes free text circle', joined_result, 'B', 'original fallback chain with model=None; language detector stubbed')

    result = dict(
        scope='D4 component-only synthetic experiment; no model or benchmark reproduction',
        repository=manifest['repository'], commit=manifest['commit'],
        source_files_verified=len(manifest['files']),
        environment=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__),
        model_calls=0, judge_calls=0, network_calls=0, real_videos_opened=0,
        synthetic_cases=len(cases), cases=cases,
        limitations=[
            'Decord is replaced by a metadata-only fake; cached dummy frame paths avoid pixel decoding.',
            'English-language detection is stubbed false; relevant matching and choice-building bodies remain original.',
            'No Video-MME-v2 task text, options, media, model predictions, or official scores are copied or replayed.',
            'No API adapter, full runner, judge, or model implementation is executed.'
        ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(f'Passed {len(cases)} synthetic component probes; no model or judge calls.')


if __name__ == '__main__':
    main()
