#!/usr/bin/env python3
"""Final (adjudicated) L1 per fingerprint for the three pilot SUTs -> final_labels_baseline_s1.csv + summary.
final = supervisor_L1 if set; else the agreed L1 (A == B); else PENDING."""
import csv
from collections import Counter
SHEETS = {'scout-api': 'batch2_adjudication.csv', 'swagger-petstore': 'swagger-petstore_adjudication.csv',
          'market': 'market_adjudication.csv', 'cwa-verification': 'cwa-verification_adjudication.csv'}
out, summ = [], {}
for sut, f in SHEETS.items():
    rows = list(csv.DictReader(open(f, newline='')))
    for r in rows:
        if r['supervisor_note'].startswith('PENDING'):
            fin, src = 'PENDING', 'pending'
        elif r['supervisor_L1']:
            fin, src = r['supervisor_L1'], 'supervisor' if 'applied by Claude' not in r['supervisor_note'] else 'rule-applied'
        elif r['L1_agree'] == 'True':
            fin, src = r['A_L1'], 'agreed'
        else:
            fin, src = 'PENDING', 'pending'
        out.append({'sut': sut, 'item_id': r['item_id'], 'method': r['method'], 'template': r['template'],
                    'kind': r['kind'], 'status': r['status'], 'occurrences': r['occurrences'],
                    'final_L1': fin, 'source': src, 'A_L1': r['A_L1'], 'B_L1': r['B_L1'], 'note': r['supervisor_note']})
    summ[sut] = Counter(o['final_L1'] for o in out if o['sut'] == sut)
with open('final_labels_baseline_s1.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
labels = ['SPEC', 'SPEC_PARTIAL', 'IMPL', 'BOTH', 'TEST', 'UNDECIDABLE', 'PENDING']
print('| SUT | n | ' + ' | '.join(labels) + ' |')
print('|---' * (len(labels) + 2) + '|')
for sut, c in summ.items():
    print(f'| {sut} | {sum(c.values())} | ' + ' | '.join(str(c.get(l, 0)) for l in labels) + ' |')
tot = sum(summ.values(), Counter())
print(f'| **total** | {sum(tot.values())} | ' + ' | '.join(str(tot.get(l, 0)) for l in labels) + ' |')
print('source:', dict(Counter(o['source'] for o in out)))
