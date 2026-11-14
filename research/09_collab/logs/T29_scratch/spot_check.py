"""Independent streaming recount of four unique raw runs; no target main() calls."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RESULTS = ROOT / '08_experiments/E1_pilot/pilot_results'
RUNS = RESULTS.parent / 'runs'
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import conformance as c


def scan(run, spec):
    meta = json.loads((run / 'run.json').read_text())
    checker = c.Spec(json.loads(spec.read_text()), deploy_origin='http://' + meta['sut_service'] + ':8080')
    tally, examples, n = Counter(), {}, 0
    with (run / 'exchanges.jsonl').open() as f:
        for line in f:
            n += 1
            for v in c.check(checker, json.loads(line)):
                tally[v['fingerprint']] += 1
                examples.setdefault(v['fingerprint'], {k: v[k] for k in ('kind', 'method', 'template', 'pointer')})
    return tally, examples, n


def diff(base, other, manifest):
    mapped = {(m['method'].upper(), m['path']) for m in manifest['mutations']}
    for m in manifest['mutations']:
        if m['fault'] == 'METHOD_SEM':
            mapped.update((str(e['after']).upper(), m['path']) for e in m['edits'])
    out, changed = Counter(), []
    for fp in base[0].keys() | other[0].keys():
        v = other[1].get(fp, base[1].get(fp))
        side = 'mut' if (v['method'], v['template']) in mapped else 'unmut'
        a, b = base[0][fp], other[0][fp]
        status = 'NEW' if not a else 'VANISHED' if not b else 'INCREASED' if b > a else 'DECREASED' if b < a else 'SAME'
        out[side + '_' + status] += 1
        if status == 'NEW':
            changed.append(dict(v, baseline_occurrences=a, mutated_occurrences=b, side=side))
    return {'counts': dict(sorted(out.items())), 'new_details': changed}


def main():
    c.INT_FORMATS = True
    rows = list(csv.DictReader((RESULTS / 'fuzzer_compare.csv').open()))
    cw = next(r for r in rows if r['sut'] == 'cwa-verification' and r['fault'] == 'REQUEST_LOOSE' and r['seed'] == '1' and r['fuzzer'] == 'schemathesis')
    em = next(r for r in rows if r['sut'] == 'market' and r['fault'] == 'REQUEST_STRICT' and r['seed'] == '1' and r['fuzzer'] == 'evomaster')
    provenance = json.loads((OUT / 'provenance.json').read_text())['selected']
    cp = next(p for p in provenance if p['run'] == cw['run'])
    ep = next(p for p in provenance if p['run'] == em['run'])
    cb = RUNS / cw['sut'] / cp['baseline']
    cm = RUNS / cw['sut'] / cw['run']
    cpeer = RUNS / cw['sut'] / cp['peers'][0]['run']
    eb = RUNS / em['sut'] / ep['baseline']
    emm = RUNS / em['sut'] / em['run']
    unique_runs = [cb, cm, cpeer, eb]
    assert len(set(unique_runs)) == 4
    before = {str(p): hashlib.sha256((p / 'exchanges.jsonl').read_bytes()).hexdigest() for p in unique_runs}
    cv = scan(cb, next(cb.glob('spec.original.*')))
    fresh = scan(cm, next(cm.glob('spec.test.*')))
    replay = scan(cb, next(cm.glob('spec.test.*')))
    peer = scan(cpeer, next(cpeer.glob('spec.original.*')))
    ev = scan(eb, next(eb.glob('spec.original.*')))
    er = scan(eb, next(emm.glob('spec.test.*')))
    manifest = json.loads((cm / 'manifest.json').read_text())
    result = {'raw_runs_scanned': [str(p.relative_to(ROOT)) for p in unique_runs],
              'cwa_fresh': diff(cv, fresh, manifest), 'cwa_replay': diff(cv, replay, manifest),
              'cwa_noise_one_pair': diff(cv, peer, manifest),
              'market_em_replay': diff(ev, er, json.loads((emm / 'manifest.json').read_text()))}
    assert cv[2] == int(cw['baseline_exchanges']) and fresh[2] == int(cw['mutated_exchanges'])
    for key in ('mut_NEW', 'mut_INCREASED', 'unmut_NEW', 'unmut_INCREASED', 'unmut_DECREASED'):
        assert result['cwa_fresh']['counts'].get(key, 0) == int(cw['fresh_' + key])
    assert result['cwa_replay']['counts']['mut_NEW'] == int(cw['replay_mut_NEW'])
    assert result['market_em_replay']['counts']['mut_NEW'] == int(em['replay_mut_NEW'])
    assert before == {str(p): hashlib.sha256((p / 'exchanges.jsonl').read_bytes()).hexdigest() for p in unique_runs}
    result['read_only_exchange_hashes'] = before
    (OUT / 'spot_check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
