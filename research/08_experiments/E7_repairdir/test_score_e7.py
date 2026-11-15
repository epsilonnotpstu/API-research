#!/usr/bin/env python3
"""Self-test for score_e7.py on synthetic data (no real key or codes are read). Run: python3 -I -B test_score_e7.py"""
import csv
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_e7 as s  # noqa: E402


def w(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        dw = csv.DictWriter(f, fieldnames=list(rows[0]))
        dw.writeheader()
        dw.writerows(rows)


def test_stats():
    # Fisher one-sided: table [[8,2],[2,8]] -> P(X>=8) = 0.01151 (hypergeometric N=20, K=10, n=10)
    assert abs(s.fisher_one_sided(8, 2, 2, 8) - 0.011497) < 1e-4, s.fisher_one_sided(8, 2, 2, 8)
    assert abs(s.fisher_one_sided(5, 5, 5, 5) - 0.6719) < 1e-3
    assert s.fisher_one_sided(0, 10, 10, 0) > 0.999
    lo, hi = s.wilson(5, 10)
    assert abs(lo - 0.2366) < 1e-3 and abs(hi - 0.7634) < 1e-3
    o, lo, hi = s.woolf_or(8, 2, 2, 8)
    assert abs(o - (8.5 * 8.5) / (2.5 * 2.5)) < 1e-9 and lo < o < hi
    assert s.kappa(['A', 'B'], ['A', 'B'], ('A', 'B')) == 1.0
    assert abs(s.kappa(list('AABB'), list('ABAB'), ('A', 'B')) - 0.0) < 1e-9


def run_synthetic(disagree_adjudicated=True):
    root = Path(tempfile.mkdtemp())
    (root / 'E7_repairdir').mkdir()
    shutil.copytree(HERE.parent / 'E4_triage', root / 'E4_triage', ignore=shutil.ignore_patterns('*', '!score_e4.py'))
    shutil.copy(HERE.parent / 'E4_triage' / 'score_e4.py', root / 'E4_triage' / 'score_e4.py')
    rng = random.Random(7)
    key, c1, c2, adj = [], [], [], []
    for n in range(40):
        iid = f'X{n + 1:02d}'
        kind = 'DELIBERATE' if n < 20 else 'ACCIDENTAL'
        truth = ('SPEC' if n < 15 else 'IMPL') if n < 20 else ('SPEC' if n < 23 else 'IMPL')
        st = 'e6_exploratory' if n >= 36 else 'new'
        key.append({'item_id': iid, 'set': st, 'stars': str(rng.choice([50, 900])), 'truth_direction': truth,
                    'confidence': '3' if n % 2 else '2', 'cross_item_flag': 'true' if n == 5 else ''})
        k2 = kind if n != 1 else 'UNCLEAR'
        c1.append({'item_id': iid, 'divergence_kind': kind, 'contract_specificity': 'GENERIC' if n % 3 else 'SPECIFIC'})
        c2.append({'item_id': iid, 'divergence_kind': k2, 'contract_specificity': 'GENERIC' if n % 3 else 'SPECIFIC'})
        if n == 1 and disagree_adjudicated:
            adj.append({'item_id': iid, 'field': 'divergence_kind', 'value': 'DELIBERATE'})
    w(root / 'E7_mining' / 'key' / 'e7_key.csv', key)
    w(root / 'E2_labelling' / 'e7_blind' / 'codes_C1.csv', c1)
    w(root / 'E2_labelling' / 'e7_blind' / 'codes_C2.csv', c2)
    if adj:
        w(root / 'E7_repairdir' / 'adjudication.csv', adj)
    r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'score_e7.py'), '--root', str(root)], capture_output=True, text=True)
    return r, root


def test_end_to_end():
    r, root = run_synthetic(True)
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert 'new 36' in out and 'exploratory 4' in out, out
    # primary: DELIBERATE 15 SPEC / 5 IMPL, ACCIDENTAL 3 SPEC / 13 IMPL (items 20..35) -> strong effect, PASS
    assert 'DELIBERATE: SPEC 15/20' in out and 'ACCIDENTAL: SPEC 3/16' in out and '| PASS' in out, out
    rows = list(csv.DictReader(open(root / 'E7_repairdir' / 'e7_scores.csv')))
    prim = [x for x in rows if x['analysis'] == 'primary'][0]
    assert abs(float(prim['fisher_p']) - s.fisher_one_sided(15, 5, 3, 13)) < 1e-6
    assert 'rule macro-F1' in out


def test_missing_adjudication_fails():
    r, _ = run_synthetic(False)
    assert r.returncode != 0 and 'adjudication missing' in (r.stderr + r.stdout)


if __name__ == '__main__':
    test_stats()
    test_end_to_end()
    test_missing_adjudication_fails()
    print('test_score_e7: 3/3 OK')
