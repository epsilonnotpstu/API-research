from pathlib import Path
import csv,json,re
root=Path('.')
rows={r[0]:r for r in (s.split('|') for s in Path('codes_work_G3/decisions.psv').read_text().splitlines())}
# Corrections established during the locator and consistency review.
rows['C007'][2]='UNCLEAR'
rows['C022'][2]='UNCLEAR'
proxy='/api/proxy/{planeType}/{planeID}/{namespace}/{crName}/{target}/{path}'
rows['C025'][1]='; '.join(m+' '+proxy for m in ('GET','POST','PUT','PATCH','DELETE'))
rows['C025'][9]='The gateway proxy forwards caller-selected methods and target paths; the sole contract describes the separate RCA agent service.'
rows['C062'][1]='; '.join(m+' '+proxy for m in ('GET','POST','PUT','PATCH','DELETE'))
rows['C071'][1]=rows['C071'][1].replace('/contents','/flow-contents')
rows['C078'][2]='NO_CONTRACT'
rows['C078'][9]='The sole nonempty document contains unrendered template directives; the affected forwarded-authorization routes and domain-canonicalization rule cannot be verified from a usable API description.'
rows['C058'][3]='contract/swagger__swagger.json:584'
rows['C069'][3]='contract/pkg__swagger__swagger.json:2321'
rows['C077'][3]='contract/api__openapi-spec__swagger.json:2895'
rows['C098'][3]='contract/Documentation__dev-guide__apispec__swagger__rpc.swagger.json:693'
rows['C097'][5]='contract/api__openapi.yaml:24'
rows['C073'][5]='contract/api__swagger.yml:12'
# Global JSON security has the same indentation as the top-level paths key.
# Otherwise, locate the selected method's security declaration inside the cited path entry.
for item,r in rows.items():
 if r[5]!='AUTO':continue
 fn,line=r[3].rsplit(':',1);p=Path(item)/fn;lines=p.read_text().splitlines();doc=json.loads(p.read_text())
 pathsline=min((l for l in lines if re.match(r'\s*"paths"\s*:',l)),key=lambda l:len(l)-len(l.lstrip()))
 indent=len(pathsline)-len(pathsline.lstrip())
 if doc.get('security'):
  indices=[i+1 for i,l in enumerate(lines) if re.match(r'\s*"security"\s*:',l) and len(l)-len(l.lstrip())==indent]
  assert len(indices)==1,(item,indices)
  r[5]=fn+':'+str(indices[0]);continue
 start=int(line)-1
 path=json.loads(re.match(r'\s*(".*")\s*:',lines[start])[1])
 entry=doc['paths'][path]
 def norm(s):return re.sub(r'\{[^}]+\}','{}',s).rstrip('/')
 methods=[]
 for operation in r[1].split('; '):
  if ' ' not in operation:continue
  m,op=operation.split(' ',1)
  if norm(op).endswith(norm(path)) and m.lower() in entry:methods.append(m.lower())
 assert methods,(item,path,r[1])
 method=next((m for m in methods if entry[m].get('security')),methods[0])
 mi=next(i for i in range(start+1,len(lines)) if re.match(r'\s*"'+method+r'"\s*:',lines[i]))
 mid=len(lines[mi])-len(lines[mi].lstrip())
 end=next((i for i in range(mi+1,len(lines)) if lines[i].strip() and len(lines[i])-len(lines[i].lstrip())<=mid and re.match(r'\s*"',lines[i])),len(lines))
 si=next(i for i in range(mi+1,end) if re.match(r'\s*"security"\s*:',lines[i]))
 r[5]=fn+':'+str(si+1)
headers='item_id,operation,contract_operation,op_locator,contract_security,sec_locator,policy_in_contract,policy_quote,confidence,rationale'.split(',')
order=[r['item_id'] for r in csv.DictReader(Path('items.csv').open())]
with Path('codes_G3.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(headers);w.writerows(rows[i] for i in order)
errors=[]
for i in order:
 r=rows[i]
 if len(r[9].split())>30:errors.append((i,'rationale words',len(r[9].split())))
 if len(r[7].split())>25:errors.append((i,'quote words',len(r[7].split())))
 for col in (3,5):
  if not r[col]:continue
  fn,ln=r[col].rsplit(':',1)
  lines=(Path(i)/fn).read_text().splitlines()
  if not ln.isdigit() or int(ln)>len(lines):errors.append((i,'invalid locator',r[col]));continue
  text=lines[int(ln)-1]
  if col==3 and not re.search(r'[\"\']?/[\w{]',text):errors.append((i,'not path line',r[col],text))
  if col==5 and 'security' not in text:errors.append((i,'not security line',r[col],text))
 if r[6]=='YES':
  contents=[p.read_text() for p in (Path(i)/'contract').iterdir() if p.is_file()]
  # JSON prose uses escapes; also check decoded strings.
  matches=any(r[7] in c or r[7].replace('`','\\u0060') in c for c in contents)
  if not matches:errors.append((i,'quote not raw substring',r[7]))
 if r[2]!='PRESENT' and r[4]!='NA':errors.append((i,'security NA expected'))
print('Rows:',len(order),'Validation issues:',json.dumps(errors,ensure_ascii=False))
print('Contract operations:',dict(__import__('collections').Counter(r[2] for r in rows.values())))
