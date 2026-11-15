#!/usr/bin/python3
"""T43 sanitized diff and exact-parent source inspection helper."""
import argparse,json,re,runpy
from pathlib import Path
m=runpy.run_path(str(Path(__file__).with_name('t43_mine.py')))
ROOT=m['ROOT'];pool=json.loads((ROOT/'candidate_pool.json').read_text())
p=argparse.ArgumentParser();p.add_argument('repo');p.add_argument('ranks',nargs='?',default='1:20');p.add_argument('--titles',action='store_true');p.add_argument('--compact',action='store_true');p.add_argument('--lines',type=int,default=130);p.add_argument('--probe',nargs=2);p.add_argument('--fix',action='store_true');p.add_argument('--context',type=int,default=4)
a=p.parse_args(); ranks=set()
for span in a.ranks.split(','):
    ends=list(map(int,span.split(':')));ranks.update(range(ends[0],ends[-1]+1))
for r in pool:
    if r['repo']!=a.repo or r['rank'] not in ranks:continue
    print('###',r['candidate_id'],r['repo'],r['rank'],r['score'],r['fix_commit'][:12],r['message_excerpt'])
    if a.titles:continue
    if a.probe:
        rev=r['fix_commit'] if a.fix else r['parent_commit']
        paths=m['git'](a.repo,'ls-tree','-r','--name-only',rev).decode().splitlines()
        for path in paths:
            if not re.search(a.probe[0],path):continue
            raw=m['blob'](a.repo,rev,path);safe=m['redact'](raw).splitlines()
            hits=[i for i,l in enumerate(safe) if re.search(a.probe[1],l)]
            if not hits:continue
            nums=sorted({j for i in hits for j in range(max(0,i-a.context),min(len(safe),i+a.context+1))})
            print(rev+':'+path)
            for j in nums[:a.lines]:print(str(j+1)+': '+safe[j][:500])
        continue
    diff=m['redact'](m['git'](a.repo,'diff','--no-ext-diff','--no-textconv','--unified=3',r['parent_commit'],r['fix_commit']).decode('utf-8','replace'))
    folder=ROOT/'review_evidence';folder.mkdir(exist_ok=True);(folder/(r['candidate_id']+'.diff')).write_text(diff+'\n')
    kept=[]
    for chunk in diff.split('diff --git ')[1:]:
        path=chunk.splitlines()[0].split(' b/')[-1]
        if re.search(r'src/test|(?:^|/)(?:tests?|generated|target)/|package-lock|\.snap$',path,re.I):continue
        if not re.search(r'\.(java|kt|yaml|yml|json|md|adoc|properties|xml)$',path):continue
        if a.compact:
            changes=[l for l in chunk.splitlines() if l.startswith(('+','-')) and not l.startswith(('+++','---','+import ','-import ')) and l[1:].strip() and not l[1:].lstrip().startswith(('*','//'))]
            if changes:kept.extend([path]+changes[:16])
        else:kept.extend(('diff --git '+chunk).splitlines())
    print('diff_lines',len(diff.splitlines()),'production_excerpt_lines',len(kept))
    for l in kept[:a.lines]:print(l[:500])
    if len(kept)>a.lines:print('[bounded diff screen; full sanitized diff saved]')
