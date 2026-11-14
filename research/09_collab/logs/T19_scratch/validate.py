"""Validate own Python, reviewed source anchors and frozen evidence; no SUT execution."""
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path.cwd()
E = ROOT / '08_experiments/E5_codemut'
S = ROOT / '09_collab/logs/T19_scratch'
H = ROOT / '08_experiments/E1_pilot/harness_v2'
spec = importlib.util.spec_from_file_location('codemut', E / 'codemut.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
results = {}
cat = json.loads((E / 'sites.json').read_text())
c.validate_sites(cat['sites'])
assert cat['roots'] == c.ROOTS
assert len(cat['sites']) == 20
per_sut = Counter(s['sut'] for s in cat['sites']); per_op = Counter(s['operator'] for s in cat['sites'])
assert set(per_sut.values()) == {5} and set(per_op.values()) == {4}
pilots = Counter(s['sut'] for s in cat['sites'] if s['pilot'])
assert sorted(pilots.values()) == [2, 2, 3, 3]
site_records = []
for s in cat['sites']:
    path = c.EMB / c.ROOTS[s['sut']] / s['file']
    raw = path.read_bytes(); changed = c.edit_bytes(raw, s)
    assert changed != raw
    assert s['evidence'] == str(path.relative_to(ROOT)) + ':' + str(s['line'])
    original_spec = json.loads((c.EMB / 'openapi-swagger' / (s['sut'] + '.json')).read_text())
    for op in s['operations']:
        assert op['method'] in original_spec['paths'][op['path']]
    site_records.append({'site_id': s['site_id'], 'file_sha256': sha(path), 'line': s['line'],
                         'anchor_unique': True, 'edit_in_memory_only': True, 'operations_in_original_spec': True})
results['catalogue'] = {'sites': len(site_records), 'per_sut': dict(per_sut), 'per_operator': dict(per_op),
                        'pilot_per_sut': dict(pilots), 'rows': site_records}

# Recount physical JSONL records independently against the frozen run selection.
ex = json.loads((E / 'exposure.json').read_text()); counts = {}; checked_locators = 0
for sut, run in ex['runs'].items():
    d = ROOT / run['run_dir']; log = d / 'exchanges.jsonl'
    assert sha(d / 'run.json') == run['run_metadata_sha256']
    assert sha(log) == run['exchanges_sha256']
    meta = json.loads((d / 'run.json').read_text())
    assert meta['complete'] and meta['mode'] == 'baseline' and meta['seed'] == 1
    rows = [r for r in ex['operations'] if r['sut'] == sut]
    routes = sorted(rows, key=lambda r: (r['path'].count('{'), -len(r['path'])))
    patterns = [(r, re.compile('^' + re.escape(run['base_path'].rstrip('/')) +
                  ''.join('[^/]+' if part.startswith('{') else re.escape(part)
                          for part in re.split(r'(\{[^{}]+\})', r['path'])) + '/?$')) for r in routes]
    all_records = [json.loads(raw) if raw.strip() else None for raw in log.read_bytes().split(b'\n')]
    counters = {r['evidence_id']: Counter() for r in rows}
    for record in all_records:
        if record is None: continue
        req, resp = record.get('request', {}), record.get('response') or {}
        for row, pat in patterns:
            if req.get('method', '').lower() == row['method'] and pat.fullmatch(req.get('path', '')):
                counters[row['evidence_id']][str(resp.get('status'))] += 1
                break
    for row in rows:
        assert dict(counters[row['evidence_id']]) == row['statuses'], row['evidence_id']
        assert sum(row['statuses'].values()) == row['requests']
        for key in ('first_exchange', 'first_2xx_exchange', 'first_nonempty_2xx_exchange'):
            line = row[key]
            if line is not None:
                req, resp = all_records[line - 1]['request'], all_records[line - 1]['response']
                assert req['method'].lower() == row['method']
                if key != 'first_exchange': assert 200 <= resp['status'] < 300
                if key == 'first_nonempty_2xx_exchange':
                    body = json.loads(resp['body']['text']); assert isinstance(body, (dict, list)) and body
                checked_locators += 1
        for name, line in row['missing_query_2xx'].items():
            rec = all_records[line - 1]
            assert name not in rec['request'].get('query', {}) and 200 <= rec['response']['status'] < 300
            checked_locators += 1
    counts[sut] = {'operations': len(rows), 'captured_requests': sum(r['requests'] for r in rows), 'hashes_verified': True}
assert len(ex['operations']) == 86
results['exposure'] = {'operations': 86, 'locators_checked': checked_locators, 'runs': counts}

# Only parse our own Python, including future inline Python; never execute build/run blocks.
py_files = list(E.glob('*.py')) + list(S.glob('*.py')) + [S / 'harness_proposal/run_metadata.py']
for p in py_files: ast.parse(p.read_text(), filename=str(p))
readme = (E / 'README.md').read_text()
blocks = re.findall(r'^```bash\n(.*?)^```', readme, re.M | re.S)
script = '\n'.join(blocks)
(S / 'readme-commands.sh').write_text(script)
for p in (S / 'readme-commands.sh', S / 'harness_proposal/run_pilot.sh'):
    outcome = subprocess.run(['bash', '-n', str(p)], text=True, capture_output=True)
    assert outcome.returncode == 0, outcome.stderr
inline = []
for text, name in [(script, 'README'), ((S / 'harness_proposal/run_pilot.sh').read_text(), 'proposed run_pilot')]:
    for match in re.finditer(r"<<'([A-Z0-9_]+)'\n(.*?)^\1$", text, re.M | re.S):
        ast.parse(match[2], filename=name + ':' + match[1]); inline.append(name + ':' + match[1])
assert len(inline) == 5, inline
assert readme.split('```diff\n', 1)[1].split('```', 1)[0] == (E / 'harness.proposed.diff').read_text()
base = json.loads((E / 'harness.proposal.base-sha256.json').read_text())
for name, digest in base.items(): assert sha(ROOT / name) == digest
# Check each unified diff hunk against the unchanged original and the staged proposal.
patch = (E / 'harness.proposed.diff').read_text().splitlines(keepends=True)
index = 0; hunk_count = 0
while index < len(patch):
    assert patch[index].startswith('--- a/'); name = patch[index][6:].strip(); index += 1
    assert patch[index].startswith('+++ b/'); index += 1
    before = (ROOT / name).read_text().splitlines(keepends=True); after = []; cursor = 0
    while index < len(patch) and patch[index].startswith('@@ '):
        start = int(re.match(r'@@ -(\d+)', patch[index])[1]) - 1
        after.extend(before[cursor:start]); cursor = start; index += 1; hunk_count += 1
        while index < len(patch) and patch[index][:1] in (' ', '-', '+') and not patch[index].startswith('--- a/'):
            line = patch[index]; index += 1
            if line[0] in (' ', '-'):
                assert before[cursor] == line[1:]; cursor += 1
            if line[0] in (' ', '+'): after.append(line[1:])
    after.extend(before[cursor:])
    assert ''.join(after) == (S / 'harness_proposal' / Path(name).name).read_text()
results['static'] = {'own_python_files_parsed': len(py_files), 'bash_blocks_parsed': len(blocks),
                     'inline_python_parsed': inline, 'embedded_diff_exact': True, 'proposal_hunks_verified': hunk_count}

# An interoperability probe executes only the existing own Python attribution function.
spec = importlib.util.spec_from_file_location('own_attribute', ROOT / '08_experiments/tools/attribute.py')
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
site = cat['sites'][0]; op = site['operations'][0]
manifest = {'mutations': [dict(op, fault=site['operator'], expected_L1='IMPL', expected_L2=site['expected_L2'], edits=[])]}
v = {'fingerprint': 'synthetic', 'method': op['method'].upper(), 'template': op['path'],
     'kind': 'SERVER_ERROR', 'status': 500, 'pointer': ''}
fresh = a.attribute([], [v], manifest, mode='fresh')[0]
assert fresh['label_L1'] == 'NEEDS_MANUAL' and fresh['expected_if_injected'] == 'IMPL'
results['attribute_interop'] = {'fresh_label': fresh['label_L1'], 'expected_only': fresh['expected_if_injected']}

protected = json.loads((S / 'protected_before.json').read_text())
changed = [name for name, digest in protected.items() if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
assert not changed, changed
results['protected_files'] = {'count': len(protected), 'changed': changed, 'scope': 'initial harness_v2 and tools regular files; excludes hidden/cache paths'}
results['execution'] = {'own_python_and_bash_syntax_only': True, 'java_maven_docker_sut_schemathesis': 'not_run',
                        'real_source_edits': 'in_memory_validation_only', 'real_builds': 'not_run'}
# Validate full repository file:line citations without interpreting external content.
citations = 0
for doc in (E / 'OPERATORS.md', E / 'README.md', ROOT / '09_collab/reports/T19_report.md'):
    for match in re.finditer(r'`((?:08_experiments|09_collab)/[^`\s:]+):(\d+(?:[–-]\d+)?(?:,\d+(?:[–-]\d+)?)*)`', doc.read_text()):
        path = ROOT / match[1]
        assert path.is_file(), (doc, match[1])
        size = len(path.read_bytes().split(b'\n'))
        for value in re.findall(r'\d+', match[2]):
            assert 1 <= int(value) <= size, (doc, match[1], value, size)
        citations += 1
results['documentation'] = {'repository_file_line_citations_checked': citations, 'status': 'PASS'}
results['status'] = 'PASS'
(S / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({k: v for k, v in results.items() if k not in ('catalogue',)}, indent=2))
