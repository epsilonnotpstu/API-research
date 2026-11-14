"""Summarize only T12 batch records using the unchanged local checker."""
import collections
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
SCRATCH = Path(os.environ.get('T12_BATCH_SCRATCH', str(ROOT / '09_collab/logs/T12_scratch')))
OUT = Path(os.environ.get('T12_RESULTS_DIR', str(ROOT / '08_experiments/E1_pilot/pilot_results')))
RUNS = ROOT / '08_experiments/E1_pilot/runs/scout-api'
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import conformance
import attribute
import specmut


def write_csv(name, rows, fields):
    with (OUT / name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    OUT.mkdir(exist_ok=True)
    snapshot = json.loads((SCRATCH / 'batch_tool_sha256.json').read_text())
    current = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / '08_experiments/tools').glob('*.py')}
    assert snapshot == current, 'Tools changed after collection'
    events = [e for e in jsonl(SCRATCH / 'batch_events.jsonl') if e['stage'] == 'run' and 'run_id' in e]
    data = {}; summaries = []; statuses = []; operations = []; kinds = []; strict_only = []
    coverage = []; integrity = []; generator_findings = []
    for event in events:
        directory = RUNS / event['run_id']; rid = directory.name
        meta = json.loads((directory / 'run.json').read_text())
        assert meta['tool_sha256'] == snapshot, rid + ' tool provenance mismatch'
        for name in ('exchanges.jsonl', 'spec.test.json', 'manifest.json'):
            path = directory / name
            if path.exists():
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                valid = actual == meta['file_sha256'].get(name)
                integrity.append({'run_id': rid, 'file': name, 'sha256': actual, 'matches_metadata': valid})
                assert valid, rid + '/' + name + ' changed'
        exchanges = jsonl(directory / 'exchanges.jsonl')
        raw = specmut.load_spec(str(next(directory.glob('spec.test.*'))))
        original_raw = specmut.load_spec(str(next(directory.glob('spec.original.*'))))
        original = conformance.Spec(original_raw)
        response_exchanges = [e for e in exchanges if isinstance(e.get('response'), dict) and 'status' in e['response']]
        probe_indices = {i for i, e in enumerate(response_exchanges) if 'x-schemathesis-probe' in {k.lower() for k in e['request'].get('headers', {})}}
        status_count = collections.Counter(str(e['response']['status']) for e in response_exchanges)
        for status, count in sorted(status_count.items()):
            statuses.append({'run_id': rid, 'status': status, 'exchanges': count})
        operation_count = collections.Counter()
        paths = collections.Counter()
        for e in response_exchanges:
            request = e['request']; method = request['method'].upper()
            template, _ = original.match(request['path'], method, request.get('origin'))
            documented = bool(template and original.operation(template, method)[0] is not None)
            operation_count[(method, template or request['path'], documented)] += 1
            paths[request['path']] += 1
        for (method, template, documented), count in sorted(operation_count.items()):
            operations.append({'run_id': rid, 'method': method, 'template': template, 'documented_in_original': documented, 'exchanges': count})
        original_total = sum(1 for _ in specmut.operations(original_raw))
        junit = {'tests': '', 'failures': '', 'errors': '', 'skipped': '', 'time': ''}
        junit_path = directory / 'schemathesis.junit.xml'
        if junit_path.exists():
            try:
                node = ET.parse(junit_path).getroot()
                for testcase in node.iter('testcase'):
                    for finding in testcase:
                        if finding.tag in ('failure', 'error', 'skipped'):
                            generator_findings.append({'run_id': rid, 'testcase': testcase.get('name', ''), 'outcome': finding.tag, 'type': finding.get('type', ''), 'message': finding.get('message', ''), 'text': finding.text or '', 'evidence': str(junit_path.relative_to(ROOT))})
                suites = [node] if node.tag == 'testsuite' else list(node.findall('testsuite'))
                for key in junit:
                    junit[key] = sum(float(s.attrib.get(key, '0')) for s in suites)
            except ET.ParseError:
                junit['errors'] = 'unparseable'
        row = {'run_id': rid, 'mode': meta['mode'], 'fault': meta['fault'], 'seed': meta['seed'],
               'budget_seconds': meta['budget_seconds'], 'auth_role': meta['auth'], 'max_examples': meta['max_examples'], 'request_timeout_ms': meta.get('request_timeout_ms', ''), 'hypothesis_phases': meta.get('hypothesis_phases', ''), 'wall_seconds': event['elapsed_seconds'],
               'utc_span_seconds': round((datetime.datetime.fromisoformat(meta['finished_at']) - datetime.datetime.fromisoformat(meta['started_at'].replace('Z', '+00:00'))).total_seconds(), 3),
               'phase': meta['phase'], 'harness_exit': meta['harness_exit'], 'schemathesis_exit': meta['schemathesis_exit'],
               'complete': meta['complete'], 'exchanges': len(exchanges), 'response_exchanges': len(response_exchanges), 'schemathesis_probe_records': len(probe_indices),
               'transport_records': len(exchanges) - len(response_exchanges),
               'captured_response_span_seconds': round(response_exchanges[-1]['ts'] - response_exchanges[0]['ts'], 3) if len(response_exchanges) > 1 else 0,
               'maximum_between_response_gap_seconds': round(max((b['ts'] - a['ts'] for a, b in zip(response_exchanges, response_exchanges[1:])), default=0), 3),
               'unique_operations_hit_original': sum(documented for _, _, documented in operation_count),
               'original_operations_total': original_total, 'distinct_method_paths': len(operation_count),
               'response_truncated': sum(bool(e['response'].get('body', {}).get('truncated')) for e in response_exchanges),
               'request_truncated': sum(bool(e['request'].get('body', {}).get('truncated')) for e in response_exchanges),
               'junit_tests': junit['tests'], 'junit_failures': junit['failures'], 'junit_errors': junit['errors'],
               'junit_skipped': junit['skipped'], 'junit_seconds': junit['time'],
               'jacoco_bytes': (directory / 'jacoco.exec').stat().st_size if (directory / 'jacoco.exec').exists() else 0,
               'coverage_exit': meta['coverage_exit'], 'cleanup_exit': meta['cleanup_exit'], 'evidence': str((directory / 'run.json').relative_to(ROOT))}
        summaries.append(row)
        coverage.append({'run_id': rid, 'jacoco_bytes': row['jacoco_bytes'], 'dump_exit': meta['coverage_exit'], 'covered_lines': '', 'total_lines': '', 'line_coverage': '', 'reason': 'Skipped: authorized reviewed harness supports JaCoCo dump only; standalone jar extraction/java report outside T12 exact external execution allowlist (tasks/T12.md Authorization).', 'evidence': row['evidence']})
        checks = {}
        for policy in ('default', 'strict'):
            spec = conformance.Spec(raw, strict_additional=(policy == 'strict'))
            violations = []
            with (OUT / f'{rid}.{policy}.violations.jsonl').open('w') as output:
                for index, exchange in enumerate(response_exchanges):
                    for v in conformance.check(spec, exchange):
                        v['exchange'] = index
                        output.write(json.dumps(v, ensure_ascii=False) + '\n')
                        violations.append(v)
            checks[policy] = violations
            counts = collections.Counter(v['kind'] for v in violations)
            for kind in sorted(set(counts) | {'ALL'}):
                selected = violations if kind == 'ALL' else [v for v in violations if v['kind'] == kind]
                kinds.append({'run_id': rid, 'policy': policy, 'kind': kind, 'occurrences': len(selected), 'unique_fingerprints': len({v['fingerprint'] for v in selected}), 'exchanges_affected': len({v['exchange'] for v in selected}), 'probe_occurrences': sum(v['exchange'] in probe_indices for v in selected), 'nonprobe_occurrences': sum(v['exchange'] not in probe_indices for v in selected), 'nonprobe_unique_fingerprints': len({v['fingerprint'] for v in selected if v['exchange'] not in probe_indices})})
        default_ids = {(v['exchange'], v['fingerprint']) for v in checks['default']}
        extras = [v for v in checks['strict'] if (v['exchange'], v['fingerprint']) not in default_ids]
        for kind, count in sorted(collections.Counter(v['kind'] for v in extras).items()):
            strict_only.append({'run_id': rid, 'kind': kind, 'occurrences': count, 'unique_fingerprints': len({v['fingerprint'] for v in extras if v['kind'] == kind}), 'interpretation': 'TEST/T-ORACLE-STRICT for additionalProperties-only policy violations; inspect details for any other delta', 'codebook': '08_experiments/R1_triage_codebook.md:177-183'})
        data[rid] = {'meta': meta, 'exchanges': response_exchanges, 'checks': checks, 'raw': raw, 'directory': directory}
        print(json.dumps({'summarized': rid, 'exchanges': len(exchanges)}), flush=True)
    if summaries:
        write_csv('runs.csv', summaries, list(summaries[0]))
    write_csv('status_codes.csv', statuses, ['run_id', 'status', 'exchanges'])
    write_csv('operations.csv', operations, ['run_id', 'method', 'template', 'documented_in_original', 'exchanges'])
    write_csv('violations_by_kind.csv', kinds, ['run_id', 'policy', 'kind', 'occurrences', 'unique_fingerprints', 'exchanges_affected', 'probe_occurrences', 'nonprobe_occurrences', 'nonprobe_unique_fingerprints'])
    write_csv('strict_only.csv', strict_only, ['run_id', 'kind', 'occurrences', 'unique_fingerprints', 'interpretation', 'codebook'])
    write_csv('coverage.csv', coverage, ['run_id', 'jacoco_bytes', 'dump_exit', 'covered_lines', 'total_lines', 'line_coverage', 'reason', 'evidence'])
    write_csv('artifact_integrity.csv', integrity, ['run_id', 'file', 'sha256', 'matches_metadata'])
    write_csv('schemathesis_findings.csv', generator_findings, ['run_id', 'testcase', 'outcome', 'type', 'message', 'text', 'evidence'])
    baseline = {d['meta']['seed']: (rid, d) for rid, d in data.items() if d['meta']['mode'] == 'baseline'}
    variable = []; variability_summary = []
    for policy in ('default', 'strict'):
        sets = {seed: {v['fingerprint'] for v in d['checks'][policy]} for seed, (_, d) in baseline.items()}
        if len(sets) != 3:
            continue
        union = set.union(*sets.values()); shared = set.intersection(*sets.values())
        for fp in sorted(union):
            seeds = [seed for seed, values in sorted(sets.items()) if fp in values]
            variable.append({'policy': policy, 'fingerprint': fp, 'seed_count': len(seeds), 'seeds': ';'.join(map(str, seeds)), 'category': 'all_three' if len(seeds) == 3 else 'seed_specific' if len(seeds) == 1 else 'two_seeds'})
        variability_summary.append({'policy': policy, 'union': len(union), 'all_three': len(shared), 'seed_specific': sum(sum(fp in values for values in sets.values()) == 1 for fp in union), 'two_seeds': sum(sum(fp in values for values in sets.values()) == 2 for fp in union), 'variable_fraction': (len(union) - len(shared)) / len(union) if union else 0, 'all_baselines_complete': all(d['meta']['complete'] for _, d in baseline.values()), 'interpretation': 'Observed seed/run variability; not a pure nondeterminism or causal estimate'})
    write_csv('baseline_variability.csv', variable, ['policy', 'fingerprint', 'seed_count', 'seeds', 'category'])
    write_csv('baseline_variability_summary.csv', variability_summary, ['policy', 'union', 'all_three', 'seed_specific', 'two_seeds', 'variable_fraction', 'all_baselines_complete', 'interpretation'])
    comparisons = []; details = []; exposure = []
    if 1 in baseline:
        base_id, base = baseline[1]
        for rid, mut in data.items():
            if mut['meta']['mode'] != 'mutated':
                continue
            manifest = json.loads((mut['directory'] / 'manifest.json').read_text())
            mutated_ops = set()
            for mutation in manifest['mutations']:
                mutated_ops.add((mutation['method'].upper(), mutation['path']))
                if mutation['fault'] == 'METHOD_SEM':
                    mutated_ops.update((str(edit['after']).upper(), mutation['path']) for edit in mutation['edits'])
            for cohort, observed in (('baseline_s1', base), ('fresh_mutated', mut)):
                op_hits = collections.Counter()
                source = conformance.Spec(base['raw'])
                for exchange in observed['exchanges']:
                    request = exchange['request']
                    template, _ = source.match(request['path'], request['method'], request.get('origin'))
                    op_hits[(request['method'].upper(), template or request['path'])] += 1
                for method, template in sorted(mutated_ops):
                    exposure.append({'run_id': rid, 'fault': mut['meta']['fault'], 'cohort': cohort, 'method': method, 'template': template, 'captured_responses': op_hits[(method, template)], 'manifest_operations_mutated': manifest['operations_mutated'], 'original_operations_total': manifest['operations_total'], 'requested_severity': manifest['severity']})
            for policy in ('default', 'strict'):
                replay = []
                checker = conformance.Spec(mut['raw'], strict_additional=(policy == 'strict'))
                for index, exchange in enumerate(base['exchanges']):
                    for v in conformance.check(checker, exchange):
                        v['exchange'] = index; replay.append(v)
                with (OUT / f'{rid}.{policy}.replay.violations.jsonl').open('w') as output:
                    for v in replay:
                        output.write(json.dumps(v, ensure_ascii=False) + '\n')
                for mode, values in (('replay', replay), ('fresh', mut['checks'][policy])):
                    rows = attribute.attribute(base['checks'][policy], values, manifest, mode=mode)
                    # The harness refuses incomplete pairs. These are explicitly separate partial audits.
                    pair_complete = bool(base['meta']['complete'] and mut['meta']['complete'])
                    for row in rows:
                        actual_expected = (row['label_L1'], row['label_L2']) == (row['expected_if_injected'], row['expected_L2_if_injected']) if mode == 'replay' and row['status'] == 'NEW' and row['op_mutated'] else ''
                        details.append({'run_id': rid, 'baseline_id': base_id, 'policy': policy, 'pair_complete': pair_complete, 'expected_label_match_new_only': actual_expected, **row})
                    for status in ('NEW', 'VANISHED', 'PERSISTENT'):
                        selected = [r for r in rows if r['status'] == status]
                        on_op = [r for r in selected if r['op_mutated']]
                        matches = sum((r['label_L1'], r['label_L2']) == (r['expected_if_injected'], r['expected_L2_if_injected']) for r in on_op) if status == 'NEW' and mode == 'replay' else ''
                        comparisons.append({'run_id': rid, 'baseline_id': base_id, 'fault': mut['meta']['fault'], 'policy': policy, 'mode': mode, 'status': status, 'unique_fingerprints': len(selected), 'on_mutated_op_explained_locality': len(on_op), 'outside_mutated_op_unexplained': len(selected) - len(on_op), 'expected_label_matches_new_replay': matches, 'expected_label_tested_new_replay': len(on_op) if status == 'NEW' and mode == 'replay' else '', 'pair_complete': pair_complete, 'operations_mutated': manifest['operations_mutated'], 'interpretation': 'Locality is not causality; replay NEW labels are assigned from manifest, not independent classifier validation'})
    fields = ['run_id', 'baseline_id', 'fault', 'policy', 'mode', 'status', 'unique_fingerprints', 'on_mutated_op_explained_locality', 'outside_mutated_op_unexplained', 'expected_label_matches_new_replay', 'expected_label_tested_new_replay', 'pair_complete', 'operations_mutated', 'interpretation']
    write_csv('fault_comparison.csv', comparisons, fields)
    write_csv('mutation_exposure.csv', exposure, ['run_id', 'fault', 'cohort', 'method', 'template', 'captured_responses', 'manifest_operations_mutated', 'original_operations_total', 'requested_severity'])
    if details:
        write_csv('attribution_details.csv', details, list(details[0]))
    summary = {'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'run_ids': list(data), 'tools_unchanged': current == snapshot, 'runs_complete': sum(d['meta']['complete'] for d in data.values()), 'runs_attempted': len(data), 'baseline_variability': variability_summary, 'external_coverage_report_executed': False, 'tool_sha256': current, 'summary_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__':
    main()
