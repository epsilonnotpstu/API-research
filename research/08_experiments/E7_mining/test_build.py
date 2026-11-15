#!/usr/bin/python3
"""Only artificial Git objects are written; upstream clones remain read-only."""
import csv
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

B=runpy.run_path(str(Path(__file__).with_name('build.py')))
M=runpy.run_path(str(Path(__file__).with_name('mine.py')))
HERE=Path(__file__).resolve().parent

class ArtificialRepo:
    def __init__(self,path):
        self.path=Path(path);self.env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,
            GIT_AUTHOR_NAME='Synthetic',GIT_AUTHOR_EMAIL='synthetic@example.invalid',
            GIT_COMMITTER_NAME='Synthetic',GIT_COMMITTER_EMAIL='synthetic@example.invalid',
            GIT_AUTHOR_DATE='2001-01-01T00:00:00Z',GIT_COMMITTER_DATE='2001-01-01T00:00:00Z')
        subprocess.run(['git','init','--bare','-q',str(path)],check=True,env=self.env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def run(self,*args,data=None):
        return subprocess.run(['git','-c','core.hooksPath=/dev/null','--git-dir='+str(self.path),*args],input=data,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,env=self.env).stdout.decode().strip()
    def revision(self,files,parent=None,message='synthetic message never included'):
        entries=[]
        for path,text in sorted(files.items()):
            oid=self.run('hash-object','-w','--stdin',data=text.encode())
            entries.append('100644 blob '+oid+'\t'+path+'\n')
        tree=self.run('mktree',data=''.join(entries).encode())
        commit=self.run('commit-tree',tree,*(['-p',parent] if parent else []),data=(message+'\n').encode())
        self.run('update-ref','refs/heads/main',commit)
        return commit

def row(i,parent,child,impl,route=(),helpers=()):
    return dict(item_id=i,set='new',repo='synthetic',stars=0,fix_commit=child,parent_commit=parent,date='2001-01-01',operation='GET /a',
        proposition='GET /a: contract says red; implementation does blue',truth_direction='IMPL',confidence=3,contract_kind='spec_file',
        mismatch_type='color',fix_family=i,message_excerpt='unique synthetic message '+i,
        proposition_check=json.dumps({'contract':[parent+':api.yaml:1'],'implementation':[parent+':'+impl+':1'],'route':[parent+':'+p+':1' for p in route]}),helper_paths=list(helpers))

SPEC='openapi: 3.0.3\ninfo: {title: Artificial, version: v}\npaths:\n  /a:\n    get:\n      responses:\n        "200":\n          description: red\n'

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='.test-',dir=HERE)
        self.folder=Path(self.temporary.name);self.repo=ArtificialRepo(self.folder/'fixture.git')
        self.initial={'api.yaml':SPEC,'A.java':'class A { String value = "PARENT_ONLY"; }\n','B.java':'class B {}\n','Helper.java':'class Helper { String value = "BEFORE_HELPER"; }\n'}
        self.parent=self.repo.revision(self.initial)
        after=dict(self.initial,**{'A.java':'class A { String value = "CHILD_ONLY"; }\n','Helper.java':'class Helper { String value = "AFTER_HELPER"; }\n'})
        self.child=self.repo.revision(after,self.parent,'unique synthetic message a')
        later=dict(after,**{'B.java':'class B { int number = 1; }\n'})
        self.last=self.repo.revision(later,self.child,'unique synthetic message b')
        self.a=row('a',self.parent,self.child,'A.java')
        self.b=row('b',self.child,self.last,'B.java',helpers=['Helper.java'])
    def tearDown(self):self.temporary.cleanup()
    def prepare(self,rows):return B['prepare'](rows,{'synthetic':self.repo.path},'synthetic salt')
    def test_determinism_and_parent_only(self):
        first=self.prepare([self.a,self.b]);second=self.prepare([self.b,self.a])
        self.assertEqual(first[:3],second[:3])
        files,key,log,rows=first
        a=next(r['item_id'] for r in rows if r['fix_family']=='a')
        self.assertIn(b'PARENT_ONLY',files[a+'/impl/A.java'])
        self.assertNotIn(b'CHILD_ONLY',files[a+'/impl/A.java'])
        for data in files.values():
            self.assertNotIn(b'unique synthetic message',data)
            self.assertNotIn(self.child.encode(),data)
            self.assertNotIn(b'2001-01-01',data)
        self.assertTrue(all(log['assertions'].values()))
    def test_cross_item_excludes_optional_and_flags_key(self):
        files,key,log,rows=self.prepare([self.a,self.b])
        b=next(r for r in rows if r['fix_family']=='b')
        self.assertEqual('true',b['cross_item_flag'])
        self.assertNotIn(b['item_id']+'/impl/Helper.java',files)
        self.assertEqual(['Helper.java'],log['cross_item_pairs'][0]['excluded'])
    def test_cross_item_own_locator_is_retained(self):
        self.b['proposition_check']=json.dumps({'contract':[self.child+':api.yaml:1'],'implementation':[self.child+':B.java:1'],'route':[self.child+':Helper.java:1']})
        files,key,log,rows=self.prepare([self.a,self.b]);b=next(r for r in rows if r['fix_family']=='b')
        self.assertEqual('true',b['cross_item_flag'])
        self.assertIn(b['item_id']+'/impl/Helper.java',files)
        self.assertEqual(['Helper.java'],log['cross_item_pairs'][0]['retained_own_locators'])
    def test_forbidden_words(self):
        for word in 'fix fixed commit later changed mined repair direction E6 E7 T42 T43 T45'.split():
            r=dict(self.a,proposition='GET /a: contract says '+word.upper()+'; implementation does blue')
            with self.assertRaises(B['O']['BuildError']):self.prepare([r])
        self.assertIsNone(B['FORBIDDEN'].search('prefix fixes fixedly directional'))
    def test_refuse_overwrite(self):
        files,key,log,_=self.prepare([self.a]);out=self.folder/'output';kd=self.folder/'key';kd.mkdir()
        B['publish'](files,key,log,out,kd)
        before=(out/'items.csv').read_bytes()
        with self.assertRaises(B['O']['BuildError']):B['publish'](files,key,log,out,kd)
        self.assertEqual(before,(out/'items.csv').read_bytes())
        self.assertFalse((kd/'accepted_full.csv').exists())
    def test_parent_locator_enforced(self):
        r=dict(self.a,proposition_check=json.dumps({'contract':[self.child+':api.yaml:1'],'implementation':[self.parent+':A.java:1']}))
        with self.assertRaises(B['O']['BuildError']):self.prepare([r])
    def test_annotation_file_serves_both_directories(self):
        r=dict(self.a,contract_kind='annotations',proposition_check=json.dumps({'contract':[self.parent+':A.java:1'],'implementation':[self.parent+':A.java:1']}))
        files,_,_,rows=self.prepare([r]);iid=rows[0]['item_id']
        self.assertEqual(files[iid+'/contract/A.java'],files[iid+'/impl/A.java'])
        self.assertEqual(self.initial['A.java'].encode(),files[iid+'/impl/A.java'])
    def test_privacy_redaction_and_fixture_values(self):
        text=b'// Signed-off-by: Synthetic <synthetic@example.invalid>\nclass A { String password = "artificial-credential"; }\n// 2001-01-01\n'
        data=B['sanitize'](text,'A.java',{b'artificial-credential'})
        self.assertEqual(len(text.splitlines()),len(data.splitlines()))
        for needle in [b'Synthetic',b'@example',b'artificial-credential',b'2001-01-01']:self.assertNotIn(needle,data)
    def test_contributor_header_continuation(self):
        text=b'/*\n * Contributors:\n *     Synthetic Person - artificial attribution\n */\nclass A {}\n'
        data=B['sanitize'](text,'A.java',())
        self.assertNotIn(b'Synthetic Person',data)
        self.assertNotIn(b'Contributors:',data)
        self.assertEqual(len(text.splitlines()),len(data.splitlines()))
        self.assertIn(b' */\nclass A {}',data)
    def test_json_projection_transitive_refs(self):
        data={'openapi':'3.0.3','info':{'title':'test','version':'v'},'paths':{'/a':{'get':{'responses':{'200':{'$ref':'#/components/responses/R'}}}},'/b':{}},'components':{'responses':{'R':{'description':'red','content':{'application/json':{'schema':{'$ref':'#/components/schemas/S'}}}}},'schemas':{'S':{'type':'string'},'Unused':{'type':'integer'}}}}
        projected=json.loads(B['project_json'](json.dumps(data).encode(),'api.json','GET /a'))
        self.assertEqual({'S'},set(projected['components']['schemas']))
        self.assertEqual({'/a'},set(projected['paths']))
        self.assertEqual('api.json',projected['x-source-path'])
    def test_yaml_projection_transitive_refs(self):
        data=b'openapi: 3.0.3\ninfo: {title: Artificial, version: v}\npaths:\n  /a:\n    get:\n      responses:\n        "200":\n          $ref: "#/components/responses/R"\n  /b:\n    get: {}\ncomponents:\n  responses:\n    R:\n      description: red\n      content:\n        application/json:\n          schema:\n            $ref: "#/components/schemas/S"\n  schemas:\n    S:\n      type: string\n    Unused:\n      type: integer\n'
        projected=B['project_yaml'](data,'api.yaml','GET /a')
        self.assertNotIn(b'Unused',projected);self.assertNotIn(b'/b:',projected)
        _,nodes=B['yaml_nodes'](projected.decode())
        self.assertIn(('paths','/a','get'),nodes)
        self.assertIn(('components','schemas','S'),nodes)
    def test_multi_file_reference_closure(self):
        files=dict(self.initial,**{'root.yaml':'openapi: 3.0.3\ninfo: {title: Artificial, version: v}\npaths:\n  /a:\n    get:\n      responses:\n        "200":\n          $ref: "part.yaml#/components/responses/R"\n','part.yaml':'components:\n  responses:\n    R:\n      description: red\n      content:\n        application/json:\n          schema:\n            $ref: "other.yaml#/components/schemas/S"\n','other.yaml':'components:\n  schemas:\n    S:\n      type: string\n'})
        parent=self.repo.revision(files,self.last);r=dict(self.a,parent_commit=parent)
        selected,_=B['contract_files'](r,B['Git'](self.repo.path),{'root.yaml'})
        self.assertEqual({'root.yaml','part.yaml','other.yaml'},set(selected))
    def test_direction_neutral_ranking(self):
        score=M['rank_candidate']
        self.assertEqual(score('fix wrong response',['api/handler.go']),score('fix wrong response',['api/openapi.yaml']))
        self.assertEqual(score('fix wrong response',['api/handler.go','api/openapi.yaml']),score('fix wrong response',['api/handler.go']))
        self.assertGreater(score('align response',['api/handler.go']),score('fix response',['api/handler.go']))

if __name__=='__main__':unittest.main()
