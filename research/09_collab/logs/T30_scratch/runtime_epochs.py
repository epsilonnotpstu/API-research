import json,sys
from collections import Counter
from pathlib import Path
ROOT=Path.cwd();D=ROOT/'09_collab/logs/T30_scratch';E=ROOT/'08_experiments/E5_codemut'
sys.path.insert(0,str(E));import e5_common as c
identity=json.loads((D/'analysis_identity_initial.json').read_text());epochs={}
for p in sorted(E.glob('work/*/*pair-validation-s*.json')):
    report=c.load(p)
    if report['status'] not in ('PASS','PASS_WITH_EXCLUSION'):continue
    meta=c.load(Path(report['control_run'])/'run.json');snapshot=c.runtime_snapshots(meta);digest=c.canonical(snapshot)
    record=epochs.setdefault(digest,{'snapshot':snapshot,'comparisons':[], 'analysis_tools_drift':'none' if snapshot['tools']==identity['tools'] else 'changed','analysis_harness_drift':'none' if snapshot['harness']==identity['harness'] else 'changed'})
    record['comparisons'].append(str(p))
(D/'runtime_epochs.json').write_text(json.dumps(epochs,indent=2)+'\n')
print(json.dumps({k:{'comparisons':len(v['comparisons']),'tools':len(v['snapshot']['tools']),'harness_files':len(v['snapshot']['harness']),'analysis_tools_drift':v['analysis_tools_drift'],'analysis_harness_drift':v['analysis_harness_drift']} for k,v in epochs.items()},indent=2))
