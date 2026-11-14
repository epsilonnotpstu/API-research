"""Independent CSV recount and read-only provenance audit. Run with python3 -I -B."""
import csv
import hashlib
import json
import re
import shlex
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RESULTS = ROOT / '08_experiments/E1_pilot/pilot_results'
RUNS = RESULTS.parent / 'runs'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inputs(p):
    return dict(line.split('=', 1) for line in p.read_text().splitlines())


def method(run, meta):
    if meta.get('fuzzer') == 'evomaster':
        return 'evomaster'
    p = run / 'schemathesis-argv.txt'
    if not p.is_file():
        return None
    args = shlex.split(p.read_text())
    for i, arg in enumerate(args):
        if arg == '--data-generation-method':
            return 'schemathesis:' + args[i + 1]
        if arg.startswith('--data-generation-method='):
            return 'schemathesis:' + arg.split('=', 1)[1]
    return None


def main():
    files = ['fuzzer_compare.py', 'fuzzer_compare.csv', 'fuzzer_noise_cross_seed.py',
             'fuzzer_noise_cross_seed.csv', 'FUZZER_COMPARE.md', 'noise_floor_spec.py']
    hashes = {str(RESULTS / f): digest(RESULTS / f) for f in files}
    compare = list(csv.DictReader((RESULTS / files[1]).open()))
    noise = list(csv.DictReader((RESULTS / files[3]).open()))
    by_run = {r['run']: r for r in compare}
    groups = defaultdict(list)
    assertions = []
    for r in noise:
        groups[(r['sut'], r['fault'], r['fuzzer'], int(r['severity']))].append(r)
        assert r['beyond_noise_NEW'] in ('True', 'False')
        assert (r['beyond_noise_NEW'] == 'True') == (int(r['fresh_mut_NEW']) > int(r['noise_max_mut_NEW']))
        assert all(r[k] == v for k, v in by_run[r['run']].items())
    table = []
    for k, rs in sorted(groups.items()):
        table.append(dict(zip(('sut', 'fault', 'fuzzer', 'severity'), k),
                          numerator=sum(r['beyond_noise_NEW'] == 'True' for r in rs), denominator=len(rs)))
    matched = {}
    for fuzzer in ('evomaster', 'schemathesis'):
        rs = [r for r in noise if r['fuzzer'] == fuzzer and int(r['severity']) == 30
              and r['sut'] in ('market', 'swagger-petstore', 'cwa-verification')
              and (r['sut'], r['fault']) != ('cwa-verification', 'REQUEST_LOOSE')]
        matched[fuzzer] = [sum(r['beyond_noise_NEW'] == 'True' for r in rs), len(rs)]
    traffic = []
    for key in sorted({(r['sut'], r['fuzzer']) for r in compare}):
        rs = [r for r in compare if (r['sut'], r['fuzzer']) == key]
        faults = defaultdict(list)
        for r in rs:
            faults[(r['fault'], r['severity'])].append(int(r['mutated_exchanges']))
        traffic.append({'sut': key[0], 'fuzzer': key[1], 'n': len(rs),
                        'mean': sum(int(r['mutated_exchanges']) for r in rs) / len(rs),
                        'min': min(int(r['mutated_exchanges']) for r in rs),
                        'max': max(int(r['mutated_exchanges']) for r in rs),
                        'cell_means': {str(k): sum(v) / len(v) for k, v in sorted(faults.items())}})
    all_runs, selected, excluded = [], [], []
    for p in sorted(RUNS.glob('*/*mutated_*/run.json')):
        m = json.loads(p.read_text())
        run = p.parent
        identity = method(run, m)
        ins = list(run.glob('analysis-*/inputs.txt'))
        eligible = [i for i in ins if not i.parent.name.endswith('-sut')]
        record = {'run': run.name, 'sut': m['sut'], 'complete': m.get('complete'),
                  'classification': identity, 'csv_included': run.name in by_run,
                  'inputs': {i.parent.name: inputs(i) for i in ins}}
        all_runs.append(record)
        if run.name not in by_run:
            excluded.append(record)
            continue
        row = by_run[run.name]
        assert m.get('complete') and identity in ('evomaster', 'schemathesis:all')
        assert len({inputs(i)['baseline'] for i in eligible}) == 1
        base = Path(inputs(eligible[0])['baseline']).resolve()
        b = json.loads((base / 'run.json').read_text())
        assert b['complete'] and b['mode'] == 'baseline'
        assert all(m[k] == b[k] for k in ('sut', 'seed', 'fuzzer') if k in m or k in b)
        pair_keys = ('sut_jar_sha256', 'emb_commit', 'source_sha256', 'base_path', 'auth',
                     'max_examples', 'budget_seconds', 'schemathesis_image', 'logger_max_body',
                     'request_timeout_ms', 'hypothesis_phases', 'schema_checks', 'sut_service',
                     'sut_image', 'internal_port', 'auth_source_sha256', 'images', 'tool_sha256',
                     'harness_sha256', 'emb_config_sha256', 'evomaster_schema_oracles')
        assert all(m.get(k) == b.get(k) for k in pair_keys), run.name
        specs = {name: list(directory.glob(pattern)) for name, directory, pattern in
                 [('base_original', base, 'spec.original.*'), ('base_test', base, 'spec.test.*'),
                  ('mut_original', run, 'spec.original.*'), ('mut_test', run, 'spec.test.*')]}
        assert all(len(v) == 1 for v in specs.values())
        spec_hashes = {k: digest(v[0]) for k, v in specs.items()}
        assert len({spec_hashes[k] for k in ('base_original', 'base_test', 'mut_original')}) == 1
        manifest = json.loads((run / 'manifest.json').read_text())
        assert all(manifest[k] == m[k] for k in ('seed', 'fault', 'severity'))
        assert manifest['source_sha256'] == spec_hashes['mut_original']
        assert len(manifest['mutations']) == int(row['mutated_ops'])
        assert digest(run / 'manifest.json') == m['file_sha256']['manifest.json']
        assert spec_hashes['mut_test'] == m['file_sha256'][specs['mut_test'][0].name]
        match = re.fullmatch(r'(.*_baseline_NONE_p0_s)(\d+)', base.name)
        peers = []
        if match:
            for peer in sorted(base.parent.glob(match[1] + '*')):
                if peer == base or not (peer / 'exchanges.jsonl').is_file():
                    continue
                pm = json.loads((peer / 'run.json').read_text())
                if not pm.get('complete'):
                    continue
                assert pm['seed'] != b['seed']
                assert method(peer, pm) == method(base, b)
                assert all(pm.get(k) == b.get(k) for k in pair_keys), peer.name
                assert digest(next(peer.glob('spec.original.*'))) == spec_hashes['base_original']
                differences = {k: [b.get(k), pm.get(k)] for k in set(b) | set(pm)
                               if b.get(k) != pm.get(k)}
                peers.append({'run': peer.name, 'differing_meta_keys': sorted(differences)})
        nr = next((n for n in noise if n['run'] == run.name), None)
        assert (nr is not None) == bool(peers)
        if nr:
            assert len(peers) == int(nr['noise_pairs'])
        record.update(baseline=base.name, spec_hashes=spec_hashes, peers=peers)
        selected.append(record)
    loose = [r for r in compare if r['fault'] == 'REQUEST_LOOSE' and int(r['replay_mut_NEW'])]
    manifest_pairs = []
    for em in compare:
        if em['fuzzer'] != 'evomaster':
            continue
        for st in compare:
            if st['fuzzer'] != 'schemathesis' or any(em[k] != st[k] for k in ('sut', 'fault', 'severity', 'seed')):
                continue
            ep = RUNS / em['sut'] / em['run'] / 'manifest.json'
            sp = RUNS / st['sut'] / st['run'] / 'manifest.json'
            ev, sv = (json.loads(p.read_text())['mutations'] for p in (ep, sp))
            manifest_pairs.append({'sut': em['sut'], 'fault': em['fault'], 'seed': em['seed'],
                                   'em': str(ep.relative_to(ROOT)), 'st': str(sp.relative_to(ROOT)),
                                   'equal_mutations': ev == sv,
                                   'em_ops': [[m['method'], m['path']] for m in ev],
                                   'st_ops': [[m['method'], m['path']] for m in sv]})
    (OUT / 'manifest_pairs.json').write_text(json.dumps(manifest_pairs, indent=2) + '\n')
    document = (RESULTS / 'FUZZER_COMPARE.md').read_text()
    table_checks = []
    sut_names = {'petstore': 'swagger-petstore', 'market': 'market', 'cwa': 'cwa-verification'}
    for line in document.splitlines():
        cells = [s.strip() for s in line.split('|')[1:-1]]
        if len(cells) != 4 or cells[0] not in sut_names or cells[1] not in ('METHOD_SEM', 'REQUEST_STRICT', 'RESPONSE_ORACLE', 'REQUEST_LOOSE'):
            continue
        for col, fuzzer in ((2, 'evomaster'), (3, 'schemathesis')):
            pairs = re.findall(r'(\d+)/(\d+)', cells[col])
            for i, pair in enumerate(pairs):
                severity = 100 if ('শুধু p100' in cells[col] or i > 0) else 30
                key = (sut_names[cells[0]], cells[1], fuzzer, severity)
                rs = groups[key]
                actual = (sum(r['beyond_noise_NEW'] == 'True' for r in rs), len(rs))
                assert actual == tuple(map(int, pair)), (key, actual, pair)
                table_checks.append({'cell': list(key), 'claimed': pair, 'actual': list(actual)})
    assert len(table_checks) == 26
    same_seed = list(csv.DictReader((RESULTS / 'noise_floor_spec.csv').open()))
    noise_by_run = {r['run']: r for r in noise}
    counterexamples = [{'run': r['run'], 'same_seed_max': int(r['noise_max_mut_NEW']),
                        'cross_seed_max': int(noise_by_run[r['run']]['noise_max_mut_NEW'])}
                       for r in same_seed if r['run'] in noise_by_run
                       and int(r['noise_max_mut_NEW']) > int(noise_by_run[r['run']]['noise_max_mut_NEW'])]
    (OUT / 'noise_counterexamples.json').write_text(json.dumps(counterexamples, indent=2) + '\n')
    summary = {'compare_rows': len(compare), 'noise_rows': len(noise),
               'duplicate_compare_runs': len(compare) - len(by_run),
               'table': table, 'matched_p30': matched, 'traffic': traffic,
               'nonzero_LOOSE_replay': loose,
               'noise_extrema': {fz: {k: max(float(r[k]) for r in noise if r['fuzzer'] == fz)
                                      for k in ('noise_max_mut_NEW', 'noise_max_mut_INC', 'noise_mean_mut_NEW')}
                                for fz in ('evomaster', 'schemathesis')},
               'replay_unmut_changes': Counter(r['replay_unmut_changes'] for r in compare),
               'selected_classifications': Counter(r['classification'] for r in selected),
               'manifest_matching': {str(k): dict(Counter(p['equal_mutations'] for p in manifest_pairs if p['fault'] == k))
                                     for k in sorted({p['fault'] for p in manifest_pairs})},
               'doc_detection_cell_checks': table_checks,
               'excluded_count': len(excluded)}
    (OUT / 'recount.json').write_text(json.dumps(summary, indent=2) + '\n')
    (OUT / 'provenance.json').write_text(json.dumps({'selected': selected, 'excluded': excluded}, indent=2) + '\n')
    assert hashes == {p: digest(Path(p)) for p in hashes}
    (OUT / 'reviewed_hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
