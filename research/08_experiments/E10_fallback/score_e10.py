"""E10 pre-registered scorer (see E10_PLAN.md). Usage: score_e10.py [--root R]

Kind = C9 if C9==C10 else UNCLEAR. R: DELIBERATE->SPEC, ACCIDENTAL->IMPL, UNCLEAR->ABSTAIN.
FB: M1 if M1 in {SPEC,IMPL} else R.  FBS: M1 if decided else SPEC.  M1F: forced-choice label.
Macro-F1 via E4 two_direction (non SPEC/IMPL = miss).
"""
import argparse, csv, math, sys
from pathlib import Path

here = Path(__file__).resolve().parent
DEC = ('SPEC', 'IMPL')


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def kinds(pa, pb):
    a, b = rd(pa), rd(pb)
    out = {}
    for i in a:
        if i in b:
            x, y = a[i]['divergence_kind'].strip().upper(), b[i]['divergence_kind'].strip().upper()
            out[i] = x if x == y else 'UNCLEAR'
    return out


def binom_ge(k, n, p=0.5):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1)) if n else 1.0


def fisher_one_sided(a, n1, c, n2):
    K, N = a + c, n1 + n2
    return sum(math.comb(n1, x) * math.comb(n2, K - x) for x in range(a, min(n1, K) + 1)) / math.comb(N, K)


def kappa(xs, ys):
    n = len(xs); cats = sorted(set(xs) | set(ys))
    po = sum(x == y for x, y in zip(xs, ys)) / n
    pe = sum((xs.count(c) / n) * (ys.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def score(root, two_direction, out):
    key = rd(root / 'E7_mining/key/e10_key.csv')
    E = root / 'E2_labelling'
    pkg = [r['item_id'] for r in csv.DictReader(open(E / 'e10_m1/items.csv', newline=''))]
    kd = kinds(E / 'e10_blind/codes_C9.csv', E / 'e10_blind/codes_C10.csv')
    c9, c10 = rd(E / 'e10_blind/codes_C9.csv'), rd(E / 'e10_blind/codes_C10.csv')
    n_both = sum(key[i]['truth_direction'].strip().upper() == 'BOTH' for i in pkg)
    items = [{'id': i, 'truth': key[i]['truth_direction'].strip().upper(), 'kind': kd[i]} for i in pkg
             if key[i]['truth_direction'].strip().upper() in DEC]
    labs = {}
    for n, d in (('L3', 'e10_m1'), ('L4', 'e10_m1'), ('F1', 'e10_m1f'), ('F2', 'e10_m1f')):
        lab = rd(E / d / f'labels_{n}.csv'); assert set(pkg) <= set(lab), n
        labs[n] = {i: v['L1'].strip().upper() for i, v in lab.items()}
    ids = [r['id'] for r in items]
    print(f'== E10: n={len(items)} (SPEC {sum(r["truth"]=="SPEC" for r in items)}, IMPL {sum(r["truth"]=="IMPL" for r in items)}; BOTH excluded {n_both}); '
          f'kinds D/A/U = {sum(r["kind"]=="DELIBERATE" for r in items)}/{sum(r["kind"]=="ACCIDENTAL" for r in items)}/{sum(r["kind"]=="UNCLEAR" for r in items)}')
    print(f'   C9-C10 kappa (divergence_kind, all package items) = {kappa([c9[i]["divergence_kind"].strip().upper() for i in pkg], [c10[i]["divergence_kind"].strip().upper() for i in pkg]):.3f}')
    R = {r['id']: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(r['kind'], 'ABSTAIN') for r in items}
    T = {r['id']: r['truth'] for r in items}

    def mf(pred):
        per, m, acc, cov = two_direction([pred[i] for i in ids if T[i] == 'SPEC'], [pred[i] for i in ids if T[i] == 'IMPL'])
        return m, acc, cov

    def row(meth, pred):
        m, acc, cov = mf(pred); print(f'   {meth}: macro-F1 {m:.3f} decided-acc {acc:.2f} coverage {cov:.2f}')
        out.append({'analysis': 'macroF1', 'method': meth, 'value': round(m, 4), 'detail': f'acc={acc:.4f} cov={cov:.4f}'})

    row('R', R)
    # H-E10-1
    pairs = {}
    preds = {}
    for n in ('L3', 'L4'):
        m1 = {i: labs[n][i] for i in ids}
        fb = {i: (m1[i] if m1[i] in DEC else R[i]) for i in ids}
        fbs = {i: (m1[i] if m1[i] in DEC else 'SPEC') for i in ids}
        preds[n] = fb
        for meth, p in ((f'{n}_M1', m1), (f'{n}_FB', fb), (f'{n}_FBS', fbs)): row(meth, p)
        ab = [i for i in ids if m1[i] not in DEC and R[i] in DEC]
        pairs[n] = (sum(R[i] == T[i] for i in ab), len(ab))
        nd = [i for i in ids if m1[i] not in DEC and R[i] not in DEC]
        diff = [i for i in ab if R[i] != 'SPEC']
        print(f'   {n}: abstentions {sum(m1[i] not in DEC for i in ids)} (R decides {len(ab)}, R correct {pairs[n][0]}; both abstain {len(nd)}); '
              f'FB vs FBS differ on {len(diff)} (FB correct {sum(R[i]==T[i] for i in diff)})')
        for k in ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'):
            g = [r['id'] for r in items if r['kind'] == k]
            if g: print(f'      M1 correct | {k}: {sum(m1[i] == T[i] for i in g)}/{len(g)}')
    k = sum(c for c, _ in pairs.values()); n = sum(t for _, t in pairs.values()); p = binom_ge(k, n)
    v = 'INSUFFICIENT' if n < 8 else ('PASS' if p < 0.05 and all(t == 0 or c / t >= 0.5 for c, t in pairs.values()) else 'FAIL')
    print(f'   H-E10-1 R correct on abstention pairs {k}/{n} binomial one-sided p={p:.4f} -> {v}')
    out.append({'analysis': 'H-E10-1', 'method': 'R_on_M1_abstentions', 'value': f'{k}/{n}', 'detail': f'p={p:.4f} {v}'})
    uq = [i for i in ids if any(labs[x][i] not in DEC for x in ('L3', 'L4')) and R[i] in DEC]
    ku = sum(R[i] == T[i] for i in uq)
    print(f'   H-E10-1 sensitivity (unique items) {ku}/{len(uq)} p={binom_ge(ku, len(uq)):.4f}')
    out.append({'analysis': 'H-E10-1_sens', 'method': 'unique_items', 'value': f'{ku}/{len(uq)}', 'detail': f'p={binom_ge(ku, len(uq)):.4f}'})
    # H-E10-2
    W = L = 0; per = {}
    for a, f in (('L3', 'F1'), ('L4', 'F2')):
        m1f = {i: labs[f][i] for i in ids}; row(f'{f}_M1F', m1f)
        fb = preds[a]
        w = sum(fb[i] != m1f[i] and fb[i] == T[i] and m1f[i] != T[i] for i in ids)
        l = sum(fb[i] != m1f[i] and m1f[i] == T[i] and fb[i] != T[i] for i in ids)
        per[a + f] = (w, l); W += w; L += l
        print(f'   {a}-FB vs {f}-M1F: discordant {sum(fb[i] != m1f[i] for i in ids)}, wins {w}, losses {l}')
    d = W + L; p2 = binom_ge(W, d); prev = binom_ge(L, d)
    v2 = 'INSUFFICIENT' if d < 5 else ('FB_BETTER' if p2 < 0.05 and all(w >= l for w, l in per.values()) else f'NOT_BETTER (reverse p={prev:.4f})')
    print(f'   H-E10-2 pooled wins {W} losses {L} sign one-sided p={p2:.4f} -> {v2}')
    out.append({'analysis': 'H-E10-2', 'method': 'FB_vs_M1F', 'value': f'W{W}/L{L}', 'detail': f'p={p2:.4f} {v2}'})
    # H-E10-3
    D = [r for r in items if r['kind'] == 'DELIBERATE']; A = [r for r in items if r['kind'] == 'ACCIDENTAL']
    ds, as_ = sum(r['truth'] == 'SPEC' for r in D), sum(r['truth'] == 'SPEC' for r in A)
    p3 = fisher_one_sided(ds, len(D), as_, len(A)) if D and A else 1.0
    v3 = 'INSUFFICIENT' if min(len(D), len(A)) < 8 else ('PASS' if p3 < 0.05 else 'FAIL')
    print(f'   H-E10-3 DELIBERATE->SPEC {ds}/{len(D)} vs ACCIDENTAL->SPEC {as_}/{len(A)} Fisher one-sided p={p3:.2e} -> {v3}')
    out.append({'analysis': 'H-E10-3', 'method': 'kind_x_direction', 'value': f'{ds}/{len(D)} vs {as_}/{len(A)}', 'detail': f'p={p3:.3e} {v3}'})
    for x, y in (('L3', 'L4'), ('F1', 'F2')):
        print(f'   agreement {x}-{y}: {sum(labs[x][i] == labs[y][i] for i in ids)}/{len(ids)}')
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); ap.add_argument('--out', default=str(here / 'e10_scores.csv'))
    a = ap.parse_args(); root = Path(a.root)
    sys.path.insert(0, str(here.parent / 'E4_triage'))
    from score_e4 import two_direction
    out = score(root, two_direction, [])
    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['analysis', 'method', 'value', 'detail']); w.writeheader(); w.writerows(out)


if __name__ == '__main__':
    main()
