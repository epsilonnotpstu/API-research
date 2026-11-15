#!/usr/bin/python3
"""Extend T42 build_tables/leakage_audit with frozen-depth review and parent-contract gates."""
from collections import Counter
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT=Path(__file__).resolve().parent
m=runpy.run_path(str(ROOT/'t43_mine.py'))
d=runpy.run_path(str(ROOT/'t43_curation.py'))
definitions=runpy.run_path(str(ROOT/'t43_accepted.py'))['ACCEPTED']
BASE=ROOT.parent
pool=json.loads((ROOT/'candidate_pool.json').read_text())
bykey={(r['repo'],r['rank']):r for r in pool}
reviews={}
for repo,notes in d['NOTES'].items():
    assert len(notes)==20
    for rank,note in enumerate(notes,1):reviews[(repo,rank)]=note
reviews.update(d['SUPPLEMENTS'])
assert len(reviews)==251
assert set(d['NOTES'])==set(m['REPOS'])

def dump(name,value):m['dump'](name,value)
def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

cache={};assertions=[]
def check(condition,label):
    assert condition,label
    assertions.append(label)
for frozen_path,digest in json.loads((ROOT/'input_freeze.json').read_text()).items():
    check(hashlib.sha256(Path(frozen_path).read_bytes()).hexdigest()==digest,'pinned input '+frozen_path)
def source(repo,rev,path):
    key=(repo,rev,path)
    if key not in cache:
        raw=m['git'](repo,'show',rev+':'+path)
        cache[key]=(raw.decode('utf-8','replace'),hashlib.sha256(raw).hexdigest())
    return cache[key]

(ROOT/'source_evidence').mkdir(exist_ok=True)
(ROOT/'review_evidence').mkdir(exist_ok=True)
for key in reviews:
    r=bykey[key]
    target=ROOT/'review_evidence'/(r['candidate_id']+'.diff')
    # Reviewed diff snapshots are sanitized again when regenerated.
    raw=m['git'](r['repo'],'diff','--no-ext-diff','--no-textconv','--unified=3',r['parent_commit'],r['fix_commit']).decode('utf-8','replace')
    target.write_text(m['redact'](raw)+'\n')

accepted=[];index=[]
stars={r[0]:r[1] for r in m['META']}
for n,a in enumerate(definitions,1):
    r=bykey[(a['repo'],a['rank'])];cid=r['candidate_id'];iid=f'T43R{n:03}'
    reviews[(a['repo'],a['rank'])]='A '+a['fix_family']+'; parent contract, implementation, route and scoped patch reviewed.'
    check(re.match(r'^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) \S+: contract says .+; implementation does .+$',a['proposition']),iid+': neutral template')
    check(not re.search(r'\b(fix|later|changed|corrected|updated|developer)\b',a['proposition'],re.I),iid+': no future cue')
    actual=m['git'](r['repo'],'log','-1','--format=%P%n%cs',r['fix_commit']).decode().splitlines()
    check(actual==[r['parent_commit'],r['date']],iid+': real single parent and date')
    locators=[];excerpts=[]
    for loc in a['locators']:
        rev=r['parent_commit'] if loc['side']=='parent' else r['fix_commit']
        raw,digest=source(r['repo'],rev,loc['path']);lines=raw.splitlines()
        hits=[j for j,line in enumerate(lines) if loc['needle'] in line]
        check(len(hits)>=loc['occurrence'],iid+': locator '+loc['path']+' '+loc['side'])
        center=hits[loc['occurrence']-1];lo=max(0,center-loc['before']);hi=min(len(lines),center+loc['after']+1)
        safe=m['redact'](raw).splitlines()
        check(len(safe)==len(lines),iid+': redaction preserves source line numbers')
        rec=dict(side=loc['side'],role=loc['role'],ref=f'{rev}:{loc["path"]}:{center+1}',path=loc['path'],revision=rev,line=center+1,excerpt_start=lo+1,excerpt_end=hi,sha256=digest)
        locators.append(rec)
        excerpts.append(f'[{loc["side"]} {loc["role"]}] {rec["ref"]}\n'+'\n'.join(f'{j+1}: {safe[j]}' for j in range(lo,hi)))
    (ROOT/'source_evidence'/(iid+'.txt')).write_text('\n\n'.join(excerpts)+'\n')
    propcheck={role:[x['ref'] for x in locators if x['side']=='parent' and x['role']==role] for role in ('contract','implementation','route')}
    check(all(propcheck.values()),iid+': all parent-only proposition roles')
    contract_gate=[]
    if a['truth_direction']=='IMPL':
        # Parent obligations must be from a checked-in spec or Swagger/OpenAPI annotations.
        parents=[x for x in locators if x['side']=='parent' and x['role']=='contract']
        check(bool(parents),iid+': existing parent contract')
        for x in parents:
            old,_=source(r['repo'],r['parent_commit'],x['path'])
            new,_=source(r['repo'],r['fix_commit'],x['path'])
            if Path(x['path']).suffix in {'.json','.yaml','.yml'}:
                check(old==new,iid+': complete independent spec unchanged')
                status='whole_contract_blob_identical'
            else:
                oldpart='\n'.join(old.splitlines()[x['excerpt_start']-1:x['excerpt_end']])
                check(oldpart in new,iid+': annotation contract block unchanged')
                check('@ApiResponse' in oldpart or '@OpenApiResponse' in oldpart,iid+': service contract annotation')
                status='scoped_annotation_block_identical'
            contract_gate.append(dict(path=x['path'],status=status,parent_sha256=x['sha256']))
    else:
        # SPEC acceptance has identical implementation excerpts in parent and fix.
        oldloc=next(x for x in locators if x['side']=='parent' and x['role']=='implementation')
        old,_=source(r['repo'],r['parent_commit'],oldloc['path']);new,_=source(r['repo'],r['fix_commit'],oldloc['path'])
        part='\n'.join(old.splitlines()[oldloc['excerpt_start']-1:oldloc['excerpt_end']])
        check(part in new,iid+': scoped SPEC implementation unchanged')
    diff=(ROOT/'review_evidence'/(cid+'.diff')).read_text();path=None;hunk=None;hunkline=None;found=None
    for j,line in enumerate(diff.splitlines(),1):
        if line.startswith('diff --git '):path=line.split(' b/',1)[-1]
        elif line.startswith('@@ '):hunk=line;hunkline=j
        elif path==a['hunk_path'] and a['hunk_needle'] in line:
            found=dict(file=path,header=hunk,evidence_file=f't43/review_evidence/{cid}.diff',hunk_line=hunkline,changed_line=j);break
    check(bool(found),iid+': exact changed hunk')
    evidence=dict(snapshots=locators,diff_hunk=found,source_excerpt=f't43/source_evidence/{iid}.txt',contract_gate=contract_gate)
    note='⚠️ Static source/framework reasoning; no runtime traffic or external service execution. Direction is scoped to this proposition.'
    if a.get('notes'):note+=' '+a['notes']
    accepted.append(dict(item_id=iid,candidate_id=cid,repo=r['repo'],fix_commit=r['fix_commit'],parent_commit=r['parent_commit'],date=r['date'],operation=a['operation'],proposition=a['proposition'],truth_direction=a['truth_direction'],evidence=json.dumps(evidence,ensure_ascii=False,separators=(',',':')),proposition_check=json.dumps(propcheck,ensure_ascii=False,separators=(',',':')),message_excerpt=r['message_excerpt'],confidence=a['confidence'],contract_kind=a['contract_kind'],mismatch_type=a['mismatch_type'],direction_judgment='static_only',runtime_traffic_observed='no',overlap_t41='no',inference_notes=note,fix_family=a['fix_family'],stars=stars[r['repo']],popularity_source='t43_repo_meta.csv; supervisor-provided GitHub API metadata 2026-11-15',source_task='T43',parent_future_reference='pending',parent_issue_reference='pending'))
    index.append(dict(item_id=iid,candidate_id=cid,locators=locators,contract_gate=contract_gate,hunk=found))

# Reuse the T42 release-note audit, extending path coverage to issue text and its identifiers.
def leakage(rows):
    records=[]
    for r in rows:
        paths=m['git'](r['repo'],'ls-tree','-r','--name-only',r['parent_commit']).decode().splitlines()
        files=[];hits=[];issue_hits=[]
        issues=set(re.findall(r'#\d+\b|\b[A-Z][A-Z0-9]+-\d+\b',r['message_excerpt']))
        for path in paths:
            ext=Path(path).suffix.lower()
            if ext not in {'.md','.txt','.rst','.adoc','.html'}:
                if not re.search(r'(change.?log|release|history|news|changes|readme|issues?)',path,re.I):continue
                if ext not in {'','.json','.yaml','.yml'}:continue
            raw,digest=source(r['repo'],r['parent_commit'],path)
            files.append(dict(path=path,sha256=digest,lines=len(raw.splitlines())))
            for line_no,line in enumerate(raw.splitlines(),1):
                for kind,needle in [('full_fix_sha',r['fix_commit']),('short_fix_sha',r['fix_commit'][:7]),('exact_subject',r['message_excerpt'])]:
                    if needle and needle.casefold() in line.casefold():hits.append(dict(path=path,line=line_no,match_kind=kind))
                for issue in issues:
                    pattern=(r'(?:#|/issues/|/pull/)'+re.escape(issue[1:])+r'\b') if issue.startswith('#') else r'\b'+re.escape(issue)+r'\b'
                    if re.search(pattern,line):issue_hits.append(dict(path=path,line=line_no,issue_identifier=issue))
        records.append(dict(item_id=r['item_id'],repo=r['repo'],source_task=r.get('source_task','T42'),parent_commit=r['parent_commit'],files_scanned=files,hits=hits,issue_identifier_hits=issue_hits))
    return records

t42=list(csv.DictReader((BASE/'accepted.csv').open()))
records=leakage(t42+accepted)
leakby={x['item_id']:x for x in records}
for r in accepted:
    scan=leakby[r['item_id']]
    r['parent_future_reference']='yes_review_required' if scan['hits'] else 'no_exact_hit'
    r['parent_issue_reference']='yes_review_required' if scan['issue_identifier_hits'] else 'no_exact_hit'
write_csv(ROOT/'accepted.csv',accepted)

candidate_rows=[]
for r in pool:
    key=(r['repo'],r['rank']);note=reviews.get(key);code=note[0] if note else ''
    candidate_rows.append(dict(candidate_id=r['candidate_id'],repo=r['repo'],rank=r['rank'],fix_commit=r['fix_commit'],parent_commit=r['parent_commit'],date=r['date'],message_excerpt=r['message_excerpt'],heuristic_score=r['score'],changed_files=r['changed_files'],surface_paths=r['surface_paths'],coarse_contract_paths_changed=' | '.join(r['contract_paths_changed']),stars=stars[r['repo']],review_status={'A':'accepted','R':'rejected','S':'deferred_static'}.get(code,'not_reviewed'),review_reason=note[2:] if note else 'Outside frozen top-20 depth and named adaptive supplement; not manually reviewed.',selection_phase=('top20' if r['rank']<=20 else 'targeted_supplement') if note else '',review_depth=('parent_fix_source_and_diff' if code=='A' else 'bounded_production_diff_screen') if note else '',review_evidence=f't43/review_evidence/{r["candidate_id"]}.diff' if note else ''))
write_csv(ROOT/'candidates.csv',candidate_rows)
dump('evidence_index.json',index)

# Keep all T42 columns/values intact; add explicit source/family/evidence roots in the union copy.
combined=[];keys=set();duplicates=[]
fields=list(t42[0])+[k for k in accepted[0] if k not in t42[0]]+['evidence_root','dedup_key']
for original,task in [(x,'T42') for x in t42]+[(x,'T43') for x in accepted]:
    row={k:original.get(k,'') for k in fields};row['source_task']=task
    row['fix_family']=row['fix_family'] or row['mismatch_type']
    row['evidence_root']='08_experiments/E6_realfix' if task=='T42' else '08_experiments/E6_realfix'
    row['stars']=row['stars'] or 'unavailable_offline_T42'
    if task=='T42':
        scan=leakby[row['item_id']]
        row['parent_future_reference']='yes_review_required' if scan['hits'] else 'no_exact_hit'
        row['parent_issue_reference']='yes_review_required' if scan['issue_identifier_hits'] else 'no_exact_hit'
    key=(row['repo'],row['operation'],row['fix_family']);row['dedup_key']=json.dumps(key,separators=(',',':'))
    if key in keys:duplicates.append(dict(item_id=row['item_id'],key=key));continue
    keys.add(key);combined.append(row)
check(sum(x['source_task']=='T42' for x in combined)==len(t42),'T42 accepted set preserved in union')
check(len({(r['repo'],r['fix_commit']) for r in accepted})==len(accepted),'one T43 proposition per fix commit')
write_csv(BASE/'combined_accepted.csv',combined)
dump('leakage_audit.json',dict(scope='All parent tracked md/txt/rst/adoc/html, plus extensionless/JSON/YAML changelog/release/history/news/changes/readme/issue paths; literal full SHA, 7-char SHA and sanitized subject; numeric issue/PR and JIRA-style identifiers separately flagged',items=records,total_files_scanned=sum(len(x['files_scanned']) for x in records),total_exact_reference_hits=sum(len(x['hits']) for x in records),total_issue_identifier_hits=sum(len(x['issue_identifier_hits']) for x in records),limits=['No external issue text was fetched. Only issue material already tracked in the parent was available.','No semantic/paraphrase, all-source, branch-independent or package-level blindness guarantee.','An issue-identifier occurrence is a potential preannouncement pointer, not proof of future fix leakage.']))

summary=dict(pool_count=len(pool),reviewed_commits=len(reviews),top20_reviewed=240,supplementary_reviewed=len(reviews)-240,accepted_items=len(accepted),direction_counts=dict(Counter(r['truth_direction'] for r in accepted)),confidence_counts=dict(Counter(str(r['confidence']) for r in accepted)),confidence3_directions=dict(Counter(r['truth_direction'] for r in accepted if r['confidence']==3)),review_status_counts=dict(Counter(r['review_status'] for r in candidate_rows)),combined_items=len(combined),combined_directions=dict(Counter(r['truth_direction'] for r in combined)),deduplication=dict(key=['repo','operation','fix_family'],dropped=duplicates),stopping_reason='All 12 frozen ranked pools exhausted to depth 20, plus 11 named adaptive supplements; combined IMPL target 16 not reached.',target_combined_IMPL=16,target_met=False,per_repo=[],runtime_traffic_observed=False,essential_runtime_experiments=0,leakage=dict(files_scanned=sum(len(x['files_scanned']) for x in records),exact_reference_hits=sum(len(x['hits']) for x in records),issue_identifier_hits=sum(len(x['issue_identifier_hits']) for x in records)))
summary.update(accepted_commit_rate=len(accepted)/len(reviews),top20_accepted=sum(x['rank']<=20 for x in definitions),supplementary_accepted=sum(x['rank']>20 for x in definitions),accepted_repos=len({r['repo'] for r in accepted}),unique_repo_operation_pairs=len({(r['repo'],r['operation']) for r in accepted}),combined_confidence3_directions=dict(Counter(r['truth_direction'] for r in combined if str(r['confidence'])=='3')),combined_IMPL_deficit=16-sum(r['truth_direction']=='IMPL' for r in combined),unreviewed_candidates=sum(r['review_status']=='not_reviewed' for r in candidate_rows))
for repo in m['REPOS']:
    rows=[r for r in candidate_rows if r['repo']==repo];acc=[r for r in accepted if r['repo']==repo]
    reviewed=[r['rank'] for r in rows if r['review_status']!='not_reviewed']
    check(all(n in reviewed for n in range(1,21)),repo+': contiguous top20 exhausted')
    summary['per_repo'].append(dict(repo=repo,stars=stars[repo],pool=len(rows),reviewed=len(reviewed),contiguous_review_depth=20,supplement_ranks=[n for n in reviewed if n>20],accepted=len(acc),directions=dict(Counter(r['truth_direction'] for r in acc))))
dump('selection.json',dict(rule='Frozen per-repo score descending, full SHA ascending; contiguous ranks 1-20. Adaptive supplements selected by focused conformance titles after bounded screens.',reviewed_ids=[bykey[k]['candidate_id'] for k in reviews],supplement_keys=[list(k) for k in d['SUPPLEMENTS']]))
dump('summary.json',summary)
frozen=json.loads((BASE.parents[1]/'09_collab/logs/T43_scratch/freeze.json').read_text())
for path,digest in frozen.items():check(hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,'T42 frozen '+path)
privacy=[]
for path in list(ROOT.rglob('*.csv'))+list((ROOT/'source_evidence').glob('*.txt'))+list((ROOT/'review_evidence').glob('*.diff'))+[BASE/'combined_accepted.csv']:
    text=path.read_text()
    for name,pattern in [('email',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'),('attribution_trailer',r'(?im)^[+\- ]*(?:Signed-off-by|Co-authored-by|Author|Committer|Reviewed-by):'),('token',r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|AKIA[A-Z0-9]{16})\b')]:
        if re.search(pattern,text):privacy.append(dict(path=str(path),kind=name))
check(not privacy,'delivered text privacy patterns')
dump('verification.json',dict(passed=True,assertions=len(assertions),checks=assertions,privacy_findings=privacy,T42_frozen_files=len(frozen),completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),limits=['Mechanical locators, hashes and gates do not prove the manual semantic judgment.','Confidence-2 rows retain framework/descriptive/success-path inference; no runtime witness.']))
print(json.dumps({k:summary[k] for k in ['reviewed_commits','accepted_items','direction_counts','combined_items','combined_directions','target_met','leakage']},indent=2))

if __name__=='__main__':pass
