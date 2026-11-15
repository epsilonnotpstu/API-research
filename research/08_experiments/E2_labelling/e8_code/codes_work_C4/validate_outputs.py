import csv
import re
from pathlib import Path

expected = list(csv.DictReader(Path('items.csv').open()))
with Path('codes_C4.csv').open(newline='', encoding='utf-8') as stream:
    reader = csv.DictReader(stream)
    assert reader.fieldnames == ['item_id', 'divergence_kind', 'contract_specificity',
                                'confidence', 'impl_locators', 'contract_locators', 'rationale']
    rows = list(reader)
assert [row['item_id'] for row in rows] == [row['item_id'] for row in expected]
assert len({row['item_id'] for row in rows}) == len(expected)
for row in rows:
    assert row['divergence_kind'] in ('DELIBERATE', 'ACCIDENTAL', 'UNCLEAR')
    assert row['contract_specificity'] in ('SPECIFIC', 'GENERIC', 'UNCLEAR')
    assert row['confidence'] in ('1', '2', '3')
    assert len(row['rationale'].split()) <= 40
    for side, column, separator in [('impl', 'impl_locators', ':'), ('contract', 'contract_locators', '#')]:
        for locator in row[column].split(';'):
            filename, line = locator.rsplit(separator, 1)
            assert filename.startswith(row['item_id'] + '/' + side + '/')
            path = Path(filename)
            assert path.is_file()
            assert 1 <= int(line) <= len(path.read_text().splitlines())
report = Path('codes_report_C4.md').read_text()
assert re.search('[\u0980-\u09ff]', report)
assert all(title in report for title in ('পদ্ধতি', 'কঠিন সিদ্ধান্ত', 'সীমাবদ্ধতা', 'Boundary incidents'))
print(f'PASS: {len(rows)} rows, order, headers, labels, confidence, rationale limits, all locators, Bengali report.')
