from pathlib import Path
import csv,re,collections
root=Path('.')
contracts={}
for line in (root/'codes_work_G2/contracts.txt').read_text().splitlines():
 parts=line.split('|'); contracts[int(parts[0])]=parts[1:]
rows=[]
header='item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale'.split(',')
confidence2={5,6,20,28,36,39,42,46,54,61,63,78,100,101,103,105,107,112,125,126,127,128,130,134,136,138}
for line in (root/'codes_work_G2/decisions.txt').read_text().splitlines():
 parts=line.split('|'); n=int(parts[0]); item=f'A{n:03}'; confidence=2 if n in confidence2 else 3
 if parts[1] in ('NO','UNCLEAR'):
  relevant=parts[1];loc=parts[2];rationale=parts[3]
  if relevant=='UNCLEAR':confidence=1
  row=[item,relevant]+['NA']*7+[str(confidence),f'{item}/diff.patch:{loc}',rationale]
 else:
  kind,principals,fix,loc,rationale=parts[1:]
  op,security,policy,clocs=contracts[n]
  clocs='; '.join(f'{item}/contract/{x}' for x in clocs.split(';'))
  row=[item,'YES',kind,principals,'YES',op,security,policy,fix,str(confidence),f'{item}/diff.patch:{loc}; {clocs}',rationale]
 assert len(row)==len(header),(item,row)
 assert len(rationale.split())<=40,(item,len(rationale.split()))
 for entry in row[10].split('; '):
  p,l=entry.rsplit(':',1);f=Path(p); assert f.is_file(),entry
  assert 0<int(l)<=len(f.read_text().splitlines()),entry
 rows.append(row)
expected=[r['item_id'] for r in csv.DictReader((root/'items.csv').open())]
assert [r[0] for r in rows]==expected
with (root/'codes_G2.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(header);writer.writerows(rows)
print('Validated',len(rows),'rows; relevance',dict(collections.Counter(r[1] for r in rows)))
