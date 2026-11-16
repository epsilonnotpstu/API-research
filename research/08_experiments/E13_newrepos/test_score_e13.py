"""Self-test for score_e13.py. Run: /usr/bin/python3 -I -B test_score_e13.py"""
import csv, io, sys, tempfile, contextlib
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here)); sys.path.insert(0, str(here.parent / 'E4_triage'))
import score_e13 as S
from score_e4 import two_direction

D, A, U = 'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'


def w(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        d = csv.DictWriter(f, fieldnames=cols); d.writeheader(); d.writerows(rows)


def build(r, spec, key, acc, pkg, coders, kdirs, kc, m1, m1f):
    """spec: (id, truth, cluster, repo, g1, g2, k1, k2, m1, m1f)"""
    K = r / 'E7_mining/key'; E = r / 'E2_labelling'
    w(K / key, [{'item_id': s[0], 'truth_direction': s[1]} for s in spec], ['item_id', 'truth_direction'])
    w(K / acc, [{'item_id': s[0], 'candidate_id': s[2], 'repo': 'o/' + s[3]} for s in spec], ['item_id', 'candidate_id', 'repo'])
    for j, c in ((4, coders[0]), (5, coders[1])):
        w(E / pkg / f'codes_{c}.csv', [{'item_id': s[0], 'divergence_kind': s[j]} for s in spec], ['item_id', 'divergence_kind'])
    if kdirs:
        n = len(kdirs); size = -(-len(spec) // n)
        for b, d in enumerate(kdirs):
            part = spec[b * size:(b + 1) * size]
            for j, c in ((6, kc[0]), (7, kc[1])):
                w(E / d / f'codes_{c}.csv', [{'item_id': s[0], 'divergence_kind': s[j]} for s in part], ['item_id', 'divergence_kind'])
    for j, (d, n) in ((8, m1), (9, m1f)):
        w(E / d / f'labels_{n}.csv', [{'item_id': s[0], 'L1': s[j]} for s in spec], ['item_id', 'L1'])


def run(q):
    v = [(f'V{i:02d}', 'SPEC', f'v{i}', 'r', D, D, D, D, 'SPEC', 'SPEC') for i in range(3)]
    u = [(f'U{i:02d}', 'IMPL', f'u{i}', 'r', A, A, A, A, 'IMPL', 'IMPL') for i in range(3)]
    with tempfile.TemporaryDirectory() as t:
        r = Path(t)
        build(r, q, 'e13_key.csv', 'accepted_full_t50.csv', 'e13_blind', ('C13', 'C14'), ('e13_kb1', 'e13_kb2', 'e13_kb3'), ('K5', 'K6'), ('e13_m1', 'L6'), ('e13_m1f', 'F4'))
        build(r, v, 'e10_key.csv', 'accepted_full_t48.csv', 'e10_blind', ('C9', 'C10'), None, None, ('e10_m1', 'L3'), ('e10_m1f', 'F1'))
        build(r, u, 'e12_key.csv', 'accepted_full_t49.csv', 'e12_blind', ('C11', 'C12'), None, None, ('e12_m1', 'L5'), ('e12_m1f', 'F3'))
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            o = S.score(r, two_direction, str(r / 'out.csv'))
        return o, buf.getvalue()


# 1) clean association across 4 repos; Claude splits UNCLEAR on two; R right and F4 wrong on 6
q = [(f'Q{i:02d}', 'SPEC', f'a{i}', f'r{i % 4}', D, D, D, D, 'SPEC', 'SPEC') for i in range(10)]
q += [(f'Q{10+i:02d}', 'IMPL', f'b{i}', f'r{i % 4}', A, A, A, A if i > 1 else D, 'IMPL', 'SPEC' if i < 6 else 'IMPL') for i in range(10)]
q += [('Q30', 'BOTH', 'z', 'r0', D, D, D, D, 'SPEC', 'SPEC')]
o, txt = run(q)
assert 'PASS' in o['H-E13-1'][2] and 'PASS' in o['H-E13-2'][2] and 'PASS' in o['H-E13-3'][2], o
assert o['H-E13-4'][1] == 'R6/F0' and 'SIGNIFICANT' in o['H-E13-4'][2], o
assert 'Claude final D/A/U = 10/8/2' in txt, txt
assert 'BOTH excluded 1' in txt and 'POOLED E10+E12+E13 (n=26)' in txt and 'repos 4' in txt
assert o['precision:ACCIDENTAL->IMPL'][2].startswith('10/10'), o
assert 'POOLED ACCIDENTAL->IMPL: 13/13' in txt.replace('precision ', ''), txt
# 2) effect carried by one big cluster -> cluster p large -> FAIL (both families)
q2 = [(f'Q{i:02d}', 'SPEC', 'big', 'r0', D, D, D, D, 'SPEC', 'SPEC') for i in range(10)]
q2 += [(f'Q{10+i:02d}', 'IMPL', f'b{i}', 'r1', A, A, A, A, 'IMPL', 'IMPL') for i in range(5)]
q2 += [(f'Q{20+i:02d}', 'SPEC', f'c{i}', 'r2', A, A, A, A, 'IMPL', 'IMPL') for i in range(3)]
o, txt = run(q2)
assert 'FAIL' in o['H-E13-1'][2] and 'FAIL' in o['H-E13-2'][2], o
assert 'INSUFFICIENT' in o['H-E13-4'][2]
# 3) too few accidental -> INSUFFICIENT
q3 = [(f'Q{i:02d}', 'SPEC', f'a{i}', 'r0', D, D, D, D, 'SPEC', 'SPEC') for i in range(10)]
q3 += [(f'Q{10+i:02d}', 'IMPL', f'b{i}', 'r1', A, A, A, A, 'IMPL', 'IMPL') for i in range(4)]
o, _ = run(q3)
assert 'INSUFFICIENT' in o['H-E13-1'][2] and 'INSUFFICIENT' in o['H-E13-3'][2], o
# helpers
assert abs(S.mcnemar_exact(6, 0) - 0.03125) < 1e-12 and S.mcnemar_exact(3, 3) == 1.0
p, lo, hi = S.wilson(19, 24); assert abs(p - 0.7917) < 1e-3 and abs(lo - 0.595) < 2e-3 and abs(hi - 0.908) < 2e-3
print('test_score_e13: OK')
