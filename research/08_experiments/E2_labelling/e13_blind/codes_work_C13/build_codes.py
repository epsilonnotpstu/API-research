import csv,pathlib,re,collections,json
src=pathlib.Path('codes_work_C13/decisions.tsv')
rows=list(csv.reader(src.open(),delimiter='|'))
assert all(len(r)==7 for r in rows)
byid={r[0]:r for r in rows}
def add(item,col,loc): byid[item][col]+=';'+loc
def replace(item,col,old,new): byid[item][col]=byid[item][col].replace(old,new)
replace('Q15',4,'enricher.go:','pkg/handler/enricher.go:')
replace('Q32',4,'enricher.go:','pkg/handler/enricher.go:')
replace('Q20',4,'authelia_context.go:228','authelia_context.go:90')
replace('Q29',4,'restream.go:189','http/handler/api/restream.go:189')
replace('Q38',4,'handler.go:430','engine/ladon/handler.go:430')
replace('Q38',5,'api.swagger.json#110','api.swagger.json#165')
replace('Q53',4,'V2EnvelopeWriter.java:163','V2EnvelopeWriter.java:169')
replace('Q58',4,'link.go:262','link.go:22;link.go:213')
replace('Q59',5,'api.yaml#750','api.yaml#771')
replace('Q61',4,'FlowFileQueueResource.java:446','FlowFileQueueResource.java:483')
replace('Q61',4,'ListingRequestEntity.java:35','ListingRequestEntity.java:36')
add('Q04',4,'server.go:62')
add('Q06',4,'ClientModel.java:101;ClientModel.java:137;ClientModel.java:153')
add('Q10',4,'image.go:166;services.gen.go:3894')
add('Q19',4,'restream.go:81;restream.go:525')
add('Q19',5,'swagger.yaml#2327;swagger.yaml#2487')
add('Q24',4,'server.go:555')
add('Q26',4,'auth.go:136')
add('Q38',4,'engine/ladon/handler.go:438')
add('Q41',4,'restream.go:129;restream.go:525')
add('Q41',5,'swagger.yaml#2387;swagger.yaml#2487')
add('Q51',4,'ClientModel.java:101;ClientModel.java:137;ClientModel.java:153')
add('Q53',4,'V2EnvelopeWriter.java:163')
add('Q54',5,'api.swagger.json#1032')
add('Q59',4,'services.gen.go:4098')
for q in ('Q06','Q08','Q31','Q38','Q45','Q49','Q51','Q52','Q56','Q57'):
 byid[q][6]='⚠️ '+byid[q][6]
header=['item_id','divergence_kind','contract_specificity','confidence','impl_locators','contract_locators','rationale']
ids=[r['item_id'] for r in csv.DictReader(open('items.csv'))]
assert [r[0] for r in rows]==ids
excerpts=[]
for r in rows:
 assert r[1] in ('DELIBERATE','ACCIDENTAL','UNCLEAR')
 assert r[2] in ('SPECIFIC','GENERIC','UNCLEAR')
 assert r[3] in ('1','2','3')
 assert len(r[6].split())<=40,(r[0],len(r[6].split()))
 for col,side,sep in ((4,'impl',':'),(5,'contract','#')):
  resolved=[]
  for loc in r[col].split(';'):
   suffix,line=loc.rsplit(sep,1)
   base=pathlib.Path(r[0])/side
   matches=[p for p in base.rglob('*') if p.is_file() and (p.as_posix().endswith('/'+suffix))]
   assert len(matches)==1,(r[0],side,suffix,[str(p) for p in matches])
   p=matches[0]
   lines=p.read_text().splitlines()
   assert 1<=int(line)<=len(lines),(loc,len(lines))
   assert lines[int(line)-1].strip(),(r[0],loc,'blank locator')
   resolved.append(str(p)+sep+line)
   excerpts.append({'item_id':r[0],'side':side,'locator':resolved[-1],'line':lines[int(line)-1]})
  r[col]=';'.join(resolved)
with open('codes_C13.csv','w',newline='') as f:
 w=csv.writer(f)
 w.writerow(header)
 w.writerows(rows)
with open('codes_work_C13/validation.json','w') as f:
 json.dump({'rows':len(rows),'order_matches_items':True,'locators_verified':len(excerpts),'max_rationale_words':max(len(r[6].split()) for r in rows),'divergence_kind_counts':dict(collections.Counter(r[1] for r in rows)),'contract_specificity_counts':dict(collections.Counter(r[2] for r in rows)),'confidence_counts':dict(collections.Counter(r[3] for r in rows))},f,indent=2)
print(pathlib.Path('codes_work_C13/validation.json').read_text())
