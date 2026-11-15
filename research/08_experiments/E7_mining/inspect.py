#!/usr/bin/python3
"""Bounded, redacted manual review views, with full diffs kept inside key/."""
import argparse
import json
from pathlib import Path
import re
import runpy
m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
HERE=m['HERE'];git=m['git'];safe=m['safe']
p=argparse.ArgumentParser();p.add_argument('repo');p.add_argument('ranks',nargs='?',default='1:30');p.add_argument('--titles',action='store_true');p.add_argument('--lines',type=int,default=80);p.add_argument('--probe',nargs=2);p.add_argument('--fix',action='store_true');p.add_argument('--context',type=int,default=3);p.add_argument('--full',action='store_true')
a=p.parse_args();ranks=set()
for span in a.ranks.split(','):
    ends=list(map(int,span.split(':')));ranks.update(range(ends[0],ends[-1]+1))
for r in m['load_sources']():
    if r['repo']!=a.repo or r['rank'] not in ranks:continue
    print('###',r['candidate_id'],r['repo'],r['rank'],r['message_excerpt'])
    if a.titles:continue
    if a.probe:
        rev=r['fix_commit'] if a.fix else r['parent_commit']
        remaining=a.lines
        for path in git(a.repo,'ls-tree','-r','--name-only',rev).decode().splitlines():
            if not re.search(a.probe[0],path) or m['SKIP'].search(path):continue
            text=safe(git(a.repo,'show',rev+':'+path).decode('utf-8','replace')).splitlines()
            hits=[i for i,l in enumerate(text) if re.search(a.probe[1],l)]
            nums=sorted({j for i in hits for j in range(max(0,i-a.context),min(len(text),i+a.context+1))})
            if nums:print('PATH',path)
            for j in nums[:remaining]:print(str(j+1)+': '+text[j][:900])
            remaining-=min(len(nums),remaining)
            if remaining<=0:break
        continue
    diff=safe(git(a.repo,'diff','--no-ext-diff','--no-textconv','--unified=3',r['parent_commit'],r['fix_commit']).decode('utf-8','replace'))
    folder=HERE/'key/review_evidence';folder.mkdir(exist_ok=True)
    (folder/(r['candidate_id']+'.diff')).write_text(diff)
    chunks=[]
    for chunk in diff.split('diff --git ')[1:]:
        path=chunk.splitlines()[0].split(' b/')[-1]
        if m['SKIP'].search(path) or not re.search(r'\.(java|kt|yaml|yml|json|go|py|properties)$',path):continue
        ls=chunk.splitlines()[1:]
        if not a.full:ls=[l for l in ls if l.startswith(('+','-','@@')) and not l.startswith(('+++','---','+import ','-import ')) and l[1:].strip()]
        if ls:chunks.extend([path]+ls[:(a.lines if a.full else 12)])
    print('diff_lines',len(diff.splitlines()),'screen_lines',len(chunks))
    for l in chunks[:a.lines]:print(l[:450])
    if len(chunks)>a.lines:print('[bounded screen; full diff saved in key]')
