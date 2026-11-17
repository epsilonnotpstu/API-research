#!/usr/bin/python3
"""T50 frozen discovery, review ordering, licensing and separated package tests."""
from collections import Counter
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
KEY=HERE/'key'
B=runpy.run_path(str(HERE/'build_t50b.py'));R=B['R'];P=R['P3']
F=runpy.run_path(str(HERE/'finalize_t50b.py'))
T=runpy.run_path(str(HERE/'test_build.py'))

def rows(path):
    csv.field_size_limit(16*1024*1024)
    with path.open() as f:return list(csv.DictReader(f))

class Pool3Tests(unittest.TestCase):
    def test_existing_keys_pools_and_freezes_preserved(self):
        baseline=json.loads((KEY/'preservation_t50_start.json').read_text())
        self.assertGreater(len(baseline),14000)
        for name in ['key/e12_key.csv','key/accepted_full_t49.csv','pool2.json','freeze2.json','candidate_pool.json','freeze.json']:self.assertIn(name,baseline)
        R['guard']()

    def test_pool3_order_scores_and_frozen_mapping_determinism(self):
        source=R['sources']();pool=json.loads((HERE/'pool3.json').read_text())
        order=[r['clone_name'] for r in P['selected']()]
        self.assertEqual(20,len(order));self.assertEqual(12832,len(source))
        expected=[];i=0
        for repo in order:
            candidates=sorted([r for r in source if r['repo']==repo],key=lambda r:(-r['score'],r['fix_commit']))
            for rank,r in enumerate(candidates,1):
                i+=1;self.assertEqual((rank,f'P3C{i:06}'),(r['rank'],r['candidate_id']))
                self.assertIn(r['score']//10,[1,2,3])
                self.assertEqual(r['score'],10*(r['score']//10)+int(any(P['M']['OP'].search(p) for p in r['surface_paths'])))
                expected.append({k:r[k] for k in pool[0]})
        self.assertEqual(pool,expected)
        old={r['repo'] for r in json.loads((KEY/'pool2_sources.json').read_text())}
        self.assertFalse(set(order)&old)

    def test_go_annotation_extension_keeps_old_filters(self):
        for annotation in [b'// @Router /a [get]\n',b'// swagger:route GET /a synthetic readA\n']:
            self.assertIn('go_swagger_annotations',P['classify']('internal/api/a.go',[annotation]))
            self.assertNotIn('go_swagger_annotations',P['classify']('internal/api/a.go',[annotation],False))
            for path in ['vendor/a.go','internal/api/a_test.go','examples/a.go']:
                self.assertEqual([],P['classify'](path,[annotation]))
        self.assertEqual([],P['classify']('.github/workflows/a.yaml',[b'openapi: 3.0.3\n']))
        self.assertIn('openapi_root',P['classify']('docs/a.yaml',[b'openapi: 3.0.3\n']))
        self.assertEqual([],P['classify']('server/src/main/resources/application.yaml',[b'name: config\n']))

    def test_full_discovery_replays_deterministically_on_a_selected_repo(self):
        metadata=next(r for r in P['selected']() if r['clone_name']=='spring-petclinic-rest')
        first,info=P['discover'](metadata);second,other=P['discover'](metadata)
        self.assertEqual((first,info),(second,other))
        actual=[{k:v for k,v in r.items() if k not in {'rank','candidate_id'}} for r in R['sources']() if r['repo']==metadata['clone_name']]
        self.assertEqual(actual,first)


class ReviewTests(unittest.TestCase):
    def test_scheduler_skips_capped_and_exhausted_repositories(self):
        fn=R['next_row'];g=fn.__globals__;names=['KEY','sources','decisions','accepted','plan'];saved={k:g[k] for k in names}
        with tempfile.TemporaryDirectory(prefix='.t50-schedule-',dir=HERE) as temporary:
            g['KEY']=Path(temporary)
            candidates=[dict(repo='a',rank=1,candidate_id='a1'),dict(repo='a',rank=2,candidate_id='a2'),dict(repo='b',rank=1,candidate_id='b1')]
            completed=[dict(repo='a',rank=1,candidate_id='a1')]
            g['sources']=lambda:candidates
            g['decisions']=lambda:completed
            g['accepted']=lambda:[dict(repo='a',candidate_id='a1') for _ in range(10)]
            g['plan']=lambda:iter([(1,'a',1),(1,'b',1),(1,'a',2)])
            try:
                self.assertEqual('b1',fn()['candidate_id'])
                completed.append(dict(repo='b',rank=1,candidate_id='b1'))
                self.assertIsNone(fn())
            finally:g.update(saved)

    def test_round_robin_plan_includes_each_rank_in_selection_order(self):
        fn=R['plan'];g=fn.__globals__;saved={k:g[k] for k in ['sources','P3']}
        g['sources']=lambda:[dict(repo='a',rank=1),dict(repo='a',rank=2),dict(repo='b',rank=1)]
        g['P3']=dict(selected=lambda:[dict(clone_name='b'),dict(clone_name='a')])
        try:self.assertEqual([(1,'b',1),(1,'a',1),(1,'a',2)],list(fn()))
        finally:g.update(saved)

    def test_real_round_robin_audit_and_target_stop(self):
        ordered,yields,summary,exported=F['audit']()
        self.assertEqual(summary,json.loads((HERE/'summary_t50b.json').read_text()))
        self.assertEqual(947,len(ordered));self.assertEqual(51,summary['completed_round'])
        order=[r['clone_name'] for r in P['selected']()]
        self.assertEqual([(repo,rank) for rank in (1,2) for repo in order],[(d['repo'],d['rank']) for d in ordered[:40]])
        self.assertEqual(947,sum(r['reviewed'] for r in yields));self.assertEqual(61,summary['accepted_items'])
        self.assertEqual(60,summary['FIX_CAP_exclusions']);self.assertEqual(1007,len(exported))
        self.assertTrue(all(len(r['reason'].split())<=25 for r in exported))

    def test_caps_only_read_operation_and_use_plain_bytes(self):
        values=[dict(operation=x) for x in ['PUT /z','GET /a','DELETE /z','POST /a']]
        expected=R['select_operations'](values,10)
        self.assertEqual(['DELETE /z','GET /a'],[r['operation'] for r in expected[0]])
        altered=[dict(r,truth_direction='arbitrary',confidence=-4) for r in reversed(values)]
        self.assertEqual([[r['operation'] for r in group] for group in expected],[[r['operation'] for r in group] for group in R['select_operations'](altered,10)])
        self.assertEqual([1,2,1],[len(g) for g in R['select_operations'](values,1)])
        with self.assertRaises(AssertionError):R['select_operations'](values+[values[0]],10)

    def test_preview_ledger_and_guard_deny_an_unreviewed_candidate(self):
        ordered,_,summary,_=F['audit']()
        events=[json.loads(p.read_text()) for p in sorted((KEY/'t50_previews').glob('*.json'))]
        evidence={p.stem for p in (KEY/'t50_evidence').glob('*.diff')}
        self.assertEqual(len(ordered),len(F['validate_previews'](ordered,events,evidence)))
        before=len(events)
        unreviewed=next(r for r in R['sources']() if r['rank']==3)
        with self.assertRaisesRegex(AssertionError,'outside current'):R['evidence'](unreviewed)
        self.assertEqual(before,len(list((KEY/'t50_previews').glob('*.json'))))
        with self.assertRaises(AssertionError):R['screen']('traccar',3,4)

    def test_display_suppresses_encoded_literals_and_credential_assignments(self):
        import base64
        value=base64.b64encode(b'artificial test data '*4).decode()
        for source in ['String encoding = "'+value+'";', 'String password = "artificial-value";', 'assert.Equal("artificial-value", object.LinkToken)', 'token: artificial-value']:
            rendered=R['display'](source)
            self.assertNotIn(value,rendered);self.assertNotIn('artificial-value',rendered)
        self.assertIn('swagger.json',R['display']('internal/api/swagger.json'))

    def test_licence_classes_restrictions_and_trademark_mentions(self):
        classify=R['licence_class']
        self.assertEqual('RESTRICTIVE',classify('Business Source License 1.1'))
        self.assertEqual('RESTRICTIVE',classify('MIT permission is hereby granted, free of charge. For non-commercial use only.'))
        self.assertEqual('RESTRICTIVE',classify('Server Side Public License'))
        self.assertEqual('AGPL-3.0',classify('GNU AFFERO GENERAL PUBLIC LICENSE. Brand use applies whether commercial or non-commercial in nature.'))
        self.assertEqual('MIT',classify('Permission is hereby granted, free of charge'))
        self.assertEqual('UNKNOWN',classify('Unspecified licence'))

    def test_restrictive_licence_records_other_rejection_before_acceptance(self):
        fn=R['licence_gate'];g=fn.__globals__;original={k:g[k] for k in ['parent_licence','decide']};calls=[]
        g['parent_licence']=lambda row:'RESTRICTIVE'
        g['decide']=lambda *args:calls.append(args)
        try:
            with self.assertRaises(R['LicenceRejected']):fn(dict(repo='synthetic',rank=1))
            self.assertEqual('OTHER',calls[0][2]);self.assertTrue(calls[0][3].startswith('LICENCE:'))
        finally:g.update(original)

    def test_accepted_parent_licence_bytes_rechecked(self):
        for item in R['accepted']():
            record=json.loads((KEY/'t50_licences'/(item['candidate_id']+'.json')).read_text())
            self.assertEqual(item['licence_at_parent'],record['licence_at_parent'])
            for detail in record['files']:
                raw=R['M']['git'](item['repo'],'show',item['parent_commit']+':'+detail['path'])
                self.assertEqual(detail['sha256'],hashlib.sha256(raw).hexdigest())
                self.assertEqual(detail['licence_class'],R['licence_class'](raw.decode()))

    def test_licence_gate_reads_parent_instead_of_restrictive_child(self):
        fixture=T['BuildTests']();fixture.setUp()
        fn=R['parent_licence'];g=fn.__globals__;names=['KEY','M','require_current','record_preview'];saved={k:g[k] for k in names};calls=[]
        try:
            before=dict(fixture.initial,LICENSE='Permission is hereby granted, free of charge.\n')
            parent=fixture.repo.revision(before,fixture.last)
            child=fixture.repo.revision(dict(before,LICENSE='Business Source License 1.1\n'),parent)
            def read(repo,*args):
                calls.append(args)
                return fixture.repo.run(*args).encode()
            g['KEY']=fixture.folder/'new-key';g['KEY'].mkdir()
            g['M']=dict(git=read);g['require_current']=lambda row:None;g['record_preview']=lambda row,kind:None
            row=dict(repo='synthetic',candidate_id='synthetic',parent_commit=parent,fix_commit=child)
            self.assertEqual('MIT',fn(row))
            self.assertIn(('show',parent+':LICENSE'),calls)
            self.assertNotIn(('show',child+':LICENSE'),calls)
        finally:
            g.update(saved);fixture.tearDown()


class PackageTests(unittest.TestCase):
    def test_columns_only_Q_items_and_lf_lines(self):
        items=rows(B['OUT']/'items.csv');key=rows(KEY/'e13_key.csv');full=rows(KEY/'accepted_full_t50.csv')
        self.assertEqual(['item_id','repo','operation','proposition'],list(items[0]))
        self.assertEqual(list(rows(KEY/'e12_key.csv')[0]),list(key[0]))
        self.assertEqual(list(rows(KEY/'accepted_full_t49.csv')[0])+['licence_at_parent'],list(full[0]))
        expected=[f'Q{i:02}' for i in range(1,len(items)+1)]
        self.assertEqual(expected,[r['item_id'] for r in items]);self.assertEqual(set(expected),{p.name for p in B['OUT'].iterdir() if p.is_dir()})
        self.assertEqual([r['proposition'] for r in full],[r['proposition'] for r in items])
        self.assertTrue(all(r['set']=='new' and r['source_task']=='T50' for r in key+full))
        self.assertNotIn(b'\r',(B['OUT']/'items.csv').read_bytes())
        self.assertIsNone(B['FORBIDDEN'].search((B['OUT']/'items.csv').read_text()))

    def test_Q_shuffle_new_salt_private_and_order_independent(self):
        salt=(KEY/'e13_shuffle_salt.txt').read_text().strip();accepted=R['accepted']()
        self.assertEqual(B['q_order'](accepted,salt),B['q_order'](list(reversed(accepted)),salt))
        expected=[dict(item_id=f'Q{i:02}',source_item=r['item_id']) for i,r in enumerate(B['q_order'](accepted,salt),1)]
        self.assertEqual(expected,rows(KEY/'e13_shuffle_mapping_t50b.csv'))
        for name in ['shuffle_salt.txt','e8b_shuffle_salt.txt','e10_shuffle_salt.txt','e12_shuffle_salt.txt']:self.assertNotEqual(salt,(KEY/name).read_text().strip())
        for p in B['OUT'].rglob('*'):
            if p.is_file():self.assertNotIn(salt.encode(),p.read_bytes())

    def test_package_hashes_leakage_privacy_and_eight_file_cap(self):
        log=json.loads((KEY/'e13_build_log_t50b.json').read_text());out=B['OUT']
        actual={p.relative_to(out).as_posix():B['B']['sha'](p.read_bytes()) for p in out.rglob('*') if p.is_file()}
        self.assertEqual(log['package_hashes'],actual);self.assertTrue(all(log['assertions'].values()))
        self.assertEqual(len(R['previous_items']())+len(R['accepted']()),log['summary']['all_items_cross_checked'])
        incident=json.loads((KEY/'e13_preview_privacy_incident.json').read_text())
        needles=B['B']['O']['fixture_needles'](sorted(B['B']['O']['AUTH'].glob('*.yaml')))|{incident['observed_value'].encode()}
        for relative in actual:self.assertFalse(B['B']['O']['privacy_findings']((out/relative).read_bytes(),needles),relative)
        for detail in log['items']:
            self.assertLessEqual(sum(p.startswith('impl/') for p in detail['files']),8)
            self.assertTrue(set(detail['protected'])<={p.split('/',1)[1] for p in detail['files']})
        audit=runpy.run_path(str(HERE/'audit_t50b.py'))
        findings,prose=audit['reason_privacy_scan'](rows(KEY/'review_decisions_t50.csv'),needles)
        self.assertEqual(2,len(prose));self.assertFalse(findings)


class SyntheticPackageTests(unittest.TestCase):
    def setUp(self):
        self.fixture=T['BuildTests']();self.fixture.setUp()
        self.new=dict(self.fixture.b,source_task='T50',licence_at_parent='Apache-2.0')
        self.old=dict(self.fixture.a,source_task='T49')

    def tearDown(self):self.fixture.tearDown()

    def prepare(self):return B['prepare']([self.new],[self.old],{'synthetic':self.fixture.repo.path},'new synthetic salt')

    def test_cross_item_parent_only_and_metadata_absence(self):
        files,_,log,full,_=self.prepare()
        self.assertEqual('true',full[0]['cross_item_flag']);self.assertNotIn('Q01/impl/Helper.java',files)
        self.assertEqual(b'class B {}\n',files['Q01/impl/B.java'])
        for data in files.values():
            self.assertNotIn(self.new['fix_commit'].encode(),data);self.assertNotIn(self.new['message_excerpt'].encode(),data)

    def test_overwrite_refused_and_prior_files_untouched(self):
        result=self.prepare();out=self.fixture.folder/'e13_blind';key=self.fixture.folder/'key';key.mkdir()
        (key/'existing.csv').write_bytes(b'unchanged')
        B['publish'](result,out,key)
        with self.assertRaises(B['B']['O']['BuildError']):B['publish'](result,out,key)
        self.assertEqual(b'unchanged',(key/'existing.csv').read_bytes())
        self.assertEqual({'contract','impl'},{p.name for p in (out/'Q01').iterdir()})

    def test_forbidden_words_and_nonparent_locators(self):
        for word in ['E13','T50','T49']:
            self.new['proposition']='GET /a: contract says '+word+'; implementation does blue'
            with self.assertRaises((AssertionError,B['B']['O']['BuildError'])):self.prepare()
        self.new['proposition']=self.fixture.b['proposition']
        self.new['proposition_check']=json.dumps({'contract':[self.fixture.last+':api.yaml:1'],'implementation':[self.fixture.child+':B.java:1']})
        with self.assertRaises(B['B']['O']['BuildError']):self.prepare()

    def test_build_rejects_missing_or_restrictive_licence(self):
        for value in ['',None,'UNKNOWN','RESTRICTIVE']:
            self.new['licence_at_parent']=value
            with self.assertRaises(AssertionError):self.prepare()

if __name__=='__main__':unittest.main()
