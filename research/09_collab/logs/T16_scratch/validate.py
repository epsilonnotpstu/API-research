"""Validate T16 coverage, evidence, aggregation, and observable subcase witnesses."""
import collections
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay import OUT,ROOT,RUNS
sys.path.insert(0,str(ROOT/'08_experiments/tools'))
import conformance

FIELDS=['item_id','L1','L2','proposed_L2','confidence','evidence_types','evidence_locators','root_cause_id','both_candidate','rationale']
files={};result=[]
capabilities={'int32_format_checker_registered':'int32' in conformance.FORMAT_CHECKER.checkers,
              'int64_format_checker_registered':'int64' in conformance.FORMAT_CHECKER.checkers,
              'jsonschema_version':importlib.metadata.version('jsonschema')}
assert not capabilities['int32_format_checker_registered'] and not capabilities['int64_format_checker_registered']
for sut,rel in RUNS.items():
    prefix,count=('P',43) if sut=='swagger-petstore' else ('M',13)
    label_path=ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_labels_codex.csv'
    root_path=ROOT/f'08_experiments/E2_labelling/{sut}_root_causes_codex.csv'
    blind_path=ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_blind.csv'
    with label_path.open(newline='') as f:
        reader=csv.DictReader(f);assert reader.fieldnames==FIELDS;labels=list(reader)
    with root_path.open(newline='') as f:
        reader=csv.DictReader(f);assert reader.fieldnames==['root_cause_id','description','fix_site','items'];roots=list(reader)
    items=list(csv.DictReader(blind_path.open(newline='')))
    assert [r['item_id'] for r in labels]==[r['item_id'] for r in items]==[f'{prefix}{i:03}' for i in range(1,count+1)]
    rootids={r['root_cause_id'] for r in roots}
    maps={r['item_id']:r for r in json.loads((OUT/f'{sut}_exchange_map.json').read_text())}
    cases=json.loads((OUT/f'{sut}_case_labels.json').read_text());by_item=collections.defaultdict(list)
    for case in cases:by_item[case['item_id']].append(case)
    xs=[json.loads(raw) for raw in (ROOT/rel/'exchanges.jsonl').open()]
    log_lines=(ROOT/rel/'compose.log').read_bytes().decode().split('\n')
    log_map=json.loads((OUT/f'{sut}_log_locations.json').read_text())
    locators=0
    for row,item in zip(labels,items):
        iid=row['item_id'];expected=set(maps[iid]['exchange_lines'])
        assert len(expected)==len(by_item[iid])==int(item['occurrences'])
        assert {c['exchange_line'] for c in by_item[iid]}==expected
        assert set(row['root_cause_id'].split(';'))=={c['root_cause_id'] for c in by_item[iid]}<=rootids
        l1s={c['L1'] for c in by_item[iid]}
        assert row['L1']==('UNDECIDABLE' if l1s=={'SPEC','TEST'} else next(iter(l1s)))
        assert row['both_candidate'] in ('true','false')
        assert row['confidence'] in ('1','2','3')
        assert row['rationale'].startswith('⚠️') and len(row['rationale'].split())<=30
        if row['L1']=='TEST':assert row['L2']=='' and row['proposed_L2'].startswith('T-')
        if row['L1']=='UNDECIDABLE':assert row['L2']==row['proposed_L2']=='' and row['confidence']=='1'
        if item['kind']=='REQUEST_UNCHECKABLE':
            assert row['L1']=='TEST' and row['proposed_L2']=='T-ORACLE-COVERAGE'
            for n in expected:
                x=xs[n-1];oracle=conformance.Spec(json.loads((ROOT/rel/'spec.original.json').read_text()))
                t,pp=oracle.match(x['request']['path'],x['request']['method'],x['request'].get('origin'))
                op,params=oracle.operation(t,x['request']['method'])
                rp=conformance.request_problems(oracle,params,op,x,pp)
                assert rp.uncheckable
                if item['status']=='500':
                    assert any(c['exchange_line']==n and c['L1']=='IMPL' and c['L2']=='I-CRASH' for c in cases)
        for locator in row['evidence_locators'].split(';'):
            m=re.fullmatch(r'(.+):(\d+)(?: \(JSON Pointer (.*)\))?',locator);assert m,locator
            name,line=m[1],int(m[2]);assert 'labels_A' not in name and '/runs/scout-api/' not in name
            path=ROOT/name;assert path.is_file(),locator
            if name not in files:files[name]=path.read_bytes()
            lines=files[name].split(b'\n');assert 1<=line<=len(lines) and lines[line-1].strip(),locator
            if m[3] is not None:
                node=json.loads(files[name]);pointer=m[3]
                for part in pointer.lstrip('/').split('/'):
                    part=part.replace('~1','/').replace('~0','~')
                    node=node[int(part)] if isinstance(node,list) else node[part]
            locators+=1
    for root in roots:
        assert root['fix_site'] in ('spec','code','test','env')
        assert root['description'].startswith(('⚠️','[H]'))
        assert root['items'].split(';')==[r['item_id'] for r in labels if root['root_cause_id'] in r['root_cause_id'].split(';')]
    # Direct subcase checks independent of label-writing code.
    for case in cases:
        n=case['exchange_line'];x=xs[n-1];category=case['category']
        if category=='oracle_ignored_int64_range':
            segment=x['request']['path'].split('/')[-2 if x['request']['path'].endswith('/uploadImage') else -1]
            assert not -(2**63)<=int(segment)<2**63
        elif category in ('oracle_ignored_int32_range','quantity_int32_overflow'):
            body=json.loads(x['request']['body']['text']);value=body['userStatus' if sut=='swagger-petstore' else 'quantity']
            assert not -(2**31)<=value<2**31
        elif category=='path_int64_overflow':
            assert not -(2**63)<=int(x['request']['path'].rsplit('/',1)[-1])<2**63
        elif category=='transport_rejection':
            if case['item_id']=='P022':assert any(ord(c)<32 or ord(c)==127 for c in x['request']['headers']['api_key'])
            else:assert '\\' in unquote(x['request']['path']) and 'Invalid URI' in x['response']['body']['text']
        elif category=='HAL_links_binding':
            message=json.loads(x['response']['body']['text'])['message']
            assert 'Expected relation name' in message and '_links' in message
            assert isinstance(json.loads(x['request']['body']['text'])['_links'],list)
        elif category=='explicit_validation_406':
            response=json.loads(x['response']['body']['text']);assert response['fieldErrors'] and x['response']['status']==406
            assert 'WARN' in log_lines[log_map[str(n)]['validation_or_notfound_line']-1]
        elif category=='inferred_null_pet_id':
            assert 'id' not in json.loads(x['request']['body']['text'])
        elif category=='unquoted_JSON_string':
            assert 'application/json' in x['response']['headers'].get('content-type','')
            try:json.loads(x['response']['body']['text'])
            except ValueError:pass
            else:raise AssertionError('login body unexpectedly parses')
    first=xs[0];assert first['request']['headers']['x-schemathesis-probe']=='NULL_BYTE_IN_HEADER'
    assert first['request']['headers']['x-schemathesis-probe-null']=='\x00'
    if sut=='swagger-petstore':
        poisoned=xs[951];assert poisoned['response']['status']==200 and json.loads(poisoned['request']['body']['text'])=={}
        assert json.loads(poisoned['response']['body']['text']).get('username') is None
    else:
        for n,x in enumerate(xs,1):
            if x['response']['status']==500:
                assert 'ERROR' in log_lines[log_map[str(n)]['error_line']-1]
    for path in [blind_path,label_path,root_path,ROOT/rel/'exchanges.jsonl',ROOT/rel/'spec.original.json',ROOT/rel/'compose.log',ROOT/rel/'generator-input.json']:
        files[str(path.relative_to(ROOT))]=path.read_bytes()
    result.append({'sut':sut,'status':'PASS','items':count,'L1':dict(collections.Counter(r['L1'] for r in labels)),
                   'evidence_locators_checked':locators,'diagnostic_cases':len(cases),
                   'root_rows':len(roots),'both_candidates':sum(r['both_candidate']=='true' for r in labels),
                   'max_rationale_words':max(len(r['rationale'].split()) for r in labels),
                   'error_log_joins_by_URI_category_order':sum('error_line' in x for x in log_map.values()),
                   'proxy_exact_URI_matches':sum('proxy_request_line' in x for x in log_map.values()),
                   'proxy_prefix_corroborations':sum('prefix_corroboration_request_line' in x for x in log_map.values()),
                   'application_ERROR_lines':sum('ERROR' in x and x.startswith('sut-') for x in log_lines)})
manifest={name:hashlib.sha256(value).hexdigest() for name,value in files.items()}
for name in ['08_experiments/tools/conformance.py','08_experiments/tools/specmut.py','08_experiments/R1_triage_codebook.md','09_collab/tasks/T16.md']:
    manifest[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
(OUT/'sha256_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(OUT/'oracle_capabilities.json').write_text(json.dumps(capabilities,indent=2)+'\n')
summary={'status':'PASS','SUTs':result,'evidence_files_checked':len(files),'oracle_capabilities':capabilities,
         'blinding':{'labels_A_opened':False,'interpretation_reports_opened':False,'board_not_used_as_label_evidence':True},
         'external_execution':False}
(OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
