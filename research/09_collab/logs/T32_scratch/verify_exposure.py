"""Independent scalar/body validation of EVERY T32 row, without request_problems.

Uses the same required conformance route matcher, coercion and JSON Schema policy,
but extracts evidence directly and applies validators to each location. The main
script instead isolates request_problems calls and maps their pointer identities.
"""
import csv
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / '08_experiments/E1_pilot'
spec = importlib.util.spec_from_file_location('strict_exposure', PILOT / 'pilot_results/strict_exposure.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
c = s.c
rows = list(csv.DictReader((PILOT / 'pilot_results/strict_exposure.csv').open()))
groups = defaultdict(list)
for row in rows:
    groups[row['run']].append(row)
checked, reports, statuses = 0, [], Counter()


def errors(spec, schema, value):
    out, unknown = [], False
    try:
        for error in spec.errors(schema, value, 'request'):
            pointer = s.specmut.ptr(*error.schema_path) if error.schema_path else ''
            for identity in c.error_identity(error):
                out.append((pointer, identity))
    except Exception:
        unknown = True
    return out, unknown


for name, run_rows in groups.items():
    summary = next(r for r in run_rows if r['row_type'] == 'run')
    sut = summary['sut']
    run = PILOT / 'runs' / sut / name
    base = PILOT / 'runs' / sut / summary['baseline_run']
    old, new = [c.Spec(json.loads((run / filename).read_text()), deploy_origin=f'http://sut-{sut}:8080')
                for filename in ('spec.original.json', 'spec.test.json')]
    ops = {}
    for op_row in (r for r in run_rows if r['row_type'] == 'operation'):
        op_key = (op_row['path'], op_row['method'])
        old_op, old_params = old.operation(*op_key)
        new_op, new_params = new.operation(*op_key)
        locs = defaultdict(list)
        for constraint in run_rows:
            if constraint['row_type'] == 'constraint' and (constraint['path'], constraint['method']) == op_key:
                locs[(constraint['location'], constraint['media_type'])].append(constraint)
        ops[op_key] = (op_row, old_op, new_op, old_params, new_params, locs)

    @lru_cache(maxsize=8192)
    def evaluate(path, method, location, media, evidence_key):
        op_row, old_op, new_op, old_params, new_params, locs = ops[(path, method)]
        constraints = locs[(location, media)]
        hits = set()
        data = json.loads(evidence_key)
        if location == 'body' or location.startswith('body:'):
            capture, ctype = data
            if capture.get('truncated') or capture.get('decode_error'):
                return False, True, ()
            if location == 'body':
                os = old_op['requestBody']['content'][media]['schema']
                ns = new_op['requestBody']['content'][media]['schema']
                required = old_op['requestBody'].get('required', False)
                selected_media = media
            else:
                bp_old = next(p for p in old_params if p['in'] == 'body')
                bp_new = next(p for p in new_params if p['in'] == 'body')
                os, ns = bp_old['schema'], bp_new['schema']
                required = bp_old.get('required', False)
                selected_media = ctype or next(iter(new_op.get('consumes', new.raw.get('consumes', ['application/json']))))
            if not capture.get('text'):
                return bool(required), False, ()
            try:
                value = c.parse_body(capture['text'], ctype or selected_media)
            except ValueError:
                return True, False, ()
            except LookupError:
                return False, True, ()
            prefix = '/requestBody'
        else:
            where, pname = location.split(':', 1)
            op = next(p for p in old_params if (p['in'], p['name']) == (where, pname))
            np = next(p for p in new_params if (p['in'], p['name']) == (where, pname))
            present, value = data
            if not present:
                for item in constraints:
                    if item['pointer'].endswith('/required') and np.get('required') and not op.get('required'):
                        hits.add(item['row_id'])
                return bool(op.get('required')), False, tuple(hits)
            os = op.get('schema', {k: op[k] for k in c.PARAM_SCHEMA_KEYS if k in op})
            ns = np.get('schema', {k: np[k] for k in c.PARAM_SCHEMA_KEYS if k in np})
            if any('content' in p or p.get('schema', {}).get('type') == 'object'
                   or '$ref' in p.get('schema', {}) for p in (op, np)):
                return False, True, ()
            if os.get('type') not in ('string', 'integer', 'number', 'boolean'):
                raise AssertionError('independent check needs scalar parameter, got ' + str(os))
            value = c.coerce(value, c.to_json_schema(ns, new.dialect, direction='request'))
            prefix = '/parameters' + s.specmut.ptr(where, pname)
        old_errors, old_unknown = errors(old, os, value)
        new_errors, new_unknown = errors(new, ns, value)
        for item in constraints:
            bv, av = json.loads(item['before']), json.loads(item['after'])
            added = set(av) - set(bv or []) if isinstance(av, list) else None
            if any(prefix + pointer == item['error_pointer'] and
                   (added is None or identity.get('property') in added) for pointer, identity in new_errors):
                hits.add(item['row_id'])
        return bool(old_errors), old_unknown or new_unknown, tuple(hits)

    for side, directory in (('fresh', run), ('baseline', base)):
        counts = defaultdict(Counter)
        matched = Counter()
        for line_no, raw in enumerate((directory / 'exchanges.jsonl').open(), 1):
            ex = json.loads(raw)
            req = ex['request']
            path, pp = new.match(req['path'], req['method'], req.get('origin'))
            method = req['method'].upper()
            if (path, method) not in ops:
                continue
            op_row, old_op, new_op, old_params, new_params, locs = ops[(path, method)]
            oid = op_row['row_id']
            matched[oid] += 1
            flags = defaultdict(set)
            headers = {k.lower(): v for k, v in req.get('headers', {}).items()}
            ctype = headers.get('content-type', '').split(';')[0].strip().lower()
            for (location, media), constraints in locs.items():
                if media and c.select_media(new_op['requestBody']['content'], ctype)[0] != media:
                    continue
                if location == 'body' or location.startswith('body:'):
                    key = [req.get('body', {}), ctype]
                else:
                    where, pname = location.split(':', 1)
                    if where == 'path':
                        key = [pname in pp, pp.get(pname)]
                    elif where == 'header':
                        key = [pname.lower() in headers, headers.get(pname.lower())]
                    elif where == 'query':
                        value = req.get('query', {}).get(pname)
                        vals = value if isinstance(value, list) else [value] if value is not None else []
                        key = [bool(vals), vals[0] if vals else None]
                    else:
                        raise AssertionError('unexpected location: ' + where)
                invalid_old, unknown, hits = evaluate(path, method, location, media, s.compact(key))
                for item in constraints:
                    for rid in (summary['row_id'], oid, item['parent_manifest_edit'], item['row_id']):
                        flags[rid].add('applicable_requests')
                        flags[rid].add('uncheckable_requests' if unknown else 'evaluated_requests')
                        if invalid_old:
                            flags[rid].add('original_invalid_requests')
                        if item['row_id'] in hits:
                            flags[rid].add('constraint_breaches')
                            if not invalid_old and not unknown:
                                status = int(ex['response']['status'])
                                flags[rid].add('violating_requests')
                                flags[rid].add('violating_2xx' if 200 <= status < 300 else
                                               'violating_4xx' if 400 <= status < 500 else 'violating_other')
            for rid, flags_for_row in flags.items():
                counts[rid].update(flags_for_row)
                if rid == summary['row_id'] and 'violating_requests' in flags_for_row:
                    statuses[(sut, summary['fuzzer'], side, str(ex['response']['status']))] += 1
        for row in run_rows:
            rid = row['row_id']
            counts[rid]['requests_to_mutated_ops'] = (sum(matched.values()) if row['row_type'] == 'run'
                else matched[ops[(row['path'], row['method'])][0]['row_id']])
            for metric in s.METRICS:
                actual, expected = counts[rid][metric], int(row[side + '_' + metric])
                assert actual == expected, (rid, side, metric, actual, expected)
                checked += 1
        reports.append({'run': name, 'side': side, 'matched': sum(matched.values()),
                        'eligible_violations': counts[summary['row_id']]['violating_requests']})
    print(name, 'PASS', flush=True)

out = {'assertions': checked, 'runs': reports,
       'eligible_response_statuses': [{'sut': sut, 'fuzzer': fuzzer, 'side': side, 'status': status, 'count': n}
                                    for (sut, fuzzer, side, status), n in sorted(statuses.items())],
       'csv_sha256': hashlib.sha256((PILOT / 'pilot_results/strict_exposure.csv').read_bytes()).hexdigest()}
(Path(__file__).parent / 'verification.json').write_text(json.dumps(out, indent=2) + '\n')
print('PASS:', checked, 'row/side/metric assertions')
