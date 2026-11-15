"""Join adjudicated labels only after the immutable decision freeze exists."""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
DEST=ROOT/'08_experiments/E2_labelling/pilot_v06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 freeze=json.loads((OUT/'decision_freeze.json').read_text())
 assert sha(OUT/'decisions_frozen.csv')==freeze['decisions_sha256']
 for path,h in freeze['review_sha256'].items():assert sha(ROOT/path)==h
 rows=list(csv.DictReader((OUT/'decisions_frozen.csv').open()))
 final_path=ROOT/'08_experiments/E2_labelling/final_labels_baseline_s1.csv'
 final={r['item_id']:r for r in csv.DictReader(final_path.open())}
 sample=json.loads((OUT/'sample.json').read_text())
 assert sha(final_path)==sample['population_sha256']
 per_stratum={}
 diffs=[]
 for r in rows:
  f=final[r['item_id']];label=f['final_L1'];r['final_L1_joined']=label
  equal=r['L1']==label;r['agrees_with_final']=str(equal).lower()
  compatible=equal or (label=='BOTH' and r['L1']=='IMPL' and r['both_candidate']=='true')
  stat=per_stratum.setdefault(label,{'n':0,'exact_agreement':0,'primary_flag_compatible':0,'non_scout':0,'items':[]})
  stat['n']+=1;stat['exact_agreement']+=int(equal)
  stat['primary_flag_compatible']+=int(compatible)
  stat['non_scout']+=int(r['sut']!='scout-api');stat['items'].append(r['item_id'])
  if not equal:
   diffs.append({'item_id':r['item_id'],'final_L1':label,'pilot_L1':r['L1'],
    'both_candidate':r['both_candidate']=='true','adjudication_flag':r['adjudication_flag'],
    'comparison_kind':'primary-versus-final-authority' if compatible else 'substantive-review-proposal',
    'rationale':r['rationale'],'review_locator':r['intent_review_locator'],
    'existing_adjudication_note':f['note']})
 target=DEST/'T36_pilot_labels.csv'
 if target.exists():raise SystemExit('Refusing to overwrite pilot final export')
 with target.open('w',newline='') as file:
  writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 summary={'n':len(rows),'exact_agreement':sum(r['agrees_with_final']=='true' for r in rows),
  'primary_flag_compatible':sum(s['primary_flag_compatible'] for s in per_stratum.values()),
  'per_stratum':per_stratum,'disagreements':diffs,
  'pilot_L1_counts':dict(Counter(r['L1'] for r in rows)),
  'search_status_counts':dict(Counter(r['intent_search_status'] for r in rows)),
  'raw_verdict_counts':dict(Counter(r['intent_search_verdict'] for r in rows)),
  'review_verdict_counts':dict(Counter(r['intent_review_verdict'] for r in rows)),
  'both_candidate_count':sum(r['both_candidate']=='true' for r in rows),
  'same_class_policy_items':[r['item_id'] for r in rows if r['adjudication_flag']=='same_class_policy'],
  'joined_utc':datetime.now(timezone.utc).isoformat(),'decision_frozen_utc':freeze['frozen_utc'],
  'labels_sha256':sha(target),'final_labels_sha256':sha(final_path),
  'not_accuracy':'Final labels are adjudicated comparisons, not ground truth; compatibility is only a transparent authority/format reconciliation, not a second label decision.'}
 (OUT/'comparison_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k not in {'disagreements'}},ensure_ascii=False))
 print(json.dumps({'disagreements':[{k:v for k,v in d.items() if k not in {'rationale','existing_adjudication_note'}} for d in diffs]}))

if __name__=='__main__':main()
