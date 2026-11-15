#!/usr/bin/python3
"""Audit dataset invariants and independently check parent/fix contract facts."""
from collections import Counter
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import runpy
m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
ROOT=m['ROOT'];git=m['git'];blob=m['blob']
candidates=list(csv.DictReader((ROOT/'candidates.csv').open()))
accepted=list(csv.DictReader((ROOT/'accepted.csv').open()))
summary=json.loads((ROOT/'summary.json').read_text())
index=json.loads((ROOT/'evidence_index.json').read_text())
checks=[]
def check(name,value):
    assert value,name
    checks.append(name)
def get(r,side,path):return blob(r['repo'],r[side+'_commit'],path)
def doc(r,side,path):return json.loads(get(r,side,path))
check('105 manually reviewed commits',sum(r['review_status']!='not_reviewed' for r in candidates)==105)
check('all 13 repositories represented',len({r['repo'] for r in candidates if r['review_status']!='not_reviewed'})==13)
check('accepted commit/item uniqueness',len(accepted)==len({(r['repo'],r['fix_commit']) for r in accepted})==13)
check('direction totals',Counter(r['truth_direction'] for r in accepted)=={'SPEC':10,'IMPL':3})
for r in candidates:
    if r['review_status']!='not_reviewed':check(r['candidate_id']+' review evidence exists',(ROOT/r['review_evidence']).is_file())
for r,item in zip(accepted,index):
    check(r['item_id']+' real single parent',git(r['repo'],'log','-1','--format=%P',r['fix_commit']).decode().strip()==r['parent_commit'])
    check(r['item_id']+' date',git(r['repo'],'log','-1','--format=%cs',r['fix_commit']).decode().strip()==r['date'])
    check(r['item_id']+' neutral template',r['proposition'].startswith(r['operation']+': contract says ') and '; implementation does ' in r['proposition'] and not re.search(r'\b(fix|changed|later|corrected|updated)\b',r['proposition'],re.I))
    pc=json.loads(r['proposition_check'])
    check(r['item_id']+' parent-only proposition locators',all(ref.startswith(r['parent_commit']+':') for k in ('contract','implementation','route') for ref in pc[k]))
    for loc in item['locators']:
        data=git(r['repo'],'show',loc['revision']+':'+loc['path'])
        check(r['item_id']+' blob '+loc['side']+' '+loc['path']+':'+str(loc['line']),hashlib.sha256(data).hexdigest()==loc['sha256'] and loc['needle'] in data.decode('utf-8','replace').splitlines()[loc['line']-1])
    check(r['item_id']+' excerpt exists',(ROOT/'source_evidence'/(r['item_id']+'.txt')).is_file())
    check(r['item_id']+' message <=160',len(r['message_excerpt'])<=160)
    cid=r['candidate_id']
    if cid=='C0010':
        check(cid+' string -> number',re.search(r'      score:\n        type: string',get(r,'parent','catwatch-api/catwatch_rest_api.yaml')) is not None and re.search(r'      score:\n        type: number',get(r,'fix','catwatch-api/catwatch_rest_api.yaml')) is not None)
    elif cid=='C0058':
        for side,expected in [('parent','DeferredResultResponseEntityTan'),('fix','Tan')]:
            ref=doc(r,side,'api-docs.json')['paths']['/version/v1/tan']['post']['responses']['201']['content']['application/json']['schema']['$ref']
            check(cid+' '+side+' response schema',ref=='#/components/schemas/'+expected)
    elif cid=='C0059':
        for side,status in [('parent','200'),('fix','201')]:
            responses=doc(r,side,'api-docs.json')['paths']['/version/v1/registrationToken']['post']['responses']
            check(cid+' '+side+' success code',status in responses and ('201' if status=='200' else '200') not in responses)
    elif cid=='C0088':
        path='src/main/java/app/coronawarn/verification/service/HashingService.java'
        check(cid+' anchored parent regex','"^[0-9A-Fa-f]{64}$"' in get(r,'parent',path))
        check(cid+' find -> matches','return matcher.find();' in get(r,'parent',path) and 'return matcher.matches();' in get(r,'fix',path))
    elif cid=='C0211':
        path='api/microcks-openapi-v1.10.yaml'
        check(cid+' date width',re.search(r'createdDate:\n\s+format: int32',get(r,'parent',path)) is not None and re.search(r'createdDate:\n\s+format: int64',get(r,'fix',path)) is not None)
    elif cid=='C0252':
        path='api/microcks-openapi-v1.10.yaml'
        check(cid+' whole parent omission','  /secrets/search:' not in get(r,'parent',path) and '  /secrets/search:' in get(r,'fix',path))
    elif cid=='C0260':
        path='api/microcks-openapi-v1.10.yaml'
        for side,required in [('parent',False),('fix',True)]:
            content=get(r,side,path);part=content.split('  /secrets/{id}:',1)[1].split('    put:',1)[1].split('    delete:',1)[0]
            check(cid+' '+side+' body',('requestBody:' in part)==required and (not required or 'required: true' in part))
    elif cid=='C0922':
        path='openapi/publicapi_spec.json'
        for side,expected in [('parent',True),('fix',False)]:
            schema=doc(r,side,path)['components']['schemas']['PaymentRefundRequest']['properties']['refund_amount_available']
            check(cid+' '+side+' readOnly',schema.get('readOnly',False)==expected)
    elif cid=='C1015':
        path='swagger/swagger.json'
        for side in ('parent','fix'):
            params=doc(r,side,path)['paths']['/v1/events']['get']['parameters']
            check(cid+' '+side+' optional dates',all(next(p for p in params if p['name']==name)['required'] is False for name in ('from_date','to_date')))
    elif cid=='C1049':
        path='swagger/swagger.json'
        parent=doc(r,'parent',path)['definitions']['CreatePaymentResult']['properties'];fix=doc(r,'fix',path)['definitions']['CreatePaymentResult']['properties']
        check(cid+' response name','paymentId' in parent and 'payment_id' not in parent and 'payment_id' in fix and 'paymentId' not in fix)
        for side in ('parent','fix'):
            check(cid+' '+side+' operation binding',doc(r,side,path)['paths']['/v1/payments']['post']['responses']['201']['schema']['$ref']=='#/definitions/CreatePaymentResult')
    elif cid=='C1054':
        for side,expected in [('parent','MandateResponse'),('fix','SearchMandateResponse')]:
            check(cid+' '+side+' response model',doc(r,side,'swagger/swagger.json')['paths']['/v1/directdebit/mandates']['get']['responses']['200']['schema']['$ref']=='#/definitions/'+expected)
    elif cid=='C1055':
        def pattern(side):return next(p['pattern'] for p in doc(r,side,'swagger/swagger.json')['paths']['/v1/directdebit/payments']['get']['parameters'] if p['name']=='state')
        check(cid+' published pattern unchanged',pattern('parent')==pattern('fix'))
    elif cid=='C1202':
        path='src/main/resources/openapi.yaml'
        for side,expected in [('parent','false'),('fix','true')]:
            part=get(r,side,path).split('  /pet/findByStatus:',1)[1].split('  /pet/findByTags:',1)[0]
            check(cid+' '+side+' status required','          required: '+expected in part)
    # Compare actual implementation evidence paths that do not also carry contract edits.
    contract_paths={x['path'] for x in item['locators'] if x['role']=='contract'}
    for path in {x['path'] for x in item['locators'] if x['role']=='implementation'}-contract_paths:
        if r['truth_direction']=='SPEC':check(cid+' unchanged behaviour '+path,get(r,'parent',path)==get(r,'fix',path))

# No live star counts or popularity ranks are invented.
for repo in json.loads((ROOT/'inventory.json').read_text()):
    check(repo['repo']+' HEAD unchanged',git(repo['repo'],'rev-list','-1','HEAD').decode().strip()==repo['head'])
    check(repo['repo']+' reachable count unchanged',int(git(repo['repo'],'rev-list','--all','--count'))==repo['all_reachable_commit_count'])

scan=[]
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.suffix not in {'.csv','.json','.diff','.txt','.md'}:continue
    content=path.read_text()
    if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',content):scan.append(str(path.relative_to(ROOT))+':email')
    if re.search(r'(?i)[?&][^\s=&"<>]*(?:token|secret|password|api.?key)[^\s=&"<>]*=(?!\[REDACTED\])[^&\s"<>]+',content):scan.append(str(path.relative_to(ROOT))+':query_value')
check('output privacy pattern scan',not scan)
result=dict(passed=True,assertions=len(checks),checks=checks,privacy_findings=scan,verified_utc=dt.datetime.now(dt.timezone.utc).isoformat(),limits=['Semantic parent propositions are manually reviewed, not proven by these mechanical checks.','No HTTP or external code was executed.','Negative source scans and static reasoning do not establish runtime reproducibility.'])
m['dump']('verification.json',result)
print(json.dumps({'passed':True,'assertions':len(checks),'accepted_items':len(accepted),'reviewed_commits':105}))
