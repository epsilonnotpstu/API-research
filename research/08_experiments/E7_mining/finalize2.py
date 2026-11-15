#!/usr/bin/python3
"""Publish individual decisions only after the frozen ranked screens are signed off."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
M=runpy.run_path(str(HERE/'mine2.py'));KEY=HERE/'key'
CODES=set('ACCEPT NOT_CONTRACT_RELATED NEW_FEATURE_OR_ENDPOINT REFACTOR_OR_RENAME GENERATED_OR_DOCS_ONLY_CHURN BOTH_CHANGED_TO_NEW_BEHAVIOUR NO_PARENT_MISMATCH TEST_OR_CLIENT_ONLY TOO_LARGE_TO_ESTABLISH OTHER'.split())

def main():
    freeze=json.loads((HERE/'freeze2.json').read_text())
    for file,field in [(HERE/'pool2.json','pool_sha256'),(KEY/'pool2_sources.json','source_sha256')]:assert hashlib.sha256(file.read_bytes()).hexdigest()==freeze[field]
    sources=json.loads((KEY/'pool2_sources.json').read_text());prior=json.loads((KEY/'new_accepted.json').read_text());new=json.loads((KEY/'new_accepted2.json').read_text())
    signs=json.loads((KEY/'review2_signoff.json').read_text());overrides=json.loads((KEY/'review2_overrides.json').read_text())
    notes={(r['repo'],int(r['rank'])):r for r in csv.DictReader((KEY/'review2_notes.tsv').open(),delimiter='\t')}
    old_counts=Counter(r['repo'] for r in prior);accepted={}
    for r in new:accepted.setdefault(r['candidate_id'],[]).append(r)
    prior_review=M['reviewed']();assert not any((r['repo'],r['fix_commit']) in prior_review for r in sources)
    decisions=[];yields=[];total=len(prior);included=[]
    for inventory in json.loads((HERE/'pool2_inventory.json').read_text()):
        repo=inventory['repo'];n=0;count=0
        for r in (r for r in sources if r['repo']==repo and r['rank']<=60):
            if old_counts[repo]+count>=6 or total>=45:break
            assert r['rank']<=signs.get(repo,0),'Screen not signed off'
            d=json.loads((KEY/'review2_drafts'/(r['candidate_id']+'.json')).read_text());assert d['repo']==repo and d['rank']==r['rank']
            note=notes.get((repo,r['rank'])) or overrides.get(repo,{}).get(str(r['rank']))
            if note:
                d['reason_code']=note['reason_code']
                if note.get('reason'):d['reason']=note['reason']
                else:
                    tails={'REFACTOR_OR_RENAME':'Refactor; no established wire discrepancy.','NOT_CONTRACT_RELATED':'Internal concern; no established operation discrepancy.','GENERATED_OR_DOCS_ONLY_CHURN':'Documentation or generation detail only.','NEW_FEATURE_OR_ENDPOINT':'Adds behaviour rather than aligning an existing discrepancy.','BOTH_CHANGED_TO_NEW_BEHAVIOUR':'Both surfaces adopt new behaviour.','TOO_LARGE_TO_ESTABLISH':'Patch too broad for a bounded parent comparison.','OTHER':'Excluded after individual patch screen.'}
                    prefix=d['reason'].replace('Parent discrepancy unestablished.','').strip()
                    tail=tails.get(d['reason_code'],'Parent discrepancy unestablished.')
                    d['reason']=' '.join(prefix.split()[:max(1,25-len(tail.split()))])+ ' '+tail
            selected=accepted.get(r['candidate_id'],[])
            if selected:
                d.update(review_status='accepted',reason_code='ACCEPT',reason='Parent locators establish '+selected[0]['operation']+' '+selected[0]['fix_family']+'; resolving patch and full evidence verified.')
                d['reason']=' '.join(d['reason'].split()[:25]);included.extend(x['item_id'] for x in selected)
            else:d['review_status']='deferred' if d['reason_code'] in {'NO_PARENT_MISMATCH','TOO_LARGE_TO_ESTABLISH'} else 'rejected'
            assert d['reason_code'] in CODES and len(d['reason'].split())<=25
            assert hashlib.sha256((HERE/d['review_evidence']).read_bytes()).hexdigest()==d['patch_sha256']
            decisions.append({k:d[k] for k in ['candidate_id','repo','rank','review_status','reason_code','reason','review_evidence','patch_sha256','patch_lines']}|dict(accepted_items='|'.join(x['item_id'] for x in selected),review_depth='exact parent contract/implementation and resolving patch' if selected else 'individual sanitized patch screen; unproved pairs deferred'))
            n+=1;count+=len(selected);total+=len(selected);assert old_counts[repo]+count<=6
        yields.append(dict(repo=repo,pool2=inventory['pool2'],reviewed=n,accepted_T46=count,accepted_T45=old_counts[repo],accepted_combined=old_counts[repo]+count,stopped='combined target reached' if total>=45 else 'per-repo cap' if old_counts[repo]+count>=6 else 'top 60' if n==60 else 'available pool exhausted'))
    assert set(included)=={r['item_id'] for r in new},'Accepted selection violates stopping rule or rank order'
    for p,rows in [(KEY/'review_decisions2.csv',decisions),(HERE/'yield2.csv',yields)]:
        with p.open('x',newline='') as f:
            w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
    result=dict(pool2=len(sources),repos=len(yields),reviewed=len(decisions),accepted_T46=len(new),accepted_combined_new=len(prior)+len(new),reason_code_counts=dict(Counter(r['reason_code'] for r in decisions)),review_status_counts=dict(Counter(r['review_status'] for r in decisions)),T46_direction_counts=dict(Counter(r['truth_direction'] for r in new)),combined_new_direction_counts=dict(Counter(r['truth_direction'] for r in prior+new)),stopping_reason='Combined new acceptance target reached.' if total>=45 else 'Every repository reached top 60, exhausted its smaller pool, or reached the six-item combined per-repository cap.',frozen_pool_verified=True,prior_review_exclusion_verified=True)
    M['M']['dump'](HERE/'summary2.json',result);print(json.dumps(result))

if __name__=='__main__':main()
