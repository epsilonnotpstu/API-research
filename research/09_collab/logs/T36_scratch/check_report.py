"""Validate explicit report citations without expanding illustrative wildcards."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
report=ROOT/'09_collab/reports/T36_report.md'
checked=[];skipped=[];errors=[]
for token in re.findall(r'`([^`]+)`',report.read_text()):
 if not token.startswith(('08_experiments/','09_collab/')) or ':' not in token:continue
 if '*' in token or '<item_id>' in token:skipped.append(token);continue
 file,ref=token.rsplit(':',1)
 if 'E5_codemut/' in file:raise SystemExit('Refusing forbidden report locator')
 p=ROOT/file
 if not p.is_file():errors.append({'locator':token,'error':'missing file'});continue
 try:
  if ref.startswith('$'):
   obj=json.loads(p.read_text())
   for quoted,key,index in re.findall(r'\."([^"]+)"|\.([A-Za-z_][A-Za-z_0-9-]*)|\[(\d+)\]',ref[1:]):
    obj=obj[int(index)] if index else obj[quoted or key]
  elif ref.startswith('item_id='):
   assert any(r['item_id']==ref.split('=',1)[1] for r in csv.DictReader(p.open()))
  else:
   count=sum(1 for _ in p.open())
   for part in ref.split(','):
    first,*last=part.split('-');first=int(first);last=int(last[0]) if last else first
    assert 1<=first<=last<=count
  checked.append(token)
 except Exception as exc:errors.append({'locator':token,'error':type(exc).__name__})
result={'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
 'resolved_report_citations':len(checked),'illustrative_wildcards_skipped':skipped,'errors':errors}
(OUT/'report_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
assert not errors
