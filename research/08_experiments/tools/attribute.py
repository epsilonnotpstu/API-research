"""Diff observed violation identities, keeping causal labels separate.

Usage: python3 attribute.py BASE MUT MANIFEST [--mode fresh|replay]
Default fresh mode requires manual labels. Explicit replay mode is the caller's
assertion that identical exchanges were checked against both specs; only then
may a changed oracle on a mutated operation use the manifest's expected label.
This does not establish the cause of fresh SUT behavior or SUT correctness.
"""
import argparse
from collections import Counter
import csv
import json
import sys


def load(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def attribute(baseline, mutated, manifest, mode='fresh'):
    if mode not in ('fresh', 'replay'):
        raise ValueError('mode must be replay or fresh')
    base_fp = {v['fingerprint']: v for v in baseline}
    mut_fp = {v['fingerprint']: v for v in mutated}
    base_counts = Counter(v['fingerprint'] for v in baseline)
    mut_counts = Counter(v['fingerprint'] for v in mutated)
    mutated_ops = {}
    for m in manifest['mutations']:
        mutated_ops[(m['method'].upper(), m['path'])] = m
        if m['fault'] == 'METHOD_SEM':
            for e in m['edits']:
                mutated_ops[(str(e['after']).upper(), m['path'])] = m
    rows = []
    for fp in sorted(set(base_fp) | set(mut_fp)):
        v = mut_fp.get(fp) or base_fp[fp]
        m = mutated_ops.get((v['method'], v['template']))
        if fp in mut_fp and fp not in base_fp:
            status = 'NEW'
            l1, l2 = ('NEEDS_MANUAL', '') if m else ('UNEXPLAINED', '')
            if m and mode == 'replay':
                l1, l2 = m['expected_L1'], m['expected_L2']
        elif fp in base_fp and fp not in mut_fp:
            status = 'VANISHED'
            l1, l2 = ('MASKED' if mode == 'replay' else 'NEEDS_MANUAL', '') if m else ('UNEXPLAINED', '')
        else:
            status, l1, l2 = 'PERSISTENT', 'NEEDS_MANUAL', ''
        rows.append({'fingerprint': fp, 'status': status, 'kind': v['kind'], 'method': v['method'],
                     'template': v['template'], 'http_status': v['status'], 'pointer': v['pointer'],
                     'op_mutated': bool(m), 'fault': m['fault'] if m else '', 'label_L1': l1, 'label_L2': l2,
                     'mode': mode, 'expected_if_injected': m['expected_L1'] if m else '',
                     'expected_L2_if_injected': m['expected_L2'] if m else '',
                     'baseline_occurrences': base_counts[fp], 'mutated_occurrences': mut_counts[fp]})
    return rows


def main(baseline_path, mutated_path, manifest_path, mode='fresh'):
    with open(manifest_path, encoding='utf-8') as f:
        rows = attribute(load(baseline_path), load(mutated_path), json.load(f), mode)
    w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]) if rows else ['fingerprint'])
    w.writeheader()
    w.writerows(rows)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('baseline')
    ap.add_argument('mutated')
    ap.add_argument('manifest')
    ap.add_argument('--mode', choices=('replay', 'fresh'), default='fresh')
    args = ap.parse_args()
    main(args.baseline, args.mutated, args.manifest, args.mode)
