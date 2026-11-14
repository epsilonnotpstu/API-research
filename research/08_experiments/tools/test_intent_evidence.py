"""Synthetic search regressions; only own Python and read-only local git run.

Run: /usr/bin/python3 -I -B 08_experiments/tools/test_intent_evidence.py
"""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intent_evidence as ie


class IntentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.spec = self.root / 'contract.json'
        self.write_spec()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def write_spec(self, path='/api/products', statuses=('200',), schema=None):
        self.spec.write_text(json.dumps({'openapi': '3.0.3', 'paths': {path: {
            'get': {'responses': {s: {'description': 'response', 'content': {
                'application/json': {'schema': schema or {}}}} for s in statuses}}}}}))

    def handler(self, framework='spring', status=418, extra=''):
        if framework == 'spring':
            return self.put('src/main/C.java', f'''@RequestMapping("/api")
public class C {{
 {extra}
 @GetMapping("/products")
 public Object products() {{ return ResponseEntity.status({status}).build(); }}
}}''')
        return self.put('src/main/C.java', f'''@Path("/api")
public class C {{
 {extra}
 @GET @Path("products")
 public Object products() {{ return Response.status({status}).build(); }}
}}''')

    def search(self, **kwargs):
        return ie.search(self.root, self.spec, 'GET', '/api/products', **kwargs)

    def hits(self, result, category):
        return [h for h in result['hits'] if h['category'] == category]

    def test_spring_class_prefix(self):
        self.handler()
        result = self.search(status=418)
        self.assertTrue(self.hits(result, 'HANDLER'))
        self.assertEqual(result['independent_evidence'], 'none_found')
        self.assertTrue(any(h.get('statuses') == [418] for h in self.hits(result, 'HANDLER')))

    def test_jaxrs_class_prefix(self):
        self.handler('jaxrs')
        result = self.search(status=418)
        self.assertTrue(self.hits(result, 'HANDLER'))
        self.assertTrue(all(not h['independent'] for h in self.hits(result, 'HANDLER')))

    def test_asserted_200_against_code_418(self):
        self.handler()
        self.put('src/test/CIT.java', 'get("/api/products").then().statusCode(200);')
        result = self.search(status=418)
        self.assertEqual(result['independent_evidence'], 'supports_spec')
        hit = self.hits(result, 'E-TEST')[0]
        self.assertEqual(hit['asserted_values'], [200])
        self.assertEqual(hit['code_agreement'], ['contradicts'])
        self.assertEqual(hit['spec_agreement'], ['agrees'])

    def test_html_template_documentation(self):
        self.handler()
        self.put('src/main/resources/templates/rest.html',
                 '<h2>GET /api/products</h2>\n<table><tr><td>200</td><td>OK</td></tr></table>')
        result = self.search(status=418)
        self.assertEqual(result['independent_evidence'], 'supports_spec')
        self.assertTrue(self.hits(result, 'E-DOC'))

    def test_two_exception_classes_406(self):
        self.handler(status=406)
        # The route handler is not counted as a third mapper in this fixture.
        (self.root / 'src/main/C.java').unlink()
        self.put('A.java', 'class BadInputExceptionMapper { Object map() { return Response.status(406); } }')
        self.put('B.java', 'class MissingInputExceptionMapper { Object map() { return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE); } }')
        result = self.search(status=406)
        self.assertEqual(result['independent_evidence'], 'supports_code')
        self.assertEqual({h['independent_sites'] for h in self.hits(result, 'E-CONSIST')}, {2})

    def test_write_only_is_only_context(self):
        self.handler(extra='')
        self.put('src/main/C.java', '''@Path("/api") class C {
@GET @Path("products") public Product products() { return null; }
}''')
        self.put('Product.java', '''class Product {
@JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
private String name;
}''')
        self.write_spec(schema={'type': 'object', 'required': ['name'], 'properties': {'name': {'type': 'string'}}})
        result = self.search(field='name')
        self.assertEqual(result['code_field_behavior'], ['absent'])
        self.assertEqual(result['independent_evidence'], 'none_found')
        self.assertEqual(result['evidence_types_found'], [])

    def test_no_git_repo_explicit_unavailable(self):
        self.handler()
        self.assertEqual(self.search()['history']['availability'], 'unavailable')

    def test_conflicting_independent_sources(self):
        self.handler()
        self.put('tests/test_http.py', 'get("/api/products").statusCode(200)')
        self.put('README.md', 'GET /api/products returns 418')
        self.assertEqual(self.search(status=418)['independent_evidence'], 'conflicting')

    def test_field_mention_does_not_become_assertion(self):
        self.handler()
        self.put('docs/api.md', 'GET /api/products\nname is a request parameter')
        self.assertEqual(self.search(field='name')['independent_evidence'], 'none_found')

    def test_unrelated_path_test_does_not_count(self):
        self.handler()
        self.put('tests/test_http.py', 'get("/api/orders").statusCode(200)')
        self.assertFalse(self.hits(self.search(status=418), 'E-TEST'))

    def test_path_segments_and_mockmvc_assertions(self):
        self.handler()
        self.put('tests/CTest.java', 'get(BASE + "/api" + "/products")\n.andExpect(status().isOk());')
        self.assertEqual(self.search(status=418)['independent_evidence'], 'supports_spec')

    def test_input_spec_never_counts_as_doc(self):
        self.handler()
        self.spec = self.root / 'spec.md'
        self.write_spec()
        self.assertEqual(self.search(status=418)['independent_evidence'], 'none_found')

    def test_skip_build_binary_and_symlink(self):
        self.handler()
        self.put('target/docs.md', 'GET /api/products returns 200')
        self.put('node_modules/a.md', 'GET /api/products returns 200')
        self.put('docs/binary.md', 'GET /api/products\x00200')
        self.put('outside.md', 'no relevant documentation')
        (self.root / 'alias.md').symlink_to(self.root / 'outside.md')
        result = self.search(status=418)
        self.assertEqual(result['independent_evidence'], 'none_found')
        self.assertEqual(result['scan']['skipped_dirs'], 2)
        self.assertEqual(result['scan']['skipped_binary_or_encoding'], 1)
        self.assertEqual(result['scan']['skipped_symlink'], 1)

    def test_javadoc_and_openapi_annotations(self):
        self.handler(extra='/** GET /api/products returns 200. */\n@ApiResponse(code = 200, message = "OK")')
        result = self.search(status=418)
        self.assertEqual(result['independent_evidence'], 'supports_spec')
        self.assertGreaterEqual(len(self.hits(result, 'E-DOC')), 2)

    def test_verb_mismatch_does_not_find_handler(self):
        self.handler()
        result = ie.search(self.root, self.spec, 'GET', '/api/products')
        self.assertTrue(self.hits(result, 'HANDLER'))
        self.put('src/main/C.java', '@RequestMapping("/api") class C { @PostMapping("/products") public Object x() { return null; } }')
        self.assertFalse(self.hits(self.search(), 'HANDLER'))

    def test_requestmapping_arrays_constants_and_templates(self):
        self.put('C.java', '''@RequestMapping(path = {"/api", "/other"}) class C {
static final String ROUTE = "/products/{productId}";
@RequestMapping(value = ROUTE, method = {RequestMethod.GET, RequestMethod.POST})
public Object x() { return ResponseEntity.status(418).build(); }
}''')
        self.write_spec('/api/products/{id}')
        result = ie.search(self.root, self.spec, 'GET', '/api/products/{id}', status=418)
        self.assertTrue(self.hits(result, 'HANDLER'))

    def test_doc_window_is_bounded(self):
        self.handler()
        self.put('README.md', 'GET /api/products\n' + 'unrelated\n' * 11 + '200 OK\n')
        self.assertEqual(self.search(status=418)['independent_evidence'], 'none_found')

    def test_one_class_is_not_two_sites(self):
        self.put('A.java', '''class ValidationExceptionMapper {
Object a() { return Response.status(406); }
Object b() { return Response.status(406); }
}''')
        self.assertFalse(self.hits(self.search(status=406), 'E-CONSIST'))

    def test_arbitrary_numeric_literals_not_policy(self):
        self.put('A.java', 'class A { int limit = 406; }')
        self.put('B.java', 'class B { int limit = 406; }')
        self.assertEqual(self.search(status=406)['independent_evidence'], 'none_found')

    def test_deterministic_order_and_snippet_limit(self):
        self.handler()
        self.put('z.md', 'GET /api/products returns 200 ' + 'a' * 200)
        self.put('a.md', 'GET /api/products returns 418')
        first = self.search(status=418)
        self.assertEqual(first, self.search(status=418))
        self.assertTrue(all(len(h['snippet']) <= 160 for h in first['hits']))
        categories = [ie.CATEGORIES.index(h['category']) for h in first['hits']]
        self.assertEqual(categories, sorted(categories))

    def test_yaml_subset_and_rejection(self):
        self.handler()
        self.spec = self.put('spec.yaml', '''openapi: 3.0.3
paths:
  /api/products:
    get:
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                required:
                  - name
                properties:
                  name:
                    type: string
''')
        self.put('README.md', 'GET /api/products returns 200')
        result = self.search(status=418, field='name')
        self.assertEqual(result['spec']['field_policy'], ['present'])
        self.assertEqual(result['independent_evidence'], 'supports_spec')
        self.spec.write_text('paths: &p {}')
        with self.assertRaises(ValueError):
            self.search()

    def test_cli_json_and_human_output(self):
        self.handler()
        args = [str(self.root), str(self.spec), '--method', 'GET', '--path', '/api/products', '--status', '418']
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(ie.main(args + ['--json']), 0)
        self.assertEqual(json.loads(output.getvalue())['independent_evidence'], 'none_found')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(ie.main(args), 0)
        self.assertIn('E-HISTORY:', output.getvalue())

    def test_git_pickaxe_is_local_readonly_and_handler_scoped(self):
        self.handler()
        commands = []
        def git(cmd, **kwargs):
            commands.append(cmd)
            output = 'true\n' if 'rev-parse' in cmd else 'abc123 update response\n'
            return subprocess.CompletedProcess(cmd, 0, output, '')
        with patch.object(ie.subprocess, 'run', side_effect=git):
            result = self.search(status=418)
        self.assertEqual(result['history']['availability'], 'available')
        self.assertTrue(self.hits(result, 'E-HISTORY'))
        self.assertEqual(result['independent_evidence'], 'none_found')
        log = next(c for c in commands if 'log' in c)
        self.assertIn('-S418', log)
        self.assertEqual(log[-2:], ['--', 'src/main/C.java'])
        self.assertFalse(any('fetch' in c for c in commands))

    def test_deadline_marks_partial(self):
        self.handler()
        result = self.search(budget=-1)
        self.assertFalse(result['scan']['complete'])
        self.assertEqual(result['history']['availability'], 'unavailable')

    def test_numeric_response_status_annotation(self):
        self.handler(extra='@ResponseStatus(code = 418)')
        result = self.search(status=418)
        self.assertTrue(any('@ResponseStatus' in h['snippet'] and h.get('statuses') == [418]
                            for h in self.hits(result, 'HANDLER')))

    def test_field_assertion_can_contradict_serialization(self):
        self.put('C.java', '''@Path("/api") class C {
@GET @Path("products") public Product products() { return null; }
}''')
        self.put('Product.java', 'class Product { @JsonProperty(access=JsonProperty.Access.WRITE_ONLY) String name; }')
        self.write_spec(schema={'type': 'object', 'required': ['name'], 'properties': {'name': {'type': 'string'}}})
        self.put('src/test/CTest.java', 'get("/api/products").andExpect(jsonPath("$.name").exists());')
        self.assertEqual(self.search(field='name')['independent_evidence'], 'supports_spec')

    def test_field_annotation_pattern_two_dtos(self):
        self.put('C.java', '''@Path("/api") class C {
@GET @Path("products") public Product products() { return null; }
}''')
        self.put('Product.java', 'class Product { @JsonProperty(access=JsonProperty.Access.WRITE_ONLY) String name; }')
        self.put('Other.java', 'class Other { @JsonProperty(access=JsonProperty.Access.WRITE_ONLY) String name; }')
        result = self.search(field='name')
        self.assertEqual(result['independent_evidence'], 'supports_code')
        self.assertEqual({h['independent_sites'] for h in self.hits(result, 'E-CONSIST')}, {2})

    def test_comments_do_not_assert_test_status(self):
        self.handler()
        self.put('src/test/CTest.java', '// get("/api/products").statusCode(200);\nclass CTest {}')
        self.assertEqual(self.search(status=418)['independent_evidence'], 'none_found')

    def test_nested_class_is_not_independent_duplicate(self):
        self.put('A.java', '''class OuterExceptionMapper {
static class InnerExceptionMapper {
Object map() { return Response.status(406); }
}
}''')
        self.assertFalse(self.hits(self.search(status=406), 'E-CONSIST'))

    def test_default_response_does_not_assert_specific_status(self):
        self.handler()
        self.write_spec(statuses=('default',))
        self.put('README.md', 'GET /api/products returns 200')
        result = self.search(status=418)
        self.assertEqual(result['independent_evidence'], 'none_found')
        self.assertEqual(self.hits(result, 'E-DOC')[0]['spec_agreement'], ['unknown'])

    def test_httpurlconnection_and_assertj_status(self):
        self.handler()
        self.put('src/test/CIntegrationTest.java', '''createRequest("products", "api");
assertThat(response.getStatus()).isEqualTo(HttpURLConnection.HTTP_OK);
assertThat(response.getStatus()).isEqualTo(200);''')
        result = self.search(status=418)
        self.assertEqual(result['independent_evidence'], 'supports_spec')
        self.assertEqual(len(self.hits(result, 'E-TEST')), 2)

    def test_html_dimension_and_example_price_are_not_status(self):
        self.handler()
        self.put('templates/api.html', '<h1>GET /api/products</h1>\n<th width="200">name</th>\n<pre>{"price": 400}</pre>')
        self.assertEqual(self.search(status=418)['independent_evidence'], 'none_found')


if __name__ == '__main__':
    unittest.main()
