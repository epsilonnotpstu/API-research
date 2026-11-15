#!/usr/bin/python3
"""Read-only independent verification of the delivered set; never emit source text."""
import ast
from collections import Counter
import csv
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '08_experiments/E6_realfix'))
import build_e6_blind as b


def main():
    checks = 0
    def check(value, description):
        nonlocal checks
        if not value:
            raise SystemExit('Verification failed: ' + description)
        checks += 1

    log = json.loads((b.HERE / 'e6_build_log.json').read_bytes())
    preflight = json.loads((ROOT / '09_collab/logs/T44_scratch/preflight.json').read_bytes())
    check({k: v for k, v in log.items() if k not in {'key_sha256', 'disk_hashes_verified'}} == preflight,
          'preflight and published plan differ')
    actual = {p.relative_to(b.BLIND).as_posix(): p.read_bytes() for p in b.BLIND.rglob('*') if p.is_file()}
    check(set(actual) == set(log['package_hashes']), 'delivered file set')
    for path, data in actual.items():
        check(b.sha(data) == log['package_hashes'][path], 'delivered hash')
        check(not (b.BLIND / path).is_symlink(), 'delivered symlink')
    check(sum(map(len, actual.values())) == log['summary']['package_bytes'], 'total package bytes')
    check(b.sha((b.HERE / 'e6_key.csv').read_bytes()) == log['key_sha256'], 'key hash')
    manifest = list(csv.DictReader(io.StringIO(actual['items.csv'].decode())))
    key = list(csv.DictReader((b.HERE / 'e6_key.csv').open()))
    source = {r['item_id']: r for r in csv.DictReader((b.HERE / 'combined_accepted.csv').open())}
    check(list(key[0]) == b.KEY_COLUMNS, 'key schema')
    check(list(manifest[0]) == b.ITEM_COLUMNS, 'manifest schema')
    check([r['item_id'] for r in manifest] == [r['item_id'] for r in key], 'manifest/key item join')
    details = {r['item_id']: r for r in log['items']}
    check(set(details) == {f'K{i:02}' for i in range(1, len(source) + 1)}, 'reserved item IDs')
    check(set(log['excluded_items']) == {i for i, d in details.items() if d['status'] == 'excluded'}, 'excluded ledger')
    check(set(d.split('/')[0] for d in actual if '/source/' in d) == {r['item_id'] for r in manifest}, 'no unscored package retained')
    git_by_repo = {repo: b.Git(path) for repo, path in log['git_dirs'].items()}
    needles = b.fixture_needles(sorted(b.AUTH.glob('*.yaml')))

    # Execute the existing E4 credential scan function verbatim, without importing
    # its builder or accessing any of its package/key inputs.
    existing_path = ROOT / '08_experiments/E4_triage/build_e4_blind.py'
    tree = ast.parse(existing_path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'assert_no_credentials')
    namespace = {'json': json, 'require': b.require, 'AUTH_NAMES': {'authorization', 'proxy-authorization', 'cookie', 'set-cookie'}}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(existing_path), 'exec'), namespace)
    namespace['assert_no_credentials'](b.BLIND, needles)
    check(True, 'existing E4 auth-fixture literal/JSON/URL scan')

    # Re-run the existing T43 leakage function verbatim with a read-only adapter
    # supplying delivered files instead of a Git parent. Every same-repo target
    # is checked against every retained package, including excluded targets.
    t43_path = b.HERE / 't43/t43_build.py'
    t43_ast = ast.parse(t43_path.read_text())
    t43_node = next(n for n in t43_ast.body if isinstance(n, ast.FunctionDef) and n.name == 'leakage')
    legacy_file_scans = 0
    for record in manifest:
        iid = record['item_id']; detail = details[iid]
        package_files = {p: actual[f'{iid}/source/{p}'] for p in detail['files']}
        def source_adapter(repo, revision, path):
            data = package_files[path]
            return data.decode(), b.sha(data)
        legacy = {'Path': Path, 're': re, 'source': source_adapter,
                  'm': {'git': lambda *args: '\n'.join(sorted(package_files)).encode()}}
        exec(compile(ast.Module(body=[t43_node], type_ignores=[]), str(t43_path), 'exec'), legacy)
        targets = [dict(r, parent_commit=detail['parent_commit']) for r in source.values() if r['repo'] == detail['repo']]
        records = legacy['leakage'](targets)
        for result in records:
            check(not result['hits'] and not result['issue_identifier_hits'], 'existing T43 actual-file scan')
            legacy_file_scans += len(result['files_scanned'])

    child_comparisons = 0; prose_scans = 0; cross_checks = 0; json_contracts = 0
    for record, k in zip(manifest, key):
        iid = record['item_id']; detail = details[iid]; row = source[detail['source_item']]
        git = git_by_repo[row['repo']]; parent = git.tree(row['parent_commit']); child = git.tree(row['fix_commit'])
        check(record['proposition'] == row['proposition'], 'verbatim proposition')
        check(record['operation'] == row['operation'], 'operation copied')
        check(record['package'] == iid, 'package locator')
        for column in b.KEY_COLUMNS[1:]:
            check(k[column] == row[column], 'hidden key field')
        paths = set(detail['files'])
        check(set(detail['protected_paths']) <= paths, 'protected source included')
        check(set(detail['contracts']) <= paths, 'all contract references included')
        check(record['contract_locator_hint'] == ' | '.join('source/' + p for p in sorted(detail['contracts'])), 'contract path-only hint')
        check(not re.search(r':\d+\b', record['contract_locator_hint']), 'no contract line hints')
        changed = git.changed(row['parent_commit'], row['fix_commit'])
        child_entries = [child[p] for p in changed if p in child and child[p].kind == 'blob' and (p not in parent or parent[p].oid != child[p].oid)]
        child_hashes = {b.sha(v) for v in git.blobs(child_entries).values()}
        git.blobs([parent[p] for p in paths])
        repo_rows = [r for r in source.values() if r['repo'] == row['repo']]
        for path in paths:
            data = actual[f'{iid}/source/{path}']; raw = git.cache[parent[path].oid]
            check(b.sha(raw) == detail['files'][path]['parent_sha256'], 'parent blob hash')
            check(data == b.redact(raw, needles), 'only approved parent redaction')
            check(len(data.splitlines()) == len(raw.splitlines()), 'source line positions')
            check(b.sha(data) not in child_hashes and b.sha(raw) not in child_hashes, 'no child-version equality')
            child_comparisons += 1
            check(not b.privacy_findings(data, needles), 'current privacy scans')
            check(not b.reference_hits(data, repo_rows, b.is_doc(path)), 'actual future-reference scan')
            prose_scans += int(b.is_doc(path))
            check(not b.omission_reason(path, parent[path]), 'source inclusion safety rules')
            if path in detail['contracts'] and path.endswith('.json'):
                json.loads(data); json_contracts += 1
        for other in manifest:
            if other['item_id'] == iid:
                continue
            other_detail = details[other['item_id']]
            if other_detail['repo'] == row['repo'] and git.ancestor(row['fix_commit'], other_detail['parent_commit']):
                check(not set(changed) & other_detail['files'].keys(), 'retained cross-item overlap')
                cross_checks += 1
    b.assert_generated(actual)
    check(actual['CODEBOOK_v0.6.md'] == (b.REFERENCE / 'CODEBOOK_v0.6.md').read_bytes(), 'unchanged codebook')
    for method in ['M1', 'M2']:
        text = actual[f'TASK_{method}.md'].decode()
        original = (b.REFERENCE / f'TASK_{method}.md').read_text()
        authorization = next(p for p in original.split('\n\n') if p.startswith('**Supervisor authorization:**'))
        check(authorization in text, 'launch authorization verbatim')
        check('do not compare files across packages' in text, 'cross-package comparison rule')
        check('Every rg, grep, find, or other search must name explicit permitted' in text, 'explicit-path rule')
        check('Redact credential-looking lines' in text, 'redaction rule')
        check('no runtime exchanges' in text, 'source-only task')
    freeze = json.loads((ROOT / '09_collab/logs/T44_scratch/input_freeze.json').read_text())
    drift = [path for path, digest in freeze.items() if b.sha((ROOT / path).read_bytes()) != digest]
    check(not drift, 'pre-existing input files unchanged')
    output = {'passed': True, 'assertions': checks, 'files_hashed': len(actual),
              'protected_inputs_unchanged': len(freeze), 'own_child_file_comparisons': child_comparisons,
              'prose_files_scanned': prose_scans, 'retained_cross_ancestry_checks': cross_checks,
              'json_contracts_parsed': json_contracts, 'existing_E4_credential_scan': 'PASS',
              'existing_T43_leakage_scan': 'PASS', 'existing_T43_item_file_scans': legacy_file_scans,
              'directions': dict(Counter(r['truth_direction'] for r in key)),
              'sizes': log['summary'],
              'per_package': [{'item_id': d['item_id'], 'files': len(d['files']), 'bytes': d['bytes']} for d in log['items'] if d['status'] == 'scored'],
              'excluded_items': log['excluded_items'], 'input_drift': drift}
    out = ROOT / '09_collab/logs/T44_scratch/production_verification.json'
    with out.open('xb') as stream:
        stream.write(b.json_bytes(output))
    print(json.dumps({k: output[k] for k in ['passed', 'assertions', 'files_hashed', 'protected_inputs_unchanged', 'directions', 'excluded_items']}))


if __name__ == '__main__':
    main()
