"""Audit saved P001 replay data without executing any external project code."""
import csv
import hashlib
import json
from pathlib import Path
import sys
from collections import Counter
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
sys.path.insert(0, str(ROOT / '08_experiments/E1_pilot'))
import conformance
import p001_oas_analysis as p001
import specmut
import pandas as pd

def emit(identifier, value):
    print(json.dumps({'id': identifier, **value}, sort_keys=True))


def brief(violations):
    unique = {(v['kind'], v['pointer'], v['message']) for v in violations}
    return {'record_count': len(violations), 'distinct_count': len(unique),
            'sample': [{'kind': k, 'pointer': p, 'message': m[:160]}
                       for k, p, m in sorted(unique)[:5]]}


raw_dir = ROOT / '08_experiments/_external/p001'
frames = []
for path in sorted(raw_dir.glob('faultClustersConfirmedBugs_*.csv')):
    frame = pd.read_csv(path, low_memory=False)
    frame['api_file'] = path.stem.split('_', 1)[1]
    frames.append(frame)
df = pd.concat(frames, ignore_index=True)
df['oracle'] = df.failReasonCategory.map(p001.CATEGORY_SHORT).fillna('OTHER')
bugs = pd.read_csv(raw_dir / 'bugs_reported.csv')
specs = {p.name.split('__openapi.')[0].lower(): p for p in (raw_dir / 'specs').iterdir()}
emit('A01_coverage', {'fault_rows': len(df), 'bug_rows': len(bugs),
                    'fault_duplicate_testCaseId': int(df.testCaseId.duplicated().sum()),
                    'bugs_duplicate_testCaseId': int(bugs.testCaseId.duplicated().sum()),
                    'missing_spec_apis': sorted(set(df.api_file.str.lower()) - set(specs)),
                    'raw_columns': list(df.columns)})

counts = Counter()
examples = []
for row in df.itertuples():
    if row.oracle != 'F_OAS':
        continue
    doc = specmut.load_spec(str(specs[row.api_file.lower()]))
    sp = conformance.Spec(doc)
    ex = p001.exchange(row._asdict(), sp)
    default = conformance.check(sp, ex)
    strict = conformance.check(conformance.Spec(doc, True), ex)
    ours = set()
    for v in default:
        if v['kind'] == 'UNDOCUMENTED_STATUS':
            ours.add('STATUS_UNDEFINED')
        elif v['kind'] == 'RESPONSE_PARSE':
            ours.add('PARSE')
        elif v['kind'] == 'RESPONSE_CONTENT_TYPE':
            ours.add('CONTENT_TYPE')
        elif v['kind'] == 'RESPONSE_SCHEMA':
            tail = v['pointer'].split('/')[-1]
            ours.add({'additionalProperties': 'ADDITIONAL_PROPERTIES',
                      'required': 'MISSING_REQUIRED', 'oneOf': 'COMPOSITION',
                      'anyOf': 'COMPOSITION', 'allOf': 'COMPOSITION',
                      'pattern': 'PATTERN', 'format': 'FORMAT', 'enum': 'ENUM',
                      'minimum': 'NUMERIC_RANGE', 'maximum': 'NUMERIC_RANGE',
                      'type': 'TYPE_NULL' if v['message'].startswith('None ') else 'TYPE_MISMATCH'}.get(tail, tail))
    src_types = p001.message_types(row.failReason)
    if 'ADDITIONAL_PROPERTIES' in src_types:
        counts['additional_source_faults'] += 1
        for mode, violations in [('default', default), ('strict', strict)]:
            counts['additional_keyword_hit_' + mode] += any(
                v['kind'] == 'RESPONSE_SCHEMA' and v['pointer'].endswith('/additionalProperties')
                for v in violations)
    broad_hit = bool({v['kind'] for v in default} & p001.OUR_KIND_FOR['F_OAS'])
    if broad_hit and 'ADDITIONAL_PROPERTIES' in src_types and 'ADDITIONAL_PROPERTIES' not in ours:
        counts['additional_source_counted_without_additional_default'] += 1
        examples.append({'api': row.api_file, 'testCaseId': row.testCaseId,
                         'p001_types': sorted(src_types), 'our_types_default': sorted(ours),
                         'our_violations_default': brief(default)})
    if broad_hit and not src_types.intersection(ours):
        counts['broad_hit_with_disjoint_message_types_default'] += 1
        emit('A02_disjoint_agreement', {'api': row.api_file, 'testCaseId': row.testCaseId,
                                      'p001_types': sorted(src_types), 'our_types_default': sorted(ours),
                                      'violations': brief(default)})
    if any(v['kind'] == 'INVALID_ACCEPTED' for v in default):
        counts['F_OAS_with_extra_INVALID_ACCEPTED_default'] += 1
    if any(v['kind'] == 'UNDOCUMENTED_OPERATION' for v in strict):
        emit('A03_unmatched_path', {'api': row.api_file, 'testCaseId': row.testCaseId,
                                  'template': row.path, 'reconstructed_path': ex['request']['path'],
                                  'pathParameters': row.pathParameters})
        raw_params = dict(part.split('=', 1) for part in row.pathParameters.split(';') if '=' in part)
        encoded_path = row.path
        for name, value in raw_params.items():
            encoded_path = encoded_path.replace('{' + name + '}', value)
        encoded_exchange = json.loads(json.dumps(ex))
        encoded_exchange['request']['path'] = sp.base + encoded_path
        encoded_kinds = {v['kind'] for v in conformance.check(conformance.Spec(doc, True), encoded_exchange)}
        emit('A03_preserved_encoding', {'api': row.api_file, 'testCaseId': row.testCaseId,
                                      'preserved_path': encoded_exchange['request']['path'],
                                      'strict_kinds': sorted(encoded_kinds)})
for item in examples:
    emit('A04_additional_not_reproduced', item)
emit('A05_message_audit_counts', dict(counts))

cells = Counter()
for row in df.itertuples():
    for col in ('pathParameters', 'queryParameters', 'headerParameters'):
        text = getattr(row, col)
        if isinstance(text, str):
            keys = [part.partition('=')[0] for part in filter(None, text.split(';'))]
            cells[col + '_duplicate_keys'] += len(keys) != len(set(keys))
            cells[col + '_literal_plus'] += '+' in text
            cells[col + '_encoded_slash'] += '%2f' in text.lower()
emit('A06_serialization_risks', dict(cells))

joined = df.merge(bugs, on='testCaseId', how='left', suffixes=('', '_bug'))
emit('A07_join', {'joined_rows': len(joined), 'original_rows': len(df)})

for name in ('summary.json', 'replay_agreement.csv', 'developer_response.csv', 'oas_violation_types.csv'):
    old = ROOT / '08_experiments/E1_pilot/p001_results' / name
    new = HERE / 'p001_rerun' / name
    if new.exists():
        emit('A08_artifact_equality', {'file': name, 'byte_equal': old.read_bytes() == new.read_bytes(),
                                     'original_sha256': hashlib.sha256(old.read_bytes()).hexdigest(),
                                     'rerun_sha256': hashlib.sha256(new.read_bytes()).hexdigest()})

# Known metric defects under controlled dataframe inputs, with no new replay artifacts.
left = pd.DataFrame([{'testCaseId': 'shared', 'api_file': 'A'},
                     {'testCaseId': 'shared', 'api_file': 'B'}])
right = pd.DataFrame([{'testCaseId': 'shared', 'api': 'A', 'confirmed': True},
                      {'testCaseId': 'shared', 'api': 'B', 'confirmed': False}])
wrong = left.merge(right, on='testCaseId', how='left')
assert len(wrong) == 4
emit('A09_cross_api_join_fixture', {'input_rows': left.to_dict('records'),
                                  'bug_rows': right.to_dict('records'),
                                  'expected_rows': 2, 'actual_rows': len(wrong),
                                  'actual_confirmed': int(wrong.confirmed.sum())})

emit('A10_missing_spec_fixture', {'faults': [{'api': 'missing', 'oracle': 'F_OAS'}],
                                 'specs': [], 'expected': 'Explicit skipped/error row in denominator',
                                 'actual_by_source_lines_128_129': 'continue; no replay row'})

reviewed = [ROOT / '08_experiments/tools' / name for name in
            ['specmut.py', 'conformance.py', 'attribute.py', 'mitm_fulllog.py', 'test_specmut.py', 'test_pipeline.py']]
reviewed += [ROOT / '08_experiments/E1_pilot/p001_oas_analysis.py',
             ROOT / '08_experiments/E1_pilot/P001_empirical_findings.md']
inputs = sorted(raw_dir.glob('faultClustersConfirmedBugs_*.csv'))
inputs += sorted((raw_dir / 'specs').iterdir()) + [raw_dir / 'bugs_reported.csv']
emb = ROOT / '08_experiments/_external/emb/openapi-swagger'
inputs += sorted(emb.glob('*.json')) + sorted(emb.glob('*.yaml'))
emit('A11_provenance', {'python': sys.version,
                        'dependencies': {n: version(n) for n in ['jsonschema', 'PyYAML', 'pandas']},
                        'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in reviewed + inputs}})

observations = [json.loads(line) for line in (HERE / 'reproductions.jsonl').read_text().splitlines()]
emit('A12_verification', {'reproduction_summary': observations[-1]['summary'],
                         'pipeline_repeat_byte_equal':
                         (HERE / 'test_pipeline.txt').read_bytes() == (HERE / 'test_pipeline_repeat.txt').read_bytes(),
                         'specmut_test_summary': (HERE / 'test_specmut.txt').read_text().strip().splitlines()[-1],
                         'emb_spec_count': len(list(emb.glob('*.json'))) + len(list(emb.glob('*.yaml')))})
