"""Original offline diagnostic for a narrowly scoped IFEval scoring behavior.

Reads user-supplied, pinned upstream sources; does not fetch data or call models.
Only selected checker and scoring definitions are executed. This is not a
benchmark reproduction and uses a synthetic prompt unrelated to the test set.
"""
import argparse
import ast
import dataclasses
import hashlib
import json
import re
from pathlib import Path
from types import SimpleNamespace


def selected_defs(source, names):
    tree = ast.parse(source)
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
    if {n.name for n in nodes} != set(names):
        raise ValueError("Expected upstream definitions are missing")
    return ast.Module(body=nodes, type_ignores=[])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instructions", type=Path, required=True)
    parser.add_argument("--evaluation-lib", type=Path, required=True)
    args = parser.parse_args()
    instructions = args.instructions.read_text()
    evaluation = args.evaluation_lib.read_text()
    namespace = {"re": re, "dataclasses": dataclasses}
    exec(compile(selected_defs(instructions, ["Instruction", "KeywordChecker", "CommaChecker"]), str(args.instructions), "exec"), namespace)
    namespace["instructions_registry"] = SimpleNamespace(INSTRUCTION_DICT={
        "keywords:existence": namespace["KeywordChecker"],
        "punctuation:no_comma": namespace["CommaChecker"],
    })
    exec(compile(selected_defs(evaluation, ["OutputExample", "test_instruction_following_strict", "test_instruction_following_loose"]), str(args.evaluation_lib), "exec"), namespace)
    inp = SimpleNamespace(prompt="Synthetic diagnostic: include HEADER and no commas.",
                          instruction_id_list=["keywords:existence", "punctuation:no_comma"],
                          kwargs=[{"keywords": ["HEADER"]}, {}])
    response = "HEADER,\nok\nFOOTER,"
    output = {"scope": "component-only synthetic diagnostic; not model or benchmark score",
              "upstream_commit": "e6890f85757dd84e27ca6df2dd30651dafad28e0",
              "sha256": {"instructions.py": hashlib.sha256(instructions.encode()).hexdigest(),
                         "evaluation_lib.py": hashlib.sha256(evaluation.encode()).hexdigest()},
              "response": response}
    for mode in ["strict", "loose"]:
        result = namespace["test_instruction_following_" + mode](inp, {inp.prompt: response})
        output[mode] = {"follow_all": result.follow_all_instructions,
                        "per_instruction": result.follow_instruction_list}
    lines = response.split("\n")
    candidates = [response, "\n".join(lines[1:]).strip(), "\n".join(lines[:-1]).strip(), "\n".join(lines[1:-1]).strip()]
    candidates += [x.replace("*", "") for x in candidates]
    candidate_results = []
    for candidate in dict.fromkeys(candidates):
        result = namespace["test_instruction_following_strict"](inp, {inp.prompt: candidate})
        candidate_results.append({"candidate": candidate, "follow_all": result.follow_all_instructions,
                                  "per_instruction": result.follow_instruction_list})
    output["candidate_results"] = candidate_results
    output["any_single_candidate_satisfies_all"] = any(x["follow_all"] for x in candidate_results)
    assert output["strict"]["follow_all"] is False
    assert output["loose"]["follow_all"] is True
    assert output["any_single_candidate_satisfies_all"] is False
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
