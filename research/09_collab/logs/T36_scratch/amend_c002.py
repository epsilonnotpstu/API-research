"""Append a post-join evidence correction without changing any frozen label.

The original review and decision freeze remain immutable. Only explanatory CSV
annotations are superseded, with exact old/new cells retained in the amendment.
"""
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
DEST=ROOT/'08_experiments/E2_labelling/pilot_v06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 path=DEST/'review_amendments/C002.json'
 if path.exists():raise SystemExit('Refusing to overwrite immutable amendment')
 path.parent.mkdir(exist_ok=True)
 working=next(r for r in json.loads((OUT/'working_evidence.json').read_text()) if r['item_id']=='C002')
 groups={'missing_key_or_keyType':[],'invalid_GUID':[],'unissued_short_TELETAN':[],'invalid_HTTP_header':[]}
 for n,line in enumerate((ROOT/working['exchanges_path']).open(),1):
  if n not in working['exchange_lines']:continue
  req=json.loads(line)['request']
  bad=any(any(ord(ch)<32 and ch!='\t' for ch in str(v)) for k,v in req['headers'].items() if k.lower() not in {'authorization','cookie'})
  if bad:key='invalid_HTTP_header'
  else:
   body=json.loads(req['body']['text'])
   if body.get('key') is None or body.get('keyType') is None:key='missing_key_or_keyType'
   elif body['keyType']=='GUID':
    assert not re.fullmatch('[A-Fa-f0-9]{64}',body['key']);key='invalid_GUID'
   else:
    assert body['keyType']=='TELETAN' and len(body['key']) in {2,4}
    key='unissued_short_TELETAN'
  groups[key].append(n)
 assert [len(v) for v in groups.values()]==[49,11,2,7]
 source=working['source_root']+'/'
 original=json.loads((DEST/'review/C002.json').read_text())
 template=original['manual_additions'][0]['independence_checklist']
 def record(file,category,disposition,reason,independent):
  gates=json.loads(json.dumps(template))
  gates['a_expected_behavior']['reason']=reason
  gates['b_target_scenario']['reason']='⚠️ Same validation branch/policy traced through RegistrationTokenRequestValidator; sample values themselves are withheld.'
  gates['c_separate_basis']={'passes':independent,'reason':'Separate integration assertions, not the questioned validator.' if independent else 'Validator is context only.'}
  return {'locator':source+file,'category':category,'disposition':disposition,
   'reason':reason,'direction':'supports_impl_behavior' if independent else 'none',
   'independence_checklist':gates,'tool_miss':independent,
   'new_independent_discovery':independent}
 added=[
  record('src/test/java/app/coronawarn/verification/VerificationApplicationExternalTest.java:616-632','E-TEST','accept',
   '⚠️ Explicit invalid-hashed-GUID request asserts 400; the eleven GUID witnesses are non-64-hex strings allowed by the saved generic-string schema.',True),
  record('src/test/java/app/coronawarn/verification/VerificationApplicationExternalTest.java:596-613','E-TEST','accept',
   '⚠️ Unissued/unknown TeleTAN is explicitly expected to receive 400. The two short TeleTAN witnesses cannot be issued by this ten-character generator; link uses the same validator/service policy, not an exact token match.',True),
  record('src/main/java/app/coronawarn/verification/validator/RegistrationTokenRequestValidator.java:55-69','HANDLER','context',
   'Missing key/type returns false; GUID delegates to hashingService.isHashValid; TELETAN delegates to tanService.verifyTeleTan. This links the separate tests to actual validation and does not independently establish intent.',False),
  record('src/test/java/app/coronawarn/verification/service/TanServiceTest.java:65-72','E-TEST','context',
   'Test-side generated-TeleTAN regex fixes length ten. Actual token literals are withheld; used only to establish that length-two/four witnesses were not issued by this generator.',True),
  record('src/test/java/app/coronawarn/verification/service/TanServiceTest.java:190-219','E-TEST','context',
   'Generator output is tested against the test-side format, while invalid/unknown TeleTAN verification returns false; linked service context corroborates the integration rejection policy.',True)]
 # All added locators were inspected read-only; do not import the SUT.
 for h in added:
  rel=h['locator'].rsplit(':',1)[0];h['source_file_sha256']=sha(ROOT/rel)
 rows=list(csv.DictReader((DEST/'T36_pilot_labels.csv').open()))
 row=next(r for r in rows if r['item_id']=='C002')
 old={k:row[k] for k in ['rationale','evidence_locators','intent_review_locator']}
 row['rationale']='⚠️ Separate tests support 49 missing-key/type, 11 invalid-GUID and 2 unissued-TeleTAN rejections omitted from the saved input contract; 7 invalid-header requests are TEST. SPEC+TEST aggregates to SPEC_PARTIAL (§10.4).'
 row['evidence_locators']+=';'+';'.join(h['locator'] for h in added)
 row['intent_review_locator']+=';08_experiments/E2_labelling/pilot_v06/review_amendments/C002.json:1'
 changes={k:{'before':v,'after':row[k]} for k,v in old.items()}
 amendment={'item_id':'C002','created_utc':datetime.now(timezone.utc).isoformat(),
  'post_join':True,'label_unchanged':'SPEC_PARTIAL','comparison_unchanged':True,
  'reason':'Post-freeze semantic audit found the original explanatory count grouped all 62 non-header rejections as missing key/type. Forty-nine have missing fields; thirteen have invalid/unissued present keys. Additional independent tests were reviewed after the final join. This evidence extension is non-blind.',
  'supersedes_annotations_only':['review/C002.json:$.decision.rationale','review/C002.json:$.decision.message_decisions','CSV C002 rationale/evidence_locators/intent_review_locator'],
  'original_review_sha256':sha(DEST/'review/C002.json'),
  'manual_additions':added,'message_decisions':[
   {'constraint':k,'L1':'TEST' if k=='invalid_HTTP_header' else 'SPEC','count':len(v),'exchange_lines':v}
   for k,v in groups.items()], 'csv_annotation_changes':changes,
  'effort_note':'Additional post-join source review is outside the original sample-to-decision-freeze timing interval.'}
 path.write_text(json.dumps(amendment,ensure_ascii=False,indent=2)+'\n')
 (OUT/'T36_pilot_labels_before_annotation_amendment.csv').write_bytes((DEST/'T36_pilot_labels.csv').read_bytes())
 with (DEST/'T36_pilot_labels.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 summary=json.loads((OUT/'comparison_summary.json').read_text())
 (OUT/'comparison_summary_initial.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 summary['initial_labels_sha256']=summary['labels_sha256'];summary['labels_sha256']=sha(DEST/'T36_pilot_labels.csv')
 summary['annotation_amendment_locator']='08_experiments/E2_labelling/pilot_v06/review_amendments/C002.json:1'
 summary['annotation_amendment_sha256']=sha(path)
 (OUT/'comparison_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'amendment':str(path.relative_to(ROOT)),'counts':{k:len(v) for k,v in groups.items()},'L1_changed':False}))

if __name__=='__main__':main()
