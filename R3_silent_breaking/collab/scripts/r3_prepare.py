"""After the T53 build: create r3_kb1..N for the Claude coders H1/H2.
Batches are consecutive slices of r3_blind/items.csv in order, at most 15 items each. items.csv is written with LF.
TASK_R3.md is copied byte-identical from the frozen plan copy. Refuses to overwrite.
Run: /usr/bin/python3 -I -B r3_prepare.py"""
import csv, filecmp, math, shutil
from pathlib import Path

P = Path(__file__).resolve().parents[2] / 'packages'
src = P / 'r3_blind'
raw = (src / 'items.csv').read_bytes(); assert b'\r' not in raw
rows = list(csv.DictReader(open(src / 'items.csv', newline='')))
cols = list(rows[0].keys()); ids = [r['item_id'] for r in rows]
assert ids and all(i.startswith('B') for i in ids) and len(set(ids)) == len(ids)
assert filecmp.cmp(src / 'TASK_R3.md', P.parent / 'plan/TASK_R3.md', shallow=False), 'TASK_R3.md differs from the frozen plan copy'
n = len(ids); N = math.ceil(n / 15); size = math.ceil(n / N)
kbs = []
for b in range(N):
    d = P / f'r3_kb{b + 1}'; assert not d.exists(), d; d.mkdir(); part = rows[b * size:(b + 1) * size]
    with open(d / 'items.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n'); w.writeheader(); w.writerows(part)
    for r in part: shutil.copytree(src / r['item_id'], d / r['item_id'])
    for name in ('TASK_R3.md', 'README.md'):
        if (src / name).exists(): shutil.copy2(src / name, d / name)
    kbs.append((d.name, len(part)))
assert [r['item_id'] for d, _ in kbs for r in csv.DictReader(open(P / d / 'items.csv', newline=''))] == ids
print('items', n, 'batches', kbs)
