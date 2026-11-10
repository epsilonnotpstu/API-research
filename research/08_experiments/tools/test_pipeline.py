"""End-to-end check of specmut -> conformance -> attribute in replay mode.

For every spec in SPEC_DIR and every fault class we synthesise exchanges from the
*original* spec (one schema-valid request/response per documented operation, with
an extra undeclared response property, plus a deliberately out-of-range variant),
check them against the original and the mutated spec, and attribute the diff.

Because traffic is identical in both checks, every NEW or VANISHED fingerprint
must sit on an operation listed in the manifest; anything else is a pipeline bug.

Usage: python3 test_pipeline.py SPEC_DIR
"""
import glob
import json
import sys
from pathlib import Path

import attribute
import conformance
import specmut


def instance(schema, depth=0):
    """Minimal schema-valid instance (best effort) for an inlined schema."""
    if not isinstance(schema, dict) or depth > 6:
        return None
    if 'enum' in schema and schema['enum']:
        return schema['enum'][0]
    for key in ('allOf', 'oneOf', 'anyOf'):
        if schema.get(key):
            return instance(schema[key][0], depth + 1)
    t = schema.get('type')
    if isinstance(t, list):
        t = next((x for x in t if x != 'null'), None)
    if t == 'object' or (t is None and 'properties' in schema):
        obj = {k: instance(v, depth + 1) for k, v in schema.get('properties', {}).items()}
        obj = {k: v for k, v in obj.items() if v is not None or k in schema.get('required', [])}
        return obj
    if t == 'array':
        item = instance(schema.get('items', {}), depth + 1)
        return [item] * max(1, schema.get('minItems', 1)) if item is not None else []
    if t in ('integer', 'number'):
        lo = schema.get('minimum', 1)
        hi = schema.get('maximum', lo + 10)
        val = lo if lo <= hi else hi
        return int(val) if t == 'integer' else float(val)
    if t == 'boolean':
        return True
    if t == 'string':
        fmt = schema.get('format')
        if fmt == 'date-time':
            return '2026-01-01T00:00:00Z'
        if fmt == 'date':
            return '2026-01-01'
        if fmt in ('uuid',):
            return '123e4567-e89b-12d3-a456-426614174000'
        if fmt == 'email':
            return 'a@b.co'
        n = max(1, schema.get('minLength', 1))
        return 'a' * min(n, schema.get('maxLength', n))
    return None


def exchanges_for(spec_obj):
    sp = conformance.Spec(spec_obj)
    out = []
    for template in spec_obj.get('paths', {}):
        for method in list(spec_obj['paths'][template]):
            if method not in specmut.HTTP_METHODS:
                continue
            op, params = sp.operation(template, method)
            path, query = sp.base + template, {}
            for p in params:
                schema = p.get('schema') or {k: p[k] for k in conformance.PARAM_SCHEMA_KEYS if k in p}
                val = instance(schema) if schema else 'a'
                if p.get('in') == 'path':
                    path = path.replace('{' + p['name'] + '}', str(val if val is not None else 'a'))
                elif p.get('in') == 'query':
                    query[p['name']] = [str(val).lower() if isinstance(val, bool) else str(val)]
            code = next((c for c in op.get('responses', {}) if str(c).startswith('2')), None)
            if code is None:
                continue
            _, schema = sp.response_schema(op, int(code))
            body = instance(schema) if schema else None
            if isinstance(body, dict):
                body['zz_undeclared'] = 1  # tolerated unless additionalProperties is false
            text = json.dumps(body) if body is not None else ''
            ex = {'request': {'method': method.upper(), 'path': path, 'query': query, 'headers': {},
                              'body': {'text': ''}},
                  'response': {'status': int(code), 'headers': {}, 'body': {'text': text, 'truncated': False}}}
            out.append(ex)
            if query:  # out-of-range variant: every query param gets a long string
                bad = json.loads(json.dumps(ex))
                bad['request']['query'] = {k: ['x' * 300] for k in query}
                out.append(bad)
    return out


def run(spec_path, fault, seed=3):
    base = specmut.load_spec(spec_path)
    mutated, manifest, _ = specmut.mutate(base, fault, 50, seed)
    exchanges = exchanges_for(base)
    b_spec, m_spec = conformance.Spec(base), conformance.Spec(mutated)
    b_viol = [v for ex in exchanges for v in conformance.check(b_spec, ex)]
    m_viol = [v for ex in exchanges for v in conformance.check(m_spec, ex)]
    rows = attribute.attribute(b_viol, m_viol, {'mutations': manifest})
    bad = [r for r in rows if r['status'] in ('NEW', 'VANISHED') and not r['op_mutated']]
    new = sum(r['status'] == 'NEW' for r in rows)
    gone = sum(r['status'] == 'VANISHED' for r in rows)
    return len(exchanges), len(manifest), new, gone, bad


def main(spec_dir):
    total_bad, summary = 0, {}
    for spec_path in sorted(glob.glob(f'{spec_dir}/*.json') + glob.glob(f'{spec_dir}/*.yaml')):
        for fault in specmut.FAULTS:
            try:
                n_ex, n_mut, new, gone, bad = run(spec_path, fault)
            except Exception as exc:
                print('ERROR', Path(spec_path).stem, fault, repr(exc)[:200])
                total_bad += 1
                continue
            s = summary.setdefault(fault, [0, 0, 0, 0])
            s[0] += n_mut; s[1] += new; s[2] += gone; s[3] += len(bad)
            for r in bad[:3]:
                print('UNEXPLAINED', Path(spec_path).stem, fault, r['status'], r['fingerprint'][:150])
            total_bad += len(bad)
    print('\nfault             mutated_ops  NEW  VANISHED  unexplained')
    for fault, (m, n, g, b) in summary.items():
        print(f'{fault:17s} {m:11d} {n:4d} {g:9d} {b:12d}')
    print('PASS' if total_bad == 0 else f'FAIL ({total_bad})')
    return 1 if total_bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
