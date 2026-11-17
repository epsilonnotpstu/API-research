"""R3 scorer (frozen before mining). Run from R3_silent_breaking/: /usr/bin/python3 -I -B plan/score_r3.py [--root R] [--out F]
Inputs (relative to root):
  mining/key/r3_key.csv            item_id, repo, commit, language, annotation_touched (true/false), spec_updated_90d (true/false)
  packages/r3_blind/codes_G1.csv, codes_G2.csv               GPT coders
  packages/r3_kb*/codes_H1.csv, codes_H2.csv                 Claude coders (batches)
Code columns: item_id, observable_change, change_kind, client_impact, contract_specified, ..."""
import argparse, collections, csv, math, random, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)

FIELDS = ('observable_change', 'change_kind', 'client_impact', 'contract_specified')
KINDS = {'STATUS_OR_ERROR_MAPPING', 'INPUT_STRICTER', 'INPUT_LOOSER', 'DEFAULT_OR_OPTIONALITY', 'RESPONSE_CONTENT', 'RESPONSE_SHAPE',
         'HEADER_OR_MEDIA_TYPE', 'AUTHZ_OR_AUTH', 'SIDE_EFFECT_OR_STATE', 'ORDERING_PAGINATION_LIMITS', 'OTHER'}
ALLOWED = {'observable_change': {'YES', 'NO', 'UNCLEAR'}, 'change_kind': KINDS | {'', 'NA'},
           'client_impact': {'BREAKING', 'COMPATIBLE', 'UNCLEAR', '', 'NA'}, 'contract_specified': {'SPECIFIED', 'UNSPECIFIED', '', 'NA'}}


def rd(p):
    return list(csv.DictReader(open(p, newline='', encoding='utf-8')))


def norm(v):
    return (v or '').strip().upper()


def load_codes(paths):
    out = {}
    for p in paths:
        for r in rd(p):
            row = {f: norm(r.get(f)) for f in FIELDS}
            for f in FIELDS:
                if row[f] not in ALLOWED[f]: raise ValueError(f'{p}: {r["item_id"]} {f}={row[f]!r}')
            if row['observable_change'] != 'YES':
                row['change_kind'] = row['client_impact'] = row['contract_specified'] = 'NA'
            out[r['item_id'].strip()] = row
    return out


def final(a, b):
    """Field-wise agreement; disagreement -> UNCLEAR. Dependent fields only when both said YES."""
    out = {}
    oc = a['observable_change'] if a['observable_change'] == b['observable_change'] else 'UNCLEAR'
    out['observable_change'] = oc
    for f in FIELDS[1:]:
        out[f] = (a[f] if a[f] == b[f] else 'UNCLEAR') if oc == 'YES' else 'NA'
    return out


def wilson(k, n, z=1.959963984540054):
    if n == 0: return float('nan'), float('nan'), float('nan')
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def binom_upper(k, n, p=0.5):
    """P(X >= k), X ~ Bin(n, p)"""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def kappa(xs, ys):
    n = len(xs)
    if n == 0: return float('nan')
    cats = sorted(set(xs) | set(ys)); po = sum(x == y for x, y in zip(xs, ys)) / n
    pe = sum((xs.count(c) / n) * (ys.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def cluster_boot(items, pred, B=2000, seed=1):
    by = collections.defaultdict(list)
    for it in items: by[it['repo']].append(it)
    repos = sorted(by); rng = random.Random(seed); vals = []
    for _ in range(B):
        s = [it for r in (rng.choice(repos) for _ in repos) for it in by[r]]
        if s: vals.append(sum(pred(it) for it in s) / len(s))
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def score(root, out=None):
    root = Path(root); P = root / 'packages'
    key = {r['item_id']: r for r in rd(root / 'mining/key/r3_key.csv')}
    G1 = load_codes([P / 'r3_blind/codes_G1.csv']); G2 = load_codes([P / 'r3_blind/codes_G2.csv'])
    kb = sorted(d for d in P.glob('r3_kb*') if d.is_dir())
    H1 = load_codes([d / 'codes_H1.csv' for d in kb]); H2 = load_codes([d / 'codes_H2.csv' for d in kb])
    ids = sorted(key)
    for name, C in (('G1', G1), ('G2', G2), ('H1', H1), ('H2', H2)):
        miss = set(ids) - set(C)
        if miss: raise ValueError(f'{name} missing {len(miss)} items')
    items = []
    for i in ids:
        k = key[i]
        items.append(dict(id=i, repo=k['repo'], lang=k.get('language', ''), ann=norm(k['annotation_touched']) == 'TRUE',
                          upd=norm(k['spec_updated_90d']) == 'TRUE', g=final(G1[i], G2[i]), h=final(H1[i], H2[i])))
    res = collections.OrderedDict(); n = len(items)
    print(f'== R3: n={n} commits; repos {len(set(it["repo"] for it in items))}')
    for f in FIELDS:
        print(f'   kappa {f}: GPT {kappa([G1[i][f] for i in ids], [G2[i][f] for i in ids]):.3f}  Claude {kappa([H1[i][f] for i in ids], [H2[i][f] for i in ids]):.3f}')
    oc = collections.Counter(it['g']['observable_change'] for it in items)
    print(f'   GPT final observable_change YES/NO/UNCLEAR = {oc["YES"]}/{oc["NO"]}/{oc["UNCLEAR"]}')
    # E-R3-1
    yes = lambda it: it['g']['observable_change'] == 'YES'
    brk = lambda it: yes(it) and it['g']['client_impact'] == 'BREAKING'
    for lab, pr in (('YES', yes), ('BREAKING', brk)):
        k = sum(pr(it) for it in items); p, lo, hi = wilson(k, n); blo, bhi = cluster_boot(items, pr)
        res[f'E-R3-1 {lab}'] = (k, n, f'{p:.3f} Wilson [{lo:.3f}, {hi:.3f}] cluster-boot [{blo:.3f}, {bhi:.3f}]')
        print(f'   E-R3-1 share {lab}: {k}/{n} = {p:.3f} Wilson [{lo:.3f}, {hi:.3f}]; repo-cluster bootstrap [{blo:.3f}, {bhi:.3f}]')
    # H-R3-1
    B = [it for it in items if brk(it)]; k = sum(not it['ann'] for it in B)
    if len(B) < 10: v = f'INSUFFICIENT (BREAKING n={len(B)} < 10)'; pv = float('nan')
    else: pv = binom_upper(k, len(B)); v = 'PASS' if pv < .05 else 'FAIL'
    res['H-R3-1'] = (k, len(B), f'p={pv:.3g} -> {v}')
    print(f'   H-R3-1 BREAKING without contract-annotation edit: {k}/{len(B)}; one-sided binomial vs 0.5 p={pv:.3g} -> {v}')
    # H-R3-2
    S = [it for it in B if it['g']['contract_specified'] == 'SPECIFIED']; k2 = sum(not it['upd'] for it in S)
    if len(S) < 8: v2 = f'INSUFFICIENT (n={len(S)} < 8)'; pv2 = float('nan')
    else: pv2 = binom_upper(k2, len(S)); v2 = 'PASS' if pv2 < .05 else 'FAIL'
    res['H-R3-2'] = (k2, len(S), f'p={pv2:.3g} -> {v2}')
    print(f'   H-R3-2 BREAKING+SPECIFIED with no contract update in 90d: {k2}/{len(S)}; p={pv2:.3g} -> {v2}')
    # H-R3-3
    xs, ys = [], []
    for it in items:
        a, b = it['g']['observable_change'], it['h']['observable_change']
        if a in ('YES', 'NO') and b in ('YES', 'NO'): xs.append(a); ys.append(b)
    kp = kappa(xs, ys); v3 = f'INSUFFICIENT (n={len(xs)} < 30)' if len(xs) < 30 else ('PASS' if kp >= 0.6 else 'FAIL')
    res['H-R3-3'] = (sum(x == y for x, y in zip(xs, ys)), len(xs), f'kappa={kp:.3f} -> {v3}')
    print(f'   H-R3-3 cross-family observable_change on {len(xs)} both-decided: agree {sum(x == y for x, y in zip(xs, ys))}, kappa {kp:.3f} -> {v3}')
    # descriptives
    Y = [it for it in items if yes(it)]
    print('   kinds (GPT final, YES items):', dict(collections.Counter(it['g']['change_kind'] for it in Y).most_common()))
    print('   impact x kind:', dict(collections.Counter((it['g']['change_kind'], it['g']['client_impact']) for it in Y).most_common()))
    print('   specified x impact:', dict(collections.Counter((it['g']['contract_specified'], it['g']['client_impact']) for it in Y).most_common()))
    print('   annotation_touched among YES:', sum(it['ann'] for it in Y), '/', len(Y))
    for lang in sorted(set(it['lang'] for it in items)):
        L = [it for it in items if it['lang'] == lang]
        print(f'   lang {lang or "?"}: n={len(L)} YES {sum(yes(it) for it in L)} BREAKING {sum(brk(it) for it in L)}')
    for r in sorted(set(it['repo'] for it in items)):
        R = [it for it in items if it['repo'] == r]
        print(f'      repo {r}: n={len(R)} YES {sum(yes(it) for it in R)} BREAKING {sum(brk(it) for it in R)}')
    lo_ = [(sum(brk(it) for it in items if it['repo'] != r) / max(1, sum(it['repo'] != r for it in items)), r) for r in sorted(set(it['repo'] for it in items))]
    print(f'   leave-one-repo-out BREAKING share: min {min(lo_)[0]:.3f} (without {min(lo_)[1]}), max {max(lo_)[0]:.3f} (without {max(lo_)[1]})')
    hy = sum(it['h']['observable_change'] == 'YES' for it in items); hb = sum(it['h']['observable_change'] == 'YES' and it['h']['client_impact'] == 'BREAKING' for it in items)
    print(f'   Claude-final shares (cross-family check): YES {hy}/{n}, BREAKING {hb}/{n}')
    if out:
        with open(out, 'w', newline='') as fh:
            w = csv.writer(fh, lineterminator='\n'); w.writerow(['measure', 'k', 'n', 'result'])
            for m, (a, b, c) in res.items(): w.writerow([m, a, b, c])
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(Path(__file__).resolve().parent.parent)); ap.add_argument('--out')
    a = ap.parse_args(); score(a.root, a.out)


if __name__ == '__main__':
    main()
