"""Empirical look at the 147 confirmed faults of P001 (Martin-Lopez et al., FSE 2022) for R1.

Data: P001 supplementary material, Zenodo 10.5281/zenodo.6941292 (CC-BY 4.0), files
results-all/faultClustersConfirmedBugs_<api>.csv (one representative test per confirmed
fault, with full response body), additional/bugs_reported.csv, and the specs under
results-replication/resources/taas_eval/<API>/openapi.(yaml|json).

Outputs (to OUT_DIR):
  oas_violation_types.csv   violation-message types per OAS-disconformity fault (multi-label)
  developer_response.csv    reported / confirmed / fixed by P001 oracle category
  replay_agreement.csv      does tools/conformance.py reproduce P001's verdict per fault?
  constraint_agreement.csv  direct keyword/location/property matches to P001 messages
  summary.json              headline counts

Usage: python3 p001_oas_analysis.py P001_DIR OUT_DIR
"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote_plus

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import conformance  # noqa: E402
import specmut  # noqa: E402

MESSAGE_TYPES = [  # (type, regex on one ' --- '-separated message); order matters
    ('STATUS_UNDEFINED', r'Response status \d+ not defined'),
    ('CONTENT_TYPE', r'Content-Type header'),
    ('NO_BODY', r'no response body found'),
    ('MISSING_REQUIRED', r'missing required properties'),
    ('ADDITIONAL_PROPERTIES', r'not allowed by the schema'),
    ('TYPE_NULL', r'instance type \(null\) does not match'),
    ('TYPE_MISMATCH', r'instance type \(\w+\) does not match'),
    ('PATTERN', r'ECMA 262 regex'),
    ('ENUM', r'not found in enum'),
    ('FORMAT', r'invalid against requested date format|not a valid (email|hostname|IPv)'),
    ('NUMERIC_RANGE', r'numeric instance is (lower|greater|not strictly)'),
    ('LENGTH', r'is too (short|long)|array is too'),
    ('PARSE', r'Unable to parse JSON'),
    ('COMPOSITION', r'failed to match (exactly one|at least one|all required) schema'),
    ('INT_OVERFLOW', r'leads to overflow'),
]
CATEGORY_SHORT = {
    'OAS disconformity': 'F_OAS',
    'This faulty test case was expecting a 4XX status code(individual_parameter_constraint': 'F_2XXP',
    'This faulty test case was expecting a 4XX status code(inter_parameter_dependency': 'F_2XXD',
    "This test case's input was (possibly) correct": 'F_400',
    'Status code 5XX with invalid request': 'F_5XXI',
    'Status code 5XX with valid request': 'F_5XXV',
}
OUR_KIND_FOR = {'F_OAS': {'RESPONSE_SCHEMA', 'UNDOCUMENTED_STATUS', 'RESPONSE_CONTENT_TYPE', 'RESPONSE_PARSE'}, 'F_2XXP': {'INVALID_ACCEPTED'},
                'F_2XXD': {'INVALID_ACCEPTED'}, 'F_400': {'VALID_REJECTED'},
                'F_5XXI': {'SERVER_ERROR'}, 'F_5XXV': {'SERVER_ERROR'}}


def message_types(fail_reason):
    text = str(fail_reason).removeprefix('OAS disconformity:')
    types = set()
    for msg in filter(None, (m.strip() for m in text.split(' --- '))):
        types.add(next((t for t, rx in MESSAGE_TYPES if re.search(rx, msg, re.I)), 'OTHER'))
    return types


def kv(cell, decode=True):
    if not isinstance(cell, str):
        return {}
    out = {}
    for part in filter(None, cell.split(';')):
        k, _, v = part.partition('=')
        out[unquote_plus(k) if decode else k] = unquote_plus(v) if decode else v
    return out


def exchange(row, spec):
    path = row['path']
    for k, v in kv(row['pathParameters'], decode=False).items():
        path = path.replace('{' + k + '}', v)
    body = row['responseBody'] if isinstance(row['responseBody'], str) else ''
    return {'request': {'method': row['httpMethod'], 'path': spec.base + path,
                        'query': {k: [v] for k, v in kv(row['queryParameters']).items()},
                        'headers': {k.lower(): v for k, v in kv(row['headerParameters']).items()},
                        'body': {'text': row['bodyParameter'] if isinstance(row['bodyParameter'], str) else ''}},
            'response': {'status': int(row['statusCode']),
                         'headers': {'content-type': row['outputContentType_y']} if isinstance(row['outputContentType_y'], str) else {},
                         'body': {'text': body, 'truncated': False}}}


KEYWORDS_FOR = {
    'MISSING_REQUIRED': 'required', 'ADDITIONAL_PROPERTIES': 'additionalProperties',
    'TYPE_NULL': 'type', 'TYPE_MISMATCH': 'type', 'PATTERN': 'pattern',
    'ENUM': 'enum', 'FORMAT': 'format', 'STATUS_UNDEFINED': 'UNDOCUMENTED_STATUS',
    'CONTENT_TYPE': 'RESPONSE_CONTENT_TYPE', 'NO_BODY': 'RESPONSE_PARSE', 'PARSE': 'RESPONSE_PARSE',
}


def source_constraints(reason):
    """Conservative message-to-keyword/location mapping, with property identity.

    P001 [item] and our array indices normalize to '*'. Multiple source messages
    at that normalized location represent one constraint, not independent faults.
    Unmapped messages remain explicit and cannot count as full agreement.
    """
    constraints = {}
    for message in str(reason).removeprefix('OAS disconformity:').split(' --- '):
        message = message.strip()
        if not message:
            continue
        typ = next(iter(message_types(message)))
        if typ == 'OTHER' and re.search(r'failed to match at least one required schema', message, re.I):
            typ = 'COMPOSITION'
        match = re.search(r"\[Path '([^']*)'\]", message)
        location = match.group(1).replace('[item]', '*') if match else '/'
        keyword = KEYWORDS_FOR.get(typ, 'UNMAPPED:' + typ)
        if typ == 'COMPOSITION':
            keyword = 'oneOf' if 'exactly one' in message else 'anyOf' if 'at least one' in message else 'allOf'
        elif typ == 'NUMERIC_RANGE':
            minimum = 'minimum' in message.lower() or ('maximum' not in message.lower() and 'lower' in message.lower())
            keyword = ('exclusive' if 'not strictly' in message else '') + ('Minimum' if minimum else 'Maximum')
            keyword = keyword[0].lower() + keyword[1:]
        elif typ == 'LENGTH':
            keyword = ('min' if 'short' in message.lower() else 'max') + ('Items' if 'array' in message.lower() else 'Length')
        props = ['']
        if typ in ('MISSING_REQUIRED', 'ADDITIONAL_PROPERTIES'):
            tail = message.split('properties', 1)[-1]
            props = re.findall(r'"([^"\n]*)"', tail) or ['UNMAPPED_PROPERTY']
        for prop in props:
            key = (keyword, location or '/', prop)
            constraints.setdefault(key, []).append(message)
    return constraints


def constraint_matches(source, violations):
    """Only emitted findings count; nested composition candidate causes do not."""
    observed = {(v.get('keyword', v['kind']), v.get('instance_location', '/'), v.get('property', ''))
                for v in violations if v['kind'] in OUR_KIND_FOR['F_OAS']}
    return {key: key in observed for key in source}


def main(p001_dir, out_dir):
    p001, out = Path(p001_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    specs = {re.sub(r'__openapi\.(yaml|json)$', '', f.name).lower(): f for f in (p001 / 'specs').iterdir()}
    frames = []
    for f in sorted(glob.glob(str(p001 / 'faultClustersConfirmedBugs_*.csv'))):
        d = pd.read_csv(f, low_memory=False)
        d['api_file'] = Path(f).stem.split('_', 1)[1]
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df['oracle'] = df['failReasonCategory'].map(CATEGORY_SHORT).fillna('OTHER')

    # 1. violation-message types of OAS faults
    oas = df[df.oracle == 'F_OAS'].copy()
    oas['types'] = oas['failReason'].map(message_types)
    rows = [{'api': r.api_file, 'testCaseId': r.testCaseId, 'operation': f'{r.httpMethod} {r.path}',
             'status': r.statusCode, 'types': ';'.join(sorted(r.types))} for r in oas.itertuples()]
    pd.DataFrame(rows).to_csv(out / 'oas_violation_types.csv', index=False)
    type_counts = Counter(t for ts in oas['types'] for t in ts)

    # 2. developer response by oracle category
    bugs = pd.read_csv(p001 / 'bugs_reported.csv')
    j = df.merge(bugs, on='testCaseId', how='left', suffixes=('', '_bug'))
    def flag(col, val):
        return j[col].astype(str).str.lower().eq(val)
    j['dev_replied'], j['dev_confirmed'], j['dev_fixed'] = flag('replied', 'true'), flag('confirmed', 'true'), flag('fixed', 'true')
    dev = j.groupby('oracle').agg(faults=('testCaseId', 'size'), reported=('reported', lambda s: s.astype(str).str.lower().eq('true').sum()),
                                  replied=('dev_replied', 'sum'), confirmed=('dev_confirmed', 'sum'),
                                  fixed=('dev_fixed', 'sum')).reset_index()
    dev.to_csv(out / 'developer_response.csv', index=False)

    # 3. replay agreement with tools/conformance.py
    agree, constraint_rows = [], []
    cache = {}
    for r in df.itertuples():
        key = r.api_file.lower()
        if key not in specs:
            continue
        row = {'api': r.api_file, 'testCaseId': r.testCaseId, 'p001_oracle': r.oracle,
               'p001_types': ';'.join(sorted(message_types(r.failReason))) if r.oracle == 'F_OAS' else ''}
        source = source_constraints(r.failReason) if r.oracle == 'F_OAS' else {}
        details = {k: {'api': r.api_file, 'testCaseId': r.testCaseId, 'keyword': k[0],
                       'instance_location': k[1], 'property': k[2], 'source_messages': json.dumps(msgs),
                       'message_count': len(msgs)} for k, msgs in source.items()}
        row['constraint_total'] = len(source)
        for mode, strict in (('default', False), ('strict', True)):
            if (key, mode) not in cache:
                cache[(key, mode)] = conformance.Spec(specmut.load_spec(str(specs[key])), strict_additional=strict)
            spec = cache[(key, mode)]
            try:
                violations = conformance.check(spec, exchange(r._asdict(), spec))
                kinds = {v['kind'] for v in violations}
                err = ''
            except Exception as exc:  # keep going; report
                violations, kinds, err = [], set(), repr(exc)[:120]
            row[f'our_kinds_{mode}'] = ';'.join(sorted(kinds))
            row[f'category_redetected_{mode}'] = bool(kinds & OUR_KIND_FOR.get(r.oracle, set()))
            matches = constraint_matches(source, violations)
            row[f'constraint_matched_{mode}'] = sum(matches.values())
            row[f'constraint_agreed_any_{mode}'] = bool(source) and any(matches.values())
            row[f'constraint_agreed_all_{mode}'] = bool(source) and all(matches.values())
            for constraint_key, matched in matches.items():
                details[constraint_key][f'matched_{mode}'] = matched
                details[constraint_key][f'evidence_{mode}'] = json.dumps([
                    {'pointer': v['pointer'], 'fingerprint': v['fingerprint']}
                    for v in violations if (v.get('keyword', v['kind']), v.get('instance_location', '/'), v.get('property', '')) == constraint_key])
            row[f'error_{mode}'] = err
        agree.append(row)
        constraint_rows.extend(details.values())
    ag = pd.DataFrame(agree)
    ag.to_csv(out / 'replay_agreement.csv', index=False)
    pd.DataFrame(constraint_rows).to_csv(out / 'constraint_agreement.csv', index=False)
    by_oracle = ag.groupby('p001_oracle')[['category_redetected_default', 'category_redetected_strict']].agg(['sum', 'size']).reset_index()
    by_oracle.columns = ['_'.join(c).strip('_') for c in by_oracle.columns]
    oas_ag = ag[ag.p001_oracle == 'F_OAS']
    addl = oas_ag[oas_ag.p001_types.str.contains('ADDITIONAL_PROPERTIES')]

    summary = {
        'faults_total': int(len(df)), 'faults_by_oracle': df['oracle'].value_counts().to_dict(),
        'oas_faults_by_message_type': dict(type_counts.most_common()),
        'oas_faults_multi_type': int((oas['types'].map(len) > 1).sum()),
        'developer_response': dev.to_dict(orient='records'),
        'category_redetected_by_oracle': by_oracle.to_dict(orient='records'),
        'constraint_agreement_oas': {
            'unit': 'Within-fault unique (keyword, normalized instance location, property); array indices -> *; root -> /; directly emitted errors only',
            'faults': int(len(oas_ag)), 'unique_constraints_within_fault': int(oas_ag.constraint_total.sum()),
            **{f'{metric}_{mode}': int(oas_ag[f'{metric}_{mode}'].sum())
               for mode in ('default', 'strict') for metric in ('constraint_matched', 'constraint_agreed_any', 'constraint_agreed_all')},
        },
        'replay_errors': int((ag['error_default'] != '').sum() + (ag['error_strict'] != '').sum()),
        'additional_properties_faults': {'n': int(len(addl)),
                                         **{f'category_redetected_{mode}': int(addl[f'category_redetected_{mode}'].sum()) for mode in ('default', 'strict')},
                                         **{f'property_constraint_agreed_any_{mode}': int(len({d['testCaseId'] for d in constraint_rows
                                             if d['keyword'] == 'additionalProperties' and d[f'matched_{mode}']})) for mode in ('default', 'strict')}},
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=1, default=int))
    print(json.dumps(summary, indent=1, default=int))


if __name__ == '__main__':
    main(*sys.argv[1:3])
