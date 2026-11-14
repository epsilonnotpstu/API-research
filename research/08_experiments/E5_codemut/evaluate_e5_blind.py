#!/usr/bin/env python3
"""Score blind E5 labels against the hidden key (coordinator only).

Usage: python3 evaluate_e5_blind.py [LABELS.csv ...]   (default: ../E2_labelling/e5_blind/labels_B*.csv)
Truth: target items were caused by an injected code fault -> expected primary L1 IMPL (or IMPL_PARTIAL).
Reports per labeller: target recall of IMPL, what targets were called instead, decoy distribution,
and B1-B2 agreement on all items and on targets.
"""
import csv
import glob
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
key = {r['item_id']: r for r in csv.DictReader(open(HERE / 'blind_key.csv', newline=''))}
files = sys.argv[1:] or sorted(glob.glob(str(HERE.parent / 'E2_labelling' / 'e5_blind' / 'labels_B*.csv')))
labels = {}
for f in files:
    name = Path(f).stem.replace('labels_', '')
    labels[name] = {r['item_id']: r for r in csv.DictReader(open(f, newline=''))}
    L = labels[name]
    assert set(L) == set(key), f'{name}: item set mismatch ({len(L)} vs {len(key)})'
IMPLISH = {'IMPL', 'IMPL_PARTIAL'}
rows = []
for name, L in labels.items():
    t = [i for i in key if key[i]['role'] == 'target']
    d = [i for i in key if key[i]['role'] == 'decoy']
    hit = [i for i in t if L[i]['L1'] in IMPLISH]
    print(f'== {name}: targets labelled IMPL* {len(hit)}/{len(t)}; '
          f'targets as {dict(Counter(L[i]["L1"] for i in t))}; decoys as {dict(Counter(L[i]["L1"] for i in d))}')
    for i in t:
        if L[i]['L1'] not in IMPLISH:
            print(f'   miss {i} {key[i]["pair"][:26]} {key[i]["change"]}: {L[i]["L1"]} {L[i]["L2"]} c{L[i]["confidence"]} | {L[i]["rationale"][:110]}')
    for i in sorted(key):
        rows.append({'labeller': name, 'item_id': i, 'role': key[i]['role'], 'pair': key[i]['pair'], 'change': key[i]['change'],
                     'L1': L[i]['L1'], 'L2': L[i]['L2'], 'confidence': L[i]['confidence'], 'both_candidate': L[i]['both_candidate']})
names = sorted(labels)
if len(names) >= 2:
    a, b = labels[names[0]], labels[names[1]]
    agree = [i for i in key if a[i]['L1'] == b[i]['L1']]
    t_agree = [i for i in key if key[i]['role'] == 'target' and a[i]['L1'] == b[i]['L1']]
    nt = sum(key[i]['role'] == 'target' for i in key)
    print(f'== {names[0]} vs {names[1]}: L1 agreement {len(agree)}/{len(key)}; on targets {len(t_agree)}/{nt}')
out = HERE / 'e5_blind_scores.csv'
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print('->', out)
