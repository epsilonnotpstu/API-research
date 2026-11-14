"""Check output coverage, evidence locators, and case-level root memberships."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / '08_experiments/E1_pilot/runs/scout-api/20261113T202103Z_baseline_NONE_p0_s1_1642810'
label_path = ROOT / '08_experiments/E2_labelling/batch2_baseline_s1_labels_codex.csv'
root_path = ROOT / '08_experiments/E2_labelling/batch2_root_causes_codex.csv'
with label_path.open(newline='') as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ['item_id','L1','L2','proposed_L2','confidence','evidence_types','evidence_locators','root_cause_id','both_candidate','rationale']
    labels = list(reader)
with root_path.open(newline='') as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ['root_cause_id','description','fix_site','items']
    roots = list(reader)
blind_path = ROOT / '08_experiments/E2_labelling/batch2_baseline_s1_blind.csv'
items = list(csv.DictReader(blind_path.open(newline='')))
assert [r['item_id'] for r in labels] == [r['item_id'] for r in items] == [f'B{i:03}' for i in range(1,100)]
assert [r['root_cause_id'] for r in roots] == [f'RC{i:02}' for i in range(1,19)]
root_ids = {r['root_cause_id'] for r in roots}
case_map = collections.defaultdict(list)
for case in json.loads((OUT / 'case_root_causes.json').read_text()):
    case_map[case['item_id']].append(case)
exmap = {r['item_id']:r for r in json.loads((OUT / 'exchange_map.json').read_text())}
file_lines = {}
loc_count = 0
allowed_l2 = {'IMPL':{'I-CRASH'},'SPEC':{'S-STRUCT','S-STATUS','S-REQ-LOOSE'},'UNDECIDABLE':{''},'TEST':{''}}
for row,item in zip(labels,items):
    iid = row['item_id']
    assert row['L2'] in allowed_l2[row['L1']]
    assert row['confidence'] in {'1','2','3'}
    assert row['both_candidate'] in {'true','false'}
    assert row['rationale'].startswith('⚠️ ')
    assert len(row['rationale'].split()) <= 30
    assert bool(row['proposed_L2']) == (iid == 'B001')
    membership = set(row['root_cause_id'].split(';'))
    assert membership <= root_ids
    for rc in membership:
        root = next(r for r in roots if r['root_cause_id']==rc)
        assert iid in root['items'].split(';')
    assert len(exmap[iid]['exchange_lines']) == int(item['occurrences'])
    if item['status']=='500':
        assert len(case_map[iid]) == int(item['occurrences']), iid
        assert len({r['exchange_line'] for r in case_map[iid]}) == int(item['occurrences'])
        assert {r['root_cause_id'] for r in case_map[iid]} == membership
        assert {r['exchange_line'] for r in case_map[iid]} == set(exmap[iid]['exchange_lines'])
    for locator in row['evidence_locators'].split(';'):
        match = re.fullmatch(r'(.+):(\d+)(?: \(JSON Pointer (.*)\))?', locator)
        assert match, locator
        name, line = match[1], int(match[2])
        assert 'labels_code' not in name and 'prelim' not in name
        path = ROOT / name
        assert path.is_file(), locator
        if name not in file_lines:
            file_lines[name] = path.read_bytes().split(b'\n')
        assert 1 <= line <= len(file_lines[name]), locator
        assert file_lines[name][line-1].strip(), locator
        if match[3] is not None:
            node = json.loads(path.read_text())
            for part in match[3].lstrip('/').split('/'):
                part = part.replace('~1','/').replace('~0','~')
                node = node[int(part)] if isinstance(node,list) else node[part]
        loc_count += 1
for root in roots:
    members = [r['item_id'] for r in labels if root['root_cause_id'] in r['root_cause_id'].split(';')]
    assert root['items'].split(';') == members
    if root['root_cause_id']=='RC18':
        assert root['description'].startswith('[H]') and root['fix_site']==''
    else:
        assert root['description'].startswith('⚠️')
        assert root['fix_site'] in {'spec','code','test','env'}

# Independently verify logged error IDs against physical LF line numbers.
log_lines = (RUN / 'compose.log').read_bytes().decode('utf-8').split('\n')
xs = [json.loads(raw) for raw in (RUN / 'exchanges.jsonl').open()]
for mapped in json.loads((OUT / 'log_map.json').read_text()):
    for error in mapped['errors']:
        message = json.loads(xs[error['exchange_line']-1]['response']['body']['text'])['message']
        error_id = re.search(r'logged \(ID ([0-9a-f]+)\)',message)[1]
        assert f'Error handling a request: {error_id}' in log_lines[error['log_line']-1]

# Directly check the overflow and probe witnesses without the replay map logic.
overflow_count = 0
for item in items:
    if item['status']=='404':
        for n in exmap[item['item_id']]['exchange_lines']:
            value = int(xs[n-1]['request']['path'].rsplit('/',1)[-1])
            assert not -(2**63) <= value < 2**63
            overflow_count += 1
first = xs[0]
assert first['request']['headers']['x-schemathesis-probe']=='NULL_BYTE_IN_HEADER'
assert first['request']['headers']['x-schemathesis-probe-null']=='\x00'
assert first['response']['status']==400

files = [blind_path,label_path,root_path,RUN/'exchanges.jsonl',RUN/'compose.log',RUN/'spec.original.json',RUN/'generator-input.json',RUN/'derecurse-cuts.json']
files += [ROOT/name for name in sorted(file_lines) if (ROOT/name) not in files]
manifest = {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
(OUT/'sha256_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
summary = {'status':'PASS','items':len(labels),'order_and_schema':'PASS','rationale_max_words':max(len(r['rationale'].split()) for r in labels),
           'evidence_locators_checked':loc_count,'evidence_files_checked':len(file_lines),
           'L1':dict(collections.Counter(r['L1'] for r in labels)), 'root_rows':len(roots),
           'provisional_root_with_unresolved_fix_site':'RC18','overflow_404_exchanges':overflow_count,
           'case_memberships_checked':sum(map(len,case_map.values())),
           'both_candidates':sum(r['both_candidate']=='true' for r in labels),
           'physical_log_line_numbering':'PASS','error_id_joins':'PASS','sha256_manifest':'sha256_manifest.json'}
(OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
