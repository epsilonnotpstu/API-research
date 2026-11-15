"""Validate delivered artifacts and record final read-only input hashes."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
S = Path(__file__).resolve().parent
P = ROOT / '08_experiments/E1_pilot/pilot_results'
report = ROOT / '09_collab/reports/T39_review.md'
text = report.read_text()
assert re.findall(r'^### (F\d+) — (P\d):', text, re.M) == [('F1', 'P1'), ('F2', 'P2'), ('F3', 'P2'), ('F4', 'P3')]
assert all(word in text for word in ['20/26', '10/19', '8/19', '34/61', '44/61', '6/25', 'Suggested fix', 'Evidence'])
r = json.loads((S / 'recount.json').read_text())
assert r['checks'] == 2971 and r['noise']['all_old_cells_identical'] and r['noise']['metadata_selector_same_61']
assert len(r['ablation']['metadata']) == 18
sch = [x for x in r['ablation']['metadata'] if x['fuzzer'] == 'schemathesis']
assert {x['schema_checks'] for x in sch if x['variant'] == 'full'} == {'response_headers_conformance'}
assert {x['schema_checks'] for x in sch if x['variant'] != 'full'} == {'all'}
assert {x['schemathesis_exit'] for x in sch if x['variant'] != 'full'} == {'1'}
loose = json.loads((S / 'loose_real_data.json').read_text())
assert (loose['runs'], loose['NEW'], loose['raw_mutated_NEW'], loose['with_same_kind_op_VANISHED']) == (7, 13, 14, 0)
market = json.loads((S / 'market.json').read_text())
assert market['traffic_rows_verified'] == 18 and len(market['HAL_examples']) == 3
assert [x['NEW_INVALID_ACCEPTED_fps'] for x in market['evo_noreq']] == [2, 0, 2]
assert [x['NEW_INVALID_ACCEPTED_occurrences'] for x in market['evo_noreq']] == [60, 0, 74]
for x in market['HAL_examples']:
    log = ROOT / '08_experiments/E1_pilot/runs/market' / x['run'] / 'compose.log'
    lines = log.read_text().splitlines()
    assert 'RestErrorResponse' in lines[x['compose_locators']['handler'] - 1]
    assert x['dto'] + '["_links"]' in lines[x['compose_locators']['dto'] - 1]
    assert 'JsonParseException: Expected relation name' in lines[x['compose_locators']['json_parse_exception'] - 1]

protected = [P / (name + ext) for name, exts in {
    'fuzzer_compare': ('.py', '.csv'), 'fuzzer_noise_cross_seed': ('.py', '.csv'),
    'fuzzer_controlled_cells': ('.py', '.csv'), 'strict_ablation': ('.py', '.csv'),
    'strict_ablation_kinds': ('.py', '.csv'), 'noise_floor_spec': ('.py', '.csv')}.items() for ext in exts]
protected += [P / n for n in ('FUZZER_COMPARE.md', 'STRICT_ABLATION.md', 'NOISE_FLOOR_SPEC.md', 'PILOT_SUMMARY.md')]
protected += [ROOT / '08_experiments/tools' / n for n in ('specmut.py', 'conformance.py', 'attribute.py')]
for row in csv.DictReader((P / 'strict_ablation.csv').open()):
    for key in ('run', 'baseline_run'):
        d = ROOT / '08_experiments/E1_pilot/runs/market' / row[key]
        protected += [d / n for n in ('run.json', 'manifest.json', 'exchanges.jsonl') if (d / n).is_file()]
protected = sorted(set(protected))
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
(S / 'final_input_sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
scanned = []
for p in sorted(S.glob('*')) + [report]:
    if not p.is_file() or p.suffix not in ('.py', '.json', '.md', '.txt'):
        continue
    content = p.read_text()
    assert not re.search(r'\b(?:Basic|Bearer)\s+[A-Za-z0-9+/=_-]{8,}', content), p.name
    assert not re.search(r'(?im)^\s*(?:Authorization|Cookie)\s*:', content), p.name
    if p.suffix == '.py':
        compile(content, str(p), 'exec')
    scanned.append(str(p.relative_to(ROOT)))
log = (ROOT / '09_collab/logs/kindfilter/fuzzer_controlled_cells.log').read_text()
assert 'TOTAL | EvoMaster 20/26 | Schemathesis 20/26' in log
assert 'TOTAL | EvoMaster 10/19 | Schemathesis 8/19' in log
result = {'status': 'PASS', 'csv_metadata_checks': r['checks'], 'report_findings': 4,
          'final_input_hash_count': len(hashes), 'hash_scope': 'Final inventory; not a start-of-task freeze.',
          'loose_selected_kinds': 13, 'loose_raw': 14, 'loose_identity_partners': 0,
          'market_rows': 18, 'HAL_representatives': 3, 'secret_pattern_scan_files': len(scanned),
          'report_sha256': hashlib.sha256(report.read_bytes()).hexdigest()}
(S / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
