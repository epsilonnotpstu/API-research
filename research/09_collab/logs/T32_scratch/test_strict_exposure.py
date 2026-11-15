"""Focused synthetic checks for T32's measurement semantics (own Python only)."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / '08_experiments/E1_pilot/pilot_results/strict_exposure.py'
spec = importlib.util.spec_from_file_location('strict_exposure', SCRIPT)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(__file__).parent / 'fixtures' / self._testMethodName
        self.run, self.baseline = self.folder / 'mutated', self.folder / 'baseline'
        self.run.mkdir(parents=True, exist_ok=True)
        self.baseline.mkdir(parents=True, exist_ok=True)

    def measure(self, old, new, exchanges):
        manifest = {'mutations': []}
        for path, item in new['paths'].items():
            for method, op in item.items():
                edits = s.specmut.document_edits(old['paths'][path][method], op, s.specmut.ptr('paths', path, method))
                if edits:
                    manifest['mutations'].append({'path': path, 'method': method, 'fault': 'REQUEST_STRICT', 'edits': edits})
        for run in (self.run, self.baseline):
            (run / 'exchanges.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in exchanges))
        rows, audit = s.analyse_run({'sut': 'market', 'seed': '1', 'severity': '30'}, 'evomaster',
                                   self.run, self.baseline, s.c.Spec(old), s.c.Spec(new), manifest, lambda *a: None)
        self.assertEqual(rows[0]['fresh_violating_requests'], rows[0]['baseline_violating_requests'])
        return rows, audit

    @staticmethod
    def ex(path='/x/2', status=200, query=None, body='', ctype='application/json', headers=None, truncated=False):
        return {'request': {'path': path, 'method': 'POST', 'query': query or {},
                            'headers': {'content-type': ctype, **(headers or {})},
                            'body': {'text': body, 'truncated': truncated, 'decode_error': False}},
                'response': {'status': status}}

    @staticmethod
    def base():
        return {'openapi': '3.0.0', 'paths': {'/x/{id}': {'post': {
            'parameters': [{'name': 'id', 'in': 'path', 'required': True,
                            'schema': {'type': 'integer', 'format': 'int64'}},
                           {'name': 'q', 'in': 'query', 'schema': {'type': 'string'}}],
            'responses': {'200': {'description': 'ok'}}}}}}

    def test_union_response_classes_and_location_gate(self):
        old = self.base()
        new = copy.deepcopy(old)
        ps = new['paths']['/x/{id}']['post']['parameters']
        ps[0]['schema']['maximum'] = 0
        ps[1]['required'] = True
        ps[1]['schema']['maxLength'] = 1
        examples = [self.ex(query={'q': ['long']}), self.ex(status=400),
                    self.ex(status=500), self.ex('/x/9223372036854775808', query={'q': ['x']}),
                    self.ex('/x/no-integer', query={'q': ['long']}), self.ex('/x/-1', query={'q': ['x']})]
        rows, audit = self.measure(old, new, examples)
        r = rows[0]
        self.assertEqual(r['fresh_requests_to_mutated_ops'], 6)
        self.assertEqual((r['fresh_violating_requests'], r['fresh_violating_2xx'], r['fresh_violating_4xx'],
                          r['fresh_violating_other']), (4, 2, 1, 1))
        # Overflow invalid originally: does not become an eligible maximum violation.
        maximum = next(r for r in rows if r['row_type'] == 'constraint' and r['pointer'].endswith('/maximum'))
        self.assertEqual(maximum['fresh_constraint_breaches'], 4)
        self.assertEqual(maximum['fresh_violating_requests'], 3)
        # Invalid id does not suppress independent valid-original query violation.
        self.assertEqual(r['fresh_original_invalid_requests'], 2)
        self.assertGreater(sum(r['fresh_violating_requests'] for r in rows if r['row_type'] == 'constraint'), 4)

    def test_body_gate_ref_expansion_and_array_unique_requests(self):
        old = self.base()
        old['components'] = {'schemas': {'Item': {'type': 'object', 'required': ['code'], 'properties': {
            'code': {'type': 'string', 'enum': ['ok']}, 'name': {'type': 'string'}}}}}
        schema = {'type': 'array', 'items': {'$ref': '#/components/schemas/Item'}}
        op = old['paths']['/x/{id}']['post']
        op['requestBody'] = {'required': True, 'content': {'application/json': {'schema': schema},
                                                        'application/xml': {'schema': copy.deepcopy(schema)}}}
        new = copy.deepcopy(old)
        ns = new['paths']['/x/{id}']['post']['requestBody']['content']['application/json']['schema']
        ns['items'] = copy.deepcopy(old['components']['schemas']['Item'])
        ns['items']['properties']['name']['maxLength'] = 1
        ns['items']['required'] = ['code', 'name']
        examples = [self.ex(body='[{"code":"ok","name":"long"},{"code":"ok","name":"long"}]'),
                    self.ex(body='[{"code":"bad","name":"long"}]'),
                    self.ex(body='[{"code":"ok"}]', status=404),
                    self.ex(body='{"code":"ok","name":"long"}'),
                    self.ex(body='[{"code":"ok","name":"long"}]', truncated=True),
                    self.ex(body='[{"code":"ok","name":"long"}]', ctype='application/xml'),
                    self.ex(body='not-json')]
        rows, _ = self.measure(old, new, examples)
        r = rows[0]
        self.assertEqual(r['fresh_violating_requests'], 2)
        self.assertEqual(r['fresh_violating_2xx'], 1)
        self.assertEqual(r['fresh_violating_4xx'], 1)
        self.assertEqual(r['fresh_constraint_breaches'], 3)
        self.assertEqual(r['fresh_original_invalid_requests'], 3)
        self.assertEqual(r['fresh_uncheckable_requests'], 1)
        structural = [r for r in rows if r.get('edit_role') == 'structural_or_annotation']
        self.assertTrue(structural)
        self.assertTrue(all(r['fresh_violating_requests'] == 0 for r in structural))

    def test_unknown_object_header_is_not_zero_compliance(self):
        old = self.base()
        ps = old['paths']['/x/{id}']['post']['parameters']
        ps.append({'name': 'Authorization', 'in': 'header', 'required': True,
                   'schema': {'type': 'object', 'properties': {'token': {'type': 'string'}}}})
        new = copy.deepcopy(old)
        new['paths']['/x/{id}']['post']['parameters'][-1]['schema']['properties']['token']['maxLength'] = 1
        rows, audit = self.measure(old, new, [self.ex(headers={'authorization': '<redacted>'})])
        self.assertEqual(rows[0]['fresh_uncheckable_requests'], 1)
        self.assertEqual(rows[0]['fresh_evaluated_requests'], 0)
        self.assertEqual(rows[0]['fresh_violating_requests'], 0)
        self.assertIn('unsupported parameter serialization: Authorization',
                      next(x for x in audit['examples'] if 'reasons' in x)['reasons'])

    def test_template_matching_concrete_precedence_and_decoding(self):
        old = self.base()
        old['paths']['/x/fixed'] = {'get': {'responses': {}}}
        new = copy.deepcopy(old)
        new['paths']['/x/{id}']['post']['parameters'][0]['schema']['maximum'] = 0
        rows, _ = self.measure(old, new, [self.ex('/x/fixed'), self.ex('/x/%32/'), self.ex('/x/3', status=302)])
        self.assertEqual(rows[0]['fresh_requests_to_mutated_ops'], 2)
        self.assertEqual(rows[0]['fresh_violating_requests'], 2)
        self.assertEqual(rows[0]['fresh_violating_other'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
