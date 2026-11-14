"""Check captured exchanges against Swagger 2 / OpenAPI 3 schemas.

Usage: python3 conformance.py SPEC EXCHANGES.jsonl > violations.jsonl
Fingerprints identify constraints and normalized instance locations; occurrences
are counted separately by attribute.py. Incomplete request evidence is explicit.
"""
import copy
import datetime
import json
import re
import sys
import warnings
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import unquote, urlsplit

import jsonschema
sys.path.insert(0, str(Path(__file__).resolve().parent))
import specmut

FORMAT_CHECKER = copy.deepcopy(jsonschema.Draft4Validator.FORMAT_CHECKER)


@FORMAT_CHECKER.checks('date', raises=ValueError)
def _date(value):
    return not isinstance(value, str) or bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) and datetime.date.fromisoformat(value))


@FORMAT_CHECKER.checks('date-time', raises=ValueError)
def _date_time(value):
    if not isinstance(value, str):
        return True
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-](?:[01]\d|2[0-3]):[0-5]\d)', value):
        return False
    # datetime cannot represent RFC3339 leap seconds: check the preceding second.
    normalized = re.sub(r':60(?=[.Zz+-])', ':59', value).upper().replace('Z', '+00:00')
    return bool(datetime.datetime.fromisoformat(normalized))


def is_31(version):
    return isinstance(version, str) and version.startswith('3.1')


def to_json_schema(schema, oas3, strict_additional=False, direction=None):
    """Visit schema positions only, preserving property names and literal JSON data."""
    s = copy.deepcopy(schema)

    def fix(node):
        if not isinstance(node, dict):
            return
        if not is_31(oas3):
            nullable = node.pop('nullable', False) if oas3 else False
            if (nullable or node.get('x-nullable') is True) and 'type' in node:
                t = node['type']
                node['type'] = list(dict.fromkeys(([t] if isinstance(t, str) else t) + ['null']))
        props = node.get('properties', {})
        if direction and isinstance(node.get('required'), list):
            ignored = 'readOnly' if direction == 'request' else 'writeOnly'
            node['required'] = [k for k in node['required']
                                if not isinstance(props.get(k), dict) or not props[k].get(ignored)]
        if strict_additional and isinstance(props, dict) and 'properties' in node and 'additionalProperties' not in node:
            node['additionalProperties'] = False
        if isinstance(node.get('pattern'), str):
            try:
                re.compile(node['pattern'])
            except re.error:
                node['x-unchecked-pattern'] = node.pop('pattern')
        for key in ('properties', 'patternProperties', '$defs', 'definitions', 'dependentSchemas'):
            for sub in node.get(key, {}).values():
                fix(sub)
        for key in ('items', 'additionalItems', 'additionalProperties', 'contains', 'not', 'if', 'then', 'else',
                    'unevaluatedProperties', 'unevaluatedItems', 'propertyNames'):
            sub = node.get(key)
            if isinstance(sub, list):
                for child in sub:
                    fix(child)
            else:
                fix(sub)
        for key in ('allOf', 'anyOf', 'oneOf', 'prefixItems'):
            for sub in node.get(key, []):
                fix(sub)
    fix(s)
    return s


def validator(schema, oas3, strict_additional=False, direction=None, root=None, resolver=None):
    cls = jsonschema.Draft202012Validator if is_31(oas3) else jsonschema.Draft4Validator
    normalized = to_json_schema(schema, oas3, strict_additional, direction)
    options = {'format_checker': FORMAT_CHECKER}
    if resolver is not None:
        options['resolver'] = resolver
    elif root is not None:
        # The resolver is local-only. External references are uncheckable, never fetched.
        context = copy.deepcopy(root)
        def normalize_document(node):
            if isinstance(node, dict):
                for k, v in list(node.items()):
                    if k == 'schema':
                        node[k] = to_json_schema(v, oas3, strict_additional, direction)
                    else:
                        normalize_document(v)
            elif isinstance(node, list):
                for child in node:
                    normalize_document(child)
        normalize_document(context)
        if 'definitions' in context:
            context['definitions'] = {k: to_json_schema(v, oas3, strict_additional, direction)
                                      for k, v in root['definitions'].items()}
        if 'schemas' in context.get('components', {}):
            context['components']['schemas'] = {k: to_json_schema(v, oas3, strict_additional, direction)
                                                for k, v in root['components']['schemas'].items()}
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            class LocalResolver(jsonschema.RefResolver):
                def resolve_remote(self, uri):
                    raise ValueError('external reference is outside the local-only validation scope: ' + uri)
            options['resolver'] = LocalResolver.from_schema(context)
    return cls(normalized, **options)


PARAM_SCHEMA_KEYS = ('type', 'format', 'enum', 'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum',
                     'minLength', 'maxLength', 'pattern', 'items', 'minItems', 'maxItems', 'multipleOf')


def server_base(server):
    url = server.get('url', '')
    for name, variable in server.get('variables', {}).items():
        url = url.replace('{' + name + '}', str(variable.get('default', '{' + name + '}')))
    return urlsplit(url).path.rstrip('/'), authority(url)


def authority(url):
    parsed = urlsplit(url)
    if not parsed.netloc:
        return ''
    return f'{parsed.hostname}:{parsed.port or (443 if parsed.scheme == "https" else 80)}'


def select_media(content, ctype):
    if not content:
        return None, None
    if not ctype:
        key = 'application/json' if 'application/json' in content else next(iter(content))
        return key, content[key].get('schema')
    matches = [k for k in content if media_matches(ctype, k)]
    if not matches:
        return None, None
    key = max(matches, key=lambda k: (k.split(';')[0].strip().lower() == ctype, k != '*/*'))
    return key, content[key].get('schema')


class Spec:
    def __init__(self, spec, strict_additional=False, deploy_origin=None, reject_statuses=(400, 422)):
        self.raw, self.strict = spec, strict_additional
        # Statuses that mean "request rejected as invalid" for VALID_REJECTED. Default: 400/422. A SUT-specific
        # set (e.g. market's deliberate 406 for validation errors) must be justified by code evidence.
        self.reject = tuple(reject_statuses)
        # Exchanges captured from the deployment under test (e.g. http://sut-x:8080) are matched by path
        # only: absolute spec servers such as http://localhost:8080 are dev placeholders for that deployment.
        self.deploy = authority(deploy_origin) if deploy_origin else None
        self.oas3 = specmut.is_oas3(spec)
        self.dialect = spec.get('openapi', False) if self.oas3 else False
        self.base = server_base((spec.get('servers') or [{}])[0])[0] if self.oas3 else spec.get('basePath', '').rstrip('/')
        self._validators = {}
        self._resolvers = {}
        self.routes = []
        for template in sorted(spec.get('paths', {}), key=lambda t: (t.count('{'), -len(t))):
            item = spec['paths'][template]
            for method in specmut.HTTP_METHODS:
                if method not in item:
                    continue
                servers = item[method].get('servers', item.get('servers', spec.get('servers', [{}]))) if self.oas3 else [{'url': self.base}]
                for server in servers:
                    base, origin = server_base(server)
                    names = re.findall(r'\{([^/{}]+)\}', template)
                    parts = re.split(r'\{[^/{}]+\}', template)
                    rx = re.escape(base) + '([^/]+?)'.join(re.escape(p) for p in parts)
                    self.routes.append((re.compile('^' + rx + '/?$'), template, names, method, origin))

    def match(self, path, method=None, origin=None):
        fallback = None
        for rx, template, names, route_method, route_origin in self.routes:
            if fallback and template != fallback[0]:
                break  # A concrete path wins even when its method is undocumented.
            if origin and route_origin and authority(origin) != route_origin \
                    and not (self.deploy and authority(origin) == self.deploy):
                continue
            m = rx.match(path)
            if m:
                result = (template, {n: unquote(v) for n, v in zip(names, m.groups())})
                if method is None or method.lower() == route_method:
                    return result
                fallback = fallback or result
        if fallback and method and method.lower() in self.raw['paths'][fallback[0]]:
            # That method exists, but its effective server did not match.
            return None, {}
        return fallback or (None, {})

    def operation(self, template, method):
        item = self.raw['paths'][template]
        op = item.get(method.lower())
        if op is None:
            return None, []
        resolved = [specmut.resolve(self.raw, p, preserve_schemas=True) for p in item.get('parameters', []) + op.get('parameters', [])]
        params = {(p.get('name'), p.get('in')): p for p in resolved}
        return specmut.resolve(self.raw, op, preserve_schemas=True), list(params.values())

    def response_entry(self, op, status):
        responses = op.get('responses', {})
        return responses.get(str(status)) or responses.get(f'{str(status)[0]}XX') or responses.get('default')

    def response_schema(self, op, status, ctype=''):
        resp = self.response_entry(op, status)
        if resp is None:
            return False, None
        return True, select_media(resp.get('content', {}), ctype)[1] if self.oas3 else resp.get('schema')

    def allowed_media(self, op, status):
        resp = self.response_entry(op, status) or {}
        if self.oas3:
            return list(resp.get('content', {})) or None
        produces = op.get('produces') or self.raw.get('produces')
        return produces if produces and 'schema' in resp else None

    def errors(self, schema, instance, direction):
        key = (json.dumps(schema, sort_keys=True), direction)
        if key not in self._validators:
            self._validators[key] = validator(schema, self.dialect, self.strict if direction == 'response' else False,
                                              direction, self.raw, self._resolvers.get(direction))
            # Reuse the normalized source document; each validator still has its
            # own root schema, while reference targets share direction/policy.
            self._resolvers[direction] = self._validators[key]._ref_resolver
        return self._validators[key].iter_errors(instance)


def coerce(value, schema, values=None, delimiter=',', explode=False):
    if not isinstance(schema, dict):
        return value
    t = schema.get('type')
    if isinstance(t, list):
        t = next((x for x in t if x != 'null'), None)
    if t == 'array':
        raw = (values if values is not None else [value]) if explode else (value.split(delimiter) if isinstance(value, str) else [value])
        return [coerce(x, schema.get('items', {})) for x in raw]
    try:
        if t == 'integer':
            return int(value)
        if t == 'number':
            return float(value)
        if t == 'boolean':
            return {'true': True, 'false': False}[value.lower()]
    except (ValueError, KeyError, AttributeError, TypeError):
        return value
    return value


def error_identity(err):
    """Array indices normalize to '*'; object keys and offending property remain distinct."""
    loc = '/' + '/'.join('*' if isinstance(p, int) else str(p).replace('~', '~0').replace('/', '~1') for p in err.absolute_path)
    properties = ['']
    if err.validator == 'required' and isinstance(err.instance, dict):
        # jsonschema emits one error per missing property; match its own quoted name.
        properties = [str(p) for p in err.validator_value if p not in err.instance and err.message == f'{p!r} is a required property'] or ['']
    elif err.validator == 'additionalProperties' and isinstance(err.instance, dict):
        props, patterns = err.schema.get('properties', {}), err.schema.get('patternProperties', {})
        properties = sorted(str(p) for p in err.instance if p not in props and not any(re.search(rx, p) for rx in patterns)) or ['']
    for prop in properties:
        yield {'keyword': str(err.validator), 'instance_location': loc, 'property': prop}


def schema_problems(spec, schema, value, direction, prefix=''):
    for err in spec.errors(schema, value, direction):
        pointer = prefix + '/' + '/'.join(str(p).replace('~', '~0').replace('/', '~1') for p in err.schema_path)
        for identity in error_identity(err):
            yield pointer, err.message, identity


def parse_body(text, media):
    media = (media or 'application/json').split(';')[0].lower()
    if media == 'application/json' or media.endswith('+json') or media == '*/*':
        return json.loads(text)
    if media.startswith('text/'):
        return text
    raise LookupError('unsupported body encoding: ' + media)


class RequestProblems(list):
    """List compatibility for existing callers, plus explicit evidence completeness."""
    def __init__(self):
        super().__init__()
        self.uncheckable = []


def request_problems(spec, params, op, exchange, path_params):
    problems = RequestProblems()
    req = exchange['request']
    headers = {k.lower(): v for k, v in req.get('headers', {}).items()}
    for p in params:
        loc, name = p.get('in'), p.get('name')
        schema = p.get('schema') if 'schema' in p else {k: p[k] for k in PARAM_SCHEMA_KEYS if k in p}
        if loc == 'body':
            continue
        all_vals = None
        if loc == 'path':
            present, raw = name in path_params, path_params.get(name)
        elif loc == 'query':
            vals = req.get('query', {}).get(name)
            all_vals = vals if isinstance(vals, list) else [vals] if vals is not None else []
            present, raw = bool(all_vals), all_vals[0] if all_vals else None
        elif loc == 'header':
            raw = headers.get(name.lower())
            present = raw is not None
        elif loc == 'cookie':
            if headers.get('cookie') == '<redacted>':
                problems.uncheckable.append('cookie values are redacted')
                continue
            cookies = SimpleCookie()
            cookies.load(headers.get('cookie', ''))
            present = name in cookies
            raw = cookies[name].value if present else None
        else:
            problems.uncheckable.append('unsupported parameter location: ' + str(loc))
            continue
        prefix = '/parameters' + specmut.ptr(loc, name)
        if not present:
            if p.get('required'):
                problems.append((prefix + '/required', f'missing required {loc} parameter {name}',
                                 {'keyword': 'required', 'instance_location': prefix, 'property': name}))
            continue
        if 'content' in p or (isinstance(schema, dict) and (schema.get('type') == 'object' or '$ref' in schema)):
            problems.uncheckable.append('unsupported parameter serialization: ' + str(name))
            continue
        js = to_json_schema(schema, spec.dialect, direction='request')
        delim = {'ssv': ' ', 'tsv': '\t', 'pipes': '|'}.get(p.get('collectionFormat'), ',')
        delim = {'spaceDelimited': ' ', 'pipeDelimited': '|'}.get(p.get('style'), delim)
        explode = (spec.oas3 and loc in ('query', 'cookie') and p.get('style', 'form') == 'form' and p.get('explode', True)) or p.get('collectionFormat') == 'multi'
        value = coerce(raw, js, all_vals, delim, explode)
        try:
            problems.extend(schema_problems(spec, schema, value, 'request', prefix))
        except Exception as exc:
            problems.uncheckable.append('parameter schema: ' + str(exc))
    body_schema, required, media = None, False, None
    ctype = headers.get('content-type', '').split(';')[0].strip().lower()
    if spec.oas3 and 'requestBody' in op:
        rb = op['requestBody']
        required = rb.get('required', False)
        media, body_schema = select_media(rb.get('content', {}), ctype)
        if rb.get('content') and ctype and media is None:
            problems.append(('/requestBody/content', 'undocumented request Content-Type', {'keyword': 'contentType'}))
    else:
        bp = next((p for p in params if p.get('in') == 'body'), {})
        body_schema, required = bp.get('schema'), bp.get('required', False)
        media = ctype or next(iter(op.get('consumes', spec.raw.get('consumes', ['application/json']))), 'application/json')
    capture = req.get('body', {})
    text = capture.get('text', '')
    if capture.get('truncated') or capture.get('decode_error'):
        problems.uncheckable.append('request body capture is incomplete or undecodable')
    elif not text:
        if required:
            problems.append(('/requestBody/required', 'missing required request body', {'keyword': 'required', 'property': 'requestBody'}))
    elif body_schema is not None:
        try:
            body = parse_body(text, ctype or media)
        except ValueError:
            problems.append(('/requestBody/parse', 'request body is not valid JSON', {'keyword': 'parse'}))
        except LookupError as exc:
            problems.uncheckable.append(str(exc))
        else:
            try:
                problems.extend(schema_problems(spec, body_schema, body, 'request', '/requestBody'))
            except Exception as exc:
                problems.uncheckable.append('request body schema: ' + str(exc))
    return problems


def media_matches(ctype, allowed):
    allowed = allowed.split(';')[0].strip().lower()
    if allowed in ('*/*', ctype):
        return True
    a_type, _, a_sub = allowed.partition('/')
    c_type, _, _ = ctype.partition('/')
    return a_type == c_type and a_sub == '*'


def check(spec, exchange):
    req, resp = exchange['request'], exchange['response']
    method, status = req['method'].upper(), int(resp['status'])
    template, path_params = spec.match(req['path'], method, req.get('origin'))

    def v(kind, pointer='', message='', identity=None):
        identity = identity or {}
        parts = [method, template or req['path'], str(status), kind, pointer,
                 identity.get('keyword', ''), identity.get('instance_location', ''), identity.get('property', '')]
        return {'kind': kind, 'method': method, 'template': template or req['path'], 'status': status,
                'pointer': pointer, 'message': message[:300], **identity,
                'fingerprint': json.dumps(parts, ensure_ascii=False, separators=(',', ':'))}

    if template is None:
        return [v('UNDOCUMENTED_OPERATION', message='path not in spec')]
    op, params = spec.operation(template, method)
    if op is None:
        return [v('UNDOCUMENTED_OPERATION', message='method not in spec')]
    out = []
    if status >= 500:
        out.append(v('SERVER_ERROR'))
    headers = {k.lower(): val for k, val in resp.get('headers', {}).items()}
    ctype = headers.get('content-type', '').split(';')[0].strip().lower()
    documented, schema = spec.response_schema(op, status, ctype)
    if not documented:
        out.append(v('UNDOCUMENTED_STATUS'))
    else:
        allowed = spec.allowed_media(op, status)
        if allowed and ctype and not any(media_matches(ctype, a) for a in allowed):
            out.append(v('RESPONSE_CONTENT_TYPE', message=f'{ctype} not in {allowed}'))
    capture = resp.get('body', {})
    text = capture.get('text', '')
    if documented and schema is not None:
        media = ctype or (select_media((spec.response_entry(op, status) or {}).get('content', {}), '')[0] if spec.oas3 else 'application/json')
        if capture.get('truncated') or capture.get('decode_error'):
            out.append(v('RESPONSE_UNCHECKABLE', message='response body capture is incomplete or undecodable'))
        elif not text and not (media or '').startswith('text/'):
            out.append(v('RESPONSE_PARSE', message='documented response body is missing'))
        else:
            try:
                body = parse_body(text, media)
            except ValueError:
                out.append(v('RESPONSE_PARSE', message='body is not valid JSON'))
            except LookupError as exc:
                out.append(v('RESPONSE_UNCHECKABLE', message=str(exc)))
            else:
                try:
                    out.extend(v('RESPONSE_SCHEMA', ptr, msg, identity)
                               for ptr, msg, identity in schema_problems(spec, schema, body, 'response'))
                except Exception as exc:
                    out.append(v('RESPONSE_UNCHECKABLE', message='response schema: ' + str(exc)))
    problems = request_problems(spec, params, op, exchange, path_params)
    if problems.uncheckable:
        out.append(v('REQUEST_UNCHECKABLE', message='; '.join(problems.uncheckable)))
    if problems and 200 <= status < 300:
        out.extend(v('INVALID_ACCEPTED', ptr, msg, identity) for ptr, msg, identity in problems)
    if not problems and not problems.uncheckable and status in spec.reject:
        out.append(v('VALID_REJECTED'))
    return out


def main(spec_path, exchanges_path, deploy_origin=None, reject_statuses=(400, 422)):
    spec = Spec(specmut.load_spec(spec_path), deploy_origin=deploy_origin, reject_statuses=reject_statuses)
    with open(exchanges_path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            for violation in check(spec, json.loads(line)):
                violation['exchange'] = i
                print(json.dumps(violation))


if __name__ == '__main__':
    # Usage: conformance.py SPEC EXCHANGES [--deploy-origin URL] [--reject-statuses 400,422]
    args = sys.argv[1:]
    deploy, reject = None, (400, 422)
    if '--deploy-origin' in args:
        i = args.index('--deploy-origin')
        deploy = args[i + 1]
        del args[i:i + 2]
    if '--reject-statuses' in args:
        i = args.index('--reject-statuses')
        reject = tuple(int(x) for x in args[i + 1].split(','))
        del args[i:i + 2]
    main(args[0], args[1], deploy, reject)
