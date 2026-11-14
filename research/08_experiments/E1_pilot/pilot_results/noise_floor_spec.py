#!/usr/bin/env python3
"""Fresh-mode noise floor for spec mutations from existing same-seed baseline replicates (Claude, 2026-11-14).

No new runs. The negative-data batches left 2-5 complete baselines per SUT x seed with identical execution
inputs (SUT jar, images, Schemathesis argv minus run id, run_pilot.sh/common.sh/logger); only batch/analysis
scripts differed (verified 2026-11-14, see NOISE_FLOOR_SPEC.md).

For every complete mutated run generated with --data-generation-method (DATA_GEN=all) and its paired baseline
(analysis inputs.txt), with the current checker (INT_FORMATS on) and the default oracle (400/422):
  signal  = fresh attribution(paired baseline @ base spec, mutated run @ mutated spec, manifest)
  noise_r = fresh attribution(paired baseline @ base spec, replicate r @ base spec, same manifest)
            for every other replicate r of the same SUT x seed; the manifest only defines the op stratum.
Reported per run: NEW / INCREASED on mutated ops (signal vs max and mean noise) and NEW / INCREASED / DECREASED
on unmutated ops. exceeds_noise_NEW := signal NEW on mutated ops > max noise NEW on the same ops.
This is a finite-sample observation, not a statistical test.

Output: noise_floor_spec.csv; summary on stdout.
"""
import csv
import glob
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


def neg_data(run):
    argv = run / 'schemathesis-argv.txt'
    return argv.is_file() and 'data-generation-method' in argv.read_text()


def violations(run, spec_path, sut):
    key = (str(run), str(spec_path))
    if key not in _cache:
        spec = c.Spec(json.load(open(spec_path)), deploy_origin=f'http://{SERVICE[sut]}:8080')
        out = []
        for line in open(run / 'exchanges.jsonl'):
            out.extend(c.check(spec, json.loads(line)))
        _cache[key] = out
    return _cache[key]


def counts(rows):
    d = defaultdict(int)
    for r in rows:
        side = 'mut' if r['op_mutated'] else 'unmut'
        if r['status'] in ('NEW', 'VANISHED'):
            d[f'{side}_{r["status"]}'] += 1
        elif r['mutated_occurrences'] > r['baseline_occurrences']:
            d[f'{side}_INCREASED'] += 1
        elif r['mutated_occurrences'] < r['baseline_occurrences']:
            d[f'{side}_DECREASED'] += 1
    return d


def main():
    c.INT_FORMATS = True
    baselines = defaultdict(list)
    for meta in sorted(RUNS.glob('*/*baseline_NONE*/run.json')):
        r = json.load(open(meta))
        if r.get('complete') and r['sut'] in SERVICE and neg_data(meta.parent) and '_e5_' not in meta.parent.name:
            baselines[(r['sut'], r['seed'])].append(meta.parent.resolve())
    out = []
    for meta in sorted(RUNS.glob('*/*mutated_*/run.json')):
        run = meta.parent.resolve()
        r = json.load(open(meta))
        if not r.get('complete') or r['sut'] not in SERVICE or not neg_data(run):
            continue
        inputs = [p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut')]
        if not inputs:
            continue
        paired = Path(dict(l.split('=', 1) for l in inputs[0].read_text().splitlines())['baseline']).resolve()
        reps = [b for b in baselines[(r['sut'], r['seed'])] if b != paired]
        if not reps:
            continue
        manifest = json.load(open(run / 'manifest.json'))
        base_spec = next(paired.glob('spec.original.*'))
        mut_spec = next(run.glob('spec.test.*'))
        base_v = violations(paired, base_spec, r['sut'])
        sig = counts(attribute.attribute(base_v, violations(run, mut_spec, r['sut']), manifest, 'fresh'))
        noise = [counts(attribute.attribute(base_v, violations(b, next(b.glob('spec.original.*')), r['sut']), manifest, 'fresh'))
                 for b in reps]
        row = {'sut': r['sut'], 'fault': r['fault'], 'severity': r['severity'], 'seed': r['seed'], 'run': run.name,
               'n_replicates': len(reps), 'mutated_ops': len(manifest['mutations'])}
        for k in ('mut_NEW', 'mut_INCREASED', 'unmut_NEW', 'unmut_INCREASED', 'unmut_DECREASED'):
            row[f'signal_{k}'] = sig[k]
            row[f'noise_max_{k}'] = max(n[k] for n in noise)
            row[f'noise_mean_{k}'] = round(sum(n[k] for n in noise) / len(noise), 1)
        row['exceeds_noise_NEW'] = sig['mut_NEW'] > row['noise_max_mut_NEW']
        out.append(row)
        print(f"{r['sut']:<17} {r['fault']:<16} p{r['severity']:<3} s{r['seed']} reps={len(reps)} "
              f"mutNEW {sig['mut_NEW']} vs noise max {row['noise_max_mut_NEW']} | "
              f"unmut N/I/D {sig['unmut_NEW']}/{sig['unmut_INCREASED']}/{sig['unmut_DECREASED']} vs noise max "
              f"{row['noise_max_unmut_NEW']}/{row['noise_max_unmut_INCREASED']}/{row['noise_max_unmut_DECREASED']}"
              f" -> {'EXCEEDS' if row['exceeds_noise_NEW'] else 'within'}", flush=True)
    with open(HERE / 'noise_floor_spec.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print('->', HERE / 'noise_floor_spec.csv')


if __name__ == '__main__':
    main()
