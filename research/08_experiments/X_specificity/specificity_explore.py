"""EXPLORATORY (post hoc, not pre-registered): does H-E7-2 (P(SPEC | GENERIC) > P(SPEC | SPECIFIC))
recur on the later disjoint new-item samples E10, E12, E13? Written 2026-11-17 after all of them were scored.
Final specificity = both coders agree, else dropped. BOTH truth excluded. One-sided Fisher (score_e10.fisher_one_sided).
Run from 08_experiments: /usr/bin/python3 -I -B X_specificity/specificity_explore.py"""
import csv, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)
B = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(B / 'E10_fallback'))
from score_e10 import fisher_one_sided  # noqa: E402

E = B / 'E2_labelling'; K = B / 'E7_mining/key'
SETS = [  # name, key, [(pkg dirs, coder ids)]
    ('E10', 'e10_key.csv', [(['e10_blind'], ('C9', 'C10'))]),
    ('E12', 'e12_key.csv', [(['e12_blind'], ('C11', 'C12')), (['e12_kb1', 'e12_kb2'], ('K3', 'K4'))]),
    ('E13', 'e13_key.csv', [(['e13_blind'], ('C13', 'C14')), (['e13_kb1', 'e13_kb2', 'e13_kb3'], ('K5', 'K6'))]),
]


def codes(dirs, cid):
    out = {}
    for d in dirs:
        for r in csv.DictReader(open(E / d / f'codes_{cid}.csv', newline='')):
            out[r['item_id']] = (r['divergence_kind'].strip().upper(), r['contract_specificity'].strip().upper())
    return out


def final(a, b, i):
    return a[i] if a[i] == b[i] else None


def tab(rows, label):
    g = [t for s, k, t in rows if s == 'GENERIC']; s_ = [t for s, k, t in rows if s == 'SPECIFIC']
    a, b = sum(t == 'SPEC' for t in g), sum(t == 'SPEC' for t in s_)
    p = fisher_one_sided(a, len(g), b, len(s_)) if g and s_ else float('nan')
    print(f'   {label}: GENERIC {a}/{len(g)} vs SPECIFIC {b}/{len(s_)}  one-sided p={p:.3g}')
    return a, len(g), b, len(s_)


pool = {'all': [0, 0, 0, 0], 'delib': [0, 0, 0, 0]}
for name, keyf, coders in SETS:
    truth = {r['item_id']: r['truth_direction'] for r in csv.DictReader(open(K / keyf, newline=''))}
    for dirs, (c1, c2) in coders:
        A, Bc = codes(dirs, c1), codes(dirs, c2)
        rows = []
        for i, t in truth.items():
            if t not in ('SPEC', 'IMPL') or i not in A or i not in Bc: continue
            s, k = final(A[i], Bc[i], 1), final(A[i], Bc[i], 0)
            if s in ('GENERIC', 'SPECIFIC'): rows.append((s, k, t))
        print(f'{name} {c1}/{c2}: specificity decided on {len(rows)}')
        r1 = tab(rows, 'all kinds')
        r2 = tab([x for x in rows if x[1] == 'DELIBERATE'], 'DELIBERATE only')
        if c1.startswith('C'):
            for key, r in (('all', r1), ('delib', r2)):
                pool[key] = [x + y for x, y in zip(pool[key], r)]
for key, (a, n, b, m) in pool.items():
    print(f'POOLED GPT E10+E12+E13 {key}: GENERIC {a}/{n} vs SPECIFIC {b}/{m}  one-sided p={fisher_one_sided(a, n, b, m):.3g}')

# cross-family agreement on final specificity (E12, E13)
from score_e10 import kappa  # noqa: E402
for name, keyf, coders in SETS[1:]:
    (gd, (g1, g2)), (cd, (k1, k2)) = coders
    G1, G2, C1, C2 = codes(gd, g1), codes(gd, g2), codes(cd, k1), codes(cd, k2)
    xs, ys = [], []
    for i in G1:
        g, c = final(G1[i], G2[i], 1), final(C1[i], C2[i], 1)
        if g in ('GENERIC', 'SPECIFIC') and c in ('GENERIC', 'SPECIFIC'): xs.append(g); ys.append(c)
    print(f'{name} specificity GPT-final vs Claude-final: n={len(xs)} agree={sum(a == b for a, b in zip(xs, ys))} kappa={kappa(xs, ys):.2f}'
          f'  | within-family kappa GPT={kappa([G1[i][1] for i in G1], [G2[i][1] for i in G1]):.2f} Claude={kappa([C1[i][1] for i in C1], [C2[i][1] for i in C1]):.2f}')
