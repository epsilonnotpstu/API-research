"""Unit tests for specmut's candidate pool (--only-ops) and eligible_ops.py.

Usage: /usr/bin/python3 -I -B test_only_ops.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import specmut  # noqa: E402

OK = {'200': {'description': 'ok', 'schema': {'type': 'object', 'properties': {'a': {'type': 'string'}}}}}
SPEC = {'swagger': '2.0', 'info': {'title': 't', 'version': '1'}, 'basePath': '/api', 'paths': {
    '/items': {'get': {'responses': OK}, 'post': {'responses': OK}},
    '/items/{id}': {'parameters': [{'name': 'id', 'in': 'path', 'required': True, 'type': 'integer'}],
                    'get': {'responses': OK}, 'delete': {'responses': OK}},
    '/items/special': {'get': {'responses': OK}},
}}


class OnlyOps(unittest.TestCase):
    def test_default_unchanged(self):
        a = specmut.mutate(SPEC, 'RESPONSE_ORACLE', 40, 3)
        b = specmut.mutate(SPEC, 'RESPONSE_ORACLE', 40, 3, only=None)
        self.assertEqual(a[1], b[1])
        self.assertEqual(a[2], 5)

    def test_pool_restricts_selection(self):
        pool = {('/items', 'GET'), ('/items/{id}', 'get')}
        for seed in range(20):
            _, manifest, n = specmut.mutate(SPEC, 'RESPONSE_ORACLE', 100, seed, only=pool)
            self.assertEqual(n, 2)
            self.assertTrue({(m['path'], m['method']) for m in manifest} <= {('/items', 'get'), ('/items/{id}', 'get')})
            self.assertTrue(manifest)

    def test_unknown_operation_rejected(self):
        with self.assertRaises(ValueError):
            specmut.mutate(SPEC, 'RESPONSE_ORACLE', 30, 1, only={('/nope', 'get')})

    def test_excluded_but_listed_is_not_unknown(self):
        _, manifest, n = specmut.mutate(SPEC, 'RESPONSE_ORACLE', 100, 1, exclude={'/items'},
                                        only={('/items', 'get'), ('/items/{id}', 'get')})
        self.assertEqual(n, 1)
        self.assertEqual([(m['path'], m['method']) for m in manifest], [('/items/{id}', 'get')])


class EligibleOps(unittest.TestCase):
    def test_counts_2xx_with_body_and_literal_paths_first(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)
            (run / 'spec.original.json').write_text(json.dumps(SPEC))

            def ex(method, path, status, size):
                return json.dumps({'request': {'method': method, 'path': path},
                                   'response': {'status': status, 'body': {'size': size}}})
            lines = [ex('GET', '/api/items?x=1', 200, 10), ex('GET', '/api/items/special', 200, 5),
                     ex('GET', '/api/items/7', 200, 0),       # empty body: not eligible
                     ex('POST', '/api/items', 500, 30),       # not 2xx
                     ex('DELETE', '/api/items/7', 204, 3)]
            (run / 'exchanges.jsonl').write_text('\n'.join(lines) + '\n')
            out = run / 'eligible.json'
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'eligible_ops.py'), str(run),
                            '--base-path', '/api', '--out', str(out)], check=True, capture_output=True)
            got = json.loads(out.read_text())['operations']
            self.assertEqual(got, [['/items', 'get'], ['/items/special', 'get'], ['/items/{id}', 'delete']])
            # an observed op whose 2xx response has no editable schema is dropped (unless --any-schema)
            spec2 = json.loads(json.dumps(SPEC))
            spec2['paths']['/items/special']['get']['responses'] = {'default': {'description': 'x'}}
            (run / 'spec.original.json').write_text(json.dumps(spec2))
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'eligible_ops.py'), str(run),
                            '--base-path', '/api', '--out', str(out)], check=True, capture_output=True)
            d = json.loads(out.read_text())
            self.assertNotIn(['/items/special', 'get'], d['operations'])
            self.assertEqual(d['observed_without_editable_schema'], ['GET /items/special'])
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'eligible_ops.py'), str(run), '--any-schema',
                            '--base-path', '/api', '--out', str(out)], check=True, capture_output=True)
            self.assertIn(['/items/special', 'get'], json.loads(out.read_text())['operations'])
            (run / 'spec.original.json').write_text(json.dumps(SPEC))
            # round trip into specmut
            only = {tuple(o) for o in got}
            _, manifest, n = specmut.mutate(SPEC, 'RESPONSE_ORACLE', 100, 1, only=only)
            self.assertEqual(n, 3)


class LoosePool(unittest.TestCase):
    def test_format_only_and_structural_ops_are_not_eligible(self):
        import eligible_ops
        spec = json.loads(json.dumps(SPEC))
        # /items/{id}: only `format` (checker-ignored) -> not eligible; /items post: maxLength -> eligible
        spec['paths']['/items/{id}']['parameters'][0]['format'] = 'int64'
        spec['paths']['/items']['post']['parameters'] = [
            {'name': 'body', 'in': 'body', 'schema': {'type': 'object', 'properties': {'a': {'type': 'string', 'maxLength': 3}}}}]
        # int64 is asserted by conformance.py since 2026-11-14 (T24 F2): eligible; legacy pools ignore formats
        self.assertTrue(eligible_ops.loose_effective(spec, '/items/{id}', 'get'))
        self.assertFalse(eligible_ops.loose_effective(spec, '/items/{id}', 'get', legacy_formats=True))
        spec['paths']['/items/{id}']['parameters'][0]['format'] = 'uuid'  # not asserted -> not eligible
        self.assertFalse(eligible_ops.loose_effective(spec, '/items/{id}', 'get'))
        self.assertFalse(eligible_ops.loose_effective(spec, '/items', 'get'))
        self.assertTrue(eligible_ops.loose_effective(spec, '/items', 'post'))
        spec['paths']['/items']['get']['parameters'] = [{'name': 'q', 'in': 'query', 'required': True, 'type': 'string'}]
        self.assertTrue(eligible_ops.loose_effective(spec, '/items', 'get'))  # required flag counts


if __name__ == '__main__':
    unittest.main()
