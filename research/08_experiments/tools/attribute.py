"""attribute — diff violation sets of a baseline and a mutated-spec run, then label with the manifest.

Both runs must exercise the same SUT build; only the spec differs. Then:
  NEW        fingerprint only in the mutated run
               on a mutated operation  -> label = manifest expected label (injected SPEC defect)
               on an untouched op      -> label = UNEXPLAINED (nondeterminism or cross-op effect)
  VANISHED   fingerprint only in the baseline run -> MASKED: the mutation hid a real
             mismatch (e.g. REQUEST_LOOSE hiding INVALID_ACCEPTED) — reported, not labelled
  PERSISTENT in both runs -> pre-existing mismatch, needs manual labelling (codebook §3)

Usage: python3 attribute.py BASELINE_violations.jsonl MUTATED_violations.jsonl MANIFEST.json > attributed.csv
Note: tools that use the spec to generate requests (all black-box fuzzers) send
different traffic under a mutated spec; NEW/VANISHED therefore mixes oracle
changes and traffic changes. Replaying the baseline requests against the
mutated spec isolates oracle-side effects (use conformance.py on the baseline
exchanges with the mutated spec).
"""
import csv
import json
import sys


def load(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def attribute(baseline, mutated, manifest):
    base_fp = {v['fingerprint']: v for v in baseline}
    mut_fp = {v['fingerprint']: v for v in mutated}
    mutated_ops = {}
    for m in manifest['mutations']:
        mutated_ops[(m['method'].upper(), m['path'])] = m
        if m['fault'] == 'METHOD_SEM':  # the operation now lives under the swapped method
            for e in m['edits']:
                mutated_ops[(str(e['after']).upper(), m['path'])] = m
    rows = []
    for fp in sorted(set(base_fp) | set(mut_fp)):
        v = mut_fp.get(fp) or base_fp[fp]
        key = (v['method'], v['template'])
        m = mutated_ops.get(key)
        if fp in mut_fp and fp not in base_fp:
            status = 'NEW'
            l1, l2 = (m['expected_L1'], m['expected_L2']) if m else ('UNEXPLAINED', '')
        elif fp in base_fp and fp not in mut_fp:
            status, l1, l2 = 'VANISHED', 'MASKED' if m else 'UNEXPLAINED', ''
        else:
            status, l1, l2 = 'PERSISTENT', 'NEEDS_MANUAL', ''
        rows.append({'fingerprint': fp, 'status': status, 'kind': v['kind'], 'method': v['method'],
                     'template': v['template'], 'http_status': v['status'], 'pointer': v['pointer'],
                     'op_mutated': bool(m), 'fault': m['fault'] if m else '', 'label_L1': l1, 'label_L2': l2})
    return rows


def main(baseline_path, mutated_path, manifest_path):
    rows = attribute(load(baseline_path), load(mutated_path), json.load(open(manifest_path)))
    w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]) if rows else ['fingerprint'])
    w.writeheader()
    w.writerows(rows)


if __name__ == '__main__':
    main(*sys.argv[1:4])
