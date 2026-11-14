#!/usr/bin/env python3
"""Recount every analysed mutated run with fingerprint- AND occurrence-level metrics.

For each mutated run with analysis-<mode>[-<oracle>]/{replay,fresh}.attributed.csv:
  NEW, VANISHED                 fingerprint level (as before)
  INCREASED, DECREASED          PERSISTENT fingerprints on a mutated op whose occurrence count changed
  CHANGED_UNMUTATED             PERSISTENT fingerprints on an unmutated op whose count changed (noise/specificity)
  UNEXPLAINED                   NEW/VANISHED on an unmutated op
  LABEL_MATCH                   NEW whose label equals the manifest's expected label (replay only)
Writes all_runs_occurrence_metrics.csv next to this script. Diagnostic run directories (prefix _) are skipped.
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
rows = []
for sut_dir in sorted(p for p in RUNS.iterdir() if p.is_dir() and not p.name.startswith('_')):
    for run in sorted(sut_dir.glob('*_mutated_*')):
        m = re.search(r'_mutated_([A-Z_]+)_p(\d+)_s(\d+)', run.name)
        if not m or not (run / 'manifest.json').is_file():
            continue
        fault, sev, seed = m.group(1), int(m.group(2)), int(m.group(3))
        batch = run.name.split('_mutated_')[0]
        meta = json.loads((run / 'run.json').read_text()) if (run / 'run.json').is_file() else {}
        argv = (run / 'schemathesis-argv.txt').read_text() if (run / 'schemathesis-argv.txt').is_file() else ''
        datagen = argv.split('--data-generation-method\n')[1].split('\n')[0] if '--data-generation-method' in argv else 'positive'
        pool = 'pool' if (run / 'only-ops.json').is_file() else 'random'
        for an in sorted(run.glob('analysis-*')):
            oracle = 'default' if an.name.endswith('-default') else ('sut' if 'reject_statuses' in
                     (an / 'inputs.txt').read_text() else 'legacy')
            if oracle == 'sut' and 'reject_statuses=400,422' in (an / 'inputs.txt').read_text():
                oracle = 'sut(=default)'
            for mode in ('replay', 'fresh'):
                f = an / f'{mode}.attributed.csv'
                if not f.is_file():
                    continue
                X = list(csv.DictReader(open(f, newline='')))
                mut = lambda z: z['op_mutated'] == 'True'
                per = [z for z in X if z['status'] == 'PERSISTENT']
                rows.append({
                    'sut': sut_dir.name, 'batch': batch, 'fault': fault, 'severity': sev, 'seed': seed,
                    'data_gen': datagen, 'op_pool': pool, 'oracle': oracle, 'mode': mode,
                    'complete': meta.get('complete'),
                    'NEW': sum(z['status'] == 'NEW' for z in X), 'VANISHED': sum(z['status'] == 'VANISHED' for z in X),
                    'INCREASED': sum(mut(z) and int(z['mutated_occurrences']) > int(z['baseline_occurrences']) for z in per),
                    'DECREASED': sum(mut(z) and int(z['mutated_occurrences']) < int(z['baseline_occurrences']) for z in per),
                    'CHANGED_UNMUTATED': sum(not mut(z) and z['mutated_occurrences'] != z['baseline_occurrences'] for z in per),
                    'UNEXPLAINED': sum(not mut(z) for z in X if z['status'] in ('NEW', 'VANISHED')),
                    'LABEL_MATCH': sum(z['label_L1'] == z['expected_if_injected'] for z in X if z['status'] == 'NEW'),
                    'run': run.name, 'analysis': an.name})
out = HERE / 'all_runs_occurrence_metrics.csv'
with open(out, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f'{len(rows)} rows -> {out}')
