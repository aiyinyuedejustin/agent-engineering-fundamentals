"""Original synthetic scorer diagnostic; no videos, model calls or test answers.

Use --source with the official standalone evaluator at the documented revision.
Only selected pure-function definitions are loaded, not the source module.
"""
import argparse
import ast
import hashlib
import json
import re
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    source = args.source.read_text()
    names = {"cal_relevance_rating", "cal_logic_rating", "extract_characters_regex_v2"}
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == names
    env = {"ast": ast, "re": re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(args.source), "exec"), env)
    patterns = [[1, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]]
    groups = []
    for pattern in patterns:
        groups.append({"correctness": pattern, "question_accuracy": 100 * sum(pattern) / 4,
                       "relevance_score": env["cal_relevance_rating"](pattern),
                       "logic_sequential_score": env["cal_logic_rating"](pattern, "[1, 2, 3, 4]"),
                       "logic_parallel_middle_score": env["cal_logic_rating"](pattern, "[1, [2, 3], 4]")})
    examples = ["D", "Final Answer: D", "Based on the sequence, the final step follows. Final Answer: D", "I choose D", "d"]
    parsed = [{"synthetic_response": x, "extracted": env["extract_characters_regex_v2"](x)} for x in examples]
    assert groups[0]["logic_sequential_score"] == 56.25
    assert groups[1]["logic_sequential_score"] == 0
    assert groups[2]["logic_sequential_score"] == 6.25
    assert parsed[2]["extracted"] == "B"
    print(json.dumps({"scope": "Synthetic pure-function experiment only; not benchmark reproduction",
                      "upstream_commit": "b2834bd4091d6234ccaf0fa1f149a7ef4eac5875",
                      "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                      "groups": groups, "parser_examples": parsed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
