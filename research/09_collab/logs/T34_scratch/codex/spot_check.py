"""Exactly three T34 rows: small cwa/market runs; independent fingerprint-set recount.

Only the repository's checker is reused. No raw requests, bodies or headers are emitted.
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / '08_experiments/E1_pilot/pilot_results'
RUNS = RESULTS.parent / 'runs'
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import conformance as checker

checker.INT_FORMATS = True
tables = {name: {r['run']: r for r in csv.DictReader((RESULTS / (name + '.csv')).open())}
          for name in ['fuzzer_compare', 'fuzzer_noise_same_seed', 'fuzzer_noise_cross_seed', 'fuzzer_trajectory_overlap']}
all_matches = json.loads((HERE / 'replicate_matches.json').read_text())
targets = [('cwa-verification', 'RESPONSE_ORACLE', '1'), ('market', 'RESPONSE_ORACLE', '2'),
           ('market', 'REQUEST_STRICT', '2')]
cache = {}
inputs = {}
assertions = 0


def assert_equal(a, b):
    global assertions
    assertions += 1
    assert a == b, (a, b)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def evaluate(run, spec_path, sut):
    key = str(run), str(spec_path)
    if key in cache:
        return cache[key]
    spec = checker.Spec(json.loads(spec_path.read_text()), deploy_origin=f'http://sut-{sut}:8080')
    violations, oldkeys, fullkeys, req_only_keys, details = {}, [], [], [], Counter()
    body_prefixes = {}
    for line in (run / 'exchanges.jsonl').open():
        e = json.loads(line)
        rq, rs = e.get('request') or {}, e.get('response') or {}
        for v in checker.check(spec, e):
            if v['fingerprint'] not in violations:
                violations[v['fingerprint']] = [v, 0]
            violations[v['fingerprint']][1] += 1
        body = rq.get('body')
        body_text = body.get('text', '') if isinstance(body, dict) else str(body)
        details['body_repr_over_2000'] += len(str(body)) > 2000
        details['body_truncated_by_logger'] += bool(isinstance(body, dict) and body.get('truncated'))
        details['requests'] += 1
        old = (rq.get('method'), rq.get('path'), json.dumps(rq.get('query'), sort_keys=True),
               str(body)[:2000], rs.get('status'))
        oldkeys.append(old)
        # Hash only in-memory comparison keys; do not emit sensitive request data.
        fullkeys.append(hashlib.sha256(canonical(rq).encode()).hexdigest())
        req_only_keys.append(old[:-1])
        bh = hashlib.sha256(body_text.encode()).hexdigest()
        body_prefixes.setdefault(old, set()).add(bh)
    details['old_key_groups_with_distinct_full_body'] = sum(len(x) > 1 for x in body_prefixes.values())
    p = run / 'exchanges.jsonl'
    inputs[str(p.relative_to(ROOT))] = {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                                       'lines': details['requests']}
    out = violations, oldkeys, fullkeys, req_only_keys, dict(details)
    cache[key] = out
    return out


def compare(a, b, manifest):
    ops = {(m['method'].upper(), m['path']) for m in manifest['mutations']}
    ops |= {(str(e['after']).upper(), m['path']) for m in manifest['mutations']
            if m['fault'] == 'METHOD_SEM' for e in m['edits']}
    counts = Counter()
    for fp, (v, n) in b.items():
        side = 'mut' if (v['method'], v['template']) in ops else 'unmut'
        if fp not in a:
            counts[side + '_NEW'] += 1
            counts[side + '_NEW_checkable'] += not v['kind'].endswith('_UNCHECKABLE')
        elif n > a[fp][1]:
            counts[side + '_INCREASED'] += 1
        elif n < a[fp][1]:
            counts[side + '_DECREASED'] += 1
    return counts


def overlap(a, b):
    n = min(len(a), len(b))
    s, t = set(a), set(b)
    return [round(sum(x == y for x, y in zip(a, b)) / n, 3) if n else 0,
            round(len(s & t) / len(s | t), 3) if s | t else 0]


out = []
for sut, fault, seed in targets:
    r = next(r for r in tables['fuzzer_compare'].values() if
             (r['sut'], r['fault'], r['seed'], r['fuzzer']) == (sut, fault, seed, 'evomaster'))
    run = RUNS / sut / r['run']
    match = next(x for x in all_matches if x['run'] == r['run'])
    base, rep = [RUNS / sut / match[k] for k in ('baseline', 'replicate')]
    manifest = json.loads((run / 'manifest.json').read_text())
    bv, bk, bf, bq, bd = evaluate(base, base / 'spec.original.json', sut)
    mv, mk, mf, mq, md = evaluate(run, run / 'spec.test.json', sut)
    rv, _, _, _, _ = evaluate(base, run / 'spec.test.json', sut)
    pv, pk, pf, pq, pd = evaluate(rep, rep / 'spec.original.json', sut)
    fresh, replay, same = [compare(bv, x, manifest) for x in (mv, rv, pv)]
    assert_equal(len(bk), int(r['baseline_exchanges']))
    assert_equal(len(mk), int(r['mutated_exchanges']))
    for k in ('mut_NEW', 'mut_NEW_checkable', 'mut_INCREASED', 'unmut_NEW', 'unmut_INCREASED', 'unmut_DECREASED'):
        assert_equal(fresh[k], int(r['fresh_' + k]))
    assert_equal(replay['mut_NEW'], int(r['replay_mut_NEW']))
    assert_equal(sum(replay[k] for k in ('unmut_NEW', 'unmut_INCREASED', 'unmut_DECREASED')), int(r['replay_unmut_changes']))
    sr = tables['fuzzer_noise_same_seed'][r['run']]
    assert_equal(same['mut_NEW'], int(sr['same_seed_max_NEW']))
    assert_equal(same['mut_NEW_checkable'], int(sr['same_seed_max_NEW_checkable']))
    peers = [p for p in sorted(base.parent.glob(re.match(r'(.*_baseline_NONE_p0_s)\d+$', base.name).group(1) + '*'))
             if p != base and (p / 'exchanges.jsonl').is_file() and json.loads((p / 'run.json').read_text()).get('complete')]
    peer_counts = [compare(bv, evaluate(p, p / 'spec.original.json', sut)[0], manifest) for p in peers]
    cr = tables['fuzzer_noise_cross_seed'][r['run']]
    assert_equal(max(x['mut_NEW_checkable'] for x in peer_counts), int(cr['noise_max_mut_NEW_checkable']))
    tr = tables['fuzzer_trajectory_overlap'][r['run']]
    assert_equal(overlap(bk, mk), [float(tr['pos_identity_vs_base']), float(tr['jaccard_vs_base'])])
    out.append({'sut': sut, 'fault': fault, 'seed': seed, 'run': run.name,
                'baseline': base.name, 'replicate': rep.name, 'cross_peers': [p.name for p in peers],
                'fresh_counts': dict(fresh), 'replay_counts': dict(replay), 'same_counts': dict(same),
                'cross_checkable_NEW': [x['mut_NEW_checkable'] for x in peer_counts],
                'sequence_lengths': [len(bk), len(mk), len(pk)],
                'old_key_overlap_mutated': overlap(bk, mk), 'full_request_overlap_mutated': overlap(bf, mf),
                'request_only_overlap_mutated': overlap(bq, mq),
                'old_key_overlap_replicate': overlap(bk, pk), 'full_request_overlap_replicate': overlap(bf, pf),
                'full_request_sequence_equal_replicate': bf == pf,
                'body_key_details': {'baseline': bd, 'mutated': md, 'replicate': pd}})
result = {'row_count': len(out), 'assertions': assertions, 'rows': out, 'raw_inputs': inputs}
(HERE / 'spot_check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'raw_inputs'}, indent=2))
