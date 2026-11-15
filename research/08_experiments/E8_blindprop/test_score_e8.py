"""Synthetic self-test for score_e8.py."""
import csv, subprocess, sys, tempfile
from pathlib import Path
here = Path(__file__).resolve().parent

def w(p, cols, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        x = csv.writer(f); x.writerow(cols); x.writerows(rows)

with tempfile.TemporaryDirectory() as t:
    r = Path(t); key, match, c3, c4 = [], [], [], []
    for n in range(40):
        i = f'X{n:02d}'; spec = n < 20; delib = n < 18 or 30 <= n < 33
        key.append([i, 'new', 'SPEC' if spec else 'IMPL'])
        m = 'NONE' if n == 39 else ('DIFFERENT' if n == 38 else 'SAME')
        match.append([i, m, '-'])
        if m != 'NONE':
            k = 'DELIBERATE' if delib else 'ACCIDENTAL'
            c3.append([i, k]); c4.append([i, k if n != 37 else 'UNCLEAR'])
    w(r/'E7_mining/key/e7_key.csv', ['item_id', 'set', 'truth_direction'], key)
    w(r/'E2_labelling/e8_match/match_J1.csv', ['item_id', 'match', 'rationale'], match)
    w(r/'E2_labelling/e8_code/codes_C3.csv', ['item_id', 'divergence_kind'], c3)
    w(r/'E2_labelling/e8_code/codes_C4.csv', ['item_id', 'divergence_kind'], c4)
    out = subprocess.run([sys.executable, '-I', '-B', str(here/'score_e8.py'), '--root', str(r)], capture_output=True, text=True)
    print(out.stdout, out.stderr)
    assert out.returncode == 0
    line = [l for l in out.stdout.splitlines() if '[primary' in l][0]
    # primary: SAME new items 0..37; DELIBERATE SPEC 18/21 (0-17 spec, 30-32 impl), ACCIDENTAL SPEC 2/16 (18,19), X37 UNCLEAR
    assert 'SPEC 18/21' in line and 'SPEC 2/16' in line and 'UNCLEAR 1' in line and 'PASS' in line, line
print('test_score_e8: OK')
