#!/usr/bin/python3
"""T53 tests. All diagnostics are counts/IDs; source values are suppressed.

Synthetic Git objects contain only nonpersonal fixture identities. Temporary
repositories are removed after each test. No upstream identity is ever saved.
Run: /usr/bin/python3 -I -B R3_silent_breaking/mining/test_t53.py
"""
from collections import Counter
from datetime import datetime, timezone
import csv
import io
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import time
import unittest

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SCRATCH=BASE/'collab/logs/T53_scratch'
P=runpy.run_path(str(HERE/'t53_pool.py'))
S=runpy.run_path(str(HERE/'t53_sample.py'))
B=runpy.run_path(str(HERE/'t53_build.py'))
C=B['C'];V=B['V']
SOURCE='src/main/java/server/Controller.java'
OTHER='src/main/java/server/Model.java'

def timestamp(value):
    return int(datetime.fromisoformat(value.replace('Z','+00:00')).timestamp())

class Fixture:
    def __init__(self,directory):
        self.path=Path(directory)/'fixture.git'
        self.path.mkdir()
        self.run('init','--bare','--quiet')
        self.state={}
        self.head=None

    def run(self,*args,data=None):
        result=subprocess.run(['git','--git-dir='+str(self.path),*args],input=data,
                              stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=P['git_env']())
        if result.returncode:raise RuntimeError('Synthetic Git failed; details suppressed')
        return result.stdout

    def object(self,kind,raw):
        return self.run('hash-object','-w','-t',kind,'--stdin',data=raw).decode().strip()

    def tree(self,files):
        nested={}
        for path,raw in files.items():
            cursor=nested
            parts=path.split('/')
            for part in parts[:-1]:cursor=cursor.setdefault(part,{})
            cursor[parts[-1]]=raw
        def emit(node):
            entries=[]
            for name,value in sorted(node.items()):
                if isinstance(value,dict):mode='040000';kind='tree';oid=emit(value)
                else:mode='100644';kind='blob';oid=self.object('blob',value)
                entries.append(f'{mode} {kind} {oid}\t{name}\n'.encode())
            return self.run('mktree',data=b''.join(entries)).decode().strip()
        return emit(nested)

    def commit(self,changes,date='2023-01-02T00:00:00Z',bot=None,parents=None,message='fixture change',email='noreply',author_date=None):
        for path,value in changes.items():
            if value is None:self.state.pop(path,None)
            else:self.state[path]=value.encode() if isinstance(value,str) else value
        parents=([self.head] if self.head else []) if parents is None else parents
        stamp=timestamp(date)
        # Deliberately no real person or email address, including in Git objects.
        identity=bot or 'fixture'
        raw=('tree '+self.tree(self.state)+'\n'+''.join('parent '+p+'\n' for p in parents)+
             f'author {identity} <{email}> {timestamp(author_date) if author_date else stamp} +0000\ncommitter fixture <noreply> {stamp} +0000\n\n'+message+'\n').encode()
        self.head=self.object('commit',raw)
        self.run('update-ref','refs/heads/main',self.head)
        self.run('symbolic-ref','HEAD','refs/heads/main')
        return self.head

    def discover(self):return P['discover'](self.path,self.head)

class SyntheticTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='test_t53_',dir=SCRATCH)
        self.f=Fixture(self.temp.name)
        self.base=self.f.commit({SOURCE:'class Controller { int x=1; }\n',OTHER:'class Model { int x=1; }\n'},date='2022-12-31T00:00:00Z')

    def tearDown(self):self.temp.cleanup()

    def test_path_rules(self):
        for path in [SOURCE,'handlers/server.go','api/model/User.kt','server/Validator.java','src/main/java/x/ErrorMapper.java']:
            self.assertTrue(P['behaviour'](path))
        for path in ['src/test/java/server/Controller.java','examples/api/a.go','vendor/api/a.go','generated/api/a.go',
                     'api/a_test.go','sdk/api/a.go','client-go/api/a.go','migrations/api/a.go','build/api/a.go',
                     '.github/api/a.go','docs/api/a.go','cmd/api/a.go','src/main/java/x/Utilities.java','../api/a.go']:
            self.assertFalse(P['behaviour'](path))

    def test_window_is_committer_inclusive(self):
        out=self.f.commit({SOURCE:'class Controller { int x=2; }\n'},date='2022-12-31T23:59:59Z')
        inside=self.f.commit({SOURCE:'class Controller { int x=3; }\n'},date='2023-01-01T00:00:00Z')
        rows,_,_=self.f.discover()
        self.assertEqual([r['sha'] for r in rows],[inside]);self.assertNotIn(out,[r['sha'] for r in rows])

    def test_nonmonotonic_dates_do_not_truncate(self):
        first=self.f.commit({SOURCE:'class Controller { int x=2; }\n'},date='2023-01-02T00:00:00Z')
        self.f.commit({SOURCE:'class Controller { int x=3; }\n'},date='2022-01-01T00:00:00Z')
        last=self.f.commit({SOURCE:'class Controller { int x=4; }\n'},date='2023-01-03T00:00:00Z')
        rows,_,_=self.f.discover();self.assertEqual({r['sha'] for r in rows},{first,last})

    def test_author_date_does_not_define_window(self):
        selected=self.f.commit({SOURCE:'class Controller { int x=2; }\n'},author_date='2020-01-01T00:00:00Z')
        rows,_,_=self.f.discover();self.assertEqual([r['sha'] for r in rows],[selected])
        self.assertEqual(timestamp(rows[0]['date']),timestamp('2023-01-02T00:00:00Z'))

    def test_root_commit_can_be_a_candidate(self):
        self.f.head=None;self.f.state={}
        root=self.f.commit({SOURCE:'class Controller {}\n'},parents=[])
        rows,_,_=self.f.discover();self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['sha'],root);self.assertIsNone(rows[0]['parent'])

    def test_first_parent_and_nonmerge(self):
        first=self.f.commit({SOURCE:'class Controller { int x=2; }\n'})
        branch=self.f.commit({SOURCE:'class Controller { int x=3; }\n'},parents=[self.base])
        merge=self.f.commit({SOURCE:'class Controller { int x=4; }\n'},parents=[first,branch])
        last=self.f.commit({SOURCE:'class Controller { int x=5; }\n'})
        rows,_,_=self.f.discover();self.assertEqual({r['sha'] for r in rows},{first,last})
        self.assertNotIn(merge,[r['sha'] for r in rows]);self.assertNotIn(branch,[r['sha'] for r in rows])

    def test_document_root_at_parent_or_child(self):
        self.f.commit({'contract.data':'openapi: 3.0.0\npaths: {}\n'},date='2022-12-31T01:00:00Z')
        self.f.commit({SOURCE:'class Controller { int x=2; }\n','contract.data':'not_a_contract: true\n'})
        self.f.commit({SOURCE:'class Controller { int x=3; }\n','new.contract':'{"swagger":"2.0","paths":{}}'})
        rows,counts,_=self.f.discover();self.assertEqual(rows,[]);self.assertEqual(counts['contract_exclusions'],2)

    def test_reference_closure_at_parent(self):
        self.f.commit({'api/root.yaml':'openapi: 3.0.0\npaths:\n  /x:\n    $ref: part.yaml#/entry\n',
                       'api/part.yaml':'entry:\n  $ref: ../fragment.data#/entry\n','fragment.data':'entry: {}\n'},date='2022-12-31T01:00:00Z')
        self.f.commit({SOURCE:'class Controller { int x=2; }\n','fragment.data':'entry: {summary: next}\n'})
        rows,counts,_=self.f.discover();self.assertEqual(rows,[]);self.assertEqual(counts['contract_exclusions'],1)

    def test_unrelated_yaml_is_not_a_document(self):
        chosen=self.f.commit({SOURCE:'class Controller { int x=2; }\n','config.yaml':'service:\n  openapi: false\n'})
        rows,_,_=self.f.discover();self.assertEqual([r['sha'] for r in rows],[chosen])

    def test_formatting_and_rename_only_dropped(self):
        self.f.commit({SOURCE:'class Controller { int x = 1; }\n'})
        self.f.commit({SOURCE:None,'src/main/java/server/RenamedController.java':'class Controller { int x = 1; }\n'})
        rows,_,_=self.f.discover();self.assertEqual(rows,[])

    def test_formatting_file_removed_from_count(self):
        chosen=self.f.commit({SOURCE:'class Controller { int x = 1; }\n',OTHER:'class Model { int x=2; }\n'})
        rows,_,_=self.f.discover();self.assertEqual([r['sha'] for r in rows],[chosen]);self.assertEqual(rows[0]['files'],[OTHER])
        self.assertEqual(rows[0]['changed_lines'],2)

    def test_size_and_eight_file_boundaries(self):
        boundary=self.f.commit({'api/boundary.go':''.join(f'line{i}\n' for i in range(400))})
        self.f.commit({'api/oversized.go':''.join(f'line{i}\n' for i in range(401))})
        eight=self.f.commit({f'api/model{i}.go':'line\n' for i in range(8)})
        self.f.commit({f'api/other{i}.go':'line\n' for i in range(9)})
        rows,counts,_=self.f.discover();self.assertEqual({r['sha'] for r in rows},{boundary,eight})
        self.assertEqual(counts['size_exclusions'],2)

    def test_binary_and_test_only_are_excluded(self):
        self.f.commit({'api/blob.go':b'\0binary\n','api/handler_test.go':'changed\n'})
        rows,_,_=self.f.discover();self.assertEqual(rows,[])

    def test_bot_scratch_process_and_no_attribution_in_records(self):
        for index,identity in enumerate(['dependabot','renovate','github-actions','fixture[bot]']):
            self.f.commit({SOURCE:f'class Controller {{ int x={index+2}; }}\n'},bot=identity)
        self.f.commit({SOURCE:'class Controller { int x=8; }\n'},email='RENOVATE')
        normal=self.f.commit({SOURCE:'class Controller { int x=9; }\n'})
        rows,counts,docs=self.f.discover();self.assertEqual([r['sha'] for r in rows],[normal]);self.assertEqual(counts['bot_exclusions'],5)
        recorded=P['jb']([rows,counts,docs]).decode()
        self.assertFalse(re.search(r'author|committer|noreply|dependabot|renovate|github-actions|\[bot\]',recorded,re.I))

    def test_annotation_patterns(self):
        for value in ['@NotNull','@jakarta.validation.constraints.Size(max=2)','@GetMapping','@ResponseStatus','@JsonProperty',
                      '@JsonIgnore','@JsonInclude','@Schema','@Parameter','@ApiResponses','@Operation',
                      '// @Router /x [get]','// @Param x string true','// @Success 200','// @Failure 400',
                      '// @Accept json','// @Produce json','// @Security BasicAuth','// swagger:route GET /x']:
            self.assertTrue(B['annotation_touched'](('@@ -1 +1 @@\n+'+value+'\n').encode()))
        self.assertFalse(B['annotation_touched'](b'--- @NotNull\n+++ @GET\n @Schema\n+@Override\n'))

    def test_spec_updated_exact_90_day_boundary(self):
        selected=self.f.commit({SOURCE:'class Controller { int x=2; }\n'},date='2023-01-01T00:00:00Z')
        self.f.commit({'spec.yaml':'openapi: 3.0.0\npaths: {}\n'},date='2023-04-01T00:00:00Z')
        rows,_,history=self.f.discover();row=next(r for r in rows if r['sha']==selected)
        self.assertTrue(B['updated_90d'](row,history))
        late=dict(history,document_updates=[dict(history['document_updates'][0],timestamp=timestamp('2023-04-01T00:00:01Z'))])
        self.assertFalse(B['updated_90d'](row,late))
        same=dict(history,document_updates=[dict(history['document_updates'][0],timestamp=timestamp(row['date']))])
        self.assertFalse(B['updated_90d'](row,same))
        ancestor=dict(history,document_updates=[dict(history['document_updates'][0],position=0)])
        self.assertFalse(B['updated_90d'](row,ancestor))

    def test_spec_update_in_merge_counts(self):
        selected=self.f.commit({SOURCE:'class Controller { int x=2; }\n'},date='2023-01-01T00:00:00Z')
        branch=self.f.commit({'unrelated.txt':'x'},parents=[self.base],date='2023-01-02T00:00:00Z')
        self.f.commit({'spec.yaml':'swagger: "2.0"\npaths: {}\n'},parents=[selected,branch],date='2023-02-01T00:00:00Z')
        rows,_,history=self.f.discover();self.assertTrue(B['updated_90d'](rows[0],history))

    def test_synthetic_pool_determinism(self):
        self.f.commit({SOURCE:'class Controller { int x=2; }\n'})
        first=self.f.discover();second=self.f.discover()
        self.assertEqual(P['sha'](P['jb'](first)),P['sha'](P['jb'](second)))

    def test_sample_and_shuffle_determinism(self):
        pool=[dict(repo=repo,sha=f'{index:040x}') for repo in ['a','B','z'] for index in range(5)]
        chosen=S['select'](pool,['z','a','B'])
        self.assertEqual(chosen,S['select'](list(reversed(pool)),['B','a','z']))
        self.assertEqual(Counter(r['repo'] for r in chosen),{'B':3,'a':3,'z':3})
        self.assertEqual(B['shuffled'](chosen,'fixture-salt'),B['shuffled'](list(reversed(chosen)),'fixture-salt'))
        self.assertNotEqual(B['shuffled'](chosen,'fixture-salt'),B['shuffled'](chosen,'different-fixture-salt'))

    def test_privacy_redaction_and_display(self):
        person='fixture'+'@'+'example.invalid'
        encoded='Q2'+'x7'*25+'=='
        raw=('// @author '+person+'\n// Copyright 2020 fixture\n// Co-authored-by: '+person+'\n'+
             'String clientSecret = "'+'fixture-private-value'+'";\n'+
             'client.setToken("'+'fixture-private-value'+'");\n'+
             'String data = "'+encoded+'";\n'+
             '// https://github.com/fixture/fixture\n// 2023-04-01\n').encode()
        redacted=V['redact'](raw)
        for value in [person,encoded,'fixture-private-value','2023-04-01','Copyright','@author','Co-authored-by:']:
            self.assertNotIn(value.encode(),redacted)
        self.assertEqual(len(raw.splitlines()),len(redacted.splitlines()))
        self.assertEqual(V['findings'](redacted),[])
        self.assertNotIn(encoded,V['display'](raw.decode()))

    def test_structured_contact_and_sensitive_examples(self):
        raw=json.dumps({'info':{'contact':{'name':'fixture contact','email':'fixture@example.invalid','url':'https://fixture.invalid'}},
                        'properties':{'password':{'example':'fixture-sensitive','type':'string'}}}).encode()
        result=V['redact'](raw)
        value=json.loads(result);self.assertEqual(value['info']['contact']['name'],'[REDACTED]')
        self.assertNotIn(b'fixture-sensitive',result);self.assertEqual(V['findings'](result),[])

    def test_extended_leakage_redaction(self):
        message='Fixture subject (#9123)\n\nTASK-8123 and PR 7123'
        lines,ids=V['message_needles'](message)
        raw=b'Fixture subject (#9123)\nTASK-8123\nhttps://fixture.invalid/pull/7123\nabcdef1234567890\n2023-02-01\n'
        result=V['redact'](raw,messages=lines,identifiers=ids,shas=['abcdef1234567890'])
        self.assertEqual(V['findings'](result,messages=lines,identifiers=ids,shas=['abcdef1234567890']),[])
        for value in ['9123','8123','7123','abcdef','2023-02-01']:self.assertNotIn(value.encode(),result)

    def test_patch_headers_and_source_hunks(self):
        raw=b'diff --git a/a b/a\nindex 1234567..7654321 100644\n--- a/a\n+++ b/a\n@@ -1 +1 @@\n-x\n+y\n'
        result=B['strip_patch'](raw)
        self.assertNotIn(b'index ',result);self.assertIn(b'@@ -1 +1 @@',result)
        self.assertIn(b'-x\n+y\n',result)

    def test_route_mapping_sources(self):
        spring=b'@RequestMapping("/api")\nclass Controller {\n@GetMapping("/things/{id}")\nvoid read() {}\n}'
        jax=b'@Path("/api")\nclass Controller {\n@GET\n@Path("/things/{id}")\nvoid read() {}\n}'
        go=b'// @Router /api/things/{id} [get]\n// swagger:route POST /api/things add\nr.GET("/api/things", handler)\n'
        self.assertIn(('get','/api/things/{}'),C['routes']([(SOURCE,spring)]))
        self.assertIn(('get','/api/things/{}'),C['routes']([(SOURCE,jax)]))
        self.assertIn(('post','/api/things'),C['routes']([('api/a.go',go)]))

    def test_operation_projection_and_reference_closure(self):
        docs={'spec.yaml':b'openapi: 3.0.0\ninfo: {title: fixture, version: v1}\npaths:\n  /x/{id}:\n    get:\n      responses:\n        "200":\n          $ref: models.yaml#/Response\n  /other:\n    post: {responses: {}}\n',
              'models.yaml':b'Response:\n  description: fixture\n  schema:\n    $ref: "#/Model"\nModel: {type: string}\nUnrelated: {type: boolean}\n'}
        result,modes,remote=C['build'](['spec.yaml'],docs.get,{('get','/x/{}')})
        root=json.loads(result['spec.yaml']);models=json.loads(result['models.yaml'])
        self.assertEqual(set(root['paths']),{'/x/{id}'});self.assertEqual(set(models),{'Response','Model'})
        self.assertEqual(modes[0]['mode'],'mapped_operations');self.assertEqual(remote,0)

    def test_fallback_bound_is_complete_operation_prefix(self):
        source={'openapi':'3.0.0','info':{'title':'fixture','version':'v1'},'paths':{
            '/'+str(i).zfill(4):{'get':{'responses':{'200':{'description':'fixture','schema':{'type':'string'}}}}} for i in range(500)}}
        result,modes,_=C['build'](['spec.json'],lambda p:json.dumps(source).encode(),set())
        value=json.loads(result['spec.json']);self.assertLessEqual(len(result['spec.json'].splitlines()),2000)
        selected=list(value['paths']);self.assertTrue(selected);self.assertEqual(selected,sorted(source['paths'])[:len(selected)])
        self.assertEqual(modes[0]['mode'],'bounded_document_prefix')

    def test_missing_reference_is_mechanical_failure(self):
        with self.assertRaises(C['ContractError']):
            C['build'](['spec.yaml'],lambda p:b'openapi: 3.0.0\npaths: {$ref: absent.yaml}\n' if p=='spec.yaml' else None,set())

    def test_synthetic_package_separation_and_refusal(self):
        self.f.commit({SOURCE:'class Controller { int x=2; }\n'})
        rows,_,history=self.f.discover()
        result=B['prepare'](rows,'fixture-salt',{'fixture':self.f.path},{'fixture':history},b'Read the source.\n')
        files,keys,_,failures=result;self.assertEqual(failures,[]);self.assertEqual(len(keys),1)
        self.assertEqual(files['TASK_R3.md'],b'Read the source.\n')
        self.assertEqual(set(files),{'items.csv','README.md','TASK_R3.md','B001/item.md','B001/diff.patch','B001/before/'+SOURCE,'B001/after/'+SOURCE})
        self.assertEqual(set(keys[0]),set(B['KEY_COLUMNS']))
        self.assertFalse(any('key' in p.split('/') or 'salt' in p for p in files))
        self.assertFalse(any(rows[0]['sha'].encode() in raw for raw in files.values()))
        out=Path(self.temp.name)/'package';key=Path(self.temp.name)/'key';key.mkdir()
        B['publish'](result,out,key)
        self.assertTrue((out/'B001/contract').is_dir())
        with self.assertRaises(FileExistsError):B['publish'](result,out,key)

    def test_failure_has_no_substitution_and_keeps_ids(self):
        self.f.commit({SOURCE:'class Controller { int x=2; }\n'})
        rows,_,history=self.f.discover()
        missing=dict(rows[0],parent='0'*40)
        result=B['prepare'](rows+[missing],'fixture-salt',{'fixture':self.f.path},{'fixture':history},b'Read.\n')
        self.assertEqual(len(result[1]),1);self.assertEqual(len(result[3]),1)
        self.assertEqual({r['item_id'] for r in result[1]+result[3]},{'B001','B002'})

class ActualArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool=json.loads((HERE/'pool4.json').read_text())
        cls.sample=json.loads((HERE/'sample4.json').read_text())
        cls.log=json.loads((HERE/'key/r3_build_log.json').read_text())
        cls.out=BASE/'packages/r3_blind'

    def test_freezes_and_current_heads(self):
        self.assertEqual(B['freeze_guard'](),self.sample)
        freeze=json.loads((HERE/'freeze4.json').read_text())
        self.assertEqual(P['sha'](P['jb'](P['code_hashes']())),freeze['code_sha256'])
        self.assertLessEqual((HERE/'freeze4.json').stat().st_mtime_ns,(HERE/'sample4.json').stat().st_mtime_ns)
        self.assertLessEqual((HERE/'freeze4_sample.json').stat().st_mtime_ns,(self.out/'items.csv').stat().st_mtime_ns)

    def test_full_pool_rebuild_and_hash(self):
        with (HERE/'heads.tsv').open() as stream:heads=list(csv.DictReader(stream,delimiter='\t'))
        rows=[];inventory=[];history={}
        for index,pinned in enumerate(heads,1):
            repo=pinned['repo']
            discovered,counts,docs=P['discover'](P['UPSTREAM']/(repo+'.git'),pinned['head'])
            rows.extend(discovered);inventory.append(dict(repo=repo,**counts));history[repo]=docs
            print(json.dumps(dict(pool_rebuild_repo=index,repositories=len(heads))),flush=True)
        self.assertEqual(P['sha'](P['jb'](rows)),P['sha']((HERE/'pool4.json').read_bytes()))
        self.assertEqual(P['sha'](P['jb'](inventory)),P['sha']((HERE/'pool4_inventory.json').read_bytes()))
        self.assertEqual(P['sha'](P['jb'](history)),P['sha']((HERE/'key/document_history.json').read_bytes()))

    def test_sample_and_shuffle_real(self):
        with (HERE/'heads.tsv').open() as stream:repos=[r['repo'] for r in csv.DictReader(stream,delimiter='\t')]
        self.assertEqual(S['select'](list(reversed(self.pool)),list(reversed(repos))),self.sample)
        salt=(HERE/'key/r3_shuffle_salt.txt').read_text().strip()
        order=B['shuffled'](self.sample,salt)
        self.assertEqual(order,B['shuffled'](list(reversed(self.sample)),salt))
        with (HERE/'key/r3_key.csv').open() as stream:keys=list(csv.DictReader(stream))
        failures=json.loads((HERE/'key/r3_build_failures.json').read_text())
        self.assertEqual({(r['item_id'],r['repo'],r['commit']) for r in keys+failures},
                         {(f'B{i:03}',r['repo'],r['sha']) for i,r in enumerate(order,1)})
        self.assertEqual(len(keys)+len(failures),len(self.sample))

    def test_candidate_metadata_bounds(self):
        self.assertEqual(len({(r['repo'],r['sha']) for r in self.pool}),len(self.pool))
        for row in self.pool:
            self.assertGreaterEqual(timestamp(row['date']),P['START'])
            self.assertTrue(0<row['changed_lines']<=400);self.assertTrue(0<len(row['files'])<=8)
            self.assertTrue(all(P['behaviour'](p) for p in row['files']))
            self.assertEqual(set(row),{'repo','sha','parent','date','files','changed_lines','language'})

    def test_package_exact_reconstruction_and_leakage(self):
        salt=(HERE/'key/r3_shuffle_salt.txt').read_text().strip()
        result=B['prepare'](self.sample,salt,{r['repo']:P['UPSTREAM']/(r['repo']+'.git') for r in self.sample},
                            json.loads((HERE/'key/document_history.json').read_text()),(BASE/'plan/TASK_R3.md').read_bytes())
        files,keys,audits,failures=result
        actual={p.relative_to(self.out).as_posix():p.read_bytes() for p in self.out.rglob('*') if p.is_file()}
        self.assertEqual({p:P['sha'](v) for p,v in actual.items()},{p:P['sha'](v) for p,v in files.items()})
        self.assertEqual(self.log['package_hashes'],{p:P['sha'](v) for p,v in files.items()})
        self.assertEqual(B['csv_bytes'](B['KEY_COLUMNS'],keys),(HERE/'key/r3_key.csv').read_bytes())
        self.assertEqual(audits,self.log['items'])
        self.assertEqual(failures,json.loads((HERE/'key/r3_build_failures.json').read_text()))
        self.assertFalse(any(V['findings'](raw) for raw in actual.values()))
        self.assertEqual(json.loads((HERE/'annotation_patterns.json').read_text()),B['PATTERNS'])

    def test_layout_separation_and_lf(self):
        raw=(self.out/'items.csv').read_bytes();self.assertNotIn(b'\r',raw)
        items=list(csv.DictReader(io.StringIO(raw.decode())))
        self.assertEqual(list(items[0]),['item_id','repo','language','files'])
        names={p.name for p in self.out.iterdir()}
        self.assertEqual(names,{'items.csv','README.md','TASK_R3.md'}|{r['item_id'] for r in items})
        for row in items:
            path=self.out/row['item_id'];self.assertTrue((path/'contract').is_dir())
            self.assertEqual(set(p.name for p in path.iterdir()),{'item.md','diff.patch','before','after','contract'})
            self.assertEqual((path/'item.md').read_bytes(),('Repository: '+row['repo']+'\nLanguage: '+row['language']+'\nFiles:\n'+''.join('- '+p+'\n' for p in row['files'].split(';'))).encode())
            patch=(path/'diff.patch').read_bytes()
            self.assertFalse(re.search(rb'(?m)^(?:index |commit |Author:|Date:)',patch))
            audit=next(r for r in self.log['items'] if r['item_id']==row['item_id'])
            if not any(m['mode']=='mapped_operations' for m in audit['contract_mapping']):
                for contract in (path/'contract').rglob('*'):
                    if contract.is_file():self.assertLessEqual(len(contract.read_bytes().splitlines()),2000)
        salt=(HERE/'key/r3_shuffle_salt.txt').read_bytes().strip()
        self.assertFalse(any(salt in p.read_bytes() for p in self.out.rglob('*') if p.is_file()))

    def test_task_copy_byte_identical(self):
        self.assertEqual((BASE/'plan/TASK_R3.md').read_bytes(),(self.out/'TASK_R3.md').read_bytes())

def main():
    SCRATCH.mkdir(parents=True,exist_ok=True)
    suite=unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SyntheticTests))
    if '--synthetic-only' not in sys.argv:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ActualArtifactTests))
    start=time.monotonic()
    # unittest's normal failure tracebacks can contain source bytes. Suppress them.
    result=unittest.TextTestRunner(stream=io.StringIO(),verbosity=0).run(suite)
    summary=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                 failed_tests=[t.id().split('.')[-1] for t,_ in result.failures+result.errors],
                 elapsed_seconds=round(time.monotonic()-start,2),diagnostics='source and exception values suppressed',
                 synthetic_only='--synthetic-only' in sys.argv)
    destination=SCRATCH/('synthetic_test_summary.json' if summary['synthetic_only'] else 'test_summary.json')
    destination.write_bytes(P['jb'](summary))
    print(json.dumps(summary),flush=True)
    return int(not result.wasSuccessful())

if __name__=='__main__':sys.exit(main())
