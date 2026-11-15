"""Read-only, explicit non-blind intent searches; all outputs stay in T33 scratch."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EMB = ROOT / '08_experiments/_external/emb'
TOOL = ROOT / '08_experiments/tools/intent_evidence.py'
SOURCES = {
    'scout': EMB / 'jdk_8_maven/cs/rest/original/scout-api',
    'market': EMB / 'jdk_11_maven/cs/rest-gui/market',
    'petstore': EMB / 'jdk_8_maven/cs/rest/original/swagger-petstore',
    'cwa': EMB / 'jdk_11_maven/cs/rest/cwa-verification-server',
}
CASES = [
    ('scout_roles', 'scout', 'scout-api', 'GET', '/v1/system/roles', ['--status', '418']),
    ('market_products', 'market', 'market', 'GET', '/products', ['--status', '200']),
    ('petstore_name', 'petstore', 'swagger-petstore', 'GET', '/pet/{petId}', ['--field', 'name']),
    ('scout_activities', 'scout', 'scout-api', 'GET', '/v2/activities', ['--status', '200']),
    ('cwa_tan', 'cwa', 'cwa-verification', 'POST', '/version/v1/tan', ['--status', '201']),
    ('baseline_B065', 'scout', 'scout-api', 'POST', '/v1/users', ['--status', '403']),
    ('baseline_M003', 'market', 'market', 'PUT', '/customer/cart', ['--status', '406']),
]
protected = [TOOL, ROOT / '08_experiments/R1_triage_codebook.md',
             ROOT / '09_collab/reports/T26_report.md', ROOT / '09_collab/tasks/T33.md']
for name in ['FINAL_LABELS.md', 'final_labels_baseline_s1.csv',
             'batch2_baseline_s1_labels_codex.csv', 'market_baseline_s1_labels_codex.csv',
             'batch2_adjudication.csv', 'market_adjudication.csv',
             'swagger-petstore_adjudication.csv', 'cwa-verification_adjudication.csv']:
    protected.append(ROOT / '08_experiments/E2_labelling' / name)

def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}

before = hashes()
(OUT / 'protected_before.json').write_text(json.dumps(before, indent=2) + '\n')
summary = []
for name, source, spec, method, route, extra in CASES:
    command = ['/usr/bin/python3', '-I', '-B', str(TOOL), str(SOURCES[source]),
               str(EMB / 'openapi-swagger' / (spec + '.json')),
               '--method', method, '--path', route, *extra, '--json']
    result = subprocess.run(command, capture_output=True, text=True, timeout=35, check=False)
    (OUT / (name + '.json')).write_text(result.stdout)
    (OUT / (name + '.stderr.txt')).write_text(result.stderr)
    if result.returncode:
        raise RuntimeError((name, result.returncode, result.stderr))
    data = json.loads(result.stdout)
    verified = all(h['snippet'] == (SOURCES[source] / h['file']).read_text(
        encoding='utf-8-sig').splitlines()[h['line'] - 1].strip()[:160] for h in data['hits'])
    assert verified, name
    summary.append({'case': name, 'command': command, 'returncode': result.returncode,
                    'verdict': data['independent_evidence'], 'scan': data['scan'],
                    'history': data['history'], 'locators_verified': verified,
                    'hit_counts': dict(collections.Counter(h['category'] for h in data['hits'])),
                    'independent_tests': sum(h['category'] == 'E-TEST' and h['independent'] for h in data['hits']),
                    'other_module_tests': sum(h['category'] == 'E-TEST' and h.get('module_scope') == 'other_module' for h in data['hits'])})
    print(name, data['independent_evidence'], summary[-1]['hit_counts'], flush=True)
(OUT / 'search_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
after = hashes()
assert before == after
(OUT / 'protected_check.json').write_text(json.dumps({'unchanged': before == after,
    'files': len(before), 'sha256': after}, indent=2) + '\n')
