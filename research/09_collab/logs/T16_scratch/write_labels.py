"""Write independently reviewed T16 labels and preserve case-level decisions."""
import collections
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay import OUT,ROOT,RUNS

CHECKER='08_experiments/tools/conformance.py'
PET='08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/'
MARKET='08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/'
REST=MARKET+'market-rest/src/main/java/market/'
DTO=MARKET+'market-core/src/main/java/market/dto/'
ROOTS={
 'swagger-petstore':{
  'RC01':('⚠️ A null-byte setup probe is counted as an undocumented API operation.','test'),
  'RC02':('⚠️ The checker cannot validate XML/form bodies or captured binary input.','test'),
  'RC03':('⚠️ Form construction overwrites the initialized photoUrls list with null; responses omit the required field.','code'),
  'RC04':('[H] Missing optional Pet.id reaches primitive getId unboxing in mutation/storage code.','code'),
  'RC05':('[H] Pet XML/form submissions fail inside binding or mutation; exact throwing sites are unavailable.','code'),
  'RC06':('⚠️ Explicit required-input guards are absent from request constraints.','spec'),
  'RC07':('⚠️ Request validation omits int32/int64 bounds and produces false VALID_REJECTED diagnostics.','test'),
  'RC08':('⚠️ Pet status updates store values outside the enum stated by model annotations and response schema.','code'),
  'RC09':('⚠️ Invalid URI/header input is rejected before business processing, but the oracle declares it valid.','test'),
  'RC10':('[H] The order form overload passes optional wrappers into primitive factory parameters without defaults.','code'),
  'RC11':('[H] A successfully stored null-username user makes later username equality operations fail.','code'),
  'RC12':('⚠️ Login emits an unquoted session string with application/json.','code'),
 },
 'market':{
  'RC01':('⚠️ A null-byte setup probe is counted as an undocumented API operation.','test'),
  'RC02':('⚠️ Advertised _links arrays trigger mapping failures that the catch-all exception handler returns as 500.','code'),
  'RC03':('⚠️ Numeric body/path conversion failures reach the catch-all 500 handler.','code'),
  'RC04':('⚠️ Explicit validation handlers return 406, which the affected operations omit.','spec'),
 },
}
CAT={
 'probe':('TEST','','T-PROBE-CONTAMINATION',3,'RC01'),
 'checker_body_coverage':('TEST','','T-ORACLE-COVERAGE',3,'RC02'),
 'missing_photoUrls':('IMPL','I-RESP-CONTRACT','',2,'RC03'),
 'inferred_null_pet_id':('IMPL','I-CRASH','',3,'RC04'),
 'unresolved_pet_nonJSON_failure':('IMPL','I-CRASH','',3,'RC05'),
 'explicit_required_input_400':('SPEC','S-REQ-LOOSE','',3,'RC06'),
 'oracle_ignored_int64_range':('TEST','','T-ORACLE-NUMERIC-FORMAT',3,'RC07'),
 'oracle_ignored_int32_range':('TEST','','T-ORACLE-NUMERIC-FORMAT',3,'RC07'),
 'status_contract':('IMPL','I-RESP-CONTRACT','',3,'RC08'),
 'transport_rejection':('TEST','','T-TRANSPORT-INPUT',2,'RC09'),
 'inferred_form_wrapper_unboxing':('IMPL','I-CRASH','',3,'RC10'),
 'inferred_null_username_state':('IMPL','I-CRASH','',3,'RC11'),
 'unquoted_JSON_string':('IMPL','I-RESP-CONTRACT','',3,'RC12'),
}
M_CAT={
 'probe':('TEST','','T-PROBE-CONTAMINATION',3,'RC01'),
 'HAL_links_binding':('IMPL','I-CRASH','',3,'RC02'),
 'quantity_int32_overflow':('IMPL','I-CRASH','',3,'RC03'),
 'path_int64_overflow':('IMPL','I-CRASH','',3,'RC03'),
 'explicit_validation_406':('SPEC','S-STATUS','',3,'RC04'),
}
SOURCES={
 'swagger-petstore':{
  'RC01':[f'{CHECKER}:391'],
  'RC02':[f'{CHECKER}:271',f'{CHECKER}:349',f'{CHECKER}:359',f'{CHECKER}:430'],
  'RC03':[PET+'model/Pet.java:32',PET+'model/Pet.java:69',PET+'data/PetData.java:115',PET+'data/PetData.java:121'],
  'RC04':[PET+'model/Pet.java:29',PET+'model/Pet.java:37',PET+'data/PetData.java:103'],
  'RC05':[PET+'controller/PetController.java:199',PET+'controller/PetController.java:227'],
  'RC07':[f'{CHECKER}:21',f'{CHECKER}:89',f'{CHECKER}:326',f'{CHECKER}:434'],
  'RC08':[PET+'model/Pet.java:84',PET+'controller/PetController.java:114',PET+'controller/PetController.java:116'],
  'RC09':[f'{CHECKER}:287',f'{CHECKER}:434'],
  'RC10':[PET+'controller/OrderController.java:71',PET+'controller/OrderController.java:73',PET+'data/OrderData.java:68'],
  'RC11':[PET+'data/UserData.java:53',PET+'data/UserData.java:55',PET+'data/UserData.java:62',PET+'data/UserData.java:65',PET+'data/UserData.java:70',PET+'data/UserData.java:73'],
  'RC12':[PET+'controller/UserController.java:103',PET+'controller/UserController.java:106',PET+'controller/UserController.java:109',PET+'utils/Util.java:14',f'{CHECKER}:419'],
 },
 'market':{
  'RC01':[f'{CHECKER}:391'],
  'RC02':[REST+'rest/exception/RestExceptionHandler.java:37',REST+'rest/exception/RestExceptionHandler.java:38'],
  'RC03':[REST+'rest/exception/RestExceptionHandler.java:37',REST+'rest/exception/RestExceptionHandler.java:38'],
  'RC04':[REST+'rest/exception/RestExceptionHandler.java:63',REST+'rest/exception/RestExceptionHandler.java:73'],
 },
}
GUARDS={
 'P014':PET+'controller/PetController.java:51',
 'P015':PET+'controller/PetController.java:234',
 'P019':PET+'controller/PetController.java:99',
 'P021':PET+'controller/PetController.java:157',
 'P027':PET+'controller/OrderController.java:59',
 'P032':PET+'controller/UserController.java:35',
 'P034':PET+'controller/UserController.java:88',
 'P043':PET+'controller/UserController.java:146',
}
RATIONALES={
 'probe':'The null-byte capability probe targets the base URL and fails HTTP parsing. Counting setup traffic as an undocumented API operation contaminates the sample.',
 'checker_body_coverage':'The checker cannot validate this non-JSON or binary body. This diagnostic records missing coverage; sibling SERVER_ERROR diagnostics retain any observed implementation failure.',
 'missing_photoUrls':"The form factory overwrites the model's initialized photo list with null. Successful responses then omit required photoUrls, including a later search result.",
 'pet_crash':'Observed 500s implicate implementation. JSON witnesses omit optional id, exposing primitive unboxing; exact non-JSON throwing sites remain unresolved without stack traces.',
 'explicit_required_input_400':'Explicit controller guards require the omitted input and return 400. The schema permits absence or an empty list, omitting that implemented requirement.',
 'oracle_ignored_int64_range':'Declared int64 and Long binding exclude every witness ID. The checker omits fixed-width bounds and incorrectly marks these rejected requests valid.',
 'transport_rejection':'HTTP processing rejects invalid URI or header characters before business validation. The checker treats transport-invalid inputs as valid, producing a false rejection diagnostic.',
 'status_contract':'The update stores arbitrary status while model annotations and response schema enumerate three states. Returned statuses violate that contract; the request enum is also absent.',
 'mixed':'Occurrences combine explicit missing-input rejections (SPEC) with numeric-format false positives (TEST). The codebook does not define their aggregation; abstain while retaining case labels.',
 'inferred_form_wrapper_unboxing':'Only form submissions reach these 500s. The form overload unboxes optional wrappers into primitive arguments; R1 establishes IMPL while the exact throwing site remains inferred.',
 'inferred_null_username_state':'An earlier successful empty user enters shared storage; later username equality dereferences lack null guards. Observed 500s establish IMPL; exact per-request causes remain inferred.',
 'unquoted_JSON_string':'The login handler labels a raw session string application/json without JSON quoting. Both captured bodies fail parsing, violating the documented JSON string response.',
 'HAL_links_binding':"A declared _links array reaches Jackson's relation-name mapping failure. The catch-all handler converts input errors to 500; schema shape/direction also warrants review.",
 'market_numeric':'Numeric conversion raises an input-binding exception; the general handler returns 500. Invalid input still requires controlled rejection rather than an implementation server error.',
 'market_mixed':'Link-mapping and int32-overflow errors reach the catch-all 500 handler. This is IMPL; the advertised _links input schema additionally warrants SPEC review.',
 'explicit_validation_406':'Explicit validation handlers return 406 with field errors. The operation omits 406; source annotations independently establish validation intent.',
}

def ptr(value):return value.replace('~','~0').replace('/','~1')

def write_sut(sut,rel):
    spec_path=rel+'/spec.original.json';ex_path=rel+'/exchanges.jsonl';log_path=rel+'/compose.log'
    spec=json.loads((ROOT/spec_path).read_text())
    slocs=json.loads((OUT/f'{sut}_spec_locations.json').read_text())
    maps={r['item_id']:r for r in json.loads((OUT/f'{sut}_exchange_map.json').read_text())}
    log_map=json.loads((OUT/f'{sut}_log_locations.json').read_text())
    cases=json.loads((OUT/f'{sut}_case_audit.json').read_text())
    by_item=collections.defaultdict(list)
    for c in cases:by_item[c['item_id']].append(c)
    items=list(csv.DictReader((ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_blind.csv').open()))
    xs=[json.loads(raw) for raw in (ROOT/ex_path).open()]
    def sl(pointer):return f'{spec_path}:{slocs[pointer]} (JSON Pointer {pointer})'
    def log_locs(n):
        value=log_map.get(str(n),{})
        return [f'{log_path}:{value[k]}' for k in ['error_line','validation_or_notfound_line','proxy_request_line','proxy_response_line',
                   'prefix_corroboration_request_line','prefix_corroboration_response_line'] if k in value]
    labels=[];case_labels=[]
    for item in items:
        iid=item['item_id'];cat_map=CAT if sut=='swagger-petstore' else M_CAT
        categories={c['category'] for c in by_item[iid]}
        decisions={cat_map[c][:3] for c in categories};l1s={d[0] for d in decisions}
        if l1s=={'SPEC','TEST'}:
            l1,l2,proposed,confidence='UNDECIDABLE','','',1;rationale=RATIONALES['mixed']
        else:
            assert len(l1s)==1,(iid,l1s)
            l1=next(iter(l1s));l2s={d[1] for d in decisions};proposals={d[2] for d in decisions}
            assert len(l2s)==len(proposals)==1
            l2=next(iter(l2s));proposed=next(iter(proposals));confidence=min(cat_map[c][3] for c in categories)
            if sut=='swagger-petstore' and item['kind']=='SERVER_ERROR' and item['template']=='/pet':rationale=RATIONALES['pet_crash']
            elif sut=='market' and len(categories)>1:rationale=RATIONALES['market_mixed']
            elif sut=='market' and categories & {'quantity_int32_overflow','path_int64_overflow'}:rationale=RATIONALES['market_numeric']
            else:rationale=RATIONALES[next(iter(categories))]
        rationale='⚠️ '+rationale
        assert len(rationale.split())<=30,(iid,len(rationale.split()))
        roots=sorted({cat_map[c][4] for c in categories})
        op_ptr='/paths/'+ptr(item['template'])+'/'+item['method'].lower()
        first=maps[iid]['exchange_lines'][0]
        locs=[f'{ex_path}:{first}']+log_locs(first)
        if iid in ('P001','M001'):
            locs.append(sl('/paths'))
            locs.append(f'{log_path}:'+str(17 if sut=='swagger-petstore' else 116))
        else:
            locs += [sl(op_ptr),sl(op_ptr+'/responses')]
        for category in sorted(categories):
            sample=next(c for c in by_item[iid] if c['category']==category)
            n=sample['exchange_line'];locs += [f'{ex_path}:{n}']+log_locs(n)
            root=cat_map[category][4];locs += SOURCES[sut].get(root,[])
            if sut=='market' and 'error_line' in log_map.get(str(n),{}):
                locs += [f'{log_path}:{f["line"]}' for f in log_map[str(n)].get('frames',[])[:2]]
        both=False;evidence=['E-OBS','E-LOG']
        if sut=='swagger-petstore':
            if 'RC06' in roots:
                locs.append(GUARDS[iid]);evidence.append('E-CODE-INTENT')
                if op_ptr+'/requestBody' in slocs:locs.append(sl(op_ptr+'/requestBody'))
                if op_ptr+'/parameters' in slocs:locs.append(sl(op_ptr+'/parameters'))
            if 'RC07' in roots:
                if iid=='P043':
                    locs += [sl('/components/schemas/User/properties/userStatus'),PET+'model/User.java:33']
                else:
                    locs.append(sl(op_ptr+'/parameters'));locs.append(PET+'controller/PetController.java:71')
            if 'RC02' in roots:
                locs.append(sl(op_ptr+'/requestBody'));evidence.append('E-CODE-INTENT')
            if 'RC03' in roots:
                locs += [sl('/components/schemas/Pet/required'),PET+'controller/PetController.java:201',PET+'controller/PetController.java:229']
                if iid=='P013':locs += [f'{ex_path}:2',f'{ex_path}:105',PET+'controller/PetController.java:58'];evidence.append('E-CROSS')
                evidence.append('E-CODE-INTENT')
            if 'RC04' in roots or 'RC05' in roots:
                locs += [sl('/components/schemas/Pet/required'),sl('/components/schemas/Pet/properties/id'),PET+'controller/PetController.java:184',PET+'controller/PetController.java:213']
                both=True
            if 'RC08' in roots:
                locs += [sl('/components/schemas/Pet/properties/status'),sl(op_ptr+'/parameters/2')];both=True;evidence.append('E-CODE-INTENT')
            if 'RC11' in roots:
                locs += [f'{ex_path}:952']+log_locs(952)+[sl('/components/schemas/User')]
                if item['method'] in ('POST','PUT'):both=True
            if 'RC12' in roots:
                locs.append(sl(op_ptr+'/responses/200'));evidence.append('E-CODE-INTENT')
            if 'RC04' in roots or 'RC05' in roots or 'RC10' in roots or 'RC11' in roots:evidence.append('E-CONV')
        else:
            if iid!='M001':
                evidence.append('E-CODE-INTENT')
                if '/customer/cart/pay'==item['template']:
                    locs += [REST+'rest/CartRestController.java:113',DTO+'CreditCardDTO.java:10']
                elif '/customer/cart'==item['template']:
                    locs += [REST+'rest/CartRestController.java:75',DTO+'CartItemDTO.java:12',DTO+'CartItemDTO.java:14',DTO+'CartItemDTO.java:18']
                elif '/customer/contacts'==item['template']:
                    locs += [REST+'rest/ContactsRestController.java:50',DTO+'ContactsDTO.java:13',DTO+'ContactsDTO.java:15',DTO+'ContactsDTO.java:20']
                elif '/register'==item['template']:
                    locs += [REST+'rest/CustomerRestController.java:52',DTO+'UserDTO.java:10',DTO+'UserDTO.java:18',DTO+'UserDTO.java:27']
                else:locs.append(REST+'rest/OrdersRestController.java:53')
                if 'RC02' in roots:
                    schema={'/customer/cart':'CartItemDTOReq','/customer/contacts':'ContactsDTOReq','/register':'UserDTOReq'}[item['template']]
                    locs.append(sl('/definitions/'+schema+'/properties/_links'));both=True
                if 'RC03' in roots:
                    if item['template']=='/customer/cart':locs.append(sl('/definitions/CartItemDTOReq/properties/quantity'))
                    else:locs.append(sl(op_ptr+'/parameters/1'))
        if len(maps[iid]['exchange_lines'])>1:evidence.append('E-CONSIST')
        labels.append(dict(item_id=iid,L1=l1,L2=l2,proposed_L2=proposed,confidence=confidence,
                           evidence_types=';'.join(dict.fromkeys(evidence)),evidence_locators=';'.join(dict.fromkeys(locs)),
                           root_cause_id=';'.join(roots),both_candidate=str(both).lower(),rationale=rationale))
        for case in by_item[iid]:
            a,b,c,d,rc=cat_map[case['category']]
            case_labels.append({**case,'L1':a,'L2':b,'proposed_L2':c,'confidence':d,'root_cause_id':rc})
    path=ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_labels_codex.csv'
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(labels[0]));writer.writeheader();writer.writerows(labels)
    root_rows=[]
    for rc,(description,fix_site) in ROOTS[sut].items():
        members=[r['item_id'] for r in labels if rc in r['root_cause_id'].split(';')]
        assert members,rc
        root_rows.append(dict(root_cause_id=rc,description=description,fix_site=fix_site,items=';'.join(members)))
    with (ROOT/f'08_experiments/E2_labelling/{sut}_root_causes_codex.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(root_rows[0]));writer.writeheader();writer.writerows(root_rows)
    (OUT/f'{sut}_case_labels.json').write_text(json.dumps(case_labels,indent=2)+'\n')
    summary={'sut':sut,'L1':dict(collections.Counter(r['L1'] for r in labels)),
             'L2':dict(collections.Counter(r['L2'] or r['proposed_L2'] or '(blank)' for r in labels)),
             'confidence':dict(collections.Counter(r['confidence'] for r in labels)),
             'root_memberships':{r['root_cause_id']:len(r['items'].split(';')) for r in root_rows},
             'multi_cause_items':[r['item_id'] for r in labels if ';' in r['root_cause_id']],
             'both_candidates':[r['item_id'] for r in labels if r['both_candidate']=='true'],
             'mixed_aggregation_gap_items':[r['item_id'] for r in labels if r['L1']=='UNDECIDABLE'],
             'case_L1':dict(collections.Counter(r['L1'] for r in case_labels)),
             'max_rationale_words':max(len(r['rationale'].split()) for r in labels)}
    (OUT/f'{sut}_label_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    for sut,rel in RUNS.items():write_sut(sut,rel)
