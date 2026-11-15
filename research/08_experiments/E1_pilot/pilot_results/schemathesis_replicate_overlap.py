#!/usr/bin/env python3
"""Schemathesis same-seed replicate trajectory overlap (Claude, 2026-11-15).

Counterpart to the EvoMaster replicate overlap in fuzzer_trajectory_overlap.py. It answers one question: does
Schemathesis (DATA_GEN=all) repeat its request sequence for the same seed, as EvoMaster nearly does?
Uses the same-seed baseline replicates of noise_floor_spec.py: complete baselines with --data-generation-method in
the argv. For every SUT x seed, compares all pairs. Request key and metrics are those of fuzzer_trajectory_overlap (T34 F2 key; statistics.median).
Replicate provenance was verified for noise_floor_spec.py (NOISE_FLOOR_SPEC.md); not re-verified here.
Output: schemathesis_replicate_overlap.csv and a summary on stdout. Offline, reads runs only.
"""
import csv
import itertools
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE))
from fuzzer_trajectory_overlap import overlap, seq  # noqa: E402


def main():
    groups = defaultdict(list)
    for p in sorted(RUNS.glob('*/*_baseline_NONE_p0_s*')):
        argv = p / 'schemathesis-argv.txt'
        if not (argv.is_file() and 'data-generation-method' in argv.read_text()):
            continue
        meta = json.load(open(p / 'run.json'))
        if meta.get('complete') and (p / 'exchanges.jsonl').is_file():
            groups[(p.parent.name, meta['seed'])].append(p)
    out = []
    for (sut, seed), runs in sorted(groups.items()):
        seqs = {r: seq(r) for r in runs}
        for a, b in itertools.combinations(runs, 2):
            ov = overlap(seqs[a], seqs[b])
            out.append({'sut': sut, 'seed': seed, 'run_a': a.name, 'run_b': b.name, 'len_a': len(seqs[a]),
                        'len_b': len(seqs[b]), **ov})
            print(f"{sut:<17} s{seed} {len(seqs[a])}/{len(seqs[b])} pos {ov['pos']:.3f} jac {ov['jac']:.3f} "
                  f"mjac {ov['mjac']:.3f}", flush=True)
    with open(HERE / 'schemathesis_replicate_overlap.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(list)
    for r in out:
        agg[r['sut']].append(r)
    print('== summary: sut | pairs | min / median / max positional identity | median pos+status | median jaccard | '
          'median multiset-jaccard')
    for k in sorted(agg):
        a = agg[k]
        p = [x['pos'] for x in a]
        med = {m: statistics.median(x[m] for x in a) for m in ('pos_with_status', 'jac', 'mjac')}
        print(f"   {k:<17} | {len(p)} | {min(p):.3f} / {statistics.median(p):.3f} / {max(p):.3f} | "
              f"{med['pos_with_status']:.3f} | {med['jac']:.3f} | {med['mjac']:.3f}")
    print('->', HERE / 'schemathesis_replicate_overlap.csv')


if __name__ == '__main__':
    main()
