"""Read-only production audit. Reports metadata and counts, never raw credentials."""
import collections
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E4 = ROOT / '08_experiments/E4_triage'
OUT = ROOT / '08_experiments/E2_labelling/e4_blind'
SCRATCH = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


b = module('builder_audit', E4 / 'build_e4_blind.py')
t = module('patch_audit', E4 / 'test_build_e4_blind.py')
config = b.configure_source_omissions(b.default_config(), [
    'cwa-verification:api-docs.json', 'swagger-petstore:src/main/webapp/openapi.yaml'])
config['allow_inherited_codebook'] = True
log = json.loads((E4 / 'build_log.json').read_bytes())
key = b.rows(E4 / 'e4_key.csv')
items = b.rows(OUT / 'items.csv')
manifests = json.loads((E4 / 'e4_manifest.json').read_bytes())
assert len(items) == len(key) == log['items'] == 50
assert [r['item_id'] for r in items] == [r['item_id'] for r in key]
assert len({r['item_id'] for r in items}) == 50
assert collections.Counter(r['role'] for r in key) == {'injected': 28, 'decoy': 22}
assert {p.name for p in OUT.iterdir() if p.is_dir()} == {'K01', 'K02', 'K03', 'K04'}
assert set(items[0]) == set(b.ITEM_COLUMNS)
assert all(k in key[0] for k in b.KEY_COLUMNS)
assert all((OUT / k).read_bytes() == p.read_bytes() for k, p in [
    ('TASK_M1.md', SCRATCH / 'task_drafts/TASK_M1.md'),
    ('TASK_M2.md', SCRATCH / 'task_drafts/TASK_M2.md'),
    ('CODEBOOK_v0.6.md', config['codebook'])])
assert log['counts'] == json.loads((SCRATCH / 'replay_preflight_counts.json').read_bytes())
assert b.audit_source_specs(config) == log['source_spec_scan']
for path, digest in log['package_file_sha256'].items():
    assert b.sha((OUT / path).read_bytes()) == digest
for path, digest in log['input_sha256'].items():
    assert b.sha((ROOT / path).read_bytes()) == digest
protected = json.loads((SCRATCH / 'protected_inputs.json').read_bytes())
assert all(b.sha((ROOT / path).read_bytes()) == digest for path, digest in protected.items())
for name in ('e4_key.csv', 'e4_manifest.json', 'build_log.json'):
    assert (E4 / name).read_bytes() == (E4 / 'build_evidence' / name).read_bytes()

needles = b.fixture_needles(config['fixtures'])
originals = []
by_item = {r['item_id']: r for r in items}
checks = {}
traffic_keyword_hits = []
copy_scan_config = copy.deepcopy(config)
kind_table = b.expected_kinds(config['kind_source'])
finals = b.rows(config['labels'])

for sut, conf in sorted(config['suts'].items()):
    package = OUT / log['package_by_sut'][sut]
    source = package / 'source'
    original = json.loads(conf['emb_spec'].read_bytes())
    originals.append(original)
    composite = json.loads((package / 'spec.json').read_bytes())
    b.checker.Spec(composite, deploy_origin=conf['origin'])
    rebuilt = copy.deepcopy(original)
    occupied = set()
    manifest = manifests[sut]
    for stage in manifest['stages']:
        assert not {tuple(op) for op in stage['only_ops']} & occupied
        occupied = {tuple(op) for op in stage['occupied_after']}
    for mutation in manifest['mutations']:
        for edit in mutation['edits']:
            t.apply_patch_record(rebuilt, edit)
    assert rebuilt == composite
    b.assert_no_new_extensions(original, composite)
    expected_source = b.tree_entries(conf['source'], conf['source_omit'])
    assert b.tree_entries(source) == expected_source == log['source_audit'][sut]['files']
    assert b.tree_hash(b.tree_entries(conf['source'])) == log['source_audit'][sut]['full_upstream_sha256']
    assert not any(p.name in b.SKIP for p in source.rglob('*'))
    for rel in conf['source_omit']:
        assert not (source / rel).exists()
        assert b.sha((conf['source'] / rel).read_bytes()) == log['source_audit'][sut]['omitted_file_sha256'][rel]
    copy_scan_config['suts'][sut]['source'] = source
    copy_scan_config['suts'][sut]['source_omit'] = []

    def jsonl(path):
        return [json.loads(line) for line in path.read_bytes().split(b'\n') if line.strip()]
    baseline = jsonl(conf['run'] / 'exchanges.jsonl')
    exchanges = jsonl(package / 'r1/exchanges.jsonl')
    needles.update(b.header_needles(baseline))
    assert len(exchanges) == len(baseline) == log['replay'][sut]['exchanges']
    assert exchanges == [b.redact_exchange(x, needles) for x in baseline]
    assert (package / 'r1/compose.log').read_bytes() == b.redact_bytes(
        (conf['run'] / 'compose.log').read_bytes(), needles)
    for filename in ('exchanges.jsonl', 'compose.log'):
        raw = (package / 'r1' / filename).read_text()
        # Report physical LF line numbers independently of Unicode separators.
        for line_number, line in enumerate(raw.split('\n'), 1):
            for match in b.FORBIDDEN.finditer(line):
                traffic_keyword_hits.append({'file': f'{package.name}/r1/{filename}',
                                             'physical_line': line_number,
                                             'token': match.group(0), 'input_provenance_verified': True})
    replay_dir = E4 / 'build_evidence/replay'
    before = jsonl(replay_dir / f'{sut}.original.jsonl')
    after = jsonl(replay_dir / f'{sut}.composite.jsonl')
    attributed = {r['fingerprint']: r for r in jsonl(replay_dir / f'{sut}.attribution.jsonl')}
    original_fps = {r['fingerprint'] for r in before}
    composite_fps = {r['fingerprint'] for r in after}
    occurrences = {(r['fingerprint'], r['exchange']): r for r in after}
    mapping = b.label_mapping(conf, sut, finals)
    for record in (k for k in key if k['sut'] == sut):
        item = by_item[record['item_id']]
        assert item['package'] == package.name and item['run'] == 'r1'
        fp = record['fingerprint']
        row = attributed[fp]
        example = int(item['example_exchange'])
        assert b.clean(exchanges[example])
        assert (fp, example) in occurrences
        violation = occurrences[fp, example]
        assert all(str(item[k]) == str(violation[k]) for k in
                   ('kind', 'method', 'template', 'status', 'pointer', 'message'))
        if record['role'] == 'injected':
            assert fp not in original_fps and fp in composite_fps
            assert b.injected_candidate(row, kind_table)
            assert record['expected_L1'] == 'SPEC' == row['label_L1']
            assert record['expected_L2'] == row['label_L2']
            assert json.loads(record['edit_pointers']) == b.edit_pointers(row, manifest)
        else:
            assert fp in original_fps & composite_fps and row['status'] == 'PERSISTENT'
            assert mapping[fp]['item_id'] == record['baseline_item_id']
            assert record['final_L1'] == mapping[fp]['final_L1'] == record['expected_L1']
    checks[sut] = {'source_files': len(expected_source), 'source_identity_passed': True,
                   'omitted_files': conf['source_omit'], 'exchanges': len(exchanges),
                   'composite_patch_reconstruction_passed': True,
                   'disjoint_operation_sets_passed': True, 'all_item_joins_passed': True}

assert all(not scan['spec_like'] for scan in b.audit_source_specs(copy_scan_config).values())
b.assert_no_original_specs(OUT, originals)
b.assert_no_credentials(OUT, needles)
allowed_tokens = {r['token'] for r in traffic_keyword_hits}
hits = b.blinding_hits(OUT, allowed_tokens, config['codebook'].read_bytes())
assert len(hits) == len(traffic_keyword_hits) == len(log['legitimate_traffic_keyword_hits'])
assert len(log['inherited_codebook_keyword_hits']) == 7
try:
    b.build(config, OUT, SCRATCH / 'must-not-create-hidden')
except ValueError as error:
    assert 'refusing to overwrite' in str(error)
else:
    raise AssertionError('Existing production output was accepted')
assert not (SCRATCH / 'must-not-create-hidden').exists()
assert all(b.sha((OUT / path).read_bytes()) == digest for path, digest in log['package_file_sha256'].items())
summary = {'production_build_started': True, 'production_build_completed': True, 'production_build_count': 1,
           'items': len(items), 'roles': dict(collections.Counter(k['role'] for k in key)),
           'tests': 26, 'tests_passed': True, 'protected_files': len(protected),
           'protected_inputs_unchanged': True, 'package_file_hashes_verified': len(log['package_file_sha256']),
           'package_bytes': sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),
           'source_files_verified': sum(v['source_files'] for v in checks.values()),
           'package_spec_like_source_files': 0, 'credential_checks_passed': True,
           'no_original_spec_checks_passed': True, 'no_unapproved_keyword_hits': True,
           'codebook_byte_identity_passed': True, 'task_draft_copy_identity_passed': True,
           'traffic_keyword_hits': len(traffic_keyword_hits), 'inherited_codebook_hits': 7,
           'overwrite_refusal_passed': True, 'labellers_launched': False, 'suts': checks}
b.dump(SCRATCH / 'traffic_keyword_provenance.json', traffic_keyword_hits)
b.dump(SCRATCH / 'production_verification.json', summary)
print(json.dumps(summary, sort_keys=True))
