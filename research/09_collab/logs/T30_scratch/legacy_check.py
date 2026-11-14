"""Explain metric differences using the checker's documented legacy switch."""
import csv,json,sys
from pathlib import Path
ROOT=Path.cwd();D=ROOT/'09_collab/logs/T30_scratch';E=ROOT/'08_experiments/E5_codemut'
sys.path.insert(0,str(E));import summarise_e5 as s;import e5_common as c
load=s.load_checker
def legacy():
    module=load();module.INT_FORMATS=False;return module
s.load_checker=legacy
fields=s.METRICS+['expected_signal_observed','expected_signal_present_mutant','expected_signal_NEW','expected_signal_INCREASED','fresh_L1_NEW_mutated']
results=[]
for row in csv.DictReader((D/'summary_HEAD.csv').open()):
    if row['analysis_status']!='COMPLETE' or row['validation_status'] not in ('PASS','PASS_WITH_EXCLUSION'):continue
    mut=Path(row['mut_dir']);kind=row['kind'];prefix,second=c.layout(kind);seed=int(row['seed'])
    members={r['role']:Path(r['run_dir']) for r in c.ledger(mut/(prefix+'runs.tsv'),kind) if int(r['seed'])==seed}
    report=c.load(mut/f'{prefix}pair-validation-s{seed}.json');manifest=c.load(mut/'manifest.json')
    reject='400,406,422' if manifest['sut']=='market' and row['oracle']=='sut' else '400,422'
    metrics=s.metrics(s.current_attribution(members,manifest,f'http://sut-{manifest["sut"]}:8080',reject,c.excluded_operations(report),kind),manifest,c.excluded_operations(report))
    diff={f:{'HEAD':row[f],'legacy_now':str(metrics[f])} for f in fields if row[f]!=str(metrics[f])}
    results.append({'kind':kind,'site_id':row['site_id'],'seed':seed,'oracle':row['oracle'],'differences':diff})
(D/'legacy_check.json').write_text(json.dumps({'rows':len(results),'rows_matching_HEAD':sum(not r['differences'] for r in results),'results':results},indent=2)+'\n')
print('legacy rows',len(results),'matching HEAD',sum(not r['differences'] for r in results),flush=True)
