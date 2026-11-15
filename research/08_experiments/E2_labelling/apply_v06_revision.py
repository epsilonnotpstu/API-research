#!/usr/bin/env python3
"""Build the codebook-v0.6 sensitivity view of the baseline final labels (Claude, 2026-11-15; supervisor-delegated).

The original final_labels_baseline_s1.csv is NOT modified and stays primary. This writes
final_labels_baseline_s1_v06.csv (= original + revised L1 for items accepted from the T36 review proposals) and
prints both distributions. Revisions: v06_revisions.csv.
"""
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / 'final_labels_baseline_s1.csv')))
rev = {r['item_id']: r for r in csv.DictReader(open(HERE / 'v06_revisions.csv'))}
for r in rows:
    x = rev.get(r['item_id'])
    r['v06_L1'] = x['v06_L1'] if x and x['decision'] == 'accept' else r['final_L1']
    r['v06_basis'] = x['basis'] if x else ''
with open(HERE / 'final_labels_baseline_s1_v06.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
order = ['SPEC', 'SPEC_PARTIAL', 'IMPL', 'BOTH', 'TEST', 'UNDECIDABLE', 'PENDING']
for col in ('final_L1', 'v06_L1'):
    c = Counter(r[col] for r in rows)
    dec = sum(c[k] for k in ('SPEC', 'SPEC_PARTIAL', 'IMPL', 'BOTH'))
    print(f"{col:<9} " + ' '.join(f'{k} {c[k]}' for k in order) +
          f" | decidable {dec}, BOTH share {c['BOTH']}/{dec} = {c['BOTH'] / dec:.1%}, TEST {c['TEST']}/{len(rows)}")
