#!/usr/bin/env python3
"""Pre-registered E7 scorer (Claude, 2026-11-15; written BEFORE any E7 coding; see E7_PLAN.md).

Inputs
  key    : ../E7_mining/key/e7_key.csv  (item_id, set, stars, truth_direction, confidence, cross_item_flag, ...)
  codes  : ../E2_labelling/e7_blind/codes_C1.csv, codes_C2.csv (item_id, divergence_kind, contract_specificity, ...)
  adjud. : adjudication.csv (item_id, field, value) -- Claude's blind adjudication of C1/C2 disagreements
Final code per field = C1 value if C1 == C2, else the adjudication value (must exist).
Primary (H-E7-1): set=new, kind in {DELIBERATE, ACCIDENTAL}, truth in {SPEC, IMPL};
  one-sided Fisher exact P(SPEC|DELIBERATE) > P(SPEC|ACCIDENTAL), alpha 0.05; Wilson 95% CIs per arm;
  Haldane-corrected Woolf 95% CI for the odds ratio; confirmatory only if each arm has >= 8 items.
Reliability: Cohen's kappa C1-C2 on divergence_kind (3-class); kappa < 0.40 -> flagged "unreliable coding".
Secondary (H-E7-2): same with contract_specificity GENERIC vs SPECIFIC.
Sensitivity: (a) confidence == 3, (b) no cross_item_flag, (c) C1-C2 agreed items only (no adjudication).
Exploratory: set=e6_exploratory, same tables (not pooled). Popularity split stars <500 / >=500 (descriptive).
Triage rule (descriptive): DELIBERATE -> SPEC, ACCIDENTAL -> IMPL, UNCLEAR -> abstain (miss); macro-F1 vs majority.
Usage: python3 score_e7.py [--root DIR]   (DIR overrides the 08_experiments root; used by the self-test)
"""
import argparse
import csv
import math
import sys
from pathlib import Path

KINDS = ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR')
SPECS = ('SPECIFIC', 'GENERIC', 'UNCLEAR')
ALPHA, MIN_ARM, KAPPA_MIN = 0.05, 8, 0.40


def read(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


def fisher_one_sided(a, b, c, d):
    """P(X >= a) under the hypergeometric with fixed margins; table [[a, b], [c, d]], rows = arm1/arm2, cols = SPEC/IMPL."""
    r1, c1, n = a + b, a + c, a + b + c + d
    denom = math.comb(n, c1)
    return sum(math.comb(r1, x) * math.comb(n - r1, c1 - x) for x in range(a, min(r1, c1) + 1)) / denom


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


def woolf_or(a, b, c, d, z=1.959964):
    a, b, c, d = (x + 0.5 for x in (a, b, c, d))
    o = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return o, math.exp(math.log(o) - z * se), math.exp(math.log(o) + z * se)


def kappa(x, y, cats):
    n = len(x)
    if n == 0:
        return float('nan')
    po = sum(i == j for i, j in zip(x, y)) / n
    pe = sum((x.count(c) / n) * (y.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def table(items, field, arm1, arm2):
    t = {arm: {'SPEC': 0, 'IMPL': 0} for arm in (arm1, arm2)}
    for it in items:
        if it[field] in t and it['truth'] in ('SPEC', 'IMPL'):
            t[it[field]][it['truth']] += 1
    a, b, c, d = t[arm1]['SPEC'], t[arm1]['IMPL'], t[arm2]['SPEC'], t[arm2]['IMPL']
    return a, b, c, d


def report_table(name, items, field, arm1, arm2, confirmatory=False):
    a, b, c, d = table(items, field, arm1, arm2)
    p = fisher_one_sided(a, b, c, d)
    o, lo, hi = woolf_or(a, b, c, d)
    w1, w2 = wilson(a, a + b), wilson(c, c + d)
    enough = (a + b) >= MIN_ARM and (c + d) >= MIN_ARM
    f = lambda k, n: f'{k}/{n}={k / n:.2f}' if n else '0/0'
    print(f'   [{name}] {arm1}: SPEC {f(a, a + b)} CI[{w1[0]:.2f},{w1[1]:.2f}] | {arm2}: SPEC {f(c, c + d)} '
          f'CI[{w2[0]:.2f},{w2[1]:.2f}] | OR {o:.2f} [{lo:.2f},{hi:.2f}] | Fisher one-sided p={p:.4f}'
          + (f" | {'PASS' if p < ALPHA else 'FAIL'}{'' if enough else ' (arm < 8: descriptive only)'}" if confirmatory else ''))
    return {'analysis': name, 'field': field, 'arm1': arm1, 'arm1_spec': a, 'arm1_impl': b, 'arm2': arm2, 'arm2_spec': c,
            'arm2_impl': d, 'odds_ratio': round(o, 4), 'or_lo': round(lo, 4), 'or_hi': round(hi, 4), 'fisher_p': round(p, 6),
            'enough_per_arm': enough}


def rule_scores(items):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'E4_triage'))
    from score_e4 import two_direction  # same macro-F1 arithmetic as E4/E6
    pred = {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}
    s = [pred.get(it['kind'], 'ABSTAIN') for it in items if it['truth'] == 'SPEC']
    p = [pred.get(it['kind'], 'ABSTAIN') for it in items if it['truth'] == 'IMPL']
    if not s or not p:
        return None
    per, mf1, acc, cov = two_direction(s, p)
    maj = 'IMPL' if len(p) >= len(s) else 'SPEC'
    _, mmf1, macc, _ = two_direction([maj] * len(s), [maj] * len(p))
    return mf1, acc, cov, per, maj, mmf1, macc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(Path(__file__).resolve().parent.parent))
    root = Path(ap.parse_args().root)
    here = root / 'E7_repairdir'
    key = {r['item_id']: r for r in read(root / 'E7_mining' / 'key' / 'e7_key.csv')}
    c1 = {r['item_id']: r for r in read(root / 'E2_labelling' / 'e7_blind' / 'codes_C1.csv')}
    c2 = {r['item_id']: r for r in read(root / 'E2_labelling' / 'e7_blind' / 'codes_C2.csv')}
    assert set(c1) == set(key) == set(c2), 'item set mismatch between key and codes'
    adj_path = here / 'adjudication.csv'
    adj = {(r['item_id'], r['field']): r['value'] for r in read(adj_path)} if adj_path.is_file() else {}
    items, missing = [], []
    for i in sorted(key):
        final = {}
        for field, cats in (('divergence_kind', KINDS), ('contract_specificity', SPECS)):
            v1, v2 = c1[i][field].strip().upper(), c2[i][field].strip().upper()
            assert v1 in cats and v2 in cats, f'{i} {field}: invalid code {v1!r}/{v2!r}'
            if v1 == v2:
                final[field] = v1
            elif (i, field) in adj:
                final[field] = adj[(i, field)].strip().upper()
                assert final[field] in cats
            else:
                missing.append((i, field))
                final[field] = None
        k = key[i]
        items.append({'id': i, 'set': k['set'], 'truth': k['truth_direction'].strip().upper(), 'kind': final['divergence_kind'],
                      'spec': final['contract_specificity'], 'conf': str(k['confidence']).strip(),
                      'flag': str(k.get('cross_item_flag', '')).strip().lower() not in ('', '0', 'false', 'no', 'none'),
                      'agreed': c1[i]['divergence_kind'].strip().upper() == c2[i]['divergence_kind'].strip().upper(),
                      'stars': int(k['stars']) if str(k['stars']).strip().isdigit() else None})
    if missing:
        sys.exit(f'adjudication missing for {len(missing)} disagreements, e.g. {missing[:5]}')
    new = [it for it in items if it['set'] == 'new']
    expl = [it for it in items if it['set'] == 'e6_exploratory']
    print(f"E7 items {len(items)}: new {len(new)} (SPEC {sum(it['truth'] == 'SPEC' for it in new)}, IMPL "
          f"{sum(it['truth'] == 'IMPL' for it in new)}, other {sum(it['truth'] not in ('SPEC', 'IMPL') for it in new)}), "
          f'exploratory {len(expl)}')
    for nm, sub in (('new', new), ('exploratory', expl)):
        x = [c1[it['id']]['divergence_kind'].strip().upper() for it in sub]
        y = [c2[it['id']]['divergence_kind'].strip().upper() for it in sub]
        kp = kappa(x, y, KINDS)
        print(f"   kappa C1-C2 divergence_kind [{nm}] = {kp:.3f} (agree {sum(a == b for a, b in zip(x, y))}/{len(x)})"
              + (' -> UNRELIABLE CODING (kappa < 0.40)' if nm == 'new' and not kp >= KAPPA_MIN else ''))
        print(f"   kind counts [{nm}]: " + ', '.join(f"{k} {sum(it['kind'] == k for it in sub)}" for k in KINDS))
    rows = []
    print('== H-E7-1 primary (confirmatory): set=new')
    rows.append(report_table('primary', new, 'kind', 'DELIBERATE', 'ACCIDENTAL', confirmatory=True))
    print('== sensitivity')
    rows.append(report_table('sens_a_conf3', [it for it in new if it['conf'] == '3'], 'kind', 'DELIBERATE', 'ACCIDENTAL'))
    rows.append(report_table('sens_b_noflag', [it for it in new if not it['flag']], 'kind', 'DELIBERATE', 'ACCIDENTAL'))
    rows.append(report_table('sens_c_agreed', [it for it in new if it['agreed']], 'kind', 'DELIBERATE', 'ACCIDENTAL'))
    print('== H-E7-2 secondary: contract_specificity, set=new')
    rows.append(report_table('secondary', new, 'spec', 'GENERIC', 'SPECIFIC', confirmatory=True))
    print('== exploratory (E6 items; Claude adjudication not blind here)')
    rows.append(report_table('exploratory', expl, 'kind', 'DELIBERATE', 'ACCIDENTAL'))
    print('== popularity (descriptive, set=new)')
    rows.append(report_table('stars<500', [it for it in new if it['stars'] is not None and it['stars'] < 500], 'kind', 'DELIBERATE', 'ACCIDENTAL'))
    rows.append(report_table('stars>=500', [it for it in new if it['stars'] is not None and it['stars'] >= 500], 'kind', 'DELIBERATE', 'ACCIDENTAL'))
    print('== triage rule DELIBERATE->SPEC, ACCIDENTAL->IMPL (descriptive, set=new)')
    r = rule_scores([it for it in new if it['truth'] in ('SPEC', 'IMPL')])
    if r:
        mf1, acc, cov, per, maj, mmf1, macc = r
        print(f"   rule macro-F1 {mf1:.3f} | SPEC P/R {per['SPEC'][0]:.2f}/{per['SPEC'][1]:.2f} | IMPL P/R "
              f"{per['IMPL'][0]:.2f}/{per['IMPL'][1]:.2f} | decided-acc {acc:.2f} coverage {cov:.2f} || majority ({maj}) "
              f"macro-F1 {mmf1:.3f} acc {macc:.2f}")
    with open(here / 'e7_scores.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print('->', here / 'e7_scores.csv')


if __name__ == '__main__':
    main()
