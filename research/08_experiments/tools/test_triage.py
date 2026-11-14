"""Synthetic rule checks and P001 regressions; no external tools/SUTs run.

Run: /usr/bin/python3 -I -B 08_experiments/tools/test_triage.py
Spec-dependent tests import our existing conformance/specmut helpers and their
already-installed libraries. No network, build, installation or fixture writes.
"""
import contextlib
import csv
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import triage as T

ROOT = Path(__file__).resolve().parents[1]
P001 = ROOT / '_external' / 'p001'
SHEET = ROOT / 'E2_labelling' / 'p001_foas_labelling_sheet.csv'
OUTPUT = ROOT / 'E2_labelling' / 'triage_output_v03.csv'
MESSAGES = ROOT / 'E2_labelling' / 'triage_messages_v03.csv'


def raw(body, test_id='a', path='/x', status=200, reason='', invalid=False):
    return {'testCaseId': test_id, 'responseBody': json.dumps(body),
            'path': path, 'httpMethod': 'GET', 'statusCode': str(status),
            'failReason': reason, 'faulty': str(invalid), '_source': 'fixture.csv:testCaseId=' + test_id}


def sheet(row, **overrides):
    return {'api': 'api', 'fault_id': 'F001', 'testCaseId': row['testCaseId'],
            'http_status': row['statusCode'], 'strict_only': False,
            'operation': row['httpMethod'] + ' ' + row['path'], **overrides}


def spec_with(schema, extra=None):
    return {'swagger': '2.0', 'paths': {
        '/x': {'get': {'responses': {'200': {'schema': schema}}}}, **(extra or {})}}


class StrictPatternFormatTests(unittest.TestCase):
    def test_strict_flag_is_parsed_not_python_string_truth(self):
        self.assertIsNone(T.strict_only({'strict_only': 'False'}, 'sheet:F1'))
        hit = T.strict_only({'strict_only': 'True'}, 'sheet:F1')
        self.assertEqual((hit.label, hit.locus, hit.confidence), ('TEST', 'T-ORACLE-STRICT', 2))

    def test_double_escape_proves_original_failure_and_repair(self):
        msg = r'ECMA 262 regex "^\\d+(\\.\\d+)?$" does not match input string "399.00"'
        hit = T.broken_pattern(msg, 'fixture:F1')
        self.assertEqual((hit.rule, hit.confidence), ('DOUBLE_ESCAPE', 3))

    def test_double_escape_with_nonmatching_repair_abstains(self):
        msg = r'ECMA 262 regex "^\\d+$" does not match input string "abc"'
        self.assertIsNone(T.broken_pattern(msg, 'fixture:F1'))

    def test_ordinary_pattern_mismatch_does_not_imply_spec(self):
        self.assertIsNone(T.broken_pattern('ECMA 262 regex "^[0-9]+$" does not match input string "abc"', 'fixture:F1'))

    def test_java_unicode_property_is_dialect_defect(self):
        hit = T.broken_pattern(r'ECMA 262 regex "^\p{L}+$" does not match input string "abc"', 'fixture:F1')
        self.assertEqual((hit.label, hit.locus, hit.rule), ('SPEC', 'S-STRUCT', 'JAVA_REGEX'))

    def test_unknown_regex_compilation_error_abstains(self):
        self.assertIsNone(T.broken_pattern(r'ECMA 262 regex "[\\d" does not match input string "3"', 'fixture:F1'))

    def test_common_alternative_dates(self):
        for value in ('2021-11-03T00:00:00-0400', '2008-06-01 00:00:00', '2021-10-31T18:00:00', '2020-02-29'):
            with self.subTest(value=value):
                hit = T.alternative_format(f'String "{value}" is invalid against requested date format(s) yyyy-MM-dd', 'fixture:F1')
                self.assertEqual((hit.label, hit.confidence), ('SPEC', 1))

    def test_malformed_dates_and_sentinels_abstain(self):
        for value in ('2021-02-29', '2021-13-03', '-0001-11-30T00:00:00-0500', '0000-00-00',
                      'yesterday', '2021-11-03T00:00:00-0199'):
            with self.subTest(value=value):
                self.assertIsNone(T.alternative_format(f'String "{value}" is invalid against requested date format', 'fixture:F1'))


class ConsistencyTests(unittest.TestCase):
    def test_null_and_nonnull_across_responses(self):
        a, b = raw({'name': None}), raw({'name': 'ok'}, 'b')
        ctx = T.Context({'api': [a, b]})
        hit = T.consistency(ctx, 'api', a, '/name', 'null')
        self.assertEqual((hit.rule, hit.confidence), ('NULL_MIXED', 1))
        self.assertEqual(set(hit.refs), {'fixture.csv:testCaseId=a', 'fixture.csv:testCaseId=b'})

    def test_all_null_or_missing_is_not_positive_evidence(self):
        for body in ({'name': None}, {}):
            a, b = raw({'name': None}), raw(body, 'b')
            self.assertIsNone(T.consistency(T.Context({'api': [a, b]}), 'api', a, '/name', 'null'))

    def test_one_response_many_array_items_is_not_multiple_responses(self):
        a = raw({'items': [{'v': None}, {'v': 1}]})
        self.assertIsNone(T.consistency(T.Context({'api': [a]}), 'api', a, '/items/[item]/v', 'null'))

    def test_cross_operation_uses_exact_path_and_marks_cross(self):
        a, b = raw({'name': None}), raw({'name': 'ok'}, 'b', '/other')
        hit = T.consistency(T.Context({'api': [a, b]}), 'api', a, '/name', 'null')
        self.assertIn('E-CROSS', hit.codes)

    def test_same_leaf_at_unrelated_path_does_not_count(self):
        a, b = raw({'a': {'name': None}}), raw({'b': {'name': 'ok'}}, 'b', '/other')
        self.assertIsNone(T.consistency(T.Context({'api': [a, b]}), 'api', a, '/a/name', 'null'))

    def test_other_apis_and_error_envelopes_do_not_count(self):
        a = raw({'name': None})
        b = raw({'name': 'error'}, 'b', status=400)
        c = raw({'name': 'ok'}, 'c')
        self.assertIsNone(T.consistency(T.Context({'api': [a, b], 'other_api': [c]}), 'api', a, '/name', 'null'))

    def test_stable_property_requires_every_applicable_object(self):
        a = raw({'items': [{'extra': 1}, {'extra': 2}]})
        b = raw({'items': [{'extra': 3}]}, 'b')
        hit = T.consistency(T.Context({'api': [a, b]}), 'api', a, '/items/[item]/extra', 'property')
        self.assertEqual(hit.rule, 'PROPERTY_STABLE')
        c = raw({'items': [{'extra': 3}, {}]}, 'c')
        self.assertIsNone(T.consistency(T.Context({'api': [a, c]}), 'api', a, '/items/[item]/extra', 'property'))

    def test_json_pointer_escaping_and_numeric_indices(self):
        self.assertEqual(T.values_at({'a/b': [{'~v': 4}]}, '/a~1b/0/~0v'), [4])
        self.assertEqual(T.values_at({'x': None}, '/x'), [None])
        self.assertEqual(T.values_at({}, '/x'), [])

    def test_enum_recurrence_requires_same_value_in_another_response(self):
        a, b = raw({'price': '€'}), raw({'price': '€'}, 'b')
        msg = 'Instance value ("€") not found in enum (possible values: ["$";"$$"])'
        hit = T.repeated_outlier(T.Context({'api': [a, b]}), 'api', a, '/price', msg)
        self.assertEqual((hit.rule, hit.confidence), ('OUTLIER_REPEATED', 1))
        b = raw({'price': '￥'}, 'b')
        self.assertIsNone(T.repeated_outlier(T.Context({'api': [a, b]}), 'api', a, '/price', msg))

    def test_numeric_range_recurrence_and_singleton(self):
        a, b = raw({'rating': 0.0}), raw({'rating': 0.0}, 'b')
        msg = 'Numeric instance is lower than the required minimum (minimum: 1; found: 0.0)'
        hit = T.repeated_outlier(T.Context({'api': [a, b]}), 'api', a, '/rating', msg)
        self.assertEqual(hit.rule, 'OUTLIER_REPEATED')
        self.assertIsNone(T.repeated_outlier(T.Context({'api': [a]}), 'api', a, '/rating', msg))

    def test_reported_outlier_must_be_present_and_outside_constraint(self):
        a, b = raw({'rating': 3}), raw({'rating': 0}, 'b')
        msg = 'Numeric instance is lower than the required minimum (minimum: 1; found: 0)'
        self.assertIsNone(T.repeated_outlier(T.Context({'api': [a, b]}), 'api', a, '/rating', msg))
        msg = 'Numeric instance is lower than the required minimum (minimum: 1; found: 3)'
        self.assertIsNone(T.repeated_outlier(T.Context({'api': [a, b]}), 'api', a, '/rating', msg))

    def test_boolean_is_not_numeric_repeat(self):
        a, b = raw({'n': 1}), raw({'n': True}, 'b')
        self.assertIsNone(T.consistency(T.Context({'api': [a, b]}), 'api', a, '/n', 'repeat', 1))


class SpecEvidenceTests(unittest.TestCase):
    def test_error_status_documented_elsewhere_with_matching_schema(self):
        err = {'type': 'object', 'required': ['code', 'message'], 'properties': {
            'code': {'type': 'integer'}, 'message': {'type': 'string'}}}
        spec = spec_with({}, {'/other': {'get': {'responses': {'404': {'description': 'Missing', 'schema': err}}}}})
        a = raw({'code': 404, 'message': 'missing'}, status=404)
        hit = T.undocumented_4xx(T.Context({'api': [a]}, {'api': spec}), 'api', a)
        self.assertEqual((hit.rule, hit.confidence), ('STATUS_CROSS_DOCUMENTED', 2))

    def test_description_only_error_status_is_lower_confidence(self):
        spec = spec_with({}, {'/other': {'get': {'responses': {'404': {'description': 'Not found'}}}}})
        a = raw({'code': 'Missing', 'message': 'missing'}, status=404)
        hit = T.undocumented_4xx(T.Context({'api': [a]}, {'api': spec}), 'api', a)
        self.assertEqual(hit.confidence, 1)
        self.assertIn('description only', hit.note)

    def test_empty_error_undocumented_elsewhere_and_malformed_json_abstain(self):
        for body in ({}, {'code': 404, 'message': 'missing'}, 'not json'):
            a = raw(body, status=404)
            if body == 'not json':
                a['responseBody'] = body
            self.assertIsNone(T.undocumented_4xx(T.Context({'api': [a]}, {'api': spec_with({})}), 'api', a))

    def test_status_schema_mismatch_and_currently_documented_status_abstain(self):
        spec = spec_with({}, {'/other': {'get': {'responses': {'404': {'schema': {'type': 'array'}}}}}})
        a = raw({'code': 'Missing', 'message': 'missing'}, status=404)
        self.assertIsNone(T.undocumented_4xx(T.Context({'api': [a]}, {'api': spec}), 'api', a))
        spec['paths']['/x']['get']['responses']['404'] = {'description': 'Already present'}
        self.assertIsNone(T.undocumented_4xx(T.Context({'api': [a]}, {'api': spec}), 'api', a))

    def test_missing_spec_or_helper_abstains_without_installation(self):
        a = raw({'code': 404, 'message': 'missing'}, status=404)
        ctx = T.Context({'api': [a]})
        self.assertIsNone(T.undocumented_4xx(ctx, 'api', a))
        self.assertIn('api', ctx.spec_errors)
        spec = spec_with({'oneOf': [{'type': 'string'}] * 2})
        with patch.object(T, 'helpers', side_effect=ImportError('unavailable')):
            self.assertIsNone(T.composition(T.Context({'api': [a]}, {'api': spec}), 'api', a, ''))

    def test_duplicate_only_oneof_has_unsat_proof(self):
        schema = {'oneOf': [{'type': 'string'}, {'type': 'string'}]}
        a = raw('x')
        hit = T.composition(T.Context({'api': [a]}, {'api': spec_with(schema)}), 'api', a, '')
        self.assertEqual((hit.label, hit.rule), ('SPEC', 'COMPOSITION_UNSAT'))

    def test_partial_overlap_or_duplicate_subset_is_not_unsat(self):
        for schema in ({'oneOf': [{'type': 'number'}, {'type': 'integer'}]},
                       {'oneOf': [{'type': 'string'}, {'type': 'string'}, {'type': 'number'}]}):
            a = raw(1)
            self.assertIsNone(T.composition(T.Context({'api': [a]}, {'api': spec_with(schema)}), 'api', a, ''))

    def test_allof_disjoint_types_and_numeric_contradiction(self):
        self.assertIsNotNone(T.unsat_proof({'allOf': [{'type': 'string'}, {'type': 'number'}]}))
        self.assertIsNotNone(T.unsat_proof({'type': 'number', 'allOf': [{'minimum': 5}, {'maximum': 1}]}))
        self.assertIsNone(T.unsat_proof({'allOf': [{'type': 'number'}, {'type': 'integer'}]}))
        self.assertIsNone(T.unsat_proof({'allOf': [{'minimum': 5}, {'maximum': 1}]}))  # non-numbers remain valid

    def test_nullable_or_external_recursive_schema_is_inconclusive(self):
        a = raw(None)
        for schema in ({'nullable': True, 'oneOf': [{'type': 'string'}] * 2},
                       {'$ref': 'https://example.invalid/schema'}, {'$ref': '#/definitions/recursive'}):
            spec = spec_with(schema)
            spec['definitions'] = {'recursive': {'$ref': '#/definitions/recursive'}}
            self.assertIsNone(T.composition(T.Context({'api': [a]}, {'api': spec}), 'api', a, ''))

    def test_documented_null_prose_is_positive_evidence(self):
        a = raw({'next': None})
        schema = {'type': 'object', 'properties': {'next': {'type': 'string', 'description': 'URL; `null` if none.'}}}
        hit = T.documented_null(T.Context({'api': [a]}, {'api': spec_with(schema)}), 'api', a, '/next')
        self.assertEqual((hit.rule, hit.confidence, hit.codes), ('NULL_DOCUMENTED_PROSE', 2, ('E-AUX',)))

    def test_null_prose_must_allow_null_and_missing_nullable(self):
        a = raw({'next': None})
        for prop in ({'type': 'string', 'description': 'Must never be null.'},
                     {'type': 'string', 'description': 'Discuss null handling elsewhere.'},
                     {'type': 'string', 'description': 'null if none', 'nullable': True}):
            schema = {'type': 'object', 'properties': {'next': prop}}
            self.assertIsNone(T.documented_null(T.Context({'api': [a]}, {'api': spec_with(schema)}), 'api', a, '/next'))


class AggregationTests(unittest.TestCase):
    def test_5xx_is_positive_impl_evidence_except_env_statuses(self):
        for status, expected in ((500, 'IMPL'), (501, 'IMPL'), (502, 'ENV'), (503, 'ENV'), (504, 'ENV'), (429, 'ENV')):
            a = raw({}, status=status, reason='Response status not defined')
            result = T.classify(sheet(a), T.Context({'api': [a]}))
            self.assertEqual(result['label_L1'], expected)

    def test_response_type_mismatch_never_implies_impl(self):
        a = raw({'n': 'x'}, reason='OAS disconformity: [Path \'/n\'] Instance type (string) does not match any allowed primitive type (allowed: ["integer"])')
        result = T.classify(sheet(a), T.Context({'api': [a]}))
        self.assertEqual(result['label_L1'], 'UNDECIDABLE')
        self.assertTrue(json.loads(result['unresolved']))

    def test_evidence_from_supported_subfinding_does_not_hide_unknown(self):
        reason = 'OAS disconformity: [Path \'/n\'] Instance type (null) does not match any allowed primitive type --- [Path \'/other\'] Object has missing required properties (["x"])'
        a, b = raw({'n': None}, reason=reason), raw({'n': 'ok'}, 'b')
        result = T.classify(sheet(a), T.Context({'api': [a, b]}))
        self.assertEqual(result['label_L1'], 'SPEC_PARTIAL')
        self.assertIn('NULL_MIXED', result['rules'])

    def test_strict_only_property_is_test(self):
        a = raw({'extra': 1}, reason='OAS disconformity: undeclared property')
        result = T.classify(sheet(a, strict_only='True'), T.Context({'api': [a]}))
        self.assertEqual((result['label_L1'], result['rules']), ('TEST', 'STRICT_ONLY'))

    def test_raw_join_rejects_missing_or_mismatched_data(self):
        a = raw({})
        ctx = T.Context({'api': [a]})
        for row in (sheet(a, testCaseId='absent'), sheet(a, http_status='400'), sheet(a, operation='GET /other')):
            with self.assertRaises(ValueError):
                T.classify(row, ctx)

    def test_cli_run_preserves_sheet_columns_with_in_memory_output(self):
        a = raw({}, status=500, reason='Response status not defined')
        rows = [sheet(a, suggested_L1='UNDECIDABLE')]
        buffers = {'out.csv': io.StringIO(), 'messages.csv': io.StringIO()}

        @contextlib.contextmanager
        def output_file(path, *args, **kwargs):
            yield buffers[str(path)]

        with patch.object(T, 'read_csv', return_value=rows), \
             patch.object(T.Context, 'from_directory', return_value=T.Context({'api': [a]})), \
             patch.object(Path, 'open', output_file), contextlib.redirect_stdout(io.StringIO()):
            T.run('sheet.csv', 'p001', 'out.csv', 'messages.csv')
        out = list(csv.DictReader(io.StringIO(buffers['out.csv'].getvalue())))
        self.assertEqual(out[0]['label_L1'], 'IMPL')
        self.assertEqual(out[0]['suggested_L1'], 'UNDECIDABLE')
        msg = list(csv.DictReader(io.StringIO(buffers['messages.csv'].getvalue())))
        self.assertEqual((msg[0]['fault_id'], msg[0]['msg_idx'], msg[0]['L1']), ('F001', '1', 'IMPL'))


class V03RuleTests(unittest.TestCase):
    def test_aggregation_table_and_unspecified_mixtures(self):
        cases = [([], 'UNDECIDABLE'), (['UNDECIDABLE'], 'UNDECIDABLE'),
                 (['SPEC', 'SPEC'], 'SPEC'), (['IMPL'], 'IMPL'), (['ENV'], 'ENV'), (['TEST'], 'TEST'),
                 (['SPEC', 'UNDECIDABLE'], 'SPEC_PARTIAL'),
                 (['IMPL', 'UNDECIDABLE'], 'IMPL_PARTIAL'),
                 (['SPEC', 'IMPL'], 'BOTH'), (['SPEC', 'IMPL', 'UNDECIDABLE'], 'BOTH'),
                 (['TEST', 'SPEC'], 'UNDECIDABLE'), (['TEST', 'UNDECIDABLE'], 'UNDECIDABLE'),
                 (['ENV', 'SPEC'], 'UNDECIDABLE'), (['ENV', 'UNDECIDABLE'], 'UNDECIDABLE')]
        for labels, expected in cases:
            with self.subTest(labels=labels):
                self.assertEqual(T.aggregate_labels(labels), expected)
        with self.assertRaises(ValueError):
            T.aggregate_labels(['SPEC_PARTIAL'])

    def test_both_requires_independent_message_evidence(self):
        reason = 'known spec --- known impl --- unknown'
        a = raw({}, reason=reason)
        hits = [T.finding('S-STRUCT', 2, 'SPEC_PROOF', ['E-AUX'], ['spec.json#/x'], 'spec witness'),
                T.finding('I-RESP-CONTRACT', 2, 'IMPL_PROOF', ['E-AUX'], ['raw.csv:1'], 'impl witness', 'IMPL'),
                T.finding('', 1, 'R5_INSUFFICIENT', [], ['raw.csv:1'], 'unknown', 'UNDECIDABLE')]
        with patch.object(T, 'message_finding', side_effect=hits):
            out = T.classify(sheet(a), T.Context({'api': [a]}))
        self.assertEqual(out['label_L1'], 'BOTH')
        self.assertEqual(out['label_L2'], 'I-RESP-CONTRACT|S-STRUCT')
        self.assertEqual(len(json.loads(out['unresolved'])), 1)
        self.assertIn('spec.json#/x', out['evidence_refs'])
        self.assertIn('raw.csv:1', out['evidence_refs'])

    def test_decisive_structural_proof_cannot_hide_unknown(self):
        a = raw('x', reason="[Path ''] instance failed to match exactly one schema --- unknown")
        ctx = T.Context({'api': [a]}, {'api': spec_with({'oneOf': [{'type': 'string'}] * 2})})
        out = T.classify(sheet(a), ctx)
        self.assertEqual(out['label_L1'], 'SPEC_PARTIAL')
        self.assertEqual([m['L1'] for m in json.loads(out['evidence_details'])], ['SPEC', 'UNDECIDABLE'])

    def test_default_extra_property_in_mixed_fault_is_test(self):
        reason = "[Path ''] Object instance has properties which are not allowed by the schema: [\"extra\"] --- unknown"
        a = raw({'extra': 1}, reason=reason)
        out = T.classify(sheet(a, strict_only='False'), T.Context({'api': [a]}, {'api': spec_with({'type': 'object'})}))
        ms = json.loads(out['evidence_details'])
        self.assertEqual((ms[0]['L1'], ms[0]['L2']), ('TEST', 'T-ORACLE-STRICT'))
        self.assertEqual(out['label_L1'], 'UNDECIDABLE')
        self.assertTrue(out['aggregation_gap'])

    def test_strict_flag_does_not_short_circuit_unrelated_messages(self):
        a = raw({}, reason='unknown type mismatch')
        self.assertEqual(T.classify(sheet(a, strict_only=True), T.Context({'api': [a]}))['label_L1'], 'UNDECIDABLE')

    def test_explicit_closure_schema_constraint_and_unknown_path_are_not_default(self):
        reason = 'Object instance has properties which are not allowed by the schema: ["extra"]'
        a = raw({'extra': 1}, reason=reason)
        for schema in ({'additionalProperties': False}, {'additionalProperties': {'type': 'integer'}},
                       {'allOf': [{'additionalProperties': False}]}, {'unevaluatedProperties': False}):
            ctx = T.Context({'api': [a]}, {'api': spec_with(schema)})
            self.assertEqual(T.classify(sheet(a, strict_only=True), ctx)['label_L1'], 'UNDECIDABLE')
        a['failReason'] = "[Path '/missing'] " + reason
        ctx = T.Context({'api': [a]}, {'api': spec_with({})})
        self.assertEqual(T.classify(sheet(a), ctx)['label_L1'], 'UNDECIDABLE')

    def test_recursive_policy_abstains(self):
        a = raw({}, reason='undeclared property')
        spec = spec_with({'$ref': '#/definitions/r'})
        spec['definitions'] = {'r': {'allOf': [{'$ref': '#/definitions/r'}]}}
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}, {'api': spec}))['label_L1'], 'UNDECIDABLE')

    def test_property_policy_follows_refs_with_annotation_siblings_only(self):
        a = raw({'extra': 1}, reason='undeclared property')
        spec = spec_with({'$ref': '#/definitions/r', 'description': 'Response annotation'})
        spec['definitions'] = {'r': {'type': 'object'}}
        ctx = T.Context({'api': [a]}, {'api': spec})
        self.assertEqual(T.classify(sheet(a), ctx)['label_L1'], 'TEST')
        spec['paths']['/x']['get']['responses']['200']['schema']['additionalProperties'] = False
        self.assertEqual(T.classify(sheet(a), ctx)['label_L1'], 'UNDECIDABLE')

    def test_composition_instance_and_converter_checks_have_separate_witnesses(self):
        a = raw(1)
        ctx = T.Context({'api': [a]}, {'api': spec_with({'oneOf': [{'type': 'number'}, {'type': 'integer'}]})})
        diag = T.composition_diagnostics(ctx, 'api', a, '')
        self.assertEqual(diag['global_unsat'], 'not_proven')
        self.assertEqual(diag['oneOf_matching_branches'], [0, 1])
        self.assertEqual(len(diag['witness']['sha256']), 64)
        self.assertIsNone(T.composition(ctx, 'api', a, ''))
        ctx = T.Context({'api': [a]}, {'api': spec_with({'oneOf': [{'type': 'integer'}] * 2})})
        diag = T.composition_diagnostics(ctx, 'api', a, '')
        self.assertEqual(diag['global_unsat'], 'proven')
        self.assertIn('identical', diag['global_unsat_witness'])
        a = raw(None)
        schema = {'nullable': True, 'oneOf': [{'type': 'object'}, {'type': 'array'}]}
        ctx = T.Context({'api': [a]}, {'api': spec_with(schema)})
        diag = T.composition_diagnostics(ctx, 'api', a, '')
        self.assertTrue(diag['nullable_parent_without_type'])
        self.assertEqual(diag['oneOf_matching_branches'], [])
        a['failReason'] = 'instance failed to match exactly one schema'
        out = T.classify(sheet(a), ctx)
        self.assertEqual(out['label_L1'], 'UNDECIDABLE')
        self.assertIn('nullable_parent_without_type', out['evidence_details'])

    def test_doc_gap_requires_missing_field_url_and_retrieval_date(self):
        a = raw({'extra': 1}, reason='Object instance has properties which are not allowed by the schema: ["extra"]')
        spec = spec_with({'type': 'object', 'properties': {}})
        key = ('api', '', 'extra')
        for evidence, expected in (({}, False), ({'url': 'https://example.org/fields#extra'}, False),
                                   ({'url': 'https://example.org/fields#extra', 'retrieved_on': 'yesterday'}, False),
                                   ({'url': 'https://example.org/fields#extra', 'retrieved_on': '2026-11-13'}, True)):
            ctx = T.Context({'api': [a]}, {'api': spec}, documentation={key: evidence})
            m = T.classify_messages(sheet(a), ctx)[0]
            self.assertEqual((m['L1'], m['doc_gap']), ('TEST', expected))
            self.assertLessEqual(m['confidence'], 2)
            if expected:
                self.assertIn('retrieved_on=2026-11-13', m['refs'])
                self.assertIn('E-DOC', m['evidence_codes'])
        spec['paths']['/x']['get']['responses']['200']['schema']['properties']['extra'] = {}
        ctx = T.Context({'api': [a]}, {'api': spec}, documentation={key: evidence})
        self.assertFalse(T.classify_messages(sheet(a), ctx)[0]['doc_gap'])

    def test_gateway_timeout_body_precedes_5xx(self):
        for status, body in ((500, {'error': 'upstream timed out'}), (200, '<h1>504 Gateway Timeout</h1>'),
                             (403, {'message': 'Bad Gateway'}), (200, {'error': 'timeout'}),
                             (500, {'title': 'Gateway error'})):
            a = raw(body, status=status, reason='Response status not defined')
            if isinstance(body, str):
                a['responseBody'] = body
            out = T.classify(sheet(a), T.Context({'api': [a]}))
            self.assertEqual((out['label_L1'], out['rules']), ('ENV', 'R4_ENV_BODY'))
        a = raw({'data': 'gateway timeout'}, reason='unknown')
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}))['label_L1'], 'UNDECIDABLE')

    def test_malformed_json_requires_documented_json_and_failed_decode(self):
        a = raw({}, reason='Unable to parse JSON')
        a['responseBody'] = '{"error":"unescaped "quote""}'
        for schema, expected in ((spec_with({}), 'UNDECIDABLE'),
                                 ({**spec_with({}), 'produces': ['application/json']}, 'IMPL'),
                                 ({**spec_with({}), 'produces': ['text/plain']}, 'UNDECIDABLE')):
            ctx = T.Context({'api': [a]}, {'api': schema})
            self.assertEqual(T.classify(sheet(a), ctx)['label_L1'], expected)
        a['outputContentType_x'] = 'application/json'
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}, {'api': spec_with({})}))['label_L1'], 'IMPL')
        a['responseBody'] = 'null'
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}, {'api': spec_with({})}))['label_L1'], 'UNDECIDABLE')
        for body in ('NaN', 'Infinity', '{"n":-Infinity}'):
            a['responseBody'] = body
            self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}, {'api': spec_with({})}))['label_L1'], 'IMPL')

    def test_malformed_json_oas3_exact_range_default_and_vendor_media(self):
        for status in ('200', '2XX', 'default'):
            a = raw({}, reason='Unable to parse JSON')
            a['responseBody'] = 'broken'
            spec = {'openapi': '3.0.3', 'paths': {'/x': {'get': {'responses': {
                status: {'content': {'application/problem+json': {'schema': {'type': 'object'}}}}}}}}}
            self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}, {'api': spec}))['label_L1'], 'IMPL')
        spec['paths']['/x']['get']['responses'] = {'404': {'content': {'application/json': {}}}}
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}, {'api': spec}))['label_L1'], 'UNDECIDABLE')

    def test_closed_source_invalid_accepted_and_undirected_dev_flags_abstain(self):
        a = raw({'offset': 500}, invalid=True, reason='Invalid input accepted with 200')
        for extra in ({}, {'dev_confirmed': 'True', 'dev_fixed': 'True'}):
            out = T.classify(sheet(a, **extra), T.Context({'api': [a]}, {'api': spec_with({})}))
            self.assertEqual(out['label_L1'], 'UNDECIDABLE')
            self.assertNotIn('R3', out['rules'])
            self.assertNotIn('E-CODE-INTENT', out['evidence_codes'])

    def test_new_l2_codes_media_and_value(self):
        a = raw({}, reason='Content-Type header application/problem+json is not documented')
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a]}))['label_L2'], 'S-MEDIA')
        a = raw({'rating': 0}, reason="[Path '/rating'] Numeric instance is lower than the required minimum (minimum: 1; found: 0)")
        b = raw({'rating': 0}, 'b')
        self.assertEqual(T.classify(sheet(a), T.Context({'api': [a, b]}))['label_L2'], 'S-RESP-VALUE')

    def test_source_order_duplicates_and_no_message_fabrication(self):
        reason = "[Path '/a'] unknown --- [Path '/a'] unknown --- [Path '/b'] unknown"
        a = raw({}, reason=reason)
        ms = T.classify_messages(sheet(a), T.Context({'api': [a]}))
        self.assertEqual([m['msg_idx'] for m in ms], [1, 2, 3])
        self.assertEqual([m['path'] for m in ms], ['/a', '/a', '/b'])
        self.assertTrue(all('msg_idx=' + str(m['msg_idx']) in m['refs'] for m in ms))
        a['failReason'] = ''
        self.assertEqual(T.classify_messages(sheet(a), T.Context({'api': [a]})), [])

    def test_strict_lenient_helpers_and_kappa(self):
        for label in ('SPEC_PARTIAL', 'IMPL_PARTIAL'):
            self.assertEqual(T.score_label(label), 'UNDECIDABLE')
            self.assertEqual(T.score_label(label, 'lenient'), label.split('_')[0])
        self.assertEqual(T.score_label('BOTH'), 'BOTH')
        a = T.agreement(['SPEC', 'IMPL', 'UNDECIDABLE', 'SPEC'], ['SPEC', 'IMPL', 'SPEC', 'UNDECIDABLE'])
        self.assertEqual((a['matched'], a['raw_agreement']), (2, .5))
        self.assertAlmostEqual(a['kappa'], .2)
        self.assertIsNone(T.agreement(['SPEC'], ['SPEC'])['kappa'])
        self.assertEqual(T.agreement(['SPEC_PARTIAL'], ['SPEC'], 'lenient')['matched'], 1)
        for mode in ('leniant', ''):
            with self.assertRaises(ValueError):
                T.score_label('SPEC', mode)
        for left, right in (([], []), (['SPEC'], [])):
            with self.assertRaises(ValueError):
                T.agreement(left, right)


@unittest.skipUnless(SHEET.exists() and P001.exists(), 'P001 local evidence not available')
class P001RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sheet = T.read_csv(SHEET)
        cls.ctx = T.Context.from_directory(P001)
        cls.results = {r['fault_id']: T.classify(r, cls.ctx, str(SHEET.relative_to(ROOT.parent))) for r in cls.sheet}

    def test_pattern_proofs_are_preserved_without_decisive_override(self):
        faults = [r for r in self.sheet if r['suggested_L1'] == 'SPEC' and r['suggested_confidence'] == '3']
        self.assertEqual({r['fault_id'] for r in faults}, {'F001', 'F003', 'F004', 'F005', 'F006'})
        for row in faults:
            with self.subTest(fault=row['fault_id']):
                out = self.results[row['fault_id']]
                self.assertEqual(out['label_L1'], 'SPEC' if row['fault_id'] == 'F001' else 'SPEC_PARTIAL')
                entries = json.loads(out['evidence_details'])
                proofs = [m for m in entries if m['rule'] == 'DOUBLE_ESCAPE']
                self.assertTrue(proofs)
                self.assertTrue(all((m['L1'], m['L2'], m['confidence']) == ('SPEC', 'S-RESP-TYPE', 3) for m in proofs))
                self.assertIn('DOUBLE_ESCAPE', out['rules'])
        self.assertTrue(json.loads(self.results['F006']['unresolved']))

    def test_partial_and_strict_undecidable_counts_are_distinct(self):
        labels = [r['label_L1'] for r in self.results.values()]
        self.assertEqual(len(labels), 73)
        self.assertEqual(labels.count('SPEC_PARTIAL'), 9)
        self.assertEqual(labels.count('UNDECIDABLE'), 29)
        self.assertEqual(sum(T.score_label(label) == 'UNDECIDABLE' for label in labels), 38)

    def test_empty_marvel_400_and_composition_remain_undecidable(self):
        for fault in ('F025', 'F028', 'F030', 'F031', 'F035', 'F007', 'F051', 'F052', 'F053', 'F055', 'F062', 'F063', 'F064'):
            self.assertEqual(self.results[fault]['label_L1'], 'UNDECIDABLE', fault)

    def test_all_rows_have_traceable_evidence_and_only_malformed_json_impl(self):
        for fault, out in self.results.items():
            self.assertIn(out['confidence'], (1, 2, 3), fault)
            self.assertIn('testCaseId=', out['evidence_refs'], fault)
            self.assertIn('fault_id=', out['evidence_refs'], fault)
            if out['label_L1'] == 'IMPL':
                self.assertEqual(fault, 'F047')
                self.assertEqual(out['label_L2'], 'I-RESP-CONTRACT')

    def test_saved_artifact_matches_recomputed_results(self):
        if not OUTPUT.exists():
            self.skipTest('Run triage CLI to produce the output artifact first')
        saved = T.read_csv(OUTPUT)
        self.assertEqual(len(saved), 73)
        for row in saved:
            out = self.results[row['fault_id']]
            for key in ('label_L1', 'label_L2', 'rules', 'unresolved', 'evidence_codes'):
                self.assertEqual(row[key], out[key], (row['fault_id'], key))
            self.assertEqual(int(row['confidence']), out['confidence'])

    def test_all_27_additional_property_faults_have_message_level_test_labels(self):
        affected = set()
        strict_faults = set()
        for row in self.sheet:
            entries = json.loads(self.results[row['fault_id']]['evidence_details'])
            for m in entries:
                if 'not allowed by the schema' in m['message']:
                    affected.add(row['fault_id'])
                    self.assertEqual((m['L1'], m['L2']), ('TEST', 'T-ORACLE-STRICT'), (row['fault_id'], m['msg_idx']))
            if T.truth(row['strict_only']):
                strict_faults.add(row['fault_id'])
                self.assertEqual(self.results[row['fault_id']]['label_L1'], 'TEST')
        self.assertEqual((len(affected), len(strict_faults)), (27, 9))

    def test_message_artifact_covers_every_raw_occurrence_in_order(self):
        saved = T.read_csv(MESSAGES)
        expected_count = 0
        for row in self.sheet:
            pairs = T.messages(self.ctx.raw(row)['failReason'])
            entries = [m for m in saved if m['fault_id'] == row['fault_id']]
            expected_count += len(pairs)
            self.assertEqual(len(entries), len(pairs))
            self.assertEqual([int(m['msg_idx']) for m in entries], list(range(1, len(pairs) + 1)))
            self.assertEqual([m['message'] for m in entries],
                             [(f"[Path '{path}'] " if path else '') + msg for path, msg in pairs])
            recomputed = json.loads(self.results[row['fault_id']]['evidence_details'])
            for actual, expected in zip(entries, recomputed):
                for key in T.MESSAGE_FIELDS:
                    value = str(expected[key])
                    if key == 'refs':
                        self.assertEqual(sorted(json.loads(actual[key])),
                                         sorted(ref.replace(str(ROOT.parent) + '/', '') for ref in json.loads(value)),
                                         (row['fault_id'], actual['msg_idx'], key))
                        continue
                    self.assertEqual(actual[key], value, (row['fault_id'], actual['msg_idx'], key))
        self.assertEqual(len(saved), expected_count)


if __name__ == '__main__':
    unittest.main(verbosity=2)
