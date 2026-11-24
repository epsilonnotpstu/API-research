"""R4b scorer (frozen before packaging). Run from R4_access_control/: /usr/bin/python3 -I -B plan/score_r4b.py [--root R] [--out F]
Inputs: mining/key/r4b_key.csv (r4b_id, r4_id, repo, ...), packages/r4b_blind/codes_G3.csv, codes_G4.csv, packages/r4b_kb*/codes_H3.csv,
codes_H4.csv, packages/r4b_blind/<id>/contract/ (for the mechanical locator check). Optional: R4 GPT final codes for the exploratory cross-tab
(recomputed from packages/r4_blind/codes_G1/G2.csv with plan/score_r4.py). Implements R4b_PLAN.md."""
import argparse, collections, csv, math, re, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_r4 import wilson, binom_upper, kappa, fmt  # noqa: E402  (frozen R4 helpers)

FIELDS = ('contract_operation', 'contract_security', 'policy_in_contract')
ALLOWED = {'contract_operation': {'PRESENT', 'ABSENT', 'NO_CONTRACT', 'UNCLEAR'},
           'contract_security': {'DECLARED', 'NOT_DECLARED', 'UNCLEAR', 'NA', ''},
           'policy_in_contract': {'YES', 'NO', 'UNCLEAR'}}
MIN_H = 20


def rd(p):
    return list(csv.DictReader(open(p, newline='', encoding='utf-8-sig')))


def load(paths):
    out = {}
    for p in paths:
        for r in rd(p):
            row = {f: (r.get(f) or '').strip().upper() for f in FIELDS}
            for f in FIELDS:
                if row[f] not in ALLOWED[f]: raise ValueError(f'{p}: {r.get("item_id")} {f}={row[f]!r}')
            if row['contract_operation'] != 'PRESENT': row['contract_security'] = 'NA'
            elif row['contract_security'] == '': row['contract_security'] = 'UNCLEAR'
            row['op_locator'] = (r.get('op_locator') or '').strip(); row['operation'] = (r.get('operation') or '').strip()
            out[r['item_id'].strip()] = row
    return out


def final(a, b):
    out = {f: (a[f] if a[f] == b[f] else 'UNCLEAR') for f in FIELDS}
    if out['contract_operation'] != 'PRESENT': out['contract_security'] = 'NA'
    return out


def locator_valid(root, iid, row):
    """op_locator 'contract/<file>:<line>' exists and a path segment of the coded operation is within +-3 lines."""
    m = re.match(r'^(?:contract/)?([^:]+):(\d+)', row['op_locator'])
    if not m: return False
    f = Path(root) / 'packages/r4b_blind' / iid / 'contract' / m.group(1)
    if not f.is_file(): return False
    lines = f.read_text(errors='replace').splitlines(); n = int(m.group(2))
    window = '\n'.join(lines[max(0, n - 4):n + 3]).lower()
    segs = [s for op in row['operation'].split(';') for s in re.split(r'[/\s]+', op.split(' ', 1)[-1].lower())
            if s and not s.startswith('{') and s not in ('get', 'post', 'put', 'patch', 'delete', 'api', 'v1', 'v2', 'v3')]
    return bool(segs) and any(s in window for s in segs)


def score(root, out=None):
    root = Path(root); P = root / 'packages'
    key = {r['r4b_id']: r for r in rd(root / 'mining/key/r4b_key.csv')}
    G3, G4 = load([P / 'r4b_blind/codes_G3.csv']), load([P / 'r4b_blind/codes_G4.csv'])
    kb = sorted(P.glob('r4b_kb*')); H3 = load([d / 'codes_H3.csv' for d in kb]); H4 = load([d / 'codes_H4.csv' for d in kb])
    ids = sorted(key)
    for nm, c in (('G3', G3), ('G4', G4), ('H3', H3), ('H4', H4)):
        miss = [i for i in ids if i not in c]
        if miss: raise ValueError(f'{nm} missing {len(miss)} items, e.g. {miss[:3]}')
    g = {i: final(G3[i], G4[i]) for i in ids}; h = {i: final(H3[i], H4[i]) for i in ids}
    n = len(ids); res = collections.OrderedDict()
    print(f'== R4b: n={n} items (R4 AC-relevant, GPT final); repos {len({key[i]["repo"] for i in ids})}')
    for f in FIELDS:
        print(f'   kappa {f}: GPT {kappa([G3[i][f] for i in ids], [G4[i][f] for i in ids]):.3f}  Claude {kappa([H3[i][f] for i in ids], [H4[i][f] for i in ids]):.3f}')
    for fam, c in (('GPT', g), ('Claude', h)):
        for f in FIELDS:
            print(f'   {fam} final {f}: ' + ', '.join(f'{v} {k}' for v, k in sorted(((v, k) for k, v in collections.Counter(c[i][f] for i in ids).items()), reverse=True)))
    pres = sum(g[i]['contract_operation'] == 'PRESENT' for i in ids); unc = sum(g[i]['contract_operation'] == 'UNCLEAR' for i in ids)
    res['E-R4-2a PRESENT'] = (pres, n, fmt(pres, n) + '  (R4: 41/102)')
    res['E-R4-2b UNCLEAR'] = (unc, n, fmt(unc, n) + '  (R4: 27/102)')
    print('   E-R4-2a share PRESENT: ' + res['E-R4-2a PRESENT'][2]); print('   E-R4-2b share UNCLEAR: ' + res['E-R4-2b UNCLEAR'][2])
    for fam, c in (('GPT', g), ('Claude', h)):
        S = [i for i in ids if c[i]['contract_operation'] == 'PRESENT' and c[i]['policy_in_contract'] in ('YES', 'NO')]
        k = sum(c[i]['policy_in_contract'] == 'NO' for i in S); m = len(S)
        if m < MIN_H: v, p = f'INSUFFICIENT (n={m} < {MIN_H})', float('nan')
        else: p = binom_upper(k, m); v = 'PASS' if (k / m > 0.5 and p < 0.05) else 'FAIL'
        tag = 'H-R4-3b' if fam == 'GPT' else 'H-R4-3b (Claude check)'
        res[tag] = (k, m, f'{fmt(k, m)}; one-sided binomial vs 0.5 p={p:.3g} -> {v}'); print(f'   {tag} policy NO among PRESENT+decided: {res[tag][2]}')
        S = [i for i in ids if c[i]['contract_operation'] == 'PRESENT' and c[i]['contract_security'] in ('DECLARED', 'NOT_DECLARED')]
        k = sum(c[i]['contract_security'] == 'NOT_DECLARED' for i in S); m = len(S)
        if m < MIN_H: v, p = f'INSUFFICIENT (n={m} < {MIN_H})', float('nan')
        else: p = binom_upper(k, m, 0.1); v = 'PASS' if p < 0.05 else 'FAIL'
        tag = 'H-R4-5' if fam == 'GPT' else 'H-R4-5 (Claude check)'
        res[tag] = (k, m, f'NOT_DECLARED {fmt(k, m)}; one-sided binomial vs 0.1 p={p:.3g} -> {v}'); print(f'   {tag}: {res[tag][2]}')
    xs = [g[i]['contract_operation'] for i in ids if 'UNCLEAR' not in (g[i]['contract_operation'], h[i]['contract_operation'])]
    ys = [h[i]['contract_operation'] for i in ids if 'UNCLEAR' not in (g[i]['contract_operation'], h[i]['contract_operation'])]
    res['cross-family kappa contract_operation'] = (sum(x == y for x, y in zip(xs, ys)), len(xs), f'kappa {kappa(xs, ys):.3f}')
    print(f'   cross-family contract_operation (both decided n={len(xs)}): agree {sum(x == y for x, y in zip(xs, ys))}, kappa {kappa(xs, ys):.3f}')
    for nm, c in (('G3', G3), ('G4', G4), ('H3', H3), ('H4', H4)):
        pr = [i for i in ids if c[i]['contract_operation'] == 'PRESENT']
        ok = sum(locator_valid(root, i, c[i]) for i in pr)
        print(f'   EXPLORATORY locator validity {nm}: {ok}/{len(pr)}')
    try:
        from score_r4 import load_codes, final as final4
        R1, R2 = load_codes([P / 'r4_blind/codes_G1.csv']), load_codes([P / 'r4_blind/codes_G2.csv'])
        ct = collections.Counter((final4(R1[key[i]['r4_id']], R2[key[i]['r4_id']])['contract_operation'], g[i]['contract_operation']) for i in ids)
        print('   EXPLORATORY R4 GPT-final x R4b GPT-final contract_operation: ' + str(dict(sorted(ct.items()))))
    except (FileNotFoundError, KeyError) as e:
        print(f'   EXPLORATORY R4 cross-tab skipped: {type(e).__name__}')
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
