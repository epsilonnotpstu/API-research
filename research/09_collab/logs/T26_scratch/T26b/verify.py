"""Verify staging, preserved live files, original-source smoke claims and install diff."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRATCH = Path(__file__).resolve().parent
before = json.loads((SCRATCH / 'protected_before.json').read_text())
report = '09_collab/reports/T26_report.md'
changed = [p for p, digest in before.items() if p != report and (
    not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != digest)]
assert not changed, changed
old_report_bytes = (ROOT / report).read_bytes().split(b'\n## T26b', 1)[0]
assert hashlib.sha256(old_report_bytes).hexdigest() == before[report], 'Prior T26 report was modified'
rows = json.loads((SCRATCH / 'after_summary.json').read_text())
assert all(r['repeat_identical'] and r['locators_verified'] and r['returncode'] == 0 for r in rows)
roles = json.loads((SCRATCH / 'after_scout_roles.json').read_text())
assert roles['independent_evidence'] == 'supports_spec'
assert any(h.get('match') == 'suffix' and h.get('asserted_values') == [200] for h in roles['hits'])
market = json.loads((SCRATCH / 'after_market_products.json').read_text())
market_tests = [h for h in market['hits'] if h['category'] == 'E-TEST']
assert len(market_tests) == 6 and all(h['module_scope'] == 'other_module' and not h['independent'] and not h['support'] for h in market_tests)
assert any(h['category'] == 'E-DOC' and h['file'].endswith('templates/rest.html') and h['module'] == 'market-web' and h['independent'] for h in market['hits'])
pet = json.loads((SCRATCH / 'after_petstore_name.json').read_text())
assert any(h.get('operation_id') == 'getPetById' and h['controller'].endswith('.PetController') for h in pet['hits'])
assert any(h['category'] == 'HANDLER' and h['file'].endswith('/Pet.java') and h['line'] == 54 and h['field'] == 'name' for h in pet['hits'])
assert pet['code_field_behavior'] == [] and pet['independent_evidence'] == 'none_found'
for row in rows:
    data = json.loads((SCRATCH / ('after_' + row['case'] + '.json')).read_text())
    assert all(len(h['snippet']) <= 160 and h['strength'].startswith('⚠️ ') for h in data['hits'])
suites = json.loads((SCRATCH / 'tests_summary.json').read_text())
assert all(suite['returncode'] == 0 for suite in suites)
assert json.loads((SCRATCH / 'p001_replay/summary.json').read_text())['replay_errors'] == 0
diff = []
install_base = {}
hashes = {}
imports = {}
for name in ('intent_evidence.py', 'test_intent_evidence.py'):
    live = ROOT / '08_experiments/tools' / name
    staged = SCRATCH / 'staged' / name
    install_base[str(live.relative_to(ROOT))] = hashlib.sha256(live.read_bytes()).hexdigest()
    hashes[str(staged.relative_to(ROOT))] = hashlib.sha256(staged.read_bytes()).hexdigest()
    diff.extend(difflib.unified_diff(live.read_text().splitlines(True), staged.read_text().splitlines(True),
                                   fromfile='a/' + str(live.relative_to(ROOT)), tofile='b/' + str(live.relative_to(ROOT))))
    tree = ast.parse(staged.read_text())
    imports[name] = sorted({n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} |
                           {alias.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names})
(SCRATCH / 'install.patch').write_text(''.join(diff))
(SCRATCH / 'install_base_sha256.json').write_text(json.dumps(install_base, indent=2) + '\n')
verification = {'protected_files_checked': len(before) - 1, 'protected_changed': changed,
                'live_tools_unchanged': True, 'prior_T26_report_prefix_preserved': True,
                'original_source_smoke_locators_verified': True, 'all_repeat_outputs_identical': True,
                'all_suites_pass': True, 'staged_sha256': hashes, 'staged_imports': imports}
(SCRATCH / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
print(json.dumps(verification, indent=2))
