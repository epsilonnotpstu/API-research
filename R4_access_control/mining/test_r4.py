#!/usr/bin/python3
"""Offline synthetic verification. All test artifacts stay in T56b_scratch.

No production advisory, repository cache, package, coder task or scorer is read.
Git's transport allow-list is set to file, and every gh invocation is mocked.
"""
from collections import Counter
import contextlib
import copy
import csv
import io
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import r4_common as common
import r4_collect as collect
import r4_resolve as resolve
import r4_pool as pool
import r4_sample as sample
import r4_build as build

SCRATCH = common.ROOT / 'collab/logs/T56b_scratch'


class Synthetic:
    def __init__(self, root):
        self.root = root
        self.work = root / 'origin'
        self.work.mkdir()
        self.command('init')
        self.command('config', 'user.name', 'PRIVATE SYNTHETIC AUTHOR')
        self.command('config', 'user.email', 'private-author@example.invalid')
        self.empty = self.commit({'src/Main.java': 'class Main { boolean allow = true; }\n'})
        self.base = self.commit({
            'api/openapi.yaml': 'openapi: 3.0.0\n' + '# padding\n' * 3100,
            'api/swagger.json': '{"swagger":"2.0"}\n',
            'api/swagger-big.yaml': 'swagger: "2.0"\n' + '# doc\n' * 20,
            'api/openapi-medium.yml': 'openapi: 3.0.0\n' + '# doc\n' * 10,
            'examples/swagger.yaml': 'swagger: "2.0"\n',
            'src/Auth.kt': '// @author PRIVATE SOURCE AUTHOR\nclass Auth\n',
            'src/server.go': 'package api\n',
            'src/test/MainTest.java': 'class MainTest {}\n',
            'test/fixture.py': 'test = True\n',
            'src/helpers_test.go': 'package api\n',
        }, self.empty)
        self.fix = self.commit({
            'src/Main.java': 'class Main { boolean allow = false; }\n',
            'src/Auth.kt': '// @author PRIVATE SOURCE AUTHOR\nclass Auth { val guard = true }\n',
            'src/test/MainTest.java': 'class MainTest { boolean checks = true; }\n',
        })
        self.annotation = self.commit({'src/Main.java': '@SecurityRequirement(name="bearer")\nclass Main {}\n'})
        self.contract = self.commit({'src/Main.java': 'class Main {}\n',
                                     'api/swagger.json': '{"swagger":"2.0","paths":{}}\n'})
        self.test_only = self.commit({'src/test/MainTest.java': 'class MainTest { int n = 2; }\n'})
        self.test_delete = self.commit({'src/Main.java': 'class Main {}\n', 'test/fixture.py': None})
        self.large = self.commit({'src/Huge.go': 'package api\n' + 'var x = true\n' * 2000})
        self.boundary = self.commit({'src/Boundary.go': 'package api\n' + '// line\n' * 1999})
        self.no_contract = self.commit({'src/Main.java': 'class Main {}\n',
                                        'api/openapi.yaml': 'openapi: 3.0.0\n'}, self.empty)
        self.rename = self.commit({'src/Main.java': None,
                                   'src/Renamed.java': 'class Main { boolean allow = true; }\n'})
        self.add_delete = self.commit({'src/Main.java': None, 'src/New.kt': 'class New\n'})
        self.cache = resolve.prepare_repo(root, 'demo/service', self.work.as_uri())
        for sha in (self.empty, self.base, self.fix, self.annotation, self.contract, self.test_only,
                    self.test_delete, self.large, self.boundary, self.no_contract,
                    self.rename, self.add_delete):
            resolve.fetch(self.cache, sha)

    def command(self, *args):
        return common.run(['git', '-C', str(self.work), *args])

    def commit(self, changes, parent=None):
        if parent is not None or hasattr(self, 'base'):
            self.command('checkout', '--detach', parent or self.base)
        for path, content in changes.items():
            target = self.work / path
            if content is None:
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding='utf-8')
        self.command('add', '--all')
        self.command('commit', '-m', 'PRIVATE COMMIT MESSAGE NEVER DELIVER THIS')
        return self.command('rev-parse', 'HEAD').strip()

    def resolution(self, sha=None, parent=None):
        return {'repo': 'demo/service', 'fix_sha': sha or self.fix,
                'parent_sha': parent or self.base}


def advisory(identifier='GHSA-0001', **overrides):
    return {'ghsa_id': identifier, 'cve_id': 'CVE-2026-12345', 'ecosystem': 'maven',
            'cwes': ['CWE-285'], 'severity': 'high', 'published_at': '2026-01-01T00:00:00Z',
            'withdrawn_at': None, 'summary': 'Synthetic access control issue',
            'description': 'Synthetic description', 'references': [],
            'source_code_location': 'https://github.com/demo/service', 'packages': ['demo'], **overrides}


class Primitives(unittest.TestCase):
    def test_contract_rule(self):
        for path in ('api/OpenAPI.YAML', 'docs/my-swagger.yml', 'openapi.json'):
            with self.subTest(path=path):
                self.assertTrue(common.is_contract_path(path))
        for path in ('openapi.txt', 'api/petstore.yaml', 'openapi.yaml/readme.md'):
            with self.subTest(path=path):
                self.assertFalse(common.is_contract_path(path))

    def test_every_excluded_segment(self):
        for segment in common.EXCLUDED:
            with self.subTest(segment=segment):
                self.assertFalse(common.is_contract_path(f'a/{segment}/openapi.json'))
                self.assertFalse(common.is_source_path(f'a/{segment}/Main.java'))

    def test_source_extensions(self):
        for path in ('src/Foo.java', 'app/Foo.kt', 'cmd/main.go'):
            self.assertTrue(common.is_source_path(path))
        for path in ('src/Foo.py', 'src/Foo.JAVA', 'src/Foo.kt.txt'):
            self.assertFalse(common.is_source_path(path))

    def test_test_paths_and_suffixes(self):
        for path in ('src/test/java/A.java', 'x/test/a.py', 'tests/a.rb', 'a_test.go',
                     'x/FooTest.java', 'FooTests.java', 'FooTest.kt', 'FooIT.java'):
            with self.subTest(path=path):
                self.assertTrue(common.is_test_path(path))
                self.assertFalse(common.is_source_path(path))
        for path in ('latest/main.go', 'testing/Main.java', 'contest.py', 'Main.java'):
            self.assertFalse(common.is_test_path(path))

    def test_annotation_hunks_only(self):
        text = ('diff --git a/X.java b/X.java\n--- a/@Operation.java\n+++ b/@Schema.java\n'
                '@@ -1,3 +1,4 @@\n-@Operation\n+@pkg.SecurityRequirement\n'
                '+@SecurityRequirements @SecurityScheme\n+// @Router /x [get]\n'
                ' @Schema\n+@SecurityRequirementExtra\n+// ordinary\n')
        self.assertEqual(common.annotation_lines(text), 4)

    def test_annotation_all_r3_names(self):
        jvm, go = common.annotation_patterns()
        self.assertTrue(jvm.search('@io.swagger.v3.oas.annotations.Operation'))
        self.assertTrue(go.search('// SWAGGER:route'))
        self.assertTrue(go.search('// @Security bearer'))
        self.assertFalse(jvm.search('@NotAContractAnnotation'))

    def test_canonical_json_and_hash(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            path = Path(directory) / 'json'
            common.write_json(path, {'z': 'বাংলা', 'a': 1})
            raw = path.read_bytes()
            self.assertTrue(raw.endswith(b'\n'))
            self.assertNotIn(b'\r', raw)
            self.assertLess(raw.index(b'"a"'), raw.index(b'"z"'))
            self.assertEqual(common.sha256_file(path), __import__('hashlib').sha256(raw).hexdigest())
            with self.assertRaises(FileExistsError):
                common.write_json(path, {})

    def test_network_retry_and_safe_error(self):
        failed = subprocess.CompletedProcess([], 1, '', 'PRIVATE VALUE HTTP 503')
        with patch.object(common.subprocess, 'run', return_value=failed) as mocked, \
                patch.object(common.time, 'sleep') as sleep:
            with self.assertRaises(common.CommandError) as error:
                common.run(['gh', 'api', '/advisories'])
            self.assertEqual(mocked.call_count, 3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [1, 2])
            self.assertNotIn('PRIVATE', str(error.exception))

    def test_fetch_retry_then_success(self):
        failed = subprocess.CompletedProcess([], 1, '', 'network error')
        success = subprocess.CompletedProcess([], 0, 'ok', '')
        with patch.object(common.subprocess, 'run', side_effect=[failed, failed, success]) as mocked, \
                patch.object(common.time, 'sleep'):
            self.assertEqual(common.run(['git', 'fetch', 'origin', 'abc']), 'ok')
            self.assertEqual(mocked.call_count, 3)

    def test_local_failure_not_retried(self):
        with patch.object(common.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', '')) as mocked:
            with self.assertRaises(common.CommandError):
                common.run(['git', 'rev-parse', '--verify', 'bad'])
            self.assertEqual(mocked.call_count, 1)

    def test_numstat_rename_and_unusual_paths(self):
        result = pool.numstat('1\t2\tsrc/a\tb.java\0' + '0\t0\t\0src/old.java\0src/new.java\0')
        self.assertEqual(result[0]['old_path'], 'src/a\tb.java')
        self.assertEqual(result[1]['new_path'], 'src/new.java')

    def test_reject_unsafe_repository(self):
        for name in ('../../x', 'a/..', './a', 'a/b/c', 'a/$(oops)'):
            with self.assertRaises(common.PipelineError):
                common.repo_cache('/tmp', name)


class Collection(unittest.TestCase):
    def test_paginated_stream(self):
        self.assertEqual(collect.decode_pages('[{"a":1}]\n[]\n'), [[{'a': 1}], []])
        with self.assertRaises(common.PipelineError):
            collect.decode_pages('{}')

    def test_normalized_fields_and_reference_order(self):
        item = collect.normalize({**advisory(), 'cwes': [{'cwe_id': 'CWE-862'}, {'cwe_id': 'CWE-285'}],
                                  'references': [{'url': 'second'}, 'first'],
                                  'vulnerabilities': [{'package': {'ecosystem': 'maven', 'name': 'z'}},
                                                      {'package': {'ecosystem': 'go', 'name': 'g'}}]}, 'maven')
        self.assertEqual(item['references'], ['second', 'first'])
        self.assertEqual(item['cwes'], ['CWE-285', 'CWE-862'])
        self.assertEqual(item['packages'], ['z'])

    def test_collect_withdrawn_cache_and_counts_only(self):
        raw = advisory(summary='DO NOT PRINT ADVISORY TEXT')
        withdrawn = advisory('GHSA-0002', withdrawn_at='2026-01-01')
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            stdout = io.StringIO()
            with patch.object(collect, 'run', side_effect=[json.dumps([raw, withdrawn]), '[]']) as mocked, \
                    contextlib.redirect_stdout(stdout):
                collect.main(root)
            self.assertNotIn(raw['summary'], stdout.getvalue())
            self.assertEqual(len(common.read_json(root / 'mining/advisories.json')), 1)
            self.assertEqual(common.read_json(root / 'mining/collect_inventory.json')['counts']['maven']['WITHDRAWN'], 1)
            self.assertEqual(common.read_json(root / 'mining/cache/advisories_maven.json'), [[raw, withdrawn]])
            for call in mocked.call_args_list:
                self.assertIn('--paginate', call.args[0])
                self.assertIn('CWE-306', call.args[0][-1])
            with self.assertRaises(common.PipelineError):
                collect.main(root)


class Sampling(unittest.TestCase):
    def items(self, repositories, per_repo):
        return [{'ghsa_id': f'GHSA-{r:03d}-{n:03d}', 'repo': f'owner/repo{r}'}
                for r in range(repositories) for n in range(per_repo)]

    def test_small_pool_keeps_all_without_cap(self):
        items = self.items(1, 160)
        self.assertEqual(sample.select(items), items)
        self.assertEqual(sample.select([]), [])

    def test_repository_cap_and_registered_seed(self):
        items = self.items(2, 100)
        chosen = sample.select(items)
        self.assertEqual(Counter(i['repo'] for i in chosen), {'owner/repo0': 4, 'owner/repo1': 4})
        expected = []
        for repo in ('owner/repo0', 'owner/repo1'):
            ids = sorted(i['ghsa_id'] for i in items if i['repo'] == repo)
            expected.extend(random.Random('r4:' + repo).sample(ids, 4))
        self.assertEqual([i['ghsa_id'] for i in chosen], sorted(expected))

    def test_global_cap_and_determinism(self):
        items = self.items(60, 10)
        first = sample.select(items)
        self.assertEqual(len(first), 160)
        self.assertEqual(first, sample.select(list(reversed(items))))
        self.assertTrue(all(v <= 4 for v in Counter(i['repo'] for i in first).values()))
        capped = []
        for r in range(60):
            repo = f'owner/repo{r}'
            capped.extend(random.Random('r4:' + repo).sample(
                sorted(i['ghsa_id'] for i in items if i['repo'] == repo), 4))
        expected = sorted(random.Random('r4-sample-20261123').sample(sorted(capped), 160))
        self.assertEqual([i['ghsa_id'] for i in first], expected)

    def test_reject_duplicate_id(self):
        with self.assertRaises(common.PipelineError):
            sample.select([{'ghsa_id': 'same'}, {'ghsa_id': 'same'}])


class GitPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(dir=SCRATCH)
        cls.fixture = Synthetic(Path(cls.directory.name))

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_source_repository_first_stable_order(self):
        item = advisory(source_code_location='https://github.com/DEMO/service.git', references=[
            'https://github.com/else/other/commit/' + 'a' * 40,
            'https://github.com/demo/service/commit/' + 'b' * 40,
            'https://github.com/else/other/commit/' + 'c' * 40,
            'https://github.com/demo/service/commit/1234567',
            'https://github.com/demo/service/pull/123',
            'https://github.com/demo/service/commit/' + 'f' * 41])
        self.assertEqual([s[1] for s in resolve.candidates(item)], ['b' * 40, '1234567', 'a' * 40, 'c' * 40])

    def test_short_sha_api_resolution_and_file_origin(self):
        f = self.fixture
        item = advisory(references=['https://github.com/demo/service/commit/' + f.fix[:8]])
        with patch.object(resolve, 'run', return_value=json.dumps({'sha': f.fix})) as mocked:
            result = resolve.resolve(item, f.root)
        self.assertEqual(result, f.resolution())
        self.assertTrue(mocked.call_args.args[0][-1].endswith(f.fix[:8]))
        self.assertEqual(common.git(f.cache, 'remote', 'get-url', 'origin').strip(), f.work.as_uri())

    def test_full_sha_also_uses_api_plan_precedence(self):
        f = self.fixture
        item = advisory(references=['https://github.com/demo/service/commit/' + f.fix])
        with patch.object(resolve, 'run', return_value=json.dumps({'sha': f.fix})) as mocked:
            self.assertEqual(resolve.resolve(item, f.root)['fix_sha'], f.fix)
        self.assertEqual(mocked.call_count, 1)

    def test_first_api_resolution_is_fixed_even_if_fetch_fails(self):
        item = advisory(references=['https://github.com/demo/service/commit/' + 'a' * 40,
                                    'https://github.com/demo/service/commit/' + 'b' * 40])
        with patch.object(resolve, 'run', return_value=json.dumps({'sha': 'a' * 40})) as api, \
                patch.object(resolve, 'fetch', side_effect=common.CommandError(1)):
            result = resolve.resolve(item, self.fixture.root)
        self.assertEqual(result['reason'], 'FETCH_ERROR')
        self.assertEqual(api.call_count, 1)

    def test_missing_candidate_fallback(self):
        f = self.fixture
        item = advisory(references=['https://github.com/demo/service/commit/' + 'a' * 40,
                                    'https://github.com/demo/service/commit/' + f.fix])
        with patch.object(resolve, 'run', side_effect=[common.CommandError(1, 'HTTP 404'),
                                                       json.dumps({'sha': f.fix})]):
            self.assertEqual(resolve.resolve(item, f.root)['fix_sha'], f.fix)

    def test_no_commit_and_fetch_error_distinguished(self):
        self.assertEqual(resolve.resolve(advisory())['reason'], 'NO_COMMIT')
        item = advisory(references=['https://github.com/demo/service/commit/' + 'a' * 40])
        with patch.object(resolve, 'run', side_effect=common.CommandError(1, 'HTTP 404')):
            self.assertEqual(resolve.resolve(item)['reason'], 'NO_COMMIT')
        with patch.object(resolve, 'run', side_effect=common.CommandError(1, 'HTTP 503')):
            self.assertEqual(resolve.resolve(item)['reason'], 'FETCH_ERROR')

    def test_api_network_error_cannot_silently_choose_later_candidate(self):
        item = advisory(references=['https://github.com/demo/service/commit/' + 'a' * 40,
                                    'https://github.com/demo/service/commit/' + 'b' * 40])
        with patch.object(resolve, 'run', side_effect=[common.CommandError(1, 'HTTP 503'),
                                                       json.dumps({'sha': 'b' * 40})]) as mocked:
            self.assertEqual(resolve.resolve(item)['reason'], 'FETCH_ERROR')
        self.assertEqual(mocked.call_count, 1)

    def test_root_commit_has_no_parent(self):
        f = self.fixture
        item = advisory(references=['https://github.com/demo/service/commit/' + f.empty])
        with patch.object(resolve, 'run', return_value=json.dumps({'sha': f.empty})):
            self.assertEqual(resolve.resolve(item, f.root)['reason'], 'NO_PARENT')

    def test_shallow_boundary_parent_repaired(self):
        f = self.fixture
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            cache = resolve.prepare_repo(Path(directory), 'demo/service', f.work.as_uri())
            common.git(cache, 'fetch', '--depth=1', '--filter=blob:none', 'origin', f.fix)
            with self.assertRaises(common.CommandError):
                common.git(cache, 'rev-parse', '--verify', f.fix + '^1')
            self.assertEqual(resolve.first_parent(cache, f.fix), f.base)

    def test_no_contract_at_parent_even_if_added_in_fix(self):
        f = self.fixture
        self.assertEqual(pool.eligible(f.resolution(f.no_contract, f.empty), f.root)['reason'], 'NO_CONTRACT_AT_PARENT')

    def test_no_source_change(self):
        f = self.fixture
        self.assertEqual(pool.eligible(f.resolution(f.test_only), f.root)['reason'], 'NO_SOURCE_CHANGE')

    def test_too_large_and_inclusive_limit(self):
        f = self.fixture
        self.assertEqual(pool.eligible(f.resolution(f.large), f.root)['reason'], 'TOO_LARGE')
        result = pool.eligible(f.resolution(f.boundary), f.root)
        self.assertEqual(result['fix_lines'], 2000)

    def test_mechanical_flags_and_source_line_count(self):
        f = self.fixture
        result = pool.eligible(f.resolution(), f.root)
        self.assertEqual(result['fix_lines'], 4)
        self.assertEqual(result['source_files'], ['src/Auth.kt', 'src/Main.java'])
        self.assertEqual(result['n_contract_docs'], 4)
        self.assertTrue(result['fix_silent'])
        self.assertTrue(result['test_in_fix'])
        self.assertFalse(result['fix_touches_contract'])
        self.assertFalse(result['fix_touches_annotation'])

    def test_contract_and_annotation_flags(self):
        f = self.fixture
        for sha, field in ((f.annotation, 'fix_touches_annotation'), (f.contract, 'fix_touches_contract')):
            result = pool.eligible(f.resolution(sha), f.root)
            self.assertTrue(result[field])
            self.assertFalse(result['fix_silent'])

    def test_deleted_test_does_not_count_as_test_added_or_modified(self):
        f = self.fixture
        self.assertFalse(pool.eligible(f.resolution(f.test_delete), f.root)['test_in_fix'])

    def test_source_rename(self):
        f = self.fixture
        result = pool.eligible(f.resolution(f.rename), f.root)
        self.assertEqual(result['fix_lines'], 0)
        self.assertEqual(result['source_files'], ['src/Main.java', 'src/Renamed.java'])

    def test_measurement_network_error_recorded(self):
        with patch.object(pool, 'git', side_effect=common.CommandError(1)):
            self.assertEqual(pool.eligible(self.fixture.resolution())['reason'], 'FETCH_ERROR')

    def test_binary_numstat_not_silently_zero(self):
        with patch.object(pool, 'git', side_effect=['openapi.yaml\0', '-\t-\tsrc/X.java\0']):
            with self.assertRaisesRegex(common.PipelineError, 'BINARY_SOURCE_NUMSTAT'):
                pool.eligible(self.fixture.resolution())

    def test_malformed_api_response_is_explicit_error(self):
        item = advisory(references=['https://github.com/demo/service/commit/' + 'a' * 40])
        for raw in ('[]', '{}', '{"sha":null}', 'not json'):
            with self.subTest(raw=raw), patch.object(resolve, 'run', return_value=raw):
                self.assertEqual(resolve.resolve(item)['reason'], 'FETCH_ERROR')

    def test_dedup_and_inventory_each_reason(self):
        f = self.fixture
        reasons = ['NO_COMMIT', 'NO_PARENT', 'FETCH_ERROR']
        advisories = [advisory(f'GHSA-{i:04d}') for i in range(9)]
        resolutions = {a['ghsa_id']: f.resolution() for a in advisories[:3]}
        resolutions.update({advisories[i + 3]['ghsa_id']: {'reason': reason}
                            for i, reason in enumerate(reasons)})
        resolutions.update({advisories[6]['ghsa_id']: f.resolution(f.no_contract, f.empty),
                            advisories[7]['ghsa_id']: f.resolution(f.test_only),
                            advisories[8]['ghsa_id']: f.resolution(f.large)})
        result, inventory = pool.make_pool(list(reversed(advisories)), resolutions, f.root)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['ghsa_id'], 'GHSA-0000')
        self.assertEqual(result[0]['ghsa_ids'], ['GHSA-0000', 'GHSA-0001', 'GHSA-0002'])
        self.assertEqual(inventory['counts']['DEDUP'], 2)
        for reason in reasons + ['NO_CONTRACT_AT_PARENT', 'NO_SOURCE_CHANGE', 'TOO_LARGE', 'ELIGIBLE']:
            self.assertEqual(inventory['counts'][reason], 1)
        self.assertEqual(sum(inventory['counts'].values()), 9)
        self.assertEqual(inventory['per_ecosystem']['maven'], inventory['counts'])
        self.assertEqual(inventory['per_repository']['demo/service']['DEDUP'], 2)


class Redaction(unittest.TestCase):
    def test_links_credit_email(self):
        text = ('https://github.com/o/r/commit/1234567\nhttps://github.com/o/r/pull/12\n'
                'https://github.com/o/r/compare/a...b\nhttps://github.com/o/r/releases/v1\n'
                'https://example.org/GHSA-abcd-efgh-1234\nhttps://example.org/CVE-2026-1234\n'
                'Credit: Jane\nThanks Jane\nReported by Jane\nDiscovered by Jane\nFound by Jane\n'
                'Contact jane@example.invalid\nHTTP check denied\n')
        counts = Counter()
        redacted = build.redact(text, counts, item=True)
        self.assertEqual(redacted.count('[LINK]'), 6)
        self.assertEqual(redacted.count('[CREDIT REDACTED]'), 5)
        self.assertNotIn('Jane', redacted)
        self.assertNotIn('jane@example.invalid', redacted)
        self.assertIn('HTTP check denied', redacted)
        self.assertEqual(counts['email'], 1)

    def test_secrets_redacted_and_only_kinds_logged(self):
        tokens = ['ghp_' + 'a' * 36, 'github_pat_' + 'A' * 40, 'AKIA' + 'A' * 16,
                  'xoxb-' + 'a' * 24, 'sk-proj-' + 'b' * 40]
        text = '\n'.join(tokens) + '\npassword = "actual-sensitive-value"\nAuthorization: Bearer abcdefghijklmnop\n'
        counts = Counter()
        redacted = build.redact(text, counts)
        for token in tokens + ['actual-sensitive-value', 'abcdefghijklmnop']:
            self.assertNotIn(token, redacted)
            self.assertNotIn(token, json.dumps(counts))
        self.assertEqual(counts['credential_prefix'], len(tokens))
        self.assertEqual(counts['credential_assignment'], 1)

    def test_structured_json_and_private_key(self):
        raw = '{"password":"secret-value","contact":{"name":"Some Person","email":"a@b.invalid"}}'
        redacted = build.redact(raw)
        self.assertNotIn('secret-value', redacted)
        self.assertNotIn('Some Person', redacted)
        raw = '-----BEGIN PRIVATE KEY-----\nABCDEF\n-----END PRIVATE KEY-----\nclass Main {}\n'
        redacted = build.redact(raw)
        self.assertNotIn('ABCDEF', redacted)
        self.assertIn('class Main {}', redacted)

    def test_hmac_shuffle_deterministic_and_salt_sensitive(self):
        items = [{'ghsa_id': f'GHSA-{i}'} for i in range(20)]
        salt = bytes(range(32))
        first = build.shuffled(items, salt)
        self.assertEqual(first, build.shuffled(list(reversed(items)), salt))
        self.assertNotEqual(first, build.shuffled(items, bytes(reversed(salt))))

    def test_majority_language_and_stable_tie(self):
        self.assertEqual(build.language({'source_files': ['A.java', 'B.kt', 'C.kt']}), 'Kotlin')
        self.assertEqual(build.language({'source_files': ['A.java', 'B.kt']}), 'Java')


class FrozenPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(dir=SCRATCH)
        cls.fixture = Synthetic(Path(cls.directory.name))

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def stage(self, root, sha=None):
        f = self.fixture
        cache = common.repo_cache(root, 'demo/service')
        cache.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(f.cache, cache)
        mining = root / 'mining'
        a = advisory(description='Reported by PRIVATE REPORTER\nEmail author@example.invalid\n'
                      'See https://github.com/demo/service/commit/' + f.fix)
        common.write_json(mining / 'advisories.json', [a])
        common.write_json(mining / 'resolved.json', {a['ghsa_id']: f.resolution(sha)})
        for ecosystem in common.ECOSYSTEMS:
            common.write_json(mining / f'cache/advisories_{ecosystem}.json', [])
        (root / 'plan').mkdir()
        (root / 'plan/TASK_R4.md').write_bytes(b'Synthetic opaque task fixture\n')
        with contextlib.redirect_stdout(io.StringIO()):
            pool.main(root)
            sample.main(root)

    def test_end_to_end_build_no_commit_metadata(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root)
            with contextlib.redirect_stdout(io.StringIO()):
                build.main(root)
            blind = root / 'packages/r4_blind'
            contents = '\n'.join(p.read_text() for p in blind.rglob('*') if p.is_file())
            for private in ('PRIVATE COMMIT MESSAGE', 'PRIVATE SYNTHETIC AUTHOR',
                            'private-author@example.invalid', 'PRIVATE SOURCE AUTHOR', 'PRIVATE REPORTER'):
                self.assertNotIn(private, contents)
            item = (blind / 'A001/item.md').read_text()
            self.assertIn('[LINK]', item)
            self.assertIn('[CREDIT REDACTED]', item)
            patch_text = (blind / 'A001/diff.patch').read_text()
            self.assertTrue(patch_text.startswith('diff --git '))
            self.assertNotIn('MainTest', patch_text)
            self.assertEqual((blind / 'TASK_R4.md').read_bytes(), b'Synthetic opaque task fixture\n')
            for p in (blind / 'A001').rglob('*'):
                if p.is_file():
                    twin = root / 'packages/r4_kb1/A001' / p.relative_to(blind / 'A001')
                    self.assertEqual(p.read_bytes(), twin.read_bytes())
            contracts = list((blind / 'A001/contract').glob('*'))
            self.assertEqual(len(contracts), 4)  # three docs plus index
            self.assertEqual(len((blind / 'A001/contract/api__openapi.yaml').read_text().splitlines()), 3000)
            self.assertFalse((blind / 'A001/contract/api__swagger.json').exists())
            self.assertIn('api/swagger.json', (blind / 'A001/contract/INDEX.md').read_text())
            self.assertEqual(len(bytes.fromhex((root / 'mining/key/r4_shuffle_salt.txt').read_text().strip())), 32)
            key_rows = list(csv.DictReader(io.StringIO((root / 'mining/key/r4_key.csv').read_text())))
            self.assertEqual(set(key_rows[0]), set(build.KEY_COLUMNS))
            self.assertEqual(key_rows[0]['fix_sha'], self.fixture.fix)
            self.assertEqual(key_rows[0]['item_id'], 'A001')
            self.assertIn('contract_truncated', common.read_json(root / 'mining/key/r4_build_log.json')['A001']['notes'])

    def test_all_pipeline_scripts_refuse_existing_frozen_outputs(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root)
            with contextlib.redirect_stdout(io.StringIO()):
                build.main(root)
            for module in (collect, resolve, pool, sample, build):
                with self.subTest(module=module.__name__), self.assertRaises(common.PipelineError):
                    module.main(root)

    def test_each_freeze_alone_prevents_overwriting(self):
        for module, frozen in ((collect, 'mining/pool_freeze.json'),
                               (resolve, 'mining/pool_freeze.json'),
                               (pool, 'mining/pool_freeze.json'),
                               (sample, 'mining/sample_freeze.json'),
                               (build, 'packages/r4_blind')):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
                root = Path(directory)
                path = root / frozen
                path.parent.mkdir(parents=True)
                path.write_text('immutable sentinel\n')
                before = common.sha256_file(path)
                with self.assertRaises(common.PipelineError):
                    module.main(root)
                self.assertEqual(common.sha256_file(path), before)

    def test_resolve_main_record_and_overwrite_guard(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            common.write_json(root / 'mining/advisories.json', [advisory()])
            with contextlib.redirect_stdout(io.StringIO()):
                resolve.main(root)
            self.assertEqual(common.read_json(root / 'mining/resolved.json'),
                             {'GHSA-0001': {'reason': 'NO_COMMIT'}})
            with self.assertRaises(common.PipelineError):
                resolve.main(root)

    def test_source_diff_secret_redaction_and_kind_only_log(self):
        f = self.fixture
        token = 'ghp_' + 'z' * 36
        sha = f.commit({'src/Main.java': '// author@example.invalid\nclass Main { String key = "' + token + '"; }\n'})
        resolve.fetch(f.cache, sha)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root, sha)
            with contextlib.redirect_stdout(io.StringIO()):
                build.main(root)
            folder = root / 'packages/r4_blind/A001'
            for path in (folder / 'diff.patch', folder / 'after/src__Main.java'):
                text = path.read_text()
                self.assertNotIn(token, text)
                self.assertNotIn('author@example.invalid', text)
                self.assertIn('[REDACTED]', text)
            log = common.read_json(root / 'mining/key/r4_build_log.json')
            self.assertGreaterEqual(log['A001']['scan_counts']['credential_prefix'], 2)
            self.assertNotIn(token, json.dumps(log))

    def test_contract_is_from_parent(self):
        f = self.fixture
        sha = f.commit({'src/Main.java': 'class Main {}\n', 'api/openapi.yaml': 'FIX_VERSION_MUST_NOT_BE_DELIVERED\n'})
        resolve.fetch(f.cache, sha)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root, sha)
            with contextlib.redirect_stdout(io.StringIO()):
                build.main(root)
            contract = (root / 'packages/r4_blind/A001/contract/api__openapi.yaml').read_text()
            self.assertTrue(contract.startswith('openapi: 3.0.0\n'))
            self.assertNotIn('FIX_VERSION_MUST_NOT_BE_DELIVERED', contract)

    def test_frozen_input_tampering_rejected(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root)
            with (root / 'mining/advisories.json').open('a') as stream:
                stream.write('\n')
            with self.assertRaises(common.PipelineError):
                build.main(root)
            self.assertFalse((root / 'packages/r4_blind').exists())

    def test_sample_refuses_pool_tampering(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root)
            (root / 'mining/sample.json').unlink()
            (root / 'mining/sample_freeze.json').unlink()
            (root / 'mining/pool.json').write_text('[]\n')
            with self.assertRaises(common.PipelineError):
                sample.main(root)

    def test_pool_freeze_link_tampering_rejected(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root)
            with (root / 'mining/pool_freeze.json').open('a') as stream:
                stream.write('\n')
            with self.assertRaises(common.PipelineError):
                build.main(root)

    def test_before_after_added_deleted_sources(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root, self.fixture.add_delete)
            with contextlib.redirect_stdout(io.StringIO()):
                build.main(root)
            folder = root / 'packages/r4_blind/A001'
            self.assertTrue((folder / 'before/src__Main.java').exists())
            self.assertFalse((folder / 'after/src__Main.java').exists())
            self.assertTrue((folder / 'after/src__New.kt').exists())
            self.assertFalse((folder / 'before/src__New.kt').exists())

    def test_largest_source_changes_first_and_twenty_limit(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            f = Synthetic(root)
            sha = f.commit({f'src/File{i:02d}.java': '// added\n' * (i + 1) for i in range(22)})
            resolve.fetch(f.cache, sha)
            mechanical = pool.eligible(f.resolution(sha), root)
            item = {**mechanical, 'ghsa_id': 'GHSA-0001', 'ghsa_ids': ['GHSA-0001'], 'cwes': ['CWE-285']}
            build.build_item(root / 'synthetic_package', item, {'GHSA-0001': advisory()}, root)
            paths = list((root / 'synthetic_package/after').glob('*'))
            self.assertEqual(len(paths), 20)
            self.assertFalse((root / 'synthetic_package/after/src__File00.java').exists())
            self.assertFalse((root / 'synthetic_package/after/src__File01.java').exists())
            self.assertTrue((root / 'synthetic_package/after/src__File21.java').exists())

    def test_claude_batches_sixteen_then_remainder(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            root = Path(directory)
            self.stage(root)
            mining = root / 'mining'
            original = common.read_json(mining / 'pool.json')[0]
            items = [{**copy.deepcopy(original), 'ghsa_id': f'GHSA-{i:04d}',
                      'ghsa_ids': [f'GHSA-{i:04d}']} for i in range(17)]
            # This synthetic fixture isolates batching; no mining inference.
            for name in ('pool.json', 'pool_freeze.json', 'sample.json', 'sample_freeze.json'):
                (mining / name).unlink()
            common.write_json(mining / 'pool.json', items)
            common.write_json(mining / 'pool_freeze.json', {'sha256': {'pool.json': common.sha256_file(mining / 'pool.json')}})
            with contextlib.redirect_stdout(io.StringIO()):
                sample.main(root)

            def fake_item(folder, item, advisories, root):
                folder.mkdir()
                build.write_text(folder / 'item.md', 'synthetic\n')
                return {'notes': {}, 'scan_counts': {}}
            with patch.object(build, 'build_item', side_effect=fake_item), contextlib.redirect_stdout(io.StringIO()):
                build.main(root)
            for number, expected in ((1, 16), (2, 1)):
                rows = list(csv.DictReader(io.StringIO((root / f'packages/r4_kb{number}/items.csv').read_text())))
                self.assertEqual(len(rows), expected)
                self.assertEqual([r['item_id'] for r in rows], sorted(r['item_id'] for r in rows))
            self.assertFalse((root / 'packages/r4_kb3').exists())


if __name__ == '__main__':
    SCRATCH.mkdir(parents=True, exist_ok=True)
    # A git invocation cannot accidentally fall back to HTTP/SSH in this suite.
    with patch.dict(os.environ, {'GIT_ALLOW_PROTOCOL': 'file'}):
        unittest.main(verbosity=2)
