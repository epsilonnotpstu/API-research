#!/usr/bin/python3
"""Audit the frozen continuation prefix, then publish only aggregate results."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
R=runpy.run_path(str(HERE/'review_t47.py'))


def audit():
    R['guard']()
    new=R['accepted']()
    prior=json.loads((KEY/'new_accepted.json').read_text())+json.loads((KEY/'new_accepted2.json').read_text())
    prior_counts=Counter(r['repo'] for r in prior)
    old_reviews=R['prior_counts']()
    decisions=[json.loads(p.read_text()) for p in (KEY/'t47_decisions').glob('*.json')]
    decisions.sort(key=lambda r:(r['repo'],r['rank']))
    by_pair={(d['repo'],d['rank']):d for d in decisions}
    assert len(by_pair)==len(decisions)
    by_candidate={}
    for row in new:by_candidate.setdefault(row['candidate_id'],[]).append(row)
    expected=[];yields=[];total=0
    for inventory in json.loads((HERE/'pool2_inventory.json').read_text()):
        repo=inventory['repo'];reviewed=0;count=0;last=old_reviews[repo]
        for row in (r for r in R['sources']() if r['repo']==repo and old_reviews[repo]<r['rank']<=150):
            if total>=40 or prior_counts[repo]+count>=10:break
            pair=repo,row['rank']
            assert pair in by_pair, 'Missing individual ranked decision: '+str(pair)
            d=by_pair[pair]
            assert d['candidate_id']==row['candidate_id']
            assert d['reason_code'] in R['CODES'] and d['reason'].strip() and len(d['reason'].split())<=25
            assert hashlib.sha256((HERE/d['review_evidence']).read_bytes()).hexdigest()==d['patch_sha256']
            additions=by_candidate.get(row['candidate_id'],[])
            assert bool(additions)==(d['review_status']=='accepted')==(d['reason_code']=='ACCEPT')
            assert all(a['rank']==row['rank'] and a['repo']==repo for a in additions)
            count+=len(additions);total+=len(additions);reviewed+=1;last=row['rank']
            assert prior_counts[repo]+count<=10
            expected.append(pair)
        stopped=('T47 target reached' if total>=40 else 'combined repo cap' if prior_counts[repo]+count>=10
                 else 'top 150' if last>=150 else 'available pool exhausted')
        yields.append(dict(repo=repo,pool2=inventory['pool2'],previous_pool2_reviewed=old_reviews[repo],
                           reviewed_T47=reviewed,last_reviewed_rank=last,accepted_T45_T46=prior_counts[repo],
                           accepted_T47=count,accepted_combined=prior_counts[repo]+count,stopped=stopped))
    assert expected==list(by_pair), 'Decisions exceed the continuation stopping prefix'
    assert total==len(new)
    with (HERE.parent/'E6_realfix/combined_accepted.csv').open() as stream:old=list(csv.DictReader(stream))
    identities=[(r['repo'],r['operation'],r['fix_family']) for r in old+prior+new]
    assert len(identities)==len(set(identities))
    assert all(r['source_task']=='T47' and r['set']=='new' for r in new)
    assert max(Counter(r['repo'] for r in prior+new).values())<=10
    selected={d['candidate_id'] for d in decisions}
    previews=Counter(r['repo'] for r in R['sources']() if (KEY/'t47_evidence'/(r['candidate_id']+'.diff')).exists() and r['candidate_id'] not in selected)
    result=dict(reviewed=len(decisions),accepted_T47=len(new),accepted_candidates=len(by_candidate),
                accepted_T45_T46=len(prior),accepted_combined_new=len(prior)+len(new),
                reason_code_counts=dict(Counter(d['reason_code'] for d in decisions)),
                review_status_counts=dict(Counter(d['review_status'] for d in decisions)),
                T47_direction_counts=dict(Counter(r['truth_direction'] for r in new)),
                combined_new_direction_counts=dict(Counter(r['truth_direction'] for r in prior+new)),
                stopping_reason='T47 acceptance threshold reached after the complete final candidate.',
                final_repo=decisions[-1]['repo'],final_rank=decisions[-1]['rank'],
                previews_outside_final_decision_prefix=dict(previews),
                frozen_pool_verified=True,existing_key_verified=True,rank_prefix_verified=True,
                dedup_verified=True,caps_verified=True)
    return decisions,yields,result


def main():
    decisions,yields,result=audit()
    for path,rows in [(KEY/'review_decisions_t47.csv',decisions),(HERE/'yield_t47.csv',yields)]:
        with path.open('x',newline='') as stream:
            writer=csv.DictWriter(stream,list(rows[0]));writer.writeheader();writer.writerows(rows)
    R['private_json'](HERE/'summary_t47.json',result)
    print(json.dumps(result))


if __name__=='__main__':main()
