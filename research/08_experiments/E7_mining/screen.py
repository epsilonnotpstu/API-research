#!/usr/bin/python3
"""Save sanitized full patches and show a conservative bounded review screen."""
import json
from pathlib import Path
import re
import runpy
import sys
m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
folder=m['HERE']/'key/review_evidence';folder.mkdir(exist_ok=True)
for r in m['load_sources']():
    if r['repo'] not in sys.argv[1:] or r['rank']>30:continue
    data=m['safe'](m['git'](r['repo'],'diff','--no-ext-diff','--no-textconv','--unified=2',r['parent_commit'],r['fix_commit']).decode('utf-8','replace'))
    target=folder/(r['candidate_id']+'.diff')
    if not target.exists():target.write_text(data)
    paths=[];changes=[]
    for chunk in data.split('diff --git ')[1:]:
        path=chunk.splitlines()[0].split(' b/')[-1]
        if m['SKIP'].search(path) or not (m['CODE'].search(path) or m['DATA'].search(path)):continue
        paths.append(path)
        ls=[x for x in chunk.splitlines()[1:] if x.startswith(('+','-')) and not x.startswith(('+++','---','+import','-import')) and x[1:].strip()]
        changes.extend(ls[:2])
    print(r['repo']+' '+str(r['rank'])+' '+r['message_excerpt'][:100]+' | '+','.join(Path(p).name for p in paths[:3])[:90]+' | '+' / '.join(changes[:2])[:100])
