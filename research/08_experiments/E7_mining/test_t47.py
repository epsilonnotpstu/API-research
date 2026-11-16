#!/usr/bin/python3
"""New-package invariants, immutable history and synthetic leakage regressions."""
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy
import unittest

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
B=runpy.run_path(str(HERE/'build_t47.py'))
T=runpy.run_path(str(HERE/'test_build.py'))
F=runpy.run_path(str(HERE/'finalize_t47.py'))


class ContinuationTests(unittest.TestCase):
    def test_every_preexisting_private_file_and_frozen_file_is_preserved(self):
        baseline=json.loads((KEY/'preservation_t47_start.json').read_text())
        self.assertIn('key/e7_key.csv',baseline)
        self.assertIn('key/corpus_key.csv',baseline)
        self.assertIn('key/accepted_full.csv',baseline)
        self.assertGreater(len(baseline),4000)
        for path,digest in baseline.items():
            self.assertEqual(digest,hashlib.sha256((HERE/path).read_bytes()).hexdigest(),path)

    def test_rank_order_stopping_reasons_caps_and_dedup(self):
        decisions,yields,summary=F['audit']()
        self.assertEqual(summary,json.loads((HERE/'summary_t47.json').read_text()))
        self.assertGreaterEqual(summary['accepted_T47'],40)
        self.assertEqual(('hydra',103),(summary['final_repo'],summary['final_rank']))
        self.assertTrue(all(row['accepted_combined']<=10 for row in yields))
        self.assertTrue(all(0<len(row['reason'].split())<=25 for row in decisions))

    def test_real_package_contains_only_new_W_rows(self):
        output=B['OUT']
        with (output/'items.csv').open() as stream:items=list(csv.DictReader(stream))
        with (KEY/'e8b_key.csv').open() as stream:keys=list(csv.DictReader(stream))
        with (KEY/'accepted_full_t47.csv').open() as stream:full=list(csv.DictReader(stream))
        self.assertEqual(['item_id','repo','operation','proposition'],list(items[0]))
        self.assertEqual(B['B']['KEY_COLUMNS'],list(keys[0]))
        expected=[f'W{i:02}' for i in range(1,len(items)+1)]
        self.assertEqual(expected,[row['item_id'] for row in items])
        self.assertEqual(expected,[row['item_id'] for row in keys])
        self.assertEqual(expected,[row['item_id'] for row in full])
        self.assertEqual(set(expected),{p.name for p in output.iterdir() if p.is_dir()})
        self.assertTrue(all(row['source_task']=='T47' and row['set']=='new' for row in keys+full))
        self.assertNotEqual('e7_blind',output.name)
        self.assertTrue(all({p.name for p in (output/iid).iterdir()}=={'contract','impl'} for iid in expected))
        self.assertEqual([r['proposition'] for r in full],[r['proposition'] for r in items])

    def test_published_hashes_and_privacy_and_forbidden_words(self):
        output=B['OUT'];log=json.loads((KEY/'e8b_build_log.json').read_text())
        hashes={p.relative_to(output).as_posix():B['B']['sha'](p.read_bytes()) for p in output.rglob('*') if p.is_file()}
        self.assertEqual(log['package_hashes'],hashes)
        self.assertIsNone(B['FORBIDDEN'].search((output/'items.csv').read_text()))
        fixtures=sorted(B['B']['O']['AUTH'].glob('*.yaml'))
        needles=B['B']['O']['fixture_needles'](fixtures)
        for relative in hashes:
            self.assertFalse(B['B']['O']['privacy_findings']((output/relative).read_bytes(),needles),relative)
        self.assertTrue(all(log['assertions'].values()))

    def test_private_salt_and_mapping_have_correct_deterministic_order(self):
        rows=B['R']['accepted']();salt=(KEY/'e8b_shuffle_salt.txt').read_text().strip()
        self.assertNotEqual((KEY/'shuffle_salt.txt').read_text().strip(),salt)
        with (KEY/'e8b_shuffle_mapping.csv').open() as stream:mapping=list(csv.DictReader(stream))
        expected=[dict(item_id=f'W{i:02}',source_item=row['item_id']) for i,row in enumerate(B['w_order'](rows,salt),1)]
        self.assertEqual(expected,mapping)
        for p in B['OUT'].rglob('*'):
            if p.is_file():self.assertNotIn(salt.encode(),p.read_bytes())


class SyntheticSeparationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=T['BuildTests']();self.fixture.setUp()
        self.old=dict(self.fixture.a,source_task='T46')
        self.new=dict(self.fixture.b,source_task='T47')
        self.repos={'synthetic':self.fixture.repo.path}

    def tearDown(self):self.fixture.tearDown()

    def prepare(self,new=None,old=None):
        return B['prepare'](new or [self.new],old or [self.old],self.repos,'synthetic independent salt')

    def test_W_shuffle_is_deterministic_and_independent_of_old_rows(self):
        other=dict(self.new,item_id='c',fix_family='c')
        first=self.prepare([self.new,other])
        second=self.prepare([other,self.new])
        self.assertEqual(first,second)
        self.assertEqual(['W01','W02'],[r['item_id'] for r in first[3]])
        self.assertEqual({self.new['item_id'],other['item_id']},{r['source_item'] for r in first[4]})

    def test_only_new_files_and_old_to_new_overlap_exclusion(self):
        files,key,log,full,mapping=self.prepare()
        self.assertEqual({'W01'},set(p.split('/')[0] for p in files if '/' in p))
        self.assertNotIn('W01/impl/Helper.java',files)
        self.assertEqual('true',full[0]['cross_item_flag'])
        self.assertEqual('a',log['cross_item_pairs'][0]['earlier'])
        self.assertEqual('W01',log['cross_item_pairs'][0]['later'])
        self.assertEqual(['Helper.java'],log['cross_item_pairs'][0]['excluded'])
        self.assertEqual(b'class B {}\n',files['W01/impl/B.java'])
        self.assertNotIn(b'int number = 1',files['W01/impl/B.java'])
        self.assertTrue(all(self.old['message_excerpt'].encode() not in data for data in files.values()))
        self.assertTrue(all(self.new['fix_commit'].encode() not in data for data in files.values()))

    def test_cross_item_own_locator_is_retained(self):
        self.new['proposition_check']=json.dumps({'contract':[self.fixture.child+':api.yaml:1'],
            'implementation':[self.fixture.child+':B.java:1'],'route':[self.fixture.child+':Helper.java:1']})
        files,key,log,full,mapping=self.prepare()
        self.assertIn('W01/impl/Helper.java',files)
        self.assertEqual(['Helper.java'],log['cross_item_pairs'][0]['retained_own_locators'])

    def test_new_publisher_refuses_overwrite_and_preserves_old_key_sentinels(self):
        result=self.prepare();root=self.fixture.folder;out=root/'separate';key=root/'new-key';key.mkdir()
        old_names=['e7_key.csv','corpus_key.csv','accepted_full.csv']
        before={name:('preserved '+name).encode() for name in old_names}
        for name,data in before.items():(key/name).write_bytes(data)
        B['publish'](result,out,key)
        delivered=(out/'items.csv').read_bytes()
        with self.assertRaises(B['B']['O']['BuildError']):B['publish'](result,out,key)
        self.assertEqual(delivered,(out/'items.csv').read_bytes())
        self.assertEqual(before,{name:(key/name).read_bytes() for name in old_names})

    def test_new_forbidden_words_are_rejected(self):
        for word in ['T47','E8']:
            row=dict(self.new,proposition='GET /a: contract says '+word+'; implementation does blue')
            with self.assertRaises(AssertionError):self.prepare([row])


if __name__=='__main__':unittest.main()
