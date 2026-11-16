"""Self-test for score_e11.py. Run: /usr/bin/python3 -I -B test_score_e11.py"""
import csv, io, sys, tempfile, contextlib
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import score_e11 as S

D, A, U = 'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'


def w(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        d = csv.DictWriter(f, fieldnames=cols); d.writeheader(); d.writerows(rows)


def run(spec):
    """spec: list of (id, truth, cluster, gptA, gptB, K1, K2); set from id prefix"""
    with tempfile.TemporaryDirectory() as t:
        r = Path(t); K = r / 'E7_mining/key'; E = r / 'E2_labelling'
        for s, kf, af, pkg, (ca, cb) in S.SETS:
            g = [x for x in spec if x[0][0] == s]
            w(K / kf, [{'item_id': x[0], 'set': 'new', 'truth_direction': x[1]} for x in g] + ([{'item_id': f'{s}99', 'set': 'e6_exploratory', 'truth_direction': 'SPEC'}] if s == 'X' else []), ['item_id', 'set', 'truth_direction'])
            w(K / af, [{'item_id': x[0], 'candidate_id': x[2]} for x in g], ['item_id', 'candidate_id'])
            for j, c in ((3, ca), (4, cb)):
                w(E / pkg / f'codes_{c}.csv', [{'item_id': x[0], 'divergence_kind': x[j]} for x in g], ['item_id', 'divergence_kind'])
        half = len(spec) // 2
        for b, part in (('e11_b1', spec[:half]), ('e11_b2', spec[half:])):
            for j, c in ((5, 'K1'), (6, 'K2')):
                w(E / b / f'codes_{c}.csv', [{'item_id': x[0], 'divergence_kind': x[j]} for x in part], ['item_id', 'divergence_kind'])
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            o = S.score(r)
        return o, buf.getvalue()


# strong association, clusters of 1 -> PASS; full cross-family agreement -> PASS
spec = [(f'X{i:02d}', 'SPEC', f'c{i}', D, D, D, D) for i in range(8)]
spec += [(f'W{i:02d}', 'IMPL', f'c{i}', A, A, A, A) for i in range(8)]
spec += [(f'V{i:02d}', 'IMPL', f'c{i}', D, D, U, D) for i in range(4)]   # K1/K2 disagree -> UNCLEAR
spec += [('V10', 'BOTH', 'cz', D, D, D, D)]
o, txt = run(spec)
assert 'PASS' in o['H-E11-1'][1] and o['H-E11-1'][0].startswith('8/8 vs 0/8'), o
assert o['H-E11-2'] == ('16/16', 'kappa=1.000 PASS'), o
assert 'n=20' in txt and 'set V: n=4' in txt
# one big cluster carries the effect -> item p small but cluster level not -> FAIL
spec2 = [(f'X{i:02d}', 'SPEC', 'big', D, D, D, D) for i in range(10)]
spec2 += [(f'W{i:02d}', 'IMPL', f'c{i}', A, A, A, A) for i in range(5)]
spec2 += [(f'V{i:02d}', 'SPEC', f'v{i}', A, A, A, A) for i in range(3)]
o, _ = run(spec2)
assert 'FAIL' in o['H-E11-1'][1], o
# too few accidental -> INSUFFICIENT; disagreement across families -> kappa low
spec3 = [(f'X{i:02d}', 'SPEC', f'c{i}', D, D, D, D) for i in range(10)] + [(f'W{i:02d}', 'IMPL', f'w{i}', A, A, D, D) for i in range(8)]
o, _ = run(spec3)
assert 'INSUFFICIENT' in o['H-E11-1'][1] and 'FAIL' in o['H-E11-2'][1], o
print('test_score_e11: OK')
