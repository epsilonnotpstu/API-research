#!/usr/bin/env python3
"""Build the blind E5 labelling package (Claude, coordinator; labellers must NOT read this file).

Items = violations observed in validated mutant runs (default oracle):
  target : NEW, or PERSISTENT with more occurrences, on a manifest-mutated operation
  decoy  : NEW on a non-mutated operation (up to 3 per pair, deterministic)
Deduplicated per pair by fingerprint (first validated seed wins).

Output (labeller-visible): ../E2_labelling/e5_blind/
  items.csv                       item_id, package, run, kind, method, template, status, pointer, message, example_exchange
  K??/source/                     deployed source tree of that build (no target/, no VCS)
  K??/spec.json                   the spec the oracle used
  K??/r<seed>/exchanges.jsonl, compose.log
Key (labeller-hidden): blind_key.csv in this directory.
"""
import csv
import glob
import hashlib
import json
import random
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'E2_labelling' / 'e5_blind'
SKIP = {'target', '.git', '.idea', 'node_modules'}
if OUT.exists():
    raise SystemExit(f'{OUT} exists; refusing to overwrite')

pairs = {}
for vf in sorted(glob.glob(str(HERE / 'work' / '*' / 'pair-validation-s*.json'))):
    v = json.load(open(vf))
    if v['status'] not in ('PASS', 'PASS_WITH_EXCLUSION'):
        continue
    pdir = Path(vf).parent
    att = pdir / f"analysis-s{v['seed']}-default" / 'attribution.csv'
    if att.is_file():
        pairs.setdefault(pdir, []).append((v['seed'], v, att))

items, key = [], []
rng = random.Random('e5-blind-2026-11-14')
pair_dirs = sorted(pairs)
pkg_names = {p: f'K{i:02d}' for i, p in enumerate(rng.sample(pair_dirs, len(pair_dirs)), 1)}
for pdir in pair_dirs:
    seen, decoys_taken = set(), 0
    for seed, v, att in sorted(pairs[pdir], key=lambda t: t[0]):
        rows = list(csv.DictReader(open(att, newline='')))
        mut_viol = [json.loads(l) for l in open(att.parent / 'mutant.violations.jsonl')]
        first_ex = {}
        for x in mut_viol:
            first_ex.setdefault(x['fingerprint'], x)
        excluded = {(e['method'].upper(), e['path']) for e in v.get('excluded_ops', []) or []}
        for r in rows:
            fp = r['fingerprint']
            if fp in seen or (r['method'].upper(), r['template']) in excluded:
                continue
            mutated = r['op_mutated'] == 'True'
            grew = r['status'] == 'PERSISTENT' and int(r['mutated_occurrences']) > int(r['baseline_occurrences'])
            if mutated and (r['status'] == 'NEW' or grew):
                role = 'target'
            elif not mutated and r['status'] == 'NEW' and decoys_taken < 3:
                role = 'decoy'
                decoys_taken += 1
            else:
                continue
            seen.add(fp)
            ex = first_ex.get(fp, {})
            items.append({'package': pkg_names[pdir], 'run': f'r{seed}', 'kind': r['kind'], 'method': r['method'],
                          'template': r['template'], 'status': r['http_status'], 'pointer': r['pointer'],
                          'message': ex.get('message', ''), 'example_exchange': ex.get('exchange', '')})
            key.append({'role': role, 'pair': pdir.name, 'seed': seed, 'change': r['status'] + ('+INCREASED' if grew else ''),
                        'control_occ': r['baseline_occurrences'], 'mutant_occ': r['mutated_occurrences'],
                        'fingerprint': fp})
order = rng.sample(range(len(items)), len(items))
for n, i in enumerate(order, 1):
    items[i]['item_id'] = key[i]['item_id'] = f'E{n:03d}'

OUT.mkdir(parents=True)
for pdir, pkg in pkg_names.items():
    dst = OUT / pkg
    shutil.copytree(pdir / 'source', dst / 'source', ignore=lambda d, names: [n for n in names if n in SKIP])
    used = {it['run'] for it in items if it['package'] == pkg}
    for seed, v, att in pairs[pdir]:
        if f'r{seed}' not in used:
            continue
        run = Path(json.load(open(att.parent / 'analysis.json'))['mutant_run'])
        (dst / f'r{seed}').mkdir(parents=True, exist_ok=True)
        for name in ('exchanges.jsonl', 'compose.log'):
            shutil.copy2(run / name, dst / f'r{seed}' / name)
        if not (dst / 'spec.json').exists():
            shutil.copy2(next(run.glob('spec.original.*')), dst / 'spec.json')
cols = ['item_id', 'package', 'run', 'kind', 'method', 'template', 'status', 'pointer', 'message', 'example_exchange']
with open(OUT / 'items.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(sorted(items, key=lambda x: x['item_id']))
with open(HERE / 'blind_key.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['item_id', 'role', 'pair', 'seed', 'change', 'control_occ', 'mutant_occ', 'fingerprint'])
    w.writeheader()
    w.writerows(sorted(key, key=lambda x: x['item_id']))
roles = [k['role'] for k in key]
print(f"{len(items)} items ({roles.count('target')} targets, {roles.count('decoy')} decoys) in {len(pkg_names)} packages -> {OUT}")
