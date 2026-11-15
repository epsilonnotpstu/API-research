#!/usr/bin/python3
"""Read text blobs using Git, filter explicit paths, redact before output."""
import argparse
import json
from pathlib import Path
import re
import runpy

m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
ROOT=m['ROOT']
p=argparse.ArgumentParser()
p.add_argument('candidate');p.add_argument('path_regex');p.add_argument('line_regex')
p.add_argument('--fix',action='store_true');p.add_argument('--context',type=int,default=5)
p.add_argument('--max-lines',type=int,default=180)
a=p.parse_args()
r=next(r for r in json.loads((ROOT/'candidate_pool.json').read_text()) if r['candidate_id']==a.candidate)
rev=r['fix_commit'] if a.fix else r['parent_commit']
paths=m['git'](r['repo'],'ls-tree','-r','--name-only',rev).decode().splitlines()
for path in paths:
    if not re.search(a.path_regex,path): continue
    lines=m['redact'](m['blob'](r['repo'],rev,path)).splitlines()
    hits=[i for i,l in enumerate(lines) if re.search(a.line_regex,l)]
    if not hits: continue
    include=sorted({j for i in hits for j in range(max(0,i-a.context),min(len(lines),i+a.context+1))})
    print('\n',a.candidate,r['repo'],rev,path)
    print('\n'.join(f'{i+1}: {lines[i][:500]}' for i in include[:a.max_lines]))
    if len(include)>a.max_lines: print('[bounded source excerpt]')
