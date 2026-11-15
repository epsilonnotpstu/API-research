#!/usr/bin/python3
"""Extend T42's read-only Git/redaction pipeline; never execute upstream code."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
m = runpy.run_path(str(BASE / 'scripts/mine.py'))
git, blob = m['git'], m['blob']
def redact(value):
    # Apply T42's filters before any upstream text is displayed or persisted.
    original_count = len(value.splitlines())
    pre=[];private_key=False
    for line in value.splitlines():
        if re.search(r'-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----',line):private_key=True
        if private_key:
            pre.append('[REDACTED private key material]')
            if re.search(r'-----END [A-Z0-9 ]*PRIVATE KEY-----',line):private_key=False
        else:pre.append(line)
    value='\n'.join(pre)+'\n' if pre else ''
    value = m['redact'](value)
    out=[]
    for line in value.splitlines():
        if re.search(r'(?i)\b(?:reviewed|acked|tested|reported|suggested|approved|contributed|signed|co-authored)-by\s*:|\b(?:thanks to|copyright|@author)\b',line):
            line='[REDACTED attribution]'
        if re.search(r'(?i)["\x27]?(?:api[_-]?key|secret|password|token)["\x27]?\s*[:=]\s*["\x27][^"\x27]{8,}',line):
            line='[REDACTED credential-related line]'
        if re.search(r'(?i)[\w.-]*(?:secret|password|api[_-]?key|access[_-]?key|auth[_-]?token)[\w.-]*["\x27]?\s*[:=]\s*["\x27][^"\x27]{8,}',line):
            line='[REDACTED credential-related line]'
        out.append(line)
    # Keep trailing blank source lines too, so every stored numeric locator is stable.
    out.extend([''] * (original_count-len(out)))
    return '\n'.join(out)+'\n' if out else ''

META = [
 ('strimzi-kafka-bridge',346,'2016-03','2026-11'),
 ('rhsm-subscriptions',75,'2019-03','2026-11'),
 ('open-banking-gateway',344,'2019-11','2026-01'),
 ('dockstore',132,'2015-04','2026-11'),
 ('hivemq-edge',167,'2023-06','2026-11'),
 ('OpenLineage',2763,'2020-10','2026-11'),
 ('service-api',54,'2016-09','2026-11'),
 ('Iced-Latte',641,'2022-12','2026-11'),
 ('eudi-srv-verifier-endpoint',66,'2023-05','2026-11'),
 ('cwms-data-api',30,'2020-10','2026-11'),
 ('allure-server',248,'2020-04','2026-11'),
 ('fineract',2627,'2015-12','2026-11')]
REPOS=[v[0] for v in META]
CUE=re.compile(r'\b(?:fix\w*|correct\w*|validat\w*|optional|required|nullable|null|NPE|serializ\w*|deserializ\w*|status|response|content.type|pagination|default|contract|swagger|openapi|conform\w*|bad.request|404|400|500|422)\b',re.I)
SURFACE=re.compile(r'\.(?:java|kt)$|(?:openapi|swagger|api-doc).*\.(?:yaml|yml|json)$',re.I)
CONTRACT_PATH=re.compile(r'(?:openapi|swagger|api-doc|api-spec|specification).*\.(?:yaml|yml|json)$',re.I)
SPECIFIC=re.compile(r'\b(?:status|response.code|http|400|404|500|422|optional|required|nullable|NPE|null.pointer|content.type|serializ\w*|deserializ\w*|pagination|default.value|validation|validat\w*|bad.request)\b',re.I)

def dump(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
    if (ROOT/'candidate_pool.json').exists():
        raise SystemExit('T43 discovery pool is frozen. Rebuild tables from the saved pool with t43_build.py; use a new task directory for new history mining.')
    pool=[];inventory=[]
    with (BASE/'t43_repo_meta.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['repo','stars','created_month','last_push_month','source','retrieved_date'])
        for repo,stars,created,pushed in META:
            w.writerow([repo,stars,created,pushed,'Supervisor-provided GitHub API metadata; 09_collab/tasks/T43.md','2026-11-15'])
    for repo in REPOS:
        head=git(repo,'rev-list','-1','HEAD').decode().strip()
        paths=git(repo,'ls-tree','-r','--name-only',head).decode().splitlines()
        specs=[]
        # Path inventory only; acceptance inspects the exact parent, including annotations.
        for p in paths:
            if CONTRACT_PATH.search(p) and not re.search(r'node_modules|package-lock',p):
                specs.append(p)
        history=git(repo,'log','--all','--no-merges','--date=short','--format=@@%H\t%P\t%cs\t%s','--name-status').decode('utf-8','replace')
        n=0
        for block in history.split('@@')[1:]:
            lines=block.splitlines()
            sha,parents,date,msg=lines[0].split('\t',3);n+=1
            changes=[l.split('\t') for l in lines[1:] if '\t' in l]
            prod=[c[-1] for c in changes if SURFACE.search(c[-1]) and not re.search(r'(?:^|/)(?:tests?|generated|target)/|src/test|/client/',c[-1],re.I)]
            if not parents or not CUE.search(msg) or not prod:continue
            if re.search(r'^(?:bump|merge|release|revert|chore\(deps\)|build\(deps\))\b|dependabot|renovate',msg,re.I):continue
            contract=[c[-1] for c in changes if CONTRACT_PATH.search(c[-1])]
            behaviour=[p for p in prod if p.endswith(('.java','.kt'))]
            specific=bool(SPECIFIC.search(msg));correction=bool(re.search(r'\bfix\w*|\bcorrect\w*|\bwrong|\binvalid|\berror|\bbug',msg,re.I))
            # Coarse contract-change penalty is a retrieval cue, never an operation-level judgment.
            score=30*specific+12*correction+10*bool(behaviour and not contract)+4*bool(re.search(r'contract|openapi|swagger|document',msg,re.I))+min(len(prod),3)
            if re.search(r'\b(?:add|introduc|implement|support|migrat|refactor|upgrad|generat)',msg,re.I) and not correction:score-=12
            pool.append(dict(repo=repo,fix_commit=sha,parent_commit=parents.split()[0],date=date,message_excerpt=redact(msg).strip()[:200],score=score,changed_files=len(changes),surface_paths=' | '.join(prod),contract_paths_changed=contract,changes=changes))
        inventory.append(dict(repo=repo,git_dir=m['REPOS'][repo],head=head,nonmerge_commits=n,head_contract_path_candidates=specs))
        print(json.dumps({'repo':repo,'commits':n,'pool':sum(x['repo']==repo for x in pool)}),flush=True)
    pool.sort(key=lambda r:(r['repo'],-r['score'],r['fix_commit']))
    ranks={}
    for i,r in enumerate(pool,1):
        ranks[r['repo']]=ranks.get(r['repo'],0)+1;r['rank']=ranks[r['repo']];r['candidate_id']=f'T43C{i:05}'
    dump('candidate_pool.json',pool);dump('inventory.json',inventory)
    dump('mining_manifest.json',dict(finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),history='all reachable refs; non-merge, single-parent',no_network=True,upstream_execution=False,reuses='scripts/mine.py:git,blob,redact',top_depth=20))

if __name__=='__main__':main()
