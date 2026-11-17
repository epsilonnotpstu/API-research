import csv
from collections import Counter
from pathlib import Path

with Path('items.csv').open(newline='') as stream:
    expected = [r['item_id'] for r in csv.DictReader(stream)]
with Path('codes_G1.csv').open(newline='') as stream:
    reader = csv.DictReader(stream)
    assert reader.fieldnames == ['item_id', 'observable_change', 'change_kind', 'client_impact', 'contract_specified', 'confidence', 'locators', 'rationale']
    rows = list(reader)
assert [r['item_id'] for r in rows] == expected
kinds = {'STATUS_OR_ERROR_MAPPING', 'INPUT_STRICTER', 'INPUT_LOOSER', 'DEFAULT_OR_OPTIONALITY', 'RESPONSE_CONTENT', 'RESPONSE_SHAPE', 'HEADER_OR_MEDIA_TYPE', 'AUTHZ_OR_AUTH', 'SIDE_EFFECT_OR_STATE', 'ORDERING_PAGINATION_LIMITS', 'OTHER'}
for row in rows:
    item = row['item_id']
    assert None not in row, item
    assert row['observable_change'] in {'YES', 'NO', 'UNCLEAR'}, item
    assert row['confidence'] in {'1', '2', '3'}, item
    assert len(row['rationale'].split()) <= 40, (item, len(row['rationale'].split()))
    if row['observable_change'] == 'YES':
        assert row['change_kind'] in kinds, item
        assert row['client_impact'] in {'BREAKING', 'COMPATIBLE', 'UNCLEAR'}, item
        assert row['contract_specified'] in {'SPECIFIED', 'UNSPECIFIED'}, item
    else:
        assert all(row[k] == 'NA' for k in ['change_kind', 'client_impact', 'contract_specified']), item
    if row['contract_specified'] == 'SPECIFIED':
        assert '/contract/' in row['locators'], item
    for locator in row['locators'].split(';'):
        filename, line = locator.rsplit(':', 1)
        p = Path(filename)
        assert p.parts[0] == item, locator
        assert p.is_file() and 1 <= int(line) <= len(p.read_text().splitlines()), locator
print('Validated rows:', len(rows))
print('Observable:', dict(Counter(r['observable_change'] for r in rows)))
print('Impact:', dict(Counter(r['client_impact'] for r in rows)))
print('Unclear items:', ', '.join(r['item_id'] for r in rows if r['observable_change'] == 'UNCLEAR'))
