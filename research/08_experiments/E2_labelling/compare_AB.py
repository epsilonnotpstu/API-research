#!/usr/bin/env python3
"""Compare labeller A (Claude) and B (Codex) on one blind sheet; write an adjudication sheet.

Usage: python3 compare_AB.py BLIND.csv A_LABELS.csv B_LABELS.csv OUT_ADJUDICATION.csv
A and B files share the T15/T16 column layout (item_id, L1, L2, ..., both_candidate, rationale).
"""
import csv
import sys
from collections import Counter


def kappa(x, y):
    n = len(x)
    po = sum(p == q for p, q in zip(x, y)) / n
    cx, cy = Counter(x), Counter(y)
    pe = sum(cx[k] * cy[k] for k in set(cx) | set(cy)) / n / n
    return po, ((po - pe) / (1 - pe) if pe < 1 else float('nan'))


def truthy(v):
    return str(v).strip().lower() in ('true', 'yes', '1')


def main(blind, a_path, b_path, out):
    items = list(csv.DictReader(open(blind, newline='')))
    A = {r['item_id']: r for r in csv.DictReader(open(a_path, newline=''))}
    B = {r['item_id']: r for r in csv.DictReader(open(b_path, newline=''))}
    ids = [r['item_id'] for r in items]
    missing = [i for i in ids if i not in A or i not in B]
    if missing:
        raise SystemExit(f'missing labels for {missing}')
    xa, xb = [A[i]['L1'] for i in ids], [B[i]['L1'] for i in ids]
    po, k = kappa(xa, xb)
    same = [i for i in ids if A[i]['L1'] == B[i]['L1']]
    print(f'n={len(ids)}  L1 agreement {po:.3f}  kappa {k:.3f}')
    print('L2 agreement given same L1:', sum(A[i]['L2'] == B[i]['L2'] for i in same), '/', len(same))
    print('A', dict(Counter(xa)))
    print('B', dict(Counter(xb)))
    print('confusion', dict(Counter((A[i]['L1'], B[i]['L1']) for i in ids if A[i]['L1'] != B[i]['L1'])))
    ab, bb = {i for i in ids if truthy(A[i]['both_candidate'])}, {i for i in ids if truthy(B[i]['both_candidate'])}
    print(f'BOTH candidates A {len(ab)} B {len(bb)} both {len(ab & bb)}; differ: {sorted(ab ^ bb)}')
    meta = {r['item_id']: r for r in items}
    cols = ['item_id', 'method', 'template', 'status', 'kind', 'occurrences']
    rows = []
    for i in ids:
        a, b, m = A[i], B[i], meta[i]
        need = a['L1'] != b['L1'] or truthy(a['both_candidate']) != truthy(b['both_candidate'])
        rows.append({**{c: m[c] for c in cols},
                     'A_L1': a['L1'], 'A_L2': a['L2'], 'A_conf': a['confidence'], 'A_both': truthy(a['both_candidate']),
                     'A_rationale': a['rationale'], 'A_evidence': a['evidence_locators'],
                     'B_L1': b['L1'], 'B_L2': b['L2'], 'B_conf': b['confidence'], 'B_both': truthy(b['both_candidate']),
                     'B_root_cause': b['root_cause_id'], 'B_rationale': b['rationale'], 'B_evidence': b['evidence_locators'],
                     'L1_agree': a['L1'] == b['L1'], 'needs_adjudication': need,
                     'supervisor_L1': '', 'supervisor_L2': '', 'supervisor_note': ''})
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print('needs adjudication:', [r['item_id'] for r in rows if r['needs_adjudication']])


if __name__ == '__main__':
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
