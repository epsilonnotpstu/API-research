#!/usr/bin/python3
"""Frozen-pool, ranked individual audit and source-preservation assertions."""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy
import unittest
import warnings

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
M=runpy.run_path(str(HERE/'mine2.py'))

def read_csv(path):return list(csv.DictReader(io.StringIO(path.read_text())))

def prior_reviewed():
    # The frozen discovery module predates this test and opens short-lived CSVs.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',ResourceWarning)
        return M['reviewed']()


class ReviewAuditTests(unittest.TestCase):
    def test_frozen_bytes_unchanged_on_continuation(self):
        guard=json.loads((KEY/'freeze2_continuation_guard.json').read_text())
        for relative,digest in guard.items():self.assertEqual(digest,hashlib.sha256((HERE/relative).read_bytes()).hexdigest())
        freeze=json.loads((HERE/'freeze2.json').read_text())
        self.assertEqual(freeze['pool_sha256'],hashlib.sha256((HERE/'pool2.json').read_bytes()).hexdigest())
        self.assertEqual(freeze['source_sha256'],hashlib.sha256((KEY/'pool2_sources.json').read_bytes()).hexdigest())
        self.assertEqual(freeze['code_sha256'],hashlib.sha256((HERE/'mine2.py').read_bytes()).hexdigest())

    def test_ranking_and_prior_exclusions(self):
        pool=json.loads((KEY/'pool2_sources.json').read_text());prior=prior_reviewed()
        self.assertFalse(any((r['repo'],r['fix_commit']) in prior for r in pool))
        self.assertEqual(pool,sorted(pool,key=lambda r:(r['repo'],-r['score'],r['fix_commit'])))
        ranks=Counter()
        for r in pool:
            ranks[r['repo']]+=1;self.assertEqual(ranks[r['repo']],r['rank'])
            strength=r['score']//10
            self.assertIn(strength,[1,2,3])
            self.assertEqual(10*strength+int(any(M['M']['OP'].search(p) for p in r['surface_paths'])),r['score'])

    def test_one_specific_reason_per_candidate(self):
        rows=read_csv(KEY/'review_decisions2.csv')
        self.assertEqual(len(rows),len({r['candidate_id'] for r in rows}))
        codes=set('ACCEPT NOT_CONTRACT_RELATED NEW_FEATURE_OR_ENDPOINT REFACTOR_OR_RENAME GENERATED_OR_DOCS_ONLY_CHURN BOTH_CHANGED_TO_NEW_BEHAVIOUR NO_PARENT_MISMATCH TEST_OR_CLIENT_ONLY TOO_LARGE_TO_ESTABLISH OTHER'.split())
        seen=Counter()
        for r in rows:
            self.assertIn(r['reason_code'],codes)
            self.assertLessEqual(len(r['reason'].split()),25)
            self.assertTrue(r['reason'].strip())
            seen[r['repo']]+=1;self.assertEqual(seen[r['repo']],int(r['rank']))
            self.assertEqual(r['patch_sha256'],hashlib.sha256((HERE/r['review_evidence']).read_bytes()).hexdigest())
        self.assertEqual(1259,len(rows))

    def test_stopping_caps_and_dedup(self):
        prior=json.loads((KEY/'new_accepted.json').read_text());new=json.loads((KEY/'new_accepted2.json').read_text())
        exploratory=read_csv(HERE.parent/'E6_realfix/combined_accepted.csv')
        self.assertEqual(45,len(prior)+len(new))
        self.assertTrue(all(n<=6 for n in Counter(r['repo'] for r in prior+new).values()))
        dedup=[(r['repo'],r['operation'],r['fix_family']) for r in exploratory+prior+new]
        self.assertEqual(len(dedup),len(set(dedup)))
        decisions=read_csv(KEY/'review_decisions2.csv')
        self.assertEqual('strimzi-kafka-bridge',decisions[-1]['repo'])
        self.assertEqual(32,int(decisions[-1]['rank']))
        admitted={item for r in decisions for item in r['accepted_items'].split('|') if item}
        self.assertEqual({r['item_id'] for r in new},admitted)

    def test_T45_source_bytes_preserved(self):
        self.assertEqual((KEY/'t45_snapshot/new_accepted.json').read_bytes(),(KEY/'new_accepted.json').read_bytes())
        original=read_csv(KEY/'t45_snapshot/e7_key.csv')
        stable={r['item_id']:r for r in read_csv(KEY/'corpus_key.csv')}
        for row in original:
            for column,value in row.items():self.assertEqual(value,stable[row['item_id']][column])


if __name__=='__main__':unittest.main()
