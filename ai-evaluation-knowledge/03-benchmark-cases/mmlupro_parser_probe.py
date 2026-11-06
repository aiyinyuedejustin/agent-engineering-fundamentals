"""Offline synthetic MMLU-Pro local parser/scorer behavior, without inference.

Usage: python mmlupro_parser_probe.py /path/to/pinned/evaluate_from_local.py
Only four reviewed functions are extracted; heavy model imports are not run.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import random
import re
import sys
import tempfile
from pathlib import Path

REVISION = "f418b116db00b065c2aea046518d8fcf74d39872"


def main() -> None:
    path = Path(sys.argv[1])
    source = path.read_bytes()
    tree = ast.parse(source)
    names = {"extract_answer", "extract_again", "extract_final", "save_res"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert len(nodes) == 4
    rng = random.Random(12345)
    ns = {"json": json, "random": rng, "re": re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    cases = [
        ("The answer is (B).", "B"),
        ("Initially the answer is (A), but after checking the answer is (D).", "A"),
        ("D", "D"),
        ("I cannot determine it.", "I"),
        ("not sure", None),
    ]
    parser_results = []
    with contextlib.redirect_stdout(io.StringIO()):
        for response, expected in cases:
            actual = ns["extract_answer"](response)
            assert actual == expected, (response, actual, expected)
            parser_results.append({"synthetic_output": response, "parsed": actual})
    fixture = [{"question_id": 0, "options": [f"synthetic option {i}" for i in range(9)],
                "answer_index": 0, "answer": "A", "pred": None,
                "model_outputs": "not sure"}]
    with tempfile.TemporaryDirectory(prefix="mmlupro-score-") as tmp:
        output = Path(tmp) / "result.json"
        repeated = [ns["save_res"](fixture, str(output))[0] for _ in range(12)]
        persisted = json.loads(output.read_text())
    assert set(repeated) == {0.0, 1.0}
    assert persisted[0]["pred"] is None
    print(json.dumps({
        "scope": "D4 only for isolated local parser/scorer with synthetic outputs, not model evaluation",
        "revision": REVISION, "source_sha256": hashlib.sha256(source).hexdigest(),
        "parser_results": parser_results,
        "same_unparsed_result_repeated_save_scores": repeated,
        "rng_seed_once": 12345, "stored_prediction_remains_null": True,
        "all_assertions_passed": True,
        "limitations": "Only evaluate_from_local.py at this revision; other backends have different policies. No published-score effect established."
    }, indent=2))


if __name__ == "__main__":
    main()
