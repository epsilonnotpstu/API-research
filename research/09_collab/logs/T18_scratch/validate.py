"""Validate T18 item coverage, replay, aggregation, evidence, and provenance."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay import OUT, ROOT, RUN, save, normalize
from write_labels import LABELS, ROOTS, HEADERS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with LABELS.open() as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == HEADERS
        rows = list(reader)
    with ROOTS.open() as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['root_cause_id', 'description', 'fix_site', 'items']
        roots = list(reader)
    blind = list(csv.DictReader((ROOT / '08_experiments/E2_labelling/cwa-verification_baseline_s1_blind.csv').open()))
    assert [r['item_id'] for r in rows] == [r['item_id'] for r in blind] == [f'C{i:03d}' for i in range(1, 7)]
    cases = json.loads((OUT / 'case_labels.json').read_text())
    cli = [json.loads(s) for s in (OUT / 'replay_cli.jsonl').read_text().splitlines()]
    fp_map = {normalize(b['fingerprint']): b['item_id'] for b in blind}
    replay = [(fp_map[d['fingerprint']], d['exchange'] + 1) for d in cli]
    assert collections.Counter(replay) == collections.Counter((c['item_id'], c['exchange_line']) for c in cases)
    assert len(replay) == 430
    assert len({line for iid, line in replay}) == 430
    root_map = {r['root_cause_id']: r for r in roots}
    assert len(root_map) == len(roots) == 7
    locator_count = 0
    evidence_files = set()

    def locator(value):
        nonlocal locator_count
        match = re.fullmatch(r'(.+):(\d+)', value)
        assert match, value
        rel, n = match.group(1), int(match.group(2))
        path = ROOT / rel
        assert 'labels_A' not in path.name
        assert not ('pilot_results' in path.parts and 'RESULTS' in path.name)
        text = path.read_text().splitlines()
        assert 1 <= n <= len(text) and text[n - 1].strip(), value
        evidence_files.add(rel)
        locator_count += 1

    for r, b in zip(rows, blind):
        iid = r['item_id']
        children = [c for c in cases if c['item_id'] == iid]
        assert len(children) == int(b['occurrences'])
        leaf_labels = {c['L1'] for c in children}
        expected = 'SPEC_PARTIAL' if leaf_labels == {'SPEC', 'TEST'} else next(iter(leaf_labels))
        assert r['L1'] == expected
        assert r['L1'] != 'BOTH' and r['both_candidate'] == 'false'
        assert r['confidence'] == '3'
        assert r['rationale'].startswith('⚠️') and len(r['rationale'].split()) <= 30
        assert r['L2'] in ('', 'S-REQ-LOOSE', 'S-RESP-MISSING')
        assert not (r['L2'] and r['proposed_L2'])
        declared_roots = set(r['root_cause_id'].split(';'))
        assert declared_roots == {rid for c in children for rid in c['root_cause_ids']}
        assert all(iid in root_map[rid]['items'].split(';') for rid in declared_roots)
        locs = r['evidence_locators'].split(';')
        assert {f'{RUN.relative_to(ROOT)}/exchanges.jsonl:{c["exchange_line"]}' for c in children} <= set(locs)
        for loc in locs:
            locator(loc)
    for r in roots:
        rid = r['root_cause_id']
        assert r['fix_site'] in ('test', 'spec')
        assert set(r['items'].split(';')) == {row['item_id'] for row in rows if rid in row['root_cause_id'].split(';')}
        for path, line in re.findall(r'((?:08_experiments|09_collab)/[A-Za-z0-9_./-]+):(\d+)', r['description']):
            locator(f'{path}:{line}')
    inputs = json.loads((OUT / 'input_sha256.json').read_text())
    assert all(digest(ROOT / rel) == sha for rel, sha in inputs.items())
    count = collections.Counter(c['L1'] for c in cases if c['item_id'] == 'C002')
    assert count == {'SPEC': 62, 'TEST': 7}
    bad = [c['exchange_line'] for c in cases if c['item_id'] == 'C002' and c['L1'] == 'TEST']
    assert bad == [164, 188, 189, 190, 191, 192, 193]
    spec = json.loads((RUN / 'spec.original.json').read_text())
    request_schema = spec['components']['schemas']['RegistrationTokenRequest']
    assert 'required' not in request_schema
    assert all('pattern' not in value for value in request_schema['properties'].values())
    log_locations = json.loads((OUT / 'log_locations.json').read_text())
    assert len(log_locations['capture_encoding_error']) == 71
    assert len(log_locations['firewall_error']) == 2
    result = {'status': 'PASS', 'items': 6, 'captured_exchanges': 430, 'diagnostic_cases': 430,
              'exact_CLI_replay': True, 'per_item_counts_exact': True,
              'L1': dict(collections.Counter(r['L1'] for r in rows)),
              'case_L1': dict(collections.Counter(c['L1'] for c in cases)),
              'C002_leaf_labels': dict(count), 'C002_invalid_HTTP_lines': bad,
              'root_rows': len(roots), 'both_candidates': 0,
              'evidence_locators_checked': locator_count,
              'distinct_evidence_files': len(evidence_files),
              'max_rationale_words': max(len(r['rationale'].split()) for r in rows),
              'input_hashes_checked': len(inputs), 'inputs_unchanged': True,
              'exact_request_log_identity_joins_claimed': False,
              'blinding': {'labels_A_opened': False, 'pilot_RESULTS_reports_opened': False,
                           'board_used_as_label_evidence': False},
              'execution_boundary': {'external_code_or_SUT_executed': False,
                                     'harness_or_tools_written': False, 'runs_written': False,
                                     'basis': 'operator record of this task; read-only input hashes also checked'}}
    save('validation.json', result)
    # The final freeze overwrites this placeholder only after all report citations are checked.
    save('freeze.json', {'status': 'pending final SHA-256 freeze'})
    report = ROOT / '09_collab/reports/T18_report.md'
    cites = re.findall(r'`((?:08_experiments|09_collab)/[^`]+):(\d+)`', report.read_text())
    for path, line in cites:
        locator(f'{path}:{line}')
    result['report_citations_checked'] = len(cites)
    save('validation.json', result)
    manifest_paths = [LABELS, ROOTS, report] + sorted(OUT.glob('*.py'))
    manifest_paths += [OUT / name for name in ['replay_summary.json', 'case_labels.json', 'case_summary.json',
                                              'label_summary.json', 'log_locations.json', 'input_sha256.json',
                                              'replay_cli.jsonl', 'validation.json']]
    save('sha256_manifest.json', {str(p.relative_to(ROOT)): digest(p) for p in manifest_paths})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
