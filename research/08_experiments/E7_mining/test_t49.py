#!/usr/bin/python3
"""Preservation, direction-neutral caps, separated publication and previews."""
from collections import Counter
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent
KEY = HERE / 'key'
B = runpy.run_path(str(HERE / 'build_t49.py'))
R = B['R']
F = runpy.run_path(str(HERE / 'finalize_t49.py'))
T = runpy.run_path(str(HERE / 'test_build.py'))


def rows(path):
    csv.field_size_limit(16 * 1024 * 1024)
    return list(csv.DictReader(io.StringIO(path.read_text())))


class ContinuationTests(unittest.TestCase):
    def test_existing_private_files_and_freeze_preserved(self):
        baseline = json.loads((KEY / 'preservation_t49_start.json').read_text())
        self.assertEqual(8853, sum(p.startswith('key/') for p in baseline))
        for name in ['e7_key.csv', 'e8b_key.csv', 'e10_key.csv', 'accepted_full_t48.csv', 'corpus_key.csv']:
            self.assertIn('key/' + name, baseline)
        R['guard']()
        freeze = json.loads((HERE / 'freeze2.json').read_text())
        for name, field in [('pool2.json', 'pool_sha256'), ('key/pool2_sources.json', 'source_sha256'), ('mine2.py', 'code_sha256')]:
            self.assertEqual(freeze[field], hashlib.sha256((HERE / name).read_bytes()).hexdigest())

    def test_rank_prefix_caps_dedup_and_stopping(self):
        decisions, yields, summary, exported = F['audit']()
        self.assertEqual(summary, json.loads((HERE / 'summary_t49.json').read_text()))
        self.assertEqual((949, 36, 24, 81, 45, 0), tuple(summary[k] for k in
                         ['reviewed', 'accepted_T49', 'accepted_candidates', 'valid_operations', 'FIX_CAP_exclusions', 'REPO_CAP_exclusions']))
        self.assertEqual({'1': 12, '2': 12}, summary['items_per_accepted_candidate'])
        self.assertEqual(('service-api', 435), (summary['final_repo'], summary['final_rank']))
        self.assertTrue(all(r['accepted_combined'] <= 10 for r in yields))
        self.assertTrue(all(r['stopped'] in {'combined repo cap', 'available pool exhausted'} for r in yields))
        self.assertEqual(994, len(exported))
        published = rows(KEY / 'review_decisions_t49.csv')
        self.assertEqual(Counter(r['reason_code'] for r in exported), Counter(r['reason_code'] for r in published))
        self.assertEqual(949, len(decisions))

    def test_only_U_rows_exact_columns_and_verbatim_propositions(self):
        output = B['OUT']
        items, keys, full = rows(output / 'items.csv'), rows(KEY / 'e12_key.csv'), rows(KEY / 'accepted_full_t49.csv')
        expected = [f'U{i:02}' for i in range(1, 37)]
        self.assertEqual(['item_id', 'repo', 'operation', 'proposition'], list(items[0]))
        self.assertEqual(list(rows(KEY / 'e10_key.csv')[0]), list(keys[0]))
        self.assertEqual(list(rows(KEY / 'accepted_full_t48.csv')[0]), list(full[0]))
        self.assertIn('candidate_id', full[0])
        for table in [items, keys, full]:
            self.assertEqual(expected, [r['item_id'] for r in table])
        self.assertTrue(all(r['set'] == 'new' and r['source_task'] == 'T49' for r in keys + full))
        self.assertEqual(set(expected), {p.name for p in output.iterdir() if p.is_dir()})
        for iid in expected:
            self.assertEqual({'contract', 'impl'}, {p.name for p in (output / iid).iterdir()})
        self.assertEqual([r['proposition'] for r in full], [r['proposition'] for r in items])
        self.assertEqual('e12_blind', output.name)
        expected_readme = (b'# Source reading excerpts\n\nEach table row identifies a proposition. The contract and implementation directories preserve repository paths. Source files are complete except for privacy redactions; large specification documents contain the selected operation and its local reference closure. Line positions in complete files are retained. Excerpts have no VCS history. Read each row independently.\n')
        self.assertEqual(expected_readme, (output / 'README.md').read_bytes())

    def test_package_hashes_privacy_leakage_and_eight_file_cap(self):
        output = B['OUT']
        log = json.loads((KEY / 'e12_build_log.json').read_text())
        hashes = {p.relative_to(output).as_posix(): B['B']['sha'](p.read_bytes()) for p in output.rglob('*') if p.is_file()}
        self.assertEqual(log['package_hashes'], hashes)
        self.assertEqual(len(hashes), log['summary']['files'])
        self.assertEqual(sum(p.stat().st_size for p in output.rglob('*') if p.is_file()), log['summary']['bytes'])
        self.assertEqual(187, log['summary']['all_items_cross_checked'])
        self.assertIsNone(B['FORBIDDEN'].search((output / 'items.csv').read_text()))
        fixtures = sorted(B['B']['O']['AUTH'].glob('*.yaml'))
        needles = B['B']['O']['fixture_needles'](fixtures)
        self.assertEqual((15, 54), (len(fixtures), len(B['B']['O']['variants'](needles))))
        for relative in hashes:
            self.assertFalse(B['B']['O']['privacy_findings']((output / relative).read_bytes(), needles), relative)
        self.assertFalse(B['B']['O']['privacy_findings']('\n'.join(r['reason'] for r in rows(KEY / 'review_decisions_t49.csv')).encode(), needles))
        self.assertTrue(all(log['assertions'].values()))
        for detail in log['items']:
            self.assertLessEqual(sum(p.startswith('impl/') for p in detail['files']), 8)
            self.assertTrue(set(detail['protected']) <= {p.split('/', 1)[1] for p in detail['files']})

    def test_U_shuffle_private_deterministic_and_independent(self):
        salt = (KEY / 'e12_shuffle_salt.txt').read_text().strip()
        for name in ['shuffle_salt.txt', 'e8b_shuffle_salt.txt', 'e10_shuffle_salt.txt']:
            self.assertNotEqual((KEY / name).read_text().strip(), salt)
        accepted = R['accepted']()
        expected = [dict(item_id=f'U{i:02}', source_item=r['item_id']) for i, r in enumerate(B['u_order'](accepted, salt), 1)]
        self.assertEqual(expected, rows(KEY / 'e12_shuffle_mapping.csv'))
        self.assertEqual(B['u_order'](accepted, salt), B['u_order'](list(reversed(accepted)), salt))
        for p in B['OUT'].rglob('*'):
            if p.is_file():
                self.assertNotIn(salt.encode(), p.read_bytes())

    def test_real_preview_ledger_and_stopped_guard(self):
        decisions, _, summary, _ = F['audit']()
        events = [json.loads(p.read_text()) for p in sorted((KEY / 't49_previews').glob('*.json'))]
        evidence = {p.stem for p in (KEY / 't49_evidence').glob('*.diff')}
        self.assertEqual(949, len(F['validate_previews'](decisions, events, evidence)))
        self.assertEqual(2473, len(events))
        self.assertEqual(0, summary['preview_record']['outside_final_prefix'])
        before = len(events), len(evidence)
        row = next(r for r in R['sources']() if r['repo'] == 'service-api' and r['rank'] == 436)
        self.assertIsNone(R['next_row']())
        with self.assertRaisesRegex(AssertionError, 'outside current'):
            R['evidence'](row)
        with self.assertRaisesRegex(AssertionError, 'Only the candidate'):
            R['screen']('service-api', 436, 437)
        self.assertEqual(before, (len(list((KEY / 't49_previews').glob('*.json'))), len(list((KEY / 't49_evidence').glob('*.diff')))))

    def test_all_generation_cross_flags_and_reference_exclusions(self):
        audit = json.loads((KEY / 'e12_cross_item_all.json').read_text())
        self.assertEqual(187, audit['all_items'])
        self.assertTrue(audit['U_flags_match'])
        self.assertTrue(audit['existing_keys_not_modified'])
        log = json.loads((KEY / 'e12_build_log.json').read_text())
        refs = json.loads((KEY / 'e12_reference_audit.json').read_text())
        excluded = {p['later'] + '/contract/' + path for p in log['cross_item_pairs']
                    for path in p['excluded'] if path.endswith(('.yaml', '.yml', '.json'))}
        self.assertTrue({r['target'] for r in refs['missing_references']} <= excluded)
        self.assertEqual(0, refs['remote_reference_incidents'])


class CapRegressionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(operation=o, truth_direction=d) for o, d in
                     [('PUT /z', 'SPEC'), ('GET /a', 'IMPL'), ('DELETE /z', 'BOTH'), ('POST /a', 'SPEC')]]

    def test_plain_byte_order_keeps_first_two(self):
        kept, excluded, repo = R['select_operations'](self.rows, 10)
        self.assertEqual(['DELETE /z', 'GET /a'], [r['operation'] for r in kept])
        self.assertEqual(['POST /a', 'PUT /z'], [r['operation'] for r in excluded])
        self.assertEqual([], repo)

    def test_direction_and_other_properties_cannot_change_selection(self):
        expected = [[r['operation'] for r in group] for group in R['select_operations'](self.rows, 10)]
        altered = [dict(r, truth_direction='arbitrary', confidence=-1, item_id=str(i)) for i, r in enumerate(reversed(self.rows))]
        self.assertEqual(expected, [[r['operation'] for r in group] for group in R['select_operations'](altered, 10)])

    def test_selection_needs_only_operation(self):
        self.assertEqual(['DELETE /z', 'GET /a'], [r['operation'] for r in R['select_operations'](
            [dict(operation=r['operation']) for r in self.rows], 2)[0]])

    def test_repo_cap_applies_after_fix_byte_order(self):
        kept, fix, repo = R['select_operations'](self.rows, 1)
        self.assertEqual(['DELETE /z'], [r['operation'] for r in kept])
        self.assertEqual(['GET /a'], [r['operation'] for r in repo])
        self.assertEqual(['POST /a', 'PUT /z'], [r['operation'] for r in fix])

    def test_duplicate_operation_rejected(self):
        with self.assertRaises(AssertionError):
            R['select_operations'](self.rows + [self.rows[0]], 2)

    def test_identity_does_not_reuse_count_after_capping(self):
        items = R['accepted']()
        self.assertEqual(len(items), len({r['item_id'] for r in items}))
        # Every retained record must still equal its original staged evidence,
        # even when earlier candidates staged more operations than were kept.
        for item in items:
            staged = next(r for r in R['valid_items'](item['candidate_id']) if r['operation'] == item['operation'])
            self.assertEqual({k: v for k, v in item.items() if k != 'item_id'},
                             {k: v for k, v in staged.items() if k != 'item_id'})
        for p in (KEY / 't49_valid').iterdir():
            valid = [json.loads(f.read_text()) for f in p.glob('*.json')]
            self.assertEqual(len(valid), len({r['operation'] for r in valid}))

    def test_preview_display_suppresses_encoded_and_credential_literals(self):
        literal = 'c3ludGhldGljLXNlY3JldC1mb3ItcmVncmVzc2lvbi1vbmx5'
        rendered = R['display']('String encoding = "' + literal + '"; String clientSecret = "artificial-value";')
        self.assertNotIn(literal, rendered)
        self.assertNotIn('artificial-value', rendered)


class SyntheticSeparationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = T['BuildTests']()
        self.fixture.setUp()
        self.old = dict(self.fixture.a, source_task='T48')
        self.new = dict(self.fixture.b, source_task='T49')
        self.repos = {'synthetic': self.fixture.repo.path}

    def tearDown(self):
        self.fixture.tearDown()

    def prepare(self, new=None, old=None):
        return B['prepare'](new or [self.new], old or [self.old], self.repos, 'synthetic new salt')

    def test_U_shuffle_deterministic_independent_of_old_order(self):
        other = dict(self.new, item_id='c', fix_family='c')
        first, second = self.prepare([self.new, other]), self.prepare([other, self.new])
        self.assertEqual(first, second)
        self.assertEqual(['U01', 'U02'], [r['item_id'] for r in first[3]])
        extra = dict(self.old, item_id='d', fix_family='d')
        self.assertEqual(first[4], self.prepare([other, self.new], [extra, self.old])[4])

    def test_parent_files_optional_cross_overlap_excluded(self):
        files, _, log, full, _ = self.prepare()
        self.assertEqual({'U01'}, {p.split('/')[0] for p in files if '/' in p})
        self.assertNotIn('U01/impl/Helper.java', files)
        self.assertEqual('true', full[0]['cross_item_flag'])
        self.assertEqual(['Helper.java'], log['cross_item_pairs'][0]['excluded'])
        self.assertEqual(b'class B {}\n', files['U01/impl/B.java'])
        for data in files.values():
            self.assertNotIn(self.new['fix_commit'].encode(), data)
            self.assertNotIn(self.old['message_excerpt'].encode(), data)
            self.assertNotIn(b'int number = 1', data)

    def test_own_locator_overlap_kept_and_flagged(self):
        self.new['proposition_check'] = json.dumps({'contract': [self.fixture.child + ':api.yaml:1'],
            'implementation': [self.fixture.child + ':B.java:1'], 'route': [self.fixture.child + ':Helper.java:1']})
        files, _, log, _, _ = self.prepare()
        self.assertIn('U01/impl/Helper.java', files)
        self.assertEqual(['Helper.java'], log['cross_item_pairs'][0]['retained_own_locators'])

    def test_overwrite_refused_prior_sentinels_unchanged(self):
        result = self.prepare()
        root = self.fixture.folder
        out, key = root / 'separate', root / 'new-key'
        key.mkdir()
        names = ['e7_key.csv', 'e8b_key.csv', 'e10_key.csv', 'accepted_full_t48.csv']
        before = {name: ('preserved ' + name).encode() for name in names}
        for name, data in before.items():
            (key / name).write_bytes(data)
        B['publish'](result, out, key)
        delivered = (out / 'items.csv').read_bytes()
        with self.assertRaises(B['B']['O']['BuildError']):
            B['publish'](result, out, key)
        self.assertEqual(delivered, (out / 'items.csv').read_bytes())
        self.assertEqual(before, {name: (key / name).read_bytes() for name in names})

    def test_forbidden_words_nonparent_locators_rejected(self):
        for word in ['T47', 'T48', 'T49', 'E8', 'E9', 'E10', 'E11', 'E12']:
            row = dict(self.new, proposition='GET /a: contract says ' + word + '; implementation does blue')
            with self.assertRaises((AssertionError, B['B']['O']['BuildError'])):
                self.prepare([row])
        row = dict(self.new, proposition_check=json.dumps({'contract': [self.fixture.last + ':api.yaml:1'],
                       'implementation': [self.fixture.child + ':B.java:1']}))
        with self.assertRaises(B['B']['O']['BuildError']):
            self.prepare([row])

    def test_generated_mount_projection_is_unique_and_preserves_closure(self):
        spec = T['SPEC'].replace('/a:', '/api/2/a:')
        projected = B['project_yaml'](spec.encode(), 'api.yaml', 'GET /a')
        self.assertIn(b'/api/2/a', projected)
        ambiguous = spec + '  /api/3/a:\n    get:\n      responses: {}\n'
        with self.assertRaises(B['B']['O']['BuildError']):
            B['project_yaml'](ambiguous.encode(), 'api.yaml', 'GET /a')

    def test_parent_phrase_reused_as_subject_is_redacted(self):
        self.new['message_excerpt'] = 'class B'
        files, _, log, _, _ = self.prepare()
        data = files['U01/impl/B.java']
        self.assertNotIn(b'class B', data)
        self.assertEqual(1, len(data.splitlines()))
        self.assertTrue(log['assertions']['message_scan'])


if __name__ == '__main__':
    unittest.main()
