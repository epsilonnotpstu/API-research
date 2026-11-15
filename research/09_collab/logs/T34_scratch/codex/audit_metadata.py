"""Read-only manifest/provenance audit; never emits auth/header values or exchanges."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / '08_experiments/E1_pilot/pilot_results'
RUNS = RESULTS.parent / 'runs'


def read(p):
    return json.loads(p.read_text())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def base_of(p):
    ins = [x for x in p.glob('analysis-*/inputs.txt') if not x.parent.name.endswith('-sut')]
    bases = {dict(l.split('=', 1) for l in x.read_text().splitlines())['baseline'] for x in ins}
    assert len(bases) == 1, (p.name, bases)
    return Path(next(iter(bases))).resolve()


def patches(m):
    return sorted(canonical({k: x.get(k) for k in ('path', 'method', 'fault', 'edits')})
                  for x in m['mutations'])


def pool(p, m):
    ops = m.get('only_ops')
    if not ops:
        return None
    q = Path(ops['file'])
    assert q.is_file()
    data = read(q)
    return sorted(data['operations'])


def settings(m):
    return (m.get('evomaster_input', 'spec'), m.get('evomaster_schema_oracles', True),
            m['budget_seconds'], m.get('evomaster_image'))


protected = list(RESULTS.glob('fuzzer*.py')) + list(RESULTS.glob('fuzzer*.csv')) + [
    RESULTS / 'FUZZER_COMPARE.md', RESULTS / 'PILOT_SUMMARY.md']
freeze = {str(p.relative_to(ROOT)): digest(p) for p in protected}
freeze_path = HERE / 'reviewed_hashes.json'
if freeze_path.exists():
    assert read(freeze_path) == freeze
else:
    freeze_path.write_text(json.dumps(freeze, indent=2) + '\n')
cells = list(csv.DictReader((RESULTS / 'fuzzer_controlled_cells.csv').open()))
manifest_pairs = []
for line, r in enumerate(cells, 2):
    ep, sp = [RUNS / r['sut'] / r[k] for k in ('evo_run', 'sch_run')]
    em, sm = read(ep / 'manifest.json'), read(sp / 'manifest.json')
    a = {'csv_line': line, 'sut': r['sut'], 'fault': r['fault'], 'seed': r['seed'],
         'controlled': r['controlled'] == 'True', 'evo_run': ep.name, 'sch_run': sp.name,
         'patch_equal': patches(em) == patches(sm),
         'source_hash_equal': em['source_sha256'] == sm['source_sha256'],
         'oracle_original_equal': digest(ep / 'spec.original.json') == digest(sp / 'spec.original.json'),
         'oracle_mutated_equal': digest(ep / 'spec.test.json') == digest(sp / 'spec.test.json'),
         'severity_equal': em['severity'] == sm['severity'],
         'operations_total_equal': em['operations_total'] == sm['operations_total'],
         'evo_pool_operations': pool(ep, em), 'sch_pool_operations': pool(sp, sm),
         'pool_ops_equal': pool(ep, em) == pool(sp, sm),
         'only_ops_sha_equal': (em.get('only_ops') or {}).get('sha256') == (sm.get('only_ops') or {}).get('sha256')}
    assert a['patch_equal'] == a['controlled']
    manifest_pairs.append(a)
(HERE / 'manifest_pairs.json').write_text(json.dumps(manifest_pairs, indent=2) + '\n')

same = list(csv.DictReader((RESULTS / 'fuzzer_noise_same_seed.csv').open()))
all_meta = {p.parent.resolve(): read(p) for p in RUNS.glob('*/*_baseline_NONE_p0_s*/run.json')}
matches = []
equality_fields = ('sut_image', 'sut_jar_sha256', 'source_sha256', 'request_timeout_ms',
                   'logger_max_body', 'base_path', 'auth', 'auth_source_sha256', 'code_mutation',
                   'emb_commit', 'emb_config_sha256', 'harness_version')
for line, r in enumerate(same, 2):
    rp = RUNS / r['sut'] / r['run']
    bp = base_of(rp)
    bm = read(bp / 'run.json')
    rm = read(rp / 'run.json')
    candidates = [(p, m) for p, m in all_meta.items() if p.parent.name == r['sut'] and
                  m.get('fuzzer') == 'evomaster' and m.get('complete') and
                  (p / 'exchanges.jsonl').is_file() and p != bp and
                  m['seed'] == bm['seed'] and settings(m) == settings(bm)]
    assert len(candidates) == int(r['replicates'])
    for p, m in candidates:
        a = {'csv_line': line, 'sut': r['sut'], 'run': rp.name, 'baseline': bp.name, 'replicate': p.name,
             'seed': bm['seed'], 'settings': settings(bm), 'self_match': p == bp,
             'mutated_baseline_settings_equal': settings(rm) == settings(bm),
             'mutated_baseline_extra_knobs_equal': all(rm.get(k) == bm.get(k) for k in equality_fields),
             'complete': bm['complete'] and m['complete'],
             'baseline_exit': {k: bm.get(k) for k in ('phase', 'harness_exit', 'evomaster_exit', 'coverage_exit')},
             'replicate_exit': {k: m.get(k) for k in ('phase', 'harness_exit', 'evomaster_exit', 'coverage_exit')},
             'extra_knobs_equal': {k: bm.get(k) == m.get(k) for k in equality_fields},
             'actual_original_equal': digest(bp / 'spec.original.json') == digest(p / 'spec.original.json'),
             'actual_generator_input_equal': digest(bp / ('generator-input.json' if settings(bm)[0] == 'derecursed' else 'spec.test.json')) ==
                                             digest(p / ('generator-input.json' if settings(m)[0] == 'derecursed' else 'spec.test.json')),
             'argv_equal': (bp / 'evomaster-argv.txt').read_bytes() == (p / 'evomaster-argv.txt').read_bytes(),
             'image_ids_equal': {k: bm.get('images', {}).get(k, {}).get('id') == m.get('images', {}).get(k, {}).get('id')
                                 for k in set(bm.get('images', {})) | set(m.get('images', {}))},
             'harness_changed_files': [k for k in sorted(set(bm['harness_sha256']) | set(m['harness_sha256']))
                                       if bm['harness_sha256'].get(k) != m['harness_sha256'].get(k)],
             'tools_changed_files': [k for k in sorted(set(bm['tool_sha256']) | set(m['tool_sha256']))
                                     if bm['tool_sha256'].get(k) != m['tool_sha256'].get(k)],
             'exchange_file_bytes': {'baseline': (bp / 'exchanges.jsonl').stat().st_size,
                                     'replicate': (p / 'exchanges.jsonl').stat().st_size,
                                     'mutated': (rp / 'exchanges.jsonl').stat().st_size}}
        matches.append(a)
(HERE / 'replicate_matches.json').write_text(json.dumps(matches, indent=2) + '\n')
summary = {
    'controlled_pairs': sum(x['controlled'] for x in manifest_pairs),
    'controlled_mismatches': {k: [x['csv_line'] for x in manifest_pairs if x['controlled'] and not x[k]]
                              for k in ('patch_equal', 'source_hash_equal', 'oracle_original_equal',
                                        'oracle_mutated_equal', 'severity_equal', 'operations_total_equal',
                                        'pool_ops_equal', 'only_ops_sha_equal')},
    'matched_rows': len(matches),
    'distinct_baseline_replicate_pairs': len({(x['baseline'], x['replicate']) for x in matches}),
    'self_matches': sum(x['self_match'] for x in matches),
    'all_complete': all(x['complete'] for x in matches),
    'mutated_baseline_settings_mismatch': sum(not x['mutated_baseline_settings_equal'] for x in matches),
    'mutated_baseline_extra_knobs_mismatch': sum(not x['mutated_baseline_extra_knobs_equal'] for x in matches),
    'extra_knob_mismatch_counts': {k: sum(not x['extra_knobs_equal'][k] for x in matches) for k in equality_fields},
    'original_mismatch': sum(not x['actual_original_equal'] for x in matches),
    'generator_input_mismatch': sum(not x['actual_generator_input_equal'] for x in matches),
    'argv_mismatch': sum(not x['argv_equal'] for x in matches),
    'image_id_mismatch': sum(not all(x['image_ids_equal'].values()) for x in matches),
    'harness_changed_rows': sum(bool(x['harness_changed_files']) for x in matches),
    'tool_changed_rows': sum(bool(x['tools_changed_files']) for x in matches),
    'unique_replicate_pairs': [x for i, x in enumerate(matches)
                               if (x['baseline'], x['replicate']) not in {(y['baseline'], y['replicate']) for y in matches[:i]}],
}
(HERE / 'metadata_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'unique_replicate_pairs'}, indent=2))
print('Distinct pairs:')
for x in summary['unique_replicate_pairs']:
    print(x['sut'], x['seed'], x['settings'][:2], 'harness drift:', x['harness_changed_files'],
          'tools drift:', x['tools_changed_files'], 'bytes:', x['exchange_file_bytes'])
