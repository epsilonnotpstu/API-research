"""E9 pre-registered scorer (see E9_PLAN.md). Usage: score_e9.py [--root R] [--part A|B]

Kind = C(a) if C(a)==C(b) else UNCLEAR. R: DELIBERATE->SPEC, ACCIDENTAL->IMPL, UNCLEAR->ABSTAIN.
HYB: ACCIDENTAL->IMPL else M1 label. Macro-F1 via E4 two_direction (non SPEC/IMPL = miss).
"""
import argparse, csv, json, math, sys
from pathlib import Path

here = Path(__file__).resolve().parent


def rd(p):
    return {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}


def kinds(pa, pb):
    a, b = rd(pa), rd(pb)
    return {i: (a[i]['divergence_kind'].strip().upper() if a[i]['divergence_kind'].strip().upper() == b[i]['divergence_kind'].strip().upper() else 'UNCLEAR')
            for i in a if i in b}


def sign_p(w, l):
    n = w + l
    return sum(math.comb(n, k) for k in range(w, n + 1)) / 2 ** n if n else 1.0


def evaluate(items, labellers, two_direction, out_rows, tag):
    """items: list of dict(id, truth, kind); labellers: {name: {id: L1}}"""
    print(f'== {tag}: n={len(items)} (SPEC {sum(r["truth"]=="SPEC" for r in items)}, IMPL {sum(r["truth"]=="IMPL" for r in items)}); '
          f'kinds D/A/U = {sum(r["kind"]=="DELIBERATE" for r in items)}/{sum(r["kind"]=="ACCIDENTAL" for r in items)}/{sum(r["kind"]=="UNCLEAR" for r in items)}')
    rule = {r['id']: {'DELIBERATE': 'SPEC', 'ACCIDENTAL': 'IMPL'}.get(r['kind'], 'ABSTAIN') for r in items}

    def mf(pred):
        s = [pred[r['id']] for r in items if r['truth'] == 'SPEC']; p = [pred[r['id']] for r in items if r['truth'] == 'IMPL']
        per, m, acc, cov = two_direction(s, p); return m, acc, cov
    m, acc, cov = mf(rule)
    print(f'   R rule: macro-F1 {m:.3f} decided-acc {acc:.2f} coverage {cov:.2f}')
    out_rows.append({'part': tag, 'method': 'R', 'macro_f1': round(m, 4), 'acc': round(acc, 4), 'cov': round(cov, 4)})
    W = L = 0; per_lab = {}
    for name, lab in labellers.items():
        m1 = {r['id']: lab[r['id']] for r in items}
        hyb = {r['id']: ('IMPL' if r['kind'] == 'ACCIDENTAL' else m1[r['id']]) for r in items}
        w = sum(hyb[r['id']] != m1[r['id']] and hyb[r['id']] == r['truth'] and m1[r['id']] != r['truth'] for r in items)
        l = sum(hyb[r['id']] != m1[r['id']] and m1[r['id']] == r['truth'] and hyb[r['id']] != r['truth'] for r in items)
        o = sum(hyb[r['id']] != m1[r['id']] for r in items)
        ov = [r for r in items if r['kind'] == 'ACCIDENTAL']; ovc = sum(r['truth'] == 'IMPL' for r in ov)
        W += w; L += l; per_lab[name] = (w, l, o)
        for meth, pred in (('M1', m1), ('HYB', hyb)):
            m, acc, cov = mf(pred)
            print(f'   {name} {meth}: macro-F1 {m:.3f} decided-acc {acc:.2f} coverage {cov:.2f}')
            out_rows.append({'part': tag, 'method': f'{name}_{meth}', 'macro_f1': round(m, 4), 'acc': round(acc, 4), 'cov': round(cov, 4)})
        print(f'   {name} discordant {o}: wins {w}, losses {l} | HYB override precision {ovc}/{len(ov)}')
        for k in ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'):
            g = [r for r in items if r['kind'] == k]
            if g: print(f'      M1 correct | {k}: {sum(m1[r["id"]] == r["truth"] for r in g)}/{len(g)}')
    if len(labellers) == 2:
        a, b = list(labellers.values()); ag = sum(a[r['id']] == b[r['id']] for r in items)
        print(f'   labeller agreement {ag}/{len(items)}')
    n = W + L; p = sign_p(W, L)
    verdict = 'INSUFFICIENT' if n < 5 else ('PASS' if p < 0.05 and all(w >= l for w, l, _ in per_lab.values()) else 'FAIL')
    print(f'   H-E9-1 [{tag}] pooled wins {W} losses {L} (discordant {n}) sign one-sided p={p:.4f} -> {verdict}')
    out_rows.append({'part': tag, 'method': 'H-E9-1', 'macro_f1': '', 'acc': f'W{W}/L{L}', 'cov': f'p={p:.4f} {verdict}'})


def part_a(root, two_direction, out):
    e6 = rd(root / 'E6_realfix/e6_key.csv')
    log = {it['item_id']: it for it in json.load(open(root / 'E6_realfix/e6_build_log.json'))['items']}
    ca = rd(root / 'E6_realfix/combined_accepted.csv')
    e7 = [r for r in csv.DictReader(open(root / 'E7_mining/key/e7_key.csv', newline='')) if r['set'] == 'e6_exploratory']
    to_x = {(r['fix_commit'], r['operation']): r['item_id'] for r in e7}
    kd = kinds(root / 'E2_labelling/e7_blind/codes_C1.csv', root / 'E2_labelling/e7_blind/codes_C2.csv')
    items = []
    for k, r in sorted(e6.items()):
        src = ca[log[k]['source_item']]; x = to_x[(src['fix_commit'], src['operation'])]
        items.append({'id': k, 'truth': r['truth_direction'].strip().upper(), 'kind': kd[x]})
    labs = {n: {i: v['L1'].strip().upper() for i, v in rd(root / f'E2_labelling/e6_blind/labels_{n}.csv').items()} for n in ('Y1', 'Y2')}
    evaluate(items, labs, two_direction, out, 'A_retrospective_E6')


def part_b(root, two_direction, out):
    kx = rd(root / 'E7_mining/key/e7_key.csv'); kw = rd(root / 'E7_mining/key/e8b_key.csv')
    kdx = kinds(root / 'E2_labelling/e7_blind/codes_C1.csv', root / 'E2_labelling/e7_blind/codes_C2.csv')
    kdw = kinds(root / 'E2_labelling/e8b_blind/codes_C7.csv', root / 'E2_labelling/e8b_blind/codes_C8.csv')
    pkg = [r['item_id'] for r in csv.DictReader(open(root / 'E2_labelling/e9_m1/items.csv', newline=''))]
    items = []
    for i in pkg:
        k, kd = (kx, kdx) if i.startswith('X') else (kw, kdw)
        assert k[i]['set'] == 'new', i
        t = k[i]['truth_direction'].strip().upper()
        if t in ('SPEC', 'IMPL'): items.append({'id': i, 'truth': t, 'kind': kd[i]})
    labs = {}
    for n in ('L1', 'L2'):
        lab = rd(root / f'E2_labelling/e9_m1/labels_{n}.csv'); assert set(pkg) <= set(lab), n
        labs[n] = {i: v['L1'].strip().upper() for i, v in lab.items()}
    evaluate(items, labs, two_direction, out, 'B_confirmatory')
    for pre in ('X', 'W'):
        evaluate([r for r in items if r['id'].startswith(pre)], labs, two_direction, [], f'B_descriptive_{pre}_only')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(here.parent)); ap.add_argument('--part', choices=('A', 'B'), required=True)
    a = ap.parse_args(); root = Path(a.root)
    sys.path.insert(0, str(root / 'E4_triage')); sys.path.insert(0, str(here.parent / 'E4_triage'))
    from score_e4 import two_direction
    out = []
    (part_a if a.part == 'A' else part_b)(root, two_direction, out)
    with open(here / f'e9_scores_{a.part}.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['part', 'method', 'macro_f1', 'acc', 'cov']); w.writeheader(); w.writerows(out)


if __name__ == '__main__':
    main()
