#!/usr/bin/python3
"""Prepare individual, evidence-linked screens; these are not acceptances."""
import argparse
import hashlib
import difflib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
M=runpy.run_path(str(HERE/'mine2.py'))

def screen(r):
    folder=HERE/'key/review2_evidence';folder.mkdir(exist_ok=True)
    target=folder/(r['candidate_id']+'.diff')
    if not target.exists():target.write_text(M['safe'](M['git'](r['repo'],'diff','--no-ext-diff','--no-textconv','--unified=3',r['parent_commit'],r['fix_commit']).decode('utf-8','replace')))
    diff=target.read_text();changes=[]
    for chunk in diff.split('diff --git ')[1:]:
        path=chunk.splitlines()[0].split(' b/')[-1]
        if path not in r['surface_paths']:continue
        delta=[l for l in chunk.splitlines()[1:] if l.startswith(('+','-')) and not l.startswith(('+++','---','+import ','-import ','+package ','-package ')) and l[1:].strip() and not re.match(r'^[+-]\s*(?:/\*|\*|//|#|\[REDACTED)',l)]
        removed=[l[1:].strip() for l in delta if l[0]=='-'];added=[l[1:].strip() for l in delta if l[0]=='+']
        meaningful=lambda values:next((l for l in values if len(l)>3),values[0] if values else '(none)')
        changes.append(dict(path=path,old=meaningful(removed),new=meaningful(added),delta=delta))
    first=next((c for c in changes if c['delta']),changes[0] if changes else dict(path=r['surface_paths'][0],old='(none)',new='(none)',delta=[]))
    # Every draft reason quotes this candidate's actual path and individual delta.
    cut=lambda text,n:' '.join(text.split()[:n])[:130]
    title=re.sub(r'(?<!\w)@[\w-]+','[REDACTED attribution]',r['message_excerpt'])
    title=re.sub(r'#\d+|\bfix(?:ed|es)?\b|\([^)]*\)','',title,flags=re.I).strip(' :')
    old,new=first['old'],first['new']
    prefix=0
    while prefix<min(len(old),len(new)) and old[prefix]==new[prefix]:prefix+=1
    # Show the differing part, so common Java prefixes do not obscure the edit.
    start=max(0,prefix-12)
    reason=f"{Path(first['path']).name}: {cut(title,5)}; {cut(old[start:],4)} → {cut(new[start:],4)}. Parent discrepancy unestablished."
    reason=' '.join(reason.split()[:25])
    return dict(candidate_id=r['candidate_id'],repo=r['repo'],rank=r['rank'],review_status='deferred',reason_code='NO_PARENT_MISMATCH',reason=reason,review_evidence=str(target.relative_to(HERE)),patch_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),patch_lines=len(diff.splitlines()),screen_delta=changes)

def main():
    p=argparse.ArgumentParser();p.add_argument('repos',nargs='+');p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=60);a=p.parse_args()
    freeze=json.loads((HERE/'freeze2.json').read_text());assert hashlib.sha256((HERE/'pool2.json').read_bytes()).hexdigest()==freeze['pool_sha256']
    folder=HERE/'key/review2_drafts';folder.mkdir(exist_ok=True)
    for r in json.loads((HERE/'key/pool2_sources.json').read_text()):
        if r['repo'] not in a.repos or not a.start<=r['rank']<=a.end:continue
        d=screen(r);(folder/(r['candidate_id']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        c=next((c for c in d['screen_delta'] if c['delta']),None)
        title=re.sub(r'(?<!\w)@[\w-]+','[REDACTED attribution]',r['message_excerpt'])
        print(f"{r['repo']} {r['rank']} [{d['patch_lines']}] {title[:100]} | "+(Path(c['path']).name+': '+c['old'][:75]+' => '+c['new'][:75] if c else 'No substantive source delta'))

if __name__=='__main__':main()
