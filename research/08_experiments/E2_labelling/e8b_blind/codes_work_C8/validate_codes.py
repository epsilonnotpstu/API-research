from pathlib import Path
import csv,re
expected=['item_id','divergence_kind','contract_specificity','confidence','impl_locators','contract_locators','rationale']
with Path('codes_C8.csv').open(newline='') as f:
 reader=csv.DictReader(f); assert reader.fieldnames==expected
 rows=list(reader)
items=list(csv.DictReader(Path('items.csv').open()))
assert [r['item_id'] for r in rows]==[r['item_id'] for r in items]
assert len(rows)==41 and len({r['item_id'] for r in rows})==41
for r in rows:
 assert r['divergence_kind'] in {'DELIBERATE','ACCIDENTAL','UNCLEAR'}
 assert r['contract_specificity'] in {'SPECIFIC','GENERIC','UNCLEAR'}
 assert r['confidence'] in {'1','2','3'}
 assert len(r['rationale'].split())<=40
 for side,field,sep in [('impl','impl_locators',':'),('contract','contract_locators','#L')]:
  for locator in r[field].split(';'):
   filename,number=locator.rsplit(sep,1)
   p=Path(filename)
   assert p.parts[:2]==(r['item_id'],side)
   assert p.is_file() and 1<=int(number)<=len(p.read_text().splitlines())
report=Path('codes_report_C8.md').read_text()
assert all(s in report for s in ['পদ্ধতি','কঠিন সিদ্ধান্ত','সীমাবদ্ধতা','Boundary incidents'])
assert any('\u0980'<=ch<='\u09ff' for ch in report)
print('PASS: 41 rows, exact columns/order, unique IDs, valid labels/confidence, existing in-item locators, rationales <=40 words, Bengali report present.')
print('Deliverables: codes_C8.csv; codes_report_C8.md')
