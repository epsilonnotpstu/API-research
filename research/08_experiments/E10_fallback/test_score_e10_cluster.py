"""Self-test for score_e10_cluster.py. Run: /usr/bin/python3 -I -B test_score_e10_cluster.py"""
import csv, io, sys, tempfile, contextlib
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import score_e10_cluster as S


def w(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        d = csv.DictWriter(f, fieldnames=cols); d.writeheader(); d.writerows(rows)


def run(spec):
    """spec: (id, cluster, truth, c9, c10, L3, L4, F1, F2)"""
    with tempfile.TemporaryDirectory() as t:
        r = Path(t); E = r / 'E2_labelling'
        w(r / 'E7_mining/key/e10_key.csv', [{'item_id': s[0], 'truth_direction': s[2]} for s in spec], ['item_id', 'truth_direction'])
        w(r / 'E7_mining/key/accepted_full_t48.csv', [{'item_id': s[0], 'candidate_id': s[1]} for s in spec], ['item_id', 'candidate_id'])
        w(E / 'e10_m1/items.csv', [{'item_id': s[0]} for s in spec], ['item_id'])
        for j, n in ((3, 'C9'), (4, 'C10')):
            w(E / f'e10_blind/codes_{n}.csv', [{'item_id': s[0], 'divergence_kind': s[j]} for s in spec], ['item_id', 'divergence_kind'])
        for j, n, d in ((5, 'L3', 'e10_m1'), (6, 'L4', 'e10_m1'), (7, 'F1', 'e10_m1f'), (8, 'F2', 'e10_m1f')):
            w(E / d / f'labels_{n}.csv', [{'item_id': s[0], 'L1': s[j]} for s in spec], ['item_id', 'L1'])
        with contextlib.redirect_stdout(io.StringIO()):
            return S.score(r)


D, A, U = 'DELIBERATE', 'ACCIDENTAL', 'UNDECIDABLE'
# one big cluster of 10 abstentions where R is right counts once; 3 small clusters where R is wrong
spec = [(f'V{i:02d}', 'c0', 'SPEC', D, D, U, U, 'IMPL', 'IMPL') for i in range(10)]
spec += [(f'V{10+i:02d}', f'c{1+i}', 'IMPL', D, D, U, U, 'IMPL', 'IMPL') for i in range(3)]
spec += [('V20', 'c9', 'BOTH', D, D, U, U, 'SPEC', 'SPEC')]
o = run(spec)
assert o['H-E10-1_cluster'][:3] == (1, 3, 0), o
assert o['H-E10-2_cluster'][:3] == (1, 3, 0), o
assert abs(o['H-E10-1_cluster'][3] - 0.9375) < 1e-9
print('test_score_e10_cluster: OK')
