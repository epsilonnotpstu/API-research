"""Run only the authorized repository tool and retain exact process artifacts."""
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
TOOL='08_experiments/tools/intent_evidence.py'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()

def main():
 items=json.loads((OUT/'working_evidence.json').read_text())
 # Spec-side candidates on 5xx need review too; do not use the primary R1
 # exemption to bypass an intent-dependent second defect.
 dual_candidates={'M002','M013','B094','B040','B098','B087'}
 summary=[]
 for r in items:
  ident=r['item_id']; base=OUT/'search'/ident
  if base.with_suffix('.manifest.json').exists():
   raise SystemExit('Refusing to overwrite immutable search '+ident)
  mandatory=not (r['status']=='500' and ident not in dual_candidates) and ident!='P035'
  rule='§11.4.1 / §12.1 Q2: unresolved intent or intent-dependent spec-side candidate'
  if not mandatory:
   rule='§11.4.1 exemption; codebook §9.3 malformed documented JSON' if ident=='P035' else '§11.4.1 exemption; R1 / §9.3 non-gateway 500 primary IMPL; no separately established intent-dependent SPEC message'
  spec_ptr='/paths/'+r['template'].replace('~','~0').replace('/','~1')+'/'+r['method'].lower()
  manifest={'item_id':ident,'mandatory':mandatory,'gate_rule':rule,
   'message':r['message'] or r['kind'],'violation_path':r['pointer'],
   'method':r['method'],'template':r['template'],'observed_status':int(r['status']),
   'field_direction': 'photoUrls missing in one response array member' if ident=='P013' else
       ('response status field outside enum; same value accepted in unconstrained request query' if ident=='P018' else 'not a response-field query'),
   'representative_exchange_locator':r['exchanges_path']+':'+str(r['exchange_lines'][0]),
   'all_exchange_lines':r['exchange_lines'], 'source_root':r['source_root'],
   'source_hash_manifest':'09_collab/logs/T36_scratch/protected_before.json',
   'spec_path':r['spec'],'spec_locator':r['spec']+'#'+spec_ptr,
   'spec_sha256':sha(r['spec']),'tool_path':TOOL,'tool_sha256':sha(TOOL),
   'scenario_review_locator':'08_experiments/E2_labelling/pilot_v06/review/'+ident+'.json',
   'reused':False,'started_utc':now()}
  argv=['/usr/bin/python3','-I','-B',TOOL,r['source_root'],r['spec'],
        '--method',r['method'],'--path',r['template'],'--status',r['status']]
  if ident in {'P013','P018'}:argv+=['--field','photoUrls' if ident=='P013' else 'status']
  argv+=['--json']; manifest['argv']=argv if mandatory else []
  start=time.monotonic()
  if mandatory:
   with base.with_suffix('.json').open('wb') as stdout,base.with_suffix('.stderr').open('wb') as stderr:
    process=subprocess.run(argv,cwd=ROOT,stdout=stdout,stderr=stderr,check=False)
   code=process.returncode
   raw=json.loads(base.with_suffix('.json').read_text()) if code==0 else {}
   manifest.update({k:raw.get(k) for k in ['scan','history','warnings']})
   manifest['raw_verdict']=raw.get('independent_evidence','NA')
  else:
   code=None;raw={}
   base.with_suffix('.json').write_text(json.dumps({'not_run':True,'reason':rule})+'\n')
   base.with_suffix('.stderr').write_text('')
   manifest.update({'scan':None,'history':None,'warnings':[], 'raw_verdict':'NA'})
  manifest.update({'exit_code':code,'elapsed_seconds':time.monotonic()-start,'finished_utc':now(),
    'raw_sha256':hashlib.sha256(base.with_suffix('.json').read_bytes()).hexdigest()})
  base.with_suffix('.exitcode').write_text('not_run\n' if code is None else str(code)+'\n')
  base.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  result={'item_id':ident,'mandatory':mandatory,'exit_code':code,
          'seconds':round(manifest['elapsed_seconds'],3),'verdict':manifest['raw_verdict'],
          'hits':len(raw.get('hits',[])),'scan':manifest['scan'],'history':manifest['history']}
  summary.append(result);print(json.dumps(result),flush=True)
 (OUT/'search_summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':main()
