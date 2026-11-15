#!/usr/bin/python3
"""Materialize manual decisions, parent-only propositions and checked source locators."""
from collections import Counter
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import runpy

m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
d=runpy.run_path(str(Path(__file__).with_name('curation.py')))
ROOT=m['ROOT'];git=m['git'];redact=m['redact']
pool=json.loads((ROOT/'candidate_pool.json').read_text());byid={r['candidate_id']:r for r in pool}
reviews=d['REVIEWS'];accepted=d['ACCEPTED']
selection=json.loads((ROOT/'selection.json').read_text())
assert set(selection['initial_ids'])<=set(reviews)
assert len(reviews)>=60
assert {x['candidate_id'] for x in accepted}=={k for k,v in reviews.items() if v[0]=='A'}
assert len({(byid[x['candidate_id']]['repo'],byid[x['candidate_id']]['fix_commit']) for x in accepted})==len(accepted)
for cid in reviews:
    path=ROOT/'review_evidence'/(cid+'.diff')
    if not path.exists():
        row=byid[cid]
        path.parent.mkdir(exist_ok=True)
        path.write_text(redact(git(row['repo'],'diff','--no-ext-diff','--no-textconv','--unified=5',row['parent_commit'],row['fix_commit']).decode('utf-8','replace'))+'\n')
selection['supplementary_ids']=sorted(set(reviews)-set(selection['initial_ids']))
selection['supplementary_rule']='Adaptive purposive expansion: own-service contract correction titles plus candidate validation/status fixes. IDs frozen explicitly; not a random sample.'
m['dump']('selection.json',selection)
source_dir=ROOT/'source_evidence';source_dir.mkdir(exist_ok=True)
cache={};assertions=0

def source(repo,rev,path):
    key=(repo,rev,path)
    if key not in cache:
        raw=git(repo,'show',rev+':'+path)
        cache[key]=(raw.decode('utf-8','replace'),hashlib.sha256(raw).hexdigest())
    return cache[key]

def write_csv(name,rows,fields=None):
    with (ROOT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields or list(rows[0]));writer.writeheader();writer.writerows(rows)

accepted_rows=[];evidence_index=[]
for i,a in enumerate(accepted,1):
    cid=a['candidate_id'];row=byid[cid];item_id=f'R{i:03}'
    assert re.match(r'^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) \S+: contract says .+; implementation does .+$',a['proposition'])
    assert a['proposition'].startswith(a['operation']+': contract says ')
    assert not re.search(r'\b(fix|later|changed|corrected|updated|developer)\b',a['proposition'],re.I)
    assert len(row['message_excerpt'])<=160
    locators=[];excerpts=[]
    for j,loc in enumerate(a['locators'],1):
        rev=row['parent_commit'] if loc['side']=='parent' else row['fix_commit']
        content,sha256=source(row['repo'],rev,loc['path']);lines=content.splitlines()
        hits=[k for k,line in enumerate(lines) if loc['needle'] in line]
        assert len(hits)>=loc['occurrence'],(cid,loc['path'],loc['needle'],len(hits))
        center=hits[loc['occurrence']-1]
        lo=max(0,center-loc['before']);hi=min(len(lines),center+loc['after']+1)
        ref=f'{rev}:{loc["path"]}:{center+1}'
        record=dict(side=loc['side'],role=loc['role'],ref=ref,line=center+1,excerpt_start=lo+1,excerpt_end=hi,sha256=sha256,path=loc['path'],revision=rev,needle=loc['needle'])
        locators.append(record)
        safe=redact(content).splitlines()
        excerpts.append(f'[{loc["side"]} {loc["role"]}] {ref}\n'+'\n'.join(f'{k+1}: {safe[k]}' for k in range(lo,hi)))
        assertions+=1
    (source_dir/(item_id+'.txt')).write_text('\n\n'.join(excerpts)+'\n')
    diff=redact(git(row['repo'],'diff','--no-ext-diff','--no-textconv','--unified=5',row['parent_commit'],row['fix_commit']).decode('utf-8','replace'))
    (ROOT/'review_evidence'/(cid+'.diff')).write_text(diff+'\n')
    diff_lines=diff.splitlines();current_path=None;hunk=None;hunk_start=None;matches=[]
    for k,line in enumerate(diff_lines,1):
        if line.startswith('diff --git '): current_path=line.split(' b/',1)[-1]
        elif line.startswith('@@ '):hunk=line;hunk_start=k
        elif current_path==a['hunk_path'] and a['hunk_needle'] in line:
            matches.append(dict(file=a['hunk_path'],header=hunk,evidence_file=f'review_evidence/{cid}.diff',hunk_line=hunk_start,changed_line=k))
    assert matches,(cid,'missing hunk')
    check={role:[v['ref'] for v in locators if v['side']=='parent' and v['role']==role] for role in ('contract','implementation','route')}
    if 'absence_check' in a:
        ac=a['absence_check'];content,digest=source(row['repo'],row['parent_commit'],ac['path'])
        assert ac['forbidden_parent'] not in content
        check['absence_scan']={'path':ac['path'],'revision':row['parent_commit'],'sha256':digest,'not_found':ac['forbidden_parent'],'all_path_headers':[{'line':n,'path':l.strip().rstrip(':')} for n,l in enumerate(content.splitlines(),1) if re.match(r'^  /[^ ]*:',l)]}
    evidence={'snapshots':[{k:v for k,v in loc.items() if k not in {'needle'}} for loc in locators],'diff_hunk':matches[0],'source_excerpt':f'source_evidence/{item_id}.txt'}
    note='⚠️ Static source/framework reasoning; no HTTP execution. Fix direction describes the scoped proposition, not all files in the commit.'
    if a['mismatch_type'].startswith('semantic_'):note+=' Semantic documentation mismatch; a permissive old schema may accept the wire payload.'
    if a['candidate_id']=='C0088':note+=' Terminal-LF acceptance follows Java anchored-regex find semantics; the contract constraint is descriptive.'
    if a['candidate_id']=='C0252':note+=' Existing implementation route; this is an omitted contract operation, not a new implementation endpoint.'
    result=dict(item_id=item_id,candidate_id=cid,repo=row['repo'],fix_commit=row['fix_commit'],parent_commit=row['parent_commit'],date=row['date'],operation=a['operation'],proposition=a['proposition'],truth_direction=a['truth_direction'],evidence=json.dumps(evidence,ensure_ascii=False,separators=(',',':')),proposition_check=json.dumps(check,ensure_ascii=False,separators=(',',':')),message_excerpt=row['message_excerpt'],confidence=a['confidence'],contract_kind=a['contract_kind'],mismatch_type=a['mismatch_type'],direction_judgment='static_only',runtime_traffic_observed='no',overlap_t41='yes' if a.get('overlap_t41') else 'no',inference_notes=note)
    accepted_rows.append(result)
    evidence_index.append(dict(item_id=item_id,candidate_id=cid,locators=locators,hunk=matches[0]))

candidate_rows=[]
statuses={'A':'accepted','R':'rejected','S':'deferred_static','T':'deferred_runtime'}
for r in pool:
    cid=r['candidate_id'];review=reviews.get(cid)
    status,category,reason=review if review else ('','not_reviewed','Not selected for manual review.')
    candidate_rows.append(dict(candidate_id=cid,repo=r['repo'],fix_commit=r['fix_commit'],parent_commit=r['parent_commit'],date=r['date'],message_excerpt=r['message_excerpt'],heuristic_score=r['score'],changed_files=r['changed_files'],surface_paths=r['surface_paths'],review_status=statuses.get(status,'not_reviewed'),review_category=category,review_reason=reason,selection_phase=('initial' if cid in selection['initial_ids'] else 'supplementary') if review else '',review_depth=('parent_fix_source_and_diff' if status=='A' else 'bounded_diff_screen') if review else '',review_evidence=f'review_evidence/{cid}.diff' if review else ''))

# Re-sanitize every persisted diff, including the original screening excerpts.
for path in (ROOT/'review_evidence').glob('*.diff'):path.write_text(redact(path.read_text())+'\n')
write_csv('candidates.csv',candidate_rows)
write_csv('accepted.csv',accepted_rows)
m['dump']('evidence_index.json',evidence_index)
summary=dict(pool_count=len(pool),reviewed_commits=len(reviews),initial_reviewed=len(selection['initial_ids']),supplementary_reviewed=len(selection['supplementary_ids']),accepted_items=len(accepted_rows),accepted_commits=len(accepted_rows),direction_counts=dict(Counter(r['truth_direction'] for r in accepted_rows)),confidence_counts=dict(Counter(str(r['confidence']) for r in accepted_rows)),contract_kind_counts=dict(Counter(r['contract_kind'] for r in accepted_rows)),review_status_counts=dict(Counter(r['review_status'] for r in candidate_rows)),accepted_commit_rate=len(accepted_rows)/len(reviews),initial_accepted=sum(x['candidate_id'] in selection['initial_ids'] for x in accepted_rows),supplementary_accepted=sum(x['candidate_id'] in selection['supplementary_ids'] for x in accepted_rows),static_direction_items=len(accepted_rows),essential_runtime_direction_items=0,overlap_t41_items=sum(r['overlap_t41']=='yes' for r in accepted_rows),per_repo=[])
summary.update(unique_repo_operation_pairs=len({(r['repo'],r['operation']) for r in accepted_rows}),semantic_documentation_items=sum(r['mismatch_type'].startswith('semantic_') for r in accepted_rows),descriptive_contract_items=sum(r['mismatch_type']=='descriptive_hash_constraint' for r in accepted_rows),confidence3_directions=dict(Counter(r['truth_direction'] for r in accepted_rows if r['confidence']==3)),non_t41_items=sum(r['overlap_t41']=='no' for r in accepted_rows),non_t41_directions=dict(Counter(r['truth_direction'] for r in accepted_rows if r['overlap_t41']=='no')))
for repo in sorted({r['repo'] for r in pool}):
    allr=[r for r in candidate_rows if r['repo']==repo];acc=[r for r in accepted_rows if r['repo']==repo]
    summary['per_repo'].append(dict(repo=repo,pool=len(allr),reviewed=sum(r['review_status']!='not_reviewed' for r in allr),accepted=len(acc),SPEC=sum(r['truth_direction']=='SPEC' for r in acc),IMPL=sum(r['truth_direction']=='IMPL' for r in acc),BOTH=sum(r['truth_direction']=='BOTH' for r in acc)))
m['dump']('summary.json',summary)
m['dump']('build_checks.json',dict(locator_assertions=assertions,accepted_rows=len(accepted_rows),reviewed_rows=len(reviews),all_passed=True,finished_utc=dt.datetime.now(dt.timezone.utc).isoformat()))
print(json.dumps(summary,indent=2))
