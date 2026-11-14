"""Cross-check result tables against raw artifacts and independent CSV sums."""
import collections
import csv
import hashlib
import json
import os
from pathlib import Path

root = Path.cwd()
out = Path(os.environ.get('T12_RESULTS_DIR', str(root / '08_experiments/E1_pilot/pilot_results')))
runs_root = root / '08_experiments/E1_pilot/runs/scout-api'
scratch = Path(os.environ.get('T12_BATCH_SCRATCH', str(root / '09_collab/logs/T12_scratch')))


def rows(name):
    with (out / name).open() as handle:
        return list(csv.DictReader(handle))


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


runs = rows('runs.csv')
assert len(runs) == 7
assert collections.Counter((r['mode'], r['fault'], int(r['seed'])) for r in runs) == collections.Counter(
    [('baseline', 'NONE', s) for s in (1, 2, 3)] + [('mutated', f, 1) for f in ('REQUEST_LOOSE', 'REQUEST_STRICT', 'RESPONSE_ORACLE', 'METHOD_SEM')])
status = rows('status_codes.csv'); operations = rows('operations.csv'); kinds = rows('violations_by_kind.csv')
comparison = rows('fault_comparison.csv'); details = rows('attribution_details.csv')
assert len(comparison) == 4 * 2 * 2 * 3
metadata = []
for row in runs:
    rid = row['run_id']; directory = runs_root / rid
    meta = json.loads((directory / 'run.json').read_text()); metadata.append(meta)
    exchanges = lines(directory / 'exchanges.jsonl')
    response_count = sum(isinstance(e.get('response'), dict) and 'status' in e['response'] for e in exchanges)
    assert len(exchanges) == int(row['exchanges'])
    assert response_count == int(row['response_exchanges'])
    assert sum(int(r['exchanges']) for r in status if r['run_id'] == rid) == response_count
    assert sum(int(r['exchanges']) for r in operations if r['run_id'] == rid) == response_count
    assert sum(r['documented_in_original'] == 'True' for r in operations if r['run_id'] == rid) == int(row['unique_operations_hit_original'])
    assert int(meta['budget_seconds']) == 600 and meta['max_examples'] == int(os.environ.get('T12_EXPECTED_EXAMPLES', '100'))
    assert meta['base_path'] == '/api' and meta['health_path'] == '/admin/healthcheck'
    for policy in ('default', 'strict'):
        vs = lines(out / f'{rid}.{policy}.violations.jsonl')
        selected = [r for r in kinds if r['run_id'] == rid and r['policy'] == policy]
        total = next(r for r in selected if r['kind'] == 'ALL')
        assert int(total['occurrences']) == len(vs)
        assert int(total['unique_fingerprints']) == len({v['fingerprint'] for v in vs})
        assert sum(int(r['occurrences']) for r in selected if r['kind'] != 'ALL') == len(vs)
        assert int(total['probe_occurrences']) + int(total['nonprobe_occurrences']) == len(vs)
    for name, expected in meta['file_sha256'].items():
        path = directory / name
        assert path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == expected, (rid, name)
for key in ('sut', 'sut_jar_sha256', 'emb_commit', 'source_sha256', 'base_path', 'auth', 'max_examples', 'budget_seconds', 'schemathesis_image', 'logger_max_body', 'tool_sha256', 'harness_sha256'):
    assert all(m[key] == metadata[0][key] for m in metadata), key
image_ids = {key: sorted({m['images'][key]['id'] for m in metadata}) for key in ('schema-image', 'sut-scout-api-image', 'mitmproxy-image')}
images_stable = all(len(ids) == 1 for ids in image_ids.values())
assert images_stable or os.environ.get('T12_ALLOW_IMAGE_VARIATION') == '1', image_ids
for row in comparison:
    selected = [d for d in details if all(d[k] == row[k] for k in ('run_id', 'policy', 'mode', 'status'))]
    assert len(selected) == int(row['unique_fingerprints'])
    assert sum(d['op_mutated'] == 'True' for d in selected) == int(row['on_mutated_op_explained_locality'])
    assert int(row['on_mutated_op_explained_locality']) + int(row['outside_mutated_op_unexplained']) == len(selected)
    if row['mode'] == 'fresh' and row['status'] in ('NEW', 'VANISHED'):
        assert all(d['label_L1'] in ('NEEDS_MANUAL', 'UNEXPLAINED') for d in selected)
    if row['mode'] == 'replay' and row['status'] == 'NEW':
        assert all(d['expected_label_match_new_only'] == 'True' for d in selected if d['op_mutated'] == 'True')
    if row['mode'] == 'replay' and row['status'] == 'VANISHED':
        assert all(d['label_L1'] == 'MASKED' for d in selected if d['op_mutated'] == 'True')
assert all(r['matches_metadata'] == 'True' for r in rows('artifact_integrity.csv'))
summary = {'result': 'PASS' if images_stable else 'RAW_AUDIT_PASS_IMAGE_IDS_INCOMPATIBLE', 'runs_checked': len(runs), 'comparison_groups_checked': len(comparison), 'attribution_rows_checked': len(details), 'all_recorded_artifact_hashes_match': True, 'tool_and_harness_hashes_stable': True, 'images_stable': images_stable, 'image_ids': image_ids, 'budget_example_and_path_settings_match': True, 'auth_roles': sorted({m['auth'] for m in metadata}), 'csv_sums_match_raw_artifacts': True}
(scratch / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
