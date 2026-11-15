#!/usr/bin/env python3
"""Per-run fresh mutated-op checkable NEW kinds for strict_ablation.csv rows (Claude, 2026-11-15).
Separates the STRICT-expected kind (INVALID_ACCEPTED) from collateral kinds (e.g. SERVER_ERROR from the pre-existing
HAL `_links` parse path, T35). Output: strict_ablation_kinds.csv and a summary on stdout. Offline.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import attribute  # noqa: E402
import conformance as c  # noqa: E402
from fuzzer_compare import violations  # noqa: E402

R = HERE.parent / 'runs' / 'market'


def main():
    c.INT_FORMATS = True
    out = []
    for r in csv.DictReader(open(HERE / 'strict_ablation.csv')):
        run, base = R / r['run'], R / r['baseline_run']
        man = json.load(open(run / 'manifest.json'))
        bv, _ = violations(base, next(base.glob('spec.original.*')), 'market')
        mv, _ = violations(run, next(run.glob('spec.test.*')), 'market', cache=False)
        k = Counter(x['kind'] for x in attribute.attribute(bv, mv, man, 'fresh')
                    if x['op_mutated'] and x['status'] == 'NEW' and not x['kind'].endswith('_UNCHECKABLE'))
        out.append({'fuzzer': r['fuzzer'], 'variant': r['variant'], 'seed': r['seed'], 'run': r['run'],
                    'new_INVALID_ACCEPTED': k['INVALID_ACCEPTED'], 'new_other': sum(k.values()) - k['INVALID_ACCEPTED'],
                    'kinds': ';'.join(f'{a}:{b}' for a, b in sorted(k.items()))})
        print(out[-1], flush=True)
    with open(HERE / 'strict_ablation_kinds.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(list)
    for x in out:
        agg[(x['fuzzer'], x['variant'])].append(x)
    print('== fuzzer variant | runs with INVALID_ACCEPTED NEW | runs with only other NEW')
    for key in sorted(agg):
        a = agg[key]
        print(f"   {key[0]:<12} {key[1]:<34} | {sum(x['new_INVALID_ACCEPTED'] > 0 for x in a)}/{len(a)} | "
              f"{sum(x['new_INVALID_ACCEPTED'] == 0 and x['new_other'] > 0 for x in a)}/{len(a)}")


if __name__ == '__main__':
    main()
