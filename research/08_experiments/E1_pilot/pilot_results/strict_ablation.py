#!/usr/bin/env python3
"""REQUEST_STRICT keyword ablation on market (Claude, 2026-11-15; follows T35, uses the T37 knob).

Variants per fuzzer:
- full: the original STRICT runs, i.e. all keyword families;
- required: object-level required lists only;
- maximum+maxLength+param_required: everything except object-level required.
Seeds 1-3, severity 30. For every mutated run, against its paired baseline (analysis inputs.txt), with the current
checker (INT_FORMATS on):
- fresh / replay mutated-op NEW, both raw and checkable (*_UNCHECKABLE excluded, T29 F3), and fresh INCREASED;
- an observed cross-seed reference (other-seed baselines of the same batch @ base spec, same manifest), checkable;
- the status-class mix of fresh requests to mutated operations;
- a market-specific T35 diagnostic: fresh PUT /customer/contacts requests whose JSON body carries `_links`, and
  how many of those got 500.
Output: strict_ablation.csv and a summary on stdout. Offline, reads runs only.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import attribute  # noqa: E402
import conformance as c  # noqa: E402
from fuzzer_compare import counts, fuzzer_of, manifest_signature, violations  # noqa: E402
from fuzzer_noise_cross_seed import base_violations  # noqa: E402

SUT = 'market'


def baseline_of(run):
    inputs = [p for p in run.glob('analysis-*/inputs.txt') if not p.parent.name.endswith('-sut')]
    return Path(dict(l.split('=', 1) for l in inputs[0].read_text().splitlines())['baseline']).resolve() if inputs else None


def traffic(run, manifest):
    ops = {(m['method'].upper(), m['path']) for m in manifest['mutations']}
    st, links, links500 = Counter(), 0, 0
    for line in open(run / 'exchanges.jsonl'):
        e = json.loads(line)
        rq, rs = e.get('request') or {}, e.get('response') or {}
        status = rs.get('status') or 0
        # mutated-op matching by template: the manifest path may contain {params}
        for m, p in ops:
            if rq.get('method') == m and re.fullmatch(re.sub(r'\{[^/]+\}', '[^/]+', p), rq.get('path') or ''):
                st[f'{status // 100}xx'] += 1
                break
        if rq.get('method') == 'PUT' and rq.get('path') == '/customer/contacts':
            t = (rq.get('body') or {}).get('text') or ''
            if '"_links"' in t:
                links += 1
                links500 += status == 500
    return st, links, links500


def main():
    c.INT_FORMATS = True
    out = []
    for meta_path in sorted((RUNS / SUT).glob('*_mutated_REQUEST_STRICT_p30_s*/run.json')):
        run = meta_path.parent.resolve()
        meta = json.load(open(meta_path))
        fz = fuzzer_of(run, meta)
        if not meta.get('complete') or fz is None or not (run / 'exchanges.jsonl').is_file():
            continue
        base = baseline_of(run)
        if base is None:
            continue
        variant = '+'.join(meta['strict_keywords']) if meta.get('strict_keywords') else 'full'
        manifest = json.load(open(run / 'manifest.json'))
        base_spec, mut_spec = next(base.glob('spec.original.*')), next(run.glob('spec.test.*'))
        bv, _ = violations(base, base_spec, SUT)
        mv, mn = violations(run, mut_spec, SUT, cache=False)
        rv, _ = violations(base, mut_spec, SUT, cache=False)
        fresh = counts(attribute.attribute(bv, mv, manifest, 'fresh'))
        replay = counts(attribute.attribute(bv, rv, manifest, 'replay'))
        m = re.match(r'(.*_baseline_NONE_p0_s)(\d+)$', base.name)
        peers = [p for p in base.parent.glob(m.group(1) + '*') if p != base and (p / 'exchanges.jsonl').is_file()
                 and json.load(open(p / 'run.json')).get('complete')]
        ref = [counts(attribute.attribute(base_violations(base, SUT), base_violations(p.resolve(), SUT), manifest,
                                          'fresh'))['mut_NEW_checkable'] for p in sorted(peers)]
        st, links, links500 = traffic(run, manifest)
        edits = Counter(e['pointer'].rsplit('/', 1)[-1] for mu in manifest['mutations'] for e in mu.get('edits', []))
        row = {'fuzzer': fz, 'variant': variant, 'seed': meta['seed'], 'run': run.name, 'baseline_run': base.name,
               'mutated_ops': len(manifest['mutations']), 'selected_no_edit': len(manifest.get('selected_no_edit', [])),
               'edit_keys': ';'.join(f'{k}:{v}' for k, v in sorted(edits.items())),
               'manifest_sig': manifest_signature(manifest), 'mutated_exchanges': mn,
               'fresh_mut_NEW': fresh['mut_NEW'], 'fresh_mut_NEW_checkable': fresh['mut_NEW_checkable'],
               'fresh_mut_INCREASED': fresh['mut_INCREASED'], 'replay_mut_NEW': replay['mut_NEW'],
               'replay_mut_NEW_checkable': replay['mut_NEW_checkable'],
               'cross_ref_max_checkable': max(ref) if ref else '',
               'beyond_cross': (fresh['mut_NEW_checkable'] > max(ref)) if ref else '',
               'mutop_2xx': st['2xx'], 'mutop_4xx': st['4xx'], 'mutop_5xx': st['5xx'],
               'contacts_put_with_links': links, 'contacts_put_with_links_500': links500}
        out.append(row)
        print(f"{fz:<12} {variant:<34} s{meta['seed']} ops {row['mutated_ops']} (no-edit {row['selected_no_edit']}) "
              f"fresh NEWc {row['fresh_mut_NEW_checkable']} INC {row['fresh_mut_INCREASED']} replay NEWc "
              f"{row['replay_mut_NEW_checkable']} ref {row['cross_ref_max_checkable']} | mutop 2xx/4xx/5xx "
              f"{st['2xx']}/{st['4xx']}/{st['5xx']} | _links PUT {links} (500: {links500})", flush=True)
    with open(HERE / 'strict_ablation.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    agg = defaultdict(list)
    for r in out:
        agg[(r['fuzzer'], r['variant'])].append(r)
    print('== summary: fuzzer variant | runs | fresh beyond cross (checkable) | fresh NEWc>0 | replay NEWc>0 | '
          '_links PUT (500)')
    for k in sorted(agg):
        a = agg[k]
        print(f"   {k[0]:<12} {k[1]:<34} | {len(a)} | {sum(x['beyond_cross'] is True for x in a)}/{len(a)} | "
              f"{sum(x['fresh_mut_NEW_checkable'] > 0 for x in a)}/{len(a)} | "
              f"{sum(x['replay_mut_NEW_checkable'] > 0 for x in a)}/{len(a)} | "
              f"{sum(x['contacts_put_with_links'] for x in a)} ({sum(x['contacts_put_with_links_500'] for x in a)})")
    print('->', HERE / 'strict_ablation.csv')


if __name__ == '__main__':
    main()
