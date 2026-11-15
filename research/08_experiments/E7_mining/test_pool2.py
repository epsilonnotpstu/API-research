#!/usr/bin/python3
"""Synthetic content filters and explicit package replacement."""
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
M=runpy.run_path(str(HERE/'mine2.py'))
B=runpy.run_path(str(HERE/'build.py'))


class Pool2Tests(unittest.TestCase):
    def test_ci_and_configuration_are_excluded(self):
        config=b'name: build\non: push\njobs: {}\n'
        for path in ['.github/workflows/api.yaml','ci/openapi.yml','helm/api.yaml','deploy/api.yaml','k8s/api.yaml','terraform/api.json','docker/api.yml','server/src/main/resources/application.yaml']:
            self.assertEqual([],M['classify'](path,[config]),path)
        self.assertEqual([],M['classify']('.github/workflows/openapi.yml',[b'openapi: 3.0.3\n']))

    def test_openapi_file_is_included_at_either_version(self):
        for raw in [b'openapi: 3.0.3\npaths: {}\n',b'{"swagger":"2.0","paths":{}}']:
            for versions in [[raw,b'other: value\n'],[b'other: value\n',raw]]:
                self.assertIn('openapi_root',M['classify']('docs/reference/service.yaml',versions))
        self.assertFalse(M['openapi'](b'config:\n  openapi: enabled\n'))
        self.assertFalse(M['openapi'](b'{"config":{"openapi":true}}'))

    def test_annotations_and_production_behaviour(self):
        source=b'import io.swagger.v3.oas.annotations.Operation;\n@Operation(summary="read") class API {}'
        self.assertIn('contract_annotations',M['classify']('server/src/main/java/a/Api.java',[source]))
        self.assertIn('production_behaviour',M['classify']('server/src/main/java/a/ThingController.java',[b'class ThingController {}']))
        self.assertEqual([],M['classify']('server/src/test/java/a/ThingController.java',[source]))
        self.assertEqual([],M['classify']('client/src/main/java/a/ThingController.java',[source]))
        self.assertEqual([],M['classify']('docs/src/main/java/a/ThingController.java',[source]))
        self.assertIn('production_behaviour',M['classify']('internal/handler/api.go',[b'package handler']))
        self.assertEqual([],M['classify']('internal/httpclient/model.go',[b'package httpclient']))
        self.assertEqual([],M['classify']('pkg/client-go/model.go',[b'package client']))
        self.assertEqual([],M['classify']('utils/maven-plugin/src/main/java/a/Mojo.java',[b'import org.apache.maven.plugins.annotations.Parameter;\n@Parameter String name;']))
        self.assertEqual([],M['classify']('operator/controller/src/main/java/a/Operator.java',[b'class Operator {}']))
        self.assertFalse(M['annotated'](b'import org.springframework.web.bind.annotation.RequestBody;\n@RequestBody String body;'))

    def test_reference_closure_uses_content(self):
        function=M['reachable'];g=function.__globals__;original=g['objects']
        files={'root.yaml':b'openapi: 3.0.3\npaths:\n  /a:\n    $ref: parts/path.yaml\n','parts/path.yaml':b'$ref: ../schemas/value.json\n','schemas/value.json':b'{"type":"string"}','config.yml':b'name: build'}
        def fake(repo,names):return {n:files.get(n.split(':',1)[1]) for n in names}
        g['objects']=fake
        try:
            reached,evidence=function('synthetic','a'*40,{'root.yaml'},{'parts/path.yaml','schemas/value.json','config.yml'})
            self.assertEqual({'parts/path.yaml','schemas/value.json'},reached)
        finally:g['objects']=original

    def test_replace_is_explicit_and_logs_old_hash(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix='.test-') as folder:
            root=Path(folder);out=root/'out';key=root/'key';key.mkdir()
            def log(files):return {'package_hashes':{p:B['sha'](d) for p,d in files.items()}}
            before={'items.csv':b'old table\n'};after={'items.csv':b'new table\n','X01/impl/A.java':b'parent\n'}
            B['publish'](before,b'old key',log(before),out,key)
            old_hash=B['package_hash'](log(before)['package_hashes'])
            with self.assertRaises(B['O']['BuildError']):B['publish'](after,b'new key',log(after),out,key)
            B['publish'](after,b'new key',log(after),out,key,replace=True)
            result=json.loads((key/'build_log.json').read_text())
            self.assertEqual(old_hash,result['replacement_history'][0]['old_package_sha256'])
            self.assertTrue(result['replacement_history'][0]['explicit_replace'])
            self.assertEqual(b'new table\n',(out/'items.csv').read_bytes())

    def test_new_task_word_is_forbidden(self):
        self.assertIsNotNone(B['FORBIDDEN'].search('T46'))

    def test_contact_metadata_is_redacted_in_json(self):
        raw=b'{\n "openapi":"3.0.3",\n "info":{"title":"Artificial","contact":{"name":"Synthetic Person","url":"https://example.invalid/person"}},\n "paths":{}\n}\n'
        data=B['sanitize'](raw,'api.json',())
        self.assertNotIn(b'Synthetic Person',data)
        self.assertEqual(len(raw.splitlines()),len(data.splitlines()))
        self.assertEqual('<redacted>',json.loads(data)['info']['contact']['name'])

    def test_contact_metadata_is_redacted_in_yaml(self):
        raw=b'openapi: 3.0.3\ninfo:\n  title: Artificial\n  contact:\n    name: Synthetic Person\n    url: https://example.invalid/person\npaths: {}\n'
        data=B['sanitize'](raw,'api.yaml',())
        self.assertNotIn(b'Synthetic Person',data)
        self.assertEqual(len(raw.splitlines()),len(data.splitlines()))


if __name__=='__main__':unittest.main()
