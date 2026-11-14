"""Synthetic saved-run evidence only. No harness, Docker, Maven, Java or SUT execution."""
import copy
import csv
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codemut
import e5_common as c
import e5_pipeline as pipeline
import summarise_e5 as summary
import validate_pair as vp

SCRATCH = Path(os.environ.get('E5_TEST_SCRATCH', str(HERE.parent.parent / '09_collab/logs/T20_scratch')))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def ident(value):
    return 'sha256:' + c.canonical(value)


class Fixture:
    def __init__(self, root):
        self.root = root
        self.harness = root / 'frozen-harness'; self.tools = root / 'trusted-tools'; self.emb = root / 'frozen-emb'
        self.harness.mkdir(); self.tools.mkdir(); (self.emb / 'dist').mkdir(parents=True)
        (self.harness / 'hash-only.txt').write_text('Not an executable harness fixture.\n')
        for name in ('run_pilot.sh','run_metadata.py'):
            (self.harness / name).write_text('# Non-executable provenance fixture\n')
        for name in ('attribute.py','conformance.py','specmut.py'):
            shutil.copyfile(HERE.parent / 'tools' / name, self.tools / name)
        (self.emb / 'dist/jacocoagent.jar').write_bytes(b'synthetic-agent')
        (self.emb / 'dist/jacococli.jar').write_bytes(b'synthetic-cli')
        (self.emb / 'compose.yaml').write_text('synthetic compose bytes\n')
        source = root / 'checkout'; source.mkdir()
        original = 'class Handler { Object read(java.util.Optional<Object> x) { return x.orElse(null); } }\n'
        (source / 'Handler.java').write_text(original)
        site = {'site_id':'synthetic-null','sut':'market','operator':'DROP_NULL_CHECK','file':'Handler.java','line':1,
                'before':'x.orElse(null)','after':'x.get()','source_sha256':c.sha(source / 'Handler.java'),
                'expected_L1':'IMPL','expected_L2':'I-CRASH','expected_conformance_signal':['SERVER_ERROR'],
                'operations':[{'path':'/things','method':'get'}]}
        self.mut = root / 'pair'
        self.manifest = codemut.mutate(source,self.mut,'market','DROP_NULL_CHECK',[site],site_id=site['site_id'])
        shutil.copytree(source,self.mut / 'control.source')
        self.base = {'Id':ident('base'),'RepoDigests':['amazoncorretto@' + ident('base')],
                     'RootFS':{'Layers':[ident('base-layer')]},'Os':'linux','Architecture':'amd64','Config':{}}
        dump(self.mut / 'runtime-base.json',[self.base])
        dump(self.mut / 'maven-image.json',[{'Id':ident('maven')}])
        (self.mut / 'maven-arguments.txt').write_text('-B\npackage\n')
        deps = {}
        self.images = {}
        for role,folder,key in [('control','control.source','source_tree_sha256'),('mutant','source','mutated_tree_sha256')]:
            cache = self.mut / ('m2-' + role); cache.mkdir(); (cache / 'a.jar').write_bytes(b'same dependency')
            deps[role] = vp.dependencies(cache)
            (self.mut / f'build-{role}.log').write_text('synthetic successful build fixture\n')
            jar = self.mut / folder / c.JARS['market']; jar.parent.mkdir(parents=True); jar.write_bytes(role.encode() + b'-jar')
            ctx = self.mut / ('context-' + role); (ctx / 'dist').mkdir(parents=True); (ctx / 'dockerfiles').mkdir()
            shutil.copyfile(jar,ctx / 'dist/market-sut.jar')
            shutil.copyfile(self.emb / 'dist/jacocoagent.jar',ctx / 'dist/jacocoagent.jar')
            (ctx / 'dockerfiles/market.dockerfile').write_text('FROM ' + self.base['RepoDigests'][0] + '\nCOPY ./dist/market-sut.jar .\n')
            self.rehash_context(role)
            tag = 'r1-market-sut:e5-synthetic-' + role
            image = {'Id':ident(role),'RepoTags':[tag], 'RepoDigests':[], 'Os':'linux','Architecture':'amd64',
                     'RootFS':{'Layers':[ident('base-layer'),ident(role + '-jar-layer')]},
                     'Config':{'Env':['SAME=1'],'Entrypoint':['java','-jar','market-sut.jar'], 'WorkingDir':'/',
                               'Labels':{'org.r1.jar_sha256':c.sha(jar),'org.r1.source_tree_sha256':self.manifest[key]}}}
            self.images[role] = image; dump(self.mut / f'image-{role}.json',[image])
            (self.mut / f'tag-{role}.txt').write_text(tag + '\n')
        dump(self.mut / 'resolved-artifacts.json',deps)
        self.paths = {'control':root / 'control-run','mutant':root / 'mutant-run'}
        self.spec = {'swagger':'2.0','host':'localhost:9000','basePath':'/','info':{'title':'synthetic','version':'1'},
                     'paths':{'/things':{'get':{'responses':{'200':{'description':'ok','schema':{'type':'object'}}}}}}}
        for role,run in self.paths.items(): self.make_run(role,run)
        self.write_ledger()

    def rehash_context(self,role):
        ctx = self.mut / ('context-' + role)
        (self.mut / f'context-{role}.sha256').write_text(''.join(c.sha(p) + '  ./' + p.relative_to(ctx).as_posix() + '\n' for p in sorted(ctx.rglob('*')) if p.is_file()))

    def make_run(self,role,run):
        run.mkdir(); image = self.images[role]; project = 'project-' + role
        for name in ('spec.original.json','spec.test.json','generator-input.json'): dump(run / name,self.spec)
        dump(run / 'derecurse-cuts.json',[])
        (run / 'sut-config.env').write_text('SUT_SERVICE=sut-market\nINTERNAL_PORT=8080\n')
        shutil.copyfile(self.mut / 'manifest.json',run / 'code.manifest.json')
        dump(run / 'compose.code-image.json',{'services':{'sut-market':{'image':image['Id']}}})
        (run / 'compose.resolved.yaml').write_text('fixture resolved compose: ' + role)
        status = 200 if role == 'control' else 500
        exchange = {'request':{'method':'GET','path':'/things','url':'http://sut-market:8080/things','query':{},'headers':{},'body':{'text':'','truncated':False}},
                    'response':{'status':status,'headers':{'content-type':'application/json'},'body':{'text':'{}','truncated':False}}}
        (run / 'exchanges.jsonl').write_text(json.dumps(exchange) + '\n')
        (run / 'jacoco.exec').write_bytes(b'synthetic coverage')
        (run / 'schemathesis.junit.xml').write_text('<testsuites tests="1"><testsuite tests="1"><testcase name="synthetic"/></testsuite></testsuites>')
        argv = ['run','/work/generator-input.json','--base-url','http://mitmproxy:8080/','--checks','response_headers_conformance',
                '--hypothesis-seed','1','--hypothesis-max-examples','100','--request-timeout','10000',
                '--hypothesis-phases','explicit,generate','--sanitize-output','true','--data-generation-method','all']
        (run / 'schemathesis-argv.txt').write_text('\n'.join(argv) + '\n')
        (run / 'schemathesis-help.txt').write_text('same synthetic help\n')
        generator = {'Id':ident('generator'),'RepoDigests':['generator@' + ident('generator')]}
        proxy = {'Id':ident('proxy'),'RepoDigests':['proxy@' + ident('proxy')]}
        for key,data in [('sut-market-image',image),('schema-image',generator),('mitmproxy-image',proxy)]: dump(run / (key + '.json'),[data])
        def container(service, img):
            config = copy.deepcopy(image['Config'] if service == 'sut-market' else {'Env':['LOG=/custom-logs'],'Entrypoint':['mitmdump'],'WorkingDir':'/','Labels':{}})
            config.update(Hostname='random-' + role, Image=img, Volumes=None)
            config['Labels'].update({'com.docker.compose.project':project,'com.docker.compose.service':service})
            return {'Id':ident(service + '-' + role),'Image':img,'Config':config,
                    'HostConfig':{'NetworkMode':project + '_default','Binds':None,'PortBindings':{'8080/tcp':[{'HostIp':'127.0.0.1','HostPort':'18080'}]},'Memory':0},
                    'Mounts':[], 'Platform':'linux','Driver':'overlay2','AppArmorProfile':'','Path':config['Entrypoint'][0], 'Args':config['Entrypoint'][1:]}
        dump(run / 'sut-market-container.json',[container('sut-market',image['Id'])])
        pc = container('mitmproxy',proxy['Id'])
        pc['Mounts'] = [{'Type':'bind','Source':str(run),'Destination':'/custom-logs','RW':True},
                        {'Type':'volume','Name':'anonymous-' + role,'Source':'/volumes/' + role,'Destination':'/home/mitmproxy/.mitmproxy','RW':True}]
        pc['HostConfig']['Binds'] = [str(run) + ':/custom-logs:rw']
        dump(run / 'mitmproxy-container.json',[pc])
        meta = {'run_id':run.name,'sut':'market','mode':'baseline','fault':'NONE','severity':0,'seed':1,
                'source_spec':str(run / 'spec.original.json'),'source_sha256':c.sha(run / 'spec.original.json'),
                'budget_seconds':300,'max_examples':100,'compose_project':project,'started_at':role,'updated_at':role,'finished_at':role,
                'complete':True,'harness_exit':'0','phase':'complete','coverage_exit':'0','cleanup_exit':'0','schemathesis_exit':'1',
                'auth':'none','auth_source':'none','auth_source_sha256':None,'health_path':'/health','base_path':'/',
                'request_timeout_ms':10000,'hypothesis_phases':'explicit,generate','schema_checks':'response_headers_conformance',
                'logger_max_body':65536,'host_port':'127.0.0.1:18080','jacoco_port':'127.0.0.1:16300',
                'sut_service':'sut-market','internal_port':8080,'sut_image':image['RepoTags'][0],
                'sut_jar_sha256':image['Config']['Labels']['org.r1.jar_sha256'],
                'code_mutation':{'role':role,'source_tree_sha256':self.manifest['source_tree_sha256' if role == 'control' else 'mutated_tree_sha256'],'manifest_sha256':c.sha(self.mut / 'manifest.json')},
                'jacoco_agent_sha256':c.sha(self.emb / 'dist/jacocoagent.jar'),'jacoco_cli_sha256':c.sha(self.emb / 'dist/jacococli.jar'),
                'harness_version':2,'emb_commit':'synthetic-commit','emb_status_porcelain':'','schemathesis_image':'synthetic-generator:1',
                'images':{key:{'id':data['Id'],'repo_digests':data.get('RepoDigests',[]),'repo_tags':data.get('RepoTags',[])} for key,data in [('sut-market-image',image),('schema-image',generator),('mitmproxy-image',proxy)]},
                'tool_sha256':{p.name:c.sha(p) for p in self.tools.glob('*.py')},
                'harness_sha256':{p.name:c.sha(p) for p in self.harness.iterdir()},
                'emb_config_sha256':{'compose.yaml':c.sha(self.emb / 'compose.yaml')},'limitations':['synthetic']}
        dump(run / 'run.json',meta); self.rehash_run(role)

    def rehash_run(self,role):
        run = self.paths[role]; meta = c.load(run / 'run.json')
        meta['file_sha256'] = {p.name:c.sha(p) for p in run.iterdir() if p.is_file() and p.name != 'run.json'}
        dump(run / 'run.json',meta)

    def change_meta(self,role,key,value):
        run = self.paths[role]; meta = c.load(run / 'run.json'); meta[key] = value; dump(run / 'run.json',meta)

    def write_ledger(self):
        with (self.mut / 'runs.tsv').open('w',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=c.LEDGER_FIELDS,delimiter='\t'); writer.writeheader()
            writer.writerows(dict(seed=1,role=role,run_dir=str(run),harness_exit='0',status='COMPLETE') for role,run in self.paths.items())

    def validate(self): return vp.validate(self.paths['control'],self.paths['mutant'],self.mut)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-',dir=SCRATCH); self.addCleanup(self.temp.cleanup)
        self.f = Fixture(Path(self.temp.name))
        for key,value in [('TOOLS',self.f.tools),('HARNESS',self.f.harness),('EMB',self.f.emb)]:
            mock = patch.object(c,key,value); mock.start(); self.addCleanup(mock.stop)

    def add_other_operation(self):
        for role,run in self.f.paths.items():
            spec=c.load(run / 'spec.original.json');spec['paths']['/other']={'get':{'responses':{'200':{'description':'ok'}}}}
            for name in ('spec.original.json','spec.test.json','generator-input.json'):dump(run / name,spec)
            self.f.change_meta(role,'source_sha256',c.sha(run / 'spec.original.json'));self.f.rehash_run(role)

    def assert_fail(self,part=None):
        r = self.f.validate()
        self.assertEqual(r['status'],'FAIL')
        if part: self.assertTrue(any(part in x['check'] and x['status'] == 'FAIL' for x in r['checks']),r)
        return r


class PairValidationTests(FixtureCase):
    def test_complete_pair_with_intended_different_images_passes(self):
        r = self.f.validate(); self.assertEqual(r['status'],'PASS',r)
        self.assertTrue(all(x['status'] == 'PASS' for x in r['checks']))

    def test_incomplete_run_fails(self):
        self.f.change_meta('mutant','complete',False); self.assert_fail('mutant.completion')

    def test_missing_artifact_fails(self):
        (self.f.paths['mutant'] / 'jacoco.exec').unlink(); self.assert_fail()

    def test_captured_exchange_tamper_fails(self):
        (self.f.paths['mutant'] / 'exchanges.jsonl').write_text('{}\n'); self.assert_fail()

    def test_seed_budget_checks_timeout_and_unknown_metadata_drift_fail(self):
        for key,value in [('seed',2),('budget_seconds',301),('schema_checks','all'),('request_timeout_ms',999),('unknown_setting',1)]:
            with self.subTest(key=key):
                meta = c.load(self.f.paths['mutant'] / 'run.json')
                self.f.change_meta('mutant',key,value); self.assert_fail()
                dump(self.f.paths['mutant'] / 'run.json',meta)

    def test_spec_must_be_unchanged_even_if_pair_agrees(self):
        for role,run in self.f.paths.items():
            dump(run / 'spec.test.json',{'different':'spec'}); self.f.rehash_run(role)
        self.assert_fail()

    def test_generator_all_required_even_if_both_same(self):
        for role,run in self.f.paths.items():
            p = run / 'schemathesis-argv.txt'; p.write_text(p.read_text().replace('\nall\n','\npositive\n')); self.f.rehash_run(role)
        self.assert_fail()

    def test_generator_and_proxy_image_drift_fail(self):
        run = self.f.paths['mutant']; image = c.load(run / 'schema-image.json'); image[0]['Id'] = ident('changed')
        dump(run / 'schema-image.json',image); self.f.rehash_run('mutant'); self.assert_fail()

    def test_runtime_container_image_must_match_build(self):
        run = self.f.paths['mutant']; x = c.load(run / 'sut-market-container.json'); x[0]['Image'] = ident('other')
        dump(run / 'sut-market-container.json',x); self.f.rehash_run('mutant'); self.assert_fail()

    def test_image_labels_are_verified(self):
        path = self.f.mut / 'image-mutant.json'; x = c.load(path); x[0]['Config']['Labels']['org.r1.jar_sha256'] = '0'*64
        dump(path,x); self.assert_fail('build.mutant')

    def test_source_tree_and_patch_tampering_fail(self):
        (self.f.mut / 'source/Handler.java').write_text('changed\n'); self.assert_fail('build.source')

    def test_non_jar_context_drift_fails_even_if_checksums_recomputed(self):
        (self.f.mut / 'context-mutant/dist/jacocoagent.jar').write_bytes(b'other agent')
        self.f.rehash_context('mutant'); self.assert_fail('build.equal_non_jar')

    def test_unrecorded_context_file_fails(self):
        (self.f.mut / 'context-mutant/unrecorded').write_bytes(b'extra'); self.assert_fail('build.mutant')

    def test_dependency_drift_fails(self):
        (self.f.mut / 'm2-mutant/a.jar').write_bytes(b'changed'); self.assert_fail('build.maven')

    def test_runtime_base_prefix_is_verified(self):
        x = c.load(self.f.mut / 'image-mutant.json'); x[0]['RootFS']['Layers'][0] = ident('other base')
        dump(self.f.mut / 'image-mutant.json',x); self.assert_fail('build.mutant')

    def test_runtime_memory_drift_fails(self):
        run = self.f.paths['mutant']; x = c.load(run / 'sut-market-container.json'); x[0]['HostConfig']['Memory'] = 100
        dump(run / 'sut-market-container.json',x); self.f.rehash_run('mutant'); self.assert_fail('pair.equal')

    def test_shared_sut_state_mount_is_rejected(self):
        for role,run in self.f.paths.items():
            x = c.load(run / 'sut-market-container.json'); x[0]['Mounts'] = [{'Type':'volume','Destination':'/data','Source':'shared','RW':True}]
            dump(run / 'sut-market-container.json',x); self.f.rehash_run(role)
        self.assert_fail('pair.equal')

    def test_copied_manifest_role_and_tree_must_match(self):
        meta = c.load(self.f.paths['mutant'] / 'run.json'); meta['code_mutation']['role'] = 'control'
        dump(self.f.paths['mutant'] / 'run.json',meta); self.assert_fail('mutant.treatment')

    def test_current_tool_and_harness_drift_does_not_invalidate_recorded_pair(self):
        (self.f.tools / 'attribute.py').write_text('# changed\n')
        (self.f.harness / 'run_pilot.sh').unlink()
        self.assertEqual(self.f.validate()['status'],'PASS')

    def test_recorded_pair_snapshot_mismatch_fails(self):
        for field in ('tool_sha256','harness_sha256'):
            with self.subTest(field=field):
                path=self.f.paths['mutant']/'run.json';original=c.load(path)
                changed=copy.deepcopy(original);changed[field][next(iter(changed[field]))]='0'*64
                dump(path,changed);self.assert_fail('pair.equal');dump(path,original)

    def test_missing_empty_malformed_and_unsafe_recorded_snapshots_fail(self):
        for field in ('tool_sha256','harness_sha256'):
            for value in (None,{},[],{'../escape':'0'*64}):
                with self.subTest(field=field,value=value):
                    originals={run:c.load(run/'run.json') for run in self.f.paths.values()}
                    for run,original in originals.items():
                        changed=dict(original)
                        if value is None:changed.pop(field)
                        else:changed[field]=value
                        dump(run/'run.json',changed)
                    self.assert_fail()
                    for run,original in originals.items():dump(run/'run.json',original)

    def test_runtime_auth_override_rejected(self):
        for role in self.f.paths: self.f.change_meta(role,'auth_source','runtime-override')
        self.assert_fail()

    def test_stale_pass_is_replaced_with_fail(self):
        self.assertEqual(vp.main([str(self.f.paths['control']),str(self.f.paths['mutant']),str(self.f.mut)]),0)
        self.f.change_meta('mutant','complete',False)
        self.assertEqual(vp.main([str(self.f.paths['control']),str(self.f.paths['mutant']),str(self.f.mut)]),1)
        self.assertEqual(c.load(self.f.mut / 'pair-validation-s1.json')['status'],'FAIL')

    def test_validation_checks_do_not_disclose_container_env(self):
        run = self.f.paths['mutant']; x = c.load(run / 'sut-market-container.json'); x[0]['Config']['Env'] = ['SECRET=sentinel-private-value']
        dump(run / 'sut-market-container.json',x); self.f.rehash_run('mutant')
        self.assertNotIn('sentinel-private-value',json.dumps(self.assert_fail()))

    def test_path_traversal_in_artifact_inventory_fails(self):
        meta = c.load(self.f.paths['mutant'] / 'run.json'); meta['file_sha256']['../escape'] = '0'*64
        dump(self.f.paths['mutant'] / 'run.json',meta); self.assert_fail()

    def test_all_failures_accumulate(self):
        self.f.change_meta('mutant','complete',False); (self.f.mut / 'source/Handler.java').write_text('bad')
        r = self.assert_fail(); self.assertGreaterEqual(sum(x['status']=='FAIL' for x in r['checks']),2)


    def test_known_compose_json_metadata_glob_entry_is_accepted(self):
        for role,run in self.f.paths.items():
            meta=c.load(run / 'run.json'); meta['images']['compose.code-image']={'inspection_error':'0'}
            dump(run / 'run.json',meta)
        self.assertEqual(self.f.validate()['status'],'PASS')

    def test_unknown_collected_image_entry_fails(self):
        meta=c.load(self.f.paths['mutant'] / 'run.json'); meta['images']['unreviewed-image']={'id':ident('other')}
        dump(self.f.paths['mutant'] / 'run.json',meta)
        self.assert_fail('pair.equal')

    def test_malformed_metadata_is_a_reported_failure(self):
        dump(self.f.paths['mutant'] / 'run.json',[])
        self.assert_fail('mutant.metadata_read')

    def test_omitted_tool_hash_fails_even_if_both_runs_agree(self):
        for role,run in self.f.paths.items():
            meta=c.load(run / 'run.json'); meta['tool_sha256'].pop('attribute.py'); dump(run / 'run.json',meta)
        self.assert_fail()

    def test_missing_harness_version_in_both_runs_fails(self):
        for role,run in self.f.paths.items():
            meta=c.load(run / 'run.json'); meta.pop('harness_version'); dump(run / 'run.json',meta)
        self.assert_fail()

    def test_missing_code_manifest_fails(self):
        (self.f.paths['mutant'] / 'code.manifest.json').unlink()
        self.assert_fail('mutant.treatment')

    def test_junit_execution_errors_and_no_cases_fail(self):
        for xml in ('<testsuites/>','<testsuites><testcase><error>timeout</error></testcase></testsuites>'):
            (self.f.paths['mutant'] / 'schemathesis.junit.xml').write_text(xml)
            self.f.rehash_run('mutant'); self.assert_fail()

    def set_junit(self,role,errors):
        import xml.etree.ElementTree as ET
        root=ET.Element('testsuites')
        ET.SubElement(root,'testcase',name='synthetic')
        for name,text in errors:
            ET.SubElement(ET.SubElement(root,'testcase',name=name),'error').text=text
        (self.f.paths[role] / 'schemathesis.junit.xml').write_text(ET.tostring(root,encoding='unicode'))
        self.f.rehash_run(role)

    def test_identical_junit_errors_pass_with_full_recorded_note(self):
        errors=[('POST /register',"Schema Error: unsupported \\pL")]
        for role in self.f.paths: self.set_junit(role,errors)
        result=self.f.validate()
        self.assertEqual(result['status'],'PASS',result)
        self.assertEqual(result['junit_errors']['control'],result['junit_errors']['mutant'])
        self.assertEqual(result['notes'][0]['errors'],[{'testcase_name':errors[0][0],'error_text':errors[0][1]}])

    def test_junit_one_sided_changed_text_or_changed_testcase_fails(self):
        base=[('POST /register','unsupported regex')]
        cases=[(base,[]),([],base),(base,[('POST /register','timeout')]),(base,[('GET /other','unsupported regex')])]
        for control,mutant in cases:
            with self.subTest(control=control,mutant=mutant):
                self.set_junit('control',control);self.set_junit('mutant',mutant)
                self.assert_fail('pair.equal_junit_errors')

    def test_junit_error_set_ignores_order_and_duplicate_occurrences(self):
        errors=[('POST /register','regex'),('GET /other','schema')]
        self.set_junit('control',errors);self.set_junit('mutant',errors[::-1]+errors[:1])
        self.assertEqual(self.f.validate()['status'],'PASS')

    def test_network_project_names_sandbox_ids_and_env_order_are_incidental(self):
        for service in ('sut-market','mitmproxy'):
            for role,run in self.f.paths.items():
                path=run / (service+'-container.json');obj=c.load(path)
                obj[0]['NetworkSettings']={'SandboxID':'sandbox-'+role}
                obj[0]['Config']['Env']=['A=1','B=2'] if role=='control' else ['B=2','A=1']
                dump(path,obj);self.f.rehash_run(role)
        self.assertEqual(self.f.validate()['status'],'PASS')

    def test_foreign_network_name_and_changed_network_suffix_fail_for_both_services(self):
        for service in ('sut-market','mitmproxy'):
            path=self.f.paths['mutant'] / (service+'-container.json');original=c.load(path)
            for name in ('foreign_default','project-mutant_other'):
                obj=copy.deepcopy(original);obj[0]['HostConfig']['NetworkMode']=name
                dump(path,obj);self.f.rehash_run('mutant');self.assert_fail('pair.equal')
            dump(path,original);self.f.rehash_run('mutant')

    def test_env_values_and_duplicate_keys_remain_strict(self):
        for service in ('sut-market','mitmproxy'):
            path=self.f.paths['mutant'] / (service+'-container.json');original=c.load(path)
            for env in (['DIFFERENT=1'],['DUP=1','DUP=2']):
                obj=copy.deepcopy(original);obj[0]['Config']['Env']=env
                dump(path,obj);self.f.rehash_run('mutant');self.assert_fail('pair.equal')
            dump(path,original);self.f.rehash_run('mutant')

    def test_environment_multiset_and_bind_set_ignore_order_but_keep_values(self):
        for role,run in self.f.paths.items():
            for service in ('sut-market','mitmproxy'):
                path=run / (service+'-container.json');obj=c.load(path)
                obj[0]['Config']['Env']=['DUP=1','DUP=2','DUP=1'] if role=='control' else ['DUP=1','DUP=1','DUP=2']
                binds=[str(run)+':/custom-logs:rw','/trusted:/addons:ro']
                obj[0]['HostConfig']['Binds']=binds if role=='control' else binds[::-1]+binds[:1]
                dump(path,obj)
            self.f.rehash_run(role)
        self.assertEqual(self.f.validate()['status'],'PASS')
        run=self.f.paths['mutant'];path=run / 'mitmproxy-container.json';obj=c.load(path)
        obj[0]['Config']['Env'].pop();dump(path,obj);self.f.rehash_run('mutant');self.assert_fail('pair.equal')

    def test_bind_source_or_mount_options_remain_strict(self):
        path=self.f.paths['mutant'] / 'mitmproxy-container.json';original=c.load(path)
        for value in ('/foreign:/custom-logs:rw',str(self.f.paths['mutant'])+':/custom-logs:ro'):
            obj=copy.deepcopy(original);obj[0]['HostConfig']['Binds']=[value]
            dump(path,obj);self.f.rehash_run('mutant');self.assert_fail('pair.equal')

    def test_non_mutated_junit_asymmetry_passes_with_reasoned_exclusion(self):
        self.add_other_operation();self.set_junit('control',[('GET /other','Schema Error')])
        result=self.f.validate();self.assertEqual(result['status'],'PASS_WITH_EXCLUSION',result)
        self.assertEqual([(x['method'],x['path']) for x in result['excluded_ops']],[('GET','/other')])
        self.assertTrue(result['excluded_ops'][0]['reason'])

    def test_any_mutated_error_difference_fails_even_with_other_excludable_errors(self):
        self.add_other_operation();self.set_junit('control',[('GET /other','schema'),('GET /things','schema')])
        self.assert_fail('pair.equal_junit_errors')

    def test_unmappable_error_name_fails_closed(self):
        self.set_junit('control',[('unmappable generator failure','schema')]);self.assert_fail('pair.equal_junit_errors')

    def test_report_can_stage_outside_mut_dir_and_remains_atomic(self):
        stage=self.f.root / 'report-stage';stage.mkdir()
        args=[str(self.f.paths['control']),str(self.f.paths['mutant']),str(self.f.mut),'--report-staging-dir',str(stage)]
        self.assertEqual(vp.main(args),0)
        self.assertEqual(c.load(self.f.mut / 'pair-validation-s1.json')['status'],'PASS')
        self.assertEqual(list(stage.iterdir()),[])
        self.assertFalse((self.f.mut / 'pair-validation-s1.json.tmp').exists())

    def test_launcher_failure_is_recorded_and_stops_without_executing_harness(self):
        (self.f.mut / 'runs.tsv').unlink()
        # Mock only the process boundary; no executable harness fixture exists.
        with patch.object(pipeline,'harness_process',return_value=7) as execute, patch.object(c,'EXP',self.f.root / 'future-experiment'):
            with self.assertRaises(ValueError): pipeline.run_pair(self.f.mut,[])
        self.assertEqual(execute.call_count,1)
        rows=c.ledger(self.f.mut / 'runs.tsv')
        self.assertEqual([(r['seed'],r['role'],r['harness_exit'],r['status']) for r in rows],[('1','control','7','FAILED')])
        self.assertEqual(execute.call_args.kwargs['env']['DATA_GEN'],'all')
        self.assertEqual(execute.call_args.kwargs['env']['SUT_IMAGE_OVERRIDE'],self.f.images['control']['Id'])
        self.assertEqual(execute.call_args.args[0][-1],'300')

    def test_launcher_wont_resume_an_existing_ledger(self):
        with patch.object(pipeline.subprocess,'run') as execute:
            with self.assertRaises(ValueError): pipeline.run_pair(self.f.mut,['1'])
            execute.assert_not_called()

    def test_launcher_interrupt_is_recorded_and_stops(self):
        (self.f.mut / 'runs.tsv').unlink()
        with patch.object(pipeline,'harness_process',side_effect=KeyboardInterrupt) as execute, patch.object(c,'EXP',self.f.root / 'future-experiment'):
            with self.assertRaises(ValueError): pipeline.run_pair(self.f.mut,['2','3'])
        self.assertEqual(execute.call_count,1)
        row=c.ledger(self.f.mut / 'runs.tsv')[0]
        self.assertEqual((row['seed'],row['harness_exit'],row['status']),('2','130','INTERRUPTED'))


class SummaryTests(FixtureCase):

    def prepare_analysis(self):
        pipeline.analyse_pair(self.f.mut)
        return summary.summarise([self.f.mut])

    def test_own_checker_analysis_and_summary_end_to_end(self):
        rows = self.prepare_analysis()
        self.assertEqual(len(rows),2)
        for row in rows:
            self.assertEqual(row['analysis_status'],'COMPLETE',row)
            self.assertEqual(row['mutated_NEW'],2)  # SERVER_ERROR plus undocumented 500.
            self.assertTrue(row['expected_signal_observed'])
            self.assertEqual(row['triage_status'],'NOT_APPLICABLE_P001_CLI')
            self.assertEqual(row['triage_L1_NEW_mutated'],'')
            self.assertEqual(json.loads(row['fresh_L1_NEW_mutated']),{'NEEDS_MANUAL':2})
        self.assertEqual(c.load(self.f.mut / 'analysis-s1-sut/analysis.json')['reject_statuses'],'400,406,422')

    def test_completed_seed_is_analysed_when_a_later_seed_failed(self):
        rows = c.ledger(self.f.mut / 'runs.tsv')
        rows.append({'seed':'2','role':'control','run_dir':str(self.f.root / 'not-complete'),'harness_exit':'7','status':'FAILED'})
        pipeline.write_ledger(self.f.mut / 'runs.tsv',rows)
        result=self.prepare_analysis()
        self.assertEqual(len(result),4)
        self.assertTrue(all(r['analysis_status']=='COMPLETE' for r in result if r['seed']==1))
        self.assertTrue(all(r['validation_status']=='FAIL' and r['mutated_NEW']=='' for r in result if r['seed']==2))

    def test_planned_unattempted_seeds_are_error_rows_not_zeros(self):
        self.prepare_analysis()
        dump(self.f.mut / 'run-plan.json',{'seeds':[1,2,3],'manifest_sha256':c.sha(self.f.mut / 'manifest.json')})
        rows=summary.summarise([self.f.mut])
        self.assertEqual(len(rows),6)
        self.assertTrue(all(r['error'] and r['mutated_NEW']=='' for r in rows if r['seed'] in (2,3)))

    def test_exclusion_filters_both_roles_before_attribution_and_summary(self):
        self.add_other_operation()
        PairValidationTests.set_junit(self,'control',[('GET /other','Schema Error')])
        for role,run in self.f.paths.items():
            record=json.loads((run / 'exchanges.jsonl').read_text());record['request']['path']='/other';record['request']['url']='http://sut-market:8080/other'
            record['response']['status']=500
            with (run / 'exchanges.jsonl').open('a') as stream:stream.write(json.dumps(record)+'\n')
            self.f.rehash_run(role)
        rows=self.prepare_analysis()
        self.assertTrue(all(r['validation_status']=='PASS_WITH_EXCLUSION' and r['non_mutated_NEW']==0 and r['mutated_NEW']==2 for r in rows))
        out=self.f.mut / 'analysis-s1-default'
        self.assertTrue(any(v['template']=='/other' for v in summary.violations(out / 'control.raw.violations.jsonl')))
        self.assertFalse(any(v['template']=='/other' for v in summary.violations(out / 'control.violations.jsonl')))
        self.assertTrue(json.loads(rows[0]['excluded_ops']))

    def test_old_empty_exclusion_reports_and_prior_pipeline_are_recomputed(self):
        self.prepare_analysis();report_path=self.f.mut / 'pair-validation-s1.json'
        report=c.load(report_path);report.pop('excluded_ops');dump(report_path,report)
        for oracle in ('default','sut'):
            p=self.f.mut / f'analysis-s1-{oracle}/analysis.json';record=c.load(p)
            record.pop('excluded_ops');record.pop('validation_status');record['pair_validation_sha256']=c.sha(report_path)
            record['pipeline_sha256'][str(HERE / 'summarise_e5.py')]='0'*64;dump(p,record)
        rows=summary.summarise([self.f.mut])
        self.assertTrue(all(r['analysis_status']=='COMPLETE' and r['pipeline_snapshot_status']=='PRIOR_SNAPSHOT_CURRENT_CHECKER_RECOMPUTED' for r in rows),rows)

    def test_drift_is_reported_and_current_checker_metrics_are_recomputed(self):
        before=self.prepare_analysis()
        self.assertTrue(all(r['analysis_tools_drift']=='none' and r['analysis_harness_drift']=='none' for r in before))
        path=self.f.tools/'conformance.py'
        source=path.read_text()
        self.assertIn('if status >= 500:',source)
        path.write_text(source.replace('if status >= 500:', 'if status >= 599:'))
        (self.f.tools/'new_analysis_tool.py').write_text('# Added after collection\n')
        (self.f.harness/'new_harness.txt').write_text('Added after collection\n')
        saved={p:c.sha(p) for p in self.f.mut.glob('analysis-s*/*') if p.is_file()}
        rows=summary.summarise([self.f.mut])
        self.assertTrue(all(r['analysis_status']=='COMPLETE' and r['validation_status']=='PASS' for r in rows),rows)
        self.assertTrue(all(r['analysis_tools_drift']=='changed' and r['analysis_harness_drift']=='changed' for r in rows))
        self.assertTrue(all(r['mutated_NEW']==1 and r['expected_signal_observed'] is False for r in rows),rows)
        self.assertNotEqual(rows[0]['analysis_tool_sha256'],before[0]['analysis_tool_sha256'])
        self.assertEqual(rows[0]['runtime_snapshot_sha256'],before[0]['runtime_snapshot_sha256'])
        self.assertEqual(saved,{p:c.sha(p) for p in saved})

    def test_pipeline_records_analysis_time_tools_after_collection_drift(self):
        path=self.f.tools/'conformance.py';path.write_text(path.read_text()+'\n# Analysis-time revision\n')
        rows=self.prepare_analysis()
        record=c.load(self.f.mut/'analysis-s1-default/analysis.json')
        self.assertEqual(record['tool_sha256'],c.tool_inventory())
        self.assertTrue(all(r['analysis_tools_drift']=='changed' and r['analysis_status']=='COMPLETE' for r in rows))

    def test_attribution_revision_can_change_current_output_schema(self):
        self.prepare_analysis()
        path=self.f.tools/'attribute.py'
        with path.open('a') as stream:
            stream.write('\n_previous_attribute = attribute\n'
                         'def attribute(*args, **kwargs):\n'
                         '    rows = _previous_attribute(*args, **kwargs)\n'
                         '    for row in rows: row["analysis_revision"] = "new"\n'
                         '    return rows\n')
        rows=summary.summarise([self.f.mut])
        self.assertTrue(all(r['analysis_status']=='COMPLETE' and r['mutated_NEW']==2 and
                            r['analysis_tools_drift']=='changed' for r in rows),rows)

    def test_tool_change_during_summary_fails(self):
        self.prepare_analysis()
        identity=summary.analysis_identity()
        with patch.object(summary,'analysis_identity',side_effect=[identity,dict(identity,tools={})]):
            with self.assertRaisesRegex(ValueError,'changed during summary'):summary.summarise([self.f.mut])

    def test_unexecuted_harness_change_during_summary_keeps_initial_identity(self):
        self.prepare_analysis()
        identity=summary.analysis_identity()
        with patch.object(summary,'analysis_identity',side_effect=[identity,dict(identity,harness={'later':'0'*64})]):
            rows=summary.summarise([self.f.mut])
        self.assertTrue(all(r['analysis_status']=='COMPLETE' and r['analysis_harness_drift']=='none' and
                            r['analysis_harness_sha256']==c.canonical(identity['harness']) for r in rows))

    def test_prior_pipeline_exception_does_not_allow_unreviewed_code_changes(self):
        self.prepare_analysis();p=self.f.mut / 'analysis-s1-default/analysis.json';record=c.load(p)
        record['pipeline_sha256'][str(HERE / 'codemut.py')]='0'*64;dump(p,record)
        self.assertEqual(summary.summarise([self.f.mut])[0]['analysis_status'],'FAIL')

    def test_summary_refuses_stale_validation(self):
        self.prepare_analysis(); self.f.change_meta('mutant','complete',False)
        rows = summary.summarise([self.f.mut])
        self.assertTrue(all(x['validation_status']=='FAIL' and x['mutated_NEW']=='' for x in rows))

    def test_summary_refuses_changed_attribution_csv(self):
        self.prepare_analysis()
        p = self.f.mut / 'analysis-s1-default/attribution.csv'; p.write_text('fabricated\n')
        rows = summary.summarise([self.f.mut]); self.assertEqual(rows[0]['analysis_status'],'FAIL')
        self.assertEqual(rows[0]['mutated_NEW'],'')

    def test_summary_detects_recomputed_hash_on_fabricated_labels(self):
        self.prepare_analysis(); out = self.f.mut / 'analysis-s1-default'
        p = out / 'attribution.csv'; p.write_text(p.read_text().replace('NEEDS_MANUAL','IMPL'))
        record = c.load(out / 'analysis.json'); record['file_sha256']['attribution.csv'] = c.sha(p); dump(out / 'analysis.json',record)
        self.assertEqual(summary.summarise([self.f.mut])[0]['analysis_status'],'FAIL')

    def test_failed_or_unpaired_seed_is_retained_as_error_rows(self):
        p = self.f.mut / 'runs.tsv'; rows = c.ledger(p); rows = rows[:1]; rows[0]['status']='FAILED'; rows[0]['harness_exit']='1'
        pipeline.write_ledger(p,rows)
        result = summary.summarise([self.f.mut]); self.assertEqual(len(result),2)
        self.assertTrue(all(x['error'] and x['mutated_NEW']=='' for x in result))

    def test_missing_analysis_is_not_a_zero(self):
        c.atomic_json(self.f.mut / 'pair-validation-s1.json',self.f.validate())
        rows = summary.summarise([self.f.mut]); self.assertTrue(all(x['analysis_status']=='FAIL' and x['mutated_NEW']=='' for x in rows))

    def test_analysis_refuses_existing_output(self):
        self.prepare_analysis()
        with self.assertRaises(ValueError): pipeline.analyse_pair(self.f.mut)

    def test_corrupt_jsonl_fails_even_with_recomputed_output_digest(self):
        self.prepare_analysis(); out = self.f.mut / 'analysis-s1-default'
        p = out / 'mutant.violations.jsonl'; p.write_text('{corrupt}\n')
        record = c.load(out / 'analysis.json'); record['file_sha256'][p.name] = c.sha(p); dump(out / 'analysis.json',record)
        self.assertEqual(summary.summarise([self.f.mut])[0]['analysis_status'],'FAIL')


class MetricTests(unittest.TestCase):
    def setUp(self):
        self.m = {'expected_conformance_signal':['SERVER_ERROR'],'operations':[{'method':'get','path':'/things'}]}

    def row(self,index,status,before,after,mapped=True,kind='SERVER_ERROR'):
        return {'fingerprint':str(index),'method':'GET','template':'/things' if mapped else '/other',
                'status':status,'baseline_occurrences':str(before),'mutated_occurrences':str(after),
                'op_mutated':str(mapped),'mode':'fresh','kind':kind,'label_L1':'NEEDS_MANUAL' if mapped else 'UNEXPLAINED'}

    def test_all_eight_metrics_are_separate_and_do_not_double_count(self):
        rows=[]
        for mapped in (True,False):
            for status,a,b in [('NEW',0,3),('VANISHED',4,0),('PERSISTENT',2,5),('PERSISTENT',5,2),('PERSISTENT',3,3)]:
                rows.append(self.row(len(rows),status,a,b,mapped))
        r=summary.metrics(rows,self.m)
        for key in summary.METRICS: self.assertEqual(r[key],1,key)
        self.assertEqual(r['expected_signal_NEW'],1); self.assertEqual(r['expected_signal_INCREASED'],1)

    def test_persistent_unchanged_signal_is_present_but_not_newly_observed(self):
        r=summary.metrics([self.row(1,'PERSISTENT',3,3)],self.m)
        self.assertTrue(r['expected_signal_present_mutant']); self.assertFalse(r['expected_signal_observed'])

    def test_non_mutated_signal_is_noise_not_expected_signal_observed(self):
        r=summary.metrics([self.row(1,'NEW',0,2,False)],self.m)
        self.assertFalse(r['expected_signal_observed']); self.assertEqual(r['non_mutated_NEW'],1)

    def test_increased_signal_can_be_observed_without_new_fingerprint(self):
        r=summary.metrics([self.row(1,'PERSISTENT',1,4)],self.m)
        self.assertTrue(r['expected_signal_observed']); self.assertEqual(r['mutated_NEW'],0)

    def test_excluded_ops_never_enter_either_metric_scope(self):
        rows=[self.row(1,'NEW',0,3),self.row(2,'NEW',0,2,False)]
        result=summary.metrics(rows,self.m,{('GET','/things'),('GET','/other')})
        self.assertTrue(all(result[k]==0 for k in summary.METRICS))
        self.assertFalse(result['expected_signal_observed'])

    def test_empty_rows_and_empty_expectation(self):
        r=summary.metrics([],dict(self.m,expected_conformance_signal=[]))
        self.assertFalse(r['expected_signal_observed']); self.assertEqual(r['mutated_NEW'],0)

    def test_bad_counts_duplicate_fingerprint_and_mapping_are_rejected(self):
        for rows in [[self.row(1,'NEW',1,2)], [self.row(1,'NEW',0,1)]*2,
                     [dict(self.row(1,'NEW',0,1),op_mutated='False')]]:
            with self.subTest(rows=rows),self.assertRaises(ValueError): summary.metrics(rows,self.m)

    def test_default_seeds_and_invalid_selection(self):
        self.assertEqual(pipeline.seeds([]),[1,2,3]); self.assertEqual(pipeline.seeds(['0','7']),[0,7])
        for values in [['1','1'],['-1'],['01'],['x']]:
            with self.assertRaises(ValueError): pipeline.seeds(values)

    def test_empty_discovery_writes_header_only_and_no_fabricated_results(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as root:
            out=Path(root) / 'summary.csv'
            self.assertEqual(summary.main(['--root',root,'--out',str(out)]),0)
            with out.open() as stream: self.assertEqual(list(csv.DictReader(stream)),[])


if __name__ == '__main__':
    unittest.main(verbosity=2)
