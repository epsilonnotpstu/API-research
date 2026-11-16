"""Synthetic self-test for score_e8b.py."""
import csv, subprocess, sys, tempfile
from pathlib import Path
here = Path(__file__).resolve().parent
def w(p, cols, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        x = csv.writer(f); x.writerow(cols); x.writerows(rows)
with tempfile.TemporaryDirectory() as t:
    r = Path(t)
    for keyf, md, cd, ca, cb, j, pre in (('e7_key.csv', 'e8_match', 'e8_code', 'C3', 'C4', 'J1', 'X'), ('e8b_key.csv', 'e8b_match', 'e8b_code', 'C5', 'C6', 'J2', 'W')):
        key, mt, k1, k2, p4 = [], [], [], [], []
        for n in range(20):
            i = f'{pre}{n:02d}'; spec = n < 10; acc = n >= 15 or n == 9
            key.append([i, 'new', 'SPEC' if spec else 'IMPL'])
            m = 'DIFFERENT' if n in (18, 19) else 'SAME'; mt.append([i, m, '-'])
            k = 'ACCIDENTAL' if acc else 'DELIBERATE'; k1.append([i, k]); k2.append([i, k]); p4.append([i, k])
        w(r/'E7_mining/key'/keyf, ['item_id', 'set', 'truth_direction'], key)
        w(r/'E2_labelling'/md/f'match_{j}.csv', ['item_id', 'match', 'rationale'], mt)
        w(r/'E2_labelling'/cd/f'codes_{ca}.csv', ['item_id', 'divergence_kind'], k1)
        w(r/'E2_labelling'/cd/f'codes_{cb}.csv', ['item_id', 'divergence_kind'], k2)
        if pre == 'W': w(r/'E2_labelling/e8b_proponly/codes_P4.csv', ['item_id', 'divergence_kind'], p4)
    o = subprocess.run([sys.executable, '-I', '-B', str(here/'score_e8b.py'), '--root', str(r)], capture_output=True, text=True)
    print(o.stdout, o.stderr); assert o.returncode == 0
    line = [l for l in o.stdout.splitlines() if 'PRIMARY' in l][0]
    # per set SAME: DELIBERATE SPEC 9/14 (0-8 spec, 10-14 impl), ACCIDENTAL SPEC 1/4 (9; 15,16,17) -> pooled 18/28, 2/8
    assert 'SPEC 18/28' in line and 'SPEC 2/8' in line and 'FAIL' in line, line
    assert 'missed 2/6' in o.stdout, o.stdout
print('test_score_e8b: OK')
