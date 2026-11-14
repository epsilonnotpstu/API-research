#!/usr/bin/env python3
"""Controlled fuzzer comparison (Claude, 2026-11-15, after T29 F2).

Reads fuzzer_noise_cross_seed.csv. Pairs EvoMaster and Schemathesis rows with the same (sut, fault, severity, seed).
A pair is CONTROLLED when both runs carry an identical mutation set (manifest_sig); otherwise it is descriptive only.
Signal = fresh mutated-op checkable NEW > observed cross-seed reference max (checkable), per run.
Output: fuzzer_controlled_cells.csv and totals on stdout. Offline.
"""
import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    rows = list(csv.DictReader(open(HERE / 'fuzzer_noise_cross_seed.csv')))
    idx = defaultdict(list)
    for r in rows:
        idx[(r['sut'], r['fault'], r['severity'], r['seed'])].append(r)
    out = []
    for k in sorted(idx):
        evo = [r for r in idx[k] if r['fuzzer'] == 'evomaster']
        sch = [r for r in idx[k] if r['fuzzer'] == 'schemathesis']
        for e in evo:
            for s in sch:
                out.append({'sut': k[0], 'fault': k[1], 'severity': k[2], 'seed': k[3],
                            'controlled': e['manifest_sig'] == s['manifest_sig'],
                            'evo_run': e['run'], 'sch_run': s['run'],
                            'evo_fresh_checkable_NEW': e['fresh_mut_NEW_checkable'],
                            'evo_ref_max': e['noise_max_mut_NEW_checkable'],
                            'evo_signal': e['beyond_ref_NEW_checkable'] == 'True',
                            'sch_fresh_checkable_NEW': s['fresh_mut_NEW_checkable'],
                            'sch_ref_max': s['noise_max_mut_NEW_checkable'],
                            'sch_signal': s['beyond_ref_NEW_checkable'] == 'True',
                            'evo_replay_NEW': e['replay_mut_NEW'], 'sch_replay_NEW': s['replay_mut_NEW'],
                            'evo_exchanges': e['mutated_exchanges'], 'sch_exchanges': s['mutated_exchanges']})
    with open(HERE / 'fuzzer_controlled_cells.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for ctl in (True, False):
        agg = defaultdict(lambda: [0, 0, 0])
        for r in out:
            if r['controlled'] is ctl:
                a = agg[(r['sut'], r['fault'])]
                a[0] += r['evo_signal']
                a[1] += r['sch_signal']
                a[2] += 1
        print('== controlled (identical manifest)' if ctl else '== manifest differs (descriptive only)')
        te = ts = tn = 0
        for k in sorted(agg):
            e, s, n = agg[k]
            te, ts, tn = te + e, ts + s, tn + n
            print(f'   {k[0]:<17} {k[1]:<16} | EvoMaster {e}/{n} | Schemathesis {s}/{n}')
        print(f'   TOTAL | EvoMaster {te}/{tn} | Schemathesis {ts}/{tn}')
    print('->', HERE / 'fuzzer_controlled_cells.csv')


if __name__ == '__main__':
    main()
