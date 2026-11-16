"""Self-test for score_e10.py on a synthetic root. Run: /usr/bin/python3 -I -B test_score_e10.py"""
import csv, io, sys, tempfile, contextlib
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here)); sys.path.insert(0, str(here.parent / 'E4_triage'))
import score_e10 as S
from score_e4 import two_direction


def w(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        d = csv.DictWriter(f, fieldnames=cols); d.writeheader(); d.writerows(rows)


def build(root, spec):
    """spec: list of (id, truth, c9, c10, L3, L4, F1, F2)"""
    w(root / 'E7_mining/key/e10_key.csv', [{'item_id': s[0], 'set': 'new', 'truth_direction': s[1]} for s in spec], ['item_id', 'set', 'truth_direction'])
    E = root / 'E2_labelling'
    w(E / 'e10_m1/items.csv', [{'item_id': s[0], 'repo': 'r', 'operation': 'o', 'proposition': 'p'} for s in spec], ['item_id', 'repo', 'operation', 'proposition'])
    for j, n in ((2, 'C9'), (3, 'C10')):
        w(E / f'e10_blind/codes_{n}.csv', [{'item_id': s[0], 'divergence_kind': s[j]} for s in spec], ['item_id', 'divergence_kind'])
    for j, n, d in ((4, 'L3', 'e10_m1'), (5, 'L4', 'e10_m1'), (6, 'F1', 'e10_m1f'), (7, 'F2', 'e10_m1f')):
        w(E / d / f'labels_{n}.csv', [{'item_id': s[0], 'L1': s[j]} for s in spec], ['item_id', 'L1'])


def run(spec):
    with tempfile.TemporaryDirectory() as t:
        root = Path(t); build(root, spec); buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = S.score(root, two_direction, [])
        return {r['analysis']: r for r in out}, buf.getvalue()


D, A, U = 'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'
# 10 items where both M1 abstain on DELIBERATE/SPEC items -> R correct 20/20 pairs -> PASS; forced-choice wrong on them -> FB better
spec = [(f'V{i:02d}', 'SPEC', D, D, 'UNDECIDABLE', 'UNDECIDABLE', 'IMPL', 'IMPL') for i in range(10)]
spec += [(f'V{i:02d}', 'IMPL', A, A, 'IMPL', 'IMPL', 'IMPL', 'IMPL') for i in range(10, 20)]
spec += [('V20', 'BOTH', D, D, 'SPEC', 'SPEC', 'SPEC', 'SPEC')]
o, txt = run(spec)
assert o['H-E10-1']['value'] == '20/20' and 'PASS' in o['H-E10-1']['detail'], o['H-E10-1']
assert o['H-E10-1_sens']['value'] == '10/10'
assert o['H-E10-2']['value'] == 'W20/L0' and 'FB_BETTER' in o['H-E10-2']['detail'], o['H-E10-2']
assert 'BOTH excluded 1' in txt
assert o['H-E10-3']['value'] == '10/10 vs 0/10' and 'PASS' in o['H-E10-3']['detail']

# R wrong on abstentions -> FAIL; forced choice right -> NOT_BETTER
spec2 = [(f'V{i:02d}', 'IMPL', D, D, 'UNDECIDABLE', 'UNDECIDABLE', 'IMPL', 'IMPL') for i in range(10)]
spec2 += [(f'V{i:02d}', 'SPEC', D, D, 'SPEC', 'SPEC', 'SPEC', 'SPEC') for i in range(10, 20)]
o, _ = run(spec2)
assert o['H-E10-1']['value'] == '0/20' and 'FAIL' in o['H-E10-1']['detail']
assert 'NOT_BETTER' in o['H-E10-2']['detail']
assert 'INSUFFICIENT' in o['H-E10-3']['detail']  # accidental arm 0

# few abstentions -> INSUFFICIENT; UNCLEAR kind (coder disagreement) -> R abstains, not a pair
spec3 = [(f'V{i:02d}', 'SPEC', D, D, 'SPEC', 'SPEC', 'SPEC', 'SPEC') for i in range(15)]
spec3 += [('V15', 'SPEC', D, D, 'UNDECIDABLE', 'SPEC', 'SPEC', 'SPEC'), ('V16', 'IMPL', D, A, 'UNDECIDABLE', 'UNDECIDABLE', 'IMPL', 'IMPL')]
o, txt = run(spec3)
assert o['H-E10-1']['value'] == '1/1' and 'INSUFFICIENT' in o['H-E10-1']['detail'], o['H-E10-1']
assert 'both abstain 1' in txt
assert 'INSUFFICIENT' in o['H-E10-2']['detail']

# per-labeller condition: pooled p<.05 but one labeller below 0.5 -> FAIL
spec4 = [(f'V{i:02d}', 'SPEC', D, D, 'UNDECIDABLE', 'SPEC', 'SPEC', 'SPEC') for i in range(14)]
spec4 += [(f'V{i:02d}', 'IMPL', D, D, 'SPEC', 'UNDECIDABLE', 'SPEC', 'SPEC') for i in range(14, 17)]
o, _ = run(spec4)
assert o['H-E10-1']['value'] == '14/17', o['H-E10-1']
assert 'FAIL' in o['H-E10-1']['detail'], o['H-E10-1']
assert abs(S.binom_ge(14, 17) - 0.006362) < 1e-4
assert abs(S.fisher_one_sided(23, 28, 0, 13) - 4.86e-07) < 1e-8
print('test_score_e10: OK')
