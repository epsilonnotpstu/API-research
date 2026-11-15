import csv,pathlib,collections,re
root=pathlib.Path.cwd()
items=list(csv.DictReader(open('items.csv')))
rows=list(csv.reader(open('codes_work_C3/decisions.tsv'),delimiter='\t'))
assert [r['item_id'] for r in items]==[r[0] for r in rows]
header=['item_id','divergence_kind','contract_specificity','confidence','impl_locators','contract_locators','rationale']
output=[]
for row in rows:
 r=row[:]
 assert len(r)==7
 assert r[1] in {'DELIBERATE','ACCIDENTAL','UNCLEAR'}
 assert r[2] in {'SPECIFIC','GENERIC','UNCLEAR'}
 assert r[3] in {'1','2','3'}
 assert len(r[6].split())<=40,(r[0],len(r[6].split()))
 for pos,kind in [(4,'impl'),(5,'contract')]:
  locators=[]
  for short in r[pos].split(';'):
   name,line=short.strip().rsplit('@',1)
   paths=list(pathlib.Path(r[0]+'/'+kind).rglob(name))
   assert len(paths)==1,(r[0],name,paths)
   path=paths[0]; n=int(line)
   assert 0<n<=len(path.read_text().splitlines()),(r[0],short)
   locators.append(str(path)+(':' if kind=='impl' else '#')+str(n))
  r[pos]=';'.join(locators)
 output.append(r)
with open('codes_C3.csv','w',newline='') as f:
 writer=csv.writer(f);writer.writerow(header);writer.writerows(output)
with open('codes_C3.csv',newline='') as f:
 check=list(csv.reader(f))
assert check[0]==header and check[1:]==output
counts={header[i]:dict(collections.Counter(r[i] for r in output)) for i in [1,2,3]}

def rowlink(item):
 n=next(i+2 for i,r in enumerate(output) if r[0]==item)
 return f'[{item}](<{root}/codes_C3.csv:{n}>)'
def evidence(item,kind,index=0):
 r=next(r for r in output if r[0]==item)
 locator=r[4 if kind=='impl' else 5].split(';')[index]
 path,n=locator.rsplit(':' if kind=='impl' else '#',1)
 return f'[{item}/{kind}, line {n}](<{root}/{path}:{n}>)'
report=f'''C3 হিসেবে `items.csv`-এর ক্রমে {len(output)}টি item স্বাধীনভাবে code করেছি। দুই coding field, confidence, implementation ও contract locator, এবং সর্বোচ্চ 40-word rationale [codes_C3.csv](<{root}/codes_C3.csv>) ফাইলে আছে। ফল: divergence_kind-এ {counts['divergence_kind'].get('DELIBERATE',0)}টি DELIBERATE, {counts['divergence_kind'].get('ACCIDENTAL',0)}টি ACCIDENTAL, {counts['divergence_kind'].get('UNCLEAR',0)}টি UNCLEAR; contract_specificity-তে {counts['contract_specificity'].get('SPECIFIC',0)}টি SPECIFIC, {counts['contract_specificity'].get('GENERIC',0)}টি GENERIC। confidence 3 পেয়েছে {counts['confidence'].get('3',0)}টি, confidence 2 পেয়েছে {counts['confidence'].get('2',0)}টি। এই সংখ্যা CSV-এর সংশ্লিষ্ট column থেকে গণনা করা হয়েছে।

পদ্ধতি: প্রথম command ছিল `cat TASK_CODE.md`; এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` পড়েছি। TASK_CODE.md-এর supervisor override অনুযায়ী COLLAB_BOARD.md বা coordinator task পড়িনি। প্রতিটি proposition-এর X ও Y আলাদাভাবে যাচাই করেছি; কোনো item-এর সিদ্ধান্তে অন্য item-এর source ব্যবহার করিনি। ⚠️ সব label static code-structure থেকে করা interpretation; DELIBERATE দিয়ে দৃশ্যমান code target বোঝানো হয়েছে, developer-এর ব্যক্তিগত উদ্দেশ্য নয়। যেমন explicit no-op branch-এর জন্য {rowlink('X06')} DELIBERATE ({evidence('X06','impl')}); missing null guard-এর জন্য {rowlink('X13')} ACCIDENTAL ({evidence('X13','impl',1)})।

দুরূহ coding boundary-গুলি:

- {rowlink('X19')}: status-only `ResponseEntity` construction-কে explicit response choice হিসেবে DELIBERATE করেছি ({evidence('X19','impl')})। অন্যদিকে {rowlink('X69')}-তে নির্বাচিত formatter-এর media type response-এ বসানো হয়নি; configured JSON default থেকে যাওয়া omission, তাই ACCIDENTAL ({evidence('X69','impl',0)}, {evidence('X69','impl',2)})।
- {rowlink('X20')} ও {rowlink('X60')}: parameter পড়ার code explicit হলেও যথাক্রমে CLOB_ID এবং DESIGNATOR ব্যবহারে proposition-এর Y wrong-variable outcome; rubric অনুযায়ী ACCIDENTAL ({evidence('X20','impl')}, {evidence('X60','impl')})।
- {rowlink('X31')}: `_links`-এর Swagger annotation আছে, Jackson naming override নেই; `getLinks()` থেকে `links` হওয়া default naming-এর inference। তাই ACCIDENTAL এবং confidence 2 ({evidence('X31','impl',0)}, {evidence('X31','impl',1)})।
- {rowlink('X44')}: `.ifPresent(...)` শুধু পাওয়া role delete করে; missing role-এর branch নেই। অনুপস্থিত role-এ error না হওয়াকে omitted handling হিসেবে ACCIDENTAL করেছি; intentional idempotence-এর প্রমাণ না থাকায় confidence 2 ({evidence('X44','impl')})।
- {rowlink('X09')}: contract-এর identifier template-এ `search` বসানোর applicability এবং undocumented search operation থেকে X আসে, তাই GENERIC; implementation-এর dedicated search route স্পষ্ট, তাই DELIBERATE ({evidence('X09','contract')}, {evidence('X09','impl')})।
- {rowlink('X05')} ও {rowlink('X42')}: collection/detail annotation reuse এবং অনুপস্থিত array marker থেকে response shape পাওয়া যায়। এদের contract_specificity GENERIC, confidence 2 ({evidence('X05','contract',0)}, {evidence('X05','contract',1)}, {evidence('X42','contract',0)}, {evidence('X42','contract',1)})।
- {rowlink('X30')}, {rowlink('X46')}, {rowlink('X47')}, {rowlink('X49')}, {rowlink('X64')}: আলাদা semantic prose ছাড়া Swagger helper/model field-এর inferred type বা name-কে GENERIC হিসেবে পড়েছি। বিশেষত X46-এ nested-map declaration-এর পাশের example flat; confidence 2 রেখেছি ({evidence('X46','contract')})। এই schema-metadata বনাম dedicated-statement সীমারেখায় interpretive uncertainty আছে।
- {rowlink('X59')} এবং {rowlink('X68')}: প্রত্যেকটির নিজস্ব contract-এ ENGLISH/WELSH enum-এর পাশেই ISO-code prose ও `en` example আছে; implementation নিজে ISO-alpha-two parser ডাকে। ENUM metadata-ভিত্তিক X-কে GENERIC, parser choice-কে DELIBERATE, confidence 2 করেছি ({evidence('X59','contract')}, {evidence('X59','impl')}; {evidence('X68','contract')}, {evidence('X68','impl')})।
- {rowlink('X67')}: sorting semantics prose থাকলেও তা shared parameter definition থেকে inherited, তাই GENERIC। handler parameter bind করে, কিন্তু query-তে sorting apply করে না, তাই ACCIDENTAL ({evidence('X67','contract',0)}, {evidence('X67','contract',1)}, {evidence('X67','impl',1)})।

সীমাবদ্ধতা: runtime data, history এবং supplied directory-এর বাইরের dependency implementation ব্যবহার করিনি। Framework property naming, validation ও async response resolution সম্পর্কে ফল static inference; production wire response যাচাইয়ের দাবি করছি না। Schema field metadata-কে GENERIC ধরার ব্যাখ্যা উপরেই দেওয়া হয়েছে; origin অস্পষ্ট এমন ক্ষেত্রে confidence 2 রেখেছি। কোন artifact সঠিক বা ভুল, তা বিচার করিনি। সরবরাহকৃত implementation দিয়ে Y সমর্থিত না হলে UNCLEAR দেওয়ার নিয়ম প্রয়োগের প্রস্তুতি ছিল; এই reading-এ এমন item পাওয়া যায়নি। বিস্তারিত item-wise evidence CSV-তে রয়েছে।

যাচাই: নিজের Python helper দিয়ে item count ও order, সাতটি column, enum label, confidence range, rationale word limit, সব locator-এর file existence ও line bounds, এবং CSV round-trip পরীক্ষা করেছি। কোনো item source execute, compile বা build করিনি; network, Docker, Java বা Maven ব্যবহার করিনি। শুধু নিজস্ব Python helper চালিয়েছি। Helper-এর একটি invalid regex expression সংশোধন করে reading পুনরায় করেছি; এটি boundary access ঘটায়নি।

Boundary incidents: কোনো accidental boundary access শনাক্ত হয়নি। অনুমোদিত protocol file ছাড়া এই directory-এর বাইরের কোনো file পড়িনি; board, coordinator task বা অন্য coder-এর output পড়িনি। Source print করার আগে credential-looking literal ও personal attribution filter করেছি; final output-এ এসব value রাখিনি। লেখা সীমিত ছিল `codes_C3.csv`, `codes_report_C3.md`, এবং `codes_work_C3/`-এ। Open question: schema-only metadata এবং dedicated contract statement-এর borderline coding supervisor চাইলে উপরোক্ত evidence থেকে পুনর্বিবেচনা করতে পারেন; কাজ শেষ করতে কোনো তথ্য বাকি নেই।
'''
pathlib.Path('codes_report_C3.md').write_text(report)
print('PASS: 67 ordered items; required columns, labels, confidence, <=40-word rationales, existing locators, line bounds, CSV round-trip.')
print(counts)
print('Wrote codes_C3.csv and codes_report_C3.md.')
