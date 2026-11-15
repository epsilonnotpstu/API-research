"""Independent CSV-only T34 recount. No project imports or exchange reads."""
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / '08_experiments/E1_pilot/pilot_results'
NAMES = ['fuzzer_compare', 'fuzzer_noise_cross_seed', 'fuzzer_controlled_cells',
         'fuzzer_noise_same_seed', 'fuzzer_trajectory_overlap']
tables = {n: list(csv.DictReader((RESULTS / (n + '.csv')).open())) for n in NAMES}
checks = Counter()


def check(test):
    checks['assertions'] += 1
    assert test


cross = {r['run']: r for r in tables['fuzzer_noise_cross_seed']}
same = {r['run']: r for r in tables['fuzzer_noise_same_seed']}
source = {r['run']: r for r in tables['fuzzer_compare']}
groups = defaultdict(lambda: defaultdict(list))
for r in cross.values():
    groups[tuple(r[k] for k in ('sut', 'fault', 'severity', 'seed'))][r['fuzzer']].append(r)
expected = {}
for k, g in groups.items():
    for e, s in itertools.product(g['evomaster'], g['schemathesis']):
        expected[e['run'], s['run']] = (k, e['manifest_sig'] == s['manifest_sig'])
check(len(expected) == len(tables['fuzzer_controlled_cells']))
controlled = defaultdict(lambda: [0, 0, 0])
uses = defaultdict(Counter)
for line, r in enumerate(tables['fuzzer_controlled_cells'], 2):
    e, s = cross[r['evo_run']], cross[r['sch_run']]
    k, ctl = expected[r['evo_run'], r['sch_run']]
    check(tuple(r[x] for x in ('sut', 'fault', 'severity', 'seed')) == k)
    check((r['controlled'] == 'True') == ctl)
    check(int(r['evo_fresh_checkable_NEW']) == int(e['fresh_mut_NEW_checkable']))
    check(int(r['sch_fresh_checkable_NEW']) == int(s['fresh_mut_NEW_checkable']))
    es = int(e['fresh_mut_NEW_checkable']) > int(e['noise_max_mut_NEW_checkable'])
    ss = int(s['fresh_mut_NEW_checkable']) > int(s['noise_max_mut_NEW_checkable'])
    check((r['evo_signal'] == 'True') == es)
    check((r['sch_signal'] == 'True') == ss)
    a = controlled[(r['controlled'], r['sut'], r['fault'])]
    a[0] += es
    a[1] += ss
    a[2] += 1
    uses[r['controlled']][r['evo_run']] += 1

same_totals = defaultdict(lambda: [0, 0, 0])
for r in same.values():
    b = int(r['fresh_mut_NEW_checkable']) > int(r['same_seed_max_NEW_checkable'])
    check((r['beyond_same_seed_ref'] == 'True') == b)
    check(r['fresh_mut_NEW_checkable'] == source[r['run']]['fresh_mut_NEW_checkable'])
    a = same_totals[r['sut'], r['fault']]
    a[0] += b
    a[1] += 1
    a[2] = max(a[2], int(r['same_seed_max_NEW_checkable']))

trajectory = defaultdict(list)
for r in tables['fuzzer_trajectory_overlap']:
    x = source[r['run']]
    check(r['fresh_mut_NEW_checkable'] == x['fresh_mut_NEW_checkable'])
    cr, sr = cross.get(r['run']), same.get(r['run'])
    refs = []
    for row, field, val_field, flag in [(cr, 'noise_max_mut_NEW_checkable', 'cross_ref_max', 'beyond_cross'),
                                       (sr, 'same_seed_max_NEW_checkable', 'same_ref_max', 'beyond_same')]:
        if row:
            ref = int(row[field])
            refs.append(ref)
            check(int(r[val_field]) == ref)
            check((r[flag] == 'True') == (int(x['fresh_mut_NEW_checkable']) > ref))
        else:
            check(r[flag] == '' and r[val_field] == '')
    check((r['beyond_both'] == 'True') == (int(x['fresh_mut_NEW_checkable']) > max(refs)))
    trajectory[r['fuzzer'], r['fault']].append(r)

summary = {
    'row_counts': {n: len(t) for n, t in tables.items()},
    'controlled_by_sut_fault': [{'controlled': k[0], 'sut': k[1], 'fault': k[2],
                               'evo_beyond': v[0], 'sch_beyond': v[1], 'pairs': v[2]}
                              for k, v in sorted(controlled.items())],
    'controlled_totals': {ctl: {'evo_beyond': sum(v[0] for k, v in controlled.items() if k[0] == ctl),
                              'sch_beyond': sum(v[1] for k, v in controlled.items() if k[0] == ctl),
                              'pairs': sum(v[2] for k, v in controlled.items() if k[0] == ctl),
                              'unique_evo_runs': len(uses[ctl]),
                              'repeated_evo_runs': {k: v for k, v in uses[ctl].items() if v > 1}}
                          for ctl in ('True', 'False')},
    'same_seed_by_sut_fault': [{'sut': k[0], 'fault': k[1], 'beyond': v[0], 'runs': v[1], 'max_ref': v[2]}
                             for k, v in sorted(same_totals.items())],
    'same_seed_total_beyond': sum(v[0] for v in same_totals.values()),
    'replicate_counts': dict(Counter(r['replicates'] for r in same.values())),
    'trajectory': [{'fuzzer': k[0], 'fault': k[1], 'runs': len(a),
                    'true_median_pos': __import__('statistics').median(float(x['pos_identity_vs_base']) for x in a),
                    'true_median_jaccard': __import__('statistics').median(float(x['jaccard_vs_base']) for x in a),
                    **{flag: [sum(x[flag] == 'True' for x in a), sum(x[flag] != '' for x in a)]
                       for flag in ('beyond_cross', 'beyond_same', 'beyond_both')}}
                   for k, a in sorted(trajectory.items())],
    'checks': dict(checks),
    'input_sha256': {n + '.csv': hashlib.sha256((RESULTS / (n + '.csv')).read_bytes()).hexdigest() for n in NAMES},
}
(HERE / 'recount.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
