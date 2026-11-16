import csv
import json
import re
from pathlib import Path

items = list(csv.DictReader(Path('items.csv').open()))
decisions = {r['id']: r for r in json.loads(Path('props_work_W2/decisions.json').read_text())}
assert len(items) == len(decisions) == 41

def locators(item, side, refs):
    result = []
    for filename, line in refs:
        matches = list(Path(item, side).rglob(filename))
        assert len(matches) == 1, (item, side, filename)
        path = matches[0]
        assert 0 < line <= len(path.read_text().splitlines())
        result.append(f'{path}{"#" if side == "contract" else ":"}{line}')
    return ';'.join(result)

rows = []
for item in items:
    key = item['item_id']
    d = decisions[key]
    none = d.get('none', False)
    rows.append({
        'item_id': key,
        'proposition': 'NONE' if none else f'{item["operation"]}: contract says {d["x"]}; implementation does {d["y"]}',
        'contract_locators': '' if none else locators(key, 'contract', d['c']),
        'impl_locators': '' if none else locators(key, 'impl', d['i']),
        'confidence': d['confidence'],
    })

for r in rows:
    assert len(r['proposition'].split()) <= 45, r['item_id']
    assert not re.search(r'\b(deliberate|deliberately|accidental|accidentally|intentional|intentionally|oversight|forgot|bug|wrong|correct|incorrect|should|mistake)\b', r['proposition'], re.I)

with Path('props_W2.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['item_id', 'proposition', 'contract_locators', 'impl_locators', 'confidence'])
    writer.writeheader()
    writer.writerows(rows)

by_id = {r['item_id']: r for r in rows}
def evidence(key):
    r = by_id[key]
    refs = (r['contract_locators']+';'+r['impl_locators']).split(';')
    return ' '.join(f'`{ref}`' for ref in refs if ref)

report = '''# W2 blind source reading প্রতিবেদন

`items.csv`-এর ক্রমে ৪১টি operation পর্যালোচনা করে `props_W2.csv`-তে ৪১টি row লেখা হয়েছে। এর মধ্যে ৩৭টি proposition এবং ৪টি `NONE`; `NONE` item হলো W26, W31, W38, W40। ফল ও সংশ্লিষ্ট evidence প্রতিটি CSV row-এর `item_id`, `contract_locators`, `impl_locators`-এ দেওয়া আছে।

## পদ্ধতি

প্রথম command ছিল `cat TASK_WRITE.md`। এরপর অনুমোদিত `../../../09_collab/PROTOCOL.md` ও `items.csv` পড়েছি। প্রতিটি item-এর নিজস্ব contract-এ নির্দিষ্ট operation, তার parameter ও response schema পড়েছি; implementation-এ handler, প্রয়োজনমতো DTO, validator, serializer এবং exception mapping অনুসরণ করেছি। এক item-এর সিদ্ধান্তে অন্য item-এর source ব্যবহার করিনি। `TASK_WRITE.md`-এর “Your task”, “Output” ও “Rules” অনুসারে প্রতিটি non-NONE row-তে একটি মাত্র proposition এবং দুই পাশের locator রাখা হয়েছে।

একাধিক candidate থাকলে সরাসরি source-supported parameter, default, response shape বা status আচরণ বেছে নিয়েছি। schema example ও declared field type আলাদা বিষয় হিসেবে বিবেচনা করেছি: date-array example-কে বাধ্যতামূলক JSON schema type বলা হয়নি। Confidence 3 মানে সরবরাহ করা source-এ দুই পাশের নির্দিষ্ট বক্তব্য পাওয়া গেছে; 2 মানে contract-এর অভ্যন্তরীণ দ্বৈত বক্তব্য, সীমিত source অথবা শর্তসাপেক্ষ error path সিদ্ধান্তকে সীমিত করেছে।

## কঠিন item ও সিদ্ধান্তের সীমা

'''

notes = [
('W01', 'Default শুধু endpoint annotation দেখে নির্ধারণ করিনি; provider-এর fallback ও application configuration অনুসরণ করেছি। CSV-তে page-size-এর 50 বনাম 10 পার্থক্যটি রাখা হয়েছে।'),
('W05', 'Success writer-এর library implementation সরবরাহ করা হয়নি। তাই default HTTP status অনুমানভিত্তিক proposition না দিয়ে contract-এর policy action ও handler-এর checked action-এর সরাসরি পার্থক্য রেখেছি।'),
('W10', 'XML response-এর contract annotation একটি CSV schema class উল্লেখ করে। implementation-এর formatter registration এবং XML wrapper অনুসরণ করে নির্দিষ্ট response-shape পার্থক্য লেখা হয়েছে।'),
('W17', 'Pagination range documentation এবং কার্যকর upper-bound clamp আলাদা করে পড়েছি। CSV-তে limit=0 থেকে setMaxResults(0)-এ পৌঁছানোর source behavior বলা হয়েছে; runtime response status দাবি করা হয়নি।'),
('W19', 'Nested disbursement date-এর example array, কিন্তু assembler যে parser ডাকে সেটি primitive value পড়ে। তাই proposition-এ example-এর কথা বলা হয়েছে।'),
('W23', '⚠️ Contract dryRun=true হলে কোনো পরিবর্তন না হওয়ার কথা বলে। Existing-artifact CREATE_VERSION fallback-এ handler dryRun বহন না করে version-creation call-এ false পাঠায়। Proposition এই conditional storage call-এর পার্থক্যটি বলে; storage implementation অনুপস্থিত বলে persisted state স্বাধীনভাবে যাচাই করা যায়নি, তাই confidence 2।'),
('W28', 'submittedOnDate-এর array example-এর সঙ্গে create validator-এর parser behavior পড়েছি। parser non-primitive array থেকে date তৈরি করে না, এবং validator null পরীক্ষা করে।'),
('W29', 'repaymentsStartingFromDate-এর array example ও schedule assembler-এর string-parsing path নির্দিষ্ট করে পড়েছি। submittedOnDate সম্পর্কে আলাদা কোনো দাবি যোগ করিনি।'),
('W39', 'Permission-এর descriptive text ও কার্যকর permission annotation-এর নাম পৃথক। proposition কেবল MANAGEMENT_ALERT বনাম API_ALERT checks উল্লেখ করে; সম্পূর্ণ permission framework-এর runtime behavior দাবি করে না।'),
('W41', '⚠️ Error-response তালিকায় অনুল্লিখিত 422-কে discrepancy হিসেবে পড়া হয়েছে। Source-এ Avro checker parsing exception-কে UnprocessableSchemaException করে এবং mapper সেটিকে 422 দেয়। এই path চালু হতে সংশ্লিষ্ট compatibility check প্রয়োজন; সব rule failure-এ 422 হয় এমন দাবি করা হয়নি। Abstract checker-এর সম্পূর্ণ dispatch এখানে সরবরাহ করা নেই, তাই confidence 2।'),
]
for key, note in notes:
    report += f'- **{key}** — {note} Evidence: {evidence(key)}\n\n'

report += '''## NONE item

`NONE` মানে এই operation-এর জন্য সরবরাহ করা সীমিত artifacts থেকে সমর্থনযোগ্য discrepancy প্রতিষ্ঠা করা যায়নি; সব সম্ভাব্য input-এ সামঞ্জস্য প্রমাণ করা হয়নি। CSV নির্দেশনা অনুসারে এসব row-এর locator cell খালি; পর্যালোচনার ভিত্তি নিচে দেওয়া হলো।

'''
none_notes = [
('W26', 'Single-log operation-এর JSON/ApplicationRequest declaration, delegated service return এবং route chain পড়েছি। Service-এ absent log-এর null branch আছে, কিন্তু contract ওই পরিস্থিতিতে নির্দিষ্ট response behavior ঘোষণা করে না। তাই কেবল অতিরিক্ত branch দেখে discrepancy দিইনি.', [
('contract','ApplicationLogsResource.java',88),('contract','ApplicationResource.java',287),('impl','ApplicationLogsResource.java',99),('impl','LogsServiceImpl.java',326),('impl','ApplicationsResource.java',257)]),
('W31', 'Cluster search-এর documented parameters, page envelope ও handler/use case পড়েছি। sortBy অনুপস্থিত হলে use case Optional.empty পাঠায়; downstream query service-এর source এখানে নেই। অতএব contract-এর default name sorting বাস্তবে অনুপস্থিত বলে স্থির করা যায়নি.', [
('contract','openapi-environments.yaml',534),('contract','openapi-environments.yaml',2824),('contract','openapi-environments.yaml',2967),('impl','ClustersResource.java',103),('impl','SearchClusterUseCase.java',89)]),
('W38', 'ApiRequest JSON declaration, single-log service path এবং route chain পড়েছি। DTO declaration ও returned object-এর মধ্যে নির্দিষ্ট বিরোধ পাওয়া যায়নি; missing-log null branch থেকে অঘোষিত status-এর দাবি করিনি.', [
('contract','ApiLogsResource.java',85),('contract','ApiResource.java',909),('impl','ApiLogsResource.java',96),('impl','LogsServiceImpl.java',186),('impl','ApisResource.java',527)]),
('W40', 'ProjectReq fields, success response ও Location header option-এর সঙ্গে create handler এবং local validation পড়েছি। Runtime configuration-নির্ভর branches-কে contract-এর স্পষ্ট বক্তব্যের বিপরীত হিসেবে প্রতিষ্ঠা করা যায়নি; অনুল্লিখিত configuration detail-কে একা discrepancy করিনি.', [
('contract','swagger.yaml',344),('contract','swagger.yaml',5374),('contract','swagger.yaml',6285),('impl','project.go',93),('impl','project.go',230),('impl','project.go',667)]),
]
for key, note, refs in none_notes:
    citations = []
    for side, filename, line in refs:
        citations.append('`'+locators(key, side, [(filename,line)])+'`')
    report += f'- **{key}** — {note} Evidence: '+ ' '.join(citations)+'\n\n'

report += '''## সাধারণ সীমাবদ্ধতা ও boundary

এই কাজ static source reading; runtime data, version history ও deployed configuration পাওয়া যায়নি (`TASK_WRITE.md`, “What you are given”)। Item source চালানো, compilation, Docker, Java, Maven বা network ব্যবহার করা হয়নি (`TASK_WRITE.md`, “Rules”)। নিজস্ব Python helper দিয়ে শুধু অনুমোদিত item path থেকে source পড়া এবং নিজের output লেখা/যাচাই করা হয়েছে। Source excerpt ছাপার আগে credential-looking value ও attribution শনাক্ত করে line redaction করা হয়েছে।

Boundary incident: নিষিদ্ধ board, coordinator task বা অন্য directory খোলা, list বা search করা হয়নি। বাইরের একমাত্র পড়া file হলো অনুমোদিত `../../../09_collab/PROTOCOL.md`। সাধারণ protocol-এর board/task-reading নিয়মের ক্ষেত্রে `TASK_WRITE.md`-এর supervisor override অনুসরণ করা হয়েছে। Output write সীমা ছিল `props_W2.csv`, `props_report_W2.md` এবং `props_work_W2/`।

## Output যাচাই

নিজস্ব validation-এ CSV header, ৪১টি row, `items.csv`-এর order, operation prefix, প্রতি proposition-এর সর্বোচ্চ ৪৫ শব্দ, নিষিদ্ধ শব্দের অনুপস্থিতি, confidence-এর 1–3 range, এবং সব non-NONE locator-এর item/side/file/line যাচাই করা হয়েছে। `NONE` row-তে দুই locator cell খালি রাখা হয়েছে। Validation-এর পুনরাবৃত্তিযোগ্য বিবরণ `props_work_W2/validate.py`-তে আছে।
'''
Path('props_report_W2.md').write_text(report)
print(f'Wrote {len(rows)} rows: {sum(r["proposition"] != "NONE" for r in rows)} propositions; {sum(r["proposition"] == "NONE" for r in rows)} NONE.')
