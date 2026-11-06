"""Synthetic probes of pinned Ovis repository helpers; no weights or network.

The NumPy tensor stand-in only implements orchestration operations used here.
It does not model torch numerics, generation, vision encoding or tokenization.
"""
import argparse
import ast
import hashlib
import json
import logging
import math
from pathlib import Path
import platform
import types
import numpy as np
from PIL import Image


class Tensor:
    def __init__(self, values): self.a = np.asarray(values)
    @property
    def shape(self): return self.a.shape
    def to(self, *args, **kwargs): return self
    def __getitem__(self, key): return Tensor(self.a[key])
    def __contains__(self, item): return item in self.a
    def tolist(self): return self.a.tolist()
    def prod(self): return self.a.prod()
    def unsqueeze(self, axis): return Tensor(np.expand_dims(self.a, axis))


def selected_class(source, original, methods, ns):
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == original)
    nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in methods]
    assert len(nodes) == len(methods)
    # Preserve method ASTs, but instantiate only an inert object shell.
    new_cls = ast.ClassDef(name=original, bases=[], keywords=[], body=nodes, decorator_list=[])
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), new_cls], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), 'verified-original-methods', 'exec'), ns)
    return ns[original]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads((Path(__file__).parent / 'source-manifest.json').read_text())
    for record in manifest['files']:
        data = (args.source_root / record['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == record['sha256']
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == record['blob_sha']
    code = (args.source_root / 'ovis/model/modeling_ovis.py').read_text()
    torch = types.SimpleNamespace(
        tensor=lambda v, **kw: Tensor(v),
        cat=lambda values, dim=0: Tensor(np.concatenate([v.a for v in values], axis=dim)),
        no_grad=lambda: (lambda func: func), long=np.int64,
    )
    ns = dict(math=math, logging=logging, np=np, torch=torch,
              VISUAL_ATOM_ID=-300, IGNORE_ID=-100)
    Visual = selected_class(code, 'VisualTokenizer', {'smart_resize', 'preprocess'}, ns)
    Ovis = selected_class(code, 'Ovis', {'_merge_inputs', 'chat'}, ns)
    cases = []

    def check(name, actual, expected, scope):
        if isinstance(actual, tuple): actual = list(actual)
        assert actual == expected, (name, actual, expected)
        cases.append(dict(id=f'OVP{len(cases)+1:03}', name=name, actual=actual,
                          expected=expected, passed=True, scope=scope))

    resize = Visual.smart_resize
    defaults = dict(factor=32, min_pixels=448**2, max_pixels=1344*1792)
    check('4K dimensions are downscaled under direct preprocess default cap',
          resize(2160, 3840, **defaults), [1152, 2048], 'original resize arithmetic')
    check('small square is upscaled to minimum area',
          resize(100, 100, **defaults), [448, 448], 'original resize arithmetic')
    check('non-multiple dimensions round to patch-stride alignment',
          resize(1080, 1920, **defaults), [1088, 1920], 'original resize arithmetic')
    check('oversized aspect ratio clamps instead of preserving original ratio',
          resize(32, 100000, **defaults), [32, 6400], 'original resize arithmetic, extreme aspect fixture')
    check('small-dimension branch can yield zero after later flooring',
          resize(1, 10000, **defaults), [0, 155168], 'boundary arithmetic only; no image processor invocation')
    shape = resize(100, 200, factor=32, min_pixels=448**2, max_pixels=448**2)
    check('equal min-max target may be exceeded after ceil alignment',
          [list(shape), math.prod(shape), math.prod(shape) > 448**2],
          [[320, 640], 204800, True], 'original resize arithmetic with equal min/max budget')

    class Processor:
        def __init__(self): self.calls = []
        def preprocess(self, image, size, return_tensors):
            self.calls.append(dict(original_size=list(image.size), requested_size=dict(size)))
            return {'pixel_values': np.zeros((1, 3, size['height'], size['width']), dtype=np.float32)}

    vis = Visual()
    vis.vit = types.SimpleNamespace(config=types.SimpleNamespace(patch_size=16, hidden_stride=2, temporal_patch_size=1))
    vis.image_processor = Processor()
    frame = Image.new('RGB', (200, 100))
    other = Image.new('RGB', (100, 200))
    pix, grid = vis.preprocess(image=frame, min_pixels=32**2, max_pixels=64**2)
    check('single-image patch packing', [list(pix.shape), grid.tolist()], [[8, 768], [[1, 2, 4]]], 'original packing with zero-valued processor output')
    pix, grid = vis.preprocess(video=[frame, other], min_pixels=32**2, max_pixels=64**2)
    check('mixed-aspect frames use dimensions of first frame',
          vis.image_processor.calls[-2:],
          [dict(original_size=[200, 100], requested_size=dict(height=32, width=64)),
           dict(original_size=[100, 200], requested_size=dict(height=32, width=64))],
          'processor call arguments, not actual pixel interpolation')
    check('video area budget applies to each supplied frame', [list(pix.shape), grid.tolist()], [[16, 768], [[2, 2, 4]]], 'original video packing with two synthetic frames')
    obj = Ovis()
    obj.visual_tokenizer = vis
    ids, labels = obj._merge_inputs([7, -201, 9], [-100]*3, [1], [grid], -303, -304)
    check('default temporal size gives four visual atoms for two frames', ids.count(-300), 4, 'original placeholder expansion, released temporal size1')

    # The released config uses temporal_patch_size=1. These are explicit
    # non-default boundary probes, not bugs demonstrated in that checkpoint.
    vis.vit.config.temporal_patch_size = 2
    pix2, grid2 = vis.preprocess(video=[frame]*3, min_pixels=32**2, max_pixels=64**2)
    check('temporal size2 pads three frames to four', [list(pix2.shape), grid2.tolist()], [[16, 1536], [[2, 2, 4]]], 'non-default temporal size2 packing')
    ids2, _ = obj._merge_inputs([7,-201,9],[-100]*3,[1],[grid2],-303,-304)
    check('non-default temporal size2 divides atom count again',
          [ids2.count(-300), pix2.shape[0]//4], [2,4], 'non-default temporal size2 placeholder count versus spatial-merge count; no model forward')
    vis.vit.config.temporal_patch_size = 3
    try:
        vis.preprocess(video=[frame]*2, min_pixels=32**2, max_pixels=64**2)
    except ValueError as exc:
        actual = type(exc).__name__
    else:
        actual = 'no exception'
    check('temporal size3 and two frames fail reshape after padding', actual, 'ValueError', 'non-default temporal size3 boundary')
    vis.vit.config.temporal_patch_size = 1

    # Test chat orchestration with fixed token fixtures, not a language model.
    class Tokenizer:
        pad_token_id = 0
        def __call__(self, text, **kw):
            # Three synthetic bridge tokens, ending with the real delimiter ID.
            return types.SimpleNamespace(input_ids=Tensor([[88,89,151668]]))
        def decode(self, ids, **kw):
            return ' '.join(str(i) for i in ids if i not in [151668,151645])

    def fake_model(outputs):
        m = Ovis()
        m.device, m.dtype = 'cpu', 'synthetic'
        m.text_tokenizer = Tokenizer()
        m.calls = []
        m.preprocess_inputs = lambda *a, **kw: ('prompt',Tensor([[1,2]]),None,None)
        queue = list(outputs)
        def gen(inputs, **kw):
            m.calls.append(dict(max_new_tokens=kw['max_new_tokens'], input_length=inputs.shape[1]))
            return Tensor([queue.pop(0)])
        m.generate = gen
        return m

    m = fake_model([[10,11,12],[20,151645]])
    response, thinking, history = m.chat('synthetic request',enable_thinking=True,thinking_budget=3,max_new_tokens=10)
    check('forced bridge consumes remaining answer budget', m.calls,
          [dict(max_new_tokens=3,input_length=2),dict(max_new_tokens=4,input_length=8)],
          'chat control flow with fixed token outputs and three-token bridge')
    check('history retains final response, not synthetic thinking tokens', history['conversations'][-1]['value'], '20', 'chat history assembly with token fixtures')
    m = fake_model([[10,151668],[20,151645]])
    m.chat('synthetic request',enable_thinking=True,thinking_budget=3,max_new_tokens=10)
    check('existing think delimiter avoids bridge insertion', m.calls,
          [dict(max_new_tokens=3,input_length=2),dict(max_new_tokens=8,input_length=4)],
          'chat control flow with preexisting delimiter')
    m = fake_model([[10,151645]])
    m.chat('synthetic request',enable_thinking=True,thinking_budget=3,max_new_tokens=10)
    check('end-of-message in phase1 skips phase2', len(m.calls), 1, 'chat control flow with fixed end token')
    m = fake_model([[10,11,12]])
    short_response, short_thinking, _ = m.chat('synthetic request',enable_thinking=True,thinking_budget=3,max_new_tokens=4)
    check('bridge may exceed total budget when insufficient margin',
          [len(m.calls), short_thinking, short_response], [1, '10 11 12 88 89', ''],
          'undersized total-budget boundary; HF documentation recommends a margin')
    m = fake_model([[10,11]])
    m.chat('synthetic request',enable_thinking=True,thinking_budget=None,max_new_tokens=10)
    check('no thinking budget means one total-budget generation call', m.calls,
          [dict(max_new_tokens=10,input_length=2)], 'chat control flow with budget omitted')

    result = dict(
        scope='D4 synthetic component-only; GitHub repository implementation, not HF remote-code model execution',
        repository=manifest['repository'], commit=manifest['commit'], source_files_verified=len(manifest['files']),
        environment=dict(python=platform.python_version(),numpy=np.__version__,torch='not installed; explicit NumPy stand-in'),
        cases=cases, synthetic_cases=len(cases), model_calls=0, judge_calls=0, network_calls=0,
        real_task_images_processed=0,
        limitations=[
            'No weights, transformer, flash attention, actual tokenizer, torch backend, or model generation executed.',
            'Pixel processor returns zero arrays; packing executes but interpolation and vision quality are not tested.',
            'Temporal sizes2/3 are outside released checkpoint config, whose temporal size is1.',
            'HF remote code differs from GitHub interface; this executable study is pinned to GitHub only.',
            'No benchmark score, actual image task answer or image fidelity reproduced.'
        ])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(f'Passed {len(cases)} synthetic Ovis component probes; no model calls.')


if __name__=='__main__': main()
