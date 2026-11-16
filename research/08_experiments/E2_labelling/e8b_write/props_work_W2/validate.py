import csv
import re
from pathlib import Path

items = list(csv.DictReader(Path('items.csv').open()))
with Path('props_W2.csv').open() as f:
    reader = csv.DictReader(f)
    assert reader.fieldnames == ['item_id', 'proposition', 'contract_locators', 'impl_locators', 'confidence']
    rows = list(reader)
assert len(rows) == len(items) == 41
assert [r['item_id'] for r in rows] == [r['item_id'] for r in items]
for item, row in zip(items, rows):
    key = row['item_id']
    assert row['confidence'] in ('1','2','3'), key
    prop = row['proposition']
    if prop == 'NONE':
        assert row['contract_locators'] == row['impl_locators'] == '', key
        continue
    assert prop.startswith(item['operation'] + ': contract says '), key
    assert prop.count('; implementation does ') == 1, key
    assert len(prop.split()) <= 45, (key, len(prop.split()))
    for col, side, sep in [('contract_locators','contract','#'),('impl_locators','impl',':')]:
        assert row[col], key
        for locator in row[col].split(';'):
            path, number = locator.rsplit(sep, 1)
            assert path.startswith(key+'/'+side+'/'), locator
            assert number.isdigit(), locator
            assert Path(path).is_file(), locator
            assert 1 <= int(number) <= len(Path(path).read_text().splitlines()), locator
for file in ('props_W2.csv','props_report_W2.md'):
    content = Path(file).read_text()
    assert not re.search(r'\b(deliberate|deliberately|accidental|accidentally|intentional|intentionally|oversight|forgot|bug|wrong|correct|incorrect|should|mistake)\b', content, re.I), file
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', content), file
print('PASS: CSV structure, item order, operation form, word limits, vocabulary, confidence, locators, and report.')
print('NONE:', ', '.join(r['item_id'] for r in rows if r['proposition'] == 'NONE'))
print('Longest proposition:', max(len(r['proposition'].split()) for r in rows), 'words')
