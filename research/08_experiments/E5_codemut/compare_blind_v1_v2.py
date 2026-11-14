#!/usr/bin/env python3
"""Compare blind E5 labelling v1 (codebook v0.4, B1/B2) with v2 (codebook v0.5, C1/C2) item by item.

Coordinator only. Items are matched on (pair, seed, fingerprint); strata come from blind_key_v2.csv
(pre-registered in E5_BLIND_V2_PLAN.md). Output: e5_blind_v1_v2.csv and a per-stratum summary on stdout.
"""
import csv
import glob
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent / 'E2_labelling'
IMPLISH, WRONG = {'IMPL', 'IMPL_PARTIAL'}, {'SPEC', 'SPEC_PARTIAL', 'TEST'}


def load(path):
    return list(csv.DictReader(open(path, newline='')))


def labels(pattern):
    out = {}
    for f in sorted(glob.glob(str(pattern))):
        out[Path(f).stem.replace('labels_', '')] = {r['item_id']: r for r in load(f)}
    return out


k1 = {(r['pair'], r['seed'], r['fingerprint']): r['item_id'] for r in load(HERE / 'blind_key.csv')}
k2 = load(HERE / 'blind_key_v2.csv')
L1, L2 = labels(LAB / 'e5_blind' / 'labels_B*.csv'), labels(LAB / 'e5_blind_v2' / 'labels_C*.csv')
names = sorted(L1) + sorted(L2)


def short(r):
    return r['L1'] + ('+b' if r['both_candidate'].strip().lower() == 'true' else '')


rows = []
for k in sorted(k2, key=lambda r: r['item_id']):
    v1 = k1[(k['pair'], k['seed'], k['fingerprint'])]
    row = {'v2_item': k['item_id'], 'v1_item': v1, 'stratum': k['stratum'], 'pair': k['pair'].split('_')[0],
           'seed': k['seed'], 'change': k['change'], 'example_basis': k['example_basis']}
    for n in sorted(L1):
        row[n] = short(L1[n][v1])
    for n in sorted(L2):
        row[n] = short(L2[n][k['item_id']])
    rows.append(row)

with open(HERE / 'e5_blind_v1_v2.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

for st in ('primary', 'v1_comparable_only', 'target_other'):
    m = [r for r in rows if r['stratum'] == st]
    print(f'== {st} (n={len(m)})')
    for n in names:
        c = Counter(r[n].split('+')[0] for r in m)
        print(f'   {n}: IMPL* {sum(c[x] for x in IMPLISH)}, misattributed {sum(c[x] for x in WRONG)}, '
              f'UNDECIDABLE {c["UNDECIDABLE"]}  {dict(c)}')
print('== per item (targets)')
for r in rows:
    if r['stratum'] != 'decoy':
        print(f"   {r['v2_item']}/{r['v1_item']} {r['pair']:<24} s{r['seed']} {r['stratum']:<18} "
              + ' '.join(f'{n}={r[n]}' for n in names))
print('->', HERE / 'e5_blind_v1_v2.csv')
