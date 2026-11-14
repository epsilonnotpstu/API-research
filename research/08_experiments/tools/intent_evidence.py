#!/usr/bin/env python3
"""Read-only, standard-library intent-evidence search (codebook v0.5 section 11).

Usage: intent_evidence.py SOURCE_DIR SPEC --method GET --path /products
                         [--status 418] [--field name] [--json]

This is a lexical search, not a Java compiler or an attribution oracle. All
relationships are reviewable candidates; handler code never counts as independent
evidence. --status supplies the observed response. --field alone supplies no
observed presence/absence: only explicit response serialization annotations allow
a tentative code comparison. JSON and a conservative block-YAML subset are read;
unsupported YAML fails explicitly rather than inventing a contract.
"""
import argparse
import bisect
from http import HTTPStatus
import html
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit


SKIP = {'.git', 'target', 'node_modules', '.venv', 'venv', '__pycache__',
        'build', 'dist', '.gradle', '.idea'}
CODE = {'.java', '.kt', '.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rb', '.cs'}
DOC = {'.md', '.adoc', '.txt', '.html', '.htm', '.rst'}
CATEGORIES = ['HANDLER', 'E-TEST', 'E-DOC', 'E-CONSIST', 'E-HISTORY']
METHODS = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE'}
STATUS = {s.name: s.value for s in HTTPStatus}
STATUS.update({'I_AM_A_TEAPOT': 418, 'PAYLOAD_TOO_LARGE': 413,
               'UNPROCESSABLE_ENTITY': 422, 'MOVED_TEMPORARILY': 302})
CALLS = {'ok': 200, 'created': 201, 'accepted': 202, 'noContent': 204,
         'badRequest': 400, 'notFound': 404, 'serverError': 500}


class SearchDeadline(Exception):
    """Hard CLI deadline; must not be swallowed by cooperative scan recovery."""


def yaml_subset(text):
    """Parse block maps/sequences and JSON flow values; reject YAML magic.

    No tags, anchors, aliases, multiline quoted scalars or implicit timestamps.
    This deliberately small parser never executes constructors or imports YAML.
    """
    rows = []
    for n, raw in enumerate(text.splitlines(), 1):
        if '\t' in raw[:len(raw) - len(raw.lstrip())]:
            raise ValueError(f'YAML tabs at line {n}')
        line = re.sub(r'''(?:"(?:\\.|[^"\\])*"|'[^']*')|(#.*$)''',
                      lambda m: '' if m.group(1) else m.group(), raw).rstrip()
        if line.strip() and line.strip() not in {'---', '...'}:
            rows.append((len(line) - len(line.lstrip()), line.strip(), n))

    def scalar(s):
        if re.search(r'(^|\s)[&*!]|<<:', s):
            raise ValueError('YAML tags/anchors/aliases are unsupported; use JSON')
        if s.startswith('"') or s.startswith(('[', '{')):
            try:
                return json.loads(s)
            except ValueError as exc:
                raise ValueError('YAML flow values must use JSON syntax') from exc
        if s.startswith("'"):
            if not s.endswith("'"):
                raise ValueError('Multiline YAML strings unsupported')
            return s[1:-1].replace("''", "'")
        if s in {'true', 'false', 'null', '~'}:
            return {'true': True, 'false': False, 'null': None, '~': None}[s]
        if re.fullmatch(r'-?\d+', s):
            return int(s)
        return s

    def mapping_pair(s):
        m = re.match(r'''((?:"[^"\n]*"|'[^'\n]*'|[^:]+)):(?:\s+(.*)|$)''', s)
        return (str(scalar(m[1].strip())), m[2] or '') if m else None

    def block(i, indent, indentless=False):
        seq = rows[i][1].startswith('- ')
        out = [] if seq else {}
        while i < len(rows) and rows[i][0] == indent:
            _, s, n = rows[i]
            if s.startswith('- ') != seq:
                if seq and indentless:
                    break
                raise ValueError(f'Mixed YAML container at line {n}')
            s = s[2:] if seq else s
            pair = mapping_pair(s)
            i += 1
            if pair:
                key, val = pair
                if val in {'|', '>', '|-', '>-', '|+', '>+'}:
                    parts = []
                    while i < len(rows) and rows[i][0] > indent:
                        parts.append(rows[i][1])
                        i += 1
                    value = '\n'.join(parts)
                elif val:
                    value = scalar(val)
                elif i < len(rows) and rows[i][0] > indent:
                    value, i = block(i, rows[i][0])
                elif i < len(rows) and rows[i][0] == indent and rows[i][1].startswith('- '):
                    value, i = block(i, indent, indentless=True)
                else:
                    value = {}
                if seq:
                    item = {key: value}
                    if i < len(rows) and rows[i][0] > indent:
                        rest, i = block(i, rows[i][0])
                        if not isinstance(rest, dict) or set(item) & set(rest):
                            raise ValueError('Unsupported YAML sequence mapping')
                        item.update(rest)
                    out.append(item)
                else:
                    if key in out:
                        raise ValueError(f'Duplicate YAML key {key}')
                    out[key] = value
            elif seq:
                out.append(scalar(s))
            else:
                raise ValueError(f'Unsupported YAML at line {n}; use JSON')
        return out, i

    if not rows:
        raise ValueError('Empty spec')
    result, end = block(0, rows[0][0])
    if end != len(rows):
        raise ValueError('Unsupported YAML indentation; use JSON')
    return result


def load_spec(path):
    text = Path(path).read_text(encoding='utf-8')
    try:
        def unique(pairs):
            out = {}
            for key, val in pairs:
                if key in out:
                    raise ValueError(f'Duplicate JSON key {key}')
                out[key] = val
            return out
        result = json.loads(text, object_pairs_hook=unique)
    except json.JSONDecodeError:
        result = yaml_subset(text)
    if not isinstance(result, dict) or not isinstance(result.get('paths'), dict):
        raise ValueError('SPEC must be an OpenAPI/Swagger mapping with paths')
    return result


def normalize(path):
    return '/' + '/'.join(p for p in path.split('/') if p)


def route_equal(a, b):
    return re.sub(r'\{[^}]+\}', '{}', normalize(a)) == re.sub(r'\{[^}]+\}', '{}', normalize(b))


def mask_java(text):
    """Keep offsets/newlines while masking comments and strings."""
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern, lambda m: re.sub(r'[^\n]', ' ', m.group()), text)


def strip_comments(text):
    pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/'
    return re.sub(pattern, lambda m: re.sub(r'[^\n]', ' ', m.group())
                  if m.group().startswith(('//', '/*')) else m.group(), text)


def matching(mask, start, opening='(', closing=')'):
    level = 0
    for i in range(start, len(mask)):
        if mask[i] == opening:
            level += 1
        elif mask[i] == closing:
            level -= 1
            if level == 0:
                return i + 1
    return len(mask)


def annotations(text, mask):
    out = []
    pos = 0
    rx = re.compile(r'@(?:[\w]+\.)*(\w+)\b')
    while (m := rx.search(mask, pos)):
        end = m.end()
        after = re.match(r'\s*\(', mask[end:])
        if after:
            end = matching(mask, end + after.end() - 1)
        out.append((m[1], m.start(), end, text[m.start():end]))
        pos = end
    return out


def java_units(file):
    text, mask = file['text'], file['mask']
    anns = annotations(text, mask)
    constants = dict(re.findall(r'\bString\s+(\w+)\s*=\s*"([^"\n]*)"', text))
    classes = []
    for m in re.finditer(r'\b(?:class|interface|record|enum)\s+(\w+)[^{;]*\{', mask):
        start = m.end() - 1
        classes.append({'name': m[1], 'start': start,
                        'end': matching(mask, start, '{', '}')})
    member_mask = list(mask)
    for _, astart, aend, _ in anns:
        member_mask[astart:aend] = ' ' * (aend - astart)
    member_mask = ''.join(member_mask)

    def paths(aa):
        selected = [a for a in aa if a[0] in {'Path', 'RequestMapping'} or a[0].endswith('Mapping')]
        values = []
        for _, _, _, raw in selected:
            inner = raw[raw.find('(') + 1:raw.rfind(')')]
            param = re.search(r'\b(?:value|path)\s*=\s*(\{[^}]*\}|"[^"]*"|\w+)', inner)
            if param:
                expr = param[1]
            elif '=' not in inner or inner.lstrip().startswith(('"', '{')):
                expr = inner.split(',')[0] if not inner.lstrip().startswith('{') else inner.split('}')[0] + '}'
            else:
                expr = ''
            literals = re.findall(r'"([^"\n]*)"', expr)
            if literals:
                values.extend(literals)
            elif expr.strip() in constants:
                values.append(constants[expr.strip()])
            elif not expr:
                values.append('')
        return values or ['']

    routes = []
    for cls in classes:
        prev = max(member_mask.rfind('}', 0, cls['start']), member_mask.rfind(';', 0, cls['start']))
        cls_anns = [a for a in anns if prev < a[1] < cls['start']]
        cls['paths'] = paths(cls_anns)
    route_anns = [a for a in anns if a[0] in METHODS or a[0] == 'RequestMapping'
                  or a[0] in {m.title() + 'Mapping' for m in METHODS}]
    for route in route_anns:
        owners = [c for c in classes if c['start'] < route[1] < c['end']]
        if not owners:
            continue
        owner = min(owners, key=lambda c: c['end'] - c['start'])
        # An annotation must begin a member at the class's top brace depth.
        between = mask[owner['start'] + 1:route[1]]
        if between.count('{') != between.count('}'):
            continue
        start = max(member_mask.rfind('}', owner['start'], route[1]),
                    member_mask.rfind(';', owner['start'], route[1]), owner['start']) + 1
        # Mask full annotation arguments before finding the method body.
        body = member_mask.find('{', route[2])
        semi = member_mask.find(';', route[2])
        if body < 0 or (0 <= semi < body) or '(' not in member_mask[start:body]:
            continue
        end = matching(mask, body, '{', '}')
        aa = [a for a in anns if start <= a[1] < body]
        methods = set()
        for name, _, _, raw in aa:
            if name in METHODS:
                methods.add(name)
            elif name == 'RequestMapping':
                methods.update(re.findall(r'RequestMethod\.(\w+)', raw))
                if not re.search(r'\bmethod\s*=', raw):
                    methods.update(METHODS)
            elif name.endswith('Mapping') and name[:-7].upper() in METHODS:
                methods.add(name[:-7].upper())
        for prefix in owner['paths']:
            for suffix in paths(aa):
                item = {'start': start, 'body': body, 'end': end,
                        'path': normalize(prefix + '/' + suffix),
                        'methods': sorted(methods), 'class': owner['name'], 'annotations': aa}
                if item not in routes:
                    routes.append(item)
    file['classes'] = classes
    return routes


def codes(text, prose=False):
    found = set()
    for m in re.finditer(r'\b(?:HttpStatus|Status)\.([A-Z][A-Z_]+)\b', text):
        if m[1] in STATUS:
            found.add(STATUS[m[1]])
    for m in re.finditer(r'\bHttpURLConnection\.HTTP_([A-Z_]+)\b', text):
        aliases = {'BAD_METHOD': 405, 'INTERNAL_ERROR': 500, 'MOVED_PERM': 301,
                   'MOVED_TEMP': 302, 'CLIENT_TIMEOUT': 408, 'PRECON_FAILED': 412,
                   'ENTITY_TOO_LARGE': 413, 'REQ_TOO_LONG': 414, 'UNSUPPORTED_TYPE': 415}
        value = STATUS.get(m[1], aliases.get(m[1]))
        if value:
            found.add(value)
    for m in re.finditer(r'(?:\.status(?:Code)?|\bsetStatus|\bassertEquals|@ResponseStatus\s*(?:\(\s*(?:code|value)\s*=)?|\bstatus_code\s*==)\s*\(?\s*([1-5]\d\d)\b', text):
        found.add(int(m[1]))
    for m in re.finditer(r'\b(?:Response|ResponseEntity)\.(\w+)\s*\(', text):
        if m[1] in CALLS:
            found.add(CALLS[m[1]])
    for m in re.finditer(r'\bstatus\s*\(\s*\)\s*\.is(\w+)\s*\(', text):
        name = re.sub(r'(?<!^)([A-Z])', r'_\1', m[1]).upper()
        if name in STATUS:
            found.add(STATUS[name])
    for m in re.finditer(r'\bstatus\s*\(\s*\)\s*\.is\s*\(\s*([1-5]\d\d)', text):
        found.add(int(m[1]))
    if re.search(r'getStatus|status_code|statusCode', text):
        found.update(int(s) for s in re.findall(r'\.isEqualTo\s*\(\s*([1-5]\d\d)\b', text))
    if prose:
        found.update(int(s) for s in re.findall(r'(?<![\w/])([1-5]\d\d)(?![\w/])', text))
    return sorted(found)


def is_test(path):
    parts = {p.lower() for p in path.parts}
    return bool(parts & {'test', 'tests', '__tests__', 'spec', 'specs'}) or bool(
        re.search(r'Test.*\.java$|IT\.java$|(?:^test_|_test\.|\.test\.|\.spec\.)', path.name))


def path_reference(text, path):
    if normalize(path) == '/':
        return bool(re.search(r'''["']/["']''', text))
    if path in text:
        return True
    segments = [s for s in path.split('/') if s and not s.startswith('{')]
    return bool(segments) and all(re.search(r'(?<![\w])' + re.escape(s) + r'(?![\w])', text)
                                  for s in segments)


def string_literals(text):
    return re.findall(r'''["']([^"'\n]*)["']''', text)


def test_path_reference(text, path, spec_paths):
    """Keep full references and add weaker, bounded prefix-stripped literals."""
    if path_reference(text, path):
        return {'match': 'literal' if path in text else 'segments'}
    target = normalize(path).strip('/').split('/')
    for literal in string_literals(text):
        parts = normalize(literal).strip('/').split('/')
        if not literal.strip('/') or len(parts) > len(target):
            continue
        suffix = target[-len(parts):]
        if not all(re.fullmatch(r'\{[^}]+\}', a) or a == b for a, b in zip(suffix, parts)):
            continue
        if len(parts) == 1:
            # A parameter-only suffix cannot identify an operation. A literal
            # must occur in just one distinct spec path, including parent paths.
            if suffix[0].startswith('{'):
                continue
            occurrences = sum(parts[0] in p.strip('/').split('/') for p in set(spec_paths))
            if occurrences != 1:
                continue
        return {'match': 'suffix', 'matched_literal': literal, 'suffix_segments': len(parts)}
    return None


def module_for(path, root, cache):
    """Nearest ancestor build descriptor; inspect paths without running builds."""
    directory = path.parent
    walked = []
    while directory not in cache:
        walked.append(directory)
        build = next((directory / n for n in ('pom.xml', 'build.gradle', 'build.gradle.kts')
                      if (directory / n).is_file() and not (directory / n).is_symlink()), None)
        if build:
            result = (os.path.relpath(directory, root), os.path.relpath(build, root))
            break
        if directory == directory.parent:
            result = (None, None)
            break
        directory = directory.parent
    else:
        result = cache[directory]
    for parent in walked:
        cache[parent] = result
    return result


def rest_base_paths(document):
    bases = [document.get('basePath', '')]
    bases.extend(urlsplit(s.get('url', '')).path for s in document.get('servers', []) if isinstance(s, dict))
    return sorted({normalize(b) for b in bases if isinstance(b, str) and normalize(b) != '/'})


def inflector_routes(files, document, spec_path, method, path, warnings):
    """Resolve explicit controller/operation keys, plus configured tag defaults.

    The configured fallback is a lexical candidate: original EMB Petstore has
    controllerPackage + operationId + tags but no controller extension on GET pet.
    Never infer an Inflector handler from operationId alone in an ordinary spec.
    """
    documents = [(str(spec_path), document)]
    configs = []
    for f in files:
        if not f.get('routing_data'):
            continue
        try:
            parsed = json.loads(f['text']) if f['path'].endswith('.json') else yaml_subset(f['text'])
            if not isinstance(parsed, dict):
                continue
            if Path(f['path']).stem == 'inflector':
                configs.append((f['path'], parsed, f['module']))
            elif isinstance(parsed.get('paths'), dict) and Path(f['path']).resolve() != Path(spec_path).resolve():
                documents.append((f['path'], parsed))
        except (ValueError, TypeError, RecursionError) as exc:
            warnings.append(f"Routing data {f['path']}: {str(exc)[:160]}")
    found = []
    for source, doc in documents:
        for route_path, item in sorted(doc.get('paths', {}).items()):
            if not isinstance(item, dict) or not route_equal(route_path, path):
                continue
            operation = item.get(method.lower(), {})
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get('operationId')
            controller = operation.get('x-swagger-router-controller', item.get('x-swagger-router-controller',
                                        doc.get('x-swagger-router-controller')))
            if not isinstance(operation_id, str) or not re.fullmatch(r'\w+', operation_id):
                continue
            choices = []
            if isinstance(controller, str):
                choices.append((controller, 'x-swagger-router-controller', None, None))
            else:
                for config_path, config, module in configs:
                    package = config.get('controllerPackage')
                    tags = operation.get('tags', [])
                    if isinstance(package, str) and tags and isinstance(tags[0], str) and re.fullmatch(r'\w+', tags[0]):
                        class_name = tags[0][:1].upper() + tags[0][1:] + 'Controller'
                        choices.append((package + '.' + class_name, 'inflector-config-tag-convention', config_path, module))
            for controller_name, basis, config_path, config_module in choices:
                for f in files:
                    if f['test'] or not f['mask'] or (config_path and f['module'] != config_module):
                        continue
                    package = re.search(r'\bpackage\s+([\w.]+)\s*;', f['mask'])
                    for cls in f['classes']:
                        qualified = ((package[1] + '.') if package else '') + cls['name']
                        if controller_name not in {cls['name'], qualified}:
                            continue
                        for match in re.finditer(r'\b' + re.escape(operation_id) + r'\s*\(', f['mask']):
                            if not cls['start'] < match.start() < cls['end']:
                                continue
                            prefix = f['mask'][cls['start'] + 1:match.start()]
                            if prefix.count('{') != prefix.count('}'):
                                continue
                            close = matching(f['mask'], match.end() - 1)
                            tail = re.match(r'\s*(?:throws\s+[\w.,\s]+)?\{', f['mask'][close:])
                            if not tail:
                                continue
                            body = close + tail.end() - 1
                            start = max(f['mask'].rfind(';', cls['start'], match.start()),
                                        f['mask'].rfind('}', cls['start'], match.start()), cls['start']) + 1
                            r = {'start': start, 'body': body,
                                 'end': matching(f['mask'], body, '{', '}'), 'path': normalize(path),
                                 'methods': [method.upper()], 'class': cls['name'],
                                 'annotations': [a for a in annotations(f['text'], f['mask']) if start <= a[1] < body],
                                 'routing': 'swagger_inflector', 'routing_basis': basis,
                                 'routing_source': source, 'operation_id': operation_id,
                                 'controller': qualified, 'inflector_config': config_path}
                            # Several specs can describe the same handler. Keep
                            # one deterministic locator, preferring the input spec.
                            if not any(mf is f and mr['body'] == body for mf, mr in found):
                                found.append((f, r))
    return found


def field_value(text, field):
    if not field or not (re.search(r'\b' + re.escape(field) + r'\b', text) or re.search(
            r'\b(?:get|set|is)' + re.escape(field[:1].upper() + field[1:]) + r'\s*\(', text)):
        return None
    if re.search(r'JsonIgnore\b(?!\s*\(\s*(?:value\s*=\s*)?false)|WRITE_ONLY', text):
        return 'absent'
    if re.search(r'doesNotExist\s*\(|hasNoJsonPath\s*\(|(?:not in|not\.toHaveProperty)', text):
        return 'absent'
    if re.search(r'READ_ONLY|JsonProperty|\.exists\s*\(|hasJsonPath\s*\(|toHaveProperty', text):
        return 'present'
    return None


def spec_context(spec, method, path, field, observed):
    base = spec.get('basePath', '')
    candidates = [(p, v) for p, v in spec['paths'].items()
                  if route_equal(p, path) or (base and route_equal(base + p, path))]
    candidates = [(p, v[method.lower()]) for p, v in candidates
                  if isinstance(v, dict) and isinstance(v.get(method.lower()), dict)]
    if len(candidates) != 1:
        raise ValueError('SPEC operation missing or ambiguous for method/path')
    op_path, op = candidates[0]
    responses = op.get('responses', {})
    statuses = sorted(str(k) for k in responses)

    def deref(value, seen=()):
        if not isinstance(value, dict) or '$ref' not in value:
            return value
        ref = value['$ref']
        if not ref.startswith('#/') or ref in seen:
            return {}
        node = spec
        for part in ref[2:].split('/'):
            node = node.get(part.replace('~1', '/').replace('~0', '~'), {})
        return deref(node, (*seen, ref))

    policies = set()
    def visit(schema, seen):
        schema = deref(schema)
        if not isinstance(schema, dict) or id(schema) in seen:
            return
        seen = seen | {id(schema)}
        props = schema.get('properties', {})
        if field in props:
            prop = deref(props[field])
            if prop.get('writeOnly'):
                policies.add('absent')
            elif field in schema.get('required', []):
                policies.add('present')
            else:
                policies.add('optional')
        for key in ('allOf', 'oneOf', 'anyOf'):
            for sub in schema.get(key, []):
                visit(sub, seen)
        visit(schema.get('items'), seen)

    # Prefer observed response, otherwise successful response schemas only.
    selected = [responses[str(observed)]] if str(observed) in responses else [
        v for k, v in responses.items() if str(k).startswith('2')]
    if field:
        for response in selected:
            response = deref(response)
            visit(response.get('schema'), set())
            for media in response.get('content', {}).values():
                visit(media.get('schema'), set())
    return {'path': op_path, 'statuses': statuses,
            'field_policy': sorted(policies), 'field': field,
            'locator': '#/paths/' + op_path.replace('~', '~0').replace('/', '~1') + '/' + method.lower()}


def search(source, spec_path, method, path, status=None, field=None, budget=25.0):
    start_time = time.monotonic()
    deadline = start_time + budget
    root = Path(source).resolve()
    if not root.is_dir():
        raise ValueError('SOURCE_DIR must be a directory')
    document = load_spec(spec_path)
    spec = spec_context(document, method.upper(), path, field, status)
    files, warnings = [], []
    module_cache = {}
    stats = {'text_files': 0, 'skipped_binary_or_encoding': 0, 'skipped_large': 0,
             'skipped_symlink': 0, 'skipped_dirs': 0, 'complete': True}
    def remaining():
        left = deadline - time.monotonic()
        if left <= 0:
            stats['complete'] = False
            raise TimeoutError('Search time budget exhausted; results are partial')
        return left

    try:
        for directory, dirs, names in os.walk(root, followlinks=False):
            remaining()
            keep = [d for d in dirs if d not in SKIP and not Path(directory, d).is_symlink()]
            stats['skipped_dirs'] += len(dirs) - len(keep)
            dirs[:] = sorted(keep)
            for name in sorted(names):
                remaining()
                full = Path(directory, name)
                relative = full.relative_to(root)
                if full.is_symlink():
                    stats['skipped_symlink'] += 1
                    continue
                suffix = full.suffix.lower()
                routing_data = suffix in {'.yaml', '.yml', '.json'} and (
                    re.match(r'^(?:openapi|swagger)', full.stem, re.I) or full.stem == 'inflector')
                doc = suffix in DOC or name.lower().startswith('readme') or bool(
                    set(relative.parts[:-1]) & {'docs', 'templates'})
                if suffix not in CODE and not doc and not routing_data:
                    continue
                try:
                    if full.stat().st_size > 2_000_000:
                        stats['skipped_large'] += 1
                        continue
                    raw = full.read_bytes()
                    if b'\0' in raw:
                        stats['skipped_binary_or_encoding'] += 1
                        continue
                    text = raw.decode('utf-8-sig')
                except UnicodeError:
                    stats['skipped_binary_or_encoding'] += 1
                    continue
                except OSError as exc:
                    stats['complete'] = False
                    warnings.append(f'{relative}: {exc.strerror}')
                    continue
                module, build_file = module_for(full, root, module_cache)
                file = {'path': relative.as_posix(), 'text': text, 'lines': text.splitlines(),
                        'offsets': [0] + [m.end() for m in re.finditer('\n', text)],
                        'test': is_test(relative), 'doc': doc and suffix not in CODE and not routing_data,
                        'module': module, 'module_build_file': build_file, 'routing_data': bool(routing_data),
                        'mask': mask_java(text) if suffix == '.java' else '', 'classes': []}
                file['clean_lines'] = (strip_comments(text) if suffix in {'.java', '.kt', '.js', '.ts', '.cs'}
                                       else re.sub(r'(?m)^\s*#.*$', '', text)).splitlines()
                file['routes'] = java_units(file) if suffix == '.java' and not file['test'] else []
                files.append(file)
                stats['text_files'] += 1
    except TimeoutError as exc:
        warnings.append(str(exc))

    hits = []
    matched = [(f, r) for f in files for r in f['routes']
               if method.upper() in r['methods'] and route_equal(r['path'], path)]
    for f, r in inflector_routes(files, document, spec_path, method, path, warnings):
        if not any(mf is f and mr['body'] == r['body'] for mf, mr in matched):
            f['routes'].append(r)
            matched.append((f, r))
    handler_modules = {f['module'] for f, _ in matched}
    handler_classes = sorted({r['class'] for _, r in matched})
    bases = rest_base_paths(document)
    code_fields = set()

    def add(category, f, line, strength, **extra):
        snippet = f['lines'][line - 1].strip() if 0 < line <= len(f['lines']) else ''
        hit = {'category': category, 'location': f"{f['path']}:{line}",
               'file': f['path'], 'line': line, 'snippet': snippet[:160],
               'module': f['module'], 'module_build_file': f['module_build_file'],
               'strength': '⚠️ ' + strength, **extra}
        if hit not in hits:
            hits.append(hit)

    def lineno(f, offset):
        return bisect.bisect_right(f['offsets'], offset)

    # 1. Routing and explicit behavior are context, never independent evidence.
    for f, r in matched:
        line = lineno(f, r['body'])
        routing = {k: r[k] for k in ('routing', 'routing_basis', 'routing_source', 'operation_id', 'controller', 'inflector_config') if k in r}
        add('HANDLER', f, line, 'context only; lexical method/path match' + (
            '; configured tag/controller convention requires review' if r.get('routing_basis') == 'inflector-config-tag-convention' else ''),
            route=r['path'], methods=r['methods'], independent=False, **routing)
        first, last = lineno(f, r['start']), lineno(f, r['end'] - 1)
        for n in range(first, last + 1):
            raw = f['clean_lines'][n - 1]
            # Exclude documentation annotations/comments from code behavior.
            offset = f['offsets'][n - 1]
            in_doc = any(a <= offset < b for name, a, b, _ in r['annotations']
                         if name in {'ApiResponse', 'ApiResponses', 'Operation'})
            values = codes(raw) if not in_doc and f['mask'][offset:offset + len(raw)].strip() else []
            if values:
                add('HANDLER', f, n, 'context only; explicit status expression, not runtime proof',
                    statuses=values, independent=False)
    # Field annotations are restricted to selected handler/response DTO references.
    referenced = ' '.join(f['text'][r['start']:r['end']] for f, r in matched)
    for f in files:
        if not field or f['test'] or not f['mask']:
            continue
        relevant = any(f is mf for mf, _ in matched) or any(
            re.search(r'\b' + re.escape(c['name']) + r'\b', referenced) for c in f['classes'])
        if not relevant:
            continue
        for name, a, b, _ in annotations(f['text'], f['mask']):
            if name not in {'JsonProperty', 'JsonIgnore', 'XmlElement'}:
                continue
            end = min((x for x in [f['mask'].find(';', b), f['mask'].find('{', b)] if x >= 0), default=b)
            window = f['text'][a:end]
            value = field_value(window, field)
            xml_field = name == 'XmlElement' and (re.search(r'''\bname\s*=\s*["']''' + re.escape(field) + r'''["']''', window)
                        or re.search(r'\b(?:get|set|is)' + re.escape(field[:1].upper() + field[1:]) + r'\s*\(', window))
            if value or xml_field:
                if value:
                    code_fields.add(value)
                add('HANDLER', f, lineno(f, a), 'context only; response DTO link and serialization are lexical inferences' + (
                    '; XML annotation does not establish JSON presence' if xml_field else ''),
                    field=field, field_behavior=value, independent=False)

    def comparison(values, behavior=None):
        directions = set()
        code_agreement, spec_agreement = [], []
        for v in values:
            agrees_code = None if status is None else v == status
            agrees_spec = str(v) in spec['statuses'] or f'{v // 100}XX' in spec['statuses']
            if not agrees_spec and 'default' in spec['statuses']:
                agrees_spec = None
            code_agreement.append('unknown' if agrees_code is None else 'agrees' if agrees_code else 'contradicts')
            spec_agreement.append('unknown' if agrees_spec is None else 'agrees' if agrees_spec else 'contradicts')
            if agrees_code:
                directions.add('supports_code')
            elif agrees_code is False and agrees_spec:
                directions.add('supports_spec')
        if behavior:
            cb = next(iter(code_fields)) if len(code_fields) == 1 else None
            sb = spec['field_policy'][0] if len(spec['field_policy']) == 1 else None
            code_agreement.append('unknown' if cb is None else 'agrees' if cb == behavior else 'contradicts')
            spec_agreement.append('unknown' if sb not in {'present', 'absent'} else 'agrees' if sb == behavior else 'contradicts')
            if cb == behavior:
                directions.add('supports_code')
            elif cb and sb == behavior:
                directions.add('supports_spec')
        return {'code_agreement': sorted(set(code_agreement)) or ['unknown'],
                'spec_agreement': sorted(set(spec_agreement)) or ['unknown'],
                'support': sorted(directions)}

    # 2. Require the path AND assertion/field in the same local window.
    for f in files:
        if not f['test']:
            continue
        for i, raw in enumerate(f['clean_lines']):
            assertion = bool(re.search(r'assert|expect|statusCode|status\s*\(\s*\)|HttpStatus\.', raw, re.I))
            values = codes(raw) if assertion else []
            mentions = bool(field and re.search(r'\b' + re.escape(field) + r'\b', raw))
            if not values and not mentions:
                continue
            window = '\n'.join(f['clean_lines'][max(0, i - 10):i + 11])
            route_match = test_path_reference(window, path, document['paths'])
            if not route_match:
                continue
            behavior = field_value(raw, field) if assertion else None
            same_module = f['module'] in handler_modules if matched else True
            linked_class = next((c for c in handler_classes if re.search(r'\b' + re.escape(c) + r'\b', '\n'.join(f['clean_lines']))), None)
            linked_base = next((base for base in bases if any(normalize(lit) == base or normalize(lit).startswith(base + '/')
                               for lit in string_literals('\n'.join(f['clean_lines'])))), None)
            independent = same_module or bool(linked_class or linked_base)
            scope = 'handler_module' if same_module and matched else 'unknown' if not matched else 'other_module_linked' if independent else 'other_module'
            note = 'candidate independent test; path within ±10 lines; verify scenario and assertion'
            if route_match['match'] == 'suffix':
                note += '; weaker suffix match; helper-added prefix is not verified'
            if not independent:
                note = 'other_module context only; no handler-class or REST-base-path reference; ' + note
            relation = comparison(values, behavior)
            if not independent:
                relation['support'] = []
            add('E-TEST', f, i + 1, note,
                asserted_values=values, field=field if mentions else None, field_behavior=behavior,
                independent=independent, counts_toward_verdict=independent, module_scope=scope,
                module_link_reason='handler_class_reference' if linked_class else 'rest_base_path_reference' if linked_base else None,
                **route_match, **relation)

    # 3. Non-code docs, handler Javadoc and OpenAPI documentation annotations.
    doc_ranges = []
    for f in files:
        if f['doc'] and Path(root / f['path']).resolve() != Path(spec_path).resolve():
            doc_ranges.append((f, 0, len(f['text']), False))
    for f, r in matched:
        prefix = f['text'][r['start']:r['body']]
        for doc in re.finditer(r'/\*\*[\s\S]*?\*/', prefix):
            doc_ranges.append((f, r['start'] + doc.start(), r['start'] + doc.end(), True))
        for name, a, b, _ in r['annotations']:
            if name in {'ApiResponse', 'ApiResponses', 'Operation'}:
                doc_ranges.append((f, a, b, True))
    for f, begin, end, linked in doc_ranges:
        first, last = lineno(f, begin), lineno(f, max(begin, end - 1))
        anchors = [i for i in range(first - 1, last) if linked or path_reference(f['lines'][i], path)
                   or (field and re.search(r'\b' + re.escape(field) + r'\b', f['lines'][i]))]
        candidates = set()
        for anchor in anchors:
            candidates.update(range(max(first - 1, anchor - 10), min(last, anchor + 11)))
        for i in sorted(candidates):
            raw = f['lines'][i]
            visible = html.unescape(re.sub(r'<[^>]+>', ' ', raw)) if f['doc'] else raw
            # HTML dimensions and JSON example prices/ids are not HTTP statuses.
            visible = re.sub(r'"(?!status(?:Code)?"|responseCode")\w+"\s*:\s*[1-5]\d\d\b', '', visible)
            values = codes(visible, prose=True)
            mentions = bool(field and re.search(r'\b' + re.escape(field) + r'\b', raw))
            if not values and not mentions and i not in anchors:
                continue
            # Documentation field mentions are not presence assertions.
            add('E-DOC', f, i + 1, 'candidate independent documentation; ±10-line proximity; verify scenario',
                statuses=values, field=field if mentions else None,
                independent=True, **comparison(values))

    # 4. Count distinct classes, excluding tests and the input specification.
    sites = {}
    for f in files:
        if f['test'] or not f['mask']:
            continue
        for cls in f['classes']:
            for n in range(lineno(f, cls['start']), lineno(f, cls['end'] - 1) + 1):
                offset = f['offsets'][n - 1]
                if not (cls['start'] <= offset + len(f['lines'][n - 1]) and offset < cls['end']):
                    continue
                # Keep enum/response expressions, never bare unrelated numbers.
                raw = f['clean_lines'][n - 1]
                owners = [c for c in f['classes'] if c['start'] <= offset + len(raw) and offset < c['end']]
                if owners and cls is not min(owners, key=lambda c: c['end'] - c['start']):
                    continue
                if not f['mask'][offset:offset + len(raw)].strip():
                    continue
                handler = any(r['class'] == cls['name'] and r['start'] <= offset < r['end'] for r in f['routes'])
                mapper = bool(re.search(r'Exception|ErrorHandler|Mapper', cls['name']) or
                              re.search(r'\b(?:ExceptionMapper|@ExceptionHandler)\b', f['text'][cls['start']:cls['end']]))
                if status in codes(raw) and (handler or mapper):
                    sites.setdefault(('status', str(status)), {})[(f['path'], cls['name'])] = (f, n)
        if field:
            for name, a, b, raw in annotations(f['text'], f['mask']):
                if name not in {'JsonIgnore', 'JsonProperty'}:
                    continue
                end = min((x for x in [f['mask'].find(';', b), f['mask'].find('{', b)] if x >= 0), default=b)
                behavior = field_value(f['text'][a:end], field)
                owners = [c for c in f['classes'] if c['start'] < a < c['end']]
                if behavior and owners:
                    cls = min(owners, key=lambda c: c['end'] - c['start'])
                    pattern = 'WRITE_ONLY' if 'WRITE_ONLY' in raw else 'READ_ONLY' if 'READ_ONLY' in raw else name
                    sites.setdefault(('field', pattern, behavior), {})[(f['path'], cls['name'])] = (f, lineno(f, a))
    for key, group in sorted(sites.items()):
        if len(group) < 2:
            continue
        values = [status] if key[0] == 'status' else []
        behavior = key[2] if key[0] == 'field' else None
        for (filename, cls), (f, n) in sorted(group.items()):
            add('E-CONSIST', f, n, 'candidate independent class sites; analogy of situations requires review',
                independent=True, independent_sites=len(group), site_class=cls,
                pattern=list(key), statuses=values, field_behavior=behavior,
                **comparison(values, behavior))

    # 5. Git is read-only, local, timeout bounded, with external diff disabled.
    history = {'availability': 'unavailable', 'reason': 'not inside a git work tree'}
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0',
               GIT_PAGER='cat', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    def git(args):
        remaining()
        return subprocess.run(['git', '--no-pager', '-C', str(root), *args],
                              capture_output=True, text=True, encoding='utf-8', errors='replace',
                              timeout=max(0.01, min(3, remaining())), env=env, check=False)
    try:
        probe = git(['rev-parse', '--is-inside-work-tree'])
        if probe.returncode == 0 and probe.stdout.strip() == 'true':
            history = {'availability': 'available', 'reason': 'local git history searched', 'queries': []}
            literals = [str(status)] if status is not None else []
            if field:
                literals.append(field)
            if not literals:
                literals.append(path)
            for filename in sorted({f['path'] for f, _ in matched}):
                f = next(f for f, _ in matched if f['path'] == filename)
                r = next(r for mf, r in matched if mf is f)
                for literal in literals:
                    log = git(['--literal-pathspecs', 'log', '--no-ext-diff', '--no-textconv',
                               '--format=%h %s', '-S' + literal, '--oneline', '--', filename])
                    history['queries'].append({'file': filename, 'literal': literal,
                                               'returncode': log.returncode})
                    if log.returncode:
                        history['availability'] = 'unavailable'
                        history['reason'] = 'git log failed'
                    for commit in log.stdout.splitlines():
                        add('E-HISTORY', f, lineno(f, r['body']),
                            'candidate commit; pickaxe occurrence does not prove intent; inspect commit',
                            independent=True, commit=commit[:160], literal=literal, support=[])
            if not matched:
                history['reason'] = 'git available; no matched handler file to search'
        elif probe.returncode and 'not a git repository' not in probe.stderr:
            history['reason'] = probe.stderr.strip()[:200] or 'git probe failed'
    except (OSError, subprocess.TimeoutExpired, TimeoutError) as exc:
        history = {'availability': 'unavailable', 'reason': str(exc)[:200]}
    hits.sort(key=lambda h: (CATEGORIES.index(h['category']), h['file'], h['line'],
                             json.dumps(h, sort_keys=True)))
    support = {s for h in hits if h.get('independent') for s in h.get('support', [])}
    verdict = 'conflicting' if len(support) > 1 else next(iter(support), 'none_found')
    if not matched:
        warnings.append('No Java handler located; routing constants/imports/inheritance may require manual inspection')
    return {'operation': {'method': method.upper(), 'path': path}, 'observed_status': status,
            'field': field, 'spec': {'file': str(spec_path), **spec},
            'code_field_behavior': sorted(code_fields), 'independent_evidence': verdict,
            'evidence_types_found': [c for c in CATEGORIES[1:] if any(h['category'] == c and h.get('independent') for h in hits)],
            'hits': hits, 'history': history, 'scan': stats, 'warnings': warnings,
            'limitations': ['Lexical candidate search; verify branch/scenario and DTO linkage before attribution.',
                            'Input specification is comparison context, never independent documentation.',
                            'Field mentions alone and git pickaxe matches do not establish intent.',
                            'No runtime field presence is supplied by --field; annotation behavior is tentative.',
                            'Files over 2 MB, symlinks, binaries, build/vendor directories are skipped.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source_dir')
    parser.add_argument('spec')
    parser.add_argument('--method', required=True, type=str.upper, choices=sorted(METHODS))
    parser.add_argument('--path', required=True)
    parser.add_argument('--status', type=int, choices=range(100, 600), metavar='100..599')
    parser.add_argument('--field')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    # The CLI has a hard wall-clock ceiling as well as cooperative scan/git
    # deadlines. This also bounds lexical parsing on unusually large source trees.
    old_handler = signal.getsignal(signal.SIGALRM) if hasattr(signal, 'SIGALRM') else None
    old_timer = None
    def timeout(signum, frame):
        raise SearchDeadline('27-second CLI deadline exceeded; search incomplete')
    try:
        if hasattr(signal, 'setitimer'):
            signal.signal(signal.SIGALRM, timeout)
            old_timer = signal.setitimer(signal.ITIMER_REAL, 27)
        result = search(args.source_dir, args.spec, args.method, args.path, args.status, args.field)
    except (OSError, ValueError, TypeError, RecursionError, SearchDeadline) as exc:
        parser.exit(2, f'intent_evidence: {exc}\n')
    finally:
        if old_timer is not None:
            signal.setitimer(signal.ITIMER_REAL, *old_timer)
            signal.signal(signal.SIGALRM, old_handler)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print('independent_evidence: ' + result['independent_evidence'])
        print('§11.1 evidence types: ' + (', '.join(result['evidence_types_found']) or 'none'))
        for h in result['hits']:
            print(f"{h['category']} {h['location']} | {h['snippet']} | {h['strength']}")
            detail = {k: v for k, v in h.items() if k not in {'category', 'location', 'file', 'line', 'snippet', 'strength'}}
            print('  ' + json.dumps(detail, ensure_ascii=False, sort_keys=True))
        print('E-HISTORY: ' + json.dumps(result['history'], ensure_ascii=False, sort_keys=True))
        for warning in result['warnings']:
            print('warning: ' + warning)
    return 0 if result['scan']['complete'] else 1


if __name__ == '__main__':
    sys.exit(main())
