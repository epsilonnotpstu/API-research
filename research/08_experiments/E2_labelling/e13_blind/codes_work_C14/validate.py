import collections
import csv
import json
import pathlib
import re

headers = ['item_id', 'divergence_kind', 'contract_specificity', 'confidence', 'impl_locators', 'contract_locators', 'rationale']
with open('items.csv', newline='') as f:
    expected = [r['item_id'] for r in csv.DictReader(f)]
with open('codes_C14.csv', newline='') as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == headers
    rows = list(reader)
assert [r['item_id'] for r in rows] == expected
assert len({r['item_id'] for r in rows}) == len(rows)
locator_count = 0
for row in rows:
    assert row['divergence_kind'] in {'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'}
    assert row['contract_specificity'] in {'SPECIFIC', 'GENERIC', 'UNCLEAR'}
    assert row['confidence'] in {'1', '2', '3'}
    assert len(row['rationale'].split()) <= 40
    for kind, sep in [('impl', ':'), ('contract', '#')]:
        for locator in row[kind + '_locators'].split(';'):
            path, number = locator.rsplit(sep, 1)
            assert path.startswith(row['item_id'] + '/' + kind + '/')
            assert '..' not in pathlib.Path(path).parts
            lines = pathlib.Path(path).read_text().splitlines()
            assert 0 < int(number) <= len(lines)
            locator_count += 1

report = pathlib.Path('codes_report_C14.md').read_text()
assert re.search('[\u0980-\u09ff]', report)
for text in [pathlib.Path('codes_C14.csv').read_text(), report]:
    assert not re.search(r'authelia_(at|rt)_[A-Za-z0-9_.-]{20,}', text)
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-z]{2,}', text, re.I)

result = {
    'status': 'passed',
    'row_count': len(rows),
    'order_matches_items_csv': True,
    'divergence_kind': dict(collections.Counter(r['divergence_kind'] for r in rows)),
    'contract_specificity': dict(collections.Counter(r['contract_specificity'] for r in rows)),
    'confidence': dict(collections.Counter(r['confidence'] for r in rows)),
    'maximum_rationale_word_count': max(len(r['rationale'].split()) for r in rows),
    'validated_locator_count': locator_count,
    'report_contains_bengali': True,
    'validation_scope': 'Output integrity and locator existence; no item-source execution or runtime verification.',
}
pathlib.Path('codes_work_C14/validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
