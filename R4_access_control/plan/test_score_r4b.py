"""Self-test of score_r4b.py on synthetic data. Run: /usr/bin/python3 -I -B plan/test_score_r4b.py"""
import contextlib, csv, io, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_r4b as S  # noqa: E402

HDR = ['item_id', 'operation', 'contract_operation', 'op_locator', 'contract_security', 'sec_locator', 'policy_in_contract', 'policy_quote', 'confidence', 'rationale']


def w(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        x = csv.writer(f); x.writerow(HDR); x.writerows(rows)


def main():
    ok = 0
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); ids = [f'C{i:03d}' for i in range(1, 26)]
        rows = []
        for n, i in enumerate(ids):
            op = 'PRESENT' if n < 22 else 'ABSENT'
            sec = ('NOT_DECLARED' if n < 6 else 'DECLARED') if op == 'PRESENT' else 'NA'
            pol = 'NO' if n < 20 else 'YES'
            rows.append([i, 'PUT /api/users/{id}', op, f'contract/a.yaml:{2}' if op == 'PRESENT' else '', sec, '', pol, '', '3', 'r, x'])
            c = root / 'packages/r4b_blind' / i / 'contract'; c.mkdir(parents=True)
            (c / 'a.yaml').write_text('paths:\n  /api/users/{id}:\n    put: {}\n' if n != 0 else 'paths:\n  /other:\n    get: {}\n')
        w(root / 'packages/r4b_blind/codes_G3.csv', rows); w(root / 'packages/r4b_blind/codes_G4.csv', rows)
        w(root / 'packages/r4b_kb1/codes_H3.csv', rows); w(root / 'packages/r4b_kb1/codes_H4.csv', rows)
        (root / 'mining/key').mkdir(parents=True)
        with open(root / 'mining/key/r4b_key.csv', 'w', newline='') as f:
            x = csv.writer(f); x.writerow(['r4b_id', 'r4_id', 'repo'])
            for n, i in enumerate(ids): x.writerow([i, f'A{n:03d}', f'r{n % 5}'])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): res = S.score(root, root / 'o.csv')
        out = buf.getvalue()
        assert res['E-R4-2a PRESENT'][:2] == (22, 25); ok += 1
        assert res['H-R4-3b'][:2] == (20, 22) and 'PASS' in res['H-R4-3b'][2]; ok += 1
        k, m, txt = res['H-R4-5']; assert (k, m) == (6, 22); ok += 1
        assert ('PASS' in txt) == (S.binom_upper(6, 22, 0.1) < 0.05); ok += 1
        assert 'locator validity G3: 21/22' in out, out; ok += 1          # item C001's locator line lacks the path
        assert 'R4 cross-tab skipped' in out; ok += 1
        try:
            bad = root / 'packages/r4b_blind/codes_G3.csv'; bad.write_text(bad.read_text().replace('PRESENT', 'YES', 1))
            with contextlib.redirect_stdout(io.StringIO()): S.score(root)
            raise AssertionError('invalid accepted')
        except ValueError: ok += 1
    print(f'test_score_r4b: {ok}/7 PASS')


if __name__ == '__main__':
    main()
