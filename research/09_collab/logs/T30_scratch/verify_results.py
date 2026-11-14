import csv,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path.cwd();D=ROOT/'09_collab/logs/T30_scratch';E=ROOT/'08_experiments/E5_codemut'
sys.path.insert(0,str(E));import summarise_e5 as s;import e5_common as c

def read(p):return list(csv.DictReader(p.open()))
def key(r):return tuple(r[x] for x in ('kind','site_id','seed','oracle'))
def complete(r):return r['validation_status'] in ('PASS','PASS_WITH_EXCLUSION') and r['analysis_status']=='COMPLETE'
def signal(r):return int(r['mutated_NEW'])+int(r['mutated_INCREASED'])>0
rows=read(E/'e5_summary.csv');head=read(D/'summary_HEAD.csv');before=read(D/'summary_before.csv')
old={key(r):r for r in head};now={key(r):r for r in rows};pre={key(r):r for r in before}
assert len(now)==len(rows)
metric_fields=s.METRICS+['expected_signal_observed','expected_signal_present_mutant','expected_signal_NEW','expected_signal_INCREASED','fresh_L1_NEW_mutated','signal_exceeds_noise']
changes=[];recoveries=[]
for r in rows:
    k=key(r)
    if k in old:
        if complete(r) and complete(old[k]):
            for field in metric_fields:
                if r[field]!=old[k][field]:changes.append(dict(zip(('kind','site_id','seed','oracle'),k))|{'field':field,'before':old[k][field],'after':r[field]})
        elif complete(r)!=complete(old[k]):recoveries.append({'key':k,'before_complete':complete(old[k]),'after_complete':complete(r)})
with (D/'metric_changes.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['kind','site_id','seed','oracle','field','before','after']);w.writeheader();w.writerows(changes)
site={}
for r in rows:
    if r['oracle']!='default':continue
    counts=site.setdefault(r['site_id'],{'pair':Counter(),'noise':Counter()})
    counts[r['kind']][r['validation_status']]+=1
saved=json.loads((D/'before.json').read_text())['validations'];restored=[]
for p,info in saved.items():
    if info['status'] not in ('PASS','PASS_WITH_EXCLUSION'):continue
    path=Path(p);record=c.load(path);kind='noise' if path.name.startswith('noise-') else 'pair'
    match=[r for r in rows if r['mut_dir']==str(path.parent) and r['kind']==kind and str(r['seed'])==str(record['seed'])]
    assert len(match)==2 and all(complete(r) for r in match),(p,match)
    restored.append(p)
golden=[r for r in rows if r['site_id']=='petstore-reject-valid-v3']
assert len(golden)==12 and all(complete(r) and r['analysis_tools_drift']=='none' for r in golden)
for r in golden:
    assert all(r[f]==pre[key(r)][f] for f in metric_fields),(key(r),r,pre[key(r)])
result={'rows':len(rows),'HEAD_rows':len(head),'common_rows':len(set(old)&set(now)), 'common_complete_rows':sum(complete(r) and complete(old[key(r)]) for r in rows if key(r) in old),
        'validation_counts':dict(Counter(r['validation_status'] for r in rows)), 'analysis_counts':dict(Counter(r['analysis_status'] for r in rows)),
        'sites_default':site,'totals':{},'drift':dict(Counter(r['analysis_tools_drift'] for r in rows)),
        'harness_drift':dict(Counter(r['analysis_harness_drift'] for r in rows)), 'metric_changed_rows':len({tuple(x[f] for f in ('kind','site_id','seed','oracle')) for x in changes}),
        'metric_changed_cells':len(changes),'restored_saved_pass_reports':len(restored),'golden_rows_unchanged':len(golden),'status_changes_vs_HEAD':recoveries,
        'errors':[dict((f,r[f]) for f in ('kind','site_id','seed','oracle','validation_status','error')) for r in rows if r['error']]}
for oracle in ('default','sut'):
    for kind in ('pair','noise'):
        group=[r for r in rows if r['oracle']==oracle and r['kind']==kind and complete(r)]
        result['totals'][oracle+'/'+kind]={'n':len(group),'signal':sum(signal(r) for r in group),'expected_kind':sum(r['expected_signal_observed']=='True' for r in group),'exceeds_noise':sum(r['signal_exceeds_noise']=='True' for r in group),'noise_false':sum(r['signal_exceeds_noise']=='False' for r in group),'noise_unknown':sum(r['signal_exceeds_noise']=='UNKNOWN' for r in group)}
identity=s.analysis_identity();(D/'analysis_identity.json').write_text(json.dumps(identity,indent=2)+'\n')
(D/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
