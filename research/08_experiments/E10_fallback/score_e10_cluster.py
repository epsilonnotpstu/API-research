"""E10 addendum (frozen before any E10 blind run): candidate-cluster sensitivity for H-E10-1 and H-E10-2.
T48 produced 40 items from 21 mined candidates (one candidate can yield several operations). Items within a
candidate are not independent, so the same tests are repeated with the candidate cluster as the unit.
Reported as sensitivity only; the frozen verdicts in E10_PLAN.md are unchanged.
Run from 08_experiments: /usr/bin/python3 -I -B E10_fallback/score_e10_cluster.py [--root R]"""
import argparse, csv, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from score_e10 import rd, kinds, binom_ge  # noqa: E402

DEC = {'SPEC', 'IMPL'}


def score(root):
    key = rd(root / 'E7_mining/key/e10_key.csv')
    cl = {r['item_id']: r['candidate_id'] for r in csv.DictReader(open(root / 'E7_mining/key/accepted_full_t48.csv', newline=''))}
    E = root / 'E2_labelling'
    pkg = [r['item_id'] for r in csv.DictReader(open(E / 'e10_m1/items.csv', newline=''))]
    kd = kinds(E / 'e10_blind/codes_C9.csv', E / 'e10_blind/codes_C10.csv')
    T = {i: key[i]['truth_direction'].strip().upper() for i in pkg}
    ids = [i for i in pkg if T[i] in DEC]
    R = {i: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(kd[i], 'ABSTAIN') for i in ids}
    lab = {}
    for n, d in (('L3', 'e10_m1'), ('L4', 'e10_m1'), ('F1', 'e10_m1f'), ('F2', 'e10_m1f')):
        lab[n] = {i: v['L1'].strip().upper() for i, v in rd(E / d / f'labels_{n}.csv').items()}
    clusters = sorted({cl[i] for i in ids})
    res = {}
    # H-E10-1 by cluster: R-correct share over the cluster's abstention pairs (L3 and L4 pooled); ties dropped
    win = loss = tie = 0
    for c in clusters:
        k = n = 0
        for L in ('L3', 'L4'):
            for i in ids:
                if cl[i] == c and lab[L][i] not in DEC and R[i] in DEC:
                    n += 1; k += R[i] == T[i]
        if n == 0: continue
        if 2 * k > n: win += 1
        elif 2 * k < n: loss += 1
        else: tie += 1
    res['H-E10-1_cluster'] = (win, loss, tie, binom_ge(win, win + loss) if win + loss else 1.0)
    # H-E10-2 by cluster: net (FB correct, M1F wrong) minus (FB wrong, M1F correct) over pairings L3-F1, L4-F2
    w = l = t = 0
    for c in clusters:
        net = 0
        for L, F in (('L3', 'F1'), ('L4', 'F2')):
            for i in ids:
                if cl[i] != c: continue
                fb = lab[L][i] if lab[L][i] in DEC else R[i]
                a, b = fb == T[i], lab[F][i] == T[i]
                net += (a and not b) - (b and not a)
        if net > 0: w += 1
        elif net < 0: l += 1
        else: t += 1
    res['H-E10-2_cluster'] = (w, l, t, binom_ge(w, w + l) if w + l else 1.0, binom_ge(l, w + l) if w + l else 1.0)
    print(f'== E10 cluster sensitivity: {len(ids)} items in {len(clusters)} candidate clusters')
    a = res['H-E10-1_cluster']; print(f'   H-E10-1 by cluster: R-majority-correct {a[0]}, wrong {a[1]}, tie {a[2]}; one-sided p={a[3]:.4f}')
    b = res['H-E10-2_cluster']; print(f'   H-E10-2 by cluster: FB better {b[0]}, M1F better {b[1]}, equal {b[2]}; p(FB>M1F)={b[3]:.4f}, p(M1F>FB)={b[4]:.4f}')
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); a = ap.parse_args()
    score(Path(a.root))


if __name__ == '__main__':
    main()
