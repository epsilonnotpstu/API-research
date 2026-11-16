"""Licence in force at each item's parent commit (read-only git on bare clones; nothing executed).
Run: /usr/bin/python3 -I -B licence_at_parent.py <accepted_full_*.csv> [...]
Prints per-repo licence class counts, plus the item ids whose licence needs review (never directions)."""
import csv, subprocess, sys, collections
from pathlib import Path

UP = Path('/run/media/afridi/Shared Data/api_research_upstream')
NAMES = ('LICENSE', 'LICENSE_SOURCE', 'LICENSE.txt', 'LICENSE.md', 'LICENCE', 'COPYING', 'LICENSE-2.0.txt', 'epl-2.0.html')
RULES = [('Personal Evaluation', 'RESTRICTIVE'), ('SPDX-License-Identifier: Apache-2.0', 'Apache-2.0'), ('Apache License', 'Apache-2.0'), ('MIT License', 'MIT'), ('Permission is hereby granted, free of charge', 'MIT'),
         ('Eclipse Public License', 'EPL-2.0'), ('GNU AFFERO', 'AGPL-3.0'), ('GNU GENERAL PUBLIC LICENSE', 'GPL'),
         ('Attribution-NonCommercial', 'CC-BY-NC')]


def git(repo, *a):
    r = subprocess.run(['git', '--git-dir', str(UP / f'{repo}.git'), *a], capture_output=True, text=True, errors='replace')
    return r.stdout if r.returncode == 0 else None


def classify(repo, commit):
    for n in NAMES:
        t = git(repo, 'show', f'{commit}:{n}')
        if t:
            head = t[:4000]
            for pat, lab in RULES:
                if pat.lower() in head.lower():
                    return lab
            return f'UNKNOWN({n})'
    return 'NONE_FOUND'


def main():
    out = collections.Counter(); bad = []
    for f in sys.argv[1:]:
        for r in csv.DictReader(open(f, newline='')):
            repo = r['repo'].split('/')[-1]
            lab = classify(repo, r['parent_commit'])
            out[(repo, lab)] += 1
            if lab in ('RESTRICTIVE', 'CC-BY-NC', 'NONE_FOUND') or lab.startswith('UNKNOWN'):
                bad.append((f, r['item_id'], repo, lab))
    for (repo, lab), n in sorted(out.items()):
        print(f'{repo:35s} {lab:15s} {n}')
    print('flagged (item_id only, review needed):', [(b[1], b[2], b[3]) for b in bad])


if __name__ == '__main__':
    main()
