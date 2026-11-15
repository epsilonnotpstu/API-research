"""Check the delivered pilot's audit links, freeze chronology and source integrity."""
import csv
import hashlib
import json
import random
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
DEST=ROOT/'08_experiments/E2_labelling/pilot_v06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=0
def check(ok,message):
 global checks
 checks+=1
 if not ok:raise AssertionError(message)

def pointer(document,parts):
 for part in parts:
  part=part.replace('~1','/').replace('~0','~')
  document=document[int(part)] if isinstance(document,list) else document[part]
 return document

def locator(value):
 if '#' in value:
  file,ptr=value.split('#',1);p=ROOT/file
  check(p.is_file(),'missing locator file '+file)
  pointer(json.loads(p.read_text()),ptr.lstrip('/').split('/'))
  check(True,'pointer resolved');return
 file,part=value.rsplit(':',1);p=ROOT/file
 check(p.is_file(),'missing locator file '+file)
 if part.startswith('$'):
  d=json.loads(p.read_text());path=part[1:]
  for quoted,key,index in re.findall(r'\."([^"]+)"|\.([A-Za-z_][A-Za-z_0-9-]*)|\[(\d+)\]',path):
   d=d[int(index)] if index else d[quoted or key]
  check(True,'json path resolved')
 else:
  m=re.fullmatch(r'(\d+)(?:-(\d+))?',part)
  check(bool(m),'invalid locator grammar '+value)
  start=int(m[1]);end=int(m[2] or start)
  count=sum(1 for _ in p.open(errors='replace'))
  check(1<=start<=end<=count,'out of range locator '+value)

def main():
 sample=json.loads((OUT/'sample.json').read_text())
 final=list(csv.DictReader((ROOT/'08_experiments/E2_labelling/final_labels_baseline_s1.csv').open()))
 rng=random.Random(20261115);expected=[]
 for label,n in zip(['SPEC','SPEC_PARTIAL','UNDECIDABLE','BOTH','IMPL'],[6,4,6,6,6]):
  pool=sorted([r for r in final if r['final_L1']==label and r['item_id'] not in {'B065','M003','M005','M007','M012'}],key=lambda r:r['item_id'])
  draw=rng.sample(pool,n)
  candidates=[r for r in pool if r['sut']!='scout-api']
  if candidates and all(r['sut']=='scout-api' for r in draw):draw[-1]=rng.sample(candidates,1)[0]
  expected += [r['item_id'] for r in draw]
 check(expected==[r['item_id'] for r in sample['items']],'sample reproducibility')
 check(all(r['final_L1']!='TEST' for r in final if r['item_id'] in expected),'TEST exemption')
 working=list(csv.DictReader((OUT/'working_sheet.csv').open()))
 check(not {'final_L1','A_L1','B_L1','note'}&set(working[0]),'hidden columns')
 frozen=json.loads((OUT/'decision_freeze.json').read_text())
 joined=json.loads((OUT/'comparison_summary.json').read_text())
 amendment_path=DEST/'review_amendments/C002.json'
 amendment=json.loads(amendment_path.read_text())
 check(sha(amendment_path)==joined['annotation_amendment_sha256'],'amendment immutable')
 check(set(amendment['csv_annotation_changes'])=={'rationale','evidence_locators','intent_review_locator'},'annotation-only changes')
 check(datetime.fromisoformat(sample['created_utc'])<datetime.fromisoformat(frozen['frozen_utc'])<datetime.fromisoformat(joined['joined_utc']),'chronology')
 check(sha(OUT/'decisions_frozen.csv')==frozen['decisions_sha256'],'decision freeze')
 check(sha(DEST/'T36_pilot_labels.csv')==joined['labels_sha256'],'pilot export hash')
 rows=list(csv.DictReader((DEST/'T36_pilot_labels.csv').open()))
 original=list(csv.DictReader((OUT/'decisions_frozen.csv').open()))
 check(len(rows)==len(original)==28,'coverage')
 finalmap={r['item_id']:r for r in final}
 totalhits=0;accepted=0;manuals=0;unresolved=0;times=[]
 for row,before in zip(rows,original):
  ident=row['item_id']
  allowed=amendment['csv_annotation_changes'] if ident=='C002' else {}
  check(all(row[k]==v if k not in allowed else
            (v==allowed[k]['before'] and row[k]==allowed[k]['after'])
            for k,v in before.items()),'unrecorded decision change after join '+ident)
  check(row['L1']==before['L1'],'L1 changed after join '+ident)
  check(row['final_L1_joined']==finalmap[ident]['final_L1'],'final join '+ident)
  check(row['agrees_with_final']==str(row['L1']==row['final_L1_joined']).lower(),'agreement '+ident)
  check(row['L1']!='BOTH','labeller BOTH authority '+ident)
  for field in ['evidence_locators','intent_search_locator','intent_review_locator']:
   check(bool(row[field]),'missing '+field)
   for loc in row[field].split(';'):locator(loc)
  path='08_experiments/E2_labelling/pilot_v06/review/'+ident+'.json'
  check(sha(ROOT/path)==frozen['review_sha256'][path],'review immutable '+ident)
  rev=json.loads((ROOT/path).read_text());raw=json.loads((OUT/'search'/(ident+'.json')).read_text())
  manifest=json.loads((OUT/'search'/(ident+'.manifest.json')).read_text())
  check(sha(OUT/'search'/(ident+'.json'))==manifest['raw_sha256'],'raw immutable '+ident)
  check(sha(ROOT/manifest['spec_path'])==manifest['spec_sha256'],'spec unchanged '+ident)
  check(sha(ROOT/manifest['tool_path'])==manifest['tool_sha256'],'intent tool unchanged '+ident)
  check(datetime.fromisoformat(sample['created_utc'])<datetime.fromisoformat(manifest['started_utc']),'sample before search '+ident)
  check(len(rev['hits'])==len(raw.get('hits',[])),'hit completeness '+ident)
  check([h['hit_index'] for h in rev['hits']]==list(range(len(raw.get('hits',[])))),'hit indices '+ident)
  for h in rev['hits']:
   check(h['disposition'] in {'accept','reject','context','unresolved'},'hit disposition')
   check(bool(h['reason']) and len(h['independence_checklist'])==5,'five-part checklist')
   locator(h['raw_hit_locator']);locator(h['source_locator']);locator(h['reviewed_context_locator'])
   if 'patch_locator' in h:locator(h['patch_locator'])
   check(sha(ROOT/(rev['source_root']+'/'+raw['hits'][h['hit_index']]['file']))==h['source_file_sha256'],'hit file integrity')
   if h['disposition']=='accept':
    check(all(v['passes'] for v in h['independence_checklist'].values()),'accepted independence gates')
   accepted+=h['disposition']=='accept';unresolved+=h['disposition']=='unresolved'
  totalhits+=len(rev['hits'])
  manual_records=rev['manual_additions']+(amendment['manual_additions'] if ident=='C002' else [])
  for h in manual_records:
   locator(h['locator']);check(len(h['independence_checklist'])==5,'manual five-part checklist')
   if h['disposition']=='accept':check(all(v['passes'] for v in h['independence_checklist'].values()),'accepted manual gates')
   unresolved+=h['disposition']=='unresolved'
  manuals+=len(manual_records)
  locator(rev['source_revision_locator']);locator(rev['coverage_inventory_locator'])
  if row['intent_search_status']=='complete':
   check(manifest['exit_code']==0 and manifest['scan']['complete'],'complete search '+ident)
   check(rev['manual_fallback']['performed'],'fallback coverage '+ident)
   check(manifest['argv'][:4]==['/usr/bin/python3','-I','-B','08_experiments/tools/intent_evidence.py'],'authorized CLI '+ident)
   times.append(manifest['elapsed_seconds'])
  elif row['intent_search_status']=='not_run':
   check(not manifest['mandatory'] and manifest['exit_code'] is None,'exempt search '+ident)
   check(bool(manifest['gate_rule']) and row['intent_search_verdict']=='NA','exemption rule '+ident)
  message_records=amendment['message_decisions'] if ident=='C002' else rev['decision']['message_decisions']
  for md in message_records:
   for n in md.get('exchange_lines',[]):check(n in rev['target']['all_exchange_lines'],'message exchange membership '+ident)
  for x in rev['manual_additions']:
   if x.get('tool_miss'):check(x['disposition']=='accept','tool miss requires accepted target evidence')
 check(totalhits==152,'raw hit total')
 protected=json.loads((OUT/'protected_before.json').read_text())
 changed=[p for p,h in protected.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
 # Concurrent T37 may edit its own files; report any drift rather than concealing it.
 # Never open forbidden material for secret scanning. Derive the known demo
 # value internally from explicitly permitted source and report counts only.
 market=ROOT/'08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market'
 tokens=set()
 for p in [market/'README_RU.md',market/'market-web/src/main/resources/templates/rest.html']:
  tokens.update(re.findall(r'(?i)Basic[ \t]+([A-Za-z0-9+/=]{24,})',p.read_text()))
 check(bool(tokens),'internal secret pattern availability')
 credential_hits=[]
 for parent in [OUT,DEST]:
  for p in parent.rglob('*'):
   if p.is_file():
    b=p.read_bytes()
    if any(t.encode() in b for t in tokens):credential_hits.append(str(p.relative_to(ROOT)))
 check(not credential_hits,'known demo credential retained in task artifacts')
 elapsed=(datetime.fromisoformat(frozen['frozen_utc'])-datetime.fromisoformat(sample['created_utc'])).total_seconds()
 result={'verified_utc':datetime.now(timezone.utc).isoformat(),'assertions_passed':checks,
  'items':len(rows),'raw_hits_reviewed':totalhits,'raw_hits_accepted':accepted,
  'manual_records':manuals,'unresolved_manual_policy_records':unresolved,
  'post_join_annotation_amendment':{'item_id':'C002','L1_unchanged':True,
    'original_review_immutable':sha(DEST/'review/C002.json')==amendment['original_review_sha256'],
    'counts':[m['count'] for m in amendment['message_decisions']]},
  'all_decisions_and_reviews_immutable':True,'all_locators_resolve':True,
  'protected_files':len(protected),'protected_changed':changed,
  'known_demo_credential_hits_in_deliverables':credential_hits,
  'search_seconds':{'sum':sum(times),'median':statistics.median(times),'min':min(times),'max':max(times)},
  'sample_to_decision_freeze_seconds':elapsed,'shared_wall_seconds_per_item':elapsed/28,
  'timing_limit':'Shared wall interval includes setup, tools, source-family review, incident handling and output writing; it is not measured per-item active reasoning time.',
  'incidents':'09_collab/logs/T36_scratch/incident.json',
  'boundary':'No SUT/external code execution/network. Accidental unscoped rg did scan forbidden paths; discarded without E5 content being displayed to model. No clean-blinding claim.'}
 (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))

if __name__=='__main__':main()
