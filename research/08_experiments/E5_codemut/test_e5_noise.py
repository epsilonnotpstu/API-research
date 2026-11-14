"""T22 synthetic controls only; the external process boundary is always mocked."""
import copy
import json
from pathlib import Path
import shutil
from unittest.mock import patch

from test_e5_pipeline import FixtureCase, dump, ident
import e5_common as c
import e5_pipeline as pipeline
import summarise_e5 as summary
import validate_pair as vp


class NoiseTests(FixtureCase):
    def setUp(self):
        super().setUp()
        self.noise = {role:self.f.root / ('noise-' + role) for role in ('control','control_repeat')}
        for run in self.noise.values(): self.clone_control(run)
        pipeline.write_ledger(self.f.mut / 'noise-runs.tsv',[
            dict(seed=1,role=role,run_dir=str(run),harness_exit='0',status='COMPLETE')
            for role,run in self.noise.items()])

    def rehash(self,run):
        meta=c.load(run / 'run.json')
        meta['file_sha256']={p.name:c.sha(p) for p in run.iterdir() if p.is_file() and p.name!='run.json'}
        dump(run / 'run.json',meta)

    def clone_control(self,run):
        source=self.f.paths['control'];shutil.copytree(source,run)
        meta=c.load(run / 'run.json');project='project-'+run.name
        meta.update(run_id=run.name,compose_project=project,source_spec=str(run / 'spec.original.json'))
        for service in ('sut-market','mitmproxy'):
            path=run / (service+'-container.json');obj=c.load(path)[0]
            obj['Id']=ident(service+str(run));obj['Config']['Hostname']=run.name
            obj['Config']['Labels']['com.docker.compose.project']=project
            obj['HostConfig']['NetworkMode']=project+'_default'
            obj['HostConfig']['Binds']=[s.replace(str(source),str(run)) for s in (obj['HostConfig']['Binds'] or [])]
            for mount in obj['Mounts']:
                if mount['Type']=='bind':mount['Source']=str(run)
                if mount['Type']=='volume':mount.update(Name='anonymous-'+run.name,Source='/volumes/'+run.name)
            dump(path,[obj])
        dump(run / 'run.json',meta);self.rehash(run)

    def change_status(self,run,status,count=1):
        data=json.loads((run / 'exchanges.jsonl').read_text().splitlines()[0])
        data['response']['status']=status
        (run / 'exchanges.jsonl').write_text((json.dumps(data)+'\n')*count);self.rehash(run)

    def validate_noise(self):
        return vp.validate(self.noise['control'],self.noise['control_repeat'],self.f.mut,'noise')

    def analyse(self,pair=True,noise=True):
        if pair:pipeline.analyse_pair(self.f.mut)
        if noise:pipeline.analyse_pair(self.f.mut,'noise')
        return summary.summarise([self.f.mut])

    def test_same_control_build_passes_both_roles_are_code_control(self):
        r=self.validate_noise();self.assertEqual(r['status'],'PASS',r)
        self.assertEqual(r['kind'],'noise');self.assertIn('control_repeat_run',r)
        self.assertNotIn('mutant_run',r)
        for run in self.noise.values():self.assertEqual(c.load(run/'run.json')['code_mutation']['role'],'control')

    def test_mutant_cannot_be_used_as_control_repeat(self):
        r=vp.validate(self.noise['control'],self.f.paths['mutant'],self.f.mut,'noise')
        self.assertEqual(r['status'],'FAIL')
        self.assertTrue(any(x['check']=='control_repeat.treatment_image_chain' and x['status']=='FAIL' for x in r['checks']))

    def test_repeat_jar_source_and_role_provenance_are_strict(self):
        path=self.noise['control_repeat']/'run.json';original=c.load(path)
        for key,value in [('sut_jar_sha256','0'*64),('code_mutation',dict(original['code_mutation'],role='control_repeat')),
                          ('code_mutation',dict(original['code_mutation'],source_tree_sha256=self.f.manifest['mutated_tree_sha256']))]:
            with self.subTest(key=key,value=value):
                dump(path,dict(original,**{key:value}));self.assertEqual(self.validate_noise()['status'],'FAIL')
        dump(path,original)

    def test_noise_keeps_all_scenario_and_snapshot_rules(self):
        path=self.noise['control_repeat']/'run.json';original=c.load(path)
        for key,value in [('seed',2),('budget_seconds',301),('complete',False),('logger_max_body',1),('unknown',True)]:
            with self.subTest(key=key):
                dump(path,dict(original,**{key:value}));self.assertEqual(self.validate_noise()['status'],'FAIL')
        dump(path,original)
        (self.noise['control_repeat']/'jacoco.exec').write_bytes(b'tampered')
        self.assertEqual(self.validate_noise()['status'],'FAIL')

    def test_noise_runtime_order_allowed_but_values_and_multiplicity_strict(self):
        for role,run in self.noise.items():
            path=run/'mitmproxy-container.json';obj=c.load(path)
            obj[0]['Config']['Env']=['A=1','A=2','A=1'] if role=='control' else ['A=2','A=1','A=1']
            binds=[str(run)+':/custom-logs:rw','/fixed:/addon:ro']
            obj[0]['HostConfig']['Binds']=binds if role=='control' else binds[::-1]+binds[:1]
            dump(path,obj);self.rehash(run)
        self.assertEqual(self.validate_noise()['status'],'PASS')
        run=self.noise['control_repeat'];path=run/'mitmproxy-container.json';obj=c.load(path)
        obj[0]['Config']['Env'].pop();dump(path,obj);self.rehash(run)
        self.assertEqual(self.validate_noise()['status'],'FAIL')

    def set_noise_junit(self,run,name):
        import xml.etree.ElementTree as ET
        root=ET.Element('testsuites');case=ET.SubElement(ET.SubElement(root,'testsuite'),'testcase',name=name)
        ET.SubElement(case,'error').text='Schema Error'
        (run/'schemathesis.junit.xml').write_bytes(ET.tostring(root));self.rehash(run)

    def test_mapped_operation_asymmetric_junit_still_fails_for_noise(self):
        self.set_noise_junit(self.noise['control'],'GET /things')
        self.assertEqual(self.validate_noise()['status'],'FAIL')

    def test_other_operation_asymmetric_junit_excluded_from_noise_analysis(self):
        for run in self.noise.values():
            spec=c.load(run/'spec.original.json');spec['paths']['/other']={'get':{'responses':{'200':{'description':'ok'}}}}
            for name in ('spec.original.json','spec.test.json','generator-input.json'):dump(run/name,spec)
            meta=c.load(run/'run.json');meta['source_sha256']=c.sha(run/'spec.original.json');dump(run/'run.json',meta)
            data=json.loads((run/'exchanges.jsonl').read_text());data['request']['path']='/other';data['response']['status']=500
            with (run/'exchanges.jsonl').open('a') as stream:stream.write(json.dumps(data)+'\n')
            self.rehash(run)
        self.set_noise_junit(self.noise['control'],'GET /other')
        self.assertEqual(self.validate_noise()['status'],'PASS_WITH_EXCLUSION')
        rows=self.analyse(pair=False)
        noise=[r for r in rows if r['kind']=='noise']
        self.assertTrue(all(r['analysis_status']=='COMPLETE' and r['non_mutated_NEW']==0 for r in noise),noise)
        out=self.f.mut/'noise-analysis-s1-default'
        self.assertTrue(any(v['template']=='/other' for v in summary.violations(out/'control.raw.violations.jsonl')))
        self.assertFalse(any(v['template']=='/other' for v in summary.violations(out/'control.violations.jsonl')))

    def test_noise_cli_writes_separate_report(self):
        sentinel=self.f.mut/'pair-validation-s1.json';sentinel.write_text('unchanged\n')
        args=[str(self.noise['control']),str(self.noise['control_repeat']),str(self.f.mut),'--kind','noise']
        self.assertEqual(vp.main(args),0);self.assertEqual(sentinel.read_text(),'unchanged\n')
        self.assertEqual(c.load(self.f.mut/'noise-pair-validation-s1.json')['kind'],'noise')

    def test_noise_ledger_role_policy_is_distinct_and_duplicate_paths_fail(self):
        self.assertEqual(len(c.ledger(self.f.mut/'noise-runs.tsv','noise')),2)
        with self.assertRaises(ValueError):c.ledger(self.f.mut/'noise-runs.tsv')
        with self.assertRaises(ValueError):c.ledger(self.f.mut/'runs.tsv','noise')
        rows=c.ledger(self.f.mut/'noise-runs.tsv','noise');rows[1]['run_dir']=rows[0]['run_dir']
        pipeline.write_ledger(self.f.mut/'noise-runs.tsv',rows)
        with self.assertRaises(ValueError):c.paired_rows(self.f.mut/'noise-runs.tsv',kind='noise')

    def test_mocked_launch_uses_identical_control_inputs_and_keeps_pair_ledger(self):
        (self.f.mut/'noise-runs.tsv').unlink();before=c.sha(self.f.mut/'runs.tsv')
        def execute(command,*,env,log):
            run=c.EXP/'E1_pilot/runs/market'/env['PILOT_RUN_ID'];run.parent.mkdir(parents=True,exist_ok=True)
            self.clone_control(run);return 0
        with patch.object(pipeline,'harness_process',side_effect=execute) as launched,patch.object(c,'EXP',self.f.root/'future-experiment'):
            pipeline.run_pair(self.f.mut,['1'],'noise')
        self.assertEqual(launched.call_count,2);self.assertEqual(c.sha(self.f.mut/'runs.tsv'),before)
        a,b=launched.call_args_list
        self.assertEqual(a.args[0],b.args[0]);self.assertEqual(a.args[0][-5:],['baseline','NONE','0','1','300'])
        ea,eb=(call.kwargs['env'] for call in (a,b))
        self.assertNotEqual(ea['PILOT_RUN_ID'],eb['PILOT_RUN_ID'])
        self.assertEqual({k:v for k,v in ea.items() if k!='PILOT_RUN_ID'},{k:v for k,v in eb.items() if k!='PILOT_RUN_ID'})
        for env in (ea,eb):
            self.assertEqual(env['CODE_ROLE'],'control');self.assertEqual(env['SUT_IMAGE_OVERRIDE'],self.f.images['control']['Id'])
            self.assertEqual(env['SUT_JAR_OVERRIDE'],str(self.f.mut/'context-control/dist/market-sut.jar'))
            self.assertEqual(env['CODE_SOURCE_TREE_SHA256'],self.f.manifest['source_tree_sha256'])
            self.assertEqual((env['DATA_GEN'],env['SCHEMA_CHECKS'],env['MAX_EXAMPLES'],env['REQUEST_TIMEOUT_MS'],env['MITM_MAX_BODY']),
                             ('all','response_headers_conformance','100','10000','65536'))
        rows=c.ledger(self.f.mut/'noise-runs.tsv','noise')
        self.assertEqual([r['role'] for r in rows],['control','control_repeat']);self.assertTrue(all(r['status']=='COMPLETE' for r in rows))
        plan=c.load(self.f.mut/'noise-run-plan.json');self.assertEqual(len(set(plan['build_image_ids'].values())),1)
        self.assertFalse((self.f.mut/'run-plan.json').exists())

    def test_noise_failed_launch_and_interrupt_persist_only_noise_ledger(self):
        for outcome,status,code in [(7,'FAILED','7'),(KeyboardInterrupt(),'INTERRUPTED','130')]:
            with self.subTest(status=status):
                for name in ('noise-runs.tsv','noise-run-plan.json','noise-run-preflight.json','noise-run-s1-control.log'):
                    (self.f.mut/name).unlink(missing_ok=True)
                kwargs={'return_value':outcome} if isinstance(outcome,int) else {'side_effect':outcome}
                before=c.sha(self.f.mut/'runs.tsv')
                with patch.object(pipeline,'harness_process',**kwargs) as launched:
                    with self.assertRaises(ValueError):pipeline.run_pair(self.f.mut,['1','2'],'noise')
                self.assertEqual(launched.call_count,1)
                row=c.ledger(self.f.mut/'noise-runs.tsv','noise')[0]
                self.assertEqual((row['status'],row['harness_exit']),(status,code));self.assertEqual(c.sha(self.f.mut/'runs.tsv'),before)

    def test_existing_noise_ledger_cannot_be_resumed(self):
        with patch.object(pipeline,'harness_process') as launched:
            with self.assertRaises(ValueError):pipeline.run_pair(self.f.mut,['1'],'noise')
            launched.assert_not_called()

    def test_noise_metrics_retain_manifest_mapped_ops_and_separate_files(self):
        self.change_status(self.noise['control_repeat'],500)
        before=c.sha(self.f.mut/'runs.tsv');rows=self.analyse()
        self.assertEqual(len(rows),4);noise=[r for r in rows if r['kind']=='noise']
        self.assertTrue(all(r['analysis_status']=='COMPLETE' and r['mutated_NEW']==2 and r['expected_signal_NEW']==1 for r in noise),noise)
        self.assertTrue(all(r['signal_exceeds_noise']=='NOT_APPLICABLE' for r in noise))
        self.assertEqual(c.sha(self.f.mut/'runs.tsv'),before)
        self.assertTrue((self.f.mut/'analysis-s1-default/mutant.violations.jsonl').exists())
        self.assertTrue((self.f.mut/'noise-analysis-s1-default/control_repeat.violations.jsonl').exists())
        with self.assertRaises(ValueError):pipeline.analyse_pair(self.f.mut,'noise')

    def test_noise_persistent_increase_decrease_and_vanished_count_on_mapped_ops(self):
        cases=[(1,3,'INCREASED'),(3,1,'DECREASED'),(1,0,'VANISHED')]
        for before,after,key in cases:
            with self.subTest(key=key):
                self.change_status(self.noise['control'],500,before)
                self.change_status(self.noise['control_repeat'],500 if after else 200,after or 1)
                # Reuse saved captures, but use a fresh output directory for each synthetic case.
                for oracle in ('default','sut'):
                    shutil.rmtree(self.f.mut/f'noise-analysis-s1-{oracle}',ignore_errors=True)
                rows=self.analyse(pair=False);noise=[r for r in rows if r['kind']=='noise']
                self.assertTrue(all(r['mutated_'+key]==2 for r in noise),noise)

    def test_signal_true_with_no_expected_fingerprint_in_either_noise_run(self):
        rows=self.analyse();pairs=[r for r in rows if r['kind']=='pair']
        self.assertTrue(all(r['signal_exceeds_noise'] is True for r in pairs),pairs)
        self.assertTrue(all(json.loads(r['signal_noise_detail'])['qualifying_fingerprints'] for r in pairs))

    def test_noise_fingerprint_presence_blocks_signal_even_when_noise_is_vanished(self):
        self.change_status(self.noise['control'],500)
        rows=self.analyse();pairs=[r for r in rows if r['kind']=='pair']
        self.assertTrue(all(r['signal_exceeds_noise'] is False for r in pairs),pairs)

    def test_increased_expected_pair_signal_can_exceed_absent_noise(self):
        self.change_status(self.f.paths['control'],500)
        self.change_status(self.f.paths['mutant'],500,3)
        rows=self.analyse();pairs=[r for r in rows if r['kind']=='pair']
        self.assertTrue(all(r['expected_signal_INCREASED']==1 and r['signal_exceeds_noise'] is True for r in pairs),pairs)

    def test_missing_or_failed_noise_is_unknown_never_false_or_zero(self):
        rows=self.analyse(noise=False)
        self.assertTrue(all(r['signal_exceeds_noise']=='UNKNOWN' for r in rows if r['kind']=='pair'))
        self.assertTrue(all(r['mutated_NEW']=='' for r in rows if r['kind']=='noise'))

    def test_same_oracle_noise_only(self):
        rows=self.analyse();p=self.f.mut/'noise-analysis-s1-sut/analysis.json';record=c.load(p);record['oracle']='default';dump(p,record)
        pairs=[r for r in summary.summarise([self.f.mut]) if r['kind']=='pair']
        self.assertEqual([r['signal_exceeds_noise'] for r in pairs],[True,'UNKNOWN'])

    def test_different_seed_noise_cannot_supply_comparison(self):
        rows=c.ledger(self.f.mut/'noise-runs.tsv','noise')
        for row in rows:row['seed']='2'
        pipeline.write_ledger(self.f.mut/'noise-runs.tsv',rows)
        for run in self.noise.values():
            meta=c.load(run/'run.json');meta['seed']=2;dump(run/'run.json',meta)
            path=run/'schemathesis-argv.txt';path.write_text(path.read_text().replace('--hypothesis-seed\n1\n','--hypothesis-seed\n2\n'))
            self.rehash(run)
        pairs=[r for r in self.analyse() if r['kind']=='pair']
        self.assertTrue(all(r['signal_exceeds_noise']=='UNKNOWN' for r in pairs),pairs)

    def test_comparison_rejects_reused_run_even_with_valid_data(self):
        self.analyse();evidence={}
        summary.summarise_kind([self.f.mut],'pair',evidence)
        summary.summarise_kind([self.f.mut],'noise',evidence)
        key=(str(self.f.mut),1,'default')
        pair=evidence[(*key,'pair')];noise=evidence[(*key,'noise')]
        reused=(noise[0],dict(noise[1],control=pair[1]['control']),noise[2])
        with self.assertRaisesRegex(ValueError,'reuse a run directory'):summary.compare_noise(self.f.mut,pair,reused)

    def test_comparison_rejects_diagonally_reused_container_or_proxy_volume(self):
        self.analyse();evidence={}
        summary.summarise_kind([self.f.mut],'pair',evidence)
        summary.summarise_kind([self.f.mut],'noise',evidence)
        key=(str(self.f.mut),1,'default');pair=evidence[(*key,'pair')];noise=evidence[(*key,'noise')]
        # Each pair alone has distinct IDs; only cross-comparison reuse reveals this.
        for service in ('sut-market','mitmproxy'):
            source=c.inspection(self.f.paths['control']/(service+'-container.json'))
            path=self.noise['control_repeat']/(service+'-container.json');original=c.load(path)
            obj=copy.deepcopy(original);obj[0]['Id']=source['Id'];dump(path,obj)
            with self.assertRaisesRegex(ValueError,'reuse a container'):summary.compare_noise(self.f.mut,pair,noise)
            dump(path,original)
        path=self.noise['control_repeat']/'mitmproxy-container.json';obj=c.load(path)
        source=c.inspection(self.f.paths['control']/'mitmproxy-container.json')
        obj[0]['Mounts'][1]['Name']=source['Mounts'][1]['Name'];dump(path,obj)
        with self.assertRaisesRegex(ValueError,'share a proxy volume'):summary.compare_noise(self.f.mut,pair,noise)

    def test_missing_operation_exposure_is_unknown(self):
        run=self.noise['control_repeat'];data=json.loads((run/'exchanges.jsonl').read_text());data['request']['path']='/not-things'
        (run/'exchanges.jsonl').write_text(json.dumps(data)+'\n');self.rehash(run)
        pairs=[r for r in self.analyse() if r['kind']=='pair']
        self.assertTrue(all(r['signal_exceeds_noise']=='UNKNOWN' for r in pairs),pairs)

    def test_cross_comparison_scenario_drift_is_unknown(self):
        for run in self.noise.values():
            meta=c.load(run/'run.json');meta['health_path']='/other-health';dump(run/'run.json',meta)
        pairs=[r for r in self.analyse() if r['kind']=='pair']
        self.assertTrue(all(r['signal_exceeds_noise']=='UNKNOWN' for r in pairs),pairs)

    def test_no_expected_changed_signal_is_false_with_valid_noise(self):
        self.change_status(self.f.paths['mutant'],200)
        pairs=[r for r in self.analyse() if r['kind']=='pair']
        self.assertTrue(all(r['signal_exceeds_noise'] is False for r in pairs),pairs)

    def test_noise_output_tamper_is_not_accepted(self):
        self.analyse();path=self.f.mut/'noise-analysis-s1-default/control_repeat.violations.jsonl';path.write_text('fabricated\n')
        rows=summary.summarise([self.f.mut]);pairs=[r for r in rows if r['kind']=='pair']
        self.assertEqual(pairs[0]['signal_exceeds_noise'],'UNKNOWN')
        self.assertEqual([r for r in rows if r['kind']=='noise'][0]['analysis_status'],'FAIL')

    def test_noise_only_discovery_and_planned_unattempted_seed(self):
        (self.f.mut/'runs.tsv').unlink()
        work=self.f.root/'discovery/work';work.mkdir(parents=True)
        dest=work/'noise-only';self.f.mut.rename(dest);self.f.mut=dest
        # Captured code manifests contain hashes, not build paths; same fixture stays valid.
        dump(dest/'noise-run-plan.json',{'seeds':[1,2],'manifest_sha256':c.sha(dest/'manifest.json')})
        pipeline.analyse_pair(dest,'noise')
        output=self.f.root/'discovered.csv'
        self.assertEqual(summary.main(['--root',str(work.parent),'--out',str(output)]),1)
        import csv
        with output.open() as stream:rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),4);self.assertTrue(all(r['kind']=='noise' for r in rows))
        self.assertTrue(all(r['mutated_NEW']=='' and r['error'] for r in rows if r['seed']=='2'))
