#!/usr/bin/env python3
"""T32: offline exposure to REQUEST_STRICT edits in controlled fuzzer cells.

Run: nice -n 10 /usr/bin/python3 -I -B strict_exposure.py \
    --audit-json /absolute/path/to/09_collab/logs/T32_scratch/audit.json

CSV row_type: run, operation, manifest_edit (every literal manifest edit),
constraint (resolved semantic strict edits, including those inside added properties).
Fresh/baseline counts are UNIQUE REQUESTS within each row, never sums of errors.
The original-valid gate covers one entire edited parameter or selected body schema,
not unrelated parameters. `constraint_breaches` also counts new-constraint errors
in locations already invalid originally; these do NOT enter `violating_requests`.
An unsupported/incomplete location is uncheckable, never evidence of compliance.
No directory scan of runs; only the 18 named runs and their recorded baselines.
Only the CSV and optional audit JSON are written. No network or SUT execution.
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOOLS = ROOT / 'tools'
sys.path.insert(0, str(TOOLS))
import conformance as c  # noqa: E402
import specmut  # noqa: E402

SUTS = {'swagger-petstore', 'market', 'cwa-verification'}
MISSING = object()
METRICS = ('requests_to_mutated_ops', 'applicable_requests', 'evaluated_requests',
           'original_invalid_requests', 'uncheckable_requests', 'constraint_breaches',
           'violating_requests', 'violating_2xx', 'violating_4xx', 'violating_other')


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def pointer_get(node, pointer, default=MISSING):
    for part in pointer.lstrip('/').split('/') if pointer else []:
        part = part.replace('~1', '/').replace('~0', '~')
        try:
            node = node[int(part)] if isinstance(node, list) else node[part]
        except (KeyError, IndexError, ValueError, TypeError):
            return default
    return node


def signature(manifest):
    return sorted(compact({k: m[k] for k in ('path', 'method', 'fault', 'edits')})
                  for m in manifest['mutations'])


def strict_changes(before, after, pointer=''):
    """Extract the exact three schema keywords changed by specmut.mutate_strict.

    Resolve local refs before calling; literal ref expansion is not a constraint.
    Walk precisely the schema positions used by the repository's strict mutator.
    """
    for suffix, node in specmut.walk_schema(after, ''):
        old = pointer_get(before, suffix, {})
        for keyword in ('maximum', 'maxLength', 'required'):
            av = node.get(keyword, MISSING)
            bv = old.get(keyword, MISSING) if isinstance(old, dict) else MISSING
            if av is not MISSING and av != bv:
                if keyword == 'required':
                    if not isinstance(av, list):
                        raise ValueError('unexpected changed non-list required')
                    if not set(bv if isinstance(bv, list) else []).issubset(av):
                        raise ValueError('required edit is not stricter')
                elif bv is not MISSING and av > bv:
                    raise ValueError('bound edit is not stricter')
                yield pointer + suffix + '/' + keyword, bv, av


def build_locations(original, mutated, mutation):
    """Each location is independently validated using request_problems on BOTH specs."""
    path, method = mutation['path'], mutation['method']
    op_old, params_old = original.operation(path, method)
    op_new, params_new = mutated.operation(path, method)
    old_by_key = {(p['in'], p['name']): p for p in params_old}
    prefix = specmut.ptr('paths', path, method)
    # Saved manifests index operation-level parameters after inherited-parameter merge.
    raw_params = mutated.raw['paths'][path][method].get('parameters', [])
    raw_indices = {(p['in'], p['name']): i for i, p in enumerate(raw_params)}
    locations = []
    for p in params_new:
        old = old_by_key[(p['in'], p['name'])]
        base = prefix + '/parameters/' + str(raw_indices[(p['in'], p['name'])])
        loc = {'name': p['in'] + ':' + p['name'], 'media': '', 'old_params': [old],
               'new_params': [p], 'old_op': {k: op_old[k] for k in ('consumes',) if k in op_old},
               'new_op': {k: op_new[k] for k in ('consumes',) if k in op_new}, 'changes': []}
        error_prefix = '/requestBody' if p['in'] == 'body' else '/parameters' + specmut.ptr(p['in'], p['name'])
        if bool(p.get('required')) != bool(old.get('required')):
            if p.get('required') is not True:
                raise ValueError('unexpected required relaxation')
            loc['changes'].append((base + '/required', old.get('required', MISSING), True,
                                   error_prefix + '/required'))
        os = specmut.resolve(original.raw, old.get('schema', {k: old[k] for k in c.PARAM_SCHEMA_KEYS if k in old}))
        ns = specmut.resolve(mutated.raw, p.get('schema', {k: p[k] for k in c.PARAM_SCHEMA_KEYS if k in p}))
        schema_base = base + ('/schema' if 'schema' in p else '')
        for suffix, bv, av in strict_changes(os, ns):
            loc['changes'].append((schema_base + suffix, bv, av, error_prefix + suffix))
        if loc['changes']:
            locations.append(loc)
    if mutated.oas3 and 'requestBody' in op_new:
        rb_old, rb_new = op_old['requestBody'], op_new['requestBody']
        if rb_old.get('required', False) != rb_new.get('required', False):
            raise ValueError('body presence changed outside strict mutator policy')
        for media, entry in rb_new['content'].items():
            os = specmut.resolve(original.raw, rb_old['content'][media].get('schema', {}))
            ns = specmut.resolve(mutated.raw, entry.get('schema', {}))
            base = prefix + '/requestBody/content' + specmut.ptr(media) + '/schema'
            changes = [(base + suffix, bv, av, '/requestBody' + suffix)
                       for suffix, bv, av in strict_changes(os, ns)]
            if changes:
                locations.append({'name': 'body', 'media': media, 'changes': changes,
                                  'old_params': [], 'new_params': [],
                                  'old_op': {'requestBody': rb_old}, 'new_op': {'requestBody': rb_new}})
    return locations, op_new


def paired_baseline(run, runs, sut):
    inputs = sorted(p for p in run.glob('analysis-*/inputs.txt')
                    if not p.parent.name.endswith('-sut'))
    if not inputs:
        raise ValueError('no recorded baseline: ' + str(run))
    pairs = []
    for p in inputs:
        values = dict(line.split('=', 1) for line in p.read_text().splitlines() if '=' in line)
        if Path(values['mutated']).resolve() != run:
            raise ValueError('recorded mutated path mismatch')
        base = Path(values['baseline']).resolve()
        if base.parent != (runs / sut).resolve():
            raise ValueError('baseline outside allowed SUT directory')
        pairs.append(base)
    if len(set(pairs)) != 1:
        raise ValueError('ambiguous recorded baseline')
    return pairs[0], inputs


def request_key(location, req, path_params):
    """Keep only inputs read by request_problems for this location; cache pure results."""
    headers = {k.lower(): v for k, v in req.get('headers', {}).items()}
    body = req.get('body', {})
    if location['name'] == 'body' or location['name'].startswith('body:'):
        reduced = {'headers': {'content-type': headers.get('content-type', '')},
                   'body': {k: body[k] for k in ('text', 'truncated', 'decode_error') if k in body}}
        return compact((reduced, {}))
    param = location['new_params'][0]
    name, where = param['name'], param['in']
    reduced = {'body': {}}
    pp = {}
    if where == 'query':
        reduced['query'] = {name: req.get('query', {}).get(name)}
    elif where == 'path':
        pp = {name: path_params[name]} if name in path_params else {}
    elif where in ('header', 'cookie'):
        key = name.lower() if where == 'header' else 'cookie'
        reduced['headers'] = {key: headers[key]} if key in headers else {}
    else:
        raise ValueError('unhandled parameter location: ' + where)
    return compact((reduced, pp))


def analyse_run(cell, fuzzer, run, baseline, original, mutated, manifest, remember):
    rows, counters, examples = [], defaultdict(Counter), {}
    violating_statuses = defaultdict(Counter)
    common = {'sut': cell['sut'], 'seed': cell['seed'], 'severity': cell['severity'],
              'fuzzer': fuzzer, 'run': run.name, 'baseline_run': baseline.name}

    def add_row(row_type, row_id, **fields):
        row = {**common, 'row_type': row_type, 'row_id': row_id, **fields}
        rows.append(row)
        return row_id

    run_id = f"{cell['sut']}.s{cell['seed']}.{fuzzer}"
    add_row('run', run_id, semantic_constraints=0, manifest_edits=sum(len(m['edits']) for m in manifest['mutations']))
    operations, all_locations = {}, []
    for mi, mutation in enumerate(manifest['mutations'], 1):
        oid = add_row('operation', run_id + f'.o{mi}', method=mutation['method'].upper(),
                      path=mutation['path'], manifest_edits=len(mutation['edits']))
        locs, op = build_locations(original, mutated, mutation)
        raw_rows = []
        for ei, edit in enumerate(mutation['edits'], 1):
            eid = add_row('manifest_edit', oid + f'.e{ei}', method=mutation['method'].upper(),
                          path=mutation['path'], pointer=edit['pointer'], edit_op=edit['op'],
                          before_exists=edit['before_exists'], after_exists=edit['after_exists'],
                          before=compact(edit['before']), after=compact(edit['after']), semantic_constraints=0)
            raw_rows.append((eid, edit))
        for loc in locs:
            loc['constraints'] = []
            loc['operation_id'] = oid
            loc['operation'] = op
            loc['index'] = len(all_locations)
            for ci, (pointer, bv, av, error_pointer) in enumerate(loc['changes'], 1):
                owners = [(eid, e) for eid, e in raw_rows
                          if pointer == e['pointer'] or pointer.startswith(e['pointer'] + '/')]
                if not owners:
                    raise ValueError('semantic edit lacks manifest owner: ' + pointer)
                eid, edit = max(owners, key=lambda x: len(x[1]['pointer']))
                cid = add_row('constraint', oid + f'.l{loc["index"] + 1}.c{ci}',
                              method=mutation['method'].upper(), path=mutation['path'],
                              pointer=pointer, parent_manifest_edit=eid, location=loc['name'],
                              media_type=loc['media'], error_pointer=error_pointer,
                              before_exists=bv is not MISSING, after_exists=True,
                              before=compact(None if bv is MISSING else bv), after=compact(av),
                              semantic_constraints=1)
                loc['constraints'].append({'id': cid, 'owner': eid, 'error_pointer': error_pointer,
                                           'keyword': pointer.rsplit('/', 1)[-1],
                                           'added_required': set(av) - set(bv if isinstance(bv, list) else [])
                                           if isinstance(av, list) else None})
            all_locations.append(loc)
        operations[(mutation['path'], mutation['method'].upper())] = (oid, locs)
    for row in rows:
        if row['row_type'] != 'constraint':
            row['semantic_constraints'] = sum(r['row_type'] == 'constraint' and
                (row['row_type'] == 'run' or
                 (row['row_type'] == 'operation' and r['row_id'].startswith(row['row_id'] + '.')) or
                 r.get('parent_manifest_edit') == row['row_id']) for r in rows)
            if row['row_type'] == 'manifest_edit':
                row['edit_role'] = 'strict_constraint' if row['semantic_constraints'] else 'structural_or_annotation'

    @lru_cache(maxsize=8192)
    def validate(index, key):
        loc = all_locations[index]
        req, pp = json.loads(key)
        ex = {'request': req}
        old = c.request_problems(original, loc['old_params'], loc['old_op'], ex, pp)
        new = c.request_problems(mutated, loc['new_params'], loc['new_op'], ex, pp)
        hits = []
        for item in loc['constraints']:
            if any(pointer == item['error_pointer'] and identity.get('keyword') == item['keyword']
                   and (item['added_required'] is None or identity.get('property') in item['added_required'])
                   for pointer, message, identity in new):
                hits.append(item['id'])
        return bool(old), tuple(old.uncheckable + new.uncheckable), tuple(hits)

    traffic = {}
    for side, traffic_run in (('fresh', run), ('baseline', baseline)):
        capture = traffic_run / 'exchanges.jsonl'
        digest, total, matched = hashlib.sha256(), 0, Counter()
        with capture.open('rb') as stream:
            for line_no, raw in enumerate(stream, 1):
                digest.update(raw)
                exchange = json.loads(raw)
                total += 1
                req = exchange['request']
                template, pp = mutated.match(req['path'], req['method'], req.get('origin'))
                operation = operations.get((template, req['method'].upper()))
                if operation is None:
                    continue
                oid, locs = operation
                matched[oid] += 1
                flags = defaultdict(set)
                status = int(exchange['response']['status'])
                for loc in locs:
                    if loc['media']:
                        headers = {k.lower(): v for k, v in req.get('headers', {}).items()}
                        ctype = headers.get('content-type', '').split(';')[0].strip().lower()
                        selected, schema = c.select_media(loc['operation']['requestBody']['content'], ctype)
                        if selected != loc['media']:
                            continue
                    invalid_old, unknown, hits = validate(loc['index'], request_key(loc, req, pp))
                    for item in loc['constraints']:
                        ids = (run_id, oid, item['owner'], item['id'])
                        for rid in ids:
                            flags[rid].add('applicable_requests')
                            flags[rid].add('uncheckable_requests' if unknown else 'evaluated_requests')
                            if invalid_old:
                                flags[rid].add('original_invalid_requests')
                            if item['id'] in hits:
                                flags[rid].add('constraint_breaches')
                                if not invalid_old and not unknown:
                                    flags[rid].add('violating_requests')
                                    flags[rid].add('violating_2xx' if 200 <= status < 300 else
                                                   'violating_4xx' if 400 <= status < 500 else 'violating_other')
                        if unknown:
                            for rid in ids:
                                examples.setdefault((side, rid, 'uncheckable_requests'),
                                                    {'capture': str(capture.relative_to(ROOT.parent)),
                                                     'line': line_no, 'status': status, 'reasons': unknown})
                for rid, names in flags.items():
                    if 'violating_requests' in names:
                        violating_statuses[(side, rid)][str(status)] += 1
                    for name in names:
                        counters[(side, rid)][name] += 1
                        if name in ('violating_2xx', 'violating_4xx', 'violating_other', 'constraint_breaches'):
                            examples.setdefault((side, rid, name),
                                                {'capture': str(capture.relative_to(ROOT.parent)),
                                                 'line': line_no, 'status': status})
        for row in rows:
            key = (side, row['row_id'])
            counters[key]['requests_to_mutated_ops'] = (sum(matched.values()) if row['row_type'] == 'run'
                                                        else matched[operations[(row['path'], row['method'])][0]])
            for metric in METRICS:
                row[side + '_' + metric] = counters[key][metric]
            row[side + '_violating_status_counts'] = compact(dict(violating_statuses[key]))
            assert row[side + '_violating_requests'] == sum(row[side + '_violating_' + k] for k in ('2xx', '4xx', 'other'))
            for name in ('violating_2xx', 'violating_4xx', 'violating_other', 'uncheckable_requests'):
                evidence = examples.get((side, row['row_id'], name))
                row[side + '_first_' + name + '_line'] = evidence['line'] if evidence else ''
        traffic[side] = {'path': str(capture.relative_to(ROOT.parent)), 'sha256': digest.hexdigest(), 'exchanges': total}
        remember(capture, digest.hexdigest())
    audit = {'run_id': run_id, 'traffic': traffic, 'validation_cache': validate.cache_info()._asdict(),
             'examples': [{'side': side, 'row_id': rid, 'metric': metric, **value}
                          for (side, rid, metric), value in sorted(examples.items())]}
    return rows, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cells', type=Path, default=HERE / 'fuzzer_controlled_cells.csv')
    parser.add_argument('--output', type=Path, default=HERE / 'strict_exposure.csv')
    parser.add_argument('--audit-json', type=Path)
    args = parser.parse_args()
    c.INT_FORMATS = True
    runs = HERE.parent / 'runs'
    hashes = {}

    def remember(path, digest=None):
        value = digest or hashlib.sha256(path.read_bytes()).hexdigest()
        key = str(path.resolve().relative_to(ROOT.parent))
        if key in hashes and hashes[key] != value:
            raise ValueError('input changed during analysis: ' + key)
        hashes[key] = value

    remember(args.cells)
    for path in (Path(__file__), TOOLS / 'conformance.py', TOOLS / 'specmut.py'):
        remember(path)
    with args.cells.open(newline='') as stream:
        cells = [r for r in csv.DictReader(stream) if r['fault'] == 'REQUEST_STRICT' and r['controlled'] == 'True']
    if len(cells) != 9 or {(r['sut'], r['seed']) for r in cells} != {(s, str(n)) for s in SUTS for n in (1, 2, 3)}:
        raise ValueError('expected exactly nine controlled STRICT cells for the allowed SUTs')
    all_rows, audits = [], []
    for cell in cells:
        manifests = []
        for short, fuzzer in (('evo', 'evomaster'), ('sch', 'schemathesis')):
            name = cell[short + '_run']
            if Path(name).name != name:
                raise ValueError('nonlocal run name')
            run = (runs / cell['sut'] / name).resolve()
            base, inputs = paired_baseline(run, runs, cell['sut'])
            for path in [run / 'run.json', base / 'run.json', run / 'manifest.json',
                         run / 'spec.original.json', run / 'spec.test.json', base / 'spec.original.json', *inputs]:
                remember(path)
            meta, bmeta = [json.loads((p / 'run.json').read_text()) for p in (run, base)]
            if not meta['complete'] or not bmeta['complete'] or str(meta['seed']) != cell['seed'] or str(bmeta['seed']) != cell['seed']:
                raise ValueError('incomplete or wrong-seed run pair')
            if meta.get('fuzzer', 'schemathesis') != fuzzer or bmeta.get('fuzzer', 'schemathesis') != fuzzer:
                raise ValueError('wrong fuzzer in run pair')
            old = json.loads((run / 'spec.original.json').read_text())
            new = json.loads((run / 'spec.test.json').read_text())
            if old != json.loads((base / 'spec.original.json').read_text()):
                raise ValueError('paired original specs differ')
            manifest = json.loads((run / 'manifest.json').read_text())
            if manifest['fault'] != 'REQUEST_STRICT' or any(m['fault'] != 'REQUEST_STRICT' for m in manifest['mutations']):
                raise ValueError('non-STRICT manifest')
            manifests.append(signature(manifest))
            for mutation in manifest['mutations']:
                for edit in mutation['edits']:
                    for document, side in ((old, 'before'), (new, 'after')):
                        value = pointer_get(document, edit['pointer'])
                        if (value is not MISSING) != edit[side + '_exists'] or (value is not MISSING and value != edit[side]):
                            raise ValueError('manifest does not describe saved specs: ' + edit['pointer'])
            origin = f"http://sut-{cell['sut']}:8080"
            original, mutated = c.Spec(old, deploy_origin=origin), c.Spec(new, deploy_origin=origin)
            rows, audit = analyse_run(cell, fuzzer, run, base, original, mutated, manifest, remember)
            if audit['traffic']['fresh']['exchanges'] != int(cell[short + '_exchanges']):
                raise ValueError('exchange count differs from controlled cell input')
            all_rows.extend(rows)
            audits.append(audit)
            summary = rows[0]
            print(f"{cell['sut']} s{cell['seed']} {fuzzer}: "
                  f"fresh {summary['fresh_violating_requests']}/{summary['fresh_requests_to_mutated_ops']}, "
                  f"baseline {summary['baseline_violating_requests']}/{summary['baseline_requests_to_mutated_ops']}", flush=True)
        if manifests[0] != manifests[1]:
            raise ValueError('controlled-cell manifests are not identical')
    # Detect concurrent source/input changes before publishing results.
    for relative, digest in hashes.items():
        if hashlib.sha256((ROOT.parent / relative).read_bytes()).hexdigest() != digest:
            raise ValueError('input changed: ' + relative)
    fields = list(dict.fromkeys(k for row in all_rows for k in row))
    with args.output.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    if args.audit_json:
        args.audit_json.write_text(json.dumps({'inputs_sha256': hashes, 'runs': audits,
                                               'csv_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                                               'row_counts': dict(Counter(r['row_type'] for r in all_rows))},
                                              ensure_ascii=False, indent=2) + '\n')
    print(f'{len(all_rows)} rows -> {args.output}')


if __name__ == '__main__':
    main()
