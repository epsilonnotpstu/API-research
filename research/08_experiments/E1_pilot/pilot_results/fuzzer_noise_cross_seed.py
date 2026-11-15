#!/usr/bin/env python3
"""Cross-seed noise floor for fuzzer_compare.py (Claude, 2026-11-15).

EvoMaster batches have one baseline per seed and no same-seed replicate.
For every row of fuzzer_compare.csv, take its paired baseline B (seed s), and every other-seed baseline B' of the
same batch. Compute attribution(B @ base spec, B' @ base spec, row manifest, 'fresh'), with no spec mutation at all.
Count mutated-op NEW / INCREASED.

This is an OBSERVED CROSS-SEED REFERENCE, not an upper bound on same-input noise (T29 F1: petstore STRICT/ORACLE s3
show same-seed max NEW > cross-seed max). 'beyond_ref' = fresh count exceeds the maximum over this finite set of
peers; no significance claim. Counts exclude *_UNCHECKABLE kinds on both sides (T29 F3); raw counts kept too.
Output: fuzzer_noise_cross_seed.csv and a summary on stdout. Offline, own Python only.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import attribute  # noqa: E402
import conformance as c  # noqa: E402
from fuzzer_compare import EXPECTED_KINDS, SERVICE, counts  # noqa: E402

_cache = {}


def base_violations(run, sut):
    if run not in _cache:
        if len(_cache) > 6:
            _cache.pop(next(iter(_cache)))
        spec = c.Spec(json.load(open(next(run.glob('spec.original.*')))), deploy_origin=f'http://{SERVICE[sut]}:8080')
        out = []
        for line in open(run / 'exchanges.jsonl'):
            out.extend(c.check(spec, json.loads(line)))
        _cache[run] = out
    return _cache[run]


def main():
    c.INT_FORMATS = True
    rows = list(csv.DictReader(open(HERE / 'fuzzer_compare.csv')))
    rows.sort(key=lambda r: (r['sut'], r['run']))
    out = []
    for r in rows:
        run = RUNS / r['sut'] / r['run']
        inputs = [p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut')]
        base = Path(dict(l.split('=', 1) for l in inputs[0].read_text().splitlines())['baseline']).resolve()
        m = re.match(r'(.*_baseline_NONE_p0_s)(\d+)$', base.name)
        if not m:
            continue
        others = [p for p in base.parent.glob(m.group(1) + '*')
                  if p != base and (p / 'exchanges.jsonl').is_file() and json.load(open(p / 'run.json')).get('complete')]
        manifest = json.load(open(run / 'manifest.json'))
        bv = base_violations(base, r['sut'])
        noise = []
        for o in sorted(others):
            d = counts(attribute.attribute(bv, base_violations(o, r['sut']), manifest, 'fresh'), EXPECTED_KINDS[r['fault']])
            noise.append((d['mut_NEW'], d['mut_INCREASED'], d['mut_NEW_checkable'], d['mut_NEW_expected']))
        if not noise:
            continue
        row = dict(r)
        row['noise_pairs'] = len(noise)
        row['noise_max_mut_NEW'] = max(x[0] for x in noise)
        row['noise_max_mut_INC'] = max(x[1] for x in noise)
        row['noise_mean_mut_NEW'] = round(sum(x[0] for x in noise) / len(noise), 2)
        row['noise_max_mut_NEW_checkable'] = max(x[2] for x in noise)
        row['beyond_ref_NEW'] = int(r['fresh_mut_NEW']) > row['noise_max_mut_NEW']
        row['beyond_ref_NEW_checkable'] = int(r['fresh_mut_NEW_checkable']) > row['noise_max_mut_NEW_checkable']
        row['noise_max_mut_NEW_expected'] = max(x[3] for x in noise)
        row['beyond_ref_NEW_expected'] = int(r['fresh_mut_NEW_expected']) > row['noise_max_mut_NEW_expected']
        out.append(row)
        print(f"{r['fuzzer']:<12} {r['sut']:<17} {r['fault']:<16} p{r['severity']} s{r['seed']} fresh mutNEW "
              f"{r['fresh_mut_NEW']} (checkable {r['fresh_mut_NEW_checkable']}) | ref mutNEW {[x[0] for x in noise]} "
              f"checkable {[x[2] for x in noise]} INC {[x[1] for x in noise]}", flush=True)
    with open(HERE / 'fuzzer_noise_cross_seed.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(list)
    for r in out:
        agg[(r['sut'], r['fault'], r['fuzzer'], r['severity'])].append(r)
    print('== summary: sut fault fuzzer sev | runs | fresh mutNEW>0 | beyond ref (NEW) | beyond ref (checkable NEW) | mean ref mutNEW')
    for k in sorted(agg):
        a = agg[k]
        n = len(a)
        print(f"   {k[0]:<17} {k[1]:<16} {k[2]:<12} p{k[3]:<4} | {n} | {sum(int(x['fresh_mut_NEW']) > 0 for x in a)}/{n} | "
              f"{sum(x['beyond_ref_NEW'] for x in a)}/{n} | {sum(x['beyond_ref_NEW_checkable'] for x in a)}/{n} | "
              f"{sum(x['noise_mean_mut_NEW'] for x in a) / n:.1f}")
    print('->', HERE / 'fuzzer_noise_cross_seed.csv')


if __name__ == '__main__':
    main()
