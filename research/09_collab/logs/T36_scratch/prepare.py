"""Prepare label-hidden evidence; never execute external code or copy secrets."""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
E2 = ROOT / '08_experiments/E2_labelling'
CONFIG = {
 'scout-api': ('batch2', 'jdk_8_maven/cs/rest/original/scout-api',
   '20261113T202103Z_baseline_NONE_p0_s1_1642810', 'T15_scratch/exchange_map.json'),
 'swagger-petstore': ('swagger-petstore', 'jdk_8_maven/cs/rest/original/swagger-petstore',
   '20261114T021748Z_batch_1701236_baseline_NONE_p0_s1', 'T16_scratch/swagger-petstore_exchange_map.json'),
 'market': ('market', 'jdk_11_maven/cs/rest-gui/market',
   '20261114T023303Z_batch_1724645_baseline_NONE_p0_s1', 'T16_scratch/market_exchange_map.json'),
 'cwa-verification': ('cwa-verification', 'jdk_11_maven/cs/rest/cwa-verification-server',
   '20261114T084828Z_batch_118863_baseline_NONE_p0_s1', 'T18_scratch/exchange_map.json'),
}
def digest(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(value):
 if isinstance(value, dict):
  return {k: ('[REDACTED]' if re.search(r'password|authorization|cookie|secret|token|hash', k, re.I)
              else safe(v)) for k,v in value.items()}
 if isinstance(value, list): return [safe(v) for v in value]
 if isinstance(value, str):
  return re.sub(r'(?i)(Basic|Bearer)\s+[^\s<"\']+', r'\1 [REDACTED]', value)
 return value
def compact_body(body):
 if isinstance(body,dict) and 'text' in body and 'truncated' in body:
  body=body['text']
 if not isinstance(body,str): return safe(body)
 try: return safe(json.loads(body))
 except (ValueError,TypeError):
  if '<html' in body.lower() or '<!doctype' in body.lower():
   titles=re.findall(r'<(?:title|h1)>(.*?)</(?:title|h1)>',body,re.I|re.S)
   return {'html_titles': titles, 'length':len(body)}
  return safe(body[:500])

def main():
 sample=json.loads((OUT/'sample.json').read_text())
 items=[]; protected={}
 for sut, (stem,source,run,mapping) in CONFIG.items():
  source=Path('08_experiments/_external/emb')/source
  rundir=Path('08_experiments/E1_pilot/runs')/sut/run
  blind_path=E2/(stem+'_baseline_s1_blind.csv')
  blind={r['item_id']:r for r in csv.DictReader(blind_path.open())}
  # Only extract locators. Do not expose prior decisions, rationales, or flags.
  locators={r['item_id']:r['evidence_locators'] for r in csv.DictReader(
    (E2/(stem+'_baseline_s1_labels_codex.csv')).open())}
  emap=json.loads((ROOT/'09_collab/logs'/mapping).read_text())
  if isinstance(emap,list): emap={r['item_id']:r['exchange_lines'] for r in emap}
  wanted=[r for r in sample['items'] if r['sut']==sut]
  needed={n for r in wanted for n in emap[r['item_id']]}
  exchanges={n:json.loads(line) for n,line in enumerate((ROOT/rundir/'exchanges.jsonl').open(),1) if n in needed}
  for row in wanted:
   item={**row,**blind[row['item_id']]}
   item.update({'source_root':str(source), 'spec':str(rundir/'spec.original.json'),
    'exchanges_path':str(rundir/'exchanges.jsonl'),
    'exchange_lines':emap[row['item_id']], 'previous_context_locators':locators[row['item_id']]})
   groups={}
   for n in item['exchange_lines']:
    exchange=exchanges[n];req=exchange['request'];resp=exchange['response']
    response=compact_body(resp.get('body',''))
    if item['item_id']=='P035':
     response={'syntax':'unquoted login text; content withheld','size':resp.get('body',{}).get('size')}
    key=json.dumps(response,sort_keys=True)
    if key not in groups:
     groups[key]={'line':n,'count':0,'request_path':req['path'],
      'request_query':safe(req.get('query',{})),
      'request_content_type':req.get('headers',{}).get('content-type',''),
      'request_body':compact_body(req.get('body','')),
      'response_content_type':resp.get('headers',{}).get('content-type',''),
      'response_body':response}
    groups[key]['count']+=1
   item['response_groups']=list(groups.values())
   items.append(item)
  for p in [blind_path,E2/(stem+'_baseline_s1_labels_codex.csv'),E2/(stem+'_adjudication.csv'),
            ROOT/rundir/'exchanges.jsonl',ROOT/rundir/'spec.original.json',ROOT/rundir/'compose.log']:
   protected[str(p.relative_to(ROOT))]=digest(p)
  for p in (ROOT/source).rglob('*'):
   if p.is_file() and not set(p.relative_to(ROOT/source).parts)&{'.git','target','build','node_modules'}:
    protected[str(p.relative_to(ROOT))]=digest(p)
 for p in [E2/'final_labels_baseline_s1.csv',E2/'FINAL_LABELS.md',
   ROOT/'08_experiments/R1_triage_codebook.md', E2/'proposals/CODEBOOK_11_4_PROPOSAL.md']:
  protected[str(p.relative_to(ROOT))]=digest(p)
 for p in (ROOT/'08_experiments/tools').glob('*.py'):
  protected[str(p.relative_to(ROOT))]=digest(p)
 order={r['item_id']:i for i,r in enumerate(sample['items'])}
 items.sort(key=lambda r:order[r['item_id']])
 (OUT/'working_evidence.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
 if not (OUT/'protected_before.json').exists():
  (OUT/'protected_before.json').write_text(json.dumps(protected,indent=2)+'\n')
 if not (OUT/'timeline.json').exists():
  (OUT/'timeline.json').write_text(json.dumps({'evidence_prepared_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
 for r in items:
  print(json.dumps({'item_id':r['item_id'],'response_groups':len(r['response_groups'])}))
 print(json.dumps({'items':len(items),'protected_files':len(protected)}))

if __name__=='__main__':main()
