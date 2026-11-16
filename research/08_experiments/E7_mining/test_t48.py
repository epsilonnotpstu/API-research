#!/usr/bin/python3
"""Preservation, isolated publication and sequential preview regressions."""
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
B = runpy.run_path(str(HERE / 'build_t48.py'))
T = runpy.run_path(str(HERE / 'test_build.py'))
F = runpy.run_path(str(HERE / 'finalize_t48.py'))


def rows(path):
    return list(csv.DictReader(io.StringIO(path.read_text())))


class ContinuationTests(unittest.TestCase):
    def test_all_existing_key_and_freeze_bytes_preserved(self):
        baseline = json.loads((KEY / 'preservation_t48_start.json').read_text())
        required = ['e7_key.csv', 'e8b_key.csv', 'corpus_key.csv', 'accepted_full.csv', 'accepted_full_t47.csv']
        for name in required:
            self.assertIn('key/' + name, baseline)
        self.assertEqual(6169, sum(p.startswith('key/') for p in baseline))
        for path, digest in baseline.items():
            self.assertEqual(digest, hashlib.sha256((HERE / path).read_bytes()).hexdigest(), path)
        freeze = json.loads((HERE / 'freeze2.json').read_text())
        for name, field in [('pool2.json', 'pool_sha256'), ('key/pool2_sources.json', 'source_sha256'), ('mine2.py', 'code_sha256')]:
            self.assertEqual(freeze[field], hashlib.sha256((HERE / name).read_bytes()).hexdigest())

    def test_two_phase_prefix_caps_dedup_and_stopping(self):
        decisions, yields, summary = F['audit']()
        self.assertEqual(summary, json.loads((HERE / 'summary_t48.json').read_text()))
        self.assertEqual((490, 40, 21), (summary['reviewed'], summary['accepted_T48'], summary['accepted_candidates']))
        self.assertEqual(('apicurio-registry', 155), (summary['final_repo'], summary['final_rank']))
        self.assertEqual((441, 49, 36, 4), tuple(summary[k] for k in ['phase1_reviewed', 'phase2_reviewed', 'phase1_accepted', 'phase2_accepted']))
        self.assertTrue(all(r['accepted_combined'] <= 10 for r in yields))
        self.assertTrue(all(0 < len(d['reason'].split()) <= 25 for d in decisions))
        published = rows(KEY / 'review_decisions_t48.csv')
        self.assertEqual([(d['repo'], d['rank']) for d in decisions], [(d['repo'], int(d['rank'])) for d in published])

    def test_real_package_contains_only_V_rows_and_separate_roles(self):
        output = B['OUT']
        items, keys, full = rows(output / 'items.csv'), rows(KEY / 'e10_key.csv'), rows(KEY / 'accepted_full_t48.csv')
        expected = [f'V{i:02}' for i in range(1, 41)]
        self.assertEqual(['item_id', 'repo', 'operation', 'proposition'], list(items[0]))
        self.assertEqual(B['B']['KEY_COLUMNS'], list(keys[0]))
        self.assertEqual(list(rows(KEY / 'e8b_key.csv')[0]), list(keys[0]))
        for table in [items, keys, full]:
            self.assertEqual(expected, [r['item_id'] for r in table])
        self.assertTrue(all(r['set'] == 'new' and r['source_task'] == 'T48' for r in keys + full))
        self.assertEqual(set(expected), {p.name for p in output.iterdir() if p.is_dir()})
        for iid in expected:
            self.assertEqual({'contract', 'impl'}, {p.name for p in (output / iid).iterdir()})
        self.assertEqual([r['proposition'] for r in full], [r['proposition'] for r in items])
        self.assertEqual('e10_blind', output.name)

    def test_package_hashes_role_counts_privacy_and_leakage_assertions(self):
        output = B['OUT']
        log = json.loads((KEY / 'e10_build_log.json').read_text())
        hashes = {p.relative_to(output).as_posix(): B['B']['sha'](p.read_bytes()) for p in output.rglob('*') if p.is_file()}
        self.assertEqual(log['package_hashes'], hashes)
        self.assertEqual(1606, len(hashes))
        for role, field, count in [('contract', 'contract_files', 1420), ('impl', 'implementation_files', 184)]:
            self.assertEqual(count, sum('/' in p and p.split('/', 2)[1] == role for p in hashes))
            self.assertEqual(count, log['summary'][field])
        self.assertIsNone(B['FORBIDDEN'].search((output / 'items.csv').read_text()))
        fixtures = sorted(B['B']['O']['AUTH'].glob('*.yaml'))
        needles = B['B']['O']['fixture_needles'](fixtures)
        self.assertEqual((15, 54), (len(fixtures), len(B['B']['O']['variants'](needles))))
        for relative in hashes:
            self.assertFalse(B['B']['O']['privacy_findings']((output / relative).read_bytes(), needles), relative)
        reasons = '\n'.join(r['reason'] for r in rows(KEY / 'review_decisions_t48.csv')).encode()
        self.assertFalse(B['B']['O']['privacy_findings'](reasons, needles))
        self.assertTrue(all(log['assertions'].values()))
        for d in log['items']:
            self.assertLessEqual(sum(p.startswith('impl/') for p in d['files']), 8)
            self.assertTrue(set(d['protected']) <= {p.split('/', 1)[1] for p in d['files']})

    def test_private_salt_and_mapping_deterministic_and_not_delivered(self):
        salt = (KEY / 'e10_shuffle_salt.txt').read_text().strip()
        for name in ['shuffle_salt.txt', 'e8b_shuffle_salt.txt']:
            self.assertNotEqual((KEY / name).read_text().strip(), salt)
        accepted = B['R']['accepted']()
        expected = [dict(item_id=f'V{i:02}', source_item=r['item_id']) for i, r in enumerate(B['v_order'](accepted, salt), 1)]
        self.assertEqual(expected, rows(KEY / 'e10_shuffle_mapping.csv'))
        self.assertEqual(B['v_order'](accepted, salt), B['v_order'](list(reversed(accepted)), salt))
        for p in B['OUT'].rglob('*'):
            if p.is_file():
                self.assertNotIn(salt.encode(), p.read_bytes())

    def test_real_preview_ledger_has_no_lookahead_or_undecided_evidence(self):
        decisions, _, summary = F['audit']()
        events = [json.loads(p.read_text()) for p in sorted((KEY / 't48_previews').glob('*.json'))]
        evidence = {p.stem for p in (KEY / 't48_evidence').glob('*.diff')}
        self.assertEqual(490, len(F['validate_previews'](decisions, events, evidence)))
        self.assertEqual(1364, len(events))
        self.assertEqual(0, summary['preview_record']['outside_final_prefix'])
        before = (len(events), len(evidence))
        # A future candidate must fail before Git access or evidence/preview writes.
        row = next(r for r in B['R']['sources']() if r['repo'] == 'apicurio-registry' and r['rank'] == 156)
        self.assertIsNone(B['R']['next_row']())
        with self.assertRaisesRegex(AssertionError, 'outside current'):
            B['R']['evidence'](row)
        with self.assertRaisesRegex(AssertionError, 'Only the candidate'):
            B['R']['screen']('apicurio-registry', 156, 157)
        self.assertEqual(before, (len(list((KEY / 't48_previews').glob('*.json'))), len(list((KEY / 't48_evidence').glob('*.diff')))))

    def test_reference_exclusions_are_recorded_and_limited_to_cross_item_paths(self):
        audit = json.loads((KEY / 'e10_reference_audit.json').read_text())
        log = json.loads((KEY / 'e10_build_log.json').read_text())
        excluded = {p['later'] + '/contract/' + path for p in log['cross_item_pairs'] for path in p['excluded']}
        self.assertEqual(3, len(excluded))
        self.assertEqual((16479, 143, 3), (audit['local_file_reference_incidents'], audit['missing_reference_incidents'], audit['affected_items']))
        self.assertEqual(excluded, {r['target'] for r in audit['missing_references']})
        self.assertEqual(0, audit['remote_reference_incidents'])


class PreviewRegressionTests(unittest.TestCase):
    def setUp(self):
        self.ordered = [dict(candidate_id='one', repo='synthetic', rank=1), dict(candidate_id='two', repo='synthetic', rank=2)]
        self.events = [dict(sequence=1, candidate_id='one', repo='synthetic', rank=1, final_decisions_before=0),
                       dict(sequence=2, candidate_id='two', repo='synthetic', rank=2, final_decisions_before=1)]

    def test_valid_sequential_previews(self):
        self.assertEqual({'one', 'two'}, F['validate_previews'](self.ordered, self.events, {'one', 'two'}))

    def test_lookahead_is_rejected(self):
        events = copy.deepcopy(self.events)
        events[1]['final_decisions_before'] = 0
        with self.assertRaisesRegex(AssertionError, 'Lookahead'):
            F['validate_previews'](self.ordered, events, {'one', 'two'})

    def test_preview_without_final_decision_is_rejected(self):
        events = copy.deepcopy(self.events)
        events[1]['candidate_id'] = 'unknown'
        with self.assertRaisesRegex(AssertionError, 'without final decision'):
            F['validate_previews'](self.ordered, events, {'one', 'two'})

    def test_reopened_candidate_and_unlogged_patch_are_rejected(self):
        events = copy.deepcopy(self.events)
        events.append(dict(events[0], sequence=3))
        with self.assertRaisesRegex(AssertionError, 'reopened'):
            F['validate_previews'](self.ordered, events, {'one', 'two'})
        with self.assertRaisesRegex(AssertionError, 'Unrecorded'):
            F['validate_previews'](self.ordered, self.events, {'one', 'two', 'extra'})


class SyntheticSeparationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = T['BuildTests']()
        self.fixture.setUp()
        self.old = dict(self.fixture.a, source_task='T47')
        self.new = dict(self.fixture.b, source_task='T48')
        self.repos = {'synthetic': self.fixture.repo.path}

    def tearDown(self):
        self.fixture.tearDown()

    def prepare(self, new=None, old=None):
        return B['prepare'](new or [self.new], old or [self.old], self.repos, 'synthetic new salt')

    def test_V_shuffle_deterministic_independent_of_old_order(self):
        other = dict(self.new, item_id='c', fix_family='c')
        first, second = self.prepare([self.new, other]), self.prepare([other, self.new])
        self.assertEqual(first, second)
        self.assertEqual(['V01', 'V02'], [r['item_id'] for r in first[3]])
        extra = dict(self.old, item_id='d', fix_family='d')
        self.assertEqual(first[4], self.prepare([other, self.new], [extra, self.old])[4])

    def test_only_new_parent_files_with_optional_cross_overlap_excluded(self):
        files, key, log, full, mapping = self.prepare()
        self.assertEqual({'V01'}, {p.split('/')[0] for p in files if '/' in p})
        self.assertNotIn('V01/impl/Helper.java', files)
        self.assertEqual('true', full[0]['cross_item_flag'])
        self.assertEqual(['Helper.java'], log['cross_item_pairs'][0]['excluded'])
        self.assertEqual(b'class B {}\n', files['V01/impl/B.java'])
        for data in files.values():
            self.assertNotIn(self.new['fix_commit'].encode(), data)
            self.assertNotIn(self.old['message_excerpt'].encode(), data)
            self.assertNotIn(b'int number = 1', data)

    def test_own_locator_overlap_is_kept_and_flagged(self):
        self.new['proposition_check'] = json.dumps({'contract': [self.fixture.child + ':api.yaml:1'],
            'implementation': [self.fixture.child + ':B.java:1'], 'route': [self.fixture.child + ':Helper.java:1']})
        files, _, log, _, _ = self.prepare()
        self.assertIn('V01/impl/Helper.java', files)
        self.assertEqual(['Helper.java'], log['cross_item_pairs'][0]['retained_own_locators'])

    def test_refuses_overwrite_preserving_all_prior_key_sentinels(self):
        result = self.prepare()
        root = self.fixture.folder
        out, key = root / 'separate', root / 'new-key'
        key.mkdir()
        names = ['e7_key.csv', 'e8b_key.csv', 'corpus_key.csv', 'accepted_full.csv', 'accepted_full_t47.csv']
        before = {name: ('preserved ' + name).encode() for name in names}
        for name, data in before.items():
            (key / name).write_bytes(data)
        B['publish'](result, out, key)
        delivered = (out / 'items.csv').read_bytes()
        with self.assertRaises(B['B']['O']['BuildError']):
            B['publish'](result, out, key)
        self.assertEqual(delivered, (out / 'items.csv').read_bytes())
        self.assertEqual(before, {name: (key / name).read_bytes() for name in names})

    def test_new_forbidden_words_and_nonparent_locators_rejected(self):
        for word in ['T47', 'T48', 'E8', 'E9', 'E10']:
            row = dict(self.new, proposition='GET /a: contract says ' + word + '; implementation does blue')
            with self.assertRaises((AssertionError, B['B']['O']['BuildError'])):
                self.prepare([row])
        row = dict(self.new, proposition_check=json.dumps({'contract': [self.fixture.last + ':api.yaml:1'],
                       'implementation': [self.fixture.child + ':B.java:1']}))
        with self.assertRaises(B['B']['O']['BuildError']):
            self.prepare([row])


if __name__ == '__main__':
    unittest.main()
