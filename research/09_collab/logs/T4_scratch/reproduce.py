"""Read-only T4 review reproductions; all generated artifacts stay in this directory.

Run: /usr/bin/python3 -I -B 09_collab/logs/T4_scratch/reproduce.py
Each assertion confirms an observed defect, not correct implementation behavior.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import os

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
sys.path.insert(0, str(ROOT / '08_experiments/E1_pilot'))
import attribute
import conformance
import p001_oas_analysis as p001
import specmut
import test_pipeline
import test_specmut

COUNT = 0


def record(case, fixture, expected, actual, observed):
    global COUNT
    assert observed, (case, actual)
    COUNT += 1
    print(json.dumps({'id': case, 'input': fixture, 'expected': expected,
                      'actual': actual, 'observation_confirmed': True}, sort_keys=True))


def document(schema=None, parameters=None, request_body=None, version='3.0.3', content=None):
    response = {'description': 'ok'}
    if content is not None:
        response['content'] = content
    elif schema is not None:
        response['content'] = {'application/json': {'schema': schema}}
    op = {'responses': {'200': response}}
    if parameters is not None:
        op['parameters'] = parameters
    if request_body is not None:
        op['requestBody'] = request_body
    return {'openapi': version, 'info': {'title': 'T4', 'version': '1'}, 'paths': {'/x': {'get': op}}}


def exchange(body='{}', request_text='', status=200, query=None, headers=None, path='/x', method='GET'):
    return {'request': {'method': method, 'path': path, 'query': query or {},
                        'headers': headers or {}, 'body': {'text': request_text, 'truncated': False}},
            'response': {'status': status, 'headers': {'content-type': 'application/json'},
                         'body': {'text': body, 'truncated': False}}}


def kinds(doc, ex):
    return [v['kind'] for v in conformance.check(conformance.Spec(doc), ex)]


def error_list(schema, instance, oas=True):
    return [e.message for e in conformance.validator(schema, oas).iter_errors(instance)]


def query_param(schema, **extra):
    return dict({'name': 'q', 'in': 'query', 'schema': schema}, **extra)


# C01: null, missing bodies, malformed requests, and partial observations.
doc = document({'type': 'object'})
actual = kinds(doc, exchange(body='null'))
record('C01_response_null', {'spec': doc, 'exchange': exchange(body='null')},
       ['RESPONSE_SCHEMA'], actual, actual == [])
rb = {'required': True, 'content': {'application/json': {'schema': {'type': 'object'}}}}
for name, text in [('missing', ''), ('malformed', '{'), ('null', 'null')]:
    doc = document(request_body=rb)
    actual = kinds(doc, exchange(request_text=text))
    record('C01_request_' + name, {'requestBody': rb, 'body': text, 'status': 200},
           ['INVALID_ACCEPTED'], actual, actual == [])
ex = exchange(request_text='{"a":', status=400)
ex['request']['body']['truncated'] = True
actual = kinds(doc, ex)
record('C01_truncated_request', ex, 'INCOMPLETE, no VALID_REJECTED verdict', actual,
       actual == ['UNDOCUMENTED_STATUS', 'VALID_REJECTED'])

# C02: OpenAPI 3.1 requires a different JSON Schema dialect.
for name, schema, value in [('exclusive', {'type': 'number', 'exclusiveMinimum': 5}, 3),
                            ('const', {'const': 5}, 3), ('false', False, {})]:
    doc = document(schema, version='3.1.0')
    actual = kinds(doc, exchange(body=json.dumps(value)))
    record('C02_' + name, {'spec': doc, 'instance': value}, ['RESPONSE_SCHEMA'], actual, actual == [])

# C03: transforms must traverse schemas, not arbitrary property names or enum values.
schema = {'type': 'object', 'properties': {'readOnly': {'type': 'integer'},
                                         'nullable': {'type': 'integer'}}}
actual = conformance.to_json_schema(schema, True)
record('C03_property_names', schema, 'Both property schemas preserved', actual,
       actual['properties'] == {})
schema = {'type': 'object', 'required': ['id'], 'properties': {'id': {'type': 'integer', 'readOnly': True}}}
actual = error_list(schema, {})
doc = document(request_body={'content': {'application/json': {'schema': schema}}})
actual = kinds(doc, exchange(request_text='{}'))
record('C03_readonly_required', {'schema': schema, 'direction': 'request', 'instance': {}}, [], actual,
       actual == ['INVALID_ACCEPTED'])
schema['properties']['id'] = {'type': 'integer', 'writeOnly': True}
actual = kinds(document(schema), exchange())
record('C03_writeonly_required', {'schema': schema, 'direction': 'response', 'instance': {}}, [], actual,
       actual == ['RESPONSE_SCHEMA'])

# C04: recursive references are cut; 3.1 $ref sibling constraints are discarded.
node = {'type': 'object', 'properties': {'value': {'type': 'integer'}, 'next': {'$ref': '#/components/schemas/Node'}}}
doc = document({'$ref': '#/components/schemas/Node'})
doc['components'] = {'schemas': {'Node': node}}
body = {'value': 'BAD'}
for _ in range(12):
    body = {'value': 1, 'next': body}
actual = kinds(doc, exchange(json.dumps(body)))
record('C04_recursive_ref', {'schema': node, 'nested_next_depth': 12, 'leaf': {'value': 'BAD'}},
       ['RESPONSE_SCHEMA'], actual, actual == [])
doc = document({'$ref': '#/components/schemas/N', 'maximum': 5}, version='3.1.0')
doc['components'] = {'schemas': {'N': {'type': 'number'}}}
actual = kinds(doc, exchange('8'))
record('C04_ref_sibling', {'spec': doc, 'instance': 8}, ['RESPONSE_SCHEMA'], actual, actual == [])

# C05: choose the response schema using the actual media type.
content = {'application/json': {'schema': {'type': 'object'}},
           'text/plain': {'schema': {'type': 'string'}}}
doc = document(content=content)
ex = exchange('hello')
ex['response']['headers']['content-type'] = 'text/plain'
actual = kinds(doc, ex)
record('C05_plain_response', {'content': content, 'body': 'hello', 'content-type': 'text/plain'}, [], actual,
       actual == ['RESPONSE_PARSE'])
content = {'application/json': {'schema': {'type': 'string'}},
           'application/problem+json': {'schema': {'type': 'object'}}}
doc = document(content=content)
ex = exchange('{}')
ex['response']['headers']['content-type'] = 'application/problem+json'
actual = kinds(doc, ex)
record('C05_json_variant', {'content': content, 'body': '{}', 'content-type': 'application/problem+json'},
       [], actual, actual == ['RESPONSE_SCHEMA'])

# C06: server scopes, variables, and later server alternatives.
doc = document(parameters=[{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}])
doc['paths']['/x/{id}'] = doc['paths'].pop('/x')
doc['servers'] = [{'url': 'https://example.test/{version}', 'variables': {'version': {'default': 'v1'}}}]
actual = conformance.Spec(doc).match('/v1/x/7')
record('C06_server_variable', doc, ['/x/{id}', {'id': '7'}], actual,
       actual != ('/x/{id}', {'id': '7'}))
doc = document()
doc['servers'] = [{'url': '/api'}]
doc['paths']['/x']['get']['servers'] = [{'url': '/custom'}]
actual = kinds(doc, exchange(path='/custom/x'))
record('C06_operation_server', doc, [], actual, actual == ['UNDOCUMENTED_OPERATION'])
doc['servers'] = [{'url': '/api'}, {'url': '/v2'}]
doc['paths']['/x']['get'].pop('servers')
actual = kinds(doc, exchange(path='/v2/x'))
record('C06_second_server', doc, [], actual, actual == ['UNDOCUMENTED_OPERATION'])

# C07: mixed literal/template segments and URL decoding.
doc = document(parameters=[{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}])
doc['paths']['/files/{id}.json'] = doc['paths'].pop('/x')
actual = conformance.Spec(doc).match('/files/7.json')
record('C07_mixed_segment', doc, ['/files/{id}.json', {'id': '7'}], actual,
       actual[1] == {'id}.jso': '7.json'})
doc = document(parameters=[{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}])
doc['paths']['/x/{id}'] = doc['paths'].pop('/x')
actual = kinds(doc, exchange(path='/x/%31'))
record('C07_encoded_path', {'spec': doc, 'path': '/x/%31'}, [], actual,
       actual == ['INVALID_ACCEPTED'])

# C08: explode=true with a single comma-containing array value must not split it.
p = query_param({'type': 'array', 'items': {'type': 'string'}, 'maxItems': 1}, style='form', explode=True)
actual = kinds(document(parameters=[p]), exchange(query={'q': ['a,b']}))
record('C08_single_exploded_value', {'parameter': p, 'query': {'q': ['a,b']}}, [], actual,
       actual == ['INVALID_ACCEPTED'])
p = query_param({'type': 'array', 'items': {'type': 'string', 'enum': ['a,b']}}, style='form', explode=True)
actual = kinds(document(parameters=[p]), exchange(query={'q': ['a,b']}))
record('C08_comma_enum', {'parameter': p, 'query': {'q': ['a,b']}}, [], actual,
       actual == ['INVALID_ACCEPTED', 'INVALID_ACCEPTED'])
p = {'name': 'session', 'in': 'cookie', 'required': True, 'schema': {'type': 'string'}}
actual = kinds(document(parameters=[p]), exchange())
record('C08_required_cookie', p, ['INVALID_ACCEPTED'], actual, actual == [])
p = query_param({}, required=True)
actual = kinds(document(parameters=[p]), exchange())
record('C08_empty_schema_required', p, ['INVALID_ACCEPTED'], actual, actual == [])

# C09: path-level parameter $refs must be deduplicated after resolution.
doc = document(parameters=[{'$ref': '#/components/parameters/Q'}])
doc['components'] = {'parameters': {'Q': query_param({'type': 'integer'}),
                                   'R': {'name': 'r', 'in': 'query', 'required': True, 'schema': {'type': 'integer'}}}}
doc['paths']['/x']['parameters'] = [{'$ref': '#/components/parameters/R'}]
mut, manifest, _ = specmut.mutate(doc, 'REQUEST_STRICT', 100, 1)
actual = [specmut.resolve(mut, p).get('name') for p in mut['paths']['/x']['get']['parameters']]
record('C09_path_ref_dedup', doc, 'Both q and inherited r materialized; r tightened too', actual,
       actual == ['q'])

# C10: strict mutation can loosen constraints or count unchanged values as edits.
p = query_param({'type': 'string', 'maxLength': 0}, required=True)
doc = document(parameters=[p])
mut, manifest, _ = specmut.mutate(doc, 'REQUEST_STRICT', 100, 1)
schema = mut['paths']['/x']['get']['parameters'][0]['schema']
record('C10_strict_widens', doc, 'maxLength <= 0', {'schema': schema, 'manifest': manifest},
       schema['maxLength'] == 1 and error_list(p['schema'], 'a') and not error_list(schema, 'a'))
p = query_param({'type': 'integer', 'maximum': -2}, required=True)
doc = document(parameters=[p])
mut, manifest, _ = specmut.mutate(doc, 'REQUEST_STRICT', 100, 1)
record('C10_noop_manifest', doc, 'No mutation record for unchanged operation', manifest,
       mut == doc and len(manifest) == 1)

# C11: composition is not visited; allOf editing is not necessarily a relaxation of oneOf.
for key in ['allOf', 'oneOf']:
    doc = document(parameters=[query_param({key: [{'type': 'integer', 'minimum': 2}]})])
    mut, manifest, _ = specmut.mutate(doc, 'REQUEST_LOOSE', 100, 1)
    record('C11_unvisited_' + key, doc, 'Nested minimum removed and manifested', manifest,
           mut == doc and manifest == [])

# C12: unescaped property names produce unusable JSON Pointers.
rb = {'content': {'application/json': {'schema': {'type': 'object', 'properties': {
    'a/b': {'type': 'string', 'maxLength': 3}, 't~n': {'type': 'string', 'maxLength': 4}}}}}}
doc = document(request_body=rb)
mut, manifest, _ = specmut.mutate(doc, 'REQUEST_LOOSE', 100, 1)
ptrs = [e['pointer'] for m in manifest for e in m['edits']]
record('C12_pointer_escaping', doc, 'a~1b and t~0n pointer segments', ptrs,
       any('/a/b/' in p for p in ptrs) and any('/t~n/' in p for p in ptrs))

# C13: structural ref inlining is absent from the edit manifest.
doc = document(parameters=[{'$ref': '#/components/parameters/Q'}])
doc['components'] = {'parameters': {'Q': query_param({'type': 'integer', 'minimum': 1}, required=True)}}
mut, manifest, _ = specmut.mutate(doc, 'REQUEST_LOOSE', 100, 1)
before_present = []
for edit in manifest[0]['edits']:
    try:
        test_specmut.get(doc, edit['pointer'])
        before_present.append(True)
    except KeyError:
        before_present.append(False)
record('C13_unlogged_structure', doc, 'Every structural edit and before-value auditable',
       {'manifest': manifest, 'before_pointer_present': before_present,
        'mutated_parameter': mut['paths']['/x']['get']['parameters'][0]},
       not any(before_present))

# C14: fingerprint collisions conceal a newly imposed required-property failure on identical traffic.
schema = {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'integer'}}, 'required': ['a']}
doc = document(schema)
mut, manifest, _ = specmut.mutate(doc, 'RESPONSE_ORACLE', 100, 1)
b = conformance.check(conformance.Spec(doc), exchange())
m = conformance.check(conformance.Spec(mut), exchange())
rows = attribute.attribute(b, m, {'mutations': manifest})
record('C14_required_fingerprint', {'spec': doc, 'exchange': exchange(), 'fault': 'RESPONSE_ORACLE'},
       'New missing b failure retained separately', {'baseline': b, 'mutated': m, 'attribution': rows},
       len(b) == 1 and len(m) == 2 and len(rows) == 1 and rows[0]['status'] == 'PERSISTENT')

# C15: different traffic cannot establish a mutation's causal ground-truth label.
doc = document(parameters=[query_param({'type': 'integer'})])
mut, manifest, _ = specmut.mutate(doc, 'REQUEST_STRICT', 100, 1)
b = conformance.check(conformance.Spec(doc), exchange(query={'q': ['0']}))
m = conformance.check(conformance.Spec(mut), exchange(status=500, query={'q': ['0']}))
rows = attribute.attribute(b, m, {'mutations': manifest})
record('C15_causal_overclaim', {'fault': 'REQUEST_STRICT', 'baseline_status': 200, 'mutated_status': 500},
       'SERVER_ERROR remains unproven/manual without causal evidence', rows,
       any(r['kind'] == 'SERVER_ERROR' and r['label_L1'] == 'SPEC' for r in rows))

# C16: Python ISO parsers accept values outside the promised RFC3339 formats.
for fmt, value in [('date', '20260101'), ('date-time', '2026-01-01'),
                   ('date-time', '2026-01-01T12:00:00')]:
    schema = {'type': 'string', 'format': fmt}
    actual = error_list(schema, value)
    record('C16_' + value, {'schema': schema, 'instance': value}, 'format error', actual, actual == [])

# C17: test generator cannot cover default/range responses and generates invalid composition instances.
doc = document()
doc['paths']['/x']['get']['responses'] = {'2XX': {'description': 'ok'}}
try:
    actual = test_pipeline.exchanges_for(doc)
except ValueError as exc:
    actual = type(exc).__name__ + ': ' + str(exc)
record('C17_range_test_crash', doc, 'Representative 200 exchange', actual, isinstance(actual, str))
doc['paths']['/x']['get']['responses'] = {'default': {'description': 'ok'}}
actual = test_pipeline.exchanges_for(doc)
record('C17_default_not_tested', doc, 'At least one documented response exchange', actual, actual == [])
schema = {'allOf': [{'type': 'object', 'properties': {'a': {'type': 'integer'}}, 'required': ['a']},
                    {'type': 'object', 'properties': {'b': {'type': 'integer'}}, 'required': ['b']}]}
actual = test_pipeline.instance(schema)
record('C17_invalid_generated_instance', schema, 'Instance conforms to both allOf branches',
       {'instance': actual, 'errors': error_list(schema, actual)}, bool(error_list(schema, actual)))

# C18: P001 replay loses duplicate keys and changes non-URL-encoded values.
actual = p001.kv('q=a;q=b;token=A+B')
record('C18_kv_loss', 'q=a;q=b;token=A+B', 'q retains both values; decode only per source encoding', actual,
       actual == {'q': 'b', 'token': 'A B'})
fake_row = {'path': '/x/{id}', 'pathParameters': 'id=a%2Fb', 'queryParameters': '', 'headerParameters': '',
            'responseBody': '{}', 'bodyParameter': '', 'httpMethod': 'GET', 'statusCode': 200,
            'outputContentType_y': 'application/json'}
actual = p001.exchange(fake_row, conformance.Spec(document()))
record('C18_path_unescape', fake_row, 'Preserve encoded slash as a path parameter value',
       actual['request']['path'], actual['request']['path'] == '/x/a/b')

# C19: broad oracle hit can be true for a different violation than the source message.
doc = document(content=content)
ex = exchange('{}')
ex['response']['headers']['content-type'] = 'application/problem+json'
actual = {v['kind'] for v in conformance.check(conformance.Spec(doc), ex)}
record('C19_broad_agreement', {'p001_message_type': 'ADDITIONAL_PROPERTIES',
                             'our_actual_error': 'wrong content-type schema -> type error'},
       'Different root cause is not message-level reproduction',
       {'our_kinds': sorted(actual), 'reproduced': bool(actual & p001.OUR_KIND_FOR['F_OAS'])},
       bool(actual & p001.OUR_KIND_FOR['F_OAS']))

# C20: addon-only mock, no mitmproxy code is imported or executed.
fake_mitm = types.ModuleType('mitmproxy')
fake_mitm.http = types.SimpleNamespace(HTTPFlow=object)
sys.modules['mitmproxy'] = fake_mitm
os.environ['MITM_LOG_DIR'] = str(HERE / 'mock_log')
module_spec = importlib.util.spec_from_file_location('t4_mitm', ROOT / '08_experiments/tools/mitm_fulllog.py')
addon = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(addon)
class FakeMessage:
    def get_content(self, strict=False):
        return b'\xff\x00'
actual = addon._body(FakeMessage())
record('C20_binary_log', {'raw_hex': 'ff00'}, 'Lossless bytes or explicit unsupported marker', actual,
       actual['text'].encode('utf-8') != b'\xff\x00')

# C21: the property test accepts a deletion whose pointer never existed.
rb = {'content': {'application/json': {'schema': {'type': 'object', 'properties': {
    'a/b': {'type': 'string', 'maxLength': 3}}}}}}
fixture = HERE / 'escaped_property.json'
fixture.write_text(json.dumps(document(request_body=rb)), encoding='utf-8')
actual = test_specmut.check(str(fixture), 'REQUEST_LOOSE', severity=100)
record('C21_bad_pointer_test_pass', {'fixture': str(fixture.relative_to(ROOT))},
       'Reject nonexistent deletion pointer', {'test_passed': True, 'counts': actual}, actual[1] == 1)

# C22: normalized nullable parameter types are not understood by the coercer.
p = query_param({'type': 'integer', 'nullable': True})
actual = kinds(document(parameters=[p]), exchange(query={'q': ['7']}))
record('C22_nullable_parameter', {'parameter': p, 'query': {'q': ['7']}}, [], actual,
       actual == ['INVALID_ACCEPTED'])

# C23: TRACE is a valid OAS3 operation but absent from all mutation candidates.
doc = document()
doc['paths']['/x']['trace'] = doc['paths']['/x'].pop('get')
actual = specmut.mutate(doc, 'METHOD_SEM', 100, 1)
record('C23_trace_not_enumerated', doc, 'One TRACE operation in operations_total',
       {'operations_total': actual[2], 'manifest': actual[1]}, actual[2] == 0)

# C24: severity zero still injects a method change.
actual = specmut.mutate(document(), 'METHOD_SEM', 0, 1)
record('C24_zero_severity', {'spec': document(), 'severity': 0}, 'Zero edits at zero percent',
       actual[1], len(actual[1]) == 1)

# C25: an empty corpus passes both existing test entry points.
empty_dir = HERE / 'empty_specs'
empty_dir.mkdir(exist_ok=True)
import contextlib
import io
output = io.StringIO()
with contextlib.redirect_stdout(output):
    status_specmut = test_specmut.main(str(empty_dir))
    status_pipeline = test_pipeline.main(str(empty_dir))
record('C25_empty_corpus_passes', {'spec_dir': str(empty_dir.relative_to(ROOT))},
       'Nonzero status for zero specs', {'specmut_exit': status_specmut,
                                       'pipeline_exit': status_pipeline, 'stdout': output.getvalue()},
       status_specmut == status_pipeline == 0)

# Positive controls prevent mistaking implemented semantics for defects.
doc = document()
doc['paths']['/pets/{id}'] = copy.deepcopy(doc['paths']['/x'])
doc['paths']['/pets/mine'] = copy.deepcopy(doc['paths']['/x'])
assert conformance.Spec(doc).match('/pets/mine')[0] == '/pets/mine'
op = {'responses': {'200': {'description': 'exact'}, '2XX': {'description': 'range'},
                    'default': {'description': 'fallback'}}}
sp = conformance.Spec(doc)
assert [sp.response_entry(op, x)['description'] for x in (200, 201, 404)] == ['exact', 'range', 'fallback']
sw2 = {'swagger': '2.0', 'basePath': '/api/v1', 'paths': {'/x': {'get': {'responses': {'200': {'description': 'ok'}}}}}}
assert conformance.Spec(sw2).match('/api/v1/x')[0] == '/x'
assert error_list({'type': 'integer', 'nullable': True}, None) == []
assert error_list({'type': 'integer'}, None)
doc = document(parameters=[query_param({'type': 'integer'})])
doc['paths']['/x']['parameters'] = [query_param({'type': 'string'})]
_, params = conformance.Spec(doc).operation('/x', 'get')
assert params[0]['schema']['type'] == 'integer'
mut1 = specmut.mutate(doc, 'REQUEST_STRICT', 100, 7)
mut2 = specmut.mutate(copy.deepcopy(doc), 'REQUEST_STRICT', 100, 7)
assert mut1 == mut2
mut, manifest, _ = specmut.mutate(document(), 'METHOD_SEM', 100, 1)
v = {'method': 'POST', 'template': '/x', 'kind': 'UNDOCUMENTED_STATUS', 'status': 418,
     'pointer': '', 'fingerprint': 'POST|/x|418|UNDOCUMENTED_STATUS|'}
assert attribute.attribute([], [v], {'mutations': manifest})[0]['op_mutated']
assert error_list({'allOf': [{'type': 'integer'}, {'minimum': 2}]}, 3) == []
assert error_list({'allOf': [{'type': 'integer'}, {'minimum': 2}]}, 1)
assert error_list({'oneOf': [{'type': 'integer'}, {'type': 'string'}]}, 3) == []
assert error_list({'oneOf': [{'type': 'integer'}, {'type': 'number'}]}, 3)
print(json.dumps({'summary': {'confirmed_observations': COUNT, 'positive_control_groups': 8}}))
