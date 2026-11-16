"""E8b pooled scorer (amendment B1). Runs once; the verdict is final.

Primary: H-E8-1 pooled over E8 items (e7_key + e8_* dirs) and T47 items (e8b_key + e8b_* dirs):
         set=new, truth SPEC/IMPL, match SAME; final kind = C(a)==C(b) else UNCLEAR.
Secondary: T47 items alone. Miss-rate (T47): P(DIFFERENT|PARTIAL | P4 ACCIDENTAL) > P(... | P4 DELIBERATE).
"""
import argparse, csv, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from score_e8 import report, kappa, KINDS, fisher_one_sided  # noqa: E402


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def build(root, keyf, match_dir, code_dir, ca, cb, jid, tag):
    key = rd(root / 'E7_mining/key' / keyf)
    match = rd(root / 'E2_labelling' / match_dir / f'match_{jid}.csv')
    c1 = rd(root / 'E2_labelling' / code_dir / f'codes_{ca}.csv')
    c2 = rd(root / 'E2_labelling' / code_dir / f'codes_{cb}.csv')
    assert set(match) == set(key), f'{tag}: match/key item mismatch'
    out = []
    for i in sorted(key):
        m = match[i]['match'].strip().upper()
        assert m in ('SAME', 'PARTIAL', 'DIFFERENT', 'NONE'), (i, m)
        k1 = c1[i]['divergence_kind'].strip().upper() if i in c1 else None
        k2 = c2[i]['divergence_kind'].strip().upper() if i in c2 else None
        if m == 'NONE' or k1 is None or k2 is None:
            kind = None
        else:
            assert k1 in KINDS and k2 in KINDS, (i, k1, k2)
            kind = k1 if k1 == k2 else 'UNCLEAR'
        out.append({'id': f'{tag}:{i}', 'raw': i, 'set': key[i]['set'], 'truth': key[i]['truth_direction'].strip().upper(),
                    'match': m, 'kind': kind, 'k1': k1, 'k2': k2})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); args = ap.parse_args()
    root = Path(args.root)
    e8 = build(root, 'e7_key.csv', 'e8_match', 'e8_code', 'C3', 'C4', 'J1', 'E8')
    t47 = build(root, 'e8b_key.csv', 'e8b_match', 'e8b_code', 'C5', 'C6', 'J2', 'T47')
    sel = lambda rows, ms=('SAME',): [r for r in rows if r['set'] == 'new' and r['truth'] in ('SPEC', 'IMPL') and r['match'] in ms]
    coded = [r for r in t47 if r['k1'] is not None and r['k2'] is not None]
    print(f'T47 match counts [new]:', {m: sum(r['match'] == m for r in t47 if r['set'] == 'new') for m in ('SAME', 'PARTIAL', 'DIFFERENT', 'NONE')})
    print(f'   kappa C5-C6 [T47 coded] = {kappa([r["k1"] for r in coded], [r["k2"] for r in coded], KINDS):.3f} (n={len(coded)})')
    out = [report('PRIMARY pooled E8+T47 SAME', sel(e8) + sel(t47), confirmatory=True),
           report('secondary T47 SAME', sel(t47)),
           report('sens pooled SAME+PARTIAL', sel(e8, ('SAME', 'PARTIAL')) + sel(t47, ('SAME', 'PARTIAL'))),
           report('sens pooled all non-NONE', sel(e8, ('SAME', 'PARTIAL', 'DIFFERENT')) + sel(t47, ('SAME', 'PARTIAL', 'DIFFERENT')))]
    p4p = root / 'E2_labelling/e8b_proponly/codes_P4.csv'
    if p4p.is_file():
        p4 = rd(p4p)
        rows = [r for r in t47 if r['set'] == 'new' and r['truth'] in ('SPEC', 'IMPL') and r['match'] != 'NONE']
        kind = lambda r: p4[r['raw']]['divergence_kind'].strip().upper()
        miss = lambda r: r['match'] in ('DIFFERENT', 'PARTIAL')
        a = sum(kind(r) == 'ACCIDENTAL' and miss(r) for r in rows); b = sum(kind(r) == 'ACCIDENTAL' and not miss(r) for r in rows)
        c = sum(kind(r) == 'DELIBERATE' and miss(r) for r in rows); d = sum(kind(r) == 'DELIBERATE' and not miss(r) for r in rows)
        print(f'   [miss-rate T47] ACCIDENTAL missed {a}/{a+b} | DELIBERATE missed {c}/{c+d} | Fisher one-sided p={fisher_one_sided(a, b, c, d):.4f}')
    with open(here / 'e8b_scores.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)


if __name__ == '__main__':
    main()
