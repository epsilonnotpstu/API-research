"""Self-test of score_r3b.py. Run: /usr/bin/python3 -I -B plan/test_score_r3b.py"""
import contextlib, csv, io, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_r3b as S  # noqa: E402

HDR = ['item_id', 'changed_behaviour', 'affected_operation', 'contract_operation', 'op_locator', 'contract_specified', 'spec_quote', 'confidence', 'rationale']


def w(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        x = csv.writer(f); x.writerow(HDR); x.writerows(rows)


def main():
    ok = 0
    assert abs(S.binom_upper(29, 32) - 1.278e-6) < 1e-8; ok += 1
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); ids = [f'D{i:03d}' for i in range(1, 31)]; rows = []
        for n, i in enumerate(ids):
            sp = 'SPECIFIED' if n < 4 else ('UNCLEAR' if n >= 28 else 'UNSPECIFIED')
            rows.append([i, 'x', 'GET /a', 'PRESENT' if n < 20 else 'ABSENT', 'contract/a.yaml:1', sp, 'maxLength: 64' if sp == 'SPECIFIED' else '', '3', 'r, y'])
            c = root / 'packages/r3b_blind' / i / 'contract'; c.mkdir(parents=True)
            (c / 'a.yaml').write_text('name:\n  maxLength:   64\n' if n != 0 else 'name: {}\n')
        w(root / 'packages/r3b_blind/codes_G5.csv', rows); w(root / 'packages/r3b_blind/codes_G6.csv', rows)
        w(root / 'packages/r3b_kb1/codes_H5.csv', rows); w(root / 'packages/r3b_kb1/codes_H6.csv', rows)
        (root / 'mining/key').mkdir(parents=True)
        with open(root / 'mining/key/r3b_key.csv', 'w', newline='') as f:
            x = csv.writer(f); x.writerow(['r3b_id', 'r3_id', 'repo'])
            for n, i in enumerate(ids): x.writerow([i, f'B{n:03d}', f'r{n % 4}'])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): res = S.score(root, root / 'o.csv')
        o = buf.getvalue()
        assert res['E-R3-2a SPECIFIED'][:2] == (4, 30); ok += 1
        assert res['H-R3-4'][:2] == (24, 28) and 'PASS' in res['H-R3-4'][2]; ok += 1
        assert res['E-R3-2b PRESENT'][:2] == (20, 30); ok += 1
        assert 'quote validity G5: 3/4' in o, o; ok += 1     # D001's contract lacks the quote; whitespace normalised for the rest
        try:
            b = root / 'packages/r3b_blind/codes_G6.csv'; b.write_text(b.read_text().replace('UNSPECIFIED', 'NO', 1))
            with contextlib.redirect_stdout(io.StringIO()): S.score(root)
            raise AssertionError('invalid accepted')
        except ValueError: ok += 1
    print(f'test_score_r3b: {ok}/6 PASS')


if __name__ == '__main__':
    main()
