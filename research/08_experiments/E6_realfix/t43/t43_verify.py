#!/usr/bin/python3
"""Independent output/contract audit; reads upstream blobs, never executes upstream code."""
import ast
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT=Path(__file__).resolve().parent
m=runpy.run_path(str(ROOT/'t43_mine.py'))
BASE=ROOT.parent
checks=0
def check(value,label):
    global checks
    assert value,label
    checks+=1
rows=list(csv.DictReader((ROOT/'candidates.csv').open()))
acc=list(csv.DictReader((ROOT/'accepted.csv').open()))
old=list(csv.DictReader((BASE/'accepted.csv').open()))
combined=list(csv.DictReader((BASE/'combined_accepted.csv').open()))
s=json.loads((ROOT/'summary.json').read_text())
check(len(rows)==s['pool_count']==6370,'pool size')
reviewed=[x for x in rows if x['review_status']!='not_reviewed']
check(len(reviewed)==s['reviewed_commits']==251,'manual review count')
check(len(acc)==s['accepted_items']==12,'accepted count')
check(Counter(x['truth_direction'] for x in acc)==s['direction_counts'],'accepted direction recount')
check(Counter(x['truth_direction'] for x in combined)==s['combined_directions'],'combined direction recount')
check(len(combined)==len(old)+len(acc)==25,'union size')
check(len({x['dedup_key'] for x in combined})==len(combined),'union family deduplication')
for prior in old:
    copied=next(x for x in combined if x['source_task']=='T42' and x['item_id']==prior['item_id'])
    check(all(copied[k]==v for k,v in prior.items()),'T42 original fields byte values '+prior['item_id'])
for repo in m['REPOS']:
    selected=[x for x in reviewed if x['repo']==repo]
    check(set(range(1,21))<=set(int(x['rank']) for x in selected),'every rank 1-20 '+repo)
    check(all(x['review_reason'] and (BASE/x['review_evidence']).is_file() for x in selected),'review reason/diff exists '+repo)
for row in acc:
    prop=json.loads(row['proposition_check']);ev=json.loads(row['evidence'])
    check(all(prop[k] for k in ('contract','implementation','route')),'parent roles '+row['item_id'])
    check(all(ref.startswith(row['parent_commit']+':') for refs in prop.values() for ref in refs),'parent-only checks '+row['item_id'])
    check((BASE/ev['source_excerpt']).is_file() and (BASE/ev['diff_hunk']['evidence_file']).is_file(),'evidence files '+row['item_id'])
    check(row['proposition'].startswith(row['operation']+': contract says '),'neutral operation '+row['item_id'])
    if row['truth_direction']=='IMPL':
        check(bool(ev['contract_gate']),'independent parent contract gate '+row['item_id'])
    for loc in ev['snapshots']:
        raw=m['git'](row['repo'],'show',loc['revision']+':'+loc['path'])
        check(hashlib.sha256(raw).hexdigest()==loc['sha256'],'blob hash '+row['item_id'])
        check(1<=loc['excerpt_start']<=loc['line']<=loc['excerpt_end']<=len(raw.decode('utf-8','replace').splitlines()),'locator extent '+row['item_id'])

byid={x['item_id']:x for x in acc}
def parent(i,path):
    r=byid[i];return m['blob'](r['repo'],r['parent_commit'],path)
def spec(i):return json.loads(parent(i,'src/main/resources/openapi.json'))
check('text/plain' in spec('T43R001')['paths']['/metrics']['get']['responses']['200']['content'],'explicit parent metrics media type')
check(set(spec('T43R002')['paths']['/topics/{topicname}']['post']['requestBody']['content'])>={'application/vnd.kafka.json.v2+json','application/vnd.kafka.binary.v2+json'},'both parent producer media types')
check('422' in spec('T43R003')['paths']['/consumers/{groupid}']['post']['responses'],'parent invalid-configuration 422')
yaml=parent('T43R004','dockstore-webservice/src/main/resources/openapi3/openapi.yaml')
block=yaml.split('  /ga4gh/trs/v2/tools/{id}/versions/{version_id}/{type}/files:',1)[1].split('\n  /',1)[0]
check('application/zip:' in block and 'name: format' in block and '- zip' in block,'parent TRS zip operation')
yaml=parent('T43R005','dockstore-webservice/src/main/resources/openapi3/openapi.yaml')
block=yaml.split('  /ga4gh/trs/v2/tools/{id}/versions/{version_id}/{type}/files:',1)[1].split('\n  /',1)[0]
check('"404":' in block and 'The tool can not be output in the specified type.' in block,'parent TRS 404 operation')
yaml=parent('T43R006','api/rhsm-subscriptions-api-spec.yaml')
block=yaml.split('  /hosts/products/{product_id}:',1)[1].split('\n  /',1)[0]
for name in ('beginning','ending'):
    parameter=block.split('- name: '+name,1)[1].split('- name:',1)[0]
    check('required: false' in parameter,'parent optional hosts '+name)
yaml=parent('T43R007','api/rhsm-subscriptions-api-v1-spec.yaml')
block=yaml.split('  /v1/tally/products/{product_id}/{metric_id}:',1)[1].split('\n  /',1)[0]
check("'400':" in block and '#/components/schemas/GranularityType' in block,'parent tally invalid input contract')
yaml=parent('T43R008','ext/hivemq-edge-openapi-2025.1-SNAPSHOT.yaml')
block=yaml.split('        persist:',1)[1].split('\n        port:',1)[0]
check('nullable: true' in block,'active parent Bridge.persist nullable')
check('inputSpec.set("${projectDir}/../ext/hivemq-edge-openapi-2025.1-SNAPSHOT.yaml")' in parent('T43R008','hivemq-edge/build.gradle.kts'),'active generated interface input')
java=parent('T43R009','hivemq-edge/src/main/java/com/hivemq/api/resources/ProtocolAdaptersApi.java')
block=java.split('operationId = "get-adapter-domainTags"',1)[1].split('Response getDomainTagsForAdapter(',1)[0]
check('responseCode = "200"' in block and 'DomainTagModelList.class' in block and 'mediaType = APPLICATION_JSON' in block,'parent empty-tags response contract')
check('@OpenApiContent(from = CsvV1Office.class, type = Formats.CSV )' in parent('T43R010','cwms_radar_api/src/main/java/cwms/radar/api/OfficeController.java'),'parent office representation annotation')
yaml=parent('T43R011','src/main/resources/api-specs/payment-openapi.yaml')
check('  /api/v1/payment:' in yaml and '"Session created successfully"' in yaml,'parent payment successful session contract')
java=parent('T43R012','cwms-data-api/src/main/java/cwms/cda/api/location/kind/OutletController.java')
check('associated with the outlets.  Defaults to the user session id.' in java and 'String office = requiredParam(ctx, OFFICE);' in java,'parent outlet discrepancy')

# Privacy checks report locations/categories only, never the matched text.
privacy=[]
data_files=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.csv','.json','.diff','.txt'}]+[BASE/'combined_accepted.csv',BASE/'t43_repo_meta.csv']
for p in data_files:
    value=p.read_text()
    for kind,pattern in [('email',r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'),('private_key_header',r'-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----'),('token',r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|AKIA[A-Z0-9]{16})\b')]:
        if re.search(pattern,value):privacy.append({'path':str(p),'kind':kind})
check(not privacy,'data privacy pattern scan')
raw='-----BEGIN PRIVATE KEY-----\n'+'A'*48+'\n-----END PRIVATE KEY-----\n\n'
safe=m['redact'](raw)
check('A'*48 not in safe and 'BEGIN PRIVATE' not in safe,'multiline key redaction')
check(len(raw.splitlines())==len(safe.splitlines()),'redaction trailing line stability')
for p in ROOT.glob('*.py'):ast.parse(p.read_text(),filename=str(p));checks+=1
for p,digest in json.loads((BASE.parents[1]/'09_collab/logs/T43_scratch/freeze.json').read_text()).items():
    check(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,'frozen prior artifact '+p)
result=dict(passed=True,assertions=checks,candidates=len(rows),reviewed=len(reviewed),accepted=len(acc),combined=len(combined),explicit_parent_contract_checks='pass',original_T42_row_values_preserved=True,privacy_findings=privacy,limits=['No runtime witness or independent semantic adjudication; this audit checks stated structural/parent-source facts.'])
(ROOT/'final_qa.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
