#!/usr/bin/env python3
"""Pre-registered E6 scorer (Claude, 2026-11-15; written BEFORE any E6 labelling; see E6_PLAN.md).

Truth = developer fix direction (e6_key.csv truth_direction: SPEC or IMPL). Prediction classes:
SPEC (SPEC, SPEC_PARTIAL), IMPL (IMPL, IMPL_PARTIAL), ABSTAIN (UNDECIDABLE, DEFERRED), OTHER (TEST, ENV, ...).
Per labeller and per method (M1 = Y1, Y2; M2 = G1, G2; M0 = all-IMPL majority and all-SPEC):
  per-class precision/recall/F1 for SPEC and IMPL, macro-F1 over {SPEC, IMPL} (ABSTAIN/OTHER = misses, never TP),
  decided-accuracy (over SPEC/IMPL answers), coverage; popularity split (stars < 500 vs >= 500); Y1-Y2 and G1-G2
  agreement. Criteria: Q1 each M1 labeller macro-F1 > M0-majority macro-F1; Q2 report M2 vs M1 macro-F1 (no
  directional prediction); Q3 each M2 labeller decided-accuracy >= the mean M1 decided-accuracy.
Usage: python3 score_e6.py
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent / 'E2_labelling' / 'e6_blind'
sys.path.insert(0, str(HERE.parent / 'E4_triage'))
from score_e4 import cls, two_direction  # noqa: E402  (same class mapping and arithmetic as E4)


def main():
    key = {r['item_id']: r for r in csv.DictReader(open(HERE / 'e6_key.csv', newline=''))}
    # Stars for T42-sourced repos were unavailable offline; Claude fetched them (e6_repo_stars.csv, GitHub API).
    stars = {r['repo']: r['stars'] for r in csv.DictReader(open(HERE / 'e6_repo_stars.csv', newline=''))}
    for r in key.values():
        if not str(r['stars']).isdigit():
            r['stars'] = stars[r['repo']]
    spec_ids = sorted(i for i in key if key[i]['truth_direction'] == 'SPEC')
    impl_ids = sorted(i for i in key if key[i]['truth_direction'] == 'IMPL')
    print(f'E6 items {len(key)}: SPEC {len(spec_ids)}, IMPL {len(impl_ids)}')
    labels = {}
    for n in ('Y1', 'Y2', 'G1', 'G2'):
        p = PKG / f'labels_{n}.csv'
        if p.is_file():
            labels[n] = {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}
            assert set(labels[n]) == set(key), f'{n}: item set mismatch'
        else:
            print(f'   {n}: (no labels file)')
    methods = {'M0 all-IMPL': {i: 'IMPL' for i in key}, 'M0 all-SPEC': {i: 'SPEC' for i in key}}
    for n, L in labels.items():
        methods[f"{'M1' if n.startswith('Y') else 'M2'} {n}"] = {i: cls(L[i]['L1']) for i in key}
    res, rows = {}, []
    for m, pred in methods.items():
        for subset, ids in (('all', list(key)), ('stars<500', [i for i in key if int(key[i]['stars'] or 0) < 500]),
                            ('stars>=500', [i for i in key if int(key[i]['stars'] or 0) >= 500])):
            s = [pred[i] for i in ids if key[i]['truth_direction'] == 'SPEC']
            p = [pred[i] for i in ids if key[i]['truth_direction'] == 'IMPL']
            if not s or not p:
                continue
            per, mf1, acc, cov = two_direction(s, p)
            if subset == 'all':
                res[m] = (mf1, acc, cov)
            rows.append({'method': m, 'subset': subset, 'n': len(ids), 'macro_f1': round(mf1, 4), 'decided_acc': round(acc, 4),
                         'coverage': round(cov, 4), 'spec_recall': round(per['SPEC'][1], 4), 'impl_recall': round(per['IMPL'][1], 4),
                         'spec_precision': round(per['SPEC'][0], 4), 'impl_precision': round(per['IMPL'][0], 4)})
            print(f"   {m:<12} [{subset:<10} n={len(ids):>2}] macro-F1 {mf1:.3f} | SPEC P/R {per['SPEC'][0]:.2f}/{per['SPEC'][1]:.2f}"
                  f" | IMPL P/R {per['IMPL'][0]:.2f}/{per['IMPL'][1]:.2f} | decided-acc {acc:.2f} coverage {cov:.2f}")
    for a, b in (('Y1', 'Y2'), ('G1', 'G2')):
        if a in labels and b in labels:
            agree = sum(cls(labels[a][i]['L1']) == cls(labels[b][i]['L1']) for i in key)
            print(f'   agreement {a}-{b}: {agree}/{len(key)}')
    print('== pre-registered criteria')
    m1 = {m: v for m, v in res.items() if m.startswith('M1')}
    m2 = {m: v for m, v in res.items() if m.startswith('M2')}
    if m1:
        print('   Q1 each M1 macro-F1 > M0 all-IMPL:', all(v[0] > res['M0 all-IMPL'][0] for v in m1.values()),
              {m: round(v[0], 3) for m, v in m1.items()}, 'M0', round(res['M0 all-IMPL'][0], 3))
    if m1 and m2:
        print('   Q2 macro-F1 M2 vs M1:', {m: round(v[0], 3) for m, v in {**m2, **m1}.items()})
        mean_m1_acc = sum(v[1] for v in m1.values()) / len(m1)
        print('   Q3 each M2 decided-acc >= mean M1 decided-acc:', all(v[1] >= mean_m1_acc for v in m2.values()),
              {m: round(v[1], 3) for m, v in m2.items()}, 'mean M1', round(mean_m1_acc, 3))
    with open(HERE / 'e6_scores.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print('->', HERE / 'e6_scores.csv')


if __name__ == '__main__':
    main()
