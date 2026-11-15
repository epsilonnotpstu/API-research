"""E8 pre-registered scorer (see E8_PLAN.md).

Inputs (relative to 08_experiments/ unless --root given):
  key   : E7_mining/key/e7_key.csv (item_id, set, truth_direction)
  match : E2_labelling/e8_match/match_J1.csv (item_id, match in SAME/PARTIAL/DIFFERENT/NONE)
  codes : E2_labelling/e8_code/codes_C3.csv, codes_C4.csv (item_id, divergence_kind)
  P2    : E2_labelling/e8_code_p/codes_P2.csv (optional, descriptive)
Final divergence_kind = C3 if C3 == C4 else UNCLEAR. NONE items have no codes (treated as excluded).
"""
import argparse, csv, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / 'E7_repairdir'))
from score_e7 import fisher_one_sided, wilson, woolf_or, kappa  # noqa: E402

KINDS = ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR')


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def build(root):
    key = rd(root / 'E7_mining/key/e7_key.csv')
    match = rd(root / 'E2_labelling/e8_match/match_J1.csv')
    c3 = rd(root / 'E2_labelling/e8_code/codes_C3.csv')
    c4 = rd(root / 'E2_labelling/e8_code/codes_C4.csv')
    assert set(match) == set(key), 'match/key item mismatch'
    items = []
    for i in sorted(key):
        m = match[i]['match'].strip().upper()
        assert m in ('SAME', 'PARTIAL', 'DIFFERENT', 'NONE'), (i, m)
        if m == 'NONE' or i not in c3 or i not in c4:
            kind, k3, k4 = None, None, None
        else:
            k3, k4 = c3[i]['divergence_kind'].strip().upper(), c4[i]['divergence_kind'].strip().upper()
            assert k3 in KINDS and k4 in KINDS, (i, k3, k4)
            kind = k3 if k3 == k4 else 'UNCLEAR'
        items.append({'id': i, 'set': key[i]['set'], 'truth': key[i]['truth_direction'].strip().upper(),
                      'match': m, 'kind': kind, 'k3': k3, 'k4': k4})
    return items


def tab(rows):
    a = sum(r['kind'] == 'DELIBERATE' and r['truth'] == 'SPEC' for r in rows)
    b = sum(r['kind'] == 'DELIBERATE' and r['truth'] == 'IMPL' for r in rows)
    c = sum(r['kind'] == 'ACCIDENTAL' and r['truth'] == 'SPEC' for r in rows)
    d = sum(r['kind'] == 'ACCIDENTAL' and r['truth'] == 'IMPL' for r in rows)
    return a, b, c, d


def report(name, rows, confirmatory=False):
    a, b, c, d = tab(rows)
    unclear = sum(r['kind'] == 'UNCLEAR' for r in rows)
    p = fisher_one_sided(a, b, c, d)
    o, lo, hi = woolf_or(a, b, c, d)
    w1, w2 = wilson(a, a + b), wilson(c, c + d)
    verdict = ''
    if confirmatory:
        verdict = 'INSUFFICIENT' if min(a + b, c + d) < 8 else ('PASS' if p < 0.05 else 'FAIL')
    print(f'   [{name}] DELIBERATE: SPEC {a}/{a+b} CI[{w1[0]:.2f},{w1[1]:.2f}] | ACCIDENTAL: SPEC {c}/{c+d} '
          f'CI[{w2[0]:.2f},{w2[1]:.2f}] | OR {o:.2f} [{lo:.2f},{hi:.2f}] | Fisher one-sided p={p:.4f} | UNCLEAR {unclear} {verdict}')
    return {'analysis': name, 'a': a, 'b': b, 'c': c, 'd': d, 'p': round(p, 6), 'unclear': unclear, 'verdict': verdict}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); args = ap.parse_args()
    root = Path(args.root)
    items = build(root)
    eligible = [r for r in items if r['truth'] in ('SPEC', 'IMPL')]
    new = [r for r in eligible if r['set'] == 'new']; exp = [r for r in eligible if r['set'] != 'new']
    cnt = {m: sum(r['match'] == m for r in items if r['set'] == 'new') for m in ('SAME', 'PARTIAL', 'DIFFERENT', 'NONE')}
    print('E8 match counts [new, all truths]:', cnt)
    coded = [r for r in items if r['k3'] is not None]
    print(f'   kappa C3-C4 divergence_kind [all coded] = {kappa([r["k3"] for r in coded], [r["k4"] for r in coded], KINDS):.3f} (n={len(coded)})')
    out = [report('primary new SAME', [r for r in new if r['match'] == 'SAME'], confirmatory=True),
           report('sens_a new SAME+PARTIAL', [r for r in new if r['match'] in ('SAME', 'PARTIAL')]),
           report('sens_b new all non-NONE', [r for r in new if r['match'] != 'NONE']),
           report('sens_c exploratory SAME', [r for r in exp if r['match'] == 'SAME'])]
    prim = [r for r in new if r['match'] == 'SAME' and r['kind'] in ('DELIBERATE', 'ACCIDENTAL')]
    if prim:
        tp = {lab: sum((r['kind'] == 'DELIBERATE') == (lab == 'SPEC') and r['truth'] == lab for r in prim) for lab in ('SPEC', 'IMPL')}
        f1 = []
        for lab in ('SPEC', 'IMPL'):
            pred = sum((r['kind'] == 'DELIBERATE') == (lab == 'SPEC') for r in prim); act = sum(r['truth'] == lab for r in prim)
            pr = tp[lab] / pred if pred else 0; rc = tp[lab] / act if act else 0
            f1.append(2 * pr * rc / (pr + rc) if pr + rc else 0)
        print(f'   triage rule on primary: macro-F1 {sum(f1)/2:.3f} (n={len(prim)})')
    p2p = root / 'E2_labelling/e8_code_p/codes_P2.csv'
    if p2p.is_file():
        p2 = rd(p2p); z = [r for r in coded if r['id'] in p2 and r['kind'] != 'UNCLEAR']
        print(f'   kappa P2 vs final (descriptive) = {kappa([r["kind"] for r in z], [p2[r["id"]]["divergence_kind"].strip().upper() for r in z], KINDS):.3f} (n={len(z)})')
    with open(here / 'e8_scores.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)


if __name__ == '__main__':
    main()
