import csv
import pathlib

root = pathlib.Path('.')
with open('items.csv', newline='') as f:
    expected = [row['item_id'] for row in csv.DictReader(f)]
with open('codes_work_C14/decisions.psv', newline='') as f:
    rows = list(csv.DictReader(f, delimiter='|'))
assert [row['item_id'] for row in rows] == expected

for row in rows:
    assert row['divergence_kind'] in {'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'}
    assert row['contract_specificity'] in {'SPECIFIC', 'GENERIC', 'UNCLEAR'}
    assert row['confidence'] in {'1', '2', '3'}
    assert len(row['rationale'].split()) <= 40, (row['item_id'], len(row['rationale'].split()))
    for kind in ('impl', 'contract'):
        key = kind + '_locators'
        resolved = []
        for locator in row[key].split(';'):
            suffix, line = locator.rsplit('@', 1)
            item_root = root / row['item_id'] / kind
            matches = [p for p in item_root.rglob('*') if p.is_file() and str(p).endswith('/' + suffix)]
            assert len(matches) == 1, (row['item_id'], kind, locator, matches)
            path = matches[0]
            assert 0 < int(line) <= len(path.read_text().splitlines()), (path, line)
            resolved.append(str(path) + (':' if kind == 'impl' else '#') + line)
        row[key] = ';'.join(resolved)

with open('codes_C14.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f'Validated and wrote {len(rows)} rows in items.csv order.')
