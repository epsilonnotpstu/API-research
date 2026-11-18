"""Exploratory (NOT pre-registered) analyses reported in the R3 paper, computed from the frozen codes and key.
  1. §4.6: cross-family client-impact cross-tab on items both families coded observable_change = YES.
  2. §6: right-censoring of spec_updated_90d -- items with < 90 days between commit and the recorded HEAD (needs the upstream bare clones;
     skipped with a note if they are absent).
Uses the frozen scorer's own load_codes/final functions (imported read-only). Run from R3_silent_breaking/: /usr/bin/python3 -I -B paper/exploratory_r3.py"""
import collections, csv, datetime as dt, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(B / 'plan'))
from score_r3 import final, load_codes  # noqa: E402

UP = Path('/run/media/afridi/Shared Data/api_research_upstream')


def main():
    P = B / 'packages'
    G1, G2 = load_codes([P / 'r3_blind/codes_G1.csv']), load_codes([P / 'r3_blind/codes_G2.csv'])
    H1, H2 = load_codes(sorted(P.glob('r3_kb*/codes_H1.csv'))), load_codes(sorted(P.glob('r3_kb*/codes_H2.csv')))
    ids = sorted(G1); g = {i: final(G1[i], G2[i]) for i in ids}; h = {i: final(H1[i], H2[i]) for i in ids}
    both = [i for i in ids if g[i]['observable_change'] == 'YES' and h[i]['observable_change'] == 'YES']
    ct = collections.Counter((g[i]['client_impact'], h[i]['client_impact']) for i in both)
    print(f'1. both families YES: {len(both)}')
    L = ['BREAKING', 'COMPATIBLE', 'UNCLEAR']
    print('   GPT \\ Claude    ' + '  '.join(f'{c:>10}' for c in L))
    for a in L: print(f'   {a:<12}({sum(ct[(a, b)] for b in L):>2}) ' + '  '.join(f'{ct[(a, b)]:>10}' for b in L))
    key = list(csv.DictReader(open(B / 'mining/key/r3_key.csv', newline='', encoding='utf-8')))
    heads = dict(l.rstrip('\n').split('\t')[:2] for l in open(B / 'mining/heads.tsv') if '\t' in l)
    if not UP.is_dir(): print('2. skipped: upstream clones not available'); return
    def cdate(repo, rev):
        return dt.datetime.fromisoformat(subprocess.run(['git', '--git-dir', str(UP / f'{repo}.git'), 'log', '-1', '--format=%cI', rev],
                                                       capture_output=True, text=True, check=True).stdout.strip())
    cens = [r for r in key if (cdate(r['repo'], heads[r['repo']]) - cdate(r['repo'], r['commit'])).days < 90]
    print(f'2. right-censored (< 90 days to recorded HEAD): {len(cens)} of {len(key)}; spec_updated_90d false among them: '
          f'{sum(r["spec_updated_90d"] == "false" for r in cens)}')


if __name__ == '__main__':
    main()
