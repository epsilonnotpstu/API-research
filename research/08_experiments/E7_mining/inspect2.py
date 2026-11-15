#!/usr/bin/python3
"""Sanitized views of frozen candidates; all history is saved only in key/."""
import argparse
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
M=runpy.run_path(str(HERE/'mine2.py'))
git=M['git'];safe=M['safe']
p=argparse.ArgumentParser();p.add_argument('repo');p.add_argument('ranks',nargs='?',default='1:60');p.add_argument('--lines',type=int,default=16);p.add_argument('--max-paths',type=int,default=5);p.add_argument('--probe',nargs=2);p.add_argument('--context',type=int,default=3);p.add_argument('--full',action='store_true');p.add_argument('--titles',action='store_true');a=p.parse_args()
ranks=set()
for part in a.ranks.split(','):
    ends=list(map(int,part.split(':')));ranks.update(range(ends[0],ends[-1]+1))
for r in json.loads((HERE/'key/pool2_sources.json').read_text()):
    if r['repo']!=a.repo or r['rank'] not in ranks:continue
    print('###',r['candidate_id'],r['repo'],r['rank'],re.sub(r'(?<!\w)@[\w-]+','[REDACTED attribution]',r['message_excerpt']))
    if a.titles:continue
    if a.probe:
        remaining=a.lines
        for path in git(a.repo,'ls-tree','-r','--name-only',r['parent_commit']).decode().splitlines():
            if M['excluded'](path) or not re.search(a.probe[0],path):continue
            lines=safe(git(a.repo,'show',r['parent_commit']+':'+path).decode('utf-8','replace')).splitlines()
            hits=[i for i,l in enumerate(lines) if re.search(a.probe[1],l)]
            nums=sorted({j for i in hits for j in range(max(0,i-a.context),min(len(lines),i+a.context+1))})
            if nums:print('PATH',path)
            for j in nums[:remaining]:print(str(j+1)+': '+lines[j][:600])
            remaining-=min(len(nums),remaining)
            if remaining<=0:break
        continue
    folder=HERE/'key/review2_evidence';folder.mkdir(exist_ok=True)
    target=folder/(r['candidate_id']+'.diff')
    if not target.exists():
        target.write_text(safe(git(a.repo,'diff','--no-ext-diff','--no-textconv','--unified=3',r['parent_commit'],r['fix_commit']).decode('utf-8','replace')))
    diff=target.read_text();chunks=[]
    for chunk in diff.split('diff --git ')[1:]:
        path=chunk.splitlines()[0].split(' b/')[-1]
        if M['excluded'](path) or not (M['production'](path) or path in r['surface_paths']):continue
        ls=chunk.splitlines()[1:]
        if not a.full:ls=[l for l in ls if l.startswith(('+','-')) and not l.startswith(('+++','---','+import ','-import ')) and l[1:].strip()]
        if ls:chunks.append((path,ls))
    print('patch_lines',len(diff.splitlines()),'production_paths',len(chunks))
    for path,ls in chunks[:a.max_paths]:
        print('PATH',path)
        for l in ls[:a.lines]:print(l[:400])
    if len(chunks)>a.max_paths:print('[additional paths in saved evidence]')
