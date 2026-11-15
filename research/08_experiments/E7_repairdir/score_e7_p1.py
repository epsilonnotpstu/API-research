"""Post-hoc control (amendment A3): proposition-only coder P1 vs truth and vs final C1/C2 code. set=new, SPEC/IMPL only."""
import csv, sys
from pathlib import Path
here = Path(__file__).resolve().parent; root = here.parent
sys.path.insert(0, str(here))
from score_e7 import fisher_one_sided, woolf_or, kappa
rd = lambda p: {r['item_id']: r for r in csv.DictReader(open(p, newline=''))}
key = rd(root/'E7_mining/key/e7_key.csv'); c1 = rd(root/'E2_labelling/e7_blind/codes_C1.csv'); c2 = rd(root/'E2_labelling/e7_blind/codes_C2.csv')
p1 = rd(root/'E2_labelling/e7_proponly/codes_P1.csv'); adj = {(r['item_id'], r['field']): r['value'] for r in csv.DictReader(open(here/'adjudication.csv'))}
assert set(p1) == set(key)
def final(i, f): return c1[i][f] if c1[i][f] == c2[i][f] else adj[(i, f)]
new = [i for i in sorted(key) if key[i]['set'] == 'new' and key[i]['truth_direction'] in ('SPEC', 'IMPL')]
for f, pos, neg in (('divergence_kind', 'DELIBERATE', 'ACCIDENTAL'), ('contract_specificity', 'GENERIC', 'SPECIFIC')):
    vals = {i: p1[i][f].strip().upper() for i in new}
    unclear = [i for i in new if vals[i] not in (pos, neg)]
    d = [i for i in new if i not in unclear]
    a = sum(vals[i] == pos and key[i]['truth_direction'] == 'SPEC' for i in d); b = sum(vals[i] == pos and key[i]['truth_direction'] == 'IMPL' for i in d)
    c = sum(vals[i] == neg and key[i]['truth_direction'] == 'SPEC' for i in d); e = sum(vals[i] == neg and key[i]['truth_direction'] == 'IMPL' for i in d)
    orv, lo, hi = woolf_or(a, b, c, e)
    k = kappa([final(i, f) for i in new], [vals[i] for i in new], (pos, neg, "UNCLEAR"))
    agree = sum(final(i, f) == vals[i] for i in new)
    print(f'[P1 {f}] {pos}: SPEC {a}/{a+b} | {neg}: SPEC {c}/{c+e} ({c/(c+e) if c+e else float("nan"):.2f}) | OR {orv:.2f} [{lo:.2f},{hi:.2f}] | Fisher p={fisher_one_sided(a,b,c,e):.4f} | UNCLEAR {len(unclear)} | kappa vs final {k:.3f} (agree {agree}/{len(new)})')
