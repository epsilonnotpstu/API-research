#!/usr/bin/env python3
"""Add the pre-registered `stratum` column to blind_key_v3.csv (coordinator only; Claude, 2026-11-15).

Rule (same as E5_BLIND_V2_PLAN.md):
- A target that matches a v2 item (same pair, seed and fingerprint) inherits its v2 stratum.
- Any other target is `primary` iff its kind is among the site's expected_signals in e5_summary.csv (kind=pair, default oracle)
  AND (change == NEW and signal_exceeds_noise == True for that site/seed, OR example_basis == SAME_REQ_DIFF_OUTCOME).
  Otherwise it is `target_other`.
- Decoys get `decoy`.
Also writes `v2_item` (the matched v2 id or empty). Rewrites blind_key_v3.csv in place; it is idempotent.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    v2 = {(r['pair'], r['seed'], r['fingerprint']): r for r in csv.DictReader(open(HERE / 'blind_key_v2.csv'))}
    summ = {}
    for r in csv.DictReader(open(HERE / 'e5_summary.csv')):
        if r['oracle'] == 'default' and r['kind'] == 'pair':
            summ[(r['site_id'], r['seed'])] = r
    path = HERE / 'blind_key_v3.csv'
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        m = v2.get((r['pair'], r['seed'], r['fingerprint']))
        r['v2_item'] = m['item_id'] if m else ''
        if r['role'] == 'decoy':
            r['stratum'] = 'decoy'
        elif m:
            r['stratum'] = m['stratum']
        else:
            site = r['pair'].split('_')[0]
            s = summ[(site, r['seed'])]
            kind = json.loads(r['fingerprint'])[3]
            expected = kind in json.loads(s['expected_signals'])
            strong = (r['change'] == 'NEW' and s['signal_exceeds_noise'] == 'True') or \
                r['example_basis'] == 'SAME_REQ_DIFF_OUTCOME'
            r['stratum'] = 'primary' if expected and strong else 'target_other'
    fields = [f for f in rows[0] if f not in ('stratum', 'v2_item')] + ['stratum', 'v2_item']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if r['role'] == 'target':
            print(r['item_id'], r['pair'].split('_')[0], r['seed'], r['stratum'], r['v2_item'] or '(new)')


if __name__ == '__main__':
    main()
