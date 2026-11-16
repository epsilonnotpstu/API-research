"""E11 scorer (frozen before coding). Run from 08_experiments: /usr/bin/python3 -I -B E11_crossfamily/score_e11.py [--root R]"""
import argparse, collections, csv, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / 'E10_fallback'))
from score_e10 import fisher_one_sided, kappa  # noqa: E402

KINDS = ('DELIBERATE', 'ACCIDENTAL')
SETS = (('X', 'e7_key.csv', 'accepted_full.csv', 'e7_blind', ('C1', 'C2')),
        ('W', 'e8b_key.csv', 'accepted_full_t47.csv', 'e8b_blind', ('C7', 'C8')),
        ('V', 'e10_key.csv', 'accepted_full_t48.csv', 'e10_blind', ('C9', 'C10')))


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def final(a, b, ids):
    out = {}
    for i in ids:
        x = a.get(i, {}).get('divergence_kind', '').strip().upper()
        y = b.get(i, {}).get('divergence_kind', '').strip().upper()
        out[i] = x if x == y and x in ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR') else 'UNCLEAR'
    return out


def fisher_items(kind, T, ids):
    dS = sum(kind[i] == 'DELIBERATE' and T[i] == 'SPEC' for i in ids); dN = sum(kind[i] == 'DELIBERATE' for i in ids)
    aS = sum(kind[i] == 'ACCIDENTAL' and T[i] == 'SPEC' for i in ids); aN = sum(kind[i] == 'ACCIDENTAL' for i in ids)
    return dS, dN, aS, aN


def fisher_clusters(kind, T, cl, ids):
    rows = []
    for c in sorted({cl[i] for i in ids}):
        g = [i for i in ids if cl[i] == c and kind[i] in KINDS]
        if not g: continue
        k = collections.Counter(kind[i] for i in g).most_common(); t = collections.Counter(T[i] for i in g).most_common()
        if (len(k) > 1 and k[0][1] == k[1][1]) or (len(t) > 1 and t[0][1] == t[1][1]): continue
        rows.append((k[0][0], t[0][0]))
    dS = sum(k == 'DELIBERATE' and t == 'SPEC' for k, t in rows); dN = sum(k == 'DELIBERATE' for k, t in rows)
    aS = sum(k == 'ACCIDENTAL' and t == 'SPEC' for k, t in rows); aN = sum(k == 'ACCIDENTAL' for k, t in rows)
    return dS, dN, aS, aN


def score(root, out=None):
    key_dir = root / 'E7_mining/key'; E = root / 'E2_labelling'
    T, cl, gpt, setof = {}, {}, {}, {}
    for s, kf, af, pkg, (ca, cb) in SETS:
        key = rd(key_dir / kf); acc = rd(key_dir / af)
        ids = [i for i, r in key.items() if r['set'] == 'new' and r['truth_direction'].strip().upper() in ('SPEC', 'IMPL')]
        for i in ids:
            T[i] = key[i]['truth_direction'].strip().upper(); cl[i] = f'{s}:{acc[i]["candidate_id"]}'; setof[i] = s
        gpt.update(final(rd(E / pkg / f'codes_{ca}.csv'), rd(E / pkg / f'codes_{cb}.csv'), ids))
    k1, k2 = {}, {}
    for b in sorted(E.glob('e11_b*')):
        if (b / 'codes_K1.csv').exists(): k1.update(rd(b / 'codes_K1.csv'))
        if (b / 'codes_K2.csv').exists(): k2.update(rd(b / 'codes_K2.csv'))
    ids = sorted(T)
    cla = final(k1, k2, ids)
    res = {}
    print(f'== E11: n={len(ids)} (X {sum(setof[i]=="X" for i in ids)}, W {sum(setof[i]=="W" for i in ids)}, V {sum(setof[i]=="V" for i in ids)}); '
          f'SPEC {sum(T[i]=="SPEC" for i in ids)}, IMPL {sum(T[i]=="IMPL" for i in ids)}; clusters {len(set(cl.values()))}')
    raw = lambda d, i: d.get(i, {}).get('divergence_kind', '').strip().upper() or 'MISSING'
    print(f'   K1 coded {sum(i in k1 for i in ids)}, K2 coded {sum(i in k2 for i in ids)}; K1-K2 kappa {kappa([raw(k1, i) for i in ids], [raw(k2, i) for i in ids]):.3f}')
    print(f'   Claude final kinds D/A/U = {sum(cla[i]=="DELIBERATE" for i in ids)}/{sum(cla[i]=="ACCIDENTAL" for i in ids)}/{sum(cla[i]=="UNCLEAR" for i in ids)}; '
          f'GPT final D/A/U = {sum(gpt[i]=="DELIBERATE" for i in ids)}/{sum(gpt[i]=="ACCIDENTAL" for i in ids)}/{sum(gpt[i]=="UNCLEAR" for i in ids)}')
    # H-E11-1
    dS, dN, aS, aN = fisher_items(cla, T, ids)
    p_i = fisher_one_sided(dS, dN, aS, aN) if dN and aN else 1.0
    cdS, cdN, caS, caN = fisher_clusters(cla, T, cl, ids)
    p_c = fisher_one_sided(cdS, cdN, caS, caN) if cdN and caN else 1.0
    v = 'INSUFFICIENT' if min(dN, aN) < 5 else ('PASS' if p_i < .05 and p_c < .05 else 'FAIL')
    print(f'   H-E11-1 items: DELIBERATE->SPEC {dS}/{dN} vs ACCIDENTAL->SPEC {aS}/{aN} p={p_i:.3g}; clusters {cdS}/{cdN} vs {caS}/{caN} p={p_c:.3g} -> {v}')
    res['H-E11-1'] = (f'{dS}/{dN} vs {aS}/{aN}; cl {cdS}/{cdN} vs {caS}/{caN}', f'p_item={p_i:.3g} p_cluster={p_c:.3g} {v}')
    # H-E11-2
    both = [i for i in ids if gpt[i] in KINDS and cla[i] in KINDS]
    kap = kappa([gpt[i] for i in both], [cla[i] for i in both]) if both else float('nan')
    v2 = 'INSUFFICIENT' if len(both) < 15 else ('PASS' if kap >= 0.6 else 'FAIL')
    agree = sum(gpt[i] == cla[i] for i in both)
    print(f'   H-E11-2 GPT vs Claude final kind on {len(both)} items both decided: agree {agree}, kappa {kap:.3f} -> {v2}')
    res['H-E11-2'] = (f'{agree}/{len(both)}', f'kappa={kap:.3f} {v2}')
    # descriptives
    tab = collections.Counter((gpt[i], cla[i]) for i in ids)
    print('   GPT (rows) x Claude (cols): ' + '; '.join(f'{g[0]}: ' + ' '.join(f'{c[0]}={tab[(g, c)]}' for c in ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR')) for g in ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR')))
    for s in ('X', 'W', 'V'):
        g = [i for i in ids if setof[i] == s]
        a = fisher_items(cla, T, g)
        R = {i: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(cla[i]) for i in g}
        dec = [i for i in g if R[i]]
        print(f'   set {s}: n={len(g)} Claude-kind D->SPEC {a[0]}/{a[1]} A->SPEC {a[2]}/{a[3]}; R(Claude) correct {sum(R[i]==T[i] for i in dec)}/{len(dec)} coverage {len(dec)}/{len(g)}')
    if out is not None:
        with open(out, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['analysis', 'value', 'detail'])
            for k, (a, b) in res.items(): w.writerow([k, a, b])
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); ap.add_argument('--out')
    a = ap.parse_args(); score(Path(a.root), a.out)


if __name__ == '__main__':
    main()
