"""Property checks for specmut over a folder of real specs (e.g. EMB openapi-swagger/).

Usage: python3 test_specmut.py SPEC_DIR
Checks, for every spec x fault class:
  1. the mutated spec serialises to JSON;
  2. locality: operations not listed in the manifest are byte-identical to the original;
  3. manifest fidelity: every recorded edit's `after` value is present at its pointer
     (or the key is absent when `after` is None);
  4. determinism: the same seed yields the same manifest.
"""
import copy
import glob
import hashlib
import random
import subprocess
import tempfile
import unittest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import specmut


def get(doc, pointer):
    node = doc
    for part in pointer.lstrip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(node, list):
            node = node[int(part)]
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(pointer)
    return node


def apply_manifest(base, manifest):
    """Verify every before-value and reconstruct the complete output document."""
    import copy
    doc = copy.deepcopy(base)
    for m in manifest:
        for e in m['edits']:
            if e.get('op') == 'move':
                item = doc['paths'][m['path']]
                assert item[e['before']] == e['value']
                assert e['after'] not in item
                item[e['after']] = item.pop(e['before'])
                continue
            try:
                before = get(doc, e['pointer'])
                exists = True
            except KeyError:
                before, exists = None, False
            assert exists == e['before_exists'], e
            assert before == e['before'], e
            parent_pointer, _, raw_key = e['pointer'].rpartition('/')
            parent = get(doc, parent_pointer)
            key = raw_key.replace('~1', '/').replace('~0', '~')
            if isinstance(parent, list):
                key = int(key)
            if e['after_exists']:
                parent[key] = copy.deepcopy(e['after'])
            else:
                del parent[key]
    return doc


def check(spec_path, fault, severity=30, seed=7):
    base = specmut.load_spec(spec_path)
    mutated, manifest, n_ops = specmut.mutate(base, fault, severity, seed)
    json.dumps(mutated, default=str)
    touched = {(m['path'], m['method']) for m in manifest}
    if fault == 'METHOD_SEM':
        touched |= {(m['path'], e['after']) for m in manifest for e in m['edits']}
    for path, method, op in specmut.operations(base):
        if (path, method) not in touched:
            assert mutated['paths'][path].get(method) == op, f'locality broken at {method} {path}'
    for m in manifest:
        for e in m['edits']:
            if fault == 'METHOD_SEM':
                assert e['after'] in mutated['paths'][m['path']]
                continue
            try:
                value = get(mutated, e['pointer'])
                assert e['after_exists'] and value == e['after'], f'{e["pointer"]}: {value!r} != {e["after"]!r}'
            except KeyError:
                assert not e['after_exists'], f'missing pointer {e["pointer"]}'
    assert apply_manifest(base, manifest) == mutated, 'manifest omits changes'
    again = specmut.mutate(base, fault, severity, seed)
    assert again == (mutated, manifest, n_ops), 'non-deterministic'
    return n_ops, len(manifest), sum(len(m['edits']) for m in manifest)


def main(spec_dir):
    failures, rows = [], []
    for spec_path in sorted(glob.glob(f'{spec_dir}/*.json') + glob.glob(f'{spec_dir}/*.yaml')):
        fmt = 'oas3' if specmut.is_oas3(specmut.load_spec(spec_path)) else 'sw2'
        for fault in specmut.FAULTS:
            try:
                rows.append((Path(spec_path).stem, fmt, fault) + check(spec_path, fault))
            except Exception as exc:  # report and continue
                failures.append((Path(spec_path).stem, fault, repr(exc)[:200]))
    for r in rows:
        print(f'{r[0]:28s} {r[1]:4s} {r[2]:16s} ops={r[3]:4d} mutated={r[4]:3d} edits={r[5]:5d}')
    print(f'\n{len(rows)} passed, {len(failures)} failed')
    for f in failures:
        print('FAIL', *f)
    return 1 if failures or not rows else 0


# Captured before T37 from the CLI at severity=30, seed=7. Each tuple pins
# serialized spec, serialized manifest and stdout bytes, in that order.
DEFAULT_GOLDENS = {'market': {'REQUEST_LOOSE': ['27cc577f04b5629f41a2fc73fbb576a56a536f0a21432092b7f0213e08d68660',
                              'b0416dddcf111defa7ac1ca316e14c6e4a199dbc65609174e7f4c9f053331962',
                              '9efc82538ea1dbcb5aade87afa71f6acb78141366b59da1b62ee1a53c4900fda'],
            'REQUEST_STRICT': ['9c411e6f174e4c903b265ee1ed9f917b78628b88529a1184a6eb761c825ccf56',
                               '434cda1ffbf52e76c0e73e2194cfc9c3817fe145d4b9b07e24438f57f8d36aec',
                               'ccdcb799bf74f9d1b8264e20e8a553f6815da13e84680a70a5b1752ca1364d87'],
            'RESPONSE_ORACLE': ['6837b14e5f182eddc12d39f7d988990fbf055aba51c85a695a544103b8dea78c',
                                'b4aa0ee971eb7e3d9d8db11474ab73800f9f2d554003a854fe52e51650896d54',
                                'eb9e3b74af667fa5d8d50bd704428634881182312f4a094d69a21b60545e7c52'],
            'METHOD_SEM': ['4e14887d32554e08deb702de567de1cb5aa1d5a159ab2f9107ede34de1ec79da',
                           '8492082ef04c7b7846aff40c185a32af22214d79c0df3655f7c64cf5c389f5de',
                           '33d1ca3ee00daea60599c0530aae4870d636ebd3864922e45578353823fda772']},
 'scout-api': {'REQUEST_LOOSE': ['99fab0787b231de60a52b373d8d86b2f0fc4c0c9aabd066284182ac414448a2a',
                                 '1f2f00ad2717edfc09a77438421c10760fa8cb82d7267febe48cb7b05963065e',
                                 '0faecc3d547e3886e1dc8df1fcb69c75095565283032b1b5c13b2d6de9c73ae0'],
               'REQUEST_STRICT': ['2b25965451b31263a7fa049ff19ad5547069f68ce978db2d9257a857999ee1f5',
                                  'a938ca29d46efad8b519a288c360a372531139c924eb6bb7bd9ab1503b8c0ee4',
                                  '13b80f27da8c0d7d16d8d10a501347bcb530c79e2cb9b5132397240f7b3df769'],
               'RESPONSE_ORACLE': ['744bff3f3183f8edce18319153ba9e0aa99dafb067056b2a4e245fbb5f577652',
                                   '9c8ec714ea4ecdc02cbc93e417895fedcd74bd4fbb8fdb37dfc8d3c5d25725ca',
                                   'fcc1f8d491dfeecb6b2dacfa7bd7ad37537f75bfc8a4a1ee68a199b13a3c76bc'],
               'METHOD_SEM': ['6754bb249689d412ed0dd43bba300dc6d4ae2259c9ae9130b0ad089f9957269d',
                              '5501ed0d7b77436d720c581dbe20382f29785fbefe04d69b05546ddffb60c3d4',
                              '1dff718c1afa0831c67b4e7473d156d761a6c5af85b05d3e1c53719118f350e1']},
 'swagger-petstore': {'REQUEST_LOOSE': ['514fbb73c79b51332557704b31ac44c120619590a704e70ccc34f107d3b6a14d',
                                        'cfdfb002256296fa4bd436c52f573b2766fe7caac9de2507ff00e764fe59cbb9',
                                        'b760c57f70fb57bc8043f1e1401589a2aaac86b78b8fc13e8dade6e6dfb22210'],
                      'REQUEST_STRICT': ['c874e3ea79d71b4540e87507e3e837ffe67c2ae40e432a158a7ed30376dd3cba',
                                         '01375d46bdd5936a13a4eb1df495500bc23292f597ed0410224a31c50cbe0999',
                                         '34119de7dfc0b9ba645e6a42038c7094b8c0019597ee073d8618e08cc0030586'],
                      'RESPONSE_ORACLE': ['43028b197d283e51ad1010e7aef7629657300b9dd7ac4da0e0b61a8fa0514ee5',
                                          'aed9f52f1ad9e854d86357b8bf168bb0cce746d06dfbed07958dc33a037633ee',
                                          'c91a4c5f8872eb0ca8c79005939150b7ee9a592bd4ffc7eddca430b887c4f873'],
                      'METHOD_SEM': ['4b7f46801158bc8680825dca4263bd285e9b70f9bd3f706955237fae35d48579',
                                     '799d29ec4a9f87c82b9b331da28bb14088b10bde581417cf744c6af2a5f37f0d',
                                     'ba59d9b8959b68878e2fca88f94a622d17735e7b80cefb74c2d7628b10dee432']},
 'cwa-verification': {'REQUEST_LOOSE': ['bde2994969bdfc69e69a8ac3ec7b81f4d469c201ea844b43c6636d83b99c5f69',
                                        '152f535a3bc18e2e6c8bf12bf356e214fc3b64fa10eb240ab6d68843e33dfbf2',
                                        '60e73e5f64991dc43fa2f81038d483e594e7ab84ef2b40719846160043db668c'],
                      'REQUEST_STRICT': ['7845bea504245a00a60c74963f3068099f7f1f1aeee3baccac63580e721cabc7',
                                         '0a2daf7ee895c9d2ce918ee4631d73c8f6d5ef1533d5be854dbe3132403701ce',
                                         'a31c101c7fb22b1ab38f6ed7bb84c09dec44d7f464eacf1a1b98dbf7fd8145aa'],
                      'RESPONSE_ORACLE': ['630449ac9f374b25dfc1a95e79d6c297c76133f1ec083a899a0236629b67b33c',
                                          'c77750dee895dd933bd279a9e2a861cd11005458d24434250a6fb395b0d10587',
                                          '47770c11a3d5a3c9d04ddac4231836299be87f0d758ccc3d5a1a88b57fe3f849'],
                      'METHOD_SEM': ['75e885329a74eff7491178b92c2978e9c8e55d54d2c913c4f46666abeb30953d',
                                     'd0fd77960c672401832ade0dc008e724f3d52cc2c481e2f0ee93971cbb25ae5e',
                                     '4d12540cd2959ccd388f4e1801425a7ea871ec722357c44f60d511b21dc3e32c']}}
ROOT = Path(__file__).resolve().parents[2]


def strict_fixture():
    def op(params):
        return {'parameters': params, 'responses': {'200': {'description': 'ok'}}}

    def body(schema):
        return {'in': 'body', 'name': 'body', 'schema': schema}

    return {'swagger': '2.0', 'paths': {
        '/number': {'post': op([body({'type': 'number', 'maximum': 10})])},
        '/string': {'post': op([body({'type': 'string', 'maxLength': 20})])},
        '/object': {'post': op([body({'type': 'object', 'properties': {'flag': {'type': 'boolean'}}})])},
        '/parameter': {'get': op([{'in': 'query', 'name': 'flag', 'type': 'boolean'}])},
        '/none': {'post': op([body({'type': 'string', 'enum': ['fixed']})])},
        '/mixed': {'post': op([{'in': 'header', 'name': 'flag', 'type': 'boolean'},
            body({'type': 'object', 'properties': {
                'n': {'type': 'integer'}, 's': {'type': 'string'},
                'items': {'type': 'array', 'items': {'type': 'object', 'properties': {
                    'nested': {'type': 'string'}}}},
                'all': {'allOf': [{'type': 'number', 'maximum': 4}]},
                'enum': {'type': 'string', 'enum': ['long']},
                'format': {'type': 'string', 'format': 'date'}}})])}}}


def cli(source, fault='REQUEST_STRICT', extra=()):
    with tempfile.TemporaryDirectory(prefix='t37-specmut-') as directory:
        out = Path(directory) / 'output'
        result = subprocess.run(['/usr/bin/python3', '-I', '-B', str(Path(specmut.__file__)),
            str(source), '--fault', fault, '--severity', '30', '--seed', '7',
            '--out', str(out), *extra], cwd=ROOT, capture_output=True)
        files = {p.name: p.read_bytes() for p in out.glob('*')}
        return result, files


def family(edit):
    key = edit['pointer'].rsplit('/', 1)[1]
    return 'param_required' if key == 'required' and isinstance(edit['after'], bool) else key


class StrictKeywordTests(unittest.TestCase):
    def test_default_cli_bytes_match_pre_T37_goldens_all_faults(self):
        for name, cases in DEFAULT_GOLDENS.items():
            source = Path('08_experiments/_external/emb/openapi-swagger') / (name + '.json')
            for fault, expected in cases.items():
                with self.subTest(spec=name, fault=fault):
                    result, files = cli(source, fault)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    stem = name + '__' + fault.lower() + '__p30__s7'
                    actual = [hashlib.sha256(files[stem + suffix]).hexdigest()
                              for suffix in ('.json', '.manifest.json')]
                    actual.append(hashlib.sha256(result.stdout).hexdigest())
                    self.assertEqual(actual, expected)
                    meta = json.loads(files[stem + '.manifest.json'])
                    self.assertNotIn('strict_keywords', meta)
                    self.assertNotIn('selected_no_edit', meta)

    def test_each_keyword_is_exact_subset_and_manifest_reconstructs_output(self):
        base = strict_fixture()
        _, full_manifest, count = specmut.mutate(base, 'REQUEST_STRICT', 100, 1)
        for keyword in specmut.STRICT_KEYWORDS:
            with self.subTest(keyword=keyword):
                actual, manifest, n = specmut.mutate(base, 'REQUEST_STRICT', 100, 1,
                                                    strict_keywords=[keyword])
                expected = copy.deepcopy(base)
                kept = []
                for mutation in full_manifest:
                    edits = [e for e in mutation['edits'] if family(e) == keyword]
                    if edits:
                        kept.append({**mutation, 'edits': edits})
                expected = apply_manifest(expected, kept)
                self.assertEqual(manifest, kept)
                self.assertEqual(actual, expected)
                self.assertEqual(apply_manifest(base, manifest), actual)
                self.assertEqual(n, count)
                self.assertEqual(base, strict_fixture())

    def test_selection_keeps_noop_candidates_seed_severity_exclude_and_only(self):
        base = strict_fixture()
        only = {('/mixed', 'post'), ('/none', 'post'), ('/parameter', 'get'), ('/number', 'post')}
        for exclude, pool in (((), None), (('/number',), None), ((), only), (('/number',), only)):
            candidates = [(p, m) for p, m, _ in specmut.operations(base)
                          if p not in exclude and (pool is None or (p, m) in pool)]
            for severity in (0, 1, 30, 100):
                for seed in (0, 1, 7):
                    k = max(1, round(len(candidates) * severity / 100)) if candidates and severity else 0
                    expected = sorted(random.Random(f'{seed}:REQUEST_STRICT').sample(candidates, k))
                    chosen, n = specmut.select_operations(base, 'REQUEST_STRICT', severity, seed, exclude, pool)
                    self.assertEqual(chosen, expected)
                    self.assertEqual(n, len(candidates))
                    for keywords in ([k] for k in specmut.STRICT_KEYWORDS):
                        _, manifest, total = specmut.mutate(base, 'REQUEST_STRICT', severity, seed,
                                                           exclude, pool, keywords)
                        self.assertEqual(total, n)
                        self.assertTrue({(m['path'], m['method']) for m in manifest} <= set(chosen))
        # A keyword with no possible edit must not cause resampling.
        result, manifest, _ = specmut.mutate(base, 'REQUEST_STRICT', 100, 1,
                                            only={('/none', 'post')}, strict_keywords=['maximum'])
        self.assertEqual(result, base)
        self.assertEqual(manifest, [])

    def test_cli_selected_no_edit_is_disjoint_and_complete(self):
        with tempfile.TemporaryDirectory(prefix='t37-selection-') as directory:
            source = Path(directory) / 'fixture.json'
            source.write_text(json.dumps(strict_fixture()))
            pool = Path(directory) / 'pool.json'
            pool.write_text(json.dumps({'operations': [['/none', 'post'], ['/mixed', 'post'],
                                                       ['/object', 'post'], ['/number', 'post']]}))
            candidates = [('/mixed', 'post'), ('/none', 'post'), ('/object', 'post')]
            for keywords in ('maximum', 'maxLength', 'required', 'param_required', 'maximum,maxLength'):
                for seed in (1, 2, 3):
                    for severity in (0, 1, 30, 100):
                        result, files = cli(source, extra=['--strict-keywords', keywords, '--severity', str(severity),
                            '--seed', str(seed), '--exclude', '/number', '--only-ops', str(pool)])
                        self.assertEqual(result.returncode, 0, result.stderr)
                        meta = json.loads(next(v for k, v in files.items() if k.endswith('.manifest.json')))
                        k = max(1, round(len(candidates) * severity / 100)) if severity else 0
                        chosen = set(random.Random(f'{seed}:REQUEST_STRICT').sample(candidates, k))
                        edited = {(m['path'], m['method']) for m in meta['mutations']}
                        skipped = {tuple(o) for o in meta['selected_no_edit']}
                        self.assertFalse(edited & skipped)
                        self.assertEqual(edited | skipped, chosen)
                        self.assertEqual(('/none', 'post') in skipped, ('/none', 'post') in chosen)
                        self.assertEqual(meta['strict_keywords'], sorted(keywords.split(',')))
                        self.assertEqual(meta['operations_mutated'], len(edited))

    def test_cli_empty_retained_edit_set_restores_spec(self):
        with tempfile.TemporaryDirectory(prefix='t37-empty-') as directory:
            source = Path(directory) / 'fixture.json'
            source.write_text(json.dumps(strict_fixture()))
            pool = Path(directory) / 'pool.json'
            for operations in ([], [['/none', 'post']]):
                pool.write_text(json.dumps({'operations': operations}))
                result, files = cli(source, extra=['--strict-keywords', 'maximum', '--severity', '100',
                                                   '--only-ops', str(pool)])
                self.assertEqual(result.returncode, 0, result.stderr)
                meta = json.loads(next(v for k, v in files.items() if k.endswith('.manifest.json')))
                self.assertEqual(meta['mutations'], [])
                self.assertEqual(meta['operations_mutated'], 0)
                self.assertEqual(meta['selected_no_edit'], operations)
                output = json.loads(next(v for k, v in files.items() if not k.endswith('.manifest.json')))
                self.assertEqual(output, strict_fixture())

    def test_explicit_all_matches_default_spec_manifest_edits_and_stdout(self):
        source = Path('08_experiments/_external/emb/openapi-swagger/market.json')
        default, files = cli(source)
        explicit, other = cli(source, extra=['--strict-keywords', ','.join(specmut.STRICT_KEYWORDS)])
        self.assertEqual(default.stdout, explicit.stdout)
        for name, content in files.items():
            if name.endswith('.manifest.json'):
                meta = json.loads(other[name])
                self.assertEqual(meta.pop('strict_keywords'), sorted(specmut.STRICT_KEYWORDS))
                meta.pop('selected_no_edit')  # Includes pre-existing no-op selections, if any.
                self.assertEqual(meta, json.loads(content))
            else:
                self.assertEqual(other[name], content)

    def test_refs_path_parameters_and_oas3_preserve_only_retained_changes(self):
        for version in ('swagger', 'openapi'):
            schema = {'type': 'object', 'properties': {'a/b~': {'type': 'string'}, 'n': {'type': 'integer'}}}
            if version == 'swagger':
                base = {'swagger': '2.0', 'definitions': {'Node': schema}, 'paths': {'/x': {
                    'parameters': [{'in': 'query', 'name': 'q', 'type': 'boolean'}],
                    'post': {'parameters': [{'in': 'body', 'name': 'body', 'schema': {'$ref': '#/definitions/Node'}}]}}}}
            else:
                base = {'openapi': '3.0.3', 'components': {'schemas': {'Node': schema}}, 'paths': {'/x': {
                    'parameters': [{'in': 'header', 'name': 'h', 'schema': {'type': 'boolean'}}],
                    'post': {'requestBody': {'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Node'}}}}}}}}
            for keyword in specmut.STRICT_KEYWORDS:
                actual, manifest, _ = specmut.mutate(base, 'REQUEST_STRICT', 100, 1, strict_keywords=[keyword])
                self.assertEqual(apply_manifest(base, manifest), actual)
                op = actual['paths']['/x']['post']
                if version == 'swagger':
                    value = op['parameters'][0]['schema']
                else:
                    value = op['requestBody']['content']['application/json']['schema']
                self.assertEqual(value.get('required'), ['a/b~', 'n'] if keyword == 'required' else None)
                self.assertEqual(value['properties']['n'].get('maximum'), 0 if keyword == 'maximum' else None)
                self.assertEqual(value['properties']['a/b~'].get('maxLength'), 1 if keyword == 'maxLength' else None)
                parameter = next(p for p in op['parameters'] if p['in'] in ('query', 'header'))
                self.assertEqual(parameter.get('required'), True if keyword == 'param_required' else None)

    def test_no_filtered_edit_undoes_structural_side_effects(self):
        base = {'swagger': '2.0', 'definitions': {'Node': {'type': 'string'}}, 'paths': {'/x': {
            'parameters': [{'in': 'query', 'name': 'q', 'type': 'boolean', 'required': True}],
            'post': {'parameters': [{'in': 'body', 'name': 'body', 'schema': {'$ref': '#/definitions/Node'}}]}}}}
        actual, manifest, _ = specmut.mutate(base, 'REQUEST_STRICT', 100, 1, strict_keywords=['required'])
        self.assertEqual(actual, base)
        self.assertEqual(manifest, [])

    def test_cli_errors_exit_2_before_output_without_echoing_value(self):
        for keywords in ('', 'Maximum', 'maximum,', ',required', 'required,required',
                         'maximum, required', 'synthetic-private-value', 'maximum\n'):
            result, files = cli('missing.json', extra=['--strict-keywords', keywords])
            self.assertEqual(result.returncode, 2)
            self.assertEqual(files, {})
            if keywords:
                self.assertNotIn(keywords.encode(), result.stdout + result.stderr)
        for fault in specmut.FAULTS:
            if fault != 'REQUEST_STRICT':
                result, files = cli('missing.json', fault, ['--strict-keywords', 'maximum'])
                self.assertEqual(result.returncode, 2)
                self.assertEqual(files, {})

    def test_library_rejects_invalid_keywords_or_fault(self):
        for keywords in ([], ['invalid'], ['required', 'required'], ['maximum', '']):
            with self.assertRaises(ValueError):
                specmut.mutate(strict_fixture(), 'REQUEST_STRICT', 30, 1, strict_keywords=keywords)
        with self.assertRaises(ValueError):
            specmut.mutate(strict_fixture(), 'METHOD_SEM', 30, 1, strict_keywords=['maximum'])


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StrictKeywordTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(main(sys.argv[1]) if result.wasSuccessful() else 1)
