"""Independent CSV and metadata audit. Run with /usr/bin/python3 -I -B."""
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P = ROOT / '08_experiments/E1_pilot/pilot_results'
RUNS = P.parent / 'runs'
EXPECTED = {'REQUEST_LOOSE': {'VALID_REJECTED'}, 'REQUEST_STRICT': {'INVALID_ACCEPTED'},
            'RESPONSE_ORACLE': {'RESPONSE_SCHEMA', 'UNDOCUMENTED_STATUS'},
            'METHOD_SEM': {'UNDOCUMENTED_OPERATION', 'UNDOCUMENTED_STATUS', 'VALID_REJECTED'}}
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def read(name):
    return list(csv.DictReader((P / name).open()))


def kinds(text):
    return {k: int(v) for k, v in (part.rsplit(':', 1) for part in text.split(';') if part)}


def inputs(run):
    files = sorted(p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut'))
    bases = {dict(line.split('=', 1) for line in p.read_text().splitlines())['baseline'] for p in files}
    check(len(bases) <= 1)
    return Path(next(iter(bases))).resolve() if bases else None


def boolean(text):
    check(text in ('True', 'False'))
    return text == 'True'


def totals(rows, fields):
    return {f: sum(boolean(r[f]) for r in rows) for f in fields} | {'n': len(rows)}


def main():
    fc, cross, controlled = (read(name + '.csv') for name in
                             ('fuzzer_compare', 'fuzzer_noise_cross_seed', 'fuzzer_controlled_cells'))
    source = {r['run']: r for r in fc}
    refs = {r['run']: r for r in cross}
    check(len(source) == len(fc) == len(refs) == len(cross))
    for r in fc:
        k = kinds(r['fresh_mut_kinds'])
        check(sum(k.values()) == int(r['fresh_mut_NEW_checkable']))
        check(sum(v for key, v in k.items() if key in EXPECTED[r['fault']]) == int(r['fresh_mut_NEW_expected']))
        meta = json.loads((RUNS / r['sut'] / r['run'] / 'run.json').read_text())
        check(meta['complete'] and not meta.get('strict_keywords') and not meta.get('code_mutation'))
    for r in cross:
        check(all(r[k] == v for k, v in source[r['run']].items()))
        check(boolean(r['beyond_ref_NEW_expected']) ==
              (int(r['fresh_mut_NEW_expected']) > int(r['noise_max_mut_NEW_expected'])))
        check(int(r['noise_max_mut_NEW_expected']) <= int(r['noise_max_mut_NEW_checkable']) <= int(r['noise_max_mut_NEW']))
    cells = defaultdict(lambda: defaultdict(list))
    for r in cross:
        cells[tuple(r[k] for k in ('sut', 'fault', 'severity', 'seed'))][r['fuzzer']].append(r)
    reconstructed = {}
    for key, fuzzers in cells.items():
        for e, s in itertools.product(fuzzers['evomaster'], fuzzers['schemathesis']):
            reconstructed[(e['run'], s['run'])] = {
                'primary': e['run'] == min(x['run'] for x in fuzzers['evomaster']) and
                           s['run'] == min(x['run'] for x in fuzzers['schemathesis']),
                'controlled': e['manifest_sig'] == s['manifest_sig']}
    check(len(reconstructed) == len(controlled))
    for r in controlled:
        expected = reconstructed[(r['evo_run'], r['sch_run'])]
        for k, v in expected.items():
            check(boolean(r[k]) == v)
        for short in ('evo', 'sch'):
            ref = refs[r[short + '_run']]
            check(r[short + '_kinds'] == ref['fresh_mut_kinds'])
            check(boolean(r[short + '_signal_expected']) ==
                  (int(ref['fresh_mut_NEW_expected']) > int(ref['noise_max_mut_NEW_expected'])))
    report = {'csv_rows': {'compare': len(fc), 'cross': len(cross), 'controlled': len(controlled)}}
    report['controlled_totals'] = {}
    for primary in (True, False):
        for ctl in (True, False):
            rows = [r for r in controlled if (not primary or boolean(r['primary'])) and boolean(r['controlled']) == ctl]
            report['controlled_totals'][f'primary={primary},controlled={ctl}'] = totals(
                rows, ['evo_signal', 'sch_signal', 'evo_signal_expected', 'sch_signal_expected'])
    old_path = Path('/tmp/claude-1000/-home-afridi-Documents-API-research/25df4c05-0198-49bf-857b-4f1d32399661/scratchpad/noise_floor_spec_before.csv')
    old = list(csv.DictReader(old_path.open()))
    noise = read('noise_floor_spec.csv')
    old_idx = {r['run']: r for r in old}
    check(set(old_idx) == {r['run'] for r in noise})
    common_diff = []
    for r in noise:
        common_diff.extend((r['run'], k) for k, v in old_idx[r['run']].items() if r[k] != v)
        check(int(r['signal_mut_NEW_expected']) == int(source[r['run']]['fresh_mut_NEW_expected']))
        check(int(r['signal_mut_NEW_checkable']) == int(source[r['run']]['fresh_mut_NEW_checkable']))
        for suffix in ('', '_checkable', '_expected'):
            check(boolean(r['exceeds_noise_NEW' + suffix]) ==
                  (int(r['signal_mut_NEW' + suffix]) > int(r['noise_max_mut_NEW' + suffix])))
    check(not common_diff)
    fields = ['exceeds_noise_NEW', 'exceeds_noise_NEW_checkable', 'exceeds_noise_NEW_expected']
    report['noise'] = {'old_source': str(old_path), 'old_source_sha256': hashlib.sha256(old_path.read_bytes()).hexdigest(),
                       'same_run_ids': True, 'all_old_cells_identical': True, 'totals': totals(noise, fields),
                       'loose': {sut: totals([r for r in noise if r['sut'] == sut and r['fault'] == 'REQUEST_LOOSE'], fields)
                                 for sut in sorted({r['sut'] for r in noise})}}
    metas = [(p.parent, json.loads(p.read_text())) for p in sorted(RUNS.glob('*/*/run.json'))]
    abl_batches = {r.name.split('_mutated_')[0] for r, m in metas if m.get('strict_keywords')}
    baselines = defaultdict(list)
    for r, m in metas:
        argv = r / 'schemathesis-argv.txt'
        if ('_baseline_NONE' in r.name and m.get('complete') and m.get('sut') in EXPECTED_SERVICE
                and argv.is_file() and 'data-generation-method' in argv.read_text() and '_e5_' not in r.name
                and r.name.split('_baseline_')[0] not in abl_batches):
            baselines[(m['sut'], m['seed'])].append(r.resolve())
    selected = []
    for r, m in metas:
        argv = r / 'schemathesis-argv.txt'
        if ('_mutated_' not in r.name or not m.get('complete') or m.get('sut') not in EXPECTED_SERVICE
                or not argv.is_file() or 'data-generation-method' not in argv.read_text() or m.get('strict_keywords')):
            continue
        base = inputs(r)
        if base is None:
            continue
        reps = [b for b in baselines[(m['sut'], m['seed'])] if b != base]
        if reps:
            selected.append(r.name)
            check(len(reps) == int(old_idx[r.name]['n_replicates']))
    check(set(selected) == set(old_idx))
    report['noise']['metadata_selector_same_61'] = len(selected) == 61
    report['noise']['replicate_counts_unchanged'] = True
    ablation, abk = read('strict_ablation.csv'), read('strict_ablation_kinds.csv')
    abki = {r['run']: r for r in abk}
    variant_counts = Counter()
    ab_meta = []
    for r in ablation:
        run, base = RUNS / 'market' / r['run'], RUNS / 'market' / r['baseline_run']
        m, b = json.loads((run / 'run.json').read_text()), json.loads((base / 'run.json').read_text())
        check(inputs(run) == base.resolve())
        check(('+'.join(m['strict_keywords']) if m.get('strict_keywords') else 'full') == r['variant'])
        check(m['complete'] and b['complete'] and not m.get('code_mutation'))
        check(m['seed'] == b['seed'] == int(r['seed']))
        def fuzzer(path, meta):
            return meta.get('fuzzer') or ('schemathesis' if (path / 'schemathesis-argv.txt').is_file() else None)
        check(fuzzer(run, m) == fuzzer(base, b) == r['fuzzer'])
        check(not b.get('strict_keywords'))
        check(m['fault'] == 'REQUEST_STRICT' and m['severity'] == 30 and b['fault'] == 'NONE')
        check(run.name.split('_mutated_')[0] == base.name.split('_baseline_')[0])
        provenance = ['sut_jar_sha256', 'source_sha256', 'images', 'emb_config_sha256', 'auth_source_sha256', 'schema_checks',
                      'budget_seconds', 'max_examples', 'request_timeout_ms', 'tool_sha256', 'harness_sha256']
        mismatches = [k for k in provenance if m.get(k) != b.get(k)]
        check(not mismatches)
        k = kinds(abki[r['run']]['kinds'])
        check(sum(k.values()) == int(r['fresh_mut_NEW_checkable']))
        check(k.get('INVALID_ACCEPTED', 0) == int(abki[r['run']]['new_INVALID_ACCEPTED']))
        variant_counts[(r['fuzzer'], r['variant'])] += 1
        peers = [q for q in base.parent.glob(base.name.rsplit('_s', 1)[0] + '_s*')
                 if q != base and (q / 'exchanges.jsonl').is_file() and json.loads((q / 'run.json').read_text()).get('complete')]
        check(len(peers) == 2)
        ab_meta.append({'run': r['run'], 'baseline': base.name, 'variant': r['variant'], 'peers': [q.name for q in sorted(peers)],
                        'fuzzer': r['fuzzer'], 'schema_checks': m.get('schema_checks'),
                        'schemathesis_exit': m.get('schemathesis_exit'), 'evomaster_exit': m.get('evomaster_exit'),
                        'harness_exit': m.get('harness_exit'),
                        'provenance_mismatches': mismatches})
    check(len(ablation) == 18 and set(variant_counts.values()) == {3})
    report['ablation'] = {'variant_counts': {str(k): v for k, v in variant_counts.items()}, 'metadata': ab_meta}
    report['checks'] = checks
    (OUT / 'recount.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'ablation'}, indent=2))


EXPECTED_SERVICE = {'scout-api', 'swagger-petstore', 'market', 'cwa-verification'}
if __name__ == '__main__':
    main()
