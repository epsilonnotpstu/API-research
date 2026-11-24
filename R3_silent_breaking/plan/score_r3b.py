"""R3b scorer (frozen before packaging). Run from R3_silent_breaking/: /usr/bin/python3 -I -B plan/score_r3b.py [--root R] [--out F]
Inputs: mining/key/r3b_key.csv (r3b_id, r3_id, repo), packages/r3b_blind/codes_G5.csv, codes_G6.csv, packages/r3b_kb*/codes_H5.csv,
codes_H6.csv; packages/r3b_blind/<id>/contract/ (quote check). Implements R3b_PLAN.md."""
import argparse, collections, csv, math, re, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)

FIELDS = ('contract_operation', 'contract_specified')
ALLOWED = {'contract_operation': {'PRESENT', 'ABSENT', 'NO_CONTRACT', 'UNCLEAR'}, 'contract_specified': {'SPECIFIED', 'UNSPECIFIED', 'UNCLEAR'}}
MIN_H = 20


def rd(p):
    return list(csv.DictReader(open(p, newline='', encoding='utf-8-sig')))


def wilson(k, n, z=1.959963984540054):
    if n == 0: return float('nan'), float('nan'), float('nan')
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def binom_upper(k, n, p=0.5):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def kappa(xs, ys):
    n = len(xs)
    if n == 0: return float('nan')
    cats = sorted(set(xs) | set(ys)); po = sum(x == y for x, y in zip(xs, ys)) / n
    pe = sum((xs.count(c) / n) * (ys.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f'{k}/{n} = {p:.3f} Wilson [{lo:.3f}, {hi:.3f}]' if n else f'{k}/0'


def load(paths):
    out = {}
    for p in paths:
        for r in rd(p):
            row = {f: (r.get(f) or '').strip().upper() for f in FIELDS}
            for f in FIELDS:
                if row[f] not in ALLOWED[f]: raise ValueError(f'{p}: {r.get("item_id")} {f}={row[f]!r}')
            row['spec_quote'] = (r.get('spec_quote') or '').strip()
            out[r['item_id'].strip()] = row
    return out


def final(a, b):
    return {f: (a[f] if a[f] == b[f] else 'UNCLEAR') for f in FIELDS}


def norm(t):
    return re.sub(r'\s+', ' ', t.replace('\\"', '"').strip().strip('"\'')).lower()


def quote_valid(root, iid, q):
    q = norm(q)
    if len(q) < 4: return False
    d = Path(root) / 'packages/r3b_blind' / iid / 'contract'
    return any(q in norm(f.read_text(errors='replace')) for f in d.glob('*') if f.is_file() and f.name != 'INDEX.md')


def score(root, out=None):
    root = Path(root); P = root / 'packages'
    key = {r['r3b_id']: r for r in rd(root / 'mining/key/r3b_key.csv')}
    G5, G6 = load([P / 'r3b_blind/codes_G5.csv']), load([P / 'r3b_blind/codes_G6.csv'])
    kb = sorted(P.glob('r3b_kb*')); H5 = load([d / 'codes_H5.csv' for d in kb]); H6 = load([d / 'codes_H6.csv' for d in kb])
    ids = sorted(key)
    for nm, c in (('G5', G5), ('G6', G6), ('H5', H5), ('H6', H6)):
        miss = [i for i in ids if i not in c]
        if miss: raise ValueError(f'{nm} missing {len(miss)} items, e.g. {miss[:3]}')
    g = {i: final(G5[i], G6[i]) for i in ids}; h = {i: final(H5[i], H6[i]) for i in ids}
    n = len(ids); res = collections.OrderedDict()
    print(f'== R3b: n={n} items (R3 GPT-final observable YES); repos {len({key[i]["repo"] for i in ids})}')
    for f in FIELDS:
        print(f'   kappa {f}: GPT {kappa([G5[i][f] for i in ids], [G6[i][f] for i in ids]):.3f}  Claude {kappa([H5[i][f] for i in ids], [H6[i][f] for i in ids]):.3f}')
        for fam, c in (('GPT', g), ('Claude', h)):
            print(f'   {fam} final {f}: ' + str(dict(collections.Counter(c[i][f] for i in ids).most_common())))
    spec = sum(g[i]['contract_specified'] == 'SPECIFIED' for i in ids); pres = sum(g[i]['contract_operation'] == 'PRESENT' for i in ids)
    res['E-R3-2a SPECIFIED'] = (spec, n, fmt(spec, n) + '  (R3: 1/60)'); res['E-R3-2b PRESENT'] = (pres, n, fmt(pres, n))
    print('   E-R3-2a share SPECIFIED: ' + res['E-R3-2a SPECIFIED'][2]); print('   E-R3-2b share operation PRESENT: ' + res['E-R3-2b PRESENT'][2])
    for fam, c in (('GPT', g), ('Claude', h)):
        S = [i for i in ids if c[i]['contract_specified'] in ('SPECIFIED', 'UNSPECIFIED')]
        k = sum(c[i]['contract_specified'] == 'UNSPECIFIED' for i in S); m = len(S)
        if m < MIN_H: v, p = f'INSUFFICIENT (n={m} < {MIN_H})', float('nan')
        else: p = binom_upper(k, m); v = 'PASS' if (k / m > 0.5 and p < 0.05) else 'FAIL'
        tag = 'H-R3-4' if fam == 'GPT' else 'H-R3-4 (Claude check)'
        res[tag] = (k, m, f'UNSPECIFIED {fmt(k, m)}; one-sided binomial vs 0.5 p={p:.3g} -> {v}'); print(f'   {tag}: {res[tag][2]}')
    xs = [g[i]['contract_specified'] for i in ids if 'UNCLEAR' not in (g[i]['contract_specified'], h[i]['contract_specified'])]
    ys = [h[i]['contract_specified'] for i in ids if 'UNCLEAR' not in (g[i]['contract_specified'], h[i]['contract_specified'])]
    res['cross-family kappa contract_specified'] = (sum(x == y for x, y in zip(xs, ys)), len(xs), f'kappa {kappa(xs, ys):.3f}')
    print(f'   cross-family contract_specified (both decided n={len(xs)}): agree {sum(x == y for x, y in zip(xs, ys))}, kappa {kappa(xs, ys):.3f}')
    for nm, c in (('G5', G5), ('G6', G6), ('H5', H5), ('H6', H6)):
        sp = [i for i in ids if c[i]['contract_specified'] == 'SPECIFIED']
        print(f'   EXPLORATORY quote validity {nm}: {sum(quote_valid(root, i, c[i]["spec_quote"]) for i in sp)}/{len(sp)}')
    if out:
        with open(out, 'w', newline='') as fh:
            w = csv.writer(fh, lineterminator='\n'); w.writerow(['measure', 'k', 'n', 'result'])
            for m_, (a, b, c_) in res.items(): w.writerow([m_, a, b, c_])
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(Path(__file__).resolve().parent.parent)); ap.add_argument('--out')
    a = ap.parse_args(); score(a.root, a.out)


if __name__ == '__main__':
    main()
