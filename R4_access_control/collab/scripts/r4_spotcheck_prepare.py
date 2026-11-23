"""Prepare the R4 human spot-check (plan §8: 20 items, stratified by ac_kind, after scoring; reported separately).
Selection (fixed here, before any human label): among items whose GPT final ac_relevant is YES, allocate 20 slots to the GPT final
ac_kind strata proportionally (largest remainder, at least 1 per non-empty stratum while slots remain), draw within strata with
random.Random('r4-spotcheck:'+stratum); then add up to 0 extra; presentation order shuffled with random.Random('r4-spotcheck-order').
Writes (refuses to overwrite): human_check/r4_spotcheck.csv (blind sheet), plan/r4_spotcheck_model_codes.csv (do NOT open before finishing).
Run from R4_access_control/: /usr/bin/python3 -I -B collab/scripts/r4_spotcheck_prepare.py"""
import collections, csv, random, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(B / 'plan'))
from score_r4 import final, load_codes, DEP  # noqa: E402

SHEET = B / 'human_check/r4_spotcheck.csv'; MODEL = B / 'plan/r4_spotcheck_model_codes.csv'; N = 20


def main():
    for f in (SHEET, MODEL):
        if f.exists(): sys.exit(f'refuse: {f} exists')
    P = B / 'packages'
    G1, G2 = load_codes([P / 'r4_blind/codes_G1.csv']), load_codes([P / 'r4_blind/codes_G2.csv'])
    kb = sorted(P.glob('r4_kb*')); H1 = load_codes([d / 'codes_H1.csv' for d in kb]); H2 = load_codes([d / 'codes_H2.csv' for d in kb])
    ids = sorted(G1); g = {i: final(G1[i], G2[i]) for i in ids}; h = {i: final(H1[i], H2[i]) for i in ids}
    strata = collections.defaultdict(list)
    for i in ids:
        if g[i]['ac_relevant'] == 'YES': strata[g[i]['ac_kind']].append(i)
    tot = sum(len(v) for v in strata.values()); n = min(N, tot)
    quota = {k: n * len(v) / tot for k, v in strata.items()}; alloc = {k: int(q) for k, q in quota.items()}
    for k in sorted(strata, key=lambda k: (-(quota[k] - alloc[k]), k)):
        if sum(alloc.values()) >= n: break
        alloc[k] += 1
    for k in sorted(strata):                         # ensure each non-empty stratum gets one if possible (take from largest)
        if alloc[k] == 0:
            big = max(alloc, key=lambda x: (alloc[x], x))
            if alloc[big] > 1: alloc[big] -= 1; alloc[k] = 1
    pick = []
    for k in sorted(strata): pick += random.Random('r4-spotcheck:' + k).sample(sorted(strata[k]), alloc[k])
    random.Random('r4-spotcheck-order').shuffle(pick)
    SHEET.parent.mkdir(exist_ok=True)
    cols = ['ac_relevant'] + list(DEP)
    with open(SHEET, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'package_folder'] + ['human_' + c for c in cols] + ['notes'])
        for i in pick: w.writerow([i, f'packages/r4_blind/{i}'] + [''] * len(cols) + [''])
    with open(MODEL, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'stratum'] + ['gpt_' + c for c in cols] + ['claude_' + c for c in cols])
        for i in pick: w.writerow([i, g[i]['ac_kind']] + [g[i][c] for c in cols] + [h[i][c] for c in cols])
    print(f'strata {dict((k, len(v)) for k, v in sorted(strata.items()))}; alloc {alloc}; wrote {len(pick)} items')


if __name__ == '__main__':
    main()
