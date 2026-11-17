#!/usr/bin/python3
"""Continuation regressions: immutability, same-salt rebuild and stopping prefix."""
import csv
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
R=runpy.run_path(str(HERE/'review_t50b.py'))
F=runpy.run_path(str(HERE/'finalize_t50b.py'))
B=runpy.run_path(str(HERE/'build_t50b.py'))

class ContinuationTests(unittest.TestCase):
    def test_original_pool_freeze_keys_and_round2_records_unchanged(self):
        R['continuation_guard']();F['archived_hashes']()
        freeze=json.loads((HERE/'freeze3.json').read_text())
        self.assertEqual(freeze['pool_sha256'],hashlib.sha256((HERE/'pool3.json').read_bytes()).hexdigest())

    def test_continuation_starts_rank3_and_stops_only_after_final_candidate(self):
        ordered,_,summary,_=F['audit']()
        self.assertEqual(3,ordered[40]['rank'])
        cid=ordered[-1]['candidate_id']
        final_count=sum(r['candidate_id']==cid for r in R['accepted']())
        self.assertLess(len(R['accepted']())-final_count,60)
        self.assertGreaterEqual(len(R['accepted']()),60)
        self.assertIsNone(R['next_row']())
        self.assertEqual((51,52,False),(summary['completed_round'],summary['current_round'],summary['current_round_complete']))

    def test_decision_csv_is_append_only_and_matches_final_json_records(self):
        original=(R['ARCHIVE']/'review_decisions_t50.csv').read_bytes()
        path=KEY/'review_decisions_t50.csv';before=path.read_bytes()
        self.assertTrue(before.startswith(original))
        R['append_csv_records']()
        self.assertEqual(before,path.read_bytes())
        with path.open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(R['decisions']()),sum(r['review_status']!='accepted_capped' for r in rows))
        with tempfile.TemporaryDirectory(dir=HERE) as temporary:
            p=Path(temporary)/'record.json';R['private_json'](p,dict(value=1))
            with self.assertRaises(FileExistsError):R['private_json'](p,dict(value=2))
            self.assertEqual(dict(value=1),json.loads(p.read_text()))

    def test_superseded_package_has_original_eight_items_and_unchanged_readme(self):
        manifest=F['archived_hashes']()
        with (R['ARCHIVE']/'e13_blind/items.csv').open() as f:old=list(csv.DictReader(f))
        self.assertEqual(8,len(old));self.assertEqual(52,len(manifest['hashes']['e13_blind']))
        self.assertEqual((R['ARCHIVE']/'e13_blind/README.md').read_bytes(),(B['OUT']/'README.md').read_bytes())
        self.assertEqual([f'Q{i:02}' for i in range(1,9)],[r['item_id'] for r in old])

    def test_same_salt_full_set_shuffle_has_exactly_current_Q_items(self):
        salt=(KEY/'e13_shuffle_salt.txt').read_text().strip()
        expected=[r['item_id'] for r in B['q_order'](R['accepted'](),salt)]
        with (KEY/'e13_shuffle_mapping_t50b.csv').open() as f:mapping=list(csv.DictReader(f))
        self.assertEqual(expected,[r['source_item'] for r in mapping])
        self.assertEqual([f'Q{i:02}' for i in range(1,62)],[r['item_id'] for r in mapping])
        with (B['OUT']/'items.csv').open() as f:items=list(csv.DictReader(f))
        self.assertEqual(61,len(items));self.assertEqual({r['item_id'] for r in mapping},{r['item_id'] for r in items})

    def test_complete_round_yield_checkpoints_exist(self):
        records=[json.loads(p.read_text()) for p in (KEY/'t50b_round_checkpoints').glob('*.json')]
        completed={r['round'] for r in records if r['complete_round'] and r['round']<52}
        self.assertTrue(set(range(3,52))<=completed)
        with (HERE/'yield_t50.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual([r['clone_name'] for r in R['P3']['selected']()],[r['repo'] for r in rows])
        self.assertEqual(947,sum(int(r['reviewed']) for r in rows))
        self.assertEqual(61,sum(int(r['items']) for r in rows))
        self.assertFalse(any(r['stop_reason']=='continuing' for r in rows))

    def test_actual_licence_rejections_are_unknown_and_never_accepted(self):
        rejected=[d for d in R['decisions']() if d['reason'].startswith('LICENCE:')]
        self.assertEqual(2,len(rejected))
        accepted={r['candidate_id'] for r in R['accepted']()}
        for row in rejected:
            self.assertEqual('OTHER',row['reason_code']);self.assertNotIn(row['candidate_id'],accepted)
            record=json.loads((KEY/'t50_licences'/(row['candidate_id']+'.json')).read_text())
            self.assertEqual('UNKNOWN',record['licence_at_parent'])

    def test_preview_filter_suppresses_hosted_attribution_hex_and_checksums(self):
        # Artificial values only; no observed private literal is repeated here.
        for source in ['// see https://gitee.example.invalid/example/source',
                       '0x'+', 0x'.join(['ab']*12),
                       'h1:ArtificialChecksumForRegressionOnly1234567890=']:
            rendered=R['display'](source)
            self.assertNotEqual(source,rendered)
            self.assertIn('redacted',rendered)

    def test_reason_prose_exception_does_not_mask_auth_literals(self):
        scan=runpy.run_path(str(HERE/'audit_t50b.py'))['reason_privacy_scan']
        base=dict(candidate_id='synthetic')
        findings,allowed=scan([dict(base,reason='Checks basic authentication and basic credentials.')])
        self.assertEqual([],findings);self.assertEqual(2,len(allowed))
        # Synthetic credential-shaped data stays detectable; never print its value.
        findings,allowed=scan([dict(base,reason='Basic '+''.join(chr(c) for c in [81,87,70,51,98,71,86,90,89,109,86,121]))])
        self.assertIn('auth_literal',findings);self.assertEqual([],allowed)

if __name__=='__main__':unittest.main()
