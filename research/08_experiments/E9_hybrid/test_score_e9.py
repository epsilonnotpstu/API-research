"""Synthetic self-test for score_e9.py part B."""
import csv, subprocess, sys, tempfile
from pathlib import Path
here = Path(__file__).resolve().parent
def w(p, cols, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        x = csv.writer(f); x.writerow(cols); x.writerows(rows)
with tempfile.TemporaryDirectory() as t:
    r = Path(t); ids = [f'W{n:02d}' for n in range(10)] + [f'X{n:02d}' for n in range(10)]
    truth = {i: ('SPEC' if int(i[1:]) < 5 else 'IMPL') for i in ids}
    kind = {i: ('ACCIDENTAL' if int(i[1:]) >= 5 else 'DELIBERATE') for i in ids}
    kind['X09'] = 'UNCLEAR'  # coder disagreement below
    # M1: wrong (SPEC) on W05,W06,X05,X06 (accidental IMPL) -> 4 wins per labeller; L2 also wrong on X00 (DELIBERATE SPEC -> IMPL), no change
    m1 = {i: truth[i] for i in ids}
    for i in ('W05', 'W06', 'X05', 'X06'): m1[i] = 'SPEC'
    w(r/'E7_mining/key/e7_key.csv', ['item_id', 'set', 'truth_direction'], [[i, 'new', truth[i]] for i in ids if i[0] == 'X'])
    w(r/'E7_mining/key/e8b_key.csv', ['item_id', 'set', 'truth_direction'], [[i, 'new', truth[i]] for i in ids if i[0] == 'W'])
    for d, pre, a, b in (('e7_blind', 'X', 'C1', 'C2'), ('e8b_blind', 'W', 'C7', 'C8')):
        rows = [i for i in ids if i[0] == pre]
        w(r/'E2_labelling'/d/f'codes_{a}.csv', ['item_id', 'divergence_kind'], [[i, 'ACCIDENTAL' if int(i[1:]) >= 5 else 'DELIBERATE'] for i in rows])
        w(r/'E2_labelling'/d/f'codes_{b}.csv', ['item_id', 'divergence_kind'], [[i, ('DELIBERATE' if i == 'X09' else ('ACCIDENTAL' if int(i[1:]) >= 5 else 'DELIBERATE'))] for i in rows])
    w(r/'E2_labelling/e9_m1/items.csv', ['item_id', 'repo', 'operation', 'proposition'], [[i, 'r', 'op', 'p'] for i in ids])
    for n in ('L1', 'L2'):
        lab = dict(m1)
        if n == 'L2': lab['X00'] = 'IMPL'
        w(r/'E2_labelling/e9_m1'/f'labels_{n}.csv', ['item_id', 'L1', 'confidence', 'evidence_locators', 'rationale'], [[i, lab[i], 3, '', ''] for i in ids])
    o = subprocess.run([sys.executable, '-I', '-B', str(here/'score_e9.py'), '--root', str(r), '--part', 'B'], capture_output=True, text=True)
    print(o.stdout, o.stderr); assert o.returncode == 0
    h = [l for l in o.stdout.splitlines() if 'H-E9-1 [B_confirmatory]' in l][0]
    assert 'wins 8 losses 0' in h and 'PASS' in h, h
    assert 'kinds D/A/U = 10/9/1' in o.stdout
    assert 'HYB override precision 9/9' in o.stdout
(here/'e9_scores_B.csv').unlink(missing_ok=True)
print('test_score_e9: OK')
