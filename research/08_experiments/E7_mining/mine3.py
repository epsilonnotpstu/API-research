#!/usr/bin/python3
"""T50: frozen content-verified pool; read-only Git, no upstream execution."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
P=runpy.run_path(str(HERE/'mine2.py'))
M=P['M']
UPSTREAM=Path('/run/media/afridi/Shared Data/api_research_upstream')
SELECTION=HERE/'t50_repo_selection/selected.tsv'
ANNOTATION=re.compile(rb'(?m)^\s*//\s*(?:@Router\s+\S+\s+\[\w+\]|swagger:route\s+\w+\s+\S+)')

def selected():
    with SELECTION.open() as f:return list(csv.DictReader(f,delimiter='\t'))

def configure():
    repos={r['clone_name']:UPSTREAM/(r['clone_name']+'.git') for r in selected()}
    M['REPOS'].update(repos)
    M['git'].__globals__['REPOS'].update(repos)
    return repos

REPOS=configure()
git=M['git']
objects=P['objects']

def classify(path,versions,has_document=True):
    roles=P['classify'](path,versions)
    if not P['excluded'](path) and not P['DOCS'].search(path) and path.endswith('.go') and has_document and any(ANNOTATION.search(x) for x in versions):
        roles.append('go_swagger_annotations')
    return roles

def discover(metadata):
    repo=metadata['clone_name'];records=[];blob_ids=set();roots=set()
    if not REPOS[repo].is_dir():return [],dict(repo=repo,missing=True,pool3=0)
    raw=git(repo,'log','--all','--no-merges','--no-renames','--raw','--no-abbrev','--date=short','--format=%x00%H%x09%P%x09%cs%x09%s').decode('utf-8','replace')
    total=0
    for block in raw.split('\0')[1:]:
        lines=block.splitlines();sha,parents,date,message=lines[0].split('\t',3);total+=1
        if not parents or not M['CUE'].search(message) or P['SKIP_MESSAGE'].search(message):continue
        changes=[];needed={}
        for line in lines[1:]:
            if not line.startswith(':') or '\t' not in line:continue
            header,path=line.split('\t',1);fields=header.split();old,new,status=fields[2:5]
            changes.append([status,path])
            if P['excluded'](path):continue
            if not (P['DATA'].search(path) or P['JVM'].search(path) and not P['DOCS'].search(path) or P['production'](path) or path.endswith('.go') and not P['DOCS'].search(path)):continue
            needed[path]=[oid for oid in (old,new) if set(oid)!={'0'}];blob_ids.update(needed[path])
        if needed:records.append(dict(repo=repo,fix_commit=sha,parent_commit=parents.split()[0],date=date,message_excerpt=M['safe'](message).strip()[:160],stars=metadata['stars'],changes=changes,needed=needed,cue_score=M['rank_candidate'](message,[])))
    classification={};ids=sorted(blob_ids)
    for start in range(0,len(ids),150):
        for oid,data in objects(repo,ids[start:start+150]).items():
            classification[oid]=(P['openapi'](data),P['annotated'](data),bool(ANNOTATION.search(data)))
    for r in records:
        roots.update(path for path,oids in r['needed'].items() if P['DATA'].search(path) and any(classification[o][0] for o in oids))
    tip=git(repo,'rev-list','--all','--max-count=1').decode().strip()
    if tip:
        paths=[p for p in git(repo,'ls-tree','-r','--name-only',tip).decode().splitlines() if P['DATA'].search(p) and not P['excluded'](p)]
        for start in range(0,len(paths),100):
            for name,data in objects(repo,[tip+':'+p for p in paths[start:start+100]]).items():
                if data and P['openapi'](data):roots.add(name.split(':',1)[1])
    sources=[]
    for r in records:
        roles={};fragments=set();go_paths=[]
        for path,oids in r.pop('needed').items():
            kind=[]
            if P['DATA'].search(path):
                if any(classification[o][0] for o in oids):kind.append('openapi_root')
                else:fragments.add(path)
            else:
                if P['JVM'].search(path) and not P['DOCS'].search(path) and any(classification[o][1] for o in oids):kind.append('contract_annotations')
                if P['production'](path) and P['BEHAVIOUR'].search(path):kind.append('production_behaviour')
                if path.endswith('.go') and not P['DOCS'].search(path) and any(classification[o][2] for o in oids):go_paths.append(path)
            if kind:roles[path]=kind
        ref_evidence={}
        if fragments and roots:
            for revision in (r['parent_commit'],r['fix_commit']):
                reached,evidence=P['reachable'](repo,revision,roots,fragments)
                if reached:
                    ref_evidence[revision]=evidence
                    for path in reached:roles.setdefault(path,[]).append('openapi_ref')
        if go_paths and roots:
            # Annotation sources qualify only alongside a checked-in document.
            present=False
            for revision in (r['parent_commit'],r['fix_commit']):
                for data in objects(repo,[revision+':'+p for p in sorted(roots)]).values():
                    if data and P['openapi'](data):present=True;break
                if present:break
            if present:
                for path in go_paths:roles.setdefault(path,[]).append('go_swagger_annotations')
        if not roles:continue
        r.update(surface_paths=sorted(roles),path_roles=roles,ref_evidence=ref_evidence,score=r.pop('cue_score')+int(any(M['OP'].search(p) for p in roles)))
        sources.append(r)
    sources.sort(key=lambda r:(-r['score'],r['fix_commit']))
    return sources,dict(repo=repo,missing=False,pool3=len(sources),nonmerge_commits=total,known_root_paths=len(roots))

def main():
    destinations=[HERE/'pool3.json',HERE/'freeze3.json',KEY/'pool3_sources.json']
    assert all(not p.exists() for p in destinations),'Refusing to replace frozen pool'
    sources=[];inventory=[]
    for metadata in selected():
        rows,info=discover(metadata);sources.extend(rows);inventory.append(info)
        print(json.dumps(info),flush=True)
    ranks=Counter()
    for i,r in enumerate(sources,1):
        ranks[r['repo']]+=1;r.update(candidate_id=f'P3C{i:06}',rank=ranks[r['repo']])
    pool=[{k:r[k] for k in ('candidate_id','repo','rank','score','surface_paths','path_roles')} for r in sources]
    M['dump'](KEY/'pool3_sources.json',sources);M['dump'](HERE/'pool3.json',pool);M['dump'](HERE/'pool3_inventory.json',inventory)
    M['dump'](HERE/'freeze3.json',dict(pool_sha256=hashlib.sha256((HERE/'pool3.json').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((KEY/'pool3_sources.json').read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),selection_sha256=hashlib.sha256(SELECTION.read_bytes()).hexdigest(),before_review=True,rule='T46 pool2 unchanged; Go @Router/swagger:route annotation sources alongside checked-in documents; descending score then SHA; selected repository order'))

if __name__=='__main__':main()
