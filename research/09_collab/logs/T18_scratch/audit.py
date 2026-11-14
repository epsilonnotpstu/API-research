"""Audit every captured T18 diagnostic without retaining credential values."""
import collections
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay import OUT, ROOT, RUN, SOURCE, save


def main():
    xs = [json.loads(s) for s in (RUN / 'exchanges.jsonl').read_text().splitlines()]
    mapping = json.loads((OUT / 'exchange_map.json').read_text())
    cases = []
    reasons = collections.Counter()
    for iid, lines in mapping.items():
        for n in lines:
            x = xs[n - 1]
            req, resp = x['request'], x['response']
            invalid_headers = {k: sorted({ord(c) for c in value
                                         if (ord(c) < 32 and c != '\t') or ord(c) == 127})
                               for k, value in req['headers'].items()}
            invalid_headers = {k: v for k, v in invalid_headers.items() if v}
            record = {'item_id': iid, 'exchange_line': n,
                      'invalid_header_control_codepoints': invalid_headers}
            text = req.get('body', {}).get('text', '')
            body = json.loads(text) if text else None
            if iid == 'C001':
                assert 'x-schemathesis-probe' in req['headers']
                assert 'x-schemathesis-probe-null' in invalid_headers
                label, category, roots = 'TEST', 'capability_probe', ['RC01']
            elif iid == 'C002':
                assert isinstance(body, dict)
                missing = [k for k in ('key', 'keyType') if k not in body]
                pattern = []
                if body.get('keyType') == 'GUID' and isinstance(body.get('key'), str):
                    if not re.fullmatch('[0-9A-Fa-f]{64}', body['key']):
                        pattern.append('GUID_key')
                if 'keyDob' in body and not re.fullmatch('[XxA-Fa-f0-9][A-Fa-f0-9]{63}', body['keyDob']):
                    pattern.append('keyDob')
                if body.get('keyType') == 'TELETAN' and isinstance(body.get('key'), str):
                    # Invalid alphabet fails independently of configured length and database state.
                    if any(c not in '23456789ABCDEFGHJKMNPQRSTUVWXYZ' for c in body['key']):
                        pattern.append('TELETAN_key_alphabet')
                record.update({'missing_required_fields': missing,
                               'source_pattern_violations': pattern})
                if invalid_headers:
                    assert resp['body']['size'] == 435
                    assert '<html' in resp['body']['text'].lower()
                    label, category, roots = 'TEST', 'invalid_HTTP_header', ['RC04']
                else:
                    assert not resp['body']['text'] and (missing or pattern)
                    label, category = 'SPEC', 'missing_request_constraints'
                    roots = (['RC02'] if missing else []) + (['RC03'] if pattern else [])
                    reasons.update('missing_' + k for k in missing)
                    reasons.update(pattern)
            elif iid in ('C003', 'C006'):
                assert not invalid_headers
                assert re.fullmatch('[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}',
                                    body['registrationToken'])
                assert not resp['body']['text']
                assert req['headers'].get('cwa-fake') != '1'
                label, category, roots = 'TEST', 'unestablished_registration_token_state', ['RC05']
            elif iid == 'C004':
                assert resp['status'] == 201
                assert 'authorization' in req['headers']
                label, category, roots = 'TEST', 'unsupported_object_header_validation', ['RC06']
            elif iid == 'C005':
                assert resp['status'] == 404 and not resp['body']['text']
                assert not resp['body'].get('truncated') and not resp['body'].get('decode_error')
                label, category, roots = 'SPEC', 'unwanted_error_body_schema', ['RC07']
            proposed = {'capability_probe': 'T-PROBE',
                        'invalid_HTTP_header': 'T-GEN-INVALID-HTTP',
                        'unestablished_registration_token_state': 'T-ORACLE-STATE',
                        'unsupported_object_header_validation': 'T-ORACLE-COVERAGE'}.get(category, '')
            record.update({'L1': label, 'category': category, 'root_cause_ids': roots,
                           'L2': ('S-REQ-LOOSE' if iid == 'C002' else 'S-RESP-MISSING') if label == 'SPEC' else '',
                           'proposed_L2': proposed})
            cases.append(record)
    logs = (RUN / 'compose.log').read_text().splitlines()
    phrases = {
        'unknown_registration_token_tan': 'VerificationAppSession not found for the registration token',
        'unknown_registration_token_testresult': 'Returning the test result for the registration token failed',
        'invalid_tan': 'No Tan found or Tan is invalid',
        'teletan_generated': 'The teleTAN is generated.',
        'invalid_GUID_syntax': 'The hashed guid has no valid pattern',
        'invalid_TELETAN_syntax': 'The teleTAN is not valid to the syntax constraints.',
        'capture_encoding_error': 'UnicodeEncodeError:',
        'firewall_error': 'RequestRejectedException:',
    }
    locations = {name: [n for n, line in enumerate(logs, 1) if phrase in line]
                 for name, phrase in phrases.items()}
    assert len(locations['unknown_registration_token_tan']) == 80
    assert len(locations['unknown_registration_token_testresult']) == 80
    assert len(locations['invalid_tan']) == 100
    assert len(locations['teletan_generated']) == 100
    # These are operation/category corroborations, not unique request/log identity joins.
    locations['join_scope'] = 'operation/category counts and source flow; no exact exchange identity join'
    locations['backend_error_matches'] = {
        phrase: [n for n, line in enumerate(logs, 1) if phrase in line]
        for phrase in ['UnknownHostException', 'ConnectException', 'FeignException']}
    save('log_locations.json', locations)
    save('case_labels.json', cases)
    summary = {'status': 'PASS', 'diagnostic_cases': len(cases),
               'L1_cases': dict(collections.Counter(c['L1'] for c in cases)),
               'C002_source_constraint_reasons_overlapping': dict(reasons),
               'C002_leaf_counts': dict(collections.Counter(c['L1'] for c in cases if c['item_id'] == 'C002')),
               'root_case_memberships': dict(collections.Counter(r for c in cases for r in c['root_cause_ids'])),
               'all_C003_C006_requests_precede_teletan_creation': max(mapping['C003'] + mapping['C006']) < min(mapping['C004']),
               'successful_registrationToken_responses': sum(x['request']['path'] == '/version/v1/registrationToken' and 200 <= x['response']['status'] < 300 for x in xs),
               'external_execution': False}
    save('case_summary.json', summary)
    evidence = [RUN / f for f in ['spec.original.json', 'generator-input.json', 'exchanges.jsonl', 'compose.log']]
    evidence += list(SOURCE.rglob('*.java'))
    evidence += [ROOT / f for f in ['08_experiments/tools/conformance.py', '08_experiments/tools/specmut.py',
                                  '08_experiments/R1_triage_codebook.md', '09_collab/tasks/T18.md',
                                  '08_experiments/E2_labelling/cwa-verification_baseline_s1_blind.csv']]
    save('input_sha256.json', {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence})
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
