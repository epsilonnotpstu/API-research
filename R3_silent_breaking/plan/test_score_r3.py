"""Self-test for score_r3.py. Run: /usr/bin/python3 -I -B plan/test_score_r3.py"""
import csv, io, sys, tempfile, contextlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_r3 as S

COLS = ['item_id', 'observable_change', 'change_kind', 'client_impact', 'contract_specified', 'confidence']


def w(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', newline='') as f:
        d = csv.DictWriter(f, fieldnames=cols); d.writeheader(); d.writerows(rows)


def code(i, oc, kind='', imp='', spec=''):
    return {'item_id': i, 'observable_change': oc, 'change_kind': kind, 'client_impact': imp, 'contract_specified': spec, 'confidence': '2'}


def build(r, spec, nkb=2):
    """spec rows: (id, repo, ann, upd, g1, g2, h1, h2) with gX/hX = (oc, kind, impact, specified)"""
    w(r / 'mining/key/r3_key.csv', [{'item_id': s[0], 'repo': s[1], 'commit': 'c' + s[0], 'language': 'java',
                                    'annotation_touched': 'true' if s[2] else 'false', 'spec_updated_90d': 'true' if s[3] else 'false'} for s in spec],
      ['item_id', 'repo', 'commit', 'language', 'annotation_touched', 'spec_updated_90d'])
    for j, c in ((4, 'G1'), (5, 'G2')):
        w(r / f'packages/r3_blind/codes_{c}.csv', [code(s[0], *s[j]) for s in spec], COLS)
    size = -(-len(spec) // nkb)
    for b in range(nkb):
        part = spec[b * size:(b + 1) * size]
        for j, c in ((6, 'H1'), (7, 'H2')):
            w(r / f'packages/r3_kb{b + 1}/codes_{c}.csv', [code(s[0], *s[j]) for s in part], COLS)


def run(spec):
    with tempfile.TemporaryDirectory() as t:
        build(Path(t), spec)
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            o = S.score(t, str(Path(t) / 'o.csv'))
        return o, buf.getvalue()


BRK = ('YES', 'INPUT_STRICTER', 'BREAKING', 'SPECIFIED')
CMP = ('YES', 'RESPONSE_CONTENT', 'COMPATIBLE', 'UNSPECIFIED')
NO = ('NO', '', '', '')
# 1) 14 breaking (12 without annotation edit; 10 of them specified and not updated), 10 compatible, 20 no-change, 4 repos
spec = [(f'B{i:03d}', f'r{i % 4}', i >= 12, i >= 10, BRK, BRK, BRK, BRK) for i in range(14)]
spec += [(f'B{100 + i:03d}', f'r{i % 4}', False, False, CMP, CMP, CMP, CMP) for i in range(10)]
spec += [(f'B{200 + i:03d}', f'r{i % 4}', False, False, NO, NO, NO, NO) for i in range(20)]
o, txt = run(spec)
assert o['E-R3-1 YES'][:2] == (24, 44) and o['E-R3-1 BREAKING'][:2] == (14, 44), o
assert o['H-R3-1'][:2] == (12, 14) and 'PASS' in o['H-R3-1'][2], o          # P(X>=12 | 14) = 0.0065
assert o['H-R3-2'][:2] == (10, 14) and 'FAIL' in o['H-R3-2'][2], o          # 10/14: p = 0.090
assert 'PASS' in o['H-R3-3'][2], o
assert 'repos 4' in txt
# 2) coder disagreement on impact -> UNCLEAR, removes item from BREAKING; Claude disagreement does not touch GPT finals
spec2 = [(s[0], s[1], s[2], s[3], s[4], ('YES', 'INPUT_STRICTER', 'COMPATIBLE', 'SPECIFIED') if i < 5 else s[5], NO, s[7]) for i, s in enumerate(spec)]
o2, _ = run(spec2)
assert o2['E-R3-1 BREAKING'][:2] == (9, 44) and 'INSUFFICIENT' in o2['H-R3-1'][2], o2
assert o2['E-R3-1 YES'][:2] == (24, 44)
# 3) too few cross-family decided -> INSUFFICIENT
o3, _ = run(spec[:20])
assert 'INSUFFICIENT' in o3['H-R3-3'][2], o3
# 4) invalid code value is rejected
bad = [(s[0], s[1], s[2], s[3], ('MAYBE', '', '', ''), s[5], s[6], s[7]) if i == 0 else s for i, s in enumerate(spec)]
try:
    run(bad); raise SystemExit('invalid value not rejected')
except ValueError:
    pass
# helpers
assert abs(S.binom_upper(12, 14) - 0.00647) < 1e-4 and abs(S.binom_upper(10, 14) - 0.0898) < 1e-3
assert S.kappa(['YES', 'NO'] * 5, ['YES', 'NO'] * 5) == 1.0
print('test_score_r3: OK')
