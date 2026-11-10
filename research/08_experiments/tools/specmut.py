"""specmut — controlled OpenAPI specification mutation with a ground-truth manifest.

Supports Swagger 2.0 and OpenAPI 3.x (JSON or YAML). Fault classes follow the
taxonomy of Mazhar, Wang & Mäntylä, "Fault Injection in OpenAPI Specifications
for Evaluating Black-Box Testing Effectiveness" (arXiv 2607.12101, CC-BY 4.0);
this is an independent re-implementation that additionally records every edit
(operation, JSON pointer, before/after, expected triage label) so that failures
observed after mutation can be attributed to the specification (R1 codebook §5).

Usage:
  python3 specmut.py SPEC --fault REQUEST_LOOSE --severity 30 --seed 1 --out OUT_DIR
"""
import argparse
import copy
import hashlib
import json
import random
from pathlib import Path

import yaml

HTTP_METHODS = ('get', 'put', 'post', 'delete', 'patch', 'head', 'options')
FAULTS = ('REQUEST_LOOSE', 'REQUEST_STRICT', 'RESPONSE_ORACLE', 'METHOD_SEM')
LOOSE_KEYS = ('minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'minLength', 'maxLength',
              'pattern', 'enum', 'format', 'minItems', 'maxItems', 'multipleOf')
EXPECTED = {  # fault class -> (L1, L2) per R1_triage_codebook.md §5
    'REQUEST_LOOSE': ('SPEC', 'S-REQ-LOOSE'),
    'REQUEST_STRICT': ('SPEC', 'S-REQ-STRICT'),
    'RESPONSE_ORACLE': ('SPEC', 'S-STATUS|S-RESP-TYPE'),
    'METHOD_SEM': ('SPEC', 'S-METHOD'),
}
METHOD_SWAP = {'get': 'post', 'post': 'get', 'put': 'patch', 'patch': 'put', 'delete': 'get'}


def load_spec(path):
    text = Path(path).read_text(encoding='utf-8')
    return json.loads(text) if path.endswith('.json') else yaml.safe_load(text)


def is_oas3(spec):
    return str(spec.get('openapi', '')).startswith('3')


def ptr(*parts):
    return '/' + '/'.join(str(p).replace('~', '~0').replace('/', '~1') for p in parts)


def resolve(spec, node, depth=0):
    """Return a deep copy of node with local $refs inlined (cycles cut at depth 8)."""
    if depth > 8:
        return {}
    if isinstance(node, dict):
        if '$ref' in node and isinstance(node['$ref'], str) and node['$ref'].startswith('#/'):
            target = spec
            for part in node['$ref'][2:].split('/'):
                target = target.get(part.replace('~1', '/').replace('~0', '~'), {})
            return resolve(spec, target, depth + 1)
        return {k: resolve(spec, v, depth) for k, v in node.items()}
    if isinstance(node, list):
        return [resolve(spec, v, depth) for v in node]
    return node


def operations(spec):
    for path in sorted(spec.get('paths', {})):
        item = spec['paths'][path]
        for method in sorted(item):
            if method.lower() in HTTP_METHODS and isinstance(item[method], dict):
                yield path, method.lower(), item[method]


def request_schemas(spec, path, method, op):
    """Yield (pointer, container, key) for every request-side schema-bearing node, inlining refs."""
    item = spec['paths'][path]
    params = op.setdefault('parameters', [])
    if 'parameters' in item:  # path-level params: copy into the operation to keep edits local
        names = {(p.get('name'), p.get('in')) for p in params if isinstance(p, dict)}
        params.extend(copy.deepcopy(p) for p in item['parameters'] if (p.get('name'), p.get('in')) not in names)
    for i, p in enumerate(params):
        params[i] = p = resolve(spec, p)
        base = ptr('paths', path, method, 'parameters', i)
        if 'schema' in p:
            yield base + '/schema', p, 'schema'
        else:  # Swagger 2.0 non-body parameter: constraints live on the parameter itself
            yield base, params, i
    if is_oas3(spec) and 'requestBody' in op:
        op['requestBody'] = rb = resolve(spec, op['requestBody'])
        for ct, media in rb.get('content', {}).items():
            if 'schema' in media:
                yield ptr('paths', path, method, 'requestBody', 'content', ct, 'schema'), media, 'schema'


def response_schemas(spec, path, method, op):
    for code, resp in list(op.get('responses', {}).items()):
        op['responses'][code] = resp = resolve(spec, resp)
        if is_oas3(spec):
            for ct, media in resp.get('content', {}).items():
                if 'schema' in media:
                    yield code, ptr('paths', path, method, 'responses', code, 'content', ct, 'schema'), media, 'schema'
        elif 'schema' in resp:
            yield code, ptr('paths', path, method, 'responses', code, 'schema'), resp, 'schema'


def walk_schema(node, pointer):
    """Yield (pointer, schema-dict) for a schema and its nested properties/items."""
    if not isinstance(node, dict):
        return
    yield pointer, node
    for name, sub in node.get('properties', {}).items():
        yield from walk_schema(sub, f'{pointer}/properties/{name}')
    if isinstance(node.get('items'), dict):
        yield from walk_schema(node['items'], f'{pointer}/items')


def set_param_required(path, method, op, value, edits):
    """Flip the parameter-level `required` flag (lives outside the schema in both formats)."""
    for i, p in enumerate(op.get('parameters', [])):
        if p.get('in') in ('query', 'header') and bool(p.get('required')) != value:
            edits.append({'pointer': ptr('paths', path, method, 'parameters', i, 'required'),
                          'before': p.get('required'), 'after': value})
            p['required'] = value


def mutate_loose(spec, path, method, op, edits):
    for pointer, container, key in list(request_schemas(spec, path, method, op)):
        for sp, schema in walk_schema(container[key], pointer):
            for k in LOOSE_KEYS:
                if k in schema:
                    edits.append({'pointer': f'{sp}/{k}', 'before': schema.pop(k), 'after': None})
            if schema.get('required') and isinstance(schema['required'], list):
                edits.append({'pointer': f'{sp}/required', 'before': schema.pop('required'), 'after': None})
    set_param_required(path, method, op, False, edits)


def mutate_strict(spec, path, method, op, edits):
    for pointer, container, key in list(request_schemas(spec, path, method, op)):
        for sp, schema in walk_schema(container[key], pointer):
            t = schema.get('type')
            if t in ('integer', 'number'):
                before = schema.get('maximum')
                schema['maximum'] = 0 if before is None else min(before, 0)
                edits.append({'pointer': f'{sp}/maximum', 'before': before, 'after': schema['maximum']})
            elif t == 'string' and 'enum' not in schema and 'format' not in schema:
                before = schema.get('maxLength')
                schema['maxLength'] = 1
                edits.append({'pointer': f'{sp}/maxLength', 'before': before, 'after': 1})
            if t == 'object' and schema.get('properties'):
                before = schema.get('required')
                schema['required'] = sorted(schema['properties'])
                if before != schema['required']:
                    edits.append({'pointer': f'{sp}/required', 'before': before, 'after': schema['required']})
    set_param_required(path, method, op, True, edits)


def mutate_response(spec, path, method, op, edits):
    for code in [c for c in list(op.get('responses', {})) if str(c).startswith('5')]:
        edits.append({'pointer': ptr('paths', path, method, 'responses', code),
                      'before': op['responses'].pop(code), 'after': None})
    for code, pointer, container, key in list(response_schemas(spec, path, method, op)):
        if not str(code).startswith('2'):
            continue
        for sp, schema in walk_schema(container[key], pointer):
            if schema.get('properties') and schema.get('additionalProperties') is not False:
                edits.append({'pointer': f'{sp}/additionalProperties',
                              'before': schema.get('additionalProperties'), 'after': False})
                schema['additionalProperties'] = False
                before = schema.get('required')
                schema['required'] = sorted(schema['properties'])
                edits.append({'pointer': f'{sp}/required', 'before': before, 'after': schema['required']})


def mutate_method(spec, path, method, op, edits):
    item = spec['paths'][path]
    target = METHOD_SWAP.get(method)
    if not target or target in item:
        return  # would collide with an existing operation; skipped (recorded as no edit)
    item[target] = item.pop(method)
    edits.append({'pointer': ptr('paths', path, method), 'before': method, 'after': target})


MUTATORS = {'REQUEST_LOOSE': mutate_loose, 'REQUEST_STRICT': mutate_strict,
            'RESPONSE_ORACLE': mutate_response, 'METHOD_SEM': mutate_method}


def mutate(spec, fault, severity, seed, exclude=()):
    spec = copy.deepcopy(spec)
    ops = [(p, m) for p, m, _ in operations(spec) if p not in exclude]
    rng = random.Random(f'{seed}:{fault}')
    k = max(1, round(len(ops) * severity / 100)) if ops else 0
    chosen = sorted(rng.sample(ops, k))
    manifest = []
    for path, method in chosen:
        op = spec['paths'][path][method]
        original = copy.deepcopy(op)
        edits = []
        MUTATORS[fault](spec, path, method, op, edits)
        if not edits:  # undo side effects ($ref inlining, copied path-level params) of a no-op
            spec['paths'][path][method] = original
        else:
            l1, l2 = EXPECTED[fault]
            manifest.append({'path': path, 'method': method, 'operationId': op.get('operationId'),
                             'fault': fault, 'expected_L1': l1, 'expected_L2': l2, 'edits': edits})
    return spec, manifest, len(ops)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec')
    ap.add_argument('--fault', choices=FAULTS, required=True)
    ap.add_argument('--severity', type=int, default=30, help='percent of operations to mutate')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--exclude', nargs='*', default=[], help='paths to leave untouched (e.g. auth/login)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    base = load_spec(a.spec)
    spec, manifest, n_ops = mutate(base, a.fault, a.severity, a.seed, set(a.exclude))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f'{Path(a.spec).stem}__{a.fault.lower()}__p{a.severity}__s{a.seed}'
    (out / f'{stem}.json').write_text(json.dumps(spec, indent=2, default=str), encoding='utf-8')
    meta = {'source_spec': a.spec, 'source_sha256': hashlib.sha256(Path(a.spec).read_bytes()).hexdigest(),
            'format': 'openapi3' if is_oas3(base) else 'swagger2', 'fault': a.fault, 'severity': a.severity,
            'seed': a.seed, 'operations_total': n_ops, 'operations_mutated': len(manifest), 'mutations': manifest}
    (out / f'{stem}.manifest.json').write_text(json.dumps(meta, indent=2, default=str), encoding='utf-8')
    print(f'{stem}: {len(manifest)}/{n_ops} operations mutated, '
          f'{sum(len(m["edits"]) for m in manifest)} edits')


if __name__ == '__main__':
    main()
