from pathlib import Path
import csv,collections
h='item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale'.split(',')
with Path('codes_G2.csv').open(newline='') as f:
 reader=csv.DictReader(f); assert reader.fieldnames==h; rows=list(reader)
expected=[r['item_id'] for r in csv.DictReader(Path('items.csv').open())]
assert [r['item_id'] for r in rows]==expected
assert len({r['item_id'] for r in rows})==138
allowed={
 'ac_relevant':{'YES','NO','UNCLEAR'},
 'ac_kind':{'OBJECT_LEVEL','FUNCTION_LEVEL','PROPERTY_LEVEL','MISSING_AUTHENTICATION','TENANT_ISOLATION','OTHER'},
 'principals_needed':{'NONE','ONE','TWO_SAME_ROLE','TWO_ROLES','UNCLEAR'},
 'observable_via_http':{'YES','NO','UNCLEAR'},
 'contract_operation':{'PRESENT','ABSENT','NO_CONTRACT','UNCLEAR'},
 'contract_security':{'DECLARED','NOT_DECLARED','UNCLEAR','NA'},
 'policy_in_contract':{'YES','NO','UNCLEAR'},
 'fix_location':{'HANDLER','MIDDLEWARE_FILTER','SERVICE_LOGIC','DATA_QUERY','MODEL_BINDING','OTHER'},
 'confidence':{'1','2','3'}}
for r in rows:
 assert None not in r
 for key,opts in allowed.items():
  if r['ac_relevant']!='YES' and key in h[2:9]:assert r[key]=='NA'
  else:assert r[key] in opts,(r['item_id'],key,r[key])
 if r['ac_relevant']=='YES' and r['contract_operation']!='PRESENT':assert r['contract_security']=='NA'
 assert len(r['rationale'].split())<=40
 for loc in r['locators'].split('; '):
  path,line=loc.rsplit(':',1); ls=Path(path).read_text().splitlines();assert 0<int(line)<=len(ls)
assert Path('codes_report_G2.md').is_file()
print('PASS: header, order, unique rows, enum values, NA rules, rationale lengths, and all locator files/lines.')
print(dict(collections.Counter(r['ac_relevant'] for r in rows)))
