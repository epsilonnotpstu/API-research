"""Read-only market aggregates and independent saved-analysis LOOSE pairing audit.

No raw headers or arbitrary bodies are emitted. Three required-only request examples
are represented solely by locators, JSON shape, and fixed HAL error markers.
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P = ROOT / '08_experiments/E1_pilot/pilot_results'
RUNS = P.parent / 'runs'
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import conformance as c


def read_csv(path):
    return list(csv.DictReader(path.open()))


def analysis(run):
    return next(p.parent for p in sorted(run.glob('analysis-*/inputs.txt')) if not p.parent.name.endswith('-sut'))


def load_jsonl(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def safe(v):
    return {k: v[k] for k in ('kind', 'method', 'template', 'http_status', 'pointer', 'status')}


def loose_audit():
    runs = [r for r in read_csv(P / 'fuzzer_compare.csv') if r['fuzzer'] == 'schemathesis'
            and r['sut'] in ('scout-api', 'swagger-petstore') and r['severity'] == '30'
            and r['fault'] == 'REQUEST_LOOSE']
    report, new_count, partner_count, raw_mutated_new = [], 0, 0, 0
    for r in runs:
        run = RUNS / r['sut'] / r['run']
        ad = analysis(run)
        rows = read_csv(ad / 'fresh.attributed.csv')
        new = [v for v in rows if v['status'] == 'NEW' and v['op_mutated'] == 'True'
               and v['kind'] in ('INVALID_ACCEPTED', 'RESPONSE_SCHEMA')]
        checkable = sum(v['status'] == 'NEW' and v['op_mutated'] == 'True'
                        and not v['kind'].endswith('_UNCHECKABLE') for v in rows)
        assert checkable == int(r['fresh_mut_NEW_checkable'])
        raw_mutated_new += sum(v['status'] == 'NEW' and v['op_mutated'] == 'True' for v in rows)
        records = []
        for v in new:
            # Broad pairing requested by supervisor; additionally test status-aware pairing.
            partners = [w for w in rows if w['status'] == 'VANISHED'
                        and all(w[k] == v[k] for k in ('kind', 'method', 'template'))]
            same_status = [w for w in partners if w['http_status'] == v['http_status']]
            assert not partners
            records.append(safe(v) | {'same_kind_op_vanished': len(partners),
                                      'same_kind_op_status_vanished': len(same_status)})
            new_count += 1
            partner_count += bool(partners)
        # Violation identities are already persisted by the original offline checker.
        # Verify that every NEW is absent in paired baseline and present in fresh violations.
        bv = {v['fingerprint'] for v in load_jsonl(ad / 'baseline.violations.jsonl')}
        mv = {v['fingerprint']: v for v in load_jsonl(ad / 'fresh.violations.jsonl')}
        for v in new:
            assert v['fingerprint'] not in bv and v['fingerprint'] in mv
            assert v['kind'] == mv[v['fingerprint']]['kind']
        report.append({'run': r['run'], 'sut': r['sut'], 'analysis': str(ad.relative_to(ROOT)),
                       'source_sha256': hashlib.sha256((ad / 'fresh.attributed.csv').read_bytes()).hexdigest(),
                       'new_records': records})
    print(json.dumps({'loose_saved_runs': len(runs), 'loose_saved_NEW': new_count,
                      'partner_count': partner_count,
                      'per_run_NEW': {r['run']: len(r['new_records']) for r in report}}), flush=True)
    assert len(runs) == 7 and new_count == 13 and partner_count == 0
    return {'runs': len(runs), 'NEW': new_count, 'raw_mutated_NEW': raw_mutated_new,
            'with_same_kind_op_VANISHED': partner_count,
            'records': report, 'limitation': 'Persisted analyses, not new full raw scout/petstore checker passes.'}


def market_audit():
    report, samples, noreq = [], [], []
    for r in read_csv(P / 'strict_ablation.csv'):
        run = RUNS / 'market' / r['run']
        man = json.loads((run / 'manifest.json').read_text())
        ops = {(m['method'].upper(), m['path']) for m in man['mutations']}
        spec = c.Spec(json.loads(next(run.glob('spec.test.*')).read_text()), deploy_origin='http://sut-market:8080')
        st, bodies, statuses, links_shapes, parsed_statuses = Counter(), Counter(), Counter(), Counter(), Counter()
        contacts_links = contacts_links500 = false_text_matches = json_links_missed_by_text = 0
        diagnostic_errors = Counter()
        required_new = []
        ad = analysis(run)
        attr = read_csv(ad / 'fresh.attributed.csv')
        newfps = {v['fingerprint']: v for v in attr if v['status'] == 'NEW' and v['op_mutated'] == 'True'}
        fresh_saved = load_jsonl(ad / 'fresh.violations.jsonl')
        # Required-only diagnostic uses saved violation indexes; no extra checker run.
        required_indexes = {v.get('exchange') for v in fresh_saved if v['fingerprint'] in newfps}
        is_required = r['fuzzer'] == 'schemathesis' and r['variant'] == 'required'
        is_evo_noreq = r['fuzzer'] == 'evomaster' and r['variant'] == 'maxLength+maximum+param_required'
        ia = {fp: v for fp, v in newfps.items() if v['kind'] == 'INVALID_ACCEPTED'}
        ia_occurrences, ia_fps = Counter(), set()
        if is_evo_noreq:
            # Independently recompute current checker violations for three small market runs only.
            baseline_fps = {v['fingerprint'] for v in load_jsonl(ad / 'baseline.violations.jsonl')}
        sample = None
        exchanges = 0
        for line_num, e in enumerate(load_jsonl(run / 'exchanges.jsonl'), 1):
            exchanges += 1
            q, s = e['request'], e['response']
            method, path, status = q['method'], q['path'], int(s['status'])
            template, _ = spec.match(path, method, q.get('origin'))
            if (method.upper(), template) in ops:
                st[f'{status // 100}xx'] += 1
            text = (q.get('body') or {}).get('text') or ''
            invalid_json = False
            try:
                body = json.loads(text) if text else None
            except ValueError:
                invalid_json = True
                body = None
            has_links = isinstance(body, dict) and '_links' in body
            if method == 'PUT' and path == '/customer/contacts':
                statuses[(has_links, status)] += 1
                body_state = 'invalid_JSON' if invalid_json else 'object_with_links' if has_links else 'object_without_links' if isinstance(body, dict) else 'non_object_or_absent'
                parsed_statuses[(body_state, status)] += 1
                bodies['contacts_with_links' if has_links else 'contacts_without_links'] += 1
                if has_links:
                    contacts_links += 1
                    contacts_links500 += status == 500
                    links_shapes[type(body['_links']).__name__] += 1
                false_text_matches += '"_links"' in text and not has_links
                json_links_missed_by_text += has_links and '"_links"' not in text
                if '"_links"' in text:
                    diagnostic_errors['text_total'] += 1
                    diagnostic_errors['invalid_JSON'] += invalid_json
                    diagnostic_errors['incomplete_capture'] += bool((q.get('body') or {}).get('truncated') or (q.get('body') or {}).get('decode_error'))
                    response_text = (s.get('body') or {}).get('text') or ''
                    diagnostic_errors['HAL_Expected_relation_name'] += 'Expected relation name' in response_text
                    diagnostic_errors['other_error'] += status >= 500 and 'Expected relation name' not in response_text
            if is_required and line_num - 1 in required_indexes:
                response_text = (s.get('body') or {}).get('text') or ''
                marker = 'Expected relation name' in response_text
                dto = 'CartItemDTO' if 'CartItemDTO' in response_text else 'ContactsDTO' if 'ContactsDTO' in response_text else None
                assert status == 500 and has_links and isinstance(body['_links'], list) and marker and dto
                required_new.append((method, path, status, dto))
                if sample is None:
                    sample = {'run': r['run'], 'seed': r['seed'], 'exchange_line': line_num, 'method': method,
                              'path': path, 'status': status, 'links_shape': 'array', 'dto': dto,
                              'error_marker': 'Expected relation name'}
            if is_evo_noreq:
                for v in c.check(spec, e):
                    if v['kind'] == 'INVALID_ACCEPTED' and (v['method'], v['template']) in ops and v['fingerprint'] not in baseline_fps:
                        assert method == 'PUT' and path == '/customer/contacts' and not has_links and 200 <= status < 300
                        assert v['keyword'] == 'maxLength' and ('phone' in v['pointer'] or 'address' in v['pointer'])
                        ia_fps.add(v['fingerprint'])
                        ia_occurrences[(v['pointer'], status)] += 1
        assert exchanges == int(r['mutated_exchanges'])
        for status_class in ('2xx', '4xx', '5xx'):
            assert st[status_class] == int(r['mutop_' + status_class])
        # Record discrepancies: the production diagnostic uses a substring, not JSON membership.
        if contacts_links != int(r['contacts_put_with_links']) or contacts_links500 != int(r['contacts_put_with_links_500']):
            print(json.dumps({'diagnostic_mismatch_run': r['run'], 'JSON_links': contacts_links,
                              'JSON_links_500': contacts_links500, 'CSV_links': int(r['contacts_put_with_links']),
                              'CSV_links_500': int(r['contacts_put_with_links_500']),
                              'text_match_without_parsed_top_level_member': false_text_matches,
                              'text_false_negative': json_links_missed_by_text}), flush=True)
        if is_required:
            assert len(required_new) == 2 and sample
            log_lines = (run / 'compose.log').read_text().splitlines()
            dto = sample['dto']
            sample['compose_locators'] = {
                'handler': next(i for i, l in enumerate(log_lines, 1) if 'RestErrorResponse' in l and 'Expected relation name' in l),
                'dto': next(i for i, l in enumerate(log_lines, 1) if dto + '["_links"]' in l),
                'json_parse_exception': next(i for i, l in enumerate(log_lines, 1) if 'com.fasterxml.jackson.core.JsonParseException: Expected relation name' in l)}
            assert any('Jackson2HalModule$HalLinkListDeserializer.deserialize' in l for l in log_lines)
            samples.append(sample)
        if is_evo_noreq:
            assert ia_fps == set(ia)
            noreq.append({'run': r['run'], 'seed': r['seed'], 'NEW_INVALID_ACCEPTED_fps': len(ia_fps),
                          'NEW_INVALID_ACCEPTED_occurrences': sum(ia_occurrences.values()),
                          'pointers_status': {str(k): v for k, v in ia_occurrences.items()},
                          'all_new_are_contacts_PUT_without_links_2xx': True})
        report.append({'run': r['run'], 'fuzzer': r['fuzzer'], 'variant': r['variant'], 'seed': r['seed'],
                       'mutated_op_status_mix': dict(st), 'contacts_bodies': dict(bodies),
                       'contacts_status_by_links': {str(k): v for k, v in statuses.items()},
                       'contacts_status_by_JSON_state': {str(k): v for k, v in parsed_statuses.items()},
                       'contacts_links_shape': dict(links_shapes), 'JSON_links': contacts_links, 'JSON_links_500': contacts_links500,
                       'CSV_links': int(r['contacts_put_with_links']), 'CSV_links_500': int(r['contacts_put_with_links_500']),
                       'text_match_without_parsed_top_level_member': false_text_matches,
                       'text_false_negative': json_links_missed_by_text, 'diagnostic_errors': dict(diagnostic_errors)})
    assert len(samples) == 3 and len(noreq) == 3
    return {'traffic_rows_verified': len(report), 'traffic': report, 'HAL_examples': samples, 'evo_noreq': noreq}


if __name__ == '__main__':
    loose = loose_audit()
    (OUT / 'loose_real_data.json').write_text(json.dumps(loose, indent=2) + '\n')
    print(json.dumps({'loose_real_NEW': loose['NEW'], 'same_kind_op_vanished': loose['with_same_kind_op_VANISHED']}), flush=True)
    market = market_audit()
    (OUT / 'market.json').write_text(json.dumps(market, indent=2) + '\n')
    print(json.dumps({'market_traffic_rows': market['traffic_rows_verified'], 'HAL_examples': market['HAL_examples'],
                      'evo_noreq': market['evo_noreq']}, indent=2))
