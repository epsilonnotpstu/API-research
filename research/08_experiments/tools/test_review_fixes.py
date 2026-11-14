"""T10 correctness regressions based on T4's concrete reproductions.

Run: /usr/bin/python3 -I -B 08_experiments/tools/test_review_fixes.py
No external code is executed. Logger conversion uses an inert mitmproxy mock.
"""
import base64
import contextlib
import copy
import importlib.util
import io
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'E1_pilot'))
import attribute
import conformance as c
import p001_oas_analysis as p001
import specmut as s
import test_pipeline
import test_specmut


def doc(schema=None, params=None, rb=None, version='3.0.3'):
    response = {'description': 'ok'}
    if schema is not None:
        response['content'] = {'application/json': {'schema': schema}}
    op = {'responses': {'200': response}}
    if params is not None:
        op['parameters'] = params
    if rb is not None:
        op['requestBody'] = rb
    return {'openapi': version, 'info': {'title': 'T10', 'version': '1'}, 'paths': {'/x': {'get': op}}}


def ex(body='{}', request='', status=200, query=None, path='/x'):
    return {'request': {'method': 'GET', 'path': path, 'query': query or {}, 'headers': {},
                        'body': {'text': request, 'truncated': False}},
            'response': {'status': status, 'headers': {'content-type': 'application/json'},
                         'body': {'text': body, 'truncated': False}}}


def param(schema, **kw):
    return {'name': 'q', 'in': 'query', 'schema': schema, **kw}


def kinds(d, e):
    return [v['kind'] for v in c.check(c.Spec(d), e)]


def body_schema(schema, required=True):
    return {'required': required, 'content': {'application/json': {'schema': schema}}}


class ReviewFixes(unittest.TestCase):
    def test_cli_compatibility_and_attribution_mode(self):
        with tempfile.TemporaryDirectory(dir=HERE.parents[1] / '09_collab/logs/T10_scratch') as tmp:
            directory = Path(tmp)
            base = directory / 'base.json'
            base.write_text(json.dumps(doc({'type': 'object', 'properties': {'a': {}}, 'required': []})))
            exchanges = directory / 'exchanges.jsonl'
            exchanges.write_text(json.dumps(ex()) + '\n')
            def cli(tool, *args):
                return subprocess.run([sys.executable, '-I', '-B', str(HERE / tool), *map(str, args)],
                                      check=True, capture_output=True, text=True).stdout
            cli('specmut.py', base, '--fault', 'RESPONSE_ORACLE', '--severity', '100', '--seed', '1', '--out', directory)
            mutated = next(directory.glob('*__response_oracle*.json'))
            if mutated.name.endswith('.manifest.json'):
                mutated = next(p for p in directory.glob('*__response_oracle*.json') if not p.name.endswith('.manifest.json'))
            manifest = next(directory.glob('*.manifest.json'))
            bv, mv = directory / 'base.jsonl', directory / 'mut.jsonl'
            bv.write_text(cli('conformance.py', base, exchanges))
            mv.write_text(cli('conformance.py', mutated, exchanges))
            self.assertIn('NEEDS_MANUAL', cli('attribute.py', bv, mv, manifest))
            self.assertIn(',SPEC,', cli('attribute.py', bv, mv, manifest, '--mode', 'replay'))

    def test_R01_constraint_vs_category_and_negative_location(self):
        reason = 'OAS disconformity: [Path \'/a\'] Object instance has properties which are not allowed by the schema: ["extra"]'
        source = p001.source_constraints(reason)
        unrelated = c.check(c.Spec(doc({'type': 'object', 'required': ['b']})), ex())
        self.assertTrue({v['kind'] for v in unrelated} & p001.OUR_KIND_FOR['F_OAS'])
        self.assertFalse(any(p001.constraint_matches(source, unrelated).values()))
        d = doc({'type': 'object', 'properties': {'a': {'type': 'object', 'additionalProperties': False}}})
        observed = c.check(c.Spec(d), ex('{"a":{"extra":1}}'))
        self.assertTrue(all(p001.constraint_matches(source, observed).values()))
        observed[0]['instance_location'] = '/b'
        self.assertFalse(any(p001.constraint_matches(source, observed).values()))

    def test_R01_normalized_array_and_required_property(self):
        reason = 'OAS disconformity: [Path \'/items/[item]\'] Object has missing required properties (["a";"b"])'
        source = p001.source_constraints(reason)
        self.assertEqual(set(source), {('required', '/items/*', 'a'), ('required', '/items/*', 'b')})
        d = doc({'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'required': ['a']}}}})
        matches = p001.constraint_matches(source, c.check(c.Spec(d), ex('{"items":[{}]}')))
        self.assertEqual(sum(matches.values()), 1)

    def test_R02_required_identity_and_occurrences(self):
        d = doc({'type': 'object', 'properties': {'a': {}, 'b': {}}, 'required': ['a']})
        m, manifest, _ = s.mutate(d, 'RESPONSE_ORACLE', 100, 1)
        base, mut = c.check(c.Spec(d), ex()), c.check(c.Spec(m), ex())
        rows = attribute.attribute(base * 2, mut * 3, {'mutations': manifest}, mode='replay')
        self.assertEqual(sorted(r['status'] for r in rows), ['NEW', 'PERSISTENT'])
        persistent = next(r for r in rows if r['status'] == 'PERSISTENT')
        self.assertEqual((persistent['baseline_occurrences'], persistent['mutated_occurrences']), (2, 3))

    def test_R02_extra_properties_and_array_locations(self):
        d = doc({'type': 'array', 'items': {'type': 'object', 'additionalProperties': False}})
        violations = c.check(c.Spec(d), ex('[{"a":1,"b":2},{"a":3}]'))
        self.assertEqual(len(violations), 3)
        self.assertEqual(len({v['fingerprint'] for v in violations}), 2)
        self.assertEqual({v['property'] for v in violations}, {'a', 'b'})

    def test_R03_fresh_and_replay_new_vanished(self):
        d = doc(params=[param({'type': 'integer'})])
        m, manifest, _ = s.mutate(d, 'REQUEST_STRICT', 100, 1)
        base = c.check(c.Spec(d), ex(query={'q': ['0']}))
        changed = c.check(c.Spec(m), ex(status=500, query={'q': ['0']}))
        fresh = attribute.attribute(base, changed, {'mutations': manifest})
        self.assertTrue(fresh)
        self.assertTrue(all(r['label_L1'] == 'NEEDS_MANUAL' and r['expected_if_injected'] == 'SPEC' for r in fresh))
        same = c.check(c.Spec(m), ex(query={'q': ['5']}))
        replay = attribute.attribute([], same, {'mutations': manifest}, mode='replay')
        self.assertEqual(replay[0]['label_L1'], 'SPEC')
        self.assertEqual(attribute.attribute(same, [], {'mutations': manifest})[0]['label_L1'], 'NEEDS_MANUAL')
        self.assertEqual(attribute.attribute(same, [], {'mutations': manifest}, mode='replay')[0]['label_L1'], 'MASKED')

    def test_R04_null_response_all_json_values(self):
        for text in ('null', 'false', '0', '"s"', '[]'):
            with self.subTest(text=text):
                self.assertIn('RESPONSE_SCHEMA', kinds(doc({'type': 'object'}), ex(text)))
        self.assertEqual(kinds(doc({'type': 'object', 'nullable': True}), ex('null')), [])

    def test_R05_missing_malformed_null_and_truncated_request(self):
        d = doc(rb=body_schema({'type': 'object'}))
        for text in ('', '{', 'null'):
            with self.subTest(text=text):
                self.assertIn('INVALID_ACCEPTED', kinds(d, ex(request=text)))
        e = ex(request='{"a":', status=400)
        e['request']['body']['truncated'] = True
        self.assertIn('REQUEST_UNCHECKABLE', kinds(d, e))
        self.assertNotIn('VALID_REJECTED', kinds(d, e))
        self.assertNotIn('VALID_REJECTED', kinds(d, ex(request='{', status=400)))
        self.assertIn('VALID_REJECTED', kinds(d, ex(request='{}', status=400)))

    def test_R06_dialect_boolean_exclusive_const_and_ref_siblings(self):
        for schema, text in [({'type': 'number', 'exclusiveMinimum': 5}, '3'), ({'const': 5}, '3'), (False, '{}')]:
            self.assertIn('RESPONSE_SCHEMA', kinds(doc(schema, version='3.1.0'), ex(text)))
        d = doc({'$ref': '#/components/schemas/N', 'maximum': 5}, version='3.1.0')
        d['components'] = {'schemas': {'N': {'type': 'number', 'maximum': 10}}}
        self.assertIn('RESPONSE_SCHEMA', kinds(d, ex('8')))
        self.assertEqual(kinds(d, ex('4')), [])
        d['components']['schemas']['N'] = True
        self.assertTrue(list(c.validator(s.resolve(d, {'$ref': '#/components/schemas/N', 'maximum': 5}), '3.1.0').iter_errors(8)))
        d['components']['schemas']['N'] = {'type': 'number', 'maximum': 10}
        d['openapi'] = '3.0.3'
        self.assertEqual(kinds(d, ex('8')), [])

    def test_R07_property_names_and_literal_data_preserved(self):
        schema = {'type': 'object', 'properties': {k: {'type': 'integer'} for k in ('readOnly', 'nullable', 'xml')},
                  'enum': [{'readOnly': 1, 'nullable': 2}]}
        normalized = c.to_json_schema(schema, True)
        self.assertEqual(normalized['properties'], schema['properties'])
        self.assertEqual(normalized['enum'], schema['enum'])
        self.assertIn('RESPONSE_SCHEMA', kinds(doc(schema), ex('{"readOnly":"bad"}')))

    def test_R08_directional_required(self):
        schema = {'type': 'object', 'required': ['id'], 'properties': {'id': {'type': 'integer', 'readOnly': True}}}
        self.assertNotIn('INVALID_ACCEPTED', kinds(doc(rb=body_schema(schema)), ex(request='{}')))
        self.assertIn('RESPONSE_SCHEMA', kinds(doc(schema), ex()))
        schema['properties']['id'] = {'type': 'integer', 'writeOnly': True}
        self.assertNotIn('RESPONSE_SCHEMA', kinds(doc(schema), ex()))
        self.assertIn('INVALID_ACCEPTED', kinds(doc(rb=body_schema(schema)), ex(request='{}')))

    def test_R09_media_selection_exact_wildcard_and_request(self):
        d = doc()
        content = {'application/json': {'schema': {'type': 'string'}},
                   'application/problem+json': {'schema': {'type': 'object'}},
                   'text/*': {'schema': {'type': 'string'}}}
        d['paths']['/x']['get']['responses']['200']['content'] = content
        for media, text in [('application/problem+json', '{}'), ('text/plain', 'hello'), ('text/plain', '')]:
            e = ex(text)
            e['response']['headers']['content-type'] = media
            self.assertEqual(kinds(d, e), [])
        d['paths']['/x']['get']['requestBody'] = {'required': True, 'content': content}
        e = ex('"s"', request='hello')
        e['request']['headers']['content-type'] = 'text/plain'
        self.assertNotIn('INVALID_ACCEPTED', kinds(d, e))
        e['request']['headers']['content-type'] = 'image/png'
        self.assertIn('INVALID_ACCEPTED', kinds(d, e))

    def test_R10_server_variables_overrides_alternatives_and_origin(self):
        d = doc(params=[{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}])
        d['paths']['/x/{id}'] = d['paths'].pop('/x')
        d['servers'] = [{'url': 'https://example.test/{version}', 'variables': {'version': {'default': 'v1'}}}]
        self.assertEqual(c.Spec(d).match('/v1/x/7'), ('/x/{id}', {'id': '7'}))
        d['paths']['/x/{id}']['get']['servers'] = [{'url': '/custom'}]
        d['paths']['/x/{id}']['post'] = {'responses': {'200': {'description': 'ok'}}}
        self.assertEqual(kinds(d, ex(path='/custom/x/7')), [])
        self.assertIn('UNDOCUMENTED_OPERATION', kinds(d, ex(path='/v1/x/7')))
        d['paths']['/x/{id}']['get'].pop('servers')
        d['servers'].append({'url': 'https://example.test/v2'})
        e = ex(path='/v2/x/7')
        e['request']['origin'] = 'https://example.test:443'
        self.assertEqual(kinds(d, e), [])
        e['request']['origin'] = 'https://else.test'
        self.assertIn('UNDOCUMENTED_OPERATION', kinds(d, e))

    def test_R11_path_parameter_refs_dedup_and_override(self):
        d = doc(params=[{'$ref': '#/components/parameters/Q'}])
        d['paths']['/x']['parameters'] = [{'$ref': '#/components/parameters/R'}]
        d['components'] = {'parameters': {'Q': param({'type': 'integer'}),
                                        'R': {**param({'type': 'integer'}), 'name': 'r'}}}
        m, manifest, _ = s.mutate(d, 'REQUEST_STRICT', 100, 1)
        ps = m['paths']['/x']['get']['parameters']
        self.assertEqual({p['name'] for p in ps}, {'q', 'r'})
        self.assertTrue(all(p['schema']['maximum'] == 0 for p in ps))
        self.assertEqual(test_specmut.apply_manifest(d, manifest), m)

    def test_R12_strict_monotonic_noop_and_required_union(self):
        for schema in ({'type': 'string', 'maxLength': 0}, {'type': 'integer', 'maximum': -2}):
            d = doc(params=[param(schema, required=True)])
            m, manifest, _ = s.mutate(d, 'REQUEST_STRICT', 100, 1)
            self.assertEqual((m, manifest), (d, []))
        schema = {'type': 'object', 'properties': {'b': {}}, 'required': ['a']}
        d = doc(rb=body_schema(schema))
        m, _, _ = s.mutate(d, 'REQUEST_STRICT', 100, 1)
        self.assertEqual(m['paths']['/x']['get']['requestBody']['content']['application/json']['schema']['required'], ['a', 'b'])
        d = doc(rb=body_schema({'type': 'object', 'properties': {'a': {}, 'b': {}}, 'required': ['b', 'a']}))
        self.assertEqual(s.mutate(d, 'REQUEST_STRICT', 100, 1)[:2], (d, []))

    def test_R13_full_patch_structural_ref_and_escaping(self):
        d = doc(params=[{'$ref': '#/components/parameters/Q'}])
        d['components'] = {'parameters': {'Q': param({'type': 'object', 'properties': {
            'a/b': {'type': 'string', 'maxLength': 3}, 't~n': {'type': 'integer', 'minimum': 1}}}, required=True)}}
        m, manifest, _ = s.mutate(d, 'REQUEST_LOOSE', 100, 1)
        self.assertEqual(test_specmut.apply_manifest(d, manifest), m)
        self.assertTrue(any(e['pointer'].endswith('/$ref') and e['op'] == 'remove' for e in manifest[0]['edits']))
        inline = doc(rb=body_schema({'type': 'object', 'properties': {'a/b': {'type': 'string', 'maxLength': 3}, 't~n': {'type': 'string', 'maxLength': 4}}}))
        m, manifest, _ = s.mutate(inline, 'REQUEST_LOOSE', 100, 1)
        self.assertEqual(test_specmut.apply_manifest(inline, manifest), m)
        self.assertTrue(any('/a~1b/' in e['pointer'] for e in manifest[0]['edits']))
        self.assertTrue(any('/t~0n/' in e['pointer'] for e in manifest[0]['edits']))
        bad = copy.deepcopy(manifest)
        bad[0]['edits'][0]['pointer'] += '/nonexistent'
        with self.assertRaises((AssertionError, KeyError)):
            test_specmut.apply_manifest(inline, bad)

    def test_R14_array_explode_and_nullable_numeric(self):
        for schema in ({'type': 'array', 'items': {'type': 'string'}, 'maxItems': 1},
                       {'type': 'array', 'items': {'type': 'string', 'enum': ['a,b']}}):
            self.assertEqual(kinds(doc(params=[param(schema, style='form', explode=True)]), ex(query={'q': ['a,b']})), [])
        schema = {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 1}
        self.assertIn('INVALID_ACCEPTED', kinds(doc(params=[param(schema, explode=False)]), ex(query={'q': ['a,b']})))
        self.assertEqual(kinds(doc(params=[param({'type': 'integer', 'nullable': True})]), ex(query={'q': ['7']})), [])
        self.assertEqual(kinds(doc(params=[param({'type': ['integer', 'null']})], version='3.1.0'), ex(query={'q': ['7']})), [])

    def test_R15_encoded_slash_remains_one_path_segment(self):
        d = doc()
        d['paths']['/x/{id}'] = d['paths'].pop('/x')
        row = {'path': '/x/{id}', 'pathParameters': 'id=a%2Fb', 'queryParameters': '', 'headerParameters': '',
               'responseBody': '{}', 'bodyParameter': '', 'httpMethod': 'GET', 'statusCode': 200, 'outputContentType_y': 'application/json'}
        e = p001.exchange(row, c.Spec(d))
        self.assertEqual(e['request']['path'], '/x/a%2Fb')
        self.assertEqual(c.Spec(d).match(e['request']['path']), ('/x/{id}', {'id': 'a/b'}))

    def test_R16_recursive_constraint_not_erased(self):
        node = {'type': 'object', 'properties': {'value': {'type': 'integer'}, 'next': {'$ref': '#/components/schemas/Node'}}}
        d = doc({'$ref': '#/components/schemas/Node'})
        d['components'] = {'schemas': {'Node': node}}
        body = {'value': 'BAD'}
        for _ in range(12):
            body = {'value': 1, 'next': body}
        self.assertIn('RESPONSE_SCHEMA', kinds(d, ex(json.dumps(body))))
        resolved = s.resolve(d, {'$ref': '#/components/schemas/Node'})
        self.assertIn('$ref', json.dumps(resolved))

    def test_R16_external_refs_abstain_without_fetch(self):
        for ref in ('https://example.test/schema', 'file:///nonexistent.json', 'ftp://example.test/schema'):
            d = doc({'$ref': ref})
            self.assertIn('RESPONSE_UNCHECKABLE', kinds(d, ex()))

    def test_R17_mixed_segments_and_single_percent_decode(self):
        d = doc(params=[{'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}])
        d['paths']['/files/{id}.json'] = d['paths'].pop('/x')
        self.assertEqual(c.Spec(d).match('/files/7.json'), ('/files/{id}.json', {'id': '7'}))
        self.assertEqual(kinds(d, ex(path='/files/%31.json')), [])
        self.assertIn('INVALID_ACCEPTED', kinds(d, ex(path='/files/%2531.json')))

    def test_R17_concrete_route_precedes_template_after_method_swap(self):
        d = doc()
        d['paths']['/x/{id}'] = copy.deepcopy(d['paths']['/x'])
        d['paths']['/x/literal'] = d['paths'].pop('/x')
        d['paths']['/x/literal']['post'] = d['paths']['/x/literal'].pop('get')
        self.assertEqual(c.Spec(d).match('/x/literal', 'GET')[0], '/x/literal')
        self.assertEqual(kinds(d, ex(path='/x/literal')), ['UNDOCUMENTED_OPERATION'])

    def test_R18_required_empty_schema_and_cookie(self):
        for p in (param({}, required=True), {'name': 'session', 'in': 'cookie', 'required': True, 'schema': {'type': 'string'}}):
            self.assertIn('INVALID_ACCEPTED', kinds(doc(params=[p]), ex()))
        d = doc(params=[{'name': 'session', 'in': 'cookie', 'required': True, 'schema': {'type': 'string'}}])
        e = ex()
        e['request']['headers']['cookie'] = 'session=abc'
        self.assertEqual(kinds(d, e), [])
        e['request']['headers']['cookie'] = '<redacted>'
        e['response']['status'] = 400
        self.assertNotIn('VALID_REJECTED', kinds(d, e))
        self.assertIn('REQUEST_UNCHECKABLE', kinds(d, e))

    def test_R19_allof_mutation_and_oneof_abstention(self):
        d = doc(params=[param({'allOf': [{'type': 'integer', 'minimum': 2}]})])
        m, manifest, _ = s.mutate(d, 'REQUEST_LOOSE', 100, 1)
        self.assertTrue(manifest)
        self.assertNotIn('minimum', m['paths']['/x']['get']['parameters'][0]['schema']['allOf'][0])
        d = doc(params=[param({'oneOf': [{'type': 'integer', 'minimum': 2}]})])
        m, manifest, _ = s.mutate(d, 'REQUEST_LOOSE', 100, 1)
        self.assertEqual((m, manifest), (d, []))

    def test_R20_rfc3339_formats(self):
        for fmt, value in [('date', '20260101'), ('date-time', '2026-01-01'), ('date-time', '2026-01-01T12:00:00'),
                           ('date-time', '2026-01-01T12:00:00+00:60')]:
            self.assertTrue(list(c.validator({'type': 'string', 'format': fmt}, True).iter_errors(value)))
        for fmt, value in [('date', '2026-01-01'), ('date-time', '2026-01-01T12:00:00Z'), ('date-time', '2026-01-01T12:00:00+06:00')]:
            self.assertEqual(list(c.validator({'type': 'string', 'format': fmt}, True).iter_errors(value)), [])

    def test_R21_range_default_allof_and_empty_corpus(self):
        for code in ('2XX', 'default'):
            d = doc()
            d['paths']['/x']['get']['responses'] = {code: {'description': 'ok'}}
            self.assertEqual(test_pipeline.exchanges_for(d)[0]['response']['status'], 200)
        schema = {'allOf': [{'type': 'object', 'properties': {'a': {'type': 'integer'}}, 'required': ['a']},
                            {'type': 'object', 'properties': {'b': {'type': 'integer'}}, 'required': ['b']}]}
        self.assertEqual(list(c.validator(schema, True).iter_errors(test_pipeline.instance(schema))), [])
        with tempfile.TemporaryDirectory(dir=HERE.parents[1] / '09_collab/logs/T10_scratch') as tmp, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(test_pipeline.main(tmp), 1)
            self.assertEqual(test_specmut.main(tmp), 1)

    def test_R22_binary_logger_roundtrip_without_external_execution(self):
        fake = types.ModuleType('mitmproxy')
        fake.http = types.SimpleNamespace(HTTPFlow=object)
        with patch.dict(sys.modules, {'mitmproxy': fake}), patch.dict(os.environ, {'MITM_LOG_DIR': str(HERE.parents[1] / '09_collab/logs/T10_scratch')}):
            spec = importlib.util.spec_from_file_location('t10_logger', HERE / 'mitm_fulllog.py')
            addon = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(addon)
        body = addon._body(types.SimpleNamespace(get_content=lambda strict=False: b'\xff\x00'))
        self.assertEqual(base64.b64decode(body['base64']), b'\xff\x00')
        self.assertTrue(body['decode_error'])
        self.assertFalse(body['truncated'])

    def test_R23_trace_severity_zero_and_range(self):
        d = doc()
        d['paths']['/x']['trace'] = d['paths']['/x'].pop('get')
        self.assertEqual(s.mutate(d, 'METHOD_SEM', 100, 1)[2], 1)
        self.assertEqual(s.mutate(doc(), 'METHOD_SEM', 0, 1)[:2], (doc(), []))
        for n in (-1, 101):
            with self.assertRaises(ValueError):
                s.mutate(doc(), 'METHOD_SEM', n, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
