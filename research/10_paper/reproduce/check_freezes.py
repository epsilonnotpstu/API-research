"""Verify every *freeze*.sha256 under 08_experiments against the working tree.
Each freeze was written from its own base directory, so each entry is looked up under every plausible base (freeze dir, 08_experiments,
research/, repo root, each package dir) and counts as OK if any of them has the frozen hash. Pseudo-entries (TREE:..., X-tree, K-tree, item-tree, W-tree) are tree hashes and are
reported separately, not checked here. Run from anywhere: /usr/bin/python3 -I -B check_freezes.py"""
import hashlib, re, sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]          # research/
X = R / '08_experiments'
TREE = re.compile(r'^(TREE:|.*-tree$)')
# Documented post-freeze changes (each disclosed where noted); anything else is an unexplained mismatch.
EXPLAINED = {
    'E12_extend/score_e12.py': 'D1 csv field-size fix, no logic change (E12_DEVIATIONS.md)',
    'E7_repairdir/E7_PLAN_AMENDMENTS.md': 'A3 appended after these freezes, append-only (0 lines removed); current text frozen in a3_freeze.sha256',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def bases(f):
    b = [f.parent, X, R, R.parent]
    b += [d for d in (X / 'E2_labelling').iterdir() if d.is_dir()]
    return b


bad_total = 0
for f in sorted(X.glob('*/*freeze*.sha256')):
    entries = []
    for line in f.read_text().splitlines():
        m = re.match(r'^([0-9a-f]{64})\s+\*?(.+)$', line.strip())
        if m: entries.append(m.groups())
    files = [(h, p) for h, p in entries if not TREE.match(p)]
    trees = len(entries) - len(files)
    ok, mism, miss = 0, [], []
    for h, p in files:
        cands = [b / p for b in bases(f) if (b / p).is_file()]
        if any(sha(q) == h for q in cands): ok += 1          # a matching hash cannot be a coincidence
        elif cands: mism.append(p)
        else: miss.append(p)
    expl = [p for p in mism if p in EXPLAINED]; mism = [p for p in mism if p not in EXPLAINED]
    bad_total += len(mism) + len(miss)
    status = 'MISMATCH' if mism else ('MISSING' if miss else ('OK*' if expl else 'OK'))
    print(f'{status:8s} {f.relative_to(X)}  files ok {ok}/{len(files)}  tree-entries {trees}')
    for p in expl: print(f'         documented change: {p} ({EXPLAINED[p]})')
    for p in mism: print(f'         changed after freeze: {p}')
    for p in miss: print(f'         not found: {p}')
print('unexplained content mismatches or missing files:', bad_total)
sys.exit(1 if bad_total else 0)
