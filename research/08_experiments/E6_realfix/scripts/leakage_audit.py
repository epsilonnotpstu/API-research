#!/usr/bin/python3
"""Bounded parent release-note/readme scan; no blind package is constructed."""
import csv
import hashlib
import json
from pathlib import Path
import re
import runpy
m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
ROOT=m['ROOT'];git=m['git'];blob=m['blob']
rows=list(csv.DictReader((ROOT/'accepted.csv').open()))
out=[]
for r in rows:
    files=[];hits=[]
    paths=git(r['repo'],'ls-tree','-r','--name-only',r['parent_commit']).decode().splitlines()
    for path in paths:
        if not re.search(r'(?:^|/)(?:[^/]*(?:change.?log|release.?notes?|history|news|changes)|readme)[^/]*\.(?:md|txt|rst|adoc)$',path,re.I):continue
        content=blob(r['repo'],r['parent_commit'],path)
        files.append(dict(path=path,sha256=hashlib.sha256(content.encode()).hexdigest(),lines=len(content.splitlines())))
        needles=[('full_fix_sha',r['fix_commit']),('short_fix_sha',r['fix_commit'][:7]),('exact_subject',r['message_excerpt'])]
        for n,line in enumerate(content.splitlines(),1):
            for kind,needle in needles:
                if needle and needle in line:hits.append({'path':path,'line':n,'match_kind':kind})
    out.append(dict(item_id=r['item_id'],repo=r['repo'],parent_commit=r['parent_commit'],files_scanned=files,hits=hits))
m['dump']('leakage_audit.json',dict(scope='Parent tracked changelog/release/history/news/changes/readme text filenames; exact future fix SHA/7-char SHA/recorded subject only',items=out,total_files_scanned=sum(len(x['files_scanned']) for x in out),total_hits=sum(len(x['hits']) for x in out),limits=['No paraphrase, issue-discussion or all-source semantic leakage audit.','No package was built; this scan is not a blindness guarantee.','Parent release notes may preannounce a squash/backport fix without its final SHA.']))
print(json.dumps({'items':len(out),'files_scanned':sum(len(x['files_scanned']) for x in out),'hits':sum(len(x['hits']) for x in out)}))
