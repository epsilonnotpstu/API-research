#!/usr/bin/env python3
"""List operations whose response oracle is actually exercised in a baseline run.

An operation is eligible when the baseline exchanges contain at least one 2xx response
with a non-empty body for it. RESPONSE_ORACLE mutations on other operations can never
fire (the checker only validates 2xx bodies), which made Batch-2 results seed-dependent.

Usage:
  python3 eligible_ops.py BASELINE_RUN_DIR [--base-path /api] --out eligible.json
Output: JSON {"source_run": ..., "criterion": ..., "operations": [[path, method], ...]}
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy  # noqa: E402
from specmut import load_spec, operations, mutate_response, mutate_loose, LOOSE_KEYS  # noqa: E402

# Constraints our checker evaluates; 'format' (e.g. int64) is not enforced by conformance.py.
CHECKED_LOOSE_KEYS = (set(LOOSE_KEYS) - {'format'}) | {'required'}


def loose_effective(spec, path, method):
    """True if REQUEST_LOOSE would remove at least one request constraint the checker evaluates."""
    s = copy.deepcopy(spec)
    edits = []
    mutate_loose(s, path, method, s['paths'][path][method], edits)
    return any(e['pointer'].rsplit('/', 1)[-1] in CHECKED_LOOSE_KEYS and e.get('before') not in (None, False)
               for e in edits)


def oracle_mutable(spec, path, method):
    """True if RESPONSE_ORACLE would edit a 2xx response schema of this operation."""
    s = copy.deepcopy(spec)
    edits = []
    mutate_response(s, path, method, s['paths'][path][method], edits)
    return any('/responses/2' in e['pointer'] for e in edits)


def template_matcher(spec):
    pats = []
    for path, method, _ in operations(spec):
        rx = '^' + re.sub(r'\\\{[^}]+\\\}', '[^/]+', re.escape(path)) + '$'
        literal = path.count('{')
        pats.append((literal, path, method, re.compile(rx)))
    pats.sort(key=lambda x: x[0])  # literal paths before templated ones
    return pats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('run_dir')
    ap.add_argument('--base-path', default='')
    ap.add_argument('--min-count', type=int, default=1)
    ap.add_argument('--any-schema', action='store_true',
                    help='do not require a 2xx response schema that RESPONSE_ORACLE can edit')
    ap.add_argument('--fault', choices=('RESPONSE_ORACLE', 'REQUEST_LOOSE'), default='RESPONSE_ORACLE',
                    help='REQUEST_LOOSE: spec-only pool of operations with a checker-evaluated request constraint')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    run = Path(a.run_dir)
    spec_file = next(run.glob('spec.original.*'))
    spec = load_spec(str(spec_file))
    if a.fault == 'REQUEST_LOOSE':
        ops = sorted((p, m) for p, m, _ in operations(spec) if loose_effective(spec, p, m))
        Path(a.out).write_text(json.dumps({'source_run': run.name, 'spec': spec_file.name, 'fault': a.fault,
            'criterion': 'REQUEST_LOOSE removes >=1 checker-evaluated request constraint (' +
                         ', '.join(sorted(CHECKED_LOOSE_KEYS)) + ')',
            'operations': [list(k) for k in ops]}, indent=2), encoding='utf-8')
        print(f'{len(ops)} eligible operations -> {a.out}')
        return
    pats = template_matcher(spec)
    base = a.base_path.rstrip('/')
    counts = {}
    with open(run / 'exchanges.jsonl', encoding='utf-8') as f:
        for line in f:
            ex = json.loads(line)
            st = ex['response']['status']
            body = (ex['response'].get('body') or {})
            if not 200 <= st < 300 or not body.get('size'):
                continue
            p = ex['request']['path'].split('?')[0]
            if base and p.startswith(base):
                p = p[len(base):] or '/'
            m = ex['request']['method'].lower()
            for _, tpath, tmethod, rx in pats:
                if tmethod == m and rx.match(p):
                    counts[(tpath, tmethod)] = counts.get((tpath, tmethod), 0) + 1
                    break
    observed = sorted(k for k, v in counts.items() if v >= a.min_count)
    ops = observed if a.any_schema else [k for k in observed if oracle_mutable(spec, *k)]
    out = {'source_run': run.name, 'spec': spec_file.name,
           'criterion': f'>= {a.min_count} baseline 2xx response(s) with non-empty body'
                        + ('' if a.any_schema else ' AND an editable 2xx response schema'),
           'observed_without_editable_schema': [f'{m.upper()} {p}' for p, m in observed if (p, m) not in ops],
           'operations': [list(k) for k in ops], 'counts': {f'{m.upper()} {p}': counts[(p, m)] for p, m in ops}}
    Path(a.out).write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'{len(ops)} eligible operations -> {a.out}')


if __name__ == '__main__':
    main()
