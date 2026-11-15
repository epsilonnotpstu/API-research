import csv
from pathlib import Path
from collections import Counter

fields = ['item_id', 'divergence_kind', 'contract_specificity', 'confidence',
          'impl_locators', 'contract_locators', 'rationale']
with Path('items.csv').open() as stream:
    order = [row['item_id'] for row in csv.DictReader(stream)]
with Path('codes_work_C2/decisions.tsv').open() as stream:
    rows = list(csv.DictReader(stream, delimiter='\t'))
assert [r['item_id'] for r in rows] == order
assert len(set(order)) == len(order) == 70
for row in rows:
    assert row['divergence_kind'] in {'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'}
    assert row['contract_specificity'] in {'SPECIFIC', 'GENERIC', 'UNCLEAR'}
    assert row['confidence'] in {'1', '2', '3'}
    assert len(row['rationale'].split()) <= 40
    for side, separator in [('impl', ':'), ('contract', '#')]:
        expanded = []
        for locator in row[f'{side}_locators'].split(';'):
            name, line = locator.rsplit(separator, 1)
            matches = list((Path(row['item_id']) / side).rglob(name))
            assert len(matches) == 1, (row['item_id'], locator, matches)
            path = matches[0]
            assert 1 <= int(line) <= len(path.read_text().splitlines())
            expanded.append(f'{path}{separator}{line}')
        row[f'{side}_locators'] = ';'.join(expanded)
with Path('codes_C2.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
with Path('codes_C2.csv').open(newline='') as stream:
    reread = list(csv.DictReader(stream))
assert reread == rows
print('Validated rows:', len(rows))
for field in ('divergence_kind', 'contract_specificity', 'confidence'):
    print(field, dict(Counter(r[field] for r in rows)))
print('Confidence 2:', ', '.join(r['item_id'] for r in rows if r['confidence'] == '2'))
