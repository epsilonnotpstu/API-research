#!/usr/bin/python3
"""Audit round-robin prefix, licence/cap gates, preview ledger and preservation."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
R=runpy.run_path(str(HERE/'review_t50.py'))
validate_previews=runpy.run_path(str(HERE/'finalize_t48.py'))['validate_previews']

def audit():
    R['guard']()
    new=R['accepted']();decisions=R['decisions']()
    by_pair={(d['repo'],d['rank']):d for d in decisions}
    assert len(by_pair)==len(decisions)
    by_candidate={}
    for row in new:by_candidate.setdefault(row['candidate_id'],[]).append(row)
    sources={(r['repo'],r['rank']):r for r in R['sources']()}
    capped=[json.loads(p.read_text()) for p in sorted((KEY/'t50_capped').glob('*.json'))]
    stop=json.loads((KEY/'t50_stop.json').read_text()) if (KEY/'t50_stop.json').exists() else None
    ordered=[];counts=Counter();valid_counts=[];cap_rows=[]
    for _,repo,rank in R['plan']():
        if len(new)>=60 and sum(counts.values())>=60:break
        if counts[repo]>=10:continue
        if stop and rank>stop['completed_round']:break
        pair=repo,rank
        assert pair in by_pair,'Missing round-robin candidate decision'
        d=by_pair[pair];source=sources[pair]
        assert d['candidate_id']==source['candidate_id']
        assert d['reason_code'] in R['CODES'] and 0<len(d['reason'].split())<=25
        assert hashlib.sha256((HERE/d['review_evidence']).read_bytes()).hexdigest()==d['patch_sha256']
        additions=by_candidate.get(d['candidate_id'],[]);valid=R['valid_items'](d['candidate_id'])
        excluded=[r for r in capped if r['candidate_id']==d['candidate_id']]
        assert bool(additions)==(d['review_status']=='accepted')==(d['reason_code']=='ACCEPT')
        assert bool(valid)==bool(additions)
        if additions:
            keep,fix,repo_cap=R['select_operations'](valid,10-counts[repo])
            assert {r['operation'] for r in keep}=={r['operation'] for r in additions}
            assert len(additions)<=2
            assert {r['operation'] for r in excluded}=={r['operation'] for r in fix+repo_cap}
            for code,group in [('FIX_CAP',fix),('REPO_CAP',repo_cap)]:
                assert {r['operation'] for r in excluded if r['reason_code']==code}=={r['operation'] for r in group}
            licence=json.loads((KEY/'t50_licences'/(d['candidate_id']+'.json')).read_text())
            assert licence['parent_commit']==source['parent_commit'] and licence['files']
            assert licence['licence_at_parent'] not in {'UNKNOWN','RESTRICTIVE'}
            for item in additions:assert item['licence_at_parent']==licence['licence_at_parent']
            valid_counts.append(len(valid));cap_rows.extend(excluded)
        if d['reason'].startswith('LICENCE:'):assert d['reason_code']=='OTHER'
        counts[repo]+=len(additions);assert counts[repo]<=10
        ordered.append(d)
    assert {(d['repo'],d['rank']) for d in ordered}==set(by_pair)
    assert len(cap_rows)==len(capped) and sum(counts.values())==len(new)
    assert R['next_row']() is None
    events=[json.loads(p.read_text()) for p in sorted((KEY/'t50_previews').glob('*.json'))]
    evidence={p.stem for p in (KEY/'t50_evidence').glob('*.diff')}
    seen=validate_previews(ordered,events,evidence)
    previous=R['previous_items']()
    identities=[(r['repo'],r['operation'],r['fix_family']) for r in previous+new]
    assert len(identities)==len(set(identities))
    for row in new:
        assert row['source_task']=='T50' and row['set']=='new'
        assert row['proposition'].startswith(row['operation']+': contract says ') and '; implementation does ' in row['proposition']
        check=json.loads(row['proposition_check']);assert check['contract'] and check['implementation']
        assert all(loc.rsplit(':',2)[0]==row['parent_commit'] for loc in sum(check.values(),[]))
    sizes=Counter(r['repo'] for r in R['sources']());yields=[]
    for meta in R['P3']['selected']():
        repo=meta['clone_name'];reviewed=[d for d in ordered if d['repo']==repo]
        last=max((d['rank'] for d in reviewed),default=0)
        reason='repo cap' if counts[repo]>=10 else 'pool exhausted' if last>=sizes[repo] else 'budget after complete round' if stop else 'T50 target reached'
        yields.append(dict(repo=repo,pool3=sizes[repo],reviewed=len(reviewed),accepted_candidates=sum(d['reason_code']=='ACCEPT' for d in reviewed),items=counts[repo],capped=counts[repo]>=10,last_reviewed_rank=last,stop_reason=reason))
    stopping=stop['reason'] if stop else 'T50 acceptance threshold reached' if len(new)>=60 else 'Every repo capped or exhausted'
    summary=dict(repositories=len(yields),pool3=sum(sizes.values()),reviewed=len(ordered),accepted_candidates=len(by_candidate),accepted_items=len(new),
        items_per_accepted_candidate=dict(sorted(Counter(str(len(v)) for v in by_candidate.values()).items())),
        valid_operations_per_candidate=dict(sorted(Counter(map(str,valid_counts)).items())),
        FIX_CAP_exclusions=sum(r['reason_code']=='FIX_CAP' for r in capped),REPO_CAP_exclusions=sum(r['reason_code']=='REPO_CAP' for r in capped),
        LICENCE_rejections=sum(d['reason'].startswith('LICENCE:') for d in ordered),reason_code_counts=dict(Counter(d['reason_code'] for d in ordered)),
        review_status_counts=dict(Counter(d['review_status'] for d in ordered)),aggregate_directions=dict(Counter(r['truth_direction'] for r in new)),
        stopping_reason=stopping,completed_round=stop['completed_round'] if stop else max(d['rank'] for d in ordered),
        preview_record=dict(events=len(events),unique_candidates=len(seen),outside_final_prefix=0,without_final_decision=0,lookahead_before_prior_decision=0,chronological_sequence_verified=True),
        preservation_verified=True,round_robin_verified=True,cap_verified=True,licence_gate_verified=True,dedup_verified=True)
    fields=list(ordered[0])+['operation','source_item'];exported=[dict(d,operation='',source_item='') for d in ordered]
    for row in cap_rows:
        d=next(d for d in ordered if d['candidate_id']==row['candidate_id'])
        exported.append(dict(d,review_status='accepted_capped',reason_code=row['reason_code'],reason=row['reason'],operation=row['operation'],source_item=row['item_id']))
    assert all(set(d)==set(fields) for d in exported)
    return ordered,yields,summary,exported

def main():
    _,yields,summary,decisions=audit()
    B=runpy.run_path(str(HERE/'build.py'))
    for path,rows in [(KEY/'review_decisions_t50.csv',decisions),(HERE/'yield_t50.csv',yields)]:
        with path.open('xb') as f:f.write(B['cb'](list(rows[0]),rows))
    R['private_json'](HERE/'summary_t50.json',summary)
    print(json.dumps(summary))

if __name__=='__main__':main()
