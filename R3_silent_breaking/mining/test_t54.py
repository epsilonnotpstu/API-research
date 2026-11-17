#!/usr/bin/python3
"""Offline, synthetic review of F1--F3; never loads frozen or package artifacts.

Risk tests characterize current gaps, so a passing suite is not a privacy verdict.
All test diagnostics suppress assertion values and exception text.
"""
from copy import deepcopy
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SCRATCH = HERE.parent / 'collab/logs/T54_scratch'
T = runpy.run_path(str(HERE / 'test_t53.py'))
P, S, B = T['P'], T['S'], T['B']
C, V = B['C'], B['V']
SOURCE = T['SOURCE']


class Fixture(T['Fixture']):
    """The T53 synthetic bare fixture, extended only to construct gitlinks."""
    def tree(self, files):
        nested = {}
        for path, raw in files.items():
            cursor = nested
            parts = path.split('/')
            for part in parts[:-1]:
                cursor = cursor.setdefault(part, {})
            cursor[parts[-1]] = raw

        def emit(node):
            entries = []
            for name, value in sorted(node.items()):
                if isinstance(value, dict):
                    mode, kind, oid = '040000', 'tree', emit(value)
                elif isinstance(value, tuple):
                    mode, kind, oid = '160000', 'commit', value[1]
                else:
                    mode, kind, oid = '100644', 'blob', self.object('blob', value)
                entries.append(f'{mode} {kind} {oid}\t{name}\n'.encode())
            return self.run('mktree', '--missing', data=b''.join(entries)).decode().strip()
        return emit(nested)


class RepoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='t54_', dir='/tmp')
        self.f = Fixture(self.temp.name)
        self.base = self.f.commit({SOURCE: 'class Controller { int x=1; }\n'},
                                  date='2022-12-30T00:00:00Z')
        self.addCleanup(self.temp.cleanup)

    def selected(self, roots, extra=None):
        self.parent = self.f.commit(dict(roots, **(extra or {})), date='2022-12-31T00:00:00Z')
        self.child = self.f.commit({SOURCE: 'class Controller { int x=2; }\n'})
        rows, _, self.history = self.f.discover()
        self.row = next(r for r in rows if r['sha'] == self.child)
        self.git = P['Git'](self.f.path)
        self.addCleanup(self.git.close)
        self.context = B['context_for_repo'](self.git, [self.row])
        return self.row

    def build(self):
        return B['build_item'](self.row, 'B001', self.git, self.history, self.context)

    def assert_clean(self, files):
        self.assertTrue(all(not V['findings'](data, **self.context) for data in files.values()))
        self.assertEqual(B['scan_package'](files, {'all': self.context}), {})


class F1Tests(RepoTests):
    def test_protocol_missing_and_submodule_keep_both_streams_aligned(self):
        for content in (False, True):
            with self.subTest(content=content):
                # Inject the documented protocol answer independently of Git version.
                tail = b'123 blob 3\n' + (b'abc\n' if content else b'')
                process = type('Process', (), {})()
                process.stdin = io.BytesIO()
                process.stdout = io.BytesIO(b'missing-name missing\nlink-name submodule\n' + tail)
                git = P['Git']('/tmp/unused-t54.git')
                setattr(git, 'reader' if content else 'checker', process)
                got = git.batch(['missing-name', 'link-name', 'blob-name'], content=content)
                self.assertIsNone(got['missing-name'])
                self.assertIsNone(got['link-name'])
                self.assertEqual(got['blob-name'], ('123', 'blob', b'abc' if content else None))
                self.assertEqual(process.stdout.read(), b'')

    def test_actual_gitlink_and_blob_are_distinguished(self):
        child = self.f.commit({'module': ('gitlink', '1' * 40)})
        git = P['Git'](self.f.path)
        self.addCleanup(git.close)
        for content in (False, True):
            names = [child + ':module', child + ':absent', child + ':' + SOURCE]
            got = git.batch(names, content=content)
            self.assertIsNone(got[names[0]])
            self.assertIsNone(got[names[1]])
            self.assertEqual(got[names[2]][1], 'blob')
        self.assertIsNone(git.blob(child, 'module'))

    def test_blob_to_gitlink_removes_root_and_discovery_is_repeatable(self):
        self.f.commit({'spec.yaml': 'openapi: 3.0.0\npaths: {}\n'}, date='2022-12-31T00:00:00Z')
        replaced = self.f.commit({'spec.yaml': ('gitlink', '1' * 40),
                                 SOURCE: 'class Controller { int x=2; }\n'})
        kept = self.f.commit({SOURCE: 'class Controller { int x=3; }\n'})
        first = self.f.discover()
        self.assertEqual(first, self.f.discover())
        rows, counts, history = first
        self.assertNotIn(replaced, [r['sha'] for r in rows])
        self.assertEqual([r['sha'] for r in rows], [kept])
        self.assertEqual(counts['contract_exclusions'], 1)
        self.assertEqual(history['roots'][replaced], [])
        self.assertEqual(S['select'](rows, ['fixture']), S['select'](list(reversed(rows)), ['fixture']))

    def test_gitlink_at_behaviour_path_does_not_become_delivered_blob(self):
        self.selected({}, {'api/handler.go': ('gitlink', '1' * 40)})
        files, _, _ = self.build()
        self.assertFalse(any('handler.go' in p for p in files))
        self.assert_clean(files)

    def test_risk_new_source_named_gitlink_alone_is_admitted_to_pool(self):
        # Characterize the downstream eligibility gap: a gitlink has numstat
        # and a source-like name, but supplies no repository behaviour blob.
        child = self.f.commit({'api/handler.go': ('gitlink', '1' * 40)})
        rows, _, history = self.f.discover()
        self.assertEqual([r['sha'] for r in rows], [child])
        self.assertEqual(rows[0]['files'], ['api/handler.go'])
        files, keys, _, failures = B['prepare'](
            rows, 'synthetic-salt', {'fixture': self.f.path}, {'fixture': history}, b'Read source.\n')
        self.assertEqual(len(keys), 1)
        self.assertEqual(failures, [])
        self.assertFalse(any('/before/' in p or '/after/' in p for p in files))


class F2Tests(unittest.TestCase):
    def test_threshold_is_inclusive_and_counts_whitespace_words(self):
        lines = ['aaaaaa bbbbbb cccccc', 'aaaaaa bbbbbb ccccccc',
                 'aaaaaaa bbbbbbb cccccc', 'abcdefghijklmnop qrstuvwxyz',
                 'one two three', 'abcdefghijklmnopqrstuvw']
        needles, _ = V['message_needles']('\n'.join(reversed(lines)))
        expected = [s for s in lines if len(s) >= 20 and len(s.split()) >= 3]
        self.assertEqual(needles, sorted(expected, key=lambda s: (-len(s), s)))
        self.assertEqual(needles, V['message_needles']('\n'.join(lines + lines))[0])

    def test_long_message_redacts_and_independent_ids_survive_filter(self):
        message = 'Synthetic orchard route correction\n#9123\nTASK-8123\nPR 7123'
        needles, ids = V['message_needles'](message)
        self.assertEqual(ids, ['#7123', '#9123', 'TASK-8123'])
        raw = (message + '\nhttps://fixture.invalid/pull/7123\n').encode()
        context = dict(messages=needles, identifiers=ids, shas=[])
        redacted = V['redact'](raw, **context)
        self.assertNotIn(needles[0].encode(), redacted)
        self.assertFalse(V['findings'](redacted, **context))

    def test_risk_short_or_two_word_distinctive_text_passes_both_scans(self):
        # Entirely invented markers: no real commit-message text is used.
        for marker in ['Cobalt otter yawns', 'CobaltOtterRouteRegression corrected',
                       'CobaltOtterRouteRegression']:
            with self.subTest(length=len(marker), words=len(marker.split())):
                needles, ids = V['message_needles'](marker)
                self.assertEqual(needles, [])
                context = dict(messages=needles, identifiers=ids, shas=[])
                raw = ('// ' + marker + '\n').encode()
                self.assertEqual(V['redact'](raw, **context), raw)
                self.assertEqual(V['findings'](raw, **context), [])
                self.assertEqual(B['scan_package']({'after/api/handler.go': raw}, {'all': context}), {})


class F2PackageRiskTests(RepoTests):
    def test_risk_invented_short_subject_reaches_prepared_package(self):
        marker = 'Cobalt otter yawns'
        self.f.commit({SOURCE: 'class Controller { int x=2; } // ' + marker + '\n'}, message=marker)
        rows, _, history = self.f.discover()
        files, keys, _, failures = B['prepare'](
            rows, 'synthetic-salt', {'fixture': self.f.path}, {'fixture': history}, b'Read source.\n')
        self.assertEqual(len(keys), 1)
        self.assertEqual(failures, [])
        self.assertTrue(any(marker.encode() in raw for raw in files.values()))


class F3Tests(RepoTests):
    def test_contract_error_fallback_redacts_and_passes_both_scans(self):
        root = ('openapi: 3.0.0\ninfo:\n  title: fixture\n'
                '  contact:\n    name: synthetic contact\n'
                'password: "synthetic-value"\n'
                'paths:\n  $ref: missing.yaml\n')
        self.selected({'spec.yaml': root})
        files, key, audit = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertEqual(audit['contract_mapping'][0]['reason'], 'ContractError')
        self.assertEqual(files['contract/spec.yaml'], V['redact'](root.encode(), **self.context))
        self.assertNotIn(b'synthetic-value', files['contract/spec.yaml'])
        self.assertNotIn(b'synthetic contact', files['contract/spec.yaml'])
        self.assert_clean(files)

    def test_json_decode_error_after_redaction_also_falls_back(self):
        root = {'openapi': '3.0.0', 'info': {'title': 'fixture'}, 'paths': {}}
        self.selected({'spec.json': json.dumps(root)})
        real_redact = V['redact']
        projected = C['encoded'](root)

        def redact(raw, **context):
            # Isolate JSONDecodeError after projection; original root stays valid.
            return b'{' if raw == projected else real_redact(raw, **context)

        with patch.dict(V, redact=redact):
            files, key, audit = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertEqual(audit['contract_mapping'][0]['reason'], 'JSONDecodeError')
        self.assertEqual(json.loads(files['contract/spec.json']), root)
        self.assert_clean(files)

    def test_redacted_missing_local_target_is_contract_error_fallback(self):
        # Redacting a ticket-shaped filename changes its $ref, not its delivered path.
        root = 'openapi: 3.0.0\npaths:\n  $ref: TASK-8123.yaml#/entry\n'
        self.selected({'spec.yaml': root}, {'TASK-8123.yaml': 'entry: {}\n'})
        self.context['identifiers'] = ['TASK-8123']
        files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertEqual({p for p in files if p.startswith('contract/')}, {'contract/spec.yaml'})
        self.assert_clean(files)

    def test_missing_fragment_after_redaction_also_falls_back(self):
        root = ('openapi: 3.0.0\npaths:\n  $ref: "#/components/schemas/TASK-8123"\n'
                'components:\n  schemas:\n    TASK-8123: {type: string}\n')
        self.selected({'spec.yaml': root})
        # This causes a different surviving reference without touching its key.
        self.context['messages'] = ['#/components/schemas/TASK-8123']
        files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assert_clean(files)

    def test_byte_order_and_global_2000_line_budget_are_deterministic(self):
        roots = {
            'z.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n',
            'a.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n' + '# filler\n' * 1995,
            'm.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n' + '# middle\n' * 10,
        }
        self.selected(roots)
        first = self.build()
        self.history['roots'][self.parent].reverse()
        self.assertEqual(first, self.build())
        files = first[0]
        contracts = {p: v for p, v in files.items() if p.startswith('contract/')}
        self.assertEqual(list(contracts), ['contract/a.yaml', 'contract/m.yaml'])
        self.assertEqual(sum(len(v.splitlines()) for v in contracts.values()), 2000)
        self.assertEqual(contracts['contract/m.yaml'], ''.join(roots['m.yaml'].splitlines(keepends=True)[:3]).encode())
        self.assert_clean(files)

    def test_projection_partial_files_are_removed_on_fallback(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {}\n'})
        def partial(*args):
            return {'old.json': b'{}\n', 'bad.json': b'{'}, [], 0
        with patch.dict(C, build=partial):
            files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertEqual({p for p in files if p.startswith('contract/')}, {'contract/spec.yaml'})

    def test_fallback_only_delivers_parent_detected_roots_not_refs_or_configs(self):
        roots = {'api/spec.yaml': 'openapi: 3.0.0\npaths: {$ref: ../config.yaml#/absent}\n'}
        extra = {'config.yaml': 'ordinary: parent configuration\n',
                 'not-contract.yaml': 'service:\n  openapi: false\n'}
        self.selected(roots, extra)
        files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertEqual(self.history['roots'][self.parent], ['api/spec.yaml'])
        self.assertEqual({p for p in files if p.startswith('contract/')}, {'contract/api/spec.yaml'})
        self.assert_clean(files)

    def test_fallback_reads_contracts_only_at_parent_even_when_child_differs(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n# parent marker\n'})
        # Deliberately outside candidate rules: directly probe build_item revision pinning.
        different_child = self.f.commit({'spec.yaml': 'openapi: 3.0.0\n# child marker\npaths: {}\n',
                                         'child.yaml': 'openapi: 3.0.0\n# child only\npaths: {}\n'})
        self.row = dict(self.row, sha=different_child)
        self.history['positions'][different_child] = 99
        calls = []
        original = self.git.blob
        def blob(revision, path):
            calls.append((revision, path))
            return original(revision, path)
        with patch.object(self.git, 'blob', side_effect=blob):
            files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertIn(b'parent marker', files['contract/spec.yaml'])
        self.assertFalse(any(b'child marker' in v or b'child only' in v for v in files.values()))
        self.assertTrue(all(rev == self.parent for rev, path in calls if path != SOURCE))
        self.assertNotIn('contract/child.yaml', files)

    def test_unsafe_root_output_path_fails_instead_of_falling_through(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n'})
        self.history['roots'][self.parent] = ['../outside.yaml']
        def projection_failure(*args):
            raise C['ContractError']('Synthetic projection failure')
        with patch.dict(C, build=projection_failure):
            with self.assertRaises(ValueError):
                self.build()

    def test_escaping_reference_cannot_read_or_deliver_outside_root(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {$ref: ../outside.yaml}\n'})
        calls = []
        original = self.git.blob
        def blob(revision, path):
            calls.append((revision, path))
            return original(revision, path)
        with patch.object(self.git, 'blob', side_effect=blob):
            files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertFalse(any(path == '../outside.yaml' for _, path in calls))
        self.assertEqual({p for p in files if p.startswith('contract/')}, {'contract/spec.yaml'})

    def test_risk_metadata_in_fallback_filename_is_not_scanned(self):
        # Shared pre-existing scan gap: package paths are never passed to findings.
        root_path = 'TASK-8123.yaml'
        self.selected({root_path: 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n'})
        self.context['identifiers'] = ['TASK-8123']
        files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertIn('contract/' + root_path, files)
        self.assert_clean(files)
        self.assertNotEqual(V['redact'](root_path.encode(), **self.context), root_path.encode())

    def test_unsafe_projected_output_path_is_not_swallowed(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {}\n'})
        with patch.dict(C, build=lambda *a: ({'../outside.yaml': b'{}'}, [], 0)):
            with self.assertRaises(ValueError):
                self.build()

    def test_privacy_findings_still_fail_after_fallback(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n'})
        with patch.dict(V, findings=lambda *a, **kw: ['synthetic_finding']):
            with self.assertRaises(ValueError):
                self.build()

    def test_package_scan_still_rejects_fallback_vcs_header(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\nDate: synthetic\n'})
        files, key, _ = self.build()
        self.assertEqual(key['contract_mapping_mode'], 'raw_fallback')
        self.assertTrue(all(not V['findings'](v, **self.context) for v in files.values()))
        self.assertEqual(B['scan_package'](files, {'all': self.context}), {'vcs_header': 1})
        result = B['prepare']
        with self.assertRaises(ValueError):
            result([self.row], 'synthetic-salt', {'fixture': self.f.path},
                   {'fixture': self.history}, b'Read source.\n')

    def test_fallback_prepare_retains_item_sample_and_salt_determinism(self):
        self.selected({'spec.yaml': 'openapi: 3.0.0\npaths: {$ref: missing.yaml}\n'})
        rows = [self.row]
        original = deepcopy(rows)
        args = ('synthetic-salt', {'fixture': self.f.path}, {'fixture': self.history}, b'Read source.\n')
        first = B['prepare'](rows, *args)
        self.assertEqual(first, B['prepare'](rows, *args))
        self.assertEqual(rows, original)
        self.assertEqual(len(first[1]), 1)
        self.assertEqual(first[3], [])
        self.assertEqual(first[1][0]['contract_mapping_mode'], 'raw_fallback')


def main():
    start = time.monotonic()
    suite = unittest.TestSuite()
    for case in (F1Tests, F2Tests, F2PackageRiskTests, F3Tests):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    summary = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                   failed_tests=[t.id().split('.')[-1] for t, _ in result.failures + result.errors],
                   elapsed_seconds=round(time.monotonic() - start, 2), synthetic_only=True,
                   diagnostics='source and exception values suppressed')
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / 't54_test_summary.json').write_bytes(P['jb'](summary))
    print(json.dumps(summary), flush=True)
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    sys.exit(main())
