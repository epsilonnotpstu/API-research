#!/usr/bin/python3
"""Offline regression tests. Synthetic Git stores are written with stdlib only."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_e6_blind as b

SCRATCH = b.ROOT / '09_collab/logs/T44_scratch'


class SyntheticGit:
    """Create actual loose Git objects without init/add/commit/checkout commands."""
    def __init__(self, path):
        self.path = path
        (path / 'objects').mkdir(parents=True)
        (path / 'refs/heads').mkdir(parents=True)
        (path / 'HEAD').write_text('ref: refs/heads/main\n')
        (path / 'config').write_text('[core]\n\tbare = true\n\trepositoryformatversion = 0\n')

    def object(self, kind, data):
        raw = f'{kind} {len(data)}\0'.encode() + data
        oid = hashlib.sha1(raw).hexdigest()
        path = self.path / 'objects' / oid[:2] / oid[2:]
        path.parent.mkdir(exist_ok=True)
        if not path.exists():
            path.write_bytes(zlib.compress(raw))
        return oid

    def tree(self, files):
        root = {}
        for path, value in files.items():
            node = root
            parts = path.split('/')
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value

        def write(node):
            records = []
            for name, value in node.items():
                if isinstance(value, dict):
                    mode, oid = '40000', write(value)
                else:
                    mode, data = value if isinstance(value, tuple) else ('100644', value)
                    oid = self.object('blob', data)
                records.append((name + ('/' if isinstance(value, dict) else ''),
                                mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(oid)))
            return self.object('tree', b''.join(r[1] for r in sorted(records)))
        return write(root)

    def revision(self, files, parent=None, message='synthetic revision'):
        data = 'tree ' + self.tree(files) + '\n'
        if parent:
            data += 'parent ' + parent + '\n'
        # Deliberately non-personal identities, never displayed by the builder.
        data += 'author [REDACTED] <redacted> 0 +0000\ncommitter [REDACTED] <redacted> 0 +0000\n\n' + message + '\n'
        oid = self.object('commit', data.encode())
        (self.path / 'refs/heads/main').write_text(oid + '\n')
        return oid


class BuilderTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-', dir=SCRATCH)
        self.root = Path(self.temp.name)
        self.store = SyntheticGit(self.root / 'fixture.git')
        self.git = b.Git(self.store.path)
        self.reference = self.root / 'reference'; self.reference.mkdir()
        for method in ['M1', 'M2']:
            (self.reference / f'TASK_{method}.md').write_text('# Task\n\n**Supervisor authorization:** supplied boundary.\n\nBody.\n')
        (self.reference / 'CODEBOOK_v0.6.md').write_text('Synthetic codebook, retained verbatim.\n')
        self.spec = 'api/contract.json'
        self.handler = 'src/main/java/p/Handler.java'
        self.other = 'src/main/java/p/Other.java'
        self.files = {self.spec: b'{"openapi":"3.0.0","paths":{}}\n',
                      self.handler: b'package p;\nclass Handler { int status = 200; }\n',
                      self.other: b'package p;\nclass Other { int value = 1; }\n',
                      'src/test/java/p/HandlerTest.java': b'package p;\nclass HandlerTest {}\n',
                      'README.md': b'API documentation\n', 'docs/guide.md': b'Review guidance\n'}

    def tearDown(self):
        self.temp.cleanup()

    def row(self, iid, parent, child, handler=None, **extra):
        paths = [('contract', self.spec), ('implementation', handler or self.handler)]
        return dict(item_id=iid, parent_commit=parent, fix_commit=child, repo='fixture',
                    operation='GET /resource', proposition='GET /resource: contract says a value; implementation does return another value.',
                    truth_direction='IMPL', stars='100', confidence='3', contract_kind='spec_file',
                    mismatch_type='status', fix_family=iid, source_task='synthetic',
                    message_excerpt='Unique subject ' + iid,
                    evidence=json.dumps({'snapshots': [{'side': 'parent', 'role': role, 'path': path} for role, path in paths]}), **extra)

    def manifest(self, rows):
        path = self.root / 'input.csv'
        path.write_bytes(b.csv_bytes(list(rows[0]), rows))
        return path

    def prepare(self, rows, salt='test'):
        return b.prepare(self.manifest(rows), {'fixture': self.store.path}, salt, self.reference, [])

    def pair(self, changed=None):
        parent = self.store.revision(self.files)
        child_files = dict(self.files)
        child_files[changed or self.handler] += b'// distinct child text\n'
        child = self.store.revision(child_files, parent)
        return parent, child, child_files

    def test_determinism_and_verbatim_proposition(self):
        parent, child, _ = self.pair()
        row = self.row('A', parent, child)
        first = self.prepare([row])
        second = self.prepare([row])
        self.assertEqual(first, second)
        records = list(csv.DictReader(io.StringIO(first[0]['items.csv'].decode())))
        self.assertEqual(records[0]['proposition'], row['proposition'])
        self.assertEqual(first[0]['CODEBOOK_v0.6.md'], (self.reference / 'CODEBOOK_v0.6.md').read_bytes())
        self.assertIn('K01/source/' + self.spec, first[0])
        self.assertNotIn('K01/contract.json', first[0])
        self.assertIn('K01/source/src/test/java/p/HandlerTest.java', first[0])
        self.assertEqual(list(csv.DictReader(io.StringIO(first[1].decode())))[0]['item_id'], 'K01')

    def test_salt_changes_mapping_and_row_order_does_not(self):
        parent, child, _ = self.pair()
        rows = [self.row(str(i), parent, child) for i in range(6)]
        first = self.prepare(rows, 'one')
        reverse = self.prepare(list(reversed(rows)), 'one')
        self.assertEqual(first[:2], reverse[:2])
        self.assertEqual(first[2]['items'], reverse[2]['items'])
        different = self.prepare(rows, 'two')
        self.assertNotEqual(first[2]['items'][0]['source_item'], different[2]['items'][0]['source_item'])

    def test_refuse_to_overwrite_each_output(self):
        files = {'items.csv': b.csv_bytes(b.ITEM_COLUMNS, [dict.fromkeys(b.ITEM_COLUMNS, 'K01')])}
        log = {'package_hashes': {'items.csv': b.sha(files['items.csv'])}}
        for target in range(3):
            paths = [self.root / f'out{target}', self.root / f'key{target}.csv', self.root / f'log{target}.json']
            paths[target].write_bytes(b'sentinel')
            with self.assertRaisesRegex(b.BuildError, 'overwrite'):
                b.publish(files, b'key', log, *paths)
            self.assertEqual(paths[target].read_bytes(), b'sentinel')
            self.assertFalse(any(p.exists() for i, p in enumerate(paths) if i != target))

    def test_publish_hashes_and_repeat_refused(self):
        parent, child, _ = self.pair()
        files, key, log = self.prepare([self.row('A', parent, child)])
        destinations = self.root / 'out', self.root / 'key.csv', self.root / 'log.json'
        result = b.publish(files, key, log, *destinations)
        self.assertTrue(result['disk_hashes_verified'])
        self.assertEqual(result['key_sha256'], b.sha(destinations[1].read_bytes()))
        self.assertEqual(json.loads(destinations[2].read_bytes()), result)
        with self.assertRaisesRegex(b.BuildError, 'overwrite'):
            b.publish(files, key, log, *destinations)

    def test_own_child_version_assertion(self):
        parent, child, child_files = self.pair()
        self.git.blobs(list(self.git.tree(parent).values()))
        row = self.row('A', parent, child)
        with self.assertRaisesRegex(b.BuildError, 'Child-version'):
            b.assert_own_leakage({self.handler: child_files[self.handler]}, {self.handler: child_files[self.handler]}, row, self.git)

    def test_child_copy_under_other_path_also_refused(self):
        parent, child, child_files = self.pair()
        self.git.blobs(list(self.git.tree(parent).values()))
        with self.assertRaisesRegex(b.BuildError, 'Child-version'):
            b.assert_own_leakage({self.other: child_files[self.handler]}, {self.other: child_files[self.handler]}, self.row('A', parent, child), self.git)

    def test_identical_parent_blob_allowed_when_only_mode_differs(self):
        parent = self.store.revision(self.files)
        child_files = dict(self.files); child_files[self.handler] = ('100755', self.files[self.handler])
        child = self.store.revision(child_files, parent)
        files, _, log = self.prepare([self.row('A', parent, child)])
        self.assertEqual(files['K01/source/' + self.handler], self.files[self.handler])
        self.assertEqual(log['items'][0]['own_child_assertion']['different_child_blobs'], 0)

    def cross_rows(self, protected):
        parent, child, later_files = self.pair(self.handler if protected else self.other)
        last_files = dict(later_files); last_files[self.handler] += b'// second child\n'
        last = self.store.revision(last_files, child)
        return [self.row('A', parent, child), self.row('B', child, last)]

    def test_cross_item_optional_path_excluded(self):
        files, _, log = self.prepare(self.cross_rows(False))
        pair = log['cross_item_pairs'][0]
        self.assertEqual(pair['decision'], 'exclude_paths_from_b')
        self.assertNotIn(pair['revealing_snapshot_item'] + '/source/' + self.other, files)
        self.assertEqual(log['excluded_items'], [])
        self.assertTrue(log['assertions']['cross_item'])

    def test_cross_item_protected_path_drops_larger_shuffled_id(self):
        rows = self.cross_rows(True)
        for salt in ['one', 'two', 'three', 'four']:
            _, key, log = self.prepare(rows, salt)
            self.assertEqual(log['excluded_items'], ['K02'])
            self.assertEqual(len(list(csv.DictReader(io.StringIO(key.decode())))), 1)
            self.assertEqual(log['cross_item_pairs'][0]['decision'], 'drop_later_sorted_item')

    def test_cross_item_same_parent_has_no_ancestry_leak(self):
        parent, child, _ = self.pair()
        _, _, log = self.prepare([self.row('A', parent, child), self.row('B', parent, child)])
        self.assertEqual(log['cross_item_pairs'], [])

    def test_future_reference_actual_prose_excluded(self):
        files = dict(self.files); files['docs/issue.md'] = b'Proposed solution for #781\n'
        parent = self.store.revision(files)
        files[self.handler] += b'// child\n'; child = self.store.revision(files, parent)
        row = self.row('A', parent, child); row['message_excerpt'] = 'Resolve condition (#781)'
        delivered, _, log = self.prepare([row])
        self.assertNotIn('K01/source/docs/issue.md', delivered)
        omission = next(o for o in log['items'][0]['omissions'] if o['path'] == 'docs/issue.md')
        self.assertEqual(omission['hits'][0]['kind'], 'issue_identifier')
        self.assertEqual(b.reference_hits(b'https://host/pull/781', [row])[0]['kind'], 'issue_identifier')

    def test_protected_future_reference_refused(self):
        self.files[self.handler] += b'// Unique subject A\n'
        parent, child, _ = self.pair()
        with self.assertRaisesRegex(b.BuildError, 'Protected evidence has a future reference'):
            self.prepare([self.row('A', parent, child)])

    def test_binaries_build_output_large_files_and_symlinks_omitted(self):
        self.files.update({'src/test/resources/data.bin': b'\0binary',
                           'src/target/generated.txt': b'build output',
                           'src/test/resources/large.bin': b'x' * (b.MAX_BYTES + 1),
                           'src/main/link': ('120000', b'../../outside'),
                           'src/main/archive.jar': b'archive', 'src/.git/config': b'vcs'})
        parent, child, _ = self.pair()
        files, _, log = self.prepare([self.row('A', parent, child)])
        excluded = {o['path'] for o in log['items'][0]['omissions']}
        self.assertEqual(len(excluded), 6)
        for path in excluded:
            self.assertNotIn('K01/source/' + path, files)

    def test_local_contract_reference_closure(self):
        self.files[self.spec] = b'{"$ref":"./schemas/model.json#/Model"}\n'
        self.files['api/schemas/model.json'] = b'{"Model":{"type":"string"}}\n'
        parent, child, _ = self.pair()
        files, _, log = self.prepare([self.row('A', parent, child)])
        self.assertIn('K01/source/api/schemas/model.json', files)
        self.assertIn('api/schemas/model.json', log['items'][0]['protected_paths'])

    def test_project_local_import_brings_dependency_module_and_tests(self):
        self.files[self.handler] = b'package p;\nimport q.Model;\nclass Handler {}\n'
        self.files['common/src/main/java/q/Model.java'] = b'package q;\nclass Model {}\n'
        self.files['common/src/test/java/q/ModelTest.java'] = b'package q;\nclass ModelTest {}\n'
        parent, child, _ = self.pair()
        files, _, log = self.prepare([self.row('A', parent, child)])
        self.assertIn('common', log['items'][0]['modules'])
        self.assertIn('K01/source/common/src/test/java/q/ModelTest.java', files)

    def test_generated_word_filter_is_word_based(self):
        files = {'items.csv': b.csv_bytes(b.ITEM_COLUMNS, [dict.fromkeys(b.ITEM_COLUMNS, 'K01')]), 'TASK_M1.md': b'prefix suffix\n'}
        b.assert_generated(files)
        for word in ['fix', 'commit', 'later', 'changed', 'E6', 'mined', 'T42', 'T43']:
            with self.subTest(word=word), self.assertRaises(b.BuildError):
                b.assert_generated(dict(files, **{'TASK_M1.md': ('Word: ' + word.upper()).encode()}))

    def test_fixture_values_literal_json_and_url_escaped(self):
        fixture = self.root / 'auth.yaml'
        fixture.write_text('auth:\n  - fixedHeaders:\n      - name: Authorization\n        value: "Basic dGVzdDpzeW50aGV0aWM="\n')
        needles = b.fixture_needles([fixture])
        self.assertGreaterEqual(len(needles), 3)
        for value in b.variants(needles):
            with self.subTest(length=len(value)):
                self.assertIn('auth_fixture_value', b.privacy_findings(value, needles))
                self.assertNotIn('auth_fixture_value', b.privacy_findings(b.redact(value, needles), needles))

    def test_credential_and_attribution_redaction_preserves_lines(self):
        text = ('// Signed-off-by: [synthetic identity]\n'
                'password: "synthetic-password"\n'
                'api_key=synthetic-value\n'
                'contact: "person@example.invalid"\n'
                '-----BEGIN PRIVATE KEY-----\nsynthetic-key-body\n-----END PRIVATE KEY-----\n'
                'keep this line\n').encode()
        safe = b.redact(text)
        self.assertEqual(len(safe.splitlines()), len(text.splitlines()))
        self.assertEqual(b.privacy_findings(safe), [])
        self.assertNotIn(b'synthetic-key-body', safe)
        self.assertNotIn(b'synthetic-password', safe)
        self.assertTrue(safe.endswith(b'keep this line\n'))

    def test_parent_required_and_no_mutating_git_command(self):
        parent, child, _ = self.pair()
        row = self.row('A', child, parent)
        with self.assertRaises(b.BuildError):
            self.prepare([row])
        for command in ['checkout', 'init', 'fetch', 'config', 'archive']:
            with self.assertRaisesRegex(b.BuildError, 'Non-read-only'):
                self.git.run(command)

    def test_multiline_auth_schema_is_not_an_auth_header(self):
        data = b'  type: Basic\n  authentication: optional\n'
        self.assertEqual(b.privacy_findings(data), [])
        self.assertEqual(b.redact(data), data)

    def test_yaml_password_schema_structure_is_preserved(self):
        data = b'properties:\n  password:\n    type: string\n    example: synthetic-password\n  other:\n    type: string\n'
        safe = b.redact(data)
        self.assertIn(b'password:\n    type: string\n', safe)
        self.assertNotIn(b'synthetic-password', safe)
        self.assertEqual(b.privacy_findings(safe), [])

    def test_json_contact_and_credential_examples_stay_valid(self):
        data = json.dumps({'info': {'contact': {'name': 'Synthetic Person', 'email': 'synthetic@example.invalid'}},
                           'properties': {'password': {'type': 'string', 'example': 'synthetic-password'}}}, indent=2).encode()
        safe = b.redact(data)
        obj = json.loads(safe)
        self.assertEqual(obj['properties']['password']['type'], 'string')
        self.assertEqual(obj['properties']['password']['example'], '<redacted>')
        self.assertEqual(obj['info']['contact']['name'], '<redacted>')
        self.assertEqual(b.privacy_findings(safe), [])
        self.assertEqual(len(safe.splitlines()), len(data.splitlines()))

    def test_literal_auth_method_arguments_redacted(self):
        data = b'header(HttpHeaders.AUTHORIZATION, "synthetic-auth-value");\nsetPassword("synthetic-password");\n'
        safe = b.redact(data)
        self.assertNotIn(b'synthetic-auth-value', safe)
        self.assertNotIn(b'synthetic-password', safe)
        self.assertEqual(b.privacy_findings(safe), [])

    def test_long_noncredential_fixture_has_bounded_scan(self):
        data = b'A' * 200000 + b'\n'
        self.assertEqual(b.redact(data), data)
        self.assertEqual(b.privacy_findings(data), [])

    def test_safe_path_and_broken_symlink_overwrite_refused(self):
        for value in ['../file', '/etc/passwd', 'a/../../b', 'a\\b', 'a\nfile']:
            with self.assertRaises(b.BuildError):
                b.safe_path(value)
        path = self.root / 'broken'; path.symlink_to(self.root / 'absent')
        with self.assertRaisesRegex(b.BuildError, 'overwrite'):
            b.assert_absent([path])


if __name__ == '__main__':
    unittest.main(verbosity=2)
