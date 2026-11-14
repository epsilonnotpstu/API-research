#!/usr/bin/env python3
"""Score blind E5 labels against the hidden key (coordinator only).

Usage: python3 evaluate_e5_blind.py [--key KEY] [--out OUT] [LABELS.csv ...]
  v1 default: blind_key.csv, ../E2_labelling/e5_blind/labels_B*.csv -> e5_blind_scores.csv
  v2: --key blind_key_v2.csv --out e5_blind_v2_scores.csv ../E2_labelling/e5_blind_v2/labels_C*.csv
If the key has a `stratum` column (v2), also reports the pre-registered metrics per stratum
(E5_BLIND_V2_PLAN.md): IMPL* rate, misattribution (SPEC/SPEC_PARTIAL/TEST), UNDECIDABLE (+both).
Truth: target items were caused by an injected code fault -> expected primary L1 IMPL (or IMPL_PARTIAL).
Reports per labeller: target recall of IMPL, what targets were called instead, decoy distribution,
and B1-B2 agreement on all items and on targets.
"""
import argparse
import csv
import glob
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--key', default=str(HERE / 'blind_key.csv'))
ap.add_argument('--out', default=str(HERE / 'e5_blind_scores.csv'))
ap.add_argument('labels', nargs='*')
args = ap.parse_args()
key = {r['item_id']: r for r in csv.DictReader(open(args.key, newline=''))}
files = args.labels or sorted(glob.glob(str(HERE.parent / 'E2_labelling' / 'e5_blind' / 'labels_B*.csv')))
labels = {}
for f in files:
    name = Path(f).stem.replace('labels_', '')
    labels[name] = {r['item_id']: r for r in csv.DictReader(open(f, newline=''))}
    L = labels[name]
    assert set(L) == set(key), f'{name}: item set mismatch ({len(L)} vs {len(key)})'
IMPLISH = {'IMPL', 'IMPL_PARTIAL'}
WRONG = {'SPEC', 'SPEC_PARTIAL', 'TEST'}
STRATA = sorted({r.get('stratum', '') for r in key.values()} - {'', 'decoy'})
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
    for st in STRATA:
        m = [i for i in key if key[i]['stratum'] == st]
        u = [i for i in m if L[i]['L1'] == 'UNDECIDABLE']
        ub = [i for i in u if L[i]['both_candidate'].strip().lower() == 'true']
        print(f'   [{st} n={len(m)}] IMPL* {sum(L[i]["L1"] in IMPLISH for i in m)}, '
              f'misattributed {sum(L[i]["L1"] in WRONG for i in m)}, UNDECIDABLE {len(u)} (both {len(ub)}), '
              f'other {sum(L[i]["L1"] not in IMPLISH | WRONG | {"UNDECIDABLE"} for i in m)}')
    for i in sorted(key):
        rows.append({'labeller': name, 'item_id': i, 'role': key[i]['role'], 'pair': key[i]['pair'], 'change': key[i]['change'],
                     'L1': L[i]['L1'], 'L2': L[i]['L2'], 'confidence': L[i]['confidence'], 'both_candidate': L[i]['both_candidate'],
                     **({'stratum': key[i]['stratum']} if 'stratum' in key[i] else {})})
names = sorted(labels)
if len(names) >= 2:
    a, b = labels[names[0]], labels[names[1]]
    agree = [i for i in key if a[i]['L1'] == b[i]['L1']]
    t_agree = [i for i in key if key[i]['role'] == 'target' and a[i]['L1'] == b[i]['L1']]
    nt = sum(key[i]['role'] == 'target' for i in key)
    print(f'== {names[0]} vs {names[1]}: L1 agreement {len(agree)}/{len(key)}; on targets {len(t_agree)}/{nt}')
out = Path(args.out)
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print('->', out)
