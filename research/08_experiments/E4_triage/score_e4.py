#!/usr/bin/env python3
"""Pre-registered E4 scorer (Claude, 2026-11-15; written BEFORE any E4 labelling; see E4_PLAN.md).

Primary (E4 injected items, truth SPEC), per labeller file:
  SPEC recall = L1 in {SPEC, SPEC_PARTIAL}; wrong direction = L1 in {IMPL, IMPL_PARTIAL};
  abstain = L1 in {UNDECIDABLE, DEFERRED}; other = TEST/ENV/anything else.
Two-direction (E4 injected SPEC + E5 v3 primary targets IMPL), per method:
  classes SPEC*, IMPL*, ABSTAIN, OTHER. Per-class precision/recall over the two truth classes, and macro-F1 over
  {SPEC, IMPL}. Abstentions and OTHER count as misses (recall) and never as true positives. Also reports
  decided-accuracy (over non-abstain answers) and coverage.
  Method pairing:
  - M0 = synthetic all-IMPL;
  - M1 = E4 labels_Z1 + E5v3 labels_Z2 (zero-shot);
  - M2 = E4 labels_F1/F2 paired with E5v3 labels_D1/D2 (F1<->D1, F2<->D2, plus the swapped pairing; both reported).
Secondary (E4 decoys): exact agreement with final_L1; compatible = final BOTH matched by IMPL or SPEC with
  both_candidate true (M2 only; M1 has no flag) — reported, not used for success criteria.
Success criteria (E4_PLAN.md): P1 M2 wrong-direction on injected <= 10% for both labellers; P2 M2 macro-F1 > M0 and
  > M1 (each M2 pairing); P3 SPEC recall reported.
Usage: python3 score_e4.py   (reads files at fixed paths; missing label files are skipped with a note)
"""
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
E4_PKG = EXP / 'E2_labelling' / 'e4_blind'
E5_PKG = EXP / 'E2_labelling' / 'e5_blind_v3'
SPEC_SET, IMPL_SET, ABST = {'SPEC', 'SPEC_PARTIAL'}, {'IMPL', 'IMPL_PARTIAL'}, {'UNDECIDABLE', 'DEFERRED'}


def cls(l1):
    l1 = (l1 or '').strip().upper()
    return 'SPEC' if l1 in SPEC_SET else 'IMPL' if l1 in IMPL_SET else 'ABSTAIN' if l1 in ABST else 'OTHER'


def load(path):
    if not path.is_file():
        return None
    return {r['item_id']: r for r in csv.DictReader(open(path, newline=''))}


def two_direction(pred_spec_items, pred_impl_items):
    """pred_*: list of predicted classes for truth-SPEC and truth-IMPL items."""
    out = {}
    for c, truth_items, other_items in (('SPEC', pred_spec_items, pred_impl_items),
                                        ('IMPL', pred_impl_items, pred_spec_items)):
        tp = sum(p == c for p in truth_items)
        fp = sum(p == c for p in other_items)
        rec = tp / len(truth_items) if truth_items else 0.0
        prec = tp / (tp + fp) if tp + fp else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        out[c] = (prec, rec, f1)
    allp = pred_spec_items + pred_impl_items
    decided = [(p, t) for p, t in zip(allp, ['SPEC'] * len(pred_spec_items) + ['IMPL'] * len(pred_impl_items))
               if p in ('SPEC', 'IMPL')]
    acc = sum(p == t for p, t in decided) / len(decided) if decided else 0.0
    return out, (out['SPEC'][2] + out['IMPL'][2]) / 2, acc, len(decided) / len(allp)


def main():
    key = {r['item_id']: r for r in csv.DictReader(open(HERE / 'e4_key.csv', newline=''))}
    inj = sorted(i for i in key if key[i]['role'] == 'injected')
    dec = sorted(i for i in key if key[i]['role'] == 'decoy')
    k5 = {r['item_id']: r for r in csv.DictReader(open(EXP / 'E5_codemut' / 'blind_key_v3.csv', newline=''))}
    imp = sorted(i for i in k5 if k5[i].get('stratum') == 'primary')
    print(f'E4 injected n={len(inj)} (truth SPEC), decoys n={len(dec)}; E5v3 primary n={len(imp)} (truth IMPL)')
    e4 = {n: load(E4_PKG / f'labels_{n}.csv') for n in ('F1', 'F2', 'Z1')}
    e5 = {n: load(E5_PKG / f'labels_{n}.csv') for n in ('D1', 'D2', 'Z2')}
    rows = []
    print('== primary (E4 injected, truth SPEC)')
    for n, L in e4.items():
        if L is None:
            print(f'   {n}: (no labels file)')
            continue
        assert set(L) == set(key), f'{n}: item set mismatch'
        c = Counter(cls(L[i]['L1']) for i in inj)
        k = len(inj)
        print(f"   {n}: SPEC recall {c['SPEC']}/{k} ({c['SPEC'] / k:.0%}) | wrong-direction IMPL {c['IMPL']}/{k} "
              f"({c['IMPL'] / k:.0%}) | abstain {c['ABSTAIN']} | other {c['OTHER']}")
        by_fault = Counter((key[i]['fault'], cls(L[i]['L1'])) for i in inj)
        parts = []
        for f in sorted({key[i]['fault'] for i in inj}):
            parts.append(f + ': ' + ','.join(f'{cl}={by_fault[(f, cl)]}' for cl in ('SPEC', 'IMPL', 'ABSTAIN', 'OTHER')
                                              if by_fault[(f, cl)]))
        print('      by fault: ' + '; '.join(parts))
        ex = sum(L[i]['L1'].strip().upper() == key[i]['final_L1'].strip().upper() for i in dec)
        comp = sum((L[i]['L1'].strip().upper() == key[i]['final_L1'].strip().upper()) or
                   (key[i]['final_L1'] == 'BOTH' and cls(L[i]['L1']) in ('SPEC', 'IMPL') and
                    L[i].get('both_candidate', '').strip().lower() == 'true') for i in dec)
        print(f'      decoys (secondary): exact {ex}/{len(dec)}, compatible {comp}/{len(dec)}')
        rows.append({'set': 'E4', 'labeller': n, 'n_injected': k, 'spec_recall': c['SPEC'], 'wrong_impl': c['IMPL'],
                     'abstain': c['ABSTAIN'], 'other': c['OTHER'], 'decoy_exact': ex, 'decoy_compatible': comp})
    print('== two-direction (E4 injected SPEC + E5v3 primary IMPL)')
    methods = {'M0 all-IMPL': (['IMPL'] * len(inj), ['IMPL'] * len(imp))}
    if e4['Z1'] and e5['Z2']:
        methods['M1 Z1+Z2'] = ([cls(e4['Z1'][i]['L1']) for i in inj], [cls(e5['Z2'][i]['L1']) for i in imp])
    for a, b in (('F1', 'D1'), ('F2', 'D2'), ('F1', 'D2'), ('F2', 'D1')):
        if e4[a] and e5[b]:
            methods[f'M2 {a}+{b}'] = ([cls(e4[a][i]['L1']) for i in inj], [cls(e5[b][i]['L1']) for i in imp])
    res = {}
    for m, (ps, pi) in methods.items():
        per, mf1, acc, cov = two_direction(ps, pi)
        res[m] = mf1
        print(f"   {m:<12} macro-F1 {mf1:.3f} | SPEC P/R/F1 {per['SPEC'][0]:.2f}/{per['SPEC'][1]:.2f}/{per['SPEC'][2]:.2f}"
              f" | IMPL P/R/F1 {per['IMPL'][0]:.2f}/{per['IMPL'][1]:.2f}/{per['IMPL'][2]:.2f} | decided-acc {acc:.2f}"
              f" coverage {cov:.2f}")
        rows.append({'set': 'two-direction', 'labeller': m, 'macro_f1': round(mf1, 4), 'decided_acc': round(acc, 4),
                     'coverage': round(cov, 4)})
    print('== pre-registered criteria')
    m2e4 = [r for r in rows if r['set'] == 'E4' and r['labeller'] in ('F1', 'F2')]
    if len(m2e4) == 2:
        print('   P1 wrong-direction <=10% both:', all(r['wrong_impl'] / r['n_injected'] <= 0.10 for r in m2e4))
    m2 = {m: v for m, v in res.items() if m.startswith('M2')}
    if m2 and 'M1 Z1+Z2' in res:
        print('   P2 every M2 pairing > M0 and > M1:', all(v > res['M0 all-IMPL'] and v > res['M1 Z1+Z2'] for v in m2.values()),
              {k: round(v, 3) for k, v in res.items()})
    keys = sorted({k for r in rows for k in r})
    with open(HERE / 'e4_scores.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print('->', HERE / 'e4_scores.csv')


if __name__ == '__main__':
    main()
