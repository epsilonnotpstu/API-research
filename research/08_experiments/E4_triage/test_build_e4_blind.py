#!/usr/bin/env python3
"""Offline behavioral tests; synthetic inputs, real repository mutation/checker APIs."""
import collections
import contextlib
import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
module_spec = importlib.util.spec_from_file_location('builder', HERE / 'build_e4_blind.py')
b = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(b)


def fixture(root):
    config = {'suts': {}, 'labels': root / 'labels.csv', 'codebook': root / 'codebook.md',
              'task_reference': root / 'task.md', 'fixtures': [root / 'auth.yaml'],
              'kind_source': b.EXPERIMENTS / 'E1_pilot/pilot_results/fuzzer_compare.py'}
    config['codebook'].write_text('Independent contract review rules.\n')
    config['task_reference'].write_text('Independent task.\n')
    config['fixtures'][0].write_text(json.dumps({'auth': [{'fixedHeaders': [
        {'name': 'Authorization', 'value': 'Bearer synthetic-test-secret-9a7b'}]}]}))
    finals = []
    for sut in ('alpha', 'beta', 'gamma', 'delta'):
        base = root / sut
        run = base / 'run'
        source = base / 'upstream'
        run.mkdir(parents=True)
        source.mkdir()
        (source / 'App.java').write_bytes(b'class App { /* original bytes */ }\r\n')
        (source / 'target').mkdir()
        (source / 'target/ignored.jar').write_bytes(b'not executable')
        (source / '.git').mkdir()
        (source / '.git/config').write_text('not copied')
        original = {'swagger': '2.0', 'info': {'title': sut, 'version': '1'}, 'paths': {}}
        exchanges = []
        for n in range(16):
            path = f'/op{n}'
            original['paths'][path] = {'get': {
                'operationId': f'op{n}', 'parameters': [
                    {'name': 'amount', 'in': 'query', 'type': 'integer', 'maximum': 10},
                    {'name': 'optional', 'in': 'query', 'type': 'string', 'maxLength': 12}],
                'responses': {'200': {'description': 'OK', 'schema': {
                    'type': 'object', 'properties': {'id': {'type': 'integer'},
                                                     'name': {'type': 'string'}}, 'required': ['id']}},
                              '400': {'description': 'Bad request'},
                              '500': {'description': 'Server error'}}}}
            for status, amount in [(200, '5'), (400, '20')]:
                exchanges.append({'request': {'method': 'GET', 'path': path,
                                  'query': {'amount': [amount]}, 'headers': {
                                      'Authorization': 'Bearer synthetic-test-secret-9a7b',
                                      'Cookie': 'session=synthetic-cookie-738a'}, 'body': {}},
                                  'response': {'status': status, 'headers': {'content-type': 'application/json'},
                                               'body': {'text': '{"id":"wrong"}'}}})
        # Duplicate a violating exchange, with dirty transport. Selection must use
        # another occurrence and retain zero-based indices through redaction.
        dirty = copy.deepcopy(exchanges[0])
        dirty['request']['headers']['x-query'] = 'bad\ntransport'
        exchanges.insert(0, dirty)
        (run / 'exchanges.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in exchanges))
        (run / 'compose.log').write_text('Server ready\nBearer synthetic-test-secret-9a7b\n')
        b.dump(run / 'run.json', {'seed': 1, 'fault': 'NONE', 'complete': True, 'sut': sut})
        b.dump(run / 'spec.original.json', original)
        b.dump(base / 'upstream-spec.json', original)
        violations = b.replay(original, exchanges, 'http://sut:8080')
        by_fp = {v['fingerprint']: v for v in violations}
        blind, adj = [], []
        for i, (fp, v) in enumerate(sorted(by_fp.items()), 1):
            item = {'item_id': f'B{i:03d}', 'method': v['method'], 'template': v['template'],
                    'status': str(v['status']), 'kind': v['kind']}
            blind.append(dict(item, fingerprint=json.dumps(fp) if i % 2 else fp))
            adj.append(item)
            finals.append(dict(item, sut=sut, final_L1=('IMPL', 'SPEC', 'TEST')[i % 3]))
        b.write_csv(base / 'blind.csv', list(blind[0]), blind)
        b.write_csv(base / 'adjudication.csv', list(adj[0]), adj)
        config['suts'][sut] = {'run': run, 'source': source, 'emb_spec': base / 'upstream-spec.json',
                               'blind_sheet': base / 'blind.csv', 'adjudication': base / 'adjudication.csv',
                               'origin': 'http://sut:8080', 'source_omit': []}
    b.write_csv(config['labels'], list(finals[0]), finals)
    return config


def apply_patch_record(spec, edit):
    """Test oracle: reconstruct the entire document from the recorded patches."""
    def parts(pointer):
        return [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    def parent(pointer):
        keys = parts(pointer)
        node = spec
        for key in keys[:-1]:
            node = node[int(key)] if isinstance(node, list) else node[key]
        return node, keys[-1]
    if edit['op'] == 'move':
        src, key = parent(edit['from'])
        value = src.pop(key)
        dest, key = parent(edit['target'])
        dest[key] = value
    else:
        node, key = parent(edit['pointer'])
        key = int(key) if isinstance(node, list) else key
        if edit['after_exists']:
            node[key] = copy.deepcopy(edit['after'])
        else:
            del node[key]


class FullBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='t40-tests-')
        cls.root = Path(cls.tmp.name)
        cls.config = fixture(cls.root)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.log = b.build(cls.config, cls.root / 'one', cls.root / 'hidden-one')
            b.build(cls.config, cls.root / 'two', cls.root / 'hidden-two')
        cls.out = cls.root / 'one'
        cls.hidden = cls.root / 'hidden-one'
        cls.key = b.rows(cls.hidden / 'e4_key.csv')
        cls.items = b.rows(cls.out / 'items.csv')
        cls.manifests = json.loads((cls.hidden / 'e4_manifest.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_two_complete_builds_are_byte_identical(self):
        for first, second in [('one', 'two'), ('hidden-one', 'hidden-two')]:
            self.assertEqual(b.tree_entries(self.root / first), b.tree_entries(self.root / second))

    def test_disjoint_sets_and_both_method_identities_reserved(self):
        for manifest in self.manifests.values():
            occupied = set()
            for stage in manifest['stages']:
                ops = {tuple(op) for op in stage['only_ops']}
                self.assertFalse(ops & occupied)
                self.assertTrue(occupied <= {tuple(op) for op in stage['occupied_after']})
                occupied = {tuple(op) for op in stage['occupied_after']}
            self.assertEqual(manifest['stages'][0]['fault'], 'METHOD_SEM')
            for mutation in manifest['mutations']:
                if mutation['fault'] == 'METHOD_SEM':
                    self.assertIn([mutation['path'], mutation['edits'][0]['after']],
                                  manifest['stages'][0]['occupied_after'])

    def test_composite_validity_and_complete_patch_reconstruction(self):
        for sut, manifest in self.manifests.items():
            original = json.loads((self.config['suts'][sut]['run'] / 'spec.original.json').read_text())
            rebuilt = copy.deepcopy(original)
            for mutation in manifest['mutations']:
                for edit in mutation['edits']:
                    apply_patch_record(rebuilt, edit)
            pkg = self.out / self.log['package_by_sut'][sut]
            composite = json.loads((pkg / 'spec.json').read_text())
            self.assertEqual(rebuilt, composite)
            parsed = b.checker.Spec(composite)
            self.assertEqual(len(list(b.specmut.operations(original))), len(parsed.routes))
            b.assert_no_new_extensions(original, composite)

    def test_actual_items_kind_filter_and_persistent_label_join(self):
        kinds = b.expected_kinds(self.config['kind_source'])
        items = {r['item_id']: r for r in self.items}
        observed = collections.Counter()
        for key in self.key:
            item = items[key['item_id']]
            records = [json.loads(line) for line in
                       (self.hidden / 'replay' / f"{key['sut']}.attribution.jsonl").read_text().splitlines()]
            row = next(r for r in records if r['fingerprint'] == key['fingerprint'])
            if key['role'] == 'injected':
                self.assertTrue(b.injected_candidate(row, kinds))
                self.assertEqual(key['expected_L1'], 'SPEC')
                self.assertIn(item['kind'], kinds[key['fault']])
                self.assertTrue(json.loads(key['edit_pointers']))
                observed[key['sut'], key['fault']] += 1
            else:
                self.assertEqual(row['status'], 'PERSISTENT')
                self.assertTrue(key['baseline_item_id'])
                self.assertEqual(key['expected_L1'], key['final_L1'])
        self.assertTrue(all(n <= 3 for n in observed.values()))
        self.assertEqual(set(k['fault'] for k in self.key if k['role'] == 'injected'), set(b.specmut.FAULTS))
        for sut in self.config['suts']:
            self.assertLessEqual(sum(k['sut'] == sut and k['role'] == 'decoy' for k in self.key), 6)

    def test_clean_examples_and_redaction_preserves_checker_results(self):
        for item in self.items:
            exchanges = [json.loads(line) for line in
                         (self.out / item['package'] / 'r1/exchanges.jsonl').read_text().splitlines()]
            example = exchanges[int(item['example_exchange'])]
            self.assertTrue(b.clean(example))
            self.assertEqual(example['request']['headers']['Authorization'], '<redacted>')
        self.assertTrue(all(v['redaction_preserves_all_checker_fingerprints']
                            for v in self.log['replay'].values()))

    def test_sources_byte_identical_and_ignored_paths_absent(self):
        for sut, audit in self.log['source_audit'].items():
            root = self.out / self.log['package_by_sut'][sut] / 'source'
            self.assertEqual(audit['sha256'], audit['copied_sha256'])
            self.assertEqual(audit['files'], b.tree_entries(root))
            self.assertFalse((root / 'target').exists())
            self.assertFalse((root / '.git').exists())

    def test_decoy_sampling_balances_label_strata(self):
        for sut, counts in self.log['counts'].items():
            strata = counts['decoy']['selected_by_final_L1']
            self.assertEqual(set(strata), {'SPEC', 'IMPL', 'TEST'})
            self.assertEqual(set(strata.values()), {2})

    def test_no_added_extension_and_codebook_byte_identity(self):
        self.assertEqual((self.out / 'CODEBOOK_v0.6.md').read_bytes(), self.config['codebook'].read_bytes())
        with self.assertRaisesRegex(ValueError, 'vendor extension'):
            b.assert_no_new_extensions({'paths': {}}, {'paths': {}, 'x-hidden': 'marker'})

    def test_package_has_no_original_spec_or_secret(self):
        originals = [json.loads(c['emb_spec'].read_text()) for c in self.config['suts'].values()]
        b.assert_no_original_specs(self.out, originals)
        b.assert_no_credentials(self.out, {b'Bearer synthetic-test-secret-9a7b',
                                           b'session=synthetic-cookie-738a'})
        for pkg in self.out.glob('K*'):
            self.assertEqual([p.name for p in pkg.iterdir() if p.is_file()], ['spec.json'])

    def test_refuse_existing_blind_or_hidden_output_without_changes(self):
        snapshot = b.tree_entries(self.out)
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            b.build(self.config, self.out, self.root / 'unused-hidden')
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            b.build(self.config, self.root / 'unused-out', self.hidden)
        self.assertEqual(snapshot, b.tree_entries(self.out))
        self.assertFalse((self.root / 'unused-out').exists())
        self.assertFalse((self.root / 'unused-hidden').exists())


class AssertionTests(unittest.TestCase):
    def test_collateral_or_persistent_kinds_rejected(self):
        kinds = b.expected_kinds(b.EXPERIMENTS / 'E1_pilot/pilot_results/fuzzer_compare.py')
        row = {'status': 'NEW', 'op_mutated': True, 'fault': 'REQUEST_LOOSE', 'kind': 'RESPONSE_SCHEMA'}
        self.assertFalse(b.injected_candidate(row, kinds))
        row['kind'] = 'VALID_REJECTED'
        self.assertTrue(b.injected_candidate(row, kinds))
        row['status'] = 'PERSISTENT'
        self.assertFalse(b.injected_candidate(row, kinds))
        row.update(status='NEW', op_mutated=False)
        self.assertFalse(b.injected_candidate(row, kinds))

    def test_no_original_spec_assertion_catches_copy_under_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'K01/source').mkdir(parents=True)
            original = {'openapi': '3.0.0', 'info': {'title': 'API', 'version': '1'}, 'paths': {}}
            b.dump(root / 'K01/source/api-docs.json', original)
            with self.assertRaisesRegex(ValueError, 'Original spec embedded'):
                b.assert_no_original_specs(root, [original])

    def test_no_original_spec_assertion_also_catches_near_equivalent_under_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'K01/source').mkdir(parents=True)
            original = {'openapi': '3.0.0', 'info': {'title': 'API', 'version': '1'}, 'paths': {}}
            near = copy.deepcopy(original)
            near['info']['version'] = '2'
            (root / 'K01/source/openapi.yaml').write_text(b.specmut.yaml.safe_dump(near))
            with self.assertRaisesRegex(ValueError, 'Original spec embedded'):
                b.assert_no_original_specs(root, [original])

    def test_credentials_assertion_scans_source_and_does_not_echo_value(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'K01/source').mkdir(parents=True)
            (root / 'K01/source/README.md').write_text('credential=synthetic-secret-4372')
            with self.assertRaises(ValueError) as caught:
                b.assert_no_credentials(root, {b'synthetic-secret-4372'})
            self.assertNotIn('synthetic-secret-4372', str(caught.exception))

    def test_unredacted_cookie_header_fails_even_without_known_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'K01/r1').mkdir(parents=True)
            (root / 'K01/r1/exchanges.jsonl').write_text(json.dumps({
                'request': {'headers': {'cOoKiE': 'session=unexpected'}}, 'response': {}}) + '\n')
            with self.assertRaisesRegex(ValueError, 'Unredacted'):
                b.assert_no_credentials(root, set())

    def test_keyword_boundaries_source_exemption_and_traffic_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'K01/source').mkdir(parents=True)
            (root / 'K01/source/App.java').write_text('mutation E4 Inject')
            (root / 'TASK_M1.md').write_text('dependency injection, E40, mutations')
            self.assertEqual(b.blinding_hits(root, set()), [])
            (root / 'TASK_M1.md').write_text('E4')
            with self.assertRaisesRegex(ValueError, 'blinding keyword'):
                b.blinding_hits(root, {'E4'})
            (root / 'TASK_M1.md').unlink()
            (root / 'K01/r1').mkdir()
            (root / 'K01/r1/compose.log').write_text('E4 from traffic')
            self.assertEqual(len(b.blinding_hits(root, {'E4'})), 1)

    def test_codebook_exception_requires_byte_identity_and_explicit_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'CODEBOOK_v0.6.md').write_bytes(b'mutation in unchanged reference\n')
            with self.assertRaisesRegex(ValueError, 'blinding keyword'):
                b.blinding_hits(root, set())
            self.assertEqual(b.blinding_hits(root, set(), b'mutation in unchanged reference\n'), [])
            with self.assertRaisesRegex(ValueError, 'codebook changed'):
                b.blinding_hits(root, set(), b'different reference\n')

    def test_control_bytes_nested_and_encoded(self):
        x = {'request': {'path': '/ok', 'query': {'q': ['good', 'bad\n']}, 'headers': {}}}
        self.assertFalse(b.clean(x))
        x['request']['query'] = {}
        x['request']['path'] = '/%00bad'
        self.assertFalse(b.clean(x))
        x['request']['path'] = '/ok'
        x['request']['headers'] = {'bad\rname': 'ok'}
        self.assertFalse(b.clean(x))

    def test_method_collision_never_overwrites_existing_verb(self):
        original = {'swagger': '2.0', 'paths': {'/a': {'get': {'responses': {}}, 'post': {'responses': {}}}}}
        current, edits, _ = b.specmut.mutate(original, 'METHOD_SEM', 100, b.SEED, only={('/a', 'get')})
        self.assertEqual(current, original)
        self.assertEqual(edits, [])

    def test_source_original_preflight_does_not_reserve_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = fixture(root)
            conf = config['suts']['alpha']
            (conf['source'] / 'api-docs.json').write_bytes(conf['emb_spec'].read_bytes())
            config['approved_source_specs'] = {'alpha': {'api-docs.json': 'exact_byte_copy'}}
            audit = b.audit_source_specs(config)['alpha']['spec_like']
            self.assertEqual(audit[0]['file'], 'api-docs.json')
            self.assertEqual(audit[0]['justification'], 'exact_byte_copy')
            with self.assertRaisesRegex(ValueError, 'source-copy constraint'):
                b.build(config, root / 'out', root / 'hidden')
            self.assertFalse((root / 'out').exists())
            self.assertFalse((root / 'hidden').exists())
            b.configure_source_omissions(config, ['alpha:api-docs.json'])
            self.assertEqual(len(b.audit_source_specs(config)['alpha']['spec_like']), 1)
            self.assertNotIn('api-docs.json', b.tree_entries(conf['source'], conf['source_omit']))
            with self.assertRaisesRegex(ValueError, 'not an approved source spec equivalent'):
                b.configure_source_omissions(config, ['beta:App.java'])

    def test_explicit_policies_preserve_sources_and_unchanged_codebook(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = fixture(root)
            conf = config['suts']['alpha']
            embedded = conf['source'] / 'api-docs.json'
            embedded.write_bytes(conf['emb_spec'].read_bytes())
            near_conf = config['suts']['beta']
            near = json.loads(near_conf['emb_spec'].read_bytes())
            for path in sorted(near['paths'])[:8]:
                near['paths'][path]['get']['description'] = 'Alternate upstream documentation'
            near_file = near_conf['source'] / 'openapi.yaml'
            near_file.write_text(b.specmut.yaml.safe_dump(near, sort_keys=True))
            config['approved_source_specs'] = {
                'alpha': {'api-docs.json': 'exact_byte_copy'},
                'beta': {'openapi.yaml': 'semantic_near_equivalent_same_path_set'}}
            config['codebook'].write_text('Inherited mutation vocabulary.\n')
            b.configure_source_omissions(config, ['alpha:api-docs.json', 'beta:openapi.yaml'])
            with self.assertRaisesRegex(ValueError, 'unchanged-copy constraint'):
                b.build(config, root / 'out', root / 'hidden')
            self.assertFalse((root / 'out').exists())
            config['allow_inherited_codebook'] = True
            with contextlib.redirect_stdout(io.StringIO()):
                log = b.build(config, root / 'out', root / 'hidden')
                b.build(config, root / 'out-two', root / 'hidden-two')
            self.assertEqual(b.tree_entries(root / 'out'), b.tree_entries(root / 'out-two'))
            self.assertEqual(b.tree_entries(root / 'hidden'), b.tree_entries(root / 'hidden-two'))
            self.assertEqual(log['inherited_codebook_keyword_hits'], [{'line': 1, 'token': 'mutation'}])
            self.assertTrue(embedded.exists())
            self.assertEqual(log['source_audit']['alpha']['omitted_file_sha256'],
                             {'api-docs.json': b.sha(embedded.read_bytes())})
            pkg = root / 'out' / log['package_by_sut']['alpha']
            self.assertFalse((pkg / 'source/api-docs.json').exists())
            self.assertEqual((root / 'out/CODEBOOK_v0.6.md').read_bytes(), config['codebook'].read_bytes())
            near_audit = log['source_audit']['beta']['omitted_spec_audit'][0]
            self.assertEqual(near_audit['justification'], 'semantic_near_equivalent_same_path_set')
            self.assertEqual(near_audit['path_count'], 16)
            self.assertEqual(near_audit['identical_path_count'], 8)
            self.assertEqual(near_audit['different_path_count'], 8)
            self.assertTrue(near_audit['path_set_equal'])
            self.assertTrue(near_file.exists())
            near_pkg = root / 'out' / log['package_by_sut']['beta']
            self.assertFalse((near_pkg / 'source/openapi.yaml').exists())

    def test_unapproved_spec_like_source_stops_even_when_equivalent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = fixture(root)
            conf = config['suts']['gamma']
            (conf['source'] / 'unexpected.YAML').write_text(
                b.specmut.yaml.safe_dump(json.loads(conf['emb_spec'].read_bytes())))
            with self.assertRaisesRegex(ValueError, 'Unexpected spec-like source file; stop and report'):
                b.configure_source_omissions(config, ['gamma:unexpected.YAML'])
            with self.assertRaisesRegex(ValueError, 'Unexpected spec-like source file; stop and report'):
                b.build(config, root / 'out', root / 'hidden')
            self.assertFalse((root / 'out').exists())
            self.assertFalse((root / 'hidden').exists())

    def test_near_equivalent_approval_rejects_path_drift_and_zero_identical_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = fixture(root)
            conf = config['suts']['alpha']
            original = json.loads(conf['emb_spec'].read_bytes())
            config['approved_source_specs'] = {
                'alpha': {'openapi.json': 'semantic_near_equivalent_same_path_set'}}
            candidate = copy.deepcopy(original)
            candidate['paths']['/unexpected'] = {}
            b.dump(conf['source'] / 'openapi.json', candidate)
            with self.assertRaisesRegex(ValueError, 'no longer matches its justification'):
                b.configure_source_omissions(config, ['alpha:openapi.json'])
            candidate = copy.deepcopy(original)
            for path in candidate['paths']:
                candidate['paths'][path]['get']['description'] = 'Entirely changed'
            b.dump(conf['source'] / 'openapi.json', candidate)
            self.assertTrue(b.audit_source_specs(config)['alpha']['spec_like'][0]['path_set_equal'])
            with self.assertRaisesRegex(ValueError, 'no longer matches its justification'):
                b.configure_source_omissions(config, ['alpha:openapi.json'])

    def test_manual_arbitrary_source_omission_cannot_bypass_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = fixture(root)
            config['suts']['alpha']['source_omit'] = ['App.java']
            with self.assertRaisesRegex(ValueError, 'Source omission was not audited'):
                b.build(config, root / 'out', root / 'hidden')
            self.assertFalse((root / 'out').exists())

    def test_unparseable_spec_like_file_stops_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = fixture(root)
            source = config['suts']['alpha']['source']
            (source / 'broken.yaml').write_text('openapi: 3.0.0\npaths: [\nsecret: synthetic-hidden-value\n')
            with self.assertRaises(ValueError) as caught:
                b.audit_source_specs(config)
            self.assertIn('Unparseable spec-like source file', str(caught.exception))
            self.assertNotIn('synthetic-hidden-value', str(caught.exception))

    def test_draft_tasks_have_distinct_access_and_answer_boundaries(self):
        tasks = b.task_texts(12)
        self.assertIn('These five values are the complete L1', tasks['TASK_M1.md'])
        self.assertNotIn('L2,proposed_L2', tasks['TASK_M1.md'])
        self.assertNotIn('intent_evidence.py', tasks['TASK_M1.md'])
        self.assertIn('../../tools/intent_evidence.py', tasks['TASK_M2.md'])
        self.assertIn('coordinator must authorize', tasks['TASK_M2.md'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
