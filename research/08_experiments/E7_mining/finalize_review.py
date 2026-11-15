#!/usr/bin/python3
"""Record the bounded manual screens separately from evidence-gated acceptance."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
m=runpy.run_path(str(HERE/'mine.py'))
# Explicit exclusions observed in the ranked title/path/delta screens. Other
# unproved pairs are DEFERRED, never automatically promoted to a mismatch.
REJECT={
 'FAAAST-Service':'4,14,18,22,23,29,30',
 'Iced-Latte':'1,2,5,11,13,14,15,20,21,26,29',
 'OpenLineage':'1:30',
 'allure-server':'3,5:18',
 'apicurio-registry':'3,9:13,16:17,19,22:24,28,30',
 'basyx-java-server-sdk':'3:4,9,12:13,17:18,20:21,24:26,29:30',
 'bibliothek':'1', 'catwatch':'1,5,8:13',
 'cwms-data-api':'2:4,6,12:16,19,22:24,29',
 'ditto':'1,3,5:8,10:21,23:30',
 'dockstore':'2,5,7:8,10:13,17,20:23,25,27:30',
 'eudi-srv-verifier-endpoint':'2:15',
 'fineract':'3:4,7,9:18,23,25:30',
 'genome-nexus':'1:18,20:29',
 'gravitee-api-management':'1:19,21:30',
 'harbor':'1:14,16:19,21:24,27:30',
 'hivemq-edge':'2,5:6,10:18,24:30',
 'hydra':'2:7,10,12:25,27:28,30',
 'kapua':'1:5,7:9,11:12,14:16,19,22:27,29:30',
 'kratos':'2:5,7:15,18:26,28:30',
 'microcks':'1:6,8:11,14:15,17:19,21:30',
 'nessie':'1:3,5:18,20,22,24:29',
 'ohsome-api':'4,6,8,10,12:14,16:26,28:30',
 'open-banking-gateway':'1:30',
 'pay-publicapi':'3:6,9:11,13:14,18:22,24,26:30',
 'polaris':'2:5,7,9:15,17:21,23:24,26:30',
 'quartz-manager':'1:30',
 'rhsm-subscriptions':'1:2,4:30',
 'service-api':'2:30',
 'session-service':'2',
 'sldt-digital-twin-registry':'3,5:10,12,14:26,28',
 'spring-batch-rest':'1',
 'strimzi-kafka-bridge':'1:3,6,8:12,14:18,20:21,23:24,26,28:30',
 'tiltaksgjennomforing-api':'1:30',
}

def expand(text):
    result=set()
    for part in text.split(','):
        ends=list(map(int,part.split(':')));result.update(range(ends[0],ends[-1]+1))
    return result

def main():
    pool=json.loads((HERE/'candidate_pool.json').read_text());sources=m['load_sources']()
    accepted=json.loads((HERE/'key/new_accepted.json').read_text())
    freeze=json.loads((HERE/'freeze.json').read_text())
    assert hashlib.sha256((HERE/'candidate_pool.json').read_bytes()).hexdigest()==freeze['pool_sha256']
    assert len(sources)==len(pool)
    assert [{k:r[k] for k in ['candidate_id','repo','rank','score','surface_paths']} for r in sources]==pool
    prior=set()
    for file in ['candidates.csv','t43/candidates.csv']:
        for r in csv.DictReader((m['BASE']/file).open()):
            if r['review_status'] in {'accepted','rejected','deferred'}:prior.add((r['repo'],r['fix_commit']))
    assert not any((r['repo'],r['fix_commit']) in prior for r in sources)
    by_candidate={}
    for r in accepted:by_candidate.setdefault(r['candidate_id'],[]).append(r['item_id'])
    decisions=[];yields=[]
    for repo in sorted({r['repo'] for r in pool}):
        n=0;count=0
        for r in (r for r in sources if r['repo']==repo and r['rank']<=30):
            if count>=6:break
            n+=1;evidence=HERE/'key/review_evidence'/(r['candidate_id']+'.diff');assert evidence.exists()
            ids=by_candidate.get(r['candidate_id'],[]);count+=len(ids)
            status='accepted' if ids else 'rejected' if r['rank'] in expand(REJECT.get(repo,'')) else 'deferred'
            reason=('Exact parent proposition and corresponding developer patch verified; see accepted_full.csv.' if ids else
                    'Ranked title/path/delta screen shows excluded infrastructure, library/client, refactor, cosmetic, generated-only, feature/evolution or internal-domain work; no accepted existing-operation mismatch established.' if status=='rejected' else
                    'Bounded ranked patch screen does not establish a complete, operation-specific parent contract/implementation mismatch. Deferred for additional parent evidence; message alone is insufficient.')
            decisions.append(dict(candidate_id=r['candidate_id'],repo=repo,rank=r['rank'],review_status=status,reason=reason,accepted_items='|'.join(ids),review_depth='bounded patch screen; exact-parent gate for acceptance',review_evidence=str(evidence.relative_to(HERE)),patch_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest()))
        yields.append(dict(repo=repo,pool=sum(r['repo']==repo for r in pool),reviewed=n,accepted=count,stopped='per-repo cap' if count>=6 else 'top 30' if n==30 else 'available pool exhausted'))
    assert sum(r['accepted'] for r in yields)==len(accepted)
    with (HERE/'key/review_decisions.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,list(decisions[0]));w.writeheader();w.writerows(decisions)
    with (HERE/'yield.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,list(yields[0]));w.writeheader();w.writerows(yields)
    summary=dict(pool=len(pool),repos=len(yields),reviewed=len(decisions),accepted_new=len(accepted),review_status_counts=dict(Counter(r['review_status'] for r in decisions)),new_direction_counts=dict(Counter(r['truth_direction'] for r in accepted)),stopping_reason='Every available bare repository reached its top 30 ranked screens or exhausted its smaller pool; 45 new acceptances were not reached.',frozen_pool_verified=True,prior_review_exclusion_verified=True)
    m['dump'](HERE/'summary.json',summary)
    print(json.dumps(summary))

if __name__=='__main__':main()
