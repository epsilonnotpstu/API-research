#!/usr/bin/env python3
"""Impact of the checker's int32/int64 format enforcement (conformance.INT_FORMATS, 2026-11-14) on saved runs.

For every complete harness_v2 run of the four SUTs, re-check exchanges.jsonl against spec.original.json
(default oracle 400/422, deploy origin http://<SUT_SERVICE>:8080) with INT_FORMATS False (legacy) and True,
and record fingerprint occurrence counts that differ.

Output: int_format_impact.csv (one row per run x fingerprint that changed) and a per-SUT summary on stdout.
Offline, own Python only (no SUT execution).
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import conformance as c  # noqa: E402

SUTS = {'scout-api': 'sut-scout-api', 'swagger-petstore': 'sut-swagger-petstore', 'market': 'sut-market',
        'cwa-verification': 'sut-cwa-verification'}


def fp_counts(spec, lines):
    out = Counter()
    for line in lines:
        for v in c.check(spec, json.loads(line)):
            out[(v['kind'], v['method'], v['template'], str(v['status']), v['fingerprint'])] += 1
    return out


rows, summary = [], defaultdict(Counter)
for sut, service in SUTS.items():
    for run in sorted((RUNS / sut).iterdir()):
        meta = run / 'run.json'
        if not meta.is_file() or not json.load(open(meta)).get('complete') or not (run / 'exchanges.jsonl').is_file():
            continue
        spec_doc = json.load(open(next(run.glob('spec.original.*'))))
        spec = c.Spec(spec_doc, deploy_origin=f'http://{service}:8080')
        lines = open(run / 'exchanges.jsonl').readlines()
        c.INT_FORMATS = False
        old = fp_counts(spec, lines)
        c.INT_FORMATS = True
        new = fp_counts(spec, lines)
        summary[sut]['runs'] += 1
        changed = False
        for k in sorted(set(old) | set(new)):
            if old[k] != new[k]:
                changed = True
                rows.append({'sut': sut, 'run': run.name, 'kind': k[0], 'method': k[1], 'template': k[2], 'status': k[3],
                             'old_occ': old[k], 'new_occ': new[k], 'fingerprint': k[4]})
                summary[sut][f'{k[0]} {"-" if new[k] < old[k] else "+"}'] += abs(new[k] - old[k])
        summary[sut]['runs_changed'] += changed

with open(HERE / 'int_format_impact.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['sut', 'run', 'kind', 'method', 'template', 'status', 'old_occ', 'new_occ', 'fingerprint'])
    w.writeheader()
    w.writerows(rows)
for sut, cnt in summary.items():
    print(sut, dict(cnt))
ops = Counter((r['sut'], r['kind'], r['method'], r['template'], r['status']) for r in rows)
print('== changed (sut, kind, op, status): runs affected')
for k, n in ops.most_common():
    print('  ', k, n)
print('->', HERE / 'int_format_impact.csv')
