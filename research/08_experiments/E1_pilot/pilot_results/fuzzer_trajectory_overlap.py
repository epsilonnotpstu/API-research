#!/usr/bin/env python3
"""Traffic-trajectory overlap: mutated run vs its paired baseline, and the same-seed replicate (Claude, 2026-11-15;
revised after Codex T34 F1-F5).

Descriptive only. It measures how far a mutated run's literal request sequence departs from its paired baseline,
next to how far an unchanged-input same-seed replicate departs from it. It does NOT determine which noise reference is
"right". That fault-class-dependent reading is a ⚠️ HYPOTHESIS (T34 F1): divergence after mutation can be a treatment
effect, and high request overlap does not make fresh attribution equal to replay attribution (responses may differ).

Request key (T34 F2): (method, origin, path, sorted query JSON, request content-type, sha256 of the full captured body
object). The captured body is a dict with text/truncated/size/base64 metadata, serialised with sorted keys. Response
status is NOT in the request key. It is a separate outcome metric: positional identity of (request key, status).
Volatile fields (generated IDs, timestamps) are not normalised, so literal overlap is a lower bound on structural
similarity.
Metrics:
- pos = index-aligned equal keys / min(len);
- jac = distinct-key Jaccard;
- mjac = multiset Jaccard (sum of min counts / sum of max counts) — sensitive to repeats;
- len_ratio = min(len)/max(len).
Reference columns:
- beyond_cross / beyond_same = checkable NEW > that observed reference max;
- beyond_both only when BOTH references exist (else empty);
- beyond_available_refs = NEW > max of the references present, with refs_available naming them.
None of these is a test or an upper bound.
Output: fuzzer_trajectory_overlap.csv and a summary on stdout. Offline, reads runs only, own Python only.
"""
import csv
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE))
from fuzzer_noise_same_seed import evo_baselines, same_seed_replicates  # noqa: E402


def _ctype(headers):
    for k, v in (headers or {}).items():
        if k.lower() == 'content-type':
            return v
    return None


def seq(run):
    """Return [(request_key, status)] for every captured exchange."""
    out = []
    for line in open(run / 'exchanges.jsonl'):
        e = json.loads(line)
        rq, rs = e.get('request') or {}, e.get('response') or {}
        body = hashlib.sha256(json.dumps(rq.get('body'), sort_keys=True).encode()).hexdigest()[:16]
        key = (rq.get('method'), rq.get('origin'), rq.get('path'), json.dumps(rq.get('query'), sort_keys=True),
               _ctype(rq.get('headers')), body)
        out.append((key, rs.get('status')))
    return out


def overlap(a, b):
    """a, b: [(key, status)]. Returns request-key metrics plus a (key, status) positional metric."""
    ka, kb = [x[0] for x in a], [x[0] for x in b]
    n = min(len(ka), len(kb))
    pos = sum(x == y for x, y in zip(ka, kb)) / n if n else 0.0
    pos_status = sum(x == y for x, y in zip(a, b)) / n if n else 0.0
    sa, sb = set(ka), set(kb)
    jac = len(sa & sb) / len(sa | sb) if sa | sb else 0.0
    ca, cb = Counter(ka), Counter(kb)
    mx = sum((ca | cb).values())
    mjac = sum((ca & cb).values()) / mx if mx else 0.0
    ratio = n / max(len(ka), len(kb)) if n else 0.0
    return {'pos': round(pos, 4), 'pos_with_status': round(pos_status, 4), 'jac': round(jac, 4),
            'mjac': round(mjac, 4), 'len_ratio': round(ratio, 4)}


def baseline_of(run):
    inputs = [p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut')]
    return Path(dict(l.split('=', 1) for l in inputs[0].read_text().splitlines())['baseline']).resolve()


def main():
    rows = list(csv.DictReader(open(HERE / 'fuzzer_compare.csv')))
    cross = {r['run']: r for r in csv.DictReader(open(HERE / 'fuzzer_noise_cross_seed.csv'))}
    same = {r['run']: r for r in csv.DictReader(open(HERE / 'fuzzer_noise_same_seed.csv'))}
    rows.sort(key=lambda r: (r['sut'], r['fuzzer'], r['run']))
    cache = {}

    def get(p):
        if p not in cache:
            if len(cache) > 3:
                cache.pop(next(iter(cache)))
            cache[p] = seq(p)
        return cache[p]

    out = []
    for r in rows:
        run = RUNS / r['sut'] / r['run']
        base = baseline_of(run)
        ba, mu = get(base), get(run)
        ov = overlap(ba, mu)
        cr, sr = cross.get(r['run']), same.get(r['run'])
        fresh = int(r['fresh_mut_NEW_checkable'])
        refs = {}
        if cr:
            refs['cross'] = int(cr['noise_max_mut_NEW_checkable'])
        if sr:
            refs['same'] = int(sr['same_seed_max_NEW_checkable'])
        row = {'sut': r['sut'], 'fault': r['fault'], 'severity': r['severity'], 'seed': r['seed'],
               'fuzzer': r['fuzzer'], 'run': r['run'], 'baseline_run': base.name, 'len_base': len(ba),
               'len_mut': len(mu)}
        row.update({f'{k}_vs_base': v for k, v in ov.items()})
        row.update({'fresh_mut_NEW_checkable': fresh, 'cross_ref_max': refs.get('cross', ''),
                    'same_ref_max': refs.get('same', ''),
                    'beyond_cross': fresh > refs['cross'] if 'cross' in refs else '',
                    'beyond_same': fresh > refs['same'] if 'same' in refs else '',
                    'beyond_both': fresh > max(refs.values()) if len(refs) == 2 else '',
                    'refs_available': '+'.join(sorted(refs)),
                    'beyond_available_refs': fresh > max(refs.values()) if refs else ''})
        out.append(row)
        print(f"{r['fuzzer']:<12} {r['sut']:<17} {r['fault']:<16} p{r['severity']} s{r['seed']} "
              f"pos {ov['pos']:.3f} jac {ov['jac']:.3f} mjac {ov['mjac']:.3f} | fresh {fresh} refs {refs}", flush=True)
    with open(HERE / 'fuzzer_trajectory_overlap.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(list)
    for r in out:
        agg[(r['fuzzer'], r['fault'])].append(r)

    def cnt(a, key):
        return f"{sum(x[key] is True for x in a)}/{sum(x[key] != '' for x in a)}"

    print('== summary: fuzzer fault | runs | median pos / pos+status / jaccard / multiset-jaccard | '
          'beyond cross | beyond same | beyond both | beyond available')
    for k in sorted(agg):
        a = agg[k]
        med = {m: statistics.median(x[f'{m}_vs_base'] for x in a) for m in ('pos', 'pos_with_status', 'jac', 'mjac')}
        print(f"   {k[0]:<12} {k[1]:<16} | {len(a)} | {med['pos']:.3f} / {med['pos_with_status']:.3f} / "
              f"{med['jac']:.3f} / {med['mjac']:.3f} | {cnt(a, 'beyond_cross')} | {cnt(a, 'beyond_same')} | "
              f"{cnt(a, 'beyond_both')} | {cnt(a, 'beyond_available_refs')}")
    print('== EvoMaster same-seed replicate baselines (same selector as fuzzer_noise_same_seed.py): '
          'pos / pos+status / jaccard / multiset-jaccard / len ratio')
    seen, pools = set(), {}
    for r in out:
        if r['run'] not in same:
            continue
        base = (RUNS / r['sut'] / r['baseline_run']).resolve()
        if (r['sut'], base) in seen:
            continue
        seen.add((r['sut'], base))
        if r['sut'] not in pools:
            pools[r['sut']] = evo_baselines(r['sut'])
        bmeta = json.load(open(base / 'run.json'))
        for p, _ in same_seed_replicates(base, bmeta, pools[r['sut']]):
            ov = overlap(get(base), get(p))
            print(f"   {r['sut']:<17} s{bmeta['seed']} {base.name} vs {p.name}: {ov['pos']:.3f} / "
                  f"{ov['pos_with_status']:.3f} / {ov['jac']:.3f} / {ov['mjac']:.3f} / {ov['len_ratio']:.3f}", flush=True)
    print('->', HERE / 'fuzzer_trajectory_overlap.csv')


if __name__ == '__main__':
    main()
