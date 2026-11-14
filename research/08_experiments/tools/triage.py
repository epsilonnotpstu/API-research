"""Evidence-based, offline triage of P001 conformance failure representatives.

Rules refer to 08_experiments/R1_triage_codebook.md v0.3 (§§2–4, 8–9).
No network, subprocess, or installation is used. Existing local
conformance/specmut helpers are imported lazily; missing dependencies cause
abstention for spec-dependent rules. Suggestions are hypotheses, not gold labels.

Usage: /usr/bin/python3 -I -B triage.py SHEET.csv P001_DIR OUT.csv --messages MESSAGES.csv
Library: classify_messages(...), aggregate_labels(...), classify(...), score_label(...).
"""
import argparse
import csv
import datetime as dt
import hashlib
import importlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# Imports of existing helpers must not rewrite their bytecode caches.
sys.dont_write_bytecode = True


CODEBOOK = '08_experiments/R1_triage_codebook.md'
MISSING = object()


@dataclass
class Finding:
    label: str
    locus: str
    confidence: int
    rule: str
    codes: tuple
    refs: tuple
    note: str
    doc_gap: bool = False


def finding(locus, confidence, rule, codes, refs, note, label='SPEC'):
    return Finding(label, locus, confidence, rule, tuple(codes), tuple(refs), note)


def truth(value):
    return str(value).strip().lower() in ('true', '1', 'yes')


def read_csv(path):
    # Some response bodies exceed the stdlib CSV default (131072 bytes).
    csv.field_size_limit(100_000_000)
    with Path(path).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def reject_json_constant(value):
    raise ValueError('Non-JSON numeric constant: ' + value)


def json_body(row):
    try:
        return json.loads(row.get('responseBody', ''), parse_constant=reject_json_constant)
    except (ValueError, TypeError):
        return MISSING


def source(row):
    return row.get('_source', 'input:row=' + str(row.get('testCaseId', '?')))


def values_at(body, path):
    """Read exact JSON pointer paths; [item] and numeric indices denote arrays.

    Codebook §3 E-CONSIST: never merge unrelated fields by leaf name. Missing
    parents and empty arrays are not observations of null or absent properties.
    """
    nodes = [body]
    for part in path.strip('/').split('/') if path.strip('/') else []:
        part = part.replace('~1', '/').replace('~0', '~')
        result = []
        for node in nodes:
            if isinstance(node, list) and (part == '[item]' or part.isdigit()):
                # The failure's array index identifies a field, not one object.
                result.extend(node)
            elif isinstance(node, dict) and part in node:
                result.append(node[part])
        nodes = result
    return nodes


def messages(reason):
    """Return every (path, message) occurrence from the full raw failReason.

    §9.1: msg_idx is one-based source order; repeated messages retain their own
    rows. They do not count as independent responses for consistency evidence.
    """
    reason = re.sub(r'^OAS disconformity:\s*', '', reason)
    result = []
    for part in reason.split(' --- '):
        match = re.match(r"\[Path '([^']*)'\]\s*(.*)", part, re.S)
        pair = (match.group(1), match.group(2)) if match else ('', part.strip())
        if pair[1]:
            result.append(pair)
    return result


def strict_only(row, ref):
    """§9.2 supersedes §8.1; use only for an undeclared-property message."""
    if truth(row.get('strict_only')):
        return finding('T-ORACLE-STRICT', 2, 'STRICT_ONLY', ['E-AUX'], [ref],
                       'Strict validator only; default OpenAPI semantics allow response.', 'TEST')


def broken_pattern(message, ref):
    """§8.4: prove double escaping by original failure + repaired match.

    A regex need not be globally unsatisfiable: the defect is in its encoding
    for the observed value. Java Unicode-property syntax is a dialect mismatch,
    not proof that the regular language is empty. Unknown regex errors abstain.
    """
    match = re.search(r'ECMA 262 regex "([^"]*)" does not match input string "([^"]*)"', message)
    if not match:
        return None
    pattern, value = match.groups()
    if re.search(r'(?<!\\)\\[pP]\{[^}]+\}', pattern):
        return finding('S-STRUCT', 2, 'JAVA_REGEX', ['E-AUX'], [ref],
                       'Unicode property escape requires an unsupported regex dialect; no IMPL inference.')
    repaired = pattern.replace('\\\\', '\\')
    if repaired == pattern:
        return None
    try:
        if re.search(pattern, value) is None and re.search(repaired, value) is not None:
            return finding('S-RESP-TYPE', 3, 'DOUBLE_ESCAPE', ['E-AUX'], [ref],
                           'Original pattern rejects value; collapsing double escapes matches it.')
    except re.error:
        return None


def alternative_format(message, ref):
    """§4 S-RESP-TYPE + §3 E-CONV: valid alternative dates lean SPEC.

    Accept only calendar-valid ISO dates/timestamps, explicit compact offsets,
    or common space-separated timestamps. Negative years, zero dates, impossible
    dates, arbitrary text and bare numbers abstain. This is weak intent evidence.
    """
    match = re.search(r'String "([^"]*)" is invalid against requested date format', message)
    if not match:
        return None
    value = match.group(1)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?)?', value):
        return None
    try:
        if len(value) == 10:
            dt.date.fromisoformat(value)
        else:
            # datetime accepts offsets such as +01:99 by normalization; reject.
            offset = re.search(r'[+-](\d{2}):?(\d{2})$', value)
            if offset and (int(offset[1]) > 23 or int(offset[2]) > 59):
                return None
            dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return finding('S-RESP-TYPE', 1, 'ALT_DATE_FORMAT', ['E-CONV'], [ref],
                   'Calendar-valid common alternative representation: ' + value)


class Context:
    """Raw representatives, exact-path observations and lazily loaded specs."""

    def __init__(self, rows, specs=None, spec_refs=None, documentation=None):
        self.rows = rows
        self.specs = specs or {}
        self.spec_refs = spec_refs or {}
        self.spec_errors = {}
        self._bodies = {id(r): json_body(r) for rs in rows.values() for r in rs}
        self._spec_paths = {}
        # Optional independently collected field documentation, never labels.
        # Key: (api, instance parent path, property); value: URL + retrieved_on.
        self.documentation = documentation or {}

    @classmethod
    def from_directory(cls, directory):
        directory = Path(directory)
        rows = {}
        for path in sorted(directory.glob('faultClustersConfirmedBugs_*.csv')):
            api = path.stem.removeprefix('faultClustersConfirmedBugs_')
            rows[api] = read_csv(path)
            seen = set()
            for row in rows[api]:
                if row['testCaseId'] in seen:
                    raise ValueError('Duplicate testCaseId: ' + str(path) + ':' + row['testCaseId'])
                seen.add(row['testCaseId'])
                row['_source'] = str(path) + ':testCaseId=' + row['testCaseId']
        ctx = cls(rows)
        ctx._spec_paths = {re.sub('[^a-z0-9]', '', p.name.split('__')[0].lower()): p
                           for p in sorted((directory / 'specs').glob('*__openapi.*'))}
        return ctx

    def raw(self, row):
        matches = [r for r in self.rows.get(row['api'], []) if r['testCaseId'] == row['testCaseId']]
        if len(matches) != 1:
            raise ValueError('Expected one raw row for ' + row['api'] + ':' + row['testCaseId'])
        raw = matches[0]
        if int(raw['statusCode']) != int(row['http_status']):
            raise ValueError('Sheet/raw status mismatch: ' + row['testCaseId'])
        if row.get('operation') != raw['httpMethod'] + ' ' + raw['path']:
            raise ValueError('Sheet/raw operation mismatch: ' + row['testCaseId'])
        return raw

    def peers(self, api, target):
        # Match status class: error envelopes must not become missing data fields.
        status_class = int(target['statusCode']) // 100
        return [r for r in self.rows.get(api, [])
                if int(r['statusCode']) // 100 == status_class and self._bodies[id(r)] is not MISSING]

    def spec(self, api):
        if api not in self.specs and api not in self.spec_errors:
            path = self._spec_paths.get(re.sub('[^a-z0-9]', '', api.lower()))
            try:
                if path is None:
                    raise ValueError('No local spec')
                _, specmut = helpers()
                self.specs[api] = specmut.load_spec(str(path))
                self.spec_refs[api] = str(path)
            except (ImportError, OSError, ValueError) as exc:
                self.spec_errors[api] = str(exc)
        return self.specs.get(api)


def consistency(ctx, api, raw, path, mode, value=MISSING):
    """§3 E-CONSIST/E-CROSS, §8.3 and R2: inspect exact paths in raw bodies.

    Prefer the same operation. Fall back to API-wide exact paths if needed;
    mark that as E-CROSS and keep confidence low. Require >=2 distinct response
    representatives, including one other testCaseId. Repetitions inside one
    body or totalFailures metadata never count as multiple responses. A stable
    extra property is only a SPEC lean: closed-source code intent is unavailable.
    """
    target_values = values_at(ctx._bodies[id(raw)], path)
    if not target_values or (mode == 'null' and not any(v is None for v in target_values)):
        return None
    if mode == 'repeat' and not any(json.dumps(v, sort_keys=True) == json.dumps(value, sort_keys=True)
                                    for v in target_values):
        return None
    peers = ctx.peers(api, raw)
    local = [r for r in peers if (r['path'], r['httpMethod']) == (raw['path'], raw['httpMethod'])]
    for scope, candidates in [('operation', local), ('api', peers)]:
        observations = []
        for row in candidates:
            vals = values_at(ctx._bodies[id(row)], path)
            if mode == 'property':
                parent, _, key = path.rpartition('/')
                key = key.replace('~1', '/').replace('~0', '~')
                vals = [key in obj for obj in values_at(ctx._bodies[id(row)], parent) if isinstance(obj, dict)]
            if vals:
                observations.append((row, vals))
        if len(observations) < 2 or not any(r['testCaseId'] != raw['testCaseId'] for r, _ in observations):
            continue
        flat = [v for _, vs in observations for v in vs]
        if mode == 'null':
            ok = any(v is None for v in flat) and any(v is not None for v in flat)
            locus, rule = 'S-RESP-TYPE', 'NULL_MIXED'
        elif mode == 'property':
            ok = all(flat)
            locus, rule = 'S-RESP-MISSING', 'PROPERTY_STABLE'
        elif mode == 'repeat':
            # JSON equality must not identify true with 1 (Python equality does).
            key = json.dumps(value, sort_keys=True, ensure_ascii=False)
            observations = [(r, vs) for r, vs in observations
                            if any(json.dumps(v, sort_keys=True, ensure_ascii=False) == key for v in vs)]
            ok = len(observations) >= 2
            locus, rule = 'S-RESP-VALUE', 'OUTLIER_REPEATED'
        else:
            raise ValueError('Unknown consistency mode: ' + mode)
        if ok:
            codes = ['E-CONSIST'] + (['E-CROSS'] if scope == 'api' else [])
            return finding(locus, 1, rule, codes, [source(r) for r, _ in observations],
                           f'{path}: {scope} scope; {len(observations)} response representatives; mode={mode}.')
    return None


def repeated_outlier(ctx, api, raw, path, message):
    """§3 E-CONSIST + §9.4 S-RESP-VALUE: repeated outliers lean SPEC.

    Verify that the reported value is outside the reported constraint; then
    require the *same* value in another response. Recurrence is not gold intent.
    """
    match = re.search(r'Instance value \((.*?)\) not found in enum \(possible values: (\[.*\])\)', message)
    if match:
        try:
            value = json.loads(match[1])
            allowed = json.loads(match[2].replace(';', ','))
        except ValueError:
            return None
        if value in allowed:
            return None
    else:
        match = re.search(r'Numeric instance is (lower|greater) than the required (minimum|maximum) \((?:minimum|maximum): ([^;]+); found: ([^)]+)\)', message)
        if not match:
            return None
        try:
            bound, value = float(match[3]), json.loads(match[4])
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return None
            if not (value < bound if match[1] == 'lower' else value > bound):
                return None
        except ValueError:
            return None
    return consistency(ctx, api, raw, path, 'repeat', value)


def helpers():
    """Load existing project helpers, including under Python -I (no cwd path)."""
    directory = str(Path(__file__).resolve().parent)
    if directory not in sys.path:
        sys.path.insert(0, directory)
    return importlib.import_module('conformance'), importlib.import_module('specmut')


def deref(spec, node, seen=(), allow_annotations=False):
    """Resolve only local references; cycles/external refs abstain, never fetch."""
    while isinstance(node, dict) and '$ref' in node:
        ref = node['$ref']
        if not isinstance(ref, str) or not ref.startswith('#/') or ref in seen:
            raise ValueError('Unresolved/cyclic/external reference')
        # Ref siblings differ between dialects; decline rather than discard them.
        annotations = {'$ref', 'description', 'title', 'example', 'examples', 'summary', 'externalDocs', 'deprecated'}
        if len(node) != 1 and not (allow_annotations and set(node) <= annotations):
            raise ValueError('Reference with siblings')
        seen += (ref,)
        node = spec
        for key in ref[2:].split('/'):
            node = node[key.replace('~1', '/').replace('~0', '~')]
    return node


def expand(spec, node, seen=()):
    if len(seen) > 40:
        raise ValueError('Schema depth/cycle limit')
    if isinstance(node, dict):
        if '$ref' in node:
            ref = node['$ref']
            if ref in seen:
                raise ValueError('Recursive schema')
            return expand(spec, deref(spec, node), seen + (ref,))
        return {k: expand(spec, v, seen + ('',)) for k, v in node.items()}
    if isinstance(node, list):
        return [expand(spec, v, seen + ('',)) for v in node]
    return node


def operation_for(spec, raw):
    conf, _ = helpers()
    template = raw['path']
    if template not in spec.get('paths', {}):
        template, _ = conf.Spec(spec).match(raw['path'])
    if template is None:
        return None, None
    item = deref(spec, spec['paths'][template])
    return template, deref(spec, item.get(raw['httpMethod'].lower(), {}))


def response_schema(spec, response):
    response = deref(spec, response)
    if 'schema' in response:
        return response['schema']
    content = response.get('content', {})
    return (content.get('application/json') or {}).get('schema')


def response_for(spec, raw):
    _, op = operation_for(spec, raw)
    if not op:
        return None
    responses = {str(k): v for k, v in op.get('responses', {}).items()}
    status = str(raw['statusCode'])
    for key in (status, status[0] + 'XX', 'default'):
        if key in responses:
            return deref(spec, responses[key])


def schema_at(spec, raw, path, expand_final=True):
    resp = response_for(spec, raw)
    if resp is None:
        return None
    node = response_schema(spec, resp)
    for key in path.strip('/').split('/') if path.strip('/') else []:
        node = deref(spec, node, allow_annotations=not expand_final)
        if not isinstance(node, dict):
            return None
        key = key.replace('~1', '/').replace('~0', '~')
        node = node.get('items') if key == '[item]' or key.isdigit() else node.get('properties', {}).get(key)
    # Policy checks need only this node, not expansion of unrelated cycles.
    return expand(spec, node) if expand_final else deref(spec, node, allow_annotations=True)


def undocumented_4xx(ctx, api, raw):
    """§3 E-CROSS + §4 S-STATUS: valid-input undocumented error object.

    Same status must be documented on another operation. If a response schema
    exists it must validate; description-only entries support only confidence 1.
    Empty objects, malformed JSON, and missing cross-operation status abstain.
    Request validity is only P001's supplied flag, not independent verification.
    """
    status = int(raw['statusCode'])
    if not 400 <= status < 500 or str(raw.get('faulty')).lower() != 'false':
        return None
    body = json_body(raw)
    if not isinstance(body, dict) or not body:
        return None
    text = body.get('message') or body.get('status') or body.get('error')
    if not isinstance(text, str) or not text.strip() or not any(k in body for k in ('code', 'error', 'status')):
        return None
    spec = ctx.spec(api)
    if spec is None:
        return None
    try:
        conf, sm = helpers()
        template, current = operation_for(spec, raw)
        if not current:
            return None
        statuses = {str(k) for k in current.get('responses', {})}
        if str(status) in statuses or 'default' in statuses or f'{status // 100}XX' in statuses:
            return None
        for path, method, op in sm.operations(spec):
            if (path, method) == (template, raw['httpMethod'].lower()):
                continue
            responses = {str(k): v for k, v in deref(spec, op).get('responses', {}).items()}
            if str(status) not in responses:
                continue
            entry = deref(spec, responses[str(status)])
            schema = response_schema(spec, entry)
            if schema is not None:
                schema = expand(spec, schema)
                if not conf.validator(schema, sm.is_oas3(spec)).is_valid(body):
                    continue
            elif not entry.get('description'):
                continue
            pointer = sm.ptr('paths', path, method, 'responses', status)
            ref = ctx.spec_refs.get(api, 'input:spec=' + api) + '#' + pointer
            return finding('S-STATUS', 2 if schema is not None else 1,
                           'STATUS_CROSS_DOCUMENTED', ['E-CROSS', 'E-AUX'], [source(raw), ref],
                           'Well-formed error; same status documented elsewhere' +
                           (' with matching schema.' if schema is not None else '; description only, body shape unverified.'))
    except (ImportError, KeyError, ValueError, TypeError):
        return None


def unsat_proof(schema):
    """§8.5: sufficient structural contradictions, never failed witness search.

    This deliberately incomplete checker proves only duplicate-only oneOf,
    impossible conjunction type intersections, and contradictory numeric bounds.
    Satisfiability of general JSON Schema is outside this prototype's scope.
    """
    if not isinstance(schema, dict) or schema.get('nullable') or schema.get('x-nullable'):
        return None
    branches = schema.get('oneOf', [])
    if len(branches) > 1 and all(branch == branches[0] for branch in branches):
        return 'Every oneOf branch is identical: instances match zero or multiple branches.'
    conjuncts = []

    def collect(node):
        if not isinstance(node, dict) or node.get('nullable') or node.get('x-nullable'):
            raise ValueError('Unsupported/nullable conjunction')
        conjuncts.append(node)
        for sub in node.get('allOf', []):
            collect(sub)
    try:
        collect(schema)
    except ValueError:
        return None
    types = {'null', 'boolean', 'object', 'array', 'string', 'integer', 'number'}
    for node in conjuncts:
        if 'type' in node:
            ts = set([node['type']] if isinstance(node['type'], str) else node['type'])
            if 'number' in ts:
                ts.add('integer')
            types &= ts
    if not types:
        return 'allOf has disjoint primitive types.'
    if types <= {'number', 'integer'}:
        lows = [n['minimum'] for n in conjuncts if 'minimum' in n]
        highs = [n['maximum'] for n in conjuncts if 'maximum' in n]
        if lows and highs and max(lows) > min(highs):
            return 'Required numeric lower bound exceeds upper bound.'
    return None


def composition(ctx, api, raw, path):
    """§8.4–8.5: SPEC only for a loaded branch with a structural UNSAT proof.

    Overlapping oneOf branches for one observed instance do not prove the whole
    schema unsatisfiable. Missing specs, unsupported refs, satisfiable branches,
    and inconclusive checks all return None (UNDECIDABLE at aggregation).
    """
    spec = ctx.spec(api)
    if spec is None:
        return None
    try:
        schema = schema_at(spec, raw, path)
        proof = unsat_proof(schema)
    except (ImportError, KeyError, TypeError, ValueError):
        return None
    if proof:
        return finding('S-STRUCT', 2, 'COMPOSITION_UNSAT', ['E-AUX'],
                       [source(raw), ctx.spec_refs.get(api, 'input:spec=' + api) + ':response-path=' + path], proof)


def documented_null(ctx, api, raw, path):
    """§3 evidence hierarchy + §8.3: explicit prose permits a null response.

    Supplement mixed-value E-CONSIST with local spec prose ('null if', 'otherwise
    null', 'always ... null'). This is E-AUX, not independent external E-DOC.
    Merely mentioning null or explicitly saying 'not null' does not qualify.
    A null observation and a non-nullable typed schema must both be present.
    """
    if not any(v is None for v in values_at(json_body(raw), path)):
        return None
    spec = ctx.spec(api)
    if spec is None:
        return None
    try:
        schema = schema_at(spec, raw, path)
        if not isinstance(schema, dict) or not schema.get('type') or schema.get('nullable') or schema.get('x-nullable'):
            return None
        if schema.get('type') == 'null' or (isinstance(schema['type'], list) and 'null' in schema['type']):
            return None
        prose = re.sub(r'[`*_]', '', schema.get('description', '')).lower()
        if re.search(r'\b(?:not|never|non)[ -]?null\b', prose):
            return None
        if not re.search(r'\bnull\s+if\b|\botherwise\s+null\b|\balways\b[^.]{0,60}\bnull\b', prose):
            return None
        return finding('S-RESP-TYPE', 2, 'NULL_DOCUMENTED_PROSE', ['E-AUX'],
                       [source(raw), ctx.spec_refs.get(api, 'input:spec=' + api) + ':response-path=' + path + '/description'],
                       'Schema prose explicitly permits null but typed schema lacks nullable: ' + schema['description'])
    except (ImportError, KeyError, TypeError, ValueError):
        return None


def composition_diagnostics(ctx, api, raw, path):
    """§9.5: record instance overlap and nullable-parent checks separately.

    Neither diagnostic establishes global UNSAT or developer intent. Keep the
    first representative as a source path + observation index + SHA-256 witness;
    do not copy an entire response subtree into every evidence note.
    """
    try:
        spec = ctx.spec(api)
        if spec is None:
            return {'limitation': 'No local spec'}
        schema = schema_at(spec, raw, path, expand_final=False)
        if not isinstance(schema, dict):
            return {'limitation': 'No schema at message path'}
        values = values_at(json_body(raw), path)
        try:
            proof = unsat_proof(schema_at(spec, raw, path))
        except (KeyError, TypeError, ValueError):
            proof = None
        result = {'global_unsat': 'proven' if proof else 'not_proven',
                  'nullable_parent_without_type': bool(schema.get('nullable') and 'type' not in schema)}
        if proof:
            result['global_unsat_witness'] = proof
        if values:
            witness = values[0]
            result['witness'] = {'response_path': path, 'observation_idx': 0,
                                 'sha256': hashlib.sha256(json.dumps(witness, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}
            conf, sm = helpers()
            for keyword in ('oneOf', 'allOf', 'anyOf'):
                if keyword in schema:
                    result[keyword + '_matching_branches'] = [i for i, branch in enumerate(schema[keyword])
                        if conf.validator(branch, spec if sm.is_oas3(spec) else False,
                                          direction='response', root=spec).is_valid(witness)]
        return result
    except Exception as exc:
        # The local-only resolver never fetches external refs. Unsupported
        # validator/schema cases produce a diagnostic limitation, never a label.
        return {'limitation': type(exc).__name__}


def strict_property(ctx, row, raw, path, message, sheet_ref):
    """§9.2: oracle policy is checked per message, including mixed clusters.

    Inspect the target schema and composition branches for explicit closure.
    An unknown path never implies default semantics. The supplied strict-only
    flag may support abstention-free policy classification if no schema loads.
    """
    if 'not allowed by the schema' not in message and 'undeclared property' not in message:
        return None
    spec = ctx.spec(row['api'])
    schema = None
    try:
        if spec is not None:
            schema = schema_at(spec, raw, path, expand_final=False)
    except (ImportError, KeyError, ValueError, TypeError):
        pass

    def open_policy(node, seen=()):
        if not isinstance(node, dict):
            return False
        node = deref(spec, node, allow_annotations=True)
        if not isinstance(node, dict) or id(node) in seen or node.get('additionalProperties', True) is not True:
            return False
        if 'unevaluatedProperties' in node or any(k in node for k in ('not', 'if', 'then', 'else')):
            return False
        return all(open_policy(branch, seen + (id(node),))
                   for key in ('allOf', 'oneOf', 'anyOf') for branch in node.get(key, []))

    try:
        allowed = open_policy(schema) if schema is not None else None
    except (KeyError, ValueError, TypeError):
        allowed = False
    if allowed is False:
        return None
    hit = strict_only(row, sheet_ref + ':fault_id=' + row['fault_id'])
    if allowed is not True and hit is None:
        return None
    if hit is None:
        hit = finding('T-ORACLE-STRICT', 2, 'STRICT_ONLY', ['E-AUX'], [],
                      'Undeclared-property oracle exceeds default OpenAPI semantics.', 'TEST')
    hit.refs += (source(raw),)
    if schema is not None:
        hit.refs += (ctx.spec_refs.get(row['api'], 'input:spec=' + row['api']) + ':response-path=' + path,)
        for prop in re.findall(r'"([^"]+)"', message):
            evidence = ctx.documentation.get((row['api'], path, prop), {})
            url, date = evidence.get('url', ''), evidence.get('retrieved_on', '')
            try:
                dt.date.fromisoformat(date)
            except (ValueError, TypeError):
                continue
            if prop not in schema.get('properties', {}) and re.match(r'https?://', url):
                hit.doc_gap = True
                hit.codes = tuple(sorted(set(hit.codes) | {'E-DOC'}))
                hit.refs += (url + ' retrieved_on=' + date,)
                hit.note += ' Public documentation includes absent schema field: ' + prop + '.'
    return hit


def environment(raw):
    """§9.3: R4 precedes R1; body evidence is limited to error envelopes."""
    if int(raw['statusCode']) in (429, 502, 503, 504):
        return finding('', 2, 'R4_ENV', ['E-CONV'], [source(raw)],
                       'Rate limit/gateway/service unavailable; repeatability unestablished.', 'ENV')
    body = json_body(raw)
    if isinstance(body, dict):
        text = ' '.join(str(body.get(k, '')) for k in ('error', 'message', 'title', 'detail'))
    elif body is MISSING:
        text = raw.get('responseBody', '')
    else:
        text = ''
    if re.search(r'\bbad gateway\b|\bgateway (?:time[ -]?out|error|failure|unavailable)\b|\b(?:timeout|timed out)\b|\b(?:request|connection|upstream|server) time out\b', text, re.I):
        return finding('', 2, 'R4_ENV_BODY', ['E-CONV'], [source(raw)],
                       'Gateway/timeout diagnostic in error body; repeatability unestablished.', 'ENV')


def malformed_json(ctx, api, raw):
    """§9.3: syntactically invalid body + documented JSON response contract.

    Swagger schema without produces also needs the captured expected JSON
    outputContentType_x. An actual JSON Content-Type alone is not a contract.
    """
    if json_body(raw) is not MISSING:
        return None
    spec = ctx.spec(api)
    if spec is None:
        return None
    try:
        _, op = operation_for(spec, raw)
        response = response_for(spec, raw)
        if response is None:
            return None
        if 'swagger' in spec:
            media = op.get('produces', spec.get('produces'))
            if media is None:
                media = [raw.get('outputContentType_x', '')] if 'schema' in response else []
        else:
            media = response.get('content', {})
        is_json = lambda value: value.split(';')[0].strip().lower() == 'application/json' or value.split(';')[0].strip().lower().endswith('+json')
        if not any(is_json(m) for m in media):
            return None
        return finding('I-RESP-CONTRACT', 2, 'MALFORMED_JSON', ['E-AUX', 'E-CONV'],
                       [source(raw), ctx.spec_refs.get(api, 'input:spec=' + api) + ':response-status=' + str(raw['statusCode'])],
                       'Captured body is syntactically invalid under documented JSON response contract.', 'IMPL')
    except (ImportError, KeyError, ValueError, TypeError):
        return None


def message_finding(row, ctx, raw, path, msg, sheet_ref):
    """§9: independent attribution; no R3 inference from closed-source code.

    confirmed/fixed flags cannot establish a fix direction and are not rules.
    Response-level ENV/5xx evidence applies to each message in that response.
    """
    ref, status = source(raw), int(raw['statusCode'])
    hit = environment(raw)
    if hit is not None:
        return hit
    if 500 <= status < 600:
        return finding('I-CRASH', 3, 'R1_5XX', ['E-CONV'], [ref], 'Observed server error.', 'IMPL')
    hit = strict_property(ctx, row, raw, path, msg, sheet_ref)
    if hit is None and 'Unable to parse JSON' in msg:
        hit = malformed_json(ctx, row['api'], raw)
    if hit is None:
        hit = broken_pattern(msg, ref)
    if hit is None and 'Instance type (null)' in msg:
        hit = consistency(ctx, row['api'], raw, path, 'null')
        if hit is None:
            hit = documented_null(ctx, row['api'], raw, path)
    if hit is None:
        hit = alternative_format(msg, ref)
    if hit is None:
        hit = repeated_outlier(ctx, row['api'], raw, path, msg)
    if hit is None and 'failed to match' in msg:
        hit = composition(ctx, row['api'], raw, path)
        if hit is None:
            diagnostics = composition_diagnostics(ctx, row['api'], raw, path)
            return finding('', 1, 'R5_INSUFFICIENT', ['E-AUX'],
                           [ref, ctx.spec_refs.get(row['api'], 'input:spec=' + row['api']) + ':response-path=' + path],
                           'Composition diagnostics (no intent attribution): ' + json.dumps(diagnostics, ensure_ascii=False), 'UNDECIDABLE')
    if hit is None and 'Response status' in msg:
        if status in (401, 403) or (400 <= status < 500 and truth(raw.get('faulty'))):
            hit = finding('S-STATUS', 2, 'STATUS_REJECT_INVALID_OR_AUTH', ['E-CONV', 'E-AUX'], [ref],
                          'Undocumented rejection/auth status; supplied invalidity flag if applicable.')
        else:
            hit = undocumented_4xx(ctx, row['api'], raw)
    if hit is None and 'Content-Type header' in msg:
        hit = finding('S-MEDIA', 1, 'MEDIA_TYPE_UNDOCUMENTED', ['E-AUX'], [ref],
                      'Retains baseline media-type SPEC lean; intent remains weak.')
    return hit or finding('', 1, 'R5_INSUFFICIENT', [], [ref],
                          'No supported intent evidence; mismatch alone is insufficient.', 'UNDECIDABLE')


MESSAGE_FIELDS = ['fault_id', 'msg_idx', 'message', 'L1', 'L2', 'confidence',
                  'rule', 'evidence_codes', 'refs', 'doc_gap', 'path', 'note']


def classify_messages(row, ctx, sheet_ref='input:sheet'):
    raw = ctx.raw(row)
    result = []
    for index, (path, msg) in enumerate(messages(raw['failReason']), 1):
        hit = message_finding(row, ctx, raw, path, msg, sheet_ref)
        refs = set(hit.refs) | {source(raw) + ':msg_idx=' + str(index),
                               sheet_ref + ':fault_id=' + row['fault_id']}
        result.append(dict(zip(MESSAGE_FIELDS, [
            row['fault_id'], index, (f"[Path '{path}'] " if path else '') + msg,
            hit.label, hit.locus, hit.confidence, hit.rule, ';'.join(hit.codes),
            json.dumps(sorted(refs), ensure_ascii=False), hit.doc_gap, path, hit.note])))
    return result


def aggregate_labels(labels):
    """§9.1; unspecified TEST/ENV mixtures conservatively remain undecidable.

    BOTH requires independently supported SPEC and IMPL messages. No decisive
    pattern/structure exception; unresolved messages always remain visible.
    """
    labels = set(labels)
    if not labels <= {'SPEC', 'IMPL', 'ENV', 'TEST', 'UNDECIDABLE'}:
        raise ValueError('Invalid message L1: ' + repr(labels))
    if len(labels) == 1:
        return next(iter(labels))
    if {'SPEC', 'IMPL'} <= labels:
        return 'BOTH'
    if labels == {'SPEC', 'UNDECIDABLE'}:
        return 'SPEC_PARTIAL'
    if labels == {'IMPL', 'UNDECIDABLE'}:
        return 'IMPL_PARTIAL'
    return 'UNDECIDABLE'


def score_label(label, mode='strict'):
    """§9.1: normalize partial labels for strict or lenient evaluation."""
    if mode not in ('strict', 'lenient'):
        raise ValueError('Scoring mode must be strict or lenient')
    if label in ('SPEC_PARTIAL', 'IMPL_PARTIAL'):
        return 'UNDECIDABLE' if mode == 'strict' else label.removesuffix('_PARTIAL')
    if label not in ('SPEC', 'IMPL', 'ENV', 'TEST', 'BOTH', 'UNDECIDABLE'):
        raise ValueError('Invalid cluster L1: ' + label)
    return label


def agreement(left, right, mode='strict'):
    """Raw agreement and Cohen's kappa; undefined degenerate kappa is None."""
    if len(left) != len(right) or not left:
        raise ValueError('Need equal, nonempty paired label sequences')
    left, right = [score_label(x, mode) for x in left], [score_label(x, mode) for x in right]
    n, a, b = len(left), Counter(left), Counter(right)
    matched = sum(x == y for x, y in zip(left, right))
    observed = matched / n
    expected = sum(a[k] * b[k] for k in a.keys() | b.keys()) / n ** 2
    return {'n': n, 'matched': matched, 'raw_agreement': observed,
            'kappa': (observed - expected) / (1 - expected) if expected != 1 else None}


def classify(row, ctx, sheet_ref='input:sheet', message_rows=None):
    """§9.1: aggregate message labels without discarding supported findings."""
    entries = classify_messages(row, ctx, sheet_ref) if message_rows is None else message_rows
    label = aggregate_labels(m['L1'] for m in entries)
    supported = [m for m in entries if m['L1'] != 'UNDECIDABLE']
    unresolved = [{'path': m['path'], 'message': m['message'], 'msg_idx': m['msg_idx']}
                  for m in entries if m['L1'] == 'UNDECIDABLE']
    mixed_gap = label == 'UNDECIDABLE' and bool(supported)
    return {
        'label_L1': label,
        'label_L2': '|'.join(sorted({m['L2'] for m in supported if m['L2']})),
        'confidence': min(m['confidence'] for m in supported) if supported and label != 'UNDECIDABLE' else 1,
        'evidence_codes': ';'.join(sorted({c for m in entries for c in m['evidence_codes'].split(';') if c})),
        'rules': ';'.join(sorted({m['rule'] for m in entries} | ({'AGGREGATION_RULE_GAP'} if mixed_gap else set()))),
        'evidence_refs': json.dumps(sorted({source(ctx.raw(row)), sheet_ref + ':fault_id=' + row['fault_id']} |
                                           {r for m in entries for r in json.loads(m['refs'])}), ensure_ascii=False),
        'evidence_details': json.dumps(entries, ensure_ascii=False),
        'unresolved': json.dumps(unresolved, ensure_ascii=False),
        'spec_limitation': ctx.spec_errors.get(row['api'], ''),
        'doc_gap': any(m['doc_gap'] for m in entries),
        'aggregation_gap': mixed_gap,
        'n_labelled_messages': len(entries),
        'note': ('Unspecified mixed L1 combination; conservative UNDECIDABLE.' if mixed_gap else
                 'Partial attribution; confidence applies to supported messages.' if label.endswith('_PARTIAL') else
                 'Message-level heuristic attribution aggregated under section 9.1.'),
        'codebook_ref': CODEBOOK + ':sections=2,3,4,8,9',
    }


def run(sheet, p001_dir, output, messages_output=None):
    rows = read_csv(sheet)
    if not rows:
        raise ValueError('Empty sheet')
    ctx = Context.from_directory(p001_dir)
    if messages_output is None:
        messages_output = Path(output).with_name('triage_messages.csv')
    if Path(output).resolve() == Path(messages_output).resolve():
        raise ValueError('Fault and message output paths must differ')
    results, message_rows = [], []
    for row in rows:
        entries = classify_messages(row, ctx, str(sheet))
        message_rows.extend(entries)
        results.append({**row, **classify(row, ctx, str(sheet), entries)})
    with Path(output).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    with Path(messages_output).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=MESSAGE_FIELDS)
        writer.writeheader()
        writer.writerows(message_rows)
    counts = Counter((r['label_L1'], r['confidence']) for r in results)
    print(json.dumps({f'{label}/confidence={conf}': n for (label, conf), n in sorted(counts.items())}))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sheet')
    parser.add_argument('p001_dir')
    parser.add_argument('output')
    parser.add_argument('--messages', dest='messages_output', help='Message CSV path (default: triage_messages.csv beside output)')
    args = parser.parse_args()
    run(args.sheet, args.p001_dir, args.output, args.messages_output)


if __name__ == '__main__':
    main()
