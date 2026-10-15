#!/usr/bin/env python3
"""Reproduce unresolved lexical false positives; NOT a correctness test.

Original synthetic bytes only. No target files, JavaScript execution, network,
input arguments, or filesystem writes. Exit 0 means documented wrong behavior
was reproduced; exit 2 means the characterization changed and needs review.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from toolkit.literals import literal_candidates, load_rules

CASES = [
    ('nested-template-raw-text', b'const t = `${`checkGate("synthetic_false")`}`;'),
    ('string-keyword-confuses-division', b'''const n = "return" / 2; const s = "/checkGate('synthetic_false'); /"; const q = /x/;'''),
    ('regex-after-arrow', b'const r = () => /checkGate("synthetic_false")/;'),
    ('regex-after-logical-and', b'const r = true && /checkGate("synthetic_false")/;'),
    ('regex-after-control-header', b'if (true) /checkGate("synthetic_false")/.test("text");'),
]


def main():
    results = []
    for name, data in CASES:
        records = literal_candidates(data, load_rules())
        flags = [record for record in records if record['category'] == 'flags']
        reproduced = len(flags) == 1 and flags[0]['key'] == 'synthetic_false'
        results.append({
            'case': name,
            'input_origin': 'newly-authored-synthetic',
            'desired_false_candidate_count': 0,
            'observed_false_candidate_count': len(flags),
            'status': 'expected-limitation-reproduced' if reproduced else 'characterization-changed-needs-review',
            'fixed': False if reproduced else None,
        })
    reproduced_all = all(item['status'] == 'expected-limitation-reproduced' for item in results)
    report = {
        'schema': 'original-known-lexical-limitations/v1',
        'purpose': 'Characterize unresolved false positives; never interpret as correctness success.',
        'outcome': 'expected-limitations-reproduced' if reproduced_all else 'characterization-changed-needs-review',
        'target_javascript_executed': False,
        'semantic_completeness_proven': False,
        'results': results,
        'reproduced_unresolved_limitations': sum(item['fixed'] is False for item in results),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if reproduced_all else 2


if __name__ == '__main__':
    raise SystemExit(main())
