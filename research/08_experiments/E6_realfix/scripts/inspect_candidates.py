#!/usr/bin/python3
"""Persist sanitized review evidence and print bounded excerpts for human/LLM review."""
import argparse
import json
from pathlib import Path
import re
import runpy

m = runpy.run_path(str(Path(__file__).with_name('mine.py')))
ROOT, git, redact = m['ROOT'], m['git'], m['redact']
POOL = json.loads((ROOT / 'candidate_pool.json').read_text())
BYID = {r['candidate_id']:r for r in POOL}

def evidence(cid):
    r=BYID[cid]
    raw=git(r['repo'],'diff','--no-ext-diff','--no-textconv','--unified=5',r['parent_commit'],r['fix_commit']).decode('utf-8','replace')
    safe=redact(raw)
    folder=ROOT/'review_evidence'
    folder.mkdir(exist_ok=True)
    path=folder/(cid+'.diff')
    path.write_text(safe+'\n')
    return safe

def main():
    p=argparse.ArgumentParser()
    p.add_argument('ids',nargs='*')
    p.add_argument('--select',action='store_true')
    p.add_argument('--limit',type=int,default=220)
    p.add_argument('--source',nargs=4,metavar=('REPO','REV','PATH','START:END'))
    args=p.parse_args()
    if args.select:
        selected=[]
        for repo in sorted({r['repo'] for r in POOL}): selected += [r['candidate_id'] for r in POOL if r['repo']==repo][:6]
        (ROOT/'selection.json').write_text(json.dumps({'rule':'first min(6,pool size) per repo by score desc then SHA asc; supplementary candidates recorded separately','initial_ids':selected},indent=2)+'\n')
        print('Initial sample:',len(selected), ' '.join(selected))
        for cid in selected: evidence(cid)
    elif args.source:
        repo,rev,path,span=args.source
        lo,hi=map(int,span.split(':'))
        source=m['blob'](repo,rev,path)
        selected='\n'.join(f'{i}: {l}' for i,l in enumerate(redact(source).splitlines(),1) if lo<=i<=hi)
        print(repo,rev,path,'\n'+selected)
        folder=ROOT/'source_evidence';folder.mkdir(exist_ok=True)
        # Numbered excerpts only: no unrequested raw source snapshots.
        target=folder/(repo+'_'+rev[:12]+'_'+path.replace('/','__')+f'_{lo}-{hi}.txt')
        target.write_text(selected+'\n')
    else:
        for cid in args.ids:
            r=BYID[cid];safe=evidence(cid)
            print('\n###',cid,r['repo'],r['fix_commit'],r['parent_commit'],r['date'],r['message_excerpt'])
            chunks=safe.split('diff --git ')
            kept=[]
            for chunk in chunks[1:]:
                first=chunk.splitlines()[0]
                if re.search(r'\.(java|kt|yaml|yml|json|py)(?: |$)',first) and not re.search(r'(?:src/test|/tests?/|test/resources|package-lock)',first,re.I):
                    kept.extend(('diff --git '+chunk).splitlines())
            print('Total diff lines:',len(safe.splitlines()),'source/contract non-test lines:',len(kept))
            for i,line in enumerate(kept[:args.limit],1): print(line[:500]+(' [long line omitted]' if len(line)>500 else ''))
            if len(kept)>args.limit: print('[Excerpt truncated; complete sanitized diff in review_evidence/'+cid+'.diff]')
            if not kept: print('\n'.join(safe.splitlines()[:min(args.limit,45)]))

if __name__=='__main__':main()
