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

v2 options (2026-11-14): --out/--key/--salt choose a separate package; --example-rule discriminating
picks, for every item, an example exchange that is transport-clean (no control bytes in path/query/headers)
and, for INCREASED items, whose request was answered by the control WITHOUT that fingerprint
(SAME_REQ_DIFF_OUTCOME) or does not occur in the control (NOVEL_REQ); requests that also produced the
fingerprint in the control are never chosen (fixes v1 item E005). The basis is recorded in the key only.
"""
import argparse
import csv
import glob
import hashlib
import json
import random
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--out', default=str(HERE.parent / 'E2_labelling' / 'e5_blind'))
ap.add_argument('--key', default=str(HERE / 'blind_key.csv'))
ap.add_argument('--salt', default='e5-blind-2026-11-14')
ap.add_argument('--example-rule', choices=['first', 'discriminating'], default='first')
args = ap.parse_args()
OUT = Path(args.out)
SKIP = {'target', '.git', '.idea', 'node_modules'}
if OUT.exists() or Path(args.key).exists():
    raise SystemExit(f'{OUT} or {args.key} exists; refusing to overwrite')

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
rng = random.Random(args.salt)


def load_ex(run):
    return [json.loads(l) for l in open(Path(run) / 'exchanges.jsonl')]


def req_key(x):
    q = x['request']
    return json.dumps([q['method'], q['path'], sorted((k, v) for k, v in (q.get('query') or {}).items()),
                       (q.get('body') or {}).get('base64', '')], sort_keys=True, default=str)


def clean(x):
    q = x['request']
    parts = [q['path']] + [str(v) for v in (q.get('query') or {}).values()] + [str(v) for v in (q.get('headers') or {}).values()]
    return not any(ord(c) < 0x20 or ord(c) == 0x7f for p in parts for c in p)


def pick(fp, mut_viol, mut_ex, ctl_fps_by_key, grew):
    cands = [x for x in mut_viol if x['fingerprint'] == fp]
    if args.example_rule == 'first':
        return cands[0], 'FIRST'
    tiers = {}
    for x in cands:
        k = req_key(mut_ex[x['exchange']])
        if not grew:
            t = 'NEW_FP'
        elif k in ctl_fps_by_key:
            if fp in ctl_fps_by_key[k]:
                continue  # control produced the same violation for this request: not discriminating
            t = 'SAME_REQ_DIFF_OUTCOME'
        else:
            t = 'NOVEL_REQ'
        c = clean(mut_ex[x['exchange']])
        tiers.setdefault((t, c), x)
    for t in ('NEW_FP', 'SAME_REQ_DIFF_OUTCOME', 'NOVEL_REQ'):
        for c in (True, False):
            if (t, c) in tiers:
                return tiers[(t, c)], t + ('' if c else '+UNCLEAN')
    return cands[0], 'NO_DISCRIMINATING_EXAMPLE'

pair_dirs = sorted(pairs)
pkg_names = {p: f'K{i:02d}' for i, p in enumerate(rng.sample(pair_dirs, len(pair_dirs)), 1)}
for pdir in pair_dirs:
    seen, decoys_taken = set(), 0
    for seed, v, att in sorted(pairs[pdir], key=lambda t: t[0]):
        rows = list(csv.DictReader(open(att, newline='')))
        mut_viol = [json.loads(l) for l in open(att.parent / 'mutant.violations.jsonl')]
        meta = json.load(open(att.parent / 'analysis.json'))
        mut_ex = load_ex(meta['mutant_run']) if args.example_rule != 'first' else None
        ctl_fps_by_key = {}
        if args.example_rule != 'first':
            ctl_ex = load_ex(meta['control_run'])
            for x in ctl_ex:
                ctl_fps_by_key.setdefault(req_key(x), set())
            for l in open(att.parent / 'control.violations.jsonl'):
                x = json.loads(l)
                ctl_fps_by_key[req_key(ctl_ex[x['exchange']])].add(x['fingerprint'])
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
            ex, basis = pick(fp, mut_viol, mut_ex, ctl_fps_by_key, grew)
            items.append({'package': pkg_names[pdir], 'run': f'r{seed}', 'kind': r['kind'], 'method': r['method'],
                          'template': r['template'], 'status': r['http_status'], 'pointer': r['pointer'],
                          'message': ex.get('message', ''), 'example_exchange': ex.get('exchange', '')})
            key.append({'role': role, 'pair': pdir.name, 'seed': seed, 'change': r['status'] + ('+INCREASED' if grew else ''),
                        'control_occ': r['baseline_occurrences'], 'mutant_occ': r['mutated_occurrences'],
                        'fingerprint': fp, 'example_basis': basis})
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
with open(args.key, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['item_id', 'role', 'pair', 'seed', 'change', 'control_occ', 'mutant_occ', 'fingerprint']
                       + (['example_basis'] if args.example_rule != 'first' else []), extrasaction='ignore')
    w.writeheader()
    w.writerows(sorted(key, key=lambda x: x['item_id']))
roles = [k['role'] for k in key]
print(f"{len(items)} items ({roles.count('target')} targets, {roles.count('decoy')} decoys) in {len(pkg_names)} packages -> {OUT}")
