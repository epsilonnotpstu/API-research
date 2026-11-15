#!/usr/bin/env python3
"""Schemathesis (negative data) vs EvoMaster (black-box) on the same spec mutations (Claude, 2026-11-15).

Every complete mutated run whose Schemathesis argv used --data-generation-method, or whose run.json says
fuzzer=evomaster, is re-checked with the CURRENT checker (int formats on, default oracle 400/422) against its
paired baseline (analysis inputs.txt):
  fresh  = attribution(baseline @ base spec, mutated run @ mutated spec, manifest)
  replay = attribution(baseline @ base spec, baseline @ mutated spec, manifest)
Counts: NEW / INCREASED on mutated ops, NEW / INCREASED / DECREASED on unmutated ops, exchange counts.
Output: fuzzer_compare.csv, and a summary per SUT x fault x fuzzer on stdout.
Offline, own Python only.
"""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import attribute  # noqa: E402
import conformance as c  # noqa: E402

SERVICE = {'scout-api': 'sut-scout-api', 'swagger-petstore': 'sut-swagger-petstore', 'market': 'sut-market',
           'cwa-verification': 'sut-cwa-verification'}
_cache = {}
# Mechanism-expected kinds per spec fault class (Claude, 2026-11-15; fixed from mutator semantics in tools/specmut.py
# BEFORE looking at per-kind results; motivated by the STRICT ablation's collateral-exposure finding). This is a
# CANONICAL, mechanism-compatible kind filter, not a causal adjudication (T39 F3): a NEW of another kind is only
# 'outside the filter' — trace-confirmed collateral only where a trace exists (market STRICT required-only, T35).
# METHOD_SEM's set is a canonical subset: a fresh target-verb contract mismatch (RESPONSE_SCHEMA, INVALID_ACCEPTED,
# RESPONSE_CONTENT_TYPE) can also come from the method swap and is not included (T39 F2).
EXPECTED_KINDS = {
    'REQUEST_LOOSE': {'VALID_REJECTED'},
    'REQUEST_STRICT': {'INVALID_ACCEPTED'},
    'RESPONSE_ORACLE': {'RESPONSE_SCHEMA', 'UNDOCUMENTED_STATUS'},
    'METHOD_SEM': {'UNDOCUMENTED_OPERATION', 'UNDOCUMENTED_STATUS', 'VALID_REJECTED'},
}


def fuzzer_of(run, meta):
    if meta.get('fuzzer') == 'evomaster':
        return 'evomaster'
    argv = run / 'schemathesis-argv.txt'
    if argv.is_file() and 'data-generation-method' in argv.read_text():
        return 'schemathesis'
    return None


def violations(run, spec_path, sut, cache=True):
    key = (str(run), str(spec_path))
    if key not in _cache or not cache:
        spec = c.Spec(json.load(open(spec_path)), deploy_origin=f'http://{SERVICE[sut]}:8080')
        out, n = [], 0
        for line in open(run / 'exchanges.jsonl'):
            out.extend(c.check(spec, json.loads(line)))
            n += 1
        if not cache:
            return out, n
        _cache.clear() if len(_cache) > 4 else None
        _cache[key] = (out, n)
    return _cache[key]


def counts(rows, expected=()):
    d = defaultdict(int)
    for r in rows:
        side = 'mut' if r['op_mutated'] else 'unmut'
        if r['status'] == 'NEW':
            d[side + '_NEW'] += 1
            if not r['kind'].endswith('_UNCHECKABLE'):  # T29 F3: checker inability is not a fault signal
                d[side + '_NEW_checkable'] += 1
            if r['kind'] in expected:
                d[side + '_NEW_expected'] += 1
        elif r['status'] == 'PERSISTENT' and r['mutated_occurrences'] > r['baseline_occurrences']:
            d[side + '_INCREASED'] += 1
        elif r['status'] == 'PERSISTENT' and r['mutated_occurrences'] < r['baseline_occurrences']:
            d[side + '_DECREASED'] += 1
    return d


def manifest_signature(manifest):
    """T29 F2: identical mutation sets (operations + edits) across fuzzers make a cell controlled."""
    key = sorted(json.dumps({k: m.get(k) for k in ('path', 'method', 'fault', 'edits')}, sort_keys=True)
                 for m in manifest['mutations'])
    return hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16]


def main():
    c.INT_FORMATS = True
    out = []
    for meta_path in sorted(RUNS.glob('*/*mutated_*/run.json')):
        run = meta_path.parent.resolve()
        meta = json.load(open(meta_path))
        if not meta.get('complete') or meta['sut'] not in SERVICE or not (run / 'exchanges.jsonl').is_file():
            continue
        if meta.get('strict_keywords'):
            continue  # T37 keyword-ablation runs are analysed separately (strict_ablation.py), never mixed in
        if meta.get('code_mutation'):
            continue  # E5 code mutants are not spec-mutation runs
        fz = fuzzer_of(run, meta)
        if fz is None:
            continue
        inputs = [p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut')]
        if not inputs:
            continue
        base = Path(dict(l.split('=', 1) for l in inputs[0].read_text().splitlines())['baseline']).resolve()
        manifest = json.load(open(run / 'manifest.json'))
        base_spec, mut_spec = next(base.glob('spec.original.*')), next(run.glob('spec.test.*'))
        bv, bn = violations(base, base_spec, meta['sut'])
        mv, mn = violations(run, mut_spec, meta['sut'], cache=False)
        rv, _ = violations(base, mut_spec, meta['sut'], cache=False)
        fresh_rows = attribute.attribute(bv, mv, manifest, 'fresh')
        fresh = counts(fresh_rows, EXPECTED_KINDS[meta['fault']])
        fresh_kinds = defaultdict(int)
        for x in fresh_rows:
            if x['op_mutated'] and x['status'] == 'NEW' and not x['kind'].endswith('_UNCHECKABLE'):
                fresh_kinds[x['kind']] += 1
        replay = counts(attribute.attribute(bv, rv, manifest, 'replay'))
        row = {'sut': meta['sut'], 'fault': meta['fault'], 'severity': meta['severity'], 'seed': meta['seed'],
               'fuzzer': fz, 'run': run.name, 'mutated_ops': len(manifest['mutations']),
               'manifest_sig': manifest_signature(manifest),
               'baseline_exchanges': bn, 'mutated_exchanges': mn}
        for k in ('mut_NEW', 'mut_NEW_checkable', 'mut_INCREASED', 'unmut_NEW', 'unmut_INCREASED', 'unmut_DECREASED'):
            row['fresh_' + k] = fresh[k]
        row['fresh_mut_NEW_expected'] = fresh['mut_NEW_expected']
        row['fresh_mut_kinds'] = ';'.join(f'{k}:{v}' for k, v in sorted(fresh_kinds.items()))
        row['replay_mut_NEW'] = replay['mut_NEW']
        row['replay_unmut_changes'] = replay['unmut_NEW'] + replay['unmut_INCREASED'] + replay['unmut_DECREASED']
        out.append(row)
        print(f"{fz:<12} {meta['sut']:<17} {meta['fault']:<16} p{meta['severity']} s{meta['seed']} "
              f"ex {bn}/{mn} fresh mutNEW {fresh['mut_NEW']} mutINC {fresh['mut_INCREASED']} | "
              f"replay mutNEW {replay['mut_NEW']}", flush=True)
    with open(HERE / 'fuzzer_compare.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(lambda: defaultdict(list))
    for r in out:
        a = agg[(r['sut'], r['fault'], r['fuzzer'], r['severity'])]  # T29: never mix severities
        for k in ('fresh_mut_NEW', 'replay_mut_NEW', 'mutated_exchanges'):
            a[k].append(r[k])
        a['detected'].append(r['fresh_mut_NEW'] > 0 or r['fresh_mut_INCREASED'] > 0)
    print('== summary: sut fault fuzzer severity | runs | fresh detected (NEW or INC) | mean fresh mutNEW | mean replay mutNEW | mean exchanges')
    for k in sorted(agg):
        a = agg[k]
        n = len(a['detected'])
        print(f"   {k[0]:<17} {k[1]:<16} {k[2]:<12} p{k[3]:<4} | {n} | {sum(a['detected'])}/{n} | "
              f"{sum(a['fresh_mut_NEW']) / n:.1f} | {sum(a['replay_mut_NEW']) / n:.1f} | {sum(a['mutated_exchanges']) / n:.0f}")
    print('->', HERE / 'fuzzer_compare.csv')


if __name__ == '__main__':
    main()
