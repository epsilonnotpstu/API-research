"""E12 scorer (frozen in round 2, before any blind run). Implements E12_PLAN.md.
Run from 08_experiments: /usr/bin/python3 -I -B E12_extend/score_e12.py [--root R] [--out F]"""
import argparse, collections, csv, math, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / 'E10_fallback')); sys.path.insert(0, str(here.parent / 'E4_triage'))
from score_e10 import fisher_one_sided, kappa  # noqa: E402

DEC = ('SPEC', 'IMPL'); KINDS = ('DELIBERATE', 'ACCIDENTAL')


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def final(a, b, ids):
    out = {}
    for i in ids:
        x = a.get(i, {}).get('divergence_kind', '').strip().upper(); y = b.get(i, {}).get('divergence_kind', '').strip().upper()
        out[i] = x if x == y and x in KINDS else 'UNCLEAR'
    return out


def merged(E, pattern, name):
    d = {}
    for b in sorted(E.glob(pattern)):
        if (b / name).exists(): d.update(rd(b / name))
    return d


def fisher_tab(kind, T, ids):
    dS = sum(kind[i] == 'DELIBERATE' and T[i] == 'SPEC' for i in ids); dN = sum(kind[i] == 'DELIBERATE' for i in ids)
    aS = sum(kind[i] == 'ACCIDENTAL' and T[i] == 'SPEC' for i in ids); aN = sum(kind[i] == 'ACCIDENTAL' for i in ids)
    return dS, dN, aS, aN


def cluster_tab(kind, T, cl, ids):
    rows = []
    for c in sorted({cl[i] for i in ids}):
        g = [i for i in ids if cl[i] == c and kind[i] in KINDS]
        if not g: continue
        k = collections.Counter(kind[i] for i in g).most_common(); t = collections.Counter(T[i] for i in g).most_common()
        if (len(k) > 1 and k[0][1] == k[1][1]) or (len(t) > 1 and t[0][1] == t[1][1]): continue
        rows.append((k[0][0], t[0][0]))
    return (sum(k == 'DELIBERATE' and t == 'SPEC' for k, t in rows), sum(k == 'DELIBERATE' for k, t in rows),
            sum(k == 'ACCIDENTAL' and t == 'SPEC' for k, t in rows), sum(k == 'ACCIDENTAL' for k, t in rows))


def fp(t):
    dS, dN, aS, aN = t
    return fisher_one_sided(dS, dN, aS, aN) if dN and aN else 1.0


def mcnemar_exact(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(k + 1)) / 2 ** n)


def load_set(root, keyf, accf, pkg, coders, kpat, m1, m1f):
    K = root / 'E7_mining/key'; E = root / 'E2_labelling'
    key = rd(K / keyf); acc = rd(K / accf)
    ids = [i for i, r in key.items() if r['truth_direction'].strip().upper() in DEC]
    T = {i: key[i]['truth_direction'].strip().upper() for i in ids}
    cl = {i: f'{keyf}:{acc[i]["candidate_id"]}' for i in ids}; repo = {i: acc[i]['repo'].split('/')[-1] for i in ids}
    g = final(rd(E / pkg / f'codes_{coders[0]}.csv'), rd(E / pkg / f'codes_{coders[1]}.csv'), ids)
    c = final(merged(E, kpat, 'codes_K3.csv'), merged(E, kpat, 'codes_K4.csv'), ids) if kpat else None
    lab = lambda d, n: {i: v['L1'].strip().upper() for i, v in rd(E / d / f'labels_{n}.csv').items()}
    return dict(ids=ids, T=T, cl=cl, repo=repo, gpt=g, cla=c, m1=lab(*m1), m1f=lab(*m1f), key=key)


def score(root, two_direction, out=None):
    S = load_set(root, 'e12_key.csv', 'accepted_full_t49.csv', 'e12_blind', ('C11', 'C12'), 'e12_k*', ('e12_m1', 'L5'), ('e12_m1f', 'F3'))
    ids, T, cl, gpt, cla = S['ids'], S['T'], S['cl'], S['gpt'], S['cla']
    nboth = sum(r['truth_direction'].strip().upper() == 'BOTH' for r in S['key'].values())
    res = []
    print(f'== E12: n={len(ids)} (SPEC {sum(T[i]=="SPEC" for i in ids)}, IMPL {sum(T[i]=="IMPL" for i in ids)}; BOTH excluded {nboth}); clusters {len(set(cl.values()))}')
    E = root / 'E2_labelling'
    raw = lambda d, i: d.get(i, {}).get('divergence_kind', '').strip().upper() or 'MISSING'
    c11, c12 = rd(E / 'e12_blind/codes_C11.csv'), rd(E / 'e12_blind/codes_C12.csv')
    k3, k4 = merged(E, 'e12_k*', 'codes_K3.csv'), merged(E, 'e12_k*', 'codes_K4.csv')
    print(f'   C11-C12 kappa {kappa([raw(c11, i) for i in ids], [raw(c12, i) for i in ids]):.3f}; K3-K4 kappa {kappa([raw(k3, i) for i in ids], [raw(k4, i) for i in ids]):.3f}')
    for nm, kd in (('GPT', gpt), ('Claude', cla)):
        print(f'   {nm} final D/A/U = {sum(kd[i]=="DELIBERATE" for i in ids)}/{sum(kd[i]=="ACCIDENTAL" for i in ids)}/{sum(kd[i]=="UNCLEAR" for i in ids)}')
    # H-E12-1
    ti, tc = fisher_tab(gpt, T, ids), cluster_tab(gpt, T, cl, ids); pi, pc = fp(ti), fp(tc)
    v = 'INSUFFICIENT' if min(ti[1], ti[3]) < 5 else ('PASS' if pi < .05 and pc < .05 else 'FAIL')
    print(f'   H-E12-1 GPT kinds: items {ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]} p={pi:.3g}; clusters {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]} p={pc:.3g} -> {v}')
    res.append(('H-E12-1', f'{ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]}; cl {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]}', f'p_item={pi:.3g} p_cluster={pc:.3g} {v}'))
    # H-E12-2
    t2 = fisher_tab(cla, T, ids); p2 = fp(t2)
    v = 'INSUFFICIENT' if min(t2[1], t2[3]) < 5 else ('PASS' if p2 < .05 else 'FAIL')
    print(f'   H-E12-2 Claude kinds: items {t2[0]}/{t2[1]} vs {t2[2]}/{t2[3]} p={p2:.3g} -> {v}')
    res.append(('H-E12-2', f'{t2[0]}/{t2[1]} vs {t2[2]}/{t2[3]}', f'p={p2:.3g} {v}'))
    # H-E12-3
    both = [i for i in ids if gpt[i] in KINDS and cla[i] in KINDS]
    kap = kappa([gpt[i] for i in both], [cla[i] for i in both]) if both else float('nan')
    v = 'INSUFFICIENT' if len(both) < 15 else ('PASS' if kap >= 0.6 else 'FAIL')
    print(f'   H-E12-3 GPT vs Claude on {len(both)} both-decided: agree {sum(gpt[i]==cla[i] for i in both)}, kappa {kap:.3f} -> {v}')
    res.append(('H-E12-3', f'{sum(gpt[i]==cla[i] for i in both)}/{len(both)}', f'kappa={kap:.3f} {v}'))
    # H-E12-4
    R = {i: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(gpt[i], 'ABSTAIN') for i in ids}
    dec = [i for i in ids if R[i] in DEC]
    b = sum(R[i] == T[i] and S['m1f'][i] != T[i] for i in dec); c = sum(R[i] != T[i] and S['m1f'][i] == T[i] for i in dec)
    p4 = mcnemar_exact(b, c); v = 'INSUFFICIENT' if b + c < 5 else ('SIGNIFICANT' if p4 < .05 else 'NS')
    print(f'   H-E12-4 R vs F3 on {len(dec)} R-decided: R-only correct {b}, F3-only correct {c}; McNemar exact two-sided p={p4:.4f} -> {v}')
    res.append(('H-E12-4', f'R{b}/F{c}', f'p={p4:.4f} {v}'))
    # descriptives
    Rc = {i: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(cla[i], 'ABSTAIN') for i in ids}
    fb = {i: (S['m1'][i] if S['m1'][i] in DEC else R[i]) for i in ids}

    def mf(pred, ii, TT):
        per, m, acc, cov = two_direction([pred[i] for i in ii if TT[i] == 'SPEC'], [pred[i] for i in ii if TT[i] == 'IMPL'])
        return m, acc, cov
    for meth, p in (('R_gpt', R), ('R_claude', Rc), ('M1_L5', S['m1']), ('M1F_F3', S['m1f']), ('FB_L5', fb)):
        m, a, cv = mf(p, ids, T); print(f'   {meth}: macro-F1 {m:.3f} acc {a:.2f} cov {cv:.2f}')
        res.append(('macroF1', meth, f'{m:.4f} acc={a:.4f} cov={cv:.4f}'))
    for r in sorted(set(S['repo'].values())):
        g = [i for i in ids if S['repo'][i] == r]; print(f'      repo {r}: items {len(g)}, clusters {len({cl[i] for i in g})}')
    # pooled E10 + E12 (descriptive)
    V = load_set(root, 'e10_key.csv', 'accepted_full_t48.csv', 'e10_blind', ('C9', 'C10'), None, ('e10_m1', 'L3'), ('e10_m1f', 'F1'))
    P = {k: {**V[k], **S[k]} for k in ('T', 'cl', 'gpt', 'm1', 'm1f')}; pid = V['ids'] + ids
    ti, tc = fisher_tab(P['gpt'], P['T'], pid), cluster_tab(P['gpt'], P['T'], P['cl'], pid)
    print(f'   POOLED E10+E12 GPT kinds: items {ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]} p={fp(ti):.3g}; clusters {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]} p={fp(tc):.3g}')
    PR = {i: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(P['gpt'][i], 'ABSTAIN') for i in pid}
    for meth, p in (('R', PR), ('M1 (L3+L5)', P['m1']), ('M1F (F1+F3)', P['m1f'])):
        m, a, cv = mf(p, pid, P['T']); print(f'   POOLED {meth}: macro-F1 {m:.3f} acc {a:.2f} cov {cv:.2f}')
    if out:
        with open(out, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['analysis', 'value', 'detail']); w.writerows(res)
    return {r[0] if r[0] != 'macroF1' else f'macroF1:{r[1]}': r for r in res}


def main():
    from score_e4 import two_direction
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); ap.add_argument('--out')
    a = ap.parse_args(); score(Path(a.root), two_direction, a.out)


if __name__ == '__main__':
    main()
