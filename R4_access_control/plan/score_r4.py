"""R4 scorer (frozen before mining). Run from R4_access_control/: /usr/bin/python3 -I -B plan/score_r4.py [--root R] [--out F]
Inputs (relative to root):
  mining/key/r4_key.csv                          item_id, repo, ecosystem, fix_silent (true/false), fix_touches_contract, fix_touches_annotation, test_in_fix
  packages/r4_blind/codes_G1.csv, codes_G2.csv   GPT coders (primary)
  packages/r4_kb*/codes_H1.csv, codes_H2.csv     Claude coders (cross-family check)
Implements R4_PLAN.md §5 (final codes) and §7 (E-R4-1, H-R4-1..4, within-family kappa, exploratory tables)."""
import argparse, collections, csv, math, random, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)

KINDS = {'OBJECT_LEVEL', 'FUNCTION_LEVEL', 'PROPERTY_LEVEL', 'MISSING_AUTHENTICATION', 'TENANT_ISOLATION', 'OTHER'}
DEP = ('ac_kind', 'principals_needed', 'observable_via_http', 'contract_operation', 'contract_security', 'policy_in_contract', 'fix_location')
FIELDS = ('ac_relevant',) + DEP
NA = {'', 'NA'}
ALLOWED = {'ac_relevant': {'YES', 'NO', 'UNCLEAR'},
           'ac_kind': KINDS | {'UNCLEAR'} | NA,
           'principals_needed': {'NONE', 'ONE', 'TWO_SAME_ROLE', 'TWO_ROLES', 'UNCLEAR'} | NA,
           'observable_via_http': {'YES', 'NO', 'UNCLEAR'} | NA,
           'contract_operation': {'PRESENT', 'ABSENT', 'NO_CONTRACT', 'UNCLEAR'} | NA,
           'contract_security': {'DECLARED', 'NOT_DECLARED', 'UNCLEAR'} | NA,
           'policy_in_contract': {'YES', 'NO', 'UNCLEAR'} | NA,
           'fix_location': {'HANDLER', 'MIDDLEWARE_FILTER', 'SERVICE_LOGIC', 'DATA_QUERY', 'MODEL_BINDING', 'OTHER', 'UNCLEAR'} | NA}
MIN_H = 20; MIN_K = 30; KAPPA_T = 0.6


def rd(p):
    return list(csv.DictReader(open(p, newline='', encoding='utf-8-sig')))


def norm(v):
    return (v or '').strip().upper()


def load_codes(paths):
    out = {}
    for p in paths:
        for r in rd(p):
            row = {f: norm(r.get(f)) for f in FIELDS}
            for f in FIELDS:
                if row[f] not in ALLOWED[f]: raise ValueError(f'{p}: {r.get("item_id")} {f}={row[f]!r}')
            if row['ac_relevant'] != 'YES':
                for f in DEP: row[f] = 'NA'
            else:
                for f in DEP:
                    if row[f] in NA: row[f] = 'NA'
                if row['contract_operation'] != 'PRESENT': row['contract_security'] = 'NA'
            out[r['item_id'].strip()] = row
    return out


def final(a, b):
    """Field-wise agreement; disagreement -> UNCLEAR. Dependent fields only when both coders said YES."""
    ac = a['ac_relevant'] if a['ac_relevant'] == b['ac_relevant'] else 'UNCLEAR'
    out = {'ac_relevant': ac}
    for f in DEP:
        out[f] = (a[f] if a[f] == b[f] else 'UNCLEAR') if ac == 'YES' else 'NA'
    if ac == 'YES' and out['contract_operation'] != 'PRESENT':
        out['contract_security'] = 'NA'
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


def cluster_boot(items, sel, hit, B=2000, seed=1):
    """CI of share(hit | sel) resampling repositories."""
    by = collections.defaultdict(list)
    for it in items: by[it['repo']].append(it)
    repos = sorted(by); rng = random.Random(seed); vals = []
    for _ in range(B):
        s = [it for r in (rng.choice(repos) for _ in repos) for it in by[r] if sel(it)]
        if s: vals.append(sum(hit(it) for it in s) / len(s))
    if not vals: return float('nan'), float('nan')
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f'{k}/{n} = {p:.3f} Wilson [{lo:.3f}, {hi:.3f}]' if n else f'{k}/0'


# hypothesis selectors: (selection, hit)
H = {
    'H-R4-1': (lambda c: c['ac_relevant'] == 'YES' and c['principals_needed'] not in ('UNCLEAR', 'NA'),
               lambda c: c['principals_needed'] in ('TWO_SAME_ROLE', 'TWO_ROLES')),
    'H-R4-2': (lambda c: c['ac_relevant'] == 'YES', lambda c: c['silent']),
    'H-R4-3': (lambda c: c['ac_relevant'] == 'YES' and c['contract_operation'] == 'PRESENT' and c['policy_in_contract'] in ('YES', 'NO'),
               lambda c: c['policy_in_contract'] == 'NO'),
}


def score(root, out=None):
    root = Path(root); P = root / 'packages'
    key = {r['item_id']: r for r in rd(root / 'mining/key/r4_key.csv')}
    G1, G2 = load_codes([P / 'r4_blind/codes_G1.csv']), load_codes([P / 'r4_blind/codes_G2.csv'])
    kb = sorted(P.glob('r4_kb*'))
    H1 = load_codes([d / 'codes_H1.csv' for d in kb]); H2 = load_codes([d / 'codes_H2.csv' for d in kb])
    ids = sorted(key)
    for nm, c in (('G1', G1), ('G2', G2), ('H1', H1), ('H2', H2)):
        miss = [i for i in ids if i not in c]
        if miss: raise ValueError(f'{nm} missing {len(miss)} items, e.g. {miss[:3]}')
    items = []
    for i in ids:
        k = key[i]; g = final(G1[i], G2[i]); h = final(H1[i], H2[i])
        items.append({'id': i, 'repo': k['repo'], 'eco': k.get('ecosystem', ''), 'silent': k['fix_silent'].strip().lower() == 'true',
                      'test': k.get('test_in_fix', '').strip().lower() == 'true', 'g': g, 'h': h})
    n = len(items); res = collections.OrderedDict()
    print(f'== R4: n={n} items; repos {len({it["repo"] for it in items})}; ecosystems {dict(collections.Counter(it["eco"] for it in items))}')
    for f in FIELDS:
        print(f'   kappa {f}: GPT {kappa([G1[i][f] for i in ids], [G2[i][f] for i in ids]):.3f}  Claude {kappa([H1[i][f] for i in ids], [H2[i][f] for i in ids]):.3f}')
    gac = collections.Counter(it['g']['ac_relevant'] for it in items)
    print(f'   GPT final ac_relevant YES/NO/UNCLEAR = {gac["YES"]}/{gac["NO"]}/{gac["UNCLEAR"]}')
    ac = [it for it in items if it['g']['ac_relevant'] == 'YES']
    res['E-R4-1 AC_RELEVANT'] = (gac['YES'], n, fmt(gac['YES'], n) + ' cluster-boot [%.3f, %.3f]' % cluster_boot(items, lambda it: True, lambda it: it['g']['ac_relevant'] == 'YES'))
    print('   E-R4-1 AC-relevant share: ' + res['E-R4-1 AC_RELEVANT'][2])
    for f in DEP:
        cnt = collections.Counter(it['g'][f] for it in ac)
        print(f'   E-R4-1 {f} (AC-relevant, n={len(ac)}): ' + ', '.join(f'{v} {c} ({c / len(ac):.2f})' for v, c in cnt.most_common()) if ac else f'   E-R4-1 {f}: n=0')
    sil = sum(it['silent'] for it in ac); tst = sum(it['test'] for it in ac)
    print(f'   fix_silent among AC-relevant: {fmt(sil, len(ac))}; test_in_fix: {fmt(tst, len(ac))}')
    for hn, (sel, hit) in H.items():
        S = [it for it in items if sel({**it['g'], 'silent': it['silent']})]
        k = sum(hit({**it['g'], 'silent': it['silent']}) for it in S); m = len(S)
        if m < MIN_H:
            verdict, p = f'INSUFFICIENT (n={m} < {MIN_H})', float('nan')
        else:
            p = binom_upper(k, m); verdict = 'PASS' if (k / m > 0.5 and p < 0.05) else 'FAIL'
        lo, hi = cluster_boot(items, lambda it: sel({**it['g'], 'silent': it['silent']}), lambda it: hit({**it['g'], 'silent': it['silent']}))
        res[hn] = (k, m, f'{fmt(k, m)} cluster-boot [{lo:.3f}, {hi:.3f}]; one-sided binomial vs 0.5 p={p:.3g} -> {verdict}')
        print(f'   {hn}: {res[hn][2]}')
        # cross-family check and leave-one-repo-out (exploratory)
        Sh = [it for it in items if sel({**it['h'], 'silent': it['silent']})]
        kh = sum(hit({**it['h'], 'silent': it['silent']}) for it in Sh)
        lo_ = []
        for r in sorted({it['repo'] for it in items}):
            s2 = [it for it in S if it['repo'] != r]
            if s2: lo_.append((sum(hit({**it['g'], 'silent': it['silent']}) for it in s2) / len(s2), r))
        loo = f'min {min(lo_)[0]:.3f} (without {min(lo_)[1]}), max {max(lo_)[0]:.3f} (without {max(lo_)[1]})' if lo_ else 'n/a'
        print(f'      Claude-final: {fmt(kh, len(Sh))}; leave-one-repo-out: {loo}')
    both = [it for it in items if it['g']['ac_relevant'] == 'YES' and it['h']['ac_relevant'] == 'YES'
            and it['g']['ac_kind'] != 'UNCLEAR' and it['h']['ac_kind'] != 'UNCLEAR']
    xs = [it['g']['ac_kind'] for it in both]; ys = [it['h']['ac_kind'] for it in both]
    if len(both) < MIN_K:
        v4, kp = f'INSUFFICIENT (n={len(both)} < {MIN_K})', float('nan')
    else:
        kp = kappa(xs, ys); v4 = 'PASS' if kp >= KAPPA_T else 'FAIL'
    res['H-R4-4'] = (sum(x == y for x, y in zip(xs, ys)), len(both), f'agree {sum(x == y for x, y in zip(xs, ys))}/{len(both)}, kappa {kp:.3f} -> {v4}')
    print(f'   H-R4-4 cross-family ac_kind: {res["H-R4-4"][2]}')
    xa = [it['g']['ac_relevant'] for it in items if 'UNCLEAR' not in (it['g']['ac_relevant'], it['h']['ac_relevant'])]
    ya = [it['h']['ac_relevant'] for it in items if 'UNCLEAR' not in (it['g']['ac_relevant'], it['h']['ac_relevant'])]
    print(f'   cross-family ac_relevant (both decided n={len(xa)}): kappa {kappa(xa, ya):.3f}')
    hac = collections.Counter(it['h']['ac_relevant'] for it in items)
    print(f'   Claude final ac_relevant YES/NO/UNCLEAR = {hac["YES"]}/{hac["NO"]}/{hac["UNCLEAR"]}')
    print('   EXPLORATORY principals x contract_security: ' + str(dict(sorted(collections.Counter((it['g']['principals_needed'], it['g']['contract_security']) for it in ac).items()))))
    print('   EXPLORATORY ac_kind x fix_location: ' + str(dict(sorted(collections.Counter((it['g']['ac_kind'], it['g']['fix_location']) for it in ac).items()))))
    print('   EXPLORATORY ac_kind x principals: ' + str(dict(sorted(collections.Counter((it['g']['ac_kind'], it['g']['principals_needed']) for it in ac).items()))))
    for e in sorted({it['eco'] for it in items}):
        s = [it for it in items if it['eco'] == e]; a = [it for it in s if it['g']['ac_relevant'] == 'YES']
        print(f'   EXPLORATORY eco {e}: n={len(s)} AC {len(a)} silent {sum(it["silent"] for it in a)} '
              f'multi-principal {sum(it["g"]["principals_needed"] in ("TWO_SAME_ROLE", "TWO_ROLES") for it in a)}')
    if out:
        with open(out, 'w', newline='') as fh:
            w = csv.writer(fh, lineterminator='\n'); w.writerow(['measure', 'k', 'n', 'result'])
            for m_, (a, b, c) in res.items(): w.writerow([m_, a, b, c])
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(Path(__file__).resolve().parent.parent)); ap.add_argument('--out')
    a = ap.parse_args(); score(a.root, a.out)


if __name__ == '__main__':
    main()
