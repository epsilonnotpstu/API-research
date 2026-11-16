"""E13 scorer (frozen with the plan, before T50 mining). Implements E13_PLAN.md.
Run from 08_experiments: /usr/bin/python3 -I -B E13_newrepos/score_e13.py [--root R] [--out F]"""
import argparse, collections, csv, math, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / 'E10_fallback')); sys.path.insert(0, str(here.parent / 'E4_triage'))
from score_e10 import fisher_one_sided, kappa  # noqa: E402
csv.field_size_limit(sys.maxsize)

DEC = ('SPEC', 'IMPL'); KINDS = ('DELIBERATE', 'ACCIDENTAL')
RULE = {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def merged(E, pattern, name):
    d = {}
    for b in sorted(E.glob(pattern)):
        if (b / name).exists(): d.update(rd(b / name))
    return d


def final(a, b, ids):
    out = {}
    for i in ids:
        x = a.get(i, {}).get('divergence_kind', '').strip().upper(); y = b.get(i, {}).get('divergence_kind', '').strip().upper()
        out[i] = x if x == y and x in KINDS else 'UNCLEAR'
    return out


def fisher_tab(kind, T, ids):
    return (sum(kind[i] == 'DELIBERATE' and T[i] == 'SPEC' for i in ids), sum(kind[i] == 'DELIBERATE' for i in ids),
            sum(kind[i] == 'ACCIDENTAL' and T[i] == 'SPEC' for i in ids), sum(kind[i] == 'ACCIDENTAL' for i in ids))


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
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(min(b, c) + 1)) / 2 ** n)


def wilson(k, n, z=1.96):
    if n == 0: return float('nan'), float('nan'), float('nan')
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def load_set(root, keyf, accf, pkg, coders, kpat, kc, m1, m1f):
    K = root / 'E7_mining/key'; E = root / 'E2_labelling'
    key = rd(K / keyf); acc = rd(K / accf)
    ids = [i for i, r in key.items() if r['truth_direction'].strip().upper() in DEC]
    T = {i: key[i]['truth_direction'].strip().upper() for i in ids}
    cl = {i: f'{keyf}:{acc[i]["candidate_id"]}' for i in ids}; repo = {i: acc[i]['repo'].split('/')[-1] for i in ids}
    g = final(rd(E / pkg / f'codes_{coders[0]}.csv'), rd(E / pkg / f'codes_{coders[1]}.csv'), ids)
    c = final(merged(E, kpat, f'codes_{kc[0]}.csv'), merged(E, kpat, f'codes_{kc[1]}.csv'), ids) if kpat else None
    lab = lambda d, n: {i: v['L1'].strip().upper() for i, v in rd(E / d / f'labels_{n}.csv').items()}
    nboth = sum(r['truth_direction'].strip().upper() == 'BOTH' for r in key.values())
    return dict(ids=ids, T=T, cl=cl, repo=repo, gpt=g, cla=c, m1=lab(*m1), m1f=lab(*m1f), nboth=nboth)


def verdict_two(ti, tc):
    if min(ti[1], ti[3]) < 5: return 'INSUFFICIENT'
    return 'PASS' if fp(ti) < .05 and fp(tc) < .05 else 'FAIL'


def score(root, two_direction, out=None):
    E = root / 'E2_labelling'
    S = load_set(root, 'e13_key.csv', 'accepted_full_t50.csv', 'e13_blind', ('C13', 'C14'), 'e13_kb*', ('K5', 'K6'), ('e13_m1', 'L6'), ('e13_m1f', 'F4'))
    ids, T, cl, gpt, cla, repo = S['ids'], S['T'], S['cl'], S['gpt'], S['cla'], S['repo']
    res = []
    print(f'== E13: n={len(ids)} (SPEC {sum(T[i]=="SPEC" for i in ids)}, IMPL {sum(T[i]=="IMPL" for i in ids)}; BOTH excluded {S["nboth"]}); clusters {len(set(cl.values()))}; repos {len(set(repo.values()))}')
    raw = lambda d, i: d.get(i, {}).get('divergence_kind', '').strip().upper() or 'MISSING'
    c1, c2 = rd(E / 'e13_blind/codes_C13.csv'), rd(E / 'e13_blind/codes_C14.csv')
    k1, k2 = merged(E, 'e13_kb*', 'codes_K5.csv'), merged(E, 'e13_kb*', 'codes_K6.csv')
    print(f'   C13-C14 kappa {kappa([raw(c1, i) for i in ids], [raw(c2, i) for i in ids]):.3f}; K5-K6 kappa {kappa([raw(k1, i) for i in ids], [raw(k2, i) for i in ids]):.3f}')
    for nm, kd in (('GPT', gpt), ('Claude', cla)):
        print(f'   {nm} final D/A/U = {sum(kd[i]=="DELIBERATE" for i in ids)}/{sum(kd[i]=="ACCIDENTAL" for i in ids)}/{sum(kd[i]=="UNCLEAR" for i in ids)}')
    for h, nm, kd in (('H-E13-1', 'GPT', gpt), ('H-E13-2', 'Claude', cla)):
        ti, tc = fisher_tab(kd, T, ids), cluster_tab(kd, T, cl, ids); v = verdict_two(ti, tc)
        print(f'   {h} {nm} kinds: items {ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]} p={fp(ti):.3g}; clusters {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]} p={fp(tc):.3g} -> {v}')
        res.append((h, f'{ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]}; cl {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]}', f'p_item={fp(ti):.3g} p_cluster={fp(tc):.3g} {v}'))
    both = [i for i in ids if gpt[i] in KINDS and cla[i] in KINDS]
    kap = kappa([gpt[i] for i in both], [cla[i] for i in both]) if both else float('nan')
    v = 'INSUFFICIENT' if len(both) < 15 else ('PASS' if kap >= 0.6 else 'FAIL')
    print(f'   H-E13-3 GPT vs Claude on {len(both)} both-decided: agree {sum(gpt[i]==cla[i] for i in both)}, kappa {kap:.3f} -> {v}')
    res.append(('H-E13-3', f'{sum(gpt[i]==cla[i] for i in both)}/{len(both)}', f'kappa={kap:.3f} {v}'))
    R = {i: RULE.get(gpt[i], 'ABSTAIN') for i in ids}; dec = [i for i in ids if R[i] in DEC]
    b = sum(R[i] == T[i] and S['m1f'][i] != T[i] for i in dec); c = sum(R[i] != T[i] and S['m1f'][i] == T[i] for i in dec)
    p4 = mcnemar_exact(b, c); v = 'INSUFFICIENT' if b + c < 5 else ('SIGNIFICANT' if p4 < .05 else 'NS')
    print(f'   H-E13-4 R vs F4 on {len(dec)} R-decided: R-only correct {b}, F4-only correct {c}; McNemar exact two-sided p={p4:.4f} -> {v}')
    res.append(('H-E13-4', f'R{b}/F{c}', f'p={p4:.4f} {v}'))
    # descriptives
    Rc = {i: RULE.get(cla[i], 'ABSTAIN') for i in ids}
    fb = {i: (S['m1'][i] if S['m1'][i] in DEC else R[i]) for i in ids}

    def mf(pred, ii, TT):
        per, m, acc, cov = two_direction([pred[i] for i in ii if TT[i] == 'SPEC'], [pred[i] for i in ii if TT[i] == 'IMPL'])
        return m, acc, cov
    for meth, p in (('R_gpt', R), ('R_claude', Rc), ('M1_L6', S['m1']), ('M1F_F4', S['m1f']), ('FB_L6', fb)):
        m, a, cv = mf(p, ids, T); print(f'   {meth}: macro-F1 {m:.3f} acc {a:.2f} cov {cv:.2f}')
        res.append(('macroF1', meth, f'{m:.4f} acc={a:.4f} cov={cv:.4f}'))

    def prec(kd, TT, ii, tag):
        dS, dN, aS, aN = fisher_tab(kd, TT, ii)
        for nm, k, n in (('ACCIDENTAL->IMPL', aN - aS, aN), ('DELIBERATE->SPEC', dS, dN)):
            p, lo, hi = wilson(k, n); print(f'   {tag}precision {nm}: {k}/{n} = {p:.3f} [{lo:.3f}, {hi:.3f}]')
            res.append(('precision', f'{tag}{nm}', f'{k}/{n} {p:.4f} [{lo:.4f},{hi:.4f}]'))
    prec(gpt, T, ids, '')
    for r in sorted(set(repo.values())):
        g = [i for i in ids if repo[i] == r]; print(f'      repo {r}: items {len(g)}, clusters {len({cl[i] for i in g})}')
    loo = []
    for r in sorted(set(repo.values())):
        ii = [i for i in ids if repo[i] != r]; loo.append((fp(fisher_tab(gpt, T, ii)), r))
    if loo:
        mx = max(loo); print(f'   leave-one-repo-out H-E13-1 item p: max {mx[0]:.3g} (without {mx[1]})')
        res.append(('LOO', mx[1], f'max_p={mx[0]:.4g}'))
    # pooled E10 + E12 + E13 (descriptive)
    V = load_set(root, 'e10_key.csv', 'accepted_full_t48.csv', 'e10_blind', ('C9', 'C10'), None, None, ('e10_m1', 'L3'), ('e10_m1f', 'F1'))
    U = load_set(root, 'e12_key.csv', 'accepted_full_t49.csv', 'e12_blind', ('C11', 'C12'), None, None, ('e12_m1', 'L5'), ('e12_m1f', 'F3'))
    P = {k: {**V[k], **U[k], **S[k]} for k in ('T', 'cl', 'gpt', 'm1', 'm1f')}; pid = V['ids'] + U['ids'] + ids
    ti, tc = fisher_tab(P['gpt'], P['T'], pid), cluster_tab(P['gpt'], P['T'], P['cl'], pid)
    print(f'   POOLED E10+E12+E13 (n={len(pid)}) GPT kinds: items {ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]} p={fp(ti):.3g}; clusters {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]} p={fp(tc):.3g}')
    res.append(('pooled', f'{ti[0]}/{ti[1]} vs {ti[2]}/{ti[3]}; cl {tc[0]}/{tc[1]} vs {tc[2]}/{tc[3]}', f'p_item={fp(ti):.3g} p_cluster={fp(tc):.3g}'))
    prec(P['gpt'], P['T'], pid, 'POOLED ')
    PR = {i: RULE.get(P['gpt'][i], 'ABSTAIN') for i in pid}
    for meth, p in (('R', PR), ('M1 (L3+L5+L6)', P['m1']), ('M1F (F1+F3+F4)', P['m1f'])):
        m, a, cv = mf(p, pid, P['T']); print(f'   POOLED {meth}: macro-F1 {m:.3f} acc {a:.2f} cov {cv:.2f}')
        res.append(('pooled_macroF1', meth, f'{m:.4f} acc={a:.4f} cov={cv:.4f}'))
    if out:
        with open(out, 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(['analysis', 'value', 'detail']); w.writerows(res)
    return {(r[0] if r[0] in ('H-E13-1', 'H-E13-2', 'H-E13-3', 'H-E13-4', 'LOO') else f'{r[0]}:{r[1]}'): r for r in res}


def main():
    from score_e4 import two_direction
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); ap.add_argument('--out')
    a = ap.parse_args(); score(Path(a.root), two_direction, a.out)


if __name__ == '__main__':
    main()
