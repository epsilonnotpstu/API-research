"""T35 offline market traffic analysis. Never serialize raw headers/body values."""
import csv
import hashlib
import importlib.util
import json
import re
import sys
import yaml
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PILOT = ROOT / '08_experiments/E1_pilot'
sys.path.insert(0, str(PILOT / 'pilot_results'))
import strict_exposure as se
c = se.c
c.INT_FORMATS = True
INPUTS = {}


def read(path):
    raw = path.read_bytes()
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return raw


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def shape(v):
    if v is None:
        return 'null'
    if isinstance(v, dict):
        return 'object'
    if isinstance(v, list):
        return 'array'
    return type(v).__name__


def response_kind(ex):
    text = ex['response'].get('body', {}).get('text', '') or ''
    if 'Expected relation name' in text:
        return 'Expected relation name'
    if 'HttpMessageNotReadableException' in text:
        return 'HttpMessageNotReadableException-other'
    if 'JSON parse error' in text:
        return 'JSON parse error-other'
    if 'Access is denied' in text:
        return 'Access is denied'
    return 'other'


def analyse():
    table = list(csv.DictReader(read(PILOT / 'pilot_results/strict_exposure.csv').decode().splitlines()))
    cells = [r for r in table if r['row_type'] == 'run' and r['sut'] == 'market']
    fixture = yaml.safe_load(read(ROOT / '08_experiments/_external/emb/auth/market-auth.yaml'))
    auth_reference = next(role for role in fixture['auth'] if role['name'] == 'user')['fixedHeaders'][0]['value']
    results, details, eligible_details = [], [], []
    for cell in cells:
        fresh = PILOT / 'runs/market' / cell['run']
        old = c.Spec(json.loads(read(fresh / 'spec.original.json')))
        new = c.Spec(json.loads(read(fresh / 'spec.test.json')))
        manifest = json.loads(read(fresh / 'manifest.json'))
        ops = {}
        for mutation in manifest['mutations']:
            locs, op = se.build_locations(old, new, mutation)
            for loc in locs:
                loc['constraints'] = []
                for pointer, before, after, err in loc['changes']:
                    loc['constraints'].append((pointer, err, pointer.rsplit('/', 1)[-1],
                        set(after) - set(before if isinstance(before, list) else []) if isinstance(after, list) else None))
            ops[(mutation['path'], mutation['method'].upper())] = locs
        for side, run_name in [('fresh', cell['run']), ('baseline', cell['baseline_run'])]:
            run = PILOT / 'runs/market' / run_name
            meta = json.loads(read(run / 'run.json'))
            lines = read(run / 'exchanges.jsonl').decode().split('\n')
            if lines[-1] == '':
                lines.pop()
            summary = {'id': cell['row_id'] + '.' + side, 'run': run_name,
                       'capture': str((run / 'exchanges.jsonl').relative_to(ROOT)),
                       'total': len(lines), 'metadata': {k: meta.get(k) for k in
                       ('fuzzer','seed','complete','sut_jar_sha256','source_spec','source_sha256','auth','auth_source_sha256','emb_commit','code_mutation','emb_config_sha256')},
                       'eligible_operations': Counter(), 'eligible_status': Counter(),
                       'contacts_status': Counter(), 'contacts_eligible_status': Counter(),
                       'contacts_groups': Counter(), 'contacts_violation_fields': Counter(),
                       'contacts_response_kinds': Counter(), 'eligible_response_kinds': Counter(),
                       'auth_states': Counter(), 'cookies_present': 0,
                       'operation_status': Counter()}
            last = None
            previous_delete = None
            first_by_group = {}
            for n, line in enumerate(lines, 1):
                ex = json.loads(line)
                req, resp = ex['request'], ex['response']
                headers = {k.lower(): v for k, v in req.get('headers', {}).items()}
                auth = headers.get('authorization')
                auth_state = ('absent' if auth is None else 'unrecoverable-redacted' if 'redact' in str(auth).lower()
                              else 'matches-user-fixture' if auth == auth_reference else 'other-unredacted')
                summary['auth_states'][auth_state] += 1
                summary['cookies_present'] += 'cookie' in headers
                path, pp = new.match(req['path'], req['method'], req.get('origin'))
                opkey = (path, req['method'].upper())
                opname = req['method'].upper() + ' ' + (path or '[unmatched]')
                status = int(resp['status'])
                summary['operation_status'][opname + ':' + str(status)] += 1
                hits = []
                for loc in ops.get(opkey, []):
                    old_errors = c.request_problems(old, loc['old_params'], loc['old_op'], ex, pp)
                    new_errors = c.request_problems(new, loc['new_params'], loc['new_op'], ex, pp)
                    if old_errors or old_errors.uncheckable or new_errors.uncheckable:
                        continue
                    for pointer, err, keyword, required in loc['constraints']:
                        if any(p == err and identity.get('keyword') == keyword and
                               (required is None or identity.get('property') in required)
                               for p, message, identity in new_errors):
                            hits.append(pointer)
                if hits:
                    summary['eligible_operations'][opname] += 1
                    summary['eligible_status'][str(status)] += 1
                    summary['eligible_response_kinds'][response_kind(ex)] += 1
                    eligible_details.append({'run': run_name, 'line': n, 'operation': opname,
                        'status': status, 'breaches': hits, 'auth_state': auth_state,
                        'auth_present': auth is not None,
                        'content_type': headers.get('content-type'), 'cookie_present': 'cookie' in headers,
                        'query_keys': sorted(req.get('query', {})),
                        'query_name_lengths': [len(v) for v in req.get('query', {}).get('name', [])],
                        'numeric_path_ids': {k:v for k,v in pp.items() if re.fullmatch(r'-?[0-9]+', str(v))}})
                if opkey == ('/customer/contacts', 'PUT'):
                    summary['contacts_status'][str(status)] += 1
                    parse_error = False
                    try:
                        body = json.loads(req.get('body', {}).get('text', ''))
                    except (ValueError, TypeError):
                        body = None
                        parse_error = True
                    b = body if isinstance(body, dict) else {}
                    links = b.get('_links')
                    linkshape = 'unknown-invalid-JSON' if parse_error else (shape(links) if '_links' in b else 'absent')
                    kind = response_kind(ex)
                    group = f'{status}|links={linkshape}|eligible={bool(hits)}|{kind}'
                    summary['contacts_groups'][group] += 1
                    summary['contacts_response_kinds'][kind] += 1
                    for p in hits:
                        summary['contacts_violation_fields'][p.rsplit('/properties/', 1)[-1]] += 1
                    if hits:
                        summary['contacts_eligible_status'][str(status)] += 1
                    phone, address = b.get('phone'), b.get('address')
                    record = {'run': run_name, 'line': n, 'status': status,
                              'eligible': bool(hits), 'breaches': hits,
                              'content_type': headers.get('content-type'), 'accept': headers.get('accept'),
                              'auth_state': auth_state,
                              'auth_present': auth is not None,
                              'cookie_present': 'cookie' in headers,
                              'query_keys': sorted(req.get('query', {})),
                              'query_name_lengths': [len(v) for v in req.get('query', {}).get('name', [])],
                              'body_json_parse_error': parse_error, 'body_json_type': shape(body),
                              'raw_links_array_prefix': bool(re.match(r'^\s*\{\s*"_links"\s*:\s*\[',req.get('body',{}).get('text',''))),
                              'first_body_key': next(iter(b),None),
                              'body_keys': sorted(b), 'links_shape': linkshape,
                              'all_link_properties_present': all(set(('deprecation','href','hreflang','media','name','profile','rel','title','type')) <= set(x)
                                  for x in links if isinstance(x, dict)) if isinstance(links, list) else None,
                              'all_link_strings_length_le_1': all(len(v) <= 1 for x in links if isinstance(x, dict)
                                  for k,v in x.items() if k != 'rel' and isinstance(v,str)) if isinstance(links, list) else None,
                              'links_count': len(links) if isinstance(links, (dict, list)) else None,
                              'link_item_shapes': dict(Counter(shape(x) for x in links)) if isinstance(links, list) else {},
                              'rel_shapes': dict(Counter(shape(x.get('rel')) if 'rel' in x else 'absent'
                                                        for x in links if isinstance(x, dict))) if isinstance(links, list) else {},
                              'phone_type': shape(phone), 'phone_length': len(phone) if isinstance(phone, str) else None,
                              'address_type': shape(address), 'address_length': len(address) if isinstance(address, str) else None,
                              'body_truncated': req.get('body', {}).get('truncated'),
                              'response_kind': kind, 'previous_request': last,
                              'previous_delete': previous_delete}
                    if status == 500 and kind == 'Expected relation name':
                        text = resp['body']['text']
                        record['response_evidence'] = {term: term in text for term in
                            ('com.fasterxml.jackson.databind.JsonMappingException', 'market.dto.ContactsDTO', '_links')}
                        try:
                            rb = json.loads(text)
                            record['empty_field_errors'] = rb.get('fieldErrors') == []
                            record['null_entity_name'] = rb.get('entityName') is None
                        except ValueError:
                            pass
                    details.append(record)
                    if group not in first_by_group:
                        first_by_group[group] = record
                last = {'line': n, 'operation': opname, 'status': status}
                if req['method'].upper() == 'DELETE':
                    previous_delete = last
            expected = json.loads(cell[side + '_violating_status_counts'])
            assert dict(summary['eligible_status']) == expected, (summary['id'], expected, summary['eligible_status'])
            summary['first_contacts_by_group'] = first_by_group
            results.append(summary)
    dump('traffic_summary.json', results)
    with (OUT / 'contacts.jsonl').open('w') as f:
        for row in details:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    with (OUT / 'eligible.jsonl').open('w') as f:
        for row in eligible_details:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    dump('inputs_sha256.json', INPUTS)
    print(json.dumps([{'id': r['id'], 'contacts_status':r['contacts_status'],
        'contacts_eligible_status': r['contacts_eligible_status'],
        'contacts_groups': r['contacts_groups'], 'eligible_operations':r['eligible_operations'],
        'auth_states': r['auth_states'], 'total':r['total']} for r in results], indent=2))


if __name__ == '__main__':
    analyse()
