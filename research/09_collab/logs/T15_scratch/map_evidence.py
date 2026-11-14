"""Replay only the project's checker; never load labeller A's artifacts."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / '08_experiments/E1_pilot/runs/scout-api/20261113T202103Z_baseline_NONE_p0_s1_1642810'
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import conformance

items = list(csv.DictReader((ROOT / '08_experiments/E2_labelling/batch2_baseline_s1_blind.csv').open()))
by_fp = {r['fingerprint']: r['item_id'] for r in items}
spec = conformance.Spec(json.loads((RUN / 'spec.original.json').read_text()))
matches = {r['item_id']: [] for r in items}
signatures = collections.defaultdict(collections.Counter)
examples = {}
unknown = collections.Counter()
exchange_count = 0
for line, raw in enumerate((RUN / 'exchanges.jsonl').open(), 1):
    exchange_count = line
    x = json.loads(raw)
    violations = conformance.check(spec, x)
    req, resp = x['request'], x['response']
    template, pp = spec.match(req['path'], req['method'], req.get('origin'))
    op, params = spec.operation(template, req['method']) if template else (None, [])
    rp = conformance.request_problems(spec, params, op, x, pp) if op else []
    try:
        rb = json.loads(resp['body']['text'])
    except (ValueError, KeyError):
        rb = {}
    # Successful bodies can contain identity information; do not record them.
    error = {k: rb[k] for k in ('code', 'message', 'errors') if k in rb} if isinstance(rb, dict) and int(resp['status']) >= 400 else {}
    signature = json.dumps(error, ensure_ascii=True, sort_keys=True)
    for v in violations:
        item = by_fp.get(v['fingerprint'])
        if not item:
            unknown[v['fingerprint']] += 1
            continue
        matches[item].append(line)
        signatures[item][signature] += 1
        key = (item, signature)
        if key not in examples:
            examples[key] = {'line': line, 'request_path': req['path'], 'query': req.get('query'),
                             'request_body_sha256': hashlib.sha256(req.get('body', {}).get('text', '').encode()).hexdigest(),
                             'request_body_size': req.get('body', {}).get('size'),
                             'request_problems': list(rp), 'request_uncheckable': getattr(rp, 'uncheckable', []),
                             'response_error': error, 'timestamp': x.get('ts')}

data = []
for r in items:
    item = r['item_id']
    assert len(matches[item]) == int(r['occurrences']), (item, len(matches[item]), r['occurrences'])
    data.append({'item_id': item, 'fingerprint': r['fingerprint'], 'exchange_lines': matches[item],
                 'response_signatures': [{'count': count, **examples[(item, sig)]}
                                         for sig, count in signatures[item].most_common()]})
(OUT / 'exchange_map.json').write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n')
summary = {'exchanges': exchange_count, 'items': len(items), 'matched_occurrences': sum(map(len, matches.values())),
           'unmatched_fingerprints': dict(unknown), 'all_occurrence_counts_match': True}
(OUT / 'replay_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
for r, mapped in zip(items, data):
    print(r['item_id'], r['kind'], r['method'], r['template'], r['status'], 'lines', mapped['exchange_lines'][:3])
    for sig in mapped['response_signatures'][:8]:
        print('  ', sig['count'], 'line', sig['line'], json.dumps(sig['response_error'], ensure_ascii=True)[:350])
