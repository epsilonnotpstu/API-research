#!/usr/bin/env python3
"""Same-seed EvoMaster noise reference (Claude, 2026-11-15; answers T29 F1).

For every EvoMaster row of fuzzer_compare.csv:
- take its paired baseline B;
- take every OTHER complete EvoMaster baseline of the same SUT and seed with identical provenance (settings():
  input mode, schemaOracles, budget, image, argv, source/generator-input digests, SUT jar, image IDs, SUT config,
  auth fixture digest, timeouts, EMB commit; T34 F5) — the replicate baselines from a later baseline-only batch.
  Collection-relevant harness drift between the pair is reported (harness_drift), not used as a filter.
Then compute attribution(B @ base spec, B_rep @ base spec, row manifest, 'fresh'), with no mutation.
Count mutated-op NEW, both raw and checkable (*_UNCHECKABLE excluded, T29 F3).

'beyond_same_seed_ref' = fresh checkable NEW > max over the replicates: an OBSERVED same-seed replicate reference
(one replicate per seed here). A finite-sample observation, not a test and not an upper bound (T34).
Output: fuzzer_noise_same_seed.csv and a summary on stdout. Offline, own Python only.
"""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import attribute  # noqa: E402
import conformance as c  # noqa: E402
from fuzzer_compare import counts  # noqa: E402
from fuzzer_noise_cross_seed import base_violations  # noqa: E402


# Provenance identity for a same-seed replicate (T34 F5). Pre-T28 batches lack the knob keys; their defaults
# (spec input, schemaOracles true) are the values the T28/T31 knobs were introduced with, and their argv is compared
# too. The auth fixture digest is compared, never printed.
def settings(meta):
    files = meta.get('file_sha256', {})
    return {'evomaster_input': meta.get('evomaster_input', 'spec'),
            'evomaster_schema_oracles': meta.get('evomaster_schema_oracles', True),
            'budget_seconds': meta['budget_seconds'], 'evomaster_image': meta.get('evomaster_image'),
            'evomaster_argv': json.dumps(meta.get('evomaster_argv')),
            'evomaster_watchdog_seconds': meta.get('evomaster_watchdog_seconds'),
            'source_sha256': meta.get('source_sha256'),
            'generator_input_sha256': meta.get('generator_input_sha256') or files.get('spec.test.json'),
            'sut_jar_sha256': meta.get('sut_jar_sha256'),
            'image_ids': json.dumps({k: v.get('id') for k, v in sorted(meta.get('images', {}).items())}),
            'sut_config_sha256': files.get('sut-config.env'), 'auth_fixture': meta.get('auth_source_sha256'),
            'request_timeout_ms': meta.get('request_timeout_ms'), 'logger_max_body': meta.get('logger_max_body'),
            'emb_commit': meta.get('emb_commit')}


def settings_digest(meta):
    return hashlib.sha256(json.dumps(settings(meta), sort_keys=True).encode()).hexdigest()[:12]


# Collection-relevant harness files; documentation/proposal/test files are excluded from drift reporting.
HARNESS_RELEVANT = ('run_pilot.sh', 'fuzzer_args.sh', 'common.sh', 'run_metadata.py', 'redact_auth.py',
                    'auth_header.py', 'derecurse.py', 'evomaster_guard.py', 'prepare_dist.sh')


def harness_drift(a, b):
    ha, hb = a.get('harness_sha256', {}), b.get('harness_sha256', {})
    out = [k for k in HARNESS_RELEVANT if ha.get(k) != hb.get(k)]
    out += [f'tool:{k}' for k in ('mitm_fulllog.py',) if a.get('tool_sha256', {}).get(k) != b.get('tool_sha256', {}).get(k)]
    return out


def same_seed_replicates(base, bmeta, pool):
    return [(p, m) for p, m in pool if p != base and m['seed'] == bmeta['seed'] and settings(m) == settings(bmeta)]


def evo_baselines(sut):
    out = []
    for p in sorted((RUNS / sut).glob('*_baseline_NONE_p0_s*/run.json')):
        meta = json.load(open(p))
        if meta.get('fuzzer') == 'evomaster' and meta.get('complete') and (p.parent / 'exchanges.jsonl').is_file():
            out.append((p.parent.resolve(), meta))
    return out


def main():
    c.INT_FORMATS = True
    rows = [r for r in csv.DictReader(open(HERE / 'fuzzer_compare.csv')) if r['fuzzer'] == 'evomaster']
    rows.sort(key=lambda r: (r['sut'], r['run']))
    pool = {}
    out = []
    for r in rows:
        run = RUNS / r['sut'] / r['run']
        inputs = [p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut')]
        base = Path(dict(l.split('=', 1) for l in inputs[0].read_text().splitlines())['baseline']).resolve()
        bmeta = json.load(open(base / 'run.json'))
        if r['sut'] not in pool:
            pool[r['sut']] = evo_baselines(r['sut'])
        reps = same_seed_replicates(base, bmeta, pool[r['sut']])
        if not reps:
            continue
        manifest = json.load(open(run / 'manifest.json'))
        bv = base_violations(base, r['sut'])
        ref = []
        for o, _ in reps:
            d = counts(attribute.attribute(bv, base_violations(o, r['sut']), manifest, 'fresh'))
            ref.append((d['mut_NEW'], d['mut_NEW_checkable']))
        row = {k: r[k] for k in ('sut', 'fault', 'severity', 'seed', 'run', 'manifest_sig',
                                 'fresh_mut_NEW', 'fresh_mut_NEW_checkable')}
        row.update(baseline_run=base.name, replicate_runs=';'.join(o.name for o, _ in reps),
                   settings_digest=settings_digest(bmeta),
                   harness_drift=';'.join(sorted({f for _, m in reps for f in harness_drift(bmeta, m)})),
                   replicates=len(ref), same_seed_max_NEW=max(x[0] for x in ref),
                   same_seed_max_NEW_checkable=max(x[1] for x in ref),
                   beyond_same_seed_ref=int(r['fresh_mut_NEW_checkable']) > max(x[1] for x in ref))
        out.append(row)
        print(f"{r['sut']:<17} {r['fault']:<16} s{r['seed']} fresh checkable {r['fresh_mut_NEW_checkable']} | "
              f"same-seed ref checkable {[x[1] for x in ref]} raw {[x[0] for x in ref]}", flush=True)
    if not out:
        print('no replicate baselines found')
        return
    with open(HERE / 'fuzzer_noise_same_seed.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(list)
    for r in out:
        agg[(r['sut'], r['fault'])].append(r)
    print('== summary: sut fault | runs | beyond same-seed ref (checkable NEW) | max same-seed ref')
    for k in sorted(agg):
        a = agg[k]
        print(f"   {k[0]:<17} {k[1]:<16} | {len(a)} | {sum(x['beyond_same_seed_ref'] for x in a)}/{len(a)} | "
              f"{max(x['same_seed_max_NEW_checkable'] for x in a)}")
    print('->', HERE / 'fuzzer_noise_same_seed.csv')


if __name__ == '__main__':
    main()
