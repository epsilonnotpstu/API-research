"""Boundary + output audit for the R4 blind coders. Prints counts and short flagged snippets only (no codes).
Codex: collab/logs/R4_G?.log (+ resume logs). Claude: subagent transcripts listed in collab/scripts/r4_claude_runs.txt
("<agent_id> <coder> <batch>" per line; transcript dir given with --tasks).
Run: /usr/bin/python3 -I -B r4_audit.py --tasks <dir with <agent_id>.output transcripts>"""
import argparse, csv, json, re, sys
from pathlib import Path
csv.field_size_limit(sys.maxsize)

B = Path(__file__).resolve().parents[2]; P = B / 'packages'; L = B / 'collab/logs'
ALLOWED = {'ac_relevant': {'YES', 'NO', 'UNCLEAR'}}
BAD = re.compile(r'\.\./|/home/afridi(?!/Documents/API research/R4_access_control/packages/r4_)|COLLAB_BOARD|/plan/|/mining/|/notes/|/paper/|'
                 r'key/|research/|r4_score|R4_PLAN|git (log|show|diff)|codes_(?!work_|report_)?(G[12]|H[12])\b')


def check_outputs(d, cid):
    items = [r['item_id'] for r in csv.DictReader(open(d / 'items.csv', newline=''))]
    f = d / f'codes_{cid}.csv'
    rows = list(csv.DictReader(open(f, newline=''))) if f.exists() else []
    order = [r['item_id'] for r in rows] == items
    vals = {r.get('ac_relevant', '').strip().upper() for r in rows}
    return dict(rows=len(rows), expected=len(items), order_ok=order, values_ok=vals <= ALLOWED['ac_relevant'],
                report=(d / f'codes_report_{cid}.md').exists())


def codex():
    for cid in ('G1', 'G2'):
        logs = sorted(L.glob(f'R4_{cid}.log')) + sorted(L.glob(f'R4_{cid}_resume*.log'))
        cmds, flags = 0, []
        for lg in logs:
            for line in lg.read_text(errors='replace').splitlines():
                if line.startswith('exec') or '"command"' in line or line.startswith('/bin/'):
                    cmds += 1
                    own = line.replace('codes_' + cid, 'OWN').replace('codes_work_' + cid, 'OWN')
                    m = BAD.search(own)
                    if m: flags.append(own[max(0, m.start() - 40):m.end() + 40])
        print(f'{cid}: logs {len(logs)} cmds {cmds} flagged {len(flags)} {check_outputs(P / "r4_blind", cid)}')
        for f in flags[:8]: print('    FLAG:', f)


def claude(tasks):
    runs = [l.split() for l in open(Path(__file__).with_name('r4_claude_runs.txt')) if l.strip()]
    for aid, cid, b in runs:
        d = P / f'r4_{b}'; t = Path(tasks) / f'{aid}.output'
        n, flags, first = 0, [], None
        for line in open(t, errors='replace'):
            try: o = json.loads(line)
            except ValueError: continue
            c = o.get('message', {}).get('content')
            for x in c if isinstance(c, list) else []:
                if x.get('type') != 'tool_use': continue
                n += 1; inp = json.dumps(x.get('input', {}), ensure_ascii=False)
                if first is None: first = inp[:110]
                txt = inp.replace(str(d), 'BATCHDIR').replace('codes_' + cid, 'OWN')
                for m in re.finditer(r'/home/afridi[^"\s]*|\.\./|r4_kb(?!' + b[2:] + r')\d|r4_blind|COLLAB|memory|\.claude|/plan/|/mining/|key/|git ', txt):
                    flags.append(txt[max(0, m.start() - 40):m.end() + 40])
        print(f'{cid} {b}: tool calls {n} flagged {len(flags)} {check_outputs(d, cid)}; first: {first}')
        for f in flags[:6]: print('    FLAG:', f)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tasks'); a = ap.parse_args()
    codex()
    if a.tasks: claude(a.tasks)
