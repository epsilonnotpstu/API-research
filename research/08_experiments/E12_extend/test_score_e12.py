"""Self-test for score_e12.py. Run: /usr/bin/python3 -I -B test_score_e12.py"""
import csv, io, sys, tempfile, contextlib
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here)); sys.path.insert(0, str(here.parent / 'E4_triage'))
import score_e12 as S
from score_e4 import two_direction

D, A, U = 'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'


def w(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        d = csv.DictWriter(f, fieldnames=cols); d.writeheader(); d.writerows(rows)


def build(r, spec, key, acc, pkg, coders, kdirs, m1, m1f):
    """spec: (id, truth, cluster, g1, g2, k1, k2, m1, m1f)"""
    K = r / 'E7_mining/key'; E = r / 'E2_labelling'
    w(K / key, [{'item_id': s[0], 'truth_direction': s[1]} for s in spec], ['item_id', 'truth_direction'])
    w(K / acc, [{'item_id': s[0], 'candidate_id': s[2], 'repo': 'o/' + s[2][:1]} for s in spec], ['item_id', 'candidate_id', 'repo'])
    for j, c in ((3, coders[0]), (4, coders[1])):
        w(E / pkg / f'codes_{c}.csv', [{'item_id': s[0], 'divergence_kind': s[j]} for s in spec], ['item_id', 'divergence_kind'])
    if kdirs:
        h = len(spec) // 2
        for d, part in ((kdirs[0], spec[:h]), (kdirs[1], spec[h:])):
            for j, c in ((5, 'K3'), (6, 'K4')):
                w(E / d / f'codes_{c}.csv', [{'item_id': s[0], 'divergence_kind': s[j]} for s in part], ['item_id', 'divergence_kind'])
    for j, (d, n) in ((7, m1), (8, m1f)):
        w(E / d / f'labels_{n}.csv', [{'item_id': s[0], 'L1': s[j]} for s in spec], ['item_id', 'L1'])


def run(u, v):
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        build(r, u, 'e12_key.csv', 'accepted_full_t49.csv', 'e12_blind', ('C11', 'C12'), ('e12_kb1', 'e12_kb2'), ('e12_m1', 'L5'), ('e12_m1f', 'F3'))
        build(r, v, 'e10_key.csv', 'accepted_full_t48.csv', 'e10_blind', ('C9', 'C10'), None, ('e10_m1', 'L3'), ('e10_m1f', 'F1'))
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            o = S.score(r, two_direction)
        return o, buf.getvalue()


v = [(f'V{i:02d}', 'SPEC', f'v{i}', D, D, D, D, 'SPEC', 'SPEC') for i in range(3)]
# clean association, singleton clusters, R right and F3 wrong on 6 accidental items
u = [(f'U{i:02d}', 'SPEC', f'a{i}', D, D, D, D, 'SPEC', 'SPEC') for i in range(8)]
u += [(f'U{10+i:02d}', 'IMPL', f'b{i}', A, A, A, A, 'IMPL', 'SPEC' if i < 6 else 'IMPL') for i in range(8)]
u += [('U30', 'BOTH', 'z', D, D, D, D, 'SPEC', 'SPEC')]
o, txt = run(u, v)
assert 'PASS' in o['H-E12-1'][2] and 'PASS' in o['H-E12-2'][2] and 'PASS' in o['H-E12-3'][2], o
assert o['H-E12-4'][1] == 'R6/F0' and 'SIGNIFICANT' in o['H-E12-4'][2], o
assert 'BOTH excluded 1' in txt and 'POOLED E10+E12' in txt
# effect carried by one big cluster -> item p small, cluster p large -> FAIL
u2 = [(f'U{i:02d}', 'SPEC', 'big', D, D, D, D, 'SPEC', 'SPEC') for i in range(10)]
u2 += [(f'U{10+i:02d}', 'IMPL', f'b{i}', A, A, A, A, 'IMPL', 'IMPL') for i in range(5)]
u2 += [(f'U{20+i:02d}', 'SPEC', f'c{i}', A, A, A, A, 'IMPL', 'IMPL') for i in range(3)]
o, _ = run(u2, v)
assert 'FAIL' in o['H-E12-1'][2], o
assert 'INSUFFICIENT' in o['H-E12-4'][2]
assert abs(S.mcnemar_exact(6, 0) - 0.03125) < 1e-12 and S.mcnemar_exact(3, 3) == 1.0
print('test_score_e12: OK')
