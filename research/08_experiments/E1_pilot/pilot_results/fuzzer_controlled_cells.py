#!/usr/bin/env python3
"""Controlled fuzzer comparison (Claude, 2026-11-15, after T29 F2).

Reads fuzzer_noise_cross_seed.csv. Pairs EvoMaster and Schemathesis rows with the same (sut, fault, severity, seed).
A pair is CONTROLLED when both runs carry an identical mutation set (manifest_sig); otherwise it is descriptive only.
Signal = fresh mutated-op checkable NEW > observed cross-seed reference max (checkable), per run.
Expected-kind signal (2026-11-15) = the same rule restricted to fuzzer_compare.EXPECTED_KINDS[fault] on both sides.
Denominators (T34 F4):
- PRIMARY = one pair per unique cell, using the earliest run (by run id = batch timestamp) of each fuzzer in that
  cell. This is a fixed tie-break rule, chosen without reference to outcomes, for the only duplicated cell:
  petstore LOOSE p30 s1, two Schemathesis batches.
- SECONDARY = every evo x sch pair-instance (the earlier report's denominator).
Output: fuzzer_controlled_cells.csv (column 'primary') and totals on stdout. Offline.
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
        first_e = min((r['run'] for r in evo), default=None)
        first_s = min((r['run'] for r in sch), default=None)
        for e in evo:
            for s in sch:
                out.append({'sut': k[0], 'fault': k[1], 'severity': k[2], 'seed': k[3],
                            'primary': e['run'] == first_e and s['run'] == first_s,
                            'controlled': e['manifest_sig'] == s['manifest_sig'],
                            'evo_run': e['run'], 'sch_run': s['run'],
                            'evo_fresh_checkable_NEW': e['fresh_mut_NEW_checkable'],
                            'evo_ref_max': e['noise_max_mut_NEW_checkable'],
                            'evo_signal': e['beyond_ref_NEW_checkable'] == 'True',
                            'sch_fresh_checkable_NEW': s['fresh_mut_NEW_checkable'],
                            'sch_ref_max': s['noise_max_mut_NEW_checkable'],
                            'sch_signal': s['beyond_ref_NEW_checkable'] == 'True',
                            'evo_signal_expected': e['beyond_ref_NEW_expected'] == 'True',
                            'sch_signal_expected': s['beyond_ref_NEW_expected'] == 'True',
                            'evo_kinds': e['fresh_mut_kinds'], 'sch_kinds': s['fresh_mut_kinds'],
                            'evo_replay_NEW': e['replay_mut_NEW'], 'sch_replay_NEW': s['replay_mut_NEW'],
                            'evo_exchanges': e['mutated_exchanges'], 'sch_exchanges': s['mutated_exchanges']})
    with open(HERE / 'fuzzer_controlled_cells.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for prim, ctl, exp in ((True, True, False), (True, False, False), (False, True, False), (False, False, False),
                           (True, True, True), (True, False, True)):
        agg = defaultdict(lambda: [0, 0, 0])
        for r in out:
            if r['controlled'] is ctl and (r['primary'] or not prim):
                a = agg[(r['sut'], r['fault'])]
                a[0] += r['evo_signal_expected' if exp else 'evo_signal']
                a[1] += r['sch_signal_expected' if exp else 'sch_signal']
                a[2] += 1
        print(('== PRIMARY (unique cells) ' if prim else '== SECONDARY (all pair-instances) ') +
              ('controlled (identical manifest)' if ctl else 'manifest differs (descriptive only)') +
              (' — EXPECTED-KIND signal' if exp else ' — checkable signal'))
        te = ts = tn = 0
        for k in sorted(agg):
            e, s, n = agg[k]
            te, ts, tn = te + e, ts + s, tn + n
            print(f'   {k[0]:<17} {k[1]:<16} | EvoMaster {e}/{n} | Schemathesis {s}/{n}')
        print(f'   TOTAL | EvoMaster {te}/{tn} | Schemathesis {ts}/{tn}')
    print('->', HERE / 'fuzzer_controlled_cells.csv')


if __name__ == '__main__':
    main()
