"""Four small synthetic fault-class spot checks using only repository checker/mutator."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import attribute
import conformance as c
import specmut

OUT = Path(__file__).resolve().parent


def document(request=None, response=None, version='3.0.3'):
    op = {'responses': {'200': {'description': 'ok', 'content': {'application/json': {
        'schema': response or {'type': 'object', 'properties': {'id': {'type': 'integer'}}}}}},
                        '400': {'description': 'bad request'}, '500': {'description': 'error'}}}
    if request:
        op['requestBody'] = {'required': True, 'content': {'application/json': {'schema': request}}}
    return {'openapi': version, 'info': {'title': 'synthetic', 'version': '1'}, 'paths': {'/x': {'get': op}}}


def exchange(method='GET', status=200, request=None, response=None, content_type='application/json'):
    return {'request': {'method': method, 'path': '/x', 'headers': {'Content-Type': 'application/json'},
                        'query': {}, 'body': {'text': json.dumps(request) if request is not None else ''}},
            'response': {'status': status, 'headers': {'Content-Type': content_type},
                         'body': {'text': json.dumps(response) if response is not None else '{}'}}}


def compare(name, spec, fault, baseline, mutated=None):
    ms, edits, _ = specmut.mutate(spec, fault, 100, 1)
    manifest = {'mutations': edits}
    bv = [v for e in baseline for v in c.check(c.Spec(spec), e)]
    rv = [v for e in baseline for v in c.check(c.Spec(ms), e)]
    mv = [v for e in mutated for v in c.check(c.Spec(ms), e)] if mutated is not None else rv
    def concise(values):
        return [{'kind': v['kind'], 'method': v['method'], 'status': v['status'], 'pointer': v['pointer']} for v in values]
    def diff(values, mode):
        return [{k: v[k] for k in ('kind', 'method', 'http_status', 'pointer', 'status', 'op_mutated')}
                for v in attribute.attribute(bv, values, manifest, mode)]
    return {'case': name, 'fault': fault, 'baseline': concise(bv), 'replay': concise(rv), 'fresh': concise(mv),
            'replay_diff': diff(rv, 'replay'), 'fresh_diff': diff(mv, 'fresh')}


results = []
# Spot-check group 1: loosening can create VALID_REJECTED while surviving violations remain.
s = document({'type': 'object', 'properties': {'name': {'type': 'string', 'minLength': 3}}, 'required': ['name']})
results.append(compare('loose_rejected_newly_valid', s, 'REQUEST_LOOSE', [exchange(status=400, request={'name': 'a'})]))
results.append(compare('loose_different_traffic_surviving_type_error', s, 'REQUEST_LOOSE',
                       [exchange(request={'name': 'abc'})], [exchange(request={'name': 12})]))
# OAS 3.1 $ref-sibling inlining changes identity of a surviving type violation.
s31 = document({'type': 'object', 'properties': {'name': {'$ref': '#/components/schemas/Name', 'minLength': 1}}}, version='3.1.0')
s31['components'] = {'schemas': {'Name': {'type': 'string', 'pattern': '^a'}}}
results.append(compare('loose_replay_identity_shift', s31, 'REQUEST_LOOSE', [exchange(request={'name': 12})]))

# Spot-check group 2: STRICT creates INVALID_ACCEPTED on exactly the same successful exchange.
results.append(compare('strict_maxlength', document({'type': 'string'}), 'REQUEST_STRICT',
                       [exchange(request='abc')]))

# Spot-check group 3: ORACLE's removed documented 500 adds UNDOCUMENTED_STATUS, not SERVER_ERROR NEW.
results.append(compare('oracle_500_and_response_schema', document(), 'RESPONSE_ORACLE',
                       [exchange(status=500), exchange(response={'extra': 1})]))
sdefault = document()
sdefault['paths']['/x']['get']['responses']['default'] = {'description': 'fallback'}
results.append(compare('oracle_default_covers_removed_500', sdefault, 'RESPONSE_ORACLE', [exchange(status=500)]))

# Spot-check group 4: METHOD_SEM moves the full request and response contract to POST.
# Synthetic captures model target-method behavior; no SUT/external code is executed.
sm = document({'type': 'object', 'properties': {'id': {'type': 'integer'}}, 'required': ['id']})
results.append(compare('method_response_and_request_contract', sm, 'METHOD_SEM',
                       [exchange(request={'id': 1}, response={'id': 1})],
                       [exchange(method='POST', request={'id': 'bad'}, response={'id': 'bad'}),
                        exchange(method='POST', status=405, request={'id': 1}),
                        exchange(method='POST', status=400, request={'id': 1})]))
results.append(compare('method_documented_error_and_bad_response_media', sm, 'METHOD_SEM',
                       [exchange(request={'id': 1}, response={'id': 1})],
                       [exchange(method='POST', status=500, request={'id': 1}),
                        exchange(method='POST', request={'id': 1}, response={'id': 1}, content_type='text/plain')]))

assert any(v['kind'] == 'VALID_REJECTED' and v['status'] == 'NEW' for v in results[0]['replay_diff'])
assert any(v['kind'] == 'INVALID_ACCEPTED' and v['status'] == 'NEW' for v in results[2]['replay_diff'])
assert any(v['kind'] == 'INVALID_ACCEPTED' and v['status'] == 'NEW' for v in results[3]['replay_diff'])
oracle = {v['kind']: v['status'] for v in results[4]['replay_diff']}
assert oracle['SERVER_ERROR'] == 'PERSISTENT' and oracle['UNDOCUMENTED_STATUS'] == 'NEW'
assert not any(v['status'] == 'NEW' for v in results[5]['replay_diff'])
assert {v['kind'] for v in results[6]['replay']} == {'UNDOCUMENTED_OPERATION'}
assert {'RESPONSE_SCHEMA', 'INVALID_ACCEPTED', 'UNDOCUMENTED_STATUS', 'VALID_REJECTED'} <= {v['kind'] for v in results[6]['fresh']}
(OUT / 'mechanisms.json').write_text(json.dumps({'spot_check_groups': 4, 'cases': results}, indent=2) + '\n')
print(json.dumps({'groups': 4, 'cases': len(results), 'assertions': 'PASS',
                  'loose_identity_shift': results[2]['replay_diff'], 'method_fresh': results[6]['fresh']}, indent=2))
