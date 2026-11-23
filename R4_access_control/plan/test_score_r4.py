"""Self-test of score_r4.py on synthetic data with known answers. Run: /usr/bin/python3 -I -B plan/test_score_r4.py"""
import csv, io, math, sys, tempfile, contextlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_r4 as S  # noqa: E402

HDR = ['item_id', 'ac_relevant', 'ac_kind', 'principals_needed', 'observable_via_http', 'contract_operation', 'contract_security',
       'policy_in_contract', 'fix_location', 'confidence', 'locators', 'rationale']


def row(i, ac='YES', kind='OBJECT_LEVEL', pr='TWO_SAME_ROLE', ob='YES', op='PRESENT', sec='DECLARED', pol='NO', loc='HANDLER'):
    if ac != 'YES': kind = pr = ob = op = sec = pol = loc = 'NA'
    return [i, ac, kind, pr, ob, op, sec, pol, loc, '3', 'x:1', 'r, with comma']


def write(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(HDR); w.writerows(rows)


def build(root):
    ids = [f'A{i:03d}' for i in range(1, 31)]
    rows = []
    for n, i in enumerate(ids):
        if n >= 25: rows.append(row(i, ac='NO')); continue
        pr = 'TWO_SAME_ROLE' if n < 15 else ('ONE' if n < 20 else ('NONE' if n < 23 else 'UNCLEAR'))
        op = 'PRESENT' if n < 20 else 'ABSENT'
        pol = 'NO' if n < 18 else 'YES'
        rows.append(row(i, pr=pr, op=op, sec='DECLARED' if op == 'PRESENT' else 'NA', pol=pol))
    g2 = [list(r) for r in rows]; g2[29][1] = 'YES'; g2[29][2:9] = ['OBJECT_LEVEL', 'ONE', 'YES', 'PRESENT', 'DECLARED', 'NO', 'HANDLER']  # A030: G disagree -> UNCLEAR
    write(root / 'packages/r4_blind/codes_G1.csv', rows); write(root / 'packages/r4_blind/codes_G2.csv', g2)
    for b in (0, 1):
        part = rows[b * 15:(b + 1) * 15]
        write(root / f'packages/r4_kb{b + 1}/codes_H1.csv', part); write(root / f'packages/r4_kb{b + 1}/codes_H2.csv', part)
    (root / 'mining/key').mkdir(parents=True)
    with open(root / 'mining/key/r4_key.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['item_id', 'repo', 'ecosystem', 'fix_silent', 'test_in_fix'])
        for n, i in enumerate(ids): w.writerow([i, f'r{n % 6}', 'maven' if n % 2 else 'go', 'true' if n < 22 else 'false', 'false'])


def main():
    ok = 0
    assert abs(S.binom_upper(29, 32) - 1.278e-6) < 1e-8; ok += 1
    p, lo, hi = S.wilson(60, 136); assert abs(p - 0.441) < 1e-3 and abs(lo - 0.3605) < 1e-3; ok += 1
    assert S.kappa(['A', 'B'] * 5, ['A', 'B'] * 5) == 1.0 and S.kappa(['A'] * 4, ['A'] * 4) == 1.0; ok += 1
    a = {'ac_relevant': 'YES', **{f: 'X' for f in S.DEP}, 'contract_operation': 'ABSENT'}
    b = dict(a); b['ac_kind'] = 'Y'
    f = S.final(a, b); assert f['ac_kind'] == 'UNCLEAR' and f['contract_security'] == 'NA' and f['fix_location'] == 'X'; ok += 1
    f = S.final(a, {**a, 'ac_relevant': 'NO'}); assert f['ac_relevant'] == 'UNCLEAR' and all(f[x] == 'NA' for x in S.DEP); ok += 1
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); build(root)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): res = S.score(root, root / 'out.csv')
        assert res['E-R4-1 AC_RELEVANT'][:2] == (25, 30), res['E-R4-1 AC_RELEVANT']; ok += 1
        assert res['H-R4-1'][:2] == (15, 23) and 'FAIL' in res['H-R4-1'][2], res['H-R4-1']; ok += 1       # 15/23, p~0.105
        assert res['H-R4-2'][:2] == (22, 25) and 'PASS' in res['H-R4-2'][2], res['H-R4-2']; ok += 1       # silent 22/25
        assert res['H-R4-3'][:2] == (18, 20) and 'PASS' in res['H-R4-3'][2], res['H-R4-3']; ok += 1       # policy NO 18/20
        assert 'INSUFFICIENT' in res['H-R4-4'][2] and res['H-R4-4'][1] == 25, res['H-R4-4']; ok += 1     # n=25 < 30
        assert 'GPT final ac_relevant YES/NO/UNCLEAR = 25/4/1' in buf.getvalue(); ok += 1
        assert len(list(csv.reader(open(root / 'out.csv')))) == 6; ok += 1
        # invalid value is rejected
        bad = root / 'packages/r4_blind/codes_G1.csv'; t = bad.read_text().replace('OBJECT_LEVEL', 'BOLA', 1); bad.write_text(t)
        try:
            with contextlib.redirect_stdout(io.StringIO()): S.score(root)
            raise AssertionError('invalid value accepted')
        except ValueError: ok += 1
    print(f'test_score_r4: {ok}/13 PASS')


if __name__ == '__main__':
    main()
