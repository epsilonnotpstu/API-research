"""Materialize independently reviewed decisions from the blind evidence index."""
import collections
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN_REL = '08_experiments/E1_pilot/runs/scout-api/20261113T202103Z_baseline_NONE_p0_s1_1642810'
SRC = '08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/'
RES = SRC + 'api/src/main/java/se/devscout/scoutapi/resource/'
MODEL = SRC + 'data-access/src/main/java/se/devscout/scoutapi/model/'
DAO = SRC + 'data-access/src/main/java/se/devscout/scoutapi/dao/'
CHECKER = '08_experiments/tools/conformance.py'
SPEC = RUN_REL + '/spec.original.json'
EXCHANGES = RUN_REL + '/exchanges.jsonl'
LOG = RUN_REL + '/compose.log'
items = list(csv.DictReader((ROOT / '08_experiments/E2_labelling/batch2_baseline_s1_blind.csv').open()))
maps = {r['item_id']: r for r in json.loads((OUT / 'exchange_map.json').read_text())}
logs = {r['item_id']: r for r in json.loads((OUT / 'log_map.json').read_text())}
access = json.loads((OUT / 'request_log_map.json').read_text())
locations = json.loads((OUT / 'spec_locations.json').read_text())
xs = [json.loads(raw) for raw in (ROOT / EXCHANGES).open()]
raw_spec = json.loads((ROOT / SPEC).read_text())

# Root-cause mechanisms are shared across operations, not independent bug counts.
# A fingerprint can contain several mechanisms; semicolons preserve membership.
causes = {
 'RC01': ('A Schemathesis null-byte setup probe is included as an undocumented API operation.', 'test'),
 'RC02': ('Missing Activity lookup is dereferenced by activity mutation/deletion or rating-key construction.', 'code'),
 'RC03': ('Missing MediaFile lookup reaches unchecked update, delete, or download code.', 'code'),
 'RC04': ('Missing SystemMessage lookup reaches unchecked update or ORM deletion.', 'code'),
 'RC05': ('Missing Tag lookup reaches unchecked tag/category update or ORM deletion.', 'code'),
 'RC06': ('Missing User lookup reaches unchecked update or ORM deletion.', 'code'),
 'RC07': ('Absent JSON request bodies reach unchecked resource, model, or persistence calls.', 'code'),
 'RC08': ('Required persistent fields are not validated before dereference or NOT NULL database enforcement.', 'code'),
 'RC09': ('Client-supplied generated IDs reach persist as updates to nonexistent rows, causing stale-state failures.', 'code'),
 'RC10': ('Favourites POST dereferences an absent id list instead of validating the request.', 'code'),
 'RC11': ('The explicitly unsupported my_favourites filter throws WebApplicationException without a non-500 status.', 'code'),
 'RC12': ('Empty activity-search tokens reach charAt(0) without an emptiness guard.', 'code'),
 'RC13': ('Mutation operations document only 200 and omit the consistently observed JSON-binding 400 response.', 'spec'),
 'RC14': ('Mutation operations omit the 404 response observed when path IDs cannot bind to Java long.', 'spec'),
 'RC15': ('User creation omits the 403 authorization rejection explicitly implemented and required by developer test source.', 'spec'),
 'RC16': ('Required path parameter id is declared on profile/favourites routes that contain no id placeholder.', 'spec'),
 'RC17': ('Activity search declares unrestricted strings where the explicit parser requires numeric lists.', 'spec'),
 'RC18': ('[H] Open request schemas and JSON binding disagree; unknown-property/date/range intent and repair site remain unresolved.', ''),
}

root_sources = {
 'RC02': [DAO + 'ActivityDao.java:156', DAO + 'ActivityDao.java:167', DAO + 'ActivityDao.java:219', MODEL + 'ActivityRating.java:90'],
 'RC03': [RES + 'MediaFileResource.java:295', RES + 'MediaFileResource.java:96', RES + 'MediaFileResource.java:260', DAO + 'MediaFileDao.java:22'],
 'RC04': [RES + 'SystemMessageResource.java:102', DAO + 'SystemMessageDao.java:21', DAO + 'SystemMessageDao.java:41'],
 'RC05': [RES + 'TagResource.java:85', DAO + 'TagDao.java:21', DAO + 'TagDao.java:72'],
 'RC06': [RES + 'UserResource.java:100', DAO + 'UserDao.java:25', DAO + 'UserDao.java:48'],
 'RC09': [MODEL + 'SystemMessage.java:37', MODEL + 'User.java:36'],
 'RC10': [RES + 'v1/FavouritesResourceV1.java:66', RES + 'v1/FavouritesResourceV1.java:84'],
 'RC11': [RES + 'ActivityResourceV2.java:76', RES + 'v1/ActivityResourceV1.java:74'],
 'RC12': [DAO + 'ActivityDao.java:65', DAO + 'ActivityDao.java:68'],
}

def ptr(path):
    return path.replace('~', '~0').replace('/', '~1')

def sl(pointer):
    return f'{SPEC}:{locations[pointer]} (JSON Pointer {pointer})'

def no_body(x):
    return x['request']['body']['text'].strip() in ('', 'null')

def classify_error(error):
    x = xs[error['exchange_line'] - 1]
    text = '\n'.join(v for _, v in error['exceptions'] + error['project_frames'])
    if 'NULL not allowed' in text:
        return 'RC08'
    if 'StaleStateException' in text or 'OptimisticLockException' in text:
        return 'RC09'
    if 'ActivityDao.update' in text or 'ActivityDao.delete' in text or 'ActivityRating$Key.<init>' in text:
        return 'RC02'
    if 'Activity.addAndPublish' in text:
        assert no_body(x)
        return 'RC07'
    if 'ActivityResource.postRating' in text:
        assert no_body(x)
        return 'RC07'
    if 'MediaFileResource.update' in text:
        return 'RC07' if no_body(x) else 'RC03'
    if 'MediaFileResource.downloadFile' in text or 'MediaFileDao.delete' in text:
        return 'RC03'
    if 'MediaFileResource.create' in text:
        return 'RC07' if no_body(x) else 'RC08'
    if 'SystemMessageResource.update' in text:
        return 'RC07' if no_body(x) else 'RC04'
    if 'SystemMessageDao.delete' in text:
        return 'RC04'
    if 'TagResource.update' in text:
        return 'RC07' if no_body(x) else 'RC05'
    if 'TagDao.delete' in text:
        return 'RC05'
    if 'UserResource.assertAuthorizationLevel' in text:
        assert no_body(x)
        return 'RC07'
    if 'UserResource.update' in text:
        return 'RC06'
    if 'UserDao.delete' in text:
        return 'RC06'
    if 'SystemMessageDao.create' in text or 'TagDao.create' in text:
        assert no_body(x)
        return 'RC07'
    if 'FavouritesResourceV1.put' in text:
        return 'RC10'
    if 'StringIndexOutOfBoundsException' in text and 'ActivityDao.' in text:
        return 'RC12'
    raise AssertionError((error['exchange_line'], text))

def model_for(item):
    path = item['template']
    if 'rating' in path:
        return 'ActivityRatingAttrs'
    if 'activities' in path:
        return 'ActivityProperties'
    if 'media_files' in path:
        return 'MediaFile'
    if 'system_messages' in path:
        return 'SystemMessage'
    if 'tags' in path or 'categories' in path:
        return 'Tag'
    if 'users' in path:
        return 'User'
    if 'favourites' in path:
        return 'PutFavouritesEntity'
    raise AssertionError(item)

def resource_site(item):
    path, method = item['template'], item['method']
    if path.startswith('/v2/activities'):
        line = {'PUT':174, 'PATCH':185, 'POST':152 if 'rating' in path else 112,
                'GET':138 if 'rating' in path else 35, 'DELETE':163 if 'rating' in path else 103}[method]
        return RES + f'ActivityResourceV2.java:{line}'
    if path.startswith('/v1/activities'):
        line = {'PUT':173, 'PATCH':184, 'POST':151 if 'rating' in path else 111,
                'GET':137 if 'rating' in path else 39, 'DELETE':162 if 'rating' in path else 102}[method]
        return RES + f'v1/ActivityResourceV1.java:{line}'
    if 'media_files' in path:
        return RES + 'MediaFileResource.java:' + str({'PUT':291,'POST':104,'GET':251,'DELETE':83}[method])
    if 'system_messages' in path:
        return RES + 'SystemMessageResource.java:' + str({'PUT':98,'POST':76,'DELETE':68}[method])
    if 'tags' in path or 'categories' in path:
        return RES + 'TagResource.java:' + str({'PUT':81,'POST':59,'DELETE':51}[method])
    if 'users' in path:
        return RES + 'UserResource.java:' + str({'PUT':94,'POST':59,'GET':84,'DELETE':51}[method])
    if 'favourites' in path:
        return RES + 'v1/FavouritesResourceV1.java:' + str(46 if method == 'GET' else 55)
    raise AssertionError(item)

def required_field_evidence(item):
    model = model_for(item)
    annotation_lines = {'ActivityRatingAttrs':15, 'MediaFile':51, 'SystemMessage':40, 'Tag':37, 'User':43}
    result = []
    if model in annotation_lines:
        result += [MODEL + f'{model}.java:{annotation_lines[model]}', sl('/definitions/' + model)]
    if model == 'Tag':
        result += [MODEL + 'Tag.java:41', MODEL + 'MediaFile.java:51', sl('/definitions/MediaFile')]
    if model == 'SystemMessage':
        result.append(MODEL + 'SystemMessage.java:44')
    return result

rationales = {
 'RC02': 'Missing activity lookup reaches an unchecked dereference. Logged NullPointerException establishes an implementation crash; status-only diagnostics share the same cause.',
 'RC03': 'Missing media lookup reaches unchecked update, download, or deletion code. The logged exception establishes an implementation failure.',
 'RC04': 'Missing system-message lookup reaches unchecked update or ORM deletion. The saved stack trace establishes an implementation failure.',
 'RC05': 'Missing tag lookup reaches unchecked update or deletion. The saved stack trace establishes an implementation failure.',
 'RC06': 'Missing user lookup reaches unchecked update or deletion. The saved stack trace establishes an implementation failure.',
 'RC07': 'An absent request body reaches unchecked object or persistence code and produces a logged exception. The 500 is an implementation failure.',
 'RC08': 'Required persistent fields reach unchecked dereference or database enforcement. Missing schema requirements are independently supported; implementation still mishandles the input with 500.',
 'RC10': 'An omitted favourites id list is dereferenced at forEach. The implementation crashes; the same operation also contains an impossible required path parameter.',
}

rows = []
cases = []
for item in items:
    iid, kind, status = item['item_id'], item['kind'], item['status']
    mapped = maps[iid]
    first = mapped['exchange_lines'][0]
    locs = [f'{EXCHANGES}:{first}']
    if str(first) in access:
        locs.append(f'{LOG}:{access[str(first)]["access_log_line"]}')
    op_ptr = '/paths/' + ptr(item['template']) + '/' + item['method'].lower()
    if iid != 'B001':
        locs += [sl(op_ptr), sl(op_ptr + '/responses'), resource_site(item)]
    evidence = ['E-OBS', 'E-LOG']
    roots = set()
    both = False
    proposed = ''
    l2 = ''
    if status == '500':
        l1, l2, confidence = 'IMPL', 'I-CRASH', 3
        evidence.append('E-CODE-INTENT')
        examples = {}
        for error in logs.get(iid, {}).get('errors', []):
            root = classify_error(error)
            roots.add(root)
            examples.setdefault(root, error)
            cases.append({'item_id': iid, 'exchange_line': error['exchange_line'],
                          'root_cause_id': root, 'log_line': error['log_line']})
        for sample in mapped['response_signatures']:
            if sample['response_error'].get('message') == 'API currently does not support filtering on your own favourites.':
                roots.add('RC11')
                examples['RC11'] = {'exchange_line': sample['line'], 'log_line': access[str(sample['line'])]['access_log_line'], 'project_frames': []}
                cases += [{'item_id': iid, 'exchange_line': n, 'root_cause_id': 'RC11',
                           'log_line': access[str(n)]['access_log_line']}
                          for n in mapped['exchange_lines']
                          if json.loads(xs[n-1]['response']['body']['text']).get('message') == sample['response_error']['message']]
        assert roots, iid
        for root, error in examples.items():
            locs += [f'{EXCHANGES}:{error["exchange_line"]}', f'{LOG}:{error["log_line"]}']
            for frame_line, frame in error['project_frames'][:2]:
                locs.append(f'{LOG}:{frame_line}')
                # Convert the logged Java frame into an exact repository locator.
                if '(' in frame and '.java:' in frame:
                    package_class = frame.split('at ',1)[1].split('(',1)[0].rsplit('.',1)[0].split('$',1)[0]
                    filename, line = frame.rsplit('(',1)[1].rstrip(')').rsplit(':',1)
                    module = 'data-access' if '.dao.' in package_class or '.model.' in package_class else 'api'
                    java = SRC + module + '/src/main/java/' + package_class.replace('.', '/') + '.java'
                    assert (ROOT / java).exists(), java
                    locs.append(java + ':' + line)
            locs += root_sources.get(root, [])
        both = bool(roots & {'RC08','RC09','RC10','RC11'})
        if 'RC08' in roots:
            locs += required_field_evidence(item)
        if 'RC09' in roots:
            locs.append(sl('/definitions/' + model_for(item) + '/properties/id'))
        if 'RC10' in roots:
            locs += [sl(op_ptr + '/parameters/0'), sl('/definitions/PutFavouritesEntity')]
        if 'RC11' in roots:
            own_param = next(n for n,p in enumerate(raw_spec['paths'][item['template']]['get']['parameters']) if p['name']=='my_favourites')
            locs.append(sl(op_ptr + f'/parameters/{own_param}'))
        if len(roots) == 1:
            rationale = rationales[next(iter(roots))]
        elif 'RC11' in roots:
            rationale = 'Unsupported favourite filtering defaults to 500; empty search tokens also crash. Both mechanisms violate error-handling intent; advertising unsupported filtering additionally warrants SPEC review.'
        elif 'rating' in item['template']:
            rationale = 'Missing activity, absent body, and omitted favourite trigger distinct unchecked failures. All observed 500 responses implicate implementation; the persistent favourite requirement additionally warrants SPEC review.'
        else:
            rationale = 'Saved stack traces expose multiple unchecked lookup, body, or persistence failures. All observed 500 responses implicate implementation; independently omitted constraints are flagged for SPEC review.'
    elif iid == 'B001':
        l1, confidence, proposed = 'TEST', 3, 'T-PROBE-CONTAMINATION'
        roots = {'RC01'}
        locs += [f'{LOG}:1314', sl('/basePath'), sl('/paths'), f'{CHECKER}:391']
        rationale = 'The NULL_BYTE_IN_HEADER setup probe targets the base URL and is rejected by Jetty before routing. Counting it as an undocumented API operation contaminates the sample.'
    elif kind == 'INVALID_ACCEPTED':
        l1, l2, confidence = 'SPEC', 'S-STRUCT', 3
        roots = {'RC16'}
        evidence += ['E-CODE-INTENT','E-CONSIST']
        locs += [sl(op_ptr + '/parameters/0'), f'{CHECKER}:318']
        rationale = 'The route has no id placeholder; source ignores its stray PathParam argument. Successful profile/favourites behavior is intentional. Remove the impossible required path parameter from the spec.'
    elif kind == 'UNDOCUMENTED_STATUS':
        l1, l2 = 'SPEC', 'S-STATUS'
        confidence = 3 if status == '403' else 2
        evidence.append('E-CONSIST')
        locs.append(f'{CHECKER}:401')
        if status == '400':
            roots = {'RC13'}
            locs.append(sl('/definitions/' + model_for(item)))
            rationale = 'JSON binding consistently returns 400 while the operation documents only 200. The validation response is missing; the separate acceptance-policy diagnostic remains unresolved.'
        elif status == '404':
            roots = {'RC14'}
            locs.append(sl(op_ptr + '/parameters/0'))
            evidence.append('E-CODE-INTENT')
            rationale = 'All witnesses use IDs outside Java long range. Path binding returns 404 before the resource executes; the operation omits this rejection response.'
        elif status == '403':
            roots = {'RC15'}
            evidence.append('E-CODE-INTENT')
            locs += [RES + 'UserResource.java:125', RES + 'UserResource.java:127',
                     SRC + 'api/src/test/java/se/devscout/scoutapi/UsersIntegrationTest.java:59',
                     SRC + 'api/src/test/java/se/devscout/scoutapi/UsersIntegrationTest.java:64']
            rationale = 'Source explicitly forbids granting authorization above the caller; a developer test requires 403. The operation documents only 200, omitting this intended rejection.'
        else:
            raise AssertionError(item)
    elif kind == 'VALID_REJECTED' and item['method'] == 'GET':
        l1, l2, confidence = 'SPEC', 'S-REQ-LOOSE', 3
        roots = {'RC17'}
        evidence += ['E-CODE-INTENT','E-CONSIST']
        locs += [RES + 'ActivityResource.java:47', RES + 'ActivityResource.java:54', f'{CHECKER}:434']
        for n,p in enumerate(raw_spec['paths'][item['template']]['get']['parameters']):
            if p['name'] in ('categories','ages','participants','durations','id','age_1','age_2','time_1','time_2'):
                locs.append(sl(op_ptr + f'/parameters/{n}'))
        rationale = 'Explicit numeric-list parsing deliberately rejects these filters with 400. The schema admits arbitrary strings, omitting the documented numeric grammar and bounds.'
    elif kind == 'VALID_REJECTED':
        l1, confidence = 'UNDECIDABLE', 1
        roots = {'RC18'}
        declaration = {'ActivityProperties':25,'ActivityRatingAttrs':10,'MediaFile':39,
                       'SystemMessage':34,'Tag':31,'User':33}[model_for(item)]
        locs += [sl('/definitions/' + model_for(item)), f'{CHECKER}:434',
                 MODEL + model_for(item) + f'.java:{declaration}']
        rationale = 'Open object schemas admit these inputs; the JSON binding boundary rejects them. No decisive policy evidence establishes whether spec or implementation needs repair.'
    else:
        raise AssertionError(item)
    roots = sorted(roots)
    locs = list(dict.fromkeys(locs))
    rationale = '⚠️ ' + rationale
    assert len(rationale.split()) <= 30, (iid, len(rationale.split()))
    rows.append(dict(item_id=iid,L1=l1,L2=l2,proposed_L2=proposed,confidence=confidence,
                     evidence_types=';'.join(dict.fromkeys(evidence)),evidence_locators=';'.join(locs),
                     root_cause_id=';'.join(roots),both_candidate=str(both).lower(),rationale=rationale))

label_path = ROOT / '08_experiments/E2_labelling/batch2_baseline_s1_labels_codex.csv'
with label_path.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
root_rows = []
for rc,(description,fix_site) in causes.items():
    members = [row['item_id'] for row in rows if rc in row['root_cause_id'].split(';')]
    assert members, rc
    description = description if description.startswith('[H]') else '⚠️ ' + description
    root_rows.append(dict(root_cause_id=rc,description=description,fix_site=fix_site,items=';'.join(members)))
with (ROOT / '08_experiments/E2_labelling/batch2_root_causes_codex.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(root_rows[0]))
    writer.writeheader()
    writer.writerows(root_rows)
(OUT / 'case_root_causes.json').write_text(json.dumps(cases,indent=2)+'\n')
summary = {'L1':dict(collections.Counter(r['L1'] for r in rows)),
           'L2':dict(collections.Counter(r['L2'] or '(blank)' for r in rows)),
           'confidence':dict(collections.Counter(r['confidence'] for r in rows)),
           'root_causes':{r['root_cause_id']:len(r['items'].split(';')) for r in root_rows},
           'multi_cause_items':[r['item_id'] for r in rows if ';' in r['root_cause_id']],
           'both_candidates':[r['item_id'] for r in rows if r['both_candidate']=='true']}
(OUT / 'label_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
