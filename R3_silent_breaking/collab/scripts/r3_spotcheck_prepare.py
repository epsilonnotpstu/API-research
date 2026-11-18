"""Prepare the R3 human spot-check (plan: "A human spot-check of 20 items by the author is planned after scoring. It is reported separately.").
Selection rule (fixed here, before any human label exists): among items whose GPT final observable_change is YES,
10 drawn from GPT final client_impact == BREAKING and 10 from the rest (COMPATIBLE or UNCLEAR), seeded; presentation order shuffled (seeded).
Writes (refuses to overwrite):
  human_check/r3_spotcheck.csv        blind sheet for the author: item_id, package folder, empty human columns
  plan/r3_spotcheck_model_codes.csv   GPT and Claude final codes for the same items -- do NOT open before the sheet is finished
Run from R3_silent_breaking/: /usr/bin/python3 -I -B collab/scripts/r3_spotcheck_prepare.py"""
import csv, random, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(B / 'plan'))
from score_r3 import final, load_codes  # noqa: E402

SEED = 'r3-spotcheck-20261118'
SHEET = B / 'human_check/r3_spotcheck.csv'; MODEL = B / 'plan/r3_spotcheck_model_codes.csv'


def main():
    for f in (SHEET, MODEL):
        if f.exists(): sys.exit(f'refuse: {f} exists')
    P = B / 'packages'
    g = final  # field-wise agreement
    G1, G2 = load_codes([P / 'r3_blind/codes_G1.csv']), load_codes([P / 'r3_blind/codes_G2.csv'])
    H1 = load_codes(sorted(P.glob('r3_kb*/codes_H1.csv'))); H2 = load_codes(sorted(P.glob('r3_kb*/codes_H2.csv')))
    ids = sorted(G1)
    gf = {i: g(G1[i], G2[i]) for i in ids}; hf = {i: g(H1[i], H2[i]) for i in ids}
    yes = [i for i in ids if gf[i]['observable_change'] == 'YES']
    brk = [i for i in yes if gf[i]['client_impact'] == 'BREAKING']; rest = [i for i in yes if i not in brk]
    rng = random.Random(SEED)
    pick = rng.sample(brk, 10) + rng.sample(rest, 10); rng.shuffle(pick)
    SHEET.parent.mkdir(exist_ok=True)
    with open(SHEET, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['item_id', 'package_folder', 'human_observable_change', 'human_client_impact', 'human_change_kind', 'notes'])
        for i in pick: w.writerow([i, f'packages/r3_blind/{i}', '', '', '', ''])
    with open(MODEL, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['item_id', 'stratum', 'gpt_observable_change', 'gpt_client_impact', 'gpt_change_kind', 'claude_observable_change', 'claude_client_impact', 'claude_change_kind'])
        for i in pick:
            w.writerow([i, 'GPT_BREAKING' if i in brk else 'GPT_NOT_BREAKING', gf[i]['observable_change'], gf[i]['client_impact'], gf[i]['change_kind'],
                        hf[i]['observable_change'], hf[i]['client_impact'], hf[i]['change_kind']])
    print(f'pool: {len(yes)} GPT-YES ({len(brk)} breaking, {len(rest)} other); wrote {SHEET.relative_to(B)} and {MODEL.relative_to(B)} (20 items)')


if __name__ == '__main__':
    main()
