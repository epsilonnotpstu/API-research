"""conformance — check logged HTTP exchanges against an OpenAPI/Swagger spec.

Input: a spec (Swagger 2.0 or OpenAPI 3.x) and exchanges in the JSONL format
written by mitm_fulllog.py. Output: one violation record per finding, each with
a stable fingerprint (method, path template, status, kind, schema pointer) so
that violation sets from different runs can be diffed (attribute.py).

Violation kinds (cf. P001 oracles and R1_triage_codebook.md):
  UNDOCUMENTED_OPERATION  path/method not in the spec
  RESPONSE_CONTENT_TYPE   Content-Type not among the documented media types
  RESPONSE_PARSE          a JSON schema is documented but the body is not JSON
  SERVER_ERROR            5xx response                      (P001 F_5XX*)
  UNDOCUMENTED_STATUS     status not listed and no `default`
  RESPONSE_SCHEMA         body violates the documented schema (P001 F_OAS)
  INVALID_ACCEPTED        request violates the spec but got 2xx (P001 F_2XXP)
  VALID_REJECTED          request conforms but got 400/422    (P001 F_400)

Usage: python3 conformance.py SPEC EXCHANGES.jsonl > violations.jsonl
"""
import copy
import datetime
import json
import re
import sys

import jsonschema

import specmut

FORMAT_CHECKER = copy.deepcopy(jsonschema.Draft4Validator.FORMAT_CHECKER)


@FORMAT_CHECKER.checks('date', raises=ValueError)
def _date(value):
    return not isinstance(value, str) or bool(datetime.date.fromisoformat(value))


@FORMAT_CHECKER.checks('date-time', raises=ValueError)
def _date_time(value):
    return not isinstance(value, str) or bool(datetime.datetime.fromisoformat(value.replace('Z', '+00:00')))


def validator(schema, oas3, strict_additional=False):
    return jsonschema.Draft4Validator(to_json_schema(schema, oas3, strict_additional), format_checker=FORMAT_CHECKER)


PARAM_SCHEMA_KEYS = ('type', 'format', 'enum', 'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum',
                     'minLength', 'maxLength', 'pattern', 'items', 'minItems', 'maxItems', 'multipleOf')


def to_json_schema(schema, oas3, strict_additional=False):
    """Normalise an (already $ref-inlined) OpenAPI schema for jsonschema validation.

    strict_additional=True treats every object schema that lists `properties` but says
    nothing about `additionalProperties` as closed (a stricter reading than OpenAPI's default).
    """
    s = copy.deepcopy(schema)

    def fix(node):
        if isinstance(node, dict):
            if oas3 and node.pop('nullable', False) and 'type' in node:
                node['type'] = [node['type'], 'null'] if isinstance(node['type'], str) else node['type'] + ['null']
            if node.get('x-nullable') is True and 'type' in node:  # Swagger 2.0 vendor extension
                node['type'] = [node['type'], 'null']
            for k in ('discriminator', 'xml', 'example', 'externalDocs', 'readOnly', 'writeOnly'):
                node.pop(k, None)
            if strict_additional and isinstance(node.get('properties'), dict) and 'additionalProperties' not in node:
                node['additionalProperties'] = False
            if isinstance(node.get('pattern'), str):
                try:
                    re.compile(node['pattern'])
                except re.error:  # e.g. Java \p{L}; not checkable with Python re -> skip, keep a trace
                    node['x-unchecked-pattern'] = node.pop('pattern')
            for v in node.values():
                fix(v)
        elif isinstance(node, list):
            for v in node:
                fix(v)
    fix(s)
    return s


class Spec:
    def __init__(self, spec, strict_additional=False):
        self.raw = spec
        self.strict = strict_additional
        self.oas3 = specmut.is_oas3(spec)
        base = spec.get('basePath', '') if not self.oas3 else ''
        if self.oas3 and spec.get('servers'):
            m = re.match(r'^(?:[a-z]+://[^/]+)?(/.*)?$', spec['servers'][0].get('url', ''))
            base = (m.group(1) or '') if m else ''
        self.base = base.rstrip('/')
        self.routes = []  # (regex, template, path_item); literal segments first
        for template in sorted(spec.get('paths', {}), key=lambda t: (t.count('{'), -len(t))):
            rx = re.escape(self.base + template)
            rx = re.sub(r'\\\{[^/]+?\\\}', '[^/]+', rx)
            names = re.findall(r'\{([^/]+?)\}', template)
            self.routes.append((re.compile('^' + rx + '/?$'), template, names))

    def match(self, path):
        for rx, template, names in self.routes:
            m = rx.match(path)
            if m:
                values = re.findall(r'[^/]+', path[len(self.base):])
                segs = template.strip('/').split('/')
                params = {s[1:-1]: v for s, v in zip(segs, values) if s.startswith('{')}
                return template, params
        return None, {}

    def operation(self, template, method):
        item = self.raw['paths'][template]
        op = item.get(method.lower())
        if op is None:
            return None, []
        resolved = [specmut.resolve(self.raw, p) for p in item.get('parameters', []) + op.get('parameters', [])]
        params = {(p.get('name'), p.get('in')): p for p in resolved}  # operation-level overrides path-level
        return specmut.resolve(self.raw, op), list(params.values())

    def response_entry(self, op, status):
        responses = op.get('responses', {})
        return responses.get(str(status)) or responses.get(f'{str(status)[0]}XX') or responses.get('default')

    def response_schema(self, op, status):
        resp = self.response_entry(op, status)
        if resp is None:
            return False, None
        if self.oas3:
            content = resp.get('content') or {}
            media = content.get('application/json') or next(iter(content.values()), {})
            return True, media.get('schema')
        return True, resp.get('schema')

    def allowed_media(self, op, status):
        """Documented response media types, or None when the spec does not constrain them."""
        resp = self.response_entry(op, status) or {}
        if self.oas3:
            return list(resp.get('content', {})) or None
        produces = op.get('produces') or self.raw.get('produces')
        return produces if produces and resp.get('schema') else None


def coerce(value, schema, values=None, delimiter=','):
    """Path/query parameters arrive as strings; coerce to the declared type.

    Arrays: repeated keys (OAS3 form/explode) or one delimited value (Swagger 2.0 csv,
    OAS3 explode=false) are split and each item is coerced against `items`.
    """
    t = schema.get('type')
    if t == 'array':
        raw = values if values and len(values) > 1 else (value.split(delimiter) if isinstance(value, str) else [value])
        return [coerce(x, schema.get('items', {})) for x in raw]
    try:
        if t == 'integer':
            return int(value)
        if t == 'number':
            return float(value)
        if t == 'boolean':
            return {'true': True, 'false': False}[value.lower()]
    except (ValueError, KeyError, AttributeError):
        return value
    return value


def request_problems(spec, params, op, exchange, path_params):
    """Return a list of (pointer, message) for spec violations in the request itself."""
    problems = []
    req = exchange['request']
    for p in params:
        loc, name = p.get('in'), p.get('name')
        schema = p.get('schema') if 'schema' in p else {k: p[k] for k in PARAM_SCHEMA_KEYS if k in p}
        if loc == 'body' or not schema:
            continue
        if loc == 'path':
            present, raw = name in path_params, path_params.get(name)
        elif loc == 'query':
            vals = req.get('query', {}).get(name)
            present, raw = bool(vals), (vals[0] if vals else None)
            all_vals = vals or []
        elif loc == 'header':
            raw = req.get('headers', {}).get(name.lower())
            present = raw is not None
        else:
            continue
        if not present:
            if p.get('required'):
                problems.append((f'/parameters/{loc}/{name}/required', f'missing required {loc} parameter {name}'))
            continue
        js = to_json_schema(schema, spec.oas3)
        delim = {'ssv': ' ', 'tsv': '\t', 'pipes': '|'}.get(p.get('collectionFormat'), ',')
        if p.get('style') == 'spaceDelimited':
            delim = ' '
        elif p.get('style') == 'pipeDelimited':
            delim = '|'
        value = coerce(raw, js, all_vals if loc == 'query' else None, delim)
        for err in validator(schema, spec.oas3).iter_errors(value):
            problems.append((f'/parameters/{loc}/{name}/' + '/'.join(map(str, err.schema_path)), err.message))
    body_schema = None
    if spec.oas3 and 'requestBody' in op:
        content = op['requestBody'].get('content', {})
        body_schema = (content.get('application/json') or next(iter(content.values()), {})).get('schema')
    else:
        body_schema = next((p.get('schema') for p in params if p.get('in') == 'body'), None)
    text = req.get('body', {}).get('text', '')
    if body_schema and text:
        try:
            body = json.loads(text)
        except ValueError:
            body = None
        if body is not None:
            for err in validator(body_schema, spec.oas3).iter_errors(body):
                problems.append(('/requestBody/' + '/'.join(map(str, err.schema_path)), err.message))
    return problems


def media_matches(ctype, allowed):
    allowed = allowed.split(';')[0].strip().lower()
    if allowed in ('*/*', ctype):
        return True
    a_type, _, a_sub = allowed.partition('/')
    c_type, _, c_sub = ctype.partition('/')
    return a_type == c_type and a_sub == '*'


def check(spec, exchange):
    req, resp = exchange['request'], exchange['response']
    method, status = req['method'].upper(), int(resp['status'])
    template, path_params = spec.match(req['path'])

    def v(kind, pointer='', message=''):
        return {'kind': kind, 'method': method, 'template': template or req['path'], 'status': status,
                'pointer': pointer, 'message': message[:300],
                'fingerprint': '|'.join([method, template or req['path'], str(status), kind, pointer])}

    if template is None:
        return [v('UNDOCUMENTED_OPERATION', message='path not in spec')]
    op, params = spec.operation(template, method)
    if op is None:
        return [v('UNDOCUMENTED_OPERATION', message='method not in spec')]
    out = []
    if status >= 500:
        out.append(v('SERVER_ERROR'))
    documented, schema = spec.response_schema(op, status)
    if not documented:
        out.append(v('UNDOCUMENTED_STATUS'))
    else:
        allowed = spec.allowed_media(op, status)
        ctype = (resp.get('headers', {}).get('content-type') or '').split(';')[0].strip().lower()
        if allowed and ctype and not any(media_matches(ctype, a) for a in allowed):
            out.append(v('RESPONSE_CONTENT_TYPE', '', f'{ctype} not in {allowed}'))
    if documented and schema and resp.get('body', {}).get('text') and not resp['body'].get('truncated'):
        try:
            body = json.loads(resp['body']['text'])
        except ValueError:
            body = None
            out.append(v('RESPONSE_PARSE', '', 'body is not valid JSON'))
        if body is not None:
            for err in validator(schema, spec.oas3, spec.strict).iter_errors(body):
                out.append(v('RESPONSE_SCHEMA', '/' + '/'.join(map(str, err.schema_path)), err.message))
    problems = request_problems(spec, params, op, exchange, path_params)
    if problems and 200 <= status < 300:
        out.extend(v('INVALID_ACCEPTED', ptr_, msg) for ptr_, msg in problems)
    if not problems and status in (400, 422):
        out.append(v('VALID_REJECTED'))
    return out


def main(spec_path, exchanges_path):
    spec = Spec(specmut.load_spec(spec_path))
    with open(exchanges_path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            for violation in check(spec, json.loads(line)):
                violation['exchange'] = i
                print(json.dumps(violation))


if __name__ == '__main__':
    main(*sys.argv[1:3])
