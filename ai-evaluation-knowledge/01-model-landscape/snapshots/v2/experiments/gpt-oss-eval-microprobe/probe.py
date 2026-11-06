"""Offline component probes, NOT a model benchmark run.

Usage: python probe.py --source-dir /path/to/pinned/gpt-oss --output results.json
Source functions/classes are extracted with AST, without altering their bodies.
Network data reads are replaced with three synthetic rows. No model or judge is called.
Requires Python >=3.10 and numpy; other dependencies are not imported.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
import platform
import random
import re
from multiprocessing.pool import ThreadPool
from pathlib import Path
from types import SimpleNamespace
import numpy as np


def select(source: str, names: set[str], namespace: dict):
    tree = ast.parse(source)
    selected = []
    for node in tree.body:
        ids = [getattr(node, 'name', '')]
        if isinstance(node, ast.Assign):
            ids += [getattr(t, 'id', '') for t in node.targets]
        if names.intersection(ids):
            selected.append(node)
    assert len(selected) == len(names), (names, len(selected))
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)] + selected, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), '<pinned-upstream-ast>', 'exec'), namespace)
    return namespace


class Row(dict):
    def to_dict(self):
        return dict(self)


class Frame:
    def __init__(self, rows):
        self.rows = rows
    def iterrows(self):
        return enumerate([Row(x) for x in self.rows])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    manifest = json.loads((Path(__file__).parent / 'source-manifest.json').read_text())
    texts = {}
    for item in manifest['files']:
        data = (args.source_dir / item['path']).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert actual == item['blob_sha'], item['path']
        texts[Path(item['path']).name] = data.decode()
    out = {'scope': 'D4 component microprobe only; no model or judge; no benchmark score reproduced',
           'commit': manifest['commit'], 'python': platform.python_version(), 'numpy': np.__version__,
           'network_calls': 0, 'model_calls': 0, 'judge_calls': 0, 'cases': []}
    def record(name, observed, **extra):
        out['cases'].append(dict(name=name, observed=observed, **extra))

    ns = select(texts['abcd_grader.py'], {'_PATTERNS', 'extract_abcd'}, {'re': re})
    abcd = ns['extract_abcd']
    for text in ['Answer: A', 'Answer: A\nAfter checking, Answer: B', 'Answer: A\n\\boxed{B}', 'Because I cannot decide.', 'no answer', '', 'Dunno']:
        record('GPQA parser', abcd(text), input=text)

    ns = select(texts['aime_eval.py'], {'extract_boxed_text', 'normalize_number'}, {'re': re})
    for text in ['The answer is \\boxed{42}', 'No answer. Tried 3 cases.', '\\boxed{1,234}', '\\boxed{\\text{42}}', '\\boxed{-1}', '']:
        extracted = ns['extract_boxed_text'](text)
        try:
            final = int(extracted)
        except (ValueError, TypeError):
            final = None
        record('AIME parser', final, input=text, extracted=extracted)

    fixture = [dict(Question=q, question=q, answer='42') for q in ['synthetic one', 'ESPRESSO spectrograph, please synthetic', 'synthetic three']]
    fake_pandas = SimpleNamespace(read_csv=lambda *a, **k: Frame(fixture), read_json=lambda path, **k: Frame(fixture if '-I.' in path else []))
    for filename, classname in [('gpqa_eval.py', 'GPQAEval'), ('aime_eval.py', 'AIME25Eval')]:
        env = {'random': random, 'pandas': fake_pandas, 'Eval': object, 'normalize_number': ns['normalize_number']}
        cls = select(texts[filename], {classname}, env)[classname]
        for kwargs in [dict(num_examples=None, n_repeats=8), dict(num_examples=0, n_repeats=8), dict(num_examples=1, n_repeats=8), dict(num_examples=1, n_repeats=1)]:
            try:
                observed = {'example_count': len(cls(**kwargs).examples)}
            except Exception as e:
                observed = {'error': type(e).__name__, 'message': str(e)}
            record(classname+' constructor', observed, input=kwargs, synthetic_source_rows=3)
        if classname == 'GPQAEval':
            for n in [0, 1, 10]:
                record('GPQA debug filter', len(cls(debug=True, num_examples=n, n_repeats=1).examples), input={'debug': True, 'num_examples': n})

    ns = select(texts['report.py'], {'map_with_progress', '_compute_stat'}, {'os': os, 'ThreadPool': ThreadPool, 'np': np})
    # pbar=False avoids importing tqdm; original ThreadPool branch stays unchanged.
    old_debug = os.environ.pop('debug', None)
    try:
        try:
            observed = ns['map_with_progress'](lambda x: x, [], pbar=False)
        except Exception as e:
            observed = {'error': type(e).__name__, 'message': str(e)}
        record('empty progress map', observed, input=[])
    finally:
        if old_debug is not None:
            os.environ['debug'] = old_debug
    record('report std is population spread, not standard error', float(ns['_compute_stat']([0.0, 1.0, 0.0, 1.0], 'std')), input=[0, 1, 0, 1])

    ns = select(texts['healthbench_eval.py'], {'RubricItem', 'calculate_score', '_compute_clipped_stats'}, {'np': np})
    item = ns['RubricItem']
    scores = [ns['calculate_score']([item('synthetic reward', 1, []), item('synthetic penalty', -2, [])], [{'criteria_met': pos}, {'criteria_met': neg}]) for pos, neg in [(False, True), (True, False)]]
    record('HealthBench clips after averaging', float(ns['_compute_clipped_stats'](scores, 'mean')), raw_example_scores=scores, alternative_clip_each_then_mean=float(np.mean(np.clip(scores, 0, 1))))
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'cases': len(out['cases']), 'output': str(args.output), 'model_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
